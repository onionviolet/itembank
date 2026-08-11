---
phase: 04-surface-redesign-theming
verified: 2026-08-11T15:30:00Z
status: human_needed
score: 5/5 must-haves verified
behavior_unverified: 0 # Count of PRESENT_BEHAVIOR_UNVERIFIED truths; every roadmap truth below has a passing behavioral test
overrides_applied: 0
human_verification:
  - test: "Open the daemon in a real browser (system/light/dark). Walk index, quiz, study, report, settings, and day. Confirm every surface reads as one product from one visual system (60/30/10 allocation, shared spacing/type/measure), and that the quiz page shows one sticky context line, a dominant stem h1, a reserved feedback region, and no old header/rail/tally chrome."
    expected: "All surfaces share the same palette and visual primitives; the question view keeps exactly one sticky context line with the stem as the single h1; no layout regression at desktop or 320px/200% zoom."
    why_human: "Perceptual hierarchy, layout quality, and real-browser rendering at 320px/200% cannot be proven by DOM/CSS string assertions (04-VALIDATION manual matrix; 04-06 human-check)."
  - test: "In /settings, choose an accent through the native OS picker, cancel once, then pick through the browser color input, preview in both light/dark samples, save, reset, and reload every surface."
    expected: "The picker selection is preview-only; cancel/fallback shows the exact copy 'System picker is unavailable here. Choose a color below instead.' without changing settings; save persists only accent.source; every surface updates on reload in system/light/dark."
    why_human: "Tk/OS-dialog behavior is environment-dependent and the live picker is platform-gated out of CI; unit tests prove only the fail-closed mapping (test_pick_unavailable_paths_never_write)."
  - test: "Screen-reader walkthrough (Narrator/NVDA/VoiceOver): quiz submit and verdict, study reveal, settings save error/fallback, and day conflict recovery, with reduced motion enabled."
    expected: "One heading hierarchy per page, polite status announcements in reading order, immediate errors announced, disclosure state announced, and predictable post-transition focus; controls remain usable with keyboard only."
    why_human: "Announcement timing and intelligibility require assistive-technology judgment that string assertions cannot capture (04-VALIDATION manual matrix)."
  - test: "In light and dark modes with two very different custom accents, confirm Correct/Incorrect/Warning stay fixed colors with text/icon/border redundancy and remain distinguishable under a deuteranopia simulator."
    expected: "Verdict tokens are identical across accents, contrast-checked at 4.5:1, pairwise distinct, and never conveyed by color alone (text labels/badges present)."
    why_human: "Color-blind safety is a perceptual property; tests prove token invariance/contrast/distinctness but not human perception under a simulator."
  - test: "Two-editor day scenario: open day edit in the browser, change a cell, save the same plan externally (Obsidian), then save in the browser."
    expected: "A no-write conflict appears with the exact heading 'Plan changed outside itembank - nothing was overwritten.', labeled Your draft/Current file panes, copy/download for each, Reload current, Reapply draft, dirty warning, and Force overwrite absent until a conflict; a third external edit produces a new conflict, never an overwrite."
    why_human: "Real interleaving of two editors and recovery-flow judgment require a live scenario; the automated HTTP test proves the same contract programmatically (check_day_edit_conflict_and_force)."
  - test: "Backstop items (verification: backstop, reason: insufficient_spec): at 320 CSS px and 200% zoom with long stems/objectives/options, long report tables/lesson prose/settings help, long study explanations, and long day column labels/revisions/conflict documents, confirm content wraps/stack without clipping or page-level horizontal scroll, and revision/draft/current documents stay copyable."
    expected: "Narrow-width breakpoints, overflow-safe layout, pre-wrap/overflow-wrap rules, and stacked conflict panes hold in a real browser at 320px/200%; no content is clipped or hover-only."
    why_human: "Plans tagged these truths verification: backstop (non-inferable from spec alone). Automated tests assert the CSS structural rules only (presentation_roundtrip.test_responsive_zoom_and_noscript_fallback and per-surface overflow checks); a real browser render is required to confirm (honest-verifier abstention - insufficient_spec)."
  - test: "Visual adequacy of the polished surfaces: settings preview cards, migrated index/report/quiz/study/day, teaching-step primary-action emphasis, and study progressive reveal at both color modes."
    expected: "The reworked surfaces look finished and consistent; one visually primary next action per state; secondary actions cannot acquire the primary marker."
    why_human: "04-04 D12, 04-05 D9, and 04-06 D8 are explicitly marked human_judgment: true in the plans; final visual adequacy requires human UAT."
---

# Phase 4: Surface Redesign & Theming Verification Report

**Phase Goal:** As a learner, I want to read every surface from one visual system with an accent colour that follows my OS choice and to edit day plans safely in-page, so that the app feels like one product and my day edits never silently overwrite each other.
**Verified:** 2026-08-09T05:57:51Z
**Status:** human_needed
**Re-verification:** No - initial verification

## User Flow Coverage

