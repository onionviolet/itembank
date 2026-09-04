# Phase 10 Handoff — Retention, Pacing & Trends (CLOSE-OUT)

**Branch:** `gsd/phase-10-close`
**Worktree:** `C:\Users\wayba\Downloads\CTF\itembank\.phase10-wt`
**Status:** CLOSED-OUT — 6/6 plans executed and merged (`8e76ea0 merge branch
'phase10' into main`); close-out verification re-run live at main HEAD
`2b5678c`; 10-VERIFICATION.md + 10-UAT.md written; ROADMAP checkbox left for
the orchestrator (per directive, not touched here).
**Date:** 2026-08-11

## What shipped

Evidence-driven retention, pacing and trends: the tool tells the learner what's
due today, stops a course being binged in one sitting, and raises or lowers
what gets selected from real performance history — with itembank's and Anki's
notions of "due" shown as two labeled signals, never silently merged.

| Plan | Deliverable | Commit (on phase10, merged to main) |
|------|-------------|-------------------------------------|
| 10-01 | `retention.py` pure derivation layer — one immutable snapshot, six states, week series, bounded weights, FSRS scheduler strategy + WaniKani stages/retired + jpdb utility order + return rate; `evidence.capture_events`; `itembank trends` CLI; `retention_report` + `retention` settings schemas; `tests/retention_roundtrip.py` | `9996c3e` |
| 10-02 | Explicit versioned lesson-completion seam: `lesson_complete` event, `retention.lesson_queue` projection, `itembank lesson --complete`, `fixtures/lesson_retention_events.jsonl`, `schema_validate` `uniqueItems`, `build.py` STAGE_FILES += retention.py; `tests/lesson_retention_roundtrip.py` | `bc00b2e` |
| 10-03 | Retention weights into the Phase 7 sole chooser: additive `retention_context` on `selection.select`, snapshot provenance in session + selection event, bounded max step, exam neutrality; `tests/selection_retention_roundtrip.py` | `66322ff` |
| 10-04 | Evidence-derived per-subject local-day cap on start+submit, one-sitting audited override, `POST /api/override` + `itembank override`, honest read-only Anki separation in `day`; `tests/pacing_roundtrip.py` | `6d99b8d` |
| 10-05 | Today panel, cap recovery + override dialog, lesson-complete route, longitudinal `/report` overview/drilldown via `surfaces/retention_view.py`; `tests/retention_ui_roundtrip.py` | `de78860` |
| 10-06 | Cross-surface UAT: one evidence claim across Today/start/selector/report, fail-closed stale refresh, public-boundary scan, 12k+ volume + sparse logs; `tests/phase10_uat.py` | `bf034c0` |

**Key files:** `retention.py`, `surfaces/retention_view.py`, `surfaces/day.py`,
`surfaces/session.py`, `surfaces/daemon.py`, `surfaces/cli.py`, `selection.py`,
`evidence.py`, `schemas/session.schema.json`, `schemas/response.schema.json`,
`schemas/report.schema.json`, `schemas/settings.schema.json`,
`fixtures/lesson_retention_events.jsonl`, and the six `tests/*_roundtrip.py` /
`tests/phase10_uat.py` files.

## Verification result (close-out re-run, live)

- **6/6 Phase 10 focused gates PASS:** `tests/retention_roundtrip.py`,
  `tests/lesson_retention_roundtrip.py`, `tests/selection_retention_roundtrip.py`,
  `tests/pacing_roundtrip.py` (7 checks), `tests/retention_ui_roundtrip.py`
  (6 checks), `tests/phase10_uat.py` (3 checks).
- **9/9 requirement rows** (SCHED-01..04, TREND-01..05) verified; **18/18
  deterministic fixtures** covered; **evidence-claim contract** proven across
  Today/cap/start/session/selection/report; **schema_validate.py live flow**
  green (session/item/response/report/lint) + Phase 10 fixture validates
  (2 instances, 0 errors); **`itembank lint fixtures/sample_bank.md`** 0 errors.
- Upstream regression gate (10-VALIDATION.md): `protocol`, `config`, `lesson`,
  `selection`, `day`, `daemon` (69 checks) all PASS; `evidence_roundtrip.py`
  FAILS — **pre-existing** (see below).
- Full suite (45 files): **41 PASS / 4 FAIL**, three independent causes:

  1. **`tests/evidence_roundtrip.py`** — FAIL "index was not rebuilt at version
     3". Pre-existing on main since the **06.2 merge `d35bd15`**: `feat(06.2-01)`
     (`376dae4`) bumped `INDEX_VERSION` 2→3 and the test to expect "3"; the
     merge kept main's `INDEX_VERSION = 2` (v2 index schema) with the test's
     "3". Phase 10 contributed no change here — at the phase-10 merge point
     `8e76ea0` the test and code agreed on "2".
  2. **`tests/gate_roundtrip.py`** — FAIL "rows must differ only by context".
     Same 06.2 merge dropped the index projection's `context` column (and
     `_row_from_index_tuple`'s `context: r[11]`), so `objective_history` rows
     lack the context field GATE-03 asserts.
  3. **`tests/packaging_roundtrip.py`** — FAIL `dist/itembank-sidecar-onedir`
     missing. Documented env gap since 10-02: PyInstaller freeze needs
     `powershell -File scripts/build_shell.ps1`, not runnable in this Linux
     bash environment.
  4. **`tests/phase_062_audit.py`** — FAIL "full suite not green": cascade of
     the three above; its own audit rows pass.

