---
phase: 7
slug: selection-engine
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-08
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — direct script execution, stdlib only |
| **Config file** | none |
| **Quick run command** | `python tests/selection_roundtrip.py` |
| **Full suite command** | `for f in tests/*_roundtrip.py; do python "$f" || exit 1; done` |
| **Estimated runtime** | ~8 seconds quick, ~70 seconds full |

---

## Sampling Rate

- **After every task commit:** Run `python tests/selection_roundtrip.py`
- **After every plan wave:** Run the full suite
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 70 seconds

---

## Per-Task Verification Map

*Filled by the planner. One row per task, mapped to a SEL-xx requirement.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| | | | | | | | | | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/selection_roundtrip.py` — new file, stubs for SEL-01..SEL-05
- [ ] `fixtures/selection_bank.md` — **new, and load-bearing.** `fixtures/sample_bank.md` holds
      6 items with unnamespaced objectives and no `[PAIR:]` tags, which is too small to exercise
      a cooldown of 20 or to make four selection modes visibly differ. The new fixture needs
      roughly 30 items across at least 4 namespaced objectives, a spread of difficulties and item
      types, at least two `[PAIR:]` groups, and at least one `[PREREQ:]` chain
- [ ] `fixtures/selection_evidence.jsonl` — a synthetic evidence history so cooldown, remediation
      selection, and the runner-up trace can be tested without sitting a real session

No framework install — the project forbids one.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The trace reads as plain English to a human, not as rule ids | SEL-05 | "In plain terms" is a readability judgment; a test can assert the fields are present but not that the sentence is legible | Run `itembank select fixtures/selection_bank.md --mode practice --explain` and read the output; every block must name the chosen item, the reason, the runner-up, and why the runner-up lost, without jargon |
| The four modes' compositions differ in a way that *matches each mode's purpose* | SEL-02 | A test can assert the four sets differ; whether the difference is the right one is a design judgment | Generate all four from the same fixture and seed, print the objective/difficulty distribution of each, and confirm diagnostic spreads, remediation concentrates on failures, and exam ignores history |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 70s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
