# Phase 16B contract-legibility review

## Verdict

`accept-with-findings`

## Provenance

**Recorded by Claude, under a standing delegation from Weibao given on
2026-08-28 in response to the Task 2 checkpoint. This is an agent judgment and
not Weibao's own.** Weibao was offered three options (review it himself, sign an
agent-drafted review, or delegate outright) and chose to delegate outright.

Striking this Provenance section reopens the review leg. A downstream phase
relying on `16B-FREEZE.md` should read this section before relying on it, the
same way `16B-01`'s precondition check was told to read `16A-REVIEW.md`'s
Provenance section before relying on `16A-FREEZE.md`.

This is the same shape `16A-REVIEW.md` used, and it carries the same limit: the
question the checkpoint exists to answer is whether the contract reads as
legible and honest **to a learner**, and an agent answering it is answering from
the same text it wrote. The findings below are recorded so a later human pass
has somewhere concrete to start.

Date: 2026-08-28.

## What was read and run

`16B-TRACER-REPORT.md` end to end, `16B-DECISIONS.md` in full, and the copy
tables on `surfaces/ia.py` read as prose rather than as code. The four new
suites were run and watched:

```
python3 tests/ia_route_roundtrip.py        IA ROUTES: 24 passed, 0 failed
python3 tests/ia_storyboard_tracer.py      STORYBOARD: 12 passed, 0 skipped, 0 failed
python3 tests/mode_layer_roundtrip.py      MODE LAYERS: 6 passed, 0 failed
python3 tests/degraded_state_roundtrip.py  DEGRADED: 7 passed, 0 failed
```

A daemon was started over an empty temporary directory and driven as a new
learner would drive it.

Rows in the tracer report that are not `passed`: one, APP-02, marked
`weaker proof`. Open findings: the full list in that report, including twenty
five backstop markers.

## Step 3, the first screen

**Does the first screen tell you what to do next, or does it describe itself?**
It tells you. An empty root renders one course card titled
`Study Skills Basics (Sample)` with the CTA `Start Study Skills Basics
(Sample)`, the note `For exploring itembank. Remove it anytime.`, and the offer
`New here? A short walkthrough shows how a course works.` There is no
product description and no feature list. **Finding:** the CTA repeats the whole
course name including the suffix, so the button reads `Start Study Skills Basics
(Sample)`, which is long and puts the least useful word last.

**Is it obvious that the sample course is a sample, without reading closely?**
Yes. `(Sample)` is inside the name string itself rather than in a renderer, so
it appears in the card title and again in the CTA, and the note beneath says
what it is for.

**Would you take the walkthrough, and did its four steps tell you anything you
would not have worked out?** Steps 1 and 3 are close to self-evident from the
screen. Steps 2 and 4 earn their place: step 2 names the seven course areas as
one click away, and step 4 names what itembank always decides for itself, which
is the one thing the interface does not otherwise volunteer. **Finding:** two of
four steps are low-value; a two-step walkthrough would likely land better.

**Could you find the remove control, and did the confirmation tell you what
would actually happen?** Yes to both. The control sits inside the sample's own
card and the confirmation reads `Remove this sample course? This deletes its
bundled files and cannot be undone.`, which names the effect and its
irreversibility. It is accurate: the action deletes exactly the bundled files.

## Step 4, the eight degraded sentences

Each is judged on whether it says what happened in words a learner would use,
whether the next action is something they could do right now, and whether it
could mislead about lost work.

| State | Says what happened | Next action is doable now | Misleads about lost work |
|---|---|---|---|
| `crash` | Yes. "Restored your last saved position" is plain and leads with the good news. | Yes, `Continue where you left off`. | No, and it actively prevents the error: "Nothing was lost since your last saved step" is the exact qualifier that stops a false alarm. |
| `cancelled` | Yes. | Yes, resume or discard, both offered. | No. "were not saved as final" is precise about the status of the partial results. |
| `disk_full` | Yes, and it names both causes it cannot distinguish. | Yes, free space then retry. | No. "Your previous version is intact" is the sentence that matters and it is second, where it is read. |
| `offline` | Yes. | Yes, keep working. | No. |
| `permission_denied` | Yes, and it shows only a basename. | Yes, re-grant or continue. | No. |
| `future_schema` | Yes. | Yes. | No. "nothing is changed or deleted" is the right reassurance. |
| `agent_unavailable` | Yes. | Yes, continue the authored loop. | No. |
| `course_corrupted` | Yes. | Yes, both offered. | No. |

