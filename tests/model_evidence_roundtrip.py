#!/usr/bin/env python3
"""Phase 08-03 evidence fixtures: model_interaction and mark_proposal events.

Covers TEACH-07..09 and MODEL-05/MODEL-03 at the evidence layer, the same
way `tests/evidence_roundtrip.py` covers the response/mark spine:

- every model interaction appends as one durable, idempotent fact and reads
  back by session (TEACH-07), with a drop outcome storing descriptors only --
  fingerprints, byte count, reason code, profile, timing -- and never the
  dropped candidate's text (D-16);
- a rubric suggestion appends as a pending mark_proposal linked to the
  genuine short-answer response event and can never settle a mark: a
  proposal-only log leaves review_state pending and marks_by_event empty
  (TEACH-08/TEACH-09, MODEL-05, D-13/D-14);
- partial credit is N booleans derived at read time by proposal_summary
  (D-24), a human mark links to the proposal it accepts via proposal_ref
  (D-14), and mark_event's `marker != "human"` guard still raises for any
  other marker, byte-for-byte unchanged (D-23, T-1-24 regression).

Standard library only, runnable as `python tests/model_evidence_roundtrip.py`.
"""
import json, os, re, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import evidence                                             # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def flatten(obj):
    """Yield (key, value) for every key at every depth -- the same scan
    evidence_roundtrip's flatten() uses, so a forbidden phrase cannot hide
    in a nested pass_payload or points entry."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield (k, v)
            yield from flatten(v)
    elif isinstance(obj, list):
        for el in obj:
            yield from flatten(el)


# A default model-interaction call so tests read as deltas, not as one
# fifteen-argument invocation each. The signature follows the plan's
# artifacts table exactly (parent_interaction_id / output_bytes / elapsed_ms
# included).
MI = dict(
    session_id="sess-m1", bank="bank.md", item_ref="Q1", operation="hint",
    interaction_id="int-000001", outcome="pass", gate_reason=None,
    permitted_tier=3, backend_class="hosted", profile="claude-profile",
    request_fingerprint="req-fp-abc", response_fingerprint="resp-fp-def",
    elapsed_ms=123, output_bytes=512,
    pass_payload={"kind": "hint_plan", "move": "anchor_error"},
    parent_interaction_id=None,
)


def test_model_interaction_envelope_no_score_key():
    ev = evidence.model_interaction_event(**MI)
    for key in ("schema_version", "event_id", "event_type", "ts", "session_id",
                "bank", "item_ref", "operation", "interaction_id", "outcome",
                "gate_reason", "permitted_tier", "backend_class", "profile",
                "request_fingerprint", "response_fingerprint", "elapsed_ms",
                "output_bytes", "pass_payload", "parent_interaction_id",
                "dedupe_key"):
        if key not in ev:
            fail("model_interaction event missing key %r: %r" % (key, ev))
    if ev["event_type"] != "model_interaction":
        fail("event_type wrong: %r" % ev["event_type"])
    if ev["operation"] != "hint":
        fail("operation wrong: %r" % ev["operation"])
    if ev["outcome"] != "pass":
        fail("outcome wrong: %r" % ev["outcome"])
    if ev["backend_class"] != "hosted":
        fail("backend_class wrong: %r" % ev["backend_class"])
    if ev["gate_reason"] is not None:
        fail("a pass interaction must carry gate_reason None, got %r"
             % ev["gate_reason"])
    if ev["pass_payload"] != MI["pass_payload"]:
        fail("a pass interaction must carry its pass payload, got %r"
             % ev["pass_payload"])
    if ev["parent_interaction_id"] is not None:
        fail("a non-retry interaction must carry parent_interaction_id None, "
             "got %r" % ev["parent_interaction_id"])
    if "score" in ev:
        fail("a model_interaction event must carry no score key (D-15): %r" % ev)

    # Builder validation: every invalid argument is a ValueError, because the
    # log is append-only and a malformed fact cannot be corrected later.
    def _bad(**over):
        kwargs = dict(MI)
        kwargs.update(over)
        return kwargs

    for kwargs, why in [
        (_bad(interaction_id=""), "empty interaction_id"),
        (_bad(interaction_id=None), "null interaction_id"),
        (_bad(operation="chat"), "operation outside (hint, rubric_review)"),
        (_bad(outcome="passed"), "outcome outside (pass, drop, unavailable)"),
        (_bad(backend_class="cloud"), "backend_class outside (hosted, local)"),
    ]:
        try:
            evidence.model_interaction_event(**kwargs)
            fail("model_interaction_event accepted %s" % why)
        except ValueError:
            pass

    # A rubric_review operation is legal.
    rev = evidence.model_interaction_event(**dict(MI, operation="rubric_review"))
    if rev["operation"] != "rubric_review":
        fail("rubric_review operation must be legal, got %r" % rev["operation"])


def test_model_interaction_append_retrieve_dedupe():
    """TEACH-07 + D-12: one interaction appends through the ONE writer,
    replaying the same interaction_id reports already_recorded, and the
    event reads back by session in append order. A retry is a NEW
    interaction id carrying a parent link, so cost and repeated failures
    stay visible without reusing the dedupe key (D-12)."""
    tmp = tempfile.mkdtemp()
    try:
        log = evidence.log_path(tmp)
        ev = evidence.model_interaction_event(**MI)

        res = evidence.append_event(log, ev)
        if res["status"] != "recorded":
            fail("first append must record, got %r" % res)
        replay = evidence.append_event(log, ev)
        if replay["status"] != "already_recorded":
            fail("replaying the same interaction_id must dedupe, got %r" % replay)

        raw = [l for l in open(log, encoding="utf-8").read().splitlines()
               if l.strip()]
        if len(raw) != 1:
            fail("a deduped log must hold one interaction line, found %d" %
                 len(raw))

        via_events = [e for e in evidence.events(log)
                      if e["event_type"] == "model_interaction"]
        if len(via_events) != 1 or via_events[0]["interaction_id"] != "int-000001":
            fail("events() must yield the interaction in append order: %r"
                 % via_events)
        live = [e for e in evidence.live_events(log)
                if e["event_type"] == "model_interaction"]
        if len(live) != 1:
            fail("live_events() must yield the interaction: %r" % live)

        by_session = evidence.model_interactions(log, "sess-m1")
        if len(by_session) != 1 or by_session[0]["event_id"] != ev["event_id"]:
            fail("model_interactions(log, session_id) must retrieve it: %r"
                 % by_session)
        if evidence.model_interactions(log, "sess-other") != []:
            fail("model_interactions must filter by session_id")

        # Explicit retry: new interaction id, parent link to the original.
        retry = evidence.model_interaction_event(**dict(
            MI, interaction_id="int-000001b", parent_interaction_id="int-000001"))
        res_retry = evidence.append_event(log, retry)
        if res_retry["status"] != "recorded":
            fail("a retry with a new interaction_id must record, got %r"
                 % res_retry)
        if retry["parent_interaction_id"] != "int-000001":
            fail("retry must carry its parent interaction id, got %r"
                 % retry["parent_interaction_id"])
        got = evidence.model_interactions(log, "sess-m1")
        if [e["interaction_id"] for e in got] != ["int-000001", "int-000001b"]:
            fail("retrieval must stay in append order with the retry: %r" % got)
        if got[0]["dedupe_key"] == got[1]["dedupe_key"]:
            fail("a retry must never share the original interaction's dedupe_key")
    finally:
        shutil_rmtree(tmp)


def test_model_interaction_drop_descriptor_only():
    """D-16 + T-08-21: a drop outcome stores descriptors only -- request and
    output fingerprints, byte count, gate reason, profile, timing -- and no
    candidate text. A scan of the raw event and every reader finds none of
    the dropped candidate's forbidden phrases."""
    tmp = tempfile.mkdtemp()
    try:
        log = evidence.log_path(tmp)
        forbidden = ["the model nearly revealed that Airway is the key",
                     "The correct option is B", "candidate-secret-xyz"]
        ev = evidence.model_interaction_event(**dict(
            MI, outcome="drop", gate_reason="gate.ambiguous",
            request_fingerprint="req-fp-drop", response_fingerprint="resp-fp-drop",
            output_bytes=2048, elapsed_ms=77, pass_payload=None))

        res = evidence.append_event(log, ev)
        if res["status"] != "recorded":
            fail("drop interaction append must record, got %r" % res)
        if ev["pass_payload"] is not None:
            fail("a drop outcome must not store pass_payload: %r" % ev["pass_payload"])
        if "score" in ev:
            fail("a drop interaction must carry no score key: %r" % ev)

        # Descriptors are present.
        if ev["gate_reason"] != "gate.ambiguous":
            fail("drop must keep its machine-readable reason code: %r"
                 % ev["gate_reason"])
        if ev["output_bytes"] != 2048 or ev["elapsed_ms"] != 77:
            fail("drop must keep byte count and timing: %r" % ev)
        if ev["response_fingerprint"] != "resp-fp-drop":
            fail("drop must keep the output fingerprint: %r" % ev)

        # The forbidden candidate phrases must not exist anywhere: in the
        # built dict, in the raw log line, or in any reader.
        for phrase in forbidden:
            for k, v in flatten(ev):
                if phrase in str(v):
                    fail("forbidden phrase %r leaked into the event dict" % phrase)
        raw_text = open(log, encoding="utf-8").read()
        for phrase in forbidden:
            if phrase in raw_text:
                fail("forbidden phrase %r was written to the log" % phrase)
        readers = (list(evidence.events(log)),
                   list(evidence.live_events(log)),
                   evidence.model_interactions(log, "sess-m1"))
        for phrase in forbidden:
            for col in readers:
                if phrase in str(col):
                    fail("forbidden phrase %r leaked into a reader" % phrase)
    finally:
        shutil_rmtree(tmp)


