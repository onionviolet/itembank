# Native restore workspace, October 3

Status: L5 source implementation and scoped native/browser gates passed.
Source ownership released to the coordinator after this record. No commit,
push, build, installation, learner mutation or remote egress occurred.

## Delivered behavior and authority

`surfaces/restore_workspace.py` supplies script-free native preview, consent,
cancel and apply forms. `surfaces/course_ops.py` supplies the importable calling
layer. The coordinator owns `/restore` GET/POST, `/restore/open` POST, shelf
entry, shared planning, direct-course-folder admission and the final broad gate.
The generic course-operation schema and published JSON grammar are unchanged.

Preview addresses a package only by its opaque ID in the serving root's existing
`_packages/<package_id>` namespace. Source selection is an already approved root
index or a course resolved by the existing course authority. A destination is
an approved-root index plus one fresh, bounded folder name. It resolves only to
`<approved-root>/_packages/_restore/<fresh-name>`. No form field grants an
arbitrary filesystem path. An entire root requires another approved destination
root because the destination must stay outside the copied source.

Preview names the exact package, course identity, entire source, destination,
file list, private/unregistered file list, bytes, package losses, rights basis
and recovery action. It changes no accepted object or source file. Existing
package preflight and journal state decide object/path conflicts. The canonical
evidence writer checks immutable identities and logical dedupe in a disposable
probe, not in the original source. Every registered source object needs existing
read/export grants before file capture. Unknown and denied rights remain
restrictive. Unregistered files are conservatively disclosed as private,
including control/history files.

Confirmed apply requires both exact-copy and private-file checkboxes. It checks
expected exact package, source-tree and operation-scope fingerprints. Scope pins
the accepted root list, workspace fingerprint, source directory identity and
destination parent identity. Exact package fingerprints include manifest and
consumed raw payload/evidence bytes, so normalized-content fingerprints cannot
hide a different reviewed package. Verified consumed bytes are frozen into an
existing owner-only `private_stage`, then `restore_merged_copy` stages and
publishes the ordinary union through the existing authorities. The transient
package keeps the original manifest/identity and invents no canonical package
store or IDs. Live package changes after pinning cannot substitute other input
bytes. Source revalidation, links/special-file restrictions, bounded capture,
no-replace publication and conflict refusal remain the primitive's authority.

The destination retains original/private files and source grants. Package-only
objects still arrive with unknown rights, as the package loss report states.
The result names its exact validated course path, course fingerprint and
destination directory identity. The explicit reopen form uses the governed
destination and never resolves its ID back to the original workspace.

The coordinator's native reopen route shows a read-only recovered course
snapshot with objectives, sources and bindings. Its narrow direct-course-folder
entry also permits an ordinary recovered course to reopen in a separate daemon
process. If the copy carries `_ia/workspace.json`, the UI suppresses that broader
CLI instruction and requires review of old approved-root references. The native
exact snapshot remains available. This avoids reopening originals through copied
machine-local references. No sitting starts, evidence score changes or course
enrollment occur merely by reopening.

## Interfaces and coordinator requests

| Interface | Signature or fields |
| --- | --- |
| Native fragment | `restore_workspace.panel(root, result=None, retained=None, action_url='/restore')` |
| Native form apply | `restore_workspace.apply(root, fields, actor_kind='human', actor_name='local learner')`; closed actions `preview`, `restore`, `cancel`. |
| Choices | `course_ops.restore_choices(root)` derives existing package IDs, approved roots and course choices. |
| Preview | `preview_merged_restore(root, package_id, source_choice, destination_root, destination_name)` |
| Apply | `apply_merged_restore(root, package_id, source_choice, destination_root, destination_name, expected_package_fingerprint, expected_source_fingerprint, expected_scope_fingerprint, confirm_copy=False, confirm_private=False, actor_kind='human', actor_name='local learner')` |
| Exact reopen | `reopen_merged_restore(root, destination_root, destination_name, expected_course_id, expected_course_fingerprint, expected_destination_identity)` returns the canonical course document as a read-only view. |
| Reopen form | POST `/restore/open`: only `destination_root`, `destination_name`, `course_object_id`, `course_fingerprint`, `destination_device`, `destination_inode`. |

