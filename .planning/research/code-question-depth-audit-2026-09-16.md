# Code-question depth audit

**Status:** bounded research and prototype recommendation, 2026-09-16.

**User direction:** consider useful levels for content-specific questions,
identify what is optimal and beneficial, and perform the same kind of audit for
code questions.

## Finding

Code questions currently have two strong endpoints but an under-specified
middle. The shared quiz surface safely renders ordinary stems as text. Check
items can provide a real editor and runtime-owned deterministic checks. The CS
Dojo prototype goes further with prediction, editing, bounded browser execution,
feedback, retry and export. A code-reading question should not need a fake IDE
to gain preserved indentation, visible control flow, or a useful variable
trace.

The missing contract is a task-sized depth choice. Depth is not quality,
difficulty, mastery, hint tier, or score. Each item should use the lowest depth
that makes its intended thinking legible and lets the learner diagnose the
kind of error the objective cares about.

## Depth model

| Depth | Learner experience | Best fit | Required floor | Main cost or risk |
|---|---|---|---|---|
| D0 faithful | exact source with language, whitespace, indentation and line breaks preserved | terminology, recognition and questions where code is only evidence | selectable plain code with an explicit language and linear reading order | flattened or malformed syntax changes the problem |
| D1 orient | D0 plus line numbers, restrained syntax roles, task label and declared context | identify, locate, compare and explain questions | non-color labels and the same source without highlighting | decoration can imply importance or an answer |
| D2 unpack | D1 plus learner-controlled state, call, stack, heap or data-flow views | output prediction, tracing and misconception diagnosis | a text state table or ordered trace that does not auto-reveal the result | the visualization can replace prediction with watching |
| D3 manipulate | D2 plus ordering, marking, small edits, test cases or comparing runs | debugging, completion and local repair | keyboard-equivalent controls, deterministic validation and retained draft | interaction can drift from the tested construct |
| D4 construct | a real editor or artifact workspace with declared runtime, tests, explanation and transfer | functions, algorithms, multi-step programming and authentic production | useful static brief, explicit execution limits, recovery and export | hostile code, packages, persistence and multi-file state become product obligations |

These depths are composable, not a forced sequence. A debugging question may
use D1 and D3 without an animated trace. A concept question may remain at D0.
An exam-aligned output question may deliberately stop at D1 because a D2 trace
would remove the construct being measured.

## Code-question family audit

| Question family | Default depth | Useful enhancement | Avoid |
|---|---:|---|---|
| concept or terminology choice | D0 to D1 | mark the named expression or compare two short snippets | an editor that adds no learning action |
| output prediction and code reading | D1 to D2 | require a prediction, then let the learner fill or step through a state table | revealing the next value before the learner commits |
| trace or state reconstruction | D2 to D3 | editable variable rows, call frames or ordered events with deterministic checks | decorative animation without a linear equivalent |
| debugging and fault location | D2 to D3 | show the symptom, let the learner mark a line, explain the cause, then make a bounded repair | treating a passing example as proof of correctness |
| completion or small function | D3 to D4 | real editor, declared examples, hidden checks only when assessment rules permit, retry and controlled reveal | client-side scoring or undeclared packages and files |
| algorithm or design explanation | D1 to D4 | pseudocode, diagram, tradeoff table and an optional runnable probe | auto-grading prose or equating execution with explanation |
| multi-file, package or security task | D4, deferred | durable project state, isolated runner, manifest, restore and explicit capabilities | production use before hostile-code and recovery gates pass |

## Optimality and benefit test

A richer depth is beneficial only when it improves the target learner action.
Acceptable evidence includes better transfer to a new example, more accurate
state prediction, faster diagnosis of a relevant misconception, fewer syntax
reading errors, or clearer explanation without answer leakage. Time-on-screen,
novelty and engagement alone are not enough.

Compare every candidate with the next simpler depth. Reject or revise it when
it adds navigation, visual noise or tool learning without improving the target
action. Also reject it when it weakens exam fidelity, exposes restricted
feedback, changes the source, loses a draft, or makes the accessible fallback a
different task.

## Progressive assistance

Runtime-issued hints may add a teaching layer to any depth, but the client must
not infer the next line, variable or bug from keyed content. Safe additions
include an authored term definition, an already-disclosed invariant, a prompt
to inspect a named line, or a blank state table tied to the visible source.
Answer-bearing traces, failing hidden cases and repairs remain locked until the
runtime explicitly releases them.

