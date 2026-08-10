# Phase 10: Retention, Pacing & Trends - Pattern Map

**Mapped:** 2026-08-10
**Files analyzed:** 24 (9 new, 15 modified, derived from `10-CONTEXT.md` D-01..D-24 + `10-RESEARCH.md` file list + the existing 10-01..06-PLAN.md `files_modified` inventories)
**Analogs found:** 23 / 24 (1 no-analog)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `retention.py` (new) | service / derivation | transform (append-only evidence replay) | `evidence.py` `objective_history:614`, `day_log_from_events:1463`, `rebuild_index:768` + `runtime.py:230` `glossable()` | role-match (no existing derivation module; `evidence.py` is its peer) |
| `surfaces/retention_view.py` (new) | component / surface | request-response | `surfaces/daemon.py:321` `handle_report_get` + `surfaces/evidence_cli.py:35` `cmd_evidence` | role-match |
| `schemas/report.schema.json` (modified) | config / contract | validation | itself (existing two-shape `oneOf`) + `schemas/response.schema.json` `$defs` | exact |
| `tests/retention_roundtrip.py` (new) | test | transform / event-driven | `tests/due_roundtrip.py` + `tests/evidence_roundtrip.py` fail() style | exact |
| `tests/pacing_roundtrip.py` (new) | test | request-response | `tests/day_roundtrip.py` (server + round-trip) | exact |
| `tests/lesson_retention_roundtrip.py` (new) | test | event-driven | `tests/lesson_roundtrip.py` (lesson parse) + `tests/due_roundtrip.py` | role-match |
| `tests/selection_retention_roundtrip.py` (new) | test | transform | `tests/due_roundtrip.py:113-139` hand-checked math style | role-match |
| `tests/retention_ui_roundtrip.py` (new) | test | request-response | `tests/day_roundtrip.py:59-95` `check_server()` + `tests/daemon_roundtrip.py` | exact |
| `tests/phase10_uat.py` (new) | test | request-response | `tests/agent_roundtrip.py` (CLI UAT harness) | role-match |
| `fixtures/lesson_retention_events.jsonl` (new) | fixture | event-driven | `fixtures/_evidence/evidence.jsonl` (recorded-event corpus) | exact |
| `evidence.py` (modified) | model / event schema | event-driven | itself: `KNOWN_EVENT_TYPES:43`, `day_tick_event:1351`, `term_lookup_event:1393`, `key_review_event:1435`, `day_log_from_events:1463` | exact |
| `surfaces/day.py` (modified) | controller / surface | request-response | itself: `day_state:1191`, `day_render:1230`, `apply_day_post:1289`, `anki_read:372` | exact |
| `surfaces/session.py` (modified) | controller / CLI | request-response | itself: `do_start:54` / `cmd_start:87` split; evidence append in `do_submit:111` | exact |
| `surfaces/daemon.py` (modified) | route / controller | request-response | itself: `API_ROUTES:70`, `ROUTES:84`, `ROUTE_CLI:109`, `api_read_json:1117`, `handle_api_report:1342` | exact |
| `surfaces/cli.py` (modified) | route / config | request-response | itself: import block `:7-21`, `main()` sub_parser registration | exact |
| `surfaces/evidence_cli.py` (modified) | controller / CLI | request-response | itself: `cmd_evidence:35`, `cmd_render:129`, `cmd_mark:253` | exact |
| `surfaces/protocol_cli.py` (modified) | controller / CLI | request-response | itself: `CONTRACTS:16-29`, `cmd_schema:58` | exact |
| `surfaces/lesson.py` (modified) | controller / CLI | request-response | itself: `record_key_review:1088`, `cmd_key_review:1105` | exact |
| `schemas/settings.schema.json` (modified) | config / contract | validation | itself: `daily_cap:91-96`, `selection_weights:98-131` | exact |
| `schemas/response.schema.json` (modified) | config / contract | validation | itself: `event_type` enum `:24-29`, `$defs` per event type `:131+` | exact |
| `schemas/session.schema.json` (modified) | config / contract | validation | itself | exact |
| `selection.py` (modified) | service / pure selector | request-response | none in tree (Phase 7 unexecuted); contract from `07-06-PLAN.md` + research RESOLVED lock | no analog |
| `itembank.json` (modified) | config | validation | itself (shipped settings defaults) | exact |
| existing tests `config_roundtrip.py`, `protocol_roundtrip.py`, `selection_roundtrip.py`, `day_roundtrip.py`, `daemon_roundtrip.py` (modified) | test | request-response | themselves (add the new command/route parity checks) | exact |

