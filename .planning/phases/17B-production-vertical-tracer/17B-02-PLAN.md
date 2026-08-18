---
phase: 17B-production-vertical-tracer
plan: 02
type: execute
wave: 2
depends_on: ["17B-01"]
files_modified:
  - course_fixture_17b/unit3_lesson.md
  - course_fixture_17b/unit3_bank.md
  - course_fixture_17b/treatments.md
  - .planning/phases/17B-production-vertical-tracer/17B-GATES.md
  - .planning/phases/17B-production-vertical-tracer/evidence/17B-02-binding.md
  - .planning/phases/17B-production-vertical-tracer/evidence/17B-02-faults.md
  - .planning/phases/17B-production-vertical-tracer/evidence/17B-02-coverage.md
autonomous: true
requirements: [G1, G2, G3, G7]
must_haves:
  truths:
    - "Every fixture artifact names its durable object, owner, authority, and source of truth before authoring begins (G2)."
    - "Each objective's treatment decision cites scope, demand, rationale, uncertainty, and the existing-artifact search, and passes review before authoring (G7)."
    - "The unit survives move, external edit, conflict, and interrupted write, preserving old or new valid state (G3)."
  artifacts:
    - "course_fixture_17b/unit3_lesson.md and unit3_bank.md, authored through the skills and lint clean"
    - "evidence/17B-02-binding.md and evidence/17B-02-faults.md"
  key_links:
    - "Gate rows flip from pending only when their evidence pointer names a file in evidence/ (17B-CONTEXT D-04)."
    - "Any capability gap found here is a defect against the owning subphase, never a 17B invention (17B-CONTEXT D-06)."
---
<objective>
Run discovery through accepted authoring on the fixture course: binding and
inventory, the cited objective map, a reviewed treatment decision per
objective, and the unit's lesson and bank authored through the skills and the
lint loop, collecting G1, G2, G3, and G7 evidence including the G3 file-fault
drills, per the ROADMAP wave 2 block and 17B-CONTEXT D-02, D-04, D-06. Surface
commands frozen by earlier subphases are cited by contract; this plan pins its
own artifacts with commands runnable today.
</objective>
<context>
@.planning/phases/17B-production-vertical-tracer/17B-CONTEXT.md
@.planning/phases/17B-production-vertical-tracer/17B-GATES.md
@course_fixture_17b/objectives.md
@.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md (operation and journal commands)
@.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md (binding and graph commands)
@.planning/phases/15B-quality-blueprint-acceptance/15B-FREEZE.md (review and acceptance commands)
</context>
<tasks>
<task type="auto">
  <name>Task 1: binding, inventory, and the object and authority record (G2, part of G1)</name>
  <files>.planning/phases/17B-production-vertical-tracer/evidence/17B-02-binding.md, .planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>14A-FREEZE.md and 14B-FREEZE.md for the frozen discovery, binding, and inventory commands; AGENTS.md object and authority summary.</read_first>
  <action>
1. Run the frozen discovery and binding flow over `course_fixture_17b/` using
   the exact commands 14A-FREEZE.md and 14B-FREEZE.md record; transcribe each
   command and its output into evidence/17B-02-binding.md.
2. For every fixture artifact (scope, two sources, objectives), record its
   durable object type, owner, authority, and source of truth, and demonstrate
   one derived view rebuilding from canonical files.
3. Update 17B-GATES.md: row G2 state to `pass` (or a D-06 defect line naming
   mechanism and owner), evidence pointer to evidence/17B-02-binding.md, and
   the proof column filled with the proving command or fixture name.
4. If any step makes a hosted-model call, record its disclosed egress manifest
   and the captured outbound payload into evidence/ at call time (17B-CONTEXT
   D-09); wave 4 cannot reconstruct sent bytes retroactively.
  </action>
  <verify>evidence/17B-02-binding.md names all four artifacts; row G2 no longer reads `pending`; `python itembank.py guard .` exits 0.</verify>
</task>
<task type="auto">
  <name>Task 2: cited objective map and reviewed treatment decisions (G7)</name>
  <files>course_fixture_17b/treatments.md, .planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>15A-FREEZE.md treatment policy contract; 15B-FREEZE.md review mechanics; course_fixture_17b/objectives.md.</read_first>
  <action>
