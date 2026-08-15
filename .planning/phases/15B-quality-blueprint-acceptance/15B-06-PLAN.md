---
phase: 15B-quality-blueprint-acceptance
plan: 06
type: execute
wave: 6
depends_on: ["15B-05"]
files_modified:
  - blueprint.py
  - schemas/evidence_proposal.schema.json
  - fixtures/corpus_15b.py
  - tests/blueprint_roundtrip.py
autonomous: true
requirements: [AGENT-03]
estimate:
  tokens: 72000
  raw_tokens: 72000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "Every evidence-based proposal names its observation window, its denominator, its included signals, its missing signals, its uncertainty, and its competing explanations; all six are required by schemas/evidence_proposal.schema.json and a record missing any one is refused before it is returned."
    - "Sparse evidence cannot produce a mastery percentage: no proposal record contains a float, and no key anywhere in a proposal record has a lowercase name containing mastery, completion, readiness, progress, percent, or score, proven by a recursive walk over the whole record rather than by inspecting the top level."
    - "An accepted next action remains a recommendation: the proposal record's status field is a schema const of the literal string recommendation, so no proposal record can assert that it acted, and the learner or the deterministic selection policy is the only thing that acts."
    - "The observation window is half-open: an event whose timestamp equals window.start is inside the denominator and an event whose timestamp equals window.end is outside it, and the record's own window block names the boundary rule in a required boundary field whose value is the const half-open."
    - "A proposal over zero events returns a record whose denominator is 0, whose uncertainty is no-evidence, whose claims list is empty, and which still names its window, its included signals, and its missing signals; it never returns None, never omits the denominator, and never raises."
    - "Objective identity for a denominator is compared as exact ASCII after NFC normalization and line-ending normalization, with no case folding, no stripping, and no prefix matching; blueprint.objective_key produces the same value as director.locator_key for every fixture string, asserted in the test rather than by importing director."
    - statement: "Whether every shipped evidence objective string round-trips to a 14B graph objective id without loss is proven only for the fixture objectives this phase builds, and is not proven for arbitrary shipped bank objective text; the evidence log keys events by objective text while the course graph keys objectives by opaque id, and nothing in this phase closes that join."
      verification: backstop
    - "The proposal's claims list is sorted by (objective_key, signal_kind, canonical_json(evidence)) and two runs over the same event rows produce byte-identical canonical_json renderings, so equal-comparing claims have a specified stable order."
    - "blueprint.py still imports no evidence module: the event rows arrive as an argument the caller read, following the precedent graph.objective_evidence_state set by taking a precomputed count rather than reading the store itself."
  prohibitions:
    - statement: "A mastery percentage, a readiness score, a completion rate, or a confident causal claim must not be minted from sparse evidence, and no proposal record may carry a number that a reader could take for one."
      status: kept
      verification: flagged-unverified
    - statement: "An accepted next action must not be treated as an action taken; a proposal remains a recommendation until the learner or the deterministic selection policy acts, and the record cannot say otherwise."
      status: kept
      verification: flagged-unverified
    - statement: "A denominator must not be reported without the window it was counted over, and a claim must not be reported without its denominator; a count with no window and no denominator is a number with no meaning."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "schemas/evidence_proposal.schema.json, x-itembank-version 1"
    - "blueprint.py gains PROPOSAL_SCHEMA_VERSION, PROPOSAL_SCHEMA_RESOURCE, PROPOSAL_KEYS, WINDOW_KEYS, CLAIM_KEYS, UNCERTAINTY_LEVELS, SPARSE_MAX, MODERATE_MAX, FORBIDDEN_PROPOSAL_SUBSTRINGS, objective_key, in_window, uncertainty_for, proposal_claim, and evidence_proposal"
    - "blueprint.BLUEPRINT_CODES gains three members: blueprint.proposal_invalid, blueprint.window_invalid, blueprint.forbidden_proposal_key"
    - "fixtures/corpus_15b.py gains build_sparse_evidence and build_dense_evidence"
    - "tests/blueprint_roundtrip.py gains check_evidence_proposal and check_proposal_edges"
  key_links:
    - "The event rows arrive as an argument. blueprint.py imports no evidence module and never will, which is what makes the evidence store read-only from this phase a property rather than a promise. graph.objective_evidence_state already set this precedent in 14B-04 by taking an event_count rather than reading the log, and this function extends it to rows so a window can be applied."
    - "The half-open window rule lives in three places that must agree: the const boundary field in the schema, the in_window helper, and the record's own window block. If the helper ever computed a closed interval while the record claimed half-open, the denominator would be off by the boundary events and nothing would notice, because a denominator has no independent check."
    - "The forbidden-key ban is a recursive walk over the finished record, not a check on the top-level keys. A nested evidence dict carrying a percent key would pass a shallow check and would be exactly the mastery claim AGENT-03 forbids, arriving one level down."
    - "objective_key must produce the same value as director.locator_key for every fixture string, asserted in the test by calling both. blueprint.py does not import director, so the two normalization rules could drift; the coupling test is what catches that, the same way a schema coupling test catches a schema drifting from its builder."
---

<objective>
Make an evidence-based proposal say what it does not know.

AGENT-03, quoted in full from `REQUIREMENTS.md`: "Evidence-based proposals name
their observation window, denominator, included and missing signals,
uncertainty, and competing explanations; sparse evidence cannot produce a
mastery percentage or a confident causal claim, and accepted next actions
remain recommendations until the learner or deterministic selection policy
acts. Owner: agent client. Durable object: proposal record. Authority: the
learner or selection policy acts, not the model. Degraded: sparse evidence
yields an explicitly uncertain recommendation."

