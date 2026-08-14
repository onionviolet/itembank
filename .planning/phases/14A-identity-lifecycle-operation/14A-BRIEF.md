# Phase 14A plan: identity, lifecycle, and operation prototype

**Status:** planned 2026-08-14, unblocked by `AUDIT-REPORT-14A-2026-08-14.md`.
**Definition of done:** the 14A freeze gate from synthesis section 15: the
**file-fault and external-edit tracer** passes end to end. Nothing else closes
this phase; polish, graph work, and course packaging belong to 14B.

**Binding inputs:**

- Resolved decisions `D-14A-1` (hybrid graph storage; only the inline-edge side
  matters in 14A), `D-14A-2` (object-level opaque IDs plus bounded component
  IDs; whitespace and line-ending normalization first, reflow decided by this
  phase's tracer), `D-14A-3` (evidence field migration mapping, byte-compatible
  reads) in `DECISIONS-PRE-14A-2026-08-14.md`.
- Requirements owned by 14A: FILE-01, FILE-02, FILE-03, ID-01, ID-02,
  RIGHTS-01, RELIABILITY-01 (each now carries its fixture sentence).
- The revision-model requirements R1 through R10 in
  `research/phase-16/16-editor-reader-landscape.md` section 4: 14A builds the
  MODEL those UI patterns need (base fingerprints, conflict on divergence,
  diff on demand, restore as a forward operation, external-edit visibility);
  it builds no UI.
- Performance budgets from `DECISIONS-12.6-REMAINING-2026-08-14.md` D-12.6-10,
  measured here on the synthetic corpus, not promised.
- Architecture constraints: one parser, one scorer, one evidence store; new
  code lands as peer modules beside `runtime.py` following the `evidence.py`
  precedent; `model.py` gains nothing that parses a second content format.

**Walking-skeleton coupling (ROADMAP Phase 13.9, audit A9):** 13.9 may stub
course-level storage over the smallest 14A identity/journal slice, which is
plan 14A-01 plus the journal append of 14A-02. Plans are ordered so that slice
lands first and 13.9 can start before 14A finishes. No 14B-or-later freeze
closes before the skeleton is walked.

**Executor bar:** this is the phase-level plan. Before execution, each plan
below is expanded to the lesser-model executor bar in
`PLANNING-DIRECTIVES.md` section 5 (exact paths, verbatim commands with
expected output, every user-visible string written out, fixture named before
each task, decisions cited, out-of-scope stated). The design decisions are
already made and cited above; the expansion adds mechanics, never re-litigates.

## Plans

### 14A-01: identity kernel (the skeleton-enabling slice)

Opaque ID minting and registration for course, objective, source, lesson,
bank, and item (items keep their shipped scheme untouched); component IDs
minted only for cited, gated, or evidence-bearing lesson blocks; fingerprints
normalized for trailing whitespace and line endings only; revision records
carrying (id, revision, fingerprint, parent revision, timestamp, origin).
Keyed assessment content is never normalized in a way that could mask a
scoring-relevant change (regression-asserted).

- Files: new peer module (identity/lifecycle), `tests/identity_roundtrip.py`,
  synthetic fixture tree under `fixtures/`.
- Fixtures: a synthetic multi-root tree (three roots, nested folders, one
  symlink cycle, one permission-denied pocket, duplicate-fingerprint pair).
- Degraded-state test: an unreadable or denied path is inventoried as denied
  and skipped; nothing is mutated; the report names the denied path.

### 14A-02: operation journal and compare-and-swap writes

Every durable write states an expected base fingerprint, writes to a
temporary file, validates, commits atomically (`os.replace`, the shipped
session-write precedent), and appends a journal entry with the undo pointer.
A mismatch between expected and actual base fingerprint refuses the write as
a conflict. Restore is a forward operation appending a new revision, never a
rollback that rewrites history (editor-landscape R7).

- Files: journal module, `tests/journal_roundtrip.py`.
- Fixtures: scripted interrupted-write faults (kill between temp write and
  commit; kill between commit and journal append).
- Degraded-state test: every injected fault leaves the old valid state or the
  new valid state on disk, never a mixed state, and the journal replay names
  which.

### 14A-03: operation vocabulary and external-edit states

Link, import, copy, move, edit-in-place, and supersede as six distinct journal
operations with distinct provenance effects; same-ID divergent-bytes is a
conflict, never a silent overwrite; an external edit (bytes changed outside
the journal) moves the object to a stale or conflict state that is visible on
read and blocks fingerprint-gated writes until reconciled. Reconciliation is
explicit; no automatic ambiguous merge (12.4 hard-reject).

- Files: extends the 14A-01/02 modules, `tests/operations_roundtrip.py`.
- Fixtures: move-then-edit, edit-both-copies, import-then-source-change
  scenarios over the synthetic tree.
- Degraded-state test: a conflicted object still reads (last accepted state
  served, conflict named); the next safe action is stated in the refusal.

### 14A-04: the file-fault and external-edit tracer (freeze gate, last)

One scripted tracer walks the G3 scenario list end to end on the synthetic
corpus: move, duplicate, conflict, external edit, denied path, interrupted
write, disk-full simulation, and a removable-volume absence stand-in (root
temporarily missing). It also: measures the D-12.6-10 budgets on the 1k/10k
corpora and records real numbers; runs the real-diff corpus check that decides
reflow normalization (the D-14A-2 deferred item) and records the decision; and
asserts the shipped parser/scorer/evidence suites still pass byte-identical
(audit A6 obligation).

- Files: `tests/file_fault_tracer.py` (or the repo's tracer convention),
  tracer report artifact in the phase directory.
- Degraded-state coverage is the tracer itself; its exit criterion is the
  phase's freeze: identity, journal, and operation semantics are frozen only
  when the tracer is green.

## Explicitly out of scope

Graph kernel, sidecar, outline projection (14B); any editor or history UI
(the Ellipsus-pattern UI waits for its subphase; 14A ships the model only);
treatment or director logic (15A); any new learner surface. The `mastered`
field migration mapping is recorded with 14A-01's revision work but the
display semantics stay in 16B.

## Re-audit trigger

After 14B, per ROADMAP governance: the first named re-audit runs before the 15
and 16 tracks fork into their own chats, seeded from
`AUDIT-REPORT-14A-2026-08-14.md` and this plan's tracer report.
