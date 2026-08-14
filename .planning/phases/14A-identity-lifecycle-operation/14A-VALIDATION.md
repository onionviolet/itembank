---
phase: 14A
slug: identity-lifecycle-operation
# status lifecycle: draft (seeded by plan-phase) -> validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-14
---

# Phase 14A — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib scripts (no pytest); each `tests/*_roundtrip.py` is a direct-execution script using the repo's `fail(msg)` convention, exit 0 on pass |
| **Config file** | none (no runner config; CI invokes scripts directly, see `.github/workflows/ci.yml`) |
| **Quick run command** | `python tests/identity_roundtrip.py` (per-plan: the roundtrip script owned by the plan being executed) |
| **Full suite command** | `for t in tests/*_roundtrip.py; do python "$t" || exit 1; done` plus `python tests/file_fault_tracer.py` once 14A-04 lands |
| **Estimated runtime** | ~60 seconds for the affected scripts; full roundtrip sweep several minutes |

---

## Sampling Rate

- **After every task commit:** Run the owning plan's roundtrip script (`python tests/identity_roundtrip.py`, `python tests/journal_roundtrip.py`, or `python tests/operations_roundtrip.py`)
- **After every plan wave:** Run all three 14A roundtrip scripts plus the shipped byte-compatibility anchors `python tests/scoring_roundtrip.py`, `python tests/evidence_roundtrip.py`, `python tests/audit_writer_roundtrip.py`, `python tests/durability_roundtrip.py`
- **Before `/gsd-verify-work`:** `python tests/file_fault_tracer.py` green end to end (the phase freeze gate), full roundtrip sweep green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (filled by planner from 14A-01..04 PLAN.md tasks) | | | FILE-01/02/03, ID-01/02, RIGHTS-01, RELIABILITY-01 | | denied paths inventoried, never mutated; conflicts refused, never overwritten | integration | per-plan roundtrip script | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/identity_roundtrip.py` — stubs for ID-01, ID-02 (14A-01)
- [ ] `fixtures/` synthetic multi-root tree — three roots, nested folders, symlink cycle (with named Windows fallback), permission-denied pocket, duplicate-fingerprint pair; synthetic content only (`itembank guard` clean)
- [ ] `tests/journal_roundtrip.py` — stubs for RELIABILITY-01, FILE-01 (14A-02)
- [ ] `tests/operations_roundtrip.py` — stubs for FILE-03, RIGHTS-01 (14A-03)

*No framework install: existing stdlib-script infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| D-12.6-10 budget numbers reviewed as plausible | RELIABILITY-01 | Budgets are measured and recorded, not asserted; a human reads the tracer report numbers | Open the 14A-04 tracer report artifact in the phase directory; confirm 1k/10k corpus numbers are recorded with units and denominators |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
