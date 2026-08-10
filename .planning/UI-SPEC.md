---
phase: cross-phase-03-11
slug: learning-workspace-and-agentic-loop
status: approved
shadcn_initialized: false
preset: none
created: 2026-08-08
verified: 2026-08-08
---

# Cross-Phase UI Design Contract — Learning Workspace and Agentic Loop

> Canonical visual and interaction contract for phases 3–11 (including 6.1). This document **supplements rather than replaces** phase UI specifications 03, 04, and 05. Where they differ, a requirement or phase-context decision marked **LOCKED** wins; otherwise this document's cross-surface token and interaction rules govern new work.

> **GSD verification:** approved across copy, visual hierarchy, color, typography, spacing, registry safety, responsive behavior, accessibility, and assessment-integrity review. Type-specific learner actions use `Check answer`, `Run code`, or `Check response`.

## Decision Legend and Authority

| Label | Meaning |
|---|---|
| **LOCKED** | Binding prior decision from `CONTEXT.md`, `REQUIREMENTS.md`, or `PROJECT.md`. Do not change in a plan. |
| **RECOMMENDED** | This contract's implementation direction; plans may improve it only with a recorded reason and equal-or-better accessibility/safety. |
| **ASSUMED** | Safe working assumption; validate with a fixture or UAT before treating it as product fact. |
| **OPEN** | Architecture-changing decision; do not implement it beyond a seam or prototype. |

**Authority boundary — LOCKED:** one parser, one scorer, one runtime, and one append-only evidence store. The browser, a visual renderer, and a model adapter are clients; none receives a hidden key, decides correctness, advances a hint tier, or writes accepted evidence. Local-first storage and no telemetry remain mandatory. A model may see item text under the accepted-risk policy, but its output is never the source of truth.

---

## 1. Plan-Gating Matrix

### Phase gates

| Phase | Classification | Gate before implementation / completion | Rationale |
|---|---|---|---|
| 03 Lesson reader | **UI-DEPENDENT** | May implement parser/lint/CLI; reader route and lesson↔item links require its existing 03 UI-SPEC and this shared contract. | Deep links, no-lesson/degraded states, reading order, and keyboard behavior are part of the public lesson contract. |
| 04 Surface redesign/theming | **UI-BLOCKED** | Do not execute presentation changes without this contract; 04 UI-SPEC remains the detailed local source. | It establishes tokens, responsive shell, accessibility primitives, and conflict-recovery UI used by every later surface. |
| 05 Code editor | **UI-DEPENDENT** | Runner/scorer work may proceed; editor, results, and refusal surfaces require 05 UI-SPEC plus the shared accessibility rules. | Editor behavior and honest execution boundaries are safety-relevant UI. |
| 06 Hint ladder/feedback modes | **UI-BLOCKED** | Runtime transition engine can be built behind fixtures; learner-facing hint/retry surface cannot ship without this contract. | Hint affordances determine evidence semantics and answer-leakage risk. |
| 06.1 Visual assessment protocol | **UI-BLOCKED** | Protocol/schema work may begin; SVG/HTML renderer and interaction-event surface require this contract. | Semantic action capture, accessible equivalents, and feedback-intent display affect scoring/evidence architecture. |
| 07 Selection engine | **UPSTREAM-CONTRACT** | Selector can proceed with a stable `trace` interface; any learner-visible “Why this item?” panel validates against this contract before completion. | Trace wording, unknown history, and pacing handoff are UI-consumed data contracts. |
| 08 Model adapter/tier gate | **UPSTREAM-CONTRACT** | Adapter/gate can proceed with typed outcomes; its learner-facing status and generated-hint panel require this contract before completion. | `pass/drop/unavailable`, provenance, and retry semantics are safety-critical UI contracts. |
| 09 Subject-invariant loop | **UI-BLOCKED** | Do not build media enhancements without the shared workspace, subject-profile, responsive-table, and degraded-media rules. | A subject fork caused by a renderer shortcut violates LOOP-01/05. |
| 10 Retention/pacing/trends | **UI-BLOCKED** | Derivation modules may begin; day/report/recommendation UI cannot ship without this contract. | “Due,” trend confidence, cap override, and Anki separation must be explainable and non-punitive. |
| 11 Authoring loop/curriculum auditor | **UI-BLOCKED** | Ingestion/lint/quality modules may begin; any agent write, diff, approval, or audit view requires this contract. | Provenance, uncertainty, authorization, and reversibility must be visible before a write is possible. |

### Existing-plan disposition

| Plans | Classification | Additional gate |
|---|---|---|
| 03-01–03-03 | UI-DEPENDENT | Parser/lint/route work can execute. Fixture must prove public lesson payload excludes answer-key material. |
| 03-04–03-06 | UI-BLOCKED | Verify reader wireframe, heading navigation, long-content behavior, and no-source/degraded state. |
| 04-01 | UI-BLOCKED | Treat as the production visual-tracer foundation; it must establish the shared shell, focus/status primitives, and baseline visual tests. |
| 04-02–04-03 | UI-DEPENDENT | Data/concurrency/token derivation may execute; conflict and picker UI require responsive/a11y acceptance checks. |
| 04-04–04-06 | UI-BLOCKED | No completion until tokens are used across quiz/study/day/report/settings and the day recovery journey passes. |
| 05-01–05-04 | UI-INDEPENDENT | Runner, scorer, bounds, and OS spike can execute under 05’s honest-limits wording. |
| 05-05–05-07 | UI-BLOCKED | Editor, results, error/refusal states, keyboard tests, and no-answer-leak review must pass. |
| 06-01 | UPSTREAM-CONTRACT | Publish transition payload/state schema and evidence semantics before rendering controls. |
| 06-02 | UI-BLOCKED | Hint stack, stumped action, held cursor, diagnostic/exam withholding, and recovery states require UI validation. |
| 06.1-01–06.1-02 | UPSTREAM-CONTRACT | Schema/protocol work can proceed only with semantic actions, public/private scene split, and event vocabulary fixed. |
| 06.1-03 | UI-BLOCKED | SVG keyboard/touch equivalent, no-leak fallback, reduced-motion, and GIFT refusal UX must pass. |
| 07-01–07-05 | UPSTREAM-CONTRACT | Publish `trace`, rationale, empty-candidate, and sparse-history shapes; no dashboard implied. |
| 07-06 | UI-DEPENDENT | CLI/API explanation is required; defer a full workspace panel to Phase 10, but contract-test copy with a future `Why this item?` renderer. |
| Phase 08 (no plans yet) | UPSTREAM-CONTRACT | Adapter, tier-gate, provenance, and typed failure work may proceed; any learner-facing model status or generated-hint surface is UI-BLOCKED. |
| 09-01 | UPSTREAM-CONTRACT | Profile/session/schema work may proceed. Its semantic-table and narrow-viewport acceptance checks are UI-DEPENDENT and must validate against this contract. |
| 09-02 | UPSTREAM-CONTRACT | Registry and client-option plumbing may proceed. Public profile/capability notices are UI-DEPENDENT and must use the shared status/error grammar. |
| 09-03 | UI-INDEPENDENT | Human KaTeX provenance, license, checksum, and distribution review can proceed without learner-facing UI decisions. |
| 09-04 | UI-BLOCKED | Vendoring/package work may proceed, but the math renderer and readable error/fallback states must satisfy the offline, responsive, accessibility, and source-preservation rules in this contract. |
| Phase 09 future media plans | UI-BLOCKED | Inline runnable lesson blocks and other new learner-facing media require UI validation before execution. |
| Phases 10–11 (no plans yet) | UI-BLOCKED / UPSTREAM-CONTRACT as above | Split derivation, protocol, and audit-engine work from presentation/approval work; include the named UI verification gates in each plan’s `must_haves`. |

