# A4 integrated synthetic study journey

Date: 2026-09-12. Base: `e7c242a89d16ecd2d715a0cb6b7197ab285bbff6` plus the preserved A1/A2/A5 working changes.
Owner: A4, task `01a0942a-63e8-7ac2-b50e-469806228dfa`.

Current gate: see the final cleanup-candidate validation below. Course-ops
and file-fault cleanup are resolved. Only the known four-subject parity
`ok / unavailable` and expected dirty-tree gates fail. The dirty tree is a
workflow condition, not a code failure. The bounded integration is complete
with those explicit limits, not repository-wide green.

## Scope and result

The supported browser journey reaches a populated course, reads its lesson,
uses canonical practice and permitted feedback, leaves, restarts the daemon,
and resumes the same sitting at item 2. A short response remains pending a
human mark. This is a completed verification journey, not a completed sitting
or course. No production repair was needed or made.

The fixture is an unchanged copy of `fixtures/lesson_bank.md`, created inside
an isolated temporary workspace through `course.create_course`. It has one
bank with a lesson and three items, zero bound sources and zero objectives.
This deliberately exercises the supported course-to-lesson route. It does not
claim a populated objective graph or a source-import browser exercise.

## Browser observations

Actual in-app browser control used the loopback daemon and visible controls.
These are browser observations, not inferred from HTTP HTML or helper calls.

| Check | Observation |
| --- | --- |
| B1: course entry | Shelf showed Start and Not started. Opening the course showed one bank, Start reading, and Sit the items. |
| B2: lesson | Start reading opened the synthetic lesson, including the table and both section headings. Read step by step showed 1 of 2 explanations. Next explanation showed 2 of 2. Reload returned to 1 of 2. |
| B3: learner notes and reading persistence | Neither continuous nor guided lesson exposed a note editor or reported-read control. Durable reading declaration and guided reading-position persistence are unavailable in this route. No substitute note file or A3 format was created. |
| B4: practice feedback | Continue to practice opened item 1 with feedback policy stated. Submitting A showed Not correct and kept the item. Open the next hint exposed only the tier 0 lesson heading while tier 1 remained locked. Submitting B showed Correct and Your answer was recorded. |
| B5: leave and restart | Continue opened item 2, a short response. Your desk showed Resume and Session in progress. After stopping and restarting the daemon on the same port, reload retained those cues. Resume opened the course overview, then Sit the items returned to item 2. |
| B6: pending review | Submitting a synthetic short response showed Recorded, and waiting on a mark. The page stated that the machine does not score it and showed no model answer. The sitting remains active at this item. No marker verdict was invented. |

Resume is a course-overview link followed by Sit the items, not a direct
one-click jump into the pending item. The browser test does not certify visual,
touch, screen-reader, zoom, reflow, or aesthetic acceptance.

## Canonical state and commands

A read-only helper used `daemon.session_index` and `runtime.read_session`
before leaving and after browser resume. Exactly one session existed, with
ID `e041b91e3f664ca39a59967b0ea082d7`, cursor 1 and selection `[0, 2, 1]`.
The comparison asserted equality of ID, cursor, selection, responses and status.
Both recorded item-1 attempts survived unchanged. After the short response,
the canonical score was `null`, cursor remained 1, and status remained active.
This is helper evidence supplementing the browser journey.

Exact commands, run from the repository root:

```sh
python3 /tmp/itembank-a4-pa5a5g/setup.py
python3 itembank.py daemon /tmp/itembank-a4-pa5a5g/workspace --no-open --port 0
python3 /tmp/itembank-a4-pa5a5g/check.py save
python3 itembank.py daemon /tmp/itembank-a4-pa5a5g/workspace --no-open --port 49936
python3 /tmp/itembank-a4-pa5a5g/check.py compare
python3 /tmp/itembank-a4-pa5a5g/check.py current > /tmp/itembank-a4-pa5a5g/final-session.json
python3 scripts/preflight.py > /tmp/itembank-a4-pa5a5g/preflight.log 2>&1
```

The first daemon was stopped with Ctrl-C before restarting. Setup and helper
scripts, the fixture workspace, baseline fingerprints and captured output live
in `/tmp/itembank-a4-pa5a5g`. These are disposable local evidence, not committed
fixtures. Preflight also uses its own standard temporary directories internally.

## Original integration gate, historical

One full `python3 scripts/preflight.py` ran to completion with exit 1.
All 123 Python files were invoked. The only named Python failure was
`tests/course_ops_roundtrip.py`. Its captured output ended after the route
parity assertion without a traceback or final failure detail. The full run
also failed the expected dirty-tree gate. The ten fast gates and JS gate
passed. Four-subject review was invoked and was not listed as a failure in
this run. This does not establish availability of every external backend.
The two CI-only steps were not performed.

Because the course-ops failure was a new integration concern, one narrow
rerun was justified and run:

