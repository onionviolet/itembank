---
phase: 16C-strategies-notes-prototype-convergence
plan: 05
type: execute
wave: 3
depends_on: ["16C-03"]
files_modified:
  - strategies.py
  - tests/strategy_precedence_roundtrip.py
  - tests/mode_layer_roundtrip.py
autonomous: true
requirements: [STRATEGY-02]
estimate:
  tokens: 60000
  raw_tokens: 60000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "The composed resolver is a collector over 16B's one precedence function: composed_resolve gathers each layer's supplied state and calls ia.mode_layer_resolve per setting; no second precedence rule, ordering, or conflict sentence exists anywhere in 16C."
    - "A conflicting learner preference yields to the higher layer with the 16B copy verbatim: the rendered sentence comes from ia.mode_layer_conflict_copy and is never rebuilt from parts in this phase."
    - "A learner chooses only among allowed strategies: the picker's locked rows carry the resolver's conflict sentence, and a strategy disallowed by a higher layer is shown and explained, never offered."
    - "Runtime assessment behavior is never user-configurable during a sitting: with sitting_active, a learner-preference change to any strategy setting is refused with the locked mid-sitting sentence and the effective value is unchanged."
    - "The STRATEGY-02 conflict matrix (learner preference contradicted by an accommodation override and by an instructor policy) resolves each case toward the higher layer with the stated-reason copy, and the fixture extends 16B's CONFLICT_CASES rather than duplicating enforcement."
  prohibitions:
    - statement: "16C must not reimplement precedence: no function in this phase may order layers, compare layer indexes, or build a conflict sentence except by calling the 16B surface (16B D8, D-16B-12, 16C-DECISIONS D-16C-5)."
      status: kept
      verification: flagged-unverified
    - statement: "Nothing a lower layer states may change scoring, keyed disclosure, retries, or the formal-test pause; the two fixed layers are read as constants, never composed as opinions."
      status: kept
      verification: flagged-unverified
    - statement: "16B's conflict copy must never be re-worded, re-formatted, or partially substituted; the fixture asserts the rendered sentence equals the 16B function's output exactly."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "strategies.py gains composed_resolve and its layer-state input contract"
    - "tests/strategy_precedence_roundtrip.py green with the conflict matrix and the mid-sitting lock"
    - "tests/mode_layer_roundtrip.py's CONFLICT_CASES extended with the 16C strategy rows, still green"
  key_links:
    - "composed_resolve's layers_state argument is an explicit input dict (16C-RESEARCH Open Question 3's recommendation) so it is testable today with synthetic layer states and wires to real course records later without a signature change."
    - "The collector does the gathering; ia.mode_layer_resolve does the deciding. The moment composed_resolve compares layer names itself, two implementations of one contract exist, which is the exact drift Pitfall 10 names."
    - "picker_rows (16C-03) renders locked rows only from copy this resolver supplies; this plan closes the empty-copy interim state 16C-03 recorded."
---

<objective>
Compose 16B's locked seven-layer precedence contract into the live strategy
surface: a collector that gathers every layer's supplied state, calls the one
16B function per setting, feeds the picker its locked rows, and refuses
mid-sitting changes.

Decisions already made, cited, and never re-derived here:

- **16C-DECISIONS.md `## D-16C-5`**: the conflict copy transcription, the
  collector-not-reimplementation boundary, and the CONFLICT_CASES extension
  point.
- **16B-DECISIONS.md `## D8` and `## D-16B-12`** (verified live by 16C-01):
  16B ships the pure `mode_layer_resolve` over an explicitly supplied
  mapping; 16C ships the collector; one precedence rule, never two.
- **16C-DECISIONS.md `## D8` (UI-SPEC)**: the locked picker row carries the
  16B conflict copy verbatim; disallowed strategies are shown and explained.
- **REQUIREMENTS.md STRATEGY-02** in full, including the degraded contract
  "a conflicting preference yields to the higher layer with a stated reason"
  and the fixture sentence naming the conflict matrix.
- **16C-UI-SPEC.md Strategy Picker Contract**: the mid-sitting line
  "Strategy changes are paused during a test sitting." renders wherever the
  picker would otherwise appear during a formal sitting.

Purpose: the deferred half of 16B D8, closed, with the two phases provably
sharing one implementation and one fixture family.
Output: one collector function, one extended 16B fixture, one new green
test.
</objective>

<context>
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-RESEARCH.md
@.planning/REQUIREMENTS.md
@strategies.py
@surfaces/ia.py
@tests/mode_layer_roundtrip.py
@tests/strategy_registry_roundtrip.py
</context>