**RECOMMENDED dependency changes:**

1. Keep 04-01 as a prerequisite for every new browser surface (06-02, 06.1-03, 08 presentation, 09 renderer, 10 reports/day, 11 approval UI), not merely Phase 4’s later plans.
2. Add `06-01 → 08 learner surface` and `06-01 → 06.1 feedback-intent surface`; both consume the permitted-tier contract.
3. Add `05-07 → 09 runnable lesson blocks`; Phase 9 must reuse the finalized runner/refusal policy.
4. Add `07-06 → 10`; Phase 10 supplies weights and evidence snapshots, while Phase 7 remains the sole selector and trace owner.
5. Add `08 gate contract + 10 provenance contract → 11`; authoring/audit UI must use the same typed status, source, uncertainty, and approval grammar.

---

## UI Considerations

The post-verification GSD state probe was run across the learning workspace, assessment, source-ingestion, retention, authoring, and agent-support surfaces. These are binding coverage truths for planning and verification:

| Surface | Resolved state consideration | Verification |
|---|---|---|
| Learning workspace | Activity, support, and status regions preserve DOM order, focus order, and the activity-first hierarchy at desktop, tablet, and narrow widths; hidden or collapsed support never removes the learner's active work. | Explicit responsive keyboard and screen-reader journey. |
| Assessment | Pre-answer, loading/running, attempted, incorrect, hint-eligible, retry, correct, exhausted, pending-review, failed-submit, and partial-recovery states use the assessment state machine; long content wraps/reflows without exposing hidden answers. | Explicit state-transition, no-leak, focus, and live-region tests. |
| Source ingestion | Zero sources, one source, many sources, in-progress extraction, partial extraction, unsupported content, conflict, failure, and populated review states preserve citations and distinguish source claims from synthesis. Lists scroll or paginate without clipping provenance. | Explicit ingestion fixtures covering empty/one/many/partial/error and long citations. |
| Retention and pacing | No-history and sparse-history states say that evidence is insufficient; populated recommendations expose their evidence and uncertainty, and never substitute decorative precision or engagement pressure. | Explicit sparse-history and conflicting-signal scenarios. |
| Authoring and audit | Empty draft, validating, partial findings, failed tool, long diff, queued review, approved, published, and reverted states preserve authorization boundaries; a failure never converts a pending write into a published one. | Explicit zero/one/many findings, long-diff, failure, undo, and focus-restoration tests. |
| Agent support | Thinking, sourcing, waiting-for-learner, uncertainty, disagreement, policy-blocked, tool-failed, model-unavailable, cancelled, retried, and completed states remain subordinate to the activity and never imply scoring authority. | Explicit typed-state fixtures and degraded-provider UAT. |

No consideration is dismissed. Any future element that does not fit these surface kinds is `⚠ unresolved — planner must treat as assumption` until a UI-SPEC revision classifies it.

---

## 2. Experience Principles

1. **Activity first, agent second — LOCKED.** The active reading, question, code, or manipulation owns the largest visual area. Agent help is contextual, collapsible, and tied to the active attempt; it is never a full-screen chat default.
2. **Evidence before inference — LOCKED.** Present source citation, observed response, event count, time window, and rule before a derived recommendation, mastery label, or generated synthesis.
3. **Progressive disclosure — LOCKED.** Show the next useful action and a concise reason; expose supporting evidence through an adjacent disclosure or detail view, not a separate metric dashboard.
4. **Make thinking observable, not performative — RECOMMENDED.** Ask for a prediction/attempt before execution or explanation when the activity permits it. “I’m stumped” is valid, explicit, and recorded; repeated empty submissions are not treated as learning.
5. **Calm progress, no engagement pressure — LOCKED.** No points, badges, levels, streak-recovery prompts, countdown pressure, or celebratory motion. Progress means completed evidence, readiness, and next instructional action.
6. **Same loop, varied media — LOCKED.** Subject profiles vary media, allowed items, and verifier only. They never create separate shells, scoring systems, or evidence semantics.
7. **Degrade honestly — LOCKED.** Offline/model-unavailable/unsupported capability states keep the authored activity usable when possible and say exactly what is unavailable; they never fake an answer, confidence, score, or model result.

---

## 3. Information Architecture

### Global shell

```
┌───────────────────────────────────────────────────────────────────┐
│ [Itembank]  Course / bank ▾       [Today] [Learn] [Review] [Report]│
│                                                           Settings  │
├───────────────────────────────────────────────────────────────────┤
│ Context line: lesson / objective / 3 of 8 / practice / offline?    │
├───────────────────────────────┬───────────────────────────────────┤
│ Activity canvas                │ Contextual support (optional)     │
│ reading | item | code | SVG    │ goal · prerequisite · hints       │
│                                │ agent status · sources · why      │
└───────────────────────────────┴───────────────────────────────────┘
```

**LOCKED:** the context line contains only bank/lesson context, objective, session progress, and feedback mode. Secondary metadata is in an accessible `<details>` disclosure. It is sticky but never obscures focused content.

| Area | Purpose | Primary objects |
|---|---|---|
| Today | bounded daily entry point | due objectives, cap state, Anki signal, recommendation rationale |
| Learn | lesson and activity workspace | lesson sections, item, attempt state, hint stack, contextual agent support |
| Review | scheduled/retrieval work | objective queue, reason, selected-item trace, no Anki schedule mutation |
| Report | evidence inspection | overview → subject → objective, raw counts, trends, pending review, trace/provenance |
| Sources | lesson/audit provenance | source location, claim/definition, confidence, disagreement, unsupported content |
| Author | human/agent closed loop | request, lint/quality findings, preview, diff, approval/undo, audit queue |
| Settings | local configuration | theme, cap, selection profile, model backend, audit autonomy; CLI twin always exists |

### Workspace rules

- Desktop (≥1024px): activity column is 2/3 width; contextual support is 1/3, independently scrolls only when necessary, and begins below activity in DOM order.
- Tablet (768–1023px): activity is full width; support opens as an in-flow “Help and evidence” disclosure after the active response controls.
- Narrow (<768px): one column; context line may wrap to two rows, but activity order never changes. Tables have a labeled horizontal-scroll wrapper or transform to definition rows; never a screenshot.
- **ASSUMED:** phone completion is not a Phase 3–11 primary target, but narrow responsive access is required for reading, ordinary item submission, hint access, and status recovery. Dense authoring and code work show an honest “best on a larger screen” advisory while remaining operable where technically possible.

---

## 4. Reusable Component Contracts

