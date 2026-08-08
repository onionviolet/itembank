# Phase 10: Retention, Pacing & Trends - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase derives objective-level due, mastery, risk, and trend signals from the evidence store; feeds bounded weights into the Phase 7 selector; enforces a daily subject cap through `day`; and presents itembank and Anki due signals side by side without merging ownership. It does not schedule individual Anki cards or create a second evidence store.

</domain>

<decisions>
## Implementation Decisions

### One evidence snapshot and provenance
- **D-01:** Every `day`, report, and selection-weight calculation for a render uses one immutable evidence snapshot marker. All displayed claims name the window, event count, and objective/subject filter behind them.
- **D-02:** Derived scheduling/trend state is disposable and reproducible from append-only evidence. Caches may accelerate reads but are never authoritative.
- **D-03:** Insufficient evidence is a first-class `unknown` state, not zero mastery, zero due, or a fabricated trend.

### Objective scheduling
- **D-04:** itembank schedules objectives, not cards. Each objective receives transparent signals for last successful evidence, recent accuracy, hint depth, pending review, and elapsed time; the planner/researcher chooses and documents the initial bounded formula.
- **D-05:** “Due today” is a labeled itembank recommendation with a reason and evidence basis. Anki due/new counts remain a separate labeled signal read in the same render snapshot; neither number is summed into the other.
- **D-06:** Objective states include due, at-risk, weak, stable, mastered, and unknown as derived labels over visible component signals. Thresholds live in settings with conservative defaults and schema bounds so later tuning does not require code changes.

### Daily cap and pacing
- **D-07:** `daily_cap` is enforced per subject using live evidence already recorded for the local day. Once reached, `day` blocks starting more ordinary work for that subject and explains the count.
- **D-08:** A deliberate override may coexist for exceptional use, but it must be explicit, time-limited to that launch/sitting, and recorded as an override event. There is no silent or persistent “ignore cap” toggle. This preserves user choice without making the cap cosmetic.
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

### Codex's Discretion
The initial formula, thresholds, and chart choices require research and a stronger planning/UI model. They may expose multiple user-selectable profiles if comparisons show no single universally best pacing model; all must remain inspectable, bounded, and reproducible.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/ROADMAP.md` § "Phase 10: Retention, Pacing & Trends" — five success criteria.
- `.planning/REQUIREMENTS.md` SCHED-01 through SCHED-04 and TREND-01 through TREND-05 — binding scheduling/trend behavior.
- `.planning/PROJECT.md` — objective-level ownership, Anki separation, and evidence-backed control-loop intent.
- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — evidence/index/retraction contracts.
- `.planning/phases/07-selection-engine/07-CONTEXT.md` — pure selector, trace, profiles, hard/soft recency, and exam neutrality.
- `.planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md` — hint-tier evidence semantics.
- `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md` — pending model review cannot affect mastery.
- `evidence.py` — objective history, subject filters, disposable index, live events, mark-state derivation.
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

### Established Patterns
- Derived indexes are disposable; append-only evidence is authoritative.
- Unknown external data is omitted/labeled, never guessed.
- Selector inputs are passed explicitly and traces explain decisions.

### Integration Points
- New pure trend/scheduling derivation module.
- `day` shared snapshot and cap guard.
- Phase 7 history/weights input and trace explanation.
- Longitudinal `/report` data endpoint plus CLI twin.
- Settings schema, provenance schema, and synthetic time-series fixtures.

</code_context>

<specifics>
## Specific Ideas

Keep both Anki and itembank signals visible because they answer different questions. Preserve multiple pacing profiles only if they can share one transparent component model; do not hide uncertainty behind a single “smart” score.

</specifics>

<deferred>
## Deferred Ideas

- Owning card intervals/ease or writing Anki schedules — out of scope for this milestone.
- Predictive ML mastery models — defer until evidence volume justifies them.
- Curriculum coverage auditing — Phase 11.

</deferred>

---

*Phase: 10-retention-pacing-trends*
*Context gathered: 2026-08-08*
