# Phase 14A: Identity, Lifecycle & Operation Prototype - Research

**Researched:** 2026-08-14
**Domain:** durable object identity, fingerprinting, and a compare-and-swap operation journal, built as new peer modules over an existing Python-stdlib runtime
**Confidence:** HIGH (this is a codebase-precedent phase; the load-bearing patterns already ship and were read this session)

<user_constraints>
## User Constraints (from DECISIONS-PRE-14A-2026-08-14.md and the 14A phase brief)

No `/gsd-discuss-phase` was run for 14A. `DECISIONS-PRE-14A-2026-08-14.md` stands
in for CONTEXT.md per the phase brief's binding-inputs list; its "Resolved"
blocks are locked decisions, not options to re-open.

### Locked Decisions

**D-14A-1 (graph storage, hybrid).** Resolved Option C: an edge lives inline
when it is wholly owned by one file's content; it lives in a readable course
sidecar when it relates two independently identified objects. Only the
inline-edge side matters to 14A per the phase brief ("Depends on: Nothing"
list item 1); the sidecar itself is 14B scope. **14A must not build the
sidecar or the cross-object edge store.**

**D-14A-2 (identity granularity and fingerprint normalization, resolved
Option B, bounded).** Object-level opaque IDs for course, objective, source,
lesson, bank, and item (items keep their shipped `[ID:]`/`[HASH:]` scheme
untouched, per the 14A-01 plan text: "items keep their shipped scheme
untouched"). Component IDs are minted **only** for lesson blocks that are
cited, gated, or evidence-bearing, never one ID per paragraph. Fingerprint
normalization for the first cut is **trailing whitespace and line endings
only**; Markdown-insignificant reflow normalization is explicitly deferred to
the 14A-04 tracer, which must run "the real-diff corpus check that decides
reflow normalization ... and records the decision" (14A-BRIEF.md line
97-98). Keyed assessment content is never normalized in a way that could mask
a scoring-relevant change, and this must be regression-asserted (14A-01 plan
text, line 51).

**D-14A-3 (evidence field rename, resolved as a Khan-style fill state, not a
simple rename).** The shipped `mastered` label (verified this session to be
one of six computed retention states, not a raw evidence-log field - see
Runtime State Inventory below) becomes a per-objective, self-adjustable fill
state, driven by valid response evidence, able to move up and down, never a
permanent claim. Working field name `evidence_support` is low-stakes; the
semantics (per-objective, evidence-driven, reversible) are the decision. Fill
thresholds and level vocabulary are routed to 16B, out of scope here. 14A-01
records the migration mapping; display semantics stay in 16B (14A-BRIEF.md
line 113-114).

### Discretion Areas (technical calibrations owned by 14A, confirmed at plan time)

**D-12.6-10 (corpus and performance budgets, recommendation recorded, 14A
confirms with real measurement).** Build one synthetic corpus generator (no
real content, `itembank guard` stays green) producing three sizes: 1k / 10k /
100k files across nested roots with symlinks, permission-denied pockets, and
duplicate fingerprints. Starting budgets to measure against, not promises:
first useful discovery results under 2 seconds on the 10k corpus; full
inventory under 60 seconds on 100k; cancel responds under 500 ms; memory
bounded (streaming, no whole-tree in RAM). The 14A-BRIEF.md text narrows
the corpus scope actually owed by 14A-04 to "the D-12.6-10 budgets ... on the
1k/10k corpora" - the 100k corpus size is D-12.6-10's own recommendation but
is not named in 14A-04's task list, so treat 100k as optional/stretch unless
the planner elects to include it.

**D-12.6-4 (solo self-acceptance, held for Weibao, touches 14A "lightly").**
Recommendation B (risk-tiered self-acceptance) is unresolved and explicitly
"pending." 14A's operation journal must not assume an answer here: it should
record who/what triggered an operation (actor field) and leave acceptance
policy as a layer 15B applies on top, not something 14A's journal format
forecloses.

### Deferred / Out of Scope (explicitly, per 14A-BRIEF.md "Explicitly out of scope")

Graph kernel, sidecar, outline projection (14B). Any editor or history UI -
the Ellipsus-pattern UI from `research/phase-16/16-editor-reader-landscape.md`
section 4 waits for its subphase; 14A ships the model only, no UI. Treatment
or director logic (15A). Any new learner surface. Do not research or propose:
graph kernel, outline projection, UI, treatment logic (per this task's own
additional_context).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FILE-01 | A course links user files where they live and edits owned files in place across multiple approved roots; an unreachable root reports unavailable and the course opens over the last valid index. Fixture: the 14A tracer's synthetic multi-root tree with one root made unreachable. | See "Architecture Patterns > Multi-root discovery" and "Common Pitfalls > Pitfall 4". The identity kernel (14A-01) must key objects by opaque ID, not by root+path, so an unreachable root degrades to "unavailable" without invalidating IDs minted from other roots. |
| FILE-02 | Discovery is read-only, root-bounded, cancellable, resumable, symlink-safe, and useful before completion. Fixture: a 14A tracer discovery run seeded with a symlink cycle and an out-of-root symlink, cancelled midway. | See "Common Pitfalls > Pitfall 3 (symlink cycles)" and "Environment Availability" for the Windows symlink-privilege caveat. `os.walk(..., followlinks=False)` plus an explicit `os.path.realpath` visited-set is the stdlib pattern; no third-party walker is needed. |
| FILE-03 | Link, import, copy, move, supersede, migrate are distinct operations with distinct identity effects; no automatic merge; name similarity is only a search hint. Fixture: two synthetic near-identically-named files that differ in bytes, exercising all five as distinct journaled operations. | See "Architecture Patterns > Pattern 3 (operation vocabulary)" and the `audit_writer.py` precedent's `WriterError` typed-refusal pattern, which 14A-03's conflict refusal should follow. |
| ID-01 | Every durable object carries a stable opaque ID plus fingerprint, revision, and applicable profile/source/generator versions. Fixture: 14A tracer's synthetic object set, plus one object stripped of its fingerprint to assert compare-and-swap is blocked. | See "Architecture Patterns > Pattern 1 (opaque ID minting)" and "Code Examples > model.new_item_id / content_fingerprint precedent". |
| ID-02 | Hashes detect change but never prove identity; same ID + divergent bytes = conflict; same fingerprint + different IDs = copy candidate; moved path + same ID = move candidate. Fixture: 14A external-edit tracer cases built from synthetic files exercising all three outcomes. | See "Architecture Patterns > Pattern 3" and "Common Pitfalls > Pitfall 2 (content-hash-as-ID orphans evidence)". |
| RIGHTS-01 | Rights are operation-specific per source; unknown stays unknown and restrictive; a source's rights authority is its owner, not the local reader. Fixture: 14A tracer scenario over synthetic sources with differing per-operation rights, including one unknown-rights source. | 14A's identity kernel needs a `rights` field slot on the source object shape so 14B can fill it without a schema break; 14A itself does not need to build rights enforcement (that is D-12.6-9, owned by 14B). Additive-field discipline (REQUIREMENTS.md LESSON-03/GATE-05 precedent) applies: an object with no rights grant yet must default to the restrictive `unknown` state, never be silently permissive. |
| RELIABILITY-01 | Every durable mutation uses expected-base-fingerprint compare-and-swap, temp output, validation, atomic commit, and an operation journal; fault injection yields the old or new valid state, never mixed. Fixture: the 14A file-fault tracer injecting crash, disk-full, and permission-denied faults into a synthetic compare-and-swap write. | See "Architecture Patterns > Pattern 2 (compare-and-swap write)", built almost entirely from the shipped `audit_writer.py` (Phase 11) and `runtime.write_session()` precedents. This is the strongest-precedented requirement in the phase. |
</phase_requirements>

## Summary

