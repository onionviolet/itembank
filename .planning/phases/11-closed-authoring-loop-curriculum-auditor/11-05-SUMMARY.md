---
phase: 11-closed-authoring-loop-curriculum-auditor
plan: 05
subsystem: closed-authoring-loop
tags: [configured-adapter, composition-root, git-writer, shadow-writer, undo, os-lock, checkpoint]

requires:
  - phase: 11-closed-authoring-loop-curriculum-auditor
    provides: plan 11-01 shadow writer + run_authoring, plan 11-02 strict schemas, plan 11-03 coverage, plan 11-04 state machine + autonomy modes, approved 11-AI-SPEC.md, Phase 8 adapter artifacts (model_adapter.py + schema + green tests)
  - phase: 08-model-adapter-interface-tier-gate-enforcement
    provides: model_adapter.invoke(request, settings) public boundary and hosted/local transports
provides:
  - model_adapter.py + schemas/model_adapter.schema.json: additive operation `author` (author_request payload = public contract + bounded request + attempt + versioned findings); existing hint/rubric operations unchanged
  - surfaces/cli.py: declarative `audit source|coverage|material|author|undo` registration; the author handler binds the configured Phase 8 adapter at the real composition root (load_settings(base)["model_backend"] -> closure over model_adapter.invoke)
  - surfaces/audit_cli.py: full config surface (mode opt-in, caps, exact approval ids, --write wiring)
  - audit_writer.py: Git/shadow writer behind one manifest/undo API -- per-bank OS lock (msvcrt/fcntl, bounded busy timeout), tracked+clean Git detection, one machine-authored commit per unit + committed manifest, content-addressed shadow with before_exists for new report artifacts, multi-location manifest lookup, git revert undo with dirty/conflict refusal
  - tests/audit_cli_roundtrip.py: --case configured-adapter (no-DI real subprocess through surfaces.cli.main -> model_adapter.invoke; malformed-first/clean-second retry; repository-blind request assertions; public undo) + --case modes (report_only / exact approval / full capped volume)
  - tests/audit_writer_roundtrip.py: shadow/Git write+undo, stale refusal, dirty->shadow fallback, before_exists artifact, prepared journal on interruption, duplicate idempotency, parallel single-mutation
  - fixtures/audit/writer_bank.md: synthetic writer fixture
  - build.py: the three Phase 11 root modules join the .pyz stage
affects: [phase handoff; daemon/frontend routes remain UI-BLOCKED pending 11-UI-SPEC]

actuals:
  tokens: 0
  tasks: 3
  commits: 1

checkpoint:
  id: 11-05-02
  decision: proceed
  outcome: "The locked D-15 Git/shadow contract was confirmed for execution per the phase instruction (plans 11-01..11-05 execute in order, including the writer task). No design option was reopened; the one-way write-id/manifest/backend/undo semantics are implemented exactly as locked."

tech-stack:
  added: []
  patterns:
    - "Composition root: surfaces/cli.py::main is the only place the configured Phase 8 adapter is bound; the subprocess test supplies configuration/files/arguments only and reaches model_adapter.invoke with no injected callable (T-11-26)."
    - "The adapter author request carries only the public format contract, the bounded request, the attempt number, and versioned structured findings; an unavailable/refusal result becomes a malformed response so the pipeline retries within its cap and retains a report with zero writes (T-11-25)."
    - "Per-bank cross-platform OS lock (msvcrt on Windows, fcntl where available) with a bounded timeout and explicit writer.busy around fingerprint revalidation + mutation; tracked+clean targets get one machine-authored git commit per accepted unit plus its manifest, everything else the content-addressed shadow path."
    - "Undo routes by manifest backend only: git revert (non-interactive, dirty/conflict refusal, writer metadata reset first) or after-fingerprint-guarded shadow restore -- no caller-selected backend and no force path (D-15/T-11-17)."

key-files:
  created:
    - tests/audit_cli_roundtrip.py
    - tests/audit_writer_roundtrip.py
    - fixtures/audit/writer_bank.md
  modified:
    - model_adapter.py
    - schemas/model_adapter.schema.json
    - surfaces/cli.py
    - surfaces/audit_cli.py
    - audit_writer.py
    - build.py

key-decisions:
  - "The adapter operation set gains `author` additively; request_from_operation's closed payload keys gain author_request. The Phase 8 suite stays green, proving the additive change did not weaken hint/rubric branches."
  - "The git manifest lives at <repo>/.itembank/audit/manifests so it can be committed with the item; the applied-state update (with the commit hash) is post-commit metadata on disk, and undo resets only the writer's own .itembank/audit metadata before reverting -- human work on the bank is never touched."
  - "The git dirty/conflict refusal is scoped to the bank path (the writer's own metadata never blocks a revert) and still refuses newer human work with no force path."
  - "A newly created derived report artifact records before_exists: false with an empty before-image; undo removes the file -- an empty before-image is distinct from a missing one."
  - "state dirs for git tests live outside the temp repos so the repo stays clean; manifest lookup covers both the caller state dir and the repo manifest dir (found even when the bank is dirty)."

patterns-established:
  - "run_cli() in the CLI test is a real subprocess of `python itembank.py audit ...`; parse_report uses raw_decode to skip the trailing human summary line."
  - "The fake hosted executable is a committed-to-temp stdlib script that records every strict request and returns malformed-first/clean-second, proving structured retry and repository blindness end to end."

requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUDIT-05, AUDIT-06, AUDIT-07, AUDIT-08, AUDIT-09]

coverage:
  - id: D1
    description: "The public `python itembank.py audit author ...` process resolves model_backend in surfaces.cli.main, calls Phase 8's model_adapter.invoke through the configured fake hosted profile, retries from structured findings, writes exactly one clean gated unit, and completes with no test-supplied callable (AUTH-01/AUTH-03, T-11-26)."
    requirement: AUTH-01
    verification:
      - kind: integration
        ref: "tests/audit_cli_roundtrip.py#case_configured_adapter"
        status: pass
    human_judgment: false
  - id: D2
    description: "Tracked-clean Git and shadow writes each apply one declared unit, create a strict manifest, and undo in one call; dirty Git falls back to shadow; stale shadow and dirty/conflicting Git undo refuse without a force path; duplicate/interruption/parallel cases leave no duplicate or hidden mutation (AUDIT-08/D-15/D-16/D-17, T-11-17..T-11-20)."
    requirement: AUDIT-08
    verification:
      - kind: integration
        ref: "tests/audit_writer_roundtrip.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "report_only, exact write-id approval, and explicit full/capped autonomy are exercised through the registered public command with volume reported on every exit; the three modes share one validation/diff/audit pipeline and differ only at the final permission decision (AUDIT-05/AUDIT-09)."
    requirement: AUDIT-09
    verification:
      - kind: integration
        ref: "tests/audit_cli_roundtrip.py#case_modes"
        status: pass
    human_judgment: false

verification:
  - command: "python tests/model_adapter_roundtrip.py"
    status: pass
  - command: "python tests/audit_cli_roundtrip.py"
    status: pass
  - command: "python tests/audit_writer_roundtrip.py"
    status: pass
  - command: "python tests/audit_roundtrip.py && python tests/audit_coverage_roundtrip.py && python tests/audit_quality_roundtrip.py && python tests/audit_authoring_roundtrip.py"
    status: pass
  - note: "The D-15 checkpoint resolved to proceed before the one-way writer task began; no frontend, daemon route, package dependency, ORM schema push, or PDF/DOCX adapter was introduced."
