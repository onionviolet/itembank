---
phase: 13-desktop-packaging-tauri-sidecar
plan: 01
subsystem: infra
tags: [sidecar, daemon, stdout-handshake, per-launch-token, single-instance]

requires:
  - phase: 02-daemon-consolidation-settings-foundation
    provides: the one Daemon/DaemonHandler pair, probe()/start_server() three-case startup, serve_scoped()
  - phase: 02.1-packaging-self-update-interop-export
    provides: the .pyz release artifact the sidecar build wraps
provides:
  - "the sidecar-half of the shell contract: fixed stdout handshake (port/token/version) with shared framing constants"
  - "the per-launch token gate on every route except the probe marker (401), inert on the CLI daemon path"
  - "single-instance attach/refuse: second launch attaches and exits 0, or refuses with the 3.3(e) copy"
  - "the kill-releases-the-port lifecycle proof the shell's job object will rely on"
affects: [13-02, 13-03]

actuals:
  tokens: 10678
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "stdout handshake with shared framing constants (one edit, not a second protocol)"
    - "per-launch token gate keyed off a handler-class attribute; None means the CLI path is byte-compatible"
    - "attach-or-refuse by port liveness: probe True attaches, bound-but-silent refuses, squatter falls back"

key-files:
  created:
    - tests/packaging_shell_roundtrip.py
  modified:
    - surfaces/daemon.py
    - surfaces/cli.py

key-decisions:
  - "Dedicated `itembank sidecar <dir>` command is the single shell entry point; the --sidecar flag on `daemon` was removed (the plan's 'flag/command' wording resolved to the command)."
  - "The token gate covers every route except the probe marker (`/__itembank__`), which must stay open for the attach probe; page navigations are gated because the shell injects the header on every request (13-02)."
  - "A missing/wrong token returns 401; the attach-failure refusal exits 1 so a caller can distinguish refusal from the exit-0 attach."
  - "The 3.3(e) attach-failed copy is printed with the name filled ('itembank') and the pid deferred to the shell: the daemon side has no stdlib port->pid mapping."
  - "`session.do_start` is called with the working tree's spec-dict signature (surfaces/session.py pre-existing WIP), not the HEAD signature."

patterns-established:
  - "Sidecar stdout is quiet: serve_scoped(quiet=True) suppresses the url banner so stdout carries exactly the three handshake lines."
  - "Refusal and attach reuse start_server()'s three-case path; only the bound-but-silent case is sidecar-specific."

requirements-completed: [DEL-09, DEL-10]

coverage:
  - id: D1
    description: "Sidecar stdout handshake (port/token/version) with shared framing constants and OS-assigned port on squatter fallback"
    requirement: DEL-09
    verification:
      - kind: integration
        ref: "tests/packaging_shell_roundtrip.py#check_sidecar_handshake"
        status: pass
    human_judgment: false
  - id: D2
    description: "Per-launch token gate: 401 without, 200 with, marker open, CLI daemon path unaffected"
    requirement: DEL-10
    verification:
      - kind: integration
        ref: "tests/packaging_shell_roundtrip.py#check_sidecar_token_gate"
        status: pass
    human_judgment: false
  - id: D3
    description: "Single-instance: second launch attaches (exit 0, already-running line), attach failure refuses with the 3.3(e) copy"
    requirement: DEL-09
    verification:
      - kind: integration
        ref: "tests/packaging_shell_roundtrip.py#check_second_launch_attaches"
        status: pass
      - kind: integration
        ref: "tests/packaging_shell_roundtrip.py#check_attach_failure_refuses"
        status: pass
    human_judgment: false
  - id: D4
    description: "Lifecycle: force-kill releases the port for both the sidecar and the CLI daemon entry, teardown timed"
    requirement: DEL-10
    verification:
      - kind: integration
        ref: "tests/packaging_shell_roundtrip.py#check_lifecycle_sidecar"
        status: pass
      - kind: integration
        ref: "tests/packaging_shell_roundtrip.py#check_lifecycle_daemon"
        status: pass
    human_judgment: false

duration: 16min
completed: 2026-08-10
status: complete
---

# Phase 13 Plan 01: Sidecar stdout handshake, per-launch token gate, single-instance attach/refuse, and the kill-releases-the-port lifecycle proof

**`itembank sidecar` announces its bound port, per-launch token, and version on stdout in a fixed handshake, gates every route except the probe marker with that token, attaches-or-refuses on a second launch, and proves a killed sidecar releases its port.**

## Performance

- **Duration:** 16 min
- **Started:** 2026-08-10T19:15:00-05:00
- **Completed:** 2026-08-10T19:31:00-05:00
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- The sidecar-half of the shell contract: `itembank sidecar <dir>` binds 127.0.0.1, prints `itembank-port:<n>` / `itembank-token:<hex>` / `itembank-version:<v>` after binding, and keeps stdout quiet so the shell's parser reads exactly three handshake lines.
- The D-04 token gate: every route except `/__itembank__` returns 401 without `X-Itembank-Token`; the CLI daemon path (no token) is byte-compatible (58 daemon checks + launcher roundtrip green).
- Single-instance D-06: a second launch against a reachable instance prints the already-running line and exits 0; a bound-but-silent holder is refused with the 13-UI-SPEC 3.3(e) copy and exit 1; a responding squatter and an OS-reserved port fall back to an OS-assigned port exactly as the CLI daemon does.
- The lifecycle proof the shell's job object will rely on: force-killing the sidecar (and the plain daemon) releases the port, measured at ~1.5s in both fixtures.

