# Q8 — Packaging Path to a Real Installer (Keep or Replace the Python Runtime)

---
date: 2026-08-09
topic: "Q8 packaging — Tauri+Python sidecar vs Electron vs PyInstaller-alone vs newer options; keep vs port the Python runtime"
confidence:
  verdict: HIGH
  tauri_sidecar: HIGH (official docs + multiple working examples)
  electron: MEDIUM (docs + community benchmarks; size numbers vary by source)
  python_alone: HIGH (official Briefcase/pywebview/Nuitka docs)
  newer_options: MEDIUM (PyApp/PyTauri verified current; maturity judgments are mine)
  sizes_and_estimates: LOW-MEDIUM (ranges, tagged ASSUMED)
  migration_plan: MEDIUM (synthesis, not verifiable externally)
---

## User Constraints (binding, from RESEARCH-BRIEF §1)

- Stdlib-only / no-build-step / Python-only / offline-first are now **preferences**, not rules. **A packaged desktop app is an end goal.** (Weibao, 2026-08-09, verbatim in the brief.)
- Non-negotiable: runtime (not model) gates what reaches the learner; **one parser, one scorer, one evidence store**; evidence/banks stay on disk, no telemetry; additive format changes; UI-SPEC accessibility gates; core loop **degrades, never blocks** offline.
- Open recommendation Weibao has NOT ruled on: keep Python runtime as a Tauri sidecar. This document argues that recommendation; the decision itself stays open until he rules.
- Roadmap note: the numbered "Phase 12" slot is **retired** (packaging pulled forward to 2.1, which shipped a `.pyz` + launcher shims + self-updater — *not* a real installer). "Phase 12" below means "the new installer/packaging phase to be inserted," whatever number it gets. [VERIFIED: .planning/ROADMAP.md lines 55, 518-520 — "~~Phase 12: Packaging, Self-Update & Interop Export~~ - MOVED to Phase 2.1 (2026-08-07) — see Phase 2.1 above. Slot retired, not reused." and "This numbered slot is retired: do not plan or execute against 'Phase 12' and do not reuse this number for new work."]

## Summary

**Verdict: KEEP the Python runtime. Package it as a PyInstaller-frozen sidecar under a thin Tauri 2.x shell.** [PACKAGING] [RUNTIME]

The four completed phases (parser `model.py`, the one scorer `runtime.py`, evidence store, daemon `surfaces/daemon.py`, plus the update/GIFT/settings surfaces, all covered by a 15-file test suite per 02.1-VERIFICATION) are the differentiating asset. Porting them to Rust or TypeScript re-opens the single most dangerous class of bug this product can have — scoring divergence — for zero user-visible gain. The sidecar's operational costs (lifecycle, ports, AV false positives, ~30 MB of frozen Python) are all known, bounded, and documented below with mitigations. The local-model future makes the argument stronger, not weaker: llama.cpp/Ollama is *another* localhost process no matter what language the runtime is in, so "porting to eliminate the extra process" eliminates nothing — the app is multi-process either way.

**Primary recommendation:** Tauri 2.x shell + PyInstaller **onedir** frozen daemon as sidecar + localhost HTTP IPC (the existing daemon *is* the IPC layer) + NSIS installer + `tauri-plugin-updater` + Azure Artifact Signing. Dev mode (`python itembank.py daemon .`) remains a first-class supported path forever.

---

## 1. Tauri 2.x + Python Sidecar — state of the art [PACKAGING]

### Sidecar support
- First-class and documented: `bundle.externalBin` in `tauri.conf.json` bundles any binary; the shell plugin's `Command::sidecar` spawns it with automatic cleanup of spawned children on app exit. Binaries need a `-$TARGET_TRIPLE` filename suffix per platform. [CITED: v2.tauri.app/develop/sidecar/]
- The dominant, repeatedly-documented pattern in 2025-2026 is exactly ours: **a Python HTTP server frozen with PyInstaller, spawned as a sidecar, with the webview talking to it over localhost**. Working public examples: `dieharders/example-tauri-v2-python-server-sidecar` (Next.js + FastAPI on localhost:8008), the pandas-sidecar writeup at mclare.blog, upskil.dev's guide, and a production-oriented LLM-app walkthrough (Tauri + FastAPI + PyInstaller + llama.cpp DLLs in one sidecar). [CITED: github.com/dieharders/example-tauri-v2-python-server-sidecar; mclare.blog/posts/writing-a-pandas-sidecar-for-tauri/; aiechoes.substack.com/p/building-production-ready-desktop]

