---
phase: 04-surface-redesign-theming
plan: 04
subsystem: ui
tags: [settings, theme, accent, presentation, semantic-html, accessibility, wcag, tdd]

# Dependency graph
requires:
  - phase: 04-01
    provides: tests/presentation_roundtrip.py Wave 0 harness, quiz view state, API-authority tracer
  - phase: 04-02
    provides: atomic settings/CLI writer patterns and the per-task TDD gate convention
  - phase: 04-03
    provides: derive_theme/theme_preview/theme_css, additive accent schema, launcher.run_native_picker child bridge
provides:
  - GET /settings and POST /api/theme with preview/pick/save/reset, loopback+same-origin mutation policy, and the exact picker fallback loop
  - surfaces/presentation.py behavior-free view/render seam with shared semantic-HTML primitives (surface_shell, context_line, teaching_step, state_panel, details_section)
  - Index, report, settings, and served quiz consuming one per-render theme.theme_css(load_settings(root)) palette; module-level fixed-CSS templates removed
  - Static itembank build reading settings beside the bank (schema defaults when missing)
affects: [04-05 study palette, 04-06 day palette, SURF-07/SURF-08 UAT, later lesson/study/day renderers]

actuals:
  tokens: 18181     # chars/4 over the realized diff for the six plan files (git diff d5447ee..HEAD)
  tasks: 2          # tasks completed
  commits: 4        # commits made (2 RED + 2 GREEN)

tech-stack:
  added: []
  patterns:
    - "Behavior-free view/render seam: render_surface(view, adapter=None) with escaped native-element primitives; adapters receive presentation-ready labels only, never scorers/keys/paths/writers"
    - "Per-render palette: every dynamic page calls theme.theme_css(settings.load_settings(root)); no module-level fixed-CSS substitution remains in the daemon"
    - "Loopback + same-origin mutation policy: /api/theme mutating actions require 127.0.0.1/::1 clients and an Origin (when present) matching the request Host; LAN clients preview only"
    - "Native picker stays out of the request thread: POST /api/theme pick delegates to the tested source/.pyz child bridge and fails closed to the browser color input"

key-files:
  created:
    - surfaces/presentation.py
  modified:
    - surfaces/theme.py
    - surfaces/daemon.py
    - surfaces/quiz.py
    - tests/presentation_roundtrip.py
    - tests/daemon_roundtrip.py

key-decisions:
  - "The four /api/theme actions accept only action/source/confirm; any css/path/tokens/config/accent_light authority field is refused with 400 before any helper runs (T-04-16)."
  - "Same-origin is validated only when an Origin header is present (CLI/curl-style clients carry none), and the netloc comparison normalizes default ports so http://127.0.0.1:8730 and 127.0.0.1:8730 compare equal."
  - "The live native-picker POST is only exercised in headless environments (CI); on interactive displays the child would open a real Tk dialog, so the daemon-level test gates on platform/DISPLAY while launcher fail-closed paths stay unit-proven in theme_roundtrip."
  - "Primary action styling uses accent-soft background + accent text/border, the pairing derive_theme guarantees at 4.5:1, instead of a literal white-on-accent that is not guaranteed in dark mode (Rule 1 contrast fix)."
  - "The report's exact empty/partial copy follows 04-UI-SPEC ('Nothing has been answered yet.' / 'Some responses still need review. Auto-graded totals exclude them.'), superseding the 04-02-era 'Nothing answered yet' heading; the existing daemon assertion was updated to the locked copy."
  - "Index surfaces stem collisions (files found but not served) as a labelled warning state with recovery text, reading only basenames so no filesystem path leaks to LAN clients."

patterns-established:
  - "Presentation primitives emit only semantic HTML with data-presentation-* / data-action-primary|secondary enhancement hooks; teaching_step renders exactly one primary action and no sequencing or pedagogy logic"
  - "Shared design tokens live once in presentation.SHARED_CSS (4/8/16/24/32/48/64 spacing, 14/16/20/28 type at 400/600, 720/800 measures, 44px targets, 2px+2px focus, 768px breakpoint, 320px overflow protection, 150ms motion, reduced-motion kill)"
  - "quiz.page_for accepts an optional theme_css argument with THEME_CSS default, so every pre-existing caller stays byte-identical while the daemon injects the live palette"

