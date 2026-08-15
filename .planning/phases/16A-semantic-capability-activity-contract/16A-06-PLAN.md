---
phase: 16A-semantic-capability-activity-contract
plan: 06
type: execute
wave: 6
depends_on: ["16A-05"]
files_modified:
  - model.py
  - capabilities.py
  - surfaces/lesson.py
  - fixtures/lesson_capability_corpus.py
  - tests/capability_stress_corpus_tracer.py
autonomous: true
requirements: [ACTIVITY-01]
estimate:
  tokens: 86000
  raw_tokens: 86000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Every activity declares all ten ACTIVITY-01 fields, purpose, cognitive demand, objective, stimulus or source, response schema, retry behavior, feedback and disclosure policy, evidence status, accessibility equivalence, and static fallback, in one ## ACTIVITIES preamble registry read through model._preamble_section and through no second section-boundary scanner."
    - "No ninth item type is minted: the response-schema column names one of the eight shipped forms, mc, multi, table, dnd, build, short, check, visual, or a form outside that set which is declared unsupported and falls back to its static equivalent, so ten purposes are served by the response forms that already exist."
    - "A declared feedback and disclosure policy describes what the runtime does and never decides it: rendering the same bank with every feedback cell rewritten to withheld_until_submit produces a byte-identical page and a byte-identical runtime.public_item result, which is the assertion that would go red the day a declaration quietly became an authority."
    - "Two ## ACTIVITIES rows naming the same item id are the lint error activity.duplicate_item; the parser keeps the first and reports the collision and never merges the two field sets (ACTIVITY-01 adjacency probe)."
    - "A bank with no ## ACTIVITIES section returns None from parse_activities, parses byte identically to before this plan, and lints clean; a section with a header row and no data rows returns an empty assets mapping with empty True and emits activity.empty_block as a warning, following terms.empty_block's shipped precedent (ACTIVITY-01 empty probe)."
    - "parse_activities returns rows in document order and never sorts by purpose, so two activities declaring the same purpose keep their authored order (ACTIVITY-01 ordering probe); and parse_activities called twice on an unchanged file returns equal dicts and writes nothing, because parsing is a pure read with no cache and no side effect (ACTIVITY-01 idempotency probe)."
    - "An unsupported response form falls back to its declared static equivalent on a real surface: a lesson whose inline check names an item whose activity declares a form outside the eight shipped types renders that activity's static_fallback text, and lint reports activity.unsupported_response_form as a warning rather than an error, because falling back is the declared behavior and not a defect."
    - statement: "If parse_activities is interrupted or run in parallel there is nothing durable to guarantee, because it is a read-only pure function with no cache and no write; an activity declaration never grants a scoring path, so a parse that stops mid-file cannot leave a partially authorized item (ACTIVITY-01 concurrency probe)."
      verification: backstop
  prohibitions:
    - statement: "A declared feedback, disclosure, retry, or evidence policy must not decide keyed disclosure or settle a score; the declaration is a description of what the runtime will do, and runtime.score_response, runtime.public_item, and evidence.append_event remain the only things that do it."
      status: kept
      verification: flagged-unverified
    - statement: "No flow, purpose, or declaration may compel learner highlighting or require a decorative block; semantic emphasis and activity purpose are author-provided orientation, per CAP-01's no-compelled-highlighting bake-in and CAP-02's no-decorative-block clause."
      status: kept
      verification: flagged-unverified
    - statement: "A ninth item type must not be minted for an activity purpose; ACTIVITY-01 warrants a new response form only when scoring semantics or response structure cannot be expressed safely, and none of the ten purposes needs one on its own."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "model.ACTIVITY_COLUMNS, model.ACTIVITY_PURPOSES, model.ACTIVITY_RETRY, model.ACTIVITY_FEEDBACK, model.ACTIVITY_EVIDENCE_STATES, model.RESPONSE_FORMS, model.parse_activities"
    - "model.LINT_CODES gains activity.duplicate_item, activity.empty_block, activity.item_unknown, activity.unknown_purpose, activity.demand_empty, activity.unknown_retry, activity.unknown_feedback, activity.unknown_evidence_state, activity.missing_static_fallback, activity.missing_a11y_equivalent, activity.unsupported_response_form"
    - "capabilities.activity_fallback"
    - "surfaces/lesson.py: the inline-check branch rendering an unsupported form's static fallback"
    - "fixtures/lesson_capability_corpus.py gains build_activity_set"
    - "tests/capability_stress_corpus_tracer.py gains scenario_activity_declarations and scenario_unsupported_response_form"
  key_links:
    - "The declared feedback policy and the runtime's actual disclosure are two different things that read like one thing. The byte-identity assertion under a rewritten feedback column is the only check that keeps them apart, because everything else about the declaration looks exactly like a policy that would be obeyed."
    - "ACTIVITY_EVIDENCE_STATES names what the shipped evidence store actually does, not what an assessment taxonomy says. Research stream 03's evidence-status column carries phrases like mixed and stronger evidence which describe an inference, not a stored state; adopting them would have created a vocabulary the evidence store cannot produce, and a state nothing can reach is a lie in a closed tuple."
    - "The cognitive demand column is free prose and not a closed tuple. Research stream 03 section 4.1 gives a per-purpose useful demand range of verbs rather than an enum, so a five-member Bloom-shaped tuple would have been this phase inventing a taxonomy the research deliberately did not fix. The check is non-empty, which is what can honestly be checked."
    - "The unsupported-form fallback renders through the shipped [!CHECK: id] slot rather than through a new block. The slot already resolves an item id and already has a no-session degraded path from plan 16A-04, so the fallback composes with an existing mechanism instead of adding a second place where an activity can appear."
