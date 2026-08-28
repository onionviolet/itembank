# 16A-04 summary: fifteen capability profiles, one published schema, one degradation proven

**Executed 2026-08-28.** Darwin arm64, Python 3.14.6. Plan
`16A-04-PLAN.md`, three tasks, all complete.

Output: fifteen profiles carrying all six CAP-02 fields, a schema the shipped
validator accepts, and the Degraded clause proven against behavior the renderer
already had.

---

## 1. The fifteen capability names in registry order

`capabilities.profiles()` returns exactly these, in the module dict's literal
source order. The first fourteen are in `SEMANTIC_ROLE_CATALOG`'s order, so the
two lists read the same way down the page.

```
callout_key, callout_warning, callout_prerequisite, callout_misconception,
callout_tip, callout_example, callout_counterexample, callout_excerpt,
glossary_definition, callout_uncertainty, callout_summary, inline_check,
hint_ladder, visual_interaction, guided_mode
```

`guided_mode` is last and is the single profile that maps to no catalog role.
The mapping between the fourteen roles and their profiles is
`capabilities._ROLE_PROFILE_NAMES`, reached through
`capabilities.catalog_profile_name`; see deviation D2.

**No profile's `known_limits` says `none`, and none needed rewriting to avoid
it.** Each was written with a real limitation in hand: the callout labels are
untranslated, the excerpt callout has no structural link to a `## SOURCES` row,
the misconception callout is unlinked to any item's distractor analysis, the
uncertainty callout does not mark the items downstream of a disputed claim, the
summary callout is never checked against the section it summarizes, the worked
example has no annotated per-step structure (`D-16A-6`), the warning has no
structured staleness field (`D-16A-7`), the glossary returns a bare 404 for a
suppressed term, the inline check's unresolvable reference loosens rather than
tightens the gate, every hint tier is authored so an unwritten trap leaves tier
2 permanently empty, visual scoring is dichotomous, and guided mode persists
nothing across a stage boundary (`D-16A-9`).

## 2. The `inline_check` `offline_fallback` string, verbatim

```
This check is available when you are reading with a session.
```

It now has exactly one home:

```
$ grep -c "This check is available when you are reading with a session." surfaces/lesson.py capabilities.py
surfaces/lesson.py:0
capabilities.py:1
```

**`tests/gate_roundtrip.py` was green before Task 3 and is green after it.** It
was run immediately before the rewire (exit 0), immediately after (exit 0), and
again at the end of the plan (exit 0). `tests/lesson_roundtrip.py` likewise.
That is what makes the byte-identity claim a proof rather than an assertion: the
gate suite asserts those exact rendered bytes, so a one-character difference
between the registry string and the shipped one would have turned it red.

## 3. Which import branch Task 1 step 5 took

**Top-level.** `identity.py` defines `RIGHTS_STATES` as a plain module-level
tuple at `identity.py:295` with no import-time side effect, so
`capabilities.py` carries `import identity` at module scope and
`MEDIA_RIGHTS_STATES = identity.RIGHTS_STATES`. No function-local import was
needed.

```
$ python -c "import capabilities as C, identity; print(C.MEDIA_RIGHTS_STATES is identity.RIGHTS_STATES, C.MEDIA_AVAILABILITY)"
True ('present', 'missing', 'remote')
```

The `is` check, not an equality check, is what makes a retyped tuple with the
same three members fail: the whole point of `D-16A-8` is that there is one
rights vocabulary and not two.

## 4. The schema's `required` and `enum` arrays as written

`required`, seven members:

```
["name", "accessible_behavior", "offline_fallback", "renderer_availability",
 "version", "validation", "known_limits"]
```

`properties.renderer_availability.enum`, three members:

```
["available", "degraded", "unavailable"]
```

`additionalProperties` is `false`. `tests/capability_profile_check.py`'s
`check_schema_drift` reads both arrays from the schema and both tuples from
`capabilities.py` and compares them, so neither is restated in the test.

## 5. Whether `check_schema` accepted the schema on the first attempt

