---
phase: 07-selection-engine
goal: "A session is assembled by rule, not by hand - targeted at an objective, a difficulty, or a discrimination pair - and the tool can say why it picked each item."
requirement_ids: SEL-01, SEL-02, SEL-03, SEL-04, SEL-05
status: gaps_found
verified: 2026-08-10
score: "5/5 binding requirements; 6/11 roadmap criteria verified (1-5 plus 9 partial)"
method: inline verification (subagent dispatch unreliable in this runtime per AGENTS.md)
---

# Phase 7 Verification - Selection Engine

## Scope note

The phase's binding requirements are SEL-01..SEL-05, all marked **Complete** in
`REQUIREMENTS.md`. ROADMAP adds research-derived success criteria 6-11 that
postdate the 2026-08-08 plans; the phase's own UI-SPEC audit (note 2) records
that plans 07-01..07-06 do not cover criteria 7-11 and that "a replan is owed
before execution". The plans executed without that replan. This report verifies
every roadmap criterion and records the uncovered ones as gaps rather than
silently dropping them.

## Goal check

### 1. Filter by objective, prerequisite, item type, and difficulty - PASS

`selection.filter_by_spec()` applies all four filters (objective, prereq,
item type, difficulty); the CLI exposes them as `--objective`,
`--prerequisite`, `--type`, `--difficulty`, plus `--prereq-satisfied`.
Tests: `check_objective_filter` (7/7 on water:regulatory.reporting) and
`check_prereq_filter` (9/9 build on water:distribution.residual). Type and
difficulty ride the same code path (CLI surface, `order_difficulty_asc/desc`
and `order_balanced` unit-covered).

### 2. Four selection modes produce visibly different sessions - PASS

The `MODES` registry gives diagnostic/practice/remediation/exam distinct
filter, order, and exposure compositions.
`check_mode_compositions_differ` passes: four modes differ, each per its
purpose.

### 3. Cooldown: no accidental repeats, across a resumed session - PASS

`check_cooldown_survives_resume` passes (exclusion survives the deleted
session file; exam ignores it) and `check_cooldown_is_bank_scoped` passes
(other-bank activity never starves the selection bank). Cooldown is
bank-scoped by design (D-13, `INDEX_VERSION` 2 with a `bank` column).

### 4. Discrimination pairs serve together - PASS

`[PAIR:]` + `filter_by_pair()`; `check_pair_served_together` passes (both
sets served whole and adjacent), and `select()` raises the count to hold the
whole pair.

### 5. The tool can say why it picked each item - PASS

Live run (`itembank select fixtures/selection_bank.md --objective
water:regulatory.reporting --count 3 --explain`):

```text
Selection: practice
Evidence: C:\Users\wayba\Downloads\CTF\itembank\fixtures\_evidence\evidence.jsonl (0 response(s), index)

- c1c714fb8df4438a (Q28): chosen because it is on objective 'water:regulatory.reporting', the practice composition ordered it; the runner-up q24 it fell outside the requested count of 3
    runner-up: 6af6d381f5424720 (Q24) -- it fell outside the requested count of 3
```

`check_trace_names_runner_up` (3 blocks name a distinct runner-up),
`check_explain_renders_plain_text` (prose, no key, no option text), and
`check_trace_leaks_no_key` all pass.

### 6. Guided path (prerequisite sequencing + application checkpoints) - NOT VERIFIED

No plan or code evidence exists for a guided-path sequencer; no later phase
claims it in the roadmap. Open gap.

### 7. ALEKS fringe (mastery-gated prerequisites, recorded override) - NOT VERIFIED

Designed in 07-UI-SPEC (override trace line, `prerequisite-fringe` strategy
label) but absent from the executed plans and from `selection.py` (no
fringe/override code). `[PREREQ:]` edges are authorable (Phase 3.2, complete)
but mastery-gating plus the recorded override is not implemented. Open gap.

### 8. Blueprint-weighted ordering + [CASE:] group serving - NOT VERIFIED

07-UI-SPEC notes 3-4 flag the trace shape ("one block for the group") and the
weight-input wording as owed decisions at replan; no serving behavior exists
in code. Open gap.

### 9. Named, registrable strategies behind one interface - PARTIAL

The `MODES` registry is one interface (filter/order/exposure per mode, reached
only through `selection.select()`), and the trace names the human label
("the practice composition ordered it"). The per-selection
`selection.strategy` spec field was declined per 07-UI-SPEC note 1; the trace
still names the strategy the mode selected, so the criterion is satisfied in
spirit. Note recorded.

### 10. Corpus reach (selection-side measure) - NOT VERIFIED

07-UI-SPEC E6 says "computed in 7, rendered in 10", but no reach computation
exists in `selection.py` or the tests. Open gap.

### 11. Pending-mark selection invariant - NOT VERIFIED

No pending-mark handling in the selection code. The criterion says this "must
be asserted here rather than assumed from Phase 8". Open gap.

## Requirement audit

| Req | Status | Evidence |
|-----|--------|----------|
| SEL-01 | Complete | `filter_by_spec` + objective/prereq tests; type/difficulty CLI |
| SEL-02 | Complete | `MODES` registry; `check_mode_compositions_differ` |
| SEL-03 | Complete | `check_cooldown_survives_resume`; bank-scoped index |
| SEL-04 | Complete | `[PAIR:]`; `check_pair_served_together` |
| SEL-05 | Complete | `--explain` live sample; trace tests |

## Behavioral evidence

- `python tests/selection_roundtrip.py` - all 18 checks green (filters,
  determinism, trace runner-up, no key leak, pair adjacency, prereq lint,
  mode recording, cooldown across resume, bank scoping, explain plain-text,
  preview writes nothing, profile flag override).
- `schemas/selection.schema.json` ships as the sixth published contract;
  `itembank select --explain` + `/api/start` preview reach the same
  `do_select` call; preview appends no evidence (surfaces/session.py:155).
- `selection` settings group + `selection.profiles` present in
  `schemas/settings.schema.json`; `INDEX_VERSION = 2` (evidence.py:750).

## Gaps (actionable)

| # | Criterion | Missing | Recommended home |
|---|-----------|---------|------------------|
| 6 | Guided path | Sequencer + checkpoints | Phase 11 (curriculum loop) or 07.1 |
| 7 | Fringe mastery-gate + override | Gating logic, override event/readout | 07.1 (UI-SPEC already designed) |
| 8 | Blueprint weights + [CASE:] unit | Weight input, group-serving | 07.1 or Phase 10 |
| 10 | Corpus reach | Reach computation | 07.1 (UI-SPEC E6 ready); render in 10 |
| 11 | Pending-mark invariant | Assertion that selection reads accepted evidence only | 07.1 now (short answers are already pending) |

## Human verification

- **SEL-05 legibility (E1 backstop):** the `--explain` sample above reads as
  plain English to a human. Automated tests prove the five-line grammar; the
  perceptual read is the manual item.
- **/api/start preview and settings group:** automated evidence covers
  behavior; a browser eyeball of the preview is optional, not gating.

## Recommendation

Close the phase for its binding scope (SEL-01..05 verified), but do not mark
it Complete until the five roadmap criteria above are either implemented in a
small 07.1 wave or explicitly re-homed. The cheap closes are #10 (reach
computation) and #11 (a pending-mark assertion using existing `short` items);
#7 is designed and depends only on Phase 3.2 evidence; #6 and #8 are the
design-heavy ones.
