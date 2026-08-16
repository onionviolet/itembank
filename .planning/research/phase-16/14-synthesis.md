# Phase 16 synthesis: one source-to-course product model

**Status:** proposed synthesis for contract reconciliation

**Scope:** research and product definition only

**Evidence base:** `USER-VISION.md`, `USER-VISION-INBOX.md`, the binding planning
contracts, `00-coverage-audit.md`, and completed Phase 16 reports 01 through 13

**Change boundary:** this document proposes changes but applies none of them

## 1. Synthesis verdict

itembank should be a local, file-centered course workspace whose normal entry is
a resumable course, not a bank, generated-artifact gallery, universal dashboard,
or chat. A course connects approved sources, a versioned objective graph,
reviewed treatment decisions, accepted learning artifacts, runtime-governed
activities, learner-owned notes, evidence, and the next justified action.

The thirteen reports agree more strongly on semantics than on features. This
does not narrow the viable idea set. Coalescing means giving broad capabilities
one coherent architecture, shared primitives, and durable dispositions. It
separates architecture breadth from simultaneous execution scope. A capability
is not removed merely because it is optional, expensive, specialized, or not in
the next implementation wave:

1. Durable meaning belongs in inspectable files and stable relations. Rich UI,
   indexes, search rankings, progress views, media derivatives, and agent jobs
   are projections or derived state.
2. Objectives are the instructional spine. A typed graph is the durable model;
   an authored outline is the default human projection.
3. Direct reading is a complete treatment. Generation fills a demonstrated gap,
   not a gallery.
4. Semantic teaching roles compose many visible features. A definition may
   appear inline, on focus, in a glossary, in search, or in notes without becoming
   five content types.
5. Learner activity purpose precedes response widget. Prediction, retrieval,
   explanation, diagnosis, transfer, and formal assessment can reuse response
   forms while retaining different feedback and evidence policies.
6. Reader and guided modes project one parsed lesson. Notes and learner state
   remain separate records. Formal assessment remains under runtime authority.
7. Every mutation is explicit, reviewable, conflict-aware, atomic, and
   recoverable. Discovery is read-only. Link, bind, import, copy, move, derive,
   supersede, migrate, and synchronize are not synonyms.
8. Accessibility, rights, privacy, localization, offline behavior, and recovery
   are acceptance properties of content and flows, not final visual polish.

Viable proposals therefore land in one of four durable destinations: core now,
a configurable mode or registered strategy, a reversible prototype or
experiment, or a backburner entry with dependencies, cost, and a revisit trigger.
Rejection is reserved for conflict with assessment authority, accessibility,
rights or licensing, safety, truthful evidence, portability, or the coherent
product model, including a genuinely mutually exclusive design that cannot share
an interface. Supersession means the user value remains but a better mechanism
implements it. No proposal disappears from the ledger.

These conclusions reconcile the source-workspace findings in
`01-source-grounded-products.md` sections 3.3, 3.4, and 6; the pedagogical model
in `02-lesson-flow-capabilities.md` sections 4 through 8; the purpose-first
activity model in `03-question-activity-matrix.md` sections 4 through 9; and the
portable contract in `04-portable-contract-agents.md` sections 7 through 9.
They are independently reinforced by `13-expected-capabilities-omissions.md`
sections 10 through 16.

### 1.1 Evidence quality

| Evidence class | Strength | Proper use |
|---|---|---|
| Binding repository contracts and shipped behavior | High for current boundaries, not proof of learning effectiveness | Preserve one parser, scorer, evidence authority, local evidence, and additive compatibility |
| Standards and official product documentation | High for documented behavior and interoperability constraints | Establish what a format or product supports, never that its pattern improves learning |
| Learning research reviewed in reports | Moderate to high where systematic or controlled, but population and task dependent | Justify retrieval, generation, feedback, worked examples, and active construction with stated limits |
| Comparative product analysis | Moderate for workflow and usability hypotheses | Generate patterns and prototype questions, not commitments |
| Report inference | Explicitly provisional | Convert to a recommendation only with a gate, owner, and failure condition |
| User vision | Authoritative for desired outcome and values | Determine product direction, not settle technical feasibility or efficacy |

External claims remain supported through each report's source list. This
synthesis does not add external factual claims. Examples from commercial tools
are patterns, not endorsements or evidence of educational efficacy.

The evidence handoff from every completed report is explicit:

| Report | Sections used for product definition |
|---|---|
| `01-source-grounded-products.md` | 3.3 to 3.4 for inference/recommendations, 4 for patterns, 5 to 7 for cross-cutting effects and disposition |
| `02-lesson-flow-capabilities.md` | 3 for facts/inference, 4 to 6 for flow and semantic capabilities, 7 to 9 for dispositions and Phase 16 implications |
| `03-question-activity-matrix.md` | 3 to 5 for purpose and response forms, 6 for authority/evidence, 7 to 11 for fidelity, quality, and disposition |
| `04-portable-contract-agents.md` | 4 to 6 for evidence/effects, 7 for contract/skills/files/upgrades, 8 to 9 for decisions and gates |
| `05-learning-program-landscape.md` | 7 for cross-cutting findings, 8 for contract implications, 9 to 10 for dispositions and risks |
| `06-feature-style-atlas.md` | 4 for semantic roles, note outputs, and learning sequences; 9 for MF-01 to MF-18; 10 to 12 for implications, dispositions, and gates |
| `07-file-lifecycle-edge-cases.md` | 4 to 8 for operations, identity, discovery, and conflicts; 11 to 15 for executable files, adapters, migrations, and recovery; 18 to 20 for dispositions and readiness |
| `08-curriculum-hierarchy-progress.md` | 4 to 6 for graph/progress, 7 for fixtures, 9 to 13 for prototypes, failure modes, and decisions |
| `09-app-flow-information-architecture.md` | Flow and screen inventories; 10 for durable jobs/recovery, 11 to 16 for patterns, dispositions, and verification scenarios |
| `10-visual-experience-system.md` | 4 to 7 for facts, alternatives, and recommended system; 8 to 12 for cross-surface rules, gates, and disposition |
| `11-cross-cutting-risks-validation.md` | 3 to 6 for constraints and ownership, 7 to 10 for adversarial evaluation, decisions, and release matrices |
| `12-active-annotation-notes.md` | 4 to 10 for note purpose, authority, and strategy; 11 to 15 for quality gates, prototypes, and dispositions |
| `13-expected-capabilities-omissions.md` | 8 to 10 for baseline, duplicates, and assumptions; 11 to 16 for contracts, adversarial tests, readiness, and dispositions |

### 1.2 Contradictions resolved

| Tension | Resolution | Basis |
|---|---|---|
| "Build both" versus finite maintainable strategies | Register both only when they share parser, scorer, evidence, object, permission, and accessibility contracts. Otherwise choose or prototype. | `PLANNING-DIRECTIVES.md` section 3; `11-cross-cutting-risks-validation.md` sections 3.2 and 6.5 |
| Flexible hierarchy versus a usable course outline | Store a constrained typed graph; present a simple authored outline by default. | `08-curriculum-hierarchy-progress.md` sections 4 and 13 |
| Markdown portability versus rich executable learning | Keep complete Markdown meaning plus validated data declarations that invoke trusted renderer components. Never accept authored scripts as lesson authority. | `04-portable-contract-agents.md` sections 7.2 and 8; `07-file-lifecycle-edge-cases.md` sections 11.2 to 11.4 and 18 |
| Edit in place versus immutable accepted revisions | Edit owned files in place through compare-and-swap and atomic writes; acceptance records a revision and fingerprint. External changes create stale or conflict state, never silent overwrite. | `07-file-lifecycle-edge-cases.md` sections 4, 7, 8, and 15; `13-expected-capabilities-omissions.md` sections 10 and 12 |
| Configurable learning styles versus objective constraints | Learners choose among allowed strategies. Authors declare supported strategies. Objectives and accommodations constrain eligibility. Runtime policy fixes assessment behavior. | `12-active-annotation-notes.md` sections 8 and 10; `03-question-activity-matrix.md` section 6 |
| Notes as learning material versus notes as unreliable authority | Notes may ground reflection, retrieval proposals, and draft questions, but cannot become accepted teaching or scoring truth without source-backed review. | `12-active-annotation-notes.md` sections 7 through 10 |
| Visual ambition versus accessibility and calm hierarchy | Adopt Structured Studio as the default direction, with Quiet Workbench density and Guided Canvas only for bounded guided moments. Fixed hierarchy, focus, contrast, and equivalence rules override theme. | `10-visual-experience-system.md` sections 6, 7, and 11 |
| Local-first preference versus hosted agents | Core reading, scoring, evidence, and recovery work locally. Optional approved operations may use hosted or local agents with identical contracts and visible egress. | `PLANNING-DIRECTIVES.md` sections 1 and 4a; `11-cross-cutting-risks-validation.md` sections 5.2 and 5.3 |

