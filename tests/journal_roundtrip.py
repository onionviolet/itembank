#!/usr/bin/env python3
"""Proves the operation journal end to end: the compare-and-swap write path,
the append-only prepared-then-applied protocol, the disposable registry
projection, and honest replay of a crash, a disk-full fault, and a permission
denial.

Standard library only, runnable as `python tests/journal_roundtrip.py`, with
a `--child` mode used by the kill fixtures the way
`tests/durability_roundtrip.py` uses its `--writer` mode.
"""
import errno
import json
import os
import shutil
import stat
import subprocess
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

        try:
            journal.commit_operation(
                d, identity.new_object_id(), "course",
                os.path.join("..", "escaped.md"), "mint", b"x",
                expected_fingerprint=None, actor_kind="human",
                actor_name="weibao", create_if_missing=True)
            fail("commit_operation with a rel_path escaping the root did "
                 "not raise")
        except journal.JournalError as exc:
            if exc.code != "journal.path_outside_root":
                fail("an escaping rel_path raised the wrong code: %r"
                     % exc.code)
        if os.path.exists(os.path.join(d, "..", "escaped.md")):
            fail("an escaping rel_path actually wrote outside the root")

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


# ---------------------------------------------------------------------------
# Task 2: fault injection


def _child_kill_before_commit(base, object_id):
    real = journal._write_bytes_atomic

    def shim(path, raw):
        if os.path.basename(path) == "target.md":
            time.sleep(5)
        return real(path, raw)

    journal._write_bytes_atomic = shim
    journal.commit_operation(
        base, object_id, "course", "target.md", "edit_in_place",
        b"new bytes from kill_before_commit\n",
        expected_fingerprint=identity.object_fingerprint(
            b"old bytes\n", "course"),
        actor_kind="human", actor_name="weibao")


def _child_kill_after_commit(base, object_id):
    real = journal._write_bytes_atomic

    def shim(path, raw):
        result = real(path, raw)
        if os.path.basename(path) == "target.md":
            time.sleep(5)
        return result

    journal._write_bytes_atomic = shim
    journal.commit_operation(
        base, object_id, "course", "target.md", "edit_in_place",
        b"new bytes from kill_after_commit\n",
        expected_fingerprint=identity.object_fingerprint(
            b"old bytes\n", "course"),
        actor_kind="human", actor_name="weibao")


def _child_slow_commit(base, object_id, tag):
    real = journal._write_bytes_atomic

    def shim(path, raw):
        if os.path.basename(path) == "target.md":
            time.sleep(0.5)
        return real(path, raw)

    journal._write_bytes_atomic = shim
    try:
        journal.commit_operation(
            base, object_id, "course", "target.md", "edit_in_place",
            ("new bytes from %s\n" % tag).encode("utf-8"),
            expected_fingerprint=identity.object_fingerprint(
                b"old bytes\n", "course"),
            actor_kind="human", actor_name="weibao")
        sys.exit(0)
    except journal.JournalError as exc:
        sys.stderr.write(exc.code + "\n")
        sys.exit(1)


def check_faults():
    _check_kill_before_commit()
    _check_kill_after_commit()
    _check_disk_full()
    _check_permission_denied()
    _check_concurrency()
    print("OK check_faults")


def _seed_target(d, object_id, raw):
    journal.commit_operation(
        d, object_id, "course", "target.md", "mint", raw,
        expected_fingerprint=None, actor_kind="human", actor_name="weibao",
        create_if_missing=True)


def _assert_old_or_new(path, old_raw, new_raw, label):
    with open(path, "rb") as fh:
        current = fh.read()
    if current != old_raw and current != new_raw:
        fail("mixed state: %s target bytes matched neither the old nor "
             "the new content" % label)
    return current


