# Phase 2: Daemon Consolidation & Settings Foundation - Context

**Gathered:** 2026-08-07
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers two things and nothing else:

1. **One daemon on one port** serving `/`, `/quiz/<bank>`, `/study/<bank>`, `/report`,
   `/api/*`, and the day view — replacing the server-per-subcommand pattern
   `server.py`/`quiz.py`/`day.py` use today — with a CLI command equivalent for every
   route.
2. **A settings foundation**: `itembank.json` and an `itembank config` command that
   prints the settings schema the way `spec` prints the format contract, rejecting an
   invalid value with a named error.

**Explicitly not in this phase:** the browser holding no key / doing no scoring for
quiz and study pages (SURF-02, Phase 4's job), theming (Phase 4), any real behavior
behind daily cap / selection weights / auditor autonomy / model backend / update
policy — those keys exist in the schema now but stay inert until their owning phase
(4, 7, 8, 10, 11, 12) reads them.

</domain>

<decisions>
## Implementation Decisions

**All decisions in this section were delegated by the user** ("just decide whats best
and auto everything" — no per-question discussion occurred this session). Each is
Claude's judgment call, grounded in the pre-roadmap research doc's own architecture
sketch and in patterns Phase 1 already established. See "Claude's Discretion" below.

### Daemon Architecture

- **D-01:** A new `daemon.py` module owns **one `Handler` subclass and a route
  table** (`/`, `/quiz/<bank>`, `/study/<bank>`, `/report`, `/settings`, `/api/*`,
  day view), replacing the per-surface `Handler` subclasses `quiz.py` and `day.py`
  each own today. Route handlers are thin dispatchers that call the *existing*
  render functions (`quiz.page_for()`, the `study` and `day` equivalents) rather
  than reimplementing HTML generation. This matches the research doc's own sketch
  (`.planning/research/ARCHITECTURE.md:100`) and keeps SURF-04 literally true — no
  second implementation of anything `runtime.py`/the surfaces already decide.
  — **Reversibility:** costly — `quiz.py` and `day.py` currently each own a
  `Handler` subclass; migrating them from call-owning to called-into touches both
  files' entry points, though the render functions themselves stay put.

### Second-Instance Behavior

- **D-02:** The daemon is a **detect-and-attach singleton**: on startup it tries
  the configured/default port; if the bind fails because the port is in use, it
  probes that port for an itembank-identifying response and, if confirmed, prints
  "itembank is already running at http://127.0.0.1:<port>" and exits (or opens the
  browser there) instead of silently falling back to a new OS-assigned port.
  SURF-03's "does not fight over the port" is satisfied as *no second daemon ever
  binds*, not as *two daemons peacefully coexist on different ports*. `server.py`'s
  existing OS-assigned-port fallback (`bind()`, line 40) is untouched for other
  callers (e.g. throwaway servers in tests) — this decision is scoped to the
  daemon's own startup path only.
  — **Reversibility:** reversible — the probe-and-attach logic is new code the
  daemon owns; reverting to silent fallback is a small, local change.

### Bank Addressing & /api/* Scope

- **D-03:** The daemon takes a **working directory (or explicit bank/plan paths)**
  as a startup argument, scans it once for `.md` bank files and day-plan files, and
  serves them by filename stem in the URL (`/quiz/<bank-stem>`), resolving the stem
  back to a file path through that pre-scanned allowlist — never by taking a raw
  filesystem path directly from the URL. This matters once `--lan` is on: a
  browser-supplied path would otherwise be attacker-influenceable input from
  another device on the wifi.
  — **Reversibility:** costly — a different addressing scheme (e.g. an explicit
  `?path=` query param) would touch every route's resolution logic and the CLI
  startup args together.

- **D-04:** In this phase, **`/api/*` mirrors exactly the four existing
  agent-facing session commands** — `start`, `next`, `submit`, `report` — as JSON
  routes over the same runtime calls `surfaces/session.py` already uses. This gives
  SURF-04 CLI parity for the routes this phase actually stands up. It does **not**
  yet implement SURF-02's "browser holds no key, no scoring" for the quiz/study
  pages themselves — that stays Phase 4's job.
  — **Reversibility:** reversible — additive; later phases add more `/api/*` routes
  without breaking this one.

### Settings Scope & Mechanism

- **D-05:** `itembank.json` ships now with **all six keys** named in PROJECT.md
  (theme, daily cap, selection weights, auditor autonomy, model backend, update
  policy) plus the daemon's own settings (default port, default `--lan` value),
  each with a documented type, allowed values/range, and a default. Keys with no
  owning phase yet are explicitly marked **inert** in the schema text — present and
  settable, but read by nothing until Phases 4/7/8/10/11/12 land. This follows the
  research doc's explicit sequencing note
  (`.planning/research/ARCHITECTURE.md:348,357`) that the settings mechanism is
  cheapest scaffolded now with a minimal schema, extended additively later.
  — **Reversibility:** reversible — additive; a later phase adding real behavior
  behind a key does not touch this phase's schema shape.

- **D-06:** `itembank config` (no args) **prints the settings schema**, mirroring
  `itembank spec`'s existing precedent. `itembank config set KEY VALUE` writes and
  validates a single value; an invalid value is rejected with a **dotted error
  code** in the same style Phase 1's D-16 established for lint (e.g.
  `settings.invalid_type`, `settings.out_of_range`) rather than a generic message.
  — **Reversibility:** one-way — once an agent parses `config`'s output shape or
  error codes, changing them is a breaking change to a published contract, the same
  rationale D-16 already recorded for lint codes.

- **D-07:** Settings validation **reuses Phase 1's `schema_validate.py`**
  (`validate(instance, schema)`), the stdlib-only JSON Schema validator already
  built for `schemas/*.json`, rather than a second hand-written checker. One
  validation mechanism for both item schemas and settings.
  — **Reversibility:** reversible — swapping validators later touches one call
  site.

### Claude's Discretion

The user delegated all four gray areas explicitly rather than answering
per-question this session. Every decision above is Claude's judgment call,
grounded in the pre-roadmap research doc's own architecture sketch (`daemon.py`,
one `Handler`, route table) and in patterns Phase 1 already established (dotted
lint-style error codes, `schema_validate.py`, additive settings). If a planner
finds any of D-01 through D-07 impractical against the real `quiz.py`/`day.py`/
`study.py` code, that is a legitimate reversal — flag it as a decision checkpoint
rather than silently overriding, the same rule Phase 1's `01-CONTEXT.md` set for
its own delegated decision (D-02).

