---
phase: 08
slug: model-adapter-interface-tier-gate-enforcement
status: approved
reviewed: 2026-08-08
shadcn_initialized: false
preset: none
created: 2026-08-08
---

# Phase 8 — UI Design Contract: Model Adapter and Tier-Gate Enforcement

> Phase 8 adds optional, subordinate assistance. The learner's activity, authored hint ladder, runtime verdict, and human-mark path remain fully usable without it. `08-AI-SPEC.md` now supplies the upstream AI/evaluation contract; no generated learner UI may be marked complete until the Phase 6 fact seam and adversarial verification evidence are green.

## Authority and Decision Legend

| Label | Meaning and source |
|---|---|
| **LOCKED** | Phase 8 CONTEXT D-01…D-17, REQUIREMENTS TEACH-04…09/MODEL-01…05, Phase 6 policy, or shared UI-SPEC. |
| **UPSTREAM-CONTRACT** | Typed interface/schema/evidence seam is required before any consumer renders it. |
| **UI-DEPENDENT** | Adapter/gate may be built, but a visible surface needs this contract and shared shell/a11y rules. |
| **UI-BLOCKED** | Learner-facing generated content is blocked pending `08-AI-SPEC.md`, a Phase 6 permitted-tier/fact-manifest seam, and adversarial gate evidence. |
| **UI-INDEPENDENT** | Profile resolution, transport, bounded request/result normalization, schema/gate/evidence tests can proceed. |
| **OPEN** | Do not ship a UI behavior; retain only a seam or explicit unavailable state. |

**Authority boundary — LOCKED:** a provider-native response is untrusted data. Only a typed `pass`, `drop`, or `unavailable` result reaches the UI. The runtime chooses permitted tier and uses private item/key/facts; browser receives neither. A model never scores structured work, chooses an item, advances a tier, writes accepted evidence, or exposes dropped text.

## Goal and Plan-Gating Matrix

| Work | Classification | Gate / exit evidence |
|---|---|---|
| Versioned adapter request/result, profiles, hosted CLI/local HTTP normalization | **UPSTREAM-CONTRACT / UI-INDEPENDENT** | Same typed outcome for fixture subprocess and loopback endpoint; configuration-only switch; bounded time/output; no secret in evidence. |
| Tier-manifest builder and deterministic gate | **UPSTREAM-CONTRACT / UI-INDEPENDENT** | Strict no-unknown-field plan, manifest reference resolution, higher-tier/key/ambiguity corpus all `drop`; no rewrite of suspect output. |
| Interaction/proposal evidence and human mark separation | **UPSTREAM-CONTRACT / UI-INDEPENDENT** | Every attempt logged; pass content only if safe; short proposal remains pending; human `mark` is sole accepted-evidence path. |
| Generated hint panel / lifecycle notices | **UI-BLOCKED** | Required `08-AI-SPEC.md`, Phase 6 callable tier/fact seam, adversarial gate suite, authored fallback and no-leak DOM tests. |
| Reviewer rubric-proposal pane | **UI-DEPENDENT** | Pending-only typed proposal, per-rubric-point evidence, actor-confirmed existing mark path, reviewer authorization/surface plan. |
| Freeform tutor/chat or raw provider text/audit transcript | **OPEN / do not build** | Requires separate security, retention, disclosure, and UI decision; current phase must not expose it. |

## Design System, Information Architecture, and Tokens

| Property | Contract |
|---|---|
| Tool / registry | None; stdlib Python + native HTML/CSS/JS. No external UI package or third-party registry. |
| Position | `AgentAssist` is contextual, collapsed by default, and subordinate to `ActivityCanvas`; never a chat-first/full-screen shell. |
| DOM order | Activity/prompt → response/hint ladder → status → collapsed `Help and evidence` → optional AgentAssist. Visual placement may be side panel on desktop but DOM is unchanged. |
| Source labeling | Every rendered generated augmentation says `Generated support` and declares `Author-provided`, `Generated support`, or `Unavailable`; citations/provenance never imply a provider is a source. |
| Motion | Static `Thinking…` status, no simulated typing; 150ms maximum and immediate state at reduced motion. |

Use the shared Phase 4 token contract: spacing 4/8/16/24/32/48/64; typography 12/16/20/32px with line heights 1.4/1.5/1.2/1.1 and only 400/600 (`--weight-normal` / `--weight-emphasis`, per the UI-SPEC §7 weight ruling of 2026-08-10); `--bg` 60%, `--card/--chip/--line` 30%, accent 10% for focus/explicit primary action/source links only; semantic `--ok/--bad/--warn/--unknown/--pending` with text and icon/structure. Generated availability, policy drop, and pending review must never use correctness colors alone.

## Annotated Wireframes

### Desktop (≥1024px)

