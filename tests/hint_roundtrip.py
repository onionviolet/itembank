#!/usr/bin/env python3
"""Phase 6 (06-01/06-02) hint-ladder, cursor-hold and feedback-mode roundtrip.

Direct standard-library roundtrip script in the project's established shape:
`fail(msg)` and a non-zero exit on failure. It drives the pure runtime
teaching transition (plan 06-01 T2), the append-only response/hint evidence
and derived report outcomes (plan 06-01 T3), and, once plan 06-02 lands, the
CLI/API/browser cross-surface equivalence and no-leakage proofs.

The fixture is `fixtures/lesson_bank.md`: q1 is an mc with a lesson pointer,
trap, discriminator and per-option distractor analysis; q2 is a multi; q3 is
a short (pending) item. No real question bank content lives in this test.
"""
import json
import os
import shutil
import sys
import tempfile
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evidence
import model
import runtime
import schema_validate

BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")
SESSION_SCHEMA = os.path.join(ROOT, "schemas", "session.schema.json")
RESPONSE_SCHEMA = os.path.join(ROOT, "schemas", "response.schema.json")
REPORT_SCHEMA = os.path.join(ROOT, "schemas", "report.schema.json")


def fail(msg):
    print("FAIL: %s" % msg)
    sys.exit(1)


def load_schema(path):
    return json.load(open(path, encoding="utf-8"))


def session(mode="practice", items=(0, 1, 2), cursor=0, status="active"):
    """A minimal version-2 session dict over the lesson bank."""
    return {
        "schema_version": runtime.SESSION_VERSION,
        "session_id": uuid.uuid4().hex,
        "bank": os.path.abspath(BANK),
        "items": list(items),
        "cursor": cursor,
        "responses": [],
        "status": status,
        "mode": mode,
        "objective": "",
        "seed": 0,
        "teaching_state": {},
    }


def qs():
    return model.load(BANK)


def q1():
    return qs()[0]


def q2():
    return qs()[1]


def q3():
    return qs()[2]


def item_key(q):
    return evidence.evidence_key(q)


# ---- plan 06-01 Task 2: pure teaching transition --------------------------

def test_transition_rejects_unknown_action():
    s = session()
    try:
        runtime.teaching_transition(s, q1(), {"kind": "skip"})
        fail("teaching_transition accepted an unknown action kind")
    except SystemExit:
        pass
    try:
        runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B", "mode": "drill"})
        fail("teaching_transition accepted a mode-carrying action")
    except SystemExit:
        pass


def test_practice_wrong_holds_and_unlocks_one_tier():
    s = session(mode="practice", items=(0,), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})
    if r["action"] != "hold":
        fail("practice wrong submit must hold, got %r" % r["action"])
    if r["session"]["cursor"] != 0:
        fail("hold must not move the cursor")
    rec = r["session"]["teaching_state"][item_key(q1())]
    if rec["highest_tier_unlocked"] != 0 or rec["highest_tier_shown"] != -1:
        fail("first genuine wrong attempt must unlock tier 0 and show nothing, got %r"
             % (rec["highest_tier_unlocked"], rec["highest_tier_shown"]))
    if r.get("hint_tier") is not None:
        fail("a wrong submit with nothing shown must record hint_tier None, got %r"
             % r.get("hint_tier"))


def test_practice_duplicate_and_empty_unlock_nothing():
    s = session(mode="practice", items=(0,), cursor=0)
    r1 = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})
    s = r1["session"]
    r2 = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})
    if r2["action"] != "hold":
        fail("a canonical-identical replay must hold, got %r" % r2["action"])
    rec = r2["session"]["teaching_state"][item_key(q1())]
    if rec["attempt_count"] != 1 or rec["highest_tier_unlocked"] != 0:
        fail("a duplicate replay must not unlock or count as a new attempt")
    r3 = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": ""})
    if r3["action"] != "hold":
        fail("an empty response must hold, got %r" % r3["action"])
    rec3 = r3["session"]["teaching_state"][item_key(q1())]
    if rec3["attempt_count"] != 1 or rec3["highest_tier_unlocked"] != 0:
        fail("an empty response must not unlock or count as a new attempt")


