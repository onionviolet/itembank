---
phase: 10-retention-pacing-trends
verified: 2026-08-11
status: passed-with-caveats
score: 9/9 requirement rows verified, 5/6 wave gates verified, phase gate automated half verified
behavior_unverified: 1 (10-06 Task 3 human UI checkpoint, deferred)
pre-existing_suite_failures: evidence_roundtrip.py, gate_roundtrip.py (06.2 merge), packaging_roundtrip.py (env)
---

# Phase 10: Retention, Pacing & Trends — Verification Report (close-out)

**Phase Goal (ROADMAP):** The tool tells the learner what's due today, stops a
course being binged in one sitting, and raises or lowers what gets selected
based on real performance history — with itembank's and Anki's notions of "due"
shown as two labeled signals, never silently merged.
**Verified:** 2026-08-11 (close-out re-run, live, on branch `gsd/phase-10-close`,
worktree `.phase10-wt` at main HEAD `2b5678c`)
**Status:** phase-10 automated truths **passed**; the repo-wide full suite is
**not green on main HEAD** due to two pre-existing, non-phase-10 failures
(root-caused below) plus one documented environment gap.

The phase code was already merged into main (`8e76ea0 merge branch 'phase10'
into main`); this run re-verifies every Phase 10 claim live at main HEAD.

## Commands run (this close-out, all live)

| Command | Result |
|---|---|
| `python tests/retention_roundtrip.py` | PASS |
| `python tests/lesson_retention_roundtrip.py` | PASS |
| `python tests/selection_retention_roundtrip.py` | PASS |
| `python tests/pacing_roundtrip.py` | PASS (7 checks) |
| `python tests/retention_ui_roundtrip.py` | PASS (6 checks) |
| `python tests/phase10_uat.py` | PASS (3 checks) |
| `python tests/evidence_roundtrip.py` | **FAIL — pre-existing (06.2 merge)** |
| `python tests/gate_roundtrip.py` | **FAIL — pre-existing (06.2 merge)** |
| `python tests/protocol_roundtrip.py` | PASS (83 lint codes, contracts validated) |
| `python tests/config_roundtrip.py` | PASS |
| `python tests/lesson_roundtrip.py` | PASS |
| `python tests/selection_roundtrip.py` | PASS |
| `python tests/day_roundtrip.py` | PASS |
| `python tests/daemon_roundtrip.py` | PASS (69 checks) |
| full suite `tests/*.py` (45 files, CI-equivalent loop) | 41 PASS / 4 FAIL (see below) |
| `python itembank.py lint fixtures/sample_bank.md` | 0 errors, 6 warnings (subject-prefix warnings, expected) |
| `python schema_validate.py` (CI-equivalent live flow, session/item/response/report/lint) | PASS |
| `python schema_validate.py schemas/response.schema.json --jsonl fixtures/lesson_retention_events.jsonl` | 2 instances, 0 errors |
| `python itembank.py trends --base . --weeks 4 --json` | live retention_report payload with full claim (snapshot_id, cutoff, zone, window, filters, live_event_count, settings_version) |

## Wave and dependency gates (10-VALIDATION.md source of truth)

| Gate | Required fact | Command | Result |
|---|---|---|---|
| Wave 0 | Fixed synthetic UTC/local-day evidence covers retraction, pending/manual settlement, sparse state, byte-stable provenance | `python tests/retention_roundtrip.py` | ✅ VERIFIED |
| Lesson seam | Phase 3 heading/objective resolution exists; explicit completion versioned; views read-only | `python tests/lesson_retention_roundtrip.py` | ✅ VERIFIED |
| Selector seam | Phase 7 07-06 sole-selector contract exists, fixed-seed compatible | `python tests/selection_retention_roundtrip.py` | ✅ VERIFIED |
| Pacing seam | Start and submit enforce live per-subject cap; override sitting-bound | `python tests/pacing_roundtrip.py` | ✅ VERIFIED |
| UI foundation | Phase 4 presentation/day contracts; Today/report no browser-side derivation | `python tests/retention_ui_roundtrip.py` | ✅ VERIFIED |
| Phase gate | One snapshot crosses Today/start/selector/report; all tests + manual widths/accessibility | `python tests/phase10_uat.py` + full suite + checkpoint | ✅ automated cross-surface VERIFIED; ⏳ full suite NOT green (2 pre-existing + 1 env, below); ⏳ human checkpoint deferred |

