# Stack Research

**Domain:** Local-first, single-user learning platform — six new capabilities layered onto an existing stdlib-only Python 3 runtime (`model.py` / `runtime.py` / `server.py` / `surfaces/`)
**Researched:** 2026-08-05
**Confidence:** HIGH overall (each recommendation individually rated below; two items are MEDIUM/watch-items, flagged explicitly)

This is not a green-field stack pick. It is six narrow additions to a system whose founding
constraint is "Python standard library only, no install step," with exactly two named
exceptions already approved in `PROJECT.md`: a vendored KaTeX asset, and stdlib `urllib` for
the opt-in updater. Every recommendation below is scoped to fit inside that constraint or is
flagged loudly if it can't.

## Recommended Stack

### Core Technologies

| Capability | Technology | Version | Purpose | Why Recommended |
|------------|-----------|---------|---------|-----------------|
| 1. Math rendering | KaTeX (vendored static files) | **0.18.1** (released 2026-07-19) | Renders LaTeX to HTML/CSS in-browser, offline, synchronously | Smaller and faster than MathJax, designed for exactly this — self-contained CSS+JS+fonts, no runtime network fetch, MIT licensed. Already the project's own named exception. |
| 1b. Delimiter parsing | KaTeX `contrib/auto-render.min.js` | ships with 0.18.1 | Finds `$...$` / `$$...$$` in rendered HTML and calls KaTeX on each | Without it you'd hand-write a delimiter scanner; this is ~4 KB and part of the same release archive — no separate dependency. |
| 2. Learner code execution | `subprocess.run(..., timeout=N)` | stdlib (3.11+) | Runs the learner's submitted script as a child process, captures stdout/stderr, enforces a wall-clock timeout | The only stdlib mechanism for "run arbitrary learner code and observe output." No install, no daemon, works identically enough on both target OSes for the timeout case. |
| 2b. POSIX resource caps | `resource.setrlimit` (RLIMIT_CPU, RLIMIT_AS) via `preexec_fn` | stdlib, **POSIX/macOS/Linux only** | Caps CPU seconds and address space before the child's `exec()` | Real OS-enforced limits, cheap, no ctypes needed — but does not exist on Windows (see Pitfalls / What NOT to claim, below). |
| 3. Code editor | Plain `<textarea>` + a synced line-number gutter, hand-written JS/CSS | n/a (no library) | Monospace code entry with tab handling and line numbers | Meets the stated bar (monospace, tabs, line numbers) with zero vendored code and zero build step — the cheapest compliant option, and the only one that needs no second named exception beyond KaTeX. |
| 4. Packaging | `python -m zipapp` | stdlib (3.11+) | Bundles the app tree into one `.pyz` archive runnable by any Python 3 interpreter | This *is* the stdlib packaging story; `PROJECT.md` already names it explicitly and rules out PyInstaller/compiled binaries. |
| 4b. Windows launch | `.pyz`/`.pyzw` file association registered by the CPython installer, or a 2-line `.bat` fallback | n/a | Double-click launch on Windows without a console window | `.pyzw` maps to `pythonw.exe` (no console) exactly the way `.pyw` does today — documented CPython behaviour, zero extra code. |
| 4c. macOS/Linux launch | A tiny `#!/bin/sh` launcher script (`.command` on macOS) that `exec`s `python3 itembank.pyz` | n/a | Double-clickable in Finder / executable from a file manager | `.pyz` itself is not Finder-double-clickable without Python's shebang being honored by the OS loader; a one-line shell wrapper is the standard workaround and stays inside "no install step." |
| 5. Self-updater transport | `urllib.request` against the GitHub REST Releases API | stdlib | Fetch latest release metadata and asset bytes | Already the project's second named exception. No `requests`, no `httpx`. |
| 5b. Integrity check | `hashlib.sha256` compared against the asset's GitHub-exposed `digest` field (and/or a self-published `SHA256SUMS` file) | stdlib | Verify the download before trusting it | GitHub now computes and serves a SHA-256 `digest` per release asset via the REST/GraphQL API (shipped June 2025) — checksum verification needs no extra published artifact, though publishing your own `SHA256SUMS.txt` alongside the release is a cheap belt-and-braces addition. |
| 5c. Atomic replace | `os.replace()` (already the project's session-write pattern) | stdlib | Swap the old `.pyz` for the new one without a partial-write window | Same primitive `runtime.write_session()` already uses (write to `.tmp`, then `os.replace`) — reuses an existing house pattern instead of inventing a second one. |
| 6. LLM backends | `subprocess` for CLI agents (Claude Code, Codex CLI); `urllib.request` POST for OpenAI-compatible HTTP servers (Ollama, llama.cpp `llama-server`) | stdlib | One adapter interface, three interchangeable backends | Both CLI tools support scripted, single-turn, JSON-out invocation; both local-model servers speak the same `/v1/chat/completions` shape, so the HTTP client code is identical for either — only the base URL changes. No `openai` pip package needed for a JSON POST. |

### Supporting Libraries (all stdlib, all already implicitly available)

| Library | Purpose | When to Use |
|---------|---------|-------------|
| `tempfile` | Isolated scratch directory per `check`-item run | Give each learner code execution its own throwaway `cwd` so stray file writes don't collide across attempts. |
| `difflib` | Human-readable diff between expected and actual output | Surfaces *why* a `check` item failed instead of a bare pass/fail, without adding a diff library. |
| `signal` (POSIX) | Send `SIGKILL` to a process *group*, not just the leaf process | A learner's script that itself calls `subprocess`/`os.fork` needs the whole group killed on timeout, not just the direct child. |
| `ctypes` | Optional Windows Job Object creation for memory/process-count limits | Advanced, optional, POSIX `resource` has no Windows equivalent in stdlib proper — `ctypes` calls into `kernel32.dll` are the only stdlib-legal path there. Treat as a v2 hardening item, not a v1 requirement (see Pitfalls). |
| `zipfile` | Inspect/rebuild the `.pyz` for the updater's staging step | The updater downloads a `.pyz`, verifies it, then replaces the running one — `zipfile` is only needed if you want to sanity-check the archive is well-formed before swapping it in. |
| `platform`, `sys.platform` | OS branching for launcher generation and resource-limit availability | Every one of the six capabilities has at least one per-OS branch; this is the stdlib primitive for detecting which branch to take. |
| `venv` (build-time only, not shipped) | N/A — **do not use for distribution** | Only relevant if CI needs an isolated environment to run `zipapp`; the shipped `.pyz` itself must not assume a venv exists on the target machine. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `python -m zipapp <dir> -o out.pyz -p "/usr/bin/env python3" -c` | Build step for the packaged artifact | `-c` compresses; `-p` writes the POSIX shebang. Run once per release, not per commit. |
| GitHub Releases (existing repo, no new service) | Update source of truth | The updater reads `GET /repos/<owner>/<repo>/releases/latest`; unauthenticated REST calls are rate-limited (60/hr per IP) — irrelevant at "check on launch, once a day" cadence, but worth knowing if testing the updater in a loop. |

## Per-Capability Detail

### 1 & 1b — LaTeX rendering (KaTeX, vendored)

**Verified facts (HIGH confidence, checked against `github.com/KaTeX/KaTeX` releases and the `unpkg` file listing for `katex@0.18.1`, 2026-08-05):**

- Latest stable release: **v0.18.1**, 2026-07-19.
- Files you actually need, vendored into the repo (not fetched at runtime):
  - `katex.min.css` — **24.7 KB**
  - `katex.min.js` — **272 KB**
  - `contrib/auto-render.min.js` — a few KB, part of the `contrib/` bundle (278 KB total, but you only need this one file from it)
  - `fonts/` — the full directory is **1.08 MB** across woff2/woff/ttf; **only the `.woff2` files are needed** for any browser this project will run in (Chrome/Edge, both required anyway for the `--app=` window). Cutting to woff2-only brings the font payload down to roughly a third of that, well under 400 KB.
- Total vendored footprint: **under 700 KB** for CSS + JS + auto-render + woff2 fonts. The published release archive (`katex.zip`, 1.35 MB) includes source maps, all three font formats, and files you don't need — do not vendor the whole zip, extract only the four items above.

**Where the files live relative to the two existing render paths:**

- `build` (the offline single-file HTML, `surfaces/quiz.py:cmd_build()`) has to stay a single portable file. Read the four vendored assets into Python at build time and **inline** them: `<style>` block for CSS, `<script>` block for JS/auto-render, and base64 `data:` URIs for the woff2 fonts substituted into the inlined CSS's `@font-face` rules (a small string-replace pass, since the released CSS references `url("fonts/...")` relative paths). This keeps `build`'s output a true single file, at a size cost of roughly +650 KB per generated HTML — acceptable for an offline quiz page.
- `serve` / `day` / the future daemon (`server.py`-based routes) already run a loopback HTTP server per request cycle. For these, add a static-file route (e.g. `/vendor/katex/<file>`) that reads the vendored files off disk and serves them with the right `Content-Type` — no inlining needed, no base64 bloat, and it's cached by the browser across requests within a session.
- Either way: **zero network requests**, because the bytes either live in the generated HTML or are served by the same loopback process already serving the page.

**What NOT to use:**

- **MathJax** — technically capable, but 3–5× the payload (MathJax 3's combined bundle is multi-megabyte once fonts and the TeX input processor are included), asynchronous two-pass layout that reflows the page after first render (visible "jump"), and no advantage for the math this project actually needs (EMT dosage calculations, Math 1400 algebra/calculus notation — squarely inside KaTeX's supported command set). Use KaTeX; do not revisit MathJax unless a specific unsupported LaTeX command is found in a real bank.
- **A CDN `<script src="https://cdn.jsdelivr.net/...">` tag** — violates the network constraint outright (Goal 5 forbids services and network, not files — a CDN reference is a network dependency, not a file). Vendor the four files into the repo instead.
- **`contenteditable` + a custom LaTeX-to-HTML hand-roll** — reinventing KaTeX badly; not worth the maintenance surface for a project with one maintainer.

### 2 & 2b — Running learner code (`check` item type)

**The honest scope statement first, because the downstream plan needs it stated plainly: this is process isolation for a trusted single local user's buggy code, not a security sandbox for adversarial code.** The learner runs as the same OS user as the itembank process. Nothing in the Python standard library — not `subprocess`, not `resource`, not anything reachable via `ctypes` without a lot more code than this project should carry — creates a security boundary against a learner who deliberately writes `os.system("rm -rf ~")` or opens a socket. `PROJECT.md` scopes `check` to "running the learner's own answer, no sandboxing claim" — the research confirms that is the correct scope, and no stdlib mechanism would let you claim more without lying about it. Do not add Docker, a VM, or a `chroot`/`seccomp`/`pledge`-based sandbox for this milestone: they are exactly the kind of dependency the project's zero-install-step rule exists to keep out, and the threat model (one learner, their own coursework) doesn't justify the cost.

**What stdlib does give you, and it's genuinely useful for the actual failure mode (runaway/buggy code, not malice):**

- `subprocess.run([sys.executable, "-I", "-S", "-B", script_path], input=..., capture_output=True, text=True, timeout=N, cwd=tmp_scratch_dir)`
  - `-I` (isolated mode) ignores `PYTHONPATH`/`PYTHONHOME`/user site-packages and most environment overrides — a cheap, real reduction in accidental cross-contamination between the learner's system Python config and the grading run.
  - `-S` skips `site.py` import (marginally faster start, avoids some environment-dependent behavior).
  - `-B` skips writing `.pyc` files into the scratch directory.
  - `cwd=` a fresh `tempfile.mkdtemp()` per attempt so filesystem side effects don't leak across runs or into the repo.
- **Timeout is genuinely cross-platform**: `subprocess.run(..., timeout=N)` raises `subprocess.TimeoutExpired` on both Windows and POSIX and stdlib kills the *direct* child for you. What it does **not** do on either OS is guarantee grandchildren die too, if the learner's own script spawns a subprocess.
  - POSIX fix (HIGH confidence, standard recipe): `subprocess.Popen(..., start_new_session=True)`, then on timeout `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)` instead of `proc.kill()`.
  - Windows fix requires `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP` at spawn time, and on timeout either shelling out to `taskkill /PID <pid> /T /F` (spawns an external process — still zero *pip* dependencies, `taskkill` ships with Windows) or building a Job Object via `ctypes` and `kernel32.dll` (`CreateJobObjectW`, `AssignProcessToJobObject`, `TerminateJobObject`) so the whole tree dies together. **Recommend `taskkill /T /F` as the v1 Windows mechanism** — it's a one-line `subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"])` call, no ctypes plumbing, and ships on every Windows install targeted here. Reserve the Job-Object/`ctypes` route as a later hardening pass if `taskkill`'s external-process-per-kill overhead ever matters (it won't, at one-learner scale).
- **Memory/CPU caps are POSIX-only in stdlib.** `resource.setrlimit(resource.RLIMIT_CPU, (N, N))` and `resource.setrlimit(resource.RLIMIT_AS, (bytes, bytes))`, set inside a `preexec_fn` passed to `subprocess.Popen`, work on macOS and Linux and cap a runaway loop or memory bomb before the OS scheduler even has to be asked to intervene. **`resource` does not exist on Windows** (`import resource` raises `ModuleNotFoundError`) — there is no stdlib memory/CPU-rlimit equivalent there. The only way to get an equivalent on Windows without a third-party dependency is the `ctypes`-built Job Object mentioned above (`JOBOBJECT_EXTENDED_LIMIT_INFORMATION` with `JOB_OBJECT_LIMIT_PROCESS_MEMORY` / `JOB_OBJECT_LIMIT_JOB_TIME`). **Recommendation: ship the wall-clock `timeout=` guard on both OSes as the v1 baseline (it alone stops the overwhelming majority of "infinite loop" submissions), add POSIX `resource` limits as a v1 nice-to-have since they're cheap, and explicitly defer the Windows Job Object as a flagged, not-yet-built capability** rather than quietly shipping asymmetric protection and calling it done.
- **Output comparison**: normalize before diffing — `.replace("\r\n", "\n")` (Windows vs POSIX line endings) and per-line `.rstrip()` (trailing whitespace) before the exact-match/diff comparison, or a submission authored and tested on one OS will spuriously fail on the other. Use `difflib.unified_diff` to show the learner *what* differed rather than a bare pass/fail — stdlib, no new dependency.

**What NOT to use:** Docker/Podman containers, a VM, PyPy sandboxing, `RestrictedPython`/`pysandbox`-style AST-rewriting sandboxes (all historically broken as security boundaries and all third-party), `seccomp`/`pledge`/`AppArmor` profiles (Linux-only, not cross-platform, and still third-party tooling to wire up from Python). All of these both violate the no-dependency constraint and overclaim a security property this project doesn't need for a single trusted local learner.

### 3 — Code editor (browser)

**Recommendation: a plain `<textarea>` plus a synced line-number gutter, written directly into the existing inline-template pattern (`quiz_page.py` / `theme.py` already inline CSS/JS as Python strings — this fits the same pattern, not a new one).**

Concretely:
- CSS: `font-family: ui-monospace, "Cascadia Code", Menlo, Consolas, "Courier New", monospace;` `tab-size: 4;` (unprefixed `tab-size` is supported in all current Chrome/Edge/Firefox/Safari; no vendor prefix needed in 2026) and `white-space: pre;` on the textarea.
- Tab handling: a `keydown` listener that intercepts `Tab`/`Shift+Tab`, calls `preventDefault()`, and inserts/removes literal `\t` (or N spaces, project's choice) at `selectionStart`/`selectionEnd`, then resets the cursor position — the standard vanilla-JS recipe for "tab doesn't leave the textarea." Roughly 20 lines of JS.
- Line numbers: a second element (an absolutely-positioned `<div>`/`<pre>` gutter) whose content is regenerated on `input` (count of `\n` + 1) and whose `scrollTop` is kept in lockstep with the textarea's `scrollTop` on the `scroll` event. This is the well-known dependency-free pattern predating CodeMirror-style editors; it is not novel engineering, just a known small recipe.

**What NOT to vendor, and why:**

| Library | Why not |
|---|---|
| Monaco Editor (VS Code's editor) | Multi-megabyte minified bundle (web worker + AMD-loader architecture), designed to be lazily fetched from a CDN or bundled by a real build tool. Wildly disproportionate for "monospace textarea with line numbers." |
| CodeMirror 6 | Ships as ES modules meant to be bundled (rollup/esbuild/etc.) — using it without a build step means hand-assembling a bundle yourself, which is a build step by another name. |
| CodeMirror 5 | Has a legacy single-file UMD bundle (~250 KB) that *would* technically work with a plain `<script>` tag and no build step — the only one of the three that's mechanically compliant. Still rejected for v1: it is a second vendored third-party asset beyond the one the project has already named and reviewed (KaTeX), and the actual requirement (monospace, tabs, line numbers, no syntax highlighting called for) doesn't need it. Revisit only if syntax highlighting or bracket-matching becomes an explicit requirement later — and if so, treat it exactly like KaTeX: named, reviewed, and vendored as static files. |
| Ace Editor | Same shape of objection as CodeMirm 5 — a real single-file distribution exists, but it's an unneeded second exception for a requirement that doesn't call for syntax highlighting. |
| `contenteditable` div as a "simple" editor | Looks simpler, is not: contributes `&nbsp;`, `<div>`/`<br>` soup on paste, inconsistent cross-browser selection/cursor APIs, and no free tab-size/monospace guarantee. `<textarea>` gives you plain-text semantics for free, which is exactly what code entry needs. |

### 4, 4b, 4c — Packaging as a double-clickable artifact

**`python -m zipapp` is the correct and only stdlib mechanism**, and it is already named in `PROJECT.md` — this research confirms the mechanics rather than picking among alternatives:

- Requires the app tree to expose a `__main__.py` at its root (or pass `-m "package.module:function"` to `zipapp` to point at an existing entry function without restructuring). Given the current layout (`itembank.py` at repo root importing `surfaces.cli`), the lowest-friction path is `python -m zipapp . -m "surfaces.cli:main" -o itembank.pyz -p "/usr/bin/env python3" -c`, run from a build directory containing only the shippable package (not `.git`, `tests/`, `.planning/`) — flag as a small restructuring/build-script task for the roadmap, not a redesign of the four layers.
- **Windows**: the CPython installer registers `.pyz` and `.pyzw` file extensions at install time (documented in the stdlib `zipapp` docs). `.pyz` opens with `python.exe` (console visible); `.pyzw` opens with `pythonw.exe` (no console) — build both, ship `.pyzw` as the double-click artifact and `.pyz` as the CLI-invokable one, from the same source tree with different `-p` shebangs (`python`/`pythonw`). This requires the target machine to have installed Python via the official installer (which is already this project's baseline assumption — "any machine with Python 3.11+"); a machine with only a Microsoft Store Python or no Python at all won't have the association, so document that requirement, don't silently assume it.
- **macOS**: `.pyz` has no Finder double-click association out of the box. Ship a tiny companion `itembank.command` (`#!/bin/sh` script, `chmod +x`, `cd` to its own directory, `exec python3 itembank.pyz "$@"`) — macOS Terminal.app runs `.command` files on double-click by convention, no code signing or notarization required for a single local user, though **first launch will trigger Gatekeeper's "unidentified developer" warning** (right-click → Open, once) — document that in the README rather than paying for an Apple Developer Program certificate ($99/yr), which is explicitly out of scope.
- **Linux**: `.pyz` is directly executable once `chmod +x` is set (the `-p` shebang line makes the OS loader hand it to the named interpreter) — `./itembank.pyz` just works from a terminal. For desktop-environment double-click integration, a `.desktop` file pointing at the same shebang-executable `.pyz` is optional polish, not a requirement.
- **`--app=` frameless window** (Chrome/Edge): confirmed still present and undeprecated in current Chromium as of this research (`peter.sh`'s maintained command-line-switches reference, cross-checked against no deprecation notice on `developer.chrome.com`'s deprecations page). Launch via `subprocess.Popen([chrome_path, f"--app=http://127.0.0.1:{port}", f"--user-data-dir={profile_dir}"])`, locating `chrome_path`/`msedge_path` per OS (`Program Files`/`Program Files (x86)` on Windows, `/Applications/...` on macOS, `which google-chrome`/`which chromium` on Linux) with a fallback to opening the URL in the system default browser (`webbrowser.open`, stdlib) if neither is found — **do not hard-fail if Chrome/Edge isn't installed**, since the constraint list explicitly wants graceful degradation. **Flag this as a MEDIUM-confidence, watch-list item**: `--app=` is a long-lived but historically unofficial/undocumented-by-Google Chromium switch (community-maintained references only, not in Google's own developer docs), so treat the frameless-window feature as progressive enhancement, not a load-bearing requirement — the daemon must be fully usable in an ordinary browser tab if the switch ever stops working in a future Chromium release.

**What NOT to use, and why (all violate "compiled binary is out of scope" and/or "no dependency"):**

| Avoid | Why | Use instead |
|---|---|---|
| PyInstaller | Bundles a full Python interpreter into a compiled binary; third-party pip dependency; the exact tool the project already got a Windows Defender false-positive from, per `PROJECT.md`'s own history. | `python -m zipapp` |
| cx_Freeze / py2exe / py2app | Same shape of objection — compiled binary, third-party, per-OS build pipeline, signing friction. | `python -m zipapp` |
| Nuitka | Compiles Python to C/binary; heavyweight build toolchain; still a compiled artifact the project has explicitly deferred to v2. | `python -m zipapp` |
| Briefcase / BeeWare | Full app-packaging framework (bundles a Python runtime per OS, produces installers); massive overkill and a dependency tree of its own. | `python -m zipapp` + per-OS launcher script |

### 5, 5b, 5c — Self-updater against GitHub Releases

- `urllib.request.urlopen("https://api.github.com/repos/<owner>/<repo>/releases/latest")` → JSON with `assets[]`, each carrying `browser_download_url`, `name`, `size`, and (as of GitHub's June 2025 platform change) a **`digest`** field exposing a SHA-256 checksum computed server-side at upload time. **MEDIUM confidence on the exact `digest` string format** (expected `"sha256:<hex>"` by analogy with GitHub's container/OCI digest convention, but this research could not directly confirm a live example value) — verify the literal field shape against one real API response before writing the parser, and fall back to publishing your own `SHA256SUMS.txt` release asset and checking against that if the built-in `digest` field's shape or availability surprises you.
- Download the asset bytes with a second `urlopen()` call, write to `tempfile.NamedTemporaryFile(delete=False)` in the same directory as the final target (matters for `os.replace` — see below), then `hashlib.sha256(data).hexdigest()` and compare.
- Atomic swap: `os.replace(tmp_path, final_path)` — atomic on the same filesystem on both POSIX and Windows since Python 3.3, and it is **the same pattern `runtime.write_session()` already uses** for session files (write-then-`os.replace`), so this is reusing an established house convention rather than introducing a new one.
- **Real cross-platform TLS gotcha, worth flagging explicitly (HIGH confidence, well-documented CPython/macOS packaging issue):** the official python.org installer for **macOS** ships its own bundled OpenSSL that does **not** read the macOS system keychain/trust store by default. A fresh python.org macOS install can raise `CERTIFICATE_VERIFY_FAILED` on the very first `urllib` HTTPS call until the user runs the one-time `Install Certificates.command` script that ships alongside the installer (in `/Applications/Python 3.x/`). **Windows does not have this problem**: CPython's `ssl.SSLContext.load_default_certs()` special-cases Windows and pulls from the Windows certificate store automatically. Document the macOS one-time step in the updater's README/first-run message rather than silently failing — and since the project's own design already treats "offline degrades silently" as correct behavior, make sure a TLS failure is distinguishable in logs from "no network," so this specific fixable gotcha doesn't get miscategorized as "offline" forever.
- **What NOT to use**: `requests`/`httpx` (pip dependencies, explicitly the thing the whole project avoids), `certifi` (a real, common, and reasonable dependency in general — but still a dependency this project has not named as an exception; the macOS one-time cert-install step is the compliant workaround, not `pip install certifi`), any GitHub SDK library (`PyGithub`, `ghapi`, etc. — all third-party, and the updater only needs two GET requests, not a full API client).

### 6 — LLM backend adapters

Both local CLI agents and both local/hosted HTTP-serving options fit stdlib cleanly, and — usefully — the interface shape ends up nearly identical across all four, which is exactly what "swappable backend" needs:

- **Claude Code**: `claude -p "<prompt>" --output-format json [--allowedTools ...] [--permission-mode ...]` via `subprocess.run(capture_output=True, text=True)`, then `json.loads(result.stdout)`. `--print`/`-p` runs one turn and exits — no interactive TUI, no pty needed. Streaming (`--output-format stream-json`) is available if the adapter interface wants incremental output later, but the simple JSON mode is sufficient for `short`-answer rubric marking and authoring-loop use described in `PROJECT.md`.
- **Codex CLI**: `codex exec "<prompt>" --json [--sandbox read-only|workspace-write] [--full-auto]` via the same `subprocess.run` shape; `--json` streams one JSON object per event to stdout (JSONL), parseable line-by-line with `json.loads` per line — same stdlib primitives, different flag names. Default sandbox is `read-only`; the auditor's "report-only through full audit-draft-lint-fix-commit" autonomy range maps directly onto Codex's own `--sandbox`/`--full-auto` knobs, which is a convenient alignment worth keeping when the adapter interface is designed.
- **Local OpenAI-compatible server (Ollama or llama.cpp `llama-server`, for Qwen or any GGUF model)**: both expose `POST /v1/chat/completions` in the OpenAI request/response shape. `urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")` → `urllib.request.urlopen(req)` → `json.loads(resp.read())`. Ollama's default base is `http://localhost:11434/v1`; llama.cpp's `llama-server` default is `http://localhost:8080/v1` (Ollama also ships a native, non-OpenAI-shaped API on the same port — prefer the `/v1/...` compatibility surface specifically, since that's the one shared with llama.cpp and any future OpenAI-compatible option). No API key is required for local servers; add an optional `Authorization` header only if the config later points at a genuinely hosted endpoint, which `PROJECT.md`'s constraints currently forbid for anything that sees bank content.
- **Adapter interface shape**: because CLI agents and HTTP servers both end up producing "a prompt in, structured text/JSON out," a single Python interface (`class ModelAdapter: def complete(self, prompt: str, **opts) -> AdapterResult`) with one concrete implementation per backend (`ClaudeCodeAdapter(subprocess)`, `CodexAdapter(subprocess)`, `OpenAICompatAdapter(urllib, base_url)`) covers all four named backends (Claude Code, Codex, Qwen-via-Ollama, Qwen-via-llama.cpp) without needing per-backend special-casing anywhere else in the codebase — matches the "interface, not a vendor" decision already recorded in `PROJECT.md`.

**What NOT to use:** the `openai` pip package (unneeded — it's a thin wrapper over exactly the HTTP call `urllib` already makes, and it is a real third-party dependency the moment it's imported), `langchain`/`llama-index`-style orchestration frameworks (heavyweight, opinionated about state and memory in ways that fight the project's own "runtime is the only state owner" rule), and pexpect/pty-based scripting of the *interactive* `claude`/`codex` REPLs (unnecessary — both tools ship dedicated non-interactive/headless modes precisely so callers don't have to script a TTY).

## Alternatives Considered

| Recommended | Alternative | When the alternative would be right |
|-------------|-------------|--------------------------------------|
| KaTeX (vendored) | MathJax (vendored) | Only if a bank needs a specific TeX macro/package KaTeX doesn't support — check KaTeX's "Support Table" against real bank content before switching, don't switch preemptively. |
| Plain `<textarea>` + gutter | CodeMirror 5 single-file bundle (vendored, ~250 KB) | If/when syntax highlighting or bracket-matching becomes an explicit product requirement, not before — and treat it as a second named exception like KaTeX, not a silent addition. |
| `subprocess` + `timeout=` + POSIX `resource` | A `ctypes`-built Windows Job Object | If Windows memory-bomb protection becomes a real, observed problem (not hypothetical) — it's a legitimate stdlib-only escalation path, just more code than v1 needs. |
| `taskkill /T /F` for Windows process-tree cleanup | `ctypes` Job Objects | If the overhead/latency of spawning `taskkill` per timeout ever measurably matters — unlikely at one-learner scale. |
| `python -m zipapp` | A future signed, compiled binary (PyInstaller/Nuitka/etc.) | Explicitly deferred to v2 per `PROJECT.md`, and only "when a second person runs it" per that same document — not a stack decision to revisit now. |
| GitHub's built-in asset `digest` field | A self-published `SHA256SUMS.txt` release asset | Use as a fallback/belt-and-braces addition regardless, since the exact `digest` field shape wasn't directly confirmed in this pass (see MEDIUM-confidence flag above) — cheap to add either way (one extra file per release). |
| `urllib` + one-time macOS cert-install doc note | `certifi` pip package | Never, under current constraints — `certifi` is a real dependency the project has not named as an exception; the one-time `Install Certificates.command` step is free and already ships with python.org's macOS installer. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Any CDN `<script src>`/`<link href>` (KaTeX, fonts, anything) | Network dependency at render time; violates "no network that sees your content, and none you did not ask for" even for non-content static assets — a CDN request still leaks *that itembank is being used, when, and from where*. | Vendor the files into the repo; serve from loopback or inline into the offline build. |
| PyInstaller / cx_Freeze / py2exe / py2app / Nuitka / Briefcase | Compiled-binary packagers; third-party; explicitly out of scope per `PROJECT.md`, and the source of this project's own prior Defender false-positive. | `python -m zipapp` + per-OS launcher script. |
| Docker / a VM / `seccomp`/`pledge`/AppArmor sandboxing for `check` items | Overclaims a security boundary the threat model (one trusted local learner) doesn't need, and is exactly the kind of service/dependency the project's zero-install rule exists to exclude. | `subprocess` + `timeout=` + POSIX `resource` limits + honest "not a sandbox" documentation. |
| CodeMirror 6 (or any ES-module-only editor library) | Requires a JS bundler — a build step by another name, even without npm. | Plain `<textarea>` + hand-written gutter/tab JS. |
| Monaco Editor | Multi-megabyte, AMD-loader/web-worker architecture designed for a real build pipeline; wildly disproportionate for the stated requirement. | Plain `<textarea>` + hand-written gutter/tab JS. |
| `requests` / `httpx` / `certifi` / `openai` / `PyGithub` / any pip package | All are real third-party dependencies; the project's constraint is stdlib-only with exactly two named exceptions (KaTeX asset, `urllib`) — none of these are on that list. | `urllib.request`, `hashlib`, `json`, `subprocess` — all stdlib, all already sufficient for every HTTP/JSON need in this milestone. |
| MathJax | 3–5× KaTeX's payload, async two-pass reflow, no capability advantage for this project's actual math content. | KaTeX, vendored. |
| `pexpect`/pty-scripting the interactive `claude`/`codex` REPL | Unnecessary complexity; both tools ship dedicated non-interactive modes for exactly this use case. | `claude -p ...` / `codex exec ...` via plain `subprocess.run`. |

## Stack Patterns by Variant

**If targeting the offline single-file `build` HTML page:**
- Inline KaTeX (CSS/JS/auto-render as `<style>`/`<script>` blocks, fonts as base64 `data:` URIs).
- No code-execution or editor concerns apply — `build` has never handled `check` items or graded submission; that stays a `serve`/daemon capability.

**If targeting `serve` / the future single daemon (`server.py`-based, loopback):**
- Serve KaTeX assets from a static-file route instead of inlining — avoids repeating ~650 KB per page load across a session.
- This is also where the `check` item type's subprocess execution and the code editor live, since both need a server round-trip (submit code → server runs it → server returns result), which `build`'s no-server static model cannot support.

**If on Windows:**
- No `resource` module for CPU/memory rlimits — rely on `timeout=` plus `taskkill /T /F` for process-tree cleanup; treat POSIX-parity memory limiting as a documented, deferred gap, not a silent one.
- `.pyzw` (via `pythonw.exe`) for the double-click artifact; `.pyz` for CLI use; both from the same source tree.
- TLS for the updater generally works out of the box (Windows cert-store integration is automatic in stdlib `ssl`).

**If on macOS:**
- `resource.setrlimit` works — use it for `check` items.
- `.command` wrapper script for Finder double-click, since `.pyz` alone has no Finder association; document the one-time Gatekeeper "Open anyway" step.
- Document the one-time `Install Certificates.command` step for the updater's TLS to work on a fresh python.org install.

**If on Linux:**
- `resource.setrlimit` works — use it for `check` items.
- `chmod +x itembank.pyz` is sufficient for direct execution; a `.desktop` file is optional desktop-environment polish, not required.
- TLS generally works out of the box (most distro Python builds link against the system OpenSSL/trust store already).

## Version Compatibility

| Component | Compatible With | Notes |
|-----------|-----------------|-------|
| KaTeX 0.18.1 | Any current Chrome/Edge/Firefox/Safari (the project's own `--app=` requirement already pins to Chrome/Edge) | No polyfills needed; KaTeX targets modern evergreen browsers. |
| `python -m zipapp` output | Python 3.11+ interpreter on the target machine (matches existing `STACK.md` baseline) | The `.pyz` is interpreted, not compiled — it needs *a* Python present, exactly like today's `python itembank.py` invocation; packaging doesn't remove that requirement, it removes the "clone the repo" step. |
| `resource.setrlimit` | CPython on Linux/macOS only | `ModuleNotFoundError` on Windows — must be wrapped in a `try`/`except ImportError` or `sys.platform` guard everywhere it's used, not assumed present. |
| GitHub REST Releases API | No auth required for public repos, GETs only | 60 requests/hour/IP unauthenticated — irrelevant at "check on launch" cadence for one user, but cache the last check timestamp so a crash-loop can't burn through it. |
| `--app=` Chromium switch | Current Chrome/Edge as of 2026-08-05 (undeprecated) | Community-documented, not in Google's own official flag docs — MEDIUM confidence; build the daemon to work in an ordinary tab as the fallback, not as an afterthought. |

## Sources

- `github.com/KaTeX/KaTeX` releases (GitHub API, `releases/latest`) — verified v0.18.1, 2026-07-19, asset sizes. HIGH confidence.
- `katex.org/docs/browser.html` — self-hosting file requirements, auto-render requirement. HIGH confidence, official docs.
- `unpkg.com` / `app.unpkg.com` file listing for `katex@0.18.1/dist` — per-file sizes (katex.min.js 272 KB, katex.min.css 24.7 KB, fonts/ 1.08 MB total across all formats). HIGH confidence, direct package inspection.
- `docs.python.org/3/library/zipapp.html` — official stdlib docs, `.pyz`/`.pyzw` Windows association behavior, shebang mechanics. HIGH confidence.
- `docs.python.org/3/library/resource.html` and cross-checked community sources — POSIX-only availability, no Windows equivalent in stdlib. HIGH confidence.
- `peter.sh/experiments/chromium-command-line-switches/` (community-maintained Chromium switch reference) — `--app=` still present, no deprecation notice found. MEDIUM confidence — not an official Google source.
- `developer.chrome.com/docs/web-platform/chrome-deprecation` — checked for any `--app=` deprecation notice; none found as of this research. MEDIUM confidence (absence of evidence, not confirmation of permanence).
- `code.claude.com/docs/en/headless` (official Claude Code docs) — `-p`/`--print`, `--output-format json`, `--allowedTools`, `--permission-mode`. HIGH confidence.
- `openai/codex` GitHub repo, `developers.openai.com/codex/noninteractive` — `codex exec`, `--json`, `--sandbox`, `--full-auto`. HIGH confidence.
- `ollama.com/blog/openai-compatibility`, `docs.ollama.com/api/openai-compatibility` — `/v1/chat/completions` compatibility, default port 11434. HIGH confidence.
- `llama.cpp` `llama-server` documentation (via `mvysny.github.io/llama-server-endpoints`, cross-checked against project docs) — OpenAI-compatible `/v1/...` surface, default port 8080. HIGH confidence.
- GitHub Changelog, 2025-06-03, "Releases now expose digests for release assets" — SHA-256 `digest` field on release assets via REST/GraphQL/UI/`gh`. MEDIUM confidence — existence confirmed, exact field string format not independently verified in a live API response during this research pass.
- General Python packaging community sources (multiple, cross-checked) on macOS `Install Certificates.command` and Windows `ssl.load_default_certs()` behavior — well-established, widely documented CPython/macOS packaging lore. HIGH confidence.
- `PROJECT.md` and `.planning/codebase/STACK.md`/`ARCHITECTURE.md` (this repository) — existing constraints, named exceptions, and layer boundaries this research is scoped inside. Primary source for scope, not for external facts.

---
*Stack research for: local-first learning platform additions (LaTeX rendering, code execution, code editor, packaging, self-update, LLM adapters)*
*Researched: 2026-08-05*