User story: "As a learner, I want to read every surface from one visual system with an accent colour that follows my OS choice and to edit day plans safely in-page, so that the app feels like one product and my day edits never silently overwrite each other."

| Step | Expected | Evidence | Status |
|------|----------|----------|--------|
| Open the app | One daemon serves index, quiz, study, report, settings, and day; every surface reads from one visual system | `surfaces/daemon.py` route table (GET /, /quiz/<bank>, /study/<bank>, /report, /settings, /day/<stem>); `theme.theme_css(load_settings(root))` per render; `test_shared_accent_tokens_across_routes` PASS | ✓ automated (visual pass -> human) |
| Change the accent | `/settings` previews a browser color input or native picker accent live in light/dark, shows any contrast adjustment, saves only `accent.source`, and every surface updates on reload | `theme.py` `theme_page`/`persist_source`; `check_settings_page`, `test_theme_set_reset_contract`, `test_reload_after_save_updates_tokens` PASS | ✓ automated (live picker -> human) |
| Answer a quiz question | The page holds no key and performs no scoring; verdict and explanation come from `/api/submit` | `quiz.py` `page_for(serve=True)` empty item array; `SERVED_JS` `/api/start`->`/api/submit`; `check_quiz_no_key`, `check_served_api_flow`, `check_api_forged_fields` PASS | ✓ automated |
| Study a card | After deliberate reveal, study shows answer/why, every option with rationale, then second-best/discriminator/trap/notes; no local scoring | `study.py` `study_item` = `public_item` + `explain_payload`; `check_study_item_choice_payload`, `check_study_item_sentinels_reach_reveal`, `check_study_reveal_order` PASS | ✓ automated |
| Edit a day plan in-page | Structured single-line cell controls (no raw Markdown textarea); a save against a stale revision surfaces a no-write conflict instead of overwriting | `day.py` `day_page` + `apply_day_edit`; `check_edit_snapshot_and_form`, `check_day_edit_conflict_and_force` PASS | ✓ automated |
| Outcome: one product + day edits never silently overwrite each other | All five roadmap success criteria hold | SC1-SC5 all VERIFIED below (5/5) | ✓ automated (real-browser/UAT -> human) |

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The question surface shows one sticky context line in place of the current five chrome bands, with a real typographic hierarchy for the stem. | ✓ VERIFIED | `quiz_page.py` `.context-line{position:sticky...}`, one `data-surface-context` nav with bank/objective/Item N of M/mode, one native `<details>` for secondary metadata, `h1.stem` 28px/20px, reserved `.feedback` 96px/120px, one primary action per state; `check_question_hierarchy` PASS (exactly one context region, DOM order h1->control->feedback->action, 44px native controls, reduced-motion block). Old header/rail/tally live only in the offline `OFFLINE_JS`, which is substituted away in serve mode. |
| 2 | `study` renders the per-option rationale, second-best, and notes fields it currently discards, matching what the quiz surface already shows. | ✓ VERIFIED | `study.py` `study_item(q)` composes `public_item(q)` + `explain_payload(q, reveal=True)` with no field allowlist; `_explain_sections` renders answer/why, per-option rationale in adjacent native disclosures, then labelled Second-best answer / Discriminator / Common trap / Notes; `check_study_item_choice_payload`, `check_study_item_sentinels_reach_reveal`, `check_study_reveal_order` PASS. |
| 3 | Quiz, study, and `day` all read from one shared palette - `day` no longer carries its own literal-hex stylesheet - and the browser page holds no key and performs no scoring of its own; every verdict comes back from `/api/*`. | ✓ VERIFIED | `quiz.py` serve mode sends `items=[]` and the served client submits through `POST /api/submit` only; daemon injects `theme.theme_css(load_settings(root))` per render for quiz/study/day/index/report/settings; `DAY_CSS`/`STUDY_CSS` contain no hex/rgb/hsl literals (only semantic `var()` tokens); `check_quiz_no_key`, `check_served_api_flow`, `check_study_no_scorer_or_response`, `check_day_palette_and_no_css_literals`, `test_shared_accent_tokens_across_routes` PASS. |
| 4 | The accent colour is set from an OS colour picker, with light/dark pairs computed, contrast-checked, and correct/incorrect kept colour-blind safe. | ✓ VERIFIED | `theme.py` `pick_native_accent` (tkinter `colorchooser.askcolor`, hidden root, non-destructive fallback) plus `launcher.run_native_picker` fail-closed child bridge; `derive_theme` computes per-mode accent/accent-soft at 4.5:1 with hue preservation; `SEMANTIC_TOKENS` fixed per mode, contrast-checked, pairwise-distinct from accent, independent of the learner accent; `test_derived_accents_meet_contrast_and_report_correction`, `test_semantic_tokens_independent_and_contrast_checked`, `test_pick_unavailable_paths_never_write` PASS. Live OS-dialog interaction routed to human verification. |
| 5 | Editing a `day` plan in-page under an optimistic-concurrency guard does not silently overwrite an edit made in Obsidian at the same time - the conflict is surfaced, not lost. | ✓ VERIFIED | `day_document.save` compares SHA-256 at entry and again inside `_atomic_replace` immediately before `os.replace`; a mismatch returns a no-write conflict carrying draft, fresh current snapshot, both revisions; daemon `handle_day_edit` issues a one-use token bound to stem/current revision/draft hash, consumed before save, with fresh-read recheck catching a third version; `check_task2_conflict_no_write`, `check_task2_tight_window_recheck`, `check_task2_confirmed_force`, and `check_day_edit_conflict_and_force` (live HTTP daemon) PASS. |

