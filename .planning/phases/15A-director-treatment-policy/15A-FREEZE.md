# Phase 15A freeze record

## Frozen at 15A

**Dated 2026-08-30.** All three freeze legs hold. The tracer was re-run in this
task rather than trusted from plan 15A-06 Task 1, because a review sits between
the two runs and a freeze record must describe the tree it freezes.

**How the second leg closed, stated first because it carries a condition.**
`15A-REVIEW.md` records `accept with concerns recorded`, written by Claude
under Weibao's instruction of 2026-08-30 to finish Phase 15A without him. Plan
15A-06 Task 2 is a blocking `checkpoint:human-verify` whose own text says "an
agent never signs it for itself". That requirement is **waived, not met**.

This is the fourth phase in a row to close a review leg this way, after 16A,
16B and 16C, and it is the heaviest of the four: those three asked whether
shipped copy reads honestly, and this one asks whether a course-design judgment
is any good. **Whoever relies on this freeze should read `15A-REVIEW.md`'s
Provenance section first**; striking that section reopens the leg.

The review was not a rubber stamp. It recorded six concerns and found one real
defect by reading the recommendations as prose: `apply_recommendation` was
binding the provider's own `coverage.state` into the sidecar, which is a model
certifying its own coverage. Fixed before this record was written.

## What is frozen

### director.py, the agent-client tier

The module contract, frozen as stated in its docstring: `director.py` drafts
and validates and never owns accepted truth; every durable write reaches disk
through `course.py` and therefore `journal.commit_operation`; every rights
decision reads the live registry at the moment of the operation. It does not
import `tier_gate`, `evidence`, `runtime`, or `model`, and their absence is
asserted by test rather than maintained by care.

**The closed vocabularies**, frozen by name and by exact membership:

| Constant | Members | Value |
|---|---|---|
| `director.PROTOCOL_STEPS` | 13 | `declare-intent`, `declare-authority`, `inventory`, `plan-treatment`, `checkpoint`, `draft`, `cite`, `validate`, `preview`, `diff`, `review`, `accept`, `report` |
| `director.AGENT_ENTRY_KEYS` | 10 | `operation_id`, `intent`, `actor_role`, `autonomy`, `scopes`, `phase`, `phase_index`, `checkpoint`, `proposal`, `egress` |
| `director.EGRESS_KEYS` | 7 | `destination`, `backend_class`, `profile`, `spans`, `omitted`, `payload_bytes`, `evidence_included` |
| `director.AUTONOMY_LEVELS` | 3 | `recommend-only`, `draft-and-review`, `approved-bounded-write`, in ascending authority order |
| `director.MATCH_KINDS` | 3 | `locator`, `heading-similarity`, `none` |
| `director.OMISSION_REASONS` | 4 | `rights-not-granted`, `span-cap`, `byte-cap`, `source-unreadable` |
| `director.PHASE_OUTCOMES` | 3 | `recorded`, `not-applicable`, `missing` |
| `director.PROTOCOL_VERDICTS` | 2 | `complete`, `incomplete` |
| `director.PROTOCOL_REPORT_KEYS` | 6 | `operation_id`, `steps`, `out_of_order`, `verdict`, `resumable`, `reason` |
| `director.RECOMMENDATION_KEYS` | 9 | `schema_version`, `objective_id`, `treatment_kind`, `rationale`, `synthesis`, `confidence`, `coverage`, `alternatives`, `citations` |
| `director.COVERAGE_CLAIM_KEYS` | 9 | `objective_id`, `source_object_id`, `locator`, `match_kind`, `confidence`, `assertion`, `span_chars`, `proposed_state`, `state` |
| `director.UNTREATED_REASONS` | 5 | `no-recommendation`, `backend-unavailable`, `rights-not-granted`, `reviewer-rejected`, `no-source-bound` |
| `director.RECOMMENDATION_OUTCOMES` | 3 | `bound`, `untreated`, `refused` |
| `director.EGRESS_DESTINATIONS` | 3 | `local`, `hosted`, `registered-local` |
| `director.PARITY_VOLATILE_KEYS` | 6 | `elapsed_ms`, `entry_id`, `interaction_id`, `operation_id`, `provider`, `timestamp` |
| `director.EVIDENCE_FIELDS` | 8 | `score`, `verdict`, `attempt_number`, `session_id`, `mark`, `response`, `canonical`, `note` |

