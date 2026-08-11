---
phase: 10-retention-pacing-trends
plan: 10-06
subsystem: phase-uat
tags: [uat, cross-surface, security, offline, volume]
key-files:
  created:
    - tests/phase10_uat.py
  modified: []
key-decisions:
  - "tests/phase10_uat.py is the one-command Phase 10 cross-surface and security gate: it drives the REAL CLI and daemon over one synthetic evidence set and proves a single evidence state flows through Today -> evidence disclosure -> focused start -> Phase 7 selection event -> CLI/browser report, that appended evidence forces an explicit fail-closed refresh (stale start -> 400, no session, no event, no mixed snapshots), and that no public serialization leaks private fields (T-10-24/T-10-25)."
  - "Snapshot ids hash the cutoff timestamp, so a later capture mints a new marker by design: the tracer asserts id equality where the system guarantees it (card/disclosure/boot; CLI report at a pinned cutoff BEFORE the start appends its selection event) and evidence-state equality elsewhere (the session binding counts match the displayed claim); the staleness append proves the refresh boundary. The session/selection derive their own fresh snapshot -- the selector's authority -- which is the documented boundary."
  - "The requirement-to-test matrix in 10-VALIDATION.md was audited against the existing suites: every row (six states, at-risk 28-day silence, pending/manual mark settlement, model-proposal immunity, retraction, week series, bounded weights, cap/override, Anki states, lesson queue, forged-field/ASVS1 negatives, window bounds) is already covered by retention/lesson/selection/pacing/day/daemon/retention_ui round trips; the genuinely-new cases (cross-surface claim, fail-closed stale, public-boundary scan, 12k+ volume log, sparse log) are added in tests/phase10_uat.py."
  - "The 10-06 Task 3 human-verify checkpoint (1280/768/375, keyboard/focus, exact copy, offline, DOM leak inspection) is a blocking human gate and is DEFERRED per the run instructions: the branch is left ready with the checkpoint recorded in this summary; it must be executed by a human before downstream auditing treats the browser behavior as approved."
requirements-completed: [SCHED-01, SCHED-02, SCHED-03, SCHED-04, TREND-01, TREND-02, TREND-03, TREND-04, TREND-05]
completed: 2026-08-11
---

# Plan 10-06 Summary — Cross-Surface UAT and Phase Gate

**Objective:** Close Phase 10 with cross-surface automated and human
verification of evidence consistency, pacing safety, explainability,
accessibility, and offline/public boundaries.

## What Was Built

- `tests/phase10_uat.py` (new, 3 checks):
  - **Cross-surface tracer** — one synthetic weak/due objective appears on
    Today (card + disclosure + boot share claim A), the CLI report derived
    at the displayed cutoff reproduces the identical snapshot id and counts
    (checked before the start appends its selection event), the focused
    start carries claim A and is accepted with a server-derived binding
    matching the displayed evidence, Phase 7 chose the objective and its
    trace names the session snapshot; appending one response makes the old
    claim fail stale (400, no session file, no event), and the refreshed
    Today mints a wholly new consistent claim while the old rendered
    payload stays unchanged.
  - **Public-boundary scan** — Today HTML, report HTML, subject drilldown,
    start JSON, selection trace, and the public item are scanned against an
    explicit private-field deny list (answer keys, rubrics, credentials,
    provider/model payloads, hidden tiers) plus path leaks; the documented
    CLI/API diagnostic fields (`session_file`, trace evidence log) and the
    day page's own "Plan read from <path>" note are redacted as documented
    Phase 2/4 loopback content.
  - **Volume and sparse logs** — a 12,000+ response plus 200 pending-event
    log derives in one bounded pass with exact counts; an empty log derives
    the honest unknown payload (T-10-26).
- Matrix audit: every row of the 10-VALIDATION.md requirement-to-test and
  deterministic-fixture matrices maps to an existing passing suite
  (retention, lesson_retention, selection_retention, pacing, day,
  daemon, retention_ui); no new parser/scorer/runner/evidence writer/
  selector/report calculator was introduced.

## Verification

- `python tests/phase10_uat.py` — pass (3 checks)
- `python tests/retention_roundtrip.py`, `python tests/retention_ui_roundtrip.py`,
  `python tests/pacing_roundtrip.py`, `python tests/lesson_retention_roundtrip.py`,
  `python tests/day_roundtrip.py`, `python tests/daemon_roundtrip.py` — pass
- Repository-wide gate (all `tests/*.py`, bash equivalent of the plan's
  PowerShell loop): every test green except the documented Windows-only
  `packaging_roundtrip.py` onedir gate (cannot run in this environment;
  unchanged from 10-02).

## Deferred: Task 3 Human-Verify Checkpoint (blocking, NOT executed)

The plan's Task 3 (`checkpoint:human-verify`, gate=blocking) requires a
human at 1280/768/375 pixels to verify visual hierarchy, owner labels,
uncertainty/evidence readability, keyboard/focus, exact cap/override/Anki
copy, stale-refresh behavior, explicit lesson completion, offline behavior,
and DOM/API leak inspection, then type `approved` or a concrete failure.
**This checkpoint is deferred and was NOT executed in this run** — it is a
human gate the agent cannot truthfully self-certify. The automated matrix
above covers the structural half; the human half remains, and the
`resume-signal` is the approval phrase or a specific failure description.

## Success Criteria

- Every Phase 10 requirement has automated evidence; the browser half has
  the automated structural fixture and awaits the deferred human gate. ✓/⏳
- No duplicate parser, scorer, runner, evidence store/writer, selector, or
  browser derivation was introduced. ✓
- Snapshot consistency, uncertainty, cap safety, Anki separation, offline
  behavior, and security boundaries hold end to end. ✓ (automated)
