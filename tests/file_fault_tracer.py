#!/usr/bin/env python3
"""The Phase 14A freeze gate: one scripted run walking all eight G3
scenarios end to end on the synthetic corpus, measuring the D-12.6-10
budgets on the 1k and 10k corpora, running the real-diff corpus check that
decides the deferred D-14A-2 reflow question, and confirming the shipped
parser/scorer/evidence suites still pass (audit A6).

Standard library only, runnable as `python tests/file_fault_tracer.py`.
Reuses the fault-injection helpers already written in
`tests/journal_roundtrip.py` (the `--child` subprocess fixtures) rather than
copying them: this tracer composes the phase's own proofs, it does not
rewrite them.

Every scenario asserts, explicitly, that the on-disk state is either the old
valid state or the new valid state; a state matching neither fails loudly
with a message beginning `"mixed state"` (RELIABILITY-01).
"""
import builtins
import errno
import hashlib
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, TESTS_DIR)
import discovery                                              # noqa: E402
import identity                                               # noqa: E402
import journal                                                # noqa: E402
import fixtures.corpus_14a as corpus_14a                      # noqa: E402
import journal_roundtrip                                      # noqa: E402
import source_adapters                                        # noqa: E402

REPORT_PATH = os.path.join(
    ROOT, ".planning", "phases", "14A-identity-lifecycle-operation",
    "14A-TRACER-REPORT.md")


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
# The reflow-normalization corpus check (D-14A-2's deferred half).


def _common_prefix_suffix_len(a, b):
    """The length of the shared prefix and the shared suffix of `a` and
    `b`, without ever counting the same character in both. Used instead of
    `difflib.SequenceMatcher` opcodes: this repository already found
    SequenceMatcher's opcodes alignment-dependent and non-minimal
    (14A-RESEARCH.md's Alternatives Considered, the 04-02 entry in
    STATE.md), so a direct prefix/suffix trim is used here instead."""
    n = min(len(a), len(b))
    p = 0
    while p < n and a[p] == b[p]:
        p += 1
    max_suffix = n - p
    s = 0
    while s < max_suffix and a[len(a) - 1 - s] == b[len(b) - 1 - s]:
        s += 1
    return p, s


def _collapse_ws(text):
    """Every run of whitespace, including newlines, collapsed to one
    space, with the result stripped. Two texts differing only by how
    much whitespace separates the same words compare equal after this."""
    return " ".join(text.split())


def _is_reflow_only(before_text, after_text):
    """True when `before_text` and `after_text` differ only by the amount
    or placement of whitespace (spaces, tabs, newlines), with no word,
    punctuation, or ordering change.

    The differing middle span is located with `_common_prefix_suffix_len`
    rather than `difflib.SequenceMatcher` opcodes, per the recorded 04-02
    caveat: SequenceMatcher's opcodes are alignment-dependent and
    non-minimal, and this repository already solved the same problem once
    with a prefix/suffix helper.
    """
    if before_text == after_text:
        return True
    p, s = _common_prefix_suffix_len(before_text, after_text)
    mid_before = before_text[p:len(before_text) - s] if s else \
        before_text[p:]
    mid_after = after_text[p:len(after_text) - s] if s else after_text[p:]
    return _collapse_ws(mid_before) == _collapse_ws(mid_after)


def _candidate_normalize(raw, kind):
    """The candidate reflow-normalizing variant this check measures only;
    it is never wired into `identity.normalize_for_fingerprint` unless
    Task 3's checkpoint selects option-b. Applies the shipped first-cut
    normalization first, then additionally collapses runs of whitespace
    (including newlines) within a paragraph before hashing.

    Never applied to kind `bank` or `lesson`: the keyed-content carve-out
    from D-14A-2 holds regardless of the reflow answer, so this function
    returns the plain first-cut normalization, unchanged, for those two
    kinds; the candidate rule is never measured against a kind it would
    never be allowed to ship for.
    """
    normalized = identity.normalize_for_fingerprint(raw, kind)
    if kind in identity.TRAILING_WS_EXEMPT_KINDS:
        return normalized
    text = normalized.decode("utf-8", errors="surrogateescape")
    paragraphs = text.split("\n\n")
    collapsed = [_collapse_ws(p) for p in paragraphs]
    collapsed_text = "\n\n".join(collapsed)
    return collapsed_text.encode("utf-8", errors="surrogateescape")


