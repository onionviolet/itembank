# 15A decisions

This file is the single source of truth for every Phase 15A checkpoint answer.
Every later 15A plan reads it before its first task.

## Provenance for every decision in this file

**Recorded by Claude, as an agent, under Weibao's instructions of 2026-08-30:
"bypass my review, just make it so that it follows and goes to achieve
uservision", and then "I have no time to work on this myself, so I want you to
finish accordingly to uservision".**

Both decisions below are rated **one-way** by plan 15A-01 and both are
`checkpoint:decision` tasks whose `<action>` block says in as many words: "Ask
Weibao the question above" and "Do not proceed with a silent default. An
unanswered checkpoint stops the wave." That instruction is **waived, not met**.
These are not silent defaults (they are recorded here with their reasoning and
their cost), but they are not Weibao's answers either.

This matters more than the 16C review waiver did, and the difference should be
stated plainly rather than buried. A review judges work already done. These two
decisions **determine what gets built**, they are one-way, and one of them
changes a published schema (`schemas/model_adapter.schema.json`) that Phase
15B and any external agent client will build against. Reversing either after a
recommendation has been journaled is a migration of recorded operations, not an
edit.

What reduces the risk to something worth taking: in both cases the plan names
a **recommended default**, and in both cases the two alternatives are rejected
by rules the project has already written down as non-negotiable rather than by
this agent's preference. Neither decision is a close call. Where a decision had
been close, this file would say so and the wave would have stopped.

**If Weibao disagrees with either, the reversal cost is stated in each section
below**, and the sooner it is read the cheaper it is: before plan 15A-02 runs,
option-b or option-c on either decision is still a plan edit.

Date: 2026-08-30.

## D-15A-1. The recommendation wire boundary

**Question.** Does a treatment recommendation cross the shipped
`model_adapter.invoke()` boundary as a fourth member of its closed `operation`
enum, or does it travel a separate path that never enters the learner-facing
adapter?

**Answer: `option-a`**, a fourth adapter operation, `treatment_recommend`.
This is the plan's recommended default.

**Recorded by Claude under the waiver above, not by Weibao.**

**Why, and why it is not a close call.** The two alternatives are each excluded
by a rule this project already holds:

- **option-b**, a separate course-scope transport owned by `director.py`,
  duplicates `TRANSPORT_REGISTRY`, profile resolution, timeout and output caps,
  the typed unavailable envelope, and secret resolution. Two transport layers
  means AGENT-02's backend-parity guarantee has to be re-proved for the second
  and can silently drift from the first. `15A-RESEARCH.md`'s "Don't Hand-Roll"
  table forbids this outcome by name. It is also the same shape as the
  architectural anti-pattern the repository lists first: a second authority for
  something that already has one.
- **option-c**, no model in the loop for 15A, cannot meet the phase's own
  freeze gate. AGENT-02's Fixture sentence requires one operation to run
  through a mock hosted and a mock local backend with identical artifacts and
  journals. With no adapter path there is no backend to run through. Choosing
  it means opening 15A-06's freeze record with `Freeze withheld` naming
  AGENT-02, which is a decision to not finish the phase.

**What this costs, stated rather than glossed.** The adapter's `operation` enum
now mixes a learner-facing family (`hint`, `rubric_review`, `author`) with a
course-builder operation, so only three of the four go near `tier_gate.py`. A
future reader cannot see that from the enum. Plan 15A-01 already requires the
distinction be written into the schema description and into `director.py`'s
docstring, and Task 4 should be held to that: it is the whole mitigation.

The `treatment_recommend` result is deliberately **not** routed through
`tier_gate.py`. `director.py` validates it against
`schemas/treatment_recommendation.schema.json` and a live rights check instead.
A course-scoped operation has no learner tier to gate against, and routing it
through a gate that cannot mean anything for it would be worse than not
routing it.

**Executor consequence.** Proceed as plans 01 through 06 are already written.
No plan edit is needed.

**Reversal cost if Weibao chooses otherwise.** Before 15A-02 runs: a plan edit
plus the `15A-DECISIONS.md` records that 15A-01's `<action>` block specifies
for option-b or option-c. After a recommendation has been journaled: a schema
migration plus a rewrite of every recorded operation.

**Reconsideration condition.** Reopened if a second non-learner-facing
operation is proposed for the adapter enum, at which point the question stops
being "does this one fit" and becomes "is the enum still one family". Also
reopened if `tier_gate.py` ever gains a course-scope meaning, which would
remove this decision's main stated cost.

## D-15A-2. Where the egress record lives

**Question.** Is the record of exactly what left this machine, and to whom, a
set of fields on the existing journal entry, or a sibling append-only file
beside the journal?

**Answer: `option-a`**, one new dict-valued journal entry key. This is the
plan's recommended default.

**Recorded by Claude under the waiver above, not by Weibao.**

**Why, and why it is not a close call.** RELIABILITY-02 requires **one** durable
local operation journal, singular. The two alternatives each add a second
durable record:

- **option-b**, a sibling append-only egress log, splits the answer to "what
  happened in this operation" across two files with no transactional
  relationship. A crash between the two writes leaves them disagreeing and
  neither authoritative, which is the exact failure the phase's own
  compare-and-swap discipline exists to prevent. A privacy review reading one
  clean file is a real benefit, and it is not worth an unresolvable
  disagreement between two records.
- **option-c**, field plus derived sibling view, costs a rebuild command and a
  staleness rule the phase would otherwise not need, and creates precisely the
  hazard the project's durable-versus-derived rule names: a derived view a
  reader mistakes for the record. The repository's own rule is that derived
  data must never become the only understandable copy; option-c does not
  violate that, but it spends real complexity buying a file whose only job is
  to be more readable than the authoritative one.

**What this costs, stated rather than glossed.** The journal entry grows a
nested structure, so a reader that wants only egress reaches one level in.
Egress and object mutation are genuinely different concerns sharing one record,
and this decision says the shared record is worth more than the separation.

**Why the shape is safe.** `journal.ENTRY_KEYS` gains exactly one member,
`agent`, whose value is a dict carrying `director.AGENT_ENTRY_KEYS`, one of
which is `egress`. This mirrors the existing `undo` key's precedent exactly (a
dict value with a documented key set) rather than inventing a pattern. It is
also why `journal.py`'s whole-phase diff stays at two lines, which
`15A-RESEARCH.md` names as the drift signal to watch: if that diff grows, this
decision was implemented wrong.

**On the key count.** The landed `journal.ENTRY_KEYS` has twenty-three members
ending in `rights`, per `14A-FREEZE.md`. Adding `agent` makes twenty-four. The
plan text originally said twenty-two and twenty-three because it was written
from `14A-02-PLAN.md`, the stale record; see `15A-PRECONDITION.md`. `rights`
stays.

**Executor consequence.** Proceed as plans 01 through 06 are already written.
No plan edit is needed.

**Reversal cost if Weibao chooses otherwise.** Before 15A-04 runs: the plan
edits 15A-01's `<action>` block specifies for option-b or option-c. After
operations have been journaled: the record is append-only by construction, so
every recorded operation carries the chosen shape and a change is a migration.

**Reconsideration condition.** Reopened if a privacy or legal review needs a
standalone egress file it can hand to someone without handing over the whole
operation journal. That is option-c's real use case and it is a rights and
disclosure question, not an architecture one, so it belongs to Weibao whenever
it arises.