```sh
python3 tests/course_ops_roundtrip.py > /tmp/itembank-a4-pa5a5g/course-ops-rerun.log 2>&1
```

It exited 1 with six failures:

```text
FAIL: route acceptance produced 2 operation journal entries, not one
FAIL: CLI acceptance produced 2 operation journal entries, not one
FAIL: CLI migration settlement acceptance produced 2 operation journal entries, not one
FAIL: CLI settlement operation id names more than its one CAS entry
FAIL: route migration settlement acceptance produced 2 operation journal entries, not one
FAIL: route settlement operation id names more than its one CAS entry
COURSE OPS: 6 failure(s)
```

F1, open integration check: `journal._commit_impl` now attributes the prepared
intent and applied record to the same agent operation so interrupted work can
be recovered. `director.operation_entries` explicitly returns every historical
entry. Course-ops assertions at lines 1040, 1145, 1853 and 1906 count these
records as separate acceptances or require a single history row. The likely
repair is to assert one applied acceptance plus its linked prepared intent,
while retaining the exact-undo checks. This is an evidence-based diagnosis,
not an implemented or independently reviewed repair. Owner: A1 recovery/test
integration. `tests/course_ops_roundtrip.py` was outside A4's named lane files,
so no test weakening or production-history filtering was applied.

F2, expected: the clean gate fails because authorized lane changes remain
uncommitted. Owner: original coordinator and user. Revisit only with explicit
Git authorization. A fingerprint comparison after preflight found no change
to pre-existing production, prototype, test, or report bytes. Only shared
STATE/index differences, if any, are allowed by that check. The full-preflight
result remains failed even if F1 is later repaired. No second full run occurred.

## Reconciliation, review and recovery

