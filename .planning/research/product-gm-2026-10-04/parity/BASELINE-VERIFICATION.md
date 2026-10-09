# Native baseline verification, October 4

Status: source/native synthetic checks released for integration. The initial
five authorized scripts and the separately authorized restore-native follow-up
all exited zero, serially, against identical per-run before/after source
manifests. Native restore copy/reopen/restart now has current proof. No
production/test edits were made. Optional browser legs and representative
human/installed acceptance remain unrun.

## Exact execution and results

Working directory for every command: repository root. Commands used `python3`
and redirected stdout and stderr to the ignored receipt directory
`.reasonix/product-gm-20261004/parity-baseline/`. Full logs are retained there.
Each script's `__main__` was read before execution. Help/artifacts expose an
optional `--browser PATH`; restore exposes `--browser-shots PATH`. No optional
flag was selected. The other two scripts use `unittest.main()`.

| ID; exact command | Current result and tested normal-route task | Log; skipped/unrun limits |
| --- | --- | --- |
| B1; `python3 tests/context_help_native_roundtrip.py > .reasonix/product-gm-20261004/parity-baseline/context-help.log 2>&1` | Exit 0. Native admitted selection, source-span preview, excluded private note, explicitly confirmed synthetic cited CLI answer, status, cancellation and late-result suppression pass. Formal-session/remote-return/unconfirmed-start refusals pass. Fresh daemon reports `help.request_unowned`; durable course/note/evidence tree is unchanged. | `context-help.log`. Browser selection/focus/scroll/320px checks unrun. Test-only contract/transport does not register production source_question or answer Q4. |
| B2; `python3 tests/learner_artifacts_native_roundtrip.py > .reasonix/product-gm-20261004/parity-baseline/learner-artifacts.log 2>&1` | Exit 0. Native start/save/preview/cancel/exact-byte pending submission, later private draft, stale competing save refusal, human mark, mark retraction, unsafe route refusal and fresh-daemon exact sitting/item return pass. Saving produces no response event; submitted Unicode/whitespace bytes remain original. | `learner-artifacts.log`. Optional Chrome flows unrun. Immutable historical rubric/origin-draft provenance remains its separate decision. |
| B3; `python3 tests/restore_workspace_browser_roundtrip.py > .reasonix/product-gm-20261004/parity-baseline/restore-workspace.log 2>&1` | Exit 0. `check_static()` POSTs the normal `/restore` preview, exposes `confirm_private`, names `private.txt` and package losses, preserves source files and creates no destination. | `restore-workspace.log`. Despite script name, copy/reopen/restart and keyboard/browser checks only run with `--browser-shots`; those are unrun in this baseline. No new restore-completion claim. |
| B4; `python3 tests/prior_improvements_native_roundtrip.py > .reasonix/product-gm-20261004/parity-baseline/prior-improvements.log 2>&1` | Exit 0, one unittest. Current retained evidence yields due practice; preview changes no bytes; wrong objective refuses without writes; explicit `start_due` creates one exact-objective practice sitting; repeat start refuses replacing active sitting; fresh daemon resumes its exact session. | `prior-improvements.log`. A `ResourceWarning` reports implicit cleanup of HTTPError 400. Assertion result is OK; the warning is retained, not suppressed. Browser/assistive-technology review unrun. |
| B5; `python3 tests/agent_cancel_retry_roundtrip.py > .reasonix/product-gm-20261004/parity-baseline/agent-cancel-retry.log 2>&1` | Exit 0, five unittests. CLI async ownership, native start/cancel/parent-linked retry/review/accept/undo, local-process cancellation, publish-once acceptance, late success refusal and pinned-base conflict pass. Restart reports unresolved transport; unowned cancellation refuses. | `agent-cancel-retry.log`. Synthetic local processes/adapters; no live paid provider, remote termination assurance, multi-job scheduler or general exactly-once transport claim. |

No test reports skipped cases. Optional browser functions were deliberately
unrun, which is different from a skip reported by unittest. No test command
failed, and no full preflight, app build, LAN probe or wider source suite ran.

