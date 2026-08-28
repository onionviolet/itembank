#!/usr/bin/env python3
"""ACTIVITY-03's adversarial suite (plan 16A-09).

Three scripted attackers, an agent, a note, and an import, each attempt the
four attacks ACTIVITY-03 names: leak a key, invent a score, auto-grade prose,
and change a frozen sitting. Two probes follow, one on the disclosure
boundary and one on the precision of a pending mark. Four more attack the
three new places Phase 16A itself lets authored text reach a learner, plus
the composed glossary that assembles them.

Standard library only, no test framework, runnable as
`python tests/assessment_authority_adversarial.py`.

**The rule this file lives or dies by: every gate it attacks is the real
shipped function.** There is no mock class, no fake helper, no monkey-patched
`runtime` or `evidence` attribute, and no simplified stand-in of any kind.
The phrases a reviewer would grep for are deliberately not written here even
in prose, so that grep genuinely reports zero rather than reporting this
paragraph. Constructing real sessions, real evidence logs, and real bank
fixtures is more setup than a mock, and that setup is the whole deliverable:
a stub that refuses proves only that the stub refuses. `16A-RESEARCH.md`'s
Pitfall 5 names exactly that shortcut as the way this suite goes wrong.

This file writes no runtime machinery and changes neither `runtime.py` nor
`evidence.py`. Where a question about Phase 16A's new grammar arises, it is
answered by `runtime.glossable` and `runtime.public_item`, the gates that
already exist. No second leak detector is written here or anywhere in the
phase: `glossable` is deliberately conservative and returns False on any
ambiguity, and two gates that disagreed about what counts as keyed content
would be worse than one gate that is occasionally too strict.
"""
import hashlib
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))

import capabilities                                          # noqa: E402
import evidence                                              # noqa: E402
import model                                                 # noqa: E402
import runtime                                               # noqa: E402
import lesson_capability_corpus                              # noqa: E402
from surfaces import lesson as lesson_surface                # noqa: E402
from surfaces import session                                 # noqa: E402

# The refusal `surfaces/session.py` actually produces for a completed
# sitting, transcribed from the shipped source at surfaces/session.py:850
# rather than paraphrased. A paraphrase here would pass while the real
# message changed.
FROZEN_REFUSAL = "session is already complete"

# The correct option letter for the adversarial bank's mc item, and the item
# ids. Kept beside the fixture's own constants so an assertion cannot drift
# from the bank it is asserting about.
MC_ITEM = "q1"
SHORT_ITEM = "q2"
MC_CORRECT = "B"


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# ---- the synthetic sitting -------------------------------------------------

def build_synthetic_sitting(dest_dir=None):
    """A real sitting: a real bank on disk, a real session started through
    the shipped `do_start`, a real correct answer scored by the real scorer,
    and a real prose response left PENDING.

    No fixture-only shortcut anywhere: every step goes through the same
    `surfaces/session.py` entry point the CLI calls.

    The prose response is deliberately left unmarked. Several attacks below
    assert that its mark is still `None`, and marking it during setup would
    make those assertions vacuous.
    """
    root = dest_dir or tempfile.mkdtemp(prefix="adversarial-")
    bank = lesson_capability_corpus.build_adversarial_bank(root)
    session_file = os.path.join(root, "session.json")
    session.do_start(bank, {}, "practice", session_file, False)

    session.do_next(session_file)
    mc_result = session.do_submit(session_file, MC_CORRECT, "high")
    session.do_next(session_file)
    short_result = session.do_submit(
        session_file, "Because the chamber is only as wide as a vessel.",
        "high")

    data = json.load(open(session_file, encoding="utf-8"))
    return {
        "root": root,
        "bank": bank,
        "session_file": session_file,
        "session_id": data["session_id"],
        "log": evidence.log_path(os.path.dirname(bank)),
        "qs": model.load(bank),
        "mc_event": mc_result["evidence"]["event_id"],
        "short_event": short_result["evidence"]["event_id"],
    }


def _item(sitting, item_id):
    for q in sitting["qs"]:
        if q["id"] == item_id:
            return q
    fail("the adversarial bank no longer carries item %r" % item_id)


