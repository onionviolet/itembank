---
phase: 02-daemon-consolidation-settings-foundation
plan: 06
subsystem: daemon
tags: [http.server, socketserver, urllib, settings, lan]

# Dependency graph
requires:
  - phase: 02-daemon-consolidation-settings-foundation
    provides: "02-01: MARKER_PATH/handle_marker, the Daemon class, DaemonHandler, serve_scoped's own binding shape; 02-02: serve_scoped's on_bound hook and extra-carried state; 02-03: schemas/settings.schema.json's daemon group and surfaces/settings.load_settings(); 02-04/02-05: the /api/* and /report handlers this plan's --lan re-test replays hostile cases against"
provides:
  - "surfaces/daemon.py: probe(port, host, timeout) -- the positive-identification-only marker check"
  - "surfaces/daemon.py: start_server(handler_cls, port, host, no_open) -- the three-case detect-and-attach startup path, returning (srv, bound_port, fell_back)"
  - "surfaces/daemon.py: ALL_INTERFACES constant -- the one place that decides the bind host"
  - "surfaces/daemon.py: serve_scoped(..., srv=None) -- accepts a pre-bound server from start_server() without re-binding"
  - "surfaces/cli.py: --lan on the daemon subcommand; --port defaults to None so itembank.json's daemon.port can supply it"
  - "cmd_daemon reads daemon.port/daemon.lan from itembank.json via settings.load_settings(), with --port/--lan overriding"
  - "tests/daemon_roundtrip.py: free_port(), start_decoy(), run_daemon_once(), start_daemon(..., force_port_zero=) -- reusable by any later plan needing a known-port daemon launch or a false-positive decoy listener"
affects: [Phase 4 (SURF-02/05-09 surface redesign, which serves from this same daemon), any future plan launching itembank daemon programmatically]

actuals:
  tokens: 6839
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "probe() mirrors day.anki_read()'s blanket except-Exception-means-absent shape: a timeout, refused connection, non-JSON body, or wrong-shaped JSON all mean not-us, never assume-us -- the same degrade-safely convention extended from Anki reachability to itembank-instance reachability"
    - "start_server() branches on the *kind* of OSError (errno.EACCES / winerror 10013 vs. everything else) before ever probing, so the Windows reserved-port case server.bind() already documents costs zero network calls"
    - "ALL_INTERFACES is the one module-level constant every bind-host decision in daemon.py reads, checked structurally (exactly one literal '0.0.0.0' in the whole module) rather than trusted as a claim in prose"
    - "serve_scoped() now accepts an already-bound srv, so start_server()'s probe outcome and serve_scoped()'s shared banner/browser/serve_forever tail compose without either one re-implementing the other's job"

key-files:
  created: []
  modified:
    - surfaces/daemon.py
    - surfaces/cli.py
    - tests/daemon_roundtrip.py

key-decisions:
  - "Task 1 discovered (not merely followed) that Daemon's allow_reuse_address=True completely defeats the detect-and-attach probe on Windows: SO_REUSEADDR on Windows lets a second process silently bind an already-listening port instead of raising OSError, unlike POSIX where it only bypasses TIME_WAIT. Fixed by removing the override (leaving the stdlib default False) -- Rule 1, a bug this plan's own new behavior surfaced, not a design choice up for debate."
  - "Followed the plan's literal instruction to call server.bind() (a plain, non-threaded socketserver.TCPServer) for both fallback branches inside start_server(), rather than re-binding the ThreadingMixIn Daemon class a second time. This means the two rare fallback paths (reserved port, unrelated squatter) serve without ThreadingMixIn until the daemon is restarted; the common no-fallback-needed path keeps it. Acceptance criteria explicitly assert 'server.bind' appears in start_server's source, matching RESEARCH.md's own worked example -- this is the plan's chosen trade, not a deviation."
  - "The 'port unavailable, using N instead' notice the plan calls for is satisfied by server.bind()'s own existing print plus serve_scoped()'s always-printed url line (which names the port actually bound), rather than a second redundant line from cmd_daemon's on_bound callback -- avoids printing the same fact twice under a fallback."
  - "--lan's store_true flag has no explicit-false counterpart (no --no-lan), so 'the flag was explicitly given' collapses to 'a.lan is True'; a.lan False (whether omitted or simply absent, there is no way to distinguish) always falls through to itembank.json's daemon.lan default -- consistent with the plan's own truths, which only ever describe --lan as a way to turn LAN mode ON, never off from the CLI."

