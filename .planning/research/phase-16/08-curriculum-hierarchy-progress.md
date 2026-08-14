# Curriculum hierarchy, pathways, and honest progress

**Stream:** 08 of the Phase 16 research program

**Status:** research complete, decisions remain proposals until Stream 11 synthesis

**Access date for external sources:** 2026-08-13
**Scope:** flexible curriculum structure and progress semantics for fields,
branches, programs, academic periods, courses, subcourses, units, concepts,
objectives, lessons, activities, and assessments.

## 1. Scope and research questions

This report asks four linked questions:

1. What representation can describe an open field, a regulated or standardized
   program, and a particular institutional course without forcing them into the
   same fixed tree?
2. How should prerequisites, alternate routes, electives, cross-listing,
   reusable lessons, multiple sources, institutions, and syllabus revisions be
   represented without duplicating identity or losing provenance?
3. Which progress claims are meaningful at each level, who defines the
   denominator, and how should optional or unknown scope appear?
4. When is a progress bar, including a displayed 100 percent, an honest account
   of a bounded task, and when does it falsely imply knowledge or finality?

The target is not a universal ontology of education. It is a portable,
authorable course map that can project several useful learner views while
preserving the distinction between curriculum structure, learning resources,
learner actions, assessment evidence, retention, and formal completion.

### 1.1 Terminology used in this report

| Term | Meaning here |
|---|---|
| Field | An open or evolving domain such as mathematics. It need not have a complete boundary. |
| Framework | A versioned, attributed set of concepts, competencies, standards, or objectives. |
| Program | A bounded route or family of routes toward a credential, exam, degree, or user goal. |
| Course offering | One institution's or user's course, tied to a syllabus version and dates when applicable. |
| Structural node | A container used for organization, such as program, semester, course, unit, or subcourse. |
| Concept | A reusable idea or subject entity. A concept is not automatically an assessable objective. |
| Objective | A versioned statement of what a learner should know or be able to do, with intended cognitive demand. |
| Artifact | A source, reading, lesson, activity, practice bank, or assessment that treats or measures objectives. |
| Path | A selected route through nodes and objectives, with required, choice, and prerequisite conditions. |
| Scope authority | The actor or document that defines what is in scope and what counts as required. |
| Evidence | Recorded observations about learner performance. Participation alone is not evidence of learning. |

## 2. Sources and evidence quality

### 2.1 Existing itembank contracts, research, and shipped behavior

| Source | What it establishes | Type and strength |
|---|---|---|
| [`SOURCE-TO-COURSE.md`](../../SOURCE-TO-COURSE.md) | The course is the user-facing unit, objectives are its spine, coverage must be cited, and sparse evidence must not become a mastery percentage. | Binding local product contract, high |
| [`PLANNING-DIRECTIVES.md`](../../PLANNING-DIRECTIVES.md) | Planning must preserve source authority, uncertainty, denominators, reversible changes, and the one-parser and one-scorer boundaries. | Binding local planning contract, high |
| [`ROADMAP.md`](../../ROADMAP.md) | Phase 14 owns the course workspace and source binding; Phase 15 owns the AI course director; Phase 16 specifies learning flow and capability contracts; Phase 17 implements the visual system. | Binding local sequencing contract, high |
| [`2026-08-09-extraction-subjects-bilingual.md`](../2026-08-09-extraction-subjects-bilingual.md) | Earlier research proposed framework/objective identifiers and citation-backed, computed coverage states. | Existing local research, medium to high |
| [`2026-08-09-landscape-widening.md`](../2026-08-09-landscape-widening.md) | Earlier research proposed prerequisite-fringe selection, hierarchical tags, and blueprint-weighted coverage. | Existing local research, medium |
| [`2026-08-10-lesson-item-coupling.md`](../2026-08-10-lesson-item-coupling.md) | Objectives belong to assessment items, lessons can treat several objectives, and the coverage map should remain computed rather than stored. | Existing local research and code audit, high |
| [`2026-08-10-tiered-verdicts.md`](../2026-08-10-tiered-verdicts.md) | Pending work must grant neither mastery credit nor a retention interval; evidence-poor objectives remain unknown. | Existing local research and implementation contract, high |
| [`model.py`](../../../model.py) | The parser accepts exact objective strings and `[PREREQ:]`; lint detects unknown prerequisites and cycles; `coverage_map()` computes objective to item links on demand. | Shipped source, high |
| [`evidence.py`](../../../evidence.py) | Evidence is append-only; objective history separates correct, wrong, and pending; lesson completion is a distinct event. | Shipped source, high |
| [`retention.py`](../../../retention.py) | Retention is derived from an immutable snapshot, has six labeled states, retains denominators, and leaves insufficient evidence `unknown`. | Shipped source, high |
| [`selection.py`](../../../selection.py) | Selection can filter on objectives and prerequisites, and uses retention state without re-deriving it. | Shipped source, high |

Direct checks on 2026-08-13 used `python3 itembank.py coverage
fixtures/sample_bank.md`, `python3 itembank.py stats
fixtures/sample_bank.md`, and `python3 tests/retention_roundtrip.py`. The sample
reported six items across five objectives, while the retention contract test
passed its snapshot, six-state, pending, retraction, trend, bounded-weight,
scheduler, and JSON/text-parity checks. These checks demonstrate current
behavior only. They do not demonstrate a course hierarchy or course completion
model.

### 2.2 External primary sources for standards and product behavior

All links in this table were accessed 2026-08-13.

