# 14A evidence-field migration mapping (D-14A-3)

Recorded 2026-08-18 by plan 14A-01. This is a decision and mapping record
only. It changes no code, no schema, and no `retention.py` logic.

## Decision

D-14A-3's resolution, quoted from `.planning/DECISIONS-PRE-14A-2026-08-14.md`:
progress is a **per-objective, self-adjustable fill state** shown as
filled-in blocks (completed, filled in, done), able to move up and down as
evidence and retention change. It is not a permanent knowledge claim. The
working stored-field name is `evidence_support`. The exact token is
low-stakes; the semantics (per-objective, evidence-driven, reversible) are
the decision.

The boundary that keeps this compatible with the honest-progress hard-reject
(synthesis 12.4): the hard-reject bans one aggregate mastery/completion score
and bans participation-as-mastery. A Khan-style filled block is allowed
because it is per objective, not one rolled-up number, and driven by valid
response evidence rather than participation alone.

## Where the old label actually lives

`mastered` is a computed retention state, not a stored evidence-log field.
The evidence log itself carries no field named `mastered`; `evidence.py`'s
`KNOWN_EVENT_TYPES` and `response_event()` store raw response events only.

| Location | What is there |
|---|---|
| `schemas/report.schema.json` lines 228 to 234 | The published enum value: `"enum": ["unknown", "weak", "mastered", "at-risk", "due", "stable"]`, under the `state` property, checked in CI by `schema_validate.py`. |
| `retention.py` line 287 | `STATES = ("unknown", "weak", "mastered", "at-risk", "due", "stable")`, the closed tuple constant. |
| `retention.py` around lines 414 to 416 | `objective_state()`'s branch that returns `{"state": "mastered", "due": False}` when the mastery condition is met. |
| `retention.py` around lines 445 to 449 | `state_reason()`'s mastered-branch prose, explaining recent settled accuracy at or above the mastery threshold. |
| `retention.py` around line 548 | `recommendation_weight()`'s `"mastery": -cfg["mastery_reduction"] if st == "mastered" else 0.0` term. |
| Five consuming call sites | `surfaces/study.py`, `surfaces/day.py`, `surfaces/retention_view.py`, `selection.py`, and `schemas/report.schema.json` itself, all of which read or branch on the `"mastered"` state string. |
| Unrelated naming collision, explicitly excluded from this mapping | `surfaces/study.py` carries a client-side JavaScript variable named `mastered`, a per-session flashcard counter in the Learn mode UI (`let mode="flash",order=[],i=0,queue=[],mastered=0;`). This is ephemeral browser state, never persisted, never read by any tool, and is not the same durable object as the retention state. Renaming it would be scope creep with no decision backing it. |

## The mapping

One row per state in `retention.STATES`, old computed label to new
fill-state concept:

| Old state label | Disposition |
|---|---|
| `unknown` | Survives unchanged. No evidence yet is still the correct starting fill level under the new model. |
| `weak` | Survives as a low fill level. Renamed only if 16B's level vocabulary chooses a different token; the semantics (below the accuracy threshold) carry forward unchanged. |
| `mastered` | Renamed. Absorbed into the new field's highest fill level. The stored field itself moves from a `mastered` boolean-shaped claim to `evidence_support` (or whatever token 16B finalizes), and the level is explicitly reversible: a filled block can empty again if evidence later contradicts it, which the old label's permanent-sounding name did not convey. |
| `at-risk` | Survives as a fill level, likely one step below the highest. Carries forward unchanged in meaning: recent evidence suggests the objective needs review soon. |
| `due` | Survives unchanged. A scheduling signal (interval elapsed), independent of the fill level itself. |
| `stable` | Survives as a fill level. Carries forward unchanged in meaning: settled evidence with no near-term risk signal. |

## What 14A does not do, and why

Renaming the published enum value in `schemas/report.schema.json` is a
format break, not an additive change: the fourth non-negotiable in
`.planning/PLANNING-DIRECTIVES.md` section 4 requires format changes to be
additive, and `schemas/report.schema.json`'s `state` enum is a published
contract checked in CI. The display semantics, the fill thresholds, and the
level vocabulary are routed to Phase 16B by D-14A-3 and by the 14A phase
brief. Therefore 14A records this mapping and changes no code: not
`retention.py`, not `selection.py`, not any file under `surfaces/`, and not
`schemas/report.schema.json`.

## Owner and verification

Phase 16B owns execution of the rename and the display-facing fill-state
vocabulary. The verification that 14A leaves the shipped contract untouched
is that `schemas/report.schema.json` still validates unchanged today,
checked by the shipped `python schema_validate.py` step, and that
`tests/scoring_roundtrip.py` and `tests/evidence_roundtrip.py` stay green.
