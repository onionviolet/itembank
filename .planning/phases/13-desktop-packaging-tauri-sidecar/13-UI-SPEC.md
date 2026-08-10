---
phase: 13
slug: desktop-packaging-tauri-sidecar
status: approved
shadcn_initialized: false
preset: none
created: 2026-08-10
reviewed_at: 2026-08-10
inputs:
  - .planning/research/2026-08-10-ui-inspiration-missing-surfaces.md §0, §0.1, §5, §6 (OPTION SET)
  - .planning/PLANNING-DIRECTIVES.md §2, §3, §4, §4a, §5
  - .planning/UI-SPEC.md (§2.5, §2.7, §3, §4, §7, §8.1–8.9, §11)
  - .planning/research/2026-08-09-packaging.md (Q8)
  - .planning/phases/13-desktop-packaging-tauri-sidecar/13-CONTEXT.md (D-01 … D-15)
  - .planning/phases/02.1-.../02.1-UI-SPEC.md Copywriting Contract + 2026-08-08 amendment
  - .claude/CLAUDE.md Constraints (network rule; D-13 `update_policy` divergence)
---

# Phase 13 — UI Design Contract: the Shell Surface

> **This is not a redesign.** Every surface inside the window is already specified by the phase
> that owns it, and Phase 4's tokens plus `UI-SPEC.md` §8's nine gates govern all of it unchanged.
> This contract covers only what the app looks like *as an application*: window chrome, first
> launch, the installer, the updater's disclosure, and — the load-bearing part — **what the window
> shows when the Python sidecar is not running.**

**Phase theme: degrade honestly.** `UI-SPEC.md` §2.7, LOCKED, verbatim: *"Offline/model-unavailable/
unsupported capability states keep the authored activity usable when possible and say exactly what
is unavailable; they never fake an answer, confidence, score, or model result."* In every other
phase that rule is about the *model* going quiet. Here it is about the **runtime** going quiet,
which is strictly worse, because the runtime is what serves the page that would otherwise explain
itself. That single fact drives §3 below.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | **none** — no shadcn, no npm UI dependency, no component registry. Confirmed by scout: no `components.json`, no `package.json`, no `tailwind.config.*` in the repo. |
| Component approach | Native semantic HTML served by the Python daemon (`surfaces/presentation.py`), plus **two shell-local static documents** (§3.2) rendered by the Tauri WebView when the daemon cannot serve anything. |
| Component library | Existing `presentation.py` primitives — `surface_shell`, `context_line`, `state_panel`, `details_section`, `_action_markup` (`button.go` / `button.go.primary`). The shell-local documents reuse these **shapes**, not the Python code (they cannot import Python; the daemon is down). |
| Icon library | none. Callout kinds are `icon + Ledger-voice label + structure`; this phase adds no icon and no icon set. |
| Font | Existing stacks only. `--font-chrome` (`system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`) for shell copy; `--font-ledger` (`ui-monospace…`) for ports, PIDs, paths, fingerprints. **No surface may name a font family literally** (UI-SPEC §7). No vendored typeface lands in this phase. |
| Window shell | Tauri 2.x, **native OS window decorations** (§2). WebView2 on Windows 11. |

**Palette source — LOCKED, restated:** `surfaces/theme.py` remains the single palette source. The
shell-local documents (§3.2) carry a **build-time-generated snapshot** of `theme.py`'s default-accent
light and dark token blocks. A hand-written hex value anywhere in `shell/` is a **build failure**,
not a review comment. This is how a document rendered without Python still obeys the one palette.

---

## Spacing Scale

Declared values (multiples of 4 — the existing `space-1..7` scale, unchanged):

| Token | Value | Usage in this phase |
|-------|-------|---------------------|
| space-1 | 4px | gap between a Ledger line and its label |
| space-2 | 8px | button padding rhythm, chip padding |
| space-3 | 16px | default block spacing inside a shell-local document; document padding at narrow widths |
| space-4 | 24px | document padding at ≥768px; gap between the message block and the action row |
| space-5 | 32px | gap between the heading block and the details disclosure |
| space-6 | 48px | top offset of the shell-local document from the window's top edge |
| space-7 | 64px | bottom padding, matching `.surface`'s existing `64px` |

**Exceptions:**

1. **44px minimum interactive target** applies to every control in a shell-local document and to
   the first-launch doors. No dense-cell 36px exception is used in this phase.
2. **Native OS menus and native window decorations are exempt** — their metrics are the OS's, and
   reimplementing them is exactly the cost §2 refuses to pay. This exemption covers the menu bar
   and the titlebar only; it covers nothing rendered inside the WebView.

---

## Typography

Three sizes, two weights. No new size and no new weight is introduced by this phase.

| Role | Size | Weight | Line Height | Voice token |
|------|------|--------|-------------|-------------|
| Body | 16px | 400 | 1.5 | `--font-chrome` |
| Label / provenance | 12px | 600 | 1.4 | `--font-ledger` — ports, PIDs, paths, SHA-256 fingerprints, the CLI twin string |
| Heading | 20px | 600 | 1.2 | `--font-chrome` |
| Display (32px) | **not used** | — | — | A failure screen does not get a 32px headline. A large red-adjacent headline reads as alarm, and §2.5 forbids the emotional register. `text-display` is reserved for report results, which this phase does not render. |

**Voice assignment (UI-SPEC §7.1, LOCKED by authorship not by preference):**

- **Ledger voice** — everything the runtime asserts about itself: `runtime: listening on 127.0.0.1:53114`,
  `pid 20984`, the log path, the installed version, the signing fingerprint, the CLI twin command.
  These are claims the learner can inspect, which is exactly what Ledger voice marks.