```text
┌ ContextLine: lesson · objective · progress · feedback mode ───────────────┐
├──────── ActivityCanvas (2/3; first in DOM) ──────┬ AgentAssist (1/3) ─────┤
│ prompt / answer / authored shown tiers           │ [Help and evidence ▾]  │
│ [I’m stumped — show next hint]                   │ status: Available /…   │
│ [Check answer]                                   │ Generated support      │
│ persistent runtime status                         │ tier-safe template     │
│                                                   │ source/provenance ▸    │
└──────────────────────────────────────────────────┴────────────────────────┘
```

The support column follows activity in DOM. It never supplies an answer/action unavailable in the main activity and never displays a model “score.”

### Tablet (768–1023px)

```text
Activity → authored ladder / answer → runtime status
<details><summary>Help and evidence</summary>
  generated-support lifecycle, provenance, retry (when legal)
</details>
```

### Narrow (320–767px and 200% zoom)

```text
Activity and authored fallback stay first
Generated-support disclosure follows status; full-width controls
Lifecycle notice + source/provenance details; no overlay, no page x-scroll
```

## Lifecycle State Machines

### Generated hint request

```text
AUTHORED_READY → REQUESTED → THINKING → GATE_CHECK
GATE_CHECK → PASS → SHOWN_GENERATED (labeled + provenance)
           → DROP → AUTHORED_FALLBACK | GENERATED_UNAVAILABLE
           → UNAVAILABLE → AUTHORED_FALLBACK | GENERATED_UNAVAILABLE
REQUESTED/THINKING → CANCELLED → AUTHORED_READY
SHOWN/UNAVAILABLE → learner-initiated RETRY (one per interaction; parent linked)
```

The provider never emits an unchecked visible string. `drop` reasons are machine-readable/evidence-visible only; learner copy does not reveal whether a key/higher tier caused the drop.

### Rubric proposal

```text
SHORT_RESPONSE_PENDING → REQUESTED → GATE_CHECK
GATE_CHECK → PASS → PROPOSAL_PENDING_REVIEW
           → DROP/UNAVAILABLE → RESPONSE_STAYS_PENDING
PROPOSAL_PENDING_REVIEW → HUMAN_ACCEPT | HUMAN_REPLACE → existing human mark event
```

Proposal is not a mark: score, accepted evidence, and `review_state` stay unchanged until an explicit human action. Rejection/expiry leaves the original response intact.

### Model lifecycle vocabulary (complete typed surface set)

| Runtime outcome/state | Learner-visible treatment | Evidence/recovery rule |
|---|---|---|
| `disabled` / no profile | No request control or `Generated help is unavailable` after an explicit request | Record configuration outcome only when requested; authored loop is normal. |
| `requested`, `thinking`, optional `sourcing` | One polite static status; source names only when runtime has safe references | Cancel remains available where transport supports it; no typing animation or streaming raw output. |
| `pass` | `Generated support` card with safe provenance | Render finite runtime template from gated plan; record pass payload/fingerprint. |
| `drop` / `policy_blocked` | Generic unavailable copy, never the detector reason | Descriptor-only event; authored fallback or legal retry. |
| `timeout`, `unreachable`, `refused`, `malformed`, output/input cap | Generic unavailable copy, with no endpoint/provider diagnostic in learner view | Typed `unavailable`; preserve attempt and authored ladder; retry only by learner and parent-link it. |
| `cancelled` | `Optional guidance was cancelled. Your current work is unchanged.` | Record cancellation outcome when a request had begun; restore ready state. |
| retry exhausted/duplicate request | `Optional guidance was already requested for this attempt. Continue with the available hint or make another attempt.` | At most one automatic generation per interaction ID; no hidden re-request loop. |

## Major Interaction Contract

