---
phase: 16A-semantic-capability-activity-contract
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
  - .planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
autonomous: false
requirements: [CAP-01, CAP-02, CAP-03, ACTIVITY-01, ACTIVITY-03, A11Y-02, PORT-01]
estimate:
  tokens: 54000
  raw_tokens: 54000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Phase 16A writes no code that imports identity, journal, graph, course, or course_package until a recorded precondition check has confirmed that those modules exist on disk and that every constant this phase was planned against matches; a divergence halts the wave by name instead of surfacing as an ImportError or a silent vocabulary drift mid-task."
    - "Both freeze records this phase depends on, 14A-FREEZE.md and 14B-FREEZE.md, are checked for their own frozen headings, and a file that opens with a Freeze withheld heading counts as a failed check rather than as a present record."
    - "Phase 13.9 is confirmed walked before 14B's freeze is trusted, because ROADMAP.md's own Phase 14B entry forbids that freeze closing before the walking skeleton has been walked, which makes an unwalked skeleton a divergence in 16A's dependency rather than a distant scheduling matter."
    - "The two one-way doors this phase cannot silently adopt are settled and recorded before any grammar exists: whether the semantic-role registry becomes the primary representation with the shipped callout vocabulary as profile version 1 or whether the seven new roles are added alongside the shipped four (D-16A-1, which also fixes the exact seven role tokens), and where the capability-profile registry lives and which module owns the media grammar (D-16A-2)."
    - "The six decisions the planner resolved from research recommendations, D-16A-3 through D-16A-8, are transcribed into 16A-DECISIONS.md by this plan so every later plan reads one file for its grammar rather than re-deriving a token, an arity, or a fallback rule."
    - "The shipped additivity baseline is recorded as two literal SHA-256 values before any 16A grammar exists, so every later plan can prove format additivity by comparison rather than by promise."
    - "The shipped surface this phase extends is re-checked live before it is extended: surfaces.lesson._CALLOUT_KINDS still has exactly four members, model.GATE_VALUES still equals the three-member required/recommended/off tuple, runtime.public_item and runtime.glossable are still callable, and evidence.mark_event still raises ValueError on any marker other than the literal string human."
    - "CAP-01's unclassified probe row is classified by this plan as a completeness question, and CAP-03's unclassified probe row as a derivation question, with the classification and its reason written into 16A-DECISIONS.md rather than left as a silent drop."
  prohibitions:
    - statement: "A failed precondition check must not be worked around by stubbing a missing module, by wrapping the import in a try or except, by continuing with a reduced check set, or by recording the divergence and proceeding anyway; the halt is the correct outcome."
      status: kept
      verification: flagged-unverified
    - statement: "An unanswered checkpoint must not receive a silent default; a decision recorded as chosen when nobody chose it is a false record of authority."
      status: kept
      verification: flagged-unverified
    - statement: "A one-way format decision that later phases will author content against must not be adopted by executor judgment; if this plan did not decide it and no checkpoint asked it, the work stops rather than inventing a token."
      status: kept
      verification: flagged-unverified
  artifacts:
    - ".planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md with its five named sections"
    - ".planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md carrying the dated headings D-16A-1, D-16A-2, and the block D-16A-3 through D-16A-8, plus the probe-classification note"
  key_links:
    - "D-16A-1 decides two coupled things at once: whether the semantic-role registry is promoted to the primary representation and what the seven new role tokens are literally spelled. They are one decision because the promote option makes the token list a versioned profile entry while the add-alongside option makes it a dict key, and the two shapes carry different additivity obligations. Splitting them would let a later plan pick a representation and a spelling that disagree."
    - "The precondition check reads 14B-FREEZE.md, but ROADMAP.md's Phase 14B entry makes that freeze conditional on Phase 13.9 having been walked. Checking only for the frozen heading would accept a freeze that its own roadmap entry forbids, so step 5 checks the 13.9 evidence directly rather than trusting the downstream record."
    - "The two golden-parse SHA-256 values recorded here are the phase's only additivity evidence. Every later plan asserts them unchanged. If this task records a hash computed after any 16A edit, every later additivity assertion passes for the wrong reason, which is why this plan runs first and touches no code file."
    - "16A-DECISIONS.md is read by every later 16A plan before its first task. A decision recorded here in words a plan cannot act on leaves the executor choosing after all, which is the exact failure PLANNING-DIRECTIVES section 5 exists to prevent."
---

<objective>
Do the three things that must happen before any Phase 16A grammar exists.

First, verify that Phases 14A and 14B actually landed on disk with the surface
16A was planned against, and halt by name if they did not. `16A-RESEARCH.md`'s
"Critical caveat" records that `identity.py`, `journal.py`, `discovery.py`,
`graph.py`, `course.py`, `course_package.py`, `director.py`, and `blueprint.py`
all read MISSING at the repository root when this phase was researched and
planned, that no `14A-FREEZE.md` or `14B-FREEZE.md` existed, and that
`.planning/phases/13.9-walking-skeleton/` held only three PLAN files with no
SUMMARY. Every 14A and 14B signature this phase cites was therefore read from
plan text, never from source.

This phase's check is one step stricter than the one plans 14B-01, 15A-01, and
15B-01 ran, for a reason `ROADMAP.md` states itself: Phase 14B's freeze may not
close "before Phase 13.9 has been walked". A `14B-FREEZE.md` carrying a frozen
heading with no walked skeleton behind it is a record its own roadmap entry
forbids, so this task checks the skeleton directly rather than trusting the
downstream file.

Second and third, settle the two one-way design doors this phase cannot
silently adopt. Both are named as checkpoint candidates by `16A-RESEARCH.md`'s
own Assumptions Log (A1 and A2), and the first is the identity-model question
the deterministic assumption-delta detector raised on this phase: the shipped
lesson grammar is a single closed callout vocabulary rendered in one continuous
mode, and 16A introduces a versioned semantic profile, required versus optional
semantics, and a second mode. Whether the semantic-role registry becomes the
primary representation or is added alongside the shipped vocabulary is a format
decision every later phase authors content against.

Decisions already made, cited, and never re-derived here:

- **PLANNING-DIRECTIVES section 4**, all five non-negotiables, in particular
  number 2 (exactly one parser, one scorer, one evidence store) and number 4
  (format changes are additive, proven by a byte-identical fixture and not by
  promise).
- **PLANNING-DIRECTIVES section 4a**, which states that section 4.2 "forbids a
  **second** parser, scorer, or evidence store. It does not freeze the one
  parser's grammar. Additive growth is section 4.4's subject and is permitted,
  proven by a byte-identical fixture." Every grammar addition in this phase
  rests on that sentence.
- **PLANNING-DIRECTIVES section 4a**, the citation-discipline rule: this plan
  quotes the sentence behind every constraint it invokes.
