---
phase: 04-surface-redesign-theming
plan: 05
subsystem: ui
tags: [study, explanation, progressive-disclosure, semantic-html, accessibility, wcag, theme, tdd]

# Dependency graph
requires:
  - phase: 04-01
    provides: surface/theme/presentation harnesses and the served-quiz client contract
  - phase: 04-02
    provides: validated local settings loading and the per-task TDD gate convention
  - phase: 04-03
    provides: theme_css/derive_theme single palette derivation
  - phase: 04-04
    provides: surfaces/presentation.py semantic shell/state-panel/details primitives and the per-render theme_css(load_settings(root)) pattern
provides:
  - Complete deliberate-review study cards composed from runtime.public_item + runtime.explain_payload (no field allowlist)
  - Progressive accessible reveal: native recall toggles, Reveal explanation button, correct/selected rationale details open by default, per-state primary actions
  - Study migrated onto the one generated palette with settings beside the bank, no component color literals
  - Script-safe study data embedding (T-04-17) and shared-shell empty/render-error states
affects: [04-06 day palette, SURF-06/SURF-07 UAT, later lesson/study/day renderers]

actuals:
  tokens: 13188      # chars/4 over the realized diff (git diff d881364..HEAD, 52,753 chars)
  tasks: 2           # tasks completed
  commits: 5         # commits made (2 RED test + 2 GREEN feat + 1 metadata docs)

tech-stack:
  added: []
  patterns:
    - "Deliberate-review composition: study_item(q) = public_item(q) + explain_payload(q, reveal=True), so any field the runtime returns reaches the learner by construction and no hand-copied projection can drift"
    - "Progressive native disclosure: correct rationale <details> open server-side, learner-selected ones open client-side on reveal, all others stay closed but keyboard-reachable"
    - "Per-state primary action groups: front/revealed/Learn-rating groups each carry exactly one data-action-primary and one visible at a time; the reveal control keeps focus while announcing the transition"
    - "Script-safe data element: escape <, >, & and U+2028/U+2029 in embedded JSON so bank prose can never close <script> or inject markup (T-04-17)"

key-files:
  created: []
  modified:
    - surfaces/study.py
    - tests/surface_roundtrip.py

key-decisions:
  - "study_item composes the runtime's two canonical builders wholesale under an `explain` member; there is no second explanation allowlist in the surface, so D-12 is enforced structurally rather than maintained by hand."
  - "Cards are server-rendered through presentation.surface_shell/state_panel/details primitives with the one theme_css(load_settings(bank_dir)) palette; the client wires only reveal/queue/rating state, never scoring, submission, or a second palette (D-04, D-14)."
  - "After reveal the Reveal explanation control becomes a quiet 'Explanation revealed' control that keeps focus per UI-SPEC while the revealed/rating groups supply the single primary next action."
  - "The embedded CARDS payload legitimately carries explain.correct (study is the deliberate reveal surface, T-04-19 accepted); the no-verdict rule is enforced on client behavior, not on the canonical payload."
  - "The locked empty copy 'No study cards match this bank.' comes from the plan's must-haves; the render-error state uses the UI-SPEC study matrix recovery copy 'This card could not be shown. Move to the next card or reload.' with Reload/Choose-another-bank actions."

patterns-established:
  - "Progressive review: one focused stem + local-recall controls on the front; answer, concise why, per-option rationales, then labelled Second-best/Discriminator/Common trap/Notes disclosures after a deliberate Reveal explanation action"
  - "Study and quiz keep distinct intent: quiz feedback is response-driven through /api/submit; study never scores, fetches, or submits, and Got it/Missed/recall affect only local presentation and queue behavior"
  - "Choice rationales pair semantic color with text labels (Correct/Selected badges) plus native open state; the custom accent marks interaction (selected recall, primary actions), never correctness"

requirements-completed: [SURF-06, SURF-07]

