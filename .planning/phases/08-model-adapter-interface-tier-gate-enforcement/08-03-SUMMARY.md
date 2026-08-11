---
phase: 08-model-adapter-interface-tier-gate-enforcement
plan: 03
subsystem: evidence
tags: [evidence, model_interaction, mark_proposal, schema, dedupe, pending, human-only-guard]

# Dependency graph
requires:
  - phase: 08-model-adapter-interface-tier-gate-enforcement
    provides: "gate reason codes and pass payloads (08-01); interaction ids and backend metadata (08-02)"
provides:
  - "Durable model_interaction evidence events: idempotent per interaction id, retry-linked via parent_interaction_id, descriptor-only on drop"
  - "Pending mark_proposal evidence events linked to the genuine short-answer response, structurally incapable of settling a mark"
  - "proposal_summary N-boolean read-time derivation and the mark_event(proposal_ref=...) human-accept seam"
  - "response.schema.json $defs + event_type enum extension for both new types and optional mark_event proposal_ref"
affects: [08-04, 08-05, 08-06, surfaces/evidence_cli, surfaces/session, surfaces/daemon, tier_gate, model_adapter]

# Actuals (#2632) — pairs with the plan's `estimate` (34000 tokens) to calibrate.
# estimateTokens scale: chars/4 over the realized diff of the three changed files.
actuals:
  tokens: 263
  tasks: 3
  commits: 7

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Event-type registration lands in KNOWN_EVENT_TYPES in the same commit as its builder"
    - "New event builders mirror term_lookup/key_review: envelope, ValueError on malformed args, sha256 dedupe over identifying fields, structurally no score key"
    - "Pending suggestions read through live_events() only; settled-mark readers (marks_by_event, review_state) filter on the mark type alone"

key-files:
  created:
    - tests/model_evidence_roundtrip.py
  modified:
    - evidence.py
    - schemas/response.schema.json

key-decisions:
  - "model_interaction_event and mark_proposal_event are registered in KNOWN_EVENT_TYPES and the schema enum in the same commit as each builder (D-23)"
  - "Dedupe is one-generation-per-interaction: sha256(session_id + interaction_id) for interactions, sha256(session_id + response_event_id + interaction_id) for proposals; retries get a NEW interaction_id with parent_interaction_id linkage (D-12)"
  - "mark_event(proposal_ref=None) folds the reference into the dedupe raw string (None encodes as empty) so accepting two different proposals for one response records two distinct human marks; the key is always present on the event dict (null when absent), matching the house 'every envelope key present' convention"
  - "session_events() stays the response-only reader by design (renders depend on it); retrieval of the new types is proven through events()/live_events()/model_interactions() per the task's own action text"
  - "The marker != 'human' guard in mark_event is byte-for-byte unchanged; a test asserts the exact guard block appears exactly once"

patterns-established:
  - "Pattern: a model suggestion is a first-class pending fact with no score/verdict fields, settled only by an explicit human mark_event(marker='human', proposal_ref=...) (D-13/D-14/D-20/D-25)"
  - "Pattern: N per-point statuses (pass|fail|uncertain) are the only stored credit; '4 of 5' style counts are derived at read time by proposal_summary, never stored as a fraction (D-24)"

requirements-completed: [TEACH-07, TEACH-08, TEACH-09, MODEL-05, MODEL-03]