def test_practice_hint_reveals_one_fixed_tier_in_order():
    s = session(mode="practice", items=(0,), cursor=0)
    s = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})["session"]
    r = runtime.teaching_transition(s, q1(), {"kind": "hint"})
    if r["action"] != "reveal_tier":
        fail("hint must reveal_tier, got %r" % r["action"])
    hint = r["hint"]
    if hint["tier"]["index"] != 0 or hint["unlock_path"] != "attempt":
        fail("first hint must show tier 0 via attempt unlock, got %r" % hint)
    if hint["shown"] != [0]:
        fail("accumulated shown tiers must start at [0], got %r" % hint["shown"])
    s = r["session"]
    r2 = runtime.teaching_transition(s, q1(), {"kind": "hint"})
    if r2["hint"]["tier"]["index"] != 1:
        fail("second hint must show tier 1, got %r" % r2["hint"])
    s = r2["session"]
    r3 = runtime.teaching_transition(s, q1(), {"kind": "hint"})
    if r3["hint"]["tier"]["index"] != 2:
        fail("third hint must show tier 2, got %r" % r3["hint"])


def test_practice_hint_without_attempt_unlocks_tier_zero():
    s = session(mode="practice", items=(0,), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "hint"})
    if r["action"] != "reveal_tier" or r["hint"]["tier"]["index"] != 0:
        fail("hint with no prior attempt must still reveal tier 0, got %r" % r)
    if r["hint"]["unlock_path"] != "attempt":
        fail("hint is always attempt-path even with no prior submit, got %r"
             % r["hint"]["unlock_path"])


def test_practice_stumped_reveals_exactly_next_tier():
    s = session(mode="practice", items=(0,), cursor=0)
    s = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})["session"]
    r = runtime.teaching_transition(s, q1(), {"kind": "stumped"})
    if r["action"] != "reveal_tier":
        fail("stumped must reveal_tier, got %r" % r["action"])
    if r["hint"]["tier"]["index"] != 0 or r["hint"]["unlock_path"] != "stumped":
        fail("stumped must show exactly tier 0 via stumped path, got %r" % r["hint"])
    s = r["session"]
    r2 = runtime.teaching_transition(s, q1(), {"kind": "stumped"})
    if r2["hint"]["tier"]["index"] != 1 or r2["hint"]["unlock_path"] != "stumped":
        fail("second stumped must show exactly tier 1, got %r" % r2["hint"])


def test_practice_correct_retry_advances_and_records_tier():
    s = session(mode="practice", items=(0, 1), cursor=0)
    s = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})["session"]
    s = runtime.teaching_transition(s, q1(), {"kind": "hint"})["session"]
    s = runtime.teaching_transition(s, q1(), {"kind": "hint"})["session"]
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})
    if r["action"] != "advance":
        fail("a correct retry must advance, got %r" % r["action"])
    if r["session"]["cursor"] != 1:
        fail("advance must move the cursor to the next item")
    if r.get("hint_tier") != 1:
        fail("correct retry must record the highest tier shown (1), got %r"
             % r.get("hint_tier"))


def test_practice_changed_answer_opens_new_attempt():
    s = session(mode="practice", items=(0,), cursor=0)
    s = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})["session"]
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "C"})
    if r["action"] != "hold":
        fail("a changed wrong answer must hold, got %r" % r["action"])
    rec = r["session"]["teaching_state"][item_key(q1())]
    if rec["attempt_count"] != 2:
        fail("a materially different response must open attempt 2, got %r"
             % rec["attempt_count"])
    if rec["last_genuine_canonical"] != "C":
        fail("last genuine canonical must follow the latest picked option")


def test_practice_tier_three_is_response_specific():
    s = session(mode="practice", items=(0,), cursor=0)
    s = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})["session"]
    s = runtime.teaching_transition(s, q1(), {"kind": "hint"})["session"]
    s = runtime.teaching_transition(s, q1(), {"kind": "hint"})["session"]
    s = runtime.teaching_transition(s, q1(), {"kind": "hint"})["session"]
    r = runtime.teaching_transition(s, q1(), {"kind": "hint"})
    tier = r["hint"]["tier"]
    if tier["index"] != 3:
        fail("fourth hint must be tier 3 (picked-option rationale), got %r" % tier)
    if not tier["available"]:
        fail("tier 3 must be available for a genuine picked option")
    q = q1()
    canonical = runtime.canonical_response(q, "B")
    expected = (q.get("da") or {}).get("B", "")
    if tier["content"] != expected:
        fail("tier 3 content must be the picked option's analysis, got %r" % tier["content"])
    if r["hint"]["for_response"] != canonical:
        fail("tier 3 must name the canonical response it was resolved for")
    # A changed answer changes the tier-3 content but keeps previously shown tiers.
    s2 = runtime.teaching_transition(
        s, q1(), {"kind": "submit", "answer": "C"})["session"]
    r2 = runtime.teaching_transition(s2, q1(), {"kind": "hint"})
    if r2["hint"]["tier"]["index"] != 3:
        fail("after unlocking tier 3 twice, the next reveal must still be tier 3")
    expected_c = (q.get("da") or {}).get("C", "")
    if r2["hint"]["tier"]["content"] != expected_c:
        fail("tier 3 must track the changed picked option, got %r" % r2["hint"]["tier"])


