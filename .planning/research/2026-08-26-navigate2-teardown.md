# Navigate2 teardown, and what itembank should take from it

Date: 2026-08-26
Method: logged-in walkthrough of `navigate2.jblearning.com` in the learner's own
browser, read-only. No scraping of item content, no bank extraction, no writes.
Course observed: Premier Access for Emergency Care and Transportation of the
Sick and Injured, 12e (Andrews-B6E335), course id 158269.

Status: **observation and interpretation**. Nothing here is an accepted product
clause. Design proposals in section 4 are recommendations only.

## 1. Observed structure (fact)

Three levels, nothing deeper:

```
My courses (card grid, filter / search / sort / card-or-list toggle)
  └── Course (section outline + persistent left section drawer)
        ├── 4 course-level sections
        │     TestPrep                          1 activity
        │     Soft-Skill Simulations            1 activity
        │     Virtual Mentor Lecture Videos    13 activities
        │     Virtual Ride-Along Videos        17 activities
        └── 41 chapter sections, each 9 or 11 activities
```

Every chapter repeats the same nine-slot template, in this fixed order:

| # | Activity | Blurb shown | Role |
|---|----------|-------------|------|
| 1 | Learning Objectives | "View the key points presented in this lesson." | orient |
| 2 | eBook | "Read and interact with the chapter on X." | source reading |
| 3 | Interactive Lecture | "Learn at your own convenience and pace." | guided teaching |
| 4 | Flashcards | "Test your knowledge of key terms." | term recall |
| 5 | Audiobook | "Listen to your reading assignments." | alternate modality |
| 6 | Slides | "Review your comprehension of key concepts." | condensed review |
| 7 | Lecture Outline | (skeleton notes) | note scaffold |
| 8 | Case Studies | (applied scenario) | transfer |
| 9 | Assessment in Action | "Apply what you have learned." | applied check |

Chapters with 11 activities add two more of the same kinds. Course-level
progress is reported per section as `Progress: 0 / N`.

## 2. Observed implementation (fact)

The shell is Moodle. Almost nothing is native to it:

- `Learning Objectives`, `eBook` are `mod/ebooklti` LTI launches. The activity
  page says "Your activity has opened in a new window" and offers one link.
- `Assessment in Action` is `mod/url`. Literally a link out. Body text is
  "Click on Assessment in Action: Chapter 1 to open the resource."
- `Interactive Lecture` is a SCORM package.
- Completion for everything except SCORM is a manual **Mark as done** button the
  learner presses. It is self-report, not evidence.

The gradebook confirms this. `grade/report/user/index.php?id=158269` lists
exactly 42 grade items: 41 SCORM `Interactive Lecture: Chapter N` rows, all
`( Empty )` and `0.00 %` weight, plus one `NREMT Practice Assessment:
Technology Enhanced Items (EMT)`. Course total is `-`.

## 2b. Code-level capture (fact, added 2026-08-26 second pass)

Raw capture kept out of the repository at
`scratchpad/nav2/capture-2026-08-26.md`. Structure only: no item content, no
eBook text, no TestPrep questions, and no vendor CSS or JS was copied.

- Platform is **Moodle 4.x** with theme `navigatexl`, a Boost child theme, and
  Bootstrap 5 utility classes throughout. Font is Roboto, body 15px.
- The `:root` design tokens are **stock Moodle Boost defaults**: `--primary
  #0f47ad`, `--success #64a44e`, `--info #008196`, `--warning #f0ad4e`,
  `--danger #ca3120`, breakpoints 576 / 768 / 992 / 1200. Nothing bespoke.
- The `My courses` page is unmodified core `block_myoverview`: a filter row
  (All / search / sort / card-or-list) over a paged Bootstrap card grid.
- The chapter section page confirms the module types. Of the nine activities,
  **seven are `modtype_url`**, plain outbound links. One is `modtype_ebooklti`,
  one is `modtype_scorm`. All nine complete via a self-pressed `Mark as done`.

**Colour caveat.** The learner's browser runs Dark Reader. Computed styles read
back as a dark card on a light body with light text, which is the extension
inverting a light theme. Screenshots from the first pass are not the real
palette and no colour decision should be taken from them.

**One mechanism genuinely worth taking.** Moodle 4.x defines six *activity
purpose* tokens, `--activityadministration`, `--activityassessment`,
`--activitycollaboration`, `--activitycommunication`, `--activitycontent`,
`--activityinteractivecontent`, and tints each activity icon by purpose so a
learner can read the pedagogical role of a row at a glance, course-wide.
Navigate2 inherits the mechanism and **does not use it**: every one of the nine
chapter activities carries an empty `purpose`. The idea is good, the execution
is absent, and itembank should take the idea. See section 4.3.

