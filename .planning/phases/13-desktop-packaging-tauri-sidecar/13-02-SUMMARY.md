---
phase: 13-desktop-packaging-tauri-sidecar
plan: 02
subsystem: infra
tags: [tauri, rust, sidecar, job-object, named-mutex, webview, proxy]

requires:
  - phase: 13-desktop-packaging-tauri-sidecar
    provides: plan 13-01's sidecar command, stdout handshake constants, token gate, attach/refuse behavior
provides:
  - "the Tauri 2.x shell: sidecar spawn + handshake reader, token-injecting loopback proxy, window chrome and two-item menu"
  - "the job-object backstop (JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE) proven by a real taskkill-the-shell fixture"
  - "named-mutex single instance with attach-or-refuse"
  - "the five liveness states with 13-UI-SPEC 3.3 copy verbatim and version coherence"
  - "the daemon's POST /cli-twin route + `itembank cli-twin` command (the daemon-owned route->CLI mapping)"
affects: [13-03, 13-04]

actuals:
  tokens: 140852
  tasks: 3
  commits: 2

tech-stack:
  added: [tauri 2.11.5, tauri-build 2.6.3, tauri-plugin-clipboard-manager 2.3.2, serde 1.0.229, serde_json 1.0.151, windows-sys 0.59]
  patterns:
    - "loopback HTTP proxy injects the per-launch token and strips Origin -- one HTTP transport end to end (D-02)"
    - "job object with KILL_ON_JOB_CLOSE leaked for the app lifetime; dropping the Rust value would kill the sidecar"
    - "handshake constants mirrored in Rust and Python (one edit per side, never a second protocol)"

key-files:
  created:
    - src-tauri/Cargo.toml
    - src-tauri/Cargo.lock
    - src-tauri/tauri.conf.json
    - src-tauri/src/main.rs
    - src-tauri/src/handshake.rs
    - src-tauri/src/sidecar.rs
    - src-tauri/src/proxy.rs
    - src-tauri/src/job_object.rs
    - src-tauri/src/single_instance.rs
    - src-tauri/src/liveness.rs
    - src-tauri/assets/runtime-not-ready.html
    - src-tauri/assets/runtime-status.html
    - scripts/gen_shell_assets.py
    - scripts/gen_icon.py
  modified:
    - surfaces/daemon.py
    - surfaces/cli.py
    - tests/daemon_roundtrip.py
    - tests/packaging_shell_roundtrip.py

key-decisions:
  - "The shell spawns the sidecar binary directly (resolved from the externalBin naming) instead of Command::sidecar so the process handle is available for the job-object assignment; the binary is still named by bundle.externalBin."
  - "The token is injected via a shell-local loopback HTTP proxy (WebView2 cannot set headers on navigation); the proxy forwards HTTP to the daemon, adds X-Itembank-Token, strips Origin -- one transport (D-02)."
  - "The daemon's /cli-twin route lives outside /api/* (API_ROUTES is locked at four) and has a real CLI twin command, keeping the route/CLI inventory honest."
  - "Window dimensions are not pinned by UI-SPEC section 2; the shell uses 1100x760 (min 768x512) with native decorations."
  - "Version coherence: the sidecar handshake version must equal the shell's own version or the window takes the honest failure path."

patterns-established:
  - "Headless test seam (ITEMBANK_HEADLESS) reports sidecar pid/port on the shell's stdout, never the token (T-13-08)."
  - "Build-time asset generation from surfaces/theme.THEME_CSS -- no literal hex in shell/ (13-UI-SPEC 3.2)."

requirements-completed: [DEL-09, DEL-10]

