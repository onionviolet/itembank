# Agent workflow for source-to-course work
**Status:** binding workflow for Codex, Claude Code/Cowork, local agents, and
other agent clients working on course, source, lesson, assessment, UI, planning,
research, migration, or product-direction tasks.

This workflow exists so a capable agent can continue the project without
flattening the user's vision, repeating research, silently dropping ideas, or
turning provisional findings into product commitments.

## 1. Authority and reading order

Use the reading mode below before consequential work. The numbered list is an
authority map, not a requirement to load every document in full:

- Planning starts with `STATE.md` front matter and current-position table,
  the active milestone, and the owning phase context or seed. Search the
  documents below for the relevant vision entries, obligations, and decisions.
  Read those sections and expand only when a dependency or conflict requires it.
- Execution starts with `EXEC-CONTEXT.md` and the assigned plan. Read the
  exact cited contract sections when the plan leaves a material question open.
- A whole-vision audit reads every quotation and its applicable interpretation.
  A bounded refinement states which entries and plans it sampled and does not
  claim exhaustive coverage.

This implements `PLANNING-DIRECTIVES.md` B4. User quotations and binding rules
remain authoritative even when a compact entry point omits them.

1. `USER-VISION.md` for the user's promoted words and intent.
2. `USER-VISION-INBOX.md` for meaningful ideas awaiting promotion or routing.
3. `SOURCE-TO-COURSE.md` for the current binding product contract.
4. `PLANNING-DIRECTIVES.md` for planning and ideaboarding rules.
5. `research/phase-16/14-synthesis.md` for the reconciled product model and
   evidence routes.
6. `REQUIREMENTS.md`, `ROADMAP.md`, and `UI-SPEC.md` for obligations, sequence,
   and learner experience.

User vision is authoritative for desired outcomes, values, and experience. It
does not by itself prove technical feasibility or learning efficacy. Research
tests possibilities. Accepted contract and requirements settle current product
direction. The runtime remains authoritative for scoring, assessment
disclosure, session state, and evidence.

When these sources disagree, do not choose the most recent summary by default.
Record the conflict, trace each statement to its origin, distinguish user intent
from inference and implementation, and resolve it in the owning document.

## 2. Capture and interpretation

Put every meaningful user statement into the capture funnel. Promote only
statements about outcomes, experience, scope, values, boundaries, users,
success, or unresolved product direction into `USER-VISION.md`.

Keep implementation guesses, links, tool choices, task mechanics, and research
leads in their owning research or planning documents unless they become a user
preference or product commitment.

Never rewrite the user's quotation. Add a dated interpretation below it with:

- Status.
- Current interpretation.
- Open questions.
- Planning effect.
- Relationship to earlier entries.

If later ideaboarding changes earlier direction, preserve both statements. Mark
the interpretation as extended, narrowed, conflicted, partly superseded, or
superseded. Link the decision that resolved it.

## 3. Ideaboarding before convergence

For consequential product questions, expand the possibility space before
writing requirements or implementation plans. Identify:

- User jobs and lifecycle stages.
- Alternative flows and representations.
- Expected baseline behavior.
- Competitor, niche, research, open-source, and publishing patterns.
- Accessibility, privacy, rights, portability, recovery, and maintenance.
- Missing states, failures, and edge cases.
- Which questions require evidence, a prototype, or direct user choice.

Do not confuse comprehensive consideration with simultaneous implementation.
Architecture may preserve broad possibility while work remains sequenced.

## 4. Research waves

Each delegated research task has one bounded question and one named output
file. It reads prior research first, uses current primary sources for product
behavior, distinguishes fact from inference and recommendation, records source
dates, and writes findings to disk rather than leaving them in chat.

Run parallel tasks only when their outputs are independent. After a wave:

1. Verify every task produced the named artifact.
2. Verify its commit contains only that artifact.
3. Integrate the atomic commits into the main project.
4. Run a coverage audit for missing, duplicated, or ownerless questions.
5. Launch synthesis only after all required inputs are present.

Synthesis reconciles reports. It does not concatenate them. It must identify
agreement, conflict, evidence quality, unsupported assumptions, shared
primitives, authority, ownership, dependencies, failure conditions, and exact
change proposals.

## 5. Product coherence and dispositions

Coalescing means organizing viable breadth into one product architecture. It
does not mean deleting ideas for minimalism.

Every substantial proposal receives one disposition:

- **Core:** required shared behavior or foundation.
- **Registered:** a composable capability, mode, or strategy with the same
  authority, accessibility, permission, recovery, and maintenance contracts.
- **Prototype:** useful but awaiting evidence or interaction validation.
- **Backburner:** viable but not timely; retain dependency, cost driver, and
  revisit trigger.
- **Deferred:** waiting for named evidence, authority, or external state.
- **Superseded:** its purpose survives through a better mechanism.
- **Rejected:** conflicts with a named product rule or quality requirement.

