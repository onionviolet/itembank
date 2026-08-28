# 16A-03 summary: the six remaining roles, the unknown-semantic contract, and the worked-example-first default

**Executed 2026-08-28.** Darwin arm64, Python 3.14.6. Plan
`16A-03-PLAN.md`, three tasks, all complete.

Output: eleven callout kinds, a fourteen-entry role catalog, two named
degradation paths, and a lint check for CAP-01's worked-example-first default
with its reasoned override.

---

## 1. The six `(slug, label)` pairs as registered

`surfaces/lesson.py` lines 659 to 664, six one-line entries added to
`_CALLOUT_KINDS` immediately after the `PREREQUISITE` entry plan 16A-02 added.
The pairs are exactly `D-16A-1` option-a's:

| Token | slug | label |
|---|---|---|
| `MISCONCEPTION` | `misconception` | `Common mistake` |
| `TIP` | `tip` | `Expert tip` |
| `COUNTEREXAMPLE` | `counterexample` | `Counterexample` |
| `EXCERPT` | `excerpt` | `From the source` |
| `UNCERTAINTY` | `uncertainty` | `Not settled` |
| `SUMMARY` | `summary` | `In short` |

`len(_CALLOUT_KINDS)` is `11`. Its sorted key list is exactly

```
['COUNTEREXAMPLE', 'EXAMPLE', 'EXCERPT', 'KEY', 'MISCONCEPTION', 'NOTE',
 'PREREQUISITE', 'SUMMARY', 'TIP', 'UNCERTAINTY', 'WARNING']
```

No parse branch was added for any of them. `_callout_spec`, `_callout_kind_of`,
and the shipped four are untouched by Task 1.

## 2. The `_CALLOUT_MARK_RE` source line, verbatim

The acceptance criteria pin this line so a later reader can compare it rather
than trust a claim. It is byte identical to its pre-16A text:

```
_CALLOUT_MARK_RE = re.compile(r"^>\s*\[!([A-Za-z][^\]]*)\]\s*(.*)$")
```

`surfaces/lesson.py:641`. Group 1 is `([A-Za-z][^\]]*)`, which already accepts a
trailing exclamation mark, which is why the required marker needed no regex
change. `git diff surfaces/lesson.py` shows no change on that line.

## 3. Line ranges added, so the no-visual-token grep is checkable

| File | Added ranges | What |
|---|---|---|
| `surfaces/lesson.py` | 659 to 664 | the six `_CALLOUT_KINDS` entries |
| `surfaces/lesson.py` | 906 to 940 | `UNSUPPORTED_SEMANTIC_COPY` (912) and `_callout_required_of` (916) |
| `surfaces/lesson.py` | 956 to 977 | `_callout_entered` |
| `surfaces/lesson.py` | 1253 to 1271 | `_unsupported_callout_html` |
| `surfaces/lesson.py` | 1247 to 1250 | `_callout_html`'s `required` flag line and signature |
| `model.py` | 518 to 546 | `_lesson_example_order` |
| `model.py` | 2209 | `LESSON_EXAMPLE_ORDERS` |
| `model.py` | 2172 to 2186 | four new SPEC lint-table rows |
| `model.py` | 2382 to 2383 | four new `LINT_CODES` members |
| `model.py` | 3492 to 3528 | the unknown-semantic lint checks |
| `model.py` | 3529 to 3568 | the example-order lint checks |

`git diff -U0 surfaces/lesson.py | grep '^+' |` grep for
`#[0-9a-fA-F]{3,6}|font-size|margin|padding|transition` returns nothing. No
color, spacing, typography, motion, or token constant was introduced anywhere
in this plan.

`git diff -U0 | grep '^+' | grep -c '—'` returns `0`. No em dash character
appears in any line this plan added.

## 4. The fourteen catalog entries as written

`capabilities.SEMANTIC_ROLE_CATALOG`, a fourteen-member tuple in CAP-01's own
listing order. Exactly seven carry `shipped_in` equal to `"16A"`.

| # | role | module | shipped_in | reachable_by |
|---|---|---|---|---|
| 1 | key idea | `surfaces.lesson` | 3.1 | `> [!KEY]` |
| 2 | warning | `surfaces.lesson` | 3.1 | `> [!WARNING]` |
| 3 | prerequisite | `surfaces.lesson` | 16A | `> [!PREREQUISITE]` |
| 4 | misconception | `surfaces.lesson` | 16A | `> [!MISCONCEPTION]` |
| 5 | expert tip | `surfaces.lesson` | 16A | `> [!TIP]` |
| 6 | worked example | `surfaces.lesson` | 3.1 | `> [!EXAMPLE]` |
| 7 | counterexample | `surfaces.lesson` | 16A | `> [!COUNTEREXAMPLE]` |
| 8 | source excerpt | `surfaces.lesson` | 16A | `> [!EXCERPT]` |
| 9 | term and definition | `model` | 3.1 | `model.parse_terms` |
| 10 | uncertainty | `surfaces.lesson` | 16A | `> [!UNCERTAINTY]` |
| 11 | summary | `surfaces.lesson` | 16A | `> [!SUMMARY]` |
| 12 | inline check | `surfaces.lesson` | 6.2 | `surfaces.lesson._gate_band_html` |
| 13 | hint | `runtime` | 6 | `runtime.authored_hint` |
| 14 | accessible visual interaction | `runtime` | 06.1 | `runtime.public_item` |