Its Fixture sentence names the exact case: "a 15B proposal fixture over a
sparse synthetic evidence set of two attempts on one objective, asserting the
proposal names its window, denominator, and uncertainty and refuses a mastery
percentage."

Two attempts is the whole point. A model looking at two attempts can produce a
sentence that sounds like knowledge, and the honest record of two attempts is a
denominator of two, an uncertainty of sparse, a list of the signals that were
not there, and at least one competing explanation. This plan makes that record
the only shape a proposal can take.

Decisions already made, cited, and never re-derived here:

- **D-15B-1** in `15B-DECISIONS.md`: where this code lives. This plan is
  written against `option-a`, which puts `evidence_proposal` in `blueprint.py`
  as a pure function over supplied event rows.
- **15B-RESEARCH.md Phase Requirements table**, the AGENT-03 row: "a proposal
  record carries `window`, `denominator`, `missing_signals`, and `uncertainty`
  fields and never a `float` or a key named
  `mastery`/`completion`/`readiness`/`progress`/`percent`/`score`, following the
  exact recursive-walk test pattern `15A-02-PLAN.md` Task 3 already wrote for
  treatment recommendations."
- **15B-RESEARCH.md Architectural Responsibility Map**, the AGENT-03 row:
  "`evidence.py` is read, never written, by any function this phase adds".
- **14B-04-PLAN.md** `graph.objective_evidence_state(doc, objective_id,
  event_count)`, the precedent for taking a precomputed evidence value as an
  argument rather than reading the store.
- **15A-03-PLAN.md** `director.locator_key(text)`, whose rule is NFC and
  line-ending normalization with no case folding. `blueprint.objective_key`
  follows the same rule and the test asserts the two agree.
- **PLANNING-DIRECTIVES section 4** non-negotiable 1, quoted: "The **runtime
  owns assessment authority**: correctness, session state, evidence, and
  disclosure of keyed assessment content." A proposal reads aggregate rows a
  caller supplied and settles nothing.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| The window boundary rule | Half-open. An event at `window.start` is in; an event at `window.end` is out. The record carries a `boundary` field whose schema value is the const `"half-open"` | Two adjacent windows must partition rather than double count, which only a half-open interval does. Writing the rule into the record means a reader never has to guess which convention produced a denominator. |
| The uncertainty vocabulary and its bands | `("no-evidence", "sparse", "moderate", "sufficient")`, with denominator `0` reading `no-evidence`, `1` through `SPARSE_MAX` of `5` reading `sparse`, `6` through `MODERATE_MAX` of `19` reading `moderate`, and `20` or more reading `sufficient` | AGENT-03's own fixture is two attempts, which must read `sparse`. The bands are integer counts with named constants so a later change is one edit and is visible; they are deliberately not tuned to any statistical claim, because a tuned threshold would itself be a confidence claim. |
| Whether a proposal may carry a proportion | Never, in any form, at any nesting depth | AGENT-03 bans a mastery percentage, and a proportion is the shape a mastery percentage takes. The record carries integer counts with their denominators beside them. |
| How the recommendation-not-action rule is enforced | Structurally: the schema's `status` property is a `const` of the literal `"recommendation"`, so no record can assert anything else | A field a builder could set to `"acted"` would eventually be set to `"acted"`. A const cannot. |
| Whether the proposal reads the evidence log | Never. The caller supplies already-read event rows | Keeps `blueprint.py` free of an `evidence` import, which is what makes read-only structural, and matches `graph.objective_evidence_state`'s precedent exactly. |
| What a competing explanation must be | At least one non-empty string whenever `claims` is non-empty; `evidence_proposal` refuses a record with claims and no competing explanation | AGENT-03 lists competing explanations among the six things a proposal must name. A claim with no alternative reading is a confident causal claim by omission. |

Purpose: make the denominator and the doubt as visible as the recommendation.
Output: the proposal record, its schema, and the recursive ban that keeps a
number from becoming a claim.
</objective>

<context>
@.planning/phases/15B-quality-blueprint-acceptance/15B-RESEARCH.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-PATTERNS.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/REQUIREMENTS.md
@.planning/phases/15A-director-treatment-policy/15A-02-PLAN.md
@.planning/phases/15A-director-treatment-policy/15A-03-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md
@evidence.py
@blueprint.py
@schema_validate.py
</context>

## Artifacts this phase produces (plan 15B-06 share)

Added to `blueprint.py`. Every symbol below is new in this phase.

- Constants: `PROPOSAL_SCHEMA_VERSION = 1`,
  `PROPOSAL_SCHEMA_RESOURCE = "schemas/evidence_proposal.schema.json"`,
  `PROPOSAL_STATUS = "recommendation"`,
  `PROPOSAL_KEYS = ("schema_version", "status", "objective_key", "window",
  "denominator", "included_signals", "missing_signals", "uncertainty",
  "competing_explanations", "claims", "recommendations")`,
  `WINDOW_KEYS = ("start", "end", "boundary")`,
  `WINDOW_BOUNDARY = "half-open"`,
  `CLAIM_KEYS = ("objective_key", "signal_kind", "observed_count",
  "denominator", "evidence", "statement")`,
  `UNCERTAINTY_LEVELS = ("no-evidence", "sparse", "moderate", "sufficient")`,
  `SPARSE_MAX = 5`, `MODERATE_MAX = 19`,
  `FORBIDDEN_PROPOSAL_SUBSTRINGS = ("completion", "mastery", "percent",
  "progress", "readiness", "score")`.
