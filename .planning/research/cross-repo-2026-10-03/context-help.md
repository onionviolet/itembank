# L1 contextual source help, October 3

Status: feasible source slice implemented and scoped gates passed. L1 source
ownership is released to coordinator chat `01a102a5-223f-7293-ae74-1922372ac0c8`.
Production provider invocation remains unavailable while direct decision Q4 on
the additive source-question operation is pending. A synthetic operation
contract in tests is not production registration or acceptance.

## Scope and authority

The dispatch in `../cross-repo-implementation-2026-10-03.md` owns this lane.
Read AGENTS, AGENT-WORKFLOW sections 1 and 5 through 9, STATE's current October 3
entries, and SOURCE-TO-COURSE sections AI's reasonable role and Durable reading
activities. Source and private-note admission reuse course, reading,
source_adapters, journal, notes and the one bank parser. Scoring, keyed
disclosure, acceptance and response evidence remain with their existing owners.

Source changes: `surfaces/research_context.py`, `surfaces/reading_desk.py`,
new `surfaces/context_help.py`, new `tests/context_help_roundtrip.py`, and new
`tests/context_help_native_roundtrip.py`. This report is the only L1 planning
write. Existing dirty reading workspace controls and other lanes' edits were
preserved. Coordinator owns all daemon, adapter, generic schema and shared
planning changes. No Git mutation, installation, real learner content, active
sitting, paid provider or learner egress occurred.

## Observable behavior

F1. Reader selection uses actual DOM range offsets converted from UTF-16 to
code points. The same phrase appearing twice produces distinct occurrences.
The current accepted reading occurrence/revision and exact quote are checked
before preview. The source picker uses location labels and excerpt text instead
of typed opaque locator IDs. Source and locator sidecar must retain accepted
source-operation provenance. A changed valid-looking sidecar cannot redirect
the second duplicate to the first.

F2. Preview shows the exact question, source words, admitted source revision,
selected private-note wording, excluded-note count and configured profile,
model and direct destination. Notes start unchecked and remain labeled learner
wording. Source requests require read, quote and transform rights. Hosted or
non-loopback direct destinations additionally require remote_process. Explicit
whole-preview consent covers only the one shown request. No alternate provider,
background scope expansion or automatic retry occurs.

F3. Help uses process-local preview/request capabilities with a 30-minute
expiry and a 64-handle bound. A used preview is idempotent for the same request.
The context and destination are re-admitted before invocation, after provider
completion and on answered-status reads. Cancellation discards late output;
restart loses ownership and refuses replay. The reading tab preserves its
question, selection and request handle as presentation state. Reload retrieves
the same owned request only. Return restores source focus and the exact
duplicate selection; script-free picker return reopens the exact L4 occurrence.

F4. Only pure source questions are supported. Assessment linkage or unknown
authority fields are refused, known assessment registrations are blocked before
opening their bytes, and banks mislabeled as sources are rejected by the one
existing bank parser during admission. There is no runtime-tutoring parity claim.
Formal withholding, hint tiers and diagnostic-question ownership remain in the
existing runtime route. Included notes must have source targets. The response
is advisory, with one or more exact source quotes from the included payload;
outside citation IDs, fabricated quoted substrings, note-only support and extra
candidate fields are refused. Citation membership does not prove factual or
pedagogical quality.

## Frozen interfaces and coordinator requests

I1. `context_help.apply(base, action, body, settings_data)` supports preview,
start, status and cancel. The coordinator strips and resolves course_id at the
route boundary and supplies the current settings. Preview accepts only
expected_fingerprint, question, source, reading, selection, note_ids and
notes_fingerprint. Exactly one source or reading is required. Source uses the
existing source_id/locator_id/fingerprint reference; reading uses occurrence_id
and revision_id. Optional selection is start/end/quote in code points.

I2. `context_help.form_apply(base, fields, settings_data)` and
`context_help.panel(base, result=None, retained=None, settings_data=None,
course_id=None)` implement script-free source choice, exact preview, explicit
request, refresh and cancellation. `context_help.CSS` is scoped presentation.
Reader controls are emitted by reader_panel and READER_SCRIPT. Coordinator
wired POST `/api/course/context-help-{preview,start,status,cancel}` and
GET/POST `/course/<id>/help`. Coordinator also wired singleton source_id,
locator_id and fingerprint on research GET for exact script-free return.
No daemon lease was granted or used by L1.

I3. The candidate contract is owned by
`source-question-contract.md`. No current adapter operation is eligible.
L1 proposes operation source_question with payload.context_request and uses
request_from_operation/invoke only when adapter schema and payload keys both
register that operation. Question is bounded to 2000 characters, request
payload to 24 KiB UTF-8, answer to 8 KiB, uncertainty to 2 KiB and serialized
candidate to 16 KiB. Citations number 1 through 16; each quote is at most 2000
characters and must match included bytes. Q4 belongs to the user and coordinator;
L1 does not register or activate this contract.

## Verification and evidence

Base HEAD: `28bf561865cf0696a8beb42dd6f356b8bf6ec648`. Dirty input pins and
initial authority are in `.reasonix/cross-repo-implementation-20261003/`.
Initial L1 source SHA-256:

| Path | Initial hash |
| --- | --- |
| surfaces/research_context.py | 84ba67510fa448131b83449fcabcb3e31004eed79eb745b264b9dc23bb21baf4 |
| surfaces/reading_desk.py | ee35c19642c88d691ce3bf9d1051d704d2dab1e02f2a23e32ab612ab8b1b88ac |

Final released source SHA-256:

| Path | Released hash |
| --- | --- |
| surfaces/research_context.py | fb266137a366690163060d7437597be48d690fa5205a0a28c41aa0407028e1ca |
| surfaces/reading_desk.py | 7283ecd06813e0711e2e4a67a97608a6c27192d267943eaac5413e1baf60e7f6 |
| surfaces/context_help.py | 711ba912a6c0139c6ce48cd08662d2bffddb974c649b30689b7c87ca15f7c675 |
| tests/context_help_roundtrip.py | 1b595decc88ae43f4cc0e384aff7e2b53d673962f269a1c08ef321bdf6fa43f4 |
| tests/context_help_native_roundtrip.py | 76c15caf0a9aac6b160d02d88077ef5ffad1928a922151ef0adb4bc613f5ea9b |

At the native gate, adapter and generic schema hashes were unchanged from
dispatch: model_adapter.py `405dda9daa4aad195b7f85b84b18ab790d50f66066c1f6dc73d5220c4401f137`
and model_adapter.schema.json `263b98ab7df365997e5b0b64cb25a2c9eb82cbccdb30b9bdb41bff6397fc6760`.
At the final native gate, the coordinator's daemon was
`6c65442ce8bfbd405f78eaf3ae59dc94248ab8562ead3a6f2a7debecdc942476`
including the exact picker-return follow-up. Coordinator must pin its final
daemon again if later integration changes its bytes.

Executed scoped gates:

| Exact command | Result and scope |
| --- | --- |
| python3 tests/context_help_roundtrip.py | 8 cases pass: duplicate identity, note exclusion/selection, rights, assessment withholding, malformed handles, unsupported-contract no-call, citations, stale before/during/after, late cancellation and unowned restart |
| ITEMBANK_VISUAL_QA_CHANNEL=chrome python3 tests/context_help_native_roundtrip.py --browser .reasonix/cross-repo-implementation-20261003/context-help-browser | Native HTTP and installed Chrome pass at 1280/390/320: actual reader ranges, Unicode offsets, exact request, excluded note, explicit consent, cited synthetic CLI reply, cancel, reload, keyboard return and script-free exact picker return; fresh daemon refuses prior handles |
| python3 tests/reading_desk_roundtrip.py | 7 existing reading/note cases pass |
| python3 tests/selected_context_search_roundtrip.py | 6 selected literal search cases pass |
| python3 tests/a5_research_context_roundtrip.py | Existing exact context, note transfer/undo and assessment-refusal scenario passes |
| node --test tests/js/reading_workspace_modes.test.mjs | 4 existing mode/storage/revision cases pass |
| python3 tests/ui_overhaul_workspace_roundtrip.py | 3 existing workspace structure cases pass |
| python3 -m py_compile surfaces/context_help.py surfaces/research_context.py surfaces/reading_desk.py | Pass |
| git diff --check for the five L1 source/test paths | Pass |

Final helper, reading, search, research and workspace logs are the
context-help-*-final.log files under the local evidence directory. Browser
screenshots and observations.json are in context-help-browser; the 320-pixel
image was inspected. Synthetic course/private-note/evidence tree hashes are
identical before and after help, including request success and cancellation.
The native success test explicitly patches the candidate schema only inside its
test process and runs a fictional CLI over synthetic input. It is not evidence
that production source_question is enabled.

Two initial failures remain failed observations. The first helper run discovered
16 cases because it imported another unittest class, and one fixture assumed a
transfer summary was a full note document. The repaired test rereads its durable
note owner and runs eight owned cases. The first existing JS mode run hit an
older render fixture without canonical note identity/status. The renderer now
omits such records from selectable help notes; its original reader display is
preserved. Both repaired focused gates pass. Existing ResourceWarnings in
reading/workspace tests do not alter their pass results.

## Recovery and limits

Undo source changes by reversing only the L1 bounded research/reader hunks and
removing the new context_help module/tests. Preserve the pre-existing reading
mode, source-return and other dirty edits. Do not reset either whole shared file
to HEAD or an old snapshot. Runtime help has no accepted write to undo; cancel
discards late output and reopening after restart requires a fresh preview.

Only the coordinator runs broad preflight. Source remains uncommitted and
uninstalled. Human learning quality, screen-reader/touch acceptance, downstream
provider behavior and live configured-provider invocation were not certified.
Model adapter, course, reading, journal and source-adapter modules were sampled
by relevant symbols, not audited whole. This lane makes no exhaustive module,
whole product, production-help or tutoring-parity claim.

Next owner action: integrate the released interfaces and scoped receipts, run
the sole combined source-only gate, and keep production registration held until
Q4 is answered. No additional chat or delegation is needed for this lane.
