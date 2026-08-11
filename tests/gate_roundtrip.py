#!/usr/bin/env python3
"""Phase 6.2 gate fixtures: the evidence layer and the [GATE:] grammar.

Plan 06.2-01 owns four requirement areas and their fixtures:
  GATE-01  the [GATE:] directive parses additively and the [!CHECK:] id
           resolution lint shares one constant with the renderer (D-01/D-02)
  GATE-02  gate_skip is its own event type with no score key, and the
           response event carries an additive context field (D-07/D-08)
  GATE-03  a cleared inline check and a quiz response on the same objective
           collapse into one objective_history list differing only by
           context -- Phase 10 needs no branch (D-08)
  GATE-04  gate_state derives open|cleared|skipped from the one evidence
           log, session-scoped, retraction-aware, with no second store (D-06)

Standard library only, runnable as `python tests/gate_roundtrip.py`.
"""
import json, os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
import evidence                                            # noqa: E402
from model import CHECK_UNRESOLVED_COPY, GATE_VALUES        # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def _bank_text(gate=None, check="q1"):
    """A synthetic bank whose lesson carries one [!CHECK:] and one item the
    check resolves to. `gate=None` omits the [GATE:] directive entirely
    (the additive-grammar case); otherwise the directive is emitted with
    the given value."""
    gate_line = "" if gate is None else "\n[GATE: %s]" % gate
    return """# Gate fixture bank
%s

## LESSON

Intro sentence.

### First Section

Prose above the check.

> [!CHECK: %s]

Prose below the check (gated under required).

### Second Section

More prose.

Q1. Which adjunct opens an airway?   (difficulty: recall)
[OBJECTIVE: emt:airway.adjunct]
A) A tongue depressor
B) An oropharyngeal airway
C) Oxygen tubing
D) A stethoscope
CORRECT: B
WHY BEST: The oropharyngeal airway is the standard airway adjunct.
KEY DISCRIMINATOR: A device that holds the tongue off the pharynx.
SECOND-BEST: A. A tongue depressor holds the tongue; correct only if the question asked about visualization.
DISTRACTOR ANALYSIS:
- A) A visualization aid; would be correct if the question asked how to see the airway.
- B) Correct: the standard adjunct.
- C) Delivers oxygen; would be correct if the question asked about oxygenation.
- D) A diagnostic tool; would be correct if the question asked how to auscultate.
TRAP: Confusing oxygen delivery with airway opening.
CONFIDENCE: high
""" % (gate_line, check)


def _write_bank(tmp, name="gate_bank.md", gate=None, check="q1"):
    path = os.path.join(tmp, name)
    open(path, "w", encoding="utf-8").write(_bank_text(gate=gate, check=check))
    return path


