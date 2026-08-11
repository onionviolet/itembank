---
phase: 10
slug: retention-pacing-trends
status: approved
reviewed: 2026-08-08
shadcn_initialized: false
preset: none
created: 2026-08-08
---

# Phase 10 — Retention, Pacing & Trends UI Design Contract

> This contract turns evidence-derived scheduling into a calm, inspectable learning surface. It supplements the approved cross-phase UI contract and the Phase 04 token contract; locked Phase 10 decisions win.

## Decision Legend and Authority

| Label | Meaning |
|---|---|
| **LOCKED** | Requirement or Context decision; implementation may not weaken it. |
| **UPSTREAM-CONTRACT** | Pure data/API work may proceed before a browser surface. |
| **UI-BLOCKED** | Browser work may not ship until this contract and its verification gates pass. |
| **RECOMMENDED** | Prescriptive UX decision for this phase. |
| **OPEN** | Keep a seam/fixture only; do not invent product behavior. |

**Authority boundary — LOCKED:** append-only live evidence is authoritative; `retention.py` is a disposable deterministic projection; the selector remains Phase 7's sole chooser; the browser only renders a server-issued snapshot. A recommendation is never a score, diagnosis, or mandate. Anki remains read-only card-review ownership; itembank owns only objective recommendations. Pending manual work counts toward pacing, never mastery; retracted events disappear. No model may make, approve, or alter a retention claim.

## Phase and Plan Gating Matrix

| Work | Classification | Gate / required output |
|---|---|---|
| Snapshot capture, settings bounds, pure state/weight/cap derivation | **UPSTREAM-CONTRACT** | Fixed synthetic snapshot fixtures including retraction, pending mark, local-day boundary, and byte-stable provenance. |
| Phase 7 weight handoff | **UPSTREAM-CONTRACT** | Explicit normalized map + same snapshot id in selector trace; exam mode remains evidence-neutral. |
| CLI JSON/plain report and `day` guard | **UI-DEPENDENT** | Exact copy/provenance fields from this contract; CLI is the recovery twin. |
| Today, focused-session, report, chart, objective drilldown, or cap-override browser surface | **UI-BLOCKED** | All Phase 10 UI gates, 1280/768/375 snapshots, keyboard/SR/no-leak/evidence tests. |
| Lesson-completion queue (`SCHED-04`) | **OPEN** | Do not render or infer completion until a versioned completion evidence event and lesson→objective seam are defined. |

## Goals and Information Architecture

**Goals:** (1) show today’s bounded next work without pressure; (2) make every label inspectable; (3) separate itembank objective work from Anki cards; (4) help a learner recover after a cap without a persistent bypass; (5) show honest longitudinal change, including unknown/conflict.

| Area | Contents | Primary action |
|---|---|---|
| Today | per-subject cap, itembank due objectives, separately labeled Anki due/new, snapshot summary | `Start focused session` |
| Focused session | one subject/objective recommendation and the existing Phase 7 explanation trace | `Start practice` / `Choose another objective` |
| Report overview | window selector, subject summaries, raw counts, pending review, no decorative score | `View objective` |
| Objective detail | series/table, state, at-risk reason, hints, weight influence, evidence drawer | `Show evidence` |
| Recovery | cap reached explanation, alternate non-ordinary activities, one-sitting override | `Request one-sitting override` |

## Major Interaction Contracts

