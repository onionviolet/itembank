---
phase: 15B
slug: quality-blueprint-acceptance
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-15
closed: 2026-08-30
---

# Phase 15B Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `15B-RESEARCH.md` section "Validation Architecture". The planner
> fills the Per-Task Verification Map once plan and task IDs exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None. Direct-execution Python scripts, this project's established convention (not pytest, not unittest) |
| **Config file** | none. See the `tests/*_roundtrip.py` convention; every test file defines its own local `fail(msg)` helper |
| **Quick run command** | `python tests/acceptance_tracer.py` (the freeze-gate tracer) plus whichever single new or extended test file the task adds |
| **Full suite command** | `for t in tests/*.py; do python "$t" || exit 1; done` |
| **Measured runtime** | **100 test files, 884 seconds**, 0 failures, measured 2026-08-30 on **Darwin 27.0.0 arm64, Python 3.14.6**. `tests/acceptance_tracer.py` alone: 31.9 seconds. `tests/blueprint_roundtrip.py` alone: 1 second. |

---

## Sampling Rate

- **After every task commit:** the quick run command for that task's specific new or changed test file.
- **After every plan wave:** the 15B subset plus the shipped-anchor spot check `python tests/scoring_roundtrip.py && python tests/evidence_roundtrip.py` (the anchor-check discipline 14A-01 Task 3 established), plus `python tests/authoring_roundtrip.py` if it exists, because 15B extends the shipped Phase 11 authoring gate composition.
- **Before `/gsd-verify-work`:** full suite green, the lesson-plus-practice acceptance tracer green, and `python itembank.py guard .` reporting `0 offending files`.
- **Freeze gate:** no 15B freeze record is written on a red acceptance tracer (mirrors 14A-04 Task 4, 14B-06, and 15A-06).
- **Max feedback latency:** **1 second**, measured 2026-08-30 on Darwin 27.0.0
  arm64, Python 3.14.6: one `python3 tests/blueprint_roundtrip.py` run, which
  is the quick-run command every 15B task except 15B-07 verifies with. It
  stayed fast across five plans because the unit file drives pure functions and
  builds its course roots in a temp directory; the freeze-gate tracer, which
  spawns six shipped suites and a fresh-process replay, carries the cost
  instead at 31.9 seconds. Recorded, not compared against a target.

---

## Phase Requirements -> Test Map

Seeded from `15B-RESEARCH.md`. The planner expands this into the Per-Task
Verification Map below.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| ACTIVITY-02 | A drafted question set stays a draft until parser, lint, review, blueprint, and runtime gates all pass; the exam-fidelity claim appears only after all five | Tracer scenario | `python tests/acceptance_tracer.py` (new) | Wave 0 gap |
| RELIABILITY-03 | A source edit marks its dependent bindings and proposals stale; acceptance is blocked until a rebind, migrate, supersede, or retain disposition is recorded | Tracer scenario, fault-style (edit a synthetic source mid-flow) | `python tests/acceptance_tracer.py` (new) | Wave 0 gap |
| AGENT-03 | A proposal built over a sparse synthetic evidence set (two attempts on one objective) names its window, denominator, and uncertainty and refuses a mastery percentage | Unit plus recursive-walk assertion, following 15A-02's `check_recommendation_edges` pattern | `python tests/acceptance_tracer.py` (new) | Wave 0 gap |

---

## Per-Task Verification Map

Populated by the planner at plan time (2026-08-15). Plan 15B-07 Task 3 updates
the Status column to `pass` or to the reason it is not, and replaces the
Estimated runtime placeholder above with a measured figure.

**Status filled 2026-08-30 by plan 15B-07 Task 3**, against a re-run tree
rather than a remembered one. Every row reads `pass` except 15B-07 Task 2, the
human review, which reads `waived`.

