# A1 exact recovery repair, 2026-09-12

Status: implementation and independent bounded review complete. A4 integration pending.

## Scope and baseline

Owner: A1 implements journal, director, and source adapter recovery. The
coordinator owns integration and shared planning pointers. No Git mutations,
real learner data, scorer changes, or other lane edits are authorized here.

The recovery probe reproduced R1, R2, both R3 observations failing and C1
passing. Its zero exit code only means the diagnostic ran.

## Smallest recovery design

D1. Keep the existing journal and its single lock as write authority. Record
creation undo as removal, distinct from restoring an existing empty before
image. Restore records remain append-only. A removed creation leaves no live
registry row, while its history remains available from the journal.

D2. Extend the nested undo descriptor with an optional restored entry identity
and paired-file descriptors. Each paired descriptor names its relative path,
before image, before fingerprint, and after fingerprint. Existing records
remain readable. Source adapters pass validated locator bytes into the journal
commit instead of writing them first. Raw source bytes are never targets.

D3. Validate all target paths and expected states under the journal lock before
any mutation. Persist prepared intent and before images first. Apply each file
atomically. On a caught pre-acceptance failure, restore all changed files to
their exact prior bytes or absence. A hard interruption stays explicitly
unresolved and replay compares every paired file, never only Markdown.

D4. Undo checks journal state and every current file under the same lock.
Repeated undo is a no-op only when the recorded restoration still matches disk
and accepted state. Divergent bytes remain a conflict. An unresolved prepared
mutation can be rolled back from its recorded before images when all files
match a recorded before or after state. Missing or corrupt before images refuse.

D5. Director reverses applied durable writes once, newest first. It includes
creation and refuses or reports incomplete for unsupported or unresolved
durable work. Pure agent intent records remain a successful no-op.

## Gate and reporting

Require all four probe acceptance observations and C1. Regression coverage:
absent versus empty, edits, repeated undo, conflicts, interruption, paired
rollback, registry reconstruction, and applicable offline restore. Run affected
suites and quick preflight. Independent review must inspect the final diff and
rerun the narrow gate. Full integrated preflight belongs to A4.

Evidence, review findings, changed paths, limits, recovery, and one next action
will be recorded here before handoff.

## Independent design review

Astra at low effort reviewed the coupled semantics before implementation.
Concrete refinements accepted: explicit removal descriptors, monotonic revision
allocation from history after removal, applied/prepared deduplication, visible
mixed paired states, exact raw-byte hashes, and validation of all before images
before mutation. An applied append that raises after writing is ambiguous and
must not trigger blind rollback. Registry failure after acceptance preserves
the accepted files. These refinements narrow the design without changing rights
or assessment authority.

## Result and observed verification

R1 and R2 are resolved for new writes and unambiguous legacy creations. Director
includes creation and prepared work, deduplicates resolution pairs, and reports
unsupported durable work as incomplete. Creation undo removes the file. Undo of
an existing empty file restores an existing empty file.

Both R3 observations are resolved for imports made with this repair. Markdown
and locator bytes share one prepared intent and one accepted journal record.
Caught pre-acceptance errors restore prior states. Hard interruptions retain
recovery descriptors and appear as interrupted, recoverable, mixed, or conflict.
Replay itself stays read-only. Raw source bytes remain unchanged. C1 passes.

Changed paths: `journal.py`, `director.py`, `source_adapters.py`,
`tests/journal_roundtrip.py`, `tests/source_adapters_roundtrip.py`, and this
artifact. No identity or schema file changed. The later coordination work also
updates the owning priorities index and active STATE pointer as delegated.