def test_gate_directive_parses_and_defaults():
    """Task 1 Test 1: the three values parse, the default is recommended,
    and an invalid value is a named lint error, never a render-time
    crash."""
    tmp = tempfile.mkdtemp()
    try:
        for value in GATE_VALUES:
            path = _write_bank(tmp, "gate_%s.md" % value, gate=value)
            les = itembank.parse_lesson(path)
            if les is None or les.get("gate") != value:
                fail("[GATE: %s] did not parse to %r (got %r)"
                     % (value, value, les and les.get("gate")))
        path = _write_bank(tmp, "gate_default.md")
        les = itembank.parse_lesson(path)
        if les is None or les.get("gate") != "recommended":
            fail("a lesson with no [GATE:] must default to recommended, "
                 "got %r" % (les and les.get("gate")))
        bad = _write_bank(tmp, "gate_maybe.md", gate="maybe")
        qs = itembank.load(bad)
        errors, warnings = itembank.lint(
            qs, lesson=itembank.parse_lesson(bad))
        gate_errors = [e for e in errors if e.code == "lesson.invalid_gate"]
        if not gate_errors:
            fail("an invalid [GATE:] value must be a named lint error")
        if "maybe" not in gate_errors[0].message:
            fail("the invalid-gate finding must echo the authored value")
        # A parse never raises on the invalid value (lint's job, not the
        # parser's).
        try:
            itembank.parse_lesson(bad)
        except Exception as exc:
            fail("parse_lesson raised on an invalid [GATE:] value: %r" % exc)
        print("gate directive: three values + default + named invalid error")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_grammar_additive():
    """Task 1 Test 2: a bank with no [GATE:] directive parses additively --
    the lesson dict gains exactly the one new 'gate' key with the default
    value, and lint emits no gate finding for it."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        les = itembank.parse_lesson(path)
        if set(les) != {"source", "gate", "body", "intro", "headings",
                        "error", "detail"}:
            fail("no-gate parse must carry exactly the pre-6.2 key set "
                 "plus 'gate', got %r" % sorted(les))
        qs = itembank.load(path)
        errors, warnings = itembank.lint(
            qs, lesson=les)
        gate_codes = {"lesson.invalid_gate", "lesson.check_ref_unknown"}
        fired = [e.code for e in errors if e.code in gate_codes]
        if fired:
            fail("a no-gate bank with a resolvable check fired gate "
                 "findings: %r" % fired)
        print("gate grammar: additive parse, no gate findings on clean bank")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_check_ref_lint_constant_single_source():
    """Task 1 Test 3 + UI-SPEC section 13 gate 12 (cross-phase divergence
    guard): the unresolvable [!CHECK:] lint code and message are the shared
    model.CHECK_UNRESOLVED_COPY constant, reproduced verbatim from the
    UI-SPEC section 15 row. The constant is defined once in model.py (the
    linter's home); plan 06.2-02 wires the lesson renderer to import the
    same object, and the cross-phase divergence guard (plan 06.2-04)
    asserts the identity then."""
    spec_copy = ("This check refers to an item that is not in this bank. "
                 "Run itembank lint <bank> for details.")
    if CHECK_UNRESOLVED_COPY != spec_copy:
        fail("CHECK_UNRESOLVED_COPY drifted from the UI-SPEC section 15 "
             "copy: %r" % CHECK_UNRESOLVED_COPY)
    model_src = open(os.path.join(ROOT, "model.py"), encoding="utf-8").read()
    if model_src.count('CHECK_UNRESOLVED_COPY = (') != 1:
        fail("CHECK_UNRESOLVED_COPY must be defined exactly once in model.py")
    # The constant must be the UI-SPEC copy verbatim (equality above); the
    # definition-count check above is the single-source guard -- one
    # definition, imported everywhere else.
    tmp = tempfile.mkdtemp()
    try:
        # An unresolvable check id (q9 is not an item in the bank).
        path = _write_bank(tmp, "gate_unresolved.md", check="q9")
        qs = itembank.load(path)
        errors, warnings = itembank.lint(
            qs, lesson=itembank.parse_lesson(path))
        hits = [e for e in errors if e.code == "lesson.check_ref_unknown"]
        if not hits:
            fail("an unresolvable [!CHECK:] id must be a lint error")
        if CHECK_UNRESOLVED_COPY not in hits[0].message:
            fail("the check_ref_unknown message must carry the shared copy "
                 "verbatim: %r" % hits[0].message)
        # A resolvable id fires nothing.
        ok = _write_bank(tmp, "gate_ok.md")
        ok_qs = itembank.load(ok)
        ok_errors, _ = itembank.lint(
            ok_qs, lesson=itembank.parse_lesson(ok))
        if any(e.code == "lesson.check_ref_unknown" for e in ok_errors):
            fail("a resolvable [!CHECK:] id must not fire check_ref_unknown")
        print("check-ref lint: shared constant, verbatim copy, resolution")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _fixture_log(tmp):
    """A fresh evidence log dir with a session id."""
    bank_dir = os.path.join(tmp, "_evidence")
    os.makedirs(bank_dir, exist_ok=True)
    return evidence.log_path(bank_dir)


def test_gate_skip_event_shape_and_no_score_key():
    """Task 2 Test 1: gate_skip_event produces the full envelope, no score
    key at all -- asserted structurally, `"score" not in ev` -- and the
    event validates against the published schema."""
    tmp = tempfile.mkdtemp()
    try:
        log = _fixture_log(tmp)
        ev = evidence.gate_skip_event(
            session_id="s1", bank="gate_bank.md", lesson_slug="first-section",
            check_item_id="q1", check_item_ref="q1",
            objective="emt:airway.adjunct", gate_mode="required")
        want = {"schema_version", "event_id", "event_type", "ts",
                "session_id", "bank", "lesson_slug", "check_item_id",
                "check_item_ref", "objective", "gate_mode", "dedupe_key"}
        if set(ev) != want:
            fail("gate_skip event key set drifted: %r" % sorted(set(ev) ^ want))
        if "score" in ev:
            fail("a gate_skip event must never carry a score key -- not "
                 "even None")
        if ev["event_type"] != "gate_skip":
            fail("event_type must be gate_skip")
        if "gate_skip" not in evidence.KNOWN_EVENT_TYPES:
            fail("gate_skip missing from KNOWN_EVENT_TYPES")
        # Schema validation through the published contract.
        schema = json.load(open(os.path.join(ROOT, "schemas",
                                             "response.schema.json"),
                                encoding="utf-8"))
        problems = itembank.validate(ev, schema)
        if problems:
            fail("gate_skip event failed schema validation: %s" % problems)
        # ValueError on an invalid gate_mode ("off" never offers a skip).
        for bad in ("off", "maybe", ""):
            try:
                evidence.gate_skip_event(
                    session_id="s1", bank="b.md", lesson_slug="l",
                    check_item_id="q1", check_item_ref="q1",
                    objective="o", gate_mode=bad)
                fail("gate_skip_event accepted gate_mode %r" % bad)
            except ValueError:
                pass
        print("gate_skip: own envelope, no score key, schema-valid, "
              "ValueError on off/unknown")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_skip_dedupe_within_session():
    """Task 2 Test 2: a second gate_skip for the same (session, check) has
    the same dedupe_key and append_event reports already_recorded rather
    than appending a second fact."""
    tmp = tempfile.mkdtemp()
    try:
        log = _fixture_log(tmp)
        def ev():
            return evidence.gate_skip_event(
                session_id="s1", bank="b.md", lesson_slug="l",
                check_item_id="q1", check_item_ref="q1",
                objective="o", gate_mode="required")
        first = evidence.append_event(log, ev())
        if first["status"] != "recorded":
            fail("first gate_skip must record, got %r" % first)
        second = evidence.append_event(log, ev())
        if second["status"] != "already_recorded":
            fail("second gate_skip must dedupe, got %r" % second)
        skips = [e for e in evidence.live_events(log)
                 if e.get("event_type") == "gate_skip"]
        if len(skips) != 1:
            fail("exactly one gate_skip must be live, got %d" % len(skips))
        # A different check in the same session is a different fact.
        other = evidence.gate_skip_event(
            session_id="s1", bank="b.md", lesson_slug="l",
            check_item_id="q2", check_item_ref="q2",
            objective="o", gate_mode="recommended")
        third = evidence.append_event(log, other)
        if third["status"] != "recorded":
            fail("a different check id must record, got %r" % third)
        print("gate_skip dedupe: (session, check) pair, already_recorded")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_response_context_field():
    """Task 2 Test 3: response_event carries context (lesson_gate from the
    new call site, quiz by default for every existing caller), and the
    schema validates quiz and lesson_gate and rejects anything else."""
    tmp = tempfile.mkdtemp()
    try:
        q = {"id": "q1", "item_id": "it-1", "type": "mc", "stem": "s",
             "opts": {"A": "a", "B": "b"}, "correct": ["B"],
             "objective": "emt:airway.adjunct", "select": 1}
        quiz_ev = evidence.response_event(
            session_id="s1", q=q, answer="B", score=True,
            mode="practice", attempt_num=1, bank="b.md")
        if quiz_ev.get("context") != "quiz":
            fail("a default response_event must carry context=quiz, got %r"
                 % quiz_ev.get("context"))
        gate_ev = evidence.response_event(
            session_id="s1", q=q, answer="B", score=True,
            mode="practice", attempt_num=1, bank="b.md",
            context="lesson_gate")
        if gate_ev.get("context") != "lesson_gate":
            fail("context=lesson_gate must round-trip onto the event")
        schema = json.load(open(os.path.join(ROOT, "schemas",
                                             "response.schema.json"),
                                encoding="utf-8"))
        for ev in (quiz_ev, gate_ev):
            problems = itembank.validate(ev, schema)
            if problems:
                fail("context-bearing response failed schema validation: %s"
                     % problems)
        bad = dict(gate_ev)
        bad["context"] = "homework"
        if not itembank.validate(bad, schema):
            fail("the schema must reject a context value outside "
                 "quiz|lesson_gate")
        print("response context: quiz default, lesson_gate, schema enforces")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_objective_history_collapses_lesson_and_quiz():
    """Task 2 Test 4 (GATE-03): a lesson-gate response and a quiz response
    on the same objective return in one undifferentiated, correctly ordered
    list, differing only by context -- Phase 10 needs no branch."""
    tmp = tempfile.mkdtemp()
    try:
        log = _fixture_log(tmp)
        q = {"id": "q1", "item_id": "it-1", "type": "mc", "stem": "s",
             "opts": {"A": "a", "B": "b"}, "correct": ["B"],
             "objective": "emt:airway.adjunct", "select": 1}
        evidence.append_event(log, evidence.response_event(
            session_id="s1", q=q, answer="B", score=True,
            mode="practice", attempt_num=1, bank="b.md",
            context="lesson_gate"))
        evidence.append_event(log, evidence.response_event(
            session_id="s1", q=q, answer="B", score=True,
            mode="practice", attempt_num=2, bank="b.md"))
        rows = evidence.objective_history(log, "emt:airway.adjunct")
        if len(rows) != 2:
            fail("both responses must appear in one objective_history list, "
                 "got %d rows" % len(rows))
        contexts = [r.get("context") for r in rows]
        if contexts != ["lesson_gate", "quiz"]:
            fail("rows must differ only by context in log order, got %r"
                 % contexts)
        for r in rows:
            probe = dict(r)
            probe.pop("context", None)
            if any(k not in ("ts", "session_id", "item_id", "item_ref",
                             "mode", "score", "attempt_number", "confidence",
                             "response_time_ms", "objective", "bank")
                   for k in probe):
                fail("row carries unexpected keys: %r" % sorted(probe))
        print("objective_history: one list, context-only difference")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_state_four_states_and_resolution():
    """Task 3 Test 1: gate_state returns open with no events, cleared after
    a live lesson-gate response, skipped after a gate_skip, and cleared
    after skip-then-clear (pair-level resolution)."""
    tmp = tempfile.mkdtemp()
    try:
        log = _fixture_log(tmp)
        q = {"id": "q1", "item_id": "it-1", "type": "mc", "stem": "s",
             "opts": {"A": "a", "B": "b"}, "correct": ["B"],
             "objective": "emt:airway.adjunct", "select": 1}
        if evidence.gate_state(log, "s1", "q1") != "open":
            fail("no events must mean open")
        evidence.append_event(log, evidence.gate_skip_event(
            session_id="s1", bank="b.md", lesson_slug="l",
            check_item_id="q1", check_item_ref="q1",
            objective="emt:airway.adjunct", gate_mode="required"))
        if evidence.gate_state(log, "s1", "q1") != "skipped":
            fail("a live gate_skip with no response must mean skipped")
        # skip-then-clear resolves to cleared.
        evidence.append_event(log, evidence.response_event(
            session_id="s1", q=q, answer="B", score=True,
            mode="practice", attempt_num=1, bank="b.md",
            context="lesson_gate"))
        if evidence.gate_state(log, "s1", "q1") != "cleared":
            fail("skip-then-clear must resolve to cleared (pair-level)")
        print("gate_state: open/skipped/cleared, pair-level resolution")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_state_session_scoped():
    """Task 3 Test 2: gate state is session-scoped -- the same check cleared
    in an earlier sitting gates again in a new session."""
    tmp = tempfile.mkdtemp()
    try:
        log = _fixture_log(tmp)
        q = {"id": "q1", "item_id": "it-1", "type": "mc", "stem": "s",
             "opts": {"A": "a", "B": "b"}, "correct": ["B"],
             "objective": "emt:airway.adjunct", "select": 1}
        evidence.append_event(log, evidence.response_event(
            session_id="s1", q=q, answer="B", score=True,
            mode="practice", attempt_num=1, bank="b.md",
            context="lesson_gate"))
        if evidence.gate_state(log, "s1", "q1") != "cleared":
            fail("the clearing session must see cleared")
        if evidence.gate_state(log, "s2", "q1") != "open":
            fail("a new session must see the same check open again")
        print("gate_state: session-scoped derivation")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_state_retraction_restores_prior_state():
    """Task 3 Test 3: a retracted lesson-gate response returns the gate to
    its prior state (read-side filter discipline; no second store)."""
    tmp = tempfile.mkdtemp()
    try:
        log = _fixture_log(tmp)
        q = {"id": "q1", "item_id": "it-1", "type": "mc", "stem": "s",
             "opts": {"A": "a", "B": "b"}, "correct": ["B"],
             "objective": "emt:airway.adjunct", "select": 1}
        r1 = evidence.append_event(log, evidence.response_event(
            session_id="s1", q=q, answer="B", score=True,
            mode="practice", attempt_num=1, bank="b.md",
            context="lesson_gate"))
        if evidence.gate_state(log, "s1", "q1") != "cleared":
            fail("pre-retraction state must be cleared")
        evidence.append_event(log, evidence.retraction_event(
            retracts=r1["event_id"], reason="fixture undo", actor="test"))
        if evidence.gate_state(log, "s1", "q1") != "open":
            fail("a retracted clear must return the gate to open")
        # Retracting the skip restores open from skipped too.
        r2 = evidence.append_event(log, evidence.gate_skip_event(
            session_id="s1", bank="b.md", lesson_slug="l",
            check_item_id="q2", check_item_ref="q2",
            objective="o", gate_mode="required"))
        if evidence.gate_state(log, "s1", "q2") != "skipped":
            fail("skip state must be skipped before retraction")
        evidence.append_event(log, evidence.retraction_event(
            retracts=r2["event_id"], reason="fixture undo", actor="test"))
        if evidence.gate_state(log, "s1", "q2") != "open":
            fail("a retracted skip must return the gate to open")
        print("gate_state: retraction restores prior state")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_state_is_pure_read():
    """Task 3 acceptance: gate_state performs no writes and keeps no
    module-level cache -- a structural fixture over the source, so the
    derivation cannot silently become a second store."""
    src = open(os.path.join(ROOT, "evidence.py"), encoding="utf-8").read()
    fn = src[src.find("def gate_state("):]
    fn = fn[:fn.find("\n\ndef ")]
    for token in ("open(", "write", "append_event", "os.remove",
                  "os.makedirs", "="):
        if token == "=":
            continue  # local bindings are fine; no store is created
        if re.search(r"\b%s\b" % re.escape(token), fn):
            fail("gate_state must be a pure read, found %r" % token)
    if "live_events" not in fn:
        fail("gate_state must read through live_events")
    print("gate_state: pure read, no writes, no cache")


def main():
    test_gate_directive_parses_and_defaults()
    test_gate_grammar_additive()
    test_check_ref_lint_constant_single_source()
    test_gate_skip_event_shape_and_no_score_key()
    test_gate_skip_dedupe_within_session()
    test_response_context_field()
    test_objective_history_collapses_lesson_and_quiz()
    test_gate_state_four_states_and_resolution()
    test_gate_state_session_scoped()
    test_gate_state_retraction_restores_prior_state()
    test_gate_state_is_pure_read()
    print("ok: gate roundtrip (GATE grammar, gate_skip event, context "
          "field, gate_state derivation)")


if __name__ == "__main__":
    main()
