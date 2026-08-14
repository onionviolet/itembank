---
phase: 14A-identity-lifecycle-operation
plan: 04
type: execute
wave: 4
depends_on: ["14A-03"]
files_modified:
  - tests/file_fault_tracer.py
  - fixtures/corpus_14a.py
  - .planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md
  - .planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md
autonomous: false
requirements: [FILE-01, FILE-02, FILE-03, ID-01, ID-02, RIGHTS-01, RELIABILITY-01]
must_haves:
  truths:
    - "One scripted tracer walks all eight G3 scenarios end to end on the synthetic corpus in one run: move, duplicate, conflict, external edit, denied path, interrupted write, disk-full simulation, and a root temporarily missing (14A-BRIEF.md 14A-04)."
    - "Every scenario asserts that the on-disk state is either the old valid state or the new valid state, and the tracer fails loudly with a message beginning FAIL: mixed state if it is neither (RELIABILITY-01)."
    - "The tracer measures the D-12.6-10 quantities on the 1k and 10k corpora and records the real numbers with their units, their hardware, and their run count. No number in the report is a promise and none is copied from the decision record (D-12.6-10)."
    - "The tracer runs a real-diff corpus check over the 10k corpus that counts how many observed file changes are Markdown-insignificant reflow only, and the count decides the deferred D-14A-2 reflow-normalization question from evidence rather than from preference."
    - "The reflow decision is recorded, with its evidence, in the tracer report and in the freeze record, whichever way it goes."
    - "The shipped parser, scorer, and evidence suites pass unchanged after 14A: the tracer runs them and records the result, closing the audit A6 obligation."
    - "python itembank.py guard . reports zero offending files after the tracer has run, so the synthetic corpus never left real content in the repository."
    - "A root that disappears between two tracer passes is reported as unavailable and the course opens over the last recorded index; the tracer never crashes on a missing root (FILE-01 degraded clause)."
    - "The freeze record states, in one place, exactly what is frozen: the object id shape, the eleven revision keys, the twenty-two journal entry keys, the two-line prepared-then-applied protocol, the six operation names, and the fingerprint normalization rule including the reflow decision."
    - "The freeze is declared only on a green tracer. A red tracer leaves 14A open and the freeze record unwritten."
    - statement: "No measured budget number in the report was produced by a run that also had a debugger, a profiler, or a competing tracer pass attached, and the report states the machine and the Python version each number came from."
      verification: backstop
  prohibitions:
    - "The tracer never reports a measured budget it did not actually measure."
    - "The reflow decision is recorded from corpus evidence, never asserted from preference."
    - "A freeze is never declared on a red tracer."
  artifacts:
    - "tests/file_fault_tracer.py, the phase freeze gate"
    - ".planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md"
    - ".planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md"
    - "the 10k corpus size in fixtures/corpus_14a.py, exercised for the first time here"
  key_links:
    - "The freeze gate is the tracer, not this plan's completion. If tests/file_fault_tracer.py is red, identity, journal, and operation semantics stay unfrozen no matter what else is done."
    - "The reflow decision is a one-way door: it changes what counts as a change for every object recorded from that point on. It is the one checkpoint in this phase."
    - "Budgets are measured here and recorded as measurements. A later phase quoting them as guarantees is the failure mode D-12.6-10's own wording exists to prevent."
---

<objective>
Close Phase 14A by running its freeze gate: the file-fault and external-edit
tracer. One scripted run walks every G3 scenario end to end on the synthetic
corpus, measures the D-12.6-10 quantities and records real numbers, decides the
deferred reflow-normalization question from a real diff corpus, and confirms
the shipped parser, scorer, and evidence suites are unchanged. Identity,
journal, and operation semantics freeze only when it is green
(14A-BRIEF.md "Definition of done" and the 14A-04 exit criterion; ROADMAP Phase
14A "Freeze gate").

Decisions already made, cited, never re-derived:

