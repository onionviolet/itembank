# Phase 15B acceptance-quality review

**Dated 2026-08-30.**

## Provenance

**Recorded by Claude, as an agent, under Weibao's instructions of 2026-08-30:
"bypass my review, just make it so that it follows and goes to achieve
uservision", then "I have no time to work on this myself, so I want you to
finish accordingly to uservision", then "keep going".**

Plan 15B-07 Task 2 is a `checkpoint:human-verify` rated blocking, and its own
prohibition reads: "An agent must not sign its own acceptance-quality review;
the judgment that acceptance, rejection, and staleness dispositions are legible
and correct is a human's, and a green tracer is not that judgment." An agent is
signing it. That prohibition is **waived, not met**.

**This is the fifth phase in a row to close a review leg this way**, after 16A,
16B, 16C and 15A. Across this session the running total is five agent-signed
reviews and five one-way agent-made decisions, one of which amended another
phase's frozen record. That is a standing pattern rather than a run of
exceptions, and it belongs in front of Weibao as one decision instead of five.

Anything relying on `15B-FREEZE.md` should read this section first. Striking it
reopens the review leg.

## What was reviewed

`15B-TRACER-REPORT.md` end to end. The tracer was run and watched:

```
python3 tests/acceptance_tracer.py
TRACER: 7 passed, 0 skipped, 0 failed
```

Exit 0. The artifacts were then printed and read as prose rather than as
assertions: the blocked acceptance's refusal message, the blueprint findings
from the `tool_forbidden` run, the `unverifiable` warn findings from a
partially supplied fact set, the sparse-evidence proposal record in full, and
the course audit's rows.

`ROADMAP.md`'s Phase 15B freeze-gate paragraph, `REQUIREMENTS.md`'s three
Fixture sentences for ACTIVITY-02, RELIABILITY-03 and AGENT-03, and
`PLANNING-DIRECTIVES.md` section 3a's accepted-recommendation discipline were
read as the standard being judged against. `15A-REVIEW.md` was read as the
precedent shape.

**Phase 13.9 has been walked.** Checked
`.planning/phases/13.9-walking-skeleton/`, which contains `13.9-01-SUMMARY.md`,
`13.9-02-SUMMARY.md` and `13.9-03-SUMMARY.md`. The third records under
`## A9 closure state` that all five A9 checkboxes are `[x]`. ROADMAP's
governance clause that no 14B-or-later freeze commits before the skeleton has
been walked is satisfied.

## Judgments

### Step 3, the blocked acceptance

The refusal reads, in full:

> this object depends on 8ce8d8cc23fb4a30, which has changed since the
> dependent recorded fingerprint 'sha256:6db2c792e5f4b83058efe7339b52814e0ccd5a765581b3afc46cd7ce4c49b9ea';
> acceptance is blocked until a reviewer records one of rebind, migrate,
> supersede, retain. A stale derivative is never rebuilt and accepted silently.

**Does it tell you which dependency changed?** Only by opaque id. A reviewer
reading this message alone knows something called `8ce8d8cc23fb4a30` moved, and
has to go look up what that is. The id is the correct durable identifier and it
is not a legible one. **Concern 1.**

**Would you know which of the four to record?** No. The message lists all four
words and offers nothing to choose between them, and the four are not
interchangeable: `rebind` points the dependent at the new state, `migrate`
moves identity, `supersede` replaces the dependent, and `retain` says the
change does not matter here. A reviewer meeting this for the first time has
four words and no basis. **Concern 2.**

