# Comparison notes for the finite parity programme

Date: 2026-10-04. Scope: all 27 capability groups, using existing pinned
research and current native symbol windows. This report changes no production
source, shared record, learner file or comparison pin. No suite was rerun,
donor code executed, private donor root crawled, or live provider invoked.

## Evidence and source keys

The [inventory](../../../FEATURE-INVENTORY.md) maps 604 numbered findings to
27 groups with zero orphan IDs. That count includes duplicate source records
and thin fork leads. The [604-finding synthesis](../../absorption-2026-09-28/06-synthesis.md)
already consolidates repeated workspace, authoring and research suggestions.
Neither count measures unfinished features. Original ID ranges remain in the
inventory; these rows select a representative task for each group rather than
claim every donor variant is equivalent.

| Key | Exact comparison basis and evidence limit |
| --- | --- |
| M | [OpenMAIC inventory](../../OPENMAIC-GAP-INVENTORY-2026-09-27.md), THU-MAIC/OpenMAIC `f2875426ae5712d26f0a76e54e9de763e86027a6`. Source/README/changelog observation, no donor task trial. Original row IDs below select the mechanism. |
| T | [OpenTutor inventory](../../opentutor-2026-09-27/GAP-INVENTORY.md), zijinz456/OpenTutor `db15d901a7c5c5f46941487ca4ebc2cfb20425c2`. Source and demo screenshots, no installed task trial. |
| H | [LearnHouse inventory](../../LEARNHOUSE-GAP-INVENTORY-2026-09-27.md), learnhouse/learnhouse `5e28b0723176b34ba8777b9980db352268aa8234`, dev. Sampled source/API/web/test names, no donor run. |
| HF | [LearnHouse fork features](../../learnhouse-forks-2026-09-27/FEATURES.md), godarrenw/learnhouse SYSU-SAM `2c778307db98827b030345e0a98943814b7c6a3a`. LF01 course-readiness source/test observation, no reproduced donor run. |
| L | [LiaScript inventory](../../liascript-gap-inventory-2026-09-27.md), runtime `c2e37e36440f270403069e47c712bbb8ffe2d9e7`, docs `17a777dfb028c7979f2e3204090452c95a01c134`. Documented patterns, no executed demonstrations. |
| N | [Open Notebook forks](../../open-notebook-2026-09-27/FORKS.md), upstream `3127f14ea9dbb519f0e4ddc64a0742ca644ba6ef`; read-only endpoint mechanisms under `api/routers/{notebooks,notes,sources}.py`. Fork/middleware pins remain in that report. Health is connectivity, not authenticated instance identity. |
| B | [Backend comparison](../../audit-expansion-2026-09-30/BACKEND-COMPARISON.md), exact source windows/hashes in its `primary-sources.json` and `mechanism-windows.json`. No package/service/model installed. B1 Huey `ffa956f5cfd89ddd11a0cf9255e72178dd10d19f`; B2 APScheduler 3.11.0 `6c72a51416893eb0eebbe63d0f2a0151952cab59`; B3 sqlite-utils `6bc1d33d583c54bd69fbdd2071117e2d38c354a1`; B4 Docling `d6f03078ad364108df3e7e82e8f0dcc3fd7f39ea`; B5 nbformat `4346f97c9d435f41ddfe76d28758b23796fdcf5a`; B6 Joplin `9cbf49b260840d165507894185b8d5dbe28f52fc`; B7 pluggy `7aa82ed6543db40a0c44b68e933c5ae630bce6ab`; B8 py-fsrs `9446cb06605c597a063aeee49f7d188d42e34dc2`; B9 marimo `c6954f6ead3c1c869cedfbd1d4bcf40e92025fb0`. |
| P | [Platform parity](../../platform-parity-2026-10-01.md), primary documents inspected October 1: Boot.dev `/about`, Brilliant Help interactives, Khan Help mastery levels, Exercism homepage, Anki Manual background. These are dated public-document snapshots, not immutable code pins or comparative trials. No current commercial-product claim is added here. |