def test_six_fixed_tiers_and_unavailable_slots():
    names = [runtime.HINT_TIERS[i]["name"] for i in range(6)]
    if names != ["lesson", "objective", "trap", "rationale", "discriminator", "reveal"]:
        fail("the six fixed authored tiers are wrong: %r" % names)
    # q3 is a short item: no picked option, so tier 3 is unavailable but keeps
    # its numbered slot.
    t = runtime.authored_hint(q3(), 3, None)
    if t["index"] != 3 or t["available"]:
        fail("short item tier 3 must be an explicit unavailable slot, got %r" % t)
    # q1 has all authored fields except that reveal content is explain_payload.
    for i in range(6):
        t = runtime.authored_hint(q1(), i, "B")
        if t["index"] != i or not t["available"]:
            fail("q1 tier %d must be available at its fixed slot, got %r" % (i, t))


def test_practice_reveal_then_advance():
    s = session(mode="practice", items=(0, 1), cursor=0)
    s = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})["session"]
    for i in range(6):
        r = runtime.teaching_transition(s, q1(), {"kind": "stumped"})
        if r["hint"]["tier"]["index"] != i:
            fail("stumped ladder must reveal tier %d, got %r" % (i, r["hint"]["tier"]))
        s = r["session"]
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})
    if r["action"] != "advance":
        fail("after the reveal, the next action must advance, got %r" % r["action"])


def test_practice_last_item_completes():
    s = session(mode="practice", items=(0,), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "A"})
    if r["action"] != "complete":
        fail("correct answer on the last item must complete, got %r" % r["action"])
    if r["session"]["status"] != "complete" or r["session"]["cursor"] != 1:
        fail("complete must set status complete and advance past the last item")


def test_drill_reveals_and_advances():
    s = session(mode="drill", items=(0, 1), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})
    if r["action"] != "advance":
        fail("drill must advance immediately, got %r" % r["action"])
    if r["session"]["cursor"] != 1:
        fail("drill advance must move the cursor")
    if not r.get("reveal"):
        fail("drill must return the immediate reveal payload")


def test_diagnostic_defers_until_completion():
    s = session(mode="diagnostic", items=(0, 1), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})
    if r["action"] != "defer_feedback":
        fail("diagnostic must defer feedback, got %r" % r["action"])
    if r["session"]["cursor"] != 0:
        fail("diagnostic must not move the cursor before completion")
    if "hint" in r or "reveal" in r:
        fail("diagnostic must return no hint or reveal payload")


def test_exam_defers_until_accepted_mark():
    s = session(mode="exam", items=(0, 1), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})
    if r["action"] != "defer_feedback":
        fail("exam must defer feedback, got %r" % r["action"])
    if r["session"]["cursor"] != 0:
        fail("exam must not move the cursor before an accepted mark")
    if "hint" in r or "reveal" in r:
        fail("exam must return no hint or reveal payload")


def test_short_response_stays_pending():
    s = session(mode="practice", items=(2,), cursor=0)
    r = runtime.teaching_transition(s, q3(), {"kind": "submit", "answer": "Reposition first."})
    if r["action"] != "defer_feedback":
        fail("a short response must stay pending, got %r" % r["action"])
    if r["session"]["cursor"] != 0:
        fail("a pending short response must not advance the cursor")


def test_mode_immutable_and_selection_mode_untouched():
    s = session(mode="practice", items=(0,), cursor=0)
    s["selection_mode"] = "spaced"
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"})
    if r["session"].get("selection_mode") != "spaced":
        fail("selection_mode must never be consulted or modified by feedback policy")
    if r["session"]["mode"] != "practice":
        fail("feedback mode must stay immutable")


