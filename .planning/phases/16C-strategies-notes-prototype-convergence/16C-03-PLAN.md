---
phase: 16C-strategies-notes-prototype-convergence
plan: 03
type: execute
wave: 2
depends_on: ["16C-01"]
files_modified:
  - strategies.py
  - tests/strategy_registry_roundtrip.py
autonomous: true
requirements: [STRATEGY-01]
estimate:
  tokens: 60000
  raw_tokens: 60000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "Learning strategies are a finite registered set of exactly four, each a versioned data record declaring purpose, eligibility, required and optional learner actions, skip and resume, evidence effects, accommodations, offline behavior, and tests; strategies are never Python subclasses."
    - "An unavailable or disallowed strategy falls back to continuous reading, never an error: resolve_strategy returns the fallback for an unknown id, an unavailable id, and a disallowed id, and raises on nothing."
    - "The picker renders exactly three row classes (choosable, fallback, locked by a higher layer) from resolver output; it never invents an option and never renders a fifth strategy."
    - "Every declared evidence effect names only the D-16C-1 lifecycle vocabulary: the two additive event types and the strategy-action states, with at most a note ID reference, never note content."
    - "The registry's declared contracts carry the accessibility equivalent for every required learner action, so no strategy requires a drag-only, hover-only, or pointer-only action."
  prohibitions:
    - statement: "No Cartesian product of style toggles: one primary strategy plus at most one optional supplement per lesson step, requiredness at the activity level, and no global force-notes toggle."
      status: kept
      verification: flagged-unverified
    - statement: "No strategy may require a second parser, scorer, note truth, or UI state machine; that is the registry's kill criterion, recorded for the freeze."
      status: kept
      verification: flagged-unverified
    - statement: "strategies.py must not import runtime; a strategy influences selection and presentation, never scoring, disclosure, or evidence settlement."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "strategies.py with STRATEGY_IDS, FALLBACK_STRATEGY, STRATEGY_NAMES, STRATEGY_PURPOSES, STRATEGY_CONTRACTS, PICKER_HEADING, UNAVAILABLE_COPY, MID_SITTING_LOCK_COPY, resolve_strategy, strategy_contract, picker_rows"
    - "tests/strategy_registry_roundtrip.py green with its contract-completeness, fallback, and picker checks"
  key_links:
    - "resolve_strategy is the STRATEGY-01 degraded path and picker_rows consumes it; if the picker computed availability itself, two availability rules would exist and the fallback fixture would prove the wrong one."
    - "STRATEGY_CONTRACTS' evidence_effects fields are consumed by plan 16C-06's lifecycle event builder and asserted by plan 16C-09's tracer; a field named here in words 16C-06 cannot act on breaks the chain."
    - "picker_rows' locked row class carries copy that only plan 16C-05's composed resolver can produce (the 16B conflict sentence); this plan renders the row shape with the copy supplied as an argument, so one copy source exists."
---

<objective>
Register the finite strategy set as data: four strategies, one shared
contract shape, one code-owned fallback, and the picker row contract.

Decisions already made, cited, and never re-derived here:

- **16C-DECISIONS.md `## D-16C-4`**: the four registry members, the
  code-owned fallback, the runway for the remaining modes, no fifth strategy
  in 16C.
- **16C-DECISIONS.md `## D-16C-1`**: evidence effects name only the two
  lifecycle event types and the strategy-action states.
- **16C-DECISIONS.md `## D-16C-6`**: strategy-action-state naming.
- **16C-DECISIONS.md `## D8` (UI-SPEC)**: the three picker row classes;
  disallowed strategies are shown and explained, not hidden.
- **16C-UI-SPEC.md Strategy Picker Contract**: the heading, the four
  strategy names and one-line purposes, the unavailable copy, and the
  mid-sitting lock line, all transcribed verbatim below.
- **`subjects.py` D-01/D-02/D-03 (shipped)**: profiles are versioned data,
  never subclasses; the conservative fallback is code-owned and never
  replaced by settings data. The registry copies this exact shape.
- **REQUIREMENTS.md STRATEGY-01**, including its degraded contract: "an
  unavailable strategy falls back to continuous reading."

Purpose: the strategy registry every other 16C deliverable reads; the
precedence resolver (16C-05), the lifecycle events (16C-06), the prototype
tracers (16C-07), and the freeze gate (16C-09) all consume these records.
Output: one registry module and one green test.
</objective>