coverage:
  - id: D1
    description: "model_interaction_event appends through the ONE writer, dedupes by interaction_id (recorded then already_recorded), reads back by session, and supports retry linkage via parent_interaction_id"
    requirement: TEACH-07
    verification:
      - kind: unit
        ref: "tests/model_evidence_roundtrip.py#test_model_interaction_append_retrieve_dedupe"
        status: pass
    human_judgment: false
  - id: D2
    description: "A dropped interaction stores descriptors only (fingerprints, byte count, gate reason, profile, timing); a forbidden-phrase scan finds no candidate text in the event, the raw log, or any reader"
    requirement: TEACH-07
    verification:
      - kind: unit
        ref: "tests/model_evidence_roundtrip.py#test_model_interaction_drop_descriptor_only"
        status: pass
    human_judgment: false
  - id: D3
    description: "mark_proposal_event appends as a pending per-point suggestion (point_index/status/rationale bounded) with no score key and no verdict field; a proposal-only log leaves review_state pending and marks_by_event empty"
    requirement: TEACH-09
    verification:
      - kind: unit
        ref: "tests/model_evidence_roundtrip.py#test_proposal_only_log_leaves_response_pending"
        status: pass
    human_judgment: false
  - id: D4
    description: "proposals_for(log, session_id, response_event_id) filters live mark_proposal events per response; an empty-points proposal is valid and reads back as pending/unknown, never a default pass"
    requirement: MODEL-05
    verification:
      - kind: unit
        ref: "tests/model_evidence_roundtrip.py#test_proposals_for_and_empty_points_pending"
        status: pass
    human_judgment: false
  - id: D5
    description: "proposal_summary derives points/pass_count/uncertain_count/pending from N per-point statuses at read time; no fractional score is stored or derived anywhere"
    requirement: TEACH-08
    verification:
      - kind: unit
        ref: "tests/model_evidence_roundtrip.py#test_proposal_summary_n_boolean_derivation"
        status: pass
    human_judgment: false
  - id: D6
    description: "mark_event(proposal_ref=...) records a human mark referencing the exact proposal, replays idempotently, records a distinct mark per different proposal_ref, and the unchanged marker != 'human' guard still raises for any other marker; an unaccepted proposal stays pending forever (terminal state)"
    requirement: MODEL-05
    verification:
      - kind: unit
        ref: "tests/model_evidence_roundtrip.py#test_mark_event_proposal_ref_human_accept"
        status: pass
      - kind: unit
        ref: "tests/model_evidence_roundtrip.py#test_human_only_guard_and_terminal_pending"
        status: pass
    human_judgment: false
  - id: D7
    description: "schemas/response.schema.json publishes model_interaction_event and mark_proposal_event $defs (additionalProperties false, own required lists), extends the event_type enum with both, and adds optional proposal_ref to the mark_event $def"
    verification:
      - kind: unit
        ref: "python itembank.py schema --all"
        status: pass
      - kind: unit
        ref: "python tests/protocol_roundtrip.py"
        status: pass
      - kind: unit
        ref: "tests/model_gate_roundtrip.py#test_schema_uses_supported_keywords_only"
        status: pass
    human_judgment: false
  - id: D8
    description: "The existing evidence spine is unchanged: the full evidence_roundtrip suite (mark flow, dedupe, retraction, renders) passes on a clean copy of the tree excluding the .phase10-wt worktree"
    verification:
      - kind: unit
        ref: "python tests/evidence_roundtrip.py (clean copy of tree excluding .phase10-wt)"
        status: pass
    human_judgment: false

# Metrics
duration: 22min
completed: 2026-08-11
status: complete
---

# Phase 08 Plan 03: Model Interaction & Rubric Proposal Evidence Summary

**Durable model_interaction and mark_proposal evidence events: idempotent per interaction id, descriptor-only drops, pending-only rubric suggestions settled exclusively by a human mark_event(proposal_ref=...), with N-boolean credit derived at read time.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-08-11T05:25:00Z
- **Completed:** 2026-08-11T05:47:41Z
- **Tasks:** 3
- **Files modified:** 3 (evidence.py, schemas/response.schema.json, tests/model_evidence_roundtrip.py)

## Accomplishments

