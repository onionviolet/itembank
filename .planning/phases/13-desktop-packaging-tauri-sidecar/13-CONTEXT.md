# Phase 13: Desktop Packaging — Tauri Shell over the Python Sidecar - Context

**Gathered:** 2026-08-10
**Status:** Ready for planning
**Mode:** autonomous (Directive §2)

<domain>
## Phase Boundary

This phase makes itembank install and launch like a real Windows desktop application, with the same Python runtime, the same scorer, and the same evidence store inside the window that the CLI uses. It delivers a Tauri 2.x shell, a PyInstaller-onedir sidecar of the Phase 2 daemon, an NSIS installer, a signed `tauri-plugin-updater` pointed at the Phase 2.1 release channel, clean process/port lifecycle, and an executed AV/code-signing checklist.

It does **not** port any runtime logic to Rust or JavaScript, add a second IPC protocol, or ship Linux/macOS. The shell is a client of the runtime, never a precondition for it.
</domain>

<decisions>
## Implementation Decisions

### Open ruling

- **D-01 (ruling 3 — ADOPTED):** Keep the Python runtime; Tauri 2.x shell over a PyInstaller sidecar; NSIS installer; this phase number. Porting the runtime to a JS/Rust stack would temporarily create **two scorers** — the one anti-pattern Directive §4.2 forbids outright — and SiYuan's kernel-behind-webview architecture is shipping proof of the pattern. — **Reversibility:** costly — the shell is thin and replaceable, but an installer, a signing identity, and an update channel accrue installed users. Nothing else in the roadmap depends on the answer.

### Process and transport

- **D-02 (one transport):** The shell talks to the sidecar over the **existing localhost HTTP surface** — the same daemon Phase 2 built, reached the same way. No Tauri command bridge duplicating a route, no second IPC protocol. A route the shell needs and the CLI lacks is a bug in the route, not a reason for a bridge.
- **D-03 (port discovery):** The sidecar **announces its bound port on stdout** and the shell reads it; the shell does not assume a fixed port and does not scan. This reuses `server.bind()`'s existing OS-port fallback (added for Windows Hyper-V reserved ranges) rather than fighting it. — **Reversibility:** reversible.
- **D-04 (loopback auth):** The daemon binds `127.0.0.1` only and requires a **per-launch token** passed by the shell, because any local process can reach a loopback port. The token is generated at sidecar start and handed to the shell on the same stdout channel as the port. The CLI path is unaffected.
- **D-05 (lifecycle, criterion 3):** Killing the shell leaves **no orphaned sidecar and no held port**. The shell owns the child and terminates it on exit; on Windows the sidecar is additionally placed in a **job object** so a hard kill of the parent takes the child with it, because graceful shutdown handlers do not run on `TerminateProcess`.
- **D-06 (second launch):** A second launch **attaches to the running instance and focuses its window**, rather than racing or refusing. Single-instance is enforced by a named mutex, not by a lock file, because a lock file survives a crash and a mutex does not. If attach fails, the second launch **refuses by name** and does not start a competing sidecar.

### Distribution

