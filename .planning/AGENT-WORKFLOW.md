# Agent workflow for source-to-course work
**Status:** binding workflow for Codex, Claude Code/Cowork, local agents, and
other agent clients working on course, source, lesson, assessment, UI, planning,
research, migration, or product-direction tasks.

This workflow exists so a capable agent can continue the project without
flattening the user's vision, repeating research, silently dropping ideas, or
turning provisional findings into product commitments.

## 1. Authority and reading order

Read these before consequential work:

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
