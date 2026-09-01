---
phase: 17B-production-vertical-tracer
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/phases/17B-production-vertical-tracer/17B-PRECONDITION.md
  - .planning/phases/17B-production-vertical-tracer/17B-GATES.md
  - course_fixture_17b/README.md
  - course_fixture_17b/scope.md
  - course_fixture_17b/objectives.md
  - course_fixture_17b/sources/fen_hydrology_field_notes.md
  - course_fixture_17b/sources/lantern_moss_survey.md
autonomous: true
requirements: [17B fixture rule, 17B-CONTEXT D-01, D-02, D-03, D-04]
must_haves:
  truths:
    - "Execution halts by exact artifact name unless 14A, 14B, 15A, 15B, 16A, 16B, 16C, 17A, and 13.9 are all recorded complete on disk."
    - "The fixture course is fully synthetic, at production depth, and itembank guard clean."
    - "17B-GATES.md carries one pending row per gate G1 through G11 before any evidence exists."
  artifacts:
    - ".planning/phases/17B-production-vertical-tracer/17B-PRECONDITION.md with a dated result line"
    - "course_fixture_17b/ with scope tree, two sources, and cited objectives"
    - "17B-GATES.md with eleven rows"
  key_links:
    - "17A-FREEZE.md must contain a freeze, not a withholding; a Freeze withheld heading is a failed check (17B-CONTEXT D-01)."
    - "course_fixture_17b/ sits at the repo root, deliberately outside fixtures/, because fixtures/ has concurrent in-flight edits as of 2026-08-17."
---
<objective>
Establish what every later 17B wave stands on: the recorded precondition halt
(17B-CONTEXT D-01), the realistic synthetic fixture course with its scope tree
(17B-CONTEXT D-02, D-03), and the gate scaffold (17B-CONTEXT D-04). Surface
commands frozen by earlier subphases are cited by contract; this plan pins its
own artifacts with commands runnable today.
</objective>
<context>
@.planning/phases/17B-production-vertical-tracer/17B-CONTEXT.md
@.planning/phases/17B-production-vertical-tracer/17B-UI-SPEC.md
@.planning/ROADMAP.md (section "Phase 17B: Production Vertical Tracer")
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-01-PLAN.md (Task 1, the halt precedent)
</context>
<tasks>
<task type="auto">
  <name>Task 1: precondition check with halt by name</name>
  <files>.planning/phases/17B-production-vertical-tracer/17B-PRECONDITION.md</files>
  <read_first>17B-CONTEXT.md D-01; 16C-01-PLAN.md Task 1 for the halt shape.</read_first>
  <action>
1. Verify each named artifact exists. Run, from the repository root:
```
python -c "import os,sys; base='.planning/phases/'; files=[base+'14A-identity-lifecycle-operation/14A-FREEZE.md', base+'14B-graph-course-package-prototype/14B-FREEZE.md', base+'15A-director-treatment-policy/15A-FREEZE.md', base+'15B-quality-blueprint-acceptance/15B-FREEZE.md', base+'16A-semantic-capability-activity-contract/16A-FREEZE.md', base+'16B-ia-modes-recovery-contract/16B-FREEZE.md', base+'16C-strategies-notes-prototype-convergence/16C-FREEZE.md', base+'17A-visual-system-component-foundation/17A-FREEZE.md', base+'13.9-walking-skeleton/13.9-01-SUMMARY.md', base+'13.9-walking-skeleton/13.9-02-SUMMARY.md', base+'13.9-walking-skeleton/13.9-03-SUMMARY.md']; missing=[f for f in files if not os.path.exists(f)]; sys.exit('HALT 17B-01: missing precondition artifact: '+missing[0]) if missing else print('precondition artifacts present')"
```
   Expected stdout on success: `precondition artifacts present`, exit 0. On any
   miss: stderr `HALT 17B-01: missing precondition artifact: <exact path>`,
   nonzero exit. The halt is the correct outcome; do not stub, skip, or proceed
   with a reduced check set.