| Gate actually run | Result |
| --- | --- |
| `python3 .planning/research/source-to-reading/recovery_probe.py` | All four acceptance observations and C1 pass. Independently rerun with the same result. |
| `python3 tests/journal_roundtrip.py` | Pass after final production change. Includes existing real subprocess interruption, disk-full, permission and concurrency checks. |
| `check_exact_recovery` in the journal suite | Pass independently after each concrete review correction. Covers absent/empty, edit stack, replay, exact whitespace conflict, accepted append ambiguity, registry failure/rebuild, corrupt paired before-image, paired rollback, copied-root offline undo, pending-work ordering, interrupted director creation and unsupported reversal. |
| `python3 tests/source_adapters_roundtrip.py` | Full existing suite passed on repaired adapter code. Newly added `check_paired_recovery` then passed separately, including raw-byte preservation and pre-commit failure with no added files. |
| `python3 tests/operations_roundtrip.py` | Pass. |
| `python3 tests/agent_operation_roundtrip.py` | Pass, including accepted proposal and two-run undo. Ran before prepared attribution addition, covered afterward by final director/journal gates. |
| `python3 tests/course_package_roundtrip.py` | Pass, including its clean restore and explicit-loss gates. |
| `python3 tests/director_roundtrip.py` | Final pass. Initial run failed its nested evidence HTTP 400 during A2's intermediate scoped-serve regression. |
| `python3 tests/evidence_roundtrip.py` | Pass after A2 repaired scoped-serve recovery. This resolves the nested failure observed above. |
| `python3 scripts/preflight.py --quick` | All ten executed gates pass. Full Python, full JS and clean-tree gates are skipped by quick mode. |
| `git diff --check` | Pass. |

The builder inspected its actual diff and the reviewer inspected the production
diff and recovery tests. Large modules were read by relevant symbols, not in
full. No whole-repository audit is claimed.

## Final independent review

The Astra-low reviewer found F6: reversing an older accepted entry could destroy
the before-state of a newer unresolved prepared write. The fix refuses under
the lock until the named pending write is recovered. Its regression passes.
The builder also found that prepared writes lacked director attribution. The
same operation metadata now accompanies prepared intent, so interruption cannot
disappear from an operation reversal. The reviewer inspected this delta and
reran the narrow regression, returning no remaining blockers. Prepared records
remain unaccepted. No independent review was replaced by the builder's claim.

## Limits and recovery

This restores prior file bytes or absence, not filesystem permissions, symlink
identity, directory cleanup, or arbitrary lifecycle history. Move undo and
metadata-only lifecycle reversal remain unsupported and cannot report complete.
Old import records did not store paired-file fingerprints. This repair does
not invent a locator before-image or silently remove an unverified legacy
sidecar. New imports carry that recovery information.

A hard stop between two file replacements can leave a reported mixed state.
Explicit `journal.undo` of the prepared entry recovers its recorded before
states. No automatic acceptance or hidden second journal is introduced.
If restoration itself fails, the prepared intent remains for explicit recovery.
Caught exceptions after an applied append are treated as potentially accepted,
so files are not blindly rolled back behind the log. Rebuild the disposable
registry when its write failed.

The offline test copies the complete synthetic root, rebuilds its registry,
and restores exact primary and sidecar bytes without the original location.
It does not certify package support for unregistered locator files, power-loss
directory durability, another operating system, or a physical clean machine.
Existing package tests report their own losses. Full integrated preflight and
the supported study journey belong to A4. Human visual, touch, screen-reader,
zoom/reflow, aesthetic and real-course acceptance remain unperformed.

All fixtures use disposable temporary roots. Code rollback means reversing
only A1's listed hunks after checking current ownership. Do not run older code
against new recovery records as a downgrade path. Preserve the journal and its
before images with any learner backup. No Git mutation or real-data migration
was performed.

NEXT ACTION: start the one A4 integration task after reconciled A2 and A5 gates,
using supported reading behavior and labeling A3 persistence unavailable.

## A4 integration follow-up: acceptance-pair assertions

The original coordinator explicitly extended A1 ownership to
`tests/course_ops_roundtrip.py` and this report after A4 stopped. The captured
A4 full preflight failed course operations and the expected dirty-tree gate.
Its isolated rerun exposed six assertions that counted prepared intent and
applied acceptance as two accepted writes. That original failed run remains
historical evidence in the A4 report and is not relabeled passing.

Inspection confirmed the production journal records one prepared intent and
one applied acceptance whose `resolves_entry` identifies that intent. This is
the attribution needed for interrupted director recovery. No production code,
history filter, acceptance authority or scope was changed in this follow-up.

The repaired assertions require exactly one row in each state, distinct entry
identities, correct chronological linkage, and matching object, revision,
path, fingerprints, before-image, undo descriptor and agent attribution.
Negative fixtures reject duplicate applied rows, missing intent, reversed
order, wrong linkage and mismatched operation attribution. Undo must name
exactly the applied entry, restore original valid bytes, and complete a repeat
as a no-op without appending history or changing the restored file. Migration
settlement history must contain only the verified pair.

