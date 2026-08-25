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
import re
import sys
import uuid

from runtime import REPORT_VERSION, SESSION_VERSION, canonical_response, response_text


# Version 2 (Phase 6): response events may carry an integer-or-null
# `hint_tier` (D-15) and a new `hint` event type exists (D-16). Readers keep
# accepting version-1 events: the version check in `events()` is a
# greater-than comparison, and version-1 shapes are unchanged.
EVENT_SCHEMA_VERSION = 2

EVIDENCE_DIRNAME = "_evidence"
LOG_FILENAME = "evidence.jsonl"
INDEX_FILENAME = "evidence_index.sqlite3"

# "retraction" was added by plan 01-07, "mark" by plan 01-09, "day_tick" by
# plan 01-10, "term_lookup" by plan 03.1-02, "key_review" by plan 03.1-03,
# "hint" by plan 06-01, "selection" by plan 07-04, "lesson_complete" by
# plan 10-02, "cap_override" by plan 10-04, "model_interaction" /
# "mark_proposal" by plan 08-03, "visual_action" by plan 06.1-02, and
# "gate_skip" by plan 06.2-01 -- response events are the only ones this
# build wrote before 01-07. events() skips and warns on anything outside
# this set (D-09), so a log written by a later build's event type degrades
# instead of crashing.
KNOWN_EVENT_TYPES = ("response", "retraction", "mark", "day_tick",
                     "term_lookup", "key_review", "hint", "selection",
                     "lesson_complete", "cap_override",
                     "model_interaction", "mark_proposal", "visual_action",
                     "gate_skip")

# The record of what a sitting asked for (D-03): one event per session, so a
# deleted session file never destroys the ability to reproduce the sitting.
SELECTION_EVENT_TYPE = "selection"

# A committed semantic state-changing action on a visual item (plan 06.1-02,
# D-04/D-05): appended only on a successful commit -- native
# control/Enter/Space, tap, or pointer-up after a changed drag. Pointer
# telemetry, focus, hover, tentative state, cancelled gestures, and unchanged
# commits never append. Final submit stays the ordinary response event.
VISUAL_ACTION_EVENT_TYPE = "visual_action"

# The Phase 6.2 gate_skip event (D-07): a learner read ahead past a gated
# check without answering. It is deliberately its own event type, never a
# `response` carrying a null score -- conflating them would make a skip
# indistinguishable from an unmarked attempt in every downstream count.
GATE_SKIP_EVENT_TYPE = "gate_skip"

# The two gate modes that may be skipped. "off" never offers a skip: an
# off lesson is the 3.1 reader, so there is nothing to record.
GATE_MODES = ("required", "recommended")

# The one context value that marks a response event as served by a lesson
# gate rather than by a quiz sitting (D-08). The default "quiz" keeps every
# pre-6.2 call site byte-compatible; "lesson_gate" is written only by the
# one new call site this phase adds (CONTEXT D-08, 06.2-RESEARCH section 2).
LESSON_GATE_CONTEXT = "lesson_gate"

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

    Returns a dict of dedupe_key -> event_id for every dedupe-eligible
    event found in the scanned tail whose event_id has not also been
    retracted within that same tail -- retraction-aware, so a retracted
    response's key is not mistaken for still-recorded when the same answer
    is resubmitted (D-10; exercised by `tests/evidence_roundtrip.py`'s
    test_retraction), and a retracted mark's key is not mistaken for
    still-recorded when the same verdict is remarked (D-12; exercised by
    test_mark_flow). "Dedupe-eligible" is any event whose own `dedupe_key`
    is non-null -- response and mark events today -- rather than a
    hardcoded list of event types, so a future event type that carries a
    real `dedupe_key` dedupes correctly without a second edit here. A
    retraction whose target lies outside the scanned window is a residual
    this bound accepts, the same way an old duplicate is: both are rare and
    both are recoverable, one by retraction and the other by the fact that
    a fresh submission (or remark) just becomes the next live one.
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
        if et == RETRACTION_EVENT_TYPE:
            target = obj.get("retracts")
            if target:
                retracted_seen.add(target)
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

    Opened with `errors="replace"`: a torn tail can cut inside a multi-byte
    UTF-8 character, and a strict decode would raise `UnicodeDecodeError` out
    of this generator and take down every reader built on it (`events`,
    `live_events`, `retracted_ids`, `attempt_number`, `objective_history`'s
    fallback, `marks_by_event`, `render_attempt_md`, `render_session_json`,
    `day_log_from_events`). With the lenient decode, the torn bytes become
    U+FFFD, `json.loads` below fails on the resulting string, and the
    `except (ValueError, TypeError)` already here reports and skips the line
    exactly as it does for a JSON-malformed one. This matches the posture
    `_tail_dedupe_keys` and `_index_tail_update` already take for the same
    reason, on the same log.
    """
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8", errors="replace") as fh:
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
                    response_time_ms=None, confidence=None, source_ref=None,
                    hint_tier=None, selection_mode=None, context="quiz", *,
                    check_source=None, interaction_version=None,
                    error_category=None):
    """Build one full response event dict. Every key named in this plan's
    must_haves is present on every event — reserved fields carry an explicit
    `None`, never an absent key, so a consumer can tell "not captured" from
    "field did not exist in this era" (Task 1 decision, option-a).

    `hint_tier` is the highest tier actually shown when this response was
    submitted (D-15): None means the ladder did not apply or no tier existed,
    0 means tier 0 was shown -- null-versus-zero is preserved exactly. Defaults
    to None so pre-Phase-6 callers (and v1-shaped records) stay byte-compatible.

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
        "error_category": error_category,   # "timeout" for a check run the deadline killed; no other taxonomy exists before Phase 8
        "check_source": check_source,   # the learner's submitted source verbatim for a `check` item, null otherwise (05-01)
        "interaction_version": interaction_version,   # the public interaction-contract version that served a `check` item, null otherwise (05-01)
        "hint_tier": hint_tier,   # integer-or-null since Phase 6 (D-15)
        "selection_mode": selection_mode,   # the composition that served this item (07-04)
        "context": context,   # "quiz" (default) or "lesson_gate" (06.2, D-08)
        "review_state": "pending" if q["type"] == "short" else "n/a",
        "dedupe_key": dedupe_key(session_id, key, attempt_num, canon),
        "source_ref": source_ref,
    }


def gate_skip_event(session_id, bank, lesson_slug, check_item_id,
                     check_item_ref, objective, gate_mode):
    """Build one gate_skip event: a learner read ahead past the gated check
    named by `check_item_id` without answering (D-07, 06.2-UI-SPEC section
    6.3). Mirrors `day_tick_event()`/`mark_event()` exactly: its own
    envelope, a deliberately narrow dedupe key, and `ValueError` on a
    malformed argument -- and, structurally, **no `score` key at all**, not
    even `None` (criterion 8's concrete form: a skip is not a response).

    `gate_mode` is the resolved gate mode the learner skipped past, never
    "off": an off lesson offers no skip, so recording one would be
    fabricating an event that never happened. `dedupe_key` is a hash over
    `(session_id, check_item_id)` alone, so a retried skip POST for the
    same check in the same sitting records once and reports
    `already_recorded` -- exactly the shape `day_tick_event()` uses for a
    lane ticked twice.
    """
    if gate_mode not in GATE_MODES:
        raise ValueError(
            "gate_skip_event: gate_mode must be one of %r, got %r"
            % (GATE_MODES, gate_mode))
    if not check_item_id:
        raise ValueError(
            "gate_skip_event: check_item_id must be a non-empty string")
    raw = "%s|%s" % (session_id, check_item_id)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": GATE_SKIP_EVENT_TYPE,
        "ts": utc_now(),
        "session_id": session_id,
        "bank": bank,
        "lesson_slug": lesson_slug,
        "check_item_id": check_item_id,
        "check_item_ref": check_item_ref,
        "objective": objective,
        "gate_mode": gate_mode,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


