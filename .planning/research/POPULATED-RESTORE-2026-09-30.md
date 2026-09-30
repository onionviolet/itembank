# Populated restore admission and remaining publication work, 2026-09-30

Status: safe refusal and exact retry implemented. Full populated-root atomic
merge remains unimplemented. Refusal does not close that capability gate.

## Fault and supported boundary

Default ordinary restore checks known conflicts and then commits each object
and evidence event sequentially into a populated root. A later failure can
expose a partial package. That documented compatibility route remains intact;
per-object journal transactions do not make it a whole-root transaction.

`restore_package(..., require_root_atomic=True)` now admits ordinary populated
destinations only as exact, read-only retries. The default is `False`, preserving
supported legacy merges and their conflict checks. The existing journal
registry, canonical journal fold, `object_state`, identity fingerprints and
evidence history supply validation.
Every supported payload must already have identical bytes and acceptance;
every carried immutable event must already have identical content. Existing
identity/path/disk conflicts and divergent evidence identities remain named
conflicts. A missing object or event produces
`package.atomic_merge_unsupported` before accepted mutation. Its recovery
action is to restore to a new sibling, validate and reopen it, then review
identity and evidence conflicts before a separately authorized merge.

Pinned reads and a second byte check detect observed changes to carried
payloads, journal, registry and evidence during verification. Directory
identity changes produce `package.destination_changed`. An exact retry returns
`publication: unchanged`; a default merge returns `publication: per-object`,
a fresh published root returns `publication: whole-root`, and an internal
private stage returns `publication: private-stage`. These describe publication,
while `complete` continues to describe carried-content coverage. Retry grants
no writer lease and does not claim an atomic snapshot of the whole populated
root. Unrelated files and accepted revisions are neither rewritten nor copied
by this path.

Absent/empty-root staged publication and reading-history transport retain their
existing contracts. The internal `_staging=True` route remains for the course
operation's owner-controlled private stage, not admission of a live root.
No new parser, scorer, identity store, evidence writer or root swap was added.

## Tested primitive admission probe and concrete follow-up proposal

The new `test_directory_swap_probe_leaves_open_evidence_writer_on_old_inode`
uses only fictional temporary roots. It pauses the canonical
`evidence.append_event` after its descriptor and advisory lock are open,
swaps a complete copied directory into the destination, and resumes the append.
The event appears in the retired directory and is absent from the live one.
Even an atomic exchange instead of the probe's two renames would retain that
old descriptor. Today's locks cannot admit populated replacement safely.

The missing authority is a stable publication owner shared by all cooperating
writers before any root-relative path or file descriptor is resolved:

| Owner | Required patch responsibility |
| --- | --- |
| `journal.py` | External, stable root-generation gate around object transactions and journal/registry access; locks inside a swapped root are insufficient. Preserve current CAS and before-images. |
| `evidence.py` | Acquire the same generation gate before opening the evidence descriptor. Reopen after publication and preserve immutable-event/correction validation. |
| `notes.py`, `reading_desk.py` | Join the parent root's generation gate even when notes use a nested journal root. Preserve paired-file recovery and accepted history. |
| `surfaces/session.py` and other accepted writers | Join the same gate before session/path resolution. A session `.lock` inside the old generation cannot authorize writing the new generation. Audit all writers before admission. |
| Publication owner plus `course_package.py` | Under exclusive admission, snapshot the populated generation, stage the union through existing identity/journal/evidence authorities, revalidate the expected base, then use a supported atomic exchange with an external durable intent and retained previous generation. Recovery chooses the old or validated new generation after crash/cancel. |

That proposal is not implemented here. It needs exclusive ownership handoffs,
an inventory of noncooperating writers and readers, supported-filesystem
exchange tests, directory fsync and crash recovery, and stale/conflict refusal.
Platforms without supported publication, and roots with writers that cannot
join the gate, must keep the sibling-restore recovery path. Quiescence guessed
from process absence or an unlocked file is not an admission proof.

## Verification and limits

| Command | Observed result |
| --- | --- |
| `python3 tests/populated_restore_atomicity_roundtrip.py` | Exit 0, 13 tests: pre-mutation refusal; unrelated acceptance preservation; fresh sibling and process reopen; source fingerprints/evidence; missing object/event; divergent object/path/evidence; stale package; cancellation/read failure; racing edit/root replacement; injected write failure; process exit; competing restores; live journal writer; old-descriptor swap probe. |
| `python3 tests/course_package_roundtrip.py` | Exit 0, existing manifest, clean restore, rights, synthetic course-archive containment, evidence and verified-snapshot checks. No application packaging occurred. |
| `python3 tests/reading_package_roundtrip.py` | Exit 0, 14 tests. Existing unclosed-file ResourceWarning remains. |
| `python3 tests/a4_source_recovery_roundtrip.py` | Exit 0, 7 tests. Existing disk-byte/conflict refusal retained. |
| `python3 tests/ordinary_restore_atomicity_roundtrip.py` | Exit 0, 12 tests. The one authorized method proves both the new explicit atomic-request refusal and preserved default merge/conflict behavior. |
| `git diff --check -- course_package.py tests/populated_restore_atomicity_roundtrip.py` | Exit 0. |

Initial probe failures came from retaining the fixture's original dedupe key,
then using incorrect event-field names when deriving a new key. The final
probe uses the shipped dedupe function with `item_id`, `attempt_number` and
`canonical`; it demonstrably appends one distinct fictional event. These were
test-fixture errors, not production defects.

An intermediate ordinary-suite failure exposed a compatibility mistake in the
initial patch: it refused default populated writes. The parent clarified that
the documented per-object merge must remain supported. The final patch adds
the explicit guarantee request and restores that default; both routes pass.

Checks ran on macOS only. Process exit is not a filesystem power-loss test.
Read-only retry detects observed races; it cannot prevent a noncooperating
writer from changing accepted bytes after verification returns. Whole-root
merge, writer coordination, representative human accessibility, packaged app,
installation, release and real learner-data gates were not executed. No full
preflight or push occurred. The installed sitting and fresh-build hold remain.

## Source ownership, fingerprints and recovery

Starting baseline: `b1a96707d668f5d49ebc4838c27ea6d9247fa737`, with startup
release explicitly supplied by the parent. Owned production path:
`course_package.py`. Owned new paths: the test above and this report. The parent
also granted only `test_populated_root_merge_and_conflict_behavior_is_retained`
in `tests/ordinary_restore_atomicity_roundtrip.py`. Other
lanes' prototype directories are preserved. Shared STATE, inventory and
integration documents remain parent-owned. Large modules were sampled by
symbol; this is not a whole-module or whole-vision audit.

| Source path | SHA256 after implementation |
| --- | --- |
| `course_package.py` | `b395e90a6f370bde536f8ddab07ae09b7100353e64df75662deac0a4239785ff` |
| `tests/populated_restore_atomicity_roundtrip.py` | `55b76c73538af76c65a10308357210a93c74b9254d1f9bd5d629ec13fc15a8be` |
| `tests/ordinary_restore_atomicity_roundtrip.py` | `097cbad1e65d1c9dc435a2cfd95d4635ffaa31e367de52a30d51a245613d3a81` |

The one scoped commit is the rollback unit. Reverting it in a separately
authorized task removes the explicit atomic-request seam and publication
labels. Default populated replay retains its partial-publication limitation
with or without this commit; no accepted learner files need recovery from
this lane. Atomic-request refusal leaves the destination untouched. Failed sibling staging
keeps that destination untouched and publishes no sibling. Existing clean-root
hard-exit recovery may retain an owner-only stage; this lane does not delete
another process's stage.
