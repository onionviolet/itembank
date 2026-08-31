# Phase 15B freeze record

## Frozen at 15B

**Dated 2026-08-30.** All three freeze legs hold. The evidence was re-run in
this task rather than trusted from plan 15B-07 Task 1, because a review sits
between the two runs and a freeze record must describe the tree it freezes.

**How the second leg closed, stated first because it carries a condition.**
`15B-REVIEW.md` records `accept with concerns recorded`, written by Claude
under Weibao's instruction of 2026-08-30 to finish Phase 15B without him. Plan
15B-07 Task 2's own prohibition reads "An agent must not sign its own
acceptance-quality review". That prohibition is **waived, not met**.

**This is the fifth phase in a row to close a review leg this way**, after 16A,
16B, 16C and 15A. Phase 15B additionally had an agent answer four one-way
checkpoint decisions, one of which amended another phase's frozen record.
**Whoever relies on this freeze should read `15B-REVIEW.md`'s Provenance
section first**; striking that section reopens the leg.

The review was not a rubber stamp. It recorded seven concerns, three of them
found by reading the refusal and finding copy as prose rather than as
assertions, and it recorded that this phase's self-checks are weakest exactly
where they check the phase's own judgement.

## What is frozen

### blueprint.py, the pure classifier

The module contract, frozen as stated in its docstring: `blueprint.py` imports
`model` and `runtime` and nothing else from this repository. It cannot write,
because it does not import `journal` or `course`; it cannot read the evidence
store, because it does not import `evidence`; and it cannot authorize anything,
because it does not import `director`. Each is asserted by the absence of the
attribute rather than by a reviewer's care.

**The closed vocabularies**, frozen by name and exact membership:

| Constant | Members | Value |
|---|---|---|
| `BLUEPRINT_FIELDS` | 8 | `construct`, `domain_weight`, `demand`, `format`, `difficulty`, `timing`, `tools`, `feedback_conditions`, in ACTIVITY-02's own order |
| `GATE_STEPS` | 5 | `parser`, `lint`, `review`, `blueprint`, `runtime`, in the order they run |
| `WARN_CODES` | 2 | `blueprint.absent`, `blueprint.unverifiable` |
| `SET_FACT_KEYS` | 2 | `construct`, `feedback_conditions` |
| `ITEM_FACT_KEYS` | 3 | `demand`, `timing_seconds`, `tools` |
| `GATE_RESULT_KEYS` | 3 | `step`, `passed`, `findings` |
| `STALENESS_DISPOSITIONS` | 4 | `rebind`, `migrate`, `supersede`, `retain`, transcribed from RELIABILITY-03 in the requirement's own order |
| `STALENESS_ROW_KEYS` | 7 | `object_id`, `object_kind`, `dependency_object_id`, `dependency_kind`, `base_fingerprint`, `current_fingerprint`, `stale` |
| `DISPOSITION_KEYS` | 9 | `schema_version`, `object_id`, `dependency_object_id`, `disposition`, `reviewer_role`, `reviewer_name`, `rationale`, `base_fingerprint`, `current_fingerprint` |
| `COVERAGE_VOCABULARIES` | 3 | `graph.BINDING_STATES`, `auditor.coverage_report`, `audit_report.coverage_row`, which are NAMES and not states |
| `AUDIT_ROW_KEYS` | 10 | `objective_id`, `vocabulary`, `state`, `source_object_id`, `treatment_kind`, `quality_codes`, `blueprint_codes`, `base_fingerprint`, `current_fingerprint`, `stale` |
| `AUDIT_REPORT_KEYS` | 10 | `schema_version`, `status`, `course_object_id`, `course_fingerprint`, `tool_version`, `stale`, `stale_inputs`, `vocabularies_cited`, `rows`, `counts` |
| `UNCERTAINTY_LEVELS` | 4 | `no-evidence`, `sparse`, `moderate`, `sufficient` |
| `WINDOW_KEYS` | 3 | `start`, `end`, `boundary` |
| `PROPOSAL_KEYS` | 10 | `schema_version`, `status`, `objective_key`, `window`, `denominator`, `included_signals`, `missing_signals`, `uncertainty`, `competing_explanations`, `claims` |
| `CLAIM_KEYS` | 5 | `objective_key`, `signal_kind`, `observed_count`, `denominator`, `evidence` |
| `FORBIDDEN_PROPOSAL_SUBSTRINGS` | 6 | `mastery`, `completion`, `readiness`, `progress`, `percent`, `score` |

