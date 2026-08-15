---
phase: 15A-director-treatment-policy
plan: 02
type: execute
wave: 2
depends_on: ["15A-01"]
files_modified:
  - director.py
  - fixtures/corpus_14b.py
  - tests/director_roundtrip.py
autonomous: true
requirements: [TREAT-01]
estimate:
  tokens: 62000
  raw_tokens: 62000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Every objective in a course reaches one of exactly three recorded outcomes after a recommendation pass: a treatment bound from the closed eleven-kind vocabulary, an explicit untreated state carrying the reason it was not treated, or a refusal naming the right that was missing. No fourth outcome exists, and no objective changes state without a journal entry."
    - "Direct reading is a complete result: an objective bound with treatment_kind direct-reading is not listed by director.untreated_objectives, is not re-proposed on a second pass, and passes through exactly the same rights gate as every generative kind, refusing when the source's read right is unknown."
    - "Generation is never automatic: when no backend answers, director.recommend_treatments writes no binding and invents no local treatment; every affected objective is reported untreated with reason backend-unavailable, and the phase's own test asserts the binding count is unchanged."
    - "TREAT-01 boundary edge: the treatment vocabulary has exactly eleven members. A candidate naming any of the eleven is accepted and a candidate naming a twelfth token is refused with director.unknown_treatment_kind before any write, so both sides of the boundary are proven rather than only the passing side."
    - "TREAT-01 adjacency edge: when two candidate treatment kinds carry the same confidence for one objective, the member earlier in graph.TREATMENT_KINDS order wins deterministically and the loser is retained in the record's alternatives list. A tie never merges into one blended kind and never silently drops the loser."
    - "TREAT-01 empty edge: a course with zero objectives returns an empty recommendation list and appends no journal entry at all; an objective with zero source bindings returns a record whose treatment_kind is the empty string and whose coverage state is missing, never a generated treatment and never a null record."
    - "TREAT-01 ordering edge: recommendations are emitted in the course document's authored objective order, and two passes over the same unchanged document produce records that are equal after the volatile keys in director.PARITY_VOLATILE_KEYS are removed."
    - "TREAT-01 precision edge: no recommendation record field ever holds a floating-point number or a percentage. Confidence is one of the four closed tokens in graph.EDGE_CONFIDENCES, and a candidate carrying a numeric confidence is refused by the schema before any field is read."
  prohibitions:
    - statement: "A model-written rationale must not be presented, stored, or exported as if it were a passage from a source; synthesis is labeled at the point it is recorded, not at the point it is displayed."
      status: kept
      verification: flagged-unverified
    - statement: "A recommendation must not produce or cache a completion, mastery, readiness, or progress value of any kind, in any field, for an objective or for a course."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "director.py gains recommend_treatments, treatment_candidates, untreated_objectives, UNTREATED_REASONS, PARITY_VOLATILE_KEYS, and RECOMMENDATION_OUTCOMES"
    - "fixtures/corpus_14b.py gains build_recommendation_fixture and an objective with zero source bindings"
    - "tests/director_roundtrip.py gains check_treatment_vocabulary, check_direct_reading_complete, and check_recommendation_edges"
  key_links:
    - "director.untreated_objectives must read the course sidecar's bindings rows, never the recommendation records it produced. A recommendation is a proposal; only a bound row means an objective is treated. If the report reads its own proposals, an untreated objective disappears from the report the moment a recommendation is drafted, which is precisely the silent-generation failure TREAT-01 exists to prevent."
    - "The tie-break rule reads graph.TREATMENT_KINDS.index(kind). If director ever holds its own ordered copy of the eleven tokens, the tie-break silently diverges from the vocabulary the moment 14B's tuple order changes for any reason."
---

<objective>
Widen the one proven path from plan 15A-01 into the full TREAT-01 surface: a
recommendation pass over a whole course that gives every objective an explicit,
reviewable outcome, chosen from the closed eleven-kind vocabulary, with direct
reading as a complete result and generation never the automatic default.

