# 15A tracer report

Measured 2026-08-30 on **Darwin 27.0.0 arm64**, **Python 3.14.6**. Every figure
below was produced by the run this report describes. No budget, target, or
estimate appears anywhere in it: a number among measurements that was not
measured is a fabricated measurement.

## What was run

```
python3 tests/four_subject_review.py
```

Exit 0. Full output, verbatim:

```
scenario four_subject_recommendation: pass
scenario direct_reading_and_untreated: pass
scenario coverage_states: pass
scenario egress_exactness: pass
scenario backend_parity: pass
scenario backend_loss: pass
scenario protocol_replay: pass
scenario reversal: pass
measured on: Darwin arm64, Python 3.14.6
measured four-subject pass: 0.377 s
measured journal entries appended: 191
measured total payload bytes: 16401
measured largest single payload: 907 bytes
measured spans approved: 5
measured spans omitted: 1
measured objectives in the pass: 19
measured outcome counts: {'bound': 8, 'untreated': 7, 'refused': 4}
measured coverage states seen, five-state binding set: ['conflicting', 'covered', 'missing', 'thin', 'unknown']
measured coverage states seen, four-subject bindings: ['thin']
measured protocol steps recorded: 12
measured interruption points walked: 13
measured whole tracer: 17.769 s
TRACER: 8 passed, 0 skipped, 0 failed
```

The tracer runs `shipped_suite_check()` before importing any 15A module.
`tests/scoring_roundtrip.py`, `tests/evidence_roundtrip.py` and
`tests/protocol_roundtrip.py` each exited 0, and both `14A-FREEZE.md` and
`14B-FREEZE.md` carry their `## Frozen at` headings. A red shipped suite or a
missing upstream freeze skips every scenario rather than reporting passes.

**Full suite**, run separately on the same machine: **98 test files, 306
seconds, 0 failures**. `python3 itembank.py guard .` reports `0 offending
files`.

## Requirement coverage

| Requirement | Scenario function | Result |
|---|---|---|
| TREAT-01 | `scenario_four_subject_recommendation` | passed |
| TREAT-01, the two named cases | `scenario_direct_reading_and_untreated` | passed |
| TREAT-02 | `scenario_coverage_states` | passed |
| RIGHTS-02 | `scenario_egress_exactness` | passed |
| AGENT-02 | `scenario_backend_parity` | passed |
| AGENT-02, degraded | `scenario_backend_loss` | passed |
| AGENT-01, RELIABILITY-02 | `scenario_protocol_replay` | passed |
| RELIABILITY-02, reverse | `scenario_reversal` | passed |

Eight rows, all `passed`. No row is `skipped` and none is `weaker proof`.

Two notes on what `passed` means here, so the rows are not read as more than
they are:

- `scenario_egress_exactness` computes the expected approved-span set
  independently, by walking each course root's `## Bindings` source rows and
  reading each source's rights from `journal.read_registry` directly. It does
  not call `director.approved_spans` to build the expectation. Comparing a
  function's output to itself would prove the function is deterministic, not
  that it is correct.
- `scenario_backend_parity` runs both transports at `recommend-only` autonomy,
  so neither writes. A writing first run would mutate the state the second
  reads, and the comparison would then compare two different situations rather
  than two backends.

## Measured budgets

Every figure is a measurement from the run above, on **Darwin arm64, Python
3.14.6**, dated **2026-08-30**. Nothing here is asserted against.

| Figure | Measured value |
|---|---|
| One full four-subject recommendation pass | **0.377 seconds** |
| Whole tracer, all eight scenarios | **17.769 seconds** |
| Journal entries appended by the pass | **191 entries** |
| Total payload bytes across the run | **16401 bytes** |
| Largest single payload | **907 bytes** |
| Spans approved for egress | **5 spans** |
| Spans omitted, with reasons | **1 span** |
| Objectives in the pass | **19 objectives** |
| Outcomes | **8 bound, 7 untreated, 4 refused** |
| Protocol steps recorded | **12 of 13**, the thirteenth being `preview`, recorded `not-applicable` |
| Interruption points walked | **13**, one per protocol step |
| Full suite | **98 files, 306 seconds, 0 failures** |

The eight outcome counts sum to 19, which equals the objective count, so no
objective was silently skipped.

## Defects found and fixed

**One, in the tracer's own first draft, found by reading a measurement rather
than an assertion.**

`scenario_coverage_states` first asserted only that every coverage state
produced across the four subjects was a member of `graph.BINDING_STATES`, and
it passed. The measured line then read `coverage states seen: ['thin']`: one
state out of five. The assertion was true and nearly worthless, and only the
measurement showed it.

TREAT-02's Fixture sentence asks for a binding set carrying one claim in each
of the five states plus a heading-similarity decoy. The scenario now asserts
all five are produced by real claim data, using the five-state binding set
`fixtures.corpus_14b.build_coverage_fixture` builds.

**This exposed a real limit, recorded rather than hidden.**
`director.coverage_claims_for` cannot by itself produce every state. It builds
claims from `## Bindings` rows, and a binding row carries no `assertion`
column, while `conflicting` is by definition two claims asserting different
things about one objective. So the four-subject bindings reach `thin` and
nothing else, and the report says so on its own measured line rather than
quietly reporting the five-state figure alone. Carried as an open finding.

No defect was found in `director.py` by this tracer.

## What this tracer does not prove

Stated plainly, because a green freeze-gate line is exactly the thing a later
reader is most likely to over-read.

- **It uses mock backends, not a real provider.** Both transports run
  `fixtures/mock_backends.py`, a fixed rule with no randomness and no clock
  read. Nothing here proves how a real model behaves, how it fails, how slow it
  is, or what it costs. The parity result proves the two transports carry the
  same answer, not that the answer is good.
- **It uses fictional corpora, not real course material.** The four subjects
  are invented. Their only relationship to EMT, Math 1400, CSCI 1100, or any
  standardized exam is their shape. No real course, book, learner, exam, or
  bank content appears, and nothing here is a paraphrase of any.
- **It exercises no learner-facing surface.** There is no CLI command, no
  daemon route, and no rendered page in Phase 15A. The `preview` protocol step
  is recorded `not-applicable` for exactly this reason, and an agent never
  self-certifies accessibility.
- **It does not freeze the course schema.** That is Phase 14B's, and 14B's own
  freeze record says it is not the course schema freeze either. It is also not
  a lesson-profile freeze, not an agent job protocol freeze, and not a
  learner-facing surface freeze.
- **It proves one operation shape.** One recommendation operation over one
  objective at a time. It does not exercise concurrent operations across
  subjects, long-running jobs, or an operation whose provider answers slowly.