- **14A-BRIEF.md 14A-04** names the eight scenarios, the 1k and 10k corpora,
  the reflow-decision corpus check, and the audit A6 byte-compatibility
  obligation. This plan adds mechanics, never scope.
- **D-12.6-10** (`DECISIONS-12.6-REMAINING-2026-08-14.md`): the starting
  budgets are first useful discovery results under 2 seconds on the 10k corpus,
  full inventory under 60 seconds on 100k, cancel responds under 500 ms, and
  memory bounded by streaming. Its own resolution line reads "pending
  measurement at 14A" and its recommendation states the numbers "are starting
  budgets to be measured against on real hardware at 14A, not promises."
- **D-14A-2** deferred reflow normalization to this tracer, "where a real diff
  corpus shows whether it is needed."
- **Audit A6** obligation: the shipped suites stay byte-compatible.

Decisions this plan makes and locks, so the executor never guesses:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| The 100k corpus | Not run in 14A. `build_corpus` accepts `"1k"` and `"10k"` only, and the report records the deferral with its reason | The 14A brief's own 14A-04 text names "the 1k/10k corpora". 100k is D-12.6-10's recommendation, not 14A's task, and generating 100k files inside a suite CI runs on every push costs minutes per run. Recorded as 14A-RESEARCH.md assumption A4 resolved by the planner rather than left to the executor. |
| Where the tracer lives | `tests/file_fault_tracer.py`, following the repository's direct-execution test convention | The 14A brief names this path first; `.github/workflows/ci.yml` runs every `tests/*.py` directly, so the freeze gate runs in CI without new infrastructure. |
| Pass or fail of a budget | The tracer never fails on a budget number. It fails only on a correctness assertion | D-12.6-10's wording is explicit that these are measurements, not promises. A budget that fails a build turns a measurement into a guarantee. |
| How the reflow question is decided | A counted corpus check, then a blocking checkpoint. The tracer counts reflow-only changes across the 10k corpus and reports the ratio; the human confirms the freeze | This is a one-way door under `PLANNING-DIRECTIVES.md` section 2 rule 1 (a format decision other phases build against), and section 2's other two stop conditions do not apply. It is the only checkpoint in Phase 14A. |
| Recommended default at the checkpoint | Do not add reflow normalization; keep the first cut (trailing whitespace and line endings, with `bank` and `lesson` exempt from the trailing-whitespace half) | Reflow normalization can only reduce the set of changes the system notices, and every change it stops noticing is a change a compare-and-swap write can silently pass. The burden of proof sits on adding it, and the corpus count is what could discharge that burden. |

Purpose: a freeze declared without a tracer is a guess.
Output: the tracer, its report with real numbers, and the freeze record.
</objective>

<context>
@.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md
@.planning/DECISIONS-PRE-14A-2026-08-14.md
@.planning/DECISIONS-12.6-REMAINING-2026-08-14.md
@.planning/phases/14A-identity-lifecycle-operation/14A-RESEARCH.md
@.planning/phases/14A-identity-lifecycle-operation/14A-VALIDATION.md
@.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-03-PLAN.md
@tests/durability_roundtrip.py
@identity.py
@discovery.py
@journal.py
</context>

## Artifacts this phase produces (plan 14A-04 share)

- `tests/file_fault_tracer.py` with these functions: `fail(msg)`,
  `scenario_move()`, `scenario_duplicate()`, `scenario_conflict()`,
  `scenario_external_edit()`, `scenario_denied_path()`,
  `scenario_interrupted_write()`, `scenario_disk_full()`,
  `scenario_root_missing()`, `measure_budgets()`, `reflow_corpus_check()`,
  `shipped_suite_check()`, and `main()`.
- `fixtures/corpus_14a.py` gains the `"10k"` size path exercised for the first
  time, plus `mutate_corpus(dest, count, seed)` producing a realistic change
  set for the reflow check (a mix of true content edits, whitespace-only edits,
  line-ending-only edits, and reflow-only edits).
- `.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md`.
- `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md`.

No new module, no CLI command, no daemon route, and no schema document.

<tasks>

