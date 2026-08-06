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
import contextlib
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

# "retraction" is added by this plan (01-07); response events are the only
# ones this build wrote before it. events() skips and warns on anything
# outside this set (D-09), so a log written by a later build's event type
# degrades instead of crashing.
KNOWN_EVENT_TYPES = ("response", "retraction")

# Bounds the tail scan `append_line_checked` and `recent_dedupe_keys` run to
# decide whether an event is a duplicate. A dedupe_key contains the
# session_id, so a duplicate can only ever come from the same sitting, and a
# sitting is at most a few hundred events -- 8 MiB is three orders of
# magnitude of headroom over that. The residual is stated honestly rather
# than assumed away: a duplicate older than this window would be recorded a
# second time, which is recoverable by retraction and is not expected to
# happen within one sitting.
DEDUPE_WINDOW_BYTES = 8 * 1024 * 1024


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


@contextlib.contextmanager
def locked(fd):
    """Hold a platform advisory lock on `fd` for the duration of the `with`
    block; the one lock implementation `append_line` and
    `append_line_checked` both use, so there is exactly one
    `msvcrt.locking` acquire site and one `fcntl.flock` acquire site in this
    module rather than one per caller.

    The Microsoft C runtime implements Windows' `O_APPEND` as `lseek(fd, 0,
    SEEK_END)` followed by `write()` — two steps, not one atomic step — so
    two concurrent appenders can interleave or clobber each other's line
    with no lock held. This is a still-open, officially-acknowledged Python
    bug (bpo-42606). The lock is taken on a one-byte range at the start of
    the file, which is a mutex over the file rather than a lock on any real
    byte of content, and released on the same range regardless of where the
    caller's own read or write left the file position. POSIX's `O_APPEND`
    is genuinely atomic, so `fcntl.flock` here is defense in depth rather
    than the only thing standing between two writers and a torn line.
    """
    win = sys.platform == "win32"
    if win:
        import msvcrt
        pos = os.lseek(fd, 0, os.SEEK_CUR)
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        yield
    finally:
        if win:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            os.lseek(fd, pos, os.SEEK_SET)
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)


def append_line(path, line):
    """Append one line to the log, holding `locked()` across exactly one
    write syscall.

    `line` is a `str` with no trailing newline; it is encoded once to UTF-8 with a
    single `b"\\n"` appended, and that whole payload goes out in a single write.
    One syscall is the point: it is what keeps a torn write to at most one line.

    Returns the number of bytes written.
    """
    payload = line.encode("utf-8") + b"\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        with locked(fd):
            if sys.platform == "win32":
                # bpo-42606: the CRT's O_APPEND is lseek+write, not one
                # atomic step, so this lseek-then-write happens while the
                # lock is held rather than relying on O_APPEND alone.
                os.lseek(fd, 0, os.SEEK_END)
            n = os.write(fd, payload)
    finally:
        os.close(fd)
    return n


def _tail_dedupe_keys(fd, window):
    """The shared tail scan behind `recent_dedupe_keys` and
    `append_line_checked`: seek to `max(0, size - window)`, drop a leading
    partial line when the seek did not land at byte 0 (that fragment
    belongs to the line before it, not a record of its own), and parse the
    rest with the same defensive per-line handling `iter_raw` uses.

    Returns a dict of dedupe_key -> event_id for every response event found
    in the scanned tail whose event_id has not also been retracted within
    that same tail -- retraction-aware, so a retracted response's key is
    not mistaken for still-recorded when the same answer is resubmitted
    (D-10; exercised by `tests/evidence_roundtrip.py`'s test_retraction).
    A retraction whose target lies outside the scanned window is a residual
    this bound accepts, the same way an old duplicate is: both are rare and
    both are recoverable, one by retraction and the other by the fact that
    a fresh submission just becomes attempt N+1.
    """
    size = os.lseek(fd, 0, os.SEEK_END)
    start = max(0, size - window)
    os.lseek(fd, start, os.SEEK_SET)
    data = os.read(fd, size - start) if size > start else b""
    text = data.decode("utf-8", errors="replace")
    if start > 0:
        nl = text.find("\n")
        text = text[nl + 1:] if nl != -1 else ""
    keys = {}
    retracted_seen = set()
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except (ValueError, TypeError):
            continue
        if not isinstance(obj, dict):
            continue
        et = obj.get("event_type")
        if et == "retraction":
            target = obj.get("retracts")
            if target:
                retracted_seen.add(target)
            continue
        if et != RESPONSE_EVENT_TYPE:
            continue
        dk, eid = obj.get("dedupe_key"), obj.get("event_id")
        if dk and eid:
            keys[dk] = eid
    if retracted_seen:
        keys = {dk: eid for dk, eid in keys.items() if eid not in retracted_seen}
    return keys


