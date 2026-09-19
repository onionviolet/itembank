# Coherent UI renewal synthesis

Date: 2026-09-18. Owner: root integrator. Status: improved, highly changeable WIP showcase.

**Status: improved UI version, WIP and highly changeable.** The user recognizes
this as an improvement, not a final design or a frozen specification. Layouts,
visual styling, navigation, question workspaces, interactions and scope may be
revised or replaced as better evidence and needs emerge. Preserve useful
findings without treating this implementation as the default answer.

Future in-app code execution remains a supported product direction. Leave room
for a runner, output, test results and debugging beside the learner's code.
The current execution-unavailable state is a prototype limitation, not a ban
or a permanent UI constraint. Execution requires an isolated runner and draft
recovery. Runtime-owned grading remains distinct from execution output.
No execution implementation or production integration is claimed here.

Authority: [the WIP and future-execution clarification](../USER-VISION.md#2026-09-18-improved-ui-version-remains-highly-changeable-wip).

Authority: [the exact user statement](../USER-VISION.md#2026-09-18-coherent-app-renewal-inspired-by-stronger-learning-interfaces).
The [refined brief](../../prototypes/ui-renewal-20260918/BRIEF.md) preserves the
original wording separately from the execution interpretation and dispositions.

## Reconciled result

Three independent Astra lanes produced
[reference research](../../prototypes/ui-renewal-20260918/research/references.md),
[learner-flow findings](../../prototypes/ui-renewal-20260918/research/flows.md),
and [integration findings](../../prototypes/ui-renewal-20260918/research/integration.md).
One root writer built the showcase. No competing designs or production writers.

| Decision | Evidence | Showcase result | Production boundary |
| --- | --- | --- | --- |
| D1: One connected course journey | Flow audit F1-F3 and reference D1/D4 | Desk, course, lesson, question, feedback, review and in-tab resume | Runtime-owned exact resume and canonical course context still need integration |
| D2: Separate new appearance from legacy CSS | Integration I1/I2, user's explicit concern | Scoped tokens and components, no production stylesheet imports | Extract palette-only theme seam and select one complete stylesheet stack per document |
| D3: Rich teaching through direct manipulation | LiaScript staged-reveal observation and Desmos docs | Linked distance bars, time control, readable emphasis, reset and static explanation | Reuse accepted lesson semantics and existing disclosure gates |
| D4: Stable question and feedback states | H5P docs and existing continuity requirement | Selection, explicit sample feedback, explicit Next and focus handoff | Fixture never scores. Real statuses, hints and explanations come from runtime |
| D5: Intentional desktop and phone layouts | Reference D1/D5 and installed window constraints | Sidebar workspace on desktop, compact navigation and stacked content on phone | Compare generated, packaged and installed renderings against the same reference |

No evidence shows one competitor is universally better. Their useful interaction
patterns can fit Itembank while their classroom, hosted storage or assessment
systems remain outside this work. New code and assets were authored locally.
None were copied from competitors.

## Next implementation packet

The next ready production slice is the shared shell and course-to-activity
navigation. It is a proposed packet, not an executed migration or a new default.

Target `surfaces/presentation.py` document assembly and course shelf/frame
composition in `surfaces/daemon.py`. Separate token-only theme derivation from
`surfaces/theme.py` look rules. Inputs should explicitly name active navigation,
course context, page title, primary action and public content. Preserve IA and
daemon route ownership. Add exact resume data to its canonical public projection
if missing rather than infer it from the first available bank.

First observable result: the same synthetic course can open a lesson and return
to its course with the new shell, without old layout rules in its document.
Verify existing presentation and course route gates, light/dark/system appearance,
keyboard order, narrow reflow and visual parity at 1100 by 760 and 390 by 844.
Then migrate quiz, reader, report, settings and recovery assemblies through the
same seam, preserving their existing runtime actions and disclosure checks.
Do not declare app-wide integration after changing only `surface_shell`.

Failure conditions include legacy CSS leaking into renewed documents, changed
session identity, a hidden available action, leaked withheld explanation, lost
answer on error, wrong resume target, or missing packaged assets. Keep the prior
renderer available for rollback until equivalent runtime behavior and packaged
asset availability pass. Keep this prototype's answer fixtures and in-memory
state out of production.

## Scope and verification

The [showcase README](../../prototypes/ui-renewal-20260918/README.md) records
the exact browser checks and remaining boundaries. The installed app was not
replaced. Real banks, sessions, scores and evidence were not read or written.
Research refreshed primary documentation and one live LiaScript progression.
It did not establish competitor learning efficacy or complete product parity.

The independent showcase review found a hash-routing skip-link bug and lost
practice resume context after a lesson detour. Both were fixed and the browser
verified route-preserving focus and return to the still-visible feedback.

The vision audit found no missing interpretations, planning effects or inbox
dispositions. Older unresolved paths, relationship fields and trace links remain
outside this bounded pass. The new statement links here as its downstream owner.
Large code modules were sampled around named symbols, not read exhaustively.


## Nonstandard formats and visible references, 2026-09-18

Authority: [the user clarification](../USER-VISION.md#2026-09-18-nonstandard-question-workspaces-and-visible-design-references).
The initial three multiple-choice screens did not establish the design for
other question families. The showcase now has a Question formats destination
with five task-specific layouts: code prediction and blank trace with a repair
draft, keyboard-accessible code ordering, table completion, visual multiple
selection, and written argument analysis. Each preserves its own in-tab draft.
These are Prototype capabilities, not production format changes. No code runs
and no response is scored. Runtime integration and human acceptance remain.

The visible References destination contains eight annotated current references
and the historical 19-project landscape. Its durable source index is
[REFERENCES.md](../../prototypes/ui-renewal-20260918/REFERENCES.md).
Python Tutor, Runestone Parsons problems and CodeMirror primary pages were
checked for this extension. The previous five sources retain today's earlier
evidence class. The 19 historical leads are explicitly dated September 8 and
were not refreshed. CodeMirror is a reference, not an installed dependency.

Browser checks exercised prediction locking, blank trace entry, code draft
editing, block movement, table input, visual selection, response preview and
draft retention across format switches. Exact source whitespace was inspected
in the DOM. At 390 px the inspected code, ordering, table, visual and reference
views had no page-level horizontal overflow. Desktop code rendered at 1440 px.
The prototype needed versioned local asset URLs to avoid mixed cached JS/CSS.
This fixes preview freshness, not the production packaging problem.
