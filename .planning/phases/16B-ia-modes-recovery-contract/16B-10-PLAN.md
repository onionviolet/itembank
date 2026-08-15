---
phase: 16B-ia-modes-recovery-contract
plan: 10
type: execute
wave: 10
depends_on: ["16B-09"]
files_modified:
  - surfaces/ia.py
  - fixtures/course_storyboard_corpus.py
  - tests/ia_storyboard_tracer.py
autonomous: true
requirements: [FLOW-01, FLOW-02]
estimate:
  tokens: 96000
  raw_tokens: 96000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "All seven core loops are the product's end-to-end acceptance surface and each is resumable at an exact position with a next justified action: a synthetic run of each of loops A through G is interrupted mid-step and every one resumes at the step boundary it was interrupted at (FLOW-01 fixture)."
    - "A loop interrupted exactly at a step boundary resumes at that boundary with the following step as the next justified action, and each of loops A through G has an enumerated step list so the boundary is unambiguous (FLOW-01 adjacency edge)."
    - "A loop run over zero items, a discovery over an empty root or a practice with zero due items, completes with a stated empty outcome and a next justified action, and never with a blank state (FLOW-01 empty edge)."
    - "When two resumable loops tie on equal timestamps or equal attention, display order is stable and deterministic with course ID as the final tiebreak (FLOW-01 ordering edge)."
    - "At the exact moment the model backend becomes unavailable, reading, scoring, the authored hint ladder, evidence, and reports still run through the one runtime, proven by a synthetic reading, lesson, practice, and feedback walk with the backend disabled (FLOW-02 fixture)."
    - "A learner moves between direct source reading, lesson, practice, feedback, and the next course action without reconstructing context: each step of the walk is reached from the previous one through a link or a command the previous step named, and the resume position at every point is read from durable state rather than from a value the walk carried in memory."
    - "No loop introduces a second parser or scorer: the whole walk reaches verdicts only through runtime.score_response and parses only through model.load, asserted structurally over the tracer's own imports and over surfaces/ia.py."
    - "Reading is continuous and scrolls, and no reading surface paginates: no page reached during the walk carries a page-number control, a next-page link, or a rel=next relation."
  prohibitions:
    - statement: "A model must not write a score, an evidence event, or a mastery judgment; an advisory grader may propose a mark and the runtime settles it, and a walk with the model disabled must produce the same verdicts as a walk with it enabled."
      status: kept
      verification: flagged-unverified
    - statement: "A reading surface must not paginate; reading is continuous and scrolls, so a page-number control anywhere in the loop is a contract violation and not a layout preference."
      status: kept
      verification: flagged-unverified
    - statement: "A second parser or a second scorer must not appear in any loop; every verdict comes from the one scorer and every parse from the one parser, whatever surface the loop runs through."
      status: kept
      verification: flagged-unverified
    - statement: "A resume position must not be reconstructed from client-side memory or from a value the surface happened to be holding; it is recomputed from durable state on every visit, or a crash silently loses it."
      status: kept
      verification: flagged-unverified
    - statement: "An empty loop run must not render a blank state; a run over zero items states its outcome and names a next action, because a blank screen tells a learner nothing about whether anything happened."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "surfaces/ia.py gains LOOP_STEPS, LOOP_NEXT_ACTION, LOOP_EMPTY_OUTCOME, LOOP_ORDER, loop_resume_state, and resumable_loops"
    - "fixtures/course_storyboard_corpus.py gains build_loop_storyboard"
    - "tests/ia_storyboard_tracer.py with scenario_loop_a through scenario_loop_g, scenario_empty_loops, scenario_loop_ordering, scenario_model_disabled_walk, scenario_no_second_authority, and main"
  key_links:
    - "The seven step lists must be transcribed from 16B-UI-SPEC.md's Core Loop Resume Contract table, which already quotes synthesis section 3 verbatim, rather than re-derived from the synthesis document. Two transcriptions of one source drift, and the UI-SPEC's copy is the one the checker approved."
    - "The interruption scenarios must assert every step boundary of every loop, not one boundary per loop. A resume that works at boundary 3 and silently restarts at boundary 7 passes a spot check and fails a learner, and the whole point of an enumerated step list is that every boundary is nameable."
    - "The FLOW-02 walk must disable the model backend at the process level and then exercise the real shipped commands, not stubs. A walk against stubs proves the stubs degrade; the requirement is that the runtime does."
    - "loop_resume_state must take the completed step as an argument and read durable state for nothing else. If it started reading a course record it would become a second resume authority beside the route handlers that already compute resume cues from evidence and the journal."
