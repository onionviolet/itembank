# Phase 2: Daemon Consolidation & Settings Foundation - Pattern Map

**Mapped:** 2026-08-07
**Files analyzed:** 10 (new/modified)
**Analogs found:** 10 / 10

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `surfaces/daemon.py` (NEW) | controller (HTTP route table) | request-response | `surfaces/day.py:cmd_day`'s `class H(server.Handler)` (lines 878-927) + `surfaces/quiz.py:cmd_serve`'s `class H(server.Handler)` (lines 134-163) | role-match (generalizing two single-route handlers into one) |
| `surfaces/daemon.py::probe()`/`start()` (detect-and-attach) | utility (network probe) | request-response | `surfaces/day.py:anki_read()`'s short-timeout local HTTP GET (line ~371-396) + `server.py:bind()` (lines 40-52) | role-match |
| `surfaces/daemon.py::_scan()` (stem allowlist) | utility (filesystem scan → dict) | batch | `surfaces/day.py:lane_files()` (line 246) + `model.parse_bank()`'s graceful-empty-list classification (used at `cmd_guard`) | exact (same "resolve identifier server-side, never trust client path" principle) |
| `surfaces/daemon.py` GET `/`  (index page) | component (server-rendered HTML) | request-response | `surfaces/quiz.py:page_for()` (lines 18-33) — `__THEME__`/`__TITLE__`/`__DATA__` substitution pattern | role-match (new template, same substitution convention) |
| `surfaces/daemon.py` GET `/report` (new HTML) | component (server-rendered HTML) | request-response | `surfaces/session.py:cmd_report()` (lines 122-127) for data shape; `surfaces/quiz.py:page_for()` for template-substitution shape | partial (no existing HTML render fn — sized as new work) |
| `surfaces/daemon.py` `/api/start`,`/api/next`,`/api/submit`,`/api/report` | controller (JSON API, thin wrapper) | request-response | `surfaces/session.py:cmd_start/cmd_next/cmd_submit/cmd_report` (lines 37-127) | exact (same runtime calls, wrapped for `SystemExit`) |
| `surfaces/settings.py` (NEW, name at planner's discretion) | service + controller (`cmd_config`) | CRUD (read/validate/write one file) | `surfaces/protocol_cli.py:cmd_schema()` (lines 77-104) for command shape; `runtime.py:write_session()` (lines 178-185) for atomic write | exact |
| `schemas/settings.schema.json` (NEW) | config (JSON Schema document) | — | `schemas/*.json` (e.g. `schemas/session.schema.json`) — same document shape `protocol_cli.py:CONTRACTS` enumerates | exact |
| `itembank.json` (NEW, generated) | config (data file) | file-I/O | `_attempts/session_*.json` written by `runtime.write_session()` | role-match (same atomic tmp-then-rename convention) |
| `schema_validate.py` (MODIFIED — add `minimum`/`maximum`) | utility (validator) | transform | `schema_validate.py:validate()`'s existing `minLength` keyword handling (lines 162-165) | exact (same file, same pattern extended) |
| `surfaces/cli.py` (MODIFIED — add `daemon`, `config` subcommands) | route (argparse registration) | request-response | `surfaces/cli.py`'s existing `sub.add_parser("schema", ...)` / `sub.add_parser("serve", ...)` blocks (lines 104-135, 262-268) | exact |
| `model.py` (reference only — dotted error code precedent) | utility (validation → error code) | transform | `model.py:LintError`/`LINT_CODES` (lines 373-400) | exact (D-06 explicitly extends this convention) |

## Pattern Assignments

### `surfaces/daemon.py` — GET route dispatch (controller, request-response)

**Analog:** `surfaces/quiz.py:cmd_serve` (lines 134-163) and `surfaces/day.py:cmd_day` (lines 878-927)

**Imports pattern** (from `surfaces/quiz.py` lines 1-15):
```python
import collections, html, json, os, sys, uuid

import evidence
import server
from model import grab, lint, load
from runtime import explain_payload, page_item, score_response
from surfaces.quiz_page import TEMPLATE
from surfaces.theme import THEME_CSS
```
`daemon.py` should follow the same shape: stdlib imports first, then `evidence`/`server`/`model`/`runtime`, then the surface render functions it dispatches into (`surfaces.quiz`, `surfaces.study`, `surfaces.day`, `surfaces.session`, the new `surfaces.settings`).

**Single-Handler-subclass-with-`self.path`-dispatch pattern** (from `surfaces/quiz.py` lines 134-163, generalize the `if self.path != X` shape into a route table):
```python
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
            ...
        except Exception as exc:                # never let a bad POST kill a sitting
            self.send_error(500, str(exc))
            return
        self.send_json(payload)
```
Generalize to: `ROUTES = {("GET", "/"): handle_index, ("GET", r"/quiz/<stem>"): handle_quiz_get, ...}` with `do_GET`/`do_POST` doing pattern match + dispatch, never HTML generation inline.

**Stem/path-never-from-client allowlist precedent** (from `surfaces/day.py` lines 892-901):
```python
if self.path == "/open":
    # Only paths this server itself resolved are openable; a
    # client names a lane and an index, never a path.
    files = (cache["info"] or {}).get("lanes", {}) \
        .get(data.get("lane"), {}).get("files", [])
    i = int(data.get("i") or 0)
    if not (0 <= i < len(files)):
        self.send_error(404)
        return
```
D-03's stem allowlist and D-04/Pitfall #5's session_id allowlist must both follow this exact shape: client sends an opaque identifier, server resolves it against a dict built at startup/request time, never a raw path.

**Server bind + browser-open pattern** (from `surfaces/day.py` lines 828-833, 957 and `surfaces/quiz.py` lines 165-177):
```python
print("itembank serve")
srv = server.bind(H, a.port)
with srv:
    url = "http://127.0.0.1:%d/" % srv.server_address[1]
    ...
    if not a.no_open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        ...
```
`daemon.py`'s `cmd_daemon`/`start()` extends this with the detect-and-attach probe (see Shared Patterns below) before calling `server.bind()`.

---

### `surfaces/daemon.py` — `/api/*` routes (controller, request-response, JSON)

**Analog:** `surfaces/session.py:cmd_start/cmd_next/cmd_submit/cmd_report` (lines 37-127)

**Core pattern to wrap, verbatim** (from `surfaces/session.py` lines 76-119, `cmd_submit`):
```python
def cmd_submit(a):
    data = read_session(a.session)
    if data["status"] != "active":
        sys.exit("session is already complete")
    qs = load(data["bank"])
    ...
    score = score_response(q, answer)
    ...
    evidence_result = evidence.append_event(log, event)
    ...
    write_session(a.session, data)
    result = {"accepted": True, "item_id": q["id"], "score": score,
              "status": data["status"], "evidence": evidence_result,
              "next": session_view(data, qs)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
```
The daemon's `/api/submit` route handler must call the *same body* (factor `cmd_submit`'s logic into a shared function `session.do_submit(session_path, answer, confidence)` if needed, or call `cmd_submit`-equivalent code directly), and never reimplement scoring/evidence-append inline — this is the literal "no second scoring path" anti-pattern the codebase's own `ARCHITECTURE.md` already documents.

