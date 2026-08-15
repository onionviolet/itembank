# Phase 15B: Quality, Blueprint & Acceptance - Research

**Researched:** 2026-08-15
**Domain:** Formal-assessment blueprint fidelity, a course-level quality audit,
an accepted-revision mechanism over the operation journal, and staleness or
dependency-impact propagation, built on top of three phases planned but not yet
executed (14A identity/journal, 14B graph/course, 15A director/treatment
policy) and two phases already shipped and executed (Phase 8 model adapter,
Phase 11 closed authoring loop and curriculum auditor).
**Confidence:** MEDIUM. Everything cited from Phase 8 and Phase 11 is
`[VERIFIED: <file>]` against real, executed source code read this session.
Everything cited from 14A, 14B, and 15A is `[VERIFIED: <plan file>]` against
plan text only, because none of those three phases has executed (confirmed
below). Architectural composition recommendations are this research's own
synthesis and are flagged `[ASSUMED]` where they are not already locked by a
prior plan's decisions.

## Critical caveat: Phase 15B's entire dependency chain is unexecuted, and Phase 11 is executed but partially superseded

Confirmed by direct filesystem check this session (`identity.py`, `journal.py`,
`discovery.py`, `graph.py`, `course.py`, `course_package.py`, `director.py`,
`fixtures/corpus_14b.py` all `MISSING` at repository root; no `*-SUMMARY.md` or
`*-FREEZE.md` file exists under `.planning/phases/14A-identity-lifecycle-operation/`,
`.planning/phases/14B-graph-course-package-prototype/`, or
`.planning/phases/15A-director-treatment-policy/`):

- **Phase 14A** (identity, journal, discovery) has not been executed.
- **Phase 14B** (graph, course sidecar, course package) has not been executed.
- **Phase 15A** (director, treatment recommender, rights/egress, operation
  protocol replay) has not been executed.
- **Phase 15B is fourth in a chain of four unexecuted phases**, one deeper than
  15A was when it was researched.

This is expected sequencing, matching the pattern `15A-RESEARCH.md` already
documented and `15A-01-PLAN.md` Task 1 already executed in plan text (a live
`python -c "import identity, journal, ..."` check that halts by name on
divergence, quoted in Code Examples below). Every function signature, constant,
and refusal code cited below as "from 14A", "from 14B", or "from 15A" is
`[VERIFIED: <plan file>:<lines>]`, never `[VERIFIED: <module>.py]`, because
those modules do not exist on disk to read. The first 15B plan must open with
the same precondition-check pattern, checking for `15A-FREEZE.md` in addition
to `14A-FREEZE.md` and `14B-FREEZE.md`.