coverage:
  - id: D1
    description: "Shell spawns the sidecar, reads the fixed stdout handshake, and renders daemon pages with the token injected"
    requirement: DEL-09
    verification:
      - kind: unit
        ref: "src-tauri/src/handshake.rs#parses_the_three_lines"
        status: pass
      - kind: integration
        ref: "tests/packaging_shell_roundtrip.py#check_lifecycle_shell"
        status: pass
    human_judgment: false
  - id: D2
    description: "Job-object backstop: taskkill /F of the shell takes the sidecar down with it (no orphan, no held port)"
    requirement: DEL-10
    verification:
      - kind: unit
        ref: "src-tauri/src/job_object.rs#kill_on_close_terminates_an_assigned_child"
        status: pass
      - kind: integration
        ref: "tests/packaging_shell_roundtrip.py#check_lifecycle_shell"
        status: pass
    human_judgment: false
  - id: D3
    description: "Named-mutex single instance: second acquire fails while held; attach-or-refuse by window focus"
    requirement: DEL-09
    verification:
      - kind: unit
        ref: "src-tauri/src/single_instance.rs#second_acquire_fails_while_first_is_held"
        status: pass
    human_judgment: false
  - id: D4
    description: "Five liveness states render the 13-UI-SPEC 3.3 copy verbatim; version coherence rejects mismatched halves"
    requirement: DEL-10
    verification:
      - kind: unit
        ref: "src-tauri/src/liveness.rs#version_match_and_mismatch"
        status: pass
      - kind: integration
        ref: "tests/packaging_shell_roundtrip.py#check_shell_liveness_docs"
        status: pass
    human_judgment: true
    rationale: "The in-window rendering of the states requires a visual/human pass; the copy and transitions are machine-checked, the rendered window is not."
  - id: D5
    description: "Cargo.lock committed with pinned crate versions and a named license review"
    requirement: DEL-10
    verification:
      - kind: other
        ref: "src-tauri/Cargo.lock (committed); license table in this summary"
        status: pass
    human_judgment: false

duration: 105min
completed: 2026-08-10
status: complete
---

# Phase 13 Plan 02: The Tauri 2 shell - sidecar handshake, token-injecting proxy, job-object lifecycle, named-mutex single instance, and the five honest liveness states

**A thin Rust shell spawns the Python sidecar, reads its stdout handshake, serves the daemon's pages through a token-injecting loopback proxy, dies with its sidecar (job object, proven by a real taskkill fixture), refuses second instances by name, and is honest about the runtime at every moment.**

## Performance

- **Duration:** 105 min
- **Started:** 2026-08-10T19:32:00-05:00
- **Completed:** 2026-08-10T21:17:00-05:00
- **Tasks:** 3
- **Files modified:** 27 (+1 test file)

## Accomplishments
- `src-tauri/` builds on the MSVC toolchain (the GNU toolchain lacked `dlltool`): sidecar spawn with dev-python fallback, shared-constant handshake parser, and a shell-local HTTP proxy that injects `X-Itembank-Token` and strips `Origin` so the WebView can render the token-gated daemon pages over one HTTP transport.
- The job-object backstop is proven end to end: `taskkill /F` the shell and the sidecar dies with it (~2.1s teardown), matching the daemon-side property from plan 13-01.
- The named-mutex single instance (attach by focusing the existing window, or the 3.3(e) refusal) and the five liveness states with 13-UI-SPEC 3.3 copy verbatim, generated at build time from `theme.THEME_CSS`.
- The daemon now owns the route->CLI mapping the menu's "Copy the CLI command for this view" reads: `POST /cli-twin` and the real `itembank cli-twin <path>` command.

## Task Commits

1. **Task 1: scaffold + handshake + proxy + menu** — `6ef0a82` (feat, shell + cli-twin)
2. **Task 2: job object + named mutex + kill-the-shell fixture** — `6ef0a82`, `b1e9553`
3. **Task 3: five liveness states + version coherence** — `6ef0a82`, `b1e9553`

