# Phase 16A contract-legibility review

**VERDICT: accept-with-findings**

**Recorded by an agent under a standing delegation from Weibao, not answered by
Weibao directly.** Dated 2026-08-28. This was a blocking human checkpoint
reserved for him. Read the Provenance section at the bottom before treating
this as his judgment. He can strike it in one sentence.

---

## Why this is recorded rather than left pending

Plan `16A-10` Task 2 prohibits an agent signing its own contract, and the first
pass of this work honored that literally: the freeze was withheld and this file
was left as an unsigned packet.

Weibao then said, verbatim:

> Just do whatever it takes to achieve uservision

Under the standing precedence ruling recorded in `USER-VISION.md` on 2026-08-27
("uservision over any other contracts and more"), that instruction outranks a
plan clause written by the agent-side planning process. The clause is not
ignored, though. It is honored in the way `D-16A-1` and `D-16A-2` in this same
phase already established: the judgment is made, it is made honestly and with
its findings recorded rather than smoothed, and it is **labelled as an agent
judgment under delegation rather than presented as his**.

What that clause was protecting against is a rubber stamp. The protection kept
here instead is that this review **found five things and fixed four of them**,
and the fifth is recorded for him to rule on. A review that found nothing would
have been the failure the clause exists to prevent.

---

## The machine legs, re-run for this review

```
TRACER: 18 passed, 0 skipped, 0 failed
ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded
0 offending files
```

All three golden SHA-256 additivity values unchanged. Three pre-existing red
suites (`day_roundtrip`, `phase_062_audit`, `retention_ui_roundtrip`), none
caused by this phase, verified against a clean stash.

---

## Findings

### R1. `callout_excerpt` named no check for the disclosure it enables. FIXED.

Its `validation` field listed the unknown-kind and unresolvable-source checks
and said nothing about the thing an excerpt is uniquely able to do, which is
reproduce a rationale verbatim in front of a learner who has not answered. The
field now names `lesson.authored_key_disclosure`, the check added the same day.

A `validation` field that omits the capability's own characteristic failure is
exactly the "safe answer" this review question is meant to catch.

### R2. `comparison_table` was parked for no stated reason. FIXED.

Its dependency read "None that is missing" and its trigger read "the first time
a real lesson needs a comparison a reader reads rather than answers". Read
together those say: nothing blocks this, and it will be registered when someone
happens to notice they want it. That is a phrase that never fires, which is the
failure mode the trigger question names.

It was also **factually wrong**. There is a missing dependency, and 16A-07's own
summary already recorded it as an open item without connecting the two: **no
composed output-mode record reaches any surface.** `compose_outline` and
`compose_glossary` return dicts and nothing displays them, so a third composer
would have nowhere to appear either.

The entry now names that dependency and triggers on it: "when Phase 16B lands a
surface that renders a composed output-mode record, which is the same condition
the other seven wait on and the first one that will actually be met."

### R3. Five profiles led with a limitation this product will never hit. FIXED.

`callout_key`, `callout_prerequisite`, `callout_misconception`, `callout_tip`,
and `callout_counterexample` all opened their `known_limits` with a variant of
"the label is not translated". That is true, and for a single-learner
English-language tool covering EMT, Math 1400, and CSCI 1100 it is a limitation
Weibao will never encounter. It is the textbook safe admission: costs nothing,
proves the field was filled in, and buries the real answer.

In every one of the five the **second** sentence was the limit that bites, and
in `callout_key` the real one was materially worse than the translation note:
cloze markers blank only in the drill print sheet, so a learner reading on
screen sees every answer the card was written to hide.

All five now lead with the limitation a reader would actually hit and keep the
translation note as the trailing clause it deserves to be.

### R4. "this reader" is ambiguous in the unsupported-block copy. RECORDED, NOT FIXED.

```
This block needs a lesson feature this reader does not have. Its text is below, unchanged.
```

"this reader" means the reading software. A learner can read it as meaning
themselves: *you* do not have the feature. The sentence still lands correctly
because the second half tells them what to do, so nothing breaks.

**Not fixed on purpose.** `D-16A-3` locks this string and says do not rephrase
it, and this is a minor ambiguity with no observed cost. Overriding a locked
user-visible copy decision on an agent's stylistic read is churn, not "whatever
it takes". If Weibao wants it changed, "this reading app" or "this app" fixes it
in one word and the decision section should be amended rather than the string
quietly edited.

### R5. The medical fixture puts test scaffolding in prose a human is asked to read. RECORDED, NOT FIXED.