- **PLANNING-DIRECTIVES section 2 rule 1**: a planning session stops only for an
  action that is hard to reverse, "such as an append-only evidence field, a
  published schema, a format decision other phases will build against". Both
  checkpoints in this plan are exactly that class and are the only two this
  plan raises.
- **ROADMAP.md Phase 16A "Depends on"**, quoted: "Phases 14A and 14B are planned
  but not yet executed, so every signature this phase imports is read from plan
  text at planning time; the first 16A plan opens with a recorded precondition
  check that halts by name on any divergence, the same pattern plans 14B-01,
  15A-01, and 15B-01 set, extended to check for a `14B-FREEZE.md` record."
- **16A-RESEARCH.md's Don't Hand-Roll table and Pitfall 1**: seven of CAP-01's
  fourteen roles already ship. This phase catalogs them and does not rebuild the
  glossary, the hint ladder, the `[!KEY]` card, the `[!CHECK:]` slot, or the
  `visual` item type.
- **The phase-shape constraint on visual scope**, binding on every 16A plan:
  visual system, tokens, and polish are Phase 17A. Guided mode in 16A is a data
  contract and a minimally rendered proof, not visual design.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar). Task 1 transcribes each of these into
`16A-DECISIONS.md` verbatim under its own dated heading.

| ID | Open question | Locked answer | One-line rationale |
|---|---|---|---|
| D-16A-3 | How is a semantic marked required versus optional, and what does an unknown one do | A callout marker may carry a trailing exclamation mark inside the brackets: `> [!MISCONCEPTION!]` declares the semantic required, and its absence means optional. Unknown and optional keeps the shipped degradation unchanged (the block falls through to plain paragraph output byte for byte) and adds the lint warning `lesson.unknown_semantic`. Unknown and required renders one locked refusal container carrying the exact copy `This block needs a lesson feature this reader does not have. Its text is below, unchanged.` followed by the raw body text, and lint emits the error `lesson.unknown_required_semantic`. Nothing is dropped and nothing raises. | CAP-01's Degraded clause verbatim: "an unknown optional semantic renders its fallback with a warning; an unknown required semantic fails safely". The trailing marker is captured by the shipped `_CALLOUT_MARK_RE` group 1 with no regex change, so a bank that uses no exclamation mark parses byte identically. |
| D-16A-4 | How is the semantic profile versioned | One preamble directive `[SEMANTIC-PROFILE: <positive integer>]`, read by `parse_lesson` with the identical `grab()` shape `[GATE:]` already uses at `model.py:530-535`, defaulting to `1` when absent. `model.SEMANTIC_PROFILE_VERSION` equals `1`. A non-integer or non-positive value is the lint error `lesson.invalid_semantic_profile`; the parse never raises and falls back to `1`. | PORT-01's "additive, versioned semantic profile", carried on the shipped directive precedent rather than a new metadata block. |
| D-16A-5 | What is the closed vocabulary for a capability's renderer-availability field | `RENDERER_AVAILABILITY = ("available", "degraded", "unavailable")`, a three member closed tuple in `model.GATE_VALUES`'s exact shape. | `16A-RESEARCH.md` Open Question 2, recommendation adopted verbatim: the binary Degraded clause plus one explicit middle state for partial breakage. |
| D-16A-6 | Does the shipped `[!EXAMPLE]` callout satisfy CAP-01's worked-example role | Yes, for 16A. Annotated per-step structure is recorded as a Registered-tier enhancement for a later capability-profile version bump and is out of scope here. CAP-01's worked-example-first default is enforced as the lint warning `lesson.definition_before_example`, suppressed only by an authored `[EXAMPLE-ORDER: definition-first because <reason>]` directive whose reason text is required and is recorded in the lint report. | `16A-RESEARCH.md` Open Question 1, recommendation adopted verbatim, plus CAP-01's own clause "an author or course director may override per lesson with a recorded reason". |
| D-16A-7 | What shape does media metadata take, and does the dated jurisdiction warning need a structured field | Media metadata is a preamble registry section `## MEDIA`, one pipe row per asset, read through `model._preamble_section(head, "MEDIA")`, following `## SOURCES`'s exact shape, with columns in this fixed order: `id`, `path`, `credit`, `alt`, `rights`, `derivation`, `availability`, `integrity`. The dated jurisdiction warning stays free prose with a stated date inside the shipped `[!WARNING]` callout; no structured `effective_date` or `jurisdiction` field is minted in 16A, and a structured field is a backburner entry contingent on 15B's staleness machinery. | `16A-RESEARCH.md` Assumption A3 recommendation and Open Question 3 recommendation, both adopted verbatim. |
| D-16A-8 | Does 16A enforce media rights | No. The `rights` column's vocabulary is `identity.RIGHTS_STATES` referenced, never a second tuple, and lint validates membership only. No 16A code path gates on it. Enforcement is deferred by name to whichever later subphase's execution first packages or exports a media asset, and that deferral is written into the 16A freeze record rather than left implicit. | `16A-RESEARCH.md` Pitfall 4 and Assumption A5: inventing a working enforcement mechanism against a vocabulary this phase does not own is how a second rights vocabulary is created. |

Guided mode's 16A data contract is locked here too, not by a checkpoint,
because the orchestrator's phase-shape constraint already settled its scope.
Recorded as `D-16A-9` by Task 1 for citation convenience:

`lesson_page` gains a keyword argument `mode` with the values `"continuous"`
and `"guided"`, defaulting to `"continuous"` so every shipped caller renders
byte identically. A guided stage is one `###` heading's body split at each
callout boundary: the run of blocks up to and including the next callout is one
stage. Guided mode renders every stage in one document, each inside
`<section class="stage" data-stage="N">`, with only the first stage carrying
`data-stage-open="1"`. No JavaScript, no color, no spacing, no motion, and no
token constant is introduced. Nothing persists across a stage boundary in 16A:
reading position and resume are Phase 16B's, named here so the executor refuses
them rather than deciding.

Purpose: make the rest of the phase transcription rather than judgment.
Output: one recorded precondition result and nine recorded decisions.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PATTERNS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-01-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-02-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-06-PLAN.md
@.agents/skills/OPERATION-CONTRACT.md
</context>

## Artifacts this phase produces (plan 16A-01 share)

This plan creates no module, no schema, no test, and no fixture. It creates
exactly two planning artifacts, both new in this phase:

- `.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md`
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`

New symbols introduced by this plan: none.
New lint codes introduced by this plan: none.
No CLI command and no daemon route is produced by this plan.

The full symbol inventory for the phase, so a plan-review source-grounding pass
can exclude newly created names from drift verification, is repeated in each
later plan's own "Artifacts this phase produces" section. The union across plans
02 through 10 is:

- `surfaces/lesson.py`: seven new `_CALLOUT_KINDS` entries (`PREREQUISITE`,
  `MISCONCEPTION`, `TIP`, `COUNTEREXAMPLE`, `EXCERPT`, `UNCERTAINTY`,
  `SUMMARY`); `_callout_required_of`; `_unsupported_callout_html`;
  `UNSUPPORTED_SEMANTIC_COPY`; `lesson_page`'s new `mode` keyword argument;
  `guided_stages`; `_stage_html`; `_media_figure_html`;
  `_static_instructional_html`.
- `model.py`: `SEMANTIC_PROFILE_VERSION`; `parse_lesson`'s new `semantic_profile`
  key; `parse_lesson`'s new `lang` and `dir` keys; `parse_media`;
  `parse_activities`; `MEDIA_COLUMNS`; `ACTIVITY_COLUMNS`; `ACTIVITY_PURPOSES`;
  `ACTIVITY_RETRY`; `ACTIVITY_FEEDBACK`; `ACTIVITY_EVIDENCE_STATES`;
  `LESSON_DIRECTIONS`; and these `LINT_CODES` members: `lesson.unknown_semantic`,
  `lesson.unknown_required_semantic`, `lesson.invalid_semantic_profile`,
  `lesson.definition_before_example`, `lesson.example_order_no_reason`,
  `lesson.lang_empty`, `lesson.invalid_direction`, `media.duplicate_id`,
  `media.missing_alt`, `media.unknown_rights`, `media.unknown_availability`,
  `media.ref_unknown`, `activity.duplicate_item`, `activity.empty_block`,
  `activity.item_unknown`, `activity.unknown_purpose`, `activity.demand_empty`,
  `activity.unknown_retry`, `activity.unknown_feedback`,
  `activity.unknown_evidence_state`, `activity.missing_static_fallback`,
  `activity.missing_a11y_equivalent`, `activity.unsupported_response_form`,
  `capability.unknown_reference`.
- `capabilities.py` (module boundary decided by D-16A-2) and every constant,
  exception, and function on it: `CAPABILITY_PROFILE_KEYS`,
  `RENDERER_AVAILABILITY`, `MEDIA_RIGHTS_STATES`, `MEDIA_AVAILABILITY`,
  `OUTPUT_MODES`, `BACKBURNER_MODES`, `CapabilityError`, `profile`, `profiles`,
  `register`, `static_path`, `compose_outline`, `compose_glossary`,
  `backburner_entry`.
- `schemas/capability_profile.schema.json`.
- `fixtures/lesson_capability_corpus.py`: `build_thin_slice`,
  `build_full_corpus`, `build_medical_case`, `build_disputed_timeline`,
  `build_localization_lesson`, `build_activity_set`, `build_all_16a`.
- `tests/capability_stress_corpus_tracer.py` and every `scenario_*` function on
  it.
- `tests/assessment_authority_adversarial.py` and every `attack_*` function on
  it.
- The planning artifacts `16A-PRECONDITION.md`, `16A-DECISIONS.md`,
  `16A-TRACER-REPORT.md`, `16A-REVIEW.md`, `16A-FREEZE.md`.

<tasks>

<task type="auto">
  <name>Task 1: verify Phases 14A and 14B landed and Phase 13.9 was walked, or halt by name</name>
  <files>.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md, .planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md</files>
  <read_first>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md`,
  the section "Critical caveat: Phase 16A's declared dependency (14B) has not
  executed, and neither has anything upstream of it", and the Assumptions Log,
  in full. This task exists because of them.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-01-PLAN.md` Task 1, in
  full. This task copies its shape exactly and adds the Phase 13.9 leg and the
  golden-hash baseline.
- `.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md`, the
  "Artifacts this phase produces" section, for the `identity.py` constant list,
  in particular `RIGHTS_OPERATIONS` and `RIGHTS_STATES`.
- `.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md`, the
  "Artifacts this phase produces" section, for `graph.SECTION_ORDER`,
  `course.COURSE_SIDECAR_FILENAME`, and `course.write_course`'s signature.
- `.planning/phases/14B-graph-course-package-prototype/14B-02-PLAN.md`, the
  "Artifacts this phase produces" section, for `graph.outline_projection`'s
  signature and return shape. Plan 16A-07 composes CAP-03's outline output mode
  from exactly that function and from no second outline generator.
- `.planning/phases/14B-graph-course-package-prototype/14B-06-PLAN.md`, the task
  that writes `14B-FREEZE.md`, specifically the step that gates the freeze on
  Phase 13.9 having been walked. Step 5 below checks that gate directly.
- `.planning/ROADMAP.md`, the `### Phase 16A: Semantic Capability & Activity
  Contract` section in full, and the `### Phase 14B` entry's freeze-gate
  paragraph.
- `surfaces/lesson.py` lines 641 to 653, `_CALLOUT_MARK_RE` and
  `_CALLOUT_KINDS`, and lines 852 to 887, `_callout_spec` and
  `_callout_kind_of`. Step 6 asserts these are unchanged.
- `model.py` line 2052, `GATE_VALUES`, and lines 574 to 602,
  `_preamble_section`.
  </read_first>
  <action>
1. Check that the six dependency modules 16A may reference import. Run:

```
python -c "import identity, journal, discovery, graph, course, course_package; print('modules present')"
```

   Expected stdout: `modules present`, exit code 0.

2. Check that the frozen 14A constants match what Phase 16A was planned against.
   Run a single `python -c` that asserts, in this order, every one of the
   following, printing `14A surface matches` on success:
   - `identity.RIGHTS_OPERATIONS` equals `("read", "quote", "transform",
     "remote_process", "package", "export", "share")`.
   - `identity.RIGHTS_STATES` equals `("granted", "denied", "unknown")`.
   - `identity.OBJECT_KINDS` is a tuple and `"lesson"` is a member of it.
   - Every one of these names is callable on its module:
     `identity.new_object_id`, `identity.object_fingerprint`,
     `identity.rights_state`, `identity.rights_granted`.

   `identity.RIGHTS_STATES` is the exact tuple decision D-16A-8 references by
   value rather than copying. A divergence here changes what the `## MEDIA`
   registry's `rights` column may contain, so it halts.

3. Check that the frozen 14B constants match. Run a single `python -c` that
   asserts, in this order, every one of the following, printing
   `14B surface matches` on success:
   - `graph.COURSE_GRAPH_VERSION` equals `1`.
   - `graph.SECTION_ORDER` is a tuple.
   - `callable(graph.outline_projection)` is `True`.
   - `callable(course.read_course)` and `callable(course.write_course)` are both
     `True`.
   - `graph.TREATMENT_KINDS` has exactly eleven members.
   - `hasattr(graph, "compose_glossary")` is `False` and
     `hasattr(capabilities := None, "x")` is not evaluated; instead assert that
     importing `capabilities` raises `ModuleNotFoundError`. Plan 16A-02 Task 2
     creates that module and nothing earlier may; finding it present means
     something else created it and the plan set must be re-read before it does.

