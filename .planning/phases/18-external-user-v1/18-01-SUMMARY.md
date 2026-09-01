---
phase: 18-external-user-v1
plan: 01
subsystem: infra
tags: [packaging, signing, smartscreen, decisions]

requires:
  - phase: 13-desktop-packaging-tauri-sidecar
    provides: the shipped shell, build script, and packaging fixtures this plan rebuilds and cites
provides:
  - "18-DECISIONS.md with the IL-20260815-11 (D-01) resolution record and the dated D-02 signing cost decision"
  - "the README SmartScreen workaround at the release-download step"
  - "the honest rebuild-blocked record with the shipped-artifact hash 18-03 can cite"
affects: [18-03]

requirements-completed: [A10-C1 (partial: signing record and workaround copy landed; rebuild blocked on host, see below)]

completed: 2026-09-01
status: complete-with-blocked-truth
---

# Phase 18 Plan 01 Summary: rebuild evidence, the packaging resolution record, and the signing decision

Executed 2026-09-01 under the standing directive of the same date (human
reviews deferred; recorded context decisions transcribed, not re-litigated).

## Task 1: Rebuild the packaged artifact. BLOCKED on this host, recorded honestly

The must-have truth "The Phase 13 shell rebuilds from current main and the
rebuilt artifact passes every shipped packaging fixture" is **blocked**, not
faked. The Phase 13 build recipe is Windows-only and this execution host is
an arm64 Mac (Darwin 27.0.0, aarch64-apple-darwin). The precise gaps:

- `powershell` and `pwsh` are both absent; `scripts/build_shell.ps1` cannot
  run at all.
- PyInstaller is not installed, and the pin in `requirements-build.txt` is
  the Windows wheel (`pyinstaller-6.22.0-py3-none-win_amd64.whl`, sha256
  `6e5f36...4853`); a macOS PyInstaller would be a new third-party artifact
  requiring SUPPLY-CHAIN-POLICY.md section 3 review, and would produce an
  aarch64-apple-darwin sidecar, not the shipped
  `itembank-sidecar-x86_64-pc-windows-msvc.exe`.
- `makensis` is absent (same recorded gap as 13-03).
- The Tauri crate cannot even compile here: its build script requires
  `src-tauri/binaries/itembank-sidecar-aarch64-apple-darwin`, which Phase 13
  never shipped (Windows triple only).

Per the executor directive, no new global tooling was installed. The rebuild
must run on the Windows build machine that produced the Phase 13 artifact
(rustc/cargo 1.97.1 stable-x86_64-pc-windows-msvc, PyInstaller 6.22.0,
Node 22.22.3, per requirements-build.txt and 13-03-SUMMARY.md).

### Fixture commands run on this host, verbatim exit states

| Command | Exit | Notes |
|---|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts/build_shell.ps1` | not runnable | `powershell not found`, `pwsh not found` |
| `python tests/packaging_roundtrip.py` | 0 | passes; prints the honest skip: "SKIP: dist/itembank-sidecar-onedir is not built -- the onedir sidecar checks did not run. Build it with powershell -File scripts/build_shell.ps1 (Windows) to cover them." |
| `python tests/packaging_shell_roundtrip.py` | 0 | "ok: packaging shell roundtrip served 10 checks"; prints "skip: itembank-shell.exe not built -- run cargo build first" |
| `cargo test --manifest-path src-tauri/Cargo.toml` | 101 | build-script failure: "resource path `binaries/itembank-sidecar-aarch64-apple-darwin` doesn't exist"; the crate targets the Windows triple and has no macOS sidecar to bundle |

### Shipped-artifact evidence (the artifact as present in the tree, not a rebuild)

- Path: `src-tauri/binaries/itembank-sidecar-x86_64-pc-windows-msvc.exe`
- Size: 2,580,996 bytes (this is the single frozen exe committed for the
  shell's externalBin; the full onedir tree, measured 28.8 MiB at 13-03, is
  a build output and is not in the tree)
- SHA-256: `8b019efd6b6db4b2f3fc3426c2b69d98411495154905aa44395316512ac9684e`
- Last built into the tree by commit `0b243c8`, 2026-08-10 22:19:32 -0500
  (the Phase 13 build session).

18-03's gates criterion 1 row cannot cite fresh rebuild hashes until the
rebuild runs on the Windows build machine; it can cite this shipped-artifact
hash and this blocked record in the interim.

### makensis state

Absent on this host, exactly as 13-03 recorded for the original build
machine. The honest skip remains the passing behavior.

## Task 2: IL-20260815-11 resolution recorded

`.planning/phases/18-external-user-v1/18-DECISIONS.md` created with the
dated entry "IL-20260815-11 resolved (18-CONTEXT D-01), 2026-08-17",
transcribing D-01: the Phase 13 shell is the delivery vehicle, one canonical
browser-served UI (17A-CONTEXT D-08, IL-20260816-02), the "no build step"
reading and the miscited DEL-02 ground (F9, F15) are dead, no new freezer
adopted. Verified: `python itembank.py guard .` exits 0.

## Task 3: Signing cost decision (checkpoint)

- Question presented: buy a Windows Authenticode OV certificate, join the
  Apple Developer Program (macOS only, deferred with reason), or ship
  unsigned for v1 with documented workarounds.
- Quote gathered 2026-09-01 from SSL Dragon
  (ssldragon.com/ssl-certificates/code-signing/): Sectigo OV 219 USD/yr,
  Comodo OV 219 USD/yr, DigiCert OV 400 USD/yr; inside D-02's 100 to 400
  USD/yr estimate.
- Weibao's live answer: DEFERRED, owed to Weibao (2026-09-01), per the
  standing directive deferring human checkpoints. The 18-CONTEXT D-02
  recorded default (unsigned for v1 with documented workarounds, revisit on
  wider distribution) is transcribed as the standing decision; the entry in
  18-DECISIONS.md names Task 4's README copy as the compensating control
  and notes any certificate purchase is Weibao's own later action.

## Task 4: SmartScreen workaround copy

The exact plan copy landed in README.md inside the release-download step
(the "Fetch the code" step of "If you are an AI assistant onboarding a new
user", the step naming GitHub Releases and SHA256SUMS.txt). The macOS
Gatekeeper workaround in the Install section is untouched.
`installers/nsis/itembank.nsi` untouched. Verified:
`python tests/packaging_roundtrip.py` exits 0
(test_install_notice_cannot_ship_placeholders green) and
`python scripts/check_readme_commands.py` exits 0.

## Deviations from plan

1. Task 1 rebuild blocked by host platform (detail above). Every other
   task completed; the plan's degraded-state clause covers the makensis
   gap but not the missing powershell/PyInstaller/Windows host, so this is
   recorded as a blocked truth, prominent in this summary.
2. Task 3's live checkpoint answer deferred to Weibao under the 2026-09-01
   standing directive; the recorded D-02 default is transcribed instead of
   an executor-invented answer.
3. `python` on this host is Python 3.14.6 invoked as `python3`; commands
   were run with `python3` where the plan writes `python`.

## Verification snapshot (2026-09-01, repo root)

- `python3 tests/packaging_roundtrip.py` exit 0
- `python3 tests/packaging_shell_roundtrip.py` exit 0
- `cargo test --manifest-path src-tauri/Cargo.toml` exit 101 (host gap above)
- `python3 itembank.py guard .` exit 0
- `python3 scripts/check_readme_commands.py` exit 0
- em dash scan of README.md and 18-DECISIONS.md: clean
