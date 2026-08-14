# Phase 14A: Identity, Lifecycle & Operation Prototype - Pattern Map

**Mapped:** 2026-08-14
**Files analyzed:** 8 (2 new peer modules, 4 new test files, 1 fixture tree, plus one recorded-mapping-only note against `retention.py`)
**Analogs found:** 8 / 8

This phase is codebase-precedent-heavy: 14A-RESEARCH.md already read every
analog file in full this session and quoted verbatim excerpts with line
numbers. This PATTERNS.md restates and organizes those excerpts for the
planner, verified against the files on disk (`audit_writer.py`, `evidence.py`,
`model.py`, `runtime.py`, `tests/durability_roundtrip.py` all confirmed
present in the working tree).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `identity.py` (new, peer of `model.py`) | model/domain module (ID minting, fingerprinting, revision shape) | transform (pure functions, no I/O) | `model.py` (`new_item_id`, `content_fingerprint`, `assign_ids`) | exact |
| `journal.py` (new, peer of `runtime.py` / `evidence.py`) | service/runtime module (compare-and-swap write, atomic commit, append-only log) | CRUD + event-driven (write path) with file-I/O | `audit_writer.py` (full CAS/atomic-commit/undo mechanism); secondary `runtime.write_session()`, `evidence.py` (locking, closed vocabulary, append-only log) | exact |
| `tests/identity_roundtrip.py` | test | unit + integration (fixture-driven) | `tests/*_roundtrip.py` convention generally; closest for fixture-tree/discovery shape is any existing roundtrip test using a local `fail()` helper (e.g. `tests/audit_writer_roundtrip.py` if present, else `tests/durability_roundtrip.py`) | role-match |
| `tests/journal_roundtrip.py` | test, fault-injection-adjacent | file-I/O, event-driven | `tests/durability_roundtrip.py` (spawn/kill harness), `audit_writer.py`'s own test precedent for CAS refusal codes | exact |
| `tests/operations_roundtrip.py` | test | CRUD (operation vocabulary) | `evidence.py`'s `KNOWN_EVENT_TYPES` / `events()` skip-and-warn precedent, exercised via a roundtrip test | role-match |
| `tests/file_fault_tracer.py` | test, tracer/freeze-gate | fault-injection, batch | `tests/durability_roundtrip.py` (full file, spawn/kill + platform-conditional probes) | exact |
| `fixtures/<14A synthetic multi-root tree>/` | fixture data (not code) | file-I/O, synthetic tree | none needed as code analog; governed by `surfaces/cli.py:322-326`'s `fixtures/` exemption from `itembank guard` | n/a (fixture, not source) |
| `retention.py` (NOT touched by 14A; mapping recorded only) | model/service (computed state) | transform | n/a - 14A-01 records the `mastered` -> `evidence_support` migration mapping as a decision note; the actual rename is out of scope for 14A and routed to 16B | n/a |

## Pattern Assignments

### `identity.py` (model tier, transform, no I/O)

**Analog:** `model.py`

**ID minting pattern** (`model.py:1514-1522`, verified in RESEARCH.md this session):
```python
def new_item_id():
    """A 64-bit-random opaque id, short enough to read in an `[ID:]` line.

    An accidental collision across a personal bank is negligible, and D-05
    makes these globally unique across every bank a caller assigns into
    together, so renaming or splitting a bank file cannot orphan an item's
    evidence history.
    """
    return uuid.uuid4().hex[:16]
```
14A-01 should mint object-level IDs (course, objective, source, lesson, bank,
bounded component) with the same `uuid.uuid4().hex[:16]` shape or
`evidence.new_event_id()`'s full-hex shape; pick one and do not invent a
third ID shape.

