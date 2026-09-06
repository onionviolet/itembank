# Feature opportunity audit, 2026-09-06

Status: evidence-backed review and proposed routes. No implementation or scope approval.
Owner: feature opportunity audit agent for this report, owning phase maintainers for follow-up.
Origin: [saved audit prompt](../FEATURE-OPPORTUNITY-AUDIT-PROMPT.md) and the 2026-09-06 feature-opportunities entry in [the inbox](../USER-VISION-INBOX.md).

The strongest opportunity is to connect existing learning capabilities into a
journey a learner can finish. Notes, transfer, source comparison, review, and
resume already have substantial contracts. Their presence in those contracts
does not prove that the learner can reach them. The next useful addition is
usually a missing connection or authoring workflow rather than another widget.

## Evidence inventory and limits

This is a bounded lifecycle audit, not an exhaustive whole-vision audit.
Read scope was this repository's planning records, code, and synthetic tests.
Write scope is this report and additive audit records in the existing ledger.
The inbox already captures the product request verbatim. Running its saved
prompt adds no new product quotation. No learner files or external source
roots were inventoried. No private material was sent to an external service.
Only public documentation URLs were opened for the two external checks below.

Snapshot: HEAD was `0fc6923` when sampled, with pre-existing uncommitted work.
This is working-copy evidence, not a claim about a release. Concurrent edits
mean future execution must recheck its own base. Existing work was preserved.

| ID | Evidence inspected | What it supports and what it cannot prove |
|---|---|---|
| E1 | `AGENTS.md`, `AGENT-WORKFLOW.md`, `SOURCE-TO-COURSE.md`, planning directives, STATE front matter/current position, REACH including its September 6 refinement | Authority and current milestone boundaries. STATE names 19A-03 as latest, but code has later operations. Do not use that summary as the current feature inventory. |
| E2 | `USER-VISION.md` August 13 source-to-course, feature breadth, reuse, guided notes and omissions entries, August 24 feedback entry, August 26 reading entry, plus the inbox's recent feature/readability entries | Desired experience. Interpretations were kept distinct from user words. Earlier percentage restrictions are not revived over the later user override. |
| E3 | `.planning/ROADMAP.md` sequence and relevant 16A/16B/16C/17/18/19 references, REQUIREMENTS NOTE/STRATEGY/APP/CAP/activity families, 19B/19C/19D/19E seeds | Existing ownership and future commitments. Unchecked requirements and completed summaries are neither positive nor negative proof of working UI. Root ROADMAP was not used to override active sequencing. |
| E4 | Phase 16 `06-feature-style-atlas.md` sections 4, 9, 12, `05-learning-program-landscape.md` pattern inventory and sources, `12-active-annotation-notes.md` taxonomy/prototype routes, `14-synthesis.md` loops and portfolio, `13-expected-capabilities-omissions.md` lifecycle/readiness rows | Reuse baseline, alternatives, existing dispositions. These are dated research records, not September product observations. |
| E5 | `2026-09-05-open-source-absorption.md` confidence analysis and existing ledger entries for confidence, generators, source reading, time axis, paper intake, bilingual reader and agent doors | Avoids rediscovering registered opportunities. External product claims in that report were not all refreshed. |
| E6 | `surfaces/daemon.py::API_ROUTES`, `surfaces/course_ops.py::_op_bind_treatment`, `_op_treatments`, `_op_recommend`, `_op_apply_recommendation` and operation dispatch symbols | Treatment, autonomy, replay/reversal and recommendation doors exist beyond STATE's snapshot. Route existence alone does not establish visible navigation or usable generated lessons. |
| E7 | `notes.py::note_record`, `resolve_anchor`, note document writer/reader, `note_outputs.py::content_instance`, `project_notebook_page`, `render_mode`, searches for their callers under `surfaces/` | Learner ownership, anchor states and portable projections exist. Sampled surface searches found no note API consumers. The writer does not itself provide a capture UI. |
| E8 | `surfaces/lesson.py::_gloss_trigger_html`, `_gloss_panel_html`, `_reader_nav_html`, `guided_stages`, `lesson_page`, `surfaces/ia.py::deep_link_target`, `loop_resume_state`, `selection.py::filter_by_pair`, `filter_by_prereq`, `retention.py::recommendation`, `model.py::ACTIVITY_PURPOSES` | Concrete components for help, navigation, pair practice, review and transfer metadata. `loop_resume_state` reads arguments and no durable record, so it cannot establish saved passage-level resume. |
| E9 | `17B-03-learner-pass.md` setup and first-use observations, `17C-AUDIT.md` loss table and September 5 addendum | Prior learner tracer used a CLI sitting and later DOM-driven controls after pointer/screenshot problems. Human visual and screen-reader legs remain owed. All five restore losses are now named, but their content still does not cross. |
| E10 | Fresh runs: `tests/note_trio_roundtrip.py`, `tests/note_promotion_roundtrip.py`, `tests/course_ops_roundtrip.py`, `tests/ia_route_roundtrip.py` | Observed automated behavior. Note trio: 9 passed. Promotion: 8 passed. Course operations exited 0. IA routes: 26 passed. These are synthetic/backend/HTTP checks, not a new browser walkthrough. |

