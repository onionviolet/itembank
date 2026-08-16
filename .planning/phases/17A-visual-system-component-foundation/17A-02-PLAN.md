---
phase: 17A-visual-system-component-foundation
plan: 02
type: execute
wave: 2
depends_on: ["17A-01"]
files_modified:
  - .planning/phases/17A-visual-system-component-foundation/17A-DIRECTION.md
  - surfaces/theme.py
  - surfaces/presentation.py
  - surfaces/day.py
  - tests/stylesheet_roundtrip.py
  - tests/day_roundtrip.py
autonomous: false
requirements: [VISUAL-01, VISUAL-02]
must_haves:
  truths:
    - "Weibao chooses the default after reviewing all three same-flow prototypes at 1280, 768, and 375 pixels."
    - "Five type tokens and bounded comfortable or compact density tokens are the only production additions to the existing scheme."
    - "The day route composes theme and SHARED_CSS through surface_shell while preserving behavior."
  artifacts:
    - "17A-DIRECTION.md records the chosen direction and review evidence."
    - "Every served route declares all four font faces and resolves every CSS variable."
  key_links:
    - "The checkpoint precedes every selected-direction token change."
---

<objective>Select the one-way visual direction, then create the token and shell freeze candidate. Implements D-01, D-02, D-03, D-04, D-05, and D-10. D-03 is interpreted against current disk evidence: completed Phase 13.5 work is verified and reused, token work is not duplicated, and its non-token behavior remains outside 17A.</objective>
<context>
@.planning/phases/17A-visual-system-component-foundation/17A-01-SUMMARY.md
@.planning/phases/17A-visual-system-component-foundation/17A-UI-SPEC.md
@surfaces/day.py
@tests/stylesheet_roundtrip.py
</context>
<tasks>
<task type="checkpoint:decision" gate="blocking">
  <name>Task 1: Choose the default visual direction</name>
  <files>.planning/phases/17A-visual-system-component-foundation/17A-DIRECTION.md</files>
  <action>Present matched screenshots for Structured Studio, Quiet Workbench, and Guided Canvas at all three widths, plus compact density. Recommend Structured Studio with Quiet Workbench density and bounded Guided Canvas elements, but apply no default silently. Record Weibao's choice, rationale, accepted screenshots, and rejected alternatives.</action>
  <verify>17A-DIRECTION.md names exactly one direction and contains a human decision record.</verify>
</task>
<task type="auto">
  <name>Task 2: Freeze token names and migrate the day shell</name>
  <files>surfaces/theme.py, surfaces/presentation.py, surfaces/day.py, tests/stylesheet_roundtrip.py, tests/day_roundtrip.py</files>
  <action>Add `--text-xs`, `--text-body`, `--text-lesson`, `--text-heading`, and `--text-display` with the UI-SPEC values. Add the three density aliases with comfortable and compact bounds. Promote only the checkpoint-selected overlay. Refactor day rendering to call `surface_shell`; remove duplicated shell ownership without changing route content or day behavior. Verify existing `--edge`, do not re-add it. Add served-byte tests for raw-size consolidation, fonts, variables, bounds, 44px targets, and day parity.</action>
  <verify>Run `python tests/stylesheet_roundtrip.py`, `python tests/day_roundtrip.py`, `python tests/visual_system_roundtrip.py`, and `python itembank.py guard .`; all exit 0.</verify>
</task>
</tasks>
<out_of_scope>Non-token Phase 13.5 behavior, alternate permanent themes, icons, IA changes, and native UI code.</out_of_scope>
<summary_obligations>Record the human choice, token table, day parity evidence, raw-value allowlist, and rollback notes in 17A-02-SUMMARY.md.</summary_obligations>