## Exact current hashes

`before.sha256` and `after.sha256` cover root production Python, all
`surfaces/*.py`, `schemas/*.json`, the five scripts and their directly imported
native fixture helpers. A textual manifest comparison has no differences.
Both manifests have SHA-256
`e621e6f7f62611201e2991786e45ce195d906d88e512a4ae0422803100c2c67b`.
This confirms bytes at both sampling boundaries; it cannot prove a transient
edit followed by restoration between them. The check was brief and serial.

| Path | SHA-256 at both boundaries |
| --- | --- |
| `tests/context_help_native_roundtrip.py` | `76c15caf0a9aac6b160d02d88077ef5ffad1928a922151ef0adb4bc613f5ea9b` |
| `tests/learner_artifacts_native_roundtrip.py` | `fea68eb81cac571928f72a45f36ec582f912e39e918ee5259e927c8ea5dde7bb` |
| `tests/restore_workspace_browser_roundtrip.py` | `9aa741eef98ba15633b51b6e5f402732a9bb922fbdbb046aa2c12eb96f00fd00` |
| `tests/prior_improvements_native_roundtrip.py` | `0735bf1d12a77bb6c0cb4dc1e3fb01b0221e9bc4937d9b31afa2d94887f71fdb` |
| `tests/agent_cancel_retry_roundtrip.py` | `19fbe0a3eeb5059359f2813b7b679fec6f52929ec2c68760d5c49926246a001a` |
| `surfaces/context_help.py` | `711ba912a6c0139c6ce48cd08662d2bffddb974c649b30689b7c87ca15f7c675` |
| `surfaces/learner_artifacts.py` | `626027207c43f7df57035f0f1925d5d31c44d4fe95a73898d72aedcb7e66ff7b` |
| `surfaces/restore_workspace.py` | `6f9f5949f52d7887c346a1aa1ebe06eb9652d85b6e77376a093ea05ca77cf893` |
| `surfaces/course_ops.py` | `e64b679708f0b390a20fb07aa08aeab5c8a73ac01a2c336f82e8395983dbff4e` |
| `surfaces/course_workbench.py` | `e1de7a5949f19c90689556347c7c8a4f856ec78ca8d8dede5bf5dd3acebe4b5f` |
| `surfaces/agent_operation.py` | `57daafb9f74c2776e0d46138108aa3c8f239215748d6101a0296839632235792` |
| `surfaces/daemon.py` | `d4b20b0b41f30fb7ca2a0b007d854d6b0f0022a6a753f57745193063ff0facd3` |
| `notes.py` | `334e024d2ca19ac0b128f93785a582a6c3ce84d0adcc1fa7309d1bfe8e95c781` |
| `retention.py` | `77a7cdb1bc74e84f1f06bea8a138e353cae1b4ba977ac4d06d724fdee9c131fd` |
| `model_adapter.py` | `405dda9daa4aad195b7f85b84b18ab790d50f66066c1f6dc73d5220c4401f137` |

Full log hashes:

| Receipt | SHA-256 |
| --- | --- |
| `context-help.log` | `f79acbd8cb823f26f104f22d949cbb3af17e103f39c879d511414042323e4951` |
| `learner-artifacts.log` | `f61192c2bd7de98e025a624a8bfc05ceabe980fbf8cef51f78d5f3f052bf8555` |
| `restore-workspace.log` | `de59cc37932137e83dd8b92ff250725b03ba6fceea1cfbed84ff946f824fb489` |
| `prior-improvements.log` | `0871ff6665e005458e1639a4c34beddca5e6ec6c27c1d1a48b18e44609ac183a` |
| `agent-cancel-retry.log` | `4af41b07eff0b79af094bb0a3874170ea34f89f129e1d95d461c2732fac69bf9` |

## Findings, limits and release

No material production defect was reproduced. The due journey's HTTPError
cleanup warning is a test-resource observation, not a failing due-practice
assertion. Its reproduction is the unchanged B4 command above; the report does
not assign a production owner without tracing the helper's cleanup path.