- Functions: `objective_key(text)`, `in_window(timestamp, window)`,
  `uncertainty_for(denominator)`, `proposal_claim(...)`,
  `evidence_proposal(objective_key_value, window, event_rows,
  included_signals, missing_signals, competing_explanations,
  recommendations=None)`.
- `BLUEPRINT_CODES` gains three members: `blueprint.forbidden_proposal_key`,
  `blueprint.proposal_invalid`, `blueprint.window_invalid`. The tuple grows
  from twenty members to twenty-three and stays sorted.

New schema file: `schemas/evidence_proposal.schema.json`,
`x-itembank-version` `1`.

Added to `fixtures/corpus_15b.py`: `build_sparse_evidence(dest)` returning two
synthetic response rows on one objective, and `build_dense_evidence(dest)`
returning twenty-four rows across three objectives with two rows landing
exactly on the window boundaries.

New test functions in `tests/blueprint_roundtrip.py`:
`check_evidence_proposal()` and `check_proposal_edges()`.

No CLI command, no daemon route, and no journal record type is produced by this
plan. `blueprint.py`'s import list is unchanged and still contains no
`evidence`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the proposal record, its window, its denominator, and its uncertainty</name>
  <files>blueprint.py, schemas/evidence_proposal.schema.json, fixtures/corpus_15b.py, tests/blueprint_roundtrip.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md` AGENT-03 in full, including its Fixture sentence
  and its Degraded clause, both quoted in this plan's objective.
- `blueprint.py` in full as it stands after plan 15B-05: `BLUEPRINT_CODES`'s
  set-then-sorted construction, `canonical_json`, `validate_blueprint`'s schema
  loading, `classify_staleness`, `course_audit`, and the module docstring's
  structural-ban paragraph, which this task must not weaken.
- `evidence.py` lines 36 to 95 and `RESPONSE_EVENT_TYPE` at line 342,
  `KNOWN_EVENT_TYPES`, `SELECTION_EVENT_TYPE`, `GATE_SKIP_EVENT_TYPE`, and
  `subject_of`. Read them so the fixture's synthetic rows have the shape a real
  caller would hand in. This module is read for its shape and is not imported
  by `blueprint.py`.
- `.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md`, the
  `graph.objective_evidence_state(doc, objective_id, event_count)` signature,
  the precedent for taking a precomputed evidence value rather than reading the
  store.
- `.planning/phases/15A-director-treatment-policy/15A-03-PLAN.md`, the
  `director.locator_key(text)` rule: NFC and line-ending normalization with no
  case folding.
- `schemas/quality_finding.schema.json` and
  `schemas/course_audit_report.schema.json` as written by plan 15B-05, the
  envelope conventions this schema copies.
- `schema_validate.py` lines 27 to 38, the `SUPPORTED` and `ANNOTATIONS`
  keyword ceiling.
  </read_first>
  <behavior>
Assertions `check_evidence_proposal()` must make. Write them first and confirm
they fail before extending `blueprint.py`.

The six required namings are required by the schema, not by convention:

- `schemas/evidence_proposal.schema.json`'s top-level `required` array equals
  `list(blueprint.PROPOSAL_KEYS)`, member for member and in order, and includes
  every one of `window`, `denominator`, `included_signals`, `missing_signals`,
  `uncertainty`, and `competing_explanations`.
- `schema_validate.check_schema` on the document raises nothing.
- A record built with any one of the six removed fails
  `schema_validate.validate`, asserted by looping over the six and removing one
  at a time, so all six are proven required rather than one sampled.
- `evidence_proposal` validates its own output against the schema before
  returning and raises `BlueprintError` with code `blueprint.proposal_invalid`
  on a failure.

The window is half-open and says so:

- `blueprint.WINDOW_KEYS` equals `("start", "end", "boundary")` and
  `blueprint.WINDOW_BOUNDARY` equals `"half-open"`.
- The schema's `window.properties.boundary` is a `const` of `"half-open"`, so
  no record can claim a different convention.
- `blueprint.in_window(t, window)` is `True` when `t` equals `window["start"]`.
- `blueprint.in_window(t, window)` is `False` when `t` equals `window["end"]`.
- `in_window` is `True` strictly between and `False` strictly outside.
- Two adjacent windows sharing a boundary value partition a row set exactly:
  build twenty-four rows with two landing on the shared boundary, run
  `evidence_proposal` over each window, and assert the two denominators sum to
  the row count with no row counted twice and none dropped.
- A window whose `end` is less than its `start`, or which is missing any of
  `WINDOW_KEYS`, raises `BlueprintError` with code `blueprint.window_invalid`
  before any row is examined.

The denominator is a count and is always present:

- `evidence_proposal` over `build_sparse_evidence`'s two rows returns a record
  whose `denominator` is exactly `2`.
- The `denominator` value is an `int`, asserted by type rather than by value.
- Every claim in `claims` carries its own `denominator` equal to the record's,
  so a claim read alone still carries its denominator.
- Every claim carries an `observed_count` that is an `int` and never a ratio of
  the two.

The uncertainty is banded, named, and derived:

- `blueprint.UNCERTAINTY_LEVELS` equals `("no-evidence", "sparse", "moderate",
  "sufficient")`.
- `blueprint.uncertainty_for(0)` is `"no-evidence"`.
- `uncertainty_for(1)` and `uncertainty_for(5)` are both `"sparse"`, and
  `blueprint.SPARSE_MAX` is `5`.
- `uncertainty_for(6)` and `uncertainty_for(19)` are both `"moderate"`, and
  `blueprint.MODERATE_MAX` is `19`.
- `uncertainty_for(20)` and `uncertainty_for(2000)` are both `"sufficient"`.
- The AGENT-03 fixture case: `evidence_proposal` over two attempts on one
  objective returns a record whose `uncertainty` is exactly `"sparse"`.
- `uncertainty_for` raises `ValueError` for a negative denominator rather than
  returning a level.

A claim always has an alternative reading:

- `evidence_proposal` with a non-empty `claims` result and an empty
  `competing_explanations` argument raises `BlueprintError` with code
  `blueprint.proposal_invalid`, and the message states that a claim with no
  competing explanation is a confident causal claim by omission.
- `evidence_proposal` with zero rows and an empty `competing_explanations`
  succeeds, because there is no claim to explain away.

The recommendation stays a recommendation:

- `blueprint.PROPOSAL_STATUS` equals `"recommendation"`.
- The schema's `status` property is a `const` of `"recommendation"`.
- Every returned record's `status` is `"recommendation"`.
- `PROPOSAL_KEYS` contains no key named `acted`, `acted_on`, `applied`,
  `taken`, or `executed`, asserted directly, so the record has no place to
  claim an action.

The evidence store stays unreachable:

- `hasattr(blueprint, "evidence")` is still `False`.
- `blueprint.py`'s source contains no line matching `import evidence` outside a
  comment.
- `evidence_proposal`'s signature has no parameter named `log`, `log_path`,
  `base`, or `path`, asserted by inspecting the signature, so it cannot be
  handed a store to read.
  </behavior>
  <action>
1. Add `check_evidence_proposal()` to `tests/blueprint_roundtrip.py` with every
   assertion in `<behavior>`, wire it into `main()`, and run
   `python tests/blueprint_roundtrip.py` to confirm it fails.

2. Add `build_sparse_evidence(dest)` and `build_dense_evidence(dest)` to
   `fixtures/corpus_15b.py`. `build_sparse_evidence` returns exactly two
   synthetic response rows on one fictional objective, each a dict with the
   keys `timestamp`, `objective`, `signal_kind`, and `payload`, matching the
   shape a caller would build by reading `evidence.events`.
   `build_dense_evidence` returns twenty-four rows across three fictional
   objectives, with exactly two rows whose timestamps equal the shared boundary
   value the window partition assertion uses. Both are fixed-seed with no
   randomness and no clock read, so two calls return equal output. All content
   is fictional.

3. Create `schemas/evidence_proposal.schema.json` copying
   `schemas/course_audit_report.schema.json`'s envelope conventions exactly:
   `$schema`, `$id` of
   `https://itembank.local/schemas/evidence_proposal.schema.json`, `title` of
   `itembank evidence-based proposal`, a `description`, `x-itembank-version` of
   `1`, `type: object`, `additionalProperties: false`, and `required` equal to
   `PROPOSAL_KEYS` in that exact order. Its properties, exactly:
   - `schema_version`: const 1.
   - `status`: string, `const` `"recommendation"`, with the description
     `"A proposal is a recommendation. It stays one until the learner or the
     deterministic selection policy acts, and this const is what makes that
     structural rather than a convention: no record can assert that it acted."`
   - `objective_key`: string, `minLength` 1.
   - `window`: object, `additionalProperties: false`, `required`
     `["start", "end", "boundary"]`, with `start` and `end` strings `minLength`
     1 and `boundary` a string `const` `"half-open"` whose description states
     that an event at `start` is inside the denominator and an event at `end`
     is outside it, so two adjacent windows partition rather than double count.
   - `denominator`: integer, `minimum` 0, with the description `"The count of
     events inside the window. A claim without this number is a number with no
     meaning."`
   - `included_signals`: array of strings.
   - `missing_signals`: array of strings, with the description `"The signals
     that were not present. Naming what is absent is the difference between a
     small denominator and an unexplained one."`
   - `uncertainty`: string, `enum` equal to `UNCERTAINTY_LEVELS`.
   - `competing_explanations`: array of strings.
   - `claims`: array of `{"$ref": "#/$defs/claim"}`.
   - `recommendations`: array of strings.
   Add `$defs.claim`, `additionalProperties: false`, `required` equal to
   `CLAIM_KEYS` in that exact order, with `observed_count` and `denominator`
   integers `minimum` 0, `evidence` an object, and the rest strings.
   The top-level `description` states in plain sentences that this is the
   AGENT-03 proposal record, that sparse evidence cannot produce a mastery
   percentage so no property in this document is a float or a proportion, that
   every count carries its denominator, and that the record names what it does
   not know. Use no schema keyword outside `schema_validate.SUPPORTED` and
   `schema_validate.ANNOTATIONS`. The string `"number"` appears nowhere as a
   `type` value. No em dash characters.

