# Phase 16B: IA, Modes & Recovery Contract - Pattern Map

**Mapped:** 2026-08-15
**Files analyzed:** 9 (new or modified)
**Analogs found:** 7 real, executed analogs / 9. Two files (`journal.py`-backed
Activity read path, the two-freeze precondition check) have only plan-text
analogs because `journal.py` (Phase 14A) does not exist on disk, confirmed
this session by the same `ls *.py` check `16B-RESEARCH.md` already ran
(`identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`,
`course_package.py`, `director.py`, `blueprint.py` all `MISSING`). Those
citations are treated as plan-text analogs, never as existing code, per
16B-RESEARCH.md's own caveat and mirroring 16A-PATTERNS.md's precedent for
the same situation one phase earlier.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `surfaces/daemon.py` (`handle_index` gains course-shelf branch) | route/controller | request-response | `surfaces/daemon.py:939-968` (`handle_index`, same file, in place) | exact (in-place additive branch) |
| `surfaces/daemon.py` (`ROUTES`/`API_ROUTES`/`ROUTE_CLI`/`SURFACE_PARITY` gain `/activity`, `/course/<id>/...`, `/help/<code>`) | route/config (route table) | request-response | `surfaces/daemon.py:210-335` (the four parallel structures, same file) | exact |
| `surfaces/ia.py` (new: course-shelf listing, deep-link/anchor resolution, mode-layer precedence resolver-stub) | model/registry (pure, no I/O beyond reading `course.py`/`journal.py` once they exist) | CRUD (in-memory lookup) + transform | `capabilities.py` naming/shape precedent from 16A-PATTERNS.md (pure lookup module, closed tuples, no file I/O); `model.py:2052` (`GATE_VALUES` closed-tuple shape) | role-match (real, via 16A precedent) |
| `surfaces/ia.py` (Activity read model over `journal.entries()`/`replay()`/`object_state()`) | service (read model) | event-driven (reads durable job log) | 14A-02-PLAN.md:104-140 (`journal.py`'s planned public surface, plan-text only); `runtime.py:1509-1531` (`glossable`) for the "decide disclosure via a gate function, never invent a scanner" shape | plan-text (data source); role-match (real, gate-function shape) |
| `schemas/settings.schema.json` (five new top-level keys: `approved_roots`, `network_egress`, `accessibility`, `storage`, plus unchanged `model_backend`/`update_policy`) | config/schema | transform (validation) | `schemas/settings.schema.json` itself (already shipped; extend, do not fork) + `schema_validate.py`'s closed keyword set | exact |
| `surfaces/settings.py` (`SETTINGS_CODES` unchanged shape, new defaults accessors for the five groups if any carry defaults) | service/validator | CRUD (load/validate settings) | `surfaces/settings.py:1-57` (module docstring, `SETTINGS_CODES`, `STYLE_SETTINGS_DEFAULTS`/`PARAPHRASE_SETTINGS_DEFAULTS` accessor precedent) | exact |
| `fixtures/help_codes.py` or bundled help lookup table (new: `ia.course_corrupted`, `ia.activity_unavailable`, `ia.route_not_found`, etc.) | config (static content) | request-response (local lookup, no network) | `surfaces/settings.py:34-42` (`SETTINGS_CODES` dotted-code convention) + `resources.py` (bundled-asset read precedent) | role-match (real, convention); role-match (real, delivery mechanism) |
| `tests/ia_route_roundtrip.py`, `tests/ia_storyboard_tracer.py`, `tests/mode_layer_roundtrip.py`, `tests/degraded_state_roundtrip.py` (new) | test (tracer/roundtrip suite) | batch (drives real routes+fixtures) | `tests/daemon_roundtrip.py` (`check_api_route_scope`, `check_surface_parity`, the real coupling-test convention for the route table this phase extends) + `tests/evidence_roundtrip.py` (`fail(msg)`, direct-execution convention) | exact |
| `fixtures/course_storyboard_corpus.py` (new: synthetic multi-course fixture for loops A-G) | test fixture / factory | batch (generates fictional corpus content) | `fixtures/grandchild_spawner.py` (closest real Python fixture-generator shape); `fixtures/lesson_capability_corpus.py` naming/seed convention from 16A-PATTERNS.md | role-match (real) |

## Pattern Assignments

### `surfaces/daemon.py` (`handle_index` course-shelf branch) (route/controller, request-response)

**Analog:** `surfaces/daemon.py:939-968`, `handle_index` (same file, in place)

**Existing branch-on-population pattern** (lines 939-964, quoted/abridged):
```python
def handle_index(handler):
    """`GET /` -- the index of every bank and day plan this daemon found at
    startup, rendered through the shared presentation shell with the
    per-render theme block (plan 04-04 Task 2). The page distinguishes the
    populated case, the no-configured-banks/plans case, and stem collisions
    ... as a labelled warning with recovery actions.
    """
    banks, plans = handler.banks, handler.plans
    theme_block = theme.theme_css(settings.load_settings(handler.root))
    stems = sorted(set(banks) | set(plans), key=str.lower)
    if stems:
        report_links = sessions_by_bank(handler.root, banks)
        rows = []
        for stem in stems:
            ...
        body = "\n".join(rows)
```
Per Decision D1 (`16B-UI-SPEC.md`), the course-shelf branch is inserted as a
new condition inside this same function, gated on whether any course exists
(`course.py`, unbuilt), never a second route. The shipped "populated /
empty / degraded-with-recovery-actions" three-way branch shape (stems truthy
/ falsy / `handler.collisions` present) is the exact shape to reuse for
"courses exist / zero courses (`No courses yet`) / a corrupted course showing
its last valid overview". When `course.py` is absent, this function's
existing bank/plan listing is the fallback body, unchanged, matching the
research's "degrades to the current bank-index behavior when no course exists
yet" recommendation.

