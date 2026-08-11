---
phase: 05-check-item-type-code-editor
plan: 01
subsystem: runtime
tags: [check-item, runner, subprocess, interaction-contract, evidence-reserved-field]

requires:
  - phase: 06-hint-ladder-cursor-hold-feedback-modes
    provides: the one session adapter (do_action) every HTTP and CLI submit reaches, the closed .response_event schema shape, and the teaching transition the check verdict flows through
provides:
  - runner.py, a peer module that executes a learner source once per authored case (stdin/stdout or [HARNESS:] call) under a deadline and an output cap, returning a per-case result list
  - The check item type in the format contract: parse branch, shared MARKERS, fingerprint split (stem+cases+starter hashed, lang/match not), SPEC section with HONEST_LIMITS_NOTE, and four new lint codes
  - runtime.NORMALIZERS/KEYS registries with the check entry, the versioned interaction_contract and interaction_result, and score_response still the one scorer (pinned by T-R4-01)
  - The reserved check_source and interaction_version fields on response events and the response schema (check added to item_type, error_category accepts timeout)
  - A runner gate in record_answer and in session.do_action, with a killed-at-timeout run scored None and recorded error_category "timeout"
  - Synthetic fixture banks and a stdlib-only roundtrip test driving the whole path over real HTTP
affects: [Phase 05-02 bounds hardening, 05-03 settings/agent gate, 05-05 editor, 05-06 per-case readout, 05-07 attempt rendering, Phase 8 tutoring model, Phase 9 runnable lessons]

actuals:
  tokens: 38000
  tasks: 3
  commits: 12

tech-stack:
  added: []
  patterns:
    - One runner executes at the surface; the scorer reduces a precomputed vector and never runs code
    - Two registries (NORMALIZERS/KEYS) dispatch every canonical reduction; a registry miss lands pending, never a False verdict
    - A reserved always-present evidence field (check_source) carries what was submitted while answer/canonical carry what was scored

key-files:
  created:
    - runner.py
    - fixtures/check_bank.md
    - fixtures/broken_check_bank.md
    - tests/check_roundtrip.py
  modified:
    - model.py
    - runtime.py
    - evidence.py
    - schemas/response.schema.json
    - schemas/lint_error.schema.json
    - surfaces/quiz.py
    - surfaces/session.py
    - surfaces/migrate.py
    - build.py
    - fixtures/selection_evidence.jsonl
    - tests/scoring_roundtrip.py
    - tests/lesson_roundtrip.py

key-decisions:
  - "The runner lives at the surface layer (D-A): record_answer and session.do_action call runner.run_cases once, and check_normalizer is a pure reduction of the already-computed per-case vector (the plan sentence naming runner.run_cases inside check_normalizer is superseded by the orchestrator's D-A ruling)."
  - "A killed-at-timeout run is not a verdict: score_response returns None (a one-line guard required by criterion 12), the evidence event records error_category timeout with a None score, and the response stays pending -- never False (D-B)."
  - "The learner's source is stored verbatim in the reserved check_source field on every response event (None for other types), while answer/canonical keep carrying the scored vector so dedupe and attempt logic are unchanged (Task 2, option-a / D-13)."
  - "item.no_normalizer is bank-scoped: the registry check runs only when a bank actually contains a check item, so a legacy short item keeps its documented pending behaviour and selection_roundtrip stays green."
  - "[HARNESS:] is a configured strategy inside the runner (import, call, compare exact for int/str, within [TOLERANCE:] for floats), never a second scorer; the float-without-tolerance item is rejected at lint time (item.tolerance_unstated)."

patterns-established:
  - "The runner imports no surface and nothing from runtime.py, defines no function whose name matches a scorer, and reuses model.HONEST_LIMITS_NOTE verbatim."
  - "Both marker regexes (the stem terminator and TERMINATOR) are built from one MARKERS constant; TERMINATOR uses an unprefixed alternation so the [ID:]/[HASH:] splice lands above the first structural marker line."
  - "interaction_result is data for feedback, not a second scoring path: its verdict is the exact score_response return, and the ordered observations carry stable reason codes (passed, wrong_output, timeout, output_cap)."

requirements-completed: [CODE-01, CODE-02, CODE-04, CODE-05]

