---
phase: 15A-director-treatment-policy
plan: 04
type: execute
wave: 4
depends_on: ["15A-03"]
files_modified:
  - director.py
  - schemas/settings.schema.json
  - itembank.json
  - tests/config_roundtrip.py
  - tests/director_roundtrip.py
  - fixtures/corpus_14b.py
autonomous: true
requirements: [RIGHTS-02, AGENT-02]
estimate:
  tokens: 66000
  raw_tokens: 66000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "An agent receives only approved source spans: director.approved_spans returns spans drawn exclusively from sources whose required right reads granted in the live registry at the moment of the call, and a source whose right is unknown or denied contributes zero spans no matter what any binding row, recommendation record, or prior egress record says about it."
    - "Egress is disclosed exactly, never approximately: the recorded egress lists every span actually sent with its source object id, its locator, and its byte count, plus every span omitted with the named reason, and the recorded payload_bytes equals the byte length of the JSON request that model_adapter.invoke was actually handed."
    - "Presentation visibility is never authorization: a source displayed in the course outline, named in a binding row, or carrying a rights_snapshot of granted contributes zero spans once its live registry right reads denied, proven by revoking the right after a successful run and re-running the same call."
    - "Autonomy is enforced policy-side and never self-reported: an operation declaring an autonomy level above settings.agent_policy.autonomy_level is refused with director.autonomy_exceeded naming both levels, and is never silently narrowed to the permitted level."
    - "No reachable backend keeps all core work local and model-free: with every registered profile unreachable, the recorded egress destination is local, the spans list is empty, no request leaves the process, and the shipped scoring, evidence, and session suites still pass."
    - "RIGHTS-02 adjacency edge: a span sent twice within one operation appears exactly once in the egress record, and two operations never share one egress record; the spans list is deduplicated by the source object id and normalized locator pair, and the omitted list carries no member that also appears in spans."
    - "RIGHTS-02 empty edge: an operation that sends nothing records an egress dict whose destination is local, whose spans and omitted lists are both empty, and whose payload_bytes is zero. The egress field is never absent and never null on a recorded agent operation."
    - "RIGHTS-02 ordering edge: the egress record's spans and omitted lists are each sorted by the source object id then the normalized locator, so two runs of one operation produce byte-comparable egress records and a diff of two journals shows a real difference rather than a reordering."
  prohibitions:
    - statement: "An egress record must not summarize, approximate, round, or elide what was sent; a count, a phrase such as the objective text, or a truncated list in place of the exact span identifiers and byte counts is a false disclosure."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "director.py gains approved_spans, egress_record, autonomy_level, authorize_write, MAX_EGRESS_SPANS, MAX_EGRESS_BYTES, and OMISSION_REASONS"
    - "schemas/settings.schema.json gains the agent_policy block with autonomy_level and max_bindings_per_operation"
    - "itembank.json gains the agent_policy block"
    - "tests/config_roundtrip.py's expected top-level key set gains agent_policy"
    - "tests/director_roundtrip.py gains check_approved_spans, check_autonomy_policy, and check_egress_record"
    - "fixtures/corpus_14b.py gains build_rights_matrix_fixture"
  key_links:
    - "tests/config_roundtrip.py::test_schema_names_every_project_key holds a hardcoded expected top-level key set and additionally requires every top-level property to carry default, x-itembank-phase, and description annotations. Adding agent_policy to the schema without adding it to that set and without all three annotations turns a shipped test red for a reason that looks unrelated to this phase."
    - "director.approved_spans must resolve the required right through graph.treatment_right and read the CURRENT registry through course.rights_for_binding on every call. If it accepts a rights value as a parameter, or caches a registry read across calls, a revoked right stays effective for the life of the process, which is Pitfall 2 in 15A-RESEARCH.md."
    - "The autonomy level the agent declares is an input to be checked, never the value used. authorize_write compares the declared level against settings.agent_policy.autonomy_level and refuses on excess; if it ever takes the minimum of the two instead, an agent that over-declares silently gets the policy level and the refusal that would have surfaced the over-declaration never happens."
---

<objective>
Make the two things RIGHTS-02 asks for true and checkable: an agent receives
only approved source spans, and what left this machine is disclosed exactly.
Then make AGENT-02's anti-self-expansion clause enforceable by moving the
autonomy level from prose into a settings-side policy that the agent cannot
raise for itself.

The defect this closes is the gap `15A-RESEARCH.md` names in plain words:
"No shipped or planned module owns 'what left the machine and to whom' today.
This is 15A's one genuinely new durable object." A recommendation system that
cannot say exactly what it sent is a system whose privacy posture is a promise
rather than a record.

Decisions already made, cited, and never re-derived here:

- **REQUIREMENTS.md RIGHTS-02**, quoted: "Hosted operations minimize and
  disclose exact egress, agents receive only approved source spans and
  operation authority, and presentation visibility is never authorization...
  Degraded: no reachable backend keeps all core work local and model-free.
  Fixture: a 15A recommendation-review run against a mock hosted backend,
  asserting the egress log lists exactly the approved synthetic source spans
  and that an unreachable backend leaves all core work local and model-free."
- **REQUIREMENTS.md AGENT-02**, quoted: an agent "may recommend,
  draft-and-review, or perform approved bounded writes but never self-expand
  scope, self-certify accessibility, silently accept its own uncertain source
  claim, transfer evidence, or cross runtime disclosure."
