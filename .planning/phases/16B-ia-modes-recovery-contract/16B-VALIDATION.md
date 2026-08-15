---
phase: 16B
slug: ia-modes-recovery-contract
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-15
---

# Phase 16B Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `16B-RESEARCH.md` section "Validation Architecture". The
> Per-Task Verification Map below is filled by the planner against the 16B
> plans; the final 16B plan finalizes the Status column, replaces the
> Estimated runtime placeholder with a measured figure, and resolves the
> sign-off boxes, the same closure pattern 16A-10 Task 3 set.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None. Direct-execution Python scripts, this project's established convention (not pytest, not unittest) |
| **Config file** | none. See the `tests/*_roundtrip.py` and `tests/*_tracer.py` convention; every test file defines its own local `fail(msg)` helper |
| **Quick run command** | `python tests/<new_test_file>.py` for whichever single new or extended test file the task adds |
| **Full suite command** | `for t in tests/*.py; do python "$t" || exit 1; done` |
| **Estimated runtime** | Unknown for the new 16B files. Do not record a figure until one has been measured on this machine. The final 16B plan replaces this cell with the measured full-suite figure and names the machine and Python version. |

---

## Sampling Rate

- **After every task commit:** the quick run command for that task's specific
  new or changed test file, plus `python itembank.py guard .` on any task that
  touches `fixtures/`.
- **After every plan wave:** the full suite command.
- **Before `/gsd-verify-work`:** full suite green, the loop-interruption
  storyboard suite green, the route-parity check green, and
  `python itembank.py guard .` reporting `0 offending files`.
- **Route parity, after every task that touches `surfaces/daemon.py`:**
  re-run the shipped route/CLI/parity coupling test so a new IA route never
  lands in one of the four parallel route structures without the others.
- **Freeze gate:** no 16B freeze record is written on a red storyboard or
  interruption suite, a missing or rejecting human review, or an unresolved
  precondition divergence from the 14A or 16A plan text (mirrors 14A-04
  Task 4, 14B-06, 15A-06, 15B-07, and 16A-10).
- **Max feedback latency:** to be measured, not asserted.

---

## Phase Requirements -> Test Map

Seeded from `16B-RESEARCH.md` (FLOW-01, FLOW-02, APP-01, APP-02, APP-03).
Expanded into the Per-Task Verification Map below by the planner.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (filled by planner) | | | | | | | | | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] (filled by planner from 16B-RESEARCH.md Validation Architecture)

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| (filled by planner; the human contract-legibility review of the freeze record is expected here) | | | |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency measured, not asserted
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
