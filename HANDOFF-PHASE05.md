# HANDOFF — Phase 05: Check Item Type & Code Editor

**Branch:** `gsd/phase-05-check` (sibling worktree `itembank-phase5`; **not merged to main**)
**Date:** 2026-08-11
**Status:** 7/7 plans complete; 2 human checkpoints PENDING (recorded, never faked)

## What shipped

A learner can now write and run their own code against a `[TYPE: check]` item in a real
editor and get a dichotomous verdict through the same scorer as every other type.

- **Format contract:** `CASE)`, `[LANG:]`, `[MATCH:]` (exact/trimmed/regex), `[HARNESS:]` +
  `[TOLERANCE:]`, `STARTER:` — parse, lint, fingerprint, and SPEC section (05-01).
- **Runner:** `runner.py` executes source once per case under `check.timeout_seconds` and
  `check.max_output_bytes`, kills the tree on both platforms (POSIX killpg; Windows
  job-object + taskkill fallback), and surfaces a killed-at-timeout run as no-verdict
  (criterion 12) (05-01, 05-02).
- **Settings + gates:** the four `check.*` settings keys; both submit paths gate on the one
  `run_check_source`; network-bound execution refused by default; unknown language refused
  with its own sentence (05-03).
- **Editor:** vendored CodeMirror 6 under `assets/vendor/codemirror/` (bundle + one boot
  script + VENDOR.md §4a record); 1-based gutter, Tab inserts a tab, Shift-Tab dedents the
  current line only, read-only after submit, no wrap; honest-limits line beside the editor
  reading the same constant SPEC does (05-05).
- **Readout + refusals:** per-case matrix (Case N / status / input / expected / actual,
  bound stops in the warning role, null verdict renders pending); offline file-page refusal
  + skip that records nothing; network refusal (pending) and language refusal (error)
  (05-06).
- **Evidence + docs + gate:** attempt file shows the submitted source; published
  item.schema.json (interaction envelope, boolean-or-null verdict, stable observation
  reasons); README check section; claim-word gate with exact per-file counts (05-07).

## Per-plan commits (all on gsd/phase-05-check)

| Plan | Commits |
|---|---|
| 05-01 | (pre-existing on branch: parser, runner, scoring, tracer) |
| 05-02 | (pre-existing: bounds, job object, grandchild fixture) |
| 05-03 | (pre-existing: settings, gates, network refusal) |
| 05-04 | `a21fb08` — spike record (measurement PENDING) |
| 05-05 | `0082ce3`, `005ea95`, `1a65e53`, `fe8bbcc`, `48553a2`, `ad6f08b`, `eb976e7`, `da42f6b` |
| 05-06 | `8b6a8ae`, `bcadf4d`, `6156ca8` |
| 05-07 | `8716073`, `b90ce47`, `b659741`, `6e01a37` |

## PENDING — human (do not mark verified without these)

1. **05-04 Windows kill spike (plan 05-04 Task 1).** This session's shell is WSL2 and cannot
   spawn any Windows process (verified three ways; `run-detectors` error on every PE
   binary). `05-SPIKE-RESULT.md` records the blocker and **0 of 50 runs executed** — the
   escape rate, both kill paths' outcomes, and `JobObjectExtendedLimitInformation` are
   PENDING. **Resume:** run the six steps in a Windows terminal on this machine, paste the
   results, then type "verified" (05-04-PLAN.md lists the steps).
2. **05-07 end-of-phase pass (plan 05-07 Task 3).** The five items need a real browser
   against a served page; this session cannot keep a daemon alive across tool calls
   (background jobs denied). The jsdom runner (`node --test tests/js/`) already executes the
   keyboard/gutter behaviours. **Resume:** `python itembank.py serve fixtures/check_bank.md`
   and work through the five items; paste the five observations, then type "verified".

## Verification status

- All automated tests green: `python tests/*_roundtrip.py` + `node --test tests/js/` (7/7).
  Pre-existing environmental exclusions unchanged: `tests/packaging_roundtrip.py` (missing
  Windows-built dist) and the tolerated FAIL line in `tests/presentation_roundtrip.py`.
- `python itembank.py guard .` PASS.
- `05-VERIFICATION.md` (10/10 automated truths; 2 human items PENDING) and `05-UAT.md`
  (8 automated tests pass, 2 blocked on environment) written honestly.
- `.planning/STATE.md` updated for the branch; `.planning/config.json` needs no per-phase
  change (verified against the git history of every prior closeout).

## Notes for the next executor

- The daemon's unknown-language refusal was normalized to a normal JSON
  `{"refused", "refused_reason"}` body on both submit routes (05-06); the CLI path still
  exits non-zero with the locked copy.
- `tests/js/` needs `npm ci --prefix tests/js` once per fresh checkout (node_modules is
  gitignored; the lockfile pins jsdom 29.1.1).
- The claim-word gate covers the phase's SUMMARY/SPIKE records too — keep the standalone-phrase
  and the literal grep pattern out of future summaries for this phase.
- The main tree's STATE.md is shared history; this branch's closeout edits are additive
  (phase-05 rows, deferred-verification row) and do not clobber 06.x tracking.