`PROTOCOL_STEPS` is compared byte for byte: no case folding, no prefix
matching, no separator normalization, no synonym table. A fourteenth step is a
change to `.agents/skills/OPERATION-CONTRACT.md`, the shared contract every
client reads, and not a change to this module.

**The numeric constants**, frozen as values whose change is a decision about
egress rather than a tuning knob: `MAX_EGRESS_SPANS = 8`,
`MAX_EGRESS_BYTES = 16384`, `THIN_SPAN_CHARS = 240`,
`DIRECTOR_SCHEMA_VERSION = 1`.

`director.AGENT_POLICY_DEFAULTS` is
`{"autonomy_level": "recommend-only", "max_bindings_per_operation": 0}`.
Both grant nothing, so a fresh install writes nothing.
`director.RECOMMENDATION_SPAN_TREATMENT` is `direct-reading`, the vocabulary
member whose right is `read`. `director.TRANSPORT_DESTINATIONS` maps
`hosted_cli` to `hosted` and `openai_compatible` to `registered-local`; a
transport it does not name records `local`.

**`director.DIRECTOR_CODES`**, fifteen typed failures, frozen:
`already_recorded`, `autonomy_exceeded`, `backend_unavailable`,
`bind_cap_exceeded`, `duplicate_coverage_claim`, `duplicate_phase`,
`egress_unapproved`, `empty_treatment_bind`, `evidence_forbidden`,
`operation_unknown`, `recommendation_invalid`, `rights_not_granted`,
`unknown_match_kind`, `unknown_phase`, `unknown_treatment_kind`, each prefixed
`director.`.

**The public functions**, frozen at these signatures and these behaviors:
`new_operation_id`, `begin_operation`, `record_phase`, `operation_entries`,
`protocol_report`, `replay_operation`, `resume_point`, `reverse_operation`,
`locator_key`, `resolve_locator`, `coverage_claim`, `coverage_claims_for`,
`classify_coverage`, `parity_view`, `treatment_candidates`, `rank_candidates`,
`autonomy_level`, `max_bindings_per_operation`, `authorize_write`,
`approved_spans`, `egress_record`, `source_texts_for`,
`recommendation_request`, `validate_recommendation`, `recommend_once`,
`recommend_treatments`, `untreated_objectives`, `apply_recommendation`.

Three behaviors frozen because they are the phase's substance rather than its
shape:

- `replay_operation(base, operation_id)` takes exactly two parameters. There is
  no parameter through which an in-memory operation object could be passed, so
  a passing replay proves the journal is the durable job record rather than
  that a process remembered its own work.
- `apply_recommendation` takes no rights argument, and the coverage state it
  binds is computed by `classify_coverage`, never adopted from the record. No
  parameter exists through which a stale right or a self-certified coverage
  claim could authorize a write.
- `authorize_write` returns `None` on success. There is no value a caller could
  mistake for a granted authority, and an over-declaration is refused rather
  than narrowed.

`classify_coverage`'s six rules are frozen in that order, first match wins, and
the order is written into the docstring so a reorder makes the docstring wrong.
`covered` is reachable only by falling through all five earlier rules, which is
how TREAT-02's similarity rule is structural rather than maintained by care.

### schemas/treatment_recommendation.schema.json

Frozen at `x-itembank-version` 1. `additionalProperties: false`, nine required
properties matching `RECOMMENDATION_KEYS`, `treatment_kind` an enum of the
eleven `graph.TREATMENT_KINDS` tokens plus the empty string, `synthesis` a
`const true`, `confidence` the four-token enum, and `coverage` an object whose
`state` is the five `graph.BINDING_STATES` and whose `match_kind` is the three
`MATCH_KINDS`.