14A is not a green-field design problem. Every mechanism the phase brief asks
for - opaque IDs, change-detection fingerprints, compare-and-swap writes with
an expected-base-fingerprint guard, atomic temp-then-replace commits, and a
durable journal with undo - already ships in this repository in two places:
`runtime.write_session()` (the simple case, one file, no conflict detection)
and `audit_writer.py` from Phase 11 (the complete case: fingerprint guard,
content-addressed before-image, prepared-then-applied manifest states,
per-target OS lock, typed refusal codes, one-step undo). 14A's job is to
**generalize** the `audit_writer.py` pattern from "one bank file" to "any
durable object" (course, objective, source, lesson, bank, item, and bounded
lesson-block components), and to add the vocabulary layer (link, import, copy,
move, edit-in-place, supersede) that `audit_writer.py` does not need because it
only ever does one kind of write.

The identity side has its own shipped precedent: `model.py`'s `[ID:]`/`[HASH:]`
scheme for items (`new_item_id()`, `content_fingerprint()`, `assign_ids()`,
the `item.content_drift` lint warning) is the exact shape D-14A-2 asks 14A to
extend to object-level IDs - and the phase brief is explicit that items
themselves are out of scope for re-identification; only the *pattern* transfers.

The one genuinely new engineering surface is fault-injection testing (14A-04):
portably killing a process between temp-write and commit, simulating
disk-full, and denying permission, on both Windows and POSIX, with stdlib
only. `tests/durability_roundtrip.py` (the Windows append-durability spike)
is a full worked example of exactly this discipline, including a subprocess
harness and platform-conditional probes, and should be read line-for-line
before 14A-04 is planned.

**Primary recommendation:** build 14A as two new root-level peer modules
(e.g. `identity.py` for ID/fingerprint/revision minting, `journal.py` for the
compare-and-swap write plus the append-only operation log), each following
`evidence.py`'s documented peer-module contract exactly, and lift the
compare-and-swap/atomic-commit/undo mechanics from `audit_writer.py` almost
verbatim rather than re-deriving them.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Opaque ID minting (course/objective/source/lesson/bank/item/component) | Domain/model tier (new `identity.py`, peer to `model.py`) | - | Mirrors `model.new_item_id()`'s placement: identity is a model-tier concern, not a runtime-tier or surface-tier one (`model.py` docstring conventions; `evidence.py:11-14` names the tier split explicitly). |
| Fingerprint computation and normalization | Domain/model tier (`identity.py`) | - | Fingerprinting is a pure function of content; it must not depend on the journal or on any surface. Same reasoning as `model.content_fingerprint()` and `authoring.bank_fingerprint()`, both pure functions with no I/O. |
| Compare-and-swap write, atomic commit, operation journal append | Runtime tier (new `journal.py`, peer to `runtime.py` and `evidence.py`) | - | This is a write-path authority concern, the same tier `runtime.write_session()` and `evidence.append_event()` already occupy. It is never a surface concern (no surface reimplements it) and never a model-tier concern (the model tier has no I/O). |
| Operation vocabulary (link/import/copy/move/edit-in-place/supersede) | Runtime tier (`journal.py`) | Course-builder-facing wording lives in 16A/16B surfaces later | The operation TYPE is a journal-tier fact recorded once; how a surface later *labels* an operation to a human is presentation, out of scope for 14A. |
| External-edit detection (stale/conflict state) | Runtime tier (`journal.py`, read path) | - | Detecting that bytes changed outside the journal is a fingerprint comparison against the last known revision - pure runtime-tier logic, no UI. |
| Fault-injection tracer (14A-04) | Test tier (`tests/`) | - | Follows the existing `tests/*_roundtrip.py` / `tests/durability_roundtrip.py` convention exactly; it is not product code. |
| Rights grant storage | Course-record tier (14B, out of scope for 14A) | Identity kernel reserves a field slot (14A) | 14A only needs to leave room for a `rights` field on the source object shape so 14B's D-12.6-9 rights work does not require a schema break; 14A does not enforce rights. |

## Standard Stack

### Core

No new external dependency is required or recommended for this phase. Every
mechanism 14A needs (`uuid`, `hashlib`, `os`, `json`, `re`, `time`,
`msvcrt`/`fcntl`, `contextlib`, `subprocess` for the fault-injection harness)
is already imported by shipped modules in this repository (`model.py`,
`runtime.py`, `evidence.py`, `audit_writer.py`, `authoring.py`,
`tests/durability_roundtrip.py`). This is consistent with the project's
"preference, not rule" stance on stdlib-only (`.claude/CLAUDE.md` Constraints,
2026-08-09 amendment): the honest reason to stay stdlib here is that the
stdlib primitives are already proven correct in this exact codebase under
Windows CRT's non-atomic `O_APPEND` (`evidence.py:131-141`, bpo-42606), not a
blanket no-dependency rule.

| Library | Version | Purpose | Why Standard (in this repo) |
|---------|---------|---------|------------------------------|
| `uuid` (stdlib) | 3.11+ | Opaque ID minting | `model.new_item_id()` already uses `uuid.uuid4().hex[:16]`; `evidence.new_event_id()` uses the full `uuid.uuid4().hex`. Reuse one of these two shapes rather than inventing a third. |
| `hashlib` (stdlib) | 3.11+ | Fingerprint/content-hash computation | `authoring.bank_fingerprint()`, `model.content_fingerprint()`, `evidence.dedupe_key()` all use `hashlib.sha256`. |
| `os` (stdlib, `os.replace`) | 3.11+ | Atomic same-filesystem file replacement | `runtime.write_session()` (`runtime.py:1430-1437`) and `audit_writer.py`'s `_write_json`/`_write_bytes_atomic` (lines 246-265) both use the identical tmp-file-then-`os.replace` idiom. `os.replace` is atomic on both POSIX and Windows when source and destination are on the same filesystem/volume - this is a documented Python stdlib guarantee, not an assumption. |
| `msvcrt` / `fcntl` (stdlib, platform-conditional) | 3.11+ | Cross-platform advisory file locking | `evidence.locked()` (`evidence.py:123-160`) and `audit_writer._bank_lock`/`_try_lock`/`_unlock` (`audit_writer.py:48-105`) are two independent, already-tested implementations of the same pattern. `audit_writer.py`'s version adds a non-blocking acquire with a bounded timeout and an explicit `writer.busy` refusal code - the better template for 14A's journal lock, since 14A's writes are per-object rather than per-append-line. |
| `subprocess` (stdlib) | 3.11+ | Fault-injection harness (spawn-and-kill) | `tests/durability_roundtrip.py:44-63` (`run_writer`/`spawn_writers`) is the exact spawn-then-`terminate()` pattern 14A-02/14A-04 need for the "kill between temp write and commit" fixture. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `time` (stdlib) | 3.11+ | Timestamps on manifests/journal entries | `audit_writer.py` uses `time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())`; `evidence.py` uses its own `utc_now()` (`evidence.py:108-116`) with millisecond precision and a `Z` suffix. **Decision needed at plan time:** pick one timestamp format for the new journal, not a third format. Recommend reusing `evidence.utc_now()` since it is already the project's evidence-adjacent timestamp convention and journal entries are evidence-adjacent records. |
| `contextlib` (stdlib) | 3.11+ | Lock context managers | Both `evidence.locked()` and `audit_writer._bank_lock()` are `@contextlib.contextmanager` functions. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Building a new lock primitive for the journal | `sqlite3`'s own locking (a single SQLite journal-of-record file) | Rejected for 14A: the project has a working, tested, dependency-free advisory-lock pattern in two places already (`evidence.py`, `audit_writer.py`); introducing SQLite as the journal's source of truth would violate "the log is the only authority" discipline `evidence.py:5-9` states for the evidence log, and 14A's own decisions record (D-14A-1) explicitly wants the journal to stay a readable, diffable artifact, not a binary database. `evidence.py`'s own `INDEX_VERSION`/`ensure_index()` sqlite3 usage (lines 1040-1300) is instructive as a **disposable projection** pattern if 14A ever wants a fast per-object journal query cache later - but the sqlite3 file must stay a rebuildable cache, never the journal of record. |
| Hand-rolled JSON diff for the "real-diff corpus check" 14A-04 owes | Python's stdlib `difflib` | `difflib.SequenceMatcher` is already used elsewhere in this codebase for exact-byte-preservation testing (per `04-02` decision log entry in `STATE.md`: "tests prove exact-byte preservation with a common-prefix/suffix single_replacement helper because difflib SequenceMatcher opcodes are alignment-dependent and non-minimal"). Note the caveat recorded there - `SequenceMatcher` opcodes are not minimal - if 14A-04's reflow-decision corpus check needs a minimal diff, a common-prefix/suffix helper (already written once) is the safer starting point than `difflib` alone. |

