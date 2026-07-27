# Grading an attempt file

`itembank serve` writes one markdown file per sitting. Selected-response items
are already marked in it. Short-answer items are not, and cannot be: matching
keywords cannot tell a correct explanation from a confident wrong one that
happens to contain the right nouns. Somebody marks those.

This file is the instruction set for whoever does. It is written so that any
capable model, or the person who sat the quiz, can do it from a cold start with
no other context.

## What you are handed

An attempt file with, per item: the stem, what was answered, and for short items
the model answer from the bank, the rubric points, and a `MARK: (unmarked)`
line. The answer text is verbatim, typos included. Leave it that way.

## The procedure

1. **Read the answer before the model answer.** Reading the model first makes
   everything look close enough to it. Form your own verdict, then compare.
2. **Mark each rubric point independently**, replacing `(unmarked)` with
   `(pass)` or `(fail)`. A point passes only if the answer actually contains it.
   An answer that implies a point without stating it fails that point, because
   the exam this is preparing for cannot read intent either.
3. **Write the verdict on the `MARK:` line**: `PASS`, `PARTIAL`, or `FAIL`, then
   one sentence naming the single most important thing that was missing or
   wrong. Not a paragraph. The sentence is what gets reread later.
4. **Never rewrite the answer.** If it is wrong, say what is wrong and why. The
   person fixes it themselves. This is a measurement, not an editing pass.
5. **Name the misconception, not just the error.** "Said the interpreter prints
   the value" is an error. "Treats the REPL echo as something Python does rather
   than something the prompt does" is the misconception, and it is the thing
   that will reappear on a different question.

## The scoring rule

Dichotomous, matching the rest of the tool. `PARTIAL` exists to describe the
answer, not to award half a mark. A partially correct answer does not pass the
item, because a half mark hides exactly the gap the item was written to find.

## What to do with the result

Whatever workflow the attempt belongs to owns that. Two conventions that travel:

- **Every failed item is a candidate flashcard**, and the card is the
  discriminator, not the question. Card the distinction that was missed.
- **A repeated miss on the same misconception across two sittings is a signal
  about the teaching, not about the person.** Fix the source material.

## If you are the one who sat it

Self-marking is worse than being marked, because you know what you meant to
write and will read it into what you actually wrote. Two ways to blunt that:
mark it at least a day later, and mark strictly against the rubric wording
rather than against your memory of your intent. If a point is arguable, it fails.
