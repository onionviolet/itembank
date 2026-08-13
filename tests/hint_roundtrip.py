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
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
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


def q1_wrong():
    """A genuine wrong answer for q1 (correct is B)."""
    return "C"


def q1_right():
    return "B"


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
        runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "C",
                                              "mode": "drill"})
        fail("teaching_transition accepted a mode-carrying action")
    except SystemExit:
        pass


def test_practice_wrong_holds_and_unlocks_one_tier():
    s = session(mode="practice", items=(0,), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_wrong()})
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
    r1 = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_wrong()})
    s = r1["session"]
    r2 = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_wrong()})
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
    s = runtime.teaching_transition(s, q1(),
                                    {"kind": "submit", "answer": q1_wrong()})["session"]
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
    s = runtime.teaching_transition(s, q1(),
                                    {"kind": "submit", "answer": q1_wrong()})["session"]
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
    s = runtime.teaching_transition(s, q1(),
                                    {"kind": "submit", "answer": q1_wrong()})["session"]
    s = runtime.teaching_transition(s, q1(), {"kind": "hint"})["session"]
    s = runtime.teaching_transition(s, q1(), {"kind": "hint"})["session"]
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_right()})
    if r["action"] != "advance":
        fail("a correct retry must advance, got %r" % r["action"])
    if r["session"]["cursor"] != 1:
        fail("advance must move the cursor to the next item")
    if r.get("hint_tier") != 1:
        fail("correct retry must record the highest tier shown (1), got %r"
             % r.get("hint_tier"))


def test_practice_changed_answer_opens_new_attempt():
    s = session(mode="practice", items=(0,), cursor=0)
    s = runtime.teaching_transition(s, q1(),
                                    {"kind": "submit", "answer": "C"})["session"]
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "D"})
    if r["action"] != "hold":
        fail("a changed wrong answer must hold, got %r" % r["action"])
    rec = r["session"]["teaching_state"][item_key(q1())]
    if rec["attempt_count"] != 2:
        fail("a materially different response must open attempt 2, got %r"
             % rec["attempt_count"])
    if rec["last_genuine_canonical"] != "D":
        fail("last genuine canonical must follow the latest picked option")


def test_practice_tier_three_is_response_specific():
    s = session(mode="practice", items=(0,), cursor=0)
    s = runtime.teaching_transition(s, q1(),
                                    {"kind": "submit", "answer": "C"})["session"]
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
    canonical = runtime.canonical_response(q, "C")
    expected = (q.get("da") or {}).get("C", "")
    if tier["content"] != expected:
        fail("tier 3 content must be the picked option's analysis, got %r" % tier["content"])
    if r["hint"]["for_response"] != canonical:
        fail("tier 3 must name the canonical response it was resolved for")
    # A changed answer changes the tier-3 content but keeps previously shown tiers.
    s2 = runtime.teaching_transition(
        s, q1(), {"kind": "submit", "answer": "D"})["session"]
    r2 = runtime.teaching_transition(s2, q1(), {"kind": "hint"})
    if r2["hint"]["tier"]["index"] != 3:
        fail("after unlocking tier 3 twice, the next reveal must still be tier 3")
    expected_c = (q.get("da") or {}).get("D", "")
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


# ---- quick 260812-e2m D4: the authored tier carries learner-facing text ----
# `authored_hint` tier 0 returned the DERIVED lesson slug as its content, and
# the served assist panel printed that content verbatim, so an offline hint
# read "Authored hint / the-airway-step-by-step". Tier 5's content is the
# explain_payload dict, which the surface's string check rejected, so the
# authorized reveal rendered as nothing at all. Both are fixed in the runtime
# -- a surface that re-derived display text from an id would be a second
# place deciding what the learner reads.

def test_tier_zero_display_is_authored_prose_not_the_slug():
    """Test 1: the tier-0 payload's learner-facing text is the author-written
    lesson reference, and the derived slug appears nowhere in it."""
    q = q1()
    ref, slug = q.get("lesson_ref") or "", q.get("lesson_slug") or ""
    if not ref or not slug or ref == slug:
        fail("the fixture item must carry a lesson reference whose prose "
             "differs from its slug (ref=%r slug=%r)" % (ref, slug))
    t = runtime.authored_hint(q, 0, None)
    if t.get("display") != ref:
        fail("tier 0 must show the author-written lesson reference, got %r "
             "(the slug is a derived identifier for anchors and lookups, "
             "never learner-facing text)" % t.get("display"))
    if slug in (t.get("display") or ""):
        fail("the derived slug %r leaked into the learner-facing text %r"
             % (slug, t.get("display")))
    if t.get("slug") != slug:
        fail("the payload must still carry the slug on its own key so a "
             "linking surface has the anchor without re-deriving it: %r" % t)
    # Availability keys on the authored reference, not on the derived slug.
    bare = dict(q)
    bare["lesson_ref"] = ""
    if runtime.authored_hint(bare, 0, None)["available"]:
        fail("tier 0 must report unavailable when no lesson reference is "
             "authored")


