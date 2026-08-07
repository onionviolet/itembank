---
phase: 02-daemon-consolidation-settings-foundation
plan: 05
subsystem: api
tags: [http.server, session-report, html-template, daemon]

# Dependency graph
requires:
  - phase: 02-daemon-consolidation-settings-foundation
    provides: "02-01/02-02: ROUTES/ROUTE_CLI, DaemonHandler, scan_dir()'s allowlist, INDEX_TEMPLATE's __THEME__ substitution convention; 02-04: session_index(root), api_session_path, the except SystemExit/except Exception containment pair, session.do_report"
provides:
  - "surfaces/daemon.py: REPORT_TEMPLATE, handle_report_get -- GET /report?session=<id>, rendered from exactly the dict session.do_report() returns, with empty/in-progress/populated states branching on that dict's own data"
  - "surfaces/daemon.py: sessions_by_bank(root, banks) and the index's per-bank View report link, wired only for banks with at least one recorded session"
  - "tests/daemon_roundtrip.py: report_field/report_progress/report_objective_rows regex helpers against REPORT_TEMPLATE's data-field markers, and drive_sitting() -- reusable by any later plan asserting against the report page"
affects: [Phase 4 (SURF-02/05-09 surface redesign and theming, which is expected to restyle this page), Phase 6+ (any future surface that renders a session summary)]

actuals:
  tokens: 6860
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "REPORT_TEMPLATE follows INDEX_TEMPLATE's __THEME__/__BODY__ str.replace() substitution convention, adding __TITLE__; the daemon's two new pages read as one family"
    - "Three render states (empty/in-progress/populated) are branches of one template chosen on session.do_report()'s own returned data, never a rendering flag threaded in from the route handler"
    - "data-field=\"<name>\" attributes on every numeric figure give tests a stable regex marker to assert against instead of scraping prose -- a copywriting change cannot silently break a numbers assertion"
    - "position/total for the in-progress state come from a direct read_session(path) call (the session's own cursor and item count), never recomputed from the responses list session_summary() already reduced"

key-files:
  created: []
  modified:
    - surfaces/daemon.py
    - tests/daemon_roundtrip.py

key-decisions:
  - "handle_report_get calls session.do_report(path) for the summary/status dict (the one function itembank report also calls), and separately calls runtime.read_session(path) only in the in-progress branch to read cursor/len(items) -- do_report's own return shape was left unchanged since this plan's files_modified scoped only surfaces/daemon.py and tests/daemon_roundtrip.py"
  - "The empty-state test is data-driven (auto_attempts==0 and pending_manual==0), independent of session status -- a session with zero responses is 'Nothing answered yet' whether it is still active or was somehow marked complete with none recorded, matching the plan's own instruction to branch on data rather than a flag"
  - "sessions_by_bank(root, banks) reads every session_index() file a second time to match its bank field against banks' own abspaths, rather than extending session_index() itself, keeping session_index()'s existing shape ({session_id: path}) untouched for /api/*'s callers"
  - "GET /report is registered as a fixed literal ahead of API_ROUTES in ROUTES, preserving the established rule that every fixed literal precedes every stem pattern (checked structurally by this plan's own acceptance criterion)"

requirements-completed: [SURF-01, SURF-04]

