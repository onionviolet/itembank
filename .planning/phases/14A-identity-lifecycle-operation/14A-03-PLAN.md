---
phase: 14A-identity-lifecycle-operation
plan: 03
type: execute
wave: 3
depends_on: ["14A-02"]
files_modified:
  - journal.py
  - identity.py
  - tests/operations_roundtrip.py
autonomous: true
requirements: [FILE-03, ID-02, RIGHTS-01]
must_haves:
  truths:
    - "link, import, copy, move, edit_in_place, and supersede are six distinct journal operations sharing one write path, differing only in their identity effect and their provenance effect, and each is recorded under its own name (FILE-03)."
    - "link records a binding to a file where it lives and mints an id without writing the file's bytes; import and copy mint a new id for a new owned artifact and record source_object_id and source_revision; move keeps the id and changes the path; edit_in_place keeps the id and the path and increments the revision; supersede keeps both ids alive and records the superseding id on the superseded object (FILE-03 identity effects)."
    - "Two objects with byte-identical normalized content and two different ids are reported as a copy candidate and are never merged, never given one id, and never written over each other (FILE-03 adjacency edge, ID-02)."
    - "Same id with divergent bytes is refused as journal.conflict; same fingerprint with different ids is a copy candidate; a moved path with the same id is a move candidate that is accepted only after the parent revision lineage checks out, never on the path-and-id pair alone (ID-02)."
    - "Name similarity is only a search hint: journal.name_hints returns near-name matches labelled as hints, and no operation ever consumes that result to decide identity (FILE-03)."
    - "Two paths whose names differ only by Unicode normalization form are two different objects; no NFC or NFD folding is applied anywhere in identity or operation matching (FILE-03 encoding edge)."
    - "An operation over an empty candidate set returns an empty result rather than raising, and an operation on a zero-byte file is a legitimate operation with a real fingerprint (FILE-03 empty edge)."
    - "Candidate lists (copy candidates, move candidates, name hints, and duplicate groups) are returned in path-sorted order, so entries that compare equal on fingerprint still come back in a specified, stable order (FILE-03 ordering edge)."
    - "All six operations serialize through the one journal lock; a second concurrent operation refuses with journal.busy after the bounded wait rather than proceeding (FILE-03 concurrency edge)."
    - "An object whose bytes changed outside the journal reads as conflict, still serves its last accepted state to a reader, and refuses any fingerprint-gated write until it is reconciled; the refusal names the next safe action (ID-02, RELIABILITY-01 degraded clause)."
    - "Detecting an external edit appends one external_edit journal record so the history is honest about a change the journal did not produce, and appending it twice for the same divergence is idempotent (editor-landscape R9)."
    - "Reconciliation is explicit: journal.reconcile records the human's chosen base fingerprint and appends a record; no automatic merge path exists anywhere in the module."
    - "import and copy require the source object's transform right to be the string granted; unknown or absent refuses with journal.rights_unknown naming the operation and the next safe action. link, move, edit_in_place, and supersede operate on owned objects and require no source rights grant (RIGHTS-01)."
    - "Rights operation names are compared as exact lowercase ASCII strings drawn from the closed seven-name tuple; an unrecognized name is treated as unknown and never fuzzy-matched to a known one (RIGHTS-01 encoding edge)."
    - statement: "The rights value is read from the registry inside the held journal lock at the moment of the operation and is never carried across a lock boundary, so a rights change cannot be raced by an in-flight operation."
      verification: backstop
  prohibitions:
    - "Two artifacts are never merged automatically; an ambiguous match is surfaced for human reconciliation."
    - "Name similarity never establishes identity."
    - "An unknown right refuses the operation by name rather than proceeding."
  artifacts:
    - "journal.OPERATION_TYPES and the six operation handlers in journal.py"
    - "journal.name_hints, journal.move_candidates, journal.copy_candidates_from_registry, journal.detect_external_edits, journal.reconcile"
    - "identity.rights_state and identity.rights_granted"
    - "tests/operations_roundtrip.py"
  key_links:
    - "The six operations must share one write path. Six write functions would be six places for the compare-and-swap guard to drift, which is the exact regression 14A-RESEARCH.md Pattern 3 warns about."
    - "A duplicate detector that compares fingerprints without comparing ids first collapses ID-02's three distinct outcomes (conflict, copy candidate, move candidate) into one. The id comparison always comes first."
    - "external_edit is a record type, not an operation type. OPERATION_TYPES stays exactly the six FILE-03 names so a caller can test membership against the frozen vocabulary."