4. Add to `blueprint.py` the eleven constants named in this plan's Artifacts
   section. Above `FORBIDDEN_PROPOSAL_SUBSTRINGS`, write a comment recording
   that AGENT-03 forbids a mastery percentage from sparse evidence, that the
   ban is enforced by a recursive walk over the finished record rather than by
   a top-level key check because a nested evidence dict carrying a `percent`
   key would pass a shallow check, and that the six substrings are compared
   against each key's `lower()` with no word-boundary matching so
   `mastery_pct` and `pct_score` are both caught.

5. Add the three new `BLUEPRINT_CODES` members, keeping the set-then-sorted
   construction so the tuple grows from twenty to twenty-three, with these
   exact message templates:
   - `blueprint.proposal_invalid`: `"the proposal record is not valid: %s; a
     proposal that does not name its window, denominator, missing signals,
     uncertainty, and competing explanations is not an evidence-based
     proposal"`
   - `blueprint.window_invalid`: `"the observation window is invalid: %s; a
     window needs a start, an end, and the half-open boundary rule, and its end
     is never before its start"`
   - `blueprint.forbidden_proposal_key`: `"the key %s at %s carries one of the
     forbidden substrings %s; sparse evidence cannot produce a mastery
     percentage, and a key that names one is refused before the record is
     returned"`