**`BLUEPRINT_CODES`, twenty-four typed codes**, frozen and sorted. Note for a
later reader: the plan set says thirteen, and each of plans 15B-02 through
15B-06 counted from the thirteen it inherited rather than from what landed.
**This record is the authority for that number**, and the divergence is
recorded in `blueprint.py` above the tuple and as concern 6 in the review.

**The numeric constants**, frozen as values whose change is a decision about
what the course claims rather than a tuning knob: `THIN_SPAN_CHARS = 240`,
`SPARSE_MAX = 5`, `MODERATE_MAX = 19`, `BLUEPRINT_SCHEMA_VERSION = 1`,
`PROPOSAL_SCHEMA_VERSION = 1`.

**Three constants frozen as constants rather than conventions**:
`WINDOW_BOUNDARY = "half-open"`, `PROPOSAL_STATUS = "recommendation"`, and
`AUDIT_STATUS = "course_audit"`. The first two are schema `const` values too,
so no record can claim a different window convention and no record can assert
that it acted.

### The four behaviors that are the phase's substance

- **The exam-fidelity claim is False until all five gates report.**
  `fidelity_claim` reads gate results and never the questions, the blueprint,
  or the proposal, so it cannot disagree with the report that recorded them. A
  missing gate is a False claim and not a partial one.
- **An absent blueprint or an unsupplied fact is `warn`.** ACTIVITY-02's
  degraded clause says the course presents practice WITHOUT the claim, so both
  withhold the claim and neither withholds the activity.
- **A stale dependent is BLOCKED and never rebuilt.** RELIABILITY-03's degraded
  clause reads "blocked from acceptance until reconciled", not "rebuilt and
  accepted". No function in this phase rebuilds, regenerates, or refreshes a
  stale derivative, asserted by a source scan.
- **An absent fingerprint reads STALE.** An unprovable freshness is not
  freshness, and reading unknown as fresh is the failure-open direction.
  Comparison is exact ASCII with no case folding: a false stale costs a
  reviewer one look, a false fresh costs the guarantee.

### The three published schemas

`schemas/blueprint.schema.json`, `schemas/course_audit_report.schema.json`, and
`schemas/evidence_proposal.schema.json`, each at `x-itembank-version` 1, each
`additionalProperties: false` throughout, and **none carrying a float type
anywhere**. Every share and tolerance is an integer percentage point and every
duration an integer of seconds, because a float reintroduces the comparison
ambiguity the inclusive-tolerance rule exists to settle.

The proposal schema requires all six of AGENT-03's namings, so the requirement
is enforced by the contract rather than by the producing function remembering
it. The audit schema's `required` array equals `AUDIT_REPORT_KEYS` member for
member and in order, so an addition to one that misses the other fails a test.

### The additive report growth

`schemas/audit_report.schema.json` gains one optional `gates.blueprint_findings`
array and one `$defs.blueprint_finding_ref`. Its `gates.required` array is
**unchanged** at `lint_errors`, `lint_warnings`, `quality_findings`, so a
proposal built before Phase 15B validates exactly as it did before. The change
is 21 insertions and 0 deletions.

`authoring.build_proposal` gains `blueprint_findings` appended last with a
default of `None`, so a caller written before this phase still builds a valid
proposal.

### The sidecar and the migration review columns

