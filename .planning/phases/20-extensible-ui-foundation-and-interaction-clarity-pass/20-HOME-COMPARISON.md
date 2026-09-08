# Phase 20 home comparison record

**Date:** 2026-09-08
**Scope:** Deterministic showcase pass with synthetic fixtures

Resume, Shelf, Agenda, and Path now render over one projection-neutral state.
The renderer receives course identity, routes, exact resume targets, evidence
labels, due facts, completion facts, agenda membership, and path states from
their existing durable owners. It does not derive or settle those facts.

| Learner job | Current disposition | Stable setting effect | Reconsideration trigger |
|---|---|---|---|
| Resume | Retained as the refined job of `next-action` | None. `next-action` keeps its name and meaning | Human comparison finds that the exact resume-led view obscures course choice |
| Shelf | Retained as the refined job of `shelf` and remains the default | None. `shelf` keeps its name and meaning | Weibao explicitly selects another default after comparison |
| Agenda | Registered prototype | None. No `agenda` setting value exists | Human comparison shows that durable time and revision groups answer a distinct recurring learner need |
| Path | Registered prototype | None. No `path` setting value exists | Human comparison shows that course position and return points outperform the simpler course outline for navigation |

The shipped `agent` and `split` values remain unchanged and render in both
Field Guide and Trajectory Deck. Switching a mode, prototype, or profile in the
synthetic matrix preserves course IDs, routes, evidence labels, resume targets,
and every saved appearance axis.

Deterministic coverage includes empty, one-course, many-course, archived,
corrupted, interrupted, and unavailable fixtures. Agenda hides empty groups and
accepts only overdue, today, upcoming, revision, and recently completed groups.
Anki due, itembank due, course completion, and evidence standing remain
separately labeled. Path nodes remain available, current, complete, pending,
locked, or unavailable and do not claim mastery.

Human visual comparison and screen-reader review were skipped by explicit user
direction. No selection, combination, or supersession of Agenda or Path is
claimed. Accessibility and usability are not certified.

Automated evidence:

- `python3 tests/home_roundtrip.py`, passed
- `python3 tests/presentation_profiles_roundtrip.py`, passed
- `python3 tests/ia_route_roundtrip.py`, 26 passed and 0 failed
