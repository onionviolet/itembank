---
phase: 14A-identity-lifecycle-operation
plan: 03
subsystem: lifecycle-operations
status: complete
tags: [journal, operations, rights, conflict, reconciliation, external-edit]
requires: [14A-01, 14A-02]
provides:
  - the six FILE-03 lifecycle operations (link, import, copy, move,
    edit_in_place, supersede) as thin handlers over journal.commit_operation
  - name_hints, copy_candidates_from_registry, duplicate_groups, and
    move_candidates as read-only, path-sorted candidate lists
  - external-edit detection, conflicted reads, and explicit reconciliation
  - the per-operation rights gate on import/copy (identity.rights_state,
    identity.rights_granted, journal's transform-right check)
  - tests/operations_roundtrip.py
affects: [14A-04, 14B]
tech-stack:
  added: []
  patterns:
    - the six operations share one write path (commit_operation /
      _commit_impl); write_target=False (used by op_link and op_supersede)
      records a revision without ever writing the target's bytes, so the
      target's mtime_ns is left untouched
    - the same-id-divergent-bytes conflict check runs unconditionally,
      before expected_fingerprint is ever consulted, so passing the
      on-disk fingerprint can never bypass it; only reconcile() clears it
    - external_edit and reconcile are record types folded through the same
      generic "any applied entry replaces the object's row" registry
      projection every other operation uses, so they must carry the
      unchanged revision/parent_revision/rights forward explicitly or they
      silently corrupt the registry
key-files:
  created:
    - tests/operations_roundtrip.py
    - .planning/phases/14A-identity-lifecycle-operation/14A-03-SUMMARY.md
  modified:
    - journal.py
    - identity.py
key-decisions:
  - "op_move commits to a rel_path that, by construction, is not the
    object's currently recorded path, so before_fingerprint read at the
    new target is not a valid stand-in for 'the object's currently
    accepted state'. _commit_impl now computes a separate
    compare_fingerprint (the registry's own fingerprint) whenever the
    commit's rel_path differs from the object's last recorded path, and
    uses that for the conflict/missing_fingerprint/stale_preflight checks
    instead of the raw on-disk-at-target fingerprint. This was not named
    in the plan's behavior list; without it every op_move call raised
    journal.conflict."
  - "The no_change refusal is now gated on write_target rather than firing
    whenever after_fingerprint == before_fingerprint. op_link and
    op_supersede never change bytes by design (write_target=False), so an
    unconditional no_change check would refuse both of them on every call;
    gating on write_target keeps the check's original behavior for every
    write_target=True caller (all of 14A-02's existing tests) while making
    link and supersede possible at all."
  - "commit_operation/_commit_impl gained three new trailing keyword
    parameters (write_target=True, note=None, rights=None), all
    backward-compatible defaults. write_target=False skips both the
    before-image capture and the atomic target write; note rides in the
    entry's message field (used by op_move to record the previous path);
    rights, meaningful only for kind=='source', defaults to
    identity.rights_default() when omitted and is threaded onto the
    journal entry (ENTRY_KEYS gained a 'rights' key) and the registry row."
  - "op_supersede does not delete or rewrite either object's bytes; it
    commits a bytes-unchanged revision on the superseding object
    (write_target=False) carrying source_object_id=superseded_object_id,
    and _compute_registry's second pass folds that into supersedes on the
    superseding row and superseded_by on the superseded row without
    touching the superseded row's own last content fields."
  - "detect_external_edits and reconcile append a single applied entry
    directly (no prepared phase): both are relationship/decision records,
    not content writes, so the two-phase compare-and-swap protocol that
    guards against a torn content write does not apply to them."
requirements-completed: [FILE-03, ID-02, RIGHTS-01]
duration: ~2h
completed: 2026-08-18
---

# Phase 14A Plan 03: Lifecycle Operations Summary

**The six FILE-03 operations exist as distinct identity and provenance effects sharing one compare-and-swap write path; an external edit is a visible, journaled, idempotent record; a conflicted object still reads with the conflict named and is cleared only by a recorded human reconciliation, never by a lucky argument; and import/copy refuse by name before any mutation when the source's transform right is not exactly "granted".**

## Task outcomes

- **Task 1 (the six operations as one write path with six identity
  effects):** Complete. `op_link`, `op_import`, `op_copy`, `op_move`,
  `op_edit_in_place`, and `op_supersede` added to `journal.py`, each a thin
  handler that mints or looks up an id and calls `commit_operation`
  (through `_commit_impl`) exactly once; none writes a byte, takes a lock,
  or appends a journal line of its own. `name_hints`,
  `copy_candidates_from_registry`, `duplicate_groups`, and
  `move_candidates` added as read-only, path-sorted candidate functions
  that no operation consumes to decide identity.
  `tests/operations_roundtrip.py`'s `check_operations()` proves: each
  handler's `operation` field, `op_link`'s untouched `mtime_ns`,
  `op_import`/`op_copy`'s `source_object_id`/`source_revision` and
  unchanged source row, `op_move`'s kept id and changed path with the
  fingerprint unchanged, `op_edit_in_place`'s kept id and path,
  `op_supersede`'s `supersedes`/`superseded_by` pair with neither row
  removed and `journal.supersede_self` on self-supersede, the corpus's
  duplicate-fingerprint pair surviving as two distinct objects with both
  files intact, the near-identically-named pair minting two ids with
  `name_hints` labelling both `hint: True` and nothing consuming that
  result, two Unicode-normalization-variant names minting two ids and two
  fingerprints, a fabricated `move_candidates` entry with a broken
  revision lineage refusing with `journal.move_lineage_mismatch`, every
  candidate function returning `[]` on an empty registry/empty input,
  stable path-sorted ordering across repeated calls, the skip-and-warn
  read path for an unrecognized log line, and a two-subprocess concurrency
  case where the loser's stderr names `journal.busy`.
- **Task 2 (external-edit states, conflicted reads, explicit
  reconciliation):** Complete. `read_object`, `detect_external_edits`, and
  `reconcile` added to `journal.py`; `RECORD_TYPES` gained `"reconcile"`
  (`OPERATION_TYPES` stays the six FILE-03 names).
  `_commit_impl`'s same-id-divergent-bytes conflict check was moved to run
  unconditionally, before `expected_fingerprint` is ever consulted, so
  passing the on-disk fingerprint as the expected base can no longer clear
  a conflict. `check_external_edits()` proves: `object_state` reports
  `conflict` after an out-of-band edit; `read_object` returns the current
  bytes, `state`, last accepted `revision`, and both fingerprints without
  writing; a write against the conflicted object refuses with
  `journal.conflict` both with the stale accepted fingerprint and with the
  correct on-disk fingerprint; `detect_external_edits` appends exactly one
  record and is idempotent on a second immediate call; `reconcile` refuses
  a fingerprint matching neither side with `journal.stale_preflight` and
  appends nothing, and clears the conflict (`object_state` returns
  `clean`) when given the on-disk fingerprint, after which a normal
  `commit_operation` succeeds again; no function name in `journal.py`
  contains "merge"; and the three named scenarios (move-then-edit,
  edit-both-copies, import-then-source-change) each run and assert their
  final registry/journal state, ending with `entries()` parsing every line
  and `rebuild_registry` reproducing the projection byte-identically.
- **Task 3 (the per-operation rights gate):** Complete. `identity.py`
  gained `RIGHTS_STATES`, `rights_state`, and `rights_granted`.
  `_commit_impl` gates `op_import`/`op_copy` (operations `"import"` and
  `"copy"` with a `source_object_id`): it reads the source's rights from
  the registry snapshot already computed inside the held lock, and on
  anything other than `identity.rights_granted(rights, "transform")`
  refuses with `journal.rights_unknown` before any mutation, using the
  exact message format the plan specifies. `check_rights()` proves:
  `RIGHTS_STATES` is the three-tuple; `rights_state` is `"unknown"` for
  `None`, `{}`, an upper-cased value, and an unrecognized operation name;
  `rights_granted` is `True` only for the exact string `"granted"`; a
  source minted with no `rights` argument carries
  `identity.rights_default()`; import/copy refuse (by name, writing
  nothing) from `"unknown"` and `"denied"` sources and succeed from a
  `"granted"` one; and `op_link`/`op_move`/`op_edit_in_place`/
  `op_supersede` all succeed against a source whose every right is
  `"unknown"`, because none of them pull source bytes into a new owned
  artifact.

## Deviations from plan

1. **Tasks 1-3 were committed together in `journal.py` rather than one
   commit per task.** All three tasks' behavior lives inside the single
   `_commit_impl` function. Task 1's `op_link`/`op_supersede`
   (`write_target=False`) require task 2's `no_change` check to be gated
   on `write_target` (an unconditional check would refuse both of them on
   every call, since neither ever changes bytes) and task 2's
   unconditional conflict check reordering was written as the same edit.
   Task 3's rights gate and the new `rights` entry field also live inside
   the same function body. Committing task 1 in isolation would have left
   `op_link`/`op_supersede` permanently broken (every call refusing with
   `journal.no_change`) until task 2 landed, and there is no intermediate
   state of `_commit_impl` that passes task 1's own `<verify>` command
   without also containing task 2's fix. Splitting the diff after the
   fact, once the whole thing was written and tested together, would only
   reintroduce a broken intermediate state for commit-history cosmetics.
   `identity.py` (task 3's self-contained `rights_state`/`rights_granted`
   addition, no journal.py dependency) is its own commit
   (`5bdcc05`); `journal.py` plus `tests/operations_roundtrip.py` (tasks
   1-3 together) is the second commit (`24e073a`), with the reason
   recorded in that commit's own body as well as here. This is recorded
   per Rule 1-3 (the alternative, a deliberately broken intermediate
   commit, is a worse outcome than one accurately-described combined
   commit).
2. **`op_move` needed a fingerprint-comparison fix not named in the
   plan's `<behavior>` list.** `op_move` commits to a *new* `rel_path`
   that, by construction, does not yet hold the object's bytes: reading
   `before_fingerprint` from that new target (as every other operation
   correctly does, since every other operation targets the object's own
   already-recorded path) returned `None`, which the conflict check then
   compared against the registry's real accepted fingerprint and raised
   `journal.conflict` on every single `op_move` call. `_commit_impl` now
   computes a `moving_to_new_path` flag (`prev is not None and
   prev["path"] != rel_path`) and substitutes the registry's own
   fingerprint (`compare_fingerprint`) for the conflict,
   `missing_fingerprint`, and `stale_preflight` checks whenever that flag
   is true, leaving every other operation's behavior (where `rel_path`
   always equals the object's current path) completely unchanged. Found
   by running the test the plan's own Task 1 `<action>` step 1 requires
   ("Run it and confirm it fails"; the first real failure past the
   expected `ModuleNotFoundError` was this one), and fixed per Rule 1-3
   (a blocking bug the plan's own test surfaced, not a design change:
   `op_move`'s behavior, "keeps the id, the recorded path changes, the
   fingerprint stays unchanged when the bytes did not change," is exactly
   what the fix delivers).
3. **`detect_external_edits` and `reconcile`'s appended entries must
   explicitly carry `revision`, `parent_revision`, and `rights` forward
   unchanged.** `_compute_registry` treats every `applied` entry,
   regardless of `operation`, as the object's complete current registry
   row (this is intentional and existing 14A-02 behavior: it is what lets
   one function serve as both the live-maintained update and the
   from-scratch `rebuild_registry`). The first draft of
   `detect_external_edits` left `revision`/`parent_revision`/`rights` at
   their template default of `None`, which meant a detected external edit
   silently corrupted the object's registry row (a later `commit_operation`
   call crashed on `None + 1`). Fixed by having both `detect_external_edits`
   and `reconcile` explicitly copy the unchanged `revision`,
   `parent_revision`, and `rights` from the row they read before
   appending. `reconcile`'s original draft already did this; only
   `detect_external_edits` needed the fix. Found by running
   `check_external_edits()` per the plan's own TDD instruction and fixed
   per Rule 1-3 (a blocking bug, not a design change).
4. **The `entries` param passed to `move_candidates` is not raw
   `discovery.py` output.** The plan's behavior list describes
   `move_candidates(base, entries)` accepting "a discovery entry," but
   `discovery.py`'s own entries (`root`, `path`, `state`, `size`,
   `fingerprint`, `note`) carry no `object_id`, `revision`, or
   `parent_revision` at all, so there is no way for an unmodified
   discovery entry to make the "revision lineage" claim the fabricated-
   entry test requires exercising. `move_candidates` accepts a
   caller-prepared list of dicts carrying `path`, `fingerprint`, and
   *optionally* `object_id`/`revision`/`parent_revision`: a candidate
   found purely by fingerprint match (no claimed identity) is accepted
   without a lineage check, and a candidate that *does* claim an
   `object_id` is validated against the registry's own recorded
   `revision`/`parent_revision` for that id, raising
   `journal.move_lineage_mismatch` on a mismatch. This is documented in
   the function's own docstring. Recorded here because the plan's wording
   could be read as expecting raw `discovery.py` entries, which the
   existing shape of `discovery.py` (deliberately unmodified by this
   plan, per its `<out_of_scope>`) cannot supply.
5. No other deviation. Every refusal code, message format, and function
   name matches the plan's "Artifacts this phase produces" section.

## A platform-specific test-fixture note (not a code deviation)

The Unicode-normalization test could not place the NFC- and NFD-named
files in the same directory: this machine's filesystem (APFS) silently
normalizes a filename on write, so two names differing only in
normalization form collide onto one directory entry when written side by
side, which would have made the test pass or fail based on filesystem
behavior rather than `identity.py`'s own no-normalization guarantee (the
same guarantee `tests/identity_roundtrip.py`'s `check_identity()` already
proves directly over in-memory bytes, bypassing the filesystem
entirely). `tests/operations_roundtrip.py`'s
`_check_unicode_normalization` places the two variants in separate
subdirectories (`nfc/` and `nfd/`), confirmed empirically to keep both
names genuinely distinct on disk, so the test still proves `op_link`
mints two different ids and two different fingerprints for the two
variants.