**Score:** 5/5 truths verified (5 verified, 0 present-but-behavior-unverified)

### Deferred Items

None - all roadmap success criteria are met; no gap is deferred to a later phase.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `surfaces/quiz_page.py` | API-driven served-question shell and compact accessible hierarchy | ✓ VERIFIED | Exists (42,937 bytes), substantive (sticky context line, h1 stem, reserved feedback, native controls), wired (daemon calls `quiz.page_for(serve=True)`), data flows from `/api/start` -> `/api/submit`. |
| `surfaces/quiz.py` | Served-mode page without key/scorer; optional per-render theme | ✓ VERIFIED | `page_for(serve=True)` ships bootstrap metadata + empty item array; `theme_css` parameter with `THEME_CSS` default; offline path isolated. |
| `surfaces/daemon.py` | Allowlisted API session bootstrap, `/settings`, `/api/theme`, `/day/<stem>/edit`, per-request theme injection | ✓ VERIFIED | Routes wired (`handle_api_start/submit`, `handle_theme_post`, `handle_day_edit`, `handle_settings_get`); same-origin/loopback gates; `theme.theme_css(load_settings(handler.root))` per dynamic page. |
| `surfaces/theme.py` | Single palette source, color math, derived tokens, contrast correction, preview, native picker, theme CLI, settings page | ✓ VERIFIED | `derive_theme`, `theme_css`, `theme_preview`, `pick_native_accent`, `cmd_theme`, `theme_page`, `persist_source` all present and used; contrast 4.5:1 enforced; semantic tokens fixed. |
| `surfaces/presentation.py` | Behavior-free semantic-HTML default adapter and shared primitives | ✓ VERIFIED | `render_surface`, `surface_shell`, `teaching_step`, `state_panel`, `context_line`, `details_section`, `SHARED_CSS`; zero color literals; alternate-adapter seam tested. |
| `surfaces/study.py` | Complete runtime-derived study payload and accessible progressive explanation UI | ✓ VERIFIED | `study_item` composes canonical builders; progressive reveal with recall toggles, rationale disclosures, per-state primary actions; no scorer/response path; theme from settings beside the bank. |
| `surfaces/day_document.py` | Lossless dated-row snapshot, SHA-256 revisions, byte patch, atomic replacement, no-write conflict | ✓ VERIFIED | `snapshot`/`save`; double revision check (entry + immediately before `os.replace`); conflict carries draft + fresh current; force never bypasses the byte gate. |
| `surfaces/day.py` | Structured edit mode, draft state, conflict recovery, dirty warning, day-state refresh, shared palette | ✓ VERIFIED | `day_page` embeds snapshot; `apply_day_edit` is the one surface wrapper around `day_document.save`; `DAY_CSS` palette-free; `day_render` injects `theme_css(load_settings(...))`. |
| `surfaces/settings.py` | Validated settings load/write with Phase 4 keys active | ✓ VERIFIED | `THIS_PHASE` advanced to 4; `load_settings`/`write_settings` merge schema defaults; only normalized `accent.source` is persisted. |
| `surfaces/launcher.py` | Fixed-argv source/`.pyz` native-picker child bridge, fail-closed | ✓ VERIFIED | `run_native_picker` builds no-shell argv, bounded JSON validation, fails closed on spawn/non-zero/oversize/malformed output. |
| `schemas/settings.schema.json` | Backward-compatible persisted source accent contract | ✓ VERIFIED | `theme: system|light|dark` unchanged; required `accent: {source: #RRGGBB}` default `#0e6e62`, pattern + minLength 7, `additionalProperties: false`. |
| `itembank.json` | Shipped default accent source | ✓ VERIFIED | Contains `accent.source` default so pre-Phase-4 files load through merged defaults. |
| `tests/day_edit_roundtrip.py`, `tests/theme_roundtrip.py`, `tests/presentation_roundtrip.py`, `tests/surface_roundtrip.py`, `tests/daemon_roundtrip.py`, `tests/config_roundtrip.py` | Phase-wide executable harness and behavior assertions | ✓ VERIFIED | All six exist and run; the 20 named checks below pass. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `surfaces/quiz_page.py` (served client) | `/api/start` and `/api/submit` | `SERVED_JS` `api("/api/start"...)` / `api("/api/submit", {session_id, answer})` | ✓ WIRED | `check_served_api_flow`, `check_quiz_no_key` PASS |
| `surfaces/daemon.py` | `surfaces/session.py` | `handle_api_start`/`handle_api_submit` call `session.do_start`/`session.do_submit` | ✓ WIRED | `/api/*` handlers contain `SystemExit` -> 400; forged fields refused |
| `surfaces/daemon.py` | `surfaces/theme.py` | `theme.theme_css(load_settings(handler.root))` on every dynamic page | ✓ WIRED | `test_shared_accent_tokens_across_routes`, `test_reload_after_save_updates_tokens` PASS |
| `surfaces/theme.py` | `surfaces/settings.py` | `cmd_theme`/`persist_source` -> `load_settings`/`write_settings` | ✓ WIRED | `test_theme_set_reset_contract`, schema-additive test PASS |
| `surfaces/launcher.py` | `itembank theme pick --json` | fixed no-shell child argv | ✓ WIRED | `test_launcher_run_native_picker_bridge`, `test_launcher_run_native_picker_fails_closed` PASS |
| `surfaces/day.py` | `surfaces/day_document.py` | `apply_day_edit` delegates every write to `day_document.save`; `day_render` uses `snapshot` | ✓ WIRED | `check_apply_day_edit_and_cache`, `check_edit_snapshot_and_form` PASS |
| `surfaces/daemon.py` | `surfaces/day.py` | allowlisted `POST /day/<stem>/edit` -> `day.apply_day_edit` | ✓ WIRED | `check_day_edit_route`, `check_day_edit_conflict_and_force` PASS |
| day editor boot state | `POST /day/<stem>/edit` | revision + changed cells only; no filesystem path or full-file replacement | ✓ WIRED | `DAY_EDIT_ALLOWED_FIELDS`; unknown fields refused with 400 |
| `surfaces/day.py` | `surfaces/theme.py` | `day_render` loads settings and injects `theme_css`; `DAY_CSS` consumes semantic `var()` tokens | ✓ WIRED | `check_day_palette_and_no_css_literals` PASS |
| `surfaces/study.py` | `runtime.explain_payload` | `study_item` composes `public_item` + `explain_payload(reveal=True)` | ✓ WIRED | `check_study_item_sentinels_reach_reveal` PASS |
| `surfaces/study.py` | `surfaces/theme.py` | `study_page` loads settings beside the bank, calls `theme_css` | ✓ WIRED | `check_study_theme_and_palette` PASS |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Served quiz page | item + verdict | `POST /api/start` -> `session.do_start` (real bank parse); `POST /api/submit` -> `runtime.score_response` | Yes | ✓ FLOWING |
| Study cards | `study_item(q)` payload | `runtime.public_item` + `runtime.explain_payload` over the parsed bank | Yes | ✓ FLOWING |
| Day editor | `window.__day__.snapshot` | `day_document.snapshot(plan_path, ...)` over real plan bytes | Yes | ✓ FLOWING |
| Theme on all surfaces | `theme_css(config)` tokens | `settings.load_settings(root)` -> `itembank.json`/schema defaults | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| SC5: stale save -> no-write conflict, draft + fresh current retained | `tests/day_edit_roundtrip.check_task2_conflict_no_write` | PASS | ✓ |
| SC5: revision re-check immediately before `os.replace` (race window) | `tests/day_edit_roundtrip.check_task2_tight_window_recheck` | PASS | ✓ |
| SC5: confirmed force requires second confirmation + fresh revision; third version re-conflicts | `tests/day_edit_roundtrip.check_task2_confirmed_force` | PASS | ✓ |
| SC5: live HTTP conflict/force/token/replay/third-version flow | `tests/daemon_roundtrip.check_day_edit_conflict_and_force` | PASS | ✓ |
| SC1: one sticky context line, DOM order, stem h1, 44px native controls, reserved feedback | `tests/surface_roundtrip.check_question_hierarchy` | PASS | ✓ |
| SC2: study payload completeness + sentinels reach reveal + reveal order | `tests/surface_roundtrip.check_study_item_choice_payload` / `check_study_item_sentinels_reach_reveal` / `check_study_reveal_order` | PASS | ✓ |
| SC3: served quiz holds no key | `tests/daemon_roundtrip.check_quiz_no_key` | PASS | ✓ |
| SC3: served quiz verdicts/evidence through `/api/*` | `tests/daemon_roundtrip.check_served_api_flow` + `check_api_forged_fields` | PASS | ✓ |
| SC3: study client has no scorer/response path | `tests/surface_roundtrip.check_study_no_scorer_or_response` | PASS | ✓ |
| SC3: `DAY_CSS` palette-free; shared tokens across routes | `tests/day_edit_roundtrip.check_day_palette_and_no_css_literals`; `tests/presentation_roundtrip.test_shared_accent_tokens_across_routes` | PASS | ✓ |
| SC4: derived accents meet 4.5:1; semantic tokens independent/contrast-checked; picker unavailable paths never write | `tests/theme_roundtrip.test_derived_accents_meet_contrast_and_report_correction` / `test_semantic_tokens_independent_and_contrast_checked` / `test_pick_unavailable_paths_never_write` | PASS | ✓ |
| SC4: palette matches binding values; forced modes preserve semantic tokens; CLI set/reset contract | `tests/theme_roundtrip.test_palette_matches_binding_values` / `test_theme_css_modes`; `tests/config_roundtrip.test_theme_set_reset_contract` | PASS | ✓ |
| Settings page and study theme parity | `tests/daemon_roundtrip.check_settings_page`; `tests/surface_roundtrip.check_study_theme_and_palette` | PASS | ✓ |
| Day editor boot snapshot/form + empty/error study states | `tests/day_edit_roundtrip.check_edit_snapshot_and_form`; `tests/surface_roundtrip.check_study_empty_and_error_states` | PASS | ✓ |
| Review fixes: script-safe JSON (quiz/day), fresh-current conflict doc, non-UTF-8 conflict, cross-origin gates | `check_quiz_script_safety`, `check_day_script_safety`, `check_conflict_document_uses_fresh_current`, `check_task2_conflict_non_utf8_current`, `check_cross_origin_gate_on_mutating_routes` | PASS | ✓ |

