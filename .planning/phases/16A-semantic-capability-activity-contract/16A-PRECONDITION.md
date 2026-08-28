# Phase 16A precondition check

## Why this check exists

`16A-RESEARCH.md` carries a critical caveat: every 14A and 14B signature in the
16A research and pattern map was read from plan text, not from source, because
those modules did not exist when Phase 16A was planned. Phase 16A therefore sits
downstream of two phases that were unexecuted and one walking skeleton that was
unwalked at planning time, and every constant it builds against was a
transcription rather than an observation. This check is what turns those
transcriptions into observations before the first line of 16A code is written,
so a divergence halts the wave by name instead of arriving later as an
ImportError or, worse, as a silent vocabulary drift that nothing goes red on.

## What was checked

Run 2026-08-27 on Darwin arm64, Python 3.14.6, immediately after
`14B-FREEZE.md` was rewritten from a withholding to a freeze.

| Step | Check | Result |
|---|---|---|
| 1 | `identity`, `journal`, `discovery`, `graph`, `course`, `course_package` all import | `ok` |
| 2 | `identity.RIGHTS_OPERATIONS` is the exact seven-tuple | `ok` |
| 2 | `identity.RIGHTS_STATES` equals `("granted", "denied", "unknown")` | `ok` |
| 2 | `identity.OBJECT_KINDS` is a tuple carrying `"lesson"` | `ok` |
| 2 | `new_object_id`, `object_fingerprint`, `rights_state`, `rights_granted` all callable | `ok` |
| 3 | `graph.COURSE_GRAPH_VERSION` equals `1` | `ok` |
| 3 | `graph.SECTION_ORDER` is a tuple | `ok` |
| 3 | `graph.outline_projection` callable | `ok` |
| 3 | `course.read_course` and `course.write_course` both callable | `ok` |
| 3 | `graph.TREATMENT_KINDS` has exactly eleven members | `ok` |
| 3 | `graph` has no `compose_glossary`, and `import capabilities` raises `ModuleNotFoundError` | `ok` |
| 4 | `14A-FREEZE.md` carries `## Frozen at 14A` and no withholding heading | `ok` |
| 4 | `14B-FREEZE.md` carries `## Frozen at 14B` and no withholding heading | `ok` |
| 5 | At least one `13.9-*-SUMMARY.md` exists, and `13.9-03-SUMMARY.md` specifically | `ok`, three summaries present |
| 6 | The shipped lesson surface is unchanged | `ok`, exact expected line |
| 6 | `evidence.mark_event` still refuses a model marker | `ok`, `mark_event human-only gate holds` |

Step 5 is checked directly rather than by trusting `14B-FREEZE.md` to have
honored it, because `ROADMAP.md`'s Phase 14B entry forbids that freeze closing
before Phase 13.9 has been walked, and a frozen 14B behind an unwalked skeleton
would be a record its own roadmap entry forbids. It is walked, so this is not
that case.

## Additivity baseline

Every later 16A plan asserts these three values unchanged. A changed value means
a format change was not additive.

```
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```

All three match the values `16A-01-PLAN.md` recorded at planning time, so the
golden fixtures did not drift between planning and execution and no
found-versus-planned pair needs recording. `python3 tests/lesson_roundtrip.py`
exits 0 against them, so they are green before being trusted as a baseline.

## Deviations found

`none`.

Every constant Phase 16A was planned against, read from plan text rather than
from source, matches the landed source exactly. Plans 02 through 10 therefore do
not need re-reading against the two freeze records before execution.

**One thing this section deliberately does not call a deviation.** `14B-FREEZE.md`
carried `## Freeze withheld` earlier on 2026-08-27 and carries `## Frozen at 14B`
now. Step 4 reads the file as it stands, which is a real freeze, and the record
itself names how both grounds of the withholding closed and names the waiver
under which the authorability leg was signed. A reader who wants to judge that
freeze should read it rather than this line.

## Dated result line

**2026-08-27. Phase 16A may proceed.** All seven checks returned `ok`, no
divergence was found, and the additivity baseline is recorded above.

Command output, verbatim:

```
modules present
14A surface matches
14B surface matches
both freezes are real freezes
13.9 walked, 3 summaries
4 ['EXAMPLE', 'KEY', 'NOTE', 'WARNING'] ('required', 'recommended', 'off') True True False
mark_event human-only gate holds
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```
