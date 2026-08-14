---
phase: 14A-identity-lifecycle-operation
plan: 02
type: execute
wave: 2
depends_on: ["14A-01"]
files_modified:
  - journal.py
  - tests/journal_roundtrip.py
  - .gitignore
autonomous: true
requirements: [RELIABILITY-01, ID-01, FILE-01]
must_haves:
  truths:
    - "Every durable write states an expected base fingerprint, writes to a temporary file, validates the committed bytes, commits atomically with os.replace, and appends to an append-only journal (RELIABILITY-01)."
    - "A successful operation produces exactly two journal lines: a prepared line written before any mutation, and an applied resolution line naming the prepared line's entry_id. A refusal reached inside the lock produces exactly one refused line."
    - "The journal is never truncated, edited in place, or reordered. A prepared entry is resolved by appending a resolution entry that names it, never by rewriting the line (append-only discipline; editor-landscape R7)."
    - "A write whose expected base fingerprint does not match the bytes on disk is refused; the refusal names the two fingerprints and states the next safe action, and nothing on disk changed (RELIABILITY-01, ID-01 degraded clause)."
    - "A write against an object that carries no fingerprint is refused with journal.missing_fingerprint rather than performed blind (ID-01 degraded clause)."
    - "A write whose new bytes are byte-identical to the current bytes is refused with journal.no_change and records no revision, so a history view never shows a revision that changed nothing (RELIABILITY-01 adjacency edge)."
    - "Writing zero bytes over an existing object is a legitimate mutation, journaled normally with a real after fingerprint; empty content is not confused with absent content (RELIABILITY-01 empty edge)."
    - "Journal replay is append order, never a timestamp sort, so two entries written inside the same millisecond replay in the order they were appended (RELIABILITY-01 ordering edge)."
    - "Two writers cannot interleave: the fingerprint check, the mutation, and both journal appends happen inside one held advisory lock, and a second writer refuses with journal.busy after a bounded ten second wait rather than proceeding (FILE-01 concurrency edge)."
    - "A process killed between the prepared append and the commit leaves the old valid bytes on disk, and replay reports the operation as interrupted with the target still at its previous fingerprint."
    - "A process killed between the commit and the applied append leaves the new valid bytes on disk, and replay detects that the target's actual fingerprint equals the prepared entry's after fingerprint and reports the operation as recoverable, naming which of the two states survived."
    - "An injected disk-full error at any of the three injection points leaves the old valid state on disk and the journal readable; no mixed state is ever produced (RELIABILITY-01)."
    - "A write into an approved root that has become unreachable refuses with journal.root_unavailable, and the last recorded index is still readable (FILE-01 degraded clause)."
    - "_journal/objects.json is a disposable projection: deleting it and calling journal.rebuild_registry regenerates a byte-identical file from journal.jsonl alone, so the log is the only source of truth."
    - "A caller can mint a course object with identity.py, append one journal entry with journal.py, and read the recorded revision back, using no course schema, no graph, and no CLI. This is the slice Phase 13.9 stubs course storage over."
  prohibitions:
    - "A conflicting write is never silently overwritten."
    - "The journal is never truncated, rewritten, or reordered; a restore appends forward."
    - "A fault-injection run is never reported as passing when the on-disk state was mixed."
  artifacts:
    - "journal.py at the repository root, a runtime-tier peer of runtime.py and evidence.py"
    - "tests/journal_roundtrip.py"
    - "the _journal/ directory layout: journal.jsonl, objects.json, journal.lock, before/"
    - ".gitignore entry for _journal/"
  key_links:
    - "The prepared entry must be appended BEFORE the mutation. If it is appended after, a crash between the commit and the append leaves an untracked mutation, which is 14A-RESEARCH.md Pitfall 1 and the exact failure the fault fixtures exist to catch."
    - "The journal append happens inside the already-held journal lock, so no second advisory lock and no reliance on O_APPEND atomicity is needed. This is why the Windows bpo-42606 hazard evidence.py documents does not apply here."
    - "journal.py calls identity.object_fingerprint with the object's kind. Passing the wrong kind silently changes whether keyed content is normalized, which is the one way this plan could reintroduce the D-14A-2 masking risk."
---

<objective>
Ship the operation journal and the compare-and-swap write: one write path for
every durable object kind, an expected-base-fingerprint guard, an atomic
temp-then-replace commit, an append-only journal carrying an undo pointer, and
a replay that reports honestly which valid state survived a fault.