**Fingerprint pattern to generalize** (`model.py:1451-1471`):
```python
def content_fingerprint(q):
    """A change-detection digest of the *tested* content only, never the
    rationale around it.

    Deliberately excludes `why`, `disc`, `second`, `trap`, `conf`, `da`,
    `notes`, `objective`, `difficulty`, `number`, `id`, `item_id`, `pair`,
    `prereq` and `content_hash` -- the hash's job is to detect that stem, options, correct
    answers, categories, rows, steps, model answer or rubric changed...
    """
```
Contrast with `authoring.py:176-179` (`bank_fingerprint`, no normalization at
all): 14A's new `object_fingerprint()` is genuinely new code, not a reuse.
Normalize a COPY of the bytes (strip trailing whitespace per line, normalize
`\r\n`/`\r` to `\n`) before hashing; never mutate stored bytes; never
normalize `model.content_fingerprint()`'s scoring-relevant digest, which
must stay byte-exact (regression-assert this per D-14A-2's keyed-content
carve-out; see Pitfall 4 in RESEARCH.md).

**ID/HASH split spec text to restate in `identity.py`'s docstring** (`model.py:1786-1790`):
```
`[ID:]` and `[HASH:]` are both optional... `[ID:]` is assigned once by
`itembank id-assign` and is never edited by hand. `[HASH:]` is a fingerprint
of the tested content, used only to detect that an item changed. The ID is
what evidence is recorded against, so deleting it orphans that item's history.
```
This is the anti-content-hash-as-ID precedent every new object kind must
follow: mint ID once with `uuid4`, store fingerprint as a separate,
recomputable field, never derive one from the other.

**Regression surface to check after normalization changes:** `model.py:2989-2996`,
the `item.content_drift` lint warning - the concrete signal that a
normalization function is (or is not) leaking into scoring-relevant content.

---

### `journal.py` (runtime tier, CRUD + event-driven, file-I/O)

**Primary analog:** `audit_writer.py` (full 620-line file read this session) - the single strongest precedent in the repository for this phase.

**Imports/lock pattern** (`audit_writer.py:48-92`):
```python
@contextlib.contextmanager
def _bank_lock(state_dir):
    os.makedirs(state_dir, exist_ok=True)
    lock_path = os.path.join(state_dir, "writer.lock")
    fh = open(lock_path, "a+b")
    try:
        if fh.tell() == 0:
            fh.write(b"\n")
            fh.flush()
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while True:
            if _try_lock(fh):
                break
            if time.monotonic() >= deadline:
                raise WriterError(
                    "writer.busy",
                    "another writer holds the per-bank lock for %s"
                    % lock_path)
            time.sleep(0.05)
        yield lock_path
    finally:
        try:
            _unlock(fh)
        finally:
            fh.close()


def _try_lock(fh):
    if os.name == "nt":
        import msvcrt
        try:
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False
    import fcntl
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False
```
Reuse this lock shape (bounded timeout, explicit `writer.busy`/`journal.busy`
refusal) rather than writing a third `msvcrt`/`fcntl` wrapper; `evidence.locked()`
(`evidence.py:123-160`) is the second independent, already-tested
implementation of the same idea, kept here only as a secondary reference.

