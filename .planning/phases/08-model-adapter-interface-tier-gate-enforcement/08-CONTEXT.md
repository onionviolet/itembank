# Phase 8: Model Adapter Interface & Tier-Gate Enforcement - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase adds a provider-neutral model adapter for error-specific hints and pending rubric suggestions, plus a runtime-owned gate that drops output exceeding the tier Phase 6 permits. It logs every interaction and degrades to the authored offline loop when unavailable. It does not let a model score accepted evidence, select items, write banks, or control tier progression.

</domain>

<decisions>
## Implementation Decisions

### Adapter contract
- **D-01:** One adapter request/response contract covers both hosted CLI and local OpenAI-compatible backends. Requests declare operation (`hint` or `rubric_review`), immutable interaction id, model/backend metadata, item context, learner response, permitted tier, and a version. Responses contain structured content, provider metadata, and refusal/error status; surfaces never parse provider-native output.
- **D-02:** Backend selection is exclusively configuration (`model_backend`); switching backend requires no caller changes. The hosted CLI is a subprocess adapter and the local endpoint is an HTTP adapter, both behind the same function boundary.
- **D-03:** Provider-specific options live under named backend profiles so multiple providers can coexist and the user can switch later. Secrets remain environment/config references and are never copied into evidence.
- **D-04:** Every call has a strict timeout and bounded output. Unreachable, malformed, timed-out, or refused calls return a typed unavailable result; authored hints, scoring, lessons, reports, and marking continue.

### Tier-gate enforcement
- **D-05:** Prompting is defense in depth, never the gate. The runtime validates model output after generation and before any surface receives it.
- **D-06:** The gate is a first-class, independently tested component with three layers: schema validation; deterministic checks against answer/key and content reserved for higher tiers; and a conservative ambiguity rule that drops uncertain output. It never rewrites a leaking hint into something that might change meaning.
- **D-07:** Model output is structured into claims/spans with source labels where possible, enabling the runtime to compare each claim with the facts permitted at the current tier. The planner/researcher must design and adversarially test the actual detection mechanism before adapter plumbing is considered complete.
- **D-08:** Gate outcomes are `pass`, `drop`, or `unavailable`, with machine-readable reasons. Only `pass` content may enter a learner-facing payload. A drop falls back to the authored tier if available and otherwise says the generated hint is unavailable without revealing why.
- **D-09:** The gate receives the full private item and the Phase 6 permitted tier, but the browser receives neither. Tier progression remains exclusively Phase 6 state; the adapter cannot request, infer, or advance it. — **Reversibility:** costly — this boundary is consumed by every future model operation and must be stable before publication.

### Error-specific hints
- **D-10:** Hint requests include the learner's most recent genuine wrong response and relevant authored analysis. The generated hint must address that error, not give a generic restatement.
- **D-11:** Generated hints augment one unlocked authored tier; they do not replace the authored ladder. Offline and model-disabled sessions remain pedagogically complete.
- **D-12:** At most one model generation is attempted for a given interaction id unless the user explicitly retries; retries retain a parent id so cost and repeated failures are visible.

### Rubric suggestions
- **D-13:** A rubric-review response is a per-point suggestion with pass/fail/uncertain and rationale. It appends a model-interaction event and a pending review proposal linked to the original short-answer response.
- **D-14:** Model rubric output never mutates the response score or creates an accepted mark. A human must explicitly accept or replace it through the existing mark event path; accepted evidence identifies the human action and may reference the proposal.

### Evidence, privacy, and observability
- **D-15:** Every attempted interaction is logged, including backend/profile, operation, timing, request fingerprint, outcome, gate result, permitted tier, and returned learner-facing content when passed. Raw secrets and provider credentials are never logged.
- **D-16:** Dropped output is recoverable for local audit only when it can be stored without exposing secrets through normal reports; normal learner/session retrieval returns the outcome and reason code, not leaked text. Research should decide the safest local audit representation.
- **D-17:** Hosted-provider transmission of item text is already accepted in PROJECT.md, but each interaction records whether it used a hosted or local backend so later audits can distinguish exposure.

### Codex's Discretion
These are delegated choices. The tier detector is explicitly not considered solved by this discussion: research and the planning model own its concrete algorithm and adversarial evaluation. They may combine compatible detectors, but must fail closed and preserve the runtime boundary.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/ROADMAP.md` § "Phase 8: Model Adapter Interface & Tier-Gate Enforcement" — goal, five success criteria, and unresolved gate mechanism.
- `.planning/REQUIREMENTS.md` TEACH-04 through TEACH-09 and MODEL-01 through MODEL-05 — binding adapter, hint, rubric, and offline behavior.
- `.planning/PROJECT.md` — runtime-authority rule, accepted hosted-model exposure, local-backend requirement, and degrade-never-block constraint.
- `.planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md` — permitted-tier state, explicit stumped unlock path, and authored fallback.
- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — append-only evidence and human-only accepted marking.
- `evidence.py` — mark events, review-state derivation, response linkage, and event storage.
- `runtime.py` — answer-key withholding and explanation boundaries.
- `model.py` — key, distractor analysis, model answer, and rubric source fields.
- `schemas/settings.schema.json` — existing inert `model_backend` contract.
- `schemas/response.schema.json` — pending review and model-interaction extension points.
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/INTEGRATIONS.md`, and `.planning/codebase/TESTING.md` — layer boundaries, external-process/network seams, and cross-platform tests.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 6's tier state is the sole authority input to the gate.
- `evidence.mark_event()` already separates pending short responses from accepted human marks.
- Settings already reserve `model_backend`; daemon and CLI already share runtime paths.

### Established Patterns
- External capability degrades to an omission, never blocks core study.
- Private payloads remain server-side; browser responses are constructed explicitly.
- Append-only events preserve proposals and later acceptance separately.

### Integration Points
- New provider-neutral adapter and tier-gate modules beside `runtime.py`.
- `surfaces/settings.py` and settings schema for backend profiles.
- Phase 6 hint path for optional generated augmentation.
- Evidence/schema additions for interaction and pending rubric proposal events.
- Adversarial gate tests plus hosted-CLI/local-endpoint contract fixtures.

</code_context>

<specifics>
## Specific Ideas

The planning model should treat leakage prevention as this phase's hardest deliverable and combine compatible defenses where they improve coverage. Provider plumbing is secondary and must not create a false sense that prompt instructions enforce the tier.

</specifics>

<deferred>
## Deferred Ideas

- Model-authored bank changes and retry-to-clean authoring — Phase 11.
- Model-driven selection — out of scope; selection remains rule-based.
- Accepted automated scoring of prose — explicitly out of scope.

</deferred>

---

*Phase: 8-model-adapter-interface-tier-gate-enforcement*
*Context gathered: 2026-08-08*