<task type="auto">
  <name>Task 1: the eight-scenario tracer</name>
  <files>tests/file_fault_tracer.py, fixtures/corpus_14a.py</files>
  <precondition>The full shipped suite is green on this machine before the
  tracer is written: `for t in tests/*.py; do python "$t" || exit 1; done`
  exits 0. If it does not, stop and report which shipped test is red; the
  tracer's A6 obligation is meaningless against an already-red trunk, which is
  the exact failure recorded in `STATE.md`'s 2026-08-12 correction.</precondition>
  <read_first>
- `14A-BRIEF.md` section 14A-04, in full. It is the scenario list.
- `tests/durability_roundtrip.py` in full, for the spawn, sleep,
  `terminate()`, `wait()` harness and the platform-conditional probe style.
- `tests/journal_roundtrip.py` and `tests/operations_roundtrip.py` as delivered
  by 14A-02 and 14A-03, for the fault-injection helpers and the scenario
  scripts this tracer composes rather than rewrites.
- `fixtures/corpus_14a.py` as delivered by 14A-01, especially `build_corpus`'s
  returned dict keys `symlinks` and `denied_mode`.
- `.planning/phases/14A-identity-lifecycle-operation/14A-VALIDATION.md`, whose
  "Sampling Rate" section names the exact commands this tracer must be
  consistent with.
  </read_first>
  <action>
1. Create `tests/file_fault_tracer.py` with its own local `fail(msg)` helper
   printing `"FAIL: " + msg` and exiting 1, following the convention every
   other file in `tests/` uses. It builds the `"1k"` corpus once for the
   scenario walk and tears it down with `teardown_corpus` in a `finally`.

2. Implement the eight scenarios, each as its own function, each printing one
   line of the exact form `"scenario <name>: <result>"` and each asserting the
   old-or-new invariant explicitly. Where the on-disk bytes match neither the
   old nor the new content, call `fail` with a message beginning exactly
   `"mixed state"`.

   | Scenario | What it does | What it asserts |
   |---|---|---|
   | `scenario_move` | `journal.op_move` a corpus file to a new path | the object id is unchanged, the recorded path changed, the revision incremented, the bytes are byte-identical at the new path and absent at the old one |
   | `scenario_duplicate` | run `journal.copy_candidates_from_registry` over the duplicate-fingerprint pair | exactly one candidate pair, path-sorted, both ids still present, both files still present with their original bytes, nothing merged |
   | `scenario_conflict` | write a corpus file directly, then attempt `commit_operation` | the refusal code is `journal.conflict`, the message carries the next-safe-action sentence, the file's bytes are unchanged by the refused attempt |
   | `scenario_external_edit` | run `journal.detect_external_edits` after the previous scenario | exactly one `external_edit` record appended, carrying both fingerprints; a second call appends none |
   | `scenario_denied_path` | run `discovery.run_report` over the corpus containing the denied pocket | the denied path is inventoried with its state, named in the report, and its `(size, mtime_ns)` are unchanged; if `denied_mode` is `"write"` print the exact line `"SKIP: read-denial assertion (os.chmod cannot deny read on this platform)"` and assert the write refusal instead |
   | `scenario_interrupted_write` | spawn a child that reaches the window between the prepared append and the commit, terminate it | the bytes on disk are the old ones, `journal.replay` reports the entry as interrupted and names the surviving state |
   | `scenario_disk_full` | patch `journal._write_bytes_atomic` to raise `OSError(errno.ENOSPC, "No space left on device")` at the target-write point | the bytes on disk are the old ones, the last accepted revision is unchanged, the journal is still readable |
   | `scenario_root_missing` | run one inventory, remove a whole root with `shutil.rmtree`, run a second inventory | the removed root is reported once under `unavailable`, the other two roots still return their entries, no exception escapes, and the registry from the first pass is still readable |

3. Where a platform blocks a scenario, print the exact skip line named in the
   table and continue. A skipped scenario is recorded as skipped in the report,
   never as passed.

