# Phase 8: Model Adapter Interface & Tier-Gate Enforcement - Context

**Gathered:** 2026-08-08, updated 2026-08-10 (round-two research absorbed)
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase adds a provider-neutral model adapter for error-specific hints and pending rubric suggestions, plus a runtime-owned gate that drops output exceeding the tier Phase 6 permits. It logs every interaction and degrades to the authored offline loop when unavailable. It does not let a model score accepted evidence, select items, write banks, or control tier progression.

Round-two scope (2026-08-10): the hosted Claude-Code-class backend is the design target and default; local backends are additional registrations behind the same interface. Tier-3 rubric review is not a scorer strategy at all — it is a peer of the human marker, implemented first as self-assessment against a revealed model answer. The refusal the learner sees is runtime state (a structural lock), never model voice.
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

### Round-two amendments (research absorbed 2026-08-10)
- **D-18 (hosted-first, ROADMAP criterion 8):** The hosted Claude-Code-class backend is the design target, is built first, and is the default. The local 24GB card is an **additional registration behind the same interface** — not a fork and not a prerequisite. Each backend profile declares its own context-size and latency limits; no plan may assume one context window everywhere. This does not relax the runtime-authority rule: the model decides nothing about correctness, and tier-3's pending rule is not a function of which backend runs. — **Reversibility:** reversible — profiles are settings entries; removing one is deleting an entry.
- **D-19 (bench honesty, ROADMAP criterion 9):** `itembank bench` is still owed but is off the critical path, and **no plan or roadmap entry may carry an invented tok/s or latency figure**. The recommended local pairing to *measure* when the hardware lands is Qwen3-30B-A3B-Instruct-2507 Q4_K_M (gpt-oss-20b as a second backend) on Vulkan-over-ROCm gfx1100. It is a starting configuration, not a validated one.
- **D-20 (tier-3 is not a scorer strategy, ROADMAP criterion 10):** Tier-3 promotability is a **constant zero**, not a spectrum: LLM judges are non-reproducible even at temperature 0, judge bias survives explicit anti-bias prompting (d=4.25), and Ofqual (14 Jan 2026) forbids AI as a sole marker. Tier 3 therefore sits **outside `score_response()` entirely**, as a peer of the human marker. — **Reversibility:** one-way in effect — a shipped auto-promotion path would contaminate accepted evidence permanently; do not build one.
- **D-21 (tier-3 approaches, all preserved for future choice):** Ranked approaches, recorded so the user can choose later without a redesign: **(1) self-assessment against a revealed model answer** — recommended default: a learner self-mark *is* a human accept, which dissolves the pending state rather than managing it (g=0.55/0.664); **(2) deferred human marking**; **(3) rubric decomposition** — justified on **accept ergonomics, not accuracy**. Implement (1) first; (2) and (3) remain registered alternatives behind one proposal interface where they can coexist without lowering quality.
- **D-22 (suggestion presentation, ROADMAP criterion 11):** The model suggestion sits behind a disclosure control `suggestion_reveal`, default `after-self-mark`, with all three values shipped as a setting. It renders only as a `--pending` token — **never a number, never a fraction, never a check or cross glyph**. Accept is the existing `mark_event`. A suggestion never accepted stays pending forever, which is a correct terminal state, not a queue to drain.
- **D-23 (mark_proposal event, ROADMAP criterion 12):** This phase adds a `mark_proposal` event type and must **not** widen the human-only guard: `mark_event` keeps raising `ValueError` on `marker != "human"` (`evidence.py:1058`). Verified facts that shape the work: a mark is already a separate append-only event about a response; `review_state` is already computed at read time; `mark_event(rubric=...)` already stores per-criterion results as N booleans. — **Reversibility:** one-way — append-only event shape can only be superseded, never rewritten.
- **D-24 (partial credit, ROADMAP criterion 13):** Partial credit is **N booleans**. No fractional score, no confidence weighting. A derived "4 of 5" computed at read time is fine. The Phase 1 one-way door stays closed; no `checkpoint:decision` is owed for it.
- **D-25 (auto-accept impossible, ROADMAP criterion 14):** Auto-accepting a tier-3 suggestion is **impossible, not off by default** — no valid gate variable exists (model confidence is uncalibrated), so there is no setting, flag, or autonomy level that turns it on. **Batch accept by a human is the only ergonomics concession and the only one offered.** The config-swap freedom of criterion 2 stops exactly here.
- **D-26 (structural lock presentation):** The refusal a learner sees is **runtime state, not model voice**: a locked tier renders as a labeled structural lock with the unlock condition stated, and generated text renders in plain chrome inside a labeled container so a model never acquires a typographic voice of its own. Copy tables in `08-UI-SPEC.md` are binding (updated to the study-mode-wave findings).
- **D-27 (third-backend extensibility, ROADMAP criterion 7):** Adding a third backend (a second hosted CLI, a local llama.cpp server, a future vendor) is **a new adapter module plus a config entry**, with zero edits to tier-gate, evidence, or prompt-assembly code — proven by adding a stub backend in a test.

