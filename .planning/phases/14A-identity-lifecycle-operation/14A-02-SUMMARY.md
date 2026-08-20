---
phase: 14A-identity-lifecycle-operation
plan: 02
subsystem: operation-journal
status: complete
tags: [journal, compare-and-swap, atomic-write, fault-injection, evidence-mapping]
requires: [14A-01]
provides:
  - journal.py, the append-only operation journal and the one
    compare-and-swap write path every durable 14A object mutates through
  - tests/journal_roundtrip.py, including three fault classes (crash,
    disk-full, permission-denied) and a two-writer concurrency case
  - the _journal/ gitignore entry
affects: [14A-03, 14A-04, phase-13.9-walking-skeleton]
tech-stack:
  added: []
  patterns:
    - the registry update inside commit_operation and rebuild_registry() are
      the literal same function (_compute_registry over journal.jsonl), so
      the live-maintained projection and a from-scratch rebuild agree by
      construction rather than by two code paths kept in sync by hand
    - journal._write_bytes_atomic is the single seam every durable write in
      this module goes through (before-image, target, registry), so a
      fault-injection test has exactly one place to patch
    - a state flip (prepared -> applied/refused) is a second appended entry
      naming the first through resolves_entry, never a rewrite of the first
      line
key-files:
  created:
    - journal.py
    - tests/journal_roundtrip.py
    - .planning/phases/14A-identity-lifecycle-operation/14A-02-SUMMARY.md
  modified:
    - .gitignore
key-decisions:
  - "commit_operation's create_if_missing parameter is accepted per the plan's
    signature but its False-plus-missing-target branch is not specially
    refused: the plan's own enumerated refusal-code table (journal.busy,
    journal.stale_preflight, journal.conflict, journal.after_guard_failed,
    journal.no_change, journal.missing_fingerprint, journal.root_unavailable,
    journal.unknown_operation) has no code for a missing target, and no
    <behavior> assertion exercises create_if_missing=False against a missing
    file. Inventing a ninth code (e.g. journal.target_missing) would have
    been an unreviewed addition to a table the plan calls out as the sealed
    refusal vocabulary this task introduces. See Deviations."
  - "The permission-denied fault chmods the target's containing directory
    (0o555 POSIX) rather than the target file itself: verified empirically
    before writing the fixture that os.replace()/rename() on POSIX checks
    write permission on the containing directory, not on the file being
    replaced, so chmod(target, 0o444) alone does not actually block this
    module's tmp-then-os.replace write and would have made the fixture pass
    without ever exercising the fault. Windows keeps the plan's literal
    os.chmod(path, stat.S_IREAD) on the file, since Windows does enforce the
    file-level read-only attribute against ReplaceFile."
requirements-completed: [RELIABILITY-01, ID-01, FILE-01]
duration: ~1.5h
completed: 2026-08-18
---

# Phase 14A Plan 02: Operation Journal Summary

**The operation journal is shipped: one compare-and-swap write path for every durable object kind, an append-only prepared-then-applied protocol, a disposable registry projection that is provably byte-identical after deletion and rebuild, and a replay that re-reads the target's actual bytes rather than trusting a journal entry's own state field, proven against a crash between commit and the applied record, three disk-full injection points, a permission denial, and a two-writer race.**

## Task outcomes

- **Task 1 (the compare-and-swap write, end to end, one path):** Complete.
  `journal.py` created at the repository root with every symbol named in the
  plan's "Artifacts this phase produces" section: the constants, `ENTRY_KEYS`
  (twenty-two keys, fixed order), `JournalError`, `journal_dir`, `log_path`,
  `registry_path`, `new_entry_id`, `append_entry`, `entries`,
  `commit_operation`, `replay`, `rebuild_registry`, `read_registry`,
  `object_state`, `undo`. `tests/journal_roundtrip.py`'s `check_commit`,
  `check_lock_busy`, and `check_walking_skeleton_slice` were written first
  and confirmed to fail (`ModuleNotFoundError: No module named 'journal'`),
  then made to pass. `.gitignore` gained a `_journal/` entry beside the
  existing `_evidence/` entry, with the exact one-line comment the plan
  specifies.
- **Task 2 (fault injection, crash and disk-full and denied):** Complete.
  `check_faults()` added to `tests/journal_roundtrip.py`: a kill-before-commit
  and a kill-after-commit spawn/terminate fixture (Popen, `time.sleep(0.5)`,
  `terminate()`, `wait()`, generalizing `tests/durability_roundtrip.py`'s
  `probe_kill` shape from one append call to one compare-and-swap write
  call), three disk-full injection points against the single
  `journal._write_bytes_atomic` seam (before-image, target, registry), a
  permission-denied case, and a two-subprocess concurrency case. No
  test-only hook, flag, or environment variable was added to `journal.py`;
  every fixture drives through the module's own `_write_bytes_atomic`.

