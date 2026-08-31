# Phase 15A four-subject recommendation review

**Dated 2026-08-30.**

## Provenance

**Recorded by Claude, as an agent, under Weibao's instructions of 2026-08-30:
"bypass my review, just make it so that it follows and goes to achieve
uservision", and then "I have no time to work on this myself, so I want you to
finish accordingly to uservision".**

Plan 15A-06 Task 2 is a `checkpoint:human-verify` rated blocking, and its
`<what-built>` block says exactly what is being waived: "What the tracer cannot
decide is whether the recommendations are any good... That judgment is the
freeze gate's actual subject, and an agent never signs it for itself." An agent
is signing it for itself. That prohibition is **waived, not met**.

This is the fourth phase in a row to close a review leg this way, after 16A,
16B and 16C. It is recorded here rather than left to accumulate, because four
is a pattern and not an exception, and because this one is different in kind
from the other three: 16A, 16B and 16C asked whether shipped copy reads
honestly, and this one asks whether a course-design judgment is any good.

Anything relying on `15A-FREEZE.md` should read this section first. Striking it
reopens the review leg.

## What was reviewed

`15A-TRACER-REPORT.md` end to end. The tracer was run and watched:

```
python3 tests/four_subject_review.py
TRACER: 8 passed, 0 skipped, 0 failed
```

Exit 0. The recommendations were then read as prose, one subject at a time:

```
python3 tests/four_subject_review.py --print-recommendations
```

`.planning/ROADMAP.md`'s Phase 15A freeze-gate paragraph,
`.planning/PLANNING-DIRECTIVES.md` section 3a's accepted-recommendation
discipline, and `.agents/skills/OPERATION-CONTRACT.md`'s thirteen numbered
steps were read as the checklist the tracer replayed against.

**Phase 13.9 has been walked.** Checked
`.planning/phases/13.9-walking-skeleton/`, which contains `13.9-01-SUMMARY.md`,
`13.9-02-SUMMARY.md`, and `13.9-03-SUMMARY.md`. The third records under
`## A9 closure state` that all five A9 checkboxes are `[x]`, four closed
2026-08-24 with dated evidence and the fifth closed with its gap named inside
the checkbox rather than hidden. ROADMAP's governance clause that no
14B-or-later freeze commits before this skeleton has been walked is satisfied.

## Per-subject judgments

**A caveat that applies to all four subjects, stated once.** The provider is
`fixtures/mock_backends.py`, whose treatment choice is
`treatment_kinds[len(objective_statement) % 11]`. It is a fixed rule with no
randomness and no clock read, which is exactly what makes backend parity
provable, and it means the treatment choices below are **arbitrary by
construction**. Judging them as course-design calls is judging a hash. What can
honestly be judged is the shape: whether the record is legible, whether
synthesis is unmistakable, whether citations point somewhere, whether the
coverage state is defensible, and whether the outcome vocabulary tells a course
builder what to do. That is what the four blocks below do, and the limit is
recorded as the first concern rather than glossed.

### meridian-field-response, the EMT stand-in

**Is the recommended treatment kind defensible?** No, and not because the
system is wrong. "Choose a body substance isolation level" got `practice` and
"State the number of patients before approaching" got `notes-or-terms`. Both
are plausible by accident. "Identify scene hazards on arrival" got
`direct-reading` from a synthetic passage that says only that it exists to give
the graph kernel something to bind against, which no course builder would call
a reading. The mock is the reason, not the director.

**Is the rationale legible, and obviously synthesis?** Legible, and
unmistakably synthesis. The sentence says so in its own words, and
`synthesis: True` is a schema `const` so no record can claim otherwise. This is
the strongest part of the contract: the label is structural, not a convention.

**Do the citations point at something findable?** Yes for the three bound
objectives: one citation each, carrying a source object id and a locator that
resolves in the source text. No for the three untreated ones, which carry zero
citations, correctly, because no span was approved for them.

**Does the coverage state match what I would have said?** Yes, after the fix
recorded under Concerns. The three bound rows now read `thin` rather than the
provider's claimed `covered`, which is right: the locators resolve but are one
short line, and one short line is not a treatment of an objective.

**Accept, reject, or send back?** Accept the machinery. The recommendations
themselves are not a course-design product and are not offered as one.

### orrery-algebra, the Math 1400 stand-in

**Defensible treatment kinds?** Same answer and same reason. The distribution
is arbitrary.

**Rationale legible and obviously synthesis?** Yes, identical shape.

**Citations findable?** Yes for the bound objectives, zero for the unbound
ones.

**Coverage state?** Yes. Same `thin` classification, same reasoning.

**Accept, reject, or send back?** Accept the machinery.

### lantern-computing, the CSCI 1100 stand-in and the untreated case

**Defensible treatment kinds?** Arbitrary, as above, and here it does not
matter: three of the five objectives never reach a bind at all.

**Rationale legible and obviously synthesis?** Yes.

**Citations findable?** Zero across the board, because the source's rights were
stripped to all-unknown before the pass, so no span was ever approved. That is
the fixture doing its job: the untreated case is caused by a real policy state
and not by the fixture declining to call a backend.

**Coverage state?** `missing` with `match_kind: none` on every entry, which is
the honest reading of an objective whose source could not be opened.