- **Chrome voice** — the tool's own words: headings, explanatory sentences, buttons, menu labels,
  installer prose.
- **Paper voice and Code voice do not appear in this phase.** No author wrote any string here and
  no machine-under-study is displayed. A shell surface that reaches for Paper voice has found a
  spec gap, not a free choice.

**Inherited inconsistency — RESOLVED 2026-08-10, no longer open.** This phase matched the shipped
code at 400/600 while `UI-SPEC.md` §7 still said *"400 regular, 700 bold"*. The §7 weight ruling has
since superseded that row and locked the pair as `--weight-normal` 400 / `--weight-emphasis` 600, on
the measured evidence that shipped code is 37×`600` to 4×`700` and `presentation.py` is unanimous at
600. **This phase's choice was correct and is now the project rule**; it needs no change. The six
non-conforming shipped sites are named in the §7 ruling as a Phase 4 cleanup.

---

## Color

| Role | Token / Value | Usage |
|------|---------------|-------|
| Dominant (60%) | `--bg` — `#f3f5f4` light / `#0e1413` dark | Window field behind every shell-local document; installer page field. |
| Secondary (30%) | `--card` `#ffffff`/`#161e1d`, `--chip`, `--line` | The message card, the details disclosure, the AV notice block, the first-launch door cards. |
| Accent (10%) | `--accent` (default `#0e6e62`, learner-derivable) and `--accent-soft` | See reserved list below. |
| Destructive / failure | `--bad` + `--bad-bg` | The `crashed` state's card border and label only, paired with text. |
| Caution | `--warn` | The `unreachable` and `port-held` states' card border and label only, paired with text. |
| Success | **`--ok` is never rendered in this phase.** | See "Ready renders nothing" below. |

**Accent reserved for — explicit list, nothing else:**

1. The 2px focus outline with 2px offset (UI-SPEC §8.3 — *"do not remove outline"*).
2. The **one** primary action on a shell-local document (`Start it again`, `Open a bank folder`,
   `Install and restart`) using the shipped contrast-guaranteed `--accent-soft` background /
   `--accent` text pairing, never white-on-accent.
3. Inline links to a log path, a release page, or the settings file.

**Accent is never** used for runtime state, for the AV/signing notice, for every button, or as a
"brand" wash on the window. Runtime state is carried by `--warn`/`--bad` **plus a text label**;
never-colour-alone is LOCKED and applies here identically.

**"Ready renders nothing" — LOCKED for this phase.** There is no green dot, no "Runtime OK" chip,
no success toast. When the sidecar is ready, the window shows the daemon's surfaces and says
nothing about itself. Silence *is* the ready signal. Reason: `UI-SPEC.md` §2.5, LOCKED, verbatim:
*"No points, badges, levels, streak-recovery prompts, countdown pressure, or celebratory motion."*
A persistent health indicator is ambient reassurance the runtime has not earned and the learner
does not need — and its absence is what makes the *presence* of a status line meaningful.

---

## 1. Scope, and the six settings this phase registers

| Setting | Values | Default | Kind | Status |
|---|---|---|---|---|
| `first_run` | `minimal` \| `checklist` | `minimal` | RENDERER | **DEFAULT (revisitable)** — Directive §3 registration, research §5.3 F1/F2 |
| `window_chrome` | `native` | `native` | PACKAGING | **LOCKED for this phase**; the name is reserved so a later phase adds `custom` as a registration, not a fork (§2) |
| `install_notice` | `signed` \| `unsigned` | build-time, **not a user setting** | PACKAGING | **LOCKED** — selected by whether a certificate exists (D-11) |
| `runtime_status_placement` | `menu` | `menu` | RENDERER | **LOCKED for this phase**; `context-line` is **BLOCKED** on a `UI-SPEC.md` §3 amendment (§4) |
| `update_policy` | `opt_in` \| `check_on_launch` | schema `opt_in` | RUNTIME | **Pre-existing (D-13), carried forward unchanged.** The shell does not get a third policy (D-08). |
| `sample_bank` | present / absent | present | PACKAGING | **DEFAULT** — the second first-launch door needs a real fixture bank in the installed payload |

Everything else in this phase is process and packaging, not UI, and is governed by `13-CONTEXT.md`
D-01 … D-15.

---

## 2. Window chrome

**Decision: native OS window decorations. Do not build a custom titlebar. — LOCKED for Phase 13.**

Reason, quoted from research §5.1: *"A custom titlebar is the default aesthetic move in every Tauri
tutorial and it costs three things this project cannot pay: Windows Snap and Aero-shake behaviour
must be reimplemented, the drag region is a known accessibility and keyboard-focus hazard, and it is
a second place where theme tokens have to be kept in sync with `theme.py` — which is LOCKED as the
single palette source (UI-SPEC §7). The gain is a slightly more branded screenshot."*

Directive §3 asks for both options where both are defensible. Here they are not: one option costs
three real things and buys a screenshot. That is a **cost verdict**, stated plainly as §4a requires
(*"If the honest reason is cost, taste, or churn, say cost, taste, or churn"*). The setting name
`window_chrome` is reserved so a later phase that wants it adds a registration rather than a fork.

`keyboard/SR:` OS-native — Alt+Space, Alt+F4, Snap, and the OS's own window announcements all work
because we did not reimplement them. This is the accessibility argument for native, not a side effect.
`print:` n/a — window decorations are not a document. Per Directive §4a, *"'It breaks print' is not
a veto"*, and equally, print is not a requirement invented for a titlebar.
`degraded:` the window frame is the OS's and exists whether or not the sidecar is running. That is
precisely why the *unreachable* document (§3.2) can be closed, moved, and resized normally.

