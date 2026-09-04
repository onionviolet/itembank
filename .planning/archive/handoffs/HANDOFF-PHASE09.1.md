# Phase 09.1 Handoff — Audio Drill Export (COMPLETE)

**Branch:** `gsd/phase-09.1-audio-export`
**Worktree:** `C:\Users\wayba\Downloads\CTF\itembank\.phase091-wt`
**Status:** EXECUTED — 4/4 plans, verification passed, UAT 5/7 automated + 2 deferred
**Date:** 2026-08-11

## What shipped

An objective now leaves itembank as an **audio drill pack** — stem, timed
pause, key, why — plus a plain-text transcript, via `itembank export audio
--objective <id>`, with a swappable TTS engine behind one interface:

| Plan | Deliverable | Commit |
|------|-------------|--------|
| 09.1-01 | TTSEngine interface + registry (model-backend shape), transcript-only engine, objective resolution, sequence builder, CLI surface, audio settings block, 11 fixtures | `31fd5cc` (feat), `a27a47e` (docs) |
| 09.1-02 | edge-tts (network, MP3-native, LGPL-3.0 pin + D-16 help disclosure) and piper (local, WAV + engine-scoped lameenc MP3, bundled-binary sidecar decision), roster contract, requirements pins | `c8882e3` (feat), `bdf30e1` (docs) |
| 09.1-03 | assemble_pack one-writer (per-pack/per-item split, timed silence, container policy, digest-stable atomic writes) + POST /api/export_audio daemon route | `2685a18` (feat), `5d0e019` (docs) |
| 09.1-04 | verification fixtures (transcript-diff, no-evidence success+failure, surface inventory, failure-path contract) + 09.1-VALIDATION.md audits + 09.1-VERIFICATION.md + 09.1-UAT.md | `252a65b` (test), `1e60c49` (docs) |

**Key files:** `surfaces/audio.py`, `surfaces/audio_edge_tts.py`,
`surfaces/audio_piper.py`, `surfaces/cli.py`, `surfaces/daemon.py`,
`schemas/settings.schema.json`, `itembank.json`, `requirements.txt`,
`tests/audio_export_roundtrip.py`, `tests/daemon_roundtrip.py`.

## Verification result

- **7/7 observable truths** verified by fixtures (interface/registry, roster,
  sequence+pauses, no-silent-fallback+atomicity, both surfaces, containers/
  splits/transcript/digest, no-evidence+supply-chain+disclosure).
- **10/10 required artifacts** exist and are substantive.
- **7/7 AUDIO requirements** satisfied and marked complete in
  `.planning/REQUIREMENTS.md`; **16/16 decisions (D-01..D-16)** covered in
  `09.1-VALIDATION.md`.
- Full suite green except two **pre-existing environment gaps** (not
  regressions):
  - `tests/model_surface_roundtrip.py` — needs `surfaces.session.
    do_rubric_review`, the Phase 08-04 *feature* commit, which exists only as
    uncommitted work in the main tree (concurrent Phase 08 chat). This
    worktree's HEAD `5aab199` is the 08-04 test-only commit. Passes once
    08-04's feat lands.
  - `tests/packaging_roundtrip.py` — needs `dist/itembank-sidecar-onedir`
    produced by `powershell -File scripts/build_shell.ps1` (PyInstaller),
    not run in this worktree.

## Usage

```bash
# zero-dependency path (transcript-only engine)
python itembank.py export audio bank.md --objective "Water / chemistry" \
    --engine transcript-only --out pack/

# network engine (needs: pip install edge-tts==7.2.8)
python itembank.py export audio bank.md --objective "Water / chemistry" \
    --engine edge-tts --out pack/

# local engine (needs: bundled piper binary + an MIT voice model)
python itembank.py export audio bank.md --objective "Water / chemistry" \
    --engine piper --container wav --split per-item --out pack/
```

Every export writes the transcript always; a missing/unreachable engine
refuses by name and exits non-zero with the transcript intact. Files are
named `<objective-slug>-<sha256-short>` so unchanged re-exports are
idempotent. Nothing touches the evidence store.

## Decisions the next session should know

1. **edge-tts 7.2.8 is LGPL-3.0** (MIT only for srt_composer.py) — research
   A2's "GPL reported" resolved at vendoring time; recorded in
   requirements.txt.
2. **The wheel-bearing piper-tts (1.3.0+) is GPL-3.0-or-later** (the
   OHF-Voice/piper1-gpl fork) and is **NOT imported**. Piper ships as a
   **bundled binary + MIT voice model** driven via subprocess (Phase 13
   sidecar pattern) — the recorded A3 decision. The `piper` engine refuses by
   name when its model file is absent.
3. **edge-tts cannot synthesize MP3 silence** (no local encoder): its
   `silence()` raises a named refusal; the local engines (piper/
   transcript-only) are the pause-capable alternatives. The pause is never
   silently dropped.
4. **`export_audio(...)` is the ONE runtime call** both the CLI and the
   daemon route reach (D-08); `assemble_pack` is the ONE writer (D-10).
5. **`--split per-item` names files** from the item index + that item's
   spoken text digest, so identical items never collide and a changed item
   never overwrites.

## UAT / manual items deferred to the user

- A real edge-tts pack sounds right (voice + pause feel) — install
  `edge-tts==7.2.8` and listen.
- A real Piper pack is truly offline — install the bundled binary + an MIT
  model and run with the network disconnected.

Both are documented in `09.1-UAT.md` with exact commands.

## Files updated for close-out

- `.planning/ROADMAP.md` — 09.1 success criteria ✅ + plan boxes [x]
- `.planning/REQUIREMENTS.md` — AUDIO-01..07 marked complete (checklist +
  status table)
- `.planning/STATE.md` — current position → 09.1 COMPLETE, progress counters
  (completed_phases 10, completed_plans 67), decisions + metrics + session
  continuity
- `.planning/config.json` — **no change**: it carries no per-phase state
  (verified against git history; phase transitions live in STATE.md, which
  was updated)

## Not done (by design / out of scope)

- **No merge, no push** — branch `gsd/phase-09.1-audio-export` is local to
  the worktree, per the run directive.
- Kokoro engine (7900 XTX) — documented registration target only (D-02).
- Player, sync, mobile, playback position — refused by D-14; verified
  structurally.
- No evidence write of any kind — verified byte-identical (D-13).

## Next steps for the integrator

1. Let Phase 08's `feat(08-04)` land, then re-run `tests/
   model_surface_roundtrip.py` in this worktree (or after merge).
2. Run `powershell -File scripts/build_shell.ps1` then re-run
   `tests/packaging_roundtrip.py`.
3. Merge `gsd/phase-09.1-audio-export` when the concurrent 05/08/10 branches
   are ready; STATE.md/REQUIREMENTS.md/ROADMAP.md may need a conflict pass
   (each chat updated its own copy).