---

<objective>
Give every activity the ten-field declaration ACTIVITY-01 requires, in the
authoring vocabulary research stream 03 established, without minting a ninth
item type and without letting a declaration become an authority.

ACTIVITY-01, quoted: "Every activity declares purpose, cognitive demand,
objective, stimulus or source, response schema, retry behavior, feedback and
disclosure policy, evidence status, accessibility equivalence, and static
fallback; existing response forms serve many purposes and a new item type is
warranted only when scoring semantics or response structure cannot be expressed
safely. Owner: author-bank and lesson-authoring. Durable object: activity
record. Authority: runtime for scored assessment. Degraded: an unsupported
response form falls back to its declared static equivalent."

Three things about this requirement decide the whole shape of the work.

The first is that ten purposes are served by eight existing response forms.
Research stream 03's summary matrix at section 4.1 lists prediction, noticing,
retrieval, explanation, comparison, diagnosis, practice, transfer, reflection,
and formal assessment, each with a range of suitable response families, and
every one of those families maps onto `mc`, `multi`, `table`, `dnd`, `build`,
`short`, `check`, or `visual`. An activity declaration is metadata beside a
shipped form, never a ninth form.

The second is that the declaration describes the runtime and does not instruct
it. A row saying `feedback: withheld_until_submit` is a statement about what the
runtime already does in that mode. It is not a lever. The one check that keeps
this honest is the byte-identity assertion in Task 3: rewrite every feedback
cell and prove nothing changed, on the page and in `runtime.public_item`'s
output. Plan 16A-09's adversarial suite attacks the same boundary from the other
side.

The third is what evidence status may say. Research stream 03's evidence-status
column carries phrases describing an inference, such as `mixed` and
`stronger evidence, but claim limited to sampled contexts`. Those are not states
the shipped evidence store can produce. The closed vocabulary here names what
`evidence.py` actually does, so every member is a state something can reach.

Decisions already made, cited, and never re-derived here:

- **`16A-DECISIONS.md` `## D-16A-2`**: which module owns the activity grammar.
  Under `option-a` it is `model.py`, beside `parse_sources` and `parse_media`.
- **`model._preamble_section`'s own docstring**: one boundary rule for every
  preamble registry. `parse_activities` calls it and writes no second scanner.
- **`REQUIREMENTS.md` `ACTIVITY-03`**, quoted, which this plan must not
  undermine: "The runtime alone scores, grants keyed disclosure, selects
  authoritative assessment behavior, and writes assessment evidence".
- **`REQUIREMENTS.md` `CAP-01`'s bake-in**, quoted: "no flow may compel learner
  highlighting".
- **The phase-shape constraint on visual scope**: no color, spacing,
  typography, motion, or token decision anywhere in Phase 16A.

Purpose: make an activity's purpose, demand, and degraded behavior authored
rather than assumed.
Output: one registry, five closed vocabularies, eleven lint codes, and one real
fallback surface.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PATTERNS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/REQUIREMENTS.md
@.planning/research/phase-16/03-question-activity-matrix.md
@model.py
@capabilities.py
@surfaces/lesson.py
@runtime.py
@tests/capability_stress_corpus_tracer.py
</context>

## Artifacts this phase produces (plan 16A-06 share)

New symbols introduced by this plan, and by nothing earlier:

- `model.ACTIVITY_COLUMNS` (eleven-member tuple)
- `model.ACTIVITY_PURPOSES` (ten-member tuple)
- `model.ACTIVITY_RETRY` (four-member tuple)
- `model.ACTIVITY_FEEDBACK` (five-member tuple)
- `model.ACTIVITY_EVIDENCE_STATES` (four-member tuple)
- `model.RESPONSE_FORMS` (eight-member tuple)
- `model.parse_activities`, `model.ACTIVITIES_UNCHECKED`
- Eleven new `model.LINT_CODES` members, listed in the frontmatter artifacts
- `capabilities.activity_fallback`
- `fixtures/lesson_capability_corpus.py`: `build_activity_set`
- `tests/capability_stress_corpus_tracer.py`:
  `scenario_activity_declarations`, `scenario_unsupported_response_form`

