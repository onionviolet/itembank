# Handoff — Phase 07 (Selection Engine) closed

- **Created:** 2026-08-11
- **Phase:** 07 — selection-engine
- **Status:** CLOSED for binding scope (SEL-01..05); five roadmap criteria beyond the binding scope tracked as gaps (see §3)
- **Handing off to:** the next phase executor (Phase 08 is already executing) and any future 07.1 wave that picks up the gaps

---

## 1. What phase 07 delivered

A session is assembled by rule, not by hand, and the tool can say why it picked each item.

- `selection.filter_by_spec()` — filter by objective, prerequisite, item type, and difficulty; the CLI exposes
  `--objective`, `--prerequisite`, `--type`, `--difficulty`, `--prereq-satisfied`.
- `MODES` registry — diagnostic / practice / remediation / exam, each a distinct composition of
  filter, order, and exposure rules; reached only through `selection.select()`.
- Cooldown — recent exposure is bank-scoped (`INDEX_VERSION` 2, `bank` column), survives a deleted session
  file, and exam mode ignores it.
- `[PAIR:]` discrimination pairs — served whole and adjacent; `select()` raises the count to hold the pair.
- `--explain` — a plain-English trace per item naming the reason and a distinct runner-up, with no key,
  rationale, or option text leakage.
- `schemas/selection.schema.json` ships as the sixth published contract; `/api/start` preview reaches the
  same `do_select` call and appends no evidence.

## 2. Verification & UAT

- `python tests/selection_roundtrip.py` — **18/18 checks green** (re-run 2026-08-11): objective filter
  7/7, prereq filter 9/9, determinism, trace runner-up, no key leak, pair adjacency, prereq lint,
  mode recording, cooldown across resume, bank scoping, explain plain-text, preview writes nothing,
  profile flag override.
- UAT: **3/4 pass** (preview writes no session; mode compositions differ; selection settings + profiles).
  **1 needs-review** — explain legibility is the manual E1 backstop; automated grammar checks pass and the
  sample output is in `07-VERIFICATION.md` (criterion 5) for a human eyeball.
- Requirements: SEL-01..05 all marked **Complete** in REQUIREMENTS.md (checkbox + table).

## 3. Open gaps (roadmap criteria beyond the binding scope)

Recorded in `07-VERIFICATION.md` with recommended homes — **do not silently drop them**:

| # | Criterion | Missing | Recommended home |
|---|-----------|---------|------------------|
| 6 | Guided path (prerequisite sequencing + application checkpoints) | Sequencer + checkpoints | Phase 11 or a 07.1 wave |
| 7 | ALEKS fringe (mastery-gated prerequisites, recorded override) | Gating logic, override event/readout | 07.1 (07-UI-SPEC already designed) |
| 8 | Blueprint-weighted ordering + `[CASE:]` group serving | Weight input, group-serving | 07.1 or Phase 10 |
| 10 | Corpus reach (selection-side measure) | Reach computation | 07.1 (07-UI-SPEC E6 ready); render in 10 |
| 11 | Pending-mark selection invariant | Assertion that selection reads accepted evidence only | 07.1 now (short answers are already pending) |

The cheap closes are #10 and #11; #7 is designed and depends only on Phase 3.2 evidence; #6 and #8 are
the design-heavy ones.

## 4. State of the tree

- Committed in this close: `07-UAT.md`, `07-VERIFICATION.md`, ROADMAP.md (phase-7 checkbox + table row →
  Complete, dated), STATE.md (decision note + timestamp), and this file.
- `config.json` was **not** touched: it carries no phase-status field and held an uncommitted change from
  another active session.
- Phase 08 is executing in parallel (current_phase 08, 3/6 plans); do not conflate the 07 close with 08 state.

## 5. Next action

Nothing blocks. Resume `$gsd-autonomous` (or the active Phase 08 session) as normal; revisit §3 gaps when a
07.1 wave or Phases 10/11 are planned.
