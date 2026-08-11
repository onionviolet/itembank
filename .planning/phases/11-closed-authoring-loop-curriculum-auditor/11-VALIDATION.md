---
phase: 11
slug: closed-authoring-loop-curriculum-auditor
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-08
updated: 2026-08-08
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for exactly five plans and twelve tasks. Test files marked W0 are created by the task that first needs them; no task relies on a manual-only gate for a behavioral requirement.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Standalone Python standard-library roundtrip scripts with plain `fail()` assertions |
| **Config file** | none |
| **Quick run command** | `python tests/audit_roundtrip.py --case tracer` |
| **Full suite command** | `Get-ChildItem tests -Filter '*_roundtrip.py' \| Sort-Object Name \| ForEach-Object { python $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }` |
| **Feedback target** | Every focused command completes in under 60 seconds |

## Sampling Rate

- **After every implementation task:** Run that task's exact `<automated>` command from the map below.
- **After Wave 1:** `python tests/audit_roundtrip.py --case tracer`
- **After Wave 2:** `python tests/audit_roundtrip.py`
- **After Wave 3:** run `python tests/audit_coverage_roundtrip.py`, `python tests/audit_quality_roundtrip.py`, and `python tests/audit_authoring_roundtrip.py`.
- **Phase 8 independence:** Plans 11-01 through 11-04 have no Phase 8 artifact precondition; they execute against strict public contracts and injected deterministic fakes while still conforming to approved `11-AI-SPEC.md` guardrails.
- **Before Wave 4 Task 11-05-01:** fail closed unless the Phase 8 artifacts/tests are present and green and `.planning/phases/11-closed-authoring-loop-curriculum-auditor/11-AI-SPEC.md`, or an exact equivalent path explicitly recorded below, exists with approved status and covers author-operation scope, structured retries, prompt-injection/untrusted-output cases, volume caps, and model-unavailable behavior.
- **After Wave 4:** run `python tests/model_adapter_roundtrip.py`, `python tests/audit_cli_roundtrip.py`, and `python tests/audit_writer_roundtrip.py`.
- **Before `$gsd-verify-work`:** Run the full suite command and require every script to exit 0.

## Five-Plan Verification Map