No CLI command, no daemon route, and no schema file is produced by this plan.
No new item type is produced by this plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the ## ACTIVITIES registry, its five closed vocabularies, and its parser</name>
  <files>model.py</files>
  <read_first>
- `.planning/research/phase-16/03-question-activity-matrix.md` section 4.1, the
  Summary matrix table, in full. Its ten purpose names are the authoring
  vocabulary this task transcribes, and its "Useful demand range" column is the
  reason cognitive demand is free prose rather than an enum.
- `.planning/REQUIREMENTS.md` `ACTIVITY-01` in full, including its Owner,
  Durable object, Authority, Degraded, and Fixture sentences.
- `model.py` lines 574 to 602, `_preamble_section` in full.
- `model.py` `parse_media` as landed by plan 16A-05, in full. This function is
  its sibling and copies its structure step for step.
- `model.py` lines 625 to 711, `parse_terms`, specifically `_terms_row_cells`
  and the `empty` key in its returned dict, which `activity.empty_block` mirrors.
- `model.py` lines 2176 to 2215, `LINT_CODES`, and `model.lint`'s signature at
  line 2864 with its `LESSON_UNCHECKED` and `TERMS_UNCHECKED` sentinels.
- `evidence.py`'s `response_event` and `mark_event`, enough to confirm which
  evidence states the store can actually produce. `ACTIVITY_EVIDENCE_STATES`
  names those and nothing else.
- `runtime.py` lines 44 to 99, `public_item`, for the eight item types
  `RESPONSE_FORMS` transcribes.
  </read_first>
  <behavior>
- `model.ACTIVITY_COLUMNS` equals the eleven-member tuple `("item", "purpose",
  "demand", "objective", "stimulus", "response_schema", "retry", "feedback",
  "evidence", "a11y_equivalent", "static_fallback")`.
- `model.ACTIVITY_PURPOSES` equals `("prediction", "noticing", "retrieval",
  "explanation", "comparison", "diagnosis", "practice", "transfer",
  "reflection", "formal_assessment")`.
- `model.ACTIVITY_RETRY` equals `("none", "unlimited", "until_correct",
  "mode_controlled")`.
- `model.ACTIVITY_FEEDBACK` equals `("immediate", "after_commitment", "staged",
  "withheld_until_submit", "non_evaluative")`.
- `model.ACTIVITY_EVIDENCE_STATES` equals `("not_recorded", "activity_trace",
  "scored_by_runtime", "pending_human_mark")`.
- `model.RESPONSE_FORMS` equals `("mc", "multi", "table", "dnd", "build",
  "short", "check", "visual")`.
- `parse_activities(bank_path)` returns `None` when the bank carries no
  `## ACTIVITIES` section.
- With a section present it returns a dict with exactly the keys `activities`,
  `order`, `duplicates`, `empty`, and `path`.
- `activities` maps each item id to a dict carrying exactly `ACTIVITY_COLUMNS`,
  with a missing trailing cell filling as the empty string rather than raising.
- `order` is a list of item ids in document order. It is never sorted, so two
  activities declaring the same purpose keep their authored order.
- `duplicates` lists item ids declared more than once, in first-seen order, and
  the first declaration wins.
- `empty` is `True` when the section exists and carries no data row, and `False`
  otherwise.
- `parse_activities` called twice on an unchanged file returns equal dicts and
  writes nothing. It opens the file for reading only; it has no cache, no
  module-level state, and no side effect.
- `parse_activities` never raises on any input, including a one-cell row, a
  twenty-cell row, a duplicate item id, and an item id naming no item in the
  bank.
  </behavior>
  <action>
1. Add the six closed vocabularies to `model.py` beside `GATE_VALUES` and
   `MEDIA_COLUMNS`, each a plain module-level tuple in `GATE_VALUES`'s shape,
   with the exact members listed in the behavior block above.

   Two of the six carry a comment stating why they are what they are, because
   both look arbitrary otherwise and a later reader will otherwise widen them by
   guess:
   - `ACTIVITY_EVIDENCE_STATES`: one line stating that these four are what
     `evidence.py` can actually produce, and that research stream 03's
     evidence-status column describes an inference rather than a stored state,
     so its phrasing is deliberately not adopted.
   - `RESPONSE_FORMS`: one line stating that these eight are the shipped item
     types, that ACTIVITY-01 warrants a ninth only when scoring semantics or
     response structure cannot be expressed safely, and that none of the ten
     purposes needs one on its own.

   Cognitive demand gets no tuple. Add a one-line comment where a tuple would
   have gone, stating that research stream 03 section 4.1 gives a per-purpose
   useful demand range of verbs rather than an enum, so the `demand` column is
   free prose validated as non-empty and nothing more.