## Requirement-to-test matrix (9/9 rows VERIFIED)

| Requirement | Observable proof | Status | Evidence |
|---|---|---|---|
| SCHED-01 | Due objectives and Anki due/new separate from one render; all claims share a snapshot | ✅ VERIFIED | retention_roundtrip (snapshot immutability, JSON/text parity); retention_ui_roundtrip check 1 (Today due card + snapshot linkage + focused start) |
| SCHED-02 | Per-subject live local-day cap blocks start/submit; one explicit override expires with the sitting | ✅ VERIFIED | pacing_roundtrip (7 checks incl. at-cap block, replay dedupe, race, override append/expiry, forgery) |
| SCHED-03 | Anki read-only, separately labeled; zero/populated/unavailable never changes objective state/cap/weight | ✅ VERIFIED | day_roundtrip (owner-labelled Anki, read-only Anki, local-day recut); retention_ui_roundtrip check 3 (locked copy, recommendation unaffected) |
| SCHED-04 | Explicit Phase 3 heading completion appends one event, enters configured review queue; view/scroll does nothing | ✅ VERIFIED | lesson_retention_roundtrip; retention_ui_roundtrip check 5 (lesson-complete route) |
| TREND-01 | Weak/due objective gets bounded higher weight; mastered leaves ordinary rotation with bounded fallback | ✅ VERIFIED | selection_retention_roundtrip (weighted ordering, mastered fallback, bounded step) |
| TREND-02 | Subject load comes from captured live evidence, re-cuts with named reason after event/retraction | ✅ VERIFIED | day_roundtrip (snapshot pacing, recut after live event, old payload stable) |
| TREND-03 | Week report exposes raw accuracy counts, highest/average hint, attempts, pending, last date across CLI/browser parity | ✅ VERIFIED | retention_roundtrip (week series); retention_ui_roundtrip check 6 (/report CLI payload parity, drilldown, weeks allowlist) |
| TREND-04 | Proven success + 28 days of silence becomes at-risk with exact reason; untouched no-success stays unknown | ✅ VERIFIED | retention_roundtrip (six states, risk_reason); phase10_uat (cross-surface trace) |
| TREND-05 | Every state, row, recommendation, weight and chosen reason references one complete evidence claim | ✅ VERIFIED | phase10_uat check 1 (cross-surface tracer: one claim across Today/start/selector/report, fail-closed stale, consistent refresh) |

## Deterministic fixture matrix (18/18 VERIFIED)

Covered by `tests/retention_roundtrip.py`, `tests/lesson_retention_roundtrip.py`,
`fixtures/lesson_retention_events.jsonl`, `tests/pacing_roundtrip.py`,
`tests/selection_retention_roundtrip.py`, `tests/retention_ui_roundtrip.py` and
`tests/phase10_uat.py`, per the 10-VALIDATION.md matrix: no-evidence `unknown`;
three settled one correct → `weak`+`due` raw 1/3; mastered out of ordinary
rotation with bounded fallback; 27d23h not at-risk; 28d at-risk with named
reason; pending-only constructed responses (pacing-only, mastery unchanged);
accepted human mark settles; Phase 8 proposal/model event never settles
mastery; compensating retraction disappears from state/series/cap/queue while
raw audit bytes remain; two-zone local-day boundary; completion before/at
review boundary; Anki zero/populated/unavailable byte-identical snapshot;
same-capture-twice byte-identical; append-after-capture new marker; prior
selection max-step; exam with/without retention context byte-identical. All
green in this close-out run.

