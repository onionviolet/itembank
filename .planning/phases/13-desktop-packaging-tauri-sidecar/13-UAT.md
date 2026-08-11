---
status: testing
phase: 13-desktop-packaging-tauri-sidecar
source: [13-VERIFICATION.md]
started: 2026-08-10
updated: 2026-08-10
---

## Current Test

number: 1
name: Compiled installer lifecycle (per-user install + uninstall preserving evidence)
expected: |
  With NSIS (makensis) installed, `scripts/build_shell.ps1` produces
  `dist/itembank-<v>-setup.exe`; installing per-user launches the app and the
  daemon serves; uninstalling removes only the application directory while
  the user-profile evidence store and banks survive (13-UI-SPEC 6.2).
awaiting: user response

## Tests

### 1. Compiled installer lifecycle (per-user install + uninstall preserving evidence)
expected: installer installs per-user, app launches and serves, uninstall leaves profile evidence/banks intact
result: [pending]

### 2. Install-notice rendering with real values
expected: the signed or unsigned notice renders 13-UI-SPEC 6.1 copy verbatim with real certificate/SHA-256 values, never a placeholder
result: [pending]

### 3. Release-time AV checklist (VirusTotal baseline + Microsoft submission)
expected: at the first real release, a VirusTotal baseline is recorded and the Microsoft false-positive submission path is used if needed
result: [pending]

### 4. Signed update install flow
expected: with a real minisign pubkey/signature and a release asset, tauri-plugin-updater verifies and installs, restarting the app with the locked 7.3 copy
result: [pending]

### 5. Window liveness states visual pass
expected: the five states render the locked 3.3 copy with the spec'd recovery actions in the real window
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps

- makensis (NSIS 3.x) absent on the build machine -- compiled-installer items pending the toolchain.
- No signing certificate / minisign key / release asset yet -- signing and live-update items pending a real release.
