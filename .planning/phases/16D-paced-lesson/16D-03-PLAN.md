---
phase: 16D-paced-lesson
plan: 03
type: execute
wave: 3
depends_on: ["16D-01", "16D-02"]
files_modified:
  - surfaces/lesson.py
  - surfaces/daemon.py
  - tests/paced_view_roundtrip.py
autonomous: true
requirements: ["16D-CONTEXT D-16D-5, D-16D-6, D-16D-7", "16D-UI-SPEC (whole file)"]
must_haves:
  truths:
    - "GET /lesson/<stem> with no view query renders byte-identically to before this plan."
    - "The paced view shows one step of already-rendered blocks, a jump-only TOC, and a pager that gates forward only on an unattempted declared gate, with the exact no-disabled-button sentence."
    - "Resume lands on the recorded step id, and a deleted step id falls back to step 1 with the exact status line, never a guessed neighbour."
    - "Offline and static builds degrade to the continuous document with the exact one-line notice; a runtime-unreachable band never gates."
  artifacts:
    - "tests/paced_view_roundtrip.py driving the served route end to end."
  key_links:
    - "The checkpoint band is the shipped Phase 6.2 gate band; this plan changes its embedding and its POST's session and context wiring, never its structure or copy."
    - "Tier rendering consumes runtime.checkpoint_feedback's payload verbatim; the surface renders what it is handed and decides nothing (the runtime invariant)."
---
<objective>
Land the paced view: the projection, navigation, resume, and checkpoint
embedding, per 16D-UI-SPEC. Implements D-16D-5 through D-16D-7. Every
learner-visible string is in the UI spec or this plan; the executor invents
none.
</objective>
<context>
@.planning/phases/16D-paced-lesson/16D-UI-SPEC.md
@.planning/phases/16D-paced-lesson/16D-CONTEXT.md
@surfaces/lesson.py (lesson_page from line 2167, guided_stages at 2067, _gate_band_html at 1123, _reader_nav_html at 877)
@surfaces/daemon.py (LESSON_GET_RE at 124, LESSON_CHECK_RE and LESSON_SKIP_RE at 190)
</context>
<tasks>
<task type="auto">
  <name>Task 1: mode="paced" in the one renderer</name>
  <files>surfaces/lesson.py</files>
  <read_first>lesson_page whole docstring and its mode branch near line 2352; guided_stages for the group-never-re-render rule</read_first>
  <action>
  1. Extend lesson_page's accepted modes to ("continuous", "guided", "paced") and its docstring with one paragraph citing D-16A-9's precedent and D-16D-7. Paced mode takes two new keyword arguments, `step_id=None` and `run=None` (the lesson-run session dict or None), both defaulting so no existing caller changes.
  2. Resolve steps with `model.lesson_steps(lesson)`. Group the already-rendered blocks into steps exactly the way guided mode groups stages: cut the rendered stream at step boundaries, never re-render a block (byte-identical containers, the guided rule).
  3. Render per 16D-UI-SPEC: the step header line "Step {n} of {total}: {title}"; the Steps details TOC with "(seen)" suffixes read from `run["attempts"]` and visited steps; the pager with "Back" and "Continue"; on a declared unattempted gate, the exact sentence "Attempt the checkpoint above to continue, or use the Steps list to jump ahead." with a live Steps link and no disabled control. Unknown step_id renders step 1 plus the polite status line "That step is not in this lesson any more. Showing the first step." Resume adds "Resuming at step {n}." when the caller says so. Step changes announce "Step {n} of {total}." through the existing role=status region, once.
  4. When the lesson carries any checkpoint at all, every step header's Ledger line carries either the step's checkpoint state or the exact sentence "This step records nothing."
  5. Tier rendering: when the POST handler passes a checkpoint_feedback payload, render tier 1 as text chips "right" / "not right" beside the learner's selected options only, tier 2 under the heading "About what you picked", tier 3 through the existing reveal rendering. Never color alone; no JavaScript required.
  6. Static and offline callers (the build path) render the continuous document with the notice "Paced view needs a served session. This is the whole lesson." exactly once at the top.
  </action>
  <verify>Task 3 drives every branch over HTTP; `python tests/lesson_roundtrip.py` and `python tests/gate_roundtrip.py` still exit 0 (byte-identity of continuous and guided modes and of the band).</verify>
</task>
<task type="auto">
  <name>Task 2: Routes and session wiring</name>
  <files>surfaces/daemon.py</files>
  <read_first>the LESSON_GET_RE handler and the LESSON_CHECK_RE/LESSON_SKIP_RE POST handlers, whole functions; how they locate the bank and build ctx</read_first>
  <action>
  1. The existing GET handler reads `view=paced` and `step=<id>` from the query. On first paced GET for a lesson with no live lesson-run session, call runtime.start_lesson_run; on later GETs resume from the newest lessonrun_ file for that bank stem. Pass run and step_id into lesson_page. No new route.
  2. The existing check POST, when the referring view is paced (a hidden `view=paced` form field the band emits in paced mode only), records the attempt into the lesson-run session (runtime.lesson_run_record), emits the response event with context "lesson_run", computes runtime.checkpoint_feedback with the run's per-item wrong-attempt count, and re-renders the paced step held with the tier payload. The non-paced check path is byte-identical to before.
  3. The skip POST in paced mode records a skip into the run (an attempt-shaped entry with state "skipped") so the gate opens (gate on attempted; a skip is the ordinary control the 6.2 spec already made it) and re-renders.
  4. When the runtime cannot record (write failure), render the band's shipped 12.1 degrade line and an ungated Continue; a gate that cannot be satisfied must not hold (16D-UI-SPEC states row).
  </action>
  <verify>Task 3; plus `python tests/daemon_roundtrip.py` still exits 0.</verify>
</task>
<task type="auto">
  <name>Task 3: The served roundtrip</name>
  <files>tests/paced_view_roundtrip.py</files>
  <read_first>tests/visual_accessibility_roundtrip.py check_served_page for the serve-and-fetch harness shape</read_first>
  <action>Drive a served daemon over fixtures/paced_lesson_bank.md in a temp dir and assert: the plain lesson GET is byte-identical to a pre-plan capture taken by the test itself with mode features unused; paced GET shows step 1 of 4 with the TOC listing all four; a forward TOC jump past the unattempted gate works; the gate step shows the exact gating sentence and no disabled control; a wrong checkpoint POST holds with tier 1 chips on selected options only and no unselected correct option text anywhere in the page bytes; a second wrong POST reveals tier 3; a skip opens the gate; a later paced GET resumes at the recorded step with the resuming line; a paced GET with a step id not in the lesson shows the fallback line and step 1; the response events written carry context "lesson_run" and validate against the schema; and the static build of the fixture contains the whole-lesson notice and no step chrome. Everything under tempfile.mkdtemp().</action>
  <verify>`python tests/paced_view_roundtrip.py` exits 0; `python itembank.py guard .` exits 0.</verify>
</task>
</tasks>
<out_of_scope>Narration, reader granularity menus, any new visual token or primitive (17A owns those; use existing classes), any change to gate-band structure or its shipped copy, the CLI (the continuous document is the accessible equivalent per D-16D-7), and Anki/audio surfaces.</out_of_scope>
<summary_obligations>Record in 16D-03-SUMMARY.md: every UI string as rendered, the byte-identity evidence for the plain lesson route, deviations, and every verify command with exit state.</summary_obligations>