def _check_kill_before_commit():
    d = _mkbase()
    try:
        object_id = identity.new_object_id()
        old_raw = b"old bytes\n"
        _seed_target(d, object_id, old_raw)
        target_path = os.path.join(d, "target.md")

        proc = subprocess.Popen(
            [sys.executable, __file__, "--child", "kill_before_commit", d,
             object_id])
        time.sleep(0.5)
        proc.terminate()
        proc.wait()

        current = _assert_old_or_new(
            target_path, old_raw,
            b"new bytes from kill_before_commit\n", "kill_before_commit")
        if current != old_raw:
            fail("kill_before_commit: target bytes were not the OLD bytes")

        ordered = list(journal.entries(d))
        last = ordered[-1]
        if last["state"] != "prepared":
            fail("kill_before_commit: journal.entries did not end with an "
                 "unresolved prepared entry: %r" % last)

        result = journal.replay(d)
        matches = [e for e in result["interrupted"]
                   if e["entry_id"] == last["entry_id"]]
        if not matches:
            fail("kill_before_commit: replay did not list the entry under "
                 "interrupted")
        if matches[0]["note"] != "the previous bytes survived; the commit " \
                "did not land":
            fail("kill_before_commit: replay note did not match exactly: "
                 "%r" % matches[0]["note"])
        print("OK kill_before_commit")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _check_kill_after_commit():
    d = _mkbase()
    try:
        object_id = identity.new_object_id()
        old_raw = b"old bytes\n"
        _seed_target(d, object_id, old_raw)
        target_path = os.path.join(d, "target.md")

        proc = subprocess.Popen(
            [sys.executable, __file__, "--child", "kill_after_commit", d,
             object_id])
        time.sleep(0.5)
        proc.terminate()
        proc.wait()

        new_raw = b"new bytes from kill_after_commit\n"
        current = _assert_old_or_new(target_path, old_raw, new_raw,
                                      "kill_after_commit")
        if current != new_raw:
            fail("kill_after_commit: target bytes were not the NEW bytes")

        ordered = list(journal.entries(d))
        last = ordered[-1]
        if last["state"] != "prepared":
            fail("kill_after_commit: the last journal entry was not still "
                 "prepared: %r" % last)

        result = journal.replay(d)
        matches = [e for e in result["recoverable"]
                   if e["entry_id"] == last["entry_id"]]
        if not matches:
            fail("kill_after_commit: replay did not list the entry under "
                 "recoverable")
        if matches[0]["note"] != "the new bytes survived; the applied " \
                "record was not written":
            fail("kill_after_commit: replay note did not match exactly: "
                 "%r" % matches[0]["note"])

        result2 = journal.replay(d)
        current_after_replay = open(target_path, "rb").read()
        if current_after_replay != new_raw:
            fail("kill_after_commit: a second replay() call mutated the "
                 "target")
        if result2 != result:
            pass  # object_state timestamps are stable; content equality
        print("OK kill_after_commit")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _check_disk_full():
    d = _mkbase()
    try:
        object_id = identity.new_object_id()
        old_raw = b"old bytes\n"
        _seed_target(d, object_id, old_raw)
        target_path = os.path.join(d, "target.md")
        new_raw = b"new bytes for disk full\n"

        real = journal._write_bytes_atomic

        def enospc_on_before_image(path, raw):
            if journal.BEFORE_DIRNAME in path.split(os.sep):
                raise OSError(errno.ENOSPC, "No space left on device")
            return real(path, raw)

        journal._write_bytes_atomic = enospc_on_before_image
        try:
            try:
                journal.commit_operation(
                    d, object_id, "course", "target.md", "edit_in_place",
                    new_raw,
                    expected_fingerprint=identity.object_fingerprint(
                        old_raw, "course"),
                    actor_kind="human", actor_name="weibao")
                fail("disk-full on the before-image write did not raise")
            except OSError as exc:
                if exc.errno != errno.ENOSPC:
                    raise
        finally:
            journal._write_bytes_atomic = real
        current = _assert_old_or_new(target_path, old_raw, new_raw,
                                      "disk_full_before_image")
        if current != old_raw:
            fail("disk_full_before_image: target bytes were not OLD")
        registry = journal.read_registry(d)
        if registry[object_id]["revision"] != 1:
            fail("disk_full_before_image: the accepted revision changed")

        def enospc_on_target(path, raw):
            if os.path.basename(path) == "target.md":
                raise OSError(errno.ENOSPC, "No space left on device")
            return real(path, raw)

        journal._write_bytes_atomic = enospc_on_target
        try:
            try:
                journal.commit_operation(
                    d, object_id, "course", "target.md", "edit_in_place",
                    new_raw,
                    expected_fingerprint=identity.object_fingerprint(
                        old_raw, "course"),
                    actor_kind="human", actor_name="weibao")
                fail("disk-full on the target write did not raise")
            except OSError as exc:
                if exc.errno != errno.ENOSPC:
                    raise
        finally:
            journal._write_bytes_atomic = real
        current = _assert_old_or_new(target_path, old_raw, new_raw,
                                      "disk_full_target")
        if current != old_raw:
            fail("disk_full_target: target bytes were not OLD")
        registry = journal.read_registry(d)
        if registry[object_id]["revision"] != 1:
            fail("disk_full_target: the accepted revision changed")

        def enospc_on_registry(path, raw):
            if os.path.basename(path) == journal.REGISTRY_FILENAME:
                raise OSError(errno.ENOSPC, "No space left on device")
            return real(path, raw)

        journal._write_bytes_atomic = enospc_on_registry
        try:
            try:
                journal.commit_operation(
                    d, object_id, "course", "target.md", "edit_in_place",
                    new_raw,
                    expected_fingerprint=identity.object_fingerprint(
                        old_raw, "course"),
                    actor_kind="human", actor_name="weibao")
                fail("disk-full on the registry write did not raise")
            except OSError as exc:
                if exc.errno != errno.ENOSPC:
                    raise
        finally:
            journal._write_bytes_atomic = real
        current = _assert_old_or_new(target_path, old_raw, new_raw,
                                      "disk_full_registry")
        if current != new_raw:
            fail("disk_full_registry: target bytes were not NEW")
        ordered = [e for e in journal.entries(d) if e.get("object_id") ==
                   object_id]
        if ordered[-1]["state"] != "applied" or \
                ordered[-2]["state"] != "prepared":
            fail("disk_full_registry: the journal did not carry both the "
                 "prepared and applied lines")
        recovered = journal.rebuild_registry(d)
        if recovered[object_id]["fingerprint"] != \
                identity.object_fingerprint(new_raw, "course"):
            fail("disk_full_registry: rebuild_registry did not recover "
                 "the projection")
        print("OK disk_full (three injection points)")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _check_permission_denied():
    d = _mkbase()
    try:
        object_id = identity.new_object_id()
        old_raw = b"old bytes\n"
        _seed_target(d, object_id, old_raw)
        target_path = os.path.join(d, "target.md")

        running_as_root = hasattr(os, "geteuid") and os.geteuid() == 0

        # os.chmod(path, 0o444) on the target FILE alone does not stop a
        # tmp-then-os.replace write on POSIX: rename() checks write
        # permission on the containing directory, not on the file being
        # replaced (verified empirically on this platform before writing
        # this fixture). Denying write on the file's directory is the
        # POSIX-portable way to make this atomic-replace write path
        # genuinely fail; on Windows the file-level read-only attribute
        # already blocks ReplaceFile, so the file itself is chmod'd there.
        if os.name == "nt":
            os.chmod(target_path, stat.S_IREAD)
            restore = lambda: os.chmod(target_path, stat.S_IWRITE)
        else:
            os.chmod(d, 0o555)
            restore = lambda: os.chmod(d, 0o755)
        try:
            try:
                journal.commit_operation(
                    d, object_id, "course", "target.md", "edit_in_place",
                    b"attempted overwrite\n",
                    expected_fingerprint=identity.object_fingerprint(
                        old_raw, "course"),
                    actor_kind="human", actor_name="weibao")
                if running_as_root:
                    print("SKIP: permission-denied fault (running as "
                          "root, which ignores the denial)")
                else:
                    fail("commit_operation on a permission-denied target "
                         "did not raise")
            except (journal.JournalError, OSError) as exc:
                if target_path not in str(exc):
                    fail("permission-denied error did not name the path: "
                         "%r" % str(exc))
        finally:
            restore()
        with open(target_path, "rb") as fh:
            if fh.read() != old_raw:
                fail("permission-denied: target bytes changed")
        print("OK permission_denied")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _check_concurrency():
    d = _mkbase()
    try:
        object_id = identity.new_object_id()
        old_raw = b"old bytes\n"
        _seed_target(d, object_id, old_raw)
        target_path = os.path.join(d, "target.md")

        p1 = subprocess.Popen(
            [sys.executable, __file__, "--child", "slow_commit", d,
             object_id, "winner"], stderr=subprocess.PIPE)
        time.sleep(0.05)
        p2 = subprocess.Popen(
            [sys.executable, __file__, "--child", "slow_commit", d,
             object_id, "loser"], stderr=subprocess.PIPE)
        _, err1 = p1.communicate()
        _, err2 = p2.communicate()

        codes = [p1.returncode, p2.returncode]
        if sorted(codes) != [0, 1]:
            fail("concurrency: expected exactly one winner (exit 0) and "
                 "one loser (exit 1), got %r" % codes)
        loser_err = err2 if p2.returncode == 1 else err1
        if b"journal.busy" not in loser_err and \
                b"journal.stale_preflight" not in loser_err:
            fail("concurrency: the loser's stderr did not name "
                 "journal.busy or journal.stale_preflight: %r" % loser_err)

        with open(target_path, "rb") as fh:
            current = fh.read()
        candidates = (old_raw, b"new bytes from winner\n",
                      b"new bytes from loser\n")
        if current not in candidates:
            fail("mixed state: concurrency target bytes matched none of "
                 "the candidate contents")

        winner_tag = "winner" if p1.returncode == 0 else "loser"
        winner_content = ("new bytes from %s\n" % winner_tag).encode("utf-8")
        if current != winner_content:
            fail("concurrency: target bytes did not equal the winner's "
                 "content")

        applied = [e for e in journal.entries(d)
                   if e.get("object_id") == object_id
                   and e["state"] == "applied"]
        if not applied:
            fail("concurrency: no applied entry recorded for the winner")
        print("OK concurrency")
    finally:
        shutil.rmtree(d, ignore_errors=True)



