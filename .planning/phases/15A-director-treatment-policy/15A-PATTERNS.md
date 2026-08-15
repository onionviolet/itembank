# Phase 15A: Director & Treatment Policy - Pattern Map

**Mapped:** 2026-08-14
**Files analyzed:** 8 (1 new peer module, 1 modified schema, 1 modified settings
fixture data, 2 modified/extended planned modules, 3 new/extended test files)
**Analogs found:** 8 / 8

## Load-bearing note on unexecuted dependencies

`identity.py`, `journal.py`, `graph.py`, `course.py`, and `course_package.py`
do not exist on disk. A filesystem check this session confirms no match at
the repository root for any of them; `.planning/phases/14A-*/` and
`.planning/phases/14B-*/` contain only `*-PLAN.md` files, no `*-SUMMARY.md`.
Every excerpt below that names one of those five modules is
`[PLAN-SPECIFIED: 14A-0N-PLAN.md]` or `[PLAN-SPECIFIED: 14B-0N-PLAN.md]`, read
from planning-artifact text, never from source, following the exact
disclosure convention `14B-PATTERNS.md` set for the same situation one phase
earlier. Each such excerpt is paired, where one exists, with a
code-verified fallback analog from the shipped codebase (`model_adapter.py`,
`tier_gate.py`, `auditor.py`, `schema_validate.py`, `evidence.py`), so the
planner has a real fallback shape even if 14A/14B's execution deviates from
their plan text before 15A runs. Per this phase's own RESEARCH.md Critical
Caveat, the 15A plan's first task must re-verify these citations against
`14A-FREEZE.md`/`14B-FREEZE.md` if either exists by the time 15A executes.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `director.py` (new peer of `model_adapter.py`/`course.py`) | service module (recommendation drafting, egress recording, autonomy-level check) | request-response + event-driven (calls the adapter, then a rights-gated write) | `model_adapter.py` `[VERIFIED]` for the invoke/typed-envelope half; `[PLAN-SPECIFIED: 14B-03-PLAN.md]` `course.bind_treatment` for the write half | exact (composed of two verified/plan-specified analogs) |
| `schemas/model_adapter.schema.json` (modified: `operation` enum gains `"treatment_recommend"`) | schema/config | request-response | itself, prior state `[VERIFIED: schemas/model_adapter.schema.json:1-30]` | exact (additive edit to existing schema, not a new file) |
| `journal.py` (modified: one new `RECORD_TYPES` member, e.g. `agent_operation`, plus optional `intent`/`checkpoint`/`egress` entry keys) | runtime module (append-only log, CAS write) | event-driven, CRUD | `[PLAN-SPECIFIED: 14A-02-PLAN.md]` `journal.py`'s own `RECORD_TYPES` additive-growth precedent, already exercised once by 14A-03 (`reconcile`) and once by 14B-04 (`migrate`) | exact (plan-specified, additive-pattern match) |
| `identity.py` (consumed, not modified) | model module (pure rights lookup) | transform | `[PLAN-SPECIFIED: 14A-03-PLAN.md]` `rights_state`/`rights_granted`; code-verified structural precedent is `evidence.py`'s `KNOWN_EVENT_TYPES` closed-vocabulary shape `[VERIFIED: evidence.py:51-55]` | exact (plan-specified) |
| `settings.model_backend.profiles` (settings fixture data extended with two mock profiles) | config/fixture data | request-response | `schemas/settings.schema.json` profile record `[VERIFIED: schemas/settings.schema.json:190-246]` | exact |
| `fixtures/corpus_14b.py` (extended with a fourth synthetic domain) | fixture data | file-I/O, synthetic tree | itself, prior state `[PLAN-SPECIFIED: 14B-02-PLAN.md:85]` (`build_three_domains`) | exact (extension of an existing planned fixture, not a new one) |
| `tests/four_subject_review.py` (new tracer) | test, tracer/freeze-gate | fault-injection, batch | `tests/three_domain_tracer.py`'s planned shape, itself modeled on `tests/file_fault_tracer.py` per `14B-PATTERNS.md:28,247-253` | exact |
| `tests/journal_roundtrip.py` (possibly extended with `check_agent_operation_record()`) | test | unit + integration | itself, prior state; convention shared with `tests/evidence_roundtrip.py` `[VERIFIED: tests/evidence_roundtrip.py:1-40]` | exact |