The defect this closes is the one TREAT-01 names in plain words: an objective
with no chosen treatment must read as untreated, never silently generated. A
system that only records what it decided to build cannot tell you what it
decided not to build, and a course whose gaps are invisible is a course whose
gaps never get filled.

Decisions already made, cited, and never re-derived here:

- **REQUIREMENTS.md TREAT-01**, quoted: "Every objective has an explicit,
  reviewable treatment chosen from direct reading, excerpt, guided lesson,
  notes or terms, worked example, visual or demonstration, practice, formal
  test, assessment-first diagnostic, learner artifact, or human review; direct
  reading is a complete result and generation is never the automatic default...
  Degraded: an objective with no chosen treatment reads as untreated, never
  silently generated."
- **14B-03-PLAN.md Task 1 step 2**: `graph.TREATMENT_KINDS` is the eleven-token
  tuple in a fixed order, with a comment stating that "Phase 15A owns choosing
  a treatment while Phase 14B owns only the record shape". This plan is that
  choosing, and it adds no twelfth member and no second copy of the tuple.
- **14B-03-PLAN.md behavior block**: `course.bind_treatment` with
  `treatment_kind="direct-reading"` against a source whose `read` right is
  unknown refuses. Direct reading is a complete treatment result, not a free
  pass. This plan inherits that assertion rather than reproving it.
- **15A-01 Task 4**: `validate_recommendation` already refuses a twelfth
  treatment kind and an invalid candidate. This plan does not re-implement
  either; it builds the pass that calls them.
- **PLANNING-DIRECTIVES section 4** non-negotiables 2 and 4.

Decisions this plan makes and locks, so the executor never guesses:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| What happens when no backend answers | The objective stays untreated with reason `backend-unavailable`; no local heuristic invents a treatment | A treatment chosen with no model and no source reading is exactly the silent generation TREAT-01 forbids. AGENT-02's own degraded clause names "fallback to another registered backend or manual continuation", not local invention. |
| Tie-break between two equal-confidence candidates | The member earlier in `graph.TREATMENT_KINDS` order wins; the loser is kept in `alternatives` | Deterministic and readable from one place. Blending two kinds would produce a value outside the closed vocabulary; dropping the loser would hide a real alternative from the reviewer. |
| The untreated report's input | The course sidecar's `## Bindings` rows, never the recommendation records | A proposal is not a treatment. Reading proposals would make the gap report go empty the moment drafting starts. |
| Confidence representation | The four closed tokens of `graph.EDGE_CONFIDENCES`, never a number | The 2026-08-14 bake-in gate recorded in `AUDIT-REPORT-14A-2026-08-14.md` states that retrievability is never a percentage; the same discipline applies to a recommendation's confidence, and a closed token cannot be averaged into a false precision. |
| Where the empty treatment kind is allowed | Only on a recommendation record, never on a binding row | The empty string is a provider saying it has no recommendation. Binding it would create a treatment row that names no treatment. |

Purpose: make every objective's outcome explicit and reviewable.
Output: the full recommendation pass, the untreated report, and the five
TREAT-01 edge behaviors proven by fixture.
</objective>

<context>
@.planning/phases/15A-director-treatment-policy/15A-RESEARCH.md
@.planning/phases/15A-director-treatment-policy/15A-PATTERNS.md
@.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-03-PLAN.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.agents/skills/OPERATION-CONTRACT.md
</context>

## Artifacts this phase produces (plan 15A-02 share)

Added to `director.py`. Every symbol below is new in this phase.

- Constants: `UNTREATED_REASONS = ("no-recommendation", "backend-unavailable",
  "rights-not-granted", "reviewer-rejected", "no-source-bound")`,
  `RECOMMENDATION_OUTCOMES = ("bound", "untreated", "refused")`,
  `PARITY_VOLATILE_KEYS = ("elapsed_ms", "entry_id", "interaction_id",
  "operation_id", "provider", "timestamp")`.
- Functions: `treatment_candidates(record)`, `rank_candidates(candidates)`,
  `recommend_treatments(...)`, `untreated_objectives(doc)`,
  `parity_view(obj)`.
- New `DirectorError` codes: `director.empty_treatment_bind`.

