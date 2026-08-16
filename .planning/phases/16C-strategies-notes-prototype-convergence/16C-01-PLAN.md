---
phase: 16C-strategies-notes-prototype-convergence
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/phases/16C-strategies-notes-prototype-convergence/16C-PRECONDITION.md
  - .planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
autonomous: false
requirements: [GRAPH-03, NOTE-01, NOTE-02, NOTE-03, STRATEGY-01, STRATEGY-02, UPGRADE-01, UPGRADE-02]
estimate:
  tokens: 55000
  raw_tokens: 55000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "Phase 16C writes no code that imports identity, journal, discovery, graph, course, course_package, capabilities, or surfaces.ia until a recorded precondition check has confirmed those modules exist on disk and that every constant this phase was planned against matches; a divergence halts the wave by name instead of surfacing as an ImportError or a silent vocabulary drift mid-task."
    - "All three freeze records this phase depends on, 14B-FREEZE.md, 16A-FREEZE.md, and 16B-FREEZE.md, are checked for their own frozen headings, and a file that carries a Freeze withheld heading counts as a failed check rather than as a present record."
    - "The three upstream precondition files' dated result lines are read as well as the freeze headings, because a present-but-wrong freeze resting on an unresolved divergence its own precondition recorded is a failure mode a heading check alone cannot see."
    - "Phase 13.9 is confirmed walked, because ROADMAP.md makes 14B's freeze conditional on the walking skeleton and 16C's own freeze is a 14B-or-later freeze; an unwalked skeleton is a divergence in 16C's transitive dependency."
    - "The shipped surface this phase composes is re-checked live before it is extended: evidence.KNOWN_EVENT_TYPES still has exactly fourteen members, EVENT_SCHEMA_VERSION is still 2, STYLE_CHECK_CATALOGUE still has exactly its ten dotted keys, parse_lesson and parse_terms still return their recorded key sets, and mark_event still refuses a non-human marker."
    - "The evidence-log additivity baseline is recorded as literal SHA-256 values and captured-view hashes before any 16C change exists, so plan 16C-06 proves the KNOWN_EVENT_TYPES extension additive by comparison rather than by promise."
    - "The sixteen UI-SPEC decisions D1 through D16 are transcribed into 16C-DECISIONS.md verbatim rather than re-litigated, and the eight further decisions this plan locks, D-16C-1 through D-16C-8, are recorded beside them so every later plan reads one file for its event split, its note format, its module names, its registry contents, its conflict copy, its naming rule, its trio input contract, and its closed vocabularies."
    - "The one decision Weibao holds, D-12.6-5's notes-placement and Evidence-prominence half, is surfaced as a blocking checkpoint with the recommended default named, never silently defaulted."
  prohibitions:
    - statement: "A failed precondition check must not be worked around by stubbing a missing module, by wrapping the import in a try or except, by continuing with a reduced check set, or by recording the divergence and proceeding anyway; the halt is the correct outcome."
      status: kept
      verification: flagged-unverified
    - statement: "An unanswered checkpoint must not receive a silent default; a decision recorded as chosen when nobody chose it is a false record of authority."
      status: kept
      verification: flagged-unverified
    - statement: "A decision the approved 16C-UI-SPEC already settled must not be reopened by a plan or an executor; transcription is the only permitted operation on D1 through D16."
      status: kept
      verification: flagged-unverified
  artifacts:
    - ".planning/phases/16C-strategies-notes-prototype-convergence/16C-PRECONDITION.md with its five named sections"
    - ".planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md carrying the transcribed D1 through D16, the locked D-16C-1 through D-16C-8, and the D-12.6-5 checkpoint record"
  key_links:
    - "The precondition check reads three freeze records, but 14B's own freeze is conditional on Phase 13.9 having been walked, so step 7 reads the 13.9 SUMMARY evidence directly rather than trusting any downstream freeze heading."
    - "16C-DECISIONS.md is read by every later 16C plan before its first task. A decision recorded here in words a plan cannot act on leaves the executor choosing after all, which is the exact failure PLANNING-DIRECTIVES section 5 exists to prevent."
    - "The evidence baselines recorded here are the only proof plan 16C-06's two new event types stayed additive. A baseline computed after a 16C edit makes every later additivity assertion pass for the wrong reason, which is why this plan runs first and touches no file outside .planning/."
    - "D-16C-5 transcribes 16B's conflict copy and names ia.mode_layer_resolve as the one precedence implementation. If step 4 finds the landed 16B string or signature differs from plan text, plans 16C-03 and 16C-05 must be re-read against 16B-FREEZE.md before execution."
---

<objective>
Do the two things that must happen before any Phase 16C module, vocabulary, or
fixture exists.

First, verify that Phases 14B, 16A, and 16B actually landed on disk with the
surface 16C was planned against, and halt by name if they did not.
`16C-RESEARCH.md`'s "Critical caveat" records that 16C sits three unexecuted
phases deep at planning time: `identity.py`, `journal.py`, `discovery.py`,
`graph.py`, `course.py`, `course_package.py`, `capabilities.py`, and
`surfaces/ia.py` all read MISSING at the repository root, no `*-FREEZE.md` of
any kind existed, and `.planning/phases/13.9-walking-skeleton/` held no
SUMMARY. Every 14A, 14B, 16A, and 16B signature this phase cites was read from
plan text, never from source. This check is one degree stricter than 16B-01's:
it distrusts three freeze records, reads three upstream precondition dated
result lines, and confirms Phase 13.9's A9 closure directly.

Second, write the phase's single decisions file. Sixteen decisions were
already settled by the checker-approved `16C-UI-SPEC.md` (D1 through D16,
all six checker dimensions PASS on 2026-08-15) and are transcribed verbatim,
never re-litigated. Eight more are locked by this plan because they are
choices an executor would otherwise make. The one decision Weibao holds,
D-12.6-5's placement half, is raised as the Task 2 checkpoint.

Decisions already made, cited, and never re-derived here:

