---
phase: 15A
slug: director-treatment-policy
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-14
---

# Phase 15A Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `15A-RESEARCH.md` section "Validation Architecture". The planner
> fills the Per-Task Verification Map once plan and task IDs exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None. Direct-execution Python scripts, this project's established convention (not pytest, not unittest) |
| **Config file** | none. See the `tests/*_roundtrip.py` convention |
| **Quick run command** | `python tests/director_roundtrip.py` (the file plans 15A-01 through 15A-05 all extend; plan 15A-06 targets `python tests/four_subject_review.py`) |
| **Full suite command** | `for t in tests/*.py; do python "$t" || exit 1; done` |
| **Estimated runtime** | Unknown for the new 15A files. Do not record a figure until one has been measured on this machine. |

---

## Sampling Rate

- **After every task commit:** the quick run command for that task's specific new or changed test file.
- **After every plan wave:** the 15A subset plus the shipped-anchor spot check `python tests/scoring_roundtrip.py && python tests/evidence_roundtrip.py` (the anchor-check discipline 14A-01 Task 3 established).
- **Before `/gsd-verify-work`:** full suite green, the four-subject recommendation review tracer green, and `python itembank.py guard .` reporting `0 offending files`.
- **Freeze gate:** no 15A freeze record is written on a red four-subject review tracer (mirrors 14A-04 Task 4 and 14B-06).
- **Max feedback latency:** to be measured, not asserted.

---

## Per-Task Verification Map

Populated by the planner at plan time (2026-08-15). Plan 15A-06 Task 3 updates
the Status column to `pass` or to the reason it is not, and replaces the
Estimated runtime placeholder above with a measured figure.

`Status` values: `planned` means the row is authored and the task has not run
yet. Every row below carries an automated command; there are no manual-only
task rows, and the one manual verification is the freeze-gate review recorded
in its own table further down.

| Plan | Task | Req ID | Behavior | Test Type | Automated Command | Assertion function | Status |
|------|------|--------|----------|-----------|-------------------|--------------------|--------|
| 15A-01 | 1 preconditions | all six | 14A and 14B landed with the constants 15A was planned against, or halt by name | precondition check | `python -c "import identity, journal, graph, course; assert len(graph.TREATMENT_KINDS)==11 and len(graph.BINDING_STATES)==5 and len(journal.ENTRY_KEYS)==22 and 'agent_operation' not in journal.RECORD_TYPES; print('15A preconditions match')"` | none, inline assertion | planned |
| 15A-01 | 2 wire-boundary decision | AGENT-02 | D-15A-1 recorded with one option id | checkpoint, file check | `grep -c "## D-15A-1. The recommendation wire boundary" .planning/phases/15A-director-treatment-policy/15A-DECISIONS.md` | none, file assertion | planned |
| 15A-01 | 3 egress-location decision | RIGHTS-02, RELIABILITY-02 | D-15A-2 recorded with one option id | checkpoint, file check | `grep -c "## D-15A-2. Where the egress record lives" .planning/phases/15A-director-treatment-policy/15A-DECISIONS.md` | none, file assertion | planned |
| 15A-01 | 4 end-to-end tracer | TREAT-01, RELIABILITY-02, AGENT-02 | one objective from intent through adapter, validation, live rights check, bind, and journaled egress | tracer, integration | `python tests/director_roundtrip.py` | `check_thin_slice` | planned |
| 15A-01 | 4 additivity | AGENT-02 | the fourth adapter operation broke none of the three shipped ones | regression | `python tests/model_adapter_roundtrip.py` | file `main` | planned |
| 15A-02 | 1 closed vocabulary and tie-break | TREAT-01 | eleven kinds accepted, a twelfth refused, ties broken by vocabulary order, no float anywhere | unit | `python tests/director_roundtrip.py` | `check_treatment_vocabulary` | planned |
| 15A-02 | 2 direct reading and the gap report | TREAT-01 | direct reading is a complete result, the untreated report reads bindings not proposals, three outcomes and no fourth | unit, integration | `python tests/director_roundtrip.py` | `check_direct_reading_complete` | planned |
| 15A-02 | 3 empty, ordering, stability | TREAT-01 | zero objectives open no operation, order is the caller's, two passes are equal under `parity_view` | unit, edge | `python tests/director_roundtrip.py` | `check_recommendation_edges` | planned |
| 15A-03 | 1 locator and the six rules | TREAT-02 | NFC and line-ending normalization with no case folding, six ordered rules, covered reachable only through a resolved locator | unit | `python tests/director_roundtrip.py` | `check_coverage_classifier` | planned |
| 15A-03 | 2 five states and the decoy | TREAT-02 | one claim per state from real fixture data, the heading-similarity decoy reads unknown, duplicates refused, order stable | unit, fixture | `python tests/director_roundtrip.py` | `check_coverage_states` | planned |
| 15A-04 | 1 approved spans | RIGHTS-02 | spans only from sources whose right reads granted in the live registry, omissions named, caps disclosed | unit, integration | `python tests/director_roundtrip.py` | `check_approved_spans` | planned |
| 15A-04 | 2 autonomy policy | AGENT-02, RIGHTS-02 | the policy is settings-side, an over-declaring agent is refused and never narrowed, a fresh install grants nothing | unit, schema coupling | `python tests/director_roundtrip.py && python tests/config_roundtrip.py` | `check_autonomy_policy`, `test_agent_policy_enum_and_default` | planned |
| 15A-04 | 3 egress record | RIGHTS-02 | the record names every span and omission exactly, carries no secret, sorts stably, and is present even when nothing was sent | unit, integration | `python tests/director_roundtrip.py` | `check_egress_record` | planned |
| 15A-05 | 1 thirteen phases and replay | AGENT-01 | frozen exact-ASCII phase tokens, replay from the journal alone, an empty journal reads incomplete | unit, integration | `python tests/director_roundtrip.py` | `check_protocol_replay` | planned |
| 15A-05 | 2 interruption, resume, reverse | RELIABILITY-02 | a kill at each of the thirteen phases resumes or reverses from the journal alone through `journal.undo` | fault injection | `python tests/director_roundtrip.py` | `check_resume_and_reverse` | planned |
| 15A-05 | 3 journal coupling and agent-disabled loop | RELIABILITY-02, AGENT-01 | the `agent_operation` record type has a coupling test beside the journal, and the core loop runs with every profile removed | coupling, regression | `python tests/journal_roundtrip.py && python tests/director_roundtrip.py` | `check_agent_operation_record`, `check_protocol_edges` | planned |
| 15A-06 | 1 four-subject tracer | all six | all six Fixture sentences implemented by named scenario functions in one run | tracer, freeze gate | `python tests/four_subject_review.py` | `scenario_four_subject_recommendation`, `scenario_direct_reading_and_untreated`, `scenario_coverage_states`, `scenario_egress_exactness`, `scenario_backend_parity`, `scenario_backend_loss`, `scenario_protocol_replay` | planned |
| 15A-06 | 2 human review | TREAT-01, AGENT-01 | a human judges recommendation quality across four subjects and signs | manual, blocking checkpoint | none, see Manual-Only Verifications | planned |
| 15A-06 | 3 freeze or withhold | all six | three legs checked, freeze written or withheld by name | freeze gate | `python tests/four_subject_review.py && python itembank.py guard .` | none, file assertion | planned |

