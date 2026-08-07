---
phase: 02-daemon-consolidation-settings-foundation
plan: 02
subsystem: api
tags: [http.server, socketserver, route-table, evidence, daemon]

# Dependency graph
requires:
  - phase: 02-daemon-consolidation-settings-foundation
    provides: "02-01: surfaces/daemon.py's route table (ROUTES/ROUTE_CLI), DaemonHandler/Daemon, scan_dir(), quiz.record_answer(), the __POST__ bank-scoping pattern, and tests/daemon_roundtrip.py's start_daemon() helper"
provides:
  - "study.study_page(bank_path, qs): the flashcard/Learn template factored out of cmd_study so the daemon and the CLI render from one function"
  - "day.day_state()/day_render()/apply_day_post(): cmd_day's pre-bind block, render() closure and POST handler factored into reusable functions the daemon holds one cached instance of per served plan"
  - "day_page()/DAY_JS's base=/D.base plan-scoping, the same fix __POST__ was for the quiz page"
  - "surfaces/daemon.py: GET /study/<stem>, GET /day/<stem>, GET /day (single-plan passthrough or documented ambiguous 404), POST /day/<stem>/save, POST /day/<stem>/open, all registered in ROUTES and ROUTE_CLI"
  - "daemon.serve_scoped(root, banks, plans, port, ...): the bind/print-URL/browser-open/serve_forever tail factored out of cmd_daemon, reused by cmd_serve and cmd_day so they launch the same daemon scoped to one bank or one plan instead of duplicating it"
  - "surfaces/quiz.py and surfaces/day.py contain no request-handler method; surfaces/daemon.py is the only module in the codebase defining do_GET/do_POST"
affects: [02-04, 02-05, 02-06]

actuals:
  tokens: 16400
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Per-surface render factoring (study_page/day_render/apply_day_post) so the daemon and the CLI call exactly one function for a page or a mutation, never a second copy in the route handler (D-08 extended to study and day)"
    - "Plan-scoped POST prefix (day_page's base=/window.__day__.base) mirroring quiz_page's __POST__ placeholder -- one process serving several plans needs each page to say which plan it posts back to"
    - "serve_scoped(...) as the one bind/print/serve_forever tail every daemon launch (whole-directory or single-bank/single-plan-scoped) shares, with extra/day_extra/on_bound as the three seams a scoped caller uses to pin session bookkeeping, per-plan --log/--lanes/--date overrides, and its own banner lines onto the shared handler class"

key-files:
  created: []
  modified:
    - surfaces/daemon.py
    - surfaces/study.py
    - surfaces/day.py
    - surfaces/quiz.py
    - tests/daemon_roundtrip.py
    - tests/serve_roundtrip.py
    - tests/day_roundtrip.py
    - tests/evidence_roundtrip.py

key-decisions:
  - "day_state()/day_render()/apply_day_post() take an explicit iso rather than always computing 'today', and day_extra threads iso through serve_scoped's extra -- otherwise itembank day --date (backfilling a missed day) would silently break once day became a daemon launch, since the daemon's own per-plan state build has no CLI flags to read from"
  - "handle_quiz_answer reads reveal/progress off the bank's session dict (defaulting to off) rather than being parameterised at the route-table level, so a general multi-bank itembank daemon launch is unaffected while itembank serve's scoped launch regains its exact --reveal behaviour and its 'd/N answered, saved' progress line"
  - "serve_scoped's on_bound(port) callback is the seam for banner lines that need the actual bound port (cmd_day's --lan phone address) printed in the same position (after 'url', before the final note) the pre-refactor code held them in"

requirements-completed: [SURF-01, SURF-04]

