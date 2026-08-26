# 14B-02 summary: the full typed graph kernel

**Executed 2026-08-26.** The proven slice is widened into the whole kernel: the
closed edge vocabulary with its degrade path and five carried fields, structural
containment that accepts any local label, the deterministic outline with order
validation and a topological fallback, and the published sidecar schema.

## The `public_api()` list as it stands at the end of this plan

Plans 03 through 06 extend this deliberately, by editing the expected list in
`tests/graph_roundtrip.py` in the same commit that adds the function.

```
add_container, add_edge, add_objective, edge_key, is_rule_row, new_course,
new_record, outline_projection, parse_course, propose_order, public_api,
serialize_course, split_row, validate_edge, validate_order
```

Fifteen names. `public_api()` excludes imported module objects and exception
classes, so `GraphError` and `identity` do not appear. This list is the
structural guard that keeps a completion, mastery, or readiness computation
from appearing in `graph.py` without a plan edit, which is GRAPH-03's boundary.

## The three domains and their container labels

| Slug | Title | Container label | Objectives | Edges written |
|---|---|---|---|---|
| `meridian-field-response` | Meridian Field Response | `module` | 6 | 3 `prerequisite-of`, 1 `covers-objective` |
| `orrery-algebra` | Orrery Algebra | `week` plus one `fortnight` | 5 | 2 `prerequisite-of` (one deliberately violated by authored order), 1 `source-supports` |
| `lantern-computing` | Lantern Computing Foundations | `chapter` | 5 | 1 `treatment-of`, 1 unregistered `alternate-path` carrying an explicit `hard-gate` |

The invented `fortnight` label is the one that proves GRAPH-01's clause: a
course that calls its unit a fortnight needs no schema change, and the
published schema carries no `enum` on the container label to make that true in
the contract and not only in the code. Every name, title, and statement is
fictional; `itembank guard .` reports `0 offending files`.

Each domain also mints one real `kind="source"` object through the 14A path, so
its rights record is a recorded grant rather than a claim in a comment:
meridian's rights are all `unknown` (restrictive), orrery's `quote` is
`granted`, and lantern's `transform` is `granted` while its `package` is
`denied`. Plan 14B-03 binds against these.

## Whether the golden parse comparison needed adjustment

**No.** `fixtures/lesson_golden_phase3_parse.json` was compared with exactly the
comparison `tests/lesson_roundtrip.py:1114` already uses,
`json.dumps(qs, sort_keys=True)` against `golden["qs"]`, and it matched with no
adjustment of any kind. That is the expected result and the reason it is worth
asserting: this phase adds no branch to `model.py`, so a bank or lesson using no
graph block parses byte-identically after it. The additivity claim is an
assertion against a snapshot that predates the phase, not a promise in prose.
The lesson half of the golden (which needs a `source` basename normalization for
platform portability) was not compared here, because `tests/lesson_roundtrip.py`
already owns that assertion and duplicating it would be a second copy of a
check, not a second check.

## Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| A local label needs no schema change | `check_structure_and_outline`, nine labels including `fortnight`, `quarter`, `sprint` | all parse, round trip, and render |
| No enum restricts the label in the published contract | `python3 -c "... print('enum' in d['$defs']['container']['properties']['label'])"` | `False` |
| Structural order mints no prerequisite status | containers and objectives built with no `add_edge` call | `doc["edges"] == []` |
| The outline is byte-identical across runs and survives a round trip | two `outline_projection` calls, then one through serialize and parse | identical |
| An order violation never reorders the authored sequence | outline compared with the edge present and absent | identical |
| Reversing two authored `order` values moves exactly two lines | line-by-line diff of two outlines | 2 |
| An edge carries all five GRAPH-02 fields with non-blocking defaults | `validate_edge` on a bare record | `proposed`, `unknown`, `advisory`, `""` |
| An unknown type is kept and downgraded, never dropped | `alternate-path`, `""`, and a missing key | `recommended-before`, a dict every time |
| An unknown type can never hard-block | `alternate-path` with an explicit `hard-gate` | `override` reads `advisory`, `original_override` keeps `hard-gate` |
| The file records what the human wrote | round trip of a downgraded edge | `alternate-path` and `hard-gate` still in the bytes |
| A duplicate, self, or unknown-endpoint edge is refused by name | three `add_edge` calls | `graph.duplicate_edge`, `graph.self_edge`, `graph.unknown_objective`; one edge still recorded |
| Edges sharing only a source, or only a target, stay separate | two documents | `len(doc["edges"])` is 2 each |
| A cycle is named, never looped or truncated | `propose_order` over a three-node cycle | `graph.prerequisite_cycle` listing all three |
| A cyclic graph still projects its authored outline | `outline_projection` over `sidecar_text_with_cycle()` | renders, and `validate_order` warns |
| The proposed order is stable under a shuffled input | `propose_order` twice with the list shuffled between | identical |
| No Unicode normalization is applied | two accent compositions fingerprinted | two different fingerprints; `hasattr(graph, "unicodedata")` is `False` |
| The whole schema was checked, not half | `schema_validate.check_schema` | returns without raising |
| The published contract carries the frozen vocabulary | the `edge_type` enum | the four frozen names |
| The shipped parser is untouched and byte-identical | golden parse snapshot plus `git diff --name-only` | matches; no `model.py`, `runtime.py`, `evidence.py`, `journal.py`, or `identity.py` in the diff |
| No real content entered the repository | `python3 itembank.py guard .` | `0 offending files` |
| The anchor suites stay green | `tests/scoring_roundtrip.py`, `tests/lesson_roundtrip.py` | both exit 0 |