`synthesis` being a `const` is frozen as the mechanism, not just the value: a
provider cannot mark a rationale as quoted source text, because no value of the
field says so.

### The model_adapter extension

`schemas/model_adapter.schema.json`'s `operation` enum is frozen at
`["hint", "rubric_review", "author", "treatment_recommend"]`, in that order.
`model_adapter._PAYLOAD_KEYS` gains `recommendation_request` appended seventh,
so the six prior keys keep their positions and every request built before this
phase serializes to byte-identical JSON.

`treatment_recommend` is the one operation never routed through
`tier_gate.py`, and the schema description says so: it has no learner
disclosure boundary and is gated on source rights instead. A
`treatment_recommend` request with no `payload.recommendation_request` returns
`adapter.request_invalid` with the message
`treatment_recommend requires payload.recommendation_request`.

### The journal extension, exactly two lines

`journal.RECORD_TYPES` gains `agent_operation`, making eleven.
`journal.ENTRY_KEYS` gains `agent` as its twenty-fourth and last member, whose
value is a dict or null whose key set is owned by `director.AGENT_ENTRY_KEYS`,
following the `undo` key's dict-valued precedent.

`journal.OPERATION_TYPES` is unchanged at exactly six.
`agent_operation` is deliberately not among them: an agent operation is a
record of what an agent did, not an operation on a file. It is also not
undoable in `surfaces/visual_fixture.UNDOABLE`, because it writes no bytes of
its own and every durable write it causes is journalled separately with its own
undo.

### The settings policy

`schemas/settings.schema.json` gains one top-level property `agent_policy`,
`additionalProperties: false`, required `["autonomy_level",
"max_bindings_per_operation"]`, carrying `default`, `x-itembank-phase` 15, and
`description`. `autonomy_level` is the three-token enum defaulting to
`recommend-only`; `max_bindings_per_operation` is an integer in `[0, 50]`
defaulting to `0`.

The authority lives here and never on the operation. An agent that could report
its own authority could raise it, which is the self-expansion AGENT-02 forbids
by name.

## What is NOT frozen

**This is not the course schema freeze.** That is Phase 14B's, and 14B's own
freeze record states that it is not the course schema freeze either. Nothing in
15A freezes the sidecar's sections, its columns, or its record shapes.

**This is not a lesson-profile freeze.** 15A ships no lesson, no profile, and
no lesson capability.

**This is not an agent job protocol freeze.** The thirteen protocol steps are
frozen as a vocabulary this module compares against; how a long-running job is
scheduled, queued, retried, or surfaced is unowned by this phase.

**This is not a learner-facing surface freeze.** There is no CLI command, no
daemon route, and no rendered page. The `preview` protocol step is recorded
`not-applicable` for exactly that reason, and an agent never self-certifies
accessibility.

**The mock profiles and the fixture corpora are not frozen.** They are test
data: `fixtures/mock_backends.py`, the four synthetic subjects in
`fixtures/corpus_14b.py`, and every rights matrix they build. A later phase may
change any of them without reopening this freeze, provided the contracts above
still hold.

## Evidence

Re-run in this task on **Darwin 27.0.0 arm64, Python 3.14.6**.

**Leg 1, the tracer.** `python3 tests/four_subject_review.py`, final line
verbatim:

```
TRACER: 8 passed, 0 skipped, 0 failed
```

Exit 0. All eight scenario rows read `pass`; none reads `skipped`. The tracer
runs `shipped_suite_check()` before importing any 15A module, so a red shipped
suite or a missing 14A or 14B freeze would have skipped every scenario rather
than reporting passes.

**Leg 2, the review.** `15A-REVIEW.md`, verdict `accept with concerns
recorded`, signed "Claude, as an agent, under Weibao's explicit instruction of
2026-08-30 to finish Phase 15A without him. Not Weibao's own signature." Six
concerns, all carried below. Read that file's Provenance section before relying
on this freeze.

