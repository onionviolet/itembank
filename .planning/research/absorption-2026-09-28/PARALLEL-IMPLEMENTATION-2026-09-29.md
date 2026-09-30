# Parallel audit implementation dispatch

Date: 2026-09-29. User instruction: "implement each accordingly and in parallel using new chats as needed".

This is an execution ownership packet for the existing capability and question backlogs, not a replacement queue or acceptance record. Read AGENTS.md, EXEC-CONTEXT.md, the current STATE entries and the exact cited contract sections. Preserve all shared edits. Base HEAD at dispatch is `8ccd45832b66b0b86bb406d6232ef0633ef71dc3`; each writer records live dirty-input hashes and a recoverable before snapshot before editing. No commit, push, merge, installation, release, real learner-data mutation or external account write is authorized by this dispatch.

## Ownership

| Lane | Writer and scope | Gate and dependencies |
| --- | --- | --- |
| A1 ordering | Existing chat `01a0f02c-714d-77c1-8d08-2fa1ea1dd5ba`, Find the next gap wave. Owns active ordering parser/runtime/schema, quiz/session/daemon/evidence integration, question workflow/backlog records, README, STATE and theme failure repair. | Existing NEXT-ORDERING-PACKET gate. Do not duplicate its implementation or full preflight. |
| A2 richer questions | New question-family chat. Initially owns only `prototypes/audit-question-families/`, its scoped tests and dated evidence in this research directory. Once A1 finishes, production parser/runtime/schema/quiz changes need a recorded ownership transfer from the integration chat. | Implement and test reversible synthetic staged-answer, multiple-blank, bounded checking/diagnostic and branching slices. Keep F1-F10 dispositions and unmet objective/domain triggers explicit. No competing parser or scorer: production scoring stays in runtime; isolated prototypes cannot settle learner grades. |
| A3 course workflows | New course-workflow chat. Owns `surfaces/course_workbench.py`, `surfaces/agent_operation.py`, `surfaces/retention_view.py`, `surfaces/study.py`, `surfaces/course_ops.py`, `authoring.py`, `blueprint.py`, their scoped tests and dated lane evidence. | Read-only readiness and durable review journey, direct-reading versus lesson treatment, bounded author corrections. Implement missing seams only. Propose contextual tutor as a synthetic isolated prototype if production wiring needs unowned modules. |
| A4 source and recovery | New source/recovery chat. Owns `surfaces/open_notebook.py`, `source_adapters.py`, `notes.py`, `course_package.py`, scoped tests and dated lane evidence. | Pinned disposable local companion if feasible, explicit source inclusion, exact citations/notes, rights-aware transfer and clean offline restore. Any bridge is read-only until identity/rights/recovery are proved. Do not install large services or copy donor code merely to claim connectivity. |
| A5 integration | New integration chat. Initially owns only this packet and its dated integration evidence. Once A1 completes and A2-A4 publish ready evidence, owns shared routing/package integration and necessary minimal wiring patches. | Inspect actual diffs and hashes, integrate family contract changes sequentially, prove source/package journeys, then run one final full preflight on a stable combined candidate. Preserve active installed app and real learner sitting. Human touch, screen-reader and learning-transfer gates remain human-owned. |

## Parallel rules

Dispatched local chats: A2 `01a0f047-1a5f-7162-9fa0-192484393b03`, A3 `01a0f047-225b-7b72-8682-722168889d84`, A4 `01a0f047-2a08-7412-95b9-6a6a89e4f54c`, A5 `01a0f048-1de1-7932-a29b-47917e192787`. A5 receives the dependency IDs in its prompt and owns coordination through compact progress reads and lane evidence. Workers freeze their changed inputs when returning completion; additional shared wiring remains with A5 after ownership release. The dispatch author releases this packet to A5 after creation.

One writer per file. A2-A4 may not edit `model.py`, `runtime.py`, `evidence.py`, `surfaces/quiz_page.py`, `surfaces/session.py`, `surfaces/daemon.py`, schemas, theme/settings, README, STATE or shared backlog while A1 is active. They return exact minimal wiring requests in their evidence files; A5 applies or explicitly transfers ownership after A1 releases the files. A3 and A4 do not edit `course.py` or `journal.py`; request a scoped change from A5 when required. New tests use distinct lane names.

Workers are not alone in the checkout. Never revert other edits, reset, clean, switch branches or stage shared work. Use existing deterministic authorities and CAS/journal controls. Run focused gates while building. Only A5 runs the combined full preflight after inputs settle; A1 may complete its already-running gate first. No continuous unchanged-state polling. A gate failure, an unsupported condition and an unrun human check are distinct outcomes.

## Completion evidence

Integration status is owned by `A5-INTEGRATION-2026-09-29.md`. Final verification is recorded in its September 30 wrap-up section. The
original full preflight failed; targeted repairs pass, and dirty-tree/app-build
limits remain explicit.

| Lane | Ownership and delivered state |
| --- | --- |
| A1 | Completed, frozen and released. A5 verified the released parser/runtime/quiz/daemon fingerprints and captured before images before shared wiring. |
| A2 | Completed and released. P1 is integrated in source as explicit opt-in inline fill, with authored marker validation and existing runtime response/scoring. P2-P5 remain executable prototypes with unpassed production contract gates. |
| A3 | Completed and released. Readiness/history are mounted by existing details routing. A5 integrated native outline review/accept/cancel/undo and admitted exact-sitting lesson return; ordinary source HTTP/restart/undo gates pass. |
| A4 | Completed, files frozen and released. A5 repaired archive schema access and note-only private backup/locator closure, and proved clean packaged native context and note recovery. |
| A5 | Source and bounded owner reconciliation completed and frozen. Shared native routing, research selection/notes, P1 inline layout and guarded structural drag are implemented and focused-tested. STATE/A5/dispatch ownership is now released to wrap-up chat `01a0f075-e39e-7801-8767-adea4d73134a`, which owns the pending one source-only combined gate and final result projection. Build hold remains active. |

Each lane returns changed paths, before/after fingerprints, exact successful and failed commands, source versus packaged proof, unresolved gates, and a concrete dependency request. Keep ready production work, prototype evidence and objective-dependent backburner capabilities distinct. A5 updates existing owners after other writers finish, preserving dated historical evidence. Do not mark the 27 capability groups or F1-F10 wholly accepted from a bounded slice.

September 30 gate transfer supersedes the dispatch-time "only A5" full-suite
rule for this one source-only run. Wrap-up owns it; no equivalent full suite
runs in this chat. Its actual results are now recorded in the existing A5/STATE owners.
Fresh archive, installed and human acceptance remain separate deferred gates.


September 30 wrap-up is complete: released source integration, the full
source-only run, full diagnostic-tail visibility and all targeted repairs are
recorded in A5 evidence. All 166 executed Python scripts are covered by the
full and targeted checks; the final Node run passes 106 tests. The original
full run was not repeated after repairs, and clean-tree/build/human/external
limits remain explicit. STATE holds the single ranked resume list. A5 and A1
follow-up chats have completed; no duplicate integrator is active.
