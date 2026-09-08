---
phase: 19E-mcp-tool-table
plan: 01
type: execute
wave: 1
depends_on: ["19A-09"]
files_modified:
  - surfaces/mcp.py
  - surfaces/daemon.py
  - surfaces/cli.py
  - itembank.py
  - tests/mcp_roundtrip.py
  - tests/daemon_roundtrip.py
autonomous: true
requirements: [V2-INT-02, V2-INT-03]
must_haves:
  truths:
    - "An MCP client discovers exactly one tool per API_ROUTES row, with the reserved SURFACE_PARITY name and the operation's published on-disk input and output contracts."
    - "An agent builds a course from an empty data root through tools/list and tools/call alone, including create, source registration, binding, structure, treatments, blueprint gate, audit, and package verification."
    - "MCP, the daemon HTTP mount, the browser UI flow, and CLI twins reach the same Python handlers, validation, tier gates, evidence store, and runtime scorer."
    - "Locked assessment content remains absent before the evidence-backed unlock, and denied tool calls return isError true with the actual unlock condition."
    - "The stdio process emits only JSON-RPC on stdout and supports discover-first clients plus the legacy initialize path."
  artifacts:
    - path: "surfaces/mcp.py"
      provides: "Generated tool table, shared dispatcher and JSON-RPC stdio framing"
    - path: "surfaces/daemon.py"
      provides: "HTTP registration of the same MCP dispatcher and the sole route/CLI/tool parity inventory"
    - path: "tests/mcp_roundtrip.py"
      provides: "Schema mutation, parity, transport, disclosure, validation and course-building acceptance proofs"
  key_links:
    - from: "surfaces/mcp.py"
      to: "surfaces/daemon.py:API_ROUTES and SURFACE_PARITY"
      via: "tool generation and dispatch lookup"
      pattern: "API_ROUTES|SURFACE_PARITY"
    - from: "surfaces/mcp.py"
      to: "resources.read_text and schema_validate.validate"
      via: "on-disk schema projection and pre-dispatch validation"
      pattern: "resources\.read_text|schema_validate\.validate"
    - from: "surfaces/mcp.py"
      to: "the existing daemon handler named by API_ROUTES"
      via: "one shared framing function used by stdio and HTTP"
      pattern: "handler|dispatch"
---

<objective>
Ship the Phase 999.3 MCP tool table as a generated third surface over the existing JSON API, then prove a tool-only agent can build a course without creating another parser, scorer, schema inventory, or authority path.

Purpose: Give agent clients the same safe course-building and assessment operations already available to the browser and CLI.
Output: One stdlib MCP implementation, stdio and daemon mounts, and complete parity and vertical-flow tests.
</objective>

<execution_context>
@.codex/get-shit-done/workflows/execute-plan.md
@.codex/get-shit-done/templates/summary.md
</execution_context>

<context>
@AGENTS.md
@.planning/phases/19E-mcp-tool-table/19E-SEED.md
@.planning/REACH-MILESTONE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/phases/19A-course-operating-surface/19A-CONTEXT.md
@surfaces/daemon.py
@surfaces/course_ops.py
@surfaces/protocol_cli.py
@resources.py
@schema_validate.py
@scripts/ocr_mcp.py

