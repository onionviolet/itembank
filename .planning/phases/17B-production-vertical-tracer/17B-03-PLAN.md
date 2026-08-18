---
phase: 17B-production-vertical-tracer
plan: 03
type: execute
wave: 3
depends_on: ["17B-02"]
files_modified:
  - .planning/phases/17B-production-vertical-tracer/evidence/17B-03-learner-pass.md
  - .planning/phases/17B-production-vertical-tracer/evidence/17B-03-rollup-choice.md
  - .planning/phases/17B-production-vertical-tracer/evidence/17B-03-legacy-audit.md
  - .planning/phases/17B-production-vertical-tracer/17B-GATES.md
autonomous: false
requirements: [G4, G5, G6, G8, G9, 17B-CONTEXT D-03, D-04, D-05]
must_haves:
  truths:
    - "All eight journey stages of 17B-UI-SPEC section 1 run on the fixture unit with evidence per stage."
    - "Both rollup models render over identical GRAPH-03 tuples and Weibao, not an agent, picks the default (17B-CONTEXT D-03)."
    - "The G4 screen-reader item and the visual acceptance are settled only by a human (17B-CONTEXT D-04)."
  artifacts:
    - "evidence/17B-03-learner-pass.md covering stages 1 through 8"
    - "evidence/17B-03-rollup-choice.md recording the checkpoint answer"
    - "evidence/17B-03-legacy-audit.md with the D-05 bounded diff"
  key_links:
    - "Hints stay collapsed by default and never pre-announce a reveal (RTS-09, 17A disclosure contract)."
    - "The short-answer item must remain pending until marked; a settled prose score before marking is a G6 failure."
---
<objective>
Run the learner pass end to end on the authored unit per 17B-UI-SPEC section 1
stages 1 through 8, render both rollup screens for Weibao's default choice, run
the D-05 legacy upgrade audit, and collect the G4, G5, G6, G8, and G9 evidence
rows, with the screen-reader item and visual acceptance held for human
verification (17B-CONTEXT D-04). Surface commands frozen by earlier subphases
are cited by contract; this plan pins its own artifacts with commands runnable
today.
</objective>
<context>
@.planning/phases/17B-production-vertical-tracer/17B-UI-SPEC.md
@.planning/phases/17B-production-vertical-tracer/17B-CONTEXT.md
@.planning/phases/17B-production-vertical-tracer/17B-GATES.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-FREEZE.md (routes and interruption scenarios)
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-FREEZE.md (notes and strategy behavior)
@.planning/UI-SPEC.md (section 8 accessibility gates)
</context>
<tasks>
<task type="auto">
  <name>Task 1: the learner pass, stages 1 through 8 (G4 agent half, G5, G6, G8, G9)</name>
  <files>.planning/phases/17B-production-vertical-tracer/evidence/17B-03-learner-pass.md, .planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>17B-UI-SPEC.md sections 1 through 4 in full; 16B-FREEZE.md route table; 16C-FREEZE.md note-authority guard.</read_first>
  <action>
1. Run stages 1 through 8 on the fixture unit using the serving commands the
   16B and 17A freezes record, at 1280, 768, and 375 widths, by keyboard and
   by touch, and once fully offline: arrive and resume, orient with cited
   sources and inspectable locators, predict (participation evidence only,
   never a graded verdict), read the lesson with every section 2 capability,
   practice with the hint ladder collapsed by default and never pre-announcing
   a reveal, graded sitting with the short-answer item left pending until
   marked and no key disclosed before the runtime's gate, both rollup screens
   (expected 17A primitives: ProgressComprehensionDisplay for ROLLUP-DIM and
   the fill-state blocks plus card primitive for ROLLUP-MAP child cards; if
   the 17A freeze lacks a fitting card primitive, record a 17A-03 primitive
   gap defect per 17B-CONTEXT D-06 before the Task 2 checkpoint, per the
   17B-UI-SPEC sign-off recommendation), and course-path continuation with
   one sampled 16B interruption scenario.
2. Confirm the lesson opens coherently in a plain Markdown reader outside the
   app (agent half of G4; the screen-reader half is Task 4).
3. For G9, record for each offered strategy: choice, requirement, skip and
   resume, accommodation, evidence effect, privacy, provenance, and the
   note-authority guard.
