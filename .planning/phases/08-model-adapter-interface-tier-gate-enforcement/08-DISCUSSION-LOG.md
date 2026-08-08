# Phase 8: Model Adapter Interface & Tier-Gate Enforcement - Discussion Log

> **Audit trail only.** Decisions are in CONTEXT.md.

**Date:** 2026-08-08
**Areas discussed:** Adapter contract, tier gate, generated hints, rubric review, evidence and degradation

## Delegated resolution

| Area | Alternatives considered | Selected |
|------|--------------------------|----------|
| Provider shape | Separate provider APIs vs one versioned adapter contract | One contract |
| Leakage defense | Prompt only vs deterministic post-generation gate vs layered gate | Layered fail-closed gate |
| Hint role | Replace authored hints vs augment unlocked authored tier | Augment |
| Rubric result | Direct score vs pending proposal | Pending proposal |
| Outage behavior | Block/retry indefinitely vs typed unavailable fallback | Fallback |

**User's choice:** Delegated under the standing comprehensive/reversible-design instruction.

## Codex's Discretion

The concrete gate algorithm is intentionally left for dedicated research and a stronger planning model; the boundary, failure posture, and verification obligation are locked.

## Deferred Ideas

Authoring writes belong to Phase 11; model selection remains out of scope.
