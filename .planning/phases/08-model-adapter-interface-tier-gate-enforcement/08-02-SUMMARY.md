---
phase: 08-model-adapter-interface-tier-gate-enforcement
plan: 02
subsystem: model-adapter
tags: [adapter-interface, TRANSPORT_REGISTRY, hosted-cli, openai-compatible, profile-registry, secret-env, suggestion-reveal]

requires:
  - phase: 08-model-adapter-interface-tier-gate-enforcement
    provides: tier gate + 30-case adversarial corpus + single learner_payload constructor (08-01)
provides:
  - model_adapter.py: invoke(request, settings), resolve_profile re-export, TRANSPORT_REGISTRY (hosted_cli + openai_compatible + test-local stub), unavailable_result(code, message, interaction_id), request_from_operation bounded builder
  - schemas/model_adapter.schema.json: closed request/result envelope (additionalProperties false; no score, tier-decision, or accepted-mark field)
  - schemas/settings.schema.json: model_backend {active, profiles} array of fixed records + top-level suggestion_reveal enum (D-22), x-itembank-phase 8 on every key
  - itembank.json: disabled default model_backend (active "" + empty profiles) and suggestion_reveal "after-self-mark"
  - surfaces/settings.py: resolve_profile shared resolver (unique names, transport-required fields, defers unknown transports to TRANSPORT_REGISTRY)
  - tests/model_adapter_roundtrip.py: parity, full failure matrix, profile-registry validation, stub third backend, secret-env references, suggestion_reveal contract
  - tests/config_roundtrip.py: expected schema key set updated for suggestion_reveal
affects: [08-03 evidence events, 08-04 gate wiring + suggestion rendering, 08-06 end-to-end scenario, Phase 9+ subject-loop integration]

actuals:
  tokens: 15500
  tasks: 3
  commits: 7

tech-stack:
  added: []
  patterns:
    - One bounded invoke boundary normalizing any number of provider transports behind TRANSPORT_REGISTRY; callers never parse provider-native output (D-01/D-02, MODEL-02)
    - Array-of-records profile registry under the SUPPORTED keyword subset (RESEARCH Pitfall 3); unique names and transport-required fields enforced by a shared runtime resolver, never the schema
    - Credentials resolved from os.environ[profile.secret_env] by name at invoke time; the value never enters settings, requests, results, logs, or evidence (D-03/D-15)
    - Every failure family converts to one typed unavailable result with a named adapter.* code; nothing raises (D-04, MODEL-03)
    - A third backend is a TRANSPORT_REGISTRY entry plus a config entry with zero tier-gate/evidence/prompt-assembly edits (D-27)

key-files:
  created:
    - model_adapter.py
    - schemas/model_adapter.schema.json
  modified:
    - schemas/settings.schema.json
    - itembank.json
    - surfaces/settings.py
    - tests/model_adapter_roundtrip.py
    - tests/config_roundtrip.py

key-decisions:
  - "model_backend is a named profile registry {active, profiles} of fixed records; the shipped default is disabled, so a fresh install never phones a provider."
  - "The shared resolver (surfaces/settings.resolve_profile) validates unique names and the two known transports' required fields; it defers unrecognized transport names to TRANSPORT_REGISTRY so a third backend needs no resolver edit (D-27), and an unregistered transport resolves to typed adapter.transport_unknown -- never a silent fallback."
  - "Credentials are resolved from os.environ[profile.secret_env] at invoke time only; the settings file stores the env-var name and never the value, enforced structurally by the profile schema's additionalProperties false."
  - "suggestion_reveal ships all three enum values with after-self-mark as the default (D-22)."
  - "Transport-required conditional fields (command for hosted_cli, endpoint for openai_compatible) cannot be expressed by the SUPPORTED keyword subset, so the resolver enforces them at read time, not the schema."

patterns-established:
  - "One closed request/result envelope, shared by every backend, with provider backend class (hosted|local) preserved only in private audit metadata (D-17)."
  - "set-then-sorted code tuples for ADAPTER_CODES, matching the SETTINGS_CODES/LINT_CODES structural precedent."
  - "A test-local stub registration proves third-backend extensibility end-to-end without touching production registry entries."

