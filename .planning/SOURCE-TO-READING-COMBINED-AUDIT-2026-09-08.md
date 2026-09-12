# Combined source acquisition and reading audit

Date: 2026-09-08.
Status: synthesis for analysis, not an accepted implementation commitment.

Current bounded decision: the 2026-09-09 Link A addendum below owns shared
preparation activities and Resources. It refines the earlier reading proposal.
Its prototype packet supersedes the earlier next-analysis request for this
slice only. Storage and production implementation remain unaccepted.

## Source records

This brief combines the findings without deleting their evidence or silently promoting recommendations. Read the originals for implementation details and verification limits:

- [Source acquisition extension audit](SOURCE-ACQUISITION-EXTENSION-AUDIT-2026-09-08.md).
- [Canvas export milestone proposal](SOURCE-ACQUISITION-MILESTONE-PROPOSAL-2026-09-08.md).
- [Pace-course architecture audit](PACE-COURSE-ARCHITECTURE-AUDIT-2026-09-08.md).

The source documents describe a changing working tree. Their claims require targeted verification before implementation. The pace-course audit inspected code and CLI help but ran no behavioral suites or UI walkthrough.

## Combined answer

The missing product spans two connected boundaries: acquiring authorized source sets and turning deliberately bound source slices into useful learner activities. Existing source adapters, identity, journal, course bindings, assessment runtime and packaging should remain the shared authorities. Neither another downloader alone nor a reading card alone proves the complete learning loop.

| Ref | Shared finding | Status and consequence |
|---|---|---|
| F1 | Local discovery, IDs, fingerprints, rights and source/treatment bindings exist | Implemented primitives. Do not rebuild them or infer write permission from discovery. |
| F2 | Available source objects can be adapted into Markdown plus locators | Implemented. Public web capture is single-page capture, not authenticated course acquisition. Transcript import exists. ASR remains a typed refusal. |
| F3 | Course-set acquisition and incremental reconciliation need a layer above adapters | Proposed. Canvas LTI is outbound delivery, not course intake. |
| F4 | Pace-course reading semantics lack one complete activity contract | Protocol-only as a combined record. Source state, acquisition state, range, time, assistance and completion need deliberate ownership. |
| F5 | Recovery and dependency composition need proof | Generic journal capabilities do not establish exact batch undo or automatic propagation into learner activities. |

## Reconciled qualifications

The acquisition audit recommends Canvas export first. The later milestone proposal qualifies this: learners cannot be assumed to have permission to generate a full `.imscc`. An authorized provided export is a useful deterministic slice, but its accessibility to the actual learner must be checked before making it the main product path. The proposal identifies live student-visible API access as a later possible general path. These external claims are source-dated findings, not freshly verified here.

The reading audit confirms journal undo primitives. The milestone proposal identifies narrower unresolved recovery defects: newly minted files have no before-image, director reversal skips them, and adapter locator sidecars are not journal objects alongside their Markdown. Verify these exact claims before promising job undo. They qualify, rather than contradict, the existence of generic undo.

Remote origin drift does not invalidate an accepted snapshot's citations. New source relevance, course policy and permission changes still need a review path for future activities. Preserve historical reading and attempt records. Do not reset unrelated evidence or silently transfer it to revised objectives.

Source adaptation and AI transformation must remain distinguishable. Rights to access or acquire a resource do not imply permission to summarize it, generate questions from it, upload it or expose keyed assessment content.

## Reconciled reading and activity model

The current personal `pace-course/references/reading-to-itembank.md` is the user-approved semantic input. The three axes refine the earlier reading findings rather than replacing treatment selection, provenance or assessment gates. The [phase addendum](LEARNING-PHASE-AXES-AUDIT-2026-09-08.md) retains the subject edge-case matrix. This section owns their consolidated interpretation and next sequence.

