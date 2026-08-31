---
phase: 16D-paced-lesson
plan: 02
type: execute
wave: 2
depends_on: ["16D-01"]
files_modified:
  - runtime.py
  - blueprint.py
  - schemas/response.schema.json
  - schemas/lesson_run.schema.json
  - tests/lesson_run_roundtrip.py
autonomous: true
requirements: ["16D-CONTEXT D-16D-3, D-16D-4", IL-20260826-10]
must_haves:
  truths:
    - "A checkpoint attempt in a paced run is an ordinary attempt in the one evidence store, scored by the one scorer, carrying context lesson_run."
    - "Every response event written before this plan still validates against the updated schema (additivity proven against a pre-change baseline, the 16C precedent)."
    - "The AGENT-03 evidence proposal's denominator excludes lesson_run attempts by default, as a read-time filter on the label."
    - "The tier ladder is released by the runtime keyed to attempt count and explicit request; exam and diagnostic modes are byte-identical to before."
  artifacts:
    - "schemas/lesson_run.schema.json, published and self-checking under schema_validate.py --all."
    - "tests/lesson_run_roundtrip.py covering the session lifecycle, the label, the exclusion, and all three tiers."
  key_links:
    - "The lesson-run session records step ids from model.lesson_steps (16D-01), so resume and the 16D-03 view read one identity."
    - "multi scoring stays all-or-nothing; tier 1 annotates the learner's selections, it never changes the verdict."
