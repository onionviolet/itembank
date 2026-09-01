# Unit 3 treatment decisions

Recorded 2026-09-01 by plan 17B-02 Task 2, before any authoring, per the
15A treatment policy vocabulary (`graph.TREATMENT_KINDS`) and the
operation protocol's plan-treatment step. Every block carries the six
required fields: treatment, scope, demand, rationale, uncertainty, and
the existing-artifact search result. The review verdicts are transcribed
at the bottom; each decision passed review before Task 3 authored
anything. All content is synthetic (Aldrasse fen ecology, invented for
the tracer).

The existing-artifact search: the approved roots for this operation are
`course_fixture_17b/` (read and write) and nothing else. The inventory
walked every file in the root (README, scope, objectives, treatments,
the two sources, the course sidecar and its journal). No lesson, bank,
activity, or exam artifact exists for any objective, so every block
below states its search result explicitly rather than by omission.

## O3.1 minerotrophy and mineral inflow

- treatment: guided-lesson plus practice
- scope: the basin overview section only; no other wetland types
  [SRC: sources/fen_hydrology_field_notes.md#basin-overview]
- demand: application (explain the mechanism and apply it to the plant
  community, not recite the definition)
- rationale: the source states the chemistry but scatters the causal
  chain across paragraphs; a short lesson section assembling the chain,
  then practice items, teaches the mechanism better than raw reading
- uncertainty: low; the source section is complete and internally
  consistent
- existing-artifact search: no prior artifact found

## O3.2 acrotelm and catotelm dynamics

- treatment: guided-lesson plus practice
- scope: the two-layer structure and the storm-versus-recharge contrast
  [SRC: sources/fen_hydrology_field_notes.md#water-table-dynamics]
- demand: application (predict the water table response to a named event)
- rationale: prediction from structure is the point; a lesson section
  with a worked contrast, then practice requiring a prediction
- uncertainty: low
- existing-artifact search: no prior artifact found

## O3.3 the drought threshold

- treatment: notes-or-terms plus practice
- scope: the single 25 cm threshold and its vegetation signal
  [SRC: sources/fen_hydrology_field_notes.md#water-table-dynamics]
- demand: recall (a stated threshold and its named signal)
- rationale: one hard number and one signal; a must-know card and a
  glossary term serve recall better than paragraphs
- uncertainty: low
- existing-artifact search: no prior artifact found

## O3.4 peat accumulation and profile age

- treatment: worked-example plus practice
- scope: accumulation tracking water table position, and one age
  estimate from a stated rate
  [SRC: sources/fen_hydrology_field_notes.md#peat-accumulation-and-decay]
- demand: application (carry out the estimate, not restate the rate)
- rationale: the estimate is a calculation; a worked example in the
  lesson, then a practice item with changed numbers
- uncertainty: medium; the source gives one rate and one profile, so
  transfer to other rates is authored synthesis, labeled as such
- existing-artifact search: no prior artifact found

## O3.5 the lagg boundary

- treatment: direct source reading, plus one practice item on the
  trigger condition
- scope: the whole lagg section, read as written
  [SRC: sources/fen_hydrology_field_notes.md#mineral-inflow-and-the-lagg-boundary]
- demand: application (state the two roles and the A1 trigger)
- rationale: the source section already teaches this well: it is
  narrative, ordered, and self-contained, and a paraphrase would lose
  the field-notes voice without adding structure. Direct reading is the
  first-class outcome here, not a failure to generate
- uncertainty: low
- existing-artifact search: no prior artifact found

## O3.6 the lantern moss annual cycle

- treatment: guided-lesson plus visual-or-demonstration plus practice
- scope: the four phases and the early-summer hinge
  [SRC: sources/lantern_moss_survey.md#annual-cycle]
- demand: analysis (sequence the phases and explain the hinge, which
  requires relating two of them)
- rationale: a cycle is the one shape prose serves worst; a cited
  diagram with a static text fallback, beside a lesson section, then
  ordering practice
- uncertainty: low for the sequence; the hinge explanation leans on one
  survey season, stated in the lesson's uncertainty callout
- existing-artifact search: no prior artifact found

## O3.7 vitality scores as an instrument

- treatment: guided-lesson plus practice, with the unit's transfer item
- scope: the station-mean threshold, its drought equivalence, and the
  connection to the dipwell threshold in the hydrology notes
  [SRC: sources/lantern_moss_survey.md#hydrological-sensitivity]
- demand: analysis (connect two sources' thresholds and apply them in a
  changed context)
- rationale: the connection spans both sources, so no single section
  teaches it; a short synthesis lesson section (labeled synthesis, both
  citations retained) plus a changed-context transfer item
- uncertainty: medium; the cross-source equivalence is the survey's own
  claim, made in one season's data
- existing-artifact search: no prior artifact found

## Review verdicts (15B review discipline, 15A protocol record)

Each decision above was recorded as a `plan-treatment` protocol phase
and passed a `review` phase in the operation journal before Task 3
authored anything, through the frozen 15A director surface
(`director.begin_operation`, `director.record_phase`, the thirteen-step
vocabulary 15A-FREEZE.md freezes), and each reviewed treatment was then
bound through the frozen rights-gated 14B path
(`course.bind_treatment`, which re-reads the live rights registry per
call). The review verdicts were recorded under Weibao's standing
2026-09-01 delegation and are labeled agent-recorded in the journal
entries themselves.

| objective | operation id | plan-treatment | review verdict |
|---|---|---|---|
| O3.1 | f43d3c87c7524fe8 | recorded | accepted |
| O3.2 | a94f46d82fd84733 | recorded | accepted |
| O3.3 | a2d75851f0c449df | recorded | accepted |
| O3.4 | f777389b874d49b0 | recorded | accepted |
| O3.5 | 5605575fbc174920 | recorded | accepted |
| O3.6 | df0d82a66f48426c | recorded | accepted |
| O3.7 | f7de6c9eef0b4962 | recorded | accepted |

Output of the review run, verbatim (command: `PYTHONPATH=. python3
t2_review.py` from the repository root; the script's full text is
transcribed in
`.planning/phases/17B-production-vertical-tracer/evidence/17B-02-coverage.md`):

```
O3.1 operation f43d3c87c7524fe8 review recorded; protocol verdict incomplete (incomplete is expected: authoring phases follow in Task 3)
  bound treatment guided-lesson            revision 10
  bound treatment practice                 revision 11
O3.2 operation a94f46d82fd84733 review recorded; protocol verdict incomplete (incomplete is expected: authoring phases follow in Task 3)
  bound treatment guided-lesson            revision 12
  bound treatment practice                 revision 13
O3.3 operation a2d75851f0c449df review recorded; protocol verdict incomplete (incomplete is expected: authoring phases follow in Task 3)
  bound treatment notes-or-terms           revision 14
  bound treatment practice                 revision 15
O3.4 operation f777389b874d49b0 review recorded; protocol verdict incomplete (incomplete is expected: authoring phases follow in Task 3)
  bound treatment worked-example           revision 16
  bound treatment practice                 revision 17
O3.5 operation 5605575fbc174920 review recorded; protocol verdict incomplete (incomplete is expected: authoring phases follow in Task 3)
  bound treatment direct-reading           revision 18
  bound treatment practice                 revision 19
O3.6 operation df0d82a66f48426c review recorded; protocol verdict incomplete (incomplete is expected: authoring phases follow in Task 3)
  bound treatment guided-lesson            revision 20
  bound treatment visual-or-demonstration  revision 21
  bound treatment practice                 revision 22
O3.7 operation f7de6c9eef0b4962 review recorded; protocol verdict incomplete (incomplete is expected: authoring phases follow in Task 3)
  bound treatment guided-lesson            revision 23
  bound treatment practice                 revision 24
```