Unsupported assumptions are not used as design premises: more interaction is
not automatically better; a fully automatic build is not presumed desirable;
plain Markdown sufficiency must be stress-tested; notes are not assumed correct;
local-first does not imply zero egress; a standards label does not prove a
faithful round trip; and configurability does not erase pedagogy or maintenance
cost. See `13-expected-capabilities-omissions.md` section 10, "Assumptions with
insufficient evidence."

### 1.3 Claim and decision labels

- **Fact:** a binding repository rule, verified shipped behavior, documented
  external behavior, or research result reported with its limitations. Facts in
  this synthesis point to the originating report and section.
- **Inference:** a product implication drawn from facts. It is not represented
  as vendor intent or settled learning science.
- **Recommendation:** the architecture or workflow judged best by reconciliation.
- **Proposed decision:** a recommendation ready to enter a binding contract only
  after the applicable prototype or direct-user gate.
- **Open question:** unresolved and routed in sections 12.6 and 17.

Sections 2 through 11 are recommendations unless they restate a named binding
boundary. Sections 12 and 15 give proposed decisions and dispositions. Section
17 contains open questions. No prototype-gated recommendation is a current
implementation fact.

## 2. Product model

### 2.1 Actors

| Actor | Authority and responsibility |
|---|---|
| Learner | Owns goals, paths within allowed constraints, private notes, scratch work, strategy preferences, evidence export, deletion, and recommendation overrides |
| Course builder | Defines course scope, treatments, paths, artifacts, and completion policy within source and rights constraints |
| Reviewer | Accepts or rejects instructional and assessment revisions at the configured consequence level |
| Source owner or authority | Supplies rights, edition, scope, and authoritative source claims; a local reader is not necessarily the rights owner |
| Instructor or assigning authority | Optionally defines a closed program, required path, accommodations, deadlines, and completion predicate without owning runtime correctness |
| Hosted or local agent client | Discovers, aligns, proposes, drafts, validates, and explains within an operation manifest; never owns accepted truth or assessment authority |
| Deterministic runtime | Sole authority for assessment session state, keyed disclosure, scoring, attempt evidence, selection policy where configured, and pending prose state |
| Filesystem and external editor | Independent mutation environment whose current bytes, permissions, and conflicts must be respected |

### 2.2 Durable objects and relations

| Object | Minimum contract | Source of truth |
|---|---|---|
| Course | Stable ID, target, learner context, approved roots, graph version, treatments, policies, accepted bindings, evidence location | Human-readable course artifact |
| Scope or framework version | Authority, version, source locator, included nodes, local overlay, migration relation | Versioned course records |
| Concept | Stable identity and labels; may be cross-listed | Course graph |
| Objective | Stable ID, demand, authority, scope, evidence rule, prerequisite relations | Course graph |
| Source | Stable ID, path or URI, version/fingerprint, rights state, language, ownership, availability | Source registry or compact course record |
| Source binding | Objective or claim, source ID, locator/selectors, role, confidence, review state | Course/artifact relation |
| Artifact | Stable ID, kind, objectives, status, revision, fingerprint, provenance, language, dependencies | The linked or owned file plus metadata |
| Lesson | Portable authored artifact containing complete explanatory meaning and semantic teaching roles | Markdown parsed once into canonical document model |
| Bank and assessment form | Existing validated bank plus blueprint and frozen form/session references | Existing parser and runtime contracts |
| Activity | Purpose, objective, prompt or stimulus relation, response schema, feedback policy, evidence policy, fallback | Semantic lesson record or assessment artifact |
| Learner note | Learner-owned text or structure, anchor, objective, provenance, privacy, strategy, revision | Separate note file or learner record |
| Learner artifact | Proof, program, diagram, explanation, project, or observation with rubric and pending/review state | Linked learner-owned file and evidence relation |
| Evidence event | Immutable observation, activity/version context, authority, result or pending status, timestamp | Existing append-only evidence store |
| Strategy | Registered sequence and learner actions with eligibility, skip/resume, accommodations, and evidence rules | Versioned strategy registry |
| Agent operation | Intent, actor, scopes, inputs, expected fingerprints, phases, checkpoints, proposals, validation, and undo | Durable local operation journal |
| Rights grant | Actor, source, operation, permitted transformation/egress/export, status, and expiry where applicable | Local policy record |
| Accepted revision | Artifact ID, accepted fingerprint/revision, reviewer, validation result, dependencies | Acceptance record linked to artifact |

Typed relations include structural containment, prerequisite, recommended-before,
corequisite, alternative or cardinality choice, alignment, treatment, citation,
derivation, binding, supersession, and migration. Structural order must never
imply prerequisite status. Alignment must never imply evidence transfer.

### 2.3 Boundaries and authority

1. One parser produces the canonical bank or lesson model. Renderers, indexes,
   exports, and agents consume it.
2. The runtime alone scores, grants keyed disclosure, selects authoritative
   assessment behavior, and writes assessment evidence. Prose remains pending
   until approved marking.
3. Accepted course, lesson, bank, note, and evidence files are canonical.
   Search indexes, thumbnails, HTML, caches, rankings, progress views, media
   conversions, and job summaries are derived and disposable.
4. Accepted content, workflow state, epistemic confidence, validation state,
   rights state, and availability are separate axes.
5. Presentation visibility is not authorization. Hidden keys, roots, sources,
   or reviewer content remain protected by runtime and filesystem boundaries.
6. Agents receive only approved source spans and operation authority. Discovery
   does not grant writing, transformation, execution, network egress, or export.

## 3. Core end-to-end loops

### Loop A: discover, reconcile, and bind

`declare read roots and rights -> scan read-only -> identify by stable ID plus
fingerprint -> preview and classify -> surface duplicates, moves, conflicts,
and unsupported files -> choose link/import/copy/move/ignore -> bind source or
artifact to objectives -> validate -> checkpoint and index`

The default is link and edit in place. Name similarity is only a search hint.
No automatic merge is permitted. This consolidates `07-file-lifecycle-edge-cases.md`
file-operation and conflict sections with `09-app-flow-information-architecture.md`
sections 10 through 14.

### Loop B: design a course

`establish target and authoritative scope -> import or draft graph -> separate
outline from prerequisites -> map sources and existing artifacts -> classify
coverage -> choose treatment per objective -> define paths and completion policy
-> review gaps and conflicts -> accept a versioned course plan`

Treatment choices are direct reading, excerpt, guided lesson, notes or terms,
worked example, visual or demonstration, practice, formal test,
assessment-first diagnostic, learner artifact, or human review. Direct reading
is not a failure to generate.

### Loop C: learn and construct notes

`resume with objective and rationale -> orient to source, privacy, and expected
action -> read, observe, predict, manipulate, explain, or construct -> optionally
or conditionally capture notes -> inspect citation/source -> perform a check ->
receive allowed feedback -> transfer in changed context -> save position and
next action`

Reader and guided presentations share one lesson. Registered strategies may
pre-highlight, prompt selection, require restatement, build a guided note spine,
or leave notes optional. Every required action has an accommodation-equivalent
path. See `12-active-annotation-notes.md` sections 4 through 12.

### Loop D: practice and test

`choose practice or enter a fixed test -> runtime provides public item -> learner
responds -> runtime records and scores or marks pending -> runtime grants the
permitted feedback tier -> practice may remediate and retry -> test preserves
formal conditions -> report separates settled, pending, unknown, and omitted`

Practice and formal test remain distinct modes. Visible widgets do not determine
authority. Purpose, construct, response form, feedback, and evidence are separate
fields. See `03-question-activity-matrix.md` sections 4 through 8.

### Loop E: evidence and remediation

`replay a named evidence snapshot -> show scope, denominator, window, pending,
unknown, and uncertainty -> explain a recommended next action -> learner accepts,
chooses another, or overrides -> revisit prerequisite, explanation, worked
example, changed-context transfer, or delayed retrieval -> append new evidence`

Completion, coverage, participation, settled evidence, retention, enrichment,
and uncertainty never collapse into one score. See
`08-curriculum-hierarchy-progress.md` section 6.

### Loop F: author, review, and accept

`declare objective, treatment, sources, write scope, and authority -> discover
existing work -> draft smallest missing semantic artifact -> record provenance
and fallbacks -> parse/lint/render/test -> show bounded diff, consequences, and
undo -> accept/reject/revise -> publish accepted revision -> mark derivatives
stale and rebuild`

Question proposals additionally pass blueprint, construct, key, distractor,
difficulty, and scorer checks. Generated visuals and media require rights,
accessible alternatives, and human acceptance.

### Loop G: maintain, recover, and leave

`detect external/source/version change -> mark affected bindings and proposals
stale -> compare base/current/proposal -> rebind, migrate, supersede, or retain ->
write atomically with journal -> validate -> export package and loss report ->
restore on a clean machine -> rebuild disposable state`

Crash, cancellation, disk-full, offline, permission-denied, future-schema, and
agent-unavailable states must preserve the last accepted state and expose the
next safe action.

## 4. Semantic primitive set

### 4.1 Shared primitives

