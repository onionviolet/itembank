# Feature and learning experience overhaul

Date: 2026-09-18. Status: research and proposed integration plan. Owner: root.

## Original request

> overhaul look at their features and flow and more and then plan integration and more, since feature parity and exceeding has not been reached yet, also considering what it takes to create UI stuff and diagrams or explainers like brilliant does and more, improve this prompt before running in parallel at the astra level

Clarifications from this conversation:

> it was a long time ago, it was the other github stuffs and LMS that we can benefit from absorbing

> and th ecompetetor short list too

## Refined execution prompt

Audit Itembank against the combined historical LMS, GitHub, and competitor
research. Produce one evidence-backed integration plan for substantially better
features and learner flows. Compare complete tasks and feature depth across
course discovery, exact resume, reading, authoring, learning, practice, testing,
feedback, notes, review, evidence, recovery, export, and maintenance.

Define parity per observable learner task. Identify what is implemented,
partial, prototype-only, missing, or unverified in Itembank. Distinguish current
source inspection, live interaction, official documentation, and dated research.
Evaluate present fitness independently of sunk effort. Do not assert overall
parity or superiority from a feature list or screenshots.

Explain what producing Brilliant-quality diagrams and interactive explainers
requires: semantic content, reusable visual primitives, linked representations,
staged explanations, simulations, code tracing, meaningful question families,
an authoring and preview workflow, portable fallback, accessible interaction,
asset creation, pedagogical review, and maintenance. Estimate effort as an
explicit assumption and distinguish platform effort from per-lesson effort.

Synthesize the evidence into shared capabilities, concrete module seams,
dependency order, migration and rollback, acceptance tasks, and one detailed
first runnable slice. Preserve later opportunities as seeds with dispositions.
Explain what would demonstrate parity and what would demonstrate an advantage.

## Execution and boundaries

Three Astra low research lanes own `LMS-FLOWS.md`, `COMPETITORS.md`, and
`INTERACTIVE-TEACHING.md` in this directory. Root owns this brief, the live-code
gap analysis and `INTEGRATION-PLAN.md`. Read AGENTS.md and the binding
AGENT-WORKFLOW.md before work. Read relevant SOURCE-TO-COURSE.md sections and
prior research before new searches. Use current primary sources and inspect
representative repository paths where useful. Public sources may be fetched.
Private course content is outside this research and receives no remote upload.

The tree has concurrent changes. Each agent writes only its named new report
using apply_patch. No commits, pushes, branch changes, production edits,
installation, or modifications to the ongoing UI showcase. Preserve other work.
This resolves the older workflow's commit-per-report language under the current
portable rule to commit only when asked.

## Required inputs

- [Older LMS and repository flow scope](../../notes/2026-09-07-home-and-transition-ui-scope.md)
- [Earlier source absorption](../2026-09-05-open-source-absorption.md)
- [Competitor landscape](../competition-2026-09-08/LANDSCAPE.md)
- [Prior absorption and implementation claims](../competition-2026-09-08/ABSORPTION.md)
- [Current UI renewal](../ui-renewal-2026-09-18.md)
- [Current code-depth audit](../code-question-depth-audit-2026-09-16.md)

## Acceptance gate

All three reports exist and cite primary evidence with access date and evidence
class. Every listed candidate has a route or explicit scope reason. Root checks
the actual artifacts, reconciles disagreements, and maps recommendations to
current code and existing owners. The plan names one ready slice, later seeds,
observable tasks, failure conditions, migration, recovery and unverified gates.
No runtime, learning-efficacy, human-accessibility, or installed-app parity claim
is established by this planning work. Documentation links and project quick
preflight are checked. Vision capture records the exact request separately.

## Operation record

Read root: this repository and the previously identified memory records.
Write scope: new reports here and append-only vision capture in the existing
vision and inbox files. Expected base for new reports: absent. Existing vision
entries use unique patch context and retain all prior bytes. Public research
queries describe products and technical capabilities only. Validation and any
conflicts are recorded in the integration plan. Undo removes this research
directory and only this pass's uniquely titled vision entries. No accepted
course, bank, source, learner evidence, or production default changes.
