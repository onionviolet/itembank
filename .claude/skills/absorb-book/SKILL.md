---
name: absorb-book
description: Turn a source document or textbook into itembank lesson and question-bank content. Use when a user has a book, chapter, PDF, or notes and wants it converted into a lesson section plus a lint-clean question bank, one objective at a time.
---

# Absorb a book into itembank

You are converting a source document into the itembank format: a bank
markdown file that lints clean and can be served as a quiz or studied. The
source may be a PDF, HTML, notes, or a pasted chapter. You never guess the
format — you read the contract from the tool itself.

## 1. Get the contract

```bash
python itembank.py spec
```

Read the whole output before writing anything. It defines the item grammar
(`Qn.` blocks, `[OBJECTIVE:]`, `[TYPE:]`, `CORRECT:`, `WHY BEST:`,
`KEY DISCRIMINATOR:`, `DISTRACTOR ANALYSIS:`, `TRAP:`, `CONFIDENCE:`), the
six item types, and the optional `## LESSON` section (teaching text above the
first question, `###` subheadings referenceable via `[LESSON-REF: heading]`).

## 2. Read and outline the source

- Read the source in full (or the chapter the user names).
- Write a short outline: the sections, and for each section the 1–3 concepts a
  reader must retain.
- Keep the bank's content faithful to the source. Do not invent facts the
  source does not support. If the source is ambiguous, ask.

## 3. Write the lesson section

One `## LESSON` at the top of the bank, above the first question:

```markdown
## LESSON

### Section One Heading

Prose paragraphs, bullet/numbered lists, pipe tables, inline code, fenced
code, bold, italic, links. That is the whole toolbox — the reader renders
nothing else, so write plain prose.

### Section Two Heading
...
```

Rules from the contract:

- Subheadings are `###` (one level deeper than `## LESSON`) and each becomes a
  section an item can point at.
- Heading text must differ in more than casing/spacing/punctuation — slugs
  that collide are a lint error (`lesson.duplicate_heading`).
- A heading's text must not contain `]` (a `[LESSON-REF:]` reads up to the
  first closing bracket).
- A fenced block's info string (```python, ```math) names its language;
  nothing acts on it yet, but write it correctly for later phases.

Alternatively, if the source is already a markdown file, you may keep the
lesson in that file and point at it: `[LESSON-SRC: path.md]` in the bank
preamble. The path must resolve inside the bank's own directory.

## 4. Write the items, one objective at a time

Each item is a `Qn.` block. Give every item an `[OBJECTIVE:]` that names its
syllabus/blueprint reference (e.g. `Airway / positioning`). Link items to
lesson sections with `[LESSON-REF: Section Heading]`.

Quality rules the linter enforces — do not fight them, write to them:

- **Every distractor must say when it WOULD be correct** (in
  `DISTRACTOR ANALYSIS:`). This is the first thing models drop under length
  pressure; it is a lint error.
- **No answer-position skew.** Spread `CORRECT:` letters evenly; the linter
  flags clustering.
- `SELECT:` count must match the number of correct answers for `multi`.
- `CATEGORIES:` must be declared for `table`; `build` steps must be unique.
- Missing `WHY BEST:` is an error. `CONFIDENCE: low` items draw a lint
  warning on every lint — raise the confidence or accept the warning.
- Stems must not duplicate; no `TRAP`-less trick questions.

## 5. Validate and iterate

```bash
python itembank.py lint bank.md
```

Fix every `error`, in order, by item number. Re-lint until clean. Warnings
advise — resolve them when they name a quality issue.

## 6. Finish

- `python itembank.py id-assign bank.md` to mint opaque ids and fingerprints
  (the only command that writes into the bank).
- `python itembank.py stats bank.md` to show objective coverage and
  difficulty spread; if one objective has nine items and another none, that is
  visible here — rebalance before handing back.
- Optional: `python itembank.py serve bank.md` for the user to sit it, or
  `python itembank.py study bank.md` for flashcards.

## Boundaries

- Never commit a real bank to this repository — real banks belong in private
  storage. `fixtures/` holds synthetic content only.
- Never auto-grade prose; a `short` item is left `pending` for a marker.
- Keep the lesson prose separate from items when the source is long: the
  lesson is reading material, the items test it.