requirements-completed: [SURF-07, SURF-08]

coverage:
  - id: D1
    description: "GET /settings renders the labeled browser color input, exact Choose with system picker / Save accent / Reset copy, side-by-side light/dark preview samples, adjustment disclosure, one Theme section, Accessibility details, and a persistent polite status"
    requirement: SURF-07
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_settings_page"
        status: pass
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_settings_page_states_and_js"
        status: pass
    human_judgment: false
  - id: D2
    description: "POST /api/theme preview/pick/save/reset follow the CLI twin helpers; preview never writes, save persists the normalized source with a generated preview, reset requires literal RESET, unknown/authority fields refused"
    requirement: SURF-07
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_theme_route_contract"
        status: pass
    human_judgment: false
  - id: D3
    description: "Native picker goes through launcher.run_native_picker (no Tk in the request thread); unavailable/cancel reads available:false with the exact fallback reason and keeps the browser color input/draft usable"
    requirement: SURF-07
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_theme_pick_contract"
        status: pass
      - kind: unit
        ref: "tests/theme_roundtrip.py#test_launcher_run_native_picker_fails_closed"
        status: pass
    human_judgment: false
  - id: D4
    description: "Mutation/pick restricted to loopback same-origin JSON; LAN clients may preview but never alter host settings or open a host dialog"
    requirement: SURF-07
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_theme_route_loopback_and_origin"
        status: pass
    human_judgment: false
  - id: D5
    description: "Index, report, settings, and served quiz carry identical accent tokens generated from the daemon root's settings; saving then reloading updates every route"
    requirement: SURF-07
    verification:
      - kind: integration
        ref: "tests/presentation_roundtrip.py#test_shared_accent_tokens_across_routes"
        status: pass
      - kind: integration
        ref: "tests/presentation_roundtrip.py#test_reload_after_save_updates_tokens"
        status: pass
    human_judgment: false
  - id: D6
    description: "Static itembank build reads settings beside the bank through the same generator; missing settings use schema defaults"
    requirement: SURF-07
    verification:
      - kind: integration
        ref: "tests/presentation_roundtrip.py#test_static_build_uses_settings_beside_bank"
        status: pass
    human_judgment: false
  - id: D7
    description: "Forced light/dark and system modes select the correct token blocks without changing semantic-state tokens"
    requirement: SURF-08
    verification:
      - kind: integration
        ref: "tests/presentation_roundtrip.py#test_forced_modes_preserve_semantic_tokens"
        status: pass
    human_judgment: false
  - id: D8
    description: "Default adapter emits one h1, landmarks, native controls, visible-focus hooks, a persistent polite status region, and intact fallback content; an alternate adapter receives the same behavior-free view data"
    requirement: SURF-07
    verification:
      - kind: unit
        ref: "tests/presentation_roundtrip.py#test_default_adapter_structure_and_alternate_adapter"
        status: pass
    human_judgment: false
  - id: D9
    description: "Index/report state contracts: exact empty and partial-review copy, plain labels, tabular numerals, visible evidence/provenance"
    requirement: SURF-07
    verification:
      - kind: integration
        ref: "tests/presentation_roundtrip.py#test_index_and_report_state_copy"
        status: pass
    human_judgment: false
  - id: D10
    description: "Lesson-compatible 720px prose shell with heading/link/code/table overflow rules and disclosures, 320px/200% zoom, reduced-motion, and no-script fallback, without adding Phase 3 parsing or media behavior"
    requirement: SURF-07
    verification:
      - kind: unit
        ref: "tests/presentation_roundtrip.py#test_lesson_compatible_prose_view"
        status: pass
      - kind: unit
        ref: "tests/presentation_roundtrip.py#test_responsive_zoom_and_noscript_fallback"
        status: pass
    human_judgment: false
  - id: D11
    description: "Teaching step expresses a concise label/prompt, immediate status slot, optional progressive details, and exactly one primary next action; secondary actions cannot acquire the primary marker and no sequencing script exists"
    requirement: SURF-07
    verification:
      - kind: unit
        ref: "tests/presentation_roundtrip.py#test_teaching_step_primary_action_contract"
        status: pass
    human_judgment: false
  - id: D12
    description: "Visual polish of the new settings preview cards and the migrated index/report/settings/quiz surfaces at real browser widths and both color modes"
    verification: []
    human_judgment: true
    rationale: "Structural/a11y contracts are automated, but final visual adequacy (60/30/10 allocation, preview-card legibility, 200% zoom in a real browser) requires human UAT per 04-VALIDATION."

