---
phase: 02-daemon-consolidation-settings-foundation
plan: 01
subsystem: api
tags: [http.server, socketserver, threading-mixin, route-table, evidence]

# Dependency graph
requires:
  - phase: 01-evidence-foundation
    provides: evidence.append_event()/response_event()/render_attempt_md(), the one writer and renderer every response event and attempt file goes through
provides:
  - "surfaces/daemon.py: one process, one port, an ordered route table (ROUTES), a machine-checkable route-to-CLI inventory (ROUTE_CLI), and cmd_daemon"
  - "scan_dir(root): the startup-built bank/day-plan allowlist every daemon route resolves a client-supplied stem through, with deterministic stem-collision handling"
  - "quiz.record_answer(): the score-then-append-then-render function cmd_serve and the daemon both call, so the CLI path and the daemon path can never diverge in how a response is scored or recorded"
  - "quiz_page.py's __POST__ placeholder + page_for(post_path=...): lets one process serve more than one bank, each posting its answer to its own bank-scoped path"
affects: [02-02-daemon-report-and-settings, 02-04, 02-05, 02-06-daemon-lan-and-probe]

actuals:
  tokens: 9638
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "First-match-wins ordered route table (ROUTES) over server.Handler, with fixed literal routes ordered before stem-parameterised routes so a bank named report/day/api can never shadow a fixed route"
    - "Route-to-CLI inventory (ROUTE_CLI) asserted equal to ROUTES' key set at test time, so a route added without a CLI equivalent fails the build instead of shipping silently (SURF-04)"
    - "Startup-built stem allowlist (scan_dir) resolved server-side; a route handler never joins a client-supplied string onto a filesystem path"

key-files:
  created:
    - surfaces/daemon.py
    - tests/daemon_roundtrip.py
  modified:
    - surfaces/quiz.py
    - surfaces/quiz_page.py
    - surfaces/cli.py

key-decisions:
  - "cmd_daemon opens one session (session_id/log/attempt-file path) per bank at startup, stored on DaemonHandler.sessions[stem] -- generalizing cmd_serve's single-session-per-process shape to one session per served bank rather than one session for the whole daemon"
  - "Daemon binds via a small _bind() helper in daemon.py that mirrors server.bind()'s free-port fallback logic against the Daemon (ThreadingMixIn+TCPServer) class, instead of modifying server.bind() itself, which is outside this plan's files_modified list"
  - "scan_dir() sorts candidates by (stem.lower(), full_path) rather than by stem alone, so a stem collision's winner is deterministic across restarts even when the filesystem's directory-enumeration order is not"
  - "cmd_serve's record() closure preserves the '(already recorded)' progress note by comparing the evidence log's byte size before/after calling quiz.record_answer(), rather than widening record_answer()'s return contract beyond the score the plan specifies"

requirements-completed: [SURF-01, SURF-04]

coverage:
  - id: D1
    description: "One daemon on one port serves the index (GET /) and one bank's quiz (GET /quiz/<stem>, POST /quiz/<stem>/answer), plus the GET /__itembank__ identifying marker"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_index_populated,check_index_order,check_index_empty,check_index_malformed_tolerated,check_index_no_truncation,check_fixed_routes_not_shadowed"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every verdict comes from runtime.score_response() and every recorded response from evidence.append_event(), both reached only through quiz.record_answer() -- no second scorer or writer in daemon.py"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_answer_scoring,check_quiz_no_key"
        status: pass
      - kind: unit
        ref: "python -c \"...'canonical_response' not in src and 'canonical_key' not in src\" (plan acceptance criterion)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two banks served from the same daemon never cross-contaminate: an answer posted to bank B's path is recorded against bank B only, reading the POST target off the served page rather than assuming the URL convention"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_two_bank_isolation"
        status: pass
    human_judgment: false
  - id: D4
    description: "Stem collisions resolve deterministically (first in case-insensitive stem order wins) with a named startup collision line; fixed routes (/, /__itembank__) are never shadowed by a colliding bank stem"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_stem_collision,check_fixed_routes_not_shadowed"
        status: pass
    human_judgment: false
  - id: D5
    description: "The daemon is concurrent (socketserver.ThreadingMixIn) so one slow route cannot stall every other in-flight request"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_concurrency"
        status: pass
    human_judgment: false
  - id: D6
    description: "Every registered route has a CLI-command equivalent, checked as a machine-verifiable inventory (ROUTE_CLI) rather than trusted as documentation"
    requirement: SURF-04
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_route_cli_inventory"
        status: pass
    human_judgment: false
  - id: D7
    description: "The / index follows 02-UI-SPEC.md's copy, spacing/typography/color contract and empty state, with no singular/plural branch and no truncation of row link text"
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_index_populated,check_index_empty,check_index_no_truncation"
        status: pass
    human_judgment: true
    rationale: "Automated checks confirm the required copy strings and the absence of nowrap/ellipsis CSS, but the actual visual rendering (spacing rhythm, color contrast, wrap behavior at 20+ rows) was not screenshotted this session -- 02-UI-SPEC.md itself holds this as a 🧪 backstop item pending a UAT pass."

