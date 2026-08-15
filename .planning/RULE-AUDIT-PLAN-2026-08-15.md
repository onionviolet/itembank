# Rule audit pass: plan (2026-08-15)

Requested by Weibao 2026-08-15 after the one-scorer reword (IDEA-LEDGER
IL-20260815-05) surfaced five more misreadable rules (IL-20260815-06). This
plan covers the full audit: every binding rule, every past pitched feature,
and a replanning gate at the end. It is a planning document; execution can be
handed to any agent client under the normal handoff contract.

## Goal

Answer three questions with evidence, and fix what the evidence supports:

1. Which binding rules, read literally, block features the product wants?
2. Which past ideas were rejected, deferred, or watered down by a rule that a
   clarified reading would have allowed?
3. Is rule friction a real drag on development velocity, and if so, is it the
   product rules (invariants) or the process rules (ledgers, manifests,
   verbatim records)?

## Scope: rule sources to audit

Ranked; audit in this order.

1. `AGENTS.md` (15 non-negotiable and course rules, object and authority
   summary)
2. `.claude/CLAUDE.md` (constraints, runtime invariant, operation summary;
   must stay consistent with AGENTS.md)
3. `.planning/SOURCE-TO-COURSE.md` (binding milestone contract)
4. `.planning/AGENT-WORKFLOW.md` and `.planning/PLANNING-DIRECTIVES.md`
   (process rules)
5. `.planning/research/phase-16/14-synthesis.md` sections 2, 6, 10, 11, 12
   (source of the mirrored summaries) and `.planning/UI-SPEC.md`
   (accessibility gates)

## Method

### Step 1: rule inventory (about 2 hours, driver: rule count)

Extract every imperative rule from the sources above into one table:
rule text, source and line, intent (one sentence), literal misreading (one
sentence, or "none"), feature class it could block, and a verdict of keep,
clarify, or amend. The IL-20260815-06 findings are rows one through seven,
already resolved; the table completes the sweep the spot check started.

### Step 2: retrospective feature audit (about 3 hours, driver: ledger size)

For every rejected, superseded, deferred, or backburnered idea in the
rejection ledger (synthesis 12.4), the DECISIONS files, USER-VISION-INBOX.md,
the research briefs, and the roadmap phase notes:

- record the cited blocking rule;
- re-test the rejection against the clarified 2026-08-15 rule readings;
- classify: rejection still stands, rejection weakens (reconsideration
  condition now met), or rejection was wrong (rule misread at the time).
- flag any rejection whose real reason was process weight or simplicity
  alone, which the project's own standard forbids.

The initial evidence sweep completed 2026-08-15; its aggregate, flags, and
revisit candidates are recorded in
`.planning/research/2026-08-15-rejection-rule-tally.md` and seed this step.

### Step 3: friction measurement (about 1 hour, driver: honesty)

Separate the two candidate friction sources and look for evidence of each:

- Product rules (one scorer, disclosure gating, on-disk evidence): cheap at
  development time, expensive only if misread. Evidence: step 2 results.
- Process rules (append-only ledgers, verbatim vision records, per-operation
  manifests, disposition taxonomy, verbatim-quote separation): paid on every
  planning session regardless of outcome. Evidence: time spent per planning
  artifact, artifact count per shipped feature, and any handoff that stalled
  on process rather than substance.

Deliverable: a one-page verdict naming which rules earn their cost, which
need a lighter tier for low-stakes work, and which are noise.

### Step 4: apply and replan (about 2 hours, driver: findings count)

- Apply clarify/amend verdicts from step 1 as dated additive notes, the same
  pattern as IL-20260815-05 and -06, mirrored in AGENTS.md and CLAUDE.md.
- Re-open any wrongly rejected idea from step 2 through the normal
  disposition funnel (new IDEA-LEDGER entries citing the original rejection).
- Replanning gate: if step 2 re-opens ideas that belong in the current
  milestone, or step 3 finds a process rule that should be tiered, take the
  result to the roadmap as a proposed phase edit rather than editing
  ROADMAP.md unilaterally. Weibao decides scope changes.

## Deliverables

1. `RULE-AUDIT-2026-08-15.md` (or dated successor): the rule table, the
   retrospective classification, and the friction verdict.
2. Dated additive clarifications in AGENTS.md and CLAUDE.md for every
   clarify/amend verdict.
3. New IDEA-LEDGER entries for every re-opened idea.
4. A proposed roadmap delta, if the replanning gate fires.

## Exit criteria

- Every rule in the five sources has a row and a verdict.
- Every ledger rejection has been re-tested against clarified readings.
- No rule text was deleted or weakened silently; every change is a dated
  additive note with a ledger citation.
- The friction question has a written answer with named evidence, not a vibe.

## Out of scope

- Runtime behavior changes (scorer versioning in evidence is tracked
  separately in IL-20260815-05, audit item 2).
- Editing the Phase 16 synthesis itself; it is the historical record.
- Rewriting USER-VISION.md or any verbatim quotation.