4. Transcribe every command, width, input mode, and observation into
   evidence/17B-03-learner-pass.md, one section per stage. If any step makes
   a hosted-model call, record its disclosed egress manifest and the captured
   outbound payload into evidence/ at call time (17B-CONTEXT D-09). Update
   gate rows G5, G6, G8, G9 with state, evidence pointer, and the proof
   column filled, and mark G4's state `human-pending`. Any gap is a D-06
   defect with mechanism and owner, never a silent skip.
  </action>
  <verify>evidence/17B-03-learner-pass.md carries eight stage sections; rows G5, G6, G8, G9 no longer read `pending` and G4 reads `human-pending`; `python itembank.py guard .` exits 0.</verify>
</task>
<task type="checkpoint:decision">
  <name>Task 2: Weibao picks the default rollup model (G5, 17B-CONTEXT D-03)</name>
  <files>.planning/phases/17B-production-vertical-tracer/evidence/17B-03-rollup-choice.md</files>
  <read_first>17B-UI-SPEC.md section 3; the two rendered rollup screens from Task 1.</read_first>
  <action>
Show Weibao both rendered screens over the same GRAPH-03 tuples and ask,
verbatim: "Which rollup model is the global default? Options: ROLLUP-DIM
(dimension-wise, stated denominators) and ROLLUP-MAP (one-level map view).
Recommended default: ROLLUP-MAP for scope trees deeper than one level,
ROLLUP-DIM otherwise." Record the answer, date, and the per-scope override
note in evidence/17B-03-rollup-choice.md. An unanswered checkpoint stops the
wave; it never gets a silent default.
  </action>
  <verify>evidence/17B-03-rollup-choice.md names the chosen model, the chooser as Weibao, and the date.</verify>
</task>
<task type="auto">
  <name>Task 3: legacy upgrade audit (17B-CONTEXT D-05)</name>
  <files>.planning/phases/17B-production-vertical-tracer/evidence/17B-03-legacy-audit.md, .planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>17B-CONTEXT.md D-05; the legacy-upgrade skill contract; CLAUDE.md course artifact workflow step 7.</read_first>
  <action>
1. Choose one legacy lesson and one legacy question artifact from the
   repository's synthetic fixtures (never real banks) and name them in the
   evidence file.
2. Run the upgrade audit per D-05: baseline audit before edit, learning-value
   delta stated, identity and assessment meaning preserved, bounded diff
   presented, static and accessibility fallbacks retained. If the
   legacy-upgrade skill is still a stub, audit against the operation contract
   directly and record the skill gap as a D-06 defect, not silently filled.
3. Write the bounded diff and each check's outcome into
   evidence/17B-03-legacy-audit.md; append the result to gate row G1's
   evidence pointer.
  </action>
  <verify>evidence/17B-03-legacy-audit.md names both artifacts and all five D-05 checks; `python itembank.py lint <audited bank path>` (the exact path named in the evidence file) exits 0.</verify>
</task>
<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 4: human screen-reader item and visual acceptance (G4, G8, 17B-CONTEXT D-04)</name>
  <files>.planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>evidence/17B-03-learner-pass.md; .planning/UI-SPEC.md section 8.</read_first>
  <action>
Ask Weibao to walk the fixture unit with a screen reader through orient,
lesson, practice, and sitting, and to visually accept the journey at 1280 and
375 widths against 17B-UI-SPEC section 1. An agent never self-certifies these.
On acceptance, flip G4 to `pass` and note the human reviewer and date on rows
G4 and G8; on refusal, record the exact gap as a D-06 defect and leave G4
`fail` with owner named.
  </action>
  <verify>Row G4 in 17B-GATES.md reads `pass` or `fail` with a human reviewer name and date, never `human-pending`.</verify>
</task>
</tasks>
<out_of_scope>New tokens or primitives, new dependencies, scorer or parser edits, real course content in-repo, the restore drill and egress checks (wave 4), repairing earlier phases beyond D-06's single-file bound, and writes under fixtures/ other than reading the chosen legacy artifacts.</out_of_scope>
<summary_obligations>Record in 17B-03-SUMMARY.md: the stage-by-stage evidence pointers, the rollup decision as answered, the legacy audit verdicts, the human checkpoint outcome with reviewer and date, and every D-06 defect with mechanism and owner.</summary_obligations>
