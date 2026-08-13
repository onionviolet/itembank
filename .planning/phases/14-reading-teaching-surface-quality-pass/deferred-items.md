# Deferred items — Phase 14

Out-of-scope discoveries logged during execution. Not fixed here.

## `surfaces/settings.THIS_PHASE` is stale at 10 (found during plan 14-03, Task 1)

`THIS_PHASE = 10` decides the STATUS column of `itembank config`: a key whose
`x-itembank-phase` is above it prints `inert -- read from phase N`. The new
`teaching` group carries `x-itembank-phase: 14` (correct — phase 14's own
`do_teach` reads `teaching.hint_locked_preview`), so both rows print as inert
while they are in fact read.

This is pre-existing rather than introduced here: `auditor_autonomy` sits at
phase 11 and prints as inert today, and `tests/config_roundtrip.py`'s
`test_config_no_args_prints_table` asserts exactly that. Bumping `THIS_PHASE`
therefore means editing that assertion and re-deciding which keys are genuinely
inert across phases 11–14 — a settings-surface change, not a teaching-route
change, and outside plan 14-03's file set and objective.

**Fix when touched:** raise `THIS_PHASE` to the current phase number and
re-derive `test_config_no_args_prints_table` / `test_phase_10_keys_read_not_inert`
against the real per-phase reader inventory. Note that
`test_phase_10_keys_read_not_inert` is defined in `tests/config_roundtrip.py`
but is not called from its `main()`, so it runs nowhere today.
