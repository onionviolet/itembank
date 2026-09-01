# 14B-04 summary (RETROSPECTIVE)

**This is a retrospective record, written 2026-09-01** to close the
plan-summary pairing gap found by the 17B-01 precondition run
(`.planning/phases/17B-production-vertical-tracer/17B-PRECONDITION.md`).
Plan 14B-04 was executed 2026-08-27; its summary was never written at the
time. Everything below is reconstructed from the commit record (commits
`5568138`, `a7d5974`, and the follow-up fix `0912f5c`), `14B-DECISIONS.md`,
`14B-06-SUMMARY.md`, `14B-TRACER-REPORT.md`, `14B-FREEZE.md`, and the
STATE.md 14B entries. Nothing here is a new claim; where the record is
silent, this file says so plainly.

## The checkpoint and how it was settled

Task 1 was a blocking `checkpoint:decision` gate: where does `migrate`
live and what does a proposal carry. Per the STATE.md 14B record ("Waves 4
to 6 are BLOCKED on four decisions only Weibao can make: D-14B-1's
provisional stand-in plus three blocking checkpoints in plans 14B-04,
14B-05 and 14B-06"), execution stopped after wave 3 until Weibao answered
through the driver packet `.planning/DECISIONS-14B-DRIVER-2026-08-27.md`.
The answer is recorded in `14B-DECISIONS.md` under
`## D-14B-3. migrate is a record type, not a seventh operation`:
**option-a**, decided by Weibao on 2026-08-27. `migrate` joined
`journal.RECORD_TYPES` with the eight-field proposal (`migration_id`,
`kind`, `from`, `to`, `rationale`, `state`, `actor`, `timestamp`),
`journal.OPERATION_TYPES` stayed at exactly six, and `14A-FREEZE.md` was
untouched. No changes to Tasks 2 and 3 were forced; option-a is the path
they were written for.

## What landed

- Commit `5568138` (2026-08-27), Task 2: `journal.RECORD_TYPES` gains
  `"migrate"`; `graph.py` gains `MIGRATION_KINDS` (five),
  `MIGRATION_STATES` (three), `EVIDENCE_CLAIM_STATES` (two),
  `migration_proposal`, `add_migration`, and `set_migration_state`;
  `course.py` gains `record_migration` writing through the frozen 14A
  compare-and-swap path with `operation="migrate"`. Diffstat: `course.py`
  +22, `graph.py` +94, `journal.py` +13/-6, `tests/graph_roundtrip.py`
  +132.
- Commit `a7d5974` (2026-08-27), Task 3: `split_objective`,
  `rename_objective`, `merge_objectives`, `objective_evidence_state`, and
  `fixtures/corpus_14b.seed_objective_evidence`. Diffstat:
  `fixtures/corpus_14b.py` +37, `graph.py` +91,
  `tests/graph_roundtrip.py` +107.

## The journal.py diff, and the deviation on the one-line bound

The plan required exactly one changed line in `journal.py`. Commit
`5568138`'s own message records the deviation: `git diff --stat journal.py`
reported 13 insertions and 6 deletions, but exactly one line of CODE
changed (the `RECORD_TYPES` tuple). The rest was the comment block directly
above it, which had become false at five added record types ("the four this
plan's own machinery writes"). The recorded reasoning: a wrong comment left
in place to satisfy a line count is worse than an accurate diff. The exact
one-line code change made `RECORD_TYPES` read
`OPERATION_TYPES + ("mint", "restore", "external_edit", "reconcile",
"migrate")`.

A second recorded deviation from the same commit: `add_migration` and
`set_migration_state` are two public names beyond the plan's artifact list
(the commit message records this; `set_migration_state` exists so that
setting a recorded row's state raises `graph.migration_state_not_settable`
by name, and it later became the typed rejection route cited in `0912f5c`).

## Evidence counts, quoted from the recorded run

From commit `a7d5974`'s measured section: the evidence event count was 1
before the split and 1 after the split, the rename, and the merge; the log
file was byte-identical after the split; the one recorded event's
`objective` still equaled the pre-split id; each of the two new ids carried
0 events; and `objective_evidence_state` returned a `str` inside the
two-member tuple. `graph.py` and `course.py` import no `evidence` module,
so the no-transfer rule is structural.

## The flagged GRAPH-04 unclassified edge

Carried forward, not resolved: `demand-change` is one of the five
`MIGRATION_KINDS` and no demand vocabulary was invented.
`14B-TRACER-REPORT.md` row 9 records it as "Flagged, not resolved", citing
this plan's own "Flagged assumption carried forward, not silently dropped"
section. The reviewer question (typed demand field in 14B, or a 16A
capability-contract concept) stayed open at the 14B freeze.

## Verification, per the commit record

Commit `5568138`: `python3 tests/graph_roundtrip.py`,
`evidence_roundtrip.py`, `scoring_roundtrip.py`, `journal_roundtrip.py`,
`operations_roundtrip.py`, `schema_validate.py --all`, and
`itembank.py guard .` all exit 0. Commit `a7d5974` records the
evidence-count assertions above from the passing run. Per-truth command
mapping beyond that was not recorded at execution time; the record is
silent there and this retrospective does not invent it.

## The regression this plan introduced, and its fix

Commit `5568138` made `migrate` the eleventh `RECORD_TYPES` member while
`surfaces/visual_fixture.OPERATION_PHRASE` stayed at ten, so
`tests/visual_system_roundtrip.py` failed and `tests/phase_062_audit.py`
cascaded. This was one of the two grounds for 14B-06's withheld freeze.
Commit `0912f5c` (2026-08-27, after the withholding) fixed it with two
values recorded as Weibao's decisions of 2026-08-27, not the agent's: the
learner-facing phrase "proposed a change to", and the inclusion of
`migrate` in `UNDOABLE`, which was against the recommendation put to him
and is recorded as his call with the stated cost accepted. The freeze
closed the same day (`14B-FREEZE.md`, `d7ef923`).

## Why this summary was missing

The record is silent on why no summary was written on 2026-08-27. The
plausible mechanism, recorded in STATE.md, is that 14B-04 sat behind a
blocking human checkpoint in a wave the orchestrator drove commit by
commit through the driver packet, and the summary step was dropped between
the Task 3 commit and the 14B-06 freeze push. That is an inference, and it
is labeled as one.