def test_v1_session_upgrades_to_v2():
    s = session(mode="practice", items=(0,), cursor=0)
    v1 = dict(s)
    v1["schema_version"] = 1
    del v1["teaching_state"]
    upgraded = runtime.upgrade_session(v1)
    if upgraded["schema_version"] != runtime.SESSION_VERSION:
        fail("v1 session must upgrade to SESSION_VERSION %d" % runtime.SESSION_VERSION)
    if "teaching_state" not in upgraded or upgraded["teaching_state"] != {}:
        fail("v1 upgrade must add an empty teaching_state")
    if 1 not in runtime.SESSION_UPGRADES:
        fail("SESSION_UPGRADES must register a v1-to-v2 upgrade")
    # A resumed v2 session keeps working through the transition.
    r = runtime.teaching_transition(upgraded, q1(), {"kind": "submit", "answer": "B"})
    if r["action"] != "hold":
        fail("an upgraded session must execute the teaching transition")


def test_evidence_reconciliation_repairs_crash_window():
    # Evidence already holds one wrong response + one shown hint for q1; the
    # session's teaching_state is stale (empty). reconcile via evidence_state
    # must repair the state without replaying disclosure.
    canon_b = runtime.canonical_response(q1(), "B")
    ev_response = evidence.response_event(
        "sess-reconcile", q1(), "B", False, "practice", 1, "lesson_bank.md",
        hint_tier=None)
    ev_hint = evidence.hint_event(
        "sess-reconcile", q1(), 0, True, "lesson", "authored", "attempt",
        response_event_id=ev_response["event_id"], response_canonical=canon_b,
        attempt_num=1)
    state = {item_key(q1()): [ev_response, ev_hint]}
    s = session(mode="practice", items=(0,), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "B"},
                                    evidence_state=state)
    if r["action"] != "hold":
        fail("reconciled replay must hold, got %r" % r["action"])
    rec = r["session"]["teaching_state"][item_key(q1())]
    if rec["attempt_count"] != 1:
        fail("reconciliation must fold the evidence attempt count, got %r"
             % rec["attempt_count"])
    if rec["highest_tier_shown"] != 0:
        fail("reconciliation must fold the evidence-shown tier, got %r"
             % rec["highest_tier_shown"])


# ---- plan 06-01 Task 3: append-only evidence and derived outcomes ----------

def test_hint_event_contract_and_dedupe():
    q = q1()
    canon = runtime.canonical_response(q, "B")
    ev = evidence.hint_event("s", q, 1, True, "objective", "authored", "attempt",
                             response_event_id="r1", response_canonical=canon,
                             attempt_num=1)
    required = ("schema_version", "event_id", "event_type", "ts", "session_id",
                "item_id", "item_ref", "item_type", "bank", "mode", "attempt_number",
                "response_event_id", "response_canonical", "tier_index", "tier_name",
                "available", "source", "unlock_path", "dedupe_key")
    for key in required:
        if key not in ev:
            fail("hint event is missing required key %r" % key)
    if ev["event_type"] != "hint":
        fail("hint event must carry event_type 'hint'")
    if ev["tier_index"] != 1 or ev["tier_name"] != "objective":
        fail("hint event tier fields are wrong: %r" % ev)
    if ev["unlock_path"] != "attempt" or ev["source"] != "authored":
        fail("hint event unlock/source fields are wrong: %r" % ev)
    if "hint" not in evidence.KNOWN_EVENT_TYPES:
        fail("hint must be a member of KNOWN_EVENT_TYPES")
    if evidence.EVENT_SCHEMA_VERSION < 2:
        fail("EVENT_SCHEMA_VERSION must be bumped for the v2 contract")
    # A stumped hint for the same tier has a distinct dedupe key.
    stumped = evidence.hint_event("s", q, 1, True, "objective", "authored",
                                  "stumped", response_event_id="r1",
                                  response_canonical=canon, attempt_num=1)
    if stumped["dedupe_key"] == ev["dedupe_key"]:
        fail("attempt and stumped unlock must never share a dedupe key")
    # Same tier+path+attempt replays to the same key (idempotent).
    again = evidence.hint_event("s", q, 1, True, "objective", "authored", "attempt",
                                response_event_id="r1", response_canonical=canon,
                                attempt_num=1)
    if again["dedupe_key"] != ev["dedupe_key"]:
        fail("an identical hint replay must reproduce the same dedupe key")


def test_response_event_v2_hint_tier_null_vs_zero():
    q = q1()
    ev_null = evidence.response_event("s", q, "B", False, "practice", 1,
                                      "lesson_bank.md", hint_tier=None)
    ev_zero = evidence.response_event("s", q, "B", False, "practice", 1,
                                      "lesson_bank.md", hint_tier=0)
    if ev_null["hint_tier"] is not None:
        fail("hint_tier=None must stay null (no ladder), got %r" % ev_null["hint_tier"])
    if ev_zero["hint_tier"] != 0:
        fail("hint_tier=0 must record zero (tier 0 shown), got %r" % ev_zero["hint_tier"])