### Frozen sidecar vs embedded CPython
- **PyInstaller onedir** is the standard route and the right one here: stdlib-only code means no hidden-import hell; onedir (not onefile) avoids the self-extraction behavior that trips AV heuristics. [CITED: pythonguis.com/faq/problems-with-antivirus-software-and-pyinstaller/]
- **Embedded CPython via python-build-standalone** is the alternative (ship the interpreter + source tree). It is what PyTauri uses for its standalone builds; for a general sidecar it means hand-rolling what PyInstaller automates. Viable fallback if PyInstaller AV problems prove intractable, since it ships the stock signed-ish python DLLs rather than a PyInstaller bootloader. [CITED: pytauri.github.io/pytauri/0.4/usage/tutorial/build-standalone/]
- **PyTauri** (Tauri bindings for Python through PyO3, v0.8.0 on PyPI, actively maintained through July 2026, 19+ plugin bindings) eliminates the sidecar entirely by running Python *inside* the Tauri process. Interesting, but it couples the runtime's lifetime to the GUI process — which breaks our "CLI and daemon are both clients of the same runtime" surface rule and the headless/agent use cases. Watch, don't adopt. [CITED: github.com/pytauri/pytauri; pypi.org/project/pytauri/]

### IPC: localhost HTTP vs stdio
- Both are used in the wild; **localhost HTTP wins for itembank specifically** because the daemon already exists, already serves every surface, and already has port-fallback logic (`server.bind`). stdio JSON-RPC would mean building a second protocol beside the HTTP one — a violation of "both surfaces are clients of the runtime" in spirit. The only stdio use we need: the sidecar should print its bound port/URL on stdout at startup so the shell learns which port to point the webview at (bind port 0 or reuse the existing fallback chain — this also dissolves the port-conflict papercut). [ASSUMED — synthesis; pattern matches the dieharders example, which hardcodes 8008 and is worse for it]

### Installer + updater
- Windows: Tauri ships NSIS `.exe` and WiX `.msi` bundlers. **NSIS is the newer, recommended one; pick one format, don't ship both** (MSI→NSIS migration is supported, NSIS→MSI is not; shipping both risks duplicate uninstall entries). [CITED: v2.tauri.app/distribute/windows-installer/; github.com/tauri-apps/tauri/discussions/8963]
- `tauri-plugin-updater` supports NSIS and MSI targets, signs updates with its own minisign-style keypair, supports static JSON or dynamic update servers, and auto-exits the app during install (a Windows-installer limitation). This can serve update artifacts from **GitHub Releases**, exactly where the Phase 2.1 self-updater already points. [CITED: v2.tauri.app/plugin/updater/]
- Linux later: AppImage/deb/rpm bundlers exist; see WebKitGTK caveat below.

### Bundle size / dependencies
- Tauri shell alone: ~5-12 MB installers typical (community benchmarks: ~12 MB average vs ~180 MB Electron; marketing-adjacent sources, treat as directional). [CITED: pkgpulse.com/guides/electron-vs-tauri-2026; buildmvpfast.com/blog/tauri-v2-vs-electron-desktop-apps-2026]
- Our stdlib-only frozen daemon: python3.dll + stdlib + code ≈ 15-35 MB onedir. **Total installer estimate: ~25-45 MB; installed ~60-100 MB; RAM ≈ WebView2 80-150 MB + Python 30-60 MB + shell ~20 MB.** [ASSUMED — estimate; no build performed]
- **WebView2 dependency:** required on Windows; ships with Windows 11 (our target machine) and evergreen-updates itself, so rendering stays a current Chromium. Tauri's installer can bootstrap it on machines that lack it. [CITED: v2.tauri.app/reference/webview-versions/]