| Component | Contract | States / a11y |
|---|---|---|
| `ContextLine` | Sticky orientation only: context, objective, progress, feedback mode. | `<header>` + labeled progress; text labels accompany color; 44px target for disclosures. |
| `ActivityCanvas` | Renders one active lesson/item/visual/code task from a public payload. Never receives key or scoring rule. | `loading`, `ready`, `attempted`, `held`, `pending-review`, `completed`, `unavailable`; announced through one `role=status` region. |
| `GoalCard` | Names current goal, prerequisite status, and “why this now.” | Optional; no mastery percentage without evidence window/count. |
| `AttemptPanel` | Captures one response and its visible validation. Submits only to runtime API. | Pre-answer, invalid local form, submitting, accepted, held/retry, pending-review, completed. Disable only while request is in flight. |
| `HintLadder` | Progressive stack of shown tiers, source label, unlock path, and next legal action. | Hidden tiers have no DOM text/ARIA label. “I’m stumped — show next hint” is a normal button, not a warning. |
| `AgentAssist` | Compact contextual support: diagnostic question, generated augmentation, source citation, uncertainty/disagreement. | Collapsed by default unless requested; statuses `thinking`, `sourcing`, `pass`, `unavailable`, `blocked`, `dropped`. No freeform conversation pane in initial tracer. |
| `EvidenceDrawer` | Shows observed evidence and derived rationale for selection/trend/audit. | Uses summary first; includes snapshot id/window/count and raw event link/CLI equivalent. |
| `SourceCitation` | Displays source-authored quote/locator separately from generated synthesis. | Citation link/locator, source fingerprint/version, confidence, and disagreement chip; generated text labeled “Generated synthesis.” |
| `StatusNotice` | Typed recovery copy for local, model, tool, or policy errors. | `role=alert` only for action-blocking changes; otherwise `status`; never exposes hidden answer/key in fallback text. |
| `VisualInteraction` | Declarative SVG/HTML scene maps pointer/touch/keyboard actions to semantic response only. | Visible instructions + equivalent native controls/state; persist committed semantic action, not raw pointer noise. |
| `CodeEditor` | Existing textarea + line gutter contract, source visible after submit. | Tab/Shift+Tab behavior, focus-within outline, no wrap/gutter drift, keyboard result readout; retains Phase 5 copy verbatim. |
| `RecommendationCard` | One recommendation, reason, confidence/sufficiency, and inspectable evidence. | Unknown is an explicit state, not `0%`; allows “review evidence” but not opaque accept/reject. |
| `DiffApproval` | Shows proposed machine/human mutation versus current bank plus citations/gate results. | Approve/reject are separate buttons; approval requires explicit confirmation, records actor, and exposes undo id. |

---

## 5. Core State Machines

### A. Learning activity and feedback — LOCKED transition authority

```
READY → SUBMITTING → (invalid → READY)
                    → (pending manual review → PENDING_REVIEW)
                    → (correct → COMPLETE → next activity)
                    → (wrong + drill → REVEAL_AND_ADVANCE)
                    → (wrong + practice → HELD[tier 0 available])
                    → (diagnostic/exam → DEFERRED)

HELD → SHOW_NEXT_HINT (genuine changed attempt or explicit stumped)
     → RETRY → SUBMITTING
     → TIER_5_REVEAL → REVEALED → ADVANCE
```

- **LOCKED:** only a materially different, non-empty canonical response unlocks a tier from an attempt; `stumped` unlocks exactly one tier and records its path.
- **LOCKED:** diagnostic has no correctness/hint/explanation until sitting completion; exam holds feedback until accepted mark. The DOM/ARIA tree must not contain concealed correctness information.
- **RECOMMENDED:** reserve the feedback panel’s vertical space, use a concise neutral header (“Try again” / “A review is pending”), and preserve the learner’s answer adjacent to relevant feedback.

### B. Agent assistance and safety

```
REQUESTED → THINKING → SOURCING? → GATE_CHECK
GATE_CHECK → PASS → shown as “Generated support” + source label
           → DROP → authored tier fallback OR “Generated help is unavailable”
           → UNAVAILABLE → authored tier fallback OR recovery notice
           → POLICY_BLOCKED → recovery notice; no reason that reveals key
```

- **LOCKED:** pass/drop/unavailable are typed outcomes. A model cannot ask for or advance a tier; a retry is learner-initiated and linked to the original interaction.
- **RECOMMENDED:** `thinking` is an inline status with a static progress label, not a looping typing animation. `sourcing` shows source names/locators as they become available. Respect reduced motion.
- **RECOMMENDED:** uncertain or conflicting synthesis presents: “This is a generated interpretation,” source A / source B, a one-sentence disagreement, and “Review sources.” Do not average confidence into false certainty.

### C. Code/visual activity execution

```
EDITING / MANIPULATING → VALIDATING → RUNNING / SUBMITTING
RUNNING → RESULT_VECTOR → scored by runtime → activity feedback state
RUNNING → timeout | output cap | daemon unreachable | LAN-blocked | static-file
        → typed StatusNotice + legal retry/recovery action
```

- **LOCKED:** Phase 5’s no-sandbox statement remains visibly present beside every code editor. A lesson run is ephemeral unless explicitly submitted as a `check` response.
- **LOCKED:** visual activity records semantic committed action/state snapshots only; no raw move telemetry.
- **RECOMMENDED:** “Predict first” is shown before Run when an authored learning activity requests it; it must be skippable only if the activity explicitly allows exploration without a prediction.

### D. Authoring and audit

```
DRAFT → VALIDATE (shape + lint + quality) → PREVIEW → DIFF
DIFF → REJECT / REVISE → DRAFT
DIFF → APPROVE → WRITE_ONE_UNIT → AUDIT_EVENT → PUBLISHED
DIFF → FULL_AUTONOMY_WRITE (only explicit opt-in, all gates pass) → AUDIT_EVENT
PUBLISHED → UNDO → REVERTED (compensating write/event)
```

- **LOCKED:** `report_only` never exposes a publish control. `draft_and_approve` cannot write without an explicit per-unit approval. `full` retains identical citations, lint, quality, diff, and volume reporting.
- **LOCKED:** retry-cap exhaustion retains a report/draft and writes no partial prefix.

---

## 6. Annotated Wireframes

### Learning workspace (desktop)

```
┌─ ContextLine ─────────────────────────────────────────────────────────────┐
│ EMT › Airway | OPA indications | 3 / 8 | Practice | [Details]              │
├───────────────────────────────────────┬───────────────────────────────────┤
│ [A] ActivityCanvas                    │ [B] Contextual support            │
│ Lesson heading                         │ Goal: distinguish OPA/NPA          │
│ prose / table / equation / code        │ Prereq: airway reflexes            │
│                                       │ [Why this item?]                   │
│ Question / visual / code editor        │ ─ Hints ─                          │
│ response controls [Check answer]       │ shown tier cards only               │
│ [C] feedback/status reserved here      │ [I'm stumped — show next hint]     │
│                                       │ ─ Agent (collapsed) ─              │
│ [D] Sources and evidence disclosure    │ source / uncertainty / retry       │
└───────────────────────────────────────┴───────────────────────────────────┘
```

`[A]` is keyboard first and is the focus landing point after navigation. `[B]` is supplementary, follows `[A]` in DOM order, and never takes focus after an ordinary submit. `[C]` is a single live-status region; it cannot preload correctness for diagnostic/exam. `[D]` labels source material and generated synthesis separately.

### Source-to-lesson intake and concept review

