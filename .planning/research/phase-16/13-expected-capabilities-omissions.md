# Stream 13: Expected capabilities and omission audit

**Status:** research complete for synthesis

**Access date for external sources:** 2026-08-13

**Method:** derive expectations from actors, jobs, lifecycle states, system
boundaries, failure modes, and quality promises first; compare the resulting
ledger with the scope and available outputs of Streams 01 through 12 second.

## 1. Scope and research questions

This report asks what a coherent local-first source-to-course workspace must do
even when nobody remembered to request the behavior as a feature. It covers the
learner, course builder, reviewer, source owner, instructor when present, and
hosted or local agent client from installation through long-term maintenance.

The questions are:

1. What jobs must each actor complete, and which actor owns each decision?
2. What states and transitions exist across the complete product lifecycle?
3. Which quality promises create baseline behavior in happy, degraded, failed,
   interrupted, accessible, private, large-scale, and portable use?
4. Which derived capabilities are already shipped, covered by Streams 01
   through 12, duplicated under different names, unsupported, or unowned?
5. Which behaviors should compose from shared primitives instead of becoming
   independent features?
6. What finite argument demonstrates useful coverage without claiming that an
   open-ended design search is complete?

Out of scope are visual styling decisions, competitor imitation, implementation
sequencing, and changes to binding product contracts. This report recommends
inputs to Stream 14 synthesis. It does not promote them to requirements.

### Evidence labels

- **Fact** means directly observed in this repository or a cited primary source.
- **Inference** means a consequence derived from facts and stated promises.
- **Recommendation** means a proposed disposition for synthesis.
- **Open question** means evidence or ownership is insufficient for commitment.

## 2. Sources and evidence limits

### Repository sources

| Source | Type | Use |
|---|---|---|
| [`AGENTS.md`](../../../AGENTS.md) | Shipped project instruction | Parser, scorer, privacy, source, authoring, upgrade, and commit boundaries |
| [`USER-VISION.md`](../../USER-VISION.md) | Authoritative verbatim intent | Desired source-to-course experience, AI role, rich lessons, file discovery, hierarchy, notes, and omission audit |
| [`SOURCE-TO-COURSE.md`](../../SOURCE-TO-COURSE.md) | Binding product contract | Course loop, objects, authority, quality promises, and scope boundaries |
| [`PLANNING-DIRECTIVES.md`](../../PLANNING-DIRECTIVES.md) | Binding planning rules | Autonomy, conflicts, immutable constraints, evidence basis, and vision handling |
| [`README.md`](../../../README.md) and source/tests | Shipped behavior | Current CLI, parser, runtime, surfaces, schemas, packaging, and deterministic checks |
| [`README.md`](README.md) and [`00-coverage-audit.md`](00-coverage-audit.md) | Research program contracts | Intended ownership and required coverage for Streams 01 through 14 |

### External primary sources

All links below were accessed 2026-08-13.