def _candidate_fingerprint(raw, kind):
    return "sha256:" + hashlib.sha256(
        _candidate_normalize(raw, kind)).hexdigest()


def reflow_corpus_check():
    """Build the 10k corpus, mutate a deterministic sample of it into four
    labelled classes, and count how many of the observed changes the
    shipped first-cut fingerprint notices, how many of those are
    reflow-only, how many the first cut already absorbs, and how many the
    candidate reflow-normalizing rule would absorb that are NOT
    reflow-only (the false-absorption count, and the reason to refuse the
    rule without more evidence). Every file mutated here fingerprints as
    kind `source`, so the `bank`/`lesson` carve-out is honored by
    `_candidate_normalize` itself, never exercised by this generic corpus.
    """
    d = tempfile.mkdtemp()
    try:
        corpus_14a.build_corpus(d, size="10k")
        mutation_count = 2000
        mutations = corpus_14a.mutate_corpus(d, mutation_count, seed=1400)

        meaningful = 0
        reflow_only_noticed = 0
        already_absorbed = 0
        false_absorption = 0
        class_counts = {}

        for _path, cls, before, after in mutations:
            class_counts[cls] = class_counts.get(cls, 0) + 1
            before_text = before.decode("utf-8", errors="surrogateescape")
            after_text = after.decode("utf-8", errors="surrogateescape")
            ground_truth_reflow = _is_reflow_only(before_text, after_text)

            first_before_fp = identity.object_fingerprint(before, "source")
            first_after_fp = identity.object_fingerprint(after, "source")
            first_differs = first_before_fp != first_after_fp

            cand_before_fp = _candidate_fingerprint(before, "source")
            cand_after_fp = _candidate_fingerprint(after, "source")
            cand_differs = cand_before_fp != cand_after_fp

            if first_differs and cls == "content":
                meaningful += 1
            if first_differs and ground_truth_reflow:
                reflow_only_noticed += 1
            if (not first_differs) and cls in ("trailing_ws", "line_ending"):
                already_absorbed += 1
            if (not cand_differs) and not ground_truth_reflow:
                false_absorption += 1

        total = len(mutations)
        proportions = {
            cls: (class_counts.get(cls, 0) / total if total else 0.0)
            for cls in ("content", "trailing_ws", "line_ending", "reflow")}
        recommendation = (
            "counts support keeping the first cut (option-a): nothing "
            "notices a change without a reason") if false_absorption == 0 \
            else ("the false-absorption count is nonzero; review before "
                  "adopting the candidate rule")

        result = {
            "total_mutations": total,
            "meaningful": meaningful,
            "reflow_only_noticed": reflow_only_noticed,
            "already_absorbed": already_absorbed,
            "false_absorption": false_absorption,
            "class_counts": class_counts,
            "proportions": proportions,
            "recommendation": recommendation,
        }
        print("reflow corpus check: %d mutations, meaningful: %d, "
              "reflow-only: %d, already-absorbed: %d, "
              "false-absorption: %d"
              % (total, meaningful, reflow_only_noticed, already_absorbed,
                 false_absorption))
        return result
    finally:
        corpus_14a.teardown_corpus(d)


# ---------------------------------------------------------------------------
# D-12.6-10 budget measurement. Never fails the tracer.


