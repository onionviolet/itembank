# Phase 6: Hint Ladder, Cursor-Hold & Feedback Modes - Research

**Researched:** 2026-08-08  
**Domain:** Runtime-owned adaptive teaching loop, bounded feedback, and append-only learning evidence  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)

- Model-written, error-specific hints and semantic leakage defense — Phase 8.
- Visual styling of the ladder — Phase 4/UI design work.
- Evidence-driven item selection — Phase 10 through the Phase 7 selector seam.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TEACH-01 | A wrong answer holds the session cursor instead of advancing, so a second attempt is possible | Runtime transition returns an action; only the policy moves the cursor. |
| TEACH-02 | A `hint` command and route return the next tier: lesson pointer, objective, trap, the rationale for the option actually picked, the discriminator, then the reveal | Ordered authored-tier resolver and one structured hint payload. |
| TEACH-03 | Hints used are recorded per response, so "right at tier 1" and "right at tier 4" are different outcomes in `report` | Immutable response snapshots plus append-only hint events; report derives, rather than trusts a counter. |
| MODE-01 | Feedback policy is a property of the session mode, chosen per sitting | Mode-keyed runtime policy table; selection mode remains separate. |
| MODE-02 | Drill mode reveals the correct answer and explanation immediately on a wrong answer, then advances | Drill transition emits a reveal-and-advance action without ladder state. |
| MODE-03 | Practice mode runs the hint ladder with the cursor held, revealing at the final tier | Practice transition preserves cursor, then exposes one unlocked authored tier. |
| MODE-04 | Diagnostic mode gives no feedback until the sitting ends | Diagnostic response records evidence but returns deferred feedback only at completion. |
| MODE-05 | Exam mode gives no feedback until the attempt file is marked | Exam response records evidence but permits no learner feedback before an accepted mark. |
| MODE-06 | The mode used is recorded with every response | Existing response event already carries a mode; Phase 6 must preserve it through retries. |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Try simple troubleshooting first: use account-selection URL parameters for the wrong Google account, use an in-page Refresh before a full reload, and try navigation/waiting before escalating rendering issues. [VERIFIED: AGENTS.md]

## Summary

Build Phase 6 as two coarse vertical slices around one runtime-owned teaching transition: receive a learner action, canonicalize and score it, decide the permitted next action from immutable session state and feedback mode, append evidence, then return a renderer-neutral payload. This is the project’s differentiator: visual/canvas clients may show state, collect a prediction, highlight the learner’s move, and render the returned hint, but they do not grade, select a tier, advance the cursor, or receive withheld content. Existing `runtime.score_response()` is the only scorer and returns `None` for manual-review responses, while `public_item()` exposes only pre-answer material. [VERIFIED: runtime.py:27-48,120-130]

