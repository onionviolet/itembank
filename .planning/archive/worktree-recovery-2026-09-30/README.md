# Worktree consolidation, 2026-09-30

The user authorized new continuation chats, cleanup of old worktrees and
integration of completed work into main. The three directories here retain
each old worktree's binary-capable dirty patch, original base commit, exact
dirty-file hashes and every untracked test as data with a `.txt` suffix.
`manifest.json` is the recovery inventory. No real learner data was present
in the tracked/untracked cleanup inventory. Ignored contents were only Python
caches and installed JS dependencies; moving the checkouts to Trash also
preserves those contents locally.

| Old lane | Current disposition |
| --- | --- |
| audited-question-features | Explicit true/false is carried into the current parser, ordinary runtime MC scorer and public schema with strict declaration validation. The old unversioned one-to-one alias is superseded by the current stable-ID `MATCHING` version 1 with `reuse: once`; its original source and tests remain in the recovery patch/data. |
| matching-interaction | The old drag helper is superseded by the current native/rich matching controls, local source-identity guards, recovery and source browser proofs. The old source and original test remain recoverable here rather than replacing the newer controls. |
| ui-audit-details | Five isolated showcase refinements and the scoped native comparison emphasis are integrated without replacing the newer source frame, exact return controls or lineplot fixes. Human preference and accessibility acceptance remain open. |

Recover a historical lane by checking out its recorded base commit into an
explicitly chosen temporary checkout, applying `working-tree.patch`, then
restoring each `untracked/<path>.txt` to `<path>`. Verify every resulting dirty
file against `dirty_files_sha256` before proceeding. Do not apply old whole-file
patches over current production files. Original Git branch references are kept
as history; this cleanup does not blindly merge stale branch implementations.

The main source candidate includes the completed audit, matching/ordering,
course/source, UI, staged and polynomial work from the primary checkout. Source
verification remains separate from the installed app and its active sitting.
The fresh-build hold remains in effect. The current integration record is
`../../research/MAIN-INTEGRATION-2026-09-30.md`.
