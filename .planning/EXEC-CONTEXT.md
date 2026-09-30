# Execution context (read this instead of the planning stack)

Written 2026-08-20 to cut the standing prompt for cheap execution runs.
An executor starts with this file, the applicable AGENTS.md and the assigned plan. Consult exact cited contract sections when the plan leaves a material question open, contradicts live state or touches an authority boundary. Do not load the full planning stack by default. A compact execution note cannot override binding contracts or the current user request.

## Act first

Write a file or run a command in your first turn. Do not restate the plan,
do not summarize these rules, do not produce an analysis section. Infer ordinary reversible details from the task. If an ambiguity changes scoring, rights, disclosure, recovery or product intent, consult the owner or flag the exact gap before dependent work. Continue independent work while it is unresolved.

## Five rules you cannot break

1. The runtime owns correctness, session state, evidence, and keyed
   assessment disclosure. A model never settles a score or decides how
   much of a key to reveal.
2. Exactly one parser (`model.py`), one scorer (`runtime.py`), one
   evidence store. Never add a second. New scoring behavior is an additive
   extension inside the existing scorer.
3. Evidence and banks stay on disk. No telemetry or vendor-held gradebook. Learner-initiated export, backup and device sync remain permitted within their granted rights.
4. Preserve format compatibility. New features are additive; documented deprecation and explicit reviewed migration may retire an element. Never break older artifacts silently.
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

When commit is authorized, use one atomic commit per plan, a conventional prefix and the plan ID:

    feat(14B-01): add the typed graph kernel
    test(14B-01): graph roundtrip over three domains
    fix(14B-01): reject an edge whose endpoint is unknown

Limit every commit to a pathspec you name explicitly. Do not use a bare
`git commit -a`. Another agent may share this working tree.

## Do not write a summary unless one of two things is true

Added 2026-08-21 after Weibao measured the cost. There are 129 `-SUMMARY.md`
files holding 23,261 lines, which is more than half the size of the entire
runtime. Most of them restate commit messages that already said the same thing
in more detail.

**The commit messages are the record.** Write them properly: what was wrong,
what you changed, what you measured, and what you did not do. A reader with
`git log` should need nothing else.

Write a `-SUMMARY.md` only when:

1. **The plan was left incomplete.** Name exactly what is not built and why,
   so nobody later reads a closed plan as a finished feature.
2. **You found something that contradicts the plan.** A measured fact that
   makes a plan task wrong, unnecessary, or impossible. Record the measurement
   and the date.

A plan whose `<summary_obligations>` block asks for a summary does not override
this. If neither condition holds, satisfy the obligation in the commit body and
move on. Ceremony that nobody reads is money spent on nothing.

Enforced mechanically since 2026-09-03 by `scripts/summary_gate.py`, run in CI
and by `scripts/preflight.py`. A summary not listed in
`.planning/summary-baseline.txt` must open with the heading
`## Why this summary exists`, stating which of the two conditions holds, and
must stay under 3,000 bytes. Do not write summaries retrospectively for plans
that already closed; the commit log is their record. Do not edit the baseline
to pass a build.

## When you are stuck

Write what you tried and what blocked you into the plan's `-SUMMARY.md`,
commit that, and stop. Do not loop. Do not redesign the plan.
