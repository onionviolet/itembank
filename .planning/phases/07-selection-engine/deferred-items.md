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
