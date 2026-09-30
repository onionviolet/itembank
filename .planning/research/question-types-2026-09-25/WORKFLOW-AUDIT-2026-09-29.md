# Question workflow and implementation audit

Date: 2026-09-29. Status: comparative source audit and implementation recommendations.
Owner: the existing F1-F10 question backlog, assessment and interactive-teaching lanes.

User direction: "Audit accordingly and be inspired from their workflow/implementation if possible"

## Scope and evidence boundary

This audit compares authoring, preview, response construction, checking,
feedback, evidence, restart and recovery. It covers all ten backlog families
at contract level and samples implementation owners for F1, F2, F6, F7, F8
and F9. It is not an exhaustive product audit or installed-app acceptance.
F3-F5 and F10 retain their prior source reports where no new implementation
inspection is named. Existing visual, typed-fill and code capabilities are
preserved rather than relabeled absent.

Itembank base: `8ccd45832b66b0b86bb406d6232ef0633ef71dc3`, with shared uncommitted
changes. Read roots: repository source, existing audits and public upstream
repositories. Write roots: this report and links in existing backlog/current
state. No learner files, banks, evidence, settings or installed processes were
used. Remote requests fetched public source only. No donor code was executed,
installed or copied into product code. Revisions below pin the source inspected;
they do not imply donor release acceptance.

The code-review skill's source-analysis rubric was applied inline to the named
symbols. This is a comparative review under the existing backlog, not a claim
that a GSD phase or its acceptance gates were completed.

## Five principal findings

| Ref | Classification | Verified observation | Implication and acceptance gate |
| --- | --- | --- | --- |
| W1 | P1 delivery gap | `surfaces/quiz_page.py:start()` returns after `installDraft()` when a server baseline exists. `_form_controls()` renders inline selects but no word bank. New word-bank dragging is in `asAssign()` only. The earlier browser fixture invoked that function directly. | Normal served baseline does not receive the new drag interaction. Enhance the accepted form path, then prove it through an ordinary course-to-sitting journey without removing the baseline. Keep native controls and the same runtime submission. |
| W2 | P2 recovery defect | Served `asBuild()` initializes `order = []` on each render, never saves a draft, and never restores it. `installDraft()` captures text inputs/textarea for non-assignment types, not build selects. A probe selected position 1, found zero stored drafts and zero restored positions after rerender. | Build answers lose unfinished work in the sampled paths. Prove exact order through detour, reload, refused submit and retry, with draft cleanup only after an acknowledged submission. This finding concerns unfinished responses, not already-recorded attempt recovery. |
| W3 | Missing semantic contract | `model.py` parses build as step text; `runtime._canonical_build()` joins the text sequence and `score_response()` compares it with one key. Duplicate build steps are already rejected by lint. No dependency or distractor contract exists in the sampled build path. | Multiple valid orders, omitted distractors and indentation cannot be delivered by changing the widget alone. Add versioned step identity, constraints and a runtime checker; preserve legacy exact-order semantics. Validate cycles, missing IDs, duplicates, omitted required steps and alternative valid orders. |
| W4 | Missing completion/cardinality contract | Current dnd maps every row to one reusable category. A single literal `___` selects the inline renderer; two markers fall back to ordinary rows. Public rows carry positional IDs within the accepted item. | This is reusable category completion, not general multi-blank text or an explicit one-to-one response contract. A one-to-one answer key can already be compared by the existing scorer; declared capacity, construction and validity rules are missing. Declare blank/choice identity, reuse policy, unmatched/distractor behavior and semantic input explicitly. Do not derive identity from duplicate display text or silently reinterpret older items. |
| W5 | Incomplete workflow evidence | Current F1 tests isolate controls; the Python inline test checks HTML. The browser fixture used a synthetic settlement callback. Earlier package evidence predates the latest word-bank addition. The most recent full preflight failed theme expectations, the dirty-tree gate and initially JavaScript; a separate JavaScript rerun passed 85 tests. | No end-to-end acceptance denominator exists for the expanded F1 family. Require author, lint, preview, normal sitting, permitted feedback, report, restart and packaged checks on the same fingerprinted candidate. Prior evidence cannot certify later bytes. |

W1 and W2 were reproduced in this audit. W3 and W4 are explicit capability
gaps, not failures of the currently documented exact-order/category contracts.
W5 is an evidence gap. No additional source defect is claimed without a probe.

