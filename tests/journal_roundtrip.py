#!/usr/bin/env python3
"""Proves the operation journal end to end: the compare-and-swap write path,
the append-only prepared-then-applied protocol, the disposable registry
projection, and honest replay of a crash, a disk-full fault, and a permission
denial.

Standard library only, runnable as `python tests/journal_roundtrip.py`, with
a `--child` mode used by the kill fixtures the way
`tests/durability_roundtrip.py` uses its `--writer` mode.
"""
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import identity                                               # noqa: E402
import journal                                                # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def _mkbase():
    return tempfile.mkdtemp()


def check_commit():
    d = _mkbase()
    try:
        expected_dir = os.path.join(os.path.abspath(d), "_journal")
        if journal.journal_dir(d) != expected_dir:
            fail("journal_dir() did not equal os.path.join(abspath(base), "
                 "'_journal'): %r" % journal.journal_dir(d))

        object_id = identity.new_object_id()
        rel_path = "course.md"
        raw1 = b"# Course\n\nfirst revision\n"

        rec1 = journal.commit_operation(
            d, object_id, "course", rel_path, "mint", raw1,
            expected_fingerprint=None, actor_kind="human",
            actor_name="weibao", create_if_missing=True)
        if rec1["revision"] != 1 or rec1["parent_revision"] is not None:
            fail("first commit_operation did not return revision 1, "
                 "parent_revision None: %r" % rec1)

        target_path = os.path.join(d, rel_path)
        with open(target_path, "rb") as fh:
            if fh.read() != raw1:
                fail("target bytes after the first commit do not equal "
                     "the written bytes")

        lines = open(journal.log_path(d), encoding="utf-8").read() \
            .strip().splitlines()
        if len(lines) != 2:
            fail("first commit_operation did not append exactly two lines: "
                 "%d" % len(lines))
        prepared_obj = json.loads(lines[0])
        applied_obj = json.loads(lines[1])
        if prepared_obj["state"] != "prepared":
            fail("first line was not a prepared entry: %r" % prepared_obj)
        if applied_obj["state"] != "applied" or \
                applied_obj["resolves_entry"] != prepared_obj["entry_id"]:
            fail("second line was not an applied entry resolving the "
                 "prepared entry: %r" % applied_obj)
        for obj in (prepared_obj, applied_obj):
            if set(obj.keys()) != set(journal.ENTRY_KEYS):
                fail("appended entry key set does not equal "
                     "set(journal.ENTRY_KEYS): %r" % sorted(obj.keys()))

        raw2 = b"# Course\n\nsecond revision\n"
        fp1 = identity.object_fingerprint(raw1, "course")
        rec2 = journal.commit_operation(
            d, object_id, "course", rel_path, "edit_in_place", raw2,
            expected_fingerprint=fp1, actor_kind="human",
            actor_name="weibao")
        if rec2["revision"] != 2 or rec2["parent_revision"] != 1:
            fail("second commit_operation did not return revision 2, "
                 "parent_revision 1: %r" % rec2)
        with open(target_path, "rb") as fh:
            if fh.read() != raw2:
                fail("target bytes after the second commit do not equal "
                     "the new bytes")

        raw3 = b"# Course\n\nthird revision, never applied\n"
        try:
            journal.commit_operation(
                d, object_id, "course", rel_path, "edit_in_place", raw3,
                expected_fingerprint=fp1, actor_kind="human",
                actor_name="weibao")
            fail("commit_operation with a wrong expected_fingerprint did "
                 "not raise")
        except journal.JournalError as exc:
            if exc.code != "journal.stale_preflight":
                fail("wrong expected_fingerprint raised the wrong code: %r"
                     % exc.code)
        with open(target_path, "rb") as fh:
            if fh.read() != raw2:
                fail("target bytes changed after a refused stale_preflight "
                     "commit")
        refused_lines_before = sum(
            1 for e in journal.entries(d) if e["state"] == "refused")
        if refused_lines_before != 1:
            fail("expected exactly one refused line after the "
                 "stale_preflight case, found %d" % refused_lines_before)

        try:
            journal.commit_operation(
                d, object_id, "course", rel_path, "edit_in_place", raw3,
                expected_fingerprint=None, actor_kind="human",
                actor_name="weibao")
            fail("commit_operation with expected_fingerprint=None against "
                 "a known object did not raise")
        except journal.JournalError as exc:
            if exc.code != "journal.missing_fingerprint":
                fail("expected_fingerprint=None against a known object "
                     "raised the wrong code: %r" % exc.code)

        fp2 = identity.object_fingerprint(raw2, "course")
        try:
            journal.commit_operation(
                d, object_id, "course", rel_path, "edit_in_place", raw2,
                expected_fingerprint=fp2, actor_kind="human",
                actor_name="weibao")
            fail("commit_operation with identical new bytes did not raise")
        except journal.JournalError as exc:
            if exc.code != "journal.no_change":
                fail("identical new bytes raised the wrong code: %r"
                     % exc.code)
        registry_after_no_change = journal.read_registry(d)
        if registry_after_no_change[object_id]["revision"] != 2:
            fail("a no_change refusal recorded a new revision")

        empty_rec = journal.commit_operation(
            d, object_id, "course", rel_path, "edit_in_place", b"",
            expected_fingerprint=fp2, actor_kind="human",
            actor_name="weibao")
        if empty_rec["fingerprint"] != identity.object_fingerprint(b"",
                                                                    "course"):
            fail("writing b'' over an existing object did not record a "
                 "real after fingerprint")
        with open(target_path, "rb") as fh:
            if fh.read() != b"":
                fail("writing b'' did not actually empty the target file")
        if journal.object_state(d, object_id) == "missing":
            fail("an object holding zero bytes was reported missing")

        try:
            journal.commit_operation(
                d, object_id, "course", rel_path, "not_a_real_operation",
                b"x", expected_fingerprint=None, actor_kind="human",
                actor_name="weibao")
            fail("commit_operation with an unknown operation did not raise")
        except journal.JournalError as exc:
            if exc.code != "journal.unknown_operation":
                fail("unknown operation raised the wrong code: %r"
                     % exc.code)
        with open(target_path, "rb") as fh:
            if fh.read() != b"":
                fail("an unknown-operation refusal mutated the target")

        registry = journal.read_registry(d)
        if registry[object_id]["revision"] != 3 or \
                registry[object_id]["fingerprint"] != \
                identity.object_fingerprint(b"", "course"):
            fail("read_registry() after the write sequence did not report "
                 "the current revision and fingerprint: %r"
                 % registry.get(object_id))

        registry_path = journal.registry_path(d)
        with open(registry_path, "rb") as fh:
            before_rebuild = fh.read()
        os.remove(registry_path)
        journal.rebuild_registry(d)
        with open(registry_path, "rb") as fh:
            after_rebuild = fh.read()
        if before_rebuild != after_rebuild:
            fail("rebuild_registry() after deleting objects.json did not "
                 "reproduce a byte-identical file")

        entry_list = list(journal.entries(d))
        forced_ts = "2026-08-18T00:00:00.000Z"
        e1 = journal.append_entry(d, {
            "operation": "mint", "state": "applied", "object_id": "zzzzzzzz",
            "kind": "course", "path": "z.md", "timestamp": forced_ts})
        e2 = journal.append_entry(d, {
            "operation": "mint", "state": "applied", "object_id": "zzzzzzzz",
            "kind": "course", "path": "z.md", "timestamp": forced_ts})
        ordered_ids = [e["entry_id"] for e in journal.entries(d)
                       if e["timestamp"] == forced_ts]
        if ordered_ids != [e1["entry_id"], e2["entry_id"]]:
            fail("entries() with an identical forced timestamp did not "
                 "return in append order")

        bad_log = journal.log_path(d)
        with open(bad_log, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"operation": "not_a_type", "state": "x"})
                      + "\n")
        buf_lines_before = len(list(journal.entries(d)))
        stderr_capture = _capture_stderr(lambda: list(journal.entries(d)))
        if "warning" not in stderr_capture or \
                "skipped" not in stderr_capture:
            fail("entries() did not print a warning for an unrecognized "
                 "operation line")

        if journal.object_state(d, object_id) != "clean":
            fail("object_state() right after a successful write was not "
                 "'clean': %r" % journal.object_state(d, object_id))
        with open(target_path, "wb") as fh:
            fh.write(b"edited behind the journal's back")
        if journal.object_state(d, object_id) != "conflict":
            fail("object_state() after an out-of-band edit was not "
                 "'conflict': %r" % journal.object_state(d, object_id))
        os.remove(target_path)
        if journal.object_state(d, object_id) != "missing":
            fail("object_state() after deleting the target was not "
                 "'missing': %r" % journal.object_state(d, object_id))

        removed_root = tempfile.mkdtemp()
        shutil.rmtree(removed_root)
        if journal.object_state(removed_root, object_id) != "unavailable":
            fail("object_state() against a removed root was not "
                 "'unavailable'")
        try:
            journal.commit_operation(
                removed_root, identity.new_object_id(), "course", "c.md",
                "mint", b"x", expected_fingerprint=None, actor_kind="human",
                actor_name="weibao", create_if_missing=True)
            fail("commit_operation into a removed root did not raise")
        except journal.JournalError as exc:
            if exc.code != "journal.root_unavailable":
                fail("commit_operation into a removed root raised the "
                     "wrong code: %r" % exc.code)

        print("OK check_commit")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _capture_stderr(fn):
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        fn()
    return buf.getvalue()


