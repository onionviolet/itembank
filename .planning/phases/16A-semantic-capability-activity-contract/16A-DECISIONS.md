# Phase 16A decisions

This file is the single source of truth for every Phase 16A grammar decision.
Every later 16A plan reads it before its first task, so a token, an arity, a
vocabulary, or a fallback rule is transcribed from here rather than re-derived
from research or from plan prose. Sections `## D-16A-3` through `## D-16A-9`
were transcribed by plan 16A-01 Task 1 from that plan's objective, which is
where those six answers were locked. Tasks 2 and 3 of the same plan append
`## D-16A-1` and `## D-16A-2` below, after the probe classification note,
because those two were blocking checkpoints and were answered separately.

## D-16A-3. Required and optional semantics and the unknown-semantic contract

**Date:** 2026-08-27. Locked by plan 16A-01's objective decision table.

**Open question.** How is a semantic marked required versus optional, and what
does an unknown one do.

**Locked answer.** A callout marker may carry a trailing exclamation mark inside
the brackets: `> [!MISCONCEPTION!]` declares the semantic required, and its
absence means optional. Unknown and optional keeps the shipped degradation
unchanged (the block falls through to plain paragraph output byte for byte) and
adds the lint warning `lesson.unknown_semantic`. Unknown and required renders
one locked refusal container carrying the exact copy `This block needs a lesson
feature this reader does not have. Its text is below, unchanged.` followed by
the raw body text, and lint emits the error
`lesson.unknown_required_semantic`. Nothing is dropped and nothing raises.

**Rationale.** CAP-01's Degraded clause verbatim: "an unknown optional semantic
renders its fallback with a warning; an unknown required semantic fails safely".
The trailing marker is captured by the shipped `_CALLOUT_MARK_RE` group 1 with
no regex change, so a bank that uses no exclamation mark parses byte
identically.

## D-16A-4. The semantic profile version directive

**Date:** 2026-08-27. Locked by plan 16A-01's objective decision table.

**Open question.** How is the semantic profile versioned.

**Locked answer.** One preamble directive `[SEMANTIC-PROFILE: <positive
integer>]`, read by `parse_lesson` with the identical `grab()` shape `[GATE:]`
already uses at `model.py:530-535`, defaulting to `1` when absent.
`model.SEMANTIC_PROFILE_VERSION` equals `1`. A non-integer or non-positive value
is the lint error `lesson.invalid_semantic_profile`; the parse never raises and
falls back to `1`.

**Rationale.** PORT-01's "additive, versioned semantic profile", carried on the
shipped directive precedent rather than a new metadata block.

## D-16A-5. The renderer-availability vocabulary

**Date:** 2026-08-27. Locked by plan 16A-01's objective decision table.

**Open question.** What is the closed vocabulary for a capability's
renderer-availability field.

**Locked answer.** `RENDERER_AVAILABILITY = ("available", "degraded",
"unavailable")`, a three member closed tuple in `model.GATE_VALUES`'s exact
shape.

**Rationale.** `16A-RESEARCH.md` Open Question 2, recommendation adopted
verbatim: the binary Degraded clause plus one explicit middle state for partial
breakage.

## D-16A-6. The worked-example bar and the example-order override

**Date:** 2026-08-27. Locked by plan 16A-01's objective decision table.

**Open question.** Does the shipped `[!EXAMPLE]` callout satisfy CAP-01's
worked-example role.

**Locked answer.** Yes, for 16A. Annotated per-step structure is recorded as a
Registered-tier enhancement for a later capability-profile version bump and is
out of scope here. CAP-01's worked-example-first default is enforced as the lint
warning `lesson.definition_before_example`, suppressed only by an authored
`[EXAMPLE-ORDER: definition-first because <reason>]` directive whose reason text
is required and is recorded in the lint report.

**Rationale.** `16A-RESEARCH.md` Open Question 1, recommendation adopted
verbatim, plus CAP-01's own clause "an author or course director may override
per lesson with a recorded reason".

## D-16A-7. The media grammar shape and the dated jurisdiction warning

**Date:** 2026-08-27. Locked by plan 16A-01's objective decision table.

