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
from runtime import (REPORT_VERSION, SESSION_VERSION, normalize_answer, read_session,
                     score_response, session_path, session_summary, session_view,
                     write_session)


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
    # D-09: the caller reads the bank-scoped evidence snapshot once and
    # passes it in -- selection.py still opens no file. A missing log means
    # no history, never an error (degrade, never block).
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
    cooldown, decay = 20, 0.2
    try:
        cfg = _settings.load_settings(
            os.path.dirname(os.path.abspath(bank_path)) or ".")
        cooldown = (cfg.get("selection") or {}).get("cooldown_responses", 20)
        decay = (cfg.get("selection_weights") or {}).get("recency_decay", 0.2)
    except Exception:
        pass
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


def cmd_start(a):
    spec = {"objective": a.objective, "count": a.count, "seed": a.seed,
            "selection_mode": a.selection_mode}
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
    data = read_session(session_file)
    if data["status"] != "active":
        sys.exit("session is already complete")
    qs = load(data["bank"])
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
        write_session(session_file, data)
        sys.exit("session is already complete")
    q = qs[data["items"][data["cursor"]]]
    answer = normalize_answer(answer)
    score = score_response(q, answer)

    response_time_ms = ms_since(data.get("served_ts"))
    log = evidence.log_path(os.path.dirname(data["bank"]))
    item_key = evidence.evidence_key(q)
    canon = evidence.idempotency_canon(q, answer)
    attempt_num = evidence.attempt_number(log, data["session_id"], item_key, canon)
    event = evidence.response_event(
        data["session_id"], q, answer, score, data["mode"], attempt_num,
        os.path.basename(data["bank"]), response_time_ms=response_time_ms,
        confidence=confidence)
    evidence_result = evidence.append_event(log, event)

    # A retry after a crash between the evidence append and the session
    # write is the session catching up, not a new response: appending a
    # second entry here for the same answer would double-count it in every
    # later report and objective-history summary. The evidence log already
    # has exactly one event for it either way (D-17).
    if evidence_result["status"] == "recorded":
        data["responses"].append({"item_id": q["id"], "objective": q.get("objective", ""),
                                   "type": q["type"], "answer": answer, "score": score,
                                   "status": evidence_result["status"]})

    data["cursor"] += 1
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
    data["served_ts"] = evidence.utc_now()   # next item's clock starts now
    write_session(session_file, data)
    return {"accepted": True, "item_id": q["id"], "score": score,
            "status": data["status"], "evidence": evidence_result,
            "next": session_view(data, qs)}


def cmd_submit(a):
    result = do_submit(a.session, a.answer, a.confidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def do_report(session_file):
    data = read_session(session_file)
    return {"schema_version": REPORT_VERSION, "session_id": data["session_id"],
            "status": data["status"], "summary": session_summary(data)}


def cmd_report(a):
    result = do_report(a.session)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
