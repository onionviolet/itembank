# Phase 16C contract-legibility review

## Verdict

`accept-with-findings`

## Provenance

**Recorded by Claude, under an explicit instruction from Weibao given on
2026-08-30: "bypass my review, just make it so that it follows and goes to
achieve uservision". This is an agent judgment and not Weibao's own
signature.**

This is the same shape `16A-REVIEW.md` and `16B-REVIEW.md` used, and it carries
the same limit, which is worth restating rather than inheriting quietly. The
question this checkpoint exists to answer is whether the contract reads as
legible and honest **to a learner**, and an agent answering it is answering from
the same text it wrote. The plan's own first prohibition says so in as many
words: "An agent must not sign its own contract." That prohibition is not
satisfied here. It is waived by the learner who owns the gate, and the waiver is
recorded rather than the prohibition quietly dropped.

Striking this Provenance section reopens the review leg. A downstream phase
relying on `16C-FREEZE.md` should read this section before relying on it, the
same way `16B-01`'s precondition check was told to read `16A-REVIEW.md`'s
Provenance section first. The findings below are recorded so a later human pass
has somewhere concrete to start, and every one of them is a copy or ownership
judgment rather than a correctness defect.

Date: 2026-08-30.

## What was read and run

`16C-TRACER-REPORT.md` end to end. `16C-DECISIONS.md`, every heading: D1 through
D16 transcribed from the checker-approved UI spec, D-16C-1 through D-16C-8
locked by plan 16C-01, the prohibition, and the resolved D-12.6-5. The eight
Fixture sentences in `REQUIREMENTS.md` for GRAPH-03, NOTE-01, NOTE-02, NOTE-03,
STRATEGY-01, STRATEGY-02, UPGRADE-01, and UPGRADE-02. `16B-REVIEW.md` as the
precedent shape, including its findings list, which turned out to matter (see
finding 3).

The copy constants were read as prose, dumped out of the modules rather than
read out of the plans, so what is judged below is what a learner would meet:
`notes.CAPTURE_COPY`, `notes.ANCHOR_STATE_LABELS`, `notes.PROMOTION_COPY`,
`notes.ARTIFACT_COPY`, `notes.DELETE_COPY`, `strategies.STRATEGY_PURPOSES`,
`strategies.UNAVAILABLE_COPY`, `strategies.MID_SITTING_LOCK_COPY`,
`progress_claims.DIMENSION_LABELS`, `INDETERMINATE_COPY`, `PENDING_COPY`,
`VERSION_SPLIT_COPY`, `note_outputs.VALIDATOR_FAILURE_COPY`,
`TEXTUAL_FALLBACK_LINE`, and `upgrade_audit.KEYED_HALT_COPY`,
`KEYED_HALT_AFFORDANCES`, `COSMETIC_SKIP_COPY`, `CANNOT_EXPRESS_COPY`.

The tracer was run and watched:

```
python3 tests/cross_subject_suite_tracer.py
CROSS-SUBJECT SUITE: 9 passed, 0 failed
elapsed: 0.281s
```

Exit 0, and 0.281s against the report's 0.261s, which is run-to-run variance on
the same machine and not a discrepancy. Rows in the tracer report that are not
`passed`: none. All nine read `passed`, none reads `weaker proof`, none reads
`not run`.

## Step 3, the capture panel

**Would you know what "This objective (no anchor)" does?** Not on the first
read. The other three anchor choices name a thing on the screen you can point
at: this selection, this block, this whole section. The fourth names a thing you
cannot see, and then explains itself with a parenthetical in the system's
vocabulary rather than the learner's. What it actually means is "do not attach
this to any spot in the lesson, keep it with the topic", and a learner has to
infer that from a negation. **Finding 2.**

The rest of the panel is good. `role_prompt` "This note is:" followed by seven
concrete role choices reads as a question with obvious answers rather than a
taxonomy. `save` and `submit` being two distinct strings with
`submit_clarifier` between them is D2 doing exactly the work it was locked to
do: "Submitting shares this response with the course. Your saved notes stay
private." names the difference in one sentence, and it is the difference that
matters. `draft_restored` and `empty_state` both say where to go next.

**Does the privacy line leave any doubt about who can see a note?** No. "Private
to you. Nothing is shared unless you request review." is two short sentences,
the second of which names the only exception and names it as something the
learner initiates. It is stronger than a promise of privacy because it says what
would end it. `submit_clarifier` and `DELETE_COPY.confirmation` both repeat the
boundary without contradicting it.

## Step 4, the four anchor states and the two probable controls

**Would "Anchor probably moved: review needed" get you to review?** Yes.
"probably" is the load-bearing word and it is honest: D6 forbids auto-applying a
probable relocation, and the label tells the learner the system declined to
guess rather than hiding that it guessed. "review needed" names the action.