requirements-completed: [MODEL-01, MODEL-02, MODEL-03, MODEL-05, TEACH-04]

coverage:
  - id: D1
    description: "model_adapter.py exports invoke(request, settings), resolve_profile (re-exported from surfaces/settings), TRANSPORT_REGISTRY, and the typed unavailable_result builder; the hosted CLI and local OpenAI-compatible transports return the same normalized shape for the same request under a config-only switch, preserving backend class in private audit metadata (MODEL-02, D-17/D-18)."
    requirement: MODEL-02
    verification:
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_hosted_cli_roundtrip"
        status: pass
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_openai_parity_and_config_switch"
        status: pass
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_stable_replay"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every failure family -- disabled profile, missing executable, nonzero exit, timeout, HTTP/URL error, malformed JSON, oversized output, provider refusal, invalid request -- converts to one typed unavailable result with a named adapter.* code and never raises; the authored hint ladder stays usable afterwards (MODEL-03, D-04)."
    requirement: MODEL-03
    verification:
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_failure_matrix_typed_unavailable"
        status: pass
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_missing_executable_and_nonzero_exit"
        status: pass
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_authored_fallback_after_unavailable"
        status: pass
    human_judgment: false
  - id: D3
    description: "The request/result contract (schemas/model_adapter.schema.json) is closed: additionalProperties false everywhere, a bounded payload builder, and no score, tier-decision, or accepted-mark field anywhere -- the model never scores or writes accepted evidence from this boundary (MODEL-05); the adapter never imports or writes evidence."
    requirement: MODEL-05
    verification:
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_request_envelope_and_unknown_field"
        status: pass
      - kind: unit
        ref: "tests/model_adapter_roundtrip.py#test_adapter_never_touches_evidence"
        status: pass
    human_judgment: false
  - id: D4
    description: "schemas/settings.schema.json defines model_backend {active, profiles} as an array of fixed records (additionalProperties false, per-field type/range, x-itembank-phase 8 on every key) plus the top-level suggestion_reveal enum; the schema uses only schema_validate SUPPORTED keywords and round-trips through load_settings and itembank config."
    requirement: MODEL-01
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_schema_names_every_project_key"
        status: pass
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_suggestion_reveal_enum_and_default"
        status: pass
    human_judgment: false
  - id: D5
    description: "Invalid profile registries are typed reasons, never a silent fallback: duplicate names and missing transport-required fields resolve to settings.invalid_value, an unknown active name to adapter.profile_unknown, and a schema-invalid registry is rejected by load_settings with a named settings.* code (RESEARCH Pitfall 3, T-08-13)."
    requirement: MODEL-01
    verification:
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_profile_registry_validation"
        status: pass
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_load_settings_rejects_bad_registry"
        status: pass
    human_judgment: false
  - id: D6
    description: "A third backend is a new adapter module plus a config entry: a test-local stub registered in TRANSPORT_REGISTRY routes end-to-end through the same invoke call with zero edits to tier-gate, evidence, or prompt-assembly code, and its result envelope carries no score/tier/accepted field (D-27, MODEL-05)."
    requirement: MODEL-05
    verification:
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_stub_third_backend_registration"
        status: pass
    human_judgment: false
  - id: D7
    description: "Credentials are resolved from os.environ[profile.secret_env] by name at invoke time, never stored inline in itembank.json and never present in any request, result, log, or evidence field; the shipped default config is disabled (active \"\" and empty profiles), so a fresh install never phones a provider (D-03/D-15, T-08-11)."
    requirement: MODEL-01
    verification:
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_secrets_from_env_never_inline"
        status: pass
    human_judgment: false
  - id: D8
    description: "suggestion_reveal validates to the three enum values (after-self-mark default, before-self-mark, after-mark), is x-itembank-phase 8, and reads back through load_settings and the itembank config table (D-22)."
    requirement: TEACH-04
    verification:
      - kind: integration
        ref: "tests/model_adapter_roundtrip.py#test_suggestion_reveal_enum_and_default"
        status: pass
      - kind: integration
        ref: "tests/config_roundtrip.py#test_config_no_args_prints_table"
        status: pass
    human_judgment: false
  - id: D9
    description: "The core loop is unchanged: scoring, evidence, and the protocol/schema contract all pass with the new settings schema (one scorer, one append_event writer, all published contracts validate)."
    requirement: MODEL-03
    verification:
      - kind: integration
        ref: "tests/scoring_roundtrip.py (clean-copy run excluding the pre-existing .phase10-wt worktree)"
        status: pass
      - kind: integration
        ref: "tests/evidence_roundtrip.py (clean-copy run excluding the pre-existing .phase10-wt worktree)"
        status: pass
      - kind: integration
        ref: "tests/protocol_roundtrip.py"
        status: pass
    human_judgment: false