| Primitive | Visible features that compose from it |
|---|---|
| Stable object plus typed relation | citation, backlink, note anchor, objective link, source comparison, provenance trail, deep link |
| Semantic teaching block | key idea, warning, prerequisite, misconception, expert tip, worked example, counterexample, source excerpt, uncertainty, summary |
| Term plus definition relation | hover/focus definition, glossary, search preview, inline expansion, note insertion |
| Activity purpose plus response schema | prediction, noticing, retrieval, comparison, diagnosis, practice, transfer, reflection, formal assessment |
| Disclosure and feedback policy | hint ladder, prediction reveal, remediation, explanation depth, test silence |
| Strategy registration | continuous reading, guided lesson, guided notes, worked reasoning, retrieval-first, assessment-first |
| Artifact lifecycle state | draft, validating, accepted, stale, conflicting, superseded, retired |
| Operation journal | agent activity, audit trail, progress, checkpoints, diagnostics, undo |
| Capability support profile | accessible behavior, offline fallback, renderer availability, version, validation, known limits |
| Scope plus denominator claim | coverage counts, completion, evidence summary, retention snapshot, job progress |
| Source/media record | citation preview, asset credit, rights disclosure, derivation, cache policy, export manifest |

States that look similar remain separate. `pending` is workflow or evidence
state, low confidence is epistemic state, and invalid is validation state.
`Unavailable`, `unsupported`, `unknown`, `empty`, and `error` require different
recovery actions.

### 4.2 Distinct contracts that must not be reduced to styling

- Assessment items and sessions require runtime authority and a frozen public
  payload boundary.
- Learner notes and artifacts require learner ownership, privacy, revision, and
  promotion rules.
- Trusted interactive models require a registered component, bounded data,
  equivalent controls, static cases, deterministic or declared behavior, and no
  authored executable authority.
- Executable notebooks require restricted preview, explicit execute authority,
  environment declaration, captured derived output, and a static instructional
  path.
- Media require rights, credit, accessibility, derivation, availability, and
  integrity metadata.
- Agent operations require permission, egress, checkpoint, review, and recovery
  semantics beyond a chat transcript.
- Interchange adapters require a supported profile, conformance fixtures, and
  an explicit semantic loss report.

## 5. Hierarchy, pathways, and honest progress

Adopt a layered graph with explicit projections, as recommended in
`08-curriculum-hierarchy-progress.md` sections 4.2, 6, and 13.

- Entity identities are independent of labels and display paths.
- Structural nodes accept local labels such as program, semester, module, week,
  unit, or chapter without schema changes.
- Dependency edges carry type, authority, rationale, confidence, and override
  policy. Hard gates are exceptional.
- Required, required-choice, and enrichment membership have separate
  denominators. Adding enrichment cannot lower completion.
- Reusable artifacts are linked through course-specific treatment bindings and
  overlays, not copied by default.
- Imported frameworks are immutable versions. Local edits are overlays.
- Splits, merges, renamed objectives, and changed demand create migration
  proposals. Historical evidence is never transferred automatically.

Progress claims use the tuple:

`claim kind + scope/version + numerator + denominator or indeterminate + rule +
snapshot/window + settled/pending/unknown + authority + uncertainty`

Seven dimensions remain independent: design coverage, participation, settled
evidence, current retention, formal completion, selected enrichment, and
uncertainty. A bounded, versioned course may truthfully be 100 percent complete
under a named predicate. An open field such as mathematics has no universal
completion percentage. Formal completion persists while retention may decay.

## 6. File, identity, and interoperability model

The default workspace links user files where they live and edits owned files in
place. A course may span multiple roots, including a vault, source directory,
bank directory, and learner-note directory.

| Operation | Identity and ownership effect | Approval and recovery |
|---|---|---|
| Discover | None | Read-root approval; cancellable; omissions visible |
| Link or bind | Preserve external identity and location | Review relation; unlink reverses |
| Import | Create owned snapshot with origin relation | Destination and rights approval; retain source identity |
| Copy | Mint new identity and `derived-from` relation | Explicit reason and destination |
| Move | Preserve identity, change locator | Preview affected links; atomic move or rollback |
| Edit in place | Preserve identity, advance revision/fingerprint | Expected-base fingerprint, bounded diff, atomic replace |
| Supersede | Preserve old and new identities plus relation | Reviewer acceptance; old revision remains recoverable |
| Migrate | Preserve history through explicit mapping | Dry run, loss report, journal, old-or-new atomicity |
| Synchronize | Reconcile concurrent histories | Deferred until local revision/event model passes conflict tests |

Stable opaque IDs, paths, fingerprints, revisions, profile versions, source
versions, and generator versions serve different purposes. Hashes detect change
but do not prove identity, truth, authorship, or rights. Same ID with divergent
bytes is a conflict. Same fingerprint with different IDs suggests a copy or
duplicate. A moved path with the same ID is a move candidate. Similar names
never justify identity.

The canonical lesson is UTF-8 Markdown with shallow metadata and an additive,
versioned semantic profile. Complete core meaning, captions, citations,
definitions, static activity instructions, and media alternatives remain
readable outside the app. Trusted UI behavior derives from validated data.
Unknown optional semantics render their fallback with a warning; unknown
required semantics fail safely. A proprietary canonical format remains rejected
unless it passes all criteria in `04-portable-contract-agents.md` section 8,
"Proprietary format decision criteria."

Portability is reported at five levels: readable, structurally editable,
behaviorally executable, evidence-preserving, and round-trip safe. Export is not
complete until a clean-machine, offline restore validates a manifest and reports
every loss. EPUB and narrow QTI profiles are prototypes. Full QTI, CASE, CTDL,
SCORM, OLX, H5P packaging, and collaboration adapters wait for named consumers.

## 7. Lessons, notes, questions, media, and activities

### 7.1 Lesson and direct-reading model

One accepted instructional sequence may combine orientation, direct source
reading, definition, explanation, example, prediction, observation, learner
construction, check, feedback, transfer, and next action. Not every objective
needs every role. The course may register multiple sequences when evidence and
objective demands support them.

Reader mode preserves authored order. Guided mode stages the same blocks,
persists position separately, and invokes registered interactions. A source pane,
citation preview, or contextual agent may assist without replacing the lesson or
course map. Generated synthesis is visibly distinguished from quotation,
paraphrase, learner note, and accepted author text.

### 7.2 Active notes

Notes are learner-owned artifacts, not annotations baked into accepted lessons.
Minimum fields are note ID, learner ownership, course/objective relation, anchor
or selector, source/lesson revision, authorship type, strategy, text or structure,
privacy, revision, and optional promotion/review state.

Initial registered strategies should be finite:

1. Continuous reading with optional highlight and note.
2. Guided note spine with prompted selection and restatement.
3. Worked reasoning with prediction, explanation, and self-check.
4. Retrieval-first or assessment-first route where objective policy permits.

Pre-highlighting is authored orientation, not evidence. Copying alone is not
credited as understanding. Required note construction must state purpose and
offer an accessible equivalent or justified skip. Notes may seed draft practice
or reflection, but accepted sources and reviewed content control keys.

### 7.3 Questions and learner activities

Every activity declares purpose, cognitive demand, objective, stimulus/source,
response schema, retry behavior, feedback/disclosure policy, evidence status,
accessibility equivalence, and static fallback. The existing response forms can
serve many purposes. New item types are warranted only when scoring semantics or
response structure cannot be expressed safely by existing contracts.

Formal assessment fidelity requires a cited, versioned blueprint with construct,
domain weight, demand, format, difficulty, timing, tools, and feedback conditions.
Practice-generated questions remain drafts until parser, lint, review, blueprint,
and runtime gates pass. Learner-created proofs, programs, diagrams, and prose
produce descriptive or pending evidence until reviewed.

### 7.4 Media and interactive activity

Audio is a synchronized companion with transcript, chapters, citations, speed,
resume, and an equivalent text lesson. Generated image, diagram, simulation, or
video acceptance requires treatment rationale, source basis, review, rights,
caption, concise alternative, long description or data/table fallback,
interaction equivalence, and stale-derivative tracking.

Do not build generic AI video, podcast theater, infographic galleries, decorative
card inventories, or arbitrary per-lesson scripts as core. Prototype one
accessible visual-math interaction and one trusted simulation declaration before
expanding the registry.

## 8. Modes, strategies, preferences, and fixed policy

| Layer | Who controls it | Examples |
|---|---|---|
| Learner preference | Learner, reversible at any safe transition | reader/guided view, density, theme, allowed note strategy, explanation form, choose-another next action |
| Author/course strategy | Course builder within catalog | authored sequence, required artifact, allowed practice route, prerequisite recommendation, direct-reading treatment |
| Objective constraint | Objective and blueprint authority | cognitive demand, required construct, transfer condition, permitted evidence |
| Accommodation override | Learner need or assigning authority | equivalent input/output, pace, reduced motion, nonvisual representation, skip/substitute inaccessible action |
| Instructor policy | Assigning authority for bounded course | required path, deadline, formal completion predicate, test conditions |
| Runtime authority | Fixed and not user-configurable during a sitting | scoring, item selection policy, keyed disclosure, retries, formal-test pause, pending prose |
| System safety | Fixed | permission scope, rights/egress checks, no authored script authority, atomic mutation, conflict refusal |
| Visual presentation | Theme system within fixed hierarchy/accessibility rules | palette, density, typographic theme, optional motion under reduced-motion rules |

