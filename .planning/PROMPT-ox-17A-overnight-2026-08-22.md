# Prompt: hand 17A-07 and 17A-08 to Ox Alpha overnight, on the Mac

Written 2026-08-22. This is the Mac and OpenRouter variant of
`PROMPT-deepseek-17A-07-2026-08-21.md`, which was written for Windows and a
local model. Differences from that file are listed at the bottom so the two do
not silently drift.

Run it with `scripts/ox_overnight.sh`, which supplies the text below as the
task. One plan per invocation, 07 first.

---

You are executing one finished plan on `itembank`, a Python project at
`/Users/weiwei/Documents/Dev/itembank`. Work on branch `main`. You are on
macOS, not Windows.

## Read exactly two files first, and no others

1. `.planning/EXEC-CONTEXT.md`
2. `.planning/phases/17A-visual-system-component-foundation/<PLAN_ID>-PLAN.md`

Do NOT read `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `UI-SPEC.md`,
`AGENT-WORKFLOW.md`, `SOURCE-TO-COURSE.md`, or `PLANNING-DIRECTIVES.md`. That
stack is about 122,000 tokens. The plan already cites what it needs. Reading
them is the single most expensive mistake available to you here.

For background on what already exists, read
`.planning/phases/17A-visual-system-component-foundation/17A-06-SUMMARY.md`.
Nothing else.

## Act first

Write a file or run a command in your first turn. Do not restate the plan, do
not summarize these rules, do not produce an analysis section. Reasoning longer
than the code you are about to write means you are spending the budget in the
wrong place.

## The job

Execute `<PLAN_ID>-PLAN.md`, every task, in order. Both plans in this run are
`autonomous: true`, so there is no checkpoint to wait for.

Write the test before the code in every task. That is not a style preference:
two bugs in an earlier plan were caught that way, and two guards were proven by
deleting the fix and watching the suite fail. Do the same here.

## Five rules you cannot break

1. The runtime owns correctness, session state, evidence, and keyed assessment
   disclosure. A model never settles a score and never decides how much of a
   key to reveal. Nothing you write may put scoring, marking, or key disclosure
   on the Agent page.
2. Exactly one parser (`model.py`), one scorer (`runtime.py`), one evidence
   store, one writer (`journal.commit_operation`). Never add a second of any.
3. Evidence and banks stay on disk. No telemetry, no cloud sync.
4. Format changes are additive.
5. No em dash characters anywhere: not in code, comments, docstrings, commit
   messages, or generated content. Use commas, colons, parentheses, or two
   sentences.

## How to verify

    python3 tests/agent_operation_roundtrip.py
    python3 tests/local_harness_roundtrip.py
    python3 tests/visual_system_roundtrip.py
    python3 itembank.py guard .

Use `python3`, not `python`. Exit code 0 is pass.

**One pre-existing failure, and only one.** `tests/lesson_roundtrip.py` fails on
a golden fixture drift. It is platform-independent, it is not yours, do not
chase it.

`tests/journal_roundtrip.py` is NOT a known failure on this machine. It fails on
Windows in `check_lock_busy`, and it was verified passing on this Mac on
2026-08-22, all six checks including `check_lock_busy`, `concurrency` and
`disk_full`. If it fails for you, you broke it. Stop and say so.

No network is available to your tests. Every endpoint they touch must be a
loopback stub, a closed port, or a socket that never answers. Your own model
traffic goes over the network, but nothing under `tests/` may.

## How to commit, and this part matters

- **Commit after every task, not at the end of the plan.** The single recorded
  failure mode for unattended runs on this project is hitting a turn or time
  limit at the final commit step with all the work uncommitted. Three headless
  runs died that way on 2026-08-11. Treat an uncommitted task as work you have
  already lost.
- One commit per plan task, atomic, conventional prefix plus the plan id:
  `feat(17A-07): ...`, `test(17A-08): ...`, `fix(17A-07): ...`
- Limit every commit to a pathspec you name explicitly:
  `git commit -- <paths>`.
- **Never `git commit -a`, never `git add .`, never `git add -A`.** Other work
  shares this tree. If you sweep it you will commit someone else's half-finished
  state.
- Do not touch `scripts/preflight.py`, `tests/preflight_roundtrip.py`,
  `AGENTS.md`, `scripts/ox_overnight.sh`, or anything under
  `.planning/phases/14A/` or `.planning/phases/14C/`.
- Do not push. Leave that to a human.

## Write the summary as you go, not at the end

Create `<PLAN_ID>-SUMMARY.md` after the FIRST task, with that task's result in
it, and commit it. Append to it after each later task. A summary written only
at the end is a summary that does not exist when the run is cut off.

## When you are stuck

Write what you tried and what blocked you into the summary file, commit that
file alone, and stop. Do not loop. Do not redesign the plan. Do not widen the
scope to something you find easier.

---

## What differs from the 2026-08-21 DeepSeek prompt

1. Path is the Mac clone, not `C:\Users\wayba\Downloads\CTF\itembank`.
2. `python3`, not `python`.
3. `journal_roundtrip` is no longer listed as an expected failure. It was
   verified passing on macOS on 2026-08-22, which also closes one of the two
   open questions in `HANDOFF-MAC-2026-08-21.md`: file locking is now verified
   on a second platform.
4. Commit-after-every-task and write-the-summary-early are promoted to their
   own sections, because the failure they prevent is the one that actually
   happened three times.
5. Covers 17A-08 as well, through `<PLAN_ID>` substitution by the launcher.
6. The model is a hosted frontier model rather than a local one, so the
   "do not hand it design questions" caution is relaxed. The plans are still
   finished plans and it should still execute rather than redesign.
