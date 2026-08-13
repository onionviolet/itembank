---
name: curriculum-design
description: Design a source-grounded course from a syllabus, standards, exam blueprint, or outline: extract objectives and prerequisites, align sources and existing artifacts, choose learning treatments, create an assessment blueprint, identify cited gaps, and propose what to build next.
---

# Design a source-grounded curriculum

Read `.planning/AGENT-WORKFLOW.md` before acting. Curriculum structure is a
versioned typed graph with familiar outline projections, not a universal tree.
Keep coverage, completion, evidence, retention, staleness, and uncertainty as
separate state axes. Preserve every viable alternative path or treatment with a
durable disposition.

Turn the target into a course plan: objectives, prerequisites, source support,
learning treatment, assessment demand, existing artifacts, and visible gaps.
The tool measures current bank coverage objectively; source alignment and
prerequisite claims require citations and stated confidence.

## 1. Get the ground truth

```bash
python itembank.py spec     # the format contract (objective naming, lesson refs)
```

Also inspect what already exists:

```bash
python itembank.py stats bank.md       # objective coverage of one bank (stats takes one bank)
```

`stats` prints the item mix, distinct objectives with item counts, difficulty
spread, and answer-position skew. Use it before and after you propose work.

For the objective-level map with citations, use the on-demand coverage map
(D-12), computed from the bank and its `## SOURCES` registry at request
time, never stored:

```bash
python itembank.py coverage bank.md       # objective -> item tags, citation-backed
```

`stats` is the item-mix/position report; `coverage` is the objective→items
map tied to the bank's `## SOURCES` registry (the sources each objective's
items cite).

## 2. Extract the objectives

From the syllabus, list every objective as a stable, hierarchical name the
bank's `[OBJECTIVE:]` lines can share, e.g.:

```text
Airway / positioning
Airway / adjuncts
Math 1400 / derivatives / chain rule
CSCI 1100 / loops / while
```

- Names must be exact-matchable: an item `[OBJECTIVE: Airway / positioning]`
  counts toward that objective and no other.
- Prefer a prefix hierarchy (`subject / topic / subtopic`) so the `evidence`
  command's `--objective` filter and `--prefix` matching work naturally.
- Preserve the target verb and cognitive demand. “Identify,” “explain,”
  “apply,” “analyze,” and “perform” are not interchangeable.
- For standardized tests, record blueprint version, domain weights, item
  formats, timing, permitted tools, and tested depth. For knowledge courses,
  use the actual syllabus and instructor emphasis rather than a generic exam.

## 3. Establish prerequisites and treatment

For each objective, identify genuine prerequisites and choose a proposed
treatment: direct source reading, excerpt, guided lesson, notes/terms, worked
example, visual or simulation, demonstration, practice, test,
assessment-first, or human review. Each treatment must have a purpose.

## 4. Map existing material

For each objective, find:

- Which lesson section (`### Heading`) teaches it.
- Which items test it (grep the bank for the `[OBJECTIVE:]` line, or trust
  `stats` counts).
- Which item types are used (`recall`-heavy is fine for definitions; make sure
  application objectives get `application`-difficulty items).

Record the map as a table:

```text
Objective                    | Lesson section     | Items | Types        | Status
Airway / positioning         | The Airway, Step.. | 3     | mc, table    | covered
Math 1400 / derivatives / .. | Chain Rule          | 1     | mc           | thin
CSCI 1100 / loops / while    | (missing)           | 0     | none         | gap
```

## 5. Find the gaps

A gap is any objective with zero (or thin) coverage, or an objective whose
lesson section does not exist. Do not paper over gaps: report them.

- **Missing lesson**: the objective has no `###` section any item points at.
- **Thin coverage**: one item for a high-stakes objective. Recommend 2–3 items
  spanning recall → application.
- **Wrong difficulty**: all items `recall` for an objective that requires
  `application`/`analysis`.

## 6. Build the assessment blueprint

Map objective weights and cognitive demand to item counts, difficulty, item
families, feedback mode, timing, and required transfer. Do not use recall
questions as evidence for an application objective. Include diagnostic,
formative, and summative assessment only where the course needs them.

## 7. Propose the work

For each gap, propose exactly what to write:

- A lesson section (`### Heading`) covering the objective's concepts.
- The items to add, with `[OBJECTIVE:]`, `[LESSON-REF: Heading]`, and the
  difficulty that matches the objective's demand.

Then validate the proposal against the real tool before claiming it works:

```bash
python itembank.py lint bank.md       # every new item lints clean
python itembank.py coverage bank.md   # the objective map re-computed, gaps visible
python itembank.py stats bank.md      # objective coverage now shows the gap closed
```

## Boundaries

- Coverage claims must be grounded in `coverage`/`stats` output and item
  counts, not in prose. If you cannot cite the item (via `coverage` or the
  `## SOURCES` registry), do not claim coverage.
- Do not generate questions beyond what the user asked for. Propose, then
  write on approval (or use the `author-bank` skill when asked to write).
- Never commit real banks or learner data to this repository.
- Never claim standardized-test fidelity without a cited, versioned blueprint.
- Hand item authoring to `author-bank` and source treatments to `absorb-book`.
