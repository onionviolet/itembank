---
name: absorb-book
description: Analyze a book, chapter, PDF, syllabus, exam guide, grading policy, or notes for a course; extract source-grounded objectives or assessment rules, choose the best learning treatment, and create only approved itembank artifacts one objective at a time.
---

# Absorb a source into a course

**Provenance:** rewritten 2026-08-14 (reframe slice 4b) to the operation
protocol in `.planning/research/phase-16/14-synthesis.md` section 10.

Read `../OPERATION-CONTRACT.md` first, then `.planning/AGENT-WORKFLOW.md`.
This skill makes objective-by-objective direct-reading versus synthesis
decisions for one source, with locators, rights, and lesson, note, and
example proposals. If the work belongs to a whole course, use `build-course`
to establish the target and objective map, then return here for source-level
treatment.

If the source is a syllabus, exam guide, blueprint, rubric, grading policy, or
official sample form, also read `../ASSESSMENT-INTAKE.md`. Treat it as an
assessment-policy source, not ordinary lesson material.

This skill starts after an authorized source is available in an approved read
root. It does not log into an LMS, scrape an authenticated course, download a
course export, or infer that viewing a page authorizes copying linked material.
Route source-set acquisition to its own approved operation. Do not import quiz
keys, student submissions, grades, or feedback as assessment truth.

Do not assume absorption means rewriting the source into lesson prose plus a
bank. Clear, authoritative passages may be the best reading; diffuse
material may need synthesis; procedures may need worked steps; spatial or
causal ideas may need visuals; durable knowledge may need terms and
retrieval practice. Direct reading is a successful outcome. Do not
manufacture a lesson merely to demonstrate generation.

## 1. Declare the operation

State intent, the approved roots (the source file or folder, and the one
bank or lesson file in write scope), the rights basis for this source
(ownership, whether quoting and transformation are permitted, whether its
text may transit to a hosted model; unknown rights stay restrictive), and
the authority level. Discovery and reading never authorize mutation.

## 2. Get the contract and inventory the source

```bash
python itembank.py spec
python itembank.py audit source source-file        # read-only, locator-faithful record
python itembank.py audit coverage --source source-file --bank bank.md   # if a bank exists
```

Read the whole `spec` output before writing anything: it defines the item
grammar (`Qn.` blocks, `[OBJECTIVE:]`, `[TYPE:]`, `CORRECT:`, `WHY BEST:`,
`KEY DISCRIMINATOR:`, `DISTRACTOR ANALYSIS:`, `TRAP:`, `CONFIDENCE:`), the
item types, and the `## LESSON` section. Then read the source in full (or
the chapter the user names) and outline it: the sections, and for each
section the one to three concepts a reader must retain. Check for an
existing lesson or bank covering this material before drafting; link or
extend rather than duplicate.

For an assessment-policy source, extract each policy claim with its locator,
effective version, authority class, and conflicts. Populate only the fields the
source actually supports. Record silence as unknown, not as permission to infer
a weight, exclusion, item format, pass mark, or grading rule.

## 3. Recommend treatment before authoring

For every supported objective, record the source locator (page, section, or
heading), the learner demand, and one recommended treatment: `read-source`,
`excerpt`, `guided-lesson`, `notes-terms`, `worked-example`, `visual`,
`demonstration`, `practice`, `test`, `assessment-first`, `learner-artifact`,
or `human-review` (the eleven treatments in requirement TREAT-01, which is
the canonical vocabulary), with the reason. Route viable
unselected treatments to the disposition ledger rather than dropping them.
Do not generate until the requested or approved treatment is clear. This
recommendation table is the checkpoint: a different client can pick up from
it.

## 4. Draft the smallest approved artifact

One objective or section at a time. Cite the source locator in the draft and
label anything the source does not literally say as synthesis. Keep the
bank's content faithful to the source; do not invent facts it does not
support, and ask when it is ambiguous.

An approved lesson treatment is one `## LESSON` at the top of the bank,
above the first question:

```markdown
## LESSON

### Section One Heading

Prose paragraphs, bullet or numbered lists, pipe tables, inline code, fenced
code, bold, italic, links. That is the whole toolbox; write plain prose.
```

Rules from the contract: subheadings are `###` and each becomes a section an
item can point at via `[LESSON-REF: heading]`; heading slugs must not
collide (`lesson.duplicate_heading`); heading text must not contain `]`; a
fenced block's info string names its language. Alternatively, if the source
is already a Markdown file, keep the lesson there and point at it with
`[LESSON-SRC: path.md]` in the bank preamble; the path must resolve inside
the bank's own directory. That is the link-not-copy default.

For approved items, follow `author-bank` (the same lint rules apply: every
distractor states when it would be correct, no answer-position skew, no
duplicate stems, `WHY BEST:` present, `SELECT:` matches the key count).

## 5. Validate deterministically

```bash
python itembank.py lint bank.md
```

Fix every `error`, in order, by item number, and re-lint until clean.
Warnings advise; resolve the ones that name a quality issue.

## 6. Preview plain and rich, then present the diff

Preview both forms before review: the bank or lesson file itself in a plain
Markdown reader (it must stay coherent there), and the rendered surface
(`python itembank.py lesson bank.md`, `build`, `serve`, or `study`). Do not
self-certify accessibility; flag learner-facing output for the human gates
in `.planning/UI-SPEC.md`. Show the reviewer a bounded diff of exactly what
was added or changed in the bank.

## 7. Accept, finish, and report

After acceptance:

```bash
python itembank.py id-assign bank.md   # mint opaque ids and fingerprints (the only direct writer)
python itembank.py stats bank.md       # objective coverage and difficulty spread; rebalance if lopsided
python itembank.py coverage bank.md    # the objective map re-computed
```

Optional: `serve` for a sitting, `study` for flashcards. Close with a
durable report: treatments chosen and deferred, locators cited, what was
drafted versus linked, the undo step for each write (re-editing the bank is
reviewable; `audit undo` applies only to `audit author` writes), what is now
stale (no command surface yet; state it), and remaining uncertainty,
including any passage you were unsure how to read.

## Boundaries

- Never commit a real bank to this repository; `fixtures/` is synthetic.
- Never auto-grade prose; a `short` item stays `pending` for a marker.
- Keep lesson prose separate from items when the source is long: the lesson
  is reading material, the items test it.
- Never claim a generated summary is a source passage. Preserve citations
  and label synthesis.
- Respect the declared rights: do not quote beyond the granted basis, and do
  not send source text to a hosted model outside the declared egress.
- Do not turn the frequency or order of topics in one source into an exam
  weight unless the governing assessment authority says it does.