def measure_budgets():
    """Median-of-three measurements of the D-12.6-10 quantities on the 1k
    and 10k corpora: time to the first yielded `discovery.inventory`
    entry, time to a complete `discovery.run_report`, time from setting a
    cancel flag to the generator stopping, and peak traced Python memory
    during a full inventory (`tracemalloc`, not process RSS).

    Never fails the tracer (D-12.6-10's own wording: these are starting
    budgets to be measured against on real hardware, never promises); an
    honest slow number is recorded rather than a build turning red on a
    measurement.
    """
    results = {"python_version": sys.version,
               "platform": platform.platform()}
    for size in ("1k", "10k"):
        first_entry_ms = []
        full_report_s = []
        cancel_ms = []
        peak_mb = []
        for _ in range(3):
            d = tempfile.mkdtemp()
            try:
                corpus = corpus_14a.build_corpus(d, size=size)
                roots = corpus["roots"]

                t0 = time.perf_counter()
                gen = discovery.inventory(roots)
                try:
                    next(gen)
                except StopIteration:
                    pass
                t1 = time.perf_counter()
                gen.close()
                first_entry_ms.append((t1 - t0) * 1000.0)

                t2 = time.perf_counter()
                discovery.run_report(roots)
                t3 = time.perf_counter()
                full_report_s.append(t3 - t2)

                cancel_box = {"hit": False}

                def cancel():
                    return cancel_box["hit"]

                gen2 = discovery.inventory(roots, cancel=cancel)
                for _ in range(50):
                    try:
                        next(gen2)
                    except StopIteration:
                        break
                cancel_box["hit"] = True
                t4 = time.perf_counter()
                try:
                    next(gen2)
                except StopIteration:
                    pass
                t5 = time.perf_counter()
                cancel_ms.append((t5 - t4) * 1000.0)

                tracemalloc.start()
                discovery.run_report(roots)
                _current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                peak_mb.append(peak / (1024.0 * 1024.0))
            except Exception as exc:  # never fail the tracer on a measurement
                print("note: measure_budgets(%s) run raised %r; recorded "
                      "as a gap, not a failure" % (size, exc))
            finally:
                corpus_14a.teardown_corpus(d)

        results[size] = {
            "first_entry_ms": (statistics.median(first_entry_ms)
                                if first_entry_ms else None),
            "full_report_s": (statistics.median(full_report_s)
                               if full_report_s else None),
            "cancel_ms": statistics.median(cancel_ms) if cancel_ms else None,
            "peak_mb": statistics.median(peak_mb) if peak_mb else None,
            "run_count": len(first_entry_ms),
        }
        print("measured budgets (%s): first_entry=%s ms, full_report=%s s, "
              "cancel=%s ms, peak=%s MB, runs=%d"
              % (size, results[size]["first_entry_ms"],
                 results[size]["full_report_s"], results[size]["cancel_ms"],
                 results[size]["peak_mb"], results[size]["run_count"]))
    return results


# ---------------------------------------------------------------------------
# Report writer.


D_12_6_10_BUDGETS = {
    "first_entry_ms": ("first useful discovery result", "< 2000 ms on 10k"),
    "full_report_s": ("full inventory", "< 60 s on 100k (measured here on "
                       "1k/10k only; see The 100k corpus section)"),
    "cancel_ms": ("cancel response", "< 500 ms"),
    "peak_mb": ("memory", "bounded by streaming (no fixed number)"),
}


def _fmt(value, suffix=""):
    if value is None:
        return "not measured (see note)"
    return "%.2f%s" % (value, suffix)