- **OPERATION-CONTRACT.md step 11**, quoted: "Recommend-only,
  draft-and-review, or approved bounded writes: the granted autonomy level
  decides who accepts." This plan makes the granted level a recorded policy
  rather than a prose sentence.
- **15A-RESEARCH.md Open Question 2**, recommendation: enforce the autonomy
  level course-side or policy-side, never self-reported, consistent with
  AGENT-02's explicit ban on an agent that can self-expand scope.
- **15A-01 Task 3 (D-15A-2)**: where the egress record lives was settled at a
  blocking checkpoint. This plan implements whichever option was recorded and
  reads `15A-DECISIONS.md` to find out which.
- **PLANNING-DIRECTIVES section 4** non-negotiable 3: evidence and banks stay
  on disk, no telemetry.

Decisions this plan makes and locks, so the executor never guesses:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Where the autonomy policy is stored | `settings.agent_policy.autonomy_level` in `itembank.json`, one place, read by `director.autonomy_level(settings)` | A per-course field would need a new sidecar header column and a 14B schema edit; a settings block is the mechanism this project already uses for every policy of this shape, and one storage location cannot disagree with itself. A per-course override is named out of scope here so a later phase adds it deliberately. |
| What happens when an agent over-declares | Refused with `director.autonomy_exceeded` naming both levels; never narrowed | Narrowing hides the over-declaration. A refusal makes the attempt visible, which is the point of AGENT-02's clause. |
| Default autonomy level | `recommend-only`, with `max_bindings_per_operation` defaulting to `0` | Unknown rights stay restrictive is this project's standing posture; the same posture applies to unknown authority. A fresh install grants nothing. |
| Egress caps | `MAX_EGRESS_SPANS = 8` and `MAX_EGRESS_BYTES = 16384` per operation | Minimization needs a number to be checkable. A dropped span is named in the `omitted` list with its reason, never truncated mid-span, so the cap is disclosed rather than silent. |
| Span dedupe key | `(source_object_id, director.locator_key(locator))` | The same normalization the coverage classifier already uses, so a span and a coverage claim can never disagree about whether two locators are the same one. |
| Sort order | Both lists sorted by `(source_object_id, locator_key(locator))` ascending | Byte-comparable egress records are what make plan 15A-06's backend-parity assertion mean something. |

Purpose: turn egress from a promise into a record, and authority from prose
into a check.
Output: the approved-span gate, the egress record, the settings policy block,
and the refusal that surfaces an over-declaring agent.
</objective>

<context>
@.planning/phases/15A-director-treatment-policy/15A-RESEARCH.md
@.planning/phases/15A-director-treatment-policy/15A-PATTERNS.md
@.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md
@.planning/phases/15A-director-treatment-policy/15A-03-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-03-PLAN.md
@.agents/skills/OPERATION-CONTRACT.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@schemas/settings.schema.json
</context>

## Artifacts this phase produces (plan 15A-04 share)

Added to `director.py`. Every symbol below is new in this phase.

- Constants: `MAX_EGRESS_SPANS = 8`, `MAX_EGRESS_BYTES = 16384`,
  `OMISSION_REASONS = ("rights-not-granted", "span-cap", "byte-cap",
  "source-unreadable")`,
  `AUTONOMY_LEVELS = ("recommend-only", "draft-and-review",
  "approved-bounded-write")`,
  `AGENT_POLICY_DEFAULTS = {"autonomy_level": "recommend-only",
  "max_bindings_per_operation": 0}`.
- Functions: `approved_spans(...)`, `egress_record(...)`,
  `autonomy_level(settings)`, `authorize_write(...)`.
- New `DirectorError` codes: `director.autonomy_exceeded`,
  `director.egress_unapproved`, `director.bind_cap_exceeded`.

Added to `schemas/settings.schema.json`: one new top-level property
`agent_policy`, an object with `additionalProperties: false`, `required`
`["autonomy_level", "max_bindings_per_operation"]`, its own `default`,
`x-itembank-phase`, and `description` annotations, and two leaf properties each
carrying a `default`, an `x-itembank-phase`, and a `description`.

Added to `itembank.json`: the `agent_policy` object with the schema's default
values.

Added to `tests/config_roundtrip.py`: the string `"agent_policy"` in the
`expected` set inside `test_schema_names_every_project_key`, and a new
`test_agent_policy_enum_and_default()` following the shape of the existing
`test_suggestion_reveal_enum_and_default`.

Added to `fixtures/corpus_14b.py`: `build_rights_matrix_fixture(dest)`
returning a course root whose four sources carry, respectively, all seven
rights granted, only `read` granted, only `transform` granted, and all seven
`unknown`.

New test functions in `tests/director_roundtrip.py`:
`check_approved_spans()`, `check_autonomy_policy()`, `check_egress_record()`.

No CLI command, no daemon route, and no journal record type is produced by this
plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the approved-span gate and its live rights read</name>
  <files>director.py, fixtures/corpus_14b.py, tests/director_roundtrip.py</files>
  <read_first>
- `director.py` as it stands after plan 15A-03, in full: `DIRECTOR_CODES`,
  `EGRESS_KEYS`, `locator_key`, `recommendation_request`,
  `apply_recommendation`, and the module docstring's live-rights sentence.
