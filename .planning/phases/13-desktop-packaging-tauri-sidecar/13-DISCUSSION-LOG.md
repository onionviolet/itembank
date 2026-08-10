# Phase 13: Desktop Packaging — Tauri Shell over the Python Sidecar - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-08-10
**Phase:** 13-desktop-packaging-tauri-sidecar
**Mode:** autonomous, per `PLANNING-DIRECTIVES.md` §1/§2. No question was put to the user.
**Areas discussed:** ruling 3 (keep Python), transport, port discovery and auth, process lifecycle, second launch, install scope, PyInstaller mode, AV and signing, platform deferral

---

## Ruling 3 — keep the Python runtime?

| Option | Description | Selected |
|--------|-------------|----------|
| Tauri 2.x shell over a PyInstaller sidecar, NSIS installer | Runtime untouched; SiYuan is shipping proof of the pattern | ✓ |
| Port the runtime to Rust/JS | Native single binary | |
| Electron over the same sidecar | Familiar, heavier | |

**Choice:** keep Python. **Notes:** a port would temporarily create **two scorers**, the one anti-pattern Directive §4.2 forbids outright. That is the whole argument; size and startup are secondary. Electron is recorded as the named Linux fallback, not the Windows choice.

---

## Transport

| Option | Description | Selected |
|--------|-------------|----------|
| The existing localhost HTTP surface | One protocol, shared with the CLI | ✓ |
| Tauri command bridge | Tighter integration | |

**Choice:** existing HTTP. **Notes:** a bridge would be a second IPC protocol. A route the shell needs and the CLI lacks is a bug in the route, not a reason for a bridge.

---

## Port discovery and auth

| Option | Description | Selected |
|--------|-------------|----------|
| Sidecar announces port + per-launch token on stdout | Reuses `server.bind()`'s OS-port fallback | ✓ |
| Fixed port | Simpler | |
| Port scan | No handshake needed | |

**Choice:** stdout handshake. **Notes:** the fallback exists because Windows Hyper-V reserves ranges — assuming a fixed port fights code that already solved this. The token is there because any local process can reach a loopback port.

---

## Process lifecycle and second launch

| Option | Description | Selected |
|--------|-------------|----------|
| Shell owns the child; Windows job object; named-mutex single instance, second launch attaches and focuses | Survives a hard kill of the parent | ✓ |
| Graceful shutdown handler only | Simpler | |
| Lock file for single instance | Familiar | |

**Choice:** job object + mutex. **Notes:** graceful handlers do not run on `TerminateProcess`, which is exactly the case criterion 3 is about. A lock file survives a crash; a mutex does not.

---

## Install scope

| Option | Description | Selected |
|--------|-------------|----------|
| Per-user by default, machine-wide optional | No UAC prompt; evidence stays in the user profile | ✓ |
| Machine-wide only | Conventional | |

**Choice:** per-user default. **Notes:** a UAC prompt makes a one-user personal tool feel like enterprise software.

---

## PyInstaller mode

| Option | Description | Selected |
|--------|-------------|----------|
| onedir | No temp extraction per launch | ✓ |
| onefile | Single file, tidier | |

**Choice:** onedir. **Notes:** onefile extracts to temp on every launch — slower, and the single strongest AV false-positive trigger. AV is the named top risk here, so this is not a close call.

---

## AV and code signing

| Option | Description | Selected |
|--------|-------------|----------|
| Checklist written **and executed** this phase; certificate named before first signed release | Authenticode, MS false-positive submission, VirusTotal baseline, user remediation note | ✓ |
| Defer signing to a later phase | Ship sooner | |

**Choice:** execute now. **Notes:** criterion 4 names AV false positives as the top risk, not a hypothetical. If no certificate exists, the plan ships unsigned with SmartScreen warnings documented plainly — it does not invent a certificate. Rated effectively one-way: SmartScreen reputation accrues to a certificate, so switching later resets it.

---

## Platform deferral

| Option | Description | Selected |
|--------|-------------|----------|
| Windows now; Linux/macOS deferred to hardware, Electron named as the Linux fallback | Deferral with a named answer | ✓ |
| Attempt all three | Broader | |

**Choice:** defer with the fallback named. **Notes:** naming the fallback is what keeps the deferral honest rather than silently unresolved.

---

## Claude's Discretion

Window chrome, stdout handshake framing, build-script factoring, CI job layout.

## Deferred Ideas

Linux and macOS builds; auto-start on login; tray residency; OS notifications; `.md` file associations. None are in the criteria; each is its own small phase if wanted.
