# Planning Directives: standing rules for every GSD session on this project

- **Created:** 2026-08-10
- **Status:** binding on every `/gsd-discuss-phase`, `/gsd-ui-phase`, `/gsd-ai-integration-phase`, and `/gsd-plan-phase` run
- **Supersedes:** nothing. Sits alongside `.claude/CLAUDE.md` Constraints (as amended
  2026-08-09) and `.planning/UI-SPEC.md`.

This file exists because the same instructions were being re-stated in every session
and losing fidelity each time. Any planning agent reads this before it reads the phase.

The cross-agent execution and handoff contract is `AGENT-WORKFLOW.md`. Planning
sessions follow both files. This document governs exploration, choices, and
phase preparation; `AGENT-WORKFLOW.md` governs authority, research waves,
dispositions, file operations, accepted revisions, readiness, and durable
handoff across agent clients.

---

## 1. Weibao's words, verbatim

Recorded 2026-08-09, reproduced here so no summary stands in for them.

> "our constraints is bendable if the idea is good enough, local first is not a
> real contraint, but a preference, build step is not a constraintm we cab build
> if need b, and shoudnt be limited by python if better options exist and mroe,
> we do want a packaged app in the end,"

> "goal is the plan and explore comprehensively, leaving executrion to deepseek"

> "Cool features no one has like keyterms with hover over, seperate blocks of
> stuff to remember, lesson generation styling/voice, we can combine all their
> unique benefits and address all their weaknesses too"

Recorded 2026-08-10:

> "we can do a /gsd-discuss-phase just pick the considerations that are most
> useful/comprehensive/if conflicting potentially implement all of them and let
> the user choose in the future, keep going without human stoppage if its
> reasonable and wont cause lasting harm, or lower quality, the idea is for UI
> and other important stuff to be planned by a more capable model before hand"

> "Different lesson styles, styles inspired by thats alreadyt upd there and more?"

Recorded 2026-08-10, after the round-two research pass:

> "can establish that the main stuff should work with something like claude code for
> now to not worry so much"

Recorded 2026-08-13, product reframe (normalized only for spelling; meaning
preserved):

> The goal is to create a course from a book, syllabus, notes, exam blueprint,
> or other collected material; extract useful lessons, terms, notes, or direct
> source readings; provide high-quality practice and tests appropriate to the
> specific course or standardized exam; let AI drive curriculum construction,
> quality work, and evidence interpretation where reasonable; and present it
> through a rich, comprehensive learning UI. Hosted coding agents and a local
> agent are both target clients.

**What this settles.** The default authoring and hint backend is a **hosted
coding-agent-class model (Claude Code or equivalent)**. The local 24GB card is a
*second registered backend*, not the design target. Consequences, binding on planning:

- Phase 8 plans against a hosted adapter first. The local backend is an additional
  registration behind the same interface, not a fork and not a prerequisite.
- R3.5's throughput unknown stops being a blocker. `itembank bench` is still owed, but
  it moves off the critical path and no phase may carry an invented tok/s figure in
  the meantime.
- Prompt-size and latency budgets are written against the hosted model. The local
  backend declares its own limits; a phase that assumes 8K everywhere is wrong.
- This does **not** relax §4.1. A hosted model decides nothing about correctness. The
  tier-3 `pending` rule is unchanged and is not a function of which backend runs.
- Offline-first survives as a preference, per the 2026-08-09 constraint relaxation.
  The runtime, the parser, the scorer and the evidence store stay local and stay
  model-free; only authoring and hint generation reach for a backend.

**What the 2026-08-13 reframe settles.** Read
`.planning/SOURCE-TO-COURSE.md` before planning the next milestone. The course,
not the bank, is the primary user-facing unit. AI is not confined to hint generation: it
may perform approved source discovery, curriculum alignment, treatment
selection, artifact drafting and revision, quality review, metric
interpretation, and remediation. The runtime invariant remains narrow:
deterministic scoring, assessment disclosure, and evidence authority do not
move into the model.

---

## 2. The autonomy rule

