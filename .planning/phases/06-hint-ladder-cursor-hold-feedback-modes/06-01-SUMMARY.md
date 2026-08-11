---
phase: 06-hint-ladder-cursor-hold-feedback-modes
plan: 01
subsystem: runtime
tags: [teaching-transition, hint-ladder, feedback-modes, evidence, schema-v2]

requires:
  - phase: 03-lesson-format-in-app-reader
    provides: lesson_slug public item pointer consumed as tier 0
  - phase: 01-evidence-spine-protocol-foundation
    provides: append-only evidence, dedupe keys, live_events, mark events
provides:
  - One mode-keyed teaching_transition in runtime.py owning scoring, cursor, tier, disclosure, completion
  - Six fixed authored tiers with unavailable-slot semantics and response-specific tier 3
  - Version-2 session teaching_state with v1-to-v2 upgrade
  - Append-only hint events and hint_tier-bearing response events (null-vs-zero)
  - evidence.teaching_outcomes() deriving D-17 outcomes from live events
affects: [06-02 CLI/API/browser surfaces, Phase 7 selection, Phase 8 model hints, Phase 10 retention]

actuals:
  tokens: 2590
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - One pure runtime transition as the sole policy boundary; surfaces are clients of returned actions
    - Pure evidence fold (reconcile_teaching_state) repairs crash windows without replaying disclosure

key-files:
  created:
    - tests/hint_roundtrip.py
  modified:
    - runtime.py
    - evidence.py
    - schemas/session.schema.json
    - schemas/response.schema.json
    - schemas/report.schema.json
    - surfaces/session.py
    - surfaces/evidence_cli.py
    - itembank.py

key-decisions:
  - "Confirmed the v2 response/hint evidence contract at the Task 1 gate: integer-or-null hint_tier, hint events linked to response/attempt with tier/unlock-path, v1 reads kept while writers emit v2."
  - "A genuine wrong practice response unlocks (never shows) the next tier; hint/stumped reveal exactly one fixed tier; tier 0 is the lesson pointer and only becomes a hint event when actually shown."
  - "After the authored reveal (tier 5) is shown, the next submit action advances even on a repeat of the last canonical response (D-06: no manufactured attempts)."
  - "teaching_outcomes omits a fully-retracted item entirely (D-10) and never counts stumped as a wrong response."

patterns-established:
  - "teaching_transition(session, q, action, evidence_state) is a pure function returning next session + action; no renderer/observation parameter can reach it."
  - "evidence.hint_event() dedupes on (session, item, tier, unlock_path); response events record the highest tier actually shown."

requirements-completed: [TEACH-01, TEACH-02, TEACH-03, MODE-01, MODE-02, MODE-03, MODE-04, MODE-05, MODE-06]

coverage:
  - id: D1
    description: "Mode-keyed teaching transition: hold/advance/reveal_tier/defer_feedback/complete across practice, drill, diagnostic, exam; one tier unlocked per genuine wrong attempt; duplicates/empty unlock nothing."
    requirement: TEACH-01
    verification:
      - kind: unit
        ref: "tests/hint_roundtrip.py#test_practice_wrong_holds_and_unlocks_one_tier, test_practice_duplicate_and_empty_unlock_nothing, test_drill_reveals_and_advances, test_diagnostic_defers_until_completion, test_exam_defers_until_accepted_mark"
        status: pass
    human_judgment: false
  - id: D2
    description: "Six fixed authored tiers (lesson, objective, trap, rationale, discriminator, reveal) with unavailable-slot semantics and response-specific tier 3."
    requirement: TEACH-02
    verification:
      - kind: unit
        ref: "tests/hint_roundtrip.py#test_six_fixed_tiers_and_unavailable_slots, test_practice_tier_three_is_response_specific"
        status: pass
    human_judgment: false
  - id: D3
    description: "Version-2 session teaching_state with v1-to-v2 upgrade and evidence reconciliation repairing crash windows."
    requirement: MODE-01
    verification:
      - kind: unit
        ref: "tests/hint_roundtrip.py#test_v1_session_upgrades_to_v2, test_evidence_reconciliation_repairs_crash_window, test_session_schema_v2_contract"
        status: pass
    human_judgment: false
  - id: D4
    description: "Append-only hint events and hint_tier-bearing response events (null-vs-zero), schema-valid, with D-17 outcomes derived from live events after retractions and marks."
    requirement: TEACH-03
    verification:
      - kind: unit
        ref: "tests/hint_roundtrip.py#test_hint_event_contract_and_dedupe, test_response_event_v2_hint_tier_null_vs_zero, test_teaching_outcomes_from_live_events, test_retraction_suppresses_hints_through_live_events"
        status: pass
    human_judgment: false

duration: 95min
completed: 2026-08-11
status: complete
---

# Phase 6 Plan 01: Runtime Hint Ladder, Cursor-Hold and Feedback Modes

**One mode-keyed runtime teaching transition with six fixed authored tiers, versioned session teaching state, and append-only hint/tier evidence with live-event-derived report outcomes**

## Performance

- **Duration:** 95 min
- **Started:** 2026-08-11T00:20:00Z (approx)
- **Completed:** 2026-08-11T01:55:00Z (approx)
- **Tasks:** 3 (Task 1 decision gate confirmed; Tasks 2-3 implemented TDD)
- **Files modified:** 9