**Licensing read.** Moodle core and `block_myoverview` are GPLv3. The
`navigatexl` theme and JB Learning branding are not ours. But nothing here is
worth vendoring in any case: the tokens are stock Boost, the markup is
Bootstrap cards, and the entire value is the information architecture, which is
an idea rather than an expression. The template itembank builds is therefore
**clean-room derived**, not a copied theme.


## 2c. The completeness number, and what it is made of (fact + arithmetic)

Added 2026-08-26 third pass, prompted by the workspace card screenshot.

The `My courses` card carries a progress bar reading **`0% complete`**. The
course landing page carries the same quantity per section as
`Activities: N` / `Progress: 0 / N`, confirmed by reading the section summary
nodes directly. Both are Moodle **activity completion** counts. Neither is a
grade, and neither consults the gradebook.

Counting the observed course:

| | Activities |
|---|---|
| 17 chapters at 11 | 187 |
| 24 chapters at 9 | 216 |
| 4 course-level sections (1 + 1 + 13 + 17) | 32 |
| **Total** | **435** |
| Of which carry a grade item (SCORM Interactive Lecture) | 41 |
| Of which complete only by a self-pressed `Mark as done` | **394** |

So **90.6% of the denominator behind the headline completeness number is
self-report.** A learner who opens nothing and ticks every box reaches 100%
complete with an empty gradebook. That is not a subtle flaw in the progress
model; it is the progress model.

## 2d. TestPrep is a second, disconnected evidence store (fact)

`testprep.jblearning.com` is a **separate application** on a separate domain
with separate branding, reached from Moodle by an outbound link. Its home
screen, `TestPrep/Home/MyHome`, is the real assessment engine, and it is far
better designed than the shell that links to it.

**Two test kinds, different authority.**
- `CREATE NEW PRACTICE TEST` plus `REVIEW PRACTICE TESTS`, learner-composed.
- `COMPLETE ASSESSMENT TEST(1)` plus `REVIEW MY ASSESSMENT TESTS`, assigned.

**Its own performance store**, headed `Review My Performance`:
- `Completed`: 0 Assessment, 0 Practice, 0 Questions.
- `Last Assessment`: 0 Correct, 0 Incorrect.
- `Qbank (690 QUESTIONS)`: `0 Taken, 690 Remaining`.

**The practice-test builder**, captured verbatim from the dialog:
- `Assessment Settings`: **Tutorial Mode** or **Test Mode**.
- `Timer`: On or Off.
- `Include Confidence meter`, **checked by default**.
- `CHOOSE QUESTIONS FROM THESE SUBJECTS`, each shown as unanswered over total:
  All subjects 690/690, Airway and Breathing 115/115, Cardiology 115/115,
  Medical 115/115, Obstetrics and Pediatrics 115/115, Operations 115/115,
  Trauma 115/115.
- Explanatory note, verbatim: the numbers after each subject represent the
  questions the user has not yet answered versus the total in that category.
- `Include questions previously answered incorrectly`, a checkbox.
- The submit button carries a live count: `CREATE TEST(0 QUESTIONS)`.

No test was created and no assessment was started; the dialog was cancelled.
No item text was viewed or captured.

**The silo.** TestPrep knows taken, remaining, correct, incorrect, confidence
and per-subject depletion. Moodle's gradebook knows 41 empty SCORM rows. Neither
knows what the other knows, and the learner's actual evidence is split across
two products that cannot see each other. This is precisely the failure the
one-runtime-one-scorer-one-evidence-store invariant exists to prevent, observed
in the wild.


## 3. Interpretation

The **template is the product**. The nine-slot chapter contract is the genuinely
good idea: every objective gets orient, read, teach, drill, review, apply, and
check, in a predictable order, so the learner never has to decide what to do
next. That is exactly the "choose the right treatment per objective" problem in
`SOURCE-TO-COURSE.md`, solved by fiat rather than by evidence.

The **plumbing is the anti-pattern**, and it is the anti-pattern itembank
already legislated against:

- Nine activities per chapter, and eight of them produce no evidence. Reading,
  flashcards, case studies, and the applied check are all invisible to the
  gradebook. `Mark as done` is presentation state being mistaken for evidence,
  which the CLAUDE.md rule "Presentation state never grants authorization"
  forbids.