A strategy is registrable only if it shares the canonical objects, has a purpose
and eligibility rule, defines required and optional learner actions, skip/resume,
evidence effects, accommodations, offline behavior, and tests. Avoid a Cartesian
product of arbitrary style toggles. Teaching voice may change examples and
explanation density, but not facts, citations, objective alignment, keys, or
assessment difficulty without review.

## 9. App information architecture and visual direction

### 9.1 Information architecture

App level:

- Home: course shelf with exact resume cue and attention state.
- Search: accepted and draft objects across approved indexed roots, with result
  type, provenance, validation, and index age.
- Activity: durable agent and maintenance jobs, needs-input, outcomes, and
  recovery.
- Utilities: Help, Settings, Diagnostics.

Course level:

- Overview: current goal, next justified action, blockers, alternate actions.
- Learn: direct readings, lessons, guided activities, and contextual notes.
- Practice: formative activities and runtime-governed remediation.
- Test: quiet formal sitting with only permitted controls.
- Course map: outline first, graph and coverage projections second.
- Sources: scope, rights, bindings, locators, conflicts, and source inspection.
- Build/review: treatments, drafts, diffs, validation, acceptance, upgrades.
- Evidence: honest snapshots and remediation rationale.
- Notes: initially contextual within Learn and Evidence; a cross-course
  destination is deferred until actual use demonstrates the need.

Navigation uses stable opaque deep links and anchors, explicit parent/back
semantics, focus and scroll restoration, and the same routes across wide and
narrow layouts. Supporting panes become stacked destinations on narrow screens.
Chat is contextual to an object or operation, never the home or sole job record.

### 9.2 Chained first-run and packaged-app flow

First launch offers a clearly synthetic, removable sample course and a skippable,
replayable contextual walkthrough. A learner can reach a first local success
without granting source roots or configuring an agent. Help is offline and
routes from named error codes. Settings expose approved roots, backends,
network/egress policy, accessibility, theme, storage, backups, and updates.

The packaged app must preserve local Learn, Practice, Test, Evidence, Search over
the last valid index, and plain-file access when agents or networks fail. Long
jobs never block learning and never invent a percent when the denominator is
unknown. Install repair, update rollback, data-aware uninstall, diagnostics
redaction, backup, evacuation, and restore receive explicit owners before release.

### 9.3 Visual system

Use the Structured Studio direction from `10-visual-experience-system.md`
sections 6.2, 6.4, and 7 as the default. Borrow Quiet Workbench's calm density
for long reading and review. Use Guided Canvas staging only inside bounded
learning moments. This combination is coherent because all three project the
same semantic flow; it is not three theme-specific products.

Configurable: light/dark palette, density, reading measure within safe bounds,
font choice from approved local assets, modest surface treatment, and optional
motion. Fixed: content hierarchy, status meaning, focus visibility, contrast,
keyboard order, target size, zoom/reflow, reduced motion, non-color state cues,
source and acceptance visibility, and semantic equivalence across widths.
Authors select semantic roles, never raw colors, shadows, coordinates, arbitrary
icons, or animation.

## 10. Agents, skills, validation, and legacy upgrades

All clients implement one operation protocol:

`declare intent -> declare approved roots, rights, egress, write, and execute
authority -> inventory before creating -> plan treatment -> checkpoint -> draft
smallest missing artifact -> cite and label synthesis -> deterministic validation
-> accessible/plain/rich preview -> bounded diff -> configured review -> atomic
acceptance -> dependency/staleness update -> undo and uncertainty report`

Hosted, local, and manual continuation share durable checkpoints. Backend changes
capability, latency, cost, and privacy disclosure, not artifact or authority
contracts. An agent may recommend, draft-and-review, or perform approved bounded
writes. It cannot self-expand scope, self-certify accessibility, silently accept
its own uncertain source claim, transfer evidence, or cross runtime disclosure.

Required skill responsibilities:

- `build-course`: orchestrate course lifecycle, permissions, identity,
  treatments, validation, acceptance, evidence review, and recovery.
- `curriculum-design`: graph, authority, blueprint, prerequisites, pathways,
  completion policy, source coverage, and migration proposals.
- `absorb-book`: objective-by-objective direct-reading versus synthesis
  decisions, locators, rights, lesson/note/example proposals.
- `author-bank`: purpose, demand, blueprint, item construction, lint, statistical
  review, runtime validation, and no learner-note key laundering.
- `guiding-questions`: operate only from runtime public payload and granted tier.
- New lesson-authoring skill: semantic roles, complete Markdown, citations,
  accessibility, capability profile, render and lint loop.
- New discovery/binding skill: root scopes, identity reconciliation, link/import
  semantics, conflicts, and no mutation during inventory.
- New media-intake skill: rights, credit, accessible alternative, derivation,
  local/remote policy, and stale tracking.
- New legacy-upgrade skill: baseline audit, learning-value delta, identity and
  assessment preservation, bounded diff, validation, and rollback.

Legacy upgrades begin with current parse, identity, fingerprint, objectives,
sources, rights, media, assessment boundaries, plain rendering, rich rendering,
and validation. Cosmetic novelty is rejected. If the old artifact cannot express
an optional enhancement, retain it and link a derived enhancement with its
portability cost. Assessment-semantic changes are separate reviewed revisions.

## 11. Cross-cutting rules

1. **Privacy:** evidence and banks stay on disk. Hosted operations minimize and
   disclose exact egress. Scratch work is not submitted evidence. Diagnostics
   redact secrets, protected content, private paths in portable reports, and keys.
2. **Rights:** rights are operation-specific: read, quote, transform, remote
   process, package, export, and share. Unknown remains unknown and restrictive.
3. **Localization:** canonical records carry language and direction. Tests cover
   RTL, mixed code/math direction, CJK, combining marks, long strings, localized
   numbers/units, and culturally dependent examples.
4. **Accessibility:** WCAG checks are necessary but insufficient. Representative
   authored outputs require keyboard, touch, screen-reader, zoom/reflow, high
   contrast, reduced-motion, and equivalent-task review. AI does not self-certify.
5. **Scale and search:** discovery is bounded, cancellable, resumable, symlink-safe,
   permission-aware, and useful before full completion. Search exposes scope,
   index age, type, provenance, ranking rationale where relevant, and stale state.
6. **Synchronization:** accepted local revision and event semantics come first.
   Cross-device sync and collaboration remain deferred until deterministic
   conflict, deletion, key, and ownership rules exist.
7. **Reliability:** every durable mutation uses expected fingerprints, temporary
   output, validation, atomic commit, and journal. Fault injection must yield the
   old or new valid state, never a mixed state.
8. **Evaluation:** evaluate learning, authoring quality, time-to-course, search,
   and recovery locally with synthetic or consented fixtures. Page views, clicks,
   streaks, and time are not learning evidence.
9. **Maintenance:** each capability has an owner, version, validator, fallback,
   dependency/license record, research refresh trigger, migration rule, fixtures,
   and retirement path. Unsupported capabilities degrade visibly.

## 12. Product portfolio and permanent disposition ledger

This ledger groups true duplicates while retaining disagreements. The permanent
disposition vocabulary is:

- **Core now:** part of the durable architecture or immediate contract.
- **Registered:** a configurable mode, strategy, renderer, adapter, or optional
  capability that composes through shared contracts.
- **Prototype:** viable, but evidence, interaction, authorability, or format
  details must be tested reversibly before commitment.
- **Backburner:** useful, not timely. Its dependency, cost, and revisit trigger
  remain explicit.
- **Superseded:** the underlying user value is retained through a better shared
  mechanism, so the original implementation form is not built.
- **Hard reject:** conflicts with a named authority or quality rule and has no
  safe form under the current architecture. It remains in section 12.4 forever.

An execution phase selects a bounded subset of `Core now`, `Registered`, and
passed prototypes. It does not erase the rest of the product architecture.

### 12.1 Baseline expectations

