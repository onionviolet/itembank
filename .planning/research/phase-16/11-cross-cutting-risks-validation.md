# Stream 11: cross-cutting risks, learner control, and validation

**Status:** research complete for synthesis review

**Access date for external sources:** 2026-08-13

## 1. Scope and research questions

This report tries to invalidate attractive Phase 16 designs before they become
contracts. It covers learner control, motivation, privacy and rights, retrieval,
localization, reliability, evaluation without telemetry, and maintenance. It
does not select a visual direction or lesson flow. It defines conditions those
directions must survive.

The governing questions are:

1. Can a learner understand and override adaptation without corrupting formal
   assessment, evidence, or keyed-content disclosure?
2. Can progress encourage useful work without presenting completion as mastery,
   punishing interruption, or exploiting social comparison?
3. Can a local-first product explain every data boundary, right, copy, derived
   asset, retention period, export, and deletion consequence?
4. Can search and recommendations remain testably useful across stale, duplicate,
   multilingual, and large collections?
5. Can files, sessions, and evidence recover from interruption, corruption,
   external edits, upgrades, storage pressure, and optional synchronization?
6. Can every semantic capability work with disability access, bidirectional
   text, notation, units, language variation, and culturally varied examples?
7. Can learning effectiveness, authoring quality, and time-to-course be measured
   locally without telemetry or false aggregate claims?
8. Can the project afford to maintain every accepted format, renderer, skill,
   asset type, migration, dependency, research claim, and help path?

### Method and evidence boundary

The local inventory used the binding product contract, planning directives,
phase index, coverage audit, shipped documentation, runtime and model contracts,
schemas, and tests. The requested reports for Streams 01 through 10 were not
present in this workspace on 2026-08-13. This report therefore audits their
assigned scopes and handoffs, not their eventual prose or recommendations. Any
claim about agreement or contradiction with a completed Stream 01 through 10
report remains an open synthesis check.

External standards and official product documentation establish current
behavior or normative requirements. Peer-reviewed reviews and meta-analyses
support learning and motivation claims, with their observational, population,
and intervention limits stated. Legal sources identify issues, not legal advice.

## 2. Sources

### 2.1 Local primary sources and shipped constraints

All local sources were accessed 2026-08-13.

| Source | Type | Use in this audit |
|---|---|---|
| [`AGENTS.md`](../../../AGENTS.md) | Repository authority | One parser and scorer, runtime assessment authority, no prose auto-grading, on-disk evidence, progressive enhancement, source identity, and audit-before-upgrade rules. |
| [`SOURCE-TO-COURSE.md`](../../SOURCE-TO-COURSE.md) | Binding product contract | Course/objective model, scoped autonomy, approved roots, citations, uncertainty, disposable indexes, plain-Markdown durability, and no sparse mastery percentages. |
| [`PLANNING-DIRECTIVES.md`](../../PLANNING-DIRECTIVES.md) | Binding planning policy | No telemetry, accessibility gates, acceptable pinned dependencies, research discipline, and separation of product decisions from findings. |
| [`README.md`](../../../README.md) | Shipped behavior documentation | Local runtime, version checking, exports, pacing override, evidence-derived retention, and compensating rather than destructive evidence events. |
| [`runtime.py`](../../../runtime.py), [`model.py`](../../../model.py) | Shipped implementation | Versioned public contracts, deterministic authority, session upgrades, accessibility descriptions, provenance parsing, and locked lint rules. |
| [`schemas/session.schema.json`](../../../schemas/session.schema.json), [`schemas/response.schema.json`](../../../schemas/response.schema.json) | Published data contracts | Versioned resumable sessions, bounded selection inputs, explicit pending states, and append-only evidence event shapes. |
| [`README.md`](README.md), [`00-coverage-audit.md`](00-coverage-audit.md) | Phase 16 routing authority | Stream ownership, required structure, cross-cutting additions, and synthesis gates. |

### 2.2 External standards, law, and official product behavior

