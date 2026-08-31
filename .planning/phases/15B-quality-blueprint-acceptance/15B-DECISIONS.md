# 15B decisions

This file is the single source of truth for every Phase 15B checkpoint answer.
Every later 15B plan reads it for its module boundary and its write path rather
than re-deriving either, so no executor chooses a module name or a write path
by judgment.

## Provenance for every decision in this file

**Recorded by Claude, as an agent, under Weibao's instructions of 2026-08-30:
"bypass my review, just make it so that it follows and goes to achieve
uservision", then "I have no time to work on this myself, so I want you to
finish accordingly to uservision", then "keep going".**

Both decisions below are rated **one-way** by plan 15B-01 and both are
`checkpoint:decision` tasks whose `<action>` blocks say "Ask Weibao the
question above" and "Do not proceed with a silent default. An unanswered
checkpoint stops the wave." That instruction is **waived, not met**. These are
not silent defaults, since they are recorded here with their reasoning and
their reversal costs, but they are not Weibao's answers either.

**This is the second phase running in which an agent has answered one-way
design questions that a plan reserved for Weibao**, after 15A's D-15A-1 and
D-15A-2. Counting the four consecutive agent-signed review legs (16A, 16B, 16C,
15A), the running total is four reviews and four one-way decisions. That is
worth putting in front of him as a standing question rather than leaving to
accumulate one phase at a time.

**D-15B-2 additionally amends a frozen record.** Option-a requires a dated
amendment appended to `14B-FREEZE.md` because `graph.SECTION_ORDER` gains a
member. Amending another phase's freeze record is a heavier act than adding to
this phase's own surface, and it is called out here rather than left inside a
plan step.

What reduces the risk to something worth taking: both questions name a
**recommended default**, and in both cases the alternatives are excluded by
rules the project has already written down rather than by this agent's taste.
Neither is a close call. Where one had been close, this file would say so and
the wave would have stopped.

Date: 2026-08-30.

## D-15B-1. Where the blueprint, staleness, audit, and acceptance code lives

**Question.** Does Phase 15B add one new pure classifier module and extend the
three existing owners for the parts that touch authority and disk, or does one
new module own the whole capability including its orchestration, or do two new
modules split the two halves?

**Answer: `option-a`**, one new pure module `blueprint.py` plus three
extensions of the existing owners. This is the plan's recommended default.

**Recorded by Claude under the waiver above, not by Weibao.**

**Why, and why it is not a close call.** The deciding property is that
option-a is the only one under which the structural bans are available at all.
`blueprint.py` imports only `model` and `runtime`, so
`hasattr(blueprint, "evidence")`, `hasattr(blueprint, "journal")` and
`hasattr(blueprint, "course")` are all `False`, and the rules that this module
never writes, never reads the evidence store, and never authorizes anything are
enforced by the absence of an import rather than by a reviewer's care. That is
the same discipline `director.py` already carries and the same one that made
15A's boundary assertions worth writing.

- **option-b**, one module owning everything, would have `blueprint.py`
  importing `identity`, `journal`, `graph`, `course`, `director`, `model` and
  `runtime`. A module that imports `journal` cannot assert that it never
  writes, so the claim "pure classifier" would become false and the bans would
  become unavailable. It also drags `surfaces.settings` transitively into
  `authoring.py`, shipped Phase 11 code that today imports only `model`, for
  the sake of two gate functions.
- **option-c**, two new modules, duplicates the layering that `graph.py` plus
  `course.py` plus `director.py` already provide. A reader would have to learn
  why acceptance has its own stack when treatment binding does not, and the
  second module would hold three functions.

**What this costs, stated rather than glossed.** Two real costs, and the second
is the one to watch.

1. The acceptance capability spreads across four files, so a reader asking "how
   does a migration get accepted" follows three hops: `graph.accept_migration`
   for the pure transition, `course.accept_migration` for the compare-and-swap
   write, `director.accept_revision` for the live authority re-check.
2. **`director.py`'s scope widens.** Plan 15A-01 locked it as "the treatment
   recommender and its rights and egress gate", and it now also owns one
   acceptance function. That is a genuine widening of a surface frozen eight
   commits ago. It lands beside `authorize_write`, the function it depends on,
   which is what makes it defensible rather than arbitrary, and `15A-FREEZE.md`
   should be read as describing the surface as of 15A rather than as forbidding
   additive growth.

**Executor consequence.** Proceed as plans 02 through 07 are already written.
No plan edit is needed.

