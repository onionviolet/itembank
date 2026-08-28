---
phase: 16A
slug: semantic-capability-activity-contract
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-15
planner_filled: 2026-08-15
---

# Phase 16A Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `16A-RESEARCH.md` section "Validation Architecture". The
> Per-Task Verification Map below was filled by the planner on 2026-08-15
> against plans `16A-01` through `16A-10`. Plan `16A-10` Task 3 finalizes the
> Status column, replaces the Estimated runtime placeholder with a measured
> figure, and resolves the sign-off boxes.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None. Direct-execution Python scripts, this project's established convention (not pytest, not unittest) |
| **Config file** | none. See the `tests/*_roundtrip.py` and `tests/*_tracer.py` convention; every test file defines its own local `fail(msg)` helper |
| **Quick run command** | `python tests/<new_test_file>.py` for whichever single new or extended test file the task adds |
| **Full suite command** | `for t in tests/*.py; do python "$t" || exit 1; done` |
| **Estimated runtime** | Unknown for the new 16A files. Do not record a figure until one has been measured on this machine. Plan 16A-10 Task 3 step 6 replaces this cell with the measured full-suite figure and names the machine and Python version. |

---

## Sampling Rate

- **After every task commit:** the quick run command for that task's specific
  new or changed test file, plus `python itembank.py guard .` on any task that
  touches `fixtures/`.
- **After every plan wave:** the full suite command.
- **Before `/gsd-verify-work`:** full suite green, the portable rich-lesson
  stress corpus tracer green, the adversarial suite green, and
  `python itembank.py guard .` reporting `0 offending files`.
- **Additivity, after every task that touches `model.py` or
  `surfaces/lesson.py`:** re-verify the two golden SHA-256 values recorded in
  `16A-PRECONDITION.md`'s Additivity baseline section. A changed value means a
  format change was not additive.
- **Freeze gate:** no 16A freeze record is written on a red stress-corpus
  tracer, a red adversarial suite, a missing or rejecting human review, or an
  unresolved leak finding from plan 16A-09 (mirrors 14A-04 Task 4, 14B-06,
  15A-06, and 15B-07).
- **Max feedback latency:** to be measured, not asserted.

---

## Phase Requirements -> Test Map

Seeded from `16A-RESEARCH.md`. Expanded into the Per-Task Verification Map
below.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CAP-01 | Every semantic teaching role parses and renders in both continuous reader and guided modes; an unknown optional semantic renders its fallback with a warning; an unknown required semantic fails safely | Tracer scenario over the stress corpus | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap, owned by 16A-02 T3 |
| CAP-02 | A declared capability's full support profile is inspectable; a capability with its renderer marked unavailable shows the static instructional path | Unit assertions over the capability registry plus one tracer scenario | `python tests/capability_profile_check.py` and `python tests/capability_stress_corpus_tracer.py` (both new) | Wave 0 gap, owned by 16A-04 |
| CAP-03 | Two registered output modes (outline, glossary) compose from one stress-corpus lesson's shared schemas; one unregistered mode stays a named backburner catalog entry | Tracer scenario | `python tests/output_mode_check.py` and `python tests/capability_stress_corpus_tracer.py` (both new) | Wave 0 gap, owned by 16A-07 |
| ACTIVITY-01 | Every declared activity in the stress corpus carries all ten fields; one unsupported response form falls back to its declared static equivalent | Tracer scenario | `python tests/activity_declaration_check.py` and `python tests/capability_stress_corpus_tracer.py` (both new) | Wave 0 gap, owned by 16A-06 |
| ACTIVITY-03 | A scripted agent, a note, and an import each attempt to leak a key, invent a score, auto-grade prose, or edit a frozen sitting; every attempt is refused | Adversarial fixture calling real `runtime.py` and `evidence.py` functions | `python tests/assessment_authority_adversarial.py` (new) | Wave 0 gap, owned by 16A-09 |
| A11Y-02 | The localization fixture set (RTL, mixed code and math direction, CJK, combining marks, long strings, localized numbers and units) renders inside the stress corpus without corruption | Tracer scenario with byte-level assertions on preserved UTF-8 | `python tests/localization_render_check.py` and `python tests/capability_stress_corpus_tracer.py` (both new) | Wave 0 gap, owned by 16A-08 |
| PORT-01 | The stress corpus, opened outside the app with every derived HTML, index, and cache deleted, stays readable; core meaning, captions, citations, and fallbacks survive; derived views rebuild | Tracer scenario following the golden-parse-snapshot precedent | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap, owned by 16A-02 T3 and 16A-10 T1 |

