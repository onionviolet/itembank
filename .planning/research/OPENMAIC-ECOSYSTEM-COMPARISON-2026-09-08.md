# OpenMAIC and the learning-product ecosystem

Date: 2026-09-08. Status: research and proposed dispositions, not an accepted migration or milestone expansion.

## Request and answer

User research lead, preserved verbatim:

> consider [https://github.com/THU-MAIC/OpenMAIC](https://github.com/THU-MAIC/OpenMAIC)
>
> does that just work better than what we have right now can we absorb what they have and more? do we fork them? copy things over? MOre to consider? how did we not find this before? look through github and more

OpenMAIC appears ahead in the breadth of implemented course generation and classroom presentation. This is a repository-based assessment, not a measured comparison of task success or learning outcomes. Its implementation deserves reuse trials. Itembank should not assume that its extensive contracts make its current learner experience better.

Proposed route: compare OpenMAIC and DeepTutor on one identical source-to-learning task, then prefer maintained packages or a bounded integration over a permanent whole-product fork. A replacement remains a legitimate option if the trial shows that adaptation costs less than completing Itembank while preserving the user's required behavior.

## Evidence scope

OpenMAIC was cloned for read-only inspection at `29735f10d0081859ac3db1a50a0cc92f46436004`. Its root package reports 1.0.1. DeepTutor was cloned at `7a96bba1ae03401644c17763a2411c28aff3dcc9`. Neither application's dependencies were installed or its live generation run. No learner material, bank, credential, or evidence was sent to either project. External requests fetched public repositories and pages only.

Itembank inputs: current STATE front matter and position, AGENT-WORKFLOW, SOURCE-TO-COURSE, relevant September 8 USER-VISION sections, Phase 16 landscape scope, and the `runtime.py:score_response` implementation. Large modules and the complete vision history were not read. Existing dirty implementation and planning files belong to concurrent work and were not edited.

Web discovery covered AI course generators, local tutors, source notebooks, interactive Markdown, document extraction, GitHub topic listings, and research papers. Related projects below received primary-document screening, except OpenMAIC's deeper symbol-level inspection and DeepTutor's reading-extension document inspection. Search results and README claims are not runtime verification. No exhaustive GitHub coverage is claimed.

## F1: Where OpenMAIC is ahead and where it differs

| Area | External evidence | Itembank comparison and implication |
|---|---|---|
| Course construction | OpenMAIC documents an agent workbench, uploaded materials, curriculum tools, editable scenes, and durable sessions | STATE still records deferred valid local-model proposals and unproved live learner legs. Treat course creation as a competitive gap until a comparable run succeeds |
| Rich teaching | Slides, interactive HTML, PBL, voice, whiteboard, and exports are documented and have implementation paths | Reuse candidates should be tested before writing more bespoke presentation machinery |
| Reusable internals | Separate DSL, generation, renderer, editor, importer, and storage packages exist | A whole-app fork is not necessary to test reuse |
| Generation boundary | `@openmaic/generation` takes a caller-supplied `AICallFn` and does not own provider configuration or persistence | Good candidate for draft generation behind Itembank's accepted-artifact boundary |
| Rendering dependency | Renderer requires React, React DOM, Motion, and Tailwind 4 | This is not a Python file copy. A renderer integration adds a JS build and dependency surface |
| Assessment | Choice grading compares keys locally. The short-answer API calls an LLM and falls back to half credit when parsing fails | Do not import this as settled assessment authority. Itembank's scorer returns pending for constructed responses |
| Recovery | Server sessions, mutation abort fences, and related tests exist | Do not dismiss OpenMAIC as a disposable demo. Exact equivalence to Itembank revision and undo requirements remains untested |
| Generated execution | The interactive host permits scripts, forms, and popups in a sandboxed iframe | Sandbox existence does not establish network isolation, accessibility, or static fallback. Validate those separately |

Primary source pointers, pinned to the inspected revision:

- [OpenMAIC release and setup documentation](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/README.md).
- [Generation package contract](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/packages/@openmaic/generation/README.md).
- [Renderer contract and peers](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/packages/@openmaic/renderer/README.md).
- [Short-answer grading and fallback](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/app/api/quiz-grade/route.ts).
- [Choice grading](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/lib/quiz/grading.ts).
- [Interactive host](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/components/scene-renderers/InteractiveIframeHost.tsx).
- [Mutation fence](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/lib/server/agent-runtime/mutation-fence.ts).

OpenMAIC's README explicitly limits its shared development persistence token to trusted single-user deployments. It says the browser-visible token does not provide user isolation. That matters if considering a hosted fork, but does not disqualify local evaluation.

## F2: Reuse choices

| Option | Proposed disposition | Cost and revisit condition |
|---|---|---|
| Run upstream as a separate comparison app | Prototype | Setup, chosen model, and one bounded generation budget. First choice for learning whether its workflow actually helps |
| Use generation package to produce drafts | Prototype | Map scene output into existing objectives and artifact review. Promote only after citations, validation, rejection, and replay work |
| Use renderer or importer as an optional client | Prototype | React/Tailwind dependency, format fidelity, offline assets, accessibility, and static representation. Promote after one representative artifact passes |
| Copy small licensed algorithms or prompt templates | Prototype | Preserve notices, pin upstream revision, track local edits, and retain focused tests. Prefer dependency reuse when the component has a maintained interface |
| Permanently fork or replace Itembank | Deferred | Requires evidence that most upstream architecture fits and migration plus ongoing merges costs less than integration. Existing effort alone is not a reason to retain Itembank |

OpenMAIC's current [MIT license](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/LICENSE) permits copying and modification subject to preserving its notice. The README records a June 28 relicensing from AGPL to MIT. Inspect the exact revision and each dependency or asset before copying. A repository license does not grant rights to arbitrary course sources, model weights, or separately licensed media.

The preferred integration would send approved source excerpts to a selected generator, receive unaccepted drafts, retain source references and generation provenance, validate through Itembank, and accept using existing revision operations. Its UI would read public assessment projections and submit responses through Itembank. An independent evaluator may offer advisory feedback but cannot settle marks. Failed generation remains failed or pending.

## F3: Broader candidates

| Candidate | Why consider it | Proposed disposition |
|---|---|---|
| [DeepTutor](https://github.com/HKUDS/DeepTutor) | Closest broader challenger in this scan: reading, course study, interactive books, question generation, memory, and agent interfaces | Prototype alongside OpenMAIC before committing to additional bespoke course and reader implementation |
| [OpenTutor](https://github.com/zijinz456/OpenTutor) | Local course workspace, notes, flashcards, quizzes, source citations, and spaced repetition | Prototype as a UX reference. Its README identifies a public beta and experimental graph/autonomous flows |
| [Open Notebook](https://github.com/lfnovo/open-notebook) | Source ingestion, bounded context selection, citations, transformations, and multi-speaker audio | Registered research candidate for source-workspace patterns and optional integration |
| [LiaScript](https://github.com/LiaScript/LiaScript) and [H5P](https://h5p.org/content-types-and-applications) | Interactive authoring and reusable learning activities beyond an AI chat interface | Registered research candidates for authored treatments. Check portability, scoring ownership, and licenses per component |
| [Docling](https://github.com/docling-project/docling) | Document conversion rather than an entire learning product | Registered extraction candidate. Trial exact page, table, and equation preservation against existing source adapters |

[LearnHouse](https://github.com/learnhouse/learnhouse) also merits a backburner disposition for institutional course publishing. Its README identifies AGPL and separately licensed enterprise features. It is less directly aligned with the current single-user desktop scope. [Lecture2Notes](https://github.com/HHousen/lecture2notes) is a backburner lecture-processing reference, not a recommended replacement without a maintenance and environment check.

DeepTutor's [reading extension contract](https://github.com/HKUDS/DeepTutor/blob/7a96bba1ae03401644c17763a2411c28aff3dcc9/READING_EXTENSIONS.md) is particularly relevant to the current reader request. It specifies server-resolved source anchors, selection verification, typed results, timeouts, and no extension-supplied raw HTML. These are useful design and reuse leads, not proof that all implementation paths meet the contract.

Research beyond repositories: [SimClass](https://arxiv.org/abs/2406.19226) reports classroom interactions in two courses. That does not prove current OpenMAIC beats individual tutoring or improves delayed retention. [DeepTutor's paper](https://arxiv.org/abs/2604.26962) includes simulated-student evaluation and reported benchmark improvements. Those percentages are not direct evidence of equivalent gains for a human Itembank learner.

## F4: Why the recorded research missed this

Verified: a case-insensitive OpenMAIC/MAIC search in the checked planning tree returned no match. Searches for OpenMAIC, OpenTutor, and DeepTutor also found no matches before this report. This establishes absence from that record, not from every prior conversation or private search.

The August 13 [source-grounded landscape](phase-16/01-source-grounded-products.md) explicitly focused on NotebookLM and a small adjacent set. It intentionally narrowed new browsing based on previously covered gaps. The broader research program asked for open-source patterns, but this sampled landscape did not establish a systematic inventory of runnable end-to-end alternatives.

Inference: pattern research and architectural fit received more attention than testing whether an existing application could already deliver the whole user job. OpenMAIC's August 27 workbench release also postdates that landscape. Timing explains missing the latest workbench, but its earlier releases mean timing does not fully explain missing the project.

Proposed correction: before a major new subsystem, search the user job with open-source and multilingual terms, inspect direct alternatives plus their related repositories and papers, and run the strongest candidate on a shared fixture. Save the query scope, version, result, and reason for build versus reuse. Refresh when entering that subsystem or when a material release changes the comparison. No recurring automation has been created.

## F5: Concrete next comparison and reconciliation

Owner: the next comparison task's coordinator. Status: proposed, not executed.

Use one public-domain or synthetic source section with two explicit objectives. Require a direct reading, one grounded explanation, one interaction, and a short practice activity. Use equivalent model settings where supported and record differences. Do not use collected homework.

Record time to the first usable activity, manual corrections, citation accuracy, objective coverage, model/tool cost, and setup effort. Then test reload/resume, offline exported content, a failed model response, and an attempted correction. Run the same learner task through Itembank, OpenMAIC, and DeepTutor. Assess retrieval or transfer with a new question rather than treating engagement or generated page count as learning.

Choose package reuse if the useful output crosses a small stable boundary. Choose a sidecar if the upstream application delivers value but has incompatible storage or UI assumptions. Reconsider a whole fork if its end-to-end experience wins and adapting the required authority, portability, and recovery behavior is cheaper. If none wins, keep the evidence and implement the smallest exposed gap.

Absorb-book, build-course, curriculum-design, author-bank, and guiding-questions remain relevant responsibilities when integrating outputs: treatment selection, objectives, validation, and tutoring disclosure do not disappear when another project generates a course. No upstream skill was installed or adopted as an instruction during this research. Stub lesson-authoring and media-intake skills are not claimed as implemented integration mechanisms.

All substantial options above retain a disposition. No permanent rejection or change to canonical formats, scoring, source rights, or milestone scope was made. The only repository mutation is this new research report. Undo is removal of this report. No commit, fork on GitHub, deployment, or product-code import was performed.
