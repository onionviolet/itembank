# Features worth considering and more

Created 2026-09-06. Status: reusable audit brief, not an implementation plan.
Owner: the next agent running the feature opportunity audit.
Origin: `USER-VISION-INBOX.md`, "feature opportunities and future additions".
Disposition records: `IDEA-LEDGER.md`, IL-20260906-01 through IL-20260906-05.

## Saved candidate ideas

These are assistant recommendations that the user asked to preserve and audit.
They are not verified implementation gaps or approved scope additions.

| ID | Candidate | Concrete learner experience | Question to audit |
|---|---|---|---|
| F1 | "I'm stuck" detour | Select a confusing passage, open a definition, prerequisite refresher, worked example, or simpler explanation, then return to the same place. | Can existing lesson, source, and help capabilities deliver this complete flow? |
| F2 | Personal confusion notebook | Save "I keep confusing X with Y", attach examples, and revisit the distinction through comparison practice. | Can notes and misconception practice connect without turning a learner note into assessment authority? |
| F3 | Learn to build my notes | Predictions, explanations, selected highlights, and corrected reasoning accumulate into an editable study document. | Does the existing note workflow preserve authorship, citations, edits, and useful plain-file output? |
| F4 | Transfer challenges | Apply an idea in a changed situation, diagnose a broken example, or explain when a rule stops working. | Are transfer activities authored, reachable, and evaluated appropriately across subjects? |
| F5 | Time-aware continuation | Choose ten minutes, a full lesson, or review only, see the reason for the proposed activity, and return to the exact stopping point. | Can existing scheduling and resume behavior accommodate a time budget without inventing completion or mastery? |

An initial prototype candidate is F1 plus F3: read, encounter confusion, take a
short explanatory detour, write an explanation, and retain it in learner notes.
Audit existing support before deciding whether this needs a new prototype.

## Copyable audit prompt

Audit itembank for **features worth considering and more**. Cover what already
exists, what is planned for the future, worthwhile additions on top of those
plans, and useful capabilities or learner needs we have overlooked. Go beyond
the five saved candidates in this file. Produce an evidence-backed opportunity
review, not implementation work or an automatic milestone expansion.

### Establish the actual baseline

Read `AGENTS.md`, `.planning/AGENT-WORKFLOW.md`, and the compact current-position
sections of `.planning/STATE.md` and `.planning/REACH-MILESTONE.md`. Follow the
binding `.planning/SOURCE-TO-COURSE.md`, relevant quotations in
`.planning/USER-VISION.md`, the inbox, and planning directives. Use
`.planning/ROADMAP.md` for active sequencing. Treat the root `ROADMAP.md` as
historical context where it disagrees with current plans.

Search the existing idea ledger, phase seeds, requirements, feature atlas,
learning-program landscape, synthesis, and recent absorption research before
proposing replacements or repeating research. Locate symbols before reading
code. Sample focused implementations, tests, and verification evidence to
distinguish a documented promise from a usable learner flow. State what you did
not inspect. Do not infer working UI from a completed plan or passing backend
test alone.

Classify each opportunity on separate axes:

- Delivery: working end to end, partially working, backend-only, planned,
  previously considered, new candidate, or unknown.
- Timing: current milestone obligation, future planned work, optional extension,
  or open research question.
- Evidence: observed behavior, source-backed fact, inference, or recommendation.

Keep feature delivery status separate from the ledger's durable disposition.
Distinguish a missing capability from an existing capability that lacks a usable
entry point, authoring support, discoverability, or integration.

### Examine breadth and coherent journeys

Audit F1 through F5 individually and their combined reading-to-notes journey.
Then examine the complete course lifecycle: first use, source discovery and
binding, course construction, reading and guided learning, note creation,
practice and tests, feedback, evidence and remediation, return after absence,
maintenance, and export or restore.

Look for expected baseline behavior, valuable enhancements, and distinctive
possibilities. Consider source-side navigation and comparison, annotation,
terminology, worked examples, simulations, alternative lesson styles, learner
explanations, cumulative review, confidence calibration, accessibility,
phone use, offline use, search, and trustworthy recovery. These are audit
dimensions, not presumed gaps or commitments.

Explore alternatives before narrowing. Consider different subjects and learner
goals. Check how features connect and whether a learner can complete the job
without an agent manually repairing the experience. Identify authoring and
review capabilities needed to make learner-facing features useful.

Reuse existing research first. Browse current primary sources when checking
external product behavior or a genuinely unanswered research question. Cite
direct sources and their dates. Explain the user benefit of an external pattern
instead of copying a competitor's feature list. Do not claim learning efficacy
without supporting evidence.

### Evaluate and route each opportunity

For every substantial candidate, record a stable ID, learner job, concrete
before-and-after flow, existing overlap with exact file or symbol references,
remaining gap, expected benefit, evidence strength, dependencies, maintenance
cost drivers, and the smallest useful verification or prototype. State what
would falsify the benefit. Label cost estimates as estimates.

Identify the durable object, owner, source of truth, scoring or disclosure
boundary, rights and egress implications, accessible and plain-file behavior,
offline behavior, staleness and conflict handling, and recovery where relevant.
Apply current rules and clarifications. Do not revive retired restrictions.

Recommend a disposition and distinguish it from approval. Reuse existing ledger
entries when the idea already exists. Preserve viable future breadth with a
dependency and revisit trigger. Any proposed rejection must cite the exact
current conflicting rule, evidence, retained alternative, and reconsideration
condition. Do not reject something merely because it is outside the current
milestone or expensive.

### Deliverables and stopping point

Write one dated report under `.planning/research/` named
`YYYY-MM-DD-feature-opportunity-audit.md`. Include an evidence inventory, a
coverage matrix of current and future capabilities, the opportunity register,
and a shortlist of at most five next actions ranked by learner value,
dependencies, and uncertainty. Keep the broader inventory in the same report.
Include concrete prototype acceptance criteria for the strongest opportunities.

Update the existing idea ledger with links and evidence for genuinely new
proposals. Preserve old records and unresolved questions. Keep user quotations
separate from interpretations. Run the applicable vision audit and required
planning checks. Report unrun checks and evidence limits honestly.

The user has authorized an audit and reviewable planning records. Do not
implement features, change binding scope, create public issues, commit, or push
as part of this prompt. Leave a clear proposed route into an existing phase,
future seed, or research follow-up for each shortlisted opportunity.

## Capture verification

This brief preserves all five suggestions and the broader future-feature audit
request. Existing implementation coverage remains unverified. The current reach
milestone is not expanded by this capture. The inbox holds the user's exact
wording, and the existing ledger holds the candidate dispositions.