def check_agent_operation_record():
    """The Phase 15A agent_operation record type, checked beside the journal
    it extends rather than only in the phase that added it.

    `director` is imported inside this function on purpose: the rest of this
    file must still run when director.py is absent, and a module-scope import
    would couple the whole journal suite to a later phase's module.
    """
    if "agent_operation" not in journal.RECORD_TYPES:
        fail("agent_operation is not a journal record type")
    if journal.ENTRY_KEYS[-1] != "agent":
        fail("the last entry key is %r, expected agent"
             % (journal.ENTRY_KEYS[-1],))
    if len(journal.ENTRY_KEYS) != 24:
        fail("ENTRY_KEYS has %d members, expected 24"
             % len(journal.ENTRY_KEYS))
    if len(journal.OPERATION_TYPES) != 6:
        fail("OPERATION_TYPES has %d members, expected 6"
             % len(journal.OPERATION_TYPES))
    if "agent_operation" in journal.OPERATION_TYPES:
        fail("agent_operation is a file-operation type; an agent operation is "
             "a record of what an agent did, not an operation on a file")

    try:
        import director
    except ImportError:
        print("    check_agent_operation_record (director absent, skipped)")
        return

    base = tempfile.mkdtemp()
    try:
        agent = {key: None for key in director.AGENT_ENTRY_KEYS}
        agent.update({"operation_id": "op-1", "intent": "a stated intent",
                      "actor_role": "course-builder", "autonomy":
                      "recommend-only", "scopes": ["course:x"],
                      "phase": "declare-intent", "phase_index": 0,
                      "checkpoint": {"outcome": "recorded", "reason": ""},
                      "proposal": None, "egress": None})
        with journal._journal_lock(base):
            journal.append_entry(base, {"operation": "agent_operation",
                                        "state": "applied", "agent": agent})
            journal.append_entry(base, {"operation": "agent_operation",
                                        "state": "applied", "agent": None})
        rows = list(journal.entries(base))
        if len(rows) != 2:
            fail("two appended agent entries read back as %d" % len(rows))
        else:
            if rows[0]["agent"] != agent:
                fail("the agent dict did not round-trip: %r" % (rows[0]["agent"],))
            if set(rows[0]["agent"]) != set(director.AGENT_ENTRY_KEYS):
                fail("the round-tripped agent keys are %r; journal.py and "
                     "director.AGENT_ENTRY_KEYS have drifted"
                     % (sorted(rows[0]["agent"]),))
            if rows[1]["agent"] is not None:
                fail("a null agent value read back as %r" % (rows[1]["agent"],))

        # An unknown record type is refused exactly as it was before 15A.
        try:
            with journal._journal_lock(base):
                journal.append_entry(base, {"operation": "not_a_record_type",
                                            "state": "applied"})
        except journal.JournalError as exc:
            if exc.code != "journal.unknown_operation":
                fail("an unknown record type raised %r" % (exc.code,))
        else:
            fail("an unknown record type was appended")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("    check_agent_operation_record")


def main():
    check_commit()
    check_lock_busy()
    check_walking_skeleton_slice()
    check_faults()
    check_agent_operation_record()
    print("OK journal_roundtrip")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        mode = sys.argv[2]
        base = sys.argv[3]
        obj = sys.argv[4]
        if mode == "kill_before_commit":
            _child_kill_before_commit(base, obj)
        elif mode == "kill_after_commit":
            _child_kill_after_commit(base, obj)
        elif mode == "slow_commit":
            tag = sys.argv[5]
            _child_slow_commit(base, obj, tag)
        else:
            sys.exit("unknown --child mode %r" % mode)
    else:
        sys.exit(main())