def test_every_available_tier_carries_learner_text():
    """Test 2: every tier that reports itself available carries a non-empty
    learner-facing string -- including the reveal tier, whose content is a
    structured payload and which rendered as nothing at all."""
    for i in range(6):
        t = runtime.authored_hint(q1(), i, "B")
        if not t["available"]:
            fail("q1 tier %d must be available: %r" % (i, t))
        if not isinstance(t.get("display"), str) or not t["display"].strip():
            fail("tier %d reports available but carries no learner-facing "
                 "text: %r" % (i, t))
    reveal = runtime.authored_hint(q1(), 5, "B")
    if runtime.answer_text(q1()) not in reveal["display"]:
        fail("the authorized reveal must render the compact answer text "
             "through the runtime's own shaper: %r" % reveal["display"])


def test_unavailable_tier_carries_empty_learner_text():
    """Test 3: a tier that reports itself unavailable carries an empty
    learner-facing string, so the surface's locked empty state is what
    renders rather than a silent nothing."""
    t = runtime.authored_hint(q3(), 3, None)
    if t["available"]:
        fail("q3 tier 3 must be unavailable: %r" % t)
    if t.get("display") != "":
        fail("an unavailable tier must carry an empty learner-facing string, "
             "got %r" % t.get("display"))


def test_tier_selection_and_existing_payload_unchanged():
    """Test 4: tier selection is byte-for-byte unchanged, and every existing
    key on the payload still carries exactly what it carried before -- this
    task changes only how the already-chosen tier is worded."""
    q = q1()
    expected_content = {
        0: q.get("lesson_slug") or "",
        1: q.get("objective") or "",
        2: q.get("trap") or "",
        3: (q.get("da") or {}).get("B", ""),
        4: q.get("disc") or "",
    }
    for i, want in expected_content.items():
        t = runtime.authored_hint(q, i, "B")
        if t["content"] != want:
            fail("tier %d content changed: %r != %r" % (i, t["content"], want))
        if t["index"] != i or t["name"] != runtime.HINT_TIERS[i]["name"] \
                or t["label"] != runtime.HINT_TIERS[i]["label"]:
            fail("tier %d index/name/label changed: %r" % (i, t))
    if runtime.authored_hint(q, 5, "B")["content"] != \
            runtime.explain_payload(q, reveal=True):
        fail("the reveal tier's content key must stay the explain payload")
    # Selection: the ladder still unlocks and shows exactly the tiers it did.
    s = session(mode="practice", items=(0,), cursor=0)
    s = runtime.teaching_transition(
        s, q1(), {"kind": "submit", "answer": q1_wrong()})["session"]
    shown = []
    for _ in range(3):
        r = runtime.teaching_transition(s, q1(), {"kind": "hint"})
        shown.append(r["hint"]["tier"]["index"])
        s = r["session"]
    if shown != [0, 1, 2]:
        fail("tier selection changed: %r" % shown)


# ---- plan 14-03 Task 2: the ladder payload, D-09's boundary made concrete --
# `runtime.teaching_payload` is the only thing a browser or a CLI is allowed
# to know about the ladder. These fixtures assert what it carries and, much
# more importantly, what it does not: no undisclosed tier's text, no
# entitlement number, and no handle a request could name a tier with.

# Keys that must never appear anywhere in a served payload, at any depth: an
# undisclosed tier's body, and the two numbers a client could reason about
# into an entitlement.
FORBIDDEN_PAYLOAD_KEYS = ("content", "attempt_count", "highest_tier_unlocked",
                          "highest_tier_shown", "shown_tiers",
                          "last_genuine_canonical", "last_response_event_id")


def payload_keys(node, found=None):
    """Every dict key appearing anywhere in a payload, at any depth."""
    found = set() if found is None else found
    if isinstance(node, dict):
        for key, value in node.items():
            found.add(key)
            payload_keys(value, found)
    elif isinstance(node, list):
        for value in node:
            payload_keys(value, found)
    return found


