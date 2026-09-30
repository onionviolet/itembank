# A3 course workflow implementation evidence

Date: 2026-09-29, America/New_York. Authority: the parallel implementation ownership packet and the user's instruction to implement accordingly in parallel. This records source implementation, not installed, packaged-runtime or human acceptance. No commit, push, installation, release, external account write or real learner-file mutation was performed.

## Scope and authorities sampled

Read the ownership packet first, applicable AGENTS instructions, `.planning/EXEC-CONTEXT.md`, `.planning/AGENT-WORKFLOW.md`, current STATE entries, absorption reports 03 and 05, OpenTutor GAP-INVENTORY L07-L11/L20 and the LearnHouse fork UI audit. Sampled SOURCE-TO-COURSE core-loop and treatment obligations, USER-VISION wrong-answer reselection and exact-resume direction. Read symbols and focused windows in course, graph, journal, model, runtime, retention, evidence, and daemon rather than claiming a whole-module audit. These research documents are comparison evidence; no donor code, assets or dependencies were imported.

The checkout was already dirty, including course_workbench and agent_operation. A recoverable before snapshot and SHA-256 manifest were captured before editing the A3 files, at `/var/folders/zg/7y5nnphj6bd6bcxgm4tmgv280000gn/T/itembank-a3-before-y80j15_j`. That snapshot includes all seven originally assigned Python paths. It preserves earlier uncommitted work and is the baseline for the hashes below. A5 should retain the snapshot through integration. Do not use HEAD as the recovery image for these dirty inputs.

## Implemented seams

| ID | Concrete result | Authority and recovery |
| --- | --- | --- |
| F1 | `course_workbench.readiness` joins registered course/source/lesson state, current source rights, binding and artifact links, native source coverage classification, and the same lesson/bank lint inputs used by the CLI. Exact paths, binding rows, item references and lint codes are repair pointers. Clean, unknown, missing, invalid, warning and failed-check states are separate. The map now includes the joined panel. | Read-only and disposable. Synthetic before/after tree hashes prove no writes. Check exceptions become error rows, not zero findings. No repair or acceptance is performed by this view. |
| F2 | `agent_operation.propose_course_outline` and `course_workbench.outline_panel`/`outline_action` implement editable outline positions and additive treatment choices with visible diff, preview fingerprints, cancel, accept and undo. Adequate direct-reading bindings stay byte-equivalent as records. Objective IDs/statements and source records remain intact; imported objective reordering is refused until the existing overlay/migration workflow is used; no lesson generation is implied by choosing a treatment. | Accepted writes use `course.write_course` and its existing CAS/journal. Current rights and source bytes are checked again at acceptance and its precommit hook. Changed course/source/rights and stale preview are refused. Restart reloads the existing durable proposal store; undo restores prior accepted bytes through the existing journal. Report-only policy remains authoritative. |
| F3 | `course_workbench.review_history` and `retention_view.course_review_history` join saved sittings to live response/mark/reading history and the existing retention derivation. Responses, missed settled responses, pending prose, withheld formal responses, reading declarations and unavailable durable self-rating remain separate. Source and lesson origin labels are explicit; sitting resume links carry exact bank stem, mode, session and course. | Uses canonical sitting admission, real-path deduplication, evidence event identity, runtime feedback-release policy, and existing retention verdict/forecast authority. No answers, keys, rubrics or inferred misconception pairs are displayed. Active formal feedback stays withheld. Corrupt/unsupported evidence or unavailable sitting ownership makes due recommendations unavailable rather than presenting a partial history as clean. Duplicate admitted routes cannot acquire a guessed resume link. |
| F4 | `prototypes/audit-course-tutor/tutor.py` implements an isolated cited tutor context and native preview. It includes the public item, already-released authored feedback, rights-checked source text/locator, private unsaved reflection and exact sitting return. | Prototype only, no production route or model transport. Reads through the existing runtime/session adapter without unlocking a tier, recording a grade or writing evidence. Formal-test teaching remains unavailable and carries no citations. Source text never leaves the machine. |

