# A4 staged answer/reason successor packet

Status: implementation proposal, not an accepted format or implemented feature.
Owner route: BACKLOG.md F3/F6 and WORKFLOW-AUDIT-2026-09-29.md A4. This packet
specifies the next bounded slice without creating another progress queue.

GOAL: One synthetic shared-stimulus activity with two existing MC children,
answer then reason. Commit the answer before opening the reason. Resume the
exact committed stage after reload, a desk detour and daemon restart, with
independent runtime disclosure and distinct child evidence.

## Existing facilities and the actual gap

`model.parse_activities` already parses ACTIVITY-01's eleven-column registry.
Its docstring explicitly makes it metadata that grants no scoring path.
`feedback=staged` therefore does not implement a staged response protocol.
`runtime.start_lesson_run`, `lesson_run_advance` and `lesson_run_record` persist
guided reading position and checkpoint bookkeeping. Their position is
presentation state, not assessment progress, and advancing accepts any known
step. `schemas/lesson_run.schema.json` is version 1, a distinct session kind;
it has no parent activity, child commitment or immutable case revision.
`checkpoint_feedback` refuses exam/diagnostic disclosure. Keep that boundary;
guided lesson steps do not satisfy A4's commitment or assessment contract.

Reuse `score_response`, `public_item`, ordinary sitting submission/deduplication,
`assessment_feedback_released`, the evidence writer and the current native
MC controls. The missing primitive is a reviewed grouping declaration plus a
runtime transition that binds child commitment to the existing sitting cursor.
Do not introduce a second lesson-run cursor that competes with the sitting.

## Proposed smallest contract, requiring review before implementation

A versioned optional case declaration names stable activity ID, accepted bank
fingerprint, stimulus, two stable child IDs and fixed order. Both children
retain their existing item identity, objective, response form and key. Reject
missing/duplicate child IDs, overlapping case membership, malformed order and
unsupported child forms. Cases not selected as complete units must be refused
or excluded explicitly; ordinary item sampling must not silently split them.

The existing sitting document is canonical for current child and commitment
state. Bind it to the declaration revision/fingerprint. A genuine accepted
answer submission opens the reason regardless of correctness; invalid entry,
replayed POST, client-supplied stage and Back never advance it. The reason
stem may refer to the learner's committed answer, but may not contain the
answer key or grading result. No correctness-conditioned branch in this slice.
After reason commitment, the ordinary cursor advances to the next activity.

Record each child response through the one evidence writer, linked to activity
ID, case revision, child ID and stage. Add no composite score or mastery claim.
If reporting groups them visually, retain each child's verdict, objective and
denominator. In exam/diagnostic mode no child key, rationale, outcome or
answer-specific diagnostic is released before existing sitting release policy.
In practice, first-child feedback waits until reason commitment so it cannot
answer the unopened reason. The exact post-reason release policy needs review.

Schema gates: decide additive session fields versus a version increment after
inspecting all version readers; update `schemas/session.schema.json`, item/public
projection schemas and evidence schema only where the reviewed contract needs
them. Legacy sitting and lesson-run documents gain no inferred case/stage or
transferred evidence. Changed/missing case revisions expose stale/conflict
recovery, preserve prior answers and do not guess a replacement stage.

## Execution boundaries and acceptance

Before editing, settle authored syntax, complete-unit selection policy,
practice release policy and session/evidence version compatibility. These are
readiness gaps, not permission granted by this packet. Use existing reviewed
proposal and journal paths for authored revisions, with expected fingerprint,
validation, atomic acceptance and undo. Session/evidence writes need a tested
crash/replay reconciliation path through their current owners, not a new store.
`runtime.write_session` uses a nonce temporary file and atomic replace, but its
docstring explicitly leaves concurrent last-writer-wins to callers. Atomic
bytes alone do not prove serialized answer/stage commitment; include concurrent
duplicate/conflicting submission tests in this gate.

Acceptance fixture: author and lint one two-child synthetic case, preview it,
commit answer, reload at reason, restart daemon at reason, submit reason and
assert exactly two linked response events. Invalid entry, forged stage,
duplicate submission, changed bank and unavailable revision preserve the last
valid state. Inspect quiz, Home, Activity, report and agent JSON for unopened
key/rationale leakage. Preserve ordinary independent MC and lesson-run tests.
Existing regression anchors: `tests/activity_declaration_check.py`,
`tests/lesson_run_roundtrip.py`, `tests/paced_lesson_tracer.py`,
`tests/agent_roundtrip.py` and the relevant served/session schema checks.

Use labelled native controls and a coherent static Markdown case containing
both prompts in order. Show the committed answer when answering the reason.
Keyboard, touch, screen-reader and narrow-width human acceptance stays separate
from automated checks. Verify the same journey in a fresh package and compare
source/package fingerprints; source checks do not certify installed acceptance.

EXCLUDES: branch graphs, video/playback checkpoints, span annotation, first-error
selection, prose auto-grading, new partial-credit aggregation, whole-course
rewrites, donor code, installation and publication. F3 remains prototype; F6
retains registered F1/F3 reuse plus prototype branching/media with their own
state, transcript, branch/endings and recovery gates.

RETURN: reviewed contract decisions, changed paths, exact fingerprinted evidence,
remaining schema/recovery gaps and unrun package/human checks. Update the existing
backlog/audit/STATE owners. This packet grants no commit or push authority.
