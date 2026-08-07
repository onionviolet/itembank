# Phase 2: Daemon Consolidation & Settings Foundation - Research

**Researched:** 2026-08-07
**Domain:** Consolidating N ad hoc `http.server` processes into one routed daemon; a stdlib JSON-Schema-validated settings file, over an existing Python-stdlib-only codebase
**Confidence:** HIGH — every claim below is grounded in the actual source files read this session (`server.py`, `surfaces/quiz.py`, `surfaces/quiz_page.py`, `surfaces/day.py`, `surfaces/study.py`, `surfaces/session.py`, `surfaces/cli.py`, `runtime.py`, `model.py`, `schema_validate.py`, `surfaces/protocol_cli.py`), not external-library research — this phase has almost no external-library surface because the project is stdlib-only.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

All seven decisions below were delegated by the user ("just decide whats best and
auto everything") and are Claude's judgment calls, not user-stated preferences.
CONTEXT.md explicitly invites a planner (and this research) to flag any of them as
impractical rather than silently overriding — several are flagged below.

- **D-01:** A new `daemon.py` module owns **one `Handler` subclass and a route
  table** (`/`, `/quiz/<bank>`, `/study/<bank>`, `/report`, `/settings`, `/api/*`,
  day view), replacing the per-surface `Handler` subclasses `quiz.py` and `day.py`
  each own today. Route handlers are thin dispatchers that call the *existing*
  render functions (`quiz.page_for()`, the `study` and `day` equivalents) rather
  than reimplementing HTML generation.
  — Reversibility: costly.
- **D-02:** The daemon is a **detect-and-attach singleton**: on startup it tries
  the configured/default port; if the bind fails because the port is in use, it
  probes that port for an itembank-identifying response and, if confirmed, prints
  "itembank is already running at http://127.0.0.1:<port>" and exits (or opens the
  browser there) instead of silently falling back to a new OS-assigned port.
  SURF-03's "does not fight over the port" is satisfied as *no second daemon ever
  binds*, not as *two daemons peacefully coexist on different ports*. `server.py`'s
  existing OS-assigned-port fallback (`bind()`) is untouched for other callers.
  — Reversibility: reversible.
- **D-03:** The daemon takes a **working directory (or explicit bank/plan paths)**
  as a startup argument, scans it once for `.md` bank files and day-plan files, and
  serves them by filename stem in the URL (`/quiz/<bank-stem>`), resolving the stem
  back to a file path through that pre-scanned allowlist — never by taking a raw
  filesystem path directly from the URL.
  — Reversibility: costly.
- **D-04:** In this phase, **`/api/*` mirrors exactly the four existing
  agent-facing session commands** — `start`, `next`, `submit`, `report` — as JSON
  routes over the same runtime calls `surfaces/session.py` already uses. Does not
  yet implement SURF-02's "browser holds no key, no scoring" for quiz/study pages.
  — Reversibility: reversible.
- **D-05:** `itembank.json` ships now with **all six keys** named in PROJECT.md
  (theme, daily cap, selection weights, auditor autonomy, model backend, update
  policy) plus the daemon's own settings (default port, default `--lan` value),
  each with a documented type, allowed values/range, and a default. Keys with no
  owning phase yet are explicitly marked **inert** in the schema text.
  — Reversibility: reversible.
- **D-06:** `itembank config` (no args) **prints the settings schema**, mirroring
  `itembank spec`'s precedent. `itembank config set KEY VALUE` writes and
  validates a single value; an invalid value is rejected with a **dotted error
  code** in the same style Phase 1's D-16 established for lint (e.g.
  `settings.invalid_type`, `settings.out_of_range`).
  — Reversibility: one-way.
- **D-07:** Settings validation **reuses Phase 1's `schema_validate.py`**
  (`validate(instance, schema)`), rather than a second hand-written checker.
  — Reversibility: reversible.

### Claude's Discretion

- Exact settings file field names/casing, the `/api/*` JSON response shape for
  start/next/submit/report, and the identifying response the daemon's
  already-running probe expects back are all unconstrained implementation detail.
- Whether today's `serve`/`study`/`day` CLI commands stay as-is alongside a new
  `daemon` command, or get folded into it, is left for the planner: SURF-04 only
  requires that daemon routes each have a CLI equivalent, not that existing
  commands are removed.

### Deferred Ideas (OUT OF SCOPE)

None — no discussion turns occurred this session, so no scope-creep ideas came up
to defer.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SURF-01 | One daemon serves every surface on one port: day view, sitting, study loop, reports, settings, JSON API | Architecture Patterns (route table over `server.Handler`); Common Pitfalls #1 (multi-bank routing), #4 (threading) |
| SURF-03 | Starting the daemon twice does not fight over the port; `--lan` still reaches a phone | Pattern 2 (detect-and-attach) + Pitfall #2 (Windows errno branching) |
| SURF-04 | Every capability has both a route and a CLI command, over one runtime | Pattern 1 (thin dispatcher over existing `cmd_*`/render functions) + Pitfall #3 (`sys.exit` inside a shared process) |
| DEL-04 | One documented config file holds theme, daily cap, selection weights, auditor autonomy, model backend, update policy | Standard Stack (`itembank.json` schema shape) + Don't Hand-Roll (`schema_validate.py` reuse) |
| DEL-05 | `itembank config` prints the settings schema like `spec`; an invalid value is rejected with a named error | Pattern 4 (`config` mirrors `protocol_cli.py:cmd_schema`) + Pitfall #6 (`minimum`/`maximum` keyword gap) |

</phase_requirements>

## Summary

This phase has almost no external-library research surface — the project is
stdlib-only by hard constraint, and every piece the daemon needs (`http.server`,
`socketserver`, `json`, `argparse`) is already in use elsewhere in this exact
codebase. The real research risk here was **whether the seven delegated decisions
survive contact with the actual code**, and reading `server.py`, `quiz.py`,
`quiz_page.py`, `day.py`, `study.py`, `session.py`, and `runtime.py` directly
surfaced six concrete places where a literal reading of D-01/D-02/D-04 would break
at runtime or reopen a security hole D-03 explicitly closes elsewhere. None of
these are reasons to abandon the decisions — they are refinements the planner
needs stated as tasks, not surprises found mid-implementation.

The two load-bearing findings: **(1)** `surfaces/session.py`'s `cmd_start`,
`cmd_submit`, and `runtime.read_session`/`upgrade_session` call `sys.exit()` on
error paths that are routine in normal use (bad objective, session already
complete, malformed JSON) — literally reusing these functions as `/api/*` handlers
without an explicit `except SystemExit` around the call site means one learner's
bad request kills the daemon for every other route and every other bank being
served from the same process. **(2)** `runtime.read_session()`/`write_session()`
and `model.load()`/`session.py`'s `cmd_start` all take a raw filesystem path with
no allowlist check — D-03's stem-allowlist principle for banks was not extended to
session identifiers or to the `bank` path recorded inside a session file, and
under `--lan` this is the exact "attacker-influenceable input from another device
on the wifi" class of bug D-03's own rationale describes, just on a different
field. Both are addressed below with concrete, low-cost fixes.

