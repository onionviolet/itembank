---
phase: 11
slug: closed-authoring-loop-curriculum-auditor
status: approved
reviewed: 2026-08-08
shadcn_initialized: false
preset: none
created: 2026-08-08
---

# Phase 11 — Closed Authoring Loop & Curriculum Auditor UI Design Contract

> This contract makes authority, source evidence, gate results, and reversibility observable before any write. It supplements the approved cross-phase contract and Phase 04 tokens. Locked Phase 11 decisions win.

## Decision Legend and Authority

| Label | Meaning |
|---|---|
| **LOCKED** | Binding Context/Requirements decision; no plan may weaken it. |
| **UPSTREAM-CONTRACT** | Domain/schema/CLI work may proceed without a browser surface. |
| **UI-BLOCKED** | Ingestion, audit, draft, diff, approval, publish, or undo browser UI may not ship before this contract’s gates pass. |
| **AI-GATED** | Requires the named Phase 8 adapter/gate contract and adversarial evidence; no substitute transport or prompt-only control. |
| **OPEN** | Keep a seam or explicit unsupported state only. |

**Authority boundary — LOCKED:** sources remain read-only; source extraction is a derived, fingerprinted artifact. A coverage claim is `covered` only with exact source-span and bank-item citations; uncited is `unknown`, never confidence-upgraded. The model is an untrusted proposal producer. Runtime schemas, request scope validation, lint, independent quality findings, full-candidate preflight, transactional writer, autonomy policy, and human approval decide what can publish. The browser never supplies a path, selected autonomy, backend, source citation, write id, gate result, or undo backend as authority.

## Phase, Plan, Research, and AI Gating Matrix

| Work | Classification | Required gate before completion |
|---|---|---|
| 11-01/02 source primitives, public schemas, injected tracer, CLI | **UPSTREAM-CONTRACT** | Synthetic temp-only fixtures; repository-blind callable sees public contract/request/structured failures only. No browser/daemon route. |
| 11-03 normalization, coverage states, material handoff | **UPSTREAM-CONTRACT** | UTF-8/Markdown stable-locator fidelity; source bytes immutable; all coverage states and stale fingerprint fixture. |
| 11-04 bounded retries and four quality detectors | **UPSTREAM-CONTRACT** | Exact detector threshold/order tests, complete failed-batch retention, scope-before-lint/preflight-before-writer tests. |
| 11-05 autonomy, writer, CLI approval/undo | **UI-DEPENDENT (CLI)** | D-15 explicit `proceed` checkpoint; diff/write-id/undo and Git/shadow stale/conflict tests. |
| Any browser audit/approval/publish/revert surface | **UI-BLOCKED** | This spec’s responsive, SR/keyboard, no-write, provenance, diff and undo UAT gates. No daemon route is authorized until those pass. |
| Phase 11 model authoring integration | **AI-GATED — currently blocked** | Phase 8 must first publish `model_adapter.py::invoke(request, profile)`, strict public request/result schema, tier/outcome evidence, and passing adapter/gate adversarial tests. Phase 11 then requires an AI-SPEC or equivalent approved AI evaluation contract covering author-operation scope, retry, prompt-injection/untrusted-output tests, volume caps, and model-unavailable behavior. No Phase 11 AI-SPEC exists in the planning inventory: retain injected fake callable/CLI seam only. |
| PDF/DOCX intake UI | **OPEN / blocked** | Do not expose until locator-preserving adapter and fidelity fixtures exist. Markdown and UTF-8 text are first-class only. |

**Research gate — explicit:** use only the researched four independent quality detectors (answer-position skew, near-duplicate stems, answer leak, distractor-rationale completeness) at their documented thresholds. Findings retain detector version and measured evidence; they never become an opaque score. A fifth detector, changed threshold, or automated PDF/DOCX promise needs a new research/contract decision.

## Goals and Information Architecture

**Goals:** show a reviewer what was supplied versus synthesized; make every claim traceable; guide bounded draft repair without hiding failure; expose all gates/diffs before an authorized write; make reversibility safe and legible; keep audit findings separate from authority to generate.

