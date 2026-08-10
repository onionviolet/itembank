# Note: MCP as the third surface, not the third implementation

- **Date:** 2026-08-10
- **Context:** `/gsd-explore` session. Topic: "MCP server as a third client of the itembank runtime."
- **Status:** design decisions recorded. No code. Promotes to Phase 999.3 (see `ROADMAP.md` Backlog).
- **Binds on:** any future plan touching `V2-INT-02`.
- **Research basis:** MCP spec revision **2026-07-28**, verified 2026-08-10 via
  `modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio` and
  `.../server/tools`.

---

## 1. This is not a new idea. It is an existing requirement with a design.

`REQUIREMENTS.md:172` already says it, and the wording is exactly right:

> **V2-INT-02**: MCP as transport over the JSON API, never as a second parser or scorer

Nothing below overturns that line. Everything below is the mechanism under it. The
reason to write it now rather than at V2 planning time is that three of the
decisions are one-way doors on the evidence and payload seams, and one of them
(§4) is a Directive §4.1 hazard that is cheap to design around and expensive to
retrofit.

## 2. The direction distinction, which is the whole point

Phase 8 and this work look similar and are opposites.

| | Phase 8 (Model Adapter) | This (MCP server) |
|---|---|---|
| Direction | itembank calls a model | a model calls itembank |
| The model is | an upstream **producer** of hint text | a downstream **client** of the runtime |
| Gate question | may this text render? | may this tool run, and what may it return? |
| Failure mode | model reveals past the tier | model reads a key it was never granted |
| Config | `model.backend` | server registration in the agent's own config |

They share zero code and must not share a phase. A plan that folds MCP into
Phase 8 has confused "involves an LLM" with "is the same seam."

## 3. What already exists, and why that makes this small

Verified against the tree on 2026-08-10:

- `surfaces/daemon.py:67` `API_ROUTES` already publishes the four verbs an agent
  needs: `POST /api/start`, `/api/next`, `/api/submit`, `/api/report`.
- `surfaces/daemon.py:99-118` `SURFACE_PARITY` already maps every route to its CLI
  command, enforcing Extensibility Rule 7.
- `surfaces/protocol_cli.py` already publishes the five JSON contracts verbatim
  (`item`, `session`, `response`, `report`, `lint_error`) and already ships a
  `COMMANDS` runbook naming which contract each command's output conforms to.

So the MCP tool table is a **projection of an existing table**, not a new design:
one MCP tool per `API_ROUTES` entry, whose `inputSchema` is the already-published
`schemas/*.json` document, read off disk by the same `resources.py` path
`protocol_cli.py` uses. No second contract, no embedded copy, no drift.

**Amend `SURFACE_PARITY` to three columns** (route, CLI command, MCP tool) rather
than adding a fourth parity map. The existing test that fails on an unmapped route
then fails on an unmapped tool for free.

## 4. The Directive §4.1 hazard, and the exact shape of the fix

§4.1: *"The **runtime**, not a model, decides what reaches the learner."*

An MCP server hands an agent a tool table. If any tool returns
`runtime.explain_payload()`, the agent holds the key, the rationale, and the
distractor analysis before the learner has answered, and §4.1 is dead. Worse than
dead: it is dead invisibly, because the HTTP surface still behaves correctly and
every existing test still passes.

Three rules, all one-way doors, decided here:

1. **Pre-response tools return `public_item()` and nothing else.** Same function
   the HTTP surface calls. The MCP layer never constructs a payload; it forwards
   one.
2. **`explain_payload()` is reachable only after a recorded response for that
   item exists in the evidence store.** The gate is the evidence log, not a flag
   on the request, because the evidence log is the thing that cannot be argued
   with.
3. **Tier gating is server-side and identical to the HTTP path.** The tool
   *description* is not a control. A description is a system prompt with better
   marketing, and the entire product thesis is that a system prompt can be talked
   past. Read the tier in the handler.

**MCP's own error semantics fit this exactly, which is a genuine piece of luck.**
The spec distinguishes protocol errors from tool execution errors: a business-logic
refusal is a normal result with `isError: true` plus explanatory text, *not* a
JSON-RPC error (`-32602` is reserved for unknown tool / malformed request). So
"tier 2 is locked, the unlock condition is N" is a first-class, spec-blessed
response shape. The runtime refuses in the protocol's own vocabulary. Nothing has
to be invented.

## 5. Spec facts that change the build

- **Revision 2026-07-28 made the core stateless.** `initialize` and
  `notifications/initialized` are **removed**. Discovery is `server/discover`,
  returning `supportedVersions`. Protocol version, clientInfo, and capabilities
  ride `_meta.io.modelcontextprotocol/*` on every request.