def ladder_record(s, q):
    """The teaching record for `q` out of a session the transition returned."""
    return s.get("teaching_state", {}).get(runtime.teaching_key(q))


def held_then_shown(q, count):
    """A practice record for `q` after one genuine wrong attempt and `count`
    stumped reveals -- built by driving the real transition, never by hand, so
    the payload is asserted against the state the runtime actually produces.
    """
    s = session(mode="practice", items=(0,), cursor=0)
    s = runtime.teaching_transition(s, q, {"kind": "submit",
                                           "answer": q1_wrong()})["session"]
    for _ in range(count):
        s = runtime.teaching_transition(s, q, {"kind": "stumped"})["session"]
    return ladder_record(s, q)


def test_teaching_payload_never_leaks_an_unshown_tier():
    """T-14-09: serialize the payload at every ladder state from the first
    hold to the reveal, under both preview settings, and assert that every
    tier the learner has not been shown contributes no byte of its authored
    text -- and that no entitlement number or tier body key is present at all.
    """
    q = q1()
    texts = {i: runtime.authored_hint(q, i, q1_wrong())["display"]
             for i in range(6)}
    if not all(texts[i] for i in range(6)):
        fail("the fixture item must author all six tiers for this proof: %r"
             % texts)
    for count in range(0, 7):
        rec = held_then_shown(q, count)
        for preview in ("full", "next"):
            payload = runtime.teaching_payload(q, rec, "practice", preview)
            blob = json.dumps(payload, ensure_ascii=False)
            disclosed = set(e["index"] for e in payload["shown"])
            if disclosed != set(range(min(count, 6))):
                fail("after %d reveals the payload disclosed %r" %
                     (count, sorted(disclosed)))
            for i in range(6):
                if i in disclosed:
                    continue
                if texts[i] in blob:
                    fail("tier %d's authored text leaked into the payload at "
                         "%d reveals (%s preview): %r"
                         % (i, count, preview, texts[i][:60]))
            leaked = payload_keys(payload) & set(FORBIDDEN_PAYLOAD_KEYS)
            if leaked:
                fail("the payload carries forbidden key(s) %r at %d reveals"
                     % (sorted(leaked), count))
            for entry in payload["further_locked"]:
                if set(entry) != {"name", "header", "unlock_copy"}:
                    fail("a further-locked tier carries more than its header "
                         "and unlock sentence: %r" % entry)


def test_teaching_payload_locked_preview_full_and_next():
    """`hint_locked_preview: full` renders every remaining locked tier with
    its own unlock sentence; `next` renders only the next one plus the
    inherited count line and emits no further-locked entries at all. Both
    unlock-copy rows are the inherited LOCKED strings, carried as separate
    lines rather than one joined string.
    """
    q = q1()
    rec = held_then_shown(q, 0)
    full = runtime.teaching_payload(q, rec, "practice", "full")
    if full["available"] is not True or full["unavailable_reason"] is not None:
        fail("practice must run the ladder: %r" % full)
    if full["shown"] != []:
        fail("a wrong submission alone must show no tier: %r" % full["shown"])
    if full["entitled"] is not True or full["unlock_path"] != "attempt":
        fail("one genuine wrong attempt entitles the next tier: %r" % full)
    if full["next_locked"]["index"] != 0 or full["next_locked"]["name"] != "lesson":
        fail("the next locked tier is not tier 0: %r" % full["next_locked"])
    if full["next_locked"]["unlock_copy"] != [
            "Tier 0 unlocks after another attempt.",
            "Or unlock it now with \"I'm stumped\"."]:
        fail("the next-locked unlock copy drifted from the LOCKED rows: %r"
             % full["next_locked"]["unlock_copy"])
    if len(full["further_locked"]) != 5:
        fail("full preview must carry the other five locked tiers: %r"
             % full["further_locked"])
    if full["further_locked"][0] != {
            "name": "objective", "header": "TIER 1 · OBJECTIVE",
            "unlock_copy": ["Tier 1 unlocks after tier 0."]}:
        fail("a further-locked tier's shape drifted: %r"
             % full["further_locked"][0])

    nxt = runtime.teaching_payload(q, rec, "practice", "next")
    if nxt["further_locked"] != []:
        fail("next preview must emit no further-locked tiers: %r"
             % nxt["further_locked"])
    if nxt["next_locked"]["unlock_copy"][-1] != "5 more tiers after this one.":
        fail("next preview must append the inherited count line: %r"
             % nxt["next_locked"]["unlock_copy"])

    # At the reveal there is nothing left to lock, and no count line is
    # invented for zero remaining tiers.
    done = runtime.teaching_payload(q, held_then_shown(q, 6), "practice", "next")
    if done["next_locked"] is not None or done["further_locked"] != []:
        fail("an exhausted ladder must carry no locked cards: %r" % done)
    if done["exhausted"] is not True or len(done["shown"]) != 6:
        fail("the exhausted payload is wrong: %r"
             % {k: v for k, v in done.items() if k != "shown"})