Use Brilliant as a pedagogical benchmark, not an implementation target: its official description emphasizes a pretest before explanation, hands-on visual manipulation, and immediate custom feedback; its tutor can observe and interact with the learning environment while guiding rather than answering. [CITED: https://brilliant.org/about/] [CITED: https://brilliant.org/help/features/] Phase 6 should adopt that loop as **diagnose → teach one bounded next move → learner prediction/action → observe → bounded feedback → append evidence**. It must not adopt Brilliant’s subscriptions, accounts, streaks, XP, leaderboards, hosted analytics, or adaptive selection, all of which are out of scope or belong to later phases. [VERIFIED: .planning/PROJECT.md]

**Primary recommendation:** Implement exactly two vertical plans: (1) the versioned policy/evidence/reporting core with exhaustive transition tests; (2) one CLI/API/browser integration that consumes the same transition and supports interactive-renderer observations without granting renderer authority. [HIGH: synthesized from locked context and codebase]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Canonical learner action and deterministic score | API / Backend | — | The existing runtime owns canonicalization and its sole scorer. [VERIFIED: runtime.py:70-130] |
| Feedback mode, cursor state, tier gate, and reveal decision | API / Backend | Database / Storage | These must survive resume and remain identical for CLI, daemon, browser, and future canvas clients. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:18-46] |
| Authored tier lookup and response-specific distractor context | API / Backend | Database / Storage | The runtime is entitled to access the private explanation half; the browser is not. [VERIFIED: runtime.py:258-279] |
| Append-only response and hint evidence | Database / Storage | API / Backend | The evidence module is the single writer and derives live views from non-retracted events. [VERIFIED: evidence.py:398-415,996-1011] |
| Progressive ladder, stumped control, immediate feedback, and visual/canvas highlighting | Browser / Client | API / Backend | A renderer presents explicit runtime actions and returns its canonical learner action/observation; it does not infer policy. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:18-31] |
| Session policy selection | API / Backend | Browser / Client | The client chooses a mode only at sitting start; the runtime stores it and rejects mid-sitting relabeling. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:33-38] |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Existing Python standard library runtime | Python 3.13.5 available | Policy transition, versioned JSON sessions, JSONL evidence, daemon routes | Project constraint forbids external dependencies; the current implementation already uses standard-library JSON and filesystem primitives. [VERIFIED: runtime.py:144-185] [VERIFIED: `python --version`] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Existing inline browser JavaScript | project-local | Render structured payloads and post learner actions | Only as a client of the daemon/runtime contract; never as a scorer or tier gate. [VERIFIED: surfaces/daemon.py:839-867] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Runtime policy engine | Per-surface CLI/HTTP/browser branches | Rejected: would violate the locked one-policy-engine decision and make feedback behavior diverge. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:18-21] |
| Renderer-neutral action payload | Canvas-specific feedback logic | Rejected: a future interactive renderer needs to participate in the loop without owning scoring or disclosure. [CITED: https://brilliant.org/help/features/] |
| Append-only hint events | Mutable `hints_used` counter | Rejected: mutable summaries lose auditability and cannot distinguish exposure from state. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:40-43] |

**Installation:** None. Do not add dependencies. [VERIFIED: .planning/PROJECT.md]

## Architecture Patterns

### System Architecture Diagram

```text
CLI / browser / future interactive canvas
      │ canonical learner action + optional renderer observation
      ▼
session adapter ──► runtime teaching transition ──► score_response
                         │                         │
                         │                         └─ deterministic verdict
                         ▼
              mode policy + authored tier resolver
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
  cursor action      permitted payload   append-only events
       │                 │                  │
       └───── surface renders only ◄────────┴───── report derives outcomes
```

The primary input/output boundary is deliberately renderer-neutral: a canvas may serialize its completed manipulation as the normal response shape and may send a compact observation that helps choose presentation, but it may not submit a score or requested tier. The teaching transition evaluates the response through the existing canonicalizer/scorer, returns the action allowed by the stored session mode, and is the only component allowed to select private tier content. [VERIFIED: runtime.py:70-130,258-279] [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:18-31]

### Recommended Project Structure

Keep the existing four-layer layout. Add the policy and authored-tier resolver beside the existing session runtime, extend the evidence module/schema as one contract change, and expose it through the current CLI/daemon adapters. The exact function and field names are planner discretion. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:45-46]

### Pattern 1: Explicit runtime transition

**What:** One pure-ish transition function returns an action plus public payload; adapters persist the returned state and render it.

**When to use:** Every `submit`, `hint`, `stumped`, completion, and accepted mark path.

**Example:**

```python
# Existing primitives: runtime.py:70-130
def teaching_transition(session, item, response, request):
    canonical = canonical_response(item, response)
    verdict = score_response(item, response)
    return policy_transition(session, item, canonical, verdict, request)
```

The existing primitives normalize a response before canonicalizing it, preserve manual-review as `None`, and centralize correctness in `score_response`. [VERIFIED: runtime.py:51-57,70-100,120-130]

### Pattern 2: Observe, do not authorize