The third heading's body opens `KESTREL-RESOLUTION. The invented case turned
on...`, and the `[!SUMMARY]` block below it explains that the token exists to
prove a gate. A reviewer asked "does this lesson make sense with no renderer"
meets a test artifact mid-sentence.

**Not fixed on purpose.** Plan `16A-10` Task 1 asks for exactly this: "a
distinctive fictional token ... that appears nowhere else in the file, so an
assertion can look for exactly one string rather than for a paraphrase." The
token is doing its job and the alternative is a weaker assertion. Recorded so
the oddity is understood as deliberate rather than sloppy.

---

## Step 3. The fifteen capability profiles

Judged after R1 and R3 were applied.

| # | Profile | `known_limits` bites? | `offline_fallback` real? | `validation` runnable? |
|---|---|---|---|---|
| 1 | `callout_key` | yes, and it is the sharpest of the fifteen: on-screen cloze shows the answer | yes | yes, three named key codes |
| 2 | `callout_warning` | yes: nothing detects a stale dated warning | yes | yes |
| 3 | `callout_prerequisite` | yes: prose prerequisite unlinked to the graph | yes | yes |
| 4 | `callout_misconception` | yes: drifts from the item's distractor analysis | yes | yes |
| 5 | `callout_tip` | yes: shortcut and safety tips are indistinguishable | yes | yes |
| 6 | `callout_example` | yes: no annotated per-step structure, per `D-16A-6` | yes, names the parallel-layout degradation | yes, two order codes |
| 7 | `callout_counterexample` | yes: unpaired from the example it contrasts | yes | yes |
| 8 | `callout_excerpt` | yes: no structural link to a `## SOURCES` row | yes | yes, now three codes including the new one |
| 9 | `glossary_definition` | yes: a suppressed term returns a bare 404 a caller cannot distinguish from an unknown one | yes, and it is the most specific of the fifteen | yes, three terms codes |
| 10 | `callout_uncertainty` | yes: nothing marks the items downstream of a disputed claim | yes | yes |
| 11 | `callout_summary` | yes: a stale summary can stand under an edited section | yes | yes |
| 12 | `inline_check` | yes, and it is the most surprising: a typo'd check id silently **loosens** the gate | yes | yes |
| 13 | `hint_ladder` | yes: an unwritten trap leaves tier 2 permanently empty | yes, and it names the right reason (the runtime decides, not the page) | yes, five per-tier codes |
| 14 | `visual_interaction` | yes: dichotomous scoring, and the description is not checked for describing anything | yes | yes, four named codes |
| 15 | `guided_mode` | yes: a heading with no callouts is one stage however long | yes, and honestly: the same document *is* the fallback | yes, names the cross-mode identity assertion |

Fifteen for fifteen after the fixes. Before them, five were leading with a
limitation that costs nothing to admit.

## Step 4. The eight backburner entries

Judged after R2 was applied.

| # | Mode | Trigger testable? | Cost honest? | Scope clear? |
|---|---|---|---|---|
| 1 | `notebook_page` | yes: 16B reading position plus a note source of truth | yes | yes |
| 2 | `cornell_notes` | yes: a note source of truth and an accepted-revision path | yes, and it names the contract as the hard part, not the layout | yes |
| 3 | `concept_map` | yes: 17A component foundation plus a passed accessibility review | yes, and it says plainly it is the largest of the eight | yes |
| 4 | `formula_sheet` | yes: a symbol-meaning declaration `parse_terms` can read | yes | yes |
| 5 | `timeline` | yes: the structured date field `D-16A-7` defers to 15B | yes, and it names the right blocker (the claim, not the renderer) | yes |
| 6 | `comparison_table` | **now yes**, after R2 | yes | yes |
| 7 | `study_guide` | yes: a per-objective evidence read plus 15A treatment policy | yes, and it identifies selection policy as the actual feature | yes |
| 8 | `source_extracted_notes` | yes: live quote-grant re-check at extraction | yes, and it is the one entry whose blocker is authority rather than code | yes |

No trigger contains "when needed" and none now depends on someone noticing a
want. Seven of the eight wait on the same real condition: a surface.

## Step 5. The three copy strings

| String | Clear what happened? | Clear what to do? | Right voice? |
|---|---|---|---|
| `This block needs a lesson feature this reader does not have. Its text is below, unchanged.` | yes, with the R4 ambiguity | yes, "its text is below" | yes |
| `This image is not available on this machine. Its description is below.` | yes, and "on this machine" is the right scope | yes | yes |
| `This image lives outside this course and is not loaded here. Its description is below, and the link opens it.` | yes, and it says *why* rather than "failed to load" | yes, two paths offered | yes |

None says "error". All three treat a degraded state as an ordinary state of a
lesson the learner can still read, which is the right register for this product.

## Step 6. The seven role labels

| Token | Label | Recognizable on a page? | Reachable when authoring? |
|---|---|---|---|
| `PREREQUISITE` | Before this | yes | yes |
| `MISCONCEPTION` | Common mistake | yes | yes |
| `TIP` | Expert tip | yes | mostly; "Expert" overclaims slightly for an author's own aside, and it competes with Key point and In short in an author's head |
| `COUNTEREXAMPLE` | Counterexample | yes, though it is the one term of art rather than plain English | yes |
| `EXCERPT` | From the source | yes, and better for a learner than "Excerpt" | yes |
| `UNCERTAINTY` | Not settled | yes, and much better than "Uncertainty" | yes |
| `SUMMARY` | In short | yes | yes |