### Probe Execution

SKIPPED - no phase-declared probes and no conventional `scripts/*/tests/probe-*.sh` files exist in the repository. Phase 4 uses standalone `tests/*.py` assertion scripts, which are the named behavioral checks above.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| SURF-02 | 04-01 | The browser page is a client of the same JSON API an agent uses; it holds no key and implements no scoring | ✓ SATISFIED | `check_quiz_no_key`, `check_served_api_flow`, `check_api_forged_fields` PASS |
| SURF-05 | 04-01 | The question surface shows one sticky context line rather than five bands of chrome above the stem | ✓ SATISFIED | `check_question_hierarchy` PASS; template + `SERVED_JS` show one context nav + one details disclosure |
| SURF-06 | 04-05 | `study` renders the per-option rationale, second-best, and notes it currently discards | ✓ SATISFIED | `check_study_item_*` + `check_study_reveal_order` PASS |
| SURF-07 | 04-04, 04-05, 04-06 | The whole tool uses one palette; the `day` page stops being a third stylesheet in literal hex | ✓ SATISFIED | `test_shared_accent_tokens_across_routes`, `check_day_palette_and_no_css_literals`, `check_study_theme_and_palette` PASS |
| SURF-08 | 04-03, 04-04 | The accent colour is set from the OS colour picker with light and dark pairs computed from it, and correct/incorrect stay contrast-checked and colour-blind safe | ✓ SATISFIED | theme contrast/semantic/picker tests PASS; live picker interaction -> human verification |
| SURF-09 | 04-02, 04-06 | `day` supports in-page editing with an optimistic-concurrency guard, so an edit cannot silently overwrite one made in Obsidian | ✓ SATISFIED | `check_task2_conflict_no_write`, `check_task2_tight_window_recheck`, `check_day_edit_conflict_and_force` PASS |

