# Phase 14B tracer report

Written 2026-08-27 by plan 14B-06 Task 4, on Darwin arm64, Python 3.14.6.
This is the evidence the freeze gate was judged against. The verdict itself
is in `14B-FREEZE.md`, and it is a withheld freeze: two of the three legs are
green and the third has no human sign-off.

## The three legs

### Leg one: the three-domain graph tracer. Green.

`python3 tests/three_domain_tracer.py`, exit code 0. Full output, verbatim:

```
authorability one cell hand edit: 1 line changed, reordering reached the projection, longest sidecar line 126 characters
scenario three_domain_outline: pass
scenario edge_vocabulary: pass
scenario migration: pass
scenario clean_restore: pass
scenario authorability_roundtrip: pass
budget build_all: 0.006 s (measured on this machine, recorded not promised)
budget outline_projection_three_domains: 0.001 s (measured on this machine, recorded not promised)
budget export_package: 0.001 s (measured on this machine, recorded not promised)
budget restore_package: 0.001 s (measured on this machine, recorded not promised)
platform: Darwin arm64
TRACER: 5 passed, 0 skipped, 0 failed
```

The final line is `TRACER: 5 passed, 0 skipped, 0 failed`.

Before its first scenario the tracer ran its own precondition,
`shipped_suite_check()`, over `tests/graph_roundtrip.py`,
`tests/course_package_roundtrip.py`, `tests/scoring_roundtrip.py`,
`tests/evidence_roundtrip.py`, and `tests/lesson_roundtrip.py`. All five
exited 0. A tracer that runs against a red suite proves nothing, so a single
non-zero exit there stops the run by name instead.

### Leg two: the clean restore drill. Green.

Run inside `scenario_clean_restore()` and reproduced here with the same
corpus so the figures can be quoted:

```
entries_verified: 2 of 2 complete: True
losses:
  external-link | linked, not imported; the external file keeps its own identity and location and is not copied into a package
  machine-local | not included by design; model backend configuration, update policy, and local paths belong to the machine, not to the course
  rights-restricted | the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged
  unreachable-source | the recorded root was unavailable when this package was built; the object is named here rather than omitted silently
restore_losses: []
evidence_recorded: 0 already: 0
```

Both loss lists are returned and neither replaces the other: `losses` is the
export-time report carried in the manifest, and `restore_losses` is what the
restore itself could not carry, which on this corpus is nothing. The
destination started empty, shared no journal, and had `HOME`, `APPDATA`, and
`XDG_DATA_HOME` redirected to a second empty directory for the duration, so
the restore could not quietly read the exporting machine's state. The
restored sidecar is byte-identical to the original, and every payload was
re-fingerprinted from the bytes on disk rather than read back from the
manifest's own claim.

The `rights-restricted` row is worth reading twice: the domain's own source
was left at its default rights, all seven `unknown`, so that row is a genuine
restrictive default rather than a denial written to make the assertion pass.

### Leg three: the authorability review. NOT green.

`.planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md`
Sign-off section, verbatim:

```
**Date:**

**Verdict (write exactly `authorable` or exactly `not authorable`):**

**Notes:**
```

It is blank. The machine half of this leg is green and is quoted in the
review file: one hand-edited `order` cell produces a one-line diff, the
reordering reaches the re-projected outline, and the sidecar's longest line
is 126 characters against a 200-character ceiling. The human half has not
been performed. `OPERATION-CONTRACT.md` states that an agent never
self-certifies this class of judgment, so no agent may close this leg, and
this report does not.

This is the first of two grounds on which the freeze is withheld. The
second is in Supporting runs below: the full suite is not green, and one of
its four red suites was caused by this phase.

## The four Fixture sentences

Every one is an executable scenario function, and every one passed.

| Requirement | Fixture sentence, from `REQUIREMENTS.md` | Scenario function | Result |
|---|---|---|---|
| GRAPH-01 | "the 14B three-domain graph tracer, a synthetic course graph spanning three fictional domains with structural containers labeled module, week, and chapter, asserting the outline projection reads in plain Markdown and structural order mints no prerequisite edge" | `scenario_three_domain_outline()` | pass |
| GRAPH-02 | "the 14B three-domain graph tracer extended with one edge of every registered type plus one deliberately unknown edge type, asserting the unknown type renders as an advisory recommended-before and never a hard block" | `scenario_edge_vocabulary()` | pass |
| GRAPH-04 | "a 14B three-domain graph tracer scenario that splits one synthetic objective and renames another, asserting a reviewed migration proposal is generated and unmigrated evidence reads unknown on the new identity" | `scenario_migration()` | pass |
| PORT-03 | "the 14B clean restore drill, exporting a synthetic course and restoring it on a clean offline machine against its manifest, asserting every loss is reported" | `scenario_clean_restore()` | pass |

