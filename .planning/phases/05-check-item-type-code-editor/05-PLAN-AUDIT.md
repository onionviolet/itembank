# Phase 5 Plan Audit — Interactive-Item Contract Amendment

**Verdict:** Revision required before execution. The seven plans credibly cover `check`
parsing, bounded execution, one-scorer grading, the editor, and case-level results. They
do **not** yet prove Roadmap Success Criterion 5: the first renderer-independent,
accessible interactive-item contract that future visual manipulatives can reuse.

This audit recommends amendments to Plans 05-01, 05-05, 05-06, and 05-07 only. Do not
add a plan or expand Phase 5 into a visual-item implementation.

## Blockers

### 1. The planned `response_schema` is check-specific, not a reusable interaction contract

**Evidence:** 05-01 plans `public_item()` to expose a `check`-only
`response_schema: {type: string, format: source, language: ...}` plus starter text.
05-07 validates only the corresponding `check_item` schema. No plan defines a public,
versioned contract that separates validated renderer configuration from the learner
response, nor a contract fixture an alternate renderer can consume without knowing the
quiz page.

**Why this blocks the goal:** A future canvas/SVG/keyboard renderer would have to infer
its own payload shape from `asCheck`, or add a browser-specific API path. That is not
renderer independence. It also leaves no proof that bank-authored configuration is
validated before reaching a renderer.

**Minimal amendment (05-01 Task 3; extend 05-07 Task 1):**

- Define and document one small public interactive-item envelope, reusing the existing
  `public_item()` boundary rather than creating a new route. It must contain a contract
  version/type, a validated declarative `renderer_config`, and an explicit
  `response_schema`; it must never contain bank-authored JavaScript or pre-answer key
  material.
- Make `check` its first instance: its language, starter source, and hidden-case count
  are renderer configuration; its source response is explicitly declared and validated.
  Keep D-12's source-text submission intact—an envelope need not turn the source into a
  different grading value.
- Add the envelope/response definitions to the published schema or protocol fixture,
  and an automated test that a renderer-independent consumer can validate and submit
  the fixture payload through `/api/submit` to the same `runtime.score_response()` path.
- Add a `must_haves` truth and key link that name this contract rather than only the
  `check` branch.

### 2. Non-pointer equivalence is assumed, not planned or verified

**Evidence:** 05-05 specifies keyboard editing (Tab/Shift-Tab), but its assertions are
HTML/source checks. 05-07's human pass checks gutter alignment, indent/undo, result-list
navigation, and safety copy. Neither requires a keyboard-only learner to submit a
response and receive the exact same response payload, verdict, evidence event, and
case-feedback shape as the ordinary control path.

**Why this blocks the goal:** Success Criterion 5 explicitly requires an accessible
non-pointer interaction to reach the same response shape. Keyboard editing alone does
not demonstrate submission parity or make the contract reusable by a semantic future
renderer.

**Minimal amendment (05-05 Task 3 and 05-07 Task 3):**

- Specify semantic label/instructions, focus order, and keyboard activation of Check
  (Enter/Space when the control is focused; no pointer-only affordance).
- Add an automated contract assertion that both the browser-facing and agent-facing
  submitters send the declared response shape and receive the same normalized verdict
  and result payload. This protects the protocol even without a JavaScript test runner.
- Add one named manual checkpoint: complete a fixture item with keyboard only, including
  focus, source entry, submission, and reading the per-case result; report the observed
  payload-equivalent verdict/feedback. Add it to 05-VALIDATION.md and 05-07 Task 3.

### 3. The feedback plan reports outcomes but does not establish the learning-loop seam

**Evidence:** 05-06 renders a pass/fail matrix with actual and expected output after a
run. It does not state that the learner's code is a prediction/action, that feedback is
case-specific and immediately tied to that action, or preserve a stable, non-answer-
leaking result shape for later diagnose → teach → retry work. The plan therefore risks a
high-quality answer-entry form rather than the first learn-by-doing interaction.

**Why this blocks the stated product direction:** Phase 5 need not implement Phase 6's
hint ladder, but it must not make future guided feedback depend on scraping page text or
re-running learner code. The response/result contract is the required seam: learner
action/prediction → bounded observation → targeted feedback → evidence, with runtime
authority intact.

**Minimal amendment (05-01 Task 3 and 05-06 Task 1):**

- Define the post-submit result payload as structured, ordered case observations
  (status/reason, actual output when safe, expected/pattern only after submission),
  associated with the submitted source and response contract version. Preserve the
  existing dichotomous verdict as the only grading authority.
- Require one fixture with a deliberately different failure per case and assert the
  feedback names the failed case/reason immediately after the action, without exposing
  inputs/expected outputs before submission. Do not add model feedback, partial credit,
  or a hint UI here; those remain Phase 6/8 work.
- State in the UI copy/contract that submitting source is the learner's executable
  prediction and the matrix is the observation, so later guided feedback has a stable
  semantic anchor rather than presentation-only strings.

## Required plan-level changes

| Plan | Amend in place | New acceptance proof |
|---|---|---|
| 05-01 | Task 3 + must_haves: public interaction envelope, validated renderer configuration, declared response/result semantics | Protocol/schema fixture validates; alternate non-page consumer reaches `/api/submit` and `runtime.score_response()` |
| 05-05 | Task 3: semantic keyboard submission parity, not just text editing | Focus/activation requirements plus normalized submit-payload assertion |
| 05-06 | Task 1: stable case-observation feedback shape and action→observation semantics | Different failures map to distinct case/reason feedback only after submit |
| 05-07 | Task 1 schema/protocol validation and Task 3 manual validation | Keyboard-only end-to-end completion, result readability, same response/verdict evidence shape |

## Scope guardrails

These amendments preserve the current phase boundary:

- No canvas/SVG/manipulative implementation, proprietary UI/content copying, editor
  theming, second language, sandbox, model hint, or partial-credit work.
- No new grading path: only `runtime.score_response()` returns the dichotomous verdict.
- No browser-held key or bank-authored executable JavaScript. Renderers receive
  validated declarative configuration and return the documented response shape.
- Phase 6 remains responsible for progressive hints/retries; this phase supplies the
  evidence-backed interaction seam it needs.

## Structured issues

```yaml
issues:
  - plan: "05-01"
    dimension: "requirement_coverage"
    severity: "blocker"
    description: "Roadmap Success Criterion 5 has no task or must_haves proof for a renderer-independent interactive-item contract; the planned response_schema is check-specific."
    task: 3
    fix_hint: "Amend Task 3 and 05-07 Task 1 to publish and test a versioned public interaction envelope with validated renderer_config, response_schema, and result semantics."
  - plan: "05-05"
    dimension: "key_links_planned"
    severity: "blocker"
    description: "Keyboard editing is planned, but no task proves an accessible non-pointer path sends the same declared response shape and reaches the same verdict/evidence/feedback as the normal submit path."
    task: 3
    fix_hint: "Add semantic keyboard submission requirements, an API payload-parity assertion, and a keyboard-only manual checkpoint in 05-07."
  - plan: "05-06"
    dimension: "verification_derivation"
    severity: "blocker"
    description: "The case matrix is presentation-oriented and does not define a stable action-to-observation feedback contract needed for the platform's diagnose→teach→learner action→bounded feedback loop."
    task: 1
    fix_hint: "Specify and test ordered per-case reason/result observations after submission, tied to source and contract version, while keeping runtime.score_response as the sole dichotomous grader."
```