def test_teaching_payload_tier_three_header_names_the_picked_option():
    """The tier-3 header names the option the learner actually picked, so the
    header is response-specific in exactly the way the tier's content already
    is -- and it is resolved here, never rebuilt by a client from an id.
    """
    q = q1()
    rec = held_then_shown(q, 4)
    payload = runtime.teaching_payload(q, rec, "practice")
    headers = [e["header"] for e in payload["shown"]]
    if headers != ["TIER 0 · LESSON", "TIER 1 · OBJECTIVE",
                   "TIER 2 · TRAP", "TIER 3 · RATIONALE FOR C"]:
        fail("the shown tier headers drifted: %r" % headers)
    if payload["next_locked"]["header"] != "TIER 4 · DISCRIMINATOR":
        fail("the next locked header is %r" % payload["next_locked"]["header"])
    # A short item has no picked option, so no letter is manufactured.
    bare = dict(runtime.new_teaching_record(), highest_tier_shown=3,
                highest_tier_unlocked=3)
    short = runtime.teaching_payload(q3(), bare, "practice")
    if short["shown"][3]["header"] != "TIER 3 · RATIONALE":
        fail("a tier-3 header with no picked option is %r"
             % short["shown"][3]["header"])


def test_teaching_payload_unavailable_shown_tier_says_so():
    """A tier the item never authored is disclosed as an unavailable slot at
    the moment it is shown (06-UI-SPEC 5.2), carrying the inherited sentence
    and its own availability flag -- which is what lets the renderer draw the
    unknown state rather than an empty card.
    """
    bare = dict(runtime.new_teaching_record(), highest_tier_shown=3,
                highest_tier_unlocked=3)
    payload = runtime.teaching_payload(q3(), bare, "practice")
    tier3 = payload["shown"][3]
    if tier3["available"] is not False:
        fail("q3 tier 3 must be shown as unavailable: %r" % tier3)
    if tier3["display"] != "This item has no authored picked-option rationale.":
        fail("an unavailable shown tier's sentence drifted: %r"
             % tier3["display"])
    if tier3["label"] != runtime.HINT_TIERS[3]["label"]:
        fail("a shown tier must carry its own label: %r" % tier3)


def test_teaching_payload_non_ladder_modes_are_absent_with_a_reason():
    """Drill, diagnostic and exam get the ladder as absent with the mode's own
    stated sentence and an empty `shown` -- and availability is derived from
    FEEDBACK_POLICIES, not from a mode list restated in the payload builder.
    """
    q = q1()
    rec = held_then_shown(q, 3)          # three tiers really are disclosed
    expected = {
        "drill": "Drill mode shows the answer straight away. The hint ladder "
                 "does not run here.",
        "diagnostic": "Diagnostic mode records your answers and shows nothing "
                      "until the sitting ends.",
        "exam": "Exam mode holds all feedback until this attempt has been "
                "marked.",
    }
    for mode, reason in expected.items():
        payload = runtime.teaching_payload(q, rec, mode)
        if payload["available"] is not False:
            fail("%s mode must not run the ladder: %r" % (mode, payload))
        if payload["unavailable_reason"] != reason:
            fail("%s mode's stated reason drifted: %r"
                 % (mode, payload["unavailable_reason"]))
        if payload["shown"] != [] or payload["next_locked"] is not None \
                or payload["further_locked"] != []:
            fail("%s mode leaked ladder content: %r" % (mode, payload))
        if payload["unlock_path"] is not None:
            fail("a ladder that does not run has no unlock path: %r"
                 % payload["unlock_path"])
        blob = json.dumps(payload, ensure_ascii=False)
        for i in range(6):
            text = runtime.authored_hint(q, i, q1_wrong())["display"]
            if text and text in blob:
                fail("%s mode leaked tier %d's authored text" % (mode, i))
    # Availability is read from the policy table, not from that mode list.
    for mode, policy in runtime.FEEDBACK_POLICIES.items():
        payload = runtime.teaching_payload(q, rec, mode)
        if payload["available"] != (policy["wrong"] == "hold"):
            fail("mode %r availability %r disagrees with its FEEDBACK_POLICIES "
                 "wrong entry %r" % (mode, payload["available"], policy["wrong"]))
        if not payload["available"] and not payload["unavailable_reason"]:
            fail("mode %r refuses the ladder with no stated reason" % mode)