---

<objective>
Prove the seven loops are one acceptance surface, and prove the core loop keeps
working when the model goes away.

`REQUIREMENTS.md` FLOW-01 makes the seven loops "the product's end-to-end
acceptance surface, each resumable with an exact position and a next justified
action", and its fixture is the 16B storyboard interrupting a synthetic run of
each of loops A through G mid-step. FLOW-02 requires a learner to move between
direct source reading, lesson, practice, feedback, and the next course action
without reconstructing context, with no loop introducing a second parser or
scorer, and its fixture disables the model backend entirely and asserts scoring,
the authored hint ladder, evidence, and reports still run.

The second fixture is the one that matters most and is the easiest to fake. A
walk against stubs proves the stubs degrade. This plan requires the walk to run
the real shipped commands with the backend genuinely unreachable, so what it
proves is that the runtime does not need the model.

Decisions already made, cited, and never re-derived here:

- **`16B-UI-SPEC.md` "Core Loop Resume Contract"**, the seven-row table, which
  already quotes synthesis section 3's step sequences verbatim and carries each
  loop's resume unit and next-action copy pattern. Task 1 transcribes from that
  table and from nowhere else.
- **`16B-UI-SPEC.md` route contract point 6**: the resume cue is server-computed
  from durable state, never guessed or cached client-side.
- **`16B-DECISIONS.md` `## D7`**: no percent anywhere, including in a next-action
  string.
- **`16B-DECISIONS.md` `## D-16B-10`**: the course-shelf ordering rule, whose
  final tiebreak on course ID this plan reuses for the resumable-loop list so
  one tiebreak rule exists and not two.
- **`PLANNING-DIRECTIVES.md` section 4**, non-negotiables 1 and 2: the runtime
  owns assessment authority, and there is exactly one parser, one scorer, one
  evidence store.
- **`.claude/CLAUDE.md`** Network constraint, quoted: the core loop must
  "degrade, never block", and "sitting a quiz, scoring, lessons, the authored
  hint ladder, evidence, and reports all work with the network unplugged".

Purpose: make the phase's two behavioral requirements executable rather than
asserted.
Output: seven enumerated loops, one storyboard tracer, and one model-disabled
walk against the real runtime.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@.claude/CLAUDE.md
@surfaces/ia.py
@runtime.py
@evidence.py
@fixtures/course_storyboard_corpus.py
@tests/hint_roundtrip.py
@tests/model_adapter_roundtrip.py
@tests/evidence_roundtrip.py
</context>

## Artifacts this phase produces (plan 16B-10 share)

New symbols introduced by this plan, and by nothing earlier:

- `surfaces/ia.py`: `LOOP_STEPS`, `LOOP_NEXT_ACTION`, `LOOP_EMPTY_OUTCOME`,
  `LOOP_ORDER`, `loop_resume_state`, `resumable_loops`.
- `fixtures/course_storyboard_corpus.py`: `build_loop_storyboard`.
- `tests/ia_storyboard_tracer.py` (whole file) and on it: `scenario_loop_a`,
  `scenario_loop_b`, `scenario_loop_c`, `scenario_loop_d`, `scenario_loop_e`,
  `scenario_loop_f`, `scenario_loop_g`, `scenario_empty_loops`,
  `scenario_loop_ordering`, `scenario_model_disabled_walk`,
  `scenario_no_second_authority`, and `main`.

The phase-wide symbol union is repeated in `16B-01-PLAN.md`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the seven enumerated loops and the resume function</name>
  <files>surfaces/ia.py, tests/ia_storyboard_tracer.py</files>
  <behavior>
    - `LOOP_STEPS` has exactly the seven keys `A` through `G`, each a dict with
      `title`, `steps`, and `resume_unit`.
    - `loop_resume_state("C", 0)` returns `next_step` equal to
      `LOOP_STEPS["C"]["steps"][0]` and `at_end` False.
    - `loop_resume_state("C", 3)` returns `next_step` equal to
      `LOOP_STEPS["C"]["steps"][3]`, `completed_step` 3, and `at_end` False.
    - `loop_resume_state("C", len(steps))` returns `next_step` None and `at_end`
      True.
    - `loop_resume_state("C", 2, item_count=0)` returns `empty` True and a
      non-empty `outcome` string, and still returns a non-empty `next_action`.
    - `loop_resume_state("Z", 0)` raises `ValueError` naming the unknown loop.
    - No `next_action` string produced for any loop at any boundary contains a
      percent character.
  </behavior>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the
  "Core Loop Resume Contract" section in full: the seven-row table's Steps
  column, Resume unit column, and Next-action copy pattern column, plus the
  binding rule paragraph beneath it. This table is the only source for the step
  text.
