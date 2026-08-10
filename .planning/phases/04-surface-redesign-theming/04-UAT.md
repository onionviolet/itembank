---
status: testing
phase: 04-surface-redesign-theming
source: [04-VERIFICATION.md]
started: 2026-08-09
updated: 2026-08-10
---

## Current Test

number: 1
name: Real-browser walk-through of every surface (index/quiz/study/report/settings/day)
expected: |
  One visual system (60/30/10 allocation, shared spacing/type/measure); quiz
  shows one sticky context line, a dominant stem h1, a reserved feedback
  region, and no old header/rail/tally chrome; no layout regression at
  desktop or 320px/200% zoom.
awaiting: user response

## Tests

### 1. Real-browser walk-through of every surface
expected: All surfaces read as one product from one visual system; the question view keeps exactly one sticky context line with the stem as the single h1.
result: [pending]

### 2. Native OS colour picker and browser fallback
expected: Picker selection is preview-only; cancel/fallback shows "System picker is unavailable here. Choose a color below instead." without changing settings; save persists only accent.source; every surface updates on reload.
result: [pending]

### 3. Screen-reader walk-through (Narrator/NVDA/VoiceOver) with reduced motion
expected: One heading hierarchy per page, polite status announcements in reading order, immediate errors announced, disclosure state announced, predictable post-transition focus, keyboard-only usable.
result: [pending]

### 4. Colour-blind safety with two very different custom accents
expected: Correct/Incorrect/Warning stay fixed colors with text/icon/border redundancy, contrast-checked at 4.5:1, pairwise distinct, distinguishable under a deuteranopia simulator.
result: [pending]

### 5. Two-editor day conflict scenario
expected: A no-write conflict appears with the exact heading "Plan changed outside itembank - nothing was overwritten.", labeled Your draft/Current file panes, copy/download, Reload current, Reapply draft, dirty warning, Force absent until a conflict; a third external edit produces a new conflict, never an overwrite.
result: [pending]

### 6. Backstop items at 320 CSS px and 200% zoom with long content
expected: Content wraps/stacks without clipping or page-level horizontal scroll; revision/draft/current documents stay copyable.
result: [pending]

### 7. Visual adequacy of the polished surfaces
expected: Settings preview cards, migrated index/report/quiz/study/day, teaching-step primary-action emphasis, and study progressive reveal look finished and consistent at both color modes.
result: [pending]

## Summary

total: 7
passed: 0
issues: 0
pending: 7
skipped: 0
blocked: 0

## Gaps

None. All 30 must-haves verified (0 failed); the remaining items are
interactive/visual/OS-window judgments.

## Note

Deferred to final-product validation per the user's explicit standing
decision (2026-08-08): automated tests are run by the agent; manual,
perception, and OS-window tests are deferred rather than blocking the
milestone.
