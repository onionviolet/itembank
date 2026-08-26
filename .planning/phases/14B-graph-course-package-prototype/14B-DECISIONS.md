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

## D-14B-2. D-12.6-8 and D-12.6-9 confirmed at 14B plan time

**Date:** 2026-08-26.

**D-12.6-8, the metadata threshold, is confirmed as recommended.** A field
lives in the lesson or bank file when it describes only that file's content,
and in the course sidecar when two or more independently identified objects
must agree on it. This is the resolved D-14A-1 hybrid rule restated for
metadata, and adopting a second, different threshold would give one question
two answers. The implementation is the `derived` marking: a registry value
duplicated into a file, or a file value duplicated into the sidecar, is a
regenerable annotation for a human reader and is never the value anything is
validated against. The `## Sources` table's `title` cell is the worked example,
and `graph.add_source`'s docstring says so at the point of use. The test proves
it is not load-bearing by editing a source's derived title to a deliberately
wrong value and then binding a treatment against that source successfully: the
binding resolves through the minted `source_object_id` alone.

**D-12.6-9, rights representation when the user does not know, is confirmed as
recommended.** `unknown` is an explicit third state distinct from granted and
denied, it defaults restrictive for every one of the seven operations, and a
refusal names the missing grant so the fix is one edit. Confirming this costs
nothing, because plan 14A-01 already built exactly this shape:
`identity.rights_default()` returns seven `unknown` values, and contradicting it
would require a second rights store. Plan 14B-03 adds a second call site for
`identity.rights_state` and `identity.rights_granted` and invents no second
rights vocabulary. **Deferred, not dropped:** the closed provenance vocabulary
named in D-12.6-9's recommendation (owned, licensed, fair-use-claimed, unknown)
and the binding user interface that would let a learner record a grant belong to
the subphase that ships a surface. Phase 14B ships no CLI command and no daemon
route, so there is nowhere for them to live yet. They are recorded here so a
later phase finds them rather than rediscovering them.

**The version-migration prototype is delivered.** `PLANNING-DIRECTIVES.md`
section 3a requires two reversible prototypes before any course schema freeze:
the graph-to-outline projection, delivered by plan 14B-02, and the version
migration, delivered here. Its evidence is `graph.UPGRADES`, a dict keyed by
the version being upgraded from whose values are named single-step functions;
`graph.upgrade_document`, which applies them in sequence and refuses a gap in
the chain by name rather than skipping it; `graph.upgrade_0_to_1`, which
supplies the least-blocking `advisory` for the `override` column version 1
introduced and never guesses a hard gate; and
`fixtures.corpus_14b.sidecar_text_version_0()`, a real version-0 sidecar that
carries an unknown section so the test can prove an upgrade preserves what it
could not read. The version check runs before a single section is parsed, so an
older build can never partially consume a newer sidecar and then destroy the
fields it did not understand on rewrite.
