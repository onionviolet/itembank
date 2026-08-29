# Prompt: paced lessons with checkpoints, from guidelines to implementation

Paste this whole file as the first message of a new session.

---

You are working on **itembank** at `/Users/weiwei/Documents/Dev/itembank` (macOS).

Your job is to turn one recorded idea into an implementable plan: **a paced
presentation of a lesson, with checkpoint questions inside it, a short read then
a check, repeating.** The idea is registered and the evidence is gathered. What
does not exist is the design decision and the plan.

## Read in this order, and stop reading when you can answer the questions

1. `.planning/research/2026-08-28-navigate2-interactive-lecture-shell.md`, all of
   it. It is short. Sections 1a, 2, 3 and 4a are the substance.
2. `IDEA-LEDGER.md`, entries `IL-20260828-01` through `IL-20260828-04`, and
   `IL-20260826-02` and `IL-20260826-10` which they depend on.
3. `.planning/USER-VISION.md`, the 2026-08-24 entry on feedback that lets you
   proceed. It constrains what a wrong checkpoint answer must show.
4. The course creation guidelines, which are spread across four places and are
   the reason this prompt exists:
   - `.claude/CLAUDE.md`, the "Course artifact workflow" eight steps and the
     "Object, authority, and operation summary". Step 6, the dual form rule, is
     the one this feature lives or dies on.
   - `.planning/SOURCE-TO-COURSE.md`, the binding milestone scope.
   - `.claude/skills/lesson-authoring/`, `build-course/`, `curriculum-design/`.
     Note that `lesson-authoring` is a **stub**: its command surface has not
     shipped. Establish what actually exists before planning against it.
   - `.planning/UI-SPEC.md`, the accessibility gates. Grep it, do not read it end
     to end.

Do **not** read `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `AGENT-WORKFLOW.md`
or `PLANNING-DIRECTIVES.md` end to end. That stack is roughly 122,000 tokens.
Grep for what you need.

## The three questions to answer before any code

**1. Is pacing an authored property of the lesson, or a view preference of the
reader?** This is the fork named in section 4a and it decides everything after
it. If authored, a step is a durable thing that can be cited and resumed, and it
needs a boundary syntax. If a view preference, a step exists only while someone
is looking and no format change is needed at all. Section 4a lists eight
boundary candidates, marked non-exhaustive; Weibao explicitly declined to narrow
them on 2026-08-28, so **present the fork with a recommendation and let him
choose.** Do not stand in for this decision. Note the recorded constraint: a
renderer-computed boundary has unstable identity across edits, which breaks
resume and step citation.

**2. What is a checkpoint attempt, in evidence terms?** Is it the same session
object as a sitting, or a distinct evidence kind. It must not silently enter a
blueprint denominator, per `IL-20260826-10`. Whatever you decide, the verdict is
the runtime's and there is no second scorer.

**3. What does a wrong checkpoint answer show?** The specimen was only observed
on the all-correct path, so there is nothing to copy here, and its correct-path
feedback merely restates the stem, which is not worth copying either. The
2026-08-24 vision entry is the authority: rule out what is wrong, show what is
right, do not make the retry a gamble. itembank's authored `DA:` already carries
per-option rationale; the missing piece is the disclosure policy that decides
when the runtime releases it, gated by session mode and hint tier.

## Constraints that are already settled, do not relitigate

- The lesson document stays the durable object. A paced view is a **projection**
  of it, not a second authored file. Same Markdown reads as a document in
  Obsidian.
- Checkpoint items are ordinary bank items scored by the one scorer, producing
  ordinary attempts in the one evidence store.
- Position in a deck is presentation state. Resumable, never progress, never
  coverage, never mastery.
- Gate a step on **attempted**, never on **correct** (`IL-20260828-03`). No
  timers (`IL-20260828-02`, rejected).
- Narration, if it exists at all, is optional, captioned, speed-controlled, and
  the deck is fully usable with audio off, which is also the offline path.
- Keyboard reachable throughout; the table of contents jumps and never gates.

## Deliverable

A phase plan, in the repository's usual plan shape, that traces backward to the
research file and the ledger entries and forward to verification. Put the three
questions above in front of Weibao as a decision packet **before** planning past
them, in the style of `.planning/DECISIONS-14B-DRIVER-2026-08-27.md`. An
unanswered checkpoint stops the wave; do not proceed on a silent default.

Check first whether this belongs inside an existing planned phase rather than a
new one. Phase 16A is planned and unexecuted, 16B halts on its precondition, and
14B waves 4 to 6 and all of 14C are blocked on eight decisions Weibao has not
made. Adding a ninth open front may be the wrong move, and saying so is a valid
outcome of this session.

## On the specimen

Do not go back to Navigate2 for more. The player's per-page XML and template
vocabulary were not obtainable and are not worth further effort: the shape is
understood, and anything itembank builds here is clean-room derived. No vendor
item content is in this repository and none should enter it.