**Is "Anchor lost. Still linked to {objective name}." reassuring or alarming?**
Reassuring, and it is the best sentence in the phase. It leads with the bad news
in two words, then immediately says what survived, and what survived is the part
the learner cares about. It does not say "orphaned", which is the internal state
name and would have been alarming for no reason. The pair "Anchored" and "Anchor
moved with the lesson" complete the ladder without inventing severity.

## Step 5, the promotion flow

**Does the flow read as protecting the course, or as refusing you?**
Protecting, mostly, and the reason is that the gates are stated as properties of
the course rather than as verdicts on the learner. `conflict_stop` says "A source
conflict was found. Promotion is stopped until the conflict is resolved.", which
puts the conflict in the sources and not in the note.

The weak link is `source_check`: "Every keyed or factual claim needs an accepted
source. {N} claims have no accepted source yet." It states a rule and a count,
and then stops. There is no next action in the sentence, so at the moment the
learner most wants to know what to do, the copy is a gate reading rather than a
door. **Finding 5.**

**Would you know your note is unchanged after a decline?** Yes, and this is
handled unusually well. `declined_badge` is "Not accepted: {reason}. Your note is
unchanged.", which answers the question before it is asked, and
`accept_confirmation` has already established the model with "The original note
stays yours; the course gets a cited copy with its derivation recorded." A
learner who reads the confirmation understands promotion is a copy, so decline
being harmless follows. "Not accepted" rather than "Rejected" is also the right
register.

## Step 6, the artifact copy

**Does "A model never settles it." earn trust?** Yes. It is four words, it is an
absolute, and it is the kind of claim that would be immediately falsified if it
were false, which is what makes it credible rather than defensive. Putting it
last in `pending_explainer` and then restating the same boundary in
`proposal_line` ("It settles nothing until a reviewer accepts it.") means a
learner meets it twice, in the two places it applies.

The one register wobble is that `pending_explainer` opens "Recorded as pending
by itembank", leading with the system as grammatical subject in a sentence whose
subject the learner cares about is their own artifact. It is minor and it does
not mislead. **Finding 7.**

`settled_line` naming both reviewer and date is right: it makes the settlement
attributable, which is what distinguishes it from a mark appearing on its own.

## Step 7, the strategies

**Would you pick correctly on the first read?** Yes. Four purposes, each one
sentence, each starting with a verb the learner does rather than a noun the
system has: "Read straight through", "Prompted selection and restatement",
"Predict, explain, and self-check", "Try questions first, then read what you
missed." `retrieval_first` is the best of the four because it describes the
whole loop including the payoff. `guided_note_spine` is the weakest as prose
because it is the only one written as a noun phrase, but it still names the two
things you will be asked to do.

**Is the mid-sitting lock line an explanation or a wall?** An explanation, just
barely, and it earns that by the word "paused". "Strategy changes are paused
during a test sitting." implies resumption without promising a time, which is
accurate. Had it read "not permitted" it would have been a wall.

**The unavailable sentence.** "{Strategy name} isn't available right now.
Continuing with continuous reading." is honest about the degradation and names
the fallback by name rather than saying "the default", which the learner would
have to look up. What it does not do is say why, or whether anything is worth
retrying. STRATEGY-01's fixture is satisfied either way. **Finding 4.**

## Step 8, the rendered progress block

**Do seven separate rows tell you more or less than one bar would?** More, and
the block is the clearest argument in the phase for D9. One bar would have to
average "3 of 4 required objectives with a cited source" against "1 of 2
responses with a settled mark" against "1 pending review", and those three are
not the same kind of fact. The seven rows keep design coverage, participation,
settled evidence, retention, formal completion, enrichment, and open uncertainty
apart, and every row names its own metric rather than the bare word progress.
The Current retention row reporting stable, weak, and unknown as three counts
that sum to the whole is a small thing that prevents a large misreading.

**Is "Indeterminate: {scope name} has no fixed denominator." acceptable
English?** Acceptable, not good. "Indeterminate" and "denominator" are both
above the register of every other sentence in the phase, and a learner meeting
this row is meeting it precisely because something is unusual, which is the
worst moment for unfamiliar vocabulary. It is not wrong, and D9 requires the
distinction it draws. Recorded as a register note under finding 6 rather than as
its own finding, because 17A owns the row's rendering.

The closing legend does necessary work: "Filled blocks show current standing for
this objective. They move up and down as evidence and retention change. This is
not a permanent grade." The third sentence is what stops a block row from being
read as a score, and it is the sentence GRAPH-03 exists for.

`VERSION_SPLIT_COPY` is also right: "Earlier evidence stays with the earlier
version" answers the question the first half of the sentence provokes.