Together with 14A-01 this completes the skeleton-enabling slice. Phase 13.9 may
stub course-level storage over `identity.mint_object` plus one
`journal.commit_operation` append (14A-BRIEF.md "Walking-skeleton coupling";
READINESS-AUDIT-14A.md A9). Task 1 is deliberately the thinnest end-to-end path
so that slice exists after one commit.

Decisions already made, cited, never re-derived:

- **RELIABILITY-01** (`REQUIREMENTS.md`): expected-base fingerprint
  compare-and-swap, temporary output, validation, atomic commit, operation
  journal; fault injection yields the old or new valid state, never a mixed
  state.
- **Editor-landscape R2, R3, R7** (`research/phase-16/16-editor-reader-landscape.md`
  section 4): the base fingerprint is stored, not recomputed from history; a
  journal entry names an object plus a revision, not just bytes; restore is a
  new forward operation that names its source revision and never truncates the
  journal.
- **14A-RESEARCH.md Pattern 2 and Pitfall 1**: the mechanism is a
  generalization of the shipped `audit_writer.py`, not a new algorithm. Lift
  the compare-and-swap guard, the prepared-before-mutation manifest, the
  after-fingerprint guard, and the typed refusal codes from it. Do not
  re-derive them.

Decisions this plan makes and locks, so the executor never guesses:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Module name | `journal.py`, root-level peer of `runtime.py` and `evidence.py` | 14A-RESEARCH.md Architectural Responsibility Map places the write-path authority at the runtime tier beside the two modules that already occupy it. |
| Journal location on disk | `<root>/_journal/`, resolved by `journal.journal_dir(base)` as `os.path.join(os.path.abspath(base), "_journal")` | Exactly mirrors the shipped `evidence.evidence_dir(base)` and the `_evidence/` and `_attempts/` precedent: a hidden directory beside the thing it describes, gitignored, never synced. |
| Files inside `_journal/` | `journal.jsonl` (record of truth, append-only, one JSON object per line), `objects.json` (disposable projection), `journal.lock` (advisory lock file), `before/<sha256 hex>` (content-addressed before-images) | `journal.jsonl` follows `evidence.jsonl`; `objects.json` follows the sqlite evidence index's explicitly disposable-projection rule; `before/` follows `audit_writer.py`'s `BEFORE_DIR`. |
| Lock granularity | One advisory lock per journal root, `_journal/journal.lock`, non-blocking acquire with a ten second deadline, following `audit_writer._bank_lock` | This is a single-learner local product with no concurrent-writer requirement. One lock serializes the fingerprint check, the mutation, and both journal appends in one critical section, which closes the time-of-check-to-time-of-use gap for all of them at once. A per-object lock would be more concurrency for no user. |
| Journal state flip | Append-only. A `prepared` entry is resolved by appending a second entry carrying `resolves_entry` and a `state` of `applied` or `refused` | `audit_writer.py` rewrites a per-write manifest file, which it can because each write owns a file. 14A's journal is one shared append-only log, so a state flip must be an append. |
| Entry id shape | `uuid.uuid4().hex`, the full 32 characters | Matches the shipped `evidence.new_event_id()`. Object identity uses the 16-character shape (`model.new_item_id()`); a log entry id uses the 32-character shape. Each new id plays the role its shipped shape already plays. |
| Timestamp | `identity.utc_now()` | One format across the new modules, locked to the shipped `evidence.utc_now()` shape by the assertion in `tests/identity_roundtrip.py`. |
| Refusals inside versus outside the lock | Every refusal reached inside the lock is journaled with `state` equal to `refused`. A `journal.busy` refusal is not journaled | A busy refusal never acquired the lock, so it cannot append safely. Everything else records why it refused, which is what makes the conflict visible on read. |

Purpose: an object that cannot be written safely cannot be owned.
Output: `journal.py`, its roundtrip test including three fault classes, and the
gitignore entry for the journal directory.
</objective>

<context>
@.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md
@.planning/phases/14A-identity-lifecycle-operation/14A-RESEARCH.md
@.planning/phases/14A-identity-lifecycle-operation/14A-PATTERNS.md
@.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md
@.planning/research/phase-16/16-editor-reader-landscape.md
@audit_writer.py
@runtime.py
@evidence.py
@tests/durability_roundtrip.py
</context>

## Artifacts this phase produces (plan 14A-02 share)

`journal.py` public surface:

- Constants: `JOURNAL_SCHEMA_VERSION = 1`, `JOURNAL_DIRNAME = "_journal"`,
  `LOG_FILENAME = "journal.jsonl"`, `REGISTRY_FILENAME = "objects.json"`,
  `LOCK_FILENAME = "journal.lock"`, `BEFORE_DIRNAME = "before"`,
  `LOCK_TIMEOUT_SECONDS = 10.0`, `ENTRY_STATES = ("prepared", "applied",
  "refused")`, `OBJECT_STATES = ("clean", "conflict", "interrupted", "missing",
  "unavailable")`, `ENTRY_KEYS` (the fixed-order key tuple below).
- Exception: `JournalError(Exception)` with `.code` and `.message`.
- Functions: `journal_dir(base)`, `log_path(base)`, `registry_path(base)`,
  `new_entry_id()`, `append_entry(base, entry)`, `entries(base)`,
  `commit_operation(...)`, `replay(base)`, `rebuild_registry(base)`,
  `read_registry(base)`, `object_state(base, object_id)`,
  `undo(base, entry_id, actor_kind, actor_name)`.
- Refusal codes introduced here: `journal.busy`,
  `journal.stale_preflight`, `journal.conflict`, `journal.after_guard_failed`,
  `journal.no_change`, `journal.missing_fingerprint`,
  `journal.root_unavailable`, `journal.unknown_operation`.

Journal entry keys, in this fixed order (`journal.ENTRY_KEYS`):

`schema_version`, `entry_id`, `timestamp`, `operation`, `state`,
`resolves_entry`, `object_id`, `kind`, `revision`, `parent_revision`, `path`,
`expected_fingerprint`, `before_fingerprint`, `after_fingerprint`,
`before_image`, `undo`, `source_object_id`, `source_revision`,
`restores_revision`, `origin`, `code`, `message`.

The `undo` value is a dict with the keys `kind` (`"restore_before_image"` or
`"none"`), `before_image` (relative path under `_journal/before/`, or null),
`target` (path relative to the journal root, or null), and `restores_revision`
(integer or null).

`tests/journal_roundtrip.py`, direct-execution script, exit 0 on pass, with a
`--child` mode used by the kill fixtures the way
`tests/durability_roundtrip.py` uses its `--writer` mode.

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: the compare-and-swap write, end to end, one path</name>
  <files>journal.py, tests/journal_roundtrip.py, .gitignore</files>
  <read_first>
- `audit_writer.py` in full. It is the strongest precedent in this repository:
  read `_bank_lock` and `_try_lock` (lines 48 to 105), `_write_json`,
  `_read_bytes`, `_write_bytes_atomic` (lines 246 to 265), `write_units`'s
  compare-and-swap guard (lines 288 to 322), `_write_shadow`'s
  prepared-manifest-before-mutation, atomic replace, and after-fingerprint
  guard (lines 346 to 402), and the `WriterError` class (line 200).
- `runtime.py` lines 1430 to 1437 (`write_session`, the tmp-then-`os.replace`
  idiom the atomic helpers derive from).
- `evidence.py` lines 1 to 19 (peer-module docstring contract), lines 51 to 55
  (`KNOWN_EVENT_TYPES`), lines 123 to 160 (`locked`), lines 755 to 774
  (`events`, the skip-and-warn-on-unknown read discipline), and lines 1030 to
  1038 and 1126 to 1131 (the disposable-index rule and its rebuild).
- `identity.py` from plan 14A-01, in full.
- `14A-RESEARCH.md` "Common Pitfalls > Pitfall 1", in full.
  </read_first>
  <behavior>
Assertions this task's test section makes, written before the module:

- `journal.journal_dir(base)` equals `os.path.join(os.path.abspath(base),
  "_journal")`.
- A first `commit_operation` on a path that does not exist yet, with
  `expected_fingerprint=None` and `create_if_missing=True`, writes the bytes,
  returns a revision record with `revision == 1` and `parent_revision is None`,
  and appends exactly two lines to `journal.jsonl`: a `prepared` line, then an
  `applied` line whose `resolves_entry` equals the prepared line's `entry_id`.
- Every appended line parses as JSON and its key set equals
  `set(journal.ENTRY_KEYS)`.
- A second `commit_operation` on the same object with the correct
  `expected_fingerprint` returns `revision == 2` with `parent_revision == 1`,
  and the target file's bytes on disk equal the new bytes exactly.
- A `commit_operation` with a wrong `expected_fingerprint` raises
  `JournalError` with code `journal.stale_preflight`, the target file's bytes
  are unchanged, and exactly one `refused` line was appended.
- A `commit_operation` against an object the registry knows, with
  `expected_fingerprint=None`, raises `JournalError` with code
  `journal.missing_fingerprint` and changes nothing.