<context>
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-RESEARCH.md
@.planning/REQUIREMENTS.md
@subjects.py
@selection.py
@tests/subject_loop_roundtrip.py
</context>

## Artifacts this phase produces (plan 16C-03 share)

New symbols introduced by this plan, and by nothing earlier:

- `strategies.py`: `STRATEGY_SCHEMA_VERSION`, `STRATEGY_IDS`,
  `FALLBACK_STRATEGY`, `STRATEGY_NAMES`, `STRATEGY_PURPOSES`,
  `STRATEGY_CONTRACTS`, `PICKER_HEADING`, `UNAVAILABLE_COPY`,
  `MID_SITTING_LOCK_COPY`, `PICKER_ROW_CLASSES`, `resolve_strategy`,
  `strategy_contract`, `picker_rows`.
- `tests/strategy_registry_roundtrip.py` and its `check_*` functions.

Plan 16C-05 later adds `composed_resolve` to this module. The phase-wide
symbol union is repeated in `16C-01-PLAN.md`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the registry, the contracts, and the fallback</name>
  <files>strategies.py, tests/strategy_registry_roundtrip.py</files>
  <behavior>
    - `STRATEGY_IDS == ("continuous_reading", "guided_note_spine",
      "worked_reasoning", "retrieval_first")` and
      `FALLBACK_STRATEGY == "continuous_reading"`.
    - `strategy_contract("guided_note_spine")` returns a dict carrying every
      one of the eleven required contract keys with non-empty values.
    - `strategy_contract("close_reading")` raises `ValueError` naming the
      unknown id, because a silently tolerated unknown contract read would
      let a fifth mode ride in unregistered.
    - `resolve_strategy("worked_reasoning", available=("continuous_reading",),
      allowed=STRATEGY_IDS)` returns `"continuous_reading"`.
    - `resolve_strategy("retrieval_first", available=STRATEGY_IDS,
      allowed=("continuous_reading", "guided_note_spine"))` returns
      `"continuous_reading"`.
    - `resolve_strategy("not_a_strategy", available=STRATEGY_IDS,
      allowed=STRATEGY_IDS)` returns `"continuous_reading"` and raises
      nothing: the degraded path is a fallback, never an error.
    - `resolve_strategy("guided_note_spine", available=STRATEGY_IDS,
      allowed=STRATEGY_IDS)` returns `"guided_note_spine"`.
  </behavior>
  <read_first>
- `subjects.py` lines 1 to 60, the versioned-data registry and code-owned
  fallback shape this module copies.
- `16C-DECISIONS.md` `## D-16C-4`, `## D-16C-1`, `## D-16C-6`, in full.
- `16C-RESEARCH.md` Pattern 4 (the closed-vocabulary registry) and the
  report 12 section 10.1 contract-field list it quotes.
- `tests/subject_loop_roundtrip.py` lines 1 to 45, the test shell.
  </read_first>
  <action>
1. Create `strategies.py` at the repository root, importing nothing beyond
   the standard library (`copy` at most). It must not import `runtime`,
   `evidence`, `notes`, or anything from `surfaces/`. Module docstring:
   strategies are versioned data records, never subclasses (subjects.py
   D-01/D-02 precedent); the fallback is code-owned and never replaced by
   settings data (D-03 precedent); plus the D-16C-6 sentence distinguishing
   strategy-action states, lowercase activity, and the capitalized Activity
   view.

2. Define:

```
STRATEGY_SCHEMA_VERSION = 1
STRATEGY_IDS = ("continuous_reading", "guided_note_spine",
                "worked_reasoning", "retrieval_first")
FALLBACK_STRATEGY = "continuous_reading"
STRATEGY_NAMES = {
    "continuous_reading": "Continuous reading",
    "guided_note_spine": "Guided note spine",
    "worked_reasoning": "Worked reasoning",
    "retrieval_first": "Retrieval first",
}
STRATEGY_PURPOSES = {
    "continuous_reading": "Read straight through, with optional highlights and notes.",
    "guided_note_spine": "Prompted selection and restatement as you go.",
    "worked_reasoning": "Predict, explain, and self-check worked steps.",
    "retrieval_first": "Try questions first, then read what you missed.",
}
```

   The four purpose strings are the UI-SPEC Copywriting Contract rows,
   verbatim; a comment says they are locked and never re-worded.