`scenario_fourteen_roles` imports every `module` and asserts every
function-shaped `reachable_by` is callable on it, so a stale entry fails the
tracer by name rather than reading plausibly.

`role_mechanism(role)` returns a shallow copy of the matching entry and `None`
for anything else; both are asserted in the tracer.

Seven roles were catalogued and not rebuilt. No task in this plan edited
`runtime.py`, `evidence.py`, or `surfaces/quiz.py`; `git diff --stat` confirms
none of the three appears in the change set.

## 5. The unknown-semantic contract

`_callout_required_of(raw)` returns the three documented tuples:

```
('MISCONCEPTION', True) ('MISCONCEPTION', False) ('WHATEVER', True)
```

`UNSUPPORTED_SEMANTIC_COPY` equals exactly:

```
This block needs a lesson feature this reader does not have. Its text is below, unchanged.
```

One deviation from the plan's Task 2 step 4 is recorded in section 9 below: the
extended guard is a named helper, `_callout_entered`, rather than the same
boolean expression written twice.

## 6. The lint findings each new fixture bank produced

`python itembank.py lint` on each generated bank, verbatim findings:

**`capability_all_roles_bank.md`**: `3 items, 0 errors, 4 warnings`. Three
`item.missing_id` and one `key.missing_id`, all of which are the unminted-id
warnings every fixture bank in this repository carries. No lesson findings.

**`capability_unknown_semantics_bank.md`**: `1 items, 1 errors, 2 warnings`.

```
error  BANK: [!ALSOUNKNOWN!] is marked required and is not a known semantic role; it renders the unsupported-block fallback
warn   Q1: no [ID:] line; run `itembank id-assign` before evidence is recorded against this item
warn   BANK: [!WHATEVER] is not a known semantic role; it renders as a plain paragraph
```

**`capability_definition_first_bank.md`** (`override=None`):
`2 items, 0 errors, 5 warnings`, including exactly one

```
warn   BANK: heading 'Defining The Lift Window' places a definition before its first worked example; CAP-01's default is example first, or record a reason with [EXAMPLE-ORDER: definition-first because ...]
```

**`capability_definition_first_reason_bank.md`** (`override="with_reason"`):
`2 items, 0 errors, 4 warnings`. Zero `lesson.definition_before_example` and
zero `lesson.example_order_no_reason`.

**`capability_definition_first_no_reason_bank.md`** (`override="no_reason"`):
`2 items, 1 errors, 5 warnings`. Both codes fire:

```
error  BANK: [EXAMPLE-ORDER: definition-first] carries no because clause; CAP-01 requires a recorded reason for the override
warn   BANK: heading 'Defining The Lift Window' places a definition before its first worked example; ...
```

**The override is not a bypass.** That last case is the degraded state Task 3's
verify block names: an override with no recorded reason neither suppresses the
warning nor passes silently.

## 7. The tracer's final summary line, verbatim

```
scenario thin_slice: pass
scenario additivity_golden_parse: pass
scenario fourteen_roles: pass
scenario unknown_semantics: pass
scenario example_order: pass
TRACER: 5 passed, 0 skipped, 0 failed
```

Exit code 0. This matches `16A-VALIDATION.md`'s expected count of 5 after
16A-03 exactly, so no scenario was added or lost.

## 8. The additivity proof, re-verified

`sha256` of the three baseline files, re-read after every change in this plan:

```
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```

All three are byte identical to `16A-PRECONDITION.md`'s Additivity baseline.

`python tests/lesson_roundtrip.py`, `python tests/gate_roundtrip.py`,
`python tests/visual_roundtrip.py`, `python tests/protocol_roundtrip.py`,
`python tests/presentation_roundtrip.py`, and `python tests/style_roundtrip.py`
each exit 0.

`python itembank.py guard .` reports `0 offending files`.

**Full suite.** `for t in tests/*.py; do python "$t" || echo FAIL; done` leaves
exactly three red files: `tests/day_roundtrip.py`,
`tests/phase_062_audit.py`, and `tests/retention_ui_roundtrip.py`. All three
were re-run against a clean `git stash` of this plan's changes and fail there
too, so all three are pre-existing and none is caused by 16A-03.
`tests/day_roundtrip.py` specifically fails because a live Anki instance is
reachable on this machine, so the "Anki closed" locked copy it asserts is not
what `day --check` prints here.

