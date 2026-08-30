# 16C-03 summary

**Plan:** 16C-03, the strategy registry and the picker row contract.
**Executed:** 2026-08-29. **Tasks:** 2 of 2. **Files:** `strategies.py`,
`tests/strategy_registry_roundtrip.py`.

## Verification, with actual final lines

```
python3 tests/strategy_registry_roundtrip.py  ->  STRATEGY REGISTRY: 5 passed, 0 failed   (exit 0)
python3 itembank.py guard .                   ->  0 offending files
```

No em dash character in either file, verified with the `chr(0x2014)` form.

## The eleven contract keys, as shipped

Every one of the four contracts carries exactly
`strategy_id`, `version`, `learning_purpose`, `eligibility`,
`required_actions`, `optional_actions`, `skip_resume`, `evidence_effects`,
`accommodations`, `offline_behavior`, `tests`, held in one module tuple
`CONTRACT_KEYS` so the completeness check reads one source rather than a
retyped list.

| Strategy | Required actions | Optional | Evidence effects | Tests named |
|---|---|---|---|---|
| `continuous_reading` | none | `highlight`, `add_note` | `activity_completed` | registry |
| `guided_note_spine` | `select_target`, `restate_in_own_words` | `add_question` | both | registry, trio |
| `worked_reasoning` | `predict_next_step`, `explain_step`, `self_check` | none | both | registry, trio |
| `retrieval_first` | `attempt_items_first` | `read_after` | both | registry |

Every `evidence_effects` member is one of the two D-16C-1 lifecycle types,
asserted per strategy rather than per registry. Empty values are refused for
every field except `required_actions` and `optional_actions`, which are
legitimately empty for a strategy that asks nothing of the learner:
`continuous_reading` requires no action, which is what makes it usable as the
fallback.

## Every fallback case exercised

| Case | Requested | Result |
|---|---|---|
| unavailable | `worked_reasoning`, available `("continuous_reading",)` | `continuous_reading` |
| disallowed | `retrieval_first`, allowed without it | `continuous_reading` |
| unknown | `not_a_strategy` | `continuous_reading` |
| allowed and available | `guided_note_spine` | `guided_note_spine` |
| empty availability | `guided_note_spine`, available `()` | `continuous_reading` |

None raised. The empty-availability row is one case beyond the plan's
behavior block, added because "nothing is available at all" is the state a
degraded install actually reaches and the fallback has to survive it.

Additionally, every member of `STRATEGY_IDS` resolved to itself under a fully
permissive call, so the fallback is not swallowing valid requests.

## The picker

Three row classes and no fourth. Asserted: registry order preserved; a fully
available registry yields four choosable rows with only the first
preselected; an unavailable `worked_reasoning` renders `fallback` with the
sentence `Worked reasoning isn't available right now. Continuing with
continuous reading.` and moves preselection to `continuous_reading`; a
disallowed `retrieval_first` renders `locked` carrying the supplied 16B
sentence verbatim and is never preselected; a disallowed strategy with no
sentence supplied is still shown rather than hidden (D8); and a bogus
`close_reading` passed inside `available` never becomes a row.

The locked sentence is an argument, never a lookup. `ia.mode_layer_conflict_copy`
is the single source of that string and plan 16C-05's composed resolver is
the only caller allowed to produce it, so this module cannot re-type it even
by accident.

## Copy checked verbatim

`PICKER_HEADING`, `UNAVAILABLE_COPY`, `MID_SITTING_LOCK_COPY`,
`STRATEGY_NAMES`, and `STRATEGY_PURPOSES` are each compared to the UI-SPEC
string written out in the test, not to the module comparing to itself. A
silent edit on either side fails.

## Tier rule

`strategies.py` imports `copy` and nothing else. The test asserts over the
module's own source with `ast`, module-level and function-level imports both,
that it reaches neither `runtime`, `evidence`, `notes`, nor any surface.

## Deviations from the plan

Two, both additive and neither changing a contract:

1. **`LIFECYCLE_EVENT_TYPES` and `CONTRACT_KEYS` exist as module constants.**
   The plan describes both as inline lists inside the contracts and the
   test. Naming them once means plan 16C-06's event builder and 16C-09's
   tracer can import the vocabulary rather than retype it, which is the same
   reason D-16C-8's vocabularies are constants.
2. **One extra fallback case** (empty availability), named above.

The plan's commands are written as `python`; this machine has only `python3`,
the deviation `16C-PRECONDITION.md` records as item 3.