Native evidence keys: E1 [October 3 implementation](../../cross-repo-implementation-2026-10-03.md),
E2 [registered-course search continuation](../../cross-repo-continuation-2026-10-03.md),
E3 [prior improvements](../../prior-implementation-improvements-2026-10-03.md),
E4 [October 4 audit](../../fresh-audit-refinement-2026-10-04.md), and
E5 [engine expansion](../../engine-expansion-2026-10-02.md).
Passing tests listed below are those records' receipts unless explicitly called
a proposed gate. A present test file alone is not a fresh passing receipt.

## Matrix-ready task rows

Disposition describes the useful capability, not every donor feature. Core
means a native course job; registered means optional capability within existing
contracts; prototype needs a bounded trial; deferred names an exact prerequisite;
unknown means sampled evidence does not establish the comparison. Every row
retains separate packaged, installed, human and learning-transfer limits.

| CAP; source/pin key and original rows | Learner or author task | Current source/test evidence | Meaningful remaining gap; disposition | Dependency and native gate | Claim limit |
| --- | --- | --- | --- | --- | --- |
| 01; T S01-S03, H A01-A07/F01, M A11-A12 | Start an owned-source course and find existing material before drafting. | `course_ops._op_create`, `_op_register_source`, `discovery.run_report`; existing course/workbench suites. Current `course_workbench.source_inventory` adds bounded explicit course-folder inventory, but this inspection has no passing receipt for that new symbol. | Joined discovery should distinguish unregistered, registered, ambiguous and oversized files; core, partial. | No silent registration/root expansion. Explicit native inventory to source choice to restart, no writes during inventory. | Course-folder discovery is not every approved root or automatically generated whole course. |
| 02; M A01-A04/G01-G23, T S09-S10 | Inspect and correct outline/treatment before accepting a course draft. | `agent_operation.propose_course_outline`, `course_workbench.outline_action`; inventory/E1 records correction, stale refusal, cancel, accept, restart and undo. | Existing flow available; course-scope/blueprint fidelity and broader generation quality remain; core. | Current course revision and source rights; repeat synthetic correction only if changed. Human scope review is separate. | Drafting an outline does not prove complete curriculum generation. |
| 03; M A13-A15/A20-A23/E01-E05, H B01-B11, L A11-A16 | Revise one lesson paragraph with preview, diff, cancel and undo. | `agent_operation.lesson_preview`, `revise`, `accept`, `undo`; `agent_lesson_revision_roundtrip.check_lesson_correction`, `check_changed_source_refuses_accept`, `check_keyed_content_refused`; E1. | Paragraph seam already exists; richer multi-block editor remains optional, no reproduced backend omission; core. | CAS admitted draft/source fingerprints, journal before-image. Native edit/accept/restart/undo if an interface changes. | No full WYSIWYG/editor parity or donor format compatibility claim. |
| 04; T U01-U14/U17-U18/U26-U28, M A05-A06 | Find next work, detour and return to exact course/sitting position. | `course_workbench.course_guidance`, `review_history`; course shell/resume/journey suites; E1/E3 desktop and narrow return receipts. | Workspace composition, clearer dependency/source context; core, partial presentation gate. | Shared route owner and UI lane. Exact objective, pending choice, sitting, scroll and focus survive restart. | Source/browser journeys do not prove learner preference or installed composition. |
| 05; M A07-A10/E17-E18, B1 `huey/storage.py::SqliteStorage`/`api.py::_execute` | Start, interrupt and explicitly retry an author request without accepting late output. | `agent_operation.start_background`, `cancel_request`, `retry_request`, `request_history`; `agent_cancel_retry_roundtrip`; E1/E5. | Owned single-request cancel/retry is available. Multi-job scheduling/backoff remains registered, retained until measured throughput need. | Durable request identity/parent retry, idempotent acceptance, runtime transport owner. Gate queued/running/restart/late-draft cases before multi-job promotion. | Local cancellation receipt cannot prove remote termination or exactly-once delivery. |
| 06; M B01-B11, T S04-S07/S11-S13/U21, B3 FTS/B4 Docling | Find the right registered source passage and open the exact occurrence. | `course_source_search.search`, `admit_match`; E2 eleven source/four native checks. `research_context.search_selected` already has Unicode folding and pagination, E3 seven checks. | Registered-course search remains exact-case and first 32 hits, unlike selected-context search; core ready extension. Optional FTS registered; extraction adapter prototype. | Keep 64-source/128-passage/8 MiB bounds, current quote/read/locator admission. Native case-fold/page/exact-return/stale/no-write journey. | No semantic retrieval, whole-root coverage, large-corpus latency or measured PDF/table fidelity. |
| 07; N ON-F1/ON-F2/ON-U1/ON-U2, T U15-U16 | Keep private notes and deliberate research context linked to a course. | `research_context.apply`, `search_selected`, `notes.read_note_document`; context/A5 suites. Existing health repair accepts `healthy`/`ok`. | Native selected-source/note path available. Live companion read trial deferred; native note/source distinctions core. | Already available pinned service, authenticated notebook identity and read-only rights. Stopped/wrong-ID/auth/stale service gate. | Mock health is not live API compatibility; personal scope export has named loss. |
| 08; N ON-F5/ON-U5 | Link or copy one source quote into a distinct learner note. | `notes.transfer_source_note`, `research_context.apply`; E1 exact duplicate occurrence, rights, independent note identity and undo. | Native Link/Copy quote available; external transfer deferred. | Source identity/revision/rights and external object identity, preview, explicit mode. Native copy/link/undo/restart. | No silent merge or wholesale Open Notebook import. |
| 09; M B12-B17, H C01-C09, L B04-B10, B4 | Reuse media with captions, source lineage and offline meaning. | Existing media/source asset owners and lint are outside this packet; inventory records partial native primitives. | Objective-specific media breadth and extraction losses; prototype, native comparison unknown for variants. | Asset/package rights, stable locators, static fallback, UI/media owners. Missing asset/caption/offline restore gate. | No video-generation, OCR or media-quality equivalence from parser presence. |
| 10; M C01-C14/D10-D14, L C01-C04/A17-A19, P2 | Predict, manipulate and explain one bounded concept. | E1 comparison/lineplot/exploration exact revision/occurrence continuity, reset/cancel and storage fallback; lesson JS/static gates. | Wider objective-specific demonstrations; prototype extensions, existing treatment core. | Lesson/UI ownership, valid scientific model and study-usable static form. Predict/change/explain/apply gate. | Controls and state retention do not establish transfer or Brilliant teaching parity. |
| 11; L E01-E17, M C01-C12, B9 `runs.ts`/`dataflow/graph.py` | Read and control a chart, map, diagram or simulation. | Finite lesson/visual owners and E1 lineplot/comparison receipts. | General chart/map/simulator breadth remains prototype; stale-output patterns registered for a named task. | Trusted bounded controls, validation, static meaning, keyboard/renderer failure. UI lane owns implementation. | No arbitrary active script admission or scientific-validity certification. |
| 12; L F01-F09, H C16-C19, B5 nbformat, P1/P4 | Build, inspect failure and revise executable code/SQL work. | `tests/coding_unit_roundtrip.py` and October 1 coding unit owner supply bounded unit evidence. Learner program text exists in `learner_artifacts`. | General execution/kernel/sandbox/interchange remains prototype and exact assessment domains deferred. | Execution/privacy/cancel boundary, human review, no key leaks. Use coding owner and isolated synthetic task. | A text/program draft is not executed correctness; notebook signatures are not scores. |
| 13; L D01-D18, T L06/L16, M C15-C17 | Practice inside learning and receive only runtime-permitted feedback. | Existing runtime/assessment/lesson owners, E1/E3 guidance/formal withholding/pending/restart tests. | Rich embedding and broader question-family promotion remain partial/prototype; Q1-Q3 exact formats deferred. | Runtime-only scoring/disclosure, stable item identity and exact return; shared/UI owner. Wrong response to allowed tier to lesson to resume. | No invented score, automatic prose mark or general tutoring parity. |
| 14; T L07-L14/P05-P07, B8 py-fsrs, P5 | Review mistakes, pending work and due practice honestly. | `course_workbench.review_history`, `_due_practice_activity`, `retention.utility_order`; E3 due native start/restart and pending precedence. | Due/history already available. Durable cards/notification jobs have distinct identity and delivery prerequisites; registered/deferred extensions. | Anki remains its scheduler. Comparator needs explicit objective/card/rating/time/version mappings. Native due start/retraction/withholding test. | No silent FSRS migration or mastery inferred from self-rating. |
| 15; M D05-D09, T L01-L05, H F02-F04 | Ask a cited source question and return to its exact passage. | `context_help.preview`, `validate_candidate`, `start`, `cancel`; E1/E3 synthetic source-only transport/citation/stale/cancel tests. | Production source_question registration waits for Q4; deferred. Existing ready synthetic source-help seam retained. | Direct adapter decision and schema owner, then synthetic native provider admission. Live chosen-provider trial separate. | Source help does not admit assessment tutoring or prove a live model request. |
| 16; T P01-P04/P15-P16, H F06-F09, B2 APScheduler, P3 | Explain current progress, uncertainty and next work. | `progress_claims.claims_from_events`, `course_workbench.course_guidance`, `retention.retention_report`; progress/guidance suites and E3. | Better objective/prerequisite evidence context ready; notifications deferred on identity/timezone/DST/duplicate-delivery gates. | Existing evidence reader/runtime release, denominators and no readiness verdict. Native graph detour/restart and malformed history refusal. | Completion/accuracy/proficiency remain separate; no copied Khan thresholds. |
| 17; M A16/E06-E16, T P11-P13/P19, L G03-G15, B5 | Export and restore editable courses with explicit losses and consent. | `course_ops.preview_merged_restore`, `apply_merged_restore`, `reopen_merged_restore`; E1/E3 `restore_workspace_roundtrip`, union-copy/reopen and reference preview. | Union-copy available. Root-reference policy application, in-place merge generation admission and interchange variants deferred. | Direct root policy; every writer must share generation admission before in-place merge. Native consent/copy/reopen/undo/offline gate. | No full artifact historical lineage, universal interchange or clean-machine guarantee from API copy alone. |
| 18; M F10-F19/B18, T P08-P10/P14, N ON-F3 | Choose a provider with explicit cost and exact egress. | Existing model adapters/diagnostics, `context_help._destination`; source operation contracts. | Setup completeness/live selected-provider trial remains deferred; optional gateways registered with named use case. | Provider identity, operation admission, rights and no paid calls under this packet. Provider-off/destination preview/refusal gate. | A provider registry does not prove subscription authentication or live model quality. |
| 19; L C05-C14, M D01-D04/D15-D18 | Hear or practice speech where the objective needs it. | Audio/export primitives and `audio_export_roundtrip` exist; no fresh speech task comparison in this pass. | ASR/pronunciation/provider breadth prototype, native comparison unknown. | Objective, model/voice rights, captions/transcript/local playback and explicit egress. UI/audio owner; offline/play/pause/failure gate. | No speech-accuracy or pronunciation-learning claim. |
| 20; H E01-E06/G01-G11, L D19-D25/G08-G15 | Share learner-owned work or collaborate deliberately. | Local ownership and explicit export/share grants remain current authority. | Multi-user/cohort/roles scope deferred; local export core. | Named cohort, authenticated identities, reviewer/share rights and recovery. No external message or account action authorized here. | Local object ownership is not collaborative ACL/auth parity. |
| 21; H A09-A15/G01-G11, M I38 | Publish to an institution/catalog/commercial system. | Native local packaging exists; no adopted SCORM/catalog/cohort publication here. | Deferred, retained backburner until named destination and institutional need. | Rights/auth/interchange/compliance owner and clean import trial. | Fork SCORM source does not prove destination acceptance. |
| 22; H D01-D13, L D19-D25, P4 | Save original work, submit exact bytes, receive human review and compare drafts. | `learner_artifacts.view`, `apply`, `notes.save_artifact_draft`, `artifact_evidence_view`; E1/E3 native pending/mark/retract/export and E4 two revision races. | Core text/proof/program workflow available. Immutable historical rubric/origin-draft provenance decision deferred; broader attachments prototype. | Exact response-event decision and evidence owner; save versus submit versus reviewer authority. Native changed-bank/no-write/mark/retract/restart gate. | Current rubric is not historical rubric; later draft is not submitted original. |
| 23; HF LF01, M H01-H14/I45, B3/B4 | See source support, broken artifacts and the next repair. | `course_workbench.readiness`, `readiness_panel`; E1 readiness tests. Current symbol now emits director source-coverage classes, but no new receipt was inspected for those additions. | Make covered/thin/missing/stale source support actionable; core ready verification/integration seam. | Existing `director.coverage_claims_for`, graph/rights owners; read-only malformed/stale/ambiguous coverage and exact objective repair links. | Structural/source-locator checks are not semantic fidelity certification. |
| 24; T P17, H G12-G14/H07-H08, B1/B6/B9 | Recover after interrupted jobs, damaged storage or restart. | `agent_operation.request_history`, native cancel/retry and restore owners; E1/E3 fault/restart receipts. E4 aggregate stops at host LAN timeout. | Local recovery available; power loss/installed portability and generation-coordinated in-place merge deferred. Optional queue/history mechanisms registered with measured triggers. | Integration owns aggregate/host boundary; no competing full suite. Preserve unresolved remote outcome and accepted files. | Restarting a source fixture does not prove every crash/platform or remote cancellation. |
| 25; M A17-A18/G24-G26/H01-H07, L A05-A10, B7 pluggy | Reuse a template/extension for an actual repeated task. | Source-first Markdown and first-party metadata registry/agent skills exist. | Optional macro/plugin/notebook ecosystem registered; concrete repeat task absent here. | Named handler/version/execute authority, static fallback and disabled-plugin recovery. | Donor macros or hook entry points cannot bypass scoring/rights/admission. |
| 26; M G01-G23/C13-C14, T P05-P07, P1/P3 | Choose a useful next activity and inspect prerequisites without forced mastery judgments. | `course_workbench.course_guidance`, due/missed/source precedence, learner override; E3. Current `prerequisite_context` exposes graph-authored edges plus released attempt counts, without readiness verdict. | Joined prerequisite explanation is ready to verify; broader domain strategies prototype/registered. | Current graph identity and runtime-permitted evidence. Gate unknown edge, missing objective/history, pending/withheld and exact map return. | Authored prerequisite and attempt counts do not prove readiness or learning transfer. |
| 27; T U19-U20, H H01-H11, L B11-B13, P2 | Navigate/read with coherent keyboard, touch and accessible fallback. | E1/E3 exact return at 1280/390/320, keyboard/script-free/reduced-motion; E4 search emphasis and no 320px overflow. | Representative human touch/screen-reader/reflow and broader visual preferences remain deferred acceptance; core. | UI lane owns presentation, integration shared routes. Native equivalent-task review, then human acceptance. | Source/browser automation never self-certifies accessibility or learner preference. |