- A `commit_operation` whose new bytes equal the current bytes raises
  `JournalError` with code `journal.no_change`, appends one `refused` line, and
  records no new revision.
- Writing `b""` over an existing non-empty object succeeds, records a real
  after fingerprint equal to `identity.object_fingerprint(b"", kind)`, and is
  distinguishable in the registry from a missing object.
- `commit_operation` with an operation string outside `journal.RECORD_TYPES`
  raises `JournalError` with code `journal.unknown_operation` before any
  mutation.
- `journal.entries(base)` returns entries in append order. Two entries appended
  with an identical forced timestamp still return in append order, proving
  replay is not a timestamp sort.
- `journal.entries(base)` on a log containing one line with an unrecognized
  `operation` value skips that line, prints a warning to stderr naming the line
  number, and returns the remaining entries, following the shipped
  `evidence.events` discipline. It does not raise.
- `journal.read_registry(base)` after the two successful writes reports
  `revision == 2` and the current fingerprint.
- Deleting `_journal/objects.json` and calling `journal.rebuild_registry(base)`
  produces a file byte-identical to the deleted one.
- `journal.object_state(base, object_id)` returns `"clean"` right after a
  successful write; returns `"conflict"` after the target file is edited on
  disk behind the journal's back; returns `"missing"` after the target file is
  deleted; and returns `"unavailable"` after the whole root is removed.
- `commit_operation` into a base whose directory has been removed raises
  `JournalError` with code `journal.root_unavailable`.
- A second in-process attempt to acquire the lock while it is held raises
  `JournalError` with code `journal.busy` after roughly ten seconds and appends
  no line.
- The walking-skeleton slice: `check_walking_skeleton_slice()` mints a `course`
  object for a file named `course.md` with `identity.mint_object`, commits it
  with `journal.commit_operation` using operation `"mint"`, reads the revision
  back with `journal.read_registry`, and asserts the round trip, using nothing
  else. This is the exact three-call sequence Phase 13.9 depends on.
  </behavior>
  <action>
1. Create `tests/journal_roundtrip.py` first, with its own local `fail(msg)`
   helper printing `"FAIL: " + msg` and exiting 1, a `check_commit()` function
   holding every assertion in `<behavior>`, a `check_walking_skeleton_slice()`
   function, and a `main()` printing `OK journal_roundtrip`. Run it and confirm
   it fails because `journal.py` does not exist.

2. Create `journal.py` at the repository root. Its module docstring restates
   the peer-module contract from `evidence.py` lines 1 to 19 with "operation
   journal" substituted, and states in plain sentences: the journal is the
   durable record of every operation and is append-only; `objects.json` is a
   disposable projection over it and never a second source of truth; the
   journal is not a cache and must be included in any backup story a later
   phase builds; and the append happens inside the already-held journal lock,
   so the Windows `O_APPEND` non-atomicity hazard that `evidence.py` documents
   does not apply. Include a short `Walking-skeleton usage` paragraph naming
   the three-call sequence in `check_walking_skeleton_slice()`. No em dash
   characters.

3. Define the constants named in "Artifacts this phase produces", including
   `RECORD_TYPES = OPERATION_TYPES + ("mint", "restore", "external_edit")`
   where `OPERATION_TYPES = ("link", "import", "copy", "move", "edit_in_place",
   "supersede")`. Plan 14A-03 gives the six operation types their distinct
   provenance and identity effects; this plan only validates membership.

4. Define `JournalError(Exception)` with `.code` and `.message`, the same shape
   as `audit_writer.WriterError`. The exact refusal messages, which are the
   user-visible strings and must be written out verbatim in the code:

   | Code | Message format string |
   |---|---|
   | `journal.busy` | `"another writer holds the journal lock for %s; retry after the running operation finishes"` |
   | `journal.stale_preflight` | `"current fingerprint %s does not match the expected base fingerprint %s; the object changed since this operation was prepared"` |
   | `journal.conflict` | `"object %s has the same id and divergent bytes: on disk %s, last accepted revision %d recorded %s. This is a conflict, not an overwrite. Next safe action: read the object, reconcile the difference by hand, then re-run the operation with the on-disk fingerprint as the expected base."` |
   | `journal.after_guard_failed` | `"the committed bytes of %s fingerprint as %s but the operation expected %s; the journal entry stays prepared and the previous revision is still the last accepted one"` |
   | `journal.no_change` | `"the new bytes for %s are identical to the current bytes; no revision was recorded"` |
   | `journal.missing_fingerprint` | `"object %s carries no fingerprint, so a compare-and-swap write cannot be checked; the write is refused rather than performed blind"` |
   | `journal.root_unavailable` | `"approved root %s is not reachable; the last recorded index is still readable and nothing was written"` |
   | `journal.unknown_operation` | `"%s is not a known journal record type; known types are: %s"` |

