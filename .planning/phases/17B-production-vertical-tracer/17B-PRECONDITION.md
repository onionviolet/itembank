# 17B precondition check

## Result

**Run 2026-09-01: HALT. Phase 17B may not proceed.** Check 2 (plan-summary
pairing) halted with the exact artifact named:

```
HALT 17B-01: plan without summary: .planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md
```

Per 17B-CONTEXT D-01 and the 16C-01 precedent, this halt is the correct
outcome, not an error in the check. Wave 1 stops here: the fixture course
(Task 2) and the gate scaffold (Task 3) were not created. No file outside
this record was written.

## Why this check exists

17B is the milestone's exit proof and builds no new subsystem; every
capability it exercises must already be frozen by 14A through 17A, with the
Phase 13.9 walking skeleton walked. 17B-CONTEXT D-01 requires execution to
halt by exact artifact name unless 14A, 14B, 15A, 15B, 16A, 16B, 16C, 17A,
and 13.9 are all recorded complete on disk. Handing the plan set to an
executor early is safe; the executor correctly refuses, and this record is
that refusal.

## What was checked

Every command was run from the repository root with `python3` substituted
for `python`; see Deviations found, item 1. Command text is otherwise
verbatim from 17B-01-PLAN.md Task 1.

| Step | Check | Result |
|---|---|---|
| 1 | Eleven named artifacts exist: `14A-FREEZE.md`, `14B-FREEZE.md`, `15A-FREEZE.md`, `15B-FREEZE.md`, `16A-FREEZE.md`, `16B-FREEZE.md`, `16C-FREEZE.md`, `17A-FREEZE.md`, and the three 13.9 walking-skeleton summaries `13.9-01-SUMMARY.md`, `13.9-02-SUMMARY.md`, `13.9-03-SUMMARY.md` | ok, `precondition artifacts present`, exit 0 |
| 2 | Every `*-PLAN.md` in the seven executed phase directories (14A, 14B, 15A, 15B, 16A, 16B, 16C) sits beside a matching `*-SUMMARY.md` | **HALT**, stderr `HALT 17B-01: plan without summary: .planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md`, exit 1 |
| 3 | `17A-FREEZE.md` records a freeze, not a withholding (`## Frozen at` present, `## Freeze withheld` absent) | ok, `17A freeze confirmed`, exit 0 (run for the record after the check 2 halt; the halt stands) |

## The halt, diagnosed but not repaired

The check named `14B-04-PLAN.md` first; a directory listing shows the same
gap for `14B-05-PLAN.md`. Both plans appear to have been executed
(`14B-06-SUMMARY.md` line 35 attributes commit `5568138` to "plan 14B-04",
and `14B-FREEZE.md` records the phase frozen on 2026-08-27 with all gate
legs green), but neither plan's SUMMARY was ever written to disk.
`.planning/STATE.md` (the "Why the wave stopped where it did" passage)
records that 14B-04, 14B-05, and 14B-06 each carried a blocking human
checkpoint, which is consistent with those summaries being owed from a
checkpointed continuation that did not record them.

This is a missing execution record in Phase 14B, owned by Phase 14B, not a
17B defect and not something this plan may repair: writing another phase's
summaries is outside 17B-01's file list and outside D-06's single-file
in-phase fix bound (D-06 covers failed gate checks inside a running tracer,
and the tracer has not started). The next safe action is for the
orchestrator or a 14B-scoped session to either write the two owed summaries
from the recorded evidence (14B-06-SUMMARY.md, 14B-FREEZE.md,
14B-TRACER-REPORT.md, and the commit history) or record why they are
deliberately absent, then rerun this precondition.

## Deviations found

1. **`python` is not on PATH on this machine; every command ran with
   `python3`.** The 16C precondition run (2026-08-29) recorded the same
   substitution. Command text was otherwise unmodified.
2. **Check 3 was run after the halt, for the record.** The plan sequences
   the three checks and the halt fired at check 2. Check 3 mutates nothing
   and its result (`17A freeze confirmed`) is recorded above so the rerun
   after the 14B repair knows checks 1 and 3 were green on 2026-09-01. The
   halt is not weakened by this: the wave stopped, and Tasks 2 and 3 did
   not run.