def shutil_rmtree(path):
    import shutil
    shutil.rmtree(path, ignore_errors=True)


# ---- Task 2: mark_proposal events ------------------------------------------
# A rubric suggestion is a pending per-point proposal linked to the genuine
# short-answer response event; it can never settle a mark (D-13/D-14, D-23).

def test_mark_proposal_envelope_no_score_no_verdict():
    points = [
        {"point_index": 0, "status": "pass",
         "rationale": "Names airway management first."},
        {"point_index": 1, "status": "uncertain",
         "rationale": "Only implies suction; does not say when."},
    ]
    ev = evidence.mark_proposal_event(
        session_id="sess-p1", bank="bank.md", item_id="item-1", item_ref="Q1",
        response_event_id="resp-ev-1", interaction_id="int-000010", points=points)
    for key in ("schema_version", "event_id", "event_type", "ts", "session_id",
                "bank", "item_id", "item_ref", "response_event_id",
                "interaction_id", "points", "dedupe_key"):
        if key not in ev:
            fail("mark_proposal event missing key %r: %r" % (key, ev))
    if ev["event_type"] != "mark_proposal":
        fail("event_type wrong: %r" % ev["event_type"])
    if ev["response_event_id"] != "resp-ev-1":
        fail("proposal must link to its response event: %r" % ev)
    if ev["interaction_id"] != "int-000010":
        fail("proposal must link to its interaction: %r" % ev)
    if len(ev["points"]) != 2:
        fail("proposal must keep every per-point suggestion: %r" % ev["points"])
    if ev["points"][0]["status"] != "pass" or ev["points"][0]["point_index"] != 0:
        fail("point shape wrong: %r" % ev["points"][0])
    if "score" in ev:
        fail("a mark_proposal event must carry no score key (D-23): %r" % ev)
    if "verdict" in ev:
        fail("a mark_proposal event must carry no verdict field (T-08-20): %r" % ev)

    # Builder validation.
    def _bad(**over):
        base = dict(session_id="s", bank="b", item_id="i", item_ref="Q1",
                    response_event_id="resp-ev-1", interaction_id="int-1",
                    points=[{"point_index": 0, "status": "pass",
                             "rationale": "ok"}])
        base.update(over)
        return base

    for kwargs, why in [
        (_bad(response_event_id=""), "empty response_event_id"),
        (_bad(response_event_id=None), "null response_event_id"),
        (_bad(interaction_id=""), "empty interaction_id"),
        (_bad(points=[{"point_index": 0, "status": "wrong",
                       "rationale": "x"}]), "status outside (pass, fail, uncertain)"),
        (_bad(points=[{"point_index": -1, "status": "pass",
                       "rationale": "x"}]), "negative point_index"),
        (_bad(points=[{"point_index": 0, "status": "pass",
                       "rationale": "r" * 241}]), "rationale over 240 chars"),
    ]:
        try:
            evidence.mark_proposal_event(**kwargs)
            fail("mark_proposal_event accepted %s" % why)
        except ValueError:
            pass

    # Idempotency: one proposal per response-interaction pair (D-13).
    tmp = tempfile.mkdtemp()
    try:
        log = evidence.log_path(tmp)
        res = evidence.append_event(log, ev)
        if res["status"] != "recorded":
            fail("first proposal append must record, got %r" % res)
        replay = evidence.append_event(log, ev)
        if replay["status"] != "already_recorded":
            fail("a second identical proposal must dedupe, got %r" % replay)
        raw = [l for l in open(log, encoding="utf-8").read().splitlines()
               if l.strip()]
        if len(raw) != 1:
            fail("a deduped proposal log must hold one line, found %d" % len(raw))
    finally:
        shutil_rmtree(tmp)