## Truth-to-command verification map

| must_have truth (abbreviated) | Verified by |
|---|---|
| Six distinct operations, one write path, own name in the log | `check_operations`, `_check_all_six_names_appear` |
| link/import/copy/move/edit_in_place/supersede identity and provenance effects | `_check_link`, `_check_import_and_copy`, `_check_move`, `_check_edit_in_place`, `_check_supersede` |
| Byte-identical content, different ids -> copy candidate, never merged | `_check_duplicate_pair` |
| Same id divergent bytes -> conflict; same fingerprint different ids -> copy candidate; moved path same id -> move candidate only with intact lineage | `check_external_edits` (conflict), `_check_duplicate_pair` (copy candidate), `_check_move_candidates` (move candidate + fabricated lineage refusal) |
| name_hints is a hint only, never consumed for identity | `_check_near_duplicate_pair` |
| No Unicode normalization | `_check_unicode_normalization` |
| Empty candidate set returns empty, not raise; zero-byte object is legitimate | `_check_empty_candidates`; zero-byte case already covered by `tests/journal_roundtrip.py` |
| Candidate lists are path-sorted and stable | `_check_candidate_ordering` |
| One journal lock serializes all six operations; busy after bounded wait | `_check_concurrent_operations` |
| Conflicted object still reads; refuses every write until reconciled; refusal names the next safe action | `check_external_edits` |
| One external_edit record per divergence, idempotent | `check_external_edits` |
| Reconciliation is explicit, no automatic merge path | `check_external_edits`, `_check_merge_free_scenarios` |
| import/copy require transform=granted; unknown/absent refuses by name | `check_rights` |
| Rights comparison is exact lowercase ASCII, never fuzzy | `check_rights` |
| Rights read inside the held lock at the moment of the operation | backstop; not independently observable from a single-process test, verified by code inspection: the read happens inside `with _journal_lock(base):` in `_commit_impl`, using the same `registry` snapshot already computed under that lock |