The coordinator accepted the native routes, loopback/origin protection, shelf
entry and reopening seam. No daemon/schema writer lease was requested or used.
Scope/identity validation remains server-side. Duplicate scalar fields and
authority-shaped fields are refused. Invalid choices remain safely renderable
in refusal responses, without creating a new approved scope.

## Verification receipts

| Exact command | Observed result and evidence |
| --- | --- |
| `python3 tests/restore_workspace_roundtrip.py` | Exit 0, 13 cases. Normal preview/restore/reopen; exact private scope; preview no-write; both consent checks and cancel; path/authority/root refusals; unknown/denied export grants before private reads; stale package/source/governance; immutable object/evidence conflicts; injected disk/publication faults and competing destination; unsupported reading transport and source links; pinned package race; stale reopen identity; native HTTP and origin refusal; no duplicate shelf; daemon restart; fresh-process exact retry; ordinary direct-course process and restrictive unknown package rights; copied workspace-reference review. |
| `python3 tests/merged_copy_restore_roundtrip.py` | Exit 0, 11 existing primitive cases. Reused, not duplicated: links/FIFO, modes, accepted identity/history, cancellation, observed staging races, no-replace collision, hard process exits before/after publication, fresh-process offline retry. |
| `python3 tests/course_ops_roundtrip.py` | Exit 0. Existing operation/CLI/schema/package contracts and refusal/recovery checks remain intact. |
| `ITEMBANK_VISUAL_QA_CHANNEL=chrome python3 tests/restore_workspace_browser_roundtrip.py --browser-shots .reasonix/cross-repo-implementation-20261003/restore-workspace` | Exit 0. Installed Chrome, no browser download. Keyboard preview, both consent toggles, copy and exact reopen at 1280/390/320; scripts disabled at 320; dark at 390; reduced motion configured. Source/private preservation checked. No horizontal overflow at script-enabled widths. Narrow screenshots inspected. Final receipt asserts authority source fingerprints unchanged across the browser run. |
| `python3 -m py_compile surfaces/course_ops.py surfaces/restore_workspace.py tests/restore_workspace_roundtrip.py tests/restore_workspace_browser_roundtrip.py` | Exit 0. |
| `git diff --check -- surfaces/course_ops.py surfaces/restore_workspace.py tests/restore_workspace_roundtrip.py tests/restore_workspace_browser_roundtrip.py` | Exit 0. Actual added restore family and new panels/tests inspected; pre-existing asynchronous agent-operation edits preserved. |

Local browser evidence: `.reasonix/cross-repo-implementation-20261003/restore-workspace/receipt.json`,
`preview-1280.png`, `preview-390.png`, `preview-320.png`, `reopened-1280.png`,
`reopened-390.png`, `reopened-320.png`. These are synthetic source-route evidence,
not application packaging or human accessibility acceptance.

Failed runs remain part of the evidence. The first 10-case run failed in the
fixture because it used an unsupported `new_path` argument; the fixture was
simplified to an unrelated accepted lesson. The next run had four errors from
missing temporary payload/evidence parents and a stale recovery-parent preview
reused after injected failure. Temporary parents are now created, and a retry
reviews a new preview when the namespace has changed. The first added direct
process assertion expected literal `Fictional`, although the synthetic course
title is `Meridian Field Response`; it now compares the canonical title. A
subsequent test edit put restart-tail statements in the new method, causing
`NameError`; those statements were restored to the HTTP restart test. These
failed receipts are not relabeled as passes. Final 13-case and source-matched
Chrome runs passed after the corrections. Screenshot review also removed the
panel's duplicate page heading; the shared shell owns that heading.

