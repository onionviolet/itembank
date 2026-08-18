# 14A-04 summary (PARTIAL: Tasks 1-2 complete, halted at Task 3 checkpoint)

**Status: Tasks 1-2 complete, halted at Task 3 checkpoint.** Task 3 (the
reflow-normalization one-way door) is a blocking human decision this executor
does not have authority to make. It is not answered here, `14A-FREEZE.md` is
not written, and Task 4 (declaring the freeze) has not run. 14A remains open
until Task 3 is answered and Task 4 is executed on a green tracer.

## Precondition check (before Task 1)

`for t in tests/*.py; do python3 "$t" || exit 1; done` was re-run at the
start of this session (the `timeout` command is not installed on this
machine, so the plain form was used, matching the precedent already recorded
in `14A-03-SUMMARY.md`). All 67 files in `tests/` passed, including
`tests/audit_writer_roundtrip.py` and `tests/lti_roundtrip.py`, both of which
were fixed by commits `a5a1c0d` and `6b33152` immediately before this
session. The precondition was green; Task 1 proceeded.

## Task 1: the eight-scenario tracer

Created `tests/file_fault_tracer.py` with a local `fail(msg)` helper, the
eight scenario functions (`scenario_move`, `scenario_duplicate`,
`scenario_conflict`, `scenario_external_edit`, `scenario_denied_path`,
`scenario_interrupted_write`, `scenario_disk_full`, `scenario_root_missing`),
`shipped_suite_check()`, and `main()`. `scenario_interrupted_write` imports
`tests/journal_roundtrip.py` as a module and reuses its `_child_kill_before_commit`
`--child` subprocess fixture rather than copying it, per the plan's own
instruction. All eight scenarios run on one "1k" corpus built and torn down
in a `finally` block.

Committed as `bc347a6` ("test(14A-04): the eight-scenario tracer"), with the
file scoped to exactly Task 1's functions (no `reflow_corpus_check`,
`measure_budgets`, or report writer yet) so the commit boundary matches the
plan's task boundary; `fixtures/corpus_14a.py` was left unchanged for this
commit.

Verified at commit time: `python3 tests/file_fault_tracer.py` exited 0 with
final line `TRACER: 8 passed, 0 skipped, 0 failed`; `python3 itembank.py
guard .` printed `0 offending files`.

## Task 2: budgets measured and the reflow corpus counted

Added `fixtures/corpus_14a.py:mutate_corpus(dest, count, seed)`, producing a
deterministic, on-disk mutation set over an already-built corpus in a fixed
1:1:1:1 proportion across four labelled classes (`content`, `trailing_ws`,
`line_ending`, `reflow`), documented in the function's own docstring. File
selection excludes the permission-denied pocket and any symlink (checked
with `os.access` and `os.path.islink`), since this function mutates ordinary
readable/writable corpus files only.

Added `tests/file_fault_tracer.py:reflow_corpus_check()`, which builds the
"10k" corpus, mutates 2000 files, and computes four counts per mutation: the
shipped first-cut fingerprint (`identity.object_fingerprint`) noticing a
change, a locally-implemented candidate reflow-normalizing fingerprint
variant (`_candidate_fingerprint`) noticing a change, and an independent
ground-truth classification of whether the mutation is reflow-only
(`_is_reflow_only`), located with a common-prefix/common-suffix helper
(`_common_prefix_suffix_len`) rather than `difflib.SequenceMatcher` opcodes,
per the plan's cited 04-02 caveat that SequenceMatcher's opcodes are
alignment-dependent and non-minimal. `_candidate_normalize` never alters
bytes for kind `bank` or `lesson`, honoring the keyed-content carve-out by
construction; every mutated file in this generic corpus fingerprints as kind
`source`, so the carve-out is coded but not exercised by this specific
corpus (recorded as a deviation-adjacent note below, not a gap: the plan
only requires the rule never be applied to those two kinds, not that the
corpus contain them).

Added `tests/file_fault_tracer.py:measure_budgets()`, a median-of-three
measurement of the four D-12.6-10 quantities (time to the first yielded
`discovery.inventory` entry, time to a complete `discovery.run_report`, time
from setting a cancel flag to the generator stopping, and peak traced Python
memory via `tracemalloc.get_traced_memory()`) on the 1k and 10k corpora.
Wrapped in a `try/except Exception` per run so a measurement failure is
recorded as a gap, never a tracer failure, matching D-12.6-10's own wording
that these are starting budgets to measure against, not promises.

Added `write_report()`, which writes
`.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md`
with the seven named sections (Run, Scenario results, Measured quantities,
The 100k corpus, Reflow corpus check, Shipped suite check, Open items routed
forward).