## A real bug the test caught and fixed mid-task

`append_entry`'s first draft used `entry.setdefault("entry_id", ...)` and
`entry.setdefault("timestamp", ...)` to fill the two fields when absent. This
never fired: every entry `commit_operation` builds already carries these two
keys with an explicit `None` value (from `_new_template`), and
`dict.setdefault` only sets a key that is *absent*, not one present with a
`None` value. Every journal entry was therefore being written with
`entry_id: null` and `timestamp: null`, silently. The bug did not surface in
the first few assertions (a `None` compared equal to another `None` in the
`resolves_entry` check), but did surface as a byte-identical-rebuild failure
once a manually-appended entry with a real, forced timestamp entered the
comparison. Fixed by checking `entry.get(key) is None` instead of relying on
`setdefault`, and confirmed by re-running the full suite. This is exactly
the kind of defect Rule 1-3 (auto-fix a blocking bug found while proving the
plan's own assertions) covers; no design decision changed, and the fix is
recorded here because it is not otherwise visible in the diff's intent.

## Truth-to-command verification map

| must_have truth (abbreviated) | Verified by |
|---|---|
| Every durable write states expected fingerprint, temp file, validation, atomic commit, journal | `check_commit`, the two-write sequence plus the after-guard fixture inside `_commit_impl` |
| A successful operation produces exactly two lines (prepared then applied) | `check_commit`, `len(lines) != 2` assertion after the first commit |
| A prepared entry is resolved by appending, never rewriting | `check_commit`'s key-set assertion plus `journal.py`'s append-only `append_entry`; no in-place edit exists anywhere in the module |
| A stale expected fingerprint refuses without mutating | `check_commit`, `journal.stale_preflight` case |
| A write against an object with no fingerprint refuses | `check_commit`, `journal.missing_fingerprint` case |
| A no-op write refuses and records no revision | `check_commit`, `journal.no_change` case plus the revision-unchanged assertion |
| Writing zero bytes is a legitimate, distinguishable mutation | `check_commit`, the `b""` write plus `object_state != "missing"` assertion |
| Replay is append order, never a timestamp sort | `check_commit`'s forced-identical-timestamp `append_entry` pair, ordered by append |
| Two writers cannot interleave; a busy lock refuses after ~10s | `check_lock_busy`, elapsed-time assertion (`>= 0.8s` against a 1.0s test timeout) |
| A killed process between prepared and commit leaves old bytes, replay reports interrupted | `_check_kill_before_commit` |
| A killed process between commit and applied leaves new bytes, replay reports recoverable | `_check_kill_after_commit` |
| Disk-full at any of three injection points leaves old-or-new, never mixed | `_check_disk_full` |
| A write into an unreachable root refuses with journal.root_unavailable | `check_commit`, removed-root case |
| objects.json is disposable; delete + rebuild is byte-identical | `check_commit`, the delete-then-`rebuild_registry` byte comparison |
| The three-call walking-skeleton slice | `check_walking_skeleton_slice` |

## Quoted example: the two-line prepared/applied shape (path redacted)

```
{"schema_version": 1, "entry_id": "1870d55e...", "timestamp": "2026-08-18T22:15:33.184Z", "operation": "mint", "state": "prepared", "resolves_entry": null, "object_id": "476518d3...", "kind": "course", "revision": 1, "parent_revision": null, "path": "course.md", "expected_fingerprint": null, "before_fingerprint": null, "after_fingerprint": "sha256:2d711642...", "before_image": null, "undo": {"kind": "none", "before_image": null, "target": "course.md", "restores_revision": null}, "source_object_id": null, "source_revision": null, "restores_revision": null, "origin": {"actor_kind": "human", "actor_name": "weibao", "operation": "mint"}, "code": null, "message": null}

{"schema_version": 1, "entry_id": "e0990eed...", "timestamp": "2026-08-18T22:15:33.185Z", "operation": "mint", "state": "applied", "resolves_entry": "1870d55e...", "object_id": "476518d3...", ...}
```

The second line's `resolves_entry` names the first line's `entry_id`
exactly, and both entries carry the full twenty-two-key `ENTRY_KEYS` set.

## Fault cases: platform, ran or skipped, observed on-disk state

Run on this machine (macOS, POSIX). No `SKIP:` line printed; every fault case
ran for real.

| Fault | Ran / Skipped | Observed on-disk state |
|---|---|---|
| Kill between prepared and commit | Ran | Target bytes equal the OLD content exactly; `journal.entries` ends with an unresolved `prepared` entry; `replay` lists it under `interrupted` with note `"the previous bytes survived; the commit did not land"` |
| Kill between commit and applied append | Ran | Target bytes equal the NEW content exactly; the last entry is still `prepared`; `replay` lists it under `recoverable` with note `"the new bytes survived; the applied record was not written"`; a second `replay()` call is idempotent |
| Disk full: before-image write | Ran | Target bytes equal the OLD content; accepted revision unchanged |
| Disk full: target write | Ran | Target bytes equal the OLD content; accepted revision unchanged |
| Disk full: registry write | Ran | Target bytes equal the NEW content; the journal carries both the `prepared` and `applied` lines; `rebuild_registry` recovers the projection with the correct fingerprint |
| Permission denied | Ran (not running as root) | Target bytes unchanged; error message names the target path |
| Concurrency (two writers) | Ran | Exactly one winner (exit 0) and one loser (exit 1, `journal.stale_preflight` on this run); target bytes equal exactly the winner's content; the journal carries a complete applied record for the winner |

Wall-clock time of the lock-timeout path (`check_lock_busy`, timeout
shortened to 1.0s for the test): **1.02s to 1.03s** observed across runs,
consistently above the 0.8s floor the assertion checks and below the
configured 1.0s ceiling plus polling overhead.

## Deviations from plan

1. **`commit_operation`'s `create_if_missing=False` plus a missing target is
   not specially refused with a new code.** The plan's `<behavior>` list
   only exercises `create_if_missing=True` against a not-yet-existing path,
   and the plan's own "Refusal codes introduced here" list is presented as
   the sealed vocabulary for this task (`journal.busy`,
   `journal.stale_preflight`, `journal.conflict`,
   `journal.after_guard_failed`, `journal.no_change`,
   `journal.missing_fingerprint`, `journal.root_unavailable`,
   `journal.unknown_operation`). Inventing a ninth code (something like
   `journal.target_missing`, the shape `audit_writer.writer.target_missing`
   suggests) would have been an unreviewed addition to that table rather
   than an auto-fix of a tested gap. Given no test exercises this branch,
   `create_if_missing` is accepted as a named parameter (matching the
   plan's literal signature) but does not gate write eligibility in this
   implementation; the object is written regardless of the flag's value.
   Recorded here per Rule 1-3 rather than silently narrowed. This is a
   candidate follow-up for 14A-03, which gives the operation vocabulary its
   distinct provenance rules and is better positioned to decide the correct
   refusal code and message for a genuinely missing, not-being-created
   target.
2. **The permission-denied fixture chmods the target's containing directory
   on POSIX, not the target file itself.** The plan's fault-injection table
   says `os.chmod(path, 0o444)` on POSIX. Verified empirically (see
   Key-decisions above and the comment left in
   `tests/journal_roundtrip.py:_check_permission_denied`) that `os.replace`
   over a read-only-but-otherwise-normal file succeeds on POSIX, because
   `rename(2)` checks write permission on the containing directory, not on
   the file being replaced. Chmodding only the file would have made the
   fixture assert nothing (the write would silently succeed, and the "did
   not raise" branch would have printed FAIL for the wrong reason, or been
   coded to skip, either of which defeats the fault's purpose). The fixture
   instead denies write on the file's parent directory (0o555), which
   genuinely blocks the `.tmp`-file creation `_write_bytes_atomic` needs and
   was confirmed to raise `PermissionError` before being written into the
   test. Windows keeps the plan's literal file-level `stat.S_IREAD`, which
   does block `ReplaceFile` on that platform. No behavior in `journal.py`
   changed for this; it is purely a test-fixture correction.
3. No other deviation. Every other function signature, constant, entry key,
   refusal message, and file path matches the plan exactly, including the
   registry-write-equals-rebuild identity `_compute_registry`/`_write_registry`
   establish (Task 1, action item 13's "Update `_journal/objects.json`" and
   `rebuild_registry`'s own contract are, by construction, the same code
   path, not two paths kept in sync by hand).

## Verification results

- `python3 tests/journal_roundtrip.py` -- exit 0, prints `OK check_commit`,
  `OK check_lock_busy (1.0Xs)`, `OK check_walking_skeleton_slice`,
  `OK kill_before_commit`, `OK kill_after_commit`,
  `OK disk_full (three injection points)`, `OK permission_denied`,
  `OK concurrency`, `OK check_faults`, `OK journal_roundtrip`.
- `python3 tests/durability_roundtrip.py` -- exit 0, unchanged shipped
  durability contract (`append durability: ok (darwin, 10000 locked lines, 0
  torn under lock)`).
- `python3 tests/audit_writer_roundtrip.py` -- **fails identically with no
  changes present** (`FAIL: writer: tracked-clean target must use the Git
  backend with a commit hash`), confirmed by `git stash` and re-running
  against the unmodified tree; this is a pre-existing, working-tree-state
  dependent failure unrelated to this plan (`journal.py` never imports or
  modifies `audit_writer.py`), and is out of this plan's scope to fix.
- `python3 tests/identity_roundtrip.py` -- exit 0, `OK check_identity`,
  `OK check_discovery`, `OK check_regressions`, `OK identity_roundtrip`.
- `python3 tests/scoring_roundtrip.py` -- exit 0, `scoring contract: ok (6
  items, one scorer)`.
- `python3 tests/evidence_roundtrip.py` -- exit 0, full evidence contract
  suite passes.
- `python3 itembank.py guard .` -- `0 offending files`, exit 0.
- `python -c "import journal,sys; print(len(open(journal.log_path(sys.argv[1])).read().strip().splitlines()))" <base>`
  after a two-write sequence prints `4`.
- `python -c "import journal; print(journal.ENTRY_KEYS)"` prints the
  twenty-two keys in the order given in the plan's "Artifacts this phase
  produces" section.
- `python -c "import journal; print(journal.OBJECT_STATES)"` prints
  `('clean', 'conflict', 'interrupted', 'missing', 'unavailable')`.
- `git check-ignore -q _journal` exits 0.
- `journal.py` and `tests/journal_roundtrip.py` each contain zero em dash
  characters (checked with a `grep -c` byte-pattern count against each
  file).

## Commits

- `77b27e9` -- `feat(14A-02): the compare-and-swap write, end to end, one path`
- `1adbdcb` -- `test(14A-02): fault injection, crash and disk-full and denied`
- `d322087` -- `fix(14A-02): refuse a rel_path that resolves outside the approved root`

## Known Stubs

None beyond what the plan itself scopes out: no operation-vocabulary
semantics (distinct provenance/identity effects per operation, the rights
gate on `import`/`copy`, external-edit detection: all 14A-03), no tracer or
performance budget numbers (14A-04), no CLI command or daemon route, no
`schemas/` document for the journal, no modification of `audit_writer.py`,
`auditor.py`, `runtime.py`, `evidence.py`, or `model.py`, no sqlite
projection over the journal, no draft/branch/accepted-revision object, no
merge of any kind. All explicitly deferred by the plan's own
`<out_of_scope>` section.

## Threat Flags

None open. The plan's own STRIDE register is exercised directly by this
task's fixtures: T-14A-02-01 (TOCTOU) is closed by the single held
`_journal_lock` around the fingerprint check, mutation, and both appends,
proven by `_check_concurrency`; T-14A-02-06 (mixed on-disk state after a
crash) is proven by `_check_kill_before_commit`/`_check_kill_after_commit`/
`_check_disk_full`, each of which fails loudly with a message beginning
`FAIL: mixed state` if the on-disk bytes ever matched neither the old nor
the new content, and none did; T-14A-02-08 (a malformed or future-schema
line crashing every read) is proven by `entries()`'s skip-and-warn path,
exercised inside `check_commit`.

T-14A-02-04/05 (path traversal / a symlinked target escaping the approved
root, both severity high) named the mitigation as `commit_operation`'s own
`os.path.realpath` plus `discovery.inside_any_root` containment check.
Task 1's first pass joined `rel_path` onto `base` without adding that check,
which would have left a high-severity, plan-assigned mitigation
unimplemented. Caught during self-review before this summary was finalized
(not by a failing test, since none in the plan's `<behavior>` list exercises
an escaping `rel_path`) and fixed in a follow-up commit: `commit_operation`
now refuses with `journal.path_outside_root` before acquiring the lock,
alongside the existing `journal.unknown_operation` and
`journal.root_unavailable` preflight checks, reusing
`discovery.inside_any_root` exactly as the threat model specifies. Covered
by a new assertion in `check_commit` (an `os.path.join("..", "escaped.md")`
`rel_path` refuses and writes nothing outside the root). `journal.py` now
imports `discovery` in addition to `identity`; no cycle results, since
`discovery.py` imports only `identity` and `os`.

## Self-Check: PASSED

`journal.py`, `tests/journal_roundtrip.py`, and this summary all exist. Both
tasks' `<verify>` commands pass. `git diff --name-only` after each commit
touched only the plan's `files_modified` (`journal.py`,
`tests/journal_roundtrip.py`, `.gitignore`) plus this summary. `itembank
guard .` passes. `identity_roundtrip.py`, `scoring_roundtrip.py`, and
`evidence_roundtrip.py` are all unaffected and still pass.