---

<objective>
Give the six operations their distinct identity and provenance effects, make an
external edit visible as a named state rather than silent drift, and gate the
two operations that pull source bytes into a new owned artifact behind the
source's transform right.

Decisions already made, cited, never re-derived:

- **FILE-03** (`REQUIREMENTS.md`): link, import, copy, move, supersede, and
  migrate are distinct operations with distinct identity effects; no automatic
  merge is permitted; name similarity is only a search hint; an ambiguous match
  is surfaced for manual reconciliation, never merged.
- **ID-02** (`REQUIREMENTS.md`): hashes detect change but never prove identity;
  same id with divergent bytes is a conflict; same fingerprint with different
  ids suggests a copy; a moved path with the same id is a move candidate; an
  undecidable case is reported as a conflict for review.
- **RIGHTS-01** (`REQUIREMENTS.md`): rights are operation-specific per source,
  unknown stays unknown and restrictive, finding a file never grants permission
  to transmit or modify it, and an unknown right refuses the unsafe operation
  by name.
- **Editor-landscape R4 and R9**: divergent accept is a conflict state and
  never an auto-merge, reported with both fingerprints so a caller can offer
  re-base or side-by-side; external edits appear as journal-visible events, not
  silent drift.
- **14A-RESEARCH.md Pattern 3**: the six operations are one closed vocabulary
  validated at write time, following `evidence.KNOWN_EVENT_TYPES`, with
  skip-and-warn on an unknown value at read time. They are not six write
  functions.

Decisions this plan makes and locks, so the executor never guesses:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Where the six operations live | Six thin handlers in `journal.py` that each build an operation descriptor and call the one `commit_operation` from 14A-02 | 14A-RESEARCH.md Pattern 3: they differ only in identity and provenance effect, never in the write mechanism. A second write function is the regression. |
| `migrate` in FILE-03's list | Recorded as out of scope for 14A and routed to 14B | The 14A brief names exactly six operations (link, import, copy, move, edit_in_place, supersede). `migrate` in FILE-03's sentence is a schema-migration operation with no schema to migrate until 14B ships the course record. Recorded here so the omission is deliberate, not forgotten. |
| Which operations consume rights | `import` and `copy` only, and both require the source's `transform` right to equal the string `granted` | Those are the only two that pull a source's bytes into a new owned artifact. `link` binds a file where it lives, and `move`, `edit_in_place`, and `supersede` act on objects the course already owns. This is the narrowest defensible gate that still refuses by name. |
| What a conflict state does to a read | The last accepted state is still served, with the state named alongside it | RELIABILITY-01's degraded clause and the 14A brief's own 14A-03 degraded-state test: a conflicted object still reads, the conflict is named, and the next safe action is stated in the refusal. |
| How reconciliation happens | `journal.reconcile(base, object_id, chosen_fingerprint, actor_kind, actor_name, note)` appends a record stating which base a human chose. There is no merge function | The append-only rejection of ambiguous auto-merge (synthesis 12.4) means reconciliation is a recorded human decision, not an algorithm. |
| Supersede semantics | Both objects stay alive. The superseded object's registry row gains `superseded_by`; the superseding object's row gains `supersedes`. Neither is deleted and neither loses its id | The append-only ledger discipline in `PLANNING-DIRECTIVES.md` section 3a applies to artifacts as well as ideas: a superseded thing is never deleted. |

Purpose: without distinct operations, a course silently loses the difference
between a file it borrowed and a file it owns.
Output: the six operations, the external-edit states, the rights gate, and
their roundtrip test.
</objective>

<context>
@.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md
@.planning/phases/14A-identity-lifecycle-operation/14A-RESEARCH.md
@.planning/phases/14A-identity-lifecycle-operation/14A-PATTERNS.md
@.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md
@.planning/REQUIREMENTS.md
@.agents/skills/OPERATION-CONTRACT.md
@evidence.py
@journal.py
@identity.py
</context>