Committed as `3ec3600` ("test(14A-04): budgets measured and the reflow
corpus counted").

## Verification results (Tasks 1-2)

- `python3 tests/file_fault_tracer.py` -- exit 0. Final line verbatim:
  `TRACER: 8 passed, 0 skipped, 0 failed`. Re-run twice to confirm
  idempotency; both runs produced the same final line and a clean guard
  afterward.
- `python3 itembank.py guard .` -- `0 offending files`, exit 0, run after
  every tracer invocation in this session.
- `python3 tests/identity_roundtrip.py` -- exit 0, `OK identity_roundtrip`.
- `python3 tests/journal_roundtrip.py` -- exit 0, `OK journal_roundtrip`.
- `python3 tests/operations_roundtrip.py` -- exit 0, `OK
  operations_roundtrip`.
- No em dash character in `tests/file_fault_tracer.py`,
  `fixtures/corpus_14a.py`, or `14A-TRACER-REPORT.md` (checked by grep).

## Tracer's final line, verbatim

```
TRACER: 8 passed, 0 skipped, 0 failed
```

## Scenarios: all 8 passed, none skipped

This machine is macOS (posix), so `corpus_14a.build_corpus`'s
`denied_mode` was `"read"` throughout every run in this session:
`scenario_denied_path` took the primary (`os.chmod`-denies-read) branch and
returned `"pass"`, never the Windows-only `"skip"` branch that prints the
exact line `SKIP: read-denial assertion (os.chmod cannot deny read on this
platform)`. No scenario was skipped on this run; the write-mode branch's
code path exists and is written to the plan's exact table (verified by
inspection, not by execution on this platform), and is exercised by
`journal_roundtrip.py`'s own `_check_permission_denied` on the Windows CI
runner.

## Every measured number, with unit and run count

All measurements are median-of-three (`run_count = 3` on every row; no
`measure_budgets` run raised an exception on this machine, so no gap note
appears in the report).

| Quantity | Corpus | Value | Unit |
|---|---|---|---|
| first useful discovery result | 1k | 0.12 | ms |
| full inventory | 1k | 0.02 | s |
| cancel response | 1k | 0.06 | ms |
| peak traced Python memory | 1k | 0.59 | MB |
| first useful discovery result | 10k | 0.28 | ms |
| full inventory | 10k | 0.19 | s |
| cancel response | 10k | 0.02 | ms |
| peak traced Python memory | 10k | 4.78 | MB |

Platform: `macOS-27.0-arm64-arm-64bit-Mach-O`. Python: `3.14.6`. Every
number is far inside its D-12.6-10 starting budget on this machine, which is
recorded as a measurement only, never as a promise, per the report's own
heading sentence.

## The four reflow counts

- Total mutations: 2000
- Meaningful (real content changes the first cut correctly notices): 500
- Reflow-only changes the first cut notices (the candidate rule would
  absorb these): 500
- Changes the first cut already absorbs (trailing whitespace, line
  endings): 1000
- False-absorption count (candidate rule would absorb a change that is
  NOT reflow-only): 0

Mutation class proportions used: `content=0.25, line_ending=0.25,
reflow=0.25, trailing_ws=0.25` (the fixed 1:1:1:1 split
`mutate_corpus` documents).

## Checkpoint answer and who gave it

**Not yet answered.** Task 3 is the phase's one blocking checkpoint (the
reflow-normalization one-way door) and requires Weibao's decision between
option-a (keep the first cut, recommended default) and option-b (add reflow
normalization for kinds other than bank/lesson). This executor halted before
Task 3 per its instructions and did not decide it. The orchestrator carries
the "Reflow corpus check" section above (with its four counts) to Weibao for
that decision.

## Freeze section: not written

`.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` was not
created. Per the plan, the freeze is declared only after Task 3's checkpoint
is answered and Task 4 re-verifies a green tracer, the full suite, and
`guard`. None of that ran in this session.

## Disposition of the two flagged edge-probe rows carried from 14A-01 and 14A-03

Both were already closed in their originating plans, not deferred to this
tracer:

- **FILE-02 unclassified edge** (14A-01): closed in `14A-01-SUMMARY.md`'s
  "Disposition of the flagged FILE-02 unclassified edge" section.
  `discovery.inventory()`'s `resume_after` contract, proven by
  `check_discovery()`, was judged sufficient; no further identity beyond
  relative path plus root was needed. Recorded again in
  `14A-TRACER-REPORT.md`'s "Open items routed forward" section for
  visibility at the freeze gate, but there is nothing left open here to
  route forward.
- **ID-02 unclassified edge** (14A-03): closed in `14A-03-SUMMARY.md`'s
  "Disposition of the flagged ID-02 unclassified edge" section. The rights
  model already keeps fingerprint and rights on separate fields; no further
  attestation record is needed to satisfy ID-02 as written. A future
  recorded rights *grant* (who granted it, when, under what license), if
  ever wanted, is RIGHTS-02, owned by 14B/15A, not a gap in ID-02 itself.
  Recorded again in `14A-TRACER-REPORT.md` for the same visibility reason.

## Which truth was verified by which command