2. Add `parse_activities(bank_path)` immediately after `parse_media`, following
   its structure step for step: an independent read, the chunk split at the
   first real question, `_preamble_section(head, "ACTIVITIES")`, row splitting
   through `_terms_row_cells`, positional mapping onto `ACTIVITY_COLUMNS`,
   first-registration-wins with a `duplicates` list, and a `None` return when
   the section is absent. Do not compile a section regex.

   Write the docstring in `parse_media`'s and `parse_sources`'s voice: an
   independent read for a different purpose, never called from `load()` or
   `parse_bank()`, changing neither's return shape, under the same preamble
   boundary rule, with a short row filling as empty strings so a malformed row
   is lint's problem and never a parse failure. Add one sentence stating that
   the returned `order` list is document order and is never sorted, and one
   stating that a declaration is metadata beside an item and grants no scoring
   path.

3. Add `ACTIVITIES_UNCHECKED` as a module-level sentinel beside
   `LESSON_UNCHECKED`, `TERMS_UNCHECKED`, and `MEDIA_UNCHECKED`, and extend
   `model.lint`'s signature with `activities=ACTIVITIES_UNCHECKED`, so a
   pre-16A caller that passes no activity data skips every activity check and
   its output is byte identical.
  </action>
  <verify>
  <automated>python tests/activity_declaration_check.py</automated>
Create `tests/activity_declaration_check.py` as part of this task, following
`tests/evidence_roundtrip.py`'s convention (shebang, standard library only,
`ROOT` plus `sys.path.insert`, a local `fail(msg)`). It asserts each of the six
vocabulary tuples equals its documented members; that `parse_activities` on
`fixtures/lesson_bank.md` returns `None`; that a temporary bank with a header
row and no data rows returns `empty` equal to `True`; that a temporary bank with
two rows naming the same item id returns one `duplicates` entry and keeps the
first row's field values; that `order` preserves document order for two rows
sharing a purpose; that two consecutive `parse_activities` calls on the same
file return equal dicts; and that a one-cell row, a twenty-cell row, and an item
id naming no item all parse without raising. It prints
`activity declarations ok` and exits 0 on success.
The degraded state this task must also prove is the absent-section path: assert
`parse_activities` returns `None` and that `model.lint` called with no
`activities` argument produces output byte identical to its pre-task output on
`fixtures/lesson_bank.md`.
  </verify>
  <acceptance_criteria>
- `python tests/activity_declaration_check.py` prints `activity declarations ok`
  and exits 0.
- `len(model.ACTIVITY_COLUMNS)` is `11`, `len(model.ACTIVITY_PURPOSES)` is `10`,
  `len(model.ACTIVITY_RETRY)` is `4`, `len(model.ACTIVITY_FEEDBACK)` is `5`,
  `len(model.ACTIVITY_EVIDENCE_STATES)` is `4`, and `len(model.RESPONSE_FORMS)`
  is `8`.
- `model.RESPONSE_FORMS` equals
  `('mc', 'multi', 'table', 'dnd', 'build', 'short', 'check', 'visual')`.
- `grep -c '_preamble_section(head, "ACTIVITIES")' model.py` reports `1`, and
  `parse_activities`'s body compiles no heading regex.
- `model.lint` called without an `activities` argument produces output byte
  identical to its pre-task output on `fixtures/lesson_bank.md`; capture both
  and diff.
- `python tests/lesson_roundtrip.py` and
  `python tests/model_surface_roundtrip.py` each exit 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="costly">The eleven column names and the five closed
  vocabularies become an authored content contract the moment a bank declares an
  activity. Rated costly rather than one-way because almost none of it is chosen
  here: the ten fields are ACTIVITY-01's own sentence, the ten purposes are
  research stream 03 section 4.1's matrix, and the eight response forms are the
  shipped item types. Only the column order and the four-member evidence-state
  tuple are this plan's, and no content outside this phase's corpus uses either
  yet. Renaming a purpose after real banks declare activities would be a content
  migration.</reversibility>
  <done>An author can declare all ten ACTIVITY-01 fields for an item, in one
  registry, through the one boundary rule, and a malformed declaration is a lint
  finding rather than a crash.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the eleven lint checks and the unsupported-form static fallback</name>
  <files>model.py, capabilities.py, surfaces/lesson.py</files>
  <read_first>
- `model.lint`'s media branch as landed by plan 16A-05, the closest analog for
  the activity branch's shape and message style.
- `model.py`'s `item.objective_unnamespaced` check, for the objective-namespace
  rule the activity `objective` column reuses rather than reinventing.