| Source | Source type | Relevant fact, not product prescription |
|---|---|---|
| [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Normative accessibility standard | Accessibility spans perceivable, operable, understandable, and robust content, with testable criteria and full-page conformance. It also states that conformance cannot meet every disability need. |
| [W3C Authoring Tool Accessibility Guidelines 2.0](https://www.w3.org/TR/ATAG20/) | Normative accessibility standard | An authoring product has two obligations: its own interface must be accessible, and it should support production of accessible content. |
| [W3C Internationalization Best Practices for Spec Developers](https://www.w3.org/TR/international-specs/) | Standards guidance | Formats and interfaces need explicit language, direction, character, locale, and text-processing behavior rather than an English-only assumption. |
| [W3C PROV-O](https://www.w3.org/TR/prov-o/) | Normative provenance recommendation | Entity, activity, and agent form a small interoperable provenance core; derivation, revision, quotation, and primary source are distinct relations. |
| [1EdTech QTI specification documents](https://www.1edtech.org/standards/qti/index) | Primary assessment interoperability specification | QTI exchanges item, test, and result content among authoring, banking, delivery, and scoring systems. Conformance profiles and validators exist. |
| [W3C EPUB 3.3](https://www.w3.org/TR/epub-33/) | Normative publication interchange standard | A portable publication can package structured semantic web content, resources, metadata, navigation, reading order, and fallbacks. |
| [RFC 8493, BagIt](https://www.rfc-editor.org/rfc/rfc8493.html) | IETF archival transfer specification | A transfer package can enumerate payloads and use manifests to detect incomplete or corrupt transfer. |
| [Library of Congress Sustainability of Digital Formats](https://www.loc.gov/preservation/digital/formats/) | Primary preservation guidance | Long-term format choice depends on disclosure, adoption, transparency, dependencies, self-documentation, and preservation risk, not file extension alone. |

These sources validate baseline expectations such as accessible authoring,
explicit provenance, international text behavior, conformance testing,
transfer integrity, and durable interchange. They do not prove that itembank
must implement each standard, nor do they validate a particular interface.

### Evidence limitation

At the comparison snapshot, the Phase 16 directory contained the research
index and coverage audit, while Streams 01 through 12 had not yet produced
their required output files in this shared worktree. Therefore the cross-stream
comparison below distinguishes **charter coverage** from **verified report
coverage**. Stream 14 must replace every `charter only` judgment with a check
against the completed report before accepting synthesis. Treating a promised
stream as evidence would hide omissions.

## 3. Shipped capability inventory

### Observed facts

The shipped system already provides more primitives than a greenfield feature
list would suggest:

| Shipped area | Observed capability | Authority or limit |
|---|---|---|
| Bank contract | One Markdown parser, item IDs and fingerprints, lint, stats, guard | Bank format is not yet a complete course workspace format |
| Assessment | One deterministic scorer, practice/test sessions, public item projection, tier gates, idempotent submit | Prose remains pending; clients cannot reveal keyed content early |
| Evidence | Local session records, objective reports, retention/due views, audit schemas | Evidence is assessment-oriented, not yet a complete course revision ledger |
| Learning surfaces | Lesson, study, day, quiz, presentation, audio, diagrams, themes | Surfaces are clients; they cannot create separate scoring or semantic truth |
| Authoring quality | Spec, actionable lint, authoring request and quality finding schemas, audit commands | A coherent multi-artifact review and acceptance workflow remains future work |
| Interchange | Anki and GIFT paths, LTI surface, normalized document and migration schemas | Export breadth does not prove lossless course round-trip portability |
| Agent protocol | JSON commands, model adapter/settings schemas, authoring and write manifests | Agent availability, permission, cancellation, and handoff need lifecycle treatment |
| Durability | On-disk banks and evidence, update/migrate surfaces, durability tests | Course backups, restore drills, source relinking, and interrupted bulk mutations are not established |
| Packaging | Launcher, daemon, packaged release tests, offline quiz | First launch, environment diagnosis, upgrade recovery, and uninstall/data retention are separate jobs |

**Inference:** the next product should extend these authorities with course,
source, objective, artifact, revision, permission, and operation primitives. It
should not replace proven parser, scorer, session, lint, or local evidence
contracts with a new all-purpose layer.

## 4. Actor and job map

| Actor | Core job | Decisions owned | Needs from others | Completion signal |
|---|---|---|---|---|
| Learner | Turn owned material into durable understanding and credible evidence | Goals, pace, optional strategies, private notes, consent, accommodations, overrides within course rules | Builder supplies coherent path; runtime supplies honest evidence; source owner supplies lawful access | Can resume, explain what is next and why, export work, and distinguish attempted, completed, reviewed, and mastered |
| Course builder | Convert targets and sources into an objective-aligned, teachable course | Scope proposal, objective map, treatment proposal, artifact drafts, course configuration | Source owner establishes rights; reviewer accepts claims; runtime validates assessment | Every in-scope objective has support, treatment, state, provenance, and validation, or an explicit gap |
| Reviewer | Decide whether artifacts and mappings are acceptable for use | Accept, reject, request change, waive with reason; never silently merge conflicts | Builder provides bounded diff, citations, uncertainty, and validation result | Accepted revision is identifiable, attributable, reproducible, and reversible |
| Source owner | Control where source files live and how they may be read, copied, transformed, quoted, or shared | Read/write roots, operation permissions, rights declarations, retention and deletion | Builder and agent explain intended operations and consequences | No action exceeds permission; each derivative retains source and rights context |
| Instructor | Define cohort-specific target, required path, accommodations, deadlines, and review rules where a course is assigned | Required versus optional activities, accepted evidence, prose marking authority, releases | Learner retains privacy and accessible alternatives; runtime retains scoring authority | Assignment state and learner-visible consequences are explicit without creating a hosted gradebook by accident |
| Hosted agent client | Assist discovery, alignment, drafting, explanation, and bounded revision | Proposes, invokes allowed commands, reports uncertainty; does not own acceptance or scores | Explicit roots, redaction policy, runtime projection, manifests, cancellation | Work is attributable, reviewable, bounded, resumable, and safe when connection fails |
| Local agent client | Provide similar help without network dependency | Same authority as hosted agent, with local model capability limits visible | Registered adapter, health checks, resource budget, deterministic runtime | Degrades honestly when model is absent or weak; accepted artifacts remain client-independent |

### Job conflicts that require an explicit resolver

| Conflict | Resolver |
|---|---|
| Learner wants to skip a required activity | Course rule identifies requirement and consequence; learner can leave or request accommodation, not falsify completion |
| Builder wants to rewrite a source-owned artifact | Source permission plus a reviewable write manifest |
| Agent proposes a score or key disclosure | Runtime rejects or withholds it |
| Reviewer and external editor change the same artifact | Fingerprint conflict, three-way information, and human resolution |
| Instructor wants aggregate tracking but product promises no hosted gradebook | Separate optional export or institution-owned integration, not silent telemetry |
| Source owner permits reading but not remote processing | Local-only pipeline or skip; no hosted-agent upload |

## 5. Lifecycle state coverage

This is a state model, not a screen list. Each stage includes a successful
transition plus the minimum degraded behavior implied by the product promises.

| Stage | Happy, novice, expert paths | Empty and degraded states | Recovery, undo, and proof |
|---|---|---|---|
| Install and update | One verified install; novice sample and guided checks; expert noninteractive install and diagnostics | Unsupported OS/runtime, corrupt package, no network, partial update, insufficient space | Preflight, version report, preserved data, rollback or repair instructions, uninstall that states what data remains |
| First launch | Explain local data boundary, choose or defer roots, open sample or existing course | No sources, no agent, inaccessible default path, narrow screen, assistive technology | Restartable onboarding, no forced upload/account, repeatable walkthrough, accessible help |
| Discovery | Search explicit roots, preview candidates, ignore rules, incremental expert filters | Empty root, permission denied, unavailable volume, huge tree, unsupported format, stale index | Resume scan, cancel without mutation, scope and exclusion report, reindex, diagnostic per skipped file |
| File binding | Link in place by stable identity and locator; disclose link/copy/import/move | Duplicate name, alias, symlink loop, placeholder, encoding issue, missing or changed file | Fingerprint and last-known locator, relink, conflict hold, operation manifest, undo for mutations |
| Target and objective mapping | Extract/import target, map supported objectives and prerequisites with confidence | Missing blueprint, contradictory editions, vague scope, multilingual target, open-ended field | Preserve competing claims, mark unknown, reviewer decision, versioned mapping, no false complete boundary |
| Treatment selection | Choose direct reading, excerpt, lesson, note, example, visual, practice, or test per objective | Source inadequate, rights prevent excerpt, accommodation requires alternative, no agent | Explain rationale and cost, allow review and override, preserve untreated gap, retry with another strategy |
| Authoring | Manual or agent-assisted bounded draft using semantic primitives | Offline/weak agent, context limit, unsupported media, stale source, interruption | Draft checkpoint, provenance per claim/asset, validation before acceptance, cancel, resume, discard, diff |
| Review and publication | Role-aware queue, source and rendered preview, accept/reject/request changes | No reviewer, conflicting edits, failed lint, inaccessible interaction, unresolved low confidence | Immutable accepted revision ID, reasoned decision, supersession relation, rollback, no draft leaks into formal test |
| Learn and active notes | Resume next meaningful action; accessible static fallback; learner owns notes | No prepared lesson, source missing, offline media, strategy unsuitable, locale mismatch | Substitute or defer with explanation, autosave locally, note provenance, skip semantics, restore interrupted state |
| Practice | Runtime selects and scores allowed items, returns permitted feedback | Empty eligible pool, stale item/source, pending prose, agent absent | Explain insufficiency, retain answer exactly once, pending state stays pending, resume and dedupe |
| Formal test | Frozen form and disclosure policy, deterministic scoring, accommodations fixed before start | Disconnect, crash, clock change, inaccessible item, invalidated item, external edit | Durable checkpoint, idempotent submit, incident record, authorized void/resume policy, never improvise score |
| Evidence | Separate exposure, completion, performance, confidence, recency, and unknown | Sparse sample, missing denominator, changed objective map, imported history | State denominator and provenance, recompute derived views, preserve raw events, no false mastery |
| Remediation | Explain why activity is recommended; learner or course rule controls path | No adequate artifact, repeated failure, low-confidence diagnosis, unavailable agent | Escalate to prerequisite/reviewer, stop retry loops, preserve uncertainty, allow alternate explanation form |
| Revision | Trigger from evidence or stale source; bounded proposal and impact analysis | Source revision conflicts, accepted test is in use, learner notes depend on old locator | Version, migrate references, preview semantic and assessment impact, approve, undo, retain history |
| Search | Query sources, objectives, artifacts, notes, and evidence with scope and freshness | Stale index, duplicate concepts, OCR uncertainty, missing volume, large collection | Show scope, freshness, provenance, why matched, reindex, open canonical object, never treat rank as authority |
| Export and sharing | Export chosen objects with manifest, rights, versions, and validation report | Restricted source, unsupported target, lossy conversion, missing dependency | Preflight and loss report, checksums, partial failure report, retry, import verification |
| Migration | Detect version, plan changes, preserve originals, validate after conversion | Unknown future version, interrupted migration, insufficient space, plugin missing | Transaction or journal, backup, dry run, resumable migration, rollback, human-readable report |
| Recovery | Diagnose broken course from manifest and event history | Deleted target, corrupt index, missing asset, conflicting copies, failed update | Rebuild disposable indexes, relink files, verify checksums, restore known revision, never fabricate missing content |
| Maintenance | Health check, storage report, source freshness, dependency and research refresh | Abandoned course, unavailable agent vendor, format drift, unbounded cache | Archive without lock-in, prune derived data safely, export before removal, scheduled checks remain optional and local |

## 6. Quality-attribute matrix

| Attribute | Baseline promise | Design consequence | Measurable check |
|---|---|---|---|
| Correctness and authority | One parser and one scorer; no prose auto-grade | Every surface and agent invokes runtime contracts | Mutation test proves no client-side key or score path; short stays pending |
| Accessibility | Authoring and consumption are accessible; rich interaction has useful alternative | Semantics precede visuals; keyboard, touch, screen reader, zoom, contrast, reduced motion, captions, transcripts, and alternatives are lifecycle gates | WCAG 2.2 AA audit plus human assistive-technology tasks; authored-output accessibility lint |
| Localization | Language and direction are explicit, not inferred from UI locale | Unicode, BCP 47 language metadata, bidirectional layout, locale-neutral IDs, units and notation policies | RTL, mixed-direction, CJK, diacritics, pluralization, long-string, math/code fixture suite |
| Privacy | Local files and evidence stay local unless a named operation says otherwise | Per-operation disclosure for hosted agent/export; least roots; retention and deletion controls | Network-off test; egress manifest test; delete/export inventory; sensitive-root denial test |
| Rights | Permission to read is not permission to copy, transform, or share | Rights state travels with source and derivative; unsupported rights remain unknown | Restricted-source export is blocked or redacted with reason; citation and asset license audit |
| Provenance | Accepted claims expose source, derivation, agent/human action, confidence, and revision | Entity/activity/agent-style ledger and stable locators | Trace any rendered claim to accepted artifact and source or visible synthesis label |
| Reliability | Interruption does not silently corrupt accepted state or duplicate evidence | Journals, atomic writes, idempotency, checkpoints, disposable indexes | Kill at each mutation boundary; reopen yields old or new valid state, never mixed state |
| Performance and scale | Large roots remain cancellable and incrementally useful | Streaming discovery, incremental indexing, bounded previews, budgets | Defined corpus benchmark for time to first result, cancellation latency, memory, reindex time |
| Portability | User can leave with inspectable artifacts, metadata, evidence, and loss disclosure | Plain durable source plus manifest; derived UI disposable; import/export versioning | Clean-machine round trip with checksums and semantic diff; unsupported loss is enumerated |
| Authorability | Both human and agent can create valid, accessible artifacts with actionable feedback | Schema/spec, examples, lint codes, preview, diff, validation | Representative novice and agent write-lint-fix tasks; error location and remedy accuracy |
| Observability | Failures explain object, operation, cause, consequence, and next action without leaking secrets | Structured diagnostics and support bundle with redaction | Fault injection asserts stable code, safe message, recovery action, and no source text leak |
| Maintainability | New strategies compose without new truths or scorers | Registries and semantic primitives; compatibility matrix and deprecation policy | Add one strategy without parser/scorer fork; migration fixtures for every supported version |
| Epistemic honesty | Unknown, unsupported, stale, inferred, and conflicting are distinct states | Tri-state or richer status, denominators, confidence basis, freshness | UI and exports never render unknown as zero, absent as complete, or suggestion as accepted |

## 7. Failure-mode analysis

| Failure | Unsafe default | Required containment | Owner | Verification |
|---|---|---|---|---|
| Root permission denied | Silently omit files | Name root and consequence; continue other roots; offer retry | Workspace/source service | Fixture with mixed readable and denied roots |
| Source disappears or changes | Render cached claim as current | Mark binding stale; retain last-known identity; block sensitive republish until review | Source registry | Rename, delete, and content-change tests |
| Duplicate or conflicting artifact | Pick newest/name match | Keep candidates distinct; show evidence; human resolves identity | Reconciliation service plus reviewer | Same-name, same-content, divergent-content matrix |
| Hosted agent unavailable mid-write | Retry blindly or accept partial text | Checkpoint draft; no accepted mutation without complete manifest and validation | Operation manager | Network cut at every step |
| Local agent too weak | Present confident synthesis | Capability and uncertainty disclosure; narrow task, switch, or defer | Agent adapter | Deliberately failing adapter contract tests |
| Accessibility fallback absent | Hide interaction or force inaccessible action | Block acceptance unless static/accessible equivalent or justified subject-specific exception exists | Renderer and reviewer | Automated lint plus keyboard/screen-reader review |
| Rights unknown | Assume fair use or export everything | Treat as unknown and constrain copying/sharing; ask source owner | Rights policy | Export fixtures for owned, licensed, restricted, unknown |
| Test crash | Lose response or rescore differently | Durable event, dedupe key, frozen form, explicit resume/void rule | Runtime | Crash and replay suite |
| Evidence denominator changes | Compare incompatible percentages | Version objective scope; show denominator and mapping changes | Evidence service | Objective split/merge fixtures |
| External edit during review | Overwrite collaborator | Compare expected fingerprint; stop; provide conflict context | Write-manifest executor | Concurrent-edit test |
| Migration interruption | Half-converted course | Journal, backup, restart detection, rollback | Migration service | Kill-point matrix and clean-machine restore |
| Index corruption | Declare content missing | Index is disposable; rebuild from canonical files | Search/index service | Delete/corrupt index and compare rebuilt results |
| Disk full | Truncate canonical file | Preflight where possible; atomic write; preserve old revision | Storage/operation manager | Quota fault injection |
| Help unavailable offline | Dead-end link | Ship task-level offline help and diagnostic glossary | App shell/docs | Offline novice recovery tasks |

## 8. First-principles capability classification

The classes are mutually exclusive here for prioritization, although one
capability may later have optional implementations. `Owner` names a product
responsibility, not necessarily a new module.

### Baseline

| Capability | Reason | Dependency | Likely owner | Validation method |
|---|---|---|---|---|
| Install, preflight, version, repair, safe update, and data-aware uninstall | A packaged app is unusable if setup failure is opaque or update risks local data | Packaging, migration, diagnostics | App shell | Fresh/upgrade/offline/corrupt install matrix |
| Restartable first launch with sample, existing-course, and defer paths | Novice and expert entry cannot share one forced wizard | App shell, course registry | App flow | Empty and returning-user task tests |
| Explicit read/write roots and operation-scoped permission | Discovery cannot imply mutation or remote processing authority | Source registry, manifests | Workspace security | Permission matrix and egress tests |
| Stable source/artifact identity, fingerprint, locator, freshness, and relink | Paths and names are not identity | Source registry | File lifecycle | Move, rename, duplicate, and stale tests |
| Versioned course, target, objective, artifact, and accepted revision states | Review, evidence, migration, and undo need stable referents | Course model | Course workspace | State-transition/property tests |
| Explicit unknown, conflict, stale, draft, accepted, superseded, invalid, and unavailable states | Binary present/absent lies in normal failure cases | Shared status vocabulary | Semantic contract | Exhaustive state rendering and export fixtures |
| Objective support and treatment coverage with denominators | A course needs visible gaps without false mastery | Objective map, treatment links | Curriculum service | Coverage audit with unsupported objectives |
| Treatment decision with rationale, evidence basis, and override history | Do-not-rewrite is otherwise unverifiable | Objective and artifact links | Builder/reviewer workflow | Representative objective decision review |
| Bounded draft, diff, validation, acceptance, rejection, supersession, rollback | AI and manual changes must remain reviewable and recoverable | Revisions, manifests, lint | Review workflow | Concurrent edit and rollback tests |
| Accessible authoring and learning with static fallbacks | Rich content that cannot be authored or consumed accessibly breaks the contract | Semantic blocks, renderer, lint | Renderer and authoring tools | WCAG AA plus human task audit |
| Explicit language, direction, notation, units, and locale metadata | Global text and subject notation cannot be repaired reliably at display time | Semantic contract | Content model/renderer | International fixture suite |
| Local autosave, resumable operations, cancellation, and idempotent mutation | Interruption is normal for long discovery and agent work | Operation journal | Operation manager/runtime | Kill-point and replay tests |
| Runtime-controlled practice/test authority and pending prose | Existing safety boundary must survive the course layer | Parser, scorer, projections | Runtime | Existing round trips plus course integration |
| Evidence with scope, denominator, recency, source, and uncertainty | Raw scores alone cannot support honest remediation | Event ledger, objective versions | Evidence service | Split/merge/sparse-evidence cases |
| Search across canonical object types with scope, freshness, and provenance | Large collections cannot rely on folder browsing, and rank is not authority | Disposable index, stable IDs | Search service | Relevance, stale index, duplicate, rebuild benchmarks |
| Loss-disclosing export and verified import with manifest and checksums | Local ownership requires a credible exit and recovery path | Versioned formats, rights, migration | Interchange | Clean-machine round trip and corruption test |
| Transactional migration, backup/restore, health check, and repair | Long-term local data otherwise becomes abandonment risk | Manifests, versions, diagnostics | Maintenance | Multi-version fixtures and restore drills |
| Structured, redacted diagnostics and offline contextual help | Local-first support cannot depend on telemetry or connectivity | Error taxonomy, help bundle | App shell/each subsystem | Fault injection and novice recovery study |
| Rights and provenance carried through derivative, note, assessment, and export | Citation alone does not encode permission or transformation history | Source registry, revision ledger | Provenance/rights policy | Claim trace and restricted export audit |

### Differentiators

| Capability | Reason | Dependency | Likely owner | Validation method |
|---|---|---|---|---|
| Inspectable objective-to-source-to-treatment-to-evidence trace | Makes the course director accountable rather than magical | Baseline graph and revisions | Course map | Trace task for random objective and claim |
| Evidence-triggered revision proposal with impact preview, never silent rewrite | Closes the loop while preserving reviewer authority | Evidence, diff, objective versions | Agent skill plus review workflow | Seeded misconception and stale-source scenarios |
| Client-independent agent handoff between hosted, local, and no-agent modes | Preserves useful work and local ownership across vendor availability | Operation protocol, manifests | Agent adapter | Interrupt hosted task and resume locally/manually |
| Progressive enhancement from coherent plain artifact to rich accessible lesson | Delivers visual ambition without proprietary lock-in | Semantic contract and renderer | Lesson contract | Plain-reader and rich-render semantic parity |
| Explainable recommendation of next activity with learner override | Supports autonomy and remediation without opaque adaptation | Evidence and strategy policy | Path recommender/runtime | Explanation fidelity and override persistence |
| Whole-course integrity audit spanning sources, objectives, treatments, rights, accessibility, and evidence | Converts many checks into one honest readiness view | All baseline validators | Audit service | Synthetic course with one fault in each dimension |

### Optional extensions

| Capability | Reason | Dependency | Likely owner | Validation method |
|---|---|---|---|---|
| Institution-owned cohort/LMS integration | Useful for instructors but conflicts with default no hosted gradebook if made core | Consent, export, LTI/QTI mapping | Integration adapter | Contract and privacy test against sandbox LMS |
| Multi-device synchronization | Valuable, but identity, encryption, conflicts, and economics are separate product commitments | Versioned event/revision model | Future sync service | Offline concurrent edit and recovery tests |
| Collaboration and sharing | Not required for a single learner-owned workspace | Roles, rights, conflict model | Future collaboration layer | Permission and concurrent-review matrix |
| QTI/EPUB package adapters | Standards can improve exchange, but conformance cost and semantic loss need evidence | Internal canonical contract | Interchange adapters | Validator plus round-trip loss ledger |
| Additional speech, OCR, and media providers | Useful capability adapters, not core truth | Accessible alternatives, rights, agent/provider registry | Plugin adapters | Provider-offline and equivalent-output tests |

### Subject-specific

| Capability | Reason | Dependency | Likely owner | Validation method |
|---|---|---|---|---|
| Executable code/notebook activity | Execution, sandboxing, data, and output semantics differ from reading | Portable fallback, execution policy | Subject adapter | Deterministic notebook fixtures and no-execution fallback |
| Symbolic math proof or algebra equivalence | General text scoring cannot establish mathematical equivalence | Runtime-approved scorer extension | Math adapter/runtime | Curated equivalence and counterexample corpus |
| Spatial, hotspot, lab, clinical, or performance task | Authentic response and safety requirements vary by domain | Interaction primitive and rubric | Subject/activity adapter | Domain expert rubric and accessibility alternative |
| Standardized-test blueprint fidelity | Construct and distribution are target-specific | Sourced blueprint and audit | Curriculum/audit skill | Blueprint trace and statistical distribution check |

### User-selectable strategies

| Capability | Reason | Dependency | Likely owner | Validation method |
|---|---|---|---|---|
| Direct reading, concise notes, guided lesson, or hybrid path | Treatment preference can vary when objective constraints allow | Treatment policy | Learner/course configuration | Same objective across modes with equivalent target trace |
| Optional highlighting, paraphrase, note-building, or skip | Generative activity can help or burden different learners | Note primitive and course rule | Lesson strategy registry | Usability and learning comparison, accessible alternative |
| Explanation depth and form | Analogy, worked example, visualization, or derivation suit different needs | Runtime tier grant | Learner preference plus tutor client | Tier-safe explanation selection tests |
| Pacing, density, theme, and reduced-motion preferences | Presentation preference should not fork content truth | Renderer tokens/settings | Learner settings | Cross-mode semantic parity and accessibility audit |

### Research prototypes

| Capability | Reason | Dependency | Likely owner | Validation method |
|---|---|---|---|---|
| Automated treatment recommender | Quality and explainability are not established across subjects | Objective/source features and decision ledger | Research prototype | Blind expert comparison across four subject families |
| Learner-note-informed question proposals | Notes may contain misconceptions and cannot become assessment authority | Note provenance and reviewer gate | Research prototype plus authoring skill | Adversarial incorrect-note corpus and reviewer yield |
| Open-field progress visualization | Honest denominator for a field may not exist | Scoped hierarchy semantics | Research prototype | User comprehension test with unknown/optional branches |
| Semantic legacy-upgrade assistant | Upgrades can silently alter meaning or assessment difficulty | Stable IDs, diff, validators | Upgrade skill prototype | Golden legacy corpus and semantic review |

### Reject

| Capability | Reason | Dependency | Likely owner | Validation method |
|---|---|---|---|---|
| Separate parser/scorer per surface, strategy, or plugin | Violates binding authority and creates contradictory truth | None | Architecture gate | Static dependency check and integration tests |
| Automatic prose grading presented as final | Violates runtime rule and overstates model authority | None | Runtime gate | Short response always remains pending until authorized review |
| Discovery that silently uploads, copies, moves, or rewrites | Violates source ownership and local-first privacy | None | Permission gate | Denial tests and operation manifest audit |
| Filename-based duplicate merging | Names are weak evidence and conflicts are destructive | None | Reconciliation gate | Same-name adversarial fixture |
| False field completion or mastery without defined scope and denominator | Misleads learner and cannot be validated | None | Evidence gate | Unknown scope never renders 100 percent |
| Opaque proprietary lesson as sole canonical artifact | Breaks plain-reader coherence and portability | None | Contract gate | Export and plain-reader acceptance test |
| Ship every strategy combination because users can choose | Multiplies incoherent paths and evades pedagogical validation | None | Synthesis gate | Each strategy needs evidence, owner, and finite test matrix |
| Punitive streaks, manipulative urgency, or unverifiable AI quality badges | Conflicts with honest motivation and provenance | None | Experience gate | Copy and behavior audit |

## 9. Primitive versus feature analysis

Many proposed features are views or policies over a small primitive set. The
semantic contract should name the primitive once and let surfaces compose it.

| Primitive | Composed behaviors | Do not create as separate truths |
|---|---|---|
| Stable object identity plus version and fingerprint | Relink, duplicate detection, staleness, citation, revision, rollback, deep link | Independent IDs for search, UI, export, and agent |
| Typed relation with provenance | Source support, objective alignment, prerequisite, derivation, supersession, note anchor, evidence link | Bespoke backlinks, citation stores, and graph copies |
| State vocabulary plus transition event | Draft queue, acceptance, conflict, stale badge, migration status, operation history | Screen-specific boolean flags |
| Semantic content block plus fallback | Definition hover, tip box, warning, example, diagram, prediction/reveal, caption, transcript | One file syntax per visual treatment |
| Runtime public projection and tier grant | Practice, test, tutor, review, offline quiz | Client-specific key redaction or hint logic |
| Append-only evidence event plus derived view | Progress, due state, remediation, objective report, audit | Mutable mastery percentage as source of truth |
| Operation plan/manifest plus journal | Agent write, copy/move, import/export, migration, recovery, undo | Custom confirmation and rollback flow per command |
| Root capability and rights grant | Discovery, hosted-agent use, editing, export, sharing | Global all-or-nothing permission |
| Strategy registry | Notes-first, lesson-first, hybrid, explanation form, pacing | Parallel parsers, scorers, and navigation products |
| Validator result with stable code and location | Lint, accessibility, rights, link, coverage, migration, course integrity | Prose-only errors that agents and help cannot route |
| Disposable index over canonical objects | Search, recents, recommendations, duplicate candidates | Search database as canonical course state |

**Recommendation:** synthesis should first approve this primitive vocabulary,
then map feature proposals onto it. A proposed feature that needs no new user
decision, stored state, authority, or validation likely belongs as a view or
composition. A distinct feature contract is justified only when at least one
of those four changes.

## 10. Cross-stream gap and duplication audit

Because reports 01 through 12 were unavailable at the snapshot, `Coverage`
below means the research charter explicitly assigns the topic. It does not mean
the stream supplied evidence or a usable decision.

| Derived concern | Charter owner(s) | Coverage | Gap or synthesis check |
|---|---|---|---|
| Install, repair, update rollback, uninstall, data retention | 09, 11 | Partial | First launch is named, but install and uninstall lifecycle guarantees have no explicit owner |
| Source roots, link-in-place, stale/missing/conflict/recovery | 07, 09, 11 | Strong charter | Verify stable identity, operation journal, rights grant, and performance checks appear together |
| Objective map, hierarchy, progress denominator | 02, 08, 11 | Strong charter | Verify objective version changes propagate into evidence and exports |
| Treatment selection and do-not-rewrite rationale | 02, 04, 06 | Partial | Explicit decision record, override history, cost, rights, and accommodation inputs need an owner |
| Draft/review/accept/supersede/rollback workflow | 04, 07, 09 | Partial | Reviewer actor, acceptance authority, and immutable accepted revision are not clearly assigned |
| Agent cancellation, resumption, handoff, capability failure | 04, 09, 11 | Partial | Hosted/local/no-agent continuity needs a protocol owner and kill-point tests |
| Accessible consumption and accessible authoring | 04, 10, 11 | Partial | WCAG-like UI checks are named; ATAG-like authoring support and artifact lint may be omitted |
| Localization and bidirectional authored semantics | 04, 10, 11 | Partial | Verify language/direction are canonical metadata, not a display-only concern |
| Practice/test authority and prose pending | 03, 11 plus shipped runtime | Strong boundary | Confirm every novel activity declares instructional versus scored authority |
| Evidence denominator, recency, uncertainty, objective migration | 08, 11 | Partial | Progress is named, but evidence comparability after map revision needs explicit testing |
| Search scope, freshness, provenance, and index rebuild | 07, 09, 11 | Strong charter | Ensure recommendations are views over evidence, not a second authority |
| Export/import round trip, rights, checksums, loss report | 04, 07, 11 | Partial | Standards are named, but clean-machine restore and loss disclosure need acceptance gates |
| Migration, backup, restore, diagnostics, repair | 07, 09, 11 | Strong charter | Verify transactional semantics and support bundle redaction, not only UI states |
| Long-term archival, dependency exit, agent vendor disappearance | 04, 11 | Partial | Format sustainability and client-independent handoff remain likely omissions |
| Instructor/cohort boundary | 05, 08, 11 | Weak | Instructor is not a primary actor in most charters; decide optional integration versus core scope |
| Source owner rights and remote-processing consent | 07, 11 | Partial | Rights is named, but actor-level grants by operation require synthesis |
| Offline help and novice recovery | 09, 11 | Partial | Help is named; diagnostic-code-to-help routing and offline availability need verification |

### Ideas duplicated under different names

| Names likely referring to one primitive | Unifying interpretation |
|---|---|
| Citation, source link, backlink, note anchor, claim trace, provenance | Typed relation between stable objects, with locator, derivation, and actor/activity history |
| Draft, pending, unreviewed, low confidence, provisional | Distinct states, not synonyms: workflow state, epistemic confidence, and validation status need separate axes |
| Undo, rollback, restore, revert, recovery | Operation-specific uses of versioned state plus journal; restore also needs external backup integrity |
| Mode, style, strategy, theme, output type | Separate axes: pedagogy strategy, semantic artifact kind, interaction behavior, and visual presentation |
| Completion, coverage, progress, mastery, readiness | Separate measures with declared scope and denominator |
| Import, copy, link, bind, move, migrate, sync | Distinct file operations with different ownership, identity, and undo semantics |
| Agent log, manifest, provenance, audit trail | One operation event model can feed several role-specific views |
| Empty state, error, unavailable, unsupported, unknown | Distinct product states with different next actions |

### Assumptions with insufficient evidence

| Assumption | Why unsupported | Required evidence or decision |
|---|---|---|
| More interactivity necessarily produces better learning | Interaction can add load or exclude users | Objective-specific prototype with learning and usability measures |
| Learners want one fully automatic course build | User vision permits partial AI driving, not forced automation | Observe review burden and control preferences across novice/expert flows |
| Plain Markdown alone can encode every future lesson | Current portability preference is not a proof of sufficiency | Contract stress test across math, code, media, accessibility, and round trip |
| A single objective hierarchy fits every subject | The research charter explicitly anticipates graphs and disputed boundaries | Cross-subject modeling fixtures and author review |
| Learner notes improve assessment generation | Notes may be incomplete or wrong | Incorrect-note adversarial study with reviewer gate |
| Local-first automatically means private | Hosted agent, update, media, and export operations can create egress | Network inventory and per-operation disclosure test |
| Standards support guarantees interoperability | Profiles, extensions, and loss differ | Conformance validator and bidirectional semantic loss analysis |
| Offline agent is an adequate substitute for hosted agent | Capability and resource limits vary | Adapter capability declaration and benchmarked tasks |
| Configurability resolves pedagogical disagreement | Every choice adds comprehension and maintenance cost | Finite strategy set with default, rationale, accessibility, and outcome tests |

### Capabilities with no clear owner or verification method

The following must not be accepted by synthesis until assigned:

| Capability | Missing owner | Missing verification |
|---|---|---|
| Install repair and data-aware uninstall | App packaging/maintenance | Corrupt install, update rollback, and retained-data matrix |
| Immutable accepted course revision | Course model/review workflow | Acceptance, external edit, supersession, rollback state tests |
| Hosted-to-local-to-manual agent handoff | Agent operation protocol | Cross-client interruption scenario |
| Rights grant by operation | Source/rights policy | Read versus transform versus remote process versus export matrix |
| Evidence comparability after objective revision | Evidence/objective migration | Split, merge, rename, and scope-change fixtures |
| Clean-machine course restore | Interchange/maintenance | Manifest, checksum, missing dependency, loss report drill |
| Diagnostic redaction | Shared diagnostic service | Secret and protected-source leakage audit |
| Accessible authored-output validation | Semantic contract/authoring | Automated plus human artifact audit |

## 11. Implications for product contracts and skills

### Learner flow

The learner needs one resumable loop: orient to goal and scope, take the next
justified activity, capture optional or required work, receive runtime-owned
feedback, inspect honest evidence, choose or follow remediation, and resume.
Search, notes, help, and source inspection are supporting views, not parallel
products. Every transition must state whether it changes completion, evidence,
accepted content, or nothing durable.

### Semantic content contract

The contract needs stable identity, language/direction, objective relation,
source/provenance relation, semantic block type, accessible fallback, rights,
workflow state, validation state, and version. Presentation tokens and agent
conversation do not belong in canonical content. Interaction state and learner
notes are separate learner-owned records linked to accepted content.

### Agent skills

Skills should share an operation protocol: declare roots and authority, inspect
before creating, create a plan or manifest, checkpoint, cite and label
synthesis, validate, present a bounded diff, request acceptance where required,
and report undo plus uncertainty. Separate lesson, bank, curriculum, and legacy
skills may specialize quality checks, but should not fork permission,
provenance, review, or recovery rules.

### Legacy upgrades

An upgrade needs an identity-preserving audit, explicit semantic delta, source
and assessment impact, accessible fallback, validation, approval, and rollback.
Cosmetic rewrites with no learning value should be rejected. If the old format
cannot represent a capability, retain it, link a derived enhancement, and state
the portability cost rather than silently converting it.

## 12. Adversarial scenarios

| Scenario | Expected behavior | Kill or redesign criterion |
|---|---|---|
| A 100,000-file root contains symlink loops, cloud placeholders, duplicate names, mixed encodings, and one denied directory | First useful results arrive within budget; scan is cancellable/resumable; every omission has a reason; no mutation occurs | Unbounded memory, silent omission, loop, or permission escalation |
| A copyrighted book is readable locally but remote processing and excerpts are not authorized | Local/manual treatment remains possible; hosted agent receives no content; export omits protected payload and explains links/rights | Any silent egress or unrestricted packaged copy |
| Source edition changes after a test was accepted and learners have attempts | Existing sitting remains tied to frozen revision; course marks affected mappings stale; reviewer sees impact before replacement | Silent test mutation or historical rescore |
| Learner loses connectivity during formal submit, repeats action, and restarts app | Exactly one durable response; same score; explicit resume state | Duplicate attempt, lost response, changed item/key exposure |
| Local model hallucinates a prerequisite and times out during write | Draft remains unaccepted, claim shows uncertain synthesis, timeout is resumable/discardable, canonical file unchanged | Partial accepted write or hidden origin |
| Screen-reader learner encounters drag-only diagram and forced highlighting | Equivalent operable response and note path exist; course acceptance blocks if they do not | Required inaccessible activity with no equivalent |
| Arabic lesson contains English code, inline math, and a right-to-left note | Reading order, cursor behavior, identifiers, code, math, and export remain intelligible | Data corruption, reversed tokens, or direction encoded only in CSS |
| Reviewer edits a lesson while an external editor changes the same file | Fingerprint mismatch stops overwrite; both versions and common base remain inspectable | Last-writer-wins data loss |
| Objective is split into three after six months of evidence | Raw evidence remains; derived views disclose mapping and uncertainty; no invented historical mastery | Old percentage silently assigned to all new objectives |
| Course is exported, original app removed, then restored offline on a clean machine | Canonical text, metadata, links, evidence, and manifest validate; unavailable rich features have documented fallbacks | Restore depends on account/vendor or silently drops evidence |
| Disk fills during migration | Old course remains valid or complete new version commits; journal explains recovery | Mixed-version canonical state |
| Learner notes state a misconception and agent proposes questions from them | Notes are attributed to learner, proposal is draft, key derives from accepted authority or requires review | Learner note silently becomes scoring truth |

## 13. Measurable completeness and readiness checks

### Lifecycle coverage checks

1. Every lifecycle row in Section 5 has at least one success, empty, denied,
   stale, conflict, offline, interrupted, undo, export, and diagnostic test or
   an explicit not-applicable reason.
2. Every durable mutation identifies actor, authority, inputs, expected
   fingerprints, outputs, validation, interruption behavior, and undo.
3. Every UI state maps to a canonical object/state or is visibly derived.
4. Every derived score or progress view names scope, denominator, timestamp,
   source events, and uncertainty.
5. Every agent operation succeeds, narrows, switches client, resumes, or
   safely stops when the agent is unavailable.

### Quantitative gates to calibrate before implementation

| Check | Initial gate for prototype comparison |
|---|---|
| Discovery time to first result | Report p50/p95 on small, medium, and 100,000-entry synthetic roots; no fixed claim until measured |
| Cancellation | Operation acknowledges cancellation and reaches a durable checkpoint within a defined interactive budget |
| Mutation durability | Fault injection at every write boundary yields exactly the old or new valid state |
| Search freshness | Result displays index age and stale bindings; rebuilt index reproduces canonical-object set |
| Portability | Clean-machine import recovers all supported canonical objects; every unsupported field appears in loss report |
| Accessibility | WCAG 2.2 AA automated checks, keyboard-only completion, screen-reader task review, zoom/reflow, reduced motion, and authored-output audit |
| Localization | Fixture suite includes RTL, mixed direction, CJK, combining characters, long strings, localized numbers/units, math, and code |
| Privacy | Network-disabled core loop works; captured egress equals the disclosed operation manifest |
| Provenance | Random accepted claim and asset can be traced to source or explicit synthesis and actor/activity history |
| Evidence honesty | Sparse, pending, stale, split, merged, optional, and unknown cases never display as zero or mastered |
| Help | Novice can diagnose denied root, stale source, offline agent, and interrupted migration using shipped offline help |

## 14. Completeness argument

This audit cannot prove that no capability was missed. It does provide a
finite, repeatable search procedure:

1. **Actors:** six roles cover consumption, construction, acceptance, source
   authority, assigned-course governance, and both remote and local automation.
2. **Lifecycle:** eighteen stages cover acquisition, creation, operation,
   evidence feedback, exchange, failure recovery, and retirement.
3. **Paths:** each stage was challenged with happy, novice, expert, empty,
   denied, missing/stale, conflicting, offline, accessible/localized,
   private/rights-constrained, uncertain/provenance-sensitive, large-scale,
   interrupted, undo, portable, diagnostic, and help states.
4. **Boundaries:** parser, scorer, filesystem, source owner, accepted artifact,
   learner-owned note/evidence, renderer, index, agent, and external interchange
   were treated as separate authorities.
5. **Quality attributes:** correctness, accessibility, localization, privacy,
   rights, provenance, reliability, performance, portability, authorability,
   observability, maintainability, and epistemic honesty were applied across
   the lifecycle.
6. **Closure:** every accepted capability in this report has a reason,
   dependency, likely owner, and validation method. Unowned items are called
   out rather than treated as commitments.

The Cartesian product is too large to enumerate as individual features. The
coverage tables reduce it through shared primitives and representative
adversarial scenarios. Stream 14 should run a final traceability query: every
vision statement, accepted proposal from Streams 01 through 13, lifecycle
stage, actor, boundary, and quality attribute must map to a primitive, owner,
and gate or to an explicit reject, defer, prototype, or open decision. Any
unmapped cell is a visible omission, not proof that the product is complete.

## 15. Disposition tables

### Accept

| Recommendation | Reason | Dependency | Owner | Validation |
|---|---|---|---|---|
| Adopt the baseline ledger in Section 8 as synthesis input | These are consequences of stated jobs and promises, not novelty features | Stream 14 conflict review | Synthesis | Every item maps to requirement candidate or explicit rejection |
| Approve a shared primitive vocabulary before a feature catalog | It collapses duplicated names and protects one truth | Semantic architecture decision | Synthesis/architecture | Every accepted feature maps to primitives and adds a contract only when justified |
| Make state, authority, provenance, and operation semantics visible | Most dangerous failures are hidden ambiguity | Course model and app flow | Cross-cutting | State/permission/fault matrix |
| Require owner and verification before acceptance | Unowned features become permanent gaps | Readiness audit | Synthesis/planning | No accepted row lacks both fields |
| Treat accessibility, localization, rights, portability, and recovery as lifecycle gates | Retrofitting them after rich UI is costly and incomplete | Semantic contract | All artifact owners | Cross-quality test matrix |

### Reject

| Proposal | Reason | Revisit trigger |
|---|---|---|
| Feature-count parity as completeness evidence | It ignores actors, failures, authority, and maintenance | Never as primary method |
| Treating stream charters as completed evidence | A promised report may omit or contradict its charter | Completed report reviewed with source quality |
| Separate workflow products for notes, lessons, practice, and agent work | The user needs one course loop with supporting views | Only if a distinct authority and durable contract are proven |
| Standards adoption without profile and loss analysis | A standard label does not ensure faithful round trip | Passing conformance and semantic loss tests |
| Automatic conflict resolution for identity or accepted content | Evidence is insufficient for safe destructive choice | Proven deterministic identity rule with no ambiguous cases |

### Defer

| Proposal | Reason | Dependency and revisit trigger |
|---|---|---|
| Multi-device sync and collaboration | Large privacy, identity, conflict, and operating-cost commitment | Stable local event/revision model and explicit user need |
| Full instructor/cohort product | Risks accidental hosted gradebook scope | Core single-user course loop plus institution-owned integration research |
| Broad QTI/EPUB conformance | Useful but potentially expensive and lossy | Internal contract stabilized and target interchange demand measured |
| Automatic archival scheduling | Maintenance benefit is secondary to explicit, reliable backup/export | Restore drills and retention policy |

### Prototype

| Prototype | Question | Success signal | Kill signal |
|---|---|---|---|
| Four-subject treatment recommender | Can it recommend reading, lesson, note, example, or practice with useful rationale? | Expert agreement and faster review without lower quality | Generic lesson bias, unexplained choice, or rights/accessibility neglect |
| Cross-client interrupted operation | Can hosted, local, and manual modes share one safe checkpoint? | No canonical corruption and understandable continuation | Client-specific hidden state |
| Portable rich lesson stress corpus | Can one semantic source support plain, rich, accessible, localized, and export views? | Meaning and provenance survive every view | Frequent escape hatches or inaccessible fallbacks |
| Objective revision with historical evidence | Can honest progress survive split/merge/scope changes? | Users understand what carried forward and what became unknown | Silent remapping or misleading continuity |
| Clean-machine course evacuation and restore | Can the user leave and return without vendor service? | Verified manifest and explicit loss report offline | Account dependency or silent loss |

### Open questions

| Question | Decision owner | Evidence needed |
|---|---|---|
| What is the smallest canonical course package beyond linked in-place files? | Semantic architecture and source owner | Stress corpus, restore prototype, rights review |
| Which review decisions may a solo builder self-accept, and which require another reviewer? | Product policy | Risk tiers by artifact and assessment use |
| Which instructor jobs belong in core versus optional integrations? | Product owner | Concrete learner/instructor scenarios without hosted telemetry |
| What performance corpus represents real large collections? | Search/file lifecycle owner | Anonymized structural statistics or synthetic benchmark rationale |
| What is the minimum offline help and diagnostic bundle for a packaged release? | App shell/support | Novice recovery study |
| Which interchange targets deserve bidirectional support? | Product owner/interchange | User demand, conformance cost, and semantic loss results |
| How are rights declarations represented when the user genuinely does not know? | Rights policy/source owner | Legal/product policy review; default must remain unknown, not permissive |
| Which active-note strategies improve outcomes for which objectives and learners? | Learning research | Accessible controlled prototypes across subjects |

## 16. Concrete recommendations and risks for Stream 14

1. Reconcile this ledger against the actual completed Streams 01 through 12,
   replacing charter-only coverage with cited report findings.
2. Build one object and authority model before selecting screens or feature
   names. At minimum name course, target, objective, source, artifact, accepted
   revision, learner note, activity, assessment form, evidence event, strategy,
   agent operation, rights grant, and disposable index.
3. Specify the transition table for draft, validation, acceptance, staleness,
   conflict, supersession, migration, and recovery. A visually polished flow
   cannot compensate for ambiguous durable state.
4. Promote only capabilities with an owner and verification gate. Route
   uncertain pedagogy to prototypes and institution-scale work to extensions.
5. Preserve the shipped one-parser, one-scorer, local-evidence boundaries.
   Extend them through projections and relations rather than replacement.
6. Make export plus clean-machine restore, not export button presence, the
   portability criterion.
7. Make interruption tests, stale-source tests, rights tests, accessible
   authored-output tests, and objective-revision evidence tests Phase 16
   contract gates before Phase 17 visual implementation.

The principal risk is not missing another attractive widget. It is building a
rich interface over ambiguous identity, authority, accepted state, provenance,
and recovery. The second risk is overcorrecting with a universal framework so
large that nobody can author or understand it. Shared primitives, finite
strategies, plain artifacts, actionable validation, and explicit deferred
extensions are the balancing constraints.
