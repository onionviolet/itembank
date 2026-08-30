# 16C-01 summary

**Plan:** 16C-01, the precondition check and the decisions file.
**Executed:** 2026-08-29. **Tasks:** 2 of 2. **Files outside `.planning/`
changed:** none.

## What this plan produced

Two planning artifacts and nothing else:
`16C-PRECONDITION.md` and `16C-DECISIONS.md`. No module, vocabulary, schema,
fixture, or test was created, and `notes.py`, `strategies.py`,
`note_outputs.py`, `progress_claims.py`, and `upgrade_audit.py` were confirmed
absent from disk at the end of the run.

## Task 1: the precondition result

Phases 14B, 16A, and 16B have landed. All eight dependency modules import. All
three freeze records carry their own `## Frozen at` heading and none carries
`## Freeze withheld`. All three upstream `*-PRECONDITION.md` dated result lines
state their phase may proceed, and 16B's two recorded deviations both carry
resolutions. Phase 13.9 is walked: `13.9-03-SUMMARY.md` exists.
`tests/evidence_roundtrip.py` and `tests/lesson_roundtrip.py` exit 0 and
`itembank.py guard .` reports `0 offending files`.

Which truth was verified by which command, with actual stdout, is recorded in
`16C-PRECONDITION.md`'s What was checked table and Dated result line. The
values are not repeated here.

### Deviations, quoted side by side

**1. `model.parse_lesson` returns sixteen keys, not the six the plan asserts.**
Plan text: `{'source', 'body', 'intro', 'headings', 'error', 'detail'}`,
asserted by set equality. Landed: those six plus `lang`, `lang_raw`, `dir`,
`dir_raw`, `dir_declared`, `gate`, `semantic_profile`, `semantic_profile_raw`,
`example_order`, `example_order_reason`. Added by `aa14114` (16A-02) and
`53dd3cf` (16A-03), both inside the frozen phase. A pure superset: every
planned key is present.

**This is the plan's halt condition, and it was obeyed rather than worked
around.** Step 11 rates a moved lesson surface a halt and forbids an executor
continuing on its own judgment. The wave stopped. The divergence was put to
Weibao with the halt option named and its cost stated (a re-read of nine plans
against three freeze records) alongside a scoped halt and a
reconcile-and-proceed option. He chose reconcile-and-proceed on 2026-08-29.
The reconciliation: the assertion becomes key presence, not key-set equality,
and every 16C plan reading `parse_lesson` reads by key and never by key count.
The one decision that reads it is D-16C-7. This mirrors
`16B-PRECONDITION.md`'s recorded-and-compared treatment of its own route and
settings counts.

**2. The 16B conflict copy carries `for this course`; plan 16C-01 step 4's
expected line does not.** Landed: `Timed test mode is set by your instructor's
policy for this course and can't be changed here.` Step 4 expected the same
sentence without `for this course`. The same plan's D-16C-5 locks the template
`{Setting name} is set by {higher layer name} for this course and can't be
changed here.`, which the landed string matches verbatim. So the plan
disagreed with itself and the landed code agrees with the half that binds.
Consequence for plans 16C-03 and 16C-05: read the copy from
`ia.mode_layer_conflict_copy`, never re-type it.

**3. `python3`, not `python`.** No `python` executable exists on this machine.
Every command was run with `python3` substituted and nothing else changed.
`16B-PRECONDITION.md` records the identical deviation.

### The additivity baseline

Five lines recorded in `16C-PRECONDITION.md`, taken before any file outside
`.planning/` was touched: three `path sha256` lines, the captured-view counts
`[40, 0]`, and the captured-view hash
`a9f88a0388669ae89a49b5d16d54c684e3d6d325af960a1c37d0521e29b492d7`. The `0` is
correct and is explained in the file so plan 16C-06 does not read it as a
broken baseline: `fixtures/lesson_retention_events.jsonl` holds one
`lesson_complete` and the `retraction` that compensates it, so
`capture_events` returns zero live events by design.

### The 16A shared-hook question

`16A-FREEZE.md` publishes the activity vocabularies (`model.ACTIVITY_COLUMNS`,
`ACTIVITY_PURPOSES`, `ACTIVITY_RETRY`, `ACTIVITY_FEEDBACK`,
`ACTIVITY_EVIDENCE_STATES`, and the `activity.*` lint codes) and states in its
own words that it is "Not a notes or strategy freeze. There is no learner-note
durable object." Recorded as `none published` for notes, with the activity
names recorded as the registration seam.

## Task 2: the checkpoint answer

**D-12.6-5, both halves, answered by Weibao on 2026-08-29: `option-c` and
`primary`.** Margin capture at the anchor inside Learn, review in the Notes
panel inside Evidence, cross-course global destination backburner, Evidence
beside Learn, Practice, and Test in primary navigation.

Both are the recommended default, so the consequence list is empty by design:
no plan edit, no module, schema, fixture, or test change follows. One docs
consequence is recorded and deliberately not executed, because this plan owns
no file outside its phase directory:
`.planning/DECISIONS-12.6-REMAINING-2026-08-14.md` D-12.6-5 still reads
`Resolved: pending` and may be updated by a later docs commit citing the
`## D-12.6-5` heading in `16C-DECISIONS.md`.

## Deviations from the plan itself

One, named above and recorded in the precondition file: the plan's step 8
command as literally written exits non-zero on this tree. The reconciled form
of that command, with the `parse_lesson` leg asserting key presence, is what
produced the recorded `shipped surface matches`. The failing raw output is
preserved in `16C-PRECONDITION.md` rather than replaced by the passing run.

Everything else ran as written. No em dash character appears in either
artifact, verified with the `chr(0x2014)` form the plan prescribes.

## What plans 16C-02 through 16C-09 must carry forward

1. Read `parse_lesson` by key, never by key count.
2. Read the mode-layer conflict copy from `ia.mode_layer_conflict_copy`, never
   re-typed, and note that D-16C-5's template is the correct one.
3. `16C-PRECONDITION.md`'s Deviations found section is non-empty, so read it
   before execution.
4. D-12.6-5 is answered; no plan needs editing for it, and 16C-09's freeze
   record carries the answer forward for Phase 17A.
