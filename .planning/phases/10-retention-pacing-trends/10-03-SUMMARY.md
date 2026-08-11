---
phase: 10-retention-pacing-trends
plan: 10-03
subsystem: selector-retention-context
tags: [selection, retention, weights, snapshot, provenance]
key-files:
  created:
    - tests/selection_retention_roundtrip.py
  modified:
    - selection.py
    - surfaces/session.py
    - evidence.py
    - schemas/session.schema.json
    - schemas/response.schema.json
    - tests/agent_roundtrip.py
    - tests/daemon_roundtrip.py
    - tests/evidence_roundtrip.py
    - tests/protocol_roundtrip.py
key-decisions:
  - "Phase 7 remains the SOLE item chooser: `selection.select` gained one additive keyword-only `retention_context` (snapshot claim + bounded normalized objective-weight map); `retention.py` returns no item indices, chooses nothing, and writes no evidence."
  - "The context is allowlist-validated before anything else (T-10-10/T-10-13): exactly two keys, a snapshot claim with a non-empty id, and weight entries carrying only weight (positive finite), components (finite numbers), and a snapshot_id matching the context -- forged maps, client paths, answer keys, hidden tiers, and model payloads are refused with named errors."
  - "Practice/remediation compose the weight AFTER Phase 7's eligibility/cooldown/recency terms (ordering step only): non-mastered objectives first by descending weight; mastered objectives leave ordinary rotation while a non-mastered eligible objective exists but remain reachable through the explicit all-mastered fallback (D-11). Exam is byte-for-byte evidence-neutral and diagnostic keeps Phase 7's coverage policy (D-12)."
  - "The prior live selection event's own recorded weights supply the previous map for the per-snapshot `max_weight_step` cap -- no weight file, cache, or second store (D-02/D-12)."
  - "Session, selection evidence event, returned trace, and every chosen reason name one identical snapshot id; the session stores only the authorization (snapshot id + weights-only map) while the full component trace lives in the selection event (D-01)."
  - "Schemas extended additively with no version bump: session.schema.json gains a closed optional `retention`; response.schema.json gains a closed `selection_event` branch (selection leaves the permissive catch-all so forged selection events fail validation) -- pre-Phase-10 sessions and selection events remain valid."
requirements-completed: [SCHED-01, TREND-01, TREND-04, TREND-05]
completed: 2026-08-15
---

# Plan 10-03 Summary — Selector Retention Context (Weights Into the Sole Chooser)

**Objective:** Feed evidence-derived objective weights into Phase 7's sole
selector with one sitting-wide snapshot and a complete component trace
(D-01, D-04, D-10 through D-12), without a second picker, cache, or writer.

## What Was Built

- `selection.select(..., *, retention_context=None)` — the one additive seam:
  `_validate_retention_context` (allowlisted, positive-finite weights,
  matching snapshot ids, named refusals), `order_weighted` (non-mastered
  first by descending weight, mastered deferred to an explicit all-mastered
  fallback, recency rank breaking ties), per-chosen `objective_weight` +
  `components` + `retention_snapshot_id` and a reason clause naming the
  snapshot, and `trace["retention"]` with the full component map. Exam and
  diagnostic outputs are byte-identical with or without the context (D-12).
- `surfaces/session._retention_context(log, cfg)` — one capture, one
  snapshot, the bounded normalized weight map, with the previous map read
  from the most recent live selection event (D-02). `do_start`/`do_select`
  pass the exact context object, the session stores
  `retention: {snapshot_id, objective_weights: {obj: {weight}}}` (weights
  only, per the session-is-not-authority boundary), and the selection event
  records the full claim (snapshot id, weight map with named components,
  component trace) via the extended `evidence.selection_event(..., retention=)`.
- `schemas/session.schema.json` — additive optional closed `retention`.
- `schemas/response.schema.json` — closed `selection_event` oneOf branch
  (spec allowlist, closed retention with weight/components/snapshot_id and
  optional trace); `selection` removed from the permissive catch-all so
  forged selection events fail validation. Old no-retention selection events
  still validate.
- `tests/selection_retention_roundtrip.py` — fixed-seed harness (9 checks)
  and `tests/protocol_roundtrip.py` `test_selection_retention_provenance`.

## Verification

- `python tests/selection_retention_roundtrip.py` — pass
- `python tests/selection_roundtrip.py` — pass (Phase 7 fixed-seed contracts intact)
- `python tests/protocol_roundtrip.py` — pass (real session + event validate,
  forged variants rejected, old documents valid)
