# Phase 16A: Semantic Capability & Activity Contract - Pattern Map

**Mapped:** 2026-08-15
**Files analyzed:** 8 (new or modified)
**Analogs found:** 6 real, executed analogs / 8; 2 files (`capability_stress_corpus_tracer.py`
naming precedent, `corpus_14b.py` naming precedent) have only plan-text
analogs because the modules they are patterned on (14A/14B) have not executed.
Confirmed this session: no `tests/three_domain_tracer.py`, no
`tests/file_fault_tracer.py`, and no `fixtures/corpus_14b.py` exist on disk.
Those names appear only inside `14A-*-PLAN.md`/`14B-*-PLAN.md` text and must
be treated as plan-text analogs, never as existing code, exactly as
16A-RESEARCH.md's own caveat states.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `surfaces/lesson.py` (`_CALLOUT_KINDS` +7 entries) | component (renderer registry) | transform (markdown block to rendered container) | `surfaces/lesson.py:648-653` (`_CALLOUT_KINDS` itself, same file) | exact (in-place additive registration) |
| `model.py` (new preamble section reader, if media/activity grammar needs one) | model/parser | transform (markdown to dict) | `model.py:574-602` (`_preamble_section`) | exact |
| `capabilities.py` (new) | model/registry (pure, no I/O) | CRUD (in-memory lookup) | `model.py:2052` (`GATE_VALUES` closed-tuple constant shape); planned `graph.py`'s no-file-I/O pure-registry pattern (`14B-01-PLAN.md:112-118`, plan-text only) | role-match (real); plan-text (structural precedent) |
| `schemas/capability_profile.schema.json` (new, if checkpoint:decision selects a published schema) | config/schema | transform (validation) | `schemas/visual_interaction.schema.json` (closed `oneOf`/`enum`/`$defs` shape) + `schema_validate.py` (the one hand-rolled validator every schema under `schemas/` is checked against) | exact |
| `fixtures/lesson_capability_corpus.py` (new) | test fixture / factory | batch (generates fictional corpus content) | `fixtures/grandchild_spawner.py` (closest real Python fixture generator in `fixtures/`) for module shape; planned `fixtures/corpus_14b.py` (`14B-RESEARCH.md`, plan-text only) for the fictional-content/fixed-seed convention this phase must also follow | partial (real); plan-text (convention) |
| `tests/capability_stress_corpus_tracer.py` (new) | test (tracer/scenario suite) | batch (drives real parser+renderer over fixture corpus) | `tests/evidence_roundtrip.py` (real: `fail(msg)` helper, subprocess-driven CLI scenarios, EXPECTED_KEYS-style structural assertions) for the actually-shipped scenario-test convention; planned `tests/three_domain_tracer.py`/`tests/file_fault_tracer.py` (14B/14A plan text only) for the specific "TRACER: N passed, M skipped, 0 failed" summary-line convention named in RESEARCH.md | role-match (real); plan-text (summary-line convention) |
| `tests/assessment_authority_adversarial.py` (new) | test (adversarial/security) | event-driven (scripted attacker calls real gates) | `runtime.py:1509-1531` (`glossable()`, the gate under attack) + `evidence.py:1416-1451` (`mark_event()`, the gate under attack) + `tests/evidence_roundtrip.py` (real end-to-end CLI-driven test structure to model the suite on) | exact (gates); role-match (test structure) |
| `fixtures/lesson_golden_phase3_parse.json` (extended, not replaced) | fixture / golden snapshot | batch (byte-identical regression fixture) | `fixtures/lesson_golden_phase3_parse.json` itself (already shipped; extend, do not fork a second golden file) | exact |

## Pattern Assignments

### `surfaces/lesson.py` (`_CALLOUT_KINDS` extension) (component, transform)

**Analog:** `surfaces/lesson.py:643-653` and `:875-887` (same file, in place)

**Core registration pattern** (lines 643-653, quoted verbatim):
```python
# The locked callout kinds (03.1-UI-SPEC 9.2-9.4): each maps to the exact
# Ledger-voice label the renderer and the linter share (15). The `CHECK:`
# prefix is handled separately as the inert reserved slot (D-18). Adding a
# kind is a one-line registration here -- the container and its degradation
# contract do not change.
_CALLOUT_KINDS = {
    "KEY": ("key", "Key point"),
    "EXAMPLE": ("example", "Example"),
    "NOTE": ("note", "Note"),
    "WARNING": ("warning", "Warning"),
}
```

