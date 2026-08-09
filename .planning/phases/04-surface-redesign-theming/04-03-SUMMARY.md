---
phase: 04-surface-redesign-theming
plan: 03
subsystem: ui
tags: [theme, accent, wcag, contrast, colorsys, tkinter, settings, cli, tdd]

# Dependency graph
requires:
  - phase: 04-01
    provides: tests/theme_roundtrip.py Wave 0 harness (token/contrast extractors, settings bases, picker mocks, source/.pyz child seam)
  - phase: 04-02
    provides: established atomic settings/CLI writer patterns and the per-task TDD gate convention
provides:
  - surfaces/theme.py deterministic WCAG-checked light/dark accent and soft derivation from one source
  - additive required accent {source: #RRGGBB} schema (default #0e6e62) with source-only atomic persistence
  - itembank theme preview/set/reset/pick CLI contract with exact fallback copy
  - launcher.run_native_picker fixed no-shell source/.pyz child bridge
affects: [04-04 settings UI and shared-palette rollout, 04-05 study palette, 04-06 day palette, SURF-08 UAT]

actuals:
  tokens: 11305
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "Bounded deterministic HLS lightness scan (colorsys) that preserves hue/saturation and stops at the nearest 4.5:1 step"
    - "Soft token derived toward the mode card color under both accent-on-soft and ink-on-soft 4.5:1 pairings"
    - "Lazy tkinter import inside the pick command; hidden root withdrawn and destroyed in finally on every path"
    - "Fixed no-shell [python, entry, theme, pick, --json, --initial, SOURCE] child argv with bounded JSON validation"
    - "Schema default merge (load_settings) keeps pre-Phase-4 files loadable; only accent.source is ever written"

key-files:
  created: []
  modified:
    - surfaces/theme.py
    - surfaces/cli.py
    - surfaces/settings.py
    - surfaces/launcher.py
    - schemas/settings.schema.json
    - itembank.json
    - tests/theme_roundtrip.py
    - tests/config_roundtrip.py

key-decisions:
  - "Accent hex format is enforced by theme.py normalization plus schema minLength 7 -- schema_validate.py's supported-keyword set has no `pattern`, and extending the shared validator is outside this plan's file scope; every write path normalizes and rejects invalid colors before anything touches disk."
  - "The derived dark accent-soft for the default teal lands exactly on the card color because that is the nearest blend meeting both 4.5:1 pairings -- soft derivation is contrast-first and honestly reported."
  - "THEME_CSS is now a computed constant from theme_css(system default), keeping every existing surface green while the light warn token moves from #b5760a to the binding #8a5900."
  - "The picker fallback reason string is the single source of the exact human copy 'System picker is unavailable here. Choose a color below instead.' in both structured and human output."
  - "D-07 resolves in favor of one source plus deterministic enforced derivation -- no manual per-mode override path exists anywhere in the persisted contract."

requirements-completed: [SURF-08]

coverage:
  - id: D1
    description: "Deterministic derive_theme: normalized lowercase #RRGGBB source, byte-stable repeated runs, per-mode accent/accent_soft/base/semantic tokens"
    requirement: SURF-08
    verification:
      - kind: unit
        ref: "tests/theme_roundtrip.py#test_derive_theme_deterministic_and_normalized"
        status: pass
    human_judgment: false
  - id: D2
    description: "WCAG contrast enforcement: every derived accent 4.5:1 on card and bg, hue-family correction for inaccessible sources, adjustment disclosure with original source retained"
    requirement: SURF-08
    verification:
      - kind: unit
        ref: "tests/theme_roundtrip.py#test_derived_accents_meet_contrast_and_report_correction"
        status: pass
    human_judgment: false
  - id: D3
    description: "Fixed semantic ok/bad/warn tokens identical across unrelated accents with 4.5:1 pairings and pairwise distinctness from the accent"
    requirement: SURF-08
    verification:
      - kind: unit
        ref: "tests/theme_roundtrip.py#test_semantic_tokens_independent_and_contrast_checked"
        status: pass
    human_judgment: false
  - id: D4
    description: "theme_css system/light/dark branch contract with exact binding base and semantic palette values"
    requirement: SURF-08
    verification:
      - kind: unit
        ref: "tests/theme_roundtrip.py#test_theme_css_modes"
        status: pass
    human_judgment: false
  - id: D5
    description: "Additive persisted schema: existing theme enum/default unchanged, required accent.source default #0e6e62, old files load through merged defaults, unknown keys preserved, set/reset idempotent and source-only"
    requirement: SURF-08
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_theme_schema_additive_accent"
        status: pass
    human_judgment: false
  - id: D6
    description: "CLI preview/set/reset contract: read-only preview with ratios and correction notice, invalid colors rejected with a named error and byte preservation"
    requirement: SURF-08
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_theme_set_reset_contract"
        status: pass
    human_judgment: false
  - id: D7
    description: "Native picker with non-destructive fallback: mocked selection is preview-only, every unavailable path preserves settings and destroys the hidden root, exact fallback copy, launcher child bridge fails closed"
    requirement: SURF-08
    verification:
      - kind: unit
        ref: "tests/theme_roundtrip.py#test_pick_unavailable_paths_never_write"
        status: pass
    human_judgment: false
  - id: D8
    description: "Settings discovery: itembank config reports theme and accent as read by Phase 4 while later-phase groups remain inert"
    requirement: SURF-08
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_phase_4_theme_keys_read_not_inert"
        status: pass
    human_judgment: false

# Metrics
duration: 10min
completed: 2026-08-08
status: complete
---

# Phase 4 Plan 3: Deterministic accessible palette, source-only accent persistence, and native picker Summary

**Deterministic WCAG-checked light/dark accent derivation from one persisted source, additive `accent.source` schema, a preview/set/reset/pick CLI with exact correction copy, and a lazy native Tk picker plus fail-closed source/`.pyz` child bridge (D-04 through D-07, SURF-08)**

## Performance

- **Duration:** 10 min
- **Started:** 2026-08-09T03:39:57Z
- **Completed:** 2026-08-09T03:50:00Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- `surfaces/theme.py` is now the single deterministic palette source: strict `#RRGGBB` normalization, sRGB relative luminance and WCAG contrast helpers, bounded HLS lightness correction that preserves hue/saturation and stops at the nearest 4.5:1 step, and per-mode soft tokens derived toward the card color under both accent-on-soft and ink-on-soft pairings.
- The exact polished default palette and fixed semantic verdict tokens ship byte-for-byte per the binding decisions; semantic ok/bad/warn never derive from the learner accent, and `theme=system` emits light tokens plus the matching `prefers-color-scheme: dark` override while forced modes emit one set.
- The persisted contract is exactly `theme: system|light|dark` plus required `accent: {source: #RRGGBB}` default `#0e6e62`; pre-Phase-4 files load through merged schema defaults, unknown top-level user keys survive, and only the normalized source is ever written (atomic, byte-idempotent).
- `itembank theme preview/set/reset/pick` proves D-05/D-06/D-07 at the CLI: read-only preview prints source, light/dark/soft tokens, measured ratios, and `Adjusted for readable contrast. Your source colour is still saved.`; reset requires `--confirm-reset RESET`; the native picker runs on the process main thread behind a lazy Tk import and every unavailable path prints the exact browser-fallback copy without writing.
- `launcher.run_native_picker` builds fixed no-shell argv for the current source script or `.pyz` and fails closed on spawn/non-zero/oversize/malformed child output, keeping Tk out of the daemon's HTTP handler (T-04-12).

## Task Commits

Each task was committed atomically (RED test gate then GREEN implementation, per `tdd="true"`):

1. **Task 1: Derive the polished accessible palette deterministically** - `e655802` (test) + `b329c74` (feat)
2. **Task 2: Persist the additive source-only schema and expose preview, set, and reset** - `2af5d77` (test) + `1262b34` (feat)
3. **Task 3: Add the native OS picker with a non-destructive fallback result** - `d432454` (test) + `f060db1` (feat)

## Files Created/Modified
- `surfaces/theme.py` - palette/token source, color math, deterministic derivation, preview, guarded native picker, and the theme CLI
- `surfaces/cli.py` - `itembank theme` subparser (preview/set/reset/pick)
- `surfaces/settings.py` - `THIS_PHASE` advanced to 4 so theme/accent report as active
- `surfaces/launcher.py` - `run_native_picker` source/`.pyz` child bridge
- `schemas/settings.schema.json` - additive required `accent` group (source default `#0e6e62`, minLength 7)
- `itembank.json` - shipped `accent.source` default
- `tests/theme_roundtrip.py` - derivation/contrast/semantic/mode-CSS/preview/picker/launcher assertions
- `tests/config_roundtrip.py` - schema-compatibility, persistence, reset-refusal, and discovery assertions

## Decisions Made
- Hex-format validation lives in `normalize_source` plus schema `minLength: 7` because `schema_validate.py` supports no `pattern` keyword; extending the shared validator was outside this plan's file list (Task 2's files are exactly the plan's five).
- Dark accent-soft for the default teal derives exactly to the card color -- the nearest blend meeting both 4.5:1 pairings; this is a contrast-first, honestly-reported derivation, not a hand-picked value.
- `THEME_CSS` is computed once from `theme_css` over the default settings document, so every existing surface keeps working while the light `--warn` moves from `#b5760a` to the binding `#8a5900`.
- `--confirm-reset RESET` mirrors the 04-02 `--confirm-force OVERWRITE` precedent: an explicit second confirmation, never a silent default restore.
- D-07's optional manual overrides are deliberately declined: one source plus enforced deterministic derivation is the entire persisted contract.

## Deviations from Plan

None - plan executed exactly as written. All three tasks followed a true RED (observed failing assertions before production changes) to GREEN (full 19-file suite green) cycle, and every task's `<files>` list was matched exactly.

## Issues Encountered
- The launcher child-bridge failure modes were initially read off the `launcher.subprocess` module attribute at call time, which broke the repo's wholesale-module-patching test seam (a fake module has no `SubprocessError`). Resolved by capturing `_SUBPROCESS_ERRORS` from the real module at import time -- implementation detail of Task 3's GREEN, no plan change.

## TDD Gate Compliance

Commit log shows the mandatory gate sequence for all three tasks:

1. `e655802` `test(04-03)` (RED) followed by `b329c74` `feat(04-03)` (GREEN)
2. `2af5d77` `test(04-03)` (RED) followed by `1262b34` `feat(04-03)` (GREEN)
3. `d432454` `test(04-03)` (RED) followed by `f060db1` `feat(04-03)` (GREEN)

No REFACTOR commits were needed; no test passed unexpectedly during a RED phase.

## Next Phase Readiness
- Plan 04-04 can call `derive_theme`, `theme_preview`, `theme_css`, `pick_native_accent`, `cmd_theme`, and `launcher.run_native_picker` directly, and can read active `theme`/`accent` rows through `itembank config` for the settings UI and the shared-palette rollout across index/report/quiz.
- The browser settings page has its own UI-SPEC copy (`Adjusted for readable contrast. Your chosen color is saved; this preview shows the accessible rendered color.`) distinct from the CLI notice; 04-04 should keep the two copywriting surfaces separate.

## Self-Check: PASSED
