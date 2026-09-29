# Source-linked feature inventory and absorption plan

Date: 2026-09-27. Status: proposed research and implementation sequence. This plan does not accept a feature, change the product contract, or authorize a code import.

## Aim and scope

Use one feature inventory to connect findings from the current and later audits. For each useful capability, compare the original project, its strongest relevant forks or independent implementations, and itembank's current behavior. Prefer studying the pinned implementation directly. Reuse source code only when its license, dependencies, architecture, and maintenance cost make that the best route. Otherwise implement the learner behavior through itembank's existing contracts.

The first sources are the [OpenMAIC inventory](OPENMAIC-GAP-INVENTORY-2026-09-27.md), [OpenMAIC fork features](openmaic-forks-2026-09-27/FEATURES.md), [OpenTutor inventory](opentutor-2026-09-27/GAP-INVENTORY.md), [LearnHouse inventory](LEARNHOUSE-GAP-INVENTORY-2026-09-27.md), [LiaScript inventory](liascript-gap-inventory-2026-09-27.md), and [Open Notebook integration research](open-notebook-2026-09-27/INTEGRATION.md). Also reconcile the older [feature atlas](phase-16/06-feature-style-atlas.md), [opportunity audit](2026-09-06-feature-opportunity-audit.md), and relevant UI, source acquisition, assessment, and course audits. Later audits use the same entry protocol.

## One inventory, with source records

Create `.planning/FEATURE-INVENTORY.md` as the human-readable index and a small structured companion only if cross-link validation needs it. Give each capability a stable `CAP-` ID. Keep the original audit ID, such as `FF16` or `S12`, in a source-reference field. Do not copy an entire audit table into the index or lose the audit's detailed evidence. Multiple source implementations and audit findings may point to one capability. A single source may support several capabilities.

Each inventory entry must record:

| Field | Required meaning |
| --- | --- |
| Capability and learner job | The observable task and why it matters, stated independently of any donor UI. |
| Source references | Exact audit IDs, repository URLs, pinned revisions, source paths or lines, and date checked. Keep upstream, fork, and independent implementations distinct. |
| Variant assessment | What each implementation actually does, evidence tier, known defects, upstream overlap, and why one variant is strongest for this job. Stars and commit counts are discovery signals, not quality scores. |
| Itembank baseline | Current code or installed-flow evidence, planned work, and whether the gap is behavior, entry point, integration, accessibility, or proof. Mark source-only and human-untested states explicitly. |
| Fit and route | Benefit, costs, rights and license, dependencies, privacy and egress, offline and fallback behavior, and the smallest useful route: reuse current code, link, adapt code, independent implementation, prototype, or retain for later. |
| Decision and trace | Disposition, owner, relevant vision and contract or requirement link, phase or seed, next evidence gate, revisit trigger, and eventual verification or rejection record. |

The inventory is an index of decisions and evidence. The detailed audit remains the source record. An unresolved row stays visible with `unknown` evidence or a research disposition. Delivery status and durable idea disposition are separate fields.

## Audit and fork method

1. **Define the job first.** State the learner or author task and comparison criteria before reading an old recommendation. Include fit, accessibility, source fidelity, reliability, recovery, maintainability, and cost. Compare the existing choice again when a better alternative is plausible.
2. **Find implementations.** For each candidate, inspect the original repository, current upstream, meaningful public forks, and relevant independent projects. Use repository trees, compare views, issues, tests, release notes, and licenses as leads. Pin every cited revision. Record the search window and limits, including private or deleted forks and unsearched branches. Review existing audits before repeating a census.
3. **Check the feature path.** Open the implementation and its call sites, tests, assets, and user entry point. Distinguish source code, reachable UI, packaged behavior, and a successful learner trial. Check whether the change has merged upstream, was removed, or is dormant. Keep contrary evidence and failure reports attached to the candidate.
4. **Compare variants against itembank.** Map the behavior to its existing parser, runtime, source, course, or surface owner. Test the smallest representative task on a synthetic course where source inspection cannot establish behavior. Judge variants on the job and evidence, not on closeness to the donor architecture.
5. **Link and route.** Give the capability one `CAP-` row and link all source and audit IDs to it. Record one recommended next test or slice, a disposition, and the evidence that would change the recommendation. Do not silently turn an audit finding into a requirement.

An audit is complete for this purpose when every substantive finding has a `CAP-` link or an explicit reason it is reference-only, duplicate, unsupported, or outside the feature inventory. A fork census is complete only for its stated search window and branch scope.

## Direct source absorption path

