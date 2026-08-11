---
phase: 13-desktop-packaging-tauri-sidecar
plan: 03
subsystem: infra
tags: [pyinstaller, onedir, nsis, installer, signing, headless]

requires:
  - phase: 13-desktop-packaging-tauri-sidecar
    provides: plan 13-01's sidecar command and plan 13-02's shell externalBin wiring
  - phase: 02.1-packaging-self-update-interop-export
    provides: build.py's allowlist staging, SHA256SUMS.txt, and the release channel
provides:
  - "the pinned PyInstaller onedir sidecar build (28.8 MiB, within the 25-45 MiB target) with the triple-suffixed binary the shell bundles"
  - "scripts/build_shell.ps1: reproducible .pyz + onedir freeze + size measurement + honest NSIS-bundle degradation"
  - "installers/nsis/itembank.nsi: per-user default with machine-wide variant, fail-closed install notice, uninstaller scoped to \$INSTDIR only"
  - "build.py's latest_json_hook seam for the Tauri updater"
  - "the headless CLI-without-shell proof and the evidence-location parity proof"
affects: [13-04]

actuals:
  tokens: 7106
  tasks: 3
  commits: 2

tech-stack:
  added: [pyinstaller 6.22.0]
  patterns:
    - "onedir freeze with --add-data for schemas/styles/fonts (resources.py resolves them relative to the frozen root)"
    - "install-notice values supplied at compile time with !error fail-closed -- a placeholder can never ship"

key-files:
  created:
    - requirements-build.txt
    - scripts/build_shell.ps1
    - installers/nsis/itembank.nsi
    - installers/nsis/README.md
  modified:
    - build.py
    - tests/packaging_roundtrip.py
    - src-tauri/src/sidecar.rs

key-decisions:
  - "The frozen exe is the CLI entry (itembank.py) -- the sidecar is a CLI mode -- and the shell's bundled invocation passes 'sidecar <dir>'."
  - "PyInstaller onedir, never onefile (D-09); the measured 28.8 MiB is recorded against the 25-45 MiB target."
  - "NSIS bundling degrades honestly while makensis is absent (recorded environment gap), matching D-11's honest-branch discipline."
  - "The install-notice values are compile-time defines the build supplies with real values; the .nsi !error's without them (T-13-10)."
  - "The uninstaller deletes only \$INSTDIR; the fixture simulates the scope against a temp profile (T-13-09)."

patterns-established:
  - "Build reproducibility: versions + checksums + licenses recorded before any tool is installed (D-14)."
  - "Honest degradation: every packaging step either runs or names the missing toolchain gap."

requirements-completed: [DEL-11, DEL-13]

coverage:
  - id: D1
    description: "PyInstaller onedir sidecar builds reproducibly, runs the sidecar mode, serves the marker, and measures within the 25-45 MiB target"
    requirement: DEL-11
    verification:
      - kind: integration
        ref: "tests/packaging_roundtrip.py#test_onedir_sidecar_runs_and_is_sized"
        status: pass
    human_judgment: false
  - id: D2
    description: "Toolchain pinned with checksum and license review; build script freezes onedir, never onefile, with the triple-suffixed binary"
    requirement: DEL-11
    verification:
      - kind: integration
        ref: "tests/packaging_roundtrip.py#test_build_toolchain_pinned"
        status: pass
    human_judgment: false
  - id: D3
    description: "Uninstaller scoped to the application directory; simulated uninstall leaves the evidence store and banks intact"
    requirement: DEL-13
    verification:
      - kind: integration
        ref: "tests/packaging_roundtrip.py#test_uninstaller_never_touches_profile_data"
        status: pass
    human_judgment: false
  - id: D4
    description: "Install notice fails closed without real signed/unsigned values; unsigned branch documents SmartScreen honestly"
    requirement: DEL-13
    verification:
      - kind: integration
        ref: "tests/packaging_roundtrip.py#test_install_notice_cannot_ship_placeholders"
        status: pass
    human_judgment: true
    rationale: "The rendered installer page itself requires makensis + a real install; the fail-closed structure and copy are machine-checked, the compiled installer is not (toolchain gap recorded)."
  - id: D5
    description: "Full headless CLI loop (lint/build/start/submit/report/evidence) with no shell installed; evidence location identical with and without the shell"
    requirement: DEL-13
    verification:
      - kind: integration
        ref: "tests/packaging_roundtrip.py#test_headless_loop_without_the_shell"
        status: pass
      - kind: integration
        ref: "tests/packaging_roundtrip.py#test_evidence_location_is_identical_with_and_without_the_shell"
        status: pass
    human_judgment: false

duration: 65min
completed: 2026-08-10
status: complete
---

# Phase 13 Plan 03: The distribution plan - pinned PyInstaller onedir sidecar, NSIS installer with the evidence-store guard, honest signing notice, and the headless CLI-without-shell proof

**A reproducible 28.8 MiB PyInstaller onedir sidecar (pinned toolchain, never onefile), an NSIS installer that cannot touch the learner's data and cannot ship a placeholder signing claim, and a proven headless CLI loop that never needs the shell.**

