---
phase: 04-surface-redesign-theming
reviewed: 2026-08-09T05:18:30Z
depth: deep
files_reviewed: 13
files_reviewed_list:
  - surfaces/cli.py
  - surfaces/daemon.py
  - surfaces/day.py
  - surfaces/day_document.py
  - surfaces/launcher.py
  - surfaces/presentation.py
  - surfaces/quiz.py
  - surfaces/quiz_page.py
  - surfaces/settings.py
  - surfaces/study.py
  - surfaces/theme.py
  - schemas/settings.schema.json
  - itembank.json
findings:
  critical: 2
  warning: 5
  info: 2
  total: 9
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-08-09T05:18:30Z
**Depth:** deep
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Reviewed the complete phase 04 implementation (`git diff c0d344b..HEAD`): the
consolidated daemon and route table, the shared presentation/theme system, the
served-quiz API flow, the study surface, and the structured day editor with
conflict recovery and the one-use force gate. Cross-file call chains were
traced (day editor -> `day_document.save` -> atomic replace; served quiz ->
`/api/start|submit` -> `session.do_*`; theme -> settings schema -> `theme_css`;
script-embedded page data for quiz/day/study).

The design is generally sound: the force gate binds a random one-use token to
stem/revision/draft-hash and re-checks the file immediately before
`os.replace`; the daemon resolves every client identifier through
startup-built allowlists; and route handlers contain `SystemExit` from the
`session.do_*` runtime. The regression suite for the day editor and theme
passes (10/10 in `tests/day_edit_roundtrip.py` + `tests/theme_roundtrip.py`).

Two security defects were reproduced live and block shipping: stored XSS
through bank/plan content embedded unescaped into page scripts (the study
surface already solved this; quiz and day did not), and missing
same-origin/CSRF protection on every state-changing daemon route except
`/api/theme`. The remaining warnings are conflict-recovery data staleness, a
UTF-8 crash in the conflict path, a settings-validation gap, and two editor
correctness edges.

## Critical Issues

### CR-01: Stored XSS via bank/plan content embedded raw into page `<script>` data

**File:** `surfaces/quiz.py:87-88`, `surfaces/day.py:1084-1091`
**Issue:** Both page builders embed JSON into a `<script>` element with plain
`json.dumps(...)`, which does not escape `<`, `>`, `&`, or U+2028/U+2029.
`page_for` writes `__DATA__` (offline build: every item's stem, option text,
explanations) and `__BOOT__`; `day_page` writes `window.__day__` containing
`snapshot.document` — the full plan text — and all cell values. Any bank item
or plan cell containing `</script>` closes the script element and injects
executable markup. Reproduced live: an option text of
`</script><script>window.__pwned__=1</script>` in a bank produces a built
`itembank build` page with four `<script>` tags (the payload executes), and a
plan cell with the same payload executes on `GET /day/<stem>` — on the daemon
origin, giving injected script same-origin access to every route. The phase's
own T-04-17 fix for the study surface (`script_safe_json`,
`surfaces/study.py:21-28`) proves this was a known hazard class; quiz and day
were not migrated to it.
**Fix:** Route `__DATA__`/`__BOOT__` and `window.__day__` through the same
script-safe encoding used by study, e.g. move the helper into a shared module
and apply it in both builders:
```python
# surfaces/quiz.py and surfaces/day.py (shared helper)
def script_safe_json(value):
    return (json.dumps(value, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))

# page_for:  .replace("__DATA__", script_safe_json(items))
#            .replace("__BOOT__", script_safe_json(boot))
# day_page:  "<script>window.__day__=%s;\n%s</script>"
#            % (script_safe_json(boot), DAY_JS)
```
Add a regression assertion that a bank option/plan cell containing
`</script>` never produces a second script tag in the rendered page.

### CR-02: No same-origin / CSRF protection on state-changing daemon routes

