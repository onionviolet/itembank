---
phase: 15B-quality-blueprint-acceptance
plan: 04
type: execute
wave: 4
depends_on: ["15B-03"]
files_modified:
  - graph.py
  - course.py
  - director.py
  - journal.py
  - schemas/course_graph.schema.json
  - fixtures/corpus_15b.py
  - tests/graph_roundtrip.py
  - tests/blueprint_roundtrip.py
autonomous: true
requirements: [RELIABILITY-03, ACTIVITY-02]
estimate:
  tokens: 78000
  raw_tokens: 78000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "graph.accept_migration and graph.reject_migration are the only two code paths permitted to move a recorded migration out of the proposed state; every other path still raises GraphError with code graph.migration_state_not_settable, asserted by a bypass attempt in the same test run."
    - "A migration cannot be accepted by the actor that proposed it: graph.accept_migration compares the proposal's recorded actor to the reviewer and refuses with graph.migration_self_accept when they are equal, so an agent that drafted a revision cannot also grant it."
    - "An already-settled migration cannot be settled again: accepting an accepted proposal, rejecting a rejected one, or accepting a rejected one each raise GraphError with code graph.migration_already_settled and leave the recorded row byte-identical."
    - "The autonomy check happens at the moment of acceptance and reads the live policy: director.accept_revision calls director.autonomy_level and director.authorize_write fresh against the settings passed in at accept time, and its signature takes no autonomy argument, so a value carried on a proposal record cannot authorize anything."
    - "A stale dependent blocks an acceptance before any write: director.accept_revision calls blueprint.acceptance_block and raises DirectorError with code director.acceptance_blocked when the returned list is non-empty, the sidecar bytes on disk are unchanged, and one refused journal entry is appended naming every blocked dependency."
    - "journal.py's diff for this whole phase is exactly one line: one new RECORD_TYPES member. OPERATION_TYPES stays at exactly six and ENTRY_KEYS stays at exactly twenty-three."
    - "Every durable write this plan performs reaches disk through course.write_course, which reaches journal.commit_operation; no function added by this plan opens a file for writing, and a refused acceptance is journaled exactly as an applied one is."
    - "A rejected migration is recorded as rejected with its reviewer and rationale rather than deleted, so a later reader can see that a revision was proposed and declined instead of finding no record at all."
  prohibitions:
    - statement: "A model or agent must not accept its own draft or its own migration proposal; the actor that proposed a revision is never the actor that grants it, and no autonomy setting makes it so."
      status: kept
      verification: flagged-unverified
    - statement: "An autonomy level, a rights value, or a staleness result carried on a proposal record must not authorize a write; every authority decision is re-read live at the moment of the acceptance."
      status: kept
      verification: flagged-unverified
    - statement: "A refused acceptance must not be silently dropped; a refusal is journaled with its reason exactly as an applied acceptance is, so a reader can tell a revision that was never proposed from one that was proposed and refused."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "graph.py gains accept_migration, reject_migration, and three GraphError codes"
    - "course.py gains accept_migration and reject_migration, both writing through write_course"
    - "director.py gains accept_revision and two DirectorError codes"
    - "journal.py gains exactly one RECORD_TYPES member and nothing else"
    - "schemas/course_graph.schema.json gains the reviewer and rationale columns on the migration section"
    - "fixtures/corpus_15b.py gains build_acceptance_fixture"
    - "tests/graph_roundtrip.py gains check_migration_acceptance"
    - "tests/blueprint_roundtrip.py gains check_accept_revision"
  key_links:
    - "graph.py holds the pure state transition and course.py holds the write, because that is the split 14B already built for migration_proposal and record_migration. If the transition lived in course.py, the refusal for a self-accept or an already-settled proposal would fire after a file read and a fingerprint check rather than before, and a caller with no course root could not test it."
    - "director.accept_revision takes settings and reads autonomy from them at call time. It does not take an autonomy argument and does not read one off the proposal. This is the same discipline 15A-04 built for authorize_write and 14B-03's Pitfall 5 named first; a snapshot that authorizes is a revoked right that stays effective forever."
    - "The staleness block runs before the autonomy check and both run before the write, so a blocked acceptance never reaches the policy question and a policy-refused acceptance never reaches the disk. Reordering them would make an authorization failure mask a staleness failure or the reverse, and the journal would record the wrong reason."
    - "journal.RECORD_TYPES gains exactly one member. OPERATION_TYPES stays at six, which 14A-FREEZE.md names as frozen and 14A-03 and 14B-04 both already refused to grow. The one-line diff is the drift signal to watch: a second added member means something in this plan grew a vocabulary it was not supposed to."
---

<objective>
Close the acceptance gap Phase 14B deliberately left open and named this phase
as the owner of, quoted verbatim from `14B-04-PLAN.md` lines 560 to 561: "No
acceptance path. A reviewer accepting or rejecting a migration proposal is
Phase 15B's 'accepted revision' work. Phase 14B records proposals only."

`14B-04` built `graph.migration_proposal`, minted
`graph.MIGRATION_STATES = ("proposed", "accepted", "rejected")`, and then
structurally refused to implement the transition: `migration_proposal` takes no
`state` argument at all, and setting a recorded row's state through any
`graph.py` function raises `GraphError` with code
`graph.migration_state_not_settable`, whose message reads "a migration state is
set by a reviewer at acceptance time, and Phase 14B implements no acceptance
path; a proposal is recorded as proposed and stays proposed".

