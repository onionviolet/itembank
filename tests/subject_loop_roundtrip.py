#!/usr/bin/env python3
"""Phase 9 (09-01) subject-invariant loop roundtrip.

Direct standard-library roundtrip script in the project's established shape:
`fail(msg)` and a non-zero exit on failure. It proves the thinnest production
subject-invariant slice: an EMT learner enters the already-built lesson and
practice-feedback loop under one selected, persisted data profile (09-CONTEXT
D-01, D-04, D-12, D-13, D-14).

It drives the real Phase 3 reader (`model.parse_lesson` +
`surfaces.lesson.render_markdown`), the real Phase 6 action adapter
(`surfaces.session.do_start`/`do_action`/`do_hint`), and the one evidence
writer (`evidence.append_event`/`session_events`) against a temporary
synthetic EMT bank. It also pins the conservative fallback, the mixed-subject
refusal, the disallowed-type refusal, the legacy-session one-time fill, and
the v3 session upgrade -- all without any subject-name branch in a surface.

The registry used here is the validated `subject_profiles` settings group
(plan 09-02): schema defaults when no itembank.json exists, checked-in
itembank.json otherwise, always through `subjects.load_registry()`.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evidence
import model
import runtime
import schema_validate
import subjects
from surfaces import session as session_surface
from surfaces import lesson as lesson_surface

SESSION_SCHEMA = os.path.join(ROOT, "schemas", "session.schema.json")

# The temporary synthetic EMT bank: fully invented teaching content, no real
# course material. Two mc items share the `emt:` objective namespace; the
# lesson carries prose, an ordered list, a bullet list, a semantic table and
# a fenced block whose content is TeX/markup shaped (so the math adapter must
# never touch it).
EMT_BANK = """# EMT scene loop (synthetic, Phase 9)

Fully invented teaching content for the subject-invariant loop roundtrip. It
is not derived from any real course, exam, or textbook.

## LESSON

### Managing the Scene

Scene management starts with a single question: is it safe to approach?

The priorities, in order:

1. Ensure scene safety.
2. Note the number of patients.
3. Call for additional resources.

Signs to record on arrival:

- Chief complaint
- Mental status
- Airway status

| Sign | What to check | First action |
| --- | --- | --- |
| Snoring | Airway patency | Head-tilt/chin-lift |
| No response | Mental status | Stimulus check |

```text
$not math$ and a **bold** marker and an _underscore_ stay inside a fence.
```

### Oxygen Delivery

Delivery method follows the patient's breathing effort.

Q1. Which first action addresses a snoring airway?   (difficulty: application)
[LESSON-REF: Managing the Scene]
[OBJECTIVE: emt:airway]

A) Suction the oropharynx
B) Head-tilt/chin-lift
C) Reposition the stretcher
D) Apply oxygen

CORRECT: B

WHY BEST: Head-tilt/chin-lift opens a tongue-obstructed airway; suction only
clears fluid, which is a different problem.

KEY DISCRIMINATOR: The action must open the airway itself, not treat a
finding elsewhere.

DISTRACTOR ANALYSIS:
- A) Suction clears fluid, not a tongue obstruction; this would be correct if the airway were blocked by secretions.
- B) Correct: the jaw and head position open the obstructed passage.
- C) Repositioning the stretcher does not open the airway; this would be correct if the question asked about spinal precautions.
- D) Oxygen is delivered after the airway is open; this would be correct if the question asked about ventilation.

TRAP: Choosing any intervention that happens after the airway is open.

CONFIDENCE: high

Q2. Which finding most clearly suggests the airway is at risk?   (difficulty: application)
[LESSON-REF: Managing the Scene]
[OBJECTIVE: emt:airway.opa]

A) Snoring respirations with a weak effort
B) Speaking in full sentences
C) Capillary refill of two seconds
D) Pulse oximetry of 98 percent

CORRECT: A

WHY BEST: Snoring with a weak effort is partial obstruction with failing
compensation -- the clearest sign that air movement is threatened.

KEY DISCRIMINATOR: The finding must describe air movement itself, not
perfusion or oxygenation readings.

DISTRACTOR ANALYSIS:
- A) Correct: snoring with a weak effort is obstruction in progress.
- B) Full sentences mean the airway is patent; this would be correct if the question asked which finding rules out obstruction.
- C) Capillary refill describes perfusion; this would be correct if the question asked about circulation.
- D) A normal reading does not describe air movement; this would be correct if the question asked about oxygenation only.

TRAP: Reaching for any abnormal vital sign instead of the finding that
describes air movement.

CONFIDENCE: high
"""

# A single-namespace bank whose subject is not in the registry (D-03): it must
# degrade to the conservative profile, not fail and not guess.
UNKNOWN_BANK = """# Water operations (synthetic, Phase 9)

## LESSON

### Residual Disinfection

Chlorine residual is measured after contact time.

Q1. When is residual measured?   (difficulty: application)
[OBJECTIVE: water:distribution.residual]

A) Before contact time
B) After contact time
C) At the intake
D) Never

CORRECT: B

WHY BEST: Residual is measured after contact time so disinfection has had a
chance to act.

KEY DISCRIMINATOR: The timing is about the contact period, not the sampling
location.

DISTRACTOR ANALYSIS:
- A) Before contact time no disinfection has happened; this would be correct if the question asked about raw water.
- B) Correct: after contact time the residual reflects real disinfection.
- C) The intake is upstream of treatment; this would be correct if the question asked where raw water enters.
- D) Residual is always measurable in principle; this would be correct if the question asked about unchlorinated supply.

TRAP: Confusing sampling location with contact timing.

CONFIDENCE: high
"""

# Two namespaces in one bank: ambiguous without an explicit profile id (D-04).
MIXED_BANK = """# Mixed synthetic bank (Phase 9)

## LESSON

### Mixed Subjects

One bank, two subject namespaces.

Q1. A mixed question.   (difficulty: application)
[OBJECTIVE: emt:airway]

A) Alpha
B) Beta
C) Gamma
D) Delta

CORRECT: A

WHY BEST: Alpha is the only option that fits.

KEY DISCRIMINATOR: None needed; synthetic.

DISTRACTOR ANALYSIS:
- A) Correct.
- B) Beta is close; this would be correct if the question asked for the second option.
- C) Gamma is unrelated; this would be correct if the question asked for the third option.
- D) Delta is unrelated; this would be correct if the question asked for the fourth option.

TRAP: None; synthetic.

CONFIDENCE: high

Q2. Another mixed question.   (difficulty: application)
[OBJECTIVE: math:derivatives]

A) Alpha
B) Beta
C) Gamma
D) Delta

CORRECT: B

WHY BEST: Beta is the only option that fits.

KEY DISCRIMINATOR: None needed; synthetic.

DISTRACTOR ANALYSIS:
- A) Alpha is close; this would be correct if the question asked for the first option.
- B) Correct.
- C) Gamma is unrelated; this would be correct if the question asked for the third option.
- D) Delta is unrelated; this would be correct if the question asked for the fourth option.

TRAP: None; synthetic.

CONFIDENCE: high
"""

# A bank carrying an item type the (temporary, narrowed) registry forbids.
DISALLOWED_BANK = """# Disallowed-type bank (synthetic, Phase 9)

## LESSON

### Scene Size-Up

Prose before the item.

Q1. Describe the scene.   (difficulty: application)
[OBJECTIVE: emt:scene]

A) Fine
B) Not fine

CORRECT: A

WHY BEST: The scene is described before any intervention.

KEY DISCRIMINATOR: None needed; synthetic.

DISTRACTOR ANALYSIS:
- A) Correct.
- B) Not fine would be correct if the scene were unsafe.

TRAP: None; synthetic.

CONFIDENCE: high