- **PLANNING-DIRECTIVES section 4**, all five non-negotiables, in particular
  number 2 (exactly one parser, one scorer, one evidence store) and number 4
  (format changes are additive, proven by a byte-identical fixture and not by
  promise).
- **PLANNING-DIRECTIVES section 4a**, quoted: section 4.2 "forbids a
  **second** parser, scorer, or evidence store. It does not freeze the one
  parser's grammar." The two additive KNOWN_EVENT_TYPES members in plan
  16C-06 rest on that sentence and on section 4.4.
- **ROADMAP.md Phase 16C "Depends on"**, quoted: "All three are planned but
  not yet executed, so every signature this phase imports is read from plan
  text at planning time; the first 16C plan opens with a recorded
  precondition check that halts by name on any divergence, the same pattern
  plans 14B-01, 15A-01, 15B-01, 16A-01, and 16B-01 set, extended to check for
  `14B-FREEZE.md`, `16A-FREEZE.md`, and `16B-FREEZE.md` records and for Phase
  13.9's A9 closure, because 16C's own freeze is a 14B-or-later freeze and
  may not close before the walking skeleton is walked."
- **16B-UI-SPEC.md decision D8 and 16B-DECISIONS.md D-16B-12** (plan text,
  re-verified here): 16B ships the pure `mode_layer_resolve` over an
  explicitly supplied mapping; 16C ships the collector; one precedence rule,
  never two.
- **16C-UI-SPEC.md**, checker-approved 2026-08-15. Its Copywriting Contract
  and Decisions log are the binding source for every user-visible string in
  this phase.
- **STYLE-DISCIPLINE-16A-2026-08-14.md** (binding order): the trio prototype
  precedes every further output-mode registration.

Decisions this plan makes and locks, so the executor never guesses (the
PLANNING-DIRECTIVES section 5 bar). Task 1 transcribes each into
`16C-DECISIONS.md` verbatim under its own dated heading.