- `identity.py` as landed: `rights_state`, `rights_granted`, `RIGHTS_STATES`,
  `RIGHTS_OPERATIONS`. Note that `rights_granted` returns True only for the
  exact ASCII string `granted`, with no case folding.
- `course.py` as landed: `rights_for_binding`, which reads the CURRENT registry
  and returns a state string while making no decision.
- `graph.py` as landed: `TREATMENT_RIGHTS`, `treatment_right`,
  `SOURCE_BINDING_RIGHT`.
- `14B-03-PLAN.md`, the "No stale snapshot ever authorizes (Pitfall 5)"
  behavior block in full. This task extends that discipline from the bind call
  to the span assembly that happens before it.
- `fixtures/corpus_14b.py` as it stands after plan 15A-03, especially
  `revoke_right` and the fixed-seed rule.
- `tests/director_roundtrip.py` as it stands after plan 15A-03.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_approved_spans()` function, written before the code.

The rights matrix, four sources, one call:

- `fixtures.corpus_14b.build_rights_matrix_fixture(dest)` builds a course root
  with four registered sources whose rights are, in order: all seven granted;
  only `read` granted; only `transform` granted; all seven `unknown`.
- `director.approved_spans(base, doc, objective_id, treatment_kind,
  source_texts)` for `treatment_kind` `"guided-lesson"`, which consumes
  `transform`, returns spans only from the first and third sources. The second
  and fourth contribute zero spans.
- The same call for `treatment_kind` `"direct-reading"`, which consumes `read`,
  returns spans only from the first and second sources.
- The same call for `treatment_kind` `"excerpt"`, which consumes `quote`,
  returns spans only from the first source.
- Every source that contributed zero spans appears in the returned omission
  list with reason `rights-not-granted`, naming the source object id and the
  right it lacked. A refused source is disclosed, never silently absent.

The read is live, and nothing else authorizes:

- After a successful call, revoke `transform` on the first source with
  `fixtures.corpus_14b.revoke_right`, then repeat the identical call. The first
  source now contributes zero spans and appears in the omission list with
  reason `rights-not-granted`.
- The revocation takes effect even though the source's existing `## Bindings`
  row still carries a `rights_snapshot` of `granted`, and even though the same
  process already read `granted` for it once. Neither the snapshot nor a prior
  read authorizes.
- `director.approved_spans` accepts no rights argument: introspecting its
  signature finds no parameter whose name contains the string `rights`.
- Setting a source's right to the exact string `Granted` with a capital letter
  contributes zero spans, because `identity.rights_granted` matches only the
  exact lowercase token.

Caps and omissions:

- With twelve eligible spans available, the returned spans list has exactly
  `director.MAX_EGRESS_SPANS` members and the omission list carries the other
  four with reason `span-cap`.
- With three eligible spans whose combined byte length exceeds
  `director.MAX_EGRESS_BYTES`, spans are included in sorted order until the
  next one would exceed the cap, and every excluded span appears in the
  omission list with reason `byte-cap`. No span is ever included partially: the
  byte length of every returned span equals the byte length of its full text.
- A source id absent from `source_texts` appears in the omission list with
  reason `source-unreadable` and contributes zero spans, raising nothing.
- Every reason in the omission list is a member of
  `director.OMISSION_REASONS`.
- No source object id appears in both the spans list and the omission list.

Dedupe, ordering, and empty:

- Two eligible spans with the same `source_object_id` and locators that differ
  only by trailing carriage returns produce exactly one span, because the
  dedupe key uses `director.locator_key`.
- Two eligible spans with the same source and locators differing by letter case
  produce two spans, because `locator_key` does not case-fold.
- The returned spans list is sorted by `(source_object_id, locator_key(locator))`
  ascending, and so is the omission list. Two calls return identical lists.
- An objective with zero source bindings returns an empty spans list and an
  empty omission list, raising nothing.
  </behavior>
  <action>
1. Add `check_approved_spans()` to `tests/director_roundtrip.py` first, wired
   into `main()`, with every assertion above. Run
   `python tests/director_roundtrip.py` and confirm it fails.

2. Add to `director.py` the constants `MAX_EGRESS_SPANS = 8`,
   `MAX_EGRESS_BYTES = 16384`, and
   `OMISSION_REASONS = ("rights-not-granted", "span-cap", "byte-cap",
   "source-unreadable")`. Give the two caps a comment stating that minimization
   needs a number to be checkable, that a dropped span is named in the omission
   list rather than truncated, and that raising either number widens what
   leaves this machine and is therefore a decision, not a tuning knob.

3. Add the code `director.egress_unapproved` to `DIRECTOR_CODES` with the exact
   message template `"the span from source %s was not approved for egress: the
   %s right reads %s; next safe action: record %s: granted on that source's
   rights record, or choose a treatment that does not consume that right"`.