1. For each objective in objectives.md, record in treatments.md: the chosen
   treatment (including direct source reading where best), scope, demand,
   rationale, uncertainty, and the existing-artifact search result (for this
   fresh fixture, "no prior artifact found", stated explicitly).
2. Pass each decision through the review step the 15B contract froze, before
   any authoring; transcribe the review command and verdict per objective.
3. At least one objective's treatment is direct source reading with a `[SRC:]`
   locator; at least one calls for a lesson plus practice.
4. Update 17B-GATES.md row G7 with state, evidence pointer, and the proof
   column filled, as in Task 1.
  </action>
  <verify>treatments.md carries one block per objective with all six fields; row G7 updated; and
```
python -c "import glob,sys; bad=[f for f in glob.glob('course_fixture_17b/**/*.md',recursive=True) if chr(8212) in open(f,encoding='utf-8').read()]; sys.exit(bad) if bad else print('no em dash')"
```
prints `no em dash`, exit 0.</verify>
</task>
<task type="auto">
  <name>Task 3: author the unit lesson and bank through the skills and lint loop (G1)</name>
  <files>course_fixture_17b/unit3_lesson.md, course_fixture_17b/unit3_bank.md, .planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>The lesson-authoring and author-bank skill contracts; 16A-FREEZE.md capability and activity contract; 17B-UI-SPEC.md section 2 checklist.</read_first>
  <action>
1. Author unit3_lesson.md through the lesson-authoring skill contract (if that
   skill is still a stub, author against the 16A contract directly and record
   the skill gap as a D-06 defect). The lesson carries every 17B-UI-SPEC
   section 2 capability: term definitions, one things-to-know block, one
   expert-tip block, one cited visual explanation with static fallback, one
   prediction prompt, and stays coherent in a plain Markdown reader.
2. Author unit3_bank.md through the author-bank skill's write, lint, fix loop:
   varied types, one short-answer item, one transfer item, every item cited to
   an objective. Synthesis labeled, citations retained.
3. Write evidence/17B-02-coverage.md: the G1 map from every capability the
   tracer exercises to its requirement row and ledger disposition; no
   undischarged tracer promise. Update 17B-GATES.md row G1 with state, the
   evidence pointer to that file, and the proof column filled.
  </action>
  <verify>`python itembank.py lint course_fixture_17b/unit3_bank.md` exits 0 with zero errors; `python itembank.py guard .` exits 0; row G1's evidence pointer names evidence/17B-02-coverage.md.</verify>
</task>
<task type="auto">
  <name>Task 4: file-fault drills on the fixture unit (G3)</name>
  <files>.planning/phases/17B-production-vertical-tracer/evidence/17B-02-faults.md, .planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>14A-FREEZE.md compare-and-swap and journal mechanics; AGENTS.md mutation rules.</read_first>
  <action>
1. Run the four drills on the authored unit, using the frozen 14A operation
   commands: (a) move unit3_lesson.md and confirm re-binding, not silent loss;
   (b) external edit to unit3_bank.md and confirm stale or conflict state,
   never silent overwrite; (c) same-ID divergent-bytes conflict surfaced as a
   conflict; (d) interrupted write (kill mid-operation) leaving old or new
   valid state, verified by re-lint.
2. Transcribe each drill's commands, observed state, and recovery into
   evidence/17B-02-faults.md. A drill the frozen surface cannot express is a
   D-06 defect against 14A, recorded with mechanism and owner, never skipped
   silently.
3. Update 17B-GATES.md row G3 with state, evidence pointer, and the proof
   column filled.
  </action>
  <verify>evidence/17B-02-faults.md records all four drills; afterward `python itembank.py lint course_fixture_17b/unit3_bank.md` still exits 0; row G3 updated.</verify>
</task>
</tasks>
<out_of_scope>New tokens, new dependencies, scorer or parser edits, real course content in-repo, the learner pass (wave 3), the restore drill (wave 4), repairing earlier phases beyond D-06's single-file bound, and writes under fixtures/.</out_of_scope>
<summary_obligations>Record in 17B-02-SUMMARY.md: every frozen-contract command used with its source freeze file, lint and guard outputs verbatim, each gate row's new state, and every D-06 defect with mechanism and owner.</summary_obligations>