Added to `fixtures/corpus_14b.py`:

- `build_recommendation_fixture(dest)` returning a dict describing the built
  course root, including the keys `course_root`, `objective_ids`,
  `unbound_objective_id`, and `source_object_ids`.

New test functions in `tests/director_roundtrip.py`:
`check_treatment_vocabulary()`, `check_direct_reading_complete()`,
`check_recommendation_edges()`.

No CLI command, no daemon route, no schema file, and no journal record type is
produced by this plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the closed eleven-kind pass, its ranking, and its tie-break</name>
  <files>director.py, fixtures/corpus_14b.py, tests/director_roundtrip.py</files>
  <read_first>
- `director.py` as it stands after plan 15A-01, in full: `DIRECTOR_CODES`,
  `RECOMMENDATION_KEYS`, `validate_recommendation`, `recommend_once`,
  `apply_recommendation`, and the module docstring's tier contract.
- `graph.py` as landed: `TREATMENT_KINDS`, `TREATMENT_RIGHTS`,
  `EDGE_CONFIDENCES`, `treatment_right`, and the comment above
  `TREATMENT_KINDS` naming Phase 15A as the owner of choosing.
- `fixtures/corpus_14b.py` as landed: `build_three_domains`, `build_all`,
  `revoke_right`, and the fixed-seed rule every generator in it follows.
- `tests/director_roundtrip.py` as it stands after plan 15A-01, for the
  `fail(msg)` helper and the `main()` wiring pattern.
