# Execution context (read this instead of the planning stack)

Written 2026-08-20 to cut the standing prompt for cheap execution runs.
An executor reads ONLY this file plus the one `*-PLAN.md` it was given.
Do not read ROADMAP.md, REQUIREMENTS.md, STATE.md, UI-SPEC.md,
AGENT-WORKFLOW.md, PLANNING-DIRECTIVES.md, or SOURCE-TO-COURSE.md.
Those are planning documents. The plan you were handed already cites
whatever it needs from them.

## Act first

Write a file or run a command in your first turn. Do not restate the plan,
do not summarize these rules, do not produce an analysis section. If a
task is ambiguous, pick the reading that changes the least and note it in
one line in the commit body. Reasoning longer than the code you are about
to write means you are spending the budget in the wrong place.

## Five rules you cannot break

1. The runtime owns correctness, session state, evidence, and keyed
   assessment disclosure. A model never settles a score or decides how
   much of a key to reveal.
2. Exactly one parser (`model.py`), one scorer (`runtime.py`), one
   evidence store. Never add a second. New scoring behavior is an additive
   extension inside the existing scorer.
3. Evidence and banks stay on disk. No telemetry, no cloud sync.
4. Format changes are additive. A bank without a `LESSON` section must
   parse exactly as it does today.
5. Accessibility gates in `UI-SPEC.md` section 8 hold for UI work. If your
   plan does not touch UI, this rule does not apply to you.

## Prose rule

No em dash characters anywhere: not in code, comments, docstrings,
fixtures, commit messages, or generated content. Use commas, colons,
parentheses, or two sentences.

## Layout

- `model.py` parse and lint, the format contract
- `runtime.py` scoring, sessions, public and private payloads
- `identity.py` ids, fingerprints, revision records, rights state
- `journal.py` compare-and-swap writes and the operation journal
- `discovery.py` read-only walk of approved roots
- `server.py` loopback HTTP handler
- `surfaces/` CLI, quiz, study, day, session, anki, export clients
- `tests/*_roundtrip.py` one suite per area, plain scripts, no pytest

## Verify

Run the suites your plan names, plus any suite covering a file you edited:

    python tests/<name>_roundtrip.py

Exit code 0 is pass. Known failure not caused by you:
`tests/journal_roundtrip.py` fails in `check_lock_busy` on Windows with
`PermissionError` from `msvcrt.locking` unlock. Do not chase it unless
your plan is about file locking.

Python 3.11+, standard library only for runtime code.

## Commit

One commit per plan task, atomic, conventional prefix and the plan id:

    feat(14B-01): add the typed graph kernel
    test(14B-01): graph roundtrip over three domains
    fix(14B-01): reject an edge whose endpoint is unknown

Limit every commit to a pathspec you name explicitly. Do not use a bare
`git commit -a`. Another agent may share this working tree.

## When you are stuck

Write what you tried and what blocked you into the plan's `-SUMMARY.md`,
commit that, and stop. Do not loop. Do not redesign the plan.