2. Verify every plan in the seven executed phases carries a matching SUMMARY
   (each `*-PLAN.md` beside a `*-SUMMARY.md`). Run, from the repository root:
```
python -c "import glob,os,sys; dirs=['14A-identity-lifecycle-operation','14B-graph-course-package-prototype','15A-director-treatment-policy','15B-quality-blueprint-acceptance','16A-semantic-capability-activity-contract','16B-ia-modes-recovery-contract','16C-strategies-notes-prototype-convergence']; missing=[p for d in dirs for p in sorted(glob.glob('.planning/phases/'+d+'/*-PLAN.md')) if not os.path.exists(p.replace('-PLAN.md','-SUMMARY.md'))]; sys.exit('HALT 17B-01: plan without summary: '+missing[0]) if missing else print('plan-summary pairing complete')"
```
   Expected stdout on success: `plan-summary pairing complete`, exit 0. On any
   miss: the HALT line with the exact plan path, nonzero exit.

   **Amendment, 2026-09-01 (coordinator, under Weibao's standing 2026-09-01
   delegation; original check text above preserved unchanged).** The
   plan-summary pairing check exempts `15A-director-treatment-policy` and
   `15B-quality-blueprint-acceptance`: those phases recorded execution
   phase-wide (`15A-REVIEW.md`, `15A-TRACER-REPORT.md`, `15A-FREEZE.md`;
   `15B-REVIEW.md`, `15B-TRACER-REPORT.md`, `15B-FREEZE.md`, `COVERAGE.md`)
   and never adopted per-plan summaries, and the check's intent is "no plan
   executed without a record", not "every phase used the per-plan record
   shape". For those two phases the amended check verifies the named
   phase-wide records exist on disk instead. The amended command, which
   replaces the step 2 command above:
```
python -c "import glob,os,sys; dirs=['14A-identity-lifecycle-operation','14B-graph-course-package-prototype','16A-semantic-capability-activity-contract','16B-ia-modes-recovery-contract','16C-strategies-notes-prototype-convergence']; missing=[p for d in dirs for p in sorted(glob.glob('.planning/phases/'+d+'/*-PLAN.md')) if not os.path.exists(p.replace('-PLAN.md','-SUMMARY.md'))]; pw=[f for f in ['.planning/phases/15A-director-treatment-policy/15A-REVIEW.md','.planning/phases/15A-director-treatment-policy/15A-TRACER-REPORT.md','.planning/phases/15A-director-treatment-policy/15A-FREEZE.md','.planning/phases/15B-quality-blueprint-acceptance/15B-REVIEW.md','.planning/phases/15B-quality-blueprint-acceptance/15B-TRACER-REPORT.md','.planning/phases/15B-quality-blueprint-acceptance/15B-FREEZE.md','.planning/phases/15B-quality-blueprint-acceptance/COVERAGE.md'] if not os.path.exists(f)]; sys.exit('HALT 17B-01: plan without summary: '+missing[0]) if missing else (sys.exit('HALT 17B-01: missing phase-wide execution record: '+pw[0]) if pw else print('plan-summary pairing complete'))"
```
   Expected stdout on success: `plan-summary pairing complete`, exit 0. On
   any miss: the HALT line naming the exact plan path or phase-wide record,
   nonzero exit. The three per-plan gaps in phases whose record shape IS
   per-plan summaries (16A-01, 16A-10, 16C-09) are not exempted; they were
   closed by retrospective summaries dated 2026-09-01, the 14B-04 and
   14B-05 precedent.
3. Verify 17A-FREEZE.md records a freeze, not a withholding:
```
python -c "t=open('.planning/phases/17A-visual-system-component-foundation/17A-FREEZE.md',encoding='utf-8').read(); import sys; sys.exit('HALT 17B-01: 17A-FREEZE.md is a withholding, not a freeze') if '## Freeze withheld' in t or '## Frozen at' not in t else print('17A freeze confirmed')"
```
   Expected stdout: `17A freeze confirmed`, exit 0.
