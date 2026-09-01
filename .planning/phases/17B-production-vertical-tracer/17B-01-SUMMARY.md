# 17B-01 summary: two halts, a ruling, and a completed run

**Executed 2026-09-01, three precondition runs. Final outcome: all three
checks GREEN, Tasks 2 and 3 executed and verified.** The first two runs
halted at Task 1 check 2, each halt the correct outcome of the check as
it then stood (17B-CONTEXT D-01). The coordinator's hybrid ruling under
Weibao's standing 2026-09-01 delegation closed the gap two ways: 15A and
15B (phase-wide record shape) were exempted by a dated amendment to
17B-01-PLAN.md Task 1 step 2 whose amended command checks their
phase-wide records instead, and the three genuine per-plan gaps got
retrospective summaries (`16A-01-SUMMARY.md`, `16A-10-SUMMARY.md`,
`16C-09-SUMMARY.md`, commit `020de23`), following the 14B pair
(`e9da36e`).

## Third run: the precondition passes

Verbatim results, run from the repository root with `python3` for
`python` (the recorded deviation):

- Check 1: `precondition artifacts present`, exit 0.
- Check 2 (amended): `plan-summary pairing complete`, exit 0.
- Check 3: `17A freeze confirmed`, exit 0.

The amended check 2 command is recorded verbatim in
`17B-PRECONDITION.md` under "Result, third run".

## Task 2: the fixture course

`course_fixture_17b/` created at the repository root, entirely synthetic
(Aldrasse fen ecology, invented for the tracer), outside `fixtures/`
deliberately. Files with word counts (`wc -w`):

| file | words |
|---|---|
| `course_fixture_17b/README.md` | 173 |
| `course_fixture_17b/scope.md` | 338 |
| `course_fixture_17b/objectives.md` | 245 |
| `course_fixture_17b/sources/fen_hydrology_field_notes.md` | 625 |
| `course_fixture_17b/sources/lantern_moss_survey.md` | 567 |

Both sources exceed the 400-word production-depth floor, carry headed
sections whose heading slugs are the stable locator anchors, and the
seven objectives in `objectives.md` each cite one source section with a
`[SRC: <source file>#<anchor>]` locator. The scope tree follows D-03:
open field "Fenland Systems" (never complete, scope version
FS-2026-09-01.1 stated on every claim), bounded course "Aldrasse Fen
Ecology 101" with named completion predicate `afe101-complete-v1`,
containing "Unit 3: Peat Hydrology and the Lantern Moss Cycle".

Verify outputs, verbatim: `python3 itembank.py guard .` printed
`0 offending files`, exit 0; the em dash sweep over
`course_fixture_17b/**/*.md` printed `no em dash`, exit 0.

## Task 3: the gate scaffold

`17B-GATES.md` written with the five columns exactly (gate, concrete
check, proof command or fixture, evidence pointer, state), one row per
gate G1 through G11 with the concrete check transcribed from the ROADMAP
details block and proof, evidence, and state all `pending`, plus the
mandatory-human-checkpoint note verbatim beneath the table.

Verify outputs, verbatim: `grep -c "^| G"` printed `11`; the em dash
check printed `no em dash`.

## History of the two halts

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

Closed. Both halts' next safe actions were carried out on 2026-09-01
(the 14B pair at `e9da36e`, the hybrid ruling at `020de23` plus the plan
amendment), the precondition passed on the third run, and Tasks 2 and 3
completed. The next action belongs to wave 2 (17B-02).