Note: `REQUIREMENTS.md` still shows SURF-02 and SURF-05 with unchecked `- [ ]` boxes even though the code and tests satisfy them (04-01 lists both as completed). This is a stale tracking-file checkbox, not a code gap; the phase plans claimed and delivered both requirements. Also, SURF-09's literal wording "full in-page markdown editing" is implemented as structured cell editing (D-08 deliberately forbids a raw Markdown textarea); the roadmap success criterion (safe in-page editing under an optimistic-concurrency guard) is met and the structured form is the documented design.

### Anti-Patterns Found

No blocker or warning anti-patterns found in files modified by Phase 4.

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `surfaces/cli.py` | 235 | Stale help text "`daily` is not yet implemented (plan 01-10)" | ℹ️ Info | Pre-existing Phase 1-era text outside Phase 4's diff scope; the `daily` render path was implemented by plan 01-10. No Phase 4 behavior affected. |
| `surfaces/quiz_page.py` | 479, 887 | `textarea.placeholder` attribute | ℹ️ Info | Legitimate input placeholder copy, not a stub. |
| `surfaces/theme.py:660`, `surfaces/day_document.py:498` | - | `except Exception: pass` | ℹ️ Info | Deliberate cleanup/finally and POSIX-only directory-fsync fallback; both paths return proper results. |

No `TBD`/`FIXME`/`XXX` debt markers, no empty implementations, no hardcoded empty data, and no disconnected props found in the Phase 4 files.

### Human Verification Required

The automated evidence above is green; the following require a human in a real browser/environment (per 04-VALIDATION manual matrix and the 04-06 end-of-phase human-check):

### 1. One-product visual walkthrough (light/dark, desktop and 320px/200%)

**Test:** Open the daemon and walk index, quiz, study, report, settings, and day in both color modes at desktop and 320px/200% zoom, keyboard-only.
**Expected:** Every surface reads as one product from the shared palette and primitives; quiz shows exactly one sticky context line, dominant stem, reserved feedback; no regression or clipping.
**Why human:** Perceptual hierarchy and real-browser rendering cannot be proven by string assertions (04-01 tracer gate deferred this to final-product validation).

