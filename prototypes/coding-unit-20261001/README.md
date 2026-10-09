# Native coding unit preview

Original synthetic practice: short boundary explanation, output prediction,
counting implementation, failed-case repair, debugging and a new event-window
transfer. A small command-line project brief connects the unit to independent
work. [The source fixture](../../fixtures/coding_boundary_unit.md) is for
author inspection; its keyed content is not a learner handout.

Run from the repository root in a terminal:

```sh
python3 prototypes/coding-unit-20261001/preview.py
```

The script prints the lesson and exact saved practice URL. Read the lesson,
then use the printed practice URL. The existing paired selection preserves
authored order; the runtime owns every submit, hint, score and evidence event.
Enter stops the server and removes its disposable synthetic root. Keep an
export or separate learner-owned work before stopping a preview.

The native form uses a textarea fallback. A failed practice run displays the
runtime's released cases with input, expected and actual output. Draft reload
and optional hint release were exercised. Formal feedback remains withheld.
The read-only prediction code panel preserves indentation and escapes markup,
including without JavaScript. This is source work, not an installed update.

Checks:

```sh
python3 tests/coding_unit_roundtrip.py
node --test tests/js/question_stimulus.test.mjs
```

[The owning research record](../../.planning/research/coding-learning-2026-10-01.md)
contains donor dispositions, exact broad/focused checks and remaining costs.
Unaided human transfer, visual/accessibility preference, durable native
feedback composition and isolated multi-file/dependency/server adapters remain
separate gates. Passing test inputs does not prove mastery. This preview does
not turn the standalone CS Dojo workers into production scorers.
