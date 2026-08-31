# 16D-02 summary

Executed 2026-08-31. All four tasks complete.

## What shipped

- `runtime.py`: the 16D section: `LESSON_RUN_KIND`, `start_lesson_run`
  (atomic, via the one `write_session` idiom), `read_lesson_run` (structured
  refusal, never a raise), `lesson_run_advance` (unknown step refused by
  name), `lesson_run_record`, `_selected_letters`, and
  `checkpoint_feedback` (the D-PACED-3 tier ladder: tier 1 marks only the
  learner's own selections, tier 2 rides with it carrying DA for touched
  options only, tier 3 on the second wrong attempt or explicit request;
  exam and diagnostic refused by name). `FEEDBACK_POLICIES` gained the
  `paced` entry (practice's held-retry shape; like `legacy`, never a
  sitting mode).
- `evidence.py`: `LESSON_RUN_CONTEXT = "lesson_run"` beside the 6.2
  constant.
- `schemas/response.schema.json`: `context` enum gained `lesson_run`, and
  the `mode` enum gained `paced` (see deviations), both with description
  sentences citing the decision.
- `schemas/lesson_run.schema.json`: published, self-checking, with the
  presentation-state-never-progress rule in its own description.
- `blueprint.py`: `evidence_proposal`'s counted rows exclude
  `context == "lesson_run"` by default, with the reconsideration condition
  in the comment. `quiz` and `lesson_gate` handling untouched.
- `tests/lesson_run_roundtrip.py`: four assertion groups, all green.

## Additivity proof

40 pre-change response events (fixtures/lesson_retention_events.jsonl and
fixtures/selection_evidence.jsonl) validate against the updated schema
unchanged; a junk context still fails. Denominator measured: 5 rows of
which 2 lesson_run, proposal denominator 3.

## Deviations

- The plan did not name the `mode` enum: a response event's `mode` is
  required and closed, and `paced` was not in it, so recording a truthful
  mode on a paced checkpoint needed the same additive enum step as
  `context`. The alternative, stamping `practice` on paced attempts, would
  have made the one label a lie and the context field load-bearing twice.
  Additive by the same proof (the 40 baselines validate).
- `start_lesson_run` imports `evidence` function-locally: `evidence`
  imports `runtime`, so a top-level edge would cycle (the pattern every
  other evidence use in runtime.py already follows).

## Verification

`python tests/lesson_run_roundtrip.py` exit 0;
`python schema_validate.py --all schemas` 26 documents clean;
hint, model_gate, selection, blueprint, evidence roundtrips and the 15B
acceptance tracer all exit 0; `python itembank.py guard .` clean.

## Rollback

Revert the runtime and evidence hunks, the two schema enum entries, the
blueprint filter, and delete the schema and test. Nothing shipped consumes
`checkpoint_feedback` until 16D-03, so the surface is unaffected.