- `.planning/phases/15A-director-treatment-policy/15A-DECISIONS.md`, both
  recorded sections, so any plan edit those answers forced is honored.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_treatment_vocabulary()` function, written before the code. Run and
confirm it fails.

Vocabulary boundary, both sides:

- `director` defines no tuple or list whose members equal
  `graph.TREATMENT_KINDS`; asserted behaviorally by monkeypatching
  `graph.TREATMENT_KINDS` to a two-member tuple in a copy of the module
  namespace and confirming `director.rank_candidates` then ranks against the
  two-member tuple. There is one vocabulary and `director` reads it.
- For each of the eleven members `k`, a candidate whose `treatment_kind` is `k`
  passes `director.validate_recommendation`.
- A candidate whose `treatment_kind` is `"flashcards"` raises `DirectorError`
  with code `director.unknown_treatment_kind`; a candidate whose
  `treatment_kind` is the empty string passes validation and yields a record
  whose `treatment_kind` is the empty string.
- `director.apply_recommendation` on a record whose `treatment_kind` is the
  empty string raises `DirectorError` with code
  `director.empty_treatment_bind`, writes nothing, and journals the refusal.

Ranking and tie-break:

- `director.treatment_candidates(record)` returns a list whose first member is
  the record's own `treatment_kind` and whose remaining members are the
  record's `alternatives`, each as a dict with the keys `treatment_kind` and
  `confidence`.
- `director.rank_candidates` sorts by confidence rank, where `"high"` outranks
  `"medium"` outranks `"low"` outranks `"unknown"`, and breaks a tie by
  `graph.TREATMENT_KINDS.index(treatment_kind)` ascending.
- Given two candidates `{"treatment_kind": "practice", "confidence": "medium"}`
  and `{"treatment_kind": "excerpt", "confidence": "medium"}`, the ranked list
  begins with `excerpt`, because `excerpt` is at index 1 and `practice` at
  index 6. Both candidates are present in the returned list; the loser is never
  dropped.
- Given the same two candidates in reversed input order, the ranked list is
  identical. Input order never decides a tie.
- `director.rank_candidates([])` returns `[]` and raises nothing.
- Two candidates with the same `treatment_kind` and the same `confidence`
  collapse to one entry in the ranked list; a duplicate is not two
  alternatives.

Precision, the closed-token rule:

- Every `confidence` value on a validated record and on every member of its
  `alternatives` is a member of `graph.EDGE_CONFIDENCES`.
- A candidate whose `confidence` is the number `0.8` is refused by
  `director.validate_recommendation` with code
  `director.recommendation_invalid`, and the refusal happens before any other
  field is read, proven by also giving that candidate an unknown treatment kind
  and asserting the raised code is `director.recommendation_invalid` and not
  `director.unknown_treatment_kind`.
- No value anywhere in a validated record, at any nesting depth, is an instance
  of `float`, asserted by a recursive walk in the test.
  </behavior>
  <action>
1. Add `check_treatment_vocabulary()` to `tests/director_roundtrip.py` first,
   wired into `main()`, with every assertion above. Run
   `python tests/director_roundtrip.py` and confirm it fails.

2. Add `build_recommendation_fixture(dest)` to `fixtures/corpus_14b.py`. It
   builds one course root by calling the existing `build_three_domains`
   generator for its first domain, then adds four objectives in this authored
   order with these exact statements, all fictional:
   `Describe the meridian field response intake sequence.`,
   `Classify a lantern computing loop by its termination condition.`,
   `Solve an orrery algebra system by elimination.`, and
   `Summarize the meridian field response handoff record.` The fourth objective
   gets no source binding at all and its id is returned under the key
   `unbound_objective_id`. It registers two sources through `journal.op_link`,
   one with `transform` granted and one with all seven rights `unknown`.
   Everything is generated from the same fixed seed the existing generators use
   so a rebuild is byte-identical. No real course, book, learner, or bank
   content of any kind.

3. Add to `director.py` the constant
   `PARITY_VOLATILE_KEYS = ("elapsed_ms", "entry_id", "interaction_id",
   "operation_id", "provider", "timestamp")`, sorted, with a comment stating
   that these are the keys whose values differ between two runs of the same
   operation and that plan 15A-06's backend-parity assertion removes exactly
   these before comparing. Add `parity_view(obj)`, a pure recursive function
   that returns a copy of `obj` with every key in `PARITY_VOLATILE_KEYS`
   removed at every depth, leaving lists and scalars otherwise untouched.

4. Add `treatment_candidates(record)` to `director.py`: return
   `[{"treatment_kind": record["treatment_kind"], "confidence":
   record["confidence"]}] + list(record["alternatives"])`, with the first entry
   omitted when the record's `treatment_kind` is the empty string.

5. Add `rank_candidates(candidates)` to `director.py`. Build the confidence
   rank from `graph.EDGE_CONFIDENCES` by index, so `"high"` is rank 0 and
   `"unknown"` is rank 3, and never from a literal list in this module. Sort
   with the key `(confidence_rank, graph.TREATMENT_KINDS.index(kind))`, drop
   exact duplicates of `(treatment_kind, confidence)` while preserving the
   first occurrence, and return the list. Raise `DirectorError` with code
   `director.unknown_treatment_kind` for a candidate whose kind is not in the
   vocabulary. The function is pure and reads no file.

6. Add the code `director.empty_treatment_bind` to `DIRECTOR_CODES` with the
   exact message template `"the recommendation for objective %s names no
   treatment kind, so there is nothing to bind; the objective stays untreated
   with reason no-recommendation"`, and make `apply_recommendation` raise it
   before any rights lookup when the record's `treatment_kind` is the empty
   string, recording the refusal phase exactly as the rights refusal does.

7. Re-run `python tests/director_roundtrip.py` until it passes, then run
   `python itembank.py guard .` and confirm it reports `0 offending files`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Degraded state this task
proves: a candidate carrying a numeric confidence and a twelfth treatment kind
at once is refused by the schema first, so a malformed candidate never reaches
the vocabulary check and never produces a misleading refusal code.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import director; print(director.PARITY_VOLATILE_KEYS == tuple(sorted(director.PARITY_VOLATILE_KEYS)), len(director.PARITY_VOLATILE_KEYS))"`
  prints `True 6`.
- `python -c "import director,graph; c=[{'treatment_kind':'practice','confidence':'medium'},{'treatment_kind':'excerpt','confidence':'medium'}]; print(director.rank_candidates(c)[0]['treatment_kind'], len(director.rank_candidates(c)))"`
  prints `excerpt 2`.