| Interaction | Goal / state | Action → response | Evidence / model / enforcement | Failure and a11y | Acceptance |
|---|---|---|---|---|---|
| Due-today recommendation | Pick bounded objective work; `unknown`, `stable`, `weak`, `due`, `at-risk`, `mastered` | Select `Why this recommendation` → open adjacent `EvidenceDrawer`; `Start focused session` only when cap permits | Snapshot id, local-day zone, filters, window, event count, state components and normalized weight. Rule model only; no model. Runtime/selector enforce one snapshot and Phase 7 selection. | Snapshot load failure retains no actionable recommendation and links CLI report; disclosure is a native button/details after card in DOM. | Same snapshot id appears on card, drawer, start request, and selector trace; no claim lacks counts/window. |
| Anki separation | Compare unlike signals without merging ownership | Read labeled `itembank: N objectives recommended` and `Anki: D due · N new`; neither is a total | Anki is optional read-only input; itembank derives only objective state. Never write Anki or sum counts. | Anki unavailable: `Anki is unavailable; card counts are not shown.` not zero. Screen reader reads owner labels before counts. | Fixture proves unavailable, zero, and populated Anki states never alter itembank recommendation/cap. |
| Cap/recovery | Stop binging while preserving deliberate choice | At cap, ordinary start is blocked. `See recovery options` reveals lesson/report/review; `Request one-sitting override` opens confirmation | Live local-day, per-subject count includes pending manual events. Runtime records one override event scoped to launch/sitting; no model. | Network/model irrelevant. Dialog traps focus, Escape returns to trigger; cancellation makes no event. | Ordinary start rejects at cap; accepted override is visible in snapshot/evidence and expires at sitting end. |
| Honest trends/drilldown | Explain change, not forecast failure | Choose 1/4/8/12-week window → overview → subject → objective; table is canonical and chart is optional | Same immutable snapshot; rates always paired with attempts, pending count, highest/average hint tier, last evidence. At-risk requires prior success + silence, not prediction. | Sparse/conflict shows state card, never blank graph or fabricated slope; table remains accessible. | Synthetic sparse, mixed, retracted, pending and at-risk series produce deterministic text/table and provenance. |
| Manual review | Keep attempted work distinct from settled evidence | Select pending count → filtered rows marked `Pending manual review` | Pending affects pacing only; accepted human mark can enter later snapshot/mastery. Model proposals never settle it. | Long lists page-scroll; no manual-mark action is introduced here. | A pending-only objective is not weak/mastered and cap count still increases. |

## State Machines

```text
snapshot: loading → ready | unavailable
ready → insufficient(unknown) | derived(state + provenance)
derived → focused-start (cap allows) | cap-blocked → override-confirm → scoped-override → focused-start
derived → evidence-drawer → close (returns focus to invoking card)

objective: unknown ↔ stable ↔ weak/due ↔ mastered
           prior confirmed success + silence → at-risk
pending/manual/retracted modify inputs only; they never bypass the live-event projection.
```

`unknown` is a terminal presentation for the snapshot, not a zero value. `conflicting` is a presentation qualifier when components disagree; it displays the components and does not collapse them into a single certainty label.

## Annotated Wireframes

### Desktop (≥1024px)

```text
┌ Today · 08 Aug                     Snapshot S-… · 7d · 18 live events ┐
│ EMT  3/4 ordinary attempts     [Start focused session]                 │
│ itembank: 2 objectives recommended     Anki: 14 due · 3 new             │
├───────────────────────────────────────┬─────────────────────────────────┤
│ Due today                             │ Why this recommendation         │
│ Airway assessment  [due] [Why…]       │ last success: 29d ago            │
│ Evidence: 3/4 settled · hints 2.0     │ recent accuracy: 2/3             │
│ [Start practice]                      │ [Show 4 events]                  │
└───────────────────────────────────────┴─────────────────────────────────┘
```

Left activity column is primary; evidence is adjacent secondary content and follows it in DOM. Owner labels, textual state chips, and counts are never color-only.

### Tablet (768–1023px)

```text
Today · Snapshot S-…
EMT 3/4 · itembank 2 recommended · Anki 14 due / 3 new
[Start focused session]
Airway assessment — Due · 3/4 settled · [Why this recommendation]
<details>Evidence and settings-threshold explanation</details>
```

Evidence disclosure moves below the card; it does not become a modal dashboard.

### Narrow (<768px)

```text
Today
EMT: 3 of 4 ordinary attempts
itembank: 2 objectives recommended
Anki: 14 due · 3 new
[Start focused session]
Airway assessment [due]
3 of 4 settled; highest hint tier 2
[Why this recommendation]
```

State tables use a labeled horizontal-scroll wrapper; chart alternatives are a data table and text summary, never an image-only chart. The cap confirmation remains usable at 375px with buttons stacked and 44px targets.

## Reusable Component Inventory

| Component | Contract |
|---|---|
| `SnapshotStamp` | Snapshot marker, as-of time, local zone, event count, filter/window; visible on every derived surface. |
| `SignalCard` | Owner-prefixed itembank or Anki signal; disallows aggregation across owners. |
| `ObjectiveState` | Text label plus shape/icon; `unknown`, `weak`, `due`, `at-risk`, `stable`, `mastered`, `conflicting`. |
| `EvidenceDrawer` | Summary first, raw live-event link/CLI equivalent second; source data before inference. |
| `TrendSeries` | Text summary + semantic data table are mandatory; SVG line/bar is enhancement only and must not encode meaning solely by color. |
| `CapGate` | Runtime-issued block/allowed result, live count/cap, recovery links, one-sitting override confirmation. |
| `PendingReviewBadge` | Counts attempts for pacing, explicitly says it is excluded from mastery. |