- `.planning/REQUIREMENTS.md`, `FLOW-01` in full, including its Fixture
  sentence.
- `surfaces/ia.py` in full as it stands after plan 16B-09, in particular
  `ATTENTION_ORDER` and the sort rule `D-16B-10` locked, which
  `resumable_loops` reuses.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md`,
  `## D-16B-10`.
  </read_first>
  <action>
1. Add `LOOP_STEPS` to `surfaces/ia.py`, a dict with exactly the seven keys
   `"A"` through `"G"`. Each value is a dict with:
   - `title`, the loop's name from the UI-SPEC table's first column, without
     the letter prefix. For example `"discover, reconcile, bind"` for A.
   - `steps`, a tuple of strings, one per arrow-separated step in that row's
     Steps column, transcribed verbatim from `16B-UI-SPEC.md` and from nowhere
     else. Do not paraphrase, reorder, merge, or split a step.
   - `resume_unit`, the string from that row's Resume unit column, verbatim.

   The expected step counts, taken from the UI-SPEC table when this plan was
   written, are A 9, B 9, C 9, D 8, E 6, F 9, G 9, for a total of 59. Assert the
   total in step 5. If your transcription yields a different count, do not
   adjust the table to match the number: record the per-loop counts you found
   and the total in `16B-10-SUMMARY.md` as a deviation, and update the asserted
   constant to your counted value with the deviation recorded beside it. The
   verbatim text is authoritative; the count is a check on the transcription.

2. Add `LOOP_NEXT_ACTION`, a dict over the same seven keys, each value a tuple
   of the next-action copy patterns from that row's final column, verbatim, in
   the order they appear. For example loop A's tuple is
   `("Continue discovery: {N} files not yet reviewed", "Resolve {N} conflicts before binding")`.
   Loop D's includes the two LOCKED reused strings `Resume practice` and
   `Start practice`, and loop E's includes the LOCKED reused string
   `Review evidence`; add a comment naming those three as reused LOCKED copy
   that is never re-worded.

3. Add `LOOP_EMPTY_OUTCOME`, a dict over the same seven keys, each a single
   sentence stating what an empty run of that loop produced. These are this
   plan's own copy, written to satisfy the FLOW-01 empty edge, and each names a
   real outcome rather than an absence:

   - A: `Nothing new was found in the roots you approved. Approve another root, or continue with what is already bound.`
   - B: `This course has no objectives yet, so there is nothing to give a treatment. Add or import objectives to continue.`
   - C: `There is nothing left to read in this course right now. Practice what you have read, or add a source.`
   - D: `Nothing is due for practice right now. Read something new, or practice ahead of schedule.`
   - E: `No evidence has been recorded for this course yet. Complete one activity and a snapshot becomes available.`
   - F: `Nothing is waiting for review. Draft a treatment, or continue reading.`
   - G: `Nothing is stale and nothing needs a decision. Export a backup, or continue where you left off.`

   Add a comment stating that none of the seven is a blank state and that this
   is the FLOW-01 empty edge made concrete.

4. Add `LOOP_ORDER = ("A", "B", "C", "D", "E", "F", "G")`, with a comment naming
   it as the stable primary key for `resumable_loops`.

