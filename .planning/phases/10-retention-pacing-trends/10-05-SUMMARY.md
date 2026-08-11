---
phase: 10-retention-pacing-trends
plan: 10-05
subsystem: retention-ui
tags: [today, report, drilldown, cap-recovery, lesson-complete, ui]
key-files:
  created:
    - surfaces/retention_view.py
    - tests/retention_ui_roundtrip.py
  modified:
    - surfaces/day.py
    - surfaces/daemon.py
    - tests/day_roundtrip.py
    - tests/daemon_roundtrip.py
key-decisions:
  - "surfaces/retention_view.py is the shared SSR component seam (SnapshotStamp, SignalCard, ObjectiveState, EvidenceDrawer, TrendSeries/text/table, CapGate, PendingReviewBadge, override dialog): render-only, accepts already-derived dicts, performs no state/weight/cap arithmetic, uses Phase 4 presentation primitives and the exact 10-UI-SPEC copies."
  - "The Today panel derives ONE recommendation payload per render (day_recommendation: due objectives with state/reason/raw counts, pending total, per-subject cap decisions over every active subject) from the same capture as day_pacing; the browser renders it and performs no derivation (D-01, D-05, D-07)."
  - "Focused start carries the displayed snapshot CLAIM (the id alone is insufficient: snapshot ids hash the cutoff timestamp). The handler re-captures current evidence and re-derives the snapshot at the displayed cutoff -- the id matches exactly iff no evidence changed, so stale/forged claims are rejected with refresh guidance and NO session/event (T-10-19). A valid action derives every private authority server-side."
  - "Cap recovery renders the runtime-issued cap decision: exact block copy, Review evidence / Request one-sitting override, a native dialog with the exact title/body/buttons (44px, stacked at narrow width) whose confirmation posts only the displayed snapshot + stable objective + explicit action token to the 10-04 override path; rendering/cancel writes nothing (D-07/D-08)."
  - "POST /api/lesson-complete is the daemon twin of `itembank lesson --complete` (heading resolved through model.lesson_slug/parse_lesson/load, one lesson_complete event through the one writer, reconcile on duplicate, refused on unknown/multi-subject refs, viewing writes nothing), registered in API_ROUTES/ROUTES/ROUTE_CLI and SURFACE_PARITY as itembank_lesson_complete (Extensibility Rule 9(a))."
  - "GET /report without `session` is the retention overview/drilldown (allowlisted 1/2/4/8/12 weeks, subject/objective identifiers), rendering the SAME retention.retention_report payload `itembank trends` prints; the semantic table + text are canonical, the return-rate ratio always states its denominator, and snapshot failure serves the locked report-failure copy with no recommendation (D-13/D-15/D-19/D-20)."
requirements-completed: [SCHED-01, SCHED-02, SCHED-03, SCHED-04, TREND-02, TREND-03, TREND-04, TREND-05]
completed: 2026-08-11
---

# Plan 10-05 Summary — Today, Cap Recovery, and the Longitudinal Report UI

**Objective:** Render and wire the approved Phase 10 Today, recovery, and
longitudinal report surfaces from the deterministic contracts, with no
browser-side authority (D-01, D-03 through D-05, D-07, D-08, D-13 through
D-15).

## What Was Built

- `surfaces/retention_view.py` (new) — render-only SSR components:
  `snapshot_stamp` (with `data-snapshot`/`data-cutoff` provenance markers),
  `signal_card` (owner-labelled, never summed), `objective_state` (text +
  shape chip, never color-only), `pending_review_badge`, `evidence_drawer`
  (observed facts / configured rules / derived conclusion regions),
  `cap_gate` (exact block copy + recovery), `override_dialog` (exact
  title/body/buttons), `trend_text`/`trend_table` (canonical text + table),
  `objective_detail`. No arithmetic beyond formatting; all locked copies
  verbatim from 10-UI-SPEC.