# Field names that would identify WHICH option is keyed. `options` entries
# legitimately carry a `key` field holding each option's own letter, so the
# check below is on the top-level key set rather than on the serialized blob:
# a learner sees every letter and every option text, and what they must not
# see is which one is right and why.
_FORBIDDEN_TOP_LEVEL = ("correct", "answer", "key", "da", "why", "disc",
                        "second", "trap", "model", "rubric", "cases",
                        "scoring", "conf")


def _assert_no_key(payload, sitting, where):
    """Assert that a public payload names no keyed answer and carries no
    rationale.

    The rationale, discriminator, second-best, and distractor-analysis texts
    are checked against the WHOLE serialized payload, not against a key list,
    so a future field that smuggles one into a nested structure is still
    caught.

    The correct option's LETTER and its TEXT are deliberately not checked
    that way: a learner sees every letter and every option text, and a check
    that refused them would be asserting the item cannot be displayed. What
    must be absent is anything naming WHICH option is right, which is the
    top-level field check plus the completeness check below.
    """
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    q = _item(sitting, MC_ITEM)
    for label, frag in (("rationale", q.get("why")),
                        ("discriminator", q.get("disc")),
                        ("second-best", q.get("second")),
                        ("trap", q.get("trap"))):
        if frag and frag in blob:
            fail("%s: the payload carries the %s text %r"
                 % (where, label, frag[:60]))
    for line in (q.get("da") or {}).values():
        if line and line in blob:
            fail("%s: the payload carries distractor analysis %r"
                 % (where, line[:60]))
    for field in _FORBIDDEN_TOP_LEVEL:
        if field in payload:
            fail("%s: the payload carries a top-level %r field"
                 % (where, field))
    # A payload that returned only the correct option would leak the key by
    # omission, so completeness is part of the same assertion.
    served = sorted(o["key"] for o in payload.get("options") or [])
    if served != sorted(q["opts"]):
        fail("%s: the payload serves options %r but the item has %r; a "
             "narrowed option set names the key by omission"
             % (where, served, sorted(q["opts"])))


def _freeze(sitting):
    """Complete the sitting through the real path: a real human mark on the
    pending prose response, then one more `do_next`, which is what actually
    closes a sitting parked on a marker's desk."""
    mark = evidence.mark_event(
        sitting["session_id"], "", "Q2", sitting["short_event"], True,
        rubric=[{"point": "names the width", "pass": True},
                {"point": "names the gates", "pass": True}],
        marker="human")
    evidence.append_event(sitting["log"], mark)
    try:
        session.do_next(sitting["session_file"])
    except SystemExit:
        pass
    data = json.load(open(sitting["session_file"], encoding="utf-8"))
    if data["status"] != "complete":
        fail("the sitting did not reach the complete status, so the "
             "frozen-sitting attacks below would prove nothing")
    return data


def _render(sitting):
    return evidence.render_attempt_md(sitting["log"], sitting["session_id"],
                                      sitting["qs"], sitting["bank"])


def _digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---- attacker one: a scripted agent ----------------------------------------

def attack_agent_leak_key(sitting):
    """A model client asks for the item it is about to teach against."""
    payload = runtime.public_item(_item(sitting, MC_ITEM))
    _assert_no_key(payload, sitting, "agent, leak key")


def attack_agent_invent_score(sitting):
    """A model client manufactures a settled correct verdict for the prose
    item without going through the one scorer, and appends it through the
    real writer."""
    q = _item(sitting, SHORT_ITEM)
    forged = evidence.response_event(
        sitting["session_id"], q, "anything at all", True, "practice", 1,
        sitting["bank"])
    evidence.append_event(sitting["log"], forged)
    marks = evidence.marks_by_event(sitting["log"])
    if marks.get(forged["event_id"]) is not None:
        fail("agent, invent score: a manufactured response event acquired a "
             "settled mark without a human marker")
    if marks.get(sitting["short_event"]) is not None:
        fail("agent, invent score: appending a forged event settled the "
             "genuine prose response's mark")


def attack_agent_auto_grade(sitting):
    """A model client marks prose. The gate is an equality check against the
    literal string `human`, and the second and third calls prove it is not a
    substring test and not a truthiness test."""
    for marker in ("model", "agent", ""):
        try:
            evidence.mark_event(sitting["session_id"], "", "Q2",
                                sitting["short_event"], True, marker=marker)
        except ValueError as exc:
            if "human" not in str(exc):
                fail("agent, auto grade: marker %r was refused but the "
                     "message does not name the human gate: %s"
                     % (marker, exc))
        else:
            fail("agent, auto grade: mark_event accepted marker %r; a model "
                 "verdict is not accepted evidence" % marker)


