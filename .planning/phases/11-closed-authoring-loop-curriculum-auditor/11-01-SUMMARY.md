---
phase: 11-closed-authoring-loop-curriculum-auditor
plan: 01
subsystem: closed-authoring-loop
tags: [tracer, authoring-pipeline, quality-gate, shadow-writer, repository-blind, audit-cli]

requires:
  - phase: 11-closed-authoring-loop-curriculum-auditor
    provides: locked decisions D-01..D-19 (11-CONTEXT), approved AI-SPEC guardrails, Research detector thresholds, Pattern map (11-PATTERNS)
provides:
  - authoring.py: provider-neutral run_authoring(request, author_callable, bank_text, writer, config); scope-before-lint (AUTH-02/D-07); structured versioned retry findings (D-06); all-or-nothing full-candidate preflight (D-08); immutable proposal with deterministic run id (AUTH-01/D-17); duplicate-run idempotency; quality_gate with exactly four named detectors (AUDIT-07/D-09/D-10); report_only / full modes (D-12)
  - auditor.py: UTF-8 bytes-to-normalized-source record (spans with heading path, line/char locators, verbatim text, SHA-256 fingerprint); exact citation records; heading/list/body objective candidates; typed SourceError for malformed UTF-8, oversize input, unregistered adapters (D-01/D-03/D-04)
  - audit_writer.py: content-addressed shadow writer — deterministic write id, prepared manifest + before-image persisted before mutation, tmp+os.replace, after-fingerprint guard, one-step undo with stale refusal and no force path (D-15/D-16/D-17, T-11-17), find_applied_manifest duplicate-run probe
  - surfaces/audit_cli.py: thin command adapter (audit source|author|undo) over the domain APIs; author callable stays injected until plan 11-05 binds the configured Phase 8 adapter
  - tests/audit_roundtrip.py: Wave 0 standalone stdlib tracer suite (--case tracer), schemas case stub for 11-02
affects: [11-02 strict public schemas, 11-03 coverage engine, 11-04 retry/state machine + autonomy modes, 11-05 configured-adapter + Git/shadow writer + CLI registration]

actuals:
  tokens: 0
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "One orchestration command (run_authoring) carries a scoped item through repository-blind author -> response scope -> lint -> four-detector quality gate -> full-candidate preflight -> atomic shadow write -> one-step undo; no provider import in the domain module (D-05, 11-PATTERNS authoring analog)"
    - "The callable receives only model.SPEC, the bounded request, the attempt number, and versioned structured findings — an allowlist the spy test asserts by serialized-payload inspection (D-06, AUTH-03)"
    - "All-or-nothing preflight: compose the whole candidate, assign ids with model.assign_ids, parse with model.parse_bank, lint with model.lint, quality-gate the complete proposed bank — the writer is invoked only after every gate passes and never accepts a clean prefix (D-08, 11-PATTERNS all-or-nothing pattern)"
    - "Deterministic identity: request/run/write ids and bank/source fingerprints derive from canonical JSON of provenance fields; a duplicate invocation returns the existing result with zero generation and zero mutation (AUTH-01, D-17)"
    - "Content-addressed shadow undo: before-image stored by its SHA-256, restore allowed only when the current fingerprint equals the recorded after-image; no force/restore-anyway path (T-11-17)"

key-files:
  created:
    - authoring.py
    - auditor.py
    - audit_writer.py
    - surfaces/audit_cli.py
    - tests/audit_roundtrip.py

