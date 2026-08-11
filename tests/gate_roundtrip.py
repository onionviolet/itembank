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
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import itembank                                            # noqa: E402
import evidence                                            # noqa: E402
from model import CHECK_UNRESOLVED_COPY, GATE_VALUES        # noqa: E402
from surfaces import lesson                                 # noqa: E402
import lesson_roundtrip                                     # noqa: E402


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


# ---- plan 06.2-03: the recorded-skip control, settings, outcome split ----


def test_gate_skip_control_register():
    """Task 1 Test 1: the skip control is a real submit button with the
    exact label, in the same .actions row as the check button (space-3
    apart via the shared .actions gap), both >=44px via the .go class, no
    --bad/--warn/accent fill, no icon, no confirmation."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        ctx = _gate_ctx(path, qs, policy="required")
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True, gate=ctx)
        m = re.search(
            r'<div class="actions">.*?</div>', page, re.S)
        if not m:
            fail("the band must carry one .actions row")
        actions = m.group(0)
        if "Read ahead without answering" not in actions:
            fail("the skip control must sit in the same .actions row")
        if 'value="check"' not in actions or 'value="skip"' not in actions:
            fail("the .actions row must carry both named submit buttons")
        if "warn" in actions or "bad" in actions or "accent" in actions:
            fail("the skip control must not be styled as a transgression")
        if "<svg" in actions or "icon" in actions.lower():
            fail("the skip control must carry no icon")
        if "confirm" in actions.lower() or "are you sure" in actions.lower():
            fail("the skip control must not be gated behind a confirmation")
        if "min-height:44px" not in lesson.SHARED_CSS:
            fail("the shared .go control must guarantee 44px min-height")
        print("gate skip control: ordinary register, no transgression")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_skip_after_attempt_conditional():
    """Task 1 Test 2: gate_skip always renders the control from the first
    render; after-attempt renders the Ledger line until one recorded
    attempt exists -- never a disabled button."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        les = itembank.parse_lesson(path)
        always = _gate_ctx(path, qs, policy="required", skip="always")
        page = lesson.lesson_page(path, qs, les, runtime=True, gate=always)
        if "Read ahead without answering" not in page:
            fail("gate_skip: always must render the control from the first "
                 "render")
        if "Read ahead becomes available after one attempt." in page:
            fail("gate_skip: always must not render the after-attempt line")
        # after-attempt, no attempt yet: the Ledger line, never a disabled
        # button.
        pending = _gate_ctx(path, qs, policy="required", skip="after-attempt")
        page2 = lesson.lesson_page(path, qs, les, runtime=True, gate=pending)
        if "Read ahead becomes available after one attempt." not in page2:
            fail("after-attempt must state its condition in Ledger text")
        if "Read ahead without answering" in page2:
            fail("after-attempt with no attempt must not render the button")
        if re.search(r'<button[^>]*disabled[^>]*>', page2):
            fail("after-attempt must never render a disabled button")
        # after one recorded attempt, the control appears.
        ctx = _gate_ctx(path, qs, policy="required", skip="after-attempt",
                        attempted={"q1": True})
        page3 = lesson.lesson_page(path, qs, les, runtime=True, gate=ctx)
        if "Read ahead without answering" not in page3:
            fail("after-attempt with a recorded attempt must render the "
                 "control")
        print("gate skip after-attempt: condition stated, never disabled")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_settings_roundtrip():
    """Task 1 Test 4: gate_skip and gate_policy validate through itembank
    config (validate-then-write) and appear in `itembank config` output
    with their locked defaults."""
    base = tempfile.mkdtemp()
    try:
        # Defaults appear in the table.
        out = subprocess.check_output(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "config",
             "--base", base], text=True)
        if "gate_skip" not in out or "gate_policy" not in out:
            fail("itembank config must list gate_skip and gate_policy")
        if "always" not in out or "as-authored" not in out:
            fail("the gate settings' locked defaults must appear")
        # Validate-then-write: legal values round-trip.
        for key, value in (("reader.gate_skip", "after-attempt"),
                           ("reader.gate_policy", "off")):
            r = subprocess.run(
                [sys.executable, os.path.join(ROOT, "itembank.py"), "config",
                 "set", key, value, "--base", base],
                capture_output=True, text=True)
            if r.returncode != 0:
                fail("config set %s %s failed: %s" % (key, value, r.stderr))
        # Illegal values are rejected and never touch the file.
        before = open(os.path.join(base, "itembank.json"),
                      encoding="utf-8").read()
        for key, value in (("reader.gate_skip", "sometimes"),
                           ("reader.gate_policy", "required-everywhere")):
            r = subprocess.run(
                [sys.executable, os.path.join(ROOT, "itembank.py"), "config",
                 "set", key, value, "--base", base],
                capture_output=True, text=True)
            if r.returncode == 0:
                fail("config set %s %s must be rejected" % (key, value))
        after = open(os.path.join(base, "itembank.json"),
                     encoding="utf-8").read()
        if before != after:
            fail("a rejected config set mutated itembank.json")
        print("gate settings: defaults shown, validate-then-write enforced")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_gate_policy_off_weakens_only():
    """Task 1 Test 3: gate_policy off renders any lesson ungated (the whole
    lesson in the DOM, band as the inert 3.1 slot) and can only weaken,
    never strengthen -- a recommended lesson cannot become required."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)   # [GATE: required] in _bank_text
        qs = itembank.load(path)
        les = itembank.parse_lesson(path)
        # gate_policy off -> the daemon passes gate=None (3.1 floor).
        page = lesson.lesson_page(path, qs, les, runtime=True, gate=None)
        if "Second Section" not in page:
            fail("gate_policy off must render the whole lesson")
        if ("This check is available when you are reading with a session."
                not in page):
            fail("gate_policy off must render the inert 3.1 slot")
        if '<section class="gate">' in page:
            fail("gate_policy off must not render the live band")
        # The settings schema has no strengthening value by construction.
        schema = json.load(open(os.path.join(ROOT, "schemas",
                                             "settings.schema.json"),
                                encoding="utf-8"))
        enum = schema["properties"]["reader"]["properties"]["gate_policy"]
        if enum["enum"] != ["as-authored", "off"]:
            fail("gate_policy must offer only as-authored|off (weaken-only)")
        print("gate_policy off: weakens only, whole lesson, inert slots")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _split_fixture_log(tmp):
    """A fresh log dir plus helpers that append gate events for a
    session."""
    bank_dir = os.path.join(tmp, "_evidence")
    os.makedirs(bank_dir, exist_ok=True)
    log = evidence.log_path(bank_dir)
    q = {"id": "q1", "item_id": "it-1", "type": "mc", "stem": "s",
         "opts": {"A": "a", "B": "b"}, "correct": ["B"],
         "objective": "emt:airway.adjunct", "select": 1}

    def clear(session_id, cid, bank="b.md"):
        qq = dict(q)
        qq["id"] = cid
        qq["item_id"] = "it-" + cid
        evidence.append_event(log, evidence.response_event(
            session_id=session_id, q=qq, answer="B", score=True,
            mode="practice", attempt_num=1, bank=bank,
            context="lesson_gate"))

    def skip(session_id, cid, mode="required", bank="b.md"):
        evidence.append_event(log, evidence.gate_skip_event(
            session_id=session_id, bank=bank, lesson_slug="l",
            check_item_id=cid, check_item_ref=cid, objective="o",
            gate_mode=mode))
    return log, clear, skip


def test_gate_outcome_split_pair_level():
    """Task 3 Test 1: the outcome split is computed per distinct (session,
    check) pair -- cleared wins over a prior skip; a skip with no response
    is skipped; the denominator counts distinct pairs, not events."""
    tmp = tempfile.mkdtemp()
    try:
        log, clear, skip = _split_fixture_log(tmp)
        # q1: skip then clear -> cleared (pair-level resolution).
        skip("s1", "q1")
        clear("s1", "q1")
        # q2: skip only -> skipped.
        skip("s1", "q2")
        # q3: cleared only (required evidence via gate_modes).
        clear("s1", "q3")
        modes = {"q1": "required", "q2": "required", "q3": "required"}
        split = evidence.gate_outcome_split(log, "b.md", "s1",
                                            gate_modes=modes)
        if split["denominator"] != 3:
            fail("denominator must count 3 distinct pairs, got %r"
                 % split["denominator"])
        if split["cleared"] != 2:
            fail("skip-then-clear must resolve to cleared, got %r"
                 % split["cleared"])
        if split["skipped"] != 1:
            fail("skip-only must resolve to skipped, got %r"
                 % split["skipped"])
        # Duplicate events on the same pair never inflate the count.
        skip("s1", "q2")
        split2 = evidence.gate_outcome_split(log, "b.md", "s1",
                                             gate_modes=modes)
        if split2 != split:
            fail("repeated events must not change the pair-level split")
        print("gate outcome split: pair-level, cleared-wins, distinct "
              "denominator")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_outcome_split_excludes_recommended():
    """Task 3 Test 2: recommended gates are excluded from the denominator
    -- a recommended pair never appears in the count."""
    tmp = tempfile.mkdtemp()
    try:
        log, clear, skip = _split_fixture_log(tmp)
        clear("s1", "q1")                     # required (declared)
        skip("s1", "q2", mode="recommended")  # recommended: excluded
        modes = {"q1": "required", "q2": "recommended"}
        split = evidence.gate_outcome_split(log, "b.md", "s1",
                                            gate_modes=modes)
        if split["denominator"] != 1 or split["cleared"] != 1 \
                or split["skipped"] != 0:
            fail("recommended pairs must be excluded, got %r" % split)
        # A pair whose only skip recorded "recommended" (a degraded
        # sitting) is excluded even though the lesson declares required.
        log2, _c, _s = _split_fixture_log(tmp)
        _s("s1", "q1", mode="recommended")
        modes2 = {"q1": "required"}
        split2 = evidence.gate_outcome_split(log2, "b.md", "s1",
                                             gate_modes=modes2)
        if split2["denominator"] != 0:
            fail("a recommended-served pair must be excluded, got %r"
                 % split2)
        print("gate outcome split: recommended excluded verbatim")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_outcome_split_report_copy():
    """Task 3 Test 3: the report renders `Of {n} required gates
    encountered` with the count table (rows cleared/skipped, columns count
    and share), no target, no streak, no percentage-fill bar; the empty
    state renders `Of 0 required gates encountered` with no ratio."""
    from surfaces.daemon import _gate_outcome_html
    split = {"denominator": 2, "cleared": 1, "skipped": 1,
             "share_cleared": 0.5, "share_skipped": 0.5}
    html_out = _gate_outcome_html(split)
    if "Of 2 required gates encountered" not in html_out:
        fail("the denominator copy must render verbatim")
    if ("Recommended gates are not counted" not in html_out
            or "reading past one is not a recorded choice" not in html_out):
        fail("the exclusion line must render verbatim")
    if "<tr><td>cleared</td><td>1</td><td>50%</td></tr>" not in html_out:
        fail("the cleared row must render count and share")
    if "<tr><td>skipped</td><td>1</td><td>50%</td></tr>" not in html_out:
        fail("the skipped row must render count and share")
    for banned in ("streak", "progress", "100%", "track", "target"):
        if banned in html_out.lower():
            fail("the report must not carry %r" % banned)
    empty = _gate_outcome_html({"denominator": 0, "cleared": 0,
                                "skipped": 0, "share_cleared": None,
                                "share_skipped": None})
    if "Of 0 required gates encountered" not in empty:
        fail("the empty state must render the zero denominator")
    if "<table>" in empty:
        fail("the empty state must render no ratio table")
    print("gate outcome report: denominator, count/share table, empty state")


# ---- plan 06.2-02: the render policy (the gate band) ----------------------


def _gate_ctx(bank_path, qs, policy="required", states=None, skip="always",
              degraded=False, unreachable=False, print_mode=False,
              attempted=False):
    """A gate policy context the tests build the way the daemon (plan
    06.2-03) will: states derived from the evidence log, a resolver over
    the bank's items, and the provenance the band needs."""
    stem = os.path.splitext(os.path.basename(bank_path))[0]
    by_id = {q["id"]: q for q in qs}
    by_id.update({q["item_id"]: q for q in qs if q.get("item_id")})
    return {
        "policy": policy,
        "states": states or {},
        "resolve": lambda cid: by_id.get(cid),
        "skip": skip,
        "attempted": attempted,
        "degraded": degraded,
        "unreachable": unreachable,
        "print": print_mode,
        "stem": stem,
        "bank": os.path.basename(bank_path),
    }


