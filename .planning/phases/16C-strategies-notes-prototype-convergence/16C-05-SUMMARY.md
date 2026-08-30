# 16C-05 summary

**Plan:** 16C-05, the composed precedence resolver.
**Executed:** 2026-08-29. **Tasks:** 2 of 2. **Files:** `strategies.py`,
`tests/strategy_precedence_roundtrip.py`, `tests/mode_layer_roundtrip.py`.

## Verification, with actual final lines

```
python3 tests/strategy_precedence_roundtrip.py  ->  STRATEGY PRECEDENCE: 5 passed, 0 failed  (exit 0)
python3 tests/strategy_registry_roundtrip.py    ->  STRATEGY REGISTRY: 5 passed, 0 failed    (exit 0)
python3 tests/mode_layer_roundtrip.py           ->  MODE LAYERS: 6 passed, 0 failed          (exit 0)
python3 itembank.py guard .                     ->  0 offending files
```

The mode-layer suite's check count is unchanged at six while its
`CONFLICT_CASES` grew by three rows, which is what the extension point was
shaped for: the rows are exercised by 16B's own machinery, and 16C added no
second enforcement.

`git diff --stat tests/mode_layer_roundtrip.py` reports 13 insertions and 0
deletions, all inside `CONFLICT_CASES` plus the one comment line. No existing
row, check body, or copy constant was touched.

No em dash character in any file this plan wrote.

## The collector

`composed_resolve(layers_state, sitting_active=False)` gathers each layer's
supplied state and calls `ia.mode_layer_resolve` per setting, in sorted key
order for determinism. It compares no layer names, reads no ordering, and
builds no sentence. `locked_picker_copy` turns the conflict entries into the
`locked_copy_by_id` mapping `picker_rows` takes, which closes the empty-copy
interim state plan 16C-03 recorded and asserts closed here.

Every case in the plan's behavior block passes, including the two the
resolver must NOT smooth over: an unknown layer key propagates
`ia.mode_layer_resolve`'s own `ValueError` un-re-worded, and the empty input
returns three empty containers rather than raising.

## The mid-sitting lock, and why it is a lock rather than a lost conflict

With `sitting_active=True` the learner-preference entry is removed BEFORE the
resolver sees it, so it does not lose a conflict, it never enters one. The
distinction is the point: a refused request that had been considered would
render as a conflict the learner might argue with, and the honest statement
is that the control is paused. The test asserts the locked call carries one
lock and zero conflicts, and that the same state with `sitting_active=False`
carries one conflict and zero locks.

Recorded both effective values, as the plan requires:
`mid-sitting: locked='continuous_reading' open='continuous_reading'`. The
value is the same by both routes and arrives by different ones, which is
exactly what makes the lock a disclosure rather than a behavior change.

## The structural check against a second implementation

`check_no_second_implementation` asserts three things, and it is the check
that matters most in this plan:

1. `composed_resolve`'s source contains no `MODE_LAYERS`, `MODE_LAYERS_FIXED`,
   `index(`, or `MODE_LAYER_CONFLICT_TEMPLATE`.
2. `strategies.py` defines no function or class whose name carries
   `mode_layer`, `layer_order`, `precedence_table`, or `precedence`, apart
   from `composed_resolve` and `locked_picker_copy` themselves.
3. The module source contains neither `is set by` nor `can't be changed
   here`, so the conflict sentence cannot be assembled here even by
   accident.

The failure messages name 16B D8 and D-16C-5, so a future author who trips
one is told which decision they are reopening rather than which assertion
they broke.

## Deviation: 16C-03's import assertion had to be narrowed

Plan 16C-03's acceptance criteria say `strategies.py` imports nothing from
`surfaces`, and its test asserted exactly that. Plan 16C-05 then requires
`from surfaces import ia` at module level. The two plans disagree, and the
disagreement is real rather than a misreading: 16C-03 was written before its
own successor added the import.

Resolved by narrowing rather than deleting the assertion.
`check_registry_shape` now collects every `surfaces.*` import and requires
the list to equal exactly `["surfaces.ia"]`. Allowing the `surfaces` package
as a whole would have let the exception cover imports nobody decided on;
allowing one dotted name keeps the tier rule enforced and records which
single exception was granted and why. `runtime`, `evidence`, and `notes`
remain refused outright.

The module docstring was updated in the same edit, since its old sentence
("the import list is the structural proof: standard library and nothing
else") had become untrue.

## Other deviations

- The `from surfaces import ia` import sits at the top of the module with
  `copy` rather than beside the 16C-05 code, which is where the plan's
  wording put it. A module-level import at the bottom of a file is the kind
  of thing a later reader deletes as a mistake.
- The plan's commands are written as `python`; this machine has only
  `python3`, the deviation `16C-PRECONDITION.md` records as item 3.