## Artifacts this phase produces (plan 16C-05 share)

New symbols introduced by this plan, and by nothing earlier:

- `strategies.py`: `composed_resolve`.
- `tests/strategy_precedence_roundtrip.py` and its `check_*` functions.
- New rows appended to `CONFLICT_CASES` in `tests/mode_layer_roundtrip.py`
  (the extension 16B's own comment reserves for Phase 16C).

The phase-wide symbol union is repeated in `16C-01-PLAN.md`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: composed_resolve, the collector over the one 16B function</name>
  <files>strategies.py, tests/strategy_precedence_roundtrip.py</files>
  <behavior>
    - `composed_resolve({"Strategy": {"learner_preference": "retrieval_first",
      "instructor_policy": "continuous_reading"}})` returns an `effective`
      mapping with `"Strategy"` equal to `"continuous_reading"` and one
      conflict entry whose `copy` equals
      `ia.mode_layer_conflict_copy("Strategy", "instructor_policy")` exactly.
    - `composed_resolve({"Strategy": {"learner_preference":
      "guided_note_spine"}})` returns that value with zero conflicts.
    - A layers_state entry carrying an unknown layer key propagates
      `ia.mode_layer_resolve`'s own `ValueError`; composed_resolve neither
      catches nor re-words it.
    - With `sitting_active=True`, a learner_preference request for any
      setting whose fixed-layer entry pins it is dropped, the effective
      value is the pinned one, and the returned `locks` list carries the
      mid-sitting sentence for that setting.
    - `composed_resolve({})` returns empty effective, empty conflicts,
      empty locks, and raises nothing.
  </behavior>
  <read_first>
- `surfaces/ia.py`, `mode_layer_resolve`, `mode_layer_conflict_copy`,
  `MODE_LAYERS`, and `MODE_LAYERS_FIXED`, in full as landed (the 16C-01
  precondition verified them against plan text; read the landed source, not
  the plan).
- `16C-DECISIONS.md` `## D-16C-5`, in full.
- `16C-RESEARCH.md` Open Question 3 and its recommendation, plus Pitfall 10.
- `strategies.py` as it stands after 16C-03, in particular `picker_rows`'
  `locked_copy_by_id` argument and `MID_SITTING_LOCK_COPY`.
  </read_first>
  <action>
1. Add `composed_resolve(layers_state, sitting_active=False)` to
   `strategies.py`, with `from surfaces import ia` imported at module level
   (the one new import; a comment cites 16C-01's precondition as the guard
   that verified it exists).
   - `layers_state` is a dict mapping a setting display name to a requests
     dict, the exact mapping shape `ia.mode_layer_resolve` takes; the
     docstring states this is the explicit-input contract from 16C-RESEARCH
     Open Question 3 so synthetic layer states test it today and 14B course
     records wire in later without a signature change.
   - For each setting, in sorted key order for determinism: when
     `sitting_active` is true and the requests dict contains
     `learner_preference` alongside any higher-layer request for the same
     setting, remove the `learner_preference` entry first and append
     `{"setting": name, "copy": MID_SITTING_LOCK_COPY}` to `locks`; a
     comment cites STRATEGY-02: runtime assessment behavior is never
     user-configurable during a sitting, and during a sitting a preference
     change does not even reach the resolver.
   - Call `ia.mode_layer_resolve(name, requests)` and collect its result.
     composed_resolve performs no layer comparison, no ordering, and builds
     no sentence: the result's `value`, `winning_layer`, `conflict`, and
     `copy` are used as returned.
   - Return `{"effective": {name: value}, "conflicts": [each result with
     conflict True, carrying setting, winning_layer, copy], "locks": [...]}`.
   - Docstring first paragraph: this is the collector half of 16B D8; the
     precedence rule lives in `surfaces/ia.py` and nowhere else; adding any
     layer logic here is the drift 16C-DECISIONS D-16C-5 forbids.

2. Add `locked_picker_copy(conflicts)` (three lines): builds the
   `locked_copy_by_id` mapping for `picker_rows` from conflict entries whose
   setting is the strategy setting, so the locked row sentence is the
   resolver's sentence and nothing else. This closes 16C-03's empty-copy
   interim state.

3. Create `tests/strategy_precedence_roundtrip.py` in the shipped
   direct-execution shape with a local `fail(msg)`. Checks:
   - `check_collector_shape`: every behavior-block case, including the
     empty-input case and the propagated `ValueError` for an unknown layer
     key.
   - `check_strategy_conflict_matrix`: the STRATEGY-02 fixture. Build the
     synthetic matrix: a learner preference of `retrieval_first`
     contradicted by (a) an accommodation override of `continuous_reading`
     and (b) an instructor policy of `guided_note_spine`, each as its own
     setting entry. Assert each resolves toward the higher layer, each
     conflict's `copy` equals `ia.mode_layer_conflict_copy` for that setting
     and winner exactly, and each rendered sentence contains no underscore
     and no internal layer key (the 16B substitution rule).
   - `check_mid_sitting_lock`: with `sitting_active=True` and a
     learner-preference change against a runtime-authority pin, the
     effective value is the pinned one, the locks list carries exactly
     `Strategy changes are paused during a test sitting.`, and the same
     call with `sitting_active=False` yields the normal conflict path
     instead; assert the two effective values and record both.
   - `check_no_second_implementation`: via `inspect.getsource`, assert
     `composed_resolve`'s source contains no reference to `MODE_LAYERS`
     other than none at all (it must not read the ordering), and that
     `strategies.py` defines no name matching `mode_layer`, `layer_order`,
     or `precedence_table` other than `composed_resolve` and
     `locked_picker_copy` themselves; the failure message names D8 and
     D-16C-5.
   - `check_picker_locked_rows`: feed `picker_rows` the matrix's conflicts
     through `locked_picker_copy` and assert a disallowed strategy's row is
     `"locked"` carrying the resolver's sentence verbatim.
   - `main()` prints `STRATEGY PRECEDENCE: 5 passed, 0 failed`.

4. Run:

```
python tests/strategy_precedence_roundtrip.py
python tests/strategy_registry_roundtrip.py
```

   Expected: final line `STRATEGY PRECEDENCE: 5 passed, 0 failed`, exit 0;
   then `STRATEGY REGISTRY: 5 passed, 0 failed`, exit 0.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/strategy_precedence_roundtrip.py && python tests/strategy_registry_roundtrip.py</automated>
Expected: `STRATEGY PRECEDENCE: 5 passed, 0 failed` then
`STRATEGY REGISTRY: 5 passed, 0 failed`, both exit 0. The degraded state
this task proves is the mid-sitting refusal: during a sitting a preference
change is refused with the locked sentence and the effective value does not
move.
  </verify>
  <acceptance_criteria>
- `python tests/strategy_precedence_roundtrip.py` exits 0 with final line
  `STRATEGY PRECEDENCE: 5 passed, 0 failed`.
- Every conflict sentence equals `ia.mode_layer_conflict_copy`'s output
  exactly; no sentence is built in `strategies.py`.
- `composed_resolve` reads no layer ordering and `strategies.py` defines no
  precedence-shaped name, asserted structurally with D8 named on failure.
- The mid-sitting lock holds with `sitting_active=True` and releases with
  `sitting_active=False`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A collector over an already-frozen 16B
  function; removing it restores 16C-03's state exactly.</reversibility>
  <done>Every layer's supplied state flows through the one 16B precedence
  function, conflicts carry the one locked sentence, and a sitting locks
  preference changes out.</done>
</task>

<task type="auto">
  <name>Task 2: extend 16B's conflict fixture, never duplicate it</name>
  <files>tests/mode_layer_roundtrip.py</files>
  <read_first>
- `tests/mode_layer_roundtrip.py` in full as landed, in particular
  `CONFLICT_CASES` and the comment above it stating that Phase 16C appends
  rows here rather than creating a second fixture.
- `16C-DECISIONS.md` `## D-16C-5`.
- `REQUIREMENTS.md` STRATEGY-02's fixture sentence.
  </read_first>
  <action>
1. Append exactly three rows to `CONFLICT_CASES` in
   `tests/mode_layer_roundtrip.py`, below the existing rows, with a comment
   line reading `# Phase 16C strategy rows (plan 16C-05): STRATEGY-02
   conflict matrix.`:

   - `("Learning strategy", {"learner_preference": "retrieval_first", "accommodation_override": "continuous_reading"}, "accommodation_override", "continuous_reading")`
   - `("Learning strategy", {"learner_preference": "retrieval_first", "instructor_policy": "guided_note_spine"}, "instructor_policy", "guided_note_spine")`
   - `("Change strategy during a test sitting", {"learner_preference": "guided_note_spine", "runtime_authority": "locked"}, "runtime_authority", "locked")`

   Change nothing else in the file: no existing row, no check function body,
   no copy constant. The existing checks iterate `CONFLICT_CASES`, so the
   three rows are exercised by the 16B suite as written.

2. Run the 16B suite beside the 16C one, the both-contracts rule from
   `16C-VALIDATION.md`'s sampling section:

```
python tests/mode_layer_roundtrip.py
python tests/strategy_precedence_roundtrip.py
python itembank.py guard .
```

   Expected: the mode-layer suite's final line reports its existing check
   count with 0 failed and exit 0 (the row count grew, the check count did
   not); then `STRATEGY PRECEDENCE: 5 passed, 0 failed`; then `0 offending
   files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/mode_layer_roundtrip.py && python tests/strategy_precedence_roundtrip.py</automated>
Expected: both exit 0, the mode-layer suite green over the extended
CONFLICT_CASES. The degraded state this task proves is the authority floor
on the new rows: the sitting-change row shows a learner preference losing to
runtime authority through 16B's own fixture machinery.
  </verify>
  <acceptance_criteria>
- `git diff tests/mode_layer_roundtrip.py` shows only appended rows and the
  one comment line inside `CONFLICT_CASES`; no other hunk.
- Both suites exit 0.
- The three appended rows resolve to `accommodation_override`,
  `instructor_policy`, and `runtime_authority` respectively.
- `python itembank.py guard .` reports `0 offending files`.
- No em dash character in the diff, verified with the `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Three fixture rows in an existing
  extension point; removing them restores the 16B fixture exactly.</reversibility>
  <done>One conflict fixture family covers both phases, and the STRATEGY-02
  matrix runs inside 16B's own machinery.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| learner preference to assessment behavior | A preference is user input that must never reach scoring, disclosure, retries, or the formal-test pause, and must not move anything mid-sitting. |
| collector to precedence rule | A collector that starts deciding becomes a second implementation nobody reviewed. |
| resolver output to picker copy | The locked row's sentence must be the resolver's sentence; a re-built sentence drifts from the 16B contract. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16C-05-01 | Elevation of Privilege | a learner preference changing assessment behavior during a sitting | critical | mitigate | sitting_active drops the preference before the resolver runs, the locks list carries the locked sentence, and the fixture's runtime_authority row proves the floor through 16B's own matrix machinery. |
| T-16C-05-02 | Tampering | a second precedence implementation growing in 16C | high | mitigate | check_no_second_implementation asserts composed_resolve reads no ordering and strategies.py defines no precedence-shaped name, naming D8 on failure. |
| T-16C-05-03 | Spoofing | a conflict sentence re-worded or key-leaking | medium | mitigate | Every rendered sentence is asserted equal to ia.mode_layer_conflict_copy's output with no underscore and no internal key. |
| T-16C-05-04 | Repudiation | a disallowed strategy silently hidden instead of explained | medium | mitigate | check_picker_locked_rows asserts the locked row renders with the resolver's sentence, per D8: shown and explained, not hidden. |
| T-16C-05-05 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; stdlib only. Per PLANNING-DIRECTIVES section 4a, any future dependency is vendored at a pinned version with a recorded checksum and a named license review. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No live-state reading: course records, accommodation records, and
  instructor policy records arrive as the explicit layers_state argument;
  wiring real 14B records is the named integration seam, not this plan.
- No change to `surfaces/ia.py`: the 16B surface is frozen and this phase
  only calls it.
- No new conflict sentence, no wording change, no second fixture file for
  conflicts.
- No settings key, route, or CLI command.
- No sitting detection: `sitting_active` is an argument; the runtime owns
  what a sitting is, and this plan does not reimplement that.
</out_of_scope>

<flagged_assumptions>
- **The mid-sitting drop happens before the resolver runs.** An alternative
  reading routes the preference through and lets runtime_authority win
  inside the resolver; both end at the same effective value. Dropping first
  is chosen so the locks list distinguishes "refused because sitting" from
  an ordinary conflict, which the picker's mid-sitting line needs; the
  fixture asserts both behaviors so the choice is visible.
- **The three appended CONFLICT_CASES rows assume the 16B fixture iterates
  its list generically.** 16C-01's precondition verified CONFLICT_CASES
  exists; if the landed iteration hard-codes a row count, the executor
  updates that count in the same commit and records the deviation.
</flagged_assumptions>

<summary_obligations>
`16C-05-SUMMARY.md` records: the final line of every verify command with
actual stdout; the rendered sentence for each conflict-matrix case, quoted;
the effective values with sitting_active true and false, side by side; the
structural-check result naming what was scanned; the exact rows appended to
CONFLICT_CASES; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16C-strategies-notes-prototype-convergence/16C-05-SUMMARY.md`
when done.
</output>