Q2. Write a short note.   (difficulty: recall)
[OBJECTIVE: emt:scene.note]
[TYPE: short]

Prompt: summarize the scene.

MODEL: none
"""


def fail(msg):
    print("FAIL: %s" % msg)
    sys.exit(1)


def write_bank(tmp, name, text):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def minimal_profile(pid="emt", allowed=None, verifier="runtime",
                    math=False, languages=None, layout="separate"):
    """A valid profile in the published 09-02 shape."""
    return {
        "id": pid,
        "version": subjects.PROFILE_SCHEMA_VERSION,
        "lesson": {"markdown": True, "tables": True, "math": math,
                   "runnable_languages": list(languages or []),
                   "lesson_layout": layout},
        "allowed_item_types": list(allowed or
                                   ["mc", "multi", "table", "dnd", "build",
                                    "short"]),
        "verifier": verifier,
    }


def default_registry():
    """The validated registry from settings defaults (no itembank.json):
    schema defaults merged and closed-shape validated."""
    d = tempfile.mkdtemp(prefix="subj_reg_")
    try:
        return subjects.load_registry(d)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_subject_ids_use_the_one_extractor():
    bank = write_bank(tempfile.gettempdir(), "sid_%s.md" % uuid.uuid4().hex,
                      EMT_BANK)
    plain_path = write_bank(tempfile.gettempdir(),
                            "sid_plain_%s.md" % uuid.uuid4().hex,
                            EMT_BANK.replace("[OBJECTIVE: emt:airway]",
                                             "[OBJECTIVE: airway]")
                            .replace("[OBJECTIVE: emt:airway.opa]",
                                     "[OBJECTIVE: airway.opa]"))
    try:
        qs = model.load(bank)
        ids = subjects.subject_ids(qs)
        if ids != ["emt"]:
            fail("subject_ids must be the distinct namespaced objectives via "
                 "evidence.subject_of, got %r" % ids)
        # An unnamespaced bank yields no subject ids, never a guessed one.
        plain = model.load(plain_path)
        if subjects.subject_ids(plain) != []:
            fail("unnamespaced objectives must yield no subject ids, got %r"
                 % subjects.subject_ids(plain))
    finally:
        for p in (bank, plain_path):
            if os.path.exists(p):
                os.remove(p)


def test_nremt_structure_rule_is_subject_scoped():
    """NREMT's published option counts are linted for EMT items and for no
    other subject (plan item 4, 2026-08-24).

    NREMT binds EMT: Multiple Choice is one correct of exactly four options,
    Multiple Response is two of five or three of six, always with exactly
    three incorrect. It has no authority over Math 1400 or CSCI 1100, so the
    same item under `math:` or with no namespace at all is checked against
    nothing. A linter that demanded four options everywhere would be wrong on
    two of the three subjects this workspace serves.

    Citations, including the authorities that say nothing at all about item
    writing, are in
    `.planning/research/2026-08-24-item-writing-standards.md`.
    """
    def findings(objective, opts, correct, kind="mc"):
        q = {"type": kind, "objective": objective,
             "opts": dict((chr(65 + i), "option %d" % i) for i in range(opts)),
             "correct": [chr(65 + i) for i in range(correct)]}
        return [f.code for f in model.structure_findings(q, "Q1")]

    if findings("emt:airway", 4, 1) != []:
        fail("a conformant EMT multiple-choice item was flagged")
    for opts in (3, 5):
        if findings("emt:airway", opts, 1) != ["item.structure_nonconformant"]:
            fail("an EMT multiple-choice item with %d options was not flagged"
                 % opts)
    for opts, correct in ((5, 2), (6, 3)):
        if findings("emt:airway", opts, correct, "multi") != []:
            fail("a conformant EMT multiple-response item (%d of %d) was "
                 "flagged" % (correct, opts))
    for opts, correct in ((6, 2), (5, 3), (4, 2)):
        if findings("emt:airway", opts, correct, "multi") != \
                ["item.structure_nonconformant"]:
            fail("an EMT multiple-response item with %d correct of %d options "
                 "was not flagged" % (correct, opts))

    # The whole point of the scoping: the same shapes elsewhere are silent.
    for objective in ("math:algebra.factoring", "cs:loops.for", "airway", ""):
        if findings(objective, 5, 1) or findings(objective, 6, 2, "multi"):
            fail("NREMT's option counts were enforced on %r, which NREMT does "
                 "not govern" % objective)

    if "item.structure_nonconformant" not in model.LINT_CODES:
        fail("the structural code is not declared in LINT_CODES")
    if set(subjects.STRUCTURE_RULES) != {"emt"}:
        fail("a subject gained structural rules without a cited authority "
             "and a test: %r" % sorted(subjects.STRUCTURE_RULES))


def test_validate_registry_rejects_bad_shapes():
    good = {"version": 1, "entries": {"emt": minimal_profile()}}
    if subjects.validate_registry(good) is not good:
        fail("a valid registry must pass through unchanged")
    # Duplicate ids (list form makes the duplicate real).
    dup = {"version": 1, "entries": [minimal_profile(), minimal_profile()]}
    try:
        subjects.validate_registry(dup)
        fail("duplicate profile ids must be rejected")
    except subjects.SubjectProfileError:
        pass
    # Extra keys.
    extra = {"version": 1, "entries": {"emt": dict(minimal_profile(),
                                                   bogus=True)}}
    try:
        subjects.validate_registry(extra)
        fail("extra profile keys must be rejected")
    except subjects.SubjectProfileError:
        pass
    # Wrong capability value type.
    badtype = {"version": 1,
               "entries": {"emt": dict(minimal_profile(),
                                       lesson=dict(minimal_profile()["lesson"],
                                                   math="yes"))}}
    try:
        subjects.validate_registry(badtype)
        fail("non-boolean capability must be rejected")
    except subjects.SubjectProfileError:
        pass
    # Unknown verifier id.
    badver = {"version": 1, "entries": {"emt": minimal_profile(
        verifier="bogus_verifier")}}
    try:
        subjects.validate_registry(badver)
        fail("unknown verifier ids must be rejected")
    except subjects.SubjectProfileError:
        pass
    # Duplicate allowed types and duplicate languages.
    duptype = {"version": 1, "entries": {"emt": minimal_profile(
        allowed=["mc", "mc"])}}
    try:
        subjects.validate_registry(duptype)
        fail("duplicate allowed item types must be rejected")
    except subjects.SubjectProfileError:
        pass
    duplang = {"version": 1, "entries": {"emt": minimal_profile(
        languages=["python", "python"])}}
    try:
        subjects.validate_registry(duplang)
        fail("duplicate runnable languages must be rejected")
    except subjects.SubjectProfileError:
        pass


def test_conservative_fallback_and_capability_report():
    # Single unknown namespace -> conservative default + named unsupported caps.
    qs = model.load(write_bank(tempfile.gettempdir(), "unk_%s.md"
                               % uuid.uuid4().hex, UNKNOWN_BANK))
    snap = subjects.select_profile(
        qs, default_registry(),
        requested_capabilities=("math", "runnable_languages:python"))
    if snap["subject_id"] != "":
        fail("unknown subject must record no subject id, got %r"
             % snap["subject_id"])
    if snap["profile"]["id"] != "default":
        fail("unknown subject must use the conservative default profile, got %r"
             % snap["profile"]["id"])
    if snap["profile"]["lesson"]["markdown"] is not True:
        fail("the conservative profile must keep readable markdown")
    if sorted(snap["unsupported_capabilities"]) != ["math",
                                                    "runnable_languages:python"]:
        fail("every requested unavailable capability must be named, got %r"
             % snap["unsupported_capabilities"])
    # Unnamespaced bank -> same conservative default, nothing requested.
    qs2 = model.load(write_bank(tempfile.gettempdir(), "plain_%s.md"
                                % uuid.uuid4().hex,
                                EMT_BANK.replace(
                                    "[OBJECTIVE: emt:airway]",
                                    "[OBJECTIVE: airway]")
                                .replace("[OBJECTIVE: emt:airway.opa]",
                                         "[OBJECTIVE: airway.opa]")))
    snap2 = subjects.select_profile(qs2, default_registry())
    if snap2["profile"]["id"] != "default" or snap2["unsupported_capabilities"]:
        fail("unnamespaced bank must get the default profile with no "
             "unsupported report, got %r" % snap2)


def test_mixed_subject_refusal_and_explicit_resolution():
    qs = model.load(write_bank(tempfile.gettempdir(), "mix_%s.md"
                               % uuid.uuid4().hex, MIXED_BANK))
    try:
        subjects.select_profile(qs, default_registry())
        fail("mixed namespaces without an explicit id must refuse")
    except subjects.SubjectProfileError as exc:
        msg = str(exc)
        if "emt" not in msg or "math" not in msg:
            fail("the refusal must name the conflicting subjects, got %r" % msg)
        if os.path.abspath(tempfile.gettempdir()) in msg:
            fail("the refusal must not disclose the bank path, got %r" % msg)
    snap = subjects.select_profile(qs, default_registry(), explicit_id="emt")
    if snap["subject_id"] != "emt" or snap["profile"]["id"] != "emt":
        fail("an explicit known id must resolve the ambiguous bank, got %r" % snap)
    try:
        subjects.select_profile(qs, default_registry(), explicit_id="nosuch")
        fail("an unknown explicit id must refuse")
    except subjects.SubjectProfileError:
        pass


def test_disallowed_item_type_refuses_before_write():
    reg = {"version": 1, "entries": {"emt": minimal_profile(allowed=["mc"])}}
    qs = model.load(write_bank(tempfile.gettempdir(), "dis_%s.md"
                               % uuid.uuid4().hex, DISALLOWED_BANK))
    try:
        subjects.select_profile(qs, reg)
        fail("an item type outside the profile allowlist must refuse")
    except subjects.SubjectProfileError as exc:
        msg = str(exc)
        if "emt" not in msg or "short" not in msg:
            fail("the refusal must name the profile id and the type, got %r"
                 % msg)


def test_emt_lesson_semantic_table(tmp):
    """The shared reader keeps headings, prose, lists and the table in source
    order, in a labelled focusable horizontal-scroll wrapper (D-12/D-13)."""
    bank = write_bank(tmp, "table_bank.md",
                      "# T\n\n## LESSON\n\n### Managing the Scene\n\n"
                      "Q1. Dummy.   (difficulty: recall)\n"
                      "[OBJECTIVE: emt:scene]\n\n"
                      "A) Alpha\nB) Beta\n\nCORRECT: A\n")
    qs = model.load(bank)
    ctx = lesson_surface._reader_context(bank, qs)
    body = ("Scene management starts with one question.\n\n"
            "- Chief complaint\n- Airway status\n\n"
            "| Sign | What to check | First action |\n"
            "| --- | --- | --- |\n"
            "| Snoring | Airway patency | Head-tilt/chin-lift |\n"
            "| No response | Mental status | Stimulus check |\n\n"
            "```text\n$not math$ and **bold** stay inside a fence.\n```\n")
    h = lesson_surface.render_markdown("### Managing the Scene\n\n%s" % body,
                                       ctx)
    if ('<div class="scroll lesson-table-scroll" tabindex="0" '
            'role="region" aria-label="Managing the Scene"><table>') not in h:
        fail("table must sit in the labelled focusable overflow wrapper: %r" % h)
    if "<thead><tr><th scope=\"col\">Sign</th>" not in h:
        fail("header cells must carry scope=col: %r" % h)
    if "<tbody><tr><td>Snoring</td>" not in h:
        fail("body cells must remain native td rows: %r" % h)
    idx_h2 = h.index("<h2>Managing the Scene</h2>")
    idx_p = h.index("<p>Scene management")
    idx_ul = h.index("<ul><li>Chief complaint</li><li>Airway status</li></ul>")
    idx_table = h.index("<table>")
    idx_pre = h.index("<pre><code class=\"language-text\">")
    if not (idx_h2 < idx_p < idx_ul < idx_table < idx_pre):
        fail("lesson source order must survive rendering: %r" % h)
    if "$not math$" not in h or "<strong>bold</strong>" in h:
        fail("fenced content must stay escaped and untouched: %r" % h)
    # The narrow-width contract is CSS-owned: wrapper is 100%-wide inside its
    # overflow container, and long cells wrap rather than widen the page.
    if ".lesson-table-scroll{max-width:100%}" not in lesson_surface.LESSON_CSS:
        fail("lesson CSS must cap the table wrapper at 100%% width")
    if "overflow-wrap:anywhere" not in lesson_surface.LESSON_CSS:
        fail("lesson CSS must allow long table cells to wrap")
    # A plain profile render keeps the same shared wrapper (no EMT-only path).
    plain = lesson_surface.render_markdown("### T\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n")
    if "lesson-table-scroll" not in plain or '<th scope="col">a</th>' not in plain:
        fail("the shared reader must emit the same semantic table for any bank: "
             "%r" % plain)


def test_emt_learner_loop_with_persisted_profile(tmp):
    bank = write_bank(tmp, "emt_loop_bank.md", EMT_BANK)
    qs = model.load(bank)
    errors, _ = model.lint(qs)
    if errors:
        fail("the synthetic EMT bank must lint clean, got %r" % errors)
    out = os.path.join(tmp, "s.json")
    res = session_surface.do_start(bank, {"count": 2}, "practice", out,
                                   force=False)
    # 1. The session persists a complete EMT snapshot and the view exposes it.
    data = json.load(open(out, encoding="utf-8"))
    sp = data.get("subject_profile")
    if not sp:
        fail("a new session must persist the resolved subject profile")
    if sp["subject_id"] != "emt" or sp["profile"]["id"] != "emt":
        fail("the bank's emt namespace must select the EMT profile, got %r" % sp)
    if sp["profile"]["verifier"] != "runtime":
        fail("EMT uses the shared runtime verifier, got %r" % sp)
    if sp["registry_version"] != subjects.load_registry(tmp)["version"]:
        fail("the snapshot must record the registry version, got %r" % sp)
    if res.get("subject_id") != "emt":
        fail("session_view must expose the subject id, got %r" % res.get("subject_id"))
    view_sp = res.get("subject_profile") or {}
    if view_sp.get("id") != "emt" or view_sp.get("verifier") != "runtime":
        fail("session_view must expose the profile metadata, got %r" % view_sp)
    if "mc" not in (view_sp.get("allowed_item_types") or []):
        fail("session_view must expose the allowed item types, got %r" % view_sp)

    # 2. The v3 session validates against the published schema.
    errs = schema_validate.validate(data, json.load(open(SESSION_SCHEMA,
                                                         encoding="utf-8")))
    if errs:
        fail("the written session must validate against session.schema.json: "
             "%r" % errs)

    # 3. Wrong genuine response -> authored hint -> correct retry through the
    #    existing Phase 6 adapter and one evidence writer.
    r1 = session_surface.do_action(out, {"kind": "submit", "answer": "A"})
    if r1["action"] != "hold":
        fail("a wrong practice response must hold the cursor, got %r" % r1)
    if r1["score"] is not False:
        fail("the wrong response must score False, got %r" % r1)
    r2 = session_surface.do_action(out, {"kind": "hint"})
    if r2["action"] != "reveal_tier":
        fail("the hint request must reveal a tier, got %r" % r2)
    if (r2.get("hint") or {}).get("tier", {}).get("index") != 0:
        fail("the first hint must be authored tier 0, got %r" % r2)
    r3 = session_surface.do_action(out, {"kind": "submit", "answer": "B"})
    if r3["action"] != "advance":
        fail("a correct retry must advance, got %r" % r3)
    if r3["score"] is not True:
        fail("the correct retry must score True, got %r" % r3)

    log = evidence.log_path(tmp)
    responses = evidence.session_events(log, data["session_id"])
    hints = evidence.hint_events(log, data["session_id"])
    if len(responses) != 2:
        fail("the loop must record exactly two response events, got %d" %
             len(responses))
    if len(hints) != 1:
        fail("the loop must record exactly one hint event, got %d" % len(hints))
    if responses[0]["score"] is not False or responses[1]["score"] is not True:
        fail("response events must carry the real scores, got %r" % responses)
    if responses[0]["subject"] != "emt":
        fail("response events must carry the namespaced subject via the one "
             "extractor, got %r" % responses[0]["subject"])
    if hints[0]["tier_index"] != 0 or hints[0]["source"] != "authored":
        fail("the hint event must record authored tier 0, got %r" % hints[0])
    if hints[0]["unlock_path"] != "attempt":
        fail("the hint must unlock via the attempt path, got %r" % hints[0])

    # 4. Resume drift: registry changes after start cannot change the stored
    #    snapshot (D-04) -- the session keeps interpreting under the profile
    #    it was created with, even when the settings file next to the bank is
    #    edited to enable a capability the session does not have.
    from surfaces import settings as settings_surface
    cfg = settings_surface.load_settings(tmp)
    cfg["subject_profiles"]["entries"]["emt"]["lesson"]["math"] = True
    settings_surface.write_settings(tmp, cfg)
    try:
        session_surface.do_action(out, {"kind": "submit", "answer": "B"})
    finally:
        os.remove(os.path.join(tmp, "itembank.json"))
    again = json.load(open(out, encoding="utf-8"))
    if again["subject_profile"]["subject_id"] != "emt":
        fail("resume must keep the stored subject id, got %r" %
             again["subject_profile"])
    if again["subject_profile"]["profile"]["lesson"]["math"] is not False:
        fail("resume must consume the stored snapshot, not the live registry, "
             "got %r" % again["subject_profile"])
    # The stored snapshot is unchanged byte-for-byte.
    if again["subject_profile"] != data["subject_profile"]:
        fail("resume must not rewrite the persisted snapshot, got %r" %
             again["subject_profile"])


def test_legacy_session_fills_snapshot_once(tmp):
    bank = write_bank(tmp, "emt_legacy_bank.md", EMT_BANK)
    qs = model.load(bank)
    # A v2-shaped session (written before Phase 9) upgrades on read with a
    # null slot, then the first action resolves and persists once.
    legacy = {
        "schema_version": 2,
        "session_id": uuid.uuid4().hex,
        "bank": os.path.abspath(bank),
        "items": [0],
        "cursor": 0,
        "responses": [],
        "status": "active",
        "mode": "practice",
        "objective": "",
        "seed": 0,
        "teaching_state": {},
    }
    legacy_path = os.path.join(tmp, "legacy.json")
    runtime.write_session(legacy_path, legacy)
    up = runtime.read_session(legacy_path)
    if up["schema_version"] != 3:
        fail("v2 sessions must upgrade to v3, got %r" % up["schema_version"])
    if up.get("subject_profile") is not None:
        fail("the v2 upgrade must leave the profile slot null, got %r" %
             up.get("subject_profile"))
    session_surface.do_action(legacy_path, {"kind": "submit", "answer": "A"})
    filled = json.load(open(legacy_path, encoding="utf-8"))
    if filled["subject_profile"]["subject_id"] != "emt":
        fail("the first action on a legacy session must fill the snapshot once, "
             "got %r" % filled.get("subject_profile"))
    errs = schema_validate.validate(filled, json.load(open(SESSION_SCHEMA,
                                                           encoding="utf-8")))
    if errs:
        fail("the filled legacy session must validate against the schema: %r"
             % errs)
    # A null slot also validates (upgrade state is documented and legal).
    errs = schema_validate.validate(up, json.load(open(SESSION_SCHEMA,
                                                       encoding="utf-8")))
    if errs:
        fail("the null upgrade slot must validate against the schema: %r" % errs)


def test_no_subject_dispatch_in_surfaces():
    """An AST guard (D-02): no learner-facing surface may branch on the
    shipped subject ids, and no root application module may branch on emt/cs
    (`math` is also a capability token inside subjects.py's capability check,
    so root modules are checked for emt/cs only, while surfaces are checked
    for all three). The guard is precise: it flags only if/match nodes that
    COMPARE against a subject-id string literal -- an error message or
    docstring that merely mentions an id is not dispatch. Profile data lives
    in JSON/settings; surfaces select, they never dispatch."""
    import ast

    def compares_id(node, ids):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Compare):
                operands = ([sub.left] if not isinstance(sub.left, ast.Constant)
                            else []) + list(sub.comparators)
                for op in operands:
                    if isinstance(op, ast.Constant) and \
                            isinstance(op.value, str) and op.value in ids:
                        return True
            elif isinstance(sub, ast.Match):
                for case in sub.cases:
                    pat = case.pattern
                    if isinstance(pat, ast.MatchValue) and \
                            isinstance(pat.value, ast.Constant) and \
                            isinstance(pat.value.value, str) and \
                            pat.value.value in ids:
                        return True
        return False

    roots = [os.path.join(ROOT, "surfaces")]
    roots += [os.path.join(ROOT, f) for f in
              ("itembank.py", "model.py", "runtime.py", "evidence.py",
               "selection.py", "server.py", "schema_validate.py",
               "resources.py", "subjects.py", "build.py", "model_adapter.py",
               "tier_gate.py")]
    for root in roots:
        if os.path.isdir(root):
            files = [os.path.join(root, f) for f in os.listdir(root)
                     if f.endswith(".py")]
        elif os.path.isfile(root):
            files = [root]
        else:
            continue
        for path in files:
            src = open(path, encoding="utf-8").read()
            tree = ast.parse(src, path)
            ids = ("emt", "cs") if root != os.path.join(ROOT, "surfaces") \
                else ("emt", "math", "cs")
            for node in ast.walk(tree):
                if not isinstance(node, (ast.If, ast.Match)):
                    continue
                if compares_id(node, ids):
                    fail("subject-name dispatch in %s: %r"
                         % (path, ast.get_source_segment(src, node) or ""))


def test_settings_registry_parity():
    """Schema defaults, a missing settings file, and the checked-in
    itembank.json expose structurally identical EMT/Math/CS registries, and
    every entry carries the lesson_layout enum (separate|inline) folded from
    Phase 3.1 D-04 (EMT/Math separate, CS inline)."""
    import json as _json
    from surfaces import settings as settings_surface
    missing = tempfile.mkdtemp(prefix="subj_parity_")
    try:
        reg_missing = subjects.load_registry(missing)
        reg_root = subjects.load_registry(os.path.join(ROOT, "fixtures"))
        schema = _json.load(open(os.path.join(ROOT, "schemas",
                                              "settings.schema.json"),
                                 encoding="utf-8"))
        shipped = _json.load(open(os.path.join(ROOT, "itembank.json"),
                                  encoding="utf-8"))
        if reg_missing != reg_root:
            fail("missing-file registry and checked-in registry differ: %r vs %r"
                 % (reg_missing, reg_root))
        if shipped["subject_profiles"] != schema["properties"]["subject_profiles"]["default"]:
            fail("itembank.json subject_profiles must mirror the schema default")
        for pid, expect_layout in (("emt", "separate"), ("math", "separate"),
                                   ("cs", "inline")):
            lesson = reg_missing["entries"][pid]["lesson"]
            if lesson["lesson_layout"] != expect_layout:
                fail("%s must default lesson_layout %r, got %r"
                     % (pid, expect_layout, lesson["lesson_layout"]))
        if reg_missing["entries"]["cs"]["verifier"] != "check":
            fail("CS must use Phase 5's check verifier id, got %r"
                 % reg_missing["entries"]["cs"]["verifier"])
        if "check" not in reg_missing["entries"]["cs"]["allowed_item_types"]:
            fail("only CS permits the check item type")
        if "check" in reg_missing["entries"]["emt"]["allowed_item_types"]:
            fail("EMT must not permit the check item type")
        if reg_missing["entries"]["cs"]["lesson"]["runnable_languages"] != ["python"]:
            fail("CS must enable runnable python, got %r"
                 % reg_missing["entries"]["cs"]["lesson"]["runnable_languages"])
    finally:
        shutil.rmtree(missing, ignore_errors=True)


def test_load_registry_rejects_malformed():
    """A malformed registry fails before selection through the public loader:
    schema-caught shape errors surface as named settings exits, and
    closed-shape registry errors (e.g. a fourth entry with an unsupported
    verifier, which the open entries object cannot see) surface as
    SubjectProfileError."""
    from surfaces import settings as settings_surface
    d = tempfile.mkdtemp(prefix="subj_bad_")
    try:
        # Unknown verifier on a KNOWN entry -> settings schema enum -> exit.
        cfg = settings_surface.load_settings(d)
        cfg["subject_profiles"]["entries"]["emt"]["verifier"] = "bogus_verifier"
        settings_surface.write_settings(d, cfg)
        try:
            subjects.load_registry(d)
            fail("an unsupported verifier on a known entry must fail")
        except SystemExit:
            pass
        os.remove(os.path.join(d, "itembank.json"))
        # Extra key on a known entry -> closed profile -> settings exit.
        cfg = settings_surface.load_settings(d)
        cfg["subject_profiles"]["entries"]["emt"]["bogus"] = True
        settings_surface.write_settings(d, cfg)
        try:
            subjects.load_registry(d)
            fail("an extra profile key on a known entry must fail")
        except SystemExit:
            pass
        os.remove(os.path.join(d, "itembank.json"))
        # An unknown FOURTH entry bypasses the open entries schema but must
        # still fail closed-shape validation in validate_registry.
        cfg = settings_surface.load_settings(d)
        cfg["subject_profiles"]["entries"]["fourth"] = {
            "id": "fourth", "version": 1,
            "lesson": {"markdown": True, "tables": True, "math": False,
                       "runnable_languages": [], "lesson_layout": "separate"},
            "allowed_item_types": ["mc"], "verifier": "bogus_verifier"}
        settings_surface.write_settings(d, cfg)
        try:
            subjects.load_registry(d)
            fail("an unknown verifier on a fourth entry must fail validation")
        except subjects.SubjectProfileError:
            pass
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_fourth_profile_is_configuration_only(tmp):
    """LOOP-05 / D-15: appending a valid fourth entry to temporary settings
    resolves through the same public loader and selector with no production
    edit, and its snapshot shape matches the shipped profiles exactly."""
    from surfaces import settings as settings_surface
    cfg = settings_surface.load_settings(tmp)
    cfg["subject_profiles"]["entries"]["fourth"] = {
        "id": "fourth", "version": 1,
        "lesson": {"markdown": True, "tables": True, "math": False,
                   "runnable_languages": [], "lesson_layout": "separate"},
        "allowed_item_types": ["mc", "multi", "table", "dnd", "build", "short"],
        "verifier": "runtime"}
    settings_surface.write_settings(tmp, cfg)
    reg = subjects.load_registry(tmp)
    if "fourth" not in reg["entries"]:
        fail("the fourth entry must load through public configuration")
    bank = write_bank(tmp, "fourth_bank.md",
                      "# Fourth synthetic bank (Phase 9)\n\n"
                      "## LESSON\n\n### Fourth Subject\n\n"
                      "Q1. A fourth-subject item.   (difficulty: recall)\n"
                      "[OBJECTIVE: fourth:magic]\n"
                      "[LESSON-REF: Fourth Subject]\n\n"
                      "A) Alpha\nB) Beta\nC) Gamma\n\nCORRECT: A\n\n"
                      "WHY BEST: Alpha is the only option that fits.\n\n"
                      "KEY DISCRIMINATOR: None; synthetic.\n\n"
                      "SECOND-BEST: Beta, if the question asked for the "
                      "runner-up.\n\n"
                      "DISTRACTOR ANALYSIS:\n"
                      "- A) Correct.\n"
                      "- B) Beta would be correct if the question asked for it.\n"
                      "- C) Gamma would be correct if the question asked for the "
                      "third option.\n\n"
                      "TRAP: None; synthetic.\n\n"
                      "CONFIDENCE: high\n")
    qs = model.load(bank)
    snap = subjects.select_profile(qs, reg)
    if snap["subject_id"] != "fourth" or snap["profile"]["id"] != "fourth":
        fail("the fourth profile must resolve from its namespace, got %r" % snap)
    emt = reg["entries"]["emt"]
    if set(snap["profile"]) != set(emt):
        fail("the fourth snapshot must carry the same keys as shipped profiles")
    snap2 = subjects.select_profile(qs, reg, requested_capabilities=("math",))
    if snap2["unsupported_capabilities"] != ["math"]:
        fail("requested unavailable capabilities must stay explicit for the "
             "fourth profile, got %r" % snap2["unsupported_capabilities"])
    # The shared driver selects it too: do_start loads the registry from the
    # bank's own directory, where the temporary settings file lives.
    out = os.path.join(tmp, "fourth_s.json")
    res = session_surface.do_start(bank, {"count": 1}, "practice", out,
                                   force=False)
    if res.get("subject_id") != "fourth":
        fail("do_start must resolve the fourth profile from bank-adjacent "
             "settings, got %r" % res.get("subject_id"))
    data = json.load(open(out, encoding="utf-8"))
    if data["subject_profile"]["subject_id"] != "fourth":
        fail("the fourth sitting must persist its profile snapshot")


def _start_daemon(workdir):
    """Launch `itembank daemon <workdir> --no-open --port 0` and return
    `(proc, url)` once the banner URL has been scraped."""
    args = [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon",
            workdir, "--no-open", "--port", "0"]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    lines = []

    def drain():
        for line in proc.stdout:
            lines.append(line)

    threading.Thread(target=drain, daemon=True).start()
    url = None
    for _ in range(300):
        for line in lines:
            m = re.search(r"http://127\.0\.0\.1:\d+/", line)
            if m:
                url = m.group(0).rstrip("/")
                break
        if url:
            break
        if proc.poll() is not None:
            break
        time.sleep(0.05)
    if not url:
        proc.kill()
        fail("daemon did not print a URL; output: " + "".join(lines))
    return proc, url


def _get(url):
    with urllib.request.urlopen(url, timeout=10) as res:
        return res.status, res.read().decode("utf-8")


def _post(url, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(body)
        except ValueError:
            return exc.code, body


def _evidence_files(workdir):
    out = []
    for dp, _, fns in os.walk(workdir):
        for fn in fns:
            if fn.startswith("session_") and fn.endswith(".json"):
                out.append(os.path.join(dp, fn))
            if fn.endswith(".jsonl"):
                out.append(os.path.join(dp, fn))
    return out


# --- plan 09-05 Task 3: the four-profile common-loop matrix -----------------
# The shipped subject fixtures live in fixtures/subject_loop_*.md; the fourth
# profile is configuration-only (09-02), driven here with a temporary entry.
EMT_FIXTURE = os.path.join(ROOT, "fixtures", "subject_loop_emt.md")
MATH_FIXTURE = os.path.join(ROOT, "fixtures", "subject_loop_math.md")
CS_FIXTURE = os.path.join(ROOT, "fixtures", "subject_loop_cs.md")

FOURTH_BANK = """# Subject-loop fourth fixture (synthetic, Phase 9)