- `surfaces/day.py` — the Today panel: `day_recommendation` (one capture:
  due objective cards, pending total, per-subject cap decisions over every
  active subject), `objective_card` (state chip, raw counts, Why disclosure,
  Start focused session), `today_section` (stamp + itembank/Anki signals +
  cards + pending badge + CapGate with recovery and override dialog +
  lesson-complete form when a scanned bank has lessons), boot carries the
  full claim for the focused-start request; JS adds focused start, dialog
  open/close/focus and lesson-complete posts with `role=status`/`role=alert`
  announcements. Sparse evidence renders the exact `Not enough evidence
  yet` copy and practice stays available; Anki closed renders the exact
  locked copy and never changes the recommendation/snapshot.
- `surfaces/daemon.py` — `POST /api/lesson-complete` (bank stem + ref;
  server-resolved heading/objectives/subject; one append; duplicate
  reconciles; unknown/multi-subject refs refused; viewing writes nothing),
  registered in API_ROUTES/ROUTES/ROUTE_CLI ("lesson")/SURFACE_PARITY
  ("itembank_lesson_complete"); `POST /api/start` gains displayed-snapshot
  validation (re-derive at the displayed cutoff; stale/forged -> 400 with
  refresh guidance, no session); `GET /report` without `session` renders
  the retention overview/drilldown from the same `retention.retention_report`
  payload `itembank trends` prints (allowlisted weeks, subject/objective
  drilldown, stated-denominator return rate, report-failure copy).
- `tests/retention_ui_roundtrip.py` (new, 6 checks) — Today due card with
  snapshot linkage + focused start; sparse/unknown copy + forged-claim
  rejection + ordinary practice; Anki closed locked copy with the
  recommendation unaffected; at-cap exact block copy + recovery + override
  dialog with no write on render; lesson-complete route (one event,
  reconcile, refusal, read-only view, Today affordance); /report CLI-payload
  parity (cutoff-pinned), subject/objective drilldown, weeks allowlist,
  public boundary. `tests/daemon_roundtrip.py`: route scope 6->7, forged
  snapshot-claim case, no-session /report is the 200 retention overview.
  `tests/day_roundtrip.py` unchanged behavior re-verified.

## Verification

- `python tests/retention_ui_roundtrip.py` — pass (6 checks)
- `python tests/day_roundtrip.py` — pass
- `python tests/daemon_roundtrip.py` — pass (61 checks)
- `python tests/lesson_retention_roundtrip.py` — pass
- `python tests/retention_roundtrip.py` — pass
- Full suite: every `tests/*_roundtrip.py` green except the documented
  Windows-only `packaging_roundtrip.py` onedir gate (unchanged).

## Post-Implementation Failures and Root Causes

1. **Snapshot staleness is cutoff-dependent.** `snapshot_id` hashes the
   cutoff timestamp, so comparing a displayed id to a fresh capture always
   mismatches. Fixed by re-deriving at the DISPLAYED cutoff over CURRENT
   events: the id matches exactly iff the evidence is unchanged, so stale
   and forged claims are both rejected, and the request carries the full
   public claim (the id alone cannot be re-derived).
2. **CapGate only covered recommended subjects.** The at-cap fixture had no
   due objective, so no cap section rendered. `day_recommendation` now
   computes cap decisions for every subject with activity today (D-07).
3. **Return rate vanished when no reviews were scheduled** (`due=0`). The
   report now always renders the ratio with its stated denominator, using
   `unknown` for a null rate (D-03/D-20).
4. **Parity test compared two captures at different cutoffs.** The CLI run
   is now pinned to the page's `data-cutoff` so both derive the identical
   snapshot id.
5. Minor: module-level `esc` for the new day helpers; template slot count
   after inserting the Today section; `check_api_route_scope` updated to
   the lesson CLI twin (`lesson`, not a new command name).

## Success Criteria

- Today and report implement the approved UI-SPEC without browser formulas
  or a second data/selection authority. ✓
- Every claim is inspectable and snapshot-consistent; stale/forged actions
  fail closed. ✓
- itembank versus Anki ownership, uncertainty, cap recovery, pending manual
  status, and offline behavior are explicit. ✓
- Existing session report and Phase 4 day/presentation contracts remain
  intact (day/daemon suites re-verified). ✓