## Pattern Assignments

### `director.py` (new peer module, request-response + event-driven)

**Analog 1, code-verified: the typed adapter boundary `director.py` must call
through unmodified except for the additive `operation` value:**

```python
# Source: model_adapter.py:17-24, 51-58, 73-85, quoted verbatim
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

import resources
import schema_validate
from surfaces.settings import resolve_profile as _resolve_profile

SCHEMA_RESOURCE = "schemas/model_adapter.schema.json"

ADAPTER_CODES = tuple(sorted({
    "adapter.executable_missing", "adapter.http_error", "adapter.internal_error",
    "adapter.malformed_response", "adapter.output_cap_exceeded",
    "adapter.profile_disabled", "adapter.profile_invalid",
    "adapter.profile_unknown", "adapter.provider_refused",
    "adapter.request_invalid", "adapter.subprocess_error", "adapter.timeout",
    "adapter.transport_unknown", "adapter.unreachable",
}))

_PAYLOAD_KEYS = ("item_context", "learner_response", "permitted_tier",
                 "fact_manifest", "rubric_points", "author_request")
# director.py's task: add "course_context"/"objective_id" (or whatever the
# 15A plan names) to this tuple, then build the request through the existing
# request_from_operation() builder below, unmodified.

def request_from_operation(operation, interaction_id, profile, **payload):
    """Build a bounded adapter request: exactly the fixed envelope fields and
    the fixed payload keys, nothing else."""
    return {
        "schema_version": 1,
        "operation": operation,
        "interaction_id": interaction_id,
        "profile": profile,
        "version": "1",
        "payload": {k: payload[k] for k in _PAYLOAD_KEYS if k in payload},
    }
```

`director.py` calls `model_adapter.invoke(request, settings)` with
`operation="treatment_recommend"` exactly the way any existing caller invokes
`hint`/`rubric_review`/`author`; it does not reimplement `TRANSPORT_REGISTRY`
resolution, subprocess/urllib dispatch, or the unavailable-result envelope.

**Analog 2, `[PLAN-SPECIFIED: 14B-03-PLAN.md:174-199]`, quoted (abridged):
the exact write-path assertions `director.py`'s accept-path must inherit by
calling `course.bind_treatment`, not by reproving them:**

```text
- Against a source whose seven rights are all `unknown`: `course.bind_source(...)`
  raises `CourseError` with code `course.rights_not_granted`. The message
  contains the source object id, the string `read`, and the string `unknown`.
- The refusal names the fix: the message contains the substring
  `next safe action: record`.
- After the refusal, the sidecar bytes on disk are unchanged and
  `len(journal.entries(root))` is unchanged. A refused binding writes nothing.
- `course.bind_treatment(..., treatment_kind="direct-reading", ...)` against a
  source whose `read` right is unknown refuses. Direct reading is a complete
  treatment result, not a free pass.
```

**Critical: what `director.py` must NOT reuse**, namely `tier_gate.py`'s five-step
no-leak algorithm. Do not route a `treatment_recommend` result through
`tier_gate.render_hint`/`learner_payload`/`GATE_REASON_CODES`. That gate's
authority model (protect a learner from over-disclosure mid-sitting) does not
map onto a course-builder recommendation review; `director.py` needs a
narrow schema-plus-rights validation instead, following `schema_validate.py`'s
subset-validator discipline (below), not `tier_gate.py`'s span/fact-resolution
machinery. Code-verified boundary for reference (what NOT to import):

```python
# Source: tier_gate.py:1-24, quoted to show the shape being deliberately
# NOT reused: director.py has no learner-facing "focus_span"/"fact_ids"/
# "move" concept and must not construct one.
GATE_REASON_CODES = (
    "gate.schema_invalid", "gate.span_unmatched", "gate.fact_protected",
    "gate.fact_unknown", "gate.ambiguous", "gate.unsupported_move",
)
```

**Rights re-check call shape director.py's validation pass must use,
`[PLAN-SPECIFIED: 14A-03-PLAN.md:412-421,443-455]`, quoted:**