`graph.SECTION_ORDER` gains `"Blueprint"` before `"Log"`, and
`graph.OPTIONAL_SECTIONS` makes it emit only when populated, so a pre-15B
sidecar carrying no blueprint serializes byte-identically. Proven against
`fixtures/golden_sidecar_pre_15b.md`, captured BEFORE the change.

The `Migrations` section gains two columns, `reviewer` and `rationale_review`.
The review rationale is a SEPARATE column from the proposal's own `rationale`:
the reason a change was proposed and the reason it was granted are two
different statements. A pre-15B sidecar round-trips with exactly four diff
lines, all in the Migrations table's header, no data row and no other section
touched. `14B-FREEZE.md` carries the dated amendment.

### The acceptance path

`graph.accept_migration` and `graph.reject_migration` are the **only two** paths
that settle a proposal. `graph.set_migration_state` stays and still refuses, so
the count of ways to settle went from zero to two rather than becoming
unbounded, and the tracer asserts the refusal in the same run as the two new
paths succeed.

Frozen refusals: `graph.migration_unknown`, `graph.migration_already_settled`
(a settled proposal is settled in either direction), `graph.migration_self_accept`
(the actor that proposed a revision is never the actor that grants it, and no
autonomy setting makes it so), and `graph.empty_rationale`, reusing 14B's code
rather than minting a second. Every refusal fires before any field is written.

Acceptance is **not idempotent**: an acceptance is an event, and a second one
means two reviewers each believe they granted it.

`director.accept_revision` runs three checks in a fixed order that carries
meaning: **staleness, then authority, then the write.** Reordering them would
let one failure mask the other and the journal would record the wrong reason,
which is worse than recording none. It takes no autonomy argument and reads
none off the proposal, and it declares the WRITE level rather than the granted
one, so the check can actually refuse.

Every outcome is journaled, refusals included. A refusal nobody recorded is
indistinguishable from a revision nobody proposed.

### The journal, exactly one line

`journal.RECORD_TYPES` gains `accept_revision`, making thirteen.
`journal.OPERATION_TYPES` is unchanged at exactly six, and `ENTRY_KEYS` at
exactly twenty-four. `accept_revision` is a record of a decision, not a file
operation, and is deliberately not undoable in
`surfaces/visual_fixture.UNDOABLE`.

## What is NOT frozen

Transcribed from `ROADMAP.md`:

> the 15B freeze covers the blueprint, audit, acceptance, staleness, and
> proposal-discipline surfaces only. It is explicitly not the course schema
> freeze, not a lesson-profile grammar freeze, not an agent job protocol
> freeze, and not a learner-facing surface freeze, and its freeze record says
> so.

**Phase 14B owns the course schema.** 15B amended `14B-FREEZE.md` to add one
sidecar section and two migration columns, additively and with the amendment
dated and recorded; that does not make this the course schema freeze, and 14B's
own record says it is not that freeze either.

**No lesson-profile grammar freeze.** 15B ships no lesson and no profile.

**No agent job protocol freeze.** The thirteen protocol steps are 15A's, and
how a long-running job is scheduled or retried is unowned here.

**No learner-facing surface freeze.** There is no CLI command and no daemon
route in Phase 15B, which is why the review judged copy from printed records
rather than from a rendered page.

**The fixtures are not frozen.** `fixtures/corpus_15b.py`, the mock backend,
and the synthetic Beacon blueprint are test data. A later phase may change any
of them without reopening this freeze, provided the contracts above hold.

## Evidence

Re-run in this task on **Darwin 27.0.0 arm64, Python 3.14.6**.

**Leg 1, the tracer.** `python3 tests/acceptance_tracer.py`, final line
verbatim:

```
TRACER: 7 passed, 0 skipped, 0 failed
```

