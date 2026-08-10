# Phase 10: Retention, Pacing & Trends - Discussion Log

> **Audit trail only.** Decisions are in CONTEXT.md.

**Date:** 2026-08-08, updated 2026-08-10
**Areas discussed:** Evidence snapshot, due model, pacing cap, selection weights, longitudinal report, round-two amendments (FSRS replay, stages, utility weighting, return rate, deferred transfer)

## Delegated resolution

| Area | Alternatives considered | Selected |
|------|--------------------------|----------|
| Due signals | Merge itembank/Anki vs parallel labeled signals | Parallel signals |
| Cap | Advisory vs hard block vs explicit recorded override | Hard block with explicit recorded override |
| Mastery | Opaque score vs inspectable components | Inspectable bounded components |
| Selection | Second selector vs weights into Phase 7 selector | Reuse Phase 7 |
| Trends | Rates alone vs rates + counts + provenance | Counts and provenance |
| Scheduler | Mutable rows vs replay-derived state | FSRS state replayed from the evidence log (D-17) |
| Strategies | One fixed algorithm vs registered strategies | One interface, FSRS default, registered alternatives (D-18) |
| Progress labels | Numeric/streak vs named stages | WaniKani-style stages with terminal "retired" (D-19) |
| Usage measure | Streak vs return-rate ratio | Return rate with stated denominator, never a streak (D-20) |

**User's choice:** Delegated under the comprehensive, future-selectable, no-unnecessary-stoppage instruction.

## Codex's Discretion

Formula, thresholds, profiles, and chart presentation are assigned to research and planning/UI design.

## Deferred Ideas

Full card scheduling and predictive ML models remain out of scope; lesson-to-item transfer is recorded with its cost (D-21).