4. Check that both freeze records exist and are real freezes, not withholdings:
   - `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` contains
     the literal heading `## Frozen at 14A`.
   - `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md`
     contains the literal heading `## Frozen at 14B`.
   - Neither contains the literal heading `## Freeze withheld`. A file carrying
     a withholding heading fails this check even if the frozen heading is also
     present, because a phase that withheld its freeze has not frozen its
     surface and 16A cannot plan against it.

5. Check the Phase 13.9 leg directly rather than trusting `14B-FREEZE.md` to
   have honored it. `ROADMAP.md`'s Phase 14B entry forbids that freeze closing
   "before Phase 13.9 has been walked", so a frozen 14B with an unwalked
   skeleton is a record its own roadmap entry forbids. Assert that at least one
   file matching `.planning/phases/13.9-walking-skeleton/13.9-*-SUMMARY.md`
   exists, and that
   `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists
   specifically. If `13.9-03-SUMMARY.md` is absent but `14B-FREEZE.md` carries
   its frozen heading, that is a divergence and it halts: record it as
   `13.9 unwalked behind a frozen 14B`.

6. Check that the shipped surface this phase extends is still what
   `16A-RESEARCH.md` and `16A-PATTERNS.md` read. Run:

```
python -c "import model, runtime, evidence, sys; sys.path.insert(0,'.'); from surfaces import lesson; print(len(lesson._CALLOUT_KINDS), sorted(lesson._CALLOUT_KINDS), model.GATE_VALUES, callable(runtime.public_item), callable(runtime.glossable), hasattr(model,'SEMANTIC_PROFILE_VERSION'))"
```

   Expected stdout exactly:
   `4 ['EXAMPLE', 'KEY', 'NOTE', 'WARNING'] ('required', 'recommended', 'off') True True False`

   Then check the human-only marking gate is still a hard refusal. Run:

```
python -c "import evidence
try:
    evidence.mark_event('s','i','ref','ev',True,marker='model')
    print('GATE OPEN')
except ValueError:
    print('mark_event human-only gate holds')"
```

   Expected stdout: `mark_event human-only gate holds`. A `GATE OPEN` result
   halts, because plan 16A-09's whole adversarial suite is written against that
   refusal.

7. Record the additivity baseline. This is the phase's only proof that format
   changes stayed additive, so it is taken before any 16A grammar exists. Run:

```
python -c "import hashlib
for p in ('fixtures/lesson_golden_phase3_parse.json','fixtures/lesson_golden_phase3_content.txt','fixtures/lesson_bank.md'):
    print(p, hashlib.sha256(open(p,'rb').read()).hexdigest())"
```

   Expected stdout exactly these three lines:

```
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```

   A hash that differs from the value printed above is not automatically a
   failure: it means the golden fixtures changed between planning and execution
   for some other reason. Record the found value as the baseline, record the
   planned value beside it in the Deviations section, and continue. What must
   never happen is recording a baseline computed after a 16A edit, which is why
   this task runs before any code file is touched.

   Confirm the shipped lesson suite is green against those fixtures before
   trusting them as a baseline. Run:

```
python tests/lesson_roundtrip.py
```

   Expected: exit code 0.

8. If any check in steps 1 through 6 fails, STOP. Write nothing else, create no
   module, and print exactly this line with the failing item substituted for
   `<item>`, then exit non-zero:

   `HALT 16A-01 precondition: Phase 14A or Phase 14B has not landed, its frozen surface differs from what Phase 16A was planned against, Phase 13.9 was not walked, or the shipped lesson and evidence surface moved. Re-verify every 16A plan against .planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md and .planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md before writing any code. Divergent or missing: <item>`

   Do not work around a failure by stubbing the missing module, by wrapping the
   import in a try or except, by continuing with a reduced check set, or by
   recording the divergence and proceeding anyway. A halt here is the correct
   outcome; it is what this task is for.

9. On success, create
   `.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md`
   with exactly these five sections and nothing more:
   - **Why this check exists.** One paragraph citing `16A-RESEARCH.md`'s
     Critical caveat: every 14A and 14B signature in the 16A research and
     pattern map was read from plan text, not from source, because the modules
     did not exist when 16A was planned, and 16A sits downstream of two
     unexecuted phases and one unwalked skeleton.
   - **What was checked.** The full list from steps 1 through 6, one line each,
     each marked `ok` or `divergent`.
   - **Additivity baseline.** The three file paths and their SHA-256 values from
     step 7, each on its own line, under the sentence: `Every later 16A plan
     asserts these three values unchanged. A changed value means a format
     change was not additive.`
   - **Deviations found.** Every place the landed 14A or 14B surface differs
     from the plan text, with the plan-text value and the landed value side by
     side. Write `none` when there are none. A deviation here is not a failure
     of this task; it is the signal that plans 02 through 10 must be re-read
     against the two freeze records before execution, and this section is where
     a later plan looks for it.
   - **Dated result line.** The date, the command output of steps 2, 3, 6, and 7
     verbatim, and one sentence stating whether 16A may proceed.

10. Also on success, create
    `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
    with these sections, in this order, and nothing more:
    - A one paragraph header stating that this file is the single source of
      truth for every 16A grammar decision, that every later 16A plan reads it
      before its first task, and that Tasks 2 and 3 of this plan append
      `## D-16A-1` and `## D-16A-2` below.
    - `## D-16A-3` through `## D-16A-8`, one dated heading each, each carrying
      the locked answer and the one-line rationale transcribed verbatim from
      this plan's objective decision table. Use these exact headings:
      `## D-16A-3. Required and optional semantics and the unknown-semantic contract`,
      `## D-16A-4. The semantic profile version directive`,
      `## D-16A-5. The renderer-availability vocabulary`,
      `## D-16A-6. The worked-example bar and the example-order override`,
      `## D-16A-7. The media grammar shape and the dated jurisdiction warning`,
      `## D-16A-8. Media rights are declared, not enforced, in 16A`.
    - `## D-16A-9. Guided mode's 16A data contract`, carrying the guided-mode
      paragraph from this plan's objective verbatim, including the sentence that
      reading position and resume are Phase 16B's.
    - `## Probe classification note`, recording that the spec-less edge-coverage
      probe returned two rows marked `unclassified`, that the planner classified
      CAP-01's as a completeness question (does every named role have a
      rendering path in both modes, and what happens to a role named in the
      requirement but absent from the registry) and CAP-03's as a derivation
      question (can an output mode become the only understandable copy), that
      both classifications produced acceptance criteria carried in the
      `must_haves` of plans 16A-03 and 16A-07 respectively, and that neither row
      was dropped.

    No em dash characters anywhere in either file.
  </action>
  <verify>
  <automated>python -c "import identity, journal, graph, course, course_package, sys; sys.path.insert(0,'.'); from surfaces import lesson; import model, runtime, evidence, hashlib; assert len(lesson._CALLOUT_KINDS)==4; assert model.GATE_VALUES==('required','recommended','off'); assert not hasattr(model,'SEMANTIC_PROFILE_VERSION'); assert hashlib.sha256(open('fixtures/lesson_golden_phase3_parse.json','rb').read()).hexdigest()=='4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa'; print('16A preconditions match')"</automated>
