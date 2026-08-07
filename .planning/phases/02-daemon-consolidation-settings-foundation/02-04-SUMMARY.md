---
phase: 02-daemon-consolidation-settings-foundation
plan: 04
subsystem: api
tags: [http.server, json-api, session, evidence, daemon]

# Dependency graph
requires:
  - phase: 02-daemon-consolidation-settings-foundation
    provides: "02-01/02-02: surfaces/daemon.py's route table (ROUTES/ROUTE_CLI), DaemonHandler/Daemon, scan_dir()'s bank/plan allowlist, and tests/daemon_roundtrip.py's start_daemon() helper"
provides:
  - "surfaces/session.py: do_start/do_next/do_submit/do_report -- the four session command bodies as callable functions returning a dict, with cmd_start/cmd_next/cmd_submit/cmd_report reduced to thin print wrappers over them"
  - "surfaces/daemon.py: session_index(root) -- the lazily-built {session_id: path} allowlist scanned from _attempts/, D-03's bank allowlist extended to session identifiers"
  - "surfaces/daemon.py: POST /api/start, /api/next, /api/submit, /api/report -- the four session routes, registered as API_ROUTES (exactly four, asserted) and wired into ROUTES/ROUTE_CLI"
  - "The SystemExit/Exception containment pattern every /api/* handler applies around a reused session.do_* call, so a routine session error (lint errors, exhausted objective, a session already complete) is a 4xx rather than a dead daemon"
affects: [02-05, 02-06, Phase 4 (SURF-02, browser-holds-no-key rework)]

actuals:
  tokens: 9356
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "cmd_* / do_* split: do_* takes plain arguments and returns a dict, cmd_* unpacks an argparse Namespace, calls do_*, prints and returns 0 -- the same body callable from a CLI process (where sys.exit() is correct) and from inside a daemon request handler (where it is not)"
    - "except SystemExit as exc: send_error(400, str(exc.code)) paired with except Exception as exc: send_error(500, str(exc)), in that order, around every reused command body -- SystemExit derives from BaseException, so the except-Exception-only pattern the quiz/day handlers already used would not have caught it"
    - "Identifier-only addressing on /api/*: bank resolves through the same stem dict the GET routes use, session_id through a lazily-built session_index(root) scan of _attempts/ -- neither is ever joined to a path, and a client-supplied 'session'/'bank_path'/'out' field is refused with 400 naming the field rather than silently accepted"

key-files:
  created: []
  modified:
    - surfaces/session.py
    - surfaces/daemon.py
    - tests/daemon_roundtrip.py
    - tests/agent_roundtrip.py

key-decisions:
  - "do_submit(session_file, answer, confidence) calls normalize_answer(answer) itself rather than expecting an already-normalized value, so the same function works whether answer arrives as a raw CLI string (cmd_submit's a.answer) or as an already-JSON-native list/dict/string from an /api/submit body"
  - "handle_api_start computes 'out' server-side under <root>/_attempts/session_<uuid>.json and never reads it from the request body -- the client cannot name where its own session file is written"
  - "session_index(root) is built lazily per API request (one _attempts/ directory listing) rather than cached at daemon startup, so a session created by a concurrent /api/start or by an itembank start run in another terminal is addressable immediately"
  - "API_FORBIDDEN_FIELDS (session, bank_path, out) is checked identically across all four handlers via one api_read_json() helper, rather than per-handler ad hoc checks, so the raw-path surface D-03's bank allowlist closed cannot be reintroduced by a client guessing the old CLI Namespace field name"

requirements-completed: [SURF-01, SURF-04]