**Compare-and-swap guard pattern** (`audit_writer.py:288-322`):
```python
def write_units(proposal, target_path, state_dir, expected_fingerprint=None,
                create_if_missing=False):
    ...
    with _bank_lock(state_dir):
        exists = os.path.exists(target_path)
        ...
        before_raw = _read_bytes(target_path) if exists else b""
        before_fp = bank_fingerprint(
            before_raw.decode("utf-8")) if exists else ""
        if expected_fingerprint is not None and before_fp != expected_fingerprint:
            raise WriterError(
                "writer.stale_preflight",
                "current bank fingerprint %s does not match the preflighted "
                "%s; the bank changed since the proposal was built"
                % (before_fp, expected_fingerprint))
```
14A-02/14A-03 should recase this refusal as `journal.conflict` when the
mismatch is same-ID-divergent-bytes (ID-02's conflict case), distinguishing
it from a plainer `journal.stale_preflight` when there is no competing
revision - see ID-02 requirement and Pattern 3 discussion below.

**Prepared-before-mutation, atomic replace, after-fingerprint guard** (`audit_writer.py:346-402`):
```python
    manifest = {
        "schema_version": WRITE_SCHEMA_VERSION,
        "write_id": write_id,
        ...
        "state": "prepared",
        ...
    }
    if before_exists:
        _write_bytes_atomic(manifest["before_image"], before_raw)
    _write_json(manifest_path, manifest)
    after_raw = proposal["bank_after_text"].encode("utf-8")
    _write_bytes_atomic(target_path, after_raw)
    current_after = bank_fingerprint(_read_bytes(target_path).decode("utf-8"))
    if current_after != proposal["bank_after_fingerprint"]:
        raise WriterError("writer.after_guard_failed", ...)
    manifest["state"] = "applied"
    ...
    _write_json(manifest_path, manifest)
```
This is the exact "journal entry written BEFORE mutation, flipped to
`applied` only after a verified after-fingerprint match" shape 14A-02's
undo-pointer journal entry must follow (Pitfall 1 in RESEARCH.md: a crash
between commit and the "applied" mark must leave a recoverable `prepared`
entry, not silent corruption).

**Secondary analog, the simpler tmp+replace idiom** (`runtime.py:1430-1437`):
```python
def write_session(path, data):
    target = session_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)
```
This is the base idiom `audit_writer.py`'s `_write_json`/`_write_bytes_atomic`
both derive from; `journal.py`'s low-level write helper should be a fourth
call site agreeing with this idiom, never a divergent implementation (see
Anti-Patterns below).

**Closed-vocabulary pattern for operation types** (`evidence.py:51-55`):
```python
KNOWN_EVENT_TYPES = ("response", "retraction", "mark", "day_tick",
                     "term_lookup", "key_review", "hint", "selection",
                     "lesson_complete", "cap_override",
                     "model_interaction", "mark_proposal", "visual_action",
                     "gate_skip")
```
14A-03 should mirror this exactly for `journal.py`'s `OPERATION_TYPES`:
`("link", "import", "copy", "move", "edit_in_place", "supersede")`, validated
at write time, with skip-and-warn (never raise) on an unrecognized type when
reading an older journal - matching `evidence.py:755-774`'s `events()`
degrade-not-crash handling of an unknown `event_type`.

**Peer-module docstring contract to restate at the top of `identity.py` and `journal.py`** (`evidence.py:1-19`):
```python
"""The evidence log: the one append-only store every later plan writes into and reads from.

`evidence.py` is to the evidence store what `runtime.score_response` is to scoring: the
single primitive every surface calls, so no surface reimplements its own append or its
own read. ...

This module is a peer of `runtime.py`, not an extension of it, and it is never imported
by `model.py` -- the same layer split `runtime.py`'s own docstring describes holds here:
identity lives in the model tier, scoring and sessions live in the runtime tier, and the
evidence log is a new runtime-tier primitive beside them.
"""
```

**Error handling pattern:** `audit_writer.WriterError` with a typed `code`
string (`writer.stale_preflight`, `writer.after_guard_failed`, `writer.busy`,
`undo.stale_target`) is the shape to reuse for `journal.py`'s own exception
(e.g. `JournalError` with codes `journal.conflict`, `journal.stale_preflight`,
`journal.busy`). This is a proven, already-tested refusal shape; do not
invent a second error taxonomy.

---

### `tests/journal_roundtrip.py` and `tests/file_fault_tracer.py` (fault-injection, file-I/O)

**Analog:** `tests/durability_roundtrip.py` (full 268-line file read this session)

**Local `fail()` helper convention** (present at the top of every one of the
60+ existing `tests/*_roundtrip.py` files; independently defined per file,
never imported from a shared module):
```python
def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)
```

**Spawn-and-kill harness** (`tests/durability_roundtrip.py:44-63`):
```python
def run_writer(mode, path, tag, count, padding, pad_key="x"):
    pad_char = PAD_CHARS[pad_key]
    for i in range(count):
        line = json.dumps({"tag": tag, "i": i, "pad": pad_char * padding}, ensure_ascii=False)
        if mode == "locked":
            itembank.append_line(path, line)
        elif mode == "raw":
            raw_append(path, line)
    return 0


def spawn_writers(mode, path, count, padding, tags=TAGS, pad_key="x"):
    procs = [subprocess.Popen([sys.executable, __file__, "--writer", mode, path,
                               tag, str(count), str(padding), pad_key]) for tag in tags]
    for p in procs:
        p.wait()
    return procs
```
`probe_kill()` (`tests/durability_roundtrip.py:185-239`) generalizes this to
`time.sleep(0.2); proc.terminate(); proc.wait()` - the exact "kill between
temp write and commit" shape `tests/journal_roundtrip.py` and
`tests/file_fault_tracer.py` need, applied to one compare-and-swap write call
instead of one append call.

**Fault-injection portability table (from RESEARCH.md, use directly in the fixtures):**

| Fault | Approach |
|-------|----------|
| Kill between temp write and commit | `subprocess.Popen` + timed `.terminate()`, per `tests/durability_roundtrip.py:206-210` |
| Disk-full simulation | Monkeypatch the journal's single low-level write helper (e.g. `_write_bytes_atomic`) to raise `OSError(errno.ENOSPC, ...)` at a chosen injection point |
| Permission-denied pocket | POSIX: `os.chmod(path, 0o000)`. Windows: `os.chmod(path, stat.S_IREAD)` (write-denied via read-only attribute; true ACL-level read denial is not stdlib-portable, name this limitation explicitly in the plan) |
| Symlink cycle / out-of-root symlink | `os.symlink()` on POSIX; Windows needs Developer Mode/elevation, fall back to `os.link()` or a mocked `os.walk` result if unavailable |
| Removable-volume absence stand-in | Create a fixture root, run discovery, `shutil.rmtree` the root, assert "unavailable" is reported, not a crash |

---

### `tests/operations_roundtrip.py` (CRUD, operation vocabulary)

**Analog:** `evidence.py`'s `KNOWN_EVENT_TYPES` / `events()` skip-and-warn
pattern (`evidence.py:51-55, 755-774`), exercised the way `evidence.py`'s own
roundtrip tests already prove an unknown `event_type` degrades rather than
raises. Use the same fixture shape: write a journal with one entry of each
of the six known operation types plus one entry of a deliberately-unknown
type, and assert the read path skips-and-warns on the unknown one instead of
crashing.

---

### `tests/identity_roundtrip.py` (unit + integration, fixture-driven)

**Analog:** the general `tests/*_roundtrip.py` convention (local `fail()`
helper, direct script execution, no framework) plus the fixture-tree
construction notes in RESEARCH.md's Fault-Injection Portability table
(symlink privilege fallback, permission-denied pocket, duplicate-fingerprint
pair). No single closest-file exists for the multi-root discovery walk
itself; RESEARCH.md's Pitfall 3 gives the exact code shape to use:
`os.walk(root, followlinks=False)` plus an explicit `os.path.realpath`
visited-set, refusing (not silently skipping) any resolved symlink target
outside the approved root.

## Shared Patterns

### Atomic tmp-then-replace write

**Source:** `runtime.py:1430-1437` (`write_session`), `audit_writer.py:246-265`
(`_write_json`/`_write_bytes_atomic`), `evidence.py:1126-1131` (index rebuild,
explicitly documented as "the same tmp-then-replace pattern
`runtime.write_session()` uses").
**Apply to:** every durable write in `journal.py`. Do not add a fourth,
slightly different implementation; this is the repository's one proven idiom
(see Anti-Patterns).

### Cross-platform advisory locking, bounded timeout, explicit busy refusal

**Source:** `audit_writer.py:48-92` (`_bank_lock`, `_try_lock`), secondary
`evidence.py:123-160` (`locked()`).
**Apply to:** `journal.py`'s per-object lock, held across the entire
check-fingerprint-then-write sequence (closes the TOCTOU threat named in
RESEARCH.md's Security Domain section).

### Opaque ID never derived from content

**Source:** `model.py:1786-1790` (the `[ID:]`/`[HASH:]` spec text),
`model.py:1514-1522` (`new_item_id`).
**Apply to:** every object kind `identity.py` mints. Content-hash-as-ID is
already hard-rejected in the decisions ledger (D-14A-2); do not reintroduce
it via a "duplicate detector" that skips the ID comparison.

### Closed vocabulary with skip-and-warn on unknown

**Source:** `evidence.py:51-55` (`KNOWN_EVENT_TYPES`), `evidence.py:755-774`
(`events()`'s degrade-not-crash handling).
**Apply to:** `journal.py`'s `OPERATION_TYPES` tuple (`link`, `import`,
`copy`, `move`, `edit_in_place`, `supersede`) and its read path.

### Typed refusal codes

**Source:** `audit_writer.WriterError` (codes `writer.stale_preflight`,
`writer.after_guard_failed`, `writer.busy`, `undo.stale_target`).
**Apply to:** `journal.py`'s own exception type and codes (`journal.conflict`,
`journal.stale_preflight`, `journal.busy`).

### Local test `fail()` helper, no shared test-util import

**Source:** every existing `tests/*_roundtrip.py` file (convention verified
by grep across `tests/` per RESEARCH.md).
**Apply to:** all four new test files in this phase.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `fixtures/<14A synthetic multi-root tree>/` | fixture data | file-I/O | Not source code; governed by construction rules in RESEARCH.md's Environment Availability and Fault-Injection Portability tables rather than a code analog. `surfaces/cli.py:322-326` already exempts `fixtures/` from `itembank guard`. |

## Anti-Patterns to Avoid (from RESEARCH.md, restated for the planner)

- **A second atomic-write helper.** Three call sites (`runtime.write_session`,
  `audit_writer._write_json`/`_write_bytes_atomic`, `evidence.rebuild_index`)
  already agree on the tmp-then-`os.replace` idiom. A fourth, different
  implementation in `journal.py` is a regression.
- **Content-hash-as-ID.** Already hard-rejected (D-14A-2). Mint the ID once
  with `uuid4`; store the fingerprint as a separate, recomputable field.
- **A second locking primitive.** `evidence.locked()` and
  `audit_writer._bank_lock()` already exist and are tested; reuse one.
- **A database file as the journal's source of truth.** `evidence.py`'s own
  sqlite3 index is an explicitly disposable materialized view, never a second
  source of truth. If `journal.py` ever adds a query cache, it must be
  similarly disposable and rebuildable.
- **Modifying `audit_writer.py`, `runtime.py`, or `evidence.py` as a side
  effect of building `journal.py`/`identity.py`.** 14A is additive only; these
  three files are read for pattern extraction, never edited by this phase.
- **Executing the `mastered` -> `evidence_support` rename inside 14A-01.** The
  enum value is a published schema contract
  (`schemas/report.schema.json:228-234`); renaming it is not additive. 14A-01
  records the migration mapping as a decision note only; the actual rename
  (touching `retention.py`, `surfaces/study.py`, `surfaces/day.py`,
  `surfaces/retention_view.py`, `selection.py`, and the schema) is routed to
  16B.

## Metadata

**Analog search scope:** root-level modules (`model.py`, `runtime.py`,
`evidence.py`, `audit_writer.py`, `authoring.py`, `retention.py`), `tests/`
directory conventions, `surfaces/cli.py` guard-exemption logic. All reads
performed by `gsd-phase-researcher` this session per 14A-RESEARCH.md's
Sources section; verified present on disk this session (`ls` check).
**Files scanned:** 8 primary source files, plus `.github/workflows/ci.yml`
and `schemas/report.schema.json` for contract verification.
**Pattern extraction date:** 2026-08-14