For a selected capability, first build a source packet: pinned commit and files, license and attribution duties, transitive dependencies, relevant tests, assets, active maintenance state, and a map from donor behavior to itembank's durable objects and surface. A permissive license alone does not make copied code a good fit. Separate code, design pattern, content, and learner data rights.

Choose the smallest route that passes the comparison:

- **Use existing itembank behavior** when the gap is discoverability or integration. Link the current owner and add only the missing path.
- **Adapt donor source** when a bounded, licensed component can retain attribution, fit the local package, and use itembank's authority and recovery contracts. Record the imported files, exact donor revision, local changes, update method, and replacement or removal path.
- **Reimplement a behavior** when the donor code brings a second scorer, remote storage authority, incompatible framework, unclear rights, or disproportionate dependency burden. Cite the pattern and test its behavior without copying protected code or assets.
- **Prototype or defer** when learner value, accessibility, licensing, or runtime behavior is still uncertain. Keep the source links and revisit trigger in the inventory.

Every production slice needs a reviewable diff, a synthetic end-to-end task, focused deterministic checks, source and rights validation, accessible and plain-file fallback where relevant, and a recovery check. Any assessment path must keep `runtime.py` as the scoring and disclosure authority. Any source or learner artifact write must use the current operation protocol, expected fingerprint, validation, and journal. A donor's hosted storage or model call does not grant remote egress for itembank data. A full fork remains an option only when a bounded component or companion service cannot meet the task and its update and data boundaries are explicit.

## Execution sequence and gates

1. **Build the register.** Create `FEATURE-INVENTORY.md`, import stable links to all current audit rows, and cross-link duplicates. Preserve the original rows and avoid bulk new dispositions in the idea ledger. Gate: every sampled audit row resolves to one capability, a documented duplicate, or a reference-only reason; broken links and orphan IDs are reported.
2. **Review variants.** Start with the OpenMAIC fork rows, since they already have pinned code links. Then inspect strong fork or independent variants for the highest-value rows in the other inventories. Gate: each proposed "best" variant has direct source evidence, a current upstream check, a fit comparison, and explicit unknowns.
3. **Rank at most five slices.** Choose by learner value, dependency order, evidence, and cost. Route each to an existing requirement or phase, a new seed, or a bounded prototype. Gate: the inventory names an owner and acceptance task without changing binding scope by implication.
4. **Implement one slice at a time.** Prepare the source packet, choose adapt or reimplement, make the smallest reviewable change, and run the relevant gates. Record exact donor provenance and local changes when code is imported. Gate: the feature works through itembank's own user path and survives the stated recovery and authority checks.
5. **Maintain the links.** On later audits and upstream updates, amend the existing `CAP-` row, preserve past decisions, and mark changed evidence stale. Gate: the inventory shows what shipped, what was only researched, what was rejected with a reconsideration condition, and what needs another trial.

The first pass is planning and evidence reconciliation. No feature should be described as shipped from an inventory row, a commit subject, or a passing source test alone.


## Parallel adoption programme, added 2026-09-28