**Yes, on the first attempt, including its annotation header.**

```
$ python -c "import json, schema_validate; d=json.load(open('schemas/capability_profile.schema.json')); schema_validate.check_schema(d); print('schema accepted')"
schema accepted
```

```
$ python schema_validate.py --all
...
20 schema documents self-check clean
```

This is deviation D1 below: the plan forbade `$schema`, `title`, and
`description` on the stated grounds that `check_schema` refuses any keyword
outside `SUPPORTED`. That is factually incorrect, and the schema carries them.

## 6. The four broken-entry validation results

Each of the four deliberately broken profiles produces at least one error
naming the offending field, asserted in
`check_schema_refuses_broken_profiles`:

| Broken entry | Result |
|---|---|
| `offline_fallback` key removed | fails, error names `offline_fallback` |
| `renderer_availability` set to `sometimes` | fails, error names `renderer_availability` |
| an extra key `colour` added | fails, error names `colour` (`additionalProperties: false`) |
| `offline_fallback` set to the empty string | fails, error names `offline_fallback` (`minLength: 1`) |

`check_validator_still_refuses_unsupported_keywords` additionally proves the
validator's own refusal path in memory rather than on disk: a copy of the schema
carrying `patternProperties` raises `SchemaError`. Nothing is written.

## 7. The tracer's final summary line, verbatim

```
scenario thin_slice: pass
scenario additivity_golden_parse: pass
scenario fourteen_roles: pass
scenario unknown_semantics: pass
scenario example_order: pass
scenario capability_profiles: pass
scenario unavailable_renderer: pass
TRACER: 7 passed, 0 skipped, 0 failed
```

Exit 0. `16A-VALIDATION.md`'s expected count after 16A-04 is 7, so no scenario
was added or lost.

`tests/capability_profile_check.py` prints `capability registry ok` and exits 0.

## 8. The additivity proof, re-verified

```
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```

All three unchanged from `16A-PRECONDITION.md`.

`python itembank.py guard .` reports `0 offending files`.

**Full suite.** The same three pre-existing red files as after 16A-03, and no
others: `tests/day_roundtrip.py`, `tests/phase_062_audit.py`, and
`tests/retention_ui_roundtrip.py`. All three fail against a clean stash of this
work as well.

## 9. Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| fifteen profiles, six fields each, catalog coupling, adjacency, empty, ordering probes | `python tests/capability_profile_check.py` | `capability registry ok`, exit 0 |
| the shipped glossary is catalogued and describes shipped behavior | the `glossary_definition` profile, read against `surfaces/lesson.py`'s `GLOSS_ENHANCEMENT_JS`, `UNAVAILABLE_COPY`, and `runtime.glossable` | its `offline_fallback` states the page ships every definition and the fetch enhancement is inert |
| duplicate registration refuses and mutates nothing | `check_duplicate_registration` | raises `CapabilityError` naming the duplicate; `profiles()` unchanged |
| the schema is accepted and validates all fifteen | `python schema_validate.py --all` and `check_schema_validates_every_profile` | `20 schema documents self-check clean`; no entry errored |
| a broken profile fails rather than passing quietly | `check_schema_refuses_broken_profiles` | four for four |
| an unavailable renderer shows its static path | `scenario_unavailable_renderer` | pass |
| the shipped bytes did not move | `tests/gate_roundtrip.py`, `tests/lesson_roundtrip.py` | exit 0 before and after |
| capabilities.py cannot reach a disclosure decision | `grep -c "open(" capabilities.py` and the evidence/runtime import grep | `0` and `0` |
| no decorative block is required | `scenario_capability_profiles`'s no-callouts leg | a zero-callout lesson produces no style or semantic finding |

## 10. Deviations from the plan, with reasons

Four.