- `python -c "import director; print(director.rank_candidates([]))"` prints `[]`.
- `python -c "import director; print('director.empty_treatment_bind' in director.DIRECTOR_CODES)"`
  prints `True`.
- `director.py` contains `def rank_candidates(` and `def parity_view(`.
- `fixtures/corpus_14b.py` contains `def build_recommendation_fixture(`.
- None of `director.py`, `fixtures/corpus_14b.py`, or
  `tests/director_roundtrip.py` contains an em dash character.
  </acceptance_criteria>
  <done>The eleven-kind vocabulary is read from one place, ranked
  deterministically, tie-broken by vocabulary order, and closed on both sides
  of its boundary.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: direct reading as a complete result, and the untreated report</name>
  <files>director.py, tests/director_roundtrip.py</files>
  <read_first>
- `director.py` as it stands after Task 1, in full.
- `course.py` as landed: `bind_treatment`, `read_course`, and the
  `bind_treatment` docstring's statement that the snapshot column is history
  and is never read back.
- `graph.py` as landed: `TREATMENT_RIGHTS`, in particular that
  `direct-reading` maps to `read` and `learner-artifact` and `human-review` map
  to `read`, while the eight generative kinds map to `transform` or `quote`.
- `REQUIREMENTS.md`, the TREAT-01 entry in full including its Fixture
  sentence.
- `tests/director_roundtrip.py` as it stands after Task 1.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_direct_reading_complete()` function, written before the code.

Direct reading is a complete result:

- `director.apply_recommendation` with a record whose `treatment_kind` is
  `"direct-reading"`, against a source whose `read` right is `granted`,
  succeeds and adds exactly one `## Bindings` row whose `treatment_kind` is
  `direct-reading`.
- After that bind, `director.untreated_objectives(doc)` does not list that
  objective id.
- A second `director.recommend_treatments` pass over the same course does not
  re-propose that objective: the returned list carries no entry whose
  `objective_id` equals it.
- Against a source whose `read` right is `unknown`, the same call raises
  `DirectorError` with code `director.rights_not_granted`, the message contains
  the string `read` and the string `unknown`, the sidecar bytes on disk are
  unchanged, and the objective is still listed by `untreated_objectives` with
  reason `rights-not-granted`. Direct reading is a complete treatment result,
  not a free pass.

The untreated report reads bindings, never proposals:

- `director.untreated_objectives(doc)` returns a list of dicts with the exact
  key set `{"objective_id", "statement", "reason"}`, in the document's authored
  objective order.
- Every returned `reason` is a member of `director.UNTREATED_REASONS`.
- On a freshly built fixture with zero treatment bindings, every objective is
  listed with reason `no-recommendation`.
- Drafting a recommendation without applying it changes the report by nothing:
  the report before and after `recommend_treatments` runs in recommend-only
  mode is equal.
- The fixture's `unbound_objective_id`, which has no source binding at all, is
  listed with reason `no-source-bound`, and that reason takes precedence over
  `no-recommendation`.

The three outcomes, and no fourth:

- `director.recommend_treatments` returns a list of dicts each carrying an
  `outcome` key whose value is a member of
  `director.RECOMMENDATION_OUTCOMES`.
- Summing the three outcome counts over one pass equals the number of
  objectives passed in. No objective is silently skipped.
- Every entry whose `outcome` is `bound` corresponds to exactly one new
  `## Bindings` row, and every entry whose outcome is `untreated` or `refused`
  corresponds to zero new rows.

Generation is never automatic:

- With the profile's command pointed at a path that does not exist, a full
  `recommend_treatments` pass over four objectives returns four entries, all
  with `outcome` equal to `untreated` and `reason` equal to
  `backend-unavailable`; `len(course.read_course(root)["doc"]["bindings"])` is
  unchanged; and the journal has grown by exactly one entry per objective.
- No code path in `director.py` produces a `treatment_kind` value that did not
  come from a validated provider candidate, asserted behaviorally: with the
  backend unavailable, every returned entry's `treatment_kind` is the empty
  string.
  </behavior>
  <action>
1. Add `check_direct_reading_complete()` to `tests/director_roundtrip.py`
   first, wired into `main()`, with every assertion above. Run and confirm it
   fails.

