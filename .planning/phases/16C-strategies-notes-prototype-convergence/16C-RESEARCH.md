# Phase 16C: Strategies, Notes & Prototype Convergence - Research

**Researched:** 2026-08-15
**Domain:** Learner-owned notes and learner artifacts (NOTE-01..03), the finite
strategy registry and the composed mode-layer precedence resolver
(STRATEGY-01..02), the honest progress comprehension display (GRAPH-03), the
legacy-upgrade contract (UPGRADE-01..02), and the note-output trio prototype
(notebook page, Cornell notes, concept map as three validated projections of
one parse). Freeze gate: the cross-subject missing-feature suite over four
synthetic subjects.
**Confidence:** MEDIUM overall. Everything cited from shipped `model.py`,
`runtime.py`, `evidence.py`, `surfaces/lesson.py`, `surfaces/study.py`, and
`surfaces/cli.py` is `[VERIFIED: <file>:<lines>]` against executed source read
this session. Everything cited from 14A, 14B, 16A, or 16B is
`[VERIFIED: <plan or spec file>]` against plan text only, because none of those
phases has executed (confirmed below by direct filesystem check). Composition
recommendations for 16C's own new modules are this research's synthesis and are
flagged `[ASSUMED]`.

## Critical caveat: all three of 16C's declared dependencies (14B, 16A, 16B) are planned but not executed, and so is everything beneath them

Confirmed by direct filesystem check this session:

- Repo root `ls *.py` returns exactly: `audit_writer.py, auditor.py,
  authoring.py, build.py, evidence.py, fake_hosted_unused.py, itembank.py,
  model.py, model_adapter.py, resources.py, retention.py, runner.py,
  runtime.py, schema_validate.py, selection.py, server.py, subjects.py,
  tier_gate.py`. None of `identity.py`, `journal.py`, `discovery.py`,
  `graph.py`, `course.py`, `course_package.py`, `capabilities.py`, or any 16B
  IA module exists. `[VERIFIED: repo root listing, this session]`
- `find .planning/phases -name "*FREEZE*"` returns **nothing**. There is no
  `14A-FREEZE.md`, no `14B-FREEZE.md`, no `16A-FREEZE.md`, no `16B-FREEZE.md`.
  `[VERIFIED: find run, this session]`
- `.planning/phases/13.9-walking-skeleton/` and
  `.planning/phases/14A-identity-lifecycle-operation/` contain no
  `*-SUMMARY.md` and no `*PRECONDITION*` file: the walking skeleton has not
  been walked and 14A has not executed. `[VERIFIED: find run, this session]`
- `.planning/phases/16B-ia-modes-recovery-contract/` contains
  `16B-01-PLAN.md` through `16B-11-PLAN.md`, `16B-PATTERNS.md`,
  `16B-RESEARCH.md`, `16B-UI-SPEC.md`, `16B-VALIDATION.md`, and nothing else.
  `[VERIFIED: directory listing, this session]`

16C therefore sits **three unexecuted phases deep**: it depends on 14B, 16A,
and 16B directly; 16B depends on 14A and 16A; 16A depends on 14B; 14B may not
freeze before 13.9 is walked. `ROADMAP.md`'s Phase 16C entry states the
consequence in its own words: "All three are planned but not yet executed, so
every signature this phase imports is read from plan text at planning time; the
first 16C plan opens with a recorded precondition check that halts by name on
any divergence, the same pattern plans 14B-01, 15A-01, 15B-01, 16A-01, and
16B-01 set, extended to check for `14B-FREEZE.md`, `16A-FREEZE.md`, and
`16B-FREEZE.md` records and for Phase 13.9's A9 closure, because 16C's own
freeze is a 14B-or-later freeze and may not close before the walking skeleton
is walked." `[VERIFIED: ROADMAP.md:2084-2095]`

Every 14A/14B/16A/16B signature cited below carries the halting
precondition-check pattern (16B-RESEARCH Pattern 1) as its guard, and each is
listed in the Assumptions Log with its falsifying condition.