Authority: [the current request](../USER-VISION.md#2026-09-28-parallel-selective-competitor-absorption), the September 8 direct-lesson preference, and the September 27 comparisons. This extends the sequence above with parallel research and bounded prototypes. It is a plan, not a claim that all competitors have been refreshed or all gaps verified.

Interpret "everything" as complete consideration and traceable routing of prior findings. It does not mean installing every platform or implementing every feature. Organize implementation around learner jobs and shared capabilities, not a separate subsystem per competitor. The integrator owns this plan and the future FEATURE-INVENTORY index. Existing audits remain evidence owners. IDEA-LEDGER remains the disposition owner.

### D1. Select capabilities without inheriting the whole product

| Family | Proposed treatment | Reason, retained alternative, and revisit condition |
| --- | --- | --- |
| Named AI personas, avatar teachers, simulated classmates, roundtables, conversational staging | Backburner outside the default adoption wave | The user's direct-lesson preference already excludes these from the default experience. They add orchestration, media, latency, and maintenance without a demonstrated task benefit here. Retain contextual help and direct manipulation. Revisit only for a named objective with a comparative trial. |
| Contextual tutoring, cited explanations, lesson generation, bounded editing, critique and remediation | Retain existing Core or Registered routes, verify each gap | These serve the course-building and learning loops. Persona removal must not remove useful AI. Keep source scope, accepted revisions, and runtime-issued disclosure. |
| TTS, captions, playback controls, pronunciation, oral practice, scenario role-play | Preserve existing routes, Prototype any new treatment | Accessibility audio and language or interview practice have different jobs from decorative speakers. A new treatment needs an objective, accessible alternative, offline behavior, and measured task outcome. No blanket audio or conversation ban. |
| Social feeds, public rankings, engagement rewards, simulated community | Backburner | Retain useful due review and personal progress. Revisit social features for a concrete cohort need and incentives that do not misrepresent learning. Cosmetic XP never substitutes for evidence. |
| Course stores, billing, subscriptions sold by itembank, tenants, SSO, institutional dashboards, certificates | Backburner, with deployment changes Deferred | They require a creator or institution scope decision plus identity, support, privacy, and recovery design. Provider cost controls remain useful now. Existing provider subscriptions are a separate integration question. |
| Automatic whole-course rewrites, autonomous graph changes, opaque mastery, hosted canonical grades | Do not inherit as default behavior | Preserve bounded drafts, explainable recommendations, reviewed graph revisions, and local runtime authority. These are mechanism-level constraints, not a rejection of generation or adaptation. Changes to authority require their own decision. |
| Full external editors, companion services, executable embeds, collaboration and synchronization | Case-by-case Prototype or Deferred under existing owners | Compare native pattern adoption, a bounded component, and a companion before a fork. Require a real interoperability task, ownership, failure recovery, and code/content/license checks. |

These are proposed routing rules under IL-20260928-01, not new hard rejections or declarations that every retained feature is missing. Keep each existing feature-level disposition until its evidence is reconciled.

### D2. Cover the prior landscape and its forks

| Source family | Existing evidence to reconcile | Primary lane |
| --- | --- | --- |
| OpenTutor, OpenMAIC, LearnHouse, LiaScript, Open Notebook | September 27 inventories and all five fork report directories linked below | L1-L5 by capability |
| DeepTutor, NotebookLM, the combined twenty-candidate shortlist | [September 18 competitor review](overhaul-2026-09-18/COMPETITORS.md), [September 8 landscape](competition-2026-09-08/LANDSCAPE.md), hands-on and reuse reports in that directory | L2, with L1/L3 consumers |
| Canvas, Moodle, Open edX, Kolibri, Navigate2, Pressbooks, eXeLearning, Lumi | [LMS flows](overhaul-2026-09-18/LMS-FLOWS.md), [open-source absorption](2026-09-05-open-source-absorption.md), [Navigate2](2026-08-26-navigate2-teardown.md), [learning landscape](phase-16/05-learning-program-landscape.md) | L1/L3 |
| H5P, Runestone, Jupyter, PhET, Desmos, Mathigon/Polypad, Excalidraw | Learning landscape plus [interactive teaching](overhaul-2026-09-18/INTERACTIVE-TEACHING.md) and [question references](question-types-2026-09-25/03-reference-patterns.md) | L4 |
| Anki/AnKing, FSRS, RemNote, Quizlet, Khan Academy/Khanmigo, Duolingo, WaniKani, jpdb, Bunpro, Clozemaster | Learning landscape, [widening survey](2026-08-09-landscape-widening.md), and existing Study implementation evidence | L5 |
| UWorld, AMBOSS, Sketchy, Pocket Prep, Limmer, MedicTests, Math Academy, ALEKS, DreamBox, Smartick | Widening survey and assessment audits | L5 |
| PrairieLearn, Exercism, CodeCrafters, LeetCode/NeetCode, SQLZoo, Regex Crossword, Code.org, code_learner, Manware toolkit | Open-source absorption, [Manware comparison](MANWARE-TOOLKIT-COMPARISON-2026-09-08.md), code-depth and question-type audits | L4/L5 |
| Docling, MinerU, Marker, Unstructured, Synapse/seer | Competitor review and [Synapse/seer source review](synapse-seer-primary-source-review-2026-09-09.md) | L2 |
| Obsidian and its SR plugins, Logseq, SiYuan, Anytype, Notion, Ellipsus, iA Writer, Typora, Scrivener, Google Docs, Bear, GitBook, Zed, Warp | [Editor/reader landscape](phase-16/16-editor-reader-landscape.md), widening survey, editor research | L1/L3 |
| Linear, Apple guidance, explorable explanations, Ciechanowski, other visual and interaction references | [Craft synthesis](ui-craft-2026-09-25/SYNTHESIS.md), its three source reports, UI renewal and Phase 16 visual research | L1/L4 |

This is a seed roster, not an exhaustive census. Wave 0 walks all research Markdown and the research brief, follows their local research links, and records every named product, fork, tool, standard, and substantive finding. Libraries, papers, design references, and direct competitors get separate kinds. References such as QTI, SCORM, Common Cartridge, LTI, OLX, EPUB, GIFT and H5P packaging stay visible as exchange capabilities, not competing canonical formats.

Fork inputs: [OpenMAIC census](openmaic-forks-2026-09-27/CENSUS.md) and [features](openmaic-forks-2026-09-27/FEATURES.md), [OpenTutor forks](opentutor-2026-09-27/FORKS.md) and [UI](opentutor-2026-09-27/UI-FORK-AUDIT.md), [LearnHouse features](learnhouse-forks-2026-09-27/FEATURES.md) and [UI](learnhouse-forks-2026-09-27/UI-AUDIT.md), [Open Notebook forks](open-notebook-2026-09-27/FORKS.md) and [UI](open-notebook-2026-09-27/UI-FORK-AUDIT.md). LiaScript's inventory is a separate source record. Do not invent a fork audit where none exists.

A product mention does not earn an implementation slot. Unknown or assumption-only observations, including explicitly marked older survey entries, remain unverified. Recheck primary sources only for a changed assumption or the next selected decision. Search new competitors when a named capability lacks a credible comparison, rather than starting another unlimited landscape survey.

### D3. Five independent lanes

All outputs below are future deliverables under research/absorption-2026-09-28/. One worker owns each named file. Workers read prior evidence first and never edit the shared inventory, vision, ledger, STATE, production code, or each other's reports.

| Lane and output | Bounded question and scope | Representative gate |
| --- | --- | --- |
| L1: 01-workspace-ui.md | Which workspace, navigation and microinteraction patterns help a learner start, focus, detour and return? Compare OpenTutor/LearnHouse plus LMS, reader and craft references. Include course modes, modular layouts, command navigation, search, source context, desktop density and focused phone flow. | On the same synthetic course, show normal entry to the next activity and exact return. Record desktop and phone states, focus/scroll, drafts, loading, empty, error, pending and unavailable behavior. Hiding a panel must not delete content. |
| L2: 02-sources-research.md | Which ingestion, source selection, citations, search, notes and notebook patterns improve source fidelity? Compare Open Notebook, DeepTutor, NotebookLM, extraction tools and Synapse/seer. | Repeated text resolves to the correct source occurrence. A retained note reopens its source. Excluded material stays excluded. Failed extraction or provider loss preserves readable originals and drafts. Test the existing companion before proposing its replacement. |
| L3: 03-authoring-production.md | Which outline, treatment, generation, preview, local edit, version and export patterns reduce correction effort? Compare OpenMAIC, LearnHouse, Lumi/eXeLearning, publishing and editor references. | Keep one direct reading, draft one missing lesson, correct one block, inspect citations and diff, accept, restart and restore. Cancellation or source staleness must not damage accepted work. |
| L4: 04-interactive-teaching.md | Which reusable teaching interactions add understanding? Compare LiaScript, H5P, Runestone, PhET/Desmos, code_learner and explorable explanations. Include authored emphasis, reveals, linked diagrams, prediction, worked examples, code and media. | Manipulate, observe, explain and apply one concept. Preserve a study-usable plain representation, keyboard/touch equivalents, reduced motion and meaningful provider-off behavior. Generated execution remains untrusted until its own boundary is proved. |
| L5: 05-practice-evidence.md | Which practice, review, exam, mistake-analysis and planning patterns improve the learning loop? Compare Anki/FSRS, RemNote/Quizlet, Khan, exam tools, adaptive systems and coding practice. | Wrong answer to permitted feedback to relevant teaching to a changed-context task to exact resume and later review. Separate self-rating, reading completion, pending prose, settled scores and inferred readiness. Test formal-mode withholding and interrupted submission. |

Each report returns source revision/date, original audit IDs, CAP candidates, exact itembank owner symbols, evidence class, comparison variants, current gap type, proposed route, failure condition, dependency, cost driver and next gate. Record source-only, browser-tested, packaged, installed and human-accepted evidence separately. Every substantive source finding gets a capability mapping, a documented duplicate, or an explicit reference-only reason.

### D4. Run in waves with one integrator

1. **Wave 0, integrator only:** reconcile the seed roster and all source findings into FEATURE-INVENTORY. Retain original audit IDs and fork revisions. Assign stable CAP IDs only after deduplication. Record total, mapped, unresolved and excluded-with-reason counts. Map every candidate to existing work before calling it missing. This is the next ready packet.
2. **Wave 1, up to three workers:** run L1, L2 and L3 in parallel. Root owns shared records and resolves ownership questions. No report is allowed to infer implementation status from another report's old gap label.
3. **Wave 2, up to two workers:** run L4 and L5 in parallel. Root audits Wave 1 coverage and contradictions. Synthesis waits for all five required outputs or explicitly records a missing lane as unresolved.
4. **Wave 3, integrator:** reconcile duplicate capabilities, competing variants, UI seams, data owners, rights, dependencies and costs. Rank at most five vertical slices. Retain lower-ranked ideas and revisit triggers. Produce one ready implementation packet with settled behavior and exact symbol ownership.
5. **Wave 4, delivery:** parallelize disposable prototypes or implementation only where files, runtime state and tests are independent. Use one writer for shared shell, daemon routing, parser, scorer and evidence changes. Integrate one verified slice at a time, then exercise the connected course journey. Never launch two full suites against the same state.

The planning request does not launch these waves. Future workers are not alone in the checkout and must preserve concurrent changes. Use separate managed worktrees for implementation when needed, after checking existing attached worktrees. Do not commit or push without user authorization. If authorized, commit each plan separately after its own gate and stage only owned files.

### D5. Selection, first slice and finish criteria

Rank task value and current failure severity first, then dependency readiness and evidence quality, then source fidelity, usability/accessibility, implementation cost and ongoing maintenance. Do not use an invented numeric score or a star-count ranking. A new dependency is a cost to evaluate, not an automatic veto.

The initial shortlist is provisional: contextual course workspace and exact resume, source research with retained notes, bounded authoring and revision, one interactive teaching treatment, and evidence-linked practice/review. Reorder after the inventory identifies which are already implemented or awaiting acceptance. Do not rebuild a shipped capability to satisfy an old audit.

For UI adoption, compare task structure, typography, reading width, density, alignment, content hierarchy, focus, selection, feedback, keyboard controls, responsive composition and all recovery states. A donor palette or dashboard screenshot is insufficient. Cross-lane components must use the shared shell and semantic owners. Desktop and phone may compose them differently while keeping the same meaning.

Use the same synthetic source and course across lanes, with duplicate passages, a table or equation, a private note, an unaccepted draft, a missing asset, pending prose and a restricted-feedback sitting. Measure task completion, wrong-source errors, correction work, lost state, generation cost and latency where available. Keep aesthetic preference and learning-transfer evidence separate. Do not expose real collected homework or active learner sessions for comparison.

Before code reuse, pin source and dependency revisions and inspect the exact licenses and attribution. Choose existing-native behavior, independent implementation, bounded licensed adaptation, companion integration or prototype explicitly. A proprietary product can inform a workflow comparison without licensing its code, assets or content for reuse.

A delivery passes only when the ordinary app entry reaches the capability, representative failure and resume checks pass, relevant deterministic tests and required preflight pass, and its source/packaged/installed status is reported accurately. Human visual and accessibility checks remain separate gates. Each packet names its recovery action and any migration or export loss.

### Evidence and current-state limits

This pass read the current STATE front matter, relevant source-to-course and vision sections, the existing absorption plan, and bounded sections/tables of the research above. It did not reread every research document or inspect production modules in full. The all-findings coverage audit belongs to Wave 0.

On September 28, a primary README refresh confirmed OpenMAIC's documented course workbench and durable sessions, OpenTutor's block-based learning workspace, and LearnHouse's learning-platform scope. These are documentation observations, not new runtime trials: [OpenMAIC](https://github.com/THU-MAIC/OpenMAIC), [OpenTutor](https://github.com/zijinz456/OpenTutor), [LearnHouse](https://github.com/learnhouse/learnhouse). Re-pin code before adoption.

The checkout already contains unrelated in-progress edits, September 27 inventories, and an Open Notebook companion candidate. STATE also records remaining installed/human acceptance. This plan does not close those gates, replace their owners, or claim the companion's live service was verified.

Planning recovery: retain before images and hashes in the local operation record. Undo only this dated section and its matching vision/inbox/ledger additions after checking for later edits. Do not reset shared files. No production behavior, schemas, scoring, learner data, commits, or installations are changed by this planning pass.


### Question implementation scope, saved 2026-09-28

The later [save-for-implementation direction](../USER-VISION.md#2026-09-28-save-question-and-competitor-capabilities-for-implementation) routes the complete F1-F10 discussion to the [question implementation backlog](question-types-2026-09-25/BACKLOG.md). L4/L5 consume that owner for response forms, checking, branching/video activities, executable Parsons, structured sketches, simulations and related review workflows. Preserve existing source behavior and candidate evidence limits. This capture does not start a worker wave or change the active acceptance gate.