def _write_event(log, ev):
    written, existing = evidence.append_line_checked(
        log, json.dumps(ev, ensure_ascii=False, sort_keys=True), ev.get("dedupe_key"))
    if not written:
        fail("test event was unexpectedly deduped: %r" % ev)


def _validate_events(log, schema):
    for line in open(log, encoding="utf-8").read().splitlines():
        line = line.strip()
        if not line:
            continue
        errs = schema_validate.validate(json.loads(line), schema)
        if errs:
            fail("event does not validate against response.schema.json: %s" % errs[0])


def test_teaching_outcomes_from_live_events():
    tmp = tempfile.mkdtemp()
    try:
        log = os.path.join(tmp, "_evidence", "evidence.jsonl")
        sid = "sess-outcomes"
        q_a, q_b, q_short = q1(), q2(), q3()
        canon_wrong = runtime.canonical_response(q_a, "B")
        canon_right = runtime.canonical_response(q_a, "A")

        # q_a: first-try correct.
        _write_event(log, evidence.response_event(
            sid, q_a, "A", True, "practice", 1, "lesson_bank.md", hint_tier=None))
        # q_b: two genuine wrong attempts, an attempt-unlocked hint, a
        # stumped-unlocked hint, then a correct retry at tier 1.
        ev_wrong1 = evidence.response_event(
            sid, q_b, ["A"], False, "practice", 1, "lesson_bank.md", hint_tier=None)
        ev_hint1 = evidence.hint_event(
            sid, q_b, 0, True, "lesson", "authored", "attempt",
            response_event_id=ev_wrong1["event_id"],
            response_canonical=evidence.idempotency_canon(q_b, ["A"]), attempt_num=1)
        ev_wrong2 = evidence.response_event(
            sid, q_b, ["C"], False, "practice", 2, "lesson_bank.md", hint_tier=0)
        ev_hint2 = evidence.hint_event(
            sid, q_b, 1, True, "objective", "authored", "stumped",
            response_event_id=ev_wrong2["event_id"],
            response_canonical=evidence.idempotency_canon(q_b, ["C"]), attempt_num=2)
        ev_right = evidence.response_event(
            sid, q_b, ["A", "B"], True, "practice", 3, "lesson_bank.md", hint_tier=1)
        for ev in (ev_wrong1, ev_hint1, ev_wrong2, ev_hint2, ev_right):
            _write_event(log, ev)
        # q_short: a pending short response then an accepted human mark.
        ev_short = evidence.response_event(
            sid, q_short, "Reposition first.", None, "practice", 1,
            "lesson_bank.md", hint_tier=None)
        _write_event(log, ev_short)
        ev_mark = evidence.mark_event(
            sid, q_short.get("item_id", ""), q_short["id"], ev_short["event_id"],
            True, rubric=None, actor="human")
        _write_event(log, ev_mark)

        # A retracted response (and its hint) must vanish from the derivation.
        q_unused = q_a
        ev_retract_target = evidence.response_event(
            sid, q_unused, "C", False, "practice", 1, "lesson_bank.md", hint_tier=None)
        ev_retract_hint = evidence.hint_event(
            sid, q_unused, 0, True, "lesson", "authored", "attempt",
            response_event_id=ev_retract_target["event_id"],
            response_canonical=evidence.idempotency_canon(q_unused, "C"), attempt_num=1)
        _write_event(log, ev_retract_target)
        _write_event(log, ev_retract_hint)
        _write_event(log, evidence.retraction_event(
            [ev_retract_target["event_id"]], reason="test retraction"))
        _write_event(log, evidence.retraction_event(
            [ev_retract_hint["event_id"]], reason="test retraction"))

        _validate_events(log, load_schema(RESPONSE_SCHEMA))

        outcomes = evidence.teaching_outcomes(log, sid)
        rows = outcomes["teaching_outcomes"]
        key_a = item_key(q_a)
        key_b = item_key(q_b)
        key_short = item_key(q_short)
        if rows[key_a]["outcome"] != "first_try_correct":
            fail("q_a outcome must be first_try_correct, got %r" % rows[key_a])
        if rows[key_a]["hints_used"] != 0 or rows[key_a]["highest_tier"] is not None:
            fail("q_a hints_used/tier must be 0/None, got %r" % rows[key_a])
        if rows[key_b]["outcome"] != "correct_after_tier":
            fail("q_b outcome must be correct_after_tier, got %r" % rows[key_b])
        if rows[key_b]["correct_after_attempts"] != 3:
            fail("q_b correct_after_attempts must be 3, got %r" % rows[key_b])
        if rows[key_b]["hints_used"] != 2 or rows[key_b]["highest_tier"] != 1:
            fail("q_b hints_used/highest_tier must be 2/1, got %r" % rows[key_b])
        if rows[key_short]["outcome"] != "accepted_mark":
            fail("q_short outcome must be accepted_mark, got %r" % rows[key_short])
        if rows[key_short]["hints_used"] != 0:
            fail("q_short hints_used must be 0, got %r" % rows[key_short])
        # The retracted q_unused events leave no row (or an unresolved row), and
        # no counting of the retracted wrong response as a genuine attempt.
        if rows.get(item_key(q_unused)):
            fail("a fully-retracted item must not contribute a counted outcome")

        # Report shape validates against the extended report schema.
        report = {"schema_version": runtime.REPORT_VERSION, "session_id": sid,
                  "status": "active", "summary": outcomes}
        errs = schema_validate.validate(report["summary"], load_schema(REPORT_SCHEMA))
        if errs:
            fail("teaching_outcomes summary fails report.schema.json: %s" % errs[0])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_retraction_suppresses_hints_through_live_events():
    tmp = tempfile.mkdtemp()
    try:
        log = os.path.join(tmp, "_evidence", "evidence.jsonl")
        sid = "sess-retract"
        q = q1()
        ev_resp = evidence.response_event(sid, q, "B", False, "practice", 1,
                                          "lesson_bank.md", hint_tier=None)
        ev_hint = evidence.hint_event(sid, q, 0, True, "lesson", "authored",
                                      "attempt", response_event_id=ev_resp["event_id"],
                                      response_canonical=evidence.idempotency_canon(q, "B"),
                                      attempt_num=1)
        _write_event(log, ev_resp)
        _write_event(log, ev_hint)
        if len(evidence.hint_events(log, sid)) != 1:
            fail("hint_events must find the one live hint")
        _write_event(log, evidence.retraction_event([ev_hint["event_id"]],
                                                    reason="retract hint"))
        if len(evidence.hint_events(log, sid)) != 0:
            fail("a retracted hint must vanish from hint_events")
        outcomes = evidence.teaching_outcomes(log, sid)
        row = outcomes["teaching_outcomes"].get(item_key(q))
        if row is not None and row["hints_used"] != 0:
            fail("a retracted hint must not count in hints_used")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_session_schema_v2_contract():
    s = session(mode="practice", items=(0,), cursor=0)
    errs = schema_validate.validate(s, load_schema(SESSION_SCHEMA))
    if errs:
        fail("v2 session fails session.schema.json: %s" % errs[0])
    doc = load_schema(SESSION_SCHEMA)
    if doc["x-itembank-version"] != runtime.SESSION_VERSION:
        fail("session.schema.json version must match SESSION_VERSION")
    if "teaching_state" not in doc["properties"]:
        fail("session.schema.json must describe teaching_state")