Expected: prints `16A preconditions match` and exits 0. The degraded state this
task must prove rather than paper over is the halt itself: if any assertion
fails, the run exits non-zero with the named HALT line and no module file is
created. Confirm this by checking that `capabilities.py` does not exist on disk
at the end of a failed run.
  </verify>
  <acceptance_criteria>
- The step 1 command prints `modules present` and exits 0.
- The step 2 command prints `14A surface matches` and exits 0.
- The step 3 command prints `14B surface matches` and exits 0, including the
  assertion that `import capabilities` raises `ModuleNotFoundError`.
- Both freeze files exist, each contains its own `## Frozen at` heading, and
  neither contains `## Freeze withheld`.
- `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists.
- The step 6 command prints exactly
  `4 ['EXAMPLE', 'KEY', 'NOTE', 'WARNING'] ('required', 'recommended', 'off') True True False`
  and the second step 6 command prints `mark_event human-only gate holds`.
- `python tests/lesson_roundtrip.py` exits 0.
- `16A-PRECONDITION.md` exists with all five named sections, and its Additivity
  baseline section carries three `path sha256` lines.
- `16A-DECISIONS.md` exists and contains the literal headings `## D-16A-3.`,
  `## D-16A-4.`, `## D-16A-5.`, `## D-16A-6.`, `## D-16A-7.`, `## D-16A-8.`,
  `## D-16A-9.`, and `## Probe classification note`.
- Neither file contains an em dash character. Verify with the command below,
  which builds the character from its code point rather than embedding it, so
  the check is not invalidated by its own text. Expected stdout: `no em dash`.

```
python -c "import io,sys; D=chr(0x2014); bad=[p for p in ('.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md','.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md') if D in io.open(p,encoding='utf-8').read()]; sys.exit('em dash found in '+', '.join(bad)) if bad else print('no em dash')"
```

  Every later 16A plan reuses this same `chr(0x2014)` form for its own em dash
  check, for the same reason. A check that embeds the character it forbids
  reports itself.
- No file outside `.planning/` is created or modified by this task.
  </acceptance_criteria>
  <precondition>Phases 14A and 14B have executed, `identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`, and `course_package.py` exist at the repository root with the surfaces frozen in `14A-FREEZE.md` and `14B-FREEZE.md`, and Phase 13.9 has been walked with `13.9-03-SUMMARY.md` recorded.</precondition>
  <reversibility rating="reversible">The two files record a check and transcribe decisions already made in the plan; nothing durable in the codebase is created and the check can be re-run at any time.</reversibility>
  <done>Either 16A is cleared to proceed with the evidence and the additivity
  baseline recorded, or the wave is halted with the divergence named.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 2: promote the semantic-role registry, or add the seven roles alongside the shipped four</name>
  <files>.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md</files>
  <read_first>
- `16A-RESEARCH.md`, the "Summary" section, the "Architectural Responsibility
  Map" table, Pattern 1 in "Architecture Patterns", the "Alternatives
  Considered" table, and Assumption A1, all in full. A1 is the reason this is a
  checkpoint rather than a silent adoption.
- `16A-PATTERNS.md`, the `surfaces/lesson.py` row of the File Classification
  table and its Pattern Assignment section, both in full.
- `surfaces/lesson.py` lines 641 to 653 (`_CALLOUT_MARK_RE`, the locked-kinds
  comment, `_CALLOUT_KINDS`) and lines 852 to 887 (`_callout_spec`,
  `_callout_kind_of`), the exact code both options modify.
- `.planning/REQUIREMENTS.md`, `CAP-01` in full, in particular the clause
  "composed from shared primitives, not separate content types" and the
  Degraded clause, and `PORT-01` in full, in particular "an additive, versioned
  semantic profile".
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  as written by Task 1, so the new section is appended below `## D-16A-9`
  rather than overwriting one.
  </read_first>
  <decision>
Does the semantic-role registry become the primary representation of a lesson's
teaching roles, with the shipped four callout kinds becoming entries in profile
version 1, or are the seven new roles added alongside the shipped four as more
entries in the existing `_CALLOUT_KINDS` dict with no promotion, and in either
case what are the seven role tokens literally spelled?
  </decision>
  <context>
