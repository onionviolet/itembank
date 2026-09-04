# Prompt: finish the sitting fallout, one plan per run

Written 2026-08-25. Pass with `IB_PROMPT` rather than adding a case to
`prompt_for()`, because the plan ids here span two directories and the
executor is forbidden from touching `scripts/` anyway. See
`.planning/OX-RUNBOOK-finish-the-sitting-2026-08-25.md` for the night order and
the acceptance ritual.

Valid plan ids for this prompt: `13.9-04`, `13.9-05`, `260817-q7d`.

---

You are executing one finished plan on `itembank`, a Python project at
`/Users/weiwei/Documents/Dev/itembank`, on macOS, branch `main`.

## Read exactly two files first, and no others

1. `.planning/EXEC-CONTEXT.md`
2. Your plan:
   - `13.9-04` and `13.9-05`:
     `.planning/phases/13.9-walking-skeleton/<PLAN_ID>-PLAN.md`
   - `260817-q7d`:
     `.planning/quick/260817-q7d-fix-135-defects-d1-d2/260817-q7d-PLAN.md`

Do NOT read `ROADMAP.md`, `REQUIREMENTS.md`, `UI-SPEC.md`,
`AGENT-WORKFLOW.md`, `SOURCE-TO-COURSE.md`, or `PLANNING-DIRECTIVES.md`. That
stack is about 122,000 tokens and your plan cites what it needs.

## What produced these plans

A real learner sat a real ten item EMT bank end to end on 2026-08-24 and the
sitting produced a queue of defects that outlived it. Three are fixed
(`f275aac`, `080bffc`, `2c4ae0a`) and one lint rule landed (`2c34a65`). Your
plan is one of the remainder. The defects are small and they are real: they
were observed by a person, not inferred from a test.

## Per-plan notes, read only the one that applies

**13.9-04, the defect sweep.** Five independent defects, one task each, in the
plan's order. They do not depend on each other. If you cannot finish one, commit
the ones you did finish, write what blocked the rest, and stop. Do not skip
ahead to an easier one and leave a hole in the middle.

**13.9-05, draft autosave.** The decision is already made and recorded in
`080bffc`: the draft is presentation state. It reaches the rendered controls
and nothing else. **It must never become a second source of truth**, it is
never read back as an answer, and no answer is recorded until a submit
succeeds. The graded sitting is a script-free form POST by design, so autosave
is the one piece here that needs client storage, and it must degrade to exactly
today's behaviour when storage is unavailable or scripting is off.

**260817-q7d, the 13.5 defects D1 and D2.** `Item 1 of 0` and a position that
never advances. Both are visible on the served page. A passing test is not
evidence that these are fixed; the rendered counter is.

## Act first

Your first tool call after reading must be a **file write**. Running
`git status` does not count.

## Rules you cannot break

1. The runtime owns correctness, session state, evidence, and keyed assessment
   disclosure. No model settles a score or decides key disclosure.
2. One parser (`model.py`), one scorer (`runtime.py`), one evidence store, one
   writer (`journal.commit_operation`). Never a second of any.
3. Evidence and banks stay on disk. No telemetry, no cloud sync.
4. Format changes are additive.
5. No em dash characters anywhere, commit messages included.
6. Presentation state never becomes truth and never grants authorization.

## How to verify

Use `python3`, not `python`. Run what your plan's verify block names, plus:

    python3 itembank.py guard .

Run the suite with `ANKI_CONNECT_URL=http://127.0.0.1:59999` exported.
`day_roundtrip` and `retention_ui_roundtrip` assert the Anki-unavailable copy
and Anki Desktop runs on this Mac, so without that export you will chase a
failure that is not yours. **Every other failure is yours.** Do not wave one
through as pre-existing.

**Your change is user facing, so drive the real page.** On 2026-08-24 a suite
of seventy green tests agreed with a broken served page all night. Start the
daemon, sit an item, and look at what you changed before you believe a green
suite. Say in the commit message what you saw.

**If a test fails after your fix, decide which of the two is wrong before you
edit either.** `agent_roundtrip` once asserted `pending_manual >= 1` after a
mark, which encoded the exact bug it was later used to catch. A test can pin a
defect.

## How to commit

- **Commit after every task, not at the end.** Three unattended runs have died
  at a final commit step with the work uncommitted.
- Conventional prefix plus the plan id: `fix(13.9-04): ...`.
- **Use the plan id in the message.** Tooling and humans both count plans this
  way, and an off-convention message is how 17A-05 came to look built when it
  was not.
- Say what was wrong, not what you touched.
- Pathspec every commit: `git commit -- <paths>`. Never `git add .`, `-A`, or
  `git commit -a`. Another session has shared this tree's index before and the
  loser's commit message was silently discarded.
- Do not touch `scripts/`, `AGENTS.md`, `.planning/STATE.md`,
  `.planning/READINESS-AUDIT-14A.md`, or any `13.9-CALIBRATION.md`. The
  roll-up and the readiness boxes belong to the human who accepts your work.
- Do not push.

## Summary obligations

`PLANNING-DIRECTIVES.md` B1 makes a summary exceptional: write one only if the
plan was left incomplete, or if a measured fact contradicts the plan. The
commit messages are otherwise the record.

## When you are stuck

Write what you tried and what blocked you into `<PLAN_ID>-SUMMARY.md` beside
your plan, commit that file alone, and stop. Do not loop, do not redesign, and
do not widen scope to something easier.