5. Implement the lock as `_journal_lock(base)`, a `contextlib.contextmanager`
   copying `audit_writer._bank_lock`'s shape exactly: open the lock file
   `a+b`, seed one newline when empty, non-blocking acquire in a loop with a
   `time.monotonic()` deadline of `LOCK_TIMEOUT_SECONDS`, `time.sleep(0.05)`
   between attempts, raise `JournalError("journal.busy", ...)` on timeout,
   release in a `finally`. Reuse `audit_writer`'s `msvcrt` and `fcntl` branch
   structure; do not invent a third locking primitive.

6. Implement `_write_bytes_atomic(path, raw)` as one module-level function that
   writes `path + ".tmp"`, flushes, `os.fsync`es, and `os.replace`s into place,
   agreeing with `runtime.write_session`'s idiom. It must be called through the
   module (`journal._write_bytes_atomic(...)`) at every mutation site so the
   fault-injection test in Task 2 has exactly one place to patch.

7. Implement `append_entry(base, entry)`: validate `entry["operation"]` against
   `RECORD_TYPES`, fill `schema_version`, `entry_id`, and `timestamp` if
   absent, serialize with `json.dumps(..., ensure_ascii=False, sort_keys=False)`
   in `ENTRY_KEYS` order, and append one line with a single `write` followed by
   `flush` and `os.fsync`. The caller must already hold the lock; state that in
   the docstring.

8. Implement `entries(base)`: read the log line by line, skip and warn on a
   malformed line or an unrecognized `operation`, printing to stderr the exact
   text `"warning  journal line %d skipped: %s"`, and return the surviving
   entries in append order. Never sort.

9. Implement `commit_operation(base, object_id, kind, rel_path, operation,
   new_bytes, expected_fingerprint, actor_kind, actor_name,
   create_if_missing=False, source_object_id=None, source_revision=None)`
   following exactly this sequence, which is `audit_writer.py`'s sequence
   generalized:

   1. Validate `operation` against `RECORD_TYPES`; refuse
      `journal.unknown_operation` before touching anything.
   2. If the journal root's parent directory does not exist, refuse
      `journal.root_unavailable`.
   3. Acquire the lock.
   4. Read the current target bytes if the file exists; compute
      `before_fingerprint = identity.object_fingerprint(raw, kind)`, else
      `None`.
   5. If the registry knows this `object_id` and `expected_fingerprint` is
      None, journal a `refused` entry and raise `journal.missing_fingerprint`.
   6. If `expected_fingerprint` is not None and differs from
      `before_fingerprint`: if the registry's last applied fingerprint for this
      object also differs from `before_fingerprint`, journal a `refused` entry
      and raise `journal.conflict`; otherwise journal a `refused` entry and
      raise `journal.stale_preflight`.
   7. Compute `after_fingerprint`. If it equals `before_fingerprint`, journal a
      `refused` entry and raise `journal.no_change`.
   8. If the target exists, write its bytes to
      `_journal/before/<sha256 hex of the raw bytes>` through
      `_write_bytes_atomic`, and set `before_image` to that relative path.
   9. Append the `prepared` entry, with its `undo` dict populated
      (`kind` `"restore_before_image"` when a before-image exists, else
      `"none"`).
   10. Write `new_bytes` through `_write_bytes_atomic` to the target.
   11. Re-read the target and recompute its fingerprint. If it differs from
       `after_fingerprint`, append a `refused` resolution entry naming the
       prepared entry and raise `journal.after_guard_failed`.
   12. Append the `applied` resolution entry with `resolves_entry` set to the
       prepared entry's `entry_id`.
   13. Update `_journal/objects.json` through `_write_bytes_atomic`.
   14. Release the lock and return the revision record built by
       `identity.mint_object` or `identity.next_revision`.

10. Implement `replay(base)` returning `{"objects": {...}, "interrupted":
    [...], "recoverable": [...], "refused": [...]}`. It walks entries in append
    order, pairs each `prepared` entry with its resolution, and for any
    unresolved `prepared` entry re-reads the target's actual fingerprint: equal
    to `after_fingerprint` means the commit landed and the entry is
    `recoverable`; equal to `before_fingerprint` means the commit did not land
    and the entry is `interrupted`; equal to neither means the object is in
    conflict. The docstring states, in plain sentences, that trusting the
    entry's own state field without re-reading the target would misreport a
    committed write as failed, which is Pitfall 1.

