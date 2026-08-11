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
