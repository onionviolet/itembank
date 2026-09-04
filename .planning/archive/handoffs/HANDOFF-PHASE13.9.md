# Handoff - Phase 13.9 (Walking Skeleton) ready for execution

- **Created:** 2026-08-15 (Claude, planning side of the dual-runtime split)
- **Handing off to:** Codex (DeepSeek executor) per PLANNING-DIRECTIVES.md: Claude plans, Codex executes, sequentially. GSD state is shared on disk; this note is the "stop and tell them", not an export.
- **Status:** Phase 13.9 has 3 plans written, 0 executed. Nothing else is queued ahead of it.

## Objective

Walk one thin real slice before any 14B-or-later freeze closes: one real source
from one live fall course, discovered read-only, bound to at least three cited
objectives, one treatment decision per objective, authored minimally, and sat by
Weibao through the shipped serve/teach/evidence loop. Defined by
`READINESS-AUDIT-14A.md` section A9, which governs on any divergence, and the
Phase 13.9 details block in `ROADMAP.md`.

## Authoritative files to read first

1. `.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md` (then 02, 03; sequential waves)
2. `.planning/READINESS-AUDIT-14A.md` section A9
3. `.planning/ROADMAP.md` Phase 13.9 details block
4. `.planning/SOURCE-TO-COURSE.md` (north star and course-building loop)
5. `.planning/PLANNING-DIRECTIVES.md` (executor bar, sequential rule)

## Critical execution facts

- **13.9-01 is `autonomous: false` and opens with a `checkpoint:decision`.**
  Task 1 asks Weibao three questions (which course, which source, which course
  root) and records the answers verbatim in `13.9-DECISIONS.md`. Do not proceed
  past the checkpoint without his answers. Recommended default in the plan: EMT.
- **Read-only discovery.** Inventory sources by path, format, size, SHA-256.
  Nothing in the source root is moved, renamed, or edited.
- **No real course content enters this repository.** Pointers, counts, and
  hashes only; `itembank guard` enforces this in CI.
- **course.md is a draft stub no tool parses.** Its header must say so; Phase
  14B owns the real schema. Do not build a parser for it.
- **No second parser, scorer, or evidence store.** Shipped surfaces only.
- **Gate this phase satisfies:** no 14B-or-later freeze closes before the
  skeleton is walked (ROADMAP revision 2026-08-14; A9).

## Current repo state (verified 2026-08-15)

- Branch `main`, clean at handoff. Recent commits `9aaeeae` and `6d35b58`
  corrected the stale ROADMAP progress table and STATE.md status line: 13.5 is
  9/9 executed with verification `human_needed` (see `13.5-VERIFICATION.md`),
  not 3/8 in flight. 13.9 may run now; it was scoped to run beside or after
  13.5 waves 3+, which are done.
- STATE.md frontmatter `progress:` counters (112/160) were not recomputed and
  may be stale; do not treat them as authoritative.
- Commit discipline: `query commit` without `--files` sweeps every dirty
  tracked file. Use pathspec-limited `git commit -- <paths>` when anything else
  shares the tree.
- Prose rule: no em dash characters in repository-authored prose.

## Verification required

- Per-plan must_haves in each PLAN.md frontmatter; write SUMMARY.md per plan.
- Phase closes only when Weibao has actually sat the slice through the shipped
  serve/teach/evidence loop and evidence is recorded. Simulated is not
  acceptable; ugly is.

## Exact next action

Open `.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md` and run Task 1's
checkpoint: put the three course/source/root questions to Weibao and record his
verbatim answers in `13.9-DECISIONS.md` before any inventory work.