---

### `surfaces/daemon.py` (route table extension: `/activity`, `/course/<id>/...`, `/help/<code>`) (route/config, request-response)

**Analog:** `surfaces/daemon.py:210-335` (`API_ROUTES`, `ROUTES`, `ROUTE_CLI`, `SURFACE_PARITY`)

**Fixed-literal-before-stem-parameterized ordering rule** (lines 238-244, quoted verbatim):
```python
# Order is load-bearing: every fixed literal route comes before every
# stem-parameterised route, so a bank or plan whose stem happens to be
# "report", "day" or "api" can never shadow a fixed route. Dispatch is
# first-match-wins over this tuple, walked in order by
# `DaemonHandler._dispatch`.
ROUTES = (
    ("GET", "/", "handle_index"),
    ("GET", MARKER_PATH, "handle_marker"),
    ("GET", "/day", "handle_day_index"),
    ("GET", "/report", "handle_report_get"),
    ("GET", "/settings", "handle_settings_get"),
    ("GET", "/disclosure", "handle_disclosure"),
    ("POST", "/api/theme", "handle_theme_post"),
    ("POST", "/cli-twin", "handle_cli_twin"),
    ("POST", "/seed/accept", "handle_seed_accept"),
) + API_ROUTES + (
    ("GET", KATEX_ASSET_RE, "handle_katex_asset"),
    ...
)
```
`GET /activity` (Decision D2) is a new fixed-literal entry inserted into the
first block, before `+ API_ROUTES +`, per the ordering rule quoted above.
`/course/<course_id>` and its eight areas (Decision D3) are new
stem-parameterized entries inserted into the trailing regex block, following
the same `..._RE` naming convention as `QUIZ_GET_RE`/`LESSON_GET_RE`. `GET
/help/<code>` is a new stem-parameterized entry in the same trailing block.