coverage:
  - id: D1
    description: "One itembank daemon process serves the quiz, the study loop, the day cockpit and the day cockpit's two mutations (save/open) on the same port"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_study_route,check_day_route,check_day_index_single_plan,check_day_save_and_isolation,check_day_open_out_of_range"
        status: pass
    human_judgment: false
  - id: D2
    description: "study_page() and day_render()/apply_day_post() are the one function the daemon and the CLI both call -- no second copy of the study template or the day POST logic lives in daemon.py"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_study_cmd_matches_study_page"
        status: pass
      - kind: unit
        ref: "python -c \"...assert 'D.base' in day.DAY_JS...\" (plan acceptance criterion)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two day plans served from one daemon keep their ticks apart: a save against one plan's stem never writes into another plan's daily_log.md"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_day_save_and_isolation"
        status: pass
    human_judgment: false
  - id: D4
    description: "GET /day serves the sole scanned plan when exactly one exists; with zero or two-or-more it is a documented 404 carrying no filesystem path"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_day_index_single_plan,check_day_index_ambiguous"
        status: pass
    human_judgment: false
  - id: D5
    description: "surfaces/quiz.py and surfaces/day.py no longer define a request handler; surfaces/daemon.py is the only module in the codebase that does"
    requirement: SURF-01
    verification:
      - kind: unit
        ref: "python -c \"...assert 'do_GET' not in inspect.getsource(quiz)...\" (plan acceptance criterion)"
        status: pass
    human_judgment: false
  - id: D6
    description: "itembank serve BANK and itembank day PLAN keep their existing argument surface and observable behaviour, now as daemon launches scoped to one bank/plan"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/serve_roundtrip.py, tests/day_roundtrip.py, tests/evidence_roundtrip.py#test_serve_writes_events,test_day_ticks_are_events"
        status: pass
      - kind: manual_procedural
        ref: "python itembank.py serve --help / itembank.py day --help diffed against git show HEAD~1:surfaces/cli.py (unchanged); itembank day ... --check --date exits 0 without binding a port"
        status: pass
    human_judgment: false
  - id: D7
    description: "ROUTE_CLI still names a CLI command for every registered route, including the new study/day routes"
    requirement: SURF-04
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_route_cli_inventory"
        status: pass
    human_judgment: false

duration: 26min
completed: 2026-08-07
status: complete
---

# Phase 02 Plan 02: Study, Day and Day-Mutation Routes; Serve/Day Become Daemon Launches Summary

**`surfaces/daemon.py` now serves the study loop and the day cockpit (plus its two POST mutations) alongside the quiz on one port, and `itembank serve`/`itembank day` were demoted from socket owners to `daemon.serve_scoped()` launches scoped to one bank or one plan -- `surfaces/daemon.py` is the only module left in the codebase defining an HTTP request handler.**

## Performance