duration: 55min
completed: 2026-08-07
status: complete
---

# Phase 02 Plan 01: Daemon Tracer Summary

**`surfaces/daemon.py` stands up one `socketserver.ThreadingMixIn` process on one port serving the `/` index and one bank's full quiz-and-score loop through a first-match-wins route table, proven end-to-end by a new 13-check `tests/daemon_roundtrip.py` harness.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-08-07T16:19:00Z (approx, per STATE.md session start)
- **Completed:** 2026-08-07T17:14:28Z
- **Tasks:** 2
- **Files modified:** 5 (1 new module, 1 new test, 3 existing files touched additively)

## Accomplishments
- New `surfaces/daemon.py`: `scan_dir()` (the startup bank/day-plan allowlist), an ordered `ROUTES` table, the `ROUTE_CLI` inventory, `DaemonHandler`/`Daemon` (threading), the index/marker/quiz-get/quiz-answer route handlers, and `cmd_daemon`
- `surfaces/quiz.py` gained `record_answer()` (factored out of `cmd_serve`'s `record()` closure) and `page_for(post_path=...)`, so the CLI `serve` path and the new daemon path score and record through exactly the same function
- `surfaces/quiz_page.py`'s hardcoded `/answer` POST target became the `__POST__` placeholder, letting one process serve more than one bank without cross-wiring their answer routes
- `itembank daemon <dir>` registered in `surfaces/cli.py`, mirroring `serve`'s subparser shape
- `tests/daemon_roundtrip.py`: a new Wave 0 integration harness with 13 checks (index populated/ordered/empty/malformed-tolerant/no-truncation, key-free quiz page, answer scoring, cross-bank isolation, stem collisions, fixed-route shadowing, unknown-stem 404s, concurrency, route/CLI inventory) plus a reusable `start_daemon()` helper exported for plans 02-02/02-04/02-05/02-06

## Task Commits

Each task was committed atomically:

1. **Task 1: One daemon, one port -- index and one bank's quiz, wired end to end** - `4678fb0` (feat)
2. **Task 2: The Wave 0 roundtrip harness and the tracer's end-to-end assertions** - `9ef16ba` (test)

_Note: this plan's docs-completion commit (SUMMARY.md/STATE.md/ROADMAP.md/REQUIREMENTS.md) follows this file's creation, per the execute-plan workflow._

## Files Created/Modified
- `surfaces/daemon.py` - new module: `MARKER_PATH`, `scan_dir()`, `ROUTES`, `ROUTE_CLI`, `DaemonHandler`, `Daemon`, `INDEX_TEMPLATE`, the four route handlers, `cmd_daemon`
- `surfaces/quiz.py` - `page_for()` gained `post_path`; `record_answer()` factored out and reused by `cmd_serve`'s closure
- `surfaces/quiz_page.py` - hardcoded `/answer` fetch target replaced with `__POST__`
- `surfaces/cli.py` - registers the `daemon` subcommand (`dir`, `--port` default 8730, `--no-open`, `--force`)
- `tests/daemon_roundtrip.py` - new Wave 0 integration harness (13 checks)

## Decisions Made
- Session bookkeeping (session_id/log/attempt-file) is opened per bank at daemon startup rather than per request or globally for the whole daemon -- one bank's sitting has its own identity even though several banks may share one `_evidence/evidence.jsonl` file in the same directory (isolation is by the `bank` field on each event, matching the existing evidence design, not by a separate log file per bank).
- Binding uses a small `_bind()` helper inside `daemon.py` that duplicates `server.bind()`'s free-port-fallback *logic* against the `Daemon` server class, rather than modifying `server.py` (not in this plan's `files_modified`).
- Stem-collision winner selection sorts candidates by `(stem.lower(), full_path)`, not stem alone, so restart-to-restart determinism holds even where OS directory enumeration order is not guaranteed stable.
- `cmd_serve`'s "(already recorded)" progress note is now derived from the evidence log's byte size before/after calling `record_answer()`, preserving the CLI's existing progress-line behavior without widening `record_answer()`'s return contract past what the plan specifies (score only).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The two-bank isolation test initially had no teeth against the `__POST__` regression it exists to guard**
- **Found during:** Task 2, while manually verifying the plan's own acceptance criterion ("deleting the `__POST__` substitution ... makes it exit non-zero")
- **Issue:** The first draft of `check_two_bank_isolation`/`check_answer_scoring` posted directly to the assumed `/quiz/<stem>/answer` URL convention rather than reading the POST target off the served page's own script. Removing the `__POST__` substitution left the test green, because the test bypassed the placeholder entirely.
- **Fix:** Added `served_post_path(quiz_url, page)`, which scrapes the `fetch("...")` target from the served page and resolves it via `urllib.parse.urljoin`; both checks now post through that resolved URL instead of a guessed one. Re-verified: with `__POST__` substitution removed, the test now fails with an unhandled `HTTPError: 404` (non-zero exit); restored, it passes cleanly.
- **Files modified:** tests/daemon_roundtrip.py
- **Verification:** Manually reverted the `.replace("__POST__", post_path)` line in `surfaces/quiz.py`, ran `python tests/daemon_roundtrip.py` (exit 1, `HTTPError: 404`), restored the file, confirmed `diff` showed no residual change, re-ran the test (exit 0).
- **Committed in:** `9ef16ba` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug, found and fixed before commit -- not a separate follow-up)
**Impact on plan:** No scope creep; the fix strengthens exactly the acceptance criterion the plan itself specified as a self-check ("the two-bank isolation check has teeth").