11. Implement `rebuild_registry(base)` regenerating `objects.json` from
    `journal.jsonl` alone, `read_registry(base)`, and `object_state(base,
    object_id)` returning one of `OBJECT_STATES` by the rules in
    `<behavior>`.

12. Implement `undo(base, entry_id, actor_kind, actor_name)`: it restores the
    named entry's before-image as a NEW forward revision, journaled with
    operation `"restore"` and `restores_revision` set to the revision the
    content came from. It never deletes or edits a line. Refuse with
    `journal.conflict` if the target's current fingerprint does not match the
    entry's `after_fingerprint`, reusing the same message and next-safe-action
    wording.

13. Add `_journal/` to `.gitignore` in the same block as `_evidence/`, with the
    one-line comment `# The operation journal is durable local record, never
    repository content.`

14. Re-run the test until green.
  </action>
  <verify>
  <automated>python tests/journal_roundtrip.py</automated>
Expected: prints `OK journal_roundtrip` and exits 0. Degraded states this task
proves: a stale expected fingerprint refuses without mutating; a missing
fingerprint refuses rather than overwriting blind; a removed root refuses and
leaves the recorded index readable; a busy lock refuses by name; an
unrecognized record type in an existing log is skipped with a warning instead
of crashing the read.
  </verify>
  <acceptance_criteria>
- `python tests/journal_roundtrip.py` exits 0.
- After a successful two-write sequence in a temp base,
  `python -c "import journal,sys; print(len(open(journal.log_path(sys.argv[1])).read().strip().splitlines()))" <base>`
  prints `4` (two lines per successful operation).
- `python -c "import journal; print(journal.ENTRY_KEYS)"` prints the
  twenty-two keys in the order given in "Artifacts this phase produces".
- `python -c "import journal; print(journal.OBJECT_STATES)"` prints
  `('clean', 'conflict', 'interrupted', 'missing', 'unavailable')`.
- `git check-ignore -q _journal` exits 0.
- `check_walking_skeleton_slice()` runs inside
  `python tests/journal_roundtrip.py` and passes.
- `journal.py` contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="costly">The twenty-two journal entry keys and the
  two-line prepared-then-applied protocol are the format 14A-03, 14A-04, Phase
  13.9, and the later history view all read. Changing them after the 14A-04
  freeze means migrating recorded journals. The freeze is declared in 14A-04.</reversibility>
  <done>A durable object can be created, updated, refused, replayed, and undone
  through one write path, and Phase 13.9 has the slice it was promised.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: fault injection, crash and disk-full and denied</name>
  <files>tests/journal_roundtrip.py, journal.py</files>
  <read_first>
- `tests/durability_roundtrip.py` in full, especially `run_writer` and
  `spawn_writers` (lines 44 to 63) and `probe_kill` (lines 185 to 239), which
  is the spawn, sleep, `terminate()`, `wait()` shape this task generalizes from
  one append call to one compare-and-swap write call.
- `14A-RESEARCH.md` "Fault-Injection Portability Notes", in full, for the
  per-fault portable approach and the named platform fallbacks.
- `journal.py` as written in Task 1, specifically the fourteen-step sequence in
  `commit_operation` and the single `_write_bytes_atomic` injection point.
  </read_first>
  <behavior>
Assertions this task adds, in a `check_faults()` function:

- **Kill between prepared and commit.** The parent spawns
  `python tests/journal_roundtrip.py --child kill_before_commit <base>
  <object_id>`, sleeps 0.5 seconds, calls `terminate()` and `wait()`. Then:
  the target file's bytes equal the OLD bytes exactly; `journal.entries` ends
  with an unresolved `prepared` entry; `journal.replay` lists that entry under
  `interrupted`; and `replay` names the surviving state in its returned
  `note` string as exactly `"the previous bytes survived; the commit did not
  land"`.
- **Kill between commit and applied append.** The parent spawns
  `--child kill_after_commit`, same timing. Then: the target file's bytes equal
  the NEW bytes exactly; the last entry is still `prepared`;
  `journal.replay` lists it under `recoverable`; and `replay`'s `note` reads
  exactly `"the new bytes survived; the applied record was not written"`.
  Calling `journal.replay` a second time is idempotent and does not mutate the
  target.
