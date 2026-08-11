# HANDOFF — Phase 02.1: Packaging, Self-Update & Interop Export

**Branch:** `gsd/phase-02.1-close` (worktree `.phase021-wt`)
**Base:** `2b5678c` (main tip, 2026-08-11)
**Status:** PHASE EXECUTED ON MAIN, CLOSE-OUT DOCS ONLY — NOT MERGED, NOT PUSHED
**Date:** 2026-08-11

## What this branch is

Phase 02.1 (double-clickable per-OS packaging, safe self-update, GIFT export)
was fully **executed and merged to main** by earlier sessions — plans 02.1-01..09
all carry SUMMARYs and their code is on main. The phase was never *closed*: the
ROADMAP checkbox was unticked and `02.1-VERIFICATION.md` still said
`status: human_needed` with no live re-verification record. This branch is the
close-out: it ports the 2026-08-11 live re-verification record that lived
unmerged on `gsd/deferred-verify` (commit `9da0da9`), re-runs the automated
verification live in this worktree, updates the UAT doc, and records a handoff.

## What was delivered (one atomic commit)

| Commit | Message | Files |
|--------|---------|-------|
| (this branch's single commit) | `docs(02.1): close phase 02.1 - live verification + UAT + handoff` | `.planning/phases/02.1-packaging-self-update-interop-export/02.1-VERIFICATION.md`, `.../02.1-UAT.md`, `.../HANDOFF-PHASE02.1.md` |

No code changed. The phase's code already lives on main (merged via plans
02.1-01..09); this branch only closes the verification/UAT/handoff loop. The
record content from `9da0da9` was ported (frontmatter `verified` →
`2026-08-11T15:30:00Z`, the "Deferred Verification Run" section) and then
reconciled with what was actually re-run in this worktree.

## Verification — live re-run in this worktree (2026-08-11)

All commands ran inside `.phase021-wt` (branch `gsd/phase-02.1-close`, at main
tip `2b5678c`).

### Phase-02.1 automated truths — all PASS

| Truth | Evidence |
|-------|----------|
| 1-3. Launcher + plain-Python artifact + side-by-side self-update | `tests/packaging_roundtrip.py` 17/18 PASS (sole failure = env-blocked phase-13 onedir, below); `tests/packaging_shell_roundtrip.py` PASS; `python build.py` → `dist/itembank-0.3.0.pyz` (1,641,586 bytes) + 5 artifacts; `cmp dist/itembank.pyz dist/itembank-0.3.0.pyz` byte-identical; `sha256sum -c dist/SHA256SUMS.txt` all 5 OK; `python dist/itembank.pyz --version` → `itembank 0.3.0` exit 0 |
| 4-7. Strictly-newer/checksum, throttle, token host gate, first-launch disclosure | `tests/update_roundtrip.py` PASS (strictly-newer, checksum accept/reject/abstain, offline/rate-limit silence, consent gate, redirect-safe auth stripping, token host gate, fresh-install throttle, first-launch disclosure) |
| 8. Daemon window setting | `tests/launcher_roundtrip.py` PASS (app-mode argv, tab fallback, opt-out); live `itembank daemon <scratch> --port 8799 --no-open` bound `http://127.0.0.1:8799/`, printed URL, opened no browser, HTTP 200 on GET /; the `window=app`/`window=tab`/`open_browser=false` branches were already run live on Windows + Chrome (2026-08-10, `02.1-UAT.md` test 4) |
| 9-10. GIFT determinism + loud failure | `tests/gift_export_roundtrip.py` PASS; live: `itembank export fixtures/sample_bank.md out.gift --format gift` exported 5 items, skipped build Q4 by number (partial-export exit 1), `cmp` of two runs byte-identical; `--strict` promoted the multi divergence to a per-item failure (4 exported / 2 skipped); `fixtures/gift_build_only_bank.md` → 0 exported / 11 skipped, exit 1 |
| Update check live | `itembank update --check --timeout 15` printed the locked unreachable line (this environment cannot reach GitHub; the locked outcome line is what is asserted). The authenticated real-API run (v0.3.0 published, `itembank is up to date (v0.3.0).`) is recorded in `02.1-UAT.md` test 6 (2026-08-10) |