## Artifacts this phase produces (plan 14A-03 share)

Added to `journal.py`:

- `OPERATION_TYPES = ("link", "import", "copy", "move", "edit_in_place",
  "supersede")`, frozen by FILE-03 and unchanged from 14A-02.
- Six handlers, each returning the revision record from `commit_operation`:
  `op_link(...)`, `op_import(...)`, `op_copy(...)`, `op_move(...)`,
  `op_edit_in_place(...)`, `op_supersede(...)`.
- `name_hints(base, name, limit=10)`, `move_candidates(base, entries)`,
  `copy_candidates_from_registry(base)`, `duplicate_groups(base)`.
- `detect_external_edits(base)`, appending one `external_edit` record per newly
  observed divergence and returning the list of affected object ids.
- `reconcile(base, object_id, chosen_fingerprint, actor_kind, actor_name,
  note)`.
- `read_object(base, object_id)` returning `{"bytes": ..., "state": ...,
  "revision": ..., "fingerprint": ..., "accepted_fingerprint": ...}` so a
  conflicted object still reads with its conflict named.
- New refusal codes: `journal.rights_unknown`,
  `journal.move_lineage_mismatch`, `journal.supersede_self`.

Added to `identity.py`:

- `rights_state(record, operation)` returning the string state for one rights
  operation, defaulting to `"unknown"` for an absent record, an empty record,
  or an unrecognized operation name.
- `rights_granted(record, operation)` returning True only when the state is
  exactly the string `"granted"`.
- `RIGHTS_STATES = ("granted", "denied", "unknown")`.

New test file: `tests/operations_roundtrip.py`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the six operations as one write path with six identity effects</name>
  <files>journal.py, tests/operations_roundtrip.py</files>
  <read_first>
- `journal.py` as delivered by 14A-02, in full: `commit_operation`'s fourteen
  steps, `ENTRY_KEYS`, `RECORD_TYPES`, `append_entry`, `read_registry`.
- `identity.py` as delivered by 14A-01, in full: `mint_object`,
  `next_revision`, `copy_candidates`, `registry_rows`.
