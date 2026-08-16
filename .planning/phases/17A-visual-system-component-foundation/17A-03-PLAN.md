---
phase: 17A-visual-system-component-foundation
plan: 03
type: execute
wave: 3
depends_on: ["17A-02"]
files_modified:
  - surfaces/presentation.py
  - surfaces/visual_fixture.py
  - tests/component_primitives_roundtrip.py
  - tests/visual_system_roundtrip.py
autonomous: true
requirements: [VISUAL-01, VISUAL-02, A11Y-01]
must_haves:
  truths:
    - "Every inherited 16B and 16C component maps to shared semantic primitives with direction-neutral state meaning."
    - "Keyboard order, text labels, wrapping, 44px targets, reduced motion, static fallbacks, and semantic equivalence hold at every width."
  artifacts:
    - "tests/component_primitives_roundtrip.py covers the complete component inventory and zero, one, many, error, loading, partial, and overflow states."
  key_links:
    - "Primitive CSS consumes the frozen tokens and never owns raw palette values."
---
<objective>Implement and verify the accessible primitive layer inherited from 16B and 16C, without reopening their semantics. Implements D-06 and D-10.</objective>
<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/17A-visual-system-component-foundation/17A-UI-SPEC.md
@.planning/phases/17A-visual-system-component-foundation/17A-02-SUMMARY.md
</context>
<tasks>
<task type="auto">
  <name>Task 1: Add shared primitives and exhaustive state fixtures</name>
  <files>surfaces/presentation.py, surfaces/visual_fixture.py, tests/component_primitives_roundtrip.py, tests/visual_system_roundtrip.py</files>
  <action>Add native semantic primitives for CourseShelf, ActivityView, FirstLaunchWalkthrough, SettingsPanel, StatusNotice, NoteCapturePanel, NotesPanelEvidence, StrategyPicker, ProgressComprehensionDisplay, NoteOutputTrio, EvidenceDrawer, diff review, loading lines, anchor chips, and fill-state blocks. Apply the exact disclosure, scroll, grow, wrapping, path, grouping, and glyph rulings from 17A-UI-SPEC. Use text labels first, correct voices, no color-only cues, no invented percentages, no focus traps, and useful plain HTML fallbacks.</action>
  <verify>Run `python tests/component_primitives_roundtrip.py`, `python tests/visual_system_roundtrip.py`, `python tests/stylesheet_roundtrip.py`, and `python itembank.py guard .`; all exit 0.</verify>
</task>
</tasks>
<out_of_scope>Data backing for unexecuted upstream modules, interactive graph canvas, new copy, new routes, or a component registry.</out_of_scope>
<summary_obligations>Map every component and state row to its primitive and test in 17A-03-SUMMARY.md.</summary_obligations>

