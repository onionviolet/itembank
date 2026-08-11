# Planning Directives — standing rules for every GSD session on this project

- **Created:** 2026-08-10
- **Status:** binding on every `/gsd-discuss-phase`, `/gsd-ui-phase`, `/gsd-ai-integration-phase`, and `/gsd-plan-phase` run
- **Supersedes:** nothing. Sits alongside `.claude/CLAUDE.md` Constraints (as amended
  2026-08-09) and `.planning/UI-SPEC.md`.

This file exists because the same instructions were being re-stated in every session
and losing fidelity each time. Any planning agent reads this before it reads the phase.

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

---

## 2. The autonomy rule

**Keep going.** Do not stop a planning session to ask a question you can answer
from the codebase, the research artifacts, or a defensible default. Record the
assumption and continue.

Stop only for these, and for nothing else:

1. An action that is **hard to reverse** — an append-only evidence field, a
   published schema, a format decision other phases will build against.
2. A choice that would **lower quality** whichever way you guess, where the
   research contains no verdict.
3. A conflict with one of the five non-negotiables in §4.

Everything else: decide, write down the reasoning, move on. A blocking question
costs a session round-trip; a recorded assumption costs one line.

## 3. The conflict rule — build both, let the learner pick

When two designs both look defensible and neither is clearly wrong, **do not
arbitrate**. Implement both behind one interface and make the choice a setting.

This is affordable here specifically because of the Extensibility Rules in
`ROADMAP.md` — a second implementation of an existing interface is a registration,
not a fork. It stops being affordable, and the rule stops applying, when the two
options need **two parsers, two scorers, or two evidence stores**. That is when you
pick one and say why.

Applies directly to: lesson styles, hint pacing, scheduler algorithm, refusal
copy, reading layout, selection strategy, TTS engine, model backend.

## 4. What never bends

Everything in `.claude/CLAUDE.md` bends per the 2026-08-09 amendment **except**:

1. The **runtime**, not a model, decides what reaches the learner.
2. Exactly **one parser, one scorer, one evidence store**.
3. Evidence and banks stay on disk. No telemetry.
4. Format changes are **additive** — a bank not using a new block parses unchanged,
   proven by a byte-identical fixture, not promised.
5. The accessibility gates in `.planning/UI-SPEC.md`.

A research finding or a design idea that violates one of these is rejected on that
basis alone, however good it is otherwise.

## 4a. Constraint basis — what binds, what does not, and how to cite it

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
  the one parser's grammar — additive growth is §4.4's subject and is permitted,
  proven by a byte-identical fixture. "This needs a new parse branch" is not a
  §4.2 violation. "This needs a second document model" is.
- §4.3 forbids evidence and banks leaving the disk. It is not a general
  ban on networked components; the network rule is `CLAUDE.md:57` — the core loop
  **degrades, never blocks**, which is a resilience requirement, not an offline
  mandate.
- §4.1 forbids a model deciding what reaches the learner. It is not a ban on a
  model *producing* anything; the gate is who accepts.

**Bank-authored JavaScript is refused** (`REQUIREMENTS.md` VIS-01,
`UI-SPEC.md:609`). This is real, it is the correct ground for rejecting per-lesson
executable content, and it is not the same thing as a no-JS rule.

**Supply chain.** Dependencies are permitted, so the absence of dependencies is no
longer a mitigation. Every third-party artifact — library, font, JS bundle,
toolchain — is vendored at a pinned version with a recorded checksum and a named
license review, following the KaTeX precedent (`09-03-PLAN.md`). A threat table
that accepts supply-chain risk on the grounds that "no dependency is installed" is
stale and must be rewritten.

**Citation discipline, binding on every artifact.** Any rejection that names a
Directive section quotes the sentence it relies on. A citation that cannot be
quoted is not a citation, and the finding it supports is void. If the honest reason
is cost, taste, or churn, say cost, taste, or churn — those are legitimate reasons
and they survive being stated plainly.

## 5. Execution split

**Claude plans. DeepSeek V4 executes.**

- This session and every planning session: `/gsd-discuss-phase`, `/gsd-ui-phase`,
  `/gsd-plan-phase`, `/gsd-phase`, research. Never `/gsd-execute-phase`.
- Handoff to DeepSeek V4 for execution, run **sequentially** — a fork-base guard
  degrades worktree parallelism to one plan at a time here regardless of config.
- GSD state is shared on disk, so the handoff is "stop and tell them," not an export.

The reason for the split is the point of the whole exercise: UI and other
consequential decisions get made by the more capable model **before** any code is
written, so execution is transcription rather than judgment. A plan that leaves a
design decision to the executor has failed at its job.

## 6. What a phase owes before it is planned

In order, per phase:

1. `/gsd-discuss-phase <n>` — surface the gray areas, apply §2 and §3 to each.
2. `/gsd-ui-phase <n>` — only if the phase has a learner-facing surface.
3. `/gsd-plan-phase <n>` — the executable plans.

A plan may not invent a design decision the discuss step did not record, and may
not defer one to execution.
