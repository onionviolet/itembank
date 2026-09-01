# 17B precondition check

## Result, second run

**Run 2026-09-01, after the 14B repair: HALT again. Phase 17B may not
proceed.** The two owed 14B summaries were reconstructed retrospectively
and committed (`e9da36e`, `14B-04-SUMMARY.md` and `14B-05-SUMMARY.md`),
and the three checks were rerun verbatim (with `python3`). Checks 1 and 3
are green. Check 2 halted with the next missing artifact named:

```
HALT 17B-01: plan without summary: .planning/phases/15A-director-treatment-policy/15A-01-PLAN.md
```

The full enumeration behind that first-named miss, from one sweep over the
seven phase directories, is sixteen plans without summaries:

- `15A-01-PLAN.md` through `15A-06-PLAN.md` (all six 15A plans)
- `15B-01-PLAN.md` through `15B-07-PLAN.md` (all seven 15B plans)
- `16A-01-PLAN.md` and `16A-10-PLAN.md`
- `16C-09-PLAN.md`

The shape of the gap differs from 14B's. Phases 15A and 15B recorded their
execution phase-wide (`15A-REVIEW.md`, `15A-TRACER-REPORT.md`,
`15A-FREEZE.md`, and the 15B equivalents plus `COVERAGE.md`) and wrote no
per-plan summary at all; 16A and 16C wrote per-plan summaries for all but
two and one plans respectively. Whether the phase-wide records satisfy the
pairing rule's intent, or sixteen retrospective summaries are owed the way
14B's two were, is a call for the orchestrator or Weibao, not for this
executor: reconstructing sixteen execution records across four frozen
phases is well past the single-artifact repair the first run's next safe
action named, and forcing the check green by bulk reconstruction is the
reduced-check-set outcome the plan forbids by name.

**Next safe action.** Either (a) the sixteen owed summaries are written
retrospectively by sessions scoped to their owning phases, from the commit
record, as the 14B pair was; or (b) the pairing rule is amended by whoever
owns 17B-01-PLAN.md to accept a phase-wide execution record (REVIEW plus
TRACER-REPORT plus FREEZE) where per-plan summaries were never the phase's
record shape, with that amendment recorded, not silently applied. Then
this precondition is rerun.

## Result, first run

**Run 2026-09-01 (first run of the day): HALT. Phase 17B may not
proceed.** Check 2 (plan-summary pairing) halted with the exact artifact
named:

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
