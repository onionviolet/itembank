# Phase 14B authorability review

One of the three legs of the Phase 14B freeze gate. The machine half is
green. The human half is Weibao's and is deliberately left blank below: an
agent never self-certifies this class of judgment.

## What is being reviewed

The `course-graph.md` sidecar and the outline projection for one domain of
the synthetic three-domain corpus, `meridian-field-response`, titled
"Meridian Field Response". It is fictional and generated, so nothing real is
being read here.

Both files were written outside this repository, so the corpus never enters
committed content:

- `/var/folders/zg/7y5nnphj6bd6bcxgm4tmgv280000gn/T/itembank-14B-authorability/course-graph.md`
- `/var/folders/zg/7y5nnphj6bd6bcxgm4tmgv280000gn/T/itembank-14B-authorability/outline.md`

They are in the system temp directory and a reboot may remove them.
Regenerating them takes one command: run `python3 tests/three_domain_tracer.py`
for the assertions, or rebuild the pair with `fixtures.corpus_14b.build_all`
and `graph.outline_projection`.

## The machine half, already green

From `scenario_authorability_roundtrip()` in `tests/three_domain_tracer.py`,
run on 2026-08-27 on Darwin arm64:

```
authorability one cell hand edit: 1 line changed, reordering reached the projection, longest sidecar line 126 characters
```

```
TRACER: 5 passed, 0 skipped, 0 failed
```

What those assertions actually check:

- **The one-line diff.** One `order` cell in the `## Structure` table is
  changed by a string replacement on the file text, the text is parsed, and
  the document is serialized again. The diff against the original is exactly
  one line removed and one line added. Reordering two containers by hand costs
  one line of diff, not a rewritten file.
- **The reordering round trip.** The re-projected outline reflects the edit:
  the container whose `order` cell was changed is first in the new outline,
  and the outline heading sequence differs from the one before the edit.
- **The maximum line length.** The longest line in the sidecar is 126
  characters, under the 200-character assertion, so a table row stays readable
  in a plain editor without horizontal scrolling that defeats reading.

## The five questions for the human

1. Open `course-graph.md` in a plain text editor. Without any tool, can you
   say what this course contains?

   
2. Open the same file in Obsidian. Do the tables render, and is the file still
   readable?

   
3. Reorder two chapters by editing one `order` cell by hand and save. Does the
   re-projected outline reflect your edit?

   
4. Open the outline. Is it something you would be willing to read and edit as
   a course plan, or only something a tool produces?

   
5. Is there any field in the sidecar whose meaning you cannot work out from
   the file alone?

   

## What a failure means

A No to question 1, 2, or 5 fails this leg of the freeze gate.
`14B-RESEARCH.md` Pitfall 8 names an unreadable sidecar as an outright gate
failure and not a nice-to-have, and D-14A-1's own text requires the sidecar
never to become the only readable copy of anything it records. A file that
needs this tool to be understood has already broken that rule, whatever its
tests say. Questions 3 and 4 are weaker signals: a No there records a real
problem worth fixing but is a judgment call about copy and layout, which this
phase's freeze deliberately leaves changeable.

## Accessibility scope note

Phase 14B introduces no learner-facing surface: no CLI command, no daemon
route, no rendered page. The nine accessibility gates in
`.planning/UI-SPEC.md` section 8 are therefore not exercised by this phase and
are not claimed as passed. This review is a plain-file readability judgment
about whether a human can open and edit a Markdown sidecar, and it is not an
accessibility certification of anything.

## Sign-off

Left blank by the agent, on purpose. `OPERATION-CONTRACT.md` states that an
agent never self-certifies this class of judgment, so the line below is
Weibao's to write and nobody else's.

**Date:**

**Verdict (write exactly `authorable` or exactly `not authorable`):**

**Notes:**

### Status as of 2026-08-27

Unsigned. Plan 14B-06 Task 4 was run on this date with this section blank, so
the authorability leg of the freeze gate is not green, and `14B-FREEZE.md`
records a withheld freeze naming this as the missing leg. Filling in the
verdict above and re-running Task 4 is what closes it.