requirements-completed: [SURF-03, SURF-04]

coverage:
  - id: D1
    description: "A second itembank daemon on a port a first daemon holds attaches instead of binding: prints the already-running line, exits 0, and binds no second socket"
    requirement: SURF-03
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_startup_second_attaches"
        status: pass
    human_judgment: false
  - id: D2
    description: "probe() identifies a real itembank daemon by its exact marker shape and never a stranger -- a closed port, a plain-text 200, and a JSON body missing the itembank field all read False"
    requirement: SURF-03
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_probe_closed_port,check_probe_non_itembank_listener,check_probe_real_daemon"
        status: pass
    human_judgment: false
  - id: D3
    description: "A reserved or permission-denied bind failure (errno.EACCES / Windows winerror 10013) skips the probe entirely and falls straight to the free-port fallback"
    requirement: SURF-03
    verification:
      - kind: unit
        ref: "plan's own acceptance criterion: python -c \"...src=inspect.getsource(daemon.start_server);assert 'EACCES' in src and 'winerror' in src...\""
        status: pass
    human_judgment: true
    rationale: "Reliably reproducing a genuine EACCES/WinError 10013 bind failure cross-platform inside an automated test (without mocking socketserver.TCPServer's constructor) was not attempted; the branch is proven present and unconditional by source inspection, matching the plan's own acceptance criterion, but the OS-refusal path itself is not exercised end-to-end by tests/daemon_roundtrip.py."
  - id: D4
    description: "A configured port held by an unrelated (non-itembank) process falls back to a free port and serves successfully there, rather than hard-failing startup"
    requirement: SURF-03
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_startup_squatter_falls_back"
        status: pass
    human_judgment: false
  - id: D5
    description: "--lan binds all interfaces; the banner carries both the loopback URL and a lan_address()-derived phone URL, and the widened bind is reachable from this machine"
    requirement: SURF-03
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_startup_lan_binds_all"
        status: pass
      - kind: manual_procedural
        ref: "02-VALIDATION.md Manual-Only Verifications: a phone on the same wifi opens the printed --lan URL"
        status: unknown
    human_judgment: true
    rationale: "Cross-device reachability from a second physical phone cannot be exercised by a loopback-only automated test, carried as this plan's own documented manual-only verification."
  - id: D6
    description: "Without --lan, and with the shipped itembank.json, the daemon binds loopback only; daemon.lan ships false"
    requirement: SURF-03
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_startup_loopback_by_default"
        status: pass
      - kind: unit
        ref: "plan's own acceptance criterion: python -c \"...assert d['daemon']['lan'] is False...\""
        status: pass
    human_judgment: false
  - id: D7
    description: "The daemon's port and LAN default come from itembank.json's daemon group via settings.load_settings(), with an explicit --port/--lan on the command line overriding the file"
    requirement: SURF-03
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_settings_driven_port"
        status: pass
    human_judgment: false
  - id: D8
    description: "The bank stem allowlist, session-id lookup, and path-shaped-field rejection behave identically whether the daemon bound loopback or all interfaces"
    requirement: SURF-03
    verification:
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_lan_path_validation_unchanged"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-07
status: complete
---

# Phase 02 Plan 06: Detect-and-Attach Daemon Startup, `--lan`, and Live Settings Summary