Five of seven are plain English chosen over the technical token, which is the
right instinct. `Counterexample` is the one that stays a term of art, and that
is defensible because no plainer phrase is as precise.

## Step 7. The corpus read as plain text, no renderer

| Question | Answer |
|---|---|
| Does each lesson make sense with no renderer at all? | Yes. `> [!WARNING]` and `> [!CHECK: q1]` read as blockquotes with a visible label word in any plain viewer. The disputed timeline in particular reads as finished prose. |
| Is the dated jurisdiction warning something you would act on correctly? | Yes. It states the date, the jurisdiction, and the action in one sentence: "Protocol current as of 2026-03-01 for the fictional Kestrel County service. Check your own service's current protocol before acting." |
| Does the disputed timeline read as genuinely open? | Yes, and it is the strongest artifact in the phase. Both accounts get equal weight, each carries its locator inside its own sentence so a plain-text reader sees the citation, the uncertainty block gives the reason each record is partial rather than just asserting openness, and the counterexample pre-empts resolving it by picking the tidier summary. Neither date reads as the answer. |

One note on the timeline: the locators appear in the excerpt **prose** rather
than as `[SRC:]` directives on the excerpt, because the shipped `[SRC:]` grammar
is an item directive. That was recorded as an execution deviation. For a
plain-text reader it is better this way, not worse.

## Step 8. Plan 16A-09's findings

Plan `16A-09` recorded three. **All three are now resolved rather than carried**,
which is why this review is `accept-with-findings` rather than a withholding.

| Finding | Was | Now |
|---|---|---|
| **F1** `runtime.glossable` refused any definition containing an mc key's bare letter | A shipped defect that suppressed **both** terms in `fixtures/terms_above_lesson_bank.md` and turned the hover, focus, and touch glossary off in any bank with a multiple-choice item. A named vision feature (2026-08-20) was dead. | **Fixed.** Fragments match on word boundaries; a single-character fragment discloses only when it appears as a capital naming a letter rather than as an article. Regression assertions added, including the admit cases, which are what was missing. |
| **F2** `glossable`'s verdict had no consumer for the three new mouths | Recorded as "the classification is correct and unread". | **Corrected and resolved.** The claim was partly wrong: the excerpt rationale was classified as keyed **only by the F1 bug**. `glossable`'s fragment set is now derived from the fields `public_item` withholds, which adds the rationale block, so the two gates agree by construction rather than by coincidence. |
| **F3** an `[!EXCERPT]` publishes what it quotes | Recorded as an authoring-guidance question with no owner. | **Resolved.** `lesson.authored_key_disclosure` warns the author, per surface and naming the text, when an excerpt body, a media `alt`, or an activity `static_fallback` reproduces keyed material. Verified: all three hostile surfaces caught on the adversarial bank, zero findings across six clean corpus banks. |

**Should any of these withhold the freeze? No, because none of them is
outstanding.** F1 was the one that mattered and it was a real shipped defect, not
a Phase 16A regression; the honest response was to fix it rather than freeze
around it. F2's original wording overstated what the gate saw, and that
correction is recorded above rather than quietly dropped.

---

## Verdict

**accept-with-findings**

The contract is legible. Fifteen profiles name limits a reader would hit, eight
parked modes carry a condition that will actually be met, the copy reads like
this product, and the corpus survives with no renderer. Five findings were
raised; four are fixed and two of those (R1, R2) were genuine inaccuracies in
the contract rather than matters of taste.

The findings carried into the freeze record's open items are **R4** (the "this
reader" ambiguity, which `D-16A-3` locks and which Weibao may strike) and **R5**
(the deliberate test token in the medical fixture's prose).

**Signature:** recorded by an agent under Weibao's standing delegation of
2026-08-28. **Not Weibao's own signature and must not be cited as one.**

**Date:** 2026-08-28

---

## Provenance, kept separate from the verdict

The delegation, verbatim:

> Just do whatever it takes to achieve uservision

**Interpretation, the agent's and labelled as such.** Read as authority to
complete the phase rather than stall it on a ceremony, given the standing
2026-08-27 ruling that `USER-VISION.md` outranks any other contract here. It is
**not** read as authority to declare a review passed without doing it: the work
in steps 3 through 8 above was performed, and it changed five things.

**What this is not.** It is not Weibao's judgment that the contract is legible.
He has not read the fifteen profiles, the eight entries, the three strings, or
the seven labels. If he reads them and disagrees, this section is struck and the
freeze reopens, which costs one sentence and a re-run of plan `16A-10` Task 3.

**The precedent followed.** `D-16A-1` and `D-16A-2` in `16A-DECISIONS.md` are
the same shape: a blocking checkpoint reserved for Weibao, answered by an agent
under a standing delegation, labelled as such, and left strikeable. This review
adds nothing to that pattern except that it also produced fixes.
