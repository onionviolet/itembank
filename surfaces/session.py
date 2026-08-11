"""The JSON session surface: the canonical agent-facing client of the runtime.

An agent drives a sitting through these four commands and never scrapes HTML or
reimplements scoring. Everything they print is JSON on stdout.

`start`, `next` and `submit` are also the first callers of `evidence.py`'s
writer: every submitted response is recorded as one event in
`_evidence/evidence.jsonl`, beside the bank, through `evidence.append_event()`
alone (D-08). The session JSON stays the resumability mechanism it always was;
it stops being a source of record in a later plan, not here.

Each command body is split into two functions: `do_start`/`do_next`/
`do_submit`/`do_report` compute and return a dict, and `cmd_start`/`cmd_next`/
`cmd_submit`/`cmd_report` unpack an argparse Namespace, call the matching
`do_*`, print its result and return 0. These bodies now run in two very
different places -- as a CLI process, where `sys.exit()` on a routine error
condition is the correct way to report it, and inside a long-lived shared
daemon, where it is not. Every `do_*` function keeps raising `SystemExit` on
exactly the conditions it always has, with the same message text, because
that is still correct for the CLI; containing it is the daemon's job
(`surfaces/daemon.py`'s `/api/*` handlers), not this module's.
"""
import datetime, json, os, re, sys

import evidence
import retention
import runner
import selection
import subjects
from model import lint, load
from surfaces import settings
from runtime import (INTERACTION_VERSION, REPORT_VERSION, SESSION_VERSION,
                     VISUAL_ACTIONS, VISUAL_PROTOCOL_VERSION,
                     VISUAL_TOLERANCE_POLICY_VERSION, canonical_visual_response,
                     explain_payload, interaction_result, invoke_hint,
                     invoke_rubric_review, normalize_answer, public_item,
                     read_session, reconcile_teaching_state, score_response,
                     session_path, session_summary, session_view, teaching_key,
                     teaching_transition, visual_observation as runtime_visual_observation,
                     visual_state_in_domain, write_session)


# Phase 6 renderer handoff (06-02, D-12): the only thing a served client may
# send beyond the Phase 6 action envelope is one short opaque renderer
# identification string. It is validated here and discarded before policy,
# persistence, evidence, response, or logs.
RENDERER_META_MAX_BYTES = 256

# Phase 10 (10-04, D-07/D-08): the exact locked UI copy for a cap block
# (10-UI-SPEC.md "Cap block") and the explicit confirmation phrase the
# one-sitting override requires. The override is a deliberate, audited,
# sitting-scoped exception -- there is deliberately NO persistent "ignore
# the cap" setting anywhere in the codebase.
CAP_BLOCK_COPY = ("Today\u2019s {subject} cap is reached "
                  "({count} of {cap} ordinary attempts).")
OVERRIDE_CONFIRMATION = "start one additional sitting"


