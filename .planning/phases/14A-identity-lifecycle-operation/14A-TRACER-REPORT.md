# 14A tracer report

## Run

- Date: 2026-08-18
- Machine: the executor's own development machine (local, not a shared or cloud host)
- Platform: macOS-27.0-arm64-arm-64bit-Mach-O
- Python: 3.14.6
- Corpus sizes run: 1k, 10k
- Run count behind each measured number: median of 3 runs, stated again per row below

## Scenario results

| Scenario | Result |
|---|---|
| move | pass |
| duplicate | pass |
| conflict | pass |
| external_edit | pass |
| denied_path | pass |
| interrupted_write | pass |
| disk_full | pass |
| root_missing | pass |
| check_two_file_pair_atomicity | pass |

## Measured quantities

These are measurements taken on this machine, on this run. They are not promises to any user or later phase (D-12.6-10).

| Quantity | Corpus | Measured | Unit | Runs | D-12.6-10 starting budget |
|---|---|---|---|---|---|
| first useful discovery result | 1k | 0.14 | ms | 3 | < 2000 ms on 10k |
| full inventory | 1k | 0.02 | s | 3 | < 60 s on 100k (measured here on 1k/10k only; see The 100k corpus section) |
| cancel response | 1k | 0.08 | ms | 3 | < 500 ms |
| peak traced Python memory (not process RSS) | 1k | 0.59 | MB | 3 | bounded by streaming (no fixed number) |
| first useful discovery result | 10k | 0.31 | ms | 3 | < 2000 ms on 10k |
| full inventory | 10k | 0.23 | s | 3 | < 60 s on 100k (measured here on 1k/10k only; see The 100k corpus section) |
| cancel response | 10k | 0.02 | ms | 3 | < 500 ms |
| peak traced Python memory (not process RSS) | 10k | 4.78 | MB | 3 | bounded by streaming (no fixed number) |

## The 100k corpus

Not run in 14A. The 14A brief's own 14A-04 text names the 1k/10k corpora; the 100k size is D-12.6-10's recommendation, not 14A's task, and generating 100k files inside a suite CI runs on every push costs minutes per run. Routed to 14B, per this plan's own locked decision table.

## Reflow corpus check

- Total mutations: 2000
- Meaningful changes noticed by the first cut: 500
- Reflow-only changes noticed by the first cut: 500
- Changes the first cut already absorbs (trailing whitespace, line endings): 1000
- False-absorption count (candidate rule would absorb a change that is NOT reflow-only): 0
- Mutation class proportions used: content=0.25, line_ending=0.25, reflow=0.25, trailing_ws=0.25
- Recommendation the counts support: counts support keeping the first cut (option-a): nothing notices a change without a reason

## Shipped suite check

| Suite | Exit code |
|---|---|
| scoring_roundtrip.py | 0 |
| evidence_roundtrip.py | 0 |
| audit_writer_roundtrip.py | 0 |
| durability_roundtrip.py | 0 |

This closes the audit A6 obligation: the shipped parser, scorer, and evidence suites pass unchanged after 14A.

## Open items routed forward

- FILE-02's flagged unclassified edge (whether the "useful before completion" clause implies a stable partial-result identity beyond streaming plus resume_after) was closed in 14A-01, not deferred here: see 14A-01-SUMMARY.md's "Disposition of the flagged FILE-02 unclassified edge" section.
- ID-02's flagged unclassified edge (whether "hashes never prove authorship or rights" implies an obligation beyond keeping the fingerprint out of rights decisions) was closed in 14A-03, not deferred here: see 14A-03-SUMMARY.md's "Disposition of the flagged ID-02 unclassified edge" section. A future recorded rights grant, if wanted, is RIGHTS-02, owned by 14B/15A.