**Finding:** `disk_full` runs to three sentences and is the longest of the
eight. **Finding:** `offline` says "Anything that needs a network connection is
marked unavailable below", which promises a marking this phase does not
render, because no route produces the offline banner yet. That is a sentence
that will be true when a producer exists and is not true today.

No sentence in the eight would make a learner think they had lost work when
they had not, or the reverse. That was the specific risk and it is not present.

## Step 5, the twelve help entries

| Code | Cause explains, or restates the name | Next action specific enough |
|---|---|---|
| `ia.activity_unavailable` | Explains. | Yes. |
| `ia.agent_unavailable` | Explains. | Yes, and it enumerates what does not need a model. |
| `ia.cancelled` | Explains. | Yes. |
| `ia.course_corrupted` | Explains. | Yes, two routes forward. |
| `ia.crash_recovered` | Explains. | Weak. "Continue where the resume cue points" assumes the reader knows what a resume cue is. |
| `ia.disk_full` | Explains. | Yes. |
| `ia.future_schema` | Explains. | Yes. |
| `ia.offline` | Explains. | Yes. |
| `ia.permission_denied` | Explains. | Yes. |
| `ia.route_not_found` | Explains, and names the three likely causes. | Yes. |
| `ia.sample_course_removed` | Explains. | Yes. |
| `ia.walkthrough_unavailable` | Explains. | Yes. |

**Is there a code whose page you would close no better off?** One:
`ia.crash_recovered`. Its cause is already the banner sentence verbatim and its
next action points at "the resume cue" without saying where that is. A learner
who followed the help link learns nothing the banner did not say. **Finding.**

## Step 6, the six attention chips

`Up to date`, `{N} due`, and `{N} pending review` are immediately clear.
`Needs your input` is clear. `Showing last valid overview` is clear enough in
context, because it appears on a card that visibly offers two recovery actions.

**Is `Needs reconciliation` meaningful?** No, not to a learner. It is the one
chip written in the vocabulary of the operation protocol rather than the
learner's. A learner seeing it on a course card would not know what is being
reconciled, by whom, or what they are being asked to do. **Finding, and the
strongest one in this review.** Suggested alternative: `Two versions disagree`,
or `Needs your decision`, either of which names the situation rather than the
internal operation. This is not blocking, because the chip is currently
reachable only when a course record's 14A object state is `conflict`, which no
16B fixture produces, so no learner can see it yet.

## Step 7, the seven mode layers and the conflict sentence

**Does the conflict sentence read as an explanation or a refusal?** As an
explanation. `Timed test mode is set by your instructor's policy for this
course and can't be changed here.` names who decided, scopes it to this course,
and says where the control is not, rather than saying no. The phrase "for this
course" carries real work: it tells the learner the setting is not globally
lost.

**Is it clear on the settings page which two layers are fixed and why?**
Partly. The disclosure is headed `Always fixed by itembank`, which is clear, and
all seven layers render inside it with their controller text, which is what
makes the two fixed ones legible by contrast. **Finding:** because all seven sit
under one heading that says "Always fixed", a reader skimming could take the
heading to apply to all seven rather than to the two. The five configurable rows
are distinguished only by their controller text and a class name. A sub-heading
separating the two groups would fix it.

## Step 8, the locked refusal card

Rendered: header `Second hint tier, locked`, body `Unlocks after you submit an
attempt on this item.`

**Does it read as a rule you understand, or as a wall?** As a rule. It names the
exact thing that unlocks it, and that thing is an action the learner was already
going to take, so the card reads as sequencing rather than as denial.

