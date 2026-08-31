---
phase: 16D-paced-lesson
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - model.py
  - fixtures/paced_lesson_bank.md
  - tests/paced_steps_roundtrip.py
autonomous: true
requirements: [FLOW-02, "16D-CONTEXT D-16D-1, D-16D-2"]
must_haves:
  truths:
    - "A lesson with no [STEP:] marker and no [LESSON-PACE:] tag parses and renders byte-identically to before this plan."
    - "model.lesson_steps resolves the ladder deterministically: markers, else configured heading level, else one whole-document step."
    - "A resume position or checkpoint anchor can be expressed as a step id that survives edits elsewhere in the document."
  artifacts:
    - "fixtures/paced_lesson_bank.md, a synthetic bank exercising every rung."
    - "tests/paced_steps_roundtrip.py proving the ladder, the lint findings, and rung-3 byte-identity."
  key_links:
    - "Step ids at rung 2 are the existing heading slugs, so 16D-03's TOC links and 16B's anchor-based resume cite one identity, not two."
---
<objective>
Land the authored pacing surface of D-16D-1/D-16D-2: the `[STEP: <id>]`
marker, the `[LESSON-PACE:]` preamble tag, and one resolver
`model.lesson_steps()`. Format change is additive: rung 3 is today's
behaviour. Implements 16D-CONTEXT D-16D-1 and D-16D-2; the executor never
re-litigates the ladder or the syntax.
</objective>
<context>
@.planning/phases/16D-paced-lesson/16D-CONTEXT.md
@.planning/DECISIONS-PACED-LESSON-2026-08-28.md (section D-PACED-1)
@model.py (parse_lesson, around line 572; the [GATE:] directive handling around line 646; lint() around line 3375 and the lint-code table around line 2346)
</context>
<tasks>
<task type="auto">
  <name>Task 1: Parse the marker and the pace tag</name>
  <files>model.py</files>
  <read_first>model.py parse_lesson (whole function) and the three 16A directive helpers it cites (lesson_lang, lesson_dir near lines 489-525); the [GATE:] fallback pattern at line 646</read_first>
  <action>
  1. Add module constants: `STEP_RE = re.compile(r"(?m)^\[STEP:\s*([a-z0-9][a-z0-9-]{0,63})\s*\]\s*$")`, `LESSON_PACE_VALUES = ("none", "h2", "h3")`.
  2. Add a preamble reader `lesson_pace(head)` copying the `[GATE:]` shape exactly: read `[LESSON-PACE: <value>]` from the effective preamble; a value outside `LESSON_PACE_VALUES` falls back to `"none"` and is reported at lint time, never here. `parse_lesson`'s returned dict gains the key `pace` alongside the 16A directive keys.
  3. Add `lesson_steps(lesson)`, taking `parse_lesson`'s return dict and resolving the ladder:
     - Rung 1: if `STEP_RE` matches anywhere in the effective lesson text (`intro` plus every heading `body`), split the document at the markers. Content before the first marker, when non-empty, is step id `intro` with title equal to the lesson's first heading text or `"Introduction"` when there is none. Each marker opens a step whose id is the captured id and whose title is the first heading text inside the step, else the first eight words of its first non-empty line.
     - Rung 2: else if `pace` is `h2` or `h3`, one step per heading of that level, id = the heading's existing `slug`, title = the heading text; content before the first such heading is the `intro` step as above.
     - Rung 3: else exactly one step, id `document`, title = the lesson's first heading text or `"Lesson"`.
     Return a list of dicts, each `{"id", "title", "rung", "content"}` where `content` is the step's slice of the effective lesson text with any `[STEP:]` marker lines removed, in document order. Marker lines are pacing metadata and are never rendered as prose in any mode; a bank written before this plan contains none, so nothing already rendering changes.
  4. Duplicate ids at rung 1 (including a literal `intro` colliding with the synthesized intro step) make `lesson_steps` keep the FIRST occurrence and mark later ones by appending nothing; do not de-duplicate silently: the function still returns them (ids as authored) and lint is the enforcement (Task 2). The docstring states this division: the parser reports what is written, the linter judges it (the house rule the [GATE:] comment already states).
  </action>
  <verify>`python - <<'E'` snippet in tests (Task 3) covers this; interim check: `python -c "import model; l = model.parse_lesson('fixtures/lesson_bank.md'); print(model.lesson_steps(l))"` prints a one-element rung-3 list with id `document`.</verify>