**Open question.** What shape does media metadata take, and does the dated
jurisdiction warning need a structured field.

**Locked answer.** Media metadata is a preamble registry section `## MEDIA`, one
pipe row per asset, read through `model._preamble_section(head, "MEDIA")`,
following `## SOURCES`'s exact shape, with columns in this fixed order: `id`,
`path`, `credit`, `alt`, `rights`, `derivation`, `availability`, `integrity`.
The dated jurisdiction warning stays free prose with a stated date inside the
shipped `[!WARNING]` callout; no structured `effective_date` or `jurisdiction`
field is minted in 16A, and a structured field is a backburner entry contingent
on 15B's staleness machinery.

**Rationale.** `16A-RESEARCH.md` Assumption A3 recommendation and Open Question
3 recommendation, both adopted verbatim.

## D-16A-8. Media rights are declared, not enforced, in 16A

**Date:** 2026-08-27. Locked by plan 16A-01's objective decision table.

**Open question.** Does 16A enforce media rights.

**Locked answer.** No. The `rights` column's vocabulary is
`identity.RIGHTS_STATES` referenced, never a second tuple, and lint validates
membership only. No 16A code path gates on it. Enforcement is deferred by name
to whichever later subphase's execution first packages or exports a media asset,
and that deferral is written into the 16A freeze record rather than left
implicit.

**Rationale.** `16A-RESEARCH.md` Pitfall 4 and Assumption A5: inventing a
working enforcement mechanism against a vocabulary this phase does not own is
how a second rights vocabulary is created.

**Note added 2026-08-27 at execution, routed rather than resolved.** Surfaced
while transcribing this decision and verified against plans 16A-04 and 16A-05
before being recorded, so it is an observation and not a suspicion.

A `## MEDIA` row's `rights` column holds one member of
`identity.RIGHTS_STATES`, so one of `granted`, `denied`, or `unknown`.
Everywhere else in this repository that records rights durably, a rights record
is a seven-key map over `identity.RIGHTS_OPERATIONS`: `identity.rights_default()`
returns one, `journal.commit_operation` stores one on a source object, and the
14C locator sidecar's `$defs.rights` requires exactly those seven keys. **A
media row is therefore coarser than every other rights record in the tree: it
says a right is granted without saying which of the seven operations is
granted.**

**This is not an error in D-16A-8 and does not reopen it.** The decision is
deliberate and consistent across plan 16A-04 step 5 and plan 16A-05, and its
whole purpose is to avoid minting a second rights vocabulary, which referencing
`identity.RIGHTS_STATES` by identity rather than by value achieves. While 16A
declares and enforces nothing, the coarseness costs nothing.

**Where it lands.** It becomes a real question for whichever later subphase
first packages or exports a media asset, which is the same subphase this
decision already names as owning enforcement. That phase cannot decide whether
a media asset may be packaged from a single `granted` without knowing whether
the `package` operation specifically was granted, so it will have to either read
the seven-key record on the underlying source object or widen this column. It is
recorded here so that phase inherits the question instead of rediscovering it.

## D-16A-9. Guided mode's 16A data contract

**Date:** 2026-08-27. Locked by plan 16A-01's objective, not by a checkpoint,
because the orchestrator's phase-shape constraint already settled its scope.
Recorded here for citation convenience.

`lesson_page` gains a keyword argument `mode` with the values `"continuous"`
and `"guided"`, defaulting to `"continuous"` so every shipped caller renders
byte identically. A guided stage is one `###` heading's body split at each
callout boundary: the run of blocks up to and including the next callout is one
stage. Guided mode renders every stage in one document, each inside
`<section class="stage" data-stage="N">`, with only the first stage carrying
`data-stage-open="1"`. No JavaScript, no color, no spacing, no motion, and no
token constant is introduced. Nothing persists across a stage boundary in 16A:
reading position and resume are Phase 16B's, named here so the executor refuses
them rather than deciding.

## Probe classification note

The spec-less edge-coverage probe run for Phase 16A returned two rows marked
`unclassified`. Neither row was dropped. The planner classified both, and each
classification produced acceptance criteria carried in a later plan's
`must_haves`.