**Primary recommendation:** Build `daemon.py` exactly as D-01 sketches — one
`Handler` subclass, one route table, thin dispatchers into `quiz.page_for()` /
`study` / `day` render functions and into `session.py`'s functions for `/api/*`
— but (a) wrap every `/api/*` and POST handler in `except (SystemExit,
Exception)`, never bare `except Exception`; (b) address sessions by `session_id`
through a server-maintained lookup, the same way banks are addressed by stem
through D-03's allowlist, never by raw path; (c) subclass
`socketserver.ThreadingMixIn` so one slow request (Anki's 2-second AnkiConnect
timeout in the day view) cannot block every other route in the one shared
process; and (d) add `minimum`/`maximum` to `schema_validate.py`'s `SUPPORTED`
keyword set, because without it there is no way to actually detect the
"out-of-range" condition D-06's own example error code names.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Route dispatch (`/`, `/quiz/<bank>`, `/study/<bank>`, `/report`, `/api/*`, day view) | Backend (daemon process) | — | `daemon.py` is the one loopback process; there is no separate frontend server tier in this architecture (§CLAUDE.md: single-process, stdlib-only) |
| HTML rendering (quiz/study/day page shells) | Backend (daemon process, at request time) | Browser (renders the returned HTML) | `page_for()`/`day_page()`/`STUDY_TEMPLATE` are server-side string templates evaluated per request; there is no build step or client framework |
| Scoring / session state machine | Backend (`runtime.py`) | — | Unconditional per project constraint: "one runtime, one scorer... the runtime, not the model, decides" |
| Bank/session/plan addressing (stem → path resolution) | Backend (`daemon.py`, at startup and per request) | — | Must never be client-supplied (D-03); this is a server-side allowlist, not a client concern |
| Settings storage (`itembank.json`) | Backend (filesystem, read/written by `surfaces/cli.py:cmd_config`) | — | No settings UI ships in this phase (only the CLI `config` command is required by DEL-05); a `/settings` HTML route is optional per the phase's own success criteria (see Open Questions) |
| Settings validation | Backend (`schema_validate.py`) | — | D-07: one validator, reused, not duplicated per surface |
| Client JS (quiz/study answer widgets) | Browser | — | Existing `quiz_page.py`/`STUDY_TEMPLATE` embedded `<script>`; unchanged in this phase except the POST-path parameterization noted below |
| Second-instance detection | Backend (`daemon.py`, at process startup) | — | A network probe on loopback, not a client-visible capability |

## Standard Stack