| Truth | Verified by |
|---|---|
| All eight G3 scenarios walk end to end on one 1k corpus in one run | `python3 tests/file_fault_tracer.py`, the eight `scenario <name>: pass` lines |
| Every scenario asserts old-or-new, fails loudly with `mixed state` on neither | code inspection of each `scenario_*` function in `tests/file_fault_tracer.py`; `_assert_old_or_new` helper used by four of the eight |
| The shipped parser/scorer/evidence suites pass unchanged (audit A6) | `shipped_suite_check()`'s subprocess run of `scoring_roundtrip.py`, `evidence_roundtrip.py`, `audit_writer_roundtrip.py`, `durability_roundtrip.py`, all exit 0 |
| `guard` reports zero offending files after the tracer runs | `python3 itembank.py guard .` run after every tracer invocation this session |
| A root that disappears is reported unavailable, the walk never crashes | `scenario_root_missing`, `python3 tests/file_fault_tracer.py` output |
| D-12.6-10 quantities are measured, not promised, and never fail the tracer | `measure_budgets()`'s own `try/except Exception` per run; the report's "Measured quantities" heading sentence |
| The reflow question has real corpus evidence behind it | `reflow_corpus_check()`'s four counts, printed to stdout and written to `14A-TRACER-REPORT.md` |
| The 100k corpus is deliberately not run, with its reason recorded | `14A-TRACER-REPORT.md`'s "The 100k corpus" section |

## Deviations from plan

1. **Commit split required temporarily writing and re-writing
   `fixtures/corpus_14a.py` and `tests/file_fault_tracer.py`.** The plan
   assigns both files to Task 1 and Task 2. Since the two tasks land as two
   separate commits and both tasks touch the same two files, this executor
   built the full Task 1 + Task 2 implementation first to prove it worked
   end to end, then reconstructed a Task-1-only version of both files
   (`fixtures/corpus_14a.py` unchanged from `HEAD`, `tests/file_fault_tracer.py`
   with only the eight scenarios and `shipped_suite_check`), verified that
   version standalone, committed it, then re-applied the Task 2 additions
   (`mutate_corpus`, `reflow_corpus_check`, `measure_budgets`,
   `write_report`) and committed those. No functional deviation from the
   plan's own action lists; this is a mechanical note about how the two
   commits were produced from what was, at one point, written as a single
   pass.
2. **`scenario_move` and `scenario_duplicate` use `journal.op_link`, not
   `journal.commit_operation(..., "mint", ...)`, to bring an already-existing
   corpus file under journal identity.** The plan's table says "`journal.op_move`
   a corpus file to a new path" and "run
   `journal.copy_candidates_from_registry` over the duplicate-fingerprint
   pair" without specifying how the corpus file first enters the journal.
   `journal.commit_operation` with `operation="mint"` refuses with
   `journal.no_change` when the target already holds the exact bytes being
   "minted" (the corpus file already exists with that content on disk), so
   `op_link` (which never writes the target) is used instead, matching the
   precedent `operations_roundtrip.py`'s own `_check_duplicate_pair` and
   `_check_near_duplicate_pair` already set for exactly this situation.
   Recorded as an auto-fix per the plan's own precedent, not a scope change.
3. **`scenario_move`'s corpus file is located by walking `root_vault` for a
   file named `file_0000.md`, not by a fixed path
   `root_vault/file_0000.md`.** `corpus_14a.build_corpus` places file
   `n` in a deterministic but not always top-level subdirectory (via
   `_relative_dirs`), so the plain path did not exist on this run (the file
   landed in `root_vault/unit_02/`). A small `_find_first_file` helper walks
   the root deterministically (sorted directories, sorted files) to locate
   it. This is a mechanical fixture-navigation fix, not a change to what
   the scenario asserts.
4. **`fixtures/corpus_14a.py:mutate_corpus`'s candidate file selection
   excludes any file that fails `os.access(p, os.R_OK | os.W_OK)` or is a
   symlink.** Without this filter, `mutate_corpus` could select the
   corpus's own permission-denied pocket file (`root_vault/private/denied.md`)
   and crash with `PermissionError`, which happened on the first run of
   `reflow_corpus_check()` in this session. The plan's `mutate_corpus`
   contract says it "produces a deterministic change set over an existing
   corpus" without addressing the denied pocket; excluding deliberately
   inaccessible fixtures from a mutation sample is the only reading
   consistent with the corpus's own purpose (the denied pocket exists to be
   denied, not mutated).

No deviation changed what a scenario asserts, what the eight scenarios or
`shipped_suite_check` prove, or the reflow check's methodology as specified
in the plan's action list.

## What Task 3 needs, carried forward

The orchestrator should present Weibao with the "Reflow corpus check"
section of `14A-TRACER-REPORT.md`, quoted verbatim (see above), and the two
options from the plan's Task 3 (`option-a`: keep the first cut, recommended
default; `option-b`: add reflow normalization for kinds other than
bank/lesson). On this corpus, the false-absorption count is 0 and the
reflow-only-noticed count is 500, both figures the plan says the
recommendation should turn on. Task 3's own text already recommends
option-a; this run's counts do not contradict that recommendation, but the
decision itself is Weibao's to make, not this executor's.