def test_proposal_only_log_leaves_response_pending():
    """TEACH-08/TEACH-09 + MODEL-05 + T-08-20: appending only proposals for a
    short response leaves the response's review_state pending and
    marks_by_event empty -- a model-only path can never settle a mark."""
    tmp = tempfile.mkdtemp()
    try:
        log = evidence.log_path(tmp)
        q = {"id": "Q1", "type": "short", "objective": "emt:airway",
             "item_id": "item-1"}
        resp = evidence.response_event(
            "sess-p2", q, "Open the airway and suction.", None, "practice", 1,
            "bank.md")
        res = evidence.append_event(log, resp)
        if res["status"] != "recorded":
            fail("response append must record, got %r" % res)

        prop = evidence.mark_proposal_event(
            session_id="sess-p2", bank="bank.md", item_id="item-1",
            item_ref="Q1", response_event_id=resp["event_id"],
            interaction_id="int-000011",
            points=[{"point_index": 0, "status": "pass",
                     "rationale": "Names the airway."},
                    {"point_index": 1, "status": "uncertain",
                     "rationale": "Suction timing unclear."}])
        if evidence.append_event(log, prop)["status"] != "recorded":
            fail("proposal append must record")

        marks = evidence.marks_by_event(log)
        if resp["event_id"] in marks:
            fail("a proposal-only log must never produce a settled mark "
                 "(T-08-20): %r" % marks)
        if marks != {}:
            fail("marks_by_event must be empty with only proposals: %r" % marks)

        # review_state is derived at read time from marks_by_event only, so
        # it stays pending: the response event's own score stays None and
        # no reader flips it.
        if resp["score"] is not None:
            fail("the response event's own score must stay None: %r"
                 % resp["score"])
        rendered = evidence.render_session_json(log, "sess-p2", [q], "bank.md")
        row = next((r for r in rendered["responses"]
                    if r["item_id"] == "Q1"), None)
        if row is None:
            fail("render_session_json must include the response: %r" % rendered)
        if row["review_state"] != "pending":
            fail("a proposal-only log must leave review_state pending, got %r"
                 % row["review_state"])
        if row["score"] is not None:
            fail("the derived view must not change the response score: %r" % row)
    finally:
        shutil_rmtree(tmp)