---

## Per-Task Verification Map

Filled by the planner 2026-08-15. The Status column reads `planned` until the
task executes; plan `16A-10` Task 3 step 6 confirms every row is filled and
resolves the column.

The stress-corpus tracer's expected scenario count grows monotonically as plans
land: 2 after 16A-02, 5 after 16A-03, 7 after 16A-04, 8 after 16A-05, 10 after
16A-06, 12 after 16A-07, 13 after 16A-08, 14 after 16A-09, and 18 after 16A-10.
The adversarial suite's expected attack count is 8 after 16A-09 Task 1, 14 after
Task 2, and 18 after Task 3. A plan whose tracer line does not match its
expected count has added or lost a scenario and its summary must say which.

| Plan | Task | Req ID | Behavior | Test Type | Automated Command | Assertion function | Status |
|------|------|--------|----------|-----------|-------------------|--------------------|--------|
| 16A-01 | T1 preconditions | all seven | 14A and 14B landed with the frozen surface 16A was planned against, 13.9 walked, the shipped lesson and evidence surface unmoved, and the additivity baseline recorded | Precondition check, halts by name | `python -c` assertion in the plan's verify block | inline assertions plus `16A-PRECONDITION.md` | planned |
| 16A-01 | T2 D-16A-1 | CAP-01 | The semantic-role representation and the seven role tokens are decided by a human, not adopted | Blocking checkpoint | none (checkpoint) | `16A-DECISIONS.md` heading `## D-16A-1` | planned |
| 16A-01 | T3 D-16A-2 | CAP-02, CAP-03 | The capability registry's module boundary and the media and activity grammar's owner are decided by a human | Blocking checkpoint | none (checkpoint) | `16A-DECISIONS.md` heading `## D-16A-2` | planned |
| 16A-02 | T1 parse layer | CAP-01, A11Y-02, PORT-01 | Three lesson directives parse with documented defaults, never raise on a malformed value, and a bank carrying none of them parses unchanged | Unit assertions plus corpus build | `python -c` assertion in the plan's verify block; `python tests/protocol_roundtrip.py`; `python tests/lesson_roundtrip.py` | inline assertions plus `build_thin_slice` | passing |
| 16A-02 | T2 registry and render | CAP-01, CAP-02 | One capability profile resolves, one new role registers, `lesson_page` gains `mode`, and both modes render the same containers | Unit assertions | `python -c` assertion in the plan's verify block; `python tests/lesson_roundtrip.py`; `python tests/presentation_roundtrip.py` | inline assertions | passing |
| 16A-02 | T3 the tracer | CAP-01, CAP-02, A11Y-02, PORT-01 | One authored block travels parser, registry, and both renderers end to end; the shipped format did not move while it did | Tracer scenario | `python tests/capability_stress_corpus_tracer.py` | `scenario_thin_slice`, `scenario_additivity_golden_parse` | passing |
| 16A-03 | T1 six roles plus catalog | CAP-01 | All fourteen CAP-01 roles have a live rendering path and a machine-readable catalog says which is which | Unit assertions plus tracer | `python tests/capability_stress_corpus_tracer.py`; `python tests/gate_roundtrip.py`; `python tests/visual_roundtrip.py` | `scenario_fourteen_roles` | passing |
| 16A-03 | T2 unknown semantics | CAP-01 | A semantic can be marked required; an unknown optional degrades unchanged with a warning; an unknown required renders a named refusal carrying the author's text | Unit assertions plus tracer | `python tests/capability_stress_corpus_tracer.py`; `python tests/lesson_roundtrip.py` | `scenario_unknown_semantics` | passing |
| 16A-03 | T3 example order plus scenarios | CAP-01 | The worked-example-first default fires, is suppressed only by an override carrying a reason, and an override with no reason produces both codes | Tracer scenarios | `python tests/capability_stress_corpus_tracer.py` | `scenario_example_order` | passing |
| 16A-04 | T1 full registry | CAP-02 | Fifteen profiles carry all six CAP-02 fields; duplicate registration refuses; a missing name returns None; order is stable | Unit assertions | `python tests/capability_profile_check.py` | `capability_profile_check.main` | passing |
| 16A-04 | T2 published schema | CAP-02 | The profile schema is accepted by the shipped validator, validates all fifteen entries, and refuses four deliberately broken ones | Unit assertions plus schema coupling | `python tests/capability_profile_check.py`; `python schema_validate.py --all` | `capability_profile_check.main` | passing |
| 16A-04 | T3 static instructional path | CAP-02 | An unavailable renderer shows its declared static path, and the shipped gate-less check render is byte identical | Tracer scenarios | `python tests/capability_stress_corpus_tracer.py`; `python tests/gate_roundtrip.py` | `scenario_capability_profiles`, `scenario_unavailable_renderer` | passing |
| 16A-05 | T1 media registry | CAP-02 | Media assets declare all six fields through the one boundary rule; a malformed registry lints rather than raises | Unit assertions | `python tests/capability_stress_corpus_tracer.py`; `python tests/model_surface_roundtrip.py` | `scenario_media_metadata` plus `parse_media` | passing |
| 16A-05 | T2 figure renderer | CAP-02, PORT-01 | A present asset renders a credited figure, a missing one renders its description, a remote one renders a link and loads nothing, an unknown reference says so | Unit assertions | `python tests/capability_stress_corpus_tracer.py`; `python tests/daemon_roundtrip.py` | `scenario_media_metadata` | passing |
| 16A-05 | T3 media scenario | CAP-02, PORT-01 | Four asset states render correctly, alternatives survive in the Markdown, and rights are proven declared and not enforced | Tracer scenario | `python tests/capability_stress_corpus_tracer.py` | `scenario_media_metadata` | passing |
| 16A-06 | T1 activity registry | ACTIVITY-01 | Eleven columns and five closed vocabularies parse through the one boundary rule; document order preserved; parsing idempotent | Unit assertions | `python tests/activity_declaration_check.py` | `activity_declaration_check.main` | passing |
| 16A-06 | T2 activity lint plus fallback | ACTIVITY-01 | Eleven lint codes fire correctly; an unsupported response form is a warning with a fallback that reaches a real surface | Unit assertions | `python tests/activity_declaration_check.py`; `python tests/gate_roundtrip.py` | `activity_declaration_check.main` | passing |
| 16A-06 | T3 ten purposes plus authority proof | ACTIVITY-01, ACTIVITY-03 | Ten purposes over eight shipped forms; no ninth type minted; a declared policy proven not to be an authority | Tracer scenarios | `python tests/capability_stress_corpus_tracer.py` | `scenario_activity_declarations`, `scenario_unsupported_response_form` | passing |
| 16A-07 | T1 composers plus catalog | CAP-03 | Two modes compose from shared schemas; eight are parked with four validated fields each | Unit assertions | `python tests/output_mode_check.py` | `output_mode_check.main` | passing |
| 16A-07 | T2 derivation proof | CAP-03, PORT-01 | Every string in a composed record comes from the canonical file; delete and rebuild reproduces equal records | Tracer scenarios | `python tests/capability_stress_corpus_tracer.py` | `scenario_output_modes`, `scenario_backburner_catalog` | passing |
| 16A-08 | T1 direction opt-in plus corpus | A11Y-02 | Explicit `[LESSON-DIR: auto]` gives each text run its own resolution; a lesson declaring nothing renders unchanged | Unit assertions | `python tests/localization_render_check.py`; `python tests/lesson_roundtrip.py` | `localization_render_check.main` | planned |
| 16A-08 | T2 preservation proof | A11Y-02, PORT-01 | Seven cases round-trip byte for byte; no normalization anywhere; a bidi override survives; an invalid direction degrades to a named finding | Tracer scenario with SHA-256 comparisons | `python tests/capability_stress_corpus_tracer.py` | `scenario_localization` | planned |
| 16A-09 | T1 agent and note attackers | ACTIVITY-03 | Two attackers fail all four attacks against the real shipped gates; no mock anywhere | Adversarial suite | `python tests/assessment_authority_adversarial.py` | `attacker_agent`, `attacker_note`, eight `attack_*` | planned |
| 16A-09 | T2 import attacker plus probes | ACTIVITY-03 | An import fails all four; `public_item` asserted at three boundary points; a pending prose mark proven uncoercible | Adversarial suite | `python tests/assessment_authority_adversarial.py` | `attacker_import`, `attack_boundary_public_item`, `attack_precision_pending_mark` | planned |
| 16A-09 | T3 16A's own new mouths | ACTIVITY-03, CAP-01, CAP-02 | The excerpt callout, the media alt, the activity fallback, and the composed glossary are each attacked through the existing gate; no second leak detector exists | Adversarial suite plus tracer | `python tests/assessment_authority_adversarial.py`; `python tests/capability_stress_corpus_tracer.py` | four `attack_16a_*`, `scenario_assessment_authority` | planned |
| 16A-10 | T1 freeze corpus plus portability | all seven | The whole freeze-gate corpus builds and walks; the medical case shows no premature reveal; the disputed timeline preserves disagreement; PORT-01 is proven by delete and rebuild | Tracer scenarios plus measured report | `python tests/capability_stress_corpus_tracer.py`; `python tests/assessment_authority_adversarial.py`; full suite | `scenario_medical_case`, `scenario_disputed_timeline`, `scenario_section_order`, `scenario_portability` | planned |
| 16A-10 | T2 legibility review | all seven | A human judges whether fifteen profiles, eight triggers, three copy strings, and seven labels are legible and honest | Blocking human checkpoint | none (checkpoint) | `16A-REVIEW.md` verdict word | planned |
| 16A-10 | T3 freeze or withhold | all seven | Five freeze legs re-evaluated against a re-run tree; the record carries exactly one of the two headings | Automated shape assertion plus re-run evidence | `python -c` assertion in the plan's verify block; full suite; `python itembank.py guard .` | `16A-FREEZE.md` heading check | planned |

