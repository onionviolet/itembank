# Phase 19B: Agent Operation Door - Pattern Map

**Mapped:** 2026-09-06
**Files analyzed:** 9 likely new or modified files
**Analogs found:** 8 / 9

## File Classification

| New or modified file | Role | Data flow | Closest analog | Match quality |
|---|---|---|---|---|
| `surfaces/agent_operation.py` | service/state machine | request-response plus file I/O | existing `surfaces/agent_operation.py` | exact, extend in place |
| `surfaces/home.py` | component/view model | file I/O to server-rendered view | `pending_proposals()` and `render_agent()` | exact seam |
| `surfaces/visual_fixture.py` | component/view | request-response HTML form | `_agent_console()` and `_proposal()` | role-match |
| `surfaces/course_ops.py` | service/CLI operation | CRUD plus file I/O | `_op_settle_migration()` and `run()` | strong role and settlement match |
| `surfaces/daemon.py` | route/controller | request-response | `_course_operation()` and route tables | exact route family |
| `schemas/course_operation.schema.json` | config/schema | request-response validation | existing `$defs.reverse_operation` | exact published contract |
| `tests/agent_operation_roundtrip.py` | test | request-response plus file I/O | existing agent loop and undo checks | exact |
| `tests/course_ops_roundtrip.py` or new focused route test | test | request-response | course operation route/parity assertions | role-match |
| course-local proposal persistence module or helper | service/model | file I/O | no durable proposal analog; use journal and tolerant sidecar readers | no analog |

## Pattern Assignments

### `surfaces/agent_operation.py` (service, request-response and file I/O)

**Analog:** the existing module itself. Preserve its single state machine and add durable identity and review disposition around it. `start()` already makes the model boundary typed and creates the bounded proposal; `accept()` already owns the only course write.

**Imports and proposal shape** (lines 28-40, 180-246):

```python
import difflib
import os
import uuid
import identity
import journal
import model_adapter
```

```python
return {
    "state": "proposed", "skill": skill, "base": base,
    "interaction_id": iid, "target": spec["target"], "kind": spec["kind"],
    "draft": draft, "citations": citations,
    "expected_fingerprint": identity.object_fingerprint(raw, spec["kind"])
        if raw is not None else None,
    "diff": _bounded_diff(spec["target"], raw or b"", draft),
    "provider": result.get("provider"),
}
```

Persist this complete server-created record, including draft, citations, target, expected fingerprint, provider, operation or interaction identity, and disposition. Accept and reject should receive only the opaque proposal id and reload this record. Do not accept client-posted draft bytes.

**Settlement and idempotence** (lines 249-335):

```python
if not isinstance(state, dict) or state.get("state") != "proposed":
    return state
...
record = journal.commit_operation(
    base, object_id, kind, rel, operation,
    state["draft"].encode("utf-8"),
    expected_fingerprint=state.get("expected_fingerprint"),
    actor_kind="agent", actor_name="agent-area:%s" % skill,
    create_if_missing=True)
```

Keep the non-proposed guard for repeated accept. Map `journal.conflict` and `journal.stale_preflight` to a visible conflicted disposition without retrying or overwriting. Record the applied journal entry id by scanning the applied entry at the resulting revision, as the existing code does at lines 313-318. Reject must update proposal review state only and must not call `commit_operation`.

**Undo:** reuse `journal.undo(base, entry_id, actor_kind, actor_name)` and the stored applied entry. The existing roundtrip calls this directly at `tests/agent_operation_roundtrip.py:653-656`; do not create a second byte-restore implementation. Update the proposal record only after the journal result verifies restoration.

### `surfaces/course_ops.py` (service and CLI operation, CRUD/file I/O)

**Analog:** `_op_settle_migration()` at lines 1824-1867 and `run()` at lines 1910 onward.

**Operation identity and one writer** (lines 1832-1852):

```python
operation_id = body.get("operation_id") or director.new_operation_id()
decision = ("accepted" if body["operation"] == "accept_migration"
            else "rejected")
...
revision = fn(base, body["migration_id"], actor_kind, actor_name,
              body["rationale"], body.get("expected_fingerprint"),
              applied_agent=applied_agent)
```