This plan adds the two functions that legitimately perform that transition, and
nothing else gains the ability. It also adds the live authority re-check that
makes an acceptance an act of reviewer authority rather than a state change,
and it wires plan 15B-03's staleness block in ahead of both.

Decisions already made, cited, and never re-derived here:

- **D-15B-1** in `15B-DECISIONS.md`: where this code lives. This plan is
  written against `option-a`, which puts the pure transition on `graph.py`
  beside `MIGRATION_STATES`, the write on `course.py` beside
  `record_migration`, and the authority re-check on `director.py` beside
  `authorize_write`. If the recorded answer is `option-b` or `option-c`, read
  that decision's recorded consequence list before Task 1.
- **D-15B-2** in `15B-DECISIONS.md`: which write path records an acceptance and
  which `journal.RECORD_TYPES` member it uses. This plan is written against
  `option-a` and the member name `"accept_revision"`.
- **14B-04-PLAN.md** `<behavior>` lines 266 to 293, for the eight-key proposal
  dict, `MIGRATION_KINDS`, `MIGRATION_STATES`, and the
  `graph.migration_state_not_settable` refusal this plan must leave standing
  for every other path.
- **14A-02-PLAN.md** "Artifacts this phase produces", for
  `journal.commit_operation`, `journal.RECORD_TYPES`,
  `journal.OPERATION_TYPES` at exactly six, and the twenty-three-key entry
  tuple frozen in `14A-FREEZE.md`
  that plan 15A-01 grew to twenty-three.
- **15A-04-PLAN.md** `<behavior>` lines 378 to 400, for
  `director.autonomy_level(settings)`, `director.AUTONOMY_LEVELS`, and
  `director.authorize_write(settings, declared_level, bindings_requested)`
  returning `None` on success and never a narrowed level.
- **15B-RESEARCH.md Pitfall 3**, whose named warning sign is
  "`graph.accept_migration` or `blueprint_gate`'s acceptance path reading a
  field named `autonomy` or `rights` off the proposal dict rather than calling
  `director.autonomy_level` or `identity.rights_granted` fresh".
- **15B-RESEARCH.md Anti-Patterns**: letting a model self-certify or accept its
  own migration, and building a third write path.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Whether the self-accept ban is a policy setting or a structural refusal | Structural. `graph.accept_migration` compares the proposal's recorded `actor` to the reviewer and refuses with `graph.migration_self_accept` when they are equal, and no setting turns it off | AGENT-02's ban on self-expanded scope and `15B-RESEARCH.md`'s anti-pattern both name self-acceptance directly; a refusal a setting can disable is not a ban. |
| What an already-settled proposal does | Raises `graph.migration_already_settled` and leaves the row byte-identical | An append-only record with a settled state has an answer already; overwriting it would destroy the first reviewer's decision. |
| Whether a rejected proposal is deleted | No. It is recorded as `rejected` with its reviewer and rationale | `PLANNING-DIRECTIVES` section 3a, quoted: "A rejected or superseded idea is never deleted". A missing row and a declined row must be distinguishable. |
| The order of the three pre-write checks | Staleness first, then self-accept and already-settled, then autonomy, then the write | Each refusal must name its own reason. Checking autonomy first would report a policy failure for a proposal that was stale anyway, and the journal would record the wrong reason. |
| Whether `accept_revision` takes an autonomy argument | No. It takes `settings` and reads the level itself | A function that accepts an autonomy value can be handed a stale one. Removing the parameter removes the failure mode rather than documenting it. |
| How many `journal.RECORD_TYPES` members this phase adds | Exactly one, `"accept_revision"`, covering both acceptance and rejection | Both are the same operation kind with different outcomes; the `state` field on the entry (`applied` or `refused`) already distinguishes them, which is the shape `journal.ENTRY_STATES` was built for. |

Purpose: make an acceptance an act of reviewer authority recorded in the one
journal, not a state change.
Output: the two transition functions, their two write wrappers, the live
authority re-check, and the one-line journal change.
</objective>

<context>
@.planning/phases/15B-quality-blueprint-acceptance/15B-RESEARCH.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-PATTERNS.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/REQUIREMENTS.md
@.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md
@.planning/phases/15A-director-treatment-policy/15A-04-PLAN.md
@audit_writer.py
@blueprint.py
</context>

## Artifacts this phase produces (plan 15B-04 share)

Added to `graph.py`. Every symbol below is new in this phase.

- Functions: `accept_migration(doc, migration_id, reviewer, rationale)`,
  `reject_migration(doc, migration_id, reviewer, rationale)`.
- New `GraphError` codes: `graph.migration_already_settled`,
  `graph.migration_self_accept`, `graph.migration_unknown`.

Added to `course.py`. Every symbol below is new in this phase.

- Functions:
  `accept_migration(course_root, migration_id, reviewer_kind, reviewer_name, rationale, expected_fingerprint)`,
  `reject_migration(course_root, migration_id, reviewer_kind, reviewer_name, rationale, expected_fingerprint)`.
- New `CourseError` code: `course.migration_unknown`.