### 2.1 Window title

`itembank` when ready; `itembank — runtime not running` in the `unreachable`, `crashed`, and
`port-held` states. **LOCKED.** The title bar is the one place a state is legible when the window is
minimised or in a taskbar preview, and a title that says `itembank` while nothing works is a small
lie of exactly the kind §2.7 forbids.

### 2.2 The menu — two items, view-independent

D-15 forbids *"a native menu that duplicates an in-page control"*. These two duplicate nothing,
because no in-page control exists for either.

| Menu item | Behaviour |
|---|---|
| **Runtime status** | Opens a plain document showing, in Ledger voice: `runtime: listening on 127.0.0.1:<port>`, `pid <n>`, `started <ISO-8601>`, `version <v>`, `log <absolute path>`. Nothing else. |
| **Copy the CLI command for this view** | The shell asks the daemon for the equivalent command for the current path and puts it on the clipboard. **The shell holds no per-view knowledge** — the daemon owns the mapping, because the daemon owns the routes. |

This is `UI-SPEC.md`'s CLI-twin rule made visible rather than documented, and it is the same pattern
as round one's F10 empty-state ("name the one command that fills it"). ROADMAP 13 criterion 5 —
*"Every capability remains reachable from the CLI without the shell installed"* — is a claim the
learner can now check in one click instead of taking on faith.

`keyboard/SR:` both items are real OS menu items with accelerators and OS-announced labels; the
Runtime-status document opens with focus on its heading. `print:` the Runtime-status document prints
verbatim — that is exactly the content of a useful bug report, so this is a real output, not a
courtesy. `degraded:` when the runtime is not ready, **both items are replaced by a single item,
`Runtime is not running — show details`**, which opens the §3.2 document. They are never present-
but-dead. `UI-SPEC.md` §8.9, LOCKED, verbatim: *"Run/model-only actions become explicit unavailable
controls; do not render a disabled button with no reason."*

### 2.3 Two shell capability rules that are UI rules, not security footnotes

1. **The shell performs no prefetch, no route preloading, and no client-side caching of daemon
   responses.** A webview shell is exactly where someone would add "warm the next route," and doing
   so would put not-yet-disclosed content in the window's DOM — the same **B4 answer-leak** failure
   that rejects research §6.3 C2 and §3.4 G3. Truncation and staged reveal are server-side or they
   are not real. **LOCKED.**
2. **The daemon-served origin is granted no Tauri filesystem, shell, or process capability.** The
   pages in the window run with exactly the browser powers they have today under `python itembank.py
   daemon .`, so the shell channel and the browser channel cannot diverge in what a page can reach.
   **LOCKED.**

---

## 3. Sidecar liveness — the phase's primary surface

### 3.1 The finding that shapes everything below

**A "degrade honestly" screen cannot be served by the thing that is down.** Every existing itembank
surface is rendered by the Python daemon. If the sidecar never came up, there is no page, no
`theme.py` palette computation, no `presentation.py`, and no route to fall back to. A shell that
navigates to `http://127.0.0.1:<port>/` and gets a connection refusal shows the WebView's own error
page — a Chromium `ERR_CONNECTION_REFUSED` screen naming an IP address, which tells the learner
nothing and is the exact opposite of "say exactly what is unavailable."

**Therefore: the shell owns two small static local documents.** This is the only new rendering
surface Phase 13 adds, and it exists because §2.7 cannot be satisfied any other way.

### 3.2 The two shell-local documents

| Document | Purpose |
|---|---|
| `runtime-not-ready.html` | One document, five states (§3.3), selected by a data attribute the shell sets. |
| `runtime-status.html` | The menu's Ledger-voice readout (§2.2). |

**Construction rules — LOCKED:**

- Both are **static files bundled with the shell**, not fetched, not templated at runtime, and not
  network-dependent.
- Their CSS is **generated at build time from `surfaces/theme.py`** (the `theme_css(system default)`
  computed-constant path 04-03 already established). A literal hex in `shell/` fails the build.
- They respect `prefers-color-scheme` for light/dark. They do **not** reflect a learner's custom
  accent, because reading `itembank.json` from the shell would be a second config reader.
  **Accepted and recorded:** on a failure screen the default teal appears even if the learner set a
  different accent. Cost of the alternative: a second settings parser in Rust. Not worth it.
- **They contain no motion.** No spinner, no pulse, no progress bar. §2.5 is LOCKED and a spinner on
  a failure screen is decoration that implies work is happening when it may not be.
- One `role="status"` region per document; state changes announce once (UI-SPEC §8.7).
- Focus lands on the document's `<h1>` when it appears. The primary action is the next tab stop.

### 3.3 The five states, with copy

Every state below is **LOCKED copy** unless marked otherwise. Placeholders in `<angle brackets>`
are substituted; nothing else varies.

#### (a) `starting`

Shown only after a **400ms grace period** — a document that appears for 200ms and is replaced is a
flash, and a flash is motion nobody asked for. If the handshake arrives inside 400ms the learner
sees the window field and then the app, with no intermediate screen at all.

> **Starting the runtime**
>
> itembank is starting its runtime. This window will load as soon as the runtime is listening.

After **10 seconds** with no handshake, one additional line appears in the same region (announced
once, no focus move):

> The runtime has not reported a port after 10 seconds.

and a `Show details` disclosure becomes available carrying the sidecar path and the log path.
**No countdown, no elapsed-seconds ticker, no percentage.** An elapsed counter is a moving number
that means nothing; a single line at a threshold is a fact.