- **CAP-01's unclassified row is a completeness question.** Does every named
  role have a rendering path in both modes, and what happens to a role named in
  the requirement but absent from the registry. The acceptance criteria this
  produced are carried in the `must_haves` of plan 16A-03.
- **CAP-03's unclassified row is a derivation question.** Can an output mode
  become the only understandable copy. The acceptance criteria this produced are
  carried in the `must_haves` of plan 16A-07.

## D-16A-1. Semantic-role registry: promote or add alongside, and the seven role tokens

**Date:** 2026-08-27. **Recorded by an agent under a standing delegation from
Weibao, not answered by Weibao directly.** This was a `blocking` decision
checkpoint reserved for him. See "Provenance" below before treating this as his
answer.

**Rated one-way by plan 16A-01.** Whichever representation is chosen is what
real authored lessons are written against from the first corpus file onward, and
what Phases 16B, 16C, and 17A read. The seven token spellings are equally
one-way: they become an authored-content contract the moment a lesson uses one.

**Question, as the plan asked it.** Does the semantic-role registry become the
primary representation of a lesson's teaching roles, with the shipped four
callout kinds becoming entries in profile version 1, or are the seven new roles
added alongside the shipped four as more entries in the existing
`_CALLOUT_KINDS` dict with no promotion, and in either case what are the seven
role tokens literally spelled?

**The options as offered.**

- **option-a (RECOMMENDED DEFAULT).** Add alongside, with the profile version
  recorded beside the vocabulary rather than owning it.
- **option-b.** Promote: the semantic-role registry becomes primary and the
  shipped four become profile version 1 entries.
- **option-c.** Add alongside now, promote behind a recorded trigger later.

**Recorded answer: option-a, the plan's own recommended default.**

`_CALLOUT_KINDS` remains the source of truth for what a callout kind means; it
gains exactly seven entries and nothing about the shipped four changes.

The seven role tokens, as literal strings: `PREREQUISITE`, `MISCONCEPTION`,
`TIP`, `COUNTEREXAMPLE`, `EXCERPT`, `UNCERTAINTY`, `SUMMARY`.

Their seven `(slug, label)` pairs, as literal strings and in the same order:
`("prerequisite", "Before this")`, `("misconception", "Common mistake")`,
`("tip", "Expert tip")`, `("counterexample", "Counterexample")`,
`("excerpt", "From the source")`, `("uncertainty", "Not settled")`,
`("summary", "In short")`.

The semantic profile version (`D-16A-4`) is a separate, additive lesson
directive that records which profile a document was authored against; it does
not own or gate the vocabulary.

**Executor consequence.** Plans 16A-02 through 16A-10 proceed as written. No
plan edit is needed, and no `## D-16A-1a. Promotion trigger` subsection is owed,
because that subsection belongs to option-c and option-c was not chosen.

**Provenance, kept separate from the decision.** Weibao gave a standing
delegation on 2026-08-27, in these verbatim words:

> Make judgement accordingly to user vision and future expnandabiliuty and improvabnility as needed and more

> why do we have a operation contract? ust do it if it serves to achieve user vision

**Interpretation, the agent's and labelled as such.** Those two sentences are
read as authority to record the plan's recommended default on his behalf when
the plan already named one and the research already backed it, rather than as
authority to invent an answer the plan did not offer. That is why the answer
here is option-a exactly as the plan wrote it, with no rider and no variant.
This section is an agent choice under delegation. It is not Weibao's own answer
and must not be cited as one. He can strike it in one sentence.

**Accepted costs, named rather than glossed.** There is no structural place to
record, per role, which profile version introduced a role, so that history lives
only in this file and in the 16A freeze record. A later phase needing per-role
version provenance has to promote then, which option-a defers rather than
avoids. The capability profile registry (`capabilities.py`, D-16A-2) and the
callout vocabulary stay two lists kept consistent by a lint check rather than by
construction.

