#!/usr/bin/env python3
"""The Phase 14A freeze gate: one scripted run walking all eight G3
scenarios end to end on the synthetic corpus, and confirming the shipped
parser/scorer/evidence suites still pass (audit A6). A later plan task adds
the D-12.6-10 budget measurements and the reflow-normalization corpus check
to this same file; this task is the eight-scenario walk plus the shipped
suite check.

Standard library only, runnable as `python tests/file_fault_tracer.py`.
Reuses the fault-injection helpers already written in
`tests/journal_roundtrip.py` (the `--child` subprocess fixtures) rather than
copying them: this tracer composes the phase's own proofs, it does not
rewrite them.

Every scenario asserts, explicitly, that the on-disk state is either the old
valid state or the new valid state; a state matching neither fails loudly
with a message beginning `"mixed state"` (RELIABILITY-01).
"""
import errno
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, TESTS_DIR)
import discovery                                              # noqa: E402
import identity                                               # noqa: E402
import journal                                                # noqa: E402
import fixtures.corpus_14a as corpus_14a                      # noqa: E402
import journal_roundtrip                                      # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def _assert_old_or_new(path, old_raw, new_raw, label):
    with open(path, "rb") as fh:
        current = fh.read()
    if current != old_raw and current != new_raw:
        fail("mixed state: %s target bytes matched neither the old nor "
             "the new content" % label)
    return current


# ---------------------------------------------------------------------------
# The eight G3 scenarios.


def _find_first_file(root, name_contains):
    for dirpath, dirs, files in os.walk(root):
        dirs.sort()
        for f in sorted(files):
            if name_contains in f:
                return os.path.join(dirpath, f)
    return None


def scenario_move(base, corpus):
    root_vault = corpus["root_paths"]["root_vault"]
    src_path = _find_first_file(root_vault, "file_0000.md")
    if src_path is None:
        fail("scenario_move: could not find file_0000.md under "
             "root_vault in the built corpus")
    rel = os.path.relpath(src_path, base).replace(os.sep, "/")
    with open(src_path, "rb") as fh:
        raw = fh.read()

    # The corpus file already exists on disk with these exact bytes, so
    # `journal.op_link` (which never writes the target) is used to bring it
    # under journal identity, the same way `scenario_duplicate` and
    # `operations_roundtrip.py`'s own corpus scenarios do.
    rec = journal.op_link(base, "source", rel, "human", "tracer")
    object_id = rec["object_id"]

    new_rel = "root_vault/moved_file_0000.md"
    moved = journal.op_move(base, object_id, new_rel, rec["fingerprint"],
                             "human", "tracer")

    if moved["object_id"] != object_id:
        fail("mixed state: scenario_move changed the object id")
    row = journal.read_registry(base)[object_id]
    if row["path"] != new_rel:
        fail("mixed state: scenario_move did not record the new path")
    if row["revision"] != rec["revision"] + 1:
        fail("mixed state: scenario_move did not advance the revision")
    new_path = os.path.join(base, new_rel)
    with open(new_path, "rb") as fh:
        new_bytes = fh.read()
    if new_bytes != raw:
        fail("mixed state: scenario_move: bytes at the new path are not "
             "byte-identical to the original")
    if os.path.exists(src_path):
        fail("mixed state: scenario_move left the old path's bytes behind")
    return "pass"