`keyboard/SR:` heading focus; the disclosure is a native `<details>` announced with its state; the
10s line is announced once through the status region. `print:` prints as-is; a printed "starting"
page is a legitimate bug-report artifact. `degraded:` this **is** the degraded path — it depends on
nothing but the shell.

#### (b) `ready`

**Renders nothing.** The window navigates to the daemon and the shell-local document is gone. See
"Ready renders nothing" in §Color.

#### (c) `unreachable` — the sidecar never handshook, or the port refuses

Card border `--warn`, label `Runtime unavailable` in Ledger voice.

> **The runtime did not start**
>
> itembank could not start its runtime, so lessons, sittings, scoring, and evidence are unavailable
> in this window. Nothing was scored and nothing was recorded.
>
> Your banks and evidence are untouched. They are files on disk, and this failure did not write to
> them.

Actions: **`Start it again`** (primary) · `Show details`.

`Show details` (native `<details>`, closed by default) contains, in Ledger voice: the expected
sidecar executable path, the last lines the sidecar wrote to stdout/stderr, the log file path, and
the CLI twin — `itembank daemon .` — with the sentence *"The runtime also runs without this window:"*
before it.

The second paragraph is not reassurance padding. It is the §2.7 obligation discharged precisely:
the surface says **what is unavailable** (lessons, sittings, scoring, evidence) and **what did not
happen** (no score, no record), and it does not fake a session that might have been in flight.

`keyboard/SR:` `<h1>` focus, then the primary button, then the disclosure; the state label is text,
not colour. `print:` prints complete with the details disclosure **forced open** — a printed failure
page with a collapsed cause is useless. `degraded:` shell-local; depends on nothing.

#### (d) `crashed` — the sidecar was ready and then exited

Card border `--bad`, label `Runtime stopped` in Ledger voice.

> **The runtime stopped**
>
> The itembank runtime stopped after it started. Anything you submitted was recorded when you
> submitted it. Anything on screen that you had not submitted was not recorded.
>
> Exit code `<n>` · stopped `<ISO-8601>`

Actions: **`Start it again`** (primary) · `Show details`.

The second sentence is the most important string in this phase. It is the exact boundary of what the
runtime can honestly claim, and it is why this state must never say "your work was saved" (a claim
the shell cannot verify) or "your work was lost" (a claim that is false for everything already
appended to the evidence log).

`keyboard/SR:` as (c). `print:` as (c), details forced open, exit code included. `degraded:`
shell-local.

#### (e) `port-held` / another instance is running (D-05, D-06)

Card border `--warn`, label `Already running` in Ledger voice.

> **itembank is already running**
>
> A runtime is already listening on `127.0.0.1:<port>`. This window did not start a second one.

Actions when attach succeeded: **`Use the running one`** (primary) — focuses the existing window.