| Grouped proposal | Disposition | Reason and evidence | Revisit trigger |
|---|---|---|---|
| Course-first shelf, overview, resume, Learn/Practice/Test, Sources, Map, Review, Evidence | Core now | Coherent app loop, `09-app-flow-information-architecture.md` sections 11 through 16 | N/A |
| Stable IDs, fingerprints, revisions, versions, typed relations, acceptance and staleness | Core now | Shared foundation across reports 04, 07, 08, 09, 11, 13 | N/A |
| Link/edit in place across multiple approved roots | Core now | Direct user requirement and `07-file-lifecycle-edge-cases.md` | N/A |
| Read-only discovery, explicit permissions, operation journal, conflict refusal, recovery | Core now | `07-file-lifecycle-edge-cases.md`; `09-app-flow-information-architecture.md` sections 10 and 14 | N/A |
| Typed graph kernel with outline projection and local labels | Prototype to core | Best cross-subject model, `08-curriculum-hierarchy-progress.md` sections 4 and 13 | Graph-to-outline tracer passes |
| Separate honest progress dimensions | Prototype to core | Prevents false mastery, report 08 section 6 | Users answer scope, authority, remaining work, and knowledge questions correctly |
| Portable Markdown lesson profile and one canonical model | Prototype to core | Strong portability/authorability fit, report 04 sections 7 and 8 | Stress corpus validates the profile or identifies an open package need |
| Source citations, provenance, rights, media alternatives | Core now | Reports 01 sections 5 and 6; 04 section 6; 11 section 5 | N/A |
| Purpose-first activities and runtime-owned assessment | Core now | Report 03 sections 4 through 9 | N/A |
| Active notes as separate learner-owned artifacts | Prototype to registered strategies | Report 12 sections 8 through 14 | Guided-note and incorrect-note tests pass |
| Accessible/offline capability profiles and loss reports | Core now | Reports 05 sections 8 through 10 and 13 sections 13 through 16 | N/A |
| Sample course, contextual walkthrough, offline help, diagnostics | Core now | Report 09 sections 11 through 15; report 13 baseline ledger | N/A |

### 12.2 Differentiators and optional extensions

| Proposal | Disposition | Reason | Revisit trigger |
|---|---|---|---|
| Source-to-objective treatment recommendation with rationale | Prototype, then differentiator | Core user value but quality and automation preference unproven | Four-subject expert review shows faster decisions without generic lesson bias |
| Citation preview plus source jump and comparison | Core now differentiator | Inspectable grounding without notebook-first IA, report 01 sections 3.4 and 4 | N/A |
| Evidence-linked remediation chain | Core now differentiator | Connects miss to misconception, transfer, and retrieval, report 05 section 9 | N/A |
| Multiple registered evidence-backed learning strategies | Prototype to registered | Valuable learner choice; one strategy interface controls combination cost, report 12 section 10 | Finite strategies pass accessibility/outcome tests |
| Contextual source-grounded agent | Registered optional mode | Helpful side channel, not durable course spine, report 01 sections 3.3 and 6 | N/A |
| Synchronized audio companion | Registered optional representation | Useful access modality with maintenance cost, reports 01 and 05 | Listening/accessibility validation and stale tracking pass |
| Semantic concept/prerequisite graph view | Prototype as secondary view | Useful overview, but outline remains primary | Structured and graphical parity test passes |
| Learner artifact and local coach review packet | Prototype | Adds authentic production without social platform | Pending-review and privacy flow solves real feedback need |
| EPUB export and narrow QTI round trip | Prototype | Tests portability; does not replace internal authority | Named target plus conformance and loss gates |
| Cross-course Notes destination | Backburner | Placement and frequency unproven; adds navigation and search maintenance | Usage study shows persistent cross-course retrieval need |
| Notebook page, outline, Cornell notes, concept map, glossary, formula sheet, timeline, comparison table, study guide, and source-extracted notes | Registered output modes after prototype | They share stable relations and provenance but retain distinct intent, structures, learner actions, and validators, `06-feature-style-atlas.md` sections 4.3, 10, and 11 | Note-mode trio and output-specific validators pass |

### 12.3 Subject-specific features and prototypes

| Proposal | Disposition | Boundary or gate |
|---|---|---|
| Accessible visual-math model with sonification/static cases | Prototype | Equivalent controls/evidence, keyboard/touch/screen-reader/offline pass |
| Code prediction, execution, inspection, and modification | Prototype | Restricted execution, static trace, derived-output provenance, runtime failure path |
| Medical evolving case and jurisdiction warning | Prototype fixture | Runtime disclosure, dated jurisdiction/source conflict, no premature reveal |
| History/source disagreement and disputed timeline | Prototype fixture | Preserve disagreement, locators, uncertainty, stacked fallback |
| Formula sheet, glossary, comparison table, timeline, Cornell note, concept map | Compose from note schema and semantic relations | Do not mint separate canonical types unless validation or behavior differs |
| Executable notebook | Link/restricted-preview first; execute optionally | Explicit environment and authority, no auto-run, static lesson path |

### 12.4 Permanent rejection and supersession ledger

This ledger is append-only in future revisions. A rejected or superseded idea is
never deleted, even if the surrounding architecture changes. Date for this
initial synthesis disposition is **2026-08-13**.

| Proposal | Source or vision origin | Evidence considered | Disposition and exact reason | Conflicting rule or quality attribute | Alternatives retained | Date | Reconsideration condition |
|---|---|---|---|---|---|---|---|
| Chat-first home, chat history as course map, or agent activity as product center | `USER-VISION.md` source-grounded and NotebookLM ideaboarding; report 01 | `01-source-grounded-products.md` sections 3.3, 4, 6; report 09 sections 11 to 16 | Superseded by course-first workspace because chat cannot preserve accepted objects, coverage, review, resumption, or safe operation state | Coherent product model, provenance, maintainability | Contextual source chat and object-scoped agent actions | 2026-08-13 | Reconsider only if chat projects the same durable objects and never becomes their sole state |
| Automatic artifact gallery or one-shot generate-everything workflow | NotebookLM and course-generation vision entries | Report 01 sections 3.3 to 4; report 05 sections 8 to 10 | Superseded by treatment-driven generation because automatic parallel artifacts lack objective need and create verification/staleness cost | Pedagogy, maintainability, truthful provenance | Every artifact family remains available through a treatment or registered output | 2026-08-13 | Reconsider default automation after measured review burden and artifact-use evidence |
| Fixed universal hierarchy or tree as prerequisite model | Hierarchy vision entry and coverage audit | `08-curriculum-hierarchy-progress.md` sections 4, 7, 10, 13 | Superseded by typed graph plus authored outline because one tree cannot represent alternate paths, reuse, cross-listing, and distinct dependency authority | Coherent product model, truthful evidence | Familiar outline projection with user-defined level labels | 2026-08-13 | Reconsider only as a projection, never canonical storage, unless all required fixtures fit losslessly |
| One aggregate completion, mastery, readiness, or personalization score | Progress vision and expected-feature audit | Report 08 section 6 and 13; report 11 sections 3 and 9 | Hard reject because it combines incompatible denominators and implies certainty unsupported by evidence | Truthful evidence, learner agency | Separate coverage, participation, evidence, retention, completion, enrichment, and uncertainty plus contextual summary | 2026-08-13 | No reconsideration as an authoritative claim; a summary may link visibly to all component claims |
| Viewed, clicks, elapsed time, streaks, percentile, or engagement used as mastery | Learning-metrics vision | Reports 05 sections 7 to 10; 08 section 10; 11 sections 8 to 9 | Hard reject because participation and comparison do not establish understanding | Truthful evidence, privacy | Local participation state, valid response evidence, learner-controlled reminders | 2026-08-13 | Reconsider a signal only with construct-valid evidence and no surveillance incentive |
| Punitive streaks, hearts or lives, paid error relief, compulsory leaderboards, or public comparison | Broader feature research request | `05-learning-program-landscape.md` sections 7, 9, 10; report 11 motivation analysis | Hard reject because these punish error or absence and distort learning incentives | Pedagogy, learner agency, privacy | Calm progress, purposeful play, optional private reminders | 2026-08-13 | A separately scoped social product with evidence of benefit and safeguards, never as core mastery |
| Arbitrary authored JavaScript, auto-running imported notebooks, or untrusted active embeds | Rich lesson, executable notebook vision | Reports 04 sections 6 to 9; 05 section 9; 07 executable-artifact sections | Hard reject because authored code would acquire executable authority outside trusted runtime components | Safety, accessibility, portability, maintainability | Registered trusted interactions, restricted notebook preview, explicit execution, static fallback | 2026-08-13 | Reconsider a specific sandbox only after threat model, reproducibility, equivalence, offline, and maintenance gates pass |
| Hover-only meaning, drag-only construct, or visual plus alt text treated as full equivalence | Hover/visual user vision | Reports 03 section 8; 06 missing-feature tests; 10 sections 7 to 11; 11 section 7 | Hard reject because required meaning or response becomes unavailable to keyboard, touch, screen-reader, or nonvisual learners | Accessibility, assessment validity | Hover/focus/touch glossary; equivalent controls, representation, feedback, and evidence | 2026-08-13 | Only the inaccessible implementation is rejected; the capability remains when equivalence passes |
| Hash, path, or display name as durable identity; automatic ambiguous merge | Find/link/edit vision | Reports 04 section 7.4; 07 identity/conflict sections; 13 section 12 | Hard reject because edits and moves break identity and ambiguous merges can destroy provenance | Safety, recovery, provenance | Opaque ID, fingerprint, revision, locator, explicit reconciliation | 2026-08-13 | Automatic reconciliation only for a proven unambiguous rule with recoverable audit trail |
| Derived HTML, index, cache, or registry as the sole understandable lesson/course meaning | Progressive-file vision | Report 04 sections 7.2 and 8; reports 05 and 13 portability sections | Hard reject because derived state can become stale, unavailable, or vendor-bound | Portability, maintainability, recovery | Canonical readable files plus disposable derived views | 2026-08-13 | Reconsider storage shape only if clean export/restore preserves complete meaning and one authority |
| Learner note silently promoted to accepted source, lesson, key, or mastery | Guided note and notes-to-question vision | `12-active-annotation-notes.md` sections 7 to 10 and 14; report 13 section 12 | Hard reject because learner notes may be incomplete or wrong and cannot silently acquire authority | Assessment authority, truthful evidence, provenance | Notes can ground reflection and draft questions; explicit review can promote source-backed content | 2026-08-13 | Explicit source-backed validation and reviewer acceptance |
| Copying protected commercial content, assets, visual identity, or distinctive voice | Brilliant visual ambition and competitor research vision | Research program copyright boundary; reports 05, 06, 10 pattern analyses | Hard reject because benchmark learning value does not grant copying or licensing rights | Rights and licensing, coherent original identity | Original Structured Studio system and transferable semantic patterns | 2026-08-13 | Only with an actual license and an independent product-fit review |
| Hidden citations or presentation state used as authorization | Source-grounded and rich UI vision | Report 01 sections 3.3 and 5; report 09 section 14 | Hard reject because hiding a panel neither revokes file access nor protects keys | Safety, privacy, assessment authority | Runtime/filesystem authorization plus always-inspectable provenance | 2026-08-13 | Never as authorization; presentation variants remain allowed |
| Automatic evidence transfer across renamed, split, merged, aligned, or superseded objectives | Flexible hierarchy and progress vision | Report 08 sections 5, 6, 10, 13; report 13 section 12 | Hard reject because similarity or alignment does not prove unchanged construct | Truthful evidence, provenance | Preserve raw evidence, propose reviewed mappings, show unknown and uncertainty | 2026-08-13 | Explicit construct-equivalence decision with preserved source events and disclosed uncertainty |