```text
- identity.RIGHTS_STATES equals ("granted", "denied", "unknown").
- identity.rights_state(None, "transform"), identity.rights_state({}, "transform"),
  and identity.rights_state({"transform": "GRANTED"}, "transform") all return
  "unknown" (no case-folding; exact ASCII match only).
- identity.rights_granted(record, op) returns True only for the exact string
  "granted".
- identity.rights_granted(rights, "transform") gates op_import/op_copy in 14A
  at the moment of the operation, reading the live registry, never a
  snapshot.
```

`director.py` reads `identity.rights_state`/`identity.rights_granted` live at
the moment it validates a `treatment_recommend` result against the source's
current rights, exactly as `course.bind_source`/`course.bind_treatment`
already do at write time (Pitfall 2 in RESEARCH.md). A recommendation record
may *display* a rights value observed at draft time, but that display value
never gates the write; the write path reads the registry again.

---

### `schemas/model_adapter.schema.json` (additive enum extension)

**Analog: itself, prior state, quoted verbatim, the exact enum to extend,
not replace:**

```json
// Source: schemas/model_adapter.schema.json:26-29
"operation": {
  "type": "string",
  "enum": ["hint", "rubric_review", "author"],
  "description": "The bounded operation: hint generation, rubric point review, or bounded item authoring ..."
}
```

The 15A edit adds `"treatment_recommend"` as a fourth enum member and extends
the description sentence; it does not restructure `oneOf`, `$defs.request`,
or `$defs.result`. `schema_validate.py`'s closed-keyword ceiling
(`SUPPORTED`/`ANNOTATIONS`, `[VERIFIED: schema_validate.py:26-35]`) already
covers a plain `enum` addition with no new schema keyword, so
`check_schema()` needs no change; only the instance data (the enum's member
list) changes. Any temptation to express "treatment_recommend requires an
`objective_id` payload key but rubric_review does not" via `if`/`then` or
`oneOf` inside the schema must be rejected: that conditional-payload
requirement belongs in `model_adapter.invoke()`'s runtime check (the same
place `rubric_review`'s `payload.rubric_points` requirement already lives),
not in the schema, following the exact discipline `schema_validate.py`'s
docstring states (`[VERIFIED: schema_validate.py:1-19]`).

---

### `journal.py` (additive `RECORD_TYPES` member, `[PLAN-SPECIFIED]`)

**Analog: itself, prior state, quoted (`14A-02-PLAN.md:104-141`), showing the
exact additive-growth precedent already used twice before 15A:**

```text
RECORD_TYPES = OPERATION_TYPES + ("mint", "restore", "external_edit")
where OPERATION_TYPES = ("link", "import", "copy", "move", "edit_in_place",
"supersede")
```
(`[PLAN-SPECIFIED: 14A-02-PLAN.md]`, restated per `14B-PATTERNS.md:122-125`,
which already cites the exact same line range for `course_package.py`'s
`"restore"` addition. 14A-03 added `"reconcile"`; 14B-04 added `"migrate"`
this same way.)

15A adds one further member (e.g. `"agent_operation"`) and, per
RESEARCH.md's Pitfall 3, maps RELIABILITY-02's field list (intent, actor,
scopes, checkpoints, proposals, egress) onto **new optional keys on the
existing entry shape** (`journal.ENTRY_KEYS`), never a second `*_journal.py`
file or a second `.jsonl` sibling log. The fixed-order key tuple this entry
extends, quoted verbatim:

```text
# Source: 14A-02-PLAN.md:126-131
schema_version, entry_id, timestamp, operation, state, resolves_entry,
object_id, kind, revision, parent_revision, path, expected_fingerprint,
before_fingerprint, after_fingerprint, before_image, undo,
source_object_id, source_revision, restores_revision, origin, code, message
```

15A's plan should state explicitly which new optional keys it adds (e.g.
`intent`, `checkpoint`, `egress`) as an appendix to this tuple, following the
exact "additive keys, never a restructured shape" rule the tuple itself
already demonstrates (every 14A/14B addition so far has been a new tuple
member or a new optional key, never a renamed or removed one).

---

### `settings.model_backend.profiles` (fixture profile registration, no new dispatcher)

**Analog: the shipped profile record shape, `[VERIFIED:
schemas/settings.schema.json:190-246]`, quoted (abridged):**

