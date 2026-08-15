# Phase 15B: Quality, Blueprint & Acceptance - Pattern Map

**Mapped:** 2026-08-15
**Files analyzed:** 7 (new files/functions named in 15B-RESEARCH.md's Recommended Project Structure and "New in this phase" table)
**Analogs found:** 7 / 7 (5 against shipped, executed code; 2 against planned-but-unexecuted plan text, cited as such per the research's Critical Caveat)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality | Analog Status |
|--------------------|------|-----------|-----------------|----------------|----------------|
| `blueprint.py` (new pure model-tier module: blueprint schema logic, `blueprint_gate`, staleness classifier, `STALENESS_DISPOSITIONS`, course-audit aggregation) | model/service (pure classifier, no I/O) | transform (CRUD-adjacent: classify, never write) | `auditor.py` (`coverage_report`, a pure citation-first transform) | role-match, same data-flow (pure function in, structured report out, no file I/O) | Shipped, executed |
| `schemas/blueprint.schema.json` (new: `construct`, `domain_weight`, `demand`, `format`, `difficulty`, `timing`, `tools`, `feedback_conditions`, `citations`) | config (JSON Schema contract) | request-response (validated at write time) | `schemas/quality_finding.schema.json` | exact (same "closed, `additionalProperties: false`, `x-itembank-version`, `schema_version` const" shape convention) | Shipped |
| `blueprint_gate` (new gate function, sibling to `authoring.quality_gate`, wired into `authoring.run_authoring`'s gate list) | service (gate/classifier) | request-response (findings list in, block/warn decision out) | `authoring.py`'s `quality_gate` / `quality_gate_blocks` (lines 539-559) | exact (same role: closed-vocabulary detector composition feeding one findings list, same severity-gate shape) | Shipped, executed |
| `graph.accept_migration` / `graph.reject_migration` (new functions on the planned `graph.py`, closing 14B-04's deliberately left-open acceptance gap) | service (state-transition / acceptance) | CRUD (state transition on an existing proposal record) | `audit_writer.write_units` / `undo` (lines 288-511, 485+) for the compare-and-swap acceptance *pattern*; `graph.migration_proposal` / `MIGRATION_STATES` / `migration_state_not_settable` (14B-04-PLAN.md) for the exact object and vocabulary being extended | role-match on data flow (compare-and-swap acceptance with a refusal code on mismatch); the object itself is plan text, not shipped code | Plan text: `.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md` (lines 91-100, 280-286, 560-561) |
| Course-audit report function (new, composing `director.untreated_objectives`, `director.classify_coverage`/`graph.BINDING_STATES`, `authoring.quality_gate` findings, and blueprint compliance) | service (read-only aggregation/report) | transform (multiple read-only signals in, one cited report out) | `auditor.py` (`coverage_report`, lines 370-421) for the aggregation/report shape; `schemas/audit_report.schema.json` for the report envelope; `director.untreated_objectives` / `classify_coverage` (15A-01-PLAN.md, 15A-04/05-PLAN.md) for two of the three input signals | role-match, same data-flow (pure aggregation over precomputed signals into one schema-validated report) | Shipped (`auditor.py`, both schemas) + plan text (`director.py`, 15A-*-PLAN.md) for two input signals |
| `tests/acceptance_tracer.py` (new: freeze-gate tracer covering ACTIVITY-02, RELIABILITY-03, AGENT-03 in one run) | test | event-driven (scenario functions run in sequence, each asserting a gate/refusal/disposition) | `tests/audit_authoring_roundtrip.py`, `tests/audit_quality_roundtrip.py`, `tests/audit_coverage_roundtrip.py` (direct-execution `fail(msg)` convention exercising `authoring.py`/`auditor.py`) for the shipped direct-execution test shape; `tests/four_subject_review.py` (15A) and `tests/three_domain_tracer.py` (14B) for the named `scenario_*()` + final `"TRACER: N passed, M skipped, 0 failed"` line convention this file must follow per research | role-match, same data-flow; the exact tracer files named in research (`four_subject_review.py`, `three_domain_tracer.py`) do not exist on disk yet, so the executable shipped convention is drawn from the `audit_*_roundtrip.py` family instead | Shipped convention (`tests/audit_*_roundtrip.py`) + plan text naming (15A/14B research references to files not yet created) |
| `fixtures/corpus_14b.py` extension (fifth fixture builder: synthetic blueprint + drafted question set + lesson stand-in) | utility (fixture builder) | batch (deterministic synthetic data construction, fixed seed) | No shipped `fixtures/corpus_14b.py` exists yet (confirmed `MISSING` per research's Critical Caveat); closest shipped analog is any fixture-construction helper already used by `tests/audit_*_roundtrip.py` (inline synthetic bank text/question dicts built directly in the test file, since this project has no standalone `fixtures/` package shipped today) | no analog (file itself is planned by 14B/15A, not yet executed; content convention is drawn from inline test fixtures) | Plan text (14B/15A research) + shipped convention (inline fixtures in `tests/audit_*_roundtrip.py`) |

## Pattern Assignments

### `blueprint.py` (model/service, pure transform)

**Analog:** `auditor.py`'s `coverage_report` (lines 370-421), a pure citation-first classifier with no file I/O, evidence import, or global state.

**Core pattern** (`auditor.py:370-421`):
```python
def coverage_report(normalized, questions, bank_fingerprint=None,
                    evidence=None, tool_version=TOOL_VERSION):
    """Pure function: a normalized document, the exact parsed bank questions,
    and optional evidence assertions in, a strict audit_report dict out --
    nothing is read or written. ..."""
    questions = questions or []
    evidence = evidence or []
    ...
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "coverage",
        "request_fingerprint": "",
        "coverage": rows,
        "stale": _evidence_stale(normalized, evidence, current_bank_fp),
        "bank_fingerprint": current_bank_fp or "",
        "source_fingerprints": [normalized["fingerprint"]],
        "tool_version": tool_version,
    }
```
`blueprint.py`'s `classify_staleness(base_fingerprint, current_fingerprint)` should follow this exact shape: precomputed fingerprints passed in as arguments (never read from disk by this module itself), a boolean derived deterministically, no caching. This mirrors the `"stale"` field's own doc comment in `schemas/audit_report.schema.json:86-89` (quoted below under Shared Patterns).

**Closed-vocabulary constant convention** (compare to `authoring.py:65-70`, `DETECTOR_VERSIONS`):
```python
DETECTOR_VERSIONS = {
    "answer_skew": 1,
    "near_duplicate_stems": 1,
    "answer_leak": 1,
    "distractor_rationale": 1,
}
```
`STALENESS_DISPOSITIONS` in `blueprint.py` should be minted the same way: a module-level tuple/dict constant, not a free-text field, following this project's closed-vocabulary discipline. Per 15B-RESEARCH's assumption A4, this should be exactly `("rebind", "migrate", "supersede", "retain")`, kept distinct from `graph.MIGRATION_STATES` (`"proposed"`, `"accepted"`, `"rejected"`) and `journal.OPERATION_TYPES`.

**Never combine into one score:** `authoring.py`'s module docstring (lines 26-31) states the second quality gate's detectors "never [produce] an aggregate score." `blueprint.classify_staleness` and any blueprint-fidelity classifier in `blueprint.py` must follow the same discipline: return per-field findings, not one opaque compliance percentage, consistent with AGENT-03's ban on a `mastery`/`progress`/`percent`/`score` key.

---

### `schemas/blueprint.schema.json`

**Analog:** `schemas/quality_finding.schema.json` (lines 1-30 read; full file is 148 lines per research).

**Shape convention to copy exactly** (`schemas/quality_finding.schema.json:1-18`):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://itembank.local/schemas/quality_finding.schema.json",
  "title": "itembank quality finding",
  "description": "...",
  "x-itembank-version": 1,
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "detector",
    "detector_version",
    "severity",
    "code",
    "item",
    "evidence",
    "remediation"
  ],
  ...
}
```
`schemas/blueprint.schema.json` should use the identical envelope shape (`$schema`, `$id`, `title`, `description`, `x-itembank-version`, `type: object`, `additionalProperties: false`, a `required` array, `properties`), with `required` naming ACTIVITY-02's eight fields verbatim (`construct`, `domain_weight`, `demand`, `format`, `difficulty`, `timing`, `tools`, `feedback_conditions`) plus `citations`, whose `{source_object_id, locator}` shape should copy `schemas/treatment_recommendation.schema.json` (15A, plan text only, not yet on disk).

---

### `blueprint_gate` (service, gate function)

**Analog:** `authoring.py`'s `quality_gate` and `quality_gate_blocks` (lines 539-559).

**Core pattern to copy** (`authoring.py:539-559`):
```python
def quality_gate(questions, profile=None):
    """Run all four named detectors over the complete proposed bank and
    return versioned findings sorted deterministically by (item, detector,
    evidence key). Never an aggregate score..."""
    findings = (
        detect_answer_skew(questions) +
        detect_near_duplicates(questions) +
        detect_answer_leak(questions) +
        detect_distractor_rationale(questions))
    return sorted(findings,
                  key=lambda f: (f["item"], f["detector"],
                                 canonical_json(f["evidence"])))


def quality_gate_blocks(questions):
    """True when any detector produced a blocking finding..."""
    return any(f["severity"] == "block" for f in quality_gate(questions))
```
`blueprint_gate(questions, blueprint_doc)` should follow the identical two-function shape: one function returning a deterministically sorted findings list, one boolean `_blocks` companion checking `severity == "block"`. Findings must match `quality_finding.schema.json`'s record shape (`detector`, `detector_version`, `severity`, `code`, `item`, `evidence`, `remediation`) per 15B-RESEARCH Pattern 2, but `blueprint_gate` is a sibling function, not a fifth member of that schema's closed `detector` enum (research Alternatives Considered, assumption A2).

**Composition into the report envelope** (`schemas/audit_report.schema.json:242-261`, quoted in research):
```json
"gates": {
  "type": "object",
  "additionalProperties": false,
  "required": ["lint_errors", "lint_warnings", "quality_findings"],
  "properties": {
    "lint_errors": { "type": "array", "items": { "$ref": "#/$defs/record" } },
    "lint_warnings": { "type": "array", "items": { "$ref": "#/$defs/record" } },
    "quality_findings": { "type": "array", "items": { "$ref": "#/$defs/quality_finding_ref" } }
  }
}
```
Add `blueprint_findings` here as one more optional array property (additive; `required` unchanged), mirroring `build_proposal`'s own `gates` construction in `authoring.py:639-643`:
```python
"gates": {
    "lint_errors": [e._asdict() for e in lint_errors],
    "lint_warnings": [w._asdict() for w in lint_warnings],
    "quality_findings": quality_findings,
},
```

**Where it is wired in:** `authoring.run_authoring` (`authoring.py:659` onward) is the orchestration point; `blueprint_gate` becomes one more gate call in that pipeline, called after `quality_gate` and before the writer handoff, per the research's five-gate diagram.

---

### `graph.accept_migration` / `graph.reject_migration` (service, state transition)

**Analog for the compare-and-swap acceptance mechanics:** `audit_writer.write_units` (lines 288-511) and `undo` (lines 485+), the shipped mutation seam.

**Refusal-on-mismatch pattern to copy** (`audit_writer.py:304-322`):
```python
def write_units(proposal, target_path, state_dir, expected_fingerprint=None,
                create_if_missing=False):
    if not isinstance(proposal, dict) or not proposal.get("bank_after_text"):
        raise WriterError("writer.proposal_invalid",
                          "writer requires an immutable preflighted proposal")
    write_id = deterministic_write_id(proposal)
    with _bank_lock(state_dir):
        exists = os.path.exists(target_path)
        if not exists and not create_if_missing:
            raise WriterError("writer.target_missing",
                              "target bank %s does not exist" % target_path)
        before_raw = _read_bytes(target_path) if exists else b""
        before_fp = bank_fingerprint(
            before_raw.decode("utf-8")) if exists else ""
        if expected_fingerprint is not None and before_fp != expected_fingerprint:
            raise WriterError(
                "writer.stale_preflight",
                "current bank fingerprint %s does not match the preflighted "
                "%s; the bank changed since the proposal was built"
                % (before_fp, expected_fingerprint))
```
`graph.accept_migration(doc, migration_id, actor, rationale)` should mirror this shape: a typed exception (like `WriterError`) carrying a machine-readable `code`, an expected-state or expected-fingerprint recheck before any mutation, and a refusal rather than a silent overwrite on mismatch. `WriterError`'s own shape (`audit_writer.py:200-206`):
```python
class WriterError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
```

**Object and vocabulary being extended (plan text, not shipped):** `graph.migration_proposal`, `MIGRATION_KINDS`, `MIGRATION_STATES = ("proposed", "accepted", "rejected")`, and the `migration_state_not_settable` refusal code are all `[VERIFIED: 14B-04-PLAN.md:91-100, 280-286]`. The explicit hand-off text this phase closes (`14B-04-PLAN.md:560-561`, quoted verbatim):
```text
- No acceptance path. A reviewer accepting or rejecting a migration proposal is
  Phase 15B's "accepted revision" work. Phase 14B records proposals only.
```
`graph.accept_migration`/`reject_migration` are the only legitimate code paths permitted to set `state="accepted"`/`"rejected"`; the existing `migration_state_not_settable` refusal must continue to fire for every other path (research State of the Art table, last row).

**Live re-check requirement (not carried-forward state):** per 15B-RESEARCH Pitfall 3, both functions must call `director.autonomy_level(settings)` fresh at accept time (plan text, `15A-04-PLAN.md`), never read an `autonomy` field off the proposal record itself.

---

### Course-audit report function (service, read-only aggregation)

**Analog:** `auditor.py`'s `coverage_report` (lines 370-421) for the aggregation-into-one-report shape; `schemas/audit_report.schema.json` for the envelope this new report should follow (research Open Question 1 recommends a new sibling schema, `schemas/course_audit_report.schema.json`, rather than extending the existing one, because of its `additionalProperties: false` `$defs.coverage_row` binding to `auditor.py`'s syllabus/bank pairing specifically).

**Pattern to copy:** the pure-transform, three-signal-composition shape of `coverage_report` (`auditor.py:370-421`, quoted above under `blueprint.py`), applied to three read-only inputs instead of one:
1. `director.untreated_objectives` / `director.classify_coverage` (plan text, `15A-01-PLAN.md:128-176`, `15A-03`-cited in research)
2. `authoring.quality_gate` findings (shipped, `authoring.py:539-552`)
3. blueprint compliance (this phase's own `blueprint_gate` findings)

**Do not conflate the three coverage-state vocabularies** (research Pitfall 2): `graph.BINDING_STATES` (plan text, five states), `auditor.coverage_report`'s own five states plus `audit_report.schema.json`'s sixth `"stale"` state, and no fourth. Each cited row in the course-audit report must record which vocabulary its `state` field came from.

---

### `tests/acceptance_tracer.py` (test)

**Analog:** `tests/audit_authoring_roundtrip.py`, `tests/audit_quality_roundtrip.py`, `tests/audit_coverage_roundtrip.py` for the shipped `fail(msg)` + direct-execution convention this project uses everywhere (confirmed no pytest/unittest dependency, per `.claude/CLAUDE.md` and this session's `ls tests/*.py`, which lists 28+ files following this pattern, e.g. `tests/agent_roundtrip.py`, `tests/guard_roundtrip.py`, `tests/evidence_roundtrip.py`).

**Structure to follow** (research, quoting the Wave 0 Gaps section verbatim):
> following `tests/four_subject_review.py`'s (15A) and `tests/three_domain_tracer.py`'s (14B) structure (`fail(msg)`, named `scenario_*()` functions, `main()`, a final `"TRACER: N passed, M skipped, 0 failed"` line)

Note: `tests/four_subject_review.py` and `tests/three_domain_tracer.py` do not exist on disk yet (confirmed via `ls tests/*.py`, neither name appears); this convention is cited from 15A/14B research and plan text, not read from an executed file. Until those land, the closest shipped, readable convention for this project's `fail(msg)`-style direct-execution tests is the `tests/audit_*_roundtrip.py` family, which this project's CLAUDE.md documents as the `*_roundtrip.py`/`*_tracer.py` naming pattern.

**Three scenario groups this one file must cover** (per research's Phase Requirements -> Test Map): ACTIVITY-02 (five-gate draft-to-fidelity-claim pipeline), RELIABILITY-03 (fault-style: edit a synthetic source mid-flow, assert staleness blocks acceptance), AGENT-03 (sparse evidence set of two attempts on one objective, assert no `mastery`/`percent`/`score` key appears, following 15A-02's `check_recommendation_edges` recursive-walk pattern, plan text).

---

### `fixtures/corpus_14b.py` extension (utility, fixture builder)

**No shipped analog on disk.** `fixtures/corpus_14b.py` itself is `MISSING`, confirmed by this session's `ls` and by the research's Critical Caveat filesystem check. It is planned by 14B and extended by 15A per the research's Recommended Project Structure. The closest available convention is the inline, fixed-content synthetic fixture construction already used directly inside `tests/audit_*_roundtrip.py` (synthetic bank text and question dicts built as literal Python data in the test file itself, since no standalone fixtures package exists yet in shipped code). When 14A/14B/15A land, `blueprint.py`'s plan should read `fixtures/corpus_14b.py`'s actual fixture-builder function signatures rather than this inline convention.

**Guard requirement:** every new fixture must pass `python itembank.py guard .` (fictional-content-only enforcement), per research's Security Domain table, "Real course, learner, or bank content entering the repository through a new fixture."

## Shared Patterns

### Closed-vocabulary constants, never a free-text field
**Source:** `authoring.py:65-70` (`DETECTOR_VERSIONS`), `audit_writer.py`'s `WriterError.code` convention, `model.py:2176` (`LINT_CODES`)
**Apply to:** `blueprint.py`'s `STALENESS_DISPOSITIONS`, every refusal code `graph.accept_migration`/`reject_migration` raises, and any new state enum this phase mints.
```python
DETECTOR_VERSIONS = {
    "answer_skew": 1,
    "near_duplicate_stems": 1,
    "answer_leak": 1,
    "distractor_rationale": 1,
}
```

### Staleness is a fingerprint comparison, recomputed on read, never a cached boolean
**Source:** `schemas/audit_report.schema.json:86-89`, quoted verbatim:
```json
"stale": {
  "type": "boolean",
  "description": "True when either input fingerprint no longer matches the
  cited source/bank; a stale report is never treated as current (D-04)."
}
```
**Apply to:** `blueprint.classify_staleness(base_fingerprint, current_fingerprint)`, the course-audit report's own `stale` field, and every acceptance path this phase's functions gate (`graph.accept_migration`, `course.write_course`, the blueprint-gated acceptance path itself).

### Typed exception with machine-readable code, no silent overwrite
**Source:** `audit_writer.py:200-206` (`WriterError`) and its use throughout `write_units` (`writer.proposal_invalid`, `writer.target_missing`, `writer.stale_preflight`)
**Apply to:** `graph.accept_migration`/`reject_migration` (a `migration_state_not_settable`-style refusal on any bypass attempt) and `blueprint_gate` (a refusal code per failed construct/weight/demand/format/difficulty/timing/tools/feedback-condition check).

### Report envelope: `schema_version`, `status`/`kind`, cited fingerprints, no aggregate score
**Source:** `auditor.py:412-421` (`coverage_report`'s return dict) and `schemas/audit_report.schema.json`'s top-level shape
**Apply to:** the course-audit report function's return value and any new report `blueprint.py` produces; never collapse multiple findings into one opaque percentage (AGENT-03, D-10).

### Atomic write convention (UTF-8, pretty JSON, trailing newline, tmp-then-replace)
**Source:** `audit_writer.py:246-253` (`_write_json`), itself citing `runtime.py:178-185`
```python
def _write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)
```
**Apply to:** any durable write this phase's functions perform through `course.write_course`/`journal.commit_operation` (plan text, 14A/14B), which is expected to follow this identical convention.

## No Analog Found

None of the seven files/functions lack a usable analog outright; two (`graph.accept_migration`/`reject_migration`'s exact target object, and `fixtures/corpus_14b.py`'s exact fixture-builder signatures) can only be matched against plan text because the modules they extend (`graph.py`, `fixtures/corpus_14b.py`) are not yet on disk, confirmed `MISSING` by this session's `ls`. The planner should treat those two rows' excerpts as provisional until `14A-FREEZE.md`/`14B-FREEZE.md` land and the real module signatures can be re-read.

## Metadata

**Analog search scope:** repository root (`*.py`), `schemas/*.json`, `tests/*.py`; plan text under `.planning/phases/14A-identity-lifecycle-operation/`, `.planning/phases/14B-graph-course-package-prototype/`, `.planning/phases/15A-director-treatment-policy/` (cited from 15B-RESEARCH.md, not independently re-read in full this session).
**Files scanned:** `authoring.py`, `audit_writer.py`, `auditor.py`, `model.py` (grep only), `runtime.py` (grep only), `schemas/quality_finding.schema.json`, `schemas/audit_report.schema.json` (cited via research), directory listing of `tests/*.py` (28+ files) and repo root `*.py`/`schemas/*.json`.
**Pattern extraction date:** 2026-08-15