## Five bounded outcomes to consider

These candidates reuse current owners and add no assessment/provider format,
rights grant, root policy or scheduler migration. New symbols observed in the
shared dirty checkout need their owning worker's receipts before acceptance;
their presence is not permission to reimplement them.

| Code | Candidate and exact owned symbols | Reproducible native acceptance gate |
| --- | --- | --- |
| O1 | Registered-course search: add optional Unicode case folding and bounded pagination to `course_source_search.search`, `admit_match`, `panel`; reuse `research_context._literal_ranges`, preserving original ranges. Existing selected-context search is already complete for this task. | A fictional course with expanded-fold characters and over 32 hits opens page two's exact duplicate occurrence, returns to the same query/mode/page, survives restart, refuses changed rights/locators, and changes no durable bytes. Shared routing/form-field additions require integration ownership. |
| O2 | Explicit local source inventory: finish/verify `course_workbench.source_inventory` through `discovery.run_report`, rather than create another discovery system. | Normal Sources form shows registered versus unregistered versus ambiguous and bounded/oversized results; cancel/reload preserves files; nothing is registered automatically and private metadata roots are excluded. Current source already adds these symbols, so coordinate receipt ownership first. |
| O3 | Source revision impact: finish/verify `course_workbench.source_impact` and `course_context_view.source_impact`, reusing `journal.object_state` and source/binding identity. | Native source changes show accepted versus current revision and exact active dependent objectives. Superseded bindings are excluded; missing/unsafe files remain unavailable. Clicking the dependent objective returns exactly; no acceptance or evidence is changed. |
| O4 | Objective prerequisite context: finish/verify `course_workbench.prerequisite_context`, `course_context_view.prerequisite_return`/`objective_section`, using graph edges and `review_history`. | Native Map shows authored prerequisite and released evidence, detours and returns exactly. Unknown relation, invalid identity, malformed history, formal withholding and pending prose fail honestly without any blocked-learning/mastery verdict. |
| O5 | Source-support readiness: finish/verify `course_workbench.readiness` with existing `director.coverage_claims_for` instead of infer coverage from treatment assignment. | Native readiness reports distinct covered/thin/missing/unknown/error states on synthetic locators and source revisions; stale/denied/malformed inputs give next repair; zero writes and no invented percentage. Existing readiness already checks links/rights/lint. |