```
Source: [research-paper.pdf / normalized text]  fingerprint · locator fidelity
┌─ Claims and definitions ───────────┐ ┌─ Concept map ──────────────────────┐
│ Claim 12 [source p.4 ¶2]            │ │ prerequisite → concept → objective │
│ confidence: low · contested         │ │ [inspect evidence]                 │
│ A says … / B says …                 │ └───────────────────────────────────┘
│ [Review sources] [Mark for human]   │ ┌─ Proposed learning sequence ───────┐
└────────────────────────────────────┘ │ objectives · examples · checks       │
                                      │ Generated, not source-authored       │
                                      │ [Preview learner renderer]           │
                                      └──────────────────────────────────────┘
```

**RECOMMENDED:** this is an author/reviewer surface in Phase 11, not an automatic learner course generator. “Unsupported,” “ambiguous,” and “needs human review” are filterable first-class rows.

### Day/report recommendation

```
Today: 2 objectives recommended              Anki: 18 reviews, 4 new (external)
┌────────────────────────────────────────────────────────────────────────────┐
│ Airway adjuncts · Due today                                                   │
│ Why: 2 misses in 7d; last successful evidence 18d ago; 6 events in window    │
│ Confidence: sufficient evidence  [Review evidence] [Start practice]          │
├────────────────────────────────────────────────────────────────────────────┤
│ Medication calculations · Unknown                                              │
│ Not enough evidence to call this weak or stable. [View history]               │
└────────────────────────────────────────────────────────────────────────────┘
Daily cap: 3/4 activities for EMT. [Override for this sitting…] (confirmation)
```

No aggregate “mastery score,” streak, or decorative chart appears above the next instructional action.

### Authoring approval

```
Request → lint/quality results → preview in real learner renderer → diff
┌ Findings ──────────────┐ ┌ Learner preview ───────┐ ┌ Proposed change ──────┐
│ 0 lint errors           │ │ shared activity canvas  │ │ + one item             │
│ 1 quality warning       │ │ sources/provenance      │ │ citations + fingerprint│
│ [inspect]               │ └────────────────────────┘ │ [Reject] [Approve…]   │
└────────────────────────┘                               └─────────────────────┘
```

Approval opens an explicit confirmation naming the one reversible unit. Success returns a write id and `Undo this write`; it never silently publishes a batch.

---

## 7. Visual Direction and Tokens

### System

| Property | Contract |
|---|---|
| Tool | None — stdlib Python with embedded HTML/CSS/vanilla JS. No shadcn, registry, npm, or external component dependency. |
| Component approach | Native semantic HTML first; inline SVG for initial visual items; vendored KaTeX only in Phase 9. |
| Font | `system-ui,-apple-system,"Segoe UI",Roboto,sans-serif`; `ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace` for code/identifiers. **These two stacks remain the fallback tail of every voice token below, so an absent vendored face renders exactly this.** |
| Voice tokens | No surface may name a font family literally. Every rule uses `var(--font-paper|--font-ledger|--font-chrome|--font-code)`. Ownership: `surfaces/theme.py` = color only (unchanged); `surfaces/presentation.py` SHARED_CSS = voice/measure/radius tokens and any `@font-face`. |
| Motion | 150ms maximum functional transitions; no autoplay/looping motion; `prefers-reduced-motion: reduce` removes transition/animation. |

### Tokens

**LOCKED:** Phase 4’s `surfaces/theme.py` is the single palette source. Persist source accent; derive contrast-correct light/dark tokens and show adjustment before save. Correct, incorrect, warning, unknown, and pending are semantic tokens independent of the accent.

| Token | Value | Use |
|---|---:|---|
| `space-1..7` | 4, 8, 16, 24, 32, 48, 64px | Only spacing scale; 44px minimum interactive target. Dense day cells may be 36px only with a neighboring 44px target. |
| `text-xs` | 12px / 1.4 | labels, provenance, compact status |
| `text-body` | 16px / 1.5 | prose, response, explanatory copy |
| `text-lesson` | 18px / 1.65 | **added 2026-08-10.** Sustained authored lesson prose only (Paper voice). Recorded reason: 16px system-ui is right for UI copy, but sustained serif reading sits best at 17–19px, inside Butterick's 15–25px / 120–145% window. Not a general fifth UI size; a surface that is not lesson prose still uses `text-body`. |
| `text-heading` | 20px / 1.2 | section/activity heading |
| `text-display` | 32px / 1.1 | page result/major report heading only |
| `--weight-normal` | 400 | body, prose, every default string |
| `--weight-emphasis` | 600 | headings, labels, primary action, table headers — the *only* emphasis tier |
| surface 60% | `--bg`, `--ink` | page field, reader, primary text |
| surface 30% | `--card`, `--chip`, `--line` | panels, sticky context, tables, disclosures |
| accent 10% | derived `--accent`, `--accent-soft` | focus rings; current/selected navigational text; explicit primary action; source-link affordances; never correctness, mastery, warning, or all buttons |
| semantic | `--ok`, `--bad`, `--warn`, `--unknown`, `--pending` | paired with text/icon/structure; never color alone |

**RECOMMENDED reconciliation:** Phase 4 tokens become the cross-surface default. Existing 03 reader and 05 editor may retain their documented local size/details where required for compatibility, but new components use the four sizes above. Do not introduce a third font weight or a second literal-hex palette.

#### Weight ruling — 2026-08-10, LOCKED, supersedes the prior "400 regular / 700 bold" row

The superseded row said `400 regular, 700 bold`. **The shipped code says otherwise and the code
wins**, because Phase 4's own redesign is what produced it. Measured this session across
`surfaces/`, excluding `__pycache__`:

| Weight | Occurrences | Where |
|---|---:|---|
| `600` | 37 | including **14 of 14** in `surfaces/presentation.py`, the shared primitive layer every new surface builds on |
| `700` | 4 | `day.py:536`, `day.py:564`, `lesson.py:69`, `quiz_page.py:155` |
| `400` | 2 | explicit resets |
| `500` | 1 | `day.py:569` |
| `800` | 1 | `study.py:99` |

**Ruling: the pair is `400` / `600`.** Three reasons, in order of weight:

1. **`presentation.py` is unanimous at 600 and is the layer everything inherits.** Ruling 700
   would mean rewriting the shared primitives and every surface that matches them — churn paid
   for a number, with no visual problem reported. Ruling 600 makes 4 sites move instead of 37.
2. **The prior row was never true of the product.** It described an intent that the Phase 4
   redesign did not follow. A spec line that no shipped surface obeys is stale, not authoritative,
   and enforcing it retroactively would be enforcing a typo.
3. **600 is the better semibold for a serif Paper voice.** Source Serif 4 is a variable face with
   a genuine 600 master, so the emphasis tier is a real design, not a synthesis.

**The Quattro consequence, stated rather than discovered later.** iA Writer Quattro is
*[ASSUMED, not verified this session]* shipped as 400/700 only, with no 600 master. A `600`
request against it therefore resolves **up to its 700 bold** by ordinary CSS font matching — a
deterministic selection, not a synthesized weight, and still **one** emphasis tier rather than
two. Verify the shipped weight set as part of §7.4's pre-fetch checklist; if Quattro ever gains a
600 master the token needs no change.

**What this makes non-conforming.** The six sites below are the entire cleanup, and the two-weight
rule is not currently true under *either* candidate — `500` and `800` are strays regardless:

| Site | Now | Becomes | Note |
|---|---|---|---|
| `surfaces/day.py:536` `.streak` | 700 | 600 | |
| `surfaces/day.py:564` `.chip b` | 700 | 600 | |
| `surfaces/day.py:569` | 500 | 600 | a genuine third weight |
| `surfaces/lesson.py:69` `th` | 700 | 600 | matches `presentation.py:97` |
| `surfaces/quiz_page.py:155` `.score` | 700 | 600 | |
| `surfaces/study.py:99` `.done .big` | 800 | 600 | a genuine fourth weight |

**Specs for already-executed phases are left as written.** `02`, `02.1` and `03` carry `700` rows
describing surfaces that shipped. Rewriting them would misreport what was built. They are historical
record; this ruling plus the cleanup table above is the authority, and the six sites it names are
exactly the surfaces those phases produced. Every *pending* phase spec (`03.1`, `05`, `06`, `06.1`,
`07`, `08`, `13`) was amended to 400/600 on 2026-08-10.

This is a mechanical substitution owed as a Phase 4 cleanup task. It is **not** authorized as an
incidental edit: `surfaces/` is shipped code and Phase 4 is mid-execution, so it goes through a
GSD workflow like any other change. Until it lands, a phase spec cites this ruling and does not
re-litigate it.

---

### 7.1 Voice, measure, and radius tokens — added 2026-08-10

**Source:** `.planning/research/2026-08-09-visual-design.md` §8–§9 ("Paper & Ledger"). **LOCKED,
restated:** `surfaces/theme.py` remains the single palette source and is never replaced. The tokens
below are *not colors*; they live in `surfaces/presentation.py` SHARED_CSS, which is why they can
land without touching the palette owner.

**These tokens land now and do not depend on Ruling 1.** Each family name resolves through a
fallback chain whose tail is the stack already shipped in the System table above, so with no
vendored file present every surface renders **byte-for-byte today's look**. That degradation
property is the whole reason the direction is safe to adopt before the typefaces are ruled on.

| Token | Value | Use |
|---:|---|---|
| `--font-paper` | `"Source Serif 4", Georgia, "Times New Roman", serif` | **Paper voice** — the author (human, or an approved and human-accepted AI write): lesson prose, item stems, options, rationales, `[!KEY]` and `[!EXAMPLE]` bodies, `## SCENARIO` stage prose, `<dfn>` glosses. |
| `--font-ledger` | `"iA Writer Quattro", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` | **Ledger voice** — what the runtime *asserts*: verdict strings, evidence counts, hint-tier headers and the locked-tier label, `[SRC:]` provenance lines, snapshot/session/write ids, gate outcomes, `StatusNotice` copy, empty-state CLI commands, `[!CHECK:]` anchors, callout small-caps labels. |
| `--font-chrome` | `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` | **Chrome voice** — the tool: nav, buttons, form labels, settings, figure captions. Names the existing stack; changes nothing. |
| `--font-code` | `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace` | **Code voice** — the machine being studied: code blocks, learner code, canonical responses, raw-LaTeX fallback disclosure. Names the existing stack; changes nothing. |
| `--leading-lesson` | `1.65` | Paired with `text-lesson`; Paper voice only. |
| `--measure-prose` | `66ch` | Default authored-prose column. **Sits under, and does not relax, §8's LOCKED 72ch maximum readable measure.** |
| `--measure-wide` | `90ch` | Tables and code-result regions only; never authored prose. |
| `--r-1` / `--r-2` / `--r-3` | `6px` / `8px` / `12px` | Tokenizes the 6/8/12 literals already shipped in `theme.py` SETTINGS_CSS. No new radius value is introduced. |

**Semantic token completion — LOCKED shape, values ASSUMED.** §7's semantic row has always named
five tokens; `theme.py` ships only `ok`, `ok_bg`, `bad`, `bad_bg`, `warn`. The gap is closed here.
These three are the *only* palette-owner additions in this revision, they follow the existing
fixed-per-mode rule, and they are never derived from the learner accent.

| Token | Light (draft) | Dark (draft) | Meaning |
|---|---|---|---|
| `--warn-bg` | `#f8f1e2` | `#2b2312` | Completes the `ok`/`bad` background pattern; `--warn` already ships. |
| `--unknown` / `--unknown-bg` | `#566067` / `#edf0f2` | `#9aa7ad` / `#1b2325` | A *stated* state — "not enough evidence" — deliberately near `mut` but distinct. Never decoration, never `0%`. |
| `--pending` / `--pending-bg` | `#5b4a9f` / `#efecf7` | `#b3a3e6` / `#221c33` | "A review is pending. This attempt counts as work, not as mastery yet." |

- **ASSUMED:** the six hex values are drafts. Landing them requires `theme.py`'s own
  `contrast_ratio` to pass the existing WCAG floors in both modes, in a fixture, before merge. A
  failing draft is re-picked, not waived.
- **LOCKED:** `--unknown` and `--pending` obey the never-color-alone rule identically to
  `--ok`/`--bad`. Each requires an accompanying text label.

### 7.2 `--pending` is load-bearing — LOCKED

From round two R4.5, and binding on Phase 8 and every surface that displays a model-suggested mark:

1. A model suggestion renders as a **`--pending` token with its text label, and nothing else**.
2. It is **never** a number, **never** a fraction (`3/5`), **never** a check glyph, **never** a
   cross glyph, and never borrows `--ok` or `--bad`. A derived "4 of 5" may be computed at read
   time **only after a human accept**, at which point it is no longer pending.
3. It carries **no typographic voice of its own**. Generated text renders in **Chrome voice**
   inside the already-specified "Generated synthesis" labeled container. Paper voice is the
   author's; Ledger voice is the runtime's. A model gets neither — it is a guest, and the label
   plus the container say so.
4. A suggestion never accepted stays pending forever, influences no selection and no schedule,
   and grants no mastery.
5. The `suggestion_reveal` disclosure control (`after-self-mark` default; all three values ship
   per Directive §3) is a native `<details>`-class disclosure in Chrome voice. Its summary text
   must not preview the suggestion. Before reveal, the DOM contains no suggestion text — the same
   no-leak rule §8 already applies to unshown hint tiers.

### 7.3 The distinctive move — RECOMMENDED

**Typography encodes authority.** One glance says who is speaking: the author (Paper), the
runtime (Ledger), the tool (Chrome), or the machine under study (Code) — and the model, pointedly,
gets no face at all.

This is the one thing that makes the product look like itself rather than a template. It is not
decoration: it renders the project's core guarantee — *the runtime, not the model, decides what
reaches the learner* — visible on every screen without a word of explanation. A report whose
numbers are in Ledger voice reads as a sworn record; a lesson in Paper voice on the existing
paper-tinted field reads as authored teaching; the seam between them is the product's thesis. No
product in the studied set distinguishes system-guaranteed text from generated text typographically.

Corollary rules, so the move stays a rule and not a mood:

- The three templated tells the direction exists to avoid: one brand hue doing nav + link +
  success; every callout being the same tinted box in a different hue; Inter-or-system sans
  everywhere plus card grids. Callout *kinds* (`[!NOTE]`, `[!KEY]`, `[!WARNING]`, `[!EXAMPLE]`,
  `[!SRC]`, `[!CHECK:]`) are distinguished by **icon + Ledger-voice small-caps label + structure**,
  with color as a secondary channel only — which the never-color-alone rule already forces.
