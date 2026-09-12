# Itembank improvement priorities

Date: 2026-09-12.
Status: bounded review and recommendations, not accepted implementation scope.
Request: "improvements to make right now and more?"
Routing instruction: use the efficient-agent-routing skill.

## Result and scope

Prioritize exact recovery, truthful course resume, and durable reading before
expanding source acquisition. The placement exporter already has a completed
synthetic gate in its owning record. The candidate runtime gate passed again
during this review. Reading completion and notes still reset on reload in the
reading prototype.

This review used the current checkout, live GitHub issues, the current product
contract, relevant workflow rules, and the latest reading and treatment records.
Recent vision entries include the approved study-desk direction, deferred human
reviews, optional answer banks, and orientation to the actual assessment target.
This is not a whole-vision, whole-codebase, or live browser audit.

## Ranked work

| Code | Timing and result | Evidence and observable completion gate | Proposed route |
| --- | --- | --- | --- |
| A1 | First: make undo restore the exact prior state | All four recovery observations fail today. Require creation undo to restore absence, batch reversal to account for all writes, and PDF text plus locator metadata to recover together. Preserve refusal of divergent edits. Include replay, interruption, registry reconstruction, and offline restore. | One Sol owner at medium effort for the coupled journal, director, and adapter work. Independent Astra review at low effort for the recovery contract when execution is authorized. |
| A2 | Small visible fix: make the shelf accurately say Start or Resume | `surfaces/ia.py:_healthy_card` defaults a missing cue to Not started. `course_shelf` passes the course record without a session projection. The earlier walkthrough observed this after a recorded response. Require a started course to display a truthful cue and return to the same pending item. Use canonical session evidence. Unknown must not imply never started. | One Terra owner at medium effort. Gate one synthetic course through submit, leave, and resume. |
| A3 | Main feature: preserve each reading activity across restarts | The reading prototype stores completion in a JavaScript Map and notes in page state. Define activity identity and its source-binding reference before durable writes. Require independent completion for two activities sharing one source, exact source return, idempotent declarations, and restart persistence. Keep notes learner-owned and self-reported reading separate from scores. | One Sol owner at medium effort for the coupled course and evidence contract. Review the smallest additive delta before implementation. |
| A4 | Next validation: finish one complete study session | Extend the populated session comparison in issue 20 through source reading, note, practice, permitted feedback, leave, and resume. Compare actual task success and context retention before changing the presentation again. Use a realistic synthetic unit now. Revisit real-course and human checks under their existing deferred conditions. | One Terra owner at medium effort. Independent or higher-tier work only for a specific unresolved finding. |
| A5 | Next authoring extension: export one table treatment | Placement export is already recorded complete. Typed and table export remain outside that unit. Choose a table task by its purpose, preserve exact source values and locator, review its actual downloaded bytes, and validate through the existing runtime. Explanation responses remain pending review. | One Terra owner at medium effort with the existing export gate pattern. Avoid a new item type unless an actual incompatibility requires it. |

The first recommendation reflects consequence rather than implementation size.
A2 is the smaller visible change. A3 can begin over already registered local
sources without a new import path, so its design need not wait on all of A1.
Production import integration still depends on A1's recovery gate.

For A3, the existing reading handoff identifies unresolved learner-label and
permanent binding-reference choices. This review recommends preparing their
concrete contract delta. It does not interpret the request for improvements as
acceptance of a new durable format. The proposed source of truth remains the
existing course, journal, and evidence authorities.

## Current checks

`python3 .planning/research/source-to-reading/recovery_probe.py` exited zero,
meaning the diagnostic ran. Its acceptance observations were:

