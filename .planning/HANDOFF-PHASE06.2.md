# HANDOFF — Phase 06.2: Executable Textbook Loop

**Branch:** `gsd/phase-06.2-textbook-loop` (worktree `.phase062-wt`)
**Status:** COMPLETE — 4/4 plans, 4 atomic commits, not merged, not pushed
**Date:** 2026-08-11

## What shipped

The lesson gate as a **presentation policy over existing item types** (no
seventh item type, no second scorer, no lesson-local schedule):

1. **feat(06.2-01) `376dae4`** — the evidence layer locked before any
   pixel: `[GATE: required|recommended|off]` lesson-preamble grammar
   (additive, default `recommended`, `lesson.invalid_gate` lint),
   `lesson.check_ref_unknown` resolution lint against the single
   `CHECK_UNRESOLVED_COPY` constant, `gate_skip` as its own
   `KNOWN_EVENT_TYPES` member (`gate_skip_event` with a
   (session, check) dedupe key and **no score key**), the response-event
   `context` field (`quiz` default / `lesson_gate`), `gate_state()`
   read-side derivation, the schema `context` enum + `gate_skip_event`
   $def, and the index projection v3 with a `context` column.
2. **feat(06.2-02) `b1be8ba`** — the gate band renders 3.1's reserved slot
   live: `<section class="gate">` with the check item's public projection,
   one form, check-first/skip-second named submit buttons, zero
   JavaScript; G1 truncation (server emits nothing below an open check),
   the two-row boundary copy, G2 recommended flow, `off`/no-session =
   3.1 byte-identical (compatibility floor), the diagnostic/exam
   mode-degrade, TOC + glossary-appendix filtering, and the unresolvable-
   check D1 degrade.
3. **feat(06.2-03) `7e74e05`** — the interaction: recorded-skip control
   (`gate_skip: always|after-attempt`, never a transgression, never a
   disabled button), `gate_skip`/`gate_policy` settings (weaken-only),
   `POST /lesson/<stem>/check` + `/skip` behind the loopback authority
   gate with 303 post-redirect-get (reload never re-submits), focus on the
   revealed `<h2 tabindex="-1" autofocus>`, the composed status-region
   announcement, the section-12.1 unreachable degrade, the
   `lesson-check`/`lesson-skip` CLI twins (ROUTE_CLI), and the
   `gate_outcome_split` report (pair-level, stated denominator, no
   target/streak/fill).
4. **test(06.2-04) `698f5df`** — the twelve UI-SPEC §13 gates as
   executable fixtures, `tests/phase_062_audit.py` (6/6 GATE-01..06
   coverage), and `06.2-GATES.md`.

## Requirement status

GATE-01..GATE-06 all DELIVERED (REQUIREMENTS.md §Gate updated; ROADMAP
Phase 6.2 checklist and phase table updated; STATE.md annotated;
06.2-VALIDATION.md set validated).

## Verification summary

- `python tests/gate_roundtrip.py` — ok (43 fixtures)
- `python tests/daemon_roundtrip.py` — ok (65 checks)
- `python tests/phase_062_audit.py --quick` — ok
- `python tests/lesson_roundtrip.py`, `evidence_roundtrip.py`,
  `protocol_roundtrip.py`, `config_roundtrip.py`, `scoring_roundtrip.py`,
  `selection_roundtrip.py`, `surface_roundtrip.py`, `hint_roundtrip.py`,
  `model_gate_roundtrip.py` — ok
- `06.2-VERIFICATION.md` (6/6) and `06.2-UAT.md` (A1–A6) both PASSED

## Known issues carried forward (NOT this phase's regressions)

Both fail identically on the base commit without this phase's changes:

1. **`tests/model_surface_roundtrip.py`** — references
   `surfaces.session.do_rubric_review`, which the committed
   `surfaces/session.py` lacks. The Phase 08 chat's main-tree working copy
   carries the uncommitted implementation; Phase 08 must land it.
2. **`tests/packaging_roundtrip.py`** — requires
   `dist/itembank-sidecar-onedir` (built by `scripts/build_shell.ps1`),
   absent in a fresh worktree; Phase 13 must build it before CI.

## Human-verify item (recorded, not claimed verified)

- True screen-reader announcement behavior on a fresh server-rendered
  page (06.2-UI-SPEC §7.2/§14 backstop). The focus move is the primary
  channel and carries the information on its own; the `role=status` text
  is additive. Test instructions are in `06.2-GATES.md`.

## Environment notes

- The daemon suite's `check_api_start_traversal` snapshots the whole /tmp
  parent directory; under concurrent chat load (other phases' suites
  creating temp dirs mid-run) it flakes. Run the suite when /tmp is quiet
  or re-run on failure. `check_serve_attempt_refresh` starts a seedless
  API session that can randomly land on a `short` item (score None by
  design) — pre-existing flake.
- The concurrent main-tree `run_all.py` pollutes /tmp the same way; do
  not attribute those failures to 6.2.

## For the next phase

- Phase 10 (retention) consumes `gate_skip` as a prioritization signal
  (D-09) and reads `context` on lesson-gate responses; `EVENT_SCHEMA_VERSION`
  stayed 2 — pre-6.2 v2 events without `context` are read by the
  version-tolerant `events()` reader, not by schema validation.
- Phase 3.2/11 authoring guidance: document the caution that a
  `[GATE: recommended]` lesson should not state the check's answer in the
  very next paragraph (UI-SPEC §5.2 residual hazard; no lint check added).
- Cross-bank `[!CHECK:]` stays rejected (D-01 ≡ 3.1 D-06); widening is
  additive and both phases must widen together.

**Merge note:** branch `gsd/phase-06.2-textbook-loop` is ready to merge to
main once the concurrent phase branches (05/08/10) land; STATE.md /
config.json / ROADMAP.md / REQUIREMENTS.md edits from this phase are in the
branch and may need light reconciliation with the concurrent chats'
updates.