The level choice and hint ladder stay independent. Opening a hint does not
silently turn D1 into D2. If assistance introduces a trace or editor, the page
labels that transition and preserves the untouched source and the learner's
prior response.

## First bounded prototype

Use one original synthetic output-prediction item with a short loop or function.
Compare:

1. D1, a dedicated read-only code panel with language, preserved indentation,
   line numbers and a prediction field.
2. D2, the same source and prediction field plus a learner-filled state table
   that can be checked only after the prediction is committed.

Measure prediction accuracy, ability to explain the first mistaken state,
completion time, navigation burden and narrow-width readability. The D2 version
earns promotion only if it improves state reasoning or error diagnosis without
giving away the output. A debugging D3 comparison comes next only if the D2
result identifies a real need for manipulation. Do not begin with another full
editor.

## Authority, safety and recovery gates

- The bank and accepted artifact retain exact code and declared language. Rich
  views are derived and disposable.
- The runtime remains the only scorer, hint-disclosure authority and evidence
  writer. Prose remains pending or explicitly advisory.
- Representative fixtures cover parsing or compilation when intended, syntax
  and indentation, keyboard and touch, screen-reader order, zoom and reflow,
  contrast themes, reduced motion and a useful no-script representation.
- Execution has no undeclared network, host filesystem or package access. It
  needs deterministic time and output limits, cancellation, isolation and an
  unavailable-capability fallback.
- Editing preserves drafts across hints, retries, navigation and interruption.
  Accepted multi-file work requires a manifest, atomic writes, export and a
  clean restore before production promotion.

## Routing

IL-20260912-02 owns thematic question presentation and the D0 through D2
comparison. IL-20260906-09 owns executable D3 and D4 capability through the CS
Dojo route. The existing runtime hint ladder owns disclosure. This audit adds
selection criteria and a promotion gate. It does not accept a new schema,
renderer, runner, scoring path or course format.

## Prototype disposition, 2026-09-18

The first bounded comparison now exists at
`prototypes/code-question-depth/`. The rendered D1 view preserves indentation,
line numbers, language context, and a prediction field. Committing a prediction
reveals a learner-filled D2 state table. The check names only the first
inconsistent row. It does not execute code, score an item, write evidence, or
reveal a result. Its Node gate passes and localhost rendering confirmed the
prediction-first transition. Promotion still requires the human comparison
metrics and accessibility observations named above.

## Runnable comparison packet, 2026-09-18

**Disposition:** ready for a formative human trial, still a disposable F5
prototype. Weibao owns promotion and learner, visual, touch, and screen-reader
acceptance. This entry supersedes the preceding prototype's browser checker
as the current trial method. It does not supersede the original depth model.

**Observed gap:** the original always exposed D1 before D2 on the same source.
Its `expectedTrace` and `checkTrace` contained a browser-held key and gave
correctness feedback. That was inadequate for a counterbalanced comparison
without answer feedback. The previous statement that it did not score an item
meant no runtime score, not an absence of correctness judgment.

**Change:** the active prototype now has two original synthetic Python loop
examples and four assignments. Across fresh participants the assignments
balance depth, task, and position. Each participant completes one D1 and one
D2 task. The code never runs. Both depths lock an initial prediction before
showing the common proposed-trace diagnosis prompt. Only D2 supplies a blank
working table. No keyed check or correctness feedback remains in the active
page. The original files survive only in the rollback archive.

The local record captures initial and final prediction, first mistaken
proposed row, proposed corrected state, explanation, D2 working states,
start/commit/finish timestamps, elapsed and reasoning milliseconds, navigation
counts, reported burden, and freeform context. Human review defaults to
unreviewed. Task success, separate initial/final prediction accuracy,
first-state diagnosis, and explanation quality have explicit manual criteria.
These are prototype observations and must not become runtime assessment
evidence or settled grades.

The learner explicitly downloads JSON or copies its read-only preview.
Responses otherwise live in the tab's memory. Reload and close lose unsaved
work. A before-unload prompt is a convenience, not guaranteed recovery.
There is no autosave, import, telemetry, external request, dependency, or
production-contract change. The source and procedure are synthetic authored
material. The learner owns observations and any decision to share them.

### Verification evidence and limits