| Area | Contents | Primary action |
|---|---|---|
| Sources | immutable source card, fingerprint, locator-preserving extraction progress/results | `Review extracted objectives` |
| Audit report | objective coverage states, dual citations, candidate material, stale status | `Inspect claim evidence` |
| Author request | exact objectives/count/types/citations, selected configured mode, caps | `Validate request` |
| Draft workspace | attempt timeline, scope/lint/quality findings, preview, real-renderer preview | `Revise draft` |
| Review queue | clean proposed units, diff, citations, gate matrix, write id after mutation | `Review proposed change` |
| Publish/revert | permission-specific publish result, volume accounting, backend/manifest, undo/refusal | `Undo this write` |

## Major Interaction Contracts

| Interaction | Goal / state | Action → response | Evidence / model / enforcement | Failure and a11y | Acceptance |
|---|---|---|---|---|---|
| Difficult source intake | Preserve source fidelity; `empty`, `reading`, `extracting`, `partial`, `unsupported`, `failed`, `ready` | Choose Markdown/UTF-8 text by validated source id → progress names current adapter and completed/total spans → review candidates | Source id/fingerprint, adapter/schema version, stable line/heading locator, verbatim span. No model is needed to normalize. Source stays read-only. | Invalid UTF-8/unsupported type says why and preserves no misleading partial report; retry/review source. Status is `role=status`; long locators wrap/scroll independently. | Fixture proves empty/one/many, difficult partial, invalid UTF-8, unsupported PDF/DOCX, and unchanged source bytes. |
| Claim evidence | Distinguish source fact, bank evidence, synthesis, confidence, ambiguity, disagreement | Select claim → side-by-side `SourceCitation`, cited item IDs and `Generated synthesis` panel | `covered` requires both exact citations; `partial`, `conflicting`, `gap`, `unknown`, `stale` remain typed. Confidence cannot upgrade uncited content. | Missing/stale citation cannot show green covered; focus returns to claim row on close. | Every state has a deterministic fixture; long quote/diff does not clip locator or IDs. |
| Bounded author request | Keep model inside explicitly requested curriculum | Enter/review objectives, count, types, citations → `Validate request`; invalid request shows field findings and cannot call author | Runtime validates scope before every attempt and final writer boundary. Model receives only public spec/schema, serialized bounded request, attempt number and structured findings. | No raw provider/repository/error leakage; errors are linked with `aria-describedby` and summary focus. | Spy fixture proves no private path, credentials, unrelated source, repo access, or out-of-scope writer call. |
| Draft → validate → revise | Make repair observable; `drafting`, `validating`, `lint-failed`, `quality-failed`, `clean`, `retrying`, `exhausted` | Request draft → show attempt/phase status → reveal named findings; `Revise draft` creates next bounded attempt | Lint then four independent quality findings then full candidate preflight. Model contribution labelled `Generated draft`; deterministic gates label source/version/measure. | Retry cap creates retained `Exhausted — not published` report, never clean-prefix write. Screen reader receives one concise phase change. | Malformed-first/clean-second and cap-exhaustion fixtures prove no prefix mutation and deterministic attempt order. |
| Preview and real renderer | Let reviewer inspect learner-visible result before approval | Select clean unit → rich artifact preview plus `Open learner preview` from public renderer payload | Preview is non-authoritative; exact source/request/bank/profile/tool fingerprints and gate results accompany it. Browser receives public preview only. | Renderer unavailable says `Preview is unavailable; this draft is not approved or published.`; never substitutes raw private key. | No-key public-payload inspection; 1280/768/375 and keyboard preview tests. |
| Approval queue | Require exact human intent in `draft_and_approve` | `Review proposed change` → diff/citations/gates/write-unit id → `Approve this unit` confirmation or `Reject this unit` | Approval requires exact proposed write id after fresh preflight; same gates run in every autonomy mode. Actor and decision are audit events. | Stale diff returns to `stale — revalidate required`; cancel/reject writes no bank. Dialog focus trapped/restored; buttons never depend on color. | Reject/approve each one unit; only exact accepted unit mutates and obtains manifest/write id. |
| Full autonomy | Expose risk, caps, and volume; `disabled`, `armed`, `running`, `completed`, `partial/failed` | Explicit configured `full` + flag agreement → preflight volume panel → run → final totals | Full is alias of `audit_draft_lint_fix_commit`, never model-selected. Same citations/lint/quality/diff/audit pipeline; per-run/per-objective caps enforced. | Default/ambiguous mode is blocked; failure lists proposed/accepted/rejected/retried/written and never calls it published. | Test each exit path and prove byte-equivalent gate outputs to other modes. |
| Publish/revert | Make reversible mutation legible; `prepared`, `published`, `stale`, `conflict`, `reverted`, `failed` | Publish only through policy → show unit/diff/backend/write id; `Undo this write` asks confirmation → guarded undo | Writer chooses clean tracked Git per-item commit else shadow before-image/manifest under lock. Undo route comes from manifest only; no force. | Git dirty/conflict or shadow fingerprint mismatch refuses with next step; no overwrite of later human work. `role=alert` for refusal. | Git and shadow test show diff, one unit, manifest, one undo; stale/conflict/parallel/interruption cannot hide mutation. |

