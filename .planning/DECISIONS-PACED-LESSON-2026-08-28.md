# Decision packet, answered: paced lessons with checkpoints

Written 2026-08-28. This file does two things: it records that **the "eight
decisions only Weibao can make" are closed**, and it answers the three open
paced-lesson questions that `PROMPT-paced-lesson-checkpoints-2026-08-28.md`
put in front of him.

## Provenance, stated first so it can be checked rather than trusted

**Weibao's instruction, 2026-08-28, quoted:** "honestly, just decide for each
accordingly to uservision of modularity and improvability and achiving the end
goal".

That is an explicit, in-session delegation of these three calls to the agent,
with a named decision rule. It is not a standing overnight authorization and it
is not a silent default. **The answers in section 2 are therefore agent
judgments made under a quoted delegation, not Weibao's own words**, and they are
labelled that way throughout. Striking this provenance section reopens all
three. Each answer names the reconsideration condition that would reverse it.

## 1. The eight decisions are already closed, and the prompt that says otherwise is stale

`PROMPT-paced-lesson-checkpoints-2026-08-28.md` closes by saying "Phase 16A is
planned and unexecuted, 16B halts on its precondition, and 14B waves 4 to 6 and
all of 14C are blocked on eight decisions Weibao has not made." That paragraph
was written from `NEXT-2026-08-27.md` and every clause of it is now false. The
tree was checked rather than remembered, which is the discipline
`NEXT-2026-08-27.md` itself names at its close.

| Blocker, as listed on 2026-08-27 | State on 2026-08-28 | Evidence |
|---|---|---|
| D-14B-1 sidecar path and 13.9 supersession | answered | `14B-DECISIONS.md` D-14B-1 |
| 14B-04 `migrate` operation or record type | answered, record type | `14B-DECISIONS.md` D-14B-3 |
| 14B-05 manifest contents and package shape | answered | `14B-DECISIONS.md` D-14B-4 |
| 14B-06 which interfaces freeze | answered, and executed | `14B-DECISIONS.md` D-14B-5, `14B-FREEZE.md` |
| 14C-01 locator schema and primary vs alongside | answered, option-a, promote | `14C-DECISIONS.md` D-14C-1 |
| 14C-07 EPUB path and the AGPL question | answered, stdlib, ebooklib parked | `14C-DECISIONS.md` D-14C-2 |
| 14C dependency adoption | approved, six packages | `14C-DECISIONS.md` D-14C-3, `VENDORED.md` |
| 17A-04 browser harness supply chain | approved with ffmpeg | `17A-04-DECISIONS.md` D-17A-04-1 |

Phase 14B is frozen (`14B-FREEZE.md`, 2026-08-27). Phase 16A is frozen
(`16A-FREEZE.md`). Phase 16B's precondition passed on 2026-08-28 and Phase 16B
is frozen (`16B-PRECONDITION.md` dated result line, `16B-FREEZE.md`).

**What is actually open is execution, not decision:** `14C-02` through `14C-08`,
all of 15A, all of 15B, all of 16C, `17A-04`, and all of 17B are planned and
unexecuted. None of them waits on an answer.

So paced lessons are not a ninth open front on top of eight unanswered
questions. They are a first open front on top of zero. That changes the balance
the prompt was weighing, and it is why the three questions are answered here
rather than deferred again.

## 2. The three answers

The decision rule Weibao named is modularity, improvability, and reaching the
end goal. Where an option is reversible it is preferred; where an option would
publish a contract that a later change must migrate, the narrower option wins.

### D-PACED-1. Pacing is an authored property, read through a precedence ladder, with a reader control that may only coarsen

**Answer to question 1, the fork named in research section 4a.**

**Pacing is authored.** A step is a durable thing that can be cited and resumed.
The research file already establishes why, and it establishes it as a
correctness property rather than a preference: a boundary computed at render
time moves when the author edits anything earlier in the document, so a resumed
position and a recorded step reference both silently point somewhere else. That
rules out candidate F as a boundary *source*, and it is the whole reason the
fork has a right answer instead of a taste.

**The ladder, in precedence order.** Candidates A, B and F are not rivals, as
section 4a observes, so they are composed rather than chosen between:

1. An explicit authored marker, if the lesson carries one. Candidate A.
2. Else the configured heading level for that lesson. Candidates B plus C.
3. Else the whole document as a single step, which **is exactly today's
   behaviour**, so every lesson already written renders byte-identically and the
   format change is additive in the sense `PLANNING-DIRECTIVES.md` non-negotiable
   4 requires.

**The marker must carry an author-assigned id.** This is the one place this
answer goes beyond the tabled options, and it is forced by the same identity
argument that killed F. A bare thematic break has position-derived identity: the
third break is the third step, so inserting a break at the top renumbers every
step after it and breaks resume and step citation in precisely the way a
renderer-computed boundary does, only at authoring granularity instead of render
granularity. An unidentified marker inherits F's defect. Therefore the marker is
an authored line carrying a stable step id, and the id, not the ordinal, is what
a resume position and a checkpoint anchor record. The exact syntax is **not**
frozen here; only the requirement that it carry an id is.

**Candidate G, the reader's granularity control, is accepted in one direction
only.** The reader may coarsen: collapse the ladder's output back to the whole
document, or to a larger grouping. The reader may never introduce a boundary the
author did not author, because a reader-invented step has no identity to cite or
resume. So pacing is authored and *presentation of* pacing is a preference, which
is the split the surfaces rule already draws.

