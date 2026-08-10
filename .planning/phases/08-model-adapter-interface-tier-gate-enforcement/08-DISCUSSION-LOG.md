# Phase 8: Model Adapter Interface & Tier-Gate Enforcement - Discussion Log

> **Audit trail only.** Decisions are in CONTEXT.md.

**Date:** 2026-08-08, updated 2026-08-10
**Areas discussed:** Adapter contract, tier gate, generated hints, rubric review, evidence and degradation, round-two amendments (hosted-first, tier-3 pathway, presentation, evidence shape)

## Delegated resolution

| Area | Alternatives considered | Selected |
|------|--------------------------|----------|
| Provider shape | Separate provider APIs vs one versioned adapter contract | One contract |
| Leakage defense | Prompt only vs deterministic post-generation gate vs layered gate | Layered fail-closed gate |
| Hint role | Replace authored hints vs augment unlocked authored tier | Augment |
| Rubric result | Direct score vs pending proposal | Pending proposal |
| Outage behavior | Block/retry indefinitely vs typed unavailable fallback | Fallback |
| Design target | Local-first vs hosted-first | Hosted Claude-Code-class first; local is an additional registration (D-18) |
| Tier-3 mechanism | Self-assessment vs deferred human marking vs rubric decomposition | Self-assessment first; all three preserved for future choice (D-21) |
| Suggestion timing | after-self-mark / before-self-mark / after-mark | All three ship; default after-self-mark (D-22) |
| Auto-accept | Possible with guardrails vs impossible | Impossible, no setting (D-25) |

**User's choice:** Delegated under the standing comprehensive/reversible-design instruction — keep going without stoppage; where options conflict, preserve all safe options and let the user choose later.

## Codex's Discretion

The concrete gate algorithm is intentionally left for dedicated research and a stronger planning model; the boundary, failure posture, and verification obligation are locked.

## Deferred Ideas

Authoring writes belong to Phase 11; model selection remains out of scope; a validated local benchmark waits for hardware and `itembank bench`.