coverage:
  - id: D1
    description: "GET /report?session=<id> renders a session's summary as a page on the same port as every other surface, completing SURF-01's route list"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_report_populated"
        status: pass
      - kind: unit
        ref: "python -c \"...('GET','/report') in [e[:2] for e in daemon.ROUTES]...\" (plan acceptance criterion)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The report page and itembank report read one summary function (session.do_report/runtime.session_summary) and cannot disagree on auto_attempts, auto_correct, or pending_manual"
    requirement: SURF-04
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_report_matches_command"
        status: pass
    human_judgment: false
  - id: D3
    description: "An unknown or missing session on /report returns HTTP 404 with the documented Not found copy, never a traceback or a filesystem path, and the session identifier is never joined to a path"
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_report_not_found"
        status: pass
    human_judgment: false
  - id: D4
    description: "A session with zero recorded responses renders the documented Nothing answered yet empty state rather than a report table with blank/zero cells"
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_report_empty"
        status: pass
    human_judgment: false
  - id: D5
    description: "An in-progress session shows a position-of-total reading from the session's own cursor and item count, so a mid-session report is never mistaken for a final one"
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_report_in_progress"
        status: pass
    human_judgment: false
  - id: D6
    description: "A session with zero auto-marked responses (all short) renders a 0 percentage, never a ZeroDivisionError or NaN, mirroring quiz_page.py's finish() guard"
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_report_zero_auto_marked"
        status: pass
    human_judgment: false
  - id: D7
    description: "The per-objective row renders the same shape at one objective as at many, and objective names/table cells wrap rather than truncate"
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_report_objective_rows_one_and_many"
        status: pass
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_report_no_truncation"
        status: pass
    human_judgment: false
  - id: D8
    description: "The overflow behaviour of a report carrying ten or more pending short items, and the concrete visual layout of the populated case, confirmed at UAT rather than automated (this plan's own must_haves backstops)"
    verification: []
    human_judgment: true
    rationale: "Explicitly carried as backstops in the plan's must_haves -- no fixture in this repo has ten pending short items, and the exact visual layout of the populated case was a planner/executor decision per RESEARCH.md Open Question 2, not fully pre-specified in the UI-SPEC."

duration: 16min
completed: 2026-08-07
status: complete
---

# Phase 02 Plan 05: The Daemon's Report Page Summary

**`surfaces/daemon.py` gained `GET /report?session=<id>`, rendered from exactly `session.do_report()`'s own dict with empty/in-progress/populated states chosen on that data, closing SURF-01's route list on the daemon's one port.**

## Performance