4. Reuse the fault helpers already written in `tests/journal_roundtrip.py` by
   importing them rather than copying them; the tracer composes the phase's own
   proofs, it does not rewrite them.

5. Implement `shipped_suite_check()` which runs, as subprocesses,
   `python tests/scoring_roundtrip.py`, `python tests/evidence_roundtrip.py`,
   `python tests/audit_writer_roundtrip.py`, and
   `python tests/durability_roundtrip.py`, and records each exit code. Any
   non-zero exit fails the tracer with a message naming the suite. This closes
   the audit A6 obligation.

6. Implement `main()` to run all eight scenarios plus `shipped_suite_check()`,
   print a final line of the exact form
   `"TRACER: <passed> passed, <skipped> skipped, 0 failed"`, and exit 0 only
   when the failed count is zero.
  </action>
  <verify>
  <automated>python tests/file_fault_tracer.py</automated>
Expected: the final line reads `TRACER: N passed, M skipped, 0 failed` and the
exit code is 0. Degraded states this task proves are the whole point of it:
every one of the eight scenarios is itself a degraded state, and each asserts
that the survivor is the old or the new valid state and never a mixture.
  </verify>
  <acceptance_criteria>
- `python tests/file_fault_tracer.py` exits 0 and its output contains one
  `scenario <name>:` line for each of the eight named scenarios.