| ID | Open question | Locked answer | One-line rationale |
|---|---|---|---|
| D-16C-1 | Which strategy events are evidence and which are private note state (16C-RESEARCH Open Question 2) | The evidence store gains exactly two additive `KNOWN_EVENT_TYPES` members, `"activity_completed"` and `"activity_skipped"`. Each such event carries exactly the keys `schema_version`, `event_id`, `event_type`, `ts`, `session_id`, `strategy_id`, `action_state`, `note_ref`, `dedupe_key`, where `note_ref` is a note ID string or the empty string, and no other key. Never note text, never learner wording, never selected content. The content-bearing strategy events (`target_selected`, `content_composed`, `relation_added`, `representation_attached`, `note_revised`, and `source_checked`'s compared content) stay in the learner-owned note store as note revisions and sidecar records, deletable. Learner-artifact pending and settled evidence uses the shipped `mark` / `mark_proposal` machinery unchanged. `EVENT_SCHema_VERSION` stays 2 because no existing event's shape changes. | Deletable learner content inside an append-only store is a contradiction (report 12 section 11.2 versus the one evidence writer); lifecycle facts without content are the only evidence-safe projection of note activity, and `events()`'s skip-and-warn on unknown types (evidence.py:765) is the proven additive route. |
| D-16C-2 | Where do note files live and in what format (16C-RESEARCH Open Question 1) | One note document per course per learner surface: a coherent Markdown file `notes.md` plus a JSON sidecar `notes.md.json` carrying the report 12 section 9.1 machine record (targets, fingerprints, hashes, states). Stored in a learner note root declared through 16B's `approved_roots` settings key, defaulting to a `_notes/` directory beside the private bank, mirroring `_evidence/` (`evidence.EVIDENCE_DIRNAME` precedent). The sidecar is the machine truth for anchors; the Markdown is the human and export truth for wording. Both are written with the compare-and-swap discipline: write to `<path>.tmp`, then `os.replace`, the `runtime.write_session` shape. Reversible: a path and format choice behind one reader, `notes.read_note_document`. | FILE-01 names note directories as an approved-root class; evidence-beside-the-private-bank is the shipped residency precedent; report 12 section 9.1 permits Markdown plus sidecar and requires one canonical parser. D-12.6-5's IA-placement half stays held for Weibao at Task 2. |
| D-16C-3 | Module and file names | Five new root-level modules, runtime-tier peers per the evidence.py:12-16 placement rule: `notes.py`, `strategies.py`, `note_outputs.py`, `progress_claims.py`, `upgrade_audit.py`. New tests: `tests/note_schema_roundtrip.py`, `tests/note_promotion_roundtrip.py`, `tests/strategy_registry_roundtrip.py`, `tests/strategy_precedence_roundtrip.py`, `tests/progress_claim_roundtrip.py`, `tests/note_trio_roundtrip.py`, `tests/legacy_upgrade_roundtrip.py`, `tests/cross_subject_suite_tracer.py`. New fixture builder: `fixtures/note_strategy_corpus.py`. New schema: `schemas/note.schema.json`. None collides with the reserved-names table in `16C-PATTERNS.md` (`identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`, `course_package.py`, `sample_course.py`, `capabilities.py`, `surfaces/ia.py`, and the reserved 14A/14B/16B test and fixture names). | The 16A `capabilities.py` and 16B `surfaces/ia.py` precedents both put new pure vocabularies in their own module rather than growing `model.py`; a name collision with unexecuted plan frontmatter would make two phases claim one file. |
| D-16C-4 | The four-strategy registry contents (16C-RESEARCH Assumption A9) | `STRATEGY_IDS = ("continuous_reading", "guided_note_spine", "worked_reasoning", "retrieval_first")` and `FALLBACK_STRATEGY = "continuous_reading"`, code-owned and never replaced by settings data, the `subjects.DEFAULT_PROFILE` D-03 precedent. Report 12 section 10.2's remaining modes stay the catalog runway: Minimal lesson folds into continuous reading; Close reading stays deferred until provenance relocation works. No fifth strategy registers in 16C. | STRATEGY-01 names exactly this set; report 12 section 10.4's kill criterion (a mode requiring a second parser, scorer, note truth, or UI state machine is killed) is written into the freeze record by plan 16C-09. |
| D-16C-5 | The 16B conflict-copy transcription and the resolver boundary | The locked conflict copy is, verbatim and never re-worded: "{Setting name} is set by {higher layer name} for this course and can't be changed here." It renders only through `ia.mode_layer_conflict_copy` and `ia.mode_layer_resolve`; 16C's composed resolver is a collector that gathers each layer's live state and calls the one 16B function, never a second precedence implementation (16B D8, D-16B-12). STRATEGY-02's conflict fixture appends rows to `CONFLICT_CASES` in `tests/mode_layer_roundtrip.py`, the extension point 16B's own comment reserves, rather than writing a second fixture. | Two implementations of one precedence contract drift (16C-RESEARCH Pitfall 10); 16B-07 shaped its fixture list so 16C appends rows rather than duplicating enforcement. |
| D-16C-6 | The strategy-action-state naming rule (16C-RESEARCH Pitfall 6, UI-SPEC D15) | The per-action states `("not_started", "draft", "completed", "skipped_optional", "equivalent_completed", "needs_review")` are named **strategy-action states** in every string, fixture, module docstring, and test. "Activity view" (capitalized) means the 16B IA area for durable agent and maintenance jobs; "activity" (lowercase) means a learner task. Every 16C module docstring touching either carries the distinguishing sentence. | Three vocabularies share the word activity (16B's IA area, the ACTIVITY-* requirement family, report 12 section 8.1's action states); naming the third distinctly closes the collision before any fixture exists. |
| D-16C-7 | The trio's input contract (16C-RESEARCH Open Question 4) | The one parsed content instance is the pair of dicts `model.parse_lesson(path)` and `model.parse_terms(path)` return for one synthetic lesson, parsed exactly once. Typed concept relations are supplied by the fixture generator as explicit data, never a new inline grammar. Anchors target heading slugs through `model.lesson_slug` today; the upgrade to D-14A-2 component IDs is a named integration seam recorded in the 16C freeze, not a 16C code change. Concept-map edges derive from `[[term]]` refs plus the fixture-declared typed relations. | Keeps the prototype executable over the shipped parser and keeps the one-parser rule literal (STYLE-DISCIPLINE corollary: a semantic style is a validator plus a projection over the one parsed content model). |
| D-16C-8 | The closed vocabularies | Transcribed verbatim from report 12 and REQUIREMENTS.md, each a module-level tuple: epistemic roles `("quote", "learner_claim", "learner_question", "learner_example", "calculation", "diagram", "accepted_reference_link")`; strategy-action states per D-16C-6; relocation states `("resolved", "relocated_exact", "relocated_probable", "orphaned")` where `relocated_probable` requires review and is never auto-applied; note status `("draft", "learner_accepted", "disputed", "superseded", "deleted")`; target kinds `("source", "lesson_step", "media", "item_public", "concept")`; artifact kinds `("proof", "program", "diagram", "explanation", "project", "observation")`; authorship types `("learner", "authored")`. | Closed sorted vocabularies are the project-wide additive-registration discipline (`STYLE_CHECK_CATALOGUE`, `GATE_MODES`, `LINT_CODES`); transcription from the verified report 12 lines removes every executor judgment about spelling. |

Purpose: make the other eight plans transcription rather than judgment.
Output: one recorded precondition result and twenty-four recorded decisions
plus one checkpoint answer.
</objective>

<context>
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-RESEARCH.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-PATTERNS.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-VALIDATION.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/DECISIONS-12.6-REMAINING-2026-08-14.md
@.planning/STYLE-DISCIPLINE-16A-2026-08-14.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-01-PLAN.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-07-PLAN.md
</context>

## Artifacts this phase produces (plan 16C-01 share)

This plan creates no module, no vocabulary, no schema, no fixture, and no
test. It creates exactly two planning artifacts:

- `.planning/phases/16C-strategies-notes-prototype-convergence/16C-PRECONDITION.md`
- `.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md`

New symbols introduced by this plan: none.

The phase-wide symbol union, repeated in each later plan's own share section:

- **`notes.py`** (new root module, plans 16C-02 and 16C-06): constants
  `NOTE_SCHEMA_VERSION`, `NOTES_DIRNAME`, `EPISTEMIC_ROLES`,
  `STRATEGY_ACTION_STATES`, `RELOCATION_STATES`, `NOTE_STATUS`,
  `TARGET_KINDS`, `AUTHORSHIP_TYPES`, `ARTIFACT_KINDS`, `PROMOTION_STATES`,
  the anchor-state and promotion copy constants; functions `new_note_id`,
  `note_record`, `target_record`, `resolve_anchor`, `authored_prehighlight`,
  `write_note_document`, `read_note_document`, `request_review`,
  `review_promotion`, `delete_note`, `artifact_record`,
  `artifact_evidence_view`, `strategy_lifecycle_event`.
- **`strategies.py`** (new root module, plans 16C-03 and 16C-05): constants
  `STRATEGY_IDS`, `FALLBACK_STRATEGY`, `STRATEGY_NAMES`, `STRATEGY_PURPOSES`,
  `STRATEGY_CONTRACTS`, `PICKER_HEADING`, `UNAVAILABLE_COPY`,
  `MID_SITTING_LOCK_COPY`; functions `resolve_strategy`, `strategy_contract`,
  `picker_rows`, `composed_resolve`.
- **`progress_claims.py`** (new root module, plan 16C-04): constants
  `CLAIM_DIMENSIONS`, `DIMENSION_LABELS`, `MEMBERSHIP_CLASSES`,
  `RETENTION_STATE_WORDS`, `FILL_STATE_LEGEND`, `INDETERMINATE_COPY`,
  `PENDING_COPY`, `VERSION_SPLIT_COPY`, `ARIA_CONTRACT`; functions `claim`,
  `claim_text`, `claims_from_events`, `fill_state`, `render_claims_text`.
- **`note_outputs.py`** (new root module, plan 16C-07): constants
  `OUTPUT_MODES`, `MODE_NAMES`, `NOTE_OUTPUT_CHECKS`,
  `VALIDATOR_FAILURE_COPY`, `TEXTUAL_FALLBACK_LINE`; functions
  `content_instance`, `validate_mode`, `project_notebook_page`,
  `project_cornell`, `project_concept_map`, `render_mode`.
- **`upgrade_audit.py`** (new root module, plan 16C-08): constants
  `BASELINE_AUDIT_ITEMS`, `PLAN_TEXT_STAND_IN`, `AUDIT_HEADING`,
  `AUDIT_COMPLETION_LINE`, `DIFF_HEADING`, `COSMETIC_SKIP_COPY`,
  `CANNOT_EXPRESS_COPY`, `KEYED_HALT_COPY`, `KEYED_HALT_AFFORDANCES`;
  functions `baseline_audit`, `bounded_diff`, `keyed_meaning_delta`,
  `run_upgrade`.
- **`evidence.py`** (plan 16C-06): two additive `KNOWN_EVENT_TYPES` members,
  `"activity_completed"` and `"activity_skipped"`, and nothing else.
- **`schemas/note.schema.json`** (plan 16C-02).
- **`fixtures/note_strategy_corpus.py`** (plan 16C-02, extended by 16C-07):
  `SEED`, `SUBJECTS`, `build_subject_bank`, `build_all`, `typed_relations`,
  `build_note_set`, `revise_lesson`, `broken_trio_fixtures`.
- **`fixtures/legacy_pre135_bank.md`** (plan 16C-08).
- **`surfaces/cli.py`** (plan 16C-02): one additive note-document marker in
  the guard's corpus-marker check.
- The eight test files named in D-16C-3 and every `check_*` and `scenario_*`
  function on them.
- The planning artifacts `16C-PRECONDITION.md`, `16C-DECISIONS.md`,
  `16C-TRACER-REPORT.md`, `16C-REVIEW.md`, `16C-FREEZE.md`.

<tasks>

<task type="auto">
  <name>Task 1: verify Phases 14B, 16A, and 16B landed, record the additivity baselines, and write the decisions file</name>
  <files>.planning/phases/16C-strategies-notes-prototype-convergence/16C-PRECONDITION.md, .planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md</files>
  <read_first>
- `16C-RESEARCH.md`, the "Critical caveat" section, Pattern 1, Pitfall 1, and
  the Assumptions Log, in full. This task exists because of them.
- `16B-01-PLAN.md` Task 1, in full. This task copies its shape and adds the
  third freeze leg and the three dated-result-line legs.
- `16C-UI-SPEC.md`, the "Decisions & Reasoning Log" table in full. Its
  sixteen rows are transcribed verbatim by step 12.
- `16B-07-PLAN.md`, the behavior block and `CONFLICT_CASES` list, for the 16B
  surface step 4 asserts.
- `evidence.py` lines 30 to 92 (the constants) and 735 to 775 (`append_event`
  and `events`).
- `model.py` lines 447 to 500 (`lesson_slug`, `parse_lesson`), 625 to 660
  (`parse_terms`), 2250 to 2261 (`STYLE_CHECK_CATALOGUE`).
  </read_first>
  <action>
1. Check that the eight dependency modules 16C may reference import. Run:

```
python -c "import identity, journal, discovery, graph, course, course_package, capabilities; from surfaces import ia; print('modules present')"
```

   Expected stdout: `modules present`, exit code 0.

2. Check the frozen 14A journal surface 16C's note writes and upgrade
   journaling compose over. Run a single `python -c` that asserts, printing
   `14A surface matches` on success:
   - `journal.OBJECT_STATES` equals
     `("clean", "conflict", "interrupted", "missing", "unavailable")`.
   - `journal.ENTRY_STATES` equals `("prepared", "applied", "refused")`.
   - Every one of `journal.entries`, `journal.replay`, `journal.object_state`,
     `journal.undo`, and `journal.commit_operation` is callable.
   - `identity.OBJECT_KINDS` is a tuple containing both `"lesson"` and
     `"bank"`, and `identity.object_fingerprint` is callable.

   Then open `14A-FREEZE.md` and confirm its frozen-surface enumeration names
   the D-14A-2 keyed-content carve-out (no trailing-whitespace normalization
   for the `bank` and `lesson` kinds). Record `ok` or `divergent` with the
   quoted sentence. Plan 16C-08's keyed-meaning halt rests on this carve-out.

3. Check the frozen 16A surface. Run a single `python -c` that asserts,
   printing `16A surface matches` on success:
   - `capabilities.RENDERER_AVAILABILITY` equals
     `("available", "degraded", "unavailable")`.
   - `model.SEMANTIC_PROFILE_VERSION` equals `1`.
   - `len(lesson._CALLOUT_KINDS) >= 4` and every one of `"KEY"`, `"EXAMPLE"`,
     `"NOTE"`, `"WARNING"` is a member, where `lesson` is
     `from surfaces import lesson`.

   Then open `16A-FREEZE.md` and record whether its frozen surface names
   shared note or activity schema hooks (CAP-03). If it does, record their
   exact names in Deviations found so plans 16C-02 and 16C-06 compose with
   them rather than duplicating; if it does not, record `none published`.

4. Check the frozen 16B surface this phase composes. Run:

```
python -c "from surfaces import ia; assert ia.MODE_LAYERS == ('learner_preference', 'author_strategy', 'objective_constraint', 'accommodation_override', 'instructor_policy', 'runtime_authority', 'system_safety'); assert tuple(ia.MODE_LAYERS_FIXED) == ('runtime_authority', 'system_safety'); assert callable(ia.mode_layer_resolve) and callable(ia.mode_layer_conflict_copy); r = ia.mode_layer_resolve('Timed test mode', {'learner_preference': 'off', 'instructor_policy': 'on'}); assert r['winning_layer'] == 'instructor_policy' and r['conflict'] is True; print(r['copy'])"
```

   Expected stdout, exactly:
   `Timed test mode is set by your instructor's policy and can't be changed here.`

   Then confirm the 16C extension point exists:

```
python -c "import io; s = io.open('tests/mode_layer_roundtrip.py', encoding='utf-8').read(); assert 'CONFLICT_CASES' in s; print('16B conflict fixture present')"
```

   Expected stdout: `16B conflict fixture present`. A different conflict
   sentence, a missing `mode_layer_resolve`, or a missing `CONFLICT_CASES`
   list is a halt: plans 16C-03 and 16C-05 are written against exactly these.

5. Check that all three freeze records exist and are real freezes, not
   withholdings:
   - `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md`
     contains the literal heading `## Frozen at 14B`.
   - `.planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md`
     contains the literal heading `## Frozen at 16A`.
   - `.planning/phases/16B-ia-modes-recovery-contract/16B-FREEZE.md`
     contains the literal heading `## Frozen at 16B`.
   - None of the three contains the literal heading `## Freeze withheld`. A
     file carrying a withholding heading fails this check even if the frozen
     heading is also present.

6. Check what those freezes rest on, rather than trusting them. For each of
   `.planning/phases/14B-graph-course-package-prototype/14B-PRECONDITION.md`,
   `.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md`,
   and `.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md`:
   the file exists and its `## Dated result line` section contains a sentence
   stating that its phase may proceed. If any instead records unresolved
   deviations, that is a divergence: record it as
   `<phase> froze on an unresolved precondition divergence`. Also read
   `16B-PRECONDITION.md`'s `Deviations found` section; a non-empty section
   whose deviations lack recorded resolutions in a 16B summary is a
   divergence.

7. Confirm Phase 13.9's A9 closure directly:
   `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists. If it
   is absent while any of the three freeze headings is present, record the
   divergence as `13.9 unwalked behind a frozen dependency`.

8. Check that the shipped surface this phase composes is still what
   `16C-RESEARCH.md` read. Run:

```
python -c "import evidence, model; assert evidence.KNOWN_EVENT_TYPES == ('response', 'retraction', 'mark', 'day_tick', 'term_lookup', 'key_review', 'hint', 'selection', 'lesson_complete', 'cap_override', 'model_interaction', 'mark_proposal', 'visual_action', 'gate_skip'); assert evidence.EVENT_SCHEMA_VERSION == 2; assert sorted(model.STYLE_CHECK_CATALOGUE) == ['style.banned_hector', 'style.filler_phrase', 'style.forbidden_marker', 'style.forbidden_phrase', 'style.heading_cadence', 'style.open_with', 'style.order_before', 'style.require_marker', 'style.section_density', 'style.sentence_length']; L = model.parse_lesson('fixtures/terms_above_lesson_bank.md'); assert set(L) == {'source', 'body', 'intro', 'headings', 'error', 'detail'}; T = model.parse_terms('fixtures/terms_above_lesson_bank.md'); assert set(T) == {'terms', 'refs', 'ignored', 'empty', 'collisions'}; s = model.lesson_slug('A  B!'); assert s == 'a-b' and model.lesson_slug(s) == s; print('shipped surface matches')"
```

   Expected stdout: `shipped surface matches`, exit 0.

   Then confirm the human-only marker gate still holds. Run:

```
python - <<"EOF"
import evidence
try:
    evidence.mark_event("s", "i", "r", "e", True, marker="model")
    raise SystemExit("mark_event accepted a model marker; the gate regressed")
except ValueError:
    print("marker gate holds")
EOF
```

   Expected stdout: `marker gate holds`, exit 0.

9. Confirm the shipped suites this phase leans on are green and the guard is
   clean before any baseline is trusted. Run:

```
python tests/evidence_roundtrip.py
python tests/lesson_roundtrip.py
python itembank.py guard .
```

   Expected: exit 0, exit 0, and a final line `0 offending files`.

10. Record the evidence additivity baseline. This is the phase's only proof
    that plan 16C-06's two new event types stayed additive, so it is taken
    before any 16C change exists. Run:

```
python -c "import hashlib
for p in ('fixtures/selection_evidence.jsonl', 'fixtures/lesson_retention_events.jsonl', 'schemas/settings.schema.json'):
    print(p, hashlib.sha256(open(p, 'rb').read()).hexdigest())"
```

    Record all three `path sha256` lines verbatim. Then capture the parsed
    view those logs produce through the one reader:

```
python -c "import json, hashlib, evidence; caps = [list(evidence.capture_events(p)) for p in ('fixtures/selection_evidence.jsonl', 'fixtures/lesson_retention_events.jsonl')]; print([len(c) for c in caps]); print(hashlib.sha256(json.dumps(caps, sort_keys=True).encode('utf-8')).hexdigest())"
```

    Record both printed lines. Plan 16C-06 re-runs both commands after its
    `KNOWN_EVENT_TYPES` extension and asserts every value identical.

11. If any check in steps 1 through 9 fails, STOP. Write nothing else, create
    no module, and print exactly this line with the failing item substituted
    for `<item>`, then exit non-zero:

    `HALT 16C-01 precondition: Phase 14B, 16A, or 16B has not landed, its frozen surface differs from what Phase 16C was planned against, a dependency froze on an unresolved divergence, Phase 13.9 was not walked, or the shipped evidence, style, or lesson surface moved. Re-verify every 16C plan against 14B-FREEZE.md, 16A-FREEZE.md, and 16B-FREEZE.md before writing any code. Divergent or missing: <item>`

    Do not work around a failure by stubbing a missing module, by wrapping
    the import in a try or except, by continuing with a reduced check set, or
    by recording the divergence and proceeding anyway. A halt here is the
    correct outcome; it is what this task is for.

12. On success, create `16C-PRECONDITION.md` in this phase directory with
    exactly these five sections and nothing more:
    - **Why this check exists.** One paragraph citing `16C-RESEARCH.md`'s
      Critical caveat: every 14A, 14B, 16A, and 16B signature in the 16C
      research and pattern map was read from plan text, not from source, and
      16C sat three unexecuted phases deep when planned.
    - **What was checked.** The full list from steps 1 through 9, one line
      each, each marked `ok` or `divergent`, including the 14A carve-out
      sentence check and the 16A shared-schema-hook check.
    - **Additivity baseline.** The three `path sha256` lines and the two
      lines from step 10's second command, each on its own line, under the
      sentence: `Plan 16C-06 asserts the evidence surface unchanged for every
      pre-16C event against these values. A changed value means the event
      extension was not additive.`
    - **Deviations found.** Every place the landed 14A, 14B, 16A, or 16B
      surface differs from the plan text this phase was planned against, with
      the plan-text value and the landed value side by side. Write `none`
      when there are none. A non-empty section means plans 02 through 09 must
      be re-read against the three freeze records before execution.
    - **Dated result line.** The date, the verbatim stdout of steps 1, 2, 3,
      4, 8, and 10, and one sentence stating whether 16C may proceed.

13. Also on success, create `16C-DECISIONS.md` in this phase directory with
    these sections, in this order, and nothing more:
    - A one-paragraph header stating that this file is the single source of
      truth for every 16C event, note-format, module-name, registry, copy,
      naming, and vocabulary decision; that every later 16C plan reads it
      before its first task; and that Task 2 of this plan appends the
      `## D-12.6-5` heading below.
    - `## Transcribed from 16C-UI-SPEC.md (checker-approved 2026-08-15)`,
      then `## D1.` through `## D16.`, one dated heading each, each carrying
      the Decision cell and the Reasoning cell copied verbatim from the
      UI-SPEC's "Decisions & Reasoning Log" table. Use these exact headings:
      `## D1. Notes capture in Learn, review in Evidence`,
      `## D2. Save and submit are always two separate controls`,
      `## D3. Private by default, no capture-time privacy picker`,
      `## D4. Epistemic role is a required choice, My claim preselected`,
      `## D5. Learner wording in Paper voice inside role-labeled containers`,
      `## D6. Relocation chips, probable never auto-applied`,
      `## D7. Promotion review reuses the reviewer-acceptance vocabulary`,
      `## D8. The strategy picker renders three row classes`,
      `## D9. One claim row per dimension, no aggregate anywhere`,
      `## D10. ARIA contract for claims and the fill state`,
      `## D11. Trio validator failure renders a warn refusal plus plain Markdown`,
      `## D12. Upgrade audit-first ordering and the blocking keyed-meaning halt`,
      `## D13. Three equivalent anchor capture paths`,
      `## D14. Authored pre-highlighting is orientation, zero events, zero ownership`,
      `## D15. Strategy-action states naming rule`,
      `## D16. The delete confirmation states the evidence boundary honestly`.
      Do not re-argue, re-word, or extend any of the sixteen. Transcription
      is the only permitted operation on them.
    - `## Locked by plan 16C-01`, then `## D-16C-1.` through `## D-16C-8.`,
      one dated heading each, each carrying the locked answer and the
      one-line rationale transcribed verbatim from this plan's objective
      decision table. In D-16C-1's transcription correct the objective
      table's one typographical slip: the constant is `EVENT_SCHEMA_VERSION`.
    - `## Prohibition`, one paragraph: no 16C plan, executor, or reviewer may
      re-litigate D1 through D16 or D-16C-1 through D-16C-8; a change request
      against any of them is a new decision record, never an edit.

    No em dash characters anywhere in either file.
  </action>
  <verify>
  <automated>python -c "import io, sys; import identity, journal, capabilities, evidence, model; from surfaces import ia; assert journal.ENTRY_STATES == ('prepared', 'applied', 'refused'); assert evidence.KNOWN_EVENT_TYPES[-1] == 'gate_skip' and len(evidence.KNOWN_EVENT_TYPES) == 14; assert len(ia.MODE_LAYERS) == 7; p = io.open('.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md', encoding='utf-8').read(); assert '## D16.' in p and '## D-16C-8.' in p and '## Prohibition' in p; q = io.open('.planning/phases/16C-strategies-notes-prototype-convergence/16C-PRECONDITION.md', encoding='utf-8').read(); assert 'Dated result line' in q and 'Additivity baseline' in q; print('16C preconditions match')"</automated>
Expected: prints `16C preconditions match` and exits 0. The degraded state this
task must prove rather than paper over is the halt itself: if any assertion
fails, the run exits non-zero with the named HALT line and no file outside
`.planning/` is created. Confirm this by checking that `notes.py`,
`strategies.py`, `note_outputs.py`, `progress_claims.py`, and
`upgrade_audit.py` do not exist on disk at the end of a failed run.
  </verify>
  <acceptance_criteria>
- The step 1 command prints `modules present` and exits 0.
- The step 2 command prints `14A surface matches` and exits 0, and the 14A
  carve-out sentence is quoted in `16C-PRECONDITION.md` marked `ok` or
  `divergent`.
- The step 3 command prints `16A surface matches` and exits 0, and the 16A
  shared-schema-hook check is recorded as names or `none published`.
- The step 4 commands print exactly
  `Timed test mode is set by your instructor's policy and can't be changed here.`
  and `16B conflict fixture present`.
- All three freeze files exist, each contains its own `## Frozen at` heading,
  and none contains `## Freeze withheld`.
- All three `*-PRECONDITION.md` files exist and each `## Dated result line`
  states its phase may proceed.
- `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists.
- The step 8 command prints `shipped surface matches` and the heredoc prints
  `marker gate holds`.
- `python tests/evidence_roundtrip.py` and `python tests/lesson_roundtrip.py`
  exit 0 and `python itembank.py guard .` reports `0 offending files`.
- `16C-PRECONDITION.md` exists with all five named sections, and its
  Additivity baseline section carries three `path sha256` lines plus the two
  lines from step 10's second command.
- `16C-DECISIONS.md` exists and contains the literal headings `## D1.`
  through `## D16.`, `## D-16C-1.` through `## D-16C-8.`, and
  `## Prohibition`.
- Neither file contains an em dash character. Verify with the command below,
  which builds the character from its code point rather than embedding it, so
  the check is not invalidated by its own text. Expected stdout: `no em dash`.

```
python -c "import io, sys; D = chr(0x2014); base = '.planning/phases/16C-strategies-notes-prototype-convergence/'; bad = [p for p in (base + '16C-PRECONDITION.md', base + '16C-DECISIONS.md') if D in io.open(p, encoding='utf-8').read()]; sys.exit('em dash found in ' + ', '.join(bad)) if bad else print('no em dash')"
```

  Every later 16C plan reuses this same `chr(0x2014)` form for its own em
  dash check, for the same reason: a check that embeds the character it
  forbids reports itself.
- No file outside `.planning/` is created or modified by this task.
  </acceptance_criteria>
  <precondition>Phases 14B, 16A, and 16B have executed; `identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`, `course_package.py`, `capabilities.py`, and `surfaces/ia.py` exist with the surfaces frozen in `14B-FREEZE.md`, `16A-FREEZE.md`, and `16B-FREEZE.md`; and Phase 13.9 has been walked with `13.9-03-SUMMARY.md` recorded.</precondition>
  <reversibility rating="reversible">The two files record a check and transcribe decisions already made in this plan and in the approved UI-SPEC; nothing durable in the codebase is created and the check can be re-run at any time.</reversibility>
  <done>Either 16C is cleared to proceed with the evidence and the additivity
  baselines recorded, or the wave is halted with the divergence named.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 2: D-12.6-5, where notes live in the IA and how prominent Evidence is</name>
  <files>.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md</files>
  <read_first>
- `.planning/DECISIONS-12.6-REMAINING-2026-08-14.md`, the `### D-12.6-5`
  section in full, including its three placement options, its Evidence
  prominence options, its recommendation, and its `Resolved: pending` line.
- `16C-UI-SPEC.md` Decision D1, which adopted recommendation C as the
  reversible default and recorded that the final resolution is held for
  Weibao.
- `16C-RESEARCH.md` Assumption A8, which records the same posture and why the
  note schema is placement-agnostic.
- `16C-DECISIONS.md` as written by Task 1, so the new section is appended
  below `## Prohibition` rather than overwriting anything.
  </read_first>
  <decision>
Two presentation questions Weibao explicitly holds (D-12.6-5, recorded
`Resolved: pending`): (1) where learner notes live by default in the IA, and
(2) whether the Evidence view is a primary navigation item or one level down.
Phase 16C's schemas and fixtures are placement-agnostic either way; this
checkpoint records the product answer so 17A renders against a decision
rather than a default.
  </decision>
  <context>
The note capture and review contracts in the checker-approved `16C-UI-SPEC.md`
were written against recommendation C as a reversible default: capture in
place at the anchor inside Learn, review in the Notes panel inside Evidence,
the cross-course global destination backburnered. D-12.6-5's own
recommendation adds that Evidence should be a primary navigation item because
the honest-evidence stance is a product differentiator. Both are daily-feel
choices, not correctness choices, which is exactly why the record says Weibao
should confirm them and why no agent may silently default them.
  </context>
  <options>
    <option id="option-a">
      <name>Margin-first notes</name>
      <pros>Notes render beside or beneath the anchored lesson block; the
      course-level list is a derived view. Strongest reading context.</pros>
      <cons>Weakest for review across lessons; the review home the UI-SPEC
      contracts (Notes panel inside Evidence) becomes secondary.</cons>
    </option>
    <option id="option-b">
      <name>Course-notes-first</name>
      <pros>Notes live in a course notes surface; lessons show anchor
      indicators that jump there. Best for review.</pros>
      <cons>Adds a navigation hop at capture time, against the capture-friction
      decisions D3 and D4 already locked.</cons>
    </option>
    <option id="option-c">
      <name>RECOMMENDED DEFAULT: margin capture, course review (recommendation C), with Evidence as a primary navigation item</name>
      <pros>Capture happens in place at the anchor; the Notes panel inside
      Evidence is the review home and durable listing; Evidence sits beside
      Learn, Practice, and Test in primary navigation. This is D-12.6-5's own
      recommendation, the posture the approved UI-SPEC D1 already contracts,
      and the reading the 16C plans and fixtures were written against.</pros>
      <cons>Two homes for one object class (capture surface and review
      surface), which a learner must learn once.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and ask the Evidence-prominence half explicitly: primary
navigation item, or one level down inside Review. Record the answer verbatim
in `16C-DECISIONS.md` under a dated heading
`## D-12.6-5. Notes placement and Evidence prominence (resolved by Weibao)`.

What the executor does with each answer:

- **option-c**: proceed exactly as plans 02 through 09 are written. No plan
  edit is needed. Record that `.planning/DECISIONS-12.6-REMAINING-2026-08-14.md`
  D-12.6-5 may be updated from `pending` to resolved by a later docs commit.
- **option-a** or **option-b**: record the choice and record these
  consequences beside it, then proceed: no 16C module, schema, fixture, or
  test changes, because the note schema is placement-agnostic (anchors plus
  objective relation); the presentation prose in `16C-UI-SPEC.md` D1 and the
  16B D4 placement note are re-rendered by Phase 17A against the recorded
  choice; plan 16C-09's freeze record carries the choice forward in its open
  items so 17A cannot miss it.
- **Evidence one level down**: record it; the only 16C effect is one line in
  the 16C-09 freeze record's open items naming 17A as the owner of the
  navigation change.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`16C-DECISIONS.md` carries the dated heading
`## D-12.6-5. Notes placement and Evidence prominence (resolved by Weibao)`
with the chosen option id, the Evidence-prominence answer, and Weibao's answer
recorded verbatim.
  </verify>
  <acceptance_criteria>
- The heading exists and names exactly one of `option-a`, `option-b`,
  `option-c`, plus one of `primary` or `one level down` for Evidence.
- When the answer is `option-a` or `option-b`, the recorded section carries
  the consequence list this task's action names.
- The file contains no em dash character, verified with the `chr(0x2014)`
  form.
  </acceptance_criteria>
  <reversibility rating="reversible">A presentation decision over a
  placement-agnostic schema; reversing it later changes UI-SPEC prose and 17A
  rendering, never a 16C schema or fixture.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`, plus `primary` or `one level down` for Evidence.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| plan text to landed code | Every 14A, 14B, 16A, and 16B signature in this phase's research was read from plan text; the precondition check is the only place that boundary is tested before code is written. |
| freeze record to this phase | Whatever the three freeze records say is frozen is what plans 02 through 09 build against; a withheld freeze read as a present one would authorize planning against an unproven surface. |
| upstream precondition to downstream freeze | A frozen record resting on an unresolved divergence its own precondition recorded is a record whose gate was never honored; three dated result lines are read directly. |
| checkpoint answer to product | The D-12.6-5 answer shapes daily feel; a silent default would convert a held decision into an agent's choice. |
| pre-phase tree to additivity claim | The evidence baselines recorded here are the only proof plan 16C-06's event types stayed additive; a baseline taken after a 16C edit passes for the wrong reason. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16C-01-01 | Tampering | the precondition check worked around instead of obeyed | high | mitigate | Step 11 forbids stubbing, try or except wrapping, a reduced check set, and recording-and-proceeding by name, and the verify block asserts no 16C module exists after a failed run. |
| T-16C-01-02 | Spoofing | a Freeze withheld file read as a present freeze record | high | mitigate | Step 5 checks for the absence of the literal `## Freeze withheld` heading in all three records in addition to the presence of `## Frozen at`, and states that a file carrying both fails. |
| T-16C-01-03 | Spoofing | a frozen record standing in for a resolved upstream precondition and a walked 13.9 | high | mitigate | Steps 6 and 7 read the three dated result lines and `13.9-03-SUMMARY.md` directly rather than trusting any freeze heading, and name both divergences by their own halt strings. |
| T-16C-01-04 | Elevation of Privilege | a held user decision silently defaulted by an agent | high | mitigate | Task 2 is a blocking `checkpoint:decision` recording a named option id and a verbatim answer; its action ends with the sentence that an unanswered checkpoint stops the wave. |
| T-16C-01-05 | Tampering | an additivity baseline taken after a 16C edit | high | mitigate | Step 10 runs before any file outside `.planning/` is touched, and the acceptance criteria assert no such file is created or modified by this task. |
| T-16C-01-06 | Repudiation | a precondition file recording a check that was not run | medium | mitigate | The Dated result line section requires the verbatim stdout of steps 1, 2, 3, 4, 8, and 10, whose expected values are written into the acceptance criteria. |
| T-16C-01-07 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; this plan runs only `python -c`, two shipped tests, and the guard against in-repo modules. Per PLANNING-DIRECTIVES section 4a the absence of dependencies is not the mitigation: any dependency ever added is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in 09-03-PLAN.md. |
| T-16C-01-08 | Information Disclosure | real learner or course content entering the repository | low | accept | This plan creates only two planning markdown files and touches no fixture, bank, note, or evidence path. Accepted because there is no content path to leak through; `python itembank.py guard .` remains an acceptance check on every later plan that touches `fixtures/`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by
executor judgment:

- No module file of any kind. `notes.py` is created by plan 16C-02 Task 2 and
  by nothing earlier; `strategies.py` by 16C-03; `progress_claims.py` by
  16C-04; `note_outputs.py` by 16C-07; `upgrade_audit.py` by 16C-08.
- No fixture, no test, no schema, no guard edit, and no evidence change.
  Every one of those belongs to a named later plan.
- No edit to `evidence.py`, `model.py`, `runtime.py`, `surfaces/cli.py`,
  `surfaces/ia.py`, or any skill file. This plan reads them and changes none.
- No second checkpoint. Every other open question in `16C-RESEARCH.md` is
  resolved either by the approved `16C-UI-SPEC.md` Decisions log (D1 through
  D16, transcribed) or by this plan's objective decision table (D-16C-1
  through D-16C-8).
