# Course shell template, v0 (tentative)

Date: 2026-08-26
Status: **tentative proposal.** Not an accepted product clause. Derived from
`.planning/research/2026-08-26-navigate2-teardown.md`, which is the evidence.
Binding scope remains `.planning/SOURCE-TO-COURSE.md`.

Purpose: give itembank a way to hold **more than one course at once**, so EMT,
Math 1400, CSCI 1100 and whatever comes next sit in one workspace with one
runtime, one scorer, one evidence store. Navigate2 is the first specimen. It is
a starting template to beat, not a model to imitate; the intent is to keep
studying other learning programs and to raise this template each time.

## 0. Why a template at all

Today itembank has banks, sessions, lessons and a `day` cockpit, but no durable
object that says "this is a course, these are its parts, here is where the
learner is in it". Every additional subject currently costs bespoke wiring.
The shell is the missing container.

## 1. The three levels

Navigate2's one defensible structural idea, kept:

```
workspace          all courses the learner owns
  └── course       EMT, Math 1400, CSCI 1100, ...
        └── unit   chapter, module, week, topic
              └── treatment   one thing to actually do
```

Deliberately only three levels below the workspace. The 2026-08-13 vision entry
asks for deeper nesting (field > subject > subcourse > concept). That is
recorded and NOT resolved here; see section 7. v0 ships three and is designed so
`unit` can nest later without breaking existing courses.

## 2. Durable objects

Per the CLAUDE.md rule that every feature names its actor, source of truth,
authority and recovery:

| Object | Source of truth | Authority | Derived? |
|--------|-----------------|-----------|----------|
| workspace index | `courses.md` at the workspace root | learner | no |
| course | `<course>/course.md` manifest | course builder | no |
| unit | a section in `course.md` | course builder | no |
| treatment | a row in a unit, pointing at an artifact | course builder | no |
| artifact | the bank, lesson, or source file itself | existing contracts | no |
| progress / mastery | evidence store | **runtime only** | **yes, disposable** |
| course card, outline, next-actions | rendered view | none | **yes, disposable** |

The manifest is plain Markdown so it stays readable and editable in Obsidian,
per the existing dual-form rule. Progress is never written into it.

## 3. Treatment purposes, and the evidence contract per purpose

The closed set. Purpose decides the icon, the colour, AND what evidence the
runtime will accept from it. This is the correction to Navigate2, where eight of
nine activities emitted nothing and the shell still showed `Progress: 0 / 9`.

| Purpose | Typical artifact | Evidence emitted | Counts toward mastery |
|---------|------------------|------------------|-----------------------|
| `orient` | objective card, unit map | viewed only | no |
| `read` | source binding, direct reading | `self_report` | no |
| `teach` | lesson with checkpoint items | scored checkpoints | yes |
| `drill` | term bank, Anki export | attempt records | yes |
| `apply` | case / scenario items | scored, advisory mark allowed | yes |
| `check` | blueprint form from the bank | full session evidence | yes |
| `reflect` | learner note, error log | learner-owned | **never** |

Two hard rules, both of them things Navigate2 gets wrong:

1. **A treatment that emits no runtime evidence is labelled as such in the UI**
   and cannot move a mastery number. `orient` and `read` show as done-by-claim,
   visibly distinct from done-by-evidence.
2. **`reflect` never becomes truth.** Direct restatement of the existing rule
   that learner notes never silently become source truth, answer keys, scores,
   or mastery.

There is no `Mark as done` primitive. The nearest thing is `self_report` on a
`read`, and it is typed, dated, and visibly a claim.

## 4. The manifest

Sketch, additive to existing formats, no change to bank parsing:

```markdown
# COURSE: EMT
ID: emt
SOURCE: AAOS Emergency Care and Transportation, 12e
FRAMEWORK: National EMS Education Standards
BLUEPRINT: nremt-emt

## UNIT: Chapter 1 EMS Systems
OBJECTIVES: emt.1.1, emt.1.2, emt.1.3

- orient  Objectives          -> objectives/emt-01.md
- read    Chapter 1           -> sources/aaos12e.md#ch1        pages 4-29
- teach   EMS system roles    -> lessons/emt-01-roles.md
- drill   Chapter 1 terms     -> banks/emt-01-terms.md
- check   Chapter 1 check     -> banks/emt-01.md  blueprint: 10 mc, 2 multi
```

Every row is `purpose  label  -> artifact`. A unit may omit any purpose. That
omission is the point: the treatment-selection rule says direct reading is
sometimes enough, and a uniform nine-slot grid per chapter is precisely the
failure mode observed in the specimen.

## 5. The surfaces

### 5.1 Workspace view, the first page

A card per course. This is the page the learner lands on, so its numbers set
the tone for everything, and the specimen gets them wrong in a way worth
stating precisely.

Navigate2's card shows **one** number, a bar reading `0% complete`. It is an
activity-completion count. Of the 435 activities in the observed course, 394
complete by a self-pressed `Mark as done`, so **90.6% of that denominator is
self-report**. Tick every box, open nothing, and the card reads 100% complete
beside an empty gradebook.

The card therefore shows **three separate quantities that may never be merged
into one bar**:

| Quantity | Means | Source |
|----------|-------|--------|
| `coverage` | units with any accepted treatment, over total units | course manifest |
| `mastery` | objectives with sufficient evidence, over total objectives | evidence store |
| `claimed` | treatments marked done-by-claim, over total claimable | learner claims |

`claimed` is rendered visibly weaker than the other two: it is the learner's
own word, useful for orientation and never mistaken for attainment. If only one
number can be shown at card size, it is `mastery`, because it is the only one
backed by the runtime.

Also on the card, and cheap: subject, unit count, last activity date, and the
next action if one is ready. Not a hero image. The specimen's card devotes most
of its area to a generated hexagon pattern carrying no information.