---

## Wave 0 Requirements

Seeded from `16A-RESEARCH.md` Wave 0 Gaps; ownership assigned by the planner
2026-08-15. All 16A test infrastructure is new direct-execution Python scripts
beside the existing `tests/` set. No framework and no install step.

- [x] `tests/capability_stress_corpus_tracer.py`, the freeze-gate tracer
  covering CAP-01, CAP-02, CAP-03, ACTIVITY-01, A11Y-02, and PORT-01. **Owner:
  plan 16A-02 Task 3** creates it carrying `scenario_thin_slice` and
  `scenario_additivity_golden_parse`; every later plan appends its own
  `scenario_*` functions rather than starting a second tracer. Follows
  `tests/evidence_roundtrip.py`'s real shipped convention (`fail(msg)`, standard
  library only, direct execution) layered with the `TRACER: N passed, M
  skipped, 0 failed` summary-line convention `16A-PATTERNS.md` records as a
  plan-text analog from 14A and 14B.
- [ ] `tests/assessment_authority_adversarial.py`, ACTIVITY-03's dedicated
  adversarial suite, calling real `runtime.py` and `evidence.py` functions.
  **Owner: plan 16A-09**, Task 1 creating it and Tasks 2 and 3 growing it to
  eighteen attacks. Final line convention: `ADVERSARIAL: N attempted, N
  refused, 0 succeeded`.