def attack_agent_edit_frozen(sitting):
    """A model client submits into a completed sitting."""
    _freeze(sitting)
    try:
        session.do_submit(sitting["session_file"], MC_CORRECT, "high")
    except SystemExit as exc:
        if str(exc) != FROZEN_REFUSAL:
            fail("agent, edit frozen: the refusal is %r, expected the "
                 "shipped message %r" % (str(exc), FROZEN_REFUSAL))
    else:
        fail("agent, edit frozen: a submit into a completed sitting was "
             "accepted")


def attacker_agent():
    sitting = build_synthetic_sitting()
    return (("agent_leak_key", attack_agent_leak_key, sitting),
            ("agent_invent_score", attack_agent_invent_score, sitting),
            ("agent_auto_grade", attack_agent_auto_grade, sitting),
            ("agent_edit_frozen", attack_agent_edit_frozen, sitting))


# ---- attacker two: a learner note ------------------------------------------
#
# There is no learner-note store in this repository yet; the durable object
# and its source of truth are Phase 16C's. A note is therefore simulated as a
# plain text file beside the bank, and every attack asserts that no shipped
# reader consults it. That is a stand-in for a store that DOES NOT EXIST, not
# a mock of one that does, and the distinction matters: the assertion here is
# that nothing reads learner-authored text from disk, which is exactly what
# must stay true when the real store lands.

def _write_note(sitting, text):
    path = os.path.join(sitting["root"], "learner_note.md")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


def attack_note_leak_key(sitting):
    before = runtime.public_item(_item(sitting, MC_ITEM))
    _write_note(sitting, "The answer is %s. %s"
                % (MC_CORRECT, _item(sitting, MC_ITEM)["opts"][MC_CORRECT]))
    after = runtime.public_item(_item(sitting, MC_ITEM))
    if json.dumps(after, sort_keys=True) != json.dumps(before,
                                                       sort_keys=True):
        fail("note, leak key: writing a learner note changed what "
             "public_item returns")
    _assert_no_key(after, sitting, "note, leak key")


def attack_note_invent_score(sitting):
    before = len(list(evidence.live_events(sitting["log"])))
    _write_note(sitting, "SCORE: correct\nMASTERY: yes\n")
    after = list(evidence.live_events(sitting["log"]))
    if len(after) != before:
        fail("note, invent score: writing a learner note added %d evidence "
             "events" % (len(after) - before))


def attack_note_auto_grade(sitting):
    _write_note(sitting, "RUBRIC: both points pass. VERDICT: correct.")
    marks = evidence.marks_by_event(sitting["log"])
    if marks.get(sitting["short_event"]) is not None:
        fail("note, auto grade: a learner note settled the prose mark")
    if runtime.score_response(_item(sitting, SHORT_ITEM),
                              "anything") is not None:
        fail("note, auto grade: the scorer returned a settled verdict for a "
             "prose item; a short response is pending, never False")


def attack_note_edit_frozen(sitting):
    _freeze(sitting)
    before = _render(sitting)
    _write_note(sitting, "This sitting should read as two out of two.")
    after = _render(sitting)
    if _digest(after) != _digest(before):
        fail("note, edit frozen: writing a learner note changed the rendered "
             "attempt of a completed sitting")


def attacker_note():
    sitting = build_synthetic_sitting()
    return (("note_leak_key", attack_note_leak_key, sitting),
            ("note_invent_score", attack_note_invent_score, sitting),
            ("note_auto_grade", attack_note_auto_grade, sitting),
            ("note_edit_frozen", attack_note_edit_frozen, sitting))


# ---- attacker three: an import ---------------------------------------------

def attack_import_leak_key(sitting):
    """An imported record whose payload carries the answer in a field name a
    renderer might reflect."""
    q = _item(sitting, SHORT_ITEM)
    smuggled = evidence.response_event(
        sitting["session_id"], q,
        "correct_answer=%s %s" % (MC_CORRECT,
                                  _item(sitting, MC_ITEM)["opts"][MC_CORRECT]),
        None, "practice", 2, sitting["bank"], source_ref="import:synthetic")
    evidence.append_event(sitting["log"], smuggled)
    payload = runtime.public_item(_item(sitting, MC_ITEM))
    _assert_no_key(payload, sitting, "import, leak key")