# Metrics
duration: 15min
completed: 2026-08-08
status: complete
---

# Phase 4 Plan 4: Semantic Presentation Adapter and Themed Settings/Index/Report/Quiz Summary

**One learner-facing settings page (`/settings`) with preview/pick/save/reset of the source accent behind a loopback+same-origin `/api/theme`, a behavior-free semantic-HTML presentation adapter (`surfaces/presentation.py`) with shared shell/step/state primitives, and index/report/settings/quiz migrated to one per-render `theme.theme_css(load_settings(root))` palette with no module-level fixed CSS left in the daemon (D-04 through D-07, SURF-07, SURF-08)**

## Performance

- **Duration:** 15 min
- **Started:** 2026-08-08T22:58:51-05:00 (first RED commit)
- **Completed:** 2026-08-08T23:13:43-05:00
- **Tasks:** 2
- **Files modified:** 6 (1 created, 5 modified)

## Accomplishments
- `/settings` implements the complete D-05..D-07 loop: labeled browser color input, current source text, live light/dark preview cards with labelled Correct/Incorrect/Warning/Selected/Focus samples, measured WCAG ratios and the exact adjustment disclosure in an Accessibility details disclosure, Choose with system picker (native Tk bridge, preview-only), Save accent, and a two-step Reset with literal `RESET` confirmation. Every state keeps the draft and recovers focus.
- `POST /api/theme` accepts exactly preview/pick/save/reset, derives every token server-side through the same helpers as `itembank theme`, refuses css/path/tokens/config fields, requires loopback+same-origin for mutation/pick, and lets LAN clients preview only (T-04-13/T-04-14/T-04-16).
- `surfaces/presentation.py` establishes the replaceable render seam: behavior-free view dictionaries render through `render_surface(view, adapter=None)`; escaped `surface_shell`, `context_line`, `teaching_step`, `state_panel`, and `details_section` primitives carry the locked design tokens (spacing 4-64, type 14/16/20/28 at 400/600, 720/800 measures, 44px targets, 2px+2px focus, 768px breakpoint, 320px overflow protection, 150ms motion, reduced-motion kill) and zero color literals.
- Index, report, settings, and the served quiz all receive `theme.theme_css(load_settings(root))` per render; saving an accent and reloading updates every route, forced light/dark/system modes keep semantic tokens fixed, and the static `build` path reads settings beside the bank (schema defaults when missing).
- Reports now render the exact UI-SPEC empty/partial copy with visible provenance, the index names stem-collision unserved entries as a warning state, and the old module-level daemon CSS templates are gone.

## Task Commits

Each task was committed atomically (RED test gate then GREEN implementation, per `tdd="true"`):

1. **Task 1: Preview, pick, save, and reset the accent from `/settings`** - `07ff254` (test) + `03ca93f` (feat)
2. **Task 2: Establish the semantic presentation adapter and migrate index, report, settings, and quiz** - `882b2b1` (test) + `4871b52` (feat)

**Plan metadata:** pending (committed after SUMMARY/state updates)

## Files Created/Modified
- `surfaces/presentation.py` - behavior-free render_surface/adapter seam and shared semantic-HTML primitives + SHARED_CSS design tokens
- `surfaces/theme.py` - theme_page now renders the settings body through presentation.surface_shell; slimmed settings CSS; public persist_source shared by CLI and route; exact browser copy constants
- `surfaces/daemon.py` - GET /settings + POST /api/theme routes, loopback/same-origin gate helpers, index/report migrated to the shell with per-render tokens, quiz route injects the palette, module-level INDEX_TEMPLATE/REPORT_TEMPLATE removed
- `surfaces/quiz.py` - page_for optional theme_css (THEME_CSS default keeps callers byte-identical); cmd_build reads settings beside the bank
- `tests/daemon_roundtrip.py` - five new /settings + /api/theme checks; empty-report copy assertion updated to the locked UI-SPEC copy
- `tests/presentation_roundtrip.py` - nine Task 2 contract tests (shared tokens, reload, static build, forced modes, adapter seam, report/index copy, lesson-compatible prose, responsive/no-script, teaching-step primary action)