**File:** `surfaces/daemon.py:770` (`handle_day_save`), `:788`
(`handle_day_open`), `:861` (`handle_day_edit`), `:624`
(`handle_quiz_answer`), `:1043`/`:1102`/`:1158`/`:1225` (`/api/*`)
**Issue:** `POST /api/theme` is the only mutating route gated by `_same_origin`
(and loopback for non-preview actions, daemon.py:524-526). Every other
mutating route accepts cross-origin browser requests. A malicious webpage can
issue a "simple" CORS request (no preflight, e.g. `Content-Type: text/plain`
with a JSON body — `read_json` ignores the content type) against
`http://127.0.0.1:<port>/day/<stem>/save` and silently tick every lane for any
date, polluting the learner's evidence log and `daily_log.md`; `/day/<stem>/edit`
is partially protected only because the attacker cannot read the current
revision hash — DNS rebinding defeats even that. `handle_theme_post`'s own
docstring establishes same-origin-plus-loopback as the intended authority
model for writes, so the day/quiz/api routes are an inconsistency with a
concrete attack path (local tool mutation, evidence forgery).
**Fix:** Apply the existing gate to every mutating route. Browsers send an
`Origin` header; LAN curl/CLI clients do not, so adding the check does not
break the documented `--lan` phone use:
```python
def _reject_cross_origin(handler):
    if not _same_origin(handler):
        handler.send_error(403, "cross-origin request refused")
        return True
    return False

# First line of handle_day_save / handle_day_open / handle_day_edit /
# handle_quiz_answer / handle_api_start|next|submit|report:
if _reject_cross_origin(handler):
    return
```
For the day routes additionally require a loopback client for writes when the
daemon is bound to `0.0.0.0`, mirroring the theme policy.

## Warnings

### WR-01: Conflict "Copy current"/"Download current" serve the stale page-load document

**File:** `surfaces/day.py:716`, `:755`
**Issue:** On a conflict, `showConflict` calls
`fillPanels(draft, currentCells(d), SNAP.document, SNAP.revision, d.current.revision)`.
The pane header and cells use the fresh conflict data (`d.current.revision`,
`d.current.cells`), but `current-doc` — the text behind the "Copy current" and
"Download current" buttons (day.py:840-843) — is filled from `SNAP.document`,
the page-load (stale) plan text. `d.current.document`, which
`_conflict_result` explicitly carries (day_document.py:254), is never read by
the client. A learner who follows the recovery UI and downloads "Current file"
gets the version they were editing against, not the actual current file — and
the revision label above it promises the fresh version.
**Fix:** Prefer the conflict's fresh document:
```js
function showConflict(d){
  ...
  fillPanels(draft, currentCells(d), (d.current && d.current.document) || SNAP.document,
             SNAP.revision, d.current.revision);
}
```
and use the same fallback in the non-conflict error branch (day.py:755).

### WR-02: Conflict path crashes on a non-UTF-8 concurrent edit instead of returning a conflict

**File:** `surfaces/day_document.py:245`
**Issue:** `_conflict_result` computes `text = data.decode("utf-8")`
unconditionally before `_analyze` runs. If the file changed to non-UTF-8 bytes
during the save window, `_atomic_replace` raises `StaleRevisionError(current_bytes)`
and `_conflict_result` raises `UnicodeDecodeError` — reproduced directly:
`_conflict_result({"Task": "x"}, "rev", b"abc\xff\xfe...", "2026-08-09", False)`
raises `UnicodeDecodeError`. The daemon's `except Exception` then returns 500
"internal error" (daemon.py:899), so the no-write recovery UI never appears.
No bytes are lost (the write is refused), but the advertised recovery contract
fails on a plausible external-edit scenario.
**Fix:** Decode defensively, e.g.:
```python
try:
    text = data.decode("utf-8")
except UnicodeDecodeError:
    text = data.decode("utf-8", errors="replace")
```
The conflict document copy is for display/copy; a lossy decode there is safe
and never written back.

### WR-03: `accent.source` schema accepts non-hex values that are silently ignored