- **Minimum server: `server/discover`, `tools/list`, `tools/call`.** Plus
  `notifications/cancelled` (may be ignored) and a **legacy `initialize` fallback**,
  because clients probe `server/discover` first and fall back on any error, and it
  is unverified whether Claude Code and Codex speak the new revision today. Build
  both paths.
- **Transport is still newline-delimited JSON-RPC over stdin/stdout.** No
  `Content-Length`, no headers. UTF-8. Messages must not contain embedded
  newlines. **The server must not write non-MCP bytes to stdout.** stderr is free.
  That last rule collides with this codebase's `print()`-to-stdout logging
  convention and is the single most likely way a first implementation breaks.
- **The server MUST validate all tool inputs.** Clients only SHOULD validate
  results. So schema enforcement is ours. `schema_validate.py` already exists and
  the six schemas are flat, so this is hand-validation, not a dependency.
- **`structuredContent` + `outputSchema` are optional.** Declare `outputSchema`
  anyway and mirror the JSON into a TextContent block, per the SHOULD. Declaring it
  costs nothing and makes the published contracts machine-checkable at the boundary.
- **Size:** roughly 350 to 450 lines of stdlib Python for transport, dispatch,
  discover-plus-legacy, and six tools. Estimate, not measured.

## 6. Transport: build both, per Directive §3

stdio and the existing loopback HTTP daemon are both defensible and neither is
wrong. The spec explicitly notes the stdio framing is reusable over TCP and Unix
domain sockets, so this is one framing function with two mounts, not two servers.

- **stdio** is what Claude Code and Codex register natively today. Zero ports, zero
  firewall, process lifetime tied to the agent.
- **HTTP mount on the Phase 2 daemon** is what the desktop shell (Phase 13) and any
  already-running instance need, and it is what makes an agent and a human able to
  share one live session.

Both register against **the same tool table**, which is the same `SURFACE_PARITY`
map. This does not trip §4.2: no second parser, no second scorer, no second
evidence store. It is one dispatcher with two byte-transports.

## 7. WebMCP, and why it is a seed rather than scope

W3C Web Machine Learning CG, authored by Google and Microsoft engineers.
Announced 2026-02-10, Draft Community Group Report 2026-02-12, first implementation
Chrome 146 Canary, public origin trial in Chrome 149. It puts
`navigator.modelContext` on HTTPS pages so a page declares callable tools to an
agent in the browser instead of the agent guessing which button submits.

Relevance is real and later: Phase 13's Tauri webview is a browser, and the tool
table from §3 is the same table. WebMCP is then a fourth mount, roughly 30 lines,
not a fourth design.

Two reasons it is not in scope now: it needs an origin trial token and HTTPS, and
Phase 13 has not started. See `.planning/seeds/webmcp-tool-declaration.md`.

## 8. The accessibility finding, which is free value

Agent browser automation moved off raw DOM onto the **accessibility tree**, the
browser's semantic projection of roles, names, states, and relationships.
Playwright MCP, Browser Use, and Skyvern all snapshot the AX tree rather than
screenshots, because it is cheaper in tokens and yields exact element handles.
A reported 2026 UC Berkeley / Michigan figure puts agent task success at 78% on a
clean AX tree against 42% on a degraded one (reported via Search Engine Journal,
**not verified at source**, treat as indicative only).

**Consequence for this project: none, and that is the finding.** `UI-SPEC.md` §8
already gates nine accessibility items and §7 already mandates "Native semantic
HTML first." The work that satisfies Directive §4.5 is the same work that makes
every surface agent-legible. Record it so a future session does not propose a
separate "agent readability" workstream that is already paid for.

## 9. What this note does not settle

- Whether an MCP session and a browser session may be the *same* session id, or
  whether an agent always gets its own. Leaning: same, because the point is a tutor
  working alongside the learner, and the evidence store already distinguishes actors.
  Not decided here.
- Whether authoring and lint tools (`lint`, `guard`, `export`) belong in the same
  tool table as the sitting tools, or a second registration. Leaning: same table,
  different capability group, because §4.2 does not care and Rule 7 does.
- Whether `mark_proposal` (Phase 8 criterion 12) is reachable over MCP at all.
  Leaning: no, until Phase 8 lands.

## 10. Related

- `REQUIREMENTS.md` V2-INT-02 (expanded 2026-08-10 with the §4 rules)
- `ROADMAP.md` Phase 999.3
- `ROADMAP.md` Extensibility Rules 1 and 7
- `.planning/seeds/webmcp-tool-declaration.md`
- `.planning/notes/2026-08-10-tanstack-verdict.md`
