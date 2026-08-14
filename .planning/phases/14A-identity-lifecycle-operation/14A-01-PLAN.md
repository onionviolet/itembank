---
phase: 14A-identity-lifecycle-operation
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - identity.py
  - discovery.py
  - fixtures/corpus_14a.py
  - tests/identity_roundtrip.py
  - .planning/phases/14A-identity-lifecycle-operation/14A-EVIDENCE-FIELD-MAPPING.md
autonomous: true
requirements: [ID-01, FILE-01, FILE-02, RIGHTS-01]
must_haves:
  truths:
    - "A caller can mint a durable opaque id for a course, objective, source, lesson, bank, or component, and the id is a 16-character hex string that is never derived from content bytes, a path, or a display name (ID-01, D-14A-2)."
    - "Every minted object carries a revision record with exactly the eleven keys object_id, kind, revision, parent_revision, fingerprint, timestamp, origin, profile_version, source_version, generator_version, rights; revision 1 has parent_revision null (ID-01)."
    - "identity.object_fingerprint normalizes line endings for every kind, and additionally strips per-line trailing whitespace for every kind except bank and lesson, so a cosmetic reformat of a course record reads as unchanged while a trailing space inside a CORRECT: line of a bank reads as changed (D-14A-2 keyed-content carve-out)."
    - "Fingerprint equality is defined over UTF-8 bytes after that normalization; no Unicode NFC or NFD normalization is ever applied, so a name written with a precomposed accent and one written with a combining accent are two different objects (FILE-03 encoding edge)."
    - "An object with no fingerprint is recorded as having no fingerprint rather than an empty-string fingerprint, so plan 14A-02 can refuse a compare-and-swap write against it instead of overwriting blind (ID-01 degraded clause)."
    - "Two files with byte-identical normalized content and two different object ids are reported as a copy candidate, never merged and never given one id (ID-01 adjacency edge, ID-02)."
    - "An empty (zero byte) file mints a valid id and a valid fingerprint of the empty normalized byte string; an inventory of zero roots returns an empty result with complete true, not an error (ID-01 empty edge)."
    - "identity.registry_rows returns objects sorted by (kind, object_id) so two objects that compare equal on kind still come back in a stable, specified order across runs (ID-01 ordering edge)."
    - "A source object with no rights record defaults every one of the seven rights operations (read, quote, transform, remote_process, package, export, share) to the string unknown; an empty rights dict is treated identically to an absent one (RIGHTS-01 empty edge)."
    - "discovery.inventory walks only inside approved roots, yields results before the walk completes, stops within one directory of a cancel signal, and can resume after a named relative path (FILE-02)."
    - "A path that a symlink resolves outside every approved root is recorded with state symlink_out_of_root and listed in the report's refused list; it is refused by name, never silently skipped (FILE-02)."
    - "An unreadable or permission-denied path is inventoried with state denied, is never mutated, and the run report names the path (FILE-01 and FILE-02 degraded clause)."
    - "An approved root that does not exist is reported with state unavailable and the rest of the inventory still returns; a missing root never raises out of discovery.inventory (FILE-01 degraded clause)."
    - "discovery.py holds no write path at all: the module object exposes no attribute named journal, subprocess, or urllib, so discovery structurally cannot grant write, execute, or transmit authority (FILE-02)."
    - "The synthetic corpus generator writes only fictional content and is the only source of 14A test data; no real bank, source, or learner file is read by any 14A test (project content rule)."
    - statement: "identity.py stays in the model tier: the imported module exposes no attribute named model, runtime, evidence, or journal, so the scoring-relevant digest in model.content_fingerprint can never be reached from the identity kernel."
      verification: backstop
  prohibitions:
    - "No object identity is ever derived from content bytes, a path, or a display name."
    - "The identity kernel never records a rights grant it was not given; an absent rights record means unknown, never permissive."
    - "No real learner, bank, or course content enters the synthetic corpus or any 14A fixture."
  artifacts:
    - "identity.py at the repository root, a model-tier peer of model.py"
    - "discovery.py at the repository root, a read-only walker with no write path"
    - "fixtures/corpus_14a.py, the synthetic multi-root corpus generator"
    - "tests/identity_roundtrip.py"
    - ".planning/phases/14A-identity-lifecycle-operation/14A-EVIDENCE-FIELD-MAPPING.md"
  key_links:
    - "identity.object_fingerprint and model.content_fingerprint are two different fingerprints for two different jobs. If they are ever unified, a cosmetic normalization silently masks a scoring-relevant change, which D-14A-2 forbids by name."
    - "The 16-hex object id shape is deliberately the same shape model.new_item_id() already mints. A third id shape in this repository is the failure mode this plan exists to avoid."
    - "identity.utc_now() must produce a string in exactly the format evidence.utc_now() produces. identity.py cannot import evidence (tier split), so the format is locked by an assertion in tests/identity_roundtrip.py instead."
---

<objective>
Ship the identity kernel: opaque id minting, a normalized change-detection
fingerprint, the revision record shape, the restrictive rights slot, bounded
component ids, and a read-only multi-root discovery walker, proven against a
synthetic corpus that includes a symlink cycle, an out-of-root symlink, a
permission-denied pocket, and a duplicate-fingerprint pair.