**Reversal cost if Weibao chooses otherwise.** Before 15B-02 runs: the
consequence lists 15B-01 Task 2 records for option-b or option-c, which are
plan edits. After the 15B freeze: the module name and boundary appear in every
import in plans 02 through 07, in every structural-ban assertion, in the freeze
record, and in whatever Phase 16 builds on it, so undoing it renames a
published surface.

**Reconsideration condition.** Reopened if `blueprint.py` ever needs an import
that would make one of its three structural bans false, because at that moment
the property this decision rests on is gone and option-c becomes the honest
shape.

## D-15B-2. Where a blueprint lives and which write path records an acceptance

**Question.** Where does a cited, versioned blueprint document durably live,
which of the two existing write paths records an accepted revision, and does
`journal.RECORD_TYPES` gain a member for it?

**Answer: `option-a`.** Three coupled answers, one decision:

- **The blueprint's durable home** is an additive `## Blueprint` section in the
  14B course sidecar. `graph.SECTION_ORDER` gains exactly one member and
  `schemas/course_graph.schema.json` gains one section shape, both additively,
  so a sidecar with no `## Blueprint` section parses exactly as it does today.
- **The write path that records an accepted revision** is
  `course.write_course` reaching `journal.commit_operation`, by construction: a
  blueprint stored inside the sidecar is written by that path and by no other.
  Bank-content acceptance stays on `audit_writer.write_units` through
  `authoring.run_authoring`, untouched.
- **`journal.RECORD_TYPES` gains exactly one member**, `"accept_revision"`.
  `journal.OPERATION_TYPES` stays at exactly six.

This is the plan's recommended default.

**Recorded by Claude under the waiver above, not by Weibao.**

**Why, and why it is not a close call.** The project has two compare-and-swap
write paths, one per object kind, both built and both proven, and
`15B-RESEARCH.md`'s Anti-Patterns section names building a third as the failure
to avoid. Option-a builds none: it puts the new object inside an existing one
and inherits its path.

- **option-b**, a separate blueprint file with its own object kind, needs a
  seventh member in `identity.OBJECT_KINDS`, which is a **14A** freeze
  amendment and therefore larger than option-a's 14B one. It also splits one
  course's durable state across two files with no transactional relationship,
  so a crash between the two writes leaves the sidecar and the blueprint file
  disagreeing and neither authoritative. That is the same objection that
  settled D-15A-2 the same way one phase ago.
- **option-c**, migrating bank-content acceptance onto
  `journal.commit_operation`, rewrites shipped, executed, tested Phase 11 code
  this phase has no other reason to open, and re-proves compare-and-swap logic
  that already exists correctly in two independently proven forms.
  `15B-RESEARCH.md` rejects it by name and says to reconsider only when a
  future phase actually needs one unified history view. Its own plan step says
  choosing it stops the wave for replanning, because a shipped-code migration
  of that size is a plan and not a task.

**What this costs, stated rather than glossed.**

1. **It amends `14B-FREEZE.md`.** `graph.SECTION_ORDER` is named in that
   record, so plan 15B-02 Task 1 appends a dated amendment section recording
   that the tuple gained `"Blueprint"` in Phase 15B, the reason (ACTIVITY-02's
   durable blueprint object), and the statement that no existing member changed
   position. Amending a frozen record is heavier than growing this phase's own
   surface, and the amendment must be additive and must say so.
2. **Two write paths continue to exist.** A reader asking "where is the history
   of this change" has to know which object kind they are asking about. That
   ambiguity is not resolved by this phase and is not made worse by it.

**Executor consequence.** Proceed as plans 02 through 07 are already written,
plus the `14B-FREEZE.md` amendment named above, which plan 15B-02 Task 1 owns.

**Reversal cost if Weibao chooses otherwise.** Before 15B-02 runs: plan edits
plus, for option-b, a 14A freeze amendment instead of a 14B one; option-c stops
the wave by its own terms. After any blueprint has been accepted: the journal
is append-only and the sidecar's section list is a published format that
`schemas/course_graph.schema.json` validates, so a change is a migration of
recorded entries and stored documents rather than an edit.

**Reconsideration condition.** Reopened when a phase genuinely needs one
unified history view across both bank content and course objects, which is
option-c's real use case and the condition `15B-RESEARCH.md` already recorded
for it. Also reopened if a blueprint ever needs to travel independently of its
course, which is option-b's.