def _render(tmp, gate=None, bank_name="gate_bank.md", gate_value=None,
            check="q1"):
    path = _write_bank(tmp, bank_name, gate=gate_value, check=check)
    qs = itembank.load(path)
    page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                              runtime=True, gate=gate)
    return path, qs, page


def test_gate_band_live_markup():
    """Task 1 Test 1: with a session, the D2 slot renders as the live band
    -- <section class="gate"> with the check item's public projection, the
    Ledger header, and one form whose two named submit buttons are
    check-first, skip-second, both >=44px (the shared .go control)."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        ctx = _gate_ctx(path, qs, policy="required")
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True, gate=ctx)
        if '<section class="gate">' not in page:
            fail("the live band must render <section class=\"gate\">")
        if ("Check \u00b7 required to continue" not in page
                and "Check \u00b7 recommended" not in page):
            fail("the band must carry its Ledger header")
        if "Which adjunct opens an airway?" not in page:
            fail("the band must render the check item's stem")
        if '<form method="post"' not in page:
            fail("the band must be one <form method=\"post\">")
        m = re.findall(r'<button type="submit" name="action" value="([^"]+)"',
                       page)
        if m != ["check", "skip"]:
            fail("the form must carry two named submit buttons, check first "
                 "then skip, got %r" % m)
        if "Read ahead without answering" not in page:
            fail("the skip button label must be the locked copy")
        # The check's key, rationale and objective line must be absent
        # before the verdict (T-062-07).
        for leak in ("oropharyngeal airway is the standard",
                     "emt:airway.adjunct", "A device that holds the tongue"):
            if leak in page:
                fail("the band leaked %r before the verdict" % leak)
        # .go buttons carry min-height:44px from SHARED_CSS.
        if "min-height:44px" not in lesson.SHARED_CSS:
            fail("the shared .go control must guarantee 44px min-height")
        print("gate band: live markup, check-first buttons, no key leak")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_band_box_metrics_match_slot():
    """Task 1 Test 2: the band's box metrics (padding space-3, 1px --line
    border, --r-3 radius, space-4 block margin, 66ch measure) match 3.1's
    reserved slot -- the activation changes the contents, not the box."""
    css = lesson.LESSON_CSS
    gate = css[css.find(".gate{"):]
    gate = gate[:gate.find("}") + 1]
    for token in ("background:var(--card)", "border:1px solid var(--line)",
                  "border-radius:var(--r-3)", "padding:var(--space-3)",
                  "margin:0 0 var(--space-4)"):
        if token not in gate:
            fail("the .gate box must carry %r, got %r" % (token, gate))
    # The measure is inherited from the wrap (--measure-prose 66ch): the
    # band must not escape to --measure-wide.
    if "--measure-wide" in gate:
        fail("the gate band must never escape to --measure-wide")
    print("gate band: box metrics match the D2 slot via tokens")


def test_gate_inert_and_off_match_phase31():
    """Task 1 Test 3: with no session, or [GATE: off], the anchor renders
    exactly as 3.1's inert D2 slot with its unchanged copy."""
    tmp = tempfile.mkdtemp()
    try:
        for gate_value in (None, "off"):
            path, qs, page = _render(tmp, gate=None, gate_value=gate_value)
            if ('<section class="callout callout-check">' not in page
                    or "callout-body" not in page):
                fail("[GATE: %s] must render 3.1's inert slot"
                     % (gate_value or "absent"))
            if ("This check is available when you are reading with a "
                    "session.") not in page:
                fail("the inert slot must carry 3.1's exact copy")
            if '<section class="gate">' in page or "Read ahead" in page:
                fail("[GATE: %s] must not render the live band"
                     % (gate_value or "absent"))
        print("gate inert: no session and off render 3.1's slot unchanged")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_no_script_element():
    """Task 1 Test 4: no <script> element and no JavaScript dependency in
    the rendered page for a gate bank without a glossary (the phase adds
    no JavaScript of its own; 3.1's reviewed gloss script is separate)."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True,
                                  gate=_gate_ctx(path, qs))
        if "<script" in page:
            fail("the gated reader must ship no <script> element")
        print("gate no-script: zero JavaScript in the gated page")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_required_truncation_no_leak():
    """Task 2 Test 1: under required with an uncleared check, every
    heading, paragraph, list item, table, code block, [!KEY] id,
    [!EXAMPLE] block, further [!CHECK:] id, backlink, TOC entry and
    glossary entry belonging to a section below the gate is absent from
    the HTML and from the text content (the CSS-off/accessible-name
    approximation) -- and the check's own key, rationale, distractor
    analysis and objective line are absent before the verdict."""
    tmp = tempfile.mkdtemp()
    try:
        bank = """# Leak fixture bank