Changed production files: `surfaces/course_workbench.py`, `surfaces/agent_operation.py`, `surfaces/retention_view.py`. New scoped tests: `tests/a3_course_workflows_roundtrip.py`, `tests/a3_course_tutor_roundtrip.py`. New isolated prototype: `prototypes/audit-course-tutor/tutor.py`. Originally assigned study/course_ops/authoring/blueprint files were not edited. Shared daemon/parser/runtime/schema/source/package files, STATE, README and backlogs were not edited by this lane.

## Focused verification

Before editing, both `python3 tests/course_workbench_roundtrip.py` and `python3 tests/agent_lesson_revision_roundtrip.py` passed. This preserved the existing HTTP author-preview/correction journey, source-staleness refusal, restart, acceptance, package export/restore and undo behavior.

Successful final source checks:

- `python3 tests/a3_course_workflows_roundtrip.py`: synthetic read-only healthy/broken/failed readiness, caller-target refusal, native editable proposal, stale preview/course/source/rights refusals, direct-reading preservation, cancel/accept/restart/byte-identical undo, pending prose, saved wrong responses, due objective derivation, active formal withholding, exact resume, ambiguous route refusal and corrupt evidence error.
- `python3 tests/a3_course_tutor_roundtrip.py`: read-only public item, wrong-response released hint and cited source, formal teaching refusal and exact return context.
- `python3 tests/course_workbench_roundtrip.py`: existing loopback source/map/evidence navigation and native author review/accept/undo/conflict/report-only journey still pass with the new map and evidence joins.
- `python3 tests/agent_operation_roundtrip.py` and `python3 tests/agent_lesson_revision_roundtrip.py`: existing lifecycle, source-grounded paragraph correction and synthetic package restore still pass.
- `python3 tests/retention_ui_roundtrip.py`: existing retention/report and pending/owner separation pass. `git diff --check` on the touched production paths passes.

The malformed evidence warnings printed by the A3 synthetic test are intentional corruption fixtures, not an unexpected gate failure. No combined preflight was run; A5 owns that gate. No packaged `.pyz`/installed-app check or browser screenshot, touch, screen-reader, zoom, aesthetic or learning-transfer acceptance is claimed.

Intermediate failures, corrected and rerun: course_workbench initially failed on a mocked resume payload lacking `state`; the new projection now marks that state unavailable. The first A3 review test revealed duplicate counts because macOS temporary roots had both `/var` and `/private/var` spellings; evidence log paths are now canonicalized before reading. A hand-check found that active formal result labels needed the runtime release gate; the final test now explicitly asserts withholding in both the row and aggregate counts. A final `python3 tests/retention_ui_roundtrip.py` rerun failed at a disposable daemon launch with "daemon never printed a URL" and empty output. The same command passed on the next isolated run. Its cause was not established, so this is retained as a transient launch observation rather than a code-repair claim. No test failures remain in the latest completed runs above.

## Exact A5 wiring requests