**`surfaces/daemon.py` gained `probe()`/`start_server()`, a three-case detect-and-attach startup (attach, reserved-port fallback, squatted-port fallback) that closes SURF-03, plus `--lan` and settings-driven port/LAN defaults read from `itembank.json`'s `daemon` group -- and fixed a Windows-only bug (`allow_reuse_address=True`) that would have silently defeated the whole mechanism.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- **`probe(port, host, timeout)`** -- a GET against `MARKER_PATH` that returns `True` only when the body parses as JSON with an `itembank` field that is exactly `True`; every other outcome (closed port, timeout, refused connection, non-JSON body, wrong-shaped JSON) returns `False` via one blanket `except Exception`, mirroring `day.anki_read()`'s own degrade-safely shape.
- **`start_server(handler_cls, port, host, no_open)`** -- tries binding `Daemon` directly first; on `OSError`, branches on the *kind* of failure: `errno.EACCES`/Windows `winerror` 10013 skips the probe entirely (nothing is listening, probing would only burn a timeout on exactly the platform this project runs on); a positive `probe()` prints the already-running line, opens a browser unless `--no-open`, and exits 0; everything else falls back to `server.bind()`'s existing free-port logic, reused rather than reimplemented a third time.
- **A real bug found and fixed**: `Daemon`'s `allow_reuse_address = True` let a second process silently bind an already-listening port on Windows (`SO_REUSEADDR`'s semantics differ from POSIX there), which would have made `start_server()`'s whole detect-and-attach path a no-op -- the very platform CLAUDE.md and `server.bind()`'s own docstring already call out. Removed; `ThreadingMixIn` needed no help from it.
- **`--lan`** on the `daemon` subcommand binds `0.0.0.0`, and the banner prints both the loopback URL and a `day.lan_address()`-derived phone line, plus an explicit one-line exposure notice (no accounts, no authentication) whenever LAN mode is on.
- **`cmd_daemon` reads `itembank.json`'s `daemon.port`/`daemon.lan`** through `settings.load_settings(root)`, with `--port`/`--lan` on the command line overriding -- `--port`'s argparse default changed to `None` (never a hardcoded 8730) so "omitted" is distinguishable from "matches the file's own value".
- **`ALL_INTERFACES = "0.0.0.0"`** is now the one place in `daemon.py` that decides the bind host; `serve_scoped()`'s display-host filter reads the same constant, checked structurally (exactly one literal `"0.0.0.0"` in the whole module).
- **`serve_scoped()` gained an optional `srv` parameter** so `cmd_daemon` can hand it an already-bound (or already-fallen-back) server from `start_server()` without a second bind; `cmd_serve`/`cmd_day` are unaffected and keep binding through `_bind()` exactly as before.
- **`tests/daemon_roundtrip.py`** gained 9 new checks (46 total) plus `free_port()`, `start_decoy()`, and `run_daemon_once()` helpers, and `start_daemon()` gained a `force_port_zero=False` escape hatch for the settings-driven-port case.

## Task Commits

Each task was committed atomically:

1. **Task 1: Detect-and-attach, the three bind-failure cases, and `--lan`** -- `4c18678` (feat)
2. **Task 2: Prove the three bind-failure cases and the loopback default** -- `aad645b` (test)

_Note: this plan's docs-completion commit (SUMMARY.md/STATE.md/ROADMAP.md/REQUIREMENTS.md) follows this file's creation, per the execute-plan workflow._

## Files Created/Modified

- `surfaces/daemon.py` -- `ALL_INTERFACES`, `probe()`, `start_server()`; `Daemon.allow_reuse_address` removed (bug fix); `_bind()`'s docstring extended to note it now serves only `cmd_serve`/`cmd_day`; `serve_scoped()` gained `srv=None`; `cmd_daemon` reads `settings.load_settings()`, calls `start_server()`, and prints the `--lan` phone/exposure lines via `on_bound`
- `surfaces/cli.py` -- `daemon` subparser: `--port` default changed to `None`, `--lan` added (`store_true`)
- `tests/daemon_roundtrip.py` -- `free_port()`, `start_decoy()`, `run_daemon_once()`; `start_daemon()` gained `force_port_zero`; 9 new checks: `check_probe_closed_port`, `check_probe_non_itembank_listener`, `check_probe_real_daemon`, `check_startup_second_attaches`, `check_startup_squatter_falls_back`, `check_startup_loopback_by_default`, `check_startup_lan_binds_all`, `check_lan_path_validation_unchanged`, `check_settings_driven_port`