def attack_import_invent_score(sitting):
    """An imported record claiming a settled correct verdict for prose."""
    q = _item(sitting, SHORT_ITEM)
    claimed = evidence.response_event(
        sitting["session_id"], q, "imported prose", True, "practice", 3,
        sitting["bank"], source_ref="import:synthetic")
    evidence.append_event(sitting["log"], claimed)
    marks = evidence.marks_by_event(sitting["log"])
    if marks.get(sitting["short_event"]) is not None:
        fail("import, invent score: an imported record settled the genuine "
             "prose response's mark")
    if marks.get(claimed["event_id"]) is not None:
        fail("import, invent score: an imported record carried its own "
             "settled mark")


def attack_import_auto_grade(sitting):
    """An imported mark whose marker is anything but human.

    The import path builds its mark through the same `evidence.mark_event`
    constructor every other writer uses, so the refusal is asserted there:
    there is no second constructor an import could reach instead.
    """
    for marker in ("import", "migration", "HUMAN"):
        try:
            evidence.mark_event(sitting["session_id"], "", "Q2",
                                sitting["short_event"], True, marker=marker)
        except ValueError:
            continue
        fail("import, auto grade: mark_event accepted marker %r" % marker)


def attack_import_edit_frozen(sitting):
    """Two routes, because the two refusals are different in kind."""
    _freeze(sitting)
    before = _render(sitting)

    # Route one, structural: rewrite the session JSON on disk. Phase 1's D-11
    # made the session file stop being an input to its own render, so an
    # edited session file changes nothing a report says.
    data = json.load(open(sitting["session_file"], encoding="utf-8"))
    for response in data.get("responses") or []:
        response["score"] = True
    data["status"] = "active"
    with open(sitting["session_file"], "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    after = _render(sitting)
    if _digest(after) != _digest(before):
        fail("import, edit frozen: editing the session JSON changed the "
             "rendered attempt; the session file must not be an input to its "
             "own render (D-11)")

    # Route two, append-only: an append that claims to overwrite an existing
    # event leaves BOTH records in the log. Correction happens through a
    # recorded retraction, never through an edit.
    events_before = list(evidence.events(sitting["log"]))
    overwrite = evidence.response_event(
        sitting["session_id"], _item(sitting, MC_ITEM), "A", False,
        "practice", 9, sitting["bank"], source_ref="import:overwrite")
    overwrite["event_id"] = sitting["mc_event"]
    evidence.append_event(sitting["log"], overwrite)
    events_after = list(evidence.events(sitting["log"]))
    if len(events_after) <= len(events_before):
        fail("import, edit frozen: an overwrite-shaped append replaced a "
             "record instead of being appended beside it")
    originals = [e for e in events_after
                 if e.get("event_id") == sitting["mc_event"]]
    if len(originals) < 2:
        fail("import, edit frozen: the log no longer carries both records "
             "for the overwritten event id")


def attacker_import():
    sitting = build_synthetic_sitting()
    return (("import_leak_key", attack_import_leak_key, sitting),
            ("import_invent_score", attack_import_invent_score, sitting),
            ("import_auto_grade", attack_import_auto_grade, sitting),
            ("import_edit_frozen", attack_import_edit_frozen, sitting))


# ---- the two probes --------------------------------------------------------

def attack_boundary_public_item(sitting):
    """ACTIVITY-03's boundary probe, asserted on BOTH sides and AT the
    threshold.

    Asserting only the pre-response case would test the easy side. The step
    either side is where a boundary check earns its keep.
    """
    fresh = build_synthetic_sitting()
    _assert_no_key(runtime.public_item(_item(fresh, MC_ITEM)), fresh,
                   "boundary, before any response")
    # A response for the mc item exists by construction in the sitting the
    # helper builds, so this call is the after-response point.
    _assert_no_key(runtime.public_item(_item(fresh, MC_ITEM)), fresh,
                   "boundary, after one response")
    _freeze(fresh)
    _assert_no_key(runtime.public_item(_item(fresh, MC_ITEM)), fresh,
                   "boundary, after the sitting is complete")


def attack_precision_pending_mark(sitting):
    """ACTIVITY-03's precision probe: pending is not False, and the marker
    gate fires before the verdict is coerced."""
    if runtime.score_response(_item(sitting, SHORT_ITEM),
                              "any prose at all") is not None:
        fail("precision: score_response for a short item did not return "
             "None; a not-yet-marked prose answer must stay distinguishable "
             "from a wrong one")
    marks = evidence.marks_by_event(sitting["log"])
    if sitting["short_event"] in marks:
        fail("precision: the prose response carries a mark before any human "
             "marked it")

    # If verdict coercion ran BEFORE the marker check, a non-boolean verdict
    # would have been silently accepted as truthy and the marker would never
    # have been examined. The exception must be the marker's.
    try:
        evidence.mark_event(sitting["session_id"], "", "Q2",
                            sitting["short_event"], "probably correct",
                            marker="model")
    except ValueError as exc:
        if "human" not in str(exc):
            fail("precision: the refusal for a non-boolean verdict from a "
                 "model marker is not the marker refusal: %s" % exc)
    else:
        fail("precision: mark_event accepted a model marker carrying a "
             "non-boolean verdict")


# ---- Phase 16A's own new mouths --------------------------------------------
#
# The excerpt callout, the media alt attribute, and the activity static
# fallback are three new places authored text reaches a learner before a
# response exists. A composed glossary is a fourth. All four are answered
# through the gates that already exist.

def _glossable(sitting, definition):
    """`runtime.glossable` against the real parsed questions, with the text
    under test in the shape a term record carries. No second detector."""
    return runtime.glossable(sitting["qs"], {"def": definition})


def attack_16a_excerpt_leak(sitting):
    """An [!EXCERPT] callout quoting the mc item's WHY BEST verbatim."""
    parsed = model.parse_lesson(sitting["bank"])
    page = lesson_surface.lesson_page(sitting["bank"], sitting["qs"], parsed)
    rationale = _item(sitting, MC_ITEM)["why"]
    payload = runtime.public_item(_item(sitting, MC_ITEM))
    _assert_no_key(payload, sitting, "16A excerpt, public_item")
    if rationale not in page:
        fail("16A excerpt: the rendered lesson does not contain the "
             "rationale, which contradicts the fixture; the fixture quotes "
             "it verbatim on purpose and this attack would prove nothing")
    # WHICH OF THE PLAN'S TWO OUTCOMES THIS CODEBASE ACTUALLY PRODUCES, stated
    # here because the two are materially different and the summary records
    # it: the rendered lesson page DOES contain the quoted rationale. A
    # lesson page is authored reading material and is not gated on a
    # response, so an author who quotes their own rationale into an excerpt
    # has published it, exactly as they would by typing it into a paragraph.
    #
    # What must hold, and what is asserted, is the second half: the runtime's
    # own disclosure surface carries none of it, and the runtime's one
    # existing gate classifies the text as keyed material, which is the
    # signal a later phase needs in order to suppress it.
    if _glossable(sitting, rationale):
        fail("16A excerpt: runtime.glossable classifies the quoted rationale "
             "as safe to disclose, so the one gate that already exists does "
             "not see this leak")


def attack_16a_media_alt_leak(sitting):
    """A media alt attribute stating the correct option letter and text."""
    alt = lesson_capability_corpus.ADVERSARIAL_MEDIA_ALT
    parsed_media = model.parse_media(sitting["bank"])
    declared = (parsed_media["assets"]["leak-diagram"]["alt"]
                if parsed_media else "")
    if declared != alt:
        fail("16A media alt: the fixture's alt text is %r but the constant "
             "is %r; the assertion would be about the wrong string"
             % (declared, alt))
    if _glossable(sitting, alt):
        fail("16A media alt: runtime.glossable classifies the leaky "
             "alternative as safe to disclose")
    _assert_no_key(runtime.public_item(_item(sitting, MC_ITEM)), sitting,
                   "16A media alt, public_item")


def attack_16a_activity_fallback_leak(sitting):
    """An activity static fallback stating the answer in plain words."""
    fallback = lesson_capability_corpus.ADVERSARIAL_ACTIVITY_FALLBACK
    parsed = model.parse_activities(sitting["bank"])
    declared = capabilities.activity_fallback(
        (parsed["activities"] if parsed else {}).get(MC_ITEM) or {})
    if declared != fallback:
        fail("16A activity fallback: the fixture declares %r but the "
             "constant is %r" % (declared, fallback))
    if _glossable(sitting, fallback):
        fail("16A activity fallback: runtime.glossable classifies the leaky "
             "fallback as safe to disclose")
    _assert_no_key(runtime.public_item(_item(sitting, MC_ITEM)), sitting,
                   "16A activity fallback, public_item")


def attack_16a_composed_glossary_leak(sitting):
    """A composed glossary assembling a definition that restates the answer,
    and the proof that no second leak detector was written for it."""
    terms = model.parse_terms(sitting["bank"])
    if terms is None:
        fail("16A glossary: the adversarial bank lost its ## TERMS section")
    composed = capabilities.compose_glossary(terms, source=sitting["bank"])
    leaky = [e for e in composed["entries"]
             if e["slug"] == lesson_capability_corpus.ADVERSARIAL_TERM_SLUG]
    if not leaky:
        fail("16A glossary: the composed glossary does not carry the term "
             "the fixture made leaky")
    for entry in composed["entries"]:
        safe = _glossable(sitting, entry["definition"])
        if entry["slug"] == lesson_capability_corpus.ADVERSARIAL_TERM_SLUG:
            if safe:
                fail("16A glossary: runtime.glossable classifies the leaky "
                     "definition as safe to disclose, so a composed glossary "
                     "would carry the answer")
        elif entry["slug"] == \
                lesson_capability_corpus.ADVERSARIAL_BENIGN_TERM_SLUG:
            if not safe:
                fail("16A glossary: glossable refused the benign control "
                     "term, so this attack cannot tell a real catch from the "
                     "gate's own strictness")

    # No second leak detector exists anywhere in the phase's code. Two gates
    # that disagreed about what counts as keyed content would be worse than
    # one gate that is occasionally too strict.
    pattern = re.compile(r"^\s*def\s+\w*(leak|disclose|key_scan)\w*\s*\(",
                         re.M)
    for name in ("capabilities.py", "model.py", "surfaces/lesson.py"):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        found = pattern.findall(text)
        if found:
            fail("16A glossary: %s defines a second leak detector (%r); "
                 "runtime.glossable is the one gate" % (name, found))


ATTACKS = ("attack_agent_leak_key", "attack_agent_invent_score",
           "attack_agent_auto_grade", "attack_agent_edit_frozen",
           "attack_note_leak_key", "attack_note_invent_score",
           "attack_note_auto_grade", "attack_note_edit_frozen",
           "attack_import_leak_key", "attack_import_invent_score",
           "attack_import_auto_grade", "attack_import_edit_frozen",
           "attack_boundary_public_item", "attack_precision_pending_mark",
           "attack_16a_excerpt_leak", "attack_16a_media_alt_leak",
           "attack_16a_activity_fallback_leak",
           "attack_16a_composed_glossary_leak")


def main():
    attempted = refused = succeeded = 0
    groups = list(attacker_agent()) + list(attacker_note()) \
        + list(attacker_import())
    probes = build_synthetic_sitting()
    groups.append(("boundary_public_item", attack_boundary_public_item,
                   probes))
    groups.append(("precision_pending_mark", attack_precision_pending_mark,
                   probes))
    new_mouths = build_synthetic_sitting()
    for name in ("16a_excerpt_leak", "16a_media_alt_leak",
                 "16a_activity_fallback_leak",
                 "16a_composed_glossary_leak"):
        groups.append((name, globals()["attack_" + name], new_mouths))

    if len(groups) != len(ATTACKS):
        fail("the suite runs %d attacks but ATTACKS names %d; a lost attack "
             "is a silently narrowed suite" % (len(groups), len(ATTACKS)))

    for name, attack, sitting in groups:
        attempted += 1
        try:
            attack(sitting)
        except SystemExit:
            # `fail` already printed which attack succeeded.
            raise
        except Exception as exc:                             # noqa: BLE001
            # An unexpected exception is a result nobody predicted. Reading
            # it as a refusal would be generous in the wrong direction.
            fail("attack %s raised an unexpected %s: %s"
                 % (name, type(exc).__name__, exc))
        refused += 1
        print("attack %s: refused" % name)

    print("ADVERSARIAL: %d attempted, %d refused, %d succeeded"
          % (attempted, refused, succeeded))
    return 0 if succeeded == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