Use the same operation-id convention, resolved course root, actor chosen by the surface, and expected-base value. For agent proposals, the acceptance path must call the shared agent operation function, not duplicate journal logic in the CLI adapter. Return stable ids, disposition, fingerprint, revision, settlement, and undo explanation in a JSON-safe payload like lines 1853-1867.

**Dispatch:** `OPERATIONS` is the operation allowlist at lines 1870-1895. Add the operation family there and keep the CLI parser and printer routed through the same `run()` dispatch. `_print_director()` at lines 2065-2109 is the closest human-readable status pattern. JSON callers must receive the full durable result, while the human CLI prints state, ids, conflict or rejection reason, and the exact next undo command.

### `surfaces/daemon.py` (controller/route, request-response)

**Analog:** the 19A route family and `_course_operation()` at lines 4883-4948.

**Route parity tables:** add one canonical route family to `API_ROUTES` at lines 319-369, its CLI name in `ROUTE_CLI` at lines 435-524, and its reserved MCP name in `SURFACE_PARITY` at lines 533-583. The route must also be included in `ROUTES` through `API_ROUTES`, not added as an untracked special case. Route ordering remains first-match-wins.

**Boundary and dispatch:** copy `_course_operation()`'s sequence:

```python
data, failed = api_read_json(handler)
if failed:
    return
result = course_ops.run(handler.root, operation, data,
                        actor_kind="human",
                        actor_name=data.get("actor") or "")
handler.send_json(result)
```

Preserve token and loopback write gates, reject authority-shaped fields before dispatch, validate against the published schema before reading proposal content, and map typed errors to safe 400/404 responses. The agent-client route should choose actor kind from the route, not from request JSON. Use a single shared handler for start, status, accept, reject, and undo variants where the operation contract permits it.

### `schemas/course_operation.schema.json` (published config, request-response)

**Analog:** `$defs.reverse_operation` at lines 344-354 and its top-level `$ref` registration at lines 7-40.

```json
"reverse_operation": {
  "type": "object",
  "additionalProperties": false,
  "required": ["operation", "course_id", "operation_id"],
  "properties": {
    "operation": {"type": "string", "const": "reverse_operation"},
    "course_id": {"$ref": "#/$defs/course_id"},
    "operation_id": {"$ref": "#/$defs/operation_id"},
    "actor": {"$ref": "#/$defs/actor"}
  }
}
```

Each new operation gets one closed `$defs` node with `additionalProperties: false`, required opaque ids, and no filesystem path, draft bytes, authority claim, or caller-supplied rights. Register every node in the top-level `oneOf`. Keep proposal identity opaque and resolve it below the course root. Follow the existing description language distinguishing request contracts from durable sidecars and journal records.

### `surfaces/home.py` (component/view model, file I/O)

**Analog:** `pending_proposals()` lines 57-68 and `render_agent()` lines 409-429.

The existing function is an intentional persistence seam:

```python
def pending_proposals(root):
    """Agent proposals waiting about objects in this root, as
    `{path, count}` rows.
    """
    return []
```

Replace the placeholder with a tolerant read of durable proposal records. Return only counts and paths for shelf badges, while the Agent view loads the selected opaque record. Follow `_load_session()` lines 71-79: malformed, half-written, or future-versioned files must not take down the home surface. Keep `AGENT_AREA_HREF` as the single URL seam and preserve the fallback HTML in `render_agent()`.

### `surfaces/visual_fixture.py` (component/view, request-response HTML)

**Analog:** `_agent_console()` lines 716-872 and `_proposal()` lines 977-991.

The current fixture already renders live skills, unavailable reasons, running status, capped diff lines, citations, and placeholder Accept/Reject controls. Preserve semantic HTML and `presentation.state_panel()` for empty and degraded states. Replace buttons with normal POST forms or the existing route-enhancement pattern, retaining the static server-rendered state. Use `agent_operation.STATE_COPY` and `NEXT_ACTIONS` as the single copy source at lines 778-792. Render distinct proposed, accepted, rejected, conflicted, and undone states with text and structure, not color alone. Undo belongs beside the accepted journal-linked row and must be hidden when journal metadata says it is not undoable.

