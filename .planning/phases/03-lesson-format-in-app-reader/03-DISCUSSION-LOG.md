# Phase 3: Lesson Format & In-App Reader - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-08
**Phase:** 3-lesson-format-in-app-reader
**Areas discussed:** Gray-area selection only — all four areas delegated to Claude

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Delegate all | Claude picks the option with the most future room, records it as Claude's discretion | ✓ |
| LESSON grammar shape | In-bank `## LESSON` section, sibling lesson file, or both | |
| LESSON-REF resolution + lint severity | Literal heading text vs stable slug; and the REQUIREMENTS-vs-ROADMAP conflict on warn vs fail | |
| Reader surface shape | Own `/lesson/<bank>` route vs folded into `study`; link direction | |

**User's choice:** Delegate all
**Notes:** Consistent with the standing instruction recorded in `02.1-CONTEXT.md` — *"plan the most optimal solution that gives us the most options and directions in the future."* No additional constraints given this session.

---

## Claude's Discretion

All four areas. Resolved in `03-CONTEXT.md` as D-01 through D-10. Three flagged as
open to planner override: the `[LESSON-SRC:]` directive (D-02), the renderer's scope
(D-08), and whether to edit REQUIREMENTS.md LESSON-04 to match ROADMAP SC3 (D-05).

**Conflict surfaced rather than silently resolved:** REQUIREMENTS.md LESSON-04 says
lint *warns* on an unknown `LESSON-REF`; ROADMAP Success Criterion 3 says it *fails*.
D-05 takes the ROADMAP as the acceptance gate and makes it an error.

## Deferred Ideas

- Lesson review queue with a hand-set schedule (SCHED-04, Phase 10)
- Tier-0 hint returning the lesson pointer (TEACH-02, Phase 6)
- LaTeX and runnable inline code in lessons (LOOP-02/LOOP-03, Phase 9)
- Theming the reader (Phase 4)
- A lesson authoring command (Phase 11)
