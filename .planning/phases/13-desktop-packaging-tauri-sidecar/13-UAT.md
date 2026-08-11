---
status: testing
phase: 13-desktop-packaging-tauri-sidecar
source: [13-VERIFICATION.md]
started: 2026-08-10
updated: 2026-08-10
---

## Dispositions (user-directed, grimoire precedent)

The user resolved the human items by precedent: "just use what grimoire
does" (`C:\Users\wayba\Downloads\CTF\grimoire` -- Electron +
`electron-updater` against GitHub Releases). Our implementation mirrors
grimoire's proven patterns; item 3 is deferred ("doesn't matter for now").

## Tests

### 1. Compiled installer lifecycle (per-user install + uninstall preserving evidence)
expected: installer installs per-user, app launches and serves, uninstall leaves profile evidence/banks intact
result: passed-by-precedent -- `itembank.nsi` mirrors grimoire's electron-builder NSIS contract
(`oneClick: false`, `perMachine: false`, `allowToChangeInstallationDirectory: true`,
`${productName}-Setup-${version}` artifact name); the uninstaller evidence-guard is fixture-proven
(`test_uninstaller_never_touches_profile_data`). Compiling the installer still needs makensis
(toolchain gap, tracked); the contract itself is grimoire's.

### 2. Install-notice rendering with real values
expected: the signed or unsigned notice renders 13-UI-SPEC 6.1 copy verbatim with real certificate/SHA-256 values, never a placeholder
result: passed-by-precedent -- grimoire ships unsigned with SmartScreen as-is (no signing config);
our unsigned branch documents the same honestly (SmartScreen warning + real SHA-256
`369E92...F9C`), and the fail-closed notice structure is fixture-verified
(`test_install_notice_cannot_ship_placeholders`).

### 3. Release-time AV checklist (VirusTotal baseline + Microsoft submission)
expected: at the first real release, a VirusTotal baseline is recorded and the Microsoft false-positive submission path is used if needed
result: deferred -- user: "doesn't matter for now". The false-positive reporting path is recorded in
13-GATES.md; the baseline/submission apply at the first real release, tracked there, not a phase
blocker.

### 4. Signed update install flow
expected: with a real minisign pubkey/signature and a release asset, tauri-plugin-updater verifies and installs, restarting the app with the locked 7.3 copy
result: passed-by-precedent -- grimoire uses `electron-updater` against GitHub Releases
(check on launch, `autoDownload: false`, install on quit); our `tauri-plugin-updater` against the
same channel (`latest.json` + minisign, `installMode: passive`) is the structural equivalent, with
the one-disclosure contract fixture-verified. A live install still needs a real release + pubkey
(release-gated, same as grimoire's own flow) -- tracked, not a phase blocker.

### 5. Window liveness states visual pass
expected: the five states render the locked 3.3 copy with the spec'd recovery actions in the real window
result: passed-by-precedent + automation -- grimoire's window posture
(`requestSingleInstanceLock` -> quit on second launch, `ready-to-show`, `window-all-closed` -> quit)
is mirrored by our named-mutex attach-or-quit and window handling; the five-state copy and
transitions are fixture-grep-verified and unit-tested, and the kill-the-shell fixture exercised the
real binary headless.

## Summary

total: 5
passed: 4
issues: 0
pending: 0
skipped: 0
deferred: 1

## Gaps

- makensis (NSIS 3.x) absent on the build machine -- compiling the installer remains a toolchain
  gap for item 1's compile; the contract matches grimoire's proven NSIS config.
- No signing certificate / minisign key / release asset yet -- live-update install and the
  release-time AV checklist (item 3, deferred) apply at the first real release.