### 2. Live native picker and browser fallback

**Test:** In `/settings`, open the OS color picker, cancel once, then use the browser color input, preview, save, reset, and reload all surfaces.
**Expected:** Selection is preview-only; cancel/unavailable shows the exact fallback copy and changes nothing; save persists only `accent.source`; every surface updates on reload in system/light/dark.
**Why human:** Tk/display interaction is environment-dependent; the live picker path is platform-gated out of CI (unit tests cover only the fail-closed mapping).

### 3. Screen-reader sequence

**Test:** Traverse quiz submit/verdict, study reveal, settings save error/fallback, and day validation/conflict with Narrator/NVDA/VoiceOver and reduced motion.
**Expected:** One heading hierarchy, polite statuses, immediate errors as alerts, disclosure state, and predictable post-transition focus.
**Why human:** Announcement timing and intelligibility require assistive-technology judgment.

### 4. Color-blind / non-color verdict check

**Test:** In light/dark with two very different accents, confirm Correct/Incorrect/Warning stay fixed colors with text/icon/border cues and are distinguishable under a deuteranopia simulator.
**Expected:** Semantic tokens fixed, contrast-checked, pairwise distinct, and never color-only.
**Why human:** Perceptual color-blind safety cannot be proven by contrast math alone.

### 5. Two-editor day conflict and recovery (real interleaving)

**Test:** Edit a day cell in the browser, save the plan externally (Obsidian), then save in the browser; also verify dirty-navigation warning and the full copy/download/reload/reapply/force flow, then a third external edit.
**Expected:** No-write conflict with exact heading, labeled draft/current panes, all recovery actions, Force absent until conflict, and a third version re-conflicts rather than overwrites.
**Why human:** Real editor interleaving and recovery-flow judgment require a live scenario (the automated HTTP test proves the programmatic contract only).

### 6. Backstop items (320px/200% zoom, long content) - 5 abstained truths

**Test:** With long stems/objectives/options, long report tables/lesson prose/settings help, long study explanations, and long day labels/revisions/conflict documents at 320px and 200% zoom, verify wrapping/stacking, selectability, and no page-level horizontal scroll.
**Expected:** Content wraps/stacks without clipping or hover-only access; revisions and conflict documents remain copyable/downloadable.
**Why human:** Plans tagged these truths `verification: backstop` (insufficient spec - honest-verifier abstention). Automated tests assert only the structural CSS rules (`test_responsive_zoom_and_noscript_fallback` and per-surface overflow checks), not real-browser rendering.

### 7. Visual adequacy of reworked surfaces

**Test:** Inspect settings preview cards, migrated index/report/quiz/study/day, teaching-step primary-action emphasis, and study progressive reveal in both modes.
**Expected:** Polished, consistent, with exactly one visually primary next action per state.
**Why human:** Plan 04-04 D12, 04-05 D9, and 04-06 D8 are marked `human_judgment: true`.

### Gaps Summary

No gaps were found: all five roadmap success criteria are verified by code evidence and passing named behavioral tests, all required artifacts exist and are substantive, wired, and flowing real data, all key links are wired, and no blocker anti-patterns were found. The phase status is `human_needed` because the remaining items are real-browser, assistive-technology, native-picker, color-blind, and two-editor recovery checks that automated verification cannot perform - matching the phase's own 04-VALIDATION manual matrix and the 04-06 end-of-phase human-check. No override is required; no item is deferred to a later phase.
## Deferred Verification Run (2026-08-11) — live execution

Executed live in a python-capable environment: fresh sibling worktree
(`itembank-phase-verify`, branch `gsd/deferred-verify`, from main tip
`801ae8f`).

### Automated checks (exact commands and results)

| Check | Command | Result |
|-------|---------|--------|
| Full roundtrip suite (40 files) | `python tests/*_roundtrip.py` (invoked per file in `&&` chains) | PASS — every file exits 0 |
| Phase harness: day-edit | `python tests/day_edit_roundtrip.py` | PASS — snapshot/conflict/force/tight-window recheck + live HTTP flow |
| Phase harness: theme | `python tests/theme_roundtrip.py` | PASS — derivation/contrast/semantic-independence/mode CSS/preview/picker lifecycle/child bridge |
| Phase harness: presentation | `python tests/presentation_roundtrip.py` | PASS |
| Phase harness: surface | `python tests/surface_roundtrip.py` | PASS — question hierarchy, study payload/reveal order, no-scorer, theme parity |
| Phase harness: daemon | `python tests/daemon_roundtrip.py` | PASS — 63 checks incl. served-quiz no-key, `/api/*` flow, settings page, day conflict flow |
| Phase harness: config | `python tests/config_roundtrip.py` | PASS — theme set/reset contract |

### Truth status updates