`waived` is not one of the planner's values. It is added rather than forcing
that row into `pass`, because the row's Behavior column reads "a HUMAN judges
that refusals, findings, proposals, and audit rows are legible, and signs", and
an agent judged it. `15B-REVIEW.md` exists, answers every question in review
steps 3 through 7, records seven concerns, and carries the verdict `accept with
concerns recorded` with a signature and a date, so the freeze's second leg is
satisfied. What is not satisfied is the word `human`. Weibao waived the
requirement on 2026-08-30; the waiver is recorded here, in `15B-REVIEW.md`'s
Provenance section, in `15B-FREEZE.md`, and in `D-15B-4`, rather than absorbed
into a green mark.

**Two rows name assertion functions that do not exist under those names**, and
the code is the authority: 15B-06 Task 2's `check_proposal_edges` and 15B-07
Task 1's `scenario_course_audit_provenance` landed as `check_evidence_proposal`
and `scenario_course_audit`. Every assertion the plan named is made; only the
function names differ.

`Status` values: `planned` means the row is authored and the task has not run
yet. Every row below carries an automated command; the three
`checkpoint:decision` rows and the one `checkpoint:human-verify` row are
verified by a file assertion over the artifact the checkpoint produces, and the
one genuinely manual verification is the freeze-gate review recorded in its own
table further down.

| Plan | Task | Req ID | Behavior | Test Type | Automated Command | Assertion function | Status |
|------|------|--------|----------|-----------|-------------------|--------------------|--------|
| 15B-01 | 1 preconditions | all three | 14A, 14B, and 15A landed with the constants 15B was planned against and three real freeze records, or halt by name | precondition check | `python -c "import identity, journal, graph, course, director; assert len(graph.MIGRATION_STATES)==3 and len(graph.BINDING_STATES)==5 and len(director.PROTOCOL_STEPS)==13 and len(journal.ENTRY_KEYS)==24 and not hasattr(graph,'accept_migration'); print('15B preconditions match')"` | none, inline assertion | pass |
| 15B-01 | 2 module-boundary decision | all three | D-15B-1 recorded with one option id | checkpoint, file check | `grep -c "## D-15B-1. Where the blueprint, staleness, audit, and acceptance code lives" .planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` | none, file assertion | pass |
| 15B-01 | 3 blueprint-home and write-path decision | ACTIVITY-02, RELIABILITY-03 | D-15B-2 recorded with one option id, a named blueprint home, a named write path, and a named journal record type | checkpoint, file check | `grep -c "## D-15B-2. Where a blueprint lives and which write path records an acceptance" .planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` | none, file assertion | pass |
| 15B-02 | 1 five-gate tracer | ACTIVITY-02 | one drafted set and one cited blueprint travel parse, lint, review, blueprint, and runtime to an accepted write; the claim is False before the fifth gate | tracer, integration | `python tests/blueprint_roundtrip.py` | `check_thin_slice` | pass |
| 15B-02 | 1 shipped-loop additivity | ACTIVITY-02 | the new gate and the new gates array broke none of the shipped Phase 11 contracts | regression | `python tests/audit_authoring_roundtrip.py && python tests/audit_roundtrip.py && python schema_validate.py` | file `main` | pass |
| 15B-02 | 2 eight blueprint fields and the claim | ACTIVITY-02 | all eight ACTIVITY-02 fields checked when supplied, reported unverifiable when not, tolerance boundary inclusive on both sides | unit, edge | `python tests/blueprint_roundtrip.py` | `check_blueprint_fields`, `check_gate_edges`, `check_no_aggregate` | pass |
| 15B-03 | 1 fingerprint comparison and dispositions | RELIABILITY-03 | staleness derived from two supplied fingerprints, absent reads stale, four transcribed dispositions, report total and ordered | unit, edge | `python tests/blueprint_roundtrip.py` | `check_staleness_classifier` | pass |
| 15B-03 | 2 the hard block | RELIABILITY-03 | a stale dependent is refused by name, a matching disposition clears only its own row, a second change supersedes the review, no rebuild path exists | unit, fault-style | `python tests/blueprint_roundtrip.py` | `check_staleness_blocks` | pass |
| 15B-04 | 1 migration transitions | RELIABILITY-03 | exactly two paths may settle a migration, four named refusals, the 14B bypass guard still fires in the same run | unit, coupling | `python tests/graph_roundtrip.py && python schema_validate.py` | `check_migration_acceptance` | pass |
| 15B-04 | 2 write, authority, journal | RELIABILITY-03, ACTIVITY-02 | acceptance writes through the one path with the live policy re-read at accept time, staleness blocks first, refusals are journaled, journal diff is one line | integration, coupling | `python tests/blueprint_roundtrip.py && python tests/journal_roundtrip.py` | `check_accept_revision` | pass |
| 15B-05 | 1 audit-schema decision | ACTIVITY-02, RELIABILITY-03 | D-15B-3 recorded with one option id | checkpoint, file check | `grep -c "## D-15B-3. Where the course audit report shape lives" .planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md` | none, file assertion | pass |
| 15B-05 | 2 cited course audit | ACTIVITY-02, RELIABILITY-03 | every row names its vocabulary, no fourth is minted, a cross-vocabulary state is refused, no proportion appears | unit, schema coupling | `python tests/blueprint_roundtrip.py && python schema_validate.py && python tests/audit_coverage_roundtrip.py` | `check_course_audit`, `check_no_aggregate` | pass |
| 15B-06 | 1 proposal record | AGENT-03 | six required namings enforced by schema, half-open window, denominator always present, two attempts read sparse | unit, schema coupling | `python tests/blueprint_roundtrip.py && python schema_validate.py` | `check_evidence_proposal` | pass |
| 15B-06 | 2 recursive ban and edges | AGENT-03 | forbidden key refused at three nesting depths, window partitions, empty and single honest, objective identity normalized not folded, order stable | unit, edge | `python tests/blueprint_roundtrip.py` | `check_proposal_edges`, `check_no_aggregate` | pass |
| 15B-07 | 1 acceptance tracer | all three | all three Fixture sentences and every ROADMAP freeze-gate clause implemented by named scenario functions in one run | tracer, freeze gate | `python tests/acceptance_tracer.py` | `shipped_suite_check`, `scenario_five_gate_acceptance`, `scenario_fidelity_claim_ordering`, `scenario_staleness_blocks`, `scenario_migration_accept_and_reject`, `scenario_sparse_evidence_proposal`, `scenario_course_audit_provenance`, `scenario_journal_replay` | pass |
| 15B-07 | 2 human review | ACTIVITY-02, RELIABILITY-03, AGENT-03 | a human judges that refusals, findings, proposals, and audit rows are legible, and signs | manual, blocking checkpoint | none, see Manual-Only Verifications | waived |
| 15B-07 | 3 freeze or withhold | all three | three legs checked, freeze written or withheld by name, seven open items carried forward with owners | freeze gate | `python tests/acceptance_tracer.py && python itembank.py guard .` | none, file assertion | pass |