**Is it obvious nothing was written and nothing was rebuilt?** Half. The last
sentence, "A stale derivative is never rebuilt and accepted silently", is a
statement about the system's policy rather than about this operation, and it is
the sentence doing the most work. What the message does not say is that THIS
acceptance wrote nothing. The tracer proves it (the sidecar bytes and the
drafted bank's bytes are both unchanged), and the message leaves a reader to
infer it. **Concern 3.**

The full fingerprint is printed at 71 characters. It is precise and it is most
of the message's length.

### Step 4, the blueprint findings

The `tool_forbidden` run produces exactly one block finding:

> `blueprint.tools_not_permitted`: remove the dependency on calculator, or
> record a blueprint version that permits it

**Does it name a field a course builder could change?** Yes, and this is the
strongest copy in the phase. It names the offending value (`calculator`), and
it names both real fixes: change the item, or change the blueprint. Neither is
presented as the obvious one, which is right, because which is correct depends
on facts the system does not have.

**Are the warn findings distinguishable from failures?** Yes, structurally and
in the words. They carry `severity: warn` and the code
`blueprint.unverifiable`, and each names its field and its reason ("no demand
fact was supplied for any item"). The remediation is the part that earns it:
"supply the demand fact for this set, or accept that the exam-fidelity claim
rests on fewer than eight checked fields." That sentence tells a reader exactly
what the warning costs, which is the thing a warning usually fails to say.

**Would you accept the drafted set?** The `tool_forbidden` set, no: one item
depends on a tool the form does not permit, and the fix is small and clear. The
conforming set, yes, with the caveat under Concern 5.

### Step 5, the sparse-evidence proposal

**Reading only this record, would you know how much evidence it rests on?**
Yes, and unusually clearly. `denominator: 2` appears at the top level AND again
inside the single claim, and the claim's evidence block repeats `counted_rows:
2` alongside the window bounds. Three chances to see the number, none of them
requiring the reader to hold anything in their head.

**Does the uncertainty read as honest rather than as a hedge?** Yes.
`"sparse"` is a word, not a number, and the record gives the reader the
denominator to check it against. A hedge is a claim wearing a qualifier; this
is a qualifier with the claim's whole basis attached.

**Are the competing explanations real alternatives?** In the fixture, yes: "the
two attempts were minutes apart, so the second may be recall of the first
rather than learning" is a genuinely different reading of the same two events,
not a restatement. But the fixture wrote that sentence, and nothing in the code
can tell a real alternative from a restatement. The requirement is that the
list be non-empty, which is checkable, and the quality of what goes in it is
not. **Concern 4.**

**Is it obvious this is a recommendation and not something that happened?**
Yes. `"status": "recommendation"` is the second key in the record, and it is a
schema `const`, so no record can say otherwise.

### Step 6, the course audit

**Can you tell which vocabulary each row's state came from?** Yes. Every row
carries a `vocabulary` field naming one of the three, and the report's
`vocabularies_cited` list summarizes which were drawn on. The fixture
deliberately includes two rows whose state string is the same word `covered`
under two different vocabularies, and they stay distinguishable.

**Does any row read as if it were merging two vocabularies?** No. There is
nowhere for a merge to happen: the audit holds no vocabulary of its own, and a
state that is not a member of the vocabulary its row names is refused before
the report is returned.

**Does any number read as a mastery or completion claim?** No. Counts carry
their denominators beside them (`objectives_total` next to
`objectives_with_treatment`) rather than being divided, and a recursive walk
finds no float and no key named for mastery, completion, readiness, progress,
percent or score.

### Step 7, the accepted and rejected migrations

**Is the rejected proposal visible as a decision rather than an absence?**
Yes. The row is present with `state: rejected`, its reviewer, and its review
rationale. A deleted proposal and a proposal that was never made look identical
in a file, and these do not.

**Is the reviewer and the rationale legible on both?** Yes, and one detail is
better than it needed to be: the review rationale lives in its own
`rationale_review` column rather than overwriting the proposal's own
`rationale`. The reason a change was proposed and the reason it was granted are
two different statements, and both survive.

## Concerns

1. **A staleness refusal names its dependency by opaque id only.** A reviewer
   reading the message alone cannot tell which source moved without a lookup.
   The id is the right durable identifier and the wrong thing to show a person.
   Owner: whichever phase first renders a refusal to a human.
2. **The refusal lists four dispositions and offers no basis for choosing.**
   The four are not interchangeable, and a reviewer meeting them for the first
   time gets four words and no guidance. Owner: the same phase as concern 1,
   and it is the more consequential of the two: a wrong disposition is a
   recorded reviewer decision that is hard to see was wrong.
3. **The refusal states the system's policy, not this operation's outcome.**
   "A stale derivative is never rebuilt and accepted silently" is true and
   general; the message never says that THIS acceptance wrote nothing. The
   tracer proves it and the reader has to infer it. Owner: a copy pass.
4. **Nothing can tell a real competing explanation from a restatement.** The
   schema requires the list to be non-empty and cannot require it to be
   useful, so an agent that wanted to satisfy AGENT-03 cheaply could write "the
   evidence may mean something else" and pass. Recorded as a real limit rather
   than a defect: the alternative is a judgement this module has no basis for.
   Owner: the human review that reads a real proposal.
5. **The tracer's conforming set was written by the same agent that wrote the
   gate**, and two of its items failed shipped Phase 11 detectors the agent did
   not anticipate: every distractor lacked a would-be-correct clause, and one
   stem quoted its own answer verbatim. Both were real defects in the fixture
   and both were caught by shipped code. It is a small sample and it points the
   same direction concern 4 does: this phase's self-checks are weakest exactly
   where they check the phase's own judgement.
6. **`BLUEPRINT_CODES` grew 13 to 14 to 19 to 21 to 24 across four plans, and
   each plan's artifacts section counted from the thirteen it inherited rather
   than from what landed.** The code is right and the plan set is wrong in four
   places. Owner: a plan-text correction, or acceptance that the freeze record
   is now the authority for that number.
7. **The evidence-to-graph join is open and this phase does not close it.** The
   evidence log keys events by objective text and the course graph keys
   objectives by opaque id. `blueprint.objective_key` normalizes text
   identically to `director.locator_key` and that is proven for the fixture
   strings; nothing proves every shipped bank objective string round-trips to a
   graph objective id without loss. Already carried as a backstop in plan
   15B-06 and repeated here because it is the largest unproven thing in the
   phase.

## Verdict

`accept with concerns recorded`

Seven concerns, all carried into the freeze record's open items. None is a
correctness defect in the shipped surface. Concerns 1 through 3 are copy and
would be caught by any reviewer reading one real refusal; 4 and 5 are honest
limits on what a self-checking phase can prove about its own judgement; 6 is
bookkeeping; 7 is a named gap with an owner.

## Signed

Claude, as an agent, under Weibao's explicit instruction of 2026-08-30 to
finish without him. **Not Weibao's own signature.** Plan 15B-07 Task 2's
requirement that a human sign this review is waived, not met.

Date: 2026-08-30.