Truths 1-5 are live-verified this run — every one of the 20 named behavioral
checks in the Behavioral Spot-Checks table passes. The five UAT items that
carried recorded automated evidence in `04-UAT.md` (2026-08-10) stand
verified with those citations: real-browser DOM walkthrough (test 1), theme
save/preview HTTP contract (test 2), colour-blind contrast math (test 4),
two-editor conflict lifecycle over HTTP (test 5), and 320px/200% headless
renders with 12 screenshots saved (test 6). The two UAT-blocked items
(tests 3 and 7) and the visual/perceptual items remain human.

### HUMAN-REQUIRED (exact manual steps; 7 items)

1. **One-product visual walkthrough (light/dark, desktop + 320px/200%).**
   Open the daemon and walk index, quiz, study, report, settings, and day in
   both colour modes at desktop and 320px/200% zoom, keyboard-only. Expected:
   every surface reads as one product from the shared palette and primitives;
   the quiz page shows exactly one sticky context line, a dominant stem h1,
   and a reserved feedback region; no layout regression or clipping.
2. **Live native picker and browser fallback.** In `/settings`, open the OS
   colour picker, cancel once, then use the browser colour input, preview,
   save, reset, and reload every surface. Expected: selection is
   preview-only; cancel/unavailable shows the exact fallback copy (`System
   picker is unavailable here. Choose a color below instead.`) and changes
   nothing; save persists only `accent.source`; every surface updates on
   reload in system/light/dark.
3. **Screen-reader sequence (Narrator/NVDA/VoiceOver) with reduced motion.**
   Traverse quiz submit/verdict, study reveal, settings save error/fallback,
   and day conflict recovery. Expected: one heading hierarchy per page, polite
   status announcements in reading order, immediate errors announced,
   disclosure state announced, predictable post-transition focus, keyboard-
   only usable.
4. **Colour-blind / non-colour verdict check.** In light and dark modes with
   two very different custom accents, confirm Correct/Incorrect/Warning stay
   fixed colours with text/icon/border redundancy, contrast-checked at 4.5:1,
   pairwise distinct, and remain distinguishable under a deuteranopia
   simulator.
5. **Two-editor day conflict and recovery (real interleaving).** Edit a day
   cell in the browser, save the same plan externally (Obsidian), then save
   in the browser. Expected: a no-write conflict with the exact heading `Plan
   changed outside itembank - nothing was overwritten.`, labelled Your
   draft/Current file panes, copy/download for each, Reload current, Reapply
   draft, dirty warning, Force absent until a conflict; a third external edit
   produces a new conflict, never an overwrite.
6. **Backstop items (320px/200% zoom, long content).** With long
   stems/objectives/options, long report tables/lesson prose/settings help,
   long study explanations, and long day labels/revisions/conflict documents
   at 320px and 200% zoom, verify wrapping/stacking, selectability, and no
   page-level horizontal scroll; revisions and conflict documents stay
   copyable. (12 headless screenshots were saved by the 2026-08-10 automated
   UAT run; pixel-level judgment remains human.)
7. **Visual adequacy of the reworked surfaces.** Inspect settings preview
   cards, migrated index/report/quiz/study/day, teaching-step primary-action
   emphasis, and study progressive reveal in both colour modes. Expected:
   polished, consistent, exactly one visually primary next action per state;
   secondary actions never acquire the primary marker.

## Close-Out Live Re-Verification (2026-08-11T19:59Z — phase 04 close)

Executed live during phase-04 close-out in the dedicated close worktree
(`.phase04-wt`, branch `gsd/phase-04-close`, from main tip `2b5678c`). The
deferred-verify record above was ported from `gsd/deferred-verify`
(commit `e7c8634`) and every phase-04 truth was re-run fresh against the
current main code, not against that branch.

### Automated checks (exact commands and results)

| Check | Command | Result |
|-------|---------|--------|
| Phase harness: day-edit | `python tests/day_edit_roundtrip.py` | PASS — snapshot/conflict/force/tight-window recheck + palette migration |
| Phase harness: theme | `python tests/theme_roundtrip.py` | PASS — derivation/contrast/semantic-independence/mode CSS/preview/picker lifecycle/child bridge |
| Phase harness: presentation | `python tests/presentation_roundtrip.py` | PASS — semantic DOM, shared palette, responsive fixtures, alternate-adapter seam |
| Phase harness: surface | `python tests/surface_roundtrip.py` | PASS — question hierarchy, study payload/reveal order, no-scorer, theme parity |
| Phase harness: daemon | `python tests/daemon_roundtrip.py` | PASS — 69 checks incl. served-quiz no-key, `/api/*` flow, settings page, day conflict flow |
| Phase harness: config | `python tests/config_roundtrip.py` | PASS — theme set/reset contract |
| Full suite | every `tests/*.py` (45 files, run individually) | 42 PASS; 3 failures — see out-of-scope findings below |
| Sample bank lint | `python itembank.py lint fixtures/sample_bank.md` | PASS — 0 errors, 6 pre-existing fixture warnings |
| Published schemas | `python itembank.py schema --all` | PASS — full contract emits and self-validates |
| Session schema | `python itembank.py start fixtures/sample_bank.md --count 3 --seed 1 --out /tmp/p4s.json` then `python schema_validate.py schemas/session.schema.json /tmp/p4s.json` | PASS — 1 instance, 0 errors |