4. Implement `approved_spans(base, doc, objective_id, treatment_kind,
   source_texts)` returning the two-tuple `(spans, omissions)`. In this order:
   resolve the required right with `graph.treatment_right(treatment_kind)`;
   collect every `## Bindings` row for the objective whose `binding_kind` is
   `source`; for each, read the CURRENT registry state through
   `course.rights_for_binding(base, source_object_id, operation)` and decide
   with `identity.rights_granted`; on a False result append an omission with
   reason `rights-not-granted` and continue; on a True result look up the
   source text and append an omission with reason `source-unreadable` if it is
   absent; otherwise build a span dict with the keys `source_object_id`,
   `locator`, `text`, and `bytes`. Then deduplicate by
   `(source_object_id, locator_key(locator))` keeping the first, sort both
   lists by the same key, and apply the span cap then the byte cap, appending
   each excluded span to the omission list with its reason. The function takes
   no rights parameter and caches no registry read; its docstring states in
   plain sentences that the registry is re-read on every call and that a value
   observed earlier in the same process is history.

5. Wire `approved_spans` into `recommendation_request` so the request's
   `source_spans` are exactly the approved spans, and so the evidence-key
   refusal from plan 15A-01 still runs over each span before the request is
   built. The `text` field is what leaves the machine; the `bytes` field is its
   UTF-8 length and is what the egress record discloses.

6. Add `build_rights_matrix_fixture(dest)` to `fixtures/corpus_14b.py`,
   building the four-source rights matrix described above plus one objective
   bound to all four sources, with twelve fictional spans available and source
   texts generated from the existing fixed seed. No real course, book, learner,
   or bank content of any kind.

7. Re-run `python tests/director_roundtrip.py` until it passes, then run
   `python itembank.py guard .` and confirm it reports `0 offending files`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Degraded states this task
proves: a source whose right is unknown contributes nothing and is named; a
right revoked between two calls takes effect on the second; a source whose text
cannot be read is disclosed as an omission rather than crashing the pass; and a
cap drops whole spans that are named rather than truncating one silently.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import director; print(director.MAX_EGRESS_SPANS, director.MAX_EGRESS_BYTES, len(director.OMISSION_REASONS))"`
  prints `8 16384 4`.
- `python -c "import director,inspect; print([p for p in inspect.signature(director.approved_spans).parameters if 'rights' in p])"`
  prints `[]`.
- `director.py` contains `def approved_spans(`.
- `fixtures/corpus_14b.py` contains `def build_rights_matrix_fixture(`.
- None of `director.py`, `fixtures/corpus_14b.py`, or
  `tests/director_roundtrip.py` contains an em dash character.
  </acceptance_criteria>
  <done>An agent receives spans only from sources whose required right reads
  granted in the live registry at the moment of the call, every excluded source
  is named with its reason, and no snapshot, prior read, or binding row can
  authorize a span.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the settings-side autonomy policy and the over-declaration refusal</name>
  <files>director.py, schemas/settings.schema.json, itembank.json, tests/config_roundtrip.py, tests/director_roundtrip.py</files>
  <read_first>
- `schemas/settings.schema.json` in full, especially the top-level `required`
  array, the `auditor_autonomy` property (the closest existing analog to what
  is being added), the `suggestion_reveal` property, and the
  `model_backend.profiles` block. Every top-level property carries `default`,
  `x-itembank-phase`, and `description`.
- `tests/config_roundtrip.py` lines 105 to 165, especially
  `test_schema_names_every_project_key` and its hardcoded `expected` set, and
  lines 645 to 665, `test_suggestion_reveal_enum_and_default`, which is the
  shape the new test copies.
- `surfaces/settings.py` lines 115 to 195: `load_schema`,
  `defaults_from_schema`, `merge_over_defaults`, and `load_settings`. Note that
  `defaults_from_schema` recurses into any object property that has its own
  `properties`, so the leaf defaults are what actually fill in, and that
  `load_settings` validates one top-level key at a time.
- `itembank.json` in full, so the new block is added in the file's existing key
  order and formatting.
- `.agents/skills/OPERATION-CONTRACT.md`, the numbered protocol step 11 and the
  paragraph beginning "An agent may recommend, draft-and-review, or perform
  approved bounded writes."