## Upstream source patterns, not just feature labels

| Reference and pinned revision | Implementation inspected | Useful pattern for Itembank | Boundary when adapting |
| --- | --- | --- | --- |
| H5P Drag Text, `043aedd9d1f5a0a2ff9e525363514729d388caa7` | `src/scripts/drag-text.js`, `draggable.js`, `droppable.js`, `semantics.json` | Separate draggable/drop-zone state, keyboard controls, check/retry/solution controls, serialized `getCurrentState()` and validated restoration. Authorable behavior and accessibility strings belong to the artifact contract. | Its state records draggable/drop-zone indices, not reusable category values. Choose token capacity explicitly. Its client correctness and instant feedback must not become Itembank scoring/disclosure authority. |
| PrairieLearn, `f95f58c7b9771d4657f095598da5d38f9fc57603` | `pl-order-blocks.py`, `dag_checker.py`, `dag_checker_test.py`, `pl-matching.py` under `apps/prairielearn/elements/` | Prepare, render, parse and grade are distinct lifecycle operations. Ordering supports dependency graphs and grouped constraints. Matching validates submitted options and exposes grading separately from controls. | Adapt declaration and test patterns. Keep grading in Itembank runtime, not donor client code. Do not adopt donor partial-credit formulas before defining Itembank evidence/aggregation semantics. |
| RunestoneComponents, `d05ee263a5cc9d9c029cfc31f8f8ecdcf669fb11` | `runestone/parsons/parsons.py`, `js/parsons.js`, `js/dagGrader.js` | Author block semantics independently of drag behavior. Restore source and answer areas, indentation/adaptive state and attempt history; provide keyboard interaction. Select line-based or DAG checking deliberately. | Restore learner state without importing a client-owned settled grade. DAG feedback code includes subset enumeration; do not transplant it without complexity limits. Ordinary Parsons is not proof of executable-code isolation. |
| STACK, `3272066b49cff4eda5d89d06913081547bfb12fd` | `stack/prt.class.php`, `stack/questiontest.php` | Named response-tree outcomes and authored question tests connect inputs, expected results and diagnostics. Test teacher answers, common mistakes and variants before accepting the question. | Start with bounded runtime-owned diagnostic/checker contracts. Separate equivalence, required form, validity and unsupported/error states. Keep formal-mode disclosure gates and reviewed prose marking. |

Pinned primary sources:

- [H5P implementation](https://github.com/h5p/h5p-drag-text/blob/043aedd9d1f5a0a2ff9e525363514729d388caa7/src/scripts/drag-text.js), [authoring semantics](https://github.com/h5p/h5p-drag-text/blob/043aedd9d1f5a0a2ff9e525363514729d388caa7/semantics.json).
- [PrairieLearn ordering checker](https://github.com/PrairieLearn/PrairieLearn/blob/f95f58c7b9771d4657f095598da5d38f9fc57603/apps/prairielearn/elements/pl-order-blocks/dag_checker.py), [matching](https://github.com/PrairieLearn/PrairieLearn/blob/f95f58c7b9771d4657f095598da5d38f9fc57603/apps/prairielearn/elements/pl-matching/pl-matching.py).
- [Runestone Parsons lifecycle](https://github.com/RunestoneInteractive/RunestoneComponents/blob/d05ee263a5cc9d9c029cfc31f8f8ecdcf669fb11/runestone/parsons/js/parsons.js), [DAG grader](https://github.com/RunestoneInteractive/RunestoneComponents/blob/d05ee263a5cc9d9c029cfc31f8f8ecdcf669fb11/runestone/parsons/js/dagGrader.js).
- [STACK response trees](https://github.com/maths/moodle-qtype_stack/blob/3272066b49cff4eda5d89d06913081547bfb12fd/stack/prt.class.php), [question-test implementation](https://github.com/maths/moodle-qtype_stack/blob/3272066b49cff4eda5d89d06913081547bfb12fd/stack/questiontest.php).

Official workflow references refreshed in this audit:
[PrairieLearn ordering](https://docs.prairielearn.com/elements/pl-order-blocks/),
[Runestone authoring](https://runestone.academy/ns/books/published/authorguide/directives/parsons.html),
[STACK authoring workflow](https://docs.stack-assessment.org/en/STACK_question_admin/Authoring_workflow/),
[STACK question tests](https://docs.stack-assessment.org/en/STACK_question_admin/Testing/),
[H5P branching](https://h5p.org/branching-scenario).
Some direct documentation fetches failed; indexed official documentation and
pinned repository source supplied the named evidence. No live donor UI trial
or learning-benefit comparison was performed.

## Family coverage and implementation disposition

This table is a ten-family coverage count, not a percentage of product completion.

| Family | Existing foundation | Missing workflow or checker contract | Disposition after audit |
| --- | --- | --- | --- |
| F1 completion/matching/order | Category assignment, inline dropdowns, drag candidates, exact-order build | Normal served drag delivery, build drafts, multiple blanks, explicit matching capacity, step IDs/dependencies/distractors | Implement repair and complete-family contracts first. W1-W5 define the gates. |
| F2 math | Typed text, numeric tolerances and multiplicative units; bounded visual numerics | Symbolic domains, required form, sets/intervals/vectors/matrices, significant figures, dimensional and affine units | Prototype one named bounded domain after grammar, limits, invalid/unsupported states and authored checker tests are specified. |
| F3 staged reasoning | Runtime modes, objective evidence, source locators | Response-span anchors, child-response state, answer/reason stages, first-error selection, case disclosure | Prototype a two-stage synthetic task with exact restart and independent disclosure. Do not infer this from guided lesson stages. |
| F4 executable/domain tasks | Existing Python check runner and case results | SQL/notebook/files/spreadsheet/domain contracts, execution isolation, environment/fixture pinning | Preserve domain adapters as backburner. Promote one actual objective; timeout alone is not isolation. |
| F5 captured/reviewed work | Pending short responses and reviewer authority | Capture objects, original media, upload/drawing/audio/observed-skill workflows and review rubrics | Backburner capture/reviewer work; keep original artifact and reviewed mark distinct. |
| F6 H5P-style activities | F1 controls, lesson media and progressive teaching foundations | Mark-word anchors, video checkpoint state, branch graph/endings, authorable preview | Registered F1/F3 reuse plus prototype branching/media. H5P tree authoring is a useful model; it does not establish Itembank branch execution. |
| F7 Parsons/code selection | Exact-order build, Python check | Distractors, indentation, valid alternatives, assembled-code submission, prediction commitment, restored source/answer areas | Prototype after W2/W3; structural and executable checking are distinct strategies. |
| F8 structured math/variants | Existing visual plots/numberlines/connections/traces and typed fill | Big-O/matrix/sketch constraints, variant seed plus checker version, multi-file workspace | Prototype bounded representations; capture and execution inherit F4/F5. Do not claim generic graph capability from one visual widget. |
| F9 diagnostics | Runtime hint tiers and rationale disclosure | Authored misconception rules, dependent inputs, named outcomes, per-question checker tests | Prototype diagnostic rules in runtime after the chosen checker domain exists. Partial credit needs separate evidence semantics. |
| F10 practical simulations | Trusted bounded lesson controls and plots | Validated scientific model, apparatus state, predictions/observations, restart and transfer task | Prototype only for one named scientific objective. Prior donor prompt/template evidence is not a verified simulator. |

Cross-family retained work: explicit binary decisions per statement, per-field/
row/test credit and rubric weighting. These need a common aggregation and
migration contract, not ten unrelated widget-specific score systems.

## Recommended implementation programme

| Unit | Complete task and source owners | Required evidence before closing |
| --- | --- | --- |
| A1, normal-path delivery and continuity | Repair W1/W2 in `surfaces/quiz_page.py` and owning JavaScript/served tests. Preserve existing parser/scorer. | Ordinary server baseline, drag and native fallback, reload/detour, refused submission, exact response, formal withholding and matching packaged renderer. |
| A2, completion and matching family | Explicit blank/choice IDs and reusable versus one-to-one policy in `model.py`, schemas, runtime, authoring and quiz. Reuse current mapping where sufficient. | Author two different tasks with duplicate display labels, preview/lint, reject forbidden reuse, correct/retry, restart, report and plain fallback. Existing dnd keeps its meaning. |
| A3, ordering and Parsons foundation | Versioned build step IDs, dependencies, distractors and optional indentation, with checker strategy in runtime. | Two valid orders pass; violated dependency, missing required block, selected distractor and invalid graph fail distinctly. Legacy items and old evidence remain interpretable. |
| A4, staged/case activities | Child-response and activity-state contract for F3/F6; author branch/stage graph before implementing controls. | Answer then reason, restart at exact stage, no unopened-key leakage, accessible static/transcript form and branch-aware evidence. |
| A5, bounded checker and authored diagnostic tests | One F2/F8 domain followed by F9 misconception rules; reuse authoring proposal and journal owners. | Correct equivalents, wrong required form, misconception cases, invalid syntax, unsupported input and checker failure. Preview, expected diagnostic tests, acceptance/undo and pinned variants. |

These are recommendations from the audit, not authorization to copy libraries,
install services, alter all scoring at once or close human acceptance gates.
F4/F5/F10 remain visible with their named promotion triggers. Wider CAP work
stays with the absorption synthesis rather than becoming a second queue here.

Every promoted unit must pin current owner-file fingerprints before editing,
preserve concurrent changes, validate the temporary candidate and accept writes
through the applicable atomic/journal owner. Schema and scoring changes name
version and historical-evidence behavior. Native and rich preview must exercise
the same semantic answer. Accepted artifacts remain local and inspectable.

## Reuse and maintenance

Prefer native implementation of the documented patterns before importing donor
code. H5P's inspected license is MIT, but its declared dependencies still need
separate review. PrairieLearn's pinned license distinguishes AGPL client/CE,
MIT portions and third-party material. STACK's pinned license is GPL v3.
Runestone's license was not resolved in this bounded pass. Any future copying
needs file-specific license/provenance, dependency, attribution, update and
recovery review; none is authorized by this audit.

## Verification and limits

New audit probes verified W1's missing word bank in `_form_controls()`, W2's
zero stored/restored build draft and exact-order runtime behavior. Duplicate
build text is already linted and is not reported as a new defect. No production
source changes or full-suite rerun were needed for this documentation audit.
Prior full-preflight failures remain open evidence in the backlog.

The audit's quick preflight passed every gate it ran, skipping full Python,
JavaScript and clean-tree gates as configured. The existing Python inline HTML
test and all eight focused inline/bucket JavaScript cases passed again. Those
passing control tests coexist with W1's untested normal-path delivery and W2's
separately reproduced recovery defect. Whitespace checks passed.

The large parser, runtime and quiz modules were sampled by symbol. Branching,
media capture, scientific simulations and live installed behavior were not
freshly exercised. Authoring proposal inspection establishes existing lint/diff/
fingerprint infrastructure, not complete new-family authoring acceptance.

Recover this audit by removing this report and its new links only. Keep the
earlier backlog, source candidates and unrelated working-tree edits. Next
concrete unit is A1, followed by A2/A3 contracts and their complete journeys.

## A1 repair evidence, 2026-09-29

W1 and W2 now have source and packaged repair evidence. `installDraft()` installs
the word bank on the ordinary native answer form, preserving the POST route and
token. Storage refusal still leaves the enhancement and dropdown usable. Native
build selects and served dynamic build controls share validated order drafts,
including empty positions; successful dynamic acknowledgement clears the draft,
while refused submission retains it. Existing parser and scoring semantics did
not change. Only the quiz source and two new owning test files were changed.

The Python served integration test passed against source and a freshly built
disposable `.pyz`: two normal forms, refused-token retries, formal withholding
on the quiz page and two runtime response events. All 88 JavaScript cases
passed, including three new normal-baseline/draft-recovery cases. Existing
inline HTML, scoring and serve suites passed. Quick preflight passed every
gate it ran. Full preflight was not repeated in this repair; earlier unrelated
theme/dirty-tree failures remain recorded, and no clean full-suite pass is
claimed.

The packaged quiz module matched live source bytes. Its SHA-256 is
`8e695bce9d4118e85c9fa759b2a421c5f5f2856929d1d02c64529bf1a2182c5f`.
Archive SHA-256:
`ab4189d2450003f58b5358dcb53588ccf1c819b6a49e7637894d9097eba1458a`.
The browser opened the ordinary packaged page with its baseline intact, dragged
three duplicate-label assignments, used the dropdown for the fourth, reloaded
and submitted through the runtime. A partial build with only position 2 filled
survived reload and a desk/back detour without moving that step. Completing
and submitting it produced the second response event. Both events were recorded
exactly once. The quiz receipt withheld correctness in exam mode.

Ignored evidence in `dist/a1-recovery-20260929/` includes the actual rendered
word-bank and restored-build screenshots, the 88-case JavaScript log and a
source patch isolated from pre-existing edits. The browser fixture requires
a terminal/PTY for `--browser-hold`; a pipe-only invocation reaches EOF and
cleans up immediately. Only the owned fixture process and tab were stopped.
The installed learner app was not changed. Native-shell and human screen-reader/
physical-touch acceptance remain open. No commit, push or release occurred.

### R1: newly reproduced cross-surface exam disclosure

During the unfinished exam, the desk detour showed a recent-activity row with
`Answered q1 (correct)`, even though the quiz receipt withheld the verdict.
`surfaces/home.py:_activity()` formats the raw event score without a disclosure
projection. This is a newly observed cross-surface defect, not a claim that W1
or W2 repairs failed. It prevents complete formal-mode journey acceptance.
Repair through a runtime-owned disclosure projection, and audit the related
Home/Activity/report routes before expanding question semantics. Preserve
raw events and local reviewer authority. The successor packet owns this first
gate and the subsequent A2 matching workflow.

## A2 implementation evidence, 2026-09-29

R1's original browser reproduction was repeated under the disposable W1/W2
PTY fixture: Home showed `Answered q1 (correct)` after one of two exam items.
Runtime now owns the shared release decision, evidence projection and report
projection. Home activity withholds score text and Home recommendations exclude
unreleased events before deriving score-based advice. Session report CLI/API and
HTML use the same runtime release decision; the global report filters withheld
events, and the report gate split follows that decision too. Missing or unreadable
silent-mode sessions fail closed. Activity is the existing maintenance-journal
metadata surface and does not read assessment scores. Raw evidence is untouched.
No installed session or learner file was used.

A2 is an additive version-1 MATCHING declaration on dnd, not a new item type or
scoring authority. It names choice IDs/text, once/unlimited reuse and stable row
IDs. Every row is required; unused choices are supported distractors. Duplicate
labels remain separate identities, displayed with IDs. Parser/lint, content
fingerprints, public schema, native controls, rich controls, form adapters and
runtime validation/checking agree on the ID mapping. Invalid capacity, missing
rows and foreign IDs refuse without new evidence or cursor movement. Existing
dnd and exact-order build semantics and old evidence remain unchanged.

The authored two-task test uses the real bounded-authoring proposal, lint and
quality gates, review diff, exact write-ID approval and transactional shadow
writer on disposable synthetic files. Practice wrong-answer hold and correct
revision pass. Native served exam tasks cover invalid capacity/token refusals,
preserved answers, revision, exact process restart/resume, released completion
report and two exact raw ID responses. Tests name malformed versions, duplicate
members/IDs, key reuse, unknown choices, missing/padded responses and fingerprint
changes. No partial-credit or unmatched-row semantics were introduced.

Served matching drafts use the public declaration signature and row/choice IDs. They preserve
partial mappings through reload and detour, retain refused work, clear only on
acknowledgement, and visibly refuse stale declarations. Storage refusal preserves
the native form. Static build remains a preview that saves no learner state.
This adapts upstream lifecycle and authored-case patterns from
the pinned audit without copying or installing donor code.

Fresh packaged HTTP and browser journeys passed using ordinary native forms.
The browser restored a partial first mapping, disabled the occupied choice in
the second row, preserved both choices through a desk/back detour, withheld the
verdict on Home and the unfinished report, kept Activity metadata-only, accepted
the second reusable task and displayed the completed 2/2 report. Both raw
responses were recorded exactly once. The live pointer drag attempts produced
no visible change; raw CDP drag interception is unsupported in this browser
harness. DOM drag/capacity cases pass, but live pointer drag is NOT accepted.
This is retained as a separate verification limit, not hidden by the native
control pass. One in-app Back action returned about:blank; reopening the observed fixture
URL restored the exact same draft. Do not interpret that harness observation
as a current restriction on another browser. Screen-reader, physical touch and installed-shell acceptance
remain human/external gates. The whole F1 family is not closed.

Source/package byte checks cover all seven owners below. Archive SHA-256:
`df9c0beeb8864c4cd00b78b96467ac5450dcea7af84ded353b775736bc55e0bc`. The earlier A1 archive retains its dated scope.

| Current owner | SHA-256 |
| --- | --- |
| model.py | 872200831a77af02716eac502a8f6aeea805aace7c4a42014c290dc3b3282ebb |
| runtime.py | 824f5f840c9b0455c4209cbd99a390b1222eea6dd2c35fc3a0dbae0300c50ca8 |
| schemas/item.schema.json | 481c7c4730324dbd92a90ea4656da60f5da535266a88eeb28af7e68e619cece9 |
| surfaces/home.py | 24307ce5b56d0e4351392d4803b1a7b585b57fc3feb6f974e2a089bb5c2c95e3 |
| surfaces/session.py | 99a24f53f09767534d6b22683ef914b7ba52873ef504c9c9d890ef229d376ad0 |
| surfaces/daemon.py | 2dcf753b8142403fa56a8ea15f912dca2fc9a0a9eea4ff97dc9783c8eafc2821 |
| surfaces/quiz_page.py | 59b66f92215374247b129ceca1a19d8829cce427767976bd783ff3f80912adcd |

Changed task paths: model.py, runtime.py, schemas/item.schema.json,
surfaces/home.py, surfaces/session.py, bounded daemon adapters/report policy,
quiz matching/draft helpers, tests/question_workflow_recovery_roundtrip.py,
tests/matching_workflow_roundtrip.py, tests/js/matching_workflow.test.mjs and
this backlog/audit/STATE/successor route. Quiz and daemon inherited edits were
preserved. The large modules were sampled by named symbol, not read whole.
Owning Home, protocol, scoring, agent and serve suites passed. All 92 JavaScript
cases passed before the final integrated preflight. One final full preflight executed all 157 Python files: 154 passed and three
failed at the same theme expectations already recorded by the predecessor:
config_roundtrip (default source expected #0e6e62), daemon_roundtrip (reset
expected the old default), and cross_subject_suite_tracer (the existing theme
page fingerprint baseline). This task changed none of those theme defaults or
fixtures. The dirty-tree gate also failed, as expected for inherited and scoped
uncommitted work; no authorization exists to clear it by committing. All other
executed gates passed, including all 92 JavaScript cases. The focused four-case
matching suite additionally confirms the served draft lifecycle and that static
preview saves no state. CI-only optional dependency installation and the full
published-schema shell pipeline remain unrun. This is not a clean full-preflight
pass. The exact failure log is in the ignored evidence directory.

Ignored evidence lives in dist/a2-matching-20260929/, including the unfinished Home and completed
report screenshots, exact browser response events, package and final gate logs.
Recovery is task-only.patch in that directory, a bounded code/test diff against
the verified input fingerprints;
retain all concurrent edits and the predecessor's W1/W2 repairs. No commit,
push, merge, installation, release or donor-library copy occurred.
Next concrete unit is [A3 ordering/Parsons](NEXT-ORDERING-PACKET-2026-09-29.md).

## A3 structural ordering evidence, 2026-09-29

The user authorized implementation and parallel work. The contract, controls
and theme-gate repair used disjoint writers; the integrator owns adapters,
authoring/gate tests, package checks and these records. Shared learner files,
the installed app and unrelated edits were preserved. Large production modules
were read by symbol windows, not whole-file review.

Version-1 ORDERING declarations add stable block IDs, required IDs and acyclic
dependency edges to build items. Duplicate labels remain separate identities.
All topological orders satisfying the requirements are correct; selected
distractors, omitted required blocks and violated dependencies have distinct
runtime categories. Duplicate or unknown response IDs refuse before session
or evidence mutation. Existing exact-text build behavior stays unchanged.
Raw new response evidence preserves IDs and checker_version 1, including lesson
gates. Public items withhold the graph and carry an opaque content revision.
Graph-only edits invalidate drafts without exposing the graph.

Native position selects, separate Add controls, drag handles and Remove/Up/Down
controls preserve partial positions, focus and scoped drafts. Refused responses
retain work; acknowledged advancement clears it, including silent-mode API
responses. Runtime diagnostics appear only when released in practice. Exam and
diagnostic submissions and unfinished reports withhold them. Offline ordering
is an explicit preview requiring a served runtime to submit. Structural version
1 does not execute code, validate indentation or assign partial credit.

The two-task authoring gate exercises cited proposals, lint, bounded diff,
plain/native preview, exact write-ID approval, transactional writes, stale-write
and stale-undo refusal, and byte-exact undo. Contract tests cover malformed JSON,
cycles, duplicate edges/IDs, missing definitions, limits, legacy verdicts,
private graph revision and silent-mode sanitization. Gate and legacy serving
recorders now share runtime construction refusal; invalid input writes no event.
The published lint namespace adds invalid_matching and invalid_ordering codes.
Three stale theme assertions were repaired against the current default while
retaining custom-color and refused-write protections.

Fresh portable archive SHA-256:
`ac17ac70807dbbcb3c5848e8af0ccd269252a5ea1b11ff74d3983b99694f19da`.
All eleven changed production/schema owners match packaged bytes exactly;
hashes live in `dist/a3-ordering-20260929/final-fingerprints.json`.
Packaged exam and practice HTTP journeys pass, including invalid/token refusal,
retry, disk restart, released diagnostic categories and raw checker version.
Native diagnostic launch remains unsupported by the existing daemon route;
diagnostic disclosure is verified through the runtime/session contract instead.

The final package's Chrome browser journey used actual matching drag, rejected
forbidden reuse, restored after reload and completed both matching tasks at 2/2.
Ordering Add/Remove/Up/Down and native selects survived reload and desk/back,
submitted both alternate orders, left the distractor unused and completed at
2/2. Four exact raw responses were recorded once each, with no early exam
verdict. Browser evidence and screenshots are retained in
`dist/a3-ordering-20260929/`, including final-package-browser-evidence.jsonl,
matching-final-package-report.png, ordering-final-package-draft.png and
ordering-final-package-report.png.

Actual structural ordering drag is NOT accepted. Both Chrome and the in-app
browser placed a block into the first position but canceled later-position
drops. Dedicated handles, explicit copy effects, target outlines and key-free
live drag status were added and pass deterministic DOM tests. Live cancellation
remains a concrete acceptance gap; neither its cause nor a complete drag journey
is claimed. Native controls work. Physical touch, screen-reader, installed-shell
and learning-transfer acceptance remain separate gates.

Final full preflight executed 166 Python scripts on the frozen production
candidate: 163 passed and three stale assertions failed (day_edit default color,
lesson_code CSS text mistaken for an editable control, and note_promotion's
historical settings-default reconstruction). Their corrected full targeted
scripts pass. The frozen note-promotion baseline was not rewritten: its test
verifies the exact authorized current defaults and restores only those two
historical values in a schema copy before checking the original digest. Static
lesson checks inspect actual button/textarea markup rather than CSS selectors.
The initial JavaScript gate also failed because hint_ladder banned aria-disabled
across all quiz code, including unrelated ordering handles. It now checks the
actual hint rendering section. A final complete Node run passes all 100 tests.
No production bytes changed after the final package/full run. Full preflight
was not repeated after these test-only repairs. The clean-tree gate fails for
preserved shared and task edits; this is not a clean full-preflight pass.
Final quick preflight and diff whitespace checks pass.
CI-only optional dependency setup and the published-schema pipeline remain
unrun locally. Two earlier full runs were interrupted before completion for
concrete wording and pointer repairs; their logs are retained and are not
successful gates. No commit, push, merge, installation or release occurred.

Recovery is `dist/a3-ordering-20260929/task-only.patch`, a bounded source/test
diff against verified A2 archive inputs, before snapshots and clean HEAD test
inputs. Input hashes are retained beside it. Reverse only reviewed task hunks,
never reset the shared checkout. Concurrent research/source work retains the
owners in the absorption programme's PARALLEL-IMPLEMENTATION packet.

Operational findings: the in-repo schema validator supports a restricted
vocabulary, so conditional if/then/else is unsupported; the ordering schema
uses supported oneOf alternatives. Single-scorer/writer scanners also inspect
ignored Python files, so recovery copies use .txt extensions. An initial .py
recovery copy triggered the duplicate-writer gate; renaming it restored the
gate without changing the scanner. Concurrent full day-edit test invocations
hit an existing 15-second CLI timeout; the serial corrected script passed
without changing that timeout.

The next contract slices are [A4 staged answer/reason](NEXT-STAGED-PACKET-2026-09-29.md)
and [A5 bounded polynomial checking](NEXT-CHECKER-PACKET-2026-09-29.md).
These are implementation proposals with explicit schema, commitment, unresolved
outcome and disclosure decisions. They do not close F3/F6 or F2/F8/F9.

A1's implementation is frozen and its named shared source/schema paths are
released to the existing A5 integration owner in the parallel absorption
packet. Verify the recorded fingerprints before further wiring. Broader course
package restore work remains with that integration owner; this ordering package
journey does not certify it. Structural drag remains an unmet original A3 gate.


### Structural drag closure diagnosis, 2026-09-30

The wrap-up requested a read-only diagnosis while A5 owns shared source. Only
`tests/js/structural_drag_closure.test.mjs` and this append were written. The
audit base SHA-256 was checked as
`7bf381a4ae4f46c81aaac836b1d61506d658380ddbb68561ffca0a61417b1f84`.
No shared parser/runtime/quiz/daemon/test, STATE or backlog was edited. No full
preflight, build, install, commit, push or real learner write was performed.

A disposable source daemon and a read-only loopback proxy served the same
native ordering page. The proxy adds a DOM event trace only and refuses POST.
Its unmodified variant observes browser events without dispatching any drag
or drop. Its optional proposal variant installs the one proposed dragenter
hook on the existing native labels; it retains the actual shipped dragover,
drop, local-source and disabled-control guards.

Actual pointer input in both Chrome and the in-app browser reproduces the
later-position failure. The destination receives trusted dragenter events on
its label/select, then dragleave and dragend. It receives no final dragover or
drop. The current renderer accepts the destination only in ondragover, so an
arrival followed immediately by release is not accepted. This explains why
an earlier position, crossed during the pointer path, can work while the final
position cancels. The failure is tied to the observed event sequence; a physical
mouse or touch acceptance claim does not follow from this automated trace.

The fixture-only proposal sets `label.ondragenter = label.ondragover`. Real
pointer input then produces trusted, prevented drop events with copy effect
at step_1 and step_2 in both browser surfaces. Consecutive drops into all three
positions produce the exact native values start, right, left, and reload
restores them with focus. These are real browser-input observations on the
proposal fixture, not mocked event-dispatch acceptance. Production and packaged
acceptance remain open until A5 applies the shared change and verifies it.
The read-only fixture deliberately does not submit or record a score.

Minimal proposed shared-file patch: add the following line immediately after
`label.ondragover` is assigned inside BOTH installOrderingControls copies in
surfaces/quiz_page.py (OFFLINE_JS and SERVED_JS):

```diff
         label.classList.add("ordering-drop-active");
       }
     };
+    label.ondragenter = label.ondragover;
     label.ondragleave = ()=>{ label.classList.remove("ordering-drop-active"); };
```

No new acceptance predicate, external payload trust, scoring rule, schema or
write path is needed. Reusing the handler preserves the local dragged-ID and
unlocked-select checks and the explicit copy effect. The checked source at
start was bf33a8c7b10e8ce72a58aeadb40dec30a417bfb0f2e984940949630db776f975;
A5's concurrent wiring later changed its whole-file hash to
200a3f35ef36e717cea533ba271752dd695a4d423d65d8402cfd974c4b573a78.
The two sampled ordering drop-handler windows still match the proposal context.
A5 must check its current source before applying the two insertions.

`node --test tests/js/structural_drag_closure.test.mjs` passes two focused DOM
checks: consecutive child-select bubbling with exact identities, and the
missing-dragenter/proposed-hook comparison including external-input refusal.
These mocked DOM checks support the regression contract only. They do not
substitute for the separately observed actual browser drops. The diagnostic
can be rerun with the existing ordering workflow's browser-hold source daemon
and `node tests/js/structural_drag_closure.test.mjs --browser-source URL`, adding
`--accept-dragenter` only for the fixture-only proposal comparison. The tool
trace and screenshot of the proposed Chrome draft are retained in this chat;
the temporary screenshot is /tmp/itembank-structural-drag-closure-20260930.png.
A5 retains implementation and final verification ownership.