## Responsive, Keyboard, Screen Reader, and Integrity Rules

- Use native buttons, `<details>`, headings, `<table>`, and `<dialog>` before custom ARIA. All controls are at least 44px; 36px dense day cells only have a neighboring 44px action.
- Tab order is Today action → objective card → Why button → evidence content; opening/closing an evidence drawer or override dialog restores focus to its invoker. Escape cancels an unconfirmed override.
- One `role=status` announces snapshot refresh, cap block, and start result; `role=alert` only announces a blocked start/error. State names and counts are read in text, never conveyed by color, trend direction, or chart position alone.
- Public DOM/API contains only derived public signals, never answer keys, hidden tiers, raw provider payloads, or a browser-side formula authority. Server rejects stale/forged snapshot, subject, cap, and override values.
- Offline/model-unavailable state does not block local evidence/report work. If Anki is unavailable, omit it with the locked explanatory copy; never cache it as current or zero.

## Design Tokens

Use the Phase 04 generated theme tokens; no new palette producer, package, registry, web font, chart, or icon library.

| Role | Value / usage |
|---|---|
| Spacing | 4, 8, 16, 24, 32, 48, 64px only; 16px card padding narrow, 24px wide. |
| Typography | 14px/400 metadata, 16px/400 body, 20px/600 section, 28px/600 display; 1.4/1.5/1.2/1.2 line-height. |
| Dominant 60% | `--bg`, `--ink`: page/read surface. |
| Secondary 30% | `--card`, `--chip`, `--line`: cards, evidence, tables, sticky context. |
| Accent 10% | `--accent`: only non-destructive primary action, focus outline, active filter, links, current context marker. |
| Semantics | `--ok`, `--warn`, `--bad` only with text/icon/border; `--bad` is reserved for destructive confirmation/error, not an at-risk objective. |

## Copy and Error Contract

| Element | Exact copy |
|---|---|
| Primary CTA | `Start focused session` |
| Evidence affordance | `Why this recommendation` / `Show evidence` |
| No evidence | `Not enough evidence yet` — `This objective has fewer than the settled attempts needed for a recommendation. Practice is still available; no mastery or trend is claimed.` |
| Conflicting signals | `Signals disagree` — `Review the evidence before changing your plan. This is not a prediction or a score.` |
| At risk | `At risk of needing review` — `You previously showed success, but there has been no confirming evidence for the configured interval.` |
| Pending | `Pending manual review` — `Counts toward today’s work, not mastery, until a human mark is accepted.` |
| Anki unavailable | `Anki is unavailable; card counts are not shown.` |
| Cap block | `Today’s {subject} cap is reached ({count} of {cap} ordinary attempts).` — `Review evidence, read a lesson, or request one additional sitting.` |
| Override confirmation | `Start one additional {subject} sitting?` — `This exception applies only to this sitting and will be recorded. It does not change your daily cap.` Buttons: `Start one additional sitting` / `Keep today’s cap`. |
| Report failure | `This report could not be derived from the current evidence snapshot.` — `Try again or run the report command; no recommendation was made.` |
| Chart fallback | `Trend table` — `The table is the complete report; the chart is an optional visual summary.` |

No streaks, points, badges, countdowns, praise animations, “catch up” pressure, or cramming prompts belong in Phase 10.

## Evidence and Determinism Contract

Every rendered claim carries `{snapshot_id, cutoff, local_day_zone, window, filters, live_event_count, settings_version}`. The rendered label, CLI JSON/plain twin, cap evaluation, objective detail, weight map, and Phase 7 trace use the same marker. A deterministic rule evaluates only captured inputs and schema-bounded settings; no browser recomputation, model inference, mutable cache, Anki count, or tick count can change it. The evidence drawer distinguishes observed facts, configured thresholds, and derived conclusion.

## UI Considerations

