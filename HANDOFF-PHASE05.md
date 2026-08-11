# HANDOFF — Phase 05: Check Item Type & Code Editor

**Branch:** `gsd/phase-05-check` (sibling worktree `itembank-phase5`)
**Date:** 2026-08-11
**Status:** 7/7 plans complete; **merged with main** (post-merge suite green); 2 human
checkpoints PENDING (recorded, never faked)

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

## Post-merge finalization (main → gsd/phase-05-check, 2026-08-11)

The branch was 73 commits behind main; `git merge main` produced 15 conflicted files,
all resolved keeping **both phases' behavior**, then the full suite was re-run live and
every regression fixed in its own atomic commit:

**Merge conflicts resolved (commit `29042a5`):**
- `build.py` — STAGE_FILES keeps both `retention.py` (main) and `runner.py` (phase 05).
- `evidence.py` — took main's superset file and re-applied phase 05's three hunks
  (`response_event` keyword-only `check_source`/`interaction_version`/`error_category`
  alongside main's `context="quiz"`, the three event keys, the check-source branch in
  `render_attempt_md`).
- `fixtures/selection_evidence.jsonl` — regenerated as the merged event shape
  (both `context` and the check fields present on all 40 events).
- `model.py` — fingerprint, SPEC (`_check_section()` + 06.1 visual section), lint codes,
  and the lint per-type branches (check + visual both; `why` not required for check).
- `runtime.py` — `public_item` (check + visual contracts), `canonical_response` /
  `canonical_key` (registry + visual branch), `score_response` (visual verdict
  special-cased, check None-on-timeout preserved).
- `schemas/item.schema.json` — JSON-level union: type enum `check`+`visual`, oneOf both
  refs, $defs from main plus phase-05's check defs (`check_item`, `interaction_contract`,
  `check_renderer_config`, `check_response_schema`, `interaction_result`,
  `case_observation`).
- `schemas/lint_error.schema.json` — deduped union of both code sets (87 codes).
- `schemas/response.schema.json` — required list union (`context` + check fields),
  item_type enum union, main's permissive-branch event types (selection moved to its own
  closed branch on main).
- `schemas/settings.schema.json` — JSON-level union: main's property values for shared
  keys (newer `model_backend`/`reader`), phase-05 `check` property added, required list
  unioned.
- `surfaces/quiz.py`, `surfaces/quiz_page.py` — CM6 bundle/boot + AgentAssist both
  embedded; `asCheck` + `asVisual`/`asVisualOffline` both shipped in the clients; LABEL
  maps and dispatchers unioned.
- `surfaces/session.py` — import union; submit path keeps the check branch and the
  10-04 cap recheck.
- `tests/config_roundtrip.py`, `tests/protocol_roundtrip.py` — expected key set and both
  contract tests kept.
- `.planning/STATE.md` — resolved to main's version (orchestrator reconciles centrally;
  ROADMAP/STATE/config untouched by this branch).

**Regression fixes after the merge (one commit each):**
- `ecb3442 fix(05-01)` — runtime: unify the two shadowing `interaction_result`
  definitions (check envelope + visual envelope dispatch on `q["type"]`).
- `3bc17f5 fix(05-03)` — settings schema keeps main's newer `model_backend`/`reader`
  shapes (the first pass had given phase 05's older shapes precedence).
- `14f9a89 fix(05-01)` — restore the 06.2 `context` index column + `INDEX_VERSION 3`
  that main's own 06.2 merge (`d35bd15`) had dropped; fixes gate_roundtrip and
  evidence_roundtrip.
- `0dd8ceb test(05-01)` — re-pin the sole scorer's source hash after the visual branch
  joined it (the pin's contract requires a plan-recorded justification, noted in-file).
- `98cc4b3 test(05-05)` — scope the editor keydown guard so the visual SVG arrow-key
  accessibility handler is permitted; editor config still lives only in the boot script.
- `990f39c test(05-06)` — allow the check case-status `reason` (published
  `case_observation.reason`) in the served-script authority-vocabulary guard.
- (The served refusal-copy `+` concatenation fix from `node --check` rode inside the
  merge commit — it was fixed before the merge was committed.)

**Post-merge verification (all run live in the worktree):**
- `python tests/*.py` — 46/47 pass; the only failure is the documented pre-existing
  environment exclusion `tests/packaging_roundtrip.py` (no Windows-built dist). Audits
  run as `phase_062_audit.py --quick` (its embedded full-suite run is redundant here).
- `python itembank.py lint fixtures/sample_bank.md` — 0 errors (6 pre-existing subject
  warnings); `fixtures/check_bank.md` lints clean; `broken_bank.md` still reports every
  CI-named message.
- `python schema_validate.py` round trip — session/item/response/report/lint_error all
  validate (7/7 harness checks, mirroring CI).
- `python itembank.py guard .` PASS; skill mirrors `diff -rq` identical; path-leak scan
  clean.
- `node --test tests/js/` — 7/7 pass (npm ci via `node npm-cli.js ci` — the npm shim is
  unusable under WSL 1).

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
- `.planning/STATE.md` was resolved to main's version at merge time — the phase-05 rows
  and the deferred-verification row are NOT in it; the orchestrator reconciles
  ROADMAP/STATE/config centrally after all phase branches merge, so this branch left
  them alone (per the finalization contract).

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