6. Implement `objective_key(text)` performing Unicode NFC normalization through
   `unicodedata.normalize("NFC", text)` and line-ending normalization of
   `\r\n` and `\r` to `\n`, with no case folding, no stripping, and no prefix
   matching. Add `import unicodedata` to `blueprint.py`; it is a standard
   library module and weakens no structural ban. Write a docstring stating that
   this rule is `director.locator_key`'s rule restated for objective identity,
   that the two are asserted to agree in the test rather than by import, and
   that the evidence log keys events by objective text while the course graph
   keys objectives by opaque id, so this function is the join and its
   limitations are recorded in the plan's flagged assumptions.

7. Implement `in_window(timestamp, window)` returning
   `window["start"] <= timestamp < window["end"]` as plain string comparison,
   after validating the window through a private helper that raises
   `blueprint.window_invalid` for a missing key or for an `end` less than a
   `start`. Implement `uncertainty_for(denominator)` returning the four bands
   by the constants, raising `ValueError` on a negative input.

8. Implement `proposal_claim(...)` returning the six-key dict, and
   `evidence_proposal(objective_key_value, window, event_rows,
   included_signals, missing_signals, competing_explanations,
   recommendations=None)`. It treats `None` for any list argument as `[]`,
   validates the window first, filters `event_rows` by `in_window` and by
   `objective_key` equality, counts the denominator, derives the uncertainty,
   builds one claim per distinct `signal_kind` present, refuses with
   `blueprint.proposal_invalid` when `claims` is non-empty and
   `competing_explanations` is empty, sorts `claims` by `(objective_key,
   signal_kind, canonical_json(evidence))`, validates the finished record
   against the schema, and returns it. It reads no file, no clock, and no
   settings.
  </action>
  <verify>
  <automated>python tests/blueprint_roundtrip.py && python schema_validate.py && python itembank.py guard .</automated>
Expected: `tests/blueprint_roundtrip.py` exits 0 with `check_evidence_proposal`
run, `schema_validate.py` reports no error, and `guard` prints
`0 offending files`. The degraded behavior this task must prove rather than
paper over is the sparse case AGENT-03's Fixture sentence names: two attempts
on one objective produce a record whose `denominator` is `2`, whose
`uncertainty` is `sparse`, whose `missing_signals` is non-empty, and whose
`competing_explanations` is non-empty. Confirm all four in the same record, and
confirm the record still validates, because an uncertain proposal is a valid
proposal and not an error.
  </verify>
  <acceptance_criteria>
- `python tests/blueprint_roundtrip.py` exits 0 with `check_evidence_proposal`
  run.
- `python -c "import blueprint as b; print(b.PROPOSAL_STATUS, b.WINDOW_BOUNDARY, b.UNCERTAINTY_LEVELS, b.SPARSE_MAX, b.MODERATE_MAX)"`
  prints `recommendation half-open ('no-evidence', 'sparse', 'moderate', 'sufficient') 5 19`.
- `python -c "import blueprint as b; print(b.uncertainty_for(0), b.uncertainty_for(2), b.uncertainty_for(5), b.uncertainty_for(6), b.uncertainty_for(20))"`
  prints `no-evidence sparse sparse moderate sufficient`.
- `python -c "import blueprint as b; w={'start':'a','end':'c','boundary':'half-open'}; print(b.in_window('a',w), b.in_window('b',w), b.in_window('c',w))"`
  prints `True True False`.
- `python -c "import json,blueprint,schema_validate; s=json.load(open('schemas/evidence_proposal.schema.json')); schema_validate.check_schema(s); print(s['required']==list(blueprint.PROPOSAL_KEYS), s['properties']['status']['const'], s['properties']['window']['properties']['boundary']['const'])"`
  prints `True recommendation half-open`.
- `python -c "import blueprint; print(len(blueprint.BLUEPRINT_CODES), blueprint.BLUEPRINT_CODES == tuple(sorted(blueprint.BLUEPRINT_CODES)))"`
  prints `23 True`.
- `python -c "import blueprint; print(hasattr(blueprint,'evidence'), hasattr(blueprint,'runtime'))"`
  prints `False True`.
- `grep -v '^#' blueprint.py | grep -c "^import evidence"` prints `0`.
- `python -c "import inspect,blueprint; p=inspect.signature(blueprint.evidence_proposal).parameters; print(any(n in p for n in ('log','log_path','base','path')))"`
  prints `False`.
- `python schema_validate.py` reports no error.
- `python itembank.py guard .` prints `0 offending files`.
- None of `blueprint.py`, `schemas/evidence_proposal.schema.json`,
  `fixtures/corpus_15b.py`, or `tests/blueprint_roundtrip.py` contains an em
  dash character.
  </acceptance_criteria>
  <precondition>Plan 15B-05 is green and `blueprint.BLUEPRINT_CODES` has twenty members.</precondition>
  <reversibility rating="costly">`PROPOSAL_KEYS`, `CLAIM_KEYS`, and
  `UNCERTAINTY_LEVELS` are consumed by the schema they must agree with and by
  plan 15B-07's tracer. Changing them before the 15B freeze costs one edit in
  each plus one fixture regeneration. `schemas/evidence_proposal.schema.json`
  becomes one-way once a proposal record has been stored by a later phase, but
  nothing in Phase 15B stores one, so the freeze is where that
  begins.</reversibility>
  <done>A proposal over two attempts names a denominator of two, an uncertainty
  of sparse, its missing signals, and a competing explanation, and the six
  namings AGENT-03 requires are enforced by a schema rather than by
  convention.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the recursive ban and the four AGENT-03 edges</name>
  <files>blueprint.py, fixtures/corpus_15b.py, tests/blueprint_roundtrip.py</files>
  <read_first>