def scenario_duplicate(base, corpus):
    dup_a, dup_b = corpus["duplicate_pair"]
    rel_a = os.path.relpath(dup_a, base).replace(os.sep, "/")
    rel_b = os.path.relpath(dup_b, base).replace(os.sep, "/")
    with open(dup_a, "rb") as fh:
        raw_a = fh.read()
    with open(dup_b, "rb") as fh:
        raw_b = fh.read()

    rec_a = journal.op_link(base, "source", rel_a, "human", "tracer")
    rec_b = journal.op_link(base, "source", rel_b, "human", "tracer")

    candidates = journal.copy_candidates_from_registry(base)
    matching = [c for c in candidates
                if {c["object_id_a"], c["object_id_b"]} ==
                {rec_a["object_id"], rec_b["object_id"]}]
    if len(matching) != 1:
        fail("mixed state: scenario_duplicate did not find exactly one "
             "candidate pair for the duplicate-fingerprint pair: %r"
             % candidates)
    if matching[0]["path_a"] > matching[0]["path_b"]:
        fail("mixed state: scenario_duplicate's candidate pair was not "
             "path-sorted")

    registry = journal.read_registry(base)
    if rec_a["object_id"] not in registry or rec_b["object_id"] not in \
            registry:
        fail("mixed state: scenario_duplicate lost an id from the "
             "registry")
    with open(dup_a, "rb") as fh:
        if fh.read() != raw_a:
            fail("mixed state: scenario_duplicate changed duplicate_a.md's "
                 "bytes")
    with open(dup_b, "rb") as fh:
        if fh.read() != raw_b:
            fail("mixed state: scenario_duplicate changed duplicate_b.md's "
                 "bytes")
    return "pass"


def scenario_conflict(base):
    rel = "root_banks/conflict_test.md"
    path = os.path.join(base, rel)
    raw1 = b"# Conflict test\n\noriginal synthetic content\n"

    rec = journal.commit_operation(
        base, identity.new_object_id(), "source", rel, "mint", raw1,
        expected_fingerprint=None, actor_kind="human", actor_name="tracer",
        create_if_missing=True)
    object_id = rec["object_id"]

    raw2 = b"# Conflict test\n\nedited outside the journal\n"
    with open(path, "wb") as fh:
        fh.write(raw2)

    try:
        journal.commit_operation(
            base, object_id, "source", rel, "edit_in_place",
            b"attempted overwrite\n", expected_fingerprint=rec["fingerprint"],
            actor_kind="human", actor_name="tracer")
        fail("scenario_conflict: commit_operation against a conflicted "
             "object did not raise")
    except journal.JournalError as exc:
        if exc.code != "journal.conflict":
            fail("scenario_conflict: wrong refusal code: %r" % exc.code)
        if "Next safe action" not in exc.message:
            fail("scenario_conflict: refusal message carried no "
                 "next-safe-action sentence: %r" % exc.message)

    current = _assert_old_or_new(path, raw1, raw2, "conflict")
    if current != raw2:
        fail("mixed state: scenario_conflict: target bytes were not the "
             "externally-edited (new, out-of-band) content")

    return "pass", {"object_id": object_id, "rel": rel, "path": path,
                     "raw2": raw2}


def scenario_external_edit(base, state):
    object_id = state["object_id"]
    affected = journal.detect_external_edits(base)
    if object_id not in affected:
        fail("scenario_external_edit: detect_external_edits did not "
             "report the conflicted object")
    external_entries = [
        e for e in journal.entries(base)
        if e["object_id"] == object_id and e["operation"] == "external_edit"]
    if len(external_entries) != 1:
        fail("scenario_external_edit: expected exactly one external_edit "
             "record, found %d" % len(external_entries))
    if not external_entries[0]["before_fingerprint"] or \
            not external_entries[0]["after_fingerprint"]:
        fail("scenario_external_edit: the external_edit record did not "
             "carry both fingerprints: %r" % external_entries[0])

    second = journal.detect_external_edits(base)
    if second:
        fail("scenario_external_edit: a second immediate call was not "
             "idempotent, appended a record for: %r" % second)

    with open(state["path"], "rb") as fh:
        if fh.read() != state["raw2"]:
            fail("mixed state: scenario_external_edit changed the target's "
                 "bytes")
    return "pass"


def _root_for_path(path, roots):
    rp = os.path.realpath(path)
    for r in roots:
        rr = os.path.realpath(r)
        if rp == rr or rp.startswith(rr + os.sep):
            return r
    return None


