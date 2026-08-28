#!/usr/bin/env python3
"""The Phase 16A stress-corpus generator (plan 16A-02 Task 1).

Every string in this file is fictional. Nothing here is a real course, a real
exam, a real syllabus, a real learner note, or a real question bank, and
nothing here is derived from or paraphrased out of any such material. The tide
table, the station name, the objective key, and every option and rationale
were invented to exercise the lesson grammar, and their only relationship to
real teaching material is their shape.

Standard library only and directly importable, following
`fixtures/grandchild_spawner.py`'s module shape: module-level functions, no
class, nothing that runs on import.

Determinism here is a literal rather than a seed. `THIN_SLICE_BANK` is a
module-level constant string, so two builds into two directories produce two
byte-identical files without a random module being involved at all, and a
diff of this file is a diff of the corpus.
"""
import os


THIN_SLICE_BANK = """# Reading a tide table (synthetic)

Fully invented teaching content for exercising the Phase 16A semantic and
capability grammar. It is not derived from any real course, exam, textbook, or
tide publication, and no real question bank belongs in this repository.

[SEMANTIC-PROFILE: 1]
[LESSON-LANG: en]
[LESSON-DIR: ltr]

## LESSON

### Reading A Tide Table

> [!PREREQUISITE]
> You can read a two column table and add whole numbers.

A tide table is a list of times paired with heights. Each row names a moment
when the water reaches a turning point, and the height beside it says how far
above or below the chart datum the water sits at that moment. Nothing in the
table describes the water between two rows, which is the most common thing a
first reader assumes it does.

> [!EXAMPLE]
> At the fictional station Kestrel Point, the table lists a high water at
> 04:12 and the next low water at 10:38. Those two rows say nothing about
> 07:00; they say only where the turning points fall.

Because the rows are turning points, the useful question is almost never what
the table says at a listed time. It is which pair of rows a moment falls
between, and which direction the water is moving across that interval.

Q1. A tide table for Kestrel Point lists a high water at 04:12 and a low water at 10:38. What does the table tell you about the water at 07:00?   (difficulty: application)
[LESSON-REF: Reading A Tide Table]
[OBJECTIVE: nav:tides]

A) The exact height of the water at 07:00
B) That the water is falling between two listed turning points
C) That the water is at its lowest point of the day
D) That no reading was taken at 07:00

CORRECT: B

WHY BEST: 07:00 falls between a listed high water and the next listed low
water, so the only thing the table establishes is the direction of travel
across that interval.

KEY DISCRIMINATOR: The answer must describe what two turning points imply
about the interval between them, not what happens at a listed row.

SECOND-BEST: A. The table does fix heights at its own rows, and this would be
correct if the question asked about 04:12 rather than about 07:00.

DISTRACTOR ANALYSIS:
- A) The table gives heights only at its listed turning points; this would be correct if the question named a listed time.
- B) Correct: 07:00 sits between a high water and the following low water, so the water is falling.
- C) The lowest listed point is 10:38, not 07:00; this would be correct if the question asked which row is the low water.
- D) A gap between rows is not a missing observation; this would be correct if the table were a log of readings rather than a table of turning points.

TRAP: Reading a table of turning points as though it were a continuous record,
and expecting a height for every clock time.

CONFIDENCE: high
"""

THIN_SLICE_FILENAME = "capability_thin_slice_bank.md"


def build_thin_slice(dest_dir):
    """Write the one thin-slice bank into `dest_dir` and return its absolute
    path. Writing it twice into the same directory, or into two directories,
    produces byte-identical content."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(os.path.abspath(dest_dir), THIN_SLICE_FILENAME)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(THIN_SLICE_BANK)
    return path