5. Add `def loop_resume_state(loop, completed_step, item_count=None):` with a
   docstring stating: that it returns the loop's resume position as a plain
   dict; that it reads only its arguments and no durable record, because the
   route handlers already compute resume cues from evidence and the journal and
   a second resume authority would compete with them; and that a loop
   interrupted exactly at a step boundary resumes at that boundary with the
   following step as the next justified action.

   Behavior:
   - Raise `ValueError("unknown loop: %r" % loop)` for a key outside
     `LOOP_STEPS`.
   - Clamp `completed_step` into `range(0, len(steps) + 1)`.
   - `at_end` is `completed_step == len(steps)`.
   - `next_step` is `steps[completed_step]` when not at end, else `None`.
   - `empty` is `item_count == 0`; when `empty`, `outcome` is
     `LOOP_EMPTY_OUTCOME[loop]`, else the empty string.
   - `next_action` is `LOOP_NEXT_ACTION[loop][0]` normally, and stays non-empty
     even when `empty` is True or `at_end` is True, because a completed or empty
     loop still owes a next action.
   - Return
     `{"loop", "title", "completed_step", "next_step", "resume_unit", "at_end",
     "empty", "outcome", "next_action"}`.

6. Add `def resumable_loops(entries):` taking a list of dicts each carrying
   `loop`, `course_id`, and `last_activity`, and returning them sorted by the
   `LOOP_ORDER` index of `loop`, then by `last_activity` descending with `None`
   last, then by `course_id` ascending. Its docstring states that the course-ID
   final tiebreak is the same rule `D-16B-10` locked for the course shelf, so one
   tiebreak rule exists and not two.

7. Create `tests/ia_storyboard_tracer.py` following the shipped
   direct-execution convention with its own local `fail(msg)`. Add
   `scenario_loop_a` through `scenario_loop_g`, one per loop, each asserting:
   - For every boundary `i` in `range(len(steps) + 1)`,
     `loop_resume_state(loop, i)` returns `completed_step` `i`, and returns
     `next_step` equal to `steps[i]` for `i < len(steps)` and `None` at
     `i == len(steps)`.
   - `at_end` is True only at the final boundary.
   - `resume_unit` is the exact string from `LOOP_STEPS`.
   - Every `next_action` is non-empty and contains no percent character.
   - The loop's step tuple contains no duplicate string and no empty string.

   Add `main()` printing `"STORYBOARD: 7 passed, 0 skipped, 0 failed"`, guarded
   by `if __name__ == "__main__": sys.exit(main())`.

8. Run:

```
python tests/ia_storyboard_tracer.py
python -c "import sys; sys.path.insert(0,'.'); from surfaces import ia; print(sorted(ia.LOOP_STEPS)); print([len(ia.LOOP_STEPS[k]['steps']) for k in 'ABCDEFG']); print(sum(len(ia.LOOP_STEPS[k]['steps']) for k in 'ABCDEFG'))"
```

   Expected: exit 0; then `['A', 'B', 'C', 'D', 'E', 'F', 'G']`; then
   `[9, 9, 9, 8, 6, 9, 9]`; then `59`. A different second or third line is a
   recorded deviation, not a silent adjustment.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_storyboard_tracer.py</automated>
Expected: final line `STORYBOARD: 7 passed, 0 skipped, 0 failed`, exit 0. The
degraded states this task proves are the end boundary, where `next_step` is
`None` and `next_action` is still non-empty, and the unknown-loop input, which
raises rather than returning a plausible-looking empty result.
  </verify>
  <acceptance_criteria>
- `python tests/ia_storyboard_tracer.py` exits 0 with final line
  `STORYBOARD: 7 passed, 0 skipped, 0 failed`.
- `sorted(ia.LOOP_STEPS)` is `['A', 'B', 'C', 'D', 'E', 'F', 'G']`.
- The per-loop step counts are `[9, 9, 9, 8, 6, 9, 9]` and the total is `59`, or
  the counted values are recorded as a deviation in the summary with the
  asserted constant updated to match the transcription.
- Every one of the 59 step strings appears verbatim in
  `16B-UI-SPEC.md`'s Core Loop Resume Contract table, spot-asserted for loops A
  and G by a substring search over that file's text.
- `loop_resume_state("C", len(steps))` returns `next_step` None, `at_end` True,
  and a non-empty `next_action`.
- `loop_resume_state("D", 2, item_count=0)` returns `empty` True and `outcome`
  equal to `LOOP_EMPTY_OUTCOME["D"]`.
- `loop_resume_state("Z", 0)` raises `ValueError` naming `Z`.
- No `next_action` for any loop at any boundary contains `%`.
- `inspect.getsource(ia.loop_resume_state)` contains no `open(` call and no
  `import` statement.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">The seven step lists become the acceptance
  surface later phases assert against and the vocabulary 16C's strategy work
  reads. They are transcribed from an approved contract rather than authored, so
  the cost of a change is a re-transcription and not a
  renegotiation.</reversibility>
  <done>Seven loops have enumerated steps, every boundary resumes at the
  following step, an empty run says what happened, and no next action carries a
  percent.</done>