def report_lines(scenario_results, shipped_results, reflow_result,
                  budgets):
    """Build the report as a list of lines. Building is separated from writing
    because an ordinary run compares and a re-record run writes, and both need
    the same text."""
    lines = []
    lines.append("# 14A tracer report")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append("- Date: 2026-08-18")
    lines.append("- Machine: the executor's own development machine "
                  "(local, not a shared or cloud host)")
    lines.append("- Platform: %s" % budgets["platform"])
    lines.append("- Python: %s" % budgets["python_version"].split()[0])
    lines.append("- Corpus sizes run: 1k, 10k")
    lines.append("- Run count behind each measured number: median of 3 "
                  "runs, stated again per row below")
    lines.append("")

    lines.append("## Scenario results")
    lines.append("")
    lines.append("| Scenario | Result |")
    lines.append("|---|---|")
    for name, status in scenario_results:
        if status == "skip":
            lines.append("| %s | skipped (SKIP: read-denial assertion, "
                          "os.chmod cannot deny read on this platform) |"
                          % name)
        else:
            lines.append("| %s | %s |" % (name, status))
    lines.append("")

    lines.append("## Measured quantities")
    lines.append("")
    lines.append("These are measurements taken on this machine, on this "
                  "run. They are not promises to any user or later phase "
                  "(D-12.6-10).")
    lines.append("")
    lines.append("| Quantity | Corpus | Measured | Unit | Runs | "
                  "D-12.6-10 starting budget |")
    lines.append("|---|---|---|---|---|---|")
    for size in ("1k", "10k"):
        b = budgets[size]
        lines.append("| first useful discovery result | %s | %s | ms | "
                      "%d | %s |"
                      % (size, _fmt(b["first_entry_ms"]), b["run_count"],
                         D_12_6_10_BUDGETS["first_entry_ms"][1]))
        lines.append("| full inventory | %s | %s | s | %d | %s |"
                      % (size, _fmt(b["full_report_s"]), b["run_count"],
                         D_12_6_10_BUDGETS["full_report_s"][1]))
        lines.append("| cancel response | %s | %s | ms | %d | %s |"
                      % (size, _fmt(b["cancel_ms"]), b["run_count"],
                         D_12_6_10_BUDGETS["cancel_ms"][1]))
        lines.append("| peak traced Python memory (not process RSS) | %s "
                      "| %s | MB | %d | %s |"
                      % (size, _fmt(b["peak_mb"]), b["run_count"],
                         D_12_6_10_BUDGETS["peak_mb"][1]))
    lines.append("")

    lines.append("## The 100k corpus")
    lines.append("")
    lines.append("Not run in 14A. The 14A brief's own 14A-04 text names "
                  "the 1k/10k corpora; the 100k size is D-12.6-10's "
                  "recommendation, not 14A's task, and generating 100k "
                  "files inside a suite CI runs on every push costs "
                  "minutes per run. Routed to 14B, per this plan's own "
                  "locked decision table.")
    lines.append("")

    lines.append("## Reflow corpus check")
    lines.append("")
    lines.append("- Total mutations: %d" % reflow_result["total_mutations"])
    lines.append("- Meaningful changes noticed by the first cut: %d"
                  % reflow_result["meaningful"])
    lines.append("- Reflow-only changes noticed by the first cut: %d"
                  % reflow_result["reflow_only_noticed"])
    lines.append("- Changes the first cut already absorbs (trailing "
                  "whitespace, line endings): %d"
                  % reflow_result["already_absorbed"])
    lines.append("- False-absorption count (candidate rule would absorb "
                  "a change that is NOT reflow-only): %d"
                  % reflow_result["false_absorption"])
    lines.append("- Mutation class proportions used: %s"
                  % ", ".join("%s=%.2f" % (k, v) for k, v in
                               sorted(reflow_result["proportions"].items())))
    lines.append("- Recommendation the counts support: %s"
                  % reflow_result["recommendation"])
    lines.append("")

    lines.append("## Shipped suite check")
    lines.append("")
    lines.append("| Suite | Exit code |")
    lines.append("|---|---|")
    for name, rc in shipped_results.items():
        lines.append("| %s | %d |" % (name, rc))
    lines.append("")
    lines.append("This closes the audit A6 obligation: the shipped "
                  "parser, scorer, and evidence suites pass unchanged "
                  "after 14A.")
    lines.append("")

    lines.append("## Open items routed forward")
    lines.append("")
    lines.append("- FILE-02's flagged unclassified edge (whether the "
                  "\"useful before completion\" clause implies a stable "
                  "partial-result identity beyond streaming plus "
                  "resume_after) was closed in 14A-01, not deferred here: "
                  "see 14A-01-SUMMARY.md's \"Disposition of the flagged "
                  "FILE-02 unclassified edge\" section.")
    lines.append("- ID-02's flagged unclassified edge (whether \"hashes "
                  "never prove authorship or rights\" implies an "
                  "obligation beyond keeping the fingerprint out of "
                  "rights decisions) was closed in 14A-03, not deferred "
                  "here: see 14A-03-SUMMARY.md's \"Disposition of the "
                  "flagged ID-02 unclassified edge\" section. A future "
                  "recorded rights grant, if wanted, is RIGHTS-02, owned "
                  "by 14B/15A.")
    lines.append("")

    lines.append("## How this report is kept")
    lines.append("")
    lines.append("This file is a durable 14A record, not a derived "
                  "artifact. `tests/file_fault_tracer.py` rebuilds it on "
                  "every run and compares, but writes only when asked with "
                  "`--write` (or `ITEMBANK_TRACER_WRITE=1`), so an ordinary "
                  "suite run leaves the committed bytes alone. The "
                  "comparison covers the scenario rows, the reflow counts, "
                  "the shipped-suite exit codes, the budget text, and the "
                  "routed-forward items. It excludes the Platform and "
                  "Python lines and the Measured column, because those are "
                  "facts about a machine and the section above already says "
                  "they are not promises. The numbers recorded here are "
                  "14A's own, restored in `53d5231` after two later runs "
                  "overwrote them by accident.")
    lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Recording versus checking.
