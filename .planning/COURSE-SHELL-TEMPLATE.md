# Course shell template, v0 (tentative)

Date: 2026-08-26
Status: **tentative proposal, corrected 2026-08-26 against shipped Phase 14B
work.** See section 0.1: three of this document's original proposals turned out
to duplicate existing requirements or shipped code and are withdrawn there
rather than silently edited out. Not an accepted product clause. Derived from
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

## 0.1 Correction, 2026-08-26: what this document got wrong

Written before checking Phase 14B, which had already shipped `graph.py`,
`course.py` and `course_package.py`, and before checking `REQUIREMENTS.md`.
Three proposals below are withdrawn. They are recorded rather than deleted
because the reasoning that produced them is still the evidence for the parts
that survive.

**Withdrawn 1: a fixed three-level hierarchy.** `graph.py` already ships
`add_container(doc, label, title, parent, order)` with a **free-text** label
and arbitrary nesting by `parent`, deliberately unconstrained because GRAPH-01
requires a local structural label to be accepted without a schema change. The
code comment is explicit that a course calling its unit a fortnight is not
wrong. Depth is solved. The shell **renders containers it does not own** and
must not introduce a competing level scheme. Section 1 is rewritten below.

**Withdrawn 2: a new seven-value treatment purpose set.** `graph.py` ships
`TREATMENT_KINDS`, an eleven-value **closed** vocabulary canonical in
`REQUIREMENTS.md` as TREAT-01: `direct-reading`, `excerpt`, `guided-lesson`,
`notes-or-terms`, `worked-example`, `visual-or-demonstration`, `practice`,
`formal-test`, `assessment-first-diagnostic`, `learner-artifact`,
`human-review`. Proposing `orient` / `read` / `teach` / `drill` / `apply` /
`check` / `reflect` beside it would have created a second vocabulary for the
same thing, which is the exact mistake this repository legislates against. The
proposed set is withdrawn entirely. What survives is the *question* it was
asking, which TREAT-01 does not answer: **which treatment kinds may emit
evidence that moves a progress dimension, and which may not.** Section 3 is
rewritten to ask only that.

**Withdrawn 3: coverage / mastery / claimed as the progress model.** GRAPH-03
already specifies something stronger: a nine-field tuple over **seven
dimensions kept permanently separate** (design coverage, participation, settled
evidence, current retention, formal completion, selected enrichment,
uncertainty), with no single aggregate score, separate denominators for
required, required-choice and enrichment, and the rule that adding enrichment
can never lower completion. It is owned by Phase 16C and read over the graph
rather than stored. My three numbers were a weaker restatement. Section 5.1 is
rewritten to contribute what it actually can, which is field evidence for
GRAPH-03 rather than a competing model.

**What survives unchanged.** The teardown facts; the reading view
(IL-20260826-06); pool depletion (IL-20260826-04); error-driven reselection
(IL-20260826-05); the time-axis gap (IL-20260826-07); the non-scored evidence
event (IL-20260826-08); and both rejections (IL-20260826-11, -12).

## 1. Structure: render containers, do not redefine them

`graph.py` already models structure as containers with free-text labels nesting
by `parent`, plus objectives placed in a container with an order. A container's
position is structure and adds zero edges; prerequisites are separate typed
edges. `outline` already projects this to a Markdown heading tree whose depth
follows `_depth(containers_by_id, ...)`.

So the shell's structural job is **rendering, not modelling**:

```
workspace          the set of courses the learner owns   <- the genuine gap
  └── course       one course sidecar (course.py)        <- exists
        └── container   arbitrary depth, free-text label <- exists
              └── objective + its treatment              <- exists
```

Only the top line is missing. Everything below it ships. `IDEA-LEDGER.md`
IL-20260817-01 additionally answers what a bounded scope is and when one may
truthfully report complete, and the shell must reconcile with that rather than
compete with it.

## 2. Durable objects

Most of this table already exists. Marked accordingly.