| Earlier finding or apparent conflict | Disposition | Reconciled meaning |
|---|---|---|
| Missing first-class reading record | Remains valid, refined | The proposed owner is an activity occurrence referencing shared content, not a phase field on every source or lesson. |
| Familiarity, summary, teaching and retrieval modes | Remains valid | Treatment describes how learning happens. Ahead/Deepen/Prove describes the job. Ahead may use direct reading without a summary. Prove includes physical or language performance, not just quizzes. |
| `source_state` and new `sequence_evidence` | Refined | When source_state means Published/Bounded/Provisional, map it to the same occurrence-scoped sequence claim. Do not maintain two editable authorities. Preserve source publication facts separately where needed. |
| Published means ready for daily work | Rejected inference | Acquisition, policy, availability and activation remain independent. Published Library stays inactive until its named trigger or learner decision. |
| Shared content versus distinct artifacts | Refined | Reuse content identity and views. Separate activity occurrences and evidence, with new authored artifacts only when content or ownership differs. |
| Skill lacks occurrence/inapplicable wording | Superseded at personal-skill layer | Current skill explicitly addresses both. Itembank schema implementation remains proposed. |
| Revision, rights, acquisition and exact undo gaps | Orthogonal | Phase labels do not solve or replace these operations. Batch acquisition need not precede a local-source reading slice. |
| Administrative and self-paced subjects | Clarified | Use not-applicable axes when the learning job or instructor sequence is absent. Administrative completion never implies demonstrated knowledge. |

### Field and authority mapping

| Concept | Proposed owner or existing authority | Duplication to avoid |
|---|---|---|
| learning_phase, activation, sequence_evidence | Activity occurrence, with not-applicable allowed where appropriate | Do not overload assessment mode, coverage state, content acceptance or availability. |
| Protocol mode | Selected treatment or view, reusing treatment bindings where adequate | Never overwrite session.mode, which controls runtime feedback policy. |
| Source version and locator | Existing source identity, accepted revision and locator authority, referenced by the activity and claim | No free-text version claiming authority over the journal or sidecar. |
| acquisition_status | Acquisition/extraction result for the referenced resource | Published plus inventory_only cannot support a claimed summary. |
| coverage | Existing objective binding coverage plus explicitly scoped extraction/visual coverage when needed | A covered objective does not mean every diagram was inspected or the learner mastered it. |
| assistance and completion | Actual occurrence/attempt evidence through the existing evidence authority | Separate intended unsupported work from observed or declared assistance. No phase-wide checkbox on a shared file. |
| Time, range, targets, class association and recheck | Activity assignment metadata referencing objectives and source locators | Calendar and Day render projections, not competing source or evidence records. |
| Learner capture, notes and performance | Learner-owned artifact or descriptive/pending evidence with modality and reviewer where required | No silent promotion into accepted source, answer key or physical competence. |

These owner assignments are proposed design, not schema additions. Actual assistance belongs to the attempt even when a generated artifact also records how it was authored. Those are distinct provenance questions.

### Retained instructional and policy requirements

Direct source reading is a successful output. A summary never replaces explicitly assigned reading. After a permitted summary, use closed-source teach-back and targeted source return if needed. Ahead does not require generated content. Deepen is optional, and first-seen-in-class work need not manufacture an Ahead stage.

Keep sparse slides incomplete when explanation is absent. Preserve notation, relationships and instructor examples. Label supplementary synthesis, exact page/slide locators, uninspected visuals and extraction gaps. Text extraction alone is not evidence of visual coverage.

Preserve learner-owned captures and course-specific prohibitions. For POL, do not generate or revise captures. Exclude collected homework, lab prompts, assignment code, screenshots, tests and assignment-specific errors under the stated course policies. Routing metadata does not authorize ingestion or generation. Physical-performance gates require the actual modality and an appropriate review path.

Stable objective wording, exact bindings, permitted original practice and independently checked answers/rubrics remain promotion gates. Provisional objectives cannot enter graded or mastery-scored quizzes. The learning phase Prove never overrides that restriction. Reading, recognition, supported work and immediate repetition of a revealed answer do not establish mastery.

Retain small-bank defaults: two or three distinct items per target and usually four to six across a reading block, with changed-context application rather than clones. Numeric ranges are defaults, not quotas. Untimed learning feedback follows a committed response. Later mixed or scored quizzes delay feedback until submission through the runtime's existing disclosure policy. After repair use a fresh transfer item, and retest after a gap. Release still requires policy/source review, answer checking, schema/lint, statistics, objective coverage and one real runtime smoke test.

### Current capability recheck