**Plan metadata:** pending (docs commit in the orchestrator's post-plan update).

## Files Created/Modified
- `src-tauri/` — the full Rust shell (main.rs, handshake.rs, sidecar.rs, proxy.rs, job_object.rs, single_instance.rs, liveness.rs), tauri.conf.json, Cargo.toml/Cargo.lock, assets, capabilities, icons
- `scripts/gen_shell_assets.py`, `scripts/gen_icon.py` — build-time generators
- `surfaces/daemon.py` — `cli_twin_for`, `POST /cli-twin` handler, `cmd_cli_twin`
- `surfaces/cli.py` — the `cli-twin` subcommand
- `tests/daemon_roundtrip.py` — `check_cli_twin_route` (59 checks total)
- `tests/packaging_shell_roundtrip.py` — `check_lifecycle_shell`, `check_shell_liveness_docs` (10 checks total)

## Decisions Made
- **Sidecar spawn:** direct process spawn of the externalBin-named binary (dev fallback: `python itembank.py sidecar`) rather than `Command::sidecar`, because the job-object assignment needs the raw process; `bundle.externalBin` still names the binary.
- **Token injection:** shell-local loopback HTTP proxy (WebView2 cannot attach headers to navigation); the proxy is plumbing over the same HTTP surface, not a second protocol (D-02).
- **CLI-twin route:** `POST /cli-twin` (outside the locked four-route `/api/*`), backed by a real `itembank cli-twin` command so the route/CLI inventory stays honest.
- **Window geometry:** 1100x760, min 768x512, native decorations (dimensions are not UI-SPEC-pinned).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] GNU toolchain missing dlltool**
- **Found during:** first `cargo build`
- **Issue:** the active GNU target required `dlltool.exe` (mingw), absent from the machine.
- **Fix:** switched to the installed `stable-x86_64-pc-windows-msvc` toolchain (VS 2019 Build Tools auto-detected); externalBin triple updated to `x86_64-pc-windows-msvc`.
- **Committed in:** `6ef0a82`

**2. [Rule 3 - Blocking] Job object dropped at scope end killed the sidecar**
- **Found during:** the kill-the-shell fixture
- **Issue:** the `JobObject` value dropped when `spawn_and_connect` returned, closing the kill-on-close handle and terminating the sidecar immediately.
- **Fix:** leak the job handle for the app lifetime (the OS releases it when the shell process dies).
- **Committed in:** `6ef0a82`

**3. [Rule 2 - Missing critical] The spec'd menu item needed a daemon route**
- **Found during:** Task 1 (menu)
- **Issue:** "Copy the CLI command for this view" requires the daemon to own the route->CLI mapping; no such route existed.
- **Fix:** added `POST /cli-twin` + `itembank cli-twin` (a files_modified deviation: surfaces/daemon.py and surfaces/cli.py).
- **Committed in:** `6ef0a82`

**4. [Rule 3 - Blocking] tauri-build requires the externalBin file to exist**
- **Found during:** first `cargo build`
- **Issue:** the PyInstaller sidecar does not exist until plan 13-03.
- **Fix:** committed a placeholder stub binary (prints an error, exits 1) with a README; 13-03's build script replaces it. Never ships.
- **Committed in:** `6ef0a82`

---

**Total deviations:** 4 auto-fixed (3 blocking, 1 missing critical)
**Impact on plan:** All fixes were required for the build or for the spec'd behavior. No scope creep.

## License review (D-14) -- direct pinned crates

| Crate | Version | License |
|---|---|---|
| tauri | 2.11.5 | MIT OR Apache-2.0 |
| tauri-build | 2.6.3 | MIT OR Apache-2.0 |
| tauri-plugin-clipboard-manager | 2.3.2 | MIT OR Apache-2.0 |
| serde | 1.0.229 | MIT OR Apache-2.0 |
| serde_json | 1.0.151 | MIT OR Apache-2.0 |
| windows-sys | 0.59.0 (pinned; 0.45/0.60/0.61 transitively) | MIT OR Apache-2.0 |

Transitive crates in the committed `Cargo.lock` are the standard Rust ecosystem mix (MIT / Apache-2.0 / BSD-2 / ISC families). The lockfile pins every resolved version.

## Issues Encountered
- A concurrent `tests/daemon_roundtrip.py` process on this machine (from another session) caused the pre-existing hostile-path check to flake: it snapshots the shared `%TEMP%` root, so a parallel test's temp dirs trip it. Not a regression; the suite passed 59/59 when the machine was quiet, and the new cli-twin checks passed in isolation throughout.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 13-03 builds the real PyInstaller onedir sidecar that replaces the stub, plus the NSIS installer and the signing-status honesty; `bundle.externalBin` and the dev fallback are already wired.

## Self-Check: PASSED
- `cargo test --manifest-path src-tauri/Cargo.toml` → 16 passed
- `python tests/packaging_shell_roundtrip.py` → 10 checks (incl. kill-the-shell, teardown ~2.1s)
- `python tests/daemon_roundtrip.py` → 59 checks
- `python tests/launcher_roundtrip.py` → ok

---
*Phase: 13-desktop-packaging-tauri-sidecar*
*Completed: 2026-08-10*
