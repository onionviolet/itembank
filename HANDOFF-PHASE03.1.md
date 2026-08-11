# Continue / Close Phase 03.1 — handoff prompt (for a fresh chat)

Paste the whole block below into a new chat:

---

Continue the Phase 03.1 closure in this repo (`C:\Users\wayba\Downloads\CTF\itembank`).
You are taking over from a previous chat. Read this entire message first.

## Where the work stands

- **Phase 03.1 (Lesson Rich Blocks, Glossary & Style) is CLOSED on branch
  `gsd/phase-03.1-finish`** in the worktree at
  `C:\Users\wayba\Downloads\CTF\itembank\.phase031-wt` (bash:
  `/mnt/c/Users/wayba/Downloads/CTF/itembank/.phase031-wt`).
- All seven plans are complete with SUMMARYs (`03.1-01..07-SUMMARY.md`),
  `03.1-VERIFICATION.md` (status `human_needed`, 7/7 truths statically
  verified) and `03.1-UAT.md` (6 static pass / 1 live-run blocked).
  `03.1-GATES.md` maps the eight UI-SPEC section-17 gates to fixtures.
- **The implementation for plans 05-07 was already in the tree** (committed
  earlier in the phase-03.1 baseline working-tree commit `0b243c8` and
  follow-ups `dc9c64c`, `8c363d2`) — this run closed the plans with docs and
  verification. Branch commits (in order):
  - `42a13c9` docs(03.1-05): complete style lint enforcement plan
  - `cb8cf9d` docs(03.1-06): complete vendored fonts, spec, and lesson_layout fold plan
  - `5572bb3` docs(03.1-07): complete verification plan - eight gates, audit, suite
  - `4505d92` docs(03.1): phase verification + UAT - lesson rich blocks, glossary, style
- `STATE.md` updated (completed_phases 9→10, completed_plans 63→66, branch
  note, decisions log rows for 03.1-05/06/07, Deferred Verification row for
  03.1). `.planning/config.json` carries **no per-phase state** (verified) —
  nothing to update there.

## What REMAINS (do not claim done)

1. **Live automated suite + schema validation in a python-capable
   environment** (this session's approval gate declined every python
   invocation — precedent `03.2-05-SUMMARY.md`):
   - `for f in tests/*_roundtrip.py; do python "$f" || exit 1; done`
   - `python schema_validate.py --all`
   - `python tests/phase_031_audit.py` (expect "phase 03.1 requirement audit: 11/11 covered, ok")
   - `python tests/lesson_roundtrip.py` and `python tests/style_roundtrip.py`
     specifically — fixture presence was verified statically (15/15
     GATES-claimed fixtures re-grepped), but no green claim is made.
2. **Human-verify items** (recorded in 03.1-GATES.md + 03.1-UAT.md):
   - True cross-browser Popover/Anchor-Positioning behavior (Escape, focus
     return, top-layer, 320px) + daemon-stopped degraded copy.
   - ClearType 18px render of Source Serif 4 + iA Writer Quattro at 375px
     and 1280px (fonts/REGISTRY-SAFETY.md precondition 4).
   - 1280/768/375px viewport snapshots of the reader with reader_nav and
     example_layout in both values.
3. **Merge decision (yours/the user's):** the branch is intentionally NOT
   merged or pushed. `main` has moved since this branch's base (`5aab199` —
   phases 05/08/10 are active there). When merging, re-merge latest `main`
   into `gsd/phase-03.1-finish` first (expect conflicts in `STATE.md` /
   `.planning` docs and possibly `model.py`/`surfaces/cli.py` if phase 05/08
   touched them), resolve, then merge back.

## Mandatory rules

1. **One atomic commit per plan** — stage by explicit path, never
   `git add -A`.
2. **One parser, one scorer, one evidence writer** — the phase's own
   contracts (closed `LINT_CODES`, `runtime.py` only scorer, evidence via
   `evidence.append_event` only).
3. **Never fabricate verification.** If a command cannot run, record the
   block (precedent 03.2-05-SUMMARY) — do not flip statuses to pass.
4. **Human-gated items stay human-gated** — ClearType, browser popover,
   snapshots, and any real-corpus calibration run.

## First actions on start

1. `git -C .phase031-wt log --oneline -6` and `git worktree list` — confirm
   branch + worktree exist (recreate: `git worktree add -b gsd/phase-03.1-finish
   C:/Users/wayba/Downloads/CTF/itembank/.phase031-wt` — note the branch may
   already exist, then use `git worktree add .phase031-wt gsd/phase-03.1-finish`).
2. In a python-capable shell, run the suite items listed under "What REMAINS"
   and record results into `03.1-GATES.md` + `03.1-VERIFICATION.md`
   (flip the blocked rows to green only with real receipts).
3. Then decide the merge with the user.