- `capabilities.py` in full as it stands after plan 16A-05.
- `surfaces/lesson.py` lines 1121 to 1160, `_callout_html`, specifically the
  `slug == "check"` branch as rewired by plan 16A-04 Task 3 to read its copy
  from the capability registry. The fallback paragraph is appended inside that
  branch.
- `surfaces/lesson.py`'s `_static_instructional_html` as landed by plan 16A-04.
- `.planning/REQUIREMENTS.md` `ACTIVITY-01`'s Degraded clause, verbatim.
  </read_first>
  <behavior>
- `model.lint` emits `activity.duplicate_item` as an error naming the item id,
  once per duplicate.
- `model.lint` emits `activity.empty_block` as a warning when the section exists
  and carries no data row, matching `terms.empty_block`'s shipped severity;
  check that code's severity in the shipped `lint` and match it.
- `model.lint` emits `activity.item_unknown` as an error when an activity row's
  item id matches no item in the bank.
- `model.lint` emits `activity.unknown_purpose`, `activity.unknown_retry`,
  `activity.unknown_feedback`, and `activity.unknown_evidence_state` as errors
  when the corresponding cell is outside its closed tuple.
- `model.lint` emits `activity.demand_empty`,
  `activity.missing_a11y_equivalent`, and `activity.missing_static_fallback` as
  errors when the corresponding cell is empty after stripping.
- `model.lint` emits `activity.unsupported_response_form` as a WARNING, not an
  error, when the `response_schema` cell is outside `RESPONSE_FORMS`. Falling
  back is the declared behavior ACTIVITY-01's Degraded clause names, so an
  unsupported form is a documented state and not a defect.
- `capabilities.activity_fallback(activity)` returns the activity's
  `static_fallback` string when its `response_schema` is outside
  `model.RESPONSE_FORMS`, and the empty string otherwise. It is pure and reads
  no file.
- A lesson whose `[!CHECK: <id>]` block names an item whose activity declares an
  unsupported form renders, inside the existing check container and after the
  existing no-session copy, one additional
  `<p class="capability-static">` carrying the escaped `static_fallback` text.
- The same lesson where the activity declares a supported form renders exactly
  the bytes it rendered before this task.
  </behavior>
  <action>
1. Add the eleven codes to `model.LINT_CODES` in one edit of the sorted set
   literal: `"activity.duplicate_item"`, `"activity.empty_block"`,
   `"activity.item_unknown"`, `"activity.unknown_purpose"`,
   `"activity.demand_empty"`, `"activity.unknown_retry"`,
   `"activity.unknown_feedback"`, `"activity.unknown_evidence_state"`,
   `"activity.missing_static_fallback"`,
   `"activity.missing_a11y_equivalent"`,
   `"activity.unsupported_response_form"`.

2. Add the activity branch to `model.lint`, beside the media branch. The exact
   message strings, which authoring agents and CI greps both read, are:
   - `BANK: activity.duplicate_item: item %s is declared more than once in ## ACTIVITIES; the first declaration is used`
   - `BANK: activity.empty_block: ## ACTIVITIES carries a header row and no declarations`
   - `BANK: activity.item_unknown: ## ACTIVITIES declares item %s, which is not an item in this bank`
   - `BANK: activity.unknown_purpose: item %s declares purpose %s, which is not one of the ten declared purposes`
   - `BANK: activity.demand_empty: item %s declares no cognitive demand; the demand column is free prose and must say something`
   - `BANK: activity.unknown_retry: item %s declares retry %s, which is not one of none, unlimited, until_correct, mode_controlled`
   - `BANK: activity.unknown_feedback: item %s declares feedback %s, which is not one of immediate, after_commitment, staged, withheld_until_submit, non_evaluative`
   - `BANK: activity.unknown_evidence_state: item %s declares evidence %s, which is not one of not_recorded, activity_trace, scored_by_runtime, pending_human_mark`
   - `BANK: activity.missing_static_fallback: item %s declares no static fallback; ACTIVITY-01 requires one because an unsupported response form falls back to it`
   - `BANK: activity.missing_a11y_equivalent: item %s declares no accessibility equivalence`
   - `BANK: activity.unsupported_response_form: item %s declares response form %s, which is not one of the eight shipped forms; the activity falls back to its declared static equivalent`

   Every one is an error except `activity.empty_block` and
   `activity.unsupported_response_form`, which are warnings.

   Reuse the existing objective-namespace rule for the `objective` column rather
   than writing a second one: if the shipped `item.objective_unnamespaced` check
   has a reusable helper, call it; if the rule is inline, extract nothing and add
   no activity-specific objective check, and record that decision in the summary
   so a later plan does not assume one exists.

