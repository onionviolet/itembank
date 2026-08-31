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

## D-15B-3. Where the course audit report shape lives

**Question.** Does the course audit report get its own schema file, extend the
shipped `audit_report.schema.json` with an eighth `status` value, or carry no
schema at all?

**Answer: `option-a`**, a new `schemas/course_audit_report.schema.json`. This
is the plan's recommended default.

**Recorded by Claude under the waiver at the top of this file, not by Weibao.**
Rated one-way: a schema is a published contract, and moving the report's home
after an audit has been produced and stored means migrating stored documents.

**Why, and why it is not a close call.** The obstacle is structural rather than
stylistic. `audit_report.schema.json`'s `$defs.coverage_row` is
`additionalProperties: false`, and its four required keys encode `auditor.py`'s
syllabus-objective-to-bank-item pairing specifically. A course-scope audit row
pairs an objective with a source, a treatment, a blueprint, and a named
vocabulary, which is a different pairing and not a longer one.

Pushing the new pairing through the shipped `$defs` would either violate that
`additionalProperties: false` or require loosening it, and **the loosening
lands on shipped Phase 11 fixtures that currently prove strictness**.
`tests/audit_coverage_roundtrip.py` and `tests/audit_roundtrip.py` assert that
strictness today. Trading a real, tested guarantee on shipped code for the
convenience of one fewer file is the wrong direction, and it is the reason
option-b is not close.

Option-c, no schema at all, is excluded by the project's own practice: every
other durable report shape in this repository carries a validated schema, and
an unvalidated one is the only kind that can drift without anything noticing.

**What this costs, stated rather than glossed.** Two report schemas now exist,
so a reader asking what an itembank audit report looks like has to know which
audit. The `stale` field is defined in both files with the same meaning, and
the two descriptions can drift even though neither behavior can: `stale` is
derived at build time from a supplied fingerprint pair in both, and neither
file stores a verdict a later read trusts.

**One thing this decision does NOT create.** No fourth coverage-state
vocabulary. Three exist (`graph.BINDING_STATES`, `auditor.coverage_report`'s
own, and the director's treatment states), and the audit names which of the
three each row's state came from rather than reconciling them into a superset.
`blueprint.COVERAGE_VOCABULARIES` is a tuple of vocabulary NAMES, not of
states, so `blueprint.py` never holds a copy of any vocabulary's members. That
is precisely how a fourth would get minted by accident.

**Executor consequence.** Proceed as plans 05 through 07 are already written.
No plan edit is needed.

**Reversal cost if Weibao chooses otherwise.** Before 15B-05 Task 2 runs: a
plan edit plus, for option-b, the `additionalProperties` loosening and its
effect on the two shipped Phase 11 fixtures. After a course audit has been
produced and stored: a migration of stored documents rather than an edit.

**Reconsideration condition.** Reopened if a consumer genuinely needs one
contract that validates every audit this tool produces, which is option-b's
real use case. Also reopened if `auditor.py`'s coverage row ever changes shape
for its own reasons, because at that moment the two pairings might turn out to
be one after all.

## D-15B-4. The Phase 15B freeze scope

**Decided 2026-08-30, at the phase's own freeze gate**, and recorded here so a
later phase reading only this file gets the same answer `15B-FREEZE.md` gives.

**What the 15B freeze covers.** The blueprint, audit, acceptance, staleness,
and proposal-discipline surfaces this phase built. Concretely: `blueprint.py`'s
closed vocabularies and its twenty-four typed codes; `SPARSE_MAX` 5 and
`MODERATE_MAX` 19; the half-open window convention and the `recommendation`
status, both schema constants rather than conventions; the three published
schemas `blueprint.schema.json`, `course_audit_report.schema.json` and
`evidence_proposal.schema.json`, each at `x-itembank-version` 1; the additive
`blueprint_findings` array and `blueprint_finding_ref` in
`audit_report.schema.json` with its `gates.required` unchanged;
`graph.SECTION_ORDER`'s `"Blueprint"` member and the two migration review
columns; `graph.accept_migration` and `graph.reject_migration` as the only two
paths that settle a proposal; `course.bind_blueprint`, `course.accept_migration`
and `course.reject_migration`; `director.accept_revision` and its fixed
staleness-then-authority-then-write order; and `journal.RECORD_TYPES`'s one new
member `accept_revision`, with `OPERATION_TYPES` unchanged at six.

Four behaviors are frozen because they are the phase's substance rather than
its shape: the exam-fidelity claim is False until all five gates report; an
absent blueprint or an unsupplied fact is `warn` and withholds the claim rather
than the practice; a stale dependent is BLOCKED and never rebuilt; and an
absent fingerprint reads stale, because an unprovable freshness is not
freshness.

**What it explicitly does not cover.** Transcribed from `ROADMAP.md`:

> the 15B freeze covers the blueprint, audit, acceptance, staleness, and
> proposal-discipline surfaces only. It is explicitly not the course schema
> freeze, not a lesson-profile grammar freeze, not an agent job protocol
> freeze, and not a learner-facing surface freeze, and its freeze record says
> so.

15B amended `14B-FREEZE.md` to add one sidecar section and did not otherwise
touch it; that amendment is additive and does not make this the course schema
freeze. The fixture corpora, the mock backend, and the synthetic Beacon
blueprint are test data and are not frozen.

**Provenance.** The freeze's review leg closed on `15B-REVIEW.md`, verdict
`accept with concerns recorded`, written by Claude under Weibao's instruction
of 2026-08-30 to finish without him. Plan 15B-07 Task 2's prohibition against
an agent signing its own acceptance-quality review is waived, not met. This is
the fifth consecutive phase to close a review leg that way. Anything relying on
this scope should read that file's Provenance section first.

**Reconsideration condition.** Reopened by any change to a frozen vocabulary's
membership, to the five-gate order, to the half-open window convention, to the
`recommendation` status constant, to `journal.ENTRY_KEYS`, or to the count of
paths that may settle a migration. Adding a blueprint field reopens it through
`BLUEPRINT_FIELDS`, which is ACTIVITY-02's list and not this module's. Changing
a fixture does not reopen it.