The first local follow-up run resolved all six integration assertions but
caught a defect in the new negative fixture: its intent and acceptance shared
the same nested agent dict, so mutating one changed both. The fixture now uses
an independent deep copy. This was test-data aliasing, not a production change.

Final `python3 tests/course_ops_roundtrip.py` passed, including route and CLI
acceptance, migration settlement, exact undo and the new negative fixtures.
The directly affected `check_exact_recovery` regression passed. Final quick
preflight passed all ten executed gates with Python/JS/clean skipped. Actual
test diff was inspected and `git diff --check` passed. No further production
change or independent subagent review was needed for this test reconciliation.

A1 has stopped writing. A4 retains shared index and STATE ownership. The
existing A4 task resumes to inspect this exact assertion patch and run final
integrated preflight against the corrected candidate. The earlier failed
preflight remains failed historical evidence. No new task or Git mutation was
made. Rollback is limited to this follow-up's course-ops test hunks and report
addition after checking current ownership.

NEXT ACTION: existing A4 task performs final integrated validation and records
every unexpected failure or expected dirty-tree disposition.

## A4 integration follow-up: atomic temporary-file cleanup

The original coordinator assigned this bounded production repair to A1 after
A4 reproduced `two_file_pair scenario 1 left a temp file behind:
['one.md.locator.json.tmp']`. A1 ran the full file-fault tracer before editing
and reproduced that exact failure. The paired import now uses the journal's
atomic writer, whose former fixed temporary file lacked exception cleanup.

Only `journal._write_bytes_atomic`, its new atomic-cleanup regression in
`tests/journal_roundtrip.py`, and this report changed in this follow-up.
`tests/file_fault_tracer.py` remains unchanged. The helper creates a unique
same-directory temporary file exclusively and records ownership only after
opening it successfully. Its finally block removes only that invocation's
file. A collision refuses without deleting or overwriting the existing file.
The durable target is never removed by cleanup. Write, flush, fsync and replace
failures preserve the old target, while a replace that completed before raising
preserves the new target for the journal's recovery logic.

The first repaired journal run found that the generated filename displaced
the durable target in a permission error. The final helper re-raises such
filesystem errors with the durable path and original exception as cause.
The existing permission-error contract now passes. Both intermediate failures
remain recorded here rather than being omitted from verification history.

| Final gate | Observed result |
| --- | --- |
| `python3 tests/file_fault_tracer.py` | 9 passed, 0 skipped, 0 failed. Unchanged paired scenarios pass. Nested scoring, evidence, audit-writer and durability suites pass. Reflow corpus reports zero false absorptions. Existing report comparison passes without rewriting it. |
| `python3 tests/journal_roundtrip.py` | Pass, including new partial-write, flush, fsync, replace, after-replace and exclusive-collision checks, plus exact paired recovery and existing interruption/concurrency/permission checks. |
| `check_paired_recovery` in source-adapters roundtrip | Pass on final patch. Raw input and prior accepted state preserved. |
| `python3 scripts/preflight.py --quick` | All ten executed gates pass. Full Python/JS/clean skipped. |
| `git diff --check` and actual narrow diff inspection | Pass. No tracer filtering or weakened assertion. |

Final SHA256 values for the complete uncommitted candidate files:
`journal.py`: `e19bce1f89556931ee4f5660c524d751eb567e27d83a8589c20ba243d4a9b6c4`.
`tests/journal_roundtrip.py`:
`5322197088c6de45526fc705ab29d9a7193acf1ded1f6aaa8b0348cf59418121`.

This closes exception cleanup, not process-kill or power-loss cleanup. A hard
kill may leave its uniquely named temporary file. Cleanup never sweeps other
files, and a cleanup permission failure remains an error. The ordering is
bounded to closing the handle then removing the owned temporary path, without
changing acceptance or paired rollback. No unresolved ordering question
required another independent subagent review. A4 will inspect the patch before
final integration. The separately known local-model parity unavailable result
is outside this repair and must retain its own disposition.

A1 has stopped writing. Recovery is to reverse only this helper/test/report
delta after inspecting ownership. No Git mutation, shared index or STATE edit,
new task, real learner mutation, or unrelated parity change occurred.
NEXT ACTION: existing A4 task verifies this final candidate and records all
remaining integrated outcomes without relabeling earlier failed runs.