| Plan | Wave | Tasks | Requirements exercised | Plan gate |
|------|------|-------|------------------------|-----------|
| 11-01 | 1 | 1 | AUTH-01, AUTH-02, AUTH-03, AUDIT-06, AUDIT-07, AUDIT-08 | `python tests/audit_roundtrip.py --case tracer` |
| 11-02 | 2 | 2 | AUTH-01, AUTH-02, AUTH-03, AUDIT-06, AUDIT-07, AUDIT-08 | `python tests/audit_roundtrip.py --case schemas` |
| 11-03 | 3 | 3 | AUDIT-01, AUDIT-02, AUDIT-03, AUDIT-04 | `python tests/audit_coverage_roundtrip.py` |
| 11-04 | 3 | 3 | AUTH-01, AUTH-02, AUTH-03, AUDIT-05, AUDIT-06, AUDIT-07, AUDIT-09 | `python tests/audit_quality_roundtrip.py`; `python tests/audit_authoring_roundtrip.py` |
| 11-05 | 4 | 3 (including one blocking decision checkpoint) | AUTH-01, AUTH-02, AUTH-03, AUDIT-05, AUDIT-06, AUDIT-07, AUDIT-08, AUDIT-09 | `python tests/model_adapter_roundtrip.py`; `python tests/audit_cli_roundtrip.py`; `python tests/audit_writer_roundtrip.py` |

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure behavior | Automated command | File exists now | Status |
|---------|------|------|-------------|------------|-----------------|-------------------|-----------------|--------|
| 11-01-01 | 01 | 1 | AUTH-01, AUTH-02, AUTH-03, AUDIT-06, AUDIT-07, AUDIT-08 | T-11-01..05 | One repository-blind malformed-first/clean-second tracer performs full preflight, one shadow write, idempotent replay, and undo; scope mismatch makes zero writer calls | `python tests/audit_roundtrip.py --case tracer` | ❌ W0 | ⬜ pending |
| 11-02-01 | 02 | 2 | AUTH-02, AUDIT-07 | T-11-22, T-11-23 | Request/source/finding schemas reject missing and extra scope/citation/evidence data and match runtime versions | `python tests/audit_roundtrip.py --case schemas` | ❌ W0 from 11-01-01 | ⬜ pending |
| 11-02-02 | 02 | 2 | AUTH-01, AUTH-03, AUDIT-06, AUDIT-08 | T-11-22, T-11-24 | Report/manifest schemas require gate, volume, unit, backend, diff, fingerprint, and provenance data with no unsafe restore selector | `python tests/audit_roundtrip.py --case schemas` | ❌ W0 from 11-01-01 | ⬜ pending |
| 11-03-01 | 03 | 3 | AUDIT-01 | T-11-06, T-11-10, T-11-27 | Markdown/text exact round trips preserve heading/list/body objectives, locators, spans, strict UTF-8, fingerprints, and unchanged inputs; the complete PDF/DOCX gold matrix yields deterministic explicit unsupported/lossy results with no fabricated locator until exact structure proof exists | `python tests/audit_coverage_roundtrip.py --case normalize` | ❌ W0 | ⬜ pending |
| 11-03-02 | 03 | 3 | AUDIT-02, AUDIT-03 | T-11-06, T-11-07, T-11-09 | Covered requires exact current source-span and stable bank-item citations; stale/empty/null remains unknown and ordering is deterministic | `python tests/audit_coverage_roundtrip.py --case coverage` | ❌ W0 from 11-03-01 | ⬜ pending |
| 11-03-03 | 03 | 3 | AUDIT-04 | T-11-08 | Candidate material and weak-objective priority cannot call an author/writer; supplied material creates only a separate cited request | `python tests/audit_coverage_roundtrip.py --case material` | ❌ W0 from 11-03-01 | ⬜ pending |
| 11-04-01 | 04 | 3 | AUDIT-07 | T-11-14, T-11-15 | All four named detectors enforce exact threshold/floor/equality cases, preserve separate measured evidence, and never change identity | `python tests/audit_quality_roundtrip.py` | ❌ W0 | ⬜ pending |
| 11-04-02 | 04 | 3 | AUTH-01, AUTH-02, AUTH-03, AUDIT-06 | T-11-11 | Scope precedes lint, structured failures drive exact-cap retry, full-batch preflight blocks prefixes, and repository-blind input is sufficient | `python tests/audit_authoring_roundtrip.py --case retry` | ❌ W0 | ⬜ pending |
| 11-04-03 | 04 | 3 | AUTH-01, AUTH-02, AUDIT-05, AUDIT-09 | T-11-12, T-11-13, T-11-21 | Duplicate/interrupted/parallel handoffs produce at most one valid write; all modes share gates and full reports capped pre/post volumes on every exit | `python tests/audit_authoring_roundtrip.py --case stateful` | ❌ W0 from 11-04-02 | ⬜ pending |
| 11-05-01 | 05 | 4 | AUTH-01, AUTH-02, AUTH-03, AUDIT-05, AUDIT-06, AUDIT-07, AUDIT-09 | T-11-16, T-11-25, T-11-26 | Only after both upstream gates pass, a real subprocess public command resolves configured Phase 8 `invoke(request, profile)`, retries structured failures, rejects prompt-injected/untrusted output, enforces caps, retains model-unavailable state with no write, applies both gates/mode policy, and accepts no injected callable | `python tests/model_adapter_roundtrip.py`; `python tests/audit_cli_roundtrip.py --case configured-adapter`; `python tests/audit_cli_roundtrip.py --case modes` | Phase 8 + approved Phase 11 AI evaluation contract preconditions + ❌ W0 | ⬜ pending |
| 11-05-02 | 05 | 4 | AUDIT-08 | D-15 one-way checkpoint | Human confirms execution of the already-locked Git/shadow write-ID, manifest, backend, and undo contract before persisted implementation | N/A — blocking `checkpoint:decision`; Task 11-05-03 is the automated postcondition | N/A | ⬜ pending |
| 11-05-03 | 05 | 4 | AUTH-01, AUTH-02, AUDIT-08 | T-11-17..20 | Tracked-clean and shadow writes are atomic/idempotent/recoverable; one undo routes by manifest and refuses stale/conflicting human work | `python tests/audit_writer_roundtrip.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

## Requirement Coverage Matrix

| Requirement | Executable proof |
|-------------|------------------|
| AUTH-01 | 11-01 tracer; 11-04 retry/stateful; 11-05 no-DI configured-adapter subprocess |
| AUTH-02 | 11-01 scope spy; 11-04 every-attempt/post-lock scope tests; 11-05 no-write-on-invalid/unavailable subprocess and writer revalidation |
| AUTH-03 | 11-01 repository-blind spy plus 11-05 external fake hosted executable completing the public command from contract/findings alone |
| AUDIT-01 | 11-03 exact Markdown/text round trips plus the separate required PDF/DOCX gold locator/reading-order/fingerprint matrix and deterministic explicit unsupported/lossy proof |
| AUDIT-02 | 11-03 deterministic objective coverage/gap cases |
| AUDIT-03 | 11-03 exact dual-citation, stale, empty, null, singleton, and confidence-non-escalation cases |
| AUDIT-04 | 11-03 inert material pointers plus separate obtained-material request with zero author/writer calls |
| AUDIT-05 | 11-04 domain permission cases plus 11-05 registered public CLI mode cases |
| AUDIT-06 | 11-01/11-04 lint-blocking and retry cases plus 11-05 public configured-adapter path |
| AUDIT-07 | 11-01 tracer and 11-04 exact four-detector threshold suite plus 11-05 public configured-adapter path |
| AUDIT-08 | 11-01 shadow tracer undo plus 11-05 report-artifact, Git, shadow, stale/conflict, interruption, and public undo cases |
| AUDIT-09 | 11-04 every-exit volume cases plus 11-05 registered full-autonomy CLI output |

## Multi-Source Coverage Audit

| Source | ID | Feature/constraint | Plan | Status |
|--------|----|--------------------|------|--------|
| GOAL | — | Closed repository-blind authoring retry plus cited curriculum audit, identical gates, graduated autonomy, visible volume, and one-step reversible writes | 11-01..11-05 | COVERED |
| REQ | AUTH-01 | One-command spec→draft→lint→repair→write loop | 11-01, 11-04, 11-05 | COVERED |
| REQ | AUTH-02 | Runtime-enforced request scope | 11-01, 11-04, 11-05 | COVERED |
| REQ | AUTH-03 | Repository-blind completion from public contract | 11-01, 11-04, 11-05 | COVERED |
| REQ | AUDIT-01 | Detailed objective extraction | 11-03 | COVERED |
| REQ | AUDIT-02 | Objective coverage/gap mapping | 11-03 | COVERED |
| REQ | AUDIT-03 | Citation-per-covered-claim; uncitable is unknown | 11-03 | COVERED |
| REQ | AUDIT-04 | Material pointers and explicit obtained-material absorption | 11-03 | COVERED |
| REQ | AUDIT-05 | Report, approval, and full autonomy | 11-04, 11-05 | COVERED |
| REQ | AUDIT-06 | Lint before any bank write | 11-01, 11-04, 11-05 | COVERED |
| REQ | AUDIT-07 | Four deterministic post-lint quality checks | 11-01, 11-04, 11-05 | COVERED |
| REQ | AUDIT-08 | Visible diff plus one-step Git/shadow undo | 11-01, 11-05 | COVERED |
| REQ | AUDIT-09 | Highest-autonomy volume visibility | 11-04, 11-05 | COVERED |
| RESEARCH | stack | Python stdlib only; compose model/schema/atomic-write seams; no package install | 11-01..11-05 | COVERED |
| RESEARCH | adapter | Public Phase 8 `model_adapter.invoke(request, profile)` and settings-selected hosted/local transport | 11-05 | COVERED |
| RESEARCH | source/citations | Markdown/text stable locators, fingerprints, exact source span + bank ID evidence; PDF/DOCX fixture-backed exact-or-explicit-failure architectural gate | 11-02, 11-03 | COVERED |
| RESEARCH | quality | Independent skew/Jaccard/answer-leak/rationale detectors at researched thresholds | 11-01, 11-04 | COVERED |
| RESEARCH | autonomy | One final permission decision with exact approval, caps, and every-exit volume | 11-04, 11-05 | COVERED |
| RESEARCH | reversibility | Exact tracked-clean Git or guarded shadow backend behind one undo API | 11-01, 11-02, 11-05 | COVERED |
| RESEARCH | UI fence | No daemon/frontend route in this phase; CLI uses reusable domain functions | 11-01, 11-03, 11-05 | COVERED |
| CONTEXT | D-01 | Versioned locator-faithful normalized source and dual citations | 11-02, 11-03 | COVERED |
| CONTEXT | D-02 | Uncited is unknown; partial/conflicting explicit | 11-02, 11-03 | COVERED |
| CONTEXT | D-03 | Guaranteed Markdown/text adapters; complete PDF/DOCX locator-fidelity fixtures; no support claim unless each structure round-trips exactly or fails explicitly | 11-03 | COVERED |
| CONTEXT | D-04 | Read-only originals, fingerprints, stale reports | 11-03 | COVERED |
| CONTEXT | D-05 | One full orchestration command/route | 11-01, 11-04, 11-05 | COVERED |
| CONTEXT | D-06 | Public contract and structured retry findings | 11-01, 11-04, 11-05 | COVERED |
| CONTEXT | D-07 | Explicit objective/count/type/citation bounds | 11-01, 11-02, 11-04 | COVERED |
| CONTEXT | D-08 | Retained exhausted batch and zero prefix write | 11-01, 11-04 | COVERED |
| CONTEXT | D-09 | Separate versioned quality findings | 11-01, 11-02, 11-04 | COVERED |
| CONTEXT | D-10 | Explainable configurable detector evidence | 11-01, 11-04 | COVERED |
| CONTEXT | D-11 | Both gates before machine-authored approval/write | 11-01, 11-04, 11-05 | COVERED |
| CONTEXT | D-12 | Three modes share one pipeline | 11-04, 11-05 | COVERED |
| CONTEXT | D-13 | Explicit full risk, caps, proposed/final volume | 11-02, 11-04, 11-05 | COVERED |
| CONTEXT | D-14 | Autonomy changes permission only | 11-04, 11-05 | COVERED |
| CONTEXT | D-15 | One writer, Git/shadow choice, one undo; one-way checkpoint retained | 11-02, 11-05 | COVERED |
| CONTEXT | D-16 | One declared reversible unit; visible resumable partial state | 11-02, 11-04, 11-05 | COVERED |
| CONTEXT | D-17 | Reproducible request/source/bank/profile/tool provenance | 11-01..11-05 | COVERED |
| CONTEXT | D-18 | Gap/material report separate from authoring authority | 11-03 | COVERED |
| CONTEXT | D-19 | Weak-objective signals only prioritize existing objectives | 11-03 | COVERED |

Excluded without gaps: claiming guaranteed PDF/DOCX extraction before the required architectural evidence turns green, unbounded autonomous curriculum invention, hosted storage/shared gradebook, and UI/daemon routes pending a separate approved contract. The PDF/DOCX gold fixture matrix and explicit unsupported/lossy proof are in scope and mandatory.

## AI-SPEC Evaluation Matrix

The executable reference set contains at least 36 synthetic cases and maps every `11-AI-SPEC.md` dimension to a deterministic proof. PDF/DOCX fidelity fixtures are a separate architectural gate and do not count toward the 36 supported-ingestion cases.

| AI-SPEC dimension | Minimum cases | Owning proof | Release assertion |
|---|---:|---|---|
| Markdown/text locator fidelity and objective recall | 10 | `python tests/audit_coverage_roundtrip.py --case normalize` | Exact Unicode/span/locator reconstruction, heading/list/body subtleties, deterministic fingerprint, unchanged bytes, and explicit malformed-UTF-8 failure |
| Citation fidelity and coverage-state boundaries | 8 | `python tests/audit_coverage_roundtrip.py --case coverage` | Covered always has exact current dual citations; stale/empty/null/uncitable remains unknown; conflicting/partial/gap stay distinct |
| Prompt-injection resistance and scope fidelity | 6 | `python tests/audit_authoring_roundtrip.py --case retry`; `python tests/audit_cli_roundtrip.py --case configured-adapter` | Source instructions and untrusted model fields cannot change operation, objectives, counts, types, citations, tools, autonomy, output schema, or writer authority |
| Malformed-first/clean-second and retry discipline | 6 | `python tests/audit_roundtrip.py --case tracer`; `python tests/audit_authoring_roundtrip.py --case retry`; `python tests/audit_cli_roundtrip.py --case configured-adapter` | Exact cap, stable structured findings, last-attempt success, retained exhaustion/unavailable report, and zero clean-prefix write |
| Permission, writer, conflict, and undo | 6 | `python tests/audit_authoring_roundtrip.py --case stateful`; `python tests/audit_writer_roundtrip.py` | Identical gates across modes, exact approval, deterministic diff/write identity, atomic Git/shadow backend, stale/conflict refusal, and one guarded undo |
| Four quality detectors | Boundary fixtures within the 36 above | `python tests/audit_quality_roundtrip.py` | Each detector's equality/floor/failure boundary is independent, measured, deterministic, and blocking without aggregate-score substitution |
| Model unavailable/offline | Adversarial variants within the 36 above | `python tests/audit_cli_roundtrip.py --case configured-adapter`; `python tests/model_adapter_roundtrip.py` | Request, source, findings, report, and diff remain readable; no publish, write, retry loop, raw provider output, or blocking spinner |

The separate `fixtures/audit/locator_fidelity_cases.py` gate deterministically materializes all nine required PDF structures and all nine required DOCX structures with gold page/section/paragraph/table-cell locators, exact Unicode spans, reading order, intentionally unsupported structures, and original-byte SHA-256. The current registry must process every fixture twice with byte-identical explicit unsupported/lossy results, no spans/locators, no AI call, and unchanged source bytes/timestamps. A future adapter may claim support only for structures that round-trip exactly; all others continue to fail explicitly.

## Wave 0 Requirements

- [ ] `tests/audit_roundtrip.py` — Plan 11-01 creates the tracer/scope/schema harness.
- [ ] `tests/audit_coverage_roundtrip.py` — Plan 11-03 creates source/citation/material coverage.
- [ ] `fixtures/audit/locator_fidelity_cases.py` — Plan 11-03 creates the deterministic redistributable PDF/DOCX byte-fixture matrix and gold locators/spans/reading order/SHA-256 expectations; current adapters prove deterministic explicit unsupported/lossy results and unchanged bytes.
- [ ] `tests/audit_quality_roundtrip.py` and `tests/audit_authoring_roundtrip.py` — Plan 11-04 creates detector/retry/stateful/autonomy coverage.
- [ ] `tests/audit_cli_roundtrip.py` and `tests/audit_writer_roundtrip.py` — Plan 11-05 creates the no-DI composition and Git/shadow writer coverage.
- [ ] Phase 8 precondition — `model_adapter.py`, `schemas/model_adapter.schema.json`, and `tests/model_adapter_roundtrip.py` exist and the adapter suite is green before 11-05-01.
- [x] Phase 11 AI evaluation contract precondition — canonical `.planning/phases/11-closed-authoring-loop-curriculum-auditor/11-AI-SPEC.md` exists with approved status and covers author-operation scope, structured retries, prompt-injection/untrusted-output cases, volume caps, and model-unavailable behavior. Phase 8 artifacts/tests and executable Phase 11 fixtures remain separate green gates before 11-05-01.
- [ ] Synthetic `fixtures/audit/` files are copied into temporary directories before any mutation; no real bank enters the repository.
- [ ] The 36-case AI reference inventory is machine-counted by the focused suites with the category minimums above; PDF/DOCX architectural fixtures remain separately counted and never masquerade as supported-ingestion cases.

## Supplemental Human Verification

| Behavior | Requirement | Why supplemental | Test instructions |
|----------|-------------|------------------|-------------------|
| Approval flow communicates the exact proposed diff clearly | AUDIT-05 | Terminal clarity is experiential; automated exact-write-id permission remains authoritative | Run draft-and-approve against a temporary synthetic fixture, reject once and approve once, and confirm only the exact approved write ID changes the copy |
| Citation and locator fidelity are understandable | AUDIT-01, AUDIT-03 | Gold-span accuracy and honest unsupported/lossy labeling benefit from author review | Inspect one Markdown body-level objective and one table-like source span against original bytes, then inspect representative PDF/DOCX results; confirm exact citations for supported text and no invented locator for unsupported structures |
| Model-unavailable report-only flow remains usable | AUTH-01, AUDIT-05 | Recovery wording and operator comprehension are experiential even though mutation absence is automated | Disable/unconfigure the Phase 8 profile, run report-only authoring, and confirm request/findings/source/report/diff remain readable, no raw provider diagnostic appears, and no approval/write/undo action is offered |
| Writer and one-step undo communicate backend and conflict clearly | AUDIT-08 | Human confidence in the diff/backend/recovery presentation supplements atomicity tests | On temporary tracked-clean and shadow fixtures, review exact diff/write ID/backend/manifest, apply once, undo once, then create a stale/conflicting edit and confirm undo refuses without changing human bytes |

## Validation Sign-Off

- [x] Exactly five plans and twelve tasks are mapped.
- [x] Every implementation task has a runnable `<automated>` verify command; the sole exception is the required blocking D-15 decision checkpoint immediately followed by an automated writer task.
- [x] AUTH-01..AUTH-03 and AUDIT-01..AUDIT-09 each have executable proof.
- [x] No three consecutive implementation tasks lack automated verification.
- [x] No watch-mode flags or external packages are required.
- [x] Full public AUTH-01/AUTH-03 proof uses configured adapter state and the real CLI subprocess with no dependency injection.
- [ ] All `11-AI-SPEC.md` dimensions, the machine-counted 36-case reference set, and the separate PDF/DOCX locator-fidelity gate are green.
- [ ] Plans 11-01 through 11-04 completed without Phase 8 artifacts; Plan 11-05 began only after green Phase 8 adapter evidence and retained the blocking D-15 writer checkpoint before writer implementation.
- [ ] `nyquist_compliant: true`, `wave_0_complete: true`, and `status: validated` are set only after the corresponding executable and human evidence exists.

**Approval:** planning-complete; execution pending