```json
{
  "name": "mock-hosted",
  "transport": "hosted_cli",
  "command": ["python", "fixtures/mock_hosted_cli.py"],
  "timeout_seconds": 30,
  "max_output_bytes": 65536,
  "context_window": 8192
}
```

Per RESEARCH.md Pitfall 4, register two ordinary profiles (one
`transport: "hosted_cli"` pointed at a fixture script, one
`transport: "openai_compatible"` pointed at a fixture HTTP server) exactly as
any other profile is registered in `settings.model_backend.profiles`, and
drive both through the unmodified `model_adapter.invoke()`. Do not write a
function or module whose name contains `mock_hosted`/`mock_local` that
bypasses `invoke()`, which is the exact anti-pattern this pitfall names.

---

### `tests/four_subject_review.py` (new tracer, fault-injection + batch)

**Analog: `tests/three_domain_tracer.py`'s planned shape, itself modeled on
`tests/file_fault_tracer.py`, per `14B-PATTERNS.md:247-253` (reused, not
re-read this session):** named `scenario_*()` functions, a `fail(msg)`
helper, a `main()`, and a final `"TRACER: N passed, M skipped, 0 failed"`
line. `14B-PATTERNS.md` already states the precondition-check convention
this tracer must extend: confirm the shipped suite is green and that
`14A-FREEZE.md`/`14B-FREEZE.md` (and, for 15A, its own precondition of both)
exist before importing `identity`/`journal`/`graph`/`course` at all.

**`fail()` helper, code-verified, identical across every existing
`tests/*_roundtrip.py` file:**

```python
# Source: tests/evidence_roundtrip.py:38-40, quoted verbatim
def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)
```

**Header/import convention, code-verified `[VERIFIED: tests/evidence_
roundtrip.py:1-25]`:**

```python
#!/usr/bin/env python3
"""One-paragraph statement of what this test proves end-to-end and why."""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
```

`tests/four_subject_review.py` differs in one respect worth naming, per the
same reasoning `14B-PATTERNS.md` already applied to `graph_roundtrip.py`:
since `director.py`/`graph.py`/`course.py` are not yet CLI-wired (per
RESEARCH.md's Open Question 1, the freeze gate defaults to an internal-API
shape), this tracer should `import director, graph, course, journal,
identity, model_adapter` directly and call functions, rather than driving
`subprocess`/CLI. `model_adapter.invoke()` itself is called directly, the
same way Phase 8's own transport-parity tests already call it (RESEARCH.md
Pitfall 4).

**Assertion-style precedent for the egress-log check, code-verified
`[VERIFIED: tests/evidence_roundtrip.py:27-35]`:**

```python
EXPECTED_KEYS = {
    "schema_version", "event_id", "event_type", "ts", "session_id", ...
}
```
Reusable shape for asserting a `treatment_recommend` journal entry's or
egress field set's required keys.

---

### `tests/journal_roundtrip.py` (possibly extended)

