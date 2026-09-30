# September 29 project instruction originals

Type: CHRONOLOGICAL. Verbatim pre-task Git text; current instructions remain in their owners.

## .agents/skills/OPERATION-CONTRACT.md

```markdown
# Shared operation contract for itembank agent skills

**Provenance:** created 2026-08-14 (reframe slice 4b). This file condenses the
agents-and-skills contract in `.planning/research/phase-16/14-synthesis.md`
section 10, with the authority vocabulary of sections 2, 3, and 6, so that
every skill can point at one copy instead of restating it. The binding product
contract is `.planning/SOURCE-TO-COURSE.md`; the cross-agent procedure is
`.planning/AGENT-WORKFLOW.md`. If this file and those disagree, those win.

This contract applies to every agent client: Claude Code/Cowork, Codex, local
backends, and any compatible agent. The backend changes capability, latency,
cost, and privacy disclosure. It never changes the artifact or authority
contract.

## The one operation protocol

Every consequential operation follows the same sequence:

1. **Declare intent.** State what the operation will produce and why.
2. **Declare authority.** Name the approved read roots, write roots, rights
   basis, permitted network egress, and execute authority for this operation.
   Discovery never grants writing, transformation, execution, egress, or
   export.
3. **Inventory before creating.** Search the approved roots for existing
   sources, artifacts, and accepted revisions. Reconcile duplicates, moves,
   and conflicts. Never identify or merge artifacts from filenames alone.
4. **Plan treatment.** Decide the best treatment per objective before
   generating anything. Direct source reading is a first-class outcome, not a
   failure to generate.
5. **Checkpoint.** Record enough durable state that a different client, or a
   human, can resume the operation without chat history.
6. **Draft the smallest missing artifact.** One bounded objective or section
   at a time. Reuse or link an adequate existing artifact instead of
   recreating it.
7. **Cite and label synthesis.** Every source-derived claim keeps a stable
   locator. Generated synthesis is labeled as such and never presented as a
   source passage.
8. **Validate deterministically.** Run the shipped lint and audit contracts.
   A draft that has not passed them is not done.
9. **Preview accessibly, plain and rich.** Show the durable plain-file form
   and the rendered learner-facing form. An agent never self-certifies
   accessibility.
10. **Present a bounded diff.** The reviewer sees exactly what would change,
    and nothing changes outside that diff.
11. **Pass configured review.** Recommend-only, draft-and-review, or approved
    bounded writes: the granted autonomy level decides who accepts.
12. **Accept atomically.** A committed write leaves the old valid state or
    the new valid state, never a mixed state.
13. **Update staleness; report undo and uncertainty.** Mark derived and
    dependent material stale, state the exact reversal step, and report what
    remains uncertain, including denominators and missing signals.

Course operations with exams, graded work, competency checks, or completion
thresholds also use `ASSESSMENT-INTAKE.md`. Assessment policy is source-bound
authority, not an authoring convenience. Official grades, runtime scores,
advisory marks, mastery inferences, and course completion remain separate.

An agent may recommend, draft-and-review, or perform approved bounded writes.
It cannot self-expand scope, self-certify accessibility, silently accept its
own uncertain source claim, transfer evidence between objectives, or cross the
runtime's keyed-disclosure boundary.

## Authority vocabulary

- The **learner** owns goals, private notes, scratch work, strategy choice,
  and evidence export.
- A **course builder** defines scope, treatments, and paths within source and
  rights limits.
- A **reviewer** accepts or rejects revisions at the configured consequence
  level.
- An **agent client** discovers, aligns, drafts, validates, and explains
  within an operation manifest. It never owns accepted truth or assessment
  authority.
- The **deterministic runtime** is the sole authority for assessment session
  state, keyed disclosure, scoring, and attempt evidence. Prose stays pending
  until approved marking.

Accepted files (courses, lessons, banks, notes, evidence) are canonical.
Indexes, HTML, caches, rankings, and progress views are derived and
disposable. Accepted content, workflow state, epistemic confidence, validation
state, rights state, and availability are separate axes; never collapse them.
Rights are operation-specific (read, quote, transform, remote-process,
package, export, share) and unknown rights stay restrictive. Link, import,
copy, move, edit-in-place, supersede, migrate, and synchronize are distinct
operations, never synonyms. Same ID with divergent bytes is a conflict, never
a silent overwrite. Similar names never justify identity.

## Shipped surfaces for the protocol steps

Skills document only shipped command surfaces. These exist today:

| Protocol step | Shipped surface |
|---|---|
| Contract and grammar | `python itembank.py spec`, `schema`, `usage`, `config` |
| Inventory a bank | `stats BANK`, `coverage BANK`, `select` |
| Inventory a source | `audit source FILE` (read-only, locator-faithful) |
| Source-versus-bank coverage | `audit coverage --source S --bank B` (read-only) |
| Deterministic validation | `lint BANK` (errors and warnings by item number) |
| Plain preview | `lesson BANK`, `study BANK`, the bank file itself in a Markdown reader |
| Rich preview | `build BANK` (static HTML), `serve BANK`, `render-style` |
| Bounded model-backed writes | `audit material`, `audit author --mode ... --state-dir ...` (manifest, before-image, pending set, exact-id approval) |
| Identity and fingerprints | `id-assign BANK` (the only direct bank writer) |
| Undo | `audit undo WRITE_ID --bank B --state-dir DIR` (refuses stale work) |
| Evidence, honestly | `evidence`, `trends`, `report`, `retract`, `mark`, `render` |
| Ship gate | `guard .` (no real bank committed; CI enforces it) |

## Pending surfaces

The following section-10 capabilities have no shipped command yet. Where a
skill needs one, it states the manual planning-level procedure and marks the
surface as pending. Do not invent commands for them:

- A course manifest or course package command (14B).
- Discovery, binding, link/import/move/supersede, and reconciliation commands
  across multiple roots (14A/14B). Today this is a manual, read-only,
  documented inventory.
- A rights-grant record or per-operation rights command. Today rights are
  stated in the operation manifest prose and unknown stays restrictive.
- A general expected-fingerprint compare-and-swap write surface outside the
  `audit author` loop. Today, bounded writes go through `audit author` or are
  ordinary reviewed file edits with the diff shown before writing.
- Dependency and staleness marking. Today staleness is reported in the
  handoff, not recorded by a command.
- The semantic lesson profile, media policy, and legacy-upgrade tooling
  (16A/16C). See the stub skills.

## Hard limits in every skill

- Never commit a real bank or learner data to this repository; `fixtures/` is
  synthetic; `guard` enforces this in CI.
- Never auto-grade prose; `short` items stay `pending` for a marker.
- A learner note or generated draft never silently becomes keyed assessment
  truth, lesson truth, a score, or mastery.
- Key material (`CORRECT:`, `TRAP:`, rationale) is disclosed by the runtime,
  never by the model mid-session.
- No em dash characters in authored repository prose.
- Handoffs land in files, not chat: objective, files read, files produced,
  decisions, unresolved conflicts, verification done and owed, exact next
  action.

```

## .agents/skills/absorb-book/SKILL.md

```markdown
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

```

## .agents/skills/author-bank/SKILL.md

```markdown
---
name: author-bank
description: Write or extend source-grounded itembank question banks that lint clean. Use when authoring diagnostic, practice, or exam-aligned items through the write, lint, fix loop, including blueprint fit, grading constraints, distractors, position skew, and confidence rules.
---

# Author an itembank bank

**Provenance:** rewritten 2026-08-14 (reframe slice 4b) to the operation
protocol in `.planning/research/phase-16/14-synthesis.md` section 10.

Read `../OPERATION-CONTRACT.md` first, then `.planning/AGENT-WORKFLOW.md`.
This skill owns purpose, demand, blueprint fit, item construction, lint,
statistical review, and runtime validation for question banks. A learner
note or generated draft never silently becomes keyed assessment truth: no
key laundering.

For summative, certification, placement, or grade-bearing items, read
`../ASSESSMENT-INTAKE.md` before drafting. The assessment profile, not the
author's intuition, supplies scope, construct, distribution, conditions, and
grading constraints.

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

For consequential items, verify the assessment readiness gate. If the tested
scope, construct, format, conditions, or scoring authority is unresolved, do
not label the item summative or blueprint-faithful. It may be drafted as
provisional exploratory practice with the uncertainty preserved.

Use the target assessment's documented item families by default. If its final
exam is single-selection multiple choice, do not add `short`, `build`, `dnd`,
or other formats to the mock or summative bank. A non-target format is allowed
only as labeled teaching or diagnostic practice, a separate completion
requirement, or learner-selected enrichment. Keep it out of exam-fidelity
statistics and do not imply that it predicts the official score.

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

For `short` items, derive the rubric from the approved grading policy and
objective demand. State criteria, performance levels, point allocation,
acceptable variation, required evidence, and escalation conditions. Do not
invent partial credit, penalties, grade bands, or a pass threshold.

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
- **Structural conformance is subject-scoped and enforced for EMT.** An item
  whose objective is namespaced `emt:` is checked against NREMT's published
  examination specifications: multiple choice is 1 correct of exactly 4
  options, and multiple response is 2 of 5 or 3 of 6, in both cases with
  exactly 3 incorrect options. A divergence is a hard error. No other subject
  is checked, because NREMT governs no other subject. Verified citations, and
  the authorities that say nothing about item writing, are in
  `.planning/research/2026-08-24-item-writing-standards.md`.

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

```

## .agents/skills/build-course/SKILL.md

```markdown
---
name: build-course
description: Orchestrate an AI-assisted itembank course from books, syllabi, standards, exam blueprints, grading policies, notes, folders, or existing banks. Use when creating or revising a complete course, scoping what is taught and tested, deciding treatments, coordinating curriculum and item skills, or using learner evidence to improve the course path.
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

When the course includes any consequential assessment, also read
`../ASSESSMENT-INTAKE.md`. The resulting assessment profile is part of the
course checkpoint and governs downstream curriculum and item work.

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
An LMS page, export, or remote source set must be acquired by a separately
approved operation before this skill inventories or transforms it. Access to
one authenticated object does not authorize collection of its linked objects.
Never treat imported quiz keys, student submissions, grades, or feedback as
accepted assessment truth.

## 2. Establish the target

Record learner, outcome, timeframe, source authority, syllabus or blueprint
version, prior knowledge, and constraints. For each exam or graded component,
complete the assessment and grading intake: purpose, tested and excluded scope,
construct, distribution, formats, conditions, scoring, standard, review,
retakes, and reporting. Distinguish a standardized-test blueprint course from
a local knowledge course. Never claim fidelity without a cited, versioned
authority and a completed readiness gate.

For a publicly documented standardized or licensing exam, discover the current
governing materials from the exam owner and question-pool authority before
relying on a textbook or preparation provider. Bind the profile to the
learner's exam date, level, and jurisdiction.

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
source alignment, treatments, coverage states, assessment profiles, and the
assessment blueprint. Preserve official grades, itembank evidence, completion,
and mastery as separate states.
Every coverage claim cites `coverage` or `stats` output or a source locator.
Unknown stays unknown.

## 5. Choose treatment, then draft the smallest missing artifact

For each objective choose direct reading, excerpt, guided lesson, terms and
notes, worked example, visual or demonstration, practice, test,
assessment-first diagnostic, learner artifact, or human review. Prefer the
source when it already teaches well, and state why the treatment fits.

Assign each objective and treatment to `core`, `support`, or `enrichment` as
defined in the assessment intake. Build the default path from core plus the
minimum necessary support. Offer enrichment as an explicit choice without
letting it displace tested coverage or required course work.

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

Report, in files rather than chat: the course map, assessment and grading
profile, direct readings,
generated and still-needed artifacts, the practice and test plan, cited gaps
and conflicts, the evidence-based next action, every write performed with its
undo step, what is now stale because of the change (staleness marking has no
command yet; state it in the handoff), and remaining uncertainty. Keep
drafts distinguishable from accepted material. Run `python itembank.py
guard .` before any commit in this repository; never commit real course
content here.

```