def ms_since(ts):
    """Milliseconds between an ISO-8601 UTC timestamp and now, or `None` when
    `ts` is absent or unparseable — a session written before `served_ts`
    existed degrades to an honest null rather than a fabricated number.
    """
    if not ts:
        return None
    try:
        served = datetime.datetime.strptime(
            ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return None
    now = datetime.datetime.now(datetime.timezone.utc)
    # Floored at zero, matching the client-side JS's
    # Math.max(0, Math.round(performance.now() - shownAt)) (surfaces/quiz_page.py,
    # T-1-25): a wall-clock delta -- not a monotonic one -- can go negative
    # under an NTP correction or a manual clock change between served_ts
    # being written and this being computed, and evidence.py's own
    # response_time_ms invariant is non-negative.
    return max(0, int((now - served).total_seconds() * 1000))


def _load_history_and_settings(bank_path):
    """Shared by `do_start` and `do_select`: the bank-scoped evidence snapshot
    (read once, D-09), the cooldown/decay settings, and the evidence source
    label -- so both surfaces converge on one history read."""
    log = evidence.log_path(
        os.path.dirname(os.path.abspath(bank_path)) or ".")
    history = []
    evidence_source = "none"
    try:
        if os.path.exists(log):
            history = evidence.objective_history(
                log, "", bank=os.path.basename(bank_path))
            try:
                stale, _ = evidence.index_stale(
                    log, evidence.index_for_log(log))
                evidence_source = "fallback" if stale else "index"
            except Exception:
                evidence_source = "fallback"
    except Exception:
        history = []
    from surfaces import settings as _settings
    cooldown, decay, cfg = 20, 0.2, {}
    try:
        cfg = _settings.load_settings(
            os.path.dirname(os.path.abspath(bank_path)) or ".")
        cooldown = (cfg.get("selection") or {}).get("cooldown_responses", 20)
        decay = (cfg.get("selection_weights") or {}).get("recency_decay", 0.2)
    except Exception:
        pass
    return log, history, evidence_source, cooldown, decay, cfg


def _retention_context(log, cfg):
    """The Phase 10 selector context (10-03, D-01/D-02/D-12): derived from
    ONE capture of the live append-only log -- the snapshot claim plus the
    bounded normalized objective-weight map from `retention.py`. The previous
    map that caps per-snapshot weight movement comes from the most recent
    live selection event's own recorded weights, so there is no weight file
    or mutable cache (D-02). `retention.py` chooses no items and writes no
    evidence; this function only derives what the sole selector consumes.

    The full snapshot is returned under `_snapshot` so the same capture
    supplies the cap decision (10-04): start and the day surface never
    capture twice for the same render. The local-day boundary is the
    snapshot's own zone, UTC by default.
    """
    events = evidence.capture_events(log) if os.path.exists(log) else ()
    snapshot = retention.capture(events, cfg=cfg)
    previous = None
    for ev in reversed(events):
        if ev.get("event_type") != evidence.SELECTION_EVENT_TYPE:
            continue
        recorded = (ev.get("retention") or {}).get("objective_weights") or {}
        prev = {}
        for obj, entry in recorded.items():
            if isinstance(entry, dict) and \
                    isinstance(entry.get("weight"), (int, float)) and \
                    not isinstance(entry.get("weight"), bool):
                prev[obj] = entry["weight"]
        if prev:
            previous = prev
        break
    summaries = retention.objective_summaries(snapshot)
    weights = retention.objective_weights(summaries, snapshot,
                                          previous=previous)
    return {"snapshot": snapshot["claim"], "_snapshot": snapshot,
            "objective_weights": weights}


def _derive_subject(spec):
    """The server-side subject derivation for the daily cap (10-04,
    T-10-14): the authoritative namespace is the selection spec's objective
    (evidence.subject_of) -- the Phase 7 authored objective namespace. The
    CLI's local `--subject` flag may name the same namespace but may never
    override or contradict it; a client-forged subject is rejected. The key
    is consumed here and never reaches `selection.select`, whose SPEC_FIELDS
    allowlist refuses unknown authority fields.

    The cap is a per-subject measurement, so an objective with NO namespace
    yields an empty subject and therefore no cap gate and no binding --
    the cap is opt-in per namespace (the linter already warns on
    unnamespaced objectives). A CLI `--subject` on an unnamespaced bank
    still names the gate, but unnamespaced responses never increment it.
    """
    subject = spec.pop("subject", None)
    if not isinstance(subject, str) or not subject:
        subject = None
    objective = spec.get("objective") or ""
    ns = evidence.subject_of(objective)
    if ns:
        if subject is not None and subject != ns:
            sys.exit("subject %r does not match the objective namespace %r; "
                     "the cap subject is derived from the objective, never "
                     "accepted from a caller" % (subject, ns))
        return ns
    return subject or ""


def do_start(bank_path, spec, mode, out, force, *, override_token=None,
             profile_id=None):
    # The D-09 focus pin is a session-level concern, not a selection filter:
    # it rides inside the spec dict so the signature stays the same for every
    # caller, and it is consumed here before the spec reaches `select()`,
    # which refuses fields it does not know.
    focus = spec.get("focus")
    sel_spec = {k: v for k, v in spec.items() if k != "focus"}
    qs = load(bank_path)
    errors, _ = lint(qs)
    if errors and not force:
        sys.exit("refusing to start a bank with errors; run lint or pass --force")
    import uuid
    log, history, evidence_source, cooldown, decay, cfg = \
        _load_history_and_settings(bank_path)
    # The cap subject is consumed from the raw spec BEFORE `expand_spec`
    # validates it: `subject` is a session-level authority field, not a
    # selection filter, so it is popped here and never reaches the selector
    # (whose SPEC_FIELDS allowlist refuses it).
    subject = _derive_subject(sel_spec)
    # Client-forged authority fields are refused by name (T-10-14): the cap,
    # the snapshot and any override marker are server-derived, never read
    # from a spec.
    for forged in ("cap", "snapshot_id", "override"):
        if forged in sel_spec:
            sys.exit("refusing %r in a start spec: the cap, snapshot and "
                     "override are derived from captured evidence, never "
                     "accepted from a caller" % forged)
    sel_spec = selection.expand_spec(cfg, sel_spec)
    ctx = _retention_context(log, cfg)
    snapshot = ctx["_snapshot"]
    cap = cfg.get("daily_cap")
    decision = retention.cap_decision(snapshot, subject=subject, cap=cap)

    # The audited one-sitting override (D-08): BEFORE anything is written,
    # the exact explicit confirmation phrase is required, the subject must
    # actually be at cap, and the override event is appended through the ONE
    # writer, bound to a freshly generated session id. A wrong token, a
    # forged override, or a cancelled confirmation exits here and writes
    # nothing -- there is no persistent cap-disable setting anywhere.
    override = None
    if override_token is not None:
        if override_token != OVERRIDE_CONFIRMATION:
            sys.exit("refusing override: the confirmation phrase must be "
                     "exactly %r" % OVERRIDE_CONFIRMATION)
        if not subject:
            sys.exit("refusing override: a subject is required (pass "
                     "--subject or a namespaced --objective)")
        if not decision["blocked"]:
            sys.exit("refusing override: %s is not at today's cap (%d of %s); "
                     "no exception is needed" %
                     (subject, decision["count"], decision["cap"]))
        override_session_id = uuid.uuid4().hex
        override_event = evidence.cap_override_event(
            override_session_id, os.path.basename(bank_path), subject,
            decision["local_day"], decision["zone"], decision["snapshot_id"],
            decision["cap"], decision["count"])
        appended = evidence.append_event(
            evidence.log_path(
                os.path.dirname(os.path.abspath(bank_path)) or "."),
            override_event)
        if appended["status"] != "recorded":
            sys.exit("refusing override: the override event could not be "
                     "recorded (%s)" % appended["status"])
        override = {"event_id": override_event["event_id"],
                    "session_id": override_session_id}
        # The override authorizes exactly this generated session. Because
        # the event is bound to it and every cap check counts only response
        # events, the exception can never outlive the sitting nor reduce a
        # later count (D-08).
        cap_authorized = True
    else:
        cap_authorized = False

    if decision["blocked"] and not cap_authorized:
        sys.exit(CAP_BLOCK_COPY.format(subject=subject, count=decision["count"],
                                       cap=decision["cap"]))
    # Below cap, ordinary selection is limited to the remaining capacity:
    # a sitting can never be binged past the cap by asking for more items
    # than remain (D-07).
    if not cap_authorized and decision["remaining"] is not None:
        sel_spec["count"] = max(1, min(sel_spec.get("count",
                                                    selection.DEFAULT_COUNT),
                                       decision["remaining"]))
    elif cap_authorized and cap is not None:
        # A confirmed override is ONE additional sitting: it is still
        # bounded to at most one cap's worth of items, so the exception can
        # never become an unbounded binge either (D-07/D-08).
        sel_spec["count"] = max(1, min(sel_spec.get("count",
                                                    selection.DEFAULT_COUNT),
                                       cap))
    items, trace = selection.select(
        qs, sel_spec, history=history, cooldown=cooldown, decay=decay,
        retention_context={k: v for k, v in ctx.items() if k != "_snapshot"})
    trace["evidence"] = {"log": log, "responses": len(history),
                         "source": evidence_source}
    # Phase 9 (D-01/D-04): resolve the subject profile from the items actually
    # selected into this sitting, and persist the complete snapshot with the
    # session. One unambiguous namespaced subject selects its registry entry
    # from validated settings; unknown/unnamespaced sittings get the
    # conservative default; a sitting whose selected items span several
    # namespaces (no objective filter) and disallowed item types refuse here,
    # before any session or evidence file exists. An explicit `profile_id`
    # (plan 09-05, threaded from the CLI `--subject-profile` flag and the
    # served `/api/start` `profile` field) wins over every inference: only
    # the id crosses a client boundary, the selector resolves it once
    # server-side, and the complete snapshot is persisted with the session.
    try:
        subject_snapshot = subjects.select_profile(
            items, subjects.load_registry(
                os.path.dirname(os.path.abspath(bank_path)) or "."),
            explicit_id=profile_id)
    except subjects.SubjectProfileError as exc:
        sys.exit(str(exc))
    index = {q["id"]: i for i, q in enumerate(qs)}
    items = [index[q["id"]] for q in items]
    # D-09 pin support: an optional item id (the `#<id>` fragment a lesson
    # backlink carries) moves that item to the front of the sitting, the served
    # analogue of the file-open client's fragment reorder. An unknown id
    # degrades to the normal order -- the same fallback the file client uses.
    if focus:
        hit = next((i for i, q in enumerate(qs) if q.get("id") == focus), None)
        if hit is not None:
            items = [i for i in items if i != hit]
            items.insert(0, hit)
            items = items[:sel_spec.get("count", selection.DEFAULT_COUNT)]
    out = out or os.path.join(os.path.dirname(os.path.abspath(bank_path)) or ".", "_attempts",
                              "session_%s.json" % uuid.uuid4().hex[:12])
    session_id = override["session_id"] if override else uuid.uuid4().hex
    data = {"schema_version": SESSION_VERSION, "session_id": session_id,
            "bank": os.path.abspath(bank_path), "items": items, "cursor": 0,
            "responses": [], "status": "active", "mode": mode,
            "objective": sel_spec.get("objective") or "",
            "seed": sel_spec.get("seed", 0),
            "served_ts": evidence.utc_now(),
            "teaching_state": {},
            "selection_mode": sel_spec.get("selection_mode", "practice"),
            "subject_profile": subject_snapshot,
            # D-01 (10-03): the sitting's retention binding -- the one
            # snapshot id every claim in this sitting references plus the
            # public bounded normalized weight map the selector consumed.
            # Weights only here; the full component trace lives in the
            # selection evidence event, never duplicated as session authority.
            "retention": {
                "snapshot_id": ctx["snapshot"]["snapshot_id"],
                "objective_weights": {
                    obj: {"weight": entry["weight"]}
                    for obj, entry in ctx["objective_weights"].items()},
                # 10-04: the per-subject cap binding this sitting was
                # authorized under -- server-derived numbers only, never a
                # client value (T-10-14). `override_event_id` is null for an
                # ordinary sitting and the audited event id for the one
                # one-sitting exception.
                "cap": {
                    "subject": subject,
                    "count": decision["count"],
                    "cap": decision["cap"],
                    "local_day": decision["local_day"],
                    "zone": decision["zone"],
                    "snapshot_id": decision["snapshot_id"],
                    "override_event_id": (override or {}).get("event_id"),
                }}}
    write_session(out, data)
    # D-03: one `selection` event per sitting, appended only after the
    # session file was written, through the one evidence writer -- a session
    # that failed to write leaves no orphan claim in the log, and the record
    # of what was asked survives the session file being deleted. The event
    # carries the sitting's full retention evidence claim (snapshot id, the
    # bounded weight map with named components, and the component trace).
    evidence.append_event(
        evidence.log_path(os.path.dirname(os.path.abspath(bank_path)) or "."),
        evidence.selection_event(
            data["session_id"], os.path.basename(bank_path), sel_spec,
            [evidence.evidence_key(qs[i]) for i in items],
            retention={
                "snapshot_id": ctx["snapshot"]["snapshot_id"],
                "objective_weights": ctx["objective_weights"],
                "trace": trace.get("retention")}))
    result = session_view(data, qs)
    result["session_file"] = session_path(out)
    result["cap"] = data["retention"]["cap"]
    result["trace"] = trace
    return result


def do_select(bank_path, spec, force):
    """Preview a selection: same load/lint/history as `do_start`, returns
    `public_item()` payloads plus the trace, writes no session file and
    appends no evidence event -- a preview that recorded itself would poison
    the very cooldown history it is previewing."""
    qs = load(bank_path)
    errors, _ = lint(qs)
    if errors and not force:
        sys.exit("refusing to select from a bank with errors; run lint or "
                 "pass --force")
    log, history, evidence_source, cooldown, decay, cfg = \
        _load_history_and_settings(bank_path)
    spec = selection.expand_spec(cfg, spec)
    ctx = _retention_context(log, cfg)
    items, trace = selection.select(
        qs, spec, history=history, cooldown=cooldown, decay=decay,
        retention_context={k: v for k, v in ctx.items() if k != "_snapshot"})
    trace["evidence"] = {"log": log, "responses": len(history),
                         "source": evidence_source}
    return {"schema_version": 1, "bank": os.path.basename(bank_path),
            "spec": trace["spec"],
            "items": [public_item(q) for q in items],
            "trace": trace}


def cmd_start(a):
    spec = {}
    for key in ("objective", "prerequisite", "type", "difficulty",
                "selection_mode", "seed", "count", "pair", "profile",
                "subject"):
        value = getattr(a, key, None)
        if value is not None:
            spec[key] = value
    if getattr(a, "prereq_satisfied", None):
        spec["prereq_satisfied"] = True
    if getattr(a, "exclude", None):
        spec["exclude_item_ids"] = list(a.exclude)
    override_token = getattr(a, "override_cap", None) or None
    result = do_start(a.bank, spec, a.mode, a.out, a.force,
                      override_token=override_token,
                      profile_id=getattr(a, "subject_profile", None))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_override(a):
    """The CLI twin of POST /api/override (10-04): the same
    `do_start(..., override_token=...)` runtime call the route serves, so the
    command and the route can never disagree about what a confirmed
    one-sitting override is. The exact confirmation phrase is mandatory; a
    wrong or missing one is rejected and writes nothing."""
    spec = {}
    for key in ("objective", "type", "difficulty", "selection_mode", "seed",
                "count", "pair", "profile", "subject"):
        value = getattr(a, key, None)
        if value is not None:
            spec[key] = value
    if getattr(a, "prereq_satisfied", None):
        spec["prereq_satisfied"] = True
    result = do_start(a.bank, spec, a.mode, a.out, a.force,
                      override_token=a.confirm)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def do_next(session_file):
    data = read_session(session_file)
    qs = load(data["bank"])
    # `next` starts writing the session here: the clock for response_time_ms
    # starts the moment an item is handed over, not the moment it is
    # answered, so a learner who reads an item for a while has that time
    # honestly recorded rather than silently discarded.
    data["served_ts"] = evidence.utc_now()
    write_session(session_file, data)
    return session_view(data, qs)


def cmd_next(a):
    result = do_next(a.session)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


UNKNOWN_LANGUAGE_COPY = (
    "This item requests the '%s' language, which isn't enabled in this "
    "itembank's settings (check.languages). Add it in settings, or ask "
    "whoever set up this bank to fix its [LANG:] value.")


def run_check_source(q, source, base):
    """The one shared runner gate for a [TYPE: check] item (plan 05-03 Task 2,
    D-14): execute the submitted source once per authored case with
    settings-derived bounds, reduce the per-case pass flags to a results
    vector, and score that vector through runtime.score_response -- the one
    scorer. Returns (run_result, vector, score).

    Shared by the browser route (surfaces/quiz.py:record_answer) and this
    module's do_action, so both submit paths reach the scorer through exactly
    one implementation rather than two copies of the gate. The bounds come
    from settings (check.timeout_seconds / max_output_bytes / languages),
    loaded only because callers reach this only for a check item.
    """
    cfg = settings.load_settings(base)
    check = cfg.get("check") or {}
    run_result = runner.run_cases(
        q, source,
        timeout_seconds=check.get("timeout_seconds",
                                  runner.DEFAULT_TIMEOUT_SECONDS),
        max_output_bytes=check.get("max_output_bytes",
                                   runner.DEFAULT_MAX_OUTPUT_BYTES),
        languages=check.get("languages"))
    vector = ",".join("1" if c["passed"] else "0" for c in run_result)
    score = score_response(q, run_result)
    return run_result, vector, score


def do_submit(session_file, answer, confidence):
    """Compatibility wrapper: the CLI/legacy submit path becomes a Phase 6
    submit action over the one session adapter."""
    return do_action(session_file, {"kind": "submit", "answer": answer},
                     confidence=confidence)


ACTION_ID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def do_interact(session_file, action):
    """The ONE interaction mutation path for a visual item (plan 06.1-02
    Task 3, D-04/D-05): commit one semantic state-changing action and append
    exactly one `visual_action` evidence event.

    `action` is the exact five-field request `{"interaction_version",
    "action_id", "action_type", "state"}` (the session is resolved
    server-side from `session_file`). Everything else -- item identity,
    before-state, observation fields, and Phase-6 hint entitlement -- is
    derived here or by the runtime, never accepted from the client. Final
    submit remains the ordinary response event and is never duplicated as a
    visual action.

    Returns {"status": "recorded"|"already_recorded"|"conflict"|"refused",
    ...} -- a duplicate action id/action/state replays with
    `already_recorded`, reusing an action id with different action/state is a
    `conflict`, and nonvisual sessions, stale versions, unknown actions,
    malformed/out-of-domain state, and completed sessions are named refusals.
    """
    data = read_session(session_file)
    if data["status"] != "active":
        sys.exit("session is already complete")
    qs = load(data["bank"])
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
        write_session(session_file, data)
        sys.exit("session is already complete")
    q = qs[data["items"][data["cursor"]]]
    if q["type"] != "visual":
        sys.exit("current item is not a visual item; interact applies only "
                 "to visual assessments")

    if not isinstance(action, dict):
        sys.exit("interact action must be an object")
    # The five-field request (D-05); anything else is refused by name.
    allowed = {"interaction_version", "action_id", "action_type", "state"}
    unknown = set(action) - allowed
    if unknown:
        sys.exit("interact carries unknown field(s): %s"
                 % ", ".join(sorted(unknown)))
    interaction_version = action.get("interaction_version")
    action_id = action.get("action_id")
    action_type = action.get("action_type")
    state = action.get("state")
    if interaction_version != VISUAL_PROTOCOL_VERSION:
        sys.exit("interaction_version %r is not the current visual protocol "
                 "version %d" % (interaction_version, VISUAL_PROTOCOL_VERSION))
    if not isinstance(action_id, str) or not ACTION_ID_RE.match(action_id):
        sys.exit("action_id must be a lowercase canonical UUID-v4 string")
    if action_type not in VISUAL_ACTIONS:
        sys.exit("unknown action_type %r (protocol %d supports %s)"
                 % (action_type, VISUAL_PROTOCOL_VERSION,
                    ", ".join(VISUAL_ACTIONS)))

    # The committed semantic state is canonicalized and validated by the
    # runtime grammar -- never trusted raw (T-06.1-06).
    after_state = canonical_visual_response(q, state)
    if after_state is None:
        sys.exit("state is not a valid canonical semantic response for this "
                 "item")
    if not visual_state_in_domain(q, after_state):
        sys.exit("state is outside the authored domain")
    before_state = None
    log = evidence.log_path(os.path.dirname(data["bank"]))
    item_key = evidence.evidence_key(q)
    trail = evidence.visual_actions(log, data["session_id"], item_id=item_key)
    if trail:
        before_state = trail[-1].get("after_state")

    # Phase-6 hint entitlement: the highest tier already permitted for this
    # item's teaching state -- never raised by the client (D-06).
    live = [ev for ev in evidence.live_events(log)
            if ev.get("session_id") == data["session_id"]
            and evidence.evidence_key({"item_id": ev.get("item_id", ""),
                                       "id": ev.get("item_ref", "")}) == item_key]
    rec = reconcile_teaching_state(data, q, {item_key: live}) \
        .get("teaching_state", {}).get(item_key)
    hint_tier = rec["highest_tier_shown"] if rec \
        and rec["highest_tier_shown"] >= 0 else None

    verdict = None
    observation = runtime_visual_observation(
        q, after_state, verdict, hint_tier=hint_tier)

    event = evidence.visual_action_event(
        data["session_id"], q, VISUAL_PROTOCOL_VERSION, action_id, action_type,
        before_state, after_state, observation["error_category"],
        observation["invariants"], observation["feedback_anchor"], hint_tier,
        os.path.basename(data["bank"]), mode=data.get("mode"))
    written = evidence.append_event(log, event)
    if written["status"] == "already_recorded":
        # Same dedupe identity (session, item, version, action id). Whether
        # this is a benign replay or an id conflict is decided by comparing
        # the stored event's action/state with the request.
        existing = next((ev for ev in evidence.visual_actions(
            log, data["session_id"], item_id=item_key)
            if ev.get("action_id") == action_id), None)
        if existing is not None and (
                existing.get("action_type") != action_type
                or existing.get("after_state") != after_state):
            return {"status": "conflict", "item_id": q["id"],
                    "action_id": action_id,
                    "reason": "action id reused with different action/state",
                    "evidence": written}
        return {"status": "already_recorded", "item_id": q["id"],
                "action_id": action_id,
                "observation": _action_observation(existing or event),
                "evidence": written}
    return {"status": "recorded", "item_id": q["id"], "action_id": action_id,
            "action_type": action_type, "before_state": before_state,
            "after_state": after_state, "observation": observation,
            "hint_tier": hint_tier, "evidence": written}


def _action_observation(event):
    """The bounded observation projection for a replayed action event: the
    same fields a fresh commit returns, read back from evidence -- never
    recomputed or client-supplied."""
    return {
        "submitted": event.get("after_state"),
        "error_category": event.get("error_category"),
        "invariants": event.get("invariants") or [],
        "feedback_anchor": event.get("feedback_anchor"),
        "hint_tier": event.get("hint_tier"),
        "tolerance_policy_version": VISUAL_TOLERANCE_POLICY_VERSION,
    }


def do_hint(session_file, retry=False, stumped=None):
    """Request one error-specific hint through the runtime orchestration
    (plan 08-04): `runtime.invoke_hint` sequences adapter -> gate -> evidence
    -> authored fallback, so the surface never touches a tier, profile, key,
    or marker.

    `stumped` is the daemon's legacy keyword: the daemon's Phase 6
    `/api/hint` still calls this function with `stumped` (True/False), and
    until plan 08-05 rewires that route those calls must keep revealing the
    next fixed authored tier through `do_action` -- the sentinel value None
    (the CLI path) selects the model orchestration, a real bool selects the
    Phase 6 reveal. The quiz page's "I'm stumped" control depends on this."""
    if stumped is not None:
        return do_action(session_file, {"kind": "stumped" if stumped else "hint"})
    return invoke_hint(session_file, retry=retry)


def _validate_renderer_meta(renderer_meta):
    """The renderer handoff gate: absent or one opaque UTF-8 string of at
    most 256 bytes. Anything else is refused before any policy work; the
    accepted value is discarded by the caller, never persisted."""
    if renderer_meta is None:
        return
    if not isinstance(renderer_meta, str):
        sys.exit("renderer_meta must be a string or absent")
    if len(renderer_meta.encode("utf-8")) > RENDERER_META_MAX_BYTES:
        sys.exit("renderer_meta must be at most %d UTF-8 bytes"
                 % RENDERER_META_MAX_BYTES)


def do_action(session_file, action, confidence=None, renderer_meta=None,
              elapsed_ms=None):
    """The ONE session adapter for every sitting action (D-01/D-02): it
    loads/upgrades the session and bank, resolves the current item, reads
    live response/hint/mark evidence, reconciles teaching state, invokes
    `runtime.teaching_transition`, appends the response and/or hint event
    through `evidence.append_event`, applies only returned cursor/status/
    teaching-state changes, and atomically writes the session after evidence
    is durable. No surface reimplements policy; no renderer/observation
    parameter reaches the runtime transition.
    """
    _validate_renderer_meta(renderer_meta)     # discarded before policy
    data = read_session(session_file)
    if data["status"] != "active":
        sys.exit("session is already complete")
    qs = load(data["bank"])
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
        write_session(session_file, data)
        sys.exit("session is already complete")
    q = qs[data["items"][data["cursor"]]]

    # Phase 9 (D-04): a legacy session whose null profile slot was never
    # filled resolves once from the bank and persists the snapshot with this
    # action; every later action consumes only the stored snapshot, never a
    # re-resolution of the bank or current settings. The resolution uses the
    # session's own item list, matching do_start.
    if data.get("subject_profile") is None:
        data["subject_profile"] = subjects.select_profile(
            [qs[i] for i in data["items"]],
            subjects.load_registry(os.path.dirname(data["bank"])))

    log = evidence.log_path(os.path.dirname(data["bank"]))
    item_key = evidence.evidence_key(q)
    # The pure evidence fold for crash-window repair: rebuild this item's
    # teaching state from live events before the transition sees it.
    live = [ev for ev in evidence.live_events(log)
            if ev.get("session_id") == data["session_id"]
            and evidence.evidence_key({"item_id": ev.get("item_id", ""),
                                       "id": ev.get("item_ref", "")}) == item_key]
    evidence_state = {item_key: live}
    data = reconcile_teaching_state(data, q, evidence_state)
    rec = data["teaching_state"].get(item_key)

    # A check item's submitted answer is source text; the runner executes it
    # once per authored case and the per-case result list is what every
    # scoring call from here on receives (plan 05-01, D-01). The raw source
    # is kept for the evidence event and the normalized result.
    run_result = None
    check_source = None
    check_vector = None
    check_score = None
    if q["type"] == "check":
        source = normalize_answer(action.get("answer"))
        if not isinstance(source, str):
            sys.exit("a check item requires source text as its answer")
        check_source = source
        try:
            run_result, check_vector, check_score = run_check_source(
                q, source, os.path.dirname(os.path.abspath(data["bank"])))
        except runner.UnknownLanguage:
            sys.exit(UNKNOWN_LANGUAGE_COPY % (q.get("lang") or "python"))
        action = dict(action, answer=run_result)

    result = teaching_transition(data, q, action)
    action_name = result["action"]
    next_data = result["session"]
    accepted = True
    recorded_event = None

    if action.get("kind") == "submit":
        if q["type"] == "check":
            score = check_score
            vector = check_vector
            canon = evidence.idempotency_canon(q, vector)
            event_answer = vector
        else:
            answer = normalize_answer(action.get("answer"))
            score = score_response(q, answer)
            canon = evidence.idempotency_canon(q, answer)
            event_answer = answer
        killed = bool(run_result) and any(c.get("timed_out") for c in run_result)
        # 10-04 cap recheck (D-07/D-08): before a GENUINE new response is
        # appended, the live local-day count for the sitting's bound subject
        # is re-captured from the log. A replay of the same canonical answer
        # is not a new ordinary attempt (it would dedupe to
        # already_recorded), so it is never blocked and never double-counts;
        # a genuinely different answer beyond the cap is blocked with the
        # exact locked copy. This is what makes a long sitting unable to run
        # past the cap and a crash-retry unable to double-count (T-10-14).
        cap_binding = (data.get("retention") or {}).get("cap") or {}
        bound_subject = cap_binding.get("subject") or ""
        if bound_subject and data["status"] == "active":
            # A replay of the SAME canonical answer is not a new ordinary
            # attempt (it would dedupe to already_recorded), so it is never
            # blocked and never double-counts. Any live canonical for this
            # item counts -- not just the last event, because a hint event
            # or an interleaved answer can sit after the response in the
            # session's live stream.
            is_replay = any(ev.get("canonical") == canon for ev in live)
            if not is_replay:
                live_now = evidence.capture_events(
                    log) if os.path.exists(log) else ()
                snap = retention.capture(live_now, cfg={})
                cap_check = retention.cap_decision(
                    snap, subject=bound_subject,
                    cap=cap_binding.get("cap"))
                override_active = any(
                    ev.get("event_type") == evidence.CAP_OVERRIDE_EVENT_TYPE
                    and ev.get("session_id") == data["session_id"]
                    for ev in live_now)
                if cap_check["blocked"] and not override_active:
                    sys.exit(CAP_BLOCK_COPY.format(
                        subject=bound_subject, count=cap_check["count"],
                        cap=cap_check["cap"]))
        # The attempt number comes from the live evidence rule
        # (evidence.attempt_number): a replay of the SAME canonical response
        # reproduces the original attempt number -- so append_event dedupes
        # it to already_recorded -- while a genuinely different answer opens
        # the next attempt (D-04/D-17).
        attempt_num = evidence.attempt_number(log, data["session_id"],
                                              item_key, canon)
        event = evidence.response_event(
            data["session_id"], q, event_answer, score, data["mode"], attempt_num,
            os.path.basename(data["bank"]),
            response_time_ms=elapsed_ms if elapsed_ms is not None
            else ms_since(data.get("served_ts")),
            confidence=confidence, hint_tier=result.get("hint_tier"),
            selection_mode=data.get("selection_mode"),
            check_source=check_source,
            interaction_version=INTERACTION_VERSION if q["type"] == "check"
            else None,
            error_category="timeout" if killed else None)
        evidence_result = evidence.append_event(log, event)
        if q["type"] == "check":
            # The normalized result is data for feedback, not a second
            # verdict: the score is the exact score_response return.
            result["interaction_result"] = interaction_result(
                q, check_source, score, run_result)
            result["explain"] = explain_payload(q, True, run_result)
        accepted = evidence_result["status"] == "recorded"
        recorded_event = evidence_result
        if not accepted:
            # A crash-window replay: evidence already has this event. The
            # transition already reconciled the state, so no second unlock or
            # cursor movement happens; report already_recorded.
            next_data["cursor"] = data["cursor"]
            next_data["status"] = data["status"]
        else:
            # The session JSON stays the resumability mechanism it always
            # was; only a genuinely recorded response is appended (an
            # already_recorded replay never double-counts).
            next_data["responses"] = list(next_data.get("responses") or []) + [{
                "item_id": q["id"], "objective": q.get("objective", ""),
                "type": q["type"], "answer": event_answer, "score": score,
                "status": "recorded"}]
    else:
        # hint / stumped
        evidence_result = None
        tier = (result.get("hint") or {}).get("tier")
        if tier is not None and tier.get("index") is not None:
            hint_ev = evidence.hint_event(
                data["session_id"], q, tier["index"], tier.get("available", True),
                tier.get("name", ""), "authored",
                result["hint"].get("unlock_path", "attempt"),
                response_event_id=rec["last_response_event_id"] if rec else None,
                response_canonical=rec["last_genuine_canonical"] if rec else None,
                attempt_num=rec["attempt_count"] if rec else None,
                bank=os.path.basename(data["bank"]))
            evidence_result = evidence.append_event(log, hint_ev)

    next_data["served_ts"] = evidence.utc_now()
    write_session(session_file, next_data)

    if action.get("kind") == "submit":
        ret = {"accepted": accepted, "item_id": q["id"], "score": score,
               "action": action_name, "status": next_data["status"],
               "evidence": recorded_event,
               "hint_tier": result.get("hint_tier"),
               "interaction_result": result.get("interaction_result"),
               "next": session_view(next_data, qs)}
        if q["type"] == "check":
            # The one run's per-case result rides along so a surface can
            # build the explain payload from that exact run (05-05 Task 1).
            # Only a check item carries it; every other type's body is
            # byte-identical to before, asserted by check_roundtrip.
            ret["run_result"] = run_result
        return ret
    return {"accepted": accepted, "item_id": q["id"], "action": action_name,
            "hint": result.get("hint"),
            "status": next_data["status"], "evidence": evidence_result,
            "next": session_view(next_data, qs)}


def do_report(session_file):
    """The report: the session summary joined with live-derived teaching
    outcomes (D-17) and the runtime's diagnostic/exam review availability.
    Never reads a mutable hint counter."""
    data = read_session(session_file)
    log = evidence.log_path(os.path.dirname(data["bank"]))
    outcomes = evidence.teaching_outcomes(log, data["session_id"])
    summary = session_summary(data)
    summary["teaching_outcomes"] = outcomes["teaching_outcomes"]
    return {"schema_version": REPORT_VERSION, "session_id": data["session_id"],
            "status": data["status"], "summary": summary,
            "review_available": {"diagnostic": data["status"] == "complete",
                                 "exam": False}}


def cmd_submit(a):
    result = do_submit(a.session, a.answer, a.confidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_hint(a):
    result = do_hint(a.session, retry=bool(a.retry))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def do_rubric_review(session_file):
    """Request pending per-point rubric suggestions for the current short
    response (plan 08-04 Task 2): `runtime.invoke_rubric_review` sequences
    adapter -> gate -> evidence. Refusals are named with no evidence write,
    and no model path can settle a mark (D-13/D-14/D-25)."""
    return invoke_rubric_review(session_file)


def cmd_rubric_review(a):
    result = do_rubric_review(a.session)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_interact(a):
    """The CLI twin of POST /api/interact: parse `--action JSON` and call the
    same `do_interact` body the route calls, printing the same JSON shape."""
    try:
        action = json.loads(a.action)
    except (TypeError, ValueError) as exc:
        sys.exit("--action must be a JSON object: %s" % exc)
    if not isinstance(action, dict):
        sys.exit("--action must be a JSON object")
    result = do_interact(a.session, action)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def render_suggestion(suggestion_reveal="after-self-mark"):
    """The ONLY surface representation of a model rubric suggestion (D-22):
    a single pending token -- never a number, fraction, check, or cross
    glyph. The suggestion_reveal setting decides WHEN the suggestion is
    disclosed relative to the learner's own mark; whatever the timing, the
    rendered form is the pending token. The per-point pass/fail/uncertain
    statuses live in the evidence proposal event and stay out of any
    learner-facing render until a human settles the proposal."""
    return "pending"


def cmd_report(a):
    result = do_report(a.session)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