Rechecked the working tree on 2026-09-08: `schemas/course_graph.schema.json` binding supports source/objective, treatment, locator, coverage and confidence but not the proposed axes. `schemas/session.schema.json:mode` remains feedback policy. `schemas/lesson_run.schema.json` explicitly states that position is presentation state and durable responses belong to the one evidence store. `evidence.lesson_complete_event` remains bank/lesson based. `surfaces/day.py:DAY_LANES` remains a fixed lane list. `surfaces.course_ops._op_staleness` still takes supplied dependent rows. The inspected schemas contain no learning_phase, sequence_evidence or acquisition_status fields. These targeted reads establish schema fit, not complete behavioral coverage.

Reader and lesson views should open the same accepted content. Study may provide supported practice without claiming Prove. Assessment sittings retain runtime mode and disclosure. Day projects eligible Now occurrences and keeps Library accessible to planning. Notes remain learner-owned. Physical-performance evidence is not inferred from study or lesson completion. No new performance-review implementation was verified.

## Consolidated minimum-change sequence

1. Settle the smallest activity-occurrence contract and existing authority references. Record the semantic mapping in its owning contract before format changes. Resolve legacy records explicitly without inventing phase or assistance history.
2. Prove one permitted local-source slice using existing binding and source opening: Ahead/Now, a separately activated second occurrence sharing the content, return navigation and descriptive completion. Prefer this bounded slice before requiring a downloader. Coordinate with the active UI owner.
3. Add the smallest occurrence evidence and eligibility composition. Reuse runtime events and disclosure for assessment. Support skip paths, not-applicable axes, policy refusals and physical-mode distinctions without adding another scorer or evidence store.
4. Prove source rescoping and recovery for that slice. Retain, revise, replace or retire affected future work, quarantine affected items with a reason and replacement trigger, preserve accepted snapshot citations and historical attempts, and leave unrelated evidence untouched.
5. Revisit acquisition and external calendar integration separately when the local slice and actual access evidence justify them. Verify mint undo and sidecar recovery before batch import. Keep API, Drive, ASR and broader providers optional with named dependencies rather than prerequisites for reading.

This is one consolidated proposed order, not authorization to implement. The next executable packet should cover only step 1 and the smallest reviewable prototype needed to settle it. Do not create every later plan now.

## Consolidated acceptance gate

| Gate | Observable result |
|---|---|
| G1: meaning and reuse | One source supports separate occurrences without duplicate content. Ahead may be direct reading. Prove may be non-quiz performance. Optional phases and not-applicable axes work. Completing one occurrence grants no stronger phase or mastery. |
| G2: eligibility and source fidelity | Published Library stays out of Day until explicit activation. Provisional preview remains labeled and ungraded. Inventory-only, sparse-slide and uninspected-visual states cannot claim a complete summary. Exact revision/locator opens or reports a precise unavailable state. |
| G3: policy and evidence | Prohibited input/generation remains blocked. Learner captures retain ownership. Assistance and modality remain explicit. Hints cannot become unsupported evidence. Physical gates reject note/card substitutes. Feedback timing remains runtime-controlled. |
| G4: change and recovery | Narrow/reorder/contradict/retire affects only linked future work and items. Quarantine records its reason. Historical completion and snapshot citations survive. Retries are idempotent, mutations recoverable, and offline restore reports losses. |
| G5: release evidence | Run the slice's targeted checks and required preflight after implementation. Any released practice also passes source/answer review, lint/schema, statistics/coverage and a real runtime smoke test. Record human accessibility checks as performed, skipped or owed, never presumed passed. |

These are proposed acceptance cases. This reconciliation performed file reads and document edits, not implementation tests. Original audits retain their narrower verification limits.

## Decisions for the next analysis

| Ref | Decision | Evidence needed |
|---|---|---|
| D1 | First user-visible slice: existing local source to reading, or export to Sources | Current user access, dependencies and active Phase 20 ownership. Avoid assuming the longer pipeline must come first. |
| D2 | Reading activity ownership and evidence semantics | Existing schemas and runtime event contracts, plus a small learner flow. |
| D3 | Recovery prerequisites | Verify mint reversal, sidecar pairing and exact pre-job restoration against current code and tests. |
| D4 | Dependency and calendar ownership | Separate snapshot validity, current relevance, deadlines, learner plans and historical completion. |
| D5 | Minimal sequence and deferred breadth | Identify only the next ready packet. Preserve Canvas API, Drive, ASR and other viable capabilities with dependencies and revisit triggers. |