**Degradation/fallback pattern** (lines 875-887, `_callout_kind_of`, abridged):
```python
def _callout_kind_of(line):
    """The dispatch key of one `> [!...]` line: the literal string "KEY"
    for any [!KEY] variant, the locked (slug, label) pair for the generic
    kinds, or None for an unknown kind that must degrade to the pre-change
    paragraph output."""
    m = _CALLOUT_MARK_RE.match(line)
    if m is None:
        return None
    kind = m.group(1)
    if kind == "KEY" or kind.startswith("KEY:"):
        return "KEY"
    return _callout_spec(kind)
```
An unknown kind returns `None` and falls through to plain-paragraph output
rather than raising. The seven new roles (`PREREQUISITE`, `MISCONCEPTION`,
`TIP`, `COUNTEREXAMPLE`, `EXCERPT`, `UNCERTAINTY`, `SUMMARY`, exact tokens
per RESEARCH.md Assumption A1) are added as dict entries only; no new
parsing branch, no new container.

---

### `model.py` (new preamble section reader) (model/parser, transform)

**Analog:** `model.py:574-602`, `_preamble_section`

**Boundary-rule pattern** (docstring, quoted verbatim, abridged):
```python
def _preamble_section(head, name):
    """THE boundary rule, defined once for every preamble registry: a
    preamble section runs until the next level-two heading or the first
    question, whichever comes first. `parse_terms`, `parse_sources` and
    `parse_cases` -- plus the lesson-body [[term]] refs scan -- all read
    through this one definition, so the file carries one boundary rule
    rather than four that can drift."""
    text = _STYLE_FENCE_RE.sub("", head or "")
    m = re.search(r"(?m)^##\s+%s\s*$" % re.escape(name), text)
    if m is None:
        return None
    body = text[m.end():]
    nxt = _PREAMBLE_HEADING_RE.search(body)
    return body[:nxt.start()] if nxt else body
```
Any new `## SECTION` this phase introduces (a media-asset registry
following `## SOURCES`'s precedent, an activity-declaration block) must call
`_preamble_section(head, "SECTION_NAME")`, never write a second
regex-based section-boundary scanner.

---

### `capabilities.py` (new) (model/registry, CRUD/lookup)

**Analog (real):** `model.py:2052`, `GATE_VALUES` closed-tuple shape

```python
# Source: model.py:2052, quoted verbatim
GATE_VALUES = ("required", "recommended", "off")
```
Every new closed vocabulary this module needs (a `renderer-availability`
tuple, `known-limits` categories) should be a plain module-level tuple
constant in this same shape, not an enum class or external config file.

**Analog (plan-text only, not executed):** `graph.py`'s no-file-I/O pure
module pattern, cited `[VERIFIED: 14B-01-PLAN.md:112-118]`. `graph.py` does
not exist on disk (confirmed this session). Its cited shape (`EDGE_TYPES`,
`TREATMENT_KINDS` as closed tuples, `outline_projection(doc)` as a pure
function with no I/O) is the structural precedent `capabilities.py` should
follow: a pure lookup module, no file reads, no session state, keyed by a
plain string name (here, capability name instead of edge type). Treat this
citation as unverified against real code; re-check if `14B-FREEZE.md`
lands before 16A executes.

**Do not fold into:** `model.py` (parsing-only scope) or the planned
`graph.py` (course-graph scope, orthogonal concern) -- see
Alternatives Considered in RESEARCH.md.

---

### `schemas/capability_profile.schema.json` (new, if selected) (config, transform)

**Analog:** `schemas/visual_interaction.schema.json` + `schema_validate.py`

**Closed-vocabulary schema shape** (`schemas/visual_interaction.schema.json:36-43`, quoted):
```json
"action_type": {
  "type": "string",
  "enum": ["place_point", "move_point",
           "select_numberline_point", "set_interval",
           "select_hotspot", "place_timeline_event",
           "move_timeline_event", "connect_diagram",
           "place_trace_point", "move_trace_point"]
}
```
Every new schema under `schemas/` is checked by `schema_validate.py`'s
hand-rolled subset validator (`type`, `properties`, `required`,
`additionalProperties`, `enum`, `const`, `items`, `minItems`, `uniqueItems`,
`minLength`, `pattern`, `minimum`, `maximum`, `$defs`, `$ref`, `oneOf` --
`schema_validate.py:27-31`). A schema using any keyword outside that set is
refused outright (`check_schema` walks the whole document first,
`schema_validate.py:13-19`), so a new `capability_profile.schema.json` must
stay inside this exact keyword set, matching `visual_interaction.schema.json`'s
own additive, closed-enum discipline (`additionalProperties: false`,
`required` listing every field, no open-ended free-form object).

---

### `fixtures/lesson_capability_corpus.py` (new) (test fixture, batch)

**Analog (real):** `fixtures/grandchild_spawner.py` -- the closest real
Python fixture-generator module shape in `fixtures/` (module-level
functions producing deterministic synthetic content, no real course/bank
data, consistent with the project's guard-checked fixture discipline).

**Analog (plan-text only):** `fixtures/corpus_14b.py`, cited
`[VERIFIED: 14B-RESEARCH.md]` as "fictional content only, fixed seed."
This file does not exist on disk (confirmed this session). Its cited
convention (fictional content, `random.Random(<fixed seed>)`, no real
course/learner/bank content) is the structural precedent to follow for
determinism; do not treat the filename or API as real until `14B-FREEZE.md`
lands.

**Mandatory acceptance check:** `python itembank.py guard .` must pass on
any task touching `fixtures/`, per RESEARCH.md's Security Domain table row
("Real course, learner, or bank content entering the repository").

---

### `tests/capability_stress_corpus_tracer.py` (new) (test/tracer, batch)

**Analog (real):** `tests/evidence_roundtrip.py`

**Shared test-file convention** (lines 1-40, quoted/abridged):
```python
#!/usr/bin/env python3
"""... Standard library only, runnable as `python tests/evidence_roundtrip.py`."""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402

def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)
```
Every `tests/*.py` file in this repo (confirmed by directory listing: no
pytest/unittest framework anywhere) defines its own local `fail(msg)`
helper and is directly executable via `python tests/<file>.py`. The new
tracer must follow this exact convention: no test framework dependency, a
local `fail()`, direct subprocess or direct-import driving of real code.

**Analog (plan-text only, summary-line convention):** `tests/three_domain_tracer.py`
and `tests/file_fault_tracer.py`, cited `[VERIFIED: 14B-01-PLAN.md]`/
`[VERIFIED: 14A-04-PLAN.md]`. Neither exists on disk (confirmed this
session). RESEARCH.md's cited structure for these (named `scenario_*()`
functions, a `main()` that runs each, and a final
`"TRACER: N passed, M skipped, 0 failed"` summary line) is the convention
`capability_stress_corpus_tracer.py` should also adopt, layered on top of
the real `fail(msg)`/direct-execution convention above. Re-verify this
naming/summary-line convention against real code once 14A/14B land.

---

### `tests/assessment_authority_adversarial.py` (new) (test/adversarial, event-driven)

**Analog:** `runtime.py:1509-1531` (`glossable`) and `evidence.py:1416-1451`
(`mark_event`) -- the real, shipped gates under attack -- plus
`tests/evidence_roundtrip.py`'s real end-to-end CLI-driven structure for
the suite's shape.

**The gate this suite must attack directly, never mock** (`runtime.py:1509-1520`, quoted):
```python
def glossable(qs, term):
    """The one gate between a term's definition and the learner: False when
    the definition text could disclose keyed answer material from any
    question in `qs`, True otherwise.

    This is the same class of decision as `public_item()` withholding a key:
    the runtime, not the author and not a model, decides what reaches the
    learner (Directive 4.1, D-20). It is deliberately conservative -- on any
    ambiguity it returns False. It is a pure function: no I/O, no side
    effects, deterministic across calls."""
```

**The human-only marking gate this suite must attack directly** (`evidence.py:1416-1451`, key lines):
```python
def mark_event(session_id, item_id, item_ref, marks_event, verdict, rubric=None,
                notes="", marker="human", proposal_ref=None):
    """`marker` must be `"human"` in this phase: a model verdict is not
    accepted evidence until Phase 8/TEACH-09 teaches the runtime to hold
    one as pending review."""
    ...
    if marker != "human":
        # rejects any marker other than the literal string "human"
```

**What NOT to do (Pitfall 5 from RESEARCH.md):** no `class Mock*` or
`def fake_*` standing in for `runtime.py`/`evidence.py`. A scripted
"agent" attempting to leak a key must literally call
`runtime.public_item()` (`runtime.py:44-73`) before a response exists and
assert the key/rationale/correct-answer fields are absent from the
returned dict; a scripted "import" attempting to invent a score must
literally call `evidence.append_event()`/`mark_event()` with a
manufactured event and assert rejection or `pending` status, never an
accepted score.

---

### `fixtures/lesson_golden_phase3_parse.json` (extended) (fixture, batch)

**Analog:** the file itself, already shipped on disk (confirmed present
this session at `fixtures/lesson_golden_phase3_parse.json`). PORT-01's
byte-identical additivity fixture (a bank/lesson using none of the seven
new callout kinds parses unchanged) extends this existing golden-parse
snapshot precedent rather than creating a second, competing golden file.

## Shared Patterns

### One-line additive registration (closed vocabulary, never a new branch)
**Source:** `surfaces/lesson.py:648-653` (`_CALLOUT_KINDS`), `model.py:2052`
(`GATE_VALUES`)
**Apply to:** the seven new callout kinds, `capabilities.py`'s closed
tuples (renderer-availability states, known-limits categories), any new
media-metadata enum field.
```python
GATE_VALUES = ("required", "recommended", "off")
```

### One boundary-rule function for every preamble section
**Source:** `model.py:574-602` (`_preamble_section`)
**Apply to:** any new `## SECTION` grammar (media registry, activity
declaration block, localization header fields) 16A adds to the lesson
preamble.

### The runtime, never the author or a model, decides disclosure
**Source:** `runtime.py:1509-1531` (`glossable`), `runtime.py:44-73`
(`public_item`)
**Apply to:** `tests/assessment_authority_adversarial.py`'s entire suite,
and any new attack surface 16A's own grammar introduces (for example, a
source-excerpt callout that could accidentally quote keyed rationale text
must be checked against this same class of gate, not a new leak-scanning
regex -- see RESEARCH.md's Don't Hand-Roll table).