### `tests/agent_operation_roundtrip.py` (test, file I/O and settlement)

**Analog:** existing tests at lines 615-707 and the assertions listed in `main()` lines 710-730.

Extend the same temporary-course and stubbed-model discipline. Assert proposal survives a fresh load, accept and reject are idempotent, reject leaves bytes unchanged, stale expected fingerprints produce a named conflict, exactly one applied journal entry exists, and undo restores byte-identical prior content while leaving both records inspectable. Keep network use to loopback stubs and never assert on optimistic UI state.

### `tests/course_ops_roundtrip.py` and route/parity tests (test, request-response)

**Analog:** existing course operation and daemon parity assertions, especially the invariants documented in `surfaces/daemon.py:430-434` and `_course_operation()` at `4883-4948`.

Add schema validation cases for every new request node, route-to-CLI-to-parity equality, token-gated dispatch, forbidden client fields, JSON and human CLI parity, duplicate settlement, conflict refusal, and reverse/undo response shape. Reuse the existing temporary roots and `schema_validate` helpers rather than constructing a second request validator.

### Course-local proposal persistence helper or module (service/model, file I/O)

**No close analog found.** The current `agent_operation.start()` keeps proposal bytes only in an in-memory dict, and `home.pending_proposals()` explicitly returns no rows. Implement the smallest course-local record store compatible with existing tolerant JSON readers and atomic mutation rules. Records must include opaque proposal id, operation and interaction ids, target and kind, expected fingerprint, draft, citations, provider or backend, validation result, disposition, reviewer and decision time, applied journal id, prior revision, and undo metadata. Writes must use expected fingerprint and atomic replacement. Read failure should produce an actionable unavailable or empty state, never fabricate a proposal.

## Shared Patterns

### One authority per boundary

Model work stays behind `model_adapter.invoke` (`surfaces/agent_operation.py:199-204`). Accepted content stays behind `journal.commit_operation` (`surfaces/agent_operation.py:293-299`). Undo stays behind `journal.undo` (`tests/agent_operation_roundtrip.py:653-656`). Routes and CLI call the same operation function.

### Compare and swap, conflict not overwrite

Carry `expected_fingerprint` from proposal creation through settlement. A stale or conflicting journal error becomes a durable `conflicted` review record with no content write. Never silently rebase or retry.

### Durable records and tolerant reads

Use the tolerant file-reading style in `surfaces/home.py:71-79`, retain review history after settlement, and make repeated accept, reject, and undo return the already-settled state without a second mutation.

### Static, accessible UI

Use server-rendered forms, semantic headings and status regions, `presentation.state_panel()`, written state labels, and the existing `--space-*` and theme primitives from `19B-UI-SPEC.md`. JavaScript may enhance a confirmed response but cannot own state or post draft bytes.

## Dirty-file Ownership Hazards

The working tree already has unrelated uncommitted changes in `surfaces/daemon.py`, `surfaces/course_ops.py`, `journal.py`, `schemas/course_operation.schema.json`, `director.py`, multiple tests, and planning documents. Before editing any of these, establish ownership with the orchestrator and inspect the current diff. Stage only Phase 19B-owned paths. Do not overwrite or reset existing changes. `journal.py` and `schemas/course_operation.schema.json` are explicitly called out by the phase context as unrelated dirty files, so prefer narrow patches and preserve all existing hunks.

## No Analog Found

| File or concern | Reason | Planner guidance |
|---|---|---|
| Durable course-local proposal persistence | No existing proposal record survives a request. | Reuse journal identity, atomic write, fingerprint, and tolerant-read conventions. Do not create a second journal or operation authority. |

## Metadata

**Analog search scope:** `surfaces/`, `schemas/`, `tests/`, `director.py`, `journal.py`, and phase planning documents.
**Files scanned:** 9 primary analogs plus route, schema, journal, and test references.
**Pattern extraction date:** 2026-09-06
