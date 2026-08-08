# Phase 6: Hint Ladder, Cursor-Hold & Feedback Modes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-08-08
**Phase:** 6-hint-ladder-cursor-hold-feedback-modes
**Areas discussed:** Attempt and cursor rules, hint ladder presentation, feedback-mode behavior, evidence and reporting

## Delegation

The user selected “Delegate all” and asked Codex to choose the most useful and comprehensive considerations, preserve multiple future choices when compatible, and continue without human stoppage where doing so is reasonable and does not cause lasting harm or lower quality. UI and other important design work should be specified before implementation by a more capable planning model.

## Attempt and cursor rules

| Option | Description | Selected |
|--------|-------------|----------|
| Retry-assisted ladder plus explicit stumped action | A genuine retry or deliberate “I’m stumped” action can reveal one next tier; duplicates are idempotent | ✓ |
| Call-gated ladder | Every hint call advances regardless of another attempt | |
| Time-gated ladder | Rate-limit progression by elapsed time | |

## Hint ladder presentation

| Option | Description | Selected |
|--------|-------------|----------|
| Structured new + accumulated payload | Runtime fixes meaning; UI remains free to choose presentation | ✓ |
| Only newest text | Minimal payload but weak future UI flexibility | |
| One fully rendered HTML block | Couples pedagogy to one surface | |

## Feedback-mode behavior

| Option | Description | Selected |
|--------|-------------|----------|
| One policy engine, four mode tables | Shared transitions with mode-specific visibility and advancement | ✓ |
| Separate implementation per mode | More direct initially, higher drift risk | |

## Evidence and reporting

| Option | Description | Selected |
|--------|-------------|----------|
| Hint events plus tier-bearing response events | Auditable history and efficient response interpretation | ✓ |
| Mutable counters only | Simpler but loses history | |

## Codex's Discretion

All areas were delegated. Exact names and UI representation remain available to downstream research, UI design, and planning as long as the locked invariants in CONTEXT.md hold.

**Follow-up amendment:** The user requested a less restrictive path with a stumped button for viewing the next hint layer. This was incorporated as an explicit, one-tier-at-a-time action whose use is recorded separately from wrong attempts.

## Deferred Ideas

Model hinting (Phase 8), visual styling (Phase 4/UI), and evidence-driven selection (Phase 10).
