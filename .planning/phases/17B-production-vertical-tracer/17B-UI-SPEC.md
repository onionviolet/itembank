---
phase: 17B-production-vertical-tracer
status: draft
created: 2026-08-17
shadcn_initialized: false
---

# 17B UI specification: the polished unit experience

This is an experience contract, not a visual system. Every token, primitive,
and component comes from the 17A freeze; every flow, route, and recovery
state comes from the 16B IA contract; every strategy and note behavior from
16C. This document binds what the tracer's one unit must feel like end to
end and what evidence each stage owes. Per 17B-CONTEXT D-10, nothing visual
is invented here; a gap found here is a defect against the owning contract.

## 1. The learner journey under test

The unit runs the one learning loop (SOURCE-TO-COURSE step 6: orient,
predict or act, observe, explain, apply, record) as eight testable stages:

1. **Arrive.** Course shelf shows the fixture course; the scope tree is
   visible as structure (field, course, unit) with honest progress per
   section 3 below. Resume lands where the learner left off.
2. **Orient.** The unit opens with its objectives and cited sources
   visible; a direct-reading treatment opens the source view, reading
   scrolls (FLOW-02 bake-in), and locators are inspectable.
3. **Predict.** At least one prediction prompt appears before explanatory
   content; its response records as participation evidence, never as a
   graded verdict.
4. **Read and learn.** The authored lesson renders with, at minimum: hover
   and focus term definitions with a keyboard and touch equivalent,
   one things-to-know block, one expert-tip block, and one cited visual
   explanation with its static and accessible fallback. The same lesson
   file opens coherently in a plain Markdown reader outside the app.
5. **Practice.** Varied practice through the hint ladder, hints collapsed
   by default and never pre-announcing a reveal (RTS-09); targeted
   feedback references the learner's specific wrong answer.
6. **Test.** A graded sitting through the one runtime; keys undisclosed
   until the runtime's own gate; a short-answer item stays pending until
   marked; one transfer item is included.
7. **See progress.** Both rollup screens (section 3) reflect the sitting's
   settled evidence; the bounded course reaches complete under its named
   predicate during the tracer; the open field visibly does not.
8. **Continue.** The course path names the next action; interruption at
   any stage resumes without loss (16B interruption scenarios sampled,
   not rerun in full).

## 2. Required capability checklist (gate G4 and G8 inputs)

Each row must be demonstrated on the fixture unit at 1280, 768, and 375
widths, by keyboard, by touch, and with the screen-reader item held for
human verification (17B-CONTEXT D-04):

| Capability | Contract owner |
|---|---|
| Hover and focus term definitions, accessible equivalent | 16A CAP family |
| Things-to-know block | 16A |
| Expert-tip block | 16A |
| Cited visual explanation with static fallback | 16A media policy |
| Prediction prompt, participation-only evidence | 16A activity matrix |
| Hint ladder collapsed by default, no pre-announce | 17A UI-SPEC disclosure contract, RTS-09 |
| Targeted feedback on the specific wrong answer | runtime explain payload |
| Varied practice and one transfer item | 15B blueprint fidelity |
| Notes capture without note-authority leak | 16C |
| Plain-Markdown coherence outside the app | SOURCE-TO-COURSE portability rule |

## 3. Progress display contract (gate G5)

Two registered rollup models over identical GRAPH-03 tuples
(IL-20260817-01), selectable per scope with a global default:

- **ROLLUP-DIM:** the seven dimensions aggregate up the scope tree
  separately; every figure shows numerator and denominator or states
  indeterminate; membership classes (required, required-choice,
  enrichment) never merge; no single aggregate number appears anywhere.
- **ROLLUP-MAP:** a scope shows each direct child as a card carrying that
  child's own tuple summary and boundedness; no aggregation past direct
  children.

Shared rules: retrievability is never a percentage (GRAPH-03 bake-in); the
learner-facing retention display is the D-14A-3 fill state; an open scope
labels itself open and names its scope version on every claim; adding
enrichment never lowers completion. Weibao picks the default model at the
17B-03 checkpoint from rendered screens.

## 4. Accessibility and degradation

The nine UI-SPEC section 8 gates apply to every served page in the journey.
Offline: the whole journey completes with the network unplugged (the fixture
course is local; any model-backed assistance goes quiet rather than
blocking). Script-free: reading, sitting, and scoring still work; rich
behaviors degrade to their static equivalents. These are G4 and G8 evidence
rows, not aspirations; each has a named check in 17B-GATES.md.

## 5. Out of scope

New tokens, new primitives, new item types, new routes, real course
content in-repo, and any change to scoring, disclosure, or evidence
authority. A wanted-but-missing capability is recorded as a defect against
its owning contract per 17B-CONTEXT D-06.

## Checker sign-off

- [ ] Flows match the 16B IA contract without invention
- [ ] Every capability row names its contract owner
- [ ] Progress contract matches GRAPH-03 and IL-20260817-01
- [ ] Accessibility gates cited, human items marked human
- [ ] Degraded and offline states specified
- [ ] Scope boundary explicit

**Approval:** pending