## Disposition of the flagged ID-02 unclassified edge

The plan's `<threat_model>` flagged an unclassified edge: whether ID-02's
"hashes never prove authorship or rights" clause imposes an obligation
beyond keeping the fingerprint out of identity and rights decisions, for
example a recorded attestation distinct from the fingerprint.

Disposition: closed here, not deferred. This plan's rights model already
keeps the fingerprint and the rights record on two entirely separate
fields (`rights_state`/`rights_granted` never read a fingerprint, and
`object_fingerprint` never reads a rights record), and no operation in
this module ever infers a rights grant, an author, or a truth claim from
a hash match: a copy candidate is reported as a hint, never as proof of
common authorship or shared rights. No further attestation record is
needed to satisfy ID-02's text as written; if a future phase wants a
recorded rights *grant* (who granted it, when, under what license), that
is RIGHTS-02's `rights grant record`, owned by 14B/15A per this plan's
`<out_of_scope>`, not a gap in ID-02 itself.

## Verification results

- `python3 tests/operations_roundtrip.py` -- exit 0, `OK check_operations`,
  `OK check_concurrent_operations`, `OK check_external_edits`,
  `OK check_rights`, `OK operations_roundtrip`.
- `python3 tests/journal_roundtrip.py` -- exit 0, unchanged from 14A-02:
  `OK check_commit`, `OK check_lock_busy`, `OK check_walking_skeleton_slice`,
  `OK kill_before_commit`, `OK kill_after_commit`, `OK disk_full (three
  injection points)`, `OK permission_denied`, `OK concurrency`,
  `OK check_faults`, `OK journal_roundtrip`.