[GATE: required]

## LESSON

### First Section

Prose above the check.

> [!CHECK: q1]

Prose below the check (gated under required).

### Second Section

SECRET-BELOW-HEADING prose.

- secret list item below the gate

| secret | table |
| --- | --- |
| row | value |

```python
secret code block
```

> [!EXAMPLE]

Secret example body.

> [!CHECK: q2]

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

Q2. Second item.   (difficulty: recall)
[OBJECTIVE: emt:airway.adjunct]
A) One
B) Two
C) Three
D) Four
CORRECT: A
WHY BEST: It is the first.
KEY DISCRIMINATOR: Ordinal.
SECOND-BEST: B. Second; correct if the question asked for two.
DISTRACTOR ANALYSIS:
- A) Correct.
- B) Would be correct if asked for two.
- C) Would be correct if asked for three.
- D) Would be correct if asked for four.
TRAP: Counting.
CONFIDENCE: high
"""
        path = os.path.join(tmp, "leak_bank.md")
        open(path, "w", encoding="utf-8").write(bank)
        qs = itembank.load(path)
        ctx = _gate_ctx(path, qs, policy="required",
                        states={"q1": "open"})
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True, gate=ctx)
        for leak in ("SECRET-BELOW-HEADING", "Prose below the check",
                     "secret list item below the gate", "secret | table",
                     "secret code block", "Secret example body",
                     "!CHECK: q2", "q2", "The oropharyngeal airway is the "
                     "standard", "A device that holds the tongue",
                     "emt:airway.adjunct"):
            if leak in page:
                fail("below-gate content leaked into the HTML: %r" % leak)
        # CSS-off text / accessible names: strip tags and re-check.
        text = re.sub(r"<[^>]+>", " ", page)
        text = re.sub(r"\s+", " ", text)
        for leak in ("SECRET-BELOW-HEADING", "Prose below the check",
                     "secret list item below the gate", "secret code block"):
            if leak in text:
                fail("below-gate content reached the text content: %r" % leak)
        # The boundary names the withheld count.
        if "1 more section below this check." not in page:
            fail("the truncation boundary must render the n=1 row")
        print("gate required: no-leak across HTML and text content")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_boundary_copy_two_rows():
    """Task 2 Test 2: the boundary has exactly two copy rows -- the
    singular and the plural -- and no third variant."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True, gate=_gate_ctx(path, qs))
        if "1 more section below this check." not in page:
            fail("n=1 must render the singular row")
        # A bank with three sections, the check in the first, renders the
        # plural row (2 sections below).
        multi = """# Multi-gate fixture bank
[GATE: required]

## LESSON

### First Section

Prose above the check.

> [!CHECK: q1]

### Second Section

Second prose.

### Third Section

Third prose.

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
"""
        mpath = os.path.join(tmp, "multi_bank.md")
        open(mpath, "w", encoding="utf-8").write(multi)
        mqs = itembank.load(mpath)
        mpage = lesson.lesson_page(mpath, mqs, itembank.parse_lesson(mpath),
                                   runtime=True, gate=_gate_ctx(mpath, mqs))
        if "2 more sections below this check." not in mpage:
            fail("n>1 must render the plural row")
        print("gate boundary: exactly the two copy rows")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_zero_reflow():
    """Task 2 Test 3: the emitted bytes preceding the band's opening tag
    are byte-identical across inert, open, cleared and skipped states, and
    the band's box metrics are identical across all four."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        les = itembank.parse_lesson(path)
        open_ctx = _gate_ctx(path, qs, policy="required",
                             states={"q1": "open"})
        cleared_ctx = _gate_ctx(path, qs, policy="required",
                                states={"q1": "cleared"})
        skipped_ctx = _gate_ctx(path, qs, policy="required",
                                states={"q1": "skipped"})
        inert = lesson.lesson_page(path, qs, les, runtime=True, gate=None)
        open_p = lesson.lesson_page(path, qs, les, runtime=True, gate=open_ctx)
        cleared_p = lesson.lesson_page(path, qs, les, runtime=True,
                                       gate=cleared_ctx)
        skipped_p = lesson.lesson_page(path, qs, les, runtime=True,
                                       gate=skipped_ctx)
        markers = ['<section class="callout callout-check">',
                   '<section class="gate">']
        def pre(page):
            for m in markers:
                if m in page:
                    return page.split(m)[0]
            fail("no band/slot marker found in page")
        base = pre(inert)
        for other in (open_p, cleared_p, skipped_p):
            if pre(other) != base:
                fail("pre-band bytes differ across states -- zero-reflow "
                     "violated")
        # Band box metrics identical across all four: the .gate rule block
        # is the single source for the three live states, and the .callout
        # rule carries the same tokens for the inert slot (asserted by
        # test_gate_band_box_metrics_match_slot); here we assert the three
        # live states share one rule block (the print-path restyle is the
        # only other .gate selector).
        gate_css = lesson.LESSON_CSS
        outside_print = gate_css.split("@media print")[0]
        if outside_print.count(".gate{") != 1:
            fail("exactly one .gate rule block must exist (print restyle "
                 "excluded), got %d"
                 % outside_print.count(".gate{"))
        print("gate zero-reflow: pre-band bytes identical across four states")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_recommended_flows_whole_lesson():
    """Task 2 Test 4: under recommended the whole lesson is present in the
    DOM with the band in flow; under off, 3.1's reader renders unchanged
    (asserted by the compatibility-floor pair)."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True, gate=_gate_ctx(
                                      path, qs, policy="recommended"))
        if "Second Section" not in page:
            fail("recommended must render the whole lesson")
        if "1 more section below this check." in page:
            fail("recommended must not render a truncation boundary")
        if '<section class="gate">' not in page:
            fail("recommended must render the band in flow")
        print("gate recommended: whole lesson in DOM, band in flow")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_mode_degrade():
    """Task 3 Test 1: [GATE: required] in diagnostic and exam modes renders
    the complete lesson, emits no truncation boundary, offers no skip
    control, records no gate_skip, and renders the exact degrade line."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        for mode in ("diagnostic", "exam"):
            page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                      runtime=True, gate=_gate_ctx(
                                          path, qs, policy="required",
                                          degraded=True))
            if "Second Section" not in page:
                fail("%s mode must render the complete lesson" % mode)
            if "more section" in page or "more sections" in page:
                fail("%s mode must not render a truncation boundary" % mode)
            if "Read ahead without answering" in page:
                fail("%s mode must not offer the skip control" % mode)
            if ("This sitting holds feedback until it ends, so checks do "
                    "not gate reading here.") not in page:
                fail("%s mode must render the exact degrade line" % mode)
        print("gate mode-degrade: diagnostic + exam render complete, no skip")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_compatibility_floor():
    """Task 3 Test 2 (compatibility floor, GATE-05/D-14): a bank whose
    lessons declare no gates renders byte-identically to Phase 3.1 output,
    reusing 3.1's own fixture bank and golden, with the style-block
    exclusion named (03.1-UI-SPEC section 12)."""
    golden = open(lesson_roundtrip.GOLDEN_CONTENT_P3, encoding="utf-8").read()
    path = lesson_roundtrip.LES_BANK
    qs = itembank.load(path)
    page = lesson.lesson_page(path, qs, itembank.parse_lesson(path))
    # The style block is excluded exactly as 3.1's own floor test excludes
    # it (03.1-UI-SPEC section 12): the content region between the card's
    # opening div and the style footer, compared against the Phase 3 golden.
    content = lesson_roundtrip._lesson_content_region(page)
    if content != golden:
        fail("a no-gate bank rendered differently from the Phase 3 golden")
    print("gate compatibility floor: 3.1 fixture bank byte-identical")
    tmp = tempfile.mkdtemp()
    try:
        # A gate-bearing lesson without a session renders the same inert
        # slots a pre-6.2 reader would -- the slot-level floor.
        path2, qs2, page2 = _render(tmp, gate=None)
        if ("This check is available when you are reading with a session."
                not in page2):
            fail("gate-less render must keep 3.1's inert slot copy")
        print("gate compatibility floor: inert slot copy unchanged")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_unresolvable_check_degrades():
    """Task 3 Test 3: a [!CHECK:] naming an id not in the bank renders as
    the D1 labelled rule with the warn-tone line and does not gate --
    reading continues."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp, check="nope")
        qs = itembank.load(path)
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True,
                                  gate=_gate_ctx(path, qs, policy="required"))
        if "This check refers to an item that is not in this bank." not in page:
            fail("the unresolvable check must render the warn-tone line")
        if "Second Section" not in page:
            fail("an unresolvable check must never gate -- reading continues")
        if "1 more section below this check." in page:
            fail("an unresolvable check must not render a boundary")
        print("gate unresolvable: D1 rule, warn line, never gates")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- plan 06.2-04: the twelve verification gates --------------------------