- Voice is assigned by **who authored the string**, never by visual preference. A new surface that
  cannot say which of the four voices a string belongs to has found a spec gap, not a free choice.
- Two weights per face — `--weight-normal` 400 and `--weight-emphasis` 600 per the §7 weight
  ruling. The direction adds no third weight and no second palette. A face without a 600 master
  resolves up to its bold by CSS font matching; that is still one emphasis tier, not two.

### 7.4 Vendored typeface asset note — 2026-08-10, GATED ON RULING 1

**Status: NOT ADOPTED. No font file is downloaded, vendored, staged, cached, or committed by this
revision.** §7.1 lands regardless; this subsection is the standing record of what a `yes` on
Ruling 1 ("adopt Paper & Ledger, vendor Source Serif 4 + iA Writer Quattro under OFL") would
authorize, and it is inert until that ruling is recorded.

**Precedent followed:** the KaTeX exception — the goal forbids network *services*, not vendored
*files* — and the Phase 9 supply-chain gate at `09-03-PLAN.md`, a blocking, metadata-only human
checkpoint that records an exact immutable version, a published-tarball SHA-256, official source
ownership, the license result, and a complete distribution inventory before 09-04 is permitted to
fetch a single byte. A font vendoring runs that same shape.

**License verification performed 2026-08-10** (metadata only; upstream LICENSE files read, no font
binaries fetched):

| Face | Upstream | License | Copyright / Reserved Font Name | Verified |
|---|---|---|---|---|
| Source Serif 4 | `adobe-fonts/source-serif` (branch `release`, `LICENSE.md`) | **SIL Open Font License 1.1** (26 Feb 2007) | Copyright 2014–2023 Adobe; **Reserved Font Name "Source"** | 2026-08-10, primary source |
| iA Writer Quattro | `iaolo/iA-Fonts`, `iA Writer Quattro/LICENSE.md` | **SIL Open Font License 1.1** (26 Feb 2007) | Copyright © 2018 Information Architects Inc.; © 2017 IBM Corp.; **Reserved Font Names "iA Writer", "Plex"** | 2026-08-10, primary source |
| Atkinson Hyperlegible Next *(optional, B13 high-legibility Paper swap)* | Braille Institute | SIL OFL — **UNVERIFIED this session** | not read | ⚠ verify before it is ruled on |

- **OFL consequence, binding:** the Reserved Font Names forbid a modified or subset build from
  shipping under the original name. A subset must be renamed, or shipped unmodified. The OFL text
  ships beside the files.
- **Preconditions on a `yes` to Ruling 1**, each of which must be satisfied before any byte lands:
  exact immutable release tag; published archive SHA-256 recorded; OFL text vendored alongside;
  measured `woff2` byte sizes recorded (§13 A3 estimates of ~100–160KB serif / ~60–90KB duospace
  are **ASSUMED** and must be measured, not quoted); rendering verified at 18px in the 375px and
  1280px snapshot fixtures on Windows ClearType (A6).
- **Delivery, if adopted:** `@font-face` with `font-display: swap`, served by the local daemon from
  `/assets/fonts/*.woff2`. No CDN, ever. The static offline build **copies** woff2 beside the
  output HTML when present and never base64-embeds them; an offline sitting must never block on a
  font. Packaging treats them as checksummed static assets.
- **If Ruling 1 is `no`, or is never made:** nothing in §7.1–§7.3 is withdrawn. `--font-paper`
  resolves to Georgia, `--font-ledger` to `ui-monospace`, and every other rule — voice assignment,
  measure, `text-lesson`, the semantic tokens, the `--pending` rule — holds unchanged. The voice
  *distinction* survives at reduced contrast between the faces; only the sharpness is lost.

### Copywriting contract

| Situation | Required copy |
|---|---|
| Primary learner CTA | `Start practice` (when a recommendation starts a practice sitting); activity submit remains type-specific (`Check answer`, `Run code`, `Check response`). |
| Contextual agent CTA | `Ask for a different explanation` (only after an attempt or shown hint; never before the activity is visible). |
| Hint CTA | `I’m stumped — show the next hint` — LOCKED Phase 6 wording. |
| Sparse evidence | `Not enough evidence to make a recommendation yet.` Then: `Review the history or complete another activity.` |
| Model unavailable | `Generated help is unavailable. You can keep learning with the lesson and authored hints.` |
| Policy-blocked output | `Generated help is unavailable for this step. Continue with the available hint or try another attempt.` |
| Source conflict | `These sources do not fully agree.` Then show labels/locators and `Review sources`. |
| Pending mark | `A review is pending. This attempt counts as work, not as mastery yet.` |
| Destructive/reversible action | `Revert this write? This restores the previous version and records the reversal.` Confirmation button: `Revert write`. |
| Day force overwrite | Preserve Phase 4’s explicit second confirmation; default action is `Reload and reapply`, never last-writer-wins. |

**Unchanged by the 2026-08-10 revision.** Every row above is LOCKED and was neither edited nor
re-voiced. Voice assignment changes the *face* a string renders in, never its wording. Model
unavailable, policy-blocked, sparse evidence, and pending-mark copy render in Ledger voice; the
strings are verbatim.

### 7.5 Section 7 checker sign-off — re-run 2026-08-10

Re-run against this revision only. The document-level sign-off at the end of this file is
unchanged and still governs the whole contract.

- [x] **Copywriting contract checked** — untouched. No string added, removed, or reworded. §7.2
      adds a *rendering* prohibition (never a number/fraction/check/cross for a pending
      suggestion), which constrains presentation, not copy.
- [x] **Visual hierarchy and responsive behavior checked** — `--measure-prose 66ch` sits under §8's
      LOCKED 72ch maximum; `--measure-wide 90ch` is scoped to tables and code results, never prose.
      No breakpoint, column ratio, or DOM-order rule changed. `text-lesson 18/1.65` is verified at
      375px and 1280px by the existing snapshot gate (§11.4), which this revision does not relax.
- [x] **Color/semantic-token usage checked** — `theme.py` remains the single palette source and is
      not replaced. `--unknown`, `--pending`, `--warn-bg` complete the five-token set §7 already
      named; fixed per mode, never derived from the learner accent, never color alone. Hex values
      are ASSUMED drafts gated on a `contrast_ratio` fixture. No second literal-hex palette.
- [x] **Typography and spacing token usage checked** — spacing scale untouched. Two weights per
      face; no intermediate weight introduced. One new size (`text-lesson`), scoped to authored
      lesson prose with a recorded reason inside Butterick's window. Four voice tokens name two new
      families and two existing stacks; no surface may name a family literally. Radius tokens
      tokenize shipped literals and add no new value.
- [x] **Accessibility/assessment-integrity gates checked** — §8 is untouched and remains LOCKED.
      No-leak extends to `suggestion_reveal`: no suggestion text in the DOM before reveal, and no
      preview in the summary. Fallback chains guarantee that a missing font degrades to today's
      rendered look, so no gate depends on a vendored asset. Atkinson Hyperlegible Next remains an
      opt-in Paper-voice swap, not a substitute for the WCAG floors.
- [x] **Registry safety checked** — unchanged. No component registry, no npm, no CDN. The only new
      third-party artifacts contemplated are two OFL 1.1 font files, and they are **not vendored by
      this revision**; §7.4 gates them on Ruling 1 behind the KaTeX-precedent supply-chain
      checkpoint.