- Exact settings file field names/casing, the `/api/*` JSON response shape for
  start/next/submit/report, and the identifying response the daemon's
  already-running probe expects back are all unconstrained implementation detail.
- Whether today's `serve`/`study`/`day` CLI commands stay as-is alongside a new
  `daemon` command, or get folded into it, is left for the planner: SURF-04 only
  requires that daemon routes each have a CLI equivalent, not that existing
  commands are removed.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §"Phase 2: Daemon Consolidation & Settings Foundation" —
  goal and the four success criteria this phase must satisfy.
- `.planning/REQUIREMENTS.md` lines 116–120 — SURF-01, SURF-03, SURF-04, and lines
  139–140 — DEL-04, DEL-05, the requirements this phase closes.
- `.planning/PROJECT.md` §Constraints, §Key Decisions — stdlib-only rule, "every
  capability reachable from both app and CLI," and the one-settings-file decision
  this phase implements.

### Prior art and sequencing guidance
- `.planning/research/ARCHITECTURE.md` lines 100, 108, 348, 357 — the `daemon.py`
  / one-`Handler` / route-table sketch (D-01) and the "settings mechanism
  scaffolded early with a minimal schema, later phases register their own keys"
  sequencing note (D-05) this phase's decisions build directly on.
- `.planning/research/SUMMARY.md` §"Phase 3: LESSON Format + Settings Scaffold" —
  pre-roadmap-renumbering; its settings-scaffold content maps to this phase, not
  current Phase 3. Corroborates the minimal-schema-now guidance.

### Existing code constraints
- `.planning/codebase/ARCHITECTURE.md` §"Server Layer", §"Architectural
  Constraints" — `server.py`'s current `Handler`/`bind()` pattern and the "single
  server instance per surface" constraint this phase deliberately changes.
- `.planning/codebase/INTEGRATIONS.md` §"Webhooks & Callbacks" — the current POST
  endpoints (`/submit` on the quiz server, `/action` on the day server) the new
  route table must preserve or replace with an equivalent.
- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — D-15/
  D-16 (the `schemas/` directory, dotted lint error codes) and the reusable
  `schema_validate.py` / `write_session()` patterns D-06/D-07 above build on
  directly.

### No external specs beyond these
No ADRs or separate specs exist for the daemon or settings. `model.SPEC` and
`itembank spec` are the precedent `itembank config` follows; read `model.py` for
the shape being mirrored.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`schema_validate.py:validate()/check_schema()`** — the stdlib JSON Schema
  validator built in Phase 1 for `schemas/*.json`; D-07 reuses it for settings
  validation instead of writing a second one.
- **`surfaces/quiz.py:page_for()`** (line 18) — existing quiz HTML render
  function; D-01's route handlers call into this rather than duplicating it.
- **`surfaces/session.py:cmd_start/cmd_next/cmd_submit/cmd_report`**
  (lines 37–122) — the exact runtime calls D-04's `/api/*` routes wrap.
- **`server.py:bind()`** (line 40) — existing port-fallback logic; D-02 layers
  detect-and-attach on top rather than replacing it for non-daemon callers.

### Established Patterns
- `server.py:Handler` (line 15) is meant to be subclassed with `do_GET`/`do_POST`
  added — today one subclass per surface (`quiz.py`, `day.py`). D-01 collapses
  this to one subclass with internal routing.
- Every surface reaches a verdict through `runtime.score_response()` and loads via
  `model.load()` — the daemon's routes must stay callers of these, never
  reimplement them, mirroring the "Scoring in Multiple Places" anti-pattern
  already documented in `codebase/ARCHITECTURE.md`.
- Phase 1's D-16 dotted-lint-code precedent (`item.missing_key`, etc.) is the
  direct model for D-06's settings error codes.

### Integration Points
- New `daemon.py` — owns the `Handler`/route table; imports from `quiz.py`,
  `study.py`, `day.py`, `session.py` rather than the reverse.
- New `itembank.json` (repo root, beside `lanes.md` per PROJECT.md) — read and
  written by a new `config` command in `surfaces/cli.py`.
- `surfaces/cli.py` — gains a `config` command (`cmd_config`); whether the
  existing `serve`/`study`/`day` commands stay standalone or gain a `daemon`
  sibling is left to the planner (see Claude's Discretion above).

</code_context>

<specifics>
## Specific Ideas

No specific implementation ideas were raised — the user delegated all four gray
areas without describing a particular mechanism or reference. Every mechanism
above is Claude's inference from the research doc and Phase 1 precedent, not a
stated preference; treat it as a strong default, not a locked requirement.

</specifics>

<deferred>
## Deferred Ideas

None — no discussion turns occurred this session, so no scope-creep ideas came up
to defer.

</deferred>

---

*Phase: 2-Daemon Consolidation & Settings Foundation*
*Context gathered: 2026-08-07*