## Pattern Assignments

### `retention.py` (service/derivation, transform)

**Analog 1:** `evidence.py` - the peer module for reading the append-only log into disposable derived views. The module docstring (evidence.py:1-12) states the tier rule Phase 10 inherits:

```python
"""The evidence log: the one append-only store every later plan writes into and reads from.
...
`evidence.py` is to the evidence store what `runtime.score_response` is to scoring: the
single primitive every surface calls, so no surface reimplements its own append or its
own read. The log is the only authority (D-08) — a derived index is a disposable
materialized view over it, never a second source of truth."""
```

**Core pattern - capture once, derive many** (RESEARCH.md "Pattern 1"): one snapshot per render, passed immutably to every derived function. The existing shape to copy is `objective_history()`'s docstring contract (evidence.py:614-627):

```python
def objective_history(log, objective, prefix=False, subject=None, mode=None,
                       session_id=None, since=None):
    """Every LIVE response event matching the given filters, oldest first,
    sorted by `(ts, log order)` ... Never recomputes a score -- reads the
    recorded `score` field."""
```

**Derivation shape** - `day_log_from_events` (evidence.py:1463-1482) is the smallest existing example of "project the log into a derived mapping, live events only":

```python
def day_log_from_events(log):
    """The `{iso_date: set_of_lanes}` mapping ... built from the live `day_tick`
    events ... Un-ticking a lane is a retraction of its tick event (D-10):
    reading through `live_events` means a retracted tick simply is not present."""
    out = {}
    for ev in live_events(log):
        if ev.get("event_type") != DAY_TICK_EVENT_TYPE:
            continue
        date, lane = ev.get("date"), ev.get("lane")
        if not date or not lane:
            continue
        out.setdefault(date, set()).add(lane)
    return out
```

`retention.py`'s objective summaries/weights/cap decisions are the same projection at higher granularity: `live_events(log)` -> filter by event type/objective -> accumulate -> return plain dicts. Keep it a pure module: no I/O, no imports from `surfaces/` (evidence.py:1483+ `render_daily_log` takes lanes/status as parameters explicitly so the runtime tier never imports a surface).

**Disposable-cache precedent** - if retention adds a cache, copy the disposable sqlite projection discipline (evidence.py:691-698, `rebuild_index:768-797`): version the projection's OWN shape (`INDEX_VERSION`), rebuild via tmp-then-`os.replace`, and prove cache equality in tests (`test_index_is_disposable`). RESEARCH.md D-02 makes caches optional and never authoritative.

**Conservative gate precedent** - `runtime.py:230` `glossable()`: "deliberately conservative -- on any ambiguity it returns False. It is a pure function: no I/O, no side effects, deterministic across calls." Apply the same posture to D-03's first-class `unknown` and D-14's at-risk flag (never a predicted failure).

---

### `evidence.py` (model/event schema, event-driven) - new event types

**Analog:** itself. New Phase 10 event types (`lesson_complete` per 10-02, cap `override` per 10-04) copy the existing event-builder shape exactly.

**Event registry** (evidence.py:43): add the new types to the tuple; `events()` skips-and-warns on anything outside it, so this is the one registration point:

```python
KNOWN_EVENT_TYPES = ("response", "retraction", "mark", "day_tick",
                     "term_lookup", "key_review")
```

**Builder shape** - `day_tick_event` (evidence.py:1351-1388) is the template: validate inputs with `ValueError` before building, hash the identity fields into `dedupe_key`, and include `schema_version`/`event_id`/`event_type`/`ts`:

```python
def day_tick_event(date, lane, source="day"):
    if not isinstance(date, str) or not _DAY_DATE_RE.match(date):
        raise ValueError(...)
    ...
    raw = "%s|%s" % (date, lane)
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": new_event_id(),
        "event_type": DAY_TICK_EVENT_TYPE,
        "ts": utc_now(),
        "date": date,
        "lane": lane,
        "source": source,
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }
```

**No-score structural rule** - `term_lookup_event` (evidence.py:1393-1431) and `key_review_event` (evidence.py:1435-1462) carry NO `score` key at all. Phase 10's `lesson_complete`/`override` events follow the same rule (they are not responses). `key_review_event`'s docstring already names the Phase 10 consumer: "Phase 10 replays these events into scheduler state."

**One writer** (evidence.py:399-418): every new event goes through `append_event`, never `append_line`/`append_line_checked` directly.

**Accepted-marks-only replay** - `marks_by_event` (evidence.py:1117-1140) is the D-16/D-22 seam: "the most recent LIVE `mark` event for every response `event_id`" - scheduler mastery reads through this (accepted marks only), never through pending `None` scores.

---

### `surfaces/day.py` (controller/surface, request-response)

**Analog:** itself. Phase 10 changes `day` into the snapshot renderer + cap gate; the per-plan `state` dict and `apply_day_post` body are the patterns to extend.

**Imports pattern** (day.py:1-10):
```python
import html, json, os, re, sys

import evidence
from surfaces import presentation, settings
from surfaces.theme import theme_css
```

**Per-render state** - `day_state` (day.py:1191-1229) builds one mutable dict per served plan, resolving the evidence log path and rebuilding the tick log from events; Phase 10 adds the snapshot marker and cap decision to this same dict:

```python
evidence_log = evidence.log_path(os.path.dirname(os.path.abspath(log_path)) or ".")
if os.path.exists(evidence_log):
    log = evidence.day_log_from_events(evidence_log)
else:
    print("note: no _evidence/evidence.jsonl found yet; reading ticks straight "
          "from %s. ..." % log_path)
    log = load_day_log(log_path)
```

**Render + cache** - `day_render` (day.py:1230-1258): a 60-second `day_info` cache, then `settings.load_settings(...)`, `theme_css(cfg)`, the document snapshot, and one `day_page(...)` call - the CLI and daemon share it. Phase 10's one-snapshot-per-render rule extends this: capture live events + snapshot metadata once, derive all claims from it.

**Write path** - `apply_day_post` (day.py:1289-1356): a tick is an append of `day_tick_event`, an un-tick is `retraction_event`, then the log mapping is rebuilt from `day_log_from_events` and `daily_log.md` is rewritten through `render_daily_log` + tmp-then-`os.replace`. The cap gate (D-07/D-08) plugs into the `save` branch: count live response events for the local day/subject first, block ordinary starts when at cap, and record the explicit one-sitting override as a new event type - never a persisted setting (research Pitfall 3).

**Anki degradation** - `anki_read` (day.py:372-404) returns `(None, None)` when Anki is closed; keep the two labeled, unsummed signals (D-05/SCHED-03) and omit on failure:

```python
for url in urls:
    try:
        names = _anki_post(url, "deckNames")
        ...
        return counts, names
    except Exception:
        continue
return None, None
```

---

### `surfaces/session.py` (controller/CLI, request-response)

**Analog:** itself. The `do_*`/`cmd_*` split (docstring, session.py:1-23) is the pattern Phase 10 keeps for the start gate: `do_*` computes and returns a dict and may raise `SystemExit` on routine errors; `cmd_*` unpacks argparse, prints JSON, returns 0; the daemon contains the `SystemExit`.

**Start gate shape** - `do_start` (session.py:54-84) already guards input before any work:

```python
if not isinstance(count, int) or isinstance(count, bool) or count < 1:
    sys.exit("count must be a positive integer, got %r" % (count,))
qs = load(bank_path)
errors, _ = lint(qs)
if errors and not force:
    sys.exit("refusing to start a bank with errors; run lint or pass --force")
```

Phase 10 (10-04) adds the per-subject cap check before `do_start` selects items, with the same fail-fast `sys.exit` style, and the explicit override argument that appends the override event.

