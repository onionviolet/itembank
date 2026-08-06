"""The evidence log: the one append-only store every later plan writes into and reads from.

`evidence.py` is to the evidence store what `runtime.score_response` is to scoring: the
single primitive every surface calls, so no surface reimplements its own append or its
own read. The log is the only authority (D-08) — a derived index is a disposable
materialized view over it, never a second source of truth. The reader treats every line
as untrusted input: a malformed line is skipped and reported, never fatal (D-09), because
a torn line at the tail of a growing log is an expected failure mode, not a corruption
event that should take the rest of the log down with it.

This module is a peer of `runtime.py`, not an extension of it, and it is never imported
by `model.py` — the same layer split `runtime.py`'s own docstring describes holds here:
identity lives in the model tier, scoring and sessions live in the runtime tier, and the
evidence log is a new runtime-tier primitive beside them.

Integrity note: this module uses `hashlib.sha256` in later plans purely as a
change-detection checksum, never as a security boundary — this project has a single
local user and no attacker in its threat model.
"""
import datetime
import json
import os
import sys
import uuid


EVENT_SCHEMA_VERSION = 1

EVIDENCE_DIRNAME = "_evidence"
LOG_FILENAME = "evidence.jsonl"
INDEX_FILENAME = "evidence_index.sqlite3"


def evidence_dir(base):
    """The `_evidence/` directory beside the bank or plan living in `base`."""
    return os.path.join(os.path.abspath(base), EVIDENCE_DIRNAME)


def log_path(base):
    return os.path.join(evidence_dir(base), LOG_FILENAME)


def index_path(base):
    return os.path.join(evidence_dir(base), INDEX_FILENAME)


def utc_now():
    """ISO-8601 UTC to millisecond precision with a `Z` suffix.

    Matches the timestamp shape already used in `.planning/STATE.md`
    (`2026-08-06T14:49:25.025Z`), so evidence timestamps read the same way every
    other timestamp in this project already does.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (now.microsecond // 1000)


def new_event_id():
    return uuid.uuid4().hex


def append_line(path, line):
    """Append one line to the log, holding a platform advisory lock across exactly
    one write syscall.

    `line` is a `str` with no trailing newline; it is encoded once to UTF-8 with a
    single `b"\\n"` appended, and that whole payload goes out in a single write.
    One syscall is the point: it is what keeps a torn write to at most one line.

    The Microsoft C runtime implements Windows' `O_APPEND` as `lseek(fd, 0,
    SEEK_END)` followed by `write()` — two steps, not one atomic step — so two
    concurrent appenders can interleave or clobber each other's line with no lock
    held. This is a still-open, officially-acknowledged Python bug (bpo-42606).
    The advisory lock below is what serializes concurrent appenders on Windows;
    POSIX's `O_APPEND` is genuinely atomic, so `fcntl.flock` there is defense in
    depth rather than the only thing standing between two writers and a torn line.

    Returns the number of bytes written.
    """
    payload = line.encode("utf-8") + b"\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    win = sys.platform == "win32"
    if win:
        import msvcrt
    else:
        import fcntl
    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        if win:
            # bpo-42606: the CRT's O_APPEND is lseek+write, not one atomic step,
            # so the lock is what serializes concurrent appenders on Windows.
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            os.lseek(fd, 0, os.SEEK_END)
        else:
            fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            n = os.write(fd, payload)
        finally:
            if win:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)
    return n


def iter_raw(path):
    """Yield `(lineno, obj, raw)` for every line in `path` that parses to a dict.

    A missing log is an empty log, never an error — yields nothing rather than
    raising. A line that fails to parse, or that parses to something other than a
    dict, is reported to stdout and skipped rather than raised: D-09 requires the
    reader to survive a torn line, and `runtime.read_session()`'s whole-file
    `sys.exit` posture is the wrong template for one line of a growing log.
    """
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except (ValueError, TypeError):
                print("warn  %s:%d malformed, skipped" % (os.path.basename(path), lineno))
                continue
            if not isinstance(obj, dict):
                print("warn  %s:%d malformed, skipped" % (os.path.basename(path), lineno))
                continue
            yield (lineno, obj, raw)