- `blueprint.py` in full as it stands after Task 1, in particular
  `FORBIDDEN_PROPOSAL_SUBSTRINGS`, `evidence_proposal`, `objective_key`,
  `in_window`, and `canonical_json`.
- `.planning/phases/15A-director-treatment-policy/15A-02-PLAN.md` Task 3, the
  `check_recommendation_edges` recursive-walk pattern this task copies for a
  different record shape.
- `.planning/phases/15A-director-treatment-policy/15A-03-PLAN.md`, the
  `director.locator_key(text)` normalization rule, so the coupling assertion
  compares against the landed function rather than against this plan's
  paraphrase of it.
- `tests/blueprint_roundtrip.py` as it stands after Task 1, in particular
  `check_no_aggregate` from plan 15B-02, which this task extends rather than
  duplicates.
- `.planning/REQUIREMENTS.md` AGENT-03's clause "accepted next actions remain
  recommendations until the learner or deterministic selection policy acts".
  </read_first>
  <behavior>
Assertions `check_proposal_edges()` must make. Write them first and confirm
they fail before extending `blueprint.py`.

The recursive ban, on the finished record and one level down:

- `evidence_proposal` walks its finished record recursively through dicts,
  lists, and tuples and raises `BlueprintError` with code
  `blueprint.forbidden_proposal_key` when any key's `lower()` contains any
  member of `FORBIDDEN_PROPOSAL_SUBSTRINGS`.
- The refusal fires for a key at the top level, for a key inside a claim, and
  for a key inside a claim's nested `evidence` dict; assert all three depths,
  because a shallow check would pass the third.
- The refusal fires for `mastery_pct`, for `pct_score`, for `Progress`, and for
  `READINESS`, so matching is on the lowercased key with no word boundary and
  no case sensitivity.
- The refusal message names the offending key, its path, and the substring it
  matched.
- `evidence_proposal` raises rather than stripping the key. A silently removed
  field would leave a caller believing it was recorded.
- No `float` appears anywhere in any returned record, asserted by the same
  recursive walk. A caller passing a `float` in a claim's `evidence` raises
  `blueprint.proposal_invalid`.

Edge: adjacency, the window boundary:

- Two adjacent windows `[t0, t1)` and `[t1, t2)` over `build_dense_evidence`'s
  twenty-four rows produce denominators that sum to exactly the number of rows
  in `[t0, t2)`, with the two boundary rows counted exactly once, in the second
  window.
- A zero-width window where `start` equals `end` produces a denominator of `0`
  and an uncertainty of `no-evidence` rather than raising, because an empty
  window is a real question with an honest answer.

Edge: empty, single, and null:

- `evidence_proposal(key, window, [], [], [], [])` returns a record whose
  `denominator` is `0`, whose `uncertainty` is `"no-evidence"`, whose `claims`
  is `[]`, and which still carries its `window`, `included_signals`, and
  `missing_signals` keys.
- The same call returns a record rather than `None` and raises nothing.
- `evidence_proposal(key, window, None, None, None, None)` behaves identically
  to the empty-list call.
- A single event row produces a `denominator` of `1`, an `uncertainty` of
  `"sparse"`, and exactly one claim whose `observed_count` is `1` and whose
  `denominator` is `1`.

Edge: encoding, whose definition of equality:

- `blueprint.objective_key("café")` equals
  `blueprint.objective_key("café")`, because both normalize to NFC.
- `blueprint.objective_key("A\r\nB")` equals `blueprint.objective_key("A\nB")`.
- `blueprint.objective_key("Objective")` does NOT equal
  `blueprint.objective_key("objective")`. No case folding.
- `blueprint.objective_key(" x")` does NOT equal `blueprint.objective_key("x")`.
  No stripping.
- `blueprint.objective_key("obj-1")` does NOT match `"obj-10"` as a prefix in
  any filtering this function performs; a row whose objective is `"obj-10"` is
  excluded from a proposal keyed on `"obj-1"`, asserted with a real row pair.
- For every string in the fixture's objective set,
  `blueprint.objective_key(s)` equals `director.locator_key(s)`. The test
  imports `director`; `blueprint.py` does not. A divergence here is the
  coupling failure this assertion exists to catch.

Edge: ordering and stability:

- `claims` is sorted by `(objective_key, signal_kind, canonical_json(evidence))`.
- Two runs over the same `event_rows` produce records whose `canonical_json`
  renderings are byte identical.
- Shuffling `event_rows` does not change the returned record.
- Two claims equal on all three sort keys both appear and their relative order
  is reproducible across two runs.
- `included_signals`, `missing_signals`, `competing_explanations`, and
  `recommendations` are each returned sorted, so two callers passing the same
  set in different orders produce equal records.

The recommendation-not-action rule, asserted against a real attempt:

- Building a record and then setting its `status` to `"acted"` and
  re-validating it against the schema fails, because `status` is a `const`.
  Assert the validation failure directly, so the const is proven load-bearing
  rather than decorative.
  </behavior>
  <action>
1. Add `check_proposal_edges()` to `tests/blueprint_roundtrip.py` with every
   assertion in `<behavior>`, wire it into `main()`, and run
   `python tests/blueprint_roundtrip.py` to confirm it fails.

