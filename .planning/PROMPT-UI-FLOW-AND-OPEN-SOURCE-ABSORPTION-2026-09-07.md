# Prompt: deepen UI flow and open-source learning-platform absorption

Paste the prompt below into a fresh Codex task opened on this repository. This
is a research and synthesis packet. It does not authorize application changes.

```text
Research and reconcile the future itembank learner UI as a complete lifecycle,
not a collection of attractive screens. Inspect current public product behavior,
official documentation, and relevant public repositories. Combine the evidence
with the project's existing audits. Save a source-grounded synthesis and a
prototype-ready transition contract. Do not implement production UI, modify
runtime authority, or copy code from external repositories.

STARTING AUTHORITY AND REQUIRED READING

Read AGENTS.md first. Follow .planning/AGENT-WORKFLOW.md. Work symbol-first and
state what large files were only sampled.

Read the current relevant sections of:

- .planning/STATE.md and .planning/REACH-MILESTONE.md
- .planning/USER-VISION.md and .planning/USER-VISION-INBOX.md, especially the
  2026-09-06 and 2026-09-07 UI entries
- .planning/SOURCE-TO-COURSE.md learner experience, extension seams, and phases
- .planning/notes/2026-09-07-home-and-transition-ui-scope.md
- .planning/UI-CHARACTER-AUDIT-2026-09-06.md
- .planning/AUDIT-REMEDIATION-PLAN-2026-09-06.md
- .planning/TRANSITION-AUDIT-SYNTHESIS.md
- .planning/research/2026-08-10-ui-inspiration-missing-surfaces.md
- .planning/research/phase-16/09-app-flow-information-architecture.md
- .planning/research/phase-16/10-visual-experience-system.md
- .planning/research/phase-16/14-synthesis.md
- .planning/research/2026-09-05-open-source-absorption.md
- .planning/research/2026-09-06-feature-opportunity-audit.md
- .planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
- .planning/phases/17A-visual-system-component-foundation/17A-UI-SPEC.md
- .planning/phases/17B-production-vertical-tracer/17B-UI-SPEC.md
- .planning/PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md
- .planning/IDEA-LEDGER.md entries IL-20260906-06, IL-20260906-08,
  IL-20260907-01, and IL-20260907-02

Treat planning claims as leads to verify against the live tree and current
product. Preserve unrelated dirty files. Discovery is read-only. Do not assume
that a route, helper, test, mockup, or requirement proves a usable flow.

RESEARCH QUESTION

What information architecture, home projections, navigation frame, transition
rules, completion states, and recovery behavior let one learner move coherently
through courses, sources, lessons, practice, quizzes, formal exams, feedback,
notes, evidence, agent operations, and return visits, while preserving local
files, assessment authority, accessibility, and exact resume?

EXTERNAL COMPARISON SET

Use current primary sources where possible. Inspect both visible behavior and
public implementation or test structure for:

- Canvas LMS: instructure/canvas-lms and instructure/instructure-ui
- Moodle web and mobile: moodle/moodle and moodlehq/moodleapp
- Open edX: openedx/frontend-app-learner-dashboard,
  openedx/frontend-app-learning, edx-platform, and documented frontend slots
- Kolibri: learningequality/kolibri, especially offline learner home, course
  unit navigation, quiz completion, interruption, and synchronization
- Khan Academy learner home and course mastery documentation
- Google Classroom homepage, class cards, due-soon modules, and classwork topics
- Duolingo path, unit guidebooks, review insertion, and current-position return
- At least three additional current systems that add a distinct pattern, such
  as Blackboard Ultra, Schoology, Brightspace, Coursera, FutureLearn, Moodle
  Workplace, Open Learning Library, Runestone, PrairieLearn, or H5P

Do not survey products merely to increase the count. Add a system only when it
contributes a distinct testable pattern, failure, or counterexample. Record
source URL, publication or revision date when available, access date, observed
fact, inference, recommendation, license, and whether the repository code was
read or only documentation was inspected.

REPOSITORY INSPECTION TARGETS

For each public repository, locate rather than read whole modules. Search for
home or dashboard composition, course cards or rows, route ownership,
breadcrumbs and back behavior, activity completion, quiz submission and result
screens, course exit, resume or bookmark state, focus restoration, mobile
navigation, empty and error states, offline behavior, visual regression and
end-to-end tests, design tokens, extension points, and accessibility tests.

Record reusable behavior and test ideas. Do not copy source, markup, styles,
assets, test fixtures, or wording. Copyleft code is prior-art evidence only.
Call out when an external pattern would violate itembank's one parser, one
scorer, local evidence, rights, disclosure, plain-file, or recovery rules.

FLOW COVERAGE

Build one transition graph and one state matrix that cover at least:

1. first launch, walkthrough start, skip, interruption, completion, and replay
2. empty, one-course, many-course, archived, unavailable, stale, and conflicted
   homes
3. start, exact resume, choose another course, Back, Home, deep link, reload,
   close, crash, offline, and model-unavailable behavior
4. source to lesson to note to practice, including exact passage return
5. practice correct, incorrect, retry, skip, stop, and remediation transitions
6. quiz and exam start, active attempt, accidental exit, timeout, submit,
   pending prose review, settled result, allowed review, locked review, evidence,
   remediation, course continuation, and return home
7. course completion, incomplete requirements, changed course revisions, and
   later return
8. agent operation pending, approval, rejection, conflict, undo, interruption,
   and recovery without making chat the home

For every transition name the actor, durable state, runtime or file authority,
derived UI state, allowed destinations, Back and Home behavior, unsaved-work
rule, idempotency risk, unavailable behavior, accessibility announcement,
mobile composition, and exact acceptance check.

COMPARATIVE HOME PROTOTYPE CONTRACT

Evaluate four reversible projections over identical data and routes:

- Resume: the best justified next action and exact continuation
- Shelf: bounded courses with identity, attention, state, and one action
- Agenda: overdue, today, upcoming, revisions, and recently completed
- Path: current position and available course movement

Do not assume all four should ship. State which user job each serves, where two
can combine, and what evidence would supersede a weak variant. Map each to the
Measured Field Guide and Learning Trajectory Deck profiles without producing
two renderers. Keep appearance themes orthogonal to presentation profiles.

FUTURE RE-RESEARCH POLICY

Treat the report as a dated evidence baseline, not permanent truth. Reopen only
the affected comparison when one of these triggers occurs:

- a named platform or repository ships a material dashboard, course-navigation,
  assessment-completion, accessibility, extension, offline, or recovery change
- a new learning platform contributes a distinct pattern absent from the source
  ledger
- a prototype or real learner sitting falsifies a recorded recommendation or
  exposes a transition missing from the matrix
- itembank adds a new activity, presentation profile, shell, input mode, or
  authority boundary that the comparison did not cover
- a cited source becomes unavailable, materially stale, contradicted, or changes
  license
- a scheduled phase begins whose decision depends on evidence older than its
  declared freshness window

For stable interaction principles, review evidence at the start of the owning
UI phase and after a failed acceptance gate. For fast-moving product behavior
and active repositories, check release notes and relevant paths again before
planning and before final acceptance. Record last checked date, upstream
version or commit when available, changed assumptions, affected findings, and
whether the change alters a recommendation. Do not rerun the complete landscape
without a changed assumption or uncovered question.

OUTPUTS

1. Update .planning/notes/2026-09-07-home-and-transition-ui-scope.md with a
   dated second-pass section. Preserve its original findings and distinguish
   corrections.
2. Create one research report under .planning/research/ with a source ledger,
   repository paths inspected, fact/inference/recommendation labels, pattern
   comparison, anti-patterns, transition graph, state matrix, gaps, exact
   prototype recommendations, and re-research trigger register.
3. Propose bounded changes to the existing UI character audit, requirements,
   roadmap, and continuation prompt. Do not apply binding changes without a
   direct user decision. Avoid creating a second owner for an existing finding.
4. Update the existing idea ledger only for genuinely new ideas. Give each one
   a disposition, owner, evidence class, dependency, cost driver, verification,
   falsifier, and relationship. Record rejected ideas with the binding rule
   text, retained alternative, and reconsideration condition.

ACCEPTANCE GATE

The research closes only when every existing audit finding and every newly
observed transition has one owner or explicit duplicate route, every cited
external pattern is traceable to a current primary source or named repository
path, facts are separated from recommendations, and the next prototype can be
built without deciding navigation, return, completion, or assessment behavior
inside the implementation task. The report must also name its freshness limits
and re-research triggers so future work can update changed evidence without
repeating the entire survey.

Run python3 scripts/vision_audit.py after record changes. Check all edited
non-quotation prose for em dash characters. Report which deterministic checks
ran, which human review remains, and what was not inspected. Do not claim that
the research proves usability. User review of comparable working flows remains
the selection gate.
```
