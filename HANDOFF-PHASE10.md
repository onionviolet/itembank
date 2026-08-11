# Continue Phase 10 — handoff prompt (for a fresh chat)

Paste the whole block below into a new chat:

---

Continue executing GSD Phase 10 in this repo (`C:\Users\wayba\Downloads\CTF\itembank`).
You are taking over from a previous chat. Read this entire message first.

## Where the work stands

- **Plan 10-01 is COMPLETE and committed** on branch `phase10` at commit
  `9996c3e` (`feat(10-01): retention derivation layer ...`), plus commit
  `49a4cde` (`docs: one atomic commit per plan is a standing repo rule`).
  Both are on the `phase10` branch, in a git worktree at
  `C:\Users\wayba\Downloads\CTF\itembank\.phase10-wt`.
- Delivered by 10-01: `retention.py` (immutable snapshot, six states, week
  series, bounded weights, FSRS scheduler strategy + WaniKani stages +
  utility ordering, return rate), `evidence.capture_events`, the `itembank
  trends` CLI (JSON + plain text), the bounded `retention` settings group,
  the additive `retention_report` variant in `schemas/report.schema.json`,
  and `tests/retention_roundtrip.py` (Wave 0 harness, green).
- Remaining plans to execute, IN ORDER (each depends on the previous):
  10-02 lesson-completion seam → 10-03 selector retention context →
  10-04 daily-cap enforcement + override → 10-05 Today/report UI →
  10-06 phase UAT + full regression.
  Plans are at `.planning/phases/10-retention-pacing-trends/10-0X-PLAN.md`.

## Mandatory rules (non-negotiable)

1. **One atomic commit per plan.** Finish a plan, run its verification,
   then commit exactly once with ONLY that plan's files (stage by name, never
   `git add -A`). Commit shape: `feat(10-0X): ...` / `test(10-0X): ...`.
   This rule is now in AGENTS.md; follow it.
2. **Run `python tests/retention_roundtrip.py` after every task** within a
   plan, and the full suite before verification.
3. **Wipe hazard:** a nested worktree under the main checkout has been
   removed twice by a concurrent process, destroying uncommitted work. Keep
   the worktree at `.phase10-wt` (or recreate: `git worktree add
   .phase10-wt phase10`), and COMMIT AS SOON AS A PLAN IS GREEN — do not
   carry uncommitted work across turns. If the worktree vanishes, recreate
   it and `git checkout phase10`; committed work survives.
4. **One parser, one scorer, one evidence writer.** `retention.py` is a pure
   projection; new events go through `evidence.append_event` only; the
   selector stays Phase 7's `selection.select` (Plan 10-03 adds an optional
   keyword-only `retention_context`). Never create a second evidence store,
   cache-as-authority, selector, or scheduler.
5. **Hard constraints from the user:** "due" is derived from the evidence
   log — never a second store; keep the one-parser/one-scorer boundary. If
   Phase 6 (06-02) or another phase is still open in another chat,
   coordinate before editing `surfaces/cli.py` — check `git log --oneline
   main -5` and `git worktree list` first; `main` may have moved.
6. **Defer the human-verify pass** (Plan 10-06 Task 3: 1280/768/375px,
   keyboard/focus, copy, offline/public-boundary) to the very end alongside
   any other pending human gates. Do not block automated plans on it; flag
   it in the final handoff.
7. Write `10-0X-SUMMARY.md` per plan, then `10-VERIFICATION.md` and update
   the ROADMAP Phase 10 checkbox/status table after 10-06.
8. When all six plans are done and green, merge `phase10` back into `main`
   (`main` will have moved — re-merge latest main into `phase10` first,
   resolve conflicts, then merge `phase10` into `main`).

## Parallelism guidance

Plans 10-02 → 10-06 are a strict dependency chain (10-03 needs 10-02, etc.),
so execute sequentially at the plan level. WITHIN a plan you may parallelize
independent tasks with subagents (e.g. writing a test harness while another
agent drafts the schema change) only if they touch disjoint files — the
plans' `files_modified` lists show overlap, so prefer sequential task
execution inside a plan unless you can prove disjoint writes. Never run two
writers on the same file concurrently.

## Environment

- Work in the worktree: `cd /mnt/c/Users/wayba/Downloads/CTF/itembank/.phase10-wt`
  (bash) — file-edit tools must use `C:/Users/wayba/Downloads/CTF/itembank/
  .phase10-wt/...` absolute paths.
- Python stdlib only; tests are `tests/*_roundtrip.py` standalone scripts.
- Scratch/probes go to `/home/sigma/scratch10/`, never the repo.

## First actions on start

1. `git -C .phase10-wt log --oneline -3` and `git worktree list` — confirm
   the branch and worktree still exist; recreate if wiped.
2. `python tests/retention_roundtrip.py` in the worktree — confirm 10-01's
   suite is green on the committed state.
3. Read `10-02-PLAN.md` and its context refs, then execute it, committing
   atomically when its verification passes.