coverage:
  - id: D1
    description: "study_item composes the canonical public item plus the full reveal explanation for every item type with no dropped field (mc/multi options+answer_text+why+correct+da+second+disc+trap+notes; table/dnd rows+row_cats; build steps; short model/rubric), and sentinels in every explanation field reach both the data and the rendered reveal output exactly once"
    requirement: SURF-06
    verification:
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_item_choice_payload"
        status: pass
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_item_nonchoice_payload"
        status: pass
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_item_sentinels_reach_reveal"
        status: pass
    human_judgment: false
  - id: D2
    description: "Bank prose containing HTML or a script terminator is serialized inert and rendered only through escaping; it can never close the data element or execute (T-04-17)"
    requirement: SURF-06
    verification:
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_script_safety"
        status: pass
    human_judgment: false
  - id: D3
    description: "Empty input renders the shared state panel with the exact 'No study cards match this bank.' copy and a Choose-another-bank action; a malformed card renders a shared error state that keeps bank context and Reload/back recovery instead of a blank page"
    requirement: SURF-06
    verification:
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_empty_and_error_states"
        status: pass
    human_judgment: false
  - id: D4
    description: "Reveal order is answer, concise why, option list with adjacent rationale disclosures, then labelled Second-best answer / Discriminator / Common trap / Notes; correct rationale opens by default, learner-selected opens on reveal, all others stay closed but keyboard-reachable (D-12, D-13)"
    requirement: SURF-06
    verification:
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_reveal_order"
        status: pass
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_recall_controls_and_default_open"
        status: pass
    human_judgment: false
  - id: D5
    description: "Non-choice cards (table/dnd/build/short) render their canonical answer/model/rubric content without inventing option controls"
    requirement: SURF-06
    verification:
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_nonchoice_cards"
        status: pass
    human_judgment: false
  - id: D6
    description: "Flash/Learn tabs, Reveal explanation, Previous/Next, Got it/Missed, recall selection and disclosures are native 44px controls with visible focus, one h1, heading order, a persistent polite status region, Revealing-explanation announcement, focus management, reduced motion, 320px/200% overflow protection, and no scorer/response path in the client (D-03, D-14)"
    requirement: SURF-06
    verification:
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_native_controls_and_a11y"
        status: pass
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_no_scorer_or_response"
        status: pass
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_reveal_announce_and_responsive"
        status: pass
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_one_primary_action_per_state"
        status: pass
    human_judgment: false
  - id: D7
    description: "Study consumes theme_css from validated local settings beside the bank (schema defaults when absent), matches quiz accent tokens in system/light/dark, and contains no component color literals or accent-as-correctness styling (D-04, SURF-07)"
    requirement: SURF-07
    verification:
      - kind: unit
        ref: "tests/surface_roundtrip.py#check_study_theme_and_palette"
        status: pass
    human_judgment: false
  - id: D8
    description: "GET /study/<stem> still renders through study_page byte-for-byte and cmd_study writes the identical page (no second study template in the daemon)"
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_study_route"
        status: pass
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_study_cmd_matches_study_page"
        status: pass
    human_judgment: false
  - id: D9
    description: "Visual adequacy of the reworked study card (real browser, keyboard-only pass, 320px/200% zoom, both color modes)"
    verification: []
    human_judgment: true
    rationale: "Structural/a11y contracts are automated, but final visual adequacy of the progressive reveal surface requires human UAT per 04-VALIDATION (same precedent as 04-04 D12)."

# Metrics
duration: 10min
completed: 2026-08-08
status: complete
---

# Phase 4 Plan 5: Complete Deliberate-Review Study Surface Summary

**Study cards now compose the runtime's full public+explanation payload with no dropped field, render it through a progressive, keyboard/screen-reader-accessible reveal (native recall toggles, Reveal explanation button, correct/selected rationales open by default), and run on the single generated palette from settings beside the bank (D-04, D-12 through D-14, SURF-06, SURF-07)**

## Performance

- **Duration:** 10 min
- **Started:** 2026-08-09T04:21:08Z
- **Completed:** 2026-08-09T04:31:38Z
- **Tasks:** 2
- **Files modified:** 2 (surfaces/study.py rewritten, tests/surface_roundtrip.py extended)

## Accomplishments

- `study_item(q)` is now a pure composition of `runtime.public_item(q)` and `runtime.explain_payload(q, reveal=True)` under one `explain` member: mc/multi cards carry public options plus answer_text, why, correct, every non-empty da rationale, second, disc, trap, and all notes; table/dnd/build/short cards carry their branch's full payload. A sentinel in every explanation field is proven to reach both the embedded data and the rendered reveal output exactly once, so no hand-copied projection can drift (D-12, SURF-06).
- The reveal surface is progressive and accessible: before reveal the front shows one focused stem and native "Your recall choice — not graded" toggle buttons for mc/multi; **Reveal explanation** announces "Revealing explanation…", opens the explanation, opens correct (server-side) and learner-selected (client-side) rationale disclosures, and leaves every other rationale closed but keyboard-reachable (D-13). Answer and concise why come first, then each option once with its rationale, then labelled Second-best answer / Discriminator / Common trap / Notes disclosures; short cards retain Model answer + What a marker checks.
- Flash/Learn tabs, Previous/Next, Got it/Missed, recall selection, and all disclosures are native 44px controls with visible focus, one h1, unbroken heading order, a persistent polite status region, focus management, and reduced-motion support. The front/revealed/Learn-rating action groups each expose exactly one primary next action. The study client never scores, fetches, or submits; Got it/Missed/recall affect only local presentation and queue behavior (D-03, D-14).
- Study now loads validated local settings beside the bank and renders through the one `theme_css` generator plus the shared semantic shell/state-panel/details primitives: empty input shows "No study cards match this bank." in the shared state panel, and a render error keeps bank context with Reload/Choose-another-bank recovery. `surfaces/study.py` contains no color literals and never uses the custom accent to mean correctness (D-04, T-04-20, T-04-26).
- Bank prose is embedded through script-safe JSON (`\u003c`/`\u003e`/`\u0026`/U+2028/U+2029 escaping) and every rendered string passes through text escaping, so HTML/script-terminator bank text can neither close the data element nor execute (T-04-17).

