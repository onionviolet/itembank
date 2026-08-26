# Phase 14B decisions

Decisions this phase made and locked, each recorded where a later plan can find
it without reading chat history, per `AGENT-WORKFLOW.md`.

## D-14B-1. Sidecar path and the Phase 13.9 supersession

**Date:** 2026-08-26.

**Question.** Where does the Phase 14B course graph live on disk inside a
course root, and what happens to the `course.md` stub that Phase 13.9 writes
there?

**Recorded answer: option-a**, the separate file with a non-destructive
migration. Phase 14B writes `<course-root>/course-graph.md` and never opens
`<course-root>/course.md` for writing. `course.migrate_stub()` reads a 13.9
shaped `course.md`, emits the new sidecar, journals the operation, and leaves
`course.md` byte-identical, which `tests/graph_roundtrip.py` asserts by
comparing the stub's bytes before and after the migration.

**Provenance of this answer, stated plainly.** Weibao has not answered this
checkpoint verbatim. He authorized overnight execution of plan 14B-01 while
away from the keyboard, so the orchestrating session recorded the plan's own
named RECOMMENDED DEFAULT rather than stopping the wave or inventing a
different path. This is an agent decision standing in for his, and the slot for
his verbatim answer is left open below. It is recorded as provisional for one
reason only: the checkpoint is rated one-way, and no agent may quietly convert
a one-way call into a settled one.

**Why the default is the safe stand-in, and not merely the convenient one.**
`13.9-CALIBRATION.md` records the walking skeleton's course root as
`~/Documents/itembank-courses/emt-unit-1`, outside this repository, with
`course.md` as its course stub and its per-objective map as the outcome half of
the calibration corpus. That file therefore already holds a real, hand-approved
objective map for a live fall course; it is covered by no test fixture and by
no repository backup. The in-place upgrade path would have a tool rewrite
exactly that file, and if the format upgrade were wrong the damaged artifact
would be the recorded objective map itself. That is the one outcome an agent
acting without its author present must not risk. The refusal path, where 14B
reads no stub at all, is safe but forces the objective map to be retyped by
hand, which is the manual re-entry this phase exists to remove. The separate
file with a non-destructive migration is the only one of the three that both
carries the recorded map forward and cannot damage it.

**What this answer costs.** Two course-shaped files exist in the course root
until a later phase retires the stub, and each needs a header line pointing at
the other. Recorded here so the cost is not rediscovered as a surprise.

**Consequence for the plans.** None. Plans 14B-01 through 14B-06 are already
written for this answer, so no plan edit was required and none was made. The
byte-identical stub assertion in 14B-01 Task 3 stands as written.

**Open slot: Weibao's verbatim answer.** To be filled in when he reads this. If
he chooses the in-place upgrade instead, the reversal is: change
`course.COURSE_SIDECAR_FILENAME` to `course.md`, delete `STUB_FILENAME`, change
`migrate_stub` to an in-place upgrade taking an `expected_fingerprint` and
journaling `operation="edit_in_place"`, and replace the byte-identical
assertion with a before-image assertion against `_journal/before/`. If he
chooses the refusal, the reversal is: delete `migrate_stub` from `course.py`
and from the Task 3 assertions, and record here who re-enters the 13.9
objective map by hand. Both reversals are cheap while no package has been
built and no sidecar exists in a real course root; both get expensive after.
The reversal window is therefore open until plan 14B-05 builds a package or
until `migrate_stub` is first run against the real EMT course root, whichever
comes first, and neither has happened as of this date.
