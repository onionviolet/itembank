# 15B tracer report

Measured 2026-08-30 on **Darwin 27.0.0 arm64**, **Python 3.14.6**. Every figure
below was produced by the run this report describes. No budget, target, or
estimate appears anywhere in it: a number among measurements that was not
measured is a fabricated measurement.

## What was run

```
python3 tests/acceptance_tracer.py
```

Exit 0. Full output, verbatim:

```
scenario five_gate_acceptance: pass
scenario fidelity_claim_ordering: pass
scenario staleness_blocks: pass
scenario migration_accept_and_reject: pass
scenario sparse_evidence_proposal: pass
scenario course_audit: pass
scenario journal_replay: pass
measured on: Darwin arm64, Python 3.14.6
measured whole tracer: 31.947 s
measured agent_entries: 6
measured audit_rows: 4
measured audit_vocabularies: 2
measured blueprint_findings_blocked: 1
measured dispositions_cleared: 4
measured gate_arrays: 4
measured gates_passed: 5
measured journal_entries: 28
measured proposal_denominator: 2
measured proposal_uncertainty: sparse
measured settlements: 2
measured stale_rows: 1
TRACER: 7 passed, 0 skipped, 0 failed
```

`shipped_suite_check()` runs before any 15B module is imported. Six shipped
suites each exited 0 as subprocesses: `scoring_roundtrip`,
`evidence_roundtrip`, `audit_authoring_roundtrip`, `audit_quality_roundtrip`,
`audit_coverage_roundtrip`, and `audit_roundtrip`. All three of
`14A-FREEZE.md`, `14B-FREEZE.md` and `15A-FREEZE.md` carry their own
`## Frozen at` heading and none carries `## Freeze withheld`. A red shipped
suite, a missing freeze, or a WITHHELD one skips every scenario rather than
reporting passes: a freeze that was withheld is not a surface 15B may plan
against.

**Full suite**, run separately on the same machine: **100 test files, 0
failures**. `python3 itembank.py guard .` reports `0 offending files`.

## Requirement coverage

| Requirement | Scenario function | Result |
|---|---|---|
| ACTIVITY-02, the five gates | `scenario_five_gate_acceptance` | passed |
| ACTIVITY-02, the claim ordering | `scenario_fidelity_claim_ordering` | passed |
| RELIABILITY-03 | `scenario_staleness_blocks` | passed |
| RELIABILITY-03, the reviewer path | `scenario_migration_accept_and_reject` | passed |
| AGENT-03 | `scenario_sparse_evidence_proposal` | passed |
| ACTIVITY-02, the cited audit | `scenario_course_audit` | passed |
| RELIABILITY-02 as 15B extends it | `scenario_journal_replay` | passed |

Seven rows, all `passed`. No row is `skipped` and none is `weaker proof`.

Three notes on what `passed` means here, so the rows are not read as more than
they are:

- `scenario_staleness_blocks` recomputes the live fingerprint from the edited
  file's BYTES through `identity.object_fingerprint`, and asserts it equals
  what `edit_source` returned. It never reads a stored fingerprint back.
- `scenario_fidelity_claim_ordering` asserts the claim at each of the five
  points, not only at the end: it is False after gates 1, 2, 3 and 4 and True
  only after gate 5.
- `scenario_journal_replay` reads the journal in a FRESH subprocess that
  imports only `journal` and opens only the journal directory. Nothing the
  tracer process holds can contribute to the answer.

## Measured budgets

Every figure is a measurement from the run above, on **Darwin arm64, Python
3.14.6**, dated **2026-08-30**. Nothing here is asserted against.

| Figure | Measured value |
|---|---|
| Whole tracer, seven scenarios | **31.947 seconds** |
| Journal entries the run appended | **28** |
| `agent_operation` entries replayed from a fresh process | **6** |
| Gates passed on the conforming set | **5 of 5** |
| Gate arrays carried in the proposal | **4** (lint errors, lint warnings, quality findings, blueprint findings) |
| Blueprint findings on the deliberately blocked set | **1** |
| Staleness dispositions that cleared a block | **4 of 4**, `retain` included |
| Stale rows produced by the mid-flow edit | **1** |
| Migration settlements | **2** (one accepted, one rejected) |
| Course audit rows | **4** |
| Coverage vocabularies cited | **2** |
| Proposal denominator | **2** |
| Proposal uncertainty | **sparse** |

The proposal figures are the AGENT-03 fixture case exactly: two attempts on one
objective, a denominator of two, and a band rather than a number.

## Defects found and fixed

**Two, both in this phase's own fixture, both found by the shipped Phase 11
quality gate rather than by anything 15B wrote.**

1. **Every distractor rationale failed `quality.distractor_rationale`.** The
   shipped detector requires each distractor to say when it WOULD be correct,
   and the synthetic items said only why they were wrong. The detector was
   right and the fixture was below the authoring standard the repository
   already enforces; every rationale now carries a would-be-correct clause.
2. **A real answer leak in the second drafted item.** Its stem read "A Beacon
   scene has two hazards and one patient" and option B read "Two hazards and
   one patient", so the correct option was quoted verbatim in the stem with no
   distractor sharing the phrase. `quality.answer_leak` caught all three
   overlapping runs. The stem is rewritten to describe the scene without naming
   the answer.

Both are worth recording rather than quietly fixing, because they are evidence
about the gate rather than about the fixture: the tracer's conforming set was
written by the same agent that wrote the gate, and the two failures it did not
anticipate were caught by shipped code it did not write.

**No defect was found in `blueprint.py`, `graph.py`, `course.py` or
`director.py` by this tracer.** One was found earlier in the phase by
`tests/blueprint_roundtrip.py`: `director.accept_revision` authorized the
policy level against itself, so the authority check could never refuse.

## What this tracer does not prove

Stated plainly, because a green freeze-gate line is exactly what a later reader
is most likely to over-read.

- **The blueprint is fictional and so is every drafted item.** The "Beacon"
  exam is invented. Its only relationship to any real standardized exam is its
  shape, and no real course, exam, syllabus, learner note, or bank appears
  here or is paraphrased here.
- **Five of the eight blueprint dimensions are checked against SUPPLIED
  facts.** Construct, demand, timing, tools and feedback conditions are not
  carried by the bank format, so the tracer supplies them. Nothing here proves
  a real operator would supply them correctly, only that an unsupplied one
  reads `unverifiable` rather than passing silently.
- **It exercises no learner-facing surface.** There is no CLI command and no
  daemon route in Phase 15B. Whether an acceptance, a rejection, or a staleness
  disposition READS correctly to a human is the review's subject and not the
  tracer's.
- **It does not freeze the course schema.** That is Phase 14B's, and 14B's own
  record says it is not that freeze either. 15B amended that record to add one
  sidecar section and did not otherwise touch it.
- **The evidence-to-graph join is not closed.** The evidence log keys events by
  objective TEXT and the course graph keys objectives by opaque id. This phase
  normalizes objective text identically to `director.locator_key` and proves
  that for its own fixture strings; it does not prove that every shipped bank
  objective string round-trips to a graph objective id without loss, and
  nothing in this phase closes that join.
- **One operation shape, one course.** No concurrent acceptances, no
  long-running job, and no course large enough to make any of these figures a
  performance claim.
