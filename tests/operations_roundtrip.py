#!/usr/bin/env python3
"""Proves the six lifecycle operations end to end: distinct identity and
provenance effects sharing one write path, external-edit detection and
explicit reconciliation, and the per-operation rights gate on import and
copy.

Standard library only, runnable as `python tests/operations_roundtrip.py`,
with a `--child` mode used by the concurrency fixture the way
`tests/journal_roundtrip.py` uses its own `--child` mode.
"""
import os
import shutil
import sys
import tempfile
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import identity                                               # noqa: E402
import journal                                                # noqa: E402
import fixtures.corpus_14a as corpus_14a                     # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def _mkbase():
    return tempfile.mkdtemp()


def _write(base, rel_path, raw):
    path = os.path.join(base, rel_path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(raw)
    return path


# ---------------------------------------------------------------------------
# Task 1: the six operations as one write path with six identity effects


def check_operations():
    if journal.OPERATION_TYPES != ("link", "import", "copy", "move",
                                    "edit_in_place", "supersede") or \
            len(journal.OPERATION_TYPES) != 6:
        fail("journal.OPERATION_TYPES did not equal the six-name tuple: %r"
             % (journal.OPERATION_TYPES,))

    d = _mkbase()
    try:
        _check_link(d)
        _check_import_and_copy(d)
        _check_move(d)
        _check_edit_in_place(d)
        _check_supersede(d)
        _check_all_six_names_appear(d)
        _check_duplicate_pair(d)
        _check_near_duplicate_pair(d)
        _check_unicode_normalization(d)
        _check_move_candidates(d)
        _check_empty_candidates(d)
        _check_candidate_ordering(d)
        _check_unknown_operation_skip(d)
        print("OK check_operations")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    _check_concurrent_operations()


def _check_link(d):
    rel_path = "link_target.md"
    _write(d, rel_path, b"# Linked\n\nBytes that stay where they live.\n")
    target_path = os.path.join(d, rel_path)
    mtime_before = os.stat(target_path).st_mtime_ns

    rec = journal.op_link(d, "source", rel_path, "human", "weibao")
    if rec["revision"] != 1 or rec["parent_revision"] is not None:
        fail("op_link did not mint revision 1 with parent_revision None: %r"
             % rec)

    mtime_after = os.stat(target_path).st_mtime_ns
    if mtime_after != mtime_before:
        fail("op_link changed the target's mtime_ns: %r -> %r"
             % (mtime_before, mtime_after))

    entries = [e for e in journal.entries(d) if e["object_id"] ==
               rec["object_id"]]
    if not entries or entries[-1]["operation"] != "link":
        fail("op_link did not append an entry with operation 'link': %r"
             % entries)


def _check_import_and_copy(d):
    source_rec = journal.commit_operation(
        d, identity.new_object_id(), "source", "source_material.md",
        "mint", b"# Source\n\noriginal material\n", expected_fingerprint=None,
        actor_kind="human", actor_name="weibao", create_if_missing=True,
        rights={"read": "granted", "quote": "granted",
                "transform": "granted", "remote_process": "unknown",
                "package": "unknown", "export": "unknown",
                "share": "unknown"})
    source_id = source_rec["object_id"]
    source_row_before = dict(journal.read_registry(d)[source_id])

    imported = journal.op_import(
        d, source_id, "bank", "imported_bank.md", b"# Imported\n\nbank\n",
        "human", "weibao")
    if imported["revision"] != 1 or imported["parent_revision"] is not None:
        fail("op_import did not mint revision 1: %r" % imported)
    if imported["object_id"] == source_id:
        fail("op_import did not mint a new object id")
    imported_entry = [e for e in journal.entries(d)
                       if e["object_id"] == imported["object_id"]
                       and e["state"] == "applied"][0]
    if imported_entry["source_object_id"] != source_id or \
            imported_entry["source_revision"] != 1:
        fail("op_import did not record source_object_id/source_revision: %r"
             % imported_entry)

    copied = journal.op_copy(
        d, source_id, "bank", "copied_bank.md", b"# Copied\n\nbank\n",
        "human", "weibao")
    if copied["object_id"] in (source_id, imported["object_id"]):
        fail("op_copy did not mint a distinct new object id")
    copied_entry = [e for e in journal.entries(d)
                     if e["object_id"] == copied["object_id"]
                     and e["state"] == "applied"][0]
    if copied_entry["source_object_id"] != source_id or \
            copied_entry["source_revision"] != 1:
        fail("op_copy did not record source_object_id/source_revision: %r"
             % copied_entry)

    source_row_after = journal.read_registry(d)[source_id]
    if source_row_after != source_row_before:
        fail("the source object's own registry row changed after import "
             "and copy: %r -> %r" % (source_row_before, source_row_after))

    with open(os.path.join(d, "imported_bank.md"), "rb") as fh:
        if fh.read() != b"# Imported\n\nbank\n":
            fail("op_import did not actually write the new owned artifact")
    with open(os.path.join(d, "copied_bank.md"), "rb") as fh:
        if fh.read() != b"# Copied\n\nbank\n":
            fail("op_copy did not actually write the new owned artifact")


def _check_move(d):
    object_id = identity.new_object_id()
    rec = journal.commit_operation(
        d, object_id, "lesson", "before_move/lesson.md", "mint",
        b"# Lesson\n\nbefore move\n", expected_fingerprint=None,
        actor_kind="human", actor_name="weibao", create_if_missing=True)
    fp_before = rec["fingerprint"]

    moved = journal.op_move(
        d, object_id, "after_move/lesson.md", fp_before, "human", "weibao")
    if moved["object_id"] != object_id:
        fail("op_move did not keep the object id: %r vs %r"
             % (moved["object_id"], object_id))
    if moved["revision"] != 2 or moved["parent_revision"] != 1:
        fail("op_move did not advance the revision by one: %r" % moved)
    if moved["fingerprint"] != fp_before:
        fail("op_move changed the fingerprint though the bytes did not "
             "change: %r vs %r" % (moved["fingerprint"], fp_before))

    row = journal.read_registry(d)[object_id]
    if row["path"] != "after_move/lesson.md":
        fail("op_move did not change the recorded path: %r" % row["path"])
    if os.path.exists(os.path.join(d, "before_move/lesson.md")):
        fail("op_move left the old file behind")
    with open(os.path.join(d, "after_move/lesson.md"), "rb") as fh:
        if fh.read() != b"# Lesson\n\nbefore move\n":
            fail("op_move did not carry the bytes to the new path")

    move_entry = [e for e in journal.entries(d) if e["object_id"] ==
                  object_id and e["operation"] == "move"][-1]
    if "before_move/lesson.md" not in (move_entry.get("message") or ""):
        fail("op_move did not record the previous path in the entry's "
             "message/note: %r" % move_entry.get("message"))


def _check_edit_in_place(d):
    object_id = identity.new_object_id()
    rec = journal.commit_operation(
        d, object_id, "course", "edit_target.md", "mint",
        b"# Course\n\nfirst\n", expected_fingerprint=None,
        actor_kind="human", actor_name="weibao", create_if_missing=True)
    fp1 = rec["fingerprint"]

    edited = journal.op_edit_in_place(
        d, object_id, "course", "edit_target.md", b"# Course\n\nsecond\n",
        fp1, "human", "weibao")
    if edited["object_id"] != object_id:
        fail("op_edit_in_place did not keep the object id")
    if edited["revision"] != 2 or edited["parent_revision"] != 1:
        fail("op_edit_in_place did not advance the revision by one: %r"
             % edited)
    row = journal.read_registry(d)[object_id]
    if row["path"] != "edit_target.md":
        fail("op_edit_in_place changed the path: %r" % row["path"])


def _check_supersede(d):
    old_id = identity.new_object_id()
    journal.commit_operation(
        d, old_id, "objective", "old_objective.md", "mint",
        b"# Objective\n\nold phrasing\n", expected_fingerprint=None,
        actor_kind="human", actor_name="weibao", create_if_missing=True)
    new_id = identity.new_object_id()
    new_rec = journal.commit_operation(
        d, new_id, "objective", "new_objective.md", "mint",
        b"# Objective\n\nnew phrasing\n", expected_fingerprint=None,
        actor_kind="human", actor_name="weibao", create_if_missing=True)

    result = journal.op_supersede(
        d, new_id, old_id, new_rec["fingerprint"], "human", "weibao")
    if result["object_id"] != new_id:
        fail("op_supersede's return value was not the superseding object's "
             "revision record: %r" % result)

    registry = journal.read_registry(d)
    if old_id not in registry or new_id not in registry:
        fail("op_supersede removed a row from the registry")
    if registry[old_id]["superseded_by"] != new_id:
        fail("the superseded row did not gain superseded_by: %r"
             % registry[old_id])
    if registry[new_id]["supersedes"] != old_id:
        fail("the superseding row did not gain supersedes: %r"
             % registry[new_id])
    if not os.path.exists(os.path.join(d, "old_objective.md")) or \
            not os.path.exists(os.path.join(d, "new_objective.md")):
        fail("op_supersede deleted a file; both must survive")

    try:
        journal.op_supersede(
            d, new_id, new_id, registry[new_id]["fingerprint"], "human",
            "weibao")
        fail("op_supersede(new_id, new_id, ...) did not raise")
    except journal.JournalError as exc:
        if exc.code != "journal.supersede_self":
            fail("supersede-self raised the wrong code: %r" % exc.code)


def _check_all_six_names_appear(d):
    ops_seen = set(e["operation"] for e in journal.entries(d))
    for name in journal.OPERATION_TYPES:
        if name not in ops_seen:
            fail("operation %r never appeared in the journal log after the "
                 "scripted six-operation run" % name)
    for name in journal.OPERATION_TYPES:
        count = sum(1 for e in journal.entries(d)
                    if e["operation"] == name and e["state"] == "applied")
        if count < 1:
            fail("operation %r has no applied entry after the scripted "
                 "run" % name)


def _check_duplicate_pair(d):
    corpus_dir = tempfile.mkdtemp()
    try:
        corpus = corpus_14a.build_corpus(corpus_dir, size="1k")
        dup_a, dup_b = corpus["duplicate_pair"]
        rel_a = os.path.relpath(dup_a, corpus_dir).replace(os.sep, "/")
        rel_b = os.path.relpath(dup_b, corpus_dir).replace(os.sep, "/")
        with open(dup_a, "rb") as fh:
            raw_a = fh.read()
        with open(dup_b, "rb") as fh:
            raw_b = fh.read()

        rec_a = journal.op_link(corpus_dir, "source", rel_a, "human",
                                 "weibao")
        rec_b = journal.op_link(corpus_dir, "source", rel_b, "human",
                                 "weibao")
        if rec_a["object_id"] == rec_b["object_id"]:
            fail("op_link minted the same id for two distinct duplicate "
                 "files")

        candidates = journal.copy_candidates_from_registry(corpus_dir)
        matching = [c for c in candidates
                    if {c["object_id_a"], c["object_id_b"]} ==
                    {rec_a["object_id"], rec_b["object_id"]}]
        if len(matching) != 1:
            fail("copy_candidates_from_registry did not return exactly "
                 "one pair for the duplicate-fingerprint pair: %r"
                 % candidates)
        if matching[0]["path_a"] > matching[0]["path_b"]:
            fail("copy_candidates_from_registry did not return the pair "
                 "in path-sorted order: %r" % matching[0])

        registry = journal.read_registry(corpus_dir)
        if rec_a["object_id"] not in registry or \
                rec_b["object_id"] not in registry:
            fail("copy_candidates_from_registry's caller lost an id after "
                 "the call")
        with open(dup_a, "rb") as fh:
            if fh.read() != raw_a:
                fail("duplicate_a.md's bytes changed after the copy "
                     "candidate call")
        with open(dup_b, "rb") as fh:
            if fh.read() != raw_b:
                fail("duplicate_b.md's bytes changed after the copy "
                     "candidate call")
    finally:
        corpus_14a.teardown_corpus(corpus_dir)


def _check_near_duplicate_pair(d):
    corpus_dir = tempfile.mkdtemp()
    try:
        corpus = corpus_14a.build_corpus(corpus_dir, size="1k")
        notes_a, notes_b = corpus["near_duplicate_pair"]
        rel_a = os.path.relpath(notes_a, corpus_dir).replace(os.sep, "/")
        rel_b = os.path.relpath(notes_b, corpus_dir).replace(os.sep, "/")

        rec_a = journal.op_link(corpus_dir, "source", rel_a, "human",
                                 "weibao")
        rec_b = journal.op_link(corpus_dir, "source", rel_b, "human",
                                 "weibao")
        if rec_a["object_id"] == rec_b["object_id"]:
            fail("op_link minted the same id for two near-identically "
                 "named, byte-different files")

        hints = journal.name_hints(corpus_dir, "notes.md")
        hint_paths = set(h["path"] for h in hints)
        if rel_a not in hint_paths and rel_b not in hint_paths:
            fail("name_hints did not surface either near-identically "
                 "named file: %r" % hints)
        for h in hints:
            if h.get("hint") is not True:
                fail("a name_hints result did not carry hint=True: %r" % h)
    finally:
        corpus_14a.teardown_corpus(corpus_dir)


def _check_unicode_normalization(d):
    unicode_dir = tempfile.mkdtemp()
    try:
        nfc_name = unicodedata.normalize("NFC", "café.md")
        nfd_name = unicodedata.normalize("NFD", "café.md")
        if nfc_name == nfd_name:
            fail("the test's own NFC/NFD names were byte-identical; the "
                 "test fixture is broken")
        # The two variants are placed in separate subdirectories: some
        # filesystems (APFS on this machine included) silently normalize a
        # filename on write, so two names differing only in normalization
        # form would collide onto one directory entry if placed side by
        # side in the same directory. Separate directories keep both
        # variants genuinely on disk so this test proves identity.py's own
        # no-normalization guarantee, not a filesystem's normalization
        # behavior.
        os.makedirs(os.path.join(unicode_dir, "nfc"))
        os.makedirs(os.path.join(unicode_dir, "nfd"))
        nfc_rel = "nfc/" + nfc_name
        nfd_rel = "nfd/" + nfd_name
        with open(os.path.join(unicode_dir, nfc_rel), "wb") as fh:
            fh.write(b"precomposed accent\n")
        with open(os.path.join(unicode_dir, nfd_rel), "wb") as fh:
            fh.write(b"combining accent\n")

        rec_nfc = journal.op_link(unicode_dir, "source", nfc_rel, "human",
                                   "weibao")
        rec_nfd = journal.op_link(unicode_dir, "source", nfd_rel, "human",
                                   "weibao")
        if rec_nfc["object_id"] == rec_nfd["object_id"]:
            fail("NFC and NFD names minted the same object id")
        if rec_nfc["fingerprint"] == rec_nfd["fingerprint"]:
            fail("NFC and NFD names with different bytes fingerprinted "
                 "identically")
    finally:
        shutil.rmtree(unicode_dir, ignore_errors=True)


def _check_move_candidates(d):
    md = _mkbase()
    try:
        object_id = identity.new_object_id()
        rec = journal.commit_operation(
            md, object_id, "source", "orig/moved.md",
            "mint", b"# Moved\n\ncontent\n", expected_fingerprint=None,
            actor_kind="human", actor_name="weibao", create_if_missing=True)
        row = journal.read_registry(md)[object_id]

        legitimate = [{"path": "new/moved.md", "fingerprint":
                       rec["fingerprint"], "object_id": object_id,
                       "revision": row["revision"],
                       "parent_revision": row["parent_revision"]}]
        candidates = journal.move_candidates(md, legitimate)
        if len(candidates) != 1 or candidates[0]["object_id"] != object_id:
            fail("move_candidates did not accept a legitimate lineage-"
                 "matched candidate: %r" % candidates)

        fabricated = [{"path": "hijack/moved.md", "fingerprint":
                       rec["fingerprint"], "object_id": object_id,
                       "revision": 99, "parent_revision": 98}]
        try:
            journal.move_candidates(md, fabricated)
            fail("move_candidates accepted a fabricated entry with a "
                 "broken revision lineage")
        except journal.JournalError as exc:
            if exc.code != "journal.move_lineage_mismatch":
                fail("a fabricated lineage raised the wrong code: %r"
                     % exc.code)
    finally:
        shutil.rmtree(md, ignore_errors=True)


def _check_empty_candidates(d):
    ed = _mkbase()
    try:
        if journal.copy_candidates_from_registry(ed) != []:
            fail("copy_candidates_from_registry over an empty registry "
                 "did not return []")
        if journal.move_candidates(ed, []) != []:
            fail("move_candidates(base, []) did not return []")
        if journal.name_hints(ed, "") != []:
            fail("name_hints(base, '') over an empty registry did not "
                 "return []")
        if journal.duplicate_groups(ed) != []:
            fail("duplicate_groups over an empty registry did not return "
                 "[]")
    finally:
        shutil.rmtree(ed, ignore_errors=True)


def _check_candidate_ordering(d):
    od = _mkbase()
    try:
        raw = b"# Ordering\n\nsame content for every copy\n"
        recs = []
        for name in ("z_third.md", "a_first.md", "m_second.md"):
            object_id = identity.new_object_id()
            rec = journal.commit_operation(
                od, object_id, "source", name, "mint", raw,
                expected_fingerprint=None, actor_kind="human",
                actor_name="weibao", create_if_missing=True)
            recs.append(rec)

        first = journal.copy_candidates_from_registry(od)
        second = journal.copy_candidates_from_registry(od)
        if first != second:
            fail("copy_candidates_from_registry was not stably ordered "
                 "across two calls: %r vs %r" % (first, second))
        paths_a = [c["path_a"] for c in first]
        if paths_a != sorted(paths_a):
            fail("copy_candidates_from_registry did not return path-"
                 "sorted results: %r" % first)

        groups = journal.duplicate_groups(od)
        if len(groups) != 1 or len(groups[0]["objects"]) != 3:
            fail("duplicate_groups did not find the three-way duplicate "
                 "group: %r" % groups)
        group_paths = [o["path"] for o in groups[0]["objects"]]
        if group_paths != sorted(group_paths):
            fail("duplicate_groups did not sort its group by path: %r"
                 % group_paths)
    finally:
        shutil.rmtree(od, ignore_errors=True)


def _check_unknown_operation_skip(d):
    ud = _mkbase()
    try:
        object_id = identity.new_object_id()
        journal.commit_operation(
            ud, object_id, "course", "known.md", "mint", b"x",
            expected_fingerprint=None, actor_kind="human",
            actor_name="weibao", create_if_missing=True)
        with open(journal.log_path(ud), "a", encoding="utf-8") as fh:
            import json as _json
            fh.write(_json.dumps({"operation": "not_a_real_operation",
                                   "state": "applied",
                                   "object_id": "ffffffffffffffff"}) + "\n")
        seen_ops = set(e["operation"] for e in journal.entries(ud))
        if "not_a_real_operation" in seen_ops:
            fail("entries() yielded a record with an unrecognized "
                 "operation instead of skipping it")
    finally:
        shutil.rmtree(ud, ignore_errors=True)


def _child_concurrent_holder(base):
    real = journal._write_bytes_atomic

    def shim(path, raw):
        if os.path.basename(path) == "contended.md":
            time.sleep(0.8)
        return real(path, raw)

    journal._write_bytes_atomic = shim
    journal.commit_operation(
        base, "cccccccccccccccc", "course", "contended.md", "mint",
        b"holder bytes\n", expected_fingerprint=None, actor_kind="human",
        actor_name="weibao", create_if_missing=True)


def _child_concurrent_waiter(base):
    journal.LOCK_TIMEOUT_SECONDS = 0.3
    try:
        journal.commit_operation(
            base, identity.new_object_id(), "course", "waiter_only.md",
            "mint", b"waiter bytes\n", expected_fingerprint=None,
            actor_kind="human", actor_name="weibao", create_if_missing=True)
        sys.exit(0)
    except journal.JournalError as exc:
        sys.stderr.write(exc.code + "\n")
        sys.exit(1)


def _check_concurrent_operations():
    import subprocess
    d = _mkbase()
    try:
        holder = subprocess.Popen(
            [sys.executable, __file__, "--child", "concurrent_holder", d])
        time.sleep(0.15)
        waiter = subprocess.Popen(
            [sys.executable, __file__, "--child", "concurrent_waiter", d],
            stderr=subprocess.PIPE)
        _, waiter_err = waiter.communicate()
        holder.wait()

        if holder.returncode != 0:
            fail("the concurrent holder process did not exit 0")
        if waiter.returncode == 0:
            fail("the concurrent waiter process succeeded even though the "
                 "holder still had the lock")
        if b"journal.busy" not in waiter_err:
            fail("the concurrent waiter's stderr did not name "
                 "journal.busy: %r" % waiter_err)
        print("OK check_concurrent_operations")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# Task 2: external-edit states, conflicted reads, explicit reconciliation


def check_external_edits():
    d = _mkbase()
    try:
        object_id = identity.new_object_id()
        raw1 = b"# Course\n\naccepted content\n"
        rec1 = journal.commit_operation(
            d, object_id, "course", "conflicted.md", "mint", raw1,
            expected_fingerprint=None, actor_kind="human",
            actor_name="weibao", create_if_missing=True)
        target_path = os.path.join(d, "conflicted.md")

        with open(target_path, "wb") as fh:
            fh.write(b"# Course\n\nedited outside the journal\n")
        if journal.object_state(d, object_id) != "conflict":
            fail("object_state did not report conflict after an "
                 "out-of-band edit")

        read = journal.read_object(d, object_id)
        if read["bytes"] != b"# Course\n\nedited outside the journal\n":
            fail("read_object did not return the current on-disk bytes "
                 "for a conflicted object")
        if read["state"] != "conflict":
            fail("read_object did not name the conflict state: %r" % read)
        if read["revision"] != 1:
            fail("read_object did not report the last accepted revision: "
                 "%r" % read)
        if read["accepted_fingerprint"] != rec1["fingerprint"]:
            fail("read_object's accepted_fingerprint did not equal the "
                 "last journaled fingerprint: %r" % read)
        if read["fingerprint"] == read["accepted_fingerprint"]:
            fail("read_object's on-disk fingerprint equalled the accepted "
                 "one even though the bytes diverged")

        on_disk_fp = read["fingerprint"]
        try:
            journal.commit_operation(
                d, object_id, "course", "conflicted.md", "edit_in_place",
                b"# Course\n\nattempted overwrite\n",
                expected_fingerprint=rec1["fingerprint"], actor_kind="human",
                actor_name="weibao")
            fail("commit_operation against a conflicted object with the "
                 "stale accepted fingerprint did not raise")
        except journal.JournalError as exc:
            if exc.code != "journal.conflict":
                fail("a write against a conflicted object raised the "
                     "wrong code: %r" % exc.code)
            if "This is a conflict, not an overwrite." not in exc.message:
                fail("the conflict message did not contain the exact "
                     "sentence: %r" % exc.message)
            if "Next safe action: read the object, reconcile the " \
                    "difference by hand," not in exc.message:
                fail("the conflict message did not contain the exact "
                     "next-safe-action sentence: %r" % exc.message)

        try:
            journal.commit_operation(
                d, object_id, "course", "conflicted.md", "edit_in_place",
                b"# Course\n\nattempted overwrite\n",
                expected_fingerprint=on_disk_fp, actor_kind="human",
                actor_name="weibao")
            fail("commit_operation against a conflicted object with the "
                 "on-disk fingerprint did not raise; a lucky argument "
                 "must never clear a conflict")
        except journal.JournalError as exc:
            if exc.code != "journal.conflict":
                fail("passing the on-disk fingerprint against a "
                     "conflicted object raised the wrong code: %r"
                     % exc.code)

        affected = journal.detect_external_edits(d)
        if affected != [object_id]:
            fail("detect_external_edits did not return exactly the "
                 "conflicted object id: %r" % affected)
        external_entries = [e for e in journal.entries(d)
                             if e["object_id"] == object_id
                             and e["operation"] == "external_edit"]
        if len(external_entries) != 1:
            fail("detect_external_edits did not append exactly one "
                 "external_edit record: %d" % len(external_entries))
        if external_entries[0]["before_fingerprint"] != rec1["fingerprint"]:
            fail("the external_edit record's before_fingerprint was not "
                 "the last accepted fingerprint: %r" % external_entries[0])
        if external_entries[0]["after_fingerprint"] != on_disk_fp:
            fail("the external_edit record's after_fingerprint was not "
                 "the observed on-disk fingerprint: %r" % external_entries[0])

        second_call = journal.detect_external_edits(d)
        if second_call != []:
            fail("a second immediate detect_external_edits call was not "
                 "idempotent: %r" % second_call)
        if len([e for e in journal.entries(d)
                if e["object_id"] == object_id
                and e["operation"] == "external_edit"]) != 1:
            fail("a second detect_external_edits call appended a "
                 "duplicate external_edit record")

        try:
            journal.reconcile(
                d, object_id, "sha256:not-a-real-fingerprint", "human",
                "weibao", "wrong fingerprint on purpose")
            fail("reconcile with a fingerprint matching neither side did "
                 "not raise")
        except journal.JournalError as exc:
            if exc.code != "journal.stale_preflight":
                fail("a bogus chosen_fingerprint raised the wrong code: "
                     "%r" % exc.code)
        if len([e for e in journal.entries(d)
                if e["object_id"] == object_id
                and e["operation"] == "reconcile"]) != 0:
            fail("a refused reconcile call appended a reconciliation "
                 "record")

        journal.reconcile(
            d, object_id, on_disk_fp, "human", "weibao",
            "accepting the out-of-band edit as the new truth")
        if journal.object_state(d, object_id) != "clean":
            fail("object_state did not return clean after reconcile")

        resumed = journal.commit_operation(
            d, object_id, "course", "conflicted.md", "edit_in_place",
            b"# Course\n\nfollow-up edit after reconciling\n",
            expected_fingerprint=on_disk_fp, actor_kind="human",
            actor_name="weibao")
        if resumed["object_id"] != object_id:
            fail("commit_operation after reconcile did not succeed")

        _check_merge_free_scenarios()
        print("OK check_external_edits")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _has_merge_named_function():
    for name in dir(journal):
        if "merge" in name.lower():
            return name
    return None


def _check_merge_free_scenarios():
    bad_name = _has_merge_named_function()
    if bad_name is not None:
        fail("journal.py defines a function whose name contains 'merge': "
             "%r" % bad_name)

    # Scenario: move-then-edit.
    d = _mkbase()
    try:
        object_id = identity.new_object_id()
        rec = journal.commit_operation(
            d, object_id, "lesson", "scenario/before.md", "mint",
            b"# Scenario\n\nmove then edit\n", expected_fingerprint=None,
            actor_kind="human", actor_name="weibao", create_if_missing=True)
        moved = journal.op_move(d, object_id, "scenario/after.md",
                                 rec["fingerprint"], "human", "weibao")
        edited = journal.op_edit_in_place(
            d, object_id, "lesson", "scenario/after.md",
            b"# Scenario\n\nmove then edit, then edited\n",
            moved["fingerprint"], "human", "weibao")
        row = journal.read_registry(d)[object_id]
        if row["path"] != "scenario/after.md" or row["revision"] != 3:
            fail("move-then-edit scenario did not end at the moved path, "
                 "revision 3: %r" % row)
        if journal.object_state(d, object_id) != "clean":
            fail("move-then-edit scenario did not end clean: %r"
                 % journal.object_state(d, object_id))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # Scenario: edit-both-copies.
    d = _mkbase()
    try:
        object_id = identity.new_object_id()
        rec = journal.commit_operation(
            d, object_id, "bank", "shared.md", "mint",
            b"# Shared\n\noriginal\n", expected_fingerprint=None,
            actor_kind="human", actor_name="weibao", create_if_missing=True,
            rights={"read": "granted", "quote": "granted",
                    "transform": "granted", "remote_process": "unknown",
                    "package": "unknown", "export": "unknown",
                    "share": "unknown"})
        copy_rec = journal.op_copy(
            d, object_id, "bank", "shared_copy.md", b"# Shared\n\noriginal\n",
            "human", "weibao")
        journal.op_edit_in_place(
            d, object_id, "bank", "shared.md", b"# Shared\n\nedited A\n",
            rec["fingerprint"], "human", "weibao")
        journal.op_edit_in_place(
            d, copy_rec["object_id"], "bank", "shared_copy.md",
            b"# Shared\n\nedited B\n", copy_rec["fingerprint"], "human",
            "weibao")
        with open(os.path.join(d, "shared.md"), "rb") as fh:
            content_a = fh.read()
        with open(os.path.join(d, "shared_copy.md"), "rb") as fh:
            content_b = fh.read()
        if content_a == content_b:
            fail("edit-both-copies scenario collapsed two copies into "
                 "identical bytes")
        registry = journal.read_registry(d)
        if object_id not in registry or copy_rec["object_id"] not in \
                registry:
            fail("edit-both-copies scenario lost an id")
        if content_a != b"# Shared\n\nedited A\n" or \
                content_b != b"# Shared\n\nedited B\n":
            fail("edit-both-copies scenario did not keep each copy's own "
                 "edit")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # Scenario: import-then-source-change.
    d = _mkbase()
    try:
        source_id = identity.new_object_id()
        source_rec = journal.commit_operation(
            d, source_id, "source", "import_source.md", "mint",
            b"# Source\n\nbefore import\n", expected_fingerprint=None,
            actor_kind="human", actor_name="weibao", create_if_missing=True,
            rights={"read": "granted", "quote": "granted",
                    "transform": "granted", "remote_process": "unknown",
                    "package": "unknown", "export": "unknown",
                    "share": "unknown"})
        imported = journal.op_import(
            d, source_id, "bank", "imported_from_source.md",
            b"# Imported\n\nbefore import\n", "human", "weibao")
        journal.op_edit_in_place(
            d, source_id, "source", "import_source.md",
            b"# Source\n\nchanged after import\n", source_rec["fingerprint"],
            "human", "weibao")
        registry = journal.read_registry(d)
        if registry[imported["object_id"]]["fingerprint"] != \
                imported["fingerprint"]:
            fail("import-then-source-change scenario mutated the "
                 "already-imported artifact when the source changed")
        with open(os.path.join(d, "imported_from_source.md"), "rb") as fh:
            if fh.read() != b"# Imported\n\nbefore import\n":
                fail("import-then-source-change scenario changed the "
                     "imported artifact's bytes")

        # Every entry still parses, and rebuild_registry reproduces the
        # log's projection byte-identically, for this scenario's base.
        entries_ok = list(journal.entries(d))
        if not entries_ok:
            fail("journal.entries did not parse any entry from the final "
                 "scenario base")
        registry_path = journal.registry_path(d)
        with open(registry_path, "rb") as fh:
            before_rebuild = fh.read()
        os.remove(registry_path)
        journal.rebuild_registry(d)
        with open(registry_path, "rb") as fh:
            after_rebuild = fh.read()
        if before_rebuild != after_rebuild:
            fail("rebuild_registry after the scenario set did not "
                 "reproduce a byte-identical projection")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# Task 3: the per-operation rights gate


def check_rights():
    if identity.RIGHTS_STATES != ("granted", "denied", "unknown"):
        fail("identity.RIGHTS_STATES did not equal the three-state tuple: "
             "%r" % (identity.RIGHTS_STATES,))
    if identity.rights_state(None, "transform") != "unknown":
        fail("rights_state(None, 'transform') was not 'unknown'")
    if identity.rights_state({}, "transform") != "unknown":
        fail("rights_state({}, 'transform') was not 'unknown'")
    if identity.rights_state({"transform": "GRANTED"}, "transform") != \
            "unknown":
        fail("rights_state with an upper-cased value was not 'unknown'; "
             "the comparison must be exact lowercase ASCII")
    if identity.rights_state({"transform": "granted"}, "Transform") != \
            "unknown":
        fail("rights_state with an unrecognized operation name was not "
             "'unknown'")
    if identity.rights_granted({"transform": "granted"}, "transform") is \
            not True:
        fail("rights_granted did not return True for the exact string "
             "'granted'")
    if identity.rights_granted({"transform": "denied"}, "transform") is \
            not False:
        fail("rights_granted returned True for 'denied'")

    d = _mkbase()
    try:
        unknown_source = journal.commit_operation(
            d, identity.new_object_id(), "source", "unknown_rights.md",
            "mint", b"# Source\n\nunknown rights\n",
            expected_fingerprint=None, actor_kind="human",
            actor_name="weibao", create_if_missing=True)
        if unknown_source["rights"] != identity.rights_default():
            fail("a source minted with no rights argument did not carry "
                 "identity.rights_default(): %r" % unknown_source["rights"])

        denied_source = journal.commit_operation(
            d, identity.new_object_id(), "source", "denied_rights.md",
            "mint", b"# Source\n\ndenied rights\n",
            expected_fingerprint=None, actor_kind="human",
            actor_name="weibao", create_if_missing=True,
            rights={"read": "granted", "quote": "denied",
                    "transform": "denied", "remote_process": "denied",
                    "package": "denied", "export": "denied",
                    "share": "denied"})

        granted_source = journal.commit_operation(
            d, identity.new_object_id(), "source", "granted_rights.md",
            "mint", b"# Source\n\ngranted rights\n",
            expected_fingerprint=None, actor_kind="human",
            actor_name="weibao", create_if_missing=True,
            rights={"read": "granted", "quote": "granted",
                    "transform": "granted", "remote_process": "unknown",
                    "package": "unknown", "export": "unknown",
                    "share": "unknown"})

        for label, source_rec in (("unknown", unknown_source),
                                   ("denied", denied_source)):
            for op_name, handler in (("import", journal.op_import),
                                      ("copy", journal.op_copy)):
                try:
                    handler(
                        d, source_rec["object_id"], "bank",
                        "%s_%s_target.md" % (label, op_name),
                        b"# pulled bytes\n", "human", "weibao")
                    fail("%s from a %s-rights source did not raise"
                         % (op_name, label))
                except journal.JournalError as exc:
                    if exc.code != "journal.rights_unknown":
                        fail("%s from a %s-rights source raised the wrong "
                             "code: %r" % (op_name, label, exc.code))
                    if "Next safe action: record a rights grant" not in \
                            exc.message:
                        fail("the rights refusal message did not contain "
                             "the exact next-safe-action sentence: %r"
                             % exc.message)
                target = os.path.join(
                    d, "%s_%s_target.md" % (label, op_name))
                if os.path.exists(target):
                    fail("a rights-refused %s wrote a file at %s"
                         % (op_name, target))

        imported = journal.op_import(
            d, granted_source["object_id"], "bank", "granted_import.md",
            b"# pulled from a granted source\n", "human", "weibao")
        if imported["object_id"] == granted_source["object_id"]:
            fail("op_import from a granted source did not mint a new id")
        copied = journal.op_copy(
            d, granted_source["object_id"], "bank", "granted_copy.md",
            b"# pulled from a granted source\n", "human", "weibao")
        if copied["object_id"] in (granted_source["object_id"],
                                    imported["object_id"]):
            fail("op_copy from a granted source did not mint a new id")

        no_rights_object = identity.new_object_id()
        rec = journal.commit_operation(
            d, no_rights_object, "lesson", "unowned_lesson.md", "mint",
            b"# Lesson\n\nowned by the course\n", expected_fingerprint=None,
            actor_kind="human", actor_name="weibao", create_if_missing=True)
        linked = journal.op_link(d, "source", "denied_rights.md", "human",
                                  "weibao")
        moved = journal.op_move(
            d, no_rights_object, "moved_unowned_lesson.md",
            rec["fingerprint"], "human", "weibao")
        edited = journal.op_edit_in_place(
            d, no_rights_object, "lesson", "moved_unowned_lesson.md",
            b"# Lesson\n\nedited\n", moved["fingerprint"], "human", "weibao")
        other_object = identity.new_object_id()
        other_rec = journal.commit_operation(
            d, other_object, "lesson", "other_lesson.md", "mint",
            b"# Lesson\n\nanother one\n", expected_fingerprint=None,
            actor_kind="human", actor_name="weibao", create_if_missing=True)
        superseded = journal.op_supersede(
            d, other_object, no_rights_object, other_rec["fingerprint"],
            "human", "weibao")
        for rec_ in (linked, edited, superseded):
            if rec_ is None:
                fail("an ownership operation against an unknown-rights "
                     "source unexpectedly failed")

        print("OK check_rights")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    check_operations()
    check_external_edits()
    check_rights()
    print("OK operations_roundtrip")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        mode = sys.argv[2]
        base = sys.argv[3]
        if mode == "concurrent_holder":
            _child_concurrent_holder(base)
        elif mode == "concurrent_waiter":
            _child_concurrent_waiter(base)
        else:
            sys.exit("unknown --child mode %r" % mode)
    else:
        sys.exit(main())