- **V1, Node:** the original `node prototypes/code-question-depth/verify.mjs`
  passed before editing. The revised command passed after implementation and
  after the final record-shape refinement. It covers all four assignments,
  prediction locking, required response fields, D2 row completeness, no repeated
  finish, timing arithmetic, partial versus complete exports, static source
  parity, and absence of the old key, evaluation, or network APIs. Original
  prediction-first and fallback assertions remain. The obsolete keyed-check
  expectations were replaced because the checker was removed.
- **V2, rendered keyboard:** Chrome at `http://127.0.0.1:8767/` completed order 1
  entirely through keyboard controls after the initial focused activation.
  Focus moved to the task heading on start, the diagnosis selector for D1,
  the first blank state cell for D2, and the summary heading on completion.
  Tab advanced through rows and common response controls. Shift+Tab returned
  from the second D2 cell to the first. A separate order-2 run completed D2
  before D1. Empty prediction submission retained focus and kept diagnosis
  hidden. No correct-answer feedback appeared. Orders 3 and 4 have Node
  coverage but were not separately completed in a rendered browser.
- **V3, rendered reflow:** both active D1 and D2 diagnosis views were inspected
  at 320 CSS pixels. Each had document scroll width 320, visible indentation,
  readable source, contained inputs, wrapped labels, and a visible focus ring.
  The manual page also measured 320 with a keyboard-opened diagnosis disclosure.
  Screenshots were inspected in-session. These are builder observations, not
  human visual or touch acceptance and not a complete zoom/contrast audit.
- **V4, no-script:** scripts were disabled on a dedicated Chrome test tab.
  The landing page displayed the Text trace fallback without dead interactive
  controls. The linked manual rendered both sources, diagnosis prompts, blank
  tables, recording sheet, rubric, and order protocol. Its native disclosure
  opened with Enter. Source text including indentation matched the active
  source in the Node check. Paper timing and observer counts are explicitly
  labeled manual. Script execution and viewport overrides were restored.
- **V5, observations:** a synthetic order-2 run's JSON preview was inspected.
  It contained two trials in the chosen order, `complete: true`, retained
  initial responses, three D2 states and zero D1 states, timing fields, and
  unreviewed human fields. No third-task control remained. Test answers were
  “unsure” and explanations labeled synthetic. They are not learner evidence.
  Download and preview use the same serialized string, but browser saving to
  disk was not exercised. The human must confirm the downloaded file opens,
  or use the copy fallback. No synthetic results were saved as learner data.

The full repository preflight was not repeated, as directed. No production
modules were edited or read in full. This pass sampled the September 16 vision
entry, the authority and operation sections of SOURCE-TO-COURSE and
AGENT-WORKFLOW, the complete small prototype files, and this audit. It makes
no whole-vision or production-module review claim. All pre-existing dirty
production and planning work remains outside this packet's write scope.

### Operational observations

Port 8765 was occupied, so the successful command was
`python3 -m http.server 8767 --bind 127.0.0.1 --directory prototypes/code-question-depth`.
The separate Playwright connector failed to connect to its extension. The
unified computer-use Chrome interface successfully rendered and exercised the
page. That interface does not support `Page.setDownloadBehavior`, so no
browser download directory was changed. Use the copyable preview when a test
cannot save into its authorized write scope. These observations live here
because this packet permits no writes to global memory or machine notes.

### Human acceptance packet

**Goal and owner:** Weibao compares state reasoning and diagnosis with D1 and
D2 and decides whether D2 adds enough value. No further Codex task is created.

**Procedure:** `prototypes/code-question-depth/manual.html` is the runnable
manual and no-script equivalent. It defines success, first-mistaken-state,
completion-time, navigation-burden, and explanation-quality recording without
an answer key or automated grade. Review happens after both tasks. Keep raw
records and add human review to a copy. Do not coach between conditions.

**Open gates:** real learner responses and human review, visual and touch
acceptance, screen-reader task equivalence, zoom/contrast review, and local
file-save confirmation. Similar task structure can cause carryover. Task
isomorphism is an assumption, not measured equivalence. Four assignments
balance order across fresh people, not within a repeated single learner.
Initial prediction precedes D2 exposure, so it is a baseline, not a D2 effect.
Use final reasoning and diagnosis to assess the aid. The common proposed
trace diagnoses a supplied misconception. D2's own state rows have no D1 row
counterpart and must not be treated as a directly comparable accuracy measure.
A single pair is formative only. No learning benefit or transfer is claimed.