**Section 7 approval:** token extensions (§7.1–§7.3) **adopted, effective 2026-08-10**. Typeface
vendoring (§7.4) **pending Ruling 1**; unruled means not vendored, and nothing else is blocked.
Draft hex values pending a contrast fixture. Atkinson Hyperlegible Next license pending
verification.

---

## 8. Responsive, Offline, and Accessibility Contract

### Responsive behavior

- **Desktop:** two-column learning workspace; code editor can be full canvas width; 72ch maximum readable prose measure.
- **Tablet:** support moves after activity as an in-flow disclosure; code results and SVG remain full-width; touch targets ≥44px.
- **Narrow:** no hover-only controls; focus/active equivalents visible; tables preserve headers using horizontal-scroll wrappers with an accessible name or stacked definition rows. Code editor keeps horizontal scrolling rather than wrapping logical lines.
- **Long content:** prose wraps; IDs and code may horizontally scroll; source citations wrap without ellipsis; all chip/meta text can wrap to a second line.

### Accessibility and assessment validity

1. Native controls and semantic headings precede ARIA. Every control has a visible label; placeholders are never the only label.
2. Keyboard path: global navigation → ContextLine details → activity heading → response/manipulation → submit/hint → feedback → support/evidence. No keyboard trap, including editor Tab handling (Tab remains insertion only inside the code editor; Escape/explicit control returns to normal navigation).
3. Focus: 2px accent outline with offset; do not remove outline. After submit, keep focus on submitted control unless an error needs focus; status is announced without a focus jump.
4. Screen readers receive the same task, legal actions, response state, hints already shown, and result. They never receive key, unshown hint text, hidden visual target, or delayed diagnostic/exam correctness via hidden labels, alt text, CSS-off content, title attributes, or live regions.
5. Visual items require an equivalent semantic control path: e.g., numberline value input/step controls plus described current state; plot point list/coordinate inputs plus visible SVG. The equivalent is scored through the same canonical response.
6. Math includes accessible rendered expression plus raw LaTex/source disclosure on rendering failure. Code retains line/column context without treating gutter decoration as the sole reference.
7. Status semantics: one `role=status` region for normal updates; `role=alert` only for blocking errors. Announce state changes once, not on each visual animation frame.
8. Contrast meets WCAG AA at minimum for text and controls; semantic status has text and structural differentiation. Motion is optional/functional.
9. Offline/degraded state preserves readable lesson/source and authored feedback. Run/model-only actions become explicit unavailable controls; do not render a disabled button with no reason.

---

## 9. Agent Interaction Boundaries

| Agent may | Agent may not | UI proof |
|---|---|---|
| Ask one diagnostic question tied to current response/objective. | Replace the activity with generic chat. | AgentAssist is contextual and collapsed; ActivityCanvas remains primary. |
| Select among permitted explanation forms (analogy, example, counterexample, visualization, derivation, simulation, Socratic question) after the runtime grants a tier. | Reveal higher-tier/key content, decide tier, or imply a score. | Each message shows source/type and permitted-tier-derived state; gate `drop` never displays text. |
| Admit uncertainty, cite sources, and show conflict. | Present generated curriculum/synthesis as source-authored. | “Generated synthesis” label plus citations/locators/conflict card. |
| Propose rubric points and authored drafts. | Write accepted marks, select items, or publish content without runtime/human authorization. | Pending review, DiffApproval, actor/audit event, autonomy banner. |
| Fail or become unavailable without halting authored loop. | Retry indefinitely or conceal a provider/tool failure. | Typed StatusNotice, explicit learner retry, interaction id/history. |

---

## 10. Acceptance Scenarios

Each scenario is a mandatory integration/UAT fixture. “Model involvement” must be observable in the evidence/audit path even when it is `none`.

| # | Goal and visible state | Action → response | Evidence / model / enforcement | Error, recovery, accessibility, acceptance |
|---|---|---|---|---|
| 1 | EMT learner distinguishes two clinically similar conditions. Workspace shows structured prose/table, objective, current prerequisite, and a pre-answer item. | Learner chooses a condition, receives a wrong held state, then uses a bounded hint and retries. | Record semantic response, mode, attempt count, shown tier, source/ref. Model optionally provides gated augmentation; runtime scores and controls tier. | If model is absent, authored ladder remains. Keyboard/table reading works; no hidden correct condition. **Pass:** learner reaches correct retry and report says correct-after-tier, not just correct. |
| 2 | Math learner sees an intuition prompt before a symbolic derivation; equation renders locally with source fallback. | Predicts relation, manipulates/answers, opens derivation only at legal hint/explanation stage. | Record prediction/response/hint events; no browser math scoring; runtime verifier decides. | KaTeX failure shows readable raw expression. Keyboard user completes equivalent symbolic response. **Pass:** no CDN, no premature derivation/key in DOM, correct verdict comes from runtime. |
| 3 | CS learner sees code editor, line gutter, hidden-case count, and honest execution limits. | Predicts behavior (when authored), edits, Tab-indents, runs, reviews per-case result. | Record source submission and final execution/result vector; model none by default; runner-before-scorer and runtime dichotomous verdict. | Timeout/output cap/LAN/static-file failure offers exact recovery message; source remains visible. **Pass:** 500-line test keeps gutter aligned; keyboard-only learner runs/reviews without hidden expected outputs before submit. |
| 4 | Learner/reviewer imports difficult paper; claims, locators, confidence, and disagreement are visible. | Inspects conflicting claims, marks one for human review, previews proposed objective map. | Store source fingerprint, locator, extraction/audit events; agent may synthesize/cite; deterministic ingestion contract labels source vs synthesis. | Unsupported/lossy source becomes unavailable with no fake locator. **Pass:** generated objective is never labeled source-authored; contested claim cannot become covered without cited evidence. |
| 5 | Learner gives plausible wrong answer in practice and sees held cursor, their answer, and one legal next action. | Chooses `I’m stumped — show the next hint`, then submits materially changed retry. | Hint event includes unlock path; response includes tier/mode; model augmentation only after gate pass; runtime enforces one tier/attempt. | Duplicate/empty retry says what is required without tier advancement. **Pass:** no tier 2–5 text/ARIA appears before unlock and report distinguishes stumped from ordinary wrong. |
| 6 | Screen-reader and keyboard-only learner completes equivalent conceptual visual task. | Uses labeled coordinate/numberline controls and submits; hears result/status once. | Record same canonical semantic response as pointer path; model irrelevant; runtime scores. | SVG/canvas failure retains semantic controls and no target/key leaks in alt text. **Pass:** pointer and keyboard paths produce identical score/evidence for matching response. |
| 7 | Provider becomes unavailable during an active session; authored activity remains visible. | Learner requests generated support; sees typed unavailable notice and selects authored hint/retries. | Log interaction outcome/timing/backend without secrets; model unavailable; runtime continues scoring/hint policy. | Explicit retry is possible once, parent-linked; no spinner forever. **Pass:** lesson, submit, authored ladder, evidence, and report remain usable with network disabled. |
| 8 | Auditor identifies genuine coverage gap without publishing. | Reviewer inspects objective, citations, candidate material, and real learner preview; rejects or drafts. | Audit report includes source/bank fingerprints, exact source spans/item IDs; model may propose but report_only forbids write. | Missing citation is `unknown`; quality/lint errors retain draft. **Pass:** no bank mutation/commit/write event occurs in report_only, and a real gap is traceable to source. |
| 9 | Sparse history prevents confident trend recommendation. | Learner opens Today/Report, reads unknown state, inspects history, may start ordinary practice. | Record snapshot marker/window/event count; no model required; scheduler derives `unknown`. | Missing Anki signal is separately omitted/labeled, never treated as zero. **Pass:** no weak/mastered label or numeric mastery claim is shown below threshold. |
| 10 | Fourth subject profile is added without separate loop. | Admin selects/configures profile; learner opens lesson/activity with unsupported capability notice where necessary. | Session records profile/subject; model optional; runtime/parser/scorer/selector unchanged. | Unknown media shows escaped source + unavailable notice; profile validation explains bad config. **Pass:** synthetic fourth profile needs configuration/assets only, passes lesson→attempt→hint→retry→evidence fixture with no new surface module. |