3. Add `activity_fallback(activity)` to `capabilities.py`. It reads
   `model.RESPONSE_FORMS` through a function-local import of `model`, so
   `capabilities.py` gains no top-level dependency on the parser, and returns
   the activity's `static_fallback` or the empty string. It is pure: no file
   read, no global, no side effect. Add one sentence to the module docstring
   stating that this function reports which fallback text applies and never
   decides whether a learner may respond, which is the runtime's call.

4. Extend `_callout_html`'s check branch in `surfaces/lesson.py`. After the
   existing no-session paragraph, when `ctx` carries an `activities` mapping and
   the check's item id resolves to an activity whose
   `capabilities.activity_fallback` returns a non-empty string, append one
   `<p class="capability-static">` carrying that string HTML-escaped. When
   `ctx` carries no `activities` mapping, or the id does not resolve, or the
   fallback is the empty string, append nothing and the branch's bytes are
   unchanged.

   Thread the activity data in the same way plan 16A-05 threaded media: an
   `activities` keyword on `lesson_page` defaulting to `None`, placed after
   `media`, put into the render `ctx` under the key `activities`, and read by
   `cmd_lesson` and the daemon lesson route through
   `model.parse_activities(bank_path)`. `lesson_page` itself reads no file.

   Introduce no CSS rule, no color, no spacing value, and no token. The
   `capability-static` class already exists from plan 16A-04 and is unstyled by
   design.
  </action>
  <verify>
  <automated>python tests/activity_declaration_check.py</automated>
Expected: prints `activity declarations ok` and exits 0, now including the lint
assertions. Extend that file in this task with: one temporary bank per lint code
producing exactly that code and no other activity code; an assertion that
`activity.empty_block` and `activity.unsupported_response_form` land in the
warnings list and every other activity code lands in the errors list; and an
assertion that `capabilities.activity_fallback` returns the empty string for a
supported form and the declared text for an unsupported one. The degraded state
this task must also prove is the no-activities render path: render a bank
carrying a `[!CHECK:]` block with `activities=None` and confirm the output is
byte identical to the same render before this task.
  </verify>
  <acceptance_criteria>
- All eleven codes are members of `model.LINT_CODES` and
  `python tests/protocol_roundtrip.py` exits 0.
- `python tests/activity_declaration_check.py` exits 0.
- `activity.empty_block` and `activity.unsupported_response_form` appear in
  `model.lint`'s warnings list; the other nine appear in its errors list.
- `capabilities.activity_fallback` on an activity whose `response_schema` is
  `mc` returns the empty string; on one whose `response_schema` is
  `oral_explanation` it returns that activity's `static_fallback` text.
- `grep -cE "^import model|^from model" capabilities.py` reports `0`, proving
  the `model` import stayed function-local.
- Rendering a `[!CHECK:]` bank with `activities=None` produces bytes identical to
  the same render before this task.
- `python tests/lesson_roundtrip.py`, `python tests/gate_roundtrip.py`, and
  `python tests/daemon_roundtrip.py` each exit 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="costly">The eleven lint message strings are read by
  authoring agents and by CI greps, so rephrasing one breaks a consumer outside
  this file. The fallback rendering is additive and reversible.</reversibility>
  <done>Every malformed declaration has a named finding, an unsupported response
  form is a documented fallback rather than a defect, and the fallback text
  reaches a real surface.</done>
</task>

<task type="auto">
  <name>Task 3: the ten-purpose activity set and the declaration-is-not-authority proof</name>
  <files>fixtures/lesson_capability_corpus.py, tests/capability_stress_corpus_tracer.py</files>
  <read_first>
- `.planning/research/phase-16/03-question-activity-matrix.md` section 4.1, the
  Summary matrix, for the suitable response family each purpose maps onto. The
  fixture pairs each purpose with a shipped form that genuinely fits it rather
  than with an arbitrary one.
- `.planning/REQUIREMENTS.md` `ACTIVITY-01`'s Fixture sentence, verbatim: "a 16A
  synthetic activity set exercising each declared purpose over the existing
  response forms, including one unsupported response form that must fall back to
  its declared static equivalent".
- `fixtures/lesson_capability_corpus.py` in full as it stands after plan
  16A-05.
- `tests/capability_stress_corpus_tracer.py` in full.
- `runtime.py` lines 44 to 99, `public_item`, because the byte-identity proof in
  step 3 calls it directly.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`.
  </read_first>
  <action>
1. Add `build_activity_set(dest_dir)` to
   `fixtures/lesson_capability_corpus.py`, following the established shape:
   literal fictional content, no `random`, deterministic bytes, no em dash
   characters.

   The generated bank carries eleven items and an eleven-row `## ACTIVITIES`
   registry. Ten rows exercise the ten purposes, each paired with a response
   form research stream 03's matrix names as suitable for it, so the fixture is
   a demonstration of the mapping rather than a shuffle. Fill every one of the
   ten fields on every row with real fictional prose; no cell is a placeholder
   and none is the word `TODO`.

   The eleventh row declares `response_schema` as the literal string
   `oral_explanation`, a form outside `RESPONSE_FORMS`, with a
   `static_fallback` reading exactly
   `Say your answer out loud, then compare it to the worked explanation below.`
   Its item is referenced by a `> [!CHECK: <id>]` block in the lesson body so
   the fallback reaches the render path.