- **D-07 (installer):** NSIS, per-user install by default (no elevation), with a machine-wide option. Per-user avoids the UAC prompt that makes a personal tool feel like enterprise software, and it keeps the evidence store in the user profile where it already lives.
- **D-08 (updater):** `tauri-plugin-updater`, **signed**, reading the **same GitHub Releases** the Phase 2.1 updater already uses. One release channel, two consumers. The `update_policy` divergence recorded in `CLAUDE.md` (schema default `opt_in`, this repo's own settings `check_on_launch`) is deliberate and carries forward unchanged — the shell does not get a third policy.
- **D-09 (size, criterion 4):** Target roughly **25–45 MB** installed. PyInstaller **onedir**, not onefile: onefile extracts to temp on every launch, which is slower and is the single strongest AV false-positive trigger. Size is measured and reported in the plan's verification, not asserted.
- **D-10 (AV, criterion 4 — the named top risk):** The code-signing and AV checklist is **written and executed** in this phase, not deferred. It includes: an Authenticode signature on the shell and the installer, submission to Microsoft's false-positive reporting path, a VirusTotal baseline recorded at release, and a documented user-facing remediation note. AV false positives on frozen Python are a named risk with prior art, not a hypothetical. — **Reversibility:** the signing identity is effectively one-way — reputation accrues to a certificate, so switching certificates later resets SmartScreen reputation. Choose once.
- **D-11 (signing identity):** The plan must **name what certificate is used and who holds it** before the first signed release. If no certificate is available yet, the plan ships unsigned with SmartScreen warnings documented in plain language — it does not pretend the problem is solved and does not invent a certificate that does not exist.

### Boundaries

- **D-12 (criterion 5, non-negotiable):** Every capability stays reachable from the CLI **without the shell installed**. A feature that only works inside the window is a defect in this phase, and the plan carries a test that runs the full loop headless.
- **D-13 (criterion 6):** Linux (WebKitGTK) and macOS are **deferred to hardware**, with **Electron recorded as the named Linux fallback** rather than silently unresolved. Naming the fallback now is what keeps the deferral honest.
- **D-14 (supply chain, Directive §4a):** Rust crates, the Tauri toolchain, and PyInstaller are pinned with recorded checksums and a named license review, following the KaTeX precedent. A lockfile is committed. "No dependency" stopped being a security control on 2026-08-09; pinning is what replaced it.
- **D-15 (no new UI):** The shell renders the **existing** daemon surfaces. This phase adds no screen, no navigation, and no theming of its own beyond window chrome — Phase 4's tokens and `UI-SPEC.md` §8's nine gates already govern what is inside the window, and a native menu that duplicates an in-page control is a second surface for one decision.

### Claude's discretion

Window chrome details, the exact stdout handshake framing, build-script factoring, and CI job layout are open. Not open: one transport, onedir, per-launch token, job-object cleanup, CLI-without-shell, the executed AV checklist, and the single release channel.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Binding rules
- `.planning/PLANNING-DIRECTIVES.md` — §2, §4.2 (one scorer — the whole reason for D-01), §4.3, §4a (supply chain, and "no dependencies as a security control does not exist").
- `.claude/CLAUDE.md` — Constraints as amended 2026-08-09 (a packaged desktop app is an end goal); the `update_policy` divergence D-08 carries forward.
- `.planning/UI-SPEC.md` §8 items 1–9 — still binding inside the window.
- `.planning/ROADMAP.md` §"Phase 13" criteria 1–6.

### Research verdicts
- `.planning/research/2026-08-09-packaging.md` Q8 — **keep the Python runtime**; SiYuan's kernel-behind-webview as shipping proof.

### Upstream phases
- `.planning/phases/02-daemon-consolidation-settings-foundation/02-CONTEXT.md` — the daemon the sidecar wraps.
- `.planning/phases/02.1-packaging-self-update-interop-export/02.1-CONTEXT.md` and `02.1-VERIFICATION.md` — the `.pyz`, the updater, and the release channel this phase reuses.
- `.planning/phases/04-surface-redesign-theming/04-CONTEXT.md` — the surfaces rendered inside the window.

### Code the plans must read before changing
- `server.py` `bind()` — the OS-port fallback D-03 depends on.
- `surfaces/daemon.py` — the sidecar's entry point.
- `surfaces/launcher.py` — existing launch behavior the shell must not duplicate.
- `surfaces/update.py` — the Phase 2.1 updater sharing the channel with D-08.
- `.github/workflows/ci.yml` — where the signed build job lands.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- `server.bind()` already handles Windows reserved-port ranges; D-03 reads its result instead of re-solving the problem.
- `surfaces/update.py` already talks to GitHub Releases through stdlib `urllib` — one channel, and the Tauri updater becomes its second consumer.
- `surfaces/launcher.py` already knows how to open a surface; the shell replaces the browser, not the launcher's logic.
- Phase 2.1's `.pyz` build is the artifact PyInstaller wraps — this phase does not invent a second build of the runtime.

### Established patterns
- The runtime is the product; every surface is a client (`itembank.py` four-layer docstring). The shell is one more client.
- Named refusal over silent failure — D-06's failed attach follows it.

### Integration points
- Sidecar stdout handshake (port + token) is the only new protocol surface in this phase, and it is a handshake, not an IPC channel.
- The evidence store and banks stay on disk in the user profile; the installer must not relocate them (Directive §4.3).
</code_context>

<specifics>
## Specific Ideas

- The point of D-01, stated plainly so a later reviewer does not re-open it: this phase exists to make the thing installable, **not** to modernize the stack. Any plan task that rewrites runtime logic in Rust or JS has misread the phase.
</specifics>

<deferred>
## Deferred Ideas

- **Linux and macOS builds** — deferred to hardware; Electron is the named Linux fallback (D-13).
- Auto-start on login, tray residency, and OS notification integration — none are in the criteria; each is its own small phase if wanted.
- File-association handling for `.md` banks — plausible and cheap, but not scoped here.
</deferred>

---

*Phase: 13-desktop-packaging-tauri-sidecar*
*Context gathered: 2026-08-10*