Normal help/original-work/due/cancel-retry paths have current synthetic native
proof at the initial pinned bytes. The follow-up below adds current native
restore copy/reopen/restart proof at its own pinned bytes. Source test success cannot settle Q1-Q4,
submission provenance, root-reference policy, human learning/accessibility,
live companion/provider, packaged or installed delivery. The previous failed
combined/host gate is unchanged by these five successes.

Release: only this report and ignored baseline receipts were added. No
production/test path was edited, no accepted learner artifact was touched,
and no Git action was performed. Integration may consume these exact receipts;
later source changes require the affected gate rather than treating these
hashes as proof of changed bytes.

## B6: separately authorized native restore follow-up

Exact command, at repository root:

`python3 tests/restore_workspace_roundtrip.py > .reasonix/product-gm-20261004/parity-baseline/restore-native.log 2>&1`

Result: exit 0; 15 tests pass; no warnings, failures or skipped tests.
`__main__` was inspected first. Its default is `unittest.main()`. Its internal
`--reopen` branch is exercised by the suite in a fresh subprocess and was not
used as an extra standalone command.

Current task evidence includes:

- `test_restore_and_explicit_read_only_reopen_preserve_original_and_shelf`:
  whole-root copy, exact private bytes, original/shelf preservation, explicit
  reopening and fresh-process unchanged retry.
- `test_native_http_preview_cancel_restore_exact_reopen_and_restart`:
  actual `/restore` preview/cancel/consent/copy and `/restore/open` forms,
  untrusted-origin and missing-consent refusals, exact objective view,
  invalid destination refusal, then daemon restart and exact reopening.
- `test_separate_process_opens_exact_recovered_course_and_preserves_unknown_rights`:
  a daemon rooted at the copied destination serves its shelf/course/Learn/
  Sources routes; restrictive export rights and accepted/private bytes persist.
- Remaining source cases preserve originals on rights/governance/identity/
  immutable-evidence conflict, disk-publication failure, destination race,
  package race and unsupported reading/link variants. Copied workspace
  references retain their explicit review gate; preview does not apply policy.

This closes the baseline's native copy/reopen/restart gap. Browser keyboard,
touch, visual composition and installed delivery remain unrun. It does not
authorize in-place merging or settle root-reference carry policy.

`restore-before.sha256` and `restore-after.sha256` cover root production Python,
all surfaces, schemas, the restore suite and daemon fixture helper. Their
comparison has no differences. Both manifest hashes are
`3dc19215ce11cf89165a6a4617bca7acdcbcc872701ea4bfe27905ed20464cd1`.
The full `restore-native.log` hash is
`4c1cdc37ee14a7ff20d26544cdb0df7916715dc9308c7d10791fb424b7f058c8`.

| Current restore input | SHA-256 at both follow-up boundaries |
| --- | --- |
| `tests/restore_workspace_roundtrip.py` | `6d5dae3b948d6d45e760bab328b8eb10b09ccea15226b725555f2c59ec60d562` |
| `surfaces/course_ops.py` | `e64b679708f0b390a20fb07aa08aeab5c8a73ac01a2c336f82e8395983dbff4e` |
| `surfaces/restore_workspace.py` | `6f9f5949f52d7887c346a1aa1ebe06eb9652d85b6e77376a093ea05ca77cf893` |
| `surfaces/daemon.py` | `d4b20b0b41f30fb7ca2a0b007d854d6b0f0022a6a753f57745193063ff0facd3` |
| `course_package.py` | `3706799d90112c8c8bfb7be2fcec3f2df87eea5aaf165ad379d0addaeeab56ae` |
| `journal.py` | `2508799797a367edaed102beba967374e329eab7299eb36611c325e5d9719372` |
| `workspace.py` | `fbcf8128a91fb1a395773aedb9bc539c891f449bf6a88636f3119f959c32c2f9` |

Source release: report and ignored receipts only. No production or test edit,
additional broad suite, private learner mutation or Git operation occurred.
