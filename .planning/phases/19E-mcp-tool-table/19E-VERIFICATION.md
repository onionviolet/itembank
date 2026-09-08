# Phase 19E verification

**Status:** passed. The MCP tool table is generated from the daemon route and
parity inventories, both mounts use one dispatcher, and the tool-only Reach
course build finishes from an empty temporary root.

## Acceptance evidence

- Discovery exposes exactly one unique tool per current `API_ROUTES` row.
- Course requests project named nodes from `course_operation.schema.json`.
  Older API requests project named nodes from `api_request.schema.json`. Both
  are read through `resources.read_text`, and mutation changes discovery.
- Invalid input is refused before handler dispatch. StructuredContent and its
  JSON TextContent mirror are identical.
- Stdio supports discover-first and legacy initialization, ping, tools/list,
  tools/call, and cancellation. Every emitted line is JSON-RPC.
- Stdio, daemon HTTP, and a test byte transport use `mcp.frame`. Calls invoke
  the handler named by `API_ROUTES`; runtime and evidence retain score,
  selection, tier, and keyed-content authority.
- The tool-only transcript creates a course, mints a bounded source through
  `journal.commit_operation`, records and binds it, adds structure and an
  objective, binds a treatment and blueprint, runs the blueprint gate and
  audit, exports, and verifies a restorable package. The browser-facing outline
  read sees the same unit and objective.
- Before a response, no key, rationale, discriminator, or distractor analysis
  appears. An authority-shaped forced-answer call returns `isError: true`.

## Gates

- `python3 tests/mcp_roundtrip.py`: pass.
- `python3 tests/course_ops_roundtrip.py`: pass.
- `python3 tests/scoring_roundtrip.py`: pass, six items and one scorer.
- `python3 scripts/preflight.py --quick`: all 19E-relevant gates pass. The run
  exits nonzero only because concurrent 19B's new summary exceeds the summary
  cap and lacks its required justification heading.
- `python3 tests/daemon_roundtrip.py`: reaches only the inherited twelve-thread
  timeout recorded in `STATE.md`; route and parity assertions before it pass.

## Scope

WebMCP remains blocked on stable browser support. This phase proves the current
server-rendered browser flow shares course handlers and durable state with MCP.
It does not claim `navigator.modelContext` or complete V2-INT-03.
