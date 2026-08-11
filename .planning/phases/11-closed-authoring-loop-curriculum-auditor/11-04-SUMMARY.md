---
phase: 11-closed-authoring-loop-curriculum-auditor
plan: 04
subsystem: closed-authoring-loop
tags: [quality-gate, retry-state-machine, preflight, autonomy-modes, volume, idempotency, interruption, prompt-injection]

requires:
  - phase: 11-closed-authoring-loop-curriculum-auditor
    provides: plan 11-01 four-detector quality_gate + run_authoring core, plan 11-02 strict schemas (quality_finding/audit_report/authoring_request), 11-RESEARCH thresholds, 11-AI-SPEC guardrails
provides:
  - authoring.py: full retry/preflight state machine (scope->lint->quality->recheck per attempt, exact cap, last-attempt success, no clean prefix, retained exhaustion); prompt-injection resistance (provider/source fields are untrusted and cannot change operation/scope/tools/autonomy/output schema/cap/permission); three-mode permission contract (report_only / draft_and_approve with durable pending-proposal resume + exact write-id approval / full with explicit opt-in + caps); every-exit volume accounting (proposed/completed/rejected/retried/written + per-objective); writer-failure surfacing (stale_preflight/interruption)
  - audit_writer.py: deterministic_write_id now derives only from provenance (request/source/bank-before/profile/quality-profile/tool), never the minted unit ids
  - schemas/audit_report.schema.json: status awaiting_approval/refused, string outcome (writer_*), message, pending_write_ids
  - fixtures/audit/quality_cases.json: 12-case four-detector boundary matrix (skew block/equality/inactive, near-dup block/just-below/five-token, leak block/2-token/shared, rationale missing-line/missing-would-be/complete)
  - fixtures/audit/retry_drafts.json: malformed/scope/lint/quality/injection draft specs
  - tests/audit_quality_roundtrip.py: exact thresholds, co-reporting, ordering, identity immutability, schema conformance
  - tests/audit_authoring_roundtrip.py: --case retry (scope-before-lint, structured findings, caps, no prefix, injection) and --case stateful (idempotency, interruption, parallel, modes, approval, opt-in, volume, stale)
affects: [11-05 configured-adapter binding, Git/shadow writer, CLI registration]

actuals:
  tokens: 0
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Every attempt is response-shape + scope validated before lint; structured scope/lint/quality records (versioned) become the next callable input -- never hand-relayed prose (D-06)."
    - "All-or-nothing preflight: compose, assign ids, parse, lint, quality-gate the complete proposed bank, recheck immediately before the writer; a dirty batch never writes its clean prefix (D-08)."
    - "Durable pending-proposal resume: draft_and_approve persists the prepared proposal by run id and an approval invocation resumes it without regenerating, so exact write-id acceptance is stable across calls (AUTH-01 interruption contract)."
    - "The permission decision is the only thing that differs across modes (D-12/D-14): identical proposal/diff/gates, verified byte-for-byte in the test; full requires explicit opt-in and caps enforced BEFORE generation with the model never called on refusal."
    - "Every exit carries volume accounting (D-13/AUDIT-09): proposed, completed, rejected, retried, written plus a per-objective breakdown."

key-files:
  created:
    - tests/audit_quality_roundtrip.py
    - tests/audit_authoring_roundtrip.py
    - fixtures/audit/quality_cases.json
    - fixtures/audit/retry_drafts.json
  modified:
    - authoring.py
    - audit_writer.py
    - schemas/audit_report.schema.json

key-decisions:
  - "draft_and_approve approval is by exact write id over a durable pending proposal: without approval the run returns awaiting_approval + pending_write_ids; an approval invocation with the same request+bank resumes the SAME proposal (never regenerates random unit ids); any id set other than the exact pending set is approval_mismatch with zero writer calls."
  - "Full autonomy is model-inaccessible: config.full_opt_in is the only switch, per-run/per-objective caps refuse before generation (callable never invoked), and every exit reports proposed/completed/rejected/retried/written volume."
  - "The deterministic write id derives from provenance only (request, source, bank-before, profile, quality profile, tool version) -- never the minted item ids -- so independent runs of the same bounded request converge on one write id."
  - "Provider output and source text are untrusted data (11-AI-SPEC 4b): injected mode/tools/retry_cap/autonomy/output-schema fields and instruction-like item text cannot change operation, scope, permission, caps, or the output shape; the adversarial fixtures prove it."
  - "The near-duplicate pair is normalized (lower id first) so findings are independent of input iteration order."

patterns-established:
  - "volume_record() is the single accounting helper emitted on every exit path (success, exhaustion, refusal, awaiting, writer failure)."
  - "A fake PrepareThenRaise writer proves prepared-state visibility: a crash after the prepared manifest leaves a visible run and an untouched bank, never a false completion."

requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUDIT-05, AUDIT-06, AUDIT-07, AUDIT-09]

coverage:
  - id: D1
    description: "The bounded repair loop: scope-before-lint on every attempt, structured versioned findings as the only retry input, exact cap (success on the last attempt proceeds; one more call never occurs), retained draft on exhaustion with zero writer calls, no clean prefix in a dirty batch, and prompt-injection resistance (AUTH-01/AUTH-02/AUTH-03, AUDIT-06, 11-AI-SPEC 4b)."
    requirement: AUTH-01
    verification:
      - kind: integration
        ref: "tests/audit_authoring_roundtrip.py#case_retry"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exactly four independently named deterministic detectors with the Research thresholds and floors (skew >=12 MC, block only >40%, equality at 40% passes; near-dup Jaccard >=0.85 with a six-token floor; leak unique contiguous >=3-token run; rationale must state the would-be condition); findings are separate, stable-sorted, versioned, evidence-rich, co-report without an aggregate score, and never mutate ids/fingerprints (AUDIT-07/D-09/D-10)."
    requirement: AUDIT-07
    verification:
      - kind: integration
        ref: "tests/audit_quality_roundtrip.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "Duplicate runs return the existing result without regenerating; interruption (including a crash after the prepared manifest) is an explicit failed report with a visible run and untouched bank; two parallel handoffs produce at most one mutation; no run completes without one matching scope-valid writer result (AUTH-01/AUTH-02)."
    requirement: AUTH-01
    verification:
      - kind: integration
        ref: "tests/audit_authoring_roundtrip.py#case_stateful"
        status: pass
    human_judgment: false
  - id: D4
    description: "report_only, draft_and_approve, and full share byte-identical gates and diff and differ only at the final permission decision; draft_and_approve requires exact write-id acceptance (awaiting_approval without it, approval_mismatch refusal otherwise); full requires explicit opt-in and caps, refuses before generation, and reports proposed/completed/rejected/retried/written volume on every exit (AUDIT-05/AUDIT-09/D-12/D-13/D-14)."
    requirement: AUDIT-09
    verification:
      - kind: integration
        ref: "tests/audit_authoring_roundtrip.py#case_stateful"
        status: pass
    human_judgment: false

verification:
  - command: "python tests/audit_quality_roundtrip.py"
    status: pass
  - command: "python tests/audit_authoring_roundtrip.py"
    status: pass
  - command: "python tests/audit_roundtrip.py"
    status: pass
  - command: "python tests/audit_coverage_roundtrip.py"
    status: pass
  - note: "Identity and fingerprint output is byte-identical before/after quality analysis; no provider is selected and no run completes without a matching scope-valid writer result (plan 11-04 verification)."