## Requested next task

Reconciliation status, 2026-09-08: the personal pace-course skill now explicitly scopes axes to activity occurrences, permits not-applicable learning/sequence axes, and forbids publication, generation or existence from automatically activating Library. Verified by reading the installed skill. The originating task reports planning-owner commit `aede2da0`, which was not independently inspected here. Do not reopen these as unresolved personal-skill wording changes. Itembank representation and implementation remain separate proposed work.

Read the subsequent [learning-phase axes addendum](LEARNING-PHASE-AXES-AUDIT-2026-09-08.md). It verifies the updated personal skill's Ahead/Deepen/Prove, Now/Next/Library and Published/Bounded/Provisional model, proposes activity-scoped ownership, and records schema fit, edge cases and acceptance tests. Reconcile its two important qualifications: shared artifacts need separate activity completion, and administrative/self-paced work must not be forced into an inapplicable phase or instructor-sequence label.

### Additional user-requested workflow improvement

User statement, 2026-09-08:

> also for daisy chain chat, for stuff that leaves audits only, oncisder making stuff be written down and then recnociled in the end like what we had to do as well as an possbile improvement

Interpretation: evaluate an improvement to `daisy-chain-work` for audit-only and mixed audit/implementation chains. This session required an explicit reminder to save the audit, followed by a separate consolidation request. That is evidence from this session, not proof of a recurring failure.

The current skill already requires durable project state and evidence in each handoff. Its gap is an explicit audit-output and final-reconciliation gate. Consider this bounded addition:

1. Every audit-producing task saves findings, source paths or revisions, verification limits and open questions before handoff. Link the existing owner document when sufficient rather than creating duplicate reports.
2. The handoff names each saved audit and whether it is awaiting reconciliation. Keep a compact index in the current state owner when several outputs accumulate.
3. Before closing the requested chain, one reconciliation pass checks overlapping findings, contradictions, stale assumptions, completed fixes and remaining decisions against the current state. Preserve the original evidence and distinguish proposals from accepted decisions.
4. Record each remaining finding's disposition, owner and next action or revisit trigger. A saved audit alone does not satisfy an implementation goal. An audit-only goal may finish with reconciled findings and explicit unresolved decisions.
5. Scale the gate to the task. Reuse an existing summary for one small audit. Do not create a new task or a broad plan solely to satisfy paperwork, and never expand mutation or commit authority through the handoff.

The next analysis should evaluate and save a concrete proposed skill diff or wording, alongside its rationale and acceptance examples. Do not silently modify the installed skill as part of the product audit. Carry this recommendation into the final reconciled next-steps report.

Reconciliation update, 2026-09-08: this skill recommendation is now implemented in both the personal installed skill and its maintained source. `daisy-chain-work` saves audit outputs before handoff, carries their reconciliation status in the handoff packet, and requires a proportional final reconciliation that records disposition, owner, next action or revisit trigger without expanding authority. The remaining findings below concern Itembank product contracts, schemas and behavior rather than skill wording.

Use one GPT-6 Astra agent at low reasoning, with no delegation, to analyze the combined evidence and recommend what to do next. Recheck disputed or consequential claims symbol-first. Read current project authority and active phase ownership. Save the analysis in the task workspace and give its exact path.

Deliver a prioritized current-state map, reconciled contradictions, a smallest coherent learner slice, dependency order, important missing questions and one bounded follow-up packet. Separate implemented, specified, recommended and unverified claims. Do not implement code, commit, acquire private material, modify external services or automatically accept a new contract. Only create a durable implementation plan if a named uncertainty or handoff requirement justifies one. Preserve the original audit records.

## Link A decision: shared preparation activities and Resources

Date: 2026-09-09. Owner and product reviewer: Weibao.
Status: implementation-ready prototype specification, not schema acceptance.
Input: `COURSE-POPULATION-HANDOFF-2026-09-09.md`, Link A and Settled direction,
in the user-named planning vault. This is an interpretation of that packet.
The settled input makes preread and prelearn occurrence modes and resources
role-labeled sources. The representation below is proposed engineering work.

### Operation and evidence boundary