- **model_interaction events (TEACH-07, D-12/D-15/D-16):** one generation per interaction is structural — `dedupe_key = sha256(session_id + interaction_id)`; an explicit retry is a new interaction id carrying `parent_interaction_id`; a drop/unavailable outcome stores fingerprints, byte count, gate reason, profile, and timing only, and a forbidden-phrase scan proves the dropped candidate's text never reaches the event, the log, or any reader.
- **mark_proposal events (TEACH-08/TEACH-09, MODEL-05, D-13/D-14/D-23):** a rubric-review outcome appends as a per-point `pass|fail|uncertain` pending suggestion linked to the genuine short-answer response event and its interaction id, with no `score` key and no `verdict` field; a proposal-only log provably leaves `review_state` pending and `marks_by_event` empty, and an unaccepted proposal stays pending forever (terminal state, D-22).
- **Human-accept seam (D-14/D-21/D-25):** `mark_event(..., proposal_ref=None)` records the human mark, folds the reference into the dedupe raw string (so two different proposals for one response are two distinct marks), and the `marker != "human"` ValueError guard is byte-for-byte unchanged and asserted to appear exactly once.
- **N-boolean derivation (D-24):** `proposal_summary` derives `{points, pass_count, uncertain_count, pending}` from the N statuses alone; no fractional score exists anywhere in events or schema.
- **Published contract:** `response.schema.json` gains both `$defs` with `additionalProperties: false` and their own required lists, the `event_type` enum is extended, and the `mark_event` $def documents the optional `proposal_ref` — all inside `schema_validate.SUPPORTED`.

## Task Commits

Each task was committed atomically, TDD test-first:

1. **Task 1: model interaction tracer** — `487889f` (test), `6c04d73` (feat)
2. **Task 2: mark_proposal pending-only** — `25229d4` (test), `4001bab` (feat)
3. **Task 3: N-boolean derivation + human-accept reference** — `bf5a4b5` (test), `f236189` (feat)

| Commit | Type | Description |
|---|---|---|
| `487889f` | test | model interaction tracer — envelope, idempotency + retry linkage, descriptor-only drop |
| `6c04d73` | feat | model_interaction_event builder, model_interactions reader, schema $def + enum |
| `25229d4` | test | mark_proposal pending-only — no settled mark from a model-only path |
| `4001bab` | feat | mark_proposal_event builder and proposals_for reader, schema $def + enum |
| `bf5a4b5` | test | N-boolean derivation and human-accept proposal_ref on mark_event |
| `f236189` | feat | proposal_summary N-boolean derivation and mark_event proposal_ref |

**Plan metadata:** the final docs commit (this SUMMARY + STATE.md + ROADMAP.md) is made via the gsd-tools commit verb at close-out.

## Files Created/Modified

- `evidence.py` — `KNOWN_EVENT_TYPES` gains `"model_interaction"` and `"mark_proposal"`; new builders `model_interaction_event(...)`, `mark_proposal_event(...)`; readers `model_interactions(log, session_id)`, `proposals_for(log, session_id, response_event_id=None)`, `proposal_summary(proposal)`; `mark_event(..., proposal_ref=None)` extended while the human-only guard stays byte-for-byte unchanged.
- `schemas/response.schema.json` — `model_interaction_event` and `mark_proposal_event` $defs, event_type enum extension, optional `proposal_ref` on the mark_event $def, description updates.
- `tests/model_evidence_roundtrip.py` — new stdlib-only suite covering TEACH-07/08/09, MODEL-05, MODEL-03 at the evidence layer.

## Decisions Made

- **One-generation-per-interaction is structural.** The interaction dedupe is over `(session_id, interaction_id)` only; a retry is a distinct interaction id with a parent link, so repeated cost stays visible without colliding with the original (D-12).
- **`mark_event.proposal_ref` is always present (None when absent).** The plan says "include it when provided"; the house convention is every envelope key present, so the key is emitted unconditionally with `null` and the schema marks it `["string","null"]` optional.
- **`session_events()` untouched.** It is the response-only reader renders depend on; the new types are retrieved through `events()`/`live_events()`/`model_interactions()` exactly as the task's action text describes ("session_events/events already include registered types").

## Deviations from Plan

### Auto-fixed Issues

