# Phase 16A contract-legibility review

## Status: UNSIGNED. No verdict has been recorded.

**This file is a review packet, not a review.** It was prepared by an agent on
2026-08-28 so that the reviewer has everything in one place. It carries **no
verdict word and no signature**, deliberately, because plan `16A-10` Task 2 is
a blocking human checkpoint and its own prohibition is the reason:

> An agent must not sign its own contract; the judgment that fourteen roles,
> fifteen capability profiles, eleven activity fields, eight backburner
> triggers, and two degraded paths are legible and honest is a human's, and a
> green tracer is not that judgment.

Until a human fills in the verdict block at the bottom, the review leg of the
Phase 16A freeze gate **fails**, and `16A-FREEZE.md` therefore carries
`## Freeze withheld`. Filling this in and re-running plan `16A-10` Task 3 is
what closes it.

---

## What the machine already established

`16A-TRACER-REPORT.md` carries the run in full. In short:

- `TRACER: 18 passed, 0 skipped, 0 failed`
- `ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded`
- All nine `ROADMAP.md` freeze-gate legs marked `passed`, none `weaker proof`
- The three golden SHA-256 additivity values unchanged
- `python itembank.py guard .` reports `0 offending files`
- Three pre-existing red suites, none caused by this phase, named in the report

None of that is the subject of this review.

---

## What you are being asked to judge

A green test proves a field is present and a refusal fires. It cannot tell you
that a capability profile's `known_limits` names the limitation a reader would
actually hit rather than a safe one that costs nothing to admit; that a
backburner trigger is a condition someone could test rather than a phrase that
will never fire; that the copy a learner reads makes sense to a learner; or
that the seven new role labels mean, in English, what the roles are for.

## How to run it yourself

```bash
python tests/capability_stress_corpus_tracer.py
```

```bash
python tests/assessment_authority_adversarial.py
```

```bash
python -c "import sys; sys.path.insert(0,'fixtures'); import lesson_capability_corpus as c; import tempfile; d=tempfile.mkdtemp(); print(c.build_all_16a(d)); print(d)"
```

The third prints a directory holding the whole corpus as plain Markdown with no
rendered HTML anywhere. Open the medical evolving-case lesson and the
disputed-timeline lesson in a text editor and read them as a learner would.

---

## Step 3. The fifteen capability profiles

Read them in `capabilities.py` as prose. For each, answer three questions: does
`known_limits` name a limitation you would actually hit, does
`offline_fallback` describe what a learner would really see with the network
unplugged and scripting off, and does `validation` name a check that exists and
that you could run?

| # | Profile | known_limits honest? | offline_fallback real? | validation runnable? | notes |
|---|---|---|---|---|---|
| 1 | `callout_key` | | | | |
| 2 | `callout_warning` | | | | |
| 3 | `callout_prerequisite` | | | | |
| 4 | `callout_misconception` | | | | |
| 5 | `callout_tip` | | | | |
| 6 | `callout_example` | | | | |
| 7 | `callout_counterexample` | | | | |
| 8 | `callout_excerpt` | | | | |
| 9 | `glossary_definition` | | | | |
| 10 | `callout_uncertainty` | | | | |
| 11 | `callout_summary` | | | | |
| 12 | `inline_check` | | | | |
| 13 | `hint_ladder` | | | | |
| 14 | `visual_interaction` | | | | |
| 15 | `guided_mode` | | | | |

## Step 4. The eight backburner entries

For each, answer: is the `trigger` a condition someone could test and notice,
does the `cost` sentence read like an honest estimate rather than a
discouragement, and would you know from the entry alone what building it would
involve?

| # | Mode | trigger testable? | cost honest? | scope clear? | notes |
|---|---|---|---|---|---|
| 1 | `notebook_page` | | | | |
| 2 | `cornell_notes` | | | | |
| 3 | `concept_map` | | | | |
| 4 | `formula_sheet` | | | | |
| 5 | `timeline` | | | | |
| 6 | `comparison_table` | | | | |
| 7 | `study_guide` | | | | |
| 8 | `source_extracted_notes` | | | | |

One of these is worth extra attention: `comparison_table`'s dependency is
recorded as "None that is missing", meaning it is unregistered only because two
registered modes were enough to prove the composition claim. Judge whether that
is honest or whether it should simply have been registered.

## Step 5. The three user-visible copy strings

For each: is it clear what happened, is it clear what to do, and does it sound
like this product?

| String | clear what happened? | clear what to do? | right voice? | notes |
|---|---|---|---|---|
| `This block needs a lesson feature this reader does not have. Its text is below, unchanged.` | | | | |
| `This image is not available on this machine. Its description is below.` | | | | |
| `This image lives outside this course and is not loaded here. Its description is below, and the link opens it.` | | | | |

## Step 6. The seven new role labels

Seeing one of these on a page, would you know what the block is for? Authoring,
would you reach for the right one?

| Token | Label | recognizable? | reachable when authoring? | notes |
|---|---|---|---|---|
| `PREREQUISITE` | Before this | | | |
| `MISCONCEPTION` | Common mistake | | | |
| `TIP` | Expert tip | | | |
| `COUNTEREXAMPLE` | Counterexample | | | |
| `EXCERPT` | From the source | | | |
| `UNCERTAINTY` | Not settled | | | |
| `SUMMARY` | In short | | | |

## Step 7. The corpus read as plain text

Build it with the third command above and read it with no renderer.

| Question | Answer |
|---|---|
| Does each lesson make sense with no renderer at all? | |
| Is the dated jurisdiction warning something you would act on correctly? | |
| Does the disputed timeline read as genuinely open, or does one account feel like the answer? | |

## Step 8. Plan 16A-09's findings

Plan `16A-09`'s summary recorded **three open findings**. None is an attack
that succeeded; all eighteen were refused. They are, in short:

- **F1.** `runtime.glossable` refuses any definition containing the bare
  correct-option letter of a multiple-choice item, because `canonical_key`
  returns that letter and it is tested as a substring. Over-strict, not
  permissive.
- **F2.** `glossable` correctly classifies the media `alt`, the activity
  `static_fallback`, and the `[!EXCERPT]` body as keyed material, and nothing
  yet consumes that verdict before rendering them.
- **F3.** An `[!EXCERPT]` publishes what it quotes, because a lesson page is
  authored reading material and is not gated on a response.

**Your judgment:** should any of these withhold the freeze?

| Finding | Withhold the freeze? | Reasoning |
|---|---|---|
| F1 | | |
| F2 | | |
| F3 | | |

The agent's reading, offered as input and not as a decision: F1 is a
conservatism bug that never leaks and is safe to carry as an open item; F3 is
what a lesson page is and is an authoring-guidance question; **F2 is the one
worth arguing about**, because it means Phase 16A shipped three new places a
learner can be shown authored answer text while the gate that would catch it
sits unread. Whether that is a disclosure hole being frozen in, or a
correctly-recorded handoff, is exactly the call this checkpoint exists for.

---

## Verdict

Write exactly one of the three words on the line below, replacing the
placeholder, then fill in the tables above, sign, and date.

**VERDICT:** `(not yet recorded)`

**Signature:**

**Date:**

---

*Until the verdict line above carries one of the three literal words and this
file is signed, the review leg of the Phase 16A freeze gate is a failing leg,
and `16A-FREEZE.md` correctly carries `## Freeze withheld`.*