2. Implement the private recursive walk in `blueprint.py` as
   `_reject_forbidden_keys(obj, path)`, walking dicts, lists, and tuples,
   raising `BlueprintError` with code `blueprint.forbidden_proposal_key` on a
   matching key and with code `blueprint.proposal_invalid` on a `float` value.
   Call it from `evidence_proposal` immediately before the schema validation,
   so a forbidden key is refused with its own named code rather than as a
   generic schema failure.

3. Extend `evidence_proposal` to sort `included_signals`, `missing_signals`,
   `competing_explanations`, and `recommendations` before building the record,
   and to sort `claims` by the three-part key. Confirm the shuffle-invariance
   assertion passes.

4. Extend `build_dense_evidence(dest)` in `fixtures/corpus_15b.py` to return
   the two adjacent windows and the boundary value the partition assertion
   uses, plus an objective set containing the pair `"obj-1"` and `"obj-10"` for
   the prefix assertion and a Unicode pair for the NFC assertion. All content
   stays fictional and fixed-seed.

5. Extend `check_no_aggregate` in `tests/blueprint_roundtrip.py` so it is
   called on every proposal record this task builds, in addition to the
   findings lists and reports it already covers. Do not write a second walker;
   reuse the one plan 15B-02 created.

6. Add the `director.locator_key` coupling assertion to
   `check_proposal_edges()`, importing `director` in the test file only. Record
   in a comment beside it that `blueprint.py` deliberately does not import
   `director`, that the two normalization rules could therefore drift, and that
   this assertion is what catches the drift.

7. Run `python tests/blueprint_roundtrip.py`,
   `for t in tests/*.py; do python "$t" || exit 1; done`, and
   `python itembank.py guard .`, and confirm all three succeed.
  </action>
  <verify>
  <automated>python tests/blueprint_roundtrip.py && python itembank.py guard .</automated>
Expected: `tests/blueprint_roundtrip.py` exits 0 with `check_proposal_edges`
run, and `guard` prints `0 offending files`. The degraded behavior this task
must prove rather than paper over is the nested forbidden key: a `percent` key
inside a claim's own `evidence` dict, two levels down, raises
`blueprint.forbidden_proposal_key` naming its path rather than being silently
stripped or passing a shallow check. Confirm the code, the path in the message,
and that no record was returned.
  </verify>
  <acceptance_criteria>
- `python tests/blueprint_roundtrip.py` exits 0 with `check_proposal_edges`
  run.
- `python -c "import blueprint as b; print(b.FORBIDDEN_PROPOSAL_SUBSTRINGS)"`
  prints
  `('completion', 'mastery', 'percent', 'progress', 'readiness', 'score')`.
- `python -c "import blueprint as b; print(b.objective_key('café')==b.objective_key('café'), b.objective_key('A\r\nB')==b.objective_key('A\nB'), b.objective_key('X')==b.objective_key('x'), b.objective_key(' x')==b.objective_key('x'))"`
  prints `True True False False`.
- `python -c "import blueprint as b, director; s='Recognize a hazard'; print(b.objective_key(s)==director.locator_key(s))"`
  prints `True`.
- A record built with a `percent` key nested inside a claim's `evidence` dict
  raises `BlueprintError` with code `blueprint.forbidden_proposal_key`, and the
  message contains the path to the nested key.
- Setting a built record's `status` to `"acted"` and re-validating against
  `schemas/evidence_proposal.schema.json` fails validation.