Fully invented teaching content for the configuration-only fourth profile.

## LESSON

### Fourth Subject

Context before the action: a configuration-only fourth profile must complete
the same guided-discovery loop with no production edit.

Q1. Which option completes the shared loop?   (difficulty: application)
[LESSON-REF: Fourth Subject]
[OBJECTIVE: fourth:loop]

A) Alpha
B) Beta
C) Gamma

CORRECT: A

WHY BEST: Alpha is the only option the loop's own contract names.

KEY DISCRIMINATOR: The learner must pick the loop's own answer.

DISTRACTOR ANALYSIS:
- A) Correct: the loop's contract.
- B) Beta would be correct if the loop asked for the second option.
- C) Gamma would be correct if the loop asked for the third option.

TRAP: None; synthetic.

CONFIDENCE: high
"""


def _fourth_registry(tmp):
    """Append a temporary fourth entry to temporary settings (09-02) and
    return the resolved registry."""
    from surfaces import settings as settings_surface
    cfg = settings_surface.load_settings(tmp)
    cfg["subject_profiles"]["entries"]["fourth"] = {
        "id": "fourth", "version": 1,
        "lesson": {"markdown": True, "tables": True, "math": False,
                   "runnable_languages": [], "lesson_layout": "separate"},
        "allowed_item_types": ["mc", "multi", "table", "dnd", "build",
                               "short"],
        "verifier": "runtime"}
    settings_surface.write_settings(tmp, cfg)
    return subjects.load_registry(tmp)


def run_subject_case(tmp, bank, profile_id, wrong_answer, correct_answer,
                     verifier, medium_fn):
    """The ONE table-driven guided-discovery driver (D-12..D-15): start a
    practice sitting on the fixture under the profile id, submit the WRONG
    response, request the targeted authored hint, submit a materially
    changed CORRECT response, and assert the shared runtime transitions,
    cursor progression, hint tier, evidence shape, and final outcome. The
    medium assertion hook checks the fixture-specific presentation; every
    other assertion is subject-independent. Returns the observed shape so
    the matrix can compare it across all four rows."""
    # Drive a copy inside tmp so the run's evidence and sessions land in the
    # temporary directory, never beside the shipped fixture.
    if os.path.dirname(os.path.abspath(bank)) != os.path.abspath(tmp):
        local = write_bank(tmp, "case_%s_%s.md"
                           % (profile_id, uuid.uuid4().hex[:8]),
                           open(bank, encoding="utf-8").read())
    else:
        local = bank
    out = os.path.join(tmp, "loop_%s.json" % profile_id)
    res = session_surface.do_start(local, {"count": 1}, "practice", out,
                                   force=False, profile_id=profile_id)
    if res.get("subject_id") != profile_id:
        fail("%s: start must resolve profile id %r, got %r"
             % (profile_id, profile_id, res.get("subject_id")))
    data = json.load(open(out, encoding="utf-8"))
    sp = data["subject_profile"]
    if sp["profile"]["verifier"] != verifier:
        fail("%s: stored verifier must be %r, got %r"
             % (profile_id, verifier, sp["profile"]["verifier"]))
    sid = data["session_id"]
    # Context -> wrong action/prediction: hold, score False.
    r1 = session_surface.do_action(out, {"kind": "submit",
                                         "answer": wrong_answer})
    if r1["action"] != "hold" or r1["score"] is not False:
        fail("%s: a wrong response must hold with score False, got %r"
             % (profile_id, r1))
    if (r1.get("next") or {}).get("position") != 0:
        fail("%s: a held cursor must not advance, got %r"
             % (profile_id, r1))
    # Wrong -> one targeted authored hint (tier 0, the lesson pointer).
    r2 = session_surface.do_action(out, {"kind": "hint"})
    if r2["action"] != "reveal_tier":
        fail("%s: the hint request must reveal a tier, got %r"
             % (profile_id, r2))
    tier = (r2.get("hint") or {}).get("tier") or {}
    if tier.get("index") != 0 or not tier.get("available"):
        fail("%s: the first hint must be the available authored lesson "
             "tier, got %r" % (profile_id, tier))
    # Retry with the materially changed correct answer: advance (or complete
    # on the final item of a one-item sitting), score True.
    r3 = session_surface.do_action(out, {"kind": "submit",
                                         "answer": correct_answer})
    if r3["action"] not in ("advance", "complete") or r3["score"] is not True:
        fail("%s: a correct retry must advance with score True, got %r"
             % (profile_id, r3))
    if (r3.get("next") or {}).get("position") != 1:
        fail("%s: a correct retry must advance the cursor, got %r"
             % (profile_id, r3))
    log = evidence.log_path(tmp)
    responses = evidence.session_events(log, sid)
    hints = evidence.hint_events(log, sid)
    if len(responses) != 2 or len(hints) != 1:
        fail("%s: the loop must record two responses and one hint, got %d/%d"
             % (profile_id, len(responses), len(hints)))
    if responses[0]["score"] is not False or responses[1]["score"] is not True:
        fail("%s: response events must carry the real scores, got %r"
             % (profile_id, responses))
    if hints[0]["tier_index"] != 0 or hints[0]["source"] != "authored":
        fail("%s: the hint event must record authored tier 0, got %r"
             % (profile_id, hints[0]))
    # The shared evidence spine: the fields every subject's events carry.
    spine = ("event_id", "event_type", "session_id", "item_ref", "ts",
             "score", "mode", "subject", "attempt_number")
    response_spine = sorted(k for k in responses[0] if k in spine)
    hint_spine = sorted(k for k in hints[0] if k in spine)
    medium_fn(local, profile_id, data, r1, r2, r3)
    return {
        "profile_id": profile_id,
        "transitions": (r1["action"], r2["action"], r3["action"]),
        "response_spine": response_spine,
        "hint_spine": hint_spine,
        "outcome": (r3["score"], len(responses), len(hints)),
    }


def _medium_emt(bank, profile_id, data, r1, r2, r3):
    """EMT medium: the shared reader keeps #lesson-content source order and
    the native labelled focusable .lesson-table-scroll wrapper (D-13)."""
    qs = model.load(bank)
    page = lesson_surface.lesson_page(
        bank, qs, model.parse_lesson(bank), runtime=True,
        profile=data["subject_profile"])
    if 'id="lesson-content"' not in page:
        fail("emt: the shared reader must carry #lesson-content")
    if ('<div class="scroll lesson-table-scroll" tabindex="0" role="region" '
            'aria-label="Scene Priorities"><table>') not in page:
        fail("emt: the table must sit in the labelled focusable wrapper")
    if "<th scope=\"col\">Sign</th>" not in page:
        fail("emt: header cells must carry scope=col")
    order = [page.index("Scene Priorities"), page.index("<p>Context before"),
             page.index("<table>")]
    if not (order[0] < order[1] < order[2]):
        fail("emt: lesson source order must survive rendering")


def _medium_math(bank, profile_id, data, r1, r2, r3):
    """Math medium: local inline/display hooks and readable degraded source
    -- the $...$ / $$...$$ source stays present and, under the math profile
    on a served page, the local adapter + display wrapper are emitted."""
    qs = model.load(bank)
    les = model.parse_lesson(bank)
    page = lesson_surface.lesson_page(
        bank, qs, les, runtime=True, profile=data["subject_profile"])
    if "$v_n = v_0 + n \\cdot d$" not in page and \
            "$v_0 + n$" not in page and "$n$" not in page:
        fail("math: the inline math source must remain readable in the page")
    if "$$" not in page:
        fail("math: the display delimiter source must remain present")
    if "renderMathInElement" not in page or "katex.min.css" not in page:
        fail("math: the math profile served page must ship the local adapter "
             "and asset hooks")
    if "lesson-math-display" not in lesson_surface.MATH_ADAPTER_JS + page:
        fail("math: the display wrapper hook must exist")
    if "Math could not be rendered" not in lesson_surface.MATH_ADAPTER_JS:
        fail("math: the parse-failure copy must be embedded")


def _medium_cs(bank, profile_id, data, r1, r2, r3):
    """CS medium: independent runnable-code lifecycle/status/output hooks --
    the data-code-block identity, Run control, status region, and labelled
    non-live streams on a served page with a session."""
    qs = model.load(bank)
    page = lesson_surface.lesson_page(
        bank, qs, model.parse_lesson(bank), runtime=True,
        profile=data["subject_profile"],
        session_id=data["session_id"])
    if 'data-code-block="1" data-lang="python"' not in page:
        fail("cs: the python fence must carry the stable runnable id")
    if lesson_surface.RUN_READY_COPY not in page:
        fail("cs: the Run control label must be present")
    if 'class="run-status" id="run-status-1" aria-live="off"' not in page:
        fail("cs: the stable idle runnable readout must be present")
    if 'aria-describedby="run-status-1"' not in page:
        fail("cs: the Run control must describe its stable idle readout")
    if 'class="run-status" role="status"' in page or \
            'class="run-status" aria-live="polite"' in page:
        fail("cs: the idle runnable readout must not be persistently polite")
    if 'class="run-label">stdout</p><pre class="run-stdout"' not in page \
            or 'class="run-label">stderr</p><pre class="run-stderr"' not in page:
        fail("cs: labelled non-live stdout/stderr streams must be present")
    if lesson_surface.RUN_RUNNING_COPY not in lesson_surface.RUNNABLE_JS:
        fail("cs: the running-state copy must be embedded")
    adapter = lesson_surface.RUNNABLE_JS
    if ('s.setAttribute("role", "alert")' not in adapter or
            's.setAttribute("aria-live", "assertive")' not in adapter or
            adapter.find('s.setAttribute("aria-live", "assertive")') >
            adapter.find("s.textContent = text")):
        fail("cs: blocking runnable errors must be assertive before text")


def _medium_plain(bank, profile_id, data, r1, r2, r3):
    """Configuration-only fourth profile: the shared reader and source order
    hold with no medium-specific hook at all -- configuration adds nothing
    to the shell (D-15)."""
    qs = model.load(bank)
    page = lesson_surface.lesson_page(
        bank, qs, model.parse_lesson(bank), runtime=True,
        profile=data["subject_profile"])
    if 'id="lesson-content"' not in page:
        fail("fourth: the shared reader must carry #lesson-content")
    order = [page.index("Fourth Subject"), page.index("<p>Context before")]
    if not (order[0] < order[1]):
        fail("fourth: lesson source order must survive rendering")


def test_four_subjects_share_one_guided_loop(tmp):
    """D-12..D-15 / plan 09-05 Task 3: EMT, Math, CS, and the configuration-
    only fourth profile call the same driver and produce the same transition
    names, cursor progression, hint tier, evidence spine, and final outcome;
    only the fixture path, profile id, medium assertion, allowed item type,
    verifier id, and response value vary."""
    fourth = write_bank(tmp, "fourth_bank.md", FOURTH_BANK)
    _fourth_registry(tmp)
    cases = [
        (EMT_FIXTURE, "emt", "A", "B", "runtime", _medium_emt),
        (MATH_FIXTURE, "math", "B", "A", "runtime", _medium_math),
        (CS_FIXTURE, "cs",
         'print(0)\n', 'print(sum(int(x) for x in input().split()))\n',
         "check", _medium_cs),
        (fourth, "fourth", "B", "A", "runtime", _medium_plain),
    ]
    shapes = []
    for bank, pid, wrong, right, verifier, medium in cases:
        shapes.append(run_subject_case(tmp, bank, pid, wrong, right,
                                       verifier, medium))
    base = shapes[0]
    for shape in shapes[1:]:
        for field in ("transitions", "response_spine", "hint_spine",
                      "outcome"):
            if shape[field] != base[field]:
                fail("%s must share the %s with emt: %r vs %r"
                     % (shape["profile_id"], field, shape[field],
                        base[field]))
    if base["transitions"] != ("hold", "reveal_tier", "complete"):
        fail("the shared loop must be wrong-hold -> hint-reveal -> "
             "correct-complete, got %r" % (base["transitions"],))
    if base["response_spine"] != sorted(
            ("event_id", "event_type", "session_id", "item_ref", "ts",
             "score", "mode", "subject", "attempt_number")):
        fail("the evidence spine differs across subjects: %r"
             % base["response_spine"])
    print("four-subject loop: %s all share one driver and evidence shape"
          % ", ".join(s["profile_id"] for s in shapes))


def test_profile_id_wired_through_clients(tmp):
    """D-01..D-04 / plan 09-05 Task 2 Test 1: CLI `start --subject-profile`,
    API start `{profile:}`, CLI `lesson --subject-profile`, and the
    `/lesson/<bank>?profile=` query all resolve the SAME id to the same
    public profile metadata through the one server-side selector."""
    bank = write_bank(tmp, "emt_prof_bank.md", EMT_BANK)
    # CLI start with an explicit id.
    out = os.path.join(tmp, "s.json")
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "start",
         bank, "--out", out, "--subject-profile", "emt"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if res.returncode != 0:
        fail("CLI start --subject-profile failed: " + res.stdout)
    started = json.loads(res.stdout)
    if started.get("subject_id") != "emt":
        fail("CLI start must expose the explicit subject id, got %r"
             % started.get("subject_id"))
    data = json.load(open(out, encoding="utf-8"))
    sp = data["subject_profile"]
    if sp["subject_id"] != "emt" or sp["profile"]["id"] != "emt" \
            or sp["profile"]["verifier"] != "runtime":
        fail("CLI start must persist the server-resolved emt snapshot, got %r"
             % sp)
    # API start with the same id resolves the same metadata.
    proc, url = _start_daemon(tmp)
    try:
        # CLI lesson and the /lesson query resolve the same presentation;
        # compared BEFORE any session is registered so neither page carries
        # the runnable session attribute.
        cli_page = os.path.join(tmp, "lesson.html")
        r2 = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "lesson",
             bank, "--out", cli_page, "--subject-profile", "emt"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            timeout=30)
        if r2.returncode != 0:
            fail("CLI lesson --subject-profile failed: " + r2.stdout)
        status2, served = _get(url + "/lesson/emt_prof_bank?profile=emt")
        if status2 != 200:
            fail("/lesson?profile=emt returned %d" % status2)
        cli_html = open(cli_page, encoding="utf-8").read()
        # The daemon adds its contextual course navigation. Compare the
        # shared lesson document after removing that daemon-only block.
        served_core = re.sub(r'<nav class="lesson-context-nav".*?</nav>',
                             "", served, flags=re.S)
        if cli_html != served_core:
            fail("CLI lesson --subject-profile and /lesson?profile= must "
                 "render the same page byte-for-byte")
        status, body = _post(url + "/api/start",
                             {"bank": "emt_prof_bank", "count": 1, "seed": 0,
                              "mode": "practice", "profile": "emt"})
        if status != 200:
            fail("API start with profile id failed: %d %r" % (status, body))
        if body.get("subject_id") != "emt":
            fail("API start must expose the explicit subject id, got %r"
                 % body.get("subject_id"))
        # The math profile on the same bank enables the adapter over the
        # served route; the explicit id is the only lever that changes it.
        status3, page3 = _get(url + "/lesson/emt_prof_bank?profile=math")
        if status3 != 200:
            fail("/lesson?profile=math returned %d" % status3)
        if "renderMathInElement" not in page3:
            fail("?profile=math must enable the math adapter")
    finally:
        proc.terminate()


def test_only_id_crosses_client_boundary(tmp):
    """D-02/D-04 / plan 09-05 Task 2 Test 2: only the profile id crosses a
    client boundary; a profile OBJECT (capabilities/verifier content) is
    rejected by name, and the session snapshot is always the server-resolved
    one -- a client can never set verifier or capabilities directly."""
    bank = write_bank(tmp, "emt_obj_bank.md", EMT_BANK)
    proc, url = _start_daemon(tmp)
    try:
        status, body = _post(url + "/api/start",
                             {"bank": "emt_obj_bank", "count": 1, "seed": 0,
                              "mode": "practice",
                              "profile": {"id": "emt", "verifier": "check",
                                          "lesson": {"runnable_languages":
                                                     ["python"]}}})
        if status != 400:
            fail("a profile object must be refused, got %d %r" % (status, body))
        # A non-string profile value is refused too.
        status2, _ = _post(url + "/api/start",
                           {"bank": "emt_obj_bank", "count": 1, "seed": 0,
                            "mode": "practice", "profile": 7})
        if status2 != 400:
            fail("a non-string profile value must be refused, got %d" % status2)
        # The id path stores only the server-resolved snapshot.
        status3, body3 = _post(url + "/api/start",
                               {"bank": "emt_obj_bank", "count": 1, "seed": 0,
                                "mode": "practice", "profile": "emt"})
        if status3 != 200 or body3.get("subject_id") != "emt":
            fail("profile id start failed: %d %r" % (status3, body3))
        sp = body3.get("subject_profile") or {}
        if sp.get("verifier") != "runtime":
            fail("the stored snapshot must carry the server-resolved "
                 "verifier, got %r" % sp)
    finally:
        proc.terminate()


def test_unknown_and_mixed_fail_before_writes(_tmp):
    """D-03/D-04 / plan 09-05 Task 2 Test 3: an unknown id and a mixed bank
    without an explicit id fail BEFORE any session or evidence file exists,
    and no failure discloses an absolute path. Uses its own fresh directory
    so the no-write assertion is exact."""
    tmp = tempfile.mkdtemp(prefix="subject_loop_nowrite_")
    try:
        bank = write_bank(tmp, "emt_unk_bank.md", EMT_BANK)
        out = os.path.join(tmp, "bad.json")
        res = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "start",
             bank, "--out", out, "--subject-profile", "nosuch"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            timeout=30)
        if res.returncode == 0:
            fail("an unknown profile id must fail the CLI start")
        if "nosuch" not in res.stdout:
            fail("the refusal must name the unknown id, got %r" % res.stdout)
        if os.path.abspath(tmp) in res.stdout:
            fail("the CLI refusal must not disclose the bank path, got %r"
                 % res.stdout)
        if os.path.exists(out) or _evidence_files(tmp):
            fail("an unknown profile id must write no session or evidence")
        # Mixed bank without an explicit id: refused before writes, path-free.
        mixed = write_bank(tmp, "mixed_bank.md", MIXED_BANK)
        out2 = os.path.join(tmp, "bad2.json")
        res2 = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "start",
             mixed, "--out", out2],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            timeout=30)
        if res2.returncode == 0:
            fail("a mixed bank without an explicit id must fail the CLI start")
        if "explicit profile id" not in res2.stdout:
            fail("the mixed refusal must ask for an explicit id, got %r"
                 % res2.stdout)
        if os.path.abspath(tmp) in res2.stdout:
            fail("the mixed refusal must not disclose the bank path, got %r"
                 % res2.stdout)
        if os.path.exists(out2) or _evidence_files(tmp):
            fail("a mixed bank refusal must write no session or evidence")
        # The same two cases through the served API are path-free 4xxs.
        proc, url = _start_daemon(tmp)
        try:
            status, body = _post(url + "/api/start",
                                 {"bank": "emt_unk_bank", "count": 1,
                                  "seed": 0, "mode": "practice",
                                  "profile": "nosuch"})
            if status != 400 or "nosuch" not in json.dumps(body):
                fail("API unknown profile id must 400 by name, got %d %r"
                     % (status, body))
            status2, body2 = _post(url + "/api/start",
                                   {"bank": "mixed_bank", "count": 2,
                                    "seed": 0, "mode": "practice"})
            if status2 != 400:
                fail("API mixed bank must 400, got %d %r" % (status2, body2))
            for blob in (json.dumps(body), json.dumps(body2)):
                if os.path.abspath(tmp) in blob or "Traceback" in blob:
                    fail("API refusals must not leak a path or traceback: %r"
                         % blob)
        finally:
            proc.terminate()
        if _evidence_files(tmp):
            fail("API refusals must write no session or evidence")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_resume_uses_stored_snapshot_with_explicit_id(tmp):
    """D-04 / plan 09-05 Task 2 Test 4: a session started with an explicit
    profile id keeps consuming its STORED snapshot after the registry
    changes -- the id is resolved once at start, never re-resolved."""
    bank = write_bank(tmp, "emt_res_bank.md", EMT_BANK)
    out = os.path.join(tmp, "res.json")
    res = session_surface.do_start(bank, {"count": 2}, "practice", out,
                                   force=False, profile_id="emt")
    if res.get("subject_id") != "emt":
        fail("explicit-id start must select emt, got %r" % res)
    data = json.load(open(out, encoding="utf-8"))
    before = data["subject_profile"]
    from surfaces import settings as settings_surface
    cfg = settings_surface.load_settings(tmp)
    cfg["subject_profiles"]["entries"]["emt"]["lesson"]["math"] = True
    settings_surface.write_settings(tmp, cfg)
    try:
        session_surface.do_action(out, {"kind": "submit", "answer": "B"})
    finally:
        os.remove(os.path.join(tmp, "itembank.json"))
    again = json.load(open(out, encoding="utf-8"))
    if again["subject_profile"] != before:
        fail("resume must keep the stored snapshot byte-for-byte, got %r"
             % again["subject_profile"])


def main():
    tmp = tempfile.mkdtemp(prefix="subject_loop_")
    try:
        test_subject_ids_use_the_one_extractor()
        test_validate_registry_rejects_bad_shapes()
        test_nremt_structure_rule_is_subject_scoped()
        test_conservative_fallback_and_capability_report()
        test_mixed_subject_refusal_and_explicit_resolution()
        test_disallowed_item_type_refuses_before_write()
        test_emt_lesson_semantic_table(tmp)
        test_emt_learner_loop_with_persisted_profile(tmp)
        test_legacy_session_fills_snapshot_once(tmp)
        test_settings_registry_parity()
        test_load_registry_rejects_malformed()
        test_fourth_profile_is_configuration_only(tmp)
        test_no_subject_dispatch_in_surfaces()
        test_profile_id_wired_through_clients(tmp)
        test_only_id_crosses_client_boundary(tmp)
        test_unknown_and_mixed_fail_before_writes(tmp)
        test_resume_uses_stored_snapshot_with_explicit_id(tmp)
        test_four_subjects_share_one_guided_loop(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("ok: subject loop (EMT tracer, persisted profile, resume drift, "
          "fallback/mixed/disallowed, semantic table, v3 upgrade, settings "
          "registry parity, configuration-only fourth profile, client "
          "profile-id wiring, four-subject shared loop)")


if __name__ == "__main__":
    main()
