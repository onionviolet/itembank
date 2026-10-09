# Overall product review and native reading modes

Date: 2026-10-01. Status: bounded source implementation and ranked review.
This record projects existing idea owners into the next useful work. It does
not create another feature backlog or settle pending content formats.

## Request, direction and authority

The user asked:

> Overall improvements and more?

Asked whether they wanted a prioritized review or a focused implementation,
the user answered:

> both

Interpretation: supply both a grounded review and a concrete, reversible
improvement. Existing direction remains authoritative: visually distinct
working areas, character and useful interactions lead the pass. These words
do not select a final visual style or grant Git, build or install authority.

Read scope: this repository, its bounded memory pointers and public primary
references. Write scope: `surfaces/reading_desk.py`, one focused JS regression
file, the disposable preview folder, this record and additive routing pointers.
No learner files, active assessment content or paid services were used.
Public reference retrieval is the only remote egress.

Existing authority read: `AGENTS.md`, `.claude/CLAUDE.md`,
`AGENT-WORKFLOW.md`, `STATE.md` front matter and latest current-state blocks,
`SOURCE-TO-COURSE.md` sections 1-4, September 30 `USER-VISION.md` entries,
the UI goal/iteration records, UI remaining criteria, current coding-learning
record and wider backend comparison. This is a sampled refinement, not a
whole-vision or full-codebase audit.

Ownership: this pass owns the reading presentation slice. The October 1
coding work owns its already dirty runtime, daemon, quiz renderer, schema,
session and test changes. Their bytes were retained in
`.reasonix/reading-modes-20261001/unrelated.before.patch`; this pass never
edits those paths or the already dirty STATE and idea ledger.

Expected source base SHA-256:
`66f36cf82e4c753d1634640a0a34a48e50dc264f66764355d3cdcb24e706851d`.
The source before-image is
`.reasonix/reading-modes-20261001/reading_desk.before.py.txt`.
Context-checked repository patches are the reviewable operation record.

## Ranked review

These recommendations are inferences from current records and source, not
claims that every capability is absent. No viable idea is rejected.

| Rank | Desired improvement and concrete task | Existing disposition and owner | Dependency, cost and next gate |
| --- | --- | --- | --- |
| I1 | Fit the working area to the activity. Read without a sidebar, compare a source with notes, or give writing the larger pane. | IL-20260930-02, Prototype, visual iteration owner. This pass implements the native reading slice below. | Existing theme and note authority. Compare identical content, keyboard navigation and narrow/dark views; user preference remains open. Small presentation-maintenance cost. |
| I2 | Use subject-specific teaching: inspect code failures, manipulate a mathematical relation, or reason through a fictional case, then attempt changed-context transfer. | IL-20260930-01 and IL-20260908-06, Prototype; teaching/subject owners. Existing coding-learning slice already supplies one original example. | Source-grounded material, static meaning and domain review. Authoring and interaction cost. Next gate is one representative unaided learner task, not another generic panel. |
| I3 | Make evidence suggest an understandable next action, with the actual misconception, pending review or review interval visible. | Existing evidence/remediation and course-pacing routes; SOURCE-TO-COURSE owns the required loop. | Runtime evidence, objective identity, sample size and strategy owner. Review existing next-action behavior before adding controls; use a synthetic wrong-answer-to-remediation task. Never turn sparse evidence into a mastery percentage. |
| I4 | Make course construction a joined task: choose sources, inspect objectives/treatments, preview the smallest missing artifact, accept a bounded diff, reopen and undo. | CAP-03/02/23 in absorption synthesis, existing authoring and operation owners. | Current source/rights and proposal receipts. The September 30 director recovery and context search already landed. Verify the full task before declaring a missing seam. Live provider and human authoring review remain separate. |
| I5 | Finish delivery quality: check the installed journey, restoration and honest failure recovery before adopting another backend platform. | IL-20260930-03 and existing package/recovery owners. | Representative human/accessibility tasks and explicit package authority. P3/P5/domain formats and in-place merge remain their existing direct-decision gates. Optional FTS, extraction, queues and notebook adapters keep the triggers in BACKEND-COMPARISON. |

