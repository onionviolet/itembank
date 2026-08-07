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


def do_start(bank_path, count, objective, mode, seed, out, force):
    # A non-positive count is rejected outright rather than handed to the
    # slice below: Python's slice semantics treat a negative stop index as
    # "up to but excluding the last |count| elements," so count=-1 would
    # otherwise silently produce nearly the entire bank instead of erroring
    # on the obviously-invalid input. Checked here, not per-caller, so both
    # the CLI's --count and /api/start's count field get the same guard.
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        sys.exit("count must be a positive integer, got %r" % (count,))
    qs = load(bank_path)
    errors, _ = lint(qs)
    if errors and not force:
        sys.exit("refusing to start a bank with errors; run lint or pass --force")
    import random, uuid
    candidates = [i for i, q in enumerate(qs) if not objective or q.get("objective") == objective]
    if not candidates:
        sys.exit("no items match objective %r" % objective)
    rng = random.Random(seed)
    rng.shuffle(candidates)
    items = candidates[:min(count, len(candidates))]
    out = out or os.path.join(os.path.dirname(os.path.abspath(bank_path)) or ".", "_attempts",
                              "session_%s.json" % uuid.uuid4().hex[:12])
    data = {"schema_version": SESSION_VERSION, "session_id": uuid.uuid4().hex,
            "bank": os.path.abspath(bank_path), "items": items, "cursor": 0,
            "responses": [], "status": "active", "mode": mode,
            "objective": objective or "", "seed": seed,
            "served_ts": evidence.utc_now()}
    write_session(out, data)
    result = session_view(data, qs)
    result["session_file"] = session_path(out)
    return result


def cmd_start(a):
    result = do_start(a.bank, a.count, a.objective, a.mode, a.seed, a.out, a.force)
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