| Object | Source of truth | Status |
|--------|-----------------|--------|
| course | the course sidecar, one `kind="course"` object | **ships** (`course.py`) |
| container | a record inside that sidecar | **ships** (`graph.py`) |
| objective | a record inside that sidecar | **ships** (`graph.py`) |
| treatment | a TREAT-01 kind on an objective | **ships** (`graph.py`) |
| artifact | the bank, lesson, or source file | ships, existing contracts |
| package | portable export and validated restore | **ships** (`course_package.py`) |
| **workspace index** | **the set of courses; undecided** | **the gap** |
| progress tuple | GRAPH-03, read over the graph | specified, Phase 16C |
| cards, outlines, next-actions | rendered views | derived, disposable |

The original draft proposed a plain-Markdown course manifest. **Withdrawn.**
The sidecar exists, is written only through `journal.commit_operation` on one
compare-and-swap lineage, and deliberately keeps objectives and edges as
addressable records inside one file rather than as independently tracked files.
A second hand-authored manifest beside it would put two object kinds in
competition for the same bytes, which is the exact thing `course.py`'s
docstring says it refuses. Section 4 is withdrawn with it.

The one genuinely open durable object is the **workspace**: what names the set
of courses, whether it is a file at all or just a directory scan, and how it
relates to the discovery roots. That is the whole gap.

## 3. The open question TREAT-01 does not answer

TREAT-01's eleven kinds are canonical and closed, and nothing here adds a
twelfth. What no shipped requirement states is the **evidence contract per
kind**: which treatments can produce something that moves a GRAPH-03 dimension,
and which structurally cannot.

A first cut, as a question to be answered rather than an answer:

| TREAT-01 kind | Plausibly emits | Note |
|---|---|---|
| `direct-reading` | nothing the runtime can verify | needs IL-20260826-08 |
| `excerpt` | nothing the runtime can verify | same |
| `visual-or-demonstration` | nothing the runtime can verify | same; covers video |
| `guided-lesson` | scored checkpoints | inside the lesson |
| `worked-example` | unclear | may be read-like or practice-like |
| `notes-or-terms` | attempt records | drill-like |
| `practice` | attempt records | settled evidence |
| `formal-test` | full session evidence | settled evidence |
| `assessment-first-diagnostic` | deliberately unscored | see IL-20260822-01 |
| `learner-artifact` | learner-owned only | never mastery |
| `human-review` | a human verdict | advisory, not the scorer |

Three kinds land in the same hole: `direct-reading`, `excerpt` and
`visual-or-demonstration` produce nothing the runtime can check. That is one
gap, not three, and it is IL-20260826-08. Note that `visual-or-demonstration`
already covers video, so the separate `watch` purpose proposed earlier is a
duplicate and is withdrawn (IL-20260826-09).

The rule that must hold however this resolves: **a treatment kind that cannot
emit verifiable evidence must not be able to move a settled-evidence
dimension**, and the UI must show which dimension a number came from. GRAPH-03
already keeps the dimensions separate; this is about which one a treatment is
allowed to touch.

## 4. The manifest (withdrawn)

The original sketch proposed a plain-Markdown `course.md` with `UNIT:` sections
and `purpose label -> artifact` rows. Withdrawn: see section 2. The course
sidecar already holds this, `graph.py` already projects a readable outline from
it, and Phase 14B's D-14B-1 deliberately leaves the hand-authored Phase 13.9
`course.md` stub byte-identical rather than writing to it. Adding an authored
manifest would reopen a decision that was made for good reasons.

The readable-outline requirement the sketch was reaching for is already met by
`graph.outline`.

## 5. The surfaces

### 5.1 Workspace view, the first page

The progress model here is GRAPH-03's, not this document's. What the teardown
contributes is **field evidence for why GRAPH-03 is right**, which is worth
recording because the requirement is written abstractly and the specimen shows
concretely what the alternative costs.

