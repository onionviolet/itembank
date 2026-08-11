---
phase: 08-model-adapter-interface-tier-gate-enforcement
plan: 04
subsystem: api
tags: [model-adapter, tier-gate, evidence, cli, rubric-review, agent-usage-contract, hint]

# Dependency graph
requires:
  - phase: 08-model-adapter-interface-tier-gate-enforcement
    provides: tier-gate (08-01), model-adapter boundary (08-02), model_interaction/mark_proposal evidence events (08-03)
provides:
  - "The one model-orchestrated hint path: runtime.hint_context/invoke_hint sequencing adapter -> gate -> evidence -> authored fallback, idempotent per interaction id with parent-linked explicit retries (D-12)"
  - "The one rubric-review path: runtime.invoke_rubric_review producing pending-only per-point suggestions with the human-only accept path through cmd_mark --proposal and proposal-bearing batch entries (D-13/D-14/D-25)"
  - "surfaces/session.py do_hint(session_file, retry=False)/do_rubric_review/cmd_hint/cmd_rubric_review and the render_suggestion pending-token helper (D-22)"
  - "surfaces/cli.py hint (--session/--retry), rubric-review, and usage sub-parsers"
  - "The machine-readable agent usage contract: schemas/agent_usage.schema.json served verbatim by itembank usage and included in itembank schema --all (MODEL-04)"
affects: [08-05 daemon routes and SURFACE_PARITY, 08-06 browser surface, model-facing consumers]

# Actuals (#2632) — chars/4 over the realized diff of this plan's nine files.
actuals:
  tokens: 18749
  tasks: 3
  commits: 7

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Runtime-owned orchestration seam: the surface calls runtime.invoke_hint/invoke_rubric_review, which sequence model_adapter.request_from_operation -> model_adapter.invoke -> tier_gate.evaluate_candidate -> evidence.model_interaction_event -> authored fallback; the CLI never touches tier, profile, key, or marker"
    - "One generation per interaction id enforced by the evidence dedupe (hash over session_id + interaction_id); retry=True mints a uuid4 child id with parent_interaction_id pointing at the most recent interaction"
    - "Human-only accept through the existing mark_event: cmd_mark --proposal resolves the proposal to its response event and records marker='human' with proposal_ref; batch entries resolve every target before any append"

key-files:
  created:
    - schemas/agent_usage.schema.json
    - tests/model_surface_roundtrip.py
  modified:
    - runtime.py
    - surfaces/session.py
    - surfaces/cli.py
    - surfaces/evidence_cli.py
    - surfaces/protocol_cli.py
    - tests/hint_roundtrip.py
    - tests/protocol_roundtrip.py

key-decisions:
  - "The CLI hint command is now the model-orchestrated diagnostic hint (--session/--retry); the Phase 6 explicit tier-reveal stays in the runtime teaching transition and the daemon's /api/hint until plan 08-05 rewires that route"
  - "A stumped=None sentinel on surfaces/session.do_hint keeps the daemon's Phase 6 /api/hint (and the quiz page's I'm-stumped control) working unchanged until 08-05, since surfaces/daemon.py is out of this plan's file scope"
  - "Interaction ids are uuid4 hex; the evidence dedupe makes at most one generation per interaction id structural, and an explicit retry is a parent-linked child, never a reuse of the dedupe key"
  - "Rubric review is pending-suggestions-only: a model path can never settle a mark; the only accept paths are the human's mark_event via --proposal and the batch 'proposal' key, and no auto-accept flag exists anywhere"
  - "The permitted tier for an offline hint after genuine wrong practice attempts is 0 (the lesson pointer): Phase 6's evidence fold reconstructs the teaching record from response events whose hint_tier records only the shown tier, so the test bank carries tier-0 lesson content to prove the authored fallback"
  - "The agent usage contract is a closed v1 schema (additionalProperties false, SUPPORTED keywords only) with exact enum/const clauses for permissions, prohibitions, disclosure, retry, manual grading, and forbidden inferences, printed byte-for-byte"

patterns-established:
  - "Runtime-orchestrated model operation: resolve session/item -> context resolver -> mint/reuse interaction id -> adapter request -> adapter invoke -> gate -> learner payload or authored fallback -> one evidence event -> typed learner payload with no reason code"
  - "Pending-only tier-3 suggestions: per-point statuses live in the mark_proposal evidence event; the surface renders a suggestion only as the pending token, and acceptance is the existing human mark_event with proposal_ref"
  - "Contract delivery: the agent usage document is a schemas/*.json published through protocol_cli CONTRACTS and printed verbatim by `itembank usage`, the no-processing house pattern"