## Source pins, scope and recovery

Starting HEAD: `28bf561865cf0696a8beb42dd6f356b8bf6ec648`.
Starting dirty `surfaces/course_ops.py` SHA256:
`ecc609225e4c86f801216dddf85d11764f8ce8fc772da49bc2f08e31116b0fc9`.
This lane added imports and the restore family; earlier asynchronous
agent-operation/cancellation/CLI edits in that file were already present.
Large authorities were read by symbol/window. No whole-module or exhaustive
vision audit is claimed.

| Final path | SHA256 |
| --- | --- |
| `surfaces/course_ops.py` | `bd1d5f113e14b007fb9b797849d74018037f459f5a253e81c76a05af2b5a25a7` |
| `surfaces/restore_workspace.py` | `b48acde31e53fff6e25aabad9d915915aca2c5493e0c44d0429b6d2e93637394` |
| `tests/restore_workspace_roundtrip.py` | `4d094de2176ad1c28c7bfd16977b9bd4fcfedf3c1f6389985c2c2fb189a7036e` |
| `tests/restore_workspace_browser_roundtrip.py` | `9aa741eef98ba15633b51b6e5f402732a9bb922fbdbb046aa2c12eb96f00fd00` |
| `surfaces/daemon.py`, coordinator input | `6c65442ce8bfbd405f78eaf3ae59dc94248ab8562ead3a6f2a7debecdc942476` |
| `surfaces/ia.py`, coordinator input | `784ba336dc37fdc3ac8640fdb5a145e2cdf93b88aa5e1dcdc39b8c52a5a4b61a` |
| `course_package.py`, unchanged authority | `3706799d90112c8c8bfb7be2fcec3f2df87eea5aaf165ad379d0addaeeab56ae` |
| `workspace.py`, unchanged authority | `4b38eea15a9c96e430092b0d896185249c1e64cbc2f1afa274661b844010efab` |

Source undo removes only this restore family/imports and the three new source
and test files after inspecting the current diff, never a whole-file reset of
the shared dirty checkout. Keep this evidence record. Native accepted-copy undo
is to move only the named new destination to trash after checking for later
dependencies; the original and package remain. Normal failure/cancel cleans
the call's transient stages. Confirmed failure may retain empty private recovery
namespace directories, which creates no accepted course and requires a fresh
preview if its expected scope changed. Hard process exit can retain an owner-only
stage; this lane never deletes another process's unfinished work.

Operational findings: an immediate scanned course child would create a duplicate
shelf identity even without enrollment, so recovery uses the existing nested
namespace. Same-process `serve_scoped` rewrites shared handler class state,
so separate full course reopening uses a distinct process. Copied workspace
records retain machine-local references and therefore need explicit review
before broader navigation. These findings are retained here for the next owner.

Remaining limits: no in-place root replacement or generation gate; no exclusion
of noncooperating external writers; no filesystem power-loss or cross-platform
certification; no ordinary union of reading-history transport; no automatic
workspace-reference rebinding; no full learning journey on a copied whole
workspace; no human touch/screen-reader/learning acceptance; no app package,
installation or release. The coordinator owns the sole final broad source gate.

## Prior-implementation refinement

The [October 3 continuation](../prior-implementation-improvements-2026-10-03.md)
adds a read-only root-reference proposal to the native restore preview. Current
accepted workspace roots inside the copied source map to the proposed fresh
destination. External roots and their course references are explicitly listed
as requiring reapproval. Neither original nor copied references are changed;
the proposal grants no access and opens no external root.

The 15 native restore checks pass, including exact unchanged source bytes and
the proposed internal/external mapping. Installed-Chrome keyboard copy/reopen
checks pass at 1280/390/320, including script-free 320. The direct choice on
applying internal remapping and disabling external references remains pending.
Existing copy and read-only snapshot behavior retain their original limits.