</task>

<task type="auto">
  <name>Task 2: the interruption storyboard, the empty runs, and the tie ordering</name>
  <files>fixtures/course_storyboard_corpus.py, tests/ia_storyboard_tracer.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md`, `FLOW-01`'s Fixture sentence verbatim, and the
  ROADMAP Phase 16B freeze-gate paragraph's FLOW-01 clause.
- `fixtures/course_storyboard_corpus.py` in full as it stands after plan
  16B-04, in particular `FICTIONAL_COURSES` and `FakeCourseModule`.
- `surfaces/ia.py`, `loop_resume_state`, `resumable_loops`, `write_ia_state`,
  and `read_ia_state`.
- `tests/ia_storyboard_tracer.py` as it stands after Task 1.
  </read_first>
  <action>
1. Add `build_loop_storyboard(dest_dir)` to
   `fixtures/course_storyboard_corpus.py`. It writes, for each of the seven
   loops, one durable position record under
   `<dest_dir>/_ia/loop_<letter>.json` using the same atomic write shape
   `ia.write_ia_state` uses, each holding
   `{"loop": <letter>, "completed_step": <a fixed per-loop value>,
   "course_id": "crs-kestrel-01", "last_activity": "2026-03-02T09:00:00Z"}`.
   Use the fixed `completed_step` values A 4, B 2, C 6, D 3, E 1, F 7, G 5, so
   every interruption is mid-loop and none is at a boundary another loop also
   uses. It returns a dict mapping loop letter to the written path. It writes no
   `.md` file and calls no clock and no random source.

2. Extend `scenario_loop_a` through `scenario_loop_g` in
   `tests/ia_storyboard_tracer.py` with the durable half of the interruption,
   which is what the FLOW-01 fixture actually asks for:

   - Build the storyboard into a temp directory.
   - For the loop under test, read its record back off disk, call
     `loop_resume_state(loop, record["completed_step"])`, and assert the
     returned `next_step` equals `LOOP_STEPS[loop]["steps"][record["completed_step"]]`.
   - Simulate the interruption as an unclean loss: delete every in-memory
     reference, re-read the file from disk in a fresh dict, and assert the
     recomputed resume state is identical to the first, field for field. This is
     the "recomputes the resume unit from durable state, never from client-side
     memory alone" rule made executable.
   - Assert the record file contains no percent character and no absolute path.

3. Add `scenario_empty_loops()`. For each of the seven loops it calls
   `loop_resume_state(loop, 0, item_count=0)` and asserts: `empty` True;
   `outcome` equals `LOOP_EMPTY_OUTCOME[loop]` and is a non-empty sentence
   ending in a period; `next_action` is non-empty; and the outcome string
   contains none of the words `nothing to show`, `no data`, or `empty`, so the
   copy states an outcome rather than an absence. Assert also that no outcome
   string is shared between two loops.

4. Add `scenario_loop_ordering()`. It builds a list of six entries covering the
   three tie cases and asserts `resumable_loops` returns one stable order across
   ten shuffles seeded by `random.Random(20260815)`:
   - Two entries with the same loop letter, the same `last_activity`, and
     different `course_id` values, ordered by course ID ascending.
   - Two entries with the same loop letter and different timestamps, ordered
     newest first.
   - Two entries with different loop letters and identical everything else,
     ordered by `LOOP_ORDER` index.
   Assert the returned sequence of `(loop, course_id)` pairs is byte-identical
   across all ten shuffles, and assert the final tiebreak is course ID by
   checking the two same-loop same-timestamp entries appear in course-ID order.

5. Update `main()` to run nine scenarios and print
   `"STORYBOARD: 9 passed, 0 skipped, 0 failed"`. Run:

```
python tests/ia_storyboard_tracer.py
python itembank.py guard .
```

   Expected: `STORYBOARD: 9 passed, 0 skipped, 0 failed` and exit 0, then
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_storyboard_tracer.py</automated>
Expected: final line `STORYBOARD: 9 passed, 0 skipped, 0 failed`, exit 0. The
degraded state this task proves is the interruption itself: every loop's resume
state is recomputed from a file read off disk after every in-memory reference is
dropped, and it matches the state computed before the loss field for field.
  </verify>
  <acceptance_criteria>
- `python tests/ia_storyboard_tracer.py` exits 0 with final line
  `STORYBOARD: 9 passed, 0 skipped, 0 failed`.
- All seven loop scenarios assert every step boundary and the durable
  interruption round trip.
- Each loop's storyboard record file exists at
  `<tmp>/_ia/loop_<letter>.json` and contains no percent character and no
  absolute path.
- All seven `LOOP_EMPTY_OUTCOME` values are distinct, end in a period, and
  contain none of `nothing to show`, `no data`, `empty`.
- `resumable_loops` returns one byte-identical sequence across ten seeded
  shuffles, and the two same-loop same-timestamp entries appear in course-ID
  order.
- `build_loop_storyboard` writes no `.md` file and calls no clock or random
  source.
- `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A fixture builder and test scenarios.
  </reversibility>
  <done>Seven loops are interrupted mid-step, every one resumes at the exact
  boundary from a file rather than from memory, an empty run says what happened,
  and a tie orders the same way every time.</done>
