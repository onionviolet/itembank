---
name: absorb-book
description: Analyze a book, chapter, PDF, or notes for a course; outline and cite its objectives, decide when direct reading versus a lesson, terms, notes, examples, visuals, practice, or test is best, and create only the approved itembank artifacts one objective at a time.
---

# Absorb a source into a course

Read `.planning/AGENT-WORKFLOW.md` before acting. Preserve the distinction
between user vision, research, accepted course content, learner-owned notes,
assessment authority, and derived views. Route viable unselected treatments to
the disposition ledger rather than silently dropping them.

Do not assume absorption means rewriting the source into lesson prose plus a
bank. First determine what each objective needs. Clear, authoritative passages
may be the best reading; diffuse material may need synthesis; procedures may
need worked steps; spatial or causal ideas may need visuals; durable knowledge
may need terms and retrieval practice.

If this work belongs to a whole course, use `build-course` to establish the
target and objective map, then return here for source-level treatment.

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

## 3. Recommend treatment before authoring

For every supported objective, record the source locator, learner demand, and
one recommended treatment: `read-source`, `excerpt`, `guided-lesson`,
`notes-terms`, `worked-example`, `visual`, `practice`, `test`, or
`human-review`. Explain why. Do not generate until the requested or approved
treatment is clear.

## 4. Write an approved lesson treatment

One `## LESSON` at the top of the bank, above the first question:

```markdown
## LESSON

### Section One Heading

Prose paragraphs, bullet/numbered lists, pipe tables, inline code, fenced
code, bold, italic, links. That is the whole toolbox. The reader renders
nothing else, so write plain prose.

### Section Two Heading
...
```

Rules from the contract:

- Subheadings are `###` (one level deeper than `## LESSON`) and each becomes a
  section an item can point at.
- Heading text must differ in more than casing/spacing/punctuation. Slugs
  that collide are a lint error (`lesson.duplicate_heading`).
- A heading's text must not contain `]` (a `[LESSON-REF:]` reads up to the
  first closing bracket).
- A fenced block's info string (```python, ```math) names its language;
  nothing acts on it yet, but write it correctly for later phases.

Alternatively, if the source is already a markdown file, you may keep the
lesson in that file and point at it: `[LESSON-SRC: path.md]` in the bank
preamble. The path must resolve inside the bank's own directory.

## 5. Write approved items, one objective at a time

Each item is a `Qn.` block. Give every item an `[OBJECTIVE:]` that names its
syllabus/blueprint reference (e.g. `Airway / positioning`). Link items to
lesson sections with `[LESSON-REF: Section Heading]`.

Quality rules the linter enforces: do not fight them, write to them:

- **Every distractor must say when it WOULD be correct** (in
  `DISTRACTOR ANALYSIS:`). This is the first thing models drop under length
  pressure; it is a lint error.
- **No answer-position skew.** Spread `CORRECT:` letters evenly; the linter
  flags clustering.
- `SELECT:` count must match the number of correct answers for `multi`.
- `CATEGORIES:` must be declared for `table`; `build` steps must be unique.
- Missing `WHY BEST:` is an error. `CONFIDENCE: low` items draw a lint
  warning on every lint. Raise the confidence or accept the warning.
- Stems must not duplicate; no `TRAP`-less trick questions.

## 6. Validate and iterate

```bash
python itembank.py lint bank.md
```

Fix every `error`, in order, by item number. Re-lint until clean. Warnings
advise. Resolve them when they name a quality issue.

## 7. Finish

- `python itembank.py id-assign bank.md` to mint opaque ids and fingerprints
  (the only command that writes into the bank).
- `python itembank.py stats bank.md` to show objective coverage and
  difficulty spread; if one objective has nine items and another none, that is
  visible here. Rebalance before handing back.
- Optional: `python itembank.py serve bank.md` for the user to sit it, or
  `python itembank.py study bank.md` for flashcards.

## Boundaries

- Never commit a real bank to this repository. Real banks belong in private
  storage. `fixtures/` holds synthetic content only.
- Never auto-grade prose; a `short` item is left `pending` for a marker.
- Keep the lesson prose separate from items when the source is long: the
  lesson is reading material, the items test it.
- Never claim a generated summary is a source passage. Preserve citations and
  label synthesis.
- Direct reading is a successful outcome. Do not manufacture a lesson merely
  to demonstrate generation.