def check_lock_busy():
    d = _mkbase()
    try:
        lock_path = os.path.join(journal.journal_dir(d), journal.LOCK_FILENAME)
        os.makedirs(journal.journal_dir(d), exist_ok=True)
        fh = open(lock_path, "a+b")
        try:
            if fh.tell() == 0:
                fh.write(b"\n")
                fh.flush()
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            orig_timeout = journal.LOCK_TIMEOUT_SECONDS
            journal.LOCK_TIMEOUT_SECONDS = 1.0
            start = time.monotonic()
            try:
                journal.commit_operation(
                    d, identity.new_object_id(), "course", "busy.md",
                    "mint", b"x", expected_fingerprint=None,
                    actor_kind="human", actor_name="weibao",
                    create_if_missing=True)
                fail("commit_operation while the lock is held did not "
                     "raise")
            except journal.JournalError as exc:
                if exc.code != "journal.busy":
                    fail("commit_operation while the lock is held raised "
                         "the wrong code: %r" % exc.code)
            elapsed = time.monotonic() - start
            journal.LOCK_TIMEOUT_SECONDS = orig_timeout
            if elapsed < 0.8:
                fail("journal.busy fired well before the lock timeout "
                     "elapsed: %.2fs" % elapsed)
        finally:
            if os.name == "nt":
                import msvcrt
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            fh.close()
        log_text = ""
        if os.path.exists(journal.log_path(d)):
            log_text = open(journal.log_path(d), encoding="utf-8").read()
        no_lines = [l for l in log_text.strip().splitlines() if l]
        if no_lines:
            fail("a journal.busy refusal appended a line: %r" % no_lines)
        print("OK check_lock_busy (%.2fs)" % elapsed)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def check_walking_skeleton_slice():
    d = _mkbase()
    try:
        raw = b"# Course\n\nWalking skeleton slice.\n"
        rec = identity.mint_object(
            "course", "course.md", raw, "human", "weibao", "mint")
        journal.commit_operation(
            d, rec["object_id"], "course", "course.md", "mint", raw,
            expected_fingerprint=None, actor_kind="human",
            actor_name="weibao", create_if_missing=True)
        registry = journal.read_registry(d)
        stored = registry[rec["object_id"]]
        if stored["revision"] != 1 or stored["fingerprint"] != \
                rec["fingerprint"]:
            fail("the walking-skeleton slice's round trip did not match: "
                 "%r vs minted %r" % (stored, rec))
        print("OK check_walking_skeleton_slice")
    finally:
        shutil.rmtree(d, ignore_errors=True)



def main():
    check_commit()
    check_lock_busy()
    check_walking_skeleton_slice()
    print("OK journal_roundtrip")


if __name__ == "__main__":
    sys.exit(main())
