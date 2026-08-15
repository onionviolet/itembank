---
phase: 15B
slug: quality-blueprint-acceptance
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-15
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
| **Estimated runtime** | Unknown for the new 15B files. Do not record a figure until one has been measured on this machine. |

---

## Sampling Rate

- **After every task commit:** the quick run command for that task's specific new or changed test file.
- **After every plan wave:** the 15B subset plus the shipped-anchor spot check `python tests/scoring_roundtrip.py && python tests/evidence_roundtrip.py` (the anchor-check discipline 14A-01 Task 3 established), plus `python tests/authoring_roundtrip.py` if it exists, because 15B extends the shipped Phase 11 authoring gate composition.
- **Before `/gsd-verify-work`:** full suite green, the lesson-plus-practice acceptance tracer green, and `python itembank.py guard .` reporting `0 offending files`.
- **Freeze gate:** no 15B freeze record is written on a red acceptance tracer (mirrors 14A-04 Task 4, 14B-06, and 15A-06).
- **Max feedback latency:** to be measured, not asserted.

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

Populated by the planner at plan time. The final 15B plan's freeze-gate task
updates the Status column to `pass` or to the reason it is not, and replaces
the Estimated runtime placeholder above with a measured figure.

`Status` values: `planned` means the row is authored and the task has not run
yet.

| Plan | Task | Req ID | Behavior | Test Type | Automated Command | Assertion function | Status |
|------|------|--------|----------|-----------|-------------------|--------------------|--------|
| (planner fills) | | | | | | | |

---

## Wave 0 Requirements

Seeded from `15B-RESEARCH.md` Wave 0 Gaps; the planner confirms ownership per
plan and task.

- [ ] `tests/acceptance_tracer.py`, the freeze-gate tracer covering all three
  requirement rows in one run, following `tests/four_subject_review.py`'s
  (15A) and `tests/three_domain_tracer.py`'s (14B) structure (`fail(msg)`,
  named `scenario_*()` functions, `main()`, a final
  `"TRACER: N passed, M skipped, 0 failed"` line).
- [ ] A synthetic blueprint document plus a drafted question set plus a lesson
  stand-in, added to `fixtures/corpus_14b.py` or a 15B-owned extension of it,
  fictional content only, fixed seed.
- [ ] `schemas/blueprint.schema.json` and its `schema_validate.check_schema`
  coupling test, following every prior new-schema plan's precedent.

*(No pre-existing test infrastructure covers this phase's three requirements;
all listed gaps are new.)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Acceptance-quality review sign-off | ACTIVITY-02, RELIABILITY-03 | The freeze gate requires a human reviewer to judge that acceptance, rejection, and staleness dispositions are legible and correct; an agent never self-certifies its own acceptance pipeline | The final 15B plan's review task defines the steps: run the tracer, read the course audit report and the journaled acceptance entries, answer the judgment questions, and record the verdict with a signature in a `15B-REVIEW.md` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency measured, not asserted
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