**D1. The schema carries `$schema`, `$id`, `title`, `description`, and
`x-itembank-version`, which the plan forbade.** The plan's Task 2 step 1, its
`out_of_scope`, and one acceptance criterion all forbid these on the stated
ground that "`check_schema` walks the whole document and refuses any of them
outright". That is not what the shipped validator does.
`schema_validate.py:33-38` defines an `ANNOTATIONS` frozenset holding exactly
`$schema`, `$id`, `title`, `description`, `x-itembank-version`, `default`, and
`x-itembank-phase`, and `check_schema`'s keyword guard at `schema_validate.py:69`
reads `if kw not in SUPPORTED and kw not in ANNOTATIONS`. Those keywords are
accepted and ignored, by design and with a comment saying so.

The premise being false, the criterion built on it was not worth honoring at the
cost of the actual goal. All nineteen shipped schemas under `schemas/` carry the
same five-key annotation header; a twentieth without one would be the only
published contract in the tree that does not say what it is or where it lives.
`python schema_validate.py --all` reports `20 schema documents self-check clean`
with the header present, which is the direct evidence. The remaining forbidden
keywords, `default`, `examples`, `format`, and `anyOf`, are genuinely absent:
`examples`, `format`, and `anyOf` really would be refused, and `default` was not
wanted.

**D2. `capabilities.catalog_profile_name` and `_ROLE_PROFILE_NAMES` were added,
and the plan's artifact list does not name them.** Task 1's behavior block
requires that "for every entry in `SEMANTIC_ROLE_CATALOG` there is exactly one
profile that maps to it", and Task 3 step 4 requires the tracer to assert it.
Nothing in the plan says how a role finds its profile, and the two cannot be
derived from each other: `key idea` is rendered by `callout_key` and
`term and definition` by `glossary_definition`, and no naming rule connects
either pair. The alternatives were a sixth key on each catalog entry, which
would break plan 16A-03's asserted five-key set, or the same mapping written by
hand inside two test files, which is the drift this cross-check exists to
prevent. One module-level dict with one accessor is the smallest thing that
works.

**D3. `build.py`'s `STAGE_FILES` gained `capabilities.py`, and the plan does not
name `build.py`.** `surfaces/lesson.py` now imports `capabilities` at module
scope, and `build.py` stages an explicit allowlist rather than walking the tree.
Omitting it made `tests/packaging_roundtrip.py` and
`tests/math_offline_roundtrip.py` fail with
`ModuleNotFoundError: No module named 'capabilities'` raised from inside the
built `.pyz`. This is the identical class of gap `build.py`'s own 14C comment
records for `identity`, `journal`, and the course modules, and it was caught the
same way. The one-line addition carries a comment saying so.

**D4. `fixtures/lesson_capability_corpus.build_no_callouts` was added, and the
plan's artifact list names only `build_unavailable_capability`.** Task 3 step 5
requires the tracer to "build a minimal bank containing a `## LESSON` section,
one `### ` heading, and prose only, with zero callouts of any kind". Every other
corpus bank in this file is a named builder writing a module-level literal, and
constructing this one inline in the tracer would have been the only fixture in
the phase that does not live in the fixtures file.

## 11. Open items recorded rather than filled

- **`.capability-static` has no CSS rule.** Task 3 step 1's recorded handoff:
  an unstyled paragraph is legible, and Phase 17A owns how it looks. Adding a
  rule here would be a visual decision Phase 16A is not allowed to make. The
  class exists so 17A has a hook that already carries the meaning.
- **The `resolved_availability` lowering rules are this plan's own policy, not
  CAP-02's.** CAP-02 names the six fields and the Degraded clause and says
  nothing about which context fact lowers which capability. The seven rules live
  in `_lowered_by_context` with a comment saying so, and an unknown context key
  is ignored rather than refused, so a later phase supplying a sixth fact
  extends them additively.
- **The declared `renderer_availability` is a ceiling, never a floor.** All
  fifteen currently declare `available`; the vocabulary's other two members are
  reachable only through `resolved_availability`, or through a profile a later
  phase registers as `degraded` or `unavailable`. `scenario_unavailable_renderer`
  registers a synthetic `unavailable` capability precisely so the ceiling
  behavior is exercised by something rather than by nothing.