## State Machines

```text
source: empty → validating → normalizing → ready
                     ↘ unsupported | failed | partial-review

claim: extracted → unknown | gap | partial | conflicting | covered
       any source/bank fingerprint change → stale (re-audit required)

authoring: request-valid → drafting → scope-check → lint → quality → full-preflight
             ↘ invalid         ↖ retry (bounded)
full-preflight → report-only-artifact | queued-approval | publish-authorized
any failed/exhausted/partial state → retained report/draft, never published

write: prepared → published → undo-requested → reverted
                 ↘ stale/conflict/failed (no force transition)
```

`partial` applies to data/finding availability, never to a silently published batch. “Generated”, “deterministic”, “human accepted”, and “published” are separate status fields, never a blended success label.

## Annotated Wireframes

### Desktop (≥1024px)

```text
┌ Audit: EMT Standards       Source v1 · 8f42… · 34 spans · current ┐
│ [Sources] [Report] [Author] [Review queue 2]                        │
├──────────────────────────────┬──────────────────────────────────────┤
│ Objective: Airway assessment │ Claim state: PARTIAL                 │
│ Source: §3.2 lines 41–53     │ Bank: [ID:EMT-…] [ID:EMT-…]          │
│ “verbatim source span…”      │ Generated synthesis (confidence: .72)│
│ [Inspect claim evidence]     │ Missing cited evidence: …            │
├──────────────────────────────┴──────────────────────────────────────┤
│ Proposed unit W-… · all deterministic gates passed · draft & approve│
│ [Open learner preview] [Review proposed change]                      │
└─────────────────────────────────────────────────────────────────────┘
```

Source authored material and evidence occupy the left/first DOM column; synthesis and inference are visibly labelled secondary. A green state never substitutes for citation text.

### Tablet (768–1023px)

```text
Objective: Airway assessment · PARTIAL
Source §3.2 lines 41–53 · Bank IDs 2
[Inspect claim evidence]
<details>Generated synthesis, confidence, ambiguity and disagreement</details>
Proposed unit W-… · gates: lint passed; quality passed
[Open learner preview] [Review proposed change]
```

### Narrow (<768px)

```text
Audit report
Airway assessment [PARTIAL]
Source: §3.2, lines 41–53
Bank evidence: 2 items
[Inspect claim evidence]
Proposal W-…
Lint: passed · Quality: passed
[Open learner preview] [Review change]
```

Diff rows are a labeled horizontally scrollable semantic table or stacked definition rows—not a screenshot. Dense authoring gets `Best reviewed on a larger screen; all review and rejection controls remain available.` at narrow width.

## Reusable Component Inventory