Added to `director.py`. Every symbol below is new in this phase.

- Constants: `ACCEPT_RECORD_TYPE = "accept_revision"`,
  `ACCEPT_OUTCOMES = ("accepted", "rejected", "refused")`.
- Functions:
  `accept_revision(base, course_root, migration_id, settings, reviewer_kind, reviewer_name, reviewer_role, rationale, staleness_rows=None, dispositions=None, decision="accept")`.
- New `DirectorError` codes: `director.acceptance_blocked`,
  `director.reviewer_required`.

Added to `journal.py`: exactly one new member in `RECORD_TYPES`, the string
`"accept_revision"`. Nothing else in `journal.py` changes.
`OPERATION_TYPES` stays at exactly six and `ENTRY_KEYS` stays at exactly
twenty-three.

Added to `schemas/course_graph.schema.json`: the `reviewer` and `rationale`
columns on the migration section's row shape, both optional so an existing
`proposed` row validates unchanged.

Added to `fixtures/corpus_15b.py`: `build_acceptance_fixture(dest)` returning a
dict with the keys `base`, `course_root`, `migration_ids`, `proposer_actor`,
`reviewer_actor`, `settings_recommend_only`, and
`settings_approved_bounded_write`.

New test functions: `check_migration_acceptance()` in
`tests/graph_roundtrip.py`, and `check_accept_revision()` in
`tests/blueprint_roundtrip.py`.

No CLI command, no daemon route, and no new schema file is produced by this
plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the two transitions that may settle a migration, and nothing else</name>
  <files>graph.py, schemas/course_graph.schema.json, fixtures/corpus_15b.py, tests/graph_roundtrip.py</files>
  <read_first>
- `.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md` in full,
  in particular the "Artifacts this phase produces" section, the `<behavior>`
  block at lines 266 to 293, the three `GraphError` message templates at lines
  323 to 329, and the out-of-scope line 560 to 561 naming this phase.
- `graph.py` as landed: `MIGRATION_KINDS`, `MIGRATION_STATES`,
  `migration_proposal`, the function that records a migration row, the
  `migration_state_not_settable` refusal and where it fires, `GraphError`, and
  `SECTION_ORDER` as plan 15B-02 left it.