### CI-equivalent checks (scratch runner, 16/16 PASS)

Sample bank lints with 0 errors; broken bank caught with all 11 named
messages; sample builds; session/item/response/report/lint_error schemas all
validate via `schema_validate.py` over a real start→submit→report→evidence
session; `itembank.py guard .` passes (0 offending files); skill mirrors
`.agents/skills` vs `.claude/skills` identical.

### Full suite: 45 files, 41 PASS, 4 FAIL — all 4 explained

- `tests/evidence_roundtrip.py` — `FAIL: index was not rebuilt at version 3
  after the stale check`. Phase 10-03-era test, **pre-existing on main tip**
  (reproduced twice; present on unmodified `2b5678c`). Not a 02.1 file.
- `tests/gate_roundtrip.py` — `FAIL: rows must differ only by context in log
  order, got [None, None]`. Phase 06.2-era test, **pre-existing on main tip**
  (same analysis). Not a 02.1 file.
- `tests/phase_062_audit.py` — cascades: asserts the full suite is green.
- `tests/packaging_roundtrip.py` — 17/18 PASS; the sole failure is
  `test_onedir_sidecar_runs_and_is_sized` (DEL-11, phase 13), which requires
  `dist/itembank-sidecar-onedir`, the Windows PyInstaller freeze built by
  `powershell -File scripts/build_shell.ps1` — impossible in this WSL/bash
  session (`powershell.exe` denied by the command gate). **No phase-02.1 truth
  depends on it.**

The two later-phase failures are flagged for the owning phase chats; this
close-out deliberately does not fix other phases' code.

## UAT status

`02.1-UAT.md` moved `diagnosed` → `complete`. Tests 4 (frameless window,
live Windows+Chrome) and 6 (real GitHub Releases API, v0.3.0 published) pass
with recorded live evidence; the three launcher blockers (G-02.1-1..3) are
resolved by the 2026-08-10 inline gap fix (stable `itembank.pyz` shipped,
byte-identical to the versioned artifact, regression test added); test 5 (real
LMS import) remains blocked on a third-party LMS being unavailable.

## What remains human (PENDING HUMAN — do not fabricate)

1. **Windows `.bat` on a no-Python machine** — double-click `itembank.bat`
   with no Python 3.11+ on PATH: console opens, shows the locked
   Python-3.11-or-newer sentence naming python.org, stays open until a key is
   pressed (no flash-close, no traceback).
2. **macOS Gatekeeper first run** — double-click `itembank.command` in Finder
   on a real Mac: it starts, or Gatekeeper blocks it and the README's
   right-click-then-Open workaround starts it on the second attempt.
3. **Linux `.desktop` double-click** — from a real GNOME/KDE/XFCE file
   manager: it starts, or the failure sentence is visible somewhere reasonable.
4. **Real LMS import of the GIFT output** — import `itembank export bank.md
   out.gift --format gift` into a real Moodle (or equivalent): all five
   expressible types import without error; a table/dnd item at the minimum row
   count is accepted as a matching question; a multi item whose correct-option
   count does not divide 100 evenly is accepted without a negative-total
   display (SC5 manual half; RESEARCH assumptions A1/A2 remain unverified —
   truth 11, the only truth excluded from the 10/11 score).

## How to review / merge

1. Check out `gsd/phase-02.1-close` (worktree `.phase021-wt`).
2. Diff the three phase docs against the phase dir on main — the
   VERIFICATION.md record (ported from `9da0da9` + reconciled with the live
   re-run), the UAT status flip, and this handoff.
3. Merge into main. ROADMAP/STATE/config.json are reconciled centrally by the
   orchestrator after all phase branches merge — do NOT touch them here.

## Files not committed (intentionally)

- `fake_hosted_unused.py` — untracked at the repo root, belongs to concurrent
  work (not this phase); left out of every commit.
- `dist/` artifacts, `.scratch-*` files, and the verification scratch runner —
  all scratch, removed before commit.