Actions when attach **failed** (D-06's named refusal): **no retry button at all.** The button is
**absent**, and the reason is the body copy:

> itembank is already running, but this window could not attach to it. Close the other itembank
> window, or end the process named `<name>` (pid `<n>`), then start itembank again.

This is §8.9 applied literally: an action that cannot work is absent with a stated reason, never a
dead disabled button.

`keyboard/SR:` heading focus; where the primary action is absent the disclosure is the next tab stop
and nothing announces a control that is not there. `print:` prints with pid and port — the two facts
someone needs to fix it. `degraded:` shell-local.

### 3.4 What the shell must never do in these states

- Never show the WebView's native `ERR_CONNECTION_REFUSED` page. If it is ever visible, that is a
  defect against this contract, not a cosmetic issue.
- Never retry silently in a loop while showing `starting`. A retry is learner-initiated and visible
  (mirrors `UI-SPEC.md` §5B: *"a retry is learner-initiated and linked to the original interaction"*).
- Never render a cached copy of a previously-served daemon page as if it were live (§2.3 rule 1).
- Never claim a session state, a score, a count, or an evidence write it did not observe.

---

## 4. Runtime state and the context line — a blocked option, recorded

**BLOCKED, not shipped.** A persistent runtime-health chip in the shell's context line is a
defensible second treatment, and Directive §3 would normally say ship both. It is blocked by a
LOCKED rule that is not this phase's to amend. `UI-SPEC.md` §3, verbatim: *"**LOCKED:** the context
line contains only bank/lesson context, objective, session progress, and feedback mode. Secondary
metadata is in an accessible `<details>` disclosure."* A healthy-runtime chip is secondary metadata.

**One narrow exception is permitted, and it is already in the spec.** The §3 wireframe's own context
line reads `lesson / objective / 3 of 8 / practice / offline?` — a degraded indicator is drawn in
the locked shell. So:

> **The context line shows runtime or network state only when it is not ready. Silence means ready.**
> — **DEFAULT (revisitable)**, resolving the tension between §3's four-item sentence and §3's own
> five-item diagram in the direction §2.7 requires.

`runtime_status_placement: context-line` stays registered as a name and unbuilt. Reviving it needs a
`UI-SPEC.md` §3 amendment, which is the same class of blocker as research §2.3's H3 and §1.3's R3.

---

## 5. First launch

**Verdict on research §5.3, recorded per binding instruction 3.**

| Option | Verdict | Reason |
|---|---|---|
| **F1 — one screen, two doors** | **ADOPTED as default** (`first_run: minimal`) | Fastest path to the actual product; leaves the learner in a real bank in one click; teaches nothing about the app, which is correct because there is nothing to teach until there is a bank. Cost **S**. |
| **F2 — F1 plus a three-step checklist** | **ADOPTED as the second registration** (`first_run: checklist`) | Directive §3. Genuinely useful for a loop that is not obvious from one screen, and the one onboarding pattern that does not become engagement pressure **provided** it has no streak, no completion celebration, and a permanent dismiss. F1 is a subset of F2's DOM, so this is one view with an optional block, not two views. Cost **S-M**. |
| **F3 — guided tour with highlighted regions** | **REJECTED** | On cost and value. Research §5.3, verbatim: *"it is **per-surface coupling** that rots the moment any of the eleven phases changes a layout, so its maintenance cost is paid by every future phase rather than by Phase 13; an overlay that traps focus over the real UI is a B1 hazard that has to be got exactly right for no product gain; and it is the most-skipped pattern in desktop software."* **Explicitly NOT rejected on JavaScript or no-JS grounds** — that objection was withdrawn in research §0.1 and is not revived here. |

### 5.1 F1 — the two doors

> **Open a bank to start**
>
> itembank reads question banks from a folder of markdown files on this machine.

Actions: **`Open a bank folder`** (primary, native OS folder picker) · `Open the sample bank`.

`keyboard/SR:` two real buttons in DOM order; focus lands on the first; the native picker is the
OS's own dialog and is keyboard-operable by construction. `print:` n/a — this screen is a chooser,
not a document, and nothing on it is a study artifact. `degraded:` **this view is served by the
daemon**, so if the sidecar has not come up the learner sees §3.3(c) instead. That is correct and
deliberate: first launch is the single most likely place a packaging failure surfaces, so the
unreachable document must be at least as good as the welcome screen. Named as a UAT.

### 5.2 F2 — the checklist block

Appended below the doors, persisted, permanently dismissible:

> **Three things to try**
> 1. Open a bank
> 2. Run your first sitting
> 3. See your evidence
>
> `Dismiss this permanently`

**Forbidden in this block, LOCKED:** any streak, any day count, any completion celebration or
motion, any percentage, any "2 of 3 complete" progress framing, any re-appearance after dismissal.
§2.5 is LOCKED and a checklist that nags violates it. Completed steps get a text marker and no
colour-only treatment.

`keyboard/SR:` an ordered list of real links; the dismiss control is a real button and its effect is
announced once. `print:` prints as a plain ordered list. `degraded:` daemon-served; §3.3(c) applies.

---

## 6. The installer

Per D-07: **NSIS, per-user by default, machine-wide optional.** Per-user avoids the UAC prompt, and
research §5.2 states the UI reason: *"a learning tool that asks for administrator rights before
showing anything is a tool a cautious user cancels."*

### 6.1 The AV / signing screen is first-class, not a footnote

Research §5.2, verbatim: *"The installer should state plainly, before install, that the app bundles
a Python runtime and that some AV products flag frozen Python, with the signing fingerprint shown.
This is the 'degrade honestly' principle (UI-SPEC §2.7) applied to the one moment the product is
most likely to look like malware."*

**`install_notice: signed`** — shown when D-11's certificate exists:

> **This app includes a Python runtime**
>
> itembank runs its scoring engine as a bundled Python program. Some antivirus products flag
> applications that bundle one. If yours quarantines itembank, that is a false positive.
>
> Signed by `<certificate subject>`
> Fingerprint `<sha256, full, monospace, wrapped>`
> Reporting path and release checklist: `<url>`

**`install_notice: unsigned`** — shown when it does not (D-11's honest branch):

> **This build is not code-signed**
>
> Windows SmartScreen will warn you when you run itembank, and some antivirus products flag
> applications that bundle a Python runtime. Both are expected for an unsigned build.
>
> Verify your download before continuing. The published SHA-256 for this release is
> `<sha256, full, monospace, wrapped>` — compare it with
> `certutil -hashfile <file> SHA256`.

**LOCKED:** the unsigned variant never implies the problem is solved, never hides the warning, and
never asks the user to disable protection. D-11's own words: *"it does not pretend the problem is
solved and does not invent a certificate that does not exist."*

`keyboard/SR:` NSIS-native page, standard tab order, no custom controls; the fingerprint is
selectable text, never an image. `print:` the notice is reproduced verbatim in `README` Install and
in the release notes, which is the printable form — the installer page itself is not a document.
`degraded:` the installer runs offline and states nothing it cannot verify locally.

### 6.2 The uninstaller must not be able to delete the evidence store — LOCKED

> Uninstalling removes the itembank application. Your banks and your evidence stay where they are:
> `<resolved user data path>`.

**No "also delete my data" checkbox ships in this phase.** A checkbox that deletes the append-only
evidence store is the single most destructive control this product could have, and Directive §4.3
keeps evidence on disk as a non-negotiable. If a later phase wants deletion, it is its own designed
flow with the §7 destructive-confirmation grammar, not an installer checkbox.

`keyboard/SR:` NSIS-native. `print:` the sentence is in the README. `degraded:` n/a.

---

## 7. The updater — a copy contract, not a dialog afterthought

### 7.1 The defect this section exists to catch

`.claude/CLAUDE.md` records the accepted risk, verbatim: *"The schema default is `opt_in`, so a fresh
install with no settings file never phones home without being asked; this repository's own checked-in
`itembank.json` sets `check_on_launch` so the updater gets dogfooded… The background check is
throttled to the configured interval and prints a one-time disclosure before its first request."*

Today that disclosure is a `print()` to the daemon's startup stream (`surfaces/update.py`
`background_check`), and 02.1's Copywriting Contract locks its wording. **In a packaged window,
stdout is invisible.** Shipping the shell without acting on this makes D-13's "prints a one-time
disclosure before its first request" false in the packaged channel, silently. That is the whole
reason this is a UI contract.

### 7.2 The contract

**LOCKED:**

1. **The disclosure renders in the window, with the same text, before any request exists.** The
   string is the 02.1 locked wording, reproduced exactly:

   > itembank will check GitHub for a new version at most once every `<N>` hours. Nothing but the
   > request leaves this machine. Set `"update_policy": "opt_in"` in `itembank.json` to turn it off.
   > This notice appears once.

2. **One additive line is permitted, and only this one:** `Your settings file is at <resolved path>.`
   Justification: in a packaged per-user install the learner has no reason to know where
   `itembank.json` lives, so the locked sentence's instruction is unactionable without it. This adds
   a fact; it rewords nothing.

3. **It is a `StatusNotice`, not a screen and not a modal.** It renders at the top of the first
   surface the window shows. Reason: D-15 — *"This phase adds no screen, no navigation, and no
   theming of its own beyond window chrome."* D-15 forbids the shell inventing surfaces; it cannot
   be read as permission to suppress a disclosure the accepted-risk record requires. A `StatusNotice`
   on an existing surface satisfies both. `role="status"`, not `role="alert"` — it does not block an
   action (UI-SPEC §8.7).

4. **Render-once semantics are identical to the CLI's print-once semantics.** `notified_at` is
   written when the notice is *rendered*, not when it is dismissed, and the launch that shows it
   performs **no check** — exactly the shipped `background_check` behaviour. One state record
   (`updates/check_state.json`), one behaviour, two renderings. The shell writes nothing; the daemon
   owns the record, as it does today.

5. **One disclosure covers both consumers.** D-08 gives one release channel two consumers (the 2.1
   `.pyz` updater and `tauri-plugin-updater`). There is one `notified_at`, so there is one notice.
   A second disclosure for the shell would be a second consent record and a second store.

6. **No telemetry exists and the copy must not imply any.** These words are **forbidden** anywhere
   in updater copy, and this list is a checkable fixture: *usage, analytics, telemetry, diagnostics,
   anonymous, help us improve, opt out of data collection, crash reports*. The only true statement
   about what leaves the machine is the one already locked: *"Nothing but the request leaves this
   machine."*

7. **Dismissal.** One control, `Got it`. It closes the notice. It is not a consent gate and must not
   be styled as one; there is no `Allow` / `Deny` pair, because the policy already lives in
   `update_policy` and inventing a second consent surface would create a second policy.

`keyboard/SR:` a `role="status"` region announced once without a focus jump; `Got it` is a real
button in reading order after the notice text. `print:` prints inline with the page — a printed page
carrying its own disclosure is correct, not noise. `degraded:` **with no network the notice still
renders** (it precedes any request) and no check is attempted; with the daemon down there is no page
and §3.3(c) applies, and the disclosure waits for the next successful launch, unnotified. It is
never skipped by a failure.

### 7.3 Update available, and the restart the updater forces

`tauri-plugin-updater` auto-exits the app during install — a Windows-installer limitation, not a
choice. Copy that hides it would be a surprise mid-sitting.

> **A new itembank version is available: v`<latest>` (you're on v`<current>`).**
>
> Installing restarts itembank. Finish anything in progress first.

Actions: **`Install and restart`** (primary) · `Not now`.

**LOCKED:** `Install and restart` names the restart in the button, not only in the body. `Not now`
is a real dismissal that does not re-prompt within the throttle interval. Neither control appears
while a sitting is mid-submit.

The 02.1 CLI line stays verbatim and unchanged for the CLI channel: `A new itembank version is
available: v<latest> (you're on v<current>). Run 'itembank update' to install it.` One channel, two
renderings, no divergence.

`keyboard/SR:` `role="status"`, announced once, focus unmoved; two real buttons.
`print:` prints inline. `degraded:` offline, the background check stays silent (DEL-07's silence rule
is unchanged), so this notice simply never appears — it is not replaced by an error.

---

## Copywriting Contract

Every row below is **LOCKED** for this phase unless marked. Rows marked *(verbatim, 02.1)* or
*(verbatim, UI-SPEC §7)* are reproduced from an already-locked contract and were neither edited nor
re-voiced.

| Element | Copy |
|---------|------|
| Primary CTA — first launch | `Open a bank folder` |
| Secondary CTA — first launch | `Open the sample bank` |
| Primary CTA — runtime failed | `Start it again` |
| Primary CTA — another instance running | `Use the running one` |
| Primary CTA — update available | `Install and restart` |
| Empty state heading (no bank yet) | `Open a bank to start` |
| Empty state body | `itembank reads question banks from a folder of markdown files on this machine.` |
| Loading state (after 400ms) | `Starting the runtime` / `itembank is starting its runtime. This window will load as soon as the runtime is listening.` |
| Loading state (after 10s, additive line) | `The runtime has not reported a port after 10 seconds.` |
| Error — runtime never started | `The runtime did not start` / `itembank could not start its runtime, so lessons, sittings, scoring, and evidence are unavailable in this window. Nothing was scored and nothing was recorded.` / `Your banks and evidence are untouched. They are files on disk, and this failure did not write to them.` |
| Error — runtime stopped after starting | `The runtime stopped` / `The itembank runtime stopped after it started. Anything you submitted was recorded when you submitted it. Anything on screen that you had not submitted was not recorded.` |
| Error — port held, attach succeeded | `itembank is already running` / `A runtime is already listening on 127.0.0.1:<port>. This window did not start a second one.` |
| Error — attach failed (named refusal, no retry control) | `itembank is already running, but this window could not attach to it. Close the other itembank window, or end the process named <name> (pid <n>), then start itembank again.` |
| Runtime status readout (Ledger voice) | `runtime: listening on 127.0.0.1:<port>` · `pid <n>` · `started <ISO-8601>` · `version <v>` · `log <path>` |
| CLI twin, in the details disclosure | `The runtime also runs without this window:` then `itembank daemon .` |
| Updater disclosure *(verbatim, 02.1)* | `itembank will check GitHub for a new version at most once every <N> hours. Nothing but the request leaves this machine. Set "update_policy": "opt_in" in itembank.json to turn it off. This notice appears once.` |
| Updater disclosure — the one additive line | `Your settings file is at <resolved path>.` |
| Updater disclosure — dismissal | `Got it` |
| Update available (in-window) | `A new itembank version is available: v<latest> (you're on v<current>).` then `Installing restarts itembank. Finish anything in progress first.` |
| Update available *(verbatim, 02.1, CLI channel unchanged)* | `A new itembank version is available: v<latest> (you're on v<current>). Run 'itembank update' to install it.` |
| Install notice — signed | `This app includes a Python runtime` / `itembank runs its scoring engine as a bundled Python program. Some antivirus products flag applications that bundle one. If yours quarantines itembank, that is a false positive.` + subject, fingerprint, reporting path |
| Install notice — unsigned | `This build is not code-signed` / `Windows SmartScreen will warn you when you run itembank, and some antivirus products flag applications that bundle a Python runtime. Both are expected for an unsigned build.` + published SHA-256 + `certutil` command |
| Destructive confirmation — uninstall | `Uninstalling removes the itembank application. Your banks and your evidence stay where they are: <resolved user data path>.` |
| Model unavailable *(verbatim, UI-SPEC §7 — unchanged, restated because the shell must not re-voice it)* | `Generated help is unavailable. You can keep learning with the lesson and authored hints.` |

**Forbidden strings in this phase, checkable:** `usage`, `analytics`, `telemetry`, `diagnostics`,
`anonymous`, `help us improve`, `crash reports` (updater copy); `Runtime OK`, `All systems normal`,
`Connected ✓` (status copy — see "Ready renders nothing"); any `Retry` control that is present and
disabled; any string claiming work was saved or lost that the shell did not observe.

---

## 8. The three lines, per element

Research §0.1's discipline, applied to every surface this phase adds.

| Element | `keyboard/SR:` | `print:` | `degraded:` |
|---|---|---|---|
| Native window + decorations | OS-native: Alt+Space, Alt+F4, Snap, OS window announcements — all free because nothing was reimplemented | n/a — chrome is not a document | exists regardless of the sidecar; that is why a failure document can be closed and moved |
| Menu → Runtime status | real OS menu item with accelerator; the document opens with focus on its `<h1>` | prints verbatim; this is the content of a bug report | replaced by `Runtime is not running — show details`, never present-and-dead (§8.9) |
| Menu → Copy CLI command | real OS menu item; clipboard result announced once via the page's status region | the command string is Ledger voice and prints inline wherever it appears | absent with a stated reason when there is no view to describe |
| `starting` document | `<h1>` focus; `<details>` native and state-announced; 10s line announced once | prints as-is | is itself the degraded path; shell-local, depends on nothing |
| `unreachable` document | `<h1>` → primary button → disclosure; state label is text not colour | prints complete, details **forced open** | shell-local; no network, no daemon, no Python needed |
| `crashed` document | as above; exit code is text in Ledger voice | prints complete with exit code and timestamp | shell-local |
| `port-held` / refused | as above; where the primary action is absent nothing announces a control that is not there | prints with pid and port | shell-local |
| First launch — two doors | two real buttons in DOM order; focus on the first; native OS folder picker | n/a — a chooser is not a study artifact | daemon-served; falls to the `unreachable` document, which must be at least as good |
| First launch — checklist | ordered list of real links; dismiss is a real button, effect announced once | prints as a plain ordered list | daemon-served; same fallback |
| Updater disclosure notice | `role="status"`, announced once, no focus jump; `Got it` in reading order | prints inline with the page | renders with no network; waits for the next launch if the daemon is down; never skipped by a failure |
| Update-available notice | `role="status"`; two real buttons; never shown mid-submit | prints inline | offline → silent, per DEL-07; not replaced by an error |
| Installer AV/signing page | NSIS-native tab order; fingerprint is selectable text, never an image | reproduced verbatim in README Install and the release notes | runs offline; states nothing it cannot verify locally |
| Uninstaller data statement | NSIS-native | in the README | n/a |

---

## UI Considerations

Applicable state considerations resolved: **7 covered, 2 backstop, 2 unresolved.**

| Category | Element(s) | Status | Resolution / Reason |
|----------|------------|--------|---------------------|
| empty | first-launch view, no bank configured | ✅ covered | Renders the two doors and the `Open a bank to start` copy; never an empty window and never a bare file browser. |
| loading | shell → sidecar handshake | ✅ covered | 400ms grace, then the `starting` document; a 10s threshold line; no spinner, no ticker, no percentage. |
| error | sidecar never started / stopped / port held / attach refused | ✅ covered | Four distinct documents with distinct copy (§3.3 c/d/e); the WebView's own `ERR_CONNECTION_REFUSED` page is a defect if ever visible. |
| populated | sidecar ready | ✅ covered | The shell renders nothing of its own; the daemon's surfaces are the window's content, unchanged from the browser channel. |
| partial | sidecar ready, bank folder missing or unreadable | ✅ covered | Falls through to the daemon's existing empty/degraded bank states (Phase 2/3/4); the shell adds no second empty state for the same condition. |
| zero-one-many | many banks in the configured folder | ✅ covered | The daemon's existing picker; the shell contributes only the native folder dialog. |
| error-copy | update check offline / rate-limited | ✅ covered | Unchanged from 02.1: the background check stays silent; the explicit command says which happened. The shell adds no third behaviour. |
| long-text | signing fingerprint (64 hex), install path, user-data path, sidecar path, `<name> (pid <n>)` | 🧪 backstop | Must wrap in `--font-ledger` with `overflow-wrap:anywhere`, never truncate, never ellipsis. Verified by responsive snapshots of the AV page and the `unreachable` document at 1280 / 768 / 375 CSS px. |
| overflow | `Show details` contents — many stderr lines from a failing sidecar | 🧪 backstop | The disclosure scrolls within a bounded region with a labelled wrapper; the log path stays visible outside the scroll area so it is reachable when the excerpt is not enough. |
| unresolved | window size, position, and DPI persistence across monitor changes | ⚠ unresolved | Planner treats as an assumption. Not in ROADMAP 13's criteria; a wrong guess is cosmetic and reversible. |
| unresolved | Linux WebKitGTK blank/flickering-window state and its copy | ⚠ unresolved | Deferred with the hardware (D-13). When Linux lands it needs its own liveness state — a window that renders blank is not "unreachable" and must not borrow that copy. |

---

## 9. Inherited rejections this phase must not revive

| Rejected | Ground | Phase 13 consequence |
|---|---|---|
| **§6.3 C2** — accordion of all `## SCENARIO` stages with unrevealed ones collapsed | **B4 answer leakage.** Research: *"the unrevealed content is in the DOM, and for a case whose later stages contain the finding that discriminates the answer, that is a leak under UI-SPEC §8.4 and §11.1."* **Unaffected by the §0.1 constraint correction; the rejection stands.** | Phase 9 owns the surface, but Phase 13 owns a way to break it: **the shell performs no prefetch, no route preloading, and no response caching** (§2.3 rule 1). Truncation must stay server-side or the guarantee is lost from the shell side. |
| **§3.4 G3** — `<details>`-hidden below-gate lesson content | B4 answer leakage, same ground | Same shell consequence as above. |
| **§5.3 F3** — first-launch guided tour | Per-surface coupling cost, focus-trap hazard, most-skipped pattern. **Reconsidered on merit; verdict unchanged; the withdrawn no-JS reason is not reproduced.** | Not built. `first_run` has two values, not three. |
| Custom titlebar as the default | Snap/Aero reimplementation, drag-region a11y hazard, second palette sync point — a cost verdict, stated as cost | `window_chrome: native` only; the name is reserved for a later registration. |
| Celebration motion, gamified progress, streaks | `UI-SPEC.md` §2.5, LOCKED | No completion animation on the F2 checklist; no success state at all for the runtime. |

**Constraints that do not exist and are not enforced here** (Directive §4a, verbatim: *"These do not
exist. Do not enforce them"*): a no-JavaScript rule; a required print path (*"'It breaks print' is
not a veto"*); a vendored-asset budget (*"KaTeX is an example, not a quota"*); and *"no dependencies
as a security control"* — replaced by the supply-chain rule below.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not applicable — no `components.json`, no npm, no component registry in this repo (verified by scout, 2026-08-10) |
| any third-party UI registry | none | not applicable |
| **Third-party toolchain and runtime artifacts** — Tauri 2.x crates, the Rust toolchain, `tauri-plugin-updater`, PyInstaller, the NSIS bundler | the shell and the frozen sidecar | **OWED at plan time, not performed here.** Directive §4a, verbatim: *"Every third-party artifact — library, font, JS bundle, toolchain — is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent."* Per 13-CONTEXT D-14 the plan commits a lockfile and records pinned versions, checksums, and a named license review. This UI-SPEC records the requirement; it does **not** claim the review was run, because it was not. |

**Explicitly not a mitigation:** "itembank has no dependencies." Directive §4a retired that argument
on 2026-08-09. A Phase 13 threat table that accepts supply-chain risk on those grounds is stale and
must be rewritten.

---

## 10. Open questions a later phase should revisit

1. **`window_chrome: custom`** — needs an answer for Windows Snap/Aero-shake, a keyboard-safe drag
   region, and a second palette sync point before it is more than a branded screenshot.
2. **Runtime state in the context line when healthy** — blocked on a `UI-SPEC.md` §3 amendment (§4).
   Same class as research H3 and R3.
3. **The learner's custom accent on shell-local failure documents** — currently the default palette
   snapshot. Fixing it costs a second settings reader in the shell; revisit only if a learner
   actually notices.
4. ~~**Font weight 400/700 vs the shipped 600**~~ — **CLOSED 2026-08-10.** The UI-SPEC §7 weight
   ruling locked 400/600 on measured evidence, vindicating this phase's choice. What remains is the
   mechanical cleanup of six named shipped sites, tracked there, not here.
5. **Linux liveness copy** — a blank WebKitGTK window is not "unreachable" and must not borrow that
   copy (D-13, deferred with hardware; Electron is the named fallback).
6. **Tray residency, auto-start on login, OS notifications, `.md` file association** — deferred by
   13-CONTEXT. Each is its own small phase; each would add a surface this contract does not cover.
7. **A designed evidence-deletion flow** — deliberately absent from the uninstaller (§6.2). If ever
   wanted, it needs the §7 destructive-confirmation grammar, not a checkbox.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** APPROVED - gsd-ui-checker, 2026-08-10. 6/6 dimensions PASS.