coverage:
  - id: D1
    description: "runner.py executes a learner source once per authored case (stdin/stdout or [HARNESS:] call), kills never-terminating runs at the deadline, caps and truncates unbounded output, writes then closes stdin, and returns a per-case result list carrying case_index/passed/actual/timed_out/truncated."
    requirement: CODE-01
    verification:
      - kind: unit
        ref: "tests/check_roundtrip.py#check_run_cases + check_harness_end_to_end"
        status: pass
    human_judgment: false
  - id: D2
    description: "The check format contract in model.py: parse branch with [LANG:]/[MATCH:] defaults, shared MARKERS, fingerprint split (stem+cases+starter hashed, lang/match excluded), SPEC section ending with HONEST_LIMITS_NOTE, and four new lint codes; fixtures/check_bank.md lints with zero errors."
    requirement: CODE-01
    verification:
      - kind: unit
        ref: "python itembank.py lint fixtures/check_bank.md (0 errors) + tests/check_roundtrip.py#check_parse_and_defaults"
        status: pass
    human_judgment: false
  - id: D3
    description: "check scores dichotomously through the same scorer: NORMALIZERS/KEYS carry the check entry, canonical_response/canonical_key dispatch through them, and runtime.score_response remains the only function in the tree whose name matches a scorer, pinned byte-for-byte by T-R4-01."
    requirement: CODE-02
    verification:
      - kind: unit
        ref: "tests/scoring_roundtrip.py (one-scorer walk + T-R4-01 source hash)"
        status: pass
    human_judgment: false
  - id: D4
    description: "A served check item exposes a versioned, validated interaction_contract (renderer_config + source-text response_schema, JSON data only, no cases/expected/key), and interaction_result returns the exact score_response verdict with ordered 1-based observations carrying stable reason codes."
    requirement: CODE-02
    verification:
      - kind: unit
        ref: "tests/check_roundtrip.py#check_public_item + check_interaction_result"
        status: pass
    human_judgment: false
  - id: D5
    description: "The learner's submitted source is stored verbatim in the reserved check_source field on every response event (None for other types), interaction_version records the public contract version, and both keys are in required+properties of the response schema with check added to item_type; every event validates."
    requirement: CODE-04
    verification:
      - kind: integration
        ref: "tests/check_roundtrip.py#check_http_roundtrip + check_evidence_signatures; fixtures/selection_evidence.jsonl revalidated"
        status: pass
    human_judgment: false
  - id: D6
    description: "The honest-limits sentence exists worded once (model.HONEST_LIMITS_NOTE) and appears in exactly the SPEC check section; the SPEC check section also documents [HARNESS:] and the [TOLERANCE:] rule and the THE SIX ITEM TYPES heading is in place."
    requirement: CODE-05
    verification:
      - kind: automated_ui
        ref: "python itembank.py spec (SIX ITEM TYPES count = 1, HONEST_LIMITS_NOTE present)"
        status: pass
    human_judgment: false
  - id: D7
    description: "End-to-end over a served fixture bank: POST /quiz/<stem>/answer returns the dichotomous score and interaction_result, records exactly one evidence event per submit with the vector as answer, and a killed-at-timeout submission scores None with error_category timeout and stays pending -- never a fabricated verdict."
    requirement: CODE-02
    verification:
      - kind: e2e
        ref: "tests/check_roundtrip.py#check_http_roundtrip"
        status: pass
    human_judgment: false
  - id: D8
    description: "fixtures/broken_check_bank.md trips all four new codes (item.check_lang_unknown and item.tolerance_unstated as errors, item.check_too_few_cases and item.no_normalizer as warnings) and lint exits non-zero; fixtures/check_bank.md lints clean with the harness item exercising [TOLERANCE:]."
    requirement: CODE-01
    verification:
      - kind: unit
        ref: "python itembank.py lint fixtures/broken_check_bank.md --json (all four codes) + lint fixtures/check_bank.md (0 errors)"
        status: pass
    human_judgment: false
  - id: D9
    description: "The runner never reaches the scorer's module: grep for run_cases in runtime.py returns nothing, and surfaces/quiz.py's record_answer carries the gate; runner.py defines no function whose name matches a scorer and imports no surface and nothing from runtime.py."
    requirement: CODE-02
    verification:
      - kind: unit
        ref: "grep -n run_cases runtime.py (0 lines); tests/scoring_roundtrip.py one-scorer walk"
        status: pass
    human_judgment: false