## .agents/skills/curriculum-design/SKILL.md

```markdown
---
name: curriculum-design
description: "Design a source-grounded course from a syllabus, standards, exam blueprint, grading policy, or outline: separate taught, tested, and prerequisite scope; extract objectives; align sources and artifacts; choose treatments; define assessment and grading maps; identify cited gaps; and propose what to build next."
---

# Design a source-grounded curriculum

**Provenance:** rewritten 2026-08-14 (reframe slice 4b) to the operation
protocol in `.planning/research/phase-16/14-synthesis.md` section 10.

Read `../OPERATION-CONTRACT.md` first, then `.planning/AGENT-WORKFLOW.md`.
This skill owns the graph, authority, blueprint, prerequisites, pathways,
completion policy, source coverage, and migration proposals for a course.

Curriculum structure is a versioned typed graph with familiar outline
projections, not a universal tree. Structural order never implies
prerequisite status, and alignment never implies evidence transfer. Keep
coverage, completion, evidence, retention, staleness, and uncertainty as
separate progress dimensions, and keep accepted content, workflow state,
epistemic confidence, validation state, rights state, and availability as
separate state axes. Preserve every viable alternative path or treatment
with a durable disposition rather than silently dropping it.

The shipped product has no graph, course, or binding command. The objective
map today is a reviewable planning artifact (tables in a plan file) plus the
`[OBJECTIVE:]` lines in real banks, measured by shipped commands. The graph
kernel surface is pending (subphase 14B).

When the course includes an exam, graded assignment, competency check, or
completion threshold, read `../ASSESSMENT-INTAKE.md` and produce its assessment
profile before finalizing objectives or an assessment blueprint.

## 1. Declare the operation

State intent (a new map, a revision, a migration proposal), the approved
read roots, whether any source text may leave the machine, and whether this
pass is recommend-only or produces reviewed edits. This skill is normally
read-only: it proposes; `author-bank` and `absorb-book` write.

## 2. Get the ground truth

```bash
python itembank.py spec        # the format contract (objective naming, lesson refs)
python itembank.py stats bank.md      # item mix, objectives with counts, difficulty, position skew
python itembank.py coverage bank.md   # objective -> item tags, citation-backed via ## SOURCES
python itembank.py audit coverage --source source-file --bank bank.md   # source-versus-bank, read-only
```

`stats` is the item-mix and position report; `coverage` is the objective-to-
items map tied to the bank's `## SOURCES` registry. Run them before and
after you propose work. Coverage claims are grounded in this output or in a
cited source locator, never in prose intuition.

## 3. Extract the objectives

From the syllabus or blueprint, list every objective as a stable
hierarchical name the bank's `[OBJECTIVE:]` lines can share:

```text
Airway / positioning
Math 1400 / derivatives / chain rule
CSCI 1100 / loops / while
```

- Names must be exact-matchable: an item `[OBJECTIVE: Airway / positioning]`
  counts toward that objective and no other.
- Prefer a prefix hierarchy (`subject / topic / subtopic`) so the
  `evidence` command's `--objective` and `--prefix` filters work naturally.
- Preserve the target verb and cognitive demand. "Identify," "explain,"
  "apply," "analyze," and "perform" are not interchangeable.
- For standardized tests, record blueprint version, domain weights, item
  formats, timing, permitted tools, and tested depth. For knowledge courses,
  use the actual syllabus and instructor emphasis, not a generic exam.
- For publicly documented exams, search the current exam owner, candidate
  handbook, test plan, official samples, rules, and any question-pool authority
  before using third-party summaries. Bind all claims to effective dates.

Cite where each objective comes from. An objective without a source or
authority is labeled as your synthesis.

Separate three sets: taught objectives, assessed objectives, and prerequisite
knowledge. Record their intersections and exclusions. An objective can be
taught but untested, tested but assumed rather than taught, or required for
course completion without contributing to an exam score. Do not collapse these
states.

## 4. Establish prerequisites, pathways, and completion

For each objective, identify genuine prerequisites with a stated reason and
confidence; a heading sequence is not a prerequisite claim. Where
alternatives exist (two adequate paths to the same objective), record both
with a disposition instead of picking one silently. State the completion
policy: what evidence would count, and what stays pending or unknown.

## 5. Choose treatment per objective

Direct source reading, excerpt, guided lesson, notes or terms, worked
example, visual or demonstration, practice, test, assessment-first
diagnostic, learner artifact, or human review. Each treatment states its
purpose. Direct reading is a successful outcome, not a fallback.

Label each treatment `core`, `support`, or `enrichment`. Default sequencing and
coverage targets include core plus only the support needed to make core work.
Enrichment is opt-in unless the learner changes the target.

## 6. Map existing material and find the gaps

For each objective, record which lesson section (`### Heading`) teaches it,
which items test it (from `coverage` or `stats`, not filename guesses),
which item types and difficulties are used, and its status:

```text
Objective                    | Lesson section | Items | Types     | Status
Airway / positioning         | The Airway...  | 3     | mc, table | covered
Math 1400 / derivatives / .. | Chain Rule     | 1     | mc        | thin
CSCI 1100 / loops / while    | (missing)      | 0     | none      | gap
```

A gap is zero or thin coverage, a missing lesson section, or wrong demand
(all `recall` items for an `application` objective). Report gaps; never
paper over them. Unknown stays unknown.

## 7. Build the assessment blueprint

First complete the source-ranked assessment profile in
`../ASSESSMENT-INTAKE.md`. Then map objective weights or published ranges and
cognitive demand to item counts or ranges, difficulty, item families, feedback
mode, timing, permitted tools, scoring authority, and required changed-context
transfer. Preserve sampled versus guaranteed coverage. Do not use recall
questions as evidence for an application objective. Include diagnostic,
formative, and summative assessment only where the course needs them.

Match mock and summative item families to the documented exam format. A format
that the real exam does not use belongs only in explicitly justified teaching,
diagnostic, course-completion, or opt-in enrichment work. Record capability or
rights mismatches instead of quietly substituting a different test experience.

Create a separate grading map for every graded component. It records the
official weight, point and partial-credit model, rounding, pass or grade rule,
minimum section rules, pending-response treatment, review and appeal path,
retake effect, and reporting scale. Unknown policy stays pending. The grading
map describes authority; it never grades a learner or invents a threshold.

## 8. Propose the work and validate the proposal

For each gap, propose exactly what to write: the lesson section, and the
items with `[OBJECTIVE:]`, `[LESSON-REF:]`, and matching difficulty. Present
the proposal as a bounded, reviewable plan; hand item authoring to
`author-bank` and source treatments to `absorb-book` on approval. If the map
itself changes (renamed or split objectives), present that as a migration
proposal with its effect on existing `[OBJECTIVE:]` lines and evidence
filters, and mark dependent material stale in the handoff (staleness has no
command surface yet).

After approved writes land, re-measure instead of asserting:

```bash
python itembank.py lint bank.md
python itembank.py coverage bank.md
python itembank.py stats bank.md
```

## Boundaries

- This skill does not write banks or lessons; it proposes.
- Never claim standardized-test fidelity without a cited, versioned
  blueprint and completed assessment readiness gate.
- Never commit real banks or learner data to this repository.
- Report undo (which proposals were accepted and how to reverse them) and
  uncertainty (confidence per prerequisite and alignment claim) at close.

```

## .agents/skills/discovery-and-binding/SKILL.md

```markdown
---
name: discovery-and-binding
description: "Stub: discover sources and artifacts across approved roots and bind them to courses and objectives (root scopes, identity reconciliation, link and import semantics, conflicts, no mutation during inventory). Not usable yet; its command surface has not shipped."
---

# Discover and bind sources and artifacts (stub)

**Provenance:** stubbed 2026-08-14 (reframe slice 4b) per
`.planning/research/phase-16/14-synthesis.md` section 10.

**This skill is a stub; its command surface has not shipped.**

Intent: teach an agent client to run Loop A of the synthesis (declare read
roots and rights, scan read-only, identify by stable ID plus fingerprint,
preview and classify, surface duplicates, moves, conflicts, and unsupported
files, choose link, import, copy, move, or ignore, bind to objectives,
validate, checkpoint, and index) without mutating anything during
inventory and without ever merging artifacts by name similarity.

It will cover: root scope declaration, identity versus fingerprint versus
path reasoning (same ID with divergent bytes is a conflict; same
fingerprint with different IDs suggests a copy; a moved path with the same
ID is a move candidate), the distinct link, import, copy, move, and
supersede operations, conflict surfacing, and the derived disposable index.

Ships after: subphases 14A (identity, lifecycle, and operation prototype)
and 14B (graph and course package prototype), which supply the stable IDs,
fingerprints, operation journal, and binding records this skill would
document. Until then, discovery is the manual read-only inventory described
in `build-course` step 3 and `../OPERATION-CONTRACT.md`.

```

## .agents/skills/guiding-questions/SKILL.md

```markdown
---
name: guiding-questions
description: Run a Socratic tutoring session with the itembank JSON protocol. Use when a learner is sitting a quiz and you are the tutor: you present items, ask one diagnostic question at a time on a wrong answer, and never see or reveal the answer key.
---

# Guiding questions — tutoring with the JSON session protocol

You administer a session as an AI tutor. The runtime owns the key, the
scoring, the position, and the record; you own explanation and remediation.
You never scrape HTML and never reimplement scoring.

## 1. Start a session

```bash
python itembank.py start bank.md --mode practice --count 10 --out s.json
```

Modes the runtime supports: `diagnostic` (default, silent until the end),
`practice` (feedback as you go), `exam`, `remediation`, `drill`. Pick
`practice` for tutoring, `diagnostic` for a pre-test, `exam` for a formal
sitting.

Optional: `--objective "Airway / positioning"` to limit to one objective;
`--seed N` for a deterministic set.

## 2. Present the current item

```bash
python itembank.py next s.json
```

The response contains the `session_view` and the current `public_item`:
id, number, type, stem, options, response schema, lesson slug — **never the
key, rationale, or model text**. Present exactly that to the learner.

## 3. Receive and submit the answer

```bash
python itembank.py submit s.json --answer '"B"'          # mc: quoted letter
python itembank.py submit s.json --answer '["B","D"]'    # multi: JSON array
python itembank.py submit s.json --answer '{"row1":"A",...}'  # table/build/dnd
python itembank.py submit s.json --answer 'free prose'   # short: recorded, never scored
```

`submit` returns `{accepted, item_id, score, status, evidence, next}` and
advances the session. Replays are idempotent — a `dedupe_key` guards them.

## 4. On a wrong answer, ask ONE diagnostic question

The runtime has the rationale; you do not. What you may do, per the agent
usage contract:

- Ask **one** diagnostic question tied to the learner's *specific* wrong
  answer — never a generic "want to try again?"
- Offer one of the permitted explanation forms: analogy, example,
  counterexample, visualization, derivation, simulation, or a Socratic
  question — but only at the tier the runtime has granted for that content.
- On the next `next`, the learner re-sees the item and may submit again.

What you may **never** do:

- Reveal the answer key, the `WHY BEST` rationale, or any higher-tier content
  the runtime has not granted.
- Decide the hint tier, imply a score, or claim a `short` answer was graded.
- Replace the activity with generic chat, or retry indefinitely.

## 5. Escalate: tier-gated hints, rubric review, selection preview

The runtime owns the hint ladder — you never decide the tier. When the
learner is stuck, request one error-specific hint:

```bash
python itembank.py hint --session s.json            # one error-specific hint
python itembank.py hint --session s.json --retry    # regenerate as a parent-linked retry
```

`hint` returns the tier the runtime granted (`tier.index`, `unlock_path`),
falls back to the authored tier when offline, and never accepts a
caller-supplied tier (D-09). At most one generation per interaction id
unless `--retry` (D-12). Present only what the runtime returned — never the
key and never a higher tier.

For a `short` response, you may request rubric guidance but never settle a
mark:

```bash
python itembank.py rubric-review --session s.json   # pending per-point suggestions
```

A model suggestion surfaces as a single `pending` token until a human marks
the response (D-25) — never a score, check, or cross.

To preview what a selection will draw before starting a session (objective,
type, difficulty, count, seed), use the inspectable selection preview:

```bash
python itembank.py select bank.md --objective "Airway / positioning" --count 5 --explain
```

`--explain` prints the "why this item" trace; without it, the selection JSON.

## 6. Close with evidence

```bash
python itembank.py report s.json
```

`report` summarizes objective-level evidence and the manually-graded response
count. Hand the learner the honest picture: what is solid, what needs work.
If a `short` item is pending, say it is pending — do not guess a mark.

## Boundaries

- `short` answers score `None` until a marker grades them (`mark` command);
  keyword matching is not grading.
- The learner's evidence stays on disk next to the bank — never commit it.
- If the runtime refuses a tier or a reveal, that is the system's call; do not
  work around it in the prompt.

```

## .agents/skills/legacy-upgrade/SKILL.md

```markdown
---
name: legacy-upgrade
description: "Upgrade legacy lessons and question artifacts safely: run the eleven-item baseline audit, propose a bounded reviewable diff, reject cosmetic novelty, link derived enhancements the artifact cannot express, and halt on any keyed-meaning change (upgrade_audit.py, Phase 16C)."
---

# Upgrade a legacy artifact

**Provenance:** stubbed 2026-08-14 (reframe slice 4b) per
`.planning/research/phase-16/14-synthesis.md` section 10; shipped 2026-08-29
by plan 16C-08.

Older lessons and banks were written before capabilities that exist now. This
skill is how you make one of them better without losing anything it already
had, and without touching the one thing an upgrade may never touch.

## The order, which is not negotiable

**1. Audit before you edit.** Run `upgrade_audit.baseline_audit(bank_path)`.
It returns eleven rows in a fixed order: `current_parse`, `identity`,
`fingerprint`, `objectives`, `sources`, `rights`, `media`,
`assessment_boundaries`, `plain_rendering`, `rich_rendering`, `validation`.
Read them before proposing anything. There is no function that produces a
diff without auditing first, so this is a property of the code rather than a
rule you have to remember.

The `sources`, `rights`, and `media` rows read `plan-text stand-in` today,
because their backing records have not shipped. That is the honest answer,
not a pass. Do not report those three as checked, and do not fill them in
from your own reading of the artifact.

**2. Propose a bounded diff.** Every change carries `before`, `after`, and a
`reason` naming its learning value. A change whose reason is empty or reads
`cosmetic` is skipped with `Skipped: no learning value added.` and never
reaches the proposed list. If you cannot say what a change teaches better,
it is churn, and this tool will not offer it.

**3. Never apply the change yourself.** `upgrade_audit` reads and proposes.
It writes nothing on any path, including the halted one. Mutation goes
through the 14A journal operations under the operation contract in
`../OPERATION-CONTRACT.md`: expected base fingerprint, temp file, validate,
atomic commit, journal entry. Present the diff for human review and stop.

**4. Preserve identity and history.** An accepted upgrade never changes an
artifact's item IDs. The audit records identity before and after so a
reviewer can see that it did not.

**5. When the artifact cannot express an enhancement, link it beside.**
`upgrade_audit.cannot_express` renders the enhancement as a derived trio
projection and states the portability cost in words: the derived form lives
beside the file, not inside it, and does not travel when the file is copied
or exported alone. Say that cost out loud. An enhancement silently stored
beside an artifact is one someone loses in the first move and cannot explain
the absence of.

## The halt

`upgrade_audit.run_upgrade(bank_path, proposed_changes)` compares what the
upgrade WOULD produce against the original through
`upgrade_audit.keyed_meaning_delta`, which pairs items by id and watches
three things: the tested-content fingerprint, the difficulty, and the
objective alignment.

On any delta the run halts. The result carries `KEYED_HALT_COPY`:

> Halted: this change would alter keyed assessment meaning ({what}).
> Assessment changes are reviewed separately and are never part of an
> upgrade.

and exactly two affordances, `Open assessment review` and `Cancel upgrade`.
There is no third, no override, no force flag, and no diff on a halted
result. Do not offer the learner or the reviewer a way past it, and do not
build one: assessment meaning belongs to the runtime and its own review, and
an upgrade is not where it changes.

A rationale rewrite is not a keyed change. `model.content_fingerprint`
deliberately excludes `why`, `disc`, `trap`, and the rest of the reasoning
around an item, so improving an explanation is an ordinary proposed change
while rewriting a stem is a halt.

## Before you start

Read the "Course artifact workflow" section of `.claude/CLAUDE.md`, step 7 in
particular, and the operation protocol in `../OPERATION-CONTRACT.md`. A
worked fixture lives at `fixtures/legacy_pre135_bank.md` and the behavior
this skill describes is asserted in `tests/legacy_upgrade_roundtrip.py`.

```

## .agents/skills/lesson-authoring/SKILL.md

```markdown
---
name: lesson-authoring
description: "Stub: author semantic itembank lessons (teaching roles, complete portable Markdown, citations, accessibility, capability profile, render and lint loop). Not usable yet; its command surface has not shipped."
---

# Author a semantic lesson (stub)

**Provenance:** stubbed 2026-08-14 (reframe slice 4b) per
`.planning/research/phase-16/14-synthesis.md` section 10.

**This skill is a stub; its command surface has not shipped.**

Intent: teach an agent client to author lessons in the versioned semantic
lesson profile: semantic teaching roles (definitions, things-to-know,
expert tips, warnings, worked examples, inline checks, staged reveals),
complete core meaning readable in plain Markdown, citations with stable
locators, accessibility behavior per capability, the capability profile
declaration, and the render and lint loop for lesson validation.

It will cover: role vocabulary and when each earns its place, the portable
plain-file fallback for every rich behavior, citation and media rules,
keyboard, touch, and screen-reader behavior per capability, and the
deterministic validation loop for the lesson grammar.

Ships after: subphase 16A (semantic capability and activity contract),
which defines the lesson roles, capability profiles, and media and citation
policy this skill would document. Until then, author lessons through the
shipped `## LESSON` contract described in `absorb-book`, and consult
`../OPERATION-CONTRACT.md` for the operation protocol.

```

## .agents/skills/media-intake/SKILL.md

```markdown
---
name: media-intake
description: "Stub: bring images, diagrams, and other media into course artifacts with rights, credit, accessible alternatives, derivation records, local and remote policy, and stale tracking. Not usable yet; its command surface has not shipped."
---

# Intake media for course artifacts (stub)

**Provenance:** stubbed 2026-08-14 (reframe slice 4b) per
`.planning/research/phase-16/14-synthesis.md` section 10.

**This skill is a stub; its command surface has not shipped.**

Intent: teach an agent client to intake and manage media (images, diagrams,
audio, video stills) for lessons and items: rights and credit per asset,
required accessible alternatives (alt text, captions, described fallbacks),
derivation records for generated or converted media, local versus remote
storage and egress policy, and staleness tracking when a source asset
changes.

It will cover: per-asset rights grants (unknown stays restrictive), credit
and citation format, the accessible alternative every asset must carry,
derivation and conversion provenance, and how a changed or missing asset
marks dependent artifacts stale.

Ships after: subphase 16A (semantic capability and activity contract),
which owns the media and citation policy this skill would document. Until
then, media decisions are recorded manually per the rights and
accessibility rules in `../OPERATION-CONTRACT.md` and
`.planning/SOURCE-TO-COURSE.md`.

```

## .agents/skills/ocr/SKILL.md

```markdown
---
name: ocr
description: OCR images (screenshots, scans, photos) into text via a local Ollama vision model — the vision bridge for text-only models like DeepSeek.
---

# OCR — read text out of images

DeepSeek (and any other text-only model) **cannot see images**. When the user
provides an image — a file path, a screenshot, a scan, a pasted picture — do
not pretend to read it. Run the local OCR bridge and use the text it returns.

## When to use

- The user gives you an image path (`*.png`, `*.jpg`, `*.jpeg`, `*.webp`, `*.bmp`).
- The user pastes an image (save it to a file first, e.g. `tmp/pasted.png`, then OCR it).
- A task needs text from a screenshot, scan, or photo (e.g. a textbook page to
  turn into an itembank question bank).

## Binding a page as a cited source

Reading an image for your own use is what the rest of this skill covers, and
it is unchanged.

Turning a photographed or scanned page into a durable, citable course source
is a different operation, and it now exists:

```bash
python itembank.py source import --base <course-root> --file <image> --adapter ocr
```

or `POST /api/source/import` with `adapter` set to `ocr`. That path runs this
same bridge, writes derived Markdown plus a locator sidecar, records one
operation journal entry, and produces a source an objective can cite. Do not
build a second way to do it.

The sidecar honestly records `bbox` and `confidence` as null, because this
bridge transcribes text and does not measure where on the page it sat. A
citation into an OCR source names the page, not a region. If you need
region-level citation, that is a change to this skill's output contract and a
locator schema version bump, not something to work around by guessing
coordinates.

The envelope confidence for an OCR source is `low` by design. Treat an OCR
transcription as the least reliable source in the course, and prefer a
text-bearing original whenever one exists.

## How to run it

```bash
python scripts/ocr.py <image-path> [more-images...]
```

The command prints the transcribed text to stdout, preserving reading order and
language. Useful variants:

```bash
python scripts/ocr.py --models                 # list models Ollama has
python scripts/ocr.py --model qwen2.5vl:7b img.png   # pick a specific model
python scripts/ocr.py --json img.png           # machine-readable output
```

If the `ocr` MCP plugin is registered (see `reasonix.toml` `[[plugins]]`), the
`ocr_image` tool is the equivalent first-class tool call — same result.

## Rules

1. **Never claim you saw the image.** You only ever see the text OCR returns.
   Say "the OCR reads: …" when relaying it, or just use it as source material.
2. **Don't invent content.** If the OCR output is garbled or has gaps, say so
   instead of guessing the missing text.