</task>

<task type="auto">
  <name>Task 3: the FLOW-02 walk with the model backend genuinely disabled</name>
  <files>tests/ia_storyboard_tracer.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md`, `FLOW-02` in full, including its Fixture
  sentence: "a 16B storyboard scenario walking a synthetic reading, lesson,
  practice, and feedback path with the model backend disabled, asserting
  scoring, the authored hint ladder, evidence, and reports still run through the
  one runtime".
- `.claude/CLAUDE.md`, the Network constraint paragraph in full.
- `tests/hint_roundtrip.py` in full, and `tests/model_adapter_roundtrip.py` in
  full. Step 1 below reads both to find the mechanism the repository already
  uses to run with no backend; do not invent a second mechanism if one exists.
- `runtime.py`, `score_response`, `canonical_response`, and `public_item`, the
  one scorer every surface reaches.
- `evidence.py`, `append_event` and `mark_event`, and the human-only marker gate.
- `fixtures/sample_bank.md` and `fixtures/lesson_bank.md`, the two shipped
  synthetic banks this walk uses.
  </read_first>
  <action>
1. Determine how to disable the backend, using one of exactly two specified
   branches, and record which one ran:

   - **Branch one**, preferred: read `tests/hint_roundtrip.py` and
     `tests/model_adapter_roundtrip.py` and find the mechanism they already use
     to run with no backend, whether that is a settings value, an environment
     variable, or a constructor argument. Reuse it verbatim.
   - **Branch two**, only if branch one finds no such mechanism: write an
     `itembank.json` into the walk's temp directory setting `model_backend` to
     an unroutable loopback endpoint, `127.0.0.1` port `9`, so every model call
     fails fast with a connection refusal rather than hanging, and additionally
     clear `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY` from the child
     environment.

   Record in `16B-10-SUMMARY.md` which branch ran and, for branch one, the exact
   mechanism reused.

2. Add `scenario_model_disabled_walk()` to `tests/ia_storyboard_tracer.py`. It
   runs the whole walk as real subprocess commands against a temp directory
   holding copies of `fixtures/sample_bank.md` and `fixtures/lesson_bank.md`,
   with the backend disabled per step 1, and asserts each stage in order:

   - **Reading.** `python itembank.py lesson <lesson bank>` exits 0 and prints
     lesson prose. Assert its output contains none of `Next page`,
     `Previous page`, `page=`, so reading is continuous.
   - **Lesson to practice without reconstructing context.**
     `python itembank.py start <sample bank> --out <session>` exits 0 and writes
     a session file; assert the session file's `bank` field names the bank the
     previous stage read from, so the next stage was reached from the previous
     one rather than by the test supplying context by hand.
   - **Practice.** `python itembank.py next --session <session>` exits 0 and
     returns an item with no `correct` key and no answer key field, which is
     `runtime.public_item`'s split holding with the model absent.
   - **Feedback and scoring.** `python itembank.py submit --session <session>
     --answer <a deliberately wrong option letter>` exits 0 and records a
     verdict. Assert the recorded verdict equals
     `runtime.score_response(<that item>, <that answer>)` computed in process, so
     the served verdict and the one scorer agree exactly.
   - **The authored hint ladder.** `python itembank.py teach` for the first
     authored tier exits 0 and returns authored tier text, and does not error on
     the missing backend. Assert its output contains the authored tier content
     from the bank and contains no phrase implying a generated answer.
   - **Evidence.** `python itembank.py evidence <the evidence root>` exits 0 and
     its output includes the response just recorded.
   - **Report.** `python itembank.py report --session <session>` exits 0 and its
     output separates settled from pending rather than reporting a single
     number; assert its output contains no percent character.
   - **The next course action.** `GET /` on a daemon over the same directory
     returns 200 and its resume cue names the same bank or course the walk was
     in, so the loop closes without the learner reconstructing context.

   Every stage asserts an exit code and a concrete string. A stage that cannot
   be run in this environment is marked `SKIPPED` in the scenario's own counter
   with one sentence naming what could not be exercised, and the tracer's
   summary line reports the skip rather than counting it as a pass.

3. Add `scenario_no_second_authority()`. It asserts structurally:
   - `tests/ia_storyboard_tracer.py`'s own source reaches verdicts only through
     `runtime.score_response`, asserted by finding no other function call whose
     name contains `score`.
   - `surfaces/ia.py`'s comment-stripped source contains no `import runtime`,
     no `score`, no `parse_bank`, and no `mark_event`.
   - `evidence.mark_event` still refuses a non-human marker, asserted by calling
     it with `marker='model'` and requiring a `ValueError`, the same shipped
     gate 16A-01 asserted.
   - `runtime.public_item` on an item from the walk's bank returns a dict with
     no `correct` key.

4. Update `main()` to run eleven scenarios and print
   `"STORYBOARD: 11 passed, 0 skipped, 0 failed"`, adjusting the skipped count
   honestly when any stage in step 2 was marked `SKIPPED`. Run the full suite
   and the guard:

```
python tests/ia_storyboard_tracer.py
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
```

   Expected: `STORYBOARD: 11 passed, 0 skipped, 0 failed` and exit 0; exit 0;
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_storyboard_tracer.py</automated>
Expected: final line `STORYBOARD: 11 passed, 0 skipped, 0 failed`, exit 0, or a
final line whose skipped count matches the number of stages honestly marked
`SKIPPED`. The degraded state this task proves is the whole point of FLOW-02:
with the model backend unreachable, reading, scoring, the authored hint ladder,
evidence, and reports all still run through the one runtime, and every verdict
equals the one scorer's own answer.
  </verify>
  <acceptance_criteria>
- `python tests/ia_storyboard_tracer.py` exits 0 and its final line reports
  eleven scenarios with a skipped count matching the stages actually skipped.
- The walk ran with the backend disabled through one of the two specified
  branches, and the summary records which and how.
- Every one of the eight walk stages asserts an exit code and a concrete string,
  or is marked `SKIPPED` with a naming sentence.
- The recorded submit verdict equals `runtime.score_response` computed in
  process for the same item and answer.
- The `next` item payload carries no `correct` key.
- The lesson output and the report output contain none of `Next page`,
  `Previous page`, `page=`, and the report output contains no `%`.
- `evidence.mark_event(..., marker='model')` raises `ValueError`.
- `surfaces/ia.py`'s comment-stripped source contains no `import runtime`, no
  `score`, no `parse_bank`, and no `mark_event`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0 and
  `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Test coverage only.</reversibility>
  <done>A learner can read, practise, be scored, get the authored hint ladder,
  see evidence, and get a report with the model unreachable, and the served
  verdict is the one scorer's own answer.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| model backend to assessment verdict | A tutoring model sits beside the scoring path and must never enter it. |
