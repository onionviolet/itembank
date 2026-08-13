---
name: author-bank
description: Write or extend itembank question banks that lint clean. Use when asked to author items through the write → lint → fix loop, with the distractor, position-skew, and confidence rules the linter enforces.
---

# Author an itembank bank

Read `.planning/AGENT-WORKFLOW.md` before acting. Search approved roots for
existing items and accepted revisions first. Preserve provenance, rights,
objective links, expected-base fingerprints, review state, and recovery. A
learner note or generated draft never silently becomes keyed assessment truth.

You write items in the itembank format and make them lint clean. The linter
is your reviewer: it names every structural and quality error by item number,
and you fix what it names. Never argue with it or skip an `error`.

## 1. Read the contract first

```bash
python itembank.py spec
```

The contract defines the item grammar, the six types, the lesson section, and
the lint codes. Read it before drafting. Do not invent fields.

## 2. Draft the bank

Before drafting, obtain the objective, intended cognitive demand,
source/locator, course role (diagnostic, formative practice, remediation, or
summative), and any exam-blueprint constraints. If these are absent, propose
them through `curriculum-design`; do not create generic trivia and attach an
objective afterward.

Items are `Qn.` blocks with shared fields:

```markdown
Q1. Stem text   (difficulty: application)
[ID: ...]                      # added by `id-assign`, not by hand
[OBJECTIVE: Airway / positioning]
[LESSON-REF: The Airway, Step By Step]   # optional, links to a lesson heading

A) Option A
B) Option B
C) Option C
D) Option D

CORRECT: B

WHY BEST: The one-sentence reason B is right.

KEY DISCRIMINATOR: The single fact the item turns on.

SECOND-BEST: C. Why C is tempting and wrong here.

DISTRACTOR ANALYSIS:
- A) When this WOULD be correct (every distractor must say this).
- B) Correct: why B is right.
- C) When this WOULD be correct.
- D) When this WOULD be correct.

TRAP: The misread this item punishes.

CONFIDENCE: high
```

Type variants: `[TYPE: multi]` + `[SELECT: 2]`, `[TYPE: table]` +
`[CATEGORIES: ...]`, `[TYPE: build]` (ordered steps), `[TYPE: dnd]` (sort into
buckets), `[TYPE: short]` (constructed response, never auto-graded; add a
`RUBRIC:` so a marker can grade it).

## 3. Lint and fix

```bash
python itembank.py lint bank.md
```

Rules that matter (all enforced; write to them, do not fight them):

- **Every distractor must say when it WOULD be correct.** This is the first
  thing dropped under length pressure and it is a hard error.
- **No answer-position skew.** Correct letters must spread; clustering on one
  letter is flagged.
- `SELECT:` count matches keyed count; keys name existing options.
- `table` categories are declared; `build` steps are unique; stems do not
  duplicate.
- Missing `WHY BEST:` is an error; `CONFIDENCE: low` items draw a lint
  warning on every lint. Raise the confidence or accept the warning.
- The stem tests the stated objective at its stated cognitive demand.
  Important objectives include changed-context transfer, not only paraphrased
  source recall.
- For standardized-test preparation, match only documented item conventions,
  construct distribution, difficulty, timing assumptions, and permitted tools.
- Distractors represent plausible misconceptions or boundary conditions, not
  comic errors. Explain why they fail here and when they would hold.

Iterate: lint → fix → lint, until `error` count is zero. Warnings advise;
resolve the quality ones.

## 4. Finish

```bash
python itembank.py id-assign bank.md    # mint ids + fingerprints (the only writer)
python itembank.py stats bank.md        # coverage + difficulty spread
python itembank.py study bank.md        # flashcards, optional sanity check
python itembank.py guard .              # ship gate: no real bank committed (CI enforces it)
```

Assisted drafting (optional, model-backed): `python itembank.py seed bank.md`
runs the one-accept loop. It drafts candidate items and reads
`accept` / `skip` / `cancel` per draft. It refuses by name when no model
backend is reachable, and its output still goes through the same lint loop
above; it is a drafting aid, not a bypass.

## Boundaries

- Never commit a real bank to this repository (private content lives
  elsewhere; `fixtures/` is synthetic).
- Never auto-grade prose: `short` items are recorded, left `pending`, and
  marked later against the rubric.
- The runtime decides what a learner sees. An item's `TRAP:` and rationale
  are key material, not teaching text to blurt out mid-session.