3. **Keep the original language.** OCR preserves it; do not translate the source
   text when the goal is transcription/authoring (itembank keeps original wording).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `model 'qwen2.5vl:7b' not found` | `ollama pull qwen2.5vl:7b` (on the host running Ollama) |
| `no Ollama server reachable` | Start Ollama, or set `OLLAMA_HOST` (e.g. `http://localhost:11434`); the script auto-probes localhost then the WSL gateway |
| OCR quality poor on handwriting/figures | Try a stronger vision model (`ollama pull qwen2.5vl:11b` / `llama3.2-vision`) via `--model` |

## Environment

- `OLLAMA_HOST` — endpoint override (default: auto-probe `localhost:11434`, then WSL2 gateway).
- `OCR_MODEL` — default vision model (default: `qwen2.5vl:7b`).

```

## .agents/skills/user-vision/SKILL.md

```markdown
---
name: user-vision
description: >
  Capture a user's product vision in their exact words, interpret it in a
  visibly separate layer, give every idea a durable disposition instead of
  deleting it, and drift-audit a planning pass before it closes. Use when
  starting or steering a project from rough ideaboarding, when a later idea
  changes an earlier direction, when deciding what belongs in a vision record
  versus a research or planning file, or when an agent must continue a project
  without flattening the user's intent. Portable across projects and agent
  clients (Claude Code, Codex, local agents).
---

# User Vision: capture, disposition, drift-audit

This skill preserves a user's product vision so a capable agent can continue a
project without flattening intent, repeating research, silently dropping ideas,
or turning provisional findings into commitments. It is subject-neutral. It
governs a records process, not any specific product's runtime.

It has three jobs, done in order and repeated as the project evolves:

1. **Capture** the user's meaning in their own words, with interpretation kept
   visibly separate from the quotation.
2. **Disposition** every substantial idea into a durable route rather than
   reducing the set for neatness.
3. **Drift-audit** a planning or direction pass before closing it, so the record
   stays honest about what is user intent, what is inference, and what is a
   commitment.

## Deference: the host project wins

This skill describes a records process. It never outranks the project it is
installed into. When this skill and the host project's own contract, workflow,
or planning directives disagree, **the project's files win** and this skill is
the generic fallback. Name that file at install time, here:

> Host contract for this installation: `.planning/AGENT-WORKFLOW.md` sections 2, 5 and 10, under `.planning/SOURCE-TO-COURSE.md` and `.claude/skills/OPERATION-CONTRACT.md`. Those win on any disagreement. The live records are `.planning/USER-VISION.md`, `.planning/USER-VISION-INBOX.md` and `.planning/IDEA-LEDGER.md`; the templates here are not to be copied over them, and the audit is `python3 scripts/vision_audit.py`.

If the host already runs an equivalent process under different file names, do
not create a second copy. Adopt the existing files and treat the templates below
as a description of what those files should contain. Two ledgers with the same
purpose is the failure this skill is supposed to prevent, not a clean install.

## When to use this

- A project is starting from rough, contradictory, or exploratory ideaboarding.
- A new statement seems to change an earlier direction and both must survive.
- You are deciding what belongs in the authoritative vision versus a research or
  planning file.
- Another agent (or a future you) must pick up the project cold.
- You are about to write requirements and want to preserve breadth without
  shipping everything at once.

## Core rule: three separate layers

Keep these three visibly distinct at all times. Collapsing them is the failure
this skill exists to prevent.

| Layer | What it holds | Editing rule |
|-------|---------------|--------------|
| **Quotation** | The user's exact words | Never rewritten. Never silently corrected. Append-only, dated. |
| **Interpretation** | What the words mean for the product | Dated. Sits below the quote. Superseded, never overwritten. |
| **Decision** | The commitment a contract or plan settled | Lives in the owning contract/requirements/plan file, linked back. |

A summary is never allowed to stand in for the user's words. When the layers
appear to conflict, reread the quotation, record the conflict, trace each
statement to its origin, and resolve it in the owning document. Do not default
to the most recent summary.

## 1. Capture

Every meaningful user statement first enters the capture funnel
(`templates/USER-VISION-INBOX.md`), verbatim. Then decide its route:

- **Promote** to the authoritative vision (`templates/USER-VISION.md`) only
  statements about outcomes, experience, scope, values, boundaries, users,
  success, or unresolved product direction.
- **Route** implementation guesses, tool choices, links, task mechanics, and
  research leads to their owning research or planning file. Keep the verbatim
  copy in the inbox with a link.
- **Split** a mixed statement: promote the product-intent clauses, route the
  implementation clauses.
- **Hold** anything whose meaning is not yet stable.
- **Duplicate**: link to the earlier statement it restates without adding a
  second authoritative copy.

**Entry headings must be machine-readable, because something will parse them.**
Use `### YYYY-MM-DD: title`, with a colon, a hyphen, or a dash as the separator,
and keep one format for the whole file. A comma after the date reads fine to a
human and defeats a date-anchored regex, which means the entry silently drops
out of every audit that walks the file. Pick the separator the host project's
existing entries already use before adding the first new one.

Preserve the wording even when it is rough, misspelled, or self-contradictory.
Do not require a statement to be rewritten as a requirement before recording it.

When you promote a statement, attach a dated interpretation note directly below
the quotation using the five fields in `references/interpretation-protocol.md`:
Status, Current interpretation, Open questions, Planning effect, Relationship to
earlier entries. Read that file before writing any interpretation.

## 2. Disposition

Coalescing a project into one coherent product does not mean deleting ideas for
minimalism. Every substantial proposal receives exactly one disposition and is
recorded in the project's idea ledger. **If the project already keeps one, under
any name, use it.** The template here is a shape to check an existing ledger
against, not a file to add beside it. The seven dispositions and their
required fields are defined in `references/disposition-vocabulary.md`; read it
before assigning one.

The dispositions are: **Core, Registered, Prototype, Backburner, Deferred,
Superseded, Rejected.**

Two rules bind hardest:

- **Simplicity alone is never a rejection reason.** A viable idea that does not
  fit now becomes Backburner or Deferred with a revisit trigger, not a deletion.
- **The rejection ledger is append-only.** A rejected idea keeps its original
  proposal, origin, evidence considered, exact reason, conflicting rule,
  retained alternatives, date, and reconsideration condition. It is never
  silently removed.

## 3. Drift-audit

Before closing a planning or product-direction pass, run the checklist in
`references/drift-audit.md`. It verifies that statements were captured or
deliberately routed, that interpretation stayed separate from quotation, that
research conclusions did not silently become commitments, that every viable idea
has a disposition, and that rejections carry evidence and a reconsideration
condition. A pass does not close until the audit passes or its failures are
recorded as open items.

**Items 8 and 9 of that checklist are placeholders and must be filled at install
time**, with the host project's own invariants and style rules. An unfilled
placeholder makes the audit weaker than whatever the project was already doing,
which is a regression disguised as adoption. If the project has its own drift
audit, keep the project's items and use this file only to check for gaps.

## Files in this skill

- `templates/USER-VISION.md`: the authoritative, verbatim-plus-interpretation
  record. Adopt the project's equivalent if one exists; copy this only if none does.
- `templates/USER-VISION-INBOX.md`: the capture funnel for rough ideaboarding.
- `templates/DISPOSITION-LEDGER.md`: the durable route for every idea.
- `references/interpretation-protocol.md`: the five-field interpretation note
  and the rule for changing an interpretation without erasing the old one.
- `references/disposition-vocabulary.md`: the seven dispositions and their
  required fields.
- `references/drift-audit.md`: the closing checklist for a planning pass.

## Installing into a project

Drop this directory into a project's skills path (for Claude Code:
`.claude/skills/user-vision/`). If the project mirrors its skills across agent
clients, install into every mirrored tree, or its byte-identical mirror check
will fail.

**Then inventory before you copy anything.** Look for a vision record, a capture
funnel, and an idea ledger that already exist under other names. Adopt what is
there. Copy a template into the project's planning directory only for a record
the project does not already keep, and never over a file that has content: the
templates are empty scaffolds and would destroy a live record. Fill in the host
contract path above, the drift-audit placeholders, and the field names the
project's own tooling greps for. The `references/` files stay in the skill and
are read on demand.

**Then regenerate whatever the host derives from its skill tree, and run the
host's own checks.** Installing a skill is not always purely additive: a project
may ship a generated manifest, index, or capability file that enumerates its
skills, and adding a directory makes that artifact stale and its test fail. Look
for a generator before assuming a copy is the whole install.

## Adapting per project

This skill carries no product-specific rules. A project layers its own
non-negotiables (its runtime invariants, authority boundaries, house style)
on top, in its own contract file, and links them from the vision record's
interpretation pointers. Keep the process generic here; keep the product rules
in the project.

## Status

Version 0.2, 2026-09-04. The capture and interpretation protocol is stable. The
disposition and conflict-resolution rules are still expected to change once a
project stress-tests a real "a later idea changed an earlier direction"
resolution end to end. Treat the API as pre-1.0.

**What 0.2 changed, and why.** v0.1 was extracted from one project and then
installed back into it, which surfaced five faults that are invisible from
inside the project a skill came from: no deference rule, so nothing said which
copy wins; a ledger template that duplicated an 82KB ledger already running the
same seven dispositions; an interpretation field named differently from the
record it was extracted from, so a grep for it found nothing; a template entry
heading whose comma separator the host's audit script could not parse; and a
drift audit whose two project-specific slots shipped empty, making it weaker
than the audit it replaced. Running the host's full preflight then found a sixth
that no amount of reading would have shown: the host generates a capability
manifest from its skill directories, so the install broke one of its tests until
that manifest was regenerated. All six are addressed above. **The pattern behind
them: a generic skill fails at the seams where it meets a project that already
has a process, not in its own body text.**

```

## .agents/skills/user-vision/references/drift-audit.md

```markdown
# Drift audit

Run this before closing a planning or product-direction pass. Its job is to
catch the record drifting away from the user's actual intent: a summary standing
in for the words, a research guess hardening into a commitment, a viable idea
quietly dropped. A pass does not close until this audit passes or its failures
are written down as open items.

## Checklist

1. **Capture:** every meaningful user statement from this pass was captured
   verbatim or deliberately routed to its owning file. None was paraphrased away.
2. **Separation:** interpretations stay visibly separate from quotations. No
   quotation was edited to match a new reading.
3. **No silent commitments:** research conclusions did not become product
   commitments without a recorded decision. A finding is still a finding until a
   contract or plan accepts it.
4. **Every idea routed:** every viable idea has one durable disposition. Nothing
   substantial is sitting undecided or silently dropped.
5. **Rejections are honest:** each rejection carries evidence, the conflicting
   rule, retained alternatives, and a reconsideration condition. None was removed.
6. **Conflicts stay visible:** where a later statement changed an earlier one,
   both survive, the older interpretation is marked, and a dated resolution links
   them.
7. **Instructions match the contract:** agent-facing instructions match the
   binding product contract. No instruction file contradicts the accepted
   direction.
8. **Product invariants intact:** no plan from this pass weakens a named
   non-negotiable the project declared (its authority boundaries, safety gates,
   or quality promises). Fill in the project's specific invariants here.
9. **House style:** the pass respects the project's own prose and formatting
   rules in generated text.

## What a failed item means

A failed item is not a blocker by itself. It becomes an explicit open item with
an owner and a next action, recorded in the owning file, so the next agent sees
it. The failure this audit exists to prevent is the silent kind: drift that no
one wrote down and no one can later trace.

