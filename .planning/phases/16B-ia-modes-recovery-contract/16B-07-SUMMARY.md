# 16B-07 summary

Plan `16B-07`, wave 7, three tasks, all complete. All seven mode layers exist as
data, a lower layer never beats a higher one across all twenty-one ordered
pairs, and the settings page shows the two fixed layers as text with no control
that cannot take effect.

## Command output, final line of every verify block

| Command | Final line |
|---|---|
| `python3 tests/mode_layer_roundtrip.py` | `MODE LAYERS: 6 passed, 0 failed`, exit 0 |
| `python3 tests/theme_roundtrip.py` | exit 0 |
| `python3 tests/daemon_roundtrip.py` | exit 0 |
| `python3 -c "... print(len(ia.MODE_LAYER_ROWS), sum(...))"` | `7 2` |
| `python3 itembank.py guard .` | `0 offending files` |
| the whole suite, 85 files | `0 failing` |

## The theme_page baseline

Taken before any edit to `surfaces/theme.py`:

```
f198e3d7d15f7033d0fa028df13c3d7449eadce5ae77a0220dc43114925f799b
```

After adding the `sections` keyword argument, `theme.theme_page(cfg)` with no
`sections` argument hashes to the identical value. The literal is written into
`tests/mode_layer_roundtrip.py` as `THEME_PAGE_BASELINE` with the date and the
producing command in a comment, so an unrelated drift is named rather than
hidden.

```
git diff --stat surfaces/theme.py
 surfaces/theme.py | 9 +++++++--
 1 file changed, 7 insertions(+), 2 deletions(-)
```

One keyword argument, three docstring lines, and one `body + sections`
concatenation. `surfaces/theme.py` gained no import of `surfaces.ia`; the
markup is built in `surfaces/daemon.py` and passed in already escaped.

## Deviations from this plan, with reasons

**1. The conflict sentence keeps "for this course", so it differs from the
literal string in this plan's acceptance criterion.** `16B-UI-SPEC.md` states
the sentence twice and the two disagree. Its Mode-Layer Precedence Contract
point 2 gives the template as "{Setting name} is set by {higher layer name} for
this course and can't be changed here." and then illustrates it with an example
that drops "for this course". Its Copywriting Contract row repeats the template
including the phrase.

The template is taken as binding, because `16B-01-PLAN.md` names the Copywriting
Contract as "the binding source for every user-visible string in this phase" and
it agrees with point 2's own template against point 2's own example. This plan
told this task to implement `MODE_LAYER_CONFLICT_TEMPLATE` with the phrase and
then to assert the example without it, which cannot both hold. The shipped
sentence is:

```
Timed test mode is set by your instructor's policy for this course and can't be changed here.
```

Recorded in `16B-DECISIONS.md` under `## Recorded discrepancy: the mode-layer
conflict sentence`, so a reviewer sees the choice rather than discovering the
mismatch. The tests assert against `mode_layer_conflict_copy` and the template
rather than against a hand-copied literal, so the copy has exactly one source.

**2. `check_conflict_fixture` and `check_theme_page_unchanged_by_default` are
separate checks, giving six rather than the plan's stated running totals of 3,
5, and 6.** The final count matches; the intermediate counts in Tasks 1 and 2
assumed a different grouping. `MODE LAYERS: 6 passed, 0 failed`.

**3. The `conflict` rule is "any lower layer supplied a differing value",
which is the plan's second, more precise formulation.** The plan gave two: a
looser one keyed on key count and position, and then "more precisely, True when
at least one lower-indexed layer also supplied a request whose value differs
from the winning value". The precise one is implemented, so two layers that
happen to agree do not report a conflict and therefore emit no refusal sentence
about a control nobody was refused.

**4. `python3` for `python`, and the full-suite criterion run with
`ANKI_CONNECT_URL=http://127.0.0.1:1/`.** Carried forward from
`16B-02-SUMMARY.md`.

## Which truth was verified by which command

| Truth | Command | Actual result |
|---|---|---|
| Seven layers in one order, last two fixed | `check_layer_table_shape` | 7 rows, order equals `MODE_LAYERS`, fixed at indices 5 and 6 |
| `mode_layer_rows()` cannot be used to mutate the constant | same check | mutating a returned dict left `MODE_LAYER_ROWS` unchanged |
| Instructor policy beats learner preference with the locked sentence | `check_instructor_beats_preference` | winner `instructor_policy`, exact copy |
| A single request is not a conflict | same check | `conflict` False, `copy` empty |
| The empty mapping raises nothing | same check | fully-shaped result, `value` None |
| An unknown layer is refused by name | same check | `ValueError` naming `not_a_layer` |
| Every ordered pair resolves upward | `check_fixed_layers_always_win` | 21 pairs, all to the higher layer |
| A fixed layer never loses | same check, plus `check_conflict_fixture` | cases 2, 4, 5 assert it and name non-negotiable number 1 |
| All seven layers are visible in settings | `check_fixed_rows_are_read_only` | 7 labels and 7 controllers in the served page |
| No affordance that cannot take effect | same check | none of `<input`, `<select`, `<button`, `<textarea`, `contenteditable`, `<form` inside the disclosure |
| The shipped Theme section survived | same check | `data-section="theme"` present |
| No shipped caller moved | `check_theme_page_unchanged_by_default` | hash equals the pre-edit baseline |
| The copy leaks no internal key | `check_conflict_fixture` | no layer key and no underscore in any of the six |
| 16C's collector is absent from 16B | same check | none of `collect_mode_layers`, `live_mode_state`, `mode_layer_state` |
| The resolver reads only its arguments | same check | no `import ` and no `open(` in its source |

## Artifacts changed

- `surfaces/ia.py`: `_MODE_LAYER_TEXT`, `MODE_LAYER_ROWS`,
  `MODE_LAYER_FIXED_HEADING`, `MODE_LAYER_CONFLICT_TEMPLATE`,
  `MODE_LAYER_DISPLAY_PHRASES`, `mode_layer_rows`, `mode_layer_conflict_copy`,
  `mode_layer_resolve`.
- `surfaces/theme.py`: the `sections=""` keyword argument, three docstring
  lines, and `body + sections`. No new import.
- `surfaces/daemon.py`: `_mode_layer_section` and one changed call in
  `handle_settings_get`.
- `tests/mode_layer_roundtrip.py`, new: `THEME_PAGE_BASELINE`,
  `CONFLICT_CASES`, `AUTHORITY_CASES`, and six checks.
- `16B-DECISIONS.md`: `## D-16B-12. What 16B ships of the mode-layer contract
  and what 16C ships`, and `## Recorded discrepancy: the mode-layer conflict
  sentence`.
