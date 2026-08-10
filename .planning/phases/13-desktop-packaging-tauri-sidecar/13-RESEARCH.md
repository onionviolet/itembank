# Phase 13: Desktop Packaging - Tauri Shell over the Python Sidecar - Research

**Researched:** 2026-08-10
**Domain:** Windows desktop packaging (Tauri 2.x shell, PyInstaller sidecar, NSIS installer, updater coexistence, process lifecycle)
**Confidence:** HIGH for the lifecycle mechanism and the toolchain availability (verified against this machine and the shipped code this session); MEDIUM for updater format details (cited from primary docs, not exercised against a live release).

This document exists because the 13-RESEARCH agent never ran at handoff. It answers the three load-bearing questions the handoff named, verifies the toolchain against this machine, and composes with the two prior research artifacts (`.planning/research/2026-08-09-packaging.md` Q8 - the keep-Python verdict - and the 13-CONTEXT.md decisions D-01..D-15, which are LOCKED and not re-litigated here).

<user_constraints>
## User Constraints (from 13-CONTEXT.md)

All 15 decisions in 13-CONTEXT.md are locked. The load-bearing ones for this research:

- **D-01:** Keep the Python runtime; Tauri 2.x shell over a PyInstaller sidecar; NSIS; this phase number. Porting creates two scorers (Directive 4.2).
- **D-02:** One transport - the existing localhost HTTP surface; no second IPC protocol.
- **D-03:** The sidecar announces its bound port on stdout; the shell reads it; no fixed-port assumption, no scanning.
- **D-04:** The daemon binds 127.0.0.1 only and requires a per-launch token passed by the shell.
- **D-05:** Killing the shell leaves no orphaned sidecar and no held port; on Windows the sidecar sits in a job object so a hard kill of the parent takes the child with it.
- **D-06:** A second launch attaches to the running instance and focuses its window; single-instance via a named mutex.
- **D-07:** NSIS, per-user by default, machine-wide option.
- **D-08:** `tauri-plugin-updater`, signed, reading the same GitHub Releases the Phase 2.1 updater uses. One release channel, two consumers.
- **D-10/D-11:** The AV/code-signing checklist is written and executed; the certificate is named or the build ships unsigned honestly.
- **D-12:** Every capability stays reachable from the CLI without the shell installed.
- **D-14:** Rust crates, the Tauri toolchain, and PyInstaller are pinned with recorded checksums and named license review; a lockfile is committed.
</user_constraints>

<phase_requirements>
## Phase Requirements

ROADMAP.md marks this phase `Requirements: TBD (assign at /gsd-plan-phase 13)`. The `DEL-*` namespace exists (DEL-01..08, all Complete for Phase 2.1), so the planner should mint **DEL-09 onward** in this phase's plan run - one ID per testably distinct criterion, following the LESSON-07..17 and GATE-01..06 precedents.
</phase_requirements>

## Summary

Three findings, all with a direct consequence for the plans:

1. **The Windows lifecycle mechanism is Job Objects - `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` - and it composes with the existing `probe()`/`start_server()` three-case startup rather than fighting it.** The shell creates a job object with the kill-on-close limit, assigns the sidecar process to it, and relies on the OS to terminate the child when the shell dies by any means (including `TerminateProcess` from Task Manager, where graceful shutdown handlers never run). Tauri's own sidecar plugin (`Command::sidecar`) has automatic child cleanup on *graceful* app exit; the job object covers the *ungraceful* case. Both are used: the plugin's exit hook for the normal path, the job object as the backstop. Verified against Microsoft's Job Objects documentation and Tauri's sidecar documentation; this machine has Rust 1.97.1 and cargo available [VERIFIED: `rustc --version` = 1.97.1, this session].
2. **The two-updater conflict resolves structurally: the Python updater and `tauri-plugin-updater` are two consumers of one GitHub Releases channel with different manifest formats, and the release pipeline publishes both artifacts.** The Phase 2.1 updater reads the GitHub API `/releases/latest` and a `SHA256SUMS.txt` asset (verified in `surfaces/update.py`: `_GITHUB_API`, `parse_sha256sums()`). `tauri-plugin-updater` reads a `latest.json` endpoint (the updater plugin's manifest format: `{version, notes, pub_date, platforms: {windows-x86_64: {signature, url}}}` with a minisign signature over the installer). Both consume the same release's assets. The phase must: (a) generate `latest.json` + a minisign signature in the release pipeline alongside the existing `SHA256SUMS.txt`; (b) keep one `notified_at` disclosure record so the packaged channel does not create a second consent store (13-UI-SPEC 7.2 item 5); (c) never have the Tauri updater replace the Python runtime artifact - the shell updates the shell+sidecar bundle, the Python updater updates the `.pyz`, and the update_policy divergence in CLAUDE.md stays unchanged (D-08).
3. **The toolchain is present and the build shape is PyInstaller onedir over the existing Phase 2.1 `.pyz`/runtime, not a second build.** Rust 1.97.1 and Node 22.22.3 are installed [VERIFIED this session]; Python 3.13.5 is installed (the CI pins 3.11 - the plan pins the runtime version explicitly); PyInstaller and NSIS are NOT installed [VERIFIED] and are added as pinned, checksummed, license-reviewed dependencies per D-14. The `bundle.externalBin` mechanism requires the `-$TARGET_TRIPLE` suffix on sidecar binaries [CITED: v2.tauri.app/develop/sidecar/].

## 1. The Windows lifecycle mechanism - Job Objects

**Finding: Job Objects with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` is the real mechanism the CONTEXT's D-05 names.** When a job object is created with this limit and the job's last handle is closed (which the OS does when the owning process dies, including on `TerminateProcess`), every process assigned to the job is terminated. This is the standard, documented Windows answer to "kill the child when the parent dies, even if the parent is force-killed." Graceful shutdown handlers (`atexit`, `finally`, `SIGTERM` handlers) do not run on `TerminateProcess`; the job object does not depend on them.

Composition with the existing startup path [VERIFIED: `surfaces/daemon.py:1391-1456` `probe()`/`start_server()` - the three-case detect-and-attach]:

- The sidecar runs the existing daemon entry (`cmd_daemon`-equivalent with a sidecar flag), which already handles the three cases: bind directly, attach to an already-running itembank (probe True), or fall back to a free port. **The shell must not re-implement this.** It spawns the sidecar with `--no-open --no-browser` semantics, reads the port + token handshake from stdout (D-03/D-04), and treats the three cases through the sidecar's own existing behavior.
- The job object wraps the sidecar *process*, not the port. A held port is the symptom of a live orphaned sidecar; killing the process releases the port. No port-level cleanup is needed beyond the process-level guarantee.
- Tauri's sidecar plugin automatically cleans up spawned children on graceful app exit [CITED: Tauri sidecar docs]. Use it for the normal path and the job object as the ungraceful backstop. The plan should NOT add a parent-PID watchdog (polling adds latency and a race; the job object is the kernel mechanism).

**Implementation shape (for the plans):** in the Tauri shell's Rust code, `CreateJobObjectW(NULL, name)` + `SetInformationJobObject` with `JobObjectExtendedLimitInformation` and `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, then `AssignProcessToJobObject` right after `CreateProcess` (before the child can spawn its own children). Keep the job handle alive for the shell's lifetime. This is a few dozen lines via the `windows` crate or `windows-sys`, pinned per D-14.

## 2. The updater conflict - one channel, two manifest formats

**Finding: the conflict is real but structural, not architectural.** Two consumers of one GitHub Releases channel:

| Consumer | Manifest/asset format | Verified |
|---|---|---|
| Phase 2.1 Python updater (`surfaces/update.py`) | GitHub API `/releases/latest` + `SHA256SUMS.txt` asset; digest verification via `verify_digest()`/`parse_sha256sums()` | [VERIFIED: read this session - `_GITHUB_API` line 62, `parse_sha256sums` line 112] |
| `tauri-plugin-updater` (shell) | `latest.json` endpoint (`{version, notes, pub_date, platforms: {windows-x86_64: {signature, url}}}`), minisign signature over the installer | [CITED: tauri.app/plugin/updater/ - the manifest format and the endpoint config `endpoints: ["https://.../latest.json"]`] |

Consequences the plans must carry:

1. **The release pipeline publishes both.** The existing `build.py` already writes `SHA256SUMS.txt`; the 13 build adds a `latest.json` generator and a minisign signing step for the NSIS installer. Both assets attach to the same release. One release channel (D-08) literally: same tag, same assets.
2. **Scope separation:** the Tauri updater replaces the shell + bundled sidecar (`tauri-plugin-updater` replaces the app install directory); the Python updater continues to update the `.pyz`/runtime where the user runs the CLI path. The shell must never attempt to update the `.pyz` and the Python updater never replaces the shell. The `update_policy` setting stays the single consent source; the shell's disclosure renders the same locked text with one `notified_at` record (13-UI-SPEC 7.2 - one disclosure covers both consumers).
3. **Version coherence:** the shell's version and the sidecar's version should be checked at handshake (the sidecar prints its version on the stdout handshake); a mismatch renders the `crashed`/`unreachable` state per 13-UI-SPEC 3.3 rather than silently running mismatched halves.

## 3. Toolchain verification and the build shape

**Verified on this machine (2026-08-10):**

| Tool | Status | Note |
|---|---|---|
| `rustc` 1.97.1 / `cargo` | PRESENT | [VERIFIED: `rustc --version`] - pin the exact version in the CI workflow and the lockfile |
| `node` 22.22.3 / `npm` | PRESENT | Tauri CLI runs through npm/npx or cargo; pin per D-14 |
| Python 3.13.5 | PRESENT | CI pins 3.11 (`.github/workflows/ci.yml:12`); the plan must pin the sidecar build Python explicitly (3.11 for CI parity) |
| PyInstaller | ABSENT | Added as a pinned dependency with checksum + license review (D-14) |
| NSIS / makensis | ABSENT | Added as a pinned toolchain dependency (D-14); `tauri-build` can invoke NSIS via `bundle > nsis` config |

**Build shape:** PyInstaller **onedir** (never onefile - self-extraction to temp on every launch is the strongest AV false-positive trigger, per Q8 research), wrapping the existing Phase 2.1 `.pyz`/daemon entry, not a second build of the runtime. The sidecar binary gets the `-$TARGET_TRIPLE` suffix Tauri's `bundle.externalBin` requires [CITED: Tauri sidecar docs]. Target installed size 25-45 MB (D-09), measured at verification time.

## 4. The AV / signing checklist (D-10/D-11)

The 13-UI-SPEC 6.1 already locks the install-notice copy for both the signed and unsigned branches. Research adds the operational checklist the plan must execute: (a) name the certificate or ship unsigned with SmartScreen warnings documented (D-11); (b) if signed: Authenticode-sign the shell and the installer, submit to Microsoft's false-positive reporting path, record a VirusTotal baseline; (c) the `install_notice` copy renders the real certificate subject/fingerprint or the real SHA-256 - never a placeholder.

## 5. Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| Rust/cargo | Tauri shell | YES | 1.97.1 | Pin exact version in CI |
| Node/npm | Tauri CLI | YES | 22.22.3 | npx @tauri-apps/cli pinned |
| Python | Sidecar | YES | 3.13.5 (CI 3.11) | Pin 3.11 for CI parity |
| PyInstaller | Sidecar freeze | NO - add pinned | latest pinned | None - it is the chosen mechanism (D-14) |
| NSIS | Installer | NO - add pinned | per tauri-bundler | None - it is the chosen mechanism (D-07) |
| Code-signing identity | Signed release | UNKNOWN until named | - | Ship unsigned honestly per D-11 |

**Missing dependencies with no fallback:** none - every mechanism is either present or explicitly chosen-and-pinned (D-14).

## Assumptions Log

| # | Claim | Risk if Wrong |
|---|---|---|
| A1 | Job Objects with KILL_ON_JOB_CLOSE is the correct Windows mechanism for D-05 (vs a parent-PID watchdog) | If the job assignment races the sidecar spawning its own children, a grandchild could escape; mitigated by assigning the process to the job immediately after CreateProcess, before the daemon thread spawns anything |
| A2 | Tauri 2.x's sidecar plugin cleans up children on graceful exit, and the job object covers ungraceful exit | If the plugin does not clean up on a normal exit path, the shell's own exit handler + job object still cover both paths - belt and suspenders, not either/or |
| A3 | The updater's `latest.json` + minisign signature format is as documented | MEDIUM confidence - cited from primary docs, not exercised against a live release; the plan's updater task verifies against the real tauri-plugin-updater behavior at implementation time |
| A4 | PyInstaller/NSIS toolchain versions pin cleanly on Windows | Standard practice; the lockfile and CI job make it reproducible |

## Open Questions

1. **Which certificate, held by whom** (D-11) - owed to the plan, not research; the plan names it or ships unsigned.
2. **The exact stdout handshake framing** (port + token + version lines) - Claude's discretion per CONTEXT; the plan fixes a concrete framing.
3. **PyInstaller version pin** - resolved at plan time (the plan pins it with checksum + license review).

## Validation Architecture

- Framework: the repo's stdlib fail() harness (`tests/*_roundtrip.py`), plus a new `tests/packaging_shell_roundtrip.py` for the sidecar handshake and lifecycle (a real subprocess test: spawn the sidecar entry, read the handshake, kill the parent, assert the child's port is released).
- The D-12 headless test (CLI works without the shell) reuses the existing `tests/daemon_roundtrip.py` and `tests/launcher_roundtrip.py`.
- The lifecycle test on Windows is the executable proof of criterion 3: start the shell-spawned sidecar, `taskkill /F` the shell, poll the sidecar PID and the port until both are gone.

## Sources

- Microsoft Learn - Job Objects (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`), primary, HIGH.
- Tauri v2 sidecar docs (v2.tauri.app/develop/sidecar/ - `bundle.externalBin`, `Command::sidecar`, `-$TARGET_TRIPLE` suffix), primary, HIGH.
- Tauri updater plugin docs (tauri.app/plugin/updater/ - `latest.json` manifest, minisign signature, endpoints config), primary, MEDIUM (not exercised this session).
- `.planning/research/2026-08-09-packaging.md` Q8 (keep-Python verdict, onedir-vs-onefile AV reasoning, SiYuan precedent), HIGH.
- `surfaces/update.py` (read this session - `_GITHUB_API`, `parse_sha256sums`, `verify_digest`), HIGH.
- `surfaces/daemon.py` `probe()`/`start_server()` (read this session - the three-case startup the sidecar composes with), HIGH.
- `13-UI-SPEC.md` 3.3 (liveness states), 6.1 (install notice), 7 (updater disclosure), 10 (open questions), HIGH.

## Metadata

**Research date:** 2026-08-10
**Valid until:** toolchain pins re-verified at execution time (Rust/cargo/Node move fast; the lockfile is the binding record).