**No CONTEXT.md exists for this phase**, matching the recorded autonomous
precedent for Phases 14A through 16B (`16B-UI-SPEC.md` header: "No CONTEXT.md
exists for this phase, matching the recorded precedent for Phases 14A through
16A"). Scope constraints come from ROADMAP.md, REQUIREMENTS.md,
PLANNING-DIRECTIVES.md, STYLE-DISCIPLINE-16A-2026-08-14.md, and the 16B specs.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| NOTE-01 | Notes are learner-owned artifacts, never annotations baked into accepted lessons, carrying note ID, ownership, course/objective relation, anchor or selector, source/lesson revision, authorship type, strategy, text or structure, privacy, revision, and optional promotion/review state; authored pre-highlighting is orientation, never learner evidence (clause C107). Degraded: a stale anchor keeps the note attached to its objective and flags the broken selector. `[VERIFIED: REQUIREMENTS.md:633-644]` | Report 12 section 9.1 gives the minimum semantic record verbatim (quoted under Pattern 4 below); section 9.3 gives the multi-selector provenance recommendation; section 8.2 gives the relocation states `resolved`, `relocated_exact`, `relocated_probable`, `orphaned` with "Probable relocation needs review" `[VERIFIED: research/phase-16/12-active-annotation-notes.md:232]`. Fixture: the 16C suite's synthetic note set anchored to a synthetic lesson, one anchor invalidated by a lesson revision, asserting the note stays attached to its objective with the broken selector flagged. |
| NOTE-02 | Notes may ground reflection, retrieval proposals, and draft questions but never silently become accepted source, lesson, key, score, or mastery; promotion requires explicit source-backed review; an unreviewed note stays learner-private and non-authoritative. `[VERIFIED: REQUIREMENTS.md:646-654]` | Report 12 section 7.2's eight-point silent-promotion prevention list (epistemic roles, derivation edges, accepted-source support edge for every keyed claim, normal bank lint, conflict stop, unkeyed self-prompts, restrictive scope inheritance, never auto-grade prose). Fixture: one synthetic note promoted through source-backed review while a second unreviewed note is asserted to stay learner-private and non-authoritative. |
| NOTE-03 | A learner artifact (proof, program, diagram, explanation, project, observation) carries a rubric and pending/review state and produces descriptive or pending evidence until reviewed; the runtime records pending and never settles. `[VERIFIED: REQUIREMENTS.md:656-663]` | The shipped `evidence.mark_event` already enforces exactly this authority split: "`marker` must be `\"human\"` in this phase: a model verdict is not a mark" `[VERIFIED: evidence.py:1427-1428, 1445-1447]`, and short answers score `None` pending review (shipped scorer behavior). Fixture: a fictional proof with a rubric reading as pending evidence until a scripted review settles it. |
| STRATEGY-01 | Learning strategies are a finite registered set (continuous reading, guided note spine, worked reasoning, retrieval-first or assessment-first where policy permits) sharing canonical objects; each states purpose, eligibility, required and optional learner actions, skip and resume, evidence effects, accommodations, offline behavior, and tests. Degraded: an unavailable strategy falls back to continuous reading. `[VERIFIED: REQUIREMENTS.md:667-677]` | Report 12 section 10.1 gives the one shared strategy contract and the closed event family; 10.4 gives the combinatorial failure controls including "Kill a mode if it requires a second parser, scorer, note truth, or UI state machine" `[VERIFIED: research/phase-16/12-active-annotation-notes.md:321]`. Fixture: every registered strategy runs against the four synthetic subjects with one strategy marked unavailable, asserting fallback to continuous reading. |
| STRATEGY-02 | Learner preference, author/course strategy, objective constraint, accommodation override, instructor policy, runtime authority, and system safety are ordered precedence layers; a learner chooses only among allowed strategies and runtime assessment behavior is never user-configurable during a sitting. `[VERIFIED: REQUIREMENTS.md:679-689]` | 16B locked the seven-layer table and the exact conflict copy ("{Setting name} is set by {higher layer name} for this course and can't be changed here.") but explicitly deferred the composed resolver to 16C: "Full precedence *resolution* as a runnable function composing every layer's live state is explicitly **out of 16B's scope** and belongs to Phase 16C" `[VERIFIED: 16B-UI-SPEC.md:279-284, Decision D8]`. Fixture: the conflict-matrix fixture (learner preference contradicting an accommodation override and an instructor policy, each yielding to the higher layer with the stated-reason copy, no mid-sitting change), extending 16B's conflict fixture rather than duplicating it. |
| GRAPH-03 | Progress is reported through the independent tuple (claim kind, scope/version, numerator, denominator or indeterminate, rule, snapshot/window, settled/pending/unknown, authority, uncertainty); seven dimensions stay separate; no aggregate completion, mastery, or readiness score anywhere; separate denominators for required, required-choice, and enrichment; a missing denominator reports indeterminate; the learner display uses the D-14A-3 per-objective self-adjustable fill state and Retrievability is never surfaced as a percentage. `[VERIFIED: REQUIREMENTS.md:403-424]` | Report 08 sections 6.1-6.3 give the seven dimensions table, the reconstructible claim contract, and the honest/dishonest bar rules including the ARIA guidance (`aria-valuenow` for determinate ranges, `aria-valuetext` when the number alone is not meaningful) `[VERIFIED: research/phase-16/08-curriculum-hierarchy-progress.md:368-457]`. D-14A-3 resolved the display: "a per-objective, self-adjustable fill state shown as filled-in blocks... able to move up and down as evidence and retention change. It is not a permanent knowledge claim" `[VERIFIED: DECISIONS-PRE-14A-2026-08-14.md:133-137]`. Fixture: synthetic evidence set with a missing denominator, a pending prose mark, and a version-split objective, asserting each tuple dimension reports separately and no aggregate score appears. |
| UPGRADE-01 | Legacy-artifact upgrades begin with the eleven-item baseline audit (current parse, identity, fingerprint, objectives, sources, rights, media, assessment boundaries, plain rendering, rich rendering, validation) and present a bounded diff before editing; stable identity and source history preserved; cosmetic novelty rejected; an artifact that cannot express an enhancement retains its form and links a derived enhancement with its portability cost. `[VERIFIED: REQUIREMENTS.md:923-933]` | Synthesis section 10's legacy-upgrade paragraph and the `legacy-upgrade` skill stub's declared scope. Fixture: a synthetic pre-13.5 lesson artifact, asserting the baseline audit runs first and the enhancement lands as a bounded diff with identity and source history preserved. |
| UPGRADE-02 | Assessment-semantic changes (keyed content, difficulty, objective alignment) are separate reviewed revisions, never silently changed by an upgrade; an upgrade touching keyed meaning halts for explicit assessment review. `[VERIFIED: REQUIREMENTS.md:935-942]` | D-14A-2's keyed-content fingerprint carve-out is the detection mechanism already planned: trailing-whitespace normalization is applied "to every kind except `bank` and `lesson`" precisely because "those are the only two 14A object kinds whose storage bytes can carry keyed assessment content" `[VERIFIED: 14A-01-PLAN.md:86, plan text]`. The shipped `model.content_fingerprint` (model.py:1451) and `_key_content_hash` (model.py:1532) are the shipped-side change detectors. Fixture: a scripted upgrade attempting to touch a synthetic item's keyed answer, halting for explicit assessment review. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

1. **Runtime invariant, unchanged by this phase.** One runtime, one scorer, one
   evidence store; the runtime, not the model, settles scoring, assessment
   disclosure, and evidence. NOTE-03's "runtime records pending and never
   settles" and NOTE-02's promotion gate are direct applications, not
   exceptions. The invariant names one scoring authority, not a frozen
   capability set (IL-20260815-05): advisory graders may propose, never settle.
2. **Five non-negotiables** (PLANNING-DIRECTIVES.md section 4): (1) runtime
   owns assessment authority; (2) exactly one parser, one scorer, one evidence
   store; (3) evidence and banks stay on disk, no telemetry; (4) format changes
   are additive, proven by byte-identical fixtures; (5) the nine accessibility
   gates in UI-SPEC.md section 8. The trio prototype's "parsed once by the one
   parser with zero re-parsing" is non-negotiable 2 applied to notes.
3. **Notes are learner data, not bank content.** The repo-data rule ("No real
   question banks in this repository, enforced by `itembank guard`") extends to
   notes: every note fixture is synthetic, and real learner notes live outside
   the repository beside the private bank, in an approved note root. The
   data-residency clarification (IL-20260815-06) permits learner-initiated
   export/backup of the learner's own copies; it bans telemetry and vendor-held
   data.
4. **Constraint relaxation (2026-08-09).** stdlib-only, no-build-step,
   offline-first are preferences. Nothing researched here needs a dependency
   (see Package Legitimacy Audit).
5. **No em dash characters** anywhere in repository-authored prose, fixtures,
   or generated notes and questions.
6. **Prose style and provenance rules**: keep quotation, interpretation,
   research finding, recommendation, and decision visibly distinct; every
   mutation uses expected fingerprint, bounded diff, atomic write, journal;
   learner notes never silently become source truth, lesson truth, keys,
   scores, or mastery (CLAUDE.md Direction and operation rules, verbatim
   subject of NOTE-02).

## Summary

Phase 16C is the convergence phase: it takes the note and strategy research
(report 12), the honest-progress research (report 08), the 16A semantic
capability contract, and the 16B IA/mode contract, and turns them into five
concrete deliverables plus one proving prototype. The deliverables are (1) the
learner-note and learner-artifact schemas with multi-selector provenance and
relocation states, (2) the promotion and review contract that keeps note error
out of accepted truth, (3) the finite four-strategy registry with declared
contracts and continuous-reading fallback, (4) the composed seven-layer
precedence resolver 16B explicitly deferred here (16B-UI-SPEC D8), and (5) the
progress comprehension display built from the GRAPH-03 claim tuple and the
D-14A-3 fill state. The prototype is the note-output trio: notebook page,
Cornell notes, and concept map produced as three validated projections of one
content instance parsed once, each validator failing meaningfully on a
deliberately broken fixture, each output degrading to coherent plain Markdown.
The trio gates the entire output-mode long tail: the remaining seven modes and
the on-demand genre styles register only after it passes
(STYLE-DISCIPLINE-16A-2026-08-14.md, binding order).

The first discovery is that **16C sits three unexecuted phases deep**, one
deeper than 16B. No FREEZE record of any kind exists on disk. Every import
from 14A (identity, journal), 14B (graph, course), 16A (capabilities, shared
note/activity schemas), and 16B (IA module, settings keys, conflict-copy
constant) is plan text. The consequence is structural: 16C's plans split into
work that needs **no unexecuted module** (schemas, registries, resolvers,
validators, projections, all pure functions over synthetic fixtures, the same
route 16A-02 took with `capabilities.py` and 16B took with its storyboard
fixtures) and thin integration seams that sit behind the 16C-01 precondition
check.

The second discovery is that **the shipped codebase already contains the exact
architectural precedents every 16C deliverable needs**. The trio's parse-once
rule is the shipped independent-preamble-read discipline (`parse_lesson` at
model.py:469 and `parse_terms` at model.py:625 are second and third reads over
one file that never change `parse_bank`'s shape). The strategy registry's
closed-vocabulary shape is the shipped Phase 03.1 style registry
(`STYLE_CHECK_CATALOGUE` at model.py:2250, a closed dict of dotted codes to
severities). The per-mode validator-plus-projection shape is the shipped
style system (`load_style`/`resolve_style` at model.py:1363/1418, with
`RENDER_REFUSAL_COPY` at surfaces/lesson.py:86 as the refusal precedent). The
pending-until-human-review discipline is the shipped `mark_event` human-only
marker gate (evidence.py:1416-1447). The one-evidence-writer discipline is
`append_event` (evidence.py:735), with `live_events` (evidence.py:1355) as the
one read-side filter and unknown-event-type skip-and-warn (evidence.py:765) as
the proven additive path for new event types.

The third discovery is the load-bearing **evidence versus note-state split**.
Report 12's strategy contract emits a closed event family (`target_selected`,
`content_composed`, `relation_added`, `representation_attached`,
`source_checked`, `note_revised`, `activity_completed`, `activity_skipped`)
`[VERIFIED: research/phase-16/12-active-annotation-notes.md:292]`, but report
12 section 11.2 also requires note deletion to cover "the note, its private
index, and queued model inputs, while preserving only explicitly required
assessment evidence." The evidence log is append-only. Those two rules are
compatible only if **note content never enters the evidence store**: lifecycle
facts (an activity completed, an activity skipped) may append to the one
evidence store as new additive event types carrying at most a note ID
reference; content-bearing events (what was selected, what was written, how a
note was revised) stay in the learner-owned note store beside the notes
themselves. This split is the phase's most consequential design decision and
is recorded as Open Question 2 with a firm recommendation.

**Primary recommendation:** structure 16C as pure-module construction over
synthetic fixtures, mirroring 16A/16B. Plan 01 is the halting precondition
check (three freeze records, three precondition dated-result lines, 13.9 A9
closure, live shipped-surface re-verification) plus a 16C-DECISIONS.md that
locks the event-taxonomy split, module boundaries, note-file placement, and
strategy-registry contents before any code plan runs. Middle waves build the
note schema, strategy registry, precedence resolver, progress display, trio
prototype, and upgrade contract as pure modules with direct-execution tests.
The final plan runs the cross-subject missing-feature suite and writes
16C-FREEZE.md with the explicit scope statement ROADMAP.md requires (not a
visual, IA, semantic-capability, or course-schema freeze).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Note record schema, provenance multi-selector, relocation states | Model tier (new pure module, e.g. `notes.py`) | Filesystem (note files in an approved note root, outside the repo) | Follows the `capabilities.py` precedent from 16A plan text: a pure registry/schema module with no file I/O in its core functions; file placement is a separate, settings-governed concern. `[ASSUMED]` module name, a `checkpoint:decision` for 16C-01. |
| Note storage and privacy | Filesystem (approved note root from 16B's `approved_roots` settings key) | Settings (`approved_roots`, plan text) | 16B's settings expansion names `approved_roots` as "the list of source/vault/bank/note-directory roots this install may read" `[VERIFIED: 16B-UI-SPEC.md:410, plan text]`; FILE-01 names "note directories" as a root class `[VERIFIED: REQUIREMENTS.md:438-440]`; the shipped precedent is evidence living beside the private bank in `_evidence/` (`EVIDENCE_DIRNAME = "_evidence"` `[VERIFIED: evidence.py:38]`). |
| Strategy registry and fallback | Model tier (new pure module, e.g. `strategies.py`) | Evidence store (lifecycle events only) | Closed-vocabulary registry following `STYLE_CHECK_CATALOGUE`'s shape; fallback to continuous reading is a pure lookup decision, not I/O. |
| Composed precedence resolver | Model tier (same strategies module) | Settings and course records (each layer's live state, partly plan text) | 16B D8 assigns the resolver here by name; the fixed layers (runtime authority, system safety) are enforced by the shipped runtime already and the resolver must read them as fixed, never compose them as opinions. |
| Progress claim tuple and comprehension display | Model tier (pure claim builder) plus presentation tier (fill-state rendering contract) | Evidence store (read-side via `live_events`/`capture_events`) | GRAPH-03's owner split: "runtime for settled evidence, course records for design coverage" `[VERIFIED: REQUIREMENTS.md:417-418]`. The display contract is documentation plus fixtures in 16C; pixel rendering is 17A. |
| Note-output trio (notebook page, Cornell, concept map) | Presentation tier (three projections) over Model tier (one parse) | Validator functions per mode (model tier) | STYLE-DISCIPLINE's corollary: "a semantic style is a validator plus a projection over the one parsed content model. It never introduces a second parser, second renderer, or second content truth." |
| Legacy-upgrade contract | Skill/authoring tier (`legacy-upgrade` skill, currently a stub) plus Model tier (baseline-audit function, keyed-content change detection) | 14A identity/fingerprint (plan text) | The audit-before-editing rule is CLAUDE.md's own; the halt-on-keyed-change detector composes shipped `content_fingerprint` and `_key_content_hash` with 14A's `object_fingerprint` carve-out (plan text). |
| Learner artifact pending evidence | Evidence store (existing `mark`/`mark_proposal` machinery) | Note store (the artifact file itself, learner-owned) | The runtime records pending and never settles; `mark_event`'s human-only marker is the shipped enforcement `[VERIFIED: evidence.py:1445-1447]`. |

## Standard Stack

### Core

No new third-party library is required. Every 16C deliverable is pure Python
over the shipped stdlib-only modules, matching every prior phase.

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python standard library | 3.11+ | Schemas, registries, resolvers, validators, projections, fixtures, direct-execution tests | Every shipped module and test in this repository is stdlib-only; 16C adds pure modules and fixtures in the same shape. `[VERIFIED: .claude/CLAUDE.md Frameworks/Key Dependencies]` |

### Supporting

None identified. The concept-map projection's textual-adjacency fallback and
the Cornell two-column degradation are plain Markdown output, not a rendering
dependency.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A new pure `notes.py`/`strategies.py` pair | Folding note and strategy logic into `model.py` | Rejected as default: `model.py`'s stated scope is the bank format contract; notes are learner data with their own lifecycle. Follows the 16A `capabilities.py` module-boundary precedent (16A-RESEARCH A2). Final name is a 16C-01 `checkpoint:decision`. |
| Markdown note files with a JSON sidecar for machine metadata | Inline machine metadata in the note Markdown | Report 12 section 9.1: "The readable export should remain coherent Markdown. Machine metadata may use a sidecar if inline syntax becomes intrusive. Either form needs one canonical parser for this contract." Recommendation below picks sidecar-per-note-document; see Open Question 1. |
| Extending `KNOWN_EVENT_TYPES` additively for strategy lifecycle events | A second event log for note/strategy events | A second log would be a second evidence store, violating non-negotiable 2. The shipped skip-and-warn degrade path (`events()` skips unknown `event_type` with a warning `[VERIFIED: evidence.py:765-768]`) is the proven additive route already used for `selection`, `visual_action`, and `gate_skip`. |

**Installation:** none required.

**Version verification:** not applicable, no external package is recommended.

## Package Legitimacy Audit

**Not applicable.** No external package is proposed. If a later 16C plan
introduces one, the planner must run the Package Legitimacy Gate and gate the
install behind a `checkpoint:human-verify` task per the supply-chain rule
(PLANNING-DIRECTIVES.md section 4a: pinned version, recorded checksum, named
license review).

**Packages removed due to [SLOP] verdict:** none (no packages evaluated).
**Packages flagged as suspicious [SUS]:** none (no packages evaluated).

## Architecture Patterns

### System Architecture Diagram

```
  One synthetic lesson + terms (fixture file, fictional content)
        |
        |  parsed ONCE by the one parser's independent reads
        v
  model.parse_lesson(bank_path)  +  model.parse_terms(bank_path)
  (shipped, model.py:469 / 625; headings carry lesson_slug anchors)
        |
        |  one in-memory content instance (dicts), zero re-parsing
        +----------------------+----------------------+
        v                      v                      v
  notebook-page          Cornell-notes           concept-map
  projection             projection              projection
  + validator            + validator             + validator
  (ownership,            (every cue maps         (every edge typed;
   anchors,               to notes; linear        textual adjacency
   provenance)            degradation)            fallback)
        |                      |                      |
        +----------+-----------+----------------------+
                   v
        plain-Markdown degradation check per output
                   |
                   v
  Learner note store (approved note root, OUTSIDE the repo)
    note document + revisions + provenance sidecar
    content-bearing events stay HERE (deletable, learner-owned)
                   |
                   |  lifecycle facts only (activity_completed,
                   |  activity_skipped, artifact pending), never note text
                   v
  evidence.append_event  ->  _evidence/evidence.jsonl (append-only)
  (the ONE evidence writer, evidence.py:735; read back through
   live_events, evidence.py:1355; reviewer settles via mark_event's
   human-only marker, evidence.py:1416-1447)
                   |
                   v
  Progress claim builder (GRAPH-03 tuple) -> fill-state display contract
  (numerator/denominator/indeterminate per dimension, no aggregate)
```

The learner trace: a learner reads a lesson under a registered strategy, the
precedence resolver having already composed the seven layers to decide which
strategies are offered; note capture writes to the note store; completing or
skipping the strategy's activity appends a lifecycle event through the one
evidence writer; the progress display recomputes its per-dimension claims from
`live_events`; a note the learner wants promoted enters the review path and
only source-backed reviewer acceptance can move its content toward accepted
truth; a learner artifact reads as pending until a human mark settles it.

### Recommended Project Structure

```
notes.py                 # NEW (name is a checkpoint:decision): note record
                         #   schema, epistemic roles, activity states,
                         #   multi-selector provenance, relocation resolution,
                         #   promotion/review state machine. Pure, no I/O in
                         #   core functions.
strategies.py            # NEW (name is a checkpoint:decision): the finite
                         #   strategy registry (closed tuple), the shared
                         #   strategy contract fields, fallback resolution,
                         #   and the composed seven-layer precedence resolver.
note_outputs.py          # NEW (or folded into notes.py, checkpoint:decision):
                         #   the three trio projections and their validators.
progress_claims.py       # NEW (name is a checkpoint:decision): GRAPH-03 claim
                         #   tuple builder over live_events + course records
                         #   (synthetic stand-ins until 14B lands).
upgrade_audit.py         # NEW: the eleven-item baseline audit and the
                         #   keyed-content halt detector (UPGRADE-01/02);
                         #   the legacy-upgrade skill references it.
fixtures/
├── note_strategy_corpus.py    # NEW: synthetic four-subject corpus generator
                               #   (EMT respiratory, math linear system, CS
                               #   loop invariant, history conflicting
                               #   accounts), fictional content, fixed seed.
tests/
├── note_schema_roundtrip.py       # NOTE-01
├── note_promotion_roundtrip.py    # NOTE-02, NOTE-03
├── strategy_registry_roundtrip.py # STRATEGY-01
├── strategy_precedence_roundtrip.py # STRATEGY-02 (extends 16B's fixture)
├── progress_claim_roundtrip.py    # GRAPH-03
├── note_trio_roundtrip.py         # trio prototype + broken fixtures
├── legacy_upgrade_roundtrip.py    # UPGRADE-01, UPGRADE-02
├── cross_subject_suite_tracer.py  # the freeze gate, one pass over all
```

### Pattern 1: Halting precondition check, extended to three freeze records (16B-RESEARCH Pattern 1, one degree further)

**What:** 16C-01 opens with a `type="auto"` task that (a) imports every
dependency module the phase was planned against and asserts success, (b)
asserts every cited constant and signature matches plan text, (c) checks the
literal frozen heading in `14B-FREEZE.md`, `16A-FREEZE.md`, and
`16B-FREEZE.md` (a `## Freeze withheld` heading counts as failure), (d) reads
each upstream `*-PRECONDITION.md` dated result line so a present-but-wrong
freeze resting on an unresolved divergence is caught, (e) confirms Phase
13.9's A9 closure, and (f) halts by name, writing nothing else, on any
divergence. Stubbing a missing module, wrapping the import in try/except, or
proceeding with a reduced check set is prohibited; the halt is the correct
outcome (16B-01 prohibition, carried forward verbatim in spirit).

**When to use:** any 16C plan importing `identity`, `journal` (14A), `graph`,
`course`, `course_package` (14B), `capabilities` or new `_CALLOUT_KINDS`
entries (16A), or the 16B IA module, settings keys, or conflict-copy constant.

**Also re-verify the shipped surface live** before extending it, following
16B-01's own precedent: `evidence.KNOWN_EVENT_TYPES` still equals exactly
`("response", "retraction", "mark", "day_tick", "term_lookup", "key_review",
"hint", "selection", "lesson_complete", "cap_override", "model_interaction",
"mark_proposal", "visual_action", "gate_skip")` `[VERIFIED:
evidence.py:51-55]`; `model.STYLE_CHECK_CATALOGUE` still has exactly its ten
dotted keys `[VERIFIED: model.py:2250-2261]`; `parse_lesson`/`parse_terms`
return shapes unchanged; and SHA-256 baselines for every file the phase will
prove additive against are recorded before any 16C change exists.

### Pattern 2: Parse once, project many (the trio's structural rule, shipped precedent)

**What:** The shipped one-parser discipline already supports multiple
independent purposes over one file without forking content truth.
`parse_lesson` is "A second, independent read over the bank file for a
different purpose... Never called from inside `load()` or `parse_bank()`, and
it changes neither's return shape" `[VERIFIED: model.py:469-472 docstring]`;
`parse_terms` is "A third, independent read... Mirrors `parse_lesson()`'s
boundary rule exactly" `[VERIFIED: model.py:625-632 docstring]`. Headings
carry stable anchor slugs via the single slugifier: `lesson_slug` is "One
slugifier for both the lesson lookup key and the rendered HTML anchor id
(D-03), a lookup that agrees with an anchor by coincidence eventually
disagrees, so there is structurally one call, not two" `[VERIFIED:
model.py:447-450 docstring]`.

**When to use:** the trio prototype. The one parsed content instance is the
pair of dicts `parse_lesson(path)` and `parse_terms(path)` return for one
synthetic lesson; all three projections consume those dicts; the fixture
asserts the parse functions are called exactly once (for example by counting
calls through a wrapper in the test), zero per-style content forks. Anchors in
notebook-page provenance target heading slugs today and D-14A-2 component IDs
once 14A lands (plan text; precondition-gated).

### Pattern 3: One evidence writer, one read filter, additive event types

**What:** `append_event` is "The ONE evidence writer, and the one place that
decides `recorded` versus `already_recorded`" `[VERIFIED: evidence.py:735-737
docstring]`. `live_events` is "the only function views may use for counting"
`[VERIFIED: evidence.py:1355-1359 docstring]`, and `capture_events`
materializes one immutable snapshot so derived claims cannot drift mid-render
`[VERIFIED: evidence.py:1374-1392]`. Old builds reading a log with a new event
type skip it with a warning rather than crashing `[VERIFIED:
evidence.py:765-768]`, which is the sanctioned additive path already used when
`selection`, `visual_action`, and `gate_skip` were added.

**When to use:** strategy lifecycle events (STRATEGY-01's "evidence effects")
and learner-artifact pending evidence (NOTE-03). A new event type (for
example `strategy_activity`) is appended through `append_event` only, read
back through `live_events` only, and added to `KNOWN_EVENT_TYPES` as one new
tuple member. The progress claim builder reads through
`capture_events`/`live_events`, never `events` and never a private reader.

### Pattern 4: Closed-vocabulary registry with per-entry validator (the Phase 03.1 style registry, generalized)

**What:** The shipped style registry is the exact shape the strategy registry
and the output-mode registry need: a closed catalogue of dotted codes with
severities,

```python
# [VERIFIED: model.py:2250-2261, quoted verbatim]
STYLE_CHECK_CATALOGUE = {
    "style.order_before": "error",
    "style.heading_cadence": "error",
    "style.require_marker": "error",
    "style.forbidden_marker": "error",
    "style.open_with": "error",
    "style.section_density": "warn",
    "style.sentence_length": "warn",
    "style.filler_phrase": "warn",
    "style.banned_hector": "warn",
    "style.forbidden_phrase": "warn",
}
```

plus a loader/resolver (`load_style` model.py:1363, `resolve_style`
model.py:1418) and a rendering-refusal path (`RENDER_REFUSAL_COPY =
("render_style cannot turn %s into %s; that is a ...")` at
surfaces/lesson.py:86). The 16C strategy registry mirrors this: a closed tuple
of strategy IDs, per-strategy declared contract fields (report 12 section
10.1's list: strategy_id and version, learning_purpose, input target kinds,
response semantic type, prompt and scaffold policy, optional/required policy
and equivalent actions, pause/resume behavior, note materialization policy,
feedback and source-check timing, derivation destinations, accessibility
contract), and a resolver whose unknown-or-unavailable case returns continuous
reading, never an error.

**When to use:** STRATEGY-01's registry, the trio's per-mode validators, and
the relocation-state and epistemic-role vocabularies. The note record's
discrete vocabularies come verbatim from report 12:

- Epistemic roles: `quote`, `learner_claim`, `learner_question`,
  `learner_example`, `calculation`, `diagram`, `accepted_reference_link`
  `[VERIFIED: research/phase-16/12-active-annotation-notes.md:198]`
- Activity states: `not_started`, `draft`, `completed`, `skipped_optional`,
  `equivalent_completed`, `needs_review` `[VERIFIED:
  research/phase-16/12-active-annotation-notes.md:226]`
- Relocation states: `resolved`, `relocated_exact`, `relocated_probable`,
  `orphaned`, with "Probable relocation needs review" `[VERIFIED:
  research/phase-16/12-active-annotation-notes.md:232]`
- Note status: `draft | learner_accepted | disputed | superseded | deleted`,
  from the 9.1 minimum record, quoted here verbatim:

```text
# [VERIFIED: research/phase-16/12-active-annotation-notes.md:239-249]
note_id, note_document_id, revision_id
owner_id or local-owner marker, privacy_scope
course_id, objective_ids[]
strategy_id, epistemic_role, learner_wording
targets[]:
  target_kind: source | lesson_step | media | item_public | concept
  stable_id, content_fingerprint, locator, quoted_context_hash
  media_time_range or region when applicable
derivations[]: from_note_revision | from_accepted_lesson | from_source
status: draft | learner_accepted | disputed | superseded | deleted
created_at, updated_at
```

- Strategy event family: `target_selected`, `content_composed`,
  `relation_added`, `representation_attached`, `source_checked`,
  `note_revised`, `activity_completed`, `activity_skipped` `[VERIFIED:
  research/phase-16/12-active-annotation-notes.md:292]`

### Pattern 5: Pending-until-human-review (learner artifacts and promotion)

**What:** The shipped mark pipeline already implements "runtime records
pending, reviewer settles": short answers score `None` pending review, and
`mark_event` enforces `marker="human"`, raising "mark_event: marker must be
'human' in this phase" on anything else `[VERIFIED: evidence.py:1445-1447]`,
with `mark_proposal` as the advisory-not-settling channel and `proposal_ref`
linking a human mark to the proposal it reviewed `[VERIFIED:
evidence.py:1432-1435]`.

**When to use:** NOTE-03's learner artifact (rubric attached, pending
evidence event on submission, settled only by a human mark) and NOTE-02's
promotion review (the reviewer-acceptance record follows the same
proposal-then-human-settlement shape). No new settlement mechanism is built;
16C composes the shipped one.

### Pattern 6: Guard-enforced synthetic-only content (notes stay out of the repo)

**What:** `cmd_guard` walks every `.md` outside `fixtures/` and the repo-owned
trees, refusing anything that parses as a bank, carries a bank filename hint,
sits under a private-bank/corpus directory, or carries a corpus marker (a
`## SOURCES` or `## LESSON` section) `[VERIFIED: surfaces/cli.py:299-352]`.

**When to use:** two ways. First, every 16C note/artifact fixture is generated
fictional content under `fixtures/`, keeping guard green. Second, real learner
notes live outside the repository in an approved note root (see Open Question
1); if the chosen note-document format carries its own marker (for example a
front-matter key like `note_document_id`), the planner should extend guard's
corpus-marker list additively so a stray real note pasted into the repo fails
CI the same way a stray bank does. That extension is one new marker check in
the existing function, not a second guard.

### Anti-Patterns to Avoid

- **A second parser for notes.** The note-document contract gets one canonical
  parser (report 12 section 9.1's own sentence). If notes are Markdown plus
  sidecar, the sidecar is `json` stdlib and the Markdown read reuses the
  shipped read discipline; no new markdown grammar engine.
- **A personal note scorer.** Report 12 section 7.2 item 4: "There is no
  'personal note scorer.'" Draft questions derived from notes run normal bank
  lint, review, ID assignment, and runtime scoring or they stay unkeyed
  self-prompts.
- **Note text in the evidence log.** Deletable learner content inside an
  append-only store is a contradiction; see Open Question 2.
- **A strategy toggle matrix.** Report 12 section 10.4: register tested modes,
  one primary strategy plus at most one optional supplement per lesson step,
  requiredness at activity level, never a global force-notes toggle, and kill
  any mode that requires a second parser, scorer, note truth, or UI state
  machine.
- **A second precedence table.** 16B locked the seven-layer table and its
  conflict copy; 16C builds the resolver over that table, sharing the copy
  string and extending 16B's conflict fixture rather than duplicating either.
- **An aggregate progress number.** GRAPH-03 and the 12.4 ledger hard-reject
  it; the fixture asserts no aggregate score appears anywhere.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Note/lesson anchor identity | A new slugifier or offset scheme | `model.lesson_slug` (model.py:447) today; D-14A-2 component IDs once 14A lands | One slugifier already exists by design (D-03); offsets are "fragile under edits and reflow" per report 12 section 9.2 and are at most one selector among several. |
| Change detection for relocation and upgrade halts | A new hash scheme | `model.content_fingerprint` (model.py:1451), `_key_content_hash` (model.py:1532), and 14A's `identity.object_fingerprint` with its keyed-content carve-out (plan text) | D-14A-2 forbids by name any unification that could mask a scoring-relevant change; hashes detect change but never prove identity (ID-02). |
| Evidence persistence for strategy/artifact events | A second log, queue, or private writer | `evidence.append_event` with new additive `KNOWN_EVENT_TYPES` members | Non-negotiable 2; the skip-and-warn degrade for unknown types is the proven additive path `[VERIFIED: evidence.py:765-768]`. |
| Settlement of learner-artifact marks | A new review-verdict store | `evidence.mark_event` (human-only marker) plus `mark_proposal`/`proposal_ref` | The runtime records pending and never settles; the human-marker gate is shipped enforcement. |
| Registry shape for strategies and output modes | A free-form config or plugin system | Closed tuples/dicts following `STYLE_CHECK_CATALOGUE` and `GATE_MODES = ("required", "recommended")` `[VERIFIED: evidence.py:76]` | Closed vocabularies plus dotted codes are the project-wide additive-registration discipline (16B-RESEARCH Pattern 4). |
| Progress display semantics | An invented completion widget | The GRAPH-03 claim tuple, report 08's honest-bar rules, and the D-14A-3 fill state | Report 08 section 6.3 enumerates dishonest bars; the ARIA guidance (`aria-valuenow`, `aria-valuetext`, no unexplained spinner) is already written. |
| Conflict copy for precedence overrides | New wording | 16B's locked string: "{Setting name} is set by {higher layer name} for this course and can't be changed here." `[VERIFIED: 16B-UI-SPEC.md:270-272, plan text]` | 16B never re-words a locked string; neither does 16C. |

**Key insight:** every 16C deliverable is a composition of shipped disciplines:
one parser (trio), one evidence writer (strategy events), one settlement gate
(artifacts), one registry shape (strategies, modes), one slugifier (anchors).
16C's genuinely new content is the schemas, the vocabularies, the resolver,
and the validators, all pure and all fixture-provable today.

## Do Not Re-Open (permanent rejection and supersession ledger, binding on every 16C plan)

The following are settled. A 16C plan, fixture, or decision that resurrects
one of these without the recorded reconsideration condition fails review.

From synthesis 12.4 (`[VERIFIED: research/phase-16/14-synthesis.md:668-689]`),
the rows 16C's domain touches most directly, with the full ledger binding:

1. **One aggregate completion, mastery, readiness, or personalization score.**
   Hard reject. GRAPH-03's display composes separate claims; a summary may
   link to component claims, never replace them.
2. **Viewed, clicks, elapsed time, streaks, percentile, or engagement as
   mastery.** Hard reject. Note count, highlight count, and note length join
   this list per report 12 section 12.2.
3. **Learner note silently promoted to accepted source, lesson, key, or
   mastery.** Hard reject; reconsideration only via explicit source-backed
   validation and reviewer acceptance (which is exactly NOTE-02's contract).
4. **Hover-only meaning, drag-only construct, or visual-plus-alt-text as full
   equivalence.** Hard reject; the capability returns only when equivalence
   passes (binds the trio's concept-map interaction and any highlight
   capture).
5. **Hash, path, or display name as durable identity; automatic ambiguous
   merge.** Hard reject (binds relocation: a probable match requires review,
   never auto-merge).
6. **Derived HTML, index, cache, or registry as the sole understandable
   meaning.** Hard reject (binds the trio: each projection degrades to
   coherent plain Markdown; the note store's index is disposable).
7. **Arbitrary authored JavaScript, auto-running notebooks, untrusted active
   embeds.** Hard reject (binds any interactive concept-map ambition).
8. **Hidden citations or presentation state as authorization.** Hard reject
   (binds note privacy: collapsing a note rail is not access control).
9. **Automatic evidence transfer across renamed/split/merged objectives.**
   Hard reject (binds the version-split objective in the GRAPH-03 fixture:
   unmigrated evidence reads unknown on the new identity).
10. **Chat-first home / agent activity as product center; automatic artifact
    gallery / one-shot generate-everything; fixed universal hierarchy;
    punitive streaks, hearts, paid error relief, leaderboards; copying
    protected commercial content or visual identity.** All superseded or hard
    rejected as recorded; none is a 16C surface.

From report 12 section 14.2 (`[VERIFIED:
research/phase-16/12-active-annotation-notes.md:428-439]`), all eight,
verbatim subjects:

11. **Force a quota of highlights** (compliance measure, accessibility
    burden).
12. **Retype visible prose as a general strategy** (high mechanical cost, weak
    conceptual justification).
13. **"Handwriting mode" justified by universal superiority** (direct
    replication does not support the blanket claim).
14. **Auto-card every highlight** (selection is not verified truth or good
    retrieval design).
15. **Auto-key from learner notes** (violates one-scorer and source-authority
    boundaries).
16. **Notes required in every lesson** (subject, prior knowledge, media, and
    accommodation differences matter; Minimal Lesson is first-class).
17. **One mutable document containing lesson, learner note, and bank key**
    (ownership, revision, privacy, and authority conflict).
18. **Arbitrary mix-and-match strategy settings** (combinatorial authoring,
    UI, and test failure).

Also standing from STYLE-DISCIPLINE-16A-2026-08-14.md: the four rejected
lesson styles (Feynman, cookbook, written Socratic, explorable explanations)
stay rejected; Socratic remains a runtime-gated tutoring mode whose refusal
renders as a locked card (16B FLOW-02 contract), and no output mode beyond the
trio registers before the trio passes.

## Runtime State Inventory

Not applicable in the rename/migration sense: 16C creates new modules,
vocabularies, and fixtures; it renames no stored key, path, or identifier.
Two adjacent facts recorded explicitly rather than left implicit:

- **Stored data:** none renamed. The evidence log gains new additive event
  types; old builds skip-and-warn on them by design (`[VERIFIED:
  evidence.py:765-768]`). No existing event is rewritten.
- **The D-14A-3 `mastered` field rename** is 14A's migration, not 16C's; 16C's
  progress display consumes the resolved fill-state decision and must not
  reintroduce the old name in new code.

## Common Pitfalls

### Pitfall 1: Trusting three freeze headings without their provenance chains
**What goes wrong:** 16C-01 checks that the three FREEZE files exist and
proceeds, missing that a freeze rests on an unresolved divergence its own
precondition recorded, or that 13.9's A9 closure never happened.
**Guard:** Pattern 1's full check: three frozen headings, three
`*-PRECONDITION.md` dated result lines, 13.9 A9 closure, live shipped-surface
re-verification, halt by name on any divergence, no stubbing or try/except
workaround.

### Pitfall 2: The trio quietly re-parsing or forking content
**What goes wrong:** a projection "just re-reads the file" for convenience, or
a Cornell-specific content tweak forks the instance, and the three outputs
drift from one truth.
**Guard:** the trio fixture asserts one parse (call-counting wrapper around
`parse_lesson`/`parse_terms`), zero per-style content forks (all three
projections consume the same in-memory dicts), and each validator fails on its
deliberately broken fixture (a cue without notes, an unlabelled edge, an
anchor to a moved block).

### Pitfall 3: Note content leaking into the append-only evidence store
**What goes wrong:** a strategy event carries `learner_wording` or selected
text into `evidence.jsonl`; deletion (report 12 section 11.2) then becomes
impossible without violating append-only, and private notes become
undeletable evidence.
**Guard:** the event-taxonomy decision in 16C-DECISIONS.md (Open Question 2's
recommendation) plus a fixture asserting the lifecycle event schema has no
content-bearing field: at most a note ID reference.

### Pitfall 4: An aggregate percent appearing in the progress display
**What goes wrong:** the fill-state rendering, the course card, or a report
synthesizes one ratio across dimensions because it is visually convenient.
**Guard:** the GRAPH-03 fixture asserts each tuple dimension reports
separately and no aggregate score appears; a missing denominator asserts
indeterminate, never an invented percent; Retrievability is asserted never to
render as a percentage.

### Pitfall 5: The strategy registry growing into a toggle matrix
**What goes wrong:** per-widget settings multiply across target type,
requiredness, scaffold, response form, privacy, feedback, derivation, and
subject, exactly the combinatorial failure report 12 section 10.4 names.
**Guard:** the registry is a closed tuple of four strategies (STRATEGY-01's
list); one primary strategy plus at most one optional supplement per lesson
step; requiredness at activity level; the kill criterion (second parser,
scorer, note truth, or UI state machine) written into the freeze record.

### Pitfall 6: The two "activity" vocabularies colliding
**What goes wrong:** report 12 section 8.1's per-action states
(`not_started`, `draft`, `completed`, `skipped_optional`,
`equivalent_completed`, `needs_review`) get conflated with 16B's Activity IA
area (durable agent/maintenance jobs) or with `REQUIREMENTS.md`'s
`ACTIVITY-*` learner-question family; a fixture named `activity_*` becomes
unreadable.
**Guard:** 16B-UI-SPEC's naming rule carried forward: "Activity view"
(capitalized, IA jobs sense) versus "activity" (lowercase, learner task
sense); every 16C fixture and module docstring touching either carries the
distinguishing doc comment; 16C's per-action states are named
**strategy-action states** in code and docs.

### Pitfall 7: An upgrade silently touching keyed meaning
**What goes wrong:** a legacy-upgrade pass reflows a lesson and, in passing,
edits a `CORRECT:` line, a rubric, or an objective tag; the fingerprint
normalization masks it.
**Guard:** UPGRADE-02's halting fixture; the audit compares keyed-content
hashes (`_key_content_hash`, `content_fingerprint`) before and after the
proposed diff and halts for explicit assessment review on any delta; D-14A-2's
carve-out (no trailing-whitespace normalization for `bank`/`lesson` kinds) is
asserted at the precondition check.

### Pitfall 8: Real note content entering the repository
**What goes wrong:** a real learner note or a real-corpus-derived note fixture
is committed; `itembank guard` may not catch a note file that carries no bank
or lesson marker.
**Guard:** every fixture is generated fictional content under `fixtures/`
(guard-exempt by location and synthetic by construction); the note-document
marker is added to guard's corpus-marker list additively so a stray real note
fails CI; the freeze-gate plan runs `python itembank.py guard .` and asserts 0
offending files (16B-11 precedent).

### Pitfall 9: Auto-resolving a probable relocation
**What goes wrong:** the relocation resolver treats a high-similarity match as
`relocated_exact` and silently moves the anchor, converting a guess into
provenance.
**Guard:** the relocation vocabulary is closed; `relocated_probable` requires
review by contract (report 12 section 8.2); the NOTE-01 fixture's invalidated
anchor asserts the note stays attached to its objective with the broken
selector flagged, not silently relocated.

### Pitfall 10: Duplicating 16B's precedence contract instead of composing it
**What goes wrong:** 16C writes its own seven-layer table or its own conflict
string, and the two phases drift.
**Guard:** the resolver reads the one table; the conflict copy is the 16B
constant reused verbatim; the STRATEGY-02 fixture extends 16B's
settings-schema conflict fixture (16B-UI-SPEC Mode-Layer contract item 3)
rather than duplicating enforcement logic. The 16C-01 precondition check
verifies the constant's exact text against whatever 16B execution shipped.

### Pitfall 11: Pre-highlighting recorded as learner evidence
**What goes wrong:** authored emphasis (sparse orientation) generates events or
counts toward participation, converting the author's attention cues into
learner claims (clause C107's exact subject).
**Guard:** the NOTE-01 schema marks authorship type; the fixture asserts an
authored pre-highlight produces zero evidence events and zero note ownership.

## Code Examples

### The strategy registry and fallback (proposed shape, composing shipped precedents)

```python
# Shape follows STYLE_CHECK_CATALOGUE (model.py:2250) and GATE_MODES
# (evidence.py:76). Contract fields from report 12 section 10.1 (verified).
STRATEGY_IDS = ("continuous_reading", "guided_note_spine",
                "worked_reasoning", "retrieval_first")
FALLBACK_STRATEGY = "continuous_reading"

def resolve_strategy(requested, available, allowed):
    """STRATEGY-01 degraded path: an unavailable or disallowed strategy
    falls back to continuous reading, never an error."""
    if requested in STRATEGY_IDS and requested in available \
            and requested in allowed:
        return requested
    return FALLBACK_STRATEGY
```

### The precedence resolver's fixed-layer rule (composing 16B's locked table)

```python
# The seven layers, lowest to highest, from the 16B-locked table
# (16B-UI-SPEC.md Mode-Layer Precedence Contract, plan text; synthesis
# section 8 table verified this session).
PRECEDENCE_LAYERS = ("learner_preference", "author_course_strategy",
                     "objective_constraint", "accommodation_override",
                     "instructor_policy", "runtime_authority",
                     "system_safety")
# 16B's locked conflict copy, reused verbatim, never re-worded:
CONFLICT_COPY = ("{setting} is set by {layer} for this course "
                 "and can't be changed here.")
# Runtime authority and system safety are FIXED: the resolver reads them
# as constants, never as composable opinions, and nothing a lower layer
# states can change scoring, keyed disclosure, retries, or formal-test
# pause during a sitting (STRATEGY-02).
```

### Appending a strategy lifecycle event (evidence side of the split)

```python
# The ONE evidence writer (evidence.py:735). A lifecycle event carries a
# note ID reference at most, NEVER note text (Open Question 2).
import evidence
event = {
    "schema_version": evidence.EVENT_SCHEMA_VERSION,
    "event_type": "strategy_activity",   # new additive KNOWN_EVENT_TYPES
    "event_id": evidence.new_event_id(), # member; old builds skip-and-warn
    "session_id": session_id,
    "strategy_id": "guided_note_spine",
    "action_state": "completed",         # strategy-action state vocabulary
    "note_ref": note_id_or_none,         # reference only, no content
    "ts": evidence.utc_now(),
}
result = evidence.append_event(log, event)  # recorded / already_recorded
```

## Assumptions Log

Every claim below is `[ASSUMED]` or plan-text-sourced; each names its
falsifying condition. The planner treats each as an input to 16C-01's
precondition check or decisions record, never as settled fact.

| # | Assumption | Falsifying condition |
|---|-----------|----------------------|
| A1 | 16B's conflict copy ships as the exact string "{Setting name} is set by {higher layer name} for this course and can't be changed here." and is importable or quotable as one constant. (Plan text: 16B-UI-SPEC Mode-Layer item 2.) | 16B execution ships different wording or no shared constant; caught by 16C-01 re-verifying the string against the executed 16B surface. |
| A2 | 14A ships `identity` object IDs (16-char hex, never content/path/name derived) and component-level anchor IDs per D-14A-2, usable as note anchor targets; until then heading slugs via `lesson_slug` are the anchor scheme. (Plan text: 14A-01-PLAN.) | 14A executes with a different ID scheme or granularity; caught by the precondition check asserting `identity` constants; the note schema's `targets[].stable_id` field is scheme-agnostic by design so only the resolver changes. |
| A3 | 16A ships `capabilities.py` (or its renamed equivalent) and the shared note/activity schema hooks CAP-03 names, which the trio and note modules compose rather than duplicate. (Plan text: 16A-RESEARCH, 16A plans.) | 16A executes with a different module boundary or schema shape; caught by 16C-01; the trio's projections depend only on `parse_lesson`/`parse_terms` shapes (shipped), so divergence narrows to the registration seam. |
| A4 | 14B ships `graph.py` course records and `outline_projection`; the GRAPH-03 claim builder's design-coverage dimension reads them; until then a synthetic course-record stand-in, named as such in the plan, feeds the fixture. (Plan text: 14B plans.) | 14B's record shape diverges; caught by precondition; the claim tuple itself is independent of the record shape. |
| A5 | Real learner notes live outside the repo in an approved note root governed by 16B's `approved_roots` settings key, following the `_evidence/`-beside-the-private-bank precedent; `itembank guard` needs one additive marker check to refuse stray note documents. | Weibao's D-12.6-5 resolution or 16B execution places notes elsewhere; the note store's path resolution is a settings read, so relocation is a config change, not a schema change. |
| A6 | New additive `KNOWN_EVENT_TYPES` members are the sanctioned evidence route for strategy lifecycle events; `EVENT_SCHEMA_VERSION` (currently 2, `[VERIFIED: evidence.py:36]`) does not need a bump because no existing event's shape changes. | A reviewer determines a new event type requires a schema-version bump; the additive fixture (old log parses byte-identically, old build skip-and-warns on new types) decides this empirically in Wave 0. |
| A7 | `parse_lesson` and `parse_terms` return shapes as read this session (headings with `text`/`slug`/`body`; terms with `canonical`/`aliases`/`def`/`xlat`/`see`, plus `refs`/`ignored`/`empty`/`collisions`) remain unchanged through 16A execution. | 16A's lesson-capability work alters the returned dicts; caught by 16C-01's live shape re-verification. |
| A8 | D-12.6-5 (notes default placement, Evidence prominence) remains pending with Weibao; 16C proceeds under its recorded recommendation C (margin capture, course review) composed with 16B D4 (contextual Notes inside Learn and Evidence, no dedicated route), both reversible presentation decisions. | Weibao decides differently; the note schema is placement-agnostic (anchors plus objective relation), so only the presentation contract and D4's placement note change. |
| A9 | The four registered strategies are STRATEGY-01's list (continuous reading, guided note spine, worked reasoning, retrieval-first/assessment-first), with report 12 section 10.2's seven modes remaining the catalog runway (Minimal lesson folds into continuous reading; Close reading deferred until provenance relocation works, per 10.4's own recommendation). | The freeze-gate cross-subject run shows a fifth mode is required to pass a fixture, or one of the four fails its kill criterion (report 12 section 14.4) and is prototyped out. |
| A10 | The trio's "one parsed content instance" is the `parse_lesson` plus `parse_terms` output pair over one synthetic lesson; concept-map edges derive from `[[term]]` refs and typed relations declared in the fixture, not from a new inline grammar. | The 16A-frozen semantic profile defines a different canonical relation source; caught by 16C-01; the projections' input contract is the decision record's to pin. |
| A11 | The eleven-item baseline audit can run today against a synthetic pre-13.5 lesson using shipped functions (`parse_bank`, `parse_lesson`, `content_fingerprint`, lint, plain/rich rendering paths), with identity/rights columns reading "plan-text stand-in" until 14A/14B land. | A reviewer requires real 14A identity in the audit before the fixture counts; then UPGRADE plans move behind the precondition boundary entirely. |

## Open Questions (each with a recommendation; none left undecided for the planner)

1. **Where exactly do note files live, and in what format?**
   - What we know: FILE-01 names note directories as an approved-root class;
     16B's `approved_roots` settings key (plan text) is the governing
     vocabulary; evidence-beside-the-private-bank is the shipped residency
     precedent; report 12 section 9.1 allows Markdown with a machine-metadata
     sidecar and requires one canonical parser; section 14.5 lists
     inline-vs-sidecar as an open question with prototypes as the evidence
     route.
   - Recommendation: one note document per course per learner surface, as
     coherent Markdown plus a JSON sidecar carrying the 9.1 machine record
     (targets, fingerprints, hashes, states), stored in a learner note root
     declared in `approved_roots`, defaulting to a `_notes/` directory beside
     the private bank (mirroring `_evidence/`). The sidecar is the machine
     truth for anchors; the Markdown is the human/export truth for wording;
     the pair is written with the compare-and-swap discipline. Lock this in
     16C-DECISIONS.md as reversible (a path and format choice behind one
     reader), and record that D-12.6-5's IA-placement half stays held for
     Weibao.

2. **Which events are evidence and which are private note state?** (The
   load-bearing distinction named in the phase brief.)
   - What we know: strategies emit the eight-member event family (report 12
     section 10.1); the evidence log is append-only with one writer; report 12
     section 11.2 requires note deletion to cover the note and its private
     index while preserving only explicitly required assessment evidence;
     participation is a separate honest-progress dimension from settled
     evidence (report 08 section 6.1); pre-highlighting is never learner
     evidence (C107).
   - Recommendation: split by content. **Evidence store (additive event
     types):** `activity_completed` and `activity_skipped` lifecycle facts
     (participation dimension), and the existing `mark`/`mark_proposal`
     machinery for learner-artifact pending/settled evidence. These carry
     strategy ID, action state, and at most a note ID reference, never note
     text. **Note store (learner data, deletable):** `target_selected`,
     `content_composed`, `relation_added`, `representation_attached`,
     `note_revised`, and `source_checked`'s compared content, stored as note
     revisions and sidecar records. `source_checked` may additionally emit a
     content-free lifecycle event if the monitoring dimension needs it, but
     the compared text stays in the note store. Rationale: deletability versus
     append-only is a hard incompatibility; participation without content is
     the only evidence-safe projection of note activity, and note count or
     length can never be mastery anyway (12.4 ledger). Lock in
     16C-DECISIONS.md as the phase's first recorded decision.

3. **Where does the composed precedence resolver live, and what feeds its
   layer states before 14B/15A exist?**
   - What we know: 16B D8 defers the resolver here by name; the fixed layers
     are shipped runtime behavior; author/course strategy and instructor
     policy read course records (14B, plan text) and the objective constraint
     reads blueprint data (15B, unexecuted and not a 16C dependency).
   - Recommendation: a pure `resolve(layers_state) -> effective_settings +
     conflicts` function in the strategies module, taking each layer's state
     as an explicit input dict so it is testable today with synthetic layer
     states and wired to real course records later without signature change.
     The conflict output carries the 16B copy string filled per conflict. The
     STRATEGY-02 fixture feeds the conflict matrix (learner preference vs
     accommodation override vs instructor policy) directly, extending 16B's
     fixture data rather than its enforcement logic.

4. **What content does the trio parse, given 16A's semantic profile is
   unexecuted?**
   - What we know: the shipped parser already returns lessons (headings with
     slugs) and terms (records plus `[[term]]` refs); STYLE-DISCIPLINE
     requires one lesson plus its terms and relations parsed once; the
     concept map needs typed edges; 16A's expanded semantic roles are plan
     text.
   - Recommendation: build the trio over shipped `parse_lesson` +
     `parse_terms` output for one synthetic lesson, with typed relations
     supplied by the fixture generator as explicit data (not a new inline
     grammar), and record in the freeze that trio anchors upgrade from
     heading slugs to D-14A-2 component IDs at the integration seam once 14A
     lands. This keeps the prototype executable now and keeps the one-parser
     rule literal.

5. **Does 16C build any UI, or only contracts and fixtures?**
   - What we know: 16C is listed among the subphases owing `/gsd-ui-phase`
     work when a learner-facing surface is introduced (PLANNING-DIRECTIVES
     section 8 table); 16B reserved Notes placement (D4) and deferred
     rendering to 17A; the progress display and note surfaces are
     learner-facing.
   - Recommendation: mirror 16B's posture: 16C ships the structural and copy
     contracts (fill-state display contract, note rail and capture contract,
     locked strings) plus fixtures, with pixel rendering deferred to 17A. Run
     `/gsd-ui-phase 16C` before `/gsd-plan-phase` to produce a 16C-UI-SPEC
     covering the note capture/review surfaces and the progress display,
     voice and token assignment only, matching 16B-UI-SPEC's deferral
     pattern.

6. **How does the legacy-upgrade contract land: skill, code, or both?**
   - What we know: the `legacy-upgrade` skill exists as a stub ("Not usable
     yet; its command surface has not shipped"); UPGRADE-01's owner is the
     legacy-upgrade skill; the audit's detection primitives are shipped code.
   - Recommendation: both halves, split by authority. Code:
     `upgrade_audit.py` with the eleven-item baseline audit and the
     keyed-content halt (pure functions plus fixtures, UPGRADE-01/02
     provable today). Skill: the playbook that drives the audit and the
     bounded-diff review flow, updated from stub to usable only insofar as
     its command surface exists; anything needing 14A journaling stays
     documented as precondition-gated. The fixture proves the code path; the
     skill references the same functions rather than restating rules.

7. **Do the four strategies each need a working interactive surface for the
   freeze gate, or does the contract-plus-fixture level suffice?**
   - What we know: the freeze gate runs "every registered strategy... against
     the synthetic subjects" with one marked unavailable; PLANNING-DIRECTIVES
     section 3a mandates the guided-note, worked-reasoning, and
     provenance-relocation pathways be prototyped before the registry
     freezes; report 12 section 12 defines prototypes A/B/C with success
     gates.
   - Recommendation: the freeze gate exercises each strategy's **contract**
     (eligibility, actions, skip/resume, evidence effects, fallback) through
     the registry and fixtures, plus three deeper prototype tracers matching
     report 12's A (guided note spine: no note loss after interruption, every
     block returns to source, no key appears), B (worked reasoning: wrong
     explanations stay learner claims and cannot seed a key), and C
     (provenance relocation: exact, probable-requires-confirmation, orphan
     recovery, export/reimport without losing ownership). Interactive
     keyboard/screen-reader rendering equivalence is asserted at the contract
     level (accessible equivalent named per required action) with full visual
     QA at 17A, mirroring how 16B handled APP-02's narrow-layout assertions.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | All 16C code and fixtures | Yes | 3.11+ | none needed |
| `identity.py`, `journal.py` (14A) | Component-ID anchors, upgrade journaling | No, confirmed missing this session | none | Heading-slug anchors plus synthetic stand-ins behind the 16C-01 precondition check |
| `graph.py`, `course.py`, `course_package.py` (14B) | Design-coverage dimension of GRAPH-03, course-scoped strategy layers | No, confirmed missing this session | none | Synthetic course-record stand-ins named as such in plans |
| `capabilities.py`, expanded `_CALLOUT_KINDS` (16A) | Trio registration seam, semantic-role rendering | No, confirmed missing this session | none | Trio built over shipped parse functions; registration seam precondition-gated |
| 16B IA module, settings keys, conflict-copy constant | Precedence resolver copy, note-root settings | No, 16B unexecuted (no FREEZE record) | none | Resolver takes layer state as explicit input; copy string transcribed from plan text and re-verified at 16C-01 |
| Git | Phase-state inspection, commits | Yes | working tree confirmed | none needed |

**Missing dependencies with no fallback:** none. Every missing dependency has
the degrade-and-precondition-check fallback 16A and 16B already established.

## Validation Architecture

(Seeds `16C-VALIDATION.md`. `config.json` `workflow.nyquist_validation` is
`true` `[VERIFIED: .planning/config.json, read this session]`.)

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Direct-execution Python scripts, no pytest/unittest runner, matching every existing `tests/*_roundtrip.py` and `tests/*_tracer.py` file `[VERIFIED: tests/ directory listing, this session]` |
| Config file | none |
| Quick run command | `python tests/note_schema_roundtrip.py` (per-file) |
| Full suite command | the CI invocation in `.github/workflows/ci.yml` (the planner confirms it verbatim before writing verify steps, per the 16B-RESEARCH precedent) |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NOTE-01 | Note record carries every required field; invalidated anchor keeps objective attachment and flags the broken selector; authored pre-highlight yields zero evidence and zero ownership | unit + fixture | `python tests/note_schema_roundtrip.py` | Wave 0 |
| NOTE-02 | Source-backed review promotes one note; the unreviewed note stays learner-private and non-authoritative; no silent path from note to key/score/mastery | integration | `python tests/note_promotion_roundtrip.py` | Wave 0 |
| NOTE-03 | Fictional proof with rubric reads pending until a scripted human mark settles it; a non-human marker is refused | integration (composes shipped `mark_event`) | `python tests/note_promotion_roundtrip.py` | Wave 0 |
| STRATEGY-01 | Each registered strategy declares its full contract; an unavailable strategy falls back to continuous reading | unit + fixture | `python tests/strategy_registry_roundtrip.py` | Wave 0 |
| STRATEGY-02 | Conflict matrix resolves toward the higher layer with the 16B copy verbatim; no mid-sitting change to runtime-authority settings | unit + fixture (extends 16B's conflict fixture data) | `python tests/strategy_precedence_roundtrip.py` | Wave 0 |
| GRAPH-03 | Missing denominator reports indeterminate; pending prose mark stays pending; version-split objective reads unknown on the new identity; no aggregate score string anywhere in output | unit + fixture | `python tests/progress_claim_roundtrip.py` | Wave 0 |
| Trio | One parse feeds three projections; each validator fails its broken fixture (cue without notes, unlabelled edge, anchor to a moved block); each output degrades to coherent plain Markdown | integration | `python tests/note_trio_roundtrip.py` | Wave 0 |
| UPGRADE-01 | Baseline audit runs first over a synthetic pre-13.5 lesson; enhancement lands as a bounded diff; identity and source history preserved | integration | `python tests/legacy_upgrade_roundtrip.py` | Wave 0 |
| UPGRADE-02 | Scripted upgrade touching a keyed answer halts for explicit assessment review | integration | `python tests/legacy_upgrade_roundtrip.py` | Wave 0 |
| Freeze gate | All fixtures above run in one pass over the four synthetic subjects, plus prototypes A/B/C's success-gate assertions, plus `python itembank.py guard .` reporting 0 offenders, plus the evidence-log additivity check (old log parses byte-identically; a new-type event is skip-and-warned by the reader contract) | tracer | `python tests/cross_subject_suite_tracer.py` | Wave 0 |

### Sampling Rate

- **Per task commit:** the specific new test file the task's verify step names.
- **Per wave merge:** every new 16C test file plus `python
  tests/evidence_roundtrip.py` (the evidence store gains event types) and
  `python tests/lesson_roundtrip.py` (the trio reads lesson parsing), both
  existing `[VERIFIED: tests/ listing]`.
- **Phase gate:** full suite green before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `fixtures/note_strategy_corpus.py` (shared four-subject synthetic
      generator; fictional content, fixed seed, guard-green)
- [ ] all eight test files named above
- [ ] Framework install: none, stdlib only

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Single-learner local product, no accounts; unchanged. |
| V3 Session Management | Partial | Any new note/strategy route added later must sit behind the existing loopback token gate; 16C's own deliverables are modules and fixtures, not routes. |
| V4 Access Control | Yes | The precedence resolver IS an access-control contract: fixed layers (runtime authority, system safety) are never composable or user-configurable during a sitting; note privacy scope is enforced at read time, and presentation state never grants authorization (12.4 ledger row 8). |
| V5 Input Validation | Yes | Note documents and sidecars are untrusted learner input: closed vocabularies validated on read (epistemic role, activity state, relocation state, status), refusal of unknown required fields, and HTML-escaping of learner wording at any render point per the shipped `html` module discipline. |
| V6 Cryptography | No | Fingerprints/hashes here detect change, never prove identity or provide security (ID-02); no new cryptographic operation. |

### Known Threat Patterns for this phase

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Learner note text sent to a hosted model without explicit choice | Information Disclosure | Report 12 section 11.2: no note text to a model unless the learner chooses a bounded operation and sees destination, fields, retention boundary, and proposed write; rights/egress grants are per operation and unknown stays restrictive. |
| Note-derived draft question laundering a key from a learner claim | Tampering / Elevation of authority | NOTE-02's accepted-source support edge rule: a keyed factual claim requires an accepted-source edge; a learner note affects selection or phrasing only; no personal note scorer. |
| Learner note wording rendered unescaped into HTML surfaces | Injection (XSS) | Escape all learner wording at render time; learner content never becomes markup or script; bank-authored JavaScript remains refused (VIS-01) and note-authored anything-executable inherits the same refusal. |
| Note anchor locator escaping the approved root (path traversal) | Information Disclosure | The `[LESSON-SRC:]` containment precedent: resolve against the owning root and refuse anything escaping it before any open `[VERIFIED: model.py:482-489 docstring]`; note target locators apply the same absolute-path-plus-separator containment. |
| Private note content leaking into shared or promoted artifacts | Information Disclosure | Report 12 section 7.2 item 7: a generated draft inherits the most restrictive input scope until the learner explicitly approves another destination; export and share are separate rights grants. |
| Evidence-store pollution with deletable content | Repudiation / Privacy | The event-taxonomy split (Open Question 2): lifecycle facts only in evidence; content stays in the deletable note store. |
| Upgrade diff smuggling a keyed change past review | Tampering | UPGRADE-02 halt on keyed-content hash delta; D-14A-2 normalization carve-out asserted at precondition. |

## Proposed Plan-Shape Sketch

Mirrors 16A/16B: plan 01 and the final freeze-gate plan are `autonomous:
false` (matching 16B-01 and 16B-11 `[VERIFIED: 16B-01-PLAN.md:10,
16B-11-PLAN.md:12, both "autonomous: false"]`); middle waves are autonomous.
Nine plans, six waves.

| Plan | Wave | Autonomous | Delivers |
|------|------|-----------|----------|
| 16C-01 | 1 | no | Precondition check (three freeze headings, three precondition dated-result lines, 13.9 A9 closure, live shipped-surface re-verification, SHA baselines) writing `16C-PRECONDITION.md`; `16C-DECISIONS.md` locking: the evidence/note-state event split (OQ2), note file placement and format (OQ1), module names, the four-strategy registry contents (A9), the 16B conflict-copy transcription, the strategy-action-state naming rule (Pitfall 6), and the trio's input contract (OQ4). Halts by name on divergence. |
| 16C-02 | 2 | yes | `fixtures/note_strategy_corpus.py` (four synthetic subjects) plus the note record schema, closed vocabularies, multi-selector provenance, and relocation resolution (`tests/note_schema_roundtrip.py`, NOTE-01). |
| 16C-03 | 2 | yes | Strategy registry with declared contracts and fallback (`tests/strategy_registry_roundtrip.py`, STRATEGY-01). |
| 16C-04 | 2 | yes | Progress claim tuple builder and fill-state display contract (`tests/progress_claim_roundtrip.py`, GRAPH-03). |
| 16C-05 | 3 | yes | Composed precedence resolver, explicit-layer-state signature, 16B copy reused, conflict-matrix fixture extending 16B's (`tests/strategy_precedence_roundtrip.py`, STRATEGY-02). |
| 16C-06 | 3 | yes | Promotion/review contract and learner-artifact pending evidence composing `mark_event`/`mark_proposal` (`tests/note_promotion_roundtrip.py`, NOTE-02, NOTE-03), plus the additive `KNOWN_EVENT_TYPES` extension with its byte-identical old-log fixture. |
| 16C-07 | 4 | yes | The note-output trio: three projections, three validators, three broken fixtures, plain-Markdown degradation, parse-once assertion (`tests/note_trio_roundtrip.py`), plus prototype tracers A/B/C success gates (guided note spine, worked reasoning, provenance relocation). |
| 16C-08 | 5 | yes | Legacy-upgrade contract: `upgrade_audit.py` eleven-item baseline audit, bounded-diff shape, keyed-content halt (`tests/legacy_upgrade_roundtrip.py`, UPGRADE-01/02); `legacy-upgrade` skill text updated to reference the shipped functions. |
| 16C-09 | 6 | no | The cross-subject missing-feature suite in one pass (`tests/cross_subject_suite_tracer.py`), guard run asserting 0 offenders, full-suite regression, `16C-TRACER-REPORT.md` (measured figures only, no targets), `16C-REVIEW.md`, and `16C-FREEZE.md` whose scope statement says verbatim what ROADMAP requires: the freeze covers the note and learner-artifact schemas, the promotion and review contract, the finite strategy registry, the composed precedence resolver, the progress comprehension display, the note-output trio, and the legacy-upgrade contract only; it is not a visual/token freeze (17A), not an IA freeze (16B), not a semantic-capability freeze (16A), not a course-schema freeze (14B). |

A `/gsd-ui-phase 16C` run (OQ5) precedes plan-phase to produce the 16C-UI-SPEC
for the note capture/review surfaces and the progress display, deferring
pixels to 17A exactly as 16B-UI-SPEC did.

## Sources

### Primary (HIGH confidence: read directly this session)

- `.planning/ROADMAP.md` Phase 16C section (lines 2032-2142)
- `.planning/REQUIREMENTS.md` GRAPH-03 (403-424), NOTE-01/02/03 (633-663),
  STRATEGY-01/02 (667-689), UPGRADE-01/02 (923-942), FILE-01 (438-446)
- `.planning/PLANNING-DIRECTIVES.md` sections 2, 3, 3a, 4, 4a, 5, 8 (full file)
- `.planning/STYLE-DISCIPLINE-16A-2026-08-14.md` (full file)
- `.planning/research/phase-16/14-synthesis.md` sections 5, 7.2, 7.3, 8, 10,
  12.4 (lines 321-470, 533-712)
- `.planning/research/phase-16/12-active-annotation-notes.md` sections 4-15
  (lines 88-489)
- `.planning/research/phase-16/08-curriculum-hierarchy-progress.md` sections
  6.1-6.3 (lines 366-457)
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md` (full file:
  D1-D9, mode-layer contract, conflict copy, Activity naming rule, deferred
  table)
- `.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md` (full
  file; structural template and Pattern 1)
- `.planning/phases/16B-ia-modes-recovery-contract/16B-01-PLAN.md` and
  `16B-11-PLAN.md` frontmatter (autonomous flags, precondition/freeze shapes)
- `.planning/DECISIONS-12.6-REMAINING-2026-08-14.md` (D-12.6-5 pending,
  D-12.6-11)
- `.planning/DECISIONS-PRE-14A-2026-08-14.md` D-14A-2 (via 14A-01-PLAN
  citations), D-14A-3 (lines 107-137)
- Shipped code read this session: `model.py` (60, 447-467, 469-500, 625-660,
  1363, 1418, 1451, 1532, 2250-2261), `runtime.py` (44, 303), `evidence.py`
  (36-92, 735-774, 1355-1392, 1416-1447), `surfaces/lesson.py` (21-86),
  `surfaces/study.py` (module heads), `surfaces/cli.py` (299-364)
- `tests/` and `fixtures/` directory listings; `.planning/config.json`
  workflow block; repo root `ls *.py`; `find` for FREEZE/SUMMARY/PRECONDITION
  records (all run this session)

### Secondary (MEDIUM confidence: plan text for unexecuted phases)

- `14A-01-PLAN.md`, `14A-02-PLAN.md` (identity/journal surfaces, D-14A-2
  carve-out)
- `16A-RESEARCH.md`, `16A-PATTERNS.md` (capabilities.py boundary, CAP-03
  shared-schema rule)
- 14B plan directory listing (graph/course modules named, unexecuted)

### Tertiary (LOW confidence)

- None. No web search was required; every question resolves against in-repo
  binding documents and shipped code.

## Metadata

**Confidence breakdown:**
- Shipped-precedent patterns (parse-once, one writer, closed registries,
  human-only marks, guard): HIGH, all read from executed source this session.
- Requirement scope and fixtures: HIGH, quoted from REQUIREMENTS.md and
  ROADMAP.md read this session.
- 14A/14B/16A/16B composition seams: MEDIUM, plan text only, every one behind
  the 16C-01 precondition check with a named falsifying condition.
- New-module design (event split, resolver signature, sidecar format): this
  research's synthesis, `[ASSUMED]`, locked as recorded decisions in 16C-01
  rather than silently carried.

**Research date:** 2026-08-15
**Valid until:** re-verify immediately if any `*-FREEZE.md` comes into
existence (at that point every plan-text claim must be re-checked against the
executed surface, which is exactly what 16C-01's precondition check does);
otherwise treat as valid for 30 days.