**Leg 3, Phase 13.9.** `.planning/phases/13.9-walking-skeleton/` contains
`13.9-01-SUMMARY.md`, `13.9-02-SUMMARY.md`, and `13.9-03-SUMMARY.md`. The
third records under `## A9 closure state` that all five A9 checkboxes are
`[x]`. ROADMAP.md's governance clause that no 14B-or-later freeze commits
before the skeleton has been walked is satisfied.

**The shipped runtime.** Full suite: **98 test files, 306 seconds, 0
failures**. `python3 itembank.py guard .` reports `0 offending files`.

## Measured, not promised

Every figure below was produced by the run that this record describes, on
**Darwin arm64, Python 3.14.6**, dated **2026-08-30**. No target, budget, or
estimate appears among them.

| Figure | Measured value |
|---|---|
| One full four-subject recommendation pass | 0.377 seconds |
| Whole tracer, eight scenarios | 17.769 seconds |
| Journal entries appended by the pass | 191 |
| Total payload bytes across the run | 16401 bytes |
| Largest single payload | 907 bytes |
| Spans approved for egress | 5 |
| Spans omitted with reasons | 1 |
| Objectives in the pass | 19 |
| Outcomes | 8 bound, 7 untreated, 4 refused |
| Protocol steps recorded | 12 of 13, the thirteenth `not-applicable` |
| Interruption points walked | 13 |
| Full suite | 98 files, 306 seconds, 0 failures |

The three outcome counts sum to 19, which equals the objective count, so no
objective was silently skipped.

## Open items carried forward

**From `15A-REVIEW.md`, six concerns:**

| # | Concern | Owner |
|---|---|---|
| 1 | Recommendation quality is untested by anything. The provider is a modulo rule, so the tracer proves the machinery is honest and proves nothing about whether a recommendation is good. The first run against a real model is an unproven step. | the phase that first points director at a real provider |
| 2 | `apply_recommendation` adopted the provider's `coverage.state`. **Fixed in this phase**, before this record: the state is now computed by `classify_coverage` and the provider's is kept as a proposal. | closed |
| 3 | `coverage_claims_for` cannot reach every coverage state: binding rows carry no `assertion` column, and `conflicting` is by definition two claims asserting different things. The four-subject bindings reach `thin` only. | the phase that gives a binding row somewhere to carry a claim |
| 4 | An untreated entry still carries a `treatment_kind`, so a row can read `untreated` and name a treatment at once. Accurate, and it reads badly. | the phase that renders this to a person |
| 5 | A locator that resolves against a heading classifies as a located match. Correct, and pointing at a heading is not pointing at a treatment. | a later coverage pass |
| 6 | The four-subject corpus is thin: nineteen objectives, one source each, all synthetic. It exercises every contract and stresses none. | 15B or later |

**From plan 15A-01, the flagged assumption:** AGENT-02's unclassified edge, the
question of what an agent may do with a capability the contract does not
name, is recorded as an assumption rather than resolved. Owner: a later agent
phase.

**Two backstop truths, carried rather than proven:**

- Plan 15A-03's locator-equality backstop: that exact string equality after NFC
  and line-ending normalization, with no case folding and no fuzzy matching
  anywhere in the comparison path, means no near-match can ever reach the
  covered branch. Proven for the paths the tests exercise; carried as a
  backstop because it is a claim about every path.
- Plan 15A-05's concurrency backstop: that two director operations against one
  course root never both write, and that an operation killed mid-write leaves
  either the old or the new valid state. The lock refusal and the thirteen
  interruption points are proven; the mid-write kill is inherited from 14A's
  own durability fixtures rather than re-proven here.

**One defect found and not fixed here, by design:** `journal.undo` raises a
bare `FileNotFoundError` when a before-image is missing, in a module whose
whole discipline is typed errors carrying codes. Plan 15A-05's acceptance
criteria forbid touching `journal.py`, so the test asserts the substantive
claim and names the defect in a comment. Owner: a journal maintenance pass.
