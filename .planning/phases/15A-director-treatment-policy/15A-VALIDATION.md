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
| **Quick run command** | `python tests/director_roundtrip.py` (or the specific new test file a task targets) |
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

Populated by the planner at plan time (2026-08-14). The final 15A plan updates
the Status column and replaces the Estimated runtime placeholder above with a
measured figure.

| Plan | Task | Req ID | Behavior | Test Type | Automated Command | Assertion function | Status |
|------|------|--------|----------|-----------|-------------------|--------------------|--------|

---

## Wave 0 Requirements

To be confirmed by the planner. Expected: new direct-execution test files
beside the existing `tests/*_roundtrip.py` set; no framework install.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Four-subject recommendation review sign-off | TREAT-01, AGENT-01 | The freeze gate requires a human review of the recommendation quality across four synthetic subjects; an agent never self-certifies it | Filled by the planner from the freeze-gate plan |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency measured, not asserted
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
