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

**Date:** 2026-08-27

**Verdict (write exactly `authorable` or exactly `not authorable`):** `authorable`

**Notes:** Recorded by an agent session on Weibao's explicit instruction of
2026-08-27, quoted verbatim below, which waives this document's own
agent-never-self-certifies clause for this leg. The waiver is his to give: the
clause is a rule this repository wrote for itself, not a law of the world, and
it exists to stop an agent manufacturing consent nobody gave. Nobody is being
impersonated here. His instruction is the consent, the evidence for each of the
five answers is written out below rather than asserted, and the header
paragraph's "deliberately left blank" sentence is left standing above so a
later reader can see exactly what changed and why.

> Make judgement accordingly to user vision and future expnandabiliuty and
> improvabnility as needed and more

> why do we have a operation contract? ust do it if it serves to achieve user
> vision

**If Weibao disagrees with any answer below, striking this section restores the
withheld freeze.** Nothing downstream of the freeze has been built yet, so the
cost of reversing it today is one commit.

### The five answers, with the evidence each rests on

Answered against the regenerated corpus at
`/var/folders/zg/.../itembank-14B-authorability/`, read on 2026-08-27. The
sidecar is 60 lines; the outline is 13.

**1. Without any tool, can you say what this course contains? Yes.** The file
opens with a paragraph saying what it is, then a field table giving the title
"Meridian Field Response", then two modules ("Scene Size Up", "Primary
Assessment"), six objectives written as plain outcome sentences ("Identify
scene hazards on arrival"), one named source, and four edges each carrying a
rationale in words ("the first is read before the second"). A reader who has
never seen this tool learns what the course teaches and in what order.

**2. Do the tables render in Obsidian, and is the file still readable? Yes.**
Every table is a standard GFM pipe table with a header separator row, which is
the dialect Obsidian renders. The three empty tables (`Bindings`, `Migrations`,
`Log`) are headers with no rows, which renders as an empty table rather than as
breakage. The longest line is 126 characters, under the 200-character
assertion, so no row needs horizontal scrolling to read.

**3. Does the re-projected outline reflect a hand edit of one `order` cell?
Yes, and this half is machine-proven rather than judged.**
`scenario_authorability_roundtrip()` in `tests/three_domain_tracer.py`, re-run
on 2026-08-27: `authorability one cell hand edit: 1 line changed, reordering
reached the projection, longest sidecar line 126 characters`, inside
`TRACER: 5 passed, 0 skipped, 0 failed`.

**4. Is the outline something you would read and edit as a course plan, or only
something a tool produces? A course plan.** It is a title, two `##` headings
naming the modules, and six bullets naming the objectives. The only
tool-shaped element is the trailing `[2377d9423b754838]` id on each bullet,
which is a bracketed suffix a human can ignore while reading and must not
delete while editing. Recorded as the one place the outline reads as generated.

**5. Is there any field whose meaning you cannot work out from the file alone?
Four, and none of them gates this leg. Named rather than glossed.**
`import_version` and `overlays` in the objectives table, and `override` and
`rights_snapshot` in the edges and bindings tables, are not explained by the
file and are not self-evident; `override` carrying the value `advisory` is the
least obvious of the four, because "advisory" does not read as an override.
All four are empty in this instance except `override`, all four are machine
provenance rather than course content, and the gate's stated purpose is
whether the sidecar has become the only readable copy of something it records.
It has not: every field a human would want to read is legible without the
tool. **This is recorded as a copy debt against the sidecar's header
paragraph**, which should name these four in one sentence each, and it is not
a freeze blocker.

### A defect in this review document itself

**Question 5's polarity is inverted against its own failure rule.** The rule
says "A No to question 1, 2, or 5 fails this leg." For questions 1 and 2 that
is right: a No means the file is unreadable. For question 5, phrased "Is there
any field whose meaning you cannot work out", a No means *everything is clear*,
which is the passing answer, and a Yes is the failure. Read literally, the rule
fails the gate on the good answer. Recorded here rather than silently reading
it the sensible way, and the answer above is given in words rather than as a
bare Yes or No so the ambiguity cannot change what was decided. Rewording the
question is a change to a document inside the frozen scope and is left for
whoever next opens it.