**Evidence append discipline** - `do_submit` (session.py:111-154): compute the event via `evidence.response_event(...)`, append via `evidence.append_event(log, event)`, and branch on `evidence_result["status"] == "recorded"` so a crash-retry never double-counts. The Phase 10 override/`lesson_complete` writers follow the same "check the append result" shape.

---

### `surfaces/daemon.py` (route/controller, request-response)

**Analog:** itself. New `/api/*` report/start routes and the retention report page register in all three tables.

**Route tables** - `API_ROUTES` (daemon.py:70-82), `ROUTES` (daemon.py:84-107), and `ROUTE_CLI` (daemon.py:109-131). Every new route must appear in all three; the key set of `ROUTE_CLI` is asserted equal to `ROUTES` by `tests/daemon_roundtrip.py`, so a route added without a CLI twin fails the build:

```python
API_ROUTES = (
    ("POST", "/api/start", "handle_api_start"),
    ...
    ("POST", "/api/report", "handle_api_report"),
)
ROUTES = ( ... ) + API_ROUTES + ( ... )
ROUTE_CLI = {
    ("POST", "/api/report"): "report",
    ...
}
```

**API body guard** - `api_read_json` (daemon.py:1117-1142) + `api_reject_path_fields` (daemon.py:1109-1116): client bodies are objects, never paths; `API_FORBIDDEN_FIELDS` (daemon.py:1070-1073) rejection stays. New report/override routes copy this verbatim.

**Handler error containment** - `handle_api_report` (daemon.py:1342-1364) is the template: cross-origin reject, `api_read_json`, resolve `session_id` through `api_session_path` (daemon.py:1143-1153 - a dict-key allowlist, never a path join), then catch `SystemExit` -> 400 and `Exception` -> `send_server_error` (path-free 500, daemon.py:1380-1390).

**Report page render** - `handle_report_get` (daemon.py:321-371): the page is rendered from exactly the dict the CLI command returns ("the page and the command can never disagree"), wrapped in `presentation.surface_shell(...)` with `theme_css(settings.load_settings(handler.root))`. `surfaces/retention_view.py` is the same pattern for the longitudinal report.

---

### `surfaces/retention_view.py` (component/surface, request-response)

**Analog 1:** `surfaces/daemon.py:321` `handle_report_get` - surface-neutral payload -> one HTML page via `presentation.surface_shell` (presentation.py:168-185):

```python
page = presentation.surface_shell(
    "itembank report", body, theme_css=theme_block,
    back={"href": "/", "label": "itembank"})
handler.send_html(page.encode("utf-8"))
```

**Analog 2:** `surfaces/evidence_cli.py:35` `cmd_evidence` - the CLI twin prints `json.dumps(result, ensure_ascii=False, indent=2)` from the same derivation dict, with the index-status provenance fields (`"index": status, "index_rebuilt": ...`). Phase 10's report CLI emits the snapshot provenance (window, event count, filters - D-01/TREND-05) in every payload the same way.

**Drill-down shape** - RESEARCH.md D-15: overview -> subject -> objective; keep the payload surface-neutral and let `retention_view` render it; the semantic `<table>` is canonical (CONTEXT "Future user choices": SVG is enhancement only).

---

### `surfaces/lesson.py` (controller/CLI, request-response) - lesson-completion seam

**Analog:** `record_key_review` (lesson.py:1088-1105) - the shared recording path used by both the daemon route and the CLI twin, resolving the identifier against the bank before appending:

```python
def record_key_review(bank_path, key_id, mode="practice", session_id="reader"):
    keys = parse_key_blocks(bank_path)
    if not any(k.get("id") == key_id for k in keys):
        return None
    bank_dir = os.path.dirname(os.path.abspath(bank_path)) or "."
    event = evidence.key_review_event(
        session_id=session_id, bank=os.path.basename(bank_path),
        key_id=key_id, mode=mode)
    evidence.append_event(evidence.log_path(bank_dir), event)
    return "Added to review."
```

10-02's `itembank lesson BANK --ref HEADING --complete` is the same shape: resolve the heading through `model.lesson_slug` (model.py:148-170) + `model.parse_lesson` (model.py:170-215) to sorted unique namespaced objectives, then append one versioned `lesson_complete` event through `evidence.append_event`; `None`/unknown heading exits non-zero, matching the route's 404 (research Open Question 1 RESOLVED lock).

