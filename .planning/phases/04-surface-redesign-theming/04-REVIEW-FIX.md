---
phase: 04-surface-redesign-theming
fixed_at: 2026-08-09T00:38:59Z
review_path: .planning/phases/04-surface-redesign-theming/04-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 04: Code Review Fix Report

**Fixed at:** 2026-08-09T00:38:59Z
**Source review:** .planning/phases/04-surface-redesign-theming/04-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 7 (Critical + Warning; Info findings IN-01/IN-02 are
  outside the default `critical_warning` fix scope)
- Fixed: 7
- Skipped: 0

## Fixed Issues

### CR-01: Stored XSS via bank/plan content embedded raw into page `<script>` data

**Files modified:** `surfaces/presentation.py`, `surfaces/study.py`,
`surfaces/quiz.py`, `surfaces/day.py`, `tests/surface_roundtrip.py`,
`tests/day_edit_roundtrip.py`
**Commit:** `7637de8`
**Applied fix:** Moved `script_safe_json` into the shared presentation module
(`surfaces/presentation.py`) and routed the quiz page's `__DATA__`/`__BOOT__`
substitutions and the day page's `window.__day__` boot through it; study now
imports the same shared helper instead of carrying its own copy. Added
regression assertions that a bank option or plan cell containing
`</script><script>...` never adds a script element to the rendered page and is
serialized as `\u003c/script\u003e`.

### CR-02: No same-origin / CSRF protection on state-changing daemon routes

**Files modified:** `surfaces/daemon.py`, `tests/daemon_roundtrip.py`
**Commit:** `30dddb8`
**Applied fix:** Added `_reject_cross_origin` and `_reject_cross_origin_write`
helpers and applied them as the first statement of every mutating route:
`handle_day_save`/`handle_day_open`/`handle_day_edit` (same-origin plus a
loopback client, mirroring the `/api/theme` write policy), and
`handle_quiz_answer` + `handle_api_start|next|submit|report` (same-origin).
Requests without an `Origin` (CLI/curl clients) still pass the same-origin
check, so LAN phone reads and the documented CLI paths are unaffected. Added a
regression check that all eight routes return 403 to a cross-origin POST
before any mutation, while Origin-less and same-origin loopback requests still
pass.

### WR-01: Conflict "Copy current"/"Download current" serve the stale page-load document

**Files modified:** `surfaces/day.py`, `tests/day_edit_roundtrip.py`
**Commit:** `69db8d2`
**Applied fix:** `showConflict` now fills `current-doc` from the conflict's
fresh `d.current.document` (falling back to `SNAP.document`), and the
non-conflict error branch prefers the server-returned `d.document` over the
stale page-load snapshot. Every `day_document.save` result already carries
`document`, so the copy/download actions now match the revision label. Added a
client-source regression assertion for both branches.

### WR-02: Conflict path crashes on a non-UTF-8 concurrent edit instead of returning a conflict

**Files modified:** `surfaces/day_document.py`, `tests/day_edit_roundtrip.py`
**Commit:** `65deda9`
**Applied fix:** `_conflict_result` decodes the current bytes defensively
(`errors="replace"` fallback on `UnicodeDecodeError`); the conflict document is
display/copy text only and is never written back. Added a regression test that
calls the conflict path with non-UTF-8 current bytes and asserts a no-write
conflict with a lossily-decoded string document instead of a crash.

### WR-03: `accent.source` schema accepts non-hex values that are silently ignored

**Files modified:** `schema_validate.py`, `schemas/settings.schema.json`,
`tests/config_roundtrip.py`
**Commit:** `1541d40`
**Applied fix:** The hand-rolled `schema_validate.py` validator refuses any
keyword outside its supported set, so the schema fix required teaching it
`pattern` first (module docstring, `SUPPORTED`, and a `re.search` check).
`schemas/settings.schema.json` now carries
`"pattern": "^#[0-9a-fA-F]{6}$"` on `accent.source` (description updated), so
`itembank config set accent.source` and a hand-edited file are rejected with
`settings.invalid_value` instead of silently falling back to the default
accent. Added a config regression test covering valid hex (lower/upper),
non-hex rejection, and no file mutation on rejection.

### WR-04: Day editor renders a phantom input for the date column when its header label is not exactly "Date"

**Files modified:** `surfaces/day.py`, `tests/day_edit_roundtrip.py`
**Commit:** `cc1b9af`
**Applied fix:** The editor's `editable` list now skips the first column by
position (`columns[1:]`), matching `day_document._build_snapshot`, which
excludes column 0 by index -- a plan whose first header is `DAY`, `DATE`, or
`Date ` no longer renders an input that can never be saved. Added a regression
test for those three header spellings plus the default `Date`.

### WR-05: Served quiz "View report" links are dead 404s

**Files modified:** `surfaces/quiz_page.py`, `tests/surface_roundtrip.py`
**Commit:** `e699ac2`
**Applied fix:** `finish()` and `emptyState()` in `SERVED_JS` now build
`/report?session=` + `encodeURIComponent(sessionId || "")` and use it as the
View report `href`, so the served client reaches the same report page
`handle_report_get` already serves by `session` query parameter. Added a
regression assertion on the rendered served script.

## Verification

Every targeted regression suite ran green inside the isolated worktree
(`.claude/worktrees/rf-04-264-1786252862`, branch `gsd-reviewfix/04-264`), not
the main checkout:

- `tests/day_edit_roundtrip.py` -- pass (CR-01 day, WR-01, WR-02, WR-04)
- `tests/surface_roundtrip.py` -- pass (CR-01 quiz, WR-05)
- `tests/daemon_roundtrip.py` -- 58 checks pass (CR-02)
- `tests/config_roundtrip.py` -- pass (WR-03)
- `tests/theme_roundtrip.py` -- pass (schema/validator regression)
- `tests/serve_roundtrip.py` -- pass (served quiz + API flow regression)

Per the fixer contract, the full test suite was not run between fixes;
end-to-end coverage is handled by the verifier phase.

---

_Fixed: 2026-08-09T00:38:59Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