The rejection ledger is append-only. Each rejected item retains its original
proposal and origin, evidence considered, exact reason, conflicting rule,
alternatives retained, date, and reconsideration condition. Never silently
delete or omit a rejected idea. Simplicity alone is not a rejection reason.

**Tiered record shape (adopted 2026-08-15, archive/RULE-AUDIT-ROADMAP-DELTA
proposal 1, approved by Weibao).** Record shape scales with consequence:

1. Reversible, low-stakes work records intent, owner, next action, and undo
   when a mutation occurs. It does not require a permanent disposition row or
   a full operation manifest.
2. Consequential proposals and durable writes use the existing disposition,
   authority, rights, validation, recovery, and accepted-revision controls.
3. Binding formats, assessment authority, rights or egress changes, hard
   rejections, and milestone scope use the full evidence, prototype, ledger,
   readiness, and direct-user-decision gates.

The tier changes documentation burden only. It never relaxes one-parser and
one-scorer authority, accessibility, data residency, rights,
compare-and-swap mutation, validation, or recovery rules. When two readings
disagree about an operation's tier, use the higher tier and record the
disagreement.

Additionally, from the same audit: a rejection must quote the currently
binding rule text it relies on. A rejection citing a retired preference or a
rule number without its text is invalid (stale-authority drift, the measured
failure mode in `archive/RULE-AUDIT-2026-08-15.md`).

## 6. Object and authority check

Before accepting a feature or plan, name:

- Actor and owner.
- Durable object and source of truth.
- Derived views or disposable indexes.
- Authority boundary.
- Lifecycle and revision state.
- Provenance and rights.
- Degraded, offline, stale, conflict, and recovery behavior.
- Accessibility and localization behavior.
- Validation gate and maintenance owner.

Keep these state axes separate: existence, validation, acceptance, publication,
completion, evidence, retention, staleness, conflict, rights, and availability.
Do not compress them into one progress or mastery score.

Learner notes remain learner-owned and cannot silently become accepted source,
lesson, answer key, score, or mastery evidence. Presentation state is not
authorization. Derived HTML, caches, and indexes are not canonical truth.

## 7. File operations and accepted revisions

Find and link existing work before creating replacements. Search only approved
roots. Linking and editing in place are the default. Moving, copying, importing,
converting, superseding, or deleting require an explicit operation and clear
user consequence.

Mutations use expected-base fingerprints, reviewable diffs, atomic writes, an
operation journal, and recoverable prior revisions. An external edit creates a
stale or conflict state, never a silent overwrite. Preserve stable identity,
provenance, objective links, rights, and accepted revision across moves and
upgrades.

Every operation declares read scope, write scope, remote egress, rights basis,
expected outputs, validation, and recovery. Discovery never grants mutation or
remote-upload authority.

## 8. Agent plans and execution

Every accepted recommendation names an owner, evidence class, dependency,
verification method, failure condition, degraded state, migration effect,
documentation obligation, and maintenance cost.

Use reversible prototypes before durable commitments involving graph schemas,
semantic lesson grammar, strategy registries, executable sources, complex
visual interactions, synchronization, or interchange formats.

Before execution, run the implementation-readiness audit defined in
`research/phase-16/14-synthesis.md`. Implementation plans must trace backward to
vision and evidence and forward to a verification gate. Do not leave product or
interaction decisions to the executor.

## 9. Agent handoff and reporting

A handoff records:

- Objective and current status.
- Authoritative files read.
- Files and commits produced.
- Decisions, assumptions, and dispositions.
- Unresolved conflicts and user decisions.
- Verification completed and still required.
- Exact next action.

Chat is not the durable record. Decisions land in the owning files during the
same workflow. A future agent should be able to reconstruct why the project is
moving in its current direction without reading old conversation transcripts.

### Budget and continuation, refined 2026-09-06

Keep one current next action in `STATE.md` and decisions in their owning phase.
Link execution evidence instead of copying it into the state, roadmap, handoff,
and a new summary. Follow the existing B1 summary exception.

An executable plan names the smallest user-observable result, exact edit
locations, settled decisions, required checks, and evidence that would falsify
success. Detail the next ready plan only. Later phases keep seeds until their
inputs exist. Do not repeat settled research without a changed assumption,
observed defect, or named unanswered question.

Run targeted checks while editing and the required preflight before handoff.
If a required preflight already runs a named suite, reuse that result for the
same revision. Repeat checks after relevant changes or failures, not to create
a second verification transcript. Record failed and unrun gates honestly.

Report cost only when measured. Reuse available elapsed time, tool usage, or
token figures without adding a tracking system. Never claim estimated savings
as measured savings. Preserve quality gates and viable feature dispositions.

### Proportional workflow, refined 2026-09-06

GSD is an escalation ladder, not the default amount of process for every
change. Choose the cheapest execution shape that preserves the task's actual
acceptance gate:

1. Use a direct edit or `gsd-fast` for a one-sentence, reversible change with
   an immediate deterministic check. Do not create a plan, summary, research
   pass, or subagent chain.