<interfaces>
- `surfaces.daemon.API_ROUTES`: ordered `(method, path, handler_name)` rows and the only MCP membership source.
- `surfaces.daemon.SURFACE_PARITY`: `(route, cli_command, reserved_mcp_tool_name)` rows and the only route/CLI/tool parity map.
- `schemas/course_operation.schema.json#/$defs/<operation>`: the course operation request signatures already loaded and validated by `surfaces.course_ops`.
- `resources.read_text(relpath)`: the packaging-safe path used to read published schemas off disk or from the archive.
- `schema_validate.validate(instance, schema)`: the existing stdlib request validator.
- `runtime.public_item(...)` and the existing daemon handlers remain the disclosure and scoring authorities. MCP must dispatch to them, never reproduce their decisions.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Specify the generated table, transports, and authority gates</name>
  <files>tests/mcp_roundtrip.py, tests/daemon_roundtrip.py</files>
  <behavior>
    - Every current API_ROUTES row produces exactly one uniquely named tool from its SURFACE_PARITY row; removing either side fails parity.
    - Each inputSchema and outputSchema is loaded through resources from the published schema source appropriate to the operation; changing a temporary copied schema changes tools/list without a Python edit.
    - Invalid arguments fail before handler dispatch; pre-response payloads contain no key, rationale, distractor analysis, or higher-tier text; forced-answer prompts cannot alter the evidence-backed refusal.
    - stdio supports server/discover, tools/list, tools/call, notifications/cancelled, initialize, notifications/initialized, and ping; every stdout line is JSON-RPC.
    - stdio, HTTP, and a stub third byte transport produce the same framed result from one dispatcher.
  </behavior>
  <action>Create focused failing tests for Phase 999.3 criteria 1 through 10. Assert that API_ROUTES plus SURFACE_PARITY generate the table, with no MCP-only capability or second parity map. Cover on-disk schema mutation, declared outputSchema plus identical structuredContent/TextContent JSON, validation via schema_validate, legacy and discover-first protocol paths, cancellation tolerance, stderr-only diagnostics, CLI reachability without MCP, and identical refusal/disclosure behavior through the existing handler. Preserve V2-INT-03 as blocked browser-standard work: do not implement navigator.modelContext; prove this phase's HTTP mount and current server-rendered browser flow still share the same handlers and remain usable without MCP.</action>
  <verify><automated>python tests/mcp_roundtrip.py &amp;&amp; python tests/daemon_roundtrip.py</automated></verify>
  <done>The tests fail only because the MCP projection, dispatcher, and mounts do not yet exist, and encode every 999.3 success criterion without weakening its gates.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Implement one generated MCP table with stdio and HTTP mounts</name>
  <files>surfaces/mcp.py, surfaces/daemon.py, surfaces/cli.py, itembank.py, tests/mcp_roundtrip.py, tests/daemon_roundtrip.py</files>
  <behavior>
    - Tool metadata is recomputed from API_ROUTES, SURFACE_PARITY, and packaged schema bytes rather than copied constants.
    - tools/call validates, invokes the named existing handler through one adapter, and frames success or business refusal consistently on every mount.
    - Assessment calls never score, unlock, select, or disclose inside MCP code.
  </behavior>
  <action>Implement `surfaces/mcp.py` with stdlib JSON-RPC framing following `scripts/ocr_mcp.py`, extended for server/discover and cancellation. Generate tools solely by joining API_ROUTES to SURFACE_PARITY. Resolve each tool's request and response contract from the published schemas through resources, including the matching `$defs` node for course operations, and validate arguments with schema_validate before invoking the same daemon handler. Return `structuredContent` and a TextContent JSON mirror for every result; return `isError: true` with the handler's refusal text for validation, locked-tier, and business errors. Register a CLI stdio entry and an HTTP mount on the daemon using the same framing/dispatch function. Keep all existing CLI commands and server-rendered UI routes working without importing or starting MCP. Do not add a dependency, duplicate API_ROUTES/SURFACE_PARITY, parse banks, inspect answer keys, call score_response, infer tier state, or introduce any scoring or mutation authority.</action>
  <verify><automated>python tests/mcp_roundtrip.py &amp;&amp; python tests/daemon_roundtrip.py &amp;&amp; python tests/scoring_roundtrip.py</automated></verify>
  <done>Both mounts expose the generated table, all protocol and security tests pass, CLI and browser flows remain independent MCP clients of the same runtime, and runtime.py remains the sole scorer.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Prove the course-building tool-table flow end to end</name>
  <files>tests/mcp_roundtrip.py</files>
  <behavior>
    - From an empty temporary data root, a protocol client uses only tools/list and tools/call to create a course and reach a valid audited, package-verifiable course state.
    - The transcript contains no shell command, direct Python call, browser form post, or raw daemon endpoint call.
    - The resulting course is visible through the existing course/browser read flow, proving both surfaces converge on the same durable objects.
  </behavior>
  <action>Add the Reach freeze-gate acceptance scenario. Drive the public MCP protocol as an external agent would: discover tools, create the course, register and bind a synthetic source, add containers/objectives/edges, choose treatments, bind and check a blueprint, audit, export, and verify the package. Use only synthetic fixtures and temporary roots. Then read the resulting course through the existing UI-facing course authority and assert the same identifiers, structure, bindings, and audit state. Exercise a representative assessment start/next/submit sequence through MCP as the retained 999.3 tutor flow, proving the response key remains runtime-owned and the recorded response governs later disclosure.</action>
  <verify><automated>python tests/mcp_roundtrip.py &amp;&amp; python scripts/preflight.py --quick</automated></verify>
  <done>An agent builds and verifies a course through the generated tool table alone, the existing browser flow sees the same durable result, and all ten Phase 999.3 criteria plus the Reach addition have executable proof.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| MCP client to dispatcher | Untrusted tool names and arguments enter local handlers. |