- **Duration:** 16 min
- **Started:** 2026-08-07T13:25:11-05:00 (approx, per prior plan's completion commit)
- **Completed:** 2026-08-07T13:41:05-05:00
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `surfaces/daemon.py` gained `REPORT_TEMPLATE` (following `INDEX_TEMPLATE`'s `__THEME__`/`__BODY__` substitution convention, adding `__TITLE__`) and `handle_report_get()`, registered as a fixed-literal `GET /report` route ahead of every stem-parameterised route and mapped to `report` in `ROUTE_CLI`
- Three render states -- empty (`Nothing answered yet`), in-progress (populated card plus a `cursor`/`len(items)` position reading), and populated (headline auto-marked percentage, three labelled figures, one objective row per `session_summary()` bucket) -- are branches of one template, chosen on `session.do_report()`'s own returned data rather than a flag
- Every numeric figure carries a `data-field="<name>"` marker (`auto_attempts`, `auto_correct`, `pending_manual`, `pct`, `progress`) so tests (and any future page) can assert against a stable attribute instead of scraping prose
- The percentage guard mirrors `quiz_page.py`'s `finish()` step (`pct = round(correct/attempts*100) if attempts else 0`), so a session with zero auto-marked responses renders `0%`, never a `ZeroDivisionError` or `NaN`
- `handle_report_get` wraps `session.do_report()` in the same `except SystemExit` / `except Exception` containment pair every `/api/*` handler already carries, so a malformed or future-versioned session file is a 4xx rather than a dead daemon
- The `/` index's per-bank row gains a `View report` link to `/report?session=<id>`, wired only for banks with at least one recorded session (`sessions_by_bank()`), omitted for banks with none rather than rendering a dead link
- `tests/daemon_roundtrip.py` gained 8 new checks covering populated, page-vs-command agreement (SURF-04), empty, in-progress, zero-auto-marked, one-vs-many objective row shape, not-found (no param / unknown id / parent-directory path), and no-truncation, plus `report_field`/`report_progress`/`report_objective_rows` regex helpers and a `drive_sitting()` fixture helper reusable by later plans

## Task Commits

Each task was committed atomically:

1. **Task 1: The report page -- populated, in-progress, empty and not-found** - `f8e899e` (feat)
2. **Task 2: Report route coverage and page-versus-command agreement** - `5177660` (test)

_Note: this plan's docs-completion commit (SUMMARY.md/STATE.md/ROADMAP.md/REQUIREMENTS.md) follows this file's creation, per the execute-plan workflow._

## Files Created/Modified
- `surfaces/daemon.py` - `REPORT_TEMPLATE`, `REPORT_EMPTY`, `_report_figure`/`_report_objective_rows`/`_report_card`, `handle_report_get`, `sessions_by_bank`; `BANK_ROW` gained a `__REPORT_LINK__` placeholder; `handle_index` wires the per-bank report link; `ROUTES`/`ROUTE_CLI` extended with `GET /report`; `runtime` import extended to include `read_session`
- `tests/daemon_roundtrip.py` - `session` added to the `surfaces` import; `report_field`/`report_progress`/`report_objective_rows`/`drive_sitting` helpers; `check_report_populated`, `check_report_matches_command`, `check_report_empty`, `check_report_in_progress`, `check_report_zero_auto_marked`, `check_report_objective_rows_one_and_many`, `check_report_not_found`, `check_report_no_truncation`, all registered in `main()`'s checks tuple

## Decisions Made
- `handle_report_get` reaches session state through two calls: `session.do_report(path)` for the summary/status dict (the exact function `itembank report` also calls, keeping the page and the command provably in agreement), and a direct `runtime.read_session(path)` call -- only in the in-progress branch -- for `cursor`/`len(items)`, since `do_report`'s own return shape carries no position data and this plan's `files_modified` scoped changes to `surfaces/daemon.py` and `tests/daemon_roundtrip.py` only, not `surfaces/session.py`.
- The empty-state branch is decided purely on `summary["auto_attempts"] == 0 and summary["pending_manual"] == 0`, independent of `status` -- matching the plan's instruction that the three states are "branches of one template," chosen on the data rather than a flag threaded through the call.
- `sessions_by_bank(root, banks)` re-reads every file `session_index()` already found (matching each session's own `bank` field against `banks`' abspaths) rather than extending `session_index()` itself, so `/api/*`'s existing `{session_id: path}` contract stays untouched for its own callers.
- The zero-auto-marked test fixture uses a hardcoded seed (8) with `count=1` against the fixture bank's sole `short` item, found once by a short local script and recorded in the test's own docstring, rather than searching for it at test time or constructing a hand-written session file.

## Deviations from Plan

None - plan executed exactly as written. The one implementation choice not fully pre-specified by the plan (whether `handle_report_get` reads position/total via a second `read_session()` call or via an extended `do_report()` return) was resolved by respecting the plan's own `files_modified` scope (Rule 4 territory in principle, but the plan's frontmatter already settled it by omitting `surfaces/session.py` from the list).

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The route list SURF-01 names is now complete on one port: `/`, `/__itembank__`, `/day`, `/report`, `/api/start|next|submit|report`, `/quiz/<stem>`, `POST /quiz/<stem>/answer`, `/study/<stem>`, `/day/<stem>`, `POST /day/<stem>/save`, `POST /day/<stem>/open` -- all asserted equal to `ROUTE_CLI`'s key set.
- `REPORT_TEMPLATE`'s `data-field` marker convention is now the established pattern for any future page needing a stable, prose-independent test hook -- Phase 4's SURF-02/05-09 surface redesign restyles this page but should keep the markers if it wants the existing report tests to survive unmodified.
- No blockers. Plan 02-06 (the daemon's `probe`/`start_server` launch consolidation, per the Artifacts table's forward reference) is next.

---
*Phase: 02-daemon-consolidation-settings-foundation*
*Completed: 2026-08-07*