def scenario_denied_path(base, corpus):
    roots = corpus["roots"]
    denied_path = corpus["denied_path"]
    root_for_denied = _root_for_path(denied_path, roots)
    denied_rel_to_root = os.path.relpath(
        denied_path, root_for_denied).replace(os.sep, "/")
    denied_rel_to_base = os.path.relpath(denied_path, base).replace(
        os.sep, "/")

    st_before = os.stat(denied_path)
    report = discovery.run_report(roots)
    st_after = os.stat(denied_path)
    if (st_before.st_size, st_before.st_mtime_ns) != \
            (st_after.st_size, st_after.st_mtime_ns):
        fail("mixed state: scenario_denied_path: the denied path's "
             "(size, mtime_ns) changed across a read-only inventory")

    if corpus["denied_mode"] == "write":
        print("SKIP: read-denial assertion (os.chmod cannot deny read on "
              "this platform)")
        try:
            journal.commit_operation(
                base, identity.new_object_id(), "source",
                denied_rel_to_base, "mint", b"attempted overwrite\n",
                expected_fingerprint=None, actor_kind="human",
                actor_name="tracer", create_if_missing=True)
            fail("scenario_denied_path: a write to a denied path did not "
                 "raise")
        except (journal.JournalError, OSError):
            pass
        return "skip"

    denied_entries = [e for e in report["entries"]
                       if e["path"] == denied_rel_to_root]
    if not denied_entries or denied_entries[0]["state"] != "denied":
        fail("scenario_denied_path: the denied path was not reported as "
             "denied: %r" % denied_entries)
    if denied_rel_to_root not in report["denied"]:
        fail("scenario_denied_path: the denied path is not named in "
             "report['denied']")
    return "pass"


def scenario_interrupted_write(base):
    object_id = identity.new_object_id()
    old_raw = b"old bytes\n"
    journal.commit_operation(
        base, object_id, "course", "target.md", "mint", old_raw,
        expected_fingerprint=None, actor_kind="human", actor_name="tracer",
        create_if_missing=True)
    target_path = os.path.join(base, "target.md")
    new_raw = b"new bytes from kill_before_commit\n"

    proc = subprocess.Popen(
        [sys.executable, journal_roundtrip.__file__, "--child",
         "kill_before_commit", base, object_id])
    time.sleep(0.5)
    proc.terminate()
    proc.wait()

    current = _assert_old_or_new(target_path, old_raw, new_raw,
                                  "interrupted_write")
    if current != old_raw:
        fail("mixed state: scenario_interrupted_write: expected the OLD "
             "bytes to survive a kill before commit")

    ordered = [e for e in journal.entries(base)
               if e.get("object_id") == object_id]
    last = ordered[-1]
    if last["state"] != "prepared":
        fail("scenario_interrupted_write: journal did not end with an "
             "unresolved prepared entry: %r" % last)

    result = journal.replay(base)
    matches = [e for e in result["interrupted"]
               if e["entry_id"] == last["entry_id"]]
    if not matches:
        fail("scenario_interrupted_write: replay() did not name the "
             "surviving (interrupted) state for this entry")
    return "pass"