| Component | Contract |
|---|---|
| `SourceStatus` | Source id, adapter/version, fingerprint, immutable/read-only status, progress/error. |
| `SourceCitation` | Exact locator + verbatim span + fingerprint; source content is visually separate from synthesis. |
| `CoverageClaim` | One typed state, dual-citation set, confidence, ambiguity/disagreement, stale check. |
| `GateTimeline` | Scope → lint → quality → preflight chronology; named findings only, no opaque score. |
| `FindingList` | Stable-sorted zero/one/many findings with code, detector version, evidence, threshold and remediation. |
| `ArtifactPreview` | Rich author preview plus public real-renderer preview, both clearly non-publish actions. |
| `DiffApproval` | Exact unit diff, citations, gates, mode, actor, proposed write id, explicit approve/reject. |
| `AutonomyBanner` | `report_only`, `draft_and_approve`, or `full`, with permission and volume—not a model claim. |
| `WriteReceipt` | Write id, backend, unit, manifest/fingerprints, final volume, `Undo this write`. |
| `StatusNotice` | Typed unavailable/policy/stale/conflict/failure recovery, with safe public copy only. |

## Responsive, Keyboard, Screen Reader, Offline, and Integrity Rules

- Native `<button>`, `<details>`, heading hierarchy, `<progress>`, `<table>`, `<dialog>`, `<pre><code>` diff blocks, and `role=status` precede custom ARIA. All actionable targets are ≥44px.
- Tab order is source/claim → evidence → synthesis → preview → review action. Opening citation, preview, or confirmation returns focus to its specific invoking row; Escape cancels but never rejects/approves/publishes.
- Use one polite status region for extraction/validation/retry/publish progress; reserve alerts for blocked request, stale preflight, conflict, or unsafe undo. Each state exposes text; confidence, detector severity, diff additions/removals, and coverage state never rely only on color.
- The UI receives server-issued status, public preview, and signed/opaque identifiers only. It cannot decide coverage, pass a gate, select mode/backend, send a filesystem path, transform an unsupported source, publish a draft, or select Git/shadow undo. Recheck authorization/scope/fingerprint after every asynchronous boundary.
- Offline/model-unavailable: existing source/report/diff artifacts remain readable; a queued request says `Authoring model unavailable. Your request and findings were retained; nothing was published.` A retry is explicit/bounded. Do not show invented extraction, draft, confidence, or success.

## Design Tokens

Use Phase 04 generated tokens and native elements only; no shadcn, npm, external diff/editor/chart/icon package, CDN font, or third-party registry.

| Role | Value / use |
|---|---|
| Spacing | 4/8/16/24/32/48/64px only; 16px narrow card padding, 24px wide. |
| Typography | 14px/400 metadata, 16px/400 body, 20px/600 section, 28px/600 display. Monospace only for IDs, locator offsets, schema versions and diffs. |
| Dominant 60% | `--bg` / `--ink` for reading authored source and primary review area. |
| Secondary 30% | `--card`, `--chip`, `--line` for citations, finding rows, diff, queue, sticky context. |
| Accent 10% | `--accent` only for primary non-destructive actions, focus, links, active tab and current row. |
| Semantic colors | `--ok`, `--warn`, `--bad` pair with text/icon/border. `--ok` means a specified deterministic stage passed, never authorized/published; destructive/revert confirmation uses `--bad` only with explicit text. |

## Copy and Error Contract

| Element | Exact copy |
|---|---|
| Primary source CTA | `Review extracted objectives` |
| Primary author CTA | `Validate request` |
| Draft repair CTA | `Revise draft` |
| Review CTA | `Review proposed change` |
| Approval CTA | `Approve this unit` |
| Rejection CTA | `Reject this unit` |
| Undo CTA | `Undo this write` |
| Empty source | `No sources yet` — `Add a UTF-8 text or Markdown source to begin a citation-first audit. PDF and DOCX are not supported until locator fidelity is verified.` |
| Extraction failure | `This source could not be normalized.` — `The original file was not changed. Review its encoding or choose a supported source.` |
| Uncited claim | `Unknown — citations are incomplete` — `Confidence cannot make this a coverage claim. Add an exact source span and bank item citation, then re-audit.` |
| Conflict | `Coverage evidence conflicts` — `Review each cited source and item. This report does not choose a side or publish content.` |
| Stale | `This report is stale` — `The source or bank changed after this report was created. Re-run the audit before acting on it.` |
| Empty draft | `No draft has been generated` — `Validate a bounded authoring request first.` |
| Retry | `Attempt {n} needs revision` — `The draft was retained. Fix the named scope, lint, or quality findings and try again.` |
| Exhausted | `Retry limit reached — not published` — `The complete draft and findings were retained. No part of this batch was written.` |
| Preview failure | `Preview is unavailable` — `This draft is not approved or published. Review the structured findings or retry the preview.` |
| Report-only | `Report-only mode — no bank changes are allowed.` |
| Approval confirmation | `Approve write {write-id}?` — `This publishes exactly one reversible unit after a final validation. You can undo it only while the recorded after-state still matches.` |
| Full warning | `Full autonomy is enabled` — `All gates still apply. This run is limited to {total} proposed units and the configured per-objective caps.` |
| Publish failure | `This change was not published.` — `The prepared report remains available; review the stale, conflict, or validation result before retrying.` |
| Unsafe undo | `Undo cannot proceed safely.` — `The bank changed after this write or Git reported a conflict. Your newer work was not overwritten.` |