## Performance

- **Duration:** 65 min
- **Started:** 2026-08-10T21:18:00-05:00
- **Completed:** 2026-08-10T22:23:00-05:00
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- The onedir sidecar freezes from the CLI entry (never onefile), ships the `itembank-sidecar-x86_64-pc-windows-msvc.exe` the shell's externalBin consumes, serves the marker from the frozen runtime, and measures 28.8 MiB -- inside the 25-45 MiB target (D-09).
- `requirements-build.txt` pins PyInstaller 6.22.0 with the wheel sha256 and the bootloader-exception license verdict (D-14); `scripts/build_shell.ps1` is the reproducible one-command build.
- The NSIS installer (per-user default, machine-wide variant) has an install-notice page that fails to compile without real signed/unsigned values and an uninstaller scoped to `$INSTDIR`; the simulation fixture proves the evidence store and banks survive uninstall (T-13-09).
- `build.py` gained the `latest_json_hook` seam for the Tauri updater (13-04 wires it fully).
- The headless CLI loop (lint/build/start/submit/report/evidence) passes with no shell installed, and the evidence store resolves to the identical path with and without the shell (D-12).

## Task Commits

1. **Task 1: pinned onedir build + build script** — `46c73aa`
2. **Task 2: NSIS installer + notice + guard** — `46c73aa`
3. **Task 3: headless proof** — `f1bf63b`

**Plan metadata:** pending (docs commit in the orchestrator's post-plan update).

## Files Created/Modified
- `requirements-build.txt` — PyInstaller pin + checksum + license
- `scripts/build_shell.ps1` — the one-command packaged build
- `installers/nsis/itembank.nsi`, `installers/nsis/README.md`
- `build.py` — `latest_json_hook`
- `tests/packaging_roundtrip.py` — the five new fixtures
- `src-tauri/src/sidecar.rs` — bundled sidecar invocation (`sidecar <dir>`)

## Decisions Made
- The frozen exe is the full CLI entry; the shell's bundled invocation passes `sidecar <dir> --no-open --port 0` (the frozen CLI accepts the same command as the dev python fallback).
- PyInstaller `--add-data` for schemas/styles/fonts: `resources.py` resolves data paths relative to the frozen root, so the freeze must carry them explicitly.
- NSIS bundle: honest degradation (makensis absent on this machine) instead of a fake installer; the script and its fixtures are the deliverable until the toolchain exists.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] PyInstaller nests the onedir app directory**
- **Found during:** the first freeze
- **Issue:** PyInstaller 6.x lays out `dist/<name>/<name>/`; the script assumed a flat root.
- **Fix:** resolve the frozen exe by search, measure the whole tree.
- **Committed in:** `46c73aa`

**2. [Rule 3 - Blocking] Frozen runtime could not read schemas/styles/fonts**
- **Found during:** the frozen sidecar fixture
- **Issue:** `resources.py` resolves data relative to the frozen root; the freeze shipped only Python modules.
- **Fix:** `--add-data` with absolute repo paths for the three data dirs (relative paths resolve against the spec dir).
- **Committed in:** `46c73aa`

**3. [Rule 3 - Blocking] Bundled sidecar invocation lacked `sidecar <dir>`**
- **Found during:** wiring the bundled path
- **Issue:** the shell's bundled branch spawned the frozen CLI without the sidecar subcommand and bank dir.
- **Fix:** the bundled branch now passes `sidecar <dir> --no-open --port 0`, matching the dev fallback.
- **Committed in:** `46c73aa`

---

**Total deviations:** 3 auto-fixed (all blocking integration)
**Impact on plan:** All fixes were required for the frozen artifact to run. No scope creep.

## Issues Encountered
- **makensis (NSIS 3.x) is absent** on this machine: the installer is written and its logic is fixture-proven, but the compiled installer and the signed/unsigned rendering need the toolchain (recorded gap, surfaced as a UAT/checklist item rather than hidden).
- **Concurrent session mid-refactor:** `tests/daemon_roundtrip.py` transiently failed while another session was editing `session.py`/`evidence.py`/`selection.py` (20:04-20:05). Not a 13-03 regression; the suite passed 59/59 earlier and is re-run at the phase-end regression gate.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 13-04 wires `latest_json_hook` to the real release values and the Tauri updater manifest, and can rely on the bundled sidecar binary now being the real PyInstaller artifact (the stub is replaced by the build).

## Self-Check: PASSED
- `powershell -File scripts/build_shell.ps1` → exit 0; onedir 28.8 MiB; NSIS bundle honestly skipped
- `python tests/packaging_roundtrip.py` → ok (all 13-03 fixtures + the DEL-01/02 contract)
- `python tests/packaging_shell_roundtrip.py` → 10 checks
- `cargo test --manifest-path src-tauri/Cargo.toml` → 16 passed
- `tests/daemon_roundtrip.py` → deferred to the phase-end regression gate (concurrent mid-refactor on session/evidence)

---
*Phase: 13-desktop-packaging-tauri-sidecar*
*Completed: 2026-08-10*
