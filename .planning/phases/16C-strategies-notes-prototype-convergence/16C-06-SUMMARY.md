# 16C-06 summary

**Plan:** 16C-06, the note promotion contract, the learner artifact, and the
one additive evidence extension.
**Executed:** 2026-08-29. **Tasks:** 3 of 3. **Files:** `evidence.py`,
`notes.py`, `schemas/response.schema.json`,
`tests/note_promotion_roundtrip.py`.

## Verification, with actual final lines

```
python3 tests/note_promotion_roundtrip.py  ->  NOTE PROMOTION: 8 passed, 0 failed  (exit 0)
python3 tests/evidence_roundtrip.py        ->  exit 0
python3 tests/note_schema_roundtrip.py     ->  NOTE SCHEMA: 8 passed, 0 failed
python3 tests/lesson_roundtrip.py          ->  exit 0
python3 schema_validate.py --all schemas   ->  21 schema documents self-check clean
python3 itembank.py guard .                ->  0 offending files
```

`evidence.py` carries pre-existing em dash characters; every line this plan
added to it was checked separately and carries none. No other file this plan
wrote contains one.

## The one-way change, and its proof

`KNOWN_EVENT_TYPES` now holds sixteen members, the two new ones last, with
the plan-numbered comment. `git diff evidence.py` is one hunk: the comment
and the tuple. No schema-version bump, no new function, no reader change.

The additivity is proven against the baselines `16C-01` recorded BEFORE any
16C change existed, read out of `16C-PRECONDITION.md` by the test rather than
recomputed, because a re-recorded baseline would make the proof circular. All
five values match:

```
fixtures/selection_evidence.jsonl       55fd52b5...861ce   unchanged
fixtures/lesson_retention_events.jsonl  a9338eb7...a5f831  unchanged
schemas/settings.schema.json            b6e5b154...4edc2a  unchanged
captured view counts                    [40, 0]            unchanged
captured view hash                      a9f88a03...92d7    unchanged
```

The D-09 degrade path is re-proven in a subprocess: a log carrying
`"event_type": "not_a_type"` yields zero events from `evidence.events` and
warns with `unknown event_type` rather than failing, which is what makes a
later build's event type survivable for this one.

## A gap the plan missed, found by checking rather than trusting

**The two new event types failed the project's own published event schema.**
Plan 16C-06 names only `KNOWN_EVENT_TYPES`. But D-23's convention is that an
event type joins the tuple AND the schema enum in the same commit as its
builder, and `schemas/response.schema.json`'s `other_event` branch carries a
closed enum. A lifecycle event validated against that schema before the enum
was touched returned:

```
$: oneOf matched 0 of 7 branches (need exactly 1)
```

Registering the tuple alone would have shipped an event type the project's
own published contract rejects, into an append-only log, which is the one
category of mistake this phase's reversibility rating calls one-way.

Fixed by adding both members to the `other_event` enum with the reason
recorded in the schema's own description, and by adding
`check_event_schema_registration` to the test so the two lists cannot drift
apart again. They are accepted by the permissive branch rather than given a
closed one because the nine-key set is enforced in
`notes.strategy_lifecycle_event` and asserted in the test; a closed branch
would be a second place to keep that key set in step.

This is why the test count is eight rather than the plan's seven.

## The lifecycle event's closed key set

Exactly nine keys: `schema_version`, `event_id`, `event_type`, `ts`,
`session_id`, `strategy_id`, `action_state`, `note_ref`, `dedupe_key`. The
test asserts the set equality, asserts no key contains `wording`, `text`,
`content`, or `body`, and asserts no string value is long enough to be
content. An identical replay reports `already_recorded`; unknown event type,
strategy id, and action state each raise.

The event is appended through `evidence.append_event` and nothing else, the
`surfaces/migrate.py` precedent: the builder may live outside `evidence.py`,
the writer may not be duplicated.

## Promotion (NOTE-02)

Both gates hold with their exact sentences. Two unsupported claims out of
three produce `Every keyed or factual claim needs an accepted source. 2
claims have no accepted source yet.` A source conflict produces the conflict
sentence and no derived record at all.

Acceptance produces a NEW record with status `learner_accepted` and a
derivation edge naming the original revision id, and the learner's note is
asserted unchanged by deep-copy comparison before and after. Decline requires
a reason and produces `Not accepted: needs a citation. Your note is
unchanged.` A promotion with no named human reviewer raises.

A model may annotate: labeled generated synthesis rides on the derived record
and there is no code path from an annotation to an outcome.

**The unreviewed default is proven inert.** A second note, never submitted,
reads `private` with its exact badge, and is asserted absent from the derived
record's JSON and from an evidence log that does carry lifecycle facts for
the promoted one. Both its note id and its wording are searched for.

## The learner artifact (NOTE-03)

Pending with the exact badge and explainer. A `mark_proposal` adds the
proposal line and the state stays `pending`. `mark_event(marker="model")`
raises through the shipped gate, re-proven here at the artifact boundary. A
human mark settles it, and the three rubric criteria render as three separate
`met` / `not met` lines with no percent character and no `digit/digit` total
anywhere, which is GRAPH-03's no-aggregate rule applied locally.

`artifact_evidence_view` reads settlement only from mark events through
`evidence.marks_by_event`. It computes no verdict, because a second thing
that could decide whether an artifact passed would be a second settlement
mechanism.

## Deletion (D16)

The note leaves the sidecar, a tombstone carrying status `deleted` takes its
place so a referencing document reads a deletion rather than a gap, the
re-read document does not carry it, and the evidence log's bytes are
asserted byte-identical across the deletion. The confirmation copy is
verbatim and says what it cannot reach: copy promising total erasure would be
a promise this architecture cannot keep, and a learner who later found the
lifecycle facts would be right to distrust everything else it said.

## Deviations from the plan

1. **The schema enum**, described above. An addition the plan did not name
   and D-23 requires.
2. **Eight checks rather than seven**, because of 1.
3. **`promotion_state()` and `PROMOTION_OUTCOMES` exist as named helpers.**
   The plan implies the default-to-private read inline at call sites; naming
   it once means the badge, the gates, and 17A read one definition.
4. The plan's commands are written as `python`; this machine has only
   `python3`.
