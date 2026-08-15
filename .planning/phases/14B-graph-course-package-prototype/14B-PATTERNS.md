# Phase 14B: Graph & Course Package Prototype - Pattern Map

**Mapped:** 2026-08-14
**Files analyzed:** 9 (2 new peer modules, 1 new schema, 3 new test files, 1 fixture module, plus the CLI surface which is explicitly NOT touched)
**Analogs found:** 9 / 9

## Load-bearing note on 14A analogs

`identity.py` and `journal.py` do not exist on disk. `Glob "*.py"` this session
confirms no match at the repository root. Every excerpt below that names
`identity.*` or `journal.*` is `[PLAN-SPECIFIED: 14A-0N-PLAN.md]`, read from
planning-artifact text, never from source. Each such excerpt is paired with a
second, code-verified analog from the shipped codebase, per the task
instruction, so the planner has a real fallback shape even if 14A's execution
deviates from its plan text before 14B runs (14B-RESEARCH.md's own Critical
Caveat and Assumption A6 name this as the single highest-impact risk in the
phase).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `graph.py` (new, peer of `identity.py`/`model.py`) | model/domain module (edge-vocabulary validation, outline projection, migration-proposal shape) | transform (pure functions, no I/O) | `model.py` (`content_fingerprint`, closed-vocabulary handling); secondarily `[PLAN-SPECIFIED: 14A-01-PLAN.md]` `identity.py`'s own pure-function shape | role-match (code-verified) / exact (plan-specified) |
| `course_package.py` (new, peer of `journal.py`/`audit_writer.py`) | runtime module (manifest build, export, clean-restore, loss report) | CRUD + file-I/O, batch | `audit_writer.py` (CAS write, manifest-then-commit shape) `[VERIFIED]`; secondarily `[PLAN-SPECIFIED: 14A-02-PLAN.md]` `journal.commit_operation` | exact (code-verified) |
| `schemas/course_graph.schema.json` (new) | schema/config | request-response (validated document) | `schemas/selection.schema.json` `[VERIFIED]` | exact |
| `tests/graph_roundtrip.py` (new) | test | unit + integration | `tests/evidence_roundtrip.py` `[VERIFIED]` (fail() helper, subprocess-driven CLI exercise) — but 14B's graph.py is explicitly not CLI-wired, so this test calls `graph.py` functions directly, closer in that specific respect to a pure-function unit test | role-match |
| `tests/course_package_roundtrip.py` (new) | test, fault-injection-adjacent | file-I/O, event-driven | `tests/durability_roundtrip.py` (spawn/kill harness, cited fully in 14A-PATTERNS.md, not re-read this session — reused via 14A-PATTERNS.md's own excerpt) | exact |
| `tests/three_domain_tracer.py` (new) | test, tracer/freeze-gate | fault-injection, batch | `tests/file_fault_tracer.py` per 14A-PATTERNS.md's own mapping (not re-read this session; reused) | exact |
| `fixtures/corpus_14b.py` (new, or extends `fixtures/corpus_14a.py`) | fixture data (not code) | file-I/O, synthetic tree | `fixtures/sample_lanes.md` `[VERIFIED]` for the pipe-table sidecar shape; not a code analog | n/a (fixture) |
| CLI surface (`surfaces/cli.py`) | **not modified in 14B** | — | n/a — explicitly out of scope, see below | n/a |
| `identity.py` / `journal.py` (14A, consumed not modified) | model/runtime (imported dependency) | transform / CRUD | `[PLAN-SPECIFIED: 14A-01/02/03-PLAN.md]`; code-verified peer precedent is `evidence.py` `[VERIFIED]` | n/a (14A's own files) |

## Pattern Assignments

### `graph.py` (model tier, pure functions, no I/O)

**Primary analog `[PLAN-SPECIFIED: 14A-01-PLAN.md]`** — the function/constant
shape `graph.py` must consume from `identity.py`, quoted from the plan text
(not yet readable from `identity.py` itself):

```
Constants: IDENTITY_SCHEMA_VERSION = 1, OBJECT_KINDS = ("course", "objective",
"source", "lesson", "bank", "component")
Functions: utc_now(), new_object_id(), new_component_id(), ...
           rights_default(), revision_record(...), mint_object(...)
```
(`14A-01-PLAN.md:115-127`, `[PLAN-SPECIFIED]`)

```
identity.new_object_id() returns a 16-character lowercase hex string
identity.rights_default() returns a dict with exactly the seven keys ...
```
(`14A-01-PLAN.md:173,206-208`, `[PLAN-SPECIFIED]`)

```
RIGHTS_STATES = ("granted", "denied", "unknown")
rights_state(record, operation) returning the string state for one rights key
rights_granted(record, operation) returning True only when the state is
"granted" (exact ASCII match, no case-folding)
```
(`14A-03-PLAN.md:127-132, 412-421`, `[PLAN-SPECIFIED]`)

**Second, code-verified analog for the "closed vocabulary, pure transform"
shape `graph.py`'s `validate_edge()` must follow** — `model.content_fingerprint`
is the project's own precedent for a pure function over a typed dict that
degrades safely rather than crashing on a partially-recognized shape (see
`14A-PATTERNS.md:50-68`, itself `[VERIFIED: model.py:1451-1471]`). For the
"unknown value degrades, never dropped, never raises" discipline specifically,
the code-verified precedent is `evidence.py`'s `KNOWN_EVENT_TYPES` /
`events()` skip-and-warn pair, already quoted in full in `14A-PATTERNS.md`
lines 206-218 (`[VERIFIED: evidence.py:51-55, 755-774]`). `graph.py` differs
from that precedent in one respect the plan must state explicitly: `evidence.
events()` *drops* an unrecognized record from the returned list; GRAPH-02
requires `graph.py` to *keep* the record and only downgrade its
`effective_type` field (RESEARCH.md Pattern 2). Copy the closed-vocabulary
constant shape from `evidence.py`, but not its drop behavior.

**Core pattern to implement (research-derived, not yet runnable, cited here
as the concrete shape for `graph.py`):**
```python
KNOWN_EDGE_TYPES = ("prerequisite-of", "covers-objective",
                    "source-supports", "treatment-of")

def validate_edge(edge_type):
    if edge_type not in KNOWN_EDGE_TYPES:
        return {"effective_type": "recommended-before", "authority": "advisory",
                "original_type": edge_type}
    return {"effective_type": edge_type, "authority": "hard", "original_type": edge_type}
```
(14B-RESEARCH.md Pattern 1, itself `[ASSUMED]` there — restated here as the
concrete function `graph.py` should contain; treat as illustrative, not
copy-paste-final.)

**Outline projection / topological-sort fallback** — see 14B-RESEARCH.md
Pattern 4 in full (`propose_order()`, Kahn's algorithm with an explicit
`sorted()` tie-break on `object_id`). Reused verbatim from research; not
re-derived here to avoid duplication. Cycle handling raises a named error
listing cycle members, mirroring `[PLAN-SPECIFIED: 14A-03-PLAN.md]`'s
`journal.move_lineage_mismatch` "report, never silently resolve" precedent.

---

### `course_package.py` (runtime tier, CRUD + file-I/O)

**Primary code-verified analog:** `audit_writer.py`, already fully excerpted
in `14A-PATTERNS.md` lines 87-241 (`[VERIFIED: audit_writer.py]`, full file
read by the 14A pattern mapper). Reuse directly rather than re-reading:

- Cross-platform lock (`_bank_lock`, `_try_lock`) — `14A-PATTERNS.md:92-138`.
- Manifest-written-before-mutation, atomic replace, after-fingerprint guard —
  `14A-PATTERNS.md:163-188`. `course_package.py`'s `export_package()` should
  write `manifest.json` with `"state": "prepared"` before writing
  `payload/`, then flip to `"state": "applied"` only after every payload
  file's fingerprint is re-verified — the same crash-safe shape.
- Atomic tmp-then-`os.replace` idiom — `14A-PATTERNS.md:190-204`
  (`[VERIFIED: runtime.py:1430-1437]`).

**Second analog, `[PLAN-SPECIFIED: 14A-02-PLAN.md]`**, for the CAS write call
`course_package.py` makes when it mints the package manifest or records a
`restore` journal entry:
```
RECORD_TYPES = OPERATION_TYPES + ("mint", "restore", "external_edit")
where OPERATION_TYPES = ("link", "import", "copy", "move", "edit_in_place",
"supersede")
```
(`14A-02-PLAN.md:239-240`, `[PLAN-SPECIFIED]`). `course_package.restore_package()`
should call the same `journal.commit_operation(..., operation="restore", ...)`
shape 14A already reserves the `"restore"` record type for, rather than
inventing a new record type for restore.

**Manifest/loss-report shape (research-derived, restated as the concrete
target, not copy-paste-final):**
```python
# manifest.json
{"schema_version": 1,
 "entries": [{"object_id": ..., "kind": ..., "revision": ...,
              "relpath": "payload/<id>.md", "fingerprint": "sha256:..."}],
 "loss_report": [...]}
```
(14B-RESEARCH.md Pattern 6, restated.)

**Zip Slip mitigation, if/when zip/tar transport is added:** reuse
`discovery.py`'s `inside_any_root`-shaped containment check
`[PLAN-SPECIFIED: 14A-01-PLAN.md]` rather than writing a second
path-containment check in `course_package.py`. Resolve every extracted
entry's target with `os.path.realpath` and refuse (never clamp) any target
outside the destination root before writing it.

---

### `schemas/course_graph.schema.json` (schema/config, request-response)

**Analog:** `schemas/selection.schema.json`, read in full above (60 lines).
Concrete shape to copy:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://itembank.local/schemas/course_graph.schema.json",
  "title": "itembank course graph sidecar",
  "description": "...",
  "x-itembank-version": 1,
  "type": "object",
  "additionalProperties": false,
  "required": [],
  "properties": { "...": {"type": "string", "enum": [...], "description": "..."} }
}
```
(`[VERIFIED: schemas/selection.schema.json:1-60]`, quoted verbatim above.)

**Consumer, `schema_validate.py`, and its exact keyword ceiling
`[VERIFIED: schema_validate.py:1-70]`:**
```python
SUPPORTED = frozenset([
    "type", "properties", "required", "additionalProperties", "enum", "const",
    "items", "minItems", "uniqueItems", "minLength", "pattern",
    "minimum", "maximum", "$defs", "$ref", "oneOf",
])
ANNOTATIONS = frozenset([
    "$schema", "$id", "title", "description", "x-itembank-version",
    "default", "x-itembank-phase",
])
```
Its own module docstring states the load-bearing rule: "a schema that uses a
keyword outside that set is refused, not partially checked... A green result
from this validator means the whole document was checked" (`schema_validate.
py:13-19`, `[VERIFIED]`). This directly constrains `course_graph.schema.json`:
the closed four-name edge vocabulary can be expressed with plain `enum`
(supported), but anything needing `patternProperties`, `allOf`, `if`/`then`,
or a conditional schema (any shape that would try to express "unknown edge
type degrades to advisory" *inside the schema itself*) is not expressible —
that degrade behavior belongs in `graph.py`'s read path (Pattern 2), never in
the schema. `check_schema()` walks the whole document before any instance is
checked (`schema_validate.py:50-64`, `[VERIFIED]`) and raises `SchemaError`
(exit code 2, distinct from an instance failure's exit code 1) on an
unsupported keyword — so 14B's schema-authoring task must self-check with
`check_schema()` before assuming the file validates anything.

---

### `tests/graph_roundtrip.py`, `tests/course_package_roundtrip.py`, `tests/three_domain_tracer.py` (tests)

**`fail()` helper convention, code-verified `[VERIFIED: tests/evidence_
roundtrip.py:38-40]`, identical in every one of 60+ existing
`tests/*_roundtrip.py` files:**
```python
def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)
```

**Header/import convention `[VERIFIED: tests/evidence_roundtrip.py:1-25]`:**
```python
#!/usr/bin/env python3
"""One-paragraph statement of what this test proves end-to-end and why it
drives the real surface rather than calling functions directly."""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
```
`tests/graph_roundtrip.py` differs from this shape in one respect worth
naming: since `graph.py` is a pure-function module with no CLI wiring in 14B
(the CLI is explicitly out of scope), this test should `import graph`
directly rather than driving `subprocess`/CLI the way `evidence_roundtrip.py`
does — closer to a plain unit-test import, still using the same `fail()`
convention and direct-execution shape.

**Assertion style, code-verified `[VERIFIED: tests/evidence_roundtrip.py:27-
35]`** — expected-keys-as-a-set pattern, reusable for asserting a graph edge
record's or a manifest entry's required fields:
```python
EXPECTED_KEYS = {
    "schema_version", "event_id", "event_type", "ts", "session_id", ...
}
```

**Spawn/kill fault-injection harness for `tests/course_package_roundtrip.py`**
— reused from `14A-PATTERNS.md:257-292` (`[VERIFIED: tests/durability_
roundtrip.py:44-63, 185-239]`, not re-read this session since 14A-PATTERNS.md
already carries the full excerpt): `subprocess.Popen` + timed `.terminate()`
to kill between temp-write and commit, applied to one `course_package.
export_package()` call instead of one append call.

**`tests/three_domain_tracer.py` structure** — follows `tests/file_fault_
tracer.py`'s shape per `14A-PATTERNS.md:23` (named scenario functions, a
final `"TRACER: N passed, M skipped, 0 failed"` line, a precondition check
that the shipped suite is green first — 14B-RESEARCH.md's Wave 0 Gaps section
states this explicitly, and 14B's own precondition must additionally confirm
`14A-FREEZE.md` exists before importing `identity`/`journal` at all, per
14B-RESEARCH.md's Critical Caveat).

---

### CLI surface — explicitly not touched

**Analog for reference only, not to be used this phase:** `surfaces/cli.py`'s
registration pattern, `[VERIFIED: surfaces/cli.py:159-195, 584-599]`:
```python
def cmd_stats(a):
    qs = load(a.bank)
    counts = collections.Counter(q["type"] for q in qs)
    print("%d items" % len(qs))
    ...
    return 0

# registration:
s = sub.add_parser("stats", help="item mix, coverage, answer-position skew")
s.set_defaults(fn=cmd_stats)
```
14B does not add a `cmd_graph`/`cmd_course_package` handler or an
`add_parser` call. `OPERATION-CONTRACT.md`'s "Pending surfaces" list names
"A course manifest or course package command (14B)" as explicitly not yet
shippable, and 14B-RESEARCH.md's Deferred section repeats this: "Do not
invent commands for them." This excerpt is recorded here only so a future
phase (whichever one does add the CLI surface) has the exact registration
shape to copy, and so this phase's planner does not accidentally add one.

## Shared Patterns

### Atomic tmp-then-replace write
**Source:** `runtime.py:1430-1437` `[VERIFIED]`, `audit_writer.py:246-322`
`[VERIFIED]` (both fully excerpted in `14A-PATTERNS.md`).
**Apply to:** every durable write in `course_package.py` (manifest write,
payload write). `graph.py` has no I/O and does not need this.

### Closed vocabulary, degrade not drop
**Source:** `evidence.py:51-55, 755-774` `[VERIFIED]` for the *shape*
(closed-tuple constant, skip-and-warn read path); GRAPH-02's fixture requires
`graph.py` to diverge from `evidence.events()`'s drop behavior and instead
downgrade-and-keep (14B-RESEARCH.md Pattern 2).
**Apply to:** `graph.py`'s `validate_edge()`.

### Opaque ID never derived from content
**Source:** `model.py:1786-1790, 1514-1522` `[VERIFIED]` (the `[ID:]`/`[HASH:]`
split); `[PLAN-SPECIFIED: 14A-01-PLAN.md]` `identity.new_object_id()`.
**Apply to:** every graph object `graph.py` mints (objective, edge, binding)
— mint via `identity.new_object_id()`, never hash the edge's own record as
its identity (14B-RESEARCH.md Anti-Patterns: "An edge's identity is the
tuple (source_object_id, edge_type, target_object_id), never a hash of the
edge's own record").

### Local test `fail()` helper, no shared test-util import
**Source:** every existing `tests/*_roundtrip.py` file, `[VERIFIED: tests/
evidence_roundtrip.py:38-40]` as one concrete instance.
**Apply to:** all three new 14B test files.

### Rights check reused at a second call site
**Source `[PLAN-SPECIFIED: 14A-03-PLAN.md:443-455]`:**
```python
identity.rights_granted(rights, "transform")
```
gates `op_import`/`op_copy` in 14A. **Apply to:** `graph.py`'s or
`course_package.py`'s `bind_source`/`bind_treatment` write path (14B-
RESEARCH.md Pattern 5) — same function pair, new call site, never a second
rights vocabulary.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `fixtures/corpus_14b.py` (three-domain synthetic corpus) | fixture data | file-I/O | Not source code. `fixtures/sample_lanes.md` `[VERIFIED]` gives the pipe-table sidecar shape to imitate (Pitfall 8 in RESEARCH.md), but there is no existing three-domain synthetic course-graph fixture to copy structurally; this is genuinely new fixture construction, governed by the fault-injection/environment tables in 14A-RESEARCH.md and restated in 14B-RESEARCH.md rather than a code analog. |

## Metadata

**Analog search scope:** root-level modules (`model.py`, `runtime.py`,
`evidence.py`, `audit_writer.py`, `schema_validate.py`), `schemas/` directory,
`surfaces/cli.py`, `tests/` directory conventions, plus the full text of
`14A-01-PLAN.md` through `14A-03-PLAN.md` and `14A-PATTERNS.md` for the
plan-specified (not-yet-real) 14A surface.
**Files scanned:** `schema_validate.py` (70 lines read), `schemas/selection.
schema.json` (60 lines, full), `surfaces/cli.py` (targeted reads: 159-198,
584-599), `tests/evidence_roundtrip.py` (40 lines), plus `14A-PATTERNS.md`
(full, reused rather than re-reading its underlying source files a second
time) and `14A-01/02/03-PLAN.md` (targeted greps for exact signatures).
**Pattern extraction date:** 2026-08-14