| Source | Relevant observed behavior | Source type |
|---|---|---|
| [1EdTech CASE overview](https://www.1edtech.org/standards/case/about) and [CASE 1.1 portal](https://standards.1edtech.org/case/) | CASE represents frameworks, human and machine-readable competency items, parent-child and cross-framework associations, rubrics, and stable identifiers. | Primary standard and standards-body overview |
| [CASE real-world scenarios](https://www.1edtech.org/standards/case/real-world-scenarios) | CASE can relate updated standards to previous versions and align resources across jurisdictions. | Primary standards-body guidance |
| [Credential Engine Pathway Builder](https://credentialengine.org/pathwaybuilder/) and [Pathway Constraints task-group archive](https://credentialengine.org/taskgrouparchive/) | CTDL pathways may contain credentials, courses, competencies, work experience, and other components; constraint work covers and/or logic, sequencing, thresholds, and levels. | Primary schema steward and project documentation |
| [Open edX course building blocks](https://docs.openedx.org/en/latest/educators/references/course_content_development.html) | Open edX uses course, section, subsection, unit, and component containers, with sections often representing time and subsections often representing topics. | Primary product documentation |
| [Open edX Progress page](https://docs.openedx.org/en/latest/educators/references/data/progress_page.html) | Its course-completion chart counts completable units, including readings, videos, practice, graded work, and some future content; visibility settings change the denominator. | Primary product documentation |
| [Open edX completion tool](https://docs.openedx.org/en/latest/educators/references/course_development/exercise_tools/completion.html) | A learner can mark an ungraded activity complete, and the completion component itself produces a practice score. | Primary product documentation |
| [Canvas Mastery Paths guide](https://community.canvaslms.com/t5/Instructor-Guide/How-do-I-use-Mastery-Paths-in-course-modules/ta-p/906) | A scored source assignment selects conditional content; manual grading can hold later content; module prerequisites and requirements are encouraged but separate. | Primary product documentation |
| [Moodle activity completion](https://docs.moodle.org/38/en/Activity_completion) and [course completion design](https://docs.moodle.org/dev/Course_completion) | Completion criteria can be manual, viewed, submitted, grade-based, time-based, or aggregated by all, any, fraction, or count. | Primary product documentation, one archived and one developer design page |
| [Mathematics Subject Classification 2020](https://msc2020.org/) | MSC is a maintained research-literature taxonomy revised through community input, not a universal learning sequence or finite mastery map. | Primary classification authority |
| [AP Calculus AB course page](https://apcentral.collegeboard.org/courses/ap-calculus-ab), [Course Audit](https://apcentral.collegeboard.org/courses/ap-calculus-ab/course-audit), and [course changes](https://apcentral.collegeboard.org/courses/how-ap-develops-courses-and-exams/course-changes-overview) | The current framework has eight commonly taught units, exam-weight ranges, cross-cutting mathematical practices, flexible local sequencing, authorization requirements, and versioned clarifications. | Primary program and assessment authority |
| [MIT Mathematics catalog](https://catalog.mit.edu/subjects/18/) and [MIT general requirements](https://catalog.mit.edu/mit/undergraduate-education/general-institute-requirements/) | MIT has alternatives for Calculus I, credit exclusions, accelerated routes, and several ways to satisfy the institute requirement. | Primary institutional catalog |
| [MIT 18.01 syllabus](https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/pages/syllabus/) | One offering defines goals, prerequisite knowledge, problem sets, four exams, a final, and course-specific weights. | Primary institutional course artifact |
| [WAI-ARIA 1.2](https://www.w3.org/TR/wai-aria/) | A progressbar is a range widget; an unknown value may be represented as indeterminate, and human-readable value text can supplement numeric state. | Primary accessibility standard |

### 2.3 Learning and UX research

All links in this table were accessed 2026-08-13.

| Source | Finding used | Method and limitation |
|---|---|---|
| [Conrad et al., “The impact of progress indicators on task completion”](https://doi.org/10.1016/j.intcom.2010.03.001) | In two online-questionnaire experiments, apparently slow early progress increased abandonment and worsened experience; intermittent feedback reduced some cost. | Primary experiments about questionnaires, not learning or mastery. Transfer to course UX is an inference. |
| [Bloom, “Learning for Mastery”](https://eric.ed.gov/?id=ED053419) | Mastery requires an explicit definition and sufficient time, quality of instruction, understanding, and perseverance. | Foundational position and early evidence, not a modern product evaluation. |
| [Kulik, Kulik, and Bangert-Drowns, “Effectiveness of Mastery Learning Programs”](https://doi.org/10.3102/00346543060002265) | The meta-analysis evaluates mastery programs as instructional systems rather than a UI label. | Secondary synthesis of heterogeneous older studies; useful for the criterion-and-correction principle, not for choosing a universal threshold. |
| [van den Broek et al., “Points and progress-bars enhance motivation but not learning”](https://doi.org/10.1016/j.chb.2025.108862) | In adaptive retrieval practice, gamified feedback improved self-reported motivational measures but not learning behavior or delayed recall. | Primary recent study, narrow task and intervention; it argues against treating a progress display as evidence of learning. |

## 3. Observed facts, inference, recommendation, and open questions

### 3.1 Observed facts

1. CASE separates a framework document, individual competency items, and
   associations. Associations can link within or across independently owned
   frameworks. This is a stronger model than encoding every relationship in a
   slash-delimited label.
2. CTDL pathway work needs logical conditions beyond a linear list, including
   alternatives, sequencing, thresholds, and and/or combinations.
3. Real LMS products use different container vocabularies and completion
   rules. Even within one product, viewing, submitting, passing, manual
   acknowledgment, and elapsed time may all count as completion.
4. AP Calculus AB is bounded by an authoritative, versioned framework, but its
   eight units are one possible sequence and local courses may organize the
   content differently. Required course content, mathematical practices, local
   teaching sequence, and exam weighting are related but not identical.
5. MIT treats several subjects and prior achievements as alternate ways to
   satisfy Calculus I. The catalog also prevents duplicate credit among
   equivalents. A single parent-child tree cannot express these rules.
6. Mathematics as a research field has a useful maintained taxonomy, MSC2020,
   but the authority describes it as a literature-classification scheme. It
   does not claim to enumerate everything a person could learn or prescribe a
   prerequisite order.
7. itembank already distinguishes coverage from evidence and pending from
   settled performance. Retention is a derived, time-sensitive state rather
   than stored completion.
8. Progress indicators can affect motivation and abandonment, but research
   does not justify reading a filled bar as learning, mastery, or retention.

### 3.2 Inferences

1. A curriculum should be stored as a typed graph with authored projections,
   not as one canonical tree. The tree remains useful as a navigation view.
2. Structural containment and prerequisite dependency are different edge
   families. Mixing them makes reordering a unit appear to change what a
   learner must know first.
3. A concept, objective, lesson, and assessment require separate identities.
   They can have many-to-many relations and different version histories.
4. “Course completion” has no portable meaning unless the scope authority,
   rule, denominator, version, and effective date are visible.
5. A 100 percent indicator is honest only for a closed set and a named
   predicate. “12 of 12 required activities submitted” may be true while
   coverage is thin, evidence is pending, and retention is unknown.
6. An open field can support progress toward a selected route, collection, or
   goal, but not progress toward completion of the field itself.

### 3.3 Recommendations

1. Adopt a small typed graph kernel with stable IDs, versioned frameworks, and
   explicit scope views. Do not hard-code a universal sequence of hierarchy
   levels.
2. Keep a convenient default course outline projection, but let a course omit
   or rename levels and let nodes contain nodes of compatible kinds.
3. Store progress as a bundle of named dimensions. Never compute one global
   percentage by averaging participation, evidence, retention, and coverage.
4. Require every determinate percentage to expose its numerator, denominator,
   denominator authority, included version, and optional-item treatment.
5. Render open or unknown scope as indeterminate or as bounded subgoal progress,
   not as zero percent and not as 100 percent.
6. Preserve imported institutional and standards frameworks as attributed,
   versioned authorities. Put local adaptations in overlays rather than
   silently editing the imported record.

### 3.4 Open questions

1. Does Phase 14 need a general graph file in its first implementation, or can
   it begin with course, objective, artifact, and edge records while reserving
   extension points?
2. Which objective relationship vocabulary is sufficient for version one:
   `prerequisite`, `part-of`, `aligns-with`, `equivalent-to`, `broader-than`,
   and `supersedes`, or a smaller subset?
3. Should “mastered” remain the shipped retention state name when the report is
   scoped to recent settled evidence rather than durable mastery?
4. Who may certify required completion in a personal course: only the learner,
   an imported authority, or an approved agent proposal followed by human
   acceptance?
5. How should evidence transfer when an objective is superseded, split, merged,
   or materially changes cognitive demand?

## 4. Hierarchy options

### Option A: fixed universal tree

```text
field > branch > program > year > semester > course > subcourse > unit
      > concept > objective > lesson > activity > assessment
```

| Benefits | Weaknesses | Applicability |
|---|---|---|
| Simple breadcrumbs, folders, and recursive percentages. | Assumes every subject uses every level; forces cross-listed and reusable objects into duplicate parents; confuses concepts and objectives with containers; cannot express alternate paths well. | Reject as the data model. It may remain a documentation checklist. |

### Option B: recursive outline with user-defined labels

Every container has `kind`, `title`, `children`, and optional completion rules.
The user can omit levels and define local labels.

| Benefits | Weaknesses | Applicability |
|---|---|---|
| Authorable as nested Markdown or JSON; supports many subject structures; easy learner outline. | Still gives each child one canonical parent; cross-listing becomes duplication or aliases; prerequisites become awkward references; reuse and versioning remain bolted on. | Useful as an authored projection, insufficient as the canonical model. |

### Option C: pure typed graph

Every framework, node, concept, objective, artifact, and scope is an entity.
Typed edges express containment, dependency, alignment, equivalence, reuse,
choice, and supersession.

| Benefits | Weaknesses | Applicability |
|---|---|---|
| Handles alternate paths, cross-listing, reusable lessons, multiple institutions, and revisions without duplication. | Harder to author and review; unrestricted graphs can become inscrutable; cycle rules differ by edge type; a graph alone does not tell the learner what to do next. | Correct semantic core, but too raw as the only interface. |

### Option D: layered graph with explicit projections, recommended

Use a constrained typed graph as the durable model, plus named scope and path
views that project it into an outline, semester plan, exam blueprint, concept
map, or next-action route.

```text
Authorities and versions
  framework, institution, syllabus, blueprint, user goal
             |
             v
Structural graph                 Knowledge graph
  contains / offered-in            prerequisite / part-of
  required-choice / elective       aligns-with / equivalent-to
             \                    /
              objectives and concepts
                        |
                 treated-by / measured-by
                        |
             lessons, activities, assessments, sources

Named projection = root + included versions + path rules + completion policy
```

| Benefits | Weaknesses | Applicability |
|---|---|---|
| Preserves flexible identity while giving learners a comprehensible outline; makes denominators explicit; supports imported authorities and local overlays. | Requires validation, projection rules, and more deliberate authoring than a folder tree. | Accept as the target model and prototype with a bounded schema. |

### 4.1 Proposed minimal entity model

| Entity | Required fields | Important optional fields |
|---|---|---|
| `authority` | stable ID, name, owner type | institution, jurisdiction, URL |
| `framework_version` | stable family ID, version ID, title, authority, effective date, source locator | supersedes, status, locale, fingerprint |
| `node` | stable ID, kind, title, owning framework version | description, time period, local label |
| `concept` | stable ID, title, owning authority or local owner | definitions, broader/narrower alignments |
| `objective` | stable ID, statement, verb, cognitive demand, owning framework version | concept links, confidence, source locators |
| `artifact` | stable ID, kind, location, owner, fingerprint | version, source citations, portability state |
| `edge` | stable ID, type, source, target, authority, confidence | condition, rationale, source locator, effective dates |
| `scope` | stable ID, root or query, included framework versions, authority | required rules, optional policy, exclusions |
| `path` | stable ID, scope ID, path rules, owner | selected electives, substitutions, milestones |
| `completion_policy` | stable ID, applies-to ID, predicate, authority, version | threshold, expiration, human approval requirement |

An entity's `kind` is not its identity. A university may call something a
module that another calls a unit. The portable record keeps a broad semantic
kind and an optional local label. A subcourse is just a course-like node nested
inside another course in one projection, not a special fixed depth.

### 4.2 Edge families and validation

| Edge family | Examples | Validation rule |
|---|---|---|
| Structural | `contains`, `offered-in`, `part-of-program` | A named outline projection must be acyclic. The underlying graph may give one entity several parents. |
| Dependency | `prerequisite`, `corequisite`, `recommended-before` | Hard prerequisites must be acyclic within the selected path. Corequisites are symmetric groups, not cycles disguised as prerequisites. |
| Choice | `choose-any-1`, `choose-n-of`, `alternative-to`, `elective-in` | The choice group states cardinality and whether extra choices are enrichment or count toward completion. |
| Alignment | `aligns-with`, `broader-than`, `narrower-than`, `equivalent-to` | Alignment does not transfer completion or evidence automatically. Equivalence requires an authority and confidence. |
| Treatment | `taught-by`, `practiced-by`, `measured-by`, `sourced-by` | Many-to-many. Coverage is derived from valid links and citations, not presence alone. |
| Lifecycle | `supersedes`, `revises`, `split-from`, `merged-from` | Preserve old nodes and links. Never overwrite a historical framework version. |

## 5. Pathways, reuse, institutions, and versioning

### 5.1 Prerequisite graphs and alternate paths

A prerequisite is a claim about readiness, not a command to lock content.
Store who made the claim, its strength, and its evidence. Distinguish:

| Relation | Meaning | Default learner behavior |
|---|---|---|
| Required prerequisite | The selected authority says the dependent assumes it. | Recommend prerequisite first; permit an explicit recorded override unless an external credential rule forbids it. |
| Recommended-before | Sequence is helpful but not required. | Show as guidance, never a lock. |
| Corequisite | Learn together or within the same period. | Group in path planning. |
| Diagnostic substitution | Demonstrated evidence may replace the learning treatment. | Skip or shorten treatment, retain objective and evidence trail. |
| Credit substitution | An authority accepts another course, exam, or experience. | Satisfy required completion only under that authority's policy. |

Alternate paths should be expressed as choice groups and conditional
substitutions, not by cloning an entire course. A path can select one branch
while the course map still exposes alternatives and why the current route was
chosen.

### 5.2 Electives and optional enrichment

Use three states, not a single `optional` boolean:

1. `required`: included in the required-completion denominator.
2. `required-choice`: part of a choice group, where the group's cardinality
   defines the denominator.
3. `enrichment`: never required for completion and never makes required
   progress fall when new enrichment is added.

An elective may become required after the learner selects it. Record that as a
versioned path decision. Do not rewrite the source program's classification.

### 5.3 Cross-listed concepts and reusable lessons

Cross-listing is multiple alignment, not duplication. One concept or objective
may be included in several course projections. Evidence remains linked to its
stable objective identity and context. A local course can align its objective
to an external one without asserting equivalence.

A lesson is reusable when its meaning, citations, accessibility fallback, and
objective treatment remain valid in the new context. Reuse should create a new
course binding, not a copy. Course-specific introductions, examples, or
assignments can be overlays. If an overlay changes the lesson's substantive
meaning or objective demand, create a new artifact version.

### 5.4 Multiple sources and institutions

Keep these distinct:

| Layer | Example | Ownership |
|---|---|---|
| External framework | AP Calculus AB 2026-27 clarifications | College Board |
| Institutional program | MIT undergraduate GIR mathematics requirement | MIT |
| Course catalog record | MIT 18.01 | MIT |
| Course offering and syllabus | A particular term or OCW release | Instructor or institution |
| User course | A learner's “Calculus for engineering refresh” | Learner |
| Artifact binding | A chosen book section, MIT lecture, local lesson, and practice bank | Respective owners plus local binding author |

One user course may draw from all five upstream layers. Provenance must answer
which source supports a claim, which authority requires an objective, and who
selected the current treatment. “Imported from MIT” must not imply MIT
endorses the assembled user course.

### 5.5 Versioned syllabi

Use immutable versions and explicit overlays:

```text
framework family: ap-calculus-ab
  version: 2025-26 CED + applicable corrections
  version: 2026-27 CED + fall-2026 clarifications

local syllabus family: district-course-42
  version: fall-2026, aligned-to ap-calculus-ab@2026-27
  overlay: local order, dates, sources, assignments
```

When a new version arrives, compute a reviewable diff with at least:

- added, removed, edited, split, merged, and reordered objectives;
- changed cognitive demand, exam weight, required status, or exclusions;
- affected lessons, activities, assessments, paths, and progress denominators;
- evidence whose interpretation may no longer transfer;
- unresolved alignments and confidence.

Historical learner claims stay attached to the version under which they were
earned. Migration is a new alignment decision, never a silent relabel.

## 6. Progress semantics

### 6.1 The seven dimensions

| Dimension | Question answered | Example numerator / denominator | Can reach 100%? |
|---|---|---|---|
| Coverage | Does the accepted course design provide adequate treatment or measurement for the scoped objectives? | required objectives with accepted, cited treatment / required objectives in scope | Yes, for a closed, versioned scope and stated adequacy rule. It says nothing about a learner. |
| Participation | What did the learner open, acknowledge, attempt, submit, or complete procedurally? | required activities submitted / required activities assigned | Yes, for a closed activity set. It does not mean correct, understood, or retained. |
| Evidence | What settled observations support performance on each objective? | objectives meeting a named evidence rule / objectives for which that rule is required | Yes only for a stated rule and window. Pending and missing evidence remain visible. |
| Retention | What does replayed, time-sensitive evidence suggest is due, stable, weak, at-risk, or unknown? | usually a state distribution, not a percentage | Avoid 100%. Retention changes with time and evidence. Show state, next review, denominator, and snapshot. |
| Required completion | Has the authority's explicit completion predicate been met? | satisfied required rules / applicable required rules | Yes, including a truthful 100%, if the predicate, version, substitutions, and authority are visible. It is a credential or workflow claim, not global mastery. |
| Optional enrichment | How much of the learner-selected or available enrichment has been explored? | selected enrichment completed / selected enrichment | A selected bounded set may reach 100%. The full enrichment catalog should not reduce required completion or imply exhaustion of the subject. |
| Uncertainty | Which scope, links, evidence, marks, versions, or authority decisions remain unresolved? | unresolved counts by type, with affected denominator | No. Show counts, labels, and confidence rather than converting uncertainty to a flattering percentage. |

### 6.2 Progress claim contract

Every displayed determinate progress claim should be reconstructible from:

```text
metric name
scope id and scope version
predicate or state rule version
numerator
denominator
included and excluded categories
optional-item policy
pending-item policy
authority
evidence snapshot or computation time
```

Recommended human-readable examples:

- “Required activities: 9 of 12 submitted for MIT 18.01 Fall 2006 outline.”
- “Assessment evidence: 5 of 12 objectives meet the accepted three-day rule;
  2 are pending review; 5 have insufficient evidence.”
- “Course design coverage: 11 of 12 required objectives have accepted cited
  treatments; 1 is thin.”
- “AP Calculus AB required-content plan: complete for the 2026-27 framework.
  This is plan completion, not exam readiness.”
- “Mathematics exploration: 14 concepts visited in your selected calculus
  route. Mathematics has no finite completion denominator.”

### 6.3 Honest and dishonest progress bars

#### Honest uses

A determinate bar is honest when all of the following are true:

1. The task or scope is closed and versioned.
2. The predicate is observable and does not stand in for a stronger claim.
3. The denominator is stable for the duration shown, or changes are disclosed.
4. Required, selected elective, and enrichment sets are distinguished.
5. Pending and unknown states are not counted as failures or passes.
6. The label names the metric, such as “required activities submitted,” not
   the vague word “progress.”
7. Text states the numerator and denominator. Color and bar length are
   redundant, not exclusive.

Examples: file import, source review queue, a lesson's five required steps, 12
assigned activities, three required assessments, or a versioned program's
accepted completion criteria.

#### Dishonest uses

A bar is misleading when it represents:

- completion of an open-ended field;
- “mastery” derived from pages viewed or activities clicked;
- readiness inferred from curriculum coverage;
- retention with no time window or evidence snapshot;
- an evolving syllabus without identifying its version;
- a denominator that silently expands when enrichment is added;
- an average of unlike quantities, such as 80% participation, 50% evidence,
  and 100% source coverage;
- missing or pending work as zero performance;
- a probability or model confidence as if it were percent of course completed.

#### UI recommendation

Use a determinate bar only for a bounded operational or completion predicate.
Use labeled state distributions, counts, and next actions for evidence and
retention. Use an indeterminate indicator only for work whose end is unknown,
such as source discovery or graph reconciliation, and never leave it as an
unexplained spinner. WAI-ARIA permits an indeterminate progressbar when the
value is unknown. Provide a named region, accessible text, `aria-valuenow` for
determinate ranges, and `aria-valuetext` when the numerical value alone is not
meaningful.

The questionnaire and retrieval-practice studies suggest that progress visuals
can alter motivation or abandonment without improving learning. Therefore the
display should orient and inform, not reward clicking or imply knowledge.

## 7. Three test cases

### 7.1 Mathematics as an open-ended field

#### Complex example

```text
Field: Mathematics                           scope: open, no completion rule
  Branch views:
    Algebra
    Analysis
    Geometry and topology
    Probability and statistics
    Discrete mathematics
    Applied mathematics

User goal: “prepare for differential equations used in engineering”
  selected route:
    algebraic manipulation
       -> functions and graphs
       -> trigonometry
       -> limits
       -> differentiation
       -> integration
       -> first-order differential equations

  alternate readiness routes:
    AP Calculus AB evidence
       OR MIT 18.01 completion
       OR diagnostic substitutions by objective

  cross-listed concepts:
    vector spaces -> linear algebra, differential equations, numerical methods
    conditional probability -> probability, statistics, machine learning

  enrichment:
    epsilon-delta limits
    numerical ODE solvers
    proof-based analysis
```

#### Results

| Dimension | Honest representation |
|---|---|
| Field coverage | “Open scope. MSC2020 is one research-literature classification reference, not a learning completion boundary.” |
| Route coverage | Percentage allowed if the user freezes a versioned route and adequacy rule. |
| Participation | Counts within chosen activities only. |
| Evidence | Per-objective states and denominator for the chosen route. |
| Retention | Due, stable, weak, at-risk, and unknown by snapshot. |
| Required completion | Only for the user-defined engineering-ODE goal, never for mathematics. |
| Enrichment | Separate selected list; adding a new topic does not revoke route completion. |

**Failure exposed:** a recursive percentage over the mathematics tree implies a
false total, makes classification changes reduce “knowledge,” and treats
overlapping branches as duplicates.

### 7.2 AP Calculus AB as a standardized program

#### Complex example

```text
Authority: College Board
Framework: AP Calculus AB, applicable 2026-27 version and clarifications
Required content: eight units, detailed topics/objectives/knowledge statements
Cross-cutting practices: processes, representations, justification,
  communication and notation
Exam blueprint: unit weight ranges plus current exam format

Local authorized course:
  institution: Example High School
  syllabus version: 2026-27
  sequence: locally chosen
  sources: college-level textbook + local lessons + approved external readings
  objective alignments: local objectives -> College Board objective IDs
  enrichment: epsilon-delta definition, explicitly outside assessed scope
```

#### Results

| Dimension | Honest representation |
|---|---|
| Program coverage | Required objectives and practices with accepted cited treatments, under the named CED version. |
| Blueprint coverage | Planned and delivered assessment distribution compared with official weight ranges and formats. |
| Participation | Local assignments and sittings, not AP program completion. |
| Evidence | Performance by objective, practice, representation, and relevant exam conditions. |
| Required completion | The local school's completion rule, distinct from AP Course Audit authorization and distinct from an AP Exam score. |
| Retention | Current objective states, never an unqualified “87% ready.” |
| Enrichment | Outside-exam content labeled and excluded from required AP denominator. |

A plan may truthfully reach 100 percent required-content coverage. A learner
may truthfully complete 100 percent of required local activities. Neither claim
means a guaranteed exam score. Readiness should be a multidimensional report
against the current blueprint, with evidence counts, transfer tasks, timing,
calculator conditions, pending marks, and uncertainty.

**Failure exposed:** treating the eight unit weights as a linear learning path
misses cross-cutting practices and College Board's explicit sequencing
flexibility. Treating a local course as identical to the program loses the
institution's sources, assignments, dates, and completion authority.

### 7.3 MIT 18.01 as one university course

#### Complex example

```text
Institutional requirement: Calculus I GIR
  alternatives:
    18.01 OR 18.01A OR 18.01L OR approved credit/standing route

Course catalog identity: 18.01 Calculus
  exclusions: equivalent listed subjects cannot also receive credit
  offering: Fall 2006 OCW syllabus
    prerequisites: high-school algebra and trigonometry
    goals: twelve stated capabilities
    activities: eight problem sets
    assessments: four in-class exams + final
    weighting: 250 + 400 + 250 points

Reusable content:
  derivative concept lesson shared with AP Calculus AB binding
  MIT-specific examples and assessments as overlays or distinct artifacts
```

#### Results

| Dimension | Honest representation |
|---|---|
| Requirement completion | MIT's rule determines whether Calculus I is satisfied, including accepted alternate routes. |
| Course participation | Problem sets and exams attempted within this offering. |
| Course grade | Institutionally weighted evidence. It is not automatically itembank's retention state. |
| Objective evidence | Settled item and assessment evidence mapped to the twelve course capabilities. |
| Coverage | Whether each capability has cited treatment and appropriate assessment demand. |
| Retention | Current replayed state after the course, which can decay even though institutional credit remains complete. |

The institutional requirement may remain 100 percent satisfied permanently
after credit is granted, while current retention on integration techniques is
at-risk. This is not a contradiction. They are different claims with different
authorities and time semantics.

**Failure exposed:** putting the MIT requirement, catalog course, one offering,
and a user's reusable calculus lesson in one tree causes either duplication or
loss of authority. It also cannot cleanly model accelerated and transfer-credit
routes.

## 8. Pattern inventory

| Pattern | Benefits | Weaknesses and risks | Applicability to itembank |
|---|---|---|---|
| Framework plus stable item IDs and associations | Interoperable identity, cross-framework alignment, preserved authority. | External alignments can be wrong or overconfident; full CASE implementation is substantial. | Adopt the conceptual separation and import/export seam; defer full CASE conformance. |
| Fixed LMS outline | Easy authoring and navigation. | Confuses time, topic, and pedagogy; poor reuse and cross-listing. | Use only as a projection. |
| Constraint-based pathway | Represents alternatives, electives, substitutions, and thresholds. | Rule authoring and explanation can become complex. | Prototype a small and/or plus cardinality vocabulary. |
| Objective prerequisite DAG | Supports readiness and alternate sequences. | Prerequisite claims are contextual and disputable; hard gates can punish imperfect models. | Accept with authority, confidence, rationale, and learner override. |
| Many-to-many artifact binding | Reuses lessons and sources, supports multi-source courses. | Drift and context mismatch require validation. | Accept with fingerprints, versions, treatment roles, and course overlays. |
| Versioned immutable framework with local overlay | Preserves provenance and makes syllabus changes auditable. | Migration UI and evidence interpretation are nontrivial. | Accept as a foundation requirement. |
| One aggregate completion bar | Familiar and compact. | Hides denominator, uncertainty, optionality, and semantic differences. | Reject. |
| Dimension-specific counts and states | Truthful and actionable. | More information than a single score; requires careful hierarchy. | Accept, with progressive disclosure and a clear next action. |
| Indeterminate open scope | Avoids invented boundaries. | Some learners may experience it as less motivating. | Accept for fields and unresolved discovery; offer bounded user goals. |

## 9. Prototype proposals

### Prototype 1: graph-to-outline tracer

Build one synthetic file containing:

- the three test cases in Section 7;
- two framework versions;
- one cross-listed concept;
- one reusable lesson bound to AP and MIT objectives;
- one hard prerequisite, one recommended-before edge, one corequisite group;
- one choose-one alternative and one diagnostic substitution;
- one unresolved alignment and one superseded objective.

Render four projections from the same records:

1. learner course outline;
2. prerequisite map;
3. source and treatment coverage table;
4. version migration diff.

**Pass gate:** no entity is duplicated to appear in two projections; every
edge exposes authority and confidence; each projection has stable deep links;
the plain-text form remains reviewable.

### Prototype 2: honest-progress component matrix

Using the same synthetic course, render:

- required activities `9 / 12`;
- design coverage `11 covered, 1 thin`;
- evidence `5 supported, 2 pending, 5 unknown`;
- retention state distribution at a named snapshot;
- required completion predicate and unmet conditions;
- selected enrichment `2 / 3`;
- open mathematics field with no percentage.

Test desktop, narrow screen, keyboard, zoom, high contrast, reduced motion, and
screen-reader output. Include a control that opens the exact denominator and
rule. Do not use celebratory motion.

**Pass gate:** in usability checks, a participant can correctly answer “what
is complete?”, “who decided?”, “what remains?”, and “does this mean I know
it?” for every display.

### Prototype 3: denominator-change and version-migration simulation

Start with a versioned 12-objective course. Then:

1. add two enrichment objectives;
2. select one elective from a choose-one group;
3. receive a new authoritative syllabus version that edits one objective and
   splits another;
4. leave one constructed response pending;
5. advance the retention snapshot by 30 days.

**Pass gate:** required completion does not fall when enrichment is added;
selected-path denominators change with an explicit event; historical progress
stays reproducible; migrated evidence is not silently credited; pending stays
pending; retention can change without altering formal completion.

## 10. Failure modes and mitigations

| Failure mode | Consequence | Mitigation or verification |
|---|---|---|
| Universal fixed depth | Empty fake levels, duplicated cross-listing, awkward nonacademic subjects. | Typed nodes plus user-defined projection; fixtures that omit semester, unit, or concept levels. |
| Tree used as prerequisite graph | Reordering content changes alleged knowledge dependencies. | Separate structural and dependency edges; distinct cycle checks. |
| Slash-delimited objective name treated as identity | Renames break evidence; identical labels collide across authorities. | Stable opaque objective ID plus display path, authority, and framework version. |
| Alignment treated as equivalence | Evidence or credit transfers without justification. | Typed alignment, confidence, authority, and explicit transfer policy. |
| Lesson copied into every course | Drift, conflicting fixes, lost provenance. | Stable reusable artifact plus bindings and local overlays. |
| Imported framework edited locally | The local map falsely appears authoritative. | Immutable imported version and a visibly local overlay. |
| New syllabus overwrites old | Historical evidence becomes uninterpretable. | Immutable versions, diff, migration proposal, preserved old scope. |
| “Covered” means a tag exists | Weak or irrelevant material appears adequate. | Citation, treatment role, cognitive-demand match, validation state, and thin/conflicting/unknown states. |
| Viewed means learned | Click-through becomes mastery. | Keep participation separate from settled evidence and retention. |
| Pending means wrong or pass | Misstates learner performance and biases selection. | Preserve pending count, exclude from settled ratios, require approved mark. |
| Sparse evidence becomes percentage mastery | False precision and harmful path decisions. | Show unknown, counts, dates, context, and evidence rule. |
| Completion and retention share one state | Credit disappears as memory decays, or stale credit implies present knowledge. | Permanent authority completion record plus independently replayed retention state. |
| Optional catalog expands denominator | Learners lose progress when content is added. | Separate required, selected-choice, and enrichment denominators. |
| Field receives 100% | Claims an indefensible boundary and discourages exploration. | No field percentage; let users freeze bounded goals or routes. |
| Progress animation rewards clicking | Participation optimization replaces learning. | Calm text-first state, no points or celebration, evidence-aware next action. |
| Graph becomes unreadable | Authoring and accessibility collapse. | Outline as default; graph is a secondary view with filters, list fallback, and keyboard navigation. |
| Private learner data leaks through shared framework | Portable curriculum export accidentally includes evidence. | Separate curriculum package from local evidence store; explicit export preview and default exclusion. |

## 11. Accessibility, portability, privacy, provenance, and authorability

### 11.1 Accessibility

- The outline is the primary navigation representation. A node-link graph must
  have an equivalent ordered list or table, searchable nodes, explicit edge
  text, and keyboard-safe focus behavior.
- Never rely on color, line thickness, or bar fill alone. State labels, counts,
  numerator, denominator, and uncertainty remain text.
- Avoid placing every map cell in a complex interactive grid unless the
  keyboard model is implemented and tested. A semantic list often serves the
  learner better.
- A determinate progressbar needs an accessible name and current value. Use
  human-readable value text when a number alone is ambiguous. Unknown field
  scope should not receive a fake numeric value.
- Collapsed optional branches must remain discoverable and announce why they
  are optional, unavailable, or not selected.

### 11.2 Portability

- Durable files should preserve stable IDs, typed edges, authorities, source
  locators, versions, and projections without depending on app-only layout.
- Plain Markdown can carry a readable outline and tables, while a sidecar or
  fenced structured block may carry graph records if Phase 16 proves Markdown
  alone too ambiguous. That format decision remains open.
- CASE is a strong alignment and exchange reference, but it does not by itself
  represent the complete itembank course, learner path, artifact lifecycle, or
  evidence model. Export or mapping is preferable to adopting it as the sole
  internal schema.
- Curriculum export excludes learner evidence by default. An evidence export
  is a separate, explicit operation.

### 11.3 Privacy

- Hierarchy, framework, and public-source records may be shareable. Selected
  paths, accommodations, diagnostic substitutions, attempts, confidence, and
  retention are learner data and remain local.
- Do not publish a learner's alternate path or weak objective merely because
  the underlying framework is public.
- Computed progress views should derive from one immutable evidence snapshot,
  matching the shipped retention boundary, so a report does not combine
  different moments or silently upload events.

### 11.4 Provenance

- Each objective and prerequisite claim identifies its authority, framework
  version, and source locator.
- Each local adaptation identifies its author and relationship to the imported
  source.
- Generated alignments remain proposals with confidence until accepted.
- Cross-institutional equivalence is never inferred from similar names alone.
- A progress claim preserves the scope version and rule that produced it.

### 11.5 Authorability

- Authors should be able to begin with a normal outline, then add cross-links
  and conditions only where needed.
- The default vocabulary should be small. Advanced edge types appear through
  progressive disclosure.
- Validation should name unknown targets, illegal dependency cycles, invalid
  choice cardinality, orphan nodes, duplicate IDs, contradictory requirements,
  stale source versions, and progress rules with no stable denominator.
- Agent skills must find and align existing objectives and artifacts before
  generating replacements. They must propose graph edits as reviewable diffs.
- User-defined labels should not require schema changes. “Week,” “module,”
  “block,” and “chapter” can all render from a structural node with a local
  label.

## 12. Implications for learner flow, content contracts, agents, and upgrades

### 12.1 Learner flow

1. Enter through a bounded course or goal, not through the complete field map.
2. See a short outline, current path, next action, and reasons.
3. Expand alternatives, prerequisites, evidence, sources, and denominator only
   when needed.
4. Permit explicit path changes and overrides, with effects previewed.
5. After an activity, update participation immediately, evidence only when a
   valid observation exists, and retention only through a new snapshot.
6. Keep formal completion visible after it is earned while showing current
   review needs separately.

### 12.2 Semantic content contract

The Phase 16 contract should support:

- stable objective and concept references independent of display paths;
- one lesson treating many objectives and one objective treated by many
  artifacts;
- course bindings that identify purpose, such as direct reading, lesson,
  practice, transfer, or assessment;
- required, required-choice, and enrichment status;
- accessible static representation of path and prerequisites;
- explicit source and framework versions;
- no progress state embedded in authored lesson content.

### 12.3 Agent skills

The course-building and curriculum-design skills should require agents to:

1. identify scope authority and framework version before claiming completeness;
2. inventory existing nodes, objectives, lessons, and assessments across
   approved roots;
3. distinguish structural nesting from prerequisites and alignment;
4. label generated prerequisite or equivalence claims with confidence and
   citations;
5. preserve alternate paths and electives rather than flattening them;
6. calculate no aggregate progress without an explicit rule and denominator;
7. present migration and path changes as diffs with downstream effects;
8. never migrate learner evidence across changed objectives automatically.

### 12.4 Legacy upgrades

Legacy banks have objective strings and local prerequisite edges but no
course-level stable objective records. Upgrade should therefore be staged:

1. inventory objective strings, namespace patterns, sources, lesson refs, and
   prerequisite edges without editing files;
2. propose stable objective records and display paths;
3. flag collisions, unnamespaced objectives, cross-bank duplicates, and
   uncertain equivalence;
4. preserve existing strings as aliases during migration;
5. bind banks and lessons to a versioned course scope;
6. recompute coverage and validate prerequisite graphs;
7. leave old evidence attached to old IDs unless an explicit, reviewed mapping
   demonstrates continuity.

## 13. Decision table

| Status | Proposal | Rationale and gate |
|---|---|---|
| Accept | Typed graph kernel with named outline and path projections. | It is the smallest model that survives all three test cases. Synthesis should confirm ownership in Phase 14. |
| Accept | Separate structural, dependency, choice, alignment, treatment, and lifecycle edges. | Prevents hierarchy order from becoming false prerequisite logic. |
| Accept | Stable concept, objective, artifact, framework-family, and framework-version identities. | Required for reuse, cross-listing, evidence continuity, and migration. |
| Accept | Imported authorities plus local overlays. | Preserves institutional and standards provenance without blocking user customization. |
| Accept | Required, required-choice, and enrichment status. | Prevents optional content from corrupting completion denominators. |
| Accept | Seven separate progress dimensions with explicit denominators. | Directly follows the binding uncertainty and evidence rules. |
| Accept | 100% only for a closed, versioned scope and named predicate. | A precise completion claim is useful when it does not imply learning. |
| Accept | Open fields show no completion percentage. | Mathematics has no defensible universal endpoint. |
| Accept | Formal completion and current retention remain independent. | Institutional credit and memory have different authorities and time semantics. |
| Reject | Fixed universal hierarchy as canonical storage. | Fails cross-listing, alternate paths, subcourses, and different subject structures. |
| Reject | One aggregate course progress or mastery bar. | Combines unlike semantics and hides uncertainty. |
| Reject | Page views, lesson completion, or course coverage as mastery. | Participation and design quality are not learner evidence. |
| Reject | Automatic evidence transfer across equivalent, split, merged, or superseded objectives. | Similarity and alignment do not prove unchanged assessment meaning. |
| Reject | Copying reusable lessons into each course by default. | Causes drift and loses stable provenance. |
| Defer | Full CASE 1.1 conformance and service implementation. | Use its model as an interoperability reference; implement only when a real exchange consumer exists. |
| Defer | Credential-level CTDL export. | The path-condition model is useful now, but full credential publishing exceeds Phase 16. |
| Defer | Cross-institutional credit equivalence automation. | Requires authoritative policies and high-stakes review. |
| Prototype | Graph-to-outline tracer. | Must prove authorability and projection stability before schema commitment. |
| Prototype | Honest-progress component matrix. | Must prove learners distinguish completion, evidence, coverage, and retention. |
| Prototype | Syllabus migration and denominator-change simulation. | Tests versioning and the most dangerous silent-state failures. |
| Open | Minimal edge vocabulary for Phase 14. | Decide from prototype coverage and validation cost. |
| Open | Durable Markdown versus Markdown plus structured sidecar. | Test plain-reader coherence, diff quality, and agent authoring error rate. |
| Open | Naming of shipped `mastered` retention state. | Consider “currently supported” or retain the term with an explicit evidence rule and window. |
| Open | Authority for personal-course completion rules. | Needs user choice and a trust model for agent proposals. |

## 14. Concrete recommendations and risks

### Recommendations for Phase 16 synthesis

1. Specify course maps as typed entities and edges with one recommended outline
   projection, not as a fixed hierarchy.
2. Make `scope` and `completion_policy` first-class, versioned records. Every
   determinate progress display depends on them.
3. Establish a progress vocabulary that surfaces coverage, participation,
   evidence, retention, required completion, enrichment, and uncertainty
   independently.
4. Reserve numeric bars for bounded operational and completion claims. Use
   counts, state distributions, and next actions for learning evidence and
   retention.
5. Require framework and syllabus versions, authority, source locator,
   confidence, and migration behavior in the semantic contract.
6. Preserve course-specific paths as overlays over reusable concepts,
   objectives, and artifacts.
7. Carry the three prototypes into Phase 16 acceptance gates before Phase 17
   commits to map and progress visuals.

### Principal risks

| Risk | Severity | Response |
|---|---|---|
| The graph model grows into an ontology project. | High | Constrain version one to relationships required by the three tracers; defer general semantic-web ambitions. |
| Flexible scope makes the UI too abstract. | High | Default to a familiar outline and one next action; put graph detail behind deliberate expansion. |
| “Mastered” overstates limited evidence. | High | Always show rule, window, settled count, pending count, and snapshot; revisit the label. |
| Imported versions drift faster than local bindings are reviewed. | High | Detect updates, freeze current scope, and offer a diff rather than silent migration. |
| Authors create unjustified prerequisite edges. | Medium | Require rationale, source or author, confidence, and override; audit hard prerequisites. |
| Reuse spreads a flawed lesson across courses. | Medium | Fingerprints, affected-binding preview, versioned updates, and course-level acceptance. |
| Separate dimensions overwhelm learners. | Medium | Show the one context-relevant state first, with plain-language disclosure of the rest. |
| A calm interface becomes uninformative. | Medium | Provide exact counts, reasons, next actions, and changes since last visit without points or celebratory pressure. |

## 15. Bottom line

itembank should not ask one hierarchy or one percentage to carry every meaning.
The durable model should be a constrained typed graph whose normal learner view
is a simple, authored outline. Frameworks, courses, concepts, objectives,
artifacts, paths, and syllabus versions keep separate identities and explicit
authorities. Cross-listing and reuse are links, not copies. Alternate paths and
electives are conditions, not duplicated courses.

Progress must name its claim. A field such as mathematics has no honest 100
percent boundary. A versioned AP content plan, a particular university course,
or a learner-selected route may have a closed completion predicate, and 100
percent can be truthful for that predicate. It still does not mean universal
knowledge, exam certainty, or durable retention. Coverage, participation,
settled evidence, retention, required completion, optional enrichment, and
uncertainty remain separately visible so the system can be encouraging without
becoming misleading.