This phase adds no third-party dependency; every module below is Python's
standard library and every one is already imported somewhere in this codebase.

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `http.server` (`BaseHTTPRequestHandler`) | stdlib, Python 3.11+ | The daemon's request handler base | Already `server.Handler`'s base class; official docs confirm `self.path` dispatch is the correct primitive for a hand-routed server [CITED: docs.python.org/3/library/http.server.html] |
| `socketserver` (`TCPServer`) | stdlib | Socket bind/accept loop | Already used by `server.bind()` [VERIFIED: server.py:12,48] |
| `socketserver.ThreadingMixIn` | stdlib | Concurrent request handling for the *consolidated* daemon | Not used by the codebase today (each existing server only ever serves one learner one item at a time); needed once one process serves quiz+study+day+api concurrently — see Pitfall #4. [CITED: docs.python.org/3/library/socketserver.html] |
| `json` | stdlib | Settings file I/O, `/api/*` payloads | Already used throughout (`server.Handler.read_json/send_json`, `runtime.write_session`) |
| `argparse` | stdlib | New `daemon`/`config` CLI subcommands | Already the sole CLI framework [VERIFIED: surfaces/cli.py:7,99-303] |
| `urllib.request` | stdlib | The detect-and-attach probe (GET the occupied port, check for an itembank marker) | Already used for the AnkiConnect probe in `day.py` [VERIFIED: surfaces/day.py:359-368] — same "local HTTP GET, short timeout, treat failure as absence" shape applies to D-02's probe |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `webbrowser` | stdlib | Opening the daemon URL, or the "already running" URL, in a browser tab | Already used identically by `quiz.py:cmd_serve` and `day.py:cmd_day` [VERIFIED: surfaces/quiz.py:79,177; surfaces/day.py:829,957] |
| `errno` | stdlib | Distinguishing "port in use" (`EADDRINUSE`) from "port reserved/blocked" (Windows `WinError 10013`) before deciding whether to probe at all | See Pitfall #2 — not used anywhere in the codebase today, but the distinction matters for D-02's own correctness on the exact platform this session ran on (Windows) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-routed `http.server` + dict dispatch | A micro web framework (Flask, `aiohttp`, `bottle`) | Rejected outright — the project's hard constraint is "Python standard library only... no install step" [VERIFIED: `.claude/CLAUDE.md` §Constraints, "Tech stack"]. Flagging this explicitly because "one process, multiple routes" is exactly the shape that tempts an implementer toward a framework; the existing `server.Handler` pattern (`self.path` string matching) is the only option in scope. |
| Port-probe detect-and-attach (D-02) | A PID/lock file in a well-known location | Rejected by D-02 itself; a probe needs no new on-disk state and self-heals if a previous daemon crashed without cleaning up a lock file — worth noting as the reason D-02 is the lower-maintenance choice, not just the user-delegated one. |
| Single-threaded `TCPServer` (today's per-surface pattern) | `socketserver.ThreadingMixIn` | The existing per-surface pattern never needed threading because each server had exactly one concern; the consolidated daemon serves quiz + study + day + report + api from one port, and day's AnkiConnect calls carry a 2-second timeout [VERIFIED: surfaces/day.py:364, `timeout=2`] that would otherwise stall every other in-flight route. |

**Installation:**
```bash
# Nothing to install. daemon.py and the settings module import only stdlib
# modules already present in this repo's Python 3.11+ runtime.
```

**Version verification:** N/A — no third-party package is introduced by this
phase. `python --version` on the machine this research ran on reports `3.13.5`
[VERIFIED: `python --version` output this session]; CI pins `3.11`
[VERIFIED: `.github/workflows/ci.yml:10`, `python-version: "3.11"`]; the project
states `Python 3.11+` as its floor [VERIFIED: `.claude/CLAUDE.md` §Runtime].
`http.server`/`socketserver`/`ThreadingMixIn` are available unchanged across
3.11–3.13.

## Package Legitimacy Audit

**Not applicable to this phase.** The project's tech-stack constraint is Python
standard library only, with two named exceptions (a vendored KaTeX asset for
math rendering and stdlib `urllib` for the opt-in updater) — neither exception is
touched by this phase [VERIFIED: `.claude/CLAUDE.md` §Constraints, "Tech stack"].
No `pip install`, no new import outside `http.server`/`socketserver`/`json`/
`argparse`/`urllib`/`webbrowser`/`errno`, all already present in this codebase's
`import` lines. The Package Legitimacy Gate protocol was not run because there is
nothing to check against a registry.

**Packages removed due to [SLOP] verdict:** none — none proposed.
**Packages flagged as suspicious [SUS]:** none — none proposed.

## Architecture Patterns

### System Architecture Diagram

```
                         ┌─────────────────────────────┐
                         │   itembank daemon <dir>     │  one process, one port
                         │        surfaces/daemon.py    │
                         └──────────────┬───────────────┘
                                         │  startup: scan <dir> once
                                         ▼
                         ┌─────────────────────────────┐
                         │  stem -> path allowlist      │  D-03: banks + day-plan
                         │  (built once, read per req)  │        files by filename
                         └──────────────┬───────────────┘        stem, never a raw
                                         │                        client-supplied path
              ┌──────────────┬──────────┴──────────┬──────────────┬───────────────┐
              ▼              ▼                     ▼              ▼               ▼
        GET /             GET /quiz/<bank>   GET /study/<bank>  GET /report   day view
        (index of         → quiz.page_for()  → study rendering  (NEW: no      → day.day_page()
        scanned banks/       (existing)        (existing)         existing      (existing)
        plans, links)                                             render fn
                                                                    to call
                                                                    into — see
                                                                    Open Q's)
              │
              ▼
        POST /quiz/<stem>/answer  ──────►  runtime.score_response()  ──►  evidence.append_event()
        (parameterized per bank;                (unchanged: the           (unchanged: the one
         quiz_page.py's TEMPLATE                 one scorer)               writer, D-08)
         must stop hardcoding "/answer" —
         see Pitfall #1)

        POST /api/start   ─┐
        POST /api/next     ├──► session_id-addressed lookup (NOT raw path) ──► runtime read/write
        POST /api/submit   │      (extension of D-03's allowlist principle       _session/score_response
        POST /api/report  ─┘      to session identifiers — see Pitfall #5)       (same calls session.py's
                                                                                   cmd_* already make)

        GET/PUT /api/config (optional, Claude's discretion) or
        `itembank config` CLI  ──►  schema_validate.py:validate()  ──►  itembank.json
                                     (extended with minimum/maximum,
                                      see Pitfall #6)                    (atomic write,
                                                                          tmp-then-rename,
                                                                          matching write_session()'s
                                                                          existing pattern)
```

A reader tracing the primary use case (a learner opens the daemon URL, answers a
quiz item, and it is recorded) follows: `GET /quiz/<stem>` renders the page via
the *existing* `quiz.page_for()` → the browser's embedded JS POSTs the answer to
a **bank-scoped** path → the daemon resolves that path back through the same
stem allowlist used at GET time → `runtime.score_response()` (unchanged) →
`evidence.append_event()` (unchanged, same writer every other surface already
uses). Nothing between "browser POSTs" and "evidence recorded" is new logic;
only the routing layer around it is new.

### Recommended Project Structure

```
itembank/
├── server.py                # UNCHANGED: Handler base class, bind() primitive
├── surfaces/
│   ├── daemon.py            # NEW: one Handler subclass, route table, dispatch
│   ├── quiz.py               # page_for() reused as-is by daemon's GET /quiz/<stem>
│   ├── quiz_page.py          # ONE additive change: __POST__ placeholder (Pitfall #1)
│   ├── study.py               # study_item()/STUDY_TEMPLATE reused as-is
│   ├── day.py                  # day_page()/day_info() reused as-is
│   ├── session.py               # cmd_start/next/submit/report's INNER LOGIC reused;
│   │                              daemon calls the same runtime/evidence functions,
│   │                              wrapped so SystemExit cannot escape (Pitfall #3)
│   ├── cli.py                    # gains `daemon` and `config` subcommands
│   └── settings.py               # NEW (name at planner's discretion): schema text,
│                                   defaults, cmd_config(), calls schema_validate.py
├── schema_validate.py         # ONE additive change: minimum/maximum keywords (Pitfall #6)
├── schemas/
│   └── settings.schema.json   # NEW: the itembank.json JSON Schema document
└── itembank.json              # NEW, generated: theme, daily_cap, selection_weights,
                                  auditor_autonomy, model_backend, update_policy,
                                  daemon.port, daemon.lan_default (Claude's discretion
                                  on exact names per CONTEXT.md)
```

### Pattern 1: Thin dispatcher over existing render/runtime functions (D-01)

**What:** `daemon.py`'s route table maps a path pattern to a small function that
extracts URL/body parameters, resolves any bank/session identifier through the
allowlist, and calls straight into `quiz.page_for()`, `day.day_page()`, or the
scoring/session functions `runtime.py`/`evidence.py` already expose — never a
second HTML-generation or scoring implementation.

**When to use:** Every route this phase adds.

**Example (GET route, safe as literally sketched):**
```python
# surfaces/daemon.py — GET /quiz/<stem> is a direct, safe reuse
def handle_quiz_get(self, stem):
    bank_path = self.banks.get(stem)          # D-03 allowlist, never self.path directly
    if bank_path is None:
        self.send_error(404, "no bank named %r" % stem)
        return
    qs = load(bank_path)                        # model.load(), same as every surface
    _, page = quiz.page_for(bank_path, qs, serve=True, reveal=False)
    self.send_html(page.encode("utf-8"))
```
This is exactly what D-01 describes and it is safe unmodified: `quiz.page_for()`
does not call `sys.exit()` and does not touch a raw client-supplied path (the
`stem` was already resolved through the allowlist before this function is
called).

**Example (POST/API route, NOT safe as a literal reuse of `cmd_submit` — see Pitfall #3):**
```python
# surfaces/daemon.py — POST /api/submit
def handle_api_submit(self, body):
    session_path = self.sessions.get(body.get("session_id"))   # NOT a raw path (Pitfall #5)
    if session_path is None:
        self.send_error(404, "unknown session_id")
        return
    try:
        data = read_session(session_path)                       # runtime.py, unchanged
        # ... the same body cmd_submit() runs today, inline or factored out ...
    except SystemExit as exc:                                    # Pitfall #3
        self.send_error(400, str(exc.code))
        return
    self.send_json(result)
```

### Pattern 2: Detect-and-attach singleton, with a probe that degrades safely (D-02)

**What:** On startup, try the fixed/configured port first. On `OSError`, decide
whether to probe based on the *kind* of failure (see Pitfall #2), then either
attach (positive itembank identification) or fall back to `server.bind()`'s
existing free-port logic — never crash startup outright, and never silently
coexist as a second daemon on a *predictable* fixed port.

**Example:**
```python
# surfaces/daemon.py
import errno, urllib.request, urllib.error

MARKER_PATH = "/__itembank__"     # unique to this daemon; not a route a bank/plan
                                   # stem could ever collide with, since D-03 stems
                                   # come from filenames and this is a fixed literal

def probe(port, timeout=0.5):
    """Return True only if something at 127.0.0.1:<port> identifies as this daemon."""
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:%d%s" % (port, MARKER_PATH), timeout=timeout) as r:
            return json.load(r).get("itembank") is True
    except Exception:
        return False               # timeout, connection refused, non-JSON, wrong shape:
                                    # all mean "not us", never "assume us"

def start(port, host, handler):
    try:
        return socketserver.TCPServer((host, port), handler), port, False
    except OSError as exc:
        # WinError 10013 / EACCES: the OS reserved this port (server.py's own
        # documented Hyper-V/WSL accommodation) -- nothing is listening, so
        # probing would just burn the timeout. Skip straight to fallback.
        reserved = getattr(exc, "winerror", None) == 10013 or exc.errno == errno.EACCES
        if not reserved and probe(port):
            print("itembank is already running at http://127.0.0.1:%d/" % port)
            sys.exit(0)             # exit here is fine: this is the CLI entry
                                     # point's own process, not a request handler
        srv = server.bind(handler, port, host)   # existing free-port fallback,
        return srv, srv.server_address[1], True   # reused, not re-implemented
```

**Trade-offs:** This slightly extends D-02's own framing ("no second daemon ever
binds") to explicitly allow the *existing* free-port fallback in the one case
that fallback already exists for (a Windows-reserved port that nothing is
listening on) while still refusing to fall back when another itembank instance
is genuinely running on the configured port. See Pitfall #2 for why collapsing
these two cases into one code path is wrong.

### Pattern 3: Bank *and day-plan* addressing by pre-scanned stem (D-03)

**What:** At daemon startup, walk the given working directory once. Classify
each `.md` file the same way `cmd_guard` already does — `model.parse_bank(text)`
returns a non-empty list for a real bank (empty list for anything else, no
exception) [VERIFIED: model.py:27-36, "def parse_bank(text): ... return
questions"; used this way already at cmd_guard: "n = len(parse_bank(open(p,
encoding='utf-8').read()))... if n > 0"] — and treat a file with at least one
dated first-column row (`day.parse_plan()`) as a day plan. Build two dicts,
`{stem: path}` for banks and `{stem: path}` for plans, once, before serving any
request.

**When to use:** Resolving every `/quiz/<stem>`, `/study/<stem>`, and day-view
path segment. Never accept a filesystem path directly from a URL or POST body.

**Existing precedent for the same principle already in this codebase:**
`day.py`'s `/open` route already does exactly this — it resolves a client-sent
`(lane, index)` pair against a server-built `files` list from `lane_files()`,
never a client-sent path [VERIFIED: surfaces/day.py:892-901, "Only paths this
server itself resolved are openable; a client names a lane and an index, never
a path."]. D-03 is not inventing a new pattern; it is extending one this
codebase already trusts.

### Pattern 4: `config` mirrors `schema`'s existing "no processing, print the
document" precedent (D-06)

**What:** `itembank schema` already established the exact shape D-06 asks
`config` to follow — a table of names/summaries with no args, the full document
verbatim with a name, and `--all` for everything in one object
[VERIFIED: surfaces/protocol_cli.py:77-104]. `cmd_config` with no args should
follow the identical three-tier shape: `itembank config` → human table,
`itembank config schema` (or similar) → the raw JSON Schema document,
`itembank config set KEY VALUE` → validate-then-write.

**Example, modeled directly on `cmd_schema`:**
```python
# surfaces/settings.py (name at planner's discretion)
def cmd_config(a):
    schema = json.loads(_load_schema_text())
    if a.action == "set":
        settings = _read_settings()                    # itembank.json, or defaults
        try:
            new_value = json.loads(a.value)              # int/bool/string/array all
        except json.JSONDecodeError:                      # decode as JSON first, so
            new_value = a.value                            # "true"/"3" behave, "foo" falls
                                                             # back to a bare string
        errs = schema_validate.validate(
            new_value, schema["properties"][a.key])
        if errs:
            code = _classify(errs[0])                       # settings.invalid_type /
            sys.exit("%s: %s" % (code, errs[0]))              # settings.invalid_value /
                                                                # settings.out_of_range
        settings[a.key] = new_value
        _write_settings(settings)                            # atomic tmp-then-rename,
        return 0                                              # matching write_session()
    print(_load_schema_text() if a.action == "schema" else _summary_table(schema))
    return 0
```

### Anti-Patterns to Avoid

- **A second scoring/session-state path in the daemon's POST handler:** Do not
  let `/api/submit` call `runtime.score_response()` and roll its own
  cursor/idempotency bookkeeping "because it's right there." This is exactly the
  debt `quiz.py`/`day.py` already carry today (each owning its own server glue)
  reappearing at the JSON layer. Call the same body `cmd_submit()` runs, not a
  parallel one.
- **Treating `sys.exit()` inside a reused `cmd_*` function as harmless because
  "it always was before":** It was harmless when each `cmd_*` ran as its own OS
  process invocation. It is not harmless once the same function runs inside a
  long-lived shared daemon process — see Pitfall #3.
- **Introducing a web framework "just for routing":** The stdlib `self.path`
  dispatch pattern `server.Handler` already established is the only option in
  scope; see Standard Stack → Alternatives Considered.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| JSON Schema validation for settings | A second hand-written type/range checker | `schema_validate.py:validate()` (D-07), extended with `minimum`/`maximum` (Pitfall #6) | One validator for item schemas and settings; the codebase's own stated reason for building `schema_validate.py` in Phase 1 was exactly to avoid a second implementation |
| HTTP routing for multiple paths on one port | A dict-of-regex router library, or a framework | `self.path` string matching in one `Handler.do_GET`/`do_POST`, same shape `server.Handler` already uses | stdlib-only constraint; the existing pattern already scales to a route table (it is what D-01's sketch literally is) |
| Second-instance detection | A PID file / lock file mechanism | A loopback HTTP probe against the daemon's own marker route (Pattern 2) | No new on-disk state to go stale after a crash; reuses the same request/response primitives the daemon already has |
| Settings file atomic write | A bespoke locking scheme | The tmp-then-`os.replace()` pattern `runtime.write_session()` already uses [VERIFIED: runtime.py:178-185] | Established, tested pattern already proven durable on this exact Windows machine per Phase 1's D-spike |
| Dotted settings error codes | A hand-maintained enum disconnected from validation | A thin classifier over `schema_validate.py`'s returned error strings (keyword-pattern match: "expected type" → `settings.invalid_type`, "is not one of" → `settings.invalid_value`, "less than minimum"/"greater than maximum" → `settings.out_of_range`), mirroring how `model.LintError` wraps a code around validation output [VERIFIED: model.py:373-382] | Keeps `schema_validate.py`'s return contract (list of plain strings) unchanged for its existing CI callers while still satisfying D-06's dotted-code requirement |

**Key insight:** Nearly everything this phase needs already exists somewhere in
this codebase in a slightly narrower form (one-bank routing, one-plan routing,
one schema-printing command, one atomic-write pattern, one client-resolved-path
allowlist). The actual work is *generalizing* four or five single-purpose
precedents into route-table entries, not inventing new mechanisms — and the
risk is precisely in the details each precedent quietly assumed ("there is only
one bank," "this function's caller is always a CLI process that's fine to
exit") that stop holding once one process serves everything at once.

## Common Pitfalls

### Pitfall 1: `quiz_page.py`'s embedded JS hardcodes `POST "/answer"`

**What goes wrong:** `quiz.py`'s existing single-bank server always serves
exactly one bank, so its page's JS can safely hardcode `fetch("/answer", ...)`
[VERIFIED: surfaces/quiz_page.py:155, `const res = await fetch("/answer",
{method:"POST", ...`]. Under the daemon, one process serves multiple banks from
one port simultaneously (`/quiz/<stem-a>`, `/quiz/<stem-b>`, ...). If the
template is reused unmodified, every open quiz tab POSTs to the *same* absolute
`/answer` path with no bank context, and the daemon cannot tell which bank
(and therefore which evidence directory, which attempt file) the answer belongs
to.
**Why it happens:** `page_for()`/`quiz_page.py:TEMPLATE` were designed for a
one-bank-per-process world and were not built with a route parameter in mind.
**How to avoid:** Add one placeholder to `TEMPLATE` (e.g. `__POST__`) that
`page_for()` fills with the bank-scoped path (`/quiz/<stem>/answer`), matching
the existing `__DATA__`/`__SERVE__`/`__TITLE__` substitution pattern already in
the same function [VERIFIED: surfaces/quiz.py:28-33]. This is a one-line
template edit plus one new `.replace()` call in `page_for()`.
**Warning signs:** A manual pass opening two different banks in two tabs at
once and answering in the second tab; if the first tab's attempt file gains the
entry instead, this pitfall was not addressed. (`study.py`'s
`STUDY_TEMPLATE` has no `fetch()` calls at all [VERIFIED: no `fetch(` anywhere
in surfaces/study.py — session-only Learn loop, "session-only" per its own
docstring] — this specific pitfall is unique to the quiz surface.)

### Pitfall 2: Not every bind failure means "another itembank instance"

**What goes wrong:** `server.py`'s own docstring for `bind()` documents that
Windows reserves scattered port ranges for Hyper-V/WSL, producing an `OSError`
that "reads as a bug in this tool" [VERIFIED: server.py:41-46]. If D-02's probe
logic treats *every* bind failure as "maybe another itembank instance, go
probe," it will burn a network timeout probing a port nothing is listening on,
on the exact platform (Windows) this research session ran on, every time that
reserved-range condition recurs.
**Why it happens:** `OSError` on a failed bind conflates "address already in
use" (`errno.EADDRINUSE`) with "permission denied / reserved" (`errno.EACCES`
or Windows `WinError 10013`), and D-02's decision as written does not
distinguish them.
**How to avoid:** Branch on the error before probing — see Pattern 2's code
example. Reserved-port errors go straight to `server.bind()`'s existing
free-port fallback with no probe attempted; only address-in-use errors are
worth a probe.
**Warning signs:** The daemon takes a visibly longer time (up to the probe
timeout) to start on a machine where the default port happens to fall in a
reserved range, with no other itembank process running.

### Pitfall 3: `sys.exit()` inside a reused `cmd_*` function kills the whole shared daemon

**What goes wrong:** `surfaces/session.py:cmd_start` calls `sys.exit("no items
match objective %r" ...)` and `sys.exit("refusing to start a bank with
errors...")` [VERIFIED: surfaces/session.py:41,45]; `cmd_submit` calls
`sys.exit("session is already complete")` twice [VERIFIED:
surfaces/session.py:79,84]; `runtime.read_session`/`upgrade_session` call
`sys.exit()` on a malformed or version-mismatched session file [VERIFIED:
runtime.py:155,159,165,174]. `SystemExit` is not a subclass of `Exception` —
`except Exception` (the pattern `quiz.py`'s existing POST handler already uses
[VERIFIED: surfaces/quiz.py:160, `except Exception as exc:`]) does **not**
catch it. If a daemon route calls these functions directly and a routine error
condition (a stale session, a bad objective) hits, `SystemExit` propagates
un-caught through the request handler and out through `socketserver`'s request
loop — one bad request from one learner's browser tab kills the daemon serving
every other bank, every other tab, and the day view, for the whole household.
**Why it happens:** These functions were designed to be a CLI process's entire
`main()` — exiting the process *is* the correct way for a CLI command to report
an error. That assumption silently breaks the moment the same function is
called from inside a long-lived shared server process instead of being the
process.
**How to avoid:** Wrap every `/api/*` and POST call site in `except SystemExit
as exc: self.send_error(400, str(exc.code))`, in addition to (not instead of)
the existing `except Exception` pattern. This is a small, mechanical fix — it
does not require rewriting `cmd_start`/`cmd_submit` to stop calling `sys.exit`,
though the planner may prefer that as a cleaner long-term fix at slightly more
cost (touches `surfaces/session.py`, which is on today's CLI path too).
**Warning signs:** A manual verification pass that submits a second answer to
an already-completed session over `/api/submit` and finds the *entire* daemon
unresponsive afterward, not just that one request.

### Pitfall 4: One synchronous `TCPServer` now serves everything at once

**What goes wrong:** Today, `quiz.py`'s `serve` and `day.py`'s `day` each run
their *own* single-threaded `socketserver.TCPServer` [VERIFIED: server.py:48,
`socketserver.TCPServer((host, port), handler)`, no `ThreadingMixIn`], and each
only ever has one concern in flight — reasonable when it is the only thing
listening. `day.py`'s Anki lookup carries an explicit 2-second network timeout
per call, potentially several calls per page render [VERIFIED:
surfaces/day.py:364, `timeout=2`, called once per lane with a configured
deck]. Under the daemon, one process now serves quiz + study + day + report +
api concurrently; a plain (non-threaded) `TCPServer` handles one request to
completion before accepting the next, so a slow day-view render (AnkiConnect
timing out) stalls a quiz page load happening at the same moment on the same
port.
**Why it happens:** The single-threaded assumption was correct for N
single-purpose servers and stops being correct the moment they are consolidated
into one.
**How to avoid:** Subclass `socketserver.ThreadingMixIn` alongside
`socketserver.TCPServer` for the daemon specifically (`server.py`'s `bind()`
primitive can stay untouched for other callers, per D-02's own scoping note) —
two lines, stdlib-only, no new dependency.
**Warning signs:** A manual verification pass with Anki closed (so every
AnkiConnect call times out at its full 2 seconds) that also loads `/quiz/<
bank>` in a second tab at the same moment, and observes the quiz page hang for
the duration of the day view's Anki timeouts.

### Pitfall 5: D-03's allowlist principle does not automatically cover sessions

**What goes wrong:** D-03 explicitly protects *bank* addressing with a
pre-scanned stem allowlist because "a browser-supplied path would otherwise be
attacker-influenceable input from another device on the wifi" once `--lan` is
on. But `runtime.read_session(path)`/`write_session(path, data)` take a raw
filesystem path with **no allowlist check at all** — `session_path(path)` is
just `os.path.abspath(path)` [VERIFIED: runtime.py:133-134,170-185] — and
`write_session` will `os.makedirs(os.path.dirname(target), exist_ok=True)`
before writing [VERIFIED: runtime.py:180]. `surfaces/session.py:cmd_start`
similarly stores whatever bank path it was given, verbatim, as
`os.path.abspath(a.bank)` inside the session file [VERIFIED:
surfaces/session.py:52, `"bank": os.path.abspath(a.bank)`], and `cmd_next`/
`cmd_submit` then `load(data["bank"])` that stored path with no re-validation.
If `/api/start`, `/api/next`, `/api/submit`, or `/api/report` accept a raw
`session` path (or a raw `bank` path) straight from a `--lan` client's JSON
body — the literal reading of D-04 ("mirrors exactly the four existing
session commands... over the same runtime calls") — this reopens exactly the
class of vulnerability D-03 was written to close, just via a different
field: an attacker on the same wifi could point `session` at an arbitrary path
and cause the daemon to create directories and write JSON files anywhere the
process has filesystem permission, or read arbitrary files that happen to
parse as JSON.
**Why it happens:** D-03's rationale was written specifically about *bank*
addressing; D-04 was written about *route scope* (which four commands become
routes), and the two decisions don't explicitly connect on this point — a real
gap CONTEXT.md's own "flag a reversal as a decision checkpoint" clause exists
for.
**How to avoid:** Extend D-03's allowlist principle to session identifiers:
`/api/*` should address a session by its existing opaque `session_id`
[already generated as `uuid.uuid4().hex` at `cmd_start`, VERIFIED:
surfaces/session.py:51], with the daemon maintaining (or deriving at request
time, by scanning the working directory's `_attempts/` folder for
`session_*.json` and matching `session_id` inside each) a `session_id → path`
lookup — never accepting a client-supplied path. `/api/start`'s `bank`
parameter must resolve through the exact same stem allowlist D-03 already
builds for GET routes, not accept a raw path either.
**Warning signs:** A security-review pass (or `security-review` skill run)
that POSTs `{"session": "../../../../etc/passwd"}` (or a Windows-equivalent
absolute path outside the working directory) to `/api/next` under `--lan` and
gets anything other than a clean 404/400.

### Pitfall 6: D-06's `settings.out_of_range` error code has no keyword to detect it

**What goes wrong:** `schema_validate.py`'s `SUPPORTED` keyword set is
`{"type", "properties", "required", "additionalProperties", "enum", "const",
"items", "minItems", "minLength", "$defs", "$ref", "oneOf"}` [VERIFIED:
schema_validate.py:23-26] — there is no `minimum`/`maximum` (or
`exclusiveMinimum`/`exclusiveMaximum`) keyword. `check_schema()` walks the
whole document and **raises `SchemaError` on any keyword outside that set**
[VERIFIED: schema_validate.py:42-51] — by design, a schema author cannot
silently sneak an unsupported keyword past it. D-06 names
`settings.out_of_range` as an example dotted error code (alongside
`settings.invalid_type`), but there is currently no schema keyword this
validator understands that expresses "a numeric value must fall within a
range" — which several settings this phase must ship inert keys for actually
need (a daily cap is a positive integer with a sane ceiling; a selection
weight is plausibly a 0.0–1.0 float; a port is 1–65535).
**Why it happens:** `schema_validate.py` was scoped in Phase 1 to exactly the
keywords `schemas/*.json` (item/session/response/report/lint_error) used —
none of those five documents needed a numeric range, so `minimum`/`maximum`
was never added.
**How to avoid:** Add `minimum` and `maximum` to `SUPPORTED`, and implement
them in `validate()` following the exact shape `minLength` already uses
[VERIFIED: schema_validate.py:162-165] — same additive-keyword, same
type-guarded (`isinstance(instance, (int, float))` excluding `bool`, matching
`_matches_type`'s existing bool-exclusion logic at schema_validate.py:76-78)
pattern already established. This is a small, in-spirit-consistent addition
(not a second validator, not a Draft 2020-12 reimplementation) that D-07 does
not currently cover, because D-07 assumes the validator already does everything
the settings schema needs.
**Warning signs:** Attempting to write the settings JSON Schema for
`daily_cap`/`selection_weights`/`daemon.port` and discovering there is no way
to express "must be ≥ 1" without either (a) a `SchemaError` at `check_schema()`
time, or (b) silently dropping the range constraint from the schema and
hand-writing a second range check outside `schema_validate.py` — which is
exactly the "second hand-written checker" D-07 exists to avoid.

## Code Examples

Verified patterns from the actual source read this session:

### The existing single-bank server pattern the daemon generalizes (`quiz.py`)
```python
# Source: surfaces/quiz.py:134-163 (verbatim structure, abbreviated)
class H(server.Handler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        self.send_html(page_bytes)

    def do_POST(self):
        if self.path != "/answer":
            self.send_error(404)
            return
        try:
            data = self.read_json()
            q = by_id.get(data.get("id"))
            ...
            payload = {"item_id": q["id"], "score": record(q, data.get("response"), elapsed_ms),
                       "explain": explain_payload(q, a.reveal)}
        except Exception as exc:
            self.send_error(500, str(exc))
            return
        self.send_json(payload)
```
This is D-01's literal precedent — the daemon's route table is this same
`if self.path == X: ...` shape generalized to a dict of patterns, with the
`by_id`/`page_bytes` closures replaced by the D-03 stem-allowlist lookup.

### The atomic-write pattern the settings file should reuse
```python
# Source: runtime.py:178-185 (verbatim)
def write_session(path, data):
    target = session_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)
```
`itembank.json` should be written the same way (tmp-then-`os.replace()`), so a
crash mid-write to the settings file cannot leave a truncated,
un-parseable `itembank.json` behind.

### The "no processing, print verbatim" precedent `config` should follow
```python
# Source: surfaces/protocol_cli.py:77-104 (structure, abbreviated)
def cmd_schema(a):
    if a.all:
        ...  # everything, one object
        return 0
    if a.name:
        ...  # one document verbatim
        return 0
    print("Published JSON contracts (schemas/*.json):\n")
    for name, summary in CONTRACTS:
        ...  # human summary table
    return 0
```

## State of the Art

Not meaningfully applicable — this phase touches no external library whose API
has changed over time. The one relevant "state of the art" note is internal to
this project: `schema_validate.py` and the dotted-lint-code convention
(`LINT_CODES`, `LintError`) are both less than 48 hours old in this codebase's
own history (Phase 1, this same milestone) — D-06/D-07 are extending a pattern
this project itself just finished establishing, not reaching for an older or
newer external one.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | Exact `itembank.json` field names (`daily_cap`, `selection_weights`, `auditor_autonomy`, `model_backend`, `update_policy`, `daemon.port`, `daemon.lan_default`) and their enum value spellings (`"opt_in"`/`"check_on_launch"`, `"report_only"`/`"draft_and_approve"`/`"audit_draft_lint_fix_commit"`, `"hosted"`/`"local"`) | Standard Stack, Architecture Patterns | Low — CONTEXT.md marks this explicitly as Claude's Discretion / "unconstrained implementation detail"; a later phase reading a differently-named key is an additive fix, not a breaking one, as long as the schema documents whatever names are chosen |
| A2 | The identifying marker for D-02's probe (`GET /__itembank__` returning `{"itembank": true}`) is a workable shape | Pattern 2 | Low — also explicitly Claude's Discretion per CONTEXT.md ("the identifying response the daemon's already-running probe expects back... unconstrained") |
| A3 | A default daemon port of `8730` (distinct from `serve`'s existing `8731` and `day`'s existing `8732` defaults) avoids collision if old and new commands run side by side during a transition period | Recommended Project Structure | Low — cosmetic; any unused port number works, this is just a suggestion to avoid confusing a learner running both an old `itembank serve` and the new daemon at once during rollout |
| A4 | Recommended daily-cap/selection-weight numeric bounds (daily cap ≥ 1; selection weight 0.0–1.0) are sensible placeholders for an *inert* key not yet read by any code this phase | Pitfall #6 | Low — these keys are explicitly inert until Phases 7/10 per CONTEXT.md; the owning phase can tighten or loosen the range later, this is scaffolding only |

**If this table is empty:** N/A — see above; all four assumptions are already
flagged in CONTEXT.md as within Claude's Discretion, so none of them need a
user confirmation checkpoint before planning proceeds. Every *architectural*
claim above (Pitfalls #1–6, the D-02/D-03/D-04 refinements) is `[VERIFIED]`
against the actual source files read this session, not `[ASSUMED]`.

## Open Questions

1. **Is a `/settings` HTML page actually required by this phase, or only the
   `itembank config` CLI command?**
   - What we know: D-01's route-table sketch lists `/settings` alongside
     `/quiz`, `/study`, `/report`, and the day view. PROJECT.md's own phrasing
     ("every capability reachable from both the app and the CLI") suggests
     eventually yes.
   - What's unclear: The phase's own four success criteria (as stated in the
     phase description this research was scoped against) only require `/`,
     `/quiz/<bank>`, `/study/<bank>`, `/report`, `/api/*`, and the day view for
     criterion 1, and only the CLI `config` command (no HTML route) for
     criterion 4. `/settings` does not appear in the success-criteria list at
     all, even though D-01 mentions it.
   - Recommendation: Treat a `/settings` HTML page as optional/stretch for this
     phase — DEL-05 and SURF-04 are fully satisfiable via `itembank config`
     alone, and theming/behavior behind these keys is explicitly Phase 4's job
     per CONTEXT.md's Phase Boundary. If the planner includes a `/settings`
     route anyway for completeness with D-01's sketch, scope it to read-only
     display of the current schema + values (mirroring `config`'s own output),
     not an editing UI — editing belongs to `itembank config set`, matching
     D-04's "not yet SURF-02" scoping for quiz/study.

2. **`/report` has no existing render function to call into.**
   - What we know: `/quiz/<stem>`, `/study/<stem>`, and the day view each have
     an existing HTML-rendering function this phase's route handlers can call
     straight into (`quiz.page_for()`, `study`'s template, `day.day_page()`).
     `/report` does not — today, `report` is exclusively a JSON-emitting CLI
     command (`session.py:cmd_report`, printing `session_summary()`) with no
     HTML shell anywhere in the codebase.
   - What's unclear: Whether `/report`'s HTML is meant to be a new,
     from-scratch page this phase writes (more effort than the strangler-fig
     "call the existing render function" pattern D-01 otherwise follows), or a
     minimal wrapper that just embeds the same JSON `/api/report` already
     returns with almost no styling.
   - Recommendation: Size `/report` as new work in the plan, not a migration
     of existing code — it is the one route in D-01's list without a
     strangler-fig precedent to strangle. A minimal page (a `<pre>` of the
     JSON, or a small table over `session_summary()`'s fields) satisfies the
     success criterion without requiring the richer trends/longitudinal view
     that is explicitly Phase 10's job.

3. **What happens when the configured port is occupied by something that is
   neither itembank nor a Windows-reserved range?**
   - What we know: D-02 covers "another itembank instance" (attach) and this
     research's Pattern 2 covers "OS-reserved range" (fall back to a free
     port, matching `server.bind()`'s existing behavior).
   - What's unclear: A third case — some unrelated local service already
     bound to the configured port (e.g., a leftover process from an unrelated
     project). CONTEXT.md does not explicitly resolve this case, and D-02's
     "no second daemon ever binds" framing does not obviously extend to "an
     unrelated process happens to be squatting the default port."
   - Recommendation: Treat this the same as the reserved-range case (fall back
     to `server.bind()`'s free-port logic, print the port chosen) rather than
     hard-failing startup — a learner should never be blocked from studying
     because an unrelated process happened to be on port 8730 that day. This
     keeps the "never block" spirit of the project's own network-degradation
     constraint. Flag for user confirmation only if the planner disagrees.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|-----------|
| Python (stdlib `http.server`/`socketserver`) | Daemon process | ✓ | 3.13.5 locally [VERIFIED: `python --version` this session]; CI pins 3.11 [VERIFIED: .github/workflows/ci.yml:10] | — |
| Git (for the existing `guard`/day-evidence checks) | Unaffected by this phase | Optional, already documented as graceful-degrade | — | Already handled: `day.py`'s `touched_today()` swallows any subprocess failure [VERIFIED: surfaces/day.py:404-420, `except Exception: return set()`] |
| AnkiConnect | day view only, unaffected by this phase | Optional, already documented as graceful-degrade | — | Already handled: `anki_read()` returns `(None, None)` on any failure [VERIFIED: surfaces/day.py:394-396] |

**Missing dependencies with no fallback:** none identified.
**Missing dependencies with fallback:** none newly introduced by this phase —
both optional dependencies above are pre-existing and already degrade
gracefully; this phase's daemon consolidation does not change their failure
behavior.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None — stdlib-only, subprocess-driven scripts following the `*_roundtrip.py` naming convention [VERIFIED: `.claude/CLAUDE.md` §Naming Patterns, "Test files use `*_roundtrip.py` pattern"] |
| Config file | none — CI runs every file under `tests/*.py` unconditionally [VERIFIED: .github/workflows/ci.yml, "for t in tests/*.py; do ... python \"$t\" || exit 1; done"] |
| Quick run command | `python tests/daemon_roundtrip.py` (new file, name at planner's discretion) |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` (already CI's own command, verified this session) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| SURF-01 | Daemon serves `/`, `/quiz/<bank>`, `/study/<bank>`, `/report`, `/api/*`, day view from one port | integration (spin daemon in a background thread, `urllib.request` each route) | `python tests/daemon_roundtrip.py` | ❌ Wave 0 |
| SURF-03 | Second daemon start attaches instead of binding a second port; `--lan` reachable on `0.0.0.0` | integration | `python tests/daemon_roundtrip.py` | ❌ Wave 0 |
| SURF-04 | Every route has a CLI equivalent reaching the same runtime call | integration (compare `/api/submit`'s recorded evidence event against `itembank submit`'s) | `python tests/daemon_roundtrip.py` (or extend `tests/agent_roundtrip.py`, which already drives the CLI session commands end-to-end [VERIFIED: tests/agent_roundtrip.py exists in `tests/`]) | ❌ Wave 0 (new assertions; existing CLI-side file already covers the CLI half) |
| DEL-04 | `itembank.json` holds all six PROJECT.md keys plus daemon settings, each typed/ranged/defaulted | unit | `python tests/config_roundtrip.py` (new file, name at planner's discretion) | ❌ Wave 0 |
| DEL-05 | `itembank config` prints schema like `spec`; invalid value rejected with a named (dotted) error | unit | `python tests/config_roundtrip.py` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** the specific `*_roundtrip.py` file(s) touched by that task
- **Per wave merge:** `for t in tests/*.py; do python "$t" || exit 1; done` (matches CI exactly)
- **Phase gate:** full suite green before `/gsd-verify-work`, matching every prior phase in this milestone

### Wave 0 Gaps

- [ ] `tests/daemon_roundtrip.py` — covers SURF-01/SURF-03/SURF-04; needs a
      background-thread server-start helper (`threading.Thread(target=srv.serve_forever)`),
      the exact pattern `tests/serve_roundtrip.py` and `tests/day_roundtrip.py`
      already use for their own single-purpose servers [VERIFIED: both files
      import `threading` and `urllib.request`]
- [ ] `tests/config_roundtrip.py` — covers DEL-04/DEL-05
- [ ] No shared fixture gap — `fixtures/sample_bank.md` and `fixtures/sample_plan.md`
      already exist and are reused by `serve_roundtrip.py`/`day_roundtrip.py`
      respectively; the daemon test can reuse both unmodified
- [ ] Framework install: none — stdlib only, nothing to install

## Security Domain

### Applicable ASVS Categories

(Level 1, per `.planning/config.json`'s `security_asvs_level: 1`)

| ASVS Category | Applies | Standard Control |
|-----------------|---------|--------------------|
| V2 Authentication | No | Explicitly out of scope by project design — "Users: One. No accounts, no auth" [VERIFIED: `.claude/CLAUDE.md` §Constraints]. `--lan` does **not** change this; it widens the trust boundary (see V4 below) without adding auth, which is an accepted, already-documented project risk, not a new one this phase introduces. |
| V3 Session Management | Partial | itembank "sessions" are assessment-progress files, not auth sessions — no cookie/token security model applies. The relevant control is **addressing**, covered under V4/V12 below. |
| V4 Access Control | **Yes** | D-03's stem-allowlist pattern (bank/plan paths never taken raw from a URL) must be extended to session identifiers and to the `bank` field recorded inside a session file — see Pitfall #5. This is the primary control this phase must get right. |
| V5 Input Validation | Yes | `schema_validate.py` (extended per Pitfall #6) for settings; existing `read_json()`/type-checking patterns (e.g. `quiz.py`'s `elapsed_ms` type guard [VERIFIED: surfaces/quiz.py:151-156]) for `/api/*` POST bodies |
| V6 Cryptography | No | No secrets, no auth tokens, no encryption surface introduced by this phase |
| V7 Error Handling and Logging | **Yes** | `SystemExit` must never escape a request handler and take down the shared daemon process — see Pitfall #3. This is a direct availability control specific to *consolidating* previously-isolated processes into one. |
| V12 Files and Resources | **Yes** | Same allowlist principle as V4, applied specifically to filesystem writes: `write_session()`'s `os.makedirs()`+write must only ever target a path this daemon itself resolved, never a client-supplied one — see Pitfall #5 |
| V13 API and Web Service | Yes | `/api/*` JSON body validation should match the rigor `quiz.py`'s existing `do_POST` already applies (type-check before use, `except Exception` around the call, now also `except SystemExit` per Pitfall #3) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Path traversal / arbitrary file read via a client-supplied `session` or `bank` value in `/api/*` | Tampering, Information Disclosure | Address by opaque `session_id`/bank stem through a server-built allowlist, never a raw path — Pitfall #5 |
| Arbitrary file/directory *write* via `write_session()`'s `os.makedirs(os.path.dirname(target))` on an unvalidated path | Tampering | Same allowlist fix as above — the write path is derived from the same value the read path is |
| One malformed request crashing the shared daemon (`SystemExit` escaping a handler) | Denial of Service | `except SystemExit` around every reused `cmd_*`-style call site — Pitfall #3 |
| `--lan` widening the trust boundary from "this machine" to "anyone on this wifi" without any corresponding tightening of path/session validation | Elevation of Privilege (of an untrusted network peer to arbitrary local file access) | The V4/V12 allowlist fix above is what actually closes this — `--lan` itself is an accepted, already-documented project decision (SURF-03 requires it to work), not something to remove or gate further |
| Malformed/oversized JSON POST body to `/api/*` | Denial of Service (resource exhaustion), Tampering | Existing `read_json()` already bounds by `Content-Length` [VERIFIED: server.py:21-23]; no new work needed here beyond the type-guard pattern `quiz.py` already demonstrates |

## Sources

### Primary (HIGH confidence — read directly this session)
- `server.py` — `Handler` base class, `bind()` port-fallback primitive
- `surfaces/quiz.py` — `page_for()`, `cmd_build()`, `cmd_serve()`, the existing single-bank `Handler` subclass and POST route
- `surfaces/quiz_page.py` — the embedded quiz-page template, its hardcoded `/answer` POST target
- `surfaces/day.py` — `parse_plan()`, `parse_lanes()`, `lane_files()`/`resolve_notes()` (the existing allowlist precedent), `anki_read()`, `cmd_day()`'s `Handler` subclass
- `surfaces/study.py` — `STUDY_TEMPLATE`, confirming no server-side POST exists for the study surface today
- `surfaces/session.py` — `cmd_start/next/submit/report`, and their `sys.exit()` call sites
- `surfaces/cli.py` — full `argparse` subcommand registration, confirming today's `serve`/`day`/`study`/`start`/`next`/`submit`/`report` default ports and flags
- `runtime.py` — `session_path()`, `read_session()`/`write_session()`/`upgrade_session()` and their `sys.exit()` call sites, `session_view()`/`session_summary()`
- `model.py` — `parse_bank()`'s graceful-empty-list behavior, `LintError`/`LINT_CODES` (the dotted-code precedent D-06 extends)
- `schema_validate.py` — the full `SUPPORTED` keyword set, `check_schema()`'s unsupported-keyword rejection, `validate()`'s per-keyword implementation (confirming the `minimum`/`maximum` gap)
- `surfaces/protocol_cli.py` — `cmd_schema()`, the existing "print the contract verbatim" precedent D-06 mirrors
- `.planning/research/ARCHITECTURE.md` — the pre-roadmap architecture sketch D-01/D-05 cite directly
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/INTEGRATIONS.md` — codebase-map documents CONTEXT.md's canonical_refs point to (see note below on a discrepancy found)
- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — D-16 (dotted lint codes) and D-17 (idempotency key) precedents D-06/D-07 build on
- `.claude/CLAUDE.md` — project constraints (stdlib-only, single-user, no accounts)
- `.planning/config.json` — `nyquist_validation: true`, `security_enforcement: true`, `security_asvs_level: 1` (governing which optional RESEARCH.md sections are required)
- `.github/workflows/ci.yml` — the actual test-invocation and lint/build CI steps

### Secondary (MEDIUM confidence)
- [Python docs: `http.server`](https://docs.python.org/3/library/http.server.html) — confirms `BaseHTTPRequestHandler`/`self.path` dispatch as the stdlib-correct primitive
- [Python docs: `socketserver`](https://docs.python.org/3/library/socketserver.html) — confirms `ThreadingMixIn` as the stdlib concurrency mechanism (no new dependency)

### Tertiary (LOW confidence / noted discrepancy)
- `.planning/codebase/INTEGRATIONS.md` states the existing webhook endpoints as `POST /submit` (quiz) and `POST /action` (day) [see INTEGRATIONS.md §Webhooks & Callbacks]. Reading the actual source this session found this is **stale**: the real endpoints are `POST /answer` (quiz, `surfaces/quiz.py:142`) and `POST /save` / `POST /open` (day, `surfaces/day.py:887`) — three endpoints, not two, and none named as INTEGRATIONS.md states. This document is one of CONTEXT.md's own canonical_refs; the planner should not trust its exact endpoint names and should confirm against the source files listed above instead. Worth a follow-up doc refresh outside this phase's scope.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no external library introduced; every module cited is already imported somewhere in this exact codebase
- Architecture: HIGH — every pattern and pitfall above is grounded in a specific file/line read this session, not inferred from the pre-roadmap architecture sketch alone
- Pitfalls: HIGH — six pitfalls found by direct code reading, two (Pitfall #3, #5) materially refine CONTEXT.md's own D-04 in a way CONTEXT.md explicitly invited flagging for

**Research date:** 2026-08-07
**Valid until:** No external dependency to go stale against; re-validate only if `server.py`, `runtime.py`, or `schema_validate.py` change materially before this phase is planned/executed.