def test_practice_reveal_then_advance():
    s = session(mode="practice", items=(0, 1), cursor=0)
    s = runtime.teaching_transition(s, q1(),
                                    {"kind": "submit", "answer": q1_wrong()})["session"]
    for i in range(6):
        r = runtime.teaching_transition(s, q1(), {"kind": "stumped"})
        if r["hint"]["tier"]["index"] != i:
            fail("stumped ladder must reveal tier %d, got %r" % (i, r["hint"]["tier"]))
        s = r["session"]
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_wrong()})
    if r["action"] != "advance":
        fail("after the reveal, the next action must advance, got %r" % r["action"])


def test_practice_last_item_completes():
    s = session(mode="practice", items=(0,), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_right()})
    if r["action"] != "complete":
        fail("correct answer on the last item must complete, got %r" % r["action"])
    if r["session"]["status"] != "complete" or r["session"]["cursor"] != 1:
        fail("complete must set status complete and advance past the last item")


def test_drill_reveals_and_advances():
    s = session(mode="drill", items=(0, 1), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_wrong()})
    if r["action"] != "advance":
        fail("drill must advance immediately, got %r" % r["action"])
    if r["session"]["cursor"] != 1:
        fail("drill advance must move the cursor")
    if not r.get("reveal"):
        fail("drill must return the immediate reveal payload")


def test_diagnostic_defers_until_completion():
    s = session(mode="diagnostic", items=(0, 1), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_wrong()})
    if r["action"] != "defer_feedback":
        fail("diagnostic must defer feedback, got %r" % r["action"])
    if r["session"]["cursor"] != 0:
        fail("diagnostic must not move the cursor before completion")
    if "hint" in r or "reveal" in r:
        fail("diagnostic must return no hint or reveal payload")


def test_exam_defers_until_accepted_mark():
    s = session(mode="exam", items=(0, 1), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_wrong()})
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
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": q1_wrong()})
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
    r = runtime.teaching_transition(upgraded, q1(),
                                    {"kind": "submit", "answer": q1_wrong()})
    if r["action"] != "hold":
        fail("an upgraded session must execute the teaching transition")


def test_evidence_reconciliation_repairs_crash_window():
    # Evidence already holds one wrong response + one shown hint for q1; the
    # session's teaching_state is stale (empty). reconcile via evidence_state
    # must repair the state without replaying disclosure.
    canon_b = runtime.canonical_response(q1(), "C")
    ev_response = evidence.response_event(
        "sess-reconcile", q1(), "C", False, "practice", 1, "lesson_bank.md",
        hint_tier=None)
    ev_hint = evidence.hint_event(
        "sess-reconcile", q1(), 0, True, "lesson", "authored", "attempt",
        response_event_id=ev_response["event_id"], response_canonical=canon_b,
        attempt_num=1, bank="lesson_bank.md")
    state = {item_key(q1()): [ev_response, ev_hint]}
    s = session(mode="practice", items=(0,), cursor=0)
    r = runtime.teaching_transition(s, q1(), {"kind": "submit", "answer": "C"},
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
    canon = runtime.canonical_response(q, "C")
    ev = evidence.hint_event("s", q, 1, True, "objective", "authored", "attempt",
                             response_event_id="r1", response_canonical=canon,
                             attempt_num=1, bank="lesson_bank.md")
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
                                  response_canonical=canon, attempt_num=1,
                                  bank="lesson_bank.md")
    if stumped["dedupe_key"] == ev["dedupe_key"]:
        fail("attempt and stumped unlock must never share a dedupe key")
    # Same tier+path+attempt replays to the same key (idempotent).
    again = evidence.hint_event("s", q, 1, True, "objective", "authored", "attempt",
                                response_event_id="r1", response_canonical=canon,
                                attempt_num=1, bank="lesson_bank.md")
    if again["dedupe_key"] != ev["dedupe_key"]:
        fail("an identical hint replay must reproduce the same dedupe key")


