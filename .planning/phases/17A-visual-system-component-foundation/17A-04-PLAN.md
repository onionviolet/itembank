---
phase: 17A-visual-system-component-foundation
plan: 04
type: execute
wave: 4
depends_on: ["17A-03"]
files_modified:
  - tools/visual_qa.py
  - tests/visual_accessibility_roundtrip.py
  - .planning/phases/17A-visual-system-component-foundation/17A-QA.md
  - .planning/phases/17A-visual-system-component-foundation/17A-FREEZE.md
autonomous: false
requirements: [VISUAL-01, VISUAL-02, A11Y-01]
must_haves:
  truths:
    - "A pinned dev-only browser harness produces repeatable layout evidence without entering the shipped runtime."
    - "The hover-only negative fixture fails equivalence review, and AI output is never treated as accessibility certification."
    - "The freeze closes only after Phase 13.9 evidence exists and Weibao accepts A11Y-01."
  artifacts:
    - "17A-QA.md links the width, zoom, keyboard, touch, contrast, motion, and screen-reader evidence."
    - "17A-FREEZE.md records exact token names, selected direction, served-byte hashes, validation commands, and any withholding reason."
  key_links:
    - "The human checkpoint consumes browser evidence and is the sole A11Y-01 acceptance authority."
---
<objective>Prove the visual foundation in a layout-capable browser, obtain human accessibility acceptance, and write the freeze record only when every gate is satisfied. Implements D-09 and D-11.</objective>
<context>
@.planning/phases/17A-visual-system-component-foundation/17A-RESEARCH.md
@.planning/phases/17A-visual-system-component-foundation/17A-03-SUMMARY.md
@.planning/UI-SPEC.md
@.planning/REQUIREMENTS.md
</context>
<tasks>
<task type="auto">
  <name>Task 1: Produce driven-browser evidence</name>
  <files>tools/visual_qa.py, tests/visual_accessibility_roundtrip.py, .planning/phases/17A-visual-system-component-foundation/17A-QA.md</files>
  <action>Prefer an already-approved driver. Otherwise stop for supply-chain approval before adding a pinned version, checksum, license record, and dev-only isolation. Capture 1280, 768, and 375 layouts; 200 percent zoom and reflow; keyboard order and visible focus; 44px targets; light and dark contrast; reduced motion; touch-equivalent disclosure; static fallback; and deliberate hover-only failure. Write exact commands, artifacts, and failures to 17A-QA.md.</action>
  <verify>Run `python tests/visual_accessibility_roundtrip.py`; the positive matrix passes and the negative hover-only case fails for the expected equivalence reason.</verify>
</task>
<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Human A11Y-01 review and freeze decision</name>
  <files>.planning/phases/17A-visual-system-component-foundation/17A-QA.md, .planning/phases/17A-visual-system-component-foundation/17A-FREEZE.md</files>
  <action>Ask Weibao to perform the scripted keyboard, touch, screen-reader, zoom, high-contrast, and reduced-motion review. If any task is not equivalent, record Freeze withheld and the exact gap. If accepted, first verify Phase 13.9's walking-skeleton summary, then write the freeze with selected direction, token inventory, component inventory, served-byte hashes, human reviewer and date, command results, rollback boundary, and deferred items.</action>
  <verify>`python tests/visual_accessibility_roundtrip.py`, `python tests/component_primitives_roundtrip.py`, `python tests/stylesheet_roundtrip.py`, and `python itembank.py guard .` all pass; 17A-FREEZE.md contains either `## Frozen at` after human acceptance or `## Freeze withheld` with named recovery.</verify>
</task>
</tasks>
<out_of_scope>Self-certifying accessibility, closing without 13.9, shipping the browser driver, 17B tracer work, signing, or native packaging.</out_of_scope>
<summary_obligations>Record supply-chain evidence, every QA artifact, human findings, gate state, and freeze or withholding rationale in 17A-04-SUMMARY.md.</summary_obligations>