def gate_state(log, session_id, check_item_id):
    """The derived gate state for one (session, check) pair -- "open",
    "cleared", or "skipped" -- read from the one evidence log, never stored
    as per-lesson progress (D-06).

    Resolution is pair-level (06.2-RESEARCH section 8): any live response
    event with context "lesson_gate" for the pair means "cleared"
    regardless of a prior skip; a live gate_skip with no subsequent
    response means "skipped"; otherwise "open". Reads through
    `live_events()` -- the same retraction discipline every other view uses
    (D-10) -- so a retracted response returns the gate to its prior state.
    Session-scoped by construction: the `session_id` argument is part of
    every match, so a check cleared in an earlier sitting gates again in a
    new one (06.2-UI-SPEC section 14 DEFAULT).

    `check_item_id` is the id the lesson's `[!CHECK: <id>]` names; a
    response event may record it as either the positional `item_ref` or the
    opaque `item_id`, and both are matched.
    """
    cleared = False
    skipped = False
    for ev in live_events(log):
        if ev.get("session_id") != session_id:
            continue
        if ev.get("event_type") == RESPONSE_EVENT_TYPE:
            if (ev.get("context") == LESSON_GATE_CONTEXT
                    and (ev.get("item_ref") == check_item_id
                         or ev.get("item_id") == check_item_id)):
                cleared = True
        elif ev.get("event_type") == GATE_SKIP_EVENT_TYPE:
            if ev.get("check_item_id") == check_item_id:
                skipped = True
    if cleared:
        return "cleared"
    if skipped:
        return "skipped"
    return "open"


def gate_outcome_split(log, bank, session_id, gate_modes=None):
    """The gate outcome split (06.2-UI-SPEC section 11, GATE-06): cleared
    vs skipped over the distinct required-gate pairs encountered in one
    session, computed from live events at request time -- derived, never
    stored (Extensibility Rule 5).

    Pair-level aggregation (06.2-RESEARCH section 8): each distinct
    (session, check) pair resolves to exactly one outcome -- any live
    lesson-gate response means "cleared" regardless of a prior skip; a
    live gate_skip with no subsequent response means "skipped". The
    denominator is the count of distinct *required*-gate pairs; recommended
    gates are excluded because reading past one produces no event and
    counting it would be inventing a number (C8).

    A pair is classified as required when (a) `gate_modes` (the lesson's
    declared check-id -> gate-mode map, which the report path derives from
    `parse_lesson()`) names it required, or (b) the pair carries a
    gate_skip whose `gate_mode` is "required" -- the skip records the mode
    the gate actually rendered under. A pair with no required evidence is
    not counted.
    """
    pairs = {}
    for ev in live_events(log):
        if ev.get("session_id") != session_id:
            continue
        if ev.get("bank") != bank:
            continue
        if ev.get("event_type") == RESPONSE_EVENT_TYPE:
            if ev.get("context") != LESSON_GATE_CONTEXT:
                continue
            cid = ev.get("item_ref") or ev.get("item_id")
            if not cid:
                continue
            pair = pairs.setdefault(cid, {"cleared": False, "skipped": False,
                                          "required": None,
                                          "served_recommended": False})
            pair["cleared"] = True
        elif ev.get("event_type") == GATE_SKIP_EVENT_TYPE:
            cid = ev.get("check_item_id")
            if not cid:
                continue
            pair = pairs.setdefault(cid, {"cleared": False, "skipped": False,
                                          "required": None,
                                          "served_recommended": False})
            pair["skipped"] = True
            if ev.get("gate_mode") == "required":
                pair["required"] = True
            elif ev.get("gate_mode") == "recommended":
                # The skip records the mode the gate actually rendered
                # under -- a degraded sitting renders a declared required
                # gate as recommended and excludes it (section 5.7/11).
                pair["served_recommended"] = True
    cleared = 0
    skipped = 0
    for cid, pair in pairs.items():
        if pair.get("served_recommended"):
            continue
        if gate_modes is not None:
            required = gate_modes.get(cid) == "required"
        else:
            required = pair["required"] is True
        if not required:
            continue
        if pair["cleared"]:
            cleared += 1
        elif pair["skipped"]:
            skipped += 1
    total = cleared + skipped
    return {
        "denominator": total,
        "cleared": cleared,
        "skipped": skipped,
        "share_cleared": (round(cleared / total, 3) if total else None),
        "share_skipped": (round(skipped / total, 3) if total else None),
    }


def selection_event(session_id, bank, spec, item_keys, retention=None):
    """Build one selection event: the record of what a sitting asked for,
    appended once per session (D-03) and separate from the responses because
    the request is one fact about a sitting, not one fact per answer.

    `spec` is the resolved selection spec as passed to `select()`; only keys
    in `selection.SPEC_FIELDS` are recorded, so no item text, option text or
    answer key can ever enter the log under this event (T-07-03). `item_keys`
    is the ordered list of `evidence_key(q)` values that were served.

    `retention` (plan 10-03) is the sitting's server-derived Phase 10
    binding: the one snapshot id, the bounded normalized objective-weight map
    (each entry with its weight, named components and snapshot id), and the
    optional component trace. It is allowlisted to exactly those keys before
    recording -- a client path, answer key, hidden tier, or model payload is
    never echoed into the log (D-01, D-10, T-10-13).

    `dedupe_key` is derived from the session id alone, so a retried start for
    the same session reconciles (`already_recorded`) rather than doubling.
    """
    from selection import SPEC_FIELDS
    spec = {k: v for k, v in (spec or {}).items() if k in SPEC_FIELDS}
    event = {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": SELECTION_EVENT_TYPE,
        "ts": utc_now(),
        "session_id": session_id,
        "bank": bank,
        "selection_mode": spec.get("selection_mode", "practice"),
        "selection_spec": spec,
        "items": list(item_keys),
        "dedupe_key": dedupe_key(
            session_id, "selection", 0,
            json.dumps(spec, ensure_ascii=False, sort_keys=True)),
    }
    if retention is not None:
        if not isinstance(retention, dict):
            raise ValueError("selection_event: retention must be an object "
                             "or None")
        snapshot_id = retention.get("snapshot_id")
        objective_weights = retention.get("objective_weights")
        if not isinstance(snapshot_id, str) or not snapshot_id:
            raise ValueError("selection_event: retention.snapshot_id must be "
                             "a non-empty string")
        if not isinstance(objective_weights, dict):
            raise ValueError("selection_event: retention.objective_weights "
                             "must be an object")
        cleaned = {
            "snapshot_id": snapshot_id,
            "objective_weights": objective_weights,
        }
        if retention.get("trace") is not None:
            cleaned["trace"] = retention["trace"]
        event["retention"] = cleaned
    return event


def visual_action_event(session_id, q, interaction_version, action_id,
                        action_type, before_state, after_state, error_category,
                        invariants, feedback_anchor, hint_tier, bank,
                        mode=None, source_ref=None):
    """Build one `visual_action` event (plan 06.1-02, D-04/D-05): a committed
    semantic state-changing action on a visual item, appended only after a
    successful commit, never for pointer-down/move, focus, hover, tentative
    state, cancelled gestures, or unchanged commits.

    The event carries exactly the common audit fields plus
    `interaction_version`, `action_id`, `action_type`, canonical
    `before_state`/`after_state`, `error_category`, ordered `invariants`,
    opaque `feedback_anchor`, `hint_tier`, and `dedupe_key` (06.1-RESEARCH.md
    Resolved Questions item 2). It never accepts raw pointer events, CSS/SVG
    coordinates, screenshots, private accepted states/tolerance, a client
    verdict or hint tier, or authored reveal text.

    `action_id` is the client-generated lowercase canonical UUID-v4 string,
    stable across retries. The dedupe identity is
    `(session_id, item identity, interaction_version, action_id)`; an
    identical retry dedupes to `already_recorded`, while `do_interact`
    reports a conflict when the same action id is reused with different
    action/state.
    """
    key = evidence_key(q)
    raw = "%s|%s|%d|%s" % (session_id, key, interaction_version, action_id)
    objective = q.get("objective", "")
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": VISUAL_ACTION_EVENT_TYPE,
        "ts": utc_now(),
        "session_id": session_id,
        "item_id": q.get("item_id", ""),
        "item_ref": q["id"],
        "item_type": q["type"],
        "bank": os.path.basename(bank) if bank else None,
        "objective": objective,
        "subject": subject_of(objective),
        "mode": mode,
        "source_ref": source_ref,
        "interaction_version": interaction_version,
        "action_id": action_id,
        "action_type": action_type,
        "before_state": before_state,
        "after_state": after_state,
        "error_category": error_category,
        "invariants": list(invariants or []),
        "feedback_anchor": feedback_anchor,
        "hint_tier": hint_tier,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


def visual_actions(log, session_id, item_id=None):
    """The tutor-facing read view over committed visual actions (D-06):
    every LIVE `visual_action` event for `session_id` (optionally one item),
    in commit order, with a bounded agent-facing projection. Built on
    `live_events`, so a retracted action vanishes exactly as it vanishes from
    a report. Never returns raw pointer telemetry or private scoring
    material -- only the semantic states and runtime observations that were
    appended.
    """
    return [ev for ev in live_events(log)
            if ev.get("event_type") == VISUAL_ACTION_EVENT_TYPE
            and ev.get("session_id") == session_id
            and (item_id is None
                 or evidence_key({"item_id": ev.get("item_id", ""),
                                  "id": ev.get("item_ref", "")}) == item_id)]


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


