# Phase 20 UI audit index

**Current routing owner:** `20-AUDIT-CROSSWALK.md`
**Implementation owner:** `20-01-PLAN.md` through `20-05-PLAN.md`
**Historical records:** preserved in place and not rewritten

## Read order

1. `20-AUDIT-CROSSWALK.md` for the current disposition and owning plan.
2. `20-INSPIRATION-MATRIX.md` for external behaviors adopted, tested, or rejected.
3. `20-EXTENSION-COVERAGE.md` for EXT-01 through EXT-05 and the independent settings axes.
4. `20-CONTEXT.md` and `20-UI-SPEC.md` for binding Phase 20 decisions.
5. The source audit named by a crosswalk row when exact evidence or rationale is needed, then the numbered plans for execution.

## Historical audit groups

| Group | Documents | What they contribute |
|---|---|---|
| Product and vision | `VISION-PLAN-AUDIT-2026-09-06.md`, `TRANSITION-AUDIT-SYNTHESIS.md`, `SOURCE-TO-COURSE.md` | Course-first product, authority, real learner journey, and wrong-direction corrections |
| Visual and interaction | `UI-CHARACTER-AUDIT-2026-09-06.md`, `13.5-UI-SPEC.md`, `17A-UI-SPEC.md` | Verified presentation defects, typography, controls, reader, hints, tokens, primitives, and accessibility gates |
| Information architecture and lifecycle | `16B-UI-SPEC.md`, `17B-UI-SPEC.md`, `2026-09-07-home-and-transition-ui-scope.md` | Routes, exact resume, Back and Home, completion, degraded states, and representative journey |
| Remediation and reach | `AUDIT-REMEDIATION-PLAN-2026-09-06.md`, `REACH-MILESTONE.md`, Phase 19 records | Existing repair order, Reach boundaries, and evidence Phase 20 may consume but not replace |
| Extensibility | `EXTENSION-DELIVERY-2026-09-06.md`, `PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md` | Profiles, themes, capability adapters, migration, removal recovery, and EXT-05 exclusions |
| External learning-platform research | `2026-09-05-open-source-absorption.md`, `2026-09-07-home-and-transition-ui-scope.md`, Phase 16 research streams | Reusable behavior patterns, counterexamples, licensing boundaries, and prototype questions |

## Hygiene rule

Do not add a new UI audit while Phase 20 is active. Add a finding to `20-AUDIT-CROSSWALK.md`, cite its evidence, assign one disposition and one plan, then update the affected plan acceptance gate. A later dated audit may remain historical, but it must point back to the crosswalk for current ownership.