| Existing reference | Observed result |
| --- | --- |
| R1 | Batch reversal returned `complete: true` and zero reversed entries while the new file remained. Failed. |
| R2 | Direct undo retained a zero-byte file instead of prior absence. Failed. |
| R3 undo | PDF-derived Markdown and locator metadata both remained. Raw PDF bytes were unchanged. Failed. |
| R3 interruption | Injected pre-commit RuntimeError returned `source.internal_error` and left a locator sidecar. Failed. This was exception injection, not process kill. |
| C1 | Divergent external bytes were preserved and undo refused with `journal.conflict`. Passed. |

`python3 prototypes/learning-treatments/runtime-candidate/validate_runtime_candidate.py`
passed on the current checkout. All three candidates linted with zero errors
and two warnings each for draft review status. Rich builds, source locators,
private-content withholding, correct and incorrect runtime responses, and
pending prose review passed. Temporary outputs were removed by the validator.
The full browser placement-export gate was not rerun. Its September 11 result
remains recorded evidence in the prototype README.

The reading reset and shelf fallback findings were inspected in current code.
The prior complete shelf journey was not rerun, so its visible symptom remains
a historical observation with a matching current implementation path.

Large modules were sampled around `journal.undo`, `director.reverse_operation`,
`surfaces.ia.course_shelf`, and `surfaces.ia._healthy_card`. No production module
was comprehensively reviewed. Existing dirty changes were preserved.

## Further candidates and revisit conditions