### 12.5 Backburner proposals

| Proposal | Dependency and cost | Why useful | Revisit trigger |
|---|---|---|---|
| Multi-device sync and collaboration | Stable local event/revision model; conflict, privacy, deletion, identity, hosting, and support cost | Continuity and shared review | Direct user need plus deterministic merge/delete/key model |
| Accounts, rosters, hosted gradebook, certificates, commerce, cohorts, social platform | Identity, authorization, moderation, compliance, hosting, and operating cost | Institutional and group learning workflows | Named institutional/product demand and separate scope |
| Full QTI, CASE, CTDL, SCORM, OLX, H5P, RDF/JSON-LD, IIIF authoring | Stable internal profile, named consumer, conformance suite, mappings, and maintenance | Exchange and institutional reuse | Consumer fixtures plus acceptable loss and support budget |
| Proprietary or open-package canonical lesson type | Stress corpus, migrator, tools, restore, dual-authoring risk | Could support an essential capability Markdown cannot express | All report 04 section 8 criteria pass |
| Required C2PA | Credentials, media coverage, verifier, dependency and UX cost | Stronger media provenance where available | Supported media workflow and credentials exist |
| Broad generative audio, video, infographic, and podcast modes | Treatment rationale, factual review, citations, rights, access, cache/storage, compute cost | Alternative explanations and accessibility when well designed | Narrow prototypes demonstrate learning/access advantage and sustainable review |
| Automatic archival scheduling | Reliable backup/restore, retention policy, user controls | Long-term maintenance at scale | Restore drills pass and storage history shows need |
| Cross-institution credit automation | Named authorities, equivalence policy, appeals, high-stakes review | Portable program/credit pathways | Authoritative partners and reviewed policy |
| Additional report templates, flashcard variants, visual explainer families, and artifact forms not covered by the initial registered outputs | Shared semantic roles and note/activity schemas, authoring/validation cost | Broad output choice requested by the vision | Register progressively after a purpose, distinct validator, and representative fixture exist |
| Native protocol registration, broad OS integrations, and cross-app round-trip sync | Packaging support and security/compatibility maintenance | Faster access and external workflow continuity | Demonstrated workflow frequency and three-OS feasibility |

### 12.6 Open decisions

Status annotations added 2026-08-14; the original open-decision record is
preserved unchanged below each annotation. CLOSED items are resolved in
`.planning/DECISIONS-PRE-14A-2026-08-14.md`; FRAMED items carry options and a
recommendation in `.planning/DECISIONS-12.6-REMAINING-2026-08-14.md` and are
decided at their owning subphase (or by Weibao where marked).

- Minimal Phase 14 edge vocabulary and whether graph records live entirely in
  Markdown or in a readable course sidecar.
  *(CLOSED 2026-08-14: hybrid, D-14A-1.)*
- Fingerprint normalization and the minimum component-ID granularity.
  *(CLOSED 2026-08-14: bounded component IDs, D-14A-2.)*
- Metadata threshold between local lesson fields and course registries.
  *(FRAMED: D-12.6-8, confirm at 14B.)*
- Naming for current evidence support currently called `mastered`.
  *(CLOSED 2026-08-14: Khan-style per-objective fill state, D-14A-3; level
  vocabulary routed to 16B.)*
- Authority for personal-course completion policies and solo self-acceptance by
  risk tier. *(CLOSED 2026-08-16: risk-tiered self-acceptance with a
  strictness setting, user-defined completion predicate; D-12.6-4 in
  `DECISIONS-12.6-REMAINING-2026-08-14.md`, resolved by delegation.)*
- Notes default placement and Evidence default prominence.
  *(CLOSED 2026-08-16: margin capture with course review, Evidence primary;
  D-12.6-5 in `DECISIONS-12.6-REMAINING-2026-08-14.md`, resolved by
  delegation, confirming 16C-UI-SPEC D1.)*
- Formal-test pause policy, which must be decided by runtime contract.
  *(CLOSED 2026-08-16: mode-dependent sealed pause, one mechanism gated by
  blueprint timing policy; D-12.6-6 in
  `DECISIONS-12.6-REMAINING-2026-08-14.md`, resolved by delegation.)*
- Trust persistence for executable sources: one run, file, fingerprint, or root.
  *(CLOSED 2026-08-16: per fingerprint with own-in-app-edit carry-forward,
  strictness setting for stricter modes; D-12.6-7 in
  `DECISIONS-12.6-REMAINING-2026-08-14.md`, resolved by delegation.)*
- Rights representation when the user does not know.
  *(FRAMED: D-12.6-9, confirm at 14B.)*
- Representative large-collection corpus and performance budgets.
  *(FRAMED: D-12.6-10, measure at 14A.)*
- Minimum packaged offline help/diagnostics bundle.
  *(FRAMED: D-12.6-11, confirm at 16B.)*

## 13. Traceability from user vision

Requirement families below include existing families and proposed additions in
section 14. Verification gates are defined in section 16.

| User-vision entry | Research evidence | Proposed contract clause | Requirements | Phase | Skills | Verification |
|---|---|---|---|---|---|---|
| Quality benchmark and original visual ambition | Reports 05 sections 7 to 10; 10 sections 6 to 11 | Semantic capability plus Structured Studio visual system; no copying | CAP, VISUAL, A11Y | 16C, 17 | lesson authoring, media intake | G4, G8 |
| Source-to-course goal | Reports 01 section 6; 08 sections 4 to 6; 09 sections 8 to 10 | Course, graph, treatments, core loops A to E | COURSE, GRAPH, TREAT, FLOW | 14, 15, 16 | build-course, curriculum-design, absorb-book | G1, G2, G5 |
| Course generator, exam alignment, metrics, rich UI, agents | Reports 03 sections 5 to 9; 05 section 8; 11 sections 8 to 10 | Blueprint, director authority, evidence honesty, learner UI | DIRECTOR, BLUEPRINT, EVIDVIEW, UI | 15, 16, 17 | build-course, author-bank, guiding-questions | G5, G7, G8 |
| Correct prior direction, audit phases, expose construction rules | Reports 04 sections 7 to 9; 13 sections 10 to 16 | Skills, validation, legacy audit, readiness audit | AGENT, UPGRADE, MAINT | 14A through 17 | all authoring skills | G6, G12 |
| Broad product and feature research | Reports 01 through 06, disposition sections | Portfolio ledger and rejection criteria | RESEARCH-GATE | 16A | research refresh playbook | G12 |
| Keep goal editable in own words | Coverage audit; Planning Directives sections 7 to 10 | Additive vision capture and traceability | VISION-GOV | Cross-cutting | reusable vision skill, separate project | G12 |
| Find previous lessons/banks in separate roots; progressive enhancement | Reports 04 sections 7.4 and 7.5; 07; 09 section 10 | Loop A, linked in-place files, audit-first upgrade | FILE, ID, UPGRADE | 14A, 14B, 16C | discovery/binding, legacy upgrade | G1, G3, G6 |
| UI flow, NotebookLM questions, broader activities, reusable visioning | Reports 01 sections 3 to 6; 03 sections 4 to 10; 09 sections 6 to 15 | Course-first IA, purpose-first activities, contextual source agent | FLOW, ACTIVITY, IA | 16B, 16C, 17 | lesson authoring, author-bank | G4, G7, G8 |
| Lesson breadth, note modes, styles, missing-feature tests | Reports 02; 06 sections 8 to 10; 12 sections 4 to 15 | Semantic roles, finite strategies, note ownership, stress fixtures | CAP, NOTE, STRATEGY | 16C | lesson authoring, absorb-book | G4, G9 |
| Files, hierarchy, onboarding, packaging, future audit | Reports 07; 08 sections 4 to 13; 09 sections 8 to 15; 13 sections 12 to 16 | Graph, file lifecycle, first run, packaged resilience, readiness audit | GRAPH, FILE, APP, MAINT | 14A, 14B, 16B, 17 | build-course, discovery/binding | G1, G2, G10, G12 |
| Complete app flow, visual experience, edit in place, edge cases | Reports 07; 09 sections 5 to 16; 10 sections 6 to 12; 11 section 7 | Loops A to G, IA, visual rules, adversarial matrix | FLOW, FILE, VISUAL, RELIABILITY | 14 to 17 | operation protocol across skills | G3, G8, G10 |
| Guided highlighting, learner-built notes, configurable paths | Report 12 sections 4 to 14; report 11 sections 3 and 6 | Separate notes, finite strategies, objective/accommodation/runtime precedence | NOTE, STRATEGY, A11Y | 16C, 17 | lesson authoring, guiding-questions | G9 |
| Expected features, omissions, one coherent product | Report 13 sections 8 to 16 | Shared primitives, disposition ledger, ownership and gates | BASELINE, MAINT | All | all | G11, G12 |

