"""The JSON session surface: the canonical agent-facing client of the runtime.

An agent drives a sitting through these four commands and never scrapes HTML or
reimplements scoring. Everything they print is JSON on stdout.
"""
import json, os, sys

from model import lint, load
from runtime import (SESSION_VERSION, normalize_answer, read_session,
                     score_response, session_path, session_summary, session_view,
                     write_session)


def cmd_start(a):
    qs = load(a.bank)
    errors, _ = lint(qs)
    if errors and not a.force:
        sys.exit("refusing to start a bank with errors; run lint or pass --force")
    import random, uuid
    candidates = [i for i, q in enumerate(qs) if not a.objective or q.get("objective") == a.objective]
    if not candidates:
        sys.exit("no items match objective %r" % a.objective)
    rng = random.Random(a.seed)
    rng.shuffle(candidates)
    items = candidates[:min(a.count, len(candidates))]
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.bank)) or ".", "_attempts",
                                "session_%s.json" % uuid.uuid4().hex[:12])
    data = {"schema_version": SESSION_VERSION, "session_id": uuid.uuid4().hex,
            "bank": os.path.abspath(a.bank), "items": items, "cursor": 0,
            "responses": [], "status": "active", "mode": a.mode,
            "objective": a.objective or "", "seed": a.seed}
    write_session(out, data)
    result = session_view(data, qs)
    result["session_file"] = session_path(out)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_next(a):
    data = read_session(a.session)
    qs = load(data["bank"])
    print(json.dumps(session_view(data, qs), ensure_ascii=False, indent=2))
    return 0


def cmd_submit(a):
    data = read_session(a.session)
    if data["status"] != "active":
        sys.exit("session is already complete")
    qs = load(data["bank"])
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
        write_session(a.session, data)
        sys.exit("session is already complete")
    q = qs[data["items"][data["cursor"]]]
    answer = normalize_answer(a.answer)
    score = score_response(q, answer)
    data["responses"].append({"item_id": q["id"], "objective": q.get("objective", ""),
                               "type": q["type"], "answer": answer, "score": score})
    data["cursor"] += 1
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
    write_session(a.session, data)
    result = {"accepted": True, "item_id": q["id"], "score": score,
              "status": data["status"], "next": session_view(data, qs)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_report(a):
    data = read_session(a.session)
    print(json.dumps({"session_id": data["session_id"], "status": data["status"],
                      "summary": session_summary(data)}, ensure_ascii=False, indent=2))
    return 0
