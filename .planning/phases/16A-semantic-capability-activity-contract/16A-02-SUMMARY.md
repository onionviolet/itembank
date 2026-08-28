# Plan 16A-02 summary

Executed 2026-08-27 into 2026-08-28, Darwin arm64, Python 3.14.6. All three
tasks ran. Three commits: `aa14114` (Task 1), `97e2005` (Task 2), `b7e505b`
(Task 3).

## Which decision options were in force

**`D-16A-1`: option-a, add alongside.** No consequence list applied. Task 2's
alternate branch, which would have rewritten `_callout_spec`,
`_callout_kind_of`, and `_CALLOUT_KINDS` under option-b, was not taken, and no
`## D-16A-1a. Promotion trigger` subsection was owed because that subsection
belongs to option-c.

**`D-16A-2`: option-a, one new pure module.** No consequence list applied.
`capabilities.py` was created at the repository root and the media and activity
grammars stayed out of it, which is plan 16A-04's and 16A-05's work.

Both were recorded on 2026-08-27 by an agent under Weibao's standing
delegation, not answered by him directly. `16A-DECISIONS.md` states that inside
each section; this summary repeats it so a reader of the execution record does
not have to go looking.

**The exact `(slug, label)` pair registered:** `("prerequisite", "Before this")`,
under the key `"PREREQUISITE"`. Checked character by character against
`16A-01-PLAN.md` lines 543 to 549 before it was written.

## Line ranges added to `surfaces/lesson.py`

So the no-visual-token grep in the acceptance criteria is checkable. Ranges are
post-change line numbers, from `git diff aa14114 b7e505b -- surfaces/lesson.py`.

| Hunk | New range | What it is |
|---|---|---|
| 1 | 329 to 335 | `LESSON_TEMPLATE`'s `<html>` tag gains `lang` and `dir` placeholders |
| 2 | 650 to 661 | the one `_CALLOUT_KINDS` entry plus its comment |
| 3 | 1757 to 1895 | `guided_stages`, `_stage_html`, `_split_rendered_stages`, and their comments |
| 4 | 1945 to 1954 | `lesson_page`'s `mode` keyword and docstring sentence |
| 5 | 2020 to 2056 | the `mode` guard and the guided grouping inside the heading loop |
| 6 | 2154 to 2170 | `doc_lang` and `doc_dir` plus their two `.replace()` calls |

`grep -nE "#[0-9a-fA-F]{3,6}|var\(--|font-size|margin|padding|transition"` over
the added lines returns exactly one hit, at the comment in hunk 3 reading "no
color, spacing, token, transition, or script is introduced by any of this". It
matches the word `transition` in prose. **No color, spacing value, font size,
CSS variable, transition, or token was added by this plan**, and no
`<details>` element and no JavaScript either.

## Which branch Task 2 step 2 took on `LESSON_CSS`

**The add-nothing branch.** Step 2 says to add one line of CSS class support
only if `LESSON_CSS` already carries a per-slug rule for the four shipped kinds.
It does not. `LESSON_CSS` carries one shared `.callout` rule at line 193 plus
`.callout-label`, `.callout-icon`, and `.callout-body`, none of them per-slug.
The two slug-shaped selectors that do exist,
`.callout-example.example-parallel` at line 272 and `.callout-check` at line
319, are a layout variant for parallel examples and the reserved check slot;
neither is a generic per-kind style, and neither of the other two shipped kinds
has one. **So no CSS was added**, which is also what keeps this plan's
no-visual-decision prohibition true by construction rather than by restraint.

## The golden SHA-256 values, re-verified

Neither moved. Recomputed after every change in this plan:

```
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```

All three are byte-identical to the values `16A-PRECONDITION.md` recorded, which
were themselves the values `16A-01-PLAN.md` recorded at planning time. The
format did not move.

## The tracer's final line, verbatim

```
TRACER: 2 passed, 0 skipped, 0 failed
```

Two is the count `16A-VALIDATION.md` predicts after plan 16A-02.

## The shipped-suite guard exercise

Run rather than reasoned about. `tests/lesson_roundtrip.py` was renamed to
`tests/lesson_roundtrip.py.hidden`, the tracer re-run, and it printed:

```
scenario thin_slice: SKIP (shipped suite red: tests/lesson_roundtrip.py)
scenario additivity_golden_parse: SKIP (shipped suite red: tests/lesson_roundtrip.py)
TRACER: 0 passed, 2 skipped, 0 failed
```

Skips rather than passes, and no green claim over a red foundation. **The file
was restored in the same command** and the tracer re-run immediately, printing
`TRACER: 2 passed, 0 skipped, 0 failed`. `git status` shows no trace of the
rename.

## Which truth was verified by which command