4. Write 17B-PRECONDITION.md: dated result line, every artifact checked, and
   the exact halt text if any check failed. No em dash characters.
  </action>
  <verify>All three commands exit 0 and 17B-PRECONDITION.md exists with a dated result line; or the run halted with the exact missing artifact named.</verify>
</task>
<task type="auto">
  <name>Task 2: create the realistic synthetic fixture course</name>
  <files>course_fixture_17b/README.md, course_fixture_17b/scope.md, course_fixture_17b/objectives.md, course_fixture_17b/sources/fen_hydrology_field_notes.md, course_fixture_17b/sources/lantern_moss_survey.md</files>
  <read_first>17B-CONTEXT.md D-02 and D-03; ROADMAP fixture rule; IDEA-LEDGER IL-20260817-01.</read_first>
  <action>
1. Create `course_fixture_17b/` at the repository root. README.md states, in
   these words: "This course is entirely synthetic. The subject, Aldrasse fen
   ecology, is invented for the 17B tracer at production depth and derives from
   no real course material. This directory sits outside fixtures/ deliberately:
   fixtures/ has concurrent in-flight edits as of 2026-08-17."
2. Write scope.md with the D-03 tree: open field scope "Fenland Systems" (open,
   never complete, states its scope version on every claim), bounded course
   scope "Aldrasse Fen Ecology 101" with its named completion predicate,
   containing one unit, "Unit 3: Peat Hydrology and the Lantern Moss Cycle".
   The scope-object format is frozen by the 14B contract; follow 14B-FREEZE.md.
3. Write two synthetic sources at production depth (each 400 words minimum,
   headed sections, stable locator anchors): fen_hydrology_field_notes.md and
   lantern_moss_survey.md.
4. Write objectives.md: five to eight unit objectives, each carrying a
   `[SRC: <source file>#<anchor>]` citation into one of the two sources.
5. No real course content, no AAOS-derivative text, no em dash characters.
  </action>
  <verify>`python itembank.py guard .` exits 0 with zero offenders, and
```
python -c "import glob,sys; bad=[f for f in glob.glob('course_fixture_17b/**/*.md',recursive=True) if chr(8212) in open(f,encoding='utf-8').read()]; sys.exit(bad) if bad else print('no em dash')"
```
prints `no em dash`, exit 0.</verify>
</task>
<task type="auto">
  <name>Task 3: gate checklist scaffold</name>
  <files>.planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>17B-CONTEXT.md D-04; ROADMAP G1 through G11 concrete checks.</read_first>
  <action>
1. Write 17B-GATES.md as a Markdown table with columns, exactly: gate, concrete
   check, proof command or fixture, evidence pointer, state.
2. One row per gate G1 through G11, the concrete check transcribed from the
   ROADMAP details block, proof and evidence columns `pending`, state `pending`.
3. Note beneath the table, verbatim: "Human checkpoints are mandatory for the
   G4 screen-reader item and the final visual acceptance; an agent never
   self-certifies those (17B-CONTEXT D-04)."
  </action>
  <verify>`grep -c "^| G" .planning/phases/17B-production-vertical-tracer/17B-GATES.md` prints `11`, and the Task 2 em dash check run over the file prints `no em dash`.</verify>
</task>
</tasks>
<out_of_scope>New tokens or primitives, new dependencies, scorer or parser edits, real course content in-repo, authoring the unit lesson or bank (wave 2), repairing earlier phases beyond D-06's single-file bound, and any write under fixtures/.</out_of_scope>
<summary_obligations>Record in 17B-01-SUMMARY.md: the precondition result line (or exact halt), the fixture file list with word counts, guard and em dash outputs verbatim, and the gate table row count.</summary_obligations>