## Evidence claim contract

The claim object `{snapshot_id, cutoff, local_day_zone, window, filters,
live_event_count, settings_version}` is asserted equal across Today card /
EvidenceDrawer / cap decision / focused-start request / session authorization /
selection event+trace / CLI JSON / CLI text / report overview / drilldowns by
`tests/phase10_uat.py` (cross-surface tracer) and `tests/retention_ui_roundtrip.py`.
Appending evidence between render and action fails stale (400, no session, no
event) — proven by phase10_uat check 1.

## Required artifacts (all exist, all exercised live)

| Artifact | Status |
|---|---|
| `retention.py` — pure derivation (capture, six states, week series, bounded weights, recommendation, lesson_queue, cap_decision, subject_pacing, scheduler strategy + FSRS default, WaniKani stages/retired, jpdb utility order, return rate) | ✅ EXISTS, tests green |
| `evidence.capture_events()` — single materialization point, retraction filter applied once | ✅ EXISTS, exercised |
| `itembank trends` CLI (`--json`/plain, weeks 1/2/4/8/12, subject/objective/cutoff/zone) | ✅ EXISTS, live-run |
| `schemas/report.schema.json` `retention_report` variant + `schemas/settings.schema.json` `retention` group | ✅ EXISTS, schema-validated |
| `evidence.lesson_complete_event` + `itembank lesson --complete` + `retention.lesson_queue` | ✅ EXISTS, tests green |
| `selection.select(..., retention_context=)` — sole-chooser seam, allowlist-validated | ✅ EXISTS, tests green |
| `evidence.cap_override_event` + `itembank override` + `POST /api/override` + daemon `send_error` encoding fix | ✅ EXISTS, tests green |
| `surfaces/retention_view.py` (render-only SSR components) + Today panel in `surfaces/day.py` | ✅ EXISTS, tests green |
| `POST /api/lesson-complete` + `GET /report` (no-session retention overview) | ✅ EXISTS, tests green |
| `fixtures/lesson_retention_events.jsonl` | ✅ EXISTS, schema-valid (2 instances, 0 errors) |
| Six Phase 10 test files (`retention`, `lesson_retention`, `selection_retention`, `pacing`, `retention_ui`, `phase10_uat`) | ✅ EXISTS, all green |

## Anti-patterns

| Anti-pattern | Status |
|---|---|
| Second parser / scorer / runner / evidence writer / selector / report calculator | ✅ ABSENT — `retention.py` is a pure projection; selection stays Phase 7's `selection.select`; asserted structurally by selection_retention_roundtrip (sole-chooser boundary) and phase10_uat (no new authority) |
| Browser-side derivation | ✅ ABSENT — retention_ui_roundtrip asserts server-derived payloads, render-only components |
| Private-field leak in public serialization | ✅ ABSENT — phase10_uat check 2 scans Today/report/drilldown/start/trace/item against a private-field deny list |
| Unbounded settings / non-finite weights / forged fields | ✅ ABSENT — config_roundtrip bounds; selection_retention_roundtrip + pacing_roundtrip forgery rejection |

## Pre-existing suite failures (NOT phase-10 regressions — root-caused)

The full suite is 41/45 green. Four FAILs, three independent causes:

1. **`tests/evidence_roundtrip.py` — FAIL: "index was not rebuilt at version 3
   after the stale check".** Pre-existing on main since the **06.2 merge
   `d35bd15`** (merged after Phase 10). `feat(06.2-01)` (`376dae4`) bumped
   `evidence.py` `INDEX_VERSION` 2→3 (its index projection gained a `context`
   column) and updated the test to expect "3"; the merge resolution kept
   main's `INDEX_VERSION = 2` and the v2 index schema while retaining the
   test's "3" expectation. Verified: `8e76ea0:evidence.py` (phase-10 merge
   point) had `INDEX_VERSION = 2` with the test expecting "2" — consistent and
   green at the time Phase 10 merged. Phase 10 contributed no change to
   `INDEX_VERSION` or the index schema.