2. Add to `director.py` the constants
   `UNTREATED_REASONS = ("no-recommendation", "backend-unavailable",
   "rights-not-granted", "reviewer-rejected", "no-source-bound")` and
   `RECOMMENDATION_OUTCOMES = ("bound", "untreated", "refused")`, each with a
   comment naming TREAT-01 as its canonical source and stating that the
   vocabulary is closed.

3. Implement `untreated_objectives(doc)`. It reads `doc["objectives"]` and
   `doc["bindings"]` only. For each objective in authored order: if a
   `## Bindings` row exists whose `objective` matches and whose `binding_kind`
   is `treatment`, the objective is treated and is not listed. Otherwise it is
   listed, with `reason` chosen by this ordered rule, first match wins:
   no `## Bindings` row at all with that objective and `binding_kind` `source`
   gives `no-source-bound`; a recorded refusal in `doc["log"]` naming that
   objective and the string `rights` gives `rights-not-granted`; otherwise
   `no-recommendation`. The function is pure, reads no journal, and reads no
   recommendation record. Its docstring states in plain sentences that a
   proposal is not a treatment and that reading proposals here would empty the
   gap report the moment drafting began.

4. Implement `recommend_treatments(base, course_root, objective_ids, settings,
   profile_name, actor_kind, actor_name, actor_role, autonomy)`. For each
   objective id in the order given: call `recommend_once`; on a result whose
   `status` is not `"ok"`, append an entry with `outcome` `untreated`,
   `reason` `backend-unavailable`, `treatment_kind` the empty string, and the
   adapter code, and continue to the next objective without raising; on
   `"ok"`, rank the candidates, take the first, and if the autonomy level
   permits a write, call `apply_recommendation` inside a try that converts
   `DirectorError` with code `director.rights_not_granted` into an entry with
   `outcome` `refused` and `reason` `rights-not-granted`, and
   `director.empty_treatment_bind` into an entry with `outcome` `untreated`
   and `reason` `no-recommendation`. Return the list of entries, one per
   objective id, in the order given. The autonomy check in this plan is the
   placeholder `autonomy == "approved-bounded-write"`; plan 15A-04 replaces it
   with the policy-side check and this plan says so in a comment naming that
   plan.

5. Re-run `python tests/director_roundtrip.py` until it passes, then run
   `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Degraded states this task
proves: an unreachable backend produces four untreated entries, zero bindings,
and one journal entry per objective, so the failure is recorded rather than
silent; and a direct-reading recommendation against an unknown `read` right is
refused exactly as a generative kind would be.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import director; print(len(director.UNTREATED_REASONS), len(director.RECOMMENDATION_OUTCOMES))"`
  prints `5 3`.
- `director.py` contains `def untreated_objectives(` and
  `def recommend_treatments(`.
- `python -c "import director,inspect; print('evidence' not in inspect.signature(director.untreated_objectives).parameters and len(inspect.signature(director.untreated_objectives).parameters)==1)"`
  prints `True`.
- Neither `director.py` nor `tests/director_roundtrip.py` contains an em dash
  character.
  </acceptance_criteria>
  <done>Every objective in a pass reaches one of exactly three recorded
  outcomes, direct reading is one of them, and the gap report is computed from
  bindings rather than from proposals.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the empty, ordering, and stability edges</name>
  <files>director.py, tests/director_roundtrip.py</files>
  <read_first>
- `director.py` as it stands after Task 2, in full.
- `graph.py` as landed: `new_course`, `add_objective`, `outline_projection`,
  and the assertion in 14B-01 that an empty course projects to the single line
  `No objectives are recorded yet.`
