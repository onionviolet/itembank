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