Filter, search, sort and a card-or-list toggle are worth keeping as-is. That
part of `block_myoverview` is fine and costs nothing to match.

### 5.2 Course view, two panes

- **Next actions**: evidence-driven, prerequisite-aware, short. This is the
  `day` cockpit scoped to one course, and it is the default pane.
- **Browse**: the full unit outline, explicitly labelled a reference index and
  not a plan.

The specimen's left drawer of 41 chapters, each expanding to 9 leaf links, is a
table of contents pretending to be a path. Keeping it as `Browse` is fine.
Letting it be the primary navigation is the mistake.

### 5.3 Reading, a surface of its own

Recorded 2026-08-26 at Weibao's instruction. In the specimen the readings live
inside each chapter as one row among nine, which he judged "good enough for now"
but not the end state, and asked for a better page or tab for reading.

Holding readings inside the unit is correct as the **default placement**: a
reading belongs to the objective it serves, and pulling it out would break the
treatment ladder. What is missing is a **second view over the same bindings**,
not a second home for them. Sketch:

- A `Read` tab listing every `read` treatment across all courses, grouped by
  source rather than by unit, so a book reads as a book.
- Per source: what is bound, what is cited by which objectives, what has been
  read, and what is queued next.
- Coverage of the source itself, distinct from coverage of the course. A
  chapter no objective cites is visible as unbound rather than invisible.
- Opens the source in place. The existing rule that files are linked and edited
  where they live still holds; the reading view binds and never relocates.

This is one view over existing `read` bindings, so it costs a renderer and no
new durable object. It stays open only because of question 2 in section 7: there
is still no evidence event for having read something.

### 5.4 Selection, the one thing the specimen does well

TestPrep's practice-test builder is the strongest artifact in the whole
specimen, and three of its four ideas are already itembank's while the fourth
is a real gap.

**Already ours, and independently confirmed by a shipped commercial NREMT
product.** `Tutorial Mode` versus `Test Mode` is exactly the mode-gated
disclosure the runtime invariant describes, arrived at by a different vendor for
the same reason. `Include Confidence meter`, on by default, confirms the
existing `conf` field is not an eccentricity.

**A real gap: pool depletion.** Every category is shown as unanswered over
total, `Airway and Breathing (115 / 115)`, with the total pool as
`Qbank (690 QUESTIONS)`, `0 Taken, 690 Remaining`. itembank records attempts but
has no notion of how much of a bank the learner has ever seen. That number
answers "am I actually practising, or recycling the same twelve items", and it
belongs beside `coverage` and `mastery` as a third denominator the learner can
inspect.

**A second real gap: error-driven reselection.** The checkbox
`Include questions previously answered incorrectly` composes a form from the
learner's own wrong answers. itembank holds the evidence to do this and has no
selector that uses it.

**One thing to not copy.** The six categories hold exactly 115 items each. That
uniformity is a content-production artifact, not a blueprint: the real NREMT
weights its domains unevenly. Equal pools per category quietly teach the wrong
proportions, so a blueprint in itembank states weights explicitly and the linter
should notice when a bank's category counts are suspiciously flat.

## 6. Degraded and offline behaviour

Unchanged from the standing rule: the shell must render, and every `read`,
`drill`, `apply` and `check` must run, with the network unplugged. Only
model-assisted `teach` and next-action ranking may go quiet. A course whose
source is a remote binding shows the binding as unavailable rather than hiding
the unit.

## 7. Open questions, carried not answered

1. **Depth.** The 2026-08-13 vision asks for field > subject > subcourse >
   concept and for "completing a field". v0 ships three levels. What counts as a
   field, and what completion of one means, is unresolved and needs ideaboarding.
2. **Evidence event for a non-scored treatment.** No type exists today for
   "read this". `self_report` needs an honesty story before it ships.
3. **Surface or mode.** Is the course view a new surface, or a mode of `day`?
4. **Where the manifest lives** relative to banks and to an Obsidian vault, and
   how discovery binds it without mutating anything.
5. **Cross-course scheduling.** `day` already spans subjects. Does the workspace
   view compete with it, or feed it?
6. **Pool depletion needs a definition.** "Seen" is not "attempted" is not
   "mastered", and a shuffled variant of an item is not a new item. Before a
   remaining-count can be shown it has to say what it counts.
7. **Does the reading view need its own progress model** or does it borrow the
   same `self_report` answer as question 2? Probably the latter, unverified.

## 8. How this template is meant to improve

Explicitly a v0 to be beaten. Each further learning program studied gets a
teardown note in `.planning/research/` on the pattern of the Navigate2 one:
observed structure as fact, implementation as fact, interpretation kept
separate, proposals marked as recommendations, and a rights note. Ideas that
lose stay in `IDEA-LEDGER.md` with the reason, per the append-only rule.

Candidate next specimens, in rough order of expected yield: Brilliant (guided
teaching), Albert (practice and blueprint reporting), Anki and its scheduler,
Khan Academy (mastery model and prerequisite graph), Duolingo (path and streak
mechanics), edX or Coursera (multi-course workspace at scale).

## 9. Rights note

Nothing from the specimen is vendored. Moodle core is GPLv3 and the `navigatexl`
theme and JB Learning branding are not ours; the observed design tokens are
stock Boost defaults and were used only to confirm that nothing bespoke exists
worth copying. This template is clean-room derived from the information
architecture, which is an idea rather than an expression. Raw capture is kept
outside the repository.

The TestPrep pass on 2026-08-26 was read-only in the same sense: the
practice-test dialog was opened to record its options and cancelled without
creating a test, no assessment was started, and no item text was viewed or
captured. The 690-item Qbank remains untouched at `0 Taken`.