**Would you try to argue with it, and does anything invite that?** No, and
nothing does. There is no text field, no button beyond at most one, no
apology, no encouragement, and no first-person voice. The absence of an
apology is what makes it read as a rule; an apology would imply the rule was
negotiable.

## Step 9, the seven empty-outcome sentences

All seven read as "something ran and produced nothing", not as "something
broke". Each names what was searched or considered and then offers two moves.
Loop A's is the clearest test of this, and it passes: "Nothing new was found in
the roots you approved" attributes the emptiness to the roots the learner chose,
which is informative rather than alarming.

**Finding:** loop B's "there is nothing to give a treatment" uses "treatment" in
the course-design sense, which is the same register problem as `Needs
reconciliation`, though milder, and loop B is a course-builder surface rather
than a learner one, so the register is more defensible there.

## Step 10, per-item judgment on the backstop list

Twenty five backstop markers are listed in the tracer report.

**Accepted as honest unknowns carried forward:** all twenty five. None should
withhold the freeze, and the reasoning divides into three groups.

- **Twelve are loading-state and overflow claims** (16B-02 both, 16B-04 first
  two, 16B-05 second and third, 16B-06 all three, 16B-08 third, 16B-09 last).
  Every one of them is unreachable by construction today because every 16B read
  is synchronous and server-rendered, and every one names Phase 17A or a
  held-out visual test as its owner. A phase that is explicitly not a visual
  freeze cannot close them, and asserting them would be asserting a state that
  cannot occur.
- **Two were actually proven** and the tracer report says so: 16B-08's banner
  precedence, proven over all 28 pairs, and 16B-09's idempotent removal and
  replayable walkthrough. They are recorded as backstops because their plans
  marked them so before the evidence existed; the record now shows the
  evidence.
- **Eleven need a producer or a record this phase does not build** (16B-04's
  torn-read claim, 16B-05's focus timing and deep-link length, 16B-08's generic
  refusal degradation, competing refusal reasons, multiple locked cards, and
  banner-before-recovery ordering, 16B-09's job-in-flight, already-removed
  first launch, and corrupted bundle). Each is honest: the thing that would
  exercise it does not exist yet, and inventing one to satisfy a marker would
  be worse than carrying it.

The one I would flag for a later human pass rather than accept silently is
16B-09's "a long-running job never blocks Learn, Practice, Test, or Evidence".
The tracer report already records it as only partially proven: `/learn` and
`/activity` both returned 200 mid-walkthrough, but no durable job was actually
in flight, because no route can start one. It is carried, correctly, but it is
the backstop closest to being a real claim about behavior rather than about
rendering.

## Findings carried into the freeze record

1. `Needs reconciliation` is written in operation-protocol vocabulary and would
   not be meaningful to a learner. Not currently reachable by any 16B fixture.
   Owner: Phase 16C, alongside the strategy and accommodation work that first
   makes it reachable.
2. `ia.crash_recovered`'s help page restates its banner and its next action
   points at "the resume cue" without saying where that is. Owner: whichever
   phase first produces a crash banner.
3. The `offline` degraded sentence promises "Anything that needs a network
   connection is marked unavailable below", a marking no 16B route renders,
   because no producer for the offline state exists yet. Owner: the phase that
   adds the producer.
4. The settings mode-layer disclosure puts all seven layers under a heading
   reading `Always fixed by itembank`, which could be read as applying to all
   seven. Owner: Phase 17A, as a rendering and hierarchy change.
5. The sample course's CTA reads `Start Study Skills Basics (Sample)`, which is
   long and ends on the least useful word. Owner: Phase 17A.
6. The walkthrough's steps 1 and 3 are close to self-evident from the screen
   they describe. Owner: Phase 17A or a later first-run pass.
7. Loop B's empty outcome uses "treatment" in the course-design register.
   Owner: Phase 16C.

None of the seven is a correctness defect and none is blocking. All seven are
copy or hierarchy judgments, which is what this checkpoint exists to surface.

## Signature

Claude, as an agent, under Weibao's standing delegation of 2026-08-28.
Not Weibao's own signature.