## Decisions Made

See `key-decisions` above -- summarized: (1) the `allow_reuse_address` fix is a Rule 1 bug fix this plan's own new probe surfaced, not a design choice; (2) `start_server()`'s fallback branches call the plain, non-threaded `server.bind()` exactly as the plan's action text and RESEARCH.md's worked example both specify, trading `ThreadingMixIn` on the two rare fallback paths for reusing `server.bind()`'s logic rather than re-implementing it a third time; (3) the "port unavailable, using N instead" notice comes from `server.bind()`'s own existing print plus `serve_scoped()`'s always-printed `url` line, not a redundant second message; (4) `--lan` has no CLI-level "off" counterpart, so "explicitly given" collapses to `a.lan is True`, with `False` always deferring to the settings file.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `Daemon.allow_reuse_address = True` silently defeats detect-and-attach on Windows**
- **Found during:** Task 1, while manually verifying the second-start-attaches scenario before writing its automated test
- **Issue:** `Daemon` (added in plan 02-01) set `allow_reuse_address = True`. On Windows, `SO_REUSEADDR` permits a second process to bind a port another process is already actively listening on, instead of merely bypassing TIME_WAIT the way it does on POSIX. With this set, `start_server()`'s first `Daemon((host, port), handler_cls)` attempt never raised `OSError` when a first daemon already held the port -- it just silently bound a second listener, so the probe branch was never reached at all. This is exactly the bug D-02 ("no second daemon ever binds") exists to prevent, on exactly the platform this project runs on.
- **Fix:** Removed the `allow_reuse_address = True` override, leaving the stdlib default (`False`). `ThreadingMixIn` does not need `SO_REUSEADDR` to serve concurrently; that flag is unrelated to request-handling concurrency.
- **Files modified:** surfaces/daemon.py
- **Verification:** Manual repro before the fix (two `Daemon` instances bound the same port with no error); after the fix, a second `itembank daemon` on a held port raises `OSError` and attaches correctly. `tests/daemon_roundtrip.py#check_startup_second_attaches` and `#check_concurrency` (pre-existing, unaffected) both pass. Full suite green.
- **Committed in:** `4c18678` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1)
**Impact on plan:** Necessary for the plan's own core deliverable (D-02's detect-and-attach) to function at all on this project's target platform. No scope creep -- the fix is a one-line attribute removal plus documentation of why.

## Issues Encountered

None beyond the one auto-fixed deviation above.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- SURF-03 and SURF-04 are both requirement-complete. The phase's full route/CLI inventory, `/api/*` session routes, `/report` page, and now the detect-and-attach startup path are all proven by `tests/daemon_roundtrip.py`'s 46 checks.
- `probe()`/`start_server()`/`ALL_INTERFACES` are reusable by any later phase that needs to launch or detect an itembank daemon programmatically (e.g. a future auditor or scheduler that wants to check "is a daemon already up" before doing its own work).
- `free_port()`/`start_decoy()`/`run_daemon_once()` in `tests/daemon_roundtrip.py` are exported at module level the same way `start_daemon()` already was, for any later plan needing a known-port daemon launch or a false-positive decoy listener.
- **Manual-only verification still outstanding** (02-VALIDATION.md, D5 above): a phone on the same wifi opening the printed `--lan` URL. This is recorded as a manual check, not automated, and not exercised in this session.
- No blockers. This was the last plan in Phase 02 (wave 5 of 5).

---
*Phase: 02-daemon-consolidation-settings-foundation*
*Completed: 2026-08-07*

## Self-Check: PASSED

All modified files (`surfaces/daemon.py`, `surfaces/cli.py`, `tests/daemon_roundtrip.py`) and this SUMMARY.md verified present on disk; both task commits (`4c18678`, `aad645b`) verified present in `git log`.