One agent owns this document. Read scope was the supplied handoff, named skills,
repository planning contracts, and relevant code and schemas. Write scope is
this existing semantic owner only. No course contents, vault files, schemas,
UI, scores, evidence, source bytes, skills, or remote services are changed.
No acquisition or source-text upload was performed. The checkout was clean at
inspection, at `5f3aaf33b1896657f5a52bd6136a5ac1fbb616fa`.
Review the document diff before accepting a durable contract. Undo is removal
of this addendum and its top pointer, preserving any later concurrent edits.

| Ref | Verified current evidence | Implication |
|---|---|---|
| LA-F1 | `graph.py:TREATMENT_KINDS`, `TREATMENT_RIGHTS`, `SECTION_COLUMNS`, `add_binding`, and `schemas/course_graph.schema.json` binding definition | Eleven treatments exist. Bindings carry objective, source, locator, coverage, confidence and rights snapshot. No occurrence ID, preparation mode or resource-role field is defined. Unknown columns are preserved, which does not give them runtime semantics. |
| LA-F2 | `course.py:read_course`, `write_course`, `bind_source`, `bind_treatment`, `rights_for_binding`, and `surfaces/course_ops.py:_op_treatments`, `_op_bindings` | Course graph and source operations are shipped. Skill claims that these remain wholly pending are stale. Use live APIs without modifying the skills in this task. |
| LA-F3 | `surfaces/daemon.py:_course_area_rows` | Learn currently lists bank-backed lessons. Sources lists source references, notes and current read rights with empty links. It does not implement exact-range source opening or the proposed Resources interaction. |
| LA-F4 | `evidence.py:lesson_complete_event` | Completion names a bank and lesson slug. Its dedupe hash omits occurrence identity. Reusing it unchanged would conflate repeated preparation over shared content and could enroll a lesson in retention review. |
| LA-F5 | `surfaces/ia.py:COURSE_AREAS`, `ACTIVITY_JOB_STATES`, `source_adapters.py:RECHECK_STATES`, and `surfaces/course_ops.py:_op_staleness` | Sources already has a route. Activity job states describe operations, not learning. Origin recheck and supplied dependency rows do not provide an automatic occurrence migration engine. |

Contract basis: `SOURCE-TO-COURSE.md` sections Course-building loop and Learner
experience, `AGENT-WORKFLOW.md` sections 5 through 8, and `REQUIREMENTS.md`
TREAT-01 and GRAPH-03. Sampled vision entries are the 2026-08-26 correction
withdrawing duplicate treatments/progress and the 2026-09-08 adopted learner
interface and selective generation entries. This was not a whole-vision audit.
Large code modules were sampled at the named symbols, not read in full.

### LA-D1: one occurrence, existing treatments, separate preparation mode

Disposition: prototype. An occurrence is an assigned or deliberately selected
unit of work with its own identity and revision. It references course and
objective IDs, accepted content and treatment bindings. It does not own source
bytes, treatment definitions, assessment state or progress counters.

| Proposed field group | Exact meaning and owner |
|---|---|
| Identity | `occurrence_id`, `occurrence_revision`, `course_object_id`, `objective_ids`. Course assignment authority owns these. Prototype IDs exist only in synthetic fixture data. |
| Content references | Ordered references to existing treatment bindings and accepted source/artifact identity, fingerprint and locator. For the prototype, identify a binding by course graph fingerprint plus row position and full row comparison. This is a revision-scoped reference, not a newly invented permanent binding ID. A mismatch refuses resolution. |
| Preparation | `preparation_mode`: `none`, `preread`, `prelearn`. `preread` requires a bounded source selection and reading purpose. `prelearn` requires a stated preparation goal and an ordered teaching path using existing treatments. Neither value changes assessment `session.mode`. |
| Assignment context | Purpose, assigned versus learner-selected range, selecting actor, source locator supporting an instructor assignment, optional class association, deadline with timezone and provenance, optional duration estimate. Unknown dates remain unknown. |
| Path role | `required-instructor-work`, `recommended-preparation`, `remediation`, `retention-review`, `optional-enrichment`. One primary role per occurrence. This is why it is offered, not its treatment, evidence or permission. Conflicting instructor claims require review. |
| Existing proposed axes | Retain `learning_phase` Ahead/Deepen/Prove/not-applicable, `activation` Now/Next/Library, and `sequence_evidence` Published/Bounded/Provisional/not-applicable from this owner. Preparation modes do not replace these axes. Preread/prelearn normally serve Ahead, but never infer missing legacy phases. |
| Policy and assistance | Reference current course policy and intended assistance limits. Actual assistance belongs to occurrence/attempt evidence. A preparation label grants no AI use. Administrative work may use not-applicable axes and no preparation mode. |