---

### Schemas (config/contract, validation)

**`schemas/settings.schema.json`** (modified) - analog is itself. Copy the bounded-key shape of `daily_cap` (settings.schema.json:91-96) and `selection_weights` (settings.schema.json:98-131) for the new scheduling/trend thresholds (D-06: "Thresholds live in settings with conservative defaults and schema bounds"): `type` + `minimum`/`maximum` + `default` + `x-itembank-phase: 10`. `surfaces/settings.py:86` `load_settings` and `defaults_from_schema:51` then pick them up with no code change.

**`schemas/response.schema.json`** (modified) - extend `event_type` enum (response.schema.json:24-29) with the new Phase 10 event names and add one `$defs` entry per new event type, exactly as `day_tick`/`term_lookup`/`key_review` were added (oneOf per event, `const` on `event_type`, `additionalProperties: false`).

**`schemas/report.schema.json`** (modified) - the existing document is already a `oneOf` of `session_summary` and `objective_history`; add the longitudinal/retention payload as an additive third branch with the provenance fields (`window`, `event_count`, filters). Keep every new count "post-retraction" per the document's own description.

**Validator constraint** - only `schema_validate.py` is used; its `SUPPORTED` keyword set (schema_validate.py:24-33) has no `patternProperties`/`allOf`, so new schemas must use only `type/properties/required/additionalProperties/enum/const/items/minItems/minLength/pattern/minimum/maximum/$defs/$ref/oneOf`.

---

### Tests (`tests/retention_roundtrip.py` and siblings)

**Analog:** `tests/due_roundtrip.py` (184 lines) - hand-checked numeric expectations against synthetic data, plus `tests/day_roundtrip.py` (107 lines) for the subprocess server round-trip.

**Harness pattern** (due_roundtrip.py:21-30):
```python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANES = os.path.join(ROOT, "fixtures", "sample_lanes.md")
sys.path.insert(0, ROOT)
import itembank

def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)
```

**Time-controlled synthetic data** - due_roundtrip.py:113-139 (`check_behind_load`) builds plan/log dicts by hand and asserts exact numbers; retention_roundtrip.py does the same with synthetic timestamp-controlled evidence events (RESEARCH.md Validation Architecture Wave 0), including retraction and pending-`None` cases.

**Closed external service** - due_roundtrip.py:141-150 (`check_anki_closed`) sets `ANKI_CONNECT_URL` to a dead port and asserts `(None, None)`; the pacing test copies this for the Anki signal and for the cap-override path.

**Server check** - day_roundtrip.py:59-95 (`check_server`): spawn `itembank day ... --port 0 --no-open` with `subprocess.Popen`, scrape the printed URL, POST JSON, assert status, kill. `retention_ui_roundtrip.py` and `phase10_uat.py` use the same harness against the report route.

**Settings schema tests** - `tests/config_roundtrip.py` is the existing bounded-settings test; new thresholds get the same "out-of-bounds value rejected by `schema_validate`" cases.

---

## Shared Patterns

### One evidence writer
**Source:** `evidence.py:399` `append_event`
**Apply to:** all new event builders (`lesson_complete`, override), `surfaces/lesson.py`, `surfaces/day.py`, `surfaces/session.py`
```python
written, existing_id = append_line_checked(...)
if written:
    return {"accepted": True, "status": "recorded", "event_id": event["event_id"]}
return {"accepted": False, "status": "already_recorded", "event_id": existing_id}
```

### Live-events-only counting; accepted-marks-only mastery
**Source:** `evidence.py:997` `live_events`, `evidence.py:1117` `marks_by_event`
**Apply to:** `retention.py` (every count, every state derivation), `surfaces/day.py` cap counts
Counts derive from `live_events(log)`/`objective_history(log, ...)`; mastery reads the latest live mark. Pending `None` counts toward pacing only (D-09); retractions disappear through the same filter (research Pitfall 2).