- **Disk full, three injection points.** With `journal._write_bytes_atomic`
  monkeypatched to raise `OSError(errno.ENOSPC, "No space left on device")` on
  (a) the before-image write, (b) the target write, and (c) the registry write,
  each case is asserted separately: in (a) and (b) the target's bytes are the
  OLD bytes and the object's last accepted revision is unchanged; in (c) the
  target's bytes are the NEW bytes, the journal carries both the `prepared` and
  the `applied` lines, and `journal.rebuild_registry` regenerates the
  projection so the fault costs nothing durable. In none of the three cases do
  the bytes on disk match neither the old nor the new content.
- **Permission denied.** The target file is made read-only with
  `os.chmod(path, stat.S_IREAD)` on Windows and `os.chmod(path, 0o444)` on
  POSIX. `commit_operation` raises `JournalError` whose `.message` names the
  path, the bytes are unchanged, and the permissions are restored by the test
  before cleanup so `shutil.rmtree` succeeds on Windows.
- **Concurrency.** Two subprocesses each run
  `--child slow_commit <base> <object_id>` at the same time. Exactly one
  succeeds; the other exits non-zero with `journal.busy` or
  `journal.stale_preflight` in its stderr; the target's bytes equal exactly one
  of the two candidate contents, never a mixture; and the journal contains a
  complete record for the winner.
- **Append-order replay.** Two entries appended with an identical injected
  timestamp replay in append order.
- Every fault case asserts explicitly that the on-disk bytes match either the
  old content or the new content, and the test fails with a message beginning
  `"FAIL: mixed state"` if they match neither.
  </behavior>
  <action>
1. Add `check_faults()` and the `--child` dispatch to
   `tests/journal_roundtrip.py`. The `--child` modes are exactly
   `kill_before_commit`, `kill_after_commit`, and `slow_commit`. Each child
   mode reaches the intended window by importing `journal`, wrapping
   `journal._write_bytes_atomic` with a shim that sleeps five seconds at the
   chosen point, then calling `journal.commit_operation` normally. This keeps
   the timing in the test, not in the product code.

2. Do not add any test-only hook, flag, or environment variable to
   `journal.py`. The single module-level `_write_bytes_atomic` is the only seam
   the fixtures need, and it exists for the product's own reasons.

3. Run the fault checks on this machine. Where a platform blocks a case, print
   the exact skip line and skip that case rather than passing silently:
   `"SKIP: read-denial fault (os.chmod cannot deny read on this platform)"`.

4. Run the full suite the way CI runs it and confirm the shipped anchors are
   unchanged.
  </action>
  <verify>
  <automated>python tests/journal_roundtrip.py &amp;&amp; python tests/durability_roundtrip.py &amp;&amp; python tests/audit_writer_roundtrip.py</automated>
Expected: all three exit 0. The degraded-state proof is the whole task: every
injected fault leaves the old valid state or the new valid state on disk, never
a mixed one, and the replay names which of the two survived.
  </verify>
  <acceptance_criteria>
- `python tests/journal_roundtrip.py` exits 0 and its output contains the
  string `OK journal_roundtrip`.
- `python tests/durability_roundtrip.py` and
  `python tests/audit_writer_roundtrip.py` both exit 0, proving the shipped
  durability and writer contracts are unchanged by this plan.
- `check_faults()` contains a separate assertion for each of the six named
  cases (kill before commit, kill after commit, three disk-full injection
  points, permission denied) plus the concurrency case.
- Every fault case's assertion compares the on-disk bytes against both the old
  and the new content and fails with a message beginning `FAIL: mixed state`
  if neither matches.
- `journal.py` gained no test-only flag, hook, or environment variable in this
  task.
  </acceptance_criteria>
  <done>RELIABILITY-01's fault-injection clause is proven on this machine for
  crash, disk-full, and permission-denied, and the journal replay reports
  honestly which valid state survived.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| caller to write path | A caller supplies the target path, the object kind, the expected fingerprint, and the new bytes. |
