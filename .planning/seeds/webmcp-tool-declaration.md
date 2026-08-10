---
title: WebMCP tool declaration in the Tauri webview
trigger_condition: Phase 13 has a running Tauri webview AND Phase 999.3's MCP tool table exists AND navigator.modelContext has shipped stable in at least one browser
planted_date: 2026-08-10
status: planted
---

# Seed: WebMCP tool declaration in the Tauri webview

## The idea

Declare itembank's tool table to a browser-resident agent via
`navigator.modelContext`, so an agent driving the desktop shell calls
`submit_response` with a typed schema instead of inferring which button submits.

## Why it is plausible here

The tool table already has to exist for Phase 999.3 (stdio and HTTP mounts).
WebMCP is a **fourth mount of the same table**, roughly 30 lines of page script.
The design cost was paid once. Phase 13 puts a real browser inside the product,
which is the precondition.

## Verified status, 2026-08-10

- W3C Web Machine Learning Community Group. Authored by Google and Microsoft engineers.
- Announced 2026-02-10. Draft Community Group Report published 2026-02-12.
- First implementation Chrome 146 Canary; **public origin trial in Chrome 149**.
- Mozilla and Apple participating in the CG. Not shipped stable anywhere.
- `navigator.modelContext` is HTTPS-only.

## Why not now

1. Origin trial, not stable. An origin trial token expires and the API can change.
2. HTTPS-only, and Phase 13's shell talks to the sidecar over plain loopback HTTP.
   Resolving that is a Phase 13 decision, not a WebMCP one.
3. Phase 13 has not started, and Phase 999.3 has not been promoted.

## The trap to carry forward

Same as `.planning/notes/2026-08-10-mcp-as-third-surface.md` §4. A WebMCP tool
*description* is not a gate. The tier check runs in the Python handler behind the
call, never in the page. A page-side check is a check the agent shares an address
space with.

## Cheaper thing that serves the same want

If the goal is only "an agent can drive the app," the stdio MCP server from
Phase 999.3 already does that with no browser, no origin trial, and no HTTPS. Reach
for WebMCP only when the want is specifically *an agent inside the learner's open
window, sharing the live session*.

## Sources

- <https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio>
- <https://www.webfuse.com/webmcp-cheat-sheet>
- <https://dev.to/ai-agent-economy/webmcp-in-2026-which-browsers-support-navigatormodelcontext-complete-compatibility-status-1oe4>
