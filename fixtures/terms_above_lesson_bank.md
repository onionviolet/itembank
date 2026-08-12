# Preamble section ordering (synthetic)

Fully invented content for the preamble-section boundary check. It is not
derived from any real course, exam, or textbook, and every term, source,
case and item below exists only to exercise the parser.

The section order here is deliberate: `## TERMS`, `## SOURCES` and
`## CASES` all sit ABOVE `## LESSON`, and the lesson body carries a
markdown table. A preamble section that scans to the end of the preamble
instead of stopping at the next `##` heading reads those table rows as
glossary entries, sources and cases.

## TERMS

Widget | A small invented thing this fixture uses to test slugging | Gadget
Sprocket | A second invented thing, also fixture-only

A term row inside a fenced block is sample markup an author is showing, not
a row of the section:

```text
Fencepost | This row lives inside a fence and is not a term
```

## SOURCES

fixture-note | Invented fixture note, page 1

## CASES

fixture-case | An invented scenario used only by this fixture

## LESSON

### Ordering Probe

Prose before the table. The lesson names [[Widget]] and [[Sprocket]].

| Step | What it does |
|------|--------------|
| Alpha | The first invented step |
| Beta | The second invented step |
| WIDGET | The third invented step, shouted for emphasis |

More prose after the table, so the section does not end at the table.

Q1. Which invented thing does this fixture name first?   (difficulty: recall)
[LESSON-REF: ordering-probe]
[OBJECTIVE: emt:airway]
A) Widget
B) Sprocket
C) Alpha
D) Beta

CORRECT: A

WHY BEST: Widget is the first term row in the fixture's TERMS section.

KEY DISCRIMINATOR: Term rows versus lesson table rows.

SECOND-BEST: B. Sprocket is the runner-up; this would be correct if the
question asked which thing the fixture names second.

DISTRACTOR ANALYSIS:
- A) Correct: the keyed answer.
- B) The runner-up; this would be correct if the question asked which thing
  the fixture names second.
- C) A lesson table row, not a term; this would be correct if the question
  asked for the first step in the table.
- D) A lesson table row, not a term; this would be correct if the question
  asked for the second step in the table.

TRAP: Reading a lesson table row as a glossary term.

CONFIDENCE: high
