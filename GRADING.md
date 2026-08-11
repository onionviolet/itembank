# Grading an attempt

`itembank start`/`next`/`submit` write every response as one event in
`_evidence/evidence.jsonl`. Selected-response items are auto-marked in that
event. Short-answer items are not, and cannot be: matching keywords cannot
tell a correct explanation from a confident wrong one that happens to
contain the right nouns. Somebody marks those, and the mark is recorded the
same way the response was: as a timestamped event, not a hand edit.

This file is the instruction set for whoever marks. It is written so that
any capable model, or the person who sat the quiz, can do it from a cold
start with no other context.

## The attempt file is generated, not edited

`itembank render attempt --session SESSION_ID --bank BANK.md` prints (or,
with `--out FILE`, writes) the attempt markdown for one session, rebuilt
fresh from `_evidence/evidence.jsonl` every time it runs. Per item it shows
the stem, what was answered, and for `short` items the model answer from
the bank, the rubric points, and a `MARK:` line reporting `pending` or the
recorded verdict.

**Editing this file changes nothing.** It is a view over the log, not a
store; the next render replaces it byte for byte from the log alone,
whatever you wrote into it in the meantime. If you find yourself reaching
for an editor to grade an item, that is the signal you want `itembank mark`
instead, below.

## What you are handed

For a `short` item: the stem, the answer text verbatim (typos included —
leave it that way), the model answer from the bank, and the rubric points.

## The procedure

1. **Read the answer before the model answer.** Reading the model first
   makes everything look close enough to it. Form your own verdict, then
   compare.
2. **Check each rubric point independently.** A point passes only if the
   answer actually contains it. An answer that implies a point without
   stating it fails that point, because the exam this is preparing for
   cannot read intent either.
3. **Record one verdict: PASS or FAIL.** Dichotomous, matching the rest of
   the tool (see "The scoring rule" below). Write one sentence — for
   `--notes` — naming the single most important thing that was missing or
   wrong. Not a paragraph. The sentence is what gets reread later.
4. **Never rewrite the answer.** If it is wrong, say what is wrong and why
   in `--notes`. The person fixes it themselves. This is a measurement, not
   an editing pass.
5. **Name the misconception, not just the error.** "Said the interpreter
   prints the value" is an error. "Treats the REPL echo as something Python
   does rather than something the prompt does" is the misconception, and it
   is the thing that will reappear on a different question.

## Recording the verdict: `itembank mark`

A mark is a timestamped event appended to `_evidence/evidence.jsonl`
alongside the response it grades — never a line edited into a file, and
never a change to the response event itself (its `score` stays `null`
forever; what changes is that a live mark now exists for it). The command
accepts a batch, because marking twenty short answers as twenty separate
invocations is a workflow regression, not a grading pass.

**Marking a batch from an NDJSON file** — one JSON object per line, each
naming the item and the verdict:

```
{"item_ref": "q6", "verdict": true, "rubric": [{"point": "Names the primary/secondary split as health-based versus aesthetic", "pass": true}, {"point": "States that secondary standards are guidelines rather than enforceable limits", "pass": true}, {"point": "Points the investigation at specific aesthetic parameters", "pass": false}], "notes": "Named the split and the guideline distinction but never named a specific parameter to investigate."}
```

Three worked marks in one call:

```
itembank mark --session SESSION_ID --file marks.ndjson
```

`--file -` reads the batch from stdin instead of a path. The command
prints one JSON result naming, per entry, whether it was newly `recorded`
or `already_recorded` (an identical re-run of the same batch dedupes
rather than double-recording), plus a closing `N recorded, N already
recorded` status line.

**Marking one answer**, the convenience form for a single verdict with no
rubric detail:

```
itembank mark --session SESSION_ID --item q6 --verdict pass
```

(`--verdict` is `pass` or `fail`.) `--marks` takes the same shape as the
NDJSON file but as one inline JSON array, for a caller building the batch
in memory rather than as a file.

**A rubric entry** is `{"point": "<the rubric text, verbatim from the
bank>", "pass": true|false}` — one entry per point, every point in the
bank's `RUBRIC:` list, so the recorded mark says exactly which claims the
answer made and which it did not.

**Correcting a mark:** mark the same `item_ref` again with the verdict (and
rubric) you actually meant. The most recent live mark is the one every
render uses; the earlier one stays in the log, unmutated, for the record.

**Undoing a mark:** `itembank retract EVENT_ID --reason "..."`, the same
compensating-append undo used for a response. The `event_id` of the mark
you want to undo is in `itembank mark`'s own JSON output (`marks_event`'s
sibling field, `event_id`) or in a rendered attempt file's `MARK:` line.
Retracting the most recent mark makes the render show whichever mark is
now the most recent live one — the original verdict, if there was one.

## The scoring rule

Dichotomous, matching the rest of the tool. PARTIAL, if you find yourself
reaching for it, exists to describe the answer in `--notes`, not to award
half a mark. A partially correct answer does not pass the item, because a
half mark hides exactly the gap the item was written to find.

## A model's verdict is a pending proposal until a human settles it

A model can read a rubric and propose a verdict — `itembank rubric-review`
requests per-point suggestions for the current `short` response. The proposal
is recorded as a `mark_proposal` event: timestamped, first-class, and
**pending**. It is never accepted as evidence. A mark becomes a settled fact
only when a human accepts the proposal (`itembank mark --proposal
EVENT_ID --verdict pass|fail`), and the recorded mark always carries
`marker: "human"` — the `proposal_ref` on the mark links it to the exact
proposal it accepted (D-14/D-24). `itembank mark` rejects any other marker
outright, so a model cannot record a verdict for itself; a model suggestion
is something you read and accept or replace, never something that records
itself.

## What to do with the result

Whatever workflow the attempt belongs to owns that. Two conventions that
travel:

- **Every failed item is a candidate flashcard**, and the card is the
  discriminator, not the question. Card the distinction that was missed.
- **A repeated miss on the same misconception across two sittings is a
  signal about the teaching, not about the person.** Fix the source
  material.

## If you are the one who sat it

Self-marking is worse than being marked, because you know what you meant to
write and will read it into what you actually wrote. Two ways to blunt
that: mark it at least a day later, and mark strictly against the rubric
wording rather than against your memory of your intent. If a point is
arguable, it fails.
