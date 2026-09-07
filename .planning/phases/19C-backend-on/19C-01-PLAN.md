---
phase: 19C-backend-on
plan: 01
type: execute
files:
  - itembank.json
  - tests/model_adapter_roundtrip.py
  - tests/local_harness_roundtrip.py
  - .planning/phases/19C-backend-on/19C-01-PLAN.md
  - .planning/phases/19C-backend-on/19C-CONTEXT.md
  - .planning/phases/19C-backend-on/19C-VERIFICATION.md
  - .planning/phases/19C-backend-on/19C-01-SUMMARY.md
---

# 19C-01: activate and inspect the local backend

## Objective

Turn on the already shipped local model profile and retain one inspected run
through each of the Phase 19C paths against real material, without accepting
diagnostic output or repairing defects owned by another phase.

## Tasks

1. Change only the active profile and its unavailable model name in
   `itembank.json`. Update the two shipped-default assertions that intentionally
   pinned the disabled Phase 17A state. Confirm the settings schema and endpoint
   accept the profile.
2. Build a disposable diagnostic copy from the real EMT course. Run the
   director recommendation and recommendation pass with `recommend-only`
   authority. Retain their complete terminal records.
3. Run the public seeding entry point on the copied real bank without accepting
   a draft. Retain its complete terminal record.
4. Inspect all records. Write `19C-VERIFICATION.md` with observed output,
   defects, exact owners, hashes, fallback, and recovery. Do not copy real bank
   content into the repository.
5. Run `tests/model_adapter_roundtrip.py`, `tests/director_roundtrip.py`,
   `tests/seeding_roundtrip.py`, `itembank guard .`, and the required preflight.

## Acceptance gate

- `model_backend.active` resolves to an installed local model.
- All three named paths were actually invoked on a disposable copy of real
  material, and every transcript was inspected and retained verbatim.
- Each defect is routed rather than repaired opportunistically.
- No diagnostic candidate is accepted and the canonical EMT course keeps its
  pre-run fingerprints.
- Targeted tests, guard, and preflight pass at the plan revision.

## Failure condition

The plan fails if any path is skipped, any output is accepted, real material is
copied into the repository, an inherited Phase 19A file is changed, or a red
deterministic gate is reported as green.

## Commit

After every gate passes, stage only the seven owned repository paths listed in
the front matter and commit once with `feat(19C-01): activate and inspect local backend`.
