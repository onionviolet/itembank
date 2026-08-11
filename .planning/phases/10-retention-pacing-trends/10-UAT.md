---
status: complete-automated
phase: 10-retention-pacing-trends
source: [10-VERIFICATION.md, 10-VALIDATION.md]
started: 2026-08-11T00:00:00Z
updated: 2026-08-11
---

## Current Test

[testing complete — all automated criteria pass; the 10-06 Task 3 human UI
checkpoint (1280/768/375 px, keyboard/focus, exact copy, offline, DOM/API leak
inspection) is DEFERRED to the user]

## Tests

### 1. `day`'s cockpit shows what's due today per objective, computed from itembank's own evidence, alongside Anki's due/new counts as a separate, clearly labeled signal, both read from one shared per-render snapshot (ROADMAP SC 1 / SCHED-01)

expected: Today's due objective cards carry owner labels (`itembank` vs `Anki`),
raw counts, state, and a snapshot id identical to the adjacent evidence
disclosure and to the focused-start request; Anki counts are never summed with
itembank counts.

why_human: none — automated.

how_to_run: `python tests/retention_ui_roundtrip.py` (check 1 Today due card +
snapshot linkage + focused start; check 3 Anki separation) and `python tests/day_roundtrip.py`.

result: pass

### 2. A daily cap enforced through `day` blocks over-work in one sitting; Anki keeps owning card reviews, itembank writes no card schedule (ROADMAP SC 2 / SCHED-02, SCHED-03)

expected: per-subject live local-day cap blocks start and genuine submit with
the exact locked copy; one explicit sitting-scoped override is the only
exception and expires; Anki is read-only (deckNames/findCards only) and
zero/populated/unavailable states never alter the snapshot or cap.

why_human: none — automated.

how_to_run: `python tests/pacing_roundtrip.py` (7 checks) and `python tests/day_roundtrip.py`.

result: pass

### 3. An objective the learner keeps missing visibly raises its selection weight in the next session; one mastered drops out of rotation (ROADMAP SC 3 / TREND-01)

expected: weak/due objectives get bounded higher weight in practice/remediation
through the Phase 7 sole selector; mastered objectives leave ordinary rotation
while a non-mastered eligible objective exists, with an explicit all-mastered
fallback; weights are capped per snapshot and exam selection is byte-for-byte
evidence-neutral.

why_human: none — automated.

how_to_run: `python tests/selection_retention_roundtrip.py`.

result: pass

### 4. An objective answered correctly a month ago and untouched since is flagged at-risk in the longitudinal `/report` view, before it would actually be failed (ROADMAP SC 4 / TREND-04)

expected: proven success + 28 days of silence → `at-risk` and due, with a
reason naming the last proven success and the elapsed configured threshold;
27d23h is not at-risk; untouched no-success stays `unknown`.

why_human: none — automated.

how_to_run: `python tests/retention_roundtrip.py` (six states + risk_reason).

result: pass

### 5. The longitudinal report shows accuracy by objective over weeks, hint tier reached, and items pending manual marking, and every trend states the evidence it rests on (ROADMAP SC 5 / TREND-03, TREND-05)

expected: week report exposes raw accuracy counts, highest/average hint,
attempts, pending, last date; the semantic table/text is canonical; every
state/row/recommendation/weight/reason references one complete evidence claim
(snapshot_id, cutoff, zone, window, filters, live_event_count,
settings_version) shared across CLI JSON, CLI text, and browser.

why_human: none — automated.

how_to_run: `python tests/retention_roundtrip.py` (week series, JSON/text parity),
`python tests/retention_ui_roundtrip.py` (check 6 /report CLI-payload parity +
drilldown + weeks allowlist), `python tests/phase10_uat.py` (cross-surface tracer).

result: pass

### 6. Recommendations favor short, focused sessions and surface the learner's strategy, surprise, or sticking point as optional reflection evidence without streaks or points (ROADMAP SC 6)

expected: focused-session recommendation is bounded and evidence-anchored;
return rate is a stated-denominator ratio, never a streak, never rendered with
a target or as a loss state; no gamification.

why_human: automated structurally; the visual calm/no-gamification reading is
part of the deferred human UI gate.

