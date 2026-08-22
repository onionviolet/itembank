# Handoff: continuing itembank on a Mac

Written 2026-08-21 at Weibao's request. Everything below is checked, not
remembered. Paste the "Opening prompt" section into a fresh session on the Mac.

## Get it running, in order

```bash
git clone https://github.com/onionviolet/itembank.git
cd itembank
python3 --version          # needs 3.11 or newer
python3 itembank.py lint fixtures/sample_bank.md
python3 tests/daemon_roundtrip.py
```

No install step and no dependencies for the core loop. If those three commands
work, the product works.

## What is different on a Mac, specifically

**1. Two test failures should disappear, and that is expected.**
`tests/journal_roundtrip.py` fails on Windows in `check_lock_busy` with a
`msvcrt.locking` unlock error. That is a Windows-only path. On a Mac it should
pass. If it does not, it is a real bug and worth chasing, because the Windows
one never was.

`tests/lesson_roundtrip.py` fails on a pre-13.5 golden fixture drift. That is
platform-independent and will still fail. Not caused by recent work.

**2. Six runtime modules branch on platform:** `audit_writer.py`, `evidence.py`,
`journal.py`, `model.py`, `runner.py`, `surfaces/day.py`. They use `msvcrt`,
`win32`, or `APPDATA`. All have POSIX branches. `.planning/WINDOWS.md` (61
lines) records the Windows-specific decisions; read it if a path behaves
oddly, not otherwise.

**3. The course root is a Windows absolute path.** The real EMT course lives at
`C:\Users\wayba\Downloads\Personal\itembank-courses\emt-unit-1` and is NOT in
this repository, by design: `itembank guard` fails CI if real bank content
lands here. Copy that folder to the Mac and point at it with its new path.
It contains `course.md`, one lesson, one 10-item bank, `_attempts/`, and
`_evidence/`.

**4. `reasonix.toml` carries Windows paths** in its allowlist and its OCR MCP
server path. It is a tool config, not product config. Ignore or rewrite it.

**5. dsh installs the same way** (`npm i -g @deepseek-ai/dsh@0.1.0-rc.7`), but
read `deps/dsh-pins.txt` first. A plain install of that version FAILS today
with ETARGET. The working install is reproduced with:

```bash
cd deps/dsh && npm ci
```

**6. The local model** is Ollama serving `qwen3.8-27b:latest`. The profile is
already in `itembank.json` as `local-qwen` and points at
`http://127.0.0.1:11434/v1/chat/completions`. `model_backend.active` is empty,
so nothing reaches a model until you set it. That is deliberate.

## Where the work stands

| Item | State |
|---|---|
| 17A-06 | Done. Local profile, five typed unavailable states, dsh embedded as the Agent tab. |
| 17A-07 | **Planned, not built.** The agent operation seam: one skill run, one journal write, one undo. `autonomous: true`. |
| 17A-08 | **Planned, not built.** The shelf home and four home modes. `autonomous: true`. |
| 13.9-03 | **Open, and it needs a human.** Sit the real EMT bank end to end. Started 2026-08-16, abandoned at question 0. Blocks the 17A token freeze and all of 17B. |
| 17A-04 | Blocked on 13.9. |

Two execution prompts are ready to paste:
`.planning/PROMPT-deepseek-17A-07-2026-08-21.md` and
`.planning/PROMPT-ui-flow-agentic-lms-2026-08-21.md`.

## What changed on 2026-08-21, and why it matters

Weibao sat the skeleton for about ten minutes. It was the first real use of
this product in twelve completed phases, and it produced two defects that
52,069 lines of tests could not:

1. `/lesson/<stem>` existed, worked, and nothing linked to it. Every test knew
   the URL already.
2. The sitting had no link back to the index. The index existed the whole
   time: `serve` and `daemon` are the same server.

Both fixed, both guarded, both guards proven by removing the fix.

It also produced six budget rules in `PLANNING-DIRECTIVES.md`, from measured
numbers: planning prose is 2.7 lines per line of runtime code, 391 `docs`
commits against 367 code commits, 129 summary files holding 23,261 lines, and
two lines of learner evidence recorded in the project's entire history.

**Summaries are now exceptional, not routine.** Write one only when a plan is
left incomplete or a measured fact contradicts it. The commit messages are the
record.

## Opening prompt for a fresh Mac session

---

You are continuing work on `itembank` on a Mac. The repository is at
`<path>`, branch `main`.

Read `.planning/EXEC-CONTEXT.md` and `.planning/HANDOFF-MAC-2026-08-21.md`
first, and nothing else until a specific question needs it. Do NOT read
`ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `UI-SPEC.md`, `AGENT-WORKFLOW.md`,
or `SOURCE-TO-COURSE.md` up front. That stack is about 122,000 tokens and one
previous run spent 5.1 billion tokens re-reading it.

The six budget rules in `PLANNING-DIRECTIVES.md` under "Budget discipline" bind
you. In particular: do not write a summary unless a plan was left incomplete or
a measured fact contradicts it, do not plan a phase whose inputs do not exist,
and end every turn with something openable.

No em dash characters anywhere.

Two plans are ready to execute and both are `autonomous: true`:
`17A-07-PLAN.md` (the agent operation seam) and `17A-08-PLAN.md` (the shelf
home). Weibao chose the shelf home and the "own area plus proposals in place"
agent placement on 2026-08-21, and asked that the options he did not pick ship
as settings rather than being deleted.

Before you start either, check whether Phase 13.9-03 is still open. It requires
Weibao to sit one real EMT bank through `itembank serve` end to end, it is
`autonomous: false` because no model can do it, and it blocks the 17A token
freeze and all of 17B. If it is still open, say so in your first paragraph.

Start by running `python3 tests/daemon_roundtrip.py` and telling me whether the
two known-failing suites behave differently on this platform than they did on
Windows.

---

## Two things to check on the Mac that nobody has

1. **`tests/journal_roundtrip.py check_lock_busy`.** It has never passed. If it
   passes on POSIX, the file-locking path has only ever been verified on one
   platform.
2. **The packaged app.** `scripts/build_shell.ps1` is PowerShell and the Tauri
   shell was only ever built on Windows. Phase 18 targets external installs.
   Nobody has built this on macOS.
