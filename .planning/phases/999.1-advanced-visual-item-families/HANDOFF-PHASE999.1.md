# HANDOFF — Phase 999.1 (Advanced Visual Item Families)

**Branch:** `gsd/phase-999.1` (worktree `.phase9991-wt`, created from `main`
at `2b5678c`)
**Date:** 2026-08-11
**Status:** executed — 4 plans, 4 commits; verification and UAT above

## What shipped

Phase 06.1's visual protocol (plot + number line, protocol integer 1) was
extended **additively** with four advanced families — `hotspot`, `timeline`,
`diagram`, `trace` — through the same envelope, the same
`session.do_interact`/`/api/interact` commit path, the same
`evidence.visual_action` append-only trail, the same SVG-plus-semantic-control
renderer rule, and the same loud GIFT refusal. Protocol integer stays 1;
06.1 items are byte-compatible.

| Plan | Commit | Contents |
|---|---|---|
| 01 hotspot | `bc82d59` | per-interaction scene allowlists + strict scene builder, exact-id verdict/observation, `renderHotspot`, schemas, `fixtures/advanced_visual_bank.md`, `tests/hotspot_roundtrip.py`, lint codes (`item.visual_invalid_geometry`) |
| 02 timeline | `0aac5ad` | event placement + per-coordinate tolerance, `renderTimeline` + shared `vf*` fraction helpers, place/move actions, `tests/timeline_roundtrip.py` |
| 03 diagram + trace | `a7ca774` | ordered node connection, element-wise polyline trace with fixed count, `renderDiagram`/`renderTrace`, `tests/diagram_roundtrip.py` + `tests/trace_roundtrip.py` |
| 04 phase verification | (this commit) | VERIFICATION/UAT/HANDOFF/SUMMARY, full-suite run |

## Tests

- New: `tests/hotspot_roundtrip.py`, `tests/timeline_roundtrip.py`,
  `tests/diagram_roundtrip.py`, `tests/trace_roundtrip.py` — all PASS.
- 06.1 suites unchanged and green: `visual_roundtrip`,
  `visual_authoring_roundtrip`, `visual_evidence_roundtrip`,
  `visual_accessibility_roundtrip`, `gift_export_roundtrip`,
  `scoring_roundtrip` (one-scorer scan), plus `protocol_roundtrip`,
  `model_ui_roundtrip`, `lesson_roundtrip`.
- Full suite `tests/*.py` (run chunked, mirroring CI): all PASS except four
  **pre-existing/environmental** failures, none caused by this phase:
  `evidence_roundtrip.py` (sqlite index version), `gate_roundtrip.py`
  (evidence context rows), `packaging_roundtrip.py` (missing local
  `dist/itembank-sidecar-onedir` build artifact), `phase_062_audit.py`
  (aggregates those; runs > 2 min).
- `python itembank.py lint fixtures/sample_bank.md` → 0 errors.
  `python itembank.py lint fixtures/advanced_visual_bank.md` → 0 errors.
  `python itembank.py guard .` → 0 offending files.

## Files touched by this phase (all committed, none staged by others)

`runtime.py`, `model.py`, `surfaces/quiz_page.py`, `schemas/item.schema.json`,
`schemas/visual_interaction.schema.json`, `schemas/lint_error.schema.json`,
`fixtures/advanced_visual_bank.md`, `fixtures/visual_gift_bank.md`,
`tests/{hotspot,timeline,diagram,trace}_roundtrip.py`,
`tests/gift_export_roundtrip.py`, and the phase directory under
`.planning/phases/999.1-advanced-visual-item-families/`.

An unrelated untracked file `fake_hosted_unused.py` appeared in the worktree
during the phase (another concurrent chat's in-flight work) — it was left
untouched and unstaged.

## Named gaps (deferred, not silently dropped — see 999.1-RESEARCH.md)

1. **Geometry/construction** — needs a multi-step construction protocol
   (drawn-object history, undo/redo, step-scoped validation, a sequence
   response grammar). A design-review task, not a response-kind extension.
2. **Dense-simulation-style responses** — 06.1's canvas rule requires the
   identical semantic HTML state/control path; the candidate first slice is a
   deterministic parametric simulation (SCALAR parameter sliders, runtime
   readout, final parameter-set response). Design question remains: the
   readout-rule grammar.
3. **Diagram label/match variants** — assign labels to nodes,
   multi-connection lists.
4. **Trace extensions** — free-length tracing, multi-segment matching
   (current scope: one ordered polyline with fixed `point_count`).

## For the orchestrator

- `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/config.json` were
  **not** touched by this phase (orchestrator-owned).
- The ROADMAP 999.1 entry's dependency line ("Phase 06.1 (0/3 plans, not
  executed)") is stale: 06.1 merged as `801ae8f` and is verified. The 999.1
  entry should be reconciled to executed status, with the phase's
  requirement mapping (VIS-01..VIS-09 now covered by four additional
  families) reflected in STATE/REQUIREMENTS as the orchestrator sees fit.
- This branch has NOT been merged into main and nothing was pushed; the
  orchestrator merges after all phase branches reconcile.