Course-scoped source help remains the next research candidate in
[issue 24](https://github.com/onionviolet/itembank/issues/24). Start with existing
local search and a small judged set of exact terms, paraphrases, and absent
answers. Add embeddings or reranking only if the comparison shows a useful
gain. Measure locator fidelity and unsupported-answer behavior separately.

Chapter grouping and prerequisite navigation remain prototypes under
IL-20260910-02. Compare a real outline before treating synthetic depth groups
as evidence of usefulness. Paper-note capture remains under IL-20260910-03,
with original material and corrected transcription kept distinguishable.
External acquisition remains a later option once the local reading and import
recovery path is verified. None of these candidates is rejected by this order.

The current STATE header predates the newer prototype records. Follow their
dated owning records for current completion and deferral status. A future
implementation handoff should update the current pointer without duplicating
the historical evidence. Human-review deferral permits further synthetic work
and does not certify accessibility or learning effectiveness.

## Sources, routing, and recovery

The source-to-reading implementation plan and next packet retain ownership of
A1 through A3. The treatment README owns A5. Live issue 20 owns the comparison
scope behind A4. Watching likely users complete relevant tasks is the later
human evidence route described by the
[GOV.UK usability-testing guide](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing),
checked 2026-09-12. That guidance supports the method, not a claim that any
Itembank interface is already effective.

The efficient-agent-routing skill was read from the user-specified skill
source. This review stayed in one agent context with the configured primary
model. The route proposals match the host's offered models and the skill's
Sol medium and Astra low subagent ceilings. No subagent, new task, external
write, commit, or push was used. No token or cost savings are claimed.

This new report is the only intended repository write. Its expected prior state
was absence. It records proposals without modifying accepted contracts or
learner objects. Remove this report to reverse the documentation addition.
Verification below records this report's final checks without replacing the
owning recovery or prototype records.

Final quick preflight passed every executed gate. Full Python, full JavaScript,
and clean-tree gates were skipped by quick mode. No full repository or human
acceptance pass is claimed.

## Parallel dispatch, 2026-09-12

User instruction: "parallelze/send out extra chats accordingly" with
`daisy-chain-work`. This authorizes bounded implementation tasks and cross-task
continuation for the recommendations above. It does not accept an unspecified
durable reading schema or authorize commits, pushes, or real-course writes.

GOAL: Execute A1 and A2, prepare A3's concrete contract for review, and route A5
without colliding with the active treatment task. A4 follows stable evidence.

OWNER: The coordinating task owns this index and STATE pointers. Each task owns
its lane below. Weibao owns unresolved product choices and human acceptance.

SCOPE: Use the same saved project and local checkout because required prototype
and audit inputs are uncommitted. Every task must check current dirty files and
other ownership before editing. Do not revert another task's edits or change
the shared branch. Independent test outputs use separate temporary roots.

| Lane | Exclusive write ownership | Gate and return artifact |
| --- | --- | --- |
| A1 recovery | `journal.py`, `director.py`, `source_adapters.py`, `identity.py` only if required by recovery, their named roundtrip tests, narrowly necessary recovery schema fixtures, and `research/source-to-reading/recovery-repair-2026-09-12.md` under this planning tree | Repair R1 through R3 while retaining C1. Add meaningful regression coverage for absence, replay, interruption, conflicts, paired import recovery, and registry or restore behavior. Save actual test results and independent review findings in the return artifact. |
| A2 resume | `surfaces/ia.py`, the explicitly authorized session-restoration symbols in `surfaces/daemon.py`, `tests/ia_route_roundtrip.py`, an optional new `tests/course_resume_roundtrip.py`, and `research/course-resume-repair-2026-09-12.md` under this planning tree | Reproduce the shelf symptom on synthetic persisted state, repair the projection, and verify accurate new, interrupted, resumed, and unavailable states plus unchanged session identity and next item. Report the actual diff and results. |
| A3 reading contract | `research/source-to-reading/durable-reading-contract-2026-09-12.md` under this planning tree. Synthetic experiments stay outside the repository. | Present a minimal additive contract delta with explicit activity and revision identity, permanent binding reference, source locator, learner declarations, note ownership, legacy compatibility, rights, stale state, replay, and restore behavior. Resolve technical recommendations and expose only material user choices. No production schema or completion writes in this link. |
| A5 table export | `prototypes/learning-treatments/` figure studio, table exporter and its focused verification files. Excludes chapter prototypes and production modules. The existing treatment task released ownership after committing `e7c242a`. | Use the existing scorer and a synthetic source. Preserve exact source values and locator, review downloaded bytes, and require prose responses to stay pending. Append final evidence to the treatment README. |

DO NOT TOUCH: other lanes, existing dirty vision/audit work, runtime scoring,
assessment disclosure policy, real courses or sources, external services, Git
history, commits, pushes, or package releases. No broad refactor. A need to edit
outside the lane requires coordination with the index owner first.

CONTEXT: The review above reran the recovery diagnostic and candidate validator.
All four recovery acceptance observations failed and C1 passed. The candidate
validator passed. The shelf code path still defaults an absent cue to Not
started. The reading prototype deliberately resets its local state.

EVIDENCE: The current review and owning September 8 recovery packet identify
the failing symbols and exact observed results. September 11 placement export
is complete within its synthetic scope. The September 10 reading handoff owns
the unresolved label and binding-reference choices.

AUDITS: This priorities report is a reconciled recommendation baseline, not an
implementation pass. A1 reconciles R1 through R3 and C1 in its result file. A2
reconciles the shelf finding there. A3 keeps its contract a proposal until
accepted. Preserve original observations and explicitly supersede only those
that a new gate resolves.

NEXT ACTION: Each lane checks its exact symbols and reproduces the relevant
condition before making the smallest change. Apply `daisy-chain-work`,
`efficient-agent-routing`, and `evidence-gated-handoff`. Use one implementation
owner and targeted gates. Routine work starts at medium effort. Independent
recovery review may use an Astra subagent at low effort under the routing skill.
No repeated coordinator-and-worker repository scans are required.

GATE: A lane closes only after its actual diff and focused evidence are reviewed.
Run required quick preflight at handoff and report concurrent or pre-existing
failures separately. Coordinate one full integrated validation after all code
writers stop. Retain deferred human checks as deferred. Do not wait for those
checks to continue already authorized synthetic work.

RETURN: Report changed paths, checks actually run, observed behavior, independent
review where required, remaining risks or decisions, rollback, and one next
action in the lane's result artifact. Send a compact completion message to the
coordinating task so it can reconcile the index.

CHAIN: After this dispatch closes, the A1 task becomes the chain coordinator.
It alone creates the A4 integration successor after A1, A2, and A5 have stable
reviewed outcomes. It checks task completion using bounded waits and reads the
actual returned artifacts and diffs. A failed required code gate is repaired
by its owning lane before integration. A4 uses current supported behavior
and labels any A3-dependent reading persistence unavailable until its contract
is accepted and implemented. A4 may verify the existing populated course flow
without waiting indefinitely for a durable-format decision. A3 hands back its
reviewable proposal before any dependent production work. Other tasks do not
create overlapping successors. Stop after the bounded outcome, a material
authority decision, or the same blocker across three consecutive links.

### Task registry

| Lane | Task ID | Current state |
| --- | --- | --- |
| A1 | `01a0941e-f8ff-73f0-9262-2a305baebc80` | Complete in bounded gate. Independent recovery review passed. Coordinates A4 dispatch. |
| A2 | `01a0941e-fcf7-7ee3-b6d4-9a8e8dd495d1` | Stable. Shelf and authorized daemon restart repairs passed focused gates. |
| A3 | `01a0941e-ffb1-7a80-9c88-fb2c36af56b8` | Proposal ready for user review, including D3 metadata correction. No persistence implementation. |
| A5 | `01a09420-397f-7a11-ad7e-ce8c4e4f49ee` | Stable and stopped. Synthetic export browser and runtime gates passed. |
| A4 | `01a0942a-63e8-7ac2-b50e-469806228dfa` | Bounded integration complete. Course-ops and recovery cleanup resolved. Final full run retains only known parity unavailable and expected dirty tree. |

All four use the saved local project and medium primary reasoning effort.
No model override was supplied, so they use the configured default model.
The earlier Sol/Terra recommendations remain recommendations, not a claim
about which model these task creations selected. Subagent choices follow the
invoked routing skill's caps.

The existing treatment task `01a09243-0daf-7bb0-a342-451da0323079`
reported its push complete. The local checkout was verified at `e7c242a`
before A5 dispatch. It explicitly excluded this report and STATE.

After dispatch, A1 owns updates to this task registry and the active STATE
pointer. A2, A3, and A5 send completion evidence to A1 as well as the original
coordinating task `01a09417-78af-7742-80a1-0c858add25cf`.
A1 must not report A4 as started until a successful create result exists.


## Lane reconciliation and A4 handoff, 2026-09-12

A1 inspected the actual A2 and A5 diffs, new exporter and regression assertions,
and read their owning result artifacts. No remaining concrete integration
blocker was found in this bounded review. This reuses the lanes' focused gate
evidence, not a second full test run. A1, A2 and A5 have stopped code edits.

| Lane | Reconciled evidence | Remaining boundary |
| --- | --- | --- |
| A1 | [Recovery result](source-to-reading/recovery-repair-2026-09-12.md). All four observations and C1 pass. Independent review and final journal/director suites pass. Source adapters, operations, agent-operation, package and evidence suites pass within the dated limits there. | Full integration pending. Legacy unrecorded sidecar recovery and unsupported lifecycle reversal are not claimed. |
| A2 | [Resume result](course-resume-repair-2026-09-12.md). Shelf and restart symptoms reproduced then repaired. Course-resume, IA 26, daemon 78, serve and quick preflight pass. | HTTP/helper evidence, no browser or human acceptance. Conservative mtime and missing-selection refusals remain explicit. |
| A5 | [Table export result](../../prototypes/learning-treatments/README.md#studio-table-export-2026-09-12). Downloaded bytes equal reviewed draft, canonical short answers stay pending, and browser export/interaction gates pass. | Synthetic fixed Monday comparison only. Editable wording still requires review against proposed rubric. Human and real-course acceptance deferred. |
| A3 | [Reading proposal](source-to-reading/durable-reading-contract-2026-09-12.md). D3 separates display placement from learning revisions so rename and Now/Library moves retain the same declaration. | Entire delta remains proposed. Initial independent review predates D3, whose evidence is a local disposable model check. Production reading persistence remains unavailable. |

A2's scope extension was explicitly authorized by the original coordinator:
only `_saved_quiz_session`, its `_ensure_quiz_session` call, and focused tests.
An intermediate scoped-serve regression caused A1's nested evidence HTTP 400.
A2 corrected the explicit-serve bypass. A1 then reran evidence and director
successfully. One parallel IA connection timeout passed in A2's isolated rerun.
These are resolved verification transients, not hidden remaining failures.

GOAL: A4 verifies one current supported populated synthetic study journey:
course and source or lesson, learner notes where supported, practice and
permitted feedback, leave/resume, and one full integrated preflight.

SCOPE: Use the same saved local checkout and preserve all uncommitted lane
changes. A4 owns its result artifact at
`research/source-to-reading/integrated-study-journey-2026-09-12.md` under this
planning tree and final reconciliation in this index and active STATE pointer.
It may repair only a concrete integration regression in the already authorized
A1/A2/A5 areas after their writers stop. Narrow tests accompany such a repair.

DO NOT TOUCH: scoring/disclosure policy, real courses or learner data, source
identity, rights authority, evidence writer authority, A3 durable formats,
external services, unrelated dirty work, Git history, stage/commit/push, branch
switches, cleanup or resets. Keep all synthetic artifacts in a private temporary
root. A4 cannot claim a reading declaration persists through unimplemented A3.

GATE: distinguish browser-driven from helper-only observations. Run one full
integrated `python3 scripts/preflight.py` and capture actual failures, including
known possible four-subject parity unavailable and expected dirty-tree clean.
Do not manufacture green by changing fixtures or configuration. Reuse stable
focused lane evidence and rerun only checks affected by concrete changes.
Record human-deferred, unsupported, unperformed and external gates explicitly.

RETURN: saved journey evidence, changed paths, exact gate results, unresolved
findings with owners, recovery and one next action. Reconcile this index without
rewriting historical observations. Stop after this bounded outcome. Do not
create further successors merely to add breadth. A3 implementation stays a
separate user-review decision.

NEXT ACTION: A4 executes its supported synthetic journey and one integrated
preflight. A4 task `01a0942a-63e8-7ac2-b50e-469806228dfa` was created on the
saved local checkout. It now owns this index and active STATE pointer.


## A4 final integration reconciliation, 2026-09-12

A4 completed the supported populated synthetic browser journey and one full
preflight. [The integration result](source-to-reading/integrated-study-journey-2026-09-12.md)
is the current evidence owner. The earlier dispatch packet is historical.
No production changes or successor task were made.

| Finding or lane | Current disposition | Owner and next action |
| --- | --- | --- |
| A1 / F1 | Recovery focused evidence retained. Full integration is not green: course-ops rerun has six assumptions counting prepared plus applied history as two acceptances. | A1, assigned by coordinator, should reconcile the assertion with one applied acceptance and linked intent while retaining exact undo. No repair is claimed. |
| A2 | Actual browser leave/restart/resume and canonical equality now supplement the prior HTTP/helper gate. Same session, selection, cursor and responses survived. | Existing conservative session-location and mtime limits remain with A2. Revisit on a concrete failure. |
| A5 | Export download equality and runtime evidence reused. Full preflight named no A5 failure. | A5 remains synthetic-only. Human and real-course acceptance remain with Weibao. |
| A3 | Entire proposal remains user-review-only, including D3. Browser guided reading reset to 1 of 2 after reload. No note editor or reported-read control in this lesson route. | Weibao reviews the proposed durable format separately. No implementation authority follows from A4. |
| F2 and deferred gates | Clean failed as expected. Ten fast gates and JS passed. All 123 Python files ran, with course-ops the only named failure. Four-subject review did not fail this run. CI-only and human gates remain unperformed. | Coordinator retains repository-wide status. User retains Git authorization, visual, touch, screen-reader, zoom, aesthetic and real-course acceptance. |

NEXT ACTION: coordinator assigns the bounded F1 course-ops reconciliation to
A1. Preserve the failed full-run record. Do not launch another broad audit or
implement A3 from this packet. The A4 chain stops here.


## A4 corrected-candidate reconciliation, 2026-09-12

This supersedes the prior next action, preserving both failed runs in
[the integrated report](source-to-reading/integrated-study-journey-2026-09-12.md#corrected-candidate-follow-up-2026-09-12).
A1's test-only correction was inspected against its exact handoff fingerprint.
The authorized follow-up full preflight ran all 123 Python files and passed
fast and JS gates. The completed browser journey was not replayed.

| Finding | Current disposition | Owner and next gate |
| --- | --- | --- |
| F1 course-ops | Resolved on corrected candidate. Exact prepared/applied linkage, malformed-history rejection and applied-entry undo checks preserved. | A1 patch complete. Course-ops not a failure in full preflight. |
| F3 file-fault cleanup | Open, reproduced in full run and isolated rerun. Partial locator write leaves `one.md.locator.json.tmp`. | A1 through coordinator. Repair atomic-write temporary cleanup and pass existing fault-injection plus affected recovery checks. |
| F4 four-subject parity | Open, `ok / unavailable` in corrected run. | Existing backend/parity owner through coordinator. Restore availability and rerun its gate. |
| F2 dirty tree | Expected workflow state, not a code failure. | User retains Git authorization. Preserve uncommitted lane work. |
| A2/A5/A3 and human gates | Prior browser/export evidence retained. A3/D3 remains proposed. Reading position resets, notes/read declaration unavailable on exercised route. | Human, real-course and durable-reading decisions remain with Weibao. |

NEXT ACTION: assign A1 the bounded F3 recovery repair. No new task or broad
browser replay was created. This A4 follow-up stops with the current full-run
failures visible, and does not claim repository-wide green.


## A4 final cleanup-candidate reconciliation, 2026-09-12

This is the current disposition, superseding the earlier next actions while
preserving the original failures. See the
[final integration evidence](source-to-reading/integrated-study-journey-2026-09-12.md#final-cleanup-candidate-validation-2026-09-12).
A4 reviewed A1's exact cleanup helper and fault-test patch after A1 stopped.
Candidate hashes match before and after the authorized final full preflight.

| Finding | Final disposition | Owner or revisit condition |
| --- | --- | --- |
| F1 course-ops | Resolved. Linked intent/applied acceptance and exact undo checks pass within final full run. | A1 patch retained. No further action in this scope. |
| F3 file-fault cleanup | Resolved. Owned temporary cleanup preserves durable targets and unrelated files. Unchanged tracer is no longer a failure. | A1 patch retained. Hard-kill, power-loss and cleanup-permission limits remain explicit. |
| F4 local-model parity | Known deferred `ok / unavailable` remains the only named Python failure. | Existing parity/backend owner. Further work needs separate scope. |
| F2 dirty tree | Expected condition, not code failure. Full preflight still exits 1. | User retains Git authorization. Preserve all lane edits. |
| Browser, A3 and human gates | Supported browser journey retained. A3/D3 remains proposed. Reading position and note-control limits unchanged. | Weibao owns durable-reading decisions and deferred human/real-course acceptance. |

All 123 Python files ran. Ten fast gates and JS passed. Diff-check passed.
No new recovery correctness failure remains in this run. Neither CI-only nor
human gates are certified. This is bounded integration completion, not a
repository-wide green result.

NEXT ACTION: coordinator returns this result with the remaining limits to
Weibao. A4 stops without successor, parity work, production co-edit or Git
mutation. Future work requires its own bounded authorization.