**Installation:** none required; every listed module is Python 3.11+ stdlib,
already imported elsewhere in this repository.

**Version verification:** not applicable - no third-party package is being
added. `python --version` on the CI image is pinned at 3.11 in
`.github/workflows/ci.yml:10-12` (`actions/setup-python@v5`, `python-version:
"3.11"`) [VERIFIED: .github/workflows/ci.yml:10-12].

## Package Legitimacy Audit

**Not applicable to this phase.** 14A adds no third-party package to any
ecosystem. Every primitive it needs is Python 3.11+ standard library and is
already imported by shipped modules in this repository (see Standard Stack
above). The Package Legitimacy Gate protocol therefore has nothing to check;
no `npm view` / `pip index versions` / registry lookup was run because no
package name is proposed.

**Packages removed due to [SLOP] verdict:** none (none proposed).
**Packages flagged as suspicious [SUS]:** none (none proposed).

## Architecture Patterns

### System Architecture Diagram

```
                    ┌─────────────────────────────┐
                    │   Caller (surface, CLI, or   │
                    │   a future skill/agent job)   │
                    └───────────────┬───────────────┘
                                    │  1. mint or look up an object's ID
                                    ▼
                    ┌─────────────────────────────┐
                    │   identity.py (new, model    │
                    │   tier, no I/O)               │
                    │   - new_object_id()           │
                    │   - object_fingerprint(bytes)  │
                    │     (normalizes trailing ws +  │
                    │      line endings, D-14A-2)     │
                    │   - component_id() for cited/  │
                    │     gated/evidence-bearing      │
                    │     lesson blocks only          │
                    └───────────────┬───────────────┘
                                    │  2. caller has: object_id,
                                    │     expected_base_fingerprint,
                                    │     new bytes
                                    ▼
                    ┌─────────────────────────────┐
                    │   journal.py (new, runtime    │
                    │   tier, peer of runtime.py     │
                    │   and evidence.py)             │
                    │                                 │
                    │   commit_operation(             │
                    │     object_id, op_type,         │
                    │     expected_fingerprint,        │
                    │     new_bytes, actor, ...)       │
                    │                                 │
                    │   ┌─────────────────────────┐   │
                    │   │ 3. acquire per-object    │   │
                    │   │    OS lock (msvcrt/fcntl,│   │
                    │   │    bounded timeout,      │   │
                    │   │    audit_writer._bank_lock│   │
                    │   │    pattern)               │   │
                    │   └────────────┬─────────────┘   │
                    │                ▼                  │
                    │   ┌─────────────────────────┐   │
                    │   │ 4. re-read current bytes, │   │
                    │   │    recompute fingerprint, │   │
                    │   │    compare to expected     │   │
                    │   │    -> mismatch = REFUSE     │   │
                    │   │    (conflict, ID-02)        │   │
                    │   └────────────┬─────────────┘   │
                    │                ▼ match             │
                    │   ┌─────────────────────────┐   │
                    │   │ 5. write journal entry     │   │
                    │   │    (prepared state) BEFORE  │   │
                    │   │    any mutation - undo       │   │
                    │   │    pointer to prior revision │   │
                    │   │    (audit_writer prepared-   │   │
                    │   │    manifest-before-mutation   │   │
                    │   │    pattern)                    │   │
                    │   └────────────┬─────────────┘   │
                    │                ▼                  │
                    │   ┌─────────────────────────┐   │
                    │   │ 6. write NEW_bytes to .tmp, │   │
                    │   │    os.replace() into place   │   │
                    │   │    (runtime.write_session /  │   │
                    │   │    audit_writer._write_shadow)│  │
                    │   └────────────┬─────────────┘   │
                    │                ▼                  │
                    │   ┌─────────────────────────┐   │
                    │   │ 7. re-read + verify after-  │   │
                    │   │    fingerprint guard; mark   │   │
                    │   │    journal entry "applied"    │   │
                    │   └────────────┬─────────────┘   │
                    │                │ release lock      │
                    └────────────────┼────────────────┘
                                    ▼
                    ┌─────────────────────────────┐
                    │  Object's durable revision      │
                    │  record on disk: (id, revision, │
                    │  fingerprint, parent revision,   │
                    │  timestamp, origin)              │
                    └─────────────────────────────┘

External-edit detection (read path, no write):
  reader loads object bytes -> recomputes fingerprint -> compares to the
  journal's last recorded fingerprint for that object_id -> mismatch with
  no matching journal entry = "stale/conflict, external edit" (FILE-01,
  RELIABILITY-01 degraded-state clause).
```

### Recommended Project Structure

```
identity.py          # NEW, root-level peer of model.py: opaque ID minting,
                      # fingerprint computation + normalization, revision
                      # record shape. No I/O beyond what callers hand it.
journal.py            # NEW, root-level peer of runtime.py/evidence.py:
                      # compare-and-swap write, atomic commit, append-only
                      # operation log, undo, external-edit detection.
tests/
  identity_roundtrip.py       # 14A-01
  journal_roundtrip.py        # 14A-02
  operations_roundtrip.py     # 14A-03
  file_fault_tracer.py        # 14A-04 (freeze gate)
fixtures/
  <synthetic multi-root tree for 14A>/   # lives under fixtures/, exempt from
                                         # `itembank guard` by construction
                                         # (surfaces/cli.py:322-326 excludes
                                         # the fixtures/ directory outright)
```