- [x] `fixtures/lesson_capability_corpus.py`, the synthetic stress-corpus
  generator (fictional content, deterministic literal constants, no `random`).
  **Owner: plan 16A-02 Task 1** creates it with `build_thin_slice`; plans
  16A-03 through 16A-10 each add their own builders; plan 16A-10 Task 1 adds
  `build_all_16a` as the one entry point, plus `build_medical_case` and
  `build_disputed_timeline` the freeze gate names by name.
- [ ] The additivity proof. **Owner: plan 16A-01 Task 1** records the baseline
  as two literal SHA-256 values in `16A-PRECONDITION.md` before any 16A grammar
  exists; **plan 16A-02 Task 3** asserts them in
  `scenario_additivity_golden_parse`, reading them from that file rather than
  carrying them as literals; every later plan re-asserts them in its acceptance
  criteria. The shipped `fixtures/lesson_golden_phase3_parse.json` and
  `fixtures/lesson_golden_phase3_content.txt` are extended by nothing and
  replaced by nothing.
- [x] `capabilities.py` and its unit assertions. **Owner: plan 16A-02 Task 2**
  creates the module with exactly one seeded profile as part of the tracer
  slice; **plan 16A-04** grows it to fifteen profiles and creates
  `tests/capability_profile_check.py`; **plan 16A-06** adds
  `activity_fallback`; **plan 16A-07** adds the output-mode composers and
  creates `tests/output_mode_check.py`.