</task>
<task type="auto">
  <name>Task 2: The three lint findings</name>
  <files>model.py</files>
  <read_first>model.py lint() lesson-finding emission (grep `lesson.invalid_gate` for the exact emission shape and the code table near line 2346)</read_first>
  <action>
  Add three findings, following `lesson.invalid_gate`'s exact shape and severity conventions, and add each to the lint-code table comment:
  1. `lesson.invalid_step` (error): a line matching `^\[STEP:` that does not match `STEP_RE`. Message: `"[STEP:] id must be 1-64 chars of a-z 0-9 hyphen, starting alphanumeric: <line>"`.
  2. `lesson.duplicate_step` (error): the same step id authored twice (or colliding with the synthesized `intro`). Message: `"[STEP: <id>] appears more than once; a resumable step needs one identity"`.
  3. `lesson.invalid_pace` (warning): `[LESSON-PACE:]` value outside `LESSON_PACE_VALUES`, message `"[LESSON-PACE: <value>] is not one of none, h2, h3; pacing falls back to none"`.
  No em dash characters in any message.
  </action>
  <verify>`python itembank.py lint fixtures/paced_lesson_bank.md` reports zero errors on the good fixture; the test's broken variants (written to a temp dir, never committed) surface all three messages.</verify>
</task>
<task type="auto">
  <name>Task 3: Fixture and roundtrip proof</name>
  <files>fixtures/paced_lesson_bank.md, tests/paced_steps_roundtrip.py</files>
  <read_first>fixtures/lesson_bank.md (shape of a lesson-carrying fixture); tests/lesson_roundtrip.py main() (house test style: fail()/ok(), stdlib only, no framework)</read_first>
  <action>
  1. Author `fixtures/paced_lesson_bank.md`: a synthetic invented-subject lesson (never real course content; `itembank guard` must stay clean) with three `[STEP:]` markers (`orientation`, `mechanism`, `application`), prose before the first marker, two `##` headings, at least two `mc` items whose ids the 16D-03 checkpoint fixture will reuse, and a `[LESSON-PACE: h2]` tag that rung 1 must override (markers win).
  2. Write `tests/paced_steps_roundtrip.py` asserting, in order:
     - rung 1: the fixture yields four steps (`intro`, `orientation`, `mechanism`, `application`), in document order, with no `[STEP:` text in any `content`;
     - marker precedence: the fixture's `[LESSON-PACE: h2]` is present and rung is still 1;
     - rung 2: the same lesson text with markers stripped (in memory) and pace `h2` yields one step per `##` heading, ids equal to the heading slugs;
     - rung 3 byte-identity: for `fixtures/lesson_bank.md` (no markers, no pace), `lesson_steps` returns exactly one step whose `content` equals the effective lesson text, and `parse_lesson`'s returned dict equals its pre-plan shape plus only the new `pace` key (assert the key set explicitly);
     - identity stability: inserting a new `[STEP: preface]` marker at the top of the fixture text (in memory) changes no other step's id;
     - lint: the three findings fire on deliberately broken in-memory variants written under `tempfile.mkdtemp()`, and the shipped fixture lints with zero errors.
  3. The test writes nothing inside the repository (the CI clean-tree step).
  </action>
  <verify>`python tests/paced_steps_roundtrip.py` exits 0 printing one ok line per assertion group; `python itembank.py lint fixtures/paced_lesson_bank.md` reports 0 errors; `python itembank.py guard .` exits 0; `python tests/lesson_roundtrip.py` still exits 0 (byte-identity leg).</verify>
</task>
</tasks>
<out_of_scope>Rendering (16D-03), sessions and evidence (16D-02), agent-proposed markers (deferred candidate H), any reader-side granularity control, narration, and any change to parse_bank(), the scorer, or existing lint findings.</out_of_scope>
<summary_obligations>Record in 16D-01-SUMMARY.md: the exact key set parse_lesson now returns, the four fixture step ids, every verify command with exit state, and any deviation.</summary_obligations>
