# Phase 19B: Agent Operation Door - Context

**Gathered:** 2026-09-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Connect the existing agent-operation state machine to the canonical course
surface. A learner can start a real skill operation from the Agent tab, review
the exact proposal, accept or reject it, and undo an accepted change. An agent
client reaches the same operation through one token-gated route and one CLI
twin. This phase adds reach to existing authority. It does not add operation
types, scoring authority, key disclosure, an extension loader, or a second
proposal or journal authority.

</domain>

<decisions>
## Implementation Decisions

### Proposal lifecycle and review history

- **D-01:** Proposal content lives on the course side of the trust boundary
  between proposal and settlement. Accept and reject requests identify the
  stored proposal. They do not repost model-controlled draft bytes from the
  browser or client.
- **D-02:** Proposed, accepted, rejected, conflicted, and undone dispositions
  remain available as durable review records when useful for later audit,
  comparison, or recovery. Settlement does not automatically delete the
  proposal record.
- **D-03:** Any future compaction is an explicit maintenance operation. It may
  reduce redundant proposal payload only after preserving stable identity,
  disposition, provenance, accepted journal linkage, review facts, and the
  ability to explain what happened. Compaction is outside Phase 19B.

### Route, settlement, and undo

- **D-04:** Follow the established 19A per-operation shape. The Agent tab, API,
  and CLI are clients of one shared operation function and one published
  request contract.
- **D-05:** One accepted proposal produces exactly one applied
  `journal.commit_operation` entry. Repeated settlement is idempotent. A stale
  expected fingerprint becomes a visible conflict and never an overwrite.
- **D-06:** Undo is visible beside the settled proposal and uses the accepted
  journal entry or its linked operation identity. It must restore the exact
  prior valid bytes and update the durable proposal disposition without
  inventing a second recovery path.
- **D-07:** Reject records the review decision and changes no accepted course
  content. It must remain distinguishable from conflict, cancellation, and
  model or backend unavailability.

### Agent tab behavior

- **D-08:** The Agent tab's existing skill controls become real actions. A run
  shows durable status, proposal target, citations, validation state, and a
  reviewable diff before acceptance.
- **D-09:** The surface provides separate Accept and Reject controls. Accepted
  proposals expose Undo. Pending, needs-input, unavailable, conflicted,
  accepted, rejected, and undone states remain visibly distinct.
- **D-10:** The UI must keep a useful static representation, keyboard access,
  actionable unavailable and empty states, and runtime-owned disclosure.

### The agent's Discretion

The planner may choose internal names, helper boundaries, and the exact
course-local proposal path. The choice must preserve opaque proposal identity,
atomic writes, expected-base validation, reload and restart behavior, and
review history. The planner may reuse the existing director operation identity
or link it to the accepted journal entry. It may not create a seventh file
operation type or a parallel journal.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase and product contract

- `.planning/phases/19B-agent-operation-door/19B-SEED.md` - Phase goal,
  dependencies, authority boundary, and acceptance gate.
- `.planning/REACH-MILESTONE.md` - Reach ordering, 19B scope, 19D dependency,
  and visible learner-journey obligations.
- `.planning/SOURCE-TO-COURSE.md` - Local-first authority, operation,
  acceptance, recovery, and agent-client contract.
- `.planning/AGENT-WORKFLOW.md` - Required planning, authority, mutation,
  recovery, and handoff process.

### Existing agent-operation contract

- `.planning/phases/17A-visual-system-component-foundation/17A-07-PLAN.md` -
  Frozen state-machine, acceptance, conflict, and Agent-tab requirements.
- `.planning/phases/17A-visual-system-component-foundation/17A-07-SUMMARY.md` -
  Implemented state-machine evidence and remaining wiring gap.
- `.planning/UI-SPEC.md` - Diff, acceptance, undo, conflict, accessibility,
  and evidence-trace behavior.
- `.planning/REQUIREMENTS.md` - AGENT, RELIABILITY, APP, RIGHTS, and
  accessibility obligations that constrain the door.

### Adjacent extension work

- `.planning/EXTENSION-DELIVERY-2026-09-06.md` - EXT-04 remains owned by the
  existing UI and 19E seams. This phase must demonstrate composition without
  creating a general loader or second catalogue.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `surfaces/agent_operation.py`: Existing `idle`, `start`, and `accept` state
  machine. Model work already goes through `model_adapter.invoke`. Accepted
  content already goes through `journal.commit_operation`.
- `director.py` and `journal.py`: Existing operation records, expected-base
  settlement, operation-entry lookup, and byte-exact undo.
- `surfaces/course_ops.py`: Shared course-operation dispatch pattern used by
  routes and CLI twins.
- `surfaces/visual_fixture.py` and `surfaces/home.py`: Current Agent-tab
  presentation, skill controls, proposal states, and pending-proposal seam.

### Established Patterns

- `surfaces/daemon.py` keeps literal `API_ROUTES`, `ROUTE_CLI`, and
  `SURFACE_PARITY` mappings aligned. 19B adds one canonical operation family
  through these tables.
- Published request schemas validate at the token-gated daemon boundary before
  dispatch.
- Durable mutations use expected fingerprints, atomic writes, one applied
  journal entry, and recoverable before-images.
- Assessment scoring, keyed disclosure, and evidence authority remain in the
  runtime and are not part of this surface.

### Integration Points

- Replace descriptive Agent-tab controls with real start, accept, reject, and
  undo submissions.
- Persist proposal state between requests and expose it through the existing
  pending and operation-status surfaces.
- Add route, CLI, parity, schema, and focused roundtrip coverage without
  duplicating dispatch or proposal authority.
- Coordinate ownership before editing `surfaces/daemon.py`, `journal.py`, or
  `schemas/course_operation.schema.json`, which currently have unrelated
  uncommitted changes.

</code_context>

<specifics>
## Specific Ideas

Proposal records should remain useful for future review. Accepted, rejected,
and conflicted proposals therefore remain inspectable after settlement. The
learner should be able to return later and understand what was proposed, what
decision was made, what changed, and whether it was undone.

</specifics>

<deferred>
## Deferred Ideas

- Proposal compaction or retention-policy controls belong to a later
  maintenance phase after real proposal volume provides evidence.
- EXT-04 may generalize a composition recipe only after 19B and 19E prove the
  two existing seams.
- Installable external packages remain EXT-05 and are not part of this phase.

</deferred>

---

*Phase: 19B-agent-operation-door*
*Context gathered: 2026-09-06*