def recent_dedupe_keys(path, window=DEDUPE_WINDOW_BYTES):
    """Public, read-only view of the dedupe keys live in the last `window`
    bytes of `path` -- for a caller that wants to inspect the same bound
    `append_line_checked` uses without taking the write lock. Opens its own
    read-only handle; a caller that already holds `locked()` on a write fd
    for `path` (namely `append_line_checked` itself) uses `_tail_dedupe_keys`
    on that same fd instead, so this process never requests a second
    Windows record lock on a file it is already holding one on.
    """
    if not os.path.exists(path):
        return {}
    fd = os.open(path, os.O_RDONLY)
    try:
        return _tail_dedupe_keys(fd, window)
    finally:
        os.close(fd)


def append_line_checked(path, line, dedupe_key):
    """Append `line` unless a live response event already carries
    `dedupe_key` within the last `DEDUPE_WINDOW_BYTES` of the log.

    Opens the file descriptor once and holds `locked()` across both the
    tail-read check and the write, so the whole check-then-append sequence
    is race-free rather than advisory -- two processes racing this call
    cannot both observe "not present yet" and both write. `dedupe_key` of
    `None` never dedupes: a retraction always writes, because whether to
    write it was already decided by its caller (`already_retracted` is a
    separate, non-writing path in `cmd_retract`), not by this function.

    Returns `(written, existing_event_id)`: `written` is `True` and
    `existing_event_id` is `None` when the line was appended; `written` is
    `False` and `existing_event_id` names the event already on disk when
    it was not.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        with locked(fd):
            if dedupe_key is not None:
                existing = _tail_dedupe_keys(fd, DEDUPE_WINDOW_BYTES)
                event_id = existing.get(dedupe_key)
                if event_id is not None:
                    return False, event_id
            os.lseek(fd, 0, os.SEEK_END)
            os.write(fd, line.encode("utf-8") + b"\n")
            return True, None
    finally:
        os.close(fd)


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
    """The canonical form used for deduplication, extended for `short`, and
    the same value `response_event()` stores in the event's `canonical`
    field (D-17): the two must never diverge, or the attempt rule below
    compares the wrong thing and every `short` retry looks like a new
    attempt.

    `runtime.canonical_response()` returns `None` for a constructed response
    by design (it has no canonical form to score against). Idempotency still
    needs *something* comparable, so a `short` answer's whitespace-collapsed,
    lowercased text is hashed instead. This is the one documented extension
    RESEARCH.md Pitfall 1 requires. The result is never `None`: every other
    item type already has a canonical form of its own.
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

    `canonical` stores `idempotency_canon()`'s output, not
    `runtime.canonical_response()`'s directly — the same value fed into
    `dedupe_key` below, so `attempt_number()`'s "does the most recent live
    event's canonical equal this one" comparison is comparing the right
    thing for a `short` item too. It is never `None`.
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
        "canonical": canon,
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
    """The ONE evidence writer, and the one place that decides `recorded`
    versus `already_recorded`.

    Every surface, the migration tool, and every future phase call this
    function and never `append_line`/`append_line_checked` directly — the
    same discipline `runtime.score_response` holds for scoring, applied to
    persistence. `recorded` and `already_recorded` are different answers,
    not two spellings of "ok": PROTO-03 asks not just "does not
    double-record" but "and the tool says which happened," and a caller
    that collapses the two loses that.
    """
    written, existing_id = append_line_checked(
        log, json.dumps(event, ensure_ascii=False, sort_keys=True),
        event.get("dedupe_key"))
    if written:
        return {"accepted": True, "status": "recorded", "event_id": event["event_id"]}
    return {"accepted": False, "status": "already_recorded", "event_id": existing_id}


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


