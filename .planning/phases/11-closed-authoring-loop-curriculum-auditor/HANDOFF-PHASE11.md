# HANDOFF — Phase 11: Closed Authoring Loop & Curriculum Auditor

**Branch:** `gsd/phase-11-auditor` (worktree: `C:\Users\wayba\Downloads\CTF\itembank\.phase11-wt`)
**Base:** `5aab199` (main HEAD at worktree creation)
**Status:** EXECUTED — 5/5 plans, 12/12 tasks, all gates green. **Merged with main and finalized for merge (`2c84132`); not pushed.**
**Handed off:** 2026-08-11

## What was delivered

Five atomic commits, one per plan:

| Commit | Plan | Contents |
|---|---|---|
| `33cebe4` feat(11-01) | tracer | `authoring.py` (repository-blind `run_authoring`, four named detectors, structured retry, immutable proposal, duplicate-run idempotency), `auditor.py` (UTF-8 source normalization + citations), `audit_writer.py` (shadow write/undo), `surfaces/audit_cli.py`, `tests/audit_roundtrip.py`, SUMMARY |
| `7e4d6f1` test(11-02) | schemas | five strict versioned JSON Schemas (authoring_request, normalized_document, quality_finding, audit_report, write_manifest) + `--case schemas` parity/rejection tests |
| `d97f56d` feat(11-03) | coverage | citation-first coverage engine (covered/partial/conflicting/gap/unknown), Markdown/text fidelity + body objectives, 18-case PDF/DOCX gold gate, material/weak-objective handoff, `tests/audit_coverage_roundtrip.py` |
| `2ece4a4` feat(11-04) | quality/retry/autonomy | exact four-detector profile + boundary fixtures, scope-before-lint retry state machine, prompt-injection resistance, three-mode autonomy (report_only / draft_and_approve with pending-resume + exact write-id approval / full with opt-in + caps), every-exit volume, `audit_quality_roundtrip.py` + `audit_authoring_roundtrip.py` |
| `7e50566` fixup!(11-04) | test follow-up | folds the required `full_opt_in` test updates into `tests/audit_roundtrip.py` (the tracer/schemas cases use full mode; left uncommitted by the plan commit, then fixed up -- a rebase was declined, so this sits as an explicit fixup commit) |
| `7df425d` feat(11-05) | adapter/writer/CLI | additive `author` adapter operation, `itembank audit source|coverage|material|author|undo` registration with configured-adapter binding in `surfaces.cli.main`, Git/shadow writer with per-bank OS lock + manifest-routed undo, `build.py` pyz stage fix, `audit_cli_roundtrip.py` (no-DI subprocess) + `audit_writer_roundtrip.py` |

New production files: `auditor.py`, `authoring.py`, `audit_writer.py`, `surfaces/audit_cli.py`, five `schemas/*` documents, `fixtures/audit/*`, seven `tests/audit*_roundtrip.py` (incl. `audit_roundtrip.py`).
Modified: `model_adapter.py`, `schemas/model_adapter.schema.json`, `surfaces/cli.py`, `audit_writer.py` internals, `build.py`, `.planning/*` (SUMMARIES, VERIFICATION, UAT, STATE.md, config review).

## Verification summary

