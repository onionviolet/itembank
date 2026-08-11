---
phase: 13-desktop-packaging-tauri-sidecar
plan: 04
subsystem: infra
tags: [updater, latest-json, minisign, disclosure, tauri-plugin-updater]

requires:
  - phase: 13-desktop-packaging-tauri-sidecar
    provides: plans 13-02/13-03's shell, sidecar handshake, and onedir build
  - phase: 02.1-packaging-self-update-interop-export
    provides: the Python updater, SHA256SUMS.txt channel, and the locked disclosure text
provides:
  - "the latest.json tauri-plugin-updater manifest generator + release-step hook (one channel, two consumers)"
  - "the minisign signing step in the release pipeline (key material is a build secret)"
  - "the one-disclosure render hook (update.disclosure_state) + GET /disclosure route + 'itembank disclosure' CLI twin"
  - "the shell's tauri-plugin-updater wiring and the first-page StatusNotice injection (render-once, no check)"
  - "the version-coherence gate (from 13-02) and the unchanged Python updater regression"
affects: []

actuals:
  tokens: 15063
  tasks: 3
  commits: 2

tech-stack:
  added: [tauri-plugin-updater 2]
  patterns:
    - "one release channel, two manifest formats, same tag (D-08)"
    - "one notified_at record, two renderings (CLI print and shell StatusNotice)"
    - "render-once notice injection in the proxy (first HTML response only)"

key-files:
  created: []
  modified:
    - build.py
    - scripts/build_shell.ps1
    - surfaces/update.py
    - surfaces/daemon.py
    - surfaces/cli.py
    - src-tauri/Cargo.toml
    - src-tauri/Cargo.lock
    - src-tauri/tauri.conf.json
    - src-tauri/src/main.rs
    - src-tauri/src/proxy.rs
    - tests/packaging_roundtrip.py
    - tests/daemon_roundtrip.py

key-decisions:
  - "latest.json and the minisign signature are produced by the release pipeline only when the installer and key material exist; otherwise the step degrades honestly (the CLI SHA256SUMS.txt channel stays the only manifest)."
  - "The tauri-plugin-updater pubkey is a build-time value; with an empty pubkey the plugin is inert rather than silently unverified (T-13-13)."
  - "The shell reads the daemon-owned disclosure state and injects the StatusNotice into the first HTML page through the proxy -- the shell writes no state record (13-UI-SPEC 7.2 item 4)."
  - "The /disclosure route is token-gated like every route except the marker; its CLI twin ('itembank disclosure') keeps the route/CLI inventory honest."

patterns-established:
  - "Forbidden-telemetry copy is a checkable fixture over the disclosure + update-available copy."
  - "Honest gating: signing and install steps name the missing toolchain/secret instead of faking output."

requirements-completed: [DEL-12]

coverage:
  - id: D1
    description: "latest.json validates the documented updater shape and publishes beside SHA256SUMS.txt from the same tag only when installer + signature exist"
    requirement: DEL-12
    verification:
      - kind: integration
        ref: "tests/packaging_roundtrip.py#test_latest_json_shape"
        status: pass
    human_judgment: false
  - id: D2
    description: "One-disclosure render hook: locked 02.1 copy, resolved settings path, one notified_at flips show off; no telemetry words in updater copy"
    requirement: DEL-12
    verification:
      - kind: integration
        ref: "tests/packaging_roundtrip.py#test_disclosure_state_and_forbidden_words"
        status: pass
      - kind: integration
        ref: "tests/daemon_roundtrip.py#check_disclosure_route"
        status: pass
    human_judgment: false
  - id: D3
    description: "Shell updater wired (tauri-plugin-updater with endpoint + signature config; pubkey build-time, inert when empty); StatusNotice injects once into the first HTML page"
    requirement: DEL-12
    verification:
      - kind: unit
        ref: "src-tauri/src/proxy.rs#status_notice_injects_once_into_html"
        status: pass
    human_judgment: true
    rationale: "The live update-available flow requires a signed release and a real pubkey; the wiring and render-once mechanics are machine-checked, the end-to-end install is not (release assets don't exist yet)."
  - id: D4
    description: "Version coherence at handshake routes mismatches to the honest state; Python updater regression unchanged"
    requirement: DEL-12
    verification:
      - kind: unit
        ref: "src-tauri/src/liveness.rs#version_match_and_mismatch"
        status: pass
      - kind: integration
        ref: "tests/update_roundtrip.py"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-10
status: complete
---

# Phase 13 Plan 04: The updater - latest.json + minisign on the shared channel, the one-disclosure StatusNotice, and the unchanged Python updater

