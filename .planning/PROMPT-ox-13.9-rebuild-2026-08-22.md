# Prompt: rebuild the 13.9 walking-skeleton course on the Mac

Written 2026-08-22, after the Windows machine became permanently unreachable and
the original course root went with it. Run through `scripts/ox_queue.sh`, which
waits for any in-flight run to finish first.

---

You are executing one finished plan on `itembank`, a Python project at
`/Users/weiwei/Documents/Dev/itembank`. Work on branch `main`, on macOS.

## Read exactly two files first, and no others

1. `.planning/EXEC-CONTEXT.md`
2. `.planning/phases/13.9-walking-skeleton/<PLAN_ID>-PLAN.md`

Then read `.planning/phases/13.9-walking-skeleton/13.9-DECISIONS.md` in full,
because it carries the answers to this plan's checkpoint and the reason the
paths changed. Nothing else. Do NOT read `ROADMAP.md`, `REQUIREMENTS.md`,
`STATE.md`, `UI-SPEC.md`, or `PLANNING-DIRECTIVES.md`.

## The checkpoint is already answered. Do not stop for it

`13.9-01-PLAN.md` is `autonomous: false` and opens with a decision checkpoint
asking three questions. **All three are answered on record and you must not put
them to Weibao again.** From `13.9-DECISIONS.md`:

- **Course:** EMT.
- **Source:** the EMT chapter 1 file in the planning vault,
  `/Users/weiwei/Documents/Claude/Projects/Weibao's Workspace/plans/02_Skills_Learning/EMT/Chapters/ch01_ems_systems.md`.
  This is the same source in substance as the Windows path in the 2026-08-16
  entry; only its location moved.
- **Course root:** `/Users/weiwei/Documents/itembank-courses/emt-unit-1`. It
  already exists as an empty parent and is outside the repository on purpose,
  because `itembank guard` fails CI if real bank content lands here.

The objective-map approval in that plan runs under the 2026-08-16 standing
authority recorded at the top of `13.9-DECISIONS.md`: a reversible draft may
take the most useful comprehensive default, and viable alternatives stay
registered for later choice. Apply it and keep going.

## Act first

Your first tool call after reading those files must be a **file write**, not a
command and not an analysis. Running `git status` does not count.

## The job

Execute `<PLAN_ID>-PLAN.md`, every task, in order.

Plan 01 inventories the source read-only (path, format, size, SHA-256), writes
the `course.md` draft manifest with Sources, Objectives and Log sections, and
maps at least three objectives with `[SRC: source-id locator]` citations and a
treatment decision each, at least one direct-reading and at least one
lesson-plus-practice.

Plan 02 authors the lesson file and the bank.

## Rules you cannot break

1. **The source root is read-only.** It is Weibao's planning vault and a live
   git repository. Inventory it. Do not move, rename, edit, or create anything
   inside it. If you need to record something about it, record it in the course
   root or in `.planning`.
2. **No real course content enters this repository.** Pointers, counts and
   hashes only. `itembank guard .` is the backstop and it wins any argument.
3. **`course.md` is a draft stub no tool parses.** Its header must say so.
   Phase 14B owns the real schema. Do not write a parser for it.
4. **No second parser, scorer or evidence store.** Shipped surfaces only.
5. **Paraphrase, never copy.** No sentence of eight or more consecutive words
   may come from the source. The paraphrase lint enforces this and the source is
   a copyrighted textbook derivative.
6. **No em dash characters anywhere**, including commit messages.

## How to verify

    python3 itembank.py lint /Users/weiwei/Documents/itembank-courses/emt-unit-1/*_bank.md
    python3 itembank.py guard .

Use `python3`. The bank must lint with exit 0 and carry minted `[ID:]` and
`[HASH:]` fingerprints, with every item resolving `[OBJ:]` and `[SRC:]` through
its `## SOURCES` registry.

## How to commit

- **Commit after every task, not at the end.** Three unattended runs on this
  project died at a final commit step with everything uncommitted.
- Conventional prefix plus the plan id: `feat(13.9-01): ...`.
- Pathspec every commit: `git commit -- <paths>`. Never `git add .`, `-A`, or
  `git commit -a`. Another agent is working in this tree.
- The course root is outside the repository and is not committed at all. Only
  `.planning/phases/13.9-walking-skeleton/` files are.
- Do not push.

## What you must not do

Do not sit the quiz. Do not answer any item. Do not simulate a sitting or write
anything into `_attempts/` or `_evidence/`. Task 1 of `13.9-03` is Weibao's and
the whole gate depends on the sitting being real. Your job ends when the bank
lints clean and he has something to sit.

## When you are stuck

Write what you tried and what blocked you into
`.planning/phases/13.9-walking-skeleton/<PLAN_ID>-SUMMARY.md`, commit that file
alone, and stop. Do not loop, do not redesign the plan, do not widen scope.