def attempt_number(log, session_id, item_key, canon):
    """D-17/D-18 in one sentence: an attempt is opened by a distinct
    canonical answer and stays open until a different canonical answer
    arrives.

    Finds the most recent *live* response event for this session and item
    key (reading through `live_events`, so a retracted response cannot open
    or continue an attempt). If there is none, this is attempt 1. If its
    `canonical` equals `canon`, this submission is a retry of that same
    attempt, so it returns that event's own `attempt_number` — which
    reproduces the same `dedupe_key` upstream and lets `append_event`
    dedupe it. Otherwise a genuinely different answer has arrived, so it
    returns one more than that attempt number, opening the next attempt
    with a dedupe key that has never been seen.

    Defined here slightly ahead of the Phase 6 cursor-hold that will make
    the number exceed 1 routinely in practice, so evidence recorded before
    and after that phase lives under one rule rather than in two
    inconsistent eras (D-18).
    """
    last = None
    for ev in live_events(log):
        if ev.get("event_type") != RESPONSE_EVENT_TYPE:
            continue
        if ev.get("session_id") != session_id:
            continue
        if evidence_key({"item_id": ev.get("item_id", ""),
                         "id": ev.get("item_ref", "")}) == item_key:
            last = ev
    if last is None:
        return 1
    if last.get("canonical") == canon:
        return last.get("attempt_number", 1)
    return last.get("attempt_number", 1) + 1


def objective_history(log, objective):
    """Every LIVE response event whose `objective` equals the argument,
    oldest first, sorted by `(ts, log order)` so events sharing a
    timestamp keep a stable, reproducible order.

    Reads through `live_events`, never `events` — a retracted response must
    never contribute to a count a learner sees (D-10). A linear scan of the
    log for now; plan 01-08 replaces the scan with the sqlite index behind
    this same signature. Never recomputes a score — reads the recorded
    `score` field.
    """
    rows = []
    for idx, ev in enumerate(live_events(log)):
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


# ---- disposable sqlite3 projection (01-08) --------------------------------
# D-08: the log is the only authority. This index is a materialized view
# over it, never a second source of truth -- deleting it and letting the
# next query rebuild it returns the same answer every time
# (test_index_is_disposable proves it for a missing, corrupt and
# permanently-unwritable index). `sqlite3` is imported lazily inside each
# of these functions rather than at module top, so a Python build without
# it still imports this module and still records and reads evidence
# through the live_events() linear-scan fallback in objective_history().

INDEX_VERSION = 1   # The projection's OWN version, bumped whenever the table
                     # shape below changes, which forces a full rebuild
                     # rather than a subtly wrong query against an old
                     # shape. This is not a published contract the way
                     # schemas/*.json are -- the index is disposable, so
                     # bumping this number costs a rebuild and nothing
                     # else, which is exactly why it lives here and not in
                     # schemas/.


def _index_connect(path):
    import sqlite3
    return sqlite3.connect(path)


def _create_index_schema(con):
    con.execute("""CREATE TABLE events (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE,
        ts TEXT,
        session_id TEXT,
        item_id TEXT,
        item_ref TEXT,
        objective TEXT,
        subject TEXT,
        mode TEXT,
        item_type TEXT,
        score TEXT,
        attempt_number INTEGER,
        confidence TEXT,
        response_time_ms INTEGER,
        review_state TEXT,
        retracted INTEGER DEFAULT 0)""")
    con.execute("CREATE INDEX idx_objective ON events(objective, ts)")
    con.execute("CREATE INDEX idx_subject ON events(subject, ts)")
    con.execute("CREATE INDEX idx_session ON events(session_id, ts)")
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")


def _insert_response_row(con, ev):
    """Insert one response event's projected row. `score` is stored as its
    JSON encoding so the three states `true`, `false` and `null` all
    survive the round trip -- a `short` item awaiting a marker is not a
    wrong answer, and collapsing that distinction here would undo the one
    `runtime.score_response`'s docstring exists to protect.
    """
    con.execute(
        "INSERT OR IGNORE INTO events (event_id, ts, session_id, item_id, "
        "item_ref, objective, subject, mode, item_type, score, "
        "attempt_number, confidence, response_time_ms, review_state) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (ev.get("event_id"), ev.get("ts"), ev.get("session_id"),
         ev.get("item_id"), ev.get("item_ref"), ev.get("objective", ""),
         ev.get("subject", ""), ev.get("mode"), ev.get("item_type"),
         json.dumps(ev.get("score")), ev.get("attempt_number"),
         ev.get("confidence"), ev.get("response_time_ms"),
         ev.get("review_state")))


def _mark_index_retracted(con, ids):
    """Mark rows retracted -- never deleted, so the index mirrors the log's
    own D-10 semantics.
    """
    if ids:
        con.executemany("UPDATE events SET retracted = 1 WHERE event_id = ?",
                        [(eid,) for eid in ids])