---

## Wave 0 Requirements

Confirmed by the planner. All 15A test infrastructure is new direct-execution
Python scripts beside the existing `tests/*_roundtrip.py` set. No framework and
no install step.

- [ ] `tests/director_roundtrip.py`, created by plan 15A-01 Task 4 before
  `director.py` exists, then extended by every later plan. This is the Wave 0
  gap that unblocks plans 01 through 05; each of those tasks writes its own
  assertions before its own code.
- [ ] `tests/four_subject_review.py`, created by plan 15A-06 Task 1, the
  freeze-gate tracer covering all six requirement Fixture sentences.
- [ ] `fixtures/mock_backends.py`, created by plan 15A-01 Task 4, the one
  shared deterministic candidate builder both mock transports call.
- [ ] `tests/journal_roundtrip.py` gains `check_agent_operation_record`, added
  by plan 15A-05 Task 3. Plan 15A-05 owns this addition, answering the
  ownership question `15A-RESEARCH.md`'s Wave 0 Gaps left open.
- [ ] `fixtures/corpus_14b.py` gains `build_recommendation_fixture`,
  `build_coverage_fixture`, `build_rights_matrix_fixture`,
  `build_interrupted_operation`, `build_four_subjects`, and `build_all_15a`,
  added by plans 15A-02 through 15A-06 respectively.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Four-subject recommendation review sign-off | TREAT-01, AGENT-01 | The freeze gate requires a human review of the recommendation quality across four synthetic subjects; an agent never self-certifies it | `15A-06-PLAN.md` Task 2 `how-to-verify`, steps 1 through 7: read `15A-TRACER-REPORT.md`, run the tracer, print the four subjects' recommendations, answer the five judgment questions per subject, read the untreated and direct-reading cases specifically, check that Phase 13.9 has been walked, and record everything in `15A-REVIEW.md` with a verdict and a signature |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency measured, not asserted
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