- `director.py` as it stands after Task 1.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_autonomy_policy()` function, and to `tests/config_roundtrip.py` in a new
`test_agent_policy_enum_and_default()` function, both written before the code.

The settings block:

- `schemas/settings.schema.json` has a top-level `agent_policy` property
  carrying `default`, `x-itembank-phase`, and `description`.
- `agent_policy` has `additionalProperties` `false` and `required` equal to
  `["autonomy_level", "max_bindings_per_operation"]`.
- `agent_policy.properties.autonomy_level` has `enum` equal to
  `["recommend-only", "draft-and-review", "approved-bounded-write"]` and
  `default` equal to `"recommend-only"`.
- `agent_policy.properties.max_bindings_per_operation` has `type` `integer`,
  `minimum` `0`, `maximum` `50`, and `default` `0`.
- `"agent_policy"` is in the schema's top-level `required` array.
- `surfaces.settings.load_settings` on a directory with no `itembank.json`
  returns a dict whose `agent_policy` equals
  `{"autonomy_level": "recommend-only", "max_bindings_per_operation": 0}`.
  A fresh install grants nothing.
- `surfaces.settings.load_settings` on a directory whose `itembank.json` omits
  `agent_policy` entirely returns the same defaults, and does not exit.
- An `itembank.json` whose `agent_policy.autonomy_level` is `"anything"` makes
  `load_settings` exit with a `settings.`-coded message naming the key.
- The repository's own `itembank.json` carries an `agent_policy` block whose
  values validate against the schema.
- `tests/config_roundtrip.py` passes with the new key in its expected set.

The refusal, never a narrowing:

- `director.autonomy_level(settings)` returns
  `settings["agent_policy"]["autonomy_level"]` and returns
  `"recommend-only"` when the block or the key is absent.
- `director.AUTONOMY_LEVELS` equals `("recommend-only", "draft-and-review",
  "approved-bounded-write")`, in ascending authority order.
- `director.authorize_write(settings, declared_level, bindings_requested)`
  returns `None` when the declared level is at or below the policy level and
  the requested binding count is at or below
  `max_bindings_per_operation`.
- With a policy of `recommend-only` and a declared level of
  `approved-bounded-write`, it raises `DirectorError` with code
  `director.autonomy_exceeded`, and the message contains both level names and
  the word `refused`.
- It never returns a narrowed level: the function's return value on the success
  path is `None`, so there is no value a caller could mistake for a granted
  level.
- With a policy of `approved-bounded-write` and
  `max_bindings_per_operation` of `2`, a request for `3` bindings raises
  `DirectorError` with code `director.bind_cap_exceeded` naming both numbers.
- With a policy of `approved-bounded-write` and a declared level of
  `recommend-only`, it returns `None`. Declaring less than the policy allows is
  always permitted.
- An unrecognized declared level raises `DirectorError` with code
  `director.autonomy_exceeded` naming the value and the three accepted members.
  An unknown authority is refused, never treated as the lowest level.

Wiring:

- `director.recommend_treatments` calls `authorize_write` before its first
  `apply_recommendation` and not once per objective, so an over-declaring
  operation is refused before any binding is written rather than after the
  first.
- With a policy of `recommend-only`, a full pass over the fixture's four
  objectives returns four entries whose `outcome` is `untreated` and appends no
  binding row, and the refusal reason is recorded on the journal entry.
  </behavior>
  <action>
1. Add `check_autonomy_policy()` to `tests/director_roundtrip.py` and
   `test_agent_policy_enum_and_default()` to `tests/config_roundtrip.py` first,
   both wired into their files' `main()` functions, with every assertion above.
   Run both and confirm both fail.

2. Edit `schemas/settings.schema.json`. Add one top-level property
   `agent_policy` in the file's existing alphabetical-adjacent placement style,
   with:
   - `"type": "object"`, `"additionalProperties": false`,
     `"required": ["autonomy_level", "max_bindings_per_operation"]`.
   - `"x-itembank-phase": "15A"`.
   - `"default": {"autonomy_level": "recommend-only",
     "max_bindings_per_operation": 0}`.
   - A `description` reading exactly: `The granted agent autonomy for this
     installation (OPERATION-CONTRACT.md step 11, RIGHTS-02, AGENT-02). The
     policy decides what an agent client may do without review; an agent that
     declares a higher level than this is refused by name and is never silently
     narrowed to the permitted level. Read by Phase 15A.`
   - `properties.autonomy_level`: `"type": "string"`, `"enum":
     ["recommend-only", "draft-and-review", "approved-bounded-write"]`,
     `"default": "recommend-only"`, `"x-itembank-phase": "15A"`, and a
     description naming the three levels and stating that unknown authority
     stays restrictive.
   - `properties.max_bindings_per_operation`: `"type": "integer"`,
     `"minimum": 0`, `"maximum": 50`, `"default": 0`,
     `"x-itembank-phase": "15A"`, and a description stating that a request for
     more bindings than this in one operation is refused by name and that zero
     means an agent writes nothing without review.
   Add `"agent_policy"` to the schema's top-level `required` array. Use no
   schema keyword that is not already present somewhere in this file.

3. Edit `itembank.json`, adding the `agent_policy` object with the two default
   values, placed to match the file's existing key ordering and its two-space
   indentation, with a trailing newline preserved.

4. Edit `tests/config_roundtrip.py`: add the string `"agent_policy"` to the
   `expected` set inside `test_schema_names_every_project_key`, and extend that
   function's docstring by appending the sentence `Phase 15A adds
   agent_policy.` Change nothing else in that function.

5. Add to `director.py` the constants
   `AUTONOMY_LEVELS = ("recommend-only", "draft-and-review",
   "approved-bounded-write")`, in ascending authority order with a comment
   saying so, and
   `AGENT_POLICY_DEFAULTS = {"autonomy_level": "recommend-only",
   "max_bindings_per_operation": 0}` with a comment stating that these mirror
   the schema defaults and exist so a caller passing a settings dict with no
   block still gets the restrictive answer.

6. Add the codes `director.autonomy_exceeded` and
   `director.bind_cap_exceeded` to `DIRECTOR_CODES` with these exact message
   templates:
   - `director.autonomy_exceeded`: `"this operation declares autonomy %s but
     the installation policy grants %s, so the operation is refused; an agent
     never raises its own authority and the declared level is never silently
     narrowed; accepted levels are recommend-only, draft-and-review,
     approved-bounded-write"`
   - `director.bind_cap_exceeded`: `"this operation requests %d bindings but
     the installation policy allows %d per operation, so the operation is
     refused; raise agent_policy.max_bindings_per_operation deliberately or
     split the work"`