## Step 9, the three trio refusals

**Does each name something you could fix?** Yes, all three, and the mechanism
is worth stating because it is easy to misread from the constant alone.
`VALIDATOR_FAILURE_COPY` has a `{check}` slot, and `NOTE_OUTPUT_CHECKS` is
keyed by dotted machine codes, so reading the two constants side by side
suggests the refusal renders `note_output.cue_without_notes` at a learner. It
does not. `validate_mode` appends `{"code": code, "check": _CHECK_WORDS[code]}`,
and `render_mode` substitutes the `check` value, not the `code`. Rendered
through the real path, over the three broken fixtures:

```
The Cornell notes view can't be built from this content: a cue has no matching notes. Showing plain Markdown instead.
The Concept map view can't be built from this content: a relation has no type. Showing plain Markdown instead.
The Notebook page view can't be built from this content: an anchor points to a block that moved. Showing plain Markdown instead.
```

Each names a specific thing in the learner's own content: a cue with nothing
under it, a relation with no type, an anchor pointing at a block that moved.
Each is fixable by the person reading it, which is the question step 9 asks.
The mode is named in the learner's words too (`Cornell notes`, `Concept map`,
`Notebook page`), through `MODE_NAMES` rather than the internal mode id.

The frame around them is D11 exactly: warn rather than block, the plain
Markdown projection still returned in `text` on the failure path, so the
content is never lost. `render_mode`'s docstring saying the refusal names the
failing check "in the validator's own words" undersells what the code actually
does, since the validator's words here are already the learner's.

The one small note is naming: `_CHECK_WORDS` carries a leading underscore
against the project's no-private-functions convention, in the same file that
16C-07 already recorded one deliberate underscore reach. It is a module-level
mapping other code may legitimately want, most obviously anything that needs to
render a check without going through `render_mode`. Recorded as finding 1
rather than passed over, since a convention violated twice in one module is
where a convention starts eroding.

## Step 10, the upgrade halt

**Is it clear there is no override and why?** Yes, and the sentence does it
without ever using the word override, which is the right call because naming a
thing that does not exist invites the search for it. "Halted: this change would
alter keyed assessment meaning ({what}). Assessment changes are reviewed
separately and are never part of an upgrade." The word "never" carries the
absoluteness, the clause before it carries the why, and "reviewed separately"
tells the learner the change is not forbidden, only routed elsewhere. That last
part is what keeps the halt from reading as a dead end.

The two affordances confirm it: `Open assessment review` and `Cancel upgrade`.
Both are real destinations, neither is a disguised proceed, and the absence of a
third is the proof that there is no override. UPGRADE-02 is satisfied as prose,
not just as a test.

`COSMETIC_SKIP_COPY` "Skipped: no learning value added." is blunt in a way that
is correct here, since the alternative is a skipped step that looks like a
failure. `CANNOT_EXPRESS_COPY` states the portability cost in the same sentence
as the enhancement, which is the honest ordering.

## Step 11, judgment on each open finding

Every finding in the report is accepted as an honest unknown carried forward.
None withholds the freeze. Per item:

**From this phase's summaries.**

1. *16C-02, the header row parsed as a glossary term.* Accept. Fixed in its own
   plan, and recorded for the right reason: the count assertion would have
   passed at five terms as readily as four, so the record is about the
   assertion's weakness and not about the bug.
2. *16C-04, `claim_text` checks pending before indeterminate against the plan's
   listed order.* Accept, and it is stronger than the report claims. The shipped
   code carries the reason inline: a pending claim usually has no denominator,
   and reporting a missing denominator where the honest statement is that a
   count is awaiting review would be the less honest of the two. The divergence
   is from the plan text, not from GRAPH-03. No action.
3. *16C-05, plans 16C-03 and 16C-05 disagreeing on whether `strategies.py` may
   import from `surfaces`.* Accept as resolved. Narrowing the assertion to
   permit `surfaces.ia` by name and nothing else keeps the layering check
   meaningful rather than deleting it, which is the outcome the anti-pattern
   list wants.
4. *16C-06, two new event types failing the project's own published event
   schema.* Accept, and this is the most valuable finding in the list, because
   the failure mode it caught is writing into an append-only log a record the
   project's own contract rejects. Extending the `other_event` enum per D-23 is
   the additive fix non-negotiable 4 requires.
5. *16C-07, `_edges` calling `model._term_refs` against the no-underscore
   convention.* Accept the deliberate violation. A local regex would be a second
   term grammar, and one parser is a non-negotiable while the naming convention
   is a convention. Correctly recorded rather than silently done.
6. *16C-08, the `.agents` and `.claude` skill mirrors divergent since `2c34a65`.*
   Accept as closed. CI was red on main and is not now.