- `tests/director_roundtrip.py` as it stands after Task 2.
- `.planning/phases/15A-director-treatment-policy/15A-RESEARCH.md`, the
  "Validation Architecture" section, for the sampling discipline this task's
  assertions follow.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_recommendation_edges()` function, written before the code.

Empty and single-element:

- `director.recommend_treatments(base, root, [], ...)` on a course with zero
  objectives returns `[]`, appends zero journal entries, and raises nothing.
  Confirmed by comparing `len(journal.entries(base))` before and after.
- `director.untreated_objectives` on a document built by
  `graph.new_course(...)` with zero objectives returns `[]`, never `None`.
- A single-objective course produces a one-entry list, and the entry's
  `objective_id` equals that objective's id.
- The fixture's `unbound_objective_id`, which has zero source bindings,
  produces a recommendation whose `treatment_kind` is the empty string and
  whose `coverage` `state` is `missing` and `match_kind` is `none`, and an
  entry whose `outcome` is `untreated`. No treatment is generated for an
  objective with no source.

Ordering and stability:

- Passing the four fixture objective ids in the document's authored order
  returns four entries in that same order.
- Passing the same four ids in reversed order returns four entries in the
  reversed order given. The function preserves the caller's order and does not
  impose its own.
- `director.untreated_objectives(doc)` always returns document authored order
  regardless of the order anything else ran in.
- Two consecutive `recommend_treatments` passes over the same unchanged
  document, both in recommend-only mode so neither writes, produce lists that
  are equal after `director.parity_view` is applied to each. Repeated runs are
  stable.
- `director.parity_view` removes every member of `PARITY_VOLATILE_KEYS` at
  every depth: given a nested dict carrying `timestamp` inside a list of dicts
  inside a dict, none of the six keys survives, and no other key is dropped.

No progress value anywhere:

- No key in any returned entry, at any depth, is named `mastery`,
  `completion`, `readiness`, `progress`, `percent`, or `score`, asserted by a
  recursive key walk in the test.
- No value in any returned entry, at any depth, is an instance of `float`.
  </behavior>
  <action>
1. Add `check_recommendation_edges()` to `tests/director_roundtrip.py` first,
   wired into `main()`, with every assertion above. Run and confirm it fails.

2. Make `recommend_treatments` return `[]` and append nothing when
   `objective_ids` is empty, before opening any operation. An operation with no
   work opens no operation.

3. Make `untreated_objectives` return `[]` for a document whose `objectives`
   list is empty, never `None`.

4. Make `recommend_once` build an empty `spans` list for an objective with no
   source bindings, and make the returned record's `coverage` carry `state`
   `missing` and `match_kind` `none` when the mock backend returns that shape.
   Do not add a special case that skips the backend call: the objective still
   goes through the one path, and the provider is the one that says it has no
   recommendation.

5. Confirm `parity_view` recurses through lists as well as dicts. If Task 1's
   implementation only recursed through dicts, fix it here and note the fix in
   the summary.

6. Re-run `python tests/director_roundtrip.py` until it passes. Then run the
   wave check: `python tests/scoring_roundtrip.py` and
   `python tests/evidence_roundtrip.py`, both expected to exit 0, the
   shipped-anchor spot check this project's validation strategy names. Then run
   `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Also run
`python tests/scoring_roundtrip.py` and `python tests/evidence_roundtrip.py`,
both expected exit 0. Degraded state this task proves: a course with zero
objectives opens no operation and writes no journal entry, so an empty pass
leaves no misleading record of work that did not happen.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python tests/scoring_roundtrip.py` exits 0.
- `python tests/evidence_roundtrip.py` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import director; print(director.parity_view({'a':[{'timestamp':1,'b':2}]}))"`
  prints `{'a': [{'b': 2}]}`.
- `tests/director_roundtrip.py` contains `def check_recommendation_edges(`.
- Neither `director.py` nor `tests/director_roundtrip.py` contains an em dash
  character.
  </acceptance_criteria>
  <done>The empty, single-element, ordering, and repeated-run edges are proven
  by fixture, and no recommendation record carries a float or a progress
  value.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| provider candidate to recommendation record | An untrusted model output becomes a structured proposal a reviewer reads. |