**Keep going.** Do not stop a planning session to ask a question you can answer
from the codebase, the research artifacts, or a defensible default. Record the
assumption and continue.

Stop only for these, and for nothing else:

1. An action that is **hard to reverse**, such as an append-only evidence field, a
   published schema, a format decision other phases will build against.
2. A choice that would **lower quality** whichever way you guess, where the
   research contains no verdict.
3. A conflict with one of the five non-negotiables in §4.

Everything else: decide, write down the reasoning, move on. A blocking question
costs a session round-trip; a recorded assumption costs one line.

## 3. The conflict rule: build both, let the learner pick

When two designs both look defensible and neither is clearly wrong, **do not
arbitrate**. Implement both behind one interface and make the choice a setting.

This is affordable here specifically because of the Extensibility Rules in
`ROADMAP.md`. A second implementation of an existing interface is a registration,
not a fork. It stops being affordable, and the rule stops applying, when the two
options need **two parsers, two scorers, or two evidence stores**. That is when you
pick one and say why.

Applies directly to: lesson styles, hint pacing, scheduler algorithm, refusal
copy, reading layout, selection strategy, TTS engine, model backend.

**Qualification added 2026-08-13 (synthesis sections 1, 1.2, and 8).** "Build
both" is not unconditional. A second design is registrable only when it shares
the canonical semantics, authority, accessibility, permission, recovery, and
maintenance contracts. Concretely, a strategy or mode may be registered only if
it shares the canonical objects, states a purpose and eligibility rule, defines
required and optional learner actions, skip and resume, evidence effects,
accommodations, offline behavior, and tests. When two options cannot share those
contracts (two parsers, two scorers, two evidence stores, or a genuinely mutually
exclusive design that cannot share an interface), you pick one and say why, or you
prototype reversibly first. Avoid a Cartesian product of arbitrary style toggles.

## 3a. Disposition, breadth, and accepted-recommendation discipline

Added 2026-08-13 from `.planning/research/phase-16/14-synthesis.md` sections 1,
12, and 15.

**Breadth is preserved by default.** Ideaboarding breadth is not narrowed by
coalescing. Coalescing gives broad capabilities one coherent architecture and
shared primitives; it organizes viable proposals into `core now`, `registered`,
`prototype`, or `backburner`. A capability is not dropped merely because it is
optional, expensive, specialized, or absent from the next wave. **Simplicity
alone is not a rejection reason.** Rejection is reserved for conflict with
assessment authority, accessibility, rights or licensing, safety, truthful
evidence, portability, or the coherent product model, including a genuinely
mutually exclusive design that cannot share an interface.

**Append-only rejection record.** A rejected or superseded idea is never deleted,
even when the surrounding architecture changes. Each entry records: the proposal,
its source or vision origin, the evidence considered, the exact reason, the
conflicting rule or quality attribute, the alternatives retained, the date, and
the reconsideration condition. The permanent ledger lives in synthesis section
12.4 and is carried forward additively. A silently omitted, deleted, or
simplicity-only rejection fails review.

**Accepted-recommendation discipline.** Every accepted recommendation names its
owner, its verification, its evidence class (see synthesis section 1.1), and its
failure condition. A recommendation with no owner, no test, or no stated failure
condition is not ready to enter a binding contract.

**Reversible prototypes are mandatory** before any durable commitment to a format
or schema, the objective graph, a registered strategy, an executable source, or a
complex visual system. Prototype the graph-to-outline projection and the
denominator or version migration before a course schema freeze; the Markdown
rich-lesson stress corpus before a lesson-profile grammar freeze; the
guided-note, worked-reasoning, and incorrect-note pathways before a strategy
registry; restricted notebook preview before an execute or trust UI; visual-math
equivalence before a broad interaction registry; cross-client interruption before
an agent job protocol freeze; clean-machine restore before a course package or
export promise; and the same logical flows in three visual directions before the
Phase 17 tokens freeze.

## 4. What never bends

Everything in `.claude/CLAUDE.md` bends per the 2026-08-09 amendment **except**:

1. The **runtime owns assessment authority**: correctness, session state,
   evidence, and disclosure of keyed assessment content. This does not limit a
   model from producing ordinary course material, teaching content, treatment
   recommendations, or course revisions through the approved authoring path.
2. Exactly **one parser, one scorer, one evidence store**.
3. Evidence and banks stay on disk. No telemetry.
4. Format changes are **additive**. A bank not using a new block parses unchanged,
   proven by a byte-identical fixture, not promised.
5. The accessibility gates in `.planning/UI-SPEC.md`.

A research finding or a design idea that violates one of these is rejected on that
basis alone, however good it is otherwise.

## 4a. Constraint basis: what binds, what does not, and how to cite it

Added 2026-08-10 from `.planning/research/2026-08-10-constraint-audit.md`. Additive
only: it disambiguates §4, and changes nothing in it.

A rejection, deferral, or "must" in any planning artifact is only as good as the
text behind it. Before you invoke a constraint, open the file and read the line.

**These five bind, and nothing else does.** They are §4.1-§4.5 above. Cite them by
number only when you have read the numbered text and it says what you need it to
say. §4.5 is exactly nine gates: `UI-SPEC.md` §8 items 1-9. It is not a general
accessibility instinct and it is not a renderer policy.

**These are preferences, per the 2026-08-09 amendment. They may inform a choice.
They may never veto one, and they may never be the whole stated reason:**
Python-stdlib-only, no install step, no build step, Python-only, offline-first,
local-first. A plan that rejects an option "because it needs a dependency" has
not made an argument. Report the real cost and decide on merit.

**These do not exist. Do not enforce them:**

- *No JavaScript.* `UI-SPEC.md` §7 permits embedded vanilla JS in plain words; the
  product vendors CodeMirror 6. The "No Node.js, JavaScript" line in
  `.claude/CLAUDE.md` sits inside the block marked HISTORICAL and non-binding.
- *A print path.* No authoritative file requires printable output. "It breaks
  print" is not a veto.
- *A vendored-asset budget.* KaTeX is an example, not a quota.
- *No dependencies as a security control.* See the supply-chain rule below.

**The three rules most often stretched past their scope:**

- §4.2 forbids a **second** parser, scorer, or evidence store. It does not freeze
  the one parser's grammar. Additive growth is §4.4's subject and is permitted,
  proven by a byte-identical fixture. "This needs a new parse branch" is not a
  §4.2 violation. "This needs a second document model" is.
- §4.3 forbids evidence and banks leaving the disk. It is not a general
  ban on networked components; the network rule is `CLAUDE.md:57`: the core loop
  **degrades, never blocks**, which is a resilience requirement, not an offline
  mandate.
- §4.1 forbids a model inventing correctness, session state, evidence, or early
  keyed disclosure. It is not a ban on a model producing or directly presenting
  ordinary approved teaching material; the gate applies to assessment authority.

**Bank-authored JavaScript is refused** (`REQUIREMENTS.md` VIS-01,
`UI-SPEC.md:609`). This is real, it is the correct ground for rejecting per-lesson
executable content, and it is not the same thing as a no-JS rule.

**Supply chain.** Dependencies are permitted, so the absence of dependencies is no
longer a mitigation. Every third-party artifact, including each library, font,
JS bundle, and toolchain, is vendored at a pinned version with a recorded checksum and a named
license review, following the KaTeX precedent (`09-03-PLAN.md`). A threat table
that accepts supply-chain risk on the grounds that "no dependency is installed" is
stale and must be rewritten.

**Citation discipline, binding on every artifact.** Any rejection that names a
Directive section quotes the sentence it relies on. A citation that cannot be
quoted is not a citation, and the finding it supports is void. If the honest reason
is cost, taste, or churn, say cost, taste, or churn. Those are legitimate reasons
and they survive being stated plainly.

## 5. Execution split

**Claude plans. DeepSeek V4 executes.**

- This session and every planning session: `/gsd-discuss-phase`, `/gsd-ui-phase`,
  `/gsd-plan-phase`, `/gsd-phase`, research. Never `/gsd-execute-phase`.