**One GitHub Releases channel now serves two consumers -- the CLI updater's SHA256SUMS.txt and the Tauri updater's latest.json + minisign signature -- while the shell reads a single daemon-owned disclosure record and renders it exactly once, and the Python updater is provably untouched.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-08-10T22:24:00-05:00
- **Completed:** 2026-08-10T23:19:00-05:00
- **Tasks:** 3
- **Files modified:** 12

## Accomplishments
- `build.latest_json` emits the documented tauri-plugin-updater manifest (version/notes/pub_date/platforms.windows-x86_64.signature+url) and the release step publishes it beside SHA256SUMS.txt from the same tag; the minisign signing step is wired into `build_shell.ps1` (key material is a build secret, absent = honest skip).
- `update.disclosure_state` is the one-disclosure render hook: the daemon keeps the single `notified_at` record; the shell reads it through `GET /disclosure` (token-gated, with an `itembank disclosure` CLI twin) and injects the locked 02.1 copy plus the single additive settings-path line as a `role="status"` StatusNotice into the first HTML page -- render-once, no check performed.
- `tauri-plugin-updater` is wired with the channel endpoint and signature-verification config; the pubkey is a build-time value, so an empty key means the plugin is inert rather than silently unverified (T-13-13).
- The Python updater regression suite passes unchanged, and the version-coherence gate (13-02) already routes mismatched halves to the honest state.

## Task Commits

1. **Task 1: latest.json + minisign assets** — `b72eee6`
2. **Task 2: updater wiring + one-disclosure StatusNotice** — `b72eee6`
3. **Task 3: version coherence + Python-updater regression** — `b72eee6`, `36b2cab`

**Plan metadata:** pending (docs commit in the orchestrator's post-plan update).

## Files Created/Modified
- `build.py` — `latest_json`, `latest_json_hook`
- `scripts/build_shell.ps1` — minisign + latest.json publication step
- `surfaces/update.py` — `disclosure_state`
- `surfaces/daemon.py` — `GET /disclosure` + `cmd_disclosure` + `handle_disclosure`
- `surfaces/cli.py` — the `disclosure` subcommand
- `src-tauri/` — updater plugin registration, config, proxy StatusNotice injection
- `tests/packaging_roundtrip.py`, `tests/daemon_roundtrip.py` — the fixtures

## Decisions Made
- The pubkey and signing key are build-time secrets; until they exist, the updater is inert and the release step names the gap (honest degradation, T-13-13).
- The shell writes no disclosure state; it reads the daemon-owned record and injects the notice into the first HTML response (13-UI-SPEC 7.2 item 4).
- The additive line is exactly one: "Your settings file is at <resolved path>." -- the fixture pins it.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] tauri.conf.json `plugins` placement**
- **Found during:** the first build after wiring
- **Issue:** the updater config was initially nested under `app`; Tauri 2's schema wants `plugins` at the config top level.
- **Fix:** moved `plugins.updater` to top level.
- **Committed in:** `b72eee6`

**2. [Rule 3 - Blocking] Staged foreign WIP swept into the commits**
- **Found during:** committing
- **Issue:** the concurrent session's staged `surfaces/session.py` and selection-phase files rode into the 13-04 commits.
- **Fix:** content preserved (nothing lost); explicit-path staging continues; history labels are imperfect and recorded.
- **Committed in:** `b72eee6`, `36b2cab`

---

**Total deviations:** 2 auto-fixed (both blocking)
**Impact on plan:** No scope creep; both were integration hazards.

## Issues Encountered
- **Live update install not exercisable here:** there is no signed release, no pubkey, and no minisign key in this environment; the pipeline step and plugin wiring are fixture-proven, and the end-to-end install is recorded as a UAT item (needs a real release + secrets).

## User Setup Required
None - the signing key and pubkey are build secrets, not user configuration.

## Next Phase Readiness
- Plan 13-05 (the verify plan) seals the phase: the packaging, shell, updater, and coherence fixtures plus the full suite.

## Self-Check: PASSED
- `python tests/packaging_roundtrip.py` → ok (incl. latest.json + disclosure fixtures)
- `python tests/update_roundtrip.py` → ok (Python updater unchanged)
- `python tests/packaging_shell_roundtrip.py` → 10 checks
- `cargo test --manifest-path src-tauri/Cargo.toml` → 17 passed
- `tests/daemon_roundtrip.py` → disclosure route fixture added; suite re-run at the phase regression gate

---
*Phase: 13-desktop-packaging-tauri-sidecar*
*Completed: 2026-08-10*