## 14. Exact change proposals by target file

These are proposals only. `New` adds a clause, `Replace` changes current wording,
`Supersede` records an intentional contract reversal while preserving history,
and `Archive/cleanup` removes obsolete navigation or duplicated guidance after
the replacement is accepted.

### `.planning/SOURCE-TO-COURSE.md`

- **New:** add "Object and authority model" using sections 2.1 through 2.3.
- **New:** add the seven core loops from section 3 and declare them the product's
  end-to-end acceptance surface.
- **Replace:** expand the fixed objective hierarchy into the constrained typed
  graph plus outline projection and honest-progress contract in section 5.
- **New:** add file-operation, identity, accepted revision, rights grant,
  derived-state, and clean-machine restore clauses from section 6.
- **New:** add learner note, learner artifact, strategy, and capability-profile
  clauses from sections 7 and 8.
- **New:** add the permanent disposition taxonomy and require every viable idea
  to remain as core, registered, prototype, or backburner. Link hard rejections
  to an append-only rejection ledger with provenance and reconsideration rules.
- **Supersede:** replace the simple Phase 14 to 17 sequence with the subphases in
  section 15, preserving the original sequence as historical rationale.

### `.planning/PROJECT.md`

- **Replace:** describe the primary product as a resumable course workspace with
  files, graph, treatments, learning, assessment, evidence, and recovery.
- **New:** add accepted-state, learner-ownership, rights, localization, and
  restoration principles.
- **New:** add explicit boundaries: derived views are not truth, presentation is
  not authorization, and note content is not assessment authority.
- **Archive/cleanup:** consolidate repeated bank-first and old phase descriptions
  after confirming all shipped-runtime context remains.

### `.planning/REQUIREMENTS.md`

- **Replace:** expand `COURSE-01..04`, `DIRECTOR-01..04`, and `LEARNUI-01..04`
  into families: `GRAPH`, `FILE`, `ID`, `TREAT`, `FLOW`, `CAP`, `ACTIVITY`,
  `NOTE`, `STRATEGY`, `RIGHTS`, `A11Y`, `PORT`, `RELIABILITY`, `APP`, `VISUAL`,
  `AGENT`, `UPGRADE`, and `MAINT`.
- **New:** make every requirement name owner, durable object, authority,
  degraded state, and verification gate.
- **New:** preserve architecture breadth through capability-catalog requirements
  even when implementation is staged. Registered and backburner capabilities
  name their shared primitive, dependency, cost, and trigger rather than being
  omitted from traceability.
- **New:** add requirements for atomic compare-and-swap writes, operation
  journals, stale proposal detection, objective migrations, honest progress,
  authored-output accessibility, localization fixtures, rights by operation,
  diagnostics redaction, and clean-machine restore.
- **Supersede:** any requirement implying a universal hierarchy, aggregate
  progress, or widget-specific lesson grammar.

### `.planning/ROADMAP.md`

- **Replace:** Phase 14 to 17 entries with section 15 subphases and dependencies.
- **New:** require prototypes before schema freeze, production UI, or broad
  interchange commitments.
- **New:** add a post-contract implementation-readiness audit and a post-Phase
  17 maintenance/restore audit.
- **New:** add a durable capability runway organized as registered extensions,
  prototypes, and backburner items. Promotion changes execution timing, not the
  existence of the proposal or its research trail.
- **New:** add the permanent rejection ledger as a roadmap governance input so a
  rejected idea cannot be silently reintroduced or deleted.
- **Archive/cleanup:** move completed or contradictory legacy roadmap prose into
  milestone history only after requirement traceability is regenerated.

### `.planning/UI-SPEC.md`

- **New:** add course-first IA, route/deep-link/resume semantics, durable jobs,
  approval hierarchy, and error/recovery matrix from sections 3 and 9.
- **New:** add structured equivalents for maps, panes, diffs, interactive
  activities, and progress claims.
- **Replace:** update visual direction to Structured Studio with contextual Quiet
  Workbench and bounded Guided Canvas, separating configurable tokens from fixed
  rules.
- **New:** add note construction, rights/egress, external-edit conflict, offline,
  localization, and packaged-help acceptance scenarios.
- **Supersede:** dashboard, bank-first, or visual-card language that conflicts
  with shared semantic primitives.

### `.planning/PLANNING-DIRECTIVES.md`

- **New:** qualify "build both" with the finite-strategy rule: shared semantics,
  authority, accessibility, permission, recovery, and maintenance contracts are
  prerequisites for registration.
- **New:** state that ideaboarding breadth is preserved by default. Coalescing
  organizes viable proposals into core, registered, prototype, or backburner;
  simplicity alone is not a rejection reason.
- **New:** require an append-only rejection record with proposal, origin,
  evidence, exact reason, conflicting rule, retained alternative, date, and
  reconsideration condition.
- **New:** require owner, verification, evidence class, and failure condition for
  every accepted recommendation.
- **New:** make reversible prototypes mandatory before durable format, graph,
  strategy, executable-source, or complex visual commitments.
- **Replace:** the Phase 16/17 split with the dependencies in section 15.

### `AGENTS.md`

- **New:** summarize the object/authority model and operation protocol.
- **New:** require compare-and-swap mutation, rights/egress declarations,
  separate state axes, authored-output accessibility, and clean recovery.
- **New:** instruct agents to preserve viable proposal breadth and update the
  permanent disposition/rejection ledgers rather than dropping untimely ideas.
- **Replace:** expand course workflow steps to include graph versioning, accepted
  revision, notes, learner artifacts, migration, and restoration.
- **Archive/cleanup:** remove duplicated skill prose only after skills themselves
  carry the detailed contracts.

### `.claude/CLAUDE.md`

- **New:** mirror the same non-negotiable operation, authority, rights,
  acceptance, and recovery summary as `AGENTS.md`.
- **New:** mirror the breadth-preservation and append-only rejection-ledger rule.
- **Replace:** stale bank-first or historical constraints with pointers to
  current binding files, keeping clearly marked history where useful.
- **Archive/cleanup:** consolidate repeated phase handoffs and old constraint
  interpretations after a drift audit against `AGENTS.md`.

### `README.md`

- **Replace:** lead with the source-to-course journey and a course-oriented quick
  start while retaining shipped bank commands as the current foundation.
- **New:** explain direct reading versus generation, link/edit-in-place roots,
  review and acceptance, learner notes, assessment authority, privacy/egress,
  portability levels, backup/restore, and unavailable-agent behavior.
- **New:** add task-oriented help paths for create, bind existing work, learn,
  practice/test, inspect evidence, upgrade, recover, and export.
- **New:** describe optional modes and future capability families without
  presenting every one as simultaneously shipped; link their status and gates.
- **Archive/cleanup:** group historical handoffs and implementation internals away
  from the first-run product story.

### Mirrored skill library

- **Replace:** update `build-course`, `curriculum-design`, `absorb-book`, and
  `author-bank` with section 10 responsibilities, then copy identically between
  `.agents/skills` and `.claude/skills`.
- **New:** add lesson-authoring, discovery-and-binding, media-intake, and
  legacy-upgrade skills with the shared operation protocol and validation gates.
- **New:** add a shared reference for objects, state axes, permissions, rights,
  provenance, acceptance, conflict, recovery, and reporting to prevent drift.
- **New:** add disposition behavior: agents preserve useful proposals as
  registered, prototype, or backburner entries and may hard-reject only for the
  named authority/quality conflicts, recording the full permanent ledger row.