- Handoff to DeepSeek V4 for execution, run **sequentially**. A fork-base guard
  degrades worktree parallelism to one plan at a time here regardless of config.
- GSD state is shared on disk, so the handoff is "stop and tell them," not an export.

The reason for the split is the point of the whole exercise: UI and other
consequential decisions get made by the more capable model **before** any code is
written, so execution is transcription rather than judgment. A plan that leaves a
design decision to the executor has failed at its job.

**The lesser-model executor bar (added 2026-08-14).** The executor for the
next milestone is a Sonnet-class model, and the split above holds only if
every plan meets a concrete legibility bar. A plan is ready when a competent
model with no chat history and no repo intuition can complete it, which means
each plan states, explicitly and in the plan itself:

1. The exact files to create or modify, by path.
2. Every command to run, verbatim, with its expected output or exit code.
3. Every user-visible string, error message, and copy decision, written out,
   never "an appropriate message".
4. The fixture or test that proves each task done, named before the task, and
   the degraded-state behavior it must also prove.
5. The design decisions already made, cited to their decision record, so the
   executor never re-derives or re-litigates one.
6. What is explicitly out of scope, so adjacent temptations are refused by
   the plan rather than by executor judgment.

The test to apply before handing a plan off: find any sentence a reasonable
executor could implement two different ways; either decide it in the plan or
name it a checkpoint. Discussion documents can hold nuance; plans cannot.

This bar is codified as a standing template in `.planning/PLAN-TEMPLATE.md`
(added 2026-08-14); the Phase 13.9 plans are its reference exemplars. New
plans start from the template, not from memory of an older plan's shape.

## 6. What a phase owes before it is planned

In order, per phase:

1. `/gsd-discuss-phase <n>`: surface the gray areas, apply §2 and §3 to each.
2. `/gsd-ui-phase <n>`: only if the phase has a learner-facing surface.
3. `/gsd-plan-phase <n>`: the executable plans.

A plan may not invent a design decision the discuss step did not record, and may
not defer one to execution.

## 7. Ideaboarding and user-vision interpretation

Rough user ideaboarding is product evidence, not disposable chat. Record it
verbatim and additively in `.planning/USER-VISION.md` before normalizing it into
requirements or phase language. A dated interpretation note may sit directly
below the quotation so the user can inspect the translation, but it must remain
visibly separate from the user's words.

Each interpretation records its status, current meaning, open questions,
planning effect, and relationship to earlier entries. If later ideaboarding
changes an earlier interpretation, preserve both quotations and add a new dated
note. Mark the old interpretation partly superseded or superseded, name what
changed, and link the decision artifact. Never rewrite history into artificial
consistency.

For consequential product ideas, ideaboarding precedes phase discussion. The
planning agent first expands the possibility space, identifies assumptions and
research questions, separates teaching value from visual novelty, and records
alternatives. Only then may it narrow the ideas into a phase contract.

## 8. Learning UI planning split

> **Superseded 2026-08-13 (kept for history, synthesis section 15).** The prior
> two-phase split read: "Logical experience design and visual system design are
> separate obligations. For the next milestone, Phase 16 defines the learner
> flow, lesson capability catalog, question-purpose matrix, semantic authored
> representation, interactions, accessibility, media policy, and agent authoring
> contract. Phase 17 defines the visual language and implements the comprehensive
> UI against those approved contracts." That coarse split placed some Phase 16
> discoveries after Phase 14 format commitments. It is replaced by the subphase
> dependencies below, which preserve the same logical-before-visual order.

Logical experience design and visual system design remain separate obligations.
The high-level order is unchanged: durable course and file semantics precede AI
course direction, and logical learning contracts precede visual productization.
The four broad phases are divided into subphases (not a new top-level phase).
Each subphase freezes shared interfaces and may register multiple composing
capabilities; optional or expensive capabilities stay in the runway rather than
being cut.

