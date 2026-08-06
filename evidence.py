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
import hashlib
import json
import os
import sys
import uuid

from runtime import canonical_response


EVENT_SCHEMA_VERSION = 1

EVIDENCE_DIRNAME = "_evidence"
LOG_FILENAME = "evidence.jsonl"
INDEX_FILENAME = "evidence_index.sqlite3"

KNOWN_EVENT_TYPES = ("response",)


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


# ---- response events --------------------------------------------------------
# The tracer: one response, one event, one writer, one reader. Every field
# named in 01-02-PLAN.md's must_haves is present on every event; the two
# EVID-07 fields with no capture point before Phase 6/8 (`error_category`,
# `hint_tier`) carry an explicit None rather than being absent, per the Task 1
# decision recorded in that plan.

RESPONSE_EVENT_TYPE = "response"


def subject_of(objective):
    """The text before the first ':' in a namespaced objective.

    D-06's `emt:airway.opa` yields `emt`. An unnamespaced or empty objective
    yields `""` rather than raising.
    """
    if not objective or ":" not in objective:
        return ""
    return objective.split(":", 1)[0]


def evidence_key(q):
    """The key a response event is recorded and deduplicated against.

    `q["item_id"]` when one has been assigned (plan 01-04), else a positional
    fallback so the key stays deterministic before any item carries a real
    id. Used identically by `response_event()` and by a caller computing the
    attempt number ahead of building an event, so the two never drift apart.
    """
    return q.get("item_id") or ("ref:" + q["id"])


def idempotency_canon(q, answer):
    """The canonical form used for deduplication, extended for `short`.

    `runtime.canonical_response()` returns `None` for a constructed response
    by design (it has no canonical form to score against). Idempotency still
    needs *something* comparable, so a `short` answer's whitespace-collapsed,
    lowercased text is hashed instead. This is the one documented extension
    RESEARCH.md Pitfall 1 requires; enforcement of the resulting key lands in
    plan 01-07 — this function only computes and stores it.
    """
    canon = canonical_response(q, answer)
    if canon is not None:
        return canon
    text = " ".join(str(answer or "").split()).lower()
    return "short:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def dedupe_key(session_id, item_key, attempt_num, canon):
    """A sha256 hex digest identifying one attempt at one item in one session."""
    raw = "%s|%s|%d|%s" % (session_id, item_key, attempt_num, canon)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def response_event(session_id, q, answer, score, mode, attempt_num, bank,
                    response_time_ms=None, confidence=None, source_ref=None):
    """Build one full response event dict. Every key named in this plan's
    must_haves is present on every event — reserved fields carry an explicit
    `None`, never an absent key, so a consumer can tell "not captured" from
    "field did not exist in this era" (Task 1 decision, option-a).
    """
    objective = q.get("objective", "")
    key = evidence_key(q)
    canon = idempotency_canon(q, answer)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": RESPONSE_EVENT_TYPE,
        "ts": utc_now(),
        "session_id": session_id,
        "item_id": q.get("item_id", ""),
        "item_ref": q["id"],
        "item_type": q["type"],
        "bank": bank,
        "objective": objective,
        "subject": subject_of(objective),
        "mode": mode,
        "attempt_number": attempt_num,
        "answer": answer,
        "canonical": canonical_response(q, answer),
        "score": score,
        "response_time_ms": response_time_ms,
        "confidence": confidence,
        "error_category": None,   # no error taxonomy exists before Phase 6
        "hint_tier": None,        # no hint ladder exists before Phase 8
        "review_state": "pending" if q["type"] == "short" else "n/a",
        "dedupe_key": dedupe_key(session_id, key, attempt_num, canon),
        "source_ref": source_ref,
    }


def append_event(log, event):
    """The ONE evidence writer.

    Every surface, the migration tool, and every future phase call this
    function and never `append_line` directly — the same discipline
    `runtime.score_response` holds for scoring, applied to persistence.
    """
    append_line(log, json.dumps(event, ensure_ascii=False, sort_keys=True))
    return {"status": "recorded", "event_id": event["event_id"]}


def events(log):
    """Yield validated event dicts from `iter_raw`.

    Skips and warns on an event whose `event_type` is unknown or whose
    `schema_version` is newer than this build supports, so a log written by a
    later version of this tool degrades instead of crashing (D-09).
    """
    for lineno, obj, raw in iter_raw(log):
        et = obj.get("event_type")
        sv = obj.get("schema_version")
        if et not in KNOWN_EVENT_TYPES:
            print("warn  %s:%d unknown event_type %r, skipped" %
                  (os.path.basename(log), lineno, et))
            continue
        if not isinstance(sv, int) or sv > EVENT_SCHEMA_VERSION:
            print("warn  %s:%d schema_version %r unsupported, skipped" %
                  (os.path.basename(log), lineno, sv))
            continue
        yield obj


def attempt_number(log, session_id, item_key):
    """One more than the count of existing response events for this session
    and this evidence key.

    Defined here slightly ahead of the Phase 6 cursor-hold that will make the
    number exceed 1 in practice, so evidence written now and evidence written
    later live under the same dedupe rule (D-18).
    """
    n = 0
    for ev in events(log):
        if ev.get("event_type") != RESPONSE_EVENT_TYPE:
            continue
        if ev.get("session_id") != session_id:
            continue
        if evidence_key({"item_id": ev.get("item_id", ""),
                         "id": ev.get("item_ref", "")}) == item_key:
            n += 1
    return n + 1


def objective_history(log, objective):
    """Every response event whose `objective` equals the argument, oldest
    first, sorted by `(ts, log order)` so events sharing a timestamp keep a
    stable, reproducible order.

    A linear scan of the log for now; plan 01-08 replaces the scan with the
    sqlite index behind this same signature. Never recomputes a score — reads
    the recorded `score` field.
    """
    rows = []
    for idx, ev in enumerate(events(log)):
        if ev.get("event_type") != RESPONSE_EVENT_TYPE:
            continue
        if ev.get("objective") != objective:
            continue
        rows.append((ev.get("ts", ""), idx, {
            "ts": ev.get("ts"),
            "session_id": ev.get("session_id"),
            "item_id": ev.get("item_id"),
            "item_ref": ev.get("item_ref"),
            "mode": ev.get("mode"),
            "score": ev.get("score"),
            "attempt_number": ev.get("attempt_number"),
            "confidence": ev.get("confidence"),
            "response_time_ms": ev.get("response_time_ms"),
        }))
    rows.sort(key=lambda r: (r[0], r[1]))
    return [r[2] for r in rows]
