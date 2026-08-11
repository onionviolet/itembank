#!/usr/bin/env python3
"""Phase 08-04 surface fixtures: hint/rubric-review CLI commands and the
agent usage contract (plan 08-04).

Drives the real CLI via subprocess and calls the shared `do_*` functions
directly, proving:

- offline hint with the shipped disabled backend returns the typed
  unavailable payload plus the authored tier content and appends exactly one
  model_interaction event (MODEL-03/D-08/D-11), is idempotent per
  interaction id, and an explicit retry mints a parent-linked child
  interaction (D-12);
- rubric review is pending-suggestions-only for a genuine pending short
  response, refusals are named with no evidence write, the human accepts
  through the existing mark command with a proposal reference, and batch
  resolution is all-or-nothing (D-13/D-14/D-25);
- the suggestion_reveal setting is read and a suggestion renders only as a
  pending token, never a number, fraction, check, or cross glyph (D-22);
- the agent usage contract validates, is machine-readable, and prints
  verbatim from `itembank usage` and inside `itembank schema --all`
  (MODEL-04).

Standard library only, runnable as `python tests/model_surface_roundtrip.py`.
"""
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import evidence                                            # noqa: E402
import runtime                                             # noqa: E402
import schema_validate                                     # noqa: E402
from surfaces import session as session_surface            # noqa: E402
from surfaces import settings as settings_surface          # noqa: E402

TOOL = os.path.join(ROOT, "itembank.py")

MC_BANK = """## LESSON

### Airway management

The OPA holds the tongue off the posterior pharynx to open the airway.

Q1. Which device opens the airway?   (difficulty: recall)
[LESSON-REF: Airway management]
[OBJECTIVE: emt:airway]
A) OPA
B) NPA
C) King
D) Combitube

CORRECT: A

WHY BEST: The OPA holds the tongue off the pharynx.

KEY DISCRIMINATOR: Indication versus contraindication.

SECOND-BEST: B. The NPA is softer; this would be correct if the question asked for the nasal route.

DISTRACTOR ANALYSIS:
- A) Correct: the oral airway.
- B) The nasal airway; this would be correct if the question asked for a nasal adjunct.
- C) A supraglottic device; this would be correct if the question asked for a rescue airway.
- D) A supraglottic device; this would be correct if the question asked for a rescue airway.

TRAP: Confusing OPA and NPA indications.

CONFIDENCE: high
"""

SHORT_BANK = """Q1. Explain the role of the OPA in maintaining the airway.   (difficulty: analysis)
[OBJECTIVE: emt:airway]
[TYPE: short]

MODEL: The OPA holds the tongue off the posterior pharynx, opening the airway.

RUBRIC:
- States that the OPA lifts the tongue
- Names the posterior pharynx as the target
- Notes when the OPA is contraindicated

TRAP: Confusing OPA with NPA indications.

CONFIDENCE: high
"""

# A fake hosted_cli backend that echoes the request's interaction id and
# returns one bounded rubric_proposal candidate -- no real provider, no
# network. The rationale texts deliberately never reproduce the item's model
# answer, so the gate's protected-fragment scan passes them.
FAKE_BACKEND = """#!/usr/bin/env python3
import json, sys
req = json.load(sys.stdin)
candidate = {"kind": "rubric_proposal", "interaction_id": req["interaction_id"],
             "points": [
                 {"point_index": 0, "status": "pass", "rationale": "Names the tongue lift."},
                 {"point_index": 1, "status": "uncertain", "rationale": "No pharynx target stated."},
                 {"point_index": 2, "status": "pass", "rationale": "Notes the contraindication."}
             ]}
print(json.dumps(candidate))
"""


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run(args, cwd):
    """Run the CLI and return parsed JSON stdout; any non-zero exit fails."""
    r = subprocess.run([sys.executable, TOOL] + [str(a) for a in args],
                       cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        fail("command %r failed (%d): %s" % (args, r.returncode, r.stderr))
    return json.loads(r.stdout)


def run_raw(args, cwd):
    """Run the CLI and return the CompletedProcess without asserting exit 0."""
    return subprocess.run([sys.executable, TOOL] + [str(a) for a in args],
                          cwd=cwd, capture_output=True, text=True)


def write_bank(tmp, text, name="bank.md"):
    path = os.path.join(tmp, name)
    open(path, "w", encoding="utf-8").write(text)
    return path


def start_session(tmp, bank, mode="practice", count=1, seed=0):
    session = os.path.join(tmp, "session.json")
    run(["start", bank, "--count", str(count), "--seed", str(seed),
         "--mode", mode, "--out", session], tmp)
    return session


def session_id_of(session_path):
    return runtime.read_session(session_path)["session_id"]


def hint_interactions(log, sid):
    return [e for e in evidence.model_interactions(log, sid)
            if e.get("operation") == "hint"]


def install_fake_backend(tmp):
    """Write a fake hosted_cli backend plus the settings file that activates
    it, so rubric review reaches a candidate without any real provider."""
    script = os.path.join(tmp, "fake_backend.py")
    open(script, "w", encoding="utf-8").write(FAKE_BACKEND)
    settings = {
        "model_backend": {
            "active": "fake",
            "profiles": [{"name": "fake", "transport": "hosted_cli",
                          "command": [sys.executable, script],
                          "model": "fake", "timeout_seconds": 5,
                          "max_output_bytes": 65536, "context_window": 4096}],
        }
    }
    open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8").write(
        json.dumps(settings))