**File:** `schemas/settings.schema.json:29-33`, `surfaces/theme.py:260-266`
**Issue:** The schema constrains `accent.source` to a string with
`minLength: 7` only — no pattern. Verified: `schema_validate.validate("zzzzzzz",
subschema)` returns no errors, so `itembank config set accent.source zzzzzzz`
(and a hand-edited file) persists an invalid source. Every render then
silently falls back to `DEFAULT_ACCENT` because `theme_css` treats a failed
`normalize_source` as "use the default" (theme.py:262-266) — the learner's
custom accent disappears with no error, and `itembank config` continues to
report the bogus value as current. The schema description even claims the
contract is "exact six-digit hex", but the schema does not enforce it.
**Fix:** Add the pattern to the schema (and cover it with a config test):
```json
"source": {
  "type": "string",
  "pattern": "^#[0-9a-fA-F]{6}$",
  "minLength": 7,
  "default": "#0e6e62"
}
```
Optionally, also route `config set accent.source` through
`theme.normalize_source` so the error message matches `theme set`.

### WR-04: Day editor renders a phantom input for the date column when its header label is not exactly "Date"

**File:** `surfaces/day.py:1007`
**Issue:** The editor builds fields with
`editable = [(c, cells.get(c, "")) for c in columns if c != "Date"]`, but the
snapshot excludes column 0 by *index* (`day_document.py:234-236`), not by
label. A plan whose first column header is `DAY`, `DATE`, `Date `, or any
other label therefore renders an empty single-line input for the date column.
Submitting it is always refused ("the date column is the row key and is not
editable"), so the page shows an input that can never be saved and the
highlighted-cell error copy ("Fix this cell.") points at a cell the learner
cannot fix.
**Fix:** Filter by position rather than label, e.g. skip the first column of
the snapshot (`columns[1:]`), or have `_build_snapshot` carry a parallel
`editable` flag per column and have `day_page` honor it.

### WR-05: Served quiz "View report" links are dead 404s

**File:** `surfaces/quiz_page.py:982-983`, `:996-997`
**Issue:** Both `finish()` and `emptyState()` in `SERVED_JS` emit
`href="/report"` with no session id. `handle_report_get` (daemon.py:314)
resolves the session from the `session` query parameter and 404s on an empty
value, so the "View report" action always lands on a Not Found page even
though the client holds the session id (`sessionId`). The OFFLINE client
correctly omits the link; only the served client is broken.
**Fix:** Carry the session id in the link:
```js
var report = "/report?session=" + encodeURIComponent(sessionId || "");
// finish() and emptyState():  href=report
```

## Info

### IN-01: Force-token store grows without bound

**File:** `surfaces/daemon.py:874-878`
**Issue:** `_issue_day_force_token` inserts into `handler.day_force_tokens` and
only ever removes on consumption. A token is never evicted on a later conflict
for the same stem (a new token is minted, the old one remains), and there is no
expiry or cap, so a long-running daemon accumulates one entry per conflict.
The entries are tiny and unguessable, so this is a housekeeping issue, not a
security one.
**Fix:** Evict any prior token bound to the same stem when issuing a new one,
or cap/expire the store (e.g. a per-stem single slot).

### IN-02: Dead code in the served/offline quiz clients

**File:** `surfaces/quiz_page.py:592`, `:689`, `:536`
**Issue:** In `SERVED_JS`, `shownAt` is assigned on every render but never
read — the served client never sends `elapsed_ms`, so response-time recording
is always `null` for API sessions (this is honest, but the variable is dead).
In `OFFLINE_JS` `finish()`, `document.getElementById("rail")` references an
element removed by the phase's own redesign and is guarded dead code.
**Fix:** Remove `shownAt` from `SERVED_JS` (or wire it into
`/api/submit`'s `elapsed_ms` if response timing is wanted) and drop the `rail`
line.

---

_Reviewed: 2026-08-09T05:18:30Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: deep_
