# Ordinary clean-root restore atomicity, 2026-09-30

Closes the clean-destination publication part of A4 R2. Ordinary restore previously preflighted known conflicts, then accepted each object directly into the destination. A later object or evidence failure could leave a partial course.

`restore_package` now constructs absent or empty destinations through existing `private_stage`, journal transactions and the one evidence writer. It syncs staged files and directories before existing `publish_directory` performs a no-replace directory rename. A competing destination or a write into the original empty root is preserved. Normal exceptions and cancellation clean temporary stages; publication failure recreates an originally empty destination when no competing destination exists. Reading transport keeps its current implementation.

Populated-root merge behavior is unchanged: existing identity, disk-byte and evidence preflight checks still apply, followed by per-object journal transactions. Whole-root atomic merging into populated destinations needs a separate design for preserving unrelated files and coordinating concurrent writers. This lane does not claim that gate complete.

## Verification and limits

| Source check | Result |
| --- | --- |
| `python3 tests/ordinary_restore_atomicity_roundtrip.py` | Exit 0, 10 tests. Complete journal and evidence before publication; second-object disk failure; evidence failure after objects; publication failure and cancellation; raced publication; raced write before empty-root removal; hard process exit during staging and after publication; clean retry; populated-root conflict preservation; symlink refusal. |
| `python3 tests/course_package_roundtrip.py` | Exit 0. Existing manifest, clean restore, archive containment, rights, evidence and snapshot gates. |
| `python3 tests/reading_package_roundtrip.py` | Exit 0, 14 tests. Existing reading transport and private-note recovery preserved. |
| `python3 tests/a4_source_recovery_roundtrip.py` | Exit 0, 7 tests. Existing source/note and ordinary conflict behavior preserved. |
| `python3 tests/journal_roundtrip.py` | Exit 0. Existing crash, disk-full, permission, concurrency and recovery gates. |
| Scoped `git diff --check` | Exit 0. |

Hard process exit may leave an owner-only `.package-stage-*` directory in the destination parent. Accepted destination contents remain absent, empty or complete, and retry ignores the abandoned stage. Automatic stage deletion is not added: another writer may still own a stage. Process-crash gates do not prove power-loss behavior on every filesystem, and tests ran on macOS only. Existing resource-file warnings remain outside this lane.

The executor inadvertently ran `tests/a5_integrated_package_roundtrip.py` once despite the build hold. It created a temporary archive with SHA256 `364a68eded49cbf36bc9a398eeb6f9ff0a04b9878e6d7536b76a424811299733`, then failed because its copied A3 test tree omitted `course_fixture_17b`. Its temporary directory was cleaned by the existing context manager. No installed app was changed. This is not an accepted package gate, will not be rerun in this lane, and the parent owns any follow-up.

## Ownership and preservation

Owned paths: `course_package.py`, `tests/ordinary_restore_atomicity_roundtrip.py`, this record. All other dirty files were left to their owners. The source baseline SHA256 was `8c46b923bce9f244e2390f2f4477ce89bbd1a688c9984863fdaaf7ffed75bb79`; its dirty bytes and diff were copied to local temporary files before editing. The lane adds only the clean-root dispatcher and extracts the unchanged ordinary replay body into a helper. Large modules were read by symbol windows, not whole-file review. No commit, push, full preflight, real-data mutation or installation occurred. Ownership is released to the integrating parent after the checks above.
