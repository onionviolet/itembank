# Deferred Items — Phase 7 (selection-engine)

Out-of-scope discoveries logged during execution, per the executor scope boundary
rule. None of these are caused by phase 7 changes; they are recorded so they are
not silently lost.

## `itembank guard .` fails on pre-existing untracked files (2026-08-10)

- `itembank guard .` reports three offending files that parse as question banks:
  `.agents/skills/author-bank/SKILL.md`, `.claude/skills/author-bank/SKILL.md`,
  and `_tmp_lesson_trial/pin_bank.md`.
- All three predate phase 7 (present as untracked files before any phase 7 edit)
  and belong to the workspace's skill installation / temp files, not to phase 7.
- The phase 7 fixture itself is guard-clean: `itembank guard fixtures/selection_bank.md`
  exits 0.
- **Fix options (not taken, out of scope):** teach `cmd_guard` to skip
  `.agents/`, `.claude/`, and `_tmp_*` scratch dirs, or move the temp bank out of
  the repo. Revisit before `$gsd-ship`, since a red `guard .` will block it.

## `tests/lesson_roundtrip.py` spec-only test red (pre-existing, 2026-08-10)

- `test_spec_only_bank_round_trips_new_constructs` (03.1-06 Task 3 Test 3)
  expects a minimal 2-option bank to lint with zero errors. The current lint
  rules (in HEAD and in the working tree alike) emit `item.too_few_options`
  plus `item.missing_id` / `item.missing_second_best` /
  `item.distractor_missing` / `key.missing_id` findings for that bank.
- Verified independent of phase 7: reproduced against `HEAD:model.py` with a
  synthetic bank; phase 7 changes touch no lint or lesson code.
- The fix belongs to the in-progress 03.1-05/03.1-06 style/grammar work
  (uncommitted `model.py` changes in the working tree), not to this phase.
- **Impact:** `for t in tests/*.py; do python "$t" || exit 1; done` stays red
  until that work lands. All phase-7-relevant suites are green.

## Coordination note: concurrent commits swept phase-7 files (2026-08-10)

- While plan 07-01 Task 2 was being committed, a concurrent session committed
  the 13-01 sidecar work; its `test(13-01)` commit swept up the still-staged
  `selection.py`, `surfaces/session.py`, `itembank.py` and `build.py` changes
  (commit `dac4bbd`). Content is fully preserved in history; only the commit
  labels are mixed. The phase-7 daemon hunk landed in its own commit
  (`b209a5f`).
- The user's pending `fonts` entry in `build.py:STAGE_DIRS` was recovered from
  the dangling stash commit `3b948c5` and restored to the working tree.

## `tests/protocol_roundtrip.py` red on SESSION_VERSION (pre-existing, 2026-08-10)

- Working-tree `runtime.py` carries an uncommitted `SESSION_VERSION = 1 -> 2`
  bump from the concurrent 06-01 session; `schemas/session.schema.json` still
  declares `x-itembank-version: 1`, so `protocol_roundtrip` fails with
  "session.schema.json's x-itembank-version is 1, does not match the constant
  it describes (2)".
- Not caused by phase 7: phase 7 never touches `SESSION_VERSION` or the session
  schema. Belongs to the in-progress 06-01 hint-ladder work (its commit history
  shows RED-test commits mid-TDD).

## Concurrent phase-6 evidence-contract migration (in flight, 2026-08-10)

The concurrent 06-01 session is mid-flight on the evidence contract. Working
tree (uncommitted or just-landed) changes break three suites that phase 7 does
not own:

- `tests/evidence_roundtrip.py`: session render misses required `teaching_state`
  key (session schema now v2).
- `tests/protocol_roundtrip.py`: `report.schema.json` gained a oneOf branch set
  (`auto_attempts`/`objectives`/`schema_version: 2` vs `const 1`) the current
  renderer does not emit.
- `tests/daemon_roundtrip.py` `check_cli_twin_route`: a route now returns a dict
  where the test expects a JSON string (sidecar/token route change).

Phase-7 handling: the selection evidence fixture was regenerated to
`schema_version: 2` (tracking the live `evidence.response_event()`), and
`check_fixture_history_matches_response_schema` validates strictly when the
schema version matches and names the drift explicitly during the transition, so
the phase-7 suite is green on either side of the migration.

## Plan-text corrections logged during 07-02

- 07-02 Task 1 acceptance claimed `lint fixtures/sample_bank.md` reports
  "0 errors, 0 warnings"; the sample bank has always carried six
  `item.objective_unnamespaced` warnings (verified identical on HEAD). CI only
  asserts zero errors. Phase 7 adds none.
- 07-02 Task 3's mutation instruction ("removing `|\n\[PAIR` makes
  `check_pair_served_together` fail") does not hold with the plan's own fixture
  placement of `[PAIR:]` after `[OBJECTIVE:]` (the stem already terminates at
  `[OBJECTIVE]`, and `q["pair"]` still parses). The alternation is instead
  pinned by a stem-purity assertion in `check_pair_singleton_lint`, which the
  same mutation does fail (verified, reverted).

## Coordination: `c08aa42` absorbed 07-03's index work (2026-08-10)

The concurrent session's `feat(06-01)` commit `c08aa42` swept up the staged
07-03 changes to `evidence.py` (bank column, objective/bank rows, `bank=`
filter), `schemas/report.schema.json` (two documented properties) and
`surfaces/evidence_cli.py` (--bank threading). All content is present in HEAD;
the remaining 07-03 pieces were committed separately (`d8a21ce` cli --bank,
`b8fc6cc` tests). Labels in history are mixed; no content was lost.