## Evidence, Determinism, and Model Boundaries

Each source/report/proposal/write view must expose schema/tool version, source fingerprints, bank fingerprint, request fingerprint, adapter profile, gate findings/version, attempt number, mode, volume, unit/write id, and state timestamp. Stable sort order applies to objective IDs, citations, findings, units, and volume rows. The deterministic runtime validates scope → lint → four quality detectors → full candidate preflight → permission → writer; it is the only publisher. The model may produce a labelled draft or structured retry response after the Phase 8/AI gate is met, but it cannot supply a passing gate, coverage state, human approval, write id, undo backend, or accepted evidence. “Confidence” describes extraction/synthesis uncertainty only and never has enforcement authority.

## UI Considerations

| Category | Element(s) | Status | Resolution |
|---|---|---|---|
| empty | Source list, claim list, draft queue | ✅ covered | Exact no-source/no-draft copy above and next action; no fake audit. |
| loading | Extraction, author attempt, validation, preview, publish/undo | ✅ covered | Phase-labelled progress and cancellable/explicit retry; one status region. |
| error | Source, claim, model, gate, preview, writer | ✅ covered | Typed actionable recovery; all failures remain non-published. |
| populated | Citations, findings, diffs, receipts | ✅ covered | Source/synthesis/evidence/authority labels stay separate. |
| partial | Extraction, citation, findings, batch | ✅ covered | Partial data may be reported; partial batch never writes prefix. |
| overflow | Locators, quotes, 0/1/many findings, large diffs | 🧪 backstop | 1280/768/375 fixture verifies wrapped prose, scrollable code/diff, visible controls and stable focus. |
| zero-one-many | Claims, findings, draft units, volume rows | ✅ covered | Stable singular/plural copy; individual units always retain own citations/gates. |
| long-text | Source spans, IDs, diff lines, messages | ✅ covered | Wrap prose; scoped code containers scroll; no ellipsis on citation or destructive target identity. |

## Acceptance and Verification

### Shared ten-scenario relevance matrix

| Shared scenario | Phase 11 relevance / required evidence |
|---|---|
| 1. EMT held-hint loop | Regression: generated authoring must not alter learner scoring/tier authority; preview uses public renderer payload only. |
| 2. Math local rendering | Regression: generated/previewed math is inspected through the same offline renderer fallback; no CDN or private answer data. |
| 3. CS code execution | Regression: generated code items retain Phase 05 public/private runner boundaries and honest limits in preview. |
| 4. Difficult-source audit | **Primary:** difficult source exposes locator, source/synthesis/confidence/disagreement, unsupported/lossy failure, and no fake locator. |
| 5. Hint/retry loop | Boundary: author retry is distinct from learner hint progression; model cannot advance learner tier or author outside the exact request. |
| 6. Accessible visual task | Regression: a visual item draft/preview cannot bypass semantic public-payload, keyboard, or deterministic scoring contracts. |
| 7. Model unavailable | **Primary AI gate:** retained request/findings, explicit bounded retry, no spinner/no publish; local source/report/diff remain readable. |
| 8. Report-only audit gap | **Primary:** real cited gap, candidate material and preview are inspectable; report-only exposes no publish control or write event. |
| 9. Sparse history | Direct uncertainty grammar: uncited/sparse/conflicting material remains unknown/partial, never confidence-upgraded to covered. |
| 10. Fourth profile | Regression: author/audit contracts are subject-profile/config driven; no subject-specific writer, scorer, or browser flow is introduced. |