**Accept, reject, or send back?** Accept, and this subject is the most
informative of the four. Three objectives read `refused` with
`director.rights_not_granted` and two read `untreated` with `no-source-bound`,
and the two reasons are genuinely different things: one says the source exists
and you may not use it, the other says there is no source. A course builder
reading only the report would know which to go fix.

### beacon-standards-blueprint, the exam-blueprint stand-in

**Defensible treatment kinds?** **Yes, and this is the one subject where the
answer is yes.** Both bound objectives got `direct-reading`, through the
provider's one deterministic per-subject branch, and for a blueprint objective
that is the right call: the blueprint's published weights are the artifact, and
generating a lesson that restates them would be strictly worse than reading
them. This is the case TREAT-01 exists to demonstrate, and it demonstrates it.

**Rationale legible and obviously synthesis?** Yes.

**Citations findable?** Yes. All three objectives carry one citation each with
a locator that occurs verbatim in the blueprint source.

**Coverage state?** Yes, with one observation recorded under Concerns: the
third objective's locator is its own statement, which appears in the source as
a heading. It resolves exactly, so it is a `locator` match rather than a
`heading-similarity` one, and it classifies accordingly. That is correct
behavior and still worth noticing, because a locator that resolves against a
heading points at a title rather than at a treatment.

**Accept, reject, or send back?** Accept.

## The untreated objective, read specifically

`Predict the value a name is bound to`, in `lantern-computing`, reads
`refused` with reason `rights-not-granted` and code
`director.rights_not_granted`. The journal carries a matching entry whose
`state` is `refused` and whose message names the missing right, so the reason
is recorded and not merely recomputed on read.

Is it legible enough to act on? Yes. The refusal message names the right, the
source, the current state, and the one edit that fixes it: record the right as
granted on that source's rights record, or choose a treatment that does not
consume it. A course builder reading only that sentence knows what to do next.

## The direct-reading binding, read specifically

It reads as a completed decision. `outcome: bound`, `treatment:
direct-reading`, a citation, a resolving locator, and the objective does not
appear in `untreated_objectives` afterwards. Nothing in the record or the
report frames it as a failure to generate: there is no "could not generate"
wording anywhere, and `direct-reading` sits in the same eleven-member
vocabulary as every generative kind and consumes a right through the same gate.
That is TREAT-01's "direct reading is a complete result" holding in practice
and not just in a constant.

## Concerns

1. **Recommendation quality is not tested by anything, here or anywhere.** The
   provider is a modulo rule. The tracer proves the machinery is honest about
   what it did; nothing in this phase proves a recommendation is good. That is
   correct scoping for a freeze gate about contracts, and it means the first
   run against a real model is an unproven step. Owner: whichever phase first
   points `director` at a real provider.

2. **A defect found by reading the recommendations, and fixed rather than
   reviewed around.** `apply_recommendation` was binding the provider's own
   `coverage.state` straight into the `## Bindings` row. That is a model
   certifying its own coverage, which AGENT-02 forbids and which 15A-03's own
   decision table rules out by name ("The provider's proposed `coverage.state`
   is recorded as `proposed_state` and never adopted"). The code now computes
   the state through `classify_coverage` and keeps the provider's as a
   proposal, and it takes an optional `source_texts` so a locator can actually
   be resolved; without it a claim is unverifiable and can never reach
   `covered`. The visible effect is that beacon's bound rows changed from the
   provider's claimed `covered` to a computed `thin`.

3. **`director.coverage_claims_for` cannot reach every coverage state.** It
   builds claims from `## Bindings` rows, and a binding row carries no
   `assertion` column, while `conflicting` is by definition two claims
   asserting different things about one objective. So the four-subject bindings
   produce `thin` and nothing else, and all five states are demonstrated
   through the five-state binding set instead. That is a real limit of the
   sidecar's binding shape, recorded on its own measured line in the tracer
   report. Owner: whichever phase gives a binding row somewhere to carry a
   claim.

4. **An untreated entry still carries a `treatment_kind`.** An entry can read
   `outcome: untreated`, `reason: no-source-bound`, and
   `treatment: assessment-first-diagnostic` at the same time. It is accurate,
   since a treatment was ranked before the bind was refused, and it reads
   badly: a row that names a treatment looks like a row where one was chosen.
   No code depends on it. Owner: whichever phase renders this to a person.

5. **A locator that resolves against a heading classifies as a located match.**
   Correct, since it is an exact resolution and not a similarity match, and
   still worth a later look, because pointing at a heading is not the same as
   pointing at a treatment of the objective. Owner: a later coverage pass.

6. **The four-subject corpus is thin as a proving ground.** Nineteen
   objectives, one source each, one locator each, all synthetic. It exercises
   every contract and stresses none of them. Owner: 15B or later.

## Verdict

`accept with concerns recorded`

Six concerns, all carried into the freeze record's open items. None is a
correctness defect in the shipped surface: concern 2 was a real defect and is
fixed, concern 3 is a recorded limit, and the other four are scoping and
presentation observations.

## Signed

Claude, as an agent, under Weibao's explicit instruction of 2026-08-30 to
finish Phase 15A without him. **Not Weibao's own signature.** Plan 15A-06 Task
2's requirement that a human sign this review is waived, not met.

Date: 2026-08-30.