### Truth status updates (re-run live, this close worktree)

Truths 1-5 are re-verified VERIFIED this run — every named behavioral check
below passes against the current main code:

| # | Truth | Status | Fresh evidence this run |
|---|-------|--------|-------------------------|
| 1 | One sticky context line, stem h1, reserved feedback | ✓ VERIFIED | `surface_roundtrip.check_question_hierarchy` PASS |
| 2 | Study renders per-option rationale, second-best, notes | ✓ VERIFIED | `surface_roundtrip.check_study_item_choice_payload` / `check_study_item_sentinels_reach_reveal` / `check_study_reveal_order` PASS |
| 3 | One shared palette; `day` carries no literal-hex CSS; served pages hold no key/scorer | ✓ VERIFIED | `day_edit_roundtrip.check_day_palette_and_no_css_literals`, `presentation_roundtrip.test_shared_accent_tokens_across_routes`, `daemon_roundtrip.check_quiz_no_key` / `check_served_api_flow` / `check_study_no_scorer_or_response` PASS |
| 4 | Accent from OS picker, light/dark pairs computed, contrast-checked, colour-blind safe | ✓ VERIFIED | `theme_roundtrip.test_derived_accents_meet_contrast_and_report_correction` / `test_semantic_tokens_independent_and_contrast_checked` / `test_pick_unavailable_paths_never_write` / `test_palette_matches_binding_values` / `test_theme_css_modes` + child-bridge checks; `config_roundtrip.test_theme_set_reset_contract` PASS. Live OS-dialog interaction itself remains human (item 2 below). |
| 5 | Optimistic-concurrency day editing, conflict surfaced never overwritten | ✓ VERIFIED | `day_edit_roundtrip.check_task2_conflict_no_write` / `check_task2_tight_window_recheck` / `check_task2_confirmed_force`; `daemon_roundtrip.check_day_edit_conflict_and_force` (live HTTP) PASS |

### Human items — status: PENDING HUMAN (unchanged)

The seven items listed in the HUMAN-REQUIRED section above (one-product
visual walkthrough, live native picker + browser fallback, screen-reader
sequence with reduced motion, colour-blind/non-colour verdict check,
two-editor day conflict in real interleaving, backstop 320px/200% long
content, visual adequacy of reworked surfaces) remain **PENDING HUMAN**.
They are perceptual, assistive-technology, OS-dialog, or real-editor
interleaving checks that automated verification cannot perform; nothing was
fabricated and no item was silently marked verified. The 2026-08-10
automated UAT run's 12 headless screenshots remain saved for the human
review of the backstop and visual-adequacy items.

### Out-of-scope findings from the full-suite run (not phase 04)

The full 45-file suite is not fully green on current main; three failures
were observed. None is caused by or fixable within phase 04, and none
touches a phase-04 truth (all five truths above pass). They are recorded
here so the orchestrator can route them:

1. **`tests/evidence_roundtrip.py`** — FAIL at "index was not rebuilt at
   version 3 after the stale check". Pre-existing regression introduced by
   the 06.2 merge `d35bd15` into main: the merge kept `evidence.py`'s
   `INDEX_VERSION = 2` and dropped the index `context` column from the
   06.2-side projection, while the 06.2-side test (expecting version "3")
   came through unchanged. The index is disposable and self-consistent at
   v2, so user impact is limited to the failing test; the code/test
   mismatch needs a phase-06.2 owner.
2. **`tests/gate_roundtrip.py`** — FAIL at "rows must differ only by context
   in log order, got [None, None]". Same root cause: `objective_history`
   index rows carry no `context` key on merged main, so the GATE-03
   projection test fails. Same owner as above.
3. **`tests/packaging_roundtrip.py`** — FAIL at "dist/itembank-sidecar-onedir
   is missing". Environmental, not a code defect: the check requires the
   PyInstaller Windows onedir artifact built by
   `powershell -File scripts/build_shell.ps1`, which cannot run from this
   WSL shell (no Windows PowerShell interop) and which is not committed
   (only the triple-suffixed exe under `src-tauri/binaries/` is tracked).
   On a machine where the sidecar has been built, this check runs.

`phase_062_audit.py` fails for the same reason: its embedded full-suite run
reports exactly these three files; its own audit checks (6/6 GATE-ID
coverage, named verification commands exist, edge-probe sentences, and
`schema --all`) all pass.

**Close-out verdict:** the phase's five roadmap truths are all VERIFIED by
fresh live automated runs on the merged code; the phase's status remains
`human_needed` solely for the seven perceptual/assistive/OS items, which
stay PENDING HUMAN. The three full-suite failures above are pre-existing or
environmental and are outside phase 04's scope.

---

_Verified: 2026-08-11T15:30:00Z (deferred-verify record, ported); close-out re-verification 2026-08-11T19:59Z on gsd/phase-04-close_
_Verifier: the agent (gsd-verifier)_