- `python3 tests/identity_roundtrip.py` -- exit 0, `OK check_identity`,
  `OK check_discovery`, `OK check_regressions`, `OK identity_roundtrip`.
- `python3 tests/scoring_roundtrip.py` -- exit 0, `scoring contract: ok (6
  items, one scorer)`.
- `python3 tests/evidence_roundtrip.py` -- exit 0, full evidence contract
  suite passes (including its own pre-existing unknown-event-type
  skip-and-warn case, unrelated to this plan).
- `python3 itembank.py guard .` -- `0 offending files`, exit 0.
- Full repository sweep (`for t in tests/*.py; do python3 "$t"; done`, run
  without the `timeout` command, which this machine does not have
  installed): only `tests/audit_writer_roundtrip.py` and
  `tests/lti_roundtrip.py` fail, and both were confirmed to fail
  identically on a clean `main` tree via `git stash` before this plan's
  changes (`tests/audit_writer_roundtrip.py`'s failure was already
  recorded as pre-existing and unrelated in the 14A-02 summary;
  `tests/lti_roundtrip.py`'s failure is newly confirmed pre-existing here,
  unrelated to `journal.py`/`identity.py`, which it does not import).
- `journal.py`, `identity.py`, and `tests/operations_roundtrip.py` each
  contain zero em dash characters (checked with a `grep -c` byte-pattern
  count against each file).

