# Phase 14B: Graph & Course Package Prototype - Research

**Researched:** 2026-08-14
**Domain:** typed graph storage over files, deterministic outline projection, source/treatment binding with rights enforcement, minimal course package and clean restore
**Confidence:** MEDIUM. The frozen 14A contract this phase builds on is fully specified in text (14A-01..04-PLAN.md) but **not yet executed on disk** (confirmed by `Glob` this session: `identity.py`, `journal.py`, `discovery.py` do not exist in the working tree, and no `14A-*-SUMMARY.md` files exist). Every architectural conclusion below that depends on that API is grounded in the *plan text*, not in a verified running module. See "Critical caveat" below and the Assumptions Log.

## Critical caveat: 14A has not executed yet

`14A-01-PLAN.md` through `14A-04-PLAN.md` fully specify `identity.py`, `discovery.py`, and `journal.py`'s public surface, but a `Glob` for `*.py` and for `14A-*-SUMMARY.md` in this repository this session found **no matches** for either. Phase 14B's ROADMAP dependency is "Depends on: 14A" (`ROADMAP.md:106`, synthesis section 15 table), so this is expected sequencing, not a defect. It means:

- Every function signature, constant, and refusal code cited below as "from 14A" is `[VERIFIED: 14A-0N-PLAN.md]` (a planning artifact read in full this session) and **not** `[VERIFIED: identity.py]`, because the module does not exist on disk to read.
- 14B's plan must open with a precondition check equivalent to 14A-04's own precondition step: confirm `14A-FREEZE.md` exists and its `## Frozen at 14A` section is present before writing any code that imports `identity` or `journal`. If 14A's real implementation deviated from its plan during execution (a deviation the plan template requires be recorded in `14A-0N-SUMMARY.md`), 14B's plan must be re-verified against `14A-FREEZE.md`, not against this research or the 14A plan text.
- This research is safe to use for **planning** 14B now (per `PLANNING-DIRECTIVES.md` section 5, "Claude plans... execution is transcription"), but the plan it produces should name this precondition explicitly as its first task, following the exact precondition-check pattern `14A-04-PLAN.md` Task 1 already uses.

<user_constraints>
## User Constraints (from binding decision records, in place of CONTEXT.md)

No `CONTEXT.md` exists for this phase (no `/gsd-discuss-phase` has run against 14B). Per the task instructions, the binding decisions live in durable planning artifacts instead. This section reproduces them in the same three-bucket shape `CONTEXT.md` would use, so the planner can treat them identically.

### Locked decisions (do not re-litigate; implement as stated)