7. Implement `autonomy_level(settings)` reading
   `settings.get("agent_policy", {}).get("autonomy_level")` and falling back to
   `AGENT_POLICY_DEFAULTS["autonomy_level"]`. Implement
   `authorize_write(settings, declared_level, bindings_requested)` raising
   `director.autonomy_exceeded` for an unrecognized declared level, raising it
   again when `AUTONOMY_LEVELS.index(declared_level)` exceeds
   `AUTONOMY_LEVELS.index(policy_level)`, raising
   `director.bind_cap_exceeded` when the requested count exceeds the policy
   cap, and otherwise returning `None`. Its docstring states in plain sentences
   that the function returns no level, so no caller can mistake its result for
   a grant, and that narrowing instead of refusing would hide the
   over-declaration this check exists to surface.

8. Replace the placeholder autonomy check inside `recommend_treatments` that
   plan 15A-02 Task 2 step 4 left, calling `authorize_write` once before the
   loop with the count of objectives that would be bound, and recording a
   refusal entry per objective when it raises.

9. Re-run `python tests/director_roundtrip.py` and
   `python tests/config_roundtrip.py` until both pass, then run
   `python tests/daemon_roundtrip.py` and `python tests/model_adapter_roundtrip.py`
   to confirm the settings change broke no other reader, then run
   `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py && python tests/config_roundtrip.py</automated>
Expected: both print their OK lines and exit 0. Also run
`python tests/daemon_roundtrip.py` and `python tests/model_adapter_roundtrip.py`,
both expected exit 0, which is the proof that adding a top-level settings block
broke no existing settings reader. Degraded states this task proves: a
directory with no settings file reads the restrictive default rather than a
permissive one; a settings file omitting the block reads the same defaults
without exiting; an invalid level exits with a named settings code rather than
reaching a caller; and an unrecognized declared level is refused rather than
treated as the lowest.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0.
- `python tests/config_roundtrip.py` exits 0.
- `python tests/daemon_roundtrip.py` exits 0.
- `python tests/model_adapter_roundtrip.py` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import json; s=json.load(open('schemas/settings.schema.json')); a=s['properties']['agent_policy']; print(a['properties']['autonomy_level']['default'], a['properties']['max_bindings_per_operation']['default'], 'agent_policy' in s['required'], sorted(a) >= ['default'])"`
  prints `recommend-only 0 True True`.
- `python -c "import json; d=json.load(open('itembank.json')); print(d['agent_policy'])"`
  prints `{'autonomy_level': 'recommend-only', 'max_bindings_per_operation': 0}`.
- `python -c "import director; print(director.AUTONOMY_LEVELS)"` prints
  `('recommend-only', 'draft-and-review', 'approved-bounded-write')`.
- `python -c "import director; print(director.authorize_write({}, 'recommend-only', 0))"`
  prints `None`.
- `director.py` contains `def authorize_write(` and `def autonomy_level(`.
- None of `director.py`, `schemas/settings.schema.json`, `itembank.json`,
  `tests/config_roundtrip.py`, or `tests/director_roundtrip.py` contains an em
  dash character.
  </acceptance_criteria>
  <done>The granted autonomy is a recorded installation policy, an agent that
  declares more is refused by name rather than narrowed, and a fresh install
  grants nothing.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the egress record, exact and ordered</name>
  <files>director.py, tests/director_roundtrip.py</files>
  <read_first>
- `director.py` as it stands after Task 2, in full, especially `EGRESS_KEYS`,
  `approved_spans`, `recommendation_request`, `record_phase`, and
  `recommend_once`.
- `.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md`, the dated
  section `## D-15A-2. Where the egress record lives`. The recorded option
  decides whether the egress dict is written into the journal entry's `agent`
  key or into a sibling file, and plan 15A-01 Task 3 already named the exact
  edits each option forces. Follow the recorded option; do not assume one.
- `journal.py` as landed: `append_entry`, `entries`, `ENTRY_KEYS`, and the
  `undo` key's dict-valued precedent.
- `model_adapter.py` lines 233 to 262, `_invoke`, especially the line that
  builds `request_json` with `json.dumps(request, ensure_ascii=False,
  sort_keys=True)`. That string is what actually crosses the boundary and is
  what `payload_bytes` must measure.
- `REQUIREMENTS.md`, the RIGHTS-02 entry in full including its Fixture
  sentence.
