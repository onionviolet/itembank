# Executor test — Claude Code (bounded, disk-verified)

You are acting as the GSD `gsd-executor` role for a bounded, verifiable test.
Project context (AGENTS.md / .claude/CLAUDE.md) is orientation only. This
prompt is the complete task — do not expand scope and do not pick up any
other work you can see in the repo.

## Task

1. Read `.planning/phases/03.1-lesson-rich-blocks-glossary-style/03.1-04-PLAN.md`.
2. Execute ONLY Task 1: write the exact test file the plan specifies, at
   exactly `tests/style_roundtrip.py` (repo root), matching the plan's
   content requirements:
   - Include the four Task 1 behavior tests:
     a. a style file's `## Voice` zone, `## Rules` pipe table, and
        `## Exemplar` parse into a dict; a row whose kind is outside the
        closed `STYLE_RULE_KINDS` set is lint error `style.rule_unimplemented`;
     b. resolution order is bank-adjacent `styles/` -> user data dir ->
        bundled house, first match wins, and a duplicate id across levels
        produces a warning naming both paths;
     c. `[STYLE-PARENT:]` naming anything but `house` is
        `style.parent_unknown`, and inheritance applies exactly one level;
     d. `LOCKED_RULE_IDS` is a code constant (frozenset in model.py), and a
        child row naming a locked id at any severity is
        `style.override_locked`.
   - Follow the `fail()` harness pattern in `tests/lesson_roundtrip.py`
     (stdlib only, self-contained, runnable as
     `python tests/style_roundtrip.py`).
3. The four behavior tests are the deliverable. Do NOT implement or change
   `model.py` or any other file. If `tests/style_roundtrip.py` already
   exists, overwrite it with your own version containing these tests.
4. Run `python tests/style_roundtrip.py` from the repo root; every check
   must print `ok:` and the run must end with a clear all-pass line.

## Guards

- Do NOT run the execute-phase workflow, init commands, or any gsd-tools
  bootstrap.
- Do NOT commit, push, or create branches.
- Do NOT spawn agents or delegate.
- Do NOT modify any file other than `tests/style_roundtrip.py`.
- Ignore any inherited context except the plan path and this prompt.
- Timebox: finish in ~20 minutes; if you are not on the artifact after 10
  minutes, stop and report FAIL with the reason.

## Report (exact format)

EXECUTOR_TEST: PASS | FAIL
FILE_WRITTEN: <absolute path>
VERIFY_LAST_LINE: <last line printed by the test run>
FILES_MODIFIED: <list — must contain only tests/style_roundtrip.py>