| filesystem to journal | Another process, a text editor, or a crash can change the target or the log between any two operations. |
| journal file to reader | The log is untrusted input on read: a torn tail line or a future record type must not take the reader down. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14A-02-01 | Tampering | time-of-check-to-time-of-use between the fingerprint read and the `os.replace` | high | mitigate | The fingerprint read, the before-image write, both journal appends, the mutation, and the after-guard all happen inside one held `_journal_lock`, following `audit_writer.py` line 308 and the discipline `evidence.append_line_checked` documents. The concurrency fixture in Task 2 proves two writers cannot interleave. |
| T-14A-02-02 | Tampering | silent overwrite of a divergent object | high | mitigate | Step 6 of `commit_operation` refuses with `journal.conflict` and appends a `refused` entry; the target is never opened for writing on that path. |
| T-14A-02-03 | Repudiation | journal truncation or line rewriting hiding an operation | high | mitigate | The journal is append-only and a state flip is an additional append naming `resolves_entry`; `undo` appends a forward `restore` and never removes a line. `entries` never sorts, so append order is the record. |
| T-14A-02-04 | Tampering | path traversal writing outside the approved root | high | mitigate | `commit_operation` takes a path relative to the journal root, joins it, resolves with `os.path.realpath`, and refuses any resolved target that `os.path.commonpath` does not place inside the root, reusing `discovery.inside_any_root`. |
| T-14A-02-05 | Tampering | symlinked target redirecting a write outside the root | high | mitigate | The same realpath containment check runs after link resolution, so a symlinked target is judged by where it actually lands. |
| T-14A-02-06 | Denial of Service | a mixed on-disk state after a crash | high | mitigate | Prepared-before-mutation plus temp-then-`os.replace` plus the after-guard; the three fault classes in Task 2 assert old-or-new and fail loudly on a mixture. |
| T-14A-02-07 | Denial of Service | a stuck lock file blocking all future writes | medium | mitigate | The advisory lock is released in a `finally` and is an OS-level lock that the kernel drops when the holder dies, so a killed child does not leave a permanent lock. The kill fixtures exercise exactly this. |
| T-14A-02-08 | Denial of Service | a malformed or future-schema journal line crashing every read | medium | mitigate | `entries` skips and warns per line with the exact warning text, following `evidence.events`. |
| T-14A-02-09 | Tampering | supply chain: a third-party locking, journaling, or atomic-write package | high | mitigate | None is added; `os`, `json`, `hashlib`, `msvcrt`, `fcntl`, and `contextlib` are Python 3.11 standard library already used by shipped modules. Absence of a dependency is not itself the mitigation: any dependency added here later must be vendored at a pinned version with a recorded checksum and a named license review, per `PLANNING-DIRECTIVES.md` section 4a. |
| T-14A-02-10 | Information Disclosure | before-images accumulating learner content in the repository | high | mitigate | `_journal/` is gitignored in this plan and `python itembank.py guard .` runs in 14A-04. Before-images live beside the object, never in the repository. |
| T-14A-02-11 | Spoofing | an operation recorded with a forged actor | low | accept | Single local user, no authentication surface exists or is planned (`.claude/CLAUDE.md` Users constraint). `origin.actor_kind` and `origin.actor_name` are honest self-reports, and the acceptance-policy decision D-12.6-4 stays open. |
</threat_model>

<out_of_scope>
- No operation vocabulary semantics. This plan validates the six operation
  names as membership only. Their distinct provenance and identity effects,
  the rights gate on `import` and `copy`, and the external-edit states are plan
  14A-03's.
- No tracer, no performance measurement, no corpus budget numbers. Those are
  plan 14A-04's, and no number measured incidentally here may be recorded as a
  budget.
- No CLI command, no daemon route, no `schemas/` document for the journal.
  `OPERATION-CONTRACT.md` lists a general compare-and-swap write surface under
  "Pending surfaces" and says not to invent commands for it.
- No modification of `audit_writer.py`, `auditor.py`, `runtime.py`,
  `evidence.py`, or `model.py`. `audit_writer.py` is not refactored to use the
  new journal in this phase; 14A-RESEARCH.md "State of the Art" names that as
  out of scope explicitly.
- No sqlite index, cache, or query projection over the journal. If one is ever
  added it must be disposable and rebuildable like `evidence.py`'s index, and
  it is not needed at 14A scale.
- No draft, branch, or accepted-revision object. R1's "open draft revision"
  state is 15B's; 14A ships the revision and journal model it will sit on.
- No merge of any kind, automatic or assisted.
</out_of_scope>

<summary_obligations>
`14A-02-SUMMARY.md` records: the exact fault cases that ran and the ones that
printed a skip line with the platform reason, the observed on-disk state for
each fault (old or new, quoted from the assertion), the wall-clock time of the
lock timeout path, the two-line-per-operation journal shape confirmed by a
quoted example line with any path redacted, which truth was verified by which
command, and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create `.planning/phases/14A-identity-lifecycle-operation/14A-02-SUMMARY.md`
when done.
</output>
