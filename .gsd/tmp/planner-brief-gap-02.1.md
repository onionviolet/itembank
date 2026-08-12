# Gap Closure Planner Brief — Phase 02.1 (packaging-self-update-interop-export)

You are planning the closure of three UAT blocker gaps found in Phase 02.1.
Read these files first:

- `C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/02.1-packaging-self-update-interop-export/02.1-UAT.md` (the UAT with full diagnoses in `## Gaps`)
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/STATE.md` (project state)
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/ROADMAP.md` (roadmap, phase 02.1 section)

Also read the affected source so the plan is concrete:

- `launchers/itembank.bat`
- `launchers/itembank.command`
- `launchers/itembank.desktop`
- `build.py`
- `tests/packaging_roundtrip.py`
- `surfaces/day.py` line 786 (minor SyntaxWarning finding)

## Gaps to close (UAT tests 1, 2, 3 — one root cause)

1. `G-02.1-1` — `itembank.bat` starts the app when Python 3.11+ is present. FAILS: the shim runs
   `py -3 "%~dp0itembank.pyz"` but the release directory contains only `itembank-0.3.0.pyz`
   (`build.py` emits `itembank-<version>.pyz`; the updater's `_ASSET_RE` requires the versioned name).
   Reproduced live on Windows: exit 2, "can't open file ... itembank.pyz".
2. `G-02.1-2` — `itembank.command` starts the app on macOS. Same hardcoded `itembank.pyz` reference
   (`exec python3 itembank.pyz "$@"`); statically broken the same way.
3. `G-02.1-3` — `itembank.desktop` starts the app on Linux. Same hardcoded `itembank.pyz` reference
   (`exec python3 itembank.pyz`); statically broken the same way.

Root cause: all three launcher shims hardcode the stable name `itembank.pyz`, but the release only
contains the versioned artifact. `tests/packaging_roundtrip.py` verifies launchers ship and carry the
locked failure sentence but never launches through a shim, so the mismatch shipped.

## Required plan content

Produce an executable `*-PLAN.md` (suggest `02.1-10-PLAN.md`) with frontmatter:

```yaml
---
gap_closure: true
gap_ids: [G-02.1-1, G-02.1-2, G-02.1-3]
---
```

The plan MUST:

1. Fix all three launchers to resolve the versioned artifact (`itembank-*.pyz`) at runtime — do NOT
   hardcode a version number. Keep the locked failure sentence, the pause/read on failure, and the
   interpreter probes (`py -3` on Windows, `python3` on macOS/Linux) byte-identical.
2. Add a packaging test asserting that the artifact each shim resolves exists in the built release
   directory (so the mismatch can never ship again). Prefer extending `tests/packaging_roundtrip.py`.
3. Optionally fix the `SyntaxWarning: invalid escape sequence '\.'` at `surfaces/day.py:786` if it is a
   one-line, zero-risk change (it is a minor finding, not a gap).
4. Rebuild `dist/` with `python build.py` and re-run `python tests/packaging_roundtrip.py` plus the
   full `python tests/*.py` suite as verification steps.
5. Constraints: do NOT bump `itembank.__version__` (0.3.0 stays). The `.pyz` itself is fine. Release
   asset replacement on the existing GitHub v0.3.0 release happens AFTER execution and is NOT part of
   this plan's code edits — but the plan must end with a "verify the corrected launchers launch"
   step (Windows `.bat` happy path at minimum, static checks for `.command`/`.desktop`).

## Deliverable

Write the completed PLAN.md into the phase directory. Reply with `## PLANNING COMPLETE` and the plan
filename(s). Keep the plan tight — this is a small, fully-diagnosed fix, not a re-plan of the phase.