| Truth | Command | Actual output |
|---|---|---|
| The two new constants exist with the planned values | `python3 -c "import model; print(model.SEMANTIC_PROFILE_VERSION, model.LESSON_DIRECTIONS)"` | `1 ('ltr', 'rtl', 'auto')` |
| The parse layer defaults and the thin slice's own values | the plan's Task 1 verify one-liner | `parse layer ok` |
| A malformed directive falls back and never raises, and lint names all three | inline assertions over a mutated copy | `malformed falls back, never raises, and lint names all three` |
| Profile 2, profile 0, profile -1, and `ar`/`rtl` all behave | inline assertions | `profile 2, zero, negative, and ar/rtl all behave` |
| The corpus is deterministic across two directories | SHA-256 of two builds | `deterministic across two directories` |
| The registry and render layers | the plan's Task 2 verify one-liner | `registry and render layers ok` |
| `capabilities.py` is pure | `grep -c "open(" capabilities.py`; `grep -cE "^import (evidence\|runtime)..."` | `0` and `0` |
| The registry's shape | `python3 -c "import capabilities; print(...)"` | the seven keys, the three availability values, and `1` |
| `register` copies and refuses three ways | inline assertions | `register: copies, refuses bad key set, bad availability, and duplicates` |
| An unregistered capability degrades to the empty string | `static_path` on a known and an unknown name | the fallback sentence, then `''` |
| Callout containers are byte-identical across modes | container extraction and list comparison | `callout containers byte-identical across modes: 2 of them` |
| Exactly one stage is open | `count('data-stage-open="1"')` | `exactly one open stage; 3 stages total` |
| An unknown mode fails loudly | `lesson_page(..., mode="sideways")` | `lesson_page: mode must be "continuous" or "guided" (got 'sideways')` |
| The tracer | `python3 tests/capability_stress_corpus_tracer.py` | `TRACER: 2 passed, 0 skipped, 0 failed` |
| No test framework, no hash literal in the tracer | the two acceptance greps | `0` and `0` |
| The full suite | `for t in tests/*.py; do python3 "$t" \|\| exit 1; done` | exit 0 |
| No repository-authored em dash | `python3 itembank.py guard .` | `0 offending files` |

The full suite was run with `ANKI_CONNECT_URL` pointed at a closed port, the
condition `day_roundtrip.py`, `retention_ui_roundtrip.py`, and
`phase_062_audit.py` are written for and the condition CI runs in. Anki is open
on this machine; with it reachable those three read live counts and fail on a
copy comparison, which is environmental and is recorded the same way
`14B-FREEZE.md` records it.

## Deviations from the plan, each with its reason

**1. `guided_stages` takes an optional second argument.** The plan writes the
signature as `guided_stages(heading_body)` but specifies the `slug` field as
"the heading slug plus a `-stage-<index>` suffix". A function given only a body
cannot know the heading slug, so the two halves of the spec cannot both be
satisfied as written. The signature is now
`guided_stages(heading_body, heading_slug="")`: the plan's one-argument call
still works, and the slug is still built through `model.lesson_slug` rather than
by raw string manipulation, which is the part of the spec that carries the
reason.

**2. Stage indices run across the document, not per heading.** The plan
describes `_stage_html` as opening index `0` only, and separately requires that
exactly one stage carry `data-stage-open="1"`. Numbering per heading satisfies
the first and breaks the second: the shipped fixture has two headings, so the
first implementation emitted two open stages. Indices are now offset by a
document-level counter. Per-heading numbering is not one guided reading, it is
several started at once.

**3. Guided mode splits the rendered string rather than re-rendering stages.**
The plan says to render through `render_markdown` "exactly as continuous mode
does, then group". Rendering each stage's raw text as a separate
`render_markdown` call would thread a shared `ctx` through several calls, and
that context accumulates glossary first-uses and panel state, so stage-by-stage
rendering could legitimately differ from whole-heading rendering. Instead the
heading is rendered once, exactly as continuous mode renders it, and
`_split_rendered_stages` cuts that string after each callout container's close.
The byte-identity requirement then holds by construction rather than by
coincidence: the containers in guided mode are literally the bytes continuous
mode produced.

**4. Three coupled files the plan did not name, all found by red tests rather
than by reading.**

- `schemas/lint_error.schema.json` carries a `code` enum asserted equal to
  `model.LINT_CODES`, so the three new codes had to be added there too.
  `tests/lesson_roundtrip.py` reported it by name.
- `tests/lesson_roundtrip.py`'s `test_spec_names_every_lesson_lint_code`
  asserts an exact lesson-code count, raised from six to nine. The assertion
  did its job: it failed until the `SPEC` table carried rows for all three new
  codes, which is exactly the coupling it exists to enforce.
- `tests/gate_roundtrip.py` has pinned `parse_lesson`'s exact key set since
  Phase 6.2 and went red on the six added keys.

**5. Both key-set assertions were strengthened rather than loosened.** The
Phase 3 golden comparison and the Phase 6.2 key-set pin both had to tolerate
six new keys, and the plan requires the golden hashes unchanged and both suites
green. Dropping the new keys from each comparison would have been enough to go
green and would have weakened both into "the old keys still agree". Instead each
now asserts that the six new keys carry exactly their documented defaults before
removing them from the comparison. That says something the golden alone does
not: a bank carrying none of the three directives reads today exactly as it read
before they existed. A key whose default changes, or a key added with no
default, now fails by name in both places.

## What this plan did not do

It added no output-mode vocabulary, no media vocabulary, no schema file, and no
second seeded capability profile: plan 16A-04 owns all four. It changed
`_callout_spec`, `_callout_kind_of`, `_callout_html`, `_CALLOUT_MARK_RE`, and
the block classifier not at all. It introduced no required-semantic handling,
which is plan 16A-03's, which is why every stage's `requires` list is empty. And
it made no visual decision of any kind, which is Phase 17A's to make.