def test_response_event_v2_hint_tier_null_vs_zero():
    q = q1()
    ev_null = evidence.response_event("s", q, "C", False, "practice", 1,
                                      "lesson_bank.md", hint_tier=None)
    ev_zero = evidence.response_event("s", q, "C", False, "practice", 1,
                                      "lesson_bank.md", hint_tier=0)
    if ev_null["hint_tier"] is not None:
        fail("hint_tier=None must stay null (no ladder), got %r" % ev_null["hint_tier"])
    if ev_zero["hint_tier"] != 0:
        fail("hint_tier=0 must record zero (tier 0 shown), got %r" % ev_zero["hint_tier"])
    # Every v2 response event validates against the published contract.
    schema = load_schema(RESPONSE_SCHEMA)
    for ev in (ev_null, ev_zero):
        errs = schema_validate.validate(ev, schema)
        if errs:
            fail("v2 response event fails response.schema.json: %s" % errs[0])


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
        # A separate, fully-retracted item (a synthetic copy with its own
        # positional id) whose events must vanish from the derivation.
        q_unused = dict(qs()[0], id="q9", item_id="")

        # q_a: first-try correct.
        _write_event(log, evidence.response_event(
            sid, q_a, "B", True, "practice", 1, "lesson_bank.md", hint_tier=None))
        # q_b: two genuine wrong attempts, an attempt-unlocked hint, a
        # stumped-unlocked hint, then a correct retry at tier 1.
        ev_wrong1 = evidence.response_event(
            sid, q_b, ["A"], False, "practice", 1, "lesson_bank.md", hint_tier=None)
        ev_hint1 = evidence.hint_event(
            sid, q_b, 0, True, "lesson", "authored", "attempt",
            response_event_id=ev_wrong1["event_id"],
            response_canonical=evidence.idempotency_canon(q_b, ["A"]),
            attempt_num=1, bank="lesson_bank.md")
        ev_wrong2 = evidence.response_event(
            sid, q_b, ["C"], False, "practice", 2, "lesson_bank.md", hint_tier=0)
        ev_hint2 = evidence.hint_event(
            sid, q_b, 1, True, "objective", "authored", "stumped",
            response_event_id=ev_wrong2["event_id"],
            response_canonical=evidence.idempotency_canon(q_b, ["C"]),
            attempt_num=2, bank="lesson_bank.md")
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
            True, rubric=None)
        _write_event(log, ev_mark)

        # A retracted response (and its hint) must vanish from the derivation.
        q_unused = dict(qs()[0], id="q9", item_id="")
        ev_retract_target = evidence.response_event(
            sid, q_unused, "C", False, "practice", 1, "lesson_bank.md", hint_tier=None)
        ev_retract_hint = evidence.hint_event(
            sid, q_unused, 0, True, "lesson", "authored", "attempt",
            response_event_id=ev_retract_target["event_id"],
            response_canonical=evidence.idempotency_canon(q_unused, "C"),
            attempt_num=1, bank="lesson_bank.md")
        _write_event(log, ev_retract_target)
        _write_event(log, ev_retract_hint)
        _write_event(log, evidence.retraction_event(
            ev_retract_target["event_id"], reason="test retraction"))
        _write_event(log, evidence.retraction_event(
            ev_retract_hint["event_id"], reason="test retraction"))

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

        # Report shape validates against the extended report schema: the
        # session-summary variant accepts the teaching_outcomes block.
        report = {"schema_version": runtime.REPORT_VERSION, "session_id": sid,
                  "status": "active", "summary": {
                      "schema_version": runtime.REPORT_VERSION,
                      "auto_attempts": 4, "auto_correct": 2, "pending_manual": 1,
                      "objectives": {"emt:airway": {"attempts": 4, "correct": 2,
                                                    "pending": 1}},
                      "teaching_outcomes": rows}}
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
                                      attempt_num=1, bank="lesson_bank.md")
        _write_event(log, ev_resp)
        _write_event(log, ev_hint)
        if len(evidence.hint_events(log, sid)) != 1:
            fail("hint_events must find the one live hint")
        _write_event(log, evidence.retraction_event(ev_hint["event_id"],
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


# ---- plan 06-02: CLI, API and served-browser surfaces ----------------------

def _run(args, cwd=None):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"), *args],
                       capture_output=True, text=True, cwd=cwd or ROOT)
    return r


def _start_cli(bank, mode="practice", count=3, seed=0, out=None):
    args = ["start", bank, "--mode", mode, "--count", str(count),
            "--seed", str(seed)]
    if out:
        args += ["--out", out]
    r = _run(args)
    if r.returncode != 0:
        fail("itembank start failed: %s" % r.stderr[-400:])
    return json.loads(r.stdout)


def test_cli_hint_tracer():
    """06-02 Task 1 flow through the CLI, updated for plan 08-04: the CLI
    `hint` command is now the model-orchestrated diagnostic hint
    (--session/--retry), so the tracer drives wrong-submit hold, a typed
    offline hint plus its parent-linked retry, a correct retry advance, and
    a tier-aware report. The Phase 6 explicit tier-reveal path stays
    exercised by the runtime-transition tests above; plan 08-05 rewired the
    daemon's /api/hint route to the same model hint."""
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "lesson_bank.md")
        shutil.copyfile(BANK, bank)
        started = _start_cli(bank, mode="practice", count=2, seed=0,
                             out=os.path.join(tmp, "s.json"))
        session_file = started["session_file"]
        wrong = _run(["submit", session_file, "--answer", "C"])
        w = json.loads(wrong.stdout)
        if w["action"] != "hold" or w["score"] is not False:
            fail("CLI wrong submit must hold: %r" % w)
        if w["next"]["position"] != 0:
            fail("CLI hold must keep position 0")
        hint = json.loads(_run(["hint", "--session", session_file]).stdout)
        if hint["status"] != "unavailable":
            fail("CLI hint with the default backend must be typed unavailable: %r"
                 % hint)
        if not hint.get("interaction_id"):
            fail("CLI hint must mint an interaction id: %r" % hint)
        retry = json.loads(_run(["hint", "--session", session_file,
                                 "--retry"]).stdout)
        if retry["interaction_id"] == hint["interaction_id"]:
            fail("CLI hint --retry must mint a child interaction id: %r" % retry)
        right = json.loads(_run(["submit", session_file, "--answer", "B"]).stdout)
        if right["action"] != "advance" or right["score"] is not True:
            fail("CLI correct retry must advance: %r" % right)
        report = json.loads(_run(["report", session_file]).stdout)
        outcomes = report["summary"]["teaching_outcomes"]
        if any(row["outcome"] not in ("correct_after_tier", "correct_after_attempts")
               for row in outcomes.values()):
            fail("CLI report must carry tier-aware outcomes: %r" % outcomes)
        if report["summary"]["auto_attempts"] < 2:
            fail("CLI report auto_attempts must count the two submits")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _daemon(workdir):
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon",
         workdir, "--no-open", "--port", "0"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    import threading
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    base = None
    for _ in range(60):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            base = m.group(0)
            break
    return proc, base, lines


