---
phase: 17A-visual-system-component-foundation
plan: 01
type: tracer
wave: 1
depends_on: []
files_modified:
  - surfaces/visual_fixture.py
  - server.py
  - tests/visual_system_roundtrip.py
  - fixtures/visual_system_flow.json
autonomous: true
requirements: [VISUAL-01, VISUAL-02]
must_haves:
  truths:
    - "One synthetic lesson-plus-practice flow exercises every VISUAL-01 state through the real shared shell."
    - "All three direction renderings use byte-identical semantic body markup and differ only through registered direction tokens and CSS."
    - "Missing upstream 16B or 16C data renders explicit synthetic or unavailable states and never invents runtime authority."
  artifacts:
    - "fixtures/visual_system_flow.json contains only synthetic content and all seven required flow stages."
    - "tests/visual_system_roundtrip.py proves route, semantic parity, token resolution, and abuse-clamp behavior."
  key_links:
    - "server.py exposes the fixture through presentation.surface_shell, never through a second shell."
---

<objective>
Ship the production-quality tracer that proves the full visual-system seam
before expanding components. Implements D-04, D-06, D-07, and D-08. D-12 is
satisfied by the existing checker-reviewed `17A-UI-SPEC.md`, which every task
in this plan treats as binding input.
</objective>

<context>
@.planning/phases/17A-visual-system-component-foundation/17A-CONTEXT.md
@.planning/phases/17A-visual-system-component-foundation/17A-UI-SPEC.md
@.planning/phases/17A-visual-system-component-foundation/17A-RESEARCH.md
@surfaces/presentation.py
@surfaces/theme.py
@server.py
</context>

<tasks>
<task type="auto">
  <name>Task 1: Define the synthetic same-flow fixture and failing contract tests</name>
  <files>fixtures/visual_system_flow.json, tests/visual_system_roundtrip.py</files>
  <action>Create synthetic data for shelf resume, source-linked objective, long lesson with all six named content forms, wrong-answer retry, sparse evidence plus pending prose, cited AI diff, and agent/offline status. Add tests first for seven-stage coverage, no keyed leak, semantic markup fingerprint equality across directions, unresolved CSS variables, fixed-rule clamping under VISUAL-02 abuse, and no em dash in authored fixture prose.</action>
  <verify>Run `python tests/visual_system_roundtrip.py`; it must fail only because the fixture route and direction registry do not yet exist.</verify>
</task>
<task type="auto">
  <name>Task 2: Serve one semantic tracer in three reversible directions</name>
  <files>surfaces/visual_fixture.py, server.py, tests/visual_system_roundtrip.py</files>
  <action>Add one fixture renderer using native semantic HTML and `surface_shell`. Register exactly `structured-studio`, `quiet-workbench`, and `guided-canvas` as CSS/token overlays. Do not fork markup, scoring, navigation, or state meaning. Keep the route explicitly synthetic and development-only. Apply every direction-neutral overflow, disclosure, wrapping, loading, empty, error, and narrow-width ruling in 17A-UI-SPEC.</action>
  <verify>Run `python tests/visual_system_roundtrip.py`, `python tests/stylesheet_roundtrip.py`, and `python itembank.py guard .`; all exit 0 and guard reports zero offenders.</verify>
</task>
</tasks>

<out_of_scope>No token freeze, no chosen default, no day migration, no real learner data, and no upstream capability implementation.</out_of_scope>
<summary_obligations>Record the semantic fingerprint, route, three direction IDs, fixture coverage, degraded states, and exact verification output in 17A-01-SUMMARY.md.</summary_obligations>