def test_proposals_for_and_empty_points_pending():
    """proposals_for filters live mark_proposal events per response; a
    proposal with an empty points array is valid and reads back as
    pending/unknown, never a default pass (D-13, D-22)."""
    tmp = tempfile.mkdtemp()
    try:
        log = evidence.log_path(tmp)
        q = {"id": "Q1", "type": "short", "objective": "emt:airway",
             "item_id": "item-1"}
        resp_a = evidence.response_event(
            "sess-p3", q, "Suction first.", None, "practice", 1, "bank.md")
        evidence.append_event(log, resp_a)
        resp_b = evidence.response_event(
            "sess-p3", dict(q, id="Q2", item_id="item-2"), "Bag the patient.",
            None, "practice", 1, "bank.md")
        evidence.append_event(log, resp_b)

        prop_a = evidence.mark_proposal_event(
            session_id="sess-p3", bank="bank.md", item_id="item-1",
            item_ref="Q1", response_event_id=resp_a["event_id"],
            interaction_id="int-000012",
            points=[{"point_index": 0, "status": "fail",
                     "rationale": "Order reversed."}])
        empty = evidence.mark_proposal_event(
            session_id="sess-p3", bank="bank.md", item_id="item-2",
            item_ref="Q2", response_event_id=resp_b["event_id"],
            interaction_id="int-000013", points=[])
        evidence.append_event(log, prop_a)
        evidence.append_event(log, empty)

        all_props = evidence.proposals_for(log, "sess-p3")
        if len(all_props) != 2:
            fail("proposals_for must return both proposals, got %d: %r"
                 % (len(all_props), all_props))
        one = evidence.proposals_for(log, "sess-p3",
                                     response_event_id=resp_a["event_id"])
        if len(one) != 1 or one[0]["event_id"] != prop_a["event_id"]:
            fail("proposals_for must filter by response_event_id: %r" % one)
        if evidence.proposals_for(log, "sess-other") != []:
            fail("proposals_for must filter by session_id")
        if evidence.proposals_for(log, "sess-p3",
                                  response_event_id="no-such-event") != []:
            fail("proposals_for must return nothing for an unknown response")

        # An empty-points proposal is valid and pending/unknown -- never a
        # default pass. This lives at the reader layer too: the event itself
        # carries points [].
        if empty["points"] != []:
            fail("an empty-points proposal must keep points [], got %r"
                 % empty["points"])
    finally:
        shutil_rmtree(tmp)


def main():
    test_model_interaction_envelope_no_score_key()
    test_model_interaction_append_retrieve_dedupe()
    test_model_interaction_drop_descriptor_only()
    test_mark_proposal_envelope_no_score_no_verdict()
    test_proposal_only_log_leaves_response_pending()
    test_proposals_for_and_empty_points_pending()
    print("model evidence contract: ok (interaction envelope/no-score, "
          "idempotency + retry linkage, descriptor-only drop, proposal "
          "envelope/no-score/no-verdict, proposal-only stays pending, "
          "proposals_for + empty-points pending)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

