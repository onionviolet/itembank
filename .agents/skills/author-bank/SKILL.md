---
name: author-bank
description: Write or extend itembank question banks that lint clean. Use when asked to author items through the write, lint, fix loop, with the distractor, position-skew, and confidence rules the linter enforces.
---

# Author an itembank bank

**Provenance:** rewritten 2026-08-14 (reframe slice 4b) to the operation
protocol in `.planning/research/phase-16/14-synthesis.md` section 10.

Read `../OPERATION-CONTRACT.md` first, then `.planning/AGENT-WORKFLOW.md`.
This skill owns purpose, demand, blueprint fit, item construction, lint,
statistical review, and runtime validation for question banks. A learner
note or generated draft never silently becomes keyed assessment truth: no
key laundering.

The linter is your reviewer for structure and quality: it names every error
by item number, and you fix what it names. Never argue with it or skip an
`error`.

## 1. Declare the operation

State intent (new bank, extension, rebalance), the one bank file in write
scope and the sources in read scope, the rights basis for any quoted source
material, whether item text may transit to a hosted model, and the authority
level: recommend-only (propose items in the plan), draft-and-review (write
to the bank, reviewer accepts the diff), or the shipped bounded loop
(section 5).

## 2. Inventory before creating

Search the approved roots for existing items and accepted revisions first.
Extend or rebalance an existing bank rather than shadowing it with a new
one. Preserve provenance, `## SOURCES` entries, objective links, existing
`[ID:]` lines, and review state. Then read the contract and the current
state:

```bash
python itembank.py spec               # the item grammar; do not invent fields
python itembank.py stats bank.md      # current mix, objectives, difficulty, position skew
python itembank.py coverage bank.md   # which objectives are already covered, with citations
```

## 3. Plan before drafting

Obtain the objective, intended cognitive demand, source and locator, course
role (diagnostic, formative practice, remediation, or summative), and any
exam-blueprint constraints. If these are absent, propose them through
`curriculum-design`; do not create generic trivia and attach an objective
afterward. Draft one bounded objective at a time and checkpoint between
objectives.

## 4. Draft the items

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

Type variants: `[TYPE: multi]` plus `[SELECT: 2]`, `[TYPE: table]` plus
`[CATEGORIES: ...]`, `[TYPE: build]` (ordered steps), `[TYPE: dnd]` (sort
into buckets), `[TYPE: short]` (constructed response, never auto-graded; add
a `RUBRIC:` so a marker can grade it).

Cite the source for source-derived items in the bank's `## SOURCES`
registry, and label synthesized scenarios as synthesis. Distractors
represent plausible misconceptions or boundary conditions, not comic
errors.

## 5. Validate deterministically: lint, fix, lint

```bash
python itembank.py lint bank.md
```

Rules that matter (all enforced; write to them, do not fight them):

- **Every distractor must say when it WOULD be correct.** This is the first
  thing dropped under length pressure and it is a hard error.
- **No answer-position skew.** Correct letters must spread; clustering is
  flagged.
- `SELECT:` count matches keyed count; keys name existing options.
- `table` categories are declared; `build` steps are unique; stems do not
  duplicate.
- Missing `WHY BEST:` is an error; `CONFIDENCE: low` draws a warning on
  every lint. Raise the confidence or accept the warning.
- The stem tests the stated objective at its stated cognitive demand;
  important objectives include changed-context transfer, not only
  paraphrased recall.
- For standardized-test preparation, match only documented item conventions,
  construct distribution, difficulty, timing assumptions, and permitted
  tools.

Iterate until the `error` count is zero. Then run the statistical review:
`stats` for mix, difficulty spread, and position skew; `coverage` for the
objective map. Rebalance a lopsided bank before handing it back.

Model-backed drafting has two shipped bounded surfaces, both of which feed
this same lint loop and neither of which bypasses it: `python itembank.py
seed bank.md` (the accept/skip/cancel loop; it refuses by name when no
backend is reachable) and the manifest-journaled loop:

```bash
python itembank.py audit material material-file --objective "Topic / sub" --mode report_only
python itembank.py audit author --source src --bank bank.md \
  --objective "Topic / sub" --mode draft_and_approve --state-dir .audit --write
python itembank.py audit undo WRITE_ID --bank bank.md --state-dir .audit
```

`audit author` enforces the operation manifest, before-image, pending set,
and exact-write-id approval, and `audit undo` is its one-step reversal,
refusing stale work. Use it when the operation needs a journal and undo.

## 6. Preview, diff, and accept

Show the plain file (it must read cleanly in a Markdown reader) and a rich
preview (`build`, `serve`, or `study`) before review; do not self-certify
accessibility. Present the reviewer a bounded diff of the bank. After
acceptance:

```bash
python itembank.py id-assign bank.md   # mint ids and content-hash fingerprints (the only direct writer)
python itembank.py guard .             # ship gate: no real bank committed (CI enforces it)
```

Close with the undo step for each write, what became stale (dependent
lessons, exports, or attempt renders; there is no staleness command yet, so
state it in the handoff), and remaining uncertainty, including any
`CONFIDENCE: low` items left standing and why.

## Boundaries

- Never commit a real bank to this repository (private content lives
  elsewhere; `fixtures/` is synthetic).
- Never auto-grade prose: `short` items are recorded, left `pending`, and
  marked later against the rubric.
- The runtime decides what a learner sees. An item's `TRAP:` and rationale
  are key material, not teaching text to blurt out mid-session.
- Never derive a key, distractor, or rationale from a learner note as if the
  note were accepted truth.