**Candidate H is accepted as the improvability path and deferred.** Agent-proposed
markers accepted by the author as a bounded diff is how rung 1 reaches legacy and
imported material without a hand edit, and it rides the review path that already
exists rather than needing a new one. It is not needed for the first
implementation and should not be built with it.

**Why this and not the alternatives.** Deciding "view preference" (the other side
of the fork) is cheaper on day one and forecloses step citation, resumable
position, and checkpoint anchoring, which are three of the four things that make
the treatment evidence-bearing at all. Deciding a single boundary rule instead of
the ladder either forces every existing lesson to be re-authored (A alone) or
couples the document outline to pacing so a long section becomes an unreadable
step (B alone). The ladder costs one knob and degrades to current behaviour.

**Accepted cost, named rather than glossed.** The lesson format grows a surface,
and an author now has something to think about while writing. Rung 3 is what
keeps that optional.

**Reconsideration condition.** If the first real paced lesson shows authors
consistently leaving no marker and taking rung 2, rung 1's syntax has failed to
earn itself and should be reconsidered before it is frozen, not after.

### D-PACED-2. A checkpoint attempt is an ordinary attempt in the one evidence store, carried in a lesson-run session, labelled so it can never reach a blueprint denominator by default

**Answer to question 2.**

**No second evidence store, no second scorer, no second session schema.** The
runtime invariant settles this half and it is not reopened. A checkpoint item is
an ordinary bank item, the verdict is the runtime's, and the attempt has the
shape every other attempt has.

**The session object is distinct from a sitting.** Reading a paced lesson opens
one **lesson-run** session that may accumulate several checkpoint attempts, in
the same way a sitting accumulates item responses. A sitting is a form assembled
against a blueprint; a lesson run is not, and calling them the same object would
mean either a sitting with no form or a blueprint with a lesson in it. Distinct
session kind, identical attempt records inside it.

**Denominator exclusion is a label on the attempt, not a hidden record.** The
attempt carries the context it was produced in. A blueprint denominator selects
on that label and excludes lesson-run attempts by default. This is the modular
answer and the improvable one: the evidence is fully recorded and fully visible,
and the question of what may consume it is a read-time policy that a later phase
can change with a query rather than a migration. The alternative, not writing the
attempt or writing it somewhere else, would make the honest answer unrecoverable
and would be the split-evidence failure the teardown already documented in the
specimen.

**This resolves `IL-20260826-10` for this case, narrowly.** Teaching pool versus
exam-fidelity pool is expressible as metadata rather than as structure, exactly
as that entry's backburner note suspected. The item's pool membership and the
attempt's session context are two labels, not two systems.

**Gating, already constrained by `IL-20260828-03` and unchanged here:** a step
gates on *attempted*, never on *correct*; backward navigation and the table of
contents are never gated.

**Reconsideration condition.** If a later blueprint genuinely wants checkpoint
evidence in a denominator, the label makes that a policy change. If instead a
checkpoint attempt is found leaking into a denominator without an explicit
policy, the default is wrong and the exclusion belongs lower in the stack.

### D-PACED-3. A wrong checkpoint rules out and confirms, tier by tier, and the runtime releases each tier

**Answer to question 3.** This is the 2026-08-24 vision entry applied to the
checkpoint case, and it is an addition to the Phase 6 feedback policy rather than
a change to the scorer, exactly as that entry's interpretation records.

In a paced lesson, which is a teaching context and never exam mode, a
not-fully-correct checkpoint discloses in tiers:

- **Tier 1, on the first wrong attempt.** Which of the learner's selections are
  wrong, and which are right. This is the rule-out plus the keep-what-you-got
  that Weibao asked for by name, and it is what turns the retry from a gamble
  into reasoning. It does not reveal unselected correct options, so the item is
  not solved by elimination.
- **Tier 2, with tier 1.** The authored `DA:` rationale for the options the
  learner actually touched, and only those. `DA:` already exists in the format
  and `explain_payload` already carries it, so the missing piece really is only
  the disclosure policy. Spending the panel on the distinction the stem tested is
  the design target; the specimen's habit of restating the stem back at the
  learner is explicitly not copied.
- **Tier 3, on a second wrong attempt or on explicit learner request.** The full
  key and `why`. The learner is never stranded, because the step gates on
  attempted and they could always have moved on regardless.

**Exam mode is untouched and stays silent.** The runtime, not the model, decides
which tier is released, gated by session mode and hint tier. A model argued into
wanting to reveal still cannot.

**Not partial credit.** Nothing here changes `multi` scoring, which stays
all-or-nothing and stays NREMT-conformant. Weibao was explicit that he was not
asking for partial credit, and this answer keeps that separation.

**Reconsideration condition.** If tier 1 turns out to make a four-option `mc`
checkpoint trivially solvable on retry, the tier boundary is wrong for that item
type and belongs per type rather than per mode.

## 3. Where this gets built, and what is not being done today

**Not folded into an existing phase.** 15A is the treatment recommender, 15B is
blueprint and acceptance, 16C is notes, strategies and legacy upgrade. The paced
mode is a lesson-renderer presentation plus a feedback-disclosure tier, and it
belongs to neither. Folding it into 16C would force a replan of nine written
plans to gain nothing.

**It does not depend on anything unexecuted.** Its dependencies are 16A and 16B,
both frozen, plus the shipped Phase 6 feedback ladder. So it can be planned
whenever it is wanted rather than waiting in a queue.

**Placed as a new subphase after 16C and before 17B**, so it lands while the
renderer is already open in 17B's runway rather than opening the renderer twice.

**This file opens no phase, writes no plan, and touches no requirement.** The
decisions are the cheap durable half and they are now recorded. The plan is a
separate sitting and is not started here.