Three further unit files are created beyond the research's original gap list,
each owned by the plan that needs it: `tests/activity_declaration_check.py`
(plan 16A-06 Task 1) and `tests/localization_render_check.py` (plan 16A-08
Task 1), plus `tests/output_mode_check.py` named above.

*(No pre-existing test infrastructure covers this phase's seven requirements
directly; all listed gaps are new. The infrastructure the new tests call,
`runtime.py`, `evidence.py`, and `model.py`'s parsing, is shipped and
unchanged.)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Freeze-gate contract-legibility review | all seven | A green test proves a field is present and a refusal fires. It cannot prove that a capability profile's `known_limits` names the limitation a reader would actually hit, that a backburner trigger is a condition someone could test, that the unsupported-block and media copy make sense to a learner, or that the seven new role labels mean in English what the roles are for. An agent never self-certifies its own contract. | Plan `16A-10` Task 2's `<how-to-verify>` block, nine numbered steps: read `16A-TRACER-REPORT.md` end to end and note every leg not marked `passed`; run both suites and confirm `TRACER: 18 passed, 0 skipped, 0 failed` and `ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded`; read the fifteen capability profiles as prose and answer three questions about each; read the eight backburner entries and answer three questions about each; read the three user-visible copy strings as a learner; read the seven role labels and judge whether you would reach for the right one when authoring; build the corpus with `build_all_16a` and read the medical evolving-case and disputed-timeline lessons as plain text with no renderer; read plan 16A-09's summary and state whether any recorded leak should withhold the freeze; record a verdict of `accept`, `accept-with-findings`, or `reject` in `16A-REVIEW.md` with a signature and a date. |
| The two decision checkpoints | CAP-01, CAP-02, CAP-03 | Both are one-way format and module-boundary decisions other phases author content against. `PLANNING-DIRECTIVES.md` section 2 rule 1 stops a planning session for exactly this class, and an unanswered checkpoint stops the wave rather than receiving a silent default. | Plan `16A-01` Tasks 2 and 3: read the three options each presents with their recorded pros and cons, choose one by its option id, and let the executor record the answer verbatim under the dated heading. Each task's action block names the exact plan edits a non-default answer forces, by plan number and by file. |

---

## Validation Sign-Off

Resolved by plan `16A-10` Task 3 step 6, not by the planner.

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency measured, not asserted
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