**What reversing this would cost today.** Today, before any 16A code exists and
before any lesson has been authored against the seven tokens, reversal is cheap:
it is an edit to this section plus the plan-edit list that plan 16A-01 Task 2
already spells out for option-b (rewriting `_CALLOUT_KINDS`, `_callout_spec`,
and `_callout_kind_of`, re-proving `tests/lesson_roundtrip.py`,
`tests/style_roundtrip.py`, and `tests/gate_roundtrip.py`, and adding one task
to plan 16A-03). The cost rises sharply once plan 16A-02 lands and again once
the first corpus lesson uses a token, at which point a rename is a content
migration across every file that used it.

## D-16A-2. Where the capability-profile registry lives and which module owns the media and activity grammar

**Date:** 2026-08-27. **Recorded by an agent under the same standing delegation
from Weibao quoted below, not answered by Weibao directly.** This was a
`blocking` decision checkpoint reserved for him.

**Rated one-way by plan 16A-01.** The module name and boundary appear in every
import in plans 04 through 10, in every structural-ban assertion, in
`schemas/capability_profile.schema.json`'s intended reader, in the 16A freeze
record, and in whatever Phases 16B, 16C, and 17A build on it. Undoing it after
the freeze renames a published surface.

**Question, as the plan asked it.** Does Phase 16A add one new pure root-level
module holding the capability-profile registry and the output-mode composition,
leaving the media and activity grammars in `model.py` where every other preamble
registry already parses, or does the new module also own the media and activity
grammar, or do the profiles fold into `model.py` with no new module at all?

**The options as offered.**

- **option-a (RECOMMENDED DEFAULT).** One new pure module `capabilities.py`,
  with the media and activity grammars staying in `model.py`.
- **option-b.** One new module owning the profiles and both new grammars.
- **option-c.** No new module: capability profiles fold into `model.py`.

**Recorded answer: option-a, the plan's own recommended default.**

The new module's name is `capabilities.py`, a root-level pure module importing
nothing from this repository except `model`, holding
`CAPABILITY_PROFILE_KEYS`, `RENDERER_AVAILABILITY`, `MEDIA_RIGHTS_STATES`,
`MEDIA_AVAILABILITY`, `OUTPUT_MODES`, `BACKBURNER_MODES`, `CapabilityError`,
`profile`, `profiles`, `register`, `static_path`, `compose_outline`,
`compose_glossary`, and `backburner_entry`. `model.py` parses `## MEDIA`.
`model.py` parses `## ACTIVITIES`. `capabilities.py` holds `compose_outline`.

The structural bans that hold are that `capabilities.py` contains no `open(`
call and imports neither `evidence` nor `runtime`, so the rules that it never
writes and never decides disclosure are structural rather than maintained by
care.

**Executor consequence.** Plans 16A-02 through 16A-10 proceed as written. No
plan edit is needed, and neither the option-b nor the option-c consequence list
is owed.

**Provenance, kept separate from the decision.** The same standing delegation
Weibao gave on 2026-08-27, verbatim:

> Make judgement accordingly to user vision and future expnandabiliuty and improvabnility as needed and more

> why do we have a operation contract? ust do it if it serves to achieve user vision

**Interpretation, the agent's and labelled as such.** Read as authority to
record the plan's recommended default on his behalf, not as authority to choose
outside the offered options. Option-a is also the option that keeps one answer
to "where does markdown become a dict", which is the expandability reading of
his first sentence. This section is an agent choice under delegation, not
Weibao's own answer, and must not be cited as one. He can strike it in one
sentence.

**Accepted costs, named rather than glossed.** The capability vocabulary and the
media grammar's `rights` and `availability` columns live in two files, so
`model.lint` imports `capabilities` to validate a `## MEDIA` row's membership.
That is one new import edge on the shipped linter, a real if small weight
increase. A reader asking "what does a media row mean" reads `model.py` for the
shape and `capabilities.py` for the vocabulary.

**What reversing this would cost today.** Today, before `capabilities.py`
exists, reversal is an edit to this section plus the plan-edit list plan 16A-01
Task 3 already spells out for the option not taken. Once plan 16A-04 lands the
module, reversal means moving every symbol above, rewriting every import in
plans 05 through 10, and replacing the `import capabilities` assertion that
16A-01 Task 1 step 3 and every later plan's acceptance criteria depend on. After
the 16A freeze record enumerates the module, reversal renames a published
surface.