- **D-14A-1 (hybrid graph storage, `DECISIONS-PRE-14A-2026-08-14.md:55-59`):** "Option C, hybrid. An edge lives inline when it is wholly owned by one file's content; it lives in the readable course sidecar when it relates two independently-identified objects. Sidecar stays diffable and never becomes the only readable copy. Minimal 14 edge vocabulary as listed above; other relations register later, not frozen in 14." The frozen minimal edge vocabulary is exactly four names: `prerequisite-of`, `covers-objective`, `source-supports`, `treatment-of` (`DECISIONS-PRE-14A-2026-08-14.md:51-53`).
- **D-14A-2 (identity granularity, resolved):** object-level opaque IDs for course/objective/source/lesson/bank, plus bounded component IDs only for cited/gated/evidence-bearing lesson blocks. 14A-01 delivers the exact shape: `identity.new_object_id()` = `uuid.uuid4().hex[:16]`, `identity.REVISION_KEYS` = the eleven-key tuple, `identity.OBJECT_KINDS = ("course", "objective", "source", "lesson", "bank", "component")`. This tuple is **frozen at the 14A-04 tracer** per `14A-FREEZE.md`'s own "Frozen" list ("the object kinds"). 14B must not add a new object kind (for example `"edge"`) without a checkpoint-gated amendment to that freeze; see "Architecture Patterns > Pattern 1" for why 14B does not need to.
- **D-14A-3 (evidence field rename):** routed to 16B. Not 14B's concern; recorded here only so 14B's plan does not accidentally touch `retention.py`, `selection.py`, or `schemas/report.schema.json`.
- **RIGHTS-01 shape, already built by 14A-03:** `identity.RIGHTS_STATES = ("granted", "denied", "unknown")`, `identity.rights_state(record, operation)`, `identity.rights_granted(record, operation)`, exact ASCII string match, no case-folding. 14B reuses this; it does not invent a second rights vocabulary.
- **The six frozen journal operations** (`journal.OPERATION_TYPES = ("link", "import", "copy", "move", "edit_in_place", "supersede")`) and the **additive, non-frozen** `journal.RECORD_TYPES` superset (which already grew from six to nine members across 14A-02 and 14A-03: `+ ("mint", "restore", "external_edit")` then `+ ("reconcile",)`). 14A-03 explicitly deferred `migrate` to 14B: "Recorded as out of scope for 14A and routed to 14B... The omission is deliberate and is recorded in the decision table above so 14B inherits it rather than rediscovering it" (`14A-03-PLAN.md`).
- **PLANNING-DIRECTIVES section 4, all five non-negotiables**, in particular #2 (one parser, one scorer, one evidence store — a typed graph kernel is additive machinery, never a second document model) and #4 (format changes are additive, proven by a byte-identical fixture).
- **PLANNING-DIRECTIVES section 3a**, the reversible-prototype mandate: 14B's freeze gate IS the required prototype (graph-to-outline projection and clean restore) for the course-schema freeze that comes later at 15A/15B. 14B is not itself the schema freeze; it is the prototype that must pass before any later phase treats the course schema as durable.
- **The 14A-03 rights gate precedent**: `op_import`/`op_copy` require the source's `transform` right to equal the exact string `"granted"`; `link`, `move`, `edit_in_place`, `supersede` do not consume rights because they act on already-owned objects. 14B's binding-time rights enforcement (RIGHTS-01's "at the binding, not just at export" requirement) reuses this exact function pair (`identity.rights_state`, `identity.rights_granted`) rather than building a second rights check.

### Claude's discretion (research options below; recommend, do not arbitrate)

- Exact serialization of the course sidecar (pipe-table Markdown vs. YAML vs. fenced JSON block). See Architecture Patterns > Pattern 1 and Pattern 6.
- Whether the sidecar supersedes or extends the `<course-root>/course.md` stub `13.9-01-PLAN.md` already wrote (see "Interaction with Phase 13.9" below) — genuinely open, named as an Open Question, not resolved here.
- Exact package/manifest format for PORT-03 (BagIt-inspired subset vs. a from-scratch format). See Architecture Patterns > Pattern 6.
- New module names (`graph.py`? `course_package.py`?). Recommended names given below; not binding.
- Three-domain tracer's fictional domain names and their structural shape. Recommended below; not binding.

### Deferred / explicitly out of scope for 14B (do not build)

- Any CLI command or daemon route for graph, binding, or package operations. `OPERATION-CONTRACT.md`'s "Pending surfaces" list names "A course manifest or course package command (14B)" and "Discovery, binding, link/import/move/supersede... commands (14A/14B)" as **not yet shippable**, and says explicitly: "Do not invent commands for them." 14B ships the model only, the same posture 14A took for identity/journal/discovery.
- Any draft, branch, or accepted-revision object. `research/phase-16/16-editor-reader-landscape.md` R1 ("open draft revision" state) is owned by 15B; both `14A-02-PLAN.md` and `14A-03-PLAN.md` out-of-scope sections say so explicitly, and nothing in 14B's ROADMAP row reassigns it.
- Treatment *recommendation* (an agent proposing which treatment an objective should get). 14B ships the treatment **binding record** (what treatment was chosen and its citation); *choosing* one is 15A's "director and treatment policy" subphase (`ROADMAP.md` subphase table).
- The `mastered` → `evidence_support` rename and anything under `surfaces/`, `retention.py`, `selection.py`, or `schemas/report.schema.json`.
- Notebook execute/trust UI, visual-interaction registry expansion, and anything from `research/phase-16/16-editor-reader-landscape.md` section 5's non-adoption list.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, `REQUIREMENTS.md`) | Research Support |
|----|-------------|------------------|
| GRAPH-01 | The durable instructional spine is a constrained, layered typed graph of concepts and objectives; structural containment nodes accept local labels (program, semester, module, week, unit, chapter) without schema change, and structural order never implies prerequisite status. An imported scope or framework binds as an immutable version; local edits are overlay records with their own identity and a migration relation, never edits to the import. **Fixture:** the 14B three-domain graph tracer, a synthetic course graph spanning three fictional domains with structural containers labeled module, week, and chapter, asserting the outline projection reads in plain Markdown and structural order mints no prerequisite edge. | Architecture Patterns > Pattern 1 (sidecar = one `course`-kind object), Pattern 4 (structural order is primary, prerequisite edges validate rather than generate order), "Three-domain graph tracer" section |
| GRAPH-02 | Dependency edges carry type, authority, rationale, confidence, and override policy; hard gates are exceptional, and alignment never implies evidence transfer. **Fixture:** the 14B three-domain graph tracer extended with one edge of every registered type plus one deliberately unknown edge type, asserting the unknown type renders as an advisory recommended-before and never a hard block. | Architecture Patterns > Pattern 2 (closed-vocabulary skip-and-warn-but-degrade, not skip-and-drop) |
| GRAPH-04 | Objective splits, merges, renames, and changed demand generate reviewed migration proposals; historical evidence is never transferred automatically. **Fixture:** a 14B three-domain graph tracer scenario that splits one synthetic objective and renames another, asserting a reviewed migration proposal is generated and unmigrated evidence reads unknown on the new identity. | Architecture Patterns > Pattern 3 (`migrate` as an additive `journal.RECORD_TYPES` member, reviewed-not-automatic per the 14A-03 `reconcile` precedent) |
| PORT-03 | Export is not complete until a clean-machine, offline restore validates a manifest and reports every loss, restoring all supported canonical objects and evidence. **Fixture:** the 14B clean restore drill, exporting a synthetic course and restoring it on a clean offline machine against its manifest, asserting every loss is reported. | Architecture Patterns > Pattern 6 (BagIt-inspired manifest), Common Pitfalls (Zip Slip), Security Domain, "Minimal course package" section |

**GRAPH-03 (owned by 16C, included here only because it constrains the graph shape, per the task's own instruction):** progress is reported through an independent tuple with seven separate dimensions; no single aggregate score. This does not add a 14B deliverable, but it does constrain GRAPH-01/02's data model: **the graph itself must never compute or cache a rolled-up completion or mastery value.** The graph stores structure, edges, and bindings; GRAPH-03's tuple is a 16C-owned read over the graph plus the evidence store, computed on demand. A `graph.py` function that returns anything resembling a percentage is out of scope and would violate a hard-rejected pattern (synthesis section 12.4).
</phase_requirements>

## Summary

Phase 14B has three real deliverables and one connective one. First, a **typed graph kernel**: a small, closed vocabulary of four edge types (frozen at D-14A-1) relating objectives, sources, and treatments, stored as one human-readable, git-diffable **course sidecar file per course**. Second, a **deterministic outline projection**: a pure function that renders the graph as a linear, plain-Markdown course outline, where the *authored structural order* (module/week/chapter) is the primary, stable ordering signal and the prerequisite graph is used to *validate* that order rather than to *generate* it from scratch (topological sort is a documented fallback only, for the case where no structural order exists yet). Third, **source and treatment bindings with rights enforcement**: reusing 14A's `identity.rights_state`/`identity.rights_granted` functions verbatim at binding time, not just at export, so RIGHTS-01's "unknown stays restrictive" is enforced the moment a treatment is bound to a source, not discovered later. Fourth, a **minimal course package and clean-restore drill**: a BagIt-inspired (not BagIt-dependent) manifest-plus-payload package, validated by exporting a synthetic course and restoring it on a machine that never saw the original, with every unsupported or unreachable item named in a loss report rather than silently dropped.

The load-bearing architectural finding of this research is that **14B needs almost no new machinery beyond 14A's frozen identity and journal kernel.** The course sidecar is not a new kind of durable object requiring a new compare-and-swap path: it is one file, minted and written as a `kind="course"` object through the *already-frozen* `journal.commit_operation`, exactly like any other 14A-managed file. `migrate` (GRAPH-04) is not a seventh entry in the frozen `journal.OPERATION_TYPES` tuple — it is an additive `journal.RECORD_TYPES` member, following the exact precedent 14A-03 already set when it added `"reconcile"` the same way. Rights enforcement at binding time is not a new subsystem — it is a second call site for the same `identity.rights_granted` function 14A-03 already gates `op_import`/`op_copy` with. This "reuse, do not re-derive" posture is the single most important planning constraint this research surfaces, because it is exactly what keeps 14B from becoming a second parser or a second identity scheme (PLANNING-DIRECTIVES section 4, non-negotiable #2).

**Primary recommendation:** ship one new peer module (`graph.py`, model tier, pure functions, no I/O — the outline projection and edge-vocabulary validation) plus thin additions to the *existing* `journal.py`/`identity.py` surface for the `migrate` record type and any binding-record helpers, plus one new runtime-tier module (`course_package.py`) for the manifest/restore drill. Do not build a CLI or daemon route (out of scope per `OPERATION-CONTRACT.md`'s pending-surfaces list). Sequence the phase tracer-first: land the sidecar-as-course-object slice, then outline projection, then bindings-with-rights, then the package/restore drill, with the three-domain tracer and the clean-restore drill as the final freeze-gate plan, exactly mirroring 14A-04's own shape (tracer last, freeze declared only on green).

## Architectural Responsibility Map

This project's shipped four-layer split (Model / Runtime / Server / Surfaces, `CLAUDE.md` "Architecture > Layers") is the tier vocabulary to use here, not a generic web-app tier map — 14B introduces no browser, server, or client tier at all.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Edge vocabulary validation, outline projection (pure functions over sidecar bytes) | Model tier (peer of `model.py`/`identity.py`) | — | No file I/O, no CAS write; a pure transform exactly like `identity.normalize_for_fingerprint`. New module `graph.py`. |
| Course sidecar read/write, `migrate` record, binding CAS writes | Runtime tier (peer of `journal.py`/`evidence.py`) | Model tier consumes its output | Every durable write in this repository goes through one CAS write path (`journal.commit_operation`); 14B adds callers, not a second writer. |
| Rights enforcement at binding time | Runtime tier (inside the same binding write) | Model tier (`identity.rights_state`) | The check is a **gate inside a write**, not a standalone service; it reuses the exact 14A-03 function pair. |
| Package manifest build, clean-restore validation | Runtime tier (new module `course_package.py`, file I/O over `_journal/` and accepted objects) | — | Analogous to `audit_writer.py`: reads accepted state, writes a durable artifact (the package), never re-derives correctness. |
| CLI command / daemon route for any of the above | **Not built in 14B** | — | `OPERATION-CONTRACT.md` "Pending surfaces" names this explicitly as not yet shippable; inventing one violates Extensibility Rule 7's own "every capability keeps both surfaces" only once a surface is *introduced* — 14B introduces none. |
| Treatment *recommendation* (choosing which treatment fits an objective) | **Not built in 14B** (15A) | — | 14B ships the binding *record shape*; 15A ships the recommender that fills it in. |
| Progress/completion computation (GRAPH-03's tuple) | **Not built in 14B** (16C reads the graph + evidence store) | — | The graph is data the tuple is computed *over*; it must never compute or cache the tuple itself. |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `identity.py` (14A, frozen per plan) | schema `IDENTITY_SCHEMA_VERSION = 1` | Object IDs, fingerprints, revision records, rights defaults/checks | 14B is a **consumer**, not a re-implementer; PLANNING-DIRECTIVES non-negotiable #2 forbids a second identity scheme. `[VERIFIED: 14A-01-PLAN.md]`, not yet `[VERIFIED: identity.py]` — see Critical Caveat. |
| `journal.py` (14A, frozen per plan) | schema `JOURNAL_SCHEMA_VERSION = 1` | Compare-and-swap writes, the append-only operation journal, the six frozen operations | Same reuse mandate. `[VERIFIED: 14A-02-PLAN.md, 14A-03-PLAN.md]`. |
| `discovery.py` (14A, frozen per plan) | schema `DISCOVERY_SCHEMA_VERSION = 1` | Read-only, root-bounded, cancellable multi-root walk | 14B's three-domain tracer and clean-restore drill both need to enumerate a synthetic multi-root tree; reuse rather than re-walk. `[VERIFIED: 14A-01-PLAN.md]`. |
| Python 3.11+ standard library: `hashlib`, `uuid`, `os`, `json`, `re`, `difflib` | stdlib | Fingerprints, IDs, file I/O, edge-vocabulary matching, name hints | Already the project's exclusive toolset for this whole problem class; no phase before this one has needed a third-party package for identity/graph/journal work. |
| Python 3.11+ standard library: `zipfile`, `tarfile`, `shutil` | stdlib | Package serialization for PORT-03 (directory tree, optional zip/tar transport) | `resources.py`'s own module docstring already documents this project's working pattern for reading from inside a `.pyz`; the same `zipfile` module serves package export. No new dependency. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `schema_validate.py` (shipped) | project-local, no version | Hand-rolled JSON-Schema-subset validator | For a new `schemas/course_graph.schema.json` (or similar) if the sidecar's non-Markdown-table portions are serialized as JSON/YAML-as-JSON; reuse the existing subset validator rather than adding a JSON Schema library, following its own stated philosophy: "There is no JSON Schema implementation in the Python standard library, and this is not a Draft 2020-12 reimplementation either... a schema that uses a keyword outside that set is refused, not partially checked" (`[VERIFIED: schema_validate.py:1-19]`, quoted verbatim). |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-rolled BagIt-inspired manifest (stdlib `hashlib` + a manifest file) | A `bagit` PyPI package | Rejected for this phase: PORT-03's fixture is a narrow, project-specific manifest (course objects + evidence + loss report), not general-purpose digital-preservation bagging; adding a dependency for a subset the project can hand-roll in under 100 lines contradicts `schema_validate.py`'s own established precedent of hand-rolling narrow validators rather than importing broad libraries. If a future phase needs full BagIt interoperability with an external archive, revisit with a named consumer (mirrors the PORT-02 "EPUB and narrow QTI wait for a named consumer" posture). |
| Kahn's-algorithm topological sort with an explicit stable tie-break | `networkx` or another graph library | Rejected: the graph here is small (a handful of edge types over at most a few hundred objectives per course), and PLANNING-DIRECTIVES section 4a requires reporting real cost before rejecting a dependency on principle — the real cost of `networkx` here is a multi-megabyte dependency for what one 20-line stdlib function does correctly and deterministically. If a future phase needs general graph algorithms (shortest path, centrality) at real scale, revisit. |
| A real relational or graph database for the sidecar | SQLite (already used by `evidence.py`'s disposable index) | Rejected as the *source of truth*: D-14A-1 requires the sidecar to be "readable, diffable" and never the only understandable copy; SQLite is opaque to `git diff` and to a plain-text reader. A SQLite index remains legitimate as a **disposable, rebuildable** query cache over the sidecar, following `evidence.py`'s own precedent, if 14B's tracer shows the three-domain scale needs one (unlikely; not recommended as a first cut). |

**Installation:** none. No `pip install` step. Every library named above is either already present in this repository or Python 3.11+ standard library.

**Version verification:** not applicable — no third-party package is proposed by this phase.

## Package Legitimacy Audit

**Not applicable.** This phase proposes zero external (PyPI or otherwise) packages. Every module named in Standard Stack is either an existing project module or Python 3.11+ standard library. The Package Legitimacy Gate protocol (`gsd_run query package-legitimacy check`) was not run because there is nothing in its input set — there is no `<pkg>` argument to check.

**Packages removed due to [SLOP] verdict:** none (none proposed).
**Packages flagged as suspicious [SUS]:** none (none proposed).

If a later 14B plan discovers a genuine need for a third-party package (for example, if the reflow-adjacent Markdown-table diffing the sidecar needs turns out to require more than `difflib`), that plan must re-run this gate before recommending it; this research found no such need.

## Architecture Patterns

### System Architecture Diagram

```
Synthetic multi-root tree (fixtures, three fictional domains)
        |
        v
  discovery.py (14A, frozen, read-only)  -->  candidate sources, fingerprints
        |
        v
  graph.py (NEW, model tier, pure)
    - mint objective/edge candidates (calls identity.new_object_id())
    - validate edge type against the frozen 4-name vocabulary
    - unknown edge type --> degrade to "advisory recommended-before" (never drop, never hard-block)
        |
        v
  ONE course sidecar file per course (e.g. <course-root>/course.md or graph.md)
    - written via journal.commit_operation(object_id=<course id>, kind="course", ...)
    - contains: structural containment (module/week/chapter), objective records,
      the four edge types, source bindings, treatment bindings, rights snapshots
        |
        +--> graph.outline_projection(sidecar_bytes) --> plain Markdown outline
        |      (pure function; authored structural order is primary;
        |       Kahn's-algorithm fallback only when no structural order exists yet)
        |
        +--> journal.py (14A, frozen) records every sidecar mutation:
        |      six frozen OPERATION_TYPES (link/import/copy/move/edit_in_place/supersede)
        |      + additive RECORD_TYPES: mint, restore, external_edit, reconcile, MIGRATE (new, 14B)
        |
        v
  course_package.py (NEW, runtime tier)
    - reads accepted objects (via journal.read_registry / journal.read_object) + evidence store
    - writes: payload/ directory + manifest (relative path, sha256, per-object kind/id/revision)
    - loss report: every unsupported/unreachable/rights-restricted item named, never silently dropped
        |
        v
  Clean-machine, offline restore drill (no shared state with the exporting machine)
    - validates every manifest entry's checksum
    - reports every loss category by name (absolute paths, machine-local settings,
      rights-restricted material, unreachable external sources)
```

A reader can trace the primary use case end to end: a synthetic multi-root tree is discovered, candidate objectives/edges are minted into one course sidecar object, the sidecar is written through the existing CAS/journal path, the outline is a pure read-side projection of that same file, and the package/restore drill is a separate export-then-verify pass over the accepted state the journal already tracks.

### Recommended Project Structure

```
graph.py                    # NEW. Model tier, peer of identity.py. Pure functions:
                             #   edge vocabulary validation, outline_projection(),
                             #   migration-proposal shape (data only, no I/O)
course_package.py           # NEW. Runtime tier, peer of journal.py/audit_writer.py.
                             #   build_manifest(), export_package(), restore_package(),
                             #   loss-report construction
schemas/course_graph.schema.json   # NEW. Published contract for the sidecar's structured
                                    #   portions, validated by the existing schema_validate.py
tests/graph_roundtrip.py           # NEW. GRAPH-01/02/04 assertions (sidecar-as-course-object,
                                    #   edge vocabulary, migrate record, outline stability)
tests/course_package_roundtrip.py  # NEW. PORT-03 assertions (manifest build, loss report)
tests/three_domain_tracer.py       # NEW. The freeze-gate tracer, following the
                                    #   tests/file_fault_tracer.py naming and structure
fixtures/corpus_14b.py             # NEW (or extends fixtures/corpus_14a.py). Three fictional
                                    #   synthetic domains, structurally faithful, no real content.
```

### Pattern 1: The sidecar is one `course`-kind object, not a new kind of durable thing

**What:** the D-14A-1 hybrid sidecar is not a new storage mechanism. It is a single file, minted once with `identity.mint_object("course", <path>, <bytes>, ...)` and thereafter written exclusively through `journal.commit_operation(object_id=<the course's id>, kind="course", rel_path=<path>, ...)` — the *exact same* compare-and-swap path every other 14A-managed object uses.

**When to use:** for every mutation to the graph: adding an objective, adding an edge, adding a binding, recording a migration proposal. All of them are one CAS write to the one sidecar file.

**Why this is the right reading of D-14A-1, not a guess:** the synthesis's own object table lists the objective's source of truth as "Course graph" (a graph, not a per-objective file) (`research/phase-16/14-synthesis.md:158`, quoted: `"Objective | Stable ID, demand, authority, scope, evidence rule, prerequisite relations | Course graph"`). `identity.OBJECT_KINDS` already includes both `"course"` and `"objective"` as separate kinds (`14A-01-PLAN.md`), but `journal.commit_operation` ties exactly one `object_id` to exactly one target path per call — two different object kinds cannot independently compare-and-swap the same physical bytes. The only architecture that satisfies both facts without inventing a second write path is: the sidecar file *is* the `course`-kind object (one file, one CAS lineage), and individual objectives/edges are addressable **records inside it**, each carrying its own `identity.new_object_id()`-minted ID for cross-referencing (by edges, bindings, and — later — evidence), but not independently CAS-tracked as their own files.

**Consequence for GRAPH-01's "immutable version, local edits are overlay records" clause:** an imported scope/framework's own objective set binds as one **frozen block** inside (or referenced by) the course sidecar, fingerprinted once at import time; a local edit to an imported objective is a **new record inside the sidecar** carrying a `migrates` / `overlays` relation back to the imported objective's ID, never a mutation of the imported block's bytes. This keeps "the import is never edited" true by construction, because the import's bytes are simply never targeted by a later `commit_operation` call for that block — the overlay is a sibling record, not a patch.

**Example (illustrative, not yet runnable against a real `journal.py`):**
```python
# graph.py (NEW) -- pure function, no I/O
def validate_edge(edge_type):
    """Frozen four-name vocabulary per D-14A-1. Unknown types degrade to an
    advisory 'recommended-before' relation; they are never dropped and never
    hard-block (GRAPH-02)."""
    KNOWN_EDGE_TYPES = ("prerequisite-of", "covers-objective",
                        "source-supports", "treatment-of")
    if edge_type not in KNOWN_EDGE_TYPES:
        return {"effective_type": "recommended-before", "authority": "advisory",
                "original_type": edge_type}
    return {"effective_type": edge_type, "authority": "hard", "original_type": edge_type}

# course_package.py or a 14B binding module (NEW) -- runtime tier, inside the write path
def bind_treatment(course_base, source_object_id, treatment_kind, ...):
    source_record = journal.read_registry(course_base)[source_object_id]
    if not identity.rights_granted(source_record.get("rights"), "quote"):
        raise BindingError("binding.rights_unknown",
            "the quote right for source %s is %s, so this binding is refused "
            "by name" % (source_object_id,
                         identity.rights_state(source_record.get("rights"), "quote")))
    # ... proceed to journal.commit_operation on the course sidecar
```
`[ASSUMED]` — this is a research-derived recommendation, not a verified 14A function; `identity.rights_granted`/`identity.rights_state` themselves are `[VERIFIED: 14A-03-PLAN.md]` (their exact signatures and refusal semantics are specified there in full).

### Pattern 2: Closed-vocabulary skip-and-warn, but *degrade the value*, not drop the record

**What:** GRAPH-02's fixture requires an unknown edge type to render as an **advisory recommended-before**, not to be silently skipped and not to hard-block. This is a different discipline than `evidence.events()`'s skip-and-warn (which *drops* the malformed line from the returned list). 14B's read path must **keep** the record and **downgrade** its authority, never remove it.

**When to use:** whenever `graph.py` reads an edge record whose `edge_type` is not one of the four frozen names.

**Example:** see Pattern 1's `validate_edge` above — the unknown type is preserved in `original_type` for a future registration to recognize, exactly the way this project preserves a rejected idea rather than deleting it (PLANNING-DIRECTIVES section 3a, "a superseded or hard-rejected idea is never deleted").

### Pattern 3: `migrate` is an additive `journal.RECORD_TYPES` member, never a seventh `OPERATION_TYPES`

**What:** GRAPH-04 needs a migration relation for objective splits/merges/renames. 14A-03 already deferred exactly this to 14B and named the mechanism it expects: an additive record type, following the precedent it set when it added `"reconcile"` to `RECORD_TYPES` while keeping `OPERATION_TYPES` frozen at exactly six (`14A-03-PLAN.md` Task 2 step 5: `'Add "reconcile" to RECORD_TYPES, keeping OPERATION_TYPES at exactly six'`).

**When to use:** 14B adds `"migrate"` to `journal.RECORD_TYPES` (which becomes `OPERATION_TYPES + ("mint", "restore", "external_edit", "reconcile", "migrate")`), and implements a `journal.migrate(...)`-shaped function (or a `graph.py` helper that calls `journal.append_entry`/`journal.commit_operation` with `operation="migrate"`) that:
1. Never transfers evidence automatically (hard-rejected, synthesis 12.4).
2. Records a **reviewed** migration proposal — following the same "reconciliation is a recorded human decision" posture 14A-03's `reconcile` uses, not an automatic algorithm.
3. Leaves unmigrated evidence reading `unknown` against the new objective identity, exactly as GRAPH-04's fixture states.

**Anti-pattern to avoid:** extending `journal.OPERATION_TYPES` itself. That tuple is explicitly named in `14A-FREEZE.md`'s "Frozen" list ("the six operation names"); changing it is a one-way-door schema break requiring a checkpoint, not an ordinary additive change, and it is unnecessary — `RECORD_TYPES` already has an established additive growth path.

### Pattern 4: Outline projection — authored structural order is primary; topological sort is a documented fallback

**What:** GRAPH-01 explicitly separates "structural order" (module/week/chapter containment) from "prerequisite status": *"structural containment nodes accept local labels... without schema change, and structural order never implies prerequisite status."* This means the outline projection does **not** need to compute an order from the prerequisite DAG in the common case — the course sidecar already carries an **authored, human-controlled order** (the sequence of module/week/chapter records as written), and that order is read back verbatim. This is inherently stable and deterministic, because it is just reading an ordered list, and it is what makes the outline hand-editable (the "authorability" the freeze gate requires): a human can reorder two chapters by cutting and pasting two table rows, with no ID minting and no graph recomputation involved.

**The graph's role in the common case is validation, not generation:** `graph.py` checks whether any `prerequisite-of` edge is violated by the authored order (a prerequisite objective appearing *after* its dependent) and reports it as a warning, never silently reordering the human's authored sequence.

**The fallback case, and where a stable topological sort is genuinely needed:** when a set of objectives has prerequisite edges but **no** authored structural order yet (for example, a 15A-recommended objective set before a human has arranged it into modules), `graph.py` needs to *propose* an order. Use Kahn's algorithm with an explicit, named deterministic tie-break — sort the "ready" set (nodes with all prerequisites already placed) by `object_id` before appending, never by dict iteration order or insertion order, so two runs over the same graph produce a byte-identical proposed order:

```python
# graph.py (NEW) -- pure function, no I/O
def propose_order(objective_ids, prerequisite_edges):
    """Kahn's algorithm with an explicit stable tie-break (sort by object_id).
    Used only as a fallback when no authored structural order exists yet;
    the normal path reads the authored order verbatim (Pattern 4)."""
    from collections import defaultdict
    indegree = {oid: 0 for oid in objective_ids}
    successors = defaultdict(list)
    for src, dst in prerequisite_edges:            # src is prerequisite-of dst
        successors[src].append(dst)
        indegree[dst] += 1
    ready = sorted(oid for oid, d in indegree.items() if d == 0)
    order = []
    while ready:
        node = ready.pop(0)                         # smallest object_id first
        order.append(node)
        for nxt in sorted(successors[node]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
        ready.sort()
    if len(order) != len(objective_ids):
        cycle_members = sorted(set(objective_ids) - set(order))
        raise GraphError("graph.prerequisite_cycle",
            "a prerequisite cycle involves at least these objects: %s; "
            "reported for review, never silently broken" % cycle_members)
    return order
```
`[ASSUMED]` — Kahn's algorithm itself is standard, verified computer-science technique (not project-specific); the tie-break-by-`object_id` discipline and the cycle-as-refusal behavior are this research's recommendation, chosen to match this project's established "an undecidable case is reported for review, never silently resolved" posture (ID-02, `14A-03-PLAN.md`'s `journal.move_lineage_mismatch` precedent).

**Cycle handling:** a cycle among `prerequisite-of` edges must be **reported by name**, never silently dropped and never left to hang the projection (mirroring 14A-RESEARCH.md's Pitfall about symlink cycles: a visited-set / explicit failure, not an infinite loop). Because the common path reads authored order verbatim, a cycle in the *edges* does not by itself break the *outline* (the outline still renders from the authored sequence) — but it must still surface as a named validation warning, since a real prerequisite cycle is a course-authoring error worth surfacing even though it cannot corrupt the rendered outline.

### Pattern 5: Rights enforcement moves to binding time, reusing 14A-03's exact function pair

**What:** RIGHTS-01 requires "unknown rights stay restrictive... enforced at the binding, not just at export." 14A-03 already built the enforcement primitive (`identity.rights_state`, `identity.rights_granted`, gating `op_import`/`op_copy`). 14B's job is a **second call site**, at the moment a treatment binding references a source: before the binding record is written, check the source's relevant right (most commonly `quote` for a citation, `transform` for anything that rewrites source text into lesson prose) via the same functions, and refuse the binding write (never the source read) when the state is not exactly `"granted"`.

**When to use:** every `bind_source`/`bind_treatment` write in `graph.py`/`course_package.py`.

**Where the rights state lives:** on the **source object's own identity record** (`identity.rights_default()` already produces the seven-key all-`"unknown"` dict at mint time, per 14A-01). 14B does not need a second rights store — it reads the same field 14A already reserved.

### Pattern 6: Minimal package = BagIt-inspired manifest, hand-rolled in stdlib

**What:** BagIt (IETF RFC 8493, `[CITED: datatracker.ietf.org/doc/html/rfc8493]`) establishes the shape worth borrowing without the dependency: a base directory containing a `data/`-equivalent payload directory and a manifest file listing every payload file's relative path alongside a checksum (`<checksum> <relative-path>` per line), so "verification software compares the checksums in the manifest against the actual files, immediately flagging any corruption, truncation, or missing files" (`[CITED: msi.dublincore.org/standards/bagit]`).

**14B's package, concretely:**
```
<package-root>/
  manifest.json          # {"schema_version":1, "entries":[{"object_id":..., "kind":...,
                          #   "revision":..., "relpath":"payload/<id>.md",
                          #   "fingerprint":"sha256:..."}], "loss_report":[...]}
  payload/
    <object_id>.md        # one file per accepted, exportable object
  evidence/
    evidence_export.jsonl # a filtered copy of the accepted evidence events for this course
```

**Loss report categories (must each be named, never silently dropped, per PORT-03):**

| Category | Example | Why it cannot travel |
|---|---|---|
| Absolute local paths | a linked (not imported) source file outside the course root | `link` operations (Pattern from 14A-03) preserve external identity/location; the external file itself is not copied into the package unless it was `import`ed |
| Rights-restricted material | a source whose `export`/`package` right is `"unknown"` or `"denied"` | RIGHTS-01: unknown stays restrictive; the package must refuse to embed it and say so by name |
| Machine-local settings | model backend config, local update-policy state | Never course data; not in scope for a course package at all, but must be named as "not included by design" so a restore does not silently assume it |
| Unreachable external sources at export time | a linked file whose root was unavailable when the package was built | `discovery.py`'s own `unavailable` state, surfaced into the loss report rather than silently omitted |

**Restore validation:** on a clean machine, walk `manifest.json`, recompute each payload file's fingerprint with `identity.object_fingerprint(raw, kind)` (the same function used at export), compare against the manifest's recorded value, and report any mismatch or missing file as a restore-time loss, distinct from the export-time loss report. Both reports must be shown; a clean restore that silently trusts the manifest is not a validated restore.

**Security note — this is the load-bearing reason the package is a *plain directory tree first*, zip/tar only as an optional transport:** if the package is ever serialized to `.zip`/`.tar` for transport, extraction is a classic Zip Slip vector — "archives can contain entries with malicious names like `../../../etc/passwd`... that, when extracted, write files outside the intended directory" (`[CITED: snyk.io/research/zip-slip-vulnerability]`). Mitigation, to be asserted by the restore drill: before writing any extracted entry, resolve its target path with `os.path.realpath` and refuse (never silently clamp) any entry whose resolved path falls outside the destination directory, reusing the exact `inside_any_root`-shaped check `discovery.py` already implements for symlinks (14A-01). This project has a single local user and its own threat model deliberately treats fingerprints as change-detection, not a security boundary (`evidence.py:16-18`) — but a package a learner might receive from someone else (the friend-installs-a-copy goal recorded in `CLAUDE.md`'s 2026-08-14 amendment) is untrusted input the moment it crosses a machine boundary, so this check is real, not defensive theater.

### Anti-Patterns to Avoid

- **A second identity or fingerprint scheme for edges.** An edge's identity is the tuple `(source_object_id, edge_type, target_object_id)`, never a hash of the edge's own record (which would make editing an edge's `rationale`/`confidence` field look like "a different edge" — the same class of error Pitfall 2 in 14A-RESEARCH.md names for objects generally).
- **A CLI command or daemon route.** Explicitly out of scope; see Deferred section above.
- **Computing GRAPH-03's progress tuple inside `graph.py`.** The graph stores structure; 16C computes the tuple by reading the graph plus the evidence store. A `graph.py` function returning a percentage is a hard-rejected pattern (synthesis 12.4).
- **Serializing the sidecar as minified/nested JSON.** Fails the "authorability review" freeze gate outright — see Common Pitfalls #9.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Durable ID minting | A second `uuid4`-based or path-based ID scheme | `identity.new_object_id()` (14A) | PLANNING-DIRECTIVES non-negotiable #2; content-hash-as-ID is already hard-rejected (D-14A-2). |
| Compare-and-swap file writes | A second atomic-write helper | `journal.commit_operation()` (14A) | Three call sites already agree on the tmp-then-`os.replace` idiom (`runtime.write_session`, `audit_writer._write_bytes_atomic`, `evidence.rebuild_index`); 14A's `journal.py` is the fourth and 14B must not add a fifth. |
| Rights checking | A second permission/grant model | `identity.rights_state()`/`identity.rights_granted()` (14A) | Already built, already tested against the exact closed vocabulary RIGHTS-01 names. |
| JSON Schema validation for the new course schema | A `jsonschema`-library dependency, or an ad hoc hand check | `schema_validate.py`'s existing subset validator | Established project precedent; its own docstring states the "refuse rather than partially check" philosophy 14B should extend, not duplicate. |
| Topological sort | Hand-rolled DFS with no documented tie-break, or a graph library | Kahn's algorithm with an explicit `sorted()` tie-break (Pattern 4) | A library is unjustified cost for a small graph (PLANNING-DIRECTIVES 4a: report real cost, do not reject on principle, but also do not add cost with no offsetting benefit); a tie-break-free hand-rolled sort is a determinism bug waiting to happen. |
| Package/manifest format | A general digital-preservation library (`bagit`) or a from-scratch ad hoc format | A BagIt-**inspired** hand-rolled manifest (Pattern 6) | Narrow, project-specific need; matches `schema_validate.py`'s own "hand-roll the subset you actually need" precedent. |

**Key insight:** every "Don't Hand-Roll" row above resolves to the same instruction: 14B's new code is thin. The heavy lifting (identity, fingerprints, CAS writes, the append-only journal, rights) is already specified by 14A. A 14B plan whose diff is large in `identity.py` or `journal.py` (beyond the additive `migrate` record type) should be treated as a signal that the design has drifted from D-14A-1's intent.

## Common Pitfalls

### Pitfall 1: the sidecar becomes a second source of truth

**What goes wrong:** if the sidecar caches a lesson's title, an item's objective tag, or a source's rights state *and* that duplicate drifts from the file it was copied from, the course now has two disagreeing truths.

**Why it happens:** convenience — rendering the outline is faster if the sidecar already has everything inline.

**How to avoid:** D-14A-1's own text: "Duplicating a registry value into a file for readability is allowed only as a derived, regenerable annotation, never the source of truth" (`DECISIONS-12.6-REMAINING-2026-08-14.md` D-12.6-8, paraphrasing the same rule for the metadata threshold). Any inline copy in the sidecar must be regenerable from the owning file and must never be the value a binding or an edge is validated against.

**Warning signs:** a lint or test that would need to fire whenever the sidecar's copy and the source file disagree, but does not exist yet.

### Pitfall 2: instability in the outline projection breaks diffing

**What goes wrong:** if the outline is regenerated by a topological sort **every time**, even when an authored order already exists, two runs over an unchanged graph can differ in the order of `prerequisite-of`-tied nodes (multiple valid topological orders), making every diff noisy and defeating the "diffable" half of D-14A-1.

**How to avoid:** Pattern 4 above — read authored order first; only fall back to a sort, and when falling back, use an explicit deterministic tie-break.

### Pitfall 3: cycle handling that hangs or silently truncates

**What goes wrong:** a naive DFS-based cycle check can either recurse forever on a genuine cycle or silently omit the cycle's nodes from the result with no error.

**How to avoid:** Kahn's algorithm naturally detects a cycle as "nodes remain with `indegree > 0` after the queue empties" (shown in Pattern 4's example); raise a named error listing the cycle's members rather than returning a partial, silently-truncated order.

### Pitfall 4: edge-vocabulary creep without the degrade path

**What goes wrong:** a future phase (or an eager agent) adds a fifth edge type informally, and the read path either crashes on it (breaking GRAPH-02's "never a hard block") or silently drops it (losing the relation entirely, which breaks provenance).

**How to avoid:** Pattern 2 — preserve the record, downgrade its `effective_type` to `"recommended-before"`, keep `original_type` for a future formal registration.

### Pitfall 5: rights bypass via a stale cached rights snapshot

**What goes wrong:** a binding record copies a source's rights state at bind time and never re-checks it; the source's rights are later revoked (or discovered to be more restrictive than assumed), but the stale binding still reads as granted.

**How to avoid:** re-read the source's *current* rights record (via `journal.read_registry`/`journal.read_object`) at the moment of every operation that needs it — never trust a value copied into the binding record itself as authoritative for a later access decision. If a snapshot is stored at all (for audit/history purposes), it must be labeled explicitly as historical, never as the current authorization.

### Pitfall 6: migration used to launder evidence transfer

**What goes wrong:** a "helpful" migration implementation copies old evidence onto the new objective identity so the learner's history "looks continuous," silently reintroducing the exact pattern synthesis 12.4 hard-rejects (automatic evidence transfer on a split/merge/rename).

**How to avoid:** `migrate` (Pattern 3) never touches the evidence store. Unmigrated evidence reads `unknown` against the new identity by construction, because nothing links it there; only a reviewed, explicit act (outside 14B's scope — a 16C or later concern) could ever create such a link, and even then, per the hard-reject, it must never be automatic.

### Pitfall 7: package/restore silently dropping what it cannot carry

**What goes wrong:** an export step that can't include a rights-restricted source, or can't resolve an absolute local path on the target machine, just... omits it, and the restored course looks complete but is missing content with no indication why.

**How to avoid:** Pattern 6's loss-report categories — every omission is named, with its reason, in a report the restore drill asserts against, matching PORT-03's exact wording: "reports every loss."

### Pitfall 8: minified/opaque sidecar serialization fails "authorability"

**What goes wrong:** choosing a compact machine-oriented format (single-line JSON, a binary format, deeply nested YAML with implicit typing) for the sidecar technically satisfies "readable" in the loosest sense but fails the freeze gate's actual test: can Weibao open the file in Obsidian or a plain editor and understand what it says without a decoder?

**How to avoid:** this project already has a working precedent for exactly this class of file — `fixtures/sample_lanes.md` is a plain Markdown document using pipe-tables for structured, machine-parseable, human-readable, git-diffable records (`[VERIFIED: fixtures/sample_lanes.md:1-19]`, quoted below). Recommend the sidecar follow the same convention: pipe-tables for edges/bindings (columns matching GRAPH-02's carried fields: type, source, target, authority, rationale, confidence, override), with a heading structure carrying the module/week/chapter containment.

```
| Lane | Anki deck | Notes file | Notes glob | Fuse | Fuse date |
|---|---|---|---|---|---|
| EMT | EMT | fixtures/sample_plan.md | fixtures/*.md | ch 1-2 read | 2026-01-08 |
```
(`[VERIFIED: fixtures/sample_lanes.md:11-13]`, quoted verbatim — this is the project's own established shape for "readable, diffable, structured course-adjacent record," not a novel proposal.)

### Pitfall 9: overloading the `[CID:...]` component-marker family

**What goes wrong:** reusing 14A's `[CID:<16hex>]` inline marker (reserved specifically for cited/gated/evidence-bearing **lesson** blocks, per D-14A-2) as a general-purpose "here is a graph object's ID" marker inside the sidecar would silently widen a frozen, narrowly-scoped contract.

**How to avoid:** give graph object references their own convention — a plain `id` column in the sidecar's pipe-tables (not an inline bracket marker at all, since the sidecar's records are already tabular, not prose that needs an inline anchor). This sidesteps the collision entirely rather than requiring a freeze amendment.

## Code Examples

Patterns 1, 4, and 6 above already carry the load-bearing code examples for this phase (edge validation/degrade, deterministic outline fallback, package manifest shape). They are not repeated here to avoid duplication; see Architecture Patterns.

### The reuse call this phase must get right (illustrative, not yet runnable — see Critical Caveat)

```python
# What 14B does NOT do: re-implement rights checking.
# What 14B DOES: call the frozen 14A-03 functions at a new call site (bind time).

import identity  # from 14A -- not yet present on disk this session; frozen per 14A-03-PLAN.md

def check_binding_rights(source_rights_record, operation_name):
    state = identity.rights_state(source_rights_record, operation_name)
    if not identity.rights_granted(source_rights_record, operation_name):
        # Exact refusal shape follows the 14A-03 op_import/op_copy precedent:
        # name the right, the state, and the next safe action.
        raise BindingError(
            "binding.rights_unknown",
            "the %s right is %s, so this binding is refused by name. "
            "Next safe action: record a rights grant for this source, or "
            "choose a treatment that does not require this operation."
            % (operation_name, state))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Item-level `objective` field: a free-text string on each item, no stable ID, no graph, no cross-file relations (shipped Phase 1-13.5) | Typed graph with stable objective IDs and a closed four-name edge vocabulary (14B) | 14B (this phase), building on 14A's frozen identity kernel | 14B does **not** retrofit existing banks' free-text `objective` strings onto the new graph — that reconciliation (matching legacy string objectives to new objective IDs) is not named in any 14B requirement or fixture and is reasonably deferred to whichever later phase (15A or 16C) first builds a real course over real content. Flagged as an Open Question below so it is not silently assumed either way. |
| `<course-root>/course.md` as an unparsed, tool-free draft stub (13.9-01-PLAN.md, "DRAFT STUB no tool parses in 13.9; Phase 14B owns the real schema and may supersede it") | A parsed, schema-validated course sidecar (14B) | 14B | See "Interaction with Phase 13.9" below — this is a named, expected supersession, not drift. |

**Deprecated/outdated:** none within 14B's own scope; the item-level `objective` string field is not deprecated by this phase, only left un-reconciled with the new graph for now.

## Interaction with Phase 13.9 (walking skeleton)

`13.9-01-PLAN.md` already creates `<course-root>/course.md` as a human-readable Markdown manifest with **Sources, Objectives, and Log sections**, explicitly labeled as a stub: *"course.md is a DRAFT STUB no tool parses in 13.9; Phase 14B owns the real schema and may supersede it. Its header must say so, or 14B inherits an accidental format commitment."* (`[VERIFIED: 13.9-01-PLAN.md:20-24]`, quoted verbatim.)

This is a real, named collision surface 14B's plan must resolve explicitly, and this research does not resolve it unilaterally (see Open Questions). Two honest options, both consistent with the frozen decisions:

1. **Adopt the same path** (`<course-root>/course.md`) as the literal `kind="course"` sidecar, with 14B's first task an explicit, tested migration step that reads 13.9's Sources/Objectives/Log sections and reformats them into the new schema (a `commit_operation` with `operation="migrate"` or `"edit_in_place"`, journaled honestly as a format upgrade, not a silent rewrite).
2. **Choose a different path** (for example `<course-root>/graph.md`) and leave `course.md` as a distinct, still-human-readable artifact, with an explicit note in both files cross-referencing the other.

Either is defensible; ROADMAP's own walking-skeleton note ("13.9 stubs course-level storage over the smallest 14A slice... 14B owns the real schema") suggests option 1 is closer to the original intent, but this is a plan-time decision, not a research-time one, because it affects whichever real course 13.9 may already have drafted by the time 14B executes.

## Assumptions Log

> Every claim below is a research-derived architectural recommendation, not a decision already recorded in a `DECISIONS-*.md` file. The 14B plan should either lock each one explicitly (citing this research) or route it to a checkpoint if it looks like a one-way door.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The course sidecar is exactly one `kind="course"` object per course, with objectives/edges as internal records rather than independently-CAS-tracked files. | Architecture Patterns > Pattern 1 | If wrong, 14B may need per-objective identity/CAS tracking, which is a materially larger design (many more files, many more journal entries) and would need its own checkpoint before the freeze gate. |
| A2 | `migrate` is added to `journal.RECORD_TYPES` (additive), never to the frozen `journal.OPERATION_TYPES` six. | Architecture Patterns > Pattern 3 | If wrong (i.e., if `OPERATION_TYPES` genuinely needs to grow), this is a one-way-door amendment to the 14A-04 freeze and requires a `checkpoint:decision`, not an ordinary plan task. |
| A3 | Outline projection reads authored structural order as primary; topological sort is a fallback used only when no authored order exists. | Architecture Patterns > Pattern 4 | If wrong (i.e., if the outline is always computed from the DAG), the stability/diffability property this research relies on to satisfy "authorability" would need a different mechanism (e.g., persisting the last-computed order as the new "authored" baseline). |
| A4 | Rights enforcement at binding time reuses `identity.rights_state`/`identity.rights_granted` with no new rights vocabulary. | Architecture Patterns > Pattern 5 | Low risk — this is the most directly supported claim in this research (RIGHTS-01 explicitly and D-12.6-9's recommendation both point here), but if 14B's plan-time review decides a richer per-binding rights record is needed (beyond source-level rights), this changes the binding schema. |
| A5 | Package format is a plain directory tree (payload + `manifest.json`) with zip/tar as optional transport only, never the source of truth. | Architecture Patterns > Pattern 6 | If wrong (project decides packages must ship as a single archive file by default), the Zip Slip mitigation becomes load-bearing for the *default* path, not an optional-transport concern, and should be tested in the freeze-gate tracer regardless of which way this goes. |
| A6 | 14A's `identity.py`/`journal.py`/`discovery.py` will be built exactly as specified in the 14A plan text, with no material deviation, before 14B executes. | Critical Caveat | If 14A's real implementation deviates (recorded in its own `SUMMARY.md` files per the plan template), every function signature and constant cited in this research must be re-verified against `14A-FREEZE.md` before 14B's plan is executed. This is the single highest-impact assumption in this document. |
| A7 | `<course-root>/course.md` (13.9's stub) either becomes the literal 14B sidecar path with an explicit migration task, or is deliberately superseded by a differently-named file with cross-references — not resolved here. | Interaction with Phase 13.9 | If the 14B plan is silent on this, it risks either silently overwriting 13.9's draft course (if any real course has been drafted there by execution time) or leaving two disagreeing "course" artifacts. |
| A8 | New module names `graph.py` and `course_package.py` do not collide with any existing or planned module. | Standard Stack, Recommended Project Structure | Verified this session via `Glob "*.py"`: no existing `graph.py` or `course_package.py` at the repository root. Low risk, but the plan should re-check at execution time in case 14A or 13.9 added either name in the interim. |

**If this table is empty:** not applicable — every architectural decision in this phase beyond the already-frozen 14A contract is a recommendation requiring plan-time confirmation.

## Open Questions

1. **Does 14B need to reconcile legacy item-level `objective` string fields with the new graph?**
   - What we know: no GRAPH-* requirement or fixture names this reconciliation; all four fixtures are synthetic, three-domain, fictional.
   - What's unclear: whether a later phase (15A, 16C) will expect 14B to have already built a bridge.
   - Recommendation: do not build it in 14B. Record explicitly in the 14B plan's out-of-scope section, citing this research, so a later phase does not assume it silently exists.

2. **Does the course sidecar supersede or coexist with 13.9's `course.md` stub?**
   - What we know: 13.9-01-PLAN.md explicitly anticipates supersession and requires its own header to say so.
   - What's unclear: whether a real course will already be drafted in that file by the time 14B executes (13.9 is sequenced to run partly in parallel with/before 14A per the walking-skeleton coupling note).
   - Recommendation: 14B's plan makes this an explicit first task with a named migration step, not a silent assumption either way. See "Interaction with Phase 13.9."

3. **Does 14B need any performance budget at all, given D-12.6-10's corpus work is 14A's job?**
   - What we know: the three-domain tracer is deliberately small-scale and synthetic; no 14B requirement names a performance budget.
   - What's unclear: whether the outline projection or package export needs to be measured on a larger synthetic course (tens of objectives across three domains is trivial; hundreds might not be).
   - Recommendation: no budget measurement required for the freeze gate itself; if the plan wants one, it should be recorded as a measurement (following D-12.6-10's own "measured, not promised" posture), not a build-breaking assertion.

4. **Exact schema fields for the treatment binding record.**
   - What we know: TREAT-01's eleven-item vocabulary is fixed by `REQUIREMENTS.md` and named canonical by the readiness audit's C036 fix ("absorb-book now carries TREAT-01's eleven and names TREAT-01 canonical"): *"direct reading, excerpt, guided lesson, notes or terms, worked example, visual or demonstration, practice, formal test, assessment-first diagnostic, learner artifact, or human review"* (`[VERIFIED: REQUIREMENTS.md TREAT-01, lines ~496-506]`, quoted verbatim).
   - What's unclear: whether 14B's binding record needs additional fields beyond TREAT-02's stated set (objective/source locator, confidence, state) for the freeze gate's fixtures, or whether TREAT-01/TREAT-02's own field lists are sufficient as written.
   - Recommendation: use TREAT-01's eleven-item vocabulary verbatim as the closed enum for a binding's `treatment_kind` field; do not invent a twelfth value in 14B.

## Environment Availability

**Skipped.** This phase has no external dependencies (no services, no databases, no new runtimes) beyond the already-verified Python 3.11+ standard library and the existing 14A modules (whose own availability is 14A's concern, tracked by the Critical Caveat above, not a new environment dependency this phase introduces).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None (direct-execution Python scripts) — this project's established convention, not pytest/unittest |
| Config file | none — see `tests/*_roundtrip.py` convention, verified across 60+ existing files this session via the 14A-PATTERNS.md analog search |
| Quick run command | `python tests/graph_roundtrip.py` (or the specific new test file a task targets) |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` (`[VERIFIED: 14A-04-PLAN.md]`, quoted from its Task 4 action step, itself matching `.github/workflows/ci.yml`'s own per-file execution) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GRAPH-01 | Sidecar-as-course-object mint/write round trip; outline reads in plain Markdown; structural order mints no prerequisite edge | unit + integration | `python tests/graph_roundtrip.py` | ❌ Wave 0 |
| GRAPH-02 | Edge of every registered type plus one unknown type; unknown renders as advisory, never a hard block | unit | `python tests/graph_roundtrip.py` | ❌ Wave 0 (same file as GRAPH-01, different function) |
| GRAPH-04 | Split one synthetic objective, rename another; reviewed migration proposal generated; unmigrated evidence reads unknown | unit + integration | `python tests/graph_roundtrip.py` (a `check_migration()` function) | ❌ Wave 0 |
| PORT-03 | Export synthetic course, restore on a clean simulated machine against the manifest, every loss reported | integration, fault-injection-adjacent | `python tests/course_package_roundtrip.py` | ❌ Wave 0 |
| (freeze gate) | The three-domain tracer, plus a real clean-restore drill and an authorability review artifact | tracer, following `tests/file_fault_tracer.py`'s shape | `python tests/three_domain_tracer.py` | ❌ Wave 0 (last plan) |

### Sampling Rate

- **Per task commit:** the quick run command for that task's specific new/changed test file.
- **Per wave merge:** `for t in tests/graph_roundtrip.py tests/course_package_roundtrip.py; do python "$t" || exit 1; done` (the 14B-specific subset) plus a spot-check of the shipped anchors (`python tests/scoring_roundtrip.py && python tests/evidence_roundtrip.py`), following the exact anchor-check discipline 14A-01 Task 3 already established.
- **Phase gate:** `python tests/three_domain_tracer.py` green, AND the full suite (`for t in tests/*.py; do python "$t" || exit 1; done`) green, AND `python itembank.py guard .` reporting `0 offending files`, before any `14B-FREEZE.md`-equivalent record is written — mirroring 14A-04 Task 4's exact "no freeze declared on a red tracer" discipline.

### Wave 0 Gaps

- [ ] `tests/graph_roundtrip.py` — covers GRAPH-01, GRAPH-02, GRAPH-04
- [ ] `tests/course_package_roundtrip.py` — covers PORT-03
- [ ] `tests/three_domain_tracer.py` — the freeze-gate tracer (last plan, following `tests/file_fault_tracer.py`'s structure: named scenario functions, a final `"TRACER: N passed, M skipped, 0 failed"` line, precondition check that the shipped suite is green first)
- [ ] `fixtures/corpus_14b.py` (or an extension of `fixtures/corpus_14a.py`) — the three fictional, structurally-faithful synthetic domains
- [ ] Framework install: none — the direct-execution convention needs no install step

## Security Domain

`security_enforcement` is `true` in `.planning/config.json` (`security_asvs_level: 1`, `security_block_on: "high"`), so this section is required and was not skipped.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Single-learner, no-accounts product; 14B introduces no auth surface (same posture as 14A). |
| V3 Session Management | No | Not related to `runtime.py`'s session JSON; the course sidecar is a durable content object, not session state. |
| V4 Access Control | **Yes, and newly real (not just reserved) this phase** | RIGHTS-01/RIGHTS-02 enforcement moves from "field reserved, unenforced" (14A) to "actually gates a write" (14B) — Pattern 5's binding-time check via `identity.rights_state`/`identity.rights_granted`, default-restrictive on unknown. |
| V5 Input Validation | Yes | Edge type validated against the closed four-name vocabulary before being trusted as a hard relation (Pattern 2); the new `schemas/course_graph.schema.json` validated through the existing `schema_validate.py` subset validator, which refuses (does not partially check) any schema using an unsupported keyword. |
| V6 Cryptography | Yes (established project posture, unchanged) | `hashlib.sha256` for fingerprints and package manifest checksums, same non-security-boundary posture `evidence.py:16-18` and `identity.py` (per 14A-01) already state explicitly: change-detection only, never an authenticity guarantee, because this project has a single local user and no attacker in its threat model *for locally-authored content*. This posture changes at the package boundary — see below. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Zip Slip: a malicious archive entry name (`../../etc/passwd`-shaped) escaping the restore destination during package extraction | Tampering / Elevation of Privilege | Resolve every extracted entry's target with `os.path.realpath` and refuse (never silently clamp) any target outside the destination root, reusing `discovery.inside_any_root`'s exact containment check. `[CITED: security.snyk.io/research/zip-slip-vulnerability]`. This is the one place in 14B where "no attacker in this project's threat model" stops applying: a package received from another person (the friend-installs-a-copy goal) is untrusted input the moment it crosses a machine boundary. |
| Rights bypass via a stale cached rights snapshot at binding time | Tampering / Elevation of Privilege | Re-read the source's *current* rights record at the moment of the operation, never trust a value copied into the binding record as authorization (Common Pitfalls #5). |
| Automatic evidence transfer laundered through a migration operation | Tampering / Repudiation | `migrate` never touches the evidence store; unmigrated evidence reads `unknown` on the new identity by construction (Common Pitfalls #6, hard-rejected pattern per synthesis 12.4). |
| A malformed or hostile edge/binding record crashing the outline projection or the package build | Denial of Service | Skip-and-warn on read for malformed records (following `evidence.events()`'s degrade-not-crash discipline), and explicit cycle detection that raises a named error rather than looping forever (Pattern 4). |
| Path traversal via a symlinked source inside the multi-root fixture tree, reaching outside the approved roots during package export | Tampering / Information Disclosure | Reuse `discovery.py`'s existing symlink-resolution-plus-containment-check exactly, rather than a second, possibly weaker check in `course_package.py`. |
| Supply chain: a third-party archive, checksum, or graph library added for this phase | Tampering | None is added; see Package Legitimacy Audit and Alternatives Considered. If a future package is ever proposed here, it must be vendored at a pinned version with a recorded checksum and a named license review, per `PLANNING-DIRECTIVES.md` section 4a (the KaTeX precedent). |

## Sources

### Primary (HIGH confidence - read directly this session)

- `.planning/DECISIONS-PRE-14A-2026-08-14.md` (full, D-14A-1/2/3)
- `.planning/DECISIONS-12.6-REMAINING-2026-08-14.md` (full, especially D-12.6-8, D-12.6-9)
- `.planning/REQUIREMENTS.md` (GRAPH-01/02/03/04, TREAT-01/02, PORT-01/02/03, RIGHTS-01/02, RELIABILITY-01/02/03, FILE-01/02/03, ID-01/02, in full, including Fixture sentences)
- `.planning/PLANNING-DIRECTIVES.md` (full)
- `.planning/SOURCE-TO-COURSE.md` (full)
- `.planning/research/phase-16/14-synthesis.md` (sections 1-3, 6, 10, 11, 15, 16 read in full this session)
- `.planning/research/phase-16/16-editor-reader-landscape.md` (section 4, R1-R10, and section 5, in full)
- `.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md`, `14A-01-PLAN.md`, `14A-02-PLAN.md`, `14A-03-PLAN.md`, `14A-04-PLAN.md`, `14A-PATTERNS.md` (all read in full this session)
- `.planning/phases/14A-identity-lifecycle-operation/14A-RESEARCH.md` (Common Pitfalls, Security Domain, Sources sections read in full)
- `.planning/AUDIT-REPORT-14A-2026-08-14.md` (A1-A4 read)
- `.planning/ROADMAP.md` (Phase 14B entry, Extensibility Rules, "Next-milestone subphase sequence" section read)
- `.planning/STATE.md` (Current Position, "Phase 14 progress" — confirmed unrelated to 14A/14B, the old pre-renumbering Phase 14 — and Session Continuity read)
- `.planning/PLAN-TEMPLATE.md` (full)
- `.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md` (frontmatter and objective read)
- `.agents/skills/OPERATION-CONTRACT.md` (full)
- `.agents/skills/discovery-and-binding/SKILL.md` (full, confirms stub status)
- `.planning/UI-SPEC.md` section 8 (the nine accessibility gates, read in full for §4.5 citation accuracy)
- `evidence.py` lines 1-60 (module docstring, `KNOWN_EVENT_TYPES`) `[VERIFIED: evidence.py:1-60]`
- `subjects.py` lines 1-60 (peer-module docstring convention) `[VERIFIED: subjects.py:1-60]`
- `resources.py` (full, 50 lines) `[VERIFIED: resources.py:1-50]`
- `schema_validate.py` lines 1-50 (module docstring, `SUPPORTED` keyword set) `[VERIFIED: schema_validate.py:1-50]`
- `fixtures/sample_lanes.md` (full, 19 lines) `[VERIFIED: fixtures/sample_lanes.md:1-19]`
- `.planning/config.json` (full, confirms `nyquist_validation: true`, `security_enforcement: true`)
- `Glob` tool runs this session confirming `identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course_package.py` do not exist at the repository root, and `schemas/*.json` (17 existing schema files, no course/graph schema yet)

### Secondary (MEDIUM confidence - WebSearch verified against an official/authoritative source)

- IWE (Intelligent Workspace Engine) and Yamlink, cited for the "markdown-in-git, diffable, local-first knowledge graph" prior-art pattern: [Turning Markdown Files into a Queryable Knowledge Graph](https://dev.to/javier_ramrez_e2b4bb54fb/turning-markdown-files-into-a-queryable-knowledge-graph-4aho), [IWE on GitHub](https://github.com/iwe-org/iwe)
- BagIt manifest format, IETF RFC 8493: [The BagIt File Packaging Format (V1.0), RFC 8493](https://datatracker.ietf.org/doc/html/rfc8493), [BagIt — Metadata Standards Index](https://msi.dublincore.org/standards/bagit/)
- Zip Slip vulnerability and mitigation: [Zip Slip Vulnerability | Snyk](https://security.snyk.io/research/zip-slip-vulnerability), [Zip Slip Vulnerability (Arbitrary file write through archive extraction) — snyk/zip-slip-vulnerability on GitHub](https://github.com/snyk/zip-slip-vulnerability)
- Topological sort / course-prerequisite-DAG background (standard CS technique, verified against general references, not project-specific): [Topological Sorting - GeeksforGeeks](https://www.geeksforgeeks.org/dsa/topological-sorting/), [Topological Sorting to Determine Course Order - DEV Community](https://dev.to/theyashsawarkar/topological-sorting-to-determine-course-order-16e8)

### Tertiary (LOW confidence)

None used for a load-bearing claim. Every architectural recommendation in this document is tagged `[ASSUMED]` explicitly in the Assumptions Log rather than presented as verified when it is this research's own synthesis rather than a cited or verified source.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - zero new dependencies, every module named is either already specified in a read planning artifact or Python standard library.
- Architecture (sidecar-as-course-object, outline-order-primary, migrate-as-additive-record, rights-at-binding): MEDIUM - each is a well-grounded inference from cited, verbatim-quoted decision text and the 14A plan's own precedents, but none is a decision already recorded in a `DECISIONS-*.md` file for 14B specifically; each is flagged in the Assumptions Log for plan-time confirmation.
- Pitfalls: HIGH for the ones grounded in this project's own prior incidents and precedents (content-hash-as-ID, evidence-transfer hard-reject, sidecar-as-second-source-of-truth); MEDIUM for the ones synthesized from general graph/security knowledge (topological instability, Zip Slip) applied to this specific system for the first time.
- The Critical Caveat (14A not yet executed): this is a verified fact this session (`Glob` returned no matches), not a confidence rating - it is the most important thing the planner should account for.

**Research date:** 2026-08-14
**Valid until:** re-verify against `14A-FREEZE.md` the moment it exists (this is a hard trigger, not a time-based expiry). Absent that trigger, treat as valid for 14 days (fast-moving: this is an active, in-progress milestone with daily planning artifact changes recorded in `STATE.md`).
