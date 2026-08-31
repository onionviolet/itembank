---
phase: 16D-paced-lesson
plan: 04
type: execute
wave: 4
depends_on: ["16D-01", "16D-02", "16D-03"]
files_modified:
  - tests/paced_lesson_tracer.py
  - .planning/phases/16D-paced-lesson/16D-FREEZE.md
autonomous: false
requirements: ["16D-CONTEXT freeze gate", A11Y-01]
must_haves:
  truths:
    - "One tracer proves the whole treatment end to end on synthetic content and asserts every reconsideration condition has not fired."
    - "The freeze closes only after Weibao reviews the rendered paced flow; an agent never signs it."
  artifacts:
    - "tests/paced_lesson_tracer.py, runnable by CI, all legs green or honestly skipped by name."
    - "16D-FREEZE.md with a freeze or a withholding, never silence."
  key_links:
    - "The tracer reuses tools/visual_qa.py's harness for its layout leg when Playwright is installed, the 17A-04 seam, and skips honestly when it is not."
---
<objective>
Prove the paced treatment end to end and put the freeze decision in front
of Weibao. Implements the 16D-CONTEXT freeze gate.
</objective>
<context>
@.planning/phases/16D-paced-lesson/16D-CONTEXT.md
@.planning/phases/16D-paced-lesson/16D-UI-SPEC.md
@tests/paced_steps_roundtrip.py, tests/lesson_run_roundtrip.py, tests/paced_view_roundtrip.py (the legs this tracer composes; do not duplicate their assertions, drive the whole flow once)
</context>
<tasks>
<task type="auto">
  <name>Task 1: The tracer</name>
  <files>tests/paced_lesson_tracer.py</files>
  <read_first>tests/cross_subject_suite_tracer.py for the scenario-table house style</read_first>
  <action>One scripted end-to-end run over fixtures/paced_lesson_bank.md in a temp dir, as scenarios: (1) ladder resolution at all three rungs; (2) a full paced sitting over HTTP: read, wrong checkpoint, tier 1 and 2, second wrong, tier 3, skip, gate opens, finish; (3) resume across an edit that inserts an earlier step, asserting the resumed step id is unchanged and the fallback line fires only when the recorded id is truly gone; (4) denominator exclusion measured through blueprint's AGENT-03 path; (5) exam contrast: the same item in an exam sitting discloses nothing at any point; (6) rung-3 byte-identity for a markerless lesson; (7) the reconsideration probes: authors-left-no-marker is observable (report, do not fail, whether the fixture uses markers), tier 1 does not make the fixture's four-option mc trivially solvable (assert at least two options remain unresolved after one wrong single pick), and no lesson-run attempt appears in any denominator without policy. When Playwright is installed, add the layout leg by invoking tools/visual_qa.py's page checks over the served paced view at 1280 and 375; when absent, print the honest skip line the 17A-04 test uses.</action>
  <verify>`python tests/paced_lesson_tracer.py` exits 0 with a scenario table; full suite still green; `python itembank.py guard .` exits 0.</verify>
</task>
<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Weibao reviews and the freeze is written</name>
  <files>.planning/phases/16D-paced-lesson/16D-FREEZE.md</files>
  <action>Ask Weibao to sit the paced fixture lesson end to end in a browser: keyboard only once, pointer once, one wrong checkpoint each way, the TOC jump, and the resume. Accessibility review per the standing rules; an agent never self-certifies. On acceptance write `## Frozen at 16D` recording the marker syntax as frozen from this date, the tracer results, the reviewer and date, served-byte hashes of the paced view, the rollback boundary (the three reverts named in the 16D-01/02/03 summaries), and the deferred list from 16D-CONTEXT. On rejection write `## Freeze withheld` with the exact gap and the next safe action.</action>
  <verify>16D-FREEZE.md contains `## Frozen at 16D` after human acceptance or `## Freeze withheld` with a named recovery; the tracer and full suite are green at the recorded commit.</verify>
</task>
</tasks>
<out_of_scope>New features of any kind; fixing 17-phase defects the tracer might surface (route them to owners, the 17B D-06 shape).</out_of_scope>
<summary_obligations>Record in 16D-04-SUMMARY.md: the scenario table, the reconsideration probe outcomes, the checkpoint outcome verbatim, and the freeze state.</summary_obligations>