O2-O5 appeared in current source during this read and may already be another
worker's programme. O1's exact-case/global-hit-stop was directly confirmed in
`search`; `tests/course_source_search_roundtrip.py::test_query_validation_case_sensitive_unicode_and_empty_course`
also names current exact-case behavior. Update compatible optional defaults,
then change only the tests for the newly selected behavior, preserving callers
that rely on exact matching.

## Retained options, dependencies and honesty limits

The source-feature absorption plan requires pin/license/dependencies/attribution/
maintenance/recovery review before code copying. This programme can adapt named
behavior independently through native owners; no donor source copy is proposed.
B1/B3/B7 stay registered until throughput, query scale or an actual plugin
requires them. B2 notification jobs and B6 high-volume history stay deferred
with their documented revisit triggers. B4/B5/B8/B9 remain bounded prototypes
with measured extraction loss, notebook execution/interchange, rating policy
or simulator need as their respective promotion gates. They were not rejected
for having a backend or dependencies.

Q1-Q4, immutable submission provenance and root-reference policy remain exact
decisions. Unanswered choices prevent promotion of those formats, not the
read-only seams above. Historical help/search/artifact/restore/due/cancel flows
already have source receipts and should not consume a new implementation slot
merely because older donor audits labeled them absent.

The October 4 aggregate receipt remains failed on two LAN-dependent scripts
and inherited dirty state. Integration owns the single combined gate after
writer release. No fresh package, installed composition, representative human
accessibility, live companion/provider trial or learning-transfer equivalence
was verified here. Wider unnumbered historical research coverage remains
unresolved, and the current 27 rows are not an exhaustive all-products census.

Reading limits: AGENTS instructions, task packet/coordination, STATE front
matter, EXEC-CONTEXT, AGENT-WORKFLOW reading/authority sections, targeted
SOURCE-TO-COURSE headings/contracts, source-feature selection gates, all CAP
rows, synthesis, pinned backend comparison, platform proposals, October 3
continuation/improvements and October 4 audit were sampled. Production source
was read by function windows, not whole-module semantic audit. Memory search
returned no task-specific authority used for this report.
