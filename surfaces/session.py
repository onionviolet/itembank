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
import datetime, json, os, sys

import evidence
import selection
from model import lint, load
import runner
from runtime import (INTERACTION_VERSION, REPORT_VERSION, SESSION_VERSION,
                     explain_payload, interaction_result, normalize_answer,
                     read_session, reconcile_teaching_state, score_response,
                     session_path, session_summary, session_view, teaching_key,
                     teaching_transition, write_session, public_item)


# Phase 6 renderer handoff (06-02, D-12): the only thing a served client may
# send beyond the Phase 6 action envelope is one short opaque renderer
# identification string. It is validated here and discarded before policy,
# persistence, evidence, response, or logs.
RENDERER_META_MAX_BYTES = 256


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


def do_start(bank_path, spec, mode, out, force):
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
    sel_spec = selection.expand_spec(cfg, sel_spec)
    items, trace = selection.select(
        qs, sel_spec, history=history, cooldown=cooldown, decay=decay)
    trace["evidence"] = {"log": log, "responses": len(history),
                         "source": evidence_source}
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
    data = {"schema_version": SESSION_VERSION, "session_id": uuid.uuid4().hex,
            "bank": os.path.abspath(bank_path), "items": items, "cursor": 0,
            "responses": [], "status": "active", "mode": mode,
            "objective": sel_spec.get("objective") or "",
            "seed": sel_spec.get("seed", 0),
            "served_ts": evidence.utc_now(),
            "teaching_state": {},
            "selection_mode": sel_spec.get("selection_mode", "practice")}
    write_session(out, data)
    # D-03: one `selection` event per sitting, appended only after the
    # session file was written, through the one evidence writer -- a session
    # that failed to write leaves no orphan claim in the log, and the record
    # of what was asked survives the session file being deleted.
    evidence.append_event(
        evidence.log_path(os.path.dirname(os.path.abspath(bank_path)) or "."),
        evidence.selection_event(
            data["session_id"], os.path.basename(bank_path), sel_spec,
            [evidence.evidence_key(qs[i]) for i in items]))
    result = session_view(data, qs)
    result["session_file"] = session_path(out)
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
    items, trace = selection.select(
        qs, spec, history=history, cooldown=cooldown, decay=decay)
    trace["evidence"] = {"log": log, "responses": len(history),
                         "source": evidence_source}
    return {"schema_version": 1, "bank": os.path.basename(bank_path),
            "spec": trace["spec"],
            "items": [public_item(q) for q in items],
            "trace": trace}


def cmd_start(a):
    spec = {}
    for key in ("objective", "prerequisite", "type", "difficulty",
                "selection_mode", "seed", "count", "pair", "profile"):
        value = getattr(a, key, None)
        if value is not None:
            spec[key] = value
    if getattr(a, "prereq_satisfied", None):
        spec["prereq_satisfied"] = True
    if getattr(a, "exclude", None):
        spec["exclude_item_ids"] = list(a.exclude)
    result = do_start(a.bank, spec, a.mode, a.out, a.force)
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


def do_submit(session_file, answer, confidence):
    """Compatibility wrapper: the CLI/legacy submit path becomes a Phase 6
    submit action over the one session adapter."""
    return do_action(session_file, {"kind": "submit", "answer": answer},
                     confidence=confidence)


def do_hint(session_file, stumped=False):
    """The explicit hint action: reveal exactly one fixed tier, appending a
    hint event when a tier is actually shown (D-05/D-07/D-16)."""
    return do_action(session_file, {"kind": "stumped" if stumped else "hint"})


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
    if q["type"] == "check":
        source = action.get("answer")
        if not isinstance(source, str):
            sys.exit("a check item requires source text as its answer")
        check_source = source
        run_result = runner.run_cases(
            q, source, timeout_seconds=runner.DEFAULT_TIMEOUT_SECONDS,
            max_output_bytes=runner.DEFAULT_MAX_OUTPUT_BYTES)
        action = dict(action, answer=run_result)

    result = teaching_transition(data, q, action)
    action_name = result["action"]
    next_data = result["session"]
    accepted = True
    recorded_event = None

    if action.get("kind") == "submit":
        answer = normalize_answer(action.get("answer"))
        score = score_response(q, answer)
        if q["type"] == "check":
            # The evidence record's answer and canonical are the results
            # vector; the scorer saw the full per-case list so a timed-out
            # run scores None, and dedupe compares the vector exactly as it
            # does for every other type (D-13).
            vector = ",".join("1" if c["passed"] else "0" for c in answer)
            canon = evidence.idempotency_canon(q, vector)
            event_answer = vector
        else:
            canon = evidence.idempotency_canon(q, answer)
            event_answer = answer
        killed = bool(run_result) and any(c.get("timed_out") for c in run_result)
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
        return {"accepted": accepted, "item_id": q["id"], "score": score,
                "action": action_name, "status": next_data["status"],
                "evidence": recorded_event,
                "hint_tier": result.get("hint_tier"),
                "interaction_result": result.get("interaction_result"),
                "next": session_view(next_data, qs)}
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
    result = do_hint(a.session, stumped=bool(a.stumped))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_report(a):
    result = do_report(a.session)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