| recommendation record to binding row | A proposal becomes durable, rights-gated course state. |
| gap report to reviewer | The untreated report is what a reviewer trusts to know what the course is missing. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15A-02-01 | Tampering | `director.untreated_objectives` reading its own proposals | high | mitigate | The function takes exactly one parameter, the course document, and reads only `objectives`, `bindings`, and `log`. It cannot see a recommendation record because none is passed to it. Asserted by an introspection check on the signature plus the behavioral assertion that drafting without applying changes the report by nothing. |
| T-15A-02-02 | Spoofing | a provider naming a treatment kind outside the closed eleven | high | mitigate | `rank_candidates` raises `director.unknown_treatment_kind` for any candidate outside `graph.TREATMENT_KINDS`, and `validate_recommendation` already refused it at the schema. Two independent checks, one structural and one at the vocabulary. |
| T-15A-02-03 | Elevation of Privilege | direct reading treated as a rights-free treatment | high | mitigate | `direct-reading` maps to the `read` right in `graph.TREATMENT_RIGHTS` and goes through the same `apply_recommendation` gate as every other kind. Asserted against a source whose `read` right is unknown. |
| T-15A-02-04 | Repudiation | an objective silently skipped in a pass | medium | mitigate | `recommend_treatments` returns exactly one entry per objective id passed in, and the test sums the three outcome counts and compares to the input length. |
| T-15A-02-05 | Information Disclosure | a model rationale mistaken for a source passage | high | mitigate | The recommendation schema carries `synthesis` as `const true`, so a record structurally cannot claim to be a source passage, and the mock candidate's rationale states the same in its own text. The label is recorded, not applied at display time. |
| T-15A-02-06 | Tampering | a false-precision confidence or a progress value entering a record | medium | mitigate | Confidence is one of four closed tokens and a numeric confidence is refused by the schema before any field is read. The tests walk every record recursively and refuse any `float` value and any key named for mastery, completion, readiness, progress, percent, or score. |
| T-15A-02-07 | Information Disclosure | real course or learner content entering the repository through the new fixture | high | mitigate | `build_recommendation_fixture` writes only the four fictional objective statements this plan names verbatim, from the existing fixed seed, into a temp directory. `python itembank.py guard .` is in the acceptance criteria of all three tasks. |
| T-15A-02-08 | Tampering | supply chain: a ranking, scoring, or NLP dependency introduced here | high | mitigate | None is added; the ranking is a `sorted` call over two integer keys from `graph`'s own tuples. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is not itself the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-15A-02-09 | Denial of Service | a pathological candidate list making ranking quadratic or unbounded | low | accept | The candidate list is bounded by the recommendation schema's own shape and by the provider output cap the adapter already enforces. Accepted because the pass is a local, single-user, non-interactive operation with no concurrency requirement. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No coverage-state classification. The `coverage` block is carried through
  as the provider supplied it and validated by the schema; computing a
  `graph.BINDING_STATES` value from a locator is plan 15A-03's.
- No autonomy-level policy, no settings block. The autonomy check in this plan
  is an explicit placeholder that plan 15A-04 replaces, and the code says so.
- No egress minimization, no span caps, no approved-span authority. Plan
  15A-04 owns them.
- No protocol replay, no resume, no reverse. Plan 15A-05 owns them.
- No twelfth treatment kind, no second copy of the eleven-token tuple, no
  alias, no synonym table.
- No CLI command and no daemon route.
- No local heuristic recommender, no keyword matcher, no fallback that invents
  a treatment when no backend answers.
- No change to `graph.py`, `course.py`, `journal.py`, `identity.py`,
  `model_adapter.py`, or any schema file. This plan's whole diff is
  `director.py`, `fixtures/corpus_14b.py`, and `tests/director_roundtrip.py`.
- No evidence read of any kind. Evidence-based proposals are AGENT-03, owned by
  Phase 15B.
</out_of_scope>

<summary_obligations>
`15A-02-SUMMARY.md` records: the four fictional objective statements as landed;
whether `parity_view` needed the list-recursion fix in Task 3 and why; which
truth was verified by which command; the measured wall-clock time of one full
`tests/director_roundtrip.py` run; the exact behavior chosen when two
alternatives tie and both are also duplicates; and any deviation from this plan
with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15A-director-treatment-policy/15A-02-SUMMARY.md`
when done.
</output>
</content>