**Changed paths:** `prototypes/code-question-depth/index.html`,
`prototype.js`, `style.css`, `verify.mjs`, and `README.md` were revised.
`manual.html` and `before-comparison.zip` were added in that directory.
This existing audit was appended. No commit, push, branch, dependency,
installed-app change, external service, or production contract was involved.

**Rollback:** the ZIP contains the five pre-edit prototype files and the
pre-edit audit at their repository-relative paths. Inspect for intervening
work before restoring with
`unzip -o prototypes/code-question-depth/before-comparison.zip` from the repo
root. Remove the added `manual.html` separately if fully retiring the packet.
Do not use the restored keyed checker for the new comparison protocol.

**Exact next action:** open `http://127.0.0.1:8767/`, leave assignment 1 selected,
and press Start task 1 after reading only the procedure above the task sources.
Retain prototype status until Weibao supplies and accepts human evidence.

Final scope check: all 23 other tracked dirty files matched their starting
SHA-256 fingerprints. IDEA-LEDGER and ROADMAP changed concurrently outside this
packet's actions and were not reverted. `git diff --check` reported no issues.
The prototype is untracked, so its actual JavaScript and test diffs were also
reviewed directly against the rollback archive. The audit's original prefix
was verified unchanged. A fresh untimed Chrome tab is left ready for the learner.

## 2026-09-18: Code Learner parity feedback

User wording is preserved in USER-VISION under word-anchored lookup and Code
Learner parity. This is a local source comparison, not a new upstream or
browser validation of Code Learner. Its inspected checkout is revision
`e5af4ac47a17c191d504d726f166e0b867f4efff`.

| Capability | Code Learner source | Itembank prototype boundary |
|---|---|---|
| Editing | CodeMirror syntax, line numbers, bracket matching, indentation and keyboard actions in app/page.tsx | CS Dojo has a simpler editor. The depth comparison has no editable program. |
| Execution | Python and JavaScript workers with declared checks and failure feedback | CS Dojo has JavaScript execution. Python remains absent. The depth comparison intentionally executes nothing. |
| Practice breadth | Language/category picker, shuffled queues, retry and solution reveal in app/page.tsx | CS Dojo contains one synthetic three-activity unit. The depth comparison contains two matched tasks. |
| Continuity | Browser-local language/category preferences and aggregate practice statistics | CS Dojo keeps drafts in page memory with explicit export. Neither prototype supplies accepted runtime evidence or mastery. |

The next useful coding slice should extend `prototypes/cs-dojo/`, retaining
prediction, repair, multi-file work, stop and timeout. First improve the
edit-run-feedback-retry loop and editor usability against explicit reference
tasks. Then address Python through a separately reviewed distribution and
execution boundary, and broaden objective-linked practice and recoverable
drafts. Preserve useful parts of the tracing experiment as activities, not as
a substitute for executable practice. Reference statistics and unrestricted
solution reveal cannot become Itembank assessment authority by copying UI.

These are proposed priorities, not newly shipped features or a commitment to
import the reference code, dependencies or content. Human experience review
and production promotion remain open.

## 2026-09-19: CS Dojo implementation check

The existing `prototypes/cs-dojo/` now restores bounded code and notes from
browser-local storage after reload. It uses Itembank's already-vendored
CodeMirror bundle in the dedicated preview, with a textarea fallback, and adds
an original Python boundary-transfer activity using pinned local Pyodide
assets. The Python worker has a separate loading deadline and a two-second
execution deadline. The focused Chromium gate passed 17 groups, including
Python error, repair, output cap, timeout, fresh worker, local requests,
keyboard navigation, narrow layout, and static fallback. Desktop and mobile
screenshots were inspected. Quick preflight passed.

This is a prototype comparison, not Code Learner parity or production
acceptance. Syntax highlighting and bracket editing remain below the reference
editor. There is no language/category drill queue, broad objective-linked
practice set, saved preference or aggregate practice view, runtime-owned
scoring or disclosure, accepted attempt evidence, clean restore, or production
execution isolation. Code Learner's question content and app code were not
copied. The 13 MB local Pyodide distribution and its license record are in the
prototype only.

The next bounded result should be a course-linked drill catalog with explicit
language, topic, objective and public checks, plus an editor usability review
against the reference tasks. Then the activity and execution contract needs
runtime authority, durable evidence, recovery, and accessibility review before
normal course navigation can present it as accepted practice. Keep the
synthetic prototype's ungraded observations distinct from settled scores.