2. Add `scenario_activity_declarations()` to
   `tests/capability_stress_corpus_tracer.py`. It builds the activity set,
   parses it, and asserts:
   - `parse_activities` returns eleven activities and eleven `order` entries,
     with no duplicates.
   - Every activity dict's key set equals `model.ACTIVITY_COLUMNS`.
   - The ten supported rows cover all ten members of `ACTIVITY_PURPOSES` exactly
     once, so no purpose is missing and none is doubled.
   - Every one of the ten fields on every row is a non-empty string.
   - `model.lint` reports exactly one `activity.unsupported_response_form`
     warning naming `oral_explanation` and no other activity code.
   - `order` matches the registry's document order, checked against a literal
     expected list built in the fixture module and exported as a module-level
     constant, so the test compares against the fixture's own declared order
     rather than against a copy that can drift.
   - Two consecutive `parse_activities` calls return equal dicts.

3. Add `scenario_unsupported_response_form()`. It builds the same bank, renders
   the lesson with `activities` supplied, and asserts:
   - The render contains the literal string
     `Say your answer out loud, then compare it to the worked explanation below.`
   - Rendering with `activities=None` produces a page not containing that
     string, so the fallback is genuinely sourced from the declaration.
   - The declaration-is-not-authority proof, which is this scenario's most
     important assertion: build a second copy of the bank in which every
     `feedback` cell is rewritten to `withheld_until_submit` and every `evidence`
     cell to `not_recorded`, render both, and assert the two rendered pages are
     byte identical; then call `runtime.public_item` on the same item from both
     copies and assert the two returned dicts are equal. A declared policy that
     changed either output would be a second authority, and this is the check
     that would go red the day one appears.
   - No new item type was minted: assert that the set of `type` values across
     every parsed item in the bank is a subset of `model.RESPONSE_FORMS`.

4. Update `16A-VALIDATION.md`'s Per-Task Verification Map with three rows for
   plan 16A-06's tasks, naming `tests/activity_declaration_check.py`,
   `scenario_activity_declarations`, and `scenario_unsupported_response_form`,
   with a Status of `passing`.
  </action>
  <verify>
  <automated>python tests/capability_stress_corpus_tracer.py</automated>
Expected final line: `TRACER: 10 passed, 0 skipped, 0 failed`, exit code 0. The
degraded state this task must also prove is the declaration-is-not-authority
claim in step 3: the rewritten-feedback render and the original render must be
byte identical and `runtime.public_item` must return equal dicts for both.
  </verify>
  <acceptance_criteria>
- `python tests/capability_stress_corpus_tracer.py` exits 0 with the final line
  `TRACER: 10 passed, 0 skipped, 0 failed`.
- The generated activity set covers all ten members of `ACTIVITY_PURPOSES`
  exactly once across its ten supported rows.
- `model.lint` on the generated bank reports exactly one
  `activity.unsupported_response_form` warning and no other activity code.
- The rewritten-feedback render is byte identical to the original render, and
  `runtime.public_item` returns equal dicts for the same item from both copies.
- Every parsed item's `type` in the generated bank is a member of
  `model.RESPONSE_FORMS`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- `16A-VALIDATION.md` has three new filled rows naming plan `16A-06`.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="reversible">A fixture builder and two test scenarios.
  Both can be rewritten without migrating content or renaming a published
  surface.</reversibility>
  <done>Ten purposes are exercised over eight shipped response forms, one
  unsupported form falls back to its declared static equivalent on a real
  surface, and a declared policy is proven not to be an authority.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| activity declaration to runtime behavior | A declared feedback, retry, disclosure, or evidence policy reads exactly like an instruction the runtime obeys, and would be one if anything ever consulted it. |
