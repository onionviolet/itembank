# Phase 11 — Closed Authoring Loop & Curriculum Auditor — Verification

**Phase:** 11-closed-authoring-loop-curriculum-auditor
**Branch:** gsd/phase-11-auditor (worktree `.phase11-wt`, based on `5aab199`)
**Status:** EXECUTED — all five plans complete; verification evidence below
**Executed:** 2026-08-11

## Plan Gates

| Plan | Wave | Gate command | Result |
|---|---|---|---|
| 11-01 | 1 | `python tests/audit_roundtrip.py --case tracer` | PASS |
| 11-02 | 2 | `python tests/audit_roundtrip.py --case schemas` (+ tracer green) | PASS |
| 11-03 | 3 | `python tests/audit_coverage_roundtrip.py` | PASS |
| 11-04 | 3 | `python tests/audit_quality_roundtrip.py`; `python tests/audit_authoring_roundtrip.py` | PASS |
| 11-05 | 4 | `python tests/model_adapter_roundtrip.py`; `python tests/audit_cli_roundtrip.py`; `python tests/audit_writer_roundtrip.py` | PASS |

## Per-Plan Verification Detail

### 11-01 — closed authoring loop tracer (AUTH-01/02/03, AUDIT-06/07/08)
- Repository-blind spy callable: malformed-first (out-of-scope) / clean-second; structured versioned scope findings returned as the retry input.
- Both gates run over the complete composed candidate before the writer; one atomic content-addressed shadow write; duplicate-run idempotency (zero regeneration, zero mutation); one-step undo restores exact before bytes; stale undo refuses with no force path; out-of-scope exhaustion makes zero writer calls; report_only never writes.
- AUTH-03 allowlist asserted over the serialized payloads (no repo paths, bank text, un-cited source prose, credentials).
- `python -m py_compile` of all five new modules: PASS.

### 11-02 — strict public schemas (AUTH-01/02/03, AUDIT-06/07/08)
- Five strict versioned JSON Schemas (authoring_request, normalized_document, quality_finding, audit_report, write_manifest) using only the `schema_validate` SUPPORTED keyword subset; `check_schema` refuses unsupported keywords.
- Runtime-version parity (`schema_version` == `x-itembank-version`); extra-property and missing-required rejections; stable ordering under reordered input; tracer case stays green.

### 11-03 — citation-first curriculum audit (AUDIT-01/02/03/04)
- Markdown/text normalization: deterministic spans with heading/list/body objectives, byte-exact reconstruction, invalid-UTF-8 and oversize explicit failures.
- Coverage engine: covered/partial/conflicting/gap/unknown states with fail-closed dual citations; confidence never upgrades; singleton/partial/conflicting boundaries; stale fingerprints never covered and the report marks stale; reordered input serializes identically.
- 18-case PDF/DOCX gold matrix (`fixtures/audit/locator_fidelity_cases.py`): deterministic bytes, literal gold sha256, repeated explicit unsupported/lossy results with no fabricated locators and unchanged bytes/timestamps.
- Material handoff: gap materials inert; obtained material creates only a separate cited request; weak-objective signals reorder without inventing; author/writer structurally unreachable.

### 11-04 — quality profile, retry state machine, autonomy (AUTH-01/02/03, AUDIT-05/06/07/09)
- Exact four-detector boundaries (skew ≥12 MC, block only >40%, equality passes; Jaccard ≥0.85 with six-token floor; unique contiguous ≥3-token leak run; rationale must state the would-be condition) with measured evidence, no aggregate score, deterministic ordering, identity/fingerprint immutability.
- Retry: scope-before-lint, structured lint/quality findings, exact cap + last-attempt success, no clean prefix in a dirty batch, malformed/empty/null retries, stable finding order, prompt-injection resistance (injected mode/tools/caps/output fields and instruction-like item text cannot change authority).
- Stateful: duplicate idempotency, interruption visibility (prepared manifest, untouched bank), parallel single-mutation, byte-identical gates/diffs across the three modes, exact write-id approval over a durable pending proposal, full-autonomy opt-in + caps before generation, every-exit volume (proposed/completed/rejected/retried/written + per-objective), stale-preflight writer refusal.

### 11-05 — configured adapter + Git/shadow writer + public undo (AUTH-01/02/03, AUDIT-05/06/07/08/09)
- Blocking preconditions recorded as satisfied: `python tests/model_adapter_roundtrip.py` exits 0; `11-AI-SPEC.md` status APPROVED covering author-operation scope, structured retries, prompt-injection/untrusted-output cases, volume caps, model-unavailable behavior.
- Additive `author` operation on `model_adapter.invoke`; Phase 8 suite stays green.
- No-DI subprocess proof: `python itembank.py audit author ...` resolves the configured fake hosted profile from `itembank.json` via `surfaces.cli.main` -> `model_adapter.invoke`, retries from structured scope findings, writes exactly one clean gated unit, and the recorded adapter requests carry only the allowlist (repository-blind).
- Writer: per-bank OS lock (msvcrt/fcntl, bounded busy); tracked+clean Git backend (one machine-authored commit per unit + committed manifest, recorded commit hash); shadow backend with `before_exists: false` report artifacts; dirty Git falls back to shadow; undo routes by manifest (git revert with dirty/conflict refusal; shadow after-fingerprint guarded restore, no force path); prepared journal visible on interrupted git commit; duplicate idempotency; parallel single-mutation.
- D-15 checkpoint 11-05-02 resolved: **proceed** (per the phase execution instruction; the locked contract was implemented without reopening the design).
- Public CLI: `itembank audit source|coverage|material|author|undo` registered; modes case proves report_only / exact write-id approval / full capped volume through the registered command.

## Full-Suite Result

`tmp_run_suite.py` (corrected runner; every `tests/*.py` in the worktree):

- **33 of 37 pass**, including all eight `audit_*` suites, `model_adapter_roundtrip`, `protocol_roundtrip`, `serve_roundtrip`, `scoring_roundtrip`, `evidence_roundtrip`, `packaging_shell_roundtrip`, `packaging_roundtrip` (pyz stage fix confirmed — the remaining packaging failure is the unbuilt Rust sidecar, a pre-existing environment prerequisite).
- 4 failures are **environmental / concurrent, not regressions from this branch**:
  1. `model_surface_roundtrip.py` — fails at baseline `5aab199` too: the committed test calls `surfaces.session.do_rubric_review` which the committed `surfaces/session.py` lacks (the Phase 8 chat's uncommitted main-tree work owns that function; this branch never touches those files).
  2. `daemon_roundtrip.py` — the hostile-bank-field check snapshots `/tmp` and fails on unrelated directories created concurrently (reasonix task dirs, other sessions' `work-*` dirs); passes under a quiet environment.
  3. `day_roundtrip.py` — HTTP timeout under parallel load; passes standalone.
  4. `packaging_roundtrip.py` — requires `dist/itembank-sidecar-onedir` built by the Phase 13 Rust/Tauri workstream (`scripts/build_shell.ps1`); not available in this checkout.

## Constraints Honored

- No `surfaces/daemon.py` route, frontend asset, ORM migration, package dependency, PDF/DOCX adapter, or `COVERAGE.md` created.
- Original source/syllabus/bank fixtures never modified; every fixture copied to a temp directory before use.
- One atomic commit per plan: `feat(11-01)` 33cebe4, `test(11-02)` 7e4d6f1, `feat(11-03)` d97f56d, `feat(11-04)` 2ece4a4, `feat(11-05)` 7df425d.
