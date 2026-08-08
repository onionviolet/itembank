# Phase 6: Hint Ladder, Cursor-Hold & Feedback Modes - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase supplies one runtime-owned feedback-policy state machine for all sitting surfaces. It holds or advances the cursor, exposes the six authored hint tiers in order, records how far the learner needed to go, and makes drill, practice, diagnostic, and exam feedback materially different. It does not generate model hints (Phase 8), select items (Phase 7), or redesign the surfaces (Phase 4).

</domain>

<decisions>
## Implementation Decisions

The user delegated all remaining decisions under a standing rule: choose the most useful and comprehensive design, preserve multiple future choices when they can coexist without lowering quality, and continue autonomously unless a choice is harmful or genuinely one-way.

### One feedback-policy state machine
- **D-01:** Feedback behavior is represented by one runtime policy table/state machine keyed by the existing feedback `mode`; CLI, daemon, and browser surfaces are clients. `selection_mode` remains a separate Phase 7 axis and must never silently alias feedback mode.
- **D-02:** The state machine returns explicit actions (`hold`, `advance`, `reveal_tier`, `defer_feedback`, `complete`) rather than letting each surface infer behavior. This preserves one behavior across every surface.
- **D-03:** Session state records attempt count, highest tier unlocked, highest tier shown, and the canonical form of the last genuine response per item. These are versioned session fields, not UI state. — **Reversibility:** costly — changing the state shape later touches session upgrades, evidence, every sitting client, and resumability.

### Genuine attempts and cursor behavior
- **D-04:** In practice mode, a wrong auto-scorable response holds the cursor. A materially different, non-empty canonical response is a genuine attempt; an empty response, an identical canonical resubmission, or a replay with the same dedupe key is idempotent and unlocks nothing.
- **D-05:** Each genuine wrong attempt can unlock at most one additional tier. The first wrong attempt makes tier 0 available; later genuine attempts make tiers 1–5 available in order. Practice mode also exposes an explicit **stumped** action: it unlocks and shows exactly the next tier without requiring a performative wrong submission. Empty or duplicate answer spam still unlocks nothing. This keeps the ladder useful rather than punitive while making bypass intentional and observable.
- **D-06:** A correct retry records the tier reached and advances. Tier 5 is the authored reveal; after it has been shown, the next action advances without manufacturing further attempts. Manual-review `short` responses remain pending and do not pretend to be wrong while awaiting a mark.

### Hint presentation and contract
- **D-07:** `hint` returns a structured payload containing the newly shown tier, the accumulated shown tiers, a stable tier name, and how it was unlocked (`attempt` or `stumped`). CLI supports an explicit `--stumped`/equivalent action; the app presents a clearly labeled “I’m stumped — show the next hint” control. The app may render the accumulated ladder as a progressive stack. All surfaces consume the same payload.
- **D-08:** The fixed ladder is: lesson pointer, objective, trap, rationale for the learner's picked option, discriminator, reveal. Missing authored content produces an explicit unavailable tier and continues safely; it never shifts later content into an earlier tier.
- **D-09:** Tier 3 is response-specific: it uses the distractor analysis for the most recent genuine picked option. Changing the answer changes the relevant tier-3 payload but does not erase previously shown evidence.

### Feedback modes
- **D-10:** Drill scores once, immediately returns the correct answer and explanation after a wrong response, records the mode, and advances. It does not walk the ladder.
- **D-11:** Practice uses D-04 through D-09: held cursor, attempt-gated ladder, reveal at tier 5, then advance.
- **D-12:** Diagnostic records responses while returning no correctness, hints, or explanations. Deferred feedback becomes available only when the sitting is complete, as one runtime-generated review payload.
- **D-13:** Exam records responses while returning no feedback. Feedback remains withheld until an explicit accepted mark event exists for the attempt; merely reaching the final item is insufficient.
- **D-14:** Mode changes are not allowed mid-sitting. Starting another sitting is the reversible way to choose another policy, preventing evidence produced under one policy from being relabeled as another.

