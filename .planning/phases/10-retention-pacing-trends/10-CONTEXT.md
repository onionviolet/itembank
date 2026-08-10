# Phase 10: Retention, Pacing & Trends - Context

**Gathered:** 2026-08-08, updated 2026-08-10 (round-two research absorbed)
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase derives objective-level due, mastery, risk, and trend signals from the evidence store; feeds bounded weights into the Phase 7 selector; enforces a daily subject cap through `day`; and presents itembank and Anki due signals side by side without merging ownership. It does not schedule individual Anki cards or create a second evidence store.

Round-two scope (2026-08-10): FSRS is the scheduler baseline, derived by replaying the append-only evidence log (including Phase 3.1 `key_review` events); progress is named in WaniKani-style stages with a terminal "retired" state; due ordering is jpdb-style utility-weighted; return rate is the usage measure (never a streak); lesson-to-item transfer is recorded as deferred with its cost.
</domain>

<decisions>
## Implementation Decisions

### One evidence snapshot and provenance
- **D-01:** Every `day`, report, and selection-weight calculation for a render uses one immutable evidence snapshot marker. All displayed claims name the window, event count, and objective/subject filter behind them.
- **D-02:** Derived scheduling/trend state is disposable and reproducible from append-only evidence. Caches may accelerate reads but are never authoritative.
- **D-03:** Insufficient evidence is a first-class `unknown` state, not zero mastery, zero due, or a fabricated trend.

### Objective scheduling
- **D-04:** itembank schedules objectives, not cards. Each objective receives transparent signals for last successful evidence, recent accuracy, hint depth, pending review, and elapsed time; the planner/researcher chooses and documents the initial bounded formula.
- **D-05:** "Due today" is a labeled itembank recommendation with a reason and evidence basis. Anki due/new counts remain a separate labeled signal read in the same render snapshot; neither number is summed into the other.
- **D-06:** Objective states include due, at-risk, weak, stable, mastered, and unknown as derived labels over visible component signals. Thresholds live in settings with conservative defaults and schema bounds so later tuning does not require code changes.

### Daily cap and pacing
- **D-07:** `daily_cap` is enforced per subject using live evidence already recorded for the local day. Once reached, `day` blocks starting more ordinary work for that subject and explains the count.
- **D-08:** A deliberate override may coexist for exceptional use, but it must be explicit, time-limited to that launch/sitting, and recorded as an override event. There is no silent or persistent "ignore cap" toggle. This preserves user choice without making the cap cosmetic.
- **D-09:** Pending manual marks count as work attempted for pacing but not as success/mastery. Retracted responses disappear through the existing live-event filter.

### Selection feedback loop
- **D-10:** Phase 10 supplies a normalized objective-weight map and evidence snapshot to Phase 7's pure selector. It does not choose items directly or add another selector.
- **D-11:** Weak/missed objectives receive a bounded boost; mastered objectives receive a bounded reduction but do not become permanently unreachable. Recency/decay and difficulty-spread inputs compose with the Phase 7 trace so every chosen item can explain the influence.
- **D-12:** Changes are gradual and capped per snapshot to avoid one bad session causing an extreme next session. Exam selection remains evidence-neutral as Phase 7 decided.

### Trends and reports
- **D-13:** Longitudinal reports show accuracy by objective over selectable week windows, highest/average hint tier, attempts, pending manual review, last evidence date, and at-risk reason. Raw counts accompany rates.
- **D-14:** At-risk means previously demonstrated success plus a configurable period without confirming evidence; it is not predicted failure presented as fact.
- **D-15:** The report supports overview→subject→objective drill-down and a CLI JSON/plain-text twin. Visual chart form is delegated to UI planning; the underlying series and provenance contract are surface-neutral.
- **D-16:** Manual-review outcomes enter mastery only after accepted mark events. Model proposals from Phase 8 never affect scheduling until accepted.

### Round-two amendments (research absorbed 2026-08-10)
- **D-17 (FSRS baseline, ROADMAP criterion 7):** **FSRS is the scheduler baseline**, its state derived by **replaying the append-only evidence log** — including Phase 3.1's `key_review` events — rather than stored as mutable per-item scheduling rows. Rebuilding scheduler state from the log alone must reproduce it exactly. — **Reversibility:** one-way — evidence shapes are append-only; scheduler state stays derived, never authoritative.
- **D-18 (scheduler interface, ROADMAP criterion 8):** The scheduler sits behind **one interface with FSRS as the default registered strategy**, so a later algorithm change is a registered strategy plus a replay, not a migration.
- **D-19 (stages and utility weighting, ROADMAP criterion 9):** Progress is named in **WaniKani-style stages with a terminal "retired" state**, and due ordering is **jpdb-style utility-weighted** — legible, non-punitive motivation with no streaks and no points.
- **D-20 (return rate, ROADMAP criterion 10):** Return rate is this phase's usage measure and is deliberately **not a streak**: a ratio with a stated denominator (sittings that occurred over sittings that came due), a property of the system's pacing, not a judgement of the person. It is never shown with a target, never renders as a consecutive count, and never produces a loss state. The anti-streak rule in `10-UI-SPEC.md` holds over any tension.
- **D-21 (lesson-to-item transfer deferred, ROADMAP criterion 11):** Lesson-to-item transfer is the most interesting available measure and is **deliberately deferred** because it is not computable from the evidence log as it stands. Recorded with its cost so a later phase picks it up knowing why it was not built now.
- **D-22 (pending model suggestion, ROADMAP criterion 12):** A pending model suggestion from Phase 8 **never advances an interval and grants no mastery**, though it does count as an attempt. Scheduler state replayed from the log must read **accepted marks only** — this is where "what is due" is decided.
- **D-23 (pacing profiles preserved for future choice):** The initial formula ships as FSRS with visible, schema-bounded thresholds; if comparisons later show no single universally best pacing model, **multiple user-selectable profiles** may coexist behind the one scheduler interface (D-18), all inspectable, bounded, and reproducible. Defaults stay conservative; nothing is hidden behind a single "smart" score.
- **D-24 (SCHED-04 review-queue seam):** A completed lesson entering the review queue requires a **versioned completion evidence event and a lesson→objective seam** to be defined first. Completion is never inferred from a page view. The queue surface stays **OPEN / do not build** until that event exists (mirrors `10-UI-SPEC.md` gating).