- `tests/director_roundtrip.py` as it stands after Task 2.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_egress_record()` function, written before the code.

Exactness:

- After one successful hosted run, exactly one journal entry carries a non-null
  egress record whose key set equals `set(director.EGRESS_KEYS)`.
- The record's `spans` list has one member per span actually sent, each with
  the keys `source_object_id`, `locator`, and `bytes`, and no `text` key. The
  disclosure names what was sent; it does not duplicate the content.
- The set of `(source_object_id, locator)` pairs in the record equals exactly
  the set in the request's `payload.recommendation_request.source_spans`. Not a
  subset, not a superset.
- Each span's `bytes` equals `len(text.encode("utf-8"))` for the text that
  actually went into the request.
- The record's `payload_bytes` equals
  `len(json.dumps(request, ensure_ascii=False, sort_keys=True).encode("utf-8"))`
  for the request that `model_adapter.invoke` was handed, computed in the test
  by rebuilding the same request and measuring it.
- The record's `omitted` list carries every span the rights gate or a cap
  excluded, each with a `reason` in `director.OMISSION_REASONS`, and no
  `(source_object_id, locator)` pair appears in both `spans` and `omitted`.
- The record's `destination` is `"hosted"` for a `hosted_cli` profile and
  `"registered-local"` for an `openai_compatible` profile, and its
  `backend_class` matches the adapter result's `provider.backend_class`.
- The record's `profile` is the profile NAME string only. No key, endpoint,
  command vector, or environment variable name appears anywhere in the record,
  asserted by a recursive walk over the record's values.
- The record's `evidence_included` is `False` on every recorded operation.

Adjacency, empty, and ordering:

- A span offered twice within one operation, differing only by trailing
  carriage returns in its locator, appears exactly once in `spans`.
- Two separate operations produce two separate journal entries with two
  separate egress records; no record is shared or appended to.
- An operation that sends nothing, because every source was refused, records an
  egress dict whose `destination` is `"local"`, whose `spans` and `omitted`
  behaviour is that `spans` is `[]` and `omitted` names every refused source,
  and whose `payload_bytes` is `0`. The egress key is present and non-null.
- An operation with no reachable backend at all records `destination` `"local"`
  and `payload_bytes` `0`, and the test asserts no HTTP request was made by
  binding a socket the fixture server would have used and confirming it is
  still free.
- Both `spans` and `omitted` are sorted by `(source_object_id,
  director.locator_key(locator))` ascending.
- Two runs of one operation with the same inputs produce egress records that
  are equal after `director.parity_view` is applied to each.

Degraded and local-only:

- With every registered profile unreachable, a full `recommend_treatments` pass
  returns entries whose `outcome` is `untreated`, appends no binding row, and
  records `destination` `"local"` on every entry.
- The shipped suites still pass after the pass: `tests/scoring_roundtrip.py`,
  `tests/evidence_roundtrip.py`, and `tests/session_roundtrip.py` if that file
  exists in this repository, else `tests/protocol_roundtrip.py`. All core work
  is local and model-free.
  </behavior>
  <action>
1. Add `check_egress_record()` to `tests/director_roundtrip.py` first, wired
   into `main()`, with every assertion above. Run and confirm it fails.

2. Implement `egress_record(destination, backend_class, profile_name, spans,
   omissions, payload_bytes)` in `director.py`, returning a dict whose key
   order is `EGRESS_KEYS`. It strips the `text` key from every span, sorts both
   lists by `(source_object_id, locator_key(locator))`, sets
   `evidence_included` to `False` unconditionally, and refuses with
   `director.evidence_forbidden` if any span or omission dict carries any of
   the keys `score`, `verdict`, `attempt_number`, `session_id`, `mark`,
   `response`, `canonical`, or `note`. Its docstring states in plain sentences
   that this record is the disclosure of what left the machine, that it names
   every span and every omission exactly rather than summarizing, and that
   `evidence_included` is a disclosure field whose value is False because no
   code path in this module can reach the evidence store.

3. Wire `egress_record` into `recommend_once` so that every recorded phase that
   involved a backend call carries the egress dict, including the failure
   paths. Compute `payload_bytes` from the same
   `json.dumps(request, ensure_ascii=False, sort_keys=True)` string
   `model_adapter._invoke` builds, encoded UTF-8. Compute it in `director.py`
   from the request `director` itself built, so the two cannot disagree without
   the request itself having changed.

4. Map the destination from the resolved profile's transport:
   `hosted_cli` gives `"hosted"`, `openai_compatible` gives
   `"registered-local"`, and no resolved profile or an unavailable result with
   no request sent gives `"local"` with `payload_bytes` `0` and an empty
   `spans` list. Never invent a fourth destination string.

5. If `15A-DECISIONS.md` recorded `option-b` or `option-c` for `D-15A-2`,
   apply the exact edits plan 15A-01 Task 3 named for that option before
   proceeding, and record in the summary that you did.

6. Re-run `python tests/director_roundtrip.py` until it passes. Then run the
   wave check: `python tests/scoring_roundtrip.py`,
   `python tests/evidence_roundtrip.py`, and
   `python tests/protocol_roundtrip.py`, all expected to exit 0. Then run
   `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Also run
`python tests/scoring_roundtrip.py`, `python tests/evidence_roundtrip.py`, and
`python tests/protocol_roundtrip.py`, all expected exit 0, which together are
the proof that a recommendation pass with no reachable backend leaves all core
work local and model-free. Degraded states this task proves: an operation that
sends nothing still records an egress dict rather than omitting the field; an
unreachable backend records destination local with zero payload bytes and makes
no network call; and a span carrying an evidence-shaped key is refused before
the record is built.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python tests/scoring_roundtrip.py` exits 0.
- `python tests/evidence_roundtrip.py` exits 0.
- `python tests/protocol_roundtrip.py` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import director; r=director.egress_record('local','',' ',[],[],0); print(sorted(r) == sorted(director.EGRESS_KEYS), r['evidence_included'], r['spans'], r['payload_bytes'])"`
  prints `True False [] 0`.
- `director.py` contains `def egress_record(`.
- `tests/director_roundtrip.py` contains `def check_egress_record(`.
- `git diff --name-only` after this task does not list `model_adapter.py`,
  `journal.py`, `identity.py`, `graph.py`, `course.py`, `model.py`,
  `runtime.py`, `evidence.py`, or any path under `surfaces/`.