## Issues Encountered
- Sending `SIGINT` to the daemon subprocess via `kill -INT` under Git Bash on Windows did not visibly print the "stopped." closing line before the process was force-terminated in a manual smoke test. This is the same `try/except KeyboardInterrupt` pattern `cmd_serve`/`cmd_day` already use and is a known Windows/Git-Bash signal-delivery quirk, not a regression introduced here; no test in `tests/daemon_roundtrip.py` depends on this path, and `proc.terminate()` (used throughout the harness) reliably tears the daemon down.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The route table, `ROUTE_CLI` inventory, `DaemonHandler`/`Daemon` classes, and `tests/daemon_roundtrip.py`'s `start_daemon()` helper are in place for plans 02-02 (report/settings), 02-04, 02-05, and 02-06 (LAN/probe) to extend without re-deriving the harness or the dispatch shape.
- `/study/<stem>` and the day-view link on the `/` index are real links per 02-UI-SPEC.md but 404 until plan 02-02 wires those routes in -- expected and documented in-plan, not a defect of this plan.
- No blockers.

---
*Phase: 02-daemon-consolidation-settings-foundation*
*Completed: 2026-08-07*

## Self-Check: PASSED

All created files (`surfaces/daemon.py`, `tests/daemon_roundtrip.py`, `surfaces/quiz.py`, `surfaces/quiz_page.py`, `surfaces/cli.py`, this SUMMARY.md) and both task commits (`4678fb0`, `9ef16ba`) verified present on disk / in git log.