coverage:
  - id: D1
    description: "An agent can drive a whole sitting -- start, next, submit, report -- over POST /api/* against the same runtime calls surfaces/session.py already makes from the shell, addressed by opaque identifiers rather than filesystem paths"
    requirement: SURF-04
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_api_sitting"
        status: pass
    human_judgment: false
  - id: D2
    description: "POST /api/submit and itembank submit against the same session and the same answer produce the same score and the same evidence status, because both reach evidence.append_event() through the one shared session.do_submit function"
    requirement: SURF-04
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_api_cli_parity"
        status: pass
      - kind: unit
        ref: "tests/agent_roundtrip.py#check_cli_reaches_shared_do_functions"
        status: pass
    human_judgment: false
  - id: D3
    description: "A routine error condition that exits the CLI (lint errors, an exhausted objective, a session already complete) returns a 4xx from the daemon and leaves every other route and every other bank served"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_api_survives_routine_error,check_api_bank_not_found"
        status: pass
      - kind: unit
        ref: "python -c \"...src.count('except SystemExit')>=4...\" (plan acceptance criterion)"
        status: pass
    human_judgment: false
  - id: D4
    description: "/api/* addresses a session by its opaque session_id (resolved through session_index) and a bank by the stem allowlist the GET routes use; a client-supplied filesystem path in either field is a 4xx and reaches no file"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_api_reject_path_fields,check_api_start_traversal"
        status: pass
      - kind: unit
        ref: "python -c \"...'read_session' not in src and 'write_session' not in src...\" (plan acceptance criterion)"
        status: pass
    human_judgment: false
  - id: D5
    description: "A session or bank value naming a path outside the served directory (absolute, or with parent-directory segments) returns 4xx and causes no file read, no directory creation and no file write"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_api_start_traversal (directory snapshot before/after a hostile bank field)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The /api/* route set is exactly four routes in this phase; ROUTE_CLI names start, next, submit and report for them, and the route/CLI inventory equality assertion still holds"
    requirement: SURF-04
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_api_route_scope,check_route_cli_inventory"
        status: pass
      - kind: unit
        ref: "python -c \"...len(daemon.API_ROUTES)==4...\" (plan acceptance criterion)"
        status: pass
    human_judgment: false
  - id: D7
    description: "A malformed JSON body on /api/submit returns 4xx and the daemon stays up"
    requirement: SURF-01
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_api_malformed_json"
        status: pass
    human_judgment: false

duration: 16min
completed: 2026-08-07
status: complete
---

# Phase 02 Plan 04: The Daemon's JSON API Summary

**`surfaces/daemon.py` gained `POST /api/start|next|submit|report`, addressed by opaque `session_id`/bank-stem identifiers over the exact runtime calls `surfaces/session.py` already made, with a `SystemExit`/`Exception` containment pair on every route so a routine CLI-style error is a 4xx rather than a dead daemon.**

## Performance

- **Duration:** 16 min
- **Started:** 2026-08-07T13:08:54-05:00 (approx, per prior plan's completion commit)
- **Completed:** 2026-08-07T13:25:11-05:00
- **Tasks:** 2
- **Files modified:** 4 (2 surface modules, 2 test files)

## Accomplishments
- `surfaces/session.py`'s `cmd_start`/`cmd_next`/`cmd_submit`/`cmd_report` split into `do_start`/`do_next`/`do_submit`/`do_report` (plain-argument functions returning the exact dict each command used to print) plus three-line print wrappers -- every `sys.exit()` call site kept exactly where it was, so CLI behaviour and exit codes stayed byte-identical
- `surfaces/daemon.py` gained `session_index(root)` (a lazily-built `{session_id: path}` allowlist scanned from `_attempts/`), `api_read_json`/`api_reject_path_fields`/`api_session_path` helpers, and the four `handle_api_*` route handlers, registered as `API_ROUTES` (four fixed-literal routes, ahead of every stem pattern) and wired into `ROUTES`/`ROUTE_CLI`
- Every `/api/*` handler resolves `bank` through the same stem dict the GET routes use and `session_id` through `session_index`, never joining either to a filesystem path; a client-supplied `session`/`bank_path`/`out` field is refused with 400 naming the field instead of silently accepted
- Every `/api/*` call into `session.do_*` is wrapped in `except SystemExit as exc: send_error(400, ...)` followed by `except Exception as exc: send_error(500, ...)` -- both required, since `SystemExit` derives from `BaseException` and the existing `except Exception`-only pattern the quiz/day handlers use would not catch it
- `tests/daemon_roundtrip.py` gained 9 new checks (full `/api/*` sitting, same-item resubmit dedupe, the daemon-survives-a-routine-error case with a `GET /` teeth assertion, unscanned-bank 404, path-traversal-in-`bank`-field with a before/after directory snapshot, rejected path-shaped fields, malformed JSON body, and a CLI/API parity check comparing recorded evidence events) plus `check_api_route_scope`; `tests/agent_roundtrip.py` gained a source-inspection assertion that the CLI's four `cmd_*` functions each call their matching `do_*`

## Task Commits

Each task was committed atomically:

1. **Task 1: Factor the four session command bodies into callable functions** - `58e7a9d` (feat)
2. **Task 2: The four `/api/*` routes -- identifier-addressed, and safe to leave running** - `e54bdea` (feat)

_Note: this plan's docs-completion commit (SUMMARY.md/STATE.md/ROADMAP.md/REQUIREMENTS.md) follows this file's creation, per the execute-plan workflow._

## Files Created/Modified
- `surfaces/session.py` - `do_start`/`do_next`/`do_submit`/`do_report` added; `cmd_start`/`cmd_next`/`cmd_submit`/`cmd_report` reduced to Namespace-unpack + print wrappers; module docstring extended to record the split
- `surfaces/daemon.py` - `API_ROUTES`, `SESSION_MODES`, `CONFIDENCE_LEVELS`, `API_FORBIDDEN_FIELDS`, `session_index`, `api_reject_path_fields`, `api_read_json`, `api_session_path`, `handle_api_start`/`handle_api_next`/`handle_api_submit`/`handle_api_report`; `ROUTES`/`ROUTE_CLI` extended; `json` and `surfaces.session` imports added
- `tests/daemon_roundtrip.py` - `agent_roundtrip` import, `api_by_id`/`api_correct_answer`/`snapshot_dirs` helpers, 9 new `check_api_*` functions, `check_api_route_scope`, all registered in `main()`'s checks tuple
- `tests/agent_roundtrip.py` - `check_cli_reaches_shared_do_functions()`, called first in `main()`, asserting each `cmd_*` calls its matching `do_*` via source inspection

## Decisions Made
- `do_submit(session_file, answer, confidence)` calls `normalize_answer(answer)` itself rather than requiring an already-normalized value, so the identical function serves a raw CLI string (`cmd_submit`'s `a.answer`) and an already-JSON-native value from an `/api/submit` body without a second normalization call site.
- `handle_api_start` computes the session output path server-side under `<root>/_attempts/session_<uuid>.json` and never reads an `out` field from the request body -- a client cannot name where its own session file is written, closing off the one place `/api/start` could otherwise have taken a client-supplied path.
- `session_index(root)` is rebuilt on every API request (one `_attempts/` directory listing) rather than cached at daemon startup, so a session created by a concurrent `POST /api/start` or by an `itembank start` run in another terminal is addressable immediately -- the plan's own action block calls this cheap next to the file reads the request is about to do anyway.
- The four forbidden-field names (`session`, `bank_path`, `out`) and the malformed-JSON/non-object-body checks are centralized in one `api_read_json()` helper called first by every handler, rather than duplicated per handler, so the four routes cannot silently drift apart on what counts as a rejected body.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The first draft of the `/api/*` sitting tests used `agent_roundtrip.answer_for()`, which is not guaranteed to be the CORRECT answer for a `table`/`dnd`/`build` item**
- **Found during:** Task 2, first run of the new `check_api_sitting` check
- **Issue:** `agent_roundtrip.answer_for(item)` (imported from `tests/agent_roundtrip.py`) exists to produce a validly-*shaped* response for whatever item type is served, not necessarily a correct one -- for a `dnd`/`table` item it always assigns every row to the first listed category, and for `build` it returns the steps in served (shuffled) order. `check_api_sitting` asserted `score is True`, which failed against `sample_bank.md`'s `q5` (`dnd`) served first under seed 7.
- **Fix:** Added `api_by_id()`/`api_correct_answer()` helpers to `tests/daemon_roundtrip.py` that resolve the real bank item (via `itembank.parse_bank`, already imported) behind an `/api/*` public item payload and delegate to `tests/serve_roundtrip.py`'s existing `correct_answer(q)` (which reads the actual `correct`/`rows`/`steps` key) instead of `agent_roundtrip.answer_for()`. Applied to every new check that needs a genuinely correct answer: `check_api_sitting`, `check_api_duplicate_submit_dedupes`, `check_api_survives_routine_error`, `check_api_cli_parity`.
- **Files modified:** tests/daemon_roundtrip.py
- **Verification:** Re-ran `python tests/daemon_roundtrip.py` -- all 29 checks pass, including `check_api_sitting` scoring `True` against the correct answer for whichever item type seed 7 serves first.
- **Committed in:** `e54bdea` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug in the plan's own new test code, found and fixed before commit -- not a regression in the shipped `surfaces/daemon.py` or `surfaces/session.py` code)
**Impact on plan:** No scope creep; the fix strengthens the plan's own acceptance criterion that the full `/api/*` sitting scores correctly, using the bank's actual answer key rather than a shape-only stand-in.

## Issues Encountered
None beyond the one auto-fixed test-helper issue above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `session_index(root)`, `api_read_json`/`api_reject_path_fields`/`api_session_path`, and the `except SystemExit` / `except Exception` containment pair are now the established pattern for any future route that reuses a `sys.exit()`-raising command body inside the daemon (plans 02-05/02-06).
- `API_ROUTES` is deliberately capped at exactly four routes this phase (asserted by `check_api_route_scope`); Phase 4's SURF-02 browser-holds-no-key rework is the next place `/api/*` widens, not this phase.
- No blockers.

---
*Phase: 02-daemon-consolidation-settings-foundation*
*Completed: 2026-08-07*

## Self-Check: PASSED

All modified files (`surfaces/session.py`, `surfaces/daemon.py`, `tests/daemon_roundtrip.py`, `tests/agent_roundtrip.py`) and both task commits (`58e7a9d`, `e54bdea`) verified present on disk / in git log.