## Commits

- `5bdcc05` -- `feat(14A-03): identity.py rights_state and rights_granted`
- `24e073a` -- `feat(14A-03): six lifecycle operations, reconciliation, and the rights gate`

## Known Stubs

None beyond what the plan itself scopes out: no `migrate` operation (routed
to 14B), no CLI command or daemon route for any of the six operations, no
rights-grant record or egress policy beyond the `transform` gate (RIGHTS-02,
14B/15A), no draft/branch object, no user interface for conflict
resolution or history, no change to `model.py`, `runtime.py`, `evidence.py`,
`audit_writer.py`, `surfaces/`, or `schemas/`.

## Threat Flags

None open beyond the plan's own STRIDE register, each row of which is
exercised directly:

- T-14A-03-01 (crafted path hijacking another object's history) --
  `move_candidates` verifies revision lineage before accepting a move,
  `_check_move_candidates`'s fabricated-lineage case.
- T-14A-03-02/03 (silent auto-merge / conflict cleared by a lucky
  argument) -- no merge function exists (`_has_merge_named_function`
  asserts this by name), and the conflict check runs unconditionally
  before `expected_fingerprint` is consulted (deviation 2 above describes
  the fix that also closes this gap for the ordinary edit case).
- T-14A-03-04 (importing/copying without the transform right) --
  `check_rights`.
- T-14A-03-05 (rights read before the lock) -- code-inspection backstop,
  described in the truth-to-command table above.
- T-14A-03-06 (name similarity as identity) -- `_check_near_duplicate_pair`.
- T-14A-03-07 (external edit disappearing from history) --
  `check_external_edits`.
- T-14A-03-08 (supply-chain risk in `difflib`) -- stdlib only, no new
  dependency added by this plan.
- T-14A-03-09 (rights refusal leaking a path) -- accepted per the plan;
  the refusal message names only the source object id and operation, not
  a path, unchanged from the plan's own text.

## Self-Check: PASSED

`journal.py`, `identity.py`, `tests/operations_roundtrip.py`, and this
summary all exist. All three tasks' `<verify>` commands pass. `git diff
--name-only` across both commits touched only `journal.py`, `identity.py`,
and `tests/operations_roundtrip.py` (plus this summary in its own commit).
`itembank guard .` passes. `journal_roundtrip.py`, `identity_roundtrip.py`,
`scoring_roundtrip.py`, and `evidence_roundtrip.py` are all unaffected and
still pass.