Treatment mapping is exact: direct source reading maps to `direct-reading`,
selected reproduced passage to `excerpt`, guided teaching to `guided-lesson`,
terms or notes to `notes-or-terms`, example to `worked-example`, visual or
demonstration to `visual-or-demonstration`, and practice to `practice`.
`formal-test`, `assessment-first-diagnostic`, `learner-artifact`, and
`human-review` retain their existing meanings. A preread may include optional
supporting terms, but a summary cannot replace its assigned source selection.
A prelearn can sequence reading, example and practice without adding a new
treatment enum or manufacturing a lesson when existing content suffices.

`graph.TREATMENT_RIGHTS` stays authoritative: direct-reading, learner-artifact
and human-review consume read, excerpt consumes quote, and the other seven
treatments consume transform for binding. Opening an existing demonstration
as a source is direct-reading access. Authoring a derived demonstration still
uses visual-or-demonstration and its transform requirement. A resource role
never alters this mapping.

### LA-D2: preparation status is a projection, never a second progress store

Disposition: prototype. Show preparation mode, assignment role and availability
separately. Do not introduce a single readiness percentage or a boolean `ready`.

| Learner-visible state | Derivation and next action |
|---|---|
| No preparation record | No occurrence evidence exists, or legacy history cannot be mapped. Offer the bounded activity when eligible. Do not infer failure or mastery. |
| In progress | A known occurrence resume position exists. Resume is presentation state only. Scrolling, opening, time and generated content cannot mark completion. |
| Marked read / Preparation self-reported | Learner explicitly declares the occurrence done. Future durable support must use the one evidence writer with occurrence revision, actor, timestamp and dedupe identity. The prototype displays simulated state only. |
| Review pending | A submitted artifact requires review under its existing treatment contract. No settled correctness or physical competency follows from submission. |
| Skipped / Deferred | Explicit learner disposition with provenance, separate from completion. It does not waive instructor requirements or silently activate another activity. |
| Unknown / Unavailable / Needs review | Missing evidence, unavailable content, or changed assignment respectively. Preserve any historical self-report beside the current availability or revision warning. |

Now is necessary but insufficient for a daily offer. Resolve policy, accepted
references, rights, source availability and sequence constraints before offering
an action. Published Library remains outside the daily path until explicit
activation. Next does not silently become Now because a file was generated.
Required work remains visible with its blocking reason even when it cannot open.
Retention-review timing stays with the existing retention authority. This model
does not calculate another interval or create a review because something was read.

Future completion events must distinguish two occurrences sharing the same
source and repeated requests for the same occurrence revision. Retraction must
use existing evidence recovery conventions. A prelearn containing practice
links to runtime results without recomputing correctness. Its self-report is
not a course completion award, grade, mastery claim or proof of independence.

### LA-D3: Resources is the learner view of Sources

Disposition: prototype. Reuse the existing `sources` course area and source
operations. Present its learner-facing title as Resources in the prototype,
with source details and management available in the same area. Do not add a
seventh parallel catalogue, a second URL registry, or another content store.
Production title adoption is LA-Q1 below.

Resource roles describe the course's use of a source, so the proposed owner is
the existing course-to-source reference, optionally narrowed by an objective
binding. It is not a global role on the source object. The same source can be
primary authority in one course and enrichment in another. Proposed role values
are `primary-authority`, `instructor-material`, `alternative-explanation`,
`demonstration`, `practice`, `reference`, and `enrichment`. These describe fit,
not treatment kinds or coverage judgments. Multiple roles may apply.

Each resource row projects its source ID, canonical origin and accepted
revision, title and publisher/author when known, role, objective fit and
supporting locator, reviewer and review date, rights, acquisition/availability,
and stale/conflict state. Do not copy authoritative rights into editable cards.
Unbound candidates remain clearly unreviewed and cannot imply objective coverage.
Free-text source `note` remains prose, never a hidden JSON field or role parser.