3. Define `STRATEGY_CONTRACTS`, a dict over `STRATEGY_IDS` where every value
   carries exactly these eleven keys (the report 12 section 10.1 list, as
   locked by D-16C-4's registry):
   `strategy_id`, `version`, `learning_purpose`, `eligibility`,
   `required_actions`, `optional_actions`, `skip_resume`,
   `evidence_effects`, `accommodations`, `offline_behavior`, `tests`.
   Fill each with declarative data, not prose essays; the binding
   specifics per strategy:
   - **continuous_reading**: `eligibility` `"always"` (it is the fallback);
     `required_actions` empty tuple; `optional_actions`
     `("highlight", "add_note")`; `skip_resume`
     `"resumes at the last read heading; skipping is always allowed"`;
     `evidence_effects` `("activity_completed",)` with a comment that an
     abandoned reading emits nothing; `offline_behavior`
     `"fully available offline"`.
   - **guided_note_spine**: `required_actions`
     `("select_target", "restate_in_own_words")`; `optional_actions`
     `("add_question",)`; `skip_resume` `"each prompted block may be
     skipped as skipped_optional; resume returns to the first block without
     a strategy-action state of completed or skipped_optional"`;
     `evidence_effects` `("activity_completed", "activity_skipped")`;
     `offline_behavior` `"fully available offline"`.
   - **worked_reasoning**: `required_actions`
     `("predict_next_step", "explain_step", "self_check")`;
     `optional_actions` empty; `skip_resume` `"a step may be skipped as
     skipped_optional; resume returns to the first unresolved step"`;
     `evidence_effects` `("activity_completed", "activity_skipped")`;
     `offline_behavior` `"fully available offline"`.
   - **retrieval_first**: `eligibility` `"only where objective policy
     permits an assessment-first route (STRATEGY-01)"`; `required_actions`
     `("attempt_items_first",)`; `optional_actions` `("read_after",)`;
     `skip_resume` `"skipping the attempt falls back to continuous reading;
     resume returns to the unattempted items"`; `evidence_effects`
     `("activity_completed", "activity_skipped")` with the comment that item
     responses themselves flow through the shipped response events and the
     one scorer, never through this registry; `offline_behavior`
     `"fully available offline"`.
   - Every strategy's `accommodations` names the keyboard, touch, and
     screen-reader equivalent for each required action (for example
     `select_target` names the D13 structured block-choice list), so no
     required action is drag-only, hover-only, or pointer-only.
   - Every strategy's `tests` names `"tests/strategy_registry_roundtrip.py"`
     plus, for guided_note_spine and worked_reasoning,
     `"tests/note_trio_roundtrip.py"` (the plan 16C-07 prototype tracers).
   - Every `evidence_effects` member must be one of the two D-16C-1 event
     types; a comment states that lifecycle events carry at most a note ID,
     never note content.

4. Define `strategy_contract(strategy_id)`: returns a deep copy of the
   contract dict, raising `ValueError("unknown strategy: %r" % strategy_id)`
   for anything outside `STRATEGY_IDS`.

5. Define `resolve_strategy(requested, available, allowed)`: returns
   `requested` when it is a member of `STRATEGY_IDS` and of `available` and
   of `allowed`; otherwise returns `FALLBACK_STRATEGY`. Pure, no I/O, raises
   nothing. Docstring cites STRATEGY-01's degraded contract.

6. Create `tests/strategy_registry_roundtrip.py` in the shipped
   direct-execution shape with a local `fail(msg)`. Checks:
   - `check_registry_shape`: the behavior-block assertions on `STRATEGY_IDS`
     and `FALLBACK_STRATEGY`; every contract carries exactly the eleven keys;
     every `evidence_effects` member is in
     `("activity_completed", "activity_skipped")`; `strategy_contract`
     returns copies (mutating a returned dict does not change the module
     constant) and raises on `"close_reading"`.
   - `check_fallback`: every behavior-block `resolve_strategy` case, plus:
     for every member of `STRATEGY_IDS`, resolving it with `available` and
     `allowed` both equal to `STRATEGY_IDS` returns it unchanged.
   - `check_accessibility_equivalents`: for every strategy, every member of
     `required_actions` has a non-empty accommodations entry naming its
     keyboard path.
   - `main()` prints `STRATEGY REGISTRY: 3 passed, 0 failed`.

7. Run:

```
python tests/strategy_registry_roundtrip.py
```

   Expected: final line `STRATEGY REGISTRY: 3 passed, 0 failed`, exit 0.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/strategy_registry_roundtrip.py</automated>
Expected: final line `STRATEGY REGISTRY: 3 passed, 0 failed`, exit 0. The
degraded state this task proves is the fallback: an unknown, unavailable, or
disallowed strategy resolves to continuous reading and raises nothing.
  </verify>
  <acceptance_criteria>
- `python tests/strategy_registry_roundtrip.py` exits 0 with final line
  `STRATEGY REGISTRY: 3 passed, 0 failed`.
- All four contracts carry exactly the eleven keys; unknown ids raise; the
  fallback path never raises.
- `strategies.py` imports neither `runtime`, `evidence`, `notes`, nor
  anything from `surfaces`, asserted in the test via `ast` over the module
  source.
- The four purpose strings equal the UI-SPEC rows verbatim.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">The four strategy ids and the eleven
  contract keys are what 16C-05, 16C-06, 16C-07, and the freeze read;
  renaming one after registration is a breaking change for every consumer.</reversibility>
  <done>Four strategies exist as complete versioned data records with a
  code-owned fallback that never errors.</done>
</task>

<task type="auto">
  <name>Task 2: the picker row contract</name>
  <files>strategies.py, tests/strategy_registry_roundtrip.py</files>
  <read_first>
- `16C-UI-SPEC.md`, the Strategy Picker Contract in full: the three row
  classes table, the fixed strings, and the rules.
- `16C-DECISIONS.md` `## D8`.
- `strategies.py` as written by Task 1.
  </read_first>
  <action>
1. Add to `strategies.py`, transcribed verbatim from the UI-SPEC:

```
PICKER_HEADING = "How do you want to work through this?"
UNAVAILABLE_COPY = "{Strategy name} isn't available right now. Continuing with continuous reading."
MID_SITTING_LOCK_COPY = "Strategy changes are paused during a test sitting."
PICKER_ROW_CLASSES = ("choosable", "fallback", "locked")
```

2. Add `picker_rows(available, allowed, locked_copy_by_id=None)`:
   - Iterates `STRATEGY_IDS` in order and returns one row dict per strategy
     with keys `strategy_id`, `name`, `purpose`, `row_class`, `copy`,
     `preselected`.
   - `row_class` is `"choosable"` when the strategy is in both `available`
     and `allowed`; `"locked"` when it is not in `allowed` and
     `locked_copy_by_id` carries a sentence for it (the sentence becomes
     `copy`, supplied by the 16C-05 composed resolver, the only source of
     the 16B conflict copy); `"fallback"` when it is allowed but not
     available, with `copy` set to `UNAVAILABLE_COPY` with
     `{Strategy name}` replaced by the display name.
   - When any allowed strategy is unavailable, the `continuous_reading` row
     carries `preselected` True (the STRATEGY-01 degraded path made
     visible); otherwise the first choosable row is preselected.
   - A strategy not in `allowed` with no supplied locked copy still renders
     as `"locked"` with `copy` the empty string, and a comment cites D8:
     disallowed strategies are shown and explained, not hidden; the empty
     string case exists only until 16C-05 wires the resolver, and the 16C-09
     tracer asserts it never reaches a learner blank.
   - The function never returns a row whose `strategy_id` is outside
     `STRATEGY_IDS`: the registry is closed and the picker never invents an
     option.

3. Extend `tests/strategy_registry_roundtrip.py`:
   - `check_picker_rows`: with everything available and allowed, four
     choosable rows in registry order, first preselected, heading constant
     equals the UI-SPEC string verbatim. With `worked_reasoning` removed
     from `available`, its row reads `row_class` `"fallback"` with copy
     exactly
     `Worked reasoning isn't available right now. Continuing with continuous reading.`
     and the `continuous_reading` row is preselected. With
     `retrieval_first` removed from `allowed` and a supplied locked
     sentence, its row reads `"locked"` carrying that sentence verbatim.
     Assert no fifth row ever appears when a bogus id is passed inside
     `available`.
   - `check_mid_sitting_copy`: `MID_SITTING_LOCK_COPY` equals the UI-SPEC
     string verbatim; the constant exists for 16C-05's sitting lock and this
     plan wires no sitting logic.
   - Update `main()` to run five checks and print
     `STRATEGY REGISTRY: 5 passed, 0 failed`.

4. Run:

```
python tests/strategy_registry_roundtrip.py
python itembank.py guard .
```

   Expected: final line `STRATEGY REGISTRY: 5 passed, 0 failed`, exit 0;
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/strategy_registry_roundtrip.py</automated>
Expected: final line `STRATEGY REGISTRY: 5 passed, 0 failed`, exit 0. The
degraded state this task proves is the fallback row: an allowed-but-
unavailable strategy renders the exact unavailable sentence with continuous
reading preselected, never an empty shell and never an error.
  </verify>
  <acceptance_criteria>
- `python tests/strategy_registry_roundtrip.py` exits 0 with final line
  `STRATEGY REGISTRY: 5 passed, 0 failed`.
- The picker renders exactly the three row classes, never a fifth strategy,
  and the fallback case preselects continuous reading with the verbatim
  sentence.
- `PICKER_HEADING`, `UNAVAILABLE_COPY`, and `MID_SITTING_LOCK_COPY` equal
  the UI-SPEC strings verbatim.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Row-shape data over the Task 1
  registry; 17A renders it and can restyle freely without touching the
  contract.</reversibility>
  <done>The picker contract renders only what the resolver returns, explains
  every absent choice, and preselects the fallback when degradation is in
  effect.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| registry data to learner choice | The picker must offer only registered, allowed, available strategies; an invented row would offer a mode nothing implements. |
| strategy contract to evidence store | evidence_effects fields feed plan 16C-06's event builder; a content-bearing field named here would leak note text into the append-only log downstream. |
| strategy layer to runtime authority | A strategy is presentation and pacing; scoring, disclosure, and settlement stay with the runtime. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16C-03-01 | Elevation of Privilege | a strategy reaching scoring or disclosure | high | mitigate | strategies.py imports neither runtime nor evidence, asserted via ast in the test; retrieval_first's contract states item responses flow through the shipped response events and the one scorer. |
| T-16C-03-02 | Tampering | a fifth mode riding in unregistered | medium | mitigate | STRATEGY_IDS is a closed tuple; strategy_contract raises on unknown ids; picker_rows never emits a row outside the registry, asserted with a bogus id. |
| T-16C-03-03 | Spoofing | an unavailable strategy silently swapped without disclosure | medium | mitigate | The fallback row class carries the locked unavailable sentence verbatim and preselects continuous reading, so the degradation is visible, not silent. |
| T-16C-03-04 | Information Disclosure | note content named as an evidence effect | high | mitigate | check_registry_shape asserts every evidence_effects member is one of the two D-16C-1 lifecycle types. |
| T-16C-03-05 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; stdlib only. Per PLANNING-DIRECTIVES section 4a, any future dependency is vendored at a pinned version with a recorded checksum and a named license review. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No precedence resolution and no layer state: `composed_resolve` and every
  use of `ia.mode_layer_resolve` is plan 16C-05's. This plan supplies locked
  copy only through an argument.
- No evidence event, no event builder, no `import evidence`; plan 16C-06
  owns the lifecycle events the contracts name.
- No sitting logic; `MID_SITTING_LOCK_COPY` is a locked constant consumed by
  16C-05.
- No interactive surface, route, or CLI command; the picker contract is data
  plus fixtures, rendering is 17A's.
- No fifth strategy, no Close reading, no Minimal lesson as a separate mode;
  D-16C-4's runway stands.
- No per-widget settings, no global force-notes toggle, no strategy toggle
  matrix (report 12 section 10.4).
</out_of_scope>

<flagged_assumptions>
- **The contract field values beyond the locked copy are this plan's own
  declarative wording.** The eleven keys and the evidence-effect vocabulary
  are locked; the prose inside `skip_resume` and `eligibility` is reviewable
  wording with no behavior behind it until 16C-05 through 16C-07 consume it,
  and the tracers assert the behavior, not the prose.
- **The locked row's empty-copy interim state exists between this plan and
  16C-05.** It is named in the code comment and asserted closed by the
  16C-09 tracer, so it cannot silently ship to a learner surface.
</flagged_assumptions>

<summary_obligations>
`16C-03-SUMMARY.md` records: the final line of every verify command with
actual stdout; the eleven contract keys as shipped for each strategy; every
fallback case exercised and its result; confirmation the four purpose
strings, the heading, the unavailable copy, and the mid-sitting lock copy
match the UI-SPEC verbatim; and any deviation from this plan with its
reason.
</summary_obligations>

<output>
Create
`.planning/phases/16C-strategies-notes-prototype-convergence/16C-03-SUMMARY.md`
when done.
</output>