If the `agent_operation` `RECORD_TYPES` member is not added by a 14A- or
14B-scoped plan before 15A executes (per RESEARCH.md's own Wave 0 Gaps note),
`tests/journal_roundtrip.py` gains a `check_agent_operation_record()`
function following the exact structure its existing `check_*()` functions
already use (per this project's stated `check_*()` convention in
`.claude/CLAUDE.md`'s "Helper functions are prefixed by purpose" note). No
code was re-read for this file this session beyond the convention already
established for every `tests/*_roundtrip.py` file above; the 15A plan should
name explicitly which phase (14A, 14B, or 15A itself) owns this addition, per
RESEARCH.md's own instruction.

## Shared Patterns

### One typed adapter boundary, additive operation, no second dispatcher
**Source:** `model_adapter.py:1-96` `[VERIFIED]`.
**Apply to:** `director.py`'s only call into the adapter layer; `settings.
model_backend.profiles`'s two new mock entries.

### Live rights re-check at write time, never a snapshot
**Source:** `[PLAN-SPECIFIED: 14A-03-PLAN.md:412-455]`; second-site precedent
`[PLAN-SPECIFIED: 14B-03-PLAN.md:174-209]` ("No stale snapshot ever
authorizes", Pitfall 5).
**Apply to:** `director.py`'s validation pass before calling
`course.bind_treatment`.

### One operation journal, additive RECORD_TYPES, never a second log
**Source:** `[PLAN-SPECIFIED: 14A-02-PLAN.md:104-141]`, already exercised by
14A-03 (`"reconcile"`) and 14B-04 (`"migrate"`).
**Apply to:** the `agent_operation` record type and the egress fields 15A
adds to the existing journal entry shape.

### Closed vocabulary, distinct from a lookalike vocabulary elsewhere in the codebase
**Source:** `auditor.py:370-489` `[VERIFIED]` (states `"gap"`, `"partial"`,
`"covered"`, `"conflicting"`, `"unknown"`, a *different* five-state
vocabulary than TREAT-02's `graph.BINDING_STATES` `[PLAN-SPECIFIED:
14B-03-PLAN.md]` (`"covered"`, `"thin"`, `"missing"`, `"conflicting"`,
`"unknown"`)).
**Apply to:** any code in `director.py` or `tests/four_subject_review.py`
that reads or writes a coverage-state string. `auditor.coverage_report` may
be called as one input signal to a recommendation, but its state strings
must never be written into a `graph.BINDING_STATES` field, and vice versa.
See RESEARCH.md Pitfall 1 for the full citation.

### Local test `fail()` helper, no shared test-util import
**Source:** every existing `tests/*_roundtrip.py` file, `[VERIFIED: tests/
evidence_roundtrip.py:38-40]`.
**Apply to:** `tests/four_subject_review.py` and any extension to `tests/
journal_roundtrip.py`.

### Schema keyword ceiling, no conditional logic inside a schema
**Source:** `schema_validate.py:1-35` `[VERIFIED]`.
**Apply to:** the `operation` enum edit to `schemas/model_adapter.schema.
json`; any payload-shape requirement specific to `treatment_recommend`
belongs in `model_adapter.py`'s runtime check, not the schema.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `director.py`'s egress-recording function itself (the specific "what left the machine and to whom" record shape) | new function, no prior owner | event-driven | RESEARCH.md states plainly: "No shipped or planned module owns 'what left the machine and to whom' today. This is 15A's one genuinely new durable object." The closest available shape is the journal-entry-field extension pattern above (reused structurally), but there is no existing egress-specific analog to copy field-for-field; the exact field set (`spans`, `destination`, `backend`, `approved_span_ids`) is new design this phase must lock, flagged in RESEARCH.md as `checkpoint:decision` candidate A2. |
| `fixtures/corpus_14b.py`'s fourth synthetic domain (standardized-exam blueprint) | fixture data | file-I/O, synthetic tree | Not source code; extends a fixture that is itself only plan-specified (`14B-02-PLAN.md:85`), not yet on disk. No standardized-exam-blueprint fixture exists anywhere in the repository to copy structurally; this is genuinely new fixture construction over an already-planned generator's `build_three_domains`/`build_all` shape. |

## Metadata

**Analog search scope:** root-level shipped modules (`model_adapter.py`,
`tier_gate.py`, `auditor.py`, `schema_validate.py`, `evidence.py`),
`schemas/` directory (`model_adapter.schema.json`, `settings.schema.json`),
`tests/` directory conventions (`tests/evidence_roundtrip.py` read in full at
40 lines; the `tests/*_roundtrip.py` naming/`fail()` convention confirmed
across the full `tests/` directory listing), plus the full text of
`.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md` and
`14A-03-PLAN.md` (targeted greps for exact signatures) and
`.planning/phases/14B-graph-course-package-prototype/14B-PATTERNS.md` (full,
reused rather than re-reading its underlying source files a second time).
**Files scanned:** `model_adapter.py` (lines 1-100), `tier_gate.py` (lines
1-60), `auditor.py` (targeted grep, lines 370-489), `schema_validate.py`
(lines 1-70), `evidence.py` (lines 45-60), `schemas/model_adapter.schema.
json` (lines 1-30), `schemas/settings.schema.json` (lines 190-250),
`tests/evidence_roundtrip.py` (lines 1-40), `14A-02-PLAN.md` (targeted grep
and lines 100-150), `14A-03-PLAN.md` (targeted grep for rights functions),
`14B-PATTERNS.md` (full, 338 lines).
**Pattern extraction date:** 2026-08-14