| Dispatcher to runtime/evidence | Existing runtime state decides scoring, tier unlock, and keyed disclosure. |
| JSON-RPC process to stdout | Any diagnostic byte can corrupt the protocol stream. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-19E-01 | Tampering | tools/call input | mitigate | Validate against the packaged published schema before resolving or invoking a handler. |
| T-19E-02 | Information disclosure | assessment responses | mitigate | Reuse existing handlers, runtime.public_item, evidence-backed tier gates, and adversarial no-key assertions. |
| T-19E-03 | Elevation of privilege | tool descriptions and caller fields | mitigate | Ignore authority-shaped claims and read tier, rights, and mutation authority only from existing Python state. |
| T-19E-04 | Denial of service | stdio framing | mitigate | Tolerate cancellation and malformed requests with bounded JSON-RPC errors while keeping stdout parseable. |
| T-19E-SC | Tampering | package supply chain | accept | No package install or new dependency is permitted in this plan. |
</threat_model>

<verification>
Run `python tests/mcp_roundtrip.py`, `python tests/daemon_roundtrip.py`, `python tests/scoring_roundtrip.py`, and `python scripts/preflight.py --quick`. Confirm the MCP module contains no bank parser, scoring call, answer-key lookup, duplicate parity table, or embedded schema copy.
</verification>

<success_criteria>
All Phase 999.3 criteria 1 through 10 pass. The Reach addition passes through a tool-only course build. The existing browser UI and CLI remain reachable and converge with MCP on the same handlers and durable state. V2-INT-03 remains explicitly blocked until stable browser WebMCP support exists and is not falsely claimed by this phase.
</success_criteria>

<source_coverage_audit>
- GOAL: generated MCP table over course-capable API_ROUTES, covered by Tasks 1 through 3.
- REQ V2-INT-02: all five binding transport, parity, disclosure, refusal, and shared-dispatch conditions, covered by Tasks 1 and 2.
- REQ V2-INT-03: preserved as blocked future fourth mount; this plan neither implements nor claims unstable WebMCP.
- RESEARCH/DESIGN: MCP revision 2026-07-28 and scripts/ocr_mcp.py stdio precedent, covered by Task 2 without a new dependency.
- CONTEXT: no 19E-CONTEXT.md exists; the 19E seed and Reach freeze gate are fully represented, with all ROADMAP criteria and the course-building addition covered.
</source_coverage_audit>

<output>
Create `.planning/phases/19E-mcp-tool-table/19E-01-SUMMARY.md` when done.
</output>