**CLI-parity dict shape** (lines 277-313, quoted/abridged):
```python
ROUTE_CLI = {
    ("GET", "/"): "daemon",
    ("GET", MARKER_PATH): "daemon",
    ("GET", "/report"): "report",
    ("GET", "/settings"): "theme",
    ...
}
```
Per Decision D1, `("GET", "/")` keeps mapping to `"daemon"` unchanged. Every
new route this phase adds needs a `ROUTE_CLI` entry (SURF-04's "every route
has a CLI equivalent" is machine-checked, not a claim in prose) and, for any
new `/api/*` entry, a `SURFACE_PARITY` row reserving its future MCP tool
name (lines 315-335), per Extensibility Rule 9(a).

**Coupling test to extend, not fork:** `tests/daemon_roundtrip.py`'s
`check_api_route_scope`/`check_surface_parity` assert these four structures
agree in shape; every new 16B route is a new row in the existing coupling
test's inputs, never a second coupling test.

---

### `surfaces/ia.py` (new pure module: course-shelf listing, deep links, mode-layer precedence) (model/registry, CRUD + transform)

**Analog (real, via naming precedent):** 16A's `capabilities.py`, itself
patterned on `model.py:2052`'s closed-tuple shape (`16A-PATTERNS.md`):
```python
# Source: model.py:2052, quoted verbatim
GATE_VALUES = ("required", "recommended", "off")
```
Every closed vocabulary `ia.py` needs (course attention-state tokens, the
seven mode-layer names, degraded-state codes) should be a plain module-level
tuple constant in this shape, not an enum class or external config file.

**Analog (plan-text only):** `graph.py`'s planned no-file-I/O pure-module
pattern, cited `[VERIFIED: 14B-01-PLAN.md:112-118]` via `16A-PATTERNS.md`.
`graph.py` is confirmed `MISSING` on disk this session. Its cited shape
(closed tuples plus a pure function with no I/O) is the structural precedent
`ia.py`'s course-shelf/resume-cue functions should follow: pure functions
that read `evidence.py` (real, shipped) directly and, once 14A lands,
`journal.py`, never a cache or a second evidence store.

**Do not fold into:** `surfaces/daemon.py` (route/rendering scope only) or
`capabilities.py` (16A's lesson-capability scope, orthogonal concern); `ia.py`
is a new, separate pure module per the project's "no barrel files, direct
imports" convention (`.claude/CLAUDE.md` Module Design section).

---

### `surfaces/ia.py` (Activity read model over the journal) (service, event-driven)

**Analog (plan-text only, not executed):** `14A-02-PLAN.md:104-140`, the
planned `journal.py` public surface:
```python
# Source: 14A-02-PLAN.md:104-140 (plan text; journal.py does not exist yet)
import journal

def activity_needs_input(course_root):
    """Return entries whose 'prepared' state has no resolving entry yet."""
    resolved_ids = set()
    prepared = []
    for entry in journal.entries(course_root):
        if entry["state"] in ("applied", "refused") and entry["resolves_entry"]:
            resolved_ids.add(entry["resolves_entry"])
        elif entry["state"] == "prepared":
            prepared.append(entry)
    return [e for e in prepared if e["entry_id"] not in resolved_ids]
```
This is the exact composition shape `ia.py`'s `handle_activity_get`-feeding
function should copy: iterate `journal.entries()`, classify by `state`,
never write to the journal from this path. When `journal.py` is absent
(`MISSING`, confirmed this session), the function must catch `ImportError`
(or check module presence) and return the "Activity isn't available yet in
this build" state (`16B-UI-SPEC.md` Activity Contract table), never raise
past the route handler.

**Analog (real) for "the runtime, never the view, decides disclosure":**
`runtime.py:1509-1531`, `glossable()`, cited via `16A-PATTERNS.md`'s Shared
Patterns section. The same discipline applies here in reverse: `ia.py`'s
Activity view must render only journal metadata (state, timestamps, object
kind, stated reason), never `before_image` or raw content bytes, mirroring
`runtime.public_item()`'s public/private payload split
(`16B-UI-SPEC.md`'s "Journal metadata boundary" clause).

---

### `schemas/settings.schema.json` (five new top-level keys) (config, transform)

**Analog:** the file itself (already shipped, confirmed via `json.load`
this session: existing top-level keys `theme, accent, daily_cap,
selection_weights, selection, auditor_autonomy, model_backend,
suggestion_reveal, update_policy, daemon, reader, teaching, update, style,
paraphrase, lti, retention, audio, check, subject_profiles`).

**Closed-vocabulary schema shape to reuse** (from `16A-PATTERNS.md`'s
extraction of `schemas/visual_interaction.schema.json:36-43`):
```json
"action_type": {
  "type": "string",
  "enum": ["place_point", "move_point", "select_numberline_point", ...]
}
```
`approved_roots` (array of strings), `network_egress` (object with a boolean
`hosted_operations_disclosed`-style field), `accessibility` (object,
`reduced_motion`/high-contrast booleans), and `storage` (object, backup/export
controls) must each stay inside `schema_validate.py`'s closed keyword set
(`type`, `properties`, `required`, `additionalProperties`, `enum`, `const`,
`items`, `minItems`, `uniqueItems`, `minLength`, `pattern`, `minimum`,
`maximum`, `$defs`, `$ref`, `oneOf`), matching every existing group's
`additionalProperties: false` discipline. A settings file predating these
five keys must still `load_settings()`/validate exactly as today
(non-negotiable #4, and `16B-UI-SPEC.md`'s own additive-format requirement).

---

### `surfaces/settings.py` (module extension, defaults accessors) (service/validator, CRUD)

**Analog:** `surfaces/settings.py:1-57` (module docstring, `SETTINGS_CODES`,
`STYLE_SETTINGS_DEFAULTS`/`PARAPHRASE_SETTINGS_DEFAULTS`), quoted verbatim:
```python
"""The settings surface: `itembank config` is to `itembank.json` what `itembank
spec` is to the bank format and `itembank schema` is to the published
documents -- one contract, printed either as a human summary or verbatim off
disk, and one validator behind every write.

There is exactly one validator here, `schema_validate.validate()` ...
"""
SETTINGS_FILE = "itembank.json"
SETTINGS_CODES = tuple(sorted({
    "settings.invalid_type", "settings.invalid_value", "settings.out_of_range",
    "settings.unknown_key", "settings.missing_key", "settings.malformed_file",
}))

STYLE_SETTINGS_DEFAULTS = {"imperative_cap": 7, "warn_fp_threshold": 0.20}
PARAPHRASE_SETTINGS_DEFAULTS = {"winnow_threshold": 8, "jaccard_threshold": 0.25}
```
`SETTINGS_CODES` is a set-then-sorted tuple; the five new settings groups
introduce **no new codes** unless a genuinely new validation failure class
is needed (the existing six codes already cover type/value/range/unknown/
missing/malformed for any new key). If any of the five groups (e.g.
`accessibility`) ships with defaults, add a module-level dict accessor in
this exact `..._SETTINGS_DEFAULTS` shape, one per settings group, never a
single catch-all defaults dict.

**One validator, reused, never duplicated:** `schema_validate.validate()` is
the only validator; `surfaces/settings.py`'s docstring states this
explicitly. No 16B code may hand-roll a second type/range check for the five
new keys.

---

### Offline help lookup table (`ia.<code>` help entries) (config, request-response)

**Analog (real):** `surfaces/settings.py:34-42`'s dotted-code convention
(`SETTINGS_CODES`) extended to a new closed namespace `ia.*`
(`ia.course_corrupted`, `ia.activity_unavailable`, `ia.route_not_found`,
matching `16B-UI-SPEC.md`'s Offline Help contract). Build the code list the
same set-then-sorted-tuple way, provably sorted and duplicate-free.

**Delivery mechanism analog:** `resources.py`'s bundled-asset-read pattern
(cited by `16B-RESEARCH.md`'s Architectural Responsibility Map row for
"First-run sample course + walkthrough" and "Offline help routed from named
error codes", both keyed to `resources.py`). The help table and the sample
course are both static, bundled, offline content read the same way, no
network fetch, ever, for the baseline (`16B-UI-SPEC.md` Offline Help
Contract, Pitfall 5 in `16B-RESEARCH.md`).

---

### `tests/ia_route_roundtrip.py`, `tests/ia_storyboard_tracer.py`, `tests/mode_layer_roundtrip.py`, `tests/degraded_state_roundtrip.py` (new) (test/tracer, batch)

**Analog (real):** `tests/daemon_roundtrip.py`'s `check_api_route_scope`/
`check_surface_parity` (the exact coupling-test convention `16B-RESEARCH.md`
Pattern 2 names) for `ia_route_roundtrip.py`; `tests/evidence_roundtrip.py`'s
shared shell (from `16A-PATTERNS.md`) for every new test file:
```python
#!/usr/bin/env python3
"""... Standard library only, runnable as `python tests/evidence_roundtrip.py`."""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402

def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)
```
No pytest/unittest framework anywhere in this repo (confirmed by the shipped
`tests/*.py` convention); every new 16B test file defines its own local
`fail(msg)` and is directly executable via `python tests/<file>.py`.

**Analog (plan-text only, summary-line convention):** the `"TRACER: N
passed, M skipped, 0 failed"` summary-line convention `16A-PATTERNS.md`
cites from `tests/three_domain_tracer.py`/`tests/file_fault_tracer.py`
(14A/14B plan text, files confirmed `MISSING` this session). `
ia_storyboard_tracer.py`'s loop-A-through-G interruption scenarios should
follow this same `scenario_*()` + `main()` + summary-line shape, re-verified
against real code once 14A/14B land.

---

### `fixtures/course_storyboard_corpus.py` (new) (test fixture, batch)

**Analog (real):** `fixtures/grandchild_spawner.py`, the closest real
Python fixture-generator module shape in `fixtures/` (module-level
functions producing deterministic synthetic content).

**Analog (real, naming/seed convention):** `fixtures/lesson_capability_corpus.py`
(16A's own new fixture, `16A-PATTERNS.md`), which itself follows the
planned `fixtures/corpus_14b.py` convention ("fictional content only, fixed
seed"). `course_storyboard_corpus.py` follows the identical convention: two
fictional courses (per APP-01's fixture), one deliberately corrupted, no
real course/learner/bank content, `random.Random(<fixed seed>)` for any
generated variance.

**Mandatory acceptance check:** `python itembank.py guard .` must pass on
any task touching `fixtures/`, matching 16A's own "no real question banks"
enforcement precedent.

## Shared Patterns

### One dispatcher, four parallel structures, never a second router
**Source:** `surfaces/daemon.py:210-335` (`ROUTES`, `API_ROUTES`,
`ROUTE_CLI`, `SURFACE_PARITY`) plus `tests/daemon_roundtrip.py`'s coupling
checks.
**Apply to:** every new route this phase adds (`/activity`,
`/course/<course_id>/...`, `/help/<code>`, the expanded `/settings`
response body).

### One-line additive registration (closed vocabulary, never a new branch)
**Source:** `model.py:2052` (`GATE_VALUES`), `surfaces/settings.py:39-42`
(`SETTINGS_CODES`).
**Apply to:** `ia.py`'s closed tuples (attention-state tokens, mode-layer
names, degraded-state codes), the new `ia.*` help-code namespace, the five
new settings-schema top-level keys.

### One validator, `schema_validate.validate()`, never duplicated
**Source:** `surfaces/settings.py:1-11` (module docstring), `schema_validate.py`.
**Apply to:** every new field in the five expanded settings groups; no 16B
code hand-rolls a second type/range/enum check.

### The runtime (or journal), never the view, decides disclosure and authority
**Source:** `runtime.py:1509-1531` (`glossable`), `runtime.py:44-73`
(`public_item`), `14A-02-PLAN.md:104-140` (`journal.py`'s planned surface).
**Apply to:** the Activity view's read-only journal-metadata rendering, the
mode-layer precedence table's "runtime authority" and "system safety" rows
(rendered read-only, never a toggle), and the locked-refusal-card contract
(FLOW-02): the card states an unlock condition computed server-side, never a
client-guessed one.

### Basename-only path disclosure, never a resolved absolute path
**Source:** `surfaces/lesson.py:77-88` (`STYLE_DEGRADED_COPY`,
`WARN_CSS` comment: "the bank basename -- never a resolved absolute path
(T-3-07 precedent)"), and `surfaces/lesson.py:1797,1821,1935,1947` (`os.path.basename(bank_path)` call sites).
**Apply to:** the Degraded-State Matrix's "Permission denied" row
(`16B-UI-SPEC.md` Decision D9), and any other 16B copy that names a
filesystem path.

### Shipped-suite regression discipline
**Source:** project convention, confirmed via `tests/*.py` directory
listing (60+ existing `*_roundtrip.py`/`*_audit.py`/`*_tracer.py` files, no
framework).
**Apply to:** every new 16B test file; full-suite check remains
`for t in tests/*.py; do python "$t" || exit 1; done`.

### Precondition check before importing an unexecuted module (extended one degree)
**Source:** `16A-01-PLAN.md:246-374` (the working single-freeze pattern),
extended per `16B-RESEARCH.md` Pattern 1 to check **two** frozen headings
(`14A-FREEZE.md`'s `## Frozen at 14A` and `16A-FREEZE.md`'s `## Frozen at
16A`) plus `16A-PRECONDITION.md`'s own dated result line (Pitfall 1).
**Apply to:** 16B-01's opening task, and any later 16B plan that would
`import journal`, `import course`, `import graph`, or `import capabilities`.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `ia.py`'s mode-layer precedence *documentation* structure (the settings-visible read-only rendering of the seven-layer table) | model/registry | transform | No existing settings group renders a fixed, non-configurable value as read-only explanatory text today; the closest shape (`STYLE_SETTINGS_DEFAULTS`) is a configurable default, not a fixed-and-inert row. Genuinely new; `16B-UI-SPEC.md`'s own Decision D8 marks full *enforcement* as out of scope for 16C, so this file only needs the display shape, not a resolver. |
| Course-level route handlers' actual content (Overview/Learn/Practice/Test/Course-map/Sources/Build-review/Evidence bodies, as opposed to their route registration and degraded fallback) | route/controller | request-response | Depends on `course.py`/`graph.py` (14B, unbuilt, confirmed `MISSING`); every such handler must sit behind the 16B-01 precondition check and render only the degraded "not yet available"/fallback state until those modules exist, per `16B-RESEARCH.md`'s own scoping. |
| Walkthrough contextual-callout anchoring mechanism | presentation | event-driven | No existing shipped surface implements an anchored, replayable, dismissible in-page walkthrough; `16B-UI-SPEC.md`'s Walkthrough steps row states each step deep-links to a real area with no separate "tour mode" route, but the callout-rendering mechanism itself has no in-repo precedent and is new client-side work deferred in part to 17A for visual tokens. |

## Metadata

**Analog search scope:** `surfaces/daemon.py`, `surfaces/settings.py`,
`surfaces/lesson.py`, `schemas/settings.schema.json`, `schema_validate.py`,
`runtime.py`, `resources.py`, `tests/daemon_roundtrip.py`,
`tests/evidence_roundtrip.py`, `fixtures/grandchild_spawner.py`, plus the
prior sibling `16A-PATTERNS.md` for its already-verified naming and
convention precedents (`capabilities.py`, `fixtures/lesson_capability_corpus.py`),
plus a live filesystem check for the plan-text-only modules 16B-RESEARCH.md
cites from 14A/14B (`journal.py`, `course.py`, `graph.py`, `identity.py`,
`discovery.py`, `course_package.py`, `director.py`, `blueprint.py`), all
confirmed `MISSING` this session, consistent with 16B-RESEARCH.md's own
caveat.
**Files scanned:** 9 target files/classes plus roughly ten real codebase
files read or grepped for analog extraction.
**Pattern extraction date:** 2026-08-15

## PATTERN MAPPING COMPLETE