**What:** Interactive/canvas renderers may send a canonical answer and a non-authoritative observation such as selected objects, attempted arrangement, or prediction state. The runtime may use it to select the response-specific authored hint, but all authorization remains server-side. [CITED: https://brilliant.org/help/features/]

**When to use:** A visual renderer needs targeted feedback or highlight coordinates after a learner action.

**Contract:** The response is canonicalized by the runtime; the observation is optional, schema-bounded, and cannot cause a higher tier, a cursor advance, a correct score, or disclosure. This preserves Phase 6 for current items while leaving an integration seam for Phase 06.1 and Phase 9. [HIGH: synthesized from locked context]

### Pattern 3: Evidence is an event stream, report is a view

**What:** Append a response snapshot and one event for every newly shown hint; reconstruct `hints_used` and learning outcomes from live events. [VERIFIED: evidence.py:398-415,996-1011]

**When to use:** Every genuine response, stumped action, new tier shown, accepted mark, report, and resume.

### Competitor-pattern comparison

| Benchmark | Borrow | Do not copy | Phase 6 implication |
|-----------|--------|-------------|----------------------|
| Brilliant | Ask before explaining; visual manipulation; immediate targeted feedback; tutor can see the active interactive. [CITED: https://brilliant.org/about/] [CITED: https://brilliant.org/help/features/] | Hosted tutor authority, gamification, accounts, telemetry, or black-box adaptation. | Pass renderer state as observation, but make the runtime issue a bounded action/payload. |
| Khanmigo / Khan Academy | A tutor should prompt the learner to do the work; its own feedback rubric treats giving the direct answer as a failure. [CITED: https://support.khanacademy.org/hc/en-us/articles/13983335341069-How-do-I-leave-feedback-about-Khanmigo] | Prompt-only leakage control. | Make the “do not reveal” guarantee executable through tier-gated private data, not prose instructions. |
| Amplify Desmos Math | Make learner thinking visible and respond to it with targeted feedback. [CITED: https://amplify.com/programs/amplify-desmos-math/] | Classroom/teacher orchestration and hosted analytics. | Preserve response/observation and hint events as inspectable local evidence. |
| ALEKS | Separate knowledge assessment from later adaptation. [CITED: https://www.mheducation.com/prek-12/support/knowledge/what-is-a-knowledge-check.html] | A fitted adaptive learner model in this phase. | Keep Phase 6 bounded to feedback; selection/adaptation stays with Phases 7 and 10. |

### Anti-Patterns to Avoid

- **Browser decides correctness or tier:** it turns every new renderer into a second scorer/gate and leaks private answer data. Use the returned runtime action instead. [VERIFIED: runtime.py:120-130,258-279]
- **Every wrong submission unlocks a hint:** empty and duplicate answers become a disclosure bypass. Use canonical distinctness and evidence dedupe before progressing. [VERIFIED: evidence.py:439-472] [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:23-26]
- **Tier content slides into an earlier missing tier:** missing authored content becomes accidental answer leakage. Represent unavailable content at its own fixed tier. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:28-31]
- **Mode as UI decoration:** diagnostic/exam leakage cannot be repaired after it is shown. Enforce policy in the runtime transition and test payload absence. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:33-38]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Answer equivalence | A Phase-6-specific equality test | `canonical_response()` | It already handles each existing item type and defines the scorer’s comparison form. [VERIFIED: runtime.py:70-117] |
| Correctness | A browser/canvas score | `score_response()` | It is explicitly the only scorer and preserves manual-review `None`. [VERIFIED: runtime.py:120-130] |
| Replay detection | A UI click counter | `attempt_number()` plus `append_event()` | Existing distinct-canonical and dedupe semantics survive crashes and retries. [VERIFIED: evidence.py:398-415,439-472] |
| Hint-use count | A mutable session counter | Derived live hint events | Evidence remains auditable and retractions remain respected. [VERIFIED: evidence.py:996-1011] |
| Page-specific disclosure rules | Conditional rendering of private fields | Runtime action/payload boundary | The private explanation payload is already explicitly separated from public item data. [VERIFIED: runtime.py:27-48,258-279] |

**Key insight:** The difficult part is not rendering hints. It is retaining one authoritative transition while making each interaction observable and reconstructable later. [HIGH: synthesized from codebase and locked decisions]

## Common Pitfalls

### Pitfall 1: Advancing the cursor before policy resolution

**What goes wrong:** The current session submit path increments the cursor after every response; copying it into practice mode would make a real retry impossible. [VERIFIED: surfaces/session.py:111-152]

**How to avoid:** Evaluate the policy transition before mutating cursor/status; persist the returned next state only once evidence append succeeds or replay recovery is resolved. [HIGH: synthesized from existing submit/evidence ordering]

### Pitfall 2: Breaking schema readers with a new event type or field

**What goes wrong:** The event reader skips unknown event types, while the response schema currently closes additional properties and reserves `hint_tier` as null. [VERIFIED: evidence.py:418-436] [VERIFIED: schemas/response.schema.json:8-14,88-94]

**How to avoid:** Version the session and response/hint contracts together; add the hint event to the known-event set and schema fixtures in the same vertical slice. Quote of existing values: `"response", "retraction", "mark", "day_tick"`. [VERIFIED: evidence.py:38-43]

### Pitfall 3: Treating a pending `short` answer as wrong

**What goes wrong:** `score_response()` deliberately returns `None` for constructed response, not `False`; a hint ladder must not fabricate a misconception before review. [VERIFIED: runtime.py:120-130]

**How to avoid:** Return a pending/hold-for-mark transition that neither advances the ladder nor releases feedback. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:23-26]

### Pitfall 4: Treating “no feedback” as “do not record”

**What goes wrong:** Diagnostic and exam sessions still need response evidence, mode, and eventual review state; withholding the payload is not permission to discard the event. [VERIFIED: schemas/response.schema.json:9-14,59-77]

**How to avoid:** Append the normal response event first, then emit the mode-specific public action with no correctness, hint, explanation, or key. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:33-42]

### Pitfall 5: Letting a visual renderer become authority

**What goes wrong:** A canvas can make an answer feel self-evident but cannot safely own correctness, tier gating, or disclosure; the next renderer would then fork learning policy. [CITED: https://brilliant.org/help/features/]

**How to avoid:** Treat renderer output as learner action plus optional observation. It may render highlight instructions in the permitted payload, never decide which payload is permitted. [HIGH: synthesized from locked architecture]

## Code Examples

Verified patterns from the existing runtime:

### Score before policy, not in the renderer

```python
# Source: runtime.py:70-130
canonical = canonical_response(item, learner_action)
verdict = score_response(item, learner_action)
transition = policy_transition(session, item, canonical, verdict, request)
```

The current canonicalizer and sole scorer are the verified reusable primitives; `policy_transition` is a proposed Phase 6 function name only. [VERIFIED: runtime.py:70-130] [ASSUMED: exact Phase 6 function name]

### Renderer integration boundary

```text
renderer action/observation → runtime transition → permitted public payload → renderer display
```

The arrow represents the proposed integration contract, not a new client-side authority. [HIGH: synthesized from locked context]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Answer then automatically advance | Explicit action-driven teaching transition | Phase 6 | Enables retry, bounded scaffold, deliberate stumped action, and mode-specific feedback. [VERIFIED: surfaces/session.py:111-152] [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:18-43] |
| Prompt a tutor not to reveal | Runtime withholds private data and permits only a bounded tier | Phase 6/8 boundary | Gives an auditable technical guarantee rather than a conversational preference. [CITED: https://support.khanacademy.org/hc/en-us/articles/13983335341069-How-do-I-leave-feedback-about-Khanmigo] [VERIFIED: runtime.py:258-279] |
| Renderer receives a complete explanation after submit | Renderer receives a policy-selected payload | Phase 6 | Enables visual manipulation and targeted feedback without leaking future tiers. [CITED: https://brilliant.org/about/] |

**Deprecated/outdated:** Per-surface advancement and explanation logic is incompatible with the Phase 6 invariant of one runtime policy. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:18-21]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The planner can keep the exact Phase 6 policy function and new JSON field names open while preserving the locked behavior. | Architecture Patterns / Code Examples | Low; context explicitly delegates names/layout, but contracts must be finalized before implementation. |
| A2 | A future interactive renderer can serialize its learner manipulation in the existing response shape plus an optional bounded observation. | Pattern 2 | Medium; Phase 06.1 must define visual-item response schemas before a concrete canvas item is implemented. |

## Open Questions

1. **What exact public schema carries an optional renderer observation/highlight target?**
   - What we know: the current session and response contracts are versioned and closed; renderer authority is forbidden. [VERIFIED: schemas/session.schema.json:5-11] [VERIFIED: schemas/response.schema.json:7-14]
   - What's unclear: Phase 06.1 has no context artifact yet, so there is no visual-item canonical state contract to reuse.
   - Recommendation: make Phase 6 renderer-neutral and additive; define a concrete visual response/observation schema only in Phase 06.1, with a compatibility test proving it still reaches `canonical_response()` and `score_response()`. [ASSUMED]

2. **What exact Phase 3 lesson-pointer resolver is available at execution time?**
   - What we know: Phase 6 depends on Phase 3 and tier 0 is a lesson pointer. [VERIFIED: .planning/ROADMAP.md:321-335]
   - What's unclear: Phase 3 has context but is not yet marked complete in the roadmap.
   - Recommendation: plan the tier resolver against Phase 3’s public lesson link contract and include a fixture-backed integration check; do not recreate lesson parsing in Phase 6. [ASSUMED]

## Environment Availability

No external dependency is required. Python is available as `Python 3.13.5`; Phase 6 remains stdlib-only and offline-capable. [VERIFIED: `python --version`] [VERIFIED: .planning/PROJECT.md]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Direct standard-library roundtrip scripts (no framework dependency). [VERIFIED: README.md:354-357] |
| Config file | none — scripts run directly. [VERIFIED: README.md:354-357] |
| Quick run command | `python tests/hint_roundtrip.py` [ASSUMED: Wave 0 file to create] |
| Full suite command | `python tests/evidence_roundtrip.py` plus `python tests/daemon_roundtrip.py` plus `python tests/protocol_roundtrip.py` plus `python tests/agent_roundtrip.py` plus `python tests/scoring_roundtrip.py` [ASSUMED: direct-script aggregate] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TEACH-01 | Wrong practice answer holds cursor; correct retry advances | integration | `python tests/hint_roundtrip.py` | ❌ Wave 0 |
| TEACH-02 | Fixed ordered tiers; unavailable tier does not shift; response-specific tier changes with genuine answer | integration | `python tests/hint_roundtrip.py` | ❌ Wave 0 |
| TEACH-03 | Hint events and response snapshots distinguish tier reached | integration | `python tests/hint_roundtrip.py` | ❌ Wave 0 |
| MODE-01..06 | Four feedback policies, mode evidence, no mid-session change | integration | `python tests/hint_roundtrip.py` | ❌ Wave 0 |
| SC6 | Interactive action/prediction receives bounded targeted payload, not a client-side verdict | API smoke | `python tests/hint_roundtrip.py` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python tests/hint_roundtrip.py` [ASSUMED: Wave 0 file to create]
- **Per wave merge:** Run the Phase 6 script plus evidence, daemon, protocol, agent, and scoring roundtrips. [ASSUMED]
- **Phase gate:** Full targeted suite green before `$gsd-verify-work`. [VERIFIED: .planning/config.json]

### Wave 0 Gaps

- [ ] `tests/hint_roundtrip.py` — all four modes, resume, duplicate/empty replay, stumped action, unavailable fixed tiers, null-vs-zero evidence, and visual-renderer contract smoke test. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:82-88]
- [ ] Extend schema roundtrip coverage for the new response/event/session versions and known hint event. [VERIFIED: schemas/response.schema.json:8-14] [VERIFIED: schemas/session.schema.json:5-11]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Local single-user tool; no account/auth capability is introduced in Phase 6. [VERIFIED: .planning/PROJECT.md] |
| V3 Session Management | yes | Server resolves `session_id` through an allowlist/index rather than treating it as a path. [VERIFIED: surfaces/daemon.py:764-794,816-867] |
| V4 Access Control | yes | Only the runtime accesses private explanation fields and selects what reaches a client. [VERIFIED: runtime.py:258-279] |
| V5 Input Validation | yes | Normalize/canonicalize answer data and reject unknown session IDs; validate any new action/observation shape before it reaches policy. [VERIFIED: runtime.py:51-57,70-100] [VERIFIED: surfaces/daemon.py:839-867] |
| V6 Cryptography | no | No new cryptographic feature; existing evidence hashes are not a security boundary. [VERIFIED: evidence.py:1-20] |

### Known Threat Patterns for the teaching loop

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Hint-tier or answer leakage through browser/canvas state | Information disclosure | Send only `public_item()` before response; policy selects bounded payload after transition. [VERIFIED: runtime.py:27-48,258-279] |
| Empty/duplicate submission farms hints | Tampering | Canonical distinctness, attempt numbering, and append dedupe precede tier progression. [VERIFIED: evidence.py:398-415,439-472] |
| Mode tampering mid-sitting | Tampering | Persist mode in versioned session and reject mode changes; start a new sitting instead. [VERIFIED: schemas/session.schema.json:8-55] [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:33-38] |
| Guessable user input becomes a filesystem path | Elevation / tampering | Continue daemon allowlist resolution; never join client session/bank identifiers into paths. [VERIFIED: surfaces/daemon.py:764-794,816-867] |
| Incorrect claim that a pending manual response is wrong | Integrity | Preserve scorer `None` and wait for an accepted mark event. [VERIFIED: runtime.py:120-130] |

## Sources

### Primary (HIGH confidence)

- [runtime.py](/C:/Users/wayba/Downloads/CTF/itembank/runtime.py:70) - canonical response, sole scorer, public/private payload boundary, and session upgrade mechanism.
- [evidence.py](/C:/Users/wayba/Downloads/CTF/itembank/evidence.py:398) - single evidence writer, dedupe semantics, and live-event derivation.
- [Phase 6 context](/C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:18) - locked policy, hint, evidence, and no-leakage decisions.
- [Brilliant: Our Method](https://brilliant.org/about/) - official current description of pretest-first interactive learning and custom feedback.
- [Brilliant: Product Features](https://brilliant.org/help/features/) - official current description of tutor interaction with active learning components.

### Secondary (MEDIUM confidence)

- [Khan Academy: Khanmigo feedback guidance](https://support.khanacademy.org/hc/en-us/articles/13983335341069-How-do-I-leave-feedback-about-Khanmigo) - direct answers are explicitly undesirable tutor behavior.
- [Amplify Desmos Math](https://amplify.com/programs/amplify-desmos-math/) - official responsive-feedback and visible-thinking pattern.
- [McGraw Hill: ALEKS Knowledge Checks](https://www.mheducation.com/prek-12/support/knowledge/what-is-a-knowledge-check.html) - official assessment/adaptation boundary.

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — no new package; existing standard-library runtime and project constraint are direct sources.
- Architecture: HIGH — locked context specifies ownership and existing code verifies seams.
- Pedagogy/competitor patterns: MEDIUM — current official public product descriptions, used as inspiration rather than evidence of efficacy.
- Pitfalls: HIGH — direct current implementation and schema behavior.

**Research date:** 2026-08-08  
**Valid until:** 2026-09-07 for codebase findings; recheck public product pages before any later design review.