For a video, bind a specific item and relevant time range. For a playlist,
review and reference a fixed item selection and its captured revision, not its
future live membership. A channel can remain a discovery lead but never grants
blanket acceptance. No real resource recommendation or external retrieval was
performed by Link A. Existing source identity and locator machinery must prove
these representations before durable adoption.

Opening an external origin is a deliberate network action with visible
destination. Do not autoplay, embed third-party trackers, fetch thumbnails,
download, transcribe or send content to a model merely to show a resource row.
Read, quote, transform, remote-process, package, export and share remain separate
grants under current rights and course policy. Unknown stays restrictive.
POL remains administrative structure and source locators only under the input
packet. These fields do not authorize POL analysis or preparation generation.

### LA-D4: revision, offline, accessibility and migration contract

Disposition: prototype now, durable migration deferred until reviewed.
An authorized local accepted revision opens offline at its exact locator.
Remote-only content says Requires internet and retains title, role, fit and
return navigation. Missing local bytes offers relink/reconcile, missing range
offers range review, denied rights offers rights review, and corrupt or future
schema data offers the last valid view when available. Unsupported media names
the limitation and offers an authorized original or static alternative.
None of these failures becomes an empty course or a completion state.

Origin drift preserves the accepted snapshot and historical citations. A new
accepted source or assignment revision marks linked future occurrences for
review. Do not transfer old completion to the revised occurrence or reset
unrelated evidence. Current denied rights block opening even if a historical
snapshot once allowed it. Divergent bytes refuse resolution instead of silently
opening newer text. Dependencies must be explicit, since `_op_staleness` does
not discover them automatically.

The prototype must show the whole path at desktop and phone widths: course,
bounded preparation, exact source range, return to the same occurrence, and
Resources details. Use labeled links and buttons, visible focus, logical
heading order, keyboard return context, text status announcements, sufficient
contrast, zoom/reflow, touch targets and reduced motion. Keep purpose, range,
source and any teaching meaning readable in plain Markdown. Video needs a
usable caption/transcript or equivalent source when permitted, with absence
reported honestly. Human touch, screen-reader and aesthetic acceptance remains
owed until performed by a person.

No migration occurs in Link A or its prototype. Do not store proposal fields
in graph `extra` and call them supported. The eventual proposed owner is an
additive occurrence section in the existing course graph, parsed by `graph.py`,
with role/fit metadata extending the existing Sources/binding relationship.
This storage choice and stable binding references need LA-Q2 before adoption.
Evidence would extend the canonical event schema and writer, never a course
JSON progress file or localStorage store. Legacy graphs remain valid and gain
no inferred roles, modes, deadlines, activation, assistance or completion.
Future acceptance requires expected-fingerprint writes, validated atomic journal
operations, conflict/retry tests and offline export/restore with explicit losses.
Earlier R1 through R3 remain recorded recovery debt from the prior probe, not
freshly verified failures here. Exact import undo stays outside this slice.

### Alternatives and unresolved choices

These dated dispositions preserve the alternatives. Owner is Weibao for product
acceptance and the implementation owner for the named proof.

| Ref | Alternative and disposition | Evidence, reason and retained route | Revisit condition |
|---|---|---|---|
| LA-R1 | Add preread/prelearn treatments: rejected for this design | LA-F1 and TREAT-01 already own the vocabulary. TREAT-01 says "Durable object: treatment binding. Authority: reviewer acceptance." The input packet explicitly places these modes on occurrences rather than adding treatments. Retain occurrence metadata over existing treatments. | An accepted treatment contract identifies a teaching behavior that composition cannot express. |
| LA-R2 | Global read checkbox or browser progress: rejected | LA-F4 cannot distinguish occurrences. Binding rule: "Do not compress them into one progress or mastery score." Retain occurrence-scoped descriptive events through the evidence writer. | Never as parallel authority. Reconsider event shape only through the canonical evidence contract. |
| LA-R3 | Independent Resources store or blanket channel acceptance: rejected | LA-F3 already projects source records. Binding rule: "Accepted files (courses, lessons, banks, notes, evidence) are canonical." Input packet explicitly refuses wholesale channel acceptance. Retain role-labeled source references and specific reviewed selections. | A source capability need is proven and accepted through the existing source contract. |
| LA-R4 | Embed, download, ASR and automatic activation: backburner | Adds acquisition, egress and recovery costs unrelated to proving preparation semantics. Retain deliberate external opening and offline references. | Verified local flow, explicit access and rights, and paired recovery gates justify one acquisition slice. |
| LA-Q1 | Production label Sources versus Resources | Recommend Resources as learner label while preserving the `sources` route and management identity. Prototype both navigation and details under that choice. | Weibao reviews the prototype before a production label change. |
| LA-Q2 | Durable occurrence and resource metadata representation | Recommend the additive existing-graph representation above. Binding rows lack stable IDs, so permanent reference strategy needs parser, revision and package proof. | Prototype passes and Weibao accepts the bounded schema and event delta. |