def _set_index_meta(con, log_bytes, log_mtime_ns):
    con.executemany(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        [("index_version", str(INDEX_VERSION)),
         ("event_schema_version", str(EVENT_SCHEMA_VERSION)),
         ("log_bytes", str(log_bytes)),
         ("log_mtime_ns", str(log_mtime_ns))])


def rebuild_index(log, index):
    """A full rebuild of the disposable projection from `log`, written
    through `index + ".tmp"` and then `os.replace()`'d into place -- the
    same tmp-then-replace pattern `runtime.write_session()` uses for a
    session file, so a half-built index can never replace a good one.

    Built on `events(log)`, which inherits `iter_raw`'s per-line
    skip-and-report (D-09): a torn or malformed line warns and is skipped
    rather than aborting the whole rebuild.
    """
    tmp = index + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    os.makedirs(os.path.dirname(index) or ".", exist_ok=True)
    con = _index_connect(tmp)
    try:
        _create_index_schema(con)
        for ev in events(log):
            if ev.get("event_type") != RESPONSE_EVENT_TYPE:
                continue
            _insert_response_row(con, ev)
        _mark_index_retracted(con, retracted_ids(log))
        size = os.path.getsize(log) if os.path.exists(log) else 0
        mtime_ns = os.stat(log).st_mtime_ns if os.path.exists(log) else 0
        _set_index_meta(con, size, mtime_ns)
        con.commit()
    finally:
        con.close()
    os.replace(tmp, index)


def index_stale(log, index):
    """Whether `index` needs a rebuild before it can answer a query for
    `log`, and the byte offset an incremental rebuild should resume from.

    Returns `(stale, offset)`. `offset` is always 0 when a FULL rebuild is
    required -- a missing index, an index that cannot even be opened, an
    `index_version`/`event_schema_version` mismatch (the table shape or the
    event shape moved since this index was built), or a log that is
    SMALLER than the `log_bytes` this index already recorded, which means
    the log was truncated or rewritten and an incremental pass would
    silently index the wrong bytes at that offset. Otherwise `offset` is
    the previously recorded `log_bytes`, for an incremental pass. Not stale
    only when the log's current size and mtime both match the index's own
    record exactly.
    """
    if not os.path.exists(index):
        return True, 0
    log_size = os.path.getsize(log) if os.path.exists(log) else 0
    log_mtime_ns = os.stat(log).st_mtime_ns if os.path.exists(log) else 0
    con = _index_connect(index)
    try:
        meta = dict(con.execute("SELECT key, value FROM meta").fetchall())
    finally:
        con.close()
    if meta.get("index_version") != str(INDEX_VERSION):
        return True, 0
    if meta.get("event_schema_version") != str(EVENT_SCHEMA_VERSION):
        return True, 0
    try:
        recorded_bytes = int(meta.get("log_bytes", "0"))
    except (TypeError, ValueError):
        return True, 0
    if log_size < recorded_bytes:
        return True, 0
    if log_size == recorded_bytes and str(log_mtime_ns) == meta.get("log_mtime_ns", ""):
        return False, 0
    return True, recorded_bytes


def _index_tail_update(log, index, offset):
    """Extend `index` with response events found in `log` from byte
    `offset` onward, marking any retraction found in that same tail.
    Retraction is monotonic -- an event is never un-retracted -- so
    applying only the new tail's retractions here is correct even when an
    earlier retraction's own target sits before `offset`.
    """
    con = _index_connect(index)
    try:
        with open(log, "rb") as fh:
            fh.seek(offset)
            data = fh.read()
        new_size = offset + len(data)
        text = data.decode("utf-8", errors="replace")
        new_retractions = set()
        for raw in text.splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except (ValueError, TypeError):
                print("warn  %s tail line malformed, skipped" % os.path.basename(log))
                continue
            if not isinstance(obj, dict):
                print("warn  %s tail line malformed, skipped" % os.path.basename(log))
                continue
            et = obj.get("event_type")
            if et == RETRACTION_EVENT_TYPE:
                target = obj.get("retracts")
                if target:
                    new_retractions.add(target)
                continue
            if et != RESPONSE_EVENT_TYPE:
                continue
            _insert_response_row(con, obj)
        _mark_index_retracted(con, new_retractions)
        mtime_ns = os.stat(log).st_mtime_ns if os.path.exists(log) else 0
        _set_index_meta(con, new_size, mtime_ns)
        con.commit()
    finally:
        con.close()


