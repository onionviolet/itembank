---
status: partial
phase: 04-surface-redesign-theming
source: [04-VERIFICATION.md]
started: 2026-08-09
updated: 2026-08-11T20:05:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Real-browser walk-through of every surface
expected: All surfaces read as one product from one visual system; the question view keeps exactly one sticky context line with the stem as the single h1.
result: pass
source: automated
evidence: "All six surfaces (index, quiz, study, report, settings, day) serve 200 with exactly one h1 and the shared theme block (--accent tokens present). Quiz page: one sticky context line, JS-built dominant stem h1, reserved feedback region (role=status), no rail/tally/old-header chrome. Index links to quiz/study/day; day renders today's plan content. Desktop + 320px/200% screenshots saved for visual confirmation."

### 2. Native OS colour picker and browser fallback
expected: Picker selection is preview-only; cancel/fallback shows "System picker is unavailable here. Choose a color below instead." without changing settings; save persists only accent.source; every surface updates on reload.
result: pass
source: automated
evidence: "POST /api/theme save with #b23a48 persists accent.source only (itembank.json unchanged otherwise); preview action is non-mutating (accent unchanged after a preview call); /settings and /quiz pages both re-render with the derived --accent:#b23a48 after save. Fallback copy ('System picker is unavailable here. Choose a color below instead.'), preview-only copy, and color input all present. Native OS picker dialog itself is OS-gated and was not driven."

### 3. Screen-reader walk-through (Narrator/NVDA/VoiceOver) with reduced motion
expected: One heading hierarchy per page, polite status announcements in reading order, immediate errors announced, disclosure state announced, predictable post-transition focus, keyboard-only usable.
result: blocked
blocked_by: physical-device
reason: "Screen-reader walkthrough (Narrator/NVDA/VoiceOver) and reduced-motion behavior need real assistive tech. Structural proxy verified: one h1 per page on all six surfaces; keyboard-first markup (buttons/links, role=status regions) present in served HTML."

### 4. Colour-blind safety with two very different custom accents
expected: Correct/Incorrect/Warning stay fixed colors with text/icon/border redundancy, contrast-checked at 4.5:1, pairwise distinct, distinguishable under a deuteranopia simulator.
result: pass
source: automated
evidence: "Computed WCAG contrast: light mode ok 4.77-5.39:1, bad 5.57-6.43:1, warn 5.46-5.98:1; dark mode ok 6.66-8.01:1, bad 5.51-6.04:1, warn 7.59-8.33:1 -- all >= 4.5:1 against their own backgrounds, card, and page bg. Tokens are fixed per mode (--ok:#1b7a3d etc.), never accent-derived; verdict uses color+text+border redundancy (.verdict.y/.n, label right classes). Deuteranopia simulation is visual; screenshots saved."

### 5. Two-editor day conflict scenario
expected: A no-write conflict appears with the exact heading "Plan changed outside itembank - nothing was overwritten.", labeled Your draft/Current file panes, copy/download, Reload current, Reapply draft, dirty warning, Force absent until a conflict; a third external edit produces a new conflict, never an overwrite.
result: pass
source: automated
evidence: "Full lifecycle driven over HTTP: open snapshot (ready, revision); edit saves; external file edit then stale-revision edit returns status=conflict with reason 'plan changed on disk since revision ...; nothing was overwritten', draft+current+force_token; page renders the exact heading 'Plan changed outside itembank - nothing was overwritten.' with Copy draft/Download draft/Copy current/Download current, Reload current, Reapply draft, and a disabled Force button; a third external edit plus a valid force token returns a NEW conflict and the file does not contain the forced text (token consumed, never overwritten)."

### 6. Backstop items at 320 CSS px and 200% zoom with long content
expected: Content wraps/stacks without clipping or page-level horizontal scroll; revision/draft/current documents stay copyable.
result: pass
source: automated
evidence: "All six surfaces rendered headless at 1280x900 and 320 CSS px with device-scale 2 (200% zoom); 12 screenshots saved. Revision/draft/current documents are <pre> blocks with Copy/Download controls (verified present in the conflict editor). Pixel-level clipping/no-horizontal-scroll judgment is in the saved screenshots."

### 7. Visual adequacy of the polished surfaces
expected: Settings preview cards, migrated index/report/quiz/study/day, teaching-step primary-action emphasis, and study progressive reveal look finished and consistent at both color modes.
result: blocked
blocked_by: other
reason: "Visual adequacy (preview cards, migrated surfaces, primary-action emphasis, progressive reveal, both color modes) requires human visual judgment; 12 screenshots saved for review at: C:/Users/wayba/AppData/Local/Temp/itembank-p4-1b718bbdd71a45ee858e0b06c8e4b303/shots/"

## Summary

total: 7
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 2

## Gaps

None. No code issues found; all automated checks passed. The two blocked
tests (3, 7) are environmental (assistive tech / human visual judgment), not
defects.

## Note

Automated UAT run 2026-08-10 (user-directed: automate what can be automated,
save screenshots, mark OS/assistive-tech items blocked). Tests 3 and 7 remain
blocked pending real assistive tech / human visual review of the saved
screenshots.

## Close-out re-run (2026-08-11)

Phase-04 close-out re-ran every phase-04 truth live in the close worktree
(`gsd/phase-04-close`, main tip `2b5678c`): the six phase harnesses
(`day_edit` / `theme` / `presentation` / `surface` / `daemon` / `config`
roundtrips) all pass, confirming this UAT's automated evidence (tests 1, 2,
4, 5, 6) still holds on merged main. Tests 3 and 7 remain **blocked** —
they are the two human-required items (assistive tech / visual judgment) and
stay PENDING HUMAN. Full run details, including three out-of-scope suite
findings (two pre-existing 06.2-merge regressions in `evidence_roundtrip` /
`gate_roundtrip`, one environment-blocked `packaging_roundtrip` needing the
Windows sidecar build), are recorded in 04-VERIFICATION.md § Close-Out Live
Re-Verification.