Exit 0. All seven scenario rows read `pass`; none reads `skipped`.
`shipped_suite_check()` ran first, before any 15B module was imported: six
shipped suites each exited 0, and all three of `14A-FREEZE.md`,
`14B-FREEZE.md` and `15A-FREEZE.md` carry their frozen heading and none of the
three carries a withholding heading. (Spelled out rather than quoted: a
downstream precondition greps these files for the two literal headings, and
writing the withholding one inside prose in a record that IS frozen would make
this file answer that grep wrongly.)

**Leg 2, the review.** `15B-REVIEW.md`, verdict `accept with concerns
recorded`, signed "Claude, as an agent, under Weibao's explicit instruction of
2026-08-30 to finish without him. Not Weibao's own signature." Seven concerns,
all carried below.

**Leg 3, Phase 13.9.** `.planning/phases/13.9-walking-skeleton/` contains
`13.9-01-SUMMARY.md`, `13.9-02-SUMMARY.md` and `13.9-03-SUMMARY.md`, and the
third records all five A9 checkboxes closed. ROADMAP's governance clause that
no 14B-or-later freeze commits before the skeleton has been walked is
satisfied.

**The shipped runtime.** Full suite: **100 test files, 884 seconds, 0
failures**. `python3 itembank.py guard .` reports `0 offending files`. Skill
mirrors identical.

## Measured, not promised

Every figure below was produced by the run this record describes, on **Darwin
arm64, Python 3.14.6**, dated **2026-08-30**. No target or estimate appears
among them.

| Figure | Measured value |
|---|---|
| Whole tracer, seven scenarios | 31.947 seconds |
| Journal entries the run appended | 28 |
| `agent_operation` entries replayed from a fresh process | 6 |
| Gates passed on the conforming set | 5 of 5 |
| Gate arrays in the proposal | 4 |
| Staleness dispositions that cleared a block | 4 of 4, `retain` included |
| Migration settlements | 2, one accepted and one rejected |
| Course audit rows | 4, citing 2 vocabularies |
| Proposal denominator | 2 |
| Proposal uncertainty | `sparse` |
| Full suite | 100 files, 884 seconds, 0 failures |

## Open items carried forward

**From `15B-REVIEW.md`, seven concerns:**

| # | Concern | Owner |
|---|---|---|
| 1 | A staleness refusal names its dependency by opaque id only, so a reviewer cannot tell which source moved without a lookup | the phase that first renders a refusal to a human |
| 2 | The refusal lists four dispositions and offers no basis for choosing; the four are not interchangeable and a wrong one is a recorded decision that is hard to see was wrong | the same phase, and the more consequential of the two |
| 3 | The refusal states the system's policy rather than this operation's outcome; it never says THIS acceptance wrote nothing | a copy pass |
| 4 | Nothing can tell a real competing explanation from a restatement. The schema can require the list be non-empty and cannot require it be useful | the human review that reads a real proposal |
| 5 | The tracer's conforming set was written by the same agent that wrote the gate, and two of its items failed shipped Phase 11 detectors the agent did not anticipate | recorded as evidence, no owner |
| 6 | `BLUEPRINT_CODES` grew 13 to 24 across four plans and each plan counted from the thirteen it inherited; the plan set is wrong in four places | a plan-text correction, or this record as the authority |
| 7 | The evidence-to-graph join is open: the evidence log keys by objective text and the graph keys by opaque id, and nothing here closes it | a later phase, carried as a backstop since 15B-06 |

**Two defects found and fixed during this phase**, recorded so a reader does
not go looking:

- `director.accept_revision` authorized the policy level against itself, so the
  authority check could never refuse. It declares the write level now.
- The packaged `.pyz` was broken: `authoring.py` imports `blueprint` at module
  scope and `build.py`'s explicit stage list omitted it. Fixed, and
  `director.py` plus 16C's five modules were staged alongside as latent gaps of
  the same class that `build.py`'s own comments record twice before.

**One backstop truth, carried rather than proven:** that every shipped bank
objective string round-trips to a 14B graph objective id without loss. This
phase proves it for its own fixture strings only.