## Decisions / facts the next session should know

1. **Phase 10's whole contract is one immutable capture** (D-01/D-02): every
   derived claim (state, trend, weight, scheduler row, recommendation, queue
   entry, cap decision) is a pure function of one `evidence.capture_events`
   snapshot plus bounded settings. Snapshot ids hash the cutoff timestamp, so a
   later capture mints a new marker by design; stale/forged action claims fail
   closed (400, no session, no event).
2. **One parser, one scorer, one evidence writer, one selector.** `retention.py`
   chooses nothing and writes no evidence; weights enter Phase 7's
   `selection.select` via an allowlist-validated additive `retention_context`;
   every new event type goes through `evidence.append_event`.
3. **Six deterministic states** (unknown/weak/mastered/at-risk/due/stable);
   at-risk = proven success + configured silence (28d default); pending manual
   responses count for pacing only; only accepted human marks settle mastery;
   model/proposal events never advance an interval.
4. **Anki is read-only and separate** — owner-labelled `Anki: D due · N new`,
   never summed with itembank counts, exact locked unavailable copy, and its
   state never changes the snapshot/cap/weight.
5. **Cap + override:** per-subject live local-day cap gating both start and
   genuine submit (re-capture before append); the one exception is a
   sitting-scoped override (`cap_override` event, exact confirmation phrase,
   expires with the sitting) — no persistent cap-disable setting exists.
6. **`schema_validate.py` real interface:** `schema_validate.py <schema>
   <instance|->`, `--jsonl <path>`, `--array <path> <key>`; CI validates real
   start/submit/report/lint payloads. Note: CI's `['item']['objective']`
   extraction is stale on this HEAD (the item payload/schema no longer carries
   `objective`); the close-out used the equivalent bank-scoped evidence query.
   Flagged for the integrator.
7. **10-VALIDATION.md stale reference:** its regression gate names
   `tests/teaching_roundtrip.py`, which no longer exists; the teaching contract
   is covered by `tests/lesson_roundtrip.py` (green).

## Human-pending items (blocking gates, NOT executed by the agent)

1. **10-06 Task 3 human UI checkpoint (blocking).** A human must verify the
   approved Phase 10 UI at 1280/768/375 px: activity-first hierarchy, owner
   labels never summed, six states/raw evidence/uncertainty readable without
   color, overview→subject→objective drilldown + week windows, keyboard order/
   focus return/Escape, exact cap/override/Anki-unavailable/report-failure
   copy, stale-refresh + explicit lesson completion + cancelled/accepted/
   expired override, offline behavior, and DOM/API leak inspection. Steps:
   `python itembank.py daemon fixtures --no-open --port 8730` with the
   synthetic Phase 10 fixture, then follow `10-06-PLAN.md` Task 3; resume-signal
   is `approved` or a concrete failure. The automated structural half is green.
2. **Fix the pre-existing 06.2 merge regression on main** (evidence index
   context column + `INDEX_VERSION` 2→3; suggested patch in
   10-VERIFICATION.md) so `evidence_roundtrip.py` / `gate_roundtrip.py` /
   `phase_062_audit.py` go green. This is Phase 6.2's code — best applied by
   the orchestrator centrally rather than on each phase branch.
3. **`packaging_roundtrip.py`** onedir gate: run `powershell -File
   scripts/build_shell.ps1` on a Windows host, then re-run.

## Files updated for close-out (this branch, one atomic commit)

- `.planning/phases/10-retention-pacing-trends/10-VERIFICATION.md` (new)
- `.planning/phases/10-retention-pacing-trends/10-UAT.md` (new)
- `HANDOFF-PHASE10.md` (replaced the mid-phase continuation prompt with this
  close-out)

Per directive, **not** touched here: `.planning/ROADMAP.md` (Phase 10 checkbox
remains unticked for the orchestrator to flip after all phase branches merge),
`.planning/STATE.md`, `.planning/config.json`, `.planning/REQUIREMENTS.md`.

## Not done (by design / out of scope)

- **No merge, no push** — branch `gsd/phase-10-close` is local to the worktree,
  per the run directive.
- Deferred Phase 10 research items, recorded with cost: lesson-to-item transfer
  (not computable from the log as it stands), Anki card-interval/ease writing,
  predictive/ML mastery, curriculum auditing.
- No gamification: return rate is a stated-denominator ratio, never a streak;
  no points, no loss states.

## Next steps for the integrator

1. Reconcile ROADMAP/STATE/config centrally after all phase branches merge;
   tick Phase 10 (checkbox + "Plans: 6/6") and mark SCHED-01..04, TREND-01..05
   complete in REQUIREMENTS.md.
2. Apply the 06.2 index fix centrally (10-VERIFICATION.md has the exact patch
   shape), re-run `tests/evidence_roundtrip.py` + `tests/gate_roundtrip.py` +
   `tests/phase_062_audit.py`.
3. Run the Phase 10 human UI gate (item 1 above) and record `approved` or the
   concrete failure in 10-UAT.md.
4. Correct the stale `teaching_roundtrip.py` reference in 10-VALIDATION.md and
   the stale CI `['item']['objective']` extraction.