| Interaction | User goal / visible state | Action → response | Evidence/model/deterministic enforcement | Failure, recovery, accessibility | Acceptance |
|---|---|---|---|---|---|
| Request error-specific help | Get help about a genuine wrong response while authored tier is visible | Learner requests help; compact `Thinking…` then one typed outcome | Request has immutable interaction ID, latest genuine wrong response, permitted tier; runtime gate accepts bounded plan only. | Cancel/timeout/refusal/drop retains activity and authored tier; retry is explicit once and parent-linked. Live status announces state once. | Provider output cannot directly render, advance tier, or contain unknown/free-text fields. |
| Read passed augmentation | Understand one legal next move | Open/collapse AgentAssist; read `Generated support` plus provenance | Runtime templates allowed facts/spans; evidence stores passed learner-facing payload/fingerprint, backend/profile/tier/timing. | Long text wraps; citations/details are keyboard native; no animated typing. | Generated/support/source labels remain distinct and no inference of correctness is made. |
| Recover from unavailable/drop | Continue learning when model is absent or unsafe | Select authored shown tier or retry legally | Typed `unavailable`/`drop`; authored ladder/scoring/report continue; normal retrieval carries reason code, never raw dropped text. | Exact unavailable notice and next action; no endless spinner or disabled unexplained control. | Network disabled/malformed/refused/timeout fixtures preserve sitting and evidence/report use. |
| Inspect short-answer proposal | See rubric-point suggestions without accepting them | Reviewer opens pending checklist: pass/fail/uncertain + rationale/provenance | Proposal event is append-only and linked to response/interaction; deterministic code does not convert it to score/mark. | Empty/partial rubric is clearly incomplete/pending; long rationale wraps; controls have labels. | Model-only path leaves response pending and `marks_by_event()` unchanged. |
| Human settles a proposal | Authorize a mark | Human accepts or replaces through existing mark action | Existing human-only marker writes accepted mark and records proposal reference/actor. | Confirmation names response and choice; conflict/error keeps proposal and response pending. | No model call can produce accepted evidence; accepted record identifies human action. |

## Components and State Inventory

| Component | Ready/populated | Loading | Partial/error/degraded | Integrity/a11y |
|---|---|---|---|---|
| `AgentAssist` | Collapsed generated augmentation, label, tier-safe provenance | `Thinking…` in polite status | `unavailable`, `drop`, `cancelled`, `tool-failed`, `policy-blocked`; authored fallback remains | No chat textbox/history; content is runtime template only; details/summary keyboard native. |
| `ModelStatusNotice` | Backend/profile class, outcome, retry affordance if allowed | bounded static label | no configured backend, timeout, malformed/refused/unreachable | Never prints endpoint, secret, raw provider output, item key, or drop text. |
| `ProvenanceDisclosure` | Generated label, backend class (hosted/local), interaction ID, safe source/fact references | n/a | unknown/ambiguous source is `Unavailable`, not invented citation | Generated synthesis distinct from author source; long locators wrap/copy. |
| `RubricProposal` | One row per rubric point, `pass`/`fail`/`uncertain`, rationale | reviewing | missing/incomplete → pending/unknown, never default pass | Semantic list/table, labels, non-color status, no score control. |
| `HumanMarkAction` | Explicit accept/replace controls after proposal | marking | failed/rejected/expired keeps pending state | Action is visible only in designated reviewer surface; confirm and focus status. |

## Assessment Integrity, Evidence, and Privacy

| Tier | Responsibilities |
|---|---|
| Browser | Requests an optional operation and renders only normalized typed runtime payload; cannot select backend/profile/tier/key/facts. |
| Adapter | Normalizes CLI/HTTP transport only; enforces timeout, input/output caps, `shell=False` subprocess invocation, and typed unavailable. |
| Tier gate | Strict schema; exact manifest references/spans; key/higher-tier/protected fact/unknown/ambiguous output is `drop`; never “sanitizes” uncertain meaning. |
| Runtime | Builds allowed manifest from private item and Phase 6 entitlement; renders finite templates; controls retry and accepts only pass content. |
| Evidence | Logs attempt, backend/profile class, operation, timing, request fingerprint, outcome/gate/tier, passed learner payload where allowed. Drop audit stores descriptor/fingerprint/byte count/reason, not raw output/secrets. |
| Human | Sole authority for accepted short-answer mark; proposal is supplemental evidence only. |

Hosted/local transmission class is visible in audit provenance, not in learner-facing source attribution. Secrets remain environment/config references. A model is not a citation; where an authored/source fact is available, show its actual source label/locator. If no safe provenance exists, label the augmentation generated and avoid a fake citation.

## Copywriting Contract

| Element | Exact copy |
|---|---|
| Support disclosure | `Help and evidence` |
| Ready control | `Get optional guidance` |
| In flight | `Preparing optional guidance…` |
| Passed heading | `Generated support` |
| Generated disclosure | `This guidance is generated from the current attempt and the help available at this step.` |
| Hosted/local provenance | `Model service: hosted` / `Model service: local` (audit/reviewer details only) |
| Unavailable | `Generated help is unavailable. You can keep learning with the lesson and authored hints.` |
| Policy drop | `Generated help is unavailable for this step. Continue with the available hint or try another attempt.` |
| Retry | `Try generated guidance again` |
| Pending rubric heading | `Pending rubric suggestion — human review required` |
| Rubric empty/partial | `No complete rubric suggestion is available. This response is still waiting for a human mark.` |
| Human action | `Record human mark` |
| Confirmation | `Record this human decision for this response? The model suggestion remains a separate audit record.` |

## UI Considerations

