# Phase 04 Close-Out — handoff

Phase 04 (surface redesign & theming) is fully EXECUTED and merged on `main`.
This handoff records the close-out work, what remains for a human, and three
out-of-scope suite findings that need routing.

## Close-out completed (2026-08-11, branch `gsd/phase-04-close`)

1. **Verification record ported.** The 2026-08-11 live re-verification
   record from branch `gsd/deferred-verify` (commit `e7c8634`, "5/5 truths
   live, 7 human items remain") was reconciled into
   `.planning/phases/04-surface-redesign-theming/04-VERIFICATION.md`
   (commit `c1dcc89`).
2. **Live re-verification re-run.** Every phase-04 truth was re-run fresh in
   the close worktree against the merged main code (`2b5678c`):
   - Truths 1-5 (sticky context line / study rationale / shared palette +
     key-free served pages / OS picker + contrast-checked pairs /
     optimistic-concurrency day editing) — **all VERIFIED** by the six phase
     harnesses (`day_edit`, `theme`, `presentation`, `surface`, `daemon`,
     `config` roundtrips), all green.
   - The seven human-only items (visual walkthrough, live OS picker,
     screen-reader sequence, colour-blind verdict check, two-editor day
     conflict, 320px/200% backstop, visual adequacy) remain
     **PENDING HUMAN** — nothing was fabricated or silently marked verified.
3. **04-UAT.md updated** with a close-out re-run note (tests 3 and 7 stay
   blocked/human); **04-VERIFICATION.md** carries the full close-out record.

## Remains human (7 items — see 04-VERIFICATION.md "HUMAN-REQUIRED")

One-product visual walkthrough (light/dark, desktop + 320px/200%, keyboard);
live native picker + browser fallback in `/settings`; screen-reader sequence
with reduced motion; colour-blind / non-colour verdict check; two-editor day
conflict with real interleaving; backstop long-content at 320px/200% (12
screenshots saved by the 2026-08-10 UAT run); visual adequacy of the
reworked surfaces. When these are done, flip 04-VERIFICATION.md
`status: human_needed` → verified and tick the ROADMAP phase-04 checkbox
(orchestrator reconciles ROADMAP/STATE centrally after branches merge).

## Out-of-scope suite findings (need routing; none is phase 04)

Full suite (`tests/*.py`, 45 files) on current main: 42 PASS, 3 FAIL.

1. **`tests/evidence_roundtrip.py`** — FAIL "index was not rebuilt at
   version 3 after the stale check". Pre-existing regression from the 06.2
   merge (`d35bd15`): merged `evidence.py` kept `INDEX_VERSION = 2` and
   dropped the index `context` column while the 06.2-side test expects
   version "3". Route to a phase-06.2 owner.
2. **`tests/gate_roundtrip.py`** — FAIL "rows must differ only by context in
   log order, got [None, None]". Same root cause (index rows lack
   `context`). Same owner.
3. **`tests/packaging_roundtrip.py`** — FAIL "dist/itembank-sidecar-onedir
   is missing". Environmental: requires the PyInstaller Windows onedir from
   `powershell -File scripts/build_shell.ps1`, which cannot run from this
   WSL shell and is not committed (only `src-tauri/binaries/...exe` is
   tracked). Runs on a machine where the sidecar is built.

`phase_062_audit.py` fails only because its embedded full-suite run hits
those same three files; its own audit checks pass.

## Environment notes

- Worktree: `C:\Users\wayba\Downloads\CTF\itembank\.phase04-wt`
  (bash path `/mnt/c/Users/wayba/Downloads/CTF/itembank/.phase04-wt`),
  branch `gsd/phase-04-close`.
- The command-approval gate in this session blocks `; echo $?` suffixes,
  inline `python -c`, compound loops, and Windows PowerShell interop;
  bare `python tests/<file>.py` and `&&` chains run fine.
- `fixtures/_evidence/` created by a verification `itembank start` run is
  gitignored; `fake_hosted_unused.py` in the worktree root is a pre-existing
  untracked file left untouched.
