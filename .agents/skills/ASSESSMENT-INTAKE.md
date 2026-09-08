# Assessment and grading intake

Read this reference when a course has an exam, certification, placement test,
graded assignment, competency check, or completion threshold. The intake is a
versioned planning artifact, not a score or a new runtime authority. It must be
complete enough that another reviewer can distinguish what is tested, how it
is tested, and how results are settled.

## Source authority and conflicts

Record each claim with a stable locator, publication or effective date, and
authority class:

1. Governing authority or current official exam blueprint.
2. Current syllabus, grading policy, rubric, or instructor clarification.
3. Official sample items, practice forms, and candidate guidance.
4. Publisher or preparation material.
5. Agent inference, labeled as synthesis.

Higher rank does not silently erase a conflict. Record the conflicting claims,
which source governs this course, who made that decision, and what remains
unknown. Do not infer tested weight from chapter length, lecture time, practice
bank frequency, or search-result prominence.

## Public standardized examinations

When the target is a publicly documented national, state, professional, or
licensing examination, search for the current public specification before
using commercial preparation material. Start with the body that owns the exam
or credential. Then inspect its current candidate handbook, test plan or
content outline, rules, official samples, errata, and change notices. For an
exam built from a public question pool, obtain the current pool, syllabus or
element design, effective dates, withdrawn questions, diagrams, and generation
rules from the body responsible for that pool.

Examples of authority paths include the National Registry and its current
candidate handbooks and test plans for NREMT certification, and the FCC rules
plus the current NCVEC question pool and element specification for United
States amateur radio licensing. These are examples, not frozen facts. Recheck
the named official sources for the learner's exam date, credential level, and
jurisdiction. Record the URL, title, publication or revision date, effective
window, access date, and any relevant local requirement. A public source may
be authoritative without granting unrestricted copying, transformation, or
redistribution, so record rights separately.

## Required assessment profile

Capture these fields when they apply. Use `unknown`, `not published`, or `not
applicable` instead of inventing a value.

| Area | Required record |
|---|---|
| Purpose | Diagnostic, formative, summative, placement, certification, or selection; the decision the result supports |
| Population | Intended learner, prerequisites, jurisdiction, course or exam version, effective dates |
| Scope | Tested domains and objectives, explicit exclusions, assumed prerequisite knowledge, and optional or sampled content |
| Construct | Observable knowledge or performance being measured, cognitive or performance demand, and prohibited construct-irrelevant shortcuts |
| Distribution | Domain weights or ranges, item counts or ranges, sampled versus guaranteed coverage, difficulty model, and changed-context transfer expectations |
| Format | Item families, response modes, sections, dependencies, adaptive or fixed form, case or stimulus rules, and scored versus unscored items |
| Conditions | Time limits, breaks, attempts, delivery mode, permitted tools and references, collaboration rules, and accommodations process |
| Scoring | Point model, partial credit, penalties, weighting, rounding, aggregation, and which authority settles each response type |
| Standard | Pass, grade, mastery, or competency rule; cut score or grade bands; conjunctive rules; minimum section scores; and whether the standard may change |
| Review | Human or model advisory grading, rubric version, blind or moderated marking, appeals, rescoring, and treatment of pending prose |
| Retakes | Eligibility, waiting period, attempt limits, supersession or averaging rule, and which evidence remains historical |
| Reporting | Score scale, subscores, confidence or uncertainty, feedback timing, keyed-content disclosure, retention, privacy, and export rules |

## Focus and format fit

Classify proposed course content into three lanes:

- **Core:** required by the target outcome or governing assessment profile.
- **Support:** prerequisite teaching or practice needed to perform the core
  task, even if it is not directly scored.
- **Enrichment:** useful breadth that is outside the tested or required scope.

Default plans spend time and authoring effort on core material first, then the
minimum support needed to make it learnable. Enrichment remains discoverable
and may be offered as an explicit learner choice, but it is not silently added
to the default path. Do not equate "not tested" with "not useful" or delete it
from the disposition record.

Match assessment practice to the actual response work. If the target exam is
single-selection multiple choice, default scored practice and mock exams to
that format and its documented constraints. Do not author essays, drag and
drop tasks, oral defenses, or projects as default assessment merely because
the system supports them. Use a different format only when at least one of
these conditions holds:

1. The governing assessment uses it.
2. It is the smallest useful teaching or diagnostic treatment for a core
   objective, and it is labeled as learning practice rather than exam mimicry.
3. The learner explicitly opts into enrichment or deeper transfer practice.
4. A separate course-completion requirement needs it.

Format fidelity does not mean copying secure or proprietary items. Reproduce
the documented response demands, timing, navigation, tool constraints, item
mix, and scoring behavior as closely as rights and shipped capabilities allow.
Record every known mismatch between practice and the real assessment.

For classroom courses, also capture the grading composition across exams,
quizzes, assignments, participation, projects, labs, and extra credit. Record
late, missing, dropped-score, makeup, academic-integrity, and attendance rules
only from an authoritative policy. Separate the official grade from the
itembank evidence used to recommend study.

## Blueprint table

Create one row per assessed domain or objective:

```text
Objective | Source locator | Included/excluded | Weight/range | Demand |
Item families | Conditions | Scoring authority | Coverage status | Confidence
```

Preserve ranges as ranges. Convert a weight to an item count only when the form
length is fixed, and show the rounding rule. Mark whether coverage is
guaranteed on every form or only sampled across forms. Keep content coverage,
item coverage, teaching coverage, and grading weight as separate claims.

## Grading policy rules

- The deterministic runtime settles objective item scores and session state.
- Constructed prose stays pending until the configured reviewer settles it.
  A model may produce a labeled advisory grade only when the operation permits
  it, and that proposal never becomes the settled mark by implication.
- A rubric names criteria, performance levels, point allocation, acceptable
  variation, required evidence, and escalation conditions. Keywords alone are
  not a rubric.
- Do not invent a pass mark, curve, partial-credit rule, penalty, grade band,
  or mastery threshold. If no authority supplies one, propose alternatives and
  leave the decision pending.
- Do not treat practice performance as an official grade or transfer evidence
  between objectives because their labels appear aligned.

## Readiness gate

Before claiming exam alignment or authoring summative items, verify that the
governing version, tested scope, construct, distribution, formats, conditions,
and scoring authority are known. If any high-impact field is unresolved, the
course may proceed with direct reading, lessons, or exploratory practice, but
label summative coverage and score interpretation as provisional. Close the
intake with unresolved questions, the named decision owner, and the exact
source or review needed to settle each one.

Also verify that every default-path artifact is justified as core or necessary
support, and that its response format matches the assessment or has a stated
teaching reason. Keep enrichment out of the default workload unless the learner
opts in.