---
<objective>
Land the evidence and disclosure half of the paced treatment: the
lesson-run session kind, the additive context label, the default
denominator exclusion, and the three-tier wrong-checkpoint disclosure.
Implements 16D-CONTEXT D-16D-3 and D-16D-4 (transcribing D-PACED-2 and
D-PACED-3); the executor never re-litigates them.
</objective>
<context>
@.planning/phases/16D-paced-lesson/16D-CONTEXT.md
@.planning/DECISIONS-PACED-LESSON-2026-08-28.md (D-PACED-2, D-PACED-3)
@runtime.py (FEEDBACK_POLICIES at line 1845 and the submit path that consumes it near line 2160; write_session at 1430; explain_payload at 1727)
@schemas/response.schema.json (the context enum near line 181)
@blueprint.py (the AGENT-03 evidence proposal section from line 983)
</context>
<tasks>
<task type="auto">
  <name>Task 1: The lesson-run session object</name>
  <files>runtime.py, schemas/lesson_run.schema.json</files>
  <read_first>runtime.py write_session (line 1430) and session_path (1379) for the atomic-write and naming conventions; an existing schemas/*.json header for the house schema style</read_first>
  <action>
  1. Add `runtime.start_lesson_run(bank_path, out_path, steps)` creating a JSON document `{"kind": "lesson_run", "bank": <abspath>, "created": <iso8601>, "step": <first step id>, "steps": [<ids in order>], "attempts": []}` written through the same tmp-then-`os.replace` shape write_session uses (one atomic-write idiom, not two). Add `runtime.lesson_run_advance(path, step_id)` which refuses (returning a `{"error": "lesson_run.unknown_step"}` dict, never raising) when the id is not in `steps`, else records it. Add `runtime.lesson_run_record(path, item_id, attempt_summary)` appending to `attempts`.
  2. A lesson run is never a sitting: it carries no blueprint, no form, no cursor over selected items, and its file name starts `lessonrun_` in the same `_attempts/` directory. Position is presentation state; nothing in this document may be read as coverage, mastery, or progress, and the schema description says so in those words.
  3. Publish `schemas/lesson_run.schema.json` for this document: additionalProperties false, every key above required, `attempts` items referencing the summary shape you store (item id, correct or held state, attempt ordinal, tier released). Register nothing else; `schema_validate.py --all schemas` must pass.
  </action>
  <verify>`python schema_validate.py --all schemas` exits 0; the Task 4 roundtrip creates, advances, refuses an unknown step, and validates the file against the schema.</verify>
</task>
<task type="auto">
  <name>Task 2: The additive context label and the denominator exclusion</name>
  <files>runtime.py, schemas/response.schema.json, blueprint.py</files>
  <read_first>schemas/response.schema.json context enum (line 181); the evidence.response_event call sites that pass context (grep "lesson_gate" across runtime.py, evidence.py, surfaces/); blueprint.py from line 983, the function that counts attempts into the AGENT-03 proposal denominator</read_first>
  <action>
  1. Extend the response schema's `context` enum to `["quiz", "lesson_gate", "lesson_run"]` and extend its description with one sentence: "\"lesson_run\" marks a checkpoint attempt inside a paced lesson run (plan 16D-02, D-PACED-2); blueprint denominators exclude it by default." Change nothing else in the schema.
  2. Thread the value: whichever function the gate-band check path calls to build its response event gains the ability to carry context "lesson_run" when the caller says the attempt happened inside a lesson run; the default stays exactly what each existing call site passes today, so every pre-16D call site emits byte-identical events.
  3. In blueprint.py's AGENT-03 proposal counting, filter response events to `context != "lesson_run"` before the denominator is formed, with a comment citing D-PACED-2 and stating the reconsideration condition: a blueprint that wants checkpoint evidence changes this policy with a query, never a migration. Do NOT change the handling of "quiz" or "lesson_gate", and do not touch Phase 10's scheduler, which deliberately treats contexts identically for review queueing.
  4. Additivity proof, the 16C precedent: before editing the schema, copy `fixtures/lesson_retention_events.jsonl` (and any other committed response-event fixture the repo carries; find them with `grep -rl response fixtures/*.jsonl`) to a temp dir; after editing, validate those pre-change baselines against the updated schema with `python schema_validate.py schemas/response.schema.json --jsonl <copy>` filtered to response events, asserting exit 0.
  </action>
  <verify>The pre-change baseline validates against the post-change schema; a synthetic lesson_run event validates; a context value outside the enum still fails; the Task 4 test asserts the proposal denominator with and without lesson_run events differs by exactly the excluded count.</verify>
</task>
<task type="auto">
  <name>Task 3: The tier ladder, inside the runtime's disclosure authority</name>
  <files>runtime.py</files>
  <read_first>runtime.py FEEDBACK_POLICIES (1845) and the wrong-answer hold path near 2160; _selection_display; explain_payload (1727) for what tier 3 may reuse; the DA: rationale fields on parsed items (model.py grab of DA lines)</read_first>
  <action>
  1. Add one policy entry: `"paced": {"wrong": "hold", "right": "advance", "selection": "own_picks"}` with a comment citing D-PACED-3 and stating that this mode is reachable only through a lesson-run checkpoint, never through a sitting's mode enum.
  2. Add `runtime.checkpoint_feedback(q, answer, wrong_attempts, reveal_requested)` returning the runtime-settled disclosure for a paced checkpoint:
     - always: the verdict from `score_response` (the one scorer; call it, never re-derive);
     - tier 1 (wrong_attempts >= 1): for each option the learner selected, `{"option": key, "state": "right" | "not_right"}`; NEVER an unselected correct option, and for non-selection types (short, build, table, dnd) tier 1 degrades to the held state with no per-part reveal, stated in the docstring as the D-PACED-3 reconsideration seam;
     - tier 2 (with tier 1): the authored DA rationale for exactly the options the learner touched, keyed by option;
     - tier 3 (wrong_attempts >= 2 or reveal_requested true): the full explain_payload;
     - the returned dict always carries `"tier"` (0, 1, or 3; tier 2 rides with 1) so the surface renders what it is handed and decides nothing.
  3. Guard the authority boundary: checkpoint_feedback asserts it is being used for a teaching context by refusing (structured error, not an exception) when handed a session mode of "diagnostic" or "exam"; those paths remain byte-identical, proven by the existing suite.
  </action>
  <verify>Task 4 covers all tiers; `python tests/model_gate_roundtrip.py` and `python tests/selection_roundtrip.py` (exam/diagnostic behavior) still exit 0 unchanged.</verify>
</task>
<task type="auto">
  <name>Task 4: The roundtrip</name>
  <files>tests/lesson_run_roundtrip.py</files>
  <read_first>tests/lesson_roundtrip.py main() for the house style; fixtures/paced_lesson_bank.md from 16D-01</read_first>
  <action>Write the stdlib-only roundtrip asserting, against fixtures/paced_lesson_bank.md in a temp dir: session lifecycle (create, advance, unknown-step refusal, schema-valid file); a checkpoint attempt scored through score_response producing a response event with context lesson_run that validates; the pre-change baseline still validating (Task 2.4); the AGENT-03 denominator excluding exactly the lesson_run events; tier 1 marking only the learner's selections on a wrong multi answer with one right and one wrong pick; tier 2 carrying DA for touched options only; tier 3 on the second wrong attempt and on explicit request after the first; the exam refusal; and `multi` scoring still all-or-nothing (a partially right selection scores wrong at every tier). The test writes only under tempfile.mkdtemp().</action>
  <verify>`python tests/lesson_run_roundtrip.py` exits 0; `python schema_validate.py --all schemas` exits 0; `python itembank.py guard .` exits 0; full-suite spot legs named in Tasks 2 and 3 stay green.</verify>
</task>
</tasks>
<out_of_scope>Rendering and routes (16D-03); any change to multi scoring, partial credit, exam or diagnostic disclosure, Phase 10 scheduling, or the hint-tier machinery; deleting or renaming the existing lesson_gate context; any second evidence store or session store.</out_of_scope>
<summary_obligations>Record in 16D-02-SUMMARY.md: the exact schema diff, the baseline files used for the additivity proof and their validation results, the denominator counts with and without exclusion, and every verify command with exit state.</summary_obligations>