## 9. Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| fourteen roles render, catalog has fourteen entries with seven from 16A | the plan's Task 1 `python -c` block | printed `fourteen roles ok`, exit 0 |
| seven roles catalogued, not rebuilt; no edit to runtime, evidence, quiz | `git diff --stat` | none of the three files appears |
| eleven callout kinds through the shipped container | `len(lesson._CALLOUT_KINDS) == 11` in the same block | passed |
| required marker needs no regex change | `grep -n '_CALLOUT_MARK_RE = re.compile' surfaces/lesson.py` | line 641, byte identical, quoted in section 2 |
| unknown optional degrades unchanged, unknown required refused out loud | the plan's Task 2 `python -c` block | printed `unknown-semantic contract ok`, exit 0 |
| worked-example-first default plus reasoned override | `python tests/capability_stress_corpus_tracer.py` | `scenario_example_order: pass` |
| additivity holds | the three sha256 values plus `tests/lesson_roundtrip.py` | unchanged, exit 0 |

## 10. Deviations from the plan, with reasons

Five, each recorded rather than glossed.

**D1. The extended guard is a named helper rather than an inlined expression.**
Task 2 step 4 says the guard at the callout branch "becomes: enter the callout
branch when the marker matches and either `_callout_kind_of(line)` is not
`None` or `_callout_required_of(<group 1>)` reports `required` is `True`", and
then says the paragraph-continuation guard "must be extended the same way".
Written literally that is the same three-clause expression in two places, and
the plan's own key_links note says the failure mode is exactly the two drifting
apart. It is therefore one function, `surfaces/lesson.py:_callout_entered`,
called from both sites. The behavior is the plan's, unchanged; only the
spelling differs.

**D2. `schemas/lint_error.schema.json` was edited, and the plan's
`files_modified` list does not name it.** `tests/lesson_roundtrip.py` asserts
every `LINT_CODES` member appears in that schema's `code` enum, so adding four
codes without adding four enum members makes the shipped suite red. The four
strings were added and nothing else in the file changed.

**D3. `model.SPEC`'s lint table gained four rows, and the plan does not mention
it.** Same cause: `tests/lesson_roundtrip.py`'s
`test_spec_names_every_lesson_lint_code` asserts each lesson code appears in
`SPEC` and asserts the exact count of lesson codes. The count assertion was
raised from `9` to `13` in that test with its docstring updated to say who
raised it and why, following the note plan 16A-02 already left there.

**D4. `tests/gate_roundtrip.py` and `tests/lesson_roundtrip.py` gained
`example_order` and `example_order_reason` in their `additive_defaults`
dicts.** Both files carry an explicit list of keys later phases added to
`parse_lesson`, each asserted to hold its documented default before being
dropped from a byte-comparison. Adding two keys without extending both lists
fails those tests by design. This is the additivity floor working, not a
weakening of it: the two new keys are now asserted to read `"example-first"`
and `""` on a bank carrying no directive.

**D5. `build_definition_first` writes three distinct filenames rather than
one.** Task 3 step 3 says the builder writes "a bank" and gains an `override`
keyword. Written with one filename, the tracer's three builds into one work
directory would overwrite each other, which is harmless today and is a trap the
moment a later scenario wants to compare two of them. Each override value gets
its own filename, and `DEFINITION_FIRST_FILENAMES` records the mapping.

## 11. Flagged assumptions carried forward

Both of the plan's flagged assumptions stand as written and are repeated here
so they are not rediscovered.

- **`data-required="1"` is a presentation marker only in this phase.** Nothing
  reads it. It exists so a guided-mode stager, a later accessibility review,
  and Phase 17A's visual system have a hook already carrying the author's
  intent rather than each inventing one. It reaches no runtime call and grants
  no authorization; plan 16A-09's adversarial suite is the place that asserts
  so.
- **CAP-01's unclassified probe row was a completeness question and is now
  answered.** Every one of the fourteen roles resolves to a module that imports
  and a mechanism that renders, and the "named in the requirement but absent
  from the registry" half is the unknown-semantic contract Task 2 built.

## 12. One edge case the plan does not name, recorded rather than decided

`> [!KEY!]` renders the generic key callout rather than the `[!KEY]` index
card. `_callout_kind_of` returns the literal `"KEY"` only for `KEY` and `KEY:`,
so `KEY!` misses that branch, falls to the required path, and resolves
`_callout_spec("KEY")`, which is the generic `("key", "Key point")` container.
No content uses it and no acceptance criterion covers it. It is recorded here
so a later phase that wants a required index card knows this is where to look
rather than discovering it as a surprise.
