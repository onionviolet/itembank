---
phase: 04
slug: surface-redesign-theming
status: draft
nyquist_compliant: false
wave_0_complete: false
wave_0_plan: "04-01 task 1"
created: 2026-08-08
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for the Surface Redesign & Theming execution. Automated checks establish authority, state, data-preservation, token, and semantic-markup contracts; the end-of-phase manual pass covers perceptual layout, real browser/Tk behavior, keyboard/screen-reader flow, and concurrent-editor recovery.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Standalone Python assertion scripts using stdlib only |
| **Config file** | None; repository CI runs each `tests/*.py` file |
| **Quick run command** | `python tests/surface_roundtrip.py` |
| **Full suite command** | `Get-ChildItem tests -Filter *.py \| Sort-Object Name \| ForEach-Object { python $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run the task's named standalone test command.
- **After 04-01 Task 1 (Wave 0):** Run all five harness scripts; keep `wave_0_complete: false` until this task has executed successfully, then set it true in the execution summary/update.
- **After every plan wave:** Run all Phase 4 focused scripts: `python tests/serve_roundtrip.py`, `python tests/daemon_roundtrip.py`, `python tests/surface_roundtrip.py`, `python tests/theme_roundtrip.py`, `python tests/presentation_roundtrip.py`, `python tests/day_edit_roundtrip.py`, `python tests/config_roundtrip.py`, and `python tests/day_roundtrip.py` (skip only not-yet-created Wave 0 scripts before their owning task).
- **Before `$gsd-verify-work`:** The full repository suite must be green, followed by the manual matrix below.
- **Max feedback latency:** 60 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 0 | Phase validation foundation | — | Executable stdlib harness/fixtures exist before production; no production file changes | infrastructure | `@('tests/day_edit_roundtrip.py','tests/theme_roundtrip.py','tests/presentation_roundtrip.py','tests/surface_roundtrip.py','tests/daemon_roundtrip.py') \| ForEach-Object { python $_; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }` | 3 ❌ W0 / 2 ✅ extend | ⬜ pending |
| 04-01-02 | 01 | 0 | SURF-02, SURF-05 | T-04-01..04 | Served HTML has no key/scorer; allowlisted `/api/*` owns verdict/explanation/evidence | integration | `python tests/serve_roundtrip.py` | ✅ | ⬜ pending |
| 04-01-03 | 01 | 0 | SURF-05 | T-04-04 | One sticky context, semantic controls/status, stable loading/error/completion layout | contract | `python tests/surface_roundtrip.py` | ✅ extend W0 | ⬜ pending |
| 04-02-01 | 02 | 1 | SURF-09 | T-04-05..07 | Exact supported/refused grammar and byte-span-only atomic edits | unit/integration | `python tests/day_edit_roundtrip.py` | ❌ W0 | ⬜ pending |
| 04-02-02 | 02 | 1 | SURF-09 | T-04-05, T-04-08 | Fresh SHA-256 comparison, no-write conflict, confirmed reapply against newest bytes | integration | `python tests/day_edit_roundtrip.py` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 2 | SURF-08 | T-04-09..11 | Deterministic contrast-qualified accent pairs and fixed semantic verdict palette | unit | `python tests/theme_roundtrip.py` | ❌ W0 | ⬜ pending |
| 04-03-02 | 03 | 2 | SURF-08 | T-04-09 | Additive source-only schema; old-file defaults; atomic validated preview/set/reset | integration | `python tests/config_roundtrip.py` | ✅ | ⬜ pending |
| 04-03-03 | 03 | 2 | SURF-08 | T-04-12 | Main-thread native picker, source/`.pyz` child bridge, exact fallback copy, and no mutation/resource leak | unit | `python tests/theme_roundtrip.py` | ❌ W0 | ⬜ pending |
| 04-04-01 | 04 | 3 | SURF-08 | T-04-13, T-04-14, T-04-16 | Same-origin loopback mutation/picker; LAN preview only; source validation | integration | `python tests/daemon_roundtrip.py` | ✅ extend W0 | ⬜ pending |
| 04-04-02 | 04 | 3 | SURF-07, SURF-08 | T-04-15 | Shared semantic adapter/fallback and one token source across index/report/settings/quiz | contract/integration | `python tests/presentation_roundtrip.py` | ❌ W0 | ⬜ pending |
| 04-05-01 | 05 | 4 | SURF-06 | T-04-17, T-04-19 | Canonical complete explanation payload and script-safe rendering | unit/contract | `python tests/surface_roundtrip.py` | ✅ extend W0 | ⬜ pending |
| 04-05-02 | 05 | 4 | SURF-06, SURF-07 | T-04-18, T-04-20, T-04-26 | Deliberate reveal, relevant disclosures, no local verdict, shared study palette | contract | `python tests/surface_roundtrip.py`, `python tests/theme_roundtrip.py`, `python tests/presentation_roundtrip.py` | W0 | ⬜ pending |
| 04-06-01 | 06 | 5 | SURF-09, SURF-07 | T-04-21, T-04-22, T-04-27 | Plan-allowlisted structured edit; exact `Plan not saved. Fix the highlighted cells and try again.` announcement with highlighted-cell associations; separately draft-preserving errors; no independent day palette | integration | `python tests/day_edit_roundtrip.py` | ❌ W0 | ⬜ pending |
| 04-06-02 | 06 | 5 | SURF-09 | T-04-22..25 | Recoverable conflict plus revision/draft/stem-bound one-use force gate | integration | `python tests/daemon_roundtrip.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Requirement and UI Contract Coverage

| Contract | Automated evidence | Manual evidence |
|----------|--------------------|-----------------|
| SURF-02 browser authority | Served-source secret/scorer assertions; `/api/start`→`/api/submit`; forged-field and evidence tests | DevTools/source spot-check: current item survives API-unavailable state and no offline verdict appears |
| SURF-05 question hierarchy | DOM order, one context region/`h1`, native input, status, focus/reduced-motion/responsive structural checks | Desktop + 320px/200%, keyboard and screen-reader pass with long objective/stem/options |
| SURF-06 study explanations | Sentinel coverage for every `explain_payload` field/type; disclosure/default-open/no-score assertions | Flash/Learn deliberate reveal, chosen/correct rationale relevance, long notes/model/rubric review |
| SURF-07 one palette | Plan 04 covers index/report/settings/quiz token equality; plan 05 covers study; plan 06's day-focused test enforces generated-token parity and scoped `DAY_CSS` literal-color prohibition | Reload index/quiz/study/day/report/settings after accent save in system/light/dark |
| SURF-08 accessible OS accent | Exact schema/default/base/semantic values, deterministic ratios/corrections, picker failure and LAN policy tests | Real browser color field and host picker success/cancel/fallback; light/dark and color-blind/non-color verdict inspection |
| SURF-09 structured optimistic day edit | Exact grammar corpus, byte diff, atomic replace, stale/third-version conflict, token replay/binding tests | Two-editor Obsidian/browser conflict recovery, dirty warning, copy/download/reload/reapply/force flow |
| Shared presentation adapter | Default semantic output, dummy alternate adapter view boundary, fallback/no-script, teaching-step and state-panel tests | Confirm polished low-chrome default, concise focused prompts, progressive details, immediate status, and one obvious next action; semantic fallback stays usable when enhancement is disabled |
| Lesson-compatible presentation | Synthetic prose/teaching-step/headings/link/code/table/disclosure overflow contract only | If Phase 3 is present, inspect its reader in both modes; otherwise verify the synthetic contract without adding lesson behavior |
| States matrix | Structural/content assertions for quiz/study/index/report/settings/day loading, empty, error, unavailable, partial, conflict states | Focus recovery, announcement timing, draft/content retention, and action clarity across each state |

Later-phase exclusions are checked by source review during verification: no hint ladder/generated-hint review, subject/media integration, pacing/trends, auditor authoring, canvas renderer, or plugin framework is introduced by Phase 4.

---

## Wave 0 Requirements

Plan `04-01`, Task 1 owns this entire foundation and executes before the phase's tracer or any other production task:

- [ ] Create executable `tests/theme_roundtrip.py` fixture/assertion infrastructure for color extraction/contrast, settings bases, picker mocks, source/`.pyz` child seams, exact fallback copy `System picker is unavailable here. Choose a color below instead.`, and cross-surface render collection. Plans 04-03 through 04-05 add their feature assertions RED-first.
- [ ] Create executable `tests/day_edit_roundtrip.py` fixture/assertion infrastructure for the exact grammar corpus, raw-byte/hash comparisons, concurrency rewrites, and CLI/HTTP helpers. Plans 04-02 and 04-06 add their feature assertions RED-first.
- [ ] Create executable `tests/presentation_roundtrip.py` fixture/assertion infrastructure for semantic parsing, teaching steps, behavior-free adapter probes, long content, states, and lesson-compatible synthetic data. Plans 04-04 through 04-06 add their feature assertions RED-first.
- [ ] Extend `tests/surface_roundtrip.py` with reusable sentinel-bank/explanation and semantic-DOM helpers while preserving current checks.
- [ ] Extend `tests/daemon_roundtrip.py` with reusable JSON, loopback/LAN, route-order, temporary plan/settings, and force-token helpers while preserving current checks.

No dependency or framework install is needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Polished hierarchy and stable quiz feedback | SURF-05 | Perceptual hierarchy/layout shift cannot be fully proven by string assertions | Open a served quiz in system/light/dark. At desktop and 320px/200%, inspect one sticky line, dominant stem, adjacent response, reserved feedback, long content, loading/checking/error/completion. Submit with keyboard only and confirm focus/status behavior. |
| Real native picker and browser fallback | SURF-08 | Tk/display/packaged/browser interaction is environment-dependent | From local app/daemon `/settings`, choose through the OS picker, cancel once, save through the browser field, reset, then simulate/unavailable Tk if possible. Verify exact fallback/correction copy, draft retention, explicit save, and global reload across surfaces. |
| Screen-reader state sequence | SURF-05, SURF-06, SURF-09 | Announcement timing and intelligibility need assistive-technology judgment | With Narrator/NVDA/VoiceOver, traverse quiz, study reveal, settings save error/fallback, and day validation/conflict. Confirm one heading hierarchy, polite statuses, immediate errors only as alerts, disclosure state, and predictable post-transition focus. |
| Semantic verdict/color-blind safety | SURF-05, SURF-08 | Color distinction and visual redundancy need human perception | In light/dark with two very different custom accents, confirm Correct/Incorrect/Warning retain fixed colors plus text/icon/border cues and remain distinguishable under a deuteranopia simulator. |
| Two-editor conflict and recovery | SURF-09 | Requires real interleaving and recovery judgment | Open day edit, change a cell, edit/save the plan externally, then save in browser. Verify exact conflict heading, both full versions, copy/download each, reload/reapply, Force absent until conflict, dirty warning, and another external edit causing a new conflict rather than overwrite. |
| Progressive teaching presentation and fallback | SURF-05, SURF-06, SURF-07, SURF-09 | Focus/clarity and browser failure presentation need human judgment | In quiz, study, and lesson-compatible prose, confirm a short focused step, progressively disclosed supporting detail, immediate status, and one unmistakable next action without copied branding. Then disable JavaScript or force enhancement initialization failure and verify semantic orientation/content/recovery remains readable; operations may explain unavailability but must not disappear behind canvas/graphical output. |
| Lesson-compatible shell | SURF-07 | Actual lesson route depends on the earlier phase's execution state | If Phase 3 artifacts exist, open a long prose lesson with headings, link, code/table and disclosure in both modes at 320px. If absent, inspect only `tests/presentation_roundtrip.py`'s synthetic contract; do not add lesson features here. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verification and their Wave 0 scripts exist before implementation.
- [ ] Sampling continuity: no three consecutive tasks lack a focused automated run.
- [ ] `04-01` Task 1 has run successfully and `wave_0_complete: true` is recorded; all dependent plans use direct automated commands with no `MISSING` marker.
- [ ] No watch-mode flag or interactive test command blocks execution.
- [ ] Focused feedback latency remains under 60 seconds.
- [ ] Exact D-01 through D-14 and SURF-02/05/06/07/08/09 coverage is green.
- [ ] Manual UI/accessibility/concurrency matrix is complete with evidence recorded in verification/UAT artifacts.
- [ ] `nyquist_compliant: true`, `wave_0_complete: true`, and `status: validated` are set only after the checks exist and pass.

**Approval:** pending