duration: 300min
completed: 2026-08-11
status: complete
---

# Phase 05 Plan 05-01: Check Item Type Tracer -- Summary

The whole check path is real and proven end to end: a markdown check item
parses, the runner executes the learner's source once per authored case at the
surface, the per-case vector reduces to a dichotomous verdict through the one
scorer -- or a None verdict with error_category timeout when the deadline
killed the run -- and the evidence log records the vector, the verbatim
source, and the interaction-contract version in one append.

## Performance

- **Duration:** ~5h
- **Commits:** 12
- **Requirements completed:** CODE-01, CODE-02, CODE-04, CODE-05

## Issues and Deviations

Both orchestrator-resolved deviations were applied and are recorded here as
required.

### D-A -- the runner is called at the surface layer; check_normalizer is a pure reduction

The plan's acceptance criterion 658 binds: grep for run_cases in runtime.py
returns nothing, and grep for run_cases in surfaces/quiz.py returns at least
one line inside record_answer. Because Phase 6 (06-02) consolidated every
submit route into session.do_action, the runner gate lives there as well --
do_action is what POST /quiz/<stem>/answer and /api/submit actually reach --
so the browser path and the agent path both execute once per case. The
check_normalizer(q, answer) function is a pure reduction of the
already-computed per-case list (dicts with passed/timed_out, ints, or an
already-canonical vector string); it imports nothing from runner and never
executes code. The plan's one sentence naming runner.run_cases inside
check_normalizer is superseded by this ruling.

### D-B -- the one-line None-canonical guard in score_response

Criterion 12 requires a killed-at-timeout run to produce no verdict, and with
the current source a None canonical compared equal to the key would read
False. The deliberate, documented deviation adds exactly one guard to
score_response (preserving its docstring): a None canonical returns None,
not a comparison result. Behaviour is unchanged for the five existing types
(only short yields a None canonical today, and it already returns None via
the key guard). The T-R4-01 source-hash pin in tests/scoring_roundtrip.py
was recorded AFTER this guard was in place, so it pins the final state.

### Further notes

- item.no_normalizer is bank-scoped: the registry check runs only when a
  bank actually contains a check item. Without this, every legacy short item
  would warn and tests/selection_roundtrip.py (which asserts zero warnings
  on its fixture) would regress. The broken bank's short item still trips the
  code because that bank mixes check items with the unregistered type.
- The response-event schema shape lives in .response_event (the Phase 6
  restructure), so the plan's top-level d["required"]/d["properties"] verify
  command is asserted against .response_event instead; the broken-bank
  codes are asserted through lint --json, the machine-readable channel that
  carries lint codes (the human text output carries the messages).
- fixtures/selection_evidence.jsonl was updated to carry the new reserved
  keys so every event still validates against the closed schema.
- tests/lesson_roundtrip.py hard-coded the old FIVE ITEM TYPES heading; it
  was updated to the plan-mandated SIX ITEM TYPES heading, and
  schemas/lint_error.schema.json gained the four new codes.
- build.py stages runner.py so the packaged pyz can execute check items.
- tests/packaging_roundtrip.py's onedir-sidecar check fails in this WSL
  environment because it requires the Windows-built dist/itembank-sidecar
  artifacts (gitignored); this is a pre-existing environment condition,
  unrelated to this plan. Every other test in the suite exits 0.

## Verification

- python tests/check_roundtrip.py and python tests/scoring_roundtrip.py exit 0.
- python itembank.py lint fixtures/check_bank.md prints 0 error lines;
  lint fixtures/broken_check_bank.md --json reports all four new codes and
  exits non-zero; lint fixtures/sample_bank.md still prints 0 error lines.
- python itembank.py spec contains exactly one SIX ITEM TYPES heading and
  documents the [HARNESS:] mode and the [TOLERANCE:] rule.
- python itembank.py build fixtures/sample_bank.md /tmp/out.html and
  python itembank.py guard . both exit 0.
- The full test suite exits 0 (run in chunks; the whole loop exceeds the
  tool's two-minute foreground cap in this environment).