**Error handling addition required** (RESEARCH.md Pitfall #3 — `sys.exit()`/`SystemExit` does not subclass `Exception`):
```python
# surfaces/daemon.py — POST /api/submit
def handle_api_submit(self, body):
    session_path_resolved = self.sessions.get(body.get("session_id"))   # allowlist, not raw path
    if session_path_resolved is None:
        self.send_error(404, "unknown session_id")
        return
    try:
        result = session.do_submit(session_path_resolved, body.get("answer"), body.get("confidence"))
    except SystemExit as exc:
        self.send_error(400, str(exc.code))
        return
    except Exception as exc:
        self.send_error(500, str(exc))
        return
    self.send_json(result)
```
Both `except SystemExit` and `except Exception` are required (`quiz.py`'s existing POST handler at line 160 only has `except Exception`, which is insufficient once `session.py`'s `sys.exit()`-calling functions are reused inside a shared long-lived process).

---

### `surfaces/settings.py` (NEW) — `cmd_config` (service + controller, CRUD)

**Analog:** `surfaces/protocol_cli.py:cmd_schema()` (lines 69-104)

**"No processing, print verbatim" three-tier command shape** (from `surfaces/protocol_cli.py` lines 77-104):
```python
def cmd_schema(a):
    if a.all:
        contracts = dict((name, json.loads(_load_schema_text(name))) for name in CONTRACT_NAMES)
        payload = {"schema_version": 1, "spec": SPEC, "contracts": contracts,
                   "commands": [dict(c) for c in COMMANDS]}
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if a.name:
        if a.name not in CONTRACT_NAMES:
            sys.exit("unknown contract %r; valid names: %s" % (a.name, ", ".join(CONTRACT_NAMES)))
        print(_load_schema_text(a.name), end="")
        return 0
    print("Published JSON contracts (schemas/*.json):\n")
    for name, summary in CONTRACTS:
        doc = json.loads(_load_schema_text(name))
        print("  %-12s v%-3d  %s" % (name, doc["x-itembank-version"], summary))
    return 0
```
`cmd_config(a)` mirrors this exactly: no-args → human summary table (mirrors the `for name, summary in CONTRACTS` loop); `config schema` → raw JSON Schema document verbatim (mirrors `a.name` branch, `print(text, end="")`); `config set KEY VALUE` → validate-then-write (new branch, not in `cmd_schema`, see below).

**Path resolution constant pattern** (from `surfaces/protocol_cli.py` lines 20-21):
```python
SCHEMA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schemas")
```
`settings.py` should locate `schemas/settings.schema.json` the identical way, and `itembank.json` beside `lanes.md` at repo root per CONTEXT.md D-05.

**Atomic write pattern** (from `runtime.py` lines 178-185, verbatim):
```python
def write_session(path, data):
    target = session_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)
```
`_write_settings(settings)` in `settings.py` must reuse this exact tmp-then-`os.replace()` shape so a crash mid-write cannot leave a truncated `itembank.json`.

**Dotted error code classification** (analog: `model.py:LintError`/`LINT_CODES`, lines 373-400):
```python
class LintError(collections.namedtuple("LintError", "code field item message")):
    """`code` is a dotted API namespace an authoring agent branches on (D-16) —
    adding a code is additive, renaming one is a breaking change for every consumer."""
    __slots__ = ()
    def __str__(self):
        return "%s: %s" % (self.item, self.message)

LINT_CODES = tuple(sorted({
    "item.duplicate_number", "item.select_mismatch", ...
}))
```
`settings.py` should define an analogous `SETTINGS_CODES` tuple (`settings.invalid_type`, `settings.invalid_value`, `settings.out_of_range`, `settings.unknown_key`) and a small classifier function over `schema_validate.validate()`'s returned plain-string errors (keyword-pattern match: `"expected type"` → `settings.invalid_type`; `"is not one of"` → `settings.invalid_value`; `"less than minimum"`/`"greater than maximum"` → `settings.out_of_range`), per RESEARCH.md's "Don't Hand-Roll" table — this keeps `schema_validate.py`'s return contract (list of plain strings) unchanged for its existing CI callers.

---

### `schema_validate.py` — add `minimum`/`maximum` keywords (utility, transform)

**Analog:** the file's own existing `minLength` implementation (lines 162-165), to be copied for numeric bounds:
```python
if "minLength" in schema and isinstance(instance, str):
    if len(instance) < schema["minLength"]:
        errors.append("%s: has length %d, shorter than minLength %d" %
                      (path, len(instance), schema["minLength"]))
```
Add, following the identical shape and the existing bool-exclusion guard at `_matches_type` (lines 71-78):
```python
if "minimum" in schema and isinstance(instance, (int, float)) and not isinstance(instance, bool):
    if instance < schema["minimum"]:
        errors.append("%s: %r is less than minimum %r" % (path, instance, schema["minimum"]))
if "maximum" in schema and isinstance(instance, (int, float)) and not isinstance(instance, bool):
    if instance > schema["maximum"]:
        errors.append("%s: %r is greater than maximum %r" % (path, instance, schema["maximum"]))
```
And add `"minimum", "maximum"` to the `SUPPORTED` frozenset (line 23-26) — `check_schema()` rejects any keyword outside `SUPPORTED`, so omitting this raises `SchemaError` the moment `schemas/settings.schema.json` is written with a range constraint.

---

### `surfaces/cli.py` — new `daemon` and `config` subcommands (route, request-response)

**Analog:** the existing `schema`/`serve` subparser registration blocks (lines 104-135, 262-268):
```python
s = sub.add_parser("schema", help="print the published JSON contracts the way "
                                    "`spec` prints the format contract")
s.add_argument("name", nargs="?", ...)
s.add_argument("--all", action="store_true")
s.set_defaults(fn=cmd_schema)

s = sub.add_parser("serve", help="sit the quiz with every answer written to disk")
s.add_argument("bank")
s.add_argument("--port", type=int, default=8731)
...
s.set_defaults(fn=cmd_serve)
```
`daemon`/`config` subparsers follow this identical shape — `daemon <dir>` (or explicit bank/plan paths) with `--port`/`--lan`, `config [schema|set KEY VALUE]` mirroring `schema`'s `name`/`--all` args plus a new `set` sub-action.

---

## Shared Patterns

### Loopback HTTP handler base
**Source:** `server.py:Handler` (lines 15-37) and `server.py:bind()` (lines 40-52)
**Apply to:** `surfaces/daemon.py`'s single `Handler` subclass
```python
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
    def send_html(self, body):
        self.send_bytes(body, "text/html; charset=utf-8")
    def send_json(self, payload):
        self.send_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8")

def bind(handler, port, host="127.0.0.1"):
    try:
        return socketserver.TCPServer((host, port), handler)
    except OSError as exc:
        print("  port %d unavailable (%s), using a free one instead"
              % (port, exc.__class__.__name__))
        return socketserver.TCPServer((host, 0), handler)
```
`daemon.py` reuses `server.Handler` and `server.bind()` unmodified for the fallback path; D-02's detect-and-attach probe layers on top rather than replacing this.

### Short-timeout local network probe (for D-02's detect-and-attach)
**Source:** `surfaces/day.py:anki_read()` (~lines 371-396) — same "local HTTP GET, short timeout, treat any failure as absence" shape
**Apply to:** `daemon.py`'s `probe(port)` function
```python
try:
    with urllib.request.urlopen(url, timeout=2) as r:
        ...
except Exception:
    return None, None   # AnkiConnect unreachable degrades to a null, never a crash
```
D-02's probe should degrade identically: any exception (timeout, connection refused, non-JSON) means "not us," never "assume us."

### Evidence writer (unchanged, called by `/api/*` routes)
**Source:** `evidence.append_event()`, called identically in `surfaces/quiz.py:record()` (line 114), `surfaces/session.py:cmd_submit` (line 98), `surfaces/day.py:do_POST` (lines 915-926)
**Apply to:** `/api/submit`'s daemon route — must call the exact same `evidence.append_event(log, event)` path, never a second writer.

### Bank/session loading — the one loader
**Source:** `model.load()`, called by every existing surface
**Apply to:** Every daemon route that needs bank contents — `daemon.py` never re-implements `model.parse_bank()`/`model.load()`.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `GET /report` HTML body (populated case: session with mix of correct/incorrect/pending) | component | request-response | No existing HTML render function produces this shape — `session.py:cmd_report()` only emits JSON via `session_summary()`. RESEARCH.md's own Open Question 2 flags this as new work, not a migration. Use `session_summary()`'s field list (bank, status, per-objective breakdown) as the data contract and `quiz.page_for()`'s `__THEME__`/template-substitution convention as the only structural precedent to reuse. |
| `GET /` index page body | component | request-response | No existing page lists multiple banks/day-plans — every existing surface serves exactly one bank or one plan per process. Build from `quiz.page_for()`'s substitution convention (imports `THEME_CSS`, `__TITLE__`/`__THEME__` replace) plus the Copywriting Contract in 02-UI-SPEC.md for exact strings. |

## Metadata

**Analog search scope:** `server.py`, `surfaces/quiz.py`, `surfaces/quiz_page.py`, `surfaces/day.py`, `surfaces/study.py`, `surfaces/session.py`, `surfaces/cli.py`, `surfaces/protocol_cli.py`, `runtime.py`, `model.py`, `schema_validate.py`
**Files scanned:** 11
**Pattern extraction date:** 2026-08-07