- `check_no_aggregate` over every built proposal record finds no `float` and no
  key containing any of the six forbidden substrings.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files`.
- `git diff --name-only` after this task lists only `blueprint.py`,
  `fixtures/corpus_15b.py`, and `tests/blueprint_roundtrip.py`.
- None of the three changed files contains an em dash character.
  </acceptance_criteria>
  <precondition>Task 1 is green and `evidence_proposal` returns a schema-valid record.</precondition>
  <reversibility rating="reversible">The recursive walker, the sort keys, and
  the edge fixtures are internal to this phase and are consumed only by plan
  15B-07's tracer; changing any of them costs one edit.</reversibility>
  <done>A forbidden key is refused by name at any nesting depth, the window
  boundary partitions rather than double counts, the empty and single-row cases
  return honest records rather than raising, objective identity is normalized
  without being case folded or prefix matched, and a proposal cannot claim it
  acted.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| supplied event rows to a denominator | The caller reads the evidence store and hands rows in; a row set that does not match the window it claims produces a denominator that means nothing. |
| proposal record to reader | A number in a proposal is read as a claim about the learner; the record's shape is the only thing preventing it from being read as a mastery percentage. |
| proposal to next action | A recommendation that reads as an action would move authority from the learner to the model. |
| evidence store to this module | The store is read-only from this phase and structurally unreachable from `blueprint.py`. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15B-06-01 | Spoofing | a mastery percentage minted from sparse evidence | high | mitigate | The record carries no float and no key whose lowercase name contains any of six substrings, enforced by a recursive walk asserted at three nesting depths, and the schema declares no `number` type anywhere. |
| T-15B-06-02 | Spoofing | a confident causal claim with no alternative reading | high | mitigate | `evidence_proposal` refuses a record with non-empty `claims` and empty `competing_explanations` with `blueprint.proposal_invalid`, so an alternative reading is required rather than encouraged. |
| T-15B-06-03 | Elevation of Privilege | a proposal record asserting it acted | high | mitigate | The schema's `status` is a `const` of `"recommendation"`; the test sets the field to `"acted"` and asserts re-validation fails, so the const is proven load-bearing. `PROPOSAL_KEYS` also contains no `acted`, `applied`, `taken`, or `executed` key. |
| T-15B-06-04 | Tampering | the evidence store written or read directly by this module | high | mitigate | `blueprint.py` imports no `evidence`, asserted by `hasattr` and by a source scan, and `evidence_proposal`'s signature has no `log`, `log_path`, `base`, or `path` parameter, so it cannot be handed a store. |
| T-15B-06-05 | Tampering | a denominator that double counts or drops boundary events | high | mitigate | The window is half-open, the rule is a schema const, and the partition assertion over two adjacent windows proves the two denominators sum to the row count with the boundary rows counted exactly once. |
| T-15B-06-06 | Tampering | a denominator reported without its window | medium | mitigate | Both are top-level required properties, and every claim carries its own denominator so a claim read alone still carries it. |
| T-15B-06-07 | Spoofing | an objective join that silently over-matches | high | mitigate | `objective_key` performs NFC and line-ending normalization only, with no case folding, no stripping, and no prefix matching; the `obj-1` versus `obj-10` case is asserted with a real row pair. |
| T-15B-06-08 | Tampering | two normalization rules drifting apart | medium | mitigate | The test asserts `blueprint.objective_key` equals `director.locator_key` for every fixture string, importing `director` in the test only, which is the coupling check that catches a drift `blueprint.py`'s deliberate non-import would otherwise hide. |
| T-15B-06-09 | Repudiation | a forbidden key silently stripped rather than refused | medium | mitigate | The walker raises rather than removing, and the message names the key, its path, and the matched substring, so a caller learns the field was rejected rather than believing it was recorded. |
| T-15B-06-10 | Information Disclosure | real learner evidence entering the repository as a fixture | high | mitigate | `build_sparse_evidence` and `build_dense_evidence` build fictional fixed-seed rows and no real attempt, session, or learner value appears; `python itembank.py guard .` is in both tasks' acceptance criteria. |
| T-15B-06-11 | Tampering | supply chain: a statistics or datetime dependency added | high | mitigate | None is added; `unicodedata` is Python standard library, timestamps are compared as plain strings, and the bands are integer constants. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review. |
| T-15B-06-12 | Denial of Service | a very large event row set making the walk slow | low | accept | The filter and the walk are each one pass over the supplied rows. Accepted because the rows are repository-local and read by the caller, and a slow proposal is a loud local failure with no data at risk. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No read of `evidence.py`'s log, index, or any path. The rows arrive as an
  argument and `blueprint.py` imports no `evidence`.
- No write of any evidence event, of any kind, ever.
- No mastery, completion, readiness, progress, percentage, score, share, rate,
  or ratio value, at any nesting depth, under any name.
- No statistical claim, confidence interval, significance test, or trend line.
  The bands are named integer thresholds and the plan says explicitly that they
  are not tuned to a statistical claim, because a tuned threshold would itself
  be a confidence claim.
- No selection, scheduling, or next-item decision. `selection.py` and
  `retention.py` are the deterministic selection policy AGENT-03 names as the
  thing that acts, and this plan does not touch either.
- No durable storage of a proposal record. `evidence_proposal` returns a dict;
  whichever phase ships a surface decides where a proposal is written and
  through which write path.
- No journal record type and no journal entry. A proposal is not an operation.
- No CLI command and no daemon route.
- No import of `director` in `blueprint.py`. The `locator_key` agreement is a
  test-side assertion precisely so the module boundary holds.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped, per the spec-less probe fallback protocol. All
four AGENT-03 probe rows are resolved: adjacency is the half-open window
boundary, empty is the zero-row and single-row behavior, ordering is the
three-part sort key with proven shuffle invariance, and encoding is resolved as
a backstop rather than as an explicit criterion, recorded in this plan's
`must_haves.truths` with `verification: backstop` and repeated here.

- **The evidence-to-graph objective join is not proven (backstop, open).**
  `blueprint.objective_key` normalizes to NFC, normalizes line endings, folds
  no case, strips nothing, and matches no prefix, and it is asserted to agree
  with `director.locator_key` for every fixture string. What is not proven is
  that every shipped evidence objective string round-trips to a 14B graph
  objective id without loss: the evidence log keys events by objective TEXT
  taken from a bank's `OBJ:` field, while the course graph keys objectives by
  an opaque `identity.new_object_id` hex value. Nothing in this phase closes
  that join, and a caller building the `event_rows` argument is the one making
  it. This is carried into plan 15B-07's freeze record as an open item with the
  phase that first builds a real evidence-to-course join named as its owner.
- **The uncertainty bands are named, not derived (assumption, recorded).**
  `SPARSE_MAX` of `5` and `MODERATE_MAX` of `19` are chosen so that AGENT-03's
  two-attempt fixture reads `sparse` and so that the bands are legible. They
  are deliberately not tuned to any statistical criterion, because a tuned
  threshold would itself be a confidence claim of the sort this requirement
  forbids. Recorded so a later reader does not mistake them for a derived
  result.
</flagged_assumptions>

<summary_obligations>
`15B-06-SUMMARY.md` records: which truth was verified by which command, with
the command's actual stdout; the exact `BLUEPRINT_CODES` tuple after this
plan's three additions, so plan 15B-07's freeze record can enumerate the final
twenty-three; the sparse-case record in full, quoted, showing its denominator,
uncertainty, missing signals, and competing explanations; the
`director.locator_key` coupling assertion's result; the measured wall-clock
time of one full `tests/blueprint_roundtrip.py` run; whether the
evidence-to-graph join backstop is still open; and any deviation from this plan
with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15B-quality-blueprint-acceptance/15B-06-SUMMARY.md`
when done.
</output>