2. Use one direct agent with a short evidence-gated packet for settled,
   multi-step implementation. The same agent investigates, edits, and runs the
   targeted gate when that keeps context local.
3. Use `gsd-quick --validate` when a bounded task needs durable state, an atomic
   plan commit, plan checking, and post-execution verification. Add discussion
   or research only for a named unanswered question.
4. Use the full discuss, research, plan, execute, review, and verify path for
   consequential format, scoring, disclosure, rights, recovery, sandbox,
   migration, or cross-system design decisions.

Subagents are exceptional. Use them only for disjoint write lanes, a required
independent review, protection of scarce coordinator context, or a specialized
tool or separate allowance. Keep one writer per file and one integrator. A
worker returns changed paths, exact gate results, assumptions, unresolved
defects, and one next action. The integrator inspects the diff and evidence
without repeating the worker's repository scan or broad test suite.

A large first-pass prototype is legitimate when it is reversible and its
purpose is to expose the learner experience quickly. Follow it with targeted
validation against observed risks. Do not require complete planning before a
prototype, and do not mistake generated breadth for accepted quality. Escalate
only the parts whose failed gate reveals ambiguity or consequence.

The 2026-09-06 structural baseline is evidence of process weight, not measured
token consumption: 67 GSD skill files contained about 7,000 lines, the active
planning tree contained about 219,000 lines and occupied 17 MB, and 638 commits
touched `.planning`. At the same revision, STATE recorded 212 completed plans
and only one real learner sitting. Use later measured tasks to determine
whether this proportional route reduces tool calls and context while retaining
correctness. Do not infer recurring behavioral failure from this one baseline.

### Continuous execution rule, refined 2026-09-06

Planning is preparation for the next observable run, not a queue that must be
fully expanded before implementation starts. Apply these rules to active
milestones:

1. Put a thin, visible end-to-end slice in front of the user before expanding
   breadth. Synthetic low-risk content is allowed when necessary. Never stub
   scoring, disclosure, accepted writes, rights, or recovery authority.
2. Bound planning for a settled packet to its observable result, exact symbols,
   smallest gate, and stop condition. If those fit in the phase context, do not
   create a separate research, plan, review, and summary chain.
3. Keep one ready packet and one active writer. Prepare only the next packet
   while a gate is running. Do not leave an executable packet idle while later
   seeds are being elaborated.
4. Run the cheapest representative check first. Add broader testing, another
   agent, or a stronger model only when that check exposes a named risk or the
   repository requires the independent gate.
5. Measure elapsed time from packet start to visible evidence, plus retries,
   tool calls, and defects found. Compare representative packets before
   changing the workflow again. Planning-file volume is not a success measure.

The `code_learner` comparison supports the first rule because one focused
activity achieved coherent interaction and broad generated content quickly.
Its missing runtime authority, durable evidence, dependency assurance, and
objective graph show where targeted hardening is still required. Preserve its
vertical-slice speed. Spend additional process only on the boundaries the slice
actually exercises.

## 10. Drift audit

Before closing a planning or product-direction pass, verify:

1. User statements were captured or deliberately routed.
2. Interpretations remain visibly separate from quotations.
3. Research conclusions did not silently become commitments.
4. Every viable idea has a durable disposition.
5. Rejections contain evidence and reconsideration conditions.
6. Agent instructions match the binding product contract.
7. Mirrored skills remain byte-identical.
8. No plan weakens the one-parser, one-scorer, one-evidence-store boundary.
9. No em dash characters were introduced outside verbatim quotations.

### Fresh evaluation of prior choices, added 2026-09-09

User authority: `USER-VISION.md`, "fresh evaluation of prior choices in future
audits", 2026-09-09. Apply this to future audits and design comparisons.

1. Define the current user need and evaluation criteria before using old
   solution choices to narrow the alternatives. Then reconcile with the exact
   earlier intent, evidence, and currently binding rules.
2. Treat prior acceptance and implementation as historical facts. Evaluate a
   credible alternative when a better fit is plausible. A choice that was best
   under earlier conditions may no longer be best now.
3. Record current fitness separately from switching cost, compatibility,
   maintenance, and recovery. Prior effort alone does not establish quality.
4. Preserve contrary evidence, failed experiments, unknowns, and the provenance
   of repeated claims. Multiple summaries of one observation are not
   independent confirmation. A passed technical gate does not establish human
   satisfaction or learning efficacy.
5. State what evidence would change the recommendation and when to revisit it.
   Keep the existing choice operational until an explicit revision changes it.
   Cite present authority when a boundary limits execution, and record a
   proposed boundary change when warranted rather than assuming it is eternal.

Record original rationale and later corrections together. No audit may claim
to be free of bias merely because it used this procedure.

The bounded [vision-reference architecture comparison](research/ui-and-project-memory-proposal-2026-09-09.md#fresh-architecture-evaluation-demonstration-2026-09-09)
demonstrates this procedure. Its recommendation preserves the local operating
choice and records missing evidence. It does not validate the proposed visual
label-withholding method or close human review gates.
