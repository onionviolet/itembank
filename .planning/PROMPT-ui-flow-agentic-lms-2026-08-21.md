# Prompt: plan the UI flow, and what makes this a proper agentic LMS

Paste this whole file as the opening message of a fresh planning session on a
capable model. It is self-contained and does not depend on chat history.

Written 2026-08-21 from the USER-VISION entry of the same date, which asked for
"a proper agentic based LMS" and for a plan of "how the UI flow should
logically work". The second half of that ask is older: the 2026-08-13 entry
asked for the same flow planning and it has not been done.

---

You are running a **planning-only** session on `itembank`
(`C:\Users\wayba\Downloads\CTF\itembank`, branch `main`).

## What to read, and nothing else at first

Read these five, in this order, before you write anything:

1. `.planning/USER-VISION.md`, the 2026-08-21 entry and its interpretation.
2. `.planning/PLANNING-DIRECTIVES.md`.
3. `.planning/SOURCE-TO-COURSE.md`.
4. `.planning/UI-SPEC.md` sections on IA and accessibility.
5. `.planning/phases/17A-visual-system-component-foundation/17A-06-SUMMARY.md`
   and `17A-07-PLAN.md`.

Do NOT read `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, or `AGENT-WORKFLOW.md`
up front. Grep them when a specific question needs them. That stack is about
122,000 tokens and re-reading it every turn is what a previous run spent 5.1
billion tokens on.

## Operating rules, in force for the whole session

1. **Keep going.** PLANNING-DIRECTIVES section 2. Do not stop to ask what you
   can answer from the codebase, the research artifacts, or a defensible
   default. Record the assumption and continue. Stop only for a hard-to-reverse
   action, a choice that lowers quality whichever way you guess with no
   research verdict, or a conflict with the five non-negotiables.
2. **When two designs both look defensible, build both.** PLANNING-DIRECTIVES
   section 3, with the 2026-08-13 qualification: a second design is registrable
   only when it shares the canonical objects, authority, accessibility,
   permission, recovery, and maintenance contracts. When two options would need
   two parsers, two scorers, or two evidence stores, pick one and write down
   why.
3. **Plan only. Do not execute.** Write planning artifacts and commit them.
4. **No em dash characters** anywhere, including plans, prose, and comments.
5. **A concurrent Codex track shares this working tree.** Use pathspec-limited
   `git commit -- <paths>` for everything. Never a bare `git commit -a`.
6. **End every turn with something openable.** Twelve phases closed without
   Weibao seeing output. If a flow decision can be shown as a rendered page
   instead of described in a paragraph, render it.

## The boundary that does not move

One parser, one scorer, one evidence store. The runtime settles scoring,
session state, keyed disclosure, and evidence. An agent may operate everything
the learner can operate and propose everything an author can propose. It may
never settle a mark or release a key. A design that needs a second authority is
rejected, not negotiated.

This is a small safety boundary, not a limit on ambition. Do not use it as a
reason to plan a timid product.

## Part 1: the UI flow

The question is not what the screens look like. 17A settled that: structured
studio, sidebar, indigo. The question is what happens next, always.

Plan the flow as a state machine over the learner's session, not as a sitemap.
For each of these, name the entry state, the exit states, what is preserved
when the app closes mid-way, and what the learner sees when the thing they
need is missing:

1. **Cold open.** The learner opens the app with nothing in progress. What is
   the single next action, how was it chosen, and what does it say when there
   is no defensible choice.
2. **Resume.** Something was in progress. What resumes automatically, what asks
   first, and what is never resumed silently (a graded sitting, for one).
3. **Objective to treatment.** A cited objective exists and the treatment is
   chosen. Direct source reading, a lesson, practice, and a test are four
   different destinations from one place. What decides, and how does the
   learner override it.
4. **Wrong answer.** The single most important screen in the product. The
   runtime owns the tier. Plan what the learner does next after a wrong
   answer, not what the model says.
5. **Evidence to next action.** Evidence exists and is honest. Plan the path
   from a weak objective to the thing that fixes it, without the learner
   reading a dashboard to work it out.
6. **Course building.** Sources bind, a map is built, artifacts are proposed.
   Plan where a proposal appears: only in the Agent area, or on the object it
   affects. Argue both and recommend one.

Deliverable: `.planning/UI-FLOW.md`, plus a rendered walkthrough of at least
the cold open, the wrong answer, and the evidence-to-next-action flows through
`surfaces/visual_fixture.py` so Weibao can click it rather than read it.

## Part 2: what "a proper agentic LMS" actually requires

Six open questions are already recorded in the USER-VISION 2026-08-21 entry.
They are your agenda. Do not re-derive them, answer them.

Beyond those, work these out and record a disposition for each. Some of these
should be rejected, and a rejection with a reason is a good outcome:

**The LMS-shaped objects.** Which of assignment, due date, enrollment-style
progress, and gradebook view are real durable objects with a source of truth,
and which are derived views over evidence that already exists. Default to
derived. A new durable object needs an actor, an authority, state axes,
provenance, degraded behavior, and a maintenance owner before it is accepted.

**The agent's unit of work.** A skill invocation, a goal that decomposes, or a
standing role that watches evidence and proposes unasked. These are not
exclusive. Say which ships first and what the others depend on.

**Where an operation lives in the UI.** An agent operation that revises a
lesson could appear in the Agent area, on the lesson, or in both. Pick, and
say what it costs to be wrong.

**Interruption.** What happens to a running operation when the app closes,
when the model goes away mid-run, and when the file it targeted changed
underneath it. `journal.commit_operation` already answers the third with a
conflict state. Answer the other two.

**The two-path question.** 17A-06 ships an embedded external console and
17A-07 ships an itembank-driven seam. Do they stay two paths permanently, or
does one absorb the other once the second works. Both shipping is the current
decision; this question is about the year after, not about now.

**What an agent must never be able to reach.** Write the list. It is short and
it should be explicit somewhere other than a docstring.

Deliverable: `.planning/AGENTIC-LMS.md`, with a disposition for every item and
a named phase or backlog row for every disposition that survives.

## Part 3: sequence it

Turn Parts 1 and 2 into roadmap rows and executable plans at the
PLANNING-DIRECTIVES section 5 lesser-model executor bar. Codex plus DeepSeek
executes them; no design question may reach an executor.

Respect what is already sequenced. 17A-07 is registered and is the seam those
flows will run on. Do not plan around it or duplicate it.

## One thing to weigh before you plan anything

**Phase 13.9-03 is still open.** It needs Weibao to put one real EMT bank
through `itembank serve` and sit it. It is `autonomous: false` because no model
can do it. Twelve phases are marked complete and the product has never been
used on real material.

If your plan produces another architecture phase and 13.9 is still open, say so
in the first paragraph of your output, and say what a flow plan built on zero
real sittings is worth. Do not quietly plan around it.