## Accomplishments
- `runtime.teaching_transition()` is now the sole authority for scoring, cursor movement, tier unlock/show, completion and disclosure; drill/practice/diagnostic/exam produce materially different actions (D-01/D-02/D-10..D-13).
- `HINT_TIERS` (lesson, objective, trap, picked-option rationale, discriminator, reveal) with `authored_hint()` returning explicit unavailable slots at the same index, and tier 3 resolving the latest picked option's distractor analysis (D-07/D-08/D-09).
- Sessions are v2 with per-item `teaching_state`; v1 sessions upgrade in place; `reconcile_teaching_state()` folds live evidence to repair crash windows without replaying disclosure.
- `evidence.hint_event()` / `hint_events()` / `teaching_outcomes()` implement the D-15/D-16/D-17 contract: response events record integer-or-null hint_tier, hint events link response/attempt/tier/unlock-path, and reports derive first-try/retry/tier/stumped/revealed/pending/unresolved outcomes from live events only.
- Published contracts bumped: session.schema.json v2 (teaching_state), response.schema.json v2 (closed hint event branch + integer-or-null hint_tier), report.schema.json gains teaching_outcomes.

## Task Commits

1. **Task 1: Preflight + confirm evidence contract** - user decision (confirm-contract), no code commit
2. **Task 2: TRACER - teaching transition, fixed tiers, resumable state** - `a38bac9` (test) + `5183927` (feat)
3. **Task 3: Live teaching outcomes and schema-valid reports** - `c08aa42` (feat)

## Files Created/Modified
- `runtime.py` - HINT_TIERS, FEEDBACK_POLICIES, authored_hint, teaching_transition, reconcile_teaching_state, v2 session upgrade
- `evidence.py` - hint_event/hint_events/teaching_outcomes, v2 response events, hint in KNOWN_EVENT_TYPES
- `schemas/session.schema.json` - v2 with teaching_state and teaching_record
- `schemas/response.schema.json` - v2 oneOf: response_event / hint_event / other_event
- `schemas/report.schema.json` - teaching_outcomes row shape
- `surfaces/session.py` - do_start writes v2 sessions
- `surfaces/evidence_cli.py` - objective-history payload stamped REPORT_VERSION (was EVENT_SCHEMA_VERSION)
- `tests/hint_roundtrip.py` - new Phase 6 roundtrip suite

## Decisions Made
- Confirmed the v2 evidence contract at Task 1 (user approved `confirm-contract`): integer-or-null `hint_tier`, hint events with response linkage and unlock path, v1 reads preserved.
- Wrong practice submits unlock but do not show; hint/stumped reveal exactly one fixed tier and append a hint event only when shown. This keeps disclosure observable and the ladder non-punitive.
- After the reveal is shown, any next submit advances (even a duplicate canonical), satisfying D-06 without manufacturing attempts.
- Fully-retracted items are omitted from teaching_outcomes entirely rather than reported unresolved, matching D-10's read-side suppression.

## Deviations from Plan
- **Task 3 auto-fix:** `surfaces/evidence_cli.py`'s objective-history payload used `EVENT_SCHEMA_VERSION` as its report stamp; bumping the event contract to v2 exposed the latent mismatch (it must describe the report, not the event). Fixed to `REPORT_VERSION`. `tests/evidence_roundtrip.py` and `tests/protocol_roundtrip.py` schema assertions were updated to the new `$defs.response_event` location.
- **Task 2/3 auto-fix:** `render_session_json` (a log-derived view) gained `teaching_state: {}` so it still validates against the v2 session contract without fabricating tiers it cannot know.

**Total deviations:** 2 auto-fixed (Rule 1/2 category)
**Impact on plan:** Necessary for the version bump to land coherently; no scope creep.

## Issues Encountered
- `tests/lesson_roundtrip.py` is red on `test_spec_only_bank_round_trips_new_constructs` -- this is the in-progress Phase 03.1-06 RED state (spec/lint grammar work), unrelated to Phase 6; the Phase 3 preflight pointer check that 06-01 requires passed.
- `tests/daemon_roundtrip.py`'s hostile-bank directory snapshot is flaky when run after `tests/serve_roundtrip.py` in one process (leftover temp dirs appear in the snapshot); reproduced at plain HEAD with no Phase 6 changes. Passes in isolation.
- The repo's `tmp/` probe-artifact directory (untracked, from an earlier session) makes `tests/evidence_roundtrip.py::test_one_writer` report a second `append_event` writer; pre-existing environment debris, not from this plan.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- 06-01 contract is green (`python tests/hint_roundtrip.py`; protocol, evidence, serve, scoring, agent, surface regressions pass).
- Ready for plan 06-02: session adapter (`do_action`/`do_hint`), CLI `hint`, `/api/hint`, and the served browser ladder over this transition.
- Phase 3 preflight: `lesson_slug` pointer check passed; full `lesson_roundtrip.py` green is pending 03.1-06 (owner: active 03.1 work).

---
*Phase: 06-hint-ladder-cursor-hold-feedback-modes*
*Completed: 2026-08-11*