key-decisions:
  - "run_authoring takes the writer as an injected callable (defaulting to audit_writer.write_units in production) so the domain stays provider-neutral and the tracer can count writer invocations; the writer contract accepts only an immutable proposal plus expected bank fingerprint and rechecks under its own control."
  - "The model never learns the bank's current numbering: item blocks are normalized with a placeholder number and the composed candidate is renumbered deterministically (identity transform for an already-sequential bank), keeping the author repository-blind."
  - "The quality gate is four independent named detectors with versioned measured evidence and no aggregate score; skew reuses the live lint precedent (>=12 MC items, block only >40%), near duplicates use Jaccard >=0.85 with a six-token floor, answer leak blocks a unique contiguous >=3-token run, and distractor rationale completeness promotes the lint-observable missing-rationale / missing-would-be-condition checks without duplicating parser logic."
  - "The shadow writer persists a prepared manifest plus content-addressed before-image before any mutation, so interruption leaves the bank untouched and the run visible; the after-fingerprint guard runs before the manifest is marked applied."
  - "mode report_only never writes; full writes exactly one clean unit in this plan — the draft_and_approve exact write-id flow and full-autonomy volume accounting are the plan 11-04 permission contract."

patterns-established:
  - "Lazy import of audit_writer inside authoring avoids a circular dependency while keeping the writer boundary explicit."
  - "canonical_json (sorted keys, compact separators) is the single fingerprint serialization for request/run/write identity."
  - "Tracer fixtures are pure strings materialized into temp dirs; the spy author returns drafts by attempt number and the spy writer counts calls while delegating to the real shadow writer."

requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUDIT-06, AUDIT-07, AUDIT-08]

coverage:
  - id: D1
    description: "A repository-blind spy callable carries one scoped mc item through response-scope validation, lint, all four quality detectors, full-candidate preflight, one atomic shadow write, duplicate-run idempotency, and one-step undo; the first attempt returns an out-of-scope draft, receives the structured scope finding as versioned retry input, and the clean second attempt writes exactly once."
    requirement: AUTH-01
    verification:
      - kind: integration
        ref: "tests/audit_roundtrip.py#case_tracer"
        status: pass
    human_judgment: false
  - id: D2
    description: "An item outside the requested objective/count/citation set is rejected before lint and before any writer call; the scope-exhaustion sub-case proves zero writer calls and a retained final draft at the retry cap (D-08)."
    requirement: AUTH-02
    verification:
      - kind: integration
        ref: "tests/audit_roundtrip.py#case_tracer (out-of-scope exhaustion)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every callable payload carries exactly {schema_version, contract, request, attempt, findings}; serialized-payload assertions reject repository file/module identifiers, absolute paths, credentials, bank text, and un-cited source prose (AUTH-03/T-11-03)."
    requirement: AUTH-03
    verification:
      - kind: integration
        ref: "tests/audit_roundtrip.py#_assert_repository_blind"
        status: pass
    human_judgment: false
  - id: D4
    description: "A lint-clean answer-leak draft is rejected by the named quality.answer_leak detector and retried; the tracer cannot reach the writer unless lint and all four detectors pass (AUDIT-06/AUDIT-07)."
    requirement: AUDIT-07
    verification:
      - kind: integration
        ref: "tests/audit_roundtrip.py#case_tracer (quality-retry sub-case)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The non-Git synthetic bank is replaced atomically only after every gate passes; the manifest records backend shadow, deterministic write id, before/after fingerprints, request/source fingerprints, tool version, and diff; undo(write_id) restores the exact before bytes, second undo is idempotent, and a stale target refuses without a force path (AUDIT-08/D-15/D-16/D-17, T-11-17)."
    requirement: AUDIT-08
    verification:
      - kind: integration
        ref: "tests/audit_roundtrip.py#case_tracer (undo/stale sub-cases)"
        status: pass
    human_judgment: false

verification:
  - command: "python tests/audit_roundtrip.py --case tracer"
    status: pass
  - command: "python -m py_compile auditor.py authoring.py audit_writer.py surfaces/audit_cli.py tests/audit_roundtrip.py"
    status: pass
  - note: "No surfaces/daemon.py, frontend asset, ORM migration, package manifest, PDF/DOCX adapter, or COVERAGE.md was created (plan 11-01 verification)."