| Subphase | Deliverable | Depends on | Freeze gate |
|---|---|---|---|
| 14A identity, lifecycle, operation | Stable IDs, revisions, fingerprints, operation journal, link/import/move/edit/supersede semantics, atomic recovery | Shipped parser and runtime | File fault and external-edit tracer |
| 14B graph and course package | Typed graph kernel, outline projection, source and treatment bindings, versions, rights, minimal package | 14A | Three-domain graph tracer, clean restore, authorability review |
| 15A director and treatment policy | Treatment recommender, source scope, rights and egress, autonomy levels, checkpoints | 14B | Four-subject recommendation review |
| 15B quality, blueprint, acceptance | Blueprint fidelity, course audit, accepted revision, staleness and dependency impact | 15A | Lesson plus practice acceptance tracer |
| 16A semantic capability and activity | Lesson roles, activity-purpose matrix, capability profiles, media and citation policy | 14B, assessment runtime | Portable rich-lesson stress corpus |
| 16B IA, modes, recovery | Core loops, routes, resume, jobs, approvals, offline/help/error states | 14A, 16A | Full storyboard and interruption scenarios |
| 16C strategies, notes, convergence | Notes, learner artifacts, finite strategies, progress comprehension, legacy upgrade | 14B, 16A, 16B | Cross-subject missing-feature suite |
| 17A visual system and components | Tokens, hierarchy, responsive shell, accessible primitives | 16B, 16C | Same-flow visual comparison and accessibility QA |
| 17B production vertical tracer | Polished unit from discovery through restore | All prior | End-to-end gates G1 through G11 |

`/gsd-ui-phase` work for a learner-facing surface is owed at the subphase that
introduces it (16B, 16C, 17A, 17B), not at a single monolithic Phase 17.

Competitor research, including NotebookLM, Brilliant, Albert, and other current
learning or source-grounded tools, records patterns, benefits, weaknesses, and
applicability. It does not copy protected content, assume popularity proves
learning value, or turn itembank into a clone. Every candidate capability must
answer what it teaches, when it helps, how it degrades in the authored file,
how it works by keyboard, touch, and screen reader, and how an agent authors and
validates it.

Question design research must classify purpose and cognitive demand before
choosing a response widget. Questions for prediction, noticing, retrieval,
explanation, comparison, diagnosis, practice, transfer, and formal assessment
may need different feedback and evidence behavior even when they share the
same visible control.

## 9. Reusable user-vision method

The vision-capture workflow should be extractable into a project-neutral skill,
but it is planned separately from itembank product code. The reusable method
must support verbatim additive capture, dated interpretations, open questions,
conflict and supersession handling, links to binding decisions, and an audit
that detects silent drift between vision and plans. Before publishing such a
skill, test it in at least one other project and remove itembank-specific paths,
phase numbers, runtime rules, and vocabulary.

## 10. What enters the user vision

The reusable workflow carries this rule verbatim:

> Do not put everything into USER-VISION.md. Put every meaningful statement
> into a capture funnel, but promote only statements about desired outcomes,
> experience, scope, values, boundaries, users, success, or unresolved product
> direction into the durable vision. Implementation guesses and research leads
> should stay linked in research or planning notes unless they become a user
> preference or product commitment.

Capture broadly, promote selectively. A statement belongs in
`.planning/USER-VISION.md` when it expresses one or more of these:

- The outcome the product should create or the problem it should solve.
- The intended user, context, experience, workflow, or quality bar.
- A product value, boundary, non-negotiable, preference, or success condition.
- A meaningful expansion, narrowing, conflict, reversal, or unresolved product
  question.
- Ideaboarding whose loss would make a later plan misunderstand the user's
  intent.

Do not promote raw links, competitor feature inventories, implementation
guesses, library choices, phase numbers, task assignments, temporary debugging
facts, or research conclusions merely because they appeared in chat. Put those
in research briefs, decision records, requirements, plans, or operational notes
and link them from an interpretation when relevant.

When uncertain, preserve the raw statement in a dated vision inbox or session
capture first. Review it for promotion after the ideaboarding pass. Never force
the user to classify thoughts while thinking aloud, and never discard a
statement only because it is rough, repetitive, or contradictory.
