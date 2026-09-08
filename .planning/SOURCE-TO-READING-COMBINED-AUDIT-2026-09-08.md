# Combined source acquisition and reading audit

Date: 2026-09-08.
Status: synthesis for analysis, not an accepted implementation commitment.

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