Current reconciliation: the September 30 UI remaining report's single-choice
draft omission is historical. Current `installDraft` already handles mc/multi
choices with a public-item signature and revision notice. This pass does not
repeat that repair or claim a fresh installed reproduction. Native code
stimulus/feedback improvements are currently uncommitted in the coding owner.

## References and design inference

Checked October 1:

- [Obsidian workspace documentation](https://help.obsidian.md/workspace)
  describes collapsible sidebars and split content areas. Inference: view
  composition should follow the learner's current job rather than a fixed
  sidebar width. The native modes independently adapt that idea.
- [marimo](https://marimo.io/) describes interactive elements and explicit stale
  outputs. Inference for I2: meaningful manipulation and visible freshness can
  support a learning experiment. No package, source code or autorun behavior
  is adopted by this reading pass.

Prior backend/license/adoption detail remains in the September 30
`audit-expansion-2026-09-30/BACKEND-COMPARISON.md`, not duplicated here.

## Implemented behavior

- Read centers the source and hides the private-note companion. Study keeps
  the existing source/notes split. Notebook gives writing the larger desktop
  pane and keeps a keyboard-scrollable source region nearby.
- Text size, line width and desktop Study note width are explicit controls.
  Mode and valid preferences survive reload in tab-local storage scoped to
  the existing course/occurrence/revision key. Malformed data and storage
  refusal leave the usable Study fallback. No durable format changes.
- Write a note and Add selection to draft enter Notebook. Return to passage
  restores the originating mode, source scroll and document position.
- View controls never save notes, declare reading, submit answers, or record
  evidence. The existing explicit save/retry and reading-declaration controls
  retain their authority. Script-free output keeps readable source and notes.
- Mode buttons expose pressed state. The constrained Notebook source becomes
  a keyboard stop with a named region. Forced-color selection has an outline.
  Mobile layouts stack and preserve the existing document order.

## Validation and remaining limits

Final checks:

- `python3 tests/reading_desk_roundtrip.py`: 7 tests pass.
- `python3 tests/reading_declarations_roundtrip.py`: 14 tests pass.
- `python3 tests/ui_overhaul_workspace_roundtrip.py`: 3 tests pass.
- `python3 tests/ui_overhaul_journey_roundtrip.py`: native HTTP read, note
  save/refusal/retry, exact reference return, practice/exam disclosure and
  sitting reload pass.
- `node --test tests/js/reading_workspace_modes.test.mjs tests/js/reading_note_save.test.mjs`:
  all 13 cases pass, including invalid/absent storage, prior-revision exclusion,
  view-only requests and existing uncertain-save recovery.
- `python3 prototypes/reading-modes-20261001/preview.py --verify`: 18 actual
  native layouts at 1280/390/320px in light/dark, six draft/preferences reloads,
  keyboard scrolling of the constrained source, script-free fallback and exact
  unchanged synthetic durable-file fingerprints pass. Desktop reader/study,
  dark Notebook and 320px Notebook screenshots were visually inspected.
- `python3 scripts/preflight.py --quick --source-only`: every running gate
  passes, including skill mirrors. Build, full Python/JS suites and clean-tree
  gates are explicitly skipped by these flags.
- `python3 scripts/vision_audit.py`: exits zero, zero missing dated
  interpretations and zero inbox entries without a disposition. Its legacy
  link/relationship backlog remains open and was not repaired by this pass.
- `git diff --check`: passes. Before/after unrelated dirty patches compare
  exactly. A concurrent platform-parity capture in the inbox was preserved.

No new full suite ran. Existing Python 3.14 file/HTTP ResourceWarnings appear
in the focused suites, which exit zero; this pass does not repair those
independent resource lifetimes. Source implementation stays separate from
installed acceptance.
Human visual preference, screen-reader/physical-touch tasks and learning
transfer remain unverified. No full-suite, package, commit, push or install
claim is made by this record.

Final source SHA-256:
`ee35c19642c88d691ce3bf9d1051d704d2dab1e02f2a23e32ab612ab8b1b88ac`.
The bounded source patch and final file fingerprints are recorded in
`.reasonix/reading-modes-20261001/source.patch` and `operation.json`.
The disposable preview is intentionally left running for user comparison;
its terminal prompt stops and cleans it on Enter. The old preliminary preview
was stopped before opening the final fixture.

## Recovery and vision audit

Review only the named source/test paths and this preview. To undo, reverse this
pass's source diff after checking the current file fingerprint against the
final operation receipt; preserve any subsequent writer's changes. Remove only
this pass's new test and preview if their bytes still match that receipt.
Tab-local workspace settings may remain harmlessly unused after rollback;
they contain only display choices. Private note and evidence files need no
migration or rollback because presentation controls never changed them.

The request is routed to the existing visual directions in the inbox.
Interpretation and implementation choices remain separate from exact user
words. I1-I5 retain their existing disposition/authority owners. No existing
quotation, rejection, contract, accepted source or learner evidence is rewritten.
The project vision audit and skill mirror check are the closing record gates.


## October 2: higher-level and granular UI and engine improvements

Status: sampled product/engine review and recommended next slice. This extends
I1-I5 above with a cross-layer view. It does not replace the capability register,
settle pending formats, or claim a new source implementation.

The user asked:

> higher level and granular UI and engine improvements and more?

Interpretation: consider the larger course experience, small interaction details,
engine behavior and wider instructional/authoring quality together. The proposals
below are agent recommendations. The question does not select a final design or
accept each proposed engine change.

Read scope: this repository, bounded prior direction pointers and public primary
references. Write scope: this additive review section and one inbox capture;
local before-images and the operation receipt live in the ignored review folder.
No learner course, real assessment, installed application or private service was
used. Public reference retrieval is the only remote egress. Existing dirty
runtime, schemas, renderers, tests, STATE and idea ledger remain under their owners.

### Current baseline and verified finding

The current October 1 records already cover native Read/Study/Notebook modes,
revision-bound code feedback and the D1-D5 lesson/interaction pass. Those records
report focused source/browser proof; this review did not rerun their browser
checks or inspect the installed app. Their human and installed limits remain.

Current source inspection confirms that the course overview in
`surfaces/daemon.py::_course_area_rows` chooses the first available reading,
lesson and quiz, with an exact saved practice resume when available. This is a
joined entry route, but the sampled selection does not explain an evidence-based
reason for those three choices. This is a bounded observation, not a claim that
all recommendation primitives are absent.

F1, reproduced using disposable synthetic storage: an absent evidence log and
an existing directory at the evidence-log path both produce exactly
`{responses: 0, marks: 0, sessions: 0, events: 0}` from
`surfaces/daemon.py::_course_evidence_counts`. The function catches read errors
and returns the same count shape. Its evidence-area caller treats zero events
as empty; the overview labels zero recorded responses. No served screenshot or
ordinary learner-file corruption was tested. The reproduction establishes the
helper's loss of unavailable versus empty state and the sampled callers' source
behavior. A production repair remains to be implemented and checked.

`evidence.py::objective_history` already uses a disposable SQLite projection
with linear-scan fallback. Reuse that owner; proposing a database from scratch
would duplicate an existing mechanism. No latency, memory or throughput benchmark
ran, so this review makes no performance-defect claim.

### H1-H5: pair visible improvements with the engine work they need

| Code and larger outcome | Granular UI work | Engine work and acceptance task | Existing route and disposition |
| --- | --- | --- | --- |
| H1, make a course tell the learner what to do and why | Show current objective, an explicit next activity and a short reason with attempts/pending review; keep exact Resume visible. | Reuse objective/evidence/strategy owners to select an eligible activity; distinguish absent, insufficient and unreadable evidence. Wrong answer, suitable remediation, changed-context attempt and exact restart must form one normal-route task. | I3, CAP-14/16/26 and the contract evidence loop, Core behavior; specific recommendation treatment remains Prototype. |
| H2, give each activity a useful composition and character | Reading puts text first; experiments put the manipulable object first; code pairs editable work with released run observations. Keep reference/notes near the task and controls where their effects appear. | Reuse current reading modes, lesson capabilities and runtime projections. Keep saved exploration, submitted attempts and stale outputs distinct. Compare the same objective in different compositions on desktop and narrow layouts. | I1/I2, IL-20260930-01/02 and CAP-10/11/27, existing Prototype directions. |
| H3, make every interaction behave deliberately | Grab the visible marker; settle Escape/blur cancellation; anchor help to its term; preserve code indentation on copy; keep focus and viewport useful after feedback; expose real pending/saved/error states. | Presentation state remains scoped to occurrence/revision and separate from evidence. Reuse existing controls before adding new ones. Check one actual changed gesture through cancel, detour, reload and failure, with keyboard equivalents. | The existing ui-character NEXT-PASS A1-A5 and native D1-D5 owners, Prototype; already delivered details are baseline, not new defects. |
| H4, make the engine trustworthy and responsive at course scale | Explain stale material, unavailable history and unresolved author jobs with the next safe action. Let the user inspect the source/revision behind a result. | First repair F1 through a typed read-only projection. Then measure long-course load/search/replay, keep derived indexes rebuildable, and close named cancel/retry and writer-admission seams. Preserve sole runtime scoring. No blanket rewrite or dependency adoption is proposed. | IL-20260930-03, CAP-05/06/23/24 and BACKEND-COMPARISON; reliability stays Core, optional indexes/jobs keep their existing Registered/Backburner triggers. |
| H5, deepen course quality and authoring | Join source selection, objective/treatment review, cited preview, bounded diff, acceptance and undo. Use actual worked examples, misconceptions, projects and unfamiliar transfer tasks to express subject depth. | Reuse current proposal receipts, bindings and reviewer authority; audit coverage, cognitive demand and changed-source effects. Reopen one accepted unit and undo one revision through normal app routes. | I2/I4, CAP-01/02/03/12/22/23/26 and existing source-to-course owners; core course-quality obligations, Prototype new subject treatments. |

Recommended first slice: use the existing synthetic coding course to repair F1
and join evidence to one understandable next action. The UI should say why the
activity is relevant, the runtime should retain assessment authority, and the
learner should return to the same working context after remediation or restart.
Absent, unreadable, pending-only and valid evidence need distinct observable
outcomes. This connects H1/H3/H4 in one useful result rather than treating five
areas as simultaneous implementation commitments.

Later work retains the existing owners: broader approved-root retrieval and
extraction fidelity, richer visual/domain adapters, exact anchors/activity graphs,
job cancellation, populated-root in-place restore and representative human
review. P3/P5/domain format decisions remain unresolved. No viable feature is
rejected or silently removed by this priority order.

### Current primary references and inference

Inspected October 2:

- [marimo's execution model](https://marimo.io/#code-and-outputs-stay-in-sync)
  describes dependency updates and an option to mark outputs stale instead of
  autorunning. Recommendation: adapt visible freshness for one admitted code or
  simulation activity; this does not adopt its platform or reactive execution.
- [SQLite FTS5 external-content behavior](https://www.sqlite.org/fts5.html#external_content_table_pitfalls)
  documents synchronization pitfalls and rebuilding an index from content.
  Recommendation: retain a disposable source index only if the current literal
  search fails a measured course-scale task. Recheck source revision and rights
  before presenting cached results. Existing evidence indexing is separate.

### Limits, recovery and closing checks

This is a sampled refinement. It read the relevant contract/vision entries,
current reviews, capability rows, backend owners and source windows around course
entry/evidence projection. It did not read the large daemon, evidence or runtime
modules in full, certify platform parity, or inspect every current renderer.

Undo removes only this dated appendix and its exact inbox entry after checking
current fingerprints; preserve all earlier content and later writers. The local
operation receipt records expected/final fingerprints and before-images. No
code, format, learner state, roadmap, commit, build or installed state changes.
The closing vision/style/link and quick source-only gates are recorded in the
receipt. Human preference, accessibility, learning transfer and performance
remain unverified by this review.


## October 2: parallel implementation packet

The user authorized:

> implement in parallel accordingly? send out new chat to look into engine feature expantions to make everything more powerful and intuitive stronger flow and a more fleshed out experience?

Goal: implement the existing evidence-to-next-action slice in the native course
journey and investigate broader engine expansion in a separate user-visible chat.
This parent is the integrator and owns this record, shared capture/state updates,
final source checks and the acceptance decision for the bounded source result.
The existing dirty checkout is the base, not clean HEAD alone. Expected hashes
and before-images are saved in the ignored course-guidance operation receipt.

The engine lane owns evidence.py, surfaces/course_workbench.py and its new
focused tests. The UI lane owns the bounded course/evidence sections of
surfaces/daemon.py and, only if needed, their style in surfaces/presentation.py.
The independent verification lane owns one new synthetic served-journey test and
its ignored browser evidence. All writers preserve prior dirty code and work
from live bytes. No lane writes another lane's paths or shared planning files.

Frozen interface: evidence.course_counts(log) provides flat response, mark,
session and event counts plus state/complete/issues. Missing/empty is distinct
from unreadable (unavailable counts are unknown, not zero); malformed or future
records retain an explicit incomplete state. Counts use live retraction-aware
reader semantics and remain read-only. No alternate scorer, evidence writer,
store or required package is introduced.

surfaces.course_workbench.course_guidance(root, course_dir, doc, banks) returns
a read-only public projection with kind (review, resume, pending, start or
unavailable), title, reason, href, objective and optional exact resume_href.
Reuse review_history, canonical sitting admission and runtime-released evidence.
A relevant released practice miss may lead to a currently admitted linked
explanation, with exact saved-sitting return. Active saved work retains exact
Resume; pending prose gets review context, never a miss or score. Withheld,
missing, ambiguous, stale or unsupported evidence cannot invent a remediation
or mastery claim. Start is a source/lesson-first fallback, not inferred weakness.
Do not read keys, disclose raw answers or recalculate correctness. The UI lane
joins this recommendation with existing readings, lessons and bound practice
routes. Read-only recommendations never auto-start a session or submit work.

Acceptance: absent/empty, unreadable, partial/unsupported, pending, retracted and
released practice histories display truthful states; a wrong-answer explanation
and exact return/reload/restart preserve the admitted session and cursor; blind
formal feedback is withheld; GET guidance does not alter accepted course/evidence
files. Inspect native desktop/390px/320px composition and keyboard use, with
human visual, screen-reader, physical-touch and learning acceptance separate.
Run focused gates during implementation, then one coordinated source-only
preflight on the integrated revision. Keep required failures and skipped legs
visible. Commit, push, package/build/install and release are outside this task.

The separately requested chat owns research/engine-expansion-2026-10-02.md and
its ignored evidence only. Its production and shared-record scope is read-only
while this implementation runs. It considers more capable engine flows and
implementation-ready expansion tracks without accepting pending formats.


## October 2: implementation and independent verification

Status: native source implementation and focused/HTTP/Chrome gates complete.
The combined source-only run failed two older assertions and the clean-tree gate;
both assertions pass focused repairs, and final quick source-only gates pass.
Engine, UI and independent verification lanes released their source.
The existing runtime, schema, lesson, coding and reading work was preserved.
This slice implements H1/H3/H4's evidence-to-next-action connection; H2's broader
visual choice and H5's course-authoring breadth retain their existing owners.

The course overview now presents a current objective, one next activity, its
reason and exact saved-sitting continuation before the longer course path.
The engine selects the activity once, using current bindings, source rights and
revision, uniquely admitted artifacts and runtime-released evidence. New attempts
displace older misses, with timestamp and log order ranking. A linked explanation
returns to the same practice session; pending prose stays pending and held
formal/staged responses cannot drive early remediation. Unknown, malformed,
future, stale and ambiguous histories show recovery instead of a fresh-start or
mastery claim. With no applicable released attempt, a valid source/lesson/bound
practice path remains available.

Live counts distinguish empty, ready, incomplete and unavailable. Unknown counts
are null; partial counts name their readable-record denominator. Reading
operation IDs are excluded from assessment-sitting counts. A narrow structured
IA flag permits validator-checked reading-only history to retain safe source-first
guidance, while actual orphan assessment evidence still requires recovery.
Per-call reader diagnostics replace global stdout interception in the joined view.
Known unreadable/incomplete logs refuse missed-item indexing before creating
sidecars; healthy nested bank history remains eligible when the root log is empty.

Owned changes: evidence.py, surfaces/course_workbench.py, bounded course/evidence
sections in surfaces/daemon.py, course-specific styles in surfaces/presentation.py,
one additive flag in surfaces/ia.py, three new course-guidance test scripts, and
the existing missed_review_roundtrip.py synthetic fixture. The fixture now writes
its actual synthetic miss rather than mocking history over an empty log. Other
assertions and prior dirty source remain intact. No source grammar, settled
scoring authority or durable course format changed.

### Actual gates and the defects they exposed

The [engine receipt](../../.reasonix/course-guidance-20261002/engine/implementation.md)
and [UI receipt](../../.reasonix/course-guidance-20261002/ui/receipt.md) name exact
focused commands and current source fingerprints. The 12 new engine tests,
new UI assertions and affected evidence, A3 course workflows, course workbench,
resume, reading declarations, navigation and accessibility suites pass.
Default cached Playwright Chromium was unavailable; the existing installed Chrome
channel passed the browser leg without downloading or installing a browser.

Independent [native results](../../.reasonix/course-guidance-20261002/verification/result.json)
and [observations](../../.reasonix/course-guidance-20261002/verification/observations.md)
prove normal HTTP source start, scoreless reading declarations, released
practice miss to explanation to exact return/reload/restart, retraction, pending
prose, active formal withholding, changed rights/source/bank refusal and active
sitting ambiguity. Direct guidance/lesson and damaged-history GETs preserve bytes.
Healthy Evidence may create only its known disposable index/lock; intentional
exact quiz navigation may refresh only the existing served_ts timing field,
without changing cursor, item, responses or response events.

Chrome 154 exercised start/review at 1280, 390 and 320 pixels and both keyboard
actions, with nine screenshots and no horizontal overflow. At 320px the secondary
Resume action partly crosses the fixed navigation at initial scroll; native Tab
scrolls it fully above that navigation with measured clearance. This is an initial
fold observation, not a failed keyboard gate. Screenshots were inspected by the
verifier and the parent inspected the desktop and 320px review compositions.
Human visual preference, screen readers, physical touch and learning transfer
remain separate from this source/browser verification.

The new native route continues to admit practice and exam. Diagnostic, drill and
remediation saved return modes lack the current exact native route and fail
closed; this pass does not add those modes. Large modules were read by symbol
windows and relevant tests, not in full.

### Separate engine expansion chat

The requested project chat completed the
[engine expansion report](engine-expansion-2026-10-02.md). Its E1-E5 tracks retain
existing owners: prerequisite context and explainable work, original projects
and transfer, richer practice/execution adapters, source discovery/fidelity, and
cancellable/recoverable jobs. Its next ready proposal adds authored prerequisite
rationale and descriptive released evidence to Course map after this slice.
Its synthetic 50,000-event benchmark supports retaining the current native index;
objective-query timings do not prove full-page or installed performance.
This parent did not adopt the broader proposals or change pending P3/P5/domain
formats. Research source/document gates are attributed to that separate chat.

### Recovery and source handoff

Expected bases, final fingerprints, task-relative source diffs and original
before-images live in the ignored course-guidance operation folder. Recovery
copies use .txt suffixes because source-authority checks can mistake .py copies
for another implementation. Undo only this task's diff against matching final
fingerprints, preserving inherited dirty work and later writers. No commit,
push, fresh package/build, installation, release or real learner mutation ran.
The combined preflight log remains the source-suite owner. It executed 194 of
197 Python scripts (three app-build scripts deferred), with two test failures:
gate_roundtrip used raw pre-control markup instead of the existing bounded
Phase 3 teaching-content projection; subject_loop_roundtrip expected a bare pre
instead of the existing keyboard-readable code region. Both preserve their
teaching/source-order assertions and now pass focused reruns. No renderer or
historical golden was changed for these repairs. The original full run remains
failed and was not repeated. Its JavaScript gate passed. Final quick source-only
gates pass; build/full Python/full JS/clean-tree legs are skipped by quick flags.
The dirty shared checkout still fails the clean-tree gate. The vision audit
reports zero missing dated interpretations/inbox dispositions and retains its
legacy reference/relationship/downstream-link debt. New record links, source
fingerprints, style and git diff --check pass. Recovery images/diffs also include
the two bounded compatibility-test repairs. Human/installed and CI-only legs
remain separate. The final receipt verifies 2,026 unrelated tracked files
unchanged.
