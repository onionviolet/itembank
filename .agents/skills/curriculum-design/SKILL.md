---
name: curriculum-design
description: Build a curriculum from a syllabus or outline as itembank objective coverage. Use when a user wants to know which objectives their material covers, where the gaps are, and what lessons/items to write next to close them.
---

# Design a curriculum as objective coverage

You turn a syllabus (or an outline of what a learner must know) into a
coverage plan: objectives, the lesson sections and items that teach each one,
and a visible gap list. The tool measures coverage objectively — you never
claim coverage by feel.

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

## 3. Map existing material

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
CSCI 1100 / loops / while    | (missing)           | 0     | —            | gap
```

## 4. Find the gaps

A gap is any objective with zero (or thin) coverage, or an objective whose
lesson section does not exist. Do not paper over gaps: report them.

- **Missing lesson**: the objective has no `###` section any item points at.
- **Thin coverage**: one item for a high-stakes objective. Recommend 2–3 items
  spanning recall → application.
- **Wrong difficulty**: all items `recall` for an objective that requires
  `application`/`analysis`.

## 5. Propose the work

For each gap, propose exactly what to write:

- A lesson section (`### Heading`) covering the objective's concepts.
- The items to add, with `[OBJECTIVE:]`, `[LESSON-REF: Heading]`, and the
  difficulty that matches the objective's demand.

Then validate the proposal against the real tool before claiming it works:

```bash
python itembank.py lint bank.md       # every new item lints clean
python itembank.py stats bank.md      # objective coverage now shows the gap closed
```

## Boundaries

- Coverage claims must be grounded in `stats` output and item counts, not in
  prose. If you cannot cite the item, do not claim coverage.
- Do not generate questions beyond what the user asked for — propose, then
  write on approval (or use the `author-bank` skill when asked to write).
- Never commit real banks or learner data to this repository.