def main():
    test_transition_rejects_unknown_action()
    test_practice_wrong_holds_and_unlocks_one_tier()
    test_practice_duplicate_and_empty_unlock_nothing()
    test_practice_hint_reveals_one_fixed_tier_in_order()
    test_practice_hint_without_attempt_unlocks_tier_zero()
    test_practice_stumped_reveals_exactly_next_tier()
    test_practice_correct_retry_advances_and_records_tier()
    test_practice_changed_answer_opens_new_attempt()
    test_practice_tier_three_is_response_specific()
    test_six_fixed_tiers_and_unavailable_slots()
    test_practice_reveal_then_advance()
    test_practice_last_item_completes()
    test_drill_reveals_and_advances()
    test_diagnostic_defers_until_completion()
    test_exam_defers_until_accepted_mark()
    test_short_response_stays_pending()
    test_mode_immutable_and_selection_mode_untouched()
    test_v1_session_upgrades_to_v2()
    test_evidence_reconciliation_repairs_crash_window()
    test_hint_event_contract_and_dedupe()
    test_response_event_v2_hint_tier_null_vs_zero()
    test_teaching_outcomes_from_live_events()
    test_retraction_suppresses_hints_through_live_events()
    test_session_schema_v2_contract()
    print("ok: hint roundtrip (transition, tiers, modes, evidence, outcomes)")


if __name__ == "__main__":
    main()