requirements-completed: [TEACH-04, TEACH-07, TEACH-08, TEACH-09, MODEL-03, MODEL-04, MODEL-05]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "Model-orchestrated hint path: offline typed unavailable payload plus authored tier content, one model_interaction event per interaction id, idempotent repeat, parent-linked explicit retry, cmd_hint prints JSON and reaches do_hint"
    requirement: MODEL-03
    verification:
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_hint_offline_disabled_backend_typed_unavailable"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_hint_idempotent_second_call"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_hint_retry_lineage"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_cmd_hint_prints_json_exits_zero_and_parity"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_hint_no_genuine_wrong_response_generates_nothing"
        status: pass
    human_judgment: false
  - id: D2
    description: "Rubric review pending-only loop: pending suggestions only for a genuine pending short response, named refusals with no evidence write, human-only proposal accept via --proposal and batch 'proposal' keys, all-or-nothing batch resolution, pending-token-only rendering and no auto-accept flag"
    requirement: TEACH-07
    verification:
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_rubric_review_pending_suggestions_short_only"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_rubric_review_refuses_with_named_reason_and_no_write"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_cmd_mark_proposal_human_accept"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_cmd_mark_proposal_batch_all_or_nothing"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_suggestion_pending_token_only_and_no_auto_accept"
        status: pass
    human_judgment: false
  - id: D3
    description: "Agent usage contract: schemas/agent_usage.schema.json validates (SUPPORTED keywords only, closed object, exact enum/const clauses), prints byte-for-byte from `itembank usage` and `itembank schema agent_usage`, and is included in `itembank schema --all`; no invented performance figure and no secret reference format beyond env-var names"
    requirement: MODEL-04
    verification:
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_agent_usage_schema_validates_and_clauses"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_usage_command_prints_contract_and_schema_all"
        status: pass
      - kind: unit
        ref: "tests/model_surface_roundtrip.py#test_usage_contract_no_invented_figures_no_secret_values"
        status: pass
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_schema_command_output"
        status: pass
    human_judgment: false
  - id: D4
    description: "The authored loop (submit, score, lesson, evidence, report, mark) and evidence/scoring authority stay unchanged with the new surfaces wired"
    requirement: MODEL-03
    verification:
      - kind: unit
        ref: "python tests/evidence_roundtrip.py (clean copy excluding .phase*-wt worktrees)"
        status: pass
      - kind: unit
        ref: "python tests/scoring_roundtrip.py (clean copy excluding .phase*-wt worktrees)"
        status: pass
      - kind: unit
        ref: "tests/hint_roundtrip.py"
        status: pass
      - kind: unit
        ref: "tests/agent_roundtrip.py"
        status: pass
    human_judgment: false

# Metrics
duration: 55min
completed: 2026-08-11
status: complete
---

# Phase 08 Plan 04: Model Surface Commands — Hint, Rubric Review, and the Agent Usage Contract Summary

**The runtime-owned model command surfaces ship: one model-orchestrated hint path (offline typed unavailable + authored fallback, one generation per interaction id, parent-linked explicit retries), a pending-suggestions-only rubric review with the human-only proposal accept, and a machine-readable agent usage contract printable from the CLI.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-11T01:05:00Z
- **Completed:** 2026-08-11T02:00:00Z
- **Tasks:** 3
- **Files modified:** 9 (runtime.py, surfaces/session.py, surfaces/cli.py, surfaces/evidence_cli.py, surfaces/protocol_cli.py, schemas/agent_usage.schema.json, tests/model_surface_roundtrip.py, tests/hint_roundtrip.py, tests/protocol_roundtrip.py)

## Accomplishments