### Future user choices (recorded now, selectable later)
- **Backend profiles:** hosted CLI (default), local OpenAI-compatible (llama.cpp / Ollama / Qwen), and any future vendor coexist as named profiles under `model_backend`. Switching is config-only; the user can add/remove without code changes.
- **Tier-3 review approaches:** self-assessment (default), deferred human marking, rubric decomposition — all three stay expressible behind one proposal interface; only self-assessment ships as the first implementation, and auto-accept of any of them stays impossible.
- **`suggestion_reveal` timing:** `after-self-mark` (default), `before-self-mark`, `after-mark` — all three values ship as a setting.

### the agent's Discretion
The concrete tier-detector algorithm, adapter module factoring, and exact copy details remain delegated to research and planning (they must fail closed and preserve the runtime boundary). Not open: auto-accept, widening the human-only mark guard, prompt-as-gate, or any path that lets a model write accepted evidence.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase contracts and requirements
- `.planning/ROADMAP.md` § "Phase 8: Model Adapter Interface & Tier-Gate Enforcement" — goal, fourteen success criteria, unresolved gate mechanism, round-two rulings.
- `.planning/REQUIREMENTS.md` TEACH-04 through TEACH-09 and MODEL-01 through MODEL-05 — binding adapter, hint, rubric, and offline behavior.
- `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-UI-SPEC.md` — approved UI design contract: lifecycle states, copy tables, `suggestion_reveal`, structural lock, no-leak DOM, a11y gates.
- `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-AI-SPEC.md` — approved AI design contract: framework decision, 30-case reference dataset, evaluation dimensions, guardrails.
- `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-RESEARCH.md` — bounded hint-plan gate, adapter parity fixtures, validation architecture.
- `.planning/PROJECT.md` — runtime-authority rule, accepted hosted-model exposure, local-backend requirement, degrade-never-block constraint.

### Cross-phase context
- `.planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md` — permitted-tier state, explicit stumped unlock path, and authored fallback.
- `.planning/phases/07-selection-engine/07-CONTEXT.md` — selection remains rule-based; the model never selects items.
- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — append-only evidence and human-only accepted marking.
- `.planning/research/2026-08-09-landscape-widening.md` — study-mode wave: the visible runtime lock is the differentiator.
- `.planning/research/2026-08-09-blind-spots.md` §B14 — degraded-model UX.
- `.planning/research/2026-08-10-tiered-verdicts.md` and `.planning/research/2026-08-10-enforcement-and-loose-threads.md` — tier-3 verdict evidence (non-reproducibility, bias, Ofqual) and enforcement shape.
- `.planning/PLANNING-DIRECTIVES.md` and `.planning/POST-RESEARCH-PROMPTS-2026-08-10.md` — round-two directives (hosted-first, bench honesty, no invented figures).

### Code seams
- `evidence.py` — mark events, `mark_event(rubric=...)` booleans, review-state derivation, response linkage, event storage.
- `runtime.py` — answer-key withholding, explanation boundaries, `public_item()`/`explain_payload()`.
- `model.py` — key, distractor analysis, model answer, and rubric source fields.
- `schemas/settings.schema.json` — existing inert `model_backend` contract and profile extension point.
- `schemas/response.schema.json` — pending review and model-interaction extension points.
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/INTEGRATIONS.md`, and `.planning/codebase/TESTING.md` — layer boundaries, external-process/network seams, and cross-platform tests.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 6's tier state is the sole authority input to the gate.
- `evidence.mark_event()` already separates pending short responses from accepted human marks and stores per-criterion booleans.
- Settings already reserve `model_backend`; daemon and CLI already share runtime paths.
- `schema_validate.py` already rejects unknown schema keywords, so strict bounded-plan validation is enforceable with existing tooling.

### Established Patterns
- External capability degrades to an omission, never blocks core study.
- Private payloads remain server-side; browser responses are constructed explicitly.
- Append-only events preserve proposals and later acceptance separately.
- Registries (TTSEngine precedent in Phase 9.1) are the house style for adding a backend.

### Integration Points
- New provider-neutral adapter and tier-gate modules beside `runtime.py`.
- `surfaces/settings.py` and settings schema for backend profiles.
- Phase 6 hint path for optional generated augmentation.
- Evidence/schema additions for interaction and pending rubric proposal events.
- Adversarial gate tests plus hosted-CLI/local-endpoint contract fixtures.
</code_context>

<specifics>
## Specific Ideas

The planning model should treat leakage prevention as this phase's hardest deliverable and combine compatible defenses where they improve coverage. Provider plumbing is secondary and must not create a false sense that prompt instructions enforce the tier. The learner-facing refusal is a structural lock with the unlock condition stated — never model voice (Weibao's standing directive: build the most comprehensive, future-selectable design; conflict → implement all safe options and let the user choose later).
</specifics>

<deferred>
## Deferred Ideas

- Model-authored bank changes and retry-to-clean authoring — Phase 11.
- Model-driven selection — out of scope; selection remains rule-based.
- Accepted automated scoring of prose — explicitly out of scope (tier-3 stays a peer of the human marker, never accepted evidence).
- A validated local-model benchmark — `itembank bench` after the 7900 XTX hardware lands; no invented figures before then.
</deferred>

---

*Phase: 8-model-adapter-interface-tier-gate-enforcement*
*Context updated: 2026-08-10*
