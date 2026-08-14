---
name: build-course
description: Orchestrate an AI-assisted itembank course from books, syllabi, standards, exam blueprints, notes, folders, or existing banks. Use when creating or revising a complete course, deciding readings versus generated treatments, coordinating curriculum and item skills, or using learner evidence and metrics to improve the course path.
---

# Build a source-grounded course

Read `.planning/AGENT-WORKFLOW.md` and `.planning/SOURCE-TO-COURSE.md` first.
Use the shared authority, vision, disposition, operation, acceptance, recovery,
and handoff contract throughout this skill. Work only in source and write roots
the user placed in scope. The shipped product has no course manifest command
yet, so do not invent one; produce reviewable planning artifacts and use
existing commands.

## 1. Establish the target

Record learner, outcome, timeframe, source authority, syllabus or blueprint
version, assessment conditions, prior knowledge, and constraints. Distinguish
a standardized test blueprint from a local knowledge course.

## 2. Inventory sources and existing artifacts

Find approved books, PDFs, notes, lesson files, banks, and evidence. Record
stable locators, ownership, conflicts, and extraction uncertainty. Never scan
unrelated roots or treat discovery as authorization to transmit or modify.

Run the real contracts where applicable:

```bash
python3 itembank.py spec
python3 itembank.py stats bank.md
python3 itembank.py coverage bank.md
python3 itembank.py audit source source-file
```

## 3. Design the curriculum

Use `curriculum-design` to create hierarchical objectives, prerequisites,
source alignment, treatments, coverage states, and the assessment blueprint.
Every covered claim cites the target and existing artifact. Unknown stays
unknown.

## 4. Choose treatment before generation

For each objective choose direct reading, excerpt, guided lesson, terms/notes,
worked example, visual or simulation, demonstration, practice, test,
assessment-first, or human review. Prefer the source when it already teaches
well. State why the treatment fits.

Use `absorb-book` for an approved source treatment and `author-bank` for
approved items. Generate one bounded objective or section at a time; lint,
review, and retain citations before expanding.

## 5. Verify course quality

Check coverage, prerequisite coherence, treatment purpose,
objective-to-assessment alignment, changed-context transfer, distractor
quality, source fidelity, accessibility, and degraded operation. Preview
learner-facing artifacts rather than approving markdown alone.

## 6. Use evidence honestly

Inspect the available evidence and trends commands for the current checkout
before invoking them. Use response correctness, attempts, hint use, confidence,
response time, error patterns, retention state, and pending review to propose
next actions or course revisions. Always state the window, denominator,
missing signals, and uncertainty. Sparse evidence cannot support mastery
percentages or confident causal claims.

## 7. Hand back a tangible plan

Report the course map, direct readings, generated and needed artifacts,
practice and test plan, cited gaps and conflicts, evidence-based next action,
proposed writes, and validation commands. Keep drafts distinguishable from
accepted material and every write recoverable. Never commit real course
content to this repository.