| ID | Shared owner request | Acceptance gate |
| --- | --- | --- |
| A1 | In `daemon._course_area_extra`, keep the current build/agent author surface. For the **build** area only, append `course_workbench.outline_panel(course_dir, course.read_course(course_dir)["doc"], selected_outline_proposal_id)`. Read the opaque ID from `?outline=...`. Map/readiness and evidence/history are already mounted through the existing `details` call. | Native build shows real objective statements, editable positions/treatments, source choice, locator, exact diff and cancel/accept/undo. It must show typed unavailable errors rather than turning a failed read into an empty outline. |
| A2 | Add loopback write-gated native POST routes `/course/<cid>/outline/{propose,accept,reject,undo}`. Resolve cid with the existing admitted-course owner, flatten form fields to single strings and reject duplicate fields. Call `course_workbench.outline_action(course_dir, action, fields, settings.load_settings(handler.root), reviewer=the existing human actor label)`. The adapter validates field names, objective identities/order, course/draft fingerprints and proposal kind. Redirect to `/course/<cid>/build?outline=<opaque proposal_id>#course-outline-proposal`; show typed refusals without an accepted-file write. Use the existing route/write-gate and parity conventions. If published operation/schema wiring is needed, A5 owns that extension. | End-to-end native form: preview, one corrected treatment, stale preview refusal, cancel, fresh preview, accept once, server restart, reload and undo to exact prior bytes. Local adapter coverage already passes; POST routing is not implemented in A3-owned files. |
| A3 | Honor the `return` query on the existing lesson route as a safe local, admitted `/quiz/<stem>?mode=...&session=...&course=...` return link, validating exact session/bank/course ownership through existing authorities. Review history already supplies this encoded return URL and separately displays the exact resume link. | Wrong response, permitted cited lesson, explicit exact-sitting return, restart and resume at the next/preserved cursor. An active formal sitting must not widen its feedback grant. This explicit lesson-return button remains unverified until shared wiring lands. |

The tutor stays isolated. Mounting it or invoking a model requires a separate operation manifest for roots, exact source spans, current remote-process/transform rights, egress, release policy, latency/cancel behavior and recovery. It cannot settle scores or turn source snippets into accepted course truth.

## Retained dispositions and triggers

Core ready source seams: joined readiness and review projections, additive treatment-proposal engine/native form adapter. Shared native routing and explicit lesson-return integration are blocked on A5 ownership, with exact requests above. The cited tutor is a reversible prototype, not an accepted tutor backend. Durable FSRS card-by-card UI, notification delivery, learner-specific difficulty policy, inferred confusion pairs and learning-transfer claims stay backburner until stable card/session/objective identities, a named authorized delivery/notification job, representative learner evidence and the corresponding runtime/policy contracts exist. The current view does not invent those capabilities from a response count or self-rating. No whole-CAP/OpenTutor/LearnHouse acceptance is recorded.

Recovery: restore only this lane's changed files from the before snapshot if rollback is needed, preserving any subsequent owner edits; the new A3 test/prototype files were absent at baseline. Synthetic operation recovery is tested through the existing proposal reject and journal undo paths. A5's next action is to apply the three minimal shared wiring requests, exercise the combined native journeys and run the single stable-candidate preflight.

## Fingerprints

SHA-256 values below use the captured dirty input, not HEAD. The evidence file itself is a new dated record.

| Path | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| `surfaces/course_workbench.py` | `fc31bfd04f94faaee2ccfa5caeda018deac4f148325d464ba3b5be0b93c0fea8` | `03545ef5ed6a7a331fa7b888293e62058c272bdcbb748d8061d9285a6b28fc81` |
| `surfaces/agent_operation.py` | `0e47a1147816d9c94e2706aefb2c9604a080c3337e7836ff807ac12e7ed9259a` | `acb8baa90e282b50d2f1a8cc72a824904d327d2b0f5d70e33b95597e790ed1a4` |
| `surfaces/retention_view.py` | `ffdfa2480232fcf746528eeff872d5436bd9620e69b56024a69b9d8225a270d6` | `5c420605bc112fb9d3ffd60e77dc8684baa235b9dd6bfc242757e8e76d535507` |
| `tests/a3_course_workflows_roundtrip.py` | `absent` | `a799a5211cbd2992df32e09c24247acac91b8767f8135e25069614350ec1e2a7` |
| `tests/a3_course_tutor_roundtrip.py` | `absent` | `c63f0e5bf2ee2eb353a0ac2e0f0e268d02b02b89c07c1d759d66b089ed515290` |
| `prototypes/audit-course-tutor/tutor.py` | `absent` | `29aafbf600a0534308a521f9a1973e1b5a5969be05e0c75360f159a2e98d3f75` |