The matrices above preserve the global public-payload, responsive, offline, keyboard/SR, and evidence-trace requirements for every author/audit view.

1. Empty/one/many Markdown/text sources normalize with stable headings/lines/spans; invalid UTF-8 and unsupported PDF/DOCX fail without source mutation.
2. `covered`, `partial`, `conflicting`, `gap`, `unknown`, and `stale` claims render exact state grammar, dual citations, confidence, ambiguity and disagreement without confidence escalation.
3. Candidate materials and weak-objective priority produce no author call/write. Obtained material produces a new explicit bounded request only.
4. Scope mismatch rejects before lint/model retry/writer and exposes structured field finding; spy confirms no repository/private context.
5. Malformed-first/clean-second draft shows ordered retry/gate timeline; cap exhaustion retains complete draft/report and writes nothing.
6. Each researched detector demonstrates pass, equality/floor and failure thresholds with measured evidence; no composite quality score appears.
7. Rich and real-renderer preview use public payloads only; no answer key or hidden data is exposed in DOM, accessible names, CSS-off text, or API.
8. `report_only`, approval, and full have byte-equivalent validation/citation/diff data; only final permission changes. Report-only has no publish control.
9. Approval requires exact unit/write id and confirmation; rejection/cancel/stale preflight produces no bank mutation; focus restores to source queue row.
10. Full requires explicit opt-in/caps and announces proposed plus final accepted/rejected/retried/written per-objective/total volume on every exit.
11. Git/shadow receipt reveals backend/write id/manifest; one undo works on unchanged after-state. Dirty Git, fingerprint mismatch, conflict, duplicate, interrupted and parallel cases refuse or resume safely without force.
12. At 1280/768/375, keyboard/SR can read source evidence, inspect a claim, preview, reject/cancel, approve when authorized, and request undo; long citations/diffs retain readable identity and controls.

Run the planned stdlib suites (`audit_roundtrip.py`, `audit_coverage_roundtrip.py`, `audit_quality_roundtrip.py`, `audit_authoring_roundtrip.py`, `audit_cli_roundtrip.py`, `audit_writer_roundtrip.py`) plus no-key public-payload, responsive, keyboard/SR, offline/model-unavailable and report-only/no-write fixtures. A browser route is not complete until all relevant fixtures pass.

## Unresolved and Do Not Build

- **BLOCKED:** The Phase 11 AI-SPEC/evaluation contract is approved, but the Phase 8 real adapter and executable Phase 11 AI fixtures are not green; do not bind a live provider, expose model authoring UI as operational, or treat prompt text as scope enforcement.
- **OPEN:** PDF/DOCX UI remains unavailable pending stable locator fidelity; do not silently extract lossy text.
- Do not auto-publish a coverage finding, gap, weak objective, candidate material, generated draft, lint-clean prefix, model suggestion, or confidence score.
- Do not create a browser-only validator/writer, freeform “generate a course” surface, persistent agent chat/memory, mutable source editor, force-undo, restore-anyway button, opaque detector score, telemetry, cloud storage, or hidden bulk mutation.

## Registry Safety and Checker Sign-Off

| Registry | Blocks used | Safety gate |
|---|---|---|
| None | None | Not applicable — stdlib HTML/CSS/JS and existing theme tokens only. |

- [x] Copywriting, visual hierarchy, color, typography, spacing: PASS
- [x] Responsive, keyboard, SR, integrity, offline, evidence gates: PASS
- [x] Research and AI gates recorded: implementation remains blocked until Phase 8 + AI-SPEC evidence exist
- [x] Registry safety: PASS

**Approval:** approved by `gsd-ui-checker` on 2026-08-08 (6/6 dimensions); live-model authoring remains blocked as stated.