### Exact next slice and gate

GOAL: demonstrate one synthetic preread and one prelearn sharing a local source,
with independent simulated status and a Resources view of that source.
OWNER: Weibao reviews product choices. One builder owns the prototype.
SCOPE: one new `prototypes/course-preparation/` fixture and presentation harness,
plus evidence appended to this owner. Read current `course` and `graph` APIs and
the source/learner seams named in LA-F1 through LA-F5. Use synthetic local content
and real course/source/binding reads in a disposable root. Prototype-only
metadata must be explicitly labeled and kept outside accepted graph records.
DO NOT TOUCH: production UI/routes, schemas, runtime, evidence, real courses,
vault files, import recovery, commits, pushes or external services.
NEXT ACTION: create the synthetic course/source/treatment fixture using existing
operations, then add an in-memory occurrence projection and source detail view.
Do not wire Mark read to `/api/lesson-complete`. Simulated status resets when
the harness restarts and is visibly labeled as such.

| Gate | Required observable evidence |
|---|---|
| LA-G1 | Same source ID and bytes back two occurrence IDs. Preread opens an exact bounded range with purpose. Prelearn presents ordered existing treatment references. Marking one simulated occurrence leaves the other unchanged. |
| LA-G2 | Published Library stays off the Now view. Role, preparation mode, self-report and availability remain separate. A prohibited-generation case offers no generated activity. |
| LA-G3 | Resources and preparation resolve the same source identity. Unknown/denied rights, missing locator, divergent revision and offline remote-only cases show distinct recovery actions. No fetch occurs during listing. |
| LA-G4 | Back returns to the originating occurrence. Capture desktop and phone separately, exercise keyboard and plain-file fallback, and report human touch/screen-reader/zoom/aesthetic review as performed or owed. |
| LA-G5 | Before/after accepted source and graph fingerprints and evidence-log inventory prove zero runtime mutation during interactions. No scoring, persistence, import, schema or production route changes appear in the diff. Run the targeted harness checks and required quick preflight. |

RETURN: prototype paths, captures, checks and failures, zero-mutation evidence,
unresolved LA-Q1/LA-Q2, and the smallest proposed durable delta for review.
Stop if the harness requires a second content parser, accepted-field writes or
scoring simulation. This packet specifies a follow-up but does not authorize
production implementation. Link A ends with this decision and returns to the
originating coordinator rather than creating a duplicate task for Link B or C.

### Link A verification and reconciliation

The saved proposal covers ownership, exact vocabulary mapping, separate learner
states, rights and policy, offline and stale behavior, accessibility, migration,
rejected alternatives and a bounded prototype. Earlier phase axes are retained.
Sources and Resources are reconciled as one area. Skill pending-command claims
are qualified by current code without rewriting unrelated instructions.
No new schema, UI implementation, accepted product contract or completion
authority is claimed.

Checks run on 2026-09-09: `python3 tests/source_binding_surface_roundtrip.py`
passed its real synthetic coverage/treatment binding and denied-right refusal
checks. `python3 scripts/preflight.py --quick` passed all ten executed gates,
including guard, schema, path and skill-mirror checks. Full Python and JavaScript
suites and the clean-tree gate were skipped by quick mode. `git diff --check`
passed. The diff contains this one planning file only. No prototype was built,
so LA-G1 through LA-G5 remain future checks rather than claimed passes.