---

## 11. Required UI Verification Gates

Every browser-facing plan must include:

1. **Public-payload inspection:** fixture asserts no key, unshown tier, accepted visual target, expected code output, or diagnostic/exam verdict is present in HTML, JSON, ARIA, CSS-off text, or accessible names before legal disclosure.
2. **State fixture:** happy, loading/in-flight, empty, error, partial, overflow, and long-text states relevant to its component. Error copy gives an actionable recovery.
3. **Keyboard/screen-reader equivalent:** directly test focus order, control labels, status announcements, and equivalent semantic response for visual interactions.
4. **Responsive snapshots:** 1280px desktop, 768px tablet, and 375px narrow view for the global shell plus changed component. Verify no clipped primary action or inaccessible table/code result.
5. **Offline/degraded fixture:** network/model/daemon capability as applicable; demonstrate authored loop continuity or an honest non-answerable refusal.
6. **Evidence trace:** confirm visible state/action maps to the expected append-only event and that model proposal, human acceptance, and deterministic score remain distinct.

### UI consideration coverage

| Surface | Empty / loading / error | Partial / overflow / long text | Verification |
|---|---|---|---|
| Lesson/reader | no lesson; source loading; missing/unsafe source | unfinished source, long headings/tables/code | explicit fixture + keyboard heading navigation |
| Activity/hints | no legal authored hint; submitting; typed unavailable/drop | shown-stack grows; long rationale | explicit no-leak DOM test |
| Visual/code | unsupported/empty authored capability; running/failure | many case rows, long output, 500 lines | backstop visual fixture at all widths |
| Today/report | no evidence; snapshot loading; external signal absent | mixed unknown/known objectives, long rationale | explicit provenance/unknown fixture |
| Auditor | empty queue; validation/retry failures | partial citations, large diff, long source locator | explicit report-only/no-write fixture |

---

## 12. Roadmap and Requirement Gaps

1. **OPEN — source-ingestion learner journey:** requirements define audit ingestion but not whether difficult-source intake is a learner-initiated route, an author-only route, or both. This contract assumes Phase 11 author/reviewer first; do not make it a learner self-service publishing flow yet.
2. **OPEN — agent dialogue scope:** requirements require diagnostic/error-specific teaching but do not define conversation history, retention, or prompt-injection handling for a freeform chat surface. Ship contextual single-turn assistance in the tracer; defer persistent chat.
3. **OPEN — visual item taxonomy and author grammar:** 06.1 specifies plot/numberline tracer but future manipulatives need a versioned catalog, supported semantic actions, tolerance representation, and accessibility equivalence rules before a gallery expands.
4. **OPEN — PDF/DOCX locator fidelity:** Phase 11 permits them only if stable locators/fidelity fixtures hold. Do not promise a UI upload path until this is proven; Markdown/UTF-8 is first-class.
5. **OPEN — learner-facing manual-mark workflow:** pending-review semantics are locked, but the authorizing human’s surface, permissions, and concurrency behavior need a dedicated Phase 8/11 plan section.
6. **RECOMMENDED requirement clarification:** `SCHED-04` says completed lessons enter a queue, while Phase 10 context focuses objective scheduling. Define the lesson-completion evidence and default hand-set interval before a schedule UI is built.

## 13. Do Not Build Yet

- Persistent chat transcripts, agent memory, autonomous follow-up messages, or a generic chat-first tutor.
- Any freeform “generate a course and publish it” command; Phase 11 begins report-only / draft-and-approve.
- A mastery percentage, BKT/FSRS model, predictive learning analytics, or false precision over sparse history.
- A separate EMT/Math/CS shell, scorer, runner, parser, or evidence schema.
- Canvas-only visual assessment, bank-authored executable JavaScript, raw pointer telemetry, or a visual renderer that infers correctness.
- PDF/DOCX upload/extraction UI until locator fidelity is validated under the stdlib constraint.
- Automated acceptance of model rubric suggestions, autonomous scoring, or model-driven selection/tier progression.
- Anki schedule mutation, leaderboard, streak mechanics, gamified rewards, telemetry, cloud sync, or content marketplace.
- “Sandboxed” execution language or any UI that overstates Phase 5’s process bounds.

## 14. Production-Quality Vertical Tracer

**Tracer: one practice-mode EMT activity with a Phase 3 lesson, a Phase 6 authored hint, and an optional Phase 8 unavailable-model fallback.**

1. Open a synthetic lesson at a deep link; keyboard navigation reaches heading, source citation, and linked item.
2. Enter one learner attempt on an auto-scorable EMT item; runtime returns held state and tier-0 lesson pointer on a genuine wrong answer.
3. Use the explicit stumped action or changed retry; show accumulated authored hints only; run no model or simulate its typed unavailable result.
4. Submit a correct retry; append response/hint evidence and show report phrase “correct after tier N,” with evidence drawer.
5. Execute desktop/tablet/narrow, offline/model-unavailable, screen-reader/keyboard, and no-key-in-public-payload verification.

**Why this tracer — RECOMMENDED:** it proves the platform’s differentiator (runtime-bounded teaching), Phase 3/4/6 interoperability, no-answer-leak accessibility, evidence semantics, and degraded behavior before the higher-risk model, visual, scheduler, and authoring surfaces expand.

### Phased prototype sequence

| Step | Build | Exit evidence |
|---|---|---|
| 1 | Shared shell/tokens + tracer above | all six verification gates pass |
| 2 | Code editor and SVG numberline/plot adapters | same semantic/evidence loop through keyboard, touch, and pointer paths |
| 3 | Typed adapter status/provenance and subject profiles | model unavailable/drop plus fourth-profile fixture pass |
| 4 | Today/report recommendation cards | unknown/sufficient evidence and Anki separation pass |
| 5 | Author/audit report-only → approval UI | source→claim→diff→one reversible write is inspectable |

---

## Registry Safety

| Registry | Blocks used | Safety gate |
|---|---|---|
| None | None | Not applicable. This project uses no component registry, npm, or third-party UI blocks. |

## Checker Sign-Off

- [ ] Copywriting contract checked
- [ ] Visual hierarchy and responsive behavior checked
- [ ] Color/semantic-token usage checked
- [ ] Typography and spacing token usage checked
- [ ] Accessibility/assessment-integrity gates checked
- [ ] Registry safety checked

**Approval:** pending cross-phase UI verification
