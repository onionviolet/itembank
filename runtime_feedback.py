"""Internal runtime component; public access goes through runtime."""
import os


def assessment_feedback_released(mode, session=None):
    """Release silent-mode correctness only from a verified closed sitting."""
    import runtime
    if session and runtime.staged_case(session) is not None:
        return False
    policy = runtime.FEEDBACK_POLICIES.get(mode, runtime.FEEDBACK_POLICIES["practice"])
    return policy["right"] != "defer_feedback" or bool(
        session and session.get("mode") == mode
        and session.get("status") == "complete")


def report_feedback(summary, session):
    """Project a derived report without changing its evidence or session."""
    import runtime
    if runtime.assessment_feedback_released(session.get("mode"), session):
        return summary
    return dict(summary, auto_correct=None, objectives={
        name: dict(row, correct=None)
        for name, row in summary["objectives"].items()})


def staged_event_released(event, session):
    """Resolve each linked event's own case independently of the current case."""
    import runtime
    if not event.get("activity_id"):
        return runtime.assessment_feedback_released(event.get("mode"), session)
    if not session or session.get("session_id") != event.get("session_id") or session.get("mode") != event.get("mode"):
        return False
    case = next((case for case in session.get("staged_cases", [])
                 if case["activity_id"] == event["activity_id"]), None)
    if case is None or case["case_revision"] != event.get("case_revision"):
        return False
    if event.get("child_id") not in case["children"]:
        return False
    index = case["children"].index(event["child_id"])
    if event.get("stage") != case["order"][index]:
        return False
    if not any(row.get("event_id") == event.get("event_id")
               for row in session.get("responses", [])):
        return False
    policy = runtime.FEEDBACK_POLICIES.get(event.get("mode"), runtime.FEEDBACK_POLICIES["practice"])
    if policy["right"] == "defer_feedback":
        return session.get("status") == "complete"
    return session.get("cursor", 0) > case["positions"][-1]


def evidence_feedback(event, session=None):
    """Fail closed when a held event's owning sitting cannot be verified."""
    import runtime
    if runtime.staged_event_released(event, session):
        out = dict(event)
        if "checker_outcomes" in out:
            out["checker_outcomes"] = runtime.polynomial_feedback(out["checker_outcomes"], event.get("hint_tier"))
        return out
    return runtime.submission_feedback(event, "exam")


def saved_check_feedback(event, session, qs, bank_revision):
    """Release a retained current-item run through the existing policy only."""
    import runtime
    from model import content_fingerprint
    if session.get("cursor", 0) >= len(session.get("items", [])):
        return None
    q = qs[session["items"][session["cursor"]]]
    if (session.get("status") != "active" or session.get("mode") != "practice"
            or q.get("type") != "check" or event.get("event_type") != "response"
            or event.get("session_id") != session.get("session_id")
            or event.get("mode") != session.get("mode")
            or event.get("bank") != os.path.basename(session["bank"])
            or event.get("item_ref") != q.get("id")
            or event.get("item_id", "") != q.get("item_id", "")
            or event.get("score") is True
            or not runtime.staged_event_released(event, session)):
        return None
    snapshot = event.get("check_feedback")
    if not isinstance(snapshot, dict) or (
            snapshot.get("bank_revision") != bank_revision
            or snapshot.get("item_revision") != content_fingerprint(q)):
        return None
    result = snapshot.get("interaction_result")
    if (not isinstance(result, dict) or result.get("type") != "check"
            or result.get("version") != runtime.INTERACTION_VERSION
            or result.get("response") != event.get("check_source")
            or result.get("verdict") != event.get("score")
            or not isinstance(result.get("observations"), list)):
        return None
    return {"interaction_result": runtime.evidence_feedback(event, session)["check_feedback"]["interaction_result"],
            "saved_check_feedback": True}


def learner_evidence(events, sessions):
    """Exclude withheld events before deriving learner-facing score summaries."""
    import runtime
    return tuple(event for event in events if runtime.staged_event_released(
        event, sessions.get(event.get("session_id"))))