| durable resume record to resumed position | A record read after a crash decides where a learner lands. |
| tracer assertions to shipped behavior | A tracer that exercises stubs proves nothing about the runtime. |
| loop step text to acceptance surface | Later phases assert against these strings. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-10-01 | Elevation of Privilege | a model writing a score, an evidence event, or a mastery judgment | critical | mitigate | `scenario_no_second_authority` asserts `evidence.mark_event` still raises on a non-human marker and that `surfaces/ia.py` contains no scoring, parsing, or evidence-writing name; the walk asserts the served verdict equals `runtime.score_response`'s own answer for the same item and answer. |
| T-16B-10-02 | Repudiation | a tracer that proves stubs degrade rather than that the runtime does | high | mitigate | Every stage of the walk runs a real shipped subprocess command against real shipped fixtures with the backend genuinely disabled through one of two specified branches; a stage that cannot be run is marked `SKIPPED` with a naming sentence and is reported in the summary line rather than counted as a pass. |
| T-16B-10-03 | Denial of Service | a disabled backend hanging the walk instead of failing fast | medium | mitigate | Branch two points the backend at an unroutable loopback port so every call is refused rather than timing out, and clears the proxy environment so no proxy absorbs the request. |
| T-16B-10-04 | Tampering | a resume position reconstructed from memory rather than from disk | high | mitigate | Each loop scenario drops every in-memory reference, re-reads the record from disk into a fresh dict, and asserts the recomputed state matches field for field. |
| T-16B-10-05 | Information Disclosure | an absolute path or an invented percentage inside a storyboard record | medium | mitigate | Each record file is asserted to contain no percent character and no absolute path, and no `next_action` string for any loop at any boundary may contain a percent. |
| T-16B-10-06 | Repudiation | a step list paraphrased rather than transcribed, drifting from the approved contract | medium | mitigate | The step text is transcribed from `16B-UI-SPEC.md`'s table and spot-asserted by substring search over that file for loops A and G; a differing step count is recorded as a deviation rather than silently adjusted. |
| T-16B-10-07 | Information Disclosure | real course or learner material entering the repository through the storyboard fixture | high | mitigate | `build_loop_storyboard` writes only JSON position records with fictional course ids and no `.md` file, and `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion. |
| T-16B-10-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every new file is standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- **No real execution of loops A, B, E, F, or G.** Those loops read and write
  objects that live in Phase 14A, 14B, 15A, and 15B modules. This plan proves
  their **resume contract**, which is 16B's obligation, against enumerated steps
  and durable position records. Executing their real work is those phases'.
- No second resume authority. `loop_resume_state` reads only its arguments; the
  route handlers keep computing resume cues from evidence and the journal.
- No change to `runtime.py`, `evidence.py`, or `model.py`. The walk exercises
  them and modifies none.
- No model call of any kind. The whole point of the FLOW-02 scenario is that
  none is needed.
- No new route, no new CLI command, no new settings key.
- No new visual constant and no CSS rule.
- No softened assertion to make a stage pass. A stage that cannot be exercised
  is `SKIPPED` with a naming sentence and the freeze decision in plan 16B-11
  weighs it.
</out_of_scope>

<flagged_assumptions>
- **The seven step counts `[9, 9, 9, 8, 6, 9, 9]` were counted from
  `16B-UI-SPEC.md`'s table when this plan was written.** Task 1 step 1 requires
  the verbatim text to win over the count and requires a differing count to be
  recorded as a deviation rather than resolved by editing the steps.

- **`LOOP_EMPTY_OUTCOME`'s seven sentences are this plan's own copy.** The
  FLOW-01 empty edge requires a stated outcome and a next action; no upstream
  artifact supplies the wording. They are display text with no behavior behind
  them and a reviewer may reword any of them, which changes one constant and one
  assertion.

- **Which backend-disabling branch runs is unknown at plan time.** Task 3 step 1
  specifies both completely and requires the summary to record which ran and
  how, so the executor runs a specified branch rather than choosing one.

- **Loops A, B, E, F, and G are proven at the resume-contract level only.** The
  seven scenarios assert every step boundary and the durable interruption round
  trip; they do not execute those loops' real work, which does not exist in this
  phase. The 16B freeze record states that boundary explicitly rather than
  implying the loops themselves were exercised.
</flagged_assumptions>

<summary_obligations>
`16B-10-SUMMARY.md` records: the final line of every verify command; the counted
per-loop step counts and the total, beside the planned `[9, 9, 9, 8, 6, 9, 9]`
and `59`, with any difference named as a deviation; which backend-disabling
branch Task 3 step 1 ran and the exact mechanism; every walk stage's exit code
and the concrete string it asserted, or the naming sentence for any stage marked
`SKIPPED`; the recorded submit verdict beside `runtime.score_response`'s own
answer for the same input; confirmation that `evidence.mark_event` still raised
on a model marker; the ten-shuffle ordering sequence proving stability; which
truth was verified by which command with its actual stdout; and any deviation
from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-10-SUMMARY.md`
when done.
</output>
