# Competitor workflows and bounded absorption

Research and access date: 2026-09-18. Owner: competitor research lane.
Status: proposals for integration synthesis, not accepted implementation.

## C1. Conclusion and evidence boundary

The parity target is a complete source-to-study loop: choose material, open the
relevant passage, ask a grounded question, retain a useful note, produce and
correct a lesson, practice, resume, and revisit a demonstrated weakness. A
source preview, generated scene, or scheduler in isolation does not establish
that loop. Competing products make the continuity between these jobs visible.
Itembank should measure that continuity before declaring feature parity.

This lane read the September 8 [landscape](../competition-2026-09-08/LANDSCAPE.md),
[absorption record](../competition-2026-09-08/ABSORPTION.md), and
[hands-on record](../competition-2026-09-08/HANDS-ON.md), plus the current brief,
AGENTS.md, AGENT-WORKFLOW.md, and relevant source-to-course contract sections.
The absorption record was sampled by its candidate table, capability matrix,
remaining gaps, and later reader verification. Its early statements must not
override later entries. Root owns the current Itembank implementation audit.

Evidence classes used below are D for current primary documentation, S for
current source inspection, and H for historical local observations dated
September 8. D and S were accessed September 18. No new installation, competitor
account action, runtime trial, cost measurement, learning experiment, or human
accessibility test was performed. Source inspections are deliberately narrow.
The earlier OpenMAIC outside-source additions, incomplete generation, and
DeepTutor reader-action failure remain observations, not universal defects.
Their different model settings prevent a fair speed or quality ranking.

## C2. Six direct workflow references