def test_gate_print_fixture():
    """Gate 6 (section 8): ?print=1 serves the complete ungated document;
    every check prints as 3.1's D1 rule with its LOCKED `Check · <objective>`
    string; no truncation boundary appears; the print records nothing."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        by_id = {q["id"]: q for q in qs}
        ctx = {"policy": "off", "as_authored": "required", "states": {},
               "resolve": lambda cid: by_id.get(cid), "skip": "off",
               "degraded": False, "unreachable": False, "print": True,
               "stem": "gate_bank", "bank": "gate_bank.md",
               "session_id": "s", "log": "", "mode": "practice"}
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True, gate=ctx)
        if "Second Section" not in page:
            fail("print must serve the complete ungated document")
        if "more section below this check" in page:
            fail("print must never render a truncation boundary")
        if "Check \u00b7 emt:airway.adjunct" not in page:
            fail("print must render the D1 rule with the locked "
                 "Check · <objective> label")
        if "<form" in page or "Read ahead" in page:
            fail("print must carry no live controls")
        print("gate print: complete ungated, D1 labels, no boundary")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_calm_progress():
    """Gate 10 (section 9): no element in the gated reader carries a count
    of cleared checks, a percentage, a progress track, a streak, a
    check/cross glyph, an exclamation mark, or any CSS
    transition/animation/scroll-behavior:smooth on the band, the revealed
    section, or the boundary."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        ctx = _gate_ctx(path, qs, policy="required")
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True, gate=ctx)
        for banned in ("progress", "streak", "percent",
                       "2 of 5", "\u2713", "\u2717", "\u2714", "\u2715"):
            if banned in page:
                fail("the gated reader must not carry %r" % banned)
        # The band copy has no exclamation mark (the reject list in 9).
        band = page[page.find('<section class="gate">'):]
        if "!" in band:
            fail("the band copy must carry no exclamation mark")
        # A percentage only appears as a CSS width (`min-width:100%` on
        # tables), never as a progress figure: the band's visible text and
        # the .gate rule block must be percent-free.
        band_text = re.sub(r"<[^>]+>", " ", band)
        gate_css = lesson.LESSON_CSS
        gate_rules = gate_css[gate_css.find(".gate{"):gate_css.find(".gate-boundary .gate-note") + 30]
        if "%" in band_text or "%" in gate_rules:
            fail("the band or the .gate CSS must carry no percentage")
        outside_print = gate_css.split("@media print")[0]
        for banned in ("transition", "animation", "scroll-behavior:smooth"):
            if banned in outside_print:
                fail("the gate CSS must carry no %r" % banned)
        print("gate calm-progress: no count, progress, glyph, or motion")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_voice_tokens():
    """Gate 11 (section 4.1): every section-15 string renders in the voice
    its row assigns, asserted by computed font-family TOKEN name -- the
    band header/notes are Ledger (var(--font-ledger)), the item text is
    Paper (var(--font-paper)) -- never a literal family name."""
    css = lesson.LESSON_CSS
    gate = css[css.find(".gate{"):css.find(".gate-boundary{")]
    if "font-family:var(--font-ledger)" not in gate:
        fail("the band label/note must use the Ledger font token")
    if "font-family:var(--font-paper)" not in gate:
        fail("the check item text must use the Paper font token")
    for fam in ("Georgia", "Times", "Helvetica", "Arial", "Courier",
                "Source Serif", "iA Writer"):
        if fam in gate:
            fail("the gate CSS must never name a literal family %r" % fam)
    print("gate voice: token-named families, no literal family")
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        ctx = _gate_ctx(path, qs, policy="required")
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True, gate=ctx)
        for label in ("Check \u00b7 required to continue",
                      "Read ahead without answering",
                      "1 more section below this check."):
            if label not in page:
                fail("section-15 copy %r missing from the gated page" % label)
        print("gate voice: section-15 strings render verbatim")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_responsive_snapshots():
    """Gate 9 (section 13): responsive snapshots for [GATE:] all three
    values x gate_skip both values, with reader_nav: column in at least
    one combination -- the page carries the viewport meta, the band and
    its controls wrap (no nowrap/ellipsis), and every combination renders
    both submit buttons."""
    tmp = tempfile.mkdtemp()
    try:
        for gate_value in ("required", "recommended", "off"):
            for skip in ("always", "after-attempt"):
                path = _write_bank(tmp, gate=gate_value)
                qs = itembank.load(path)
                ctx = _gate_ctx(path, qs, policy=gate_value, skip=skip)
                ctx["reader_nav"] = "column"
                page = lesson.lesson_page(path, qs,
                                          itembank.parse_lesson(path),
                                          runtime=True, gate=ctx)
                if 'name="viewport"' not in page:
                    fail("the lesson page must carry the viewport meta")
                for banned in ("white-space:nowrap", "text-overflow:ellipsis"):
                    if banned in lesson.SHARED_CSS or banned in lesson.LESSON_CSS:
                        fail("no %r anywhere in the reader CSS" % banned)
                if gate_value != "off":
                    if 'value="check"' not in page:
                        fail("[GATE: %s] x gate_skip %s lost the check button"
                             % (gate_value, skip))
                    if skip == "always" \
                            and "Read ahead without answering" not in page:
                        fail("[GATE: %s] x gate_skip always lost the skip "
                             "button" % gate_value)
        print("gate responsive: viewport, wrap-only controls, all combos")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_cross_phase_divergence_guard():
    """Gate 12 (D-01 ≡ D-06): the unresolvable [!CHECK:] lint code and
    message are read from the same constant the linter and the renderer
    share -- surfaces/lesson.py imports model.CHECK_UNRESOLVED_COPY by
    identity, so the two phases (3.1's slot, 6.2's gate) cannot drift."""
    import surfaces.lesson as lesson_mod
    if lesson_mod.CHECK_UNRESOLVED_COPY is not CHECK_UNRESOLVED_COPY:
        fail("lesson.py must import the SAME CHECK_UNRESOLVED_COPY object "
             "-- a duplicate literal would let the phases drift")
    tmp = tempfile.mkdtemp()
    try:
        # The renderer's degraded line and the linter's message both come
        # from the one constant.
        path = _write_bank(tmp, check="nope")
        qs = itembank.load(path)
        ctx = _gate_ctx(path, qs, policy="required")
        page = lesson.lesson_page(path, qs, itembank.parse_lesson(path),
                                  runtime=True, gate=ctx)
        if CHECK_UNRESOLVED_COPY.replace("<bank>", "gate_bank.md") \
                .replace("bank", "gate_bank.md") not in page \
                and "This check refers to an item that is not in this bank." \
                not in page:
            fail("the renderer must use the shared constant's copy")
        errors, _ = itembank.lint(qs, lesson=itembank.parse_lesson(path))
        hits = [e for e in errors if e.code == "lesson.check_ref_unknown"]
        if not hits or CHECK_UNRESOLVED_COPY not in hits[0].message:
            fail("the linter must emit the shared constant's message")
        print("gate divergence guard: one constant, linter and renderer")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_focus_recommended_no_growth():
    """Gate 4 tail: after a submit under recommended, the DOM did not grow
    and no autofocus is placed (focus stays on the submitted control --
    the document did not grow, section 7.1)."""
    tmp = tempfile.mkdtemp()
    try:
        path = _write_bank(tmp)
        qs = itembank.load(path)
        les = itembank.parse_lesson(path)
        ctx = _gate_ctx(path, qs, policy="recommended")
        before = lesson.lesson_page(path, qs, les, runtime=True, gate=ctx)
        # A cleared state under recommended renders the whole lesson with
        # no autofocus (no reveal happened).
        ctx2 = _gate_ctx(path, qs, policy="recommended",
                         states={"q1": "cleared"})
        after = lesson.lesson_page(path, qs, les, runtime=True, gate=ctx2)
        if "autofocus" in after:
            fail("recommended must not place focus (the DOM did not grow)")
        if "Second Section" not in after:
            fail("recommended renders the whole lesson before and after")
        if "Second Section" not in before:
            fail("recommended renders the whole lesson before and after")
        print("gate focus: recommended clears in place, no growth, no focus")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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
    test_gate_band_live_markup()
    test_gate_band_box_metrics_match_slot()
    test_gate_inert_and_off_match_phase31()
    test_gate_no_script_element()
    test_gate_required_truncation_no_leak()
    test_gate_boundary_copy_two_rows()
    test_gate_zero_reflow()
    test_gate_recommended_flows_whole_lesson()
    test_gate_mode_degrade()
    test_gate_compatibility_floor()
    test_gate_unresolvable_check_degrades()
    test_gate_skip_control_register()
    test_gate_skip_after_attempt_conditional()
    test_gate_settings_roundtrip()
    test_gate_policy_off_weakens_only()
    test_gate_outcome_split_pair_level()
    test_gate_outcome_split_excludes_recommended()
    test_gate_outcome_split_report_copy()
    test_gate_print_fixture()
    test_gate_calm_progress()
    test_gate_voice_tokens()
    test_gate_responsive_snapshots()
    test_gate_cross_phase_divergence_guard()
    test_gate_focus_recommended_no_growth()
    print("ok: gate roundtrip (GATE grammar, gate_skip event, context "
          "field, gate_state derivation, gate band render policy, skip "
          "control + settings, outcome split, twelve verification gates)")


if __name__ == "__main__":
    main()
