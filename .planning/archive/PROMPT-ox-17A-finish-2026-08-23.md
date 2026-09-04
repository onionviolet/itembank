# Prompt: finish 17A, plans 02 then 05 then 03

Written 2026-08-23 after an artifact-level audit found 17A-02 half done and
17A-05 never built. See `.planning/STATE.md`, entry 2026-08-23. Run through
`scripts/ox_queue.sh` with `IB_FORCE=1`, because 17A-02 already carries a
planning-convention commit and the skip guard would otherwise skip it.

Order matters and is not negotiable: **02, then 05, then 03.** Both 05 and 03
depend on 02's code. Their `files_modified` sets do not intersect each other, so
if 02 lands and you want them in parallel later, that is safe in separate
worktrees. In one tree, run them in sequence.

---

You are executing one finished plan on `itembank`, a Python project at
`/Users/weiwei/Documents/Dev/itembank`, on macOS, branch `main`.

## Read exactly two files first, and no others

1. `.planning/EXEC-CONTEXT.md`
2. `.planning/phases/17A-visual-system-component-foundation/<PLAN_ID>-PLAN.md`

Then read `.planning/STATE.md`'s **first section only**, the 2026-08-23 entry,
because it records what is really built and what is not. Do NOT read
`ROADMAP.md`, `REQUIREMENTS.md`, `UI-SPEC.md`, `AGENT-WORKFLOW.md`,
`SOURCE-TO-COURSE.md`, or `PLANNING-DIRECTIVES.md`. That stack is about 122,000
tokens and the plan cites what it needs.

If your plan is 02, also read
`.planning/phases/17A-visual-system-component-foundation/17A-DIRECTION.md`. It
is short and it closes your Task 1.

## Per-plan notes, read only the one that applies

**17A-02.** The plan is `autonomous: false` and its Task 1 is a decision
checkpoint. **That checkpoint is already closed.** Weibao chose on 2026-08-20
and `17A-DIRECTION.md` records it: look `structured-studio`, navigation
`sidebar`, and the accent named there. Do not ask him again and do not stop.
**Execute Task 2 only.** Task 1 produces no new artifact.

Task 2 is fully specified: add the five type tokens, add the three density
aliases with comfortable and compact bounds, promote only the selected overlay,
refactor `surfaces/day.py` to call `surface_shell` from `surfaces/presentation.py`
and remove the duplicated shell ownership without changing route content or day
behaviour, verify `--edge` already exists rather than re-adding it, and add the
served-byte tests the plan lists.

**17A-05 and 17A-03.** Straightforward execution, every task in order. If 02's
code is not present when you start, stop and say so rather than working around
it: `surface_shell` should appear in `surfaces/day.py` and `surfaces/theme.py`
should carry density tokens. That check takes one grep and it is the difference
between building on the plan and building on a guess.

## Act first

Your first tool call after reading must be a **file write**. Running `git status`
does not count.

## Rules you cannot break

1. The runtime owns correctness, session state, evidence, and keyed assessment
   disclosure. No model settles a score or decides key disclosure.
2. One parser (`model.py`), one scorer (`runtime.py`), one evidence store, one
   writer (`journal.commit_operation`). Never a second of any.
3. Evidence and banks stay on disk. No telemetry, no cloud sync.
4. Format changes are additive.
5. No em dash characters anywhere, commit messages included.

## How to verify

Use `python3`, not `python`. Run what your plan's verify block names, plus:

    python3 itembank.py guard .

**There are no known failing tests on this machine.** `lesson_roundtrip` was
recorded as a standing failure in older handoffs and it passes here, verified
2026-08-23. If any test fails, it is yours. Do not wave one through as
pre-existing.

## How to commit

- **Commit after every task, not at the end.** Three unattended runs died at a
  final commit step with the work uncommitted.
- Conventional prefix plus the plan id: `feat(17A-02): ...`.
- **Use the plan id in the message.** Tooling and humans both count plans this
  way, and an off-convention message is how 17A-05 came to look built when it
  was not.
- Pathspec every commit: `git commit -- <paths>`. Never `git add .`, `-A`, or
  `git commit -a`.
- Do not touch `scripts/`, `AGENTS.md`, `.planning/STATE.md`, or anything under
  `.planning/phases/13.9-walking-skeleton/` or `14A/` or `14C/`.
- Do not push.

## Summary obligations

`PLANNING-DIRECTIVES.md` B1 makes a summary exceptional: write one only if the
plan was left incomplete, or if a measured fact contradicts the plan. 17A-02's
own plan additionally asks for a token table and day-parity evidence, so for
that plan write `17A-02-SUMMARY.md`. For 05 and 03 the commit messages are the
record unless something contradicted the plan.

## When you are stuck

Write what you tried and what blocked you into
`<PLAN_ID>-SUMMARY.md`, commit that file alone, and stop. Do not loop, redesign,
or widen scope to something easier.
