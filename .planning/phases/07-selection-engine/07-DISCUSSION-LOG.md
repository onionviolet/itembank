# Phase 7: Selection Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-08
**Phase:** 7-selection-engine
**Areas discussed:** Gray-area selection only — all four areas delegated to Claude

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Delegate all | Claude picks, biased toward inspectability and the Phase 10 seam | ✓ |
| How a selection is requested | CLI flags per sitting vs named profiles in settings | |
| Discrimination pairs source | Derive from the existing `conf` field vs a new `[PAIR:]` tag | |
| Recent-exposure rule | Last N items, last N sessions, or a time window; hard exclusion vs weight penalty | |

**User's choice:** Delegate all
**Notes:** Same standing instruction as Phase 2.1. No additional constraints given.

---

## Claude's Discretion

All four areas. Resolved in `07-CONTEXT.md` as D-01 through D-10. Three flagged as open
to planner override: whether the selection spec earns a sixth published schema (D-02),
how the selection-mode / feedback-mode name collision is resolved (D-06), and the
default cooldown of 20 responses, which is a guess rather than a measurement (D-08).

**Finding that killed one of the options offered:** the `conf` field parsed at
`model.py:61` comes from `CONFIDENCE:` — the author's confidence in the item, not a
confusion set. Nothing in the current format records which items are commonly confused,
so SEL-04 needs a new `[PAIR:]` tag rather than a derivation.

**Naming hazard recorded for the planner:** `session.mode` already means *feedback
policy* (MODE-01..06, Phase 6) and overlaps this phase's *selection* modes in three
words. D-06 requires the planner to either rename or document the coupling, never to
let them silently alias — once the evidence log records a conflated field, separating
them needs a migration.

## Deferred Ideas

- Evidence-driven selection weight and mastery drop-out (TREND-01, Phase 10)
- What is due today, and the daily cap (SCHED-01/02, Phase 10)
- At-risk objectives feeding selection (TREND-04, Phase 10)
- Rendering the trace in `/report` or `day` — CLI and API only this phase
- Authoring `[PAIR:]` tags across the real banks — authoring work, possibly Phase 11
- Adaptive / IRT-style selection — not this milestone
