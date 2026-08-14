---
name: build-course
description: Orchestrate an AI-assisted itembank course from books, syllabi, standards, exam blueprints, notes, folders, or existing banks. Use when creating or revising a complete course, deciding readings versus generated treatments, coordinating curriculum and item skills, or using learner evidence and metrics to improve the course path.
---

# Build a source-grounded course

**Provenance:** rewritten 2026-08-14 (reframe slice 4b) to the operation
protocol in `.planning/research/phase-16/14-synthesis.md` section 10.

Read `../OPERATION-CONTRACT.md` first, then `.planning/AGENT-WORKFLOW.md` and
`.planning/SOURCE-TO-COURSE.md`. This skill orchestrates the whole course
lifecycle: permissions, identity, treatments, validation, acceptance,
evidence review, and recovery. It delegates curriculum structure to
`curriculum-design`, source treatments to `absorb-book`, and item writing to
`author-bank`, and it is responsible for the operation manifest they work
under.

The shipped product has no course manifest command. Do not invent one. A
course today is a set of reviewable planning artifacts (target statement,
objective map, treatment table, gap list) plus the real banks and lessons,
validated with existing commands. The manifest command surface is pending
(subphase 14B).

## 1. Declare the operation manifest

Before touching anything, record in the working plan:

- **Intent:** what this operation will produce (a new course plan, a revision,
  a remediation pass).
- **Approved roots:** the exact folders the user placed in read scope and the
  exact folders in write scope. Never scan or mutate outside them.
- **Rights and egress:** whether source text may transit to a hosted model,
  per the recorded per-subject decisions. Unknown rights stay restrictive.
- **Authority level:** recommend-only, draft-and-review, or approved bounded
  writes, and who reviews.

Discovery is read-only and never authorizes transmission or mutation.

## 2. Establish the target

Record learner, outcome, timeframe, source authority, syllabus or blueprint
version, assessment conditions, prior knowledge, and constraints. Distinguish
a standardized-test blueprint course from a local knowledge course; never
claim standardized-test fidelity without a cited, versioned blueprint.

## 3. Inventory before creating

Find approved books, PDFs, notes, lesson files, banks, and evidence inside
the approved roots. Record stable locators, ownership, fingerprints where
available, conflicts, and extraction uncertainty. Reconcile likely
duplicates and moved files; similar names never justify identity. Prefer
linking an adequate existing artifact over recreating it.

Run the shipped read-only contracts where applicable:

```bash
python itembank.py spec
python itembank.py stats bank.md
python itembank.py coverage bank.md
python itembank.py audit source source-file
python itembank.py audit coverage --source source-file --bank bank.md
python itembank.py evidence --base .
```

There is no discovery or binding command yet (pending 14A/14B); the
inventory is a documented table in the plan, and it must state what was not
scanned.

## 4. Design the curriculum

Use `curriculum-design` to produce hierarchical objectives, prerequisites,
source alignment, treatments, coverage states, and the assessment blueprint.
Every coverage claim cites `coverage` or `stats` output or a source locator.
Unknown stays unknown.

## 5. Choose treatment, then draft the smallest missing artifact

For each objective choose direct reading, excerpt, guided lesson, terms and
notes, worked example, visual or demonstration, practice, test,
assessment-first diagnostic, learner artifact, or human review. Prefer the
source when it already teaches well, and state why the treatment fits.

Then generate only what is genuinely missing, one bounded objective or
section at a time: `absorb-book` for an approved source treatment,
`author-bank` for approved items. Checkpoint between objectives so a
different client can resume. Cite sources and label synthesis in every
draft.

## 6. Validate, preview, and present the diff

Every draft passes the deterministic gates before review:

```bash
python itembank.py lint bank.md       # zero errors before handing over
python itembank.py stats bank.md      # mix, difficulty, position skew
python itembank.py coverage bank.md   # the gap visibly closed
```

Preview in both forms: the plain file in a Markdown reader, and the rich
surface (`build`, `serve`, `lesson`, or `study`). Never approve markdown
alone, and never self-certify accessibility; flag learner-facing output for
the human accessibility gates in `.planning/UI-SPEC.md`.

Show the reviewer a bounded diff of exactly what changes. Model-backed item
writes go through the shipped bounded loop, which enforces the manifest,
before-image, pending set, and exact-id approval:

```bash
python itembank.py audit author --source src --bank bank.md \
  --objective "Topic / subtopic" --mode draft_and_approve --state-dir .audit --write
python itembank.py audit undo WRITE_ID --bank bank.md --state-dir .audit
```

`id-assign` is the only other direct bank writer; run it after acceptance to
mint ids and fingerprints. There is no general expected-fingerprint write
surface outside `audit author` yet (pending 14A); ordinary file edits are
shown as diffs and accepted explicitly.

## 7. Use evidence honestly

Inspect the shipped `evidence`, `trends`, and `report` commands for the
current checkout before invoking them. Use response correctness, attempts,
hint use, confidence, response time, error patterns, retention state, and
pending review to propose next actions or course revisions. Always state the
window, denominator, missing signals, and uncertainty. Sparse evidence never
supports mastery percentages or confident causal claims. Evidence is never
transferred between objectives by alignment alone.

## 8. Close the operation

Report, in files rather than chat: the course map, direct readings,
generated and still-needed artifacts, the practice and test plan, cited gaps
and conflicts, the evidence-based next action, every write performed with its
undo step, what is now stale because of the change (staleness marking has no
command yet; state it in the handoff), and remaining uncertainty. Keep
drafts distinguishable from accepted material. Run `python itembank.py
guard .` before any commit in this repository; never commit real course
content here.