### Disposable derived state + snapshot provenance
**Source:** `evidence.py:691-798` (INDEX_VERSION, rebuild_index), `surfaces/day.py:1191` `day_state`
**Apply to:** `retention.py`, `surfaces/day.py`, report payloads
Every `day`, report, and selection-weight calculation uses one immutable snapshot marker; caches are disposable and never authoritative (D-01/D-02); every output names window, event count, and filter (D-15/TREND-05).

### Event builder shape
**Source:** `evidence.py:1351` `day_tick_event`, `evidence.py:1435` `key_review_event`
**Apply to:** new event types in `evidence.py`
UPPERCASE `*_EVENT_TYPE` constant added to `KNOWN_EVENT_TYPES` (evidence.py:43); input validation raises `ValueError`; identity fields hashed into `dedupe_key`; `schema_version`/`event_id`/`event_type`/`ts` on every event; non-response events carry no `score` key, structurally.

### Conservative gate / first-class unknown
**Source:** `runtime.py:230` `glossable`
**Apply to:** `retention.py` state derivation (D-03 `unknown`; D-14 at-risk is "previously demonstrated success plus a configurable silence interval", never predicted failure)

### do_*/cmd_* split
**Source:** `surfaces/session.py:54/87` and docstring `:1-23`
**Apply to:** `surfaces/session.py` cap gate, `surfaces/lesson.py` complete command, CLI twins in `surfaces/evidence_cli.py`/`surfaces/retention_view.py`

### Route + CLI parity
**Source:** `surfaces/daemon.py:70-131` (API_ROUTES, ROUTES, ROUTE_CLI)
**Apply to:** new report/start routes; `tests/daemon_roundtrip.py` and `tests/protocol_roundtrip.py` assert the parity sets.

### API error containment
**Source:** `surfaces/daemon.py:1109-1153, 1342-1364`
**Apply to:** all new daemon handlers: `api_read_json`, identifier allowlist lookup, `SystemExit` -> 400, `Exception` -> path-free 500.

### Render via surface_shell
**Source:** `surfaces/presentation.py:168` `surface_shell`, `surfaces/daemon.py:321` `handle_report_get`
**Apply to:** `surfaces/retention_view.py`, `surfaces/day.py` cap-recovery surface

### Bounded settings + schema defaults
**Source:** `schemas/settings.schema.json:91-131`, `surfaces/settings.py:51-64` `defaults_from_schema`
**Apply to:** all new thresholds (min/max/default + `x-itembank-phase`); settings stays the only tunable surface (D-06/D-23).

### Atomic writes
**Source:** `evidence.py:768` `rebuild_index` (tmp + `os.replace`), `surfaces/evidence_cli.py:129` `cmd_render`
**Apply to:** report render outputs, any regenerated daily/report files.

### Anki read-only degradation
**Source:** `surfaces/day.py:372` `anki_read`
**Apply to:** `surfaces/day.py` due/new display; omit with an explanatory note, never block (SCHED-03).

### Test harness
**Source:** `tests/due_roundtrip.py:21-30`, `tests/day_roundtrip.py:59-95`
**Apply to:** all new `tests/*_roundtrip.py`: stdlib-only, `fail()` helper, synthetic fixtures, subprocess server checks, exact hand-checked numbers.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `selection.py` (modified) | service / pure selector | request-response | Phase 7 is unexecuted; the file does not exist in the tree. Phase 10 only adds an optional keyword-only `retention_context=None` while preserving all three-argument callers (10-03-PLAN.md lock). The planner should use `07-06-PLAN.md`'s contract: `selection.select(questions, spec, history) -> (items, trace)`, and keep practice/remediation consuming the context, diagnostic preserving Phase 7 coverage policy, and exam ignoring it. |

## Metadata

**Analog search scope:** repo root (`evidence.py`, `model.py`, `runtime.py`, `schema_validate.py`, `itembank.json`), `surfaces/` (day, session, daemon, lesson, cli, evidence_cli, protocol_cli, settings, presentation), `schemas/`, `tests/` (roundtrip suites), `fixtures/`.
**Files scanned:** ~30 source/test/config files; 24 classified; 13 analogs read in full or targeted sections.
**Pattern extraction date:** 2026-08-10