- `runtime.hint_context(session_data, q)` resolves the learner's most recent genuine wrong response, the Phase 6 permitted tier, picked option, and mode (or None), and `runtime.invoke_hint(session_file, retry=False)` is the ONE orchestration path: session/current-item resolution → `model_adapter.request_from_operation(operation=hint)` → `model_adapter.invoke` with `surfaces.settings.load_settings` → `tier_gate.evaluate_candidate` on any candidate → `learner_payload` on pass or the `runtime.authored_hint(q, tier)` fallback on drop/unavailable → one `evidence.model_interaction_event` (evidence-only) → the typed `{"status", "generated", "authored", "interaction_id", "evidence"}` payload with no reason code (D-08).
- Idempotency and retry lineage are structural: interaction ids are uuid4 hex, the evidence dedupe (hash over session_id + interaction_id) makes at most one generation per interaction id, and `retry=True` mints a child id whose `parent_interaction_id` references the most recent interaction for the session/item (D-12).
- `runtime.invoke_rubric_review(session_file)` requires a short current item with a still-pending live response, builds the rubric_review request from the item's rubric points, gates the candidate (rubric_proposal shape, gate tier 5 with correct/model always protected), appends the interaction event and, on pass, the `mark_proposal_event` linked to the response and interaction, and returns `{"status": "pending", "points": [...]}`; every other state is a named refusal with no evidence write (D-13/D-14).
- `cmd_mark` accepts a human proposal through `--proposal <event_id>` and through `"proposal"` keys in `--marks` batch entries; every entry resolves (proposal → its response event) before any append, so an unknown proposal id anywhere aborts the batch with nothing written (D-25 batch-accept ergonomics).
- The suggestion surface reads `suggestion_reveal` from settings and renders a suggestion only as the pending token — never a number, fraction, check, or cross glyph (D-22); `render_suggestion` is the single helper and no auto-accept flag exists anywhere.
- The agent usage contract (`schemas/agent_usage.schema.json`, x-itembank-version 1, closed object, SUPPORTED schema keywords only) declares permissions, prohibitions, disclosure limits, retry rules (one attempt, explicit retry, parent-linked), manual-grading rules (marker human; self_mark|batch_mark), and forbidden inferences; `itembank usage` prints it byte-for-byte and `itembank schema --all` serves it under `agent_usage` (MODEL-04).

## Task Commits

Each task was committed atomically, tests first:

1. **Task 1: hint orchestration** - `124541b` (test) + `e2aee2d` (feat)
2. **Task 2: rubric review + human-only accept** - `5aab199` (test) + `afcb1bf` (feat)
3. **Task 3: agent usage contract** - `75f7125` (test) + `2cd9835` (feat)

**Plan metadata:** `docs(08-04): complete model surface commands plan` (final commit, includes SUMMARY.md + STATE.md)

## Files Created/Modified

- `runtime.py` - `hint_context`, `invoke_hint`, `invoke_rubric_review`, interaction-id minting with parent linkage, `_interaction_fingerprint`, `_serializable_manifest`, `_backend_descriptors`
- `surfaces/session.py` - `do_hint(session_file, retry=False)` (+ legacy `stumped=None` sentinel), `cmd_hint`, `do_rubric_review`, `cmd_rubric_review`, `render_suggestion`
- `surfaces/cli.py` - `hint` (--session/--retry), `rubric-review`, and `usage` sub-parsers; `mark` gains `--proposal`/`--rubric`
- `surfaces/evidence_cli.py` - `cmd_mark` resolves proposal targets via `_resolve_proposal`, records `proposal_ref`, batch all-or-nothing extended
- `surfaces/protocol_cli.py` - `agent_usage` added to CONTRACTS, `cmd_usage` added, help text updated to seven documents
- `schemas/agent_usage.schema.json` - the machine-readable usage contract
- `tests/model_surface_roundtrip.py` - new CLI/orchestration fixtures (13 tests across the three tasks)
- `tests/hint_roundtrip.py` - Phase 6 CLI tracer updated to the model-hint command (deviation, see below)
- `tests/protocol_roundtrip.py` - `test_schema_command_output` expected contract set now includes `agent_usage` (deviation, see below)

## Decisions Made

- The runtime, not the surface, sequences adapter → gate → evidence → authored fallback for both hint and rubric review; surfaces only relay typed payloads and never accept a caller-supplied tier, profile, key, or marker.
- The CLI `hint` command is the model-orchestrated diagnostic hint; the Phase 6 explicit tier-reveal remains in the runtime teaching transition and the daemon's `/api/hint` until plan 08-05 rewires that route.
- Rubric suggestions are pending-only; the only accept paths are the learner's explicit self-mark and the reviewer's explicit human batch accept, both through the existing `mark_event` with `proposal_ref`.
- The agent usage contract is a published, closed schema — no invented performance figures and no secret reference format beyond env-var names (D-19).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Phase 6 CLI hint tracer and schema --all contract-set tests updated**
- **Found during:** Task 1 (CLI hint parser) and Task 3 (CONTRACTS)
- **Issue:** The plan repurposes the CLI `hint` command from the Phase 6 positional/`--stumped` tier-reveal to the model-orchestrated `--session/--retry` command, which necessarily invalidates `tests/hint_roundtrip.py::test_cli_hint_tracer` (it invoked `itembank hint SESSION` / `--stumped`); and adding `agent_usage` to `protocol_cli.CONTRACTS` necessarily invalidates `tests/protocol_roundtrip.py::test_schema_command_output`'s exact six-name assertion. The plan's `files_modified` list omitted these two test files, but its own verification requires the suite to stay green.
- **Fix:** `test_cli_hint_tracer` now drives the model hint (typed unavailable + parent-linked retry) while keeping the wrong-hold/advance/report flow, and `test_schema_command_output` expects the seven-name contract set including `agent_usage`.
- **Files modified:** tests/hint_roundtrip.py, tests/protocol_roundtrip.py
- **Verification:** `python tests/hint_roundtrip.py`, `python tests/protocol_roundtrip.py`
- **Committed in:** e2aee2d, 2cd9835

