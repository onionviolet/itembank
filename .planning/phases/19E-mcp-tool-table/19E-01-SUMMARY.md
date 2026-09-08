---
## Why this summary exists
summary_reason: "Measured implementation showed the plan assumed request schemas and a first-source operation that did not exist; both gaps were closed here."
phase: 19E-mcp-tool-table
plan: 01
subsystem: api
tags: [mcp, json-rpc, stdio, schema, course]
requires: [{phase: 19A-course-operating-surface, provides: validated course handlers and parity inventory}]
provides: [generated MCP tools, stdio and HTTP mounts, tool-only course build]
affects: [19D-math-1400, agent-clients]
tech-stack: {added: [], patterns: [resource-backed tool schemas, shared handler adapter]}
key-files:
  created: [surfaces/mcp.py, schemas/api_request.schema.json, tests/mcp_roundtrip.py]
  modified: [surfaces/daemon.py, surfaces/cli.py, surfaces/course_ops.py, schemas/course_operation.schema.json]
key-decisions:
  - "First-source registration mints through journal.commit_operation and accepts only a bounded leaf filename."
  - "MCP membership and names remain generated from API_ROUTES and SURFACE_PARITY."
requirements-completed: [V2-INT-02]
duration: 35min
completed: 2026-09-07
---

# Phase 19E Plan 01: MCP Tool Table Summary

**Resource-backed MCP tools now reach the existing daemon handlers over stdio
and HTTP, including a complete tool-only course build from an empty root.**

## Accomplishments

- Generated one tool per route with published input and output metadata.
- Preserved runtime ownership of scoring, tier unlock, evidence, and disclosure.
- Added bounded first-source minting through the existing journal CAS authority.
- Proved MCP-created structure is visible in the server-rendered UI read flow.

## Verification

MCP, course-operation, and scoring suites pass. The quick preflight's 19E gates
pass; its only failure is concurrent 19B summary formatting. The daemon suite
reaches its previously recorded concurrency timeout after route checks pass.

## Deviations from Plan

Two measured assumptions were false. Older API routes lacked request schemas,
so one packaged request document was added. No route could register the first
source, so `register_source` was added through `journal.commit_operation` with
schema-bounded naming, containment, a one MiB byte limit, atomic write, rights,
and recovery text. Neither change adds a parser, scorer, identity authority, or
MCP-only operation.

## Known Stubs

None. WebMCP is a named future mount and V2-INT-03 remains incomplete.

## Self-Check: PASSED

All listed files exist and the tool-only course package verifies complete and
restorable. No commit was made, as directed by the coordinating agent.
