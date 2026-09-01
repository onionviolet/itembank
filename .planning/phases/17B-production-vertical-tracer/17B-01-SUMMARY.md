# 17B-01 summary: precondition halt, twice

**Executed 2026-09-01, two runs. Outcome of both: HALT at Task 1, check
2.** Per 17B-CONTEXT D-01 and the plan's own instruction ("The halt is the
correct outcome; do not stub, skip, or proceed with a reduced check set"),
the halt is this plan's correct result, not a failure of execution. Tasks
2 and 3 did not run in either attempt.

## Second run, after the 14B repair

Following the first run's recorded next safe action, the two owed 14B
summaries were reconstructed retrospectively from the commit record
(commits `5568138`, `a7d5974`, `0912f5c`, `fbd7283`, `4c9d2e8`,
`14B-DECISIONS.md`, `14B-FREEZE.md`, `14B-TRACER-REPORT.md`, STATE.md) and
committed as `e9da36e`. The three checks were then rerun verbatim
(`python3` for `python`, the recorded deviation). Results:

- Check 1: `precondition artifacts present`, exit 0.
- Check 2, the halt, verbatim:

```
HALT 17B-01: plan without summary: .planning/phases/15A-director-treatment-policy/15A-01-PLAN.md
```

- Check 3: `17A freeze confirmed`, exit 0.

Behind the first-named miss stand sixteen plans without summaries: all six
15A plans, all seven 15B plans, 16A-01, 16A-10, and 16C-09. 15A and 15B
recorded execution phase-wide (REVIEW, TRACER-REPORT, FREEZE) and never
wrote per-plan summaries. Bulk-reconstructing sixteen execution records
across four frozen phases to force the check green is the reduced-check-set
outcome the plan forbids, so the halt stands and the choice between
retrospective reconstruction and an amended pairing rule goes to the
orchestrator or Weibao; both options are written out in
`17B-PRECONDITION.md` under "Result, second run".

## First run: precondition result

The exact halt, verbatim from check 2 (plan-summary pairing), run from the
repository root with `python3` substituted for `python` because `python` is
not on PATH (the 16C precedent deviation):

```
HALT 17B-01: plan without summary: .planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md
```

Check 1 printed `precondition artifacts present`, exit 0. Check 3, run for
the record after the halt, printed `17A freeze confirmed`, exit 0. Full
detail, diagnosis, and the next safe action are in `17B-PRECONDITION.md`.

The gap is genuine: `14B-04-PLAN.md` and `14B-05-PLAN.md` both sit beside
no SUMMARY in `.planning/phases/14B-graph-course-package-prototype/`, even
though `14B-FREEZE.md` records the phase frozen and `14B-06-SUMMARY.md`
attributes commit `5568138` to plan 14B-04. The owed record belongs to
Phase 14B; repairing it is outside this plan's file list and outside D-06's
bound.

## Fixture file list with word counts

None. `course_fixture_17b/` was not created; Task 2 did not run.

## Guard and em dash outputs

Not run; they are Task 2 and Task 3 verifies and those tasks did not run.
An em dash check over the two files this plan did write
(`17B-PRECONDITION.md`, this summary) printed `no em dash`, exit 0.

## Gate table row count

None. `17B-GATES.md` was not created; Task 3 did not run.

## Next safe action

Superseded for the 14B half: the owed `14B-04-SUMMARY.md` and
`14B-05-SUMMARY.md` were written and committed (`e9da36e`) before the
second run. The standing next safe action after the second run's halt:
either sixteen retrospective summaries are written by sessions scoped to
their owning phases (15A, 15B, 16A, 16C), or the pairing rule in
17B-01-PLAN.md is amended by its owner to accept a phase-wide execution
record where per-plan summaries were never that phase's record shape.
Then this plan is rerun from Task 1.