**Where the journal/registry files live on disk (per additional_context item
7):** follow the existing `_evidence/` precedent exactly - a hidden,
`.gitignore`d directory living **beside** the object it describes, the same
way `evidence.evidence_dir(base)` resolves to `os.path.join(os.path.abspath(base),
"_evidence")` [VERIFIED: evidence.py:95-97, quoted: `def evidence_dir(base):\n    """The \`_evidence/\` directory beside the bank or plan living in \`base\`."""\n    return os.path.join(os.path.abspath(base), EVIDENCE_DIRNAME)`].
Recommend a new `_journal/` directory beside the object root (or beside the
course root once 14B exists), added to `.gitignore` the same way `_attempts/`
and `_evidence/` already are (`.gitignore:12,14`). This keeps 14A consistent
with the data-residency rule ("evidence and banks stay on disk... no cloud
sync") and with `SOURCE-TO-COURSE.md`'s repeated instruction that "any
machine index is derived and disposable" - the journal is NOT disposable (it
is the operation record of truth per RELIABILITY-02's "journal is the durable
job record, not a chat transcript"), so it must NOT live in a directory named
like a cache, and it must be included in whatever `itembank guard`/backup
story 14B eventually builds for course data, unlike `_evidence`'s own index
file which genuinely is disposable.

### Pattern 1: opaque ID minting and change-detection fingerprinting (14A-01)

**What:** every durable object gets an ID assigned once, at creation, that
never changes; a fingerprint is a separate, recomputed-on-demand value used
only to detect change, never as the key.

**When to use:** every object 14A-01 must mint an ID for: course, objective,
source, lesson, bank, plus bounded component IDs for cited/gated/
evidence-bearing lesson blocks. **Not** for items (they keep the shipped
`[ID:]` scheme untouched per the phase brief).

**Example (the shipped item-identity precedent to generalize):**
```python
# Source: model.py:1514-1522 (read this session)
def new_item_id():
    """A 64-bit-random opaque id, short enough to read in an `[ID:]` line.

    An accidental collision across a personal bank is negligible, and D-05
    makes these globally unique across every bank a caller assigns into
    together, so renaming or splitting a bank file cannot orphan an item's
    evidence history.
    """
    return uuid.uuid4().hex[:16]
```
```python
# Source: model.py:1451-1471 (read this session) - the fingerprint precedent
def content_fingerprint(q):
    """A change-detection digest of the *tested* content only, never the
    rationale around it.

    Deliberately excludes `why`, `disc`, `second`, `trap`, `conf`, `da`,
    `notes`, `objective`, `difficulty`, `number`, `id`, `item_id`, `pair`,
    `prereq` and `content_hash` -- the hash's job is to detect that stem, options, correct
    answers, categories, rows, steps, model answer or rubric changed...
    """
```
**What 14A-01 must add that this precedent does not have:** normalization of
trailing whitespace and line endings *before* hashing (D-14A-2). Verified
this session: `authoring.bank_fingerprint()` hashes exact bytes with **no**
normalization (`authoring.py:176-179`, quoted: `def bank_fingerprint(text):\n
"""The change-detection fingerprint of the exact bank text bytes, used\n
as the writer's expected-fingerprint guard (D-17/T-11-02)."""\n    return
"sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()`) - so 14A-01's
`object_fingerprint()` is genuinely new code, not a reuse of
`bank_fingerprint()` as-is. The safe implementation is: normalize a copy of
the bytes for hashing (strip trailing whitespace per line, normalize `\r\n`/`\r`
to `\n`) while never mutating the object's stored bytes, and keep this
normalization in a single named function so the 14A-04 tracer's "real-diff
corpus check that decides reflow normalization" has exactly one place to
extend later.

### Pattern 2: compare-and-swap write with atomic commit (14A-02)

**What:** the full mechanism RELIABILITY-01 asks for already ships, nearly
verbatim, in `audit_writer.py` (Phase 11). This is the single most valuable
precedent in the repository for 14A-02.

**When to use:** every durable mutation 14A-02 performs.

**Example (the precedent to generalize - read `audit_writer.py` in full
before planning 14A-02):**
```python
# Source: audit_writer.py:288-322 (read this session) - the CAS guard shape
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
```python
# Source: audit_writer.py:346-402 (read this session) - prepared-before-
# mutation manifest, atomic replace, after-fingerprint guard
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
```python
# Source: runtime.py:1430-1437 (read this session) - the simpler tmp+replace
# idiom `_write_json`/`_write_bytes_atomic` above both derive from
def write_session(path, data):
    target = session_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)
```

**What 14A-02 must generalize that `audit_writer.py` does not need:**
`audit_writer.py` is scoped to exactly one target kind (a bank file text
blob) and one backend choice (shadow vs. git, decided per-call). 14A-02's
journal must work over heterogeneous object kinds (course/objective/source/
lesson/bank/component) with one write path, and it must record an **undo
pointer** as part of every journal entry (not a separate `undo()` lookup
keyed by write_id alone) since the phase brief specifically calls for "a
journal entry with the undo pointer." Recommend keeping `audit_writer.py`'s
`WriterError`-with-typed-`code` pattern (`writer.stale_preflight`,
`writer.after_guard_failed`, `undo.stale_target`, etc.) - it is a clean,
already-proven shape for the refusal codes RELIABILITY-01/ID-02 need
(e.g. `journal.conflict`, `journal.stale_preflight`).

### Pattern 3: operation vocabulary as distinct journal entries (14A-03)

**What:** link, import, copy, move, edit-in-place, and supersede are six
**distinct operation types** recorded in the journal, not six code paths that
each reimplement the compare-and-swap write. Each operation type differs only
in its provenance effect (what it says happened) and its identity effect
(whether a new ID is minted or an existing one is reused), never in the
write mechanism itself.

**When to use:** 14A-03 extends 14A-01/14A-02; it should not introduce a
second write function.

**Example (the closest shipped precedent - a typed, closed vocabulary of
operations distinguished by one field, never six functions):**
```python
# Source: evidence.py:51-55 (read this session) - the KNOWN_EVENT_TYPES
# closed-vocabulary precedent this repo already uses for a similar problem
KNOWN_EVENT_TYPES = ("response", "retraction", "mark", "day_tick",
                     "term_lookup", "key_review", "hint", "selection",
                     "lesson_complete", "cap_override",
                     "model_interaction", "mark_proposal", "visual_action",
                     "gate_skip")
```
Recommend the same shape for the journal's `operation_type` field: a closed
tuple `OPERATION_TYPES = ("link", "import", "copy", "move", "edit_in_place",
"supersede")`, validated at journal-write time, with `evidence.py:764-772`'s
degrade-not-crash posture on an unrecognized type when reading an older
journal (skip and warn, never raise) - matching `events()`'s handling of an
unknown `event_type`.

**Same-ID-divergent-bytes conflict (ID-02):** this is the CAS mismatch path
already shown in Pattern 2 (`writer.stale_preflight` in `audit_writer.py`);
14A-03 just needs to name this specific case in its refusal message and
surface it as `journal.conflict` rather than reusing a generic staleness
code, since the phase brief and ID-02 both require the conflict to be
*distinguishable* from ordinary staleness (a conflict has a competing
revision; plain staleness may not).

### Anti-Patterns to Avoid

- **A second atomic-write helper.** `runtime.write_session()`,
  `audit_writer._write_json`/`_write_bytes_atomic`, and
  `evidence.rebuild_index()` (which explicitly says "written through `index +
  ".tmp"` and then `os.replace()`'d into place -- the same tmp-then-replace
  pattern `runtime.write_session()` uses", `evidence.py:1126-1131`) are
  already three call sites agreeing on one idiom. A fourth, slightly
  different implementation in `journal.py` is a regression, not a phase
  deliverable.
- **Content-hash-as-ID.** The rejection ledger already hard-rejects this
  (cited in `DECISIONS-PRE-14A-2026-08-14.md` D-14A-2: "the research
  independently found that content-hash-as-ID silently orphans a learner's
  evidence history on every edit"). Mint the ID once with `uuid4`; store the
  fingerprint as a separate, recomputable field.
- **A second locking primitive.** Two are already shipped and tested
  (`evidence.locked()`, `audit_writer._bank_lock()`). Reuse one; do not add a
  third `msvcrt`/`fcntl` wrapper.
- **Storing the journal as a database file that is also the source of
  truth.** `evidence.py`'s own sqlite3 index is explicitly a "disposable
  materialized view... never a second source of truth" (`evidence.py:1030-1038`).
  If 14A ever adds a query cache over the journal, it must be similarly
  disposable and rebuildable, never the record itself.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Atomic same-directory file replace | A custom "safe write" wrapper | `os.replace(tmp, target)` after writing `target + ".tmp"` | Already the proven idiom in three modules (`runtime.py`, `audit_writer.py`, `evidence.py`); `os.replace` is documented-atomic on the same filesystem on both platforms this project targets. |
| Cross-platform advisory locking | A new lock library or a lockfile-with-PID scheme | `msvcrt.locking`/`fcntl.flock`, following `audit_writer._bank_lock()`'s non-blocking-with-timeout shape | Already solves the exact Windows CRT `O_APPEND` non-atomicity bug (bpo-42606) this project has already characterized and tested against (`evidence.py:131-141`). |
| Fault-injection process control | A custom process supervisor or a third-party fault-injection framework | `subprocess.Popen` + `.terminate()` + `time.sleep()` timing, following `tests/durability_roundtrip.py:44-63,185-239` | Already a complete, working example in this exact repository, tuned for both platforms. |
| Diffing two revisions for the reflow-decision corpus check | A third-party diff library | stdlib `difflib`, with the documented caveat that `SequenceMatcher` opcodes are non-minimal (see Alternatives Considered above) and a common-prefix/suffix helper may be needed for a minimal diff | The project has already hit and solved this exact tradeoff once (04-02 decision log entry, `STATE.md`). |
| A closed vocabulary of typed records with graceful degrade on an unknown value | An enum class or a third-party validation library | A module-level tuple constant plus an explicit `if x not in KNOWN` skip-and-warn check | `evidence.KNOWN_EVENT_TYPES` / `evidence.events()` is the shipped, tested pattern; it is plain Python, no dependency, and already proven to degrade instead of crash on a future/unknown record. |

**Key insight:** almost nothing in 14A is a new algorithm. It is new
*generalization* of four already-shipped, already-tested mechanisms
(item identity, session atomic write, audit-writer compare-and-swap, evidence
append-only log) into object-agnostic peer modules. The highest-risk mistake
this phase can make is re-deriving one of these from first principles instead
of reading and generalizing the shipped code.

## Runtime State Inventory

> Included because D-14A-3 (the `mastered` field) is a rename/migration
> obligation that 14A-01 explicitly owes ("The `mastered` field migration
> mapping is recorded with 14A-01's revision work", 14A-BRIEF.md line
> 113). This inventory answers: after every file is updated, what runtime
> state still has the old string cached, stored, or registered?

**Verified this session: `mastered` is a computed retention STATE, not a
stored evidence-log field.** This changes the shape of the migration work
significantly from what "rename an evidence field" implies.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data (evidence log / attempt files) | **None.** `evidence.py`'s `KNOWN_EVENT_TYPES` and `response_event()` (`evidence.py:394-446`, read in full this session) carry no field named `mastered`. The evidence log stores raw response events only; `mastered` never appears in an event dict. | No evidence-log migration needed. `RELIABILITY-01`'s "shipped tests must stay byte-compatible" obligation (audit item A6) is therefore satisfied trivially for the evidence log - there is nothing there to change. |
| Published schema / API contract | **One published enum value.** `schemas/report.schema.json:228-234` [VERIFIED: schemas/report.schema.json:228-234, quoted: `"properties": {\n  "state": {\n    "type": "string",\n    "enum": ["unknown", "weak", "mastered", "at-risk", "due", "stable"]\n  },`]. This is a schema-level contract that `schema_validate.py` checks in CI (`.github/workflows/ci.yml:152-153`, "Every published schema self-checks"). | Renaming the enum value is a **published-schema break**, not an additive change (violates CLAUDE.md non-negotiable #4, "format changes are additive"). Recommend: 14A-01 does NOT rename this enum value. It records the migration MAPPING (old label -> new fill-state concept) and leaves the schema/enum rename itself to whichever phase actually surfaces the new display (16B, per the phase brief's own routing: "the display semantics stay in 16B"). |
| Live computed logic | `retention.py:287,414-416,445-449,546-548` (read this session) - `STATES = ("unknown", "weak", "mastered", "at-risk", "due", "stable")`, `objective_state()`'s branch returning `{"state": "mastered", "due": False}`, `state_reason()`'s mastered-branch prose, and `recommendation_weight()`'s `"mastery": -cfg["mastery_reduction"] if st == "mastered" else 0.0` term. | This is the actual "field" D-14A-3 is renaming - it is a **label in a closed tuple constant plus branch logic in `retention.py`**, consumed by `surfaces/study.py`, `surfaces/day.py`, `surfaces/retention_view.py`, `selection.py`, and `schemas/report.schema.json`. A full rename touches five files and one published schema. **14A-01 should record this mapping as a plan-level note, not execute the rename itself**, since the phase brief scopes 14A-01 to recording the mapping, and the actual display-facing rename is explicitly routed to 16B. |
| OS-registered state | None found. `mastered` is not a filename, directory name, task name, or environment variable anywhere this session's grep touched. | None - verified by grep across the full repository tree; no OS-level registration references this string. |
| Secrets / env vars | None found. No settings key, SOPS key, or env var named `mastered` appears in `schemas/settings.schema.json`'s surrounding context beyond the enum note captured above. | None. |
| Build artifacts / installed packages | Not applicable - `mastered` is source-level Python/JSON, not a package or build-artifact name. | None. |
| Unrelated naming collision (flagged so it is not mistaken for the same thing) | `surfaces/study.py:267,335,352,354,365` uses a **client-side JavaScript variable** named `mastered` as a per-session flashcard counter in the Learn mode UI (`let mode="flash",order=[],i=0,queue=[],mastered=0;`). This is unrelated to the evidence/retention `mastered` state - it is ephemeral browser state, never persisted, never read by any tool. | **Do not rename this** as part of D-14A-3; it is coincidental naming, not the same durable object. Renaming it would be scope creep with no decision backing it. |

**Bottom line for the planner:** 14A-01's D-14A-3 obligation is narrow -
record the mapping (old `mastered` state label -> new `evidence_support`
per-objective fill-state concept) as a decision artifact, and note explicitly
in the plan that the actual schema enum, `retention.py` constant, and the
five consuming call sites are NOT touched by 14A (they are 16B's obligation
per the phase brief's own text). Attempting the full rename inside 14A-01
would both violate the additive-format-change non-negotiable (the enum is a
published schema) and duplicate work 16B is scoped to do with the level
vocabulary decision it still owes.

## Common Pitfalls

### Pitfall 1: treating `os.replace` as sufficient without re-verifying after the write

**What goes wrong:** a compare-and-swap write can still corrupt state if the
process is killed between the successful `os.replace()` and the caller
recording that the write succeeded - the bytes on disk are correct, but the
in-memory/journal bookkeeping never learns that.

**Why it happens:** `os.replace` is atomic for the file's *bytes*, but a
crash immediately after it, before the journal entry is marked "applied,"
leaves the journal thinking the write is still "prepared."

**How to avoid:** `audit_writer.py` already solves this by writing the
manifest in `"prepared"` state *before* the mutation, then re-reading the
target and updating the manifest to `"applied"` *after* a verified
after-fingerprint match (`audit_writer.py:390-401`). A crash between commit
and the "applied" mark leaves a `"prepared"` manifest that a recovery pass
can detect (the target's actual fingerprint matches `after_fingerprint`) and
repair by simply flipping the state - this exact recovery case is what
14A-02's fixture "kill between commit and journal append" (14A-BRIEF.md
line 71) is testing.

**Warning signs:** a journal replay that trusts only the entry's own `state`
field without re-reading the actual current fingerprint of the target will
silently misreport a successfully-committed write as failed (or vice versa).

### Pitfall 2: content-hash-as-ID (already hard-rejected, worth restating precisely)

**What goes wrong:** using the fingerprint itself as the object's identity
means every edit mints a "new" object, silently orphaning all evidence tied
to the old identity.

**Why it happens:** it is tempting because it needs no extra minting step
and gives free deduplication.

**How to avoid:** `model.py`'s entire `[ID:]`/`[HASH:]` split exists
specifically to prevent this (`model.py:1786-1790`, quoted: "`[ID:]` and
`[HASH:]` are both optional... `[ID:]` is assigned once by `itembank
id-assign` and is never edited by hand. `[HASH:]` is a fingerprint of the
tested content, used only to detect that an item changed. The ID is what
evidence is recorded against, so deleting it orphans that item's history.").
14A must keep this split for every object kind it mints.

**Warning signs:** a "duplicate" detector that treats two same-fingerprint
objects as automatically identical, without an ID comparison first - this
collapses ID-02's three distinct outcomes (conflict / copy-candidate /
move-candidate) into one.

### Pitfall 3: symlink cycles and out-of-root symlinks on discovery (FILE-02)

**What goes wrong:** a naive `os.walk` follows a symlink cycle into infinite
recursion, or follows a symlink that points outside the approved root,
silently widening the read boundary FILE-02 requires to stay root-bounded.

**Why it happens:** `os.walk`'s default `followlinks=False` already protects
against directory-symlink traversal by default - the risk is a plan author
setting `followlinks=True` without realizing the default is already correct,
or manually resolving symlinks with `os.path.realpath` without tracking
already-visited real paths (which reintroduces the cycle risk for symlinks
that point at each other rather than at themselves).

**How to avoid:** keep `os.walk`'s default `followlinks=False` (do not
override it), and if the fixture wants to prove the cycle is handled rather
than merely avoided, explicitly resolve each symlink target with
`os.path.realpath` and check it against a `set()` of already-visited real
paths before descending, refusing (not silently skipping) any target whose
real path falls outside the approved root. No stdlib call is missing here -
this is a discipline the fixture's synthetic tree exists to verify, not a
new library need.

**Warning signs:** the D-12.6-10 corpus generator seeding "a symlink cycle
and an out-of-root symlink" (FILE-02's own fixture sentence) must actually
hang or leak outside the root if this pitfall is present - so this pitfall is
self-detecting if the fixture is built correctly, which is exactly why the
fixture sentence names it explicitly.

### Pitfall 4: normalizing keyed assessment content when computing a fingerprint

**What goes wrong:** D-14A-2's trailing-whitespace/line-ending normalization,
applied carelessly, could strip a change that is scoring-relevant (for
example, a trailing space inside a `> [!KEY]` cloze answer, or a line-ending
difference inside a `check` item's expected stdout).

**Why it happens:** the normalization function is written once and applied
uniformly to "content" without distinguishing assessment-bearing content
from ordinary prose.

**How to avoid:** the phase brief is explicit that this must be
"regression-asserted" (14A-01 must have a test proving it). The existing
precedent for *not* normalizing keyed content is `model.content_fingerprint()`
itself, which hashes tested fields exactly as authored with no normalization
step at all (`model.py:1451-1471`). 14A-01's `object_fingerprint()` should
apply whitespace/line-ending normalization only to the object's *storage
bytes* (the file-level fingerprint used for the CAS guard), and must never
be substituted for `model.content_fingerprint()`'s own scoring-relevant
digest, which stays untouched. These are two different fingerprints serving
two different purposes and must not be unified into one function.

**Warning signs:** a lint or test that fires `item.content_drift`
unexpectedly (or fails to fire when it should) after 14A ships is the
concrete regression signal - `model.py:2989-2996`'s `item.content_drift`
warning is the load-bearing existing test surface to check against.

## Code Examples

### The full atomic-write idiom (verbatim, three independent confirmations)

```python
# Source: runtime.py:1430-1437
def write_session(path, data):
    target = session_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)
```

### Cross-platform advisory locking with a bounded timeout and explicit busy refusal

```python
# Source: audit_writer.py:48-92 (read this session)
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

### Fault-injection spawn-and-kill harness

```python
# Source: tests/durability_roundtrip.py:44-63,185-210 (read this session)
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

# probe_kill() (lines 185-239) spawns a writer subprocess, sleeps 0.2s, then
# proc.terminate(); proc.wait() -- the exact "kill between temp write and
# commit" shape 14A-02/14A-04's fixtures need, generalized from one append
# call to one compare-and-swap write call.
```

### The peer-module docstring contract every new 14A module should restate

```python
# Source: evidence.py:1-19 (read this session) - the exact contract to
# restate (with "identity"/"journal" substituted for "evidence log") at the
# top of identity.py and journal.py
"""The evidence log: the one append-only store every later plan writes into and reads from.

`evidence.py` is to the evidence store what `runtime.score_response` is to scoring: the
single primitive every surface calls, so no surface reimplements its own append or its
own read. ...

This module is a peer of `runtime.py`, not an extension of it, and it is never imported
by `model.py` — the same layer split `runtime.py`'s own docstring describes holds here:
identity lives in the model tier, scoring and sessions live in the runtime tier, and the
evidence log is a new runtime-tier primitive beside them.
"""
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `authoring.bank_fingerprint()`: exact-byte SHA-256, no normalization | 14A's `object_fingerprint()` must normalize trailing whitespace + line endings first (D-14A-2) | This phase (14A) | Two fingerprint functions will coexist for a while (`bank_fingerprint` for the Phase 11 auditor's own writer, the new normalized one for 14A's journal). Do not unify them in this phase - `audit_writer.py` is a working, tested system that 14A should not modify as a side effect. |
| One-off compare-and-swap logic scoped to bank text only (`audit_writer.py`) | A general, object-agnostic compare-and-swap journal (14A-02) | This phase (14A) | 14A-02 is the generalization step; `audit_writer.py` itself is not expected to be refactored to use the new journal in this phase (out of scope; the phase brief does not mention touching `auditor.py`/`audit_writer.py`). |

**Deprecated/outdated:** nothing yet deprecated by this phase. 14A is
additive - it introduces new modules and does not modify `audit_writer.py`,
`runtime.py`, or `evidence.py` (only reads their patterns). Any plan that
proposes editing those three files should be treated as scope creep unless
explicitly justified.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Recommending `_journal/` as the new directory name and placement (beside the object root, `.gitignore`d like `_evidence/`/`_attempts/`) | Recommended Project Structure | Low - this is Claude's-discretion naming per the phase brief's silence on exact directory names; if the planner or 14B prefers a different name, only the directory constant changes, not the architecture. |
| A2 | Recommending `evidence.utc_now()`'s timestamp format for journal entries, over `audit_writer.py`'s `time.strftime` format | Standard Stack > `time` row | Low - both are ISO-8601-shaped; picking one consistently matters more than which one. |
| A3 | Recommending the journal record an "actor" field to stay compatible with the still-pending D-12.6-4 self-acceptance decision | User Constraints > Discretion Areas | Low-medium - if 14B/15B's acceptance model turns out to need more than a single actor field (e.g., a full manifest of intent/scopes per RELIABILITY-02), the field may need to grow; additive-field discipline (already the project's own rule) mitigates this. |
| A4 | Treating the 100k-file corpus size from D-12.6-10 as optional/stretch for 14A-04, since the phase-brief plan text for 14A-04 names only "the D-12.6-10 budgets... on the 1k/10k corpora" | Discretion Areas | Medium - if the planner disagrees and believes 100k is required reading of D-12.6-10, this changes 14A-04's scope and runtime; flagged explicitly so the planner makes this call deliberately rather than by omission. |
| A5 | Recommending `WriterError`-style typed refusal codes (`journal.conflict`, `journal.stale_preflight`, etc.) for the new journal, modeled on `audit_writer.WriterError` | Architecture Patterns > Pattern 2 | Low - this is an internal error-shape convention; changing it later is a mechanical rename, not an architecture change. |

**If this table is empty:** not applicable - the table above lists the
judgment calls made when reconciling read code with the phase brief's
intentionally spare prescription. Every locked decision (D-14A-1/2/3,
D-12.6-10 core numbers) is cited to its resolved source, not assumed.

## Open Questions

1. **Exact shape of the "revision record" tuple**
   - What we know: the phase brief names the fields explicitly - "(id,
     revision, fingerprint, parent revision, timestamp, origin)"
     (14A-BRIEF.md line 49).
   - What's unclear: whether `revision` is an integer counter, a hash, or an
     opaque revision-id string (the R1-R10 requirements in
     `research/phase-16/16-editor-reader-landscape.md` section 4 use "base
     fingerprint" and "revision object" language but do not pin the type).
   - Recommendation: an integer counter per object (0, 1, 2, ...) is simplest
     to reason about for "parent revision" and journal ordering, and is
     consistent with `evidence.py`'s own `attempt_number()` precedent
     (an incrementing integer scoped to one identity). Recommend the planner
     lock this as an integer in the 14A-01 plan rather than leaving it
     open for the executor to guess (per PLANNING-DIRECTIVES.md section 5's
     executor-bar rule: "find any sentence a reasonable executor could
     implement two different ways; either decide it in the plan").

2. **Whether the 14A-01/14A-02 "walking-skeleton slice" needs its own
   narrower fixture separate from the full 14A-01 fixture tree**
   - What we know: STATE.md and the phase brief both say "13.9 may stub
     course-level storage over the smallest 14A identity/journal slice, which
     is plan 14A-01 plus the journal append of 14A-02" and that "plans are
     ordered so that slice lands first."
   - What's unclear: whether this means 14A-01 should be split into two
     waves (a minimal slice, then the rest) or whether the existing
     single-plan structure already satisfies "lands first" by virtue of
     14A-01 preceding 14A-02/03/04 in the phase's own plan order.
   - Recommendation: the existing plan ordering (14A-01, then 14A-02, 03, 04)
     already satisfies "lands first" at the phase-plan level; no special
     internal restructuring of 14A-01 appears necessary unless 13.9 is
     already blocked waiting on 14A when the planner picks this up - check
     13.9's live status in STATE.md at plan time before assuming the
     ordering constraint is still live.

## Environment Availability

> This phase adds no new external dependency (see Standard Stack /
> Package Legitimacy Audit above). The only environment fact worth recording
> is the symlink-privilege caveat for the FILE-02 fixture.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | All of 14A | Yes (project baseline; `.github/workflows/ci.yml:10-12` pins 3.11) | 3.11+ | None needed - already the project floor. |
| Symlink creation privilege on Windows | 14A-01's synthetic fixture tree ("one symlink cycle") and FILE-02's fixture ("symlink cycle and an out-of-root symlink") | Not verified this session (this is a fixture-construction concern, not a runtime dependency) | - | On Windows, creating a symlink via `os.symlink()` normally requires either Developer Mode enabled or an elevated process (`SeCreateSymbolicLinkPrivilege`), a well-documented Windows constraint. **Portable fallback named per additional_context item 5:** if the CI/dev machine cannot create real symlinks, use `os.link()` (hardlink, same-volume only) to construct a same-ID-different-path duplicate-detection scenario instead, or synthesize the cycle at the directory-walk level with a mocked `os.scandir`/`os.walk` result rather than real filesystem symlinks, and name this substitution explicitly in the 14A-01/14A-04 plan text so the executor is not left guessing whether a `PermissionError` on `os.symlink()` mid-fixture-build is expected. |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** the Windows symlink-privilege case
above; a documented fallback exists and should be named explicitly in the
plan rather than discovered by the executor at fixture-build time.

## Fault-Injection Portability Notes (additional_context item 5, detailed)

For each fault 14A-02/14A-04 must inject, the portable stdlib approach and
its named fallback:

| Fault | Portable stdlib approach | POSIX note | Windows note |
|-------|---------------------------|------------|----------------|
| Kill between temp write and commit | `subprocess.Popen(...)` running a small script that does the temp-write step then sleeps; parent calls `.terminate()` at a timed point, following `tests/durability_roundtrip.py:206-210`'s `time.sleep(0.2); proc.terminate(); proc.wait()` shape | `SIGTERM` is what `.terminate()` sends; the child dies mid-write reliably with the sleep-then-kill timing already proven in the durability spike. | `.terminate()` on Windows calls `TerminateProcess`, which is a hard kill (no cleanup handlers run) - actually the *more* reliable choice for this fixture than a graceful signal, since the fixture wants to prove recovery from an abrupt kill, not a clean shutdown. |
| Disk-full simulation | No portable stdlib way to actually fill a disk safely in CI. Recommend a **mock injection point**: the journal's write function should call a single, named low-level write helper (e.g. `_write_bytes_atomic`) that the fault-injection test can monkeypatch to raise `OSError(errno.ENOSPC, ...)` at a chosen point (before temp-write, after temp-write but before `os.replace`, after `os.replace`). | Same as Windows - this is a code-injection-point concern, not a platform-specific mechanism. | Same as POSIX. |
| Permission-denied pocket | Real, portable, and platform-differing: `os.chmod(path, 0o000)` reliably denies access on POSIX; on Windows, `os.chmod` has much weaker effect on NTFS permissions (Windows ACLs are not fully controlled by the POSIX mode bits `os.chmod` sets) - a read-only *file* attribute (`os.chmod(path, stat.S_IREAD)`) is the more reliable Windows-portable denial to simulate for a **write** refusal, while a genuinely unreadable file on Windows typically needs `icacls`/ACL manipulation, which is not stdlib-portable. | `os.chmod(path, 0o000)` then attempt read/write; expect `PermissionError`. | Recommend testing the **write-denied** case via `os.chmod(path, stat.S_IREAD)` (clears the write bit) rather than attempting a true unreadable-file simulation, and naming this scope limitation explicitly in the 14A-01/14A-04 plan text: "permission-denied" on Windows is simulated as read-only-attribute denial of a write, not a full ACL-level read denial, because the latter is not portably stdlib-achievable. This is consistent with 14A-01's own fixture wording, "a permission-denied pocket," which does not specify read vs. write denial. |
| Symlink cycle / out-of-root symlink | See Environment Availability table above. | `os.symlink()` works without elevated privilege on typical POSIX dev/CI machines. | Needs Developer Mode or elevation; name the `os.link()`/mocked-walk fallback explicitly in the plan. |
| Removable-volume absence stand-in (14A-04 only: "root temporarily missing") | Create a fixture root, run discovery once, then **remove the directory** (`shutil.rmtree`) before the second pass, and assert the tracer reports the root as unavailable rather than crashing. No platform-specific mechanism needed - this is ordinary directory removal, not a device-level simulation. | Works identically. | Works identically. |

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None (no pytest/unittest runner) - direct script execution, matching the whole repository's convention |
| Config file | none - see `.github/workflows/ci.yml:100-105`: `for t in tests/*.py; do python "$t" \|\| exit 1; done` |
| Quick run command | `python tests/identity_roundtrip.py` (or whichever of the four new test files, run individually) |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` (exact CI command, `.github/workflows/ci.yml:100-105`) |

Every new test file must define its own `fail(msg)` helper printing `"FAIL: "
+ msg` and calling `sys.exit(1)` - this is not a shared import, it is
independently defined in every one of the 60+ existing `tests/*_roundtrip.py`
files (verified this session via grep across `tests/`; every file greps to
its own local `def fail(msg):` at the top). New 14A test files should follow
this exact local-helper convention rather than importing a shared test
utility module, since no such shared module exists in this codebase.

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| ID-01 | Every object minted carries id/fingerprint/revision/versions; a fingerprint-stripped object blocks CAS write | unit | `python tests/identity_roundtrip.py` | Wave 0 (14A-01 must create this file) |
| ID-02 | Same-ID-divergent-bytes = conflict; same-fingerprint-different-ID = copy candidate; moved-path-same-ID = move candidate | unit | `python tests/journal_roundtrip.py` and/or `python tests/operations_roundtrip.py` | Wave 0 |
| FILE-01 | Unreachable root reports unavailable; course opens over last valid index | integration (synthetic multi-root tree) | `python tests/identity_roundtrip.py` (fixture: 14A-01's own multi-root tree) | Wave 0 |
| FILE-02 | Discovery read-only, cancellable, symlink-safe, useful before completion | integration | `python tests/identity_roundtrip.py` or a dedicated discovery test | Wave 0 - see the symlink-privilege fallback note above before writing this fixture |
| FILE-03 | Link/import/copy/move/supersede/migrate are distinct, no auto-merge | unit + integration | `python tests/operations_roundtrip.py` | Wave 0 (14A-03) |
| RIGHTS-01 | Unknown rights refuse the unsafe operation by name | unit | `python tests/identity_roundtrip.py` (object shape carries an unfilled `rights` slot defaulting to `unknown`) | Wave 0 |
| RELIABILITY-01 | Fault injection (crash, disk-full, permission-denied) yields old-or-new valid state, never mixed; journal records the operation | integration, fault-injection | `python tests/journal_roundtrip.py` and the freeze-gate `python tests/file_fault_tracer.py` | Wave 0 (14A-02 and 14A-04) |

### Sampling Rate

- **Per task commit:** the single new test file the task's own plan names
  (e.g. `python tests/identity_roundtrip.py` after an 14A-01 task).
- **Per wave merge:** `for t in tests/*.py; do python "$t" || exit 1; done`
  (the full suite) plus `python itembank.py guard .` (the fixture tree must
  stay synthetic and pass the guard - it lives under `fixtures/`, which
  `surfaces/cli.py:322-326` already exempts from the walk, so this should be
  a no-op check, not a design constraint on where fixtures live).
- **Phase gate:** the freeze gate IS the full suite plus
  `tests/file_fault_tracer.py` green, per the phase brief's own wording:
  "identity, journal, and operation semantics are frozen only when the
  tracer is green" (14A-BRIEF.md line 106).

### Wave 0 Gaps

- [ ] `tests/identity_roundtrip.py` - covers ID-01, FILE-01, FILE-02, RIGHTS-01
- [ ] `tests/journal_roundtrip.py` - covers RELIABILITY-01, ID-02 (compare-and-swap half)
- [ ] `tests/operations_roundtrip.py` - covers FILE-03, ID-02 (operation-vocabulary half)
- [ ] `tests/file_fault_tracer.py` - covers RELIABILITY-01's full fault-injection scenario list end to end (freeze gate)
- [ ] `fixtures/<14A synthetic multi-root tree>/` - three roots, nested folders, one symlink cycle, one permission-denied pocket, duplicate-fingerprint pair (14A-01's own fixture sentence, 14A-BRIEF.md line 56)
- [ ] Framework install: none - the repository's `tests/*.py` direct-execution convention needs no new install step.

*(No pytest/unittest scaffolding gap exists - the project deliberately has
none, and 14A should not introduce one.)*

## Security Domain

> `security_enforcement` was not found set to `false` in `.planning/config.json`
> during this research session (the file's presence/contents were not part of
> the required-reading list for this task, and no explicit disable was cited
> in any of the read decision records) - treat as enabled per the default rule.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Single-learner, no-accounts product (`.claude/CLAUDE.md` Constraints, "Users" bullet); 14A introduces no auth surface. |
| V3 Session Management | No | 14A's journal is not a session-auth concept; it is a durable-object write log, unrelated to `runtime.py`'s session JSON. |
| V4 Access Control | Partially | The "unknown rights stay restrictive" rule (RIGHTS-01) is an access-control-shaped concern even though 14A only reserves the field slot rather than enforcing it. No standard library or framework is needed - the control is "default state is restrictive, not permissive," enforced by 14A-01's object-shape default and by 14B's later enforcement. |
| V5 Input Validation | Yes | Every journal entry's `operation_type` must validate against the closed `OPERATION_TYPES` tuple before being written (Pattern 3 above), following `evidence.events()`'s existing skip-and-warn-on-unknown-type discipline. Fingerprint comparisons are exact-string equality, not a partial/fuzzy match, closing the ID-02 conflict/copy/move decision to no ambiguity. |
| V6 Cryptography | Yes (already-established project posture) | `hashlib.sha256` for fingerprints, same as every other hash use in this codebase. `evidence.py:16-18`'s own integrity note applies verbatim to 14A: "this module uses `hashlib.sha256`... purely as a change-detection checksum, never as a security boundary -- this project has a single local user and no attacker in its threat model." 14A must not treat the fingerprint as a security/authenticity guarantee - it is a change-detection value only. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|------------------------|
| TOCTOU (time-of-check-to-time-of-use) between fingerprint check and write | Tampering | The per-object OS lock held across the entire check-then-write sequence (Pattern 2 above, `audit_writer.py:308` - the fingerprint recheck happens *inside* `with _bank_lock(state_dir):`), the same discipline `evidence.append_line_checked()` already documents explicitly: "the whole check-then-append sequence is race-free rather than advisory" (`evidence.py:267-269`). |
| Path traversal via a symlink escaping the approved root | Tampering / Information Disclosure | The `os.path.realpath` + visited-set + root-boundary check described in Pitfall 3 above; refuse (log, do not silently skip) any resolved target outside the approved root. |
| A crafted "moved path with same ID" used to hijack another object's evidence history | Spoofing | ID-02's own rule already covers this: a moved path with the same ID is only a *move candidate*, not an automatic reclassification - the journal must still verify the fingerprint chain (parent revision lineage) before accepting the move, never trusting the path+ID pair alone. |

## Sources

### Primary (HIGH confidence - read directly this session, `[VERIFIED: path:lines]`)

- `runtime.py` (session_path/write_session/read_session, lines 1379-1437) - the atomic-write precedent
- `evidence.py` (module docstring lines 1-19, `locked()` lines 123-160, `append_line`/`append_line_checked` lines 162-293, `KNOWN_EVENT_TYPES`/`events()` lines 51-55,755-774, sqlite3 disposable-index section lines 1030-1300) - the peer-module and closed-vocabulary precedents
- `model.py` (MARKERS/identity-splice comments lines 14-52, `content_fingerprint()` lines 1451-1471, `new_item_id()` lines 1514-1522, `assign_ids()` lines 1624-1652, `[ID:]`/`[HASH:]` spec text lines 1786-1790, `item.content_drift` lint warning lines 2989-2996) - the shipped item-identity scheme
- `audit_writer.py` (full file, 620 lines) - the compare-and-swap/atomic-commit/undo precedent, the strongest single source for 14A-02/03
- `authoring.py` (lines 44-60, 166-190: `canonical_json`, `bank_fingerprint`, `WRITE_SCHEMA_VERSION`) - confirms no existing normalization in the bank fingerprint
- `tests/durability_roundtrip.py` (full file, 268 lines) - the fault-injection harness precedent
- `tests/guard_roundtrip.py` and `surfaces/cli.py:299-351` (`cmd_guard`) - confirms `fixtures/` is exempt from the real-content guard
- `.github/workflows/ci.yml` (full file) - the test-runner convention and CI steps
- `retention.py` (lines 16-22, 65-80, 285-290, 385-420, 428-449, 540-552) and `schemas/report.schema.json:228-234` and `surfaces/study.py:267,335,352,354,365` - the `mastered`-field runtime-state inventory
- `.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md`, `.planning/DECISIONS-PRE-14A-2026-08-14.md`, `.planning/AUDIT-REPORT-14A-2026-08-14.md`, `.planning/DECISIONS-12.6-REMAINING-2026-08-14.md`, `.planning/REQUIREMENTS.md` (FILE-01..03, ID-01/02, RIGHTS-01, RELIABILITY-01 sections), `.planning/STATE.md`, `.planning/PLANNING-DIRECTIVES.md`, `.planning/PLAN-TEMPLATE.md`, `.planning/research/phase-16/16-editor-reader-landscape.md` (section 4), `.agents/skills/OPERATION-CONTRACT.md`, `.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md`, `.gitignore` - all read in full or in the relevant section this session

### Secondary (MEDIUM confidence)

None used - this phase did not require web research; every finding was
verified against the local codebase and planning artifacts, which the
additional_context explicitly prioritized over web research ("this is a
codebase-precedent phase, not a web-research phase").

### Tertiary (LOW confidence)

None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no external dependency; every stdlib module cited is already imported and proven in this exact codebase.
- Architecture: HIGH - the compare-and-swap/atomic-commit/journal pattern is not proposed, it is read directly from `audit_writer.py`, a shipped Phase 11 module solving nearly the identical problem at smaller scope.
- Pitfalls: HIGH for the ones grounded in shipped code and lint messages (content-hash-as-ID, keyed-content normalization, TOCTOU); MEDIUM for the Windows symlink-privilege and disk-full-simulation notes, which are general platform knowledge rather than something verified against this exact machine this session.

**Research date:** 2026-08-14
**Valid until:** 30 days (stable domain - stdlib file I/O primitives and this repository's own established patterns do not move quickly), but re-check immediately if `audit_writer.py`, `runtime.py`, or `evidence.py` are modified by any concurrent phase before 14A executes, since this research's strongest claims are direct quotes from their current line numbers.