- Neither `director.py` nor `tests/director_roundtrip.py` contains an em dash
  character.
  </acceptance_criteria>
  <done>Every operation that touched a backend carries an exact, ordered,
  secret-free record of what left this machine and what was withheld and
  why.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| rights registry to span assembly | A registry value decides whether a source's text may leave the machine at all. |
| director to model backend | Approved span text crosses out of the process to a subprocess or an HTTP endpoint. |
| agent-declared authority to write decision | A value the agent supplies about its own permissions reaches a durable write gate. |
| settings file to policy read | An on-disk policy value decides what an agent may do without review. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15A-04-01 | Elevation of Privilege | an agent raising its own autonomy | high | mitigate | `authorize_write` compares the declared level against `settings.agent_policy.autonomy_level` and refuses with `director.autonomy_exceeded` on excess, returning `None` on success so no caller can mistake its result for a grant. An unrecognized level is refused, not treated as the lowest. |
| T-15A-04-02 | Information Disclosure | more of a source leaving than the rights allow | high | mitigate | `approved_spans` reads the CURRENT registry through `course.rights_for_binding` on every call, decides with `identity.rights_granted`, and takes no rights parameter. The four-source rights matrix asserts all three treatment right classes independently. |
| T-15A-04-03 | Elevation of Privilege | a revoked right staying effective through a snapshot, a cache, or a binding row | high | mitigate | The revocation case re-runs the identical call after `revoke_right` and asserts zero spans, while the existing binding row still shows `granted`. Presentation and history never authorize. |
| T-15A-04-04 | Information Disclosure | an egress record that under-reports what was sent | high | mitigate | The recorded span pair set is asserted equal, not merely a subset, to the request's own `source_spans`, and `payload_bytes` is asserted equal to the measured length of the exact JSON string the adapter serializes. |
| T-15A-04-05 | Information Disclosure | a credential, endpoint, or command vector recorded in the egress log | high | mitigate | The record carries the profile NAME and the backend class only. A recursive walk over the record's values asserts no endpoint, command, or environment-variable name appears. `director.py` never reads `secret_env`. |
| T-15A-04-06 | Information Disclosure | learner evidence reaching a backend inside a span | high | mitigate | `egress_record` and `recommendation_request` both refuse any span dict carrying an evidence-shaped key with `director.evidence_forbidden`, and `director.py` imports no `evidence` and no `runtime`, asserted at runtime in plan 15A-01. |
| T-15A-04-07 | Repudiation | an operation that sent something with no record of it | high | mitigate | Every backend-touching phase records an egress dict, including the failure paths, and the empty case records `destination` `local` with zero bytes rather than omitting the field. |
| T-15A-04-08 | Tampering | a settings edit widening egress caps or autonomy without review | medium | mitigate | Both caps and the policy live in named constants and a schema-validated settings block with restrictive defaults, and the schema description states in plain words that raising either is a decision. Detection of an unreviewed local edit is out of scope for a single-user installation. |
| T-15A-04-09 | Denial of Service | an unbounded span set making one request enormous | medium | mitigate | `MAX_EGRESS_SPANS` and `MAX_EGRESS_BYTES` bound the request before it is built, and the adapter's own per-profile `timeout_seconds` and `max_output_bytes` bound the response. Excluded spans are named rather than truncated. |
| T-15A-04-10 | Tampering | supply chain: a policy engine, permission library, or telemetry client introduced here | high | mitigate | None is added; the whole gate is a tuple index comparison and a registry read. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is not itself the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. A telemetry client would be a direct violation of non-negotiable 3 and is refused on that ground, not on cost. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No per-course autonomy override. The policy is one installation-level
  settings block in this phase. A per-course field would need a new course
  sidecar header column and a 14B schema edit, and belongs to whichever phase
  first has a reason to differ per course.
- No CLI command and no daemon route for reading or setting the policy.
  `itembank config` already reads and writes any schema-declared key by its
  existing generic path, and no new command is added.
- No rights-grant command. `OPERATION-CONTRACT.md` "Pending surfaces" names it
  as not yet shipped; rights are recorded through the 14A registry path.
- No sibling egress file unless `15A-DECISIONS.md` recorded `option-b` or
  `option-c` for `D-15A-2`. Under the recommended default the egress dict lives
  on the journal entry and no second log exists.
- No egress replay, no protocol checklist, no resume, no reverse. Plan 15A-05
  owns them.
- No fourth synthetic domain and no freeze record. Plan 15A-06 owns both.
- No change to `model_adapter.py`, `journal.py`, `identity.py`, `graph.py`,
  `course.py`, `model.py`, `runtime.py`, `evidence.py`, or anything under
  `surfaces/`. The settings block is a schema and data change; no settings
  reader is modified.
- No accessibility claim of any kind. An agent never self-certifies
  accessibility, and this phase ships no learner-facing surface to certify.
</out_of_scope>

<summary_obligations>
`15A-04-SUMMARY.md` records: the `agent_policy` block as landed in both the
schema and `itembank.json`; the exact `payload_bytes` figure the hosted fixture
run measured, recorded and not promised; the number of spans the rights matrix
approved for each of the three treatment right classes; whether `D-15A-2`
forced any option-b or option-c edit and exactly which; which truth was
verified by which command; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15A-director-treatment-policy/15A-04-SUMMARY.md`
when done.
</output>
</content>