#
# This report is a durable phase record, not a derived artifact: 14A is frozen
# and the numbers in it were reviewed. Rewriting it on every run made it both,
# which is the distinction the project refuses to collapse. Three commits paid
# for that: `9590eb4` and `4d59ceb` carried a later run's timings into 14C's
# work without meaning to, and `53d5231` had to put 14A's own numbers back and
# left the question of who owns the tracer open.
#
# So an ordinary run measures everything and writes nothing. It compares what
# it built against what is committed, on the part of the report that carries
# meaning: which scenarios ran and how they ended, the reflow counts (seeded,
# so they are reproducible), the shipped-suite exit codes, the budget text, and
# the routed-forward items. Machine facts are excluded by name, because the
# report's own sentence says the measurements are "taken on this machine, on
# this run" and "not promises". A number that is explicitly not a promise
# cannot also be a regression.
#
# Re-record deliberately with `--write`, or `ITEMBANK_TRACER_WRITE=1`.

MACHINE_LINE_PREFIXES = ("- Platform:", "- Python:")


def report_signature(lines):
    """The part of the report a later run must still reproduce.

    Drops the two machine-identity lines and blanks the Measured column of the
    measured-quantities table, keeping the quantity, corpus, unit, run count,
    and budget text. Everything else compares verbatim, so a renamed section, a
    dropped scenario, a changed reflow count, or a non-zero suite exit code
    still fails loudly.
    """
    signature = []
    for line in lines:
        if line.startswith(MACHINE_LINE_PREFIXES):
            signature.append(line.split(":", 1)[0] + ": (machine)")
            continue
        cells = line.split("|")
        # A measured row is `| quantity | corpus | value | unit | runs |
        # budget |`, which splits into eight cells with empty ends.
        if len(cells) == 8 and cells[4].strip() in ("ms", "s", "MB"):
            cells[3] = " (measured) "
            signature.append("|".join(cells))
            continue
        signature.append(line)
    return signature


def _trimmed(lines):
    trimmed = list(lines)
    while trimmed and not trimmed[-1].strip():
        trimmed.pop()
    return trimmed


def write_report(lines):
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def check_report(lines):
    """Compare against the committed record and leave it untouched.

    Fails with the first differing line rather than a diff, because one named
    line is what a reader needs to know which part of the contract moved.
    """
    if not os.path.exists(REPORT_PATH):
        fail("the tracer report is missing at %s; re-record it deliberately "
             "with `python3 tests/file_fault_tracer.py --write`"
             % os.path.relpath(REPORT_PATH, ROOT))
    with open(REPORT_PATH, encoding="utf-8") as fh:
        committed = fh.read().split("\n")
    # Both sides lose their trailing blank lines before comparing: the writer
    # ends the report with a blank line and then a newline, so a file read back
    # carries one more empty string than the list that produced it, and that
    # difference is about newlines rather than about the contract.
    built = _trimmed(report_signature(lines))
    recorded = _trimmed(report_signature(committed))
    if built == recorded:
        return
    for index, (a, b) in enumerate(zip(recorded, built)):
        if a != b:
            fail("the tracer report no longer describes this run at line %d:\n"
                 "  recorded: %s\n  this run: %s\n"
                 "Machine timings are excluded from this comparison, so this "
                 "is a contract change. Re-record it deliberately with "
                 "`python3 tests/file_fault_tracer.py --write` once you have "
                 "decided the change is right." % (index + 1, a, b))
    fail("the tracer report has %d lines and this run produced %d; re-record "
         "it deliberately with `python3 tests/file_fault_tracer.py --write` "
         "once you have decided the change is right."
         % (len(recorded), len(built)))


# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Plan 14C-02: the source pair. A source is TWO durable files, the derived
# Markdown and its locator sidecar, written under one logical operation. The
# eight scenarios above cover one file; this one covers the pair, and the
# property it asserts is that an `applied` source object never exists on disk
# without a valid sidecar beside it.