Large modules were located by symbols and sampled rather than audited end to
end. A note-module read produced truncated output and is not treated as a
complete inspection. Runtime scoring internals, all source adapters, all
strategy implementations, mobile devices, assistive technology, installed-app
flows, real courses, settings endpoints, and the full historical research
corpus were not inspected. No human accessibility or instructional-quality
approval is claimed. No end-to-end UI claim in this report rests only on tests.

### Current primary-source checks

X1: The [Anki manual, Daily Limits](https://docs.ankiweb.net/deck-options.html#daily-limits),
accessed 2026-09-06, describes review caps, a today-only override and disclosure
of reviews hidden by a limit. The inspected page did not establish a publication
date. The useful pattern for F5 is an explicit workload choice that leaves
unfinished work visible. A cap on item count is not a prediction of minutes.

X2: [EPUB Reading Systems 3.3](https://www.w3.org/TR/epub-rs-33/),
W3C Recommendation, accessed 2026-09-06, provides a reading-system reference
for navigation and accessible content presentation. It is a standard, not
evidence that an itembank source-comparison UI works or improves learning.
The practical implication is to verify ordinary reading access alongside rich
lesson behavior rather than treating file opening as the whole reading job.

No new learning-efficacy claim is made. Expected benefits below are hypotheses.
The existing research remains the starting point if an outcome study is needed.

## Coverage matrix

Delivery, timing, and evidence are separate axes. A durable disposition appears
in the opportunity register and is not a delivery status. No whole UI journey
is classified as working end to end without fresh observation in this audit.

| Learner job | Delivery | Timing | Evidence | Remaining question and owner |
|---|---|---|---|---|
| First use, shelf, sample, orientation | Partially working | Current milestone obligation | E9 prior observations, E10 HTTP behavior | Can a new learner follow visible controls without guessed URLs? 19D, with Phase 18 cold-install leg. |
| Discover, reconcile, bind existing material | Partially working | Current milestone obligation | E6/E10 behavior, E1 contract | Multi-root identity and rights exist as contracts, but full learner discovery is not freshly observed. 19A/19D, 14A/14C owners. |
| Course outline, objectives, treatment | Partially working | Current milestone obligation | E6/E10 behavior | Several operations work through API and CLI. Full source-to-accepted-course path still needs 19B/19D evidence. |
| Read sources, navigate, compare | Partially working | Current milestone obligation | E8 code, IL-20260826-06 | Opening a bound source does not prove passage-specific comparison and return. Source owner, 19D. |
| Guided lessons, terms, worked examples | Partially working | Current milestone obligation | E8 code, E9 recorded tracer | Authorability and useful plain-file treatment must be checked on a representative unit. 19D. |
| F1 contextual help and return | Partially working | Current milestone obligation for existing help, optional extension for new detour orchestration | E8 code, inference | Glossary and prerequisite components exist. Complete selected-passage detour unknown. |
| F2 personal confusion notebook | Backend-only overlap | Optional extension | E7/E8 code, recommendation | Connect private note to reviewed comparison practice without a new assessment authority. |
| F3 learning builds notes | Backend-only in sampled surface integration | Current milestone obligation | E7/E10 behavior | Persisted/projection tests do not create a learner-facing note capture door. Route the reach gap to 19D and its note owner. |
| F4 transfer activities | Partially working | Current milestone obligation | E8 metadata and E3 requirements | Authored purpose can say transfer. A subject reviewer must establish changed demand and a reachable activity. |
| F5 time-aware continuation | Previously considered, partial review primitives | Optional extension beyond exact resume obligation | E8 code, IL-20260826-07 | No time-budget planner was established. Exact saved reading return remains a separate existing obligation. |
| Practice, formal tests and feedback | Partially working at course-journey level | Current milestone obligation | E9 prior CLI sitting, E10 HTTP review | Existing runtime remains authority. Validate visible course links and mode-specific feedback in 19D. |
| Evidence, cumulative review, remediation | Partially working | Current milestone obligation | `retention.recommendation`, selection filters | A reasoned due queue is not a complete miss-to-reteach-to-transfer journey. |
| Confidence calibration | Previously considered, field backend-only for this use | Optional extension | E5 and fresh zero consumer hits in retention/selection/blueprint/progress_claims/auditor | Reuse IL-20260905-01. Verify surface collection before proposing a diagnostic. |
| Return after absence | Partially working primitives | Current milestone obligation for resume, optional extension for change recap | E8, E4 | Resume location, due work and source changes need distinct explanations. |
| Search across source, note and lesson | Planned baseline, current UI unknown | Current milestone obligation under APP-04 | E3/E4, limited surface search | Search-entry and result-quality tracer is needed. No conclusion that all search is absent. |
| Accessibility and phone use | Partially verified | Current milestone obligation | E9 recorded limitations and owed legs | Sampled code or automated tests cannot sign keyboard/touch/screen-reader equivalence. |
| Offline learning and source availability | Partially working | Current milestone obligation | E1/E3, E9 | Local core can exist while a referenced source or media file is unavailable. Verify one actual offline unit. |
| Maintenance, export, restore | Partially working with explicit loss | Current milestone obligation for truthful loss, future decisions for carrying omitted state | E9 September 5 addendum | Provenance, rights, attempt state, unregistered files and media remain named losses. |
| Agent construction, review, accept, undo | Partially working, 19B planned | Current milestone obligation | E6, `surfaces/agent_operation.py::start/accept`, seeds | Existing recommendation doors do not prove Agent-tab proposal acceptance and undo. |
| Bilingual/audio, paper intake, broader outputs, sync | Previously considered or planned | Future planned work or optional extension | Existing ledger and E4 portfolio | Preserve registered/backburner routes rather than re-proposing a new platform. |

## Opportunity register

Costs are relative estimates, not measured time or token savings. Each entry
states a benefit hypothesis and a falsifier. Authority profiles below supply
the shared object, ownership, rights, accessibility, offline and recovery rules.
They describe candidate acceptance requirements, not verified implementation.

### Shared authority and recovery profiles

| Profile | Durable object, owner and truth | Boundaries and degraded behavior |
|---|---|---|
| P1 reading/help | Accepted source or lesson revision belongs to its content owner. Position is learner navigation state. Help is authored content or a labeled agent draft. | Read/quote/transform/remote-process grants are separate. No remote help by implication. Use stable locator plus revision, preserve return state, flag stale targets. Keyboard/touch opens and dismisses help with focus restored. Plain files retain terms, citations and explanations. Offline uses accepted content and names unavailable help. Runtime controls assessment disclosure. |
| P2 notes | Learner-owned note document and sidecar, with original wording, role, objective links and revision. Projections are disposable. | Save does not submit or promote. A wrong claim remains a private claim. Review requires explicit source support. Remote processing/export needs its own grant. Linear Markdown stays useful. Orphaned anchors retain objective links. External edits cause conflict, not overwrite. Interrupted saves preserve the last accepted document. |
| P3 assessment/evidence | Accepted bank and blueprint owned by course builder, session and attempt evidence owned by runtime, settled prose reviewed under runtime policy. | One parser/scorer/evidence writer. Transfer metadata never grades an explanation. No early key disclosure through help, search or notes. Offline sessions follow the same mode. Version changes never transfer historical evidence automatically. Text alternatives must preserve the construct. |
| P4 planning/return | Accepted course, scope and evidence remain canonical. Suggested queue, change recap and duration are derived views. Learner chooses among eligible actions. | Explain denominator and missing evidence. Unknown duration stays unknown. Persist actual stopping state, never invented completion. Read prior accepted revision to explain changes, or disclose that no comparison is available. Offline uses a dated last-valid view. Conflicts remain visible and reversible. |
| P5 maintenance/search | Accepted files, rights and journal remain canonical. Search/readiness indexes and loss previews are derived. Learner owns export decisions. | Search only approved roots and allowed disclosure. Do not reveal private notes through shared results. Unknown rights remain restrictive. Offline results distinguish cached text from available files. Reindex recovers derived state. A restore validates its manifest and names losses. No automatic replay of old rights or overwritten local edits. |
| P6 author/reviewer | Bounded draft, its cited base revision, review record and accepted revision. Builder proposes and reviewer accepts. | Generation does not publish. Rights and egress apply per input. Validate semantic and plain-file output, then compare-and-swap acceptance and journaled undo. A failed model leaves accepted material usable. Readability suggestions never silently alter warnings, keyed meaning or difficulty. |

### F1: contextual stuck detour

Existing ID: IL-20260906-01. Proposed disposition: Prototype, not approved.
Job: understand a confusing passage and continue reading. Before: use an
available glossary or leave the lesson to seek an explanation. After: select
the passage, choose an accepted definition, prerequisite refresher or worked
example, and return to the exact place. Alternative: a pinned reference panel
instead of a modal detour. Use the smaller pattern that passes the return test.

Overlap: E8 glossary helpers, `selection.filter_by_prereq`,
`surfaces.ia.deep_link_target`, atlas MF-01/MF-08/MF-18. Gap is the combined
entry point, grounding and return flow, not proof of absent help capability.
Expected benefit: less context loss. Evidence: code-backed components, weak
evidence for the complete journey. Profile P1 and P3. Dependencies: stable
anchors, authored help targets, runtime disclosure. Cost estimate: medium,
driven by anchor/focus restoration and content review. Owner/route: 19D
existing navigation verification first, optional P-A prototype only if a gap
remains. Falsifier: ordinary glossary/source links complete the job with equal
or fewer errors and no extra navigation burden.

### F2: personal confusion notebook

Existing ID: IL-20260906-02. Proposed disposition: Prototype, not approved.
Job: distinguish concepts repeatedly confused. Before: save a free note and
manually find practice. After: a private contrast note links examples and a
reviewed comparison set, then records the learner's revised explanation.
Alternative: objective-linked questions inside the existing notebook instead
of a separate confusion destination.

Overlap: `notes.note_record` roles, `note_outputs.project_notebook_page`,
`selection.filter_by_pair`, NOTE-02, synthesis section 12.2 remediation chain.
Gap: the note-to-reviewed-practice connection and usable capture. Expected
benefit: make recurring distinctions retrievable. Evidence: backend support,
unproven learner benefit. P2/P3. Dependencies: F3 entry point, pair-authored
items, source-backed reviewer. Cost estimate: medium, dominated by contrast
quality and stale links. Owner/route: note/selection owners, optional follow-up
after 19D. Smallest check: save a deliberately wrong contrast, propose practice,
and show that neither note nor draft becomes a key. Falsifier: the link produces
irrelevant sets or existing pair practice already solves the retrieval job.

### F3: learning produces editable notes

Existing ID: IL-20260906-03. Proposed disposition: Core for the existing
NOTE-01/02 reach obligation, not a new format commitment.
Job: leave a learning session with one's own usable study document. Before:
note projections and persistence can be exercised through Python tests. After:
save a prediction, explanation and correction while learning, edit them later,
and open the resulting Markdown outside the product.

Overlap: E7, E10, NOTE-01/02, atlas MF-11/MF-13/MF-16, note prototype A.
Remaining gap: no surface callers of the sampled note APIs were found.
Expected benefit: preserve learner work without manual file repair. Evidence:
strong synthetic persistence/projection evidence, no live capture verification.
P2/P6. Dependencies: existing note writer, learner save controls, source
locators and revision conflict handling. Cost estimate: medium, integration
and save/reopen ergonomics dominate. Owner/route: 19D records the NOTE owner
defect and resolves the existing obligation through that owner. Do not assume
19A's course operations automatically include notes. Smallest verification:
P-A below. Falsifier: a pre-existing discoverable capture route passes P-A,
in which case add verification evidence rather than duplicate controls.

### F4: changed-context transfer challenges

Existing ID: IL-20260906-04. Proposed disposition: Core under existing
ACTIVITY-02 and course-quality obligations.
Job: apply the idea beyond the example just seen. Before: an activity may be
labeled transfer without a demonstrated changed demand. After: the learner
chooses a method in a changed situation, explains its limits, or diagnoses a
broken solution, with the appropriate review path.

Overlap: `model.ACTIVITY_PURPOSES`, REQUIREMENTS activity family, atlas MF-04
and MF-07, synthesis section 7.3. Gap: author/reviewer evidence and reachability,
not a need for a ninth item type. Expected benefit: expose dependence on copied
procedures. Evidence: contract and metadata support, unverified instructional
quality. P3/P6. Dependencies: accepted examples, explicit changed dimensions,
rubric or deterministic response contract. Cost estimate: medium to high,
subject review dominates. Owner/route: 19D representative-unit review, 15B/16A
quality owners. Smallest verification: P-B. Falsifier: changing nouns or numbers
is the only difference, or the task assesses an untaught prerequisite.

### F5: time-aware continuation

Existing ID: IL-20260906-05, overlap IL-20260826-07 course time axis.
Proposed disposition: Prototype for time-budget choice. Exact resume remains
an existing Core obligation.
Job: use a short interval and stop safely. Before: a due-objective recommendation
or generic resume cue. After: choose review-only, a full lesson, or an estimated
short activity, see the reason and uncertainty, and resume actual saved state.
Alternative: learner-set item cap with no duration prediction, following X1's
workload transparency pattern.

Overlap: `retention.recommendation`, `cap_decision`, `subject_pacing`,
`surfaces.ia.loop_resume_state`. Gap: that helper reads no durable state and
does not prove an exact passage save. No time-budget implementation was
established by the bounded search. Expected benefit: fewer abandoned sessions.
Evidence: partial primitives, recommendation. P4/P3. Dependencies: real return
state, activity boundaries, enough duration observations or explicit unknown.
Cost estimate: medium, timing uncertainty and sealed-test interruption dominate.
Owner/route: verify resume in 19D first, optional prototype after it. Smallest
check: P-C. Falsifier: a simple count cap is equally useful, or duration estimates
repeatedly lead to unsafe stopping points.

### O6: source comparison with scoped terminology

Reuse IL-20260826-06, synthesis 12.2 source comparison, atlas MF-06/MF-09.
Proposed disposition: Core existing reading obligation. Delivery: partially
working. Timing: current obligation. Evidence: E8 code plus research contract.
Job/flow: from opening separate sources and losing context to comparing two
cited passages while keeping source identity, disputed claims and term scope.
Gap: comparison and scoped lookup are not established by a source link.
Benefit: verify a claim and avoid conflating the same symbol across subjects.
P1/P5. Dependencies: locators and accepted source bindings. Estimated cost:
medium, extraction fidelity and narrow-screen layout. Owner: source/14C,
verified through 19D before optional presentation work. Smallest check: history
sources disagree and math uses `m` differently, with a stacked text fallback.
Falsifier: ordinary labeled links already preserve context and distinctions.

### O7: confidence-informed remediation

Reuse IL-20260905-01, proposed disposition Registered as already recorded.
Delivery: previously considered with backend field support. Timing: optional
extension. Evidence: E5 plus zero search hits in the five named consumers.
Job/flow: from undifferentiated wrong answers to a separately labeled
confident-wrong diagnostic with its response count and missing-confidence count.
Gap: verify collection on learner surfaces before adding a reader. Benefit:
identify which explanation the learner believes, without changing the mark.
P3/P4. Dependencies: usable collection, settled responses and denominator.
Estimated cost: low to medium, disclosure and sparse-sample copy. Owner:
evidence/selection follow-up after real 19D evidence exists. Smallest check:
synthetic confidence/correctness cells including missing confidence. Falsifier:
collection is too incomplete or the diagnostic never changes a useful next step.

### O8: course search that returns to the learning task

Reuse APP-04 and synthesis 12.1, no new ledger identity needed.
Proposed disposition: Core existing baseline. Delivery: planned, usable entry
point unknown. Timing: current obligation. Evidence: contract, inference.
Job/flow: from manually opening files to finding a term, source passage or own
note, seeing its kind and revision, then returning to the interrupted activity.
Gap: neither a file inventory nor an index proves useful search results.
Benefit: retrieve prior work instead of regenerating it. P5/P1/P2.
Dependencies: approved-root index, note privacy and runtime disclosure filters.
Estimated cost: medium, result quality and stale indexing. Owner: APP/16B
maintenance owner, 19D verification route. Smallest check: same term in source,
private note and unreleased exam key. Only permitted results appear offline.
Falsifier: users cannot find the intended passage or search leaks keyed/private
content. This is verification of a baseline, not approval of a semantic-search
backend.

### O9: offline and restore readiness before leaving

Reuse synthesis 12.1 loss profiles and landscape section 6 readiness manifest.
Proposed disposition: Core for truthful readiness, Backburner only for wider
state-carrying options already left open by 17C. Delivery: partially working.
Timing: current obligation plus future package decisions. Evidence: E9 fact.
Job/flow: from discovering missing media or notes after departure to seeing a
unit's available files and exact package losses before relying on it.
Gap: explicit loss reports now exist, but that does not prove all study material
travels. Benefit: avoid unusable study plans and false restore confidence.
P5/P2. Dependencies: registered objects and current 17C loss report. Estimated
cost: medium, registration and compatibility. Owner: 17C/package owner, 19D
only when its walkthrough exports. Smallest check: package a unit with an
unregistered note, cited media and attempt state, then compare the report with
an offline restore. Falsifier: the preview omits any actual loss. Wider carrying
options return when a real course needs the lost state and rights are settled.

### O10: authoring support that produces a usable learning sequence

Reuse TREAT/CAP/ACTIVITY requirements and the inbox's held readability idea.
Proposed disposition: Core for existing authoring quality, Prototype for any
new readability heuristic. Delivery: partially working, some skills are stubs.
Timing: current obligation plus optional extension. Evidence: installed
`lesson-authoring`, `discovery-and-binding`, and `media-intake` SKILL stubs,
E3/E4 and E6. Job/flow: from choosing a rich block without useful content to a
cited example, learner action, feedback and changed-context application that
can be reviewed as a bounded diff. Gap: renderer capability and treatment
recommendation do not ensure a working authoring playbook.
Benefit: usable activities rather than a larger empty capability catalog.
P6/P3. Dependencies: shipped commands, reviewed source unit, plain-file output.
Estimated cost: medium to high, subject validation and representative access
review. Owner: 19B/19D with 15B and skill owners. Smallest check: author one
math and one CS or history treatment manually through the current contract,
then evaluate what the skill cannot guide. Falsifier: the existing playbook
already produces the sequence reliably. Readability must be judged with dense
subject terminology, not a generic reading-age threshold.

### O11: return briefing that separates changes from due work

New composition candidate, proposed ledger IL-20260906-06. Proposed
disposition: Prototype. Delivery: new candidate over existing primitives.
Timing: optional extension. Evidence: inference from E4/E8, not an absence
claim about all prior plans. Job/flow: after an absence, move from a generic
resume cue to three distinct facts: where reading stopped, which accepted
material changed, and what evidence justifies review. Benefit: orient a returning
learner without making revision look like forgetting or erasing prior work.

Overlap: APP resume, accepted revisions, retention recommendations, source
staleness. Novelty is the combined explanation, not a new change-history store.
Gap: no such combined explanation was established in the sampled surfaces.
P4/P5. Dependencies: accepted revision comparison and saved position.
Estimated cost: medium, unavailable baselines and renamed objectives. Owner:
APP/evidence owners, future prototype after 19D resume evidence. Smallest check:
resume after a lesson revision and after an absence with no revision, then ask
the learner to distinguish the two reasons. Falsifier: separate existing cues
answer the questions equally well or the recap misattributes a change to skill
loss. Preserve as a prototype proposal rather than expanding Reach.

## Broader inventory retained

These are alternatives and already-dispositioned portfolios, not silent cuts.
Each inherits the cited source's durable identity and remains outside the
shortlist until its trigger occurs. No new rejection is proposed.

| ID | Capability and concrete job | Existing route/disposition | Dependency, cost driver and revisit test |
|---|---|---|---|
| B1 | Simulations, visual math and code traces let learners predict, vary a parameter and explain limits | Synthesis 12.3, atlas MF-05/MF-07, Prototype | P1/P3/P6. Validated model and static cases. High estimated interaction/access review cost. Revisit for a named objective unsatisfied by worked examples, falsified if manipulation adds no useful reasoning. |
| B2 | Cornell, concept maps, formula sheets and other note modes expose cues or relations rather than merely shortening a lesson | Synthesis 12.2, Registered after prototype | P2. Trio exists in backend, other modes require distinct validation. Medium estimated authoring cost. Revisit after F3 capture is usable and a learner needs the specific representation. |
| B3 | Reader, guided, worked-reasoning and retrieval-first styles support different tasks over shared content | STRATEGY-01/02, Registered strategies | P1/P3. Eligibility and accommodation precedence. Medium estimated combination-test cost. Verify existing strategy access before adding a new style. Failure is changed meaning or inaccessible fallback. |
| B4 | Paper notes and handwriting recognition recover prior learner work | IL-20260820-01/02, retained registered/enhancement routes | P2/P5/P6. OCR accuracy, source rights, privacy and correction. High estimated review cost. Revisit when a real paper workflow has a reviewed sample, not as live handwriting canvas by default. |
| B5 | Bilingual reading and synchronized audio make the same source usable in another access mode | IL-20260817-02 and synthesis 12.2, future/registered routes | P1. Language/term alignment, rights and stale audio. Medium to high estimated cost. Revisit for a named learner access need with equivalent cited text. |
| B6 | Generator-authored variants and separate teaching/exam pools reduce repetition while retaining exam fidelity | IL-20260905-04 and IL-20260826-10, retained registered routes | P3/P6. Freeze generated items through the existing review/lint process. High estimated answer validation cost. Revisit after pool depletion is measured. Wrong variants falsify readiness. |
| B7 | Local coach packet lets a learner obtain review of a proof, program or explanation | Synthesis 12.2, Prototype | P2/P3/P5. Explicit sharing, pending-review state and named reviewer. Medium estimated review coordination cost. Revisit when pending work has no usable feedback route. |
| B8 | Sync, external formats and cross-app continuity reduce hand-copying between devices or tools | Synthesis 12.5, Backburner | P5. Deterministic conflict/delete model, rights and named consumer. High estimated compatibility cost. Revisit with a concrete device/consumer and a loss-tested round trip. |

These portfolios cover richer possibilities without claiming that optional
formats, social features or expensive modalities must ship now. Phone and
assistive access are quality obligations across the register, not optional
features that can be displaced by this inventory.

## Combined journey and concrete prototype criteria

### P-A: read, get help, write, return

Start with an accepted synthetic lesson and bound source, containing one
ambiguous term and one worked example. Enter from the shelf using visible
controls. Record the actual lesson/source revision and stopping locator.

| Criterion | Passing evidence |
|---|---|
| Discoverability | Learner reaches reading, help and note capture without an agent inventing a URL, invoking Python or editing files to repair the flow. |
| Detour | Keyboard and touch can open a cited definition or prerequisite example, dismiss it, and restore the same passage and focus. Missing help is explicit and does not block reading. |
| Ownership | Save the learner's explanation, including a deliberately wrong claim. It stays private and labeled as learner wording. Saving neither submits an assessment nor creates a key. |
| Durable output | Reopen and edit the note through a visible control, then read the Markdown outside the product with wording, role and source attribution preserved. |
| Recovery | Leave and reopen. The actual position and saved note return. Revise the source externally and verify stale/orphan handling without attaching the note silently to different text. Interrupted save keeps the prior accepted document. |
| Degradation | Accepted text and note remain useful with the model unavailable. Plain-file core meaning is intact. Screen-reader and zoom/reflow legs receive human evidence rather than agent self-certification. |

First use this as a verification tracer over current controls. Prototype only
the failed connection. This prevents F1/F3 from becoming a duplicate note system.

### P-B: transfer that is more than a label

Use one Math 1400 objective and one contrasting synthetic domain, such as code
tracing or historical-source comparison. The author names the learned rule,
changed dimensions, unchanged objective demand and expected reasoning. A
reviewer rejects cosmetic substitutions and unintended prerequisite demand.
Reach the activity from the lesson using visible controls. Structured responses
use the existing scorer. Explanations remain pending until the permitted review
action. Plain-text and accessible alternatives preserve the task. A successful
tracer establishes delivery and alignment, not long-term transfer efficacy.

### P-C: short-session choice and honest stopping

Compare a learner-set item cap with a duration estimate only where supporting
observations exist. Show due work left out, the reason for the queue, and
unknown duration explicitly. Interrupt at a permitted boundary and reopen the
actual session or passage. Exam pause follows runtime policy. Time spent alone
creates neither completion nor mastery. Retain a prototype only if observed
choice and stopping are more useful than the simpler existing queue.

## Ranked next actions

| Rank/ID | Next action and proposed route | Value, dependency and uncertainty |
|---|---|---|
| 1 / A1 | Run P-A as the note-and-return leg of 19D. Route failures to the existing NOTE/APP/source owners before proposing additional controls. | Highest immediate learner value because it preserves work. Needs accepted unit and current doors. Capture integration is the strongest gap found, but live UI remains unobserved. |
| 2 / A2 | Run P-B during 19D representative-unit quality review, using 15B/16A ownership. | Establishes that authored content teaches beyond recall. Depends on accepted source/objectives. Instructional-quality uncertainty is high. |
| 3 / A3 | Verify source lookup/comparison and privacy-safe search in the same unit, routing O6/O8 failures to existing source/APP owners. | Enables reuse and checking claims. Depends on reliable locators and disclosure. Search-entry status is unknown. |
| 4 / A4 | When exporting or studying offline, run O9 against the current loss report and a clean restore. Keep larger package options with the 17C owner. | Prevents lost-work surprises. Known losses give strong evidence, but full preservation is not implemented by naming them. |
| 5 / A5 | After exact resume works, evaluate P-C and O11 together as a future optional prototype. Keep O7 calibration registered until useful confidence data exists. | Improves return and short sessions without changing Reach. Depends on actual position/history data. Benefits and duration estimates remain uncertain. |

No action here silently creates a new phase or grants implementation approval.
19A remains the course-operation workstream, 19B the agent door, 19C the
diagnostic model run, 19D the real learner walkthrough and 19E the generated
tool table. A failed existing obligation is routed as a defect. A genuinely
new interaction remains a proposed prototype until separately planned.

## Validation and handoff

Fresh focused checks are recorded in E10. Full Python
and JavaScript suites, live browser walkthroughs, screen-reader review,
real-course quality review and a fresh package restore were not run in this
planning-only audit. Prior execution records are explicitly distinguished from
new observations.

Manual drift review: the existing inbox supplies the quotation route. Report
interpretations remain labeled. No binding requirement, phase or contract was
changed. F1-F5 reuse their ledger identities, O6-O10 and B1-B8 reuse existing
routes, and O11 receives a new additive candidate entry. No rejection, retired
constraint, new scoring authority or inferred human sign-off was introduced.

Recovery: remove this new report and only the appended audit section from the
ledger to undo this planning pass. Preserve all earlier and concurrent edits.
The ledger append is a dated operation record identifying scope, ownership,
evidence and the proposed disposition changes. There is no commit or push.

Validation run on 2026-09-06:

| Check | Result |
|---|---|
| `python3 scripts/preflight.py --quick` | Exit 0. All invoked gates passed, including skill mirrors, path checks and summary checks. Tests, clean and JS gates were skipped by this mode. The two CI-only steps were not run. |
| `python3 scripts/vision_audit.py` | Exit 0. No missing files, missing dated interpretations, missing planning effects, orphaned entries or undispositioned inbox entries. Ten existing missing-relationship notes remain a reported backlog. |
| `git diff --check` scoped to the report and ledger | Passed for the tracked diff. The report is new and untracked, so its contents were separately inspected for style. |
| Report style search | No em dash or semicolon found. The appended ledger section uses the same prose convention. |

The vision backlog remains owned by the vision-record maintainer. Its next
action is a dedicated relationship review if requested, not an unrelated
rewrite during this audit. The implementation-readiness gate is not applicable
because this report does not authorize an executable plan or freeze a format.