## Decisions Made
- The four `/api/theme` actions read only action/source/confirm; any authority field is refused with 400 before any helper runs.
- Same-origin validation applies only when an Origin header is present, with default-port normalization in the netloc comparison.
- The live native-picker POST is exercised only where the child fails fast (headless CI); interactive displays skip the live call per the repo's established platform-gated-test precedent, while the fail-closed mapping stays unit-proven.
- Primary action styling uses the contrast-guaranteed accent-soft/accent pairing instead of white-on-accent (not guaranteed in dark mode).
- Report exact empty/partial copy follows 04-UI-SPEC, superseding the 04-02-era heading.
- Index names stem collisions as a labelled warning with recovery text, using basenames only (no path leak to LAN clients).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Primary action color pairing not guaranteed readable in dark mode**
- **Found during:** Task 2 (presentation adapter)
- **Issue:** The initial primary-action rule set white text on `var(--accent)`; the theme only guarantees the accent at 4.5:1 against card/bg, so a lightened dark-mode accent could render white-on-light below contrast.
- **Fix:** Primary actions now use `background:var(--accent-soft); color:var(--accent)` -- the pairing `derive_theme` provably meets at 4.5:1 -- in both SHARED_CSS and the settings Save button.
- **Files modified:** surfaces/presentation.py, surfaces/theme.py
- **Verification:** full 19-file suite green; no color literals remain in presentation.py
- **Committed in:** 4871b52 (Task 2 commit)

**2. [Rule 3 - Blocking] Existing report empty-state assertion referenced superseded copy**
- **Found during:** Task 2 (report migration)
- **Issue:** `check_report_empty` asserted the 04-02-era "Nothing answered yet" heading; plan 04-04 Test 6 locks the UI-SPEC copy "Nothing has been answered yet."
- **Fix:** Updated the assertion to the locked copy; the report now renders the exact contract.
- **Files modified:** tests/daemon_roundtrip.py, surfaces/daemon.py
- **Verification:** daemon_roundtrip 55/55 checks green
- **Committed in:** 4871b52 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 Rule 1, 1 Rule 3)
**Impact on plan:** Both fixes were required for the plan's own correctness/contract; no scope creep.

## Issues Encountered
- `page_for()`'s new optional argument initially carried a different name than the daemon call site, producing a `TypeError` on the served quiz route -- caught by the Task 2 RED suite and fixed by naming the parameter `theme_css` per the plan's `<interfaces>` wording.
- The a11y heading-order checker tripped on the adapter's h1->h3 step label; `teaching_step` labels are h2 so heading levels never skip.
- On interactive displays (this machine), a live `POST /api/theme pick` would open a real Tk dialog; the daemon-level check is platform-gated, and the launcher's fail-closed unit tests cover the mapping.

## TDD Gate Compliance

Commit log shows the mandatory RED->GREEN gate sequence for both tasks:

1. `07ff254` `test(04-04)` (RED) followed by `03ca93f` `feat(04-04)` (GREEN)
2. `882b2b1` `test(04-04)` (RED) followed by `4871b52` `feat(04-04)` (GREEN)

No REFACTOR commits were needed; no test passed unexpectedly during a RED phase.

## Next Phase Readiness
- Plan 04-05 (study) and 04-06 (day) can consume `presentation.surface_shell`/primitives and `theme.theme_css(settings.load_settings(...))` without creating a second palette; study/day source ownership is explicitly isolated there.
- `/settings` and `/api/theme` are live browser surfaces ready for the 04-VALIDATION visual UAT (real browser, both color modes, 200% zoom, keyboard-only pass, picker fallback).
- SURF-08 is ready to flip Complete now (04-03 + 04-04 both carry SUMMARYs); SURF-07 stays open until 04-05 and 04-06 finish per the shared-ID gate.

## Self-Check: PASSED