- **New:** extend `guiding-questions` only to consume new activity context while
  preserving its no-key runtime boundary.
- **Archive/cleanup:** remove duplicated local rules after shared references are
  versioned and mirror-diff CI covers them.

## 15. Phase 14 through 17 reassessment

The high-level order remains correct: durable course/file semantics precede AI
course direction, logical learning contracts precede visual productization.
The current four broad phases are too coarse and place some Phase 16 discoveries
after Phase 14 format commitments. Use subphases, not a new top-level phase.
These subphases bound execution, not product possibility. Each freezes shared
interfaces and can register multiple capabilities that compose cheaply. Optional
or expensive capabilities remain in the runway rather than being cut.

| Subphase | Deliverable | Depends on | Freeze gate |
|---|---|---|---|
| 14A: identity, lifecycle, and operation prototype | Stable IDs, revisions, fingerprints, operation journal, link/import/move/edit/supersede semantics, atomic recovery | Shipped parser/runtime | File fault and external-edit tracer |
| 14B: graph and course package prototype | Typed graph kernel, outline projection, source/treatment bindings, versions, rights, minimal package | 14A | Three-domain graph tracer, clean restore, authorability review |
| 15A: director and treatment policy | Treatment recommender, source scope, rights/egress, autonomy levels, checkpoints | 14B | Four-subject recommendation review |
| 15B: quality, blueprint, and acceptance | Blueprint fidelity, course audit, accepted revision, staleness/dependency impact | 15A | Lesson plus practice acceptance tracer |
| 16A: semantic capability and activity contract | Lesson roles, activity-purpose matrix, capability profiles, media/citation policy | 14B, assessment runtime | Portable rich lesson stress corpus |
| 16B: IA, modes, and recovery contract | Core loops, routes, resume, jobs, approvals, offline/help/error states | 14A, 16A | Full storyboard and interruption scenarios |
| 16C: strategies, notes, and prototype convergence | Notes, learner artifacts, finite strategies, progress comprehension, legacy upgrade | 14B, 16A, 16B | Cross-subject missing-feature suite |
| 17A: visual system and component foundation | Tokens, hierarchy, responsive shell, accessible primitives | 16B, 16C | Same-flow visual comparison and accessibility QA |
| 17B: production vertical tracer | Polished unit from discovery through restore | All prior | End-to-end gates G1 through G11 |

Prototype before durable commitment:

- Graph-to-outline and denominator/version migration before course schema freeze.
- Markdown rich-lesson stress corpus before lesson-profile grammar freeze.
- Guided-note, worked-reasoning, and incorrect-note pathways before strategy
  registry or question-from-notes support.
- Restricted notebook preview before execute/trust UI.
- Visual-math equivalence before broad interaction registry.
- Cross-client interruption before agent job protocol freeze.
- Clean-machine restore before course package or export promise.
- Same logical flows in three visual directions before Phase 17 tokens freeze.

## 16. Exit gates and next readiness audit

### 16.1 Synthesis exit gates

- **G1 Coverage:** every row in `00-coverage-audit.md` maps to section 13 and a
  ledger disposition. Secondary checks include reports 05, 06, 09, 10, 11, 12,
  and 13 as routed.
- **G2 Object/authority:** every accepted feature maps to a durable or derived
  object, owner, authority, state axes, and source of truth.
- **G3 File safety:** move, duplicate, conflict, external edit, denied path,
  removable volume, interrupted write, and disk-full scenarios preserve the
  old or new valid state.
- **G4 Portable capability:** representative EMT, math, CS, and knowledge lessons
  remain coherent in plain Markdown, rich UI, narrow screen, keyboard, touch,
  screen reader, offline, and localization fixtures.
- **G5 Evidence honesty:** pending, sparse, unknown, stale, optional, split,
  merged, and retention-changed cases never become false mastery or completion.
- **G6 Assessment authority:** no surface, agent, note, import, or visual leaks a
  key, invents a score, auto-grades prose, or changes a frozen sitting.
- **G7 Course quality:** treatment and blueprint proposals cite scope, demand,
  rationale, uncertainty, and existing-artifact search, then pass review.
- **G8 Flow/visual:** first-run, resume, learn, practice, test, source inspection,
  review, agent failure, and narrow-screen transitions preserve context and
  hierarchy.
- **G9 Strategy/notes:** each strategy states choice, requirement, skip/resume,
  accommodation, evidence effect, privacy, provenance, and note-authority guard.
- **G10 Portability/recovery:** a clean machine restores all supported canonical
  objects and evidence offline; every unsupported capability appears in a loss
  report.
- **G11 Cross-cutting:** egress capture equals disclosed manifests; rights-unknown
  refuses unsafe operations; RTL/mixed notation works; large scans are bounded;
  diagnostics are redacted.
- **G12 Governance:** every accepted item has owner, phase, dependency, test,
  maintenance plan, and research/user-decision trigger where uncertain.

### 16.2 Completeness check against `00-coverage-audit.md`

All explicit ideas listed in its section "Explicit ideas and destinations" have
an evidence path and disposition:

- NotebookLM, Brilliant, broad products, niche programs, and GitHub patterns:
  sections 1, 4, and 12. Patterns accepted, copying and gallery parity rejected.
- Better lesson flow, definitions, highlights, images, diagrams, callouts,
  styles, note/full-learning outputs, question variety, and missing-feature
  tests: sections 4, 7, 8, 12, and G4/G9.
- Portable progressive files, agents, previous files in separate roots, edit in
  place, folders, notebooks, hierarchy, prerequisites, alternate paths, and
  honest progress: sections 5, 6, 10, 12, and G1 through G6.
- First-run, README/help, complete chained flow, visual experience, packaged app,
  privacy, rights, localization, scale, search, sync, evaluation, reliability,
  and maintenance: sections 9, 11, 14, 15, and G8 through G12.
- Active highlighting, learner-built notes, source/lesson/note sequences,
  strategy choice, and notes-to-question authority: sections 7, 8, and G9.
- Expected baseline, omissions, shared primitives, owners, and completeness:
  sections 2, 4, 12, and G12.

The cross-cutting additions in audit section "Cross-cutting additions found by
audit" are covered by capability profiles, learner artifacts, publication and
staleness, offline readiness, collaboration provenance, loss-aware adapters,
operation rights, and maintenance ownership. No audit idea is silently treated
as committed merely because it was routed to a report.

### 16.3 Next implementation-readiness audit

Run after the proposed contract files and requirements are updated, before any
Phase 14A implementation plan. It must:

1. Diff every accepted synthesis clause against the updated contract and expose
   missing, duplicate, conflicting, or weaker translations.
2. Map each requirement to one owner, subphase, prerequisite, fixture, success
   gate, degraded state, migration, documentation, and maintenance obligation.
3. Confirm prototypes occur before their dependent schema/UI freezes.
4. Build a dependency graph and reject circular ownership among course, lesson,
   evidence, notes, jobs, and UI state.
5. Separate foundation, prototype, productization, migration, documentation,
   packaging, and long-term maintenance work.
6. Confirm the shipped parser/scorer/evidence tests remain byte-compatible where
   required and that no second authority was introduced.
7. Produce a realistic execution sequence and name a new audit trigger after
   14B, 16C, and 17B.
8. Confirm every research proposal has a permanent disposition and every hard
   rejection contains all fields required by section 12.4. Fail the audit on a
   silently omitted, deleted, or simplicity-only rejection.

## 17. Unresolved choices and routing

### More ideaboarding

- How much learner choice should the default overview expose before it becomes
  distracting?
- Should Notes become a cross-course destination, and what real retrieval job
  would justify it?
- Which review decisions may a solo learner-builder self-accept?
- What emotional tone should progress use while remaining calm and honest?

### More research

- Rights policy for unknown, privately owned, licensed, and institutional
  sources across remote processing, transformation, packaging, and export.
- Reliable accessibility validation for authored math, audio, diagrams,
  sonification, and mixed RTL/code/math content.
- Representative large-root corpus and search quality measures without
  telemetry.
- Which interchange profiles have real consumers and acceptable semantic loss.

### Reversible prototype

- Graph/outline, denominator migration, Markdown stress corpus, note strategies,
  restricted notebooks, visual-math equivalence, interrupted agent handoff,
  clean restore, and visual-direction comparison, as listed in section 15.

### Direct user decision

- Default visual direction after the same-flow prototypes. This synthesis
  recommends Structured Studio.
- Default note strategy and whether required note construction is permitted by
  default.
- Personal-course completion authority and default rule.
- Hosted-agent egress default and remembered-consent scope.
- Initial interchange target, if any.
- Whether open-ended fields should offer user-frozen bounded goals as the main
  progress affordance.

## 18. Proposed decision

Accept this synthesis as the evidence-backed product-definition input for
contract revision, but do not treat open or prototype-gated recommendations as
format commitments. Keep the Phase 14 to 17 order, divide it into the subphases
in section 15, and run the implementation-readiness audit before planning 14A.
The product should become richer by composing stable semantics and trusted
behavior, not by accumulating disconnected features.
