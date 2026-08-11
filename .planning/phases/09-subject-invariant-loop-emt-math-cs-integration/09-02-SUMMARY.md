---
phase: 09-subject-invariant-loop-emt-math-cs-integration
plan: 02
subsystem: settings
tags: [subject-profiles, settings-registry, lesson-layout, fourth-profile, ast-guard]

requires:
  - phase: 09-subject-invariant-loop-emt-math-cs-integration (09-01)
    provides: subjects.validate_registry/select_profile/session_profile, DEFAULT_PROFILE, PROFILE_SCHEMA_VERSION
  - phase: 02-daemon-consolidation-settings-foundation
    provides: settings schema conventions (closed object, required, per-key default/x-itembank-phase), defaults_from_schema, merge_over_defaults, load_settings
provides:
  - Required top-level subject_profiles settings group (version + closed entries; lesson_layout enum folded from Phase 3.1 D-04)
  - Shipped emt/math/cs entries in the schema default and checked-in itembank.json
  - subjects.load_registry(base) over validated settings; temporary REGISTRY constant removed
  - THIS_PHASE advanced to 9 so `itembank config` reports the group active
  - Executable configuration-only fourth-profile proof (LOOP-05/D-15) and a precise AST dispatch guard
affects: [09-04 math assets, 09-05 runnable-code clients + fixtures, Phase 10]

actuals:
  tokens: 0
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - Settings schema is the source of truth; defaults_from_schema mirrors it into itembank.json and missing keys
    - Registry validation stays in subjects.validate_registry; the schema validates the shipped entries, the open entries object lets a fourth profile in, and closed-shape validation catches it

key-files:
  created:
    - .planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-02-SUMMARY.md
  modified:
    - schemas/settings.schema.json
    - itembank.json
    - subjects.py
    - surfaces/settings.py
    - surfaces/session.py
    - schemas/session.schema.json
    - tests/subject_loop_roundtrip.py
    - tests/config_roundtrip.py

key-decisions:
  - "The CS entry's `check` verifier id and `check` allowed item type are registry DATA declared by this plan; Phase 5 owns the one scoring implementation and 09-05 routes CS submissions to it. This resolves the PRE-FLIGHT cross-phase contract: the id string is pinned to `check`."
  - "The shipped entries are inlined in the settings schema (no $refs): defaults_from_schema cannot resolve $refs, and a $ref'd entry would have collapsed to a null default. The entries object stays open so a fourth profile is legal configuration; validate_registry performs the closed-shape check the schema cannot express for unknown keys."
  - "lesson_layout (separate|inline) folded from Phase 3.1 D-04: EMT and Math default separate, CS inline; added to the profile shape, the session snapshot contract, and the conservative default."
  - "THE_PHASE advances to 9: model_backend and suggestion_reveal (Phase 8) become active in the config table; the config roundtrip's inert-count and inert-group assertions were updated to the new discovery contract."

patterns-established:
  - "load_registry(base) is the one boundary through which known subjects enter the runtime; do_start and the legacy fill read it from the bank's own directory, so a fourth profile works from bank-adjacent settings with zero production edits."
  - "The AST guard flags only if/match nodes that COMPARE against a subject-id literal (docstring/message mentions are not dispatch); surfaces are checked for all three ids, root modules for emt/cs (math is also a capability token in subjects.py)."

requirements-completed: [LOOP-01, LOOP-05]

coverage:
  - id: D1
    description: "The versioned subject-profile registry ships as required subject_profiles settings; schema defaults, a missing settings file, and checked-in itembank.json expose structurally identical EMT/Math/CS registries, each carrying the lesson_layout enum (EMT/Math separate, CS inline)."
    requirement: LOOP-01
    verification:
      - kind: unit
        ref: "tests/subject_loop_roundtrip.py#test_settings_registry_parity"
        status: pass
    human_judgment: false
  - id: D2
    description: "Malformed registries fail before selection: unsupported verifiers and extra keys on known entries surface as named settings exits through the schema; an unknown fourth entry with a bad verifier fails closed-shape validation in validate_registry."
    requirement: LOOP-01
    verification:
      - kind: unit
        ref: "tests/subject_loop_roundtrip.py#test_load_registry_rejects_malformed"
        status: pass
    human_judgment: false
  - id: D3
    description: "A fourth subject enters the selector from temporary configuration only -- the same keys and version semantics as the shipped profiles -- and the shared do_start resolves and persists it from bank-adjacent settings (LOOP-05/D-15)."
    requirement: LOOP-05
    verification:
      - kind: integration
        ref: "tests/subject_loop_roundtrip.py#test_fourth_profile_is_configuration_only"
        status: pass
    human_judgment: false
  - id: D4
    description: "No production comparison/dispatch branch keyed by the shipped subject ids exists in surfaces or root application modules; the precise AST guard passes."
    requirement: LOOP-05
    verification:
      - kind: unit
        ref: "tests/subject_loop_roundtrip.py#test_no_subject_dispatch_in_surfaces"
        status: pass
    human_judgment: false
  - id: D5
    description: "itembank config reports subject_profiles as read by Phase 9 and publishes the closed entry contract."
    requirement: LOOP-01
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py (config table + phase-9 discovery assertions)"
        status: pass
    human_judgment: false

