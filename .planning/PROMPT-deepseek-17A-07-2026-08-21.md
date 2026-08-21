# Prompt: hand 17A-07 to DeepSeek through dsh

Paste everything below the line into the `dsh` console as the first message.
It is self-contained.

Written 2026-08-21. Scoped deliberately narrow: this is execution work with a
finished plan behind it, which is what a local model is good at. Do not hand it
design questions.

---

You are executing one finished plan on `itembank`, a Python project at
`C:\Users\wayba\Downloads\CTF\itembank`. Work on branch `main`.

## Read exactly two files first, and no others

1. `.planning/EXEC-CONTEXT.md`
2. `.planning/phases/17A-visual-system-component-foundation/17A-07-PLAN.md`

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

Execute `17A-07-PLAN.md`, all three tasks, in order. It is `autonomous: true`,
so there is no checkpoint to wait for.

In one sentence: the Agent page has skill buttons that run nothing, and
`journal.commit_operation` is a working writer with an undo, and your job is to
join them so one skill run produces exactly one undoable change.

Write the test before the code in every task. That is not a style preference:
two bugs in the previous plan were caught that way, and two guards were proven
by deleting the fix and watching the suite fail. Do the same here.

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

    python tests/agent_operation_roundtrip.py
    python tests/local_harness_roundtrip.py
    python tests/visual_system_roundtrip.py
    python itembank.py guard .

Exit code 0 is pass. Two failures are pre-existing and are NOT yours:
`tests/journal_roundtrip.py` fails in `check_lock_busy` with a Windows
`msvcrt` unlock error, and `tests/lesson_roundtrip.py` fails on a golden
fixture drift. Do not chase either one.

No network is available to your tests. Every endpoint they touch must be a
loopback stub, a closed port, or a socket that never answers.

## How to commit, and this part matters

**Two other agents are writing to this same working tree right now.** A Codex
track commits into it, and a graded sitting is running out of it.

- One commit per plan task, atomic, conventional prefix plus the plan id:
  `feat(17A-07): ...`, `test(17A-07): ...`, `fix(17A-07): ...`
- Limit every commit to a pathspec you name explicitly:
  `git commit -- <paths>`.
- **Never `git commit -a`, never `git add .`, never `git add -A`.** If you
  sweep the tree you will commit another agent's half-finished work.
- Do not touch `scripts/preflight.py`, `tests/preflight_roundtrip.py`,
  `AGENTS.md`, or anything under `.planning/phases/14A/` or
  `.planning/phases/14C/`. Those belong to the other track.
- Do not push. Leave that to a human.

## When you are stuck

Write what you tried and what blocked you into
`.planning/phases/17A-visual-system-component-foundation/17A-07-SUMMARY.md`,
commit that file alone, and stop. Do not loop. Do not redesign the plan. Do not
widen the scope to something you find easier.
