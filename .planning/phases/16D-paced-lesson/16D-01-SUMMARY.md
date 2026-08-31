# 16D-01 summary

Executed 2026-08-31. All three tasks complete.

## What shipped

- `model.py`: `LESSON_PACE_VALUES = ("none", "h3")`, `STEP_RE`,
  `STEP_LINE_RE`, `_lesson_pace()` (the `[LESSON-DIR:]` shape),
  `parse_lesson` carries the `pace`/`pace_raw` pair on every return path,
  and `lesson_steps()` resolves the D-16D-1 ladder (markers, else `h3`,
  else one `document` step). Marker lines are never rendered as prose.
- Three lint findings in the SPEC-embedded table and the emitter:
  `lesson.invalid_step` (error), `lesson.duplicate_step` (error, `intro`
  reserved), `lesson.invalid_pace` (warning).
- `fixtures/paced_lesson_bank.md`: invented-field (glimmerkeeping) bank
  with three markers, intro prose, `[LESSON-PACE: h3]` for the precedence
  assertion, and two id-assigned items; lints 0 errors, guard clean.
- `tests/paced_steps_roundtrip.py`: all six assertion groups green.

## Deviations, each the sanctioned additive path

- `schemas/lint_error.schema.json`: the three codes added to the published
  enum (the schema's own description names adding a code as additive; the
  lesson_roundtrip/gate_roundtrip guards fail on a code missing from it,
  which is how this was caught).
- `tests/lesson_roundtrip.py` and `tests/gate_roundtrip.py`: the
  `additive_defaults` maps gained the pace pair, which is those tests' own
  documented mechanism for additive parse_lesson keys (assert the default,
  then exclude), and the lesson-lint-code count assertion moved 14 to 17
  with a dated docstring note, which is that test's own documented protocol
  for new codes.
- The plan's fixture instruction said "two `##` headings"; the LESSON
  grammar's headings are `###` (the same fact that corrected `h2` out of
  LESSON_PACE_VALUES before execution), so the fixture carries three `###`
  headings, one per step.
- `parse_lesson` grew the `_raw` companion (`pace_raw`) beside `pace`,
  following the 16A convention the plan's cited helpers all use; the
  roundtrip asserts the exact key set including both.

## Verification

`python tests/paced_steps_roundtrip.py` exit 0 (six ok lines);
`python itembank.py lint fixtures/paced_lesson_bank.md` 0 errors;
`python itembank.py guard .` 0 offending files;
`python tests/lesson_roundtrip.py`, `tests/gate_roundtrip.py`,
`tests/serve_roundtrip.py`, `tests/seeding_roundtrip.py`,
`python schema_validate.py --all schemas` all exit 0.

## Rollback

Revert the model.py hunks and delete the fixture and test; the schema enum
entries and the two test additive rows come out with them. No shipped
surface reads `lesson_steps` yet, so nothing else moves.