def wrong_session(tmp):
    """A practice session on the mc bank whose current item has two genuine
    wrong answers -- unlocking tier 1 (the objective), which this bank
    carries, so the authored fallback is present for the offline hint."""
    bank = write_bank(tmp, MC_BANK)
    session = start_session(tmp, bank)
    run(["submit", session, "--answer", json.dumps("B")], tmp)
    run(["submit", session, "--answer", json.dumps("C")], tmp)
    return session


# ---- Task 1: offline hint, idempotency, retry lineage ----------------------

def test_hint_offline_disabled_backend_typed_unavailable():
    """MODEL-03 + D-08/D-11: with the shipped disabled backend, do_hint
    returns the typed unavailable payload, carries the authored tier content
    for the permitted tier, appends exactly one model_interaction event
    (outcome unavailable, operation hint), and never leaks a reason code or
    tier into the learner-facing payload."""
    tmp = tempfile.mkdtemp()
    try:
        session = wrong_session(tmp)
        result = session_surface.do_hint(session)

        if result["status"] != "unavailable":
            fail("offline hint must be typed unavailable, got %r" % result)
        if result["generated"] is not None:
            fail("offline hint must generate nothing, got %r" % result["generated"])
        if not result["interaction_id"]:
            fail("offline hint must mint an interaction id")
        authored = result["authored"]
        if not authored or authored.get("available") is not True:
            fail("authored tier content must be present when the item has it: %r"
                 % authored)
        if not authored.get("content"):
            fail("authored tier content must be non-empty: %r" % authored)
        for key in ("reason", "gate_reason", "tier", "error", "backend_class"):
            if key in result:
                fail("the learner-facing hint payload must not carry %r: %r"
                     % (key, result))

        log = evidence.log_path(tmp)
        evs = hint_interactions(log, session_id_of(session))
        if len(evs) != 1:
            fail("exactly one model_interaction event expected, found %d: %r"
                 % (len(evs), evs))
        ev = evs[0]
        if ev["outcome"] != "unavailable":
            fail("interaction outcome must be unavailable, got %r" % ev["outcome"])
        if ev["interaction_id"] != result["interaction_id"]:
            fail("evidence interaction_id must match the payload")
        if ev["permitted_tier"] != 0:
            fail("the recorded permitted tier must be 0 (lesson pointer), got %r"
                 % ev["permitted_tier"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_hint_idempotent_second_call():
    """D-12: a repeated do_hint without retry returns the same interaction
    id and reports already_recorded, and the log still holds one generation
    -- at most one generation per interaction id."""
    tmp = tempfile.mkdtemp()
    try:
        session = wrong_session(tmp)
        first = session_surface.do_hint(session)
        second = session_surface.do_hint(session)

        if second["interaction_id"] != first["interaction_id"]:
            fail("a repeated hint must return the same interaction id, got %r vs %r"
                 % (second["interaction_id"], first["interaction_id"]))
        if second["evidence"].get("status") != "already_recorded":
            fail("a repeated hint must report already_recorded, got %r"
                 % second["evidence"])
        log = evidence.log_path(tmp)
        if len(hint_interactions(log, session_id_of(session))) != 1:
            fail("a repeated hint must not generate a second event")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_hint_retry_lineage():
    """D-12: do_hint(retry=True) mints a child interaction id whose
    parent_interaction_id references the original and appends a new
    model_interaction event with a distinct dedupe key."""
    tmp = tempfile.mkdtemp()
    try:
        session = wrong_session(tmp)
        first = session_surface.do_hint(session)
        retry = session_surface.do_hint(session, retry=True)

        if retry["interaction_id"] == first["interaction_id"]:
            fail("a retry must mint a new child interaction id")
        if retry["evidence"].get("status") != "recorded":
            fail("a retry must append a new event, got %r" % retry["evidence"])

        log = evidence.log_path(tmp)
        evs = hint_interactions(log, session_id_of(session))
        if len(evs) != 2:
            fail("a retry must produce exactly two hint interactions, found %d"
                 % len(evs))
        child = evs[-1]
        if child["interaction_id"] != retry["interaction_id"]:
            fail("the retry event must carry the returned child id")
        if child["parent_interaction_id"] != first["interaction_id"]:
            fail("the retry must carry parent_interaction_id referencing the "
                 "original, got %r" % child["parent_interaction_id"])
        if child["dedupe_key"] == evs[0]["dedupe_key"]:
            fail("a retry must never reuse the original interaction's dedupe key")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_cmd_hint_prints_json_exits_zero_and_parity():
    """cmd_hint prints the typed payload as JSON and exits 0, and the CLI
    path reaches the same do_hint the daemon will call (source-inspection
    parity)."""
    tmp = tempfile.mkdtemp()
    try:
        session = wrong_session(tmp)
        r = run_raw(["hint", "--session", session], tmp)
        if r.returncode != 0:
            fail("itembank hint exited %d: %s" % (r.returncode, r.stderr))
        payload = json.loads(r.stdout)
        if payload["status"] != "unavailable":
            fail("the CLI hint payload must be typed unavailable, got %r" % payload)

        src = inspect.getsource(session_surface.cmd_hint)
        if "do_hint(" not in src:
            fail("cmd_hint does not call do_hint() -- the CLI and the daemon "
                 "must reach the same orchestration function")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_hint_no_genuine_wrong_response_generates_nothing():
    """Edge probe: a session whose current response is a pending short answer
    (never wrong) returns the typed unavailable payload with no interaction
    id and writes no evidence."""
    tmp = tempfile.mkdtemp()
    try:
        bank = write_bank(tmp, SHORT_BANK)
        session = start_session(tmp, bank)
        run(["submit", session, "--answer",
             json.dumps("The OPA opens the airway.")], tmp)

        result = session_surface.do_hint(session)
        if result["status"] != "unavailable" or result["interaction_id"] is not None:
            fail("hint with no genuine wrong response must be typed unavailable "
                 "with no interaction id, got %r" % result)
        log = evidence.log_path(tmp)
        if evidence.model_interactions(log, session_id_of(session)):
            fail("no interaction may be recorded without a genuine wrong response")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- Task 2: rubric review, pending suggestions, human-only accept --------

def _short_pending_session(tmp):
    """A session on the short bank whose current item has one pending
    short-answer response, with the fake backend installed so rubric review
    reaches a candidate."""
    install_fake_backend(tmp)
    bank = write_bank(tmp, SHORT_BANK)
    session = start_session(tmp, bank)
    run(["submit", session, "--answer",
         json.dumps("The OPA lifts the tongue to open the airway.")], tmp)
    return session


def test_rubric_review_pending_suggestions_short_only():
    """D-13/D-22: do_rubric_review on a genuine pending short response
    returns {"status": "pending", "points": [...]} with one suggestion per
    rubric point, appends a mark_proposal event linked to the response event
    and to the interaction, reads suggestion_reveal from settings, and never
    settles a mark -- marks_by_event stays empty and review_state stays
    pending."""
    tmp = tempfile.mkdtemp()
    try:
        session = _short_pending_session(tmp)
        result = session_surface.do_rubric_review(session)

        if result["status"] != "pending":
            fail("rubric review must return status pending, got %r" % result)
        points = result.get("points")
        if not points or len(points) != 3:
            fail("rubric review must carry one suggestion per rubric point, got %r"
                 % points)
        for p in points:
            if not isinstance(p.get("point_index"), int) or \
                    p.get("status") not in ("pass", "fail", "uncertain") or \
                    not isinstance(p.get("rationale"), str):
                fail("each point must carry point_index/status/rationale, got %r"
                     % p)
        if not result.get("interaction_id"):
            fail("rubric review must mint an interaction id: %r" % result)
        if result.get("suggestion_reveal") != "after-self-mark":
            fail("the shipped default suggestion_reveal must be read from "
                 "settings: %r" % result)

        log = evidence.log_path(tmp)
        sid = session_id_of(session)
        interactions = evidence.model_interactions(log, sid)
        if len(interactions) != 1 or \
                interactions[0]["operation"] != "rubric_review":
            fail("rubric review must append one rubric_review interaction: %r"
                 % interactions)
        responses = evidence.session_events(log, sid)
        if not responses:
            fail("the short response event must exist")
        resp = responses[-1]
        proposals = evidence.proposals_for(log, sid,
                                           response_event_id=resp["event_id"])
        if len(proposals) != 1:
            fail("one mark_proposal event must be linked to the response, got %r"
                 % proposals)
        proposal = proposals[0]
        if proposal["response_event_id"] != resp["event_id"]:
            fail("the proposal must reference the response event")
        if proposal["interaction_id"] != result["interaction_id"]:
            fail("the proposal must reference the interaction")
        if resp["event_id"] in evidence.marks_by_event(log):
            fail("a model-only path must never settle a mark")
        rendered = evidence.render_session_json(log, sid, [], "bank.md")
        row = next((r for r in rendered["responses"]
                    if r["item_id"] == resp["item_ref"]), None)
        if row is None or row["review_state"] != "pending":
            fail("review_state must stay pending, got %r" % row)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_rubric_review_refuses_with_named_reason_and_no_write():
    """D-13 edge probes: a non-short item or an already-marked response is a
    typed refusal with a named reason and no evidence write at all."""
    tmp = tempfile.mkdtemp()
    try:
        # Non-short current item: mc session with one genuine wrong answer.
        install_fake_backend(tmp)
        mc_bank = write_bank(tmp, MC_BANK)
        mc_session = start_session(tmp, mc_bank)
        run(["submit", mc_session, "--answer", json.dumps("B")], tmp)
        refused = session_surface.do_rubric_review(mc_session)
        if refused["status"] != "refused" or not refused.get("reason"):
            fail("rubric review on a non-short item must refuse with a named "
                 "reason, got %r" % refused)
        log = evidence.log_path(tmp)
        if evidence.model_interactions(log, session_id_of(mc_session)) or \
                evidence.proposals_for(log, session_id_of(mc_session)):
            fail("a refusal must write no interaction and no proposal event")

        # Already-marked short response: mark it, then ask again.
        short_session = _short_pending_session(tmp)
        sid = session_id_of(short_session)
        run(["mark", "--session", sid, "--item", "Q1", "--verdict", "pass",
             "--base", tmp], tmp)
        again = session_surface.do_rubric_review(short_session)
        if again["status"] != "refused" or again.get("reason") != "already_marked":
            fail("rubric review on an already-marked response must refuse with "
                 "reason already_marked, got %r" % again)
        log2 = evidence.log_path(tmp)
        proposals_before = len(evidence.proposals_for(log2, sid))
        interactions_before = len(evidence.model_interactions(log2, sid))
        if proposals_before != 0 or interactions_before != 0:
            fail("the refused rubric review must write nothing; found %d "
                 "proposal(s), %d interaction(s)"
                 % (proposals_before, interactions_before))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_cmd_mark_proposal_human_accept():
    """D-14: cmd_mark --proposal <event_id> resolves the proposal to its
    response event and records mark_event(marker='human', proposal_ref=...);
    the proposal event stays separate and the response reads as marked."""
    tmp = tempfile.mkdtemp()
    try:
        session = _short_pending_session(tmp)
        sid = session_id_of(session)
        result = session_surface.do_rubric_review(session)
        proposal_event_id = result["proposal_event_id"]
        if not proposal_event_id:
            fail("rubric review must return its proposal event id: %r" % result)

        marked = run(["mark", "--session", sid, "--proposal", proposal_event_id,
                      "--verdict", "pass", "--base", tmp], tmp)
        log = evidence.log_path(tmp)
        responses = evidence.session_events(log, sid)
        resp = responses[-1]
        marks = evidence.marks_by_event(log)
        mark = marks.get(resp["event_id"])
        if mark is None:
            fail("--proposal accept must record a settled mark: %r" % marks)
        if mark["marker"] != "human":
            fail("an accepted mark must be marker 'human', got %r" % mark["marker"])
        if mark["proposal_ref"] != proposal_event_id:
            fail("the accepted mark must carry proposal_ref, got %r" % mark)
        proposals = evidence.proposals_for(log, sid)
        if len(proposals) != 1 or proposals[0]["event_id"] != proposal_event_id:
            fail("the proposal event must stay separate: %r" % proposals)
        rendered = evidence.render_session_json(log, sid, [], "bank.md")
        row = next((r for r in rendered["responses"]
                    if r["item_id"] == resp["item_ref"]), None)
        if row is None or row["review_state"] != "marked":
            fail("the response must read as marked after the human accept, got %r"
                 % row)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_cmd_mark_proposal_batch_all_or_nothing():
    """D-25 + the cmd_mark batch discipline: a --marks batch whose entries
    carry proposal ids validates every entry before appending any; an
    unknown proposal id anywhere exits non-zero with nothing appended."""
    tmp = tempfile.mkdtemp()
    try:
        session = _short_pending_session(tmp)
        sid = session_id_of(session)
        result = session_surface.do_rubric_review(session)
        good_id = result["proposal_event_id"]

        bad_batch = [{"proposal": good_id, "verdict": "pass"},
                     {"proposal": "no-such-proposal-1234567890abcdef",
                      "verdict": "pass"}]
        r = run_raw(["mark", "--session", sid, "--marks", json.dumps(bad_batch),
                     "--base", tmp], tmp)
        if r.returncode == 0:
            fail("a batch naming one unknown proposal id must exit non-zero")
        log = evidence.log_path(tmp)
        responses = evidence.session_events(log, sid)
        if responses:
            resp = responses[-1]
            if resp["event_id"] in evidence.marks_by_event(log):
                fail("a failed batch must append nothing -- the valid entry "
                     "must not be recorded on its own")
        # A fully valid batch records exactly one human mark.
        good_batch = [{"proposal": good_id, "verdict": "pass"}]
        r2 = run_raw(["mark", "--session", sid, "--marks", json.dumps(good_batch),
                      "--base", tmp], tmp)
        if r2.returncode != 0:
            fail("a valid proposal batch must exit 0: %s" % r2.stderr)
        marks = evidence.marks_by_event(log)
        if len(marks) != 1:
            fail("a valid proposal batch must record exactly one mark, got %r"
                 % marks)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_suggestion_pending_token_only_and_no_auto_accept():
    """D-22/D-25: the surface representation of a suggestion is a single
    pending token -- never a number, fraction, check, or cross glyph -- the
    suggestion_reveal setting is read from settings, and no auto-accept flag
    or setting exists anywhere."""
    tmp = tempfile.mkdtemp()
    try:
        for setting in ("after-self-mark", "before-self-mark", "after-mark"):
            open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8").write(
                json.dumps({"suggestion_reveal": setting}))
            loaded = settings_surface.load_settings(tmp)
            if loaded.get("suggestion_reveal") != setting:
                fail("suggestion_reveal must read back from settings")
            token = session_surface.render_suggestion(
                loaded.get("suggestion_reveal"))
            if token != "pending":
                fail("a suggestion must render only as the pending token, got %r"
                     % token)
            for glyph in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                          "/", "%", "✓", "✗", "✘", "✔", "☑", "☒"):
                if glyph in token:
                    fail("a suggestion must never render a %r glyph: %r"
                         % (glyph, token))

        settings_text = open(os.path.join(ROOT, "schemas",
                                          "settings.schema.json"),
                             encoding="utf-8").read()
        session_src = inspect.getsource(session_surface)
        runtime_src = inspect.getsource(runtime)
        for needle in ("auto_accept", "auto-accept", "autoaccept"):
            if needle in settings_text or needle in session_src \
                    or needle in runtime_src:
                fail("no auto-accept flag may exist (D-25), found %r" % needle)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    test_hint_offline_disabled_backend_typed_unavailable()
    test_hint_idempotent_second_call()
    test_hint_retry_lineage()
    test_cmd_hint_prints_json_exits_zero_and_parity()
    test_hint_no_genuine_wrong_response_generates_nothing()
    test_rubric_review_pending_suggestions_short_only()
    test_rubric_review_refuses_with_named_reason_and_no_write()
    test_cmd_mark_proposal_human_accept()
    test_cmd_mark_proposal_batch_all_or_nothing()
    test_suggestion_pending_token_only_and_no_auto_accept()
    print("model surface contract: ok (offline typed hint + authored, "
          "idempotency, retry lineage, CLI parity, no-wrong edge, pending "
          "rubric suggestions, named refusals, human-only proposal accept, "
          "all-or-nothing batch, pending-token-only + no auto-accept)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