def submission_feedback(payload, mode):
    """Project a submission response through the runtime's feedback policy.

    Silent sittings release review through the completion/report path, never
    through submission observations. Walk nested adapters and replay envelopes
    too, so moving a feedback field cannot accidentally make it public.
    Durable evidence and session state do not pass through this projection.
    """
    import runtime
    policy = runtime.FEEDBACK_POLICIES.get(mode, runtime.FEEDBACK_POLICIES["practice"])
    if policy["right"] != "defer_feedback":
        return payload
    private = {"score", "verdict", "passed", "expected", "run_result",
               "interaction_result", "observations", "explain", "reveal",
               "selection_feedback", "ordering_diagnostic", "activity_feedback", "input", "actual", "stdout", "stderr",
               "checker_outcomes", "diagnostic_id", "runtime_comparison",
               "exit_code", "timed_out", "truncated"}

    def project(value):
        if isinstance(value, dict):
            return {key: project(child) for key, child in value.items()
                    if key not in private}
        if isinstance(value, (list, tuple)):
            return [project(child) for child in value]
        return value

    return project(payload)


def polynomial_feedback(outcomes, hint_tier=None):
    """Diagnostic identity is teaching content released at the trap tier."""
    import runtime
    return {ident: {key: value for key, value in result.items()
                    if key != "diagnostic_id" or isinstance(hint_tier, int) and hint_tier >= 2}
            for ident, result in outcomes.items()}


def staged_feedback(data, qs, case):
    import runtime
    if data["cursor"] <= case["positions"][-1]:
        return None
    policy = runtime.FEEDBACK_POLICIES.get(data["mode"], runtime.FEEDBACK_POLICIES["practice"])
    if policy["right"] == "defer_feedback" and data["status"] != "complete":
        return None
    return [{"child_id": child, "item_id": qs[data["items"][pos]]["id"],
             "score": next(row["score"] for row in data["responses"]
                           if row["item_id"] == qs[data["items"][pos]]["id"]),
             "explain": runtime.explain_payload(qs[data["items"][pos]], True)}
            for child, pos in zip(case["children"], case["positions"])]


def response_text(q, answer):
    """Human-readable rendering of what the learner actually gave.

    The attempt file records option text, not letters. Letters are reshuffled on
    every page load, so "B" in a saved attempt names a different option the next
    time the same bank is sat, which makes the record unreadable exactly when
    somebody comes back to mark it.
    """
    import runtime
    answer = runtime.normalize_answer(answer)
    t = q["type"]
    if t == "fill":
        if not isinstance(answer, dict):
            return ""
        return "\n".join("%s: %s" % (f["label"], answer.get(f["id"], ""))
                         for f in q["fields"])
    if t == "short":
        return str(answer or "")
    if t in ("mc", "multi"):
        given = answer if isinstance(answer, list) else [answer]
        keys = [str(k).strip().upper() for k in given]
        return "; ".join("%s) %s" % (k, q["opts"][k]) for k in keys if k in q["opts"])
    if t in ("table", "dnd"):
        if isinstance(answer, list):
            answer = dict((str(i), v) for i, v in enumerate(answer))
        if not isinstance(answer, dict):
            return ""
        return "; ".join("%s -> %s" % (r["text"], answer.get(str(r.get("id", i)), "(unassigned)"))
                         for i, r in enumerate(q["rows"]))
    if t == "build":
        return " -> ".join(str(x) for x in answer) if isinstance(answer, list) else ""
    if t == "check":
        # The attempt file records the learner's own source, readable by a
        # marker or a later reader, bounded at a stated line count with a
        # marker when longer -- the full text is always in the evidence log's
        # check_source regardless (plan 05-07).
        lines = str(answer or "").splitlines()
        KEEP = 40
        head = lines[:KEEP]
        if len(lines) > KEEP:
            head.append("... (%d more lines in the evidence log)" % (len(lines) - KEEP))
        return "\n".join(head)
    return ""