**2. [Rule 2 - Missing Critical] Daemon Phase 6 `/api/hint` kept working via a `stumped=None` sentinel**
- **Found during:** Task 1 (surfaces/session.py `do_hint`)
- **Issue:** `surfaces/daemon.py` (out of this plan's file scope) calls `session.do_hint(path, stumped=...)` for the quiz page's "I'm stumped" control. A clean `do_hint(session_file, retry=False)` would break that route at runtime until plan 08-05 rewires it.
- **Fix:** `do_hint(session_file, retry=False, stumped=None)` — the CLI path passes `stumped=None` (model orchestration), while the daemon's real bool routes to the Phase 6 `do_action` reveal. Documented in the docstring as a legacy shim removed by 08-05.
- **Files modified:** surfaces/session.py
- **Verification:** `python tests/hint_roundtrip.py` (includes `test_api_hint_and_renderer_meta` exercising /api/hint end to end)
- **Committed in:** e2aee2d

**3. [Verification deviation - the plan's `schema_validate.py --all` is not this repo's CLI]**
- **Found during:** final verification
- **Issue:** The plan's `<verification>` and Task 3 `<verify>` list `python schema_validate.py --all`, but that is not a CLI this repo ships; `schema_validate.py` is a two-argument validator.
- **Fix:** Ran `python itembank.py schema --all` (parses, includes all seven contracts), `python tests/protocol_roundtrip.py`, and `test_schema_uses_supported_keywords_only()` from `tests/model_gate_roundtrip.py` (green), plus `python tests/model_surface_roundtrip.py`. Recorded here as the planned deviation.
- **Verification:** `python itembank.py schema --all`, `python tests/protocol_roundtrip.py`, `python tests/model_gate_roundtrip.py`

---

**Total deviations:** 3 (2 auto-fixed issues, 1 verification deviation)
**Impact on plan:** All necessary for correctness and for the existing test/daemon contract; no scope creep.

## Issues Encountered

- **Known environment condition (not fixed):** in-repo `python tests/evidence_roundtrip.py` and `python tests/scoring_roundtrip.py` fail their structural one-writer/one-scorer scans because the pre-existing `.phase*-wt` git worktrees (including `.phase10-wt`, `.phase031-wt`, `.phase061-wt`, `.phase062-wt`, `.phase07-verify-tmp`, `.phase091-wt`, `.phase11-wt`) ship second `evidence.py`/`runtime.py` files. Both tests pass in a clean copy of the tree that excludes `.phase*-wt` (verified in /tmp). Nothing under the worktrees was touched.
- The bank parser lowercases item ids (`q1`, not `Q1`); the rubric-review fixtures resolve the item ref dynamically from the response event so they are robust to that.
- The Phase 6 evidence fold reconstructs `highest_tier_unlocked` from response events whose `hint_tier` records only the shown tier, so after genuine wrong practice submissions the permitted tier is 0 (lesson pointer). The test bank carries tier-0 lesson content so the authored-fallback assertion is meaningful; this is existing Phase 6 behavior, not a regression.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 08-05 can relay `session.do_hint`/`do_rubric_review` through identifier-safe daemon routes and replace the legacy `stumped` shim with SURFACE_PARITY; the `usage` command and the `agent_usage` contract are already CLI-printable for any agent consumer.
- The hint/rubric-review orchestration, idempotency/retry lineage, and human-only accept paths are proven offline end to end; a provider-connected pass path only needs a configured profile.

---
*Phase: 08-model-adapter-interface-tier-gate-enforcement*
*Completed: 2026-08-11*

## Self-Check: PASSED

- Created files: `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-04-SUMMARY.md` exists; `schemas/agent_usage.schema.json` and `tests/model_surface_roundtrip.py` exist.
- Commits: 124541b, e2aee2d, 5aab199, afcb1bf, 75f7125, 2cd9835 (the six task commits) and the final `docs(08-04): complete model surface commands plan` metadata commit all present on main.
- Verification: `python tests/model_surface_roundtrip.py` green; `python tests/protocol_roundtrip.py` green; `python itembank.py schema --all` parses with all seven contracts; `test_schema_uses_supported_keywords_only()` green; `python tests/evidence_roundtrip.py` and `python tests/scoring_roundtrip.py` green in a clean copy excluding `.phase*-wt` (known in-repo worktree condition).