def _like_escape(s):
    """Escape `%`, `_` and `\\` in `s` for a parameterized SQL `LIKE ...
    ESCAPE '\\'` clause, so an objective name that happens to contain a SQL
    wildcard character cannot widen a prefix match beyond D-06's `.`/`:`
    separator rule.
    """
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def event_matches(ev, objective, prefix=False, subject=None, mode=None,
                   session_id=None, since=None, bank=None):
    """The one filter predicate both `objective_history()`'s live-scan
    fallback and its indexed SQL path implement identically, and that
    `surfaces/evidence_cli.py` reuses to count retracted rows under the
    same query -- so the two paths, and the retracted count next to them,
    can never silently disagree about what a query matched.

    `subject`, when given, filters on the event's `subject` field ALONE and
    ignores `objective` entirely (D-06). Otherwise `objective` is matched
    exactly, or as a prefix when `prefix` is true: equal to `objective`, or
    beginning with `objective` followed by a `.` or a `:` separator -- so
    `emt:airway` matches `emt:airway.opa` but never `emt:airwaymanagement`.
    """
    if subject:
        if ev.get("subject") != subject:
            return False
    elif objective:
        ev_obj = ev.get("objective") or ""
        if prefix:
            if not (ev_obj == objective or ev_obj.startswith(objective + ".")
                    or ev_obj.startswith(objective + ":")):
                return False
        elif ev_obj != objective:
            return False
    if mode and ev.get("mode") != mode:
        return False
    if session_id and ev.get("session_id") != session_id:
        return False
    if since and (ev.get("ts") or "") < since:
        return False
    if bank and ev.get("bank") != bank:
        return False
    return True


def index_for_log(log):
    """The disposable projection sitting beside `log` -- for a caller
    holding only a log path, so it can reach the index without
    re-deriving the evidence directory itself.
    """
    return os.path.join(os.path.dirname(log), INDEX_FILENAME)


def _row_from_index_tuple(r):
    return {
        "ts": r[0], "session_id": r[1], "item_id": r[2], "item_ref": r[3],
        "mode": r[4], "score": json.loads(r[5]) if r[5] is not None else None,
        "attempt_number": r[6], "confidence": r[7], "response_time_ms": r[8],
        "objective": r[9], "bank": r[10], "context": r[11],
    }


def _objective_history_indexed(index, objective, prefix, subject, mode,
                                session_id, since, bank):
    """The SQL half of `objective_history()`. T-1-19: every filter value is
    bound as a `?` parameter -- never concatenated or `%`-formatted into the
    query text -- so a filter value can shape which parameter it binds to,
    never the query's own structure.
    """
    con = _index_connect(index)
    try:
        clauses = ["retracted = 0"]
        params = []
        if subject:
            clauses.append("subject = ?")
            params.append(subject)
        elif objective:
            if prefix:
                esc = _like_escape(objective)
                clauses.append(
                    "(objective = ? OR objective LIKE ? ESCAPE '\\' "
                    "OR objective LIKE ? ESCAPE '\\')")
                params.append(objective)
                params.append(esc + ".%")
                params.append(esc + ":%")
            else:
                clauses.append("objective = ?")
                params.append(objective)
        if mode:
            clauses.append("mode = ?")
            params.append(mode)
        if session_id:
            clauses.append("session_id = ?")
            params.append(session_id)
        if since:
            clauses.append("ts >= ?")
            params.append(since)
        if bank:
            clauses.append("bank = ?")
            params.append(bank)
        parts = [
            "SELECT ts, session_id, item_id, item_ref, mode, score, ",
            "attempt_number, confidence, response_time_ms, objective, bank, ",
            "context FROM events WHERE ",
            " AND ".join(clauses),
            " ORDER BY ts, seq",
        ]
        sql = "".join(parts)
        cur = con.execute(sql, params)
        return [_row_from_index_tuple(r) for r in cur.fetchall()]
    finally:
        con.close()


def _objective_history_fallback(log, objective, prefix, subject, mode,
                                 session_id, since, bank):
    """The linear-scan half of `objective_history()`, used when the index
    could not be built or extended at all (`ensure_index()` returned
    `"fallback"`). Reads through `live_events`, never `events` -- a
    retracted response must never contribute to a count a learner sees
    (D-10). Sorted by `(ts, log order)` so events sharing a timestamp keep
    a stable, reproducible order, identical to the indexed path's `ORDER BY
    ts, seq` (seq is assigned in log order too).
    """
    rows = []
    for idx, ev in enumerate(live_events(log)):
        if ev.get("event_type") != RESPONSE_EVENT_TYPE:
            continue
        if not event_matches(ev, objective, prefix, subject, mode, session_id,
                             since, bank):
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
            "objective": ev.get("objective"),
            "bank": ev.get("bank"),
            "context": ev.get("context", "quiz"),
        }))
    rows.sort(key=lambda r: (r[0], r[1]))
    return [r[2] for r in rows]


def objective_history(log, objective, prefix=False, subject=None, mode=None,
                       session_id=None, since=None, bank=None):
    """Every LIVE response event matching the given filters, oldest first,
    sorted by `(ts, log order)` so events sharing a timestamp keep a
    stable, reproducible order across repeated queries and across an index
    rebuild.

    Calls `ensure_index(log, index_for_log(log))` and queries the disposable
    sqlite3 projection (01-08) when it answers "used"; falls back to a
    linear scan over `live_events(log)` when it answers "fallback" --
    identical results, slower, so the index is provably a cache and never a
    second source of truth (D-08; `test_index_is_disposable` is what proves
    the two paths agree).

    `objective` is matched exactly by default; `prefix=True` also matches an
    objective beginning with `objective` followed by a `.` or `:`
    separator. `subject=` filters on the indexed `subject` column alone and
    ignores `objective` entirely. `mode=`, `session_id=` and `since=` (an
    ISO date compared as a string prefix against `ts`, which sorts
    correctly because timestamps are ISO-8601 UTC) are additional filters.
    `bank=` filters on the recorded bank basename (phase 7, D-13).
    Never recomputes a score -- reads the recorded `score` field.
    """
    index = index_for_log(log)
    status = ensure_index(log, index)
    if status == "used":
        try:
            return _objective_history_indexed(
                index, objective, prefix, subject, mode, session_id, since,
                bank)
        except Exception as exc:
            print("warn  evidence index unavailable (%s); falling back to a "
                  "full log scan" % exc)
            try:
                if os.path.exists(index):
                    os.remove(index)
            except Exception:
                pass
    return _objective_history_fallback(
        log, objective, prefix, subject, mode, session_id, since, bank)


def objective_rollup(rows):
    """Per-mode rollup over `objective_history()`'s rows: EVID-08's visible
    half. A drill-mode correct and an exam-mode correct are counted in
    different mode buckets and never summed into one figure -- the caller
    is the one place a combined total could sneak in, and it does not.

    Returns a dict mapping `mode` to `{"attempts", "correct", "wrong",
    "pending"}`. `score` of `True`, `False` and `None` are counted
    separately; `pending` is a `short` item awaiting a marker and is
    deliberately not folded into `wrong`.
    """
    by_mode = {}
    for row in rows:
        mode = row.get("mode") or "(unknown)"
        bucket = by_mode.setdefault(
            mode, {"attempts": 0, "correct": 0, "wrong": 0, "pending": 0})
        bucket["attempts"] += 1
        score = row.get("score")
        if score is True:
            bucket["correct"] += 1
        elif score is False:
            bucket["wrong"] += 1
        else:
            bucket["pending"] += 1
    return by_mode


# ---- disposable sqlite3 projection (01-08) --------------------------------
# D-08: the log is the only authority. This index is a materialized view
# over it, never a second source of truth -- deleting it and letting the
# next query rebuild it returns the same answer every time
# (test_index_is_disposable proves it for a missing, corrupt and
# permanently-unwritable index). `sqlite3` is imported lazily inside each
# of these functions rather than at module top, so a Python build without
# it still imports this module and still records and reads evidence
# through the live_events() linear-scan fallback in objective_history().