### Human-only marking discipline
**Source:** `evidence.py:1416-1451` (`mark_event`)
**Apply to:** `tests/assessment_authority_adversarial.py`'s "auto-grade
prose" and "invent a score" attack scenarios.

### Shipped-suite regression discipline
**Source:** project convention, confirmed via `tests/*.py` directory
listing (60+ existing `*_roundtrip.py`/`*_audit.py` files, no framework)
**Apply to:** every new test file in this phase; full-suite check is
`for t in tests/*.py; do python "$t" || exit 1; done`.

### Hand-rolled JSON Schema validation, closed keyword set
**Source:** `schema_validate.py:27-31` (`SUPPORTED` keyword set),
`schemas/visual_interaction.schema.json` (closed `enum`/`oneOf`/`$defs` shape)
**Apply to:** `schemas/capability_profile.schema.json` if that
checkpoint:decision selects a published schema for the capability profile.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| Media-asset metadata grammar (new preamble block/section, exact file TBD by checkpoint:decision A3) | model/parser | transform | No existing block, callout kind, or item field carries rights/credit/derivation/availability/integrity metadata anywhere in `model.py` (confirmed by grep this session: no `figure`, `credit`, `rights`, or `derivation` handling exists). Closest structural precedent is `## SOURCES`/`## TERMS`'s preamble-section shape (see `_preamble_section` pattern above), but the field vocabulary itself is genuinely new; RESEARCH.md flags this `[ASSUMED]`, checkpoint:decision candidate A3. |
| Guided-mode data contract (stage sequencing, disclosure-state persistence) inside `surfaces/lesson.py` | presentation (new render path) | event-driven (stage transitions) | Does not exist in any form today; continuous reader mode is the only shipped presentation path. No in-repo analog; RESEARCH.md's own Architecture Patterns section states 16A must define this data contract from scratch, deferring visual tokens to Phase 17A. |
| Purpose-first activity declaration grammar (ten fields: purpose, cognitive demand, objective, stimulus/source, response schema, retry behavior, feedback/disclosure policy, evidence status, accessibility equivalence, static fallback) | model/parser (metadata attached to existing item types) | transform | No parser field carries "purpose" or "cognitive demand" today (confirmed by RESEARCH.md's own grep-based claim, corroborated this session by no matching field names found in `model.py`'s item dict shape at `runtime.py:44-73`). The ten-purpose taxonomy is sourced from research stream 03's matrix, not from shipped code. |
| Localization `lang`/`dir` header field | model/parser | transform | No document-level language/direction field exists; the only `[LANG:]` marker in `model.py` is a per-`check`-item programming-language tag, unrelated (confirmed `model.py:25,151-155` per RESEARCH.md, not independently re-read this session to conserve budget). |

## Metadata

**Analog search scope:** `surfaces/lesson.py`, `model.py`, `runtime.py`,
`evidence.py`, `schema_validate.py`, `schemas/*.json`, `tests/*.py`,
`fixtures/*.py`, plus a live filesystem check for the plan-text-only
modules/tests/fixtures RESEARCH.md cites from 14A/14B (`identity.py`,
`graph.py`, `course.py`, `tests/three_domain_tracer.py`,
`tests/file_fault_tracer.py`, `fixtures/corpus_14b.py`), all confirmed
`MISSING` this session, consistent with 16A-RESEARCH.md's own caveat.
**Files scanned:** 8 target files/classes plus roughly a dozen real
codebase files read or grepped for analog extraction.
**Pattern extraction date:** 2026-08-15

## PATTERN MAPPING COMPLETE