**1. [Plan CLI deviation] `python schema_validate.py --all` is not this repo's CLI**
- **Found during:** all task verifies
- **Issue:** the plan's `<verify>`/`<verification>` invokes `python schema_validate.py --all`, which does not exist in this repository.
- **Fix:** substituted the real contract checks: `python itembank.py schema --all` (PROTO-05's published-contract delivery), `python tests/protocol_roundtrip.py` (full schema/runtime round trip), and ran `test_schema_uses_supported_keywords_only()` from `tests/model_gate_roundtrip.py` (proves the extended response schema stays inside `schema_validate.SUPPORTED`).
- **Files modified:** none
- **Verification:** all three substitute commands passed.
- **Committed in:** n/a (deviation recorded)

**2. [Known environment condition] `tests/evidence_roundtrip.py` / `tests/scoring_roundtrip.py` fail in-repo on structural one-writer/one-scorer scans**
- **Found during:** final verification
- **Issue:** the pre-existing `.phase10-wt` git worktree (branch phase10, uncommitted WIP) ships a second `evidence.py`/`runtime.py`, so the in-repo `append_event`-writer scan reports `[('evidence.py', 'append_event'), ('.phase10-wt/evidence.py', 'append_event')]`. Per the executing instructions this is a known environment condition, NOT to be fixed by touching the worktree.
- **Fix:** proved the core loop unchanged by running `python tests/evidence_roundtrip.py` and `python tests/scoring_roundtrip.py` in a clean copy of the tree excluding `.phase10-wt` (tar/cp to /tmp) — both passed. The worktree was not modified, deleted, or committed.
- **Files modified:** none
- **Verification:** `evidence contract: ok (...)` and `scoring contract: ok (6 items, one scorer)` in the clean copy.
- **Committed in:** n/a (deviation recorded)

**3. [Plan reading] "reads back through session_events" is satisfied via events()/live_events()/model_interactions()**
- **Found during:** Task 1
- **Issue:** the plan's acceptance line names `session_events` alongside `model_interactions`, but `session_events()` filters to `RESPONSE_EVENT_TYPE` only and the renders depend on that.
- **Fix:** followed the task's own action text ("Retrieval needs no reader changes beyond KNOWN_EVENT_TYPES because session_events/events already include registered types") and proved retrieval through `events()`, `live_events()`, and the new `model_interactions()`. `session_events()` was deliberately left untouched.
- **Files modified:** none
- **Verification:** `test_model_interaction_append_retrieve_dedupe` passes.
- **Committed in:** n/a (deviation recorded)

---

**Total deviations:** 3 (1 plan-CLI substitution, 1 known environment condition, 1 plan-reading clarification)
**Impact on plan:** None of the three changed code or scope; all were verification-routing or documentation adjustments. No scope creep.

## Issues Encountered

- `test_schema_uses_supported_keywords_only()` lives in `tests/model_gate_roundtrip.py` (plan 08-01's suite), not in this plan's files; it was invoked directly rather than by running the whole 08-01 suite.
- The executing shell silently expands `$defs` in command strings (even quoted heredocs), so schema-probe snippets used `chr(36) + 'defs'` to avoid a mangled key; no product code was affected.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The evidence layer for model interactions and rubric proposals is complete and green: `tests/model_evidence_roundtrip.py`, `tests/protocol_roundtrip.py`, and (clean-copy) `tests/evidence_roundtrip.py` all pass.
- Ready for 08-04/08-05/08-06, which can now build the adapter→evidence and proposal→CLI/daemon call paths on `model_interactions`, `proposals_for`, `proposal_summary`, and `mark_event(proposal_ref=...)` without touching event shapes.

---
*Phase: 08-model-adapter-interface-tier-gate-enforcement*
*Completed: 2026-08-11*

## Self-Check: PASSED

- [x] `tests/model_evidence_roundtrip.py` created — 9 behavior tests, all green.
- [x] 6 code commits present (3 test + 3 feat), plus the docs commit.
- [x] `python itembank.py schema --all` exit 0.
- [x] `python tests/protocol_roundtrip.py` green.
- [x] `test_schema_uses_supported_keywords_only()` green.
- [x] `tests/evidence_roundtrip.py` green in clean copy excluding `.phase10-wt`; in-repo one-writer scan failure recorded as the known environment deviation.