- **Duration:** 26 min
- **Started:** 2026-08-07T17:16:22Z (approx, per prior plan's completion)
- **Completed:** 2026-08-07T17:42:05Z
- **Tasks:** 2
- **Files modified:** 8 (4 surface modules, 4 test files)

## Accomplishments
- `study.study_page(bank_path, qs)` factored out of `cmd_study`'s inline substitution chain; `surfaces/daemon.py`'s `handle_study_get` renders `GET /study/<stem>` from the exact same function, and `cmd_study`'s own written file is asserted byte-identical to it
- `day.day_state()`/`day_render()`/`apply_day_post()` factored out of `cmd_day`'s pre-bind block, `render()` closure and POST handler; `day_page()` and `DAY_JS` gained a `base=`/`D.base` plan-scoped POST prefix (the same fix `__POST__` was for the quiz page) so one daemon can serve several day plans without their save/open routes colliding
- `surfaces/daemon.py` gained `GET /study/<stem>`, `GET /day/<stem>`, the single-plan-passthrough-or-documented-404 `GET /day`, `POST /day/<stem>/save` and `POST /day/<stem>/open`, all registered in `ROUTES` and `ROUTE_CLI`, with per-plan `day_state` cached on the handler class so ticks accumulate across requests
- `daemon.serve_scoped(root, banks, plans, port, ...)` factored out of `cmd_daemon`'s tail (bind, print URL, optional browser open, `serve_forever()` inside the `KeyboardInterrupt` guard); `cmd_daemon`, `cmd_serve` and `cmd_day` now all call it instead of each binding their own socket
- `surfaces/quiz.py`'s `cmd_serve` and `surfaces/day.py`'s `cmd_day` deleted their handler classes entirely; `surfaces/daemon.py` is now the only module in the codebase defining `do_GET`/`do_POST`
- 11 new integration checks across `tests/daemon_roundtrip.py` (study route, cmd_study/study_page equality, day route, single-plan and zero/two-plan `GET /day`, two-plan save isolation, out-of-range open 404) plus fixes to `tests/serve_roundtrip.py`, `tests/day_roundtrip.py` and `tests/evidence_roundtrip.py` so their POST helpers resolve the now bank-/plan-scoped paths instead of assuming a bare `/answer` or `/save`

## Task Commits

Each task was committed atomically:

1. **Task 1: Study, day and day-mutation routes on the same port** - `6d098fb` (feat)
2. **Task 2: `serve` and `day` become daemon launches -- the second HTTP mechanism is removed** - `f92a1cf` (feat)

_Note: this plan's docs-completion commit (SUMMARY.md/STATE.md/ROADMAP.md/REQUIREMENTS.md) follows this file's creation, per the execute-plan workflow._

## Files Created/Modified
- `surfaces/study.py` - `study_page(bank_path, qs)` factored out; `cmd_study` now calls it
- `surfaces/day.py` - `day_state()`, `day_render()`, `apply_day_post()` factored out of `cmd_day`; `day_page()`/`DAY_JS` gained `base`/`D.base`; `cmd_day` rewritten to call `serve_scoped` instead of binding its own socket; unused `server` import removed
- `surfaces/daemon.py` - `STUDY_GET_RE`/`DAY_GET_RE`/`DAY_SAVE_RE`/`DAY_OPEN_RE`, `handle_study_get`, `_plan_day_state`, `handle_day_get`, `handle_day_index`, `handle_day_save`, `handle_day_open`, `DAY_AMBIGUOUS_BODY`, `day_states`/`day_extra` handler-class attributes, `serve_scoped()`; `handle_quiz_answer` gained `reveal`/`progress` support off the session dict; `cmd_daemon` slimmed to call `serve_scoped`
- `surfaces/quiz.py` - `cmd_serve` rewritten to call `daemon.serve_scoped()`; deleted its handler class, the `server` import and the now-unused `explain_payload` import
- `tests/daemon_roundtrip.py` - `write_today_plan()` helper plus 11 new checks (study route, study/cmd_study equality, day route, single-plan/ambiguous `GET /day`, two-plan save isolation, out-of-range open)
- `tests/serve_roundtrip.py` - `served_post_path()` helper; POST target resolved off the served page instead of assumed to be `<url>answer`
- `tests/day_roundtrip.py` - save target resolved as `<url>day/<stem>/save` instead of `<url>save`
- `tests/evidence_roundtrip.py` - `start_serve()`/`served_post_path()`/`test_day_ticks_are_events()` updated to the same bank-/plan-scoped path convention (not in this plan's `files_modified`, but broken by Task 2's own change -- see Deviations)

## Decisions Made
- `day_state()`/`day_render()`/`apply_day_post()` take an explicit `iso` rather than computing "today" internally, and `day_extra` threads `iso` through `serve_scoped`'s `extra` -- caught while smoke-testing `itembank day --date`: without this, backfilling a missed day would silently stop working the moment `day` became a daemon launch, since the daemon's lazy per-plan state build has no CLI flag to read a date from.
- `handle_quiz_answer` reads `reveal`/`progress` off the bank's session dict (both defaulting to off) rather than being parameterised at the route-table level: a general `itembank daemon <dir>` launch serving several banks is unaffected (both flags absent), while `itembank serve`'s scoped launch regains its exact `--reveal` behaviour and its "d/N answered, saved" progress line by setting both in `extra`.
- `serve_scoped`'s `on_bound(port)` callback exists specifically so `cmd_day`'s `--lan` phone-address line (which needs the actual bound port) prints in the same position the pre-refactor code held it in -- after "url", before the final "Ticks are saved..." note.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `_plan_day_state` ignored `itembank day --date`, silently breaking backfill**
- **Found during:** Task 2, while smoke-testing `itembank day ... --date 2026-01-06` end to end after the `serve_scoped` refactor
- **Issue:** The daemon's lazily-built per-plan `day_state` always computed `iso` from `datetime.date.today()`, with no way for `cmd_day`'s `--date` flag to reach it -- a backfill request silently served today's (empty) row instead of the requested date.
- **Fix:** Added an `iso` key to `day_extra`'s per-stem override dict; `cmd_day` now passes its resolved `iso` through, and `_plan_day_state` reads `override.get("iso")` before falling back to today.
- **Files modified:** surfaces/daemon.py, surfaces/day.py
- **Verification:** Re-ran `itembank day fixtures/sample_plan.md --date 2026-01-06 --log <tmp>` and curled `/day/sample_plan` directly -- the plan's `2026-01-06` task text ("ch 2 first half") now appears; `tests/day_roundtrip.py`'s `check_server()` (which also depends on `--date`) passes.
- **Committed in:** `f92a1cf` (Task 2 commit)

**2. [Rule 1 - Bug] `tests/evidence_roundtrip.py`'s serve/day helpers assumed the pre-consolidation URL shape**
- **Found during:** Task 2, running the full `for t in tests/*.py` suite after `cmd_serve`/`cmd_day` became daemon launches
- **Issue:** `tests/evidence_roundtrip.py` (not in this plan's `files_modified`) carries its own duplicated `start_serve`/`post_answer` and day-server helpers (documented in-file as deliberate duplication rather than an import from `serve_roundtrip.py`). Both assumed the served process's root URL was the quiz/day page and that `/answer`/`/save` were bare paths -- exactly the assumption Task 2's consolidation broke.
- **Fix:** Applied the same fix as `tests/serve_roundtrip.py`/`tests/day_roundtrip.py`: `start_serve` now returns the bank-scoped `/quiz/<stem>` URL, a `served_post_path()` helper resolves the answer target off the served page, and the day test builds `/day/<stem>/save` from the plan's own stem. No assertion removed or weakened.
- **Files modified:** tests/evidence_roundtrip.py
- **Verification:** `python tests/evidence_roundtrip.py` passes (was failing with "could not find the item payload in the served page" before the fix).
- **Committed in:** `f92a1cf` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 bugs, both found and fixed before commit, both directly caused by this plan's own Task 2 change -- not scope creep)
**Impact on plan:** Both fixes were necessary for the plan's own verification block (`for t in tests/*.py; do python "$t" || exit 1; done`) to pass, and both are corrections to behaviour Task 2's refactor itself changed.

## Issues Encountered
None beyond the two auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `daemon.serve_scoped()` is now the one bind/print/serve_forever tail available to any future scoped launch (plans 02-04/02-05/02-06 for the report/API/settings/LAN-probe surfaces)
- `_plan_day_state`'s `day_extra` override mechanism and `handle_quiz_answer`'s session-dict `reveal`/`progress` flags are the established seams for a scoped launch to pin per-launch state onto the shared `DaemonHandler` class without widening the route handlers themselves
- No blockers.

---
*Phase: 02-daemon-consolidation-settings-foundation*
*Completed: 2026-08-07*

## Self-Check: PASSED

All modified files (`surfaces/study.py`, `surfaces/day.py`, `surfaces/daemon.py`, `surfaces/quiz.py`, `tests/daemon_roundtrip.py`, `tests/serve_roundtrip.py`, `tests/day_roundtrip.py`, `tests/evidence_roundtrip.py`) and both task commits (`6d098fb`, `f92a1cf`) verified present on disk / in git log.