def ensure_index(log, index):
    """Bring `index` up to date with `log` -- a full rebuild or an
    incremental tail extension, whichever `index_stale()` says is needed --
    and return `"used"` when a query may now read the index, or
    `"fallback"` when it could not be built or extended at all.

    Every step runs inside one `try/except Exception`: an index that
    cannot be built must never stop a learner from studying, the same
    degrade-never-block rule PROJECT.md applies to the model layer, applied
    here to the query layer. On any failure this prints a warning, removes
    the index file if one exists (so the next call starts clean), and
    returns `"fallback"` -- the caller is expected to answer the query
    through `live_events()` instead.

    Takes the same advisory lock `append_line` takes around the log, but
    around the index's own on-disk `.lock` file, so two concurrent queries
    cannot rebuild or extend the index over each other.
    """
    try:
        stale, offset = index_stale(log, index)
        if not stale:
            return "used"
        lock_path = index + ".lock"
        os.makedirs(os.path.dirname(index) or ".", exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
        try:
            with locked(fd):
                # Re-check now that the lock is held: another process may
                # have already rebuilt or extended the index while this one
                # waited for the lock.
                stale, offset = index_stale(log, index)
                if not stale:
                    return "used"
                if offset == 0:
                    rebuild_index(log, index)
                else:
                    size = os.path.getsize(log) if os.path.exists(log) else 0
                    if size < offset:
                        rebuild_index(log, index)
                    else:
                        _index_tail_update(log, index, offset)
        finally:
            os.close(fd)
        return "used"
    except Exception as exc:
        print("warn  evidence index unavailable (%s); falling back to a full log scan" %
              exc)
        try:
            if os.path.exists(index):
                os.remove(index)
        except Exception:
            pass
        return "fallback"


# ---- retractions --------------------------------------------------------
# D-10: undo is an append, never a removal. A retraction is a compensating
# event that references the event it undoes; nothing is ever deleted, so a
# raw line count of the log overstates history and every view or count a
# learner sees has to read through the filter below instead.

RETRACTION_EVENT_TYPE = "retraction"


def retraction_event(retracts, reason, actor="human"):
    """Build one retraction event: an append-only compensating record that
    suppresses `retracts` in every view (`live_events` and everything built
    on it) without removing anything from the log.

    `reason` must be a non-empty string — an unexplained undo is not an
    audit trail, so an empty one raises `ValueError` rather than being
    silently accepted. `dedupe_key` is always `None`: a retraction always
    writes once its caller (`cmd_retract`) has decided to write it: whether
    the target is already retracted is that caller's job to check first, an
    `already_retracted` response that appends nothing, not a job for
    `append_line_checked`'s ordinary dedupe path.
    """
    if not reason or not reason.strip():
        raise ValueError("a retraction reason must be a non-empty string; "
                          "an unexplained undo is not an audit trail")
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": RETRACTION_EVENT_TYPE,
        "ts": utc_now(),
        "retracts": retracts,
        "reason": reason,
        "actor": actor,
        "dedupe_key": None,
    }


def retracted_ids(log):
    """Every event_id ever named by a retraction's `retracts` field,
    collected over the WHOLE log in one pass before anything is emitted —
    so a retraction that physically precedes its target in the file (which
    a migration can produce, importing records in source order rather than
    chronological order) still suppresses it. See `live_events`.
    """
    ids = set()
    for ev in events(log):
        if ev.get("event_type") == RETRACTION_EVENT_TYPE:
            target = ev.get("retracts")
            if target:
                ids.add(target)
    return ids


def live_events(log):
    """Every non-retraction event whose `event_id` is not in
    `retracted_ids(log)`, in log order.

    This is the only function views may use for counting; `events()`
    remains the raw reader for a tool that genuinely needs retracted
    history too, such as an audit. `attempt_number` and `objective_history`
    both read through this rather than `events` (D-10).
    """
    retracted = retracted_ids(log)
    for ev in events(log):
        if ev.get("event_type") == RETRACTION_EVENT_TYPE:
            continue
        if ev.get("event_id") in retracted:
            continue
        yield ev


def event_by_id(log, event_id):
    """The raw event dict for `event_id`, or `None` — used to validate a
    retract target before anything is appended. Reads through `events()`,
    not `live_events()`, because an already-retracted event is still a
    valid retract target to look up (its retraction status is `cmd_retract`'s
    next question, not this function's).
    """
    for ev in events(log):
        if ev.get("event_id") == event_id:
            return ev
    return None