This is the skeleton-enabling slice. Phase 13.9 stubs course-level storage over
this plan plus the journal append of 14A-02 (14A-BRIEF.md "Walking-skeleton
coupling"; ROADMAP Phase 13.9; READINESS-AUDIT-14A.md A9). It lands first so
13.9 is not blocked.

Decisions already made, cited, and never re-derived here:

- **D-14A-2** (`DECISIONS-PRE-14A-2026-08-14.md`): object-level opaque ids for
  course, objective, source, lesson, and bank, plus component ids only for
  lesson blocks that are cited, gated, or evidence-bearing. Items keep their
  shipped `[ID:]`/`[HASH:]` scheme and are untouched by this phase. Fingerprint
  normalization for the first cut is trailing whitespace and line endings only.
  Reflow normalization is deferred to the 14A-04 tracer. Keyed assessment
  content is never normalized in a way that could mask a scoring-relevant
  change, and that is regression-asserted here.
- **D-14A-3**: the shipped `mastered` label becomes a per-objective,
  self-adjustable, evidence-driven fill state. This plan records the migration
  mapping only. It renames nothing.
- **D-14A-1**: only the inline-edge side of the hybrid graph decision touches
  14A. No sidecar and no cross-object edge store is built here.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Module names | `identity.py` (model tier, no I/O) and `discovery.py` (read-only walker), both root-level peers | 14A-RESEARCH.md "Architectural Responsibility Map" places identity in the model tier beside `model.py`; `discovery.py` is split out so FILE-02's "discovery grants no write authority" is structural rather than maintained by care. |
| Object id shape | `uuid.uuid4().hex[:16]`, bare, with no kind prefix | Identical to the shipped `model.new_item_id()`; 14A-RESEARCH.md Standard Stack says pick one of the two shipped shapes and do not invent a third. A kind prefix would invite parsing identity out of a string. |
| Revision field type | Integer counter. The first recorded revision is `1` and its `parent_revision` is JSON `null` | 14A-RESEARCH.md Open Question 1 recommends an integer counter, consistent with `evidence.attempt_number()`. A 1-based counter makes "no parent" express itself as null rather than as a magic zero. |
| Trailing-whitespace normalization scope | Applied to every kind except `bank` and `lesson` | Those are the only two 14A object kinds whose storage bytes can carry keyed assessment content (`CORRECT:` lines, rubrics, `> [!KEY]` cloze answers). Exempting them makes D-14A-2's "never masks a scoring-relevant change" structurally true. |
| Line-ending normalization scope | Applied to every kind including `bank` and `lesson` | Line endings are already established as not scoring-relevant in this repository: the CRLF byte-comparison defect in `runner.py` was fixed rather than enshrined (`STATE.md`, 2026-08-12 correction). |
| Timestamp format | `identity.utc_now()`, producing exactly the string shape `evidence.utc_now()` produces | One timestamp format across the project (14A-RESEARCH.md assumption A2). `identity.py` cannot import `evidence` without breaking the tier split, so the format is locked by a test assertion instead of by an import. |
| Component id serialization | The anchor marker text is `[CID:<16 hex>]`, one marker per line, and `identity.find_component_anchors(text)` returns `(component_id, offset)` pairs from one regex | R8 in `research/phase-16/16-editor-reader-landscape.md` section 4 requires component ids to be locatable in canonical bytes. `[CID:...]` joins the shipped `[ID:]`/`[HASH:]` marker family, and a single-marker regex locator is not a second content parser: it builds no document model. |
| Corpus form | `fixtures/corpus_14a.py` is a generator that builds a tree into a caller-supplied directory. No corpus tree is committed | D-12.6-10 asks for a corpus generator, and 10k files cannot live in git. `itembank guard` already skips `fixtures/`, and generated trees live in temp directories, so the guard stays green by construction. |

Purpose: nothing else in Phase 14A can be built until an object has a durable
name and a trustworthy change signal.
Output: `identity.py`, `discovery.py`, the corpus generator, its roundtrip test,
and the recorded evidence-field migration mapping.
</objective>

<context>
@.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md
@.planning/DECISIONS-PRE-14A-2026-08-14.md
@.planning/phases/14A-identity-lifecycle-operation/14A-RESEARCH.md
@.planning/phases/14A-identity-lifecycle-operation/14A-PATTERNS.md
@.planning/PLANNING-DIRECTIVES.md
@.agents/skills/OPERATION-CONTRACT.md
@model.py
@evidence.py
@authoring.py
</context>

## Artifacts this phase produces (plan 14A-01 share)

New modules and their public symbols:

- `identity.py`
  - Constants: `IDENTITY_SCHEMA_VERSION = 1`, `OBJECT_KINDS = ("course",
    "objective", "source", "lesson", "bank", "component")`,
    `TRAILING_WS_EXEMPT_KINDS = ("bank", "lesson")`,
    `COMPONENT_ROLES = ("cited", "gated", "evidence_bearing")`,
    `RIGHTS_OPERATIONS = ("read", "quote", "transform", "remote_process",
    "package", "export", "share")`, `RIGHTS_UNKNOWN = "unknown"`,
    `ACTOR_KINDS = ("human", "agent", "runtime")`,
    `COMPONENT_MARKER = "[CID:%s]"`, `REVISION_KEYS` (the eleven-key tuple in
    fixed order).
  - Exception: `IdentityError(Exception)` with `.code` and `.message`.
  - Functions: `utc_now()`, `new_object_id()`, `new_component_id()`,
    `normalize_for_fingerprint(raw, kind)`, `object_fingerprint(raw, kind)`,
    `rights_default()`, `revision_record(...)`, `mint_object(...)`,
    `next_revision(...)`, `mint_component(parent_object_id, role)`,
    `component_anchor(component_id)`, `find_component_anchors(text)`,
    `registry_rows(records)`, `copy_candidates(records)`.
- `discovery.py`
  - Constants: `DISCOVERY_SCHEMA_VERSION = 1`, `ENTRY_STATES = ("readable",
    "denied", "symlink_out_of_root", "symlink_cycle", "unavailable")`.
  - Exception: `DiscoveryError(Exception)` with `.code` and `.message`.
  - Functions: `inventory(roots, cancel=None, resume_after=None)` (a
    generator), `run_report(roots, cancel=None, resume_after=None)`,
    `inside_any_root(path, roots)`.
- `fixtures/corpus_14a.py`
  - `build_corpus(dest, size="1k")` returning a dict describing what was built,
    including the key `symlinks` (bool) and `denied_mode` (`"read"` or
    `"write"`).
  - `teardown_corpus(dest)`, which restores permissions before removing.
- `tests/identity_roundtrip.py`, direct-execution script, exit 0 on pass.
- `.planning/phases/14A-identity-lifecycle-operation/14A-EVIDENCE-FIELD-MAPPING.md`.

Refusal codes introduced by this plan: `identity.unknown_kind`,
`identity.component_role_ineligible`, `discovery.root_unapproved`.

No CLI command, no daemon route, no schema file, and no journal is produced by
this plan.

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: identity.py, minted and fingerprinted end to end</name>
  <files>identity.py, tests/identity_roundtrip.py</files>
  <read_first>
- `model.py` lines 1451 to 1471 (`content_fingerprint`, the change-detection
  digest of tested content only) and lines 1514 to 1522 (`new_item_id`, the
  16-hex opaque id) and lines 1786 to 1790 (the `[ID:]` versus `[HASH:]` spec
  text stating that the id is what evidence is recorded against).
- `authoring.py` lines 166 to 190 (`bank_fingerprint`, which hashes exact bytes
  with no normalization and returns the `"sha256:" + hexdigest` shape).
- `evidence.py` lines 1 to 19 (the peer-module docstring contract to restate)
  and lines 108 to 120 (`utc_now` and `new_event_id`).
- `.planning/DECISIONS-PRE-14A-2026-08-14.md` D-14A-2, in full.
- Any existing `tests/*_roundtrip.py` file, for the local `fail(msg)` helper
  convention (each test file defines its own; there is no shared test module).
  </read_first>
  <behavior>
Assertions this task's test section must make, written before the module:

- `identity.new_object_id()` returns a 16-character lowercase hex string, and
  1000 consecutive calls produce 1000 distinct values.
- The same bytes minted twice produce two different object ids: identity is not
  a function of content.
- `identity.utc_now()` and `evidence.utc_now()` both match the regular
  expression `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$`.
- `identity.object_fingerprint(b"line\r\n", "course")` equals
  `identity.object_fingerprint(b"line\n", "course")`.
- `identity.object_fingerprint(b"line   \n", "course")` equals
  `identity.object_fingerprint(b"line\n", "course")`.
- `identity.object_fingerprint(b"CORRECT: B \n", "bank")` does NOT equal
  `identity.object_fingerprint(b"CORRECT: B\n", "bank")`, and the same
  inequality holds for kind `"lesson"`.
- `identity.object_fingerprint(b"x\r\n", "bank")` equals
  `identity.object_fingerprint(b"x\n", "bank")`.
- `identity.object_fingerprint(raw, "bank")` equals
  `authoring.bank_fingerprint(raw.decode("utf-8"))` for any `raw` that contains
  no carriage return, proving the two agree on the shape and on exact bytes.
- `identity.object_fingerprint(b"", "course")` returns a value starting with
  `"sha256:"` and does not raise.
- `identity.object_fingerprint(b"caf\xc3\xa9", "course")` differs from
  `identity.object_fingerprint(b"cafe\xcc\x81", "course")`: no Unicode
  normalization is applied.
- `identity.object_fingerprint(b"\xff\xfe raw", "source")` returns a value and
  does not raise: a non-UTF-8 file in an approved root must not crash the
  kernel.
- `identity.mint_object("course", "course.md", b"x", "human", "weibao",
  "mint")` returns a dict whose keys, in order, equal `identity.REVISION_KEYS`,
  with `revision == 1` and `parent_revision is None`.
- `identity.next_revision(rec, b"y", "agent", "claude-code", "edit_in_place")`
  returns `revision == 2` and `parent_revision == 1` and the same `object_id`.
- `identity.mint_object("item", ...)` raises `IdentityError` with code
  `identity.unknown_kind`; `"item"` is not in `OBJECT_KINDS`.
- `identity.rights_default()` returns a dict with exactly the seven keys in
  `RIGHTS_OPERATIONS`, each mapped to `"unknown"`.
- A minted `source` record's `rights` value equals `identity.rights_default()`
  when no rights argument is given.
- A record minted with `fingerprint=None` keeps `None`, not `""`.
- `identity.mint_component(parent_id, "cited")` returns a 16-hex component id;
  `identity.mint_component(parent_id, "summary")` raises `IdentityError` with
  code `identity.component_role_ineligible`.
- `identity.component_anchor(cid)` equals `"[CID:" + cid + "]"`, and
  `identity.find_component_anchors("a\n[CID:%s]\nb" % cid)` returns exactly one
  pair whose first element is `cid`.
- `identity.registry_rows` over three records with kinds `source`, `bank`,
  `bank` returns them sorted by `(kind, object_id)` and the order is identical
  across two calls with the input list shuffled between them.
- `identity.copy_candidates` over two records with equal fingerprints and
  different object ids returns exactly one pair, and returns an empty list when
  the fingerprints differ.
- `hasattr(identity, "model")`, `hasattr(identity, "runtime")`,
  `hasattr(identity, "evidence")`, and `hasattr(identity, "journal")` are all
  False: the model tier stays free of runtime-tier imports.
  </behavior>
  <action>
1. Create `tests/identity_roundtrip.py` first, with the local `fail(msg)`
   helper that prints `"FAIL: " + msg` and calls `sys.exit(1)`, a
   `check_identity()` function holding every assertion listed in `<behavior>`
   above, and a `main()` that calls it and prints `"OK identity_roundtrip"`.
   Run it and confirm it fails, because `identity.py` does not exist yet.

2. Create `identity.py` at the repository root. Open it with a module docstring
   restating the peer-module contract from `evidence.py` lines 1 to 19 with
   "identity kernel" substituted, and stating in plain sentences: this module
   is the model tier, it performs no file input or output, it never imports a
   runtime-tier module, and its fingerprint is a change-detection value only
   and never a security boundary (the same integrity note `evidence.py`
   carries). No em dash characters anywhere in the file.

3. Define the constants named in "Artifacts this phase produces" above.
   `REVISION_KEYS` is the fixed-order tuple `("object_id", "kind", "revision",
   "parent_revision", "fingerprint", "timestamp", "origin", "profile_version",
   "source_version", "generator_version", "rights")`.

4. Define `IdentityError(Exception)` carrying `.code` and `.message`, with the
   two-argument constructor shape `audit_writer.WriterError` already uses. Its
   two codes and their exact messages:
   - `identity.unknown_kind`: `"%s is not a known object kind; known kinds are:
     course, objective, source, lesson, bank, component"`
   - `identity.component_role_ineligible`: `"component ids are minted only for
     cited, gated, or evidence-bearing blocks; role %s is not one of them"`

5. Implement `utc_now()` producing the identical output shape to
   `evidence.utc_now()` (ISO-8601 UTC to millisecond precision with a `Z`
   suffix), with a docstring naming `evidence.utc_now()` as the origin of the
   format and stating that the two must produce the same shape, which
   `tests/identity_roundtrip.py` asserts. Do not import `evidence`.

6. Implement `new_object_id()` and `new_component_id()`, both returning
   `uuid.uuid4().hex[:16]`, with a docstring citing `model.new_item_id()` as
   the shape's origin and stating that an id is minted once and is never
   derived from content, path, or display name (D-14A-2, and the ledger's
   hard rejection of content-hash-as-identity).

7. Implement `normalize_for_fingerprint(raw, kind)`: decode `raw` as UTF-8 with
   `errors="surrogateescape"`, replace `"\r\n"` then `"\r"` with `"\n"`, and if
   `kind` is not in `TRAILING_WS_EXEMPT_KINDS` also strip trailing whitespace
   from each line, then re-encode with the same error handler. The docstring
   states the carve-out in full: `bank` and `lesson` are exempt from trailing
   whitespace stripping because they are the only kinds whose storage bytes can
   carry keyed assessment content, so stripping there could mask a
   scoring-relevant change, which D-14A-2 forbids.

8. Implement `object_fingerprint(raw, kind)` returning `"sha256:" +
   hashlib.sha256(normalize_for_fingerprint(raw, kind)).hexdigest()`. Raise
   `IdentityError("identity.unknown_kind", ...)` for a kind outside
   `OBJECT_KINDS`. The docstring states, in plain sentences, that this function
   is not and must never become a substitute for `model.content_fingerprint`,
   which stays byte-exact over tested fields, and that the two exist for two
   different jobs.

9. Implement `rights_default()` returning a fresh dict mapping every entry of
   `RIGHTS_OPERATIONS` to `RIGHTS_UNKNOWN`. The docstring states that an absent
   or empty rights record is identical to an all-unknown record, and that
   unknown is restrictive, never permissive (RIGHTS-01).

10. Implement `revision_record(object_id, kind, revision, parent_revision,
    fingerprint, timestamp, origin, profile_version=None,
    source_version=None, generator_version=None, rights=None)` returning a
    dict built in `REVISION_KEYS` order. `origin` is a dict with exactly the
    three keys `actor_kind` (a member of `ACTOR_KINDS`), `actor_name` (a
    string, default `""`), and `operation` (a string). The docstring states
    that `origin` records who triggered the change without deciding who may
    accept it, so the still-open self-acceptance decision (D-12.6-4) is not
    foreclosed by this format.

11. Implement `mint_object(kind, path, raw, actor_kind, actor_name, operation,
    rights=None, ...)` returning a revision record with a fresh id,
    `revision=1`, `parent_revision=None`, and the fingerprint computed for that
    kind; and `next_revision(prev, raw, actor_kind, actor_name, operation)`
    returning the same `object_id` with `revision = prev["revision"] + 1` and
    `parent_revision = prev["revision"]`. Passing `raw=None` records
    `fingerprint=None` rather than an empty string, so 14A-02 can refuse a
    compare-and-swap write against it.

12. Implement `mint_component(parent_object_id, role)`, `component_anchor`,
    `find_component_anchors` (one compiled regular expression matching
    `[CID:` followed by exactly sixteen hex characters and `]`, returning
    `(component_id, match.start())` pairs in match order),
    `registry_rows(records)` returning `sorted(records, key=lambda r:
    (r["kind"], r["object_id"]))`, and `copy_candidates(records)` returning
    path-sorted pairs of records that share a fingerprint and differ in
    `object_id`.

13. Re-run the test and confirm it passes.
  </action>
  <verify>
  <automated>python tests/identity_roundtrip.py</automated>
Expected: prints `OK identity_roundtrip` and exits 0. Degraded state this task
must also prove, and which is included in the assertion list above: a non-UTF-8
byte sequence and a zero-byte input both fingerprint without raising, and a
record minted with no content records `fingerprint=None` rather than a
falsely-empty fingerprint.
  </verify>
  <acceptance_criteria>
- `python tests/identity_roundtrip.py` exits 0.
- `python -c "import identity; print(len(identity.new_object_id()))"` prints
  `16`.
- `python -c "import identity; print(identity.REVISION_KEYS)"` prints the
  eleven keys in the order given in step 3.
- `python -c "import identity; print(identity.rights_default())"` prints a dict
  with seven keys, every value the string `unknown`.
- `python -c "import identity; identity.object_fingerprint(b'x', 'item')"`
  exits non-zero with `identity.unknown_kind` in the traceback.
- `python -c "import identity; print(hasattr(identity,'model'),
  hasattr(identity,'runtime'), hasattr(identity,'evidence'))"` prints
  `False False False`.
- `identity.py` contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="costly">The id shape, the eleven revision keys, and
  the normalization carve-out are consumed by 14A-02, 14A-03, and Phase 13.9.
  Changing them after the 14A-04 freeze means migrating recorded revisions;
  changing them before it costs one edit. The freeze is named explicitly in
  14A-04, not gated here, because D-14A-2 already resolved the scheme.</reversibility>
  <done>identity.py exists with every symbol listed in "Artifacts this phase
  produces", and tests/identity_roundtrip.py proves every assertion in
  `<behavior>`.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the synthetic corpus generator and the read-only discovery walker</name>
  <files>fixtures/corpus_14a.py, discovery.py, tests/identity_roundtrip.py</files>
  <read_first>
- `14A-RESEARCH.md` "Common Pitfalls > Pitfall 3" (symlink cycles and
  out-of-root symlinks) and the "Fault-Injection Portability Notes" table, in
  full, for the Windows symlink-privilege and permission-denied fallbacks.
- `surfaces/cli.py` `cmd_guard` (roughly lines 299 to 351), which excludes the
  `fixtures` directory from the real-content walk, so the executor knows why a
  generator under `fixtures/` needs no guard exemption work.
- `tests/durability_roundtrip.py` in full, for the direct-execution test
  convention and the platform-conditional probe style.
- `.planning/REQUIREMENTS.md` FILE-01 and FILE-02, in full, including their
  Fixture sentences.
  </read_first>
  <behavior>
Assertions this task adds to `tests/identity_roundtrip.py`, in a new
`check_discovery()` function, written before `discovery.py`:

- Building the `"1k"` corpus into a temp directory produces exactly three
  roots, and every generated file's content is fictional text produced by the
  generator.
- `discovery.run_report([root_a, root_b, root_c])` returns a dict with keys
  `roots`, `counts`, `entries`, `complete`, `cancelled`, `denied`, `refused`,
  `unavailable`, and `complete` is True for an uninterrupted run.
- Every entry's `state` is a member of `discovery.ENTRY_STATES`.
- The duplicate-fingerprint pair appears as two entries with equal
  `fingerprint` and different paths, and `identity.copy_candidates` over their
  minted records returns exactly one pair.
- A recursive snapshot of `(relative path, size, mtime_ns)` over all three
  roots taken before the run is equal to the snapshot taken after the run:
  discovery mutated nothing. Access time is deliberately excluded from the
  snapshot because reading a file legitimately updates it.
- Consuming only the first five yields of `discovery.inventory(...)` returns
  five entries and leaves the generator unfinished: results are useful before
  completion.
- A `cancel` callable that returns True after the first ten entries yields a
  report with `cancelled` True, `complete` False, and a non-empty
  `omitted_reason` string reading exactly `"cancelled by caller; the entries
  after %s were not inventoried"`.
- Passing `resume_after=<the relative path of the last entry of a cancelled
  run>` yields entries strictly after it in the same deterministic order, and
  the concatenation of the cancelled run and the resumed run equals the entry
  list of one uninterrupted run.
- The out-of-root symlink is reported with `state` equal to
  `symlink_out_of_root` and its path appears in `report["refused"]`; its target
  is never read (the target file's `mtime_ns` is unchanged and the entry's
  `fingerprint` is None).
- The symlink cycle is reported with `state` equal to `symlink_cycle` and the
  run terminates. If the corpus reports `symlinks` False (the platform could
  not create symlinks), the test prints exactly `"SKIP: symlink assertions
  (os.symlink unavailable on this platform)"` and skips these two assertions
  rather than passing silently.
- The permission-denied pocket: when `corpus["denied_mode"] == "read"` the
  entry is reported with `state` equal to `denied` and its path appears in
  `report["denied"]`; when it is `"write"` (the Windows fallback) the test
  prints exactly `"SKIP: read-denial assertion (os.chmod cannot deny read on
  this platform); write refusal is proven in tests/journal_roundtrip.py"` and
  skips that one assertion. Under either mode the file is never mutated.
- A root path that does not exist is reported once in `report["unavailable"]`,
  the other two roots still return their entries, and no exception escapes.
- `discovery.inventory([], ...)` returns an empty entry list with `complete`
  True.
- `discovery.inside_any_root("/etc/passwd", roots)` is False, and
  `discovery.run_report(["/some/path/outside"])` with an explicit approved-root
  list that excludes it raises `DiscoveryError` with code
  `discovery.root_unapproved`.
- `hasattr(discovery, "journal")`, `hasattr(discovery, "subprocess")`, and
  `hasattr(discovery, "urllib")` are all False.
  </behavior>
  <action>
1. Add `check_discovery()` and its assertions to `tests/identity_roundtrip.py`
   first, wired into `main()`. Run and confirm it fails.

2. Create `fixtures/corpus_14a.py` with `build_corpus(dest, size="1k")`. It
   creates three sibling roots under `dest` named `root_vault`, `root_sources`,
   and `root_banks`, each with nested subdirectories, and fills them with
   fictional Markdown and text files. Sizes: `"1k"` produces 1000 files total,
   `"10k"` produces 10000, spread across the three roots. Content is generated
   from a fixed seed so a rebuild is byte-identical, and every file's body is
   plainly synthetic, for example a heading reading `# Synthetic file NNNN` and
   two paragraphs of generated filler naming no real course, book, or learner.

   The corpus additionally contains, by construction:
   - a duplicate-fingerprint pair: two files in different roots with identical
     bytes;
   - a near-identically-named pair that differs in bytes, for 14A-03's use:
     `root_sources/unit_04/notes.md` and `root_sources/unit_04/Notes.md` where
     the platform is case-sensitive, otherwise `notes.md` and `notes .md`;
   - a symlink cycle (a directory symlink pointing at its own ancestor) and an
     out-of-root symlink (pointing at a file created under `dest` but outside
     all three roots), both attempted with `os.symlink`. On `OSError`,
     `NotImplementedError`, or `AttributeError`, set the returned dict's
     `symlinks` key to False, create ordinary placeholder files in their place,
     and do not raise;
   - a permission-denied pocket: `root_vault/private/denied.md`, made
     inaccessible with `os.chmod(path, 0o000)` on POSIX and
     `os.chmod(path, stat.S_IREAD)` on Windows. Set the returned dict's
     `denied_mode` key to `"read"` in the first case and `"write"` in the
     second.

   Also provide `teardown_corpus(dest)` which restores write permissions on
   every path (so `shutil.rmtree` succeeds on Windows) before removing `dest`.

3. Create `discovery.py` at the repository root. Its module docstring states,
   in plain sentences: this module is read-only by construction; it opens no
   file for writing, spawns no process, and makes no network request; finding a
   file grants no authority to transmit, transform, execute, or modify it
   (FILE-02); and the module deliberately does not import the journal so the
   read-only property is structural rather than maintained by care.

4. Implement `inside_any_root(path, roots)` comparing `os.path.realpath` of the
   candidate against `os.path.realpath` of each approved root using
   `os.path.commonpath`, returning True only for a genuine containment.

5. Implement `inventory(roots, cancel=None, resume_after=None)` as a generator.
   For each root in the order given: if it does not exist or cannot be listed,
   yield one entry with `state` equal to `unavailable` and continue to the next
   root. Otherwise walk with `os.walk(root, followlinks=False)`, sorting both
   `dirs` and `files` in place with `sorted()` on every level, so the order is
   deterministic and resumable. For each entry:
   - if `resume_after` is set and the entry's relative path sorts at or before
     it, skip the entry;
   - if `cancel` is not None and `cancel()` returns True, stop the generator;
   - if `os.path.islink(p)`: resolve `os.path.realpath(p)`; if the resolved
     path is not inside any approved root, yield `state` equal to
     `symlink_out_of_root` with `fingerprint` None and do not open it; if the
     resolved path is already in the visited real-path set, yield `state` equal
     to `symlink_cycle` and do not descend;
   - otherwise attempt to read the bytes; on `PermissionError` or `OSError`,
     yield `state` equal to `denied` with `fingerprint` None and the exception
     text in `note`; on success, yield `state` equal to `readable` with `size`
     and `fingerprint` computed by `identity.object_fingerprint(raw, "source")`.

   Each yielded entry is a dict with the keys `root`, `path` (relative to its
   root, using forward slashes), `state`, `size`, `fingerprint`, and `note`.

6. Implement `run_report(roots, cancel=None, resume_after=None)` which drains
   `inventory` and returns a dict with the keys `roots`, `entries`, `counts`
   (a per-state count dict), `complete`, `cancelled`, `denied` (paths),
   `refused` (paths whose state is `symlink_out_of_root`), `unavailable`
   (roots), and `omitted_reason` (empty string when complete). When a cancel
   fires, `omitted_reason` is exactly `"cancelled by caller; the entries after
   %s were not inventoried"` filled with the last inventoried relative path.

7. `DiscoveryError` carries `.code` and `.message`. Its one code and exact
   message: `discovery.root_unapproved`: `"%s is outside every approved root;
   discovery refuses to read it"`.

8. Re-run the test until green. Then run `python itembank.py guard .` and
   confirm it reports `0 offending files`.
  </action>
  <verify>
  <automated>python tests/identity_roundtrip.py</automated>
Expected: prints `OK identity_roundtrip` and exits 0, having printed any of the
two named SKIP lines when the platform forced a fallback. Also run
`python itembank.py guard .`, expected final line `0 offending files` and exit
code 0. Degraded states this task proves: a missing root reports unavailable
and the rest of the inventory still returns; a denied path is inventoried,
named in the report, and never mutated; a cancelled run returns partial results
with the omission stated.
  </verify>
  <acceptance_criteria>
- `python tests/identity_roundtrip.py` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import discovery; print(hasattr(discovery,'journal'),
  hasattr(discovery,'subprocess'), hasattr(discovery,'urllib'))"` prints
  `False False False`.
- `python -c "import fixtures.corpus_14a as c; import tempfile;
  d=tempfile.mkdtemp(); r=c.build_corpus(d); print(sorted(r.keys()));
  c.teardown_corpus(d)"` prints a key list containing `denied_mode` and
  `symlinks`.
- The before-and-after `(path, size, mtime_ns)` snapshot equality assertion is
  present in `tests/identity_roundtrip.py` and passes.
- Neither `discovery.py` nor `fixtures/corpus_14a.py` contains an em dash
  character.
  </acceptance_criteria>
  <done>The corpus generator builds the three-root synthetic tree with every
  fixture feature FILE-01 and FILE-02 name, and discovery walks it read-only,
  cancellably, resumably, and symlink-safely.</done>
</task>

<task type="auto">
  <name>Task 3: record the evidence-field migration mapping and close the ID-01 regression set</name>
  <files>.planning/phases/14A-identity-lifecycle-operation/14A-EVIDENCE-FIELD-MAPPING.md, tests/identity_roundtrip.py</files>
  <read_first>
- `.planning/DECISIONS-PRE-14A-2026-08-14.md` D-14A-3, in full, including the
  boundary paragraph that keeps a Khan-style fill state compatible with the
  one-aggregate-score hard rejection.
- `14A-RESEARCH.md` "Runtime State Inventory", in full. It is the verified
  answer to where the `mastered` string actually lives.
- `retention.py` lines 285 to 290 and 440 to 450 (the `STATES` tuple and the
  branch that returns the `mastered` state). Read only. This plan modifies
  nothing in `retention.py`.
- `schemas/report.schema.json` lines 228 to 234 (the published enum).
  </read_first>
  <action>
1. Create
   `.planning/phases/14A-identity-lifecycle-operation/14A-EVIDENCE-FIELD-MAPPING.md`
   with these sections and nothing more:

   - **Decision.** Quote D-14A-3's resolution: progress is a per-objective,
     self-adjustable fill state driven by valid response evidence, able to move
     up and down, never a permanent claim. Working stored-field name
     `evidence_support`. The exact token is low-stakes; the semantics are the
     decision.
   - **Where the old label actually lives.** A table copied from the research
     inventory: the published enum value in `schemas/report.schema.json`; the
     `STATES` tuple and three branches in `retention.py`; the five consuming
     call sites (`surfaces/study.py`, `surfaces/day.py`,
     `surfaces/retention_view.py`, `selection.py`, and the report schema); and
     the unrelated client-side JavaScript counter in `surfaces/study.py`, which
     is a naming coincidence and is explicitly excluded from the mapping.
   - **The mapping.** Old computed state label to new fill-state concept, one
     row per state, stating for each whether it survives, is renamed, or is
     absorbed into a fill level.
   - **What 14A does not do, and why.** Renaming the published enum value is a
     format break, not an additive change, and the fourth non-negotiable in
     `PLANNING-DIRECTIVES.md` section 4 requires format changes to be additive.
     The display semantics, the fill thresholds, and the level vocabulary are
     routed to Phase 16B by D-14A-3 and by the 14A phase brief. Therefore 14A
     records this mapping and changes no code.
   - **Owner and verification.** Phase 16B owns execution; the verification is
     that `schemas/report.schema.json` still validates unchanged today, checked
     by the shipped `python schema_validate.py` step.

   No em dash characters. Do not quote real learner data.

2. Add the remaining ID-01 and RIGHTS-01 regression assertions to
   `tests/identity_roundtrip.py` in a `check_regressions()` function:
   - the keyed-content carve-out, stated as a single named assertion: for a
     bank-shaped byte string containing the line `CORRECT: B` followed by a
     trailing space, `identity.object_fingerprint(raw, "bank")` differs from
     the same bytes with the trailing space removed, while for the identical
     text fingerprinted as kind `course` the two are equal;
   - `model.content_fingerprint` of a parsed fixture item is unchanged by
     anything in this plan: parse `fixtures/lesson_bank.md` with
     `model.load` and assert the fingerprint of its first item equals the value
     recomputed after `identity.object_fingerprint` has been called on the same
     file's bytes, proving the identity kernel has no side effect on the
     scoring-relevant digest;
   - a source record built with `rights={}` has the same effective rights as
     one built with `rights=None`, both equal to `identity.rights_default()`;
   - `identity.registry_rows` ordering stability across a shuffled input;
   - `identity.copy_candidates` returns the pair for equal fingerprints with
     different ids and an empty list otherwise.

3. Run the full 14A test file and the shipped anchors named in
   `14A-VALIDATION.md`.
  </action>
  <verify>
  <automated>python tests/identity_roundtrip.py &amp;&amp; python tests/scoring_roundtrip.py &amp;&amp; python tests/evidence_roundtrip.py</automated>
Expected: all three exit 0. The degraded behavior proved here is the honest
non-action one: the mapping is recorded and no shipped state label, enum value,
or consuming call site changed, which the two shipped anchor suites confirm by
staying green.
  </verify>
  <acceptance_criteria>
- `.planning/phases/14A-identity-lifecycle-operation/14A-EVIDENCE-FIELD-MAPPING.md`
  exists with all five named sections.
- `git diff --name-only` after this task lists no path under `schemas/`, and
  does not list `retention.py`, `selection.py`, or any file under `surfaces/`.
- `python tests/identity_roundtrip.py` exits 0.
- `python tests/scoring_roundtrip.py` and `python tests/evidence_roundtrip.py`
  both exit 0.
- The mapping file contains no em dash character.
  </acceptance_criteria>
  <done>The D-14A-3 migration mapping is a recorded artifact, the shipped
  retention and schema surfaces are untouched, and the ID-01 and RIGHTS-01
  regression set is green.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| approved root to walker | Arbitrary filesystem content, including hostile path shapes, crosses into `discovery.inventory`. |
| filesystem to fingerprint | Arbitrary bytes, including non-UTF-8 and zero-length, cross into `identity.object_fingerprint`. |
| caller to identity kernel | A caller supplies the object kind and the rights record; a wrong kind decides whether keyed content is normalized. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14A-01-01 | Tampering / Information Disclosure | `discovery.inventory` symlink handling | high | mitigate | `os.walk(..., followlinks=False)` is kept at its default, every link is resolved with `os.path.realpath` and tested against `inside_any_root`, an out-of-root target is recorded as `symlink_out_of_root` and refused by name rather than silently skipped, and a repeat real path is recorded as `symlink_cycle`. Asserted by the corpus's own cycle and out-of-root links. |
| T-14A-01-02 | Denial of Service | `discovery.inventory` on a cyclic tree | high | mitigate | The visited real-path set bounds the walk; the corpus contains a real cycle so a regression hangs the test rather than shipping. |
| T-14A-01-03 | Tampering | keyed assessment content normalized away by `object_fingerprint` | high | mitigate | `TRAILING_WS_EXEMPT_KINDS` exempts `bank` and `lesson` structurally, and Task 3's regression asserts the trailing space inside a `CORRECT:` line changes the bank fingerprint. |
| T-14A-01-04 | Spoofing | content hash or filename used as durable identity | high | mitigate | `new_object_id` is `uuid4`-derived only; `copy_candidates` reports equal fingerprints as candidates and never merges ids; asserted by the duplicate-fingerprint pair in the corpus. |
| T-14A-01-05 | Elevation of Privilege | discovery gaining write, execute, or transmit authority | high | mitigate | `discovery.py` imports no journal, no `subprocess`, and no `urllib`, asserted at runtime; the before-and-after `(path, size, mtime_ns)` snapshot proves nothing was mutated. |
| T-14A-01-06 | Information Disclosure | real course or learner content entering the repository as a fixture | high | mitigate | The corpus is generated from a fixed seed with fictional content only, lives in temp directories at test time, and `python itembank.py guard .` is part of this plan's verification. |
| T-14A-01-07 | Denial of Service | a permission-denied path aborting the whole inventory | medium | mitigate | `PermissionError` and `OSError` are caught per entry and recorded as `denied`; the run continues and the report names the path. |
| T-14A-01-08 | Tampering | supply chain: a third-party package introduced for hashing, walking, or uuid work | high | mitigate | This plan adds no third-party package; `hashlib`, `uuid`, and `os` are Python 3.11 standard library already imported by shipped modules. Per `PLANNING-DIRECTIVES.md` section 4a, absence of dependencies is not itself the mitigation: the mitigation is that if any future dependency is added here it must be vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent. |
| T-14A-01-09 | Repudiation | a minted revision with no recorded actor | low | accept | `origin` carries `actor_kind` and `actor_name`; a caller that passes an empty name records an empty name honestly. Accepted because 14A has a single local user and the acceptance-policy decision (D-12.6-4) is still open. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No journal, no compare-and-swap write, and no file mutation of any kind.
  Every durable write is plan 14A-02's.
- No operation vocabulary. `link`, `import`, `copy`, `move`, `edit_in_place`,
  and `supersede` are plan 14A-03's.
- No CLI command, no daemon route, no schema file under `schemas/`. The
  operation-contract skill's "Pending surfaces" list says do not invent
  commands for capabilities that have not shipped, and the 14A brief puts every
  new learner surface out of scope.
- No graph kernel, sidecar, cross-object edge store, or outline projection
  (14B, D-14A-1).
- No editor, history, draft, or diff user interface. 14A ships the model that
  R1 through R10 need and no UI.
- No rename of the `mastered` state, no edit to `retention.py`, `selection.py`,
  `schemas/report.schema.json`, or anything under `surfaces/`. Task 3 records a
  mapping only.
- No modification of `model.py`, `runtime.py`, `evidence.py`,
  `audit_writer.py`, or `authoring.py`. They are read for patterns; 14A is
  additive.
- No re-identification of items. Items keep the shipped `[ID:]` and `[HASH:]`
  scheme, and `"item"` is deliberately absent from `OBJECT_KINDS`.
- No lesson block-structure parsing. `find_component_anchors` locates one
  marker with one regular expression; it builds no document model, so `model.py`
  gains nothing that parses a second content format.
- No 100k-file corpus. `build_corpus` accepts `"1k"` and `"10k"` only; the
  100k size is D-12.6-10's own recommendation, is not named in the 14A brief,
  and is deferred with its reason recorded in 14A-04's report.

## Flagged assumption carried forward, not silently dropped

**FILE-02, unclassified edge.** The deterministic edge probe over FILE-02's
requirement text produced one row it could not classify ("unclassified, review
manually"). It is recorded here rather than dropped. The reviewer's question
when this plan is verified: does FILE-02's "useful before completion" clause
imply any obligation beyond streaming partial results, for example a stable
partial-result identity that survives a resume, that this plan's generator plus
`resume_after` contract does not already satisfy? If yes, it becomes a 14B
requirement; if no, close it in the 14A-04 tracer report.
</out_of_scope>

<summary_obligations>
`14A-01-SUMMARY.md` records: the exact platform fallbacks that fired (symlink
creation available or not, denied mode `read` or `write`), the two SKIP lines
printed if any, the measured wall-clock time of one full `"1k"` corpus build
plus inventory (for 14A-04's budget baseline, recorded not promised), which
truth was verified by which command, the disposition of the flagged FILE-02
unclassified edge, and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create `.planning/phases/14A-identity-lifecycle-operation/14A-01-SUMMARY.md`
when done.
</output>