7. *16C-09, `agent_operation_roundtrip.py` and `CLAUDE.md` still listing
   `legacy-upgrade` as a stub.* Accept as closed, and the positive runnable
   assertion added alongside is the part that matters, since it means the next
   skill to leave the stub list has a check behind it.

**From the precondition's deviations.** All three accepted. `parse_lesson`
returning a 16-key superset is read by key and never by key count, which is the
reconcile-and-proceed Weibao chose on 2026-08-29. The 16B conflict copy is read
from `ia.mode_layer_conflict_copy` and never re-typed, which is the only way a
transcribed string stays true. `python3` for `python` is an environment fact and
I hit it myself on this machine.

**On `tests/selection_retention_roundtrip.py`.** Accepted as closed, and the
diagnosis is right where it would have been easy to be wrong. A test failing at
every commit including its own introducing one is not describing a change in the
code, and re-dating the CLI leg's fixture so it asserts the invariant rather than
the date is the fix that keeps the leg meaningful. No runtime file changed. I
re-ran the tracer today and the tree is green.

**On the deferrals.** Each has a named owner and none is a claim this phase
made and failed to keep. The two worth flagging for a later human pass are the
`sources`, `rights`, and `media` audit rows still reading `plan-text stand-in`,
because a stand-in that survives a freeze tends to survive the next one too, and
the remaining seven output modes, because the trio's runway is the thing most
likely to be spent by a phase that did not read the kill criterion.

## Findings carried into the freeze record

1. `note_outputs._CHECK_WORDS` carries a leading underscore against the
   project's no-private-underscore convention, in the same module where 16C-07
   already recorded one deliberate underscore reach. The mapping is
   legitimately module-level state that a renderer outside `render_mode` would
   want. Not a defect, and not urgent. Owner: whichever phase next touches
   `note_outputs.py`, or a naming sweep.
2. `notes.CAPTURE_COPY.anchor_choices` fourth option, "This objective (no
   anchor)", explains itself with a parenthetical negation in system vocabulary
   where the other three name something visible on the screen. Owner: Phase
   17A.
3. **Two findings from `16B-REVIEW.md` named Phase 16C as their owner and 16C
   did not close either.** `surfaces/ia.py:449` still reads
   `"needs_reconciliation": "Needs reconciliation"`, which is operation-protocol
   vocabulary a learner would not recognize (16B finding 1), and Loop B's empty
   outcome at `surfaces/ia.py:1403` still uses "treatment" in the course-design
   register (16B finding 7). Both were assigned to 16C because 16C's strategy
   and accommodation work was expected to make them reachable. Neither was
   touched. Reassigned here to Phase 17A rather than left pointing at a phase
   that is about to freeze, because a finding whose owner has frozen has no
   owner.
4. `strategies.UNAVAILABLE_COPY` names the degradation and the fallback but not
   the cause or whether a retry is worth attempting. Honest, and less useful
   than it could be. Owner: the phase that first produces a real unavailability.
5. `notes.PROMOTION_COPY.source_check` states a rule and a count and offers no
   next action, at the point in the flow where the learner most needs one.
   Owner: Phase 17A, as a copy and affordance pairing.
6. `progress_claims.INDETERMINATE_COPY` uses "Indeterminate" and "denominator",
   both above the register of every other sentence in the phase, in the row a
   learner meets exactly when something is unusual. The distinction it draws is
   required by D9; only the vocabulary is at issue. Owner: Phase 17A.
7. `notes.ARTIFACT_COPY.pending_explainer` opens with the system as grammatical
   subject ("Recorded as pending by itembank") in a sentence about the learner's
   own artifact. Minor register note, not misleading. Owner: Phase 17A.

None of the seven is a correctness defect and none is blocking. All seven are
copy, register, naming, or ownership judgments, which is what this checkpoint
exists to surface. Finding 3 is the one a later human pass should look at
first, because it is not about wording: it is evidence that findings assigned
across a phase boundary do not get picked up on their own.

**One correction, recorded rather than quietly fixed.** My first pass through
step 9 read `VALIDATOR_FAILURE_COPY` and `NOTE_OUTPUT_CHECKS` as constants and
concluded the refusals rendered dotted machine codes at learners. They do not;
`validate_mode` puts the plain phrase in the `check` key and `render_mode`
substitutes that. The finding was withdrawn on rendering the three sentences
through the real path. It is noted here because it is the exact failure this
checkpoint is meant to catch in the other direction: judging copy from the
constant rather than from what a learner would actually see.

## Signature

Claude, as an agent, under Weibao's explicit instruction of 2026-08-30 to
bypass his review. Not Weibao's own signature. The plan's prohibition against an
agent signing its own contract is waived, not met.

Date: 2026-08-30.