verification-runs:
  - command: "python tests/subject_loop_roundtrip.py"
    exit: 0
  - command: "python tests/config_roundtrip.py"
    exit: 0
  - command: "python tests/protocol_roundtrip.py"
    exit: 0
  - command: "python tests/agent_roundtrip.py"
    exit: 0
  - command: "python tests/lesson_roundtrip.py"
    exit: 0
  - command: "python tests/hint_roundtrip.py"
    exit: 0
  - command: "python tests/scoring_roundtrip.py"
    exit: 0
  - command: "python tests/evidence_roundtrip.py"
    exit: 0
  - command: "python tests/selection_roundtrip.py"
    exit: 0
  - command: "python tests/serve_roundtrip.py"
    exit: 0
  - command: "python tests/daemon_roundtrip.py"
    exit: 0
  - command: "python tests/packaging_roundtrip.py"
    exit: 1
    notes: "Environment-blocked at the Phase 13-03 onedir sidecar handshake (Windows PE exec unavailable from this WSL bash; cmd/powershell blocked by the approval gate). The pyz portion passes, including the staged subjects.py and the updated settings schema."

duration: 55min
completed: 2026-08-11
status: complete
---

# Phase 9 Plan 02: Versioned Subject-Profile Registry and Configuration-Only Extension

**The tracer's subject-profile seam becomes one validated settings contract, and LOOP-05 gets an executable configuration-only proof**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-11T03:15:00Z (approx)
- **Completed:** 2026-08-11T04:10:00Z (approx)
- **Tasks:** 2 (registry publication + fourth-profile proof; both TDD)
- **Files modified:** 9

## Accomplishments
- `subject_profiles` is a required, versioned settings group with `version` and a closed `entries` contract; the shipped emt/math/cs entries are inlined in the schema (so `defaults_from_schema` mirrors them into missing keys and `itembank.json`), and the entries object stays open so a fourth subject is configuration.
- Every entry's `lesson` object carries the `lesson_layout` enum (`separate` | `inline`) folded from Phase 3.1 D-04: EMT and Math default `separate`, CS `inline`. The same key joined the profile shape, the conservative default, and the session snapshot contract.
- `subjects.load_registry(base)` is the one settings-backed boundary; the temporary `REGISTRY` constant is gone, and `do_start`/legacy-fill read the registry from the bank's own directory. `THIS_PHASE` advanced to 9.
- The fourth-profile proof appends `fourth` to temporary settings, loads it through the public loader, resolves it from a `fourth:` bank through `select_profile` AND `do_start` (bank-adjacent settings), and verifies snapshot-shape parity with the shipped profiles.
- The AST dispatch guard is now precise (flags only comparisons against subject-id literals, not message/docstring mentions) and covers surfaces (all three ids) plus root application modules (emt/cs).

## Decisions
- **`check` verifier id pinned as registry data:** Phase 5's scorer has no id concept; 09-02 declares `verifier: "check"` and the `check` allowed type for CS, and 09-05 routes CS submissions to Phase 5's scorer. This closes the PRE-FLIGHT cross-phase contract without blocking on Phase 5 code.
- **Inlined entries, open entries object:** `$ref`s would break `defaults_from_schema` (it cannot resolve them), and a closed entries object would reject the fourth profile the plan requires. Schema validates the shipped entries; `validate_registry` validates everything, including unknown ids.
- **`config_roundtrip` updates:** the expected top-level key set gained `subject_profiles`; the inert-count floor moved 5→4 and model_backend/suggestion_reveal moved to the active set (Phase 8 groups are read by THIS_PHASE 9).