- `evidence.py` lines 51 to 55 (`KNOWN_EVENT_TYPES`) and lines 755 to 774
  (`events`'s skip-and-warn on an unknown type), the closed-vocabulary
  precedent this task mirrors.
- `.planning/REQUIREMENTS.md` FILE-03 and ID-02, in full, including their
  Fixture sentences.
- `fixtures/corpus_14a.py` from 14A-01, specifically the near-identically-named
  pair and the duplicate-fingerprint pair it builds.
  </read_first>
  <behavior>
Assertions written before the handlers, in `check_operations()`:

- `journal.OPERATION_TYPES` equals `("link", "import", "copy", "move",
  "edit_in_place", "supersede")` and has exactly six members.
- Each of the six handlers appends journal entries whose `operation` field is
  its own name, and the six names appear in the log exactly once each after a
  scripted run of all six.
- **link**: mints a new object id, records the file's current fingerprint and
  path, and does not write the target file. The target's `mtime_ns` is
  unchanged after the operation.
- **import** and **copy**: mint a new object id, write the new owned artifact,
  and record `source_object_id` and `source_revision` on the entry. The source
  object's own registry row is unchanged.
- **move**: keeps the object id, changes the recorded path, increments the
  revision, and leaves the fingerprint unchanged when the bytes did not change.
- **edit_in_place**: keeps the object id and the path and increments the
  revision.
- **supersede**: leaves both object ids in the registry; the superseded row
  gains `superseded_by` and the superseding row gains `supersedes`; neither row
  is removed. Superseding an object with itself raises `JournalError` with code
  `journal.supersede_self`.
- Over the corpus's duplicate-fingerprint pair,
  `journal.copy_candidates_from_registry` returns exactly one pair, in
  path-sorted order, and no operation merges them: after the call both ids are
  still present and both files still exist with their original bytes.
- Over the corpus's near-identically-named pair that differs in bytes,
  `journal.name_hints(base, "notes.md")` returns both paths labelled with the
  key `hint` set to True, and no handler and no candidate function consumes
  that result. Asserted by: minting both files and confirming they receive two
  different object ids.
- Two file names differing only by Unicode normalization form (a precomposed
  accent versus a combining accent) mint two different object ids and produce
  two different fingerprints; `name_hints` may list them, and nothing merges
  them.
- `journal.move_candidates(base, entries)` returns a move candidate only when
  the candidate's recorded parent revision lineage matches the registry's
  lineage for that id; a fabricated entry carrying a known id at a new path
  with a broken lineage is refused with `journal.move_lineage_mismatch` rather
  than accepted as a move.
- `journal.copy_candidates_from_registry(base)`,
  `journal.move_candidates(base, [])`, `journal.name_hints(base, "")`, and
  `journal.duplicate_groups(base)` on an empty registry all return empty lists
  and do not raise.
- Every candidate list is returned in path-sorted order, asserted by calling
  twice with the registry's internal order perturbed between calls.
- A journal written with an operation value outside `RECORD_TYPES` is read by
  `journal.entries` with a skip and the warning line, and by the six handlers
  not at all.
- Two concurrent handler calls from two subprocesses: exactly one succeeds, the
  other exits non-zero with `journal.busy` in its stderr.
  </behavior>
  <action>
1. Write `tests/operations_roundtrip.py` first, with its own local `fail(msg)`
   helper printing `"FAIL: " + msg` and exiting 1, `check_operations()` holding
   every assertion in `<behavior>`, and a `main()` printing
   `OK operations_roundtrip`. It builds the `"1k"` corpus with
   `fixtures.corpus_14a.build_corpus` and tears it down with
   `teardown_corpus`. Run it and confirm it fails.

2. In `journal.py`, add the six handlers. Each one builds its operation
   descriptor and calls the single `commit_operation` from 14A-02. Do not add a
   second write function, a second lock, or a second atomic-write helper. Each
   handler's docstring states its identity effect in one sentence, using this
   exact vocabulary:

   | Handler | Identity effect | Provenance effect |
   |---|---|---|
   | `op_link` | mints a new id for a file that stays where it lives; the bytes are not written | records the linked absolute path and the fingerprint observed at link time |
   | `op_import` | mints a new id for a new owned artifact | records `source_object_id` and `source_revision` |
   | `op_copy` | mints a new id for a new owned artifact | records `source_object_id` and `source_revision` |
   | `op_move` | keeps the id; the recorded path changes | records the previous path in `note` |
   | `op_edit_in_place` | keeps the id and the path | records nothing extra; the revision lineage is the provenance |
   | `op_supersede` | keeps both ids; neither is deleted | records `supersedes` and `superseded_by` on the two registry rows |

3. Implement `name_hints(base, name, limit=10)`. It compares lowercased base
   names with `difflib.get_close_matches` and returns dicts carrying `path`,
   `object_id`, and the literal key `hint` set to True. Its docstring states,
   in plain sentences, that this result is a search hint only and that no
   caller in this module consumes it to decide identity, because a similar name
   never establishes identity (FILE-03, and the name-based-identity rejection
   in synthesis 12.4).

4. Implement `copy_candidates_from_registry(base)` and `duplicate_groups(base)`
   over the registry, both comparing object ids first and fingerprints second,
   and both returning path-sorted results. The docstring states that comparing
   fingerprints without comparing ids first would collapse ID-02's three
   outcomes into one.

5. Implement `move_candidates(base, entries)`: a discovery entry whose
   fingerprint matches a registry row's fingerprint at a different path is a
   move candidate only if the row's revision lineage is intact. Otherwise raise
   `JournalError("journal.move_lineage_mismatch", ...)` with the exact message
   `"path %s carries the id of object %s but its revision lineage does not
   match the recorded one; this is reported as a conflict for review, not
   accepted as a move"`.

6. Add the two new refusal codes with their exact messages:
   - `journal.supersede_self`: `"object %s cannot supersede itself"`
   - `journal.move_lineage_mismatch`: as written in step 5.

7. Re-run the test until green.
  </action>
  <verify>
  <automated>python tests/operations_roundtrip.py</automated>
Expected: prints `OK operations_roundtrip` and exits 0. Degraded states this
task proves: an ambiguous name match is surfaced as a hint and never consumed;
a fabricated move with a broken lineage is refused by name; a duplicate
fingerprint pair survives as two distinct objects with both files intact.
  </verify>
  <acceptance_criteria>
- `python tests/operations_roundtrip.py` exits 0.
- `python -c "import journal; print(journal.OPERATION_TYPES,
  len(journal.OPERATION_TYPES))"` prints the six names and `6`.
- After the scripted six-operation run, the journal log contains each of the
  six operation names at least once, verified by the test's own count
  assertion.
- `journal.py` contains exactly one function that performs a durable mutation,
  namely `commit_operation`; the six handlers call it and perform no write of
  their own. Verified by the test asserting each handler's return value is the
  revision record `commit_operation` produced.
- `journal.py` contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="costly">The six operation names and their identity
  effects are the vocabulary 14B's course record and every later provenance
  view read. They freeze at the 14A-04 tracer.</reversibility>
  <done>Six distinct operations exist, share one write path, and no path in the
  module merges two artifacts.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: external-edit states, conflicted reads, and explicit reconciliation</name>
  <files>journal.py, tests/operations_roundtrip.py</files>
  <read_first>
- `journal.object_state` and `journal.replay` as delivered by 14A-02.
- `.planning/research/phase-16/16-editor-reader-landscape.md` section 4,
  requirements R4, R6, R7, and R9, in full.
- `.planning/REQUIREMENTS.md` ID-02 and RELIABILITY-01, in full.
- `evidence.py` lines 755 to 774, for the read-path degrade-not-crash posture
  the conflicted read must match.
  </read_first>
  <behavior>
Assertions added in `check_external_edits()`:

- After a successful write followed by an out-of-band edit of the target file
  (the test writes the file directly, not through the journal),
  `journal.object_state` returns `"conflict"`.
- `journal.read_object(base, object_id)` on that conflicted object returns the
  current bytes, `state` equal to `"conflict"`, the last accepted revision
  number, and both fingerprints (`fingerprint` for what is on disk,
  `accepted_fingerprint` for the last journaled revision). It does not raise
  and it does not write.
- Any `commit_operation` against the conflicted object, including one carrying
  the last accepted fingerprint as the expected base, raises `JournalError`
  with code `journal.conflict`, and the raised `.message` contains the exact
  sentence `"This is a conflict, not an overwrite."` and the exact sentence
  beginning `"Next safe action: read the object, reconcile the difference by
  hand,"`.
- Passing the on-disk fingerprint as the expected base still refuses until
  `journal.reconcile` has been called, so a conflict is cleared by a recorded
  decision and never by a lucky argument.
- `journal.detect_external_edits(base)` appends exactly one record with
  `operation` equal to `"external_edit"` for that object, returns its id, and a
  second immediate call appends nothing and returns an empty list.
- The `external_edit` record carries `before_fingerprint` set to the last
  accepted fingerprint and `after_fingerprint` set to the observed on-disk
  fingerprint, so a history view can render the divergence honestly.
- `journal.reconcile(base, object_id, chosen_fingerprint, "human", "weibao",
  note)` appends one record, after which `journal.object_state` returns
  `"clean"` and a `commit_operation` carrying the chosen fingerprint succeeds.
- `journal.reconcile` with a `chosen_fingerprint` matching neither the on-disk
  nor the accepted fingerprint raises `JournalError` with code
  `journal.stale_preflight` and appends no reconciliation record.
- No function named with any form of the word merge exists in `journal.py`, and
  no code path combines bytes from two revisions. Asserted by the test
  scripting the edit-both-copies scenario and confirming both copies keep their
  own bytes and both ids after every available operation.
- The three scripted scenarios named in the 14A brief all run: move-then-edit,
  edit-both-copies, and import-then-source-change. Each asserts its final state
  in the registry and in the journal.
- After the whole scenario set, `journal.entries` still parses every line and
  `journal.rebuild_registry` reproduces the projection byte-identically.
  </behavior>
  <action>
1. Add `check_external_edits()` and its assertions to
   `tests/operations_roundtrip.py` first, wired into `main()`. Run and confirm
   it fails.

2. Implement `read_object(base, object_id)` in `journal.py`. It reads the
   target's current bytes, computes the fingerprint for the object's kind,
   reads the registry's last accepted revision and fingerprint, and returns all
   of them plus the state. It never writes, and it serves the bytes even when
   the state is `"conflict"`, because a conflicted object must still read
   (14A-BRIEF.md 14A-03 degraded-state test).

3. Implement `detect_external_edits(base)`. For every registry row whose
   on-disk fingerprint differs from its accepted fingerprint and which has no
   `external_edit` record since its last `applied` record, append one
   `external_edit` record inside the journal lock and collect the object id.
   Return the collected ids. Idempotency is the "since its last applied record"
   clause, and the docstring says so.

4. Make `commit_operation` refuse any write against an object whose state is
   `"conflict"` until a reconciliation record exists, with `journal.conflict`
   and the exact message already defined in 14A-02. Implement this as a state
   check inside the lock, immediately after the fingerprint read, so it cannot
   be bypassed by passing the on-disk fingerprint.

5. Implement `reconcile(base, object_id, chosen_fingerprint, actor_kind,
   actor_name, note)`. It validates that `chosen_fingerprint` equals either the
   on-disk fingerprint or the last accepted fingerprint, refusing with
   `journal.stale_preflight` otherwise, and appends one record with `operation`
   equal to `"reconcile"`. Add `"reconcile"` to `RECORD_TYPES`, keeping
   `OPERATION_TYPES` at exactly six. Its docstring states that reconciliation
   is a recorded human decision and that this module contains no merge
   function, because ambiguous automatic merge is a recorded hard rejection.

6. Re-run the test until green, then run the shipped anchors.
  </action>
  <verify>
  <automated>python tests/operations_roundtrip.py &amp;&amp; python tests/journal_roundtrip.py &amp;&amp; python tests/identity_roundtrip.py</automated>
Expected: all three exit 0. Degraded state proved here: a conflicted object
still reads and serves its last accepted state with the conflict named, and
every write against it refuses with the next safe action stated in the message.
  </verify>
  <acceptance_criteria>
- `python tests/operations_roundtrip.py` exits 0.
- The conflict refusal message asserted by the test contains both exact
  sentences quoted in `<behavior>`.
- `python -c "import journal; print('reconcile' in journal.RECORD_TYPES,
  len(journal.OPERATION_TYPES))"` prints `True 6`.
- `journal.detect_external_edits` called twice in a row appends one record the
  first time and zero the second, asserted by the test.
- The three named scenarios (move-then-edit, edit-both-copies,
  import-then-source-change) each have their own assertion block in
  `tests/operations_roundtrip.py`.
  </acceptance_criteria>
  <done>An external edit is a visible, journaled, named state, a conflicted
  object still reads, and clearing a conflict requires a recorded human
  decision.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the per-operation rights gate</name>
  <files>identity.py, journal.py, tests/operations_roundtrip.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md` RIGHTS-01, in full, including its Fixture
  sentence and the "lands clause C004" note about edition and scope.
- `identity.rights_default`, `identity.RIGHTS_OPERATIONS`, and
  `identity.RIGHTS_UNKNOWN` as delivered by 14A-01.
- `.agents/skills/OPERATION-CONTRACT.md` "Authority vocabulary", specifically
  the sentence stating that rights are operation-specific and unknown rights
  stay restrictive.
  </read_first>
  <behavior>
Assertions added in `check_rights()`, over synthetic sources with differing
per-operation rights including one source with unknown rights:

- `identity.RIGHTS_STATES` equals `("granted", "denied", "unknown")`.
- `identity.rights_state(None, "transform")`,
  `identity.rights_state({}, "transform")`, and
  `identity.rights_state({"transform": "GRANTED"}, "transform")` all return
  `"unknown"`. The third case proves the comparison is exact lowercase ASCII
  and never case-folded or fuzzy-matched.
- `identity.rights_state({"transform": "granted"}, "Transform")` returns
  `"unknown"`: an unrecognized operation name is unknown, never matched to a
  known one.
- `identity.rights_granted(record, op)` returns True only for the exact string
  `"granted"`.
- `journal.op_import` and `journal.op_copy` from a source whose `transform`
  right is `"unknown"` raise `JournalError` with code `journal.rights_unknown`,
  and no file is written, no id is minted, and no `prepared` entry survives
  unresolved.
- The same two operations from a source whose `transform` right is `"denied"`
  raise the same code with the state named in the message.
- The same two operations from a source whose `transform` right is `"granted"`
  succeed.
- `journal.op_link`, `journal.op_move`, `journal.op_edit_in_place`, and
  `journal.op_supersede` all succeed against a source whose every right is
  `"unknown"`, because they do not pull source bytes into a new owned artifact.
- A source object minted with no rights argument carries
  `identity.rights_default()` and therefore refuses import and copy by default.
- The refusal message is exactly the string recorded in the action step below,
  asserted by substring comparison, not paraphrase.
  </behavior>
  <action>
1. Add `check_rights()` and its assertions to `tests/operations_roundtrip.py`
   first, wired into `main()`. Run and confirm it fails.

2. In `identity.py`, add `RIGHTS_STATES = ("granted", "denied", "unknown")`,
   `rights_state(record, operation)`, and `rights_granted(record, operation)`.
   `rights_state` returns `RIGHTS_UNKNOWN` when the record is None, when it is
   empty, when the operation name is not in `RIGHTS_OPERATIONS`, or when the
   stored value is not in `RIGHTS_STATES`. Its docstring states, in plain
   sentences, that comparison is exact ASCII string equality over a closed
   vocabulary, that no case folding, trimming, or near-match is applied, and
   that a source's rights authority is its owner or its license terms and not
   the local reader of the file (RIGHTS-01).

3. In `journal.py`, gate `op_import` and `op_copy`: read the source object's
   rights from the registry inside the held lock, call
   `identity.rights_granted(rights, "transform")`, and on False raise
   `JournalError("journal.rights_unknown", ...)` before any mutation, with this
   exact message format string:

   `"the transform right for source %s is %s, so %s is refused by name.
   Next safe action: record a rights grant for this source, or link the file
   where it lives instead of importing it."`

   filled with the source object id, the observed state, and the operation
   name. Journal one `refused` entry for the attempt.

4. Add a docstring paragraph on both handlers naming the four operations that
   do not consume rights and why: `link`, `move`, `edit_in_place`, and
   `supersede` act on objects the course already owns or merely binds where
   they live, so no source transform grant is required.

5. Re-run the test until green. Then run the full suite the way CI runs it:
   `for t in tests/*.py; do python "$t" || exit 1; done`.
  </action>
  <verify>
  <automated>python tests/operations_roundtrip.py</automated>
Expected: prints `OK operations_roundtrip` and exits 0. Degraded state proved:
a source with no rights record at all refuses import and copy by name, with the
next safe action stated, while the four ownership operations still work, so an
unknown right degrades the course rather than blocking it entirely.
  </verify>
  <acceptance_criteria>
- `python tests/operations_roundtrip.py` exits 0.
- `python -c "import identity; print(identity.RIGHTS_STATES,
  identity.rights_state({}, 'transform'), identity.rights_state({'transform':
  'GRANTED'}, 'transform'))"` prints `('granted', 'denied', 'unknown') unknown
  unknown`.
- The test asserts the refusal message by exact substring, including the
  sentence beginning `Next safe action: record a rights grant`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `identity.py` and `journal.py` contain no em dash character.
  </acceptance_criteria>
  <done>Rights are operation-specific, unknown is restrictive by default, and
  the two operations that pull source bytes refuse by name with the next safe
  action stated.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| discovery result to operation | A discovery entry, which is untrusted filesystem data, is offered as a move or copy candidate to an operation that could change identity. |
| external editor to journal | A file the course owns can be changed by any editor at any time, outside the journal. |
| source rights record to operation | A rights record decides whether source bytes may be transformed into a new owned artifact. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14A-03-01 | Spoofing | a crafted path carrying a known object id, used to hijack another object's evidence history | high | mitigate | `move_candidates` verifies the revision lineage before accepting a move and refuses with `journal.move_lineage_mismatch` otherwise; the path-and-id pair alone is never trusted. Asserted by the fabricated-lineage test case. |
| T-14A-03-02 | Tampering | silent auto-merge of two divergent artifacts | high | mitigate | No merge function exists in the module; a conflict refuses, `reconcile` records a human decision, and the edit-both-copies scenario asserts both copies keep their own bytes and ids. |
| T-14A-03-03 | Tampering | a conflicted object being overwritten by passing the observed on-disk fingerprint as the expected base | high | mitigate | The conflict state check runs inside the lock immediately after the fingerprint read, before the expected-base comparison, so a lucky argument cannot clear a conflict. Asserted directly. |
| T-14A-03-04 | Elevation of Privilege | importing or copying a source the course has no transform right to | high | mitigate | `op_import` and `op_copy` require the exact string `granted`; unknown, denied, absent, and unrecognized all refuse by name before any mutation. |
| T-14A-03-05 | Tampering | rights value read before the lock and acted on after it | medium | mitigate | The rights read happens inside the held lock at the moment of the operation. Recorded as a backstop-verified truth because a same-process test cannot observe the lock boundary directly. |
| T-14A-03-06 | Spoofing | name similarity used as identity | high | mitigate | `name_hints` returns results flagged `hint`, no handler or candidate function consumes it, and the near-identically-named corpus pair is asserted to receive two different ids. |
| T-14A-03-07 | Repudiation | an external edit disappearing from history | medium | mitigate | `detect_external_edits` appends an `external_edit` record carrying both fingerprints, and the record is idempotent per divergence, so the history shows the change the journal did not produce. |
| T-14A-03-08 | Tampering | supply chain: a third-party fuzzy-matching or diff package for name hints | high | mitigate | `difflib` is Python 3.11 standard library and is already the project's chosen tool for this class of problem (`STATE.md` 04-02 entry). Absence of a dependency is not itself the mitigation: any package added here later must be vendored at a pinned version with a recorded checksum and a named license review, per `PLANNING-DIRECTIVES.md` section 4a. |
| T-14A-03-09 | Information Disclosure | a rights refusal message leaking a source's absolute path | low | accept | The message names the source object id and the operation, not the path. Accepted as low because the message is local and this product has a single local user. |

## Flagged assumption carried forward, not silently dropped

**ID-02, unclassified edge.** The deterministic edge probe over ID-02's
requirement text produced one row it could not classify ("unclassified, review
manually"). It is recorded here rather than dropped. The reviewer's question
when this plan is verified: does ID-02's "hashes never prove authorship or
rights" clause impose an obligation on 14A beyond keeping the fingerprint out
of the identity and rights decisions, for example a recorded attestation
distinct from the fingerprint? If yes, it becomes a 14B or RIGHTS-02
requirement; if no, close it in the 14A-04 tracer report.
</threat_model>

<out_of_scope>
- No `migrate` operation. It is FILE-03's sixth verb but has no schema to
  migrate until 14B ships the course record. The omission is deliberate and is
  recorded in the decision table above so 14B inherits it rather than
  rediscovering it.
- No merge, no three-way merge, no rebase helper, no conflict-resolution
  algorithm. Reconciliation is a recorded human decision.
- No draft or branch object. R1's open-draft-revision state is 15B's.
- No rights enforcement beyond the `transform` gate on `import` and `copy`. The
  rights-grant record, the per-operation grant surface, and egress policy are
  D-12.6-9 and RIGHTS-02, owned by 14B.
- No graph edge, sidecar, or course record. D-14A-1's sidecar side is 14B's.
- No CLI command or daemon route for any of the six operations.
  `OPERATION-CONTRACT.md` lists discovery, binding, and link, import, move, and
  supersede commands under "Pending surfaces" and says not to invent them.
- No user interface for conflict resolution, history, or diff.
- No change to `model.py`, `runtime.py`, `evidence.py`, `audit_writer.py`, or
  anything under `surfaces/` or `schemas/`.
- No second write function. The six handlers call `commit_operation` and
  perform no write of their own.
</out_of_scope>

<summary_obligations>
`14A-03-SUMMARY.md` records: the six operations with their observed identity
effects quoted from the test assertions, the outcome of each of the three named
scenarios (move-then-edit, edit-both-copies, import-then-source-change), the
exact refusal messages emitted for `journal.conflict`,
`journal.rights_unknown`, and `journal.move_lineage_mismatch`, the disposition
of the flagged ID-02 unclassified edge, which truth was verified by which
command, and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create `.planning/phases/14A-identity-lifecycle-operation/14A-03-SUMMARY.md`
when done.
</output>