By contrast, **Phase 11 (closed authoring loop and curriculum auditor) is
executed and shipped**, confirmed by reading `authoring.py`, `audit_writer.py`,
`auditor.py`, `schemas/quality_finding.schema.json`, and
`schemas/audit_report.schema.json` directly this session. Phase 11 already
built machinery this phase must reuse, not rebuild (see Don't Hand-Roll). One
naming collision matters immediately: `REQUIREMENTS.md`'s `AUDIT-01` through
`AUDIT-09` rows still render as unchecked `- [ ]` in the source file despite
Phase 11 being complete `[VERIFIED: ROADMAP.md:100]`; the checkbox state is
stale bookkeeping, not evidence the functionality is missing. Trust the code,
not the checkbox, when reasoning about what Phase 11 shipped.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ACTIVITY-02 | Formal assessment fidelity requires a cited, versioned blueprint (construct, domain weight, demand, format, difficulty, timing, tools, feedback conditions); the UI never claims exam fidelity without it; practice-generated questions stay drafts until parser, lint, review, blueprint, and runtime gates pass. `[VERIFIED: REQUIREMENTS.md:608-618]` | The blueprint object is a new, additive `## Blueprint` section on `course.py`'s course sidecar (14B), validated against a new `schemas/blueprint.schema.json`. The five gates compose from three already-shipped functions (`model.parse_bank`, `model.lint`, `authoring.quality_gate`) plus one genuinely new pure classifier this phase builds (blueprint fidelity) plus the existing scorer (`runtime.score_response`) as a conformance smoke test. No gate is a second scorer. |
| RELIABILITY-03 | External, source, or version changes mark affected bindings and proposals stale and require a rebind, migrate, supersede, or retain review; a stale derivative is rebuilt, never trusted silently; a stale proposal is blocked from acceptance until reconciled. `[VERIFIED: REQUIREMENTS.md:804-812]` | Staleness is computed by comparing a binding's or proposal's stored base fingerprint (14A's `identity.object_fingerprint`, carried forward per R2 in `16-editor-reader-landscape.md`) against the live fingerprint of what it depends on. `migrate` and `supersede` already have owning mechanisms in 14B (`graph.migration_proposal`) and 14A (`journal.OPERATION_TYPES`); `rebind` and `retain` are new dispositions this phase must mint as a closed vocabulary. |
| AGENT-03 | Evidence-based proposals name their observation window, denominator, included and missing signals, uncertainty, and competing explanations; sparse evidence cannot produce a mastery percentage or a confident causal claim; accepted next actions remain recommendations until the learner or deterministic selection policy acts. `[VERIFIED: REQUIREMENTS.md:909-919]` | Composes `evidence.py`'s shipped append-only log (read-only from this phase, never written by it) with the closed-vocabulary discipline `director.py` (15A) already established for recommendation records: a proposal record carries `window`, `denominator`, `missing_signals`, and `uncertainty` fields and never a `float` or a key named `mastery`/`completion`/`readiness`/`progress`/`percent`/`score`, following the exact recursive-walk test pattern `15A-02-PLAN.md` Task 3 already wrote for treatment recommendations. |
</phase_requirements>

## Summary

Phase 15B adds three new capabilities on top of a stack that is mostly already
designed: **blueprint fidelity** (a cited, versioned exam-construct contract
gating whether a practice set may claim exam fidelity), a **course audit**
(the aggregation and citation-discipline layer over TREAT-01/TREAT-02 coverage,
Phase 11's shipped quality findings, and blueprint compliance), an **accepted
revision** mechanism (turning a draft into durable, journaled, reviewed state
through the one compare-and-swap write path), and **staleness/dependency
propagation** (RELIABILITY-03, closing the "acceptance" gap 14B-04 explicitly
left open for 15B by name).

The load-bearing discovery this session is that **Phase 11 already shipped
half of this phase's "quality" surface**. `authoring.py`'s `quality_gate()`
function and its four named detectors (`answer_skew`, `near_duplicate_stems`,
`answer_leak`, `distractor_rationale`), `schemas/quality_finding.schema.json`,
and `schemas/audit_report.schema.json` (which already carries a `stale` field
and a `coverage_row.state` enum including the literal value `"stale"`)
`[VERIFIED: schemas/quality_finding.schema.json:1-148,
schemas/audit_report.schema.json:1-357]` are executed, tested, shipped
machinery for exactly the "second quality gate beyond lint" AUDIT-07 asks for
and exactly the staleness-signaling shape RELIABILITY-03 needs. 15B's job is
composition and one genuinely new layer (blueprint fidelity), not
reimplementation. The single most important pitfall this research identifies
is that **three, not two, coverage-state vocabularies now exist in this
codebase** (`auditor.coverage_report`'s legacy five states, the
`audit_report.schema.json` `coverage_row` six states including `stale`, and
14B's planned `graph.BINDING_STATES` five states for TREAT-02), and 15B must
neither conflate them nor invent a fourth.

**Primary recommendation:** build the blueprint/audit/acceptance layer as one
new root-level peer module, provisionally named `blueprint.py` (a
`checkpoint:decision` candidate, see Open Questions), following the pure
model-tier pattern `graph.py` already established: no file I/O, no evidence
import, closed vocabularies validated at write time. Route every durable write
this phase produces through the two write paths this project already owns for
their respective object kinds, never a third: bank-content acceptance
(practice-generated question sets) continues through `authoring.run_authoring`
plus `audit_writer.write_units`, the shipped Phase 11 mechanism, extended with
one new gate function; course-scoped objects (the blueprint document, the
course audit report, migration acceptance/rejection) go through
`course.write_course`, which itself calls `journal.commit_operation` (14A/14B).
Building a third write path, or routing bank-item acceptance through
`journal.py`, is the anti-pattern this research names explicitly below.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Blueprint document (the cited, versioned contract) | Course tier (`course.py`'s sidecar, planned 14B) | Model tier (`blueprint.py`, pure validation) | The blueprint is a durable course-scoped object with the same lifecycle as a binding or a migration proposal; its shape validation is a pure function, following `graph.py`'s split between pure classification and `course.py`'s I/O orchestration. |
| Five-gate acceptance pipeline (parser, lint, review, blueprint, runtime) | Model tier (`model.parse_bank`, `model.lint`, shipped) + Agent-client tier (`authoring.quality_gate`, shipped) | New model-tier function (`blueprint.py`'s blueprint-fidelity classifier) + Runtime tier (`runtime.score_response`, shipped, reused as conformance smoke test) | No gate is a new scorer or a new parser. Three of five gates are shipped and reused unmodified; one is new and pure; one is the existing scorer used as a conformance check, not extended. |
| Course audit (TREAT-01/TREAT-02 aggregation, quality findings, blueprint compliance) | Agent-client tier (`blueprint.py`, reads `director.untreated_objectives` and `director.classify_coverage`, both 15A) | Reviewer (accepts or rejects the audit's findings) | An audit is a read-only aggregation over three already-computed sources (treatment state, coverage state, quality findings); it must not recompute or duplicate any of the three, following the same "read bindings, never proposals" discipline `director.untreated_objectives` already established in 15A-02. |
| Accepted revision (draft becomes durable) | Runtime tier (`journal.commit_operation`, 14A) for course objects; Agent-client tier (`audit_writer.write_units`, shipped Phase 11) for bank content | Reviewer (the actual accept/reject decision, gated by `director.authorize_write`, 15A-04) | Two natural write paths for two natural object kinds, both already built. 15B adds no third. |
| Staleness detection (RELIABILITY-03) | Model tier (`blueprint.py`, a pure fingerprint-comparison classifier) | Course tier (`course.py`, reads the live registry to compare) | Staleness is computable from two fingerprints and needs no I/O of its own once both fingerprints are supplied, mirroring `graph.objective_evidence_state`'s (14B-04) pattern of taking a precomputed value as an argument rather than reading the store itself. |
| Migration acceptance/rejection (closing the gap 14B-04 named) | Course tier (`graph.py`, extended) | Runtime tier (`journal.commit_operation` through `course.record_migration`) | 14B-04 built `graph.migration_proposal` and explicitly refused to build the accept path, naming Phase 15B as the owner `[VERIFIED: 14B-04-PLAN.md:560-561]`. This phase adds `graph.accept_migration`/`graph.reject_migration`, not a parallel mechanism. |
| Evidence-based proposal discipline (AGENT-03) | Agent-client tier (`blueprint.py` or a sibling function reading `evidence.py` read-only) | N/A | `evidence.py` is read, never written, by any function this phase adds; the closed-field discipline (`window`, `denominator`, `uncertainty`, no float, no progress-named key) is structural, following 15A-02's precedent for treatment recommendations. |

## Standard Stack

This phase adds no new third-party dependency and no new runtime. It composes
existing, shipped, or already-planned Python-stdlib-only modules.

### Core (already shipped and executed)

| Module | Status | Purpose | Why reused, not rebuilt |
|--------|--------|---------|--------------------------|
| `authoring.py` | Shipped, executed (Phase 11) `[VERIFIED: authoring.py:22,659]` | `run_authoring(request, author_callable, bank_text, writer, config=None)`, the closed draft-lint-retry-accept loop; `quality_gate(questions, profile=None)` and `quality_gate_blocks(questions)` | ACTIVITY-02's "review" and part of its "lint" gate are this loop, already tested against a real writer seam. A `blueprint_gate` is the one new gate function this loop needs. |
| `audit_writer.py` | Shipped, executed (Phase 11) `[VERIFIED: audit_writer.py:200,288,485]` | `write_units(proposal, target_path, state_dir, expected_fingerprint=None, ...)`, `undo(write_id, target_path, state_dir)`, `WriterError` | The one mutation seam `authoring.run_authoring` already calls (`authoring.py` line 22: "`writer` is the one mutation seam"). This is the shipped compare-and-swap write path for bank content specifically, distinct from and older than 14A's `journal.py`, which owns course-scoped objects. |
| `auditor.py` | Shipped, executed (Phase 11) `[VERIFIED: auditor.py:370-489]` | `coverage_report(normalized, questions, bank_fingerprint=None, ...)`, a citation-first syllabus-to-bank coverage classifier with its own five-state vocabulary (`covered`, `gap`, `partial`, `conflicting`, `unknown`) | A third input signal to the course audit, kept structurally distinct from TREAT-02's `graph.BINDING_STATES` (14B) per 15A-RESEARCH's Pitfall 1, which this research extends into a three-vocabulary warning below. |
| `schemas/quality_finding.schema.json` | Shipped `[VERIFIED: schemas/quality_finding.schema.json:1-148]` | The exact machine-readable record shape for `answer_skew`, `near_duplicate_stems`, `answer_leak`, `distractor_rationale` findings, each carrying `severity` (`block`/`warn`), versioned `evidence`, and a `remediation` string | This is AUDIT-07's "second quality gate beyond lint" already built, tested, and schema-validated. 15B's blueprint-fidelity gate should follow this exact record shape (`detector`, `detector_version`, `severity`, `code`, `item`, `evidence`, `remediation`) for its own findings rather than inventing a second finding shape. |
| `schemas/audit_report.schema.json` | Shipped `[VERIFIED: schemas/audit_report.schema.json:1-357]` | The strict report contract for an authoring run or a coverage audit; already carries a top-level `stale: boolean` field (`[VERIFIED: schemas/audit_report.schema.json:86-89]`, quoted: `"True when either input fingerprint no longer matches the cited source/bank; a stale report is never treated as current (D-04)"`) and a `coverage_row.state` enum that already includes the literal value `"stale"` (`[VERIFIED: schemas/audit_report.schema.json:334-337]`) | Direct prior art for RELIABILITY-03's staleness signal, already proven and shipped for the auditor's own coverage domain. 15B's course-audit report should follow the same "carry a `stale` boolean plus a fingerprint pair, recompute don't cache" pattern rather than inventing a second staleness representation, while keeping its own report schema and `BINDING_STATES`-scoped vocabulary structurally distinct from `auditor.py`'s. |
| `model.py` | Shipped, executed | `parse_bank`, `lint` (already includes `bank.answer_position_skew`, `item.duplicate_stem`, `item.distractor_no_would_be` in `LINT_CODES` `[VERIFIED: model.py:2178-2213]`, confirmed live via `python -c "import model; print([c for c in model.LINT_CODES if ...])"` this session, printing `['bank.answer_position_skew', 'item.distractor_missing', 'item.distractor_no_would_be', 'item.duplicate_stem', 'item.missing_distractor_notes']`) | The "parser" and "lint" gates, unmodified. Some content that AUDIT-07's prose implies would be a "second gate beyond lint" is in fact already inside `lint()` itself; see Common Pitfalls. |
| `runtime.py` | Shipped, executed | `score_response`, `canonical_response` | The "runtime" gate: a drafted item must score correctly through the one scorer before it stops being a draft. This is a conformance smoke test that calls the existing scorer; it is not a new scoring path. |
| `evidence.py` | Shipped, executed | Append-only evidence log, `KNOWN_EVENT_TYPES` | AGENT-03's read-only input. No function this phase adds may import `evidence` for writing; only for reading aggregate counts, following the exact "structurally cannot transfer evidence" ban `course.py` and `graph.py` already carry (`[VERIFIED: 14B-04-PLAN.md:22]`). |

### Core (planned, not yet executed - 14A/14B/15A)

| Module | Status | Purpose | Why reused, not rebuilt |
|--------|--------|---------|--------------------------|
| `journal.py` | Planned `[VERIFIED: 14A-02-PLAN.md:104-141]` | `commit_operation`, `entries`, `undo`, `RECORD_TYPES` (additive), `OPERATION_TYPES` (six, frozen) | The one operation journal for course-scoped durable objects. 15B adds no second journal; any new record type it needs is one additive `RECORD_TYPES` member, following the `reconcile`/`migrate` precedent already set twice. |
| `graph.py` | Planned `[VERIFIED: 14B-02-PLAN.md:107-119, 14B-03-PLAN.md:101-114, 14B-04-PLAN.md:91-100]` | `BINDING_STATES` (five, closed), `MIGRATION_KINDS`, `MIGRATION_STATES = ("proposed", "accepted", "rejected")`, `migration_proposal`, `migration_state_not_settable` refusal code | 14B-04 minted the `MIGRATION_STATES` vocabulary and the proposal shape but structurally refused to implement the transition to `accepted`/`rejected`, naming this phase as the owner. 15B adds `graph.accept_migration`/`graph.reject_migration`, the functions that legitimately perform that transition; it does not touch the vocabulary. |
| `course.py` | Planned `[VERIFIED: 14B-01-PLAN.md:119-127, 14B-03-PLAN.md:116-121, 14B-04-PLAN.md:102-104]` | `read_course`, `write_course`, `bind_treatment`, `record_migration` | The one write path for the course sidecar. The blueprint document, the audit report, and a migration acceptance all become durable only by calling into `course.py`'s functions; 15B never writes the sidecar directly. |
| `identity.py` | Planned `[VERIFIED: 14A-01-PLAN.md:110-147]` | `object_fingerprint`, `rights_state`, `rights_granted` | Staleness is a fingerprint comparison; this phase reads `identity.object_fingerprint` to compute "did the thing this binding depends on change", never re-derives fingerprinting logic. |
| `director.py` | Planned `[VERIFIED: 15A-01-PLAN.md:128-176, 15A-04-PLAN.md:116-156, 15A-05-PLAN.md:110-140]` | `PROTOCOL_STEPS` (thirteen frozen tokens), `record_phase`, `replay_operation`, `AGENT_ENTRY_KEYS`, `authorize_write`, `autonomy_level`, `AUTONOMY_LEVELS`, `untreated_objectives`, `classify_coverage` (per 15A-03) | 15B's blueprint-gated acceptance operations are additional `agent_operation` journal entries recorded through the SAME thirteen-step protocol 15A already built and froze, not a second protocol. The course audit reads `director.untreated_objectives` and the TREAT-02 coverage classifier directly rather than recomputing either. |

### New in this phase

| Component | Purpose | Why it is new |
|-----------|---------|----------------|
| `blueprint.py` (name is this research's proposal, a `checkpoint:decision` candidate) | Pure model-tier module: blueprint schema logic, the blueprint-fidelity classifier, the staleness classifier, `STALENESS_DISPOSITIONS`, `DRAFT_STATES` | No existing module owns "does this drafted question set match the accepted blueprint's construct/weight/demand/format/difficulty/timing/tools/feedback-conditions", and no existing module owns the rebind/migrate/supersede/retain disposition vocabulary RELIABILITY-03 needs. |
| `schemas/blueprint.schema.json` | The cited, versioned blueprint contract: `construct`, `domain_weight`, `demand`, `format`, `difficulty`, `timing`, `tools`, `feedback_conditions`, plus `citations` following the exact `{source_object_id, locator}` shape `schemas/treatment_recommendation.schema.json` (15A) already uses | ACTIVITY-02 names these eight fields verbatim; no existing schema carries this shape. |
| `blueprint_gate` (a new gate function parallel to `authoring.quality_gate`) | The fourth of five ACTIVITY-02 gates, checking a drafted question set against the course's accepted blueprint | Fits into `authoring.run_authoring`'s existing gate-composition shape (`gates.lint_errors`, `gates.lint_warnings`, `gates.quality_findings` in `audit_report.schema.json`'s `proposal.gates` object) as one more named gate, following its own `quality_finding.schema.json`-shaped record. |
| `graph.accept_migration(doc, migration_id, actor, rationale)` / `graph.reject_migration(...)` | Closes the acceptance gap 14B-04 named explicitly for this phase | 14B-04's own out-of-scope section: "No acceptance path. A reviewer accepting or rejecting a migration proposal is Phase 15B's 'accepted revision' work." `[VERIFIED: 14B-04-PLAN.md:560-561]` |
| A course audit report function, composing `director.untreated_objectives`, `director.classify_coverage` (or `graph.BINDING_STATES` rows directly), `authoring.quality_gate` findings, and blueprint compliance into one cited report | AUDIT-03's "every coverage claim cites the evidence it rests on" applied at course scope, which no single existing function currently aggregates | None of the three input functions currently talk to each other; a course audit is the first consumer that reads all three. |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| A new `blueprint.py` peer module | Extending `director.py` directly | Rejected as the default: `director.py`'s scope was explicitly locked in 15A-01 as "the treatment recommender and its rights/egress gate" `[VERIFIED: 15A-RESEARCH.md:251-253]`. Blueprint fidelity, course audit, and migration acceptance are a materially different concern (quality and acceptance, not recommendation), and 14B's own precedent (splitting `graph.py`, pure, from `course.py`, I/O) argues for a new pure-tier module rather than growing one module past its stated scope. This is flagged as a `checkpoint:decision` candidate, not silently adopted. |
| Extending `authoring.quality_gate`'s four detectors to a fifth ("blueprint fidelity") | A wholly separate `blueprint_gate` function | The four existing detectors are versioned as a closed set (`_DETECTOR_VERSIONS` dict-shaped constant at `authoring.py:66-69`, all currently `1`) tied to `quality_finding.schema.json`'s closed `detector` enum (`["answer_skew", "near_duplicate_stems", "answer_leak", "distractor_rationale"]`). Adding a fifth member to that closed enum is possible but conflates two different gates (AUDIT-07's machine-authored-failure-mode detectors versus ACTIVITY-02's blueprint-fidelity check) that ACTIVITY-02's own prose lists as separate pipeline stages ("parser, lint, review, blueprint, and runtime"). Keeping `blueprint_gate` a sibling function, not a fifth `quality_finding` detector, respects that the requirement text itself treats them as distinct gates. |
| Routing bank-item acceptance through `journal.commit_operation` (14A) instead of `audit_writer.write_units` (Phase 11) | Migrating bank-content acceptance onto the new journal | Rejected: `audit_writer.py` is executed, tested, shipped, and is `authoring.run_authoring`'s only mutation seam today. Migrating it onto `journal.py` mid-phase would touch shipped Phase 11 code this phase's `files_modified` has no stated reason to open, and would duplicate compare-and-swap logic that already exists correctly in two independently-proven forms for two different object kinds (bank markdown files versus course sidecar sections). Reconsider only if a future phase needs one unified history view across both kinds. |

## Package Legitimacy Audit

Not applicable. This phase installs no new external package; it is pure
Python-stdlib composition over existing, shipped, and planned in-repo modules,
consistent with the project's stated preference (still a preference, not a
rule, per the 2026-08-09 constraint relaxation) and the fact that no research
question in this phase's scope names a new library.

## Architecture Patterns

### System Architecture Diagram

```text
 Practice-generated question set (draft, from authoring.run_authoring)
   |
   v
 gate 1: model.parse_bank  ---------------------------> [refuse: parse error]
   | (shipped, unmodified)
   v
 gate 2: model.lint  -------------------------------------> [refuse: lint.*]
   | (shipped, unmodified; already includes position-skew,
   |  duplicate-stem, distractor-would-be checks)
   v
 gate 3: authoring.quality_gate  --------------------------> [refuse: quality.*]
   | (shipped, unmodified; answer_skew, near_duplicate_stems,
   |  answer_leak, distractor_rationale, severity block/warn)
   v
 gate 4: blueprint_gate (NEW, blueprint.py)  --------------> [refuse: blueprint.*]
   | reads schemas/blueprint.schema.json-validated course blueprint
   | checks construct/domain_weight/demand/format/difficulty/timing/
   |        tools/feedback_conditions against the drafted set
   v
 gate 5: runtime conformance (runtime.score_response smoke test)  --> [refuse: runtime mismatch]
   | (existing scorer, called not extended)
   v
 all five gates pass --> exam-fidelity claim is now permitted
   |
   v
 director.authorize_write (15A-04)  --> autonomy level check, never self-reported
   |
   | approved
   v
 audit_writer.write_units (bank content)  OR  course.write_course (course-scoped object)
   | (two existing write paths, one per object kind; both journal/manifest-backed)
   v
 accepted revision recorded  --> journal entries updated (agent protocol steps
   |                              "accept" and "report", 15A's PROTOCOL_STEPS)
   v
 staleness watch begins: base fingerprint stored at accept time
   |
   v
 [later] a dependency (source, objective, imported version) changes fingerprint
   |
   v
 blueprint.classify_staleness(base_fp, current_fp)  -->  stale = True
   |
   v
 acceptance of anything still depending on the stale object is BLOCKED
   |
   v
 reviewer disposition: rebind | migrate | supersede | retain  (closed vocabulary, NEW)
   |
   v
 reconciled --> re-run the five gates --> re-accept
```

A reader can trace the primary use case (a practice-generated question set
becomes an accepted, exam-fidelity-claiming form) from the top (a draft exists)
to the bottom (an accepted revision, later marked stale, later reconciled) by
following the arrows: no gate is skipped, no gate is a second scorer, and the
two existing write paths are never bypassed by a third.

### Recommended Project Structure

```text
<repo root>/
├── authoring.py         # existing; gains blueprint_gate wired into run_authoring's gate list
├── audit_writer.py       # existing; UNCHANGED by this phase
├── auditor.py             # existing; UNCHANGED structurally, its vocabulary stays distinct
├── model.py                 # existing; UNCHANGED
├── runtime.py                 # existing; UNCHANGED, called not extended
├── identity.py                 # planned by 14A; consumed for object_fingerprint
├── journal.py                    # planned by 14A; gains at most one RECORD_TYPES member
├── graph.py                       # planned by 14B; gains accept_migration/reject_migration
├── course.py                       # planned by 14B; consumed for write_course/record_migration
├── director.py                      # planned by 15A; consumed for PROTOCOL_STEPS, authorize_write,
│                                       untreated_objectives, classify_coverage
├── blueprint.py                      # NEW (name is this research's proposal, a checkpoint:decision
│                                        candidate) -- blueprint schema logic, blueprint_gate,
│                                        staleness classifier, STALENESS_DISPOSITIONS, DRAFT_STATES,
│                                        the course-audit aggregation function
├── schemas/
│   ├── blueprint.schema.json           # NEW
│   ├── quality_finding.schema.json     # existing; unchanged, referenced as the record shape to follow
│   └── audit_report.schema.json        # existing; unchanged, referenced as the report shape to follow
├── fixtures/
│   └── corpus_14b.py                # planned by 14B, extended by 15A; gains a fifth fixture builder
│                                        for the acceptance tracer (a synthetic blueprint plus a
│                                        drafted question set plus a lesson stand-in)
└── tests/
    └── acceptance_tracer.py         # NEW, following tests/four_subject_review.py's (15A) and
                                        tests/three_domain_tracer.py's (14B) structure
```

### Pattern 1: Precondition check against three unexecuted prior phases

**What:** Before importing a module a dependency phase has only planned (not
executed), the plan's first task runs a live import-and-constant-check and
halts by name on any divergence, extended here to check three freeze records
instead of two.
**When to use:** The 15B plan's first task, exactly as 15A-01's Task 1 did for
14A and 14B.
**Example (from the shipped precedent this phase's precondition task copies,
quoted verbatim):**

```text
# Source: 15A-01-PLAN.md Task 1, itself copying 14B-01-PLAN.md Task 1
1. Check that the dependency modules import. Run
   `python -c "import identity, journal, discovery, graph, course, course_package, director; print('modules present')"`.
   Expected stdout: `modules present`, exit code 0.
2. Check that the frozen constants match what this phase was planned against.
3. Check that every relevant freeze record exists, carrying its own
   `## Frozen at <phase>` heading.
6. If any check fails, STOP. Write nothing else, create no module, and print
   a named HALT line, then exit non-zero.
```
`[VERIFIED: 15A-01-PLAN.md:181-331]`

The 15B plan's equivalent task must check `14A-FREEZE.md`, `14B-FREEZE.md`,
AND `15A-FREEZE.md`, re-asserting `graph.MIGRATION_STATES`,
`graph.migration_state_not_settable`'s continued existence for the
not-yet-accepted case, `director.PROTOCOL_STEPS`, `director.AUTONOMY_LEVELS`,
and `director.AGENT_ENTRY_KEYS`, following the exact citation-and-quote
discipline the prior precondition tasks already established.

### Pattern 2: A closed-vocabulary gate composes into an existing report shape, never a new one

**What:** A new gate (`blueprint_gate`) produces findings shaped exactly like
`schemas/quality_finding.schema.json`'s existing record
(`detector`, `detector_version`, `severity`, `code`, `item`, `evidence`,
`remediation`), and slots into `audit_report.schema.json`'s existing
`proposal.gates` object as one more named array, rather than inventing a
second report envelope.
**When to use:** Any new gate this phase or a future phase adds to the closed
authoring loop.
**Example:**

```json
// Source: schemas/audit_report.schema.json:242-261, quoted verbatim -- the
// exact object this phase's blueprint_gate findings must be added beside,
// as "blueprint_findings", following "quality_findings"'s own shape.
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

Because `additionalProperties` is `false` and `gates` is not itself declared
`x-itembank-version`-bumpable without a schema edit, adding `blueprint_findings`
here is an additive schema change (new optional property, existing `required`
array unchanged), proven by the same byte-identical-fixture discipline every
additive format change in this project already carries (non-negotiable 4).

### Pattern 3: Staleness is a fingerprint comparison, never a cached boolean

**What:** A binding, proposal, or accepted revision that depends on another
object is never marked stale at write time and trusted later; staleness is
recomputed at read/accept time by comparing the dependency's live fingerprint
against the base fingerprint recorded when the dependent was created or last
reconciled.
**When to use:** Every RELIABILITY-03 staleness check this phase adds.
**Example (the existing precedent this phase's staleness classifier follows):**

```text
# Source: schemas/audit_report.schema.json:86-89, quoted verbatim
"stale": {
  "type": "boolean",
  "description": "True when either input fingerprint no longer matches the
  cited source/bank; a stale report is never treated as current (D-04)."
}
```

15B's `blueprint.classify_staleness(base_fingerprint, current_fingerprint)`
follows the identical logic this D-04 field already encodes: a boolean derived
from two fingerprints, recomputed on read, never stored as the sole truth.

### Anti-Patterns to Avoid

- **A third write path.** Any code in this phase that writes a bank file
  without going through `audit_writer.write_units` (via `authoring.run_authoring`),
  or writes a course-scoped object without going through `course.write_course`
  (which itself calls `journal.commit_operation`), duplicates compare-and-swap
  logic this project already has correctly, twice, for its two real object
  kinds.
- **A fourth coverage-state vocabulary.** Three already exist:
  `auditor.coverage_report`'s legacy five states (`covered`, `gap`, `partial`,
  `conflicting`, `unknown`), `audit_report.schema.json`'s six-state
  `coverage_row.state` enum (the same five plus `stale`), and 14B's planned
  `graph.BINDING_STATES` (`covered`, `thin`, `missing`, `conflicting`,
  `unknown`). A course audit report may READ from any of the three as an input
  signal but must not mint a fourth; it should cite which vocabulary each cited
  claim came from.
- **Reimplementing Phase 11's quality detectors.** `answer_skew`,
  `near_duplicate_stems`, `answer_leak`, and `distractor_rationale` are shipped,
  tested, and versioned (`detector_version`). A blueprint-fidelity check that
  re-derives, say, its own near-duplicate-stem logic instead of calling
  `authoring.detect_near_duplicate_stems` (or reading its findings) duplicates
  working code and risks the two detectors silently disagreeing.
- **Letting a model self-certify blueprint fidelity or accept its own
  migration.** AGENT-02's ban on self-certification (already built structurally
  into `director.authorize_write`, 15A-04) extends here: the blueprint gate is
  a deterministic classifier, and `graph.accept_migration` must be callable only
  by a reviewer actor, never by the same operation that drafted the proposal.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| The "second quality gate beyond lint" (AUDIT-07) | A new detector set or a new severity model | `authoring.quality_gate` and its four named detectors, `schemas/quality_finding.schema.json` | Shipped, executed, tested, and already wired into `authoring.run_authoring`'s gate composition. |
| A staleness signal | A new stale/fresh boolean scheme invented from scratch | `identity.object_fingerprint` comparison, following the exact pattern `audit_report.schema.json`'s `stale` field and `coverage_row.state`'s `"stale"` value already encode | Prior art exists in this exact codebase for exactly this problem, already schema-validated. |
| Bank-content compare-and-swap writes | A new write path for practice-generated question sets | `audit_writer.write_units` via `authoring.run_authoring` | Shipped, executed, the one mutation seam `authoring.py` already documents itself as owning. |
| Course-scoped object compare-and-swap writes | A second course-object write path | `course.write_course`, which calls `journal.commit_operation` | The one write path 14A/14B already built for exactly this object kind. |
| Migration proposal shape and vocabulary | A new migration/acceptance vocabulary | `graph.MIGRATION_KINDS`, `graph.MIGRATION_STATES` (14B-04), extended with `graph.accept_migration`/`graph.reject_migration` | 14B-04 built the proposal half and named this phase as the owner of the accept half; inventing a parallel migration concept would produce two ways to revise an objective. |
| The operation protocol replay/resume/reverse machinery | A second protocol for "acceptance operations" | `director.PROTOCOL_STEPS`, `director.record_phase`, `director.replay_operation` (15A-05) | AGENT-01 requires ONE operation protocol across every client and every operation kind; a blueprint-gated acceptance is one more `agent_operation` journal entry through the same thirteen steps, not a new state machine. |
| Autonomy-level enforcement | A new self-reported or per-phase autonomy flag | `director.authorize_write`, `director.autonomy_level`, `settings.agent_policy` (15A-04) | AGENT-02 forbids self-expanded scope; the policy-side check 15A already built is the one enforcement point, and this phase's accept operations must reach it, not bypass it. |

**Key insight:** every problem this phase touches already has a designed
(if unexecuted, in the case of 14A/14B/15A) or shipped (in the case of Phase
11) owner. The actual net-new surface area of 15B is narrow: one blueprint
schema, one new pure-tier module holding the blueprint classifier and the
staleness/disposition vocabulary, one new gate function, two new `graph.py`
functions closing 14B-04's deliberately-left-open acceptance gap, and one
course-audit aggregation function. Everything else is composition over three
already-designed write paths and one already-built protocol.

## Runtime State Inventory

Not applicable. This is a greenfield capability-addition phase, not a rename,
refactor, or migration of existing state. No file, database, service
configuration, OS registration, secret, or build artifact carries a name this
phase changes.

## Common Pitfalls

### Pitfall 1: Believing AUDIT-07's "second quality gate" is separate from `lint()`

**What goes wrong:** `REQUIREMENTS.md`'s AUDIT-07 prose reads "a second quality
gate beyond `lint`", which a planner might read as meaning `lint()` contains
none of the machine-authored-failure-mode checks and a wholly separate module
owns all of them.
**Why it happens:** The two are complementary but the boundary is not obvious
from prose alone.
**How to avoid:** Confirmed live this session via
`python -c "import model; print([c for c in model.LINT_CODES if 'stem' in c or 'skew' in c or 'distractor' in c])"`,
printing `['bank.answer_position_skew', 'item.distractor_missing',
'item.distractor_no_would_be', 'item.duplicate_stem',
'item.missing_distractor_notes']`. Some of AUDIT-07's named failure modes
(answer-position skew, a distractor missing its "would be correct" condition,
a duplicate stem) are already `lint()` codes `[VERIFIED: model.py:2178-2213]`,
while the four `quality_finding.schema.json` detectors (`answer_skew`,
`near_duplicate_stems`, `answer_leak`, `distractor_rationale`) live in
`authoring.py` as a genuinely separate, more heavily evidenced pass (Jaccard
scores, per-letter counts, contiguous-token-run leak detection) that `lint()`
does not perform. Both exist; they are not the same check restated twice, but
they do overlap in stated failure mode (duplicate stems, position skew) with
different rigor. 15B's ACTIVITY-02 "lint" gate is `model.lint()`; its "review"
gate (or a named sibling of it) is `authoring.quality_gate()`. Do not treat
either as redundant with the other, and do not build a third pass that
re-covers the same failure modes at a third rigor level.
**Warning signs:** A new detector in `blueprint.py` whose stated purpose is
"duplicate stems" or "answer position skew" rather than blueprint construct/
weight/demand/format/difficulty/timing/tools/feedback-condition compliance.

### Pitfall 2: Conflating three coverage-state vocabularies into a fourth

**What goes wrong:** A course audit report needs a coverage signal, finds
`auditor.coverage_report` first (it is the one that actually runs today,
shipped and executed), and either renames its five states to look like TREAT-02's
five states, or invents a sixth "unified" vocabulary that tries to reconcile
all three.
**Why it happens:** All three vocabularies classify "does a source cover an
objective/syllabus item", and their state names overlap in spirit
(`covered`/`gap`/`partial` vs `covered`/`thin`/`missing`) without being
identical.
**How to avoid:** Keep the three vocabularies structurally distinct, following
15A-RESEARCH's Pitfall 1 discipline extended one level further: `graph.BINDING_STATES`
(`covered`, `thin`, `missing`, `conflicting`, `unknown`) is TREAT-02's, scoped
to an objective-to-source binding inside a course graph. `auditor.coverage_report`'s
states (`covered`, `gap`, `partial`, `conflicting`, `unknown`, plus `audit_report.schema.json`'s
sixth `stale`) are Phase 11's, scoped to a syllabus-objective-to-bank-item
pairing. A course audit report this phase produces cites which vocabulary each
row's state came from; it does not merge them.
**Warning signs:** A course-audit record whose `state` field could plausibly
have come from either `graph.BINDING_STATES` or `auditor.coverage_report`
without the record itself saying which.

### Pitfall 3: Accepting a migration or a blueprint-gated draft without a live rights/autonomy re-check

**What goes wrong:** `graph.accept_migration` or the blueprint-gated
acceptance path is implemented to trust a proposal's own recorded state (for
example, "this was drafted at `recommend-only` so it must still be
`recommend-only`") instead of re-checking the CURRENT autonomy policy and
rights registry at the moment of acceptance.
**Why it happens:** The natural implementation shape for "draft, then later
accept" is to carry forward whatever the drafting step observed, exactly the
failure 15A-RESEARCH's Pitfall 2 already named for treatment recommendations.
**How to avoid:** Every acceptance function this phase adds re-reads
`director.autonomy_level(settings)` and, where the acceptance touches a
source-bound object, `identity.rights_granted` against the live registry,
never a value carried on the proposal record, following the exact "no stale
snapshot ever authorizes" discipline `14B-03-PLAN.md`'s Pitfall 5 already
established and `15A-04-PLAN.md` already extended to egress spans.
**Warning signs:** `graph.accept_migration` or `blueprint_gate`'s acceptance
path reading a field named `autonomy` or `rights` off the proposal dict rather
than calling `director.autonomy_level` or `identity.rights_granted` fresh.

### Pitfall 4: A stale dependent silently rebuilding instead of blocking acceptance

**What goes wrong:** RELIABILITY-03's Degraded clause is explicit: "a stale
proposal is shown as stale and blocked from acceptance until reconciled"
`[VERIFIED: REQUIREMENTS.md:808-809]`. A tempting shortcut is to have the
acceptance path silently re-run the drafting step against the new dependency
and accept the refreshed result, which looks helpful but removes the
reviewer's chance to see that anything changed.
**Why it happens:** "Just rebuild it" is the path of least resistance once a
staleness check already exists.
**How to avoid:** `blueprint.classify_staleness` returning `True` must be a
hard block on `graph.accept_migration`, `course.write_course` (for the object
in question), and the blueprint-gated acceptance path, refused with a named
code before any write, until an explicit reviewed disposition
(`rebind`/`migrate`/`supersede`/`retain`) is recorded.
**Warning signs:** Any acceptance function that reads a staleness flag, finds
it `True`, and proceeds to write anyway "because the content still passed the
gates".

## Code Examples

### The five-gate composition point this phase extends

```python
# Source: authoring.py:539-549, quoted verbatim -- the exact function whose
# gate list this phase's blueprint_gate joins.
def quality_gate(questions, profile=None):
    findings = (
        detect_answer_skew(questions) +
        detect_near_duplicate_stems(questions) +
        detect_answer_leak(questions) +
        detect_distractor_rationale(questions))
    return findings
```

### The shipped quality-finding record shape this phase's blueprint findings must match

```json
// Source: schemas/quality_finding.schema.json:9-18, quoted verbatim
"required": [
  "schema_version", "detector", "detector_version", "severity",
  "code", "item", "evidence", "remediation"
]
```

### The shipped staleness field this phase's staleness classifier follows

```json
// Source: schemas/audit_report.schema.json:86-89, quoted verbatim
"stale": {
  "type": "boolean",
  "description": "True when either input fingerprint no longer matches the
  cited source/bank; a stale report is never treated as current (D-04)."
}
```

### The migration-acceptance gap this phase closes

```text
# Source: 14B-04-PLAN.md:560-561, quoted verbatim
- No acceptance path. A reviewer accepting or rejecting a migration proposal is
  Phase 15B's "accepted revision" work. Phase 14B records proposals only.
```

### The accepted-revision model this phase's plan must satisfy (R1-R10)

```text
# Source: research/phase-16/16-editor-reader-landscape.md:302-306, quoted
# (abridged) -- the framing sentence naming 15B as the owner of accepted-
# revision objects, which this phase's plan must trace every accept operation
# back to.
Frame [synthesis]: the branching-drafts, history, and diff experience is a
THIN UI over the already-planned 14A objects (opaque durable IDs with
fingerprints per D-14A-2, compare-and-swap writes, the append-only operation
journal, accepted-revision objects per 15B).
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Superseded `DIRECTOR-03` requirement (a single "AI course director" story covering blueprint fidelity) | Split into `ACTIVITY-02` (blueprint fidelity, owned by 15B) plus `AGENT-01`/`AGENT-02` (protocol/parity, owned by 15A) plus `AGENT-03` (evidence proposals, owned by 15B) | 2026-08-13 family expansion `[VERIFIED: REQUIREMENTS.md:290-293]` | 15B does not own the treatment recommender (15A's) or the operation protocol itself (15A's); it owns quality, blueprint fidelity, acceptance, and staleness on top of both. |
| Flat Phase 15 ("AI Course Director & Quality Pipeline") | Split into 15A (director/treatment policy) and 15B (quality/blueprint/acceptance) | 2026-08-13, `[VERIFIED: ROADMAP.md:128-135]` | 15B's freeze gate is narrower than the old flat-Phase-15 tracer ("generate one missing lesson treatment and one blueprint-aligned practice set, approve them, sit the set" per `SOURCE-TO-COURSE.md`'s superseded Phase 15 tracer); the current 15B freeze gate is specifically "the lesson-plus-practice acceptance tracer" `[VERIFIED: ROADMAP.md:1780]`, which the ROADMAP subphase table names but for which no phase-detail section yet exists (owed by the orchestrator after this research, per the same precedent 15A's roadmap section followed). |
| 14B-04's `graph.migration_state_not_settable` refusal (any code path setting `state="accepted"` in Phase 14B raises) | 15B adds the one legitimate path: `graph.accept_migration`/`graph.reject_migration`, reviewer-gated | 14B-04, `[VERIFIED: 14B-04-PLAN.md:280-286]` | The refusal code itself should remain in place for any OTHER code path attempting the transition; only the two new named functions may perform it, and the plan should assert the refusal still fires for a bypass attempt. |

**Deprecated/outdated:** none. This is new-capability research; no prior 15B
research exists to supersede.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | A new root-level peer module named `blueprint.py` is the right home for blueprint fidelity, the staleness classifier, and the course-audit aggregation, rather than extending `director.py` or `graph.py`. | Standard Stack "New in this phase", Alternatives Considered | If wrong, either `director.py` grows past its 15A-01-locked scope ("the treatment recommender and its rights/egress gate") or `graph.py` gains I/O-adjacent responsibilities it was designed pure to avoid. This is a one-way module-boundary decision (affects every downstream import and every `hasattr` structural-ban test) and should be a `checkpoint:decision` in the plan, not silently adopted. |
| A2 | `blueprint_gate` is a sibling function to `authoring.quality_gate`, not a fifth member of `quality_finding.schema.json`'s closed `detector` enum. | Alternatives Considered | If wrong, the two "second gate" concepts (AUDIT-07's machine-authored-failure-mode detectors and ACTIVITY-02's blueprint-fidelity check) get silently merged into one enum, which would misrepresent ACTIVITY-02's own five-gate prose ("parser, lint, review, blueprint, and runtime") as only four. Low risk of contract breakage either way since both are additive schema changes, but the semantic distinction matters for future readers. |
| A3 | Bank-content acceptance stays on `audit_writer.write_units`/`authoring.run_authoring`, and only course-scoped objects (blueprint document, audit report, migration acceptance) move onto `journal.commit_operation`/`course.write_course`. | Standard Stack "Alternatives Considered", Anti-Patterns | If wrong, and a future audit finds that having two write paths for two object kinds is itself a non-negotiable-2 violation ("exactly one... evidence store" read expansively), a later phase would need to migrate one onto the other, which is a costly but not one-way change (both paths already produce recoverable, journaled/manifest-backed history). |
| A4 | `rebind` and `retain` are new closed-vocabulary dispositions this phase mints (`STALENESS_DISPOSITIONS`), distinct from `migrate` (14B, changes objective identity) and `supersede` (14A `OPERATION_TYPES`, changes object identity via a new object). | Architectural Responsibility Map, Common Pitfalls 4 | If wrong (for example, if `rebind` is actually meant to reuse `journal`'s existing `edit_in_place` operation type rather than being a distinct reviewer disposition), the plan would need one fewer new constant, a low-cost correction, but the fixture text's own four named words ("rebind, migrate, supersede, or retain") strongly support minting exactly these four as the disposition vocabulary, keeping them distinct from the underlying operation each ultimately performs. |

**If this table is empty:** N/A, four assumptions are recorded above. A1 and
A3 touch one-way module-boundary and write-path decisions and should surface
to the user as checkpoints per `PLANNING-DIRECTIVES.md` section 2 rule 1
(format decisions other phases will build against). A2 and A4 are lower-risk
and may be resolved by the planner with the recommendation stated here, named
as an assumption in the plan's decision table.

## Open Questions

1. **Does the course audit report get its own schema file, or extend
   `audit_report.schema.json`?**
   - What we know: `audit_report.schema.json`'s `status` enum already includes
     `"coverage"` for Phase 11's syllabus-coverage audits, and its structure
     (proposal/manifest/coverage branches on `status`) is built to be
     multi-purpose.
   - What's unclear: whether a course-scope audit (spanning TREAT-01/TREAT-02
     state, quality findings, and blueprint compliance, none of which existed
     when this schema was authored) fits inside that same enum as a new
     `status` value, or needs its own `schemas/course_audit_report.schema.json`.
   - Recommendation: default to a new, additively-versioned
     `schemas/course_audit_report.schema.json`, because the existing schema's
     `additionalProperties: false` `$defs.coverage_row` shape is bound to
     `auditor.py`'s syllabus/bank pairing (Pitfall 2) and forcing a
     structurally different pairing (objective/source/blueprint) through the
     same `$defs` would either violate `additionalProperties: false` or
     require loosening it, which is a real strictness regression on shipped
     Phase 11 fixtures. Treat this as a `checkpoint:decision` naming both
     options.

2. **What is the exact closed vocabulary for `DRAFT_STATES` (the artifact
   lifecycle state primitive named in synthesis section 4.1: draft,
   validating, accepted, stale, conflicting, superseded, retired)?**
   - What we know: synthesis section 4.1 names seven candidate states in
     prose as a "shared primitive" `[VERIFIED: research/phase-16/14-synthesis.md:291]`
     (quoted: "Artifact lifecycle state | draft, validating, accepted, stale,
     conflicting, superseded, retired"), but no executed or planned module
     currently defines this as a Python tuple constant.
   - What's unclear: whether all seven apply to every object kind this phase
     touches (a blueprint document, a drafted question set, a migration
     proposal), or whether each object kind needs its own subset, following
     the precedent that `graph.MIGRATION_STATES` is a narrower three-value
     set (`proposed`, `accepted`, `rejected`) rather than the full seven.
   - Recommendation: do not mint one universal `DRAFT_STATES` tuple applied
     uniformly. Instead, each object kind keeps its own narrow, closed state
     set (as `graph.MIGRATION_STATES` already does), and the seven-word prose
     in synthesis 4.1 is a naming vocabulary to draw individual states from,
     not a single enum to instantiate wholesale. Name this explicitly in the
     plan so the executor does not invent a seven-member `DRAFT_STATES` tuple
     that no object kind actually uses in full.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | Everything in this phase | Present (confirmed `python --version` this session reports 3.13.5 on this machine) | 3.13.5 (dev machine); 3.11+ is the project floor per CI | N/A |
| Phase 14A, 14B, 15A landing on disk | Every import this phase's precondition task checks | Not yet; confirmed `MISSING` this session for all named modules | N/A | The precondition task (Pattern 1) halts by name; this phase cannot execute until 14A, 14B, and 15A have landed, matching the dependency chain ROADMAP.md already states. |
| A hosted or local model backend | AGENT-03's evidence-based proposal drafting, if the proposal is model-authored | Not required for the freeze gate | N/A | Following 15A's own precedent, the freeze gate should use fixture/mock data for any model-authored content, not a live backend. |

No missing dependency blocks planning this phase; the blocking dependency is
sequencing (14A/14B/15A must execute first), not tooling.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Direct-execution Python scripts (`tests/*.py`), no pytest/unittest framework dependency, per the project's shipped convention `[VERIFIED: .claude/CLAUDE.md "Test runner" section]` |
| Config file | None; every test file defines its own local `fail(msg)` helper (confirmed convention across every `tests/*_roundtrip.py` and `tests/*_tracer.py` file read this session and in 15A/14B research) |
| Quick run command | `python tests/<new_test_file>.py` for whichever single new test a task adds |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done`, the exact command `14A-04-PLAN.md` and `15A-RESEARCH.md` already establish as this project's full-suite check |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|-------------|
| ACTIVITY-02 | A drafted question set stays a draft until parser, lint, review, blueprint, and runtime gates all pass; the exam-fidelity claim appears only after all five | Tracer scenario | `python tests/acceptance_tracer.py` (new) | Wave 0 gap |
| RELIABILITY-03 | A source edit marks its dependent bindings/proposals stale; acceptance is blocked until a rebind/migrate/supersede/retain disposition is recorded | Tracer scenario, fault-style (edit a synthetic source mid-flow) | `python tests/acceptance_tracer.py` (new) | Wave 0 gap |
| AGENT-03 | A proposal built over a sparse synthetic evidence set (two attempts on one objective) names its window, denominator, and uncertainty and refuses a mastery percentage | Unit + recursive-walk assertion, following 15A-02's `check_recommendation_edges` pattern | `python tests/acceptance_tracer.py` (new) | Wave 0 gap |

### Sampling Rate

- **Per task commit:** the single new/extended test file for that task's scope.
- **Per wave merge:** `for t in tests/*.py; do python "$t" || exit 1; done`.
- **Phase gate:** the lesson-plus-practice acceptance tracer green, plus the
  shipped-suite check (confirms 15B introduced no regression in
  `model.py`/`runtime.py`/`evidence.py`/`authoring.py`/`audit_writer.py`
  byte-compatibility).

### Wave 0 Gaps

- [ ] `tests/acceptance_tracer.py` -- the freeze-gate tracer; covers all three
  requirement rows above in one run, following `tests/four_subject_review.py`'s
  (15A) and `tests/three_domain_tracer.py`'s (14B) structure (`fail(msg)`,
  named `scenario_*()` functions, `main()`, a final `"TRACER: N passed, M
  skipped, 0 failed"` line).
- [ ] A synthetic blueprint document plus a drafted question set plus a lesson
  stand-in, added to `fixtures/corpus_14b.py` (or a 15B-owned extension of it,
  following the file the plan's Task 1 checks).
- [ ] `schemas/blueprint.schema.json` and its `schema_validate.check_schema`
  coupling test, following every prior new-schema plan's precedent.

*(No pre-existing test infrastructure covers this phase's three requirements;
all listed gaps are new.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Single-learner local product; no accounts, no auth surface (`.claude/CLAUDE.md` Users constraint, unchanged by this phase). |
| V3 Session Management | No | No new session concept; `runtime.py`'s session model is untouched. |
| V4 Access Control | Yes | `director.authorize_write`/`director.autonomy_level` (15A-04), re-checked live at every acceptance call this phase adds (Pitfall 3). This is the phase's actual access-control surface: which actor may accept a migration or a blueprint-gated draft. |
| V5 Input Validation | Yes | `schema_validate.py`'s closed-keyword subset validator, already used by every schema in this project; `schemas/blueprint.schema.json` validates the same way. |
| V6 Cryptography | No | No new secret material; nothing in this phase touches `model_adapter.py`'s `secret_env` resolution. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|------------------------|
| A migration or blueprint-gated draft accepted by the same actor/operation that drafted it, bypassing reviewer authority | Elevation of Privilege | `graph.accept_migration`/`graph.reject_migration` and the blueprint-gated acceptance path both re-check `director.authorize_write` live at accept time (Pitfall 3), never trusting a self-reported autonomy field on the proposal. |
| A stale dependent silently accepted or silently rebuilt, hiding a real content change from the reviewer | Tampering / Repudiation | `blueprint.classify_staleness` is a hard block on every acceptance path until an explicit reviewed disposition is recorded (Pitfall 4). |
| A fourth coverage-state vocabulary silently reintroducing an over-generous "covered" classification (the exact pattern TREAT-02 and 14B-03's read-time degradation rule already guard against) | Tampering | The course audit report cites which of the three existing vocabularies each row's state came from and mints no fourth (Pitfall 2). |
| Real course, learner, or bank content entering the repository through a new fixture for the acceptance tracer | Information Disclosure | Every new fixture builder follows the fictional-content-only, fixed-seed convention every prior 14A/14B/15A fixture already established; `python itembank.py guard .` is a required acceptance check on every task that touches `fixtures/`. |
| Supply chain: a diff, scoring-adjacent, or NLP dependency introduced for the blueprint-fidelity classifier | Tampering | None is needed; blueprint-fidelity classification is closed-vocabulary comparison over already-structured data (`treatment_kind`, `domain_weight` maps, `difficulty` tags), not free-text analysis. Per `PLANNING-DIRECTIVES.md` section 4a, any dependency ever added here later is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent. |

## Sources

### Primary (HIGH confidence -- shipped, executed code and requirements read this session)

- `authoring.py` (module docstring, `quality_gate`, `quality_gate_blocks`, the four `detect_*` functions, `run_authoring`) - the shipped closed authoring loop and second quality gate.
- `audit_writer.py` (`WriterError`, `write_units`, `undo`, `_write_bytes_atomic`) - the shipped compare-and-swap write path for bank content.
- `auditor.py` (`coverage_report` and its `_row`/`_coverage_row` helpers, lines 370-489) - the shipped, differently-scoped legacy coverage vocabulary.
- `model.py` (`LINT_CODES`, confirmed live via `python -c`) - the shipped lint gate, already carrying some AUDIT-07-adjacent checks.
- `schemas/quality_finding.schema.json` and `schemas/audit_report.schema.json` (full read) - the shipped second-quality-gate record shape and the shipped, already-staleness-aware report contract.
- `schemas/model_adapter.schema.json` (targeted grep, confirmed the live three-member `operation` enum matches 15A-RESEARCH's citation) - confirms 15A has not yet landed on disk.
- `.planning/REQUIREMENTS.md` (full `ACTIVITY-*`, `RELIABILITY-*`, `AGENT-*` family sections, the traceability table, and the family-alias note) - the three owned requirements verbatim with Fixture sentences.
- `.planning/ROADMAP.md` (Phase 15A detail section, the nine-subphase table, the roadmap governance clauses, the superseded flat-sequence Phase 15 narrative) - phase goals, dependencies, and freeze gate.
- `.planning/PLANNING-DIRECTIVES.md` (full read) - the autonomy rule, build-both rule, five non-negotiables, executor bar.
- `.planning/AGENT-WORKFLOW.md` (full read) - the cross-agent operating contract.
- `.claude/skills/OPERATION-CONTRACT.md` (full read) - the thirteen-step operation protocol, pending-surfaces list.
- `.planning/PLAN-TEMPLATE.md` (full read) - the executor-bar structure every 15B plan must satisfy.
- `.planning/phases/15A-director-treatment-policy/15A-RESEARCH.md` (full read) - the immediately prior sibling phase's research, its critical caveat, pitfalls, and Don't Hand-Roll table.
- `.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md` through `15A-06-PLAN.md` (objective, decisions-locked table, and "Artifacts this phase produces" sections read for each) - the planned `director.py` API surface, protocol steps, autonomy/egress mechanism.
- `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md` (full read) - the planned `journal.py` compare-and-swap write path and fault-injection discipline.
- `.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md` (full read) - the planned migration proposal mechanism and its explicit hand-off of acceptance to Phase 15B.
- `.planning/research/phase-16/14-synthesis.md` (sections 2, 3, 6, 7, 10, 15, 16 read in full) - product model, operation protocol, cross-cutting rules, subphase table, exit gates.
- `.planning/research/phase-16/16-editor-reader-landscape.md` (section 4, R1-R10, full read) - the accepted-revision object model explicitly naming Phase 15B as the owner.
- Live filesystem check this session confirming `identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`, `course_package.py`, `director.py`, and `fixtures/corpus_14b.py` are all `MISSING`, and no `*-SUMMARY.md`/`*-FREEZE.md` exists for 14A, 14B, or 15A.

### Secondary (MEDIUM confidence)

- `.planning/SOURCE-TO-COURSE.md` (full read) - the superseded-but-traceable Phase 15 narrative description, used only to confirm the current ROADMAP/REQUIREMENTS supersede it.
- `.planning/STATE.md` (lines 1-470) - project history and decision-log context.

### Tertiary (LOW confidence)

- None used; no web search was performed, as this phase's research scope is entirely in-repo architecture composition with no new external library or API to verify against an authoritative external source.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH for shipped modules (`authoring.py`, `audit_writer.py`,
  `auditor.py`, `model.py`, `runtime.py`, both quality/audit-report schemas),
  MEDIUM for planned-but-unexecuted modules (`identity.py`, `journal.py`,
  `graph.py`, `course.py`, `director.py`) because their real implementation
  may deviate from plan text during 14A/14B/15A execution.
- Architecture: MEDIUM - the composition pattern (reuse the two existing write
  paths, the one operation protocol, the shipped quality gate) is well-grounded
  in explicit, cited precedent, but the module-boundary decision (A1) and the
  write-path-count decision (A3) are recommendations, not locked facts, and are
  flagged as checkpoint candidates.
- Pitfalls: HIGH - Pitfall 1 (lint-versus-quality-gate boundary) and Pitfall 2
  (three coverage vocabularies) are directly verified against real, executed
  code and schemas read this session with exact line citations; Pitfalls 3 and
  4 are directly grounded in explicit precedent 14B-03/15A-04 already
  established and tested for structurally identical problems.

**Research date:** 2026-08-15
**Valid until:** Re-check immediately if `14A-FREEZE.md`, `14B-FREEZE.md`, or
`15A-FREEZE.md` appears in the repository before 15B is planned or executed
(their real, frozen constants supersede the plan-text citations in this
document per the Critical Caveat above). Otherwise, valid for approximately 14
days (fast-moving: this phase sits directly downstream of three unexecuted
phases whose real implementation may shift plan-text details, and one
executed phase, Phase 11, whose shipped surface this research treats as
stable).