GRAPH-01's corpus carries a fourth container label, `fortnight`, which no
tuple in `graph.py` restricts, because a course that calls its unit a
fortnight is not wrong and finding out would cost a release.

## Measured, not promised

```
budget build_all: 0.006 s (measured on this machine, recorded not promised)
budget outline_projection_three_domains: 0.001 s (measured on this machine, recorded not promised)
budget export_package: 0.001 s (measured on this machine, recorded not promised)
budget restore_package: 0.001 s (measured on this machine, recorded not promised)
```

These are single measurements taken once on one machine, on a corpus of
three small synthetic domains. They are not budgets, and no later phase may
assert against them. `measure_budgets()` makes no assertion of its own, by
design: `14B-RESEARCH.md` open question 3 recommends no performance budget
for this gate, and D-12.6-10's 100k-file corpus was routed to Phase 14A and
deferred there with its reason recorded.

For scale rather than for promise: the tracer's own wall clock is 16.31 s,
almost all of which is `shipped_suite_check()` running five suites as
subprocesses before the first scenario.

## Platform fallbacks

None fired. The tracer printed zero `SKIP:` lines, and its final line reports
`0 skipped`.

The platform: Darwin arm64. Both capabilities the tracer probes for were
available on this machine, measured rather than assumed by
`fixtures.corpus_14b.platform_capabilities()`:

| Capability | Available here | What a fallback would have done |
|---|---|---|
| Filesystem symbolic link creation | yes | `SKIP: filesystem symlink creation` printed and counted separately from the passes |
| Symbolic link entry inside a zip | yes | `SKIP: archive symlink entry refusal` printed, and the `package.symlink_payload` assertion not run |

A different platform may print those lines. They are skips, not passes, and
the final line counts them apart from the passes for exactly that reason.

## The nine probe-surfaced edges

Nine edge cases were surfaced by the deterministic edge probe over the four
requirement texts at plan time. Eight were authored as truths across plans 01
through 05. One, GRAPH-04's "changed demand", was flagged rather than
resolved, and is carried in plan 14B-04's own out-of-scope section.

A caveat about this table, recorded rather than glossed: no single enumerated
probe list survives in the phase's artifacts, so the eight authored rows below
were reconstructed at report time from the requirement clauses and the plan
tasks that implement them. The reconstruction is the reason the ninth row is
worth checking against `14B-04-PLAN.md` directly, which states it in full.

| # | Requirement | Edge case | Where it landed |
|---|---|---|---|
| 1 | GRAPH-01 | A local container label the schema has never seen must be accepted without a schema change | Authored: 14B-02 Task 2, asserted by `check_structure_and_outline()` and by the `fortnight` label in the tracer corpus |
| 2 | GRAPH-01 | Structural order must never imply prerequisite status | Authored: 14B-02 Task 2, and asserted again in `scenario_three_domain_outline()` against a freshly built document |
| 3 | GRAPH-01 | An imported scope is immutable; a local edit is an overlay record with its own identity and a migration relation | Authored: 14B-03 Task 2, asserted by `check_bindings_and_rights()` and `check_overlays()` |
| 4 | GRAPH-01 | Degraded clause: with no graph, the authored outline projection still reads in plain Markdown | Authored: 14B-01 Task 3, the empty-course and single-objective projections in `check_thin_slice()` |
| 5 | GRAPH-02 | Degraded clause: an unknown edge type renders as an advisory recommended-before, never dropped and never a hard block | Authored: 14B-02 Task 1, asserted by `check_edges()` and by `scenario_edge_vocabulary()`, including a `hard-gate` cell written into the file by hand |
| 6 | GRAPH-02 | Hard gates are exceptional and alignment never implies evidence transfer | Authored: 14B-02 Task 1, enforced structurally: `hard-gate` is never a default, is unreachable by degradation, and `graph.py` imports no evidence module |
| 7 | GRAPH-04 | Degraded clause: unmigrated evidence stays on the original objective identity and reads unknown for the new one | Authored: 14B-04 Task 3, asserted by `check_migration()` and by `scenario_migration()` |
| 8 | PORT-03 | Degraded clause: a restore gap is reported against the manifest, never silently accepted | Authored: 14B-05 Tasks 2 and 3, asserted by `check_manifest_and_losses()`, `check_clean_restore()`, and `scenario_clean_restore()` |
| 9 | GRAPH-04 | "Changed demand" as a migration trigger: no artifact read while planning this phase defines a demand vocabulary or what values demand can take | **Flagged, not resolved.** `14B-04-PLAN.md` "Flagged assumption carried forward, not silently dropped". `demand-change` is carried as one of the five `MIGRATION_KINDS` and no demand vocabulary was invented |