## Task Commits

1. **Task 1: stdout handshake + per-launch token** — `3575f79`, `80b1a44`, `dac4bbd`, `73710fc` (test + impl commits, see deviations for the fork-drift history)
2. **Task 2: single-instance attach/refuse** — `73710fc` (named-refusal copy, refusal exit 1)
3. **Task 3: lifecycle subprocess fixture** — `dac4bbd` (both fixtures timed)

**Plan metadata:** pending (docs commit in the orchestrator's post-plan update).

## Files Created/Modified
- `surfaces/daemon.py` — `SIDECAR_HANDSHAKE`, `SIDECAR_TOKEN_HEADER`, `SIDECAR_PORT_HELD_COPY`, `DaemonHandler.sidecar_token` + `_sidecar_token_ok`, `_port_silent`, `_build_sessions`, `cmd_sidecar`, `serve_scoped(quiet=True)`
- `surfaces/cli.py` — the `sidecar` subcommand registered
- `tests/packaging_shell_roundtrip.py` — the full 8-check roundtrip suite

## Decisions Made
- Single entry point: the dedicated `sidecar` subcommand (the plan's "flag/command" wording resolved to the command; the transient `--sidecar` flag on `daemon` was removed).
- Gate scope: every route except the probe marker (the shell injects the header on every request it makes; navigation included, per 13-02's plan wording "with the token injected for the shell-used routes").
- Refusal semantics: attach-failed copy with name filled, pid deferred to the shell; exit 1 so the caller can distinguish refusal from exit-0 attach.
- `session.do_start` adapted to the working tree's spec-dict signature (pre-existing uncommitted `surfaces/session.py` WIP), keeping `/api/start` functional.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Working-tree `session.do_start` signature mismatch**
- **Found during:** Task 1 verification (`/api/start` returned 500)
- **Issue:** The working tree's uncommitted `surfaces/session.py` refactors `do_start` to `(bank_path, spec, mode, out, force)`; the committed daemon handler called the old 8-arg form.
- **Fix:** `handle_api_start` builds the spec dict (`objective`/`count`/`seed`/`focus`) and calls the new signature.
- **Files modified:** surfaces/daemon.py
- **Verification:** POST /api/start returns 200 with the token.
- **Committed in:** `73710fc`

**2. [Rule 3 - Blocking] Fork-drift during the concurrent-prep run**
- **Found during:** Task 1 (RED)
- **Issue:** Two background research agents spawned for downstream prep drifted into implementing 13-01 (the documented Codex fork-drift hazard in AGENTS.md), committing a test file (`0002d57`) and an implementation (`80b1a44`) with a different gate scope (`/api/*` only, 401) and a squatter-refusal variant.
- **Fix:** Interrupted both agents; adopted their handshake/single-instance/lifecycle mechanics, reconciled to the final design (full gate except the marker, dedicated subcommand, attach-failed refusal copy), and rewrote the test suite to the reconciled contract.
- **Files modified:** surfaces/daemon.py, surfaces/cli.py, tests/packaging_shell_roundtrip.py
- **Verification:** 8/8 checks green; daemon + launcher roundtrips green.
- **Committed in:** `dac4bbd`, `73710fc`

**3. [Rule 3 - Blocking] Named-refusal copy pid**
- **Found during:** Task 2
- **Issue:** The full 3.3(e) copy carries `(pid <n>)`; the daemon side has no stdlib port->pid mapping.
- **Fix:** Refuses by the one name it knows (`itembank`); the pid is the shell's to fill in its window document (13-02). Documented in the constant.
- **Committed in:** `73710fc`

---

**Total deviations:** 3 auto-fixed (2 blocking integration, 1 contract-resolution)
**Impact on plan:** All auto-fixes were required for correctness or for integrating with the dirty working tree. No scope creep.

## Issues Encountered
- **Concurrent-writer hazard:** while the background prep agents ran, other commits landed on `main` (including a `test(07-01)` selection commit and pre-staged user WIP). One of my intermediate commits (`dac4bbd`, labeled test(13-01)) swept in pre-staged user WIP (`build.py`, `itembank.py`, `selection.py`, `surfaces/session.py`). No content was lost — all files are intact in history — but the commit message understates its contents. Subsequent commits were staged with explicit paths and verified.
- The two prep agents produced no research deliverables before drifting; their brief files remain in the phase directory with the original instructions only.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 13-02 can consume the sidecar contract: spawn `itembank sidecar <dir> --no-open`, parse the three handshake lines with the shared constants, send `X-Itembank-Token` on every request, and map exit 0 + "already running at <url>" to attach, exit 1 + the port-held copy to refusal.

## Self-Check: PASSED
- Created files exist: tests/packaging_shell_roundtrip.py, plus modified surfaces/daemon.py and surfaces/cli.py
- Commits present: 3575f79, 80b1a44, dac4bbd, 73710fc
- `python tests/packaging_shell_roundtrip.py` → ok (8 checks)
- `python tests/daemon_roundtrip.py` → ok (58 checks)
- `python tests/launcher_roundtrip.py` → ok

---
*Phase: 13-desktop-packaging-tauri-sidecar*
*Completed: 2026-08-10*