- `schemas/course_graph.schema.json` as landed, the migration section's row
  shape and its `required` array.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md`, both
  recorded decisions.
- `tests/graph_roundtrip.py` as landed, its `fail(msg)` helper, its `main()`
  wiring, and `check_migration()` from 14B-04, which this task's new function
  sits beside.
- `audit_writer.py` lines 200 to 206 and 304 to 322, `WriterError` and the
  refuse-rather-than-overwrite shape both new functions copy.
  </read_first>
  <behavior>
Assertions `check_migration_acceptance()` in `tests/graph_roundtrip.py` must
make. Write them first and confirm they fail before extending `graph.py`.

The two functions exist and the bypass still refuses:

- `graph.accept_migration` and `graph.reject_migration` are both callable.
- The 14B path that would set a recorded row's state directly still raises
  `GraphError` with code `graph.migration_state_not_settable`. This is asserted
  in the same run as the two new functions succeeding, so the test proves that
  exactly two paths were opened rather than that the refusal was removed.
- `graph.MIGRATION_STATES` still equals `("proposed", "accepted", "rejected")`
  and has exactly three members. This plan adds no fourth state.
- `graph.MIGRATION_KINDS` is unchanged at five members.

The happy transitions:

- `graph.accept_migration(doc, mid, reviewer, "reviewed against the new
  edition")` returns a doc whose row for `mid` has `state` `"accepted"`, whose
  `reviewer` equals the supplied reviewer, and whose `rationale` equals the
  supplied string. The other seven proposal keys are unchanged in value.
- `graph.reject_migration(doc, mid2, reviewer, "the split loses the
  prerequisite edge")` sets `state` to `"rejected"` and records the same two
  fields. The row is present, not removed.
- Neither function mutates the doc passed in; each returns a new doc, or
  mutates and returns the same object, following whichever convention
  `graph.add_binding` already uses as landed. Assert the convention that
  landed rather than assuming one.
- Serializing and re-parsing the doc after either call round-trips the new
  fields: `graph.parse_course(graph.serialize_course(doc))` produces an equal
  doc.

The refusals, each with its own code:

- An unknown `migration_id` raises `GraphError` with code
  `graph.migration_unknown`, and the message contains the id.
- Accepting an already-accepted proposal raises `GraphError` with code
  `graph.migration_already_settled`, and the recorded row's bytes after the
  raise are identical to before it.
- Rejecting an already-rejected proposal raises the same code.
- Accepting an already-rejected proposal raises the same code. A settled state
  is settled in either direction.
- A reviewer equal to the proposal's recorded `actor` raises `GraphError` with
  code `graph.migration_self_accept`, and the message states that the actor
  that proposed a revision is never the actor that grants it. The comparison is
  exact ASCII with no case folding.
- The same self-accept refusal fires for `reject_migration`, so an agent cannot
  quietly withdraw its own proposal through the reviewer path either.
- An empty or whitespace-only `rationale` raises `GraphError` with code
  `graph.empty_rationale`, reusing 14B-04's existing code rather than minting a
  second one, and the message is 14B-04's existing template.
- Every refusal happens before any field of the row is written, asserted by
  comparing the serialized doc before and after each raise.

Schema additivity:

- `schemas/course_graph.schema.json`'s migration row `required` array is
  unchanged; `reviewer` and `rationale` are optional properties.
- A doc carrying only `proposed` rows with no `reviewer` and no `rationale`
  validates exactly as it did before this plan, proven against a stored golden
  fixture compared byte for byte.
- `python schema_validate.py` reports no error.

Ordering and edges:

- `graph.accept_migration(doc, mid, reviewer, rationale)` called twice with the
  same arguments raises `graph.migration_already_settled` on the second call
  rather than being idempotent. An acceptance is an event, not a desired state.
- A doc with no migration section at all raises `graph.migration_unknown` for
  any id rather than crashing.
- Two proposals sharing every field except `migration_id` are settled
  independently; settling one leaves the other `proposed`.
  </behavior>
  <action>
1. Add `check_migration_acceptance()` to `tests/graph_roundtrip.py` with every
   assertion in `<behavior>`, wire it into `main()`, and run
   `python tests/graph_roundtrip.py` to confirm it fails.

2. Add `build_acceptance_fixture(dest)` to `fixtures/corpus_15b.py`, returning
   the seven keys named in this plan's Artifacts section. It builds one course
   root carrying at least three recorded migration proposals: one to accept,
   one to reject, and one whose recorded `actor` equals the reviewer so the
   self-accept refusal has a real case. It also returns two settings dicts, one
   whose `agent_policy.autonomy_level` is `recommend-only` and one whose level
   is `approved-bounded-write` with `max_bindings_per_operation` of `2`, for
   Task 2. All content is fictional and fixed-seed.

3. Add to `graph.py` the three new `GraphError` codes with these exact message
   templates:
   - `graph.migration_unknown`: `"no migration proposal carries id %s in this
     course; there is nothing to accept or reject"`
   - `graph.migration_already_settled`: `"migration %s is already %s; a settled
     proposal keeps the decision that settled it and is never re-settled"`
   - `graph.migration_self_accept`: `"actor %s proposed migration %s and cannot
     also review it; the actor that proposed a revision is never the actor that
     grants it"`

4. Implement `accept_migration(doc, migration_id, reviewer, rationale)` and
   `reject_migration(doc, migration_id, reviewer, rationale)` as two thin
   wrappers over one private helper that takes the target state, so the two
   share every refusal and cannot drift. The helper performs its checks in this
   order and writes nothing until all four pass: unknown id, already-settled
   state, self-accept, empty rationale. On success it sets `state`, `reviewer`,
   and `rationale` on the row and returns the doc following the landed
   convention. It reads no file, no clock, and no settings, and it never
   consults `MIGRATION_STATES` for anything except membership.

5. Leave the existing `graph.migration_state_not_settable` refusal exactly
   where 14B-04 put it, firing for every path other than these two. Add a
   one-line comment above it naming plan 15B-04 and stating that
   `accept_migration` and `reject_migration` are the only two exceptions and
   that a third would be a change to this comment as well as to the code.

6. Add the optional `reviewer` and `rationale` properties to the migration row
   shape in `schemas/course_graph.schema.json`, both strings with `minLength`
   1, with descriptions naming Phase 15B and RELIABILITY-03. Change no existing
   `required` array. Run `python schema_validate.py` and confirm no error.

7. Run `python tests/graph_roundtrip.py` and confirm it passes, then run
   `python itembank.py guard .` and confirm `0 offending files`.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py && python schema_validate.py && python itembank.py guard .</automated>
Expected: `tests/graph_roundtrip.py` exits 0 with both `check_migration` and
`check_migration_acceptance` run, `schema_validate.py` reports no error, and
`guard` prints `0 offending files`. The degraded behavior this task must prove
rather than paper over is the bypass refusal: in the same run in which the two
new functions succeed, the 14B path that would set a state directly still
raises `graph.migration_state_not_settable`. Assert both in one run, because a
test that only proves the new path works cannot tell an added exception from a
removed guard.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0.
- `python -c "import graph; print(graph.MIGRATION_STATES, len(graph.MIGRATION_KINDS), callable(graph.accept_migration), callable(graph.reject_migration))"`
  prints `('proposed', 'accepted', 'rejected') 5 True True`.
- `python -c "import graph; print(all(c in graph.__dict__.get('GRAPH_CODES', ()) or True for c in ('graph.migration_unknown','graph.migration_already_settled','graph.migration_self_accept')))"`
  prints `True`, and the three literal strings each appear in `graph.py`'s
  source outside a comment.
- `grep -v '^#' graph.py | grep -c "migration_state_not_settable"` prints a
  number greater than `0`.
- `python schema_validate.py` reports no error.
- The stored golden course document with only `proposed` migration rows
  round-trips byte identically through `graph.parse_course` and
  `graph.serialize_course`.
- `python itembank.py guard .` prints `0 offending files`.
- `git diff --name-only` after this task lists only `graph.py`,
  `schemas/course_graph.schema.json`, `fixtures/corpus_15b.py`, and
  `tests/graph_roundtrip.py`.
- None of the four changed files contains an em dash character.
  </acceptance_criteria>
  <precondition>Plan 15B-03 is green, and `graph.migration_proposal`, `graph.MIGRATION_STATES`, and the `graph.migration_state_not_settable` refusal are present on the landed `graph.py` as plan 15B-01's precondition check confirmed.</precondition>
  <reversibility rating="costly">The two function names and their four refusal
  codes are consumed by plan 15B-07's tracer and by whatever Phase 16 builds on
  acceptance. Changing them before the 15B freeze costs one edit per consumer;
  changing them after a migration has been settled and journaled means
  migrating recorded entries.</reversibility>
  <done>Exactly two code paths can settle a migration, each refuses by name for
  four distinct reasons before touching the row, an agent cannot settle its own
  proposal, and the 14B guard that refuses every other path still fires in the
  same test run.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the write, the live authority re-check, and the one-line journal change</name>
  <files>course.py, director.py, journal.py, fixtures/corpus_15b.py, tests/blueprint_roundtrip.py</files>
  <read_first>
- `graph.py` in full as it stands after Task 1, both new functions and their
  four refusals.
- `course.py` as landed: `read_course`, `write_course`, `record_migration`,
  `bind_treatment`, `rights_for_binding`, `bind_blueprint` as plan 15B-02 left
  it, and `CourseError`.
- `journal.py` as landed: `RECORD_TYPES`, `OPERATION_TYPES`, `ENTRY_KEYS`,
  `commit_operation`, `append_entry`, `entries`, and `JournalError`.
- `director.py` as landed: `AGENT_ENTRY_KEYS`, `AUTONOMY_LEVELS`,
  `autonomy_level`, `authorize_write`, `record_phase`, `begin_operation`,
  `PROTOCOL_STEPS`, `DIRECTOR_CODES`, and `DirectorError`.
- `.planning/phases/15A-director-treatment-policy/15A-04-PLAN.md` `<behavior>`
  lines 378 to 400, the exact `authorize_write` contract this task calls and
  does not reimplement.
- `blueprint.py` in full as it stands after plan 15B-03: `staleness_report`,
  `acceptance_block`, and `disposition_record`.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md`,
  `D-15B-2`, for the recorded `journal.RECORD_TYPES` member name.
- `tests/blueprint_roundtrip.py` as it stands after plan 15B-03.
  </read_first>
  <behavior>
Assertions `check_accept_revision()` in `tests/blueprint_roundtrip.py` must
make. Write them first and confirm they fail before extending `course.py`,
`director.py`, and `journal.py`.

The journal grows by exactly one line:

- `"accept_revision"` is in `journal.RECORD_TYPES`.
- `len(journal.OPERATION_TYPES)` is still `6`.
- `len(journal.ENTRY_KEYS)` is still `23` and its last member is still
  `"agent"`.
- `director.ACCEPT_RECORD_TYPE` equals `"accept_revision"` and equals the
  member added to `RECORD_TYPES`, asserted as string equality rather than as
  two literals that happen to match.

The write reaches disk through the one path:

- `course.accept_migration(course_root, mid, "human", "weibao", rationale,
  expected_fingerprint)` returns a revision record whose `revision` is one
  greater than before, and afterwards the parsed sidecar's row for `mid` has
  `state` `"accepted"`.
- The same call appends journal entries whose `operation` is
  `"accept_revision"`, asserted by reading `journal.entries(base)` and finding
  at least one such entry after the call and none before it.
- `course.accept_migration` with a wrong `expected_fingerprint` raises the
  landed `journal.stale_preflight` refusal through `write_course`, the
  sidecar's bytes are unchanged, and a `refused` entry is appended. This plan
  adds no second compare-and-swap check; it inherits the one `write_course`
  already performs.
- `course.reject_migration` behaves identically with `state` `"rejected"`.
- An unknown `migration_id` raises `CourseError` with code
  `course.migration_unknown` before any read of the sidecar's bytes for
  writing.
- No function added by this task opens a file for writing, asserted
  behaviorally by the sidecar's revision advancing by exactly one per
  successful call and by no file appearing outside `_journal/` and the course
  root.

The authority re-check is live and its signature makes a stale value
impossible:

- `inspect.signature(director.accept_revision)` has no parameter named
  `autonomy`, `autonomy_level`, `rights`, or `stale`.
- With `settings` whose `agent_policy.autonomy_level` is `recommend-only`,
  `director.accept_revision(..., reviewer_role="reviewer", decision="accept")`
  raises `DirectorError` with the code `director.autonomy_exceeded` that
  `authorize_write` already raises, the sidecar's bytes are unchanged, and one
  `refused` journal entry is appended whose `agent.phase` is `"accept"`.
- With `settings` whose level is `approved-bounded-write` and whose
  `max_bindings_per_operation` is at least `1`, the same call succeeds.
- The check reads the settings passed at call time: build a proposal while the
  policy reads `approved-bounded-write`, then pass a `recommend-only` settings
  dict to `accept_revision`, and assert it refuses. The proposal's own recorded
  fields never authorize.
- `director.accept_revision` with a `reviewer_role` other than the literal
  `reviewer` raises `DirectorError` with code `director.reviewer_required`
  before the autonomy check, so an agent role is refused for being the wrong
  authority rather than for exceeding a level.

The staleness block runs first and writes nothing:

- With one stale row and no matching disposition,
  `director.accept_revision(..., staleness_rows=rows, dispositions=[])` raises
  `DirectorError` with code `director.acceptance_blocked`, the message names
  every blocked `dependency_object_id`, the sidecar's bytes are unchanged, and
  one `refused` journal entry is appended whose message carries the same list.
- With the same rows and a matching `blueprint.disposition_record`, the call
  succeeds.
- The block runs before the autonomy check: with a stale row AND a
  `recommend-only` policy, the raised code is
  `director.acceptance_blocked`, not `director.autonomy_exceeded`. Assert the
  code, so the ordering is proven rather than assumed.
- With `staleness_rows` omitted entirely, the call proceeds and no staleness
  refusal is raised; a caller supplying no rows asserts nothing, and
  `acceptance_block([], [])` returning `[]` is what makes that safe.

A refusal is recorded exactly as an acceptance is:

- After a run producing one accepted migration, one rejected migration, one
  autonomy refusal, one reviewer refusal, and one staleness block, exactly five
  `accept_revision` entries exist in the journal, and their `state` values are
  `applied`, `applied`, `refused`, `refused`, `refused` in that order.
- Every one of the five entries carries a non-empty `message` naming its
  reason, and the two applied ones carry the reviewer name and the rationale.
- `director.ACCEPT_OUTCOMES` equals `("accepted", "rejected", "refused")` and
  every entry's recorded outcome is a member of it.

Edges:

- `director.accept_revision` with `decision` outside `{"accept", "reject"}`
  raises `DirectorError` with code `director.recommendation_invalid`, reusing
  the landed 15A code rather than minting a second one for the same idea.
- Two `accept_revision` calls for the same `migration_id` produce one applied
  entry and one refused entry, the second refused with the
  `graph.migration_already_settled` reason propagated into the journal message.
  </behavior>
  <action>
1. Add `check_accept_revision()` to `tests/blueprint_roundtrip.py` with every
   assertion in `<behavior>`, wire it into `main()`, and run
   `python tests/blueprint_roundtrip.py` to confirm it fails.

2. Edit `journal.py`. Add exactly one member and nothing else: the string
   `"accept_revision"` to `RECORD_TYPES`, with a one-line comment naming Phase
   15B and RELIABILITY-03 as its reason and stating that both an acceptance and
   a rejection use this one record type, distinguished by the entry's existing
   `state` field. Do not touch `OPERATION_TYPES` and do not touch `ENTRY_KEYS`.

3. Edit `course.py`. Add `accept_migration(...)` and `reject_migration(...)`
   with the six-parameter signatures named in this plan's Artifacts section.
   Each reads the course through `read_course`, calls the matching `graph.py`
   function, and writes through `write_course` with the supplied
   `expected_fingerprint` and `operation="accept_revision"`, following
   `record_migration`'s existing shape exactly, including its `CourseError`
   propagation and its actor arguments. Add the `course.migration_unknown` code
   with the message `"no migration proposal carries id %s in course %s"`,
   raised when `graph` raised `graph.migration_unknown`, so a caller holding
   only a course root gets a course-scoped error. Neither function checks
   rights and neither checks autonomy; both are `director.accept_revision`'s
   and both are checked before either of these is called.

4. Edit `director.py`. Add
   `ACCEPT_RECORD_TYPE = "accept_revision"` and
   `ACCEPT_OUTCOMES = ("accepted", "rejected", "refused")`. Add the two new
   `DIRECTOR_CODES` members with these exact message templates:
   - `director.acceptance_blocked`: `"acceptance is blocked: the dependencies
     %s have changed since this object was built, and each needs a recorded
     rebind, migrate, supersede, or retain review before anything built on it
     becomes durable"`
   - `director.reviewer_required`: `"role %s cannot accept or reject a
     revision; RELIABILITY-03 names the reviewer as the authority, and an agent
     never grants its own draft"`

5. Implement `director.accept_revision(base, course_root, migration_id,
   settings, reviewer_kind, reviewer_name, reviewer_role, rationale,
   staleness_rows=None, dispositions=None, decision="accept")` performing its
   steps in exactly this order:
   - Validate `decision` is `"accept"` or `"reject"`; otherwise raise
     `director.recommendation_invalid`.
   - Call `blueprint.acceptance_block(staleness_rows, dispositions)`; on a
     non-empty list, append one `refused` journal entry through `record_phase`
     with `phase="accept"` and a message naming every blocked
     `dependency_object_id`, then raise `director.acceptance_blocked`.
   - Check `reviewer_role` equals the literal `"reviewer"`; otherwise append
     one `refused` entry and raise `director.reviewer_required`.
   - Call `director.authorize_write(settings, "approved-bounded-write", 1)`,
     which reads the live policy itself; on its raise, append one `refused`
     entry carrying that code and message, then re-raise unchanged. Do not
     catch and rewrite the code.
   - Call `course.accept_migration` or `course.reject_migration` per
     `decision`; on a `CourseError`, `GraphError`, or `JournalError`, append
     one `refused` entry carrying that code and message and re-raise unchanged.
   - On success, append one `applied` entry through `record_phase` with
     `phase="accept"` carrying the reviewer name, the rationale, and the
     outcome (`"accepted"` or `"rejected"`), and return the revision record.

   Write the function's docstring stating in plain sentences that it takes no
   autonomy, rights, or staleness argument that could carry a stale value; that
   it re-reads the policy from the settings handed to it at call time; that the
   three checks run in a fixed order so each refusal names its own reason; and
   that a refusal is journaled exactly as an acceptance is.

6. Add `import blueprint` to `director.py` if it is not already present, beside
   its existing imports. `director.py` may import `blueprint` because
   `blueprint.py` imports nothing that imports `director`; confirm no cycle by
   running `python -c "import director, blueprint; print('no cycle')"`.

7. Run `python tests/blueprint_roundtrip.py`, then
   `for t in tests/*.py; do python "$t" || exit 1; done`, then
   `python itembank.py guard .`, and confirm all three succeed.

8. Confirm the one-line journal rule: run `git diff --stat journal.py` and
   confirm it reports exactly one changed line of added content beyond the
   comment.
  </action>
  <verify>
  <automated>python tests/blueprint_roundtrip.py && python tests/journal_roundtrip.py && python tests/graph_roundtrip.py && python itembank.py guard .</automated>
Expected: all three test files exit 0 and `guard` prints `0 offending files`.
The degraded behavior this task must prove rather than paper over is the
ordering of the refusals: with a stale dependency AND a `recommend-only` policy
AND a non-reviewer role all true at once, the raised code is
`director.acceptance_blocked`, the sidecar's bytes are unchanged, and exactly
one `refused` journal entry exists naming the staleness reason. A refusal that
named the policy instead would tell the reviewer to change a setting when the
real problem is an unreviewed change.
  </verify>
  <acceptance_criteria>
- `python tests/blueprint_roundtrip.py` exits 0 with `check_accept_revision`
  run.
- `python -c "import journal, director; print('accept_revision' in journal.RECORD_TYPES, len(journal.OPERATION_TYPES), len(journal.ENTRY_KEYS), director.ACCEPT_RECORD_TYPE)"`
  prints `True 6 23 accept_revision`.
- `python -c "import inspect, director; p=inspect.signature(director.accept_revision).parameters; print(any(n in p for n in ('autonomy','autonomy_level','rights','stale')))"`
  prints `False`.
- `python -c "import director; print(director.ACCEPT_OUTCOMES)"` prints
  `('accepted', 'rejected', 'refused')`.
- `python -c "import director, blueprint; print('no cycle')"` prints
  `no cycle`.
- `python -c "import course; print(callable(course.accept_migration), callable(course.reject_migration))"`
  prints `True True`.
- `git diff --stat journal.py` reports exactly one changed line of added
  content beyond comments.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files`.
- `git diff --name-only` after this task lists only `course.py`, `director.py`,
  `journal.py`, `fixtures/corpus_15b.py`, and `tests/blueprint_roundtrip.py`.
- None of the five changed files contains an em dash character.
  </acceptance_criteria>
  <precondition>Task 1 is green, and `blueprint.acceptance_block` and `blueprint.disposition_record` exist on `blueprint.py` from plan 15B-03.</precondition>
  <reversibility rating="costly">The genuinely one-way part of this task, the
  append-only `journal.RECORD_TYPES` member name and the write path that uses
  it, was decided by the blocking `checkpoint:decision` `D-15B-2` in plan
  15B-01 Task 3. This task implements that decision and makes none of its own,
  so no second checkpoint is owed and the residual cost here is a costly one:
  changing the two function names or their six-parameter signatures before the
  15B freeze costs one edit per consumer, while changing the recorded member
  name after an acceptance has been journaled would be a migration of recorded
  entries and would require reopening `D-15B-2`.</reversibility>
  <done>A reviewer accepts or rejects a migration through the one write path
  with the live policy re-read at accept time, a stale dependency blocks it
  before the policy is consulted, a refusal is journaled exactly as an
  acceptance is, and `journal.py`'s whole-phase diff is one line.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| proposal record to acceptance decision | An agent-authored proposal carries fields that must never authorize the write that settles it. |
| settings to write permission | A policy value read at the moment of acceptance decides whether a durable write proceeds. |
| proposer actor to reviewer actor | The one identity comparison that separates drafting authority from granting authority. |
| in-memory doc to durable sidecar | The transition happens in memory and becomes real only through `course.write_course` and `journal.commit_operation`. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15B-04-01 | Elevation of Privilege | an agent accepting its own migration proposal | high | mitigate | `graph.accept_migration` and `graph.reject_migration` compare the proposal's recorded `actor` to the reviewer with exact ASCII equality and refuse with `graph.migration_self_accept`; no setting disables the refusal, and it is asserted for both functions. |
| T-15B-04-02 | Elevation of Privilege | a carried-forward autonomy value authorizing a write | high | mitigate | `director.accept_revision`'s signature has no `autonomy`, `autonomy_level`, `rights`, or `stale` parameter, asserted by inspecting the signature, and it calls `director.authorize_write` against the settings handed to it at call time. The build-permissive-then-accept-restrictive case is asserted directly. |
| T-15B-04-03 | Tampering | a stale dependency accepted because the policy allowed the write | high | mitigate | `blueprint.acceptance_block` runs before the reviewer and autonomy checks, and the all-three-failing case asserts the raised code is `director.acceptance_blocked` rather than the policy code. |
| T-15B-04-04 | Tampering | a third code path gaining the ability to settle a migration | high | mitigate | The 14B `graph.migration_state_not_settable` refusal is left in place and is asserted to still fire in the same test run in which the two new functions succeed. |
| T-15B-04-05 | Repudiation | a refused acceptance leaving no record | high | mitigate | Every refusal path appends one `refused` journal entry carrying its code and message before raising, and the five-entry sequence with its exact `state` order is asserted. |
| T-15B-04-06 | Tampering | an already-settled proposal re-settled, destroying the first decision | high | mitigate | `graph.migration_already_settled` fires for all three re-settlement directions, and the row's bytes are compared before and after each raise. |
| T-15B-04-07 | Tampering | a second write path or a second compare-and-swap check | high | mitigate | Both `course.py` functions write only through `write_course` and inherit its `journal.stale_preflight` check; the wrong-fingerprint case is asserted to refuse and leave bytes unchanged, and no new lock or fingerprint comparison is added. |
| T-15B-04-08 | Tampering | a journal vocabulary growing past one member | high | mitigate | `git diff --stat journal.py` reporting exactly one changed line of added content is an acceptance criterion, and `OPERATION_TYPES` at six and `ENTRY_KEYS` at twenty-three are each asserted. |
| T-15B-04-09 | Repudiation | a rejected proposal deleted rather than recorded | medium | mitigate | `reject_migration` sets `state` to `"rejected"` and records the reviewer and rationale on the existing row; the assertion checks the row is present, not absent. |
| T-15B-04-10 | Information Disclosure | real course content entering through the acceptance fixture | high | mitigate | `build_acceptance_fixture` builds fictional fixed-seed content, and `python itembank.py guard .` is in both tasks' acceptance criteria. |
| T-15B-04-11 | Tampering | supply chain: a dependency added for the acceptance path | high | mitigate | None is added; every function composes already-present in-repo modules. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review. |
| T-15B-04-12 | Denial of Service | two clients accepting against one course root at once | low | accept | `journal.commit_operation` already holds the journal lock and refuses with `journal.busy` after its ten-second timeout. Accepted because this is a single-learner local product and the shipped lock is the mitigation; the interleaving case is named as an open backstop rather than proven. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No fourth `graph.MIGRATION_STATES` member. Three states are what 14B-04
  minted and this plan adds transitions, not states.
- No acceptance path for a drafted question set. Bank content is accepted by
  `audit_writer.write_units` through `authoring.run_authoring`, which plan
  15B-02 already wired the blueprint gate into, and this plan does not touch
  either.
- No second compare-and-swap check, no second lock, and no second fingerprint
  comparison. Both new `course.py` functions inherit `write_course`'s.
- No `journal.OPERATION_TYPES` change. `14A-FREEZE.md` names the six operation
  names as frozen, and 14A-03 and 14B-04 both already refused to grow it.
- No `journal.ENTRY_KEYS` change. Plan 15A-01 added the one member this family
  needed and the tuple stays at twenty-three.
- No undo or reversal command for an acceptance. `journal.undo` already exists
  and reversing an accepted revision through it is a real capability that no
  requirement in this phase asks for; whichever phase ships a builder-facing
  surface owns it.
- No rights check on `course.bind_blueprint`. Plan 15B-02 wrote that function
  without one deliberately and said so; adding one here would put an authority
  decision in the I/O layer where a caller could bypass it.
- No course audit and no evidence proposal. Those are plans 15B-05 and 15B-06.
- No CLI command and no daemon route for accepting anything.
  `OPERATION-CONTRACT.md`'s "Pending surfaces" section names these commands as
  not yet shippable and says in plain words not to invent them.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped:

- **The reviewer identity is a string, not an authenticated one (assumption,
  recorded, carried from plan 15B-03).** `director.accept_revision` refuses any
  `reviewer_role` other than `reviewer` and `graph.accept_migration` refuses a
  reviewer equal to the proposer, but nothing authenticates that the caller is
  either. This matches the authority model `journal.commit_operation`'s
  `origin` already carries. Recorded so plan 15B-07's freeze record does not
  imply a stronger guarantee than the code makes.
- **The concurrency backstop (open).** The interleavings the fixtures reach all
  leave one valid state, because `journal.commit_operation`'s lock is the one
  serialization point. Whether some interleaving exists that the fixtures do
  not reach is not proven here and is owned by the phase that first runs two
  agent clients against one course root in earnest, exactly as plan 15A-05
  recorded the same backstop for its own operations.
</flagged_assumptions>

<summary_obligations>
`15B-04-SUMMARY.md` records: which truth was verified by which command, with
the command's actual stdout; the exact `git diff --stat journal.py` output
proving the one-line rule; the five-entry journal sequence from the refusal
ordering assertion, quoted; whether the 14B `migration_state_not_settable`
bypass refusal still fired in the same run as the two new functions succeeding;
the measured wall-clock time of one full `tests/blueprint_roundtrip.py` run;
and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15B-quality-blueprint-acceptance/15B-04-SUMMARY.md`
when done.
</output>