| Reference | Verified reference behavior and useful end-to-end benchmark | Boundary and proposed absorption |
| --- | --- | --- |
| OpenMAIC, D and H | Current documentation describes a course-building workbench with uploaded materials, editable generated pages, durable sessions, cancellation, steering, and resume. It advertises slides, quizzes, interactive scenes, and export. [Repository](https://github.com/THU-MAIC/OpenMAIC) | Benchmark production as an editable job with persistent state. Keep outline review, bounded page revisions, and recoverable interrupted generation. The historical source-fidelity failure means generation quality still needs a shared fixture. Simulated classmates and voice retain their prior optional disposition. |
| DeepTutor, D, S and H | The project documents knowledge workspaces, notebooks, reading, question generation, and versioned indexes with reindex recovery. [Repository](https://github.com/HKUDS/DeepTutor) | Benchmark passage-to-help-to-retained-note continuity. A chat success cannot close a failed reading extension. Separate extraction/index state from readable originals and make the failed action retryable without losing position. |
| OpenTutor, D and S | Documents a block workspace, generated notes and practice, wrong-answer diagnosis, study planning, and FSRS review. LOOM graph adaptation and LECTOR semantic review are explicitly experimental. [Repository](https://github.com/zijinz456/OpenTutor) | Benchmark a course page that leads naturally into practice, mistakes, and due review. Retain graph adaptation as a prototype until observable learner tasks and scheduling semantics are proved. Do not equate an experimental graph score with mastery. |
| Open Notebook, D and S | Documents multi-source notebooks, manual and generated notes, full-text/vector retrieval, transformations, selected context, citations, and provider choice. [Repository](https://github.com/lfnovo/open-notebook) | Benchmark an inspectable source workspace and repeatable transformation workflow. Adapt context selection and provenance presentation. Do not substitute a source notebook for course objectives or an assessment runtime. |
| NotebookLM, D | The requested help URLs currently redirect to Google's Gemini Notebook help. Its documented sources/chat/studio arrangement makes generated artifacts discoverable. [Notebook guide](https://support.google.com/gemininotebook/answer/16206563) | Registered UX benchmark, not a code dependency. Confirm actual account availability in a later live trial. Current docs are evidence of published behavior, not proof this user's interface contains every feature. |
| LearnHouse, D and S | Documents a course player/editor, AI assistance, collaborative editing, and operational backup/diagnosis commands. Its deployment includes database, cache, API, web, and collaboration services. [Repository](https://github.com/learnhouse/learnhouse) | Learn from course production, revision, and learner delivery even while institutional hosting remains backburner. Do not discard these relevant patterns merely because multi-user deployment is out of scope. LMS lane owns delivery details. |

NotebookLM's concrete correction and retention loops deserve explicit gates.
Its help describes source selection, citation preview, and jumping to the
quoted passage. The same page describes experimental agentic artifact editing,
including versions, and warns that these functions remain early. The older
blanket description that every possible interaction exclusively uses notebook
sources is too broad for this combined documentation. Itembank should expose
the distinction between source-bound help and optional wider research.
[Chat documentation](https://support.google.com/gemininotebook/answer/16179559)

Google documents retained flashcard progress, answer explanations, missed-card
review, retakes, and CSV download. These are a stronger baseline than merely
rendering flashcards. [Study-aid documentation](https://support.google.com/gemininotebook/answer/16958963)
Its notes documentation distinguishes authored notes from saved chat responses,
which are not editable, and offers explicit conversion into sources. Exported
Docs/Sheets changes do not synchronize back. Itembank's opportunity is an
editable learner note with retained provenance and a deliberate promotion
operation, not an invisible change of authority.
[Notes documentation](https://support.google.com/gemininotebook/answer/16262519)

## C3. Representative source inspection

These pinned files were fetched from public GitHub raw content. The first
150 lines were inspected for each, except DeepTutor's shorter complete helper.
Tree inventories were used to locate paths. None of these repositories was
installed or executed. A path's presence alone is not implementation proof.

| Pinned source | Observed code | Consequence for the proposed Itembank seam |
| --- | --- | --- |
| [OpenMAIC course edit application](https://github.com/THU-MAIC/OpenMAIC/blob/d51f4b83505e5a14f096c8bc575ee130b39a192f/lib/server/agent-runtime/course-edit/apply.ts) | Exposes element IDs, types, text, geometry, and media inventory. Supports a visible-text projection and typed edit operations. Comments distinguish agent-facing tools from the browser editor contract. | Give a draft editor stable semantic targets and a before/after preview. Do not regenerate an entire course to correct one label. This sample does not establish atomic persistence, citation validation, or conflict safety. |
| [DeepTutor grounding helper](https://github.com/HKUDS/DeepTutor/blob/897fce52f24bf22e6e50d8a3e4df532632a26322/deeptutor/reading/_grounding.py) | Collapses whitespace while retaining original positions and selects a bounded 6,000-character context. Its matching helper uses the first found occurrence. | Preserve a canonical occurrence locator alongside selection text. Duplicate quotes need explicit identity. This is a limitation of the inspected helper, not proof that all upstream callers mishandle duplicates. Prior Itembank prototype fixes should be retained. |
| [OpenTutor flashcard service](https://github.com/zijinz456/OpenTutor/blob/4f169f5ee98315ba7abb8f8e1a7914bc4e13d381/apps/api/services/spaced_repetition/flashcards.py) | Generates cards from selected or recent course content, limits assembled context, applies mode hints, and translates user ratings to updated review state. Malformed non-list output is converted into an empty list. | Show objective coverage and context truncation in draft review. Distinguish failed generation from a valid empty result. Keep self-rated review events distinct from settled assessment responses. This sample does not establish FSRS conformance. |
| [Open Notebook source-context utility](https://github.com/lfnovo/open-notebook/blob/3127f14ea9dbb519f0e4ddc64a0742ca644ba6ef/frontend/src/lib/utils/source-context.ts) | Supports full content, insights, and exclusion. Bulk defaults apply to subsequently loaded sources. Explicit full-content choice survives the arrival of insights. Notes have a separate binary context mode. | Source selection must persist across pagination and asynchronous ingestion. Show whether help uses original material, generated summaries, or learner notes. Context inclusion does not grant source authority or remote-processing rights. |
| [LearnHouse activity versioning](https://github.com/learnhouse/learnhouse/blob/01c645862451a1d48529fd88e0398176883b15bd/apps/api/src/services/courses/activities/versioning.py) | The inspected service creates a content snapshot before updates and declares a maximum of 20 activity versions. | Make revision retention and restoration visible. An Itembank accepted-revision contract needs an explicit retention policy and loss report. Do not infer whole-course restore or conflict handling from activity snapshots. |

## C4. Parity tasks and falsifiable advantages

The following are proposed product tasks, not claims about missing code.
Root must map each to the current native owner and avoid duplicate systems.
Each task uses a public-domain or synthetic fixture containing repeated text,
one table, one equation, two objectives, a deliberately unsupported claim, and
a later corrected source revision. Test the same task in selected competitors
before naming a comparative advantage.

| Task and proposed owner | Observable parity task | Failure and potential advantage |
| --- | --- | --- |
| P1. Intake and reading, source/reader owner | Register two documents, inspect extraction status and losses, assign an exact passage, read it, select the second instance of a repeated sentence, request help, and reopen that occurrence after restart. | Fail on silent extraction loss, wrong occurrence, lost position, or help grounded in stale bytes. Advantage hypothesis: zero wrong anchors across the fixture and explicit revision conflicts while keeping the original readable. Competing products must run the same test before a superiority claim. |
| P2. Retrieval and notes, source/notes owner | Restrict help to one source, inspect supporting quotes, save a learner note, edit it, search it later, reopen the source anchor, and export the note with its provenance. | Fail if excluded material enters the request, source restrictions reset with pagination, or a learner note silently becomes authoritative. Advantage hypothesis: every retained claim traces to source revision or labeled synthesis and exports without losing identity. |
| P3. Course production and correction, authoring owner | Review objectives and proposed treatments, keep one direct reading, draft only one missing lesson, inspect citations and unsupported material, revise one step, preview, accept, restart, and restore the previous accepted revision. | Fail if correction rewrites unrelated content, stale source acceptance succeeds, cancellation corrupts the accepted artifact, or a draft appears accepted. Advantage hypothesis: fewer manual corrections at equal source fidelity, plus recoverable editable Markdown. Measure corrections and elapsed active work rather than counting generated artifacts. |
| P4. Practice and revisiting, assessment/review owner | Start approved practice from the lesson, submit a wrong answer, receive permitted feedback, return to the relevant explanation, complete a changed application, reopen the result, and review due material later. | Fail if leaving loses the attempt, feedback advances before the learner chooses, prose receives an unreviewed settled mark, or a card rating changes an exam score. Advantage hypothesis: one traceable evidence history drives useful remediation without presenting inferred mastery as fact. |
| P5. Maintenance and recovery, course/package owner | Correct a source, identify affected accepted lessons and cards, review bounded updates, preserve old attempt meaning, export the course, and restore it offline in a clean location. | Fail on silent history reassignment, missing assets, stale citations presented as current, or unreported restore loss. Advantage hypothesis: a verified complete local restore and explicit stale dependencies outperform a comparator's tested task. Source inspection alone cannot establish that comparison. |

A comparative trial records setup effort, completed steps, source-locator
accuracy, unsupported claims, manual corrections, restart fidelity, model
configuration, bytes sent remotely, and measured cost when available. UI
preference and task success are separate observations. No numerical superiority
threshold is justified by this research pass. A proposed gate is zero critical
authority, data-loss, or wrong-source failures on the bounded fixture, followed
by observed user completion and a human accessibility review.

## C5. Complete candidate routing

All 20 candidates from the earlier combined shortlist remain represented.
Dispositions below are proposals or retained dispositions, not new dependency
approvals. D18 means documentation refreshed September 18. H8 means the cited
September 8 hands-on record. Prior means historical survey only in this lane.

| Candidate | Evidence | Disposition, owner, next gate or revisit trigger |
| --- | --- | --- |
| OpenMAIC | D18, S18, H8 | Prototype course production. Authoring owner runs P3 with source fidelity before reuse. |
| DeepTutor | D18, S18, H8 | Prototype reading assistance. Reader owner runs P1 with duplicate anchors and failed-model recovery. |
| OpenTutor | D18, S18 | Prototype workspace/review comparison. Course UX owner runs P2/P4 before adopting adaptation. |
| Open Notebook | D18, S18 | Prototype source workspace. Source owner runs P1/P2 and context-selection persistence. |
| NotebookLM | D18 | Registered UX benchmark. UX owner verifies P2/P4 in a live synthetic notebook. |
| LearnHouse | D18, S18 | Registered authoring/version patterns. Institutional deployment retains backburner status. Publishing owner and LMS lane separate these scopes. |
| Moodle | Prior | Registered LMS integration reference. LMS lane owns workflow refresh and consumer-specific interchange gates. |
| Open edX | Prior | Backburner institutional deployment, retained authoring/delivery reference. LMS lane owns current comparison. |
| Kolibri | Prior | Registered offline distribution reference. LMS lane owns offline-package and restore comparison. |
| LiaScript | Prior, H8 through later absorption entries | Prototype portable interaction reference. Rich-teaching lane owns current treatment and export gates. |
| H5P | Prior | Prototype content-type adapter. Rich-teaching lane owns one selected type, accessibility, export, and runtime authority. |
| [Lumi AI Editor](https://github.com/Lumieducation/Lumi-AI-Editor) | D18 | Registered drafting/export candidate. Authoring owner tests one generated worksheet through edit, H5P export, and re-open. No package trial here. |
| [eXeLearning](https://github.com/exelearning/exelearning) | D18 | Registered editable OER authoring candidate. Publishing owner tests editable project/export/reimport and reports loss. No incorporation approved. |
| [Docling](https://github.com/docling-project/docling) | D18 | Prototype extraction adapter. Source owner compares native extraction against structured document output and exact page/table/equation locators. |
| [MinerU](https://github.com/opendatalab/MinerU) | D18 | Registered extraction comparator. Source owner verifies selected code/model terms and runs the same multilingual/layout fixture when native extraction fails. |
| [Marker](https://github.com/datalab-to/marker) | D18 | Registered extraction comparator. Current repository redirects from VikParuchuri to datalab-to. Source owner checks exact code/model/service terms and local execution before benchmarking. |
| [Unstructured](https://github.com/Unstructured-IO/unstructured) | D18 | Registered partitioning comparator. Source owner measures hierarchy, provenance and locator retention, not only text yield. |
| [Anki](https://docs.ankiweb.net/exporting.html) | D18, prior native integration evidence | Registered interoperability. Review owner verifies export/import identity, scheduling/media options and explicit loss, without score transfer. |
| [FSRS](https://github.com/open-spaced-repetition/fsrs4anki) | D18, prior native partial integration evidence | Prototype upstream conformance. Review owner pins an implementation/version and replays identical review events before claiming compatibility. |
| [Excalidraw](https://github.com/excalidraw/excalidraw) | D18 | Backburner learner drawing. Notes owner revisits for a concrete construction task with editable artifact, static explanation, keyboard equivalent and export. Rich-teaching lane owns explanatory diagrams. |

Ancillary refresh is documentation-level only. It confirms the candidate's
current entry point and broad role, not extraction fidelity, installation
compatibility, H5P round trips, algorithm equivalence, or accessible drawing.
Docling's structured representation and local execution make it a useful first
comparator. They do not establish that it wins on this user's materials.
Anki's documented distinction between plain-text export and packaged decks
means that a successful TSV export cannot prove a complete media and scheduling
round trip. [Export manual](https://docs.ankiweb.net/exporting.html)

## C6. Cost, rights, maintenance, and next integration gate

No cost savings were measured. The main cost drivers are extraction models,
embedding/reindex jobs, generation retries, media creation, and engineering
maintenance of imported runtimes. A new database or collaboration service also
adds backup, migration, security, and launch work. Open Notebook's setup makes
its database and provider-key encryption explicit. LearnHouse's documented
service layout makes its operational footprint explicit. Neither fact means
these projects are unsuitable. It means a UI pattern and an app deployment
have different costs. [Open Notebook setup](https://github.com/lfnovo/open-notebook)
[LearnHouse setup](https://github.com/learnhouse/learnhouse)

Prefer native pattern adoption when a bounded interaction fits existing owners.
Use an adapter prototype for extraction, generation, scheduling or an external
activity format when an actual fixture exposes a capability gap. Reassess
whole-app adoption if a controlled end-to-end trial shows materially better
task completion with lower total ownership cost. The September 8 decision to
retain Itembank is historical context, not proof against a future alternative.

Before copying code or adding a dependency, pin the exact revision and inspect
its LICENSE, notices, dependency licenses, model-weight terms and any selected
service terms. README badges do not clear this set. The sampled LearnHouse
repository explicitly separates AGPL core and enterprise licensing. That
requires a path-specific decision, not a blanket ban on learning its workflow.
No legal compatibility determination is made here. Read, quote, transform,
remote-process, package and share grants for learner material remain separate.
Selecting a local UI with a cloud provider does not make source processing
local.

The proposed first comparison is P1 plus the note portion of P2, using one
source occurrence and one learner note. It creates reusable source identity,
selection, provenance, and resume evidence for later generation and correction
tasks. Root should either map this to an existing runnable native slice or
choose the nearest user-visible unverified transition. It should not reopen a
completed reader feature based solely on the September 8 gap labels.

Validation for this artifact is a 20-row coverage audit, primary URL access,
pinned source-path inspection, and prose/diff checks. Root owns final link and
repository preflight reconciliation. No production code, dependencies, real
course material, banks, evidence, or external accounts changed. Undo removes
this new report only. Remaining limits are current live competitor behavior,
actual Itembank gap classification, model-quality comparisons, measured cost,
human accessibility, and learning outcomes.