def _post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc


def test_api_hint_and_renderer_meta():
    """06-02 Task 2 (updated for plan 08-05): /api/hint returns the typed
    model-hint payload -- never the Phase 6 tier reveal -- and /api/submit
    accepts the Phase 6 action envelope plus an optional opaque renderer_meta
    string that is never persisted, echoed, or passed to policy;
    authority-shaped fields and oversized metadata are refused."""
    tmp = tempfile.mkdtemp()
    try:
        shutil.copyfile(BANK, os.path.join(tmp, "lesson_bank.md"))
        proc, base, lines = _daemon(tmp)
        if base is None:
            fail("daemon never printed a URL: %s" % "".join(lines))
        try:
            started = _post(base + "api/start",
                            {"bank": "lesson_bank", "count": 2, "seed": 0,
                             "mode": "practice"})
            sid = started["session_id"]
            wrong = _post(base + "api/submit",
                          {"session_id": sid, "action": {"kind": "submit",
                                                         "answer": "C"}})
            if wrong.get("action") != "hold":
                fail("API action-envelope submit must hold: %r" % wrong)
            hint = _post(base + "api/hint", {"session_id": sid})
            if hint.get("action") == "reveal_tier" or \
                    hint.get("status") != "unavailable":
                fail("API hint must return the typed model-hint payload "
                     "(plan 08-05 rewire), not the Phase 6 tier reveal: %r"
                     % hint)
            if not hint.get("interaction_id"):
                fail("API hint must mint an interaction id: %r" % hint)
            if hint.get("authored", {}).get("available") is not True:
                fail("API hint must carry the authored fallback for this "
                     "bank: %r" % hint)
            if "reason" in hint:
                fail("API hint must never carry a reason code: %r" % hint)

            meta_ok = _post(base + "api/submit",
                            {"session_id": sid,
                             "action": {"kind": "submit", "answer": "B"},
                             "renderer_meta": "browser-fragment-42"})
            if meta_ok.get("action") != "advance":
                fail("a valid renderer_meta must not change policy: %r" % meta_ok)

            session_file = started["session_file"]
            session_text = open(session_file, encoding="utf-8").read()
            log = os.path.join(tmp, "_evidence", "evidence.jsonl")
            log_text = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
            captured = "".join(lines)
            for needle in ("browser-fragment-42",):
                if needle in session_text or needle in log_text or needle in captured:
                    fail("renderer_meta must never be persisted, logged, or echoed")

            oversized = _post(base + "api/submit",
                              {"session_id": sid,
                               "action": {"kind": "submit", "answer": "C"},
                               "renderer_meta": "x" * 257})
            if not isinstance(oversized, urllib.error.HTTPError) or oversized.code != 400:
                fail("oversized renderer_meta must be refused with 400")
            nonstr = _post(base + "api/submit",
                           {"session_id": sid,
                            "action": {"kind": "submit", "answer": "C"},
                            "renderer_meta": {"structured": True}})
            if not isinstance(nonstr, urllib.error.HTTPError) or nonstr.code != 400:
                fail("structured renderer_meta must be refused with 400")
            authority = _post(base + "api/submit",
                              {"session_id": sid,
                               "action": {"kind": "submit", "answer": "C",
                                          "canvas_state": {"x": 1}}})
            if not isinstance(authority, urllib.error.HTTPError) or authority.code != 400:
                fail("canvas_state inside the action must be refused with 400")
            top_authority = _post(base + "api/submit",
                                  {"session_id": sid, "answer": "C",
                                   "mode": "drill"})
            if not isinstance(top_authority, urllib.error.HTTPError) or \
                    top_authority.code != 400:
                fail("a top-level mode field must be refused with 400")
            conflicting = _post(base + "api/submit",
                                {"session_id": sid, "answer": "C",
                                 "action": {"kind": "submit", "answer": "C"}})
            if not isinstance(conflicting, urllib.error.HTTPError) or \
                    conflicting.code != 400:
                fail("answer given both top-level and inside action must be refused")
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_served_browser_contract():
    """06-02 Task 3: the served page is a pure client of runtime actions --
    no local scoring, tier increment, mode policy, or cursor authority lives
    in its JavaScript, and diagnostic/exam responses leak no private content."""
    tmp = tempfile.mkdtemp()
    try:
        shutil.copyfile(BANK, os.path.join(tmp, "lesson_bank.md"))
        proc, base, lines = _daemon(tmp)
        if base is None:
            fail("daemon never printed a URL: %s" % "".join(lines))
        try:
            page = urllib.request.urlopen(base + "quiz/lesson_bank",
                                          timeout=5).read().decode("utf-8")
            for needle in ("/api/start", "/api/submit", "/api/hint",
                           "const BOOT ="):
                if needle not in page:
                    fail("served page missing %r" % needle)
            # Client authority markers: local scoring/canonicalization, the
            # bank's own key material, a local tier counter, or a mode
            # policy table would each violate the renderer-is-a-client rule.
            for banned in ("function canon(", "const KEY", "key = q.correct",
                           "tier++", "modePolicy", "FEEDBACK_POLICIES"):
                if banned in page:
                    fail("served page contains client authority %r" % banned)
            # Diagnostic and exam pre-release responses leak nothing.
            for mode in ("diagnostic", "exam"):
                started = _post(base + "api/start",
                                {"bank": "lesson_bank", "count": 2, "seed": 0,
                                 "mode": mode})
                sid = started["session_id"]
                r = _post(base + "api/submit",
                          {"session_id": sid, "answer": "C"})
                if r.get("action") != "defer_feedback":
                    fail("%s must defer feedback: %r" % (mode, r))
                if "explain" in r or r.get("score") is False:
                    fail("%s submit leaked feedback: %r" % (mode, r))
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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
    test_tier_zero_display_is_authored_prose_not_the_slug()
    test_every_available_tier_carries_learner_text()
    test_unavailable_tier_carries_empty_learner_text()
    test_tier_selection_and_existing_payload_unchanged()
    test_teaching_payload_never_leaks_an_unshown_tier()
    test_teaching_payload_locked_preview_full_and_next()
    test_teaching_payload_tier_three_header_names_the_picked_option()
    test_teaching_payload_unavailable_shown_tier_says_so()
    test_teaching_payload_non_ladder_modes_are_absent_with_a_reason()
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
    test_cli_hint_tracer()
    test_api_hint_and_renderer_meta()
    test_served_browser_contract()
    print("ok: hint roundtrip (transition, tiers, modes, evidence, outcomes, "
          "CLI/API/browser surfaces)")


if __name__ == "__main__":
    main()