Navigate2's card shows **one** number, a bar reading `0% complete`. It is an
activity-completion count that never consults the gradebook. Of the 435
activities in the observed course, 41 carry a grade item and **394 (90.6%)
complete by a self-pressed `Mark as done`**. Tick every box, open nothing, and
the card reads 100% complete beside an empty gradebook.

That is precisely the failure GRAPH-03's "no single aggregate completion,
mastery, or readiness score" clause forbids, and the specimen shows the failure
is not theoretical: the number is not merely imprecise, it is uncorrelated with
learning and is trusted anyway. Worth citing whenever someone asks why one
friendly percentage would not be simpler.

Two things the teardown adds that GRAPH-03 does not obviously already cover:

- **Participation must not be sourced from an unverifiable claim** without
  saying so. GRAPH-03 has a participation dimension and an authority field; the
  specimen shows what happens when a claim silently fills a participation slot.
  This is IL-20260826-08's honesty story, restated as a display rule.
- **Card-size display needs a rule.** Seven dimensions do not fit on a course
  card. Which one shows when only one fits, and whether showing one re-creates
  the aggregate problem by the back door, is unresolved and belongs to Phase
  16C rather than here.

Beyond the numbers, and cheap: subject, container count, last activity, and the
next action if one is ready. Not a hero image; the specimen's card spends most
of its area on a generated hexagon pattern carrying no information. Filter,
search, sort and a card-or-list toggle are worth matching as-is.

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

1. **Depth, and it is less open than it looked.** The 2026-08-13 vision asks
   for field > subject > subcourse > concept and for "completing a field".
   `IDEA-LEDGER.md` IL-20260817-01 already answers it with a recursive,
   authored, versioned **scope** object over the typed graph, plus a
   boundedness axis so an open scope never reports complete. v0's three levels
   must therefore **reconcile with that model rather than compete with it**:
   `unit` is a scope, and the question is whether the shell needs its own
   nesting at all or should render scopes it does not own. Resolve this before
   the manifest format is fixed, because getting it wrong is expensive later.
2. **Evidence event for a non-scored treatment** (IL-20260826-08, the smallest
   blocking piece). No type exists today for "read this". `self_report` needs an
   honesty story before it ships, and the obvious fix is the rejected one.
3. **Surface or mode.** Is the course view a new surface, or a mode of `day`?
4. **Where the manifest lives** relative to banks and to an Obsidian vault, and
   how discovery binds it without mutating anything.
5. **Cross-course scheduling.** `day` already spans subjects. Does the workspace
   view compete with it, or feed it?
6. **Pool depletion needs a definition** (IL-20260826-04). "Seen" is not "attempted" is not
   "mastered", and a shuffled variant of an item is not a new item. Before a
   remaining-count can be shown it has to say what it counts.
7. **Does the reading view need its own progress model** (IL-20260826-06) or does it borrow the
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

## 9. Dispositions

Every idea in this document has a durable route in `.planning/IDEA-LEDGER.md`,
per the standing rule that no viable idea is left without one:

- Registered: IL-20260826-01 (narrowed to the workspace level only), -04 (pool
  depletion), -05 (error-driven reselection), -06 (reading view), -07 (time
  axis), -08 (evidence event for a non-scored treatment, the smallest blocking
  piece).
- Backburner: IL-20260826-10 (teaching pool separate from exam-fidelity pool).
- Duplicate, withdrawn same day after checking shipped code: IL-20260826-02
  (a parallel treatment vocabulary; TREAT-01 is canonical), -03 (a progress
  model; GRAPH-03 is stronger and owned by Phase 16C), -09 (a `watch` purpose;
  TREAT-01 ships `visual-or-demonstration`).
- Rejected: IL-20260826-11 (`Mark as done` as a progress primitive),
  -12 (flat equal-size category pools as a blueprint).
- Reconcile with, do not duplicate: IL-20260817-01 (scope object, boundedness,
  progress rollup), TREAT-01, GRAPH-01, GRAPH-03.

## 10. Rights note

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