duration: ~40min (continuation close-out of prior executor's Tasks 1-2)
completed: 2026-08-11
status: complete
---

# Phase 08 — Plan 08-02: One model-adapter interface, a named profile registry, secret-env credentials, and the third-backend stub proof

**A single bounded adapter boundary (invoke -> TRANSPORT_REGISTRY -> typed result) that makes hosted CLI and local OpenAI-compatible providers the same code path behind a config-only switch, with a named {active, profiles} settings registry, secrets resolved from environment variables by name, and a test-proven third-backend registration that requires zero tier-gate, evidence, or prompt-assembly edits.**

## Performance

- **Duration:** ~40 min (continuation close-out of prior executor's Tasks 1-2)
- **Started:** 2026-08-10 (Tasks 1-2 by prior executor)
- **Completed:** 2026-08-11
- **Tasks:** 3/3
- **Files modified:** 7 (2 created, 5 modified)

## Accomplishments
- One `invoke(request, settings)` boundary normalizes the hosted CLI (subprocess, shell=False) and local OpenAI-compatible (urllib) transports; switching the active profile is a settings-only change and the normalized result shape is identical modulo backend class (MODEL-02, D-17/D-18).
- Every provider failure — disabled profile, missing executable, nonzero exit, timeout, HTTP/URL error, malformed JSON, oversized output, refusal, invalid request — converts to one typed `unavailable_result` with a named `adapter.*` code; nothing raises and the authored hint ladder stays usable (MODEL-03, D-04).
- `schemas/settings.schema.json` replaces the old single-object `model_backend` with `{active, profiles}` — an array of fixed profile records (name, transport, command|endpoint, model, timeout, output cap, context window, secret_env) — and adds the top-level `suggestion_reveal` enum defaulting to `after-self-mark` (D-22). The shipped default is disabled, so a fresh install never phones a provider.
- The shared profile resolver (`surfaces/settings.resolve_profile`, re-exported by `model_adapter`) validates unique names and transport-required fields at read time (settings.invalid_value / adapter.profile_unknown), and defers unrecognized transport names to `TRANSPORT_REGISTRY` — which is what lets a stub third backend route with no resolver edit (D-27).
- Secrets are resolved from `os.environ[profile.secret_env]` at invoke time only; the settings file stores the env-var *name*, never the value, and the value never reaches requests, results, logs, or evidence (D-03/D-15) — asserted with a `flatten()` scan over request and result bodies.

## Task Commits

Each task was committed atomically (TDD: test -> feat):

| # | Commit | Message |
|---|--------|---------|
| 1 | `9e331a0` | `test(08-02): tracer — hosted CLI roundtrip, request envelope, executable-missing/refusal` |
| 2 | `3637057` | `feat(08-02): tracer — invoke boundary, closed request/result schema, hosted_cli transport` |
| 3 | `f7274bb` | `test(08-02): parity — hosted/local same-shape under config switch, full failure matrix, authored fallback` |
| 4 | `dece792` | `feat(08-02): parity — openai_compatible transport, hosted/local same-shape under a config-only switch` |
| 5 | `0962c5f` | `test(08-02): profile registry validation, stub third backend, secret env references, suggestion_reveal contract` |
| 6 | `a2d52cc` | `feat(08-02): settings schema — named profile registry {active, profiles}, suggestion_reveal; resolver defers unknown transports to the registry` |

**Plan metadata:** final `docs(08-02)` commit (SUMMARY.md, STATE.md, ROADMAP.md) via the gsd-tools commit verb.

## Files Created/Modified
- `model_adapter.py` - The single typed boundary: request validation, profile resolution, TRANSPORT_REGISTRY routing, per-profile timeout/output-cap enforcement, env-resolved credentials
- `schemas/model_adapter.schema.json` - Closed request/result envelope (additionalProperties false, no score/tier/accepted field)
- `schemas/settings.schema.json` - `model_backend` `{active, profiles}` fixed-record array + top-level `suggestion_reveal` enum
- `itembank.json` - Disabled default `model_backend` and `suggestion_reveal: "after-self-mark"`
- `surfaces/settings.py` - `resolve_profile` shared resolver (unique names, transport-required fields, defers unknown transports to the registry)
- `tests/model_adapter_roundtrip.py` - Task 1-3 behavior tests: parity, failure matrix, profile registry, stub third backend, secret env, suggestion_reveal
- `tests/config_roundtrip.py` - Expected schema key set updated for `suggestion_reveal` (see Deviations)

## Decisions Made
- `model_backend` is a named profile registry, not a single vendor object; the shipped default is disabled (active "" + empty profiles).
- The resolver lives in `surfaces/settings.py` (shared by config and adapter) and is re-exported from `model_adapter.py` so callers see one public boundary.
- Unknown transport names are deferred to `TRANSPORT_REGISTRY`, not rejected by the resolver — required for D-27's third-backend proof; an unregistered transport still resolves to typed `adapter.transport_unknown`.
- Credentials are environment-referenced by `secret_env`; the profile schema's `additionalProperties false` structurally forbids a secret-value field in settings.
- `suggestion_reveal` ships all three enum values with `after-self-mark` as the default (D-22).

## Deviations from Plan

### Auto-fixed Issues

**1. Verification command substitution — `python schema_validate.py --all` does not exist in this repo's CLI**
- **Found during:** plan verification list (Task 3 `<verify>` and `<verification>`)
- **Issue:** `schema_validate.py` takes a schema path and has no `--all` mode; the plan's verification line cannot run as written.
- **Fix:** Used `python itembank.py schema --all` (the repo's published-schema emitter, passes) plus `python tests/protocol_roundtrip.py`, whose `test_schema_command_output` runs `schema_validate.check_schema` over every published contract — the SUPPORTED-keywords gate the plan's `schema_validate.py --all` line was after.
- **Files modified:** none
- **Verification:** `python itembank.py schema --all`, `python tests/protocol_roundtrip.py`, `python tests/model_adapter_roundtrip.py` all pass
- **Committed in:** n/a (verification substitution, no code change)

**2. `tests/config_roundtrip.py` expected-key set updated for the new top-level `suggestion_reveal` key**
- **Found during:** Task 3 (schema change)
- **Issue:** The plan's `files_modified` list does not name `tests/config_roundtrip.py`, but its own verification list requires `python tests/config_roundtrip.py` to pass, and `test_schema_names_every_project_key` asserts the exact top-level key set. Adding `suggestion_reveal` to the schema changed that set, so the test would go red.
- **Fix:** Added `suggestion_reveal` to the test's expected key set (and refreshed its docstring). Test-only change; no production behavior altered.
- **Files modified:** tests/config_roundtrip.py
- **Verification:** `python tests/config_roundtrip.py` -> "config contract: ok (... all 6 dotted codes reachable)"
- **Committed in:** `a2d52cc` (part of the Task 3 feat commit)

**3. Resolver behavior refinement — unrecognized transports are deferred to `TRANSPORT_REGISTRY`, not rejected**
- **Found during:** Task 3 (D-27 stub registration)
- **Issue:** The resolver committed with Tasks 1-2 rejected any transport outside `hosted_cli|openai_compatible` with `settings.invalid_value`. That would block the plan's own D-27 acceptance criterion ("the stub routes end-to-end with no edits outside model_adapter's registry"), because the stub's transport name is not one of the two shipped transports.
- **Fix:** `resolve_profile` now validates unique names and the two known transports' required fields, and defers any other transport name to the adapter's registry lookup. A registered stub routes; an unregistered transport resolves to typed `adapter.transport_unknown` in invoke — still "never a silent fallback", still a typed unavailable result.
- **Files modified:** surfaces/settings.py (docstring + the transport check)
- **Verification:** `python tests/model_adapter_roundtrip.py` -> "model adapter: ok (... profile registry validation, stub third backend ...)"
- **Committed in:** `a2d52cc` (part of the Task 3 feat commit)

**4. Environmental — the pre-existing `.phase10-wt` git worktree breaks the in-repo one-scorer/one-writer scans**
- **Found during:** verification (`python tests/scoring_roundtrip.py`, `python tests/evidence_roundtrip.py`)
- **Issue:** The `.phase10-wt` git worktree (branch `phase10`, created after 08-01's summary removed it, carrying 13 uncommitted WIP files from parallel Phase 10 work) ships a second `runtime.py`/`evidence.py` inside the repo tree, so `scoring_roundtrip`'s "exactly one scorer" and `evidence_roundtrip`'s "exactly one append_event writer" structural scans fail in-repo.
- **Fix:** Left the worktree untouched (it holds another phase's uncommitted work; the instruction was to not modify pre-existing files). Proved the core loop is unchanged by running both tests against a clean copy of the tree without `.phase10-wt`: both pass ("scoring contract: ok (6 items, one scorer)", "evidence contract: ok (...)").
- **Files modified:** none
- **Verification:** clean-copy runs of `python tests/scoring_roundtrip.py` and `python tests/evidence_roundtrip.py` pass; in-repo runs fail only on the worktree copy
- **Committed in:** n/a (environment condition, no code change)

---

**Total deviations:** 4 (1 verification-command substitution, 1 test-contract update, 1 resolver behavior refinement, 1 environment condition)
**Impact on plan:** All necessary for correctness and for the plan's own verification list; no scope creep. `model_adapter.py`, `tier_gate.py`, `evidence.py`, and `runtime.py` behavior was not changed by these fixes.

## Issues Encountered
- `.phase10-wt` (a git worktree for parallel Phase 10 work, recreated after 08-01 removed it) silently breaks the in-repo scoring/evidence structural scans; documented in Deviation 4 and proven green via clean-copy runs.
- This shell drops variable assignments, so shell loop variables could not be used for the clean-copy test sweep; each test was invoked explicitly.

## User Setup Required

None - no external service configuration required. The shipped `model_backend` is disabled and credentials, when a user enables a backend, come from the environment variable named by `secret_env`.

## Next Phase Readiness
- `model_adapter.invoke` and the closed request/result contract are ready for 08-03's evidence event builders and 08-04's gate wiring to call.
- The named profile registry + `suggestion_reveal` setting are ready for the 08-04/08-05 surfaces to read (D-22).
- The D-27 stub proof shows any future provider (including the local Qwen target) is a new adapter module plus a config entry.
- The environment-referenced credential rule is the standing contract for every future backend.

---

*Phase: 08-model-adapter-interface-tier-gate-enforcement*
*Completed: 2026-08-11*

---

# Self-Check

- [x] Task 1: hosted CLI round-trips through invoke with the same interaction_id and backend_class "hosted"; a request with an unknown field and a missing executable are typed unavailable with named codes; no exception escapes invoke.
- [x] Task 2: hosted and local transports produce the same normalized shape under a config-only switch; every failure-matrix row returns unavailable with a named adapter.* code; scoring/evidence core loop proven unchanged (clean-copy run).
- [x] Task 3: {active, profiles} with unique names resolve; duplicate names / unknown active / missing transport-required fields are typed reasons, never silent fallback; a stub third backend routes through TRANSPORT_REGISTRY with zero tier-gate/evidence/prompt-assembly edits (D-27); secrets come from the environment by name and never appear in requests, results, logs, or evidence; shipped default is disabled; suggestion_reveal validates to three enum values with after-self-mark default (D-22).
- [x] Verification list green: `python tests/model_adapter_roundtrip.py`, `python tests/config_roundtrip.py`, `python itembank.py schema --all`, `python tests/protocol_roundtrip.py` in-repo; `python tests/scoring_roundtrip.py` + `python tests/evidence_roundtrip.py` green in a clean copy (in-repo blocked only by the pre-existing `.phase10-wt` worktree).
- [x] Scratch cleanup: untracked `fake_hosted_unused.py` deleted; no pre-existing untracked/modified files touched.
- [x] SUMMARY.md written, STATE.md updated, roadmap progress updated, final docs commit created.

**Self-Check: PASSED**
