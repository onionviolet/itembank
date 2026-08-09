---
phase: 04-surface-redesign-theming
plan: 04-01
subsystem: quiz-surface
tags: [quiz, api-authority, hierarchy, accessibility, tracer]
key-files:
  created:
    - tests/day_edit_roundtrip.py
    - tests/theme_roundtrip.py
    - tests/presentation_roundtrip.py
  modified:
    - surfaces/quiz_page.py
    - surfaces/quiz.py
    - surfaces/daemon.py
    - tests/daemon_roundtrip.py
    - tests/serve_roundtrip.py
    - tests/surface_roundtrip.py
    - tests/lesson_roundtrip.py
    - tests/evidence_roundtrip.py
key-decisions:
  - "The served quiz page is a client of the canonical /api/start -> /api/submit JSON API (SURF-02): bootstrap metadata only, no key, no scorer, no full item array; every verdict and explanation comes from the server."
  - "One sticky context line (bank/lesson context, objective, item N of M, session mode) replaces the header/rail/tally chrome; secondary metadata lives in one native details disclosure (D-01)."
  - "Native controls: mc is a radio fieldset, multi is checkboxes, all controls have a 44px target; the stem is the page's single dominant h1 (28px wide / 20px narrow); the feedback region is reserved at 96px/120px (D-02/D-03)."
requirements-completed: [SURF-02, SURF-05]
completed: 2026-08-08
---

# Plan 04-01 Summary - Wave 0 Harness, API-Authority Tracer, Question Hierarchy

**Objective:** Create the Phase 4 validation harness first, then make the
served question page a real client of the canonical JSON session API and
replace its stacked chrome with one accessible answering hierarchy per D-01,
D-02, and D-03.

## What Was Built

- **Task 1 (executor):** the three missing standalone harness modules
  (`tests/day_edit_roundtrip.py`, `tests/theme_roundtrip.py`,
  `tests/presentation_roundtrip.py`) plus reusable semantic-DOM/sentinel
  helpers in `tests/surface_roundtrip.py` and JSON/route helpers in
  `tests/daemon_roundtrip.py`. No production changes.
- **Task 2 (executor, tracer):** the served quiz page now drives the sitting
  through POST `/api/start` and POST `/api/submit`. The served HTML carries
  bootstrap metadata only (allowlisted bank stem, count, mode, resolving
  lesson slugs); forged item-id/score/key/explanation/bank-path/out/session
  fields are rejected with 400; evidence is recorded exactly once; the
  scoped `serve` attempt view refreshes atomically; the static `build`
  compatibility path stays isolated and green.
- **Task 3 (orchestrator):** collapsed the header, rail, tally, card-meta
  band and save-state strip into one sticky `.context-line`
  (`data-surface-context`): bank/lesson context, objective, `Item N of M`,
  and session mode. Secondary metadata (type, difficulty, no-partial-credit,
  dichotomous note) moved into one native `<details><summary>Session
  details</summary>`. The stem is the single dominant `h1` (28px wide, 20px
  narrow); mc renders as a native radio fieldset and multi as native
  checkboxes (44px targets); a reserved `role=status` feedback region
  (96px/120px min-height) sits between the controls and the primary action;
  the primary CTA is `Submit answer`; reduced-motion disables transitions
  and smooth scrolling; loading/checking/error/empty/completed states use
  the same shell with keyboard-reachable recovery actions.

## Commits

| Task | Commit |
|------|--------|
| Task 1 - Wave 0 harness foundation | e40f0c5 |
| Task 2 - API-authority tracer (RED + GREEN) | c5b6947, ae797c0 |
| Task 3 - sticky context line + native controls | 8d2c215 |

## Tracer Gate

The tracer feedback gate (after Task 2) was resolved by the orchestrator:
the API-authority claims were verified over HTTP against the live daemon
(bootstrap metadata present, no `Q` item array, no `canon`/scoring code,
`/api/start` responding, lesson chip preserved), and the interactive
click-through was deferred to final-product validation per the user's
standing instruction (browser automation unavailable in this session).

## Deviations

- The Task 3 empty/unavailable state copy follows the locked UI-SPEC matrix
  ("This session has no question ready." + **View report** / **Filters /
  settings**), matching the plan's behavior intent rather than its sketch
  wording.
- The fragment-pin deep link remains an offline `build`-page feature; the
  served client is API-driven and the server owns item selection.

## Verification

- `python tests/surface_roundtrip.py` - question-hierarchy assertions pass.
- Full suite (`python tests/*.py`) passes, including `serve_roundtrip`
  (API tracer), `daemon_roundtrip` (50 checks), `lesson_roundtrip`,
  `evidence_roundtrip`, `theme_roundtrip`, `presentation_roundtrip`.
- Rendered served page markers verified: context line, details disclosure,
  h1 stem template, native radio/checkbox, `Submit answer`, checking/error/
  empty copy, lesson chip base/label, reduced-motion rule, no old
  header/rail/tally.

## Self-Check: PASSED

All Task 1-3 acceptance criteria hold; the tracer gate's automatable checks
passed and the interactive check is deferred to final-product validation.