A1 recovery and independent-review evidence remains owned by
[the recovery report](recovery-repair-2026-09-12.md). A2's prior HTTP/helper resume
gate now has the additional B5 browser and canonical-state evidence above.
A5's actual download equality and runtime checks remain the evidence in
[the export report](../../../prototypes/learning-treatments/README.md#studio-table-export-2026-09-12).
A4 reused those focused checks and did not repeat their full lane suites.
A3 remains [a proposal](durable-reading-contract-2026-09-12.md), including D3.
Its earlier independent review predates D3. No durable reading format is
accepted or implemented by this run.

No independent A4 reviewer was required or spawned. The single integration
owner inspected this artifact and the bounded live results. Large modules were
sampled around existing test/setup and route symbols, not read exhaustively.
This is not another repository audit. The vision reading was limited to the
source-to-course and learner-note intent, plus the binding contract opening and
workflow authority sections.

A4 changes only this report, the priorities index, and the active STATE pointer.
All pre-existing production and test edits are preserved. No stage, commit,
push, branch switch, reset, real-course edit, or external-service write occurred.
Recovery is to remove only A4's report and its added index/STATE reconciliation
hunks after checking ownership. The synthetic daemon is stopped at completion.
Temporary evidence can be discarded later without any learner-data migration.

NEXT ACTION: the coordinator assigns A1 a bounded course-ops assertion
reconciliation using F1 and its exact-undo gate. A3/D3 remains a separate
user-review decision before any durable reading implementation. Human and real-course acceptance remain
deferred under their existing gates. No successor task is created.


## Corrected-candidate follow-up, 2026-09-12

The original coordinator authorized resuming this A4 task after A1's bounded
course-ops patch. A1 stopped before inspection. No new task was created.
A4 inspected the actual complete test diff and matched its SHA256:
`eaab1cface7ef735f7c77abd6e4c84ef22a077f55ef61da0c31311405c36ab9f`.
The assertion requires one prepared and one applied record with distinct IDs,
chronological order, a correct `resolves_entry` link and equal transaction
fields. Negative fixtures reject duplicate applied records, missing intent,
wrong linkage and misattribution. Route and migration helpers preserve exact
byte restoration and repeat-undo no-op checks. CLI reversal identifies the
applied entry and preserves original valid bytes. Production was unchanged.
A4 did not rerun the browser because this test-only patch introduced no browser
behavior concern. The earlier browser evidence and reading limits stand.

This corrective patch justified the expressly authorized second full run:

```sh
python3 scripts/preflight.py > /tmp/itembank-a4-pa5a5g/preflight-corrected.log 2>&1
python3 tests/file_fault_tracer.py > /tmp/itembank-a4-pa5a5g/file-fault-rerun.log 2>&1
```

Full preflight exited 1 after invoking all 123 Python files. Ten fast gates and
JS passed. Course-ops was no longer a failure, resolving F1 on this candidate.
Two Python files failed:

```text
== tests/file_fault_tracer.py
FAIL: two_file_pair scenario 1 left a temp file behind: ['one.md.locator.json.tmp']
== tests/four_subject_review.py
FAIL: a parity run did not succeed: 'ok' / 'unavailable'
```

F3, open recovery defect: the isolated file-fault rerun also exited 1 with the
same leftover temporary locator. Inspection found `journal._write_bytes_atomic`
writes `path + ".tmp"` without exception cleanup. The partial-write injection
at the paired locator leaves that temporary file behind. The tracer checks
previously accepted Markdown/locator bytes and absence of a new sidecar before
this assertion, so this observation proves leaked temporary output, not loss
of those accepted bytes. Later scenarios are not certified by the failing
rerun. Owner: A1 recovery, through the original coordinator. Next gate is the
existing file-fault tracer after a bounded cleanup repair, plus affected
journal/source-adapter checks. A4 made no production repair.

F4, separate backend gate: four-subject parity again returned `ok / unavailable`.
It passed its listed synthetic scenarios, but the overall test failed.
Owner: the existing parity/backend owner through the coordinator. Do not hide
this failure or infer backend availability from the earlier non-failing run.

F2 remains expected: the clean gate failed because lane work is uncommitted.
It is not evidence of a code failure and does not authorize staging or commits.
The two CI-only steps and all human/real-course acceptance remain unperformed.
No third full run occurred in this follow-up. The first failed run remains
historical, and the second failed run is the current candidate result.

A4 changed only this report, the shared index and active STATE pointer. It
inspected the assertion diff and relevant atomic-write/fault-test symbol
windows, not whole production modules. Recovery of documentation edits uses
only A4's appended sections and active pointer hunks, preserving older evidence.
Raw logs remain in the private temporary root. The original coordinator was
notified of the repeatable new recovery failure.

NEXT ACTION: coordinator assigns A1 the bounded F3 temporary-file cleanup
repair and its existing fault-injection gate. A3/D3 remains a separate user
review decision. Stop this follow-up without another task or feature expansion.


## Final cleanup-candidate validation, 2026-09-12

The coordinator authorized A1's exclusive cleanup repair and this final A4
validation after A1 stopped writing. A4 inspected the exact helper and new
regression test. The temporary path is unique and created with exclusive `xb`
mode. Ownership is set only after successful open. Cleanup removes only that
owned temporary path and never the durable target. Name collisions are refused
without removing another file. The tests inject write, flush, fsync, replace
and after-replace failures and preserve unrelated temporary files. Permission
errors continue to identify the durable target. The unchanged file-fault
tracer still injects the paired locator partial write.

Complete candidate SHA256 values were checked before and after validation:

| File | SHA256 |
| --- | --- |
| `journal.py` | `e19bce1f89556931ee4f5660c524d751eb567e27d83a8589c20ba243d4a9b6c4` |
| `tests/journal_roundtrip.py` | `5322197088c6de45526fc705ab29d9a7193acf1ded1f6aaa8b0348cf59418121` |
| `tests/course_ops_roundtrip.py` | `eaab1cface7ef735f7c77abd6e4c84ef22a077f55ef61da0c31311405c36ab9f` |

The shared atomic-write helper change justified this third full run. Each
follow-up was authorized after a concrete corrective patch. No unchanged
candidate was repeatedly run to seek green.

```sh
python3 scripts/preflight.py > /tmp/itembank-a4-pa5a5g/preflight-cleanup-corrected.log 2>&1
shasum -a 256 journal.py tests/journal_roundtrip.py tests/course_ops_roundtrip.py
git diff --check
```

Full preflight completed with exit 1. All 123 Python files were invoked.
The only named Python failure was:

```text
== tests/four_subject_review.py
FAIL: a parity run did not succeed: 'ok' / 'unavailable'
```

F1 course-ops and F3 file-fault cleanup are resolved on this final candidate.
File-fault, journal, director, course-ops, course-resume, source-adapter and
other Python checks were not failures. Ten fast gates and the JS gate passed.
F4 is the known deferred local-model parity availability gate. F2 is the
expected dirty working tree with no Git mutation authority, not a code failure.
The full command remains failed and is not reported as repository-wide green.
The prior two failed full runs remain historical evidence above.

The completed actual-browser journey remains applicable. No practice UI,
scoring or disclosure behavior changed in this cleanup patch. A4 did not replay
the browser or self-certify human acceptance. A3/D3 and the observed missing
reading persistence/note controls retain their prior status. Hard-kill and
power-loss temporary cleanup remain outside this exception-cleanup evidence.
Cleanup permission failure remains an error, as described in A1's report.

A4 changed only this integrated report, the shared index and active STATE
pointer. A1 owned both corrective patches and its recovery report. No staging,
commit, push, branch switch, real data changes, parity work, successor task or
A3 implementation occurred. Final diff-check passed. The browser and synthetic
daemon remain closed. Local temporary logs and the per-write fingerprint
journal remain in `/tmp/itembank-a4-pa5a5g` for inspection.

NEXT ACTION: the coordinator returns the bounded result to Weibao with F4's
known parity limit and F2's expected dirty-tree condition. Further parity work,
Git operations, durable reading implementation and human acceptance retain
separate authority. This A4 chain is complete within its bounded scope and
stops without another successor.