### Future user choices (recorded now, selectable later)
- **Scheduler strategy:** FSRS (default) plus any registered alternative; switching is a strategy registration plus a replay, never a migration.
- **Stage/state presentation:** WaniKani-style named stages with terminal "retired" (default); labels remain text-plus-shape, never color-only.
- **Report chart form:** semantic data table is canonical; SVG line/bar is an enhancement only and must never be the only representation.

### the agent's Discretion
The initial formula coefficients, exact thresholds, profile names, and chart presentation require research and a stronger planning/UI model. All must remain inspectable, bounded, and reproducible. Not open: a second evidence store, writing Anki schedules, ML mastery models, streaks/points, or a persistent cap-disable setting.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase contracts and requirements
- `.planning/ROADMAP.md` § "Phase 10: Retention, Pacing & Trends" — goal, twelve success criteria, round-two rulings.
- `.planning/REQUIREMENTS.md` SCHED-01 through SCHED-04 and TREND-01 through TREND-05 — binding scheduling/trend behavior.
- `.planning/phases/10-retention-pacing-trends/10-UI-SPEC.md` — approved UI design contract: Today/focused-session/report/objective/cap-recovery surfaces, snapshot stamp, copy tables, anti-streak rules.
- `.planning/phases/10-retention-pacing-trends/10-RESEARCH.md` — retention.py derivation layer, FSRS/WaniKani/jpdb research support, validation architecture.
- `.planning/PROJECT.md` — objective-level ownership, Anki separation, and evidence-backed control-loop intent.

### Cross-phase context
- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — evidence/index/retraction contracts.
- `.planning/phases/07-selection-engine/07-CONTEXT.md` — pure selector, trace, profiles, hard/soft recency, and exam neutrality.
- `.planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md` — hint-tier evidence semantics.
- `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md` — pending model review cannot affect mastery.
- `.planning/phases/03.1-lesson-rich-blocks-glossary-style/03.1-CONTEXT.md` — `key_review` event type feeding the replay (D-19).
- `.planning/phases/06.2-executable-textbook-loop/06.2-CONTEXT.md` — gate outcomes as prioritization signals for the scheduler.
- `.planning/research/2026-08-09-landscape-widening.md` — FSRS, WaniKani stages, jpdb weighting.
- `.planning/research/2026-08-09-differentiators-d1-d2-d3.md` — D2 memorizables entering the queue.
- `.planning/research/2026-08-10-enforcement-and-loose-threads.md` and `.planning/research/2026-08-10-tiered-verdicts.md` — round-two scheduler/verdict rulings.

### Code seams
- `evidence.py` — objective history, subject filters, disposable index, live events, mark-state derivation, `key_review` event type.
- `surfaces/day.py` — existing cockpit, Anki due/new signal, lane load, and per-render state.
- `schemas/settings.schema.json` — existing `daily_cap` and `selection_weights` keys.
- `surfaces/report.py` or current report handlers, `surfaces/daemon.py`, and `surfaces/session.py` — report and selector integration points.
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/INTEGRATIONS.md`, and `.planning/codebase/TESTING.md` — derived-state and Anki degradation patterns.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `evidence.objective_history()` already supports objective, prefix, subject, mode, session, and time filtering with an indexed/fallback path.
- `live_events()` and mark derivation provide correct retraction/pending semantics.
- `day` already reads Anki due/new and degrades when Anki is absent.
- Settings already reserve bounded daily-cap and selection-weight groups.
- Phase 3.1's `key_review` event type is available as scheduler input; Phase 6.2's gate outcomes are prioritization signals.

### Established Patterns
- Derived indexes are disposable; append-only evidence is authoritative.
- Unknown external data is omitted/labeled, never guessed.
- Selector inputs are passed explicitly and traces explain decisions.
- Registries-plus-settings (TTSEngine, backend profiles) are the house style for swappable strategies.

### Integration Points
- New pure trend/scheduling derivation module (`retention.py`).
- `day` shared snapshot and cap guard.
- Phase 7 history/weights input and trace explanation.
- Longitudinal `/report` data endpoint plus CLI twin.
- Settings schema, provenance schema, and synthetic time-series fixtures.
</code_context>

<specifics>
## Specific Ideas

Keep both Anki and itembank signals visible because they answer different questions. Preserve multiple pacing profiles only if they can share one transparent component model; do not hide uncertainty behind a single "smart" score. Scheduler state must be reproducible from the evidence log alone (FSRS replay), and the usage measure is return rate with a stated denominator — never a streak (Weibao's standing directive: comprehensive, future-selectable, no unnecessary stoppage).
</specifics>

<deferred>
## Deferred Ideas

- Owning card intervals/ease or writing Anki schedules — out of scope for this milestone.
- Predictive ML mastery models — defer until evidence volume justifies them.
- Curriculum coverage auditing — Phase 11.
- Lesson-to-item transfer measurement — recorded with cost (D-21); needs a lesson→objective evidence seam first.
</deferred>

---

*Phase: 10-retention-pacing-trends*
*Context updated: 2026-08-10*