## Deviations from this plan, with reasons

1. **`python schema_validate.py` with no arguments exits 2, not 0.** The plan's
   Task 3 acceptance criterion names it as "the shipped self-check step", but
   the shipped self-check is `python schema_validate.py --all`, which exits 0
   and does validate this new schema along with every other one. The no-argument
   form prints usage and returns 2 by design (`schema_validate.py:289`). The
   test asserts `check_schema` directly and `--all` was run by hand; the plan
   text is what was wrong.
2. **`course.py` was edited, and it is not in this plan's `files_modified`.**
   One line: `migrate_stub` recorded `origin="imported-13.9"`, and the published
   schema puts an `enum` of `local` and `imported` on the objective `origin`
   property, exactly as the plan directs. A migrated document would therefore
   have failed its own published contract. Changing the written value was the
   smaller fix than widening a contract the plan specified.
3. **`parent`, `container`, and `source_object_id` carry the pattern
   `^([0-9a-f]{16})?$`, not `^[0-9a-f]{16}$`.** The plan says to put the
   sixteen-hex pattern on every id property, but these three are legitimately
   empty: a top-level container has no parent, an unplaced objective has no
   container, and a treatment binding names no source. The strict pattern would
   have made the empty case a schema violation. The intent, that a present id
   is a minted opaque id, is preserved.
4. **`validate_order` also appends one line naming a prerequisite cycle.** The
   plan describes it as one warning per violated edge. A cycle always produces
   at least one violation, so the cycle would have surfaced anyway, but as a
   bare ordering complaint that does not say the word cycle. Naming it is more
   honest and costs one line.
5. **The degraded authority `advisory` sits outside `EDGE_AUTHORITIES`.** This
   is what the plan specifies for an unknown edge type, and it is worth stating
   plainly rather than leaving to be discovered: a relation this build does not
   recognize is not making any of the three authority claims, so a distinct word
   is more honest than picking the least wrong member of a closed set it does
   not belong to. Recorded as `DEGRADED_AUTHORITY` with that reasoning in the
   source.
6. **The corpus's authored content is fixed but its object ids are not.** The
   plan asks for content generated from a fixed seed so a rebuild is
   byte-identical. Every authored string is fixed, and every id is minted with
   `identity.new_object_id()`, so two builds mint two different id sets. That is
   not a defect to fix: D-14A-2 requires a minted opaque id never derived from
   content, and a seeded id would violate it. Byte-identical holds for
   everything a human wrote, which is what the property is for.
7. **`outline_projection` now reads the authored `order` cell** rather than list
   position alone, with list position as the tie-break. Both are what the human
   wrote; the plan's assertion that reversing two `order` values moves exactly
   two outline lines requires the cell to be read.
8. **`_endpoint_ids` accepts a container id as an edge endpoint**, not only
   objectives and sources. The refusal message names objectives and sources
   because those are the endpoints this plan's edges use, but a
   `covers-objective` edge from a container is a shape plan 14B-03 will want and
   refusing it here would have been an invented restriction.

## Suite state

72 of 75 suites pass. The three failures are the same pre-existing,
Anki-environment-dependent ones recorded in `14B-01-SUMMARY.md`
(`day_roundtrip.py`, `retention_ui_roundtrip.py`, and `phase_062_audit.py`
which reports the first two): they assert the exact copy printed with Anki
closed, and Anki is running on this machine. No new failure was introduced.