INDEX_VERSION = 3   # The projection's OWN version, bumped whenever the table
                     # shape below changes, which forces a full rebuild
                     # rather than a subtly wrong query against an old
                     # shape. This is not a published contract the way
                     # schemas/*.json are -- the index is disposable, so
                     # bumping this number costs a rebuild and nothing
                     # else, which is exactly why it lives here and not in
                     # schemas/. Version 2 (phase 7): the projection gained
                     # a `bank` column so a bank-scoped exposure query
                     # (D-13) has a fast path. Version 3 (phase 6.2): the
                     # projection gained a `context` column so
                     # objective_history() rows can name whether a
                     # response came from a quiz or a lesson gate (D-08).


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
        bank TEXT,
        context TEXT,
        retracted INTEGER DEFAULT 0)""")
    con.execute("CREATE INDEX idx_objective ON events(objective, ts)")
    con.execute("CREATE INDEX idx_subject ON events(subject, ts)")
    con.execute("CREATE INDEX idx_session ON events(session_id, ts)")
    con.execute("CREATE INDEX idx_bank ON events(bank, ts)")
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
        "attempt_number, confidence, response_time_ms, review_state, bank, "
        "context) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (ev.get("event_id"), ev.get("ts"), ev.get("session_id"),
         ev.get("item_id"), ev.get("item_ref"), ev.get("objective", ""),
         ev.get("subject", ""), ev.get("mode"), ev.get("item_type"),
         json.dumps(ev.get("score")), ev.get("attempt_number"),
         ev.get("confidence"), ev.get("response_time_ms"),
         ev.get("review_state"), ev.get("bank", ""), ev.get("context", "quiz")))


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
    try:
        con = _index_connect(index)
        try:
            meta = dict(con.execute("SELECT key, value FROM meta").fetchall())
        finally:
            con.close()
    except Exception:
        # Cannot even be opened -- a directory sitting at this path, a
        # corrupted file, anything at all: treat it the same as missing,
        # a full rebuild, rather than letting the exception escape and be
        # mistaken by a caller for "the index cannot be used at all".
        return True, 0
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


def capture_events(log):
    """Materialize the append-only log into ONE immutable in-memory sequence
    of live events (D-01, D-02).

    Phase 10's snapshot contract needs every derived claim -- objective
    state, trend row, weight, recommendation, cap decision -- to read the
    same event sequence, so that appending to the log after a render can
    never silently change claims the render already returned. This is that
    single materialization point: it applies the existing compensating-
    retraction filter (`live_events`) exactly once and returns a tuple, so
    a caller that captures twice gets two independent immutable snapshots,
    and appending after capture cannot alter the already-returned one.

    The returned tuple is JSON-native and immutable by construction; marks
    are NOT folded in here (they stay a join the caller performs via
    `marks_by_event`, because a mark is a separate fact about a response).
    This is the one primitive Phase 10's `retention.capture` reads; no
    Phase 10 code opens a second reader, filter, cache, store, or writer.
    """
    return tuple(live_events(log))


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


# ---- marks (01-09) ----------------------------------------------------------
# D-12: the attempt file stops being an editable input, so marking a `short`
# answer moves to a first-class, timestamped event instead of a hand-edited
# `MARK:` line. A mark is a separate fact ABOUT a response, never a mutation
# OF it (T-1-23): the response event's own `score` stays `None` forever, and
# `review_state` is computed at read time from `marks_by_event`, above.


def mark_event(session_id, item_id, item_ref, marks_event, verdict, rubric=None,
                notes="", marker="human", proposal_ref=None):
    """Build one mark event: a timestamped, first-class fact about the
    response event named by `marks_event`, appended alongside it rather
    than mutating it.

    `verdict` is coerced to `bool` -- dichotomous, matching every other
    scored surface in this tool (PARTIAL exists in `GRADING.md`'s procedure
    to describe an answer, never to award half credit). `rubric` is a list
    of `{"point": <the rubric text>, "pass": <bool>}`, defaulting to `[]`.

    `marker` must be `"human"` in this phase: a model verdict is not
    accepted evidence until Phase 8 (TEACH-09) teaches the runtime to hold
    one as pending review instead, so any other value raises `ValueError`
    rather than being recorded as a settled fact (T-1-24).

    `proposal_ref` links this human mark to the exact mark_proposal event it
    accepts (D-14/D-24): it is recorded on the event and folded into the
    dedupe raw string (None encodes as empty), so accepting two different
    proposals for the same response records two distinct human marks rather
    than deduping into one.

    `dedupe_key` is computed over `(session_id, marks_event, verdict, a
    canonical encoding of rubric, proposal_ref)`, so replaying an identical
    batch is idempotent (`append_event` reports `already_recorded`), while a
    genuinely corrected verdict, rubric, or proposal reference -- a
    different tuple -- always records as a new, live mark that
    `marks_by_event` then prefers.
    """
    if marker != "human":
        raise ValueError(
            "mark_event: marker must be 'human' in this phase (got %r); a "
            "model verdict is not accepted evidence until Phase 8 (TEACH-09)"
            % (marker,))
    rubric = [{"point": r["point"], "pass": bool(r["pass"])} for r in (rubric or [])]
    rubric_canon = json.dumps(rubric, ensure_ascii=False, sort_keys=True)
    verdict = bool(verdict)
    raw = "%s|%s|%s|%s|%s" % (session_id, marks_event, verdict, rubric_canon,
                               proposal_ref or "")
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": MARK_EVENT_TYPE,
        "ts": utc_now(),
        "session_id": session_id,
        "item_id": item_id,
        "item_ref": item_ref,
        "marks_event": marks_event,
        "verdict": verdict,
        "rubric": rubric,
        "notes": notes or "",
        "marker": marker,
        "proposal_ref": proposal_ref,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


# ---- renders (01-09) --------------------------------------------------------
# D-11: `_attempts/*.md` and the session JSON stop being inputs and become
# views computed fresh from the log on every call. Neither is ever read back
# in by anything -- `itembank start`/`next`/`submit` still write the session
# file as a sitting's live working state (the cursor `next` advances); the
# functions below are how that state, and the attempt markdown, are
# recovered if the file is lost, not a replacement for it while a sitting is
# still active.

MARK_EVENT_TYPE = "mark"


def session_events(log, session_id):
    """Every LIVE response event for `session_id`, in stable `(ts, log
    order)` order -- the same ordering rule `objective_history()`'s
    fallback path uses (`ORDER BY ts, seq`), so two events sharing an
    identical `ts` keep the order they were appended in rather than an
    order that depends on dict or sort internals. Built on `live_events`,
    never `events`, so a retracted response vanishes from a render exactly
    as it vanishes from a count (D-10) -- reading `events` here instead
    would let a retracted response keep rendering and keep counting.
    """
    rows = []
    for idx, ev in enumerate(live_events(log)):
        if ev.get("event_type") != RESPONSE_EVENT_TYPE:
            continue
        if ev.get("session_id") != session_id:
            continue
        rows.append((ev.get("ts", ""), idx, ev))
    rows.sort(key=lambda r: (r[0], r[1]))
    return [r[2] for r in rows]


def marks_by_event(log):
    """The most recent LIVE `mark` event for every response `event_id` that
    has one, keyed by that response's own `event_id`.

    Most recent rather than first, because a second mark carrying a
    different verdict is a correction, not a duplicate (D-12); live,
    because a retracted mark leaves the response pending again, the same
    way a retracted response leaves an attempt open again (T-1-23). Marks
    are appended to the log in the order they are recorded, so simply
    keeping the last one seen while walking `live_events` in log order IS
    the most recent live one. Nothing here mutates the response event
    itself -- `review_state` is computed at read time by every caller of
    this function, never written back onto the response.
    """
    marks = {}
    for ev in live_events(log):
        if ev.get("event_type") != MARK_EVENT_TYPE:
            continue
        target = ev.get("marks_event")
        if target:
            marks[target] = ev
    return marks


# ---- hint events and teaching outcomes (06-01) -----------------------------
# D-15/D-16: every response records the highest tier actually shown using
# null-versus-zero semantics, and every newly shown hint is its own
# append-only event linked to the response/attempt state that authorized it.
# Reports derive tier/attempt/stumped/reveal outcomes from these live events
# and never trust a mutable counter.

HINT_EVENT_TYPE = "hint"


def hint_event(session_id, q, tier_index, available, tier_name, source,
               unlock_path, response_event_id=None, response_canonical=None,
               attempt_num=None, bank=None, ts=None):
    """Build one hint event: a first-class, timestamped fact that a fixed
    authored tier was shown, linked to the response/attempt that authorized
    it (D-16). `unlock_path` is `attempt` or `stumped`; `source` is
    `authored` in this phase (generated/model hints are Phase 8).

    The dedupe key covers (session, item, tier, unlock path), so showing the
    same tier through the same path twice is idempotent, while a stumped
    unlock and an attempt unlock of the same tier are two distinct events.
    """
    if source != "authored":
        raise ValueError("hint_event: source must be 'authored' in this phase "
                         "(got %r); generated hints are Phase 8" % (source,))
    if unlock_path not in ("attempt", "stumped"):
        raise ValueError("hint_event: unlock_path must be 'attempt' or "
                         "'stumped', got %r" % (unlock_path,))
    key = evidence_key(q)
    canon = response_canonical if response_canonical is not None else ""
    raw = "%s|%s|%s|%d|%s" % (session_id, key, unlock_path, tier_index, canon)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": HINT_EVENT_TYPE,
        "ts": ts or utc_now(),
        "session_id": session_id,
        "item_id": q.get("item_id", ""),
        "item_ref": q["id"],
        "item_type": q["type"],
        "bank": os.path.basename(bank) if bank else None,
        "mode": q.get("mode"),
        "attempt_number": attempt_num,
        "response_event_id": response_event_id,
        "response_canonical": canon,
        "tier_index": tier_index,
        "tier_name": tier_name,
        "available": available,
        "source": source,
        "unlock_path": unlock_path,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


def hint_events(log, session_id, item_key=None):
    """Every LIVE hint event for `session_id` (optionally one item), in log
    order. Built on `live_events`, never `events`, so a retracted hint
    vanishes exactly as it vanishes from a report (D-10/D-16)."""
    return [ev for ev in live_events(log)
            if ev.get("event_type") == HINT_EVENT_TYPE
            and ev.get("session_id") == session_id
            and (item_key is None
                 or evidence_key({"item_id": ev.get("item_id", ""),
                                  "id": ev.get("item_ref", "")}) == item_key)]


def teaching_outcomes(log, session_id):
    """Derive per-item teaching outcomes (D-17, TEACH-03) from live response,
    hint, and mark events -- never from a mutable counter and never from the
    session's teaching_state.

    Returns {"schema_version": REPORT_VERSION, "session_id": session_id,
    "teaching_outcomes": {item_key: row}}. Each row carries first_try_correct,
    correct_after_attempts (total attempts to the first correct response),
    correct_after_tier (same, but a hint had been shown), stumped_at_tier,
    revealed, hints_used (live hint events), highest_tier (highest tier shown
    or None), and one of the D-17 outcome labels: first_try_correct,
    correct_after_attempts, correct_after_tier, accepted_mark,
    marked_incorrect, revealed, stumped, pending, or unresolved. A settled
    mark is never `pending`: `pending` means no human has ruled yet, and both
    verdicts end that state. A stumped action never counts as a wrong
    response; a retracted event never counts at all.
    """
    resp_by_item = {}
    hint_by_item = {}
    marks = {}
    for ev in live_events(log):
        if ev.get("session_id") != session_id:
            continue
        et = ev.get("event_type")
        key = evidence_key({"item_id": ev.get("item_id", ""),
                            "id": ev.get("item_ref", "")})
        if et == RESPONSE_EVENT_TYPE:
            resp_by_item.setdefault(key, []).append(ev)
        elif et == HINT_EVENT_TYPE:
            hint_by_item.setdefault(key, []).append(ev)
        elif et == MARK_EVENT_TYPE:
            marks[ev.get("marks_event")] = ev

    rows = {}
    for key, resps in resp_by_item.items():
        hints = hint_by_item.get(key, [])
        hints_used = len(hints)
        highest = max((h["tier_index"] for h in hints
                       if isinstance(h.get("tier_index"), int)), default=None)
        stumped = min((h["tier_index"] for h in hints
                       if h.get("unlock_path") == "stumped"
                       and isinstance(h.get("tier_index"), int)), default=None)
        revealed = any(h.get("tier_index") == 5 for h in hints)
        first = resps[0]
        first_try_correct = first.get("score") is True
        correct = next((r for r in resps if r.get("score") is True), None)
        correct_after = len(resps) if correct is not None else None
        if correct is not None and hints_used:
            outcome = "correct_after_tier"
        elif correct is not None:
            outcome = "first_try_correct" if first_try_correct \
                else "correct_after_attempts"
        elif revealed:
            outcome = "revealed"
        elif stumped is not None:
            outcome = "stumped"
        elif any(resp.get("score") is None
                 and marks.get(resp.get("event_id"), {}).get("verdict") is True
                 for resp in resps):
            outcome = "accepted_mark"
        elif any(resp.get("score") is None
                 and marks.get(resp.get("event_id"), {}).get("verdict") is False
                 for resp in resps):
            # A failed mark is SETTLED, not outstanding. Until 2026-08-24 this
            # branch did not exist and a `fail` verdict fell through to
            # `pending`, which is the label for an item no human has looked at
            # yet. The marker's own work therefore disappeared from the report
            # that marker reads, and the honest reading of the row was "still
            # to do". Found by the 13.9 sitting, where q8 was marked fail and
            # the report went on claiming one pending manual mark.
            outcome = "marked_incorrect"
        elif any(resp.get("score") is None for resp in resps):
            outcome = "pending"
        else:
            outcome = "unresolved"
        rows[key] = {
            "item_id": first.get("item_id", ""),
            "item_ref": first.get("item_ref", ""),
            "outcome": outcome,
            "first_try_correct": first_try_correct,
            "correct_after_attempts": correct_after,
            "correct_after_tier": correct_after if hints_used else None,
            "stumped_at_tier": stumped,
            "revealed": revealed,
            "hints_used": hints_used,
            "highest_tier": highest,
        }
    # An item whose every response was retracted has no live record at all:
    # it must not contribute a counted row (D-10) -- but an item with a live
    # response and no correct answer is `unresolved`, which is a real,
    # counted outcome.
    return {"schema_version": REPORT_VERSION,
            "session_id": session_id,
            "teaching_outcomes": rows}


def render_attempt_md(log, session_id, qs, bank_path):
    """The attempt markdown for one session, computed fresh from the log
    every time this is called (D-11) -- never read back in as an input by
    anything. Same document shape `surfaces/quiz.attempt_markdown` produces
    today (title, status line, one section per item, the short-item rubric
    block), with two deliberate differences, both consequences of this
    being a render: the provenance line says the file is generated from the
    evidence log and names the session, and the `MARK:` line reports the
    recorded state read through `marks_by_event` instead of accepting a
    hand edit.

    `qs` is the parsed bank (`model.load(bank_path)`'s return value); a
    response event carries only `item_ref`/`item_id`, never the item text
    itself, so the stem, options and rubric are looked up in `qs` by
    `item_ref`. `runtime.response_text(q, answer)` is reused for the
    auto-scored answer line rather than reimplemented, which is what keeps
    this render readable by whoever comes back to mark it: it records
    option *text*, not a letter that a reshuffled page would reassign to a
    different option next time (see that function's own docstring).

    This function has no access to a session's original item selection or
    cursor -- that lives only in the session JSON, which a render
    deliberately never reads (D-11). So unlike the file this replaces, it
    cannot say whether a sitting is "finished"; it reports exactly what has
    been recorded and nothing about what has not yet been served.
    """
    events_ = session_events(log, session_id)
    marks = marks_by_event(log)
    by_ref = {}
    for q in qs:
        by_ref.setdefault(q["id"], q)

    auto = [ev for ev in events_ if ev.get("score") is not None]
    correct = sum(1 for ev in auto if ev.get("score") is True)
    shorts = [ev for ev in events_ if ev.get("item_type") == "short"]
    pending_shorts = [ev for ev in shorts if ev["event_id"] not in marks]

    L = []
    L.append("# Attempt: %s" % os.path.basename(bank_path))
    L.append("")
    L.append("*Generated from the evidence log for session `%s`. Bank: `%s`. "
             "Editing this file changes nothing: it is rebuilt from "
             "`_evidence/evidence.jsonl` every time `itembank render attempt` "
             "runs.*" % (session_id, bank_path))
    L.append("")
    L.append("**Status:** %d response(s) recorded, %d auto-marked, %d correct. "
             "%d short answer(s) awaiting a marker."
             % (len(events_), len(auto), correct, len(pending_shorts)))
    L.append("")
    L.append("**To grade this:** see `GRADING.md`. Record each verdict with "
             "`itembank mark --session %s ...` -- a batch marks many answers "
             "in one call, and a mark is a timestamped event, never a line "
             "edited in this file." % session_id)
    L.append("")
    for ev in events_:
        q = by_ref.get(ev.get("item_ref"))
        L.append("---")
        L.append("")
        head = "## Item %s, %s" % (q.get("number") if q else "?", ev.get("item_type", "?"))
        score = ev.get("score")
        if score is True:
            head += "  [auto: correct]"
        elif score is False:
            head += "  [auto: WRONG]"
        L.append(head)
        objective = ev.get("objective") or ""
        if objective:
            L.append("")
            L.append("*Objective: %s*" % objective)
        L.append("")
        stem = q["stem"] if q else "(this item no longer resolves against the given bank)"
        L.append("**Q.** %s" % stem.replace("\n", " "))
        L.append("")
        if ev.get("item_type") == "short":
            L.append("**Answer, verbatim:**")
            L.append("")
            L.append("```")
            L.append(str(ev.get("answer") or "") or "(left blank)")
            L.append("```")
            L.append("")
            model_text = ((q.get("model", "") if q else "") or "")
            if model_text:
                L.append("**Model answer (from the bank, not the learner's):** %s" %
                         model_text.replace("\n", " "))
                L.append("")
            rubric = ((q.get("rubric") or []) if q else [])
            mark = marks.get(ev["event_id"])
            if rubric:
                L.append("**Rubric:**")
                L.append("")
                mark_by_point = {}
                if mark:
                    for r in mark.get("rubric") or []:
                        mark_by_point[r.get("point")] = r.get("pass")
                for point in rubric:
                    if mark and point in mark_by_point:
                        state = "(pass)" if mark_by_point[point] else "(fail)"
                    else:
                        state = "(unmarked)"
                    L.append("- %s %s" % (state, point))
                L.append("")
            if mark:
                verdict_text = "PASS" if mark.get("verdict") else "FAIL"
                notes = mark.get("notes") or ""
                L.append("MARK: %s -- marked by %s at %s%s" %
                         (verdict_text, mark.get("marker", "human"), mark.get("ts", ""),
                          (": " + notes) if notes else ""))
            else:
                L.append("MARK: pending -- run `itembank mark --session %s --item %s "
                         "--verdict pass|fail` to record a verdict" %
                         (session_id, ev.get("item_ref")))
        elif ev.get("item_type") == "check":
            # The evidence answer for a check item is the results vector;
            # the learner's own source lives in check_source. Render the
            # source so a marker or later reader sees what was written
            # (plan 05-07), bounded by response_text's line cap -- the
            # full text is always in the log's check_source.
            L.append("**Source, submitted:**")
            L.append("")
            L.append("```")
            L.append(response_text(q, ev.get("check_source")) if q
                     else str(ev.get("check_source") or ""))
            L.append("```")
            L.append("")
            L.append("**Result vector:** %s" % (ev.get("answer") or "(none)"))
        else:
            answer_val = response_text(q, ev.get("answer")) if q else ""
            L.append("**Selected:** %s" % (answer_val or "(nothing)"))
        L.append("")
    return "\n".join(L)


def render_session_json(log, session_id, qs, bank_path):
    """Reconstruct the session dict shape `surfaces/session.py` writes,
    from `session_events(log, session_id)` alone (D-11).

    This is a VIEW: `itembank start` still writes the session JSON as a
    sitting's live working state -- the cursor `next` advances, and the
    mode/objective/seed a fresh `submit` reads. This function is how that
    state is recovered if the file is lost, not a replacement for it while
    a sitting is active. Two consequences of building this from the log
    alone, stated rather than silently guessed at:

    - `seed` is never recorded in any response event -- only the session
      file itself ever held it -- so a recovered session always reports 0.
    - `items`/`cursor`/`status` describe exactly the items this
      reconstruction can see (every distinct `item_ref` with a live
      response), not the session's original selection, which is unknowable
      without the session file. `status` is therefore "complete" whenever
      there is at least one response and "active" when there are none, by
      construction rather than by comparing against an item count this
      function has no way to see.

    Each response record also carries an additive `review_state`
    ("n/a"/"pending"/"marked"), read through `marks_by_event` the same way
    `render_attempt_md`'s `MARK:` line is -- so a mark is visible from this
    view too, without ever mutating the response event it describes.
    """
    events_ = session_events(log, session_id)
    marks = marks_by_event(log)
    index_by_ref = {}
    for i, q in enumerate(qs):
        index_by_ref.setdefault(q["id"], i)

    items = []
    responses = []
    modes = []
    objectives = []
    for ev in events_:
        ref = ev.get("item_ref")
        idx = index_by_ref.get(ref)
        if idx is not None and idx not in items:
            items.append(idx)
        item_type = ev.get("item_type")
        if item_type != "short":
            review_state = "n/a"
        elif ev.get("event_id") in marks:
            review_state = "marked"
        else:
            review_state = "pending"
        responses.append({
            "item_id": ref,
            "objective": ev.get("objective") or "",
            "type": item_type,
            "answer": ev.get("answer"),
            "score": ev.get("score"),
            "status": "recorded",
            "review_state": review_state,
        })
        modes.append(ev.get("mode"))
        objectives.append(ev.get("objective") or "")

    mode = modes[0] if modes else "diagnostic"
    objective = (objectives[0] if objectives and all(o == objectives[0] for o in objectives)
                else "")

    return {
        "schema_version": SESSION_VERSION,
        "session_id": session_id,
        "bank": os.path.abspath(bank_path),
        "items": items,
        "cursor": len(items),
        "responses": responses,
        "status": "complete" if events_ else "active",
        "mode": mode,
        "objective": objective,
        "seed": 0,
        # The v2 session contract (Phase 6) requires teaching_state; a
        # recovered view cannot know tiers that were never recorded, so it
        # reports the honest empty state rather than fabricating one.
        "teaching_state": {},
    }


# ---- day ticks (01-10) -------------------------------------------------------
# EVID-03's third and last legacy store: `daily_log.md` stops being written
# directly and becomes a render, exactly as the attempt markdown and the
# session JSON already did in plan 01-09. Only the TICKS become events here --
# the streak/pacing computation (`day_streak`, `lane_behind`, `lane_load`)
# stays in `surfaces/day.py`, reading the rebuilt `{iso_date: set_of_lanes}`
# mapping the same way it always has, per this plan's own narrow reading of
# CONTEXT.md's deferred item (see 01-10-PLAN.md's Flagged Assumptions).

DAY_TICK_EVENT_TYPE = "day_tick"

_DAY_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def day_tick_event(date, lane, source="day"):
    """Build one day_tick event: `lane` marked done on `date`, appended
    rather than mutating `daily_log.md` in place -- D-11 extended to the
    third of the three legacy stores EVID-03 names.

    `date` must be `YYYY-MM-DD` AND a real calendar date; anything else
    raises `ValueError` rather than becoming a silently wrong row in the
    regenerated table (T-1-27) -- the same defensive posture
    `retraction_event()`'s empty-reason check already takes for an
    unexplained undo.

    `dedupe_key` is a hash over `(date, lane)` alone, deliberately not
    `source` or a timestamp: ticking the same lane on the same date twice
    -- from the day POST route, from a future CLI, on the same session or a
    different one -- must record once and report `already_recorded`.
    """
    if not isinstance(date, str) or not _DAY_DATE_RE.match(date):
        raise ValueError(
            "day_tick_event: date must be YYYY-MM-DD, got %r" % (date,))
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        raise ValueError(
            "day_tick_event: date must be a real calendar date, got %r" % (date,))
    if not lane:
        raise ValueError("day_tick_event: lane must be a non-empty string")
    raw = "%s|%s" % (date, lane)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": DAY_TICK_EVENT_TYPE,
        "ts": utc_now(),
        "date": date,
        "lane": lane,
        "source": source,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


TERM_LOOKUP_EVENT_TYPE = "term_lookup"


def term_lookup_event(session_id, bank, term_slug, mode, source,
                      ts=None, actor="learner"):
    """Build one term_lookup event: a learner looked up a lesson term's
    definition, appended through the one writer like every other fact
    (D-19). It is NOT a response and carries no score key -- structurally,
    not merely by convention: the returned dict has no `score` field at all.

    `source` is the provenance the reader-path/session-path split owns
    (UI-SPEC §8.5): "reader" for a lookup served by the lesson reader's own
    path, "session" for a lookup inside a sitting. It is validated here
    because the log is append-only: an ambiguous provenance cannot be
    corrected later, only superseded.

    `dedupe_key` is a hash over (session_id, bank, term_slug, source, mode),
    so replaying an identical lookup reports `already_recorded` while a
    genuinely different lookup always records.
    """
    if source not in ("reader", "session"):
        raise ValueError(
            "term_lookup_event: source must be 'reader' or 'session', "
            "got %r" % (source,))
    if not term_slug:
        raise ValueError("term_lookup_event: term_slug must be non-empty")
    raw = "%s|%s|%s|%s|%s" % (session_id, bank, term_slug, source, mode)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": TERM_LOOKUP_EVENT_TYPE,
        "ts": ts if ts is not None else utc_now(),
        "session_id": session_id,
        "bank": bank,
        "term_slug": term_slug,
        "mode": mode,
        "source": source,
        "actor": actor,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


KEY_REVIEW_EVENT_TYPE = "key_review"


def key_review_event(session_id, bank, key_id, mode, ts=None, actor="learner"):
    """Build one key_review event: a learner asked to add a [!KEY] card to
    review, appended through the one writer (D-19). It is NOT a response
    and carries no score key -- structurally, not merely by convention.
    Phase 10 replays these events into scheduler state; this plan only
    records them.

    `dedupe_key` is a hash over (session_id, bank, key_id, mode), so
    replaying the same review request reports `already_recorded` while a
    different card or session always records.
    """
    if not key_id:
        raise ValueError("key_review_event: key_id must be non-empty")
    raw = "%s|%s|%s|%s" % (session_id, bank, key_id, mode)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": KEY_REVIEW_EVENT_TYPE,
        "ts": ts if ts is not None else utc_now(),
        "session_id": session_id,
        "bank": bank,
        "key_id": key_id,
        "mode": mode,
        "actor": actor,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


LESSON_COMPLETE_EVENT_TYPE = "lesson_complete"


def lesson_complete_event(session_id, bank, lesson_slug, subject, objectives,
                          zone="UTC", ts=None, actor="learner"):
    """Build one lesson_complete event: a learner explicitly completed a
    named Phase 3 lesson heading, appended through the one writer (SCHED-04,
    D-24). It is the ONLY way a lesson enters the objective review queue --
    no page view, scroll, or model activity can manufacture it (D-24,
    T-10-06), and it is not a response: structurally, it carries no score
    key at all.

    The event names the server/CLI-resolved facts only: the bank's basename
    (never a client-derived path, T-10-07), the Phase 3 `lesson_slug()` of
    the completed heading, the single namespaced subject the referenced
    objectives share, and the sorted unique referenced objectives. Every
    field is validated here because the log is append-only: an ambiguous
    completion cannot be corrected later, only superseded.

    `zone` is the local-day zone the completion's next-review date must be
    derived in (an IANA name, "UTC", or a fixed offset such as "UTC+09:00");
    retention projects the event's `ts` into it. `dedupe_key` hashes
    (bank, lesson_slug, subject, sorted objectives, zone) alone -- NOT a
    timestamp -- so retrying the identical completion is idempotent
    (`append_event` reports `already_recorded`), while a compensating
    retraction (D-10) makes the same completion record again as the next
    live one.
    """
    if not session_id:
        raise ValueError("lesson_complete_event: session_id must be non-empty")
    if not bank or "/" in bank or "\\" in bank or os.sep in bank:
        raise ValueError(
            "lesson_complete_event: bank must be a basename, never a path "
            "(got %r)" % (bank,))
    if not lesson_slug:
        raise ValueError(
            "lesson_complete_event: lesson_slug must be a non-empty Phase 3 "
            "lesson slug")
    objectives = sorted({o for o in (objectives or []) if o})
    if not objectives:
        raise ValueError(
            "lesson_complete_event: objectives must be a non-empty list of "
            "namespaced objectives")
    if any(":" not in o for o in objectives):
        raise ValueError(
            "lesson_complete_event: every referenced objective must be "
            "namespaced (got %r)" % (objectives,))
    if not subject or ":" in subject:
        raise ValueError(
            "lesson_complete_event: subject must be the non-empty namespace "
            "shared by the referenced objectives (got %r)" % (subject,))
    if not zone:
        raise ValueError("lesson_complete_event: zone must be non-empty")
    raw = "%s|%s|%s|%s|%s" % (bank, lesson_slug, subject,
                              json.dumps(objectives, ensure_ascii=False,
                                         sort_keys=True), zone)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": LESSON_COMPLETE_EVENT_TYPE,
        "ts": ts if ts is not None else utc_now(),
        "session_id": session_id,
        "bank": bank,
        "lesson_slug": lesson_slug,
        "subject": subject,
        "objectives": objectives,
        "zone": zone,
        "actor": actor,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


CAP_OVERRIDE_EVENT_TYPE = "cap_override"


def cap_override_event(session_id, bank, subject, local_date, zone,
                       snapshot_id, cap, count, ts=None):
    """Build one cap_override event (plan 10-04, D-08): the audited
    exception that lets one additional per-subject sitting start after the
    daily cap was reached. It is the record of a deliberate, explicit choice
    -- NOT a persistent bypass (no setting, no flag, no standing
    authorization): the event is bound to the one server-generated
    `session_id` it authorizes, and every later cap check ignores it as a
    count while honoring it only for that session's live lifetime.

    Like every non-response event it is structurally scoreless (no `score`
    key at all). All values are server-derived and validated here because
    the log is append-only: `subject` is the non-empty namespace (no colon),
    `local_date` is the local calendar date in `zone`, `snapshot_id` is the
    one snapshot the count was decided on, `cap`/`count` are the exact
    numbers shown to the learner, and `scope` is the constant "sitting".
    `dedupe_key` hashes (session_id, subject, local_date, snapshot_id, cap)
    -- NOT a timestamp -- so retrying the identical confirmed override for
    the same generated session reconciles (`already_recorded`) instead of
    appending a second exception.
    """
    if not session_id:
        raise ValueError("cap_override_event: session_id must be non-empty")
    if not bank or "/" in bank or "\\" in bank or os.sep in bank:
        raise ValueError(
            "cap_override_event: bank must be a basename, never a path "
            "(got %r)" % (bank,))
    if not subject or ":" in subject:
        raise ValueError(
            "cap_override_event: subject must be the non-empty namespace "
            "(got %r)" % (subject,))
    if not local_date:
        raise ValueError("cap_override_event: local_date must be non-empty")
    if not zone:
        raise ValueError("cap_override_event: zone must be non-empty")
    if not snapshot_id:
        raise ValueError("cap_override_event: snapshot_id must be non-empty")
    if not isinstance(cap, int) or isinstance(cap, bool) or cap < 1:
        raise ValueError("cap_override_event: cap must be a positive integer "
                         "(got %r)" % (cap,))
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("cap_override_event: count must be a non-negative "
                         "integer (got %r)" % (count,))
    raw = "%s|%s|%s|%s|%s" % (session_id, subject, local_date, snapshot_id,
                               cap)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": CAP_OVERRIDE_EVENT_TYPE,
        "ts": ts if ts is not None else utc_now(),
        "session_id": session_id,
        "bank": bank,
        "subject": subject,
        "local_date": local_date,
        "zone": zone,
        "snapshot_id": snapshot_id,
        "cap": cap,
        "count": count,
        "scope": "sitting",
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


# ---- model interactions (08-03) --------------------------------------------
# D-12/D-15/D-16: every attempted model interaction -- a generated hint or a
# rubric review -- is one durable, append-only evidence fact carrying the
# backend/profile, operation, timing, request/output fingerprints, outcome,
# gate result, and permitted tier. A dropped candidate stores descriptors
# only: raw dropped text is never written, so no normal retrieval path can
# re-expose it (T-08-21).

MODEL_INTERACTION_EVENT_TYPE = "model_interaction"


def model_interaction_event(session_id, bank, item_ref, operation, interaction_id,
                            outcome, gate_reason, permitted_tier, backend_class,
                            profile, request_fingerprint, response_fingerprint,
                            elapsed_ms, output_bytes, pass_payload=None,
                            parent_interaction_id=None, ts=None):
    """Build one model_interaction event: a first-class, timestamped fact
    that one model generation was attempted (D-12/D-15).

    `operation` is `hint` or `rubric_review`; `outcome` is `pass`, `drop`,
    or `unavailable` (D-08); `backend_class` is `hosted` or `local` (D-17);
    `gate_reason` carries plan 08-01's machine-readable reason code (e.g.
    `gate.ambiguous`) or None. `pass_payload` is stored only when `outcome`
    is `pass` -- a dropped or unavailable candidate never leaves its text in
    evidence (D-16). The returned dict carries no `score` key at all,
    structurally mirroring term_lookup/key_review: an interaction is a fact
    about the model, never accepted evidence about the learner.

    `dedupe_key` is a hash over (session_id, interaction_id), so at most one
    generation is recorded per interaction id (D-12): appending the same
    interaction twice reports `already_recorded`. An explicit retry is a NEW
    interaction id whose `parent_interaction_id` names the original, keeping
    cost and repeated failures visible without reusing the dedupe key.
    """
    if not interaction_id:
        raise ValueError("model_interaction_event: interaction_id must be "
                         "non-empty")
    if operation not in ("hint", "rubric_review"):
        raise ValueError("model_interaction_event: operation must be 'hint' "
                         "or 'rubric_review', got %r" % (operation,))
    if outcome not in ("pass", "drop", "unavailable"):
        raise ValueError("model_interaction_event: outcome must be 'pass', "
                         "'drop' or 'unavailable', got %r" % (outcome,))
    if backend_class not in ("hosted", "local"):
        raise ValueError("model_interaction_event: backend_class must be "
                         "'hosted' or 'local', got %r" % (backend_class,))
    payload = pass_payload if outcome == "pass" else None
    raw = "%s|%s" % (session_id, interaction_id)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": MODEL_INTERACTION_EVENT_TYPE,
        "ts": ts if ts is not None else utc_now(),
        "session_id": session_id,
        "bank": bank,
        "item_ref": item_ref,
        "operation": operation,
        "interaction_id": interaction_id,
        "outcome": outcome,
        "gate_reason": gate_reason,
        "permitted_tier": permitted_tier,
        "backend_class": backend_class,
        "profile": profile,
        "request_fingerprint": request_fingerprint,
        "response_fingerprint": response_fingerprint,
        "elapsed_ms": elapsed_ms,
        "output_bytes": output_bytes,
        "pass_payload": payload,
        "parent_interaction_id": parent_interaction_id,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


def model_interactions(log, session_id):
    """Every LIVE model_interaction event for `session_id`, in log order.

    Reads through `live_events`, never `events`, so a retracted interaction
    vanishes from a report exactly as it vanishes from a count (D-10).
    Reports and the CLI query this one shape instead of each re-filtering
    `events()` themselves (08-03).
    """
    return [ev for ev in live_events(log)
            if ev.get("event_type") == MODEL_INTERACTION_EVENT_TYPE
            and ev.get("session_id") == session_id]


# ---- mark proposals (08-03) -------------------------------------------------
# D-13/D-14/D-23: a rubric-review outcome is a per-point pass|fail|uncertain
# pending suggestion linked to the genuine short-answer response event and to
# the interaction that produced it. A proposal is structurally incapable of
# settling a mark: it carries no score key and no verdict field, and the
# settled-mark readers (marks_by_event, the review_state derivation) filter
# on the mark event type only (T-08-20).

MARK_PROPOSAL_EVENT_TYPE = "mark_proposal"


def mark_proposal_event(session_id, bank, item_id, item_ref, response_event_id,
                        interaction_id, points, ts=None):
    """Build one mark_proposal event: a first-class, timestamped pending
    suggestion for the response event named by `response_event_id`, produced
    by the model interaction named by `interaction_id` (D-13).

    `points` is a list of per-point suggestions, each carrying `point_index`
    (a non-negative integer), `status` (pass, fail, or uncertain), and a
    `rationale` bounded at 240 characters. An empty `points` array is valid
    and reads back as pending/unknown, never a default pass (D-22).

    The returned dict carries no `score` key and no `verdict` field --
    structurally, not merely by convention: a proposal can never be mistaken
    for the settled mark that only a human's `mark_event(marker="human",
    proposal_ref=...)` creates (D-14/D-23).

    `dedupe_key` is a hash over (session_id, response_event_id,
    interaction_id), so one proposal per response-interaction pair is
    structural: a second identical proposal reports `already_recorded`.
    """
    if not response_event_id:
        raise ValueError("mark_proposal_event: response_event_id must be "
                         "non-empty")
    if not interaction_id:
        raise ValueError("mark_proposal_event: interaction_id must be "
                         "non-empty")
    out_points = []
    for i, p in enumerate(points or []):
        point_index = p.get("point_index")
        status = p.get("status")
        rationale = p.get("rationale", "")
        if (not isinstance(point_index, int) or isinstance(point_index, bool)
                or point_index < 0):
            raise ValueError(
                "mark_proposal_event: point %d point_index must be a "
                "non-negative integer, got %r" % (i, point_index))
        if status not in ("pass", "fail", "uncertain"):
            raise ValueError(
                "mark_proposal_event: point %d status must be 'pass', 'fail' "
                "or 'uncertain', got %r" % (i, status))
        if not isinstance(rationale, str) or len(rationale) > 240:
            raise ValueError(
                "mark_proposal_event: point %d rationale must be a string of "
                "at most 240 characters" % (i,))
        out_points.append({"point_index": point_index, "status": status,
                           "rationale": rationale})
    raw = "%s|%s|%s" % (session_id, response_event_id, interaction_id)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": MARK_PROPOSAL_EVENT_TYPE,
        "ts": ts if ts is not None else utc_now(),
        "session_id": session_id,
        "bank": bank,
        "item_id": item_id,
        "item_ref": item_ref,
        "response_event_id": response_event_id,
        "interaction_id": interaction_id,
        "points": out_points,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


def proposals_for(log, session_id, response_event_id=None):
    """Every LIVE mark_proposal event for `session_id`, optionally filtered
    to one response event, in log order.

    Reads through `live_events`, never `events` (post-retraction discipline,
    D-10): a retracted proposal disappears from this reader as it does from
    a count. A proposal this reader still returns has never been accepted --
    `proposal_summary` derives its pending state, and only a human's
    `mark_event(marker="human", proposal_ref=...)` settles it (D-22).
    """
    return [ev for ev in live_events(log)
            if ev.get("event_type") == MARK_PROPOSAL_EVENT_TYPE
            and ev.get("session_id") == session_id
            and (response_event_id is None
                 or ev.get("response_event_id") == response_event_id)]


def proposal_summary(proposal):
    """Derive {points, pass_count, uncertain_count, pending} from a
    mark_proposal event's N per-point statuses -- a pure read-time
    derivation that never stores a fractional score anywhere (D-24). A
    "4 of 5" style count is computed here, at read time, from the statuses
    alone.

    `pending` is True when any point is `uncertain` or the points array is
    empty -- a suggestion with open points stays pending until a human
    decides (D-22). An unaccepted proposal stays pending forever; this
    function never fabricates a default pass (D-25).
    """
    pts = proposal.get("points") or []
    pass_count = sum(1 for p in pts if p.get("status") == "pass")
    uncertain_count = sum(1 for p in pts if p.get("status") == "uncertain")
    return {
        "points": len(pts),
        "pass_count": pass_count,
        "uncertain_count": uncertain_count,
        "pending": len(pts) == 0 or uncertain_count > 0,
    }


def day_log_from_events(log):
    """The `{iso_date: set_of_lanes}` mapping `surfaces/day.load_day_log()`
    returns, built from the live `day_tick` events instead of the markdown
    table (D-11 extended to the day surface's tick log).

    Un-ticking a lane is a retraction of its tick event (D-10): reading
    through `live_events` means a retracted tick simply is not present,
    with no un-tick-specific code needed here at all.
    """
    out = {}
    for ev in live_events(log):
        if ev.get("event_type") != DAY_TICK_EVENT_TYPE:
            continue
        date, lane = ev.get("date"), ev.get("lane")
        if not date or not lane:
            continue
        out.setdefault(date, set()).add(lane)
    return out


def render_daily_log(log, lanes, floor_lanes, status_fn):
    """The `daily_log.md` markdown table, computed fresh from `log` (the
    mapping `day_log_from_events()` returns) rather than read back in as an
    input by anything (D-11) -- byte-for-byte the same structure
    `surfaces/day.write_day_log()` produces for the same tick mapping:
    heading, provenance line, the floor/full explanation, the header row,
    and one row per date with `x`/`.` marks and a day-status column.

    Takes the lane list, the floor list and the status function as
    parameters rather than importing them from `surfaces/day.py` -- the
    runtime tier must not import a surface, the same boundary
    `runtime.py`'s own docstring holds for scoring, applied here to what a
    lane means. Passing them keeps this module unaware of that.
    """
    L = ["# Daily log", "",
         "*Written by `itembank day`. One row per day, `x` where the lane was done.*", "",
         "**Floor** = %s, the smallest day that still counts. **Full** = every lane. "
         "A missed day is never made up; the next day runs its own row at normal size."
         % ", ".join(floor_lanes), "",
         "| Date | " + " | ".join(lanes) + " | Day |",
         "|---" * (len(lanes) + 2) + "|"]
    for iso in sorted(log):
        marks = ["x" if l in log[iso] else "." for l in lanes]
        L.append("| %s | %s | %s |" % (iso, " | ".join(marks), status_fn(log[iso])))
    L.append("")
    return "\n".join(L)