def explain_payload(q, reveal=True, run_result=None):
    """Everything the learner may see AFTER responding, and nothing before it.

    Under `serve` this is what the process hands back with the verdict, which is
    what lets the page render a full explanation while never having been sent a
    key it could leak or grade against.
    """
    import runtime
    out = {"answer_text": runtime.answer_text(q), "why": q.get("why", ""),
           # C7 (03.1-03): the syllabus reference and the one-sentence
           # Educational Objective line are answer-adjacent, so both live in
           # the post-verdict payload only -- never public_item().
           "objective": q.get("objective", ""),
           "educational_objective": q.get("objective_line", ""),
           "disc": q.get("disc", ""), "second": q.get("second", ""),
           "trap": q.get("trap", ""), "notes": q.get("notes") or []}
    t = q["type"]
    if t in ("mc", "multi"):
        out["correct"] = q["correct"]
        out["da"] = dict((k, v) for k, v in (q.get("da") or {}).items() if v)
    elif t in ("table", "dnd"):
        out["row_cats"] = dict((str(r.get("id", i)), r["cat"]) for i, r in enumerate(q["rows"]))
    elif t == "build":
        if "ordering" in q:
            example = runtime.ordering_example(q)
            texts = {b["id"]: b["text"] for b in q["blocks"]}
            out["steps"] = [texts[i] for i in example]
            out["answer_text"] = " -> ".join(out["steps"])
            out["ordering"] = q["ordering"]
            out["example_order"] = example
        else:
            out["steps"] = q["steps"]
    elif t == "short":
        # The model answer stays hidden unless asked for, because reading it
        # turns every item after this one into recognition rather than recall.
        out["model"] = q.get("model", "") if reveal else ""
        out["rubric"] = (q.get("rubric") or []) if reveal else []
        if not reveal:
            out["trap"] = ""
            # answer_text for a short IS the model answer; blanking model
            # while leaving it here defeated the blanking.
            out["answer_text"] = ""
    elif t == "check":
        # With `run_result` the per-case actual output and the timed-out /
        # truncated flags are zipped against the authored input and expected
        # halves (the only channel through which actual output can reach the
        # explanation, D-15); without it the authored halves stand alone.
        rows = []
        for i, c in enumerate(q.get("cases") or []):
            row = {
                "case_index": i + 1,
                "input": c.get("call") if q.get("harness") else c.get("stdin", ""),
                "expected": c["expected"],
                "expected_kind": "pattern" if q.get("match") == "regex" else "output",
            }
            if run_result is not None and i < len(run_result):
                rc = run_result[i]
                row["actual"] = rc.get("actual", "")
                row["timed_out"] = bool(rc.get("timed_out"))
                row["truncated"] = bool(rc.get("truncated"))
            rows.append(row)
        out["cases"] = rows
    return out


FEEDBACK_POLICIES = {
    # drill already discloses the full authored reveal on a wrong answer, so
    # a partial disclosure before it would be strictly less than it gets.
    "drill": {"wrong": "advance", "right": "advance", "selection": "none"},
    "practice": {"wrong": "hold", "right": "advance", "selection": "own_picks"},
    # Diagnostic and exam stay silent, which is fidelity to how the real
    # examination behaves: an examinee learns nothing mid-item.
    "diagnostic": {"wrong": "defer_feedback", "right": "defer_feedback",
                   "selection": "none"},
    "exam": {"wrong": "defer_feedback", "right": "defer_feedback",
             "selection": "none"},
    # remediation was not one of the four planned Phase 6 modes, but it ships
    # in the session mode enum; practice's held-retry ladder is the honest
    # teaching behavior for it rather than an unhandled mode.
    "remediation": {"wrong": "hold", "right": "advance",
                    "selection": "own_picks"},
    # paced is the 16D lesson-run checkpoint context (D-PACED-3), reachable
    # only through a paced lesson's checkpoint and never a sitting: the
    # session mode enum does not carry it, exactly as with 'legacy'. Its
    # held-retry shape is practice's; the tier ladder on top of it is
    # checkpoint_feedback's, released by the runtime.
    "paced": {"wrong": "hold", "right": "advance", "selection": "own_picks"},
    # 'legacy' appears only on events migrated from a pre-mode store; a
    # live session can never carry it, and a legacy mode must not pretend to
    # be a policy it never was.
    "legacy": {"wrong": "defer_feedback", "right": "defer_feedback",
               "selection": "none"},
}


def saved_pending_feedback(event, session, qs, settled_marks):
    """Project the recorded pending state without a verdict or keyed content."""
    import runtime
    cursor = session.get("cursor", 0)
    if (session.get("status") != "active" or session.get("mode") in ("exam", "diagnostic")
            or cursor >= len(session.get("items", [])) or runtime.staged_activity(session)):
        return None
    q = qs[session["items"][cursor]]
    if (q.get("type") != "short" or runtime.teaching_key(q) in settled_marks
            or event.get("event_type") != "response" or event.get("item_type") != "short"
            or event.get("session_id") != session.get("session_id")
            or event.get("mode") != session.get("mode")
            or event.get("bank") != os.path.basename(session["bank"])
            or event.get("item_ref") != q.get("id")
            or event.get("item_id", "") != q.get("item_id", "")
            or event.get("objective", "") != q.get("objective", "")
            or "score" not in event or event["score"] is not None):
        return None
    return {"action": "defer_feedback", "score": None}