<!-- gsd:write-continue -->
## Task Commits

Each task was committed atomically (RED test gate then GREEN implementation, per `tdd="true"`):

1. **Task 1: Build every study card from the canonical complete explanation payload** - `b91a031` (test) + `69cd063` (feat)
2. **Task 2: Render relevant rationales and advanced explanation progressively** - `d0921a0` (test) + `1dc5e54` (feat)

**Plan metadata:** `pending` (committed after SUMMARY/state updates)

## Files Created/Modified

- `surfaces/study.py` - rewritten: `study_item` composes public_item + explain_payload; `script_safe_json` inert embedding; `_card_markup`/`_explain_sections` server-render the progressive reveal with recall toggles, rationale details, and per-state action groups; `study_page` loads settings beside the bank and renders through presentation.surface_shell/state_panel with the generated palette; STUDY_JS wires reveal/queue/rating with no scorer or response path
- `tests/surface_roundtrip.py` - extended with synthetic_q helpers, study_page_for_question renderer, and 13 new checks: payload completeness (all six types), sentinel reach, script safety, empty/error states, reveal order, recall/default-open contract, non-choice cards, native controls/a11y, no-scorer client, responsive/reduced-motion, one-primary-per-state, and study/quiz palette parity

## Decisions Made

- `study_item` uses the runtime's two canonical builders wholesale; there is no second explanation allowlist in the surface, so D-12 is structural.
- Cards are server-rendered through the shared semantic primitives with the one generated palette; the client wires only reveal/queue/rating state.
- After reveal the Reveal control becomes a quiet "Explanation revealed" control that keeps focus per UI-SPEC while the revealed/rating groups supply the single primary next action.
- The embedded payload legitimately carries `explain.correct` (T-04-19 accepted); the no-verdict rule is enforced on client behavior, not on the canonical payload.
- Empty copy follows the plan's locked "No study cards match this bank."; render-error copy follows the UI-SPEC study matrix recovery wording.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Two newly-authored Task 1/Task 2 test assertions were refined during GREEN: the hostile-markup check originally re-unescaped the page before grepping (fixed to assert raw markup is absent and the escaped form present), the focus check required the literal `focus()` (relaxed to `focus(` for the preventScroll call), and the no-verdict check was scoped to client behavior after the data element because the canonical payload legitimately carries `explain.correct`.
- `tests/theme_roundtrip.py` and `tests/presentation_roundtrip.py` were consumed unmodified: the Wave 0 harnesses from 04-04 already carried the token-provenance and semantic-adapter helpers the plan's Task 2 files list referenced, so no edits were needed there.

## TDD Gate Compliance

Commit log shows the mandatory RED->GREEN gate sequence for both tasks:

1. `b91a031` `test(04-05)` (RED) followed by `69cd063` `feat(04-05)` (GREEN)
2. `d0921a0` `test(04-05)` (RED) followed by `1dc5e54` `feat(04-05)` (GREEN)

No REFACTOR commits were needed; no test passed unexpectedly during a RED phase.

## Next Phase Readiness

- Plan 04-06 (day cockpit/editor) can consume the same `theme_css(load_settings(...))` + presentation primitives pattern and the study surface's progressive-disclosure/primary-action conventions without creating a second palette.
- SURF-06 is ready to flip Complete; SURF-07 stays open until 04-06 finishes per the shared-ID gate.
- The reworked study page is a live browser surface ready for the 04-VALIDATION visual UAT (keyboard-only pass, 320px/200% zoom, both color modes, screen-reader details/reveal announcements).

## Self-Check: PASSED

---
*Phase: 04-surface-redesign-theming*
*Completed: 2026-08-08*