### Evidence and reporting
- **D-15:** Every genuine response event records feedback mode and the highest hint tier actually shown at submission time; `null` continues to mean the ladder did not apply or no tier existed, while `0` means tier 0 was shown. This preserves Phase 1's null-vs-zero distinction. — **Reversibility:** one-way — append-only evidence cannot recover a tier that was not recorded.
- **D-16:** Each newly shown hint is also an append-only `hint` event linked to session, response/attempt, item, tier, source (`authored`), and unlock path (`attempt` or `stumped`). Reports derive `hints_used` from these events rather than trusting a mutable counter.
- **D-17:** Reports distinguish first-try correct, correct after N genuine attempts, correct after tier T, learner-declared stumped at tier T, revealed, and unresolved. They do not collapse these into one accuracy number or treat using the stumped control as a wrong answer.

### Codex's Discretion
All decisions above are delegated design choices. The planning model may improve exact field names and payload layout, but must preserve the invariants: one policy engine, attempt-gated progression, separate feedback/selection axes, append-only evidence, and no feedback leakage in diagnostic or exam mode.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/ROADMAP.md` § "Phase 6: Hint Ladder, Cursor-Hold & Feedback Modes" — phase boundary and five success criteria.
- `.planning/REQUIREMENTS.md` § "Teaching" (TEACH-01 through TEACH-03) and § "Feedback modes" (MODE-01 through MODE-06) — binding behavior.
- `.planning/PROJECT.md` — core rule that the runtime, not a model or browser, decides what reaches the learner.
- `.planning/phases/03-lesson-format-in-app-reader/03-CONTEXT.md` — tier-0 lesson pointer and item↔lesson link.
- `.planning/phases/07-selection-engine/07-CONTEXT.md` — distinct `selection_mode` decision and existing feedback-mode collision.
- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — append-only event and idempotency contracts.
- `runtime.py` — central scorer, public/private payload separation, and session upgrades.
- `evidence.py` — response event, reserved `hint_tier`, dedupe, live-event reads, and mark events.
- `schemas/response.schema.json` and `schemas/session.schema.json` — published contracts requiring versioned changes.
- `surfaces/session.py`, `surfaces/daemon.py`, and `surfaces/quiz_page.py` — current submit, route, and rendering clients.
- `.planning/codebase/ARCHITECTURE.md` and `.planning/codebase/CONVENTIONS.md` — one-runtime layering and direct roundtrip-test patterns.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `runtime.score_response()` and canonical-response helpers define genuine answer equivalence.
- Evidence dedupe keys and `live_events()` provide replay resistance and append-only derivation.
- Phase 3's lesson deep link supplies tier 0 without new lesson logic.

### Established Patterns
- One scorer and one evidence store; this phase adds one feedback-policy engine.
- State is passed or persisted in versioned JSON, never owned by browser code.
- Missing optional capability degrades explicitly instead of guessing.

### Integration Points
- `runtime.py`: feedback transition function and session upgrade.
- `evidence.py`: hint event and tier-bearing response event.
- `surfaces/session.py`: `hint` CLI path and held-cursor submit.
- `surfaces/daemon.py`: hint route and mode-safe submit response.
- `schemas/*.json`: session, response, and hint event contracts.
- `tests/hint_roundtrip.py`: all four modes, resume, duplicate/empty spam, and null-vs-zero evidence.

</code_context>

<specifics>
## Specific Ideas

Preserve future UI freedom by returning structured transition and hint payloads. A more capable UI-planning model can later choose progressive cards, a compact rail, or another presentation without changing pedagogy or evidence. The stumped control should feel like a legitimate learning action, not a failure-state warning or hidden escape hatch.

</specifics>

<deferred>
## Deferred Ideas

- Model-written, error-specific hints and semantic leakage defense — Phase 8.
- Visual styling of the ladder — Phase 4/UI design work.
- Evidence-driven item selection — Phase 10 through the Phase 7 selector seam.

</deferred>

---

*Phase: 6-hint-ladder-cursor-hold-feedback-modes*
*Context gathered: 2026-08-08*
