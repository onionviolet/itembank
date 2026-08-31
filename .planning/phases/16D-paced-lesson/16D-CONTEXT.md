# Phase 16D context: paced lesson projection and checkpoints

- **Gathered:** 2026-08-31, planning session, autonomous under
  PLANNING-DIRECTIVES section 2. The three consequential design questions
  were already answered on 2026-08-28 under Weibao's quoted same-day
  delegation ("just decide for each accordingly to uservision of modularity
  and improvability and achiving the end goal"); this context transcribes
  and binds them, it does not re-decide them.
- **Decision records this phase implements:**
  `.planning/DECISIONS-PACED-LESSON-2026-08-28.md` (D-PACED-1, D-PACED-2,
  D-PACED-3), IDEA-LEDGER IL-20260828-01 (registered), IL-20260828-02
  (rejected timed lock, binding as a refusal), IL-20260828-03 (gate on
  attempted, registered), and
  `.planning/research/2026-08-28-navigate2-interactive-lecture-shell.md`
  section 3.3 (what the mode owes).
- **Placement:** after 16C, before 17B, per the decision packet section 3.
  Dependencies 16A and 16B are frozen; the Phase 6 feedback machinery and
  the Phase 6.2 gate bands are shipped. Nothing here waits on 17A's freeze,
  and nothing here is a 17B gate.

## Domain

A `paced` presentation of an already authored lesson: the same Markdown
reads as a continuous document in Obsidian and projects as an ordered
sequence of steps, with a table of contents that jumps rather than gates,
and checkpoint items drawn from the bank, scored by the one scorer,
producing ordinary attempts in the one evidence store inside a distinct
lesson-run session. The lesson stays the durable artifact; pacing is a
projection, never a second file (dual-form rule).

## Binding decisions

- **D-16D-1 (from D-PACED-1). Pacing is authored, read through the ladder.**
  Precedence: an explicit authored marker with a stable id, else the
  configured heading level for that lesson, else the whole document as one
  step, which is byte-identical to today's behaviour. The reader may only
  coarsen, never introduce a boundary. Agent-proposed markers (candidate H)
  are deferred and NOT built in this phase.
- **D-16D-2 (syntax, resolved here; D-PACED-1 froze only the id
  requirement).** The marker is `[STEP: <id>]` alone on a line inside the
  lesson body, following the existing `[SRC:]`/`[LESSON-REF:]` bracket-line
  convention, where `<id>` matches `[a-z0-9][a-z0-9-]{0,63}`. Duplicate ids
  and malformed ids are lint ERRORS. The rung-2 knob is a preamble tag
  `[LESSON-PACE: <value>]` with values `h3`, `none`; default `none`
  (rung 3, whole document). Corrected 2026-08-31 before execution: the
  first draft listed `h2`, but the LESSON grammar's headings are `###`
  only (the `##` level is the section marker itself), so `h2` named a
  boundary that cannot occur and was removed rather than shipped inert. A resume position and a checkpoint anchor
  record the step id, never the ordinal. Basis: D-PACED-1's identity
  argument; the bracket-line convention keeps the document readable as
  plain Markdown in Obsidian, which the format already accepts for `[SRC:]`.
- **D-16D-3 (from D-PACED-2). One evidence store, distinct session kind.**
  A lesson run is its own session object (`kind: "lesson_run"`), never a
  sitting: no blueprint, no form. Checkpoint attempts inside it are
  ordinary attempts with the shape every attempt has, carrying an additive
  context label; blueprint denominators exclude lesson-run attempts by
  default, as a read-time policy on the label, never as a hidden or
  separate record. Additivity is proven against pre-change baselines (the
  16C evidence-event precedent).
- **D-16D-4 (from D-PACED-3). Tiered disclosure on a wrong checkpoint,
  released by the runtime.** Tier 1 on the first wrong attempt: which of
  the learner's own selections are wrong and which are right, never
  unselected correct options. Tier 2 with tier 1: the authored `DA:`
  rationale for the options the learner actually touched, only those.
  Tier 3 on a second wrong attempt or explicit learner request: the full
  key and why. This is a feedback-policy addition inside the runtime's
  existing disclosure authority (`FEEDBACK_POLICIES` and the reveal path),
  never a scorer change: `multi` stays all-or-nothing, exam and diagnostic
  modes stay silent and untouched, and a model cannot argue a tier open.
- **D-16D-5 (from IL-20260828-02, IL-20260828-03). Gates and the refusal.**
  A step may gate forward navigation on an ATTEMPTED checkpoint, never on
  correct. Backward navigation and the table of contents are never gated.
  No timed lock of any kind; elapsed time is not learning. The Phase 6.2
  gate-band machinery (check first, skip as an ordinary control, degrade
  lines) is reused, not reimplemented.
- **D-16D-6 (from research 3.3). What the surface owes.** Every step
  reachable by keyboard and by the jump-only table of contents. Position is
  resumable presentation state and never counts as coverage, mastery, or
  progress; a step that emits no evidence says so. Narration is out of
  scope for this phase entirely (research question 4 stays open). Offline
  and static builds degrade to the continuous document, never block.
- **D-16D-7. Surface placement.** The paced projection lives in the lesson
  renderer (`surfaces/lesson.py`) behind the existing lesson route, as a
  query-selected view, not a fourth surface module. The CLI owes no slide
  view (presentation-only behaviour owes an accessible equivalent, which
  the continuous document is); the checkpoint items owe both and already
  have both through the quiz machinery. Basis: research question 3 plus the
  2026-08-15 surfaces clarification.

## Freeze gate

A paced-lesson tracer on synthetic fixture content: author markers, resolve
the ladder at every rung, sit checkpoints through the runtime with the tier
ladder exercised (tier 1, 2, 3, and the never-disclosed exam contrast),
prove the denominator exclusion, prove resume stability across a lesson
edit that inserts an earlier step, and prove rung-3 byte-identity for a
markerless lesson. Human checkpoint: Weibao reviews the rendered paced flow
before freeze (accessibility per the standing A11Y rules; an agent never
self-certifies).

## Deferred, recorded so it is not rediscovered

- Candidate H, agent-proposed markers as a bounded diff (D-PACED-1).
- Narration authoring, captions, speed control (research question 4).
- The reader coarsening control beyond "whole document" (candidate G's full
  granularity menu); this phase ships paced versus continuous only.
- Inline-select cloze checkpoints (IL-20260828-04) stay on their own ledger
  disposition.

## Reconsideration conditions carried forward

Each binding decision above inherits its reconsideration condition from
`DECISIONS-PACED-LESSON-2026-08-28.md` verbatim; the tracer plan asserts
none of them has fired at execution time.