- Full suite: every `tests/*_roundtrip.py` green except the documented
  Windows-only `packaging_roundtrip.py` onedir gate (unchanged from 10-02).

## Post-Implementation Failure and Root Cause

`tests/evidence_roundtrip.py` failed after the 10-03 edit
(`test_serve_writes_events`: the exam block was moved BEFORE the drill
sitting so the exam sitting would be empty-evidence). The failure was
reported as "exam-mode answer must defer feedback: action 'hold'".

An empirical A/B probe (not theory) showed the ordering code was NOT the
cause: `select` with `retention_context` carrying an EMPTY `objective_weights`
map is byte-identical to `retention_context=None` on both the 10-02 tree and
this one — `itembank start sample_bank.md --count 6 --seed 0` serves
q5 first in BOTH trees when the evidence log is empty. The two candidate
fixes (skip the weighted path when the map is empty; make `order_weighted`
byte-identical to `order_shuffled` for equal weights) are both already true
and were rejected as unnecessary — and skipping the weighted path on empty
weights would have contradicted D-01's "every chosen reason names one
identical snapshot id".

The real chain of causes, each verified:

1. `session.do_action` always answers the session's CURRENT cursor item; the
   posted item id only selects the `explain` payload.
2. With an empty log, the seed-0 practice composition serves q5 (a `dnd`
   item) first — pre-existing Phase 7 behavior, not introduced by 10-03.
3. The moved exam block hard-coded `by_id["q1"]` (an `mc` answer). Scored
   against the current `dnd` item, that string has an EMPTY idempotency
   canon (`canonical_response` returns "" for a non-dict dnd answer), so
   `teaching_transition` classifies it `not genuine` and returns `hold`
   (runtime.py) instead of the exam policy's `defer_feedback`.
4. Even with a valid answer, exam-first also poisons the DRILL sitting:
   after the exam response the drill composition excludes q5 and serves q6
   (a `short` item) first, which never auto-advances — breaking the drill
   block's "must advance with explanation" assertion.

Fix (test-only, `tests/evidence_roundtrip.py`):

- Restored the original block order: the drill sitting runs FIRST against
  the empty log (its advance/cursor/time assertions need the stable
  q5 → q3 → q2 flow), the exam sitting runs AFTER it.
- The exam block is now order-independent, matching its own stated purpose
  ("exam feedback policy, not item order, is what this block is proving"):
  it learns the served CURRENT item with the same `start` probe the drill
  block uses and answers it correctly. A genuinely recorded exam answer —
  scored or pending — must return `defer_feedback` with no `score`/`explain`
  leak. With 10-03 weights non-empty, the exam-after-drill selection
  legitimately serves a different objective than before; the block no longer
  assumes which one.
- The EVID-08 `by_mode` assertion queries the whole bank log
  (`evidence --bank <stem> --base <tmp>`) instead of the drill current's
  objective, so "two sittings' scores stay in separate drill/exam buckets"
  holds whichever objectives the weighted selection served. (Same-objective
  drill/exam separation is still proven by `test_mode_recorded`.)

No selector code changed: the empty-weights weighted path already reproduces
`order_shuffled` byte-for-byte, so D-03's "no evidence ⇒ no invented
influence" holds structurally without a special case.

Second fallout (same class as the `tests/agent_roundtrip.py` fix): the full
suite surfaced `tests/daemon_roundtrip.py`'s `check_serve_attempt_refresh`,
which served the REPO fixture directly, so its evidence landed in
`fixtures/_evidence` and the next run's retention-weighted selection served
the `short` item first (auto answer scored `None` instead of `True`). Fixed
the same way as agent_roundtrip: serve a temp COPY of the bank so the log
lands in `workdir/_evidence`; `fixtures/_evidence` stays absent across
repeated runs. `tests/daemon_roundtrip.py` was added to this plan's commit
because it is the identical hermeticity fix the plan already applied to
`tests/agent_roundtrip.py`, and without it the suite is green only until the
first daemon run pollutes the shared fixture.

## Success Criteria

- Trend evidence changes the next eligible ordinary session without bypassing
  Phase 7. ✓
- Every weight and choice is bounded, component-explainable, snapshot-labeled,
  and model-independent. ✓
- Exam selection remains evidence-neutral and mastered material is out of
  ordinary rotation without becoming unreachable. ✓