---

## Wave 0 Requirements

Confirmed by the planner (2026-08-15), with ownership assigned per plan and
task. All 15B test infrastructure is new direct-execution Python scripts beside
the existing `tests/*_roundtrip.py` set. No framework and no install step.

The research's Wave 0 Gaps listed three items and left the fixture file's
ownership open between `fixtures/corpus_14b.py` and a 15B-owned extension. The
planner resolved that: 15B creates its own `fixtures/corpus_15b.py` rather than
extending `corpus_14b.py`, because 14B and 15A both still own theirs and a
fourth phase appending to one file makes every later plan's `read_first` list
grow without bound. `corpus_15b.py` may call into `corpus_14b.py` where a
builder already exists.

- [x] `tests/blueprint_roundtrip.py`, created by plan 15B-02 Task 1 before
  `blueprint.py` exists, then extended by plans 15B-03 through 15B-06. This is
  the Wave 0 gap that unblocks plans 02 through 06; each of those tasks writes
  its own assertions before its own code.
- [x] `tests/acceptance_tracer.py`, created by plan 15B-07 Task 1, the
  freeze-gate tracer covering all three requirement Fixture sentences and every
  ROADMAP freeze-gate clause in one run, following
  `tests/four_subject_review.py`'s (15A) and `tests/three_domain_tracer.py`'s
  (14B) structure (`fail(msg)`, named `scenario_*()` functions, `main()`, a
  final `"TRACER: N passed, M skipped, 0 failed"` line).