- Every activity is a separate vendor tool behind an LTI or SCORM boundary, so
  there is no single scorer and no single evidence store. Scoring authority is
  scattered across products that cannot see each other.
- The template is uniform rather than adaptive. Chapter 1 and Chapter 29 get the
  same nine slots regardless of difficulty, prerequisite depth, or how the
  learner actually performed. There is no path revision from evidence.
- Nothing is learner-owned or exportable. Close the browser and the course is
  gone.

Put bluntly: Navigate2 is a good curriculum shape wrapped around no runtime.
itembank is a real runtime that has not yet committed to a curriculum shape.
They are complementary halves.

## 4. Proposal for itembank (recommendation, not accepted)

### 4.1 Take the treatment template, make it evidence-bearing

Adopt a per-objective treatment ladder modelled on the nine slots, but define
each rung by what evidence it emits rather than by which vendor tool it opens:

| Rung | itembank artifact | Evidence emitted |
|------|-------------------|------------------|
| Orient | objective card with citations | viewed, no score |
| Read | source binding, direct reading | read-through with dwell, self-report allowed but labelled `self_report` |
| Teach | lesson (`lesson-authoring`) | checkpoint items inside the lesson, scored by the one scorer |
| Drill | term bank, Anki export | attempt records |
| Review | condensed lesson view | derived, no new evidence |
| Apply | case-style `short` or `table` items | scored, advisory mark allowed |
| Check | blueprint-selected form from the bank | full session evidence |

The rule that makes this different from Navigate2: **a rung that emits no
evidence must be visibly labelled as emitting no evidence**, and must never
contribute to a mastery or progress number. `Progress: 0 / 9` counting a
self-pressed checkbox is the exact failure to avoid.

### 4.2 Take the three-level navigation, drop the drawer-of-41

`My courses` grid → course section outline → activity, with prev/next/jump
between activities, is a sound and cheap shape. It maps onto the existing `day`
cockpit as a third surface.

But the left drawer listing all 41 chapters, each expanding to 9 or 11 leaf
links, is a table of contents pretending to be a plan. itembank already has a
better answer: the `day` cockpit says what to do today. Recommendation is a
**two-pane course view**: a "next actions" pane driven by evidence and the
prerequisite map, and a "browse everything" pane that is explicitly a reference
index, not a path.

### 4.3 Take the activity-purpose taxonomy, and actually use it

Moodle defines six activity purposes and Navigate2 leaves them blank. itembank
should define its own small, closed set and make it load-bearing rather than
decorative, because the purpose is exactly what decides whether a rung emits
evidence:

| Purpose | Example treatments | Emits evidence |
|---------|--------------------|----------------|
| `orient` | objective card, chapter map | no, and says so |
| `read` | source binding, direct reading | `self_report` only |
| `teach` | lesson with checkpoints | yes, scored |
| `drill` | term bank, flashcard export | yes, attempts |
| `apply` | case items, scenarios | yes, scored |
| `check` | blueprint form from the bank | yes, full session |
| `reflect` | learner note, error log | learner-owned, never mastery |

The colour and icon follow the purpose, so the learner reads the row's role
before reading its title. More importantly the **evidence contract follows the
purpose too**, which is the thing Navigate2 never wired up.


### 4.4 Do not copy

- `Mark as done` as a completion primitive.
- Per-activity vendor silos. One runtime, one scorer, one evidence store stands.
- A uniform slot count per chapter. Treatment selection is per objective and
  should be allowed to say "direct reading is enough here".
- A gradebook whose only rows are the one activity type that happened to ship
  with a SCORM wrapper.

## 5. Open questions before any of this is planned

1. Does the treatment ladder live in the format contract, or in a course
   manifest beside the banks? `SOURCE-TO-COURSE.md` implies the latter.
2. What is the durable object for "a learner completed a reading"? There is no
   evidence event type for non-scored treatments today.
3. `self_report` evidence needs a rights and honesty story. It is learner-owned
   claim, not runtime verdict, and the two must not merge. See the CLAUDE.md
   rule that learner notes never silently become score or mastery.
4. Does the course view earn a new surface, or is it a mode of `day`?

## 6. Rights and provenance note

This teardown records structure, activity names, blurb text, URLs, and module
types from the learner's own enrolled course. No item content, no eBook text,
no TestPrep questions were extracted or stored. AAOS 12e content remains under
its publisher's terms; the `guard` rule that no real banks enter this repository
is unaffected.