## Adapting per project

Items 8 and 9 are placeholders for project-specific rules. A project fills them
with its own invariants and style rules and links them from the vision record's
interpretation pointers. The other seven items are generic and apply to any
project using this skill.

**Fill them at install time, not later.** An unfilled placeholder silently drops
whatever the project was already checking. Real examples worth stealing, from
the project this skill was extracted from: mirrored skill trees stay
byte-identical, no plan weakens the one-parser and one-evidence-store boundary,
and no em dash characters appear outside verbatim quotations. Add an item for
any check the project's own tooling can run, and name the command next to it, so
the audit says what to type rather than what to remember.

```

## .claude/CLAUDE.md

```markdown
<!-- GSD:project-start source:PROJECT.md -->

<!-- CONTEXT BUDGET, a standing rule for this file.
     This file is loaded in full on every session and in every subagent, so
     its size is charged unconditionally. It was 37.9KB (~9.5k tokens per
     session, per subagent) until 2026-08-29 and is now held near 16KB by
     keeping rules that bind and pointers to detail, never inlined reference
     material rediscoverable from the code or from .planning/. If it passes
     ~18KB, something reference-shaped has crept back in.
     `gsd-tools generate-claude-md` will re-inline the full text of
     .planning/PROJECT.md and .planning/codebase/*.md into the marker blocks
     below and undo that. If you regenerate, re-apply this trim. -->

## Project

**itembank** is a source-to-course learning workspace built on a local-first
assessment protocol and runtime. It ships today: a markdown format contract
with an actionable linter, seven item types, deterministic scoring behind one
scorer, resumable JSON sessions, an offline HTML quiz, a graded loopback
sitting, Anki TSV export, and a cross-subject `day` cockpit.

The next milestone turns learner-owned books, syllabi, exam blueprints, notes,
existing banks, and folders into a coherent course: discover and bind sources,
build a cited objective and prerequisite map, choose the right treatment per
objective (including direct source reading), create missing artifacts, provide
guided teaching and practice where useful, and revise the path from recorded
evidence. A capable model is a first-class course builder, analyst, and
optional teaching collaborator, not the sole teaching surface.

One learner, Weibao, across EMT, Math 1400, and CSCI 1100, with AI tutors as
first-class clients of the same runtime a human uses.

**Product North Star:** **Learner-owned sources become an inspectable,
high-quality, AI-operable course whose readings, lessons, practice, tests, and
next actions are aligned to cited objectives and improved by honest evidence.**

**Runtime invariant:** **One runtime, one scorer, one evidence store, and the
runtime, not the model, settles scoring, assessment disclosure, and evidence.**

The tutoring model reads the item, the key, the rationale, and the learner's
specific wrong answer, so it can teach about *this* error. What it may not do
is choose how much to say: the runtime gates disclosure by session mode and
hint tier, so a model argued into wanting to reveal still cannot.

This is a small safety boundary, not a capability ceiling. AI may search
approved roots, design curricula, select readings, draft and revise artifacts,
interpret metrics, propose remediation, and perform approved bounded writes.
New scoring behavior (partial credit, semantic short-answer matching,
AI-proposed marks, new item types) belongs *inside* the one scorer as an
additive extension; advisory graders may propose a mark but never settle one.
A feature is wrong only if it needs a second, competing authority.

### The five non-negotiables

1. The runtime owns correctness, session state, evidence, and keyed
   assessment disclosure.
2. Exactly one parser, one scorer, one evidence store.
3. Evidence and banks stay on disk. No telemetry, no vendor-held data.
   Learner-initiated export, backup, and device sync are legitimate features
   gated by the export and share rights grants.
4. Format changes are additive. A bank without a `LESSON` section must parse
   as it does today. Additive does not mean permanent: an element may be
   deprecated with documentation and retired through an explicit `migrate`
   operation. Only *silent* breakage is forbidden.
5. The accessibility gates in `.planning/UI-SPEC.md` hold.

Everything else once listed as a constraint (Python-stdlib-only, no build
step, Python-only, offline-first) is a **preference**, relaxed 2026-08-09 by
Weibao. Dependencies, bundlers, npm, and non-Python components are permitted
when they earn their cost. A packaged desktop app is an end goal. Judge ideas
on product merit and report real cost. The core loop must still **degrade,
never block**: sitting a quiz, scoring, lessons, the authored hint ladder,
evidence, and reports all work with the network unplugged.

### Prose style rule

Do not use em dash characters in repository-authored prose, documentation,
comments, fixtures, generated lessons, or questions. Use commas, parentheses,
colons, semicolons, or separate sentences instead. Verbatim source quotations
and additive statements in `.planning/USER-VISION.md` are the only exceptions.

### Reading before consequential work (read sections, not whole files)

These files are large. Read the section you need, not the file.

| Need | Read |
|---|---|
| Binding next-milestone scope | `.planning/SOURCE-TO-COURSE.md` (17KB, read whole) |
| Shared agent operating contract | `.planning/AGENT-WORKFLOW.md` (10KB, read whole) |
| Object, authority, rights, acceptance, recovery detail | `AGENTS.md` §"Object and authority model" |
| Weibao's verbatim goal | `.planning/USER-VISION.md` (85KB). Grep it. Never replace the record with an interpreted summary. |
| Full authority synthesis | `.planning/research/phase-16/14-synthesis.md` §2, §3, §6, §10 (84KB total) |
| Current phase and state | `.planning/STATE.md` (17KB). Read "Current position" only; the log through 2026-08-30 is archived. |
| Roadmap | `.planning/ROADMAP.md` (120KB). Read the "Phases" checklist and the subphase table's Status column for status; read one phase's detail block only when planning it. |
| Idea dispositions | `.planning/IDEA-LEDGER.md` (82KB). Grep by ID. |
| Requirement wording by ID | `.planning/REQUIREMENTS.md` (97KB). Grep the ID. Its checkboxes are not status; see its header note. |
| How a past decision was reached | `.planning/archive/` (index in its README). Never for current status. |
| Stack, conventions, architecture detail | `.planning/codebase/*.md` |

### Object, authority, and operation summary

Full text: `AGENTS.md` §"Object and authority model", which is the mirror of
record. The rules that gate every change:

- **Authority.** The learner owns goals, private notes, scratch work, strategy
  choice, and evidence export. A course builder defines scope, treatments, and
  paths within source and rights limits. A reviewer accepts or rejects. An
  agent discovers, aligns, drafts, validates, and explains within an operation
  manifest, and never owns accepted truth or assessment authority. The runtime
  is the sole authority for session state, keyed disclosure, scoring, and
  attempt evidence.
- **Durable versus derived.** Accepted files are canonical. Indexes, HTML,
  caches, rankings, and progress views are derived and disposable, and never
  become the only understandable copy.
- **Separate state axes.** Accepted content, workflow state, epistemic
  confidence, validation state, rights state, and availability are
  independent. Do not collapse them.
- **Compare-and-swap mutation.** Every durable write states an expected base
  fingerprint, writes to a temporary file, validates, commits atomically, and
  journals the operation, so any fault leaves the old or new valid state.
  Link, import, copy, move, edit-in-place, supersede, migrate, and synchronize
  are distinct operations, not synonyms. Same ID with divergent bytes is a
  conflict, never a silent overwrite.
- **Rights and egress are per operation.** Read, quote, transform,
  remote-process, package, export, and share are separate grants. Unknown
  rights stay restrictive. Hosted operations minimize and disclose egress.
- **Learner notes** never silently become source truth, lesson truth, answer
  keys, scores, or mastery. Presentation state never grants authorization.
- **Accessibility** review (keyboard, touch, screen reader, zoom and reflow,
  high contrast, reduced motion) covers representative outputs: sampled per
  template or capability profile, full when a template or interaction pattern
  changes. An agent never self-certifies.
- **Clean recovery.** Export is not complete until a clean-machine, offline
  restore validates a manifest and reports every loss. Interrupted, offline,
  denied, future-schema, and agent-unavailable states preserve the last
  accepted state and expose the next safe action.
- **Append-only ledger.** Every viable idea keeps a disposition (core,
  registered, prototype, backburner, deferred). Untimely is not rejected, and
  simplicity alone is not a rejection reason. Rejections record evidence,
  reason, conflicting rule, retained alternative, date, and reconsideration
  condition, and are never deleted. Append-only forbids deleting records, not
  archiving or compacting completed-milestone ledgers into summaries that
  point at the full record.
- **One operation protocol.** Declare intent and declare approved roots,
  rights, egress, write, and execute authority; inventory before creating;
  plan treatment; checkpoint; draft the smallest missing artifact; cite and
  label synthesis; validate deterministically; show an accessible plain and
  rich preview; present a bounded diff; pass configured review; accept
  atomically; update dependency and staleness state; report undo and
  uncertainty. Backend choice changes cost, latency, and disclosure, not the
  artifact or authority contract.

### Course artifact workflow

Full text: `AGENTS.md` §"Course artifact workflow". Before creating a lesson,
question set, bank, activity, or exam, in order:

1. **Inventory** sources and artifacts across every user-approved root (course
   folders, source folders, an Obsidian vault) with location, stable identity,
   fingerprint, ownership, provenance, objective links, draft or accepted
   state, and validation status. Discovery is read-only and authorizes no
   mutation.
2. **Reconcile** duplicates, moved files, stale links, and conflicting
   versions. Never identify or merge artifacts from filenames alone.
3. **Map** the cited objectives and prerequisites, and choose the treatment
   per objective (direct reading included) before generating anything.
4. **Reuse or link** an adequate existing artifact. Linking, importing,
   copying, moving, and superseding are distinct; provenance is preserved.
5. **Create** only genuinely missing treatments, through the relevant skill
   and the format contract. Label synthesis and retain citations.
6. **Verify** lessons in both forms: the durable authored document (coherent
   in plain Markdown or Obsidian) and the richer itembank presentation.
7. **Audit before editing** legacy material. Preserve stable identity and
   history, retain static and accessibility fallbacks, present a bounded diff.
   Never silently change keyed content, assessment meaning, difficulty, or
   objective alignment.
8. **Reindex and report** disposable discovery data, validated links, changes,
   uncertainties, and reversal steps.

Agent skills are part of the product interface and must work as portable
playbooks for Claude, Codex, and other clients against the same runtime and
artifact contracts.

### Accepted risks, recorded so they are not rediscovered

- **Hosted models see item text** (Weibao, 2026-08-05). AAOS-12e-derivative
  EMT items and CSCI 1100 items transit to a hosted provider. Hosted or local,
  this is AI assistance on graded coursework and the CSCI 1100 AI-use ban
  applies to both. The local-only path stays fully built, so any subject moves
  back behind it by changing one setting.
- **The `update_policy` divergence is deliberate** (D-13, 2026-08-08). The
  schema default is `opt_in` so a fresh install never phones home unasked;
  this repository's own `itembank.json` sets `check_on_launch` so the updater
  is dogfooded. The two values are meant to differ.
- **External installations are now a supported goal** (2026-08-14), scoped as
  Phase 18. The original "one learner, no design work spent on others" wording
  is superseded; no-accounts and no-multi-tenancy still bind.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

Python 3.11+, standard library only as built today (`json`, `re`, `os`, `sys`,
`collections`, `argparse`, `html`, `http.server`, `socketserver`, `random`).
No install step, no build system, no lockfile, no `requirements.txt`. Two
vendored exceptions: a KaTeX asset for Math rendering and stdlib `urllib` for
the opt-in updater. CI pins two optional LTI deps (`cryptography`, `PyJWT`)
that the core loop must never import.

This describes the stack **as built**, not a forward constraint. See the five
non-negotiables above. Optional integrations: Anki Desktop via AnkiConnect
(`ANKI_CONNECT_URL`), git for `day`'s status line.

Entry points: `python itembank.py [COMMAND]`, or `import itembank` for the
public API in `__all__`. Single-threaded, stateless, no daemon, no database.

Detail: `.planning/codebase/STACK.md`, `INTEGRATIONS.md`, `TESTING.md`.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Match the surrounding code. No linter or formatter is configured; formatting
is manual, 4 spaces, `%`-style string formatting throughout.

- snake_case modules, functions, and variables. UPPERCASE module constants.
- Command handlers use a `cmd_` prefix (`cmd_lint`, `cmd_serve`) and take an
  argparse `Namespace`.
- Tests are `tests/*_roundtrip.py` (plus `*_check.py`, `*_tracer.py`, audits).
  CI runs every `tests/*.py`.
- No private underscore-prefixed functions; everything module-level is
  importable. `__all__` exists only in `itembank.py`.
- Direct imports, never `import *`, no barrel files, no path aliases.
- CLI errors use `sys.exit("message")`. Validation accumulates into
  `(errors, warnings)` lists of `"Qn: message"` strings. `None` means unknown
  or not-yet-marked, `False` means wrong, `""` means missing data.
- Docstrings explain WHY and WHAT, not HOW, and often restate the invariant
  the function protects. Comments are complete sentences.
- Canonical form separators are `FIELD_SEP = "\x1f"` and `PAIR_SEP = "\x1e"`,
  chosen because item content contains `|`, `>`, and `,`.
- Item types: `mc`, `multi`, `table`, `dnd`, `build`, `short`.

Detail: `.planning/codebase/CONVENTIONS.md`.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:codebase/ARCHITECTURE.md -->
## Architecture

Four layers. The boundaries are the design.

| Layer | Responsibility | Files |
|---|---|---|
| Model | Format contract, parsing, validation | `model.py` |
| Runtime | The only scorer; sessions; public/private payload visibility | `runtime.py` |
| Server | Loopback HTTP handler and port fallback | `server.py` |
| Surfaces | Rendering and interaction, all of them clients | `surfaces/*.py` |
| Entry | Command routing | `itembank.py`, `surfaces/cli.py` |

Key abstractions: `public_item()` is what a learner sees before answering (no
key); `explain_payload()` is what they see after; `canonical_response()`
reduces any response to a comparable string so the offline page and the
scorer cannot disagree about what a response *is*; sessions are JSON in
`_attempts/session_*.json` holding item indices, a cursor, and responses.

Architectural constraints, all enforced by the layering:

- Every surface reaches a verdict through `runtime.score_response()`. No
  surface reimplements grading.
- Every surface loads banks through `model.load()`. Nothing else parses.
- No circular imports, no global state, no module-level caches.
- Session writes are atomic (`.tmp` then `os.replace`), so a session is safe
  to read while being written.
- No database. Markdown and JSON on disk.

Anti-patterns, each of which has bitten this repo: scoring in more than one
place, parsing the bank more than once per invocation, leaking answer keys to
the browser before the learner answers, and long operations with no progress
output.

Detail: `.planning/codebase/ARCHITECTURE.md`, `STRUCTURE.md`, `CONCERNS.md`.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

`.claude/skills/` and `.agents/skills/` are byte-identical mirrors, enforced
by CI (`diff -rq`), and share `OPERATION-CONTRACT.md`. Shipped: `absorb-book`,
`author-bank`, `build-course`, `curriculum-design`, `guiding-questions`,
`legacy-upgrade`, `ocr`. Stubs whose command surface has not shipped:
`discovery-and-binding`, `lesson-authoring`, `media-intake`.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Treat GSD as guidance and structure, not mandatory ceremony. Use it when it
earns its tokens: real phase work, multi-step execution, or anything where the
planner/executor/verifier structure genuinely improves the outcome. For small
doc edits and ad-hoc changes, edit files directly and commit with plain `git`;
loading the full framework or the `gsd-sdk` wrapper for one-line changes wastes
tokens.

Entry points, when the structure pays for itself:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

```

## .planning/EXEC-CONTEXT.md

```markdown
# Execution context (read this instead of the planning stack)

Written 2026-08-20 to cut the standing prompt for cheap execution runs.
An executor reads ONLY this file plus the one `*-PLAN.md` it was given.
Do not read ROADMAP.md, REQUIREMENTS.md, STATE.md, UI-SPEC.md,
AGENT-WORKFLOW.md, PLANNING-DIRECTIVES.md, or SOURCE-TO-COURSE.md.
Those are planning documents. The plan you were handed already cites
whatever it needs from them.

## Act first

Write a file or run a command in your first turn. Do not restate the plan,
do not summarize these rules, do not produce an analysis section. If a
task is ambiguous, pick the reading that changes the least and note it in
one line in the commit body. Reasoning longer than the code you are about
to write means you are spending the budget in the wrong place.

## Five rules you cannot break

1. The runtime owns correctness, session state, evidence, and keyed
   assessment disclosure. A model never settles a score or decides how
   much of a key to reveal.
2. Exactly one parser (`model.py`), one scorer (`runtime.py`), one
   evidence store. Never add a second. New scoring behavior is an additive
   extension inside the existing scorer.
3. Evidence and banks stay on disk. No telemetry, no cloud sync.
4. Format changes are additive. A bank without a `LESSON` section must
   parse exactly as it does today.
5. Accessibility gates in `UI-SPEC.md` section 8 hold for UI work. If your
   plan does not touch UI, this rule does not apply to you.

## Prose rule

No em dash characters anywhere: not in code, comments, docstrings,
fixtures, commit messages, or generated content. Use commas, colons,
parentheses, or two sentences.

## Layout

- `model.py` parse and lint, the format contract
- `runtime.py` scoring, sessions, public and private payloads
- `identity.py` ids, fingerprints, revision records, rights state
- `journal.py` compare-and-swap writes and the operation journal
- `discovery.py` read-only walk of approved roots
- `server.py` loopback HTTP handler
- `surfaces/` CLI, quiz, study, day, session, anki, export clients
- `tests/*_roundtrip.py` one suite per area, plain scripts, no pytest

## Verify

Run the suites your plan names, plus any suite covering a file you edited:

    python tests/<name>_roundtrip.py

Exit code 0 is pass. Known failure not caused by you:
`tests/journal_roundtrip.py` fails in `check_lock_busy` on Windows with
`PermissionError` from `msvcrt.locking` unlock. Do not chase it unless
your plan is about file locking.

Python 3.11+, standard library only for runtime code.

## Commit

One commit per plan task, atomic, conventional prefix and the plan id:

    feat(14B-01): add the typed graph kernel
    test(14B-01): graph roundtrip over three domains
    fix(14B-01): reject an edge whose endpoint is unknown

Limit every commit to a pathspec you name explicitly. Do not use a bare
`git commit -a`. Another agent may share this working tree.

## Do not write a summary unless one of two things is true

Added 2026-08-21 after Weibao measured the cost. There are 129 `-SUMMARY.md`
files holding 23,261 lines, which is more than half the size of the entire
runtime. Most of them restate commit messages that already said the same thing
in more detail.

**The commit messages are the record.** Write them properly: what was wrong,
what you changed, what you measured, and what you did not do. A reader with
`git log` should need nothing else.

Write a `-SUMMARY.md` only when:

1. **The plan was left incomplete.** Name exactly what is not built and why,
   so nobody later reads a closed plan as a finished feature.
2. **You found something that contradicts the plan.** A measured fact that
   makes a plan task wrong, unnecessary, or impossible. Record the measurement
   and the date.

A plan whose `<summary_obligations>` block asks for a summary does not override
this. If neither condition holds, satisfy the obligation in the commit body and
move on. Ceremony that nobody reads is money spent on nothing.

Enforced mechanically since 2026-09-03 by `scripts/summary_gate.py`, run in CI
and by `scripts/preflight.py`. A summary not listed in
`.planning/summary-baseline.txt` must open with the heading
`## Why this summary exists`, stating which of the two conditions holds, and
must stay under 3,000 bytes. Do not write summaries retrospectively for plans
that already closed; the commit log is their record. Do not edit the baseline
to pass a build.

## When you are stuck

Write what you tried and what blocked you into the plan's `-SUMMARY.md`,
commit that, and stop. Do not loop. Do not redesign the plan.

```

## AGENTS.md

```markdown
# AGENTS.md - itembank for AI coding agents

This file is the universal on-ramp for AI coding agents (OpenAI Codex, Claude
Code, Cursor, Gemini CLI, and anything else that reads `AGENTS.md`). Read this
first, then the files it points at. Claude Code should also load
`.claude/CLAUDE.md`, which carries the full GSD project context.

## What this repo is

`itembank` is becoming a source-to-course learning workspace. It turns books,
syllabi, exam blueprints, notes, existing banks, and other learner-owned files
into an objective map and a tangible course: direct readings where the source
is best, guided lessons where synthesis helps, key terms and notes, worked
examples, interactive explanations, practice, and formal tests. Evidence then
informs the next activity and future course revisions.

The shipped foundation is a local-first assessment protocol and runtime.
Question banks are plain markdown; the tool validates them, renders lessons and
offline quizzes, runs graded sittings, records evidence, audits source coverage,
and exposes deterministic JSON sessions. A hosted coding-agent client or a
registered local model may drive discovery, course design, authoring, analysis,
and remediation, but accepted artifacts remain inspectable files and
deterministic scoring remains in the runtime.

The useful artifact is the **contract**: `itembank spec` prints the format,
`itembank lint` tells an author exactly what it got wrong, by item number, in
language it can act on. Authoring becomes write, check, fix.

The binding next-milestone product contract is
`.planning/SOURCE-TO-COURSE.md`. Read it before planning course, source, agent,
authoring, metrics, or learner-UI work. The course is the user-facing unit;
objectives are its spine; a bank is one assessment artifact inside it.
`.planning/USER-VISION.md` preserves the user's goal verbatim. Never overwrite
it with a summary; append new dated statements and keep interpretations in the
product contract and plans.

The binding cross-agent workflow is `.planning/AGENT-WORKFLOW.md`. Read it
before consequential course, source, lesson, assessment, UI, research,
migration, or product-direction work. It defines vision capture, ideaboarding,
research waves, synthesis, dispositions, authority checks, safe operations,
readiness audits, and handoffs for Codex, Claude Code/Cowork, local agents, and
other clients.

## The four layers (boundaries are the design)

```
model.py                  what a bank is, and what makes one invalid (one parser)
runtime.py                the only scorer; decides what a surface may see
server.py                 one loopback HTTP server
surfaces/                 clients only: quiz, study, day, session, CLI, export
```

Non-negotiable rules:

1. **One parser, one scorer.** Never parse a bank a second way and never decide
   correctness outside `runtime.py`. A future MCP/function-calling adapter must
   wrap the JSON commands, not reimplement them. Clarified 2026-08-15
   (IDEA-LEDGER IL-20260815-05): this names one scoring authority, not a frozen
   capability set. New scoring behavior extends `score_response` additively,
   and advisory graders, human or model, may propose a mark but never settle
   one. A feature is wrong only if it needs a second, parallel authority whose
   verdicts compete with the runtime's.
2. **The runtime owns assessment authority.** Correctness, session state,
   evidence recording, and disclosure of keyed assessment content belong to
   the runtime. An agent may build and teach the course, but it may not invent
   a score, bypass the active feedback mode, or reveal keyed content early.
3. **Never auto-grade prose.** A `short` item scores `None` (pending review),
   never `False`. Marking happens later against a rubric, by a human or a
   human-approved model. Clarified 2026-08-15 (IDEA-LEDGER IL-20260815-06):
   a labeled, provisional AI assessment of a short answer is an advisory
   grade and is allowed; only the settled mark waits for review.
4. **Never commit real question banks.** This repository holds code and
   synthetic fixtures only. `itembank guard .` enforces it in CI.
5. **Evidence and banks stay on disk.** No telemetry, no hosted gradebook.
   Clarified 2026-08-15 (IDEA-LEDGER IL-20260815-06): this bans telemetry and
   vendor-held data, not the learner's own copies. Learner-initiated export,
   backup, and device sync are legitimate features gated by the export and
   share rights grants; Phase 18 external installs need this distinction.

For course-building work:

6. **Do not rewrite by default.** Decide per objective whether direct source
   reading, an excerpt, lesson, notes/terms, example, visual, practice, or test
   is the best treatment.
7. **AI is allowed to do useful work.** It may search approved roots, align and
   draft, interpret evidence, propose a path, and perform approved bounded
   writes. It must cite sources, label synthesis, disclose uncertainty and
   denominators, and keep changes reviewable and recoverable.
8. **Match the real target.** Standardized-test courses require a sourced
   blueprint and faithful construct, difficulty, and item-format distribution;
   other knowledge courses follow their actual objectives and cognitive demand.
9. **Find before creating.** Search every user-approved root for existing
   lessons, questions, banks, exams, notes, and source bindings before drafting
   replacements. Roots may be separate and may include an Obsidian vault.
10. **Link deliberately.** Distinguish linking, importing, copying, moving,
    and superseding. Preserve stable identity, provenance, objective links, and
    citations. Never silently merge artifacts because their names look alike.
11. **Enhance progressively.** Authored lesson files must remain coherent and
    useful in plain Markdown readers. The itembank UI may add hover and focus
    definitions, interactive diagrams, demonstrations, adaptive disclosure,
    and other learning controls, but core meaning cannot depend on the richer
    display. Every interactive feature needs a useful static representation
    and an accessible interaction. Clarified 2026-08-15 (IDEA-LEDGER
    IL-20260815-06): the static bar is that the fallback conveys the core
    meaning and remains study-usable, not that it reproduces the interactive
    experience. An inherently interactive treatment is acceptable when its
    static form meets that bar.
12. **Audit before upgrading.** When improving an older lesson, question, or
    exam for new UI capabilities, inspect it first, preserve its identity and
    source history, propose a reviewable diff, and validate it afterward. Do
    not make cosmetic rewrites that add no learning value or silently change
    assessment meaning, keyed content, difficulty, or objective alignment.
13. **Preserve direction.** Keep user quotations separate from interpretations.
    Route every meaningful idea through the vision funnel and trace accepted
    work from vision to evidence, contract, requirement, phase, and verification.
14. **Preserve viable breadth.** Record proposals as core, registered,
    prototype, backburner, deferred, superseded, or rejected. Never silently
    drop an idea. Untimely is not rejected: an optional, expensive, or
    specialized capability stays in the permanent disposition ledger as
    registered, prototype, or backburner with its dependency, cost, and revisit
    trigger. The rejection and supersession ledger is append-only; a superseded
    or hard-rejected idea is never deleted, and every rejection records
    evidence, exact reason, conflicting rule, retained alternative, date, and
    reconsideration condition (synthesis sections 1 and 12). Clarified
    2026-08-15 (IDEA-LEDGER IL-20260815-06): append-only forbids deleting
    records, not organizing them. Completed-milestone ledgers may be archived
    or compacted into summaries that point to the full record, and disposition
    upkeep scales with the stakes of the idea, so the ledger has a maintenance
    path.
15. **Name authority and recovery.** Every operation names its durable object,
    owner, source of truth, rights, remote egress, accepted revision, stale and
    conflict behavior, validation, and recovery. Presentation is not
    authorization, learner notes are not assessment authority, and derived
    views are not canonical truth.

## Object and authority model (summary)

This condenses the Phase 16 synthesis
(`.planning/research/phase-16/14-synthesis.md` sections 2, 3, 6, and 10). The
binding contract is `.planning/SOURCE-TO-COURSE.md`; this summary orients an
agent, it does not replace that file.

- **Actors and authority (synthesis 2.1, 2.3).** The learner owns goals, private
  notes, scratch work, strategy choice, and evidence export. A course builder
  defines scope, treatments, and paths within source and rights limits. A
  reviewer accepts or rejects revisions. A source owner supplies rights and
  authoritative claims. A hosted or local agent discovers, aligns, drafts,
  validates, and explains within an operation manifest, and never owns accepted
  truth or assessment authority. The deterministic runtime is the sole authority
  for assessment session state, keyed disclosure, scoring, and attempt evidence.
- **Durable objects (synthesis 2.2).** Course, scope or framework version,
  concept, objective, source, source binding, artifact, lesson, bank or
  assessment form, activity, learner note, learner artifact, evidence event,
  strategy, agent operation, rights grant, and accepted revision. Each names a
  source of truth. Accepted files are canonical; search indexes, HTML, caches,
  thumbnails, rankings, and progress views are derived and disposable.
- **Separate state axes (synthesis 2.3, 4.1).** Accepted content, workflow state
  (`pending`), epistemic confidence (low), validation state (invalid), rights
  state, and availability are independent axes. Do not collapse them.
  `unavailable`, `unsupported`, `unknown`, `empty`, and `error` each need a
  different recovery action.
- **Core loops (synthesis 3).** The product's end-to-end acceptance surface is
  seven loops: discover/reconcile/bind, design a course, learn and construct
  notes, practice and test, evidence and remediation, author/review/accept, and
  maintain/recover/leave. Each is an acceptance surface, not a single screen.
- **One operation protocol for every client (synthesis 10).** Declare intent;
  declare approved roots, rights, egress, write, and execute authority;
  inventory before creating; plan treatment; checkpoint; draft the smallest
  missing artifact; cite and label synthesis; run deterministic validation; show
  an accessible plain and rich preview; present a bounded diff; pass configured
  review; accept atomically; update dependency and staleness state; report undo
  and uncertainty. Backend choice changes cost, latency, and privacy disclosure,
  never the artifact or authority contract.
- **Mutation is compare-and-swap (synthesis 6).** Every durable write states an
  expected base fingerprint, writes to a temporary file, validates, commits
  atomically, and appends to an operation journal, so any fault leaves the old
  or the new valid state and never a mixed one. Discovery is read-only. Link,
  import, copy, move, edit-in-place, supersede, migrate, and synchronize are
  distinct operations with distinct identity, approval, and recovery effects;
  they are not synonyms. A same-ID, divergent-bytes case is a conflict, never a
  silent overwrite.
- **Rights and egress are declared per operation (synthesis 6, 11).** Read,
  quote, transform, remote-process, package, export, and share are separate
  grants. Unknown rights stay unknown and restrictive. Hosted operations
  minimize and disclose exact egress; evidence and banks stay on disk.
- **Authored-output accessibility (synthesis 11.4).** Representative authored
  outputs pass keyboard, touch, screen-reader, zoom and reflow, high-contrast,
  and reduced-motion review with equivalent tasks. An agent never self-certifies
  accessibility. Clarified 2026-08-15 (IDEA-LEDGER IL-20260815-06):
  "representative" means sampled per template or capability profile, with full
  review when a template or interaction pattern changes; it does not mean human
  review of every generated artifact.
- **Clean recovery (synthesis 3 loop G, 6).** Export is not complete until a
  clean-machine, offline restore validates a manifest and reports every loss.
  Crash, cancel, disk-full, offline, permission-denied, future-schema, and
  agent-unavailable states preserve the last accepted state and expose the next
  safe action.

## Course artifact workflow

Use this sequence for higher-level course work, whether driven manually or by
Codex, Claude Code/Cowork, a local agent, or another compatible client:

1. Read `.planning/USER-VISION.md` and `.planning/SOURCE-TO-COURSE.md`.
2. Establish explicit read roots and write roots. Discovery is read-only by
   default, and finding a file does not authorize changing it.
3. Inventory existing sources and artifacts across all approved roots. Record
   stable identity, fingerprint, location, ownership, provenance, objective
   links, draft or accepted state, and validation status where available.
4. Reconcile likely duplicates, moved files, stale links, and conflicts. Ask
   for review when identity is uncertain; never infer identity from a filename
   alone.
5. Build or update the versioned objective graph and its outline projection,
   record the graph version, and keep structural order separate from
   prerequisite order. Then decide the best treatment for each objective, and
   reuse or link adequate artifacts before proposing new ones. A rename, split,
   merge, or changed-demand objective creates a reviewed migration proposal;
   historical evidence is never transferred automatically.
6. Create only missing artifacts through the relevant skill and deterministic
   contract. Keep generated synthesis and citations visible. Publish each
   accepted change as a recorded revision with its accepted fingerprint,
   reviewer, and validation result, then mark dependent derivatives stale.
7. Keep learner notes and learner artifacts as separate learner-owned records.
   A note, or a learner-built proof, program, diagram, or explanation, may
   ground reflection or a draft and produces descriptive or pending evidence
   until reviewed; it never silently becomes source truth, lesson truth, a key,
   a score, or mastery.
8. Render and verify lessons both as durable source documents and in the rich
   learning UI. Lint and statistically review question banks and exams.
9. For legacy enhancement, audit first, choose learning-value improvements,
   preserve fallbacks and assessment semantics, then present the bounded diff
   for approval.
10. Reindex disposable discovery data, validate links and artifacts, and report
    what changed, what remains uncertain, and how to undo accepted mutations.
    Every durable mutation goes through compare-and-swap with an expected
    fingerprint, atomic write, and operation journal.
11. Before promising an export or package, prove a clean-machine, offline
    restore that validates a manifest and reports every loss. Preserve the last
    accepted state on crash, cancel, disk-full, offline, permission-denied,
    future-schema, and agent-unavailable conditions.

## Prose style

Do not use em dash characters in repository-authored prose, documentation,
comments, fixtures, generated lessons, or questions. Use commas, parentheses,
colons, semicolons, or separate sentences instead. Verbatim source quotations
and the additive user statements in `.planning/USER-VISION.md` are the only
exceptions. Future linting should enforce this rule without rewriting quoted
source material.

## Reading the code (context discipline, a standing rule)

This repository is larger than the context window of most models that work in
it. Whole-file reads are the fastest way to end a session early. The five
largest modules cost roughly 41k tokens (`model.py`), 43k (`surfaces/daemon.py`),
44k (`tests/lesson_roundtrip.py`), 28k (`runtime.py`, `surfaces/lesson.py`), and
26k (`evidence.py`). Several open phase tasks touch four of those at once, so
reading each one whole is not affordable at any context size currently
available locally.

Work symbol-first instead:

1. **Locate before reading.** Search for the symbol (`grep -rn "_render_blocks"`
   or the editor's equivalent) and read a window around each hit, not the file.
   Sixty lines of the right function beats two thousand lines of the right file.
2. **Read whole files only when they are small,** under roughly 400 lines, or
   when the task is genuinely file-shaped, such as a rename across every
   definition in one module.
3. **Prefer the contract to the implementation.** `python itembank.py spec`,
   the schemas, and the roundtrip test names describe behavior in a fraction of
   the tokens the implementation costs.
4. **Let one test name the requirement.** When changing behavior, read the
   failing assertion and its immediate helper, not the whole roundtrip suite.
5. **Say what you did not read.** If a change touches a module you only sampled,
   note it in the summary so a reviewer knows where the blind spot is.

The point is not frugality for its own sake. Everything read early stays in the
window and competes with the reasoning that comes later, so an unnecessary file
read at turn 3 is paid for at turn 40 when the useful context has been
summarized away to make room for it.

## Quick start

```bash
python itembank.py spec                 # the whole format contract
python itembank.py lint bank.md         # validate; exits non-zero on error
python itembank.py build bank.md out.html   # offline quiz (holds the key, saves nothing)
python itembank.py serve bank.md        # graded sitting; every answer written to disk
python itembank.py stats bank.md        # item mix, objective coverage, position skew
python itembank.py study bank.md        # flashcards + Learn loop
python itembank.py day plan.md          # the day cockpit across subjects
```

## The authoring loop (writing a bank)

1. `python itembank.py spec` and follow the contract. Items are `Qn.` blocks
   with `[OBJECTIVE:]`, `[TYPE:]` (mc/multi/table/build/dnd/short/check/visual/fill),
   `CORRECT:`,
   `WHY BEST:`, `KEY DISCRIMINATOR:`, `DISTRACTOR ANALYSIS:`, `TRAP:`,
   `CONFIDENCE:`. A bank may carry one optional `## LESSON` section of teaching
   text above the first question, with `###` subheadings items link to via
   `[LESSON-REF: heading text]`.
2. `python itembank.py lint bank.md` - fix every `error`; warnings advise.
   Notable checks: every distractor must say when it WOULD be correct;
   answer-position skew is flagged; `CONFIDENCE: low` items must be reviewed.
3. `python itembank.py id-assign bank.md` - the only command that writes into a
   bank; mints opaque ids and content-hash fingerprints.
4. `python itembank.py stats bank.md` - check objective coverage and difficulty
   spread before shipping.

## The tutoring loop (administering a test as an AI tutor)

```bash
python itembank.py start bank.md --count 10 --mode practice --out s.json
python itembank.py next s.json        # returns the item WITHOUT its key
python itembank.py submit s.json --answer '"B"'
python itembank.py report s.json      # objective-level evidence
```

What the runtime guarantees you (an agent):

- `next` returns a `public_item` - stem, options, response schema - never the
  key, rationale, or model text.
- `submit` scores deterministically, records the attempt locally, and returns
  the next item.
- `short` responses are recorded but left `pending` for a marker; you must not
  pretend to have graded them.
- Repeated `submit` calls are idempotent (a `dedupe_key` guards replays).

Your side of the contract (see UI-SPEC.md §9 for the full list):

- You may ask **one diagnostic question** tied to the learner's actual wrong
  answer, and choose among permitted explanation forms (analogy, example,
  counterexample, visualization, derivation, simulation, Socratic question) -
  but only after the runtime has granted the tier for that content.
- You may **not**: reveal the key or higher-tier content, decide the hint tier,
  imply a score, select items, mark prose as accepted, or replace the activity
  with generic chat. Do not retry indefinitely.
- A learner's response may be `submit`-ted multiple times only as the runtime
  allows; you never change the test or the scoring.

## Commit discipline (standing rule)

**One atomic commit per plan.** When executing a GSD plan (or any phase
task), commit exactly once per plan, after that plan's own verification
passes, and only that plan's files. Do not batch two plans into one commit,
do not commit another plan's in-flight work, and do not leave a plan's work
uncommitted in a worktree - a nested worktree under the main checkout can be
removed by a concurrent process, and uncommitted work is then lost. If the
working tree carries another agent's uncommitted edits (this repo is
sometimes executed by concurrent chats), stage only your own plan's files by
name, never `git add -A`. Commit messages follow the repo's
`<type>(<plan>): <summary>` shape, e.g. `feat(10-01): ...` or
`test(10-02): ...`.

## Testing

Every test is stdlib-only and self-contained. There is no pytest dependency:

```bash
python tests/protocol_roundtrip.py     # lint codes, schemas, published contracts
python tests/agent_roundtrip.py        # full JSON session round trip
python tests/serve_roundtrip.py        # served sitting reaches disk, no key leak
python tests/scoring_roundtrip.py      # one scorer, offline key matches it
python tests/lesson_roundtrip.py       # LESSON grammar and reader
python tests/surface_roundtrip.py      # study and Anki export
# ...any tests/*_roundtrip.py - CI runs every tests/*.py (see .github/workflows/ci.yml)
```

CI (`.github/workflows/ci.yml`) additionally asserts `fixtures/sample_bank.md`
lints clean, `fixtures/broken_bank.md` is caught with each named error, the
sample builds, and every session payload validates against `schemas/*.json`
via `schema_validate.py`.

**Before you hand work back, run the gates locally.** `scripts/preflight.py`
mirrors ten of the twelve CI steps in one command, so a change is checked
before the push rather than after it:

```bash
python scripts/preflight.py --quick    # fast gates only (~15 seconds)
python scripts/preflight.py            # adds the Python and JS suites
python scripts/preflight.py --list     # which gate mirrors which CI step
```

Each gate names the CI step it stands in for. Two steps are deliberately not
mirrored and are listed with their reason in `CI_ONLY`; the pinned-LTI install
is setup rather than a gate, and the schema pipeline is a long shell sequence
that a Python copy would only be able to disagree with.
`tests/preflight_roundtrip.py` fails the build when CI gains a step that no
gate claims, so the mirror cannot drift silently.

## Skills

Repo playbooks live in two mirrored trees so every agent finds them:

| Skill | Purpose |
|---|---|
| `build-course` | Orchestrate sources → objectives → treatment → artifacts → evidence |
| `absorb-book` | Analyze a source and create only the treatments it actually needs |
| `curriculum-design` | Build objectives, prerequisites, source alignment, coverage, and assessment blueprint |
| `guiding-questions` | Run a Socratic tutoring session with the JSON protocol |
| `author-bank` | The write → lint → fix loop for new items |
| `ocr` | Read text out of images via a local Ollama vision model (optional; needs the model pulled) |

Where each tool finds the playbooks:

- **Codex, Gemini CLI, Cursor, GitHub Copilot, and other agents.md readers**:
  `.agents/skills/<name>/SKILL.md`, auto-discovered from the repo root.
- **Claude Code**: mirrored at `.claude/skills/<name>/SKILL.md` (project-level).
  Invoke with `/name` or let Claude auto-match the description.
- **Reasonix**: auto-discovers `.agents/skills/` as a convention root - no
  config needed. The optional OCR plugin wiring is personal config, shown
  in `reasonix.toml.example` (the file itself is gitignored).
- **Anything else**: point your tool's skill root at `.agents/skills/`.

The two trees are mirrors of the same playbooks - edit either and copy to
the other; CI runs `diff -rq .agents/skills .claude/skills` and fails on
drift.

## Recording operational findings (a rule for agents working here)

When a session learns something operational that cost it turns or probes - a
tool/permission-gate quirk, a launch recipe, an environment limitation, a
concurrency hazard - **persist it before the session ends** instead of letting
the next session rediscover it from scratch:

1. Save a memory (`remember`) with the concrete behavior and a "how to apply"
   rule.
2. Write the full details to `.reasonix/REASONIX.md` - machine-local and
   gitignored; the canonical home for this machine's runtime notes.
3. Keep machine-specific checkout paths and usernames out of committed docs -
   the CI path-leak step fails agent-facing files that contain them.

Recorded example (2026-08-11): in interactive sessions the command gate
declines `; echo $?` status suffixes, background bash jobs, inline interpreter
code (`python -c`, heredocs, loops), and ad-hoc runner scripts, while bare
commands and simple `&&`-chains run. Full notes: `.reasonix/REASONIX.md` §7.

## Where to look next

- `README.md` - full user documentation (item types, serve vs build, the day
  surface, design boundaries).
- `ROADMAP.md` - the public product contract and sequenced improvement plan.
- `.planning/` - the GSD planning workspace (PROJECT.md, REQUIREMENTS.md, the
  per-phase plans under `.planning/phases/`).
- `.claude/CLAUDE.md` - GSD project context for Claude Code.


<!-- BEGIN PORTABLE AGENT RULES v1 -->
## Working agreement (portable, synced)

*This block is generated. Canonical source: `weibao-planing/_templates/portable_agent_rules.md`. Edit it there and re-run `.claude/scripts/sync_agent_rules.py`, not here. Anything you write outside the BEGIN and END markers is yours and survives a re-sync.*

Applies to every AI agent reading this file, whichever tool loaded it.

### Commits

- Never add a `Co-Authored-By` trailer to a commit message. This overrides the Claude Code harness default, which instructs the opposite.
- Commit or push only when asked. Branch first if the current branch is the default one.

### Communication

- Lead with the answer. Put context after it, and only the context that changes what I do next.
- Do the work first. Then say what you did, whether it worked, and what is left.
- Say what was actually wrong before saying what you did about it.
- Separate what you verified from what you inferred. Never state a guess as a fact.
- Never report a file change, a command, or a commit you did not actually run.
- Correct an error in one sentence, then continue. No apology, no post-mortem.
- Answer every question I asked, each one by name.
- Five items maximum in any list I have to act on. Rank the rest and split it off.

### Prose

- No em dashes, and no ` -- ` standing in for one. Restructure the sentence.
- Banned phrases, no substitutes: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "let me be direct". Say the thing instead of announcing that you are about to.
- No flattery, no enthusiasm you did not feel, no decorative headings, no emoji.
- No hollow adjectives. Replace "robust" with the fact it stands for, or cut it.
- One instruction per sentence. No semicolons, no fragments.
- State each fact once. Do not repeat yourself.

### Reference points

When a reply carries three or more findings, decisions, options, risks, questions, or actions, give each one a short code and keep that code for the rest of the session: `F1` findings, `D1` decisions, `O1` options, `R1` risks, `Q1` questions, `A1` actions. Invent a letter for a category not listed here. No codes on short answers.

### Aliases

When one of these appears as a standalone word in a message, expand it and act as if the expansion had been typed. Inside a longer word or phrase it is not an alias.

- `scr` = simplify and compress your last response, then repeat it.
- `eli` = explain that like I am 18. Simpler words, shorter answer.
- `foc` = what is the real signal here? Cut to the one thing that matters.
- `ref` = rewrite your last response with reference points.

### Scope

- Deliver what was asked at the scope asked. Do not widen the work into cleanup, refactoring, or documentation nobody requested.
- Do not build abstractions for requirements that do not exist yet.
- Never claim something is done without evidence you ran it.
- Restate finished work in one or two sentences. Do not re-narrate every step.

<!-- END PORTABLE AGENT RULES v1 -->

```