### Papercuts (each with mitigation)
| Papercut | Reality | Mitigation | Tag |
|---|---|---|---|
| Sidecar lifecycle / zombies | Real, well-documented: killing the sidecar can orphan *its* children; apps that won't relaunch because the old process holds the port | `Command::sidecar` auto-cleanup + a `POST /shutdown` (or stdin-close watchdog) in the daemon + Windows Job Object / process-group kill; daemon already single-process so no grandchildren today | PACKAGING, cost: ~1 plan [CITED: github.com/tauri-apps/tauri/discussions/3273; github.com/tauri-apps/plugins-workspace/issues/3062] |
| Port conflicts | Real when ports are hardcoded | Bind port 0 (or existing fallback), print bound URL to stdout, shell reads handshake line — `server.bind` already half-does this | PACKAGING, cost: trivial |
| AV false positives on frozen Python | Real, chronic, worst with `--onefile` | Use **onedir**; code-sign (Azure Artifact Signing, **$9.99/mo, open to individuals since April 2026, no 3-year history requirement**); submit false positives to Microsoft; SmartScreen reputation still accumulates over downloads even when signed | PACKAGING, cost: $120/yr + a release-checklist item [CITED: pythonguis.com FAQ; techcommunity.microsoft.com Trusted Signing individual GA; melatonin.dev/blog/code-signing-on-windows-with-azure-trusted-signing/] |
| Linux WebKitGTK instability | Real: blank/flickering windows, mostly NVIDIA DMABUF; performance and feature gaps vs Chromium | 7900 XTX is AMD, the worst reports are NVIDIA-specific; `WEBKIT_DISABLE_DMABUF_RENDERER=1` escape hatch; browser-tab fallback (today's launcher) remains as degrade path | PACKAGING, cost: accept + document [CITED: v2.tauri.app/develop/debug/linux-graphics/; github.com/orgs/tauri-apps/discussions/8524] |
| Rust toolchain enters the repo | New build dependency, CI cross-compile per-target-triple naming for sidecars | Confined to a `shell/` directory; the Python runtime never imports it; brief §1 explicitly permits build steps | PACKAGING, cost: CI work, 1 plan |

## 2. Electron + Python child process [PACKAGING]

- Same architecture (PyInstaller exe spawned via `child_process`, bundled through electron-builder `extraResources`), mature and heavily documented. [CITED: til.simonwillison.net/electron/python-inside-electron; medium.com/@abulka/building-a-deployable-python-electron-app-4e8c807bfa5e]
- Costs: installers ~85-150 MB before the sidecar, RAM 150-500 MB, 1-2 s+ cold start — because it ships Chromium + Node beside a Python we'd also ship (three runtimes for one app). [CITED: blog.openreplay.com/comparing-electron-tauri-desktop-applications/; pkgpulse.com]
- When it still wins: pixel-identical Chromium on every OS (kills the WebKitGTK risk), the most mature updater (`electron-updater`), biggest ecosystem. For a single-user app whose Linux target is one known AMD box, those don't outweigh 100+ MB and triple runtimes. **Rejected, but it is the named fallback if Linux WebKitGTK proves unusable in practice.**

## 3. Python-alone: PyInstaller / Briefcase / Nuitka + (system browser | pywebview) [PACKAGING]

- **Briefcase (BeeWare)** is the strongest pure-Python story in 2026: real Windows MSI with customizable branding, .NET-runtime preconditions, ARM64 builds, active monthly development. What it lacks: **any auto-updater** (its `--update-support` overlay is explicitly fragile), and its GUI story assumes Toga/native — we'd still be a browser page or pywebview window. [CITED: beeware.org/news/buzz/2026/april-2026-status-update/; briefcase.beeware.org/en/stable/reference/platforms/windows/index.html]
- **pywebview 6.2.1** (April 2026) gives window chrome over WebView2 with a Python API — but distribution is still "freeze it yourself with PyInstaller, then build an installer yourself with NSIS/Inno," and auto-update is entirely DIY. It is today's `--app=` Chrome window with fewer papercuts, not an installer story. [CITED: pypi.org/project/pywebview/; pywebview.flowrl.com]
- **Nuitka** compiles to C — but AV mitigation for **standalone mode is gated behind Nuitka Commercial and still "coming"**; malware authors have adopted Nuitka too (ApolloRat), so its AV profile is not better than PyInstaller's. No installer, no updater. [CITED: nuitka.net/doc/commercial.html; cyble.com/blog/apollorat-evasive-malware-compiled-using-nuitka/]
- What Python-alone gives up: the updater (2.1's hand-rolled one only swaps `.pyz` files — it cannot update a frozen exe safely without redoing 2.1 against a new artifact format), a real frameless window (the `--app=` Chrome trick is already flagged human-verify in 02.1), tray/menu/deep-link niceties, and the mobile door Tauri 2 leaves open. **Viable as a modest step up from 2.1, but it plateaus below "real app."**

## 4. Newer 2025-2026 options [PACKAGING]

- **PyApp** (Ofek Lev/Hatch): Rust launcher that fetches python-build-standalone + installs the project via uv on first run (or embeds everything with `PYAPP_DISTRIBUTION_EMBED=1`). Excellent for CLI distribution; no window, no installer, no updater UI. Could someday replace the `.pyz`+shim for the checkout/CLI channel. [CITED: infoworld.com/article/4030697/; github.com/jlevy/py-app-standalone]
- **uv-based installs** (`uv tool install`) — developer-audience only; not an end-user installer.
- **Wails v3** hit **beta** ("v3.0.0-beta.0"), Go-centric; adopting it means a Go shell instead of Rust for no advantage over Tauri here. **Neutralino** remains lightweight but with a far thinner plugin/updater ecosystem. [CITED: v3.wails.io/blog/wails-v3-beta/]
- **Pyodide-in-Tauri** (CPython-on-WASM in the webview): would eliminate the sidecar, but stdlib coverage gaps (no real sockets/subprocess/threads semantics), no filesystem authority over the evidence store without plumbing every I/O call through JS, and it would put the scorer *inside* the surface — structurally the wrong side of the "runtime gates the model" line. Rejected. [CITED: pyodide.org]
- **PyTauri** — see §1; the one to re-evaluate in a year.

## 5. KEEP vs REPLACE — the explicit answer [RUNTIME]

**KEEP.** Reasons, in order:

1. **Porting cost is ~4 phases of proven code plus a parity problem with no oracle.** The parser, the one scorer, canonicalization (`\x1f`/`\x1e` canonical forms), evidence semantics, session atomicity, GIFT escaping, and the redirect-safe updater were each verified through dedicated phases. A Rust/TS port must reproduce byte-for-byte scoring on every item type or silently violate the core invariant ("one scorer"); during any incremental port there would be *two* scorers in the tree — the exact anti-pattern the architecture exists to forbid.
2. **The sidecar's costs are operational, not architectural** — lifecycle, ports, AV, ~30 MB. Every one has a documented mitigation (§1). None of them ever touches scoring correctness.
3. **The local-model future is process-shaped anyway.** llama.cpp's `llama-server` / Ollama on the 7900 XTX is an OpenAI-compatible HTTP server on localhost — a sibling process whatever the runtime language. Production Tauri LLM apps already run this exact three-process shape (shell + backend sidecar + llama-server, or dynamic download of llama-server from GitHub releases on first use). A Rust port would not absorb inference; it would just be a riskier runtime next to the same inference process. [CITED: github.com/dillondesilva/tauri-local-lm; explore.n1n.ai blog; aiechoes.substack.com]
4. **Python is the agent-facing surface.** AI tutors are first-class clients calling the CLI/HTTP protocol; the readable, greppable, plain-Python artifact (2.1's "plain Python inside" success criterion) is a feature for the authoring loop of Phase 11.
5. **What would justify replacing:** if the product later needs the scorer *inside* the webview offline (no sidecar at all, e.g., mobile), a port of `model.py`+`runtime.py` scoring core to TS becomes arguable — but that is a second implementation problem to refuse until forced, and Tauri mobile could still ship the sidecar-less subset differently. Not now.

## 6. Recommended architecture [PACKAGING] [RUNTIME]

```
┌─────────────────────────── itembank.exe (Tauri 2 shell, Rust, ~8 MB) ──────────────┐
│  WebView2 window (Win11) / WebKitGTK (Linux later)                                 │
│  - navigates to http://127.0.0.1:<port>/  (all existing HTML surfaces unchanged)   │
│  - tauri-plugin-updater: checks GitHub Releases, signed NSIS update, relaunch      │
│  - spawns + owns sidecar lifecycle (kill on exit, Job Object)                      │
└───────────────┬────────────────────────────────────────────────────────────────────┘
                │ spawn; read one stdout handshake line: "LISTENING http://127.0.0.1:<port>"
                ▼
┌────────── itembank-daemon (PyInstaller onedir sidecar, ~25 MB) ────────────────────┐
│  Today's runtime, unchanged: model.py → runtime.py (ONE scorer) → surfaces/daemon  │
│  binds 127.0.0.1 port 0 → prints URL; POST /shutdown; serves every surface + CLI   │
│  protocol; evidence + banks on disk in user dirs (never under Program Files)       │
└───────────────┬────────────────────────────────────────────────────────────────────┘
                │ optional, degrade-never-block: OpenAI-compatible HTTP
                ▼
┌────────── model processes (optional) ──────────────────────────────────────────────┐
│  hosted API over network  │  llama-server / Ollama on 127.0.0.1:11434 (7900 XTX)  │
│  unreachable ⇒ tutor goes quiet; quiz/score/lesson/evidence fully functional       │
└────────────────────────────────────────────────────────────────────────────────────┘
Update flow: GitHub Release → updater plugin verifies signature → NSIS silent update
(shell + sidecar together, one version) → app auto-exits → relaunch. The 2.1 .pyz
self-updater remains the updater for the git-checkout / CLI channel only.
```

## 7. Phased migration from `python itembank.py serve` [PACKAGING]

1. **Now → Phase 12: nothing blocks.** Dev/agent mode (`python itembank.py …`) stays supported forever; the installer is an additional channel, like the `.pyz` was.
2. **12-A Freeze:** PyInstaller onedir spec for the daemon; route all bundled reads through `resources.py`/importlib.resources (no `__file__`-relative paths); run the full 15-file suite against the frozen binary; add port-0 + stdout handshake + `/shutdown`.
3. **12-B Shell:** minimal Tauri project in `shell/`; `externalBin` sidecar; spawn→handshake→navigate→kill-on-exit; window chrome replaces the `--app=` Chrome trick (which stays as fallback when the shell isn't installed).
4. **12-C Installer + update:** NSIS target (not MSI, not both); `tauri-plugin-updater` against GitHub Releases beside the existing `.pyz` assets; updater keypair generated and stored offline; Azure Artifact Signing wired into CI; Microsoft AV false-positive submission in the release checklist.
5. **12-D Linux (deferred to the 7900 XTX arriving):** AppImage/deb; test WebKitGTK on that AMD box; llama-server systemd/user service or app-spawned; browser-tab fallback if WebKitGTK misbehaves.

**Estimated sizes [ASSUMED]:** installer 25-45 MB; installed 60-100 MB; idle RAM 130-230 MB total across processes. Electron equivalent: ~3-4× each.

## 8. What Phase 12 must contain

- Frozen-daemon build (onedir) + frozen-mode test gate (the suite passes against the exe, not just source).
- Sidecar contract: port-0 bind, stdout handshake line (locked wording), `/shutdown`, kill-tree on shell exit, second-launch-after-crash recovery (stale process/port detection).
- Tauri shell with window, spawn/own/kill, and offline-degrade verified (unplug network: everything but the tutor works).
- NSIS installer; updater plugin + signing keypair; Azure Artifact Signing; release checklist (sign → AV submit → publish `.pyz` and NSIS side by side).
- Decision record: which channel each user class gets (installer = Weibao's daily driver; `.pyz`/checkout = agents and dev).
- Explicit non-goal list (below).

## 9. Constraints on earlier phases (act before Phase 12)

- **Asset bundling [PACKAGING, constrains Phases 3-6.1]:** every static asset (KaTeX, fonts, future CodeMirror/editor JS) must be served by the daemon from bundled resources via `resources.py` — never `file://`, never CDN, never `__file__`-relative. This is both the offline rule and the freeze-compatibility rule; adopting it now makes 12-A nearly free.
- **Writable-state location [RUNTIME, constrains any phase adding state]:** installed apps live in a read-only Program Files dir. Banks/evidence already live in user directories (fine); anything new (caches, `updates/check_state.json`-style records) must resolve to APPDATA/XDG, never beside the executable.
- **No hardcoded port anywhere** in new surfaces or docs; always derive from the daemon's announced URL.

## 10. What NOT to decide yet

- Whether the hand-rolled `.pyz` updater is eventually retired or kept permanently for the checkout channel (decide after the first NSIS release cycle).
- Ollama vs raw `llama-server` on the Linux box, and whether the app spawns it or a user service owns it (decide when hardware exists).
- PyTauri adoption (re-evaluate ≥ v1.0 / in a year).
- Tauri mobile (Android/iOS) — B2 in the brief; door stays open, no work now.
- MSIX / Microsoft Store distribution; macOS signing/notarization (no Mac user today).
- Exact frontend framework inside the webview — none is required; the server-rendered surfaces keep working unchanged, and any richer frontend is a separate, later argument.

## 11. Assumptions log

| # | Claim | Risk if wrong |
|---|---|---|
| A1 | Frozen stdlib-only daemon lands at 15-35 MB onedir | Cosmetic — installer grows, verdict unchanged |
| A2 | Full test suite passes under PyInstaller freeze with only resource-path work | If frozen-mode breakage is deep, 12-A grows by a plan; embedded python-build-standalone is the fallback |
| A3 | WebKitGTK acceptable on the AMD 7900 XTX box | Fallback: browser-tab mode on Linux, or Electron shell for Linux only |
| A4 | Signed onedir + Microsoft submissions keep Defender quiet in practice | Fallback: embedded CPython layout (stock DLLs, no PyInstaller bootloader) |

## Sources (primary)

- Tauri official: [sidecar](https://v2.tauri.app/develop/sidecar/), [updater](https://v2.tauri.app/plugin/updater/), [Windows installer](https://v2.tauri.app/distribute/windows-installer/), [webview versions](https://v2.tauri.app/reference/webview-versions/), [Linux graphics issues](https://v2.tauri.app/develop/debug/linux-graphics/)
- Examples: [dieharders/example-tauri-v2-python-server-sidecar](https://github.com/dieharders/example-tauri-v2-python-server-sidecar), [pandas sidecar](https://mclare.blog/posts/writing-a-pandas-sidecar-for-tauri/), [Tauri+FastAPI+llama.cpp](https://aiechoes.substack.com/p/building-production-ready-desktop), [tauri-local-lm](https://github.com/dillondesilva/tauri-local-lm)
- Lifecycle/ports: [discussion #3273](https://github.com/tauri-apps/tauri/discussions/3273), [plugins-workspace #3062](https://github.com/tauri-apps/plugins-workspace/issues/3062)
- AV/signing: [PythonGUIs AV FAQ](https://www.pythonguis.com/faq/problems-with-antivirus-software-and-pyinstaller/), [Trusted Signing individuals](https://techcommunity.microsoft.com/blog/microsoft-security-blog/trusted-signing-is-now-open-for-individual-developers-to-sign-up-in-public-previ/4273554), [melatonin.dev signing guide](https://melatonin.dev/blog/code-signing-on-windows-with-azure-trusted-signing/), [Nuitka commercial](https://nuitka.net/doc/commercial.html)
- Python-alone: [Briefcase Windows](https://briefcase.beeware.org/en/stable/reference/platforms/windows/index.html), [BeeWare April 2026](https://beeware.org/news/buzz/2026/april-2026-status-update/), [pywebview](https://pypi.org/project/pywebview/), [PyApp](https://www.infoworld.com/article/4030697/pyapp-an-easy-way-to-package-python-apps-as-executables.html), [PyTauri](https://github.com/pytauri/pytauri), [pytauri standalone build](https://pytauri.github.io/pytauri/0.4/usage/tutorial/build-standalone/)
- Comparisons: [OpenReplay Electron vs Tauri](https://blog.openreplay.com/comparing-electron-tauri-desktop-applications/), [PkgPulse 2026](https://www.pkgpulse.com/guides/electron-vs-tauri-2026), [Wails v3 beta](https://v3.wails.io/blog/wails-v3-beta/), [MSI/NSIS discussion #8963](https://github.com/orgs/tauri-apps/discussions/8963), [Electron+Python TIL](https://til.simonwillison.net/electron/python-inside-electron)