- All plan gates pass: `audit_roundtrip.py` (tracer+schemas), `audit_coverage_roundtrip.py`, `audit_quality_roundtrip.py`, `audit_authoring_roundtrip.py`, `model_adapter_roundtrip.py`, `audit_cli_roundtrip.py`, `audit_writer_roundtrip.py`.
- Full suite in the worktree: **33/37 pass**, including every Phase 11 suite. See `11-VERIFICATION.md` for the four environmental/non-regression failures:
  - `model_surface_roundtrip` — already failing at baseline `5aab199` (Phase 8 chat's uncommitted `do_rubric_review`); this branch never touches those files.
  - `daemon_roundtrip` — hostile-dir `/tmp` snapshot trips on concurrent reasonix/session temp dirs.
  - `day_roundtrip` — HTTP timeout under parallel load; passes standalone.
  - `packaging_roundtrip` — requires the Phase 13 Rust sidecar (`scripts/build_shell.ps1`); the pyz stage regression this branch introduced was fixed (auditor/authoring/audit_writer now staged).
- The D-15 checkpoint (11-05-02) resolved to **proceed** — the locked Git/shadow write-id/manifest/backend/undo contract was implemented without reopening the design.

## Notes for the integrator / next phases

1. ~~Do not merge until...~~ **Merged.** `git merge main` landed on this branch as `2c84132` (2026-08-11) after main had advanced 50 commits (phases 03.1, 06.1, 06.2, 07, 08-04/05, 09.1, 10, 999.5, 13-03/04/05). The branch is now up to date with main and carries no pending integration work from this side.
2. `.planning/config.json` contains no per-phase status keys (reviewed end to end); state lives in `.planning/STATE.md`. **The merge resolved `.planning/STATE.md` to main's version (both sides had rewritten it; this branch's phase-11 status update was dropped by design — the orchestrator reconciles STATE.md/ROADMAP.md/config.json centrally after all phase branches merge).** Do not expect `current_phase: 11` in STATE.md until that central pass runs.
3. `11-UAT.md` lists the four supplemental human checks (approval UX, locator inspection, model-unavailable flow, undo/conflict presentation) that remain experiential; the automated authority for each is cited.
4. PDF/DOCX remain an explicit unsupported/lossy gate (`fixtures/audit/locator_fidelity_cases.py`, 18 gold cases). A future adapter may claim support only for structures that round-trip exactly; the gate will fail any builder drift by sha256.
5. The `audit` CLI is the sole Phase 11 surface. Daemon/frontend routes are UI-BLOCKED pending `11-UI-SPEC` approval; `surfaces/audit_cli.py` and the domain modules are ready for a thin route twin.
6. Full autonomy (`--mode full`) is wired through an explicit CLI opt-in with `--cap-run`/`--cap-objective` bounds; the settings enum value `audit_draft_lint_fix_commit` is exposed as the `full` mode and the model can never select it.
7. Machine-authored Git writes commit one unit + its manifest per commit under `<repo>/.itembank/audit/manifests/`; the applied-state metadata update is post-commit on disk, and undo resets only the writer's own metadata before `git revert`. Verify this layout is acceptable for your vault repos before enabling `--write` on real banks.
8. `--base` on `audit author` resolves `itembank.json` (model backend); a disabled backend (default) makes authoring fail closed with a retained report and zero writes.

## Post-merge finalization (2026-08-11)

**Merge conflicts resolved** (3 files; all others merged cleanly):

| File | Conflict | Resolution |
|---|---|---|
| `.planning/STATE.md` | both sides rewrote the state front-matter and tables | kept **main's version** (theirs); orchestrator reconciles centrally — see note 2 |
| `build.py` | both sides edited `STAGE_FILES` (main added `retention.py`; this branch added `auditor.py`, `authoring.py`, `audit_writer.py`) | kept **both** — the merged tuple contains all four additions |
| `surfaces/cli.py` | main converted the file CRLF→LF and added Phase 9.1 audio/export commands; this branch added the Phase 11 audit subcommands | took main's LF version and **re-applied this branch's four additive chunks** (`cmd_audit` import, `_configured_author_callable`, the `audit source\|coverage\|material\|author\|undo` subparser block, `_load_settings_for`) — file stays LF to match main |

`model_adapter.py` and `schemas/model_adapter.schema.json` were changed only by this branch and merged cleanly (main never touched them).

**Post-merge suite (full `tests/*.py`, run live in this worktree):** 48/51 pass, including all six Phase 11 audit tests (`audit_roundtrip`, `audit_cli_roundtrip`, `audit_coverage_roundtrip`, `audit_quality_roundtrip`, `audit_authoring_roundtrip`, `audit_writer_roundtrip`), `model_adapter_roundtrip`, the Phase 8/10/06.1/09.1 suites, `itembank.py lint fixtures/sample_bank.md` (0 errors), and `schema_validate.py` against a live runtime payload (0 errors). Three non-regression failures, all **pre-existing on main** (verified by running them in a clean `main` worktree):

- `tests/evidence_roundtrip.py` — main's own `evidence.py` still carries `INDEX_VERSION = 2` while its test asserts a v3 rebuild; fails identically on clean main.
- `tests/gate_roundtrip.py` — main's `objective_history()` rows project no `context` key while its own test expects `["lesson_gate", "quiz"]`; fails identically on clean main.
- `tests/packaging_roundtrip.py` — requires the Phase 13 Windows sidecar build (`powershell -File scripts/build_shell.ps1` → `dist/itembank-sidecar-onedir`); a build-artifact prerequisite, not a code regression. All pre-sidecar packaging checks (incl. `python build.py` with the merged `STAGE_FILES`) pass.
- `tests/phase_062_audit.py` passes with its documented `--quick` flag (its full mode re-runs the whole `tests/*_roundtrip.py` suite internally and would inherit the two pre-existing failures above).

**No regressions were introduced by the merge** — no fix commits were required.

## Files created for review

- `.planning/phases/11-closed-authoring-loop-curriculum-auditor/11-01..05-SUMMARY.md`
- `.planning/phases/11-closed-authoring-loop-curriculum-auditor/11-VERIFICATION.md`
- `.planning/phases/11-closed-authoring-loop-curriculum-auditor/11-UAT.md`
- `.planning/STATE.md` (updated — superseded by main's version at merge, see note 2)