| Category | Element | Status | Resolution / verification |
|---|---|---|---|
| empty/zero-one-many | Generated support and rubric points | ✅ covered | No generated content → authored fallback/unavailable; one/many points preserve labeled row shape; no inferred pass. |
| loading | Adapter request, human marking | ✅ covered | Bounded `Thinking…` / marking status; only active control disables; activity/draft/response stays visible. |
| error | Transport, malformed output, gate drop, marker error | ✅ covered | Typed outcome plus exact recovery; raw response/secrets/key never reach error copy. |
| partial | Incomplete rubric/provenance | ✅ covered | Label pending/unknown; show present point/source detail without fabricating absent claim. |
| overflow/long-text | Generated template, source locator, rubric rationale | 🧪 backstop | Wrap prose; scroll only labeled evidence pane; 320px/200% long-content visual test. |
| long-text | Interaction ID/reason code | ✅ covered | Monospace token wraps/breaks safely in reviewer details; learner surface never needs diagnostic strings. |

## Registry Safety

| Registry | Blocks used | Safety gate |
|---|---|---|
| None | None | Not applicable: native HTML/CSS/JS only; no shadcn, npm component registry, or third-party UI block is authorized. |

## Required Verification and Acceptance

| Gate | Evidence |
|---|---|
| Adapter parity | `python tests/model_adapter_roundtrip.py`: fake hosted executable and loopback OpenAI-compatible endpoint normalize to the same typed result under profile switch. |
| Gate adversarial corpus | `python tests/tier_gate_roundtrip.py`: malformed/unknown/free-text/key/correct-option/higher-tier/fake-source/ambiguous fixtures all `drop`; legal bounded plan alone passes. |
| No-leak UI | DOM/JSON/ARIA/CSS-off assertions: only passed runtime payload enters UI; no private key/tier/fact/drop text/secret. |
| Evidence and manual review | Pass/drop/unavailable log/retrieve safely; proposal remains pending; only explicit human `mark` settles it. |
| Degradation | Disabled, timeout, malformed, refusal, unreachable tests preserve authored hint, scoring, lesson, sitting, evidence and report. |
| A11y/visual | 1280/768/375 snapshots; keyboard disclosure/retry/reviewer controls; single live announcement; screen-reader label/provenance; reduced motion. |

**Combined-contract scenarios 1–10 audit:**

| # | Relevance to Phase 8 | Contract result |
|---|---|---|
| 1 | Optional help after a genuine wrong held attempt | Pass output augments exactly one legal authored tier; runtime still scores/holds. |
| 2 | Prediction-first math sequence | No request exposes a derivation/key before Phase 6 entitlement. |
| 3 | Code activity | Model stays disabled by default; code runner/result authority is unchanged. |
| 4 | Source ingestion/synthesis | Generated interpretation and source citation are explicitly distinct. |
| 5 | Stumped/changed retry | Adapter cannot unlock/advance a tier; it consumes the runtime grant only. |
| 6 | Equivalent visual task | Model is irrelevant to semantic visual score/evidence; it cannot replace accessible controls. |
| 7 | Provider outage | Directly covered: typed unavailable retains authored ladder, scoring, sitting, evidence and report. |
| 8 | Report-only auditor | Proposal/synthesis cannot publish/write/mark; reviewer/human authority remains explicit. |
| 9 | Sparse history | No model result fabricates a trend, confidence, or mastery claim. |
| 10 | New subject profile | Same adapter/status contract is profile-neutral; unsupported capability is typed unavailable, not a new shell. |

## Unresolved and Do Not Build

- **IMPLEMENTATION/VERIFICATION GATE:** `08-AI-SPEC.md` is approved. Do not ship learner-facing generated support until the Phase 6 permitted/reserved-fact seam, bounded structured output, offline fallback, backend parity, and adversarial leakage suites are implemented and green.
- **UPSTREAM:** Phase 6 must publish a callable permitted-tier/allowed-fact seam; no UI infers tier from local state.
- **OPEN:** Raw dropped-output forensic export; default is descriptor-only local audit. Any raw disclosure needs a separate security decision.
- **OPEN:** Exact first hosted CLI executable/profile; ship default backend disabled and test with fakes.
- Do not build persistent/freeform chat, agent memory, provider-native output rendering, model scoring/accepted marks, model selection/tier progression, model-authored bank writes, raw transcript/report exposure, secrets in UI/evidence, or an unavailable state that blocks the authored loop.

## Checker Sign-Off

- [ ] Copywriting and lifecycle state copy
- [ ] Subordinate responsive wireframes and token use
- [ ] Provenance/citation and pending-review distinction
- [ ] Assessment integrity, typed gate and no-leak verification
- [ ] Registry safety (not applicable)

**Approval:** UI contract approved by `gsd-ui-checker` on 2026-08-08 (6/6 dimensions); generated-support implementation remains blocked on the required AI-SPEC and gate evidence above.
