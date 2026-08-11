---
phase: 10-retention-pacing-trends
plan: 10-01
subsystem: retention-derivation-layer
tags: [retention, pacing, trends, snapshot, fsrs]
key-files:
  created:
    - retention.py
    - tests/retention_roundtrip.py
  modified:
    - evidence.py
    - surfaces/evidence_cli.py
    - surfaces/cli.py
    - schemas/settings.schema.json
    - schemas/report.schema.json
key-decisions:
  - "Phase 10's whole contract is one immutable capture: every derived claim (state, trend, weight, scheduler row, recommendation, queue entry) is a pure function of one `evidence.capture_events` snapshot plus bounded settings (D-01/D-02)."
  - "Six deterministic states (unknown/weak/mastered/at-risk/due/stable) over visible component signals; every threshold and interval lives in the bounded `retention` settings group (D-06)."
  - "Scheduler state is derived by replaying captured events through one strategy interface with FSRS as the registered default; progress is WaniKani-style stages with a terminal 'retired' state; due ordering is jpdb-style utility-weighted (D-17/D-18/D-19/D-23)."
  - "The usage measure is return rate -- occurred sittings over due sittings with the denominator stated -- never a streak (D-20)."
requirements-completed: [SCHED-01, SCHED-04, TREND-05]
completed: 2026-08-15
---

# Plan 10-01 Summary — Retention Derivation Layer (Wave 0)

**Objective:** Build the pure retention, pacing and trends derivation layer: one
immutable snapshot contract, six objective states, week series, bounded weights,
the FSRS scheduler strategy, the `itembank trends` CLI, and the additive
`retention_report` contract.

## What Was Built

- `retention.py` — the pure derivation layer (no second store, reader, writer, or
  selector): `capture()` materializes one immutable snapshot (claim + captured
  events + single marks join); `objective_summaries` / `objective_state` /
  `risk_reason` implement the six-state grammar; `week_series` carries raw counts
  beside every rate with null uncertainty (D-03); `objective_weights` are bounded,
  normalized, and capped per snapshot (D-11/D-12); `recommendation` is a bounded
  focused-session recommendation with no gamification.
- Scheduler strategy interface with the FSRS default (published parameter set,
  replay-only, deterministic), WaniKani-style stage names incl. terminal
  "Retired", `utility_order` (jpdb-style), and `return_rate` (D-20).
- `evidence.capture_events()` — the single materialization point over the
  append-only log with the compensating-retraction filter applied exactly once.
- `itembank trends` CLI (`--json` / plain text) rendering the SAME payload (D-15)
  with the full evidence claim in `schemas/report.schema.json`'s additive
  `retention_report` variant; bounded `retention` settings group in
  `schemas/settings.schema.json`.
- `tests/retention_roundtrip.py` — Wave 0 fixed-clock harness (immutability,
  states, pending/mark/retraction semantics, week buckets, weights, FSRS replay +
  stages + utility order, return rate, CLI JSON/text parity), green.

## Verification

- `python tests/retention_roundtrip.py` — pass
- Full-suite note: `tests/packaging_roundtrip.py` was NOT run by 10-01; its
  packaged-artifact check surfaced a gap in 10-02 (retention.py missing from
  `build.py` STAGE_FILES), fixed there.

## Success Criteria

- One parser, one scorer, one evidence writer; retention is a pure projection. ✓
- Every derived claim names its snapshot provenance and is disposable. ✓