| Category | Element(s) | Status | Resolution |
|---|---|---|---|
| empty | Today/report objective list | ✅ covered | Renders `Not enough evidence yet`; ordinary practice remains available. |
| loading | Snapshot, Anki read | ✅ covered | One status line; recommendations/actions wait for server-issued snapshot; Anki remains separate. |
| error | Snapshot/report/start | ✅ covered | Actionable copy above; no stale or fabricated recommendation. |
| populated | Cards, table, trend enhancement | ✅ covered | Every row includes raw counts + provenance and owner label. |
| partial | Known/unknown mix and pending review | ✅ covered | Preserve per-objective state; pending excluded from mastery. |
| overflow | Tables and evidence event rows | 🧪 backstop | 1280/768/375 fixture verifies page scroll/labeled table wrapper and no clipped provenance. |
| zero-one-many | Due cards, Anki signal | ✅ covered | Singular/plural copy; zero is not unavailable; owners remain unsummed. |
| long-text | Objective names, at-risk reasons, citations | ✅ covered | Wrap prose; identifiers scroll only in their own code-like container. |

## Acceptance and Verification

### Shared ten-scenario relevance matrix

| Shared scenario | Phase 10 relevance / required evidence |
|---|---|
| 1. EMT held-hint loop | Regression only: report must distinguish the recorded mode/tier outcome without re-scoring it. |
| 2. Math local rendering | Regression only: subject/objective rows remain profile-neutral and provenance works when math renderer is unavailable. |
| 3. CS code execution | Regression only: code outcomes enter evidence through the same snapshot; no execution data becomes a retention authority outside evidence. |
| 4. Difficult-source audit | Cross-phase boundary: Phase 10 may prioritize already-defined audited objectives only; it cannot create a curriculum objective. |
| 5. Hint/retry loop | Direct: highest/average shown hint tier is an observed report field, not a mastery score. |
| 6. Accessible visual task | Regression only: semantic visual evidence appears as ordinary objective evidence; no renderer-specific scoring/chart logic. |
| 7. Model unavailable | Direct degradation: model outage cannot block Today, local report, evidence drawer, or cap guard. |
| 8. Report-only audit gap | Cross-phase boundary: a gap or candidate material cannot mutate Phase 10 state or cause automatic work generation. |
| 9. Sparse history | **Primary Phase 10 fixture:** unknown state, separate omitted Anki signal, ordinary practice remains available. |
| 10. Fourth profile | Regression: new configured subject uses the same snapshot, cap, state grammar, and CLI twin; no new scheduling surface. |

1. **Sparse/unknown:** fewer than configured settled attempts produces no weak/mastered/rate/graph claim; accessibility tree contains the explanatory copy.
2. **Due and separate ownership:** same snapshot renders itembank recommendation and Anki value separately; changing Anki result does not change weight/cap/due count.
3. **Pending/retracted:** pending increments pacing only; accepted mark changes a later snapshot; retraction disappears everywhere.
4. **Cap/recovery:** subject-specific cap blocks ordinary work; cancel writes nothing; confirmed override creates exactly one scoped event and expires with sitting.
5. **Trend honesty:** previously correct then silent becomes at-risk with reason; inconsistent inputs show conflict; all charts have table/text alternatives.
6. **Drilldown:** overview → subject → objective preserves same snapshot stamp and returns focus correctly.
7. **Integrity/offline:** output contains no key/model claim; Anki/model offline leaves evidence-derived work usable and honestly labeled.
8. **Responsive/a11y:** test 1280, 768, 375; keyboard-only complete focused start, drawer, drilldown, block/cancel/confirm override; SR hears owner/state/count/action.

Run deterministic `tests/retention_roundtrip.py` (new), relevant `tests/day_roundtrip.py`, daemon/report fixtures, and visual/a11y fixtures before marking browser work complete.

## Unresolved and Do Not Build

- **OPEN:** a lesson-completion event and transparent review-queue default are not yet defined; never infer completion from a page view.
- Do not implement card intervals/ease, write to Anki, predictive mastery/ML, a second selector, persistent cap-disable setting, browser-held formula, or a “smart” composite score.
- Do not make a chart the only representation; do not treat absence as zero; do not use Phase 10 labels for disciplinary, diagnostic, or punitive copy.

## Registry Safety and Checker Sign-Off

| Registry | Blocks used | Safety gate |
|---|---|---|
| None | None | Not applicable — stdlib HTML/CSS/JS and existing theme tokens only. |

- [x] Copywriting, visual hierarchy, color, typography, spacing: PASS
- [x] Responsive, keyboard, SR, integrity, offline, evidence gates: PASS
- [x] Registry safety: PASS

**Approval:** approved by `gsd-ui-checker` on 2026-08-08 (6/6 dimensions).