how_to_run: `python tests/retention_roundtrip.py` (recommendation, return_rate).

result: pass (structural); visual confirmation deferred to the human gate

### 7. FSRS is the scheduler baseline, state derived by replaying the append-only evidence log, rebuilding identically (ROADMAP SC 7)

expected: scheduler state replays captured events through the FSRS default
strategy; rebuild from the log reproduces it exactly.

why_human: none — automated.

how_to_run: `python tests/retention_roundtrip.py` (FSRS replay).

result: pass

### 8. The scheduler sits behind one interface with FSRS as the default strategy (ROADMAP SC 8)

expected: one strategy interface; a later algorithm change is a registered
strategy plus a replay, not a migration.

why_human: none — automated (structural).

how_to_run: `python tests/retention_roundtrip.py` (scheduler strategy
interface, FSRS registered default).

result: pass

### 9. Progress is named in WaniKani-style stages with a terminal "retired" state; due ordering is jpdb-style utility-weighted (ROADMAP SC 9)

expected: stage names incl. terminal "Retired"; due ordering utility-weighted
(jpdb-style) and legible.

why_human: none — automated.

how_to_run: `python tests/retention_roundtrip.py` (stages, utility_order).

result: pass

### 10. Return rate is a stated-denominator ratio, never a streak (ROADMAP SC 10)

expected: occurred sittings over due sittings with the denominator always
stated; never a consecutive count; the report always renders the ratio even at
due=0 (null rate shows `unknown`).

why_human: none — automated.

how_to_run: `python tests/retention_roundtrip.py` (return_rate); `python tests/retention_ui_roundtrip.py` (check 6, due=0 rendering).

result: pass

### 11. Lesson-to-item transfer is deliberately deferred, recorded with its cost (ROADMAP SC 11)

expected: not computable from the log as it stands; recorded rather than
silently dropped; no half-built transfer feature.

why_human: none — deferred by decision (D-21), not a gap.

how_to_run: `python tests/lesson_retention_roundtrip.py` (completion queue is
the only lesson seam built).

result: pass (deferred decision honored)

### 12. A pending model suggestion never advances an interval and grants no mastery, though it does count as an attempt (ROADMAP SC 12)

expected: scheduler reads accepted marks only; model proposal/interaction
events never settle completion or mastery and never change recommendation or
weight; pending constructed responses count for pacing only.

why_human: none — automated.

how_to_run: `python tests/retention_roundtrip.py`, `python tests/selection_retention_roundtrip.py`
(model-event immunity), `python tests/pacing_roundtrip.py` (pending pacing-only).

result: pass

### 13. Human UI checkpoint at 1280/768/375 px (10-06 Task 3) — DEFERRED to user

expected: start `python itembank.py daemon fixtures --no-open --port 8730`
with the synthetic Phase 10 fixture; verify activity-first hierarchy, owner
labels never summed, all six state names + raw evidence + provenance readable
without color, overview→subject→objective drilldown with week windows, keyboard
order/focus trap/Escape, exact cap/override/Anki-unavailable/report-failure
copy, stale-snapshot refresh, explicit lesson completion, cancelled/accepted/
expired override, offline behavior, and DOM/API leak inspection.

why_human: a blocking human gate an agent cannot truthfully self-certify.

how_to_run: per `10-06-PLAN.md` Task 3; resume-signal is `approved` or a
concrete failure description.

result: deferred

## Summary

total: 13
passed: 12 (all automated; item 6 structural, visual half deferred)
issues: 0
pending: 0
skipped: 0
blocked: 0
deferred: 1 (10-06 Task 3 human UI checkpoint — see HANDOFF-PHASE10.md)

## Gaps

- The 10-06 Task 3 human UI gate (responsive/accessibility/copy/offline/DOM
  inspection at 1280/768/375) is deferred to the user; the automated structural
  half (exact locked copies, focus/label fixtures, public-boundary scan) is green.
- Pre-existing non-Phase-10 suite failures (`evidence_roundtrip.py`,
  `gate_roundtrip.py` — 06.2 merge; `packaging_roundtrip.py` — env) and the
  `phase_062_audit.py` cascade are documented with root causes in
  10-VERIFICATION.md; they are not Phase 10 UAT failures.