class _PartialWriteFile:
    """A file object that creates the temp file, writes a fragment, and then
    fails the way a full disk fails: partway, with the fragment on disk."""

    def __init__(self, real_open, path):
        self._fh = real_open(path, "wb")
        self._fh.write(b"{\"partial\":")

    def write(self, raw):
        raise OSError(errno.EIO, "injected partial sidecar write")

    def flush(self):
        self._fh.flush()

    def fileno(self):
        return self._fh.fileno()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self._fh.close()
        return False


def _seed_source_pair(base, name, body):
    rel = name + ".md"
    with open(os.path.join(base, rel), "w", encoding="utf-8") as fh:
        fh.write(body)
    record = journal.op_link(base, "source", rel, "human", "tracer",
                             rights={op: "granted"
                                     for op in identity.RIGHTS_OPERATIONS})
    return rel, record["object_id"]


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


def _sidecars(base):
    return sorted(n for n in os.listdir(base) if n.endswith(".locator.json"))


def _temps(base):
    return sorted(n for n in os.listdir(base) if n.endswith(".tmp"))


def check_two_file_pair_atomicity(base):
    accepted_rel, accepted_id = _seed_source_pair(base, "accepted",
                                                   "# Accepted\n\nOne line.\n")
    first = source_adapters.import_source(base, "markdown", accepted_id,
                                           "human", "tracer")
    if first["status"] != "ok":
        fail("two_file_pair: the seeded import failed: %r" % (first["error"],))
    accepted_md = os.path.join(base, first["md_rel_path"])
    accepted_sidecar = os.path.join(base, first["sidecar_rel_path"])
    md_before = _read(accepted_md)
    sidecar_before = _read(accepted_sidecar)
    # --- 1. the sidecar write fails partway --------------------------------
    # The counts are taken after seeding, not before: linking a raw file is
    # itself a journalled operation, so a count taken earlier would charge
    # this scenario for the link it needs to run at all.
    _next_rel, next_id = _seed_source_pair(base, "one", "# One\n\nBody.\n")
    applied_before = [e for e in journal.entries(base)
                      if e.get("state") == "applied"]
    real_open = builtins.open

    def failing_open(path, mode="r", *args, **kwargs):
        if isinstance(path, str) and path.endswith(".locator.json.tmp"):
            return _PartialWriteFile(real_open, path)
        return real_open(path, mode, *args, **kwargs)

    builtins.open = failing_open
    try:
        result = source_adapters.import_source(base, "markdown", next_id,
                                               "human", "tracer")
    finally:
        builtins.open = real_open
    if result["status"] != "unsupported":
        fail("two_file_pair: a failed sidecar write reported %r rather than a "
             "typed refusal" % result["status"])
    if _read(accepted_md) != md_before or \
            _read(accepted_sidecar) != sidecar_before:
        fail("mixed state: two_file_pair scenario 1 disturbed the previously "
             "accepted pair")
    if _sidecars(base) != [os.path.basename(accepted_sidecar)]:
        fail("mixed state: two_file_pair scenario 1 left a sidecar for an "
             "object that was never applied: %r" % _sidecars(base))
    if _temps(base):
        fail("two_file_pair scenario 1 left a temp file behind: %r"
             % _temps(base))
    if len([e for e in journal.entries(base)
            if e.get("state") == "applied"]) != len(applied_before):
        fail("two_file_pair scenario 1 added an applied journal entry")

    # --- 2. the sidecar lands and the journal append then fails ------------
    _two_rel, two_id = _seed_source_pair(base, "two", "# Two\n\nBody.\n")
    registry_before = journal.read_registry(base)
    real_commit = journal.commit_operation

    def refusing_commit(*args, **kwargs):
        raise journal.JournalError("journal.injected",
                                    "injected append failure")

    journal.commit_operation = refusing_commit
    try:
        source_adapters.import_source(base, "markdown", two_id, "human",
                                       "tracer")
        fail("two_file_pair scenario 2: a refused journal append did not "
             "raise JournalError out of import_source")
    except journal.JournalError as exc:
        if exc.code != "journal.injected":
            raise
    finally:
        journal.commit_operation = real_commit
    if _read(accepted_md) != md_before:
        fail("mixed state: two_file_pair scenario 2 disturbed the previously "
             "accepted Markdown")
    if _sidecars(base) != [os.path.basename(accepted_sidecar)]:
        fail("mixed state: two_file_pair scenario 2 left an orphan sidecar "
             "with no journal entry: %r" % _sidecars(base))
    registry_after = journal.read_registry(base)
    new_ids = set(registry_after) - set(registry_before)
    if new_ids:
        fail("two_file_pair scenario 2 registered a source object %r despite "
             "the refused append" % sorted(new_ids))

    # --- 3. the append succeeds and the process stops right after ----------
    _three_rel, three_id = _seed_source_pair(base, "three",
                                              "# Three\n\nBody.\n")
    result = source_adapters.import_source(base, "markdown", three_id,
                                           "human", "tracer")
    if result["status"] != "ok":
        fail("two_file_pair scenario 3: the import failed: %r"
             % (result["error"],))
    md_path = os.path.join(base, result["md_rel_path"])
    sidecar_path = os.path.join(base, result["sidecar_rel_path"])
    if not os.path.exists(md_path) or not os.path.exists(sidecar_path):
        fail("mixed state: two_file_pair scenario 3 left half a pair")
    import json as _json
    sidecar = _json.loads(_read(sidecar_path).decode("utf-8"))
    registry = journal.read_registry(base)
    row = registry.get(sidecar["source_id"])
    if row is None:
        fail("two_file_pair scenario 3: the applied source is not in the "
             "registry")
    if row["fingerprint"] != sidecar["fingerprint"]:
        fail("mixed state: two_file_pair scenario 3: the sidecar and the "
             "registry disagree on the fingerprint")
    # `replay` re-reads every target rather than trusting the log, so a clean
    # verdict here means the applied pair on disk is the pair the journal says
    # it is, which is the reproducibility this scenario is asserting.
    replayed = journal.replay(base)["objects"]
    if replayed.get(sidecar["source_id"]) != "clean":
        fail("two_file_pair scenario 3: replay reports the applied source as "
             "%r rather than clean" % replayed.get(sidecar["source_id"]))
    if journal.read_registry(base) != registry:
        fail("two_file_pair scenario 3: reading the registry twice did not "
             "reproduce the same rows")

    # The property, stated once over the whole base rather than per scenario:
    # an applied IMPORT is the operation that writes a pair, so every applied
    # import entry must have a sidecar beside its derived Markdown. A linked
    # raw file is a source object too and has no sidecar by design, which is
    # why the filter is on the operation and not on the file suffix.
    for entry in journal.entries(base):
        if entry.get("state") != "applied" or entry.get("operation") != "import":
            continue
        rel = entry["path"]
        sidecar_name = source_adapters.sidecar_path_for(rel)
        if not os.path.exists(os.path.join(base, sidecar_name)):
            fail("mixed state: %s is an applied source object with no sidecar "
                 "beside it" % rel)
    return "pass"


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
        pair_base = tempfile.mkdtemp(prefix="two-file-pair-")
        try:
            scenario_results.append(
                ("check_two_file_pair_atomicity",
                 check_two_file_pair_atomicity(pair_base)))
        finally:
            shutil.rmtree(pair_base, ignore_errors=True)
    finally:
        corpus_14a.teardown_corpus(d)

    for name, status in scenario_results:
        print("scenario %s: %s" % (name, status))

    shipped_results = shipped_suite_check()
    reflow_result = reflow_corpus_check()
    budgets = measure_budgets()

    lines = report_lines(scenario_results, shipped_results, reflow_result,
                         budgets)
    if "--write" in sys.argv[1:] or os.environ.get("ITEMBANK_TRACER_WRITE"):
        write_report(lines)
        print("report: re-recorded %s" % os.path.relpath(REPORT_PATH, ROOT))
    else:
        check_report(lines)
        print("report: matches the committed record (timings excluded); "
              "re-record with --write")

    passed = sum(1 for _, status in scenario_results if status == "pass")
    skipped = sum(1 for _, status in scenario_results if status == "skip")
    print("TRACER: %d passed, %d skipped, 0 failed" % (passed, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