- No re-litigation of D1 through D16. The UI-SPEC passed all six checker
  dimensions on 2026-08-15; a plan that reopens one of its decisions is
  reopening an approved contract, not making a plan.
- No new visual constant of any kind. Colors, spacing, typography, and glyphs
  are Phase 17A's; reusing the existing semantic and voice token names by
  assignment is what `16C-UI-SPEC.md` already did and is permitted.
- No freeze record and no freeze amendment. Plan 16C-09 owns the 16C freeze.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped:

- **The landed 14A, 14B, 16A, and 16B surfaces may differ from plan text
  (open until Task 1 runs).** Every constant value and signature Task 1
  asserts was read from plan frontmatter and objectives, never from source,
  because none of those modules existed when 16C was planned. A non-empty
  Deviations found section means plans 02 through 09 must be re-read against
  the three freeze records before execution.
- **`EVENT_SCHEMA_VERSION` staying 2 is an empirical claim (16C-RESEARCH
  A6).** The two new event types add tuple members and change no existing
  event's shape; if a reviewer determines a bump is required after all, the
  additive fixture in plan 16C-06 is where that surfaces, and the decision
  record is amended by a new dated entry, never edited.
- **The 16A shared note and activity schema hooks (CAP-03) may or may not
  have shipped names.** Step 3 records what 16A actually froze; if hooks
  exist, plans 16C-02 and 16C-06 compose with them at the registration seam
  and the Deviations section says exactly where.
- **Phase 13.9 execution is in flight on this branch at planning time.** The
  A9-closure check reads whatever SUMMARY evidence exists at execution time,
  which is exactly what the check is for; this plan neither reads nor touches
  any 13.9 file beyond the existence check.
</flagged_assumptions>

<summary_obligations>
`16C-01-SUMMARY.md` records: the precondition result and every deviation the
landed 14A, 14B, 16A, and 16B surfaces showed against their plan text, quoted
side by side; whether each upstream precondition recorded unresolved
deviations and whether Phase 13.9 was walked, with the files that proved
each; the five additivity baseline lines as recorded; the option Weibao chose
at Task 2 for both halves of D-12.6-5 and every consequence recorded for it;
which truth was verified by which command, with the command's actual stdout;
and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16C-strategies-notes-prototype-convergence/16C-01-SUMMARY.md`
when done.
</output>