The deterministic assumption-delta detector fired on this phase, and this is the
identity-model question underneath it. The shipped lesson grammar is a single
closed callout vocabulary (`_CALLOUT_KINDS`, four members) rendered in one
continuous mode by one renderer. Phase 16A introduces three things that vocabulary
was not designed to carry: a versioned semantic profile (PORT-01), a required
versus optional distinction (CAP-01's Degraded clause), and a second rendering
mode (CAP-01's first clause).

The shipped code's own comment says "Adding a kind is a one-line registration
here, the container and its degradation contract do not change"
(`surfaces/lesson.py:646`). That sentence is true for a fifth label. It is not
obviously true for a vocabulary that also has to answer "which profile version
introduced this role", "is this role required", and "what does the guided-mode
stager do with it".

This is rated one-way. Whichever representation is chosen is what real authored
lessons are written against from the first corpus file onward, and what Phase
16B, 16C, and 17A read. The seven token spellings are equally one-way: they
become an authored-content contract the moment a lesson uses one, and a rename
after that is a content migration, not an edit. `16A-RESEARCH.md` Assumption A1
says so directly: the tokens are "this research's proposed tokens, not verified
against any prior decision record" and "should be a plan-level
checkpoint:decision naming the final seven tokens rather than silently
adopted".

The two questions are one decision because they resolve into different shapes.
Under promotion the token list is data inside a versioned profile record, and
adding a role in a later phase is a profile version bump with a recorded
migration. Under add-alongside the token list is a set of dict keys, and adding
a role in a later phase is another one-line registration with no version story.
Choosing a representation and a spelling separately would let a later plan pick
two that disagree.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: add alongside, with the profile version recorded beside the vocabulary rather than owning it</name>
      <pros>`_CALLOUT_KINDS` gains exactly seven entries and stays the one
      source of truth for what a callout kind means, which is the pattern the
      shipped comment describes and the pattern `16A-RESEARCH.md` recommends by
      name ("register the seven new callout kinds using the exact
      `_CALLOUT_KINDS` one-line pattern"). The seven tokens are
      `PREREQUISITE`, `MISCONCEPTION`, `TIP`, `COUNTEREXAMPLE`, `EXCERPT`,
      `UNCERTAINTY`, `SUMMARY`, each mapping to a `(slug, label)` pair exactly
      as the shipped four do: `("prerequisite", "Before this")`,
      `("misconception", "Common mistake")`, `("tip", "Expert tip")`,
      `("counterexample", "Counterexample")`, `("excerpt", "From the source")`,
      `("uncertainty", "Not settled")`, `("summary", "In short")`. The
      semantic profile version (`D-16A-4`) is a separate, additive lesson
      directive that records which profile a document was authored against; it
      does not own or gate the vocabulary. Additivity is provable in one line:
      a bank using none of the seven parses and renders byte identically,
      asserted against the golden hashes Task 1 recorded. Nothing about the
      shipped four changes, so no migration exists and the `[!KEY]` card, the
      `[!CHECK:]` reserved slot, and the gate band keep their current
      dispatch.</pros>
      <cons>There is no structural place to record, per role, which profile
      version introduced it, so that history lives only in `16A-DECISIONS.md`
      and the freeze record. A later phase that needs per-role version
      provenance has to promote then, which is the migration this option
      defers rather than avoids. The capability profile registry
      (`capabilities.py`, D-16A-2) and the callout vocabulary stay two lists
      that must be kept consistent by a lint check rather than by
      construction.</cons>
    </option>
    <option id="option-b">
      <name>Promote: the semantic-role registry becomes primary and the shipped four become profile version 1 entries</name>
      <pros>One registry answers every question about a role: its token, its
      slug, its label, its profile version, whether it is required-capable, and
      which capability profile describes its rendering. Per-role version
      provenance is structural, so a later phase adds a role by bumping the
      profile version with a recorded migration rather than by editing a dict
      and hoping documentation follows. The capability profile registry and the
      role registry become one list rather than two kept consistent by
      hand.</pros>
      <cons>`_CALLOUT_KINDS` stops being the source of truth and becomes a
      derived view, which means the shipped `_callout_spec` and
      `_callout_kind_of` dispatch changes shape rather than gaining entries.
      That is a rewrite of shipped, tested, executed Phase 3.1 code this phase
      has no defect to fix in, and every existing assertion in
      `tests/lesson_roundtrip.py`, `tests/style_roundtrip.py`, and
      `tests/gate_roundtrip.py` that reaches `_CALLOUT_KINDS` has to be
      re-proven rather than left alone. It also creates a versioned published
      contract in the same phase that first authors content against it, so the
      version-1 shape is frozen with no second version to have learned
      from.</cons>
    </option>
    <option id="option-c">
      <name>Add alongside now, promote behind a recorded trigger later</name>
      <pros>Option-a's cost today, with the promotion written down as a
      registered capability rather than forgotten: `16A-DECISIONS.md` records
      the exact trigger that would justify promotion (a second profile version
      is genuinely needed, or a role's rendering differs by profile version)
      and names the phase that would own it. Nothing is rebuilt now and nothing
      is silently dropped, which is the disposition discipline
      `PLANNING-DIRECTIVES.md` section 3a requires.</pros>
      <cons>A recorded trigger is only as good as the phase that reads it, and
      this project already carries several. It also adds a paragraph to the
      freeze record whose only function is to describe work not done.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and record the answer verbatim in
`.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
under a dated heading `## D-16A-1. Semantic-role registry: promote or add
alongside, and the seven role tokens`.

The recorded section must state, in one sentence each: which option was chosen,
the seven role tokens as literal strings, the seven `(slug, label)` pairs as
literal strings, and whether `_CALLOUT_KINDS` remains the source of truth.

What the executor does with each answer:

- **option-a**: proceed as every task in plans 02 through 10 is already written.
  No plan edit is needed. The seven tokens and their `(slug, label)` pairs are
  exactly the values listed in option-a above.
- **option-b**: before plan 16A-02 Task 1, record in `16A-DECISIONS.md` that
  `surfaces/lesson.py`'s `_CALLOUT_KINDS`, `_callout_spec`, and
  `_callout_kind_of` are rewritten rather than extended; that a new
  `SEMANTIC_ROLES` registry becomes the source of truth and `_CALLOUT_KINDS`
  becomes a derived mapping built from it; that `tests/lesson_roundtrip.py`,
  `tests/style_roundtrip.py`, and `tests/gate_roundtrip.py` enter the
  `files_modified` list of plan 16A-03 and each must be run green before and
  after the rewrite; that plan 16A-03 gains one task for the derivation and its
  regression proof, taking that plan to three tasks with the unknown-semantic
  work moving to plan 16A-04; and that the 16A freeze record enumerates a
  versioned role registry as a published contract. Then build it that way.
- **option-c**: proceed exactly as option-a, and additionally append to
  `16A-DECISIONS.md` a `## D-16A-1a. Promotion trigger` subsection naming the
  exact condition that would justify promotion, the phase that would own it,
  and the migration it would require. Plan 16A-10's freeze record carries that
  subsection forward as a registered, not deferred, capability.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`16A-DECISIONS.md` exists and carries a dated `## D-16A-1` heading with the
chosen option id, Weibao's answer recorded verbatim, and the seven role tokens
written as literal strings.
  </verify>
  <acceptance_criteria>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  contains the literal heading `## D-16A-1. Semantic-role registry: promote or
  add alongside, and the seven role tokens`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The recorded section lists exactly seven role tokens and exactly seven
  `(slug, label)` pairs as literal strings.
- The recorded section states in one sentence whether `_CALLOUT_KINDS` remains
  the source of truth.
- When the answer is `option-b` or `option-c`, the file also carries the
  consequence list this task's action names for that option.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">The chosen representation is what every
  authored lesson from the first corpus file onward is written against, and the
  seven token spellings become an authored-content contract the moment a lesson
  uses one. A rename or a reshape after that is a content migration across every
  file that used it, not an edit.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 3: where the capability-profile registry lives and which module owns the media grammar</name>
  <files>.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md</files>
  <read_first>
- `16A-RESEARCH.md`, the "Standard Stack" section's "New in this phase" table,
  the "Alternatives Considered" table row on `capabilities.py` versus
  `graph.py`, the "Architectural Responsibility Map" rows for "Capability
  support profile" and "Media asset metadata", and Assumption A2, all in full.
  A2 is the reason this is a checkpoint rather than a silent adoption.
- `16A-PATTERNS.md`, the `capabilities.py` row of the File Classification table
  and its Pattern Assignment section, including the "Do not fold into" note.
- `model.py` lines 1 to 20, the module docstring, for the parsing-only scope
  option-b would widen.
- `model.py` lines 574 to 602, `_preamble_section`, the one boundary rule every
  new preamble section reads through under every option.
- `model.py` line 2052, `GATE_VALUES`, the closed-tuple constant shape the new
  registry's vocabularies follow under every option.
- `.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md`, the
  "Artifacts this phase produces" section, for the pure-versus-I/O split
  between `graph.py` and `course.py` that option-a extends.
- `.planning/PLAN-TEMPLATE.md`, the standing rule "Name the seam before adding a
  provider", in full.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`,
  so the new section is appended below `## D-16A-1`.
  </read_first>
  <decision>
Does Phase 16A add one new pure root-level module holding the capability-profile
registry and the output-mode composition, leaving the media and activity
grammars in `model.py` where every other preamble registry already parses, or
does the new module also own the media and activity grammar, or do the profiles
fold into `model.py` with no new module at all?
  </decision>
  <context>
Phase 16A adds four kinds of new surface: a capability support profile registry
(CAP-02), a media asset metadata registry (CAP-02), a purpose-first activity
declaration (ACTIVITY-01), and two registered output modes composed from shared
schemas (CAP-03).

Two of those four are parsing: `## MEDIA` and `## ACTIVITIES` are preamble
registry sections in exactly the shape `## SOURCES` and `## TERMS` already take,
and `model._preamble_section` is the one boundary rule they must read through
under every option. The other two are not parsing: a capability's
accessible-behavior, offline-fallback, renderer-availability, version,
validation, and known-limits tuple is static declared data with no document
behind it, and composing an outline or a glossary is a transform over an already
parsed document.

`14B` already established a pure-versus-I/O split in an adjacent domain:
`graph.py` is the pure kernel and `course.py` is the I/O layer.
`16A-RESEARCH.md`'s Alternatives Considered rejects folding capability profiles
into `graph.py` on scope grounds, but it does not settle the boundary between a
new module and `model.py`, and it flags that as Assumption A2.

This is rated one-way. The chosen module name and boundary appear in every
import in plans 04 through 10, in every structural-ban assertion, in
`schemas/capability_profile.schema.json`'s intended reader, in the 16A freeze
record, and in whatever Phases 16B, 16C, and 17A build on top. Undoing it after
the freeze means renaming a published surface, not editing a line.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: one new pure module `capabilities.py`, with the media and activity grammars staying in `model.py`</name>
      <pros>`capabilities.py` is a new root-level module importing nothing from
      this repository except `model` for the document shapes it composes over.
      It holds `CAPABILITY_PROFILE_KEYS`, `RENDERER_AVAILABILITY`,
      `MEDIA_RIGHTS_STATES`, `MEDIA_AVAILABILITY`, `OUTPUT_MODES`,
      `BACKBURNER_MODES`, `CapabilityError`, `profile`, `profiles`, `register`,
      `static_path`, `compose_outline`, `compose_glossary`, and
      `backburner_entry`, every one of them a pure function or a plain tuple or
      dict constant, with no file read and no session state. `## MEDIA` and
      `## ACTIVITIES` parse in `model.py` beside `parse_sources` and
      `parse_terms`, through the same `_preamble_section` boundary rule, so the
      file keeps one boundary rule rather than gaining a second scanner in a
      second module. `hasattr(capabilities, "open")` is not the test; the
      structural bans that hold are that `capabilities.py` contains no `open(`
      call and imports neither `evidence` nor `runtime`, so the rules that it
      never writes and never decides disclosure are structural rather than
      maintained by care. `model.py`'s stated scope, parse markdown and return
      plain dicts, is unchanged: two more registries is exactly what it already
      does four times.</pros>
      <cons>The capability vocabulary and the media grammar's `rights` and
      `availability` columns live in two files, so `model.lint` imports
      `capabilities` to validate a `## MEDIA` row's membership. That is one new
      import edge on the shipped linter, which is a real if small weight
      increase. A reader asking "what does a media row mean" reads `model.py`
      for the shape and `capabilities.py` for the vocabulary.</cons>
    </option>
    <option id="option-b">
      <name>One new module owning the profiles and both new grammars</name>
      <pros>Everything 16A invents lives in one file, so the phase's whole new
      surface is readable in one place and `model.py` is untouched by this
      phase except for the lesson directives. The freeze record enumerates one
      module.</pros>
      <cons>`## MEDIA` and `## ACTIVITIES` would parse outside `model.py`, which
      means either `capabilities.py` imports `model._preamble_section` (reaching
      into another module's private boundary rule) or it writes a second
      section-boundary scanner. `16A-RESEARCH.md`'s Anti-Patterns names the
      second scanner by name as reintroducing "the exact four boundary rules
      that can drift risk the shipped function's own docstring names as the
      reason it exists". It also splits parsing across two modules for the first
      time in this codebase, so "where does markdown become a dict" stops having
      one answer.</cons>
    </option>
    <option id="option-c">
      <name>No new module: capability profiles fold into `model.py`</name>
      <pros>Zero new root-level modules. Every 16A grammar and vocabulary is in
      the file that already owns the format contract, and `model.SPEC` can
      describe all of it in one place.</pros>
      <cons>`model.py`'s stated scope is parsing and validation, and a
      capability's renderer-availability and offline-fallback are rendering
      facts with no document behind them, so this puts presentation semantics
      inside the parser. `model.py` is already the largest module in the
      repository. It also gives CAP-03's output-mode composition
      (`compose_outline`, which calls `graph.outline_projection`) a home inside
      `model.py`, which would make the format contract module import the course
      graph, an edge that does not exist today and that would make `model.py`
      depend on a Phase 14B module.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and record the answer verbatim in
`.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
under a dated heading `## D-16A-2. Where the capability-profile registry lives
and which module owns the media and activity grammar`.

The recorded section must state, in one sentence each: which option was chosen,
the name of any new module, which module parses `## MEDIA`, which module parses
`## ACTIVITIES`, and which module holds `compose_outline`.

What the executor does with each answer:

- **option-a**: proceed as every task in plans 02 through 10 is already written.
  No plan edit is needed.
- **option-b**: before plan 16A-02 Task 2, record in `16A-DECISIONS.md` that
  `model.py` leaves the `files_modified` lists of plans 16A-05 and 16A-06 except
  for its `LINT_CODES` additions; that `capabilities.py` gains `parse_media` and
  `parse_activities`; that those two functions call `model._preamble_section`
  by import rather than writing a second scanner, and that a second scanner is
  refused by name; and that plan 16A-10's freeze record states that parsing now
  lives in two modules and names the reason. Then build it that way.
- **option-c**: before plan 16A-02 Task 2, record in `16A-DECISIONS.md` that no
  `capabilities.py` is created; that every symbol listed in option-a lands on
  `model.py` instead, with the same names; that `model.py` gains an import of
  `graph` for `compose_outline` and that this new dependency edge is stated in
  the freeze record; and that the `import capabilities` assertion in plan
  16A-01 Task 1 step 3 and in every later plan's acceptance criteria is replaced
  by an assertion on `model`. Then build it that way.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`16A-DECISIONS.md` carries a dated `## D-16A-2` heading with the chosen option
id and Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  contains the literal heading `## D-16A-2. Where the capability-profile
  registry lives and which module owns the media and activity grammar`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The recorded section states, in one sentence each, the new module's name, which
  module parses `## MEDIA`, which module parses `## ACTIVITIES`, and which
  module holds `compose_outline`.
- When the answer is `option-b` or `option-c`, the file also carries the
  consequence list this task's action names for that option.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">The module name and boundary appear in every
  import in plans 04 through 10, in every structural-ban assertion, in the
  schema's intended reader, in the 16A freeze record, and in whatever Phases 16B,
  16C, and 17A build on it. Undoing it after the freeze renames a published
  surface.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| plan text to landed code | Every 14A and 14B signature in this phase's research was read from plan text; the precondition check is the only place that boundary is tested before code is written. |
| freeze record to this phase | Whatever the two freeze records say is frozen is what plans 02 through 10 build against; a withheld freeze read as a present one would silently authorize planning against an unproven surface. |
| roadmap gate to freeze record | Phase 14B's freeze is conditional on Phase 13.9 having been walked; a frozen 14B with an unwalked skeleton is a record its own roadmap entry forbids. |
| checkpoint answer to plan set | A recorded decision changes which files later plans may touch and what tokens authored content carries; a decision recorded without being asked would authorize a one-way change nobody chose. |
| pre-phase tree to additivity claim | The golden-parse hashes recorded here are the only evidence that 16A's format changes stayed additive; a hash taken after a 16A edit makes every later assertion pass for the wrong reason. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-01-01 | Tampering | the precondition check worked around instead of obeyed | high | mitigate | Step 8 forbids stubbing, `try` or `except` wrapping, a reduced check set, and recording-and-proceeding by name, and the acceptance criteria assert `capabilities.py` does not exist after a failed run. |
| T-16A-01-02 | Spoofing | a `Freeze withheld` file read as a present freeze record | high | mitigate | Step 4 checks for the absence of the literal `## Freeze withheld` heading in addition to the presence of `## Frozen at`, and states that a file carrying both fails. |
| T-16A-01-03 | Spoofing | a frozen 14B standing in for a walked 13.9 | high | mitigate | Step 5 checks `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` directly rather than trusting `14B-FREEZE.md` to have honored its own gate, and names `13.9 unwalked behind a frozen 14B` as its own halt reason. |
| T-16A-01-04 | Elevation of Privilege | a one-way format or module decision adopted without being asked | high | mitigate | Both decisions are `checkpoint:decision` tasks with `gate="blocking"`, each recording a named option id and a verbatim answer, and each action ends with the sentence that an unanswered checkpoint stops the wave. |
| T-16A-01-05 | Repudiation | a decision recorded with no consequence, leaving the executor to choose after all | high | mitigate | Each option's action block names the exact plan edits that option forces, by plan number and by file, so a non-default answer produces an actionable record rather than a note. |
| T-16A-01-06 | Tampering | an additivity baseline taken after a 16A edit | high | mitigate | Step 7 runs before any code file is touched, prints three literal expected hashes the plan already carries, and the acceptance criteria assert no file outside `.planning/` is created or modified by this task. |
| T-16A-01-07 | Tampering | the shipped lesson and evidence surface drifting between research and execution | medium | mitigate | Step 6 re-checks `_CALLOUT_KINDS`'s membership, `model.GATE_VALUES`, the callability of `runtime.public_item` and `runtime.glossable`, and the `mark_event` human-only refusal live, each with an exact expected stdout. |
| T-16A-01-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; this plan runs only `python -c` and one shipped test against in-repo modules. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-16A-01-09 | Repudiation | a precondition file recording a check that was not run | medium | mitigate | The Dated result line section requires the verbatim stdout of steps 2, 3, 6, and 7, so a fabricated record would have to fabricate four command outputs whose expected values are written into the acceptance criteria. |
| T-16A-01-10 | Information Disclosure | real course or learner content entering the repository | low | accept | This plan creates only two planning markdown files and touches no fixture, bank, or evidence path. Accepted because there is no content path to leak through; `python itembank.py guard .` remains an acceptance check on every later plan that touches `fixtures/`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No module file of any kind. `capabilities.py` is created by plan 16A-02 Task 2
  carrying exactly one seeded profile, and by nothing earlier; plan 16A-04 grows
  it into the full registry.
- No edit to `model.py`, `surfaces/lesson.py`, `runtime.py`, or `evidence.py`.
  This plan reads them and changes none.
- No schema file. `schemas/capability_profile.schema.json` is plan 16A-04's.
- No fixture and no test. `fixtures/lesson_capability_corpus.py` and
  `tests/capability_stress_corpus_tracer.py` are plan 16A-02's, and
  `tests/assessment_authority_adversarial.py` is plan 16A-09's.
- No third checkpoint. Every remaining open question in `16A-RESEARCH.md` is
  resolved in this plan's objective decision table with the research's own
  recommendation, transcribed by Task 1 as `D-16A-3` through `D-16A-8`.
- No visual decision of any kind. Color, spacing, typography, motion, and token
  constants are Phase 17A's, and no 16A plan may name one.
- No freeze record and no freeze amendment. Plan 16A-10 owns the 16A freeze.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped, per the spec-less probe fallback protocol. The
phase's seventeen probe rows are distributed to the plans that own their
requirements: the CAP-01 row is resolved in plan 16A-03's `must_haves`, the
three CAP-02 rows in plan 16A-04's, the CAP-03 row in plan 16A-07's, the five
ACTIVITY-01 rows in plan 16A-06's, the two ACTIVITY-03 rows in plan 16A-09's,
the two A11Y-02 rows in plans 16A-02's and 16A-08's, and the three PORT-01 rows
in plans 16A-02's and 16A-10's. Seventeen rows produce seventeen authored
criteria and zero unresolved drops. This plan holds none of the seventeen
itself; Task 1 step 10 records the classification of the two rows the probe
returned as `unclassified`.

- **The landed surface may differ from plan text (open until Task 1 runs).**
  Every constant value and function signature this plan asserts in Task 1 steps
  2 and 3 was read from `14A-01-PLAN.md` and `14B-01-PLAN.md` through
  `14B-06-PLAN.md`, never from source, because none of those modules existed
  when 16A was planned. Task 1's Deviations found section is where a real
  divergence is recorded; a non-empty Deviations section means plans 02 through
  10 must be re-read against the two freeze records before execution, and this
  assumption is what makes that re-read owed rather than optional.

- **The three golden hashes in Task 1 step 7 were computed on the tree as it
  stood on 2026-08-15.** They are written into the plan so the executor has an
  expected output rather than a bare instruction. If the tree moved for an
  unrelated reason between planning and execution, the found value becomes the
  baseline and the planned value is recorded beside it as a deviation, which
  step 7 states explicitly.
</flagged_assumptions>

<summary_obligations>
`16A-01-SUMMARY.md` records: the precondition result and every deviation the
landed 14A and 14B surfaces showed against their plan text, quoted side by side;
whether Phase 13.9 was walked and which file proved it; the three additivity
baseline hashes as recorded, and whether any differed from the values this plan
carried; the options Weibao chose at Tasks 2 and 3 and every plan edit those
choices forced in plans 02 through 10, by plan number and by file; the seven
role tokens and their `(slug, label)` pairs as finally recorded; which truth was
verified by which command, with the command's actual stdout; and any deviation
from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-01-SUMMARY.md`
when done.
</output>
