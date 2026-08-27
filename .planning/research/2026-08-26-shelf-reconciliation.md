# The main menu already exists on paper: reconciling the teardown with APP-01 and 16B

Date: 2026-08-26
Status: reconciliation note. Changes no requirement and opens no plan.
Prompted by: Weibao, "consider the main menu creating based off the template".

## Summary

The main menu is not an open design question. `REQUIREMENTS.md` **APP-01**
specifies it and Phase **16B-04** plans it in full, with exact copy, ordering,
degraded states, and a test fixture. This note maps the Navigate2 teardown onto
that existing work rather than proposing a second design.

The headline: **16B-04 already forbids, by name and with `status: kept`, the
exact thing Navigate2 does.** The teardown is therefore confirmation and field
evidence, not new direction.

## 1. What APP-01 and 16B-04 already say

- The home surface is a **course shelf**: one card per course, each with an
  **exact resume cue** and an **attention state**. Banks are assessment
  artifacts inside courses, not the primary navigation unit.
- Each course exposes nine areas: Overview, Learn, Practice, Test, Course map
  (outline first), Sources, Build and review, Evidence, and contextual Notes.
  Routes are already fixed in 16B-01 and 16B-05, as
  `/course/<id>` and `/course/<id>/(learn|practice|test|map|sources|build|evidence)`.
- **Six attention states**, each with required text and never colour alone:
  `up to date`, `due`, `pending review`, `needs your input`,
  `needs reconciliation`, `showing last valid overview`.
- **Ordering is a total order**: attention rank, then most recent recorded
  activity descending, then course ID ascending (D-16B-10).
- **Empty state copy is exact**: heading `No courses yet`, body
  `Start with the sample course, or bind a source to create your first course.`
- A corrupted course still renders, with `Showing last valid overview` plus
  `Open last valid overview` and `View files`, so it is never a dead end.
- Names wrap rather than truncate. Two courses with identical names stay two
  cards keyed by course ID.

## 2. The prohibition that makes the teardown a confirmation

16B-04 carries this prohibition, `status: kept`, quoted:

> A single aggregate completion, mastery, or readiness percentage must not
> appear on a course card, because a ratio synthesized across incompatible
> evidence dimensions is a fabricated measurement presented as fact.

And this must-have truth:

> No surface derives or rounds a progress percentage: no shelf card, chip, or
> resume cue contains a percent character, and a denominator appears only when
> the underlying record carried one.

Navigate2's card is a bar reading `0% complete`. The teardown measured what is
behind it: of 435 activities, 41 carry a grade item, so **394 (90.6%) complete
by a self-pressed `Mark as done`**. The prohibition was written from principle;
the specimen supplies the field measurement that shows the principle is not
fussiness. That measurement is the note's main contribution and belongs in any
future defence of the clause.

**The replacement is also better than what this teardown proposed.** A
qualitative attention state plus an exact resume cue answers "what should I do
about this course" directly, where any percentage answers a question the learner
did not ask. The course-shell template's `coverage` / `mastery` / `claimed`
triple was already withdrawn against GRAPH-03; it is withdrawn again here
against something more concrete.

## 3. What Navigate2 most conspicuously lacks, and we already planned

**A resume cue.** There is nothing anywhere in the specimen that says continue
where you left off. The learner re-navigates a drawer of 41 chapters, each
expanding to nine leaf links, and reconstructs their own position every session.
16B-04 requires the cue to be server-computed, exact, never guessed, never
cached client-side, never stale, and to read `Not started` rather than a
carried-over value when the record is unavailable.

This is the single largest experiential difference between the two products and
it is already specified. Worth stating plainly because it is easy to look at a
tidy Moodle shelf and conclude we are behind it.

## 4. Teardown items reconciled

| Teardown item | Disposition against existing work |
|---|---|
| One aggregate percentage is wrong | Already prohibited, `status: kept`. Teardown supplies the 90.6% field evidence. |
| Coverage / mastery / claimed triple | Withdrawn. GRAPH-03 is stronger; attention states are more useful at card size. |
| Next-actions pane over a browse drawer | Already the resume cue plus Overview. No new surface. |
| Reading view | Substantially `/course/<id>/sources`. **Residue survives:** Sources is per course; grouping bindings by source **across** courses so a book reads as a book is not covered. IL-20260826-06 narrowed to that. |
| Time axis, deadlines and pacing | Partly covered: `due` is a shipped attention state. **Residue survives:** where `due` comes from is unspecified, and nothing in the graph holds a date. IL-20260826-07 narrowed to that. |
| Pool depletion | Not covered by APP-01 or 16B. Genuinely open, and a selection-engine concern rather than a shelf one. IL-20260826-04 stands. |
| Error-driven reselection | Not covered. IL-20260826-05 stands. |
| Evidence event for a non-scored treatment | Not covered. IL-20260826-08 stands, still the smallest blocking piece. |
| Activity-purpose colour coding | Superseded by something stricter: attention states must never be colour alone and always carry required text. |

## 5. One stale precondition found, worth fixing before 16B runs

`16B-PATTERNS.md` line 381 records the course-area handlers as depending on
`course.py` and `graph.py`, annotated **"(14B, unbuilt, confirmed MISSING)"**,
and requires every such handler to sit behind the 16B-01 precondition check and
render only a degraded not-yet-available state until those modules exist.

**That annotation is now stale.** Phase 14B waves 1 to 3 landed on 2026-08-26
and `graph.py`, `course.py` and `course_package.py` all exist. Similarly
`16B-01`'s D-16B-3 reasons that a `course` CLI verb would be "a command with
nothing behind it" because "`course.py` does not exist".

Neither is a defect in those plans; both were written honestly against the tree
at the time, and 16B-04's own must-haves already anticipate 14B landing. But the
16B-01 precondition check should be **re-run against the current tree** before
16B executes, or the phase will ship degraded fallbacks for modules that are
present, and D-16B-3 may deserve revisiting now that a `course` verb would have
something behind it.

Recorded here rather than edited into those plans, since amending a built plan
is a decision for whoever executes 16B.

## 6. What this note does not do

It opens no plan, changes no requirement, and does not schedule 16B. Phase 14B
waves 4 to 6 each carry a blocking human checkpoint and are not started, and
`STATE.md` still names 14B as the current phase. The shelf mockup produced
alongside this note is an illustration of the existing 16B-04 copy contract, not
an implementation and not a new design.
