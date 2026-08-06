---
phase: 1
slug: evidence-spine-protocol-foundation
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-06
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `01-RESEARCH.md` § Validation Architecture. Task IDs are filled in by
> `/gsd-validate-phase` once PLAN.md task numbering exists.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — standalone Python scripts run directly. Convention is `tests/*_roundtrip.py`, each with a `fail(msg)` helper printing `"FAIL: " + msg` and exiting 1 (`tests/scoring_roundtrip.py:21-23`) |
| **Config file** | none — no pytest.ini, no test-runner dependency, by the stdlib-only constraint |
| **Quick run command** | `python tests/evidence_roundtrip.py && python tests/protocol_roundtrip.py` |
| **Full suite command** | `for t in tests/*.py; do python "$t" || exit 1; done` (identical to `.github/workflows/ci.yml:40-43`) |
| **Estimated runtime** | ~2 seconds (pure Python, temp-file I/O only; existing roundtrips run sub-second) |

---

## Sampling Rate

- **After every task commit:** Run `python tests/evidence_roundtrip.py && python tests/protocol_roundtrip.py`
- **After every plan wave:** Run `for t in tests/*.py; do python "$t" || exit 1; done`
- **Before `/gsd-verify-work`:** Full suite must be green, AND the Windows append-durability
  spike result (RESEARCH.md Open Question 1) must be recorded in the plan
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

Task IDs are `TBD` until PLAN.md files exist; `/gsd-validate-phase` resolves them. Requirement,
test type, and command are already fixed by RESEARCH.md § Validation Architecture.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | EVID-01, EVID-02 | — | N/A | unit | `python tests/evidence_roundtrip.py` (`test_identity_survives_edit`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | EVID-03 | — | N/A | unit | `python tests/evidence_roundtrip.py` (`test_renders_match_log`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | EVID-04 | — | N/A | unit | `python tests/evidence_roundtrip.py` (`test_objective_query`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | EVID-05 | — | N/A | unit | `python tests/evidence_roundtrip.py` (`test_retraction`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | EVID-06 | T-1-03 | Migration inputs scoped to well-known relative locations, not an arbitrary path argument | integration | `python tests/evidence_roundtrip.py` (`test_migration_reconciliation`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | EVID-07 | — | N/A | unit | `python tests/protocol_roundtrip.py` (`test_event_schema_fields`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | EVID-08 | — | N/A | unit | `python tests/evidence_roundtrip.py` (`test_mode_recorded`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | PROTO-01 | — | N/A | unit | `python tests/protocol_roundtrip.py` (`test_schema_versions_present`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | PROTO-02 | — | N/A | unit + existing CI step | `python tests/protocol_roundtrip.py`; existing "Broken fixture is caught" step (`ci.yml:19-30`) stays green unchanged | ❌ W0 (new test); ✅ (existing CI half) | ⬜ pending |
| TBD | TBD | TBD | PROTO-03 | — | N/A | unit | `python tests/evidence_roundtrip.py` (`test_duplicate_submit_dedupes`, covering the `short`-item key fallback) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | PROTO-04 | — | N/A | CI step | new `.github/workflows/ci.yml` step running the minimal schema validator | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | PROTO-05 | — | N/A | smoke | `python tests/protocol_roundtrip.py` (`test_schema_command_output`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | (all reads) | T-1-01, T-1-02 | Malformed/truncated JSONL line is skipped and reported, never crashes the reader (D-09) | unit | `python tests/evidence_roundtrip.py` (malformed-line case) | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/evidence_roundtrip.py` — stubs for EVID-01 … EVID-06, EVID-08, PROTO-03
- [ ] `tests/protocol_roundtrip.py` — stubs for EVID-07, PROTO-01, PROTO-02, PROTO-05
- [ ] `fixtures/legacy_attempts/*.md`, `fixtures/legacy_session.json`, `fixtures/legacy_daily_log.md`
      — synthetic legacy-shaped data for the EVID-06 migration reconciliation test. None exist
      today (`fixtures/` holds only `sample_bank.md`, `broken_bank.md`, `sample_plan.md`,
      `sample_lanes.md`, and two generated HTML outputs)
- [ ] New CI step in `.github/workflows/ci.yml` — covers PROTO-04
- [ ] Windows append-durability spike — a dedicated documented experiment, not a conventional
      unit test; its **result** must be recorded before evidence-writing tasks proceed
      (RESEARCH.md Open Question 1)
- [ ] Framework install: **none** — the existing `python tests/*.py` convention needs no new
      tooling, only new files following it

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Windows append-write durability under crash-mid-write | EVID-03 (log integrity) | Requires inducing a real process kill mid-append on the target Windows 11 machine; not reproducible inside a same-process unit test, and CI runs `ubuntu-latest` (POSIX), so CI cannot cover the Windows path at all | Run the spike script from the plan's spike task on the target machine: concurrent appenders + forced kill; confirm no interleaved or torn lines survive the reader's skip-and-report path |
| `itembank schema` output is usable by an agent with no repository context | PROTO-05 | "Self-contained and comprehensible to a fresh agent" is a judgment about sufficiency, not a string match; the automated smoke test can only confirm the output parses and carries the version fields | Paste `itembank schema` output alone into a fresh model context and ask it to author one valid item of each type; it must succeed without reading the repo |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] Windows durability spike result recorded in PLAN.md
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
