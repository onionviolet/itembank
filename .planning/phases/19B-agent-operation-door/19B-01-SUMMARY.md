# Phase 19B Plan 01: Agent Operation Door Summary

## Why this summary exists

The plan was executed without a commit, so this bounded record preserves the
verification result and the remaining human-only acceptance legs.

**Course-local proposals now survive reload, settle once through the journal, undo byte-exactly, and are reachable from one API, CLI, and server-rendered Agent flow.**

## Accomplishments

- Added versioned atomic proposal records with proposed, accepted, rejected, conflicted, undone, and typed unavailable readings.
- Added the closed `agent_operation` request family, `/api/course/agent-operation`, `itembank course agent-operation`, and its reserved MCP parity name.
- Added Agent to the live course navigation with static review, citation, validation, diff, evidence, decision, history, and undo controls.
- Added regression proof for opaque-id reload, one-write acceptance, no-write rejection, and byte-identical undo.

## Verification

Focused agent, course-operation, home, IA-route, and visual-system suites pass. Quick preflight passes. `tests/daemon_roundtrip.py` reaches only its previously recorded concurrent-request timeout and passed all preceding assertions on both runs.

Human screen-reader and visual acceptance remains owed. It was not self-certified.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Security] Refused configured targets that escape the course root**

- The existing target lookup accepted absolute and parent-relative configured paths before proposal creation.
- The target is now refused before any file read.

**2. [Rule 3 - Compatibility] Updated the local model stub to the active OpenAI-compatible response envelope**

- Concurrent Phase 19C work made the former bare-candidate test response invalid.
- The fixture now supplies the same candidate inside the supported response envelope.

## Known Stubs

None.

## Threat Flags

No unplanned trust boundary was added. The new HTTP route, proposal sidecar, and journal crossing are the three surfaces declared in the plan threat model.

## Self-Check: PASSED

All listed implementation files exist. No commit was made, as directed by the coordinating agent.