- [ ] `fixtures/corpus_15b.py`, created by plan 15B-02 Task 1 with
  `build_blueprint_fixture`, `build_draft_set`, `build_golden_sidecar`, and
  `teardown`; extended by plan 15B-02 Task 2 with `build_item_facts`; by plan
  15B-03 with `build_staleness_fixture`, `edit_source`, and
  `build_reconciliation_case`; by plan 15B-04 with `build_acceptance_fixture`;
  by plan 15B-05 with `build_audit_signals`; by plan 15B-06 with
  `build_sparse_evidence` and `build_dense_evidence`; and by plan 15B-07 with
  `build_all_15b`. Fictional content only, fixed seed, no clock read.
- [ ] `schemas/blueprint.schema.json` and its `schema_validate.check_schema`
  coupling test, created by plan 15B-02 Task 1.
- [ ] `schemas/course_audit_report.schema.json` and its coupling test, created
  by plan 15B-05 Task 2 subject to the `D-15B-3` checkpoint.
- [ ] `schemas/evidence_proposal.schema.json` and its coupling test, created by
  plan 15B-06 Task 1.
- [ ] `tests/graph_roundtrip.py` gains `check_migration_acceptance`, added by
  plan 15B-04 Task 1 beside 14B-04's existing `check_migration`.

*(No pre-existing test infrastructure covers this phase's three requirements;
all listed gaps are new.)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Acceptance-quality review sign-off | ACTIVITY-02, RELIABILITY-03, AGENT-03 | The freeze gate requires a human reviewer to judge that acceptance, rejection, staleness dispositions, blueprint findings, sparse-evidence proposals, and audit-row provenance are legible and correct; an agent never self-certifies its own acceptance pipeline | `15B-07-PLAN.md` Task 2 `how-to-verify`, steps 1 through 9: read `15B-TRACER-REPORT.md`, run `python tests/acceptance_tracer.py`, read the blocked acceptance's refused journal entry, the `tool_forbidden` blueprint findings, the sparse-evidence proposal, the course audit report, and the accepted and rejected migrations, answer the questions grouped per step, confirm Phase 13.9 has been walked, and record everything in `15B-REVIEW.md` with a verdict and a signature |

---

## Validation Sign-Off

Resolved 2026-08-30 by plan 15B-07 Task 3.

- [x] All tasks have `<automated>` verify or Wave 0 dependencies. Fifteen of
      the sixteen rows carry an automated command; the sixteenth is the manual
      review, which has its own table.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
      Only one row in the whole map lacks one.
- [x] Wave 0 covers all MISSING references. Both Wave 0 test files shipped,
      and `fixtures/corpus_15b.py` shipped with every builder the plans named.
- [x] No watch-mode flags. None was added; the suite is direct-execution
      scripts as it was.
- [x] Feedback latency measured, not asserted. 1 second, recorded above with
      the machine and Python version, and deliberately not compared against a
      target.
- [x] `nyquist_compliant: true` set in frontmatter. Every task row carries an
      automated command except one, so no three consecutive tasks lack one.
- [ ] **Human sign-off on the acceptance-quality review.** Left unchecked.
      This box is not one the planner wrote; it is added here because ticking
      the six above without it would let the file read as though the phase
      closed cleanly. `15B-REVIEW.md` was written by an agent under Weibao's
      waiver, not by Weibao, and this is the fifth consecutive phase in that
      state. See the `waived` row in the map above.

**Approval:** the six automated legs pass and the freeze is written.
`15B-FREEZE.md` opens `## Frozen at 15B`. The human review leg is waived, not
met, and anything relying on this phase should read `15B-REVIEW.md`'s
Provenance section first.