2. **`tests/gate_roundtrip.py` — FAIL: "rows must differ only by context in log
   order, got [None, None]".** Same root cause, other half: 06.2's index
   projection `context` column (and `_row_from_index_tuple`'s `"context": r[11]`)
   was dropped by the same merge resolution, so `objective_history` rows lack
   the context field GATE-03's "Phase 10 needs no branch" proof asserts.
3. **`tests/packaging_roundtrip.py` — FAIL: `dist/itembank-sidecar-onedir`
   missing.** Documented environment gap since 10-02: the PyInstaller onedir
   freeze is produced by `powershell -File scripts/build_shell.ps1`, which
   cannot run in this Linux bash environment. `tests/packaging_shell_roundtrip.py`
   degrades gracefully (skip: `itembank-shell.exe` not built).
4. **`tests/phase_062_audit.py` — FAIL: "full suite not green".** Cascade: it
   shells out to the full suite and asserts green; it fails only because of
   failures 1–3 above. Its own requirement audit rows pass (6/6 IDs covered,
   every named test exists, skip sentence recorded, published schemas emit).

**Suggested integrator fix (out of scope for this close-out):** restore 06.2's
index-projection half in `evidence.py` — add `context TEXT` to
`_create_index_schema`, write `context` in `_insert_response_row`, select it in
`_objective_history_indexed`, map `"context": r[11]` in
`_row_from_index_tuple`, and bump `INDEX_VERSION` 2→3. Both failing tests then
pass and main CI returns to green. This is Phase 6.2's code, not Phase 10's;
the orchestrator should apply it centrally so concurrent phase branches do not
each carry the same fix.

**Stale reference:** 10-VALIDATION.md's "Required upstream regression gate"
lists `tests/teaching_roundtrip.py`, which no longer exists; the teaching /
LESSON-SRC contract is covered by `tests/lesson_roundtrip.py` (slug, parse,
fingerprint, LESSON-SRC, degraded state, coupling guards — green). Noted for
the matrix to be corrected at reconciliation.

## Human UI gate (10-06 Task 3 — DEFERRED, blocking, human-pending)

Plan 10-06 Task 3 (`checkpoint:human-verify`, gate=blocking) requires a human
at 1280/768/375 px to verify visual hierarchy, owner labels, uncertainty/
evidence readability, keyboard/focus, exact cap/override/Anki copy,
stale-refresh, explicit lesson completion, offline behavior, and DOM/API leak
inspection, then type `approved` or a concrete failure. **Not executed — it is
a human gate an agent cannot truthfully self-certify.** The automated half
(10-UI-SPEC structural fixtures, exact locked copies, public-boundary scan)
is green; the human half remains and is recorded in 10-UAT.md and
HANDOFF-PHASE10.md.

## Sign-Off

- [x] 9/9 requirement rows (SCHED-01..04, TREND-01..05) verified by live tests
- [x] 18/18 deterministic fixtures covered and green
- [x] 5/6 wave gates verified; phase-gate automated half verified
- [x] All six Phase 10 focused test files green in this close-out run
- [x] schema_validate.py live flow (session/item/response/report/lint) green;
      Phase 10 fixture schema-valid
- [x] `itembank lint fixtures/sample_bank.md` — 0 errors
- [ ] Full suite green — **NOT met on main HEAD**: 2 pre-existing 06.2-merge
      failures + 1 documented env gap + 1 cascade (root causes above)
- [ ] 10-06 Task 3 human UI checkpoint — **deferred, blocking, human-pending**
- [x] Verified by: autonomous close-out run on branch `gsd/phase-10-close`
      (worktree `.phase10-wt`)

**Status: PASSED (Phase 10 automated truths) — with 2 pre-existing non-Phase-10
suite failures, 1 environment gap, and 1 deferred human gate documented.**