**Nine surfaced, eight authored, one flagged, zero dropped.**

**The flagged row's disposition, left open on purpose.** The reviewer's
question is whether GRAPH-04's "changed demand" requires a typed demand field
on the objective record in Phase 14B, or whether demand is a Phase 16A
capability-contract concept that 14B is correct to leave untyped. This report
does not close it, for two reasons. It is a scope judgment rather than a
measurement, and the freeze it would inform is withheld anyway. It stays
flagged for whoever re-runs Task 4 after the authorability sign-off lands.

## Requirement status

GRAPH-01, GRAPH-02, GRAPH-04, and PORT-03 all remain `Pending` in
`.planning/REQUIREMENTS.md`. Plan 14B-06 Task 4 step 5 permits moving them to
`Complete` only when step 4 wrote a `## Frozen at 14B` section, and it did
not. Every automated assertion behind those four requirements is green; what
is missing is the human leg of the gate, and a status table is not the place
to round that up.

## Supporting runs

| Command | Result |
|---|---|
| `python3 tests/three_domain_tracer.py` | exit 0, `TRACER: 5 passed, 0 skipped, 0 failed` |
| `python3 tests/graph_roundtrip.py` | exit 0, 0.09 s |
| `python3 tests/course_package_roundtrip.py` | exit 0, 0.12 s |
| `python3 schema_validate.py --all` | exit 0, `18 schema documents self-check clean` |
| `python3 itembank.py guard .` | exit 0, `0 offending files` |
| every `tests/*.py` run individually | **73 of 77 exit 0. Four are red.** |

The plan predicted this last command would exit 0. Measured on 2026-08-27, it
does not, and one of the four reds is this phase's own. Both facts are
recorded here rather than filtered out of a count.

### The four red suites, by cause

| Suite | Cause | This phase's? |
|---|---|---|
| `tests/day_roundtrip.py` | `day --check with Anki closed did not print the exact locked copy`. A live Anki is answering AnkiConnect on this machine, so the assertion's precondition is false rather than its subject being broken | No. Environmental, pre-existing |
| `tests/retention_ui_roundtrip.py` | `Anki closed must render the exact locked copy on Today`. Same live-Anki cause | No. Environmental, pre-existing |
| `tests/visual_system_roundtrip.py` | `journal record type migrate has no learner-facing phrase`, in `check_harness_undo_classification` | **Yes. Caused by this phase** |
| `tests/phase_062_audit.py` | `full suite not green`, listing the three above | Cascade of the three above |

### The regression this phase introduced, named rather than absorbed

`tests/visual_system_roundtrip.py` asserts that every member of
`journal.RECORD_TYPES` has a learner-facing phrase in
`surfaces/visual_fixture.OPERATION_PHRASE`. Commit `5568138`
(`feat(14B-04): migrate as a record type, and the reviewed migration
proposal`) added `migrate` as the eleventh record type under D-14B-3, and no
matching phrase was added, so:

```
RECORD_TYPES: ('link', 'import', 'copy', 'move', 'edit_in_place', 'supersede', 'mint', 'restore', 'external_edit', 'reconcile', 'migrate')
PHRASE keys: ['copy', 'edit_in_place', 'external_edit', 'import', 'link', 'mint', 'move', 'reconcile', 'restore', 'supersede']
missing: ['migrate']
```

The decision that put `migrate` in `RECORD_TYPES` is sound and is not being
reopened: D-14B-3 chose it precisely so that `journal.replay` can reconstruct
a migration and so that `OPERATION_TYPES` stays at the six names
`14A-FREEZE.md` froze. What is missing is one line of learner-facing copy for
the eleventh record type, which is a `surfaces/` change.

Plan 14B-06 fixes it in neither direction: its out-of-scope section refuses
any change under `surfaces/`, and the phrase is copy a human should choose
rather than an executor should invent. It is named here, it is a second
independent ground for the withheld freeze in `14B-FREEZE.md`, and it is one
line of work for whoever closes the gate.