| Source | Source type | Relevant fact |
|---|---|---|
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | W3C Recommendation | Testable accessibility requirements include keyboard operation, focus, reflow, target size, alternatives, names and roles, status messages, and accessible authentication. WCAG explicitly does not meet every disability need. Accessed 2026-08-13. |
| [EPUB Accessibility 1.1](https://www.w3.org/TR/epub-a11y-11/) | W3C Recommendation | Defines publication accessibility conformance and discoverability metadata. Accessed 2026-08-13. |
| [W3C authoring guidance for bidirectional text](https://www.w3.org/TR/i18n-html-tech-bidi/) | W3C Working Group Note | Direction belongs in semantic markup; unknown-direction text needs isolation; logical content order must be preserved. Accessed 2026-08-13. |
| [MathML Core](https://www.w3.org/TR/mathml-core/) | W3C Candidate Recommendation | Provides structured mathematical notation intended for browser rendering and processing, including accessible alternatives in conforming user agents. Accessed 2026-08-13. |
| [Unicode LDML 48.2](https://www.unicode.org/reports/tr35/) | Unicode Technical Standard | Defines locale identifiers and data for language, collation, numbers, dates, units, plural rules, and related formatting. Accessed 2026-08-13. |
| [Web Annotation Data Model](https://www.w3.org/TR/annotation-model/) | W3C Recommendation | Models bodies, targets, selectors, state, lifecycle, agents, language, direction, rights, and accessibility for portable annotations. External-resource hints are not authoritative over the resource itself. Accessed 2026-08-13. |
| [NIST Privacy Framework, getting started](https://www.nist.gov/privacy-framework/getting-started-0) | U.S. government guidance | Privacy risk concerns problems people can experience across the full data lifecycle, from collection through disposal and across processors. Accessed 2026-08-13. |
| [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj) | Primary law | Establishes principles and rights that include data minimization, storage limitation, access, erasure, and portability, subject to scope and exceptions. Accessed 2026-08-13. |
| [U.S. Copyright Office fair-use guidance](https://www.copyright.gov/fair-use/more-info.html) | U.S. government guidance | Educational purpose alone does not establish fair use; the statutory factors must be considered case by case. Accessed 2026-08-13. |
| [Creative Commons license overview](https://creativecommons.org/share-your-work/cclicenses/) | License steward guidance | CC licenses differ on attribution, adaptation, share-alike, noncommercial use, and no-derivatives. Accessed 2026-08-13. |
| [RFC 9111, HTTP Caching](https://datatracker.ietf.org/doc/html/rfc9111) | IETF Internet Standard | Defines freshness, validation, invalidation, and constrained use of stale responses. Accessed 2026-08-13. |
| [TREC 2025 retrieval-only results](https://trec.nist.gov/pubs/trec34/appendices/trec2025-rag-retrieval.html) | NIST evaluation program | Uses separate ranking and recall measures, illustrating that retrieval quality is multi-dimensional rather than one accuracy number. Accessed 2026-08-13. |
| [Electron `autoUpdater`](https://www.electronjs.org/docs/latest/api/auto-updater/) | Official product documentation | Built-in automatic updating supports macOS and Windows, requires signing on macOS, and does not provide built-in Linux support. Accessed 2026-08-13. |
| [SQLite write-ahead logging](https://www.sqlite.org/wal.html) | Official product documentation | WAL has concurrency and checkpoint behavior plus version-specific reliability concerns, so storage selection does not remove backup and recovery obligations. Accessed 2026-08-13. |

### 2.3 Learning and UX research

| Source | Source type and limits | Relevant finding |
|---|---|---|
| [Wang et al., 2024, SDT intervention review](https://doi.org/10.1016/j.lmot.2024.102015) | Systematic review and meta-analysis of 36 education interventions. Intervention designs and settings varied. | Need-supportive interventions improved intrinsic motivation, autonomy, and competence on average. This does not prove any specific app control causes achievement. Accessed 2026-08-13. |
| [Bureau et al., 2023, autonomy-support meta-analysis](https://doi.org/10.1016/j.cedpsych.2023.102235) | Meta-analysis of 179 independent samples, mostly associations rather than product experiments. | Perceived autonomy support relates positively to motivation, engagement, self-regulation, beliefs, and performance, with moderation by outcome and support source. Accessed 2026-08-13. |
| [Patall et al., 2025, autonomy support and structure](https://doi.org/10.1007/s10648-025-09994-2) | Systematic review and meta-analysis of 94 studies. Definitions and measures vary. | Autonomy support and useful structure can coexist; user control need not mean absence of guidance. Accessed 2026-08-13. |
| [Kalyuga et al., 2007, expertise reversal](https://doi.org/10.1007/s10648-007-9054-3) | Review of cognitive-load studies, with strongest evidence in structured domains. | Guidance effective for novices can become redundant or harmful for more knowledgeable learners. Accessed 2026-08-13. |
| [Kalmi et al., 2023, gamified learning strategies](https://pmc.ncbi.nlm.nih.gov/articles/PMC10448467/) | Systematic review with heterogeneous designs and generally limited long-term evidence. | Effects on motivation are mixed; leaderboards and failure states produced negative reactions in some studies, and some interventions reduced intrinsic motivation. Accessed 2026-08-13. |

## 3. Observed facts, inference, recommendation, and open questions

### 3.1 Observed facts

1. The shipped runtime, not an agent or renderer, owns scoring, mode, session
   state, and keyed-content disclosure. Prose remains pending until approved.
2. Evidence and banks stay on disk; planning forbids telemetry and a hosted
   gradebook. Derived indexes are intended to be disposable.
3. Current contracts require explicit uncertainty and denominators and reject
   sparse evidence as a mastery percentage.
4. Discovery is read-only by default. Approved roots and bounded write modes
   separate finding from permission to mutate.
5. Session and evidence contracts carry versions; the runtime upgrades known
   older sessions and rejects unknown future versions.
6. The shipped learner pacing model has daily caps and an explicit one-sitting
   override, rather than a permanent bypass.
7. Visual items require an accessibility description and tests assert semantic
   alternatives, but this does not establish accessibility of every future
   lesson capability, authoring flow, language, or assistive technology.
8. No Stream 01 through 10 output file was available in this workspace. The
   index gives each stream broad responsibilities but does not assign durable
   owners for privacy, localization, sync, evaluation operations, or long-term
   maintenance after synthesis.
9. WCAG conformance is necessary but not sufficient for all disability needs.
10. Local storage reduces external disclosure but does not by itself provide
    minimization, encryption, retention, deletion, backup, or safe sharing.
11. Educational use is not an automatic copyright exception. License terms can
    restrict adaptation, commercial use, and redistribution differently.
12. Search relevance requires more than one metric. High early precision can
    coexist with low recall, and stale or duplicate results can look plausible.
13. Desktop update behavior and costs differ by operating system, signing,
    distribution channel, and framework.

### 3.2 Inferences

1. A recommendation engine that cannot state the evidence snapshot, reasons,
   uncertainty, and override path conflicts with the existing product contract.
2. Learner autonomy is best represented as constrained choice plus transparent
   structure, not unrestricted control over assessment authority.
3. A streak is especially risky in a local-first product because device gaps,
   travel, disability, illness, and missing sync can be misread as lack of effort.
4. Course completion, content coverage, practice exposure, and demonstrated
   performance are different measures. Combining them produces false mastery.
5. Generated media and source excerpts are the highest-rights-risk artifacts
   because they can be copied into exports or shared independently of the
   provenance record that justified their use.
6. Multilingual retrieval cannot be validated by translating an English query
   suite. Tokenization, morphology, transliteration, cross-language concepts,
   script, collation, and source-language preference affect relevance.
7. Sync is not a feature-sized extension to local storage. It changes identity,
   conflict, deletion, encryption, availability, cost, and collaboration rules.
8. A semantic capability with no plain representation, accessible interaction,
   versioning policy, fixture, migration, and retirement plan is future debt,
   even if its first renderer is attractive.

### 3.3 Recommendations

1. Make adaptation advisory and inspectable. Preserve runtime authority and
   provide skip, choose another eligible activity, adjust depth or pace, and
   reset preference controls where they do not invalidate formal assessment.
2. Store preferences separately from evidence. Record their scope, source,
   timestamp, and whether they are learner-set, inferred, accommodation-driven,
   or course-required. Never infer an accommodation from performance.
3. Treat progress as a labeled vector, not one percent: scope coverage,
   completed work, settled evidence, retention state, and unknowns.
4. Reject punitive streaks, public leaderboards, loss-framed reminders, and
   reward mechanics unrelated to learning. If habit support is explored, use
   learner-chosen schedules, pause, quiet hours, grace, and neutral resumption.
5. Require an artifact rights record before generated media, excerpts, or
   transformed source content becomes accepted or exportable.
6. Make index state visible and rebuildable. Results and recommendations must
   identify source roots, index timestamp or fingerprint, exclusions, and why
   an item ranked or was recommended.
7. Keep sync and collaboration outside the Phase 16 core contract. First define
   stable identities, local conflict/recovery semantics, export bundles, and
   deletion tombstones that can later support sync safely.
8. Set WCAG 2.2 AA as a baseline verification target, then add task-based tests
   with assistive technologies, cognitive and learning accommodations, zoom,
   reduced motion, keyboard-only use, RTL, and mixed-direction notation.
9. Evaluate locally with versioned, consented study bundles and synthetic
   benchmarks. Export de-identified aggregates only by an explicit user action.
10. Put every accepted capability on a maintenance ledger with owner, version,
    dependencies, fixtures, migration rule, documentation, research-refresh
    date, and retirement trigger.

### 3.4 Open questions

1. Is the primary learner an independent adult, a student subject to instructor
   requirements, or both? Override and consent models differ.
2. Which data, if any, is sensitive enough to require application-level
   encryption, and how would key loss and recovery work?
3. Does deletion mean removal of derived indexes only, selected learner history,
   a whole course, source copies, backups, or every linked external artifact?
4. Who makes a rights determination for excerpts and generated media, and what
   jurisdictions and distribution contexts are in scope?
5. Which languages and scripts form the first supported localization matrix?
6. Is multi-device access a future first-party service, filesystem-based user
   choice, or explicit non-goal?
7. Who owns post-release accessibility testing, dependency updates, migration
   support, and research refreshes?

## 4. Pattern inventory

| Pattern | Benefit | Weakness or failure mode | Applicability to itembank |
|---|---|---|---|
| Inspectable recommendation card | Supports trust and correction through reason, evidence window, uncertainty, and alternatives. | Explanations can become post-hoc rationalizations or expose sensitive evidence. | Accept only when reasons are generated from deterministic inputs and do not leak keyed content. |
| Learner-set pace and depth | Supports autonomy and different prior knowledge. | A novice may skip prerequisites; a course requirement may limit choice. | Accept as preference within eligibility constraints, with easy reset and no score penalty. |
| Diagnostic pre-check | Can reduce redundant instruction and expose prerequisites. | A short diagnostic is noisy and can become a hidden placement exam. | Prototype with confidence bounds and a learner override; never label identity or ability. |
| Accessibility profile | Avoids repeating common adjustments. | Can expose disability information or stereotype a learner. | Store only explicit functional preferences, locally, with granular deletion. Do not infer diagnoses. |
| Calm progress vector | Separates completed work, scope, evidence, due review, and unknowns. | More complex than one percentage. | Accept. Complexity is preferable to false certainty; provide a concise summary and drill-down. |
| Flexible habit support | Learner-selected reminders, pause, grace, and resumption can aid planning. | Notifications can become coercive or leak sensitive study topics. | Prototype only after local notification privacy and opt-in tests. |
| Streak or leaderboard | Immediately legible engagement signal. | Penalizes interruption, invites gaming, social comparison, and false learning proxies. | Reject for the core product. |
| Rights manifest | Makes source, license, transformation, attribution, and export constraints reviewable. | Requires author effort and cannot decide fair use automatically. | Accept as metadata and validation, with `unknown` as a first-class blocking state for redistribution. |
| Content-addressed disposable index | Detects changed inputs and permits safe rebuilding. | Renames and moved files still need stable identity; embeddings add model/version drift. | Accept with source fingerprints, index schema/model version, rebuild and exclusion reports. |
| Hybrid lexical and semantic retrieval | Can find exact terms and conceptually related material. | Semantic ranking can hide exact misses, language bias, and inexplicable ordering. | Prototype against a fixed multilingual relevance set; retain exact filters and result reasons. |
| Automatic duplicate merge | Reduces clutter. | Same names may be distinct concepts; distinct names may be the same concept. | Reject. Propose clusters with evidence and require review for identity changes. |
| Local append-only evidence | Auditability and recovery from erroneous derived claims. | Unbounded growth and erasure tension. | Keep raw events immutable by default, but define user-visible redaction or cryptographic erasure semantics before claiming complete deletion. |
| Exportable course bundle | Portability, backup, and user control. | Can leak keys, learner evidence, copyrighted media, or absolute paths. | Prototype separate author, learner, assessment-key, and support bundles with explicit manifests. |
| Filesystem sync by user choice | Avoids building a service. | Partial files, conflicts, placeholders, case differences, and deletion propagation remain. | Defer as an unsupported boundary until conflict fixtures pass. Never imply safety merely because a folder syncs. |
| Signed in-app updates | Faster fixes and migrations. | Signing, hosting, bandwidth, rollback, and platform variance create recurring cost. | Prototype updater economics only after packaging framework and support window are chosen. Keep manual verified updates. |
| Semantic lesson capability registry | Enables portable authoring and multiple renderers. | Registry growth creates renderer, migration, accessibility, and documentation burden. | Accept only with capability budgets and retirement rules. |
| Local evaluation bundle | Preserves no-telemetry boundary while measuring outcomes. | Selection bias, small samples, and manual study operations limit inference. | Accept for formative evaluation; do not generalize beyond stated samples. |

## 5. Cross-cutting effects

### 5.1 Accessibility

Accessibility is a property of the complete task, not a field on an asset. Each
capability needs equivalent purpose, instructions, state, action, feedback, and
evidence across input and output modes. A text description of a drag task does
not provide an equivalent way to answer it. Required validation includes:

- Keyboard-only completion with visible, unobscured focus and no pointer-only
  action.
- Screen-reader names, roles, state changes, instructions, errors, and status
  messages tested in at least the supported platform combinations.
- Reflow and zoom at 400 percent, narrow viewport, high contrast, forced colors,
  reduced motion, large text, and long translated strings.
- Captions, transcripts, meaningful alternatives, and non-audio cues for media.
- A non-timed or adjustable-time route unless timing is the measured construct.
- No color, spatial position, hover, drag, sound, or animation as the sole carrier
  of meaning.
- Functional preferences such as motion, text size, modality, and response time,
  without requiring disclosure of a diagnosis.

### 5.2 Portability

Portable Markdown must carry the coherent lesson, stable objective and source
references, semantic roles, language and direction, rights metadata, and static
fallback. Renderer state, indexes, thumbnails, caches, and model embeddings are
derived. Exports need a manifest of versions, fingerprints, included and omitted
content, rights constraints, and whether assessment keys or learner evidence are
present. Absolute paths and machine-only identifiers must not be portability
contracts.

### 5.3 Privacy

Use a data inventory by category: sources, source fingerprints, annotations,
preferences, accommodation settings, agent prompts and outputs, sessions,
responses, keys, derived claims, indexes, logs, backups, exports, and optional
external-provider transfers. For each category record purpose, location, reader,
writer, retention, deletion behavior, export behavior, and sensitivity.

Local-first means no unapproved network transfer. It does not mean anonymous or
safe. Agent calls can disclose source text, learner errors, or sensitive course
topics. Before every external operation, the system needs a bounded preview of
what leaves, which provider receives it, and whether the response is retained.
Logs must not silently retain prompt bodies or keyed assessment content.

### 5.4 Provenance and rights

Every accepted artifact should identify source locators, source fingerprint,
creator type, generator and version when applicable, creation and modification
time, transformation type, license or rights status, attribution requirement,
review state, and export restrictions. `unknown` is valid for private study but
must block claims of permission and default redistribution. Rights metadata is
evidence, not a legal verdict. Source deletion or relocation must leave a
reviewable broken provenance link rather than silently laundering the derivative.

### 5.5 Authorability

Every new required field increases failure and abandonment risk. Authoring must
use progressive requirements: minimal coherent Markdown remains possible, while
acceptance or redistribution gates demand more metadata only when relevant. The
linter should identify the exact artifact, missing fact, consequence, and repair
path. It must not fabricate a license, language, accommodation, or citation.

## 6. Implications for Phase 16 contracts and Streams 01 through 10

### 6.1 Learner flow

The flow must show whether an action is required, recommended, optional, or
unavailable; why; what evidence informed it; and what safe alternatives exist.
Learners may alter pace, explanation depth, modality, reminder schedule, and
eligible next activity. They may not alter deterministic scoring, formal timing
when timing is the construct, keyed disclosure, settled evidence, or instructor
requirements without an explicit authorized path.

Resumption is a first-class state. After absence, interruption, failed agent
work, stale sources, or an app upgrade, present what changed and offer resume,
review, rebuild, or choose another task. Never use shame or lost-streak language.

### 6.2 Semantic content contract

Candidate cross-cutting fields are `language`, `text_direction`, `reading_level`
as a declared target rather than an ability claim, `units`, `rights`, `creator`,
`generator`, `source_state`, `static_fallback`, `accessibility_purpose`, and
`capability_version`. Synthesis must decide which belong in authored Markdown,
sidecar metadata, course manifests, or derived indexes. Do not put transient
renderer preferences into durable lesson meaning.

Math, code, and mixed-direction text require structured source forms and literal
round-trip tests. Unit conversion must preserve original quantity and unit,
display converted values as a view, and never silently change the value used in
an assessment key.

### 6.3 Agent skills

Skills must receive approved roots and operation mode, disclose external data
transfer, cite sources, preserve rights fields, label synthesis, and produce a
bounded manifest of reads, proposals, writes, omissions, and uncertainty. They
must not infer learner disability, silently merge identities, decide fair use,
turn engagement into mastery, or resolve sync conflicts without review.

Recommendation skills require a deterministic candidate set and evidence trace.
The model may explain or rerank only within the authorized set. Runtime authority
still governs formal assessment and disclosure.

### 6.4 Legacy upgrades

Legacy audit must detect language, direction, encoding, source status, rights,
capability version, accessibility fallback, external assets, stale generated
claims, and renderer dependencies. An upgrade may add missing metadata or an
equivalent fallback without restyling unrelated prose. Changes to facts,
assessment semantics, source identity, or rights require explicit review. Every
migration needs dry run, backup, diff, idempotence, interruption recovery, and
old-version fixtures.

### 6.5 Missing ownership and scope contradictions

Because reports 01 through 10 are unavailable, these are routing findings to be
verified at synthesis, not claims that an author omitted work.

| Streams | Potential contradiction or unowned boundary | Required synthesis resolution |
|---|---|---|
| 01, 05, 09 | Source-grounded recommendation can drift into chat-first or opaque ranking. | Name one owner for candidate generation, ranking evidence, stale-index behavior, and learner override. |
| 02, 03, 08 | Adaptive flow may confuse objective coverage, activity completion, evidence, retention, and mastery. | Define separate measures and prohibit one aggregate completion score. |
| 02, 06, 10 | Rich interactions can depend on hover, drag, motion, color, imagery, or renderer-only meaning. | Require static and accessible equivalents before accepting a capability or visual primitive. |
| 03, 09 | Learner choice can conflict with formal assessment validity and runtime authority. | Define which controls disappear or become read-only in each mode. |
| 04, 06, 07 | Portable files, generated media, in-place editing, and exports can carry incompatible rights and path assumptions. | Assign a rights manifest and export sanitizer owner. |
| 04, 07 | Stable identity and external-editor changes can conflict with automatic legacy upgrade. | Require fingerprint conflict states and prohibit unattended semantic merges. |
| 05, 06 | Broad product inspiration can become protected style imitation or asset copying. | Record transferable pattern, source, and non-copying rationale; reject voice or layout cloning. |
| 06, 10 | A visual style option can silently change instructional strategy, reading order, or emphasis. | Separate semantic role, teaching strategy, interaction, and visual tokens in the contract. |
| 07, 09 | Link-and-edit-in-place can conflict with simple undo, deletion, onboarding, and diagnostics. | Define operation previews and recovery for each storage class before promising one flow. |
| 07, 08 | Duplicate file reconciliation and duplicate concept reconciliation are different identity problems. | Assign separate artifact and concept identity models linked by reviewed mappings. |
| 08, 09, 10 | Deep hierarchy can overload navigation and falsely bound open fields. | Prototype progressive disclosure with unknown and optional scope, not universal 100 percent. |
| 09, 10 | Seamless chained flows can hide long-running work, permission changes, external calls, and failures. | Make state, authority, data boundary, cancellation, and recovery visible without modal overload. |
| 01 through 10 | No durable post-synthesis owner is named for privacy, localization, sync, evaluation operations, or maintenance. | Readiness audit must assign one accountable owner and verification gate per accepted capability. |

## 7. Adversarial scenarios, validation, and kill criteria

| ID | Adversarial scenario | Measurable validation method | Kill or redesign criterion |
|---|---|---|---|
| A1 | An expert is forced through novice explanations after a noisy diagnostic. | Counterbalanced novice/expert fixture and user test; measure unnecessary steps, completion, errors, and override discovery. | Redesign if expert median unnecessary steps exceed 2, or fewer than 90% can find the depth control without help. |
| A2 | A novice skips prerequisites and receives an impossible transfer task. | Prerequisite graph fixtures with deliberate override attempts. | Kill unrestricted skip if any path reaches an invalid formal item without warning and explicit authorization. |
| A3 | An accommodation is inferred from errors and persists as a disability label. | Inspect all preference writes and run seeded error histories. | Kill if any diagnosis or protected-class proxy is inferred, exported, or shown as fact. |
| A4 | An instructor requirement removes learner choice without explanation. | Mode matrix covering learner, instructor, and runtime authority. | Redesign if a disabled control lacks a reason and authorized appeal or alternate path. |
| A5 | Illness breaks a streak and the home screen frames the learner as failing. | Copy audit across absence lengths, timezone changes, and missing-device history. | Reject any loss counter, shame copy, paid recovery, or reset animation. |
| A6 | Course map shows 100% although evidence is sparse or objectives are unknown. | Synthetic maps with missing, optional, pending, and stale evidence. | Kill any single progress number that collapses scope coverage and mastery, or omits denominator and unknown scope. |
| A7 | A recommendation repeats weak practice because clicks are mistaken for learning. | Offline replay with high activity but poor settled evidence. | Kill ranking feature if engagement events directly increase mastery or outrank contradictory settled evidence. |
| A8 | A hosted model receives private source passages or learner errors without consent. | Network-deny integration test plus outbound payload snapshots. | Block release if an external request can occur without provider, purpose, exact data categories, and explicit authority. |
| A9 | Deleting a course leaves embeddings, thumbnails, logs, backups, or exports behind. | Seed unique canaries in every storage class; execute scoped deletion and search all managed roots. | Redesign deletion claims if any managed live copy remains undisclosed. Backups must state expiry or tombstone behavior. |
| A10 | Export includes answer keys, sensitive evidence, absolute paths, or unlicensed media. | Golden bundle tests for each export audience and rights state. | Block export if forbidden content appears or the manifest fails to enumerate omissions and rights. |
| A11 | A generated image resembles a protected source asset and has no provenance. | Rights-manifest lint plus human review queue for accepted media. | Block acceptance and redistribution when creator, source relation, generator, or rights status is unknown. |
| A12 | Search returns a stale moved lesson above the current accepted lesson. | Mutate, move, supersede, and delete indexed fixtures; query before and after rebuild. | Kill hidden indexing if stale accepted-state errors exceed 0 in the curated critical-query suite. |
| A13 | Duplicate concept names in different fields are auto-merged. | Polysemy fixture such as `normal`, `ring`, and `cell`, with distinct source/objective identities. | Reject automatic semantic identity mutation if any cross-domain false merge occurs. |
| A14 | Search works in English but fails Arabic, Chinese, accented text, or transliteration. | Human-judged multilingual suite with exact, inflected, transliterated, mixed-script, and cross-language queries. Report Recall@20, nDCG@10, first relevant rank, and no-result rate by language. | Redesign before claiming language support if any supported language has Recall@20 below 0.85 on critical queries or a gap over 0.10 versus the best-supported language without disclosure. |
| A15 | Ranking explanation cites features that did not determine the rank. | Log deterministic feature contribution or rule trace and compare displayed reason. | Kill explanation if any displayed factor is absent from the actual scoring path. |
| A16 | A 100,000-file collection freezes onboarding or grows indexes without bound. | Cold and warm benchmarks at 1k, 10k, and 100k mixed files on minimum supported hardware; measure p50/p95 query latency, peak memory, cancellation, index size, and incremental update. | Redesign if UI input blocks over 100 ms, warm p95 query exceeds 500 ms, cancellation exceeds 1 s, or index growth exceeds the documented budget without warning. |
| A17 | Power loss interrupts evidence append or migration. | Fault injection before, during, and after each durable write; validate checksums and replay. | Block release if the last acknowledged event is lost, a partial record is accepted, or recovery requires manual file editing. |
| A18 | Backup restores course files but not links, rights, evidence, or versions. | Restore onto a clean machine path and run full integrity audit. | Reject backup format if stable identity, provenance, evidence, and migration status do not round-trip. |
| A19 | Filesystem sync produces two valid divergent edits or resurrects deletion. | Two-device simulation with offline edits, clock skew, rename, case change, and delete/edit conflicts. | Keep sync unsupported if conflicts are silently last-write-wins, deletions resurrect, or assessment keys cross audience boundaries. |
| A20 | App update changes a renderer and old lessons change meaning. | Golden semantic and visual fixtures across supported old schema versions; rollback test. | Block update if scoring, reading order, static fallback, citations, or keyed meaning changes without migration review. |
| A21 | RTL prose mixed with code, formulas, and Latin citations becomes unreadable or reordered. | Native-speaker review plus screenshot and assistive-technology tests for Arabic and Hebrew mixed-direction fixtures. | Do not claim RTL support if logical copy order, cursor movement, answer entry, or spoken order is wrong in any critical task. |
| A22 | Unit localization silently converts an assessment answer or rounds a medical value. | Property tests preserving canonical value/unit and reversible display conversions. | Kill automatic conversion in scored content if canonical quantity changes or rounding exceeds a declared tolerance. |
| A23 | Reading-level simplification changes facts, nuance, or construct. | Source-cited claim diff and expert review across original and transformed versions. | Reject automatic acceptance if any supported claim, warning, exception, or assessment demand changes. |
| A24 | Cultural examples stereotype a group or assume inaccessible prior experience. | Diverse human review rubric covering relevance, stereotype, harm, prerequisite knowledge, and replaceability. | Block accepted templates with identity-essential stereotypes or examples that cannot be substituted without changing the objective. |
| A25 | A beautiful interactive lesson increases time-on-task but not transfer. | Local counterbalanced study comparing direct reading or static lesson with the rich treatment; delayed changed-context test and attrition reported. | Reject the capability as a learning requirement if it adds at least 25% median time with no practically meaningful transfer gain and no accessibility or authoring benefit. |
| A26 | AI authoring is fast but produces uncited, low-quality courses. | Blind expert rubric, lint pass rate, citation verification, learner usability, correction minutes, and time-to-accepted-course. | Redesign if median time falls but critical factual or rights errors rise, or reviewer correction time erases the gain. |
| A27 | Local evaluation reports a misleading improvement from tiny samples. | Require sample, assignment method, exclusions, missing data, interval or uncertainty, version, and raw local export. | Reject comparative claim when denominator is hidden, outcomes changed after inspection, or confidence is presented as certainty. |
| A28 | Capability and dependency growth exceeds maintenance capacity. | Quarterly ledger: owners, open defects, fixture coverage, migration count, bundle size, security age, docs freshness, and release effort. | Freeze new capabilities when any accepted capability lacks an owner or critical fixture, or when two releases miss the dependency/security support window. |

Thresholds above are prototype gates, not universal scientific constants. Change
them only before running a validation set, record the reason, and report results
by subject, language, disability task, collection size, and device class where
applicable. Averages must not hide a critical subgroup failure.

## 8. Evaluation without telemetry

### 8.1 Learning effectiveness

Use local, consented protocols with versioned course fixtures. Primary outcomes
should be delayed retention and changed-context transfer on objectives defined
before the study. Secondary outcomes can include completion, hint use, confidence
calibration, time, and abandonment, but not as substitutes for learning. Compare
against the best reasonable baseline, often direct source reading or the existing
static lesson, not no instruction. Report pending prose separately.

The app can generate a study bundle containing protocol version, randomized
assignment seed, content fingerprints, pre-specified outcomes, local events, and
an analysis script. The learner or researcher explicitly exports it. No automatic
upload is needed. Small-N within-person trials can guide prototypes but cannot
establish broad effectiveness.

### 8.2 Authoring quality and time-to-course

Measure source inventory recall, objective traceability, coverage-state accuracy,
factual and citation defects, rights completeness, accessibility completeness,
lint results, expert rubric scores, reviewer correction minutes, accepted reuse,
and elapsed time from approved roots to accepted course. Report AI generation
time and human review time separately. A faster first draft is not a faster
accepted course.

### 8.3 Search and recommendation

Maintain checked-in synthetic relevance suites and optional local private suites.
Measure exact known-item success, Recall@20, nDCG@10, first relevant rank, no-result
rate, stale-result rate, duplicate diversity, explanation fidelity, latency, and
index freshness. Report each collection and language separately. Recommendation
replay tests must include sparse, conflicting, pending, stale, and manually
overridden evidence.

### 8.4 Privacy-preserving product health

Use deterministic diagnostics, local self-tests, user-initiated support bundles,
and release test matrices. A support bundle should preview and redact paths,
source text, responses, keys, tokens, and personal metadata by default. Product
decisions may use opt-in interviews or exported studies, but absence of telemetry
must never be treated as evidence that failures do not occur.

## 9. Decision tables

### 9.1 Accept

| Decision | Reason | Owner or gate needed |
|---|---|---|
| Inspectable, overridable recommendations within runtime constraints | Aligns autonomy with deterministic authority. | Stream 08/09 contract plus runtime validation. |
| Separate preference, accommodation, evidence, and requirement records | Prevents inference from becoming fact or score. | Semantic contract and privacy inventory. |
| Multi-dimensional honest progress | Matches existing uncertainty and evidence rules. | Stream 08/09, tested with sparse and open scope. |
| Neutral resumption and learner-chosen pacing | Supports autonomy without punitive mechanics. | Learner-flow copy and accessibility tests. |
| Rights and provenance manifest with `unknown` state | Makes copying, transformation, and export reviewable. | Stream 04/07 and export gate. |
| Disposable fingerprinted indexes with visible freshness | Preserves source authority and rebuildability. | Stream 07 search owner. |
| Local evaluation bundles and synthetic benchmarks | Measures quality without telemetry. | Named evaluation owner and protocol versions. |
| WCAG 2.2 AA baseline plus task-based disability tests | Standards baseline plus real workflow coverage. | Stream 10 and release gate. |
| Capability maintenance ledger and budget | Prevents unbounded semantic and renderer debt. | Readiness audit owner. |

### 9.2 Reject

| Decision | Reason | Revisit trigger |
|---|---|---|
| Punitive streaks, public leaderboards, paid recovery, or loss-framed reminders | Engagement proxy, coercion, exclusion, and sync errors can masquerade as learning. | None for the core product; a separate consensual social product would need new research. |
| One overall mastery or course-completion percentage | Collapses scope, activity, evidence, retention, and unknowns. | None while the binding contract requires honest denominators. |
| Automatic duplicate concept or artifact merge | Identity cannot be established from similarity alone. | Only if a reversible, reviewed identity protocol proves zero critical false merges. |
| Opaque adaptation with no reason or override | Conflicts with scoped autonomy and makes errors hard to correct. | None for learner-facing recommendations. |
| Automatic accommodation or diagnosis inference | Sensitive, unreliable, and outside assessment authority. | None; accept only explicit functional preferences. |
| Automatic fair-use or license verdicts | Context-dependent legal judgment cannot be linted from metadata alone. | None; provide evidence and review workflow instead. |
| Renderer-only core meaning | Violates portable Markdown and progressive enhancement. | None under the current product contract. |
| Silent last-write-wins sync | Can lose work, resurrect deletion, and corrupt assessment boundaries. | Only after conflict and deletion adversarial gates pass. |

### 9.3 Defer

| Decision | Why defer | Revisit trigger |
|---|---|---|
| First-party cloud sync and multi-device service | Changes privacy, identity, conflict, cost, support, and deletion architecture. | Stable local identity, export, conflict, encryption, and recovery contracts plus an explicit business decision. |
| Sharing, cohorts, and live collaboration | Requires roles, consent, keys, moderation, version conflicts, and withdrawal semantics. | Separate collaboration contract and threat model. |
| Automatic cross-language semantic recommendation | Evidence and evaluation cost exceed Phase 16 core. | Human-judged multilingual suite and supported-language commitment. |
| App-level encryption | Key recovery and threat model are unresolved. | Data classification and explicit threat model identify protected classes and recovery policy. |
| Automatic reading-level transformation | High risk of factual and construct drift. | Domain-specific claim-preservation evaluation and required human review path. |
| Broad generated-media library | Rights, storage, accessibility, and maintenance costs are unclear. | Rights manifest, alt/transcript gate, storage budget, and export policy all pass. |

### 9.4 Prototype

| Prototype | Validation target | Exit criterion |
|---|---|---|
| Recommendation explanation and override card | Reason fidelity, comprehension, correction, keyed-content safety. | 100% trace fidelity in fixtures; at least 90% task success without help; no key leaks. |
| Prior-knowledge depth control | Expertise reversal, prerequisite safety, learner preference. | Meets A1 and A2 gates across at least two structured and one knowledge domain. |
| Calm progress vector | Correct interpretation of coverage, evidence, retention, and unknowns. | At least 90% of representative users answer interpretation tasks correctly; no false mastery language. |
| Rights-aware artifact and export manifest | Private use, unknown rights, attribution, no-derivatives, and key/evidence separation. | All golden bundles pass A10 and A11. |
| Hybrid local retrieval | Exact, semantic, duplicate, stale, multilingual, and scale behavior. | Meets A12 through A16 on declared supported collections and languages. |
| Backup and clean-machine restore | Identity, links, evidence, rights, schemas, and migrations. | Meets A17 and A18 with documented recovery time. |
| RTL plus math/code lesson fixture | Direction, speech order, copying, answer entry, and static fallback. | Meets A21 on supported platform and assistive-technology matrix. |
| Local learning and authoring evaluation bundle | Reproducibility without automatic upload. | Independent rerun reproduces reported metrics from exported inputs. |
| Packaged updater proof | Signing, delta/full size, failure, rollback, support window, and annual cost. | Written platform matrix and affordable recurring budget before framework commitment. |

### 9.5 Open

| Open question | Why it matters | Decision owner needed |
|---|---|---|
| Supported learner roles and who can constrain overrides | Determines consent, formal requirements, and UI authority. | Product synthesis. |
| Supported languages, scripts, locales, and assistive technologies | A generic localization claim is not testable. | Phase 16/17 release matrix owner. |
| Retention and deletion semantics for append-only evidence and backups | Auditability can conflict with meaningful erasure. | Privacy and data-contract owner. |
| Rights review jurisdiction and redistribution scope | Private study, classroom sharing, and publication differ. | Product/legal policy owner. |
| Search corpus and relevance-judgment ownership | Metrics need maintained representative queries. | Retrieval evaluation owner. |
| Backup responsibility and default location | Local-first users can still lose all data. | Packaging/data owner. |
| Whether filesystem sync is supported, tolerated, or warned against | External sync behavior affects recovery promises. | Product and support owner. |
| Packaged framework, signing identities, update host, and support window | Determines security and recurring economics. | Packaging owner. |
| Research refresh cadence and claim expiry | Learning and product evidence becomes stale. | Maintenance owner. |

## 10. Concrete recommendations and residual risks

### 10.1 Required synthesis gates

Before Phase 16 accepts a lesson flow or capability, require:

1. A portable semantic form and coherent static fallback.
2. An accessible interaction and declared test matrix.
3. Authored and derived data boundaries, including language, rights, provenance,
   privacy, and retention.
4. Learner controls, authority limits, recommendation reasons, and override rules.
5. Search and index freshness behavior when the capability creates discoverable
   content.
6. Performance and storage budgets at a declared collection size.
7. Failure, cancellation, backup, restore, migration, and rollback behavior.
8. A local measurable learning or authoring hypothesis with a credible baseline.
9. An owner, fixture, documentation path, dependency policy, and retirement rule.

If any gate has no owner, the capability is a prototype or deferred item, not an
accepted contract requirement.

### 10.2 Minimum release matrices

Synthesis should define explicit matrices rather than say "accessible, local,
and multilingual":

- Learner modes: learn, practice, formal test, review, authoring, diagnostics.
- Evidence states: none, sparse, pending, settled, conflicting, stale, retracted.
- File states: local, read-only, moved, deleted, duplicate, external-edit,
  placeholder, unsupported, corrupt, removable, network unavailable.
- Language states: LTR, RTL, mixed direction, CJK, combining marks, long words,
  plural variants, localized numbers and units, math, code.
- Access states: keyboard, screen reader, zoom/reflow, high contrast, reduced
  motion, captions/transcripts, alternate response action, extended time.
- Scale states: 1k, 10k, and 100k files plus large individual source and media.
- Recovery states: crash, power loss, disk full, partial migration, bad update,
  backup restore, clock skew, and optional sync conflict.

### 10.3 Residual risks

Even if all proposed gates pass, important risks remain:

- Local study samples may not generalize to other learners, institutions, or
  high-stakes settings.
- Accessibility conformance and representative testing cannot cover every
  disability combination or assistive technology.
- Rights metadata may be incomplete or legally disputed.
- Search judgments age as collections and terminology change.
- User-managed backups and sync can fail outside the application's control.
- Platform signing, distribution, and dependency economics can change after the
  framework decision.
- Maintenance capacity is a product constraint, not merely an engineering task.

These residual risks require honest scope statements, visible uncertainty,
support diagnostics, and scheduled revalidation. They do not justify opaque
automation or a weaker evidence standard.

## 11. Synthesis handoff

Stream 12 should treat this report as an adversarial gate, then compare it with
the completed Streams 01 through 10. For every recommendation it accepts, record
which A-scenario it must survive, who owns the validation, and whether failure
kills the capability, changes its default, narrows supported scope, or returns it
to prototype. The later implementation-readiness audit must assign the recurring
maintenance work, not only initial implementation.