- The output's final line matches the form `TRACER: N passed, M skipped, 0
  failed`.
- Every scenario function contains an explicit comparison of the on-disk bytes
  against both the old and the new content, and a `fail` call whose message
  begins `mixed state` when neither matches.
- `shipped_suite_check()` runs all four named shipped suites and records their
  exit codes.
- `python itembank.py guard .` prints `0 offending files` and exits 0 after the
  tracer run.
- `tests/file_fault_tracer.py` contains no em dash character.
  </acceptance_criteria>
  <done>All eight G3 scenarios walk end to end on the synthetic corpus in one
  scripted run, and the shipped suites are confirmed unchanged.</done>
</task>

<task type="auto">
  <name>Task 2: measure the D-12.6-10 quantities and run the reflow corpus check</name>
  <files>tests/file_fault_tracer.py, fixtures/corpus_14a.py, .planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md</files>
  <read_first>
- `.planning/DECISIONS-12.6-REMAINING-2026-08-14.md` D-12.6-10, in full,
  including the sentence stating the numbers are starting budgets to be
  measured against, not promises.
- `.planning/DECISIONS-PRE-14A-2026-08-14.md` D-14A-2, specifically the
  sentence deferring reflow normalization to this tracer "where a real diff
  corpus shows whether it is needed".
- `identity.normalize_for_fingerprint` as delivered by 14A-01, the one function
  a reflow rule would extend.
- `14A-RESEARCH.md` "Alternatives Considered", specifically the recorded
  caveat that `difflib.SequenceMatcher` opcodes are alignment-dependent and
  non-minimal, and that this repository already solved that once with a
  common-prefix and common-suffix helper (`STATE.md`, the 04-02 entry).
  </read_first>
  <action>
1. Add `mutate_corpus(dest, count, seed)` to `fixtures/corpus_14a.py`. It
   produces a deterministic change set over an existing corpus with four
   labelled classes, in a fixed proportion recorded in the function's
   docstring:
   - `content`: a real semantic edit (a word changed, a line added);
   - `trailing_ws`: trailing spaces added or removed on some lines;
   - `line_ending`: the file rewritten with CRLF instead of LF;
   - `reflow`: the same words rewrapped at a different column, with no word,
     punctuation, or ordering change.
   It returns a list of `(path, class, before_bytes, after_bytes)` tuples and
   writes nothing outside `dest`.

2. Implement `reflow_corpus_check()` in `tests/file_fault_tracer.py`. Build the
   `"10k"` corpus, run `mutate_corpus` over it, and for every mutation compute
   whether `identity.object_fingerprint(before, kind)` differs from
   `identity.object_fingerprint(after, kind)` under the shipped first-cut
   normalization. Then compute the same under a candidate reflow-normalizing
   variant implemented locally inside the tracer, which additionally collapses
   runs of whitespace including newlines within a paragraph before hashing.
   Record four counts:
   - changes the first cut notices and a reader would call meaningful;
   - changes the first cut notices that are reflow-only, meaning the candidate
     rule would have absorbed them;
   - changes the first cut already absorbs (trailing whitespace and line
     endings);
   - changes the candidate rule would absorb that are NOT reflow-only, which is
     the false-absorption count and the reason to refuse the rule.

   Implement the reflow comparison with a common-prefix and common-suffix
   helper rather than raw `difflib` opcodes, per the recorded 04-02 caveat, and
   say so in the function's docstring.

   Do not apply the candidate rule to kinds `bank` or `lesson`: the
   keyed-content carve-out from D-14A-2 holds regardless of the reflow answer,
   and the check must not measure a rule it would never be allowed to ship.

3. Implement `measure_budgets()`. On the 1k corpus and then on the 10k corpus,
   measure and record, each as a median of three runs with the run count stated:
   - time to the first yielded `discovery.inventory` entry, in milliseconds;
   - time to a complete `discovery.run_report`, in seconds;
   - time from setting a cancel flag to the generator stopping, in
     milliseconds;
   - peak resident memory during a full inventory, measured with
     `tracemalloc.get_traced_memory()` peak value, in megabytes, with a note
     that this measures Python allocations and not process RSS.
   Also record the Python version from `sys.version`, the platform from
   `platform.platform()`, and the machine identifier the report will name.

   `measure_budgets()` never fails the tracer. It returns its numbers.

4. Write
   `.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md`
   with exactly these sections:

   - **Run.** Date, machine, `platform.platform()` string, `sys.version`, the
     corpus sizes run, and the run count behind each number.
   - **Scenario results.** One row per scenario from Task 1, with pass,
     skipped, or failed, and for a skip the exact platform reason.
   - **Measured quantities.** A table of the D-12.6-10 quantities with the
     measured value, the unit, the denominator or run count, and the starting
     budget from D-12.6-10 alongside it, under a heading sentence stating in
     plain words that these are measurements on this machine and are not
     promises to any user or later phase.
   - **The 100k corpus.** One paragraph recording that it was not run in 14A,
     with the reason from this plan's decision table, and routing it to 14B.
   - **Reflow corpus check.** The four counts, the mutation proportions used,
     and the recommendation the counts support.
   - **Shipped suite check.** The four suites and their exit codes, closing the
     audit A6 obligation.
   - **Open items routed forward.** The two flagged edge-probe rows carried by
     14A-01 (FILE-02 unclassified) and 14A-03 (ID-02 unclassified), each closed
     here or routed to a named later requirement.

   No em dash characters. No real content, no absolute path pointing at a
   private bank, and no learner data.
  </action>
  <verify>
  <automated>python tests/file_fault_tracer.py</automated>
Expected: exit 0, and the run prints the measured numbers and the four reflow
counts. Degraded behavior proved here: `measure_budgets` never fails the tracer
on a slow machine, so an honest slow number is recorded rather than a build
being turned red by a measurement.
  </verify>
  <acceptance_criteria>
- `python tests/file_fault_tracer.py` exits 0 and prints a line containing
  `reflow-only:` followed by an integer.
- `.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md`
  exists with all seven named sections.
- Every number in the "Measured quantities" table carries a unit and a run
  count, and the section's heading sentence states that they are measurements
  and not promises.
- The "The 100k corpus" paragraph exists and names the reason for the
  deferral.
- The "Reflow corpus check" section reports all four counts.
- The report contains no absolute path under a private bank or vault
  directory, and no em dash character.
  </acceptance_criteria>
  <done>The D-12.6-10 quantities are measured and recorded honestly, and the
  reflow question has evidence behind it instead of an opinion.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 3: Weibao decides the reflow normalization rule, the one-way door</name>
  <files>.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md</files>
  <decision>
Should `identity.normalize_for_fingerprint` additionally normalize
Markdown-insignificant reflow before hashing, for the kinds that are not
`bank` or `lesson`?
  </decision>
  <context>
This is the deferred half of D-14A-2, and it is the phase's one-way door. The
rule decides what counts as a change for every object recorded from this point
on. Adding it later means every fingerprint recorded before the change reads as
stale; removing it later means changes the system stopped noticing were never
recorded at all.

Show Weibao the "Reflow corpus check" section of
`14A-TRACER-REPORT.md` verbatim: the four counts and the mutation
proportions. State the two consequences in one sentence each: a rule that
absorbs reflow means a file rewrapped by an editor does not read as changed and
does not create a revision; a rule that does not absorb it means such a file
does read as changed and creates a revision that says only that the wrapping
moved.

The keyed-content carve-out is not on the table either way. `bank` and `lesson`
stay exempt from trailing-whitespace normalization under both options, per
D-14A-2's own sentence that keyed assessment content is never normalized in a
way that could mask a scoring-relevant change.
  </context>
  <options>
    <option id="option-a">
      <name>Keep the first cut. No reflow normalization. (Recommended default)</name>
      <pros>Nothing the system currently notices stops being noticed. The
      burden of proof stays on the rule that removes information. A spurious
      revision that says "the wrapping moved" is a cosmetic annoyance; a change
      silently absorbed by a compare-and-swap write is a correctness
      problem.</pros>
      <cons>An editor that rewraps on save creates revisions with no semantic
      content, which a later history view will have to present
      gracefully.</cons>
    </option>
    <option id="option-b">
      <name>Add reflow normalization for kinds other than bank and lesson</name>
      <pros>A rewrap-on-save editor stops generating empty revisions, and the
      history view stays readable without filtering.</pros>
      <cons>Every change the rule absorbs is a change a compare-and-swap write
      will pass without noticing. The false-absorption count in the report is
      the direct measure of that risk.</cons>
    </option>
  </options>
  <action>
Present the report section and the two options. Record the answer in
`.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` under a dated
heading, with the four counts quoted beside it as the evidence, and note that
the decision amends D-14A-2's deferred item.

What the executor does with each answer:

- **option-a**: change nothing in `identity.normalize_for_fingerprint`. Record
  the decision and the counts. Proceed to Task 4.
- **option-b**: implement the rule in
  `identity.normalize_for_fingerprint` for kinds not in
  `TRAILING_WS_EXEMPT_KINDS`, re-run `python tests/identity_roundtrip.py`,
  `python tests/journal_roundtrip.py`,
  `python tests/operations_roundtrip.py`, and
  `python tests/file_fault_tracer.py`, and add the assertions that a reflow-only
  edit produces an equal fingerprint for a `course` object and an unequal one
  for a `bank` object. Only then proceed to Task 4. Note that this adds
  `identity.py` to this plan's modified files, which is a deliberate,
  checkpoint-authorized deviation to be recorded in the summary.

Do not proceed with a silent default. An unanswered checkpoint stops the wave
and leaves 14A unfrozen.
  </action>
  <resume-signal>Select: option-a or option-b</resume-signal>
  <verify>
`14A-FREEZE.md` carries a dated decision line naming option-a or option-b, the
four counts quoted as evidence, and, if option-b, a green re-run of all four
test commands recorded beside it.
  </verify>
  <acceptance_criteria>
- `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` exists and
  contains a dated line naming exactly one of `option-a` or `option-b`.
- The four reflow counts appear in the freeze record as the recorded evidence.
- If option-b was chosen, `python tests/identity_roundtrip.py`,
  `python tests/journal_roundtrip.py`, `python tests/operations_roundtrip.py`,
  and `python tests/file_fault_tracer.py` all exit 0 after the change, and the
  two new assertions exist.
- The freeze record contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">This decides what counts as a change for
  every object fingerprinted afterward. It is the reason this task is a
  checkpoint rather than an executor judgment.</reversibility>
  <done>The deferred D-14A-2 item is decided by a human, from the corpus
  evidence, and recorded.</done>
</task>

<task type="auto">
  <name>Task 4: declare the freeze, or leave it open</name>
  <files>.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md</files>
  <read_first>
- The tracer's own final output line from Task 1.
- `14A-BRIEF.md` "Definition of done" and the 14A-04 exit criterion.
- `identity.REVISION_KEYS`, `journal.ENTRY_KEYS`, `journal.OPERATION_TYPES`,
  and `identity.TRAILING_WS_EXEMPT_KINDS` as they stand after Task 3.
  </read_first>
  <action>
1. Re-run the freeze gate one final time and capture its output verbatim:

```
python tests/file_fault_tracer.py
```

   Expected final line: `TRACER: N passed, M skipped, 0 failed`, exit code 0.
   If the failed count is not zero, stop. Do not write a freeze section, and
   report which scenario is red. A red tracer means 14A stays open, which is
   the brief's own exit criterion.

2. Run the full suite the way CI runs it and capture the result:

```
for t in tests/*.py; do python "$t" || exit 1; done
```

   Expected: exit code 0.

3. Run the content guard and capture the result:

```
python itembank.py guard .
```

   Expected final line: `0 offending files`, exit code 0.

4. Append a `## Frozen at 14A` section to `14A-FREEZE.md` naming, in one place,
   exactly what is now frozen and what is deliberately not:

   - **Frozen.** The object id shape (16 lowercase hex characters, minted with
     `uuid4`, never derived from content, path, or name); the eleven revision
     record keys in their fixed order; the twenty-two journal entry keys in
     their fixed order; the two-line prepared-then-applied protocol and the
     append-only resolution rule; the six operation names; the object kinds; the
     seven rights operation names and the three rights states; and the
     fingerprint normalization rule as decided in Task 3, including the
     `bank` and `lesson` carve-out.
   - **Not frozen, and deliberately so.** The `_journal/` directory name and
     internal file names, which are local layout a later phase may change with
     a migration; the disposable `objects.json` projection shape, which is
     rebuildable; the refusal message wording, which is copy and not contract;
     and everything routed to 14B in the three plans' out-of-scope sections.
   - **The evidence.** The tracer's final line quoted verbatim, the full suite
     result, the guard result, and a pointer to `14A-TRACER-REPORT.md`.
   - **What breaks if this is changed later.** One sentence per frozen item
     naming the migration it would force.

5. Update `.planning/REQUIREMENTS.md`'s status table rows for FILE-01, FILE-02,
   FILE-03, ID-01, ID-02, RIGHTS-01, and RELIABILITY-01 from `Pending` to
   `Complete`, editing only those seven rows and nothing else in the file.
  </action>
  <verify>
  <automated>python tests/file_fault_tracer.py</automated>
Expected: exit 0 with a failed count of zero. Degraded behavior this task must
honor rather than paper over: if the tracer is red, no freeze section is
written and the plan reports which scenario failed. A freeze declared on a red
tracer is the one outcome this task exists to prevent.
  </verify>
  <acceptance_criteria>
- `python tests/file_fault_tracer.py` exits 0 with `0 failed` in its final
  line.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `14A-FREEZE.md` contains a `## Frozen at 14A` section with all four named
  subsections, and the tracer's final line quoted verbatim.
- `.planning/REQUIREMENTS.md` shows `Complete` for exactly the seven 14A
  requirement rows, and `git diff --stat .planning/REQUIREMENTS.md` reports
  seven changed lines.
- `14A-FREEZE.md` contains no em dash character.
  </acceptance_criteria>
  <done>Identity, journal, and operation semantics are frozen on a green
  tracer, with the evidence recorded in one place, or 14A stays open with the
  red scenario named.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| tracer to repository | The tracer generates a 10k-file corpus and writes a report into the repository; both are paths where synthetic content could leak into committed content. |
| measurement to record | A number measured once on one machine becomes a written record other phases may read as a guarantee. |
| tracer result to freeze | A green or red tracer decides whether a format other phases build against is frozen. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14A-04-01 | Information Disclosure | corpus or report content entering the repository | high | mitigate | The corpus is generated into a temp directory and torn down in a `finally`; the report is prose with no bank content and no private path; `python itembank.py guard .` is an acceptance criterion of both Task 1 and Task 4. |
| T-14A-04-02 | Tampering | a measured number recorded as a promise | high | mitigate | The "Measured quantities" heading sentence states in plain words that the numbers are measurements on this machine; each carries a unit and a run count; `measure_budgets()` cannot fail the tracer, so no build depends on a number. |
| T-14A-04-03 | Repudiation | a freeze declared without the evidence that supports it | high | mitigate | Task 4 quotes the tracer's final line verbatim into the freeze record and refuses to write the section on a non-zero failed count. |
| T-14A-04-04 | Tampering | a reflow rule silently absorbing a scoring-relevant change | high | mitigate | The candidate rule is never applied to `bank` or `lesson` in the corpus check, the false-absorption count is reported as its own number, and the decision is a blocking human checkpoint rather than an executor judgment. |
| T-14A-04-05 | Tampering | a leftover permission-denied pocket or read-only file blocking teardown and leaving corpus files behind | medium | mitigate | `teardown_corpus` restores write permissions on every path before removal, and teardown runs in a `finally`. |
| T-14A-04-06 | Denial of Service | the 10k corpus making the CI suite unacceptably slow | medium | accept | The 10k corpus is built once per tracer run and torn down; the 100k size is deliberately not run. Accepted with the measured full-run time recorded in the report so a later phase can revisit it with a number. |
| T-14A-04-07 | Tampering | supply chain: a benchmarking, diffing, or fault-injection package added for the tracer | high | mitigate | None is added; `time`, `tracemalloc`, `platform`, `subprocess`, `difflib`, `shutil`, and `errno` are Python 3.11 standard library already used by shipped tests. Absence of a dependency is not itself the mitigation: any package added here later must be vendored at a pinned version with a recorded checksum and a named license review, per `PLANNING-DIRECTIVES.md` section 4a. |
| T-14A-04-08 | Spoofing | the tracer passing because a scenario silently skipped | high | mitigate | Every skip prints its exact platform reason, is counted separately in the final line, and is recorded as skipped rather than passed in the report. |
</threat_model>

<out_of_scope>
- No 100k corpus run. Recorded with its reason and routed to 14B.
- No new product module, function, CLI command, daemon route, or schema
  document. The tracer is a test; the only product code this plan may change is
  `identity.normalize_for_fingerprint`, and only if the Task 3 checkpoint
  returns option-b.
- No performance optimization. If a measured number is worse than the D-12.6-10
  starting budget, it is recorded as measured and routed forward. Tuning
  discovery is not a 14A task and must not be started here.
- No 14B work: no graph kernel, no sidecar, no outline projection, no course
  package, no clean-restore check. The clean-machine restore obligation belongs
  to 14B's freeze gate.
- No UI of any kind, including a history or diff view.
- No rename of the `mastered` state and no edit to `retention.py`,
  `selection.py`, `schemas/`, or anything under `surfaces/`.
- No re-litigation of D-14A-1, D-14A-2's resolved half, or D-14A-3. The only
  decision open in this phase is the reflow question in Task 3.
</out_of_scope>

<summary_obligations>
`14A-04-SUMMARY.md` records: the tracer's final line verbatim, which scenarios
were skipped and the exact platform reason for each, every measured number with
its unit and run count, the four reflow counts, the checkpoint answer and who
gave it, whether the freeze section was written or the phase left open and why,
the disposition of the two flagged edge-probe rows carried from 14A-01 and
14A-03, which truth was verified by which command, and any deviation from this
plan with its reason.
</summary_obligations>

<output>
Create `.planning/phases/14A-identity-lifecycle-operation/14A-04-SUMMARY.md`
when done.
</output>