def scenario_disk_full(base):
    object_id = identity.new_object_id()
    old_raw = b"old bytes\n"
    rel = "disk_full_target.md"
    journal.commit_operation(
        base, object_id, "course", rel, "mint", old_raw,
        expected_fingerprint=None, actor_kind="human", actor_name="tracer",
        create_if_missing=True)
    target_path = os.path.join(base, rel)
    new_raw = b"new bytes for disk full\n"

    real = journal._write_bytes_atomic

    def enospc_on_target(path, raw):
        if os.path.basename(path) == rel:
            raise OSError(errno.ENOSPC, "No space left on device")
        return real(path, raw)

    journal._write_bytes_atomic = enospc_on_target
    try:
        try:
            journal.commit_operation(
                base, object_id, "course", rel, "edit_in_place", new_raw,
                expected_fingerprint=identity.object_fingerprint(
                    old_raw, "course"),
                actor_kind="human", actor_name="tracer")
            fail("scenario_disk_full: a simulated ENOSPC on the target "
                 "write did not raise")
        except OSError as exc:
            if exc.errno != errno.ENOSPC:
                raise
    finally:
        journal._write_bytes_atomic = real

    current = _assert_old_or_new(target_path, old_raw, new_raw, "disk_full")
    if current != old_raw:
        fail("mixed state: scenario_disk_full: expected the OLD bytes to "
             "survive a simulated ENOSPC on the target write")
    registry = journal.read_registry(base)
    if registry[object_id]["revision"] != 1:
        fail("scenario_disk_full: the last accepted revision changed "
             "despite the refused write")
    if not list(journal.entries(base)):
        fail("scenario_disk_full: the journal became unreadable after the "
             "fault")
    return "pass"


def scenario_root_missing(base, corpus):
    roots = list(corpus["roots"])
    discovery.run_report(roots)

    victim = roots[-1]
    import shutil as _shutil
    _shutil.rmtree(victim)

    report2 = discovery.run_report(roots)
    if report2["unavailable"].count(victim) != 1:
        fail("scenario_root_missing: the removed root was not reported "
             "exactly once under unavailable: %r" % report2["unavailable"])

    remaining = [r for r in roots if r != victim]
    for r in remaining:
        entries_for_root = [e for e in report2["entries"] if e["root"] == r]
        if not entries_for_root:
            fail("scenario_root_missing: a surviving root returned no "
                 "entries after another root disappeared")

    registry = journal.read_registry(base)
    if not isinstance(registry, dict):
        fail("scenario_root_missing: journal.read_registry() became "
             "unreadable after a corpus root disappeared")
    return "pass"


# ---------------------------------------------------------------------------
# Shipped suite byte-compatibility (audit A6).


def shipped_suite_check():
    suites = ("scoring_roundtrip.py", "evidence_roundtrip.py",
              "audit_writer_roundtrip.py", "durability_roundtrip.py")
    results = {}
    for name in suites:
        path = os.path.join(TESTS_DIR, name)
        proc = subprocess.run([sys.executable, path], capture_output=True,
                               text=True)
        results[name] = proc.returncode
    failing = [name for name, rc in results.items() if rc != 0]
    if failing:
        fail("shipped_suite_check: non-zero exit for %s" % ", ".join(failing))
    print("shipped suite check: pass (%s)"
          % ", ".join("%s=0" % name for name in suites))
    return results


# ---------------------------------------------------------------------------


def main():
    scenario_results = []
    d = tempfile.mkdtemp()
    try:
        corpus = corpus_14a.build_corpus(d, size="1k")
        base = d

        scenario_results.append(("move", scenario_move(base, corpus)))
        scenario_results.append(
            ("duplicate", scenario_duplicate(base, corpus)))
        conflict_status, conflict_state = scenario_conflict(base)
        scenario_results.append(("conflict", conflict_status))
        scenario_results.append(
            ("external_edit", scenario_external_edit(base, conflict_state)))
        scenario_results.append(
            ("denied_path", scenario_denied_path(base, corpus)))
        scenario_results.append(
            ("interrupted_write", scenario_interrupted_write(base)))
        scenario_results.append(("disk_full", scenario_disk_full(base)))
        scenario_results.append(
            ("root_missing", scenario_root_missing(base, corpus)))
    finally:
        corpus_14a.teardown_corpus(d)

    for name, status in scenario_results:
        print("scenario %s: %s" % (name, status))

    shipped_suite_check()

    passed = sum(1 for _, status in scenario_results if status == "pass")
    skipped = sum(1 for _, status in scenario_results if status == "skip")
    print("TRACER: %d passed, %d skipped, 0 failed" % (passed, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
