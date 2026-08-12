---
title: True/False button rendering and prose-category UX modes
trigger_condition: V2-GRA-01 lands and a real author asks for T/F buttons, or learners start taking category notes in study/day
planted_date: 2026-08-11
status: planted
---

# Seed: item-grammar user options

## The deferred choices (deliberately kept open — do not silently pick one)

1. **T/F presentation.** `V2-GRA-03` ships True/False as a plain 2-option mc
   (labels A/B). A dedicated `[TYPE: tf]` — True/False buttons, no
   distractor-analysis / SECOND-BEST lint, clean export — remains an option.
   Implement only when a real bank wants it; the 2-option-mc foundation makes it
   purely additive.

2. **Graded vs capture UX for prose categories.** `V2-GRA-04` ships both modes
   behind one grammar capability. Which surface shows rubric scoring vs free
   capture, and how notes persist, is UX for the planning model — per the user's
   directive: "UI and other important stuff to be planned by a more capable model
   beforehand."

## Why kept open

The user's directive for this exploration: pick the most comprehensive option, and
where options conflict, implement all of them and let the user choose later. Nothing
here is irreversible or quality-lowering, so both paths stay open.
