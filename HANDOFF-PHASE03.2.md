# HANDOFF — Phase 03.2: Seeding, Import & Provenance

**Branch:** `gsd/phase-03.2-close` (worktree `.phase032-wt`)
**Status:** CLOSED — 5/5 plans executed on main (`f799c05`, `dc9c64c`,
`b8fed76`, `07e6596`, `b301f0e`); close-out docs committed on this branch;
not merged, not pushed.
**Date:** 2026-08-11

## What shipped (executed on main)

1. **feat(03.2-01) `f799c05`** — the Anki `.apkg` importer
   (`surfaces/import_anki.py` + `itembank import anki`): ZIP container
   reader with zstd decode through one pinned, checksummed, license-reviewed
   `zstandard` binding (legacy SQLite members dependency-free), note-type map
   with loud per-note refusal, the `model.lint()` gate every candidate must
   pass, an exhaustive per-note report (converted/skipped/refused + the total
   line, zero silent drops), and a CLI that stages + reports and never writes
   a bank directly (D-03/04/05/06, SEED-01/09).
2. **feat(03.2-02) `dc9c64c`** — provenance: the additive `## SOURCES`
   registry, `[SRC:]`/`[OBJ:]` resolution with unresolvable-id lint errors
   naming id + file (`prov.src_unknown`/`prov.obj_unknown`/
   `prov.src_duplicate`), the on-demand objective coverage map that is never
   stored, and the byte-identity compatibility floor (D-11/12/20,
   SEED-04/08/09).
3. **feat(03.2-03) `b8fed76`** — the six-stage seeding loop
   (`surfaces/seeding.py`): draft → lint → retry → explicit human accept,
   one item at a time, nothing writes without an accept, cancelled runs write
   nothing; one accept endpoint (`seeding.accept_candidate`) shared by the
   CLI command and the daemon route behind the loopback authority gate; the
   batch-framed UI and the no-backend degrade contract (D-06/07/09/10,
   SEED-02/03).
4. **feat(03.2-04) `07e6596`** — paraphrase lint via stdlib winnowing over
   fingerprints only (≥8 consecutive copied words errors
   `prov.paraphrase_copy`, Jaccard > 0.25 warns `prov.paraphrase_overlap`,
   both thresholds settings, source text never stored), the structural
   `style.unsourced_specific` warning, the `[CASE:]`/`[PREREQ:]` grammar with
   cycle + unresolvable-target lint (`prov.case_unknown`/
   `prov.prereq_unknown`/`prov.prereq_cycle`), all wired into the seeding
   stage-4 deterministic gate (D-13/14/15/16, SEED-05/06).
5. **feat(03.2-05) `b301f0e`** — the extended corpus-residency guard
   (refuses corpus-shaped content outside fixtures/; `.planning` and `_tmp*`
   added to the repo-owned skip list), the style-warning calibration command
   + `03.2-CALIBRATION.md` (synthetic corpus: `sentence_length` 0.50
   disabled, `require_marker` 1.00 disabled, `unsourced_specific` 0.00
   enabled, all 11 codes recorded), the SEED-01..09 9/9 requirement audit,
   and the D-19 item/prose write-separation fixture (D-17/18/19, SEED-07).

## Close-out verification (this branch, run live 2026-08-11)

All in the `.phase032-wt` worktree (WSL python 3.13.3):

- `python tests/import_roundtrip.py` — **20/20 PASS** (incl. guard-refusal,
  calibration, `seed coverage: 9/9 SEED ids`)
- `python tests/seeding_roundtrip.py` — **24/24 PASS** (incl. D-19
  separation)
- `python tests/lesson_roundtrip.py` — **ok** (provenance grammar +
  compatibility floor)
- `python tests/config_roundtrip.py` — **ok** (paraphrase threshold settings)
- `python tests/daemon_roundtrip.py` — **ok** (69 checks)
- `python tests/protocol_roundtrip.py` — **ok** (83 lint codes, runtime
  output validated against schemas/)
- `python itembank.py lint fixtures/sample_bank.md` — **0 errors**
  (6 advisory warnings)
- `python itembank.py guard .` — **0 offending files**
- Full suite (45 files, subprocess driver): **41 PASS / 4 FAIL** — every
  03.2 file green; the 4 failures are provably **not** 03.2 regressions:

| File | Failure | Attribution |
|---|---|---|
| `packaging_roundtrip.py` | `dist/itembank-sidecar-onedir is missing` | Environmental, pre-existing (run `scripts/build_shell.ps1`); already attributed in 03.2-GATES.md |
| `evidence_roundtrip.py` | `index was not rebuilt at version 3 after the stale check` | Post-03.2: the "expects 3" assertion came from `376dae4` (06.2-01); HEAD `evidence.py` has `INDEX_VERSION = 2` restored by `5b7f397` (08-06). 03.2 never touches `evidence.py` |
| `gate_roundtrip.py` | `rows must differ only by context in log order, got [None, None]` | Post-03.2: the file is 06.2's own test (`698f5df test(06.2-04)`); assertion from `376dae4` |
| `phase_062_audit.py` | re-runs the full suite internally | Cascade from the three above (its own 6/6 audit + schema checks pass) |

## Docs created/updated (this branch)

- `03.2-VALIDATION.md` — `status: draft` → `validated`; the 14-task
  per-task verification matrix filled (plan/wave/requirement/threat/command/
  status), Wave 0 completed, sign-off approved.
- `03.2-VERIFICATION.md` — 9/9 observable truths VERIFIED live; user-flow
  coverage table; deferred items; full-suite attribution.
- `03.2-UAT.md` — created (did not exist); 9/9 UAT items passed live.
- `HANDOFF-PHASE03.2.md` — this file.

## Requirement status

SEED-01..SEED-09 all DELIVERED (REQUIREMENTS.md rows remain `Pending` — the
orchestrator reconciles REQUIREMENTS.md/ROADMAP.md/STATE.md centrally after
all phase branches merge; do not edit them here).

## Human-verify items (recorded, not claimed verified)

1. **Real-corpus calibration (SEED-07 / D-18)** — the private EMT/Math/CS
   corpus lives beside the private bank, outside the repo by design. On that
   machine: `python itembank.py calibrate <corpus-dir> --out <report>` and
   record the per-warning FP rates + ship-state in `03.2-CALIBRATION.md`.
   Synthetic-corpus measurement is automated and green.
2. **Suite green at HEAD** — `evidence_roundtrip.py` and `gate_roundtrip.py`
   need the 06.2/08-06 evidence-index version mismatch reconciled (either
   bump `INDEX_VERSION` back to 3 or fix the 06.2-era assertions), and the
   packaging onedir must be built for `packaging_roundtrip.py`. All are
   owned by later phases, not 03.2.

## For the next phase

- Phases 6/7 consume `[CASE:]`/`[PREREQ:]` edges; `prov.*` lint codes and the
  `## CASES` registry are the contract (`model.parse_cases`).
- The seeding accept endpoint (`seeding.accept_candidate`) is the one write
  path into a bank; any future surface must call it, never write directly.
- `itembank import anki` is a staging-only command; there is deliberately no
  direct bank write in `surfaces/import_anki.py` (test-asserted).
- The guard's skip list now includes `.planning` and `_tmp*` alongside the
  repo-owned playbook dirs; a future phase that starts a real private corpus
  dir in the tree must add it to the skip list or the guard will refuse it.

**Merge note:** branch `gsd/phase-03.2-close` carries only the close-out docs
and is ready to merge to main once the orchestrator reconciles the central
files (ROADMAP.md / STATE.md / config.json / REQUIREMENTS.md stay untouched
on this branch).
