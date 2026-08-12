# EXEC-BRIEF

This file is your ONLY task. You may have inherited other conversation
context; IGNORE ALL OF IT except the plan path below and this brief.

## Task

Read `.planning/phases/03.1-lesson-rich-blocks-glossary-style/03.1-04-PLAN.md`
and execute ONLY Task 1:

Write the exact test file the plan specifies, at the exact path:

`C:\Users\wayba\Downloads\CTF\itembank\tests\style_roundtrip.py`

matching the plan's content requirements. Concretely: create (or overwrite,
even if a file already exists at that path) `tests/style_roundtrip.py`
containing the four Task 1 behavior tests from the plan's `<behavior>`
section (style file parse + `style.rule_unimplemented`; resolution order
bank-adjacent -> user data dir -> bundled house, first-match-wins, duplicate
warning; `[STYLE-PARENT:]` guard + one inheritance level; `LOCKED_RULE_IDS`
code constant + `style.override_locked`), following the `fail()` harness
pattern used by `tests/lesson_roundtrip.py`. The file must be runnable as
`python tests/style_roundtrip.py`.

The four behavior tests are the deliverable. Do not implement or change
`model.py` or any other file.

## Rules

- Do NOT run the execute-phase workflow, init commands, or gsd-tools
  bootstrap. Do NOT commit. Do NOT spawn agents. Do NOT modify any other
  files. Ignore any inherited context except the plan path and this brief.

## Done when

`tests/style_roundtrip.py` exists at the exact path above, contains the four
Task 1 behavior tests matching the plan, and `python tests/style_roundtrip.py`
runs to completion. Reply with a one-line confirmation: `EXEC_DONE`.