| authored registry to lint and to renderer | Two consumers of one registry can disagree about what a malformed row means. |
| purpose taxonomy to item types | A ten-member purpose vocabulary invites a ninth item type per purpose that does not obviously fit an existing form. |
| fixture generator to repository | Eleven synthetic items and their declarations enter version control. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-06-01 | Elevation of Privilege | a declared feedback or disclosure policy becoming a second authority over what a learner sees | high | mitigate | Nothing in this plan reads the `feedback` or `evidence` column at render or score time, and Task 3 step 3 proves it by rendering a bank with every such cell rewritten and asserting byte identity of both the page and `runtime.public_item`'s output. Plan 16A-09 attacks the same boundary with a scripted agent. |
| T-16A-06-02 | Elevation of Privilege | a ninth item type minted for a purpose, creating a response form outside the one scorer's vocabulary | high | mitigate | `RESPONSE_FORMS` is the eight shipped types, an unsupported form is a warning with a declared fallback rather than a reason to add a type, and the tracer asserts every parsed item's `type` is a member of that tuple. |
| T-16A-06-03 | Tampering | a closed vocabulary naming a state nothing can produce | medium | mitigate | `ACTIVITY_EVIDENCE_STATES` names what `evidence.py` actually does, with a source comment stating why research stream 03's phrasing was not adopted, and `read_first` sends the executor to `evidence.py` to confirm before writing the tuple. |
| T-16A-06-04 | Tampering | a second section-boundary scanner drifting from `_preamble_section` | medium | mitigate | Task 1 requires the call and the acceptance criteria assert `parse_activities`'s body compiles no heading regex; `grep` counts the one call site. |
| T-16A-06-05 | Repudiation | an activity row whose fields are placeholders, so the declaration exists and says nothing | medium | mitigate | Eight of the eleven lint codes are emptiness or membership checks that fire on a blank or invented cell, and the tracer asserts every field on every fixture row is a non-empty string. The freeze-gate human review in plan 16A-10 reads the declarations for honesty, which is the part a grep cannot check. |
| T-16A-06-06 | Denial of Service | a malformed registry raising during parse | medium | mitigate | The behavior block names a one-cell row, a twenty-cell row, a duplicate id, and an unknown item id as cases that must not raise, and `tests/activity_declaration_check.py` exercises each. |
| T-16A-06-07 | Information Disclosure | real course or exam content entering the repository through an eleven-item fixture | high | mitigate | Every string in `build_activity_set` is a literal fictional constant with no `random` and no external read; `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion. |
| T-16A-06-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every change is standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- A ninth item type, for any purpose, for any reason. ACTIVITY-01 warrants one
  only when scoring semantics or response structure cannot be expressed safely,
  and no purpose in the matrix needs one on its own.
- Any change to `runtime.score_response`, `runtime.public_item`,
  `runtime.explain_payload`, `evidence.append_event`, or `evidence.mark_event`.
  This plan reads `runtime.public_item` in a test and changes nothing.
- Any code path that consults the `feedback`, `retry`, or `evidence` column at
  render or score time. The declaration is a description; Task 3's byte-identity
  assertion is what keeps it one.
- A closed vocabulary for cognitive demand. Research stream 03 deliberately
  gives a per-purpose verb range rather than an enum, and inventing a taxonomy
  here would be this phase deciding something the research left open.
- An activity-specific objective-namespace check, unless the shipped
  `item.objective_unnamespaced` rule already exposes a reusable helper. Task 2
  step 2 states the branch and requires it recorded either way.
- Any CSS rule for `.capability-static`. Phase 17A owns appearance.
- The registered output modes and the localization fixture set. Plans 16A-07 and
  16A-08 own them.
</out_of_scope>

<flagged_assumptions>
- **Four of ACTIVITY-01's five probe rows are resolved by this plan** as explicit
  criteria carried in `must_haves.truths`: adjacency as the duplicate-item
  refusal, empty as the absent-section `None` and the empty-block warning,
  ordering as document order never sorted, and idempotency as two equal parses
  with no write.
- **ACTIVITY-01's concurrency probe row is resolved as a backstop**, carried in
  `must_haves.truths` below as a structured entry. Parsing is a read-only pure
  function with no cache and no durable write, so an interruption or a parallel
  run has no durable failure mode to check explicitly; what can be stated and
  not cheaply proven is that an activity declaration never grants a scoring
  path, so a parse interrupted mid-file cannot leave a partially authorized
  item.
- **The eleven-column order is this plan's own choice**, following
  ACTIVITY-01's own sentence order with `item` prepended as the key. It is
  recorded here so a later phase can find the choice rather than assume it was
  required.
</flagged_assumptions>

<summary_obligations>
`16A-06-SUMMARY.md` records: the eleven `ACTIVITY_COLUMNS` and the five closed
vocabularies exactly as written; the severity chosen for `activity.empty_block`
and which shipped code was checked to match it; whether the shipped
objective-namespace rule exposed a reusable helper and what was done either way;
the ten purpose-to-response-form pairings the fixture used and the research
matrix row each came from; the result of the declaration-is-not-authority
byte-identity assertion, including the `runtime.public_item` comparison; the
tracer's final summary line verbatim; the two golden SHA-256 values as
re-verified; which truth was verified by which command with the command's actual
stdout; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-06-SUMMARY.md`
when done.
</output>
