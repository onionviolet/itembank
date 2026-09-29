# OpenTutor to itembank gap inventory

**Date:** 2026-09-27. **Status:** research and routing, no product behavior changed.
**Request:** [verbatim direction](../../USER-VISION.md#2026-09-27-opentutor-comparison-and-modular-ui).

## Evidence and reading limits

OpenTutor was inspected at [`db15d901`](https://github.com/zijinz456/OpenTutor/tree/db15d901a7c5c5f46941487ca4ebc2cfb20425c2), cloned read-only outside this repository. Its [README](https://github.com/zijinz456/OpenTutor/blob/db15d901a7c5c5f46941487ca4ebc2cfb20425c2/README.md), [beta notes](https://github.com/zijinz456/OpenTutor/blob/db15d901a7c5c5f46941487ca4ebc2cfb20425c2/docs/public-beta-release-notes.md), [architecture decision](https://github.com/zijinz456/OpenTutor/blob/db15d901a7c5c5f46941487ca4ebc2cfb20425c2/docs/architecture-decisions.md), block code, app routes, service inventory, and bundled demo screenshots were sampled. The upstream app was not installed or exercised. Screenshots show example states, not proof of a complete workflow. Its beta notes call mobile layouts incomplete and LOOM, LECTOR, and advanced autonomy experimental. The 30-second ingestion claim is marketing, not a measured result here.

Itembank was inspected at `af105e1` on the new `codex/opentutor-gap-inventory-20260927` branch. This is a source comparison, not an installed-app acceptance check. Itembank's [product contract](../../SOURCE-TO-COURSE.md), `surfaces/daemon.py`, `surfaces/ia.py`, `surfaces/course_workbench.py`, `source_adapters.py`, `retention.py`, `model_adapter.py`, and targeted prior research were sampled. Large modules were searched by symbol and read in short windows. No real learner data was opened.

In the tables, **Present** means an equivalent core path exists in source, **Partial** means the capability exists but the named OpenTutor interaction is missing or less integrated, **Missing** means no comparable production path was found in the sampled repo, and **Unverified** means upstream code or a screenshot suggests behavior but this comparison did not execute it. A missing label is a research finding, not an automatic feature requirement. Every candidate remains subject to source rights, runtime authority, offline use, accessibility, and recovery.

## 1. Workspace and visual UI

Upstream evidence: [block types and registry](https://github.com/zijinz456/OpenTutor/blob/db15d901a7c5c5f46941487ca4ebc2cfb20425c2/apps/web/src/lib/block-system/registry.ts), [grid](https://github.com/zijinz456/OpenTutor/blob/db15d901a7c5c5f46941487ca4ebc2cfb20425c2/apps/web/src/components/blocks/block-grid.tsx), [wrapper](https://github.com/zijinz456/OpenTutor/blob/db15d901a7c5c5f46941487ca4ebc2cfb20425c2/apps/web/src/components/blocks/block-wrapper.tsx), [templates](https://github.com/zijinz456/OpenTutor/blob/db15d901a7c5c5f46941487ca4ebc2cfb20425c2/apps/web/src/lib/block-system/templates.ts), and `docs/assets/demo-workspace-full.png`. Itembank evidence: `surfaces/daemon.py` `_course_frame`, `surfaces/ia.py` `COURSE_AREAS`, `surfaces/presentation.py`, and the separate `prototypes/ui-renewal-20260918/`.

| ID | Small OpenTutor mechanism | Itembank today | Gap and fit |
| --- | --- | --- | --- |
| U01 | Course home is a set of independently rendered learning blocks | Partial | Itembank has addressable course areas and an overview path, but no course-home block registry. A registry could compose existing source, lesson, practice, and evidence read models. |
| U02 | Twelve named block types with a shared metadata contract | Partial | Existing semantic treatment and area types are not a display-block vocabulary. Keep display blocks derived and disposable. |
| U03 | Add-block palette | Missing | Useful only for already supported activities. Never offer a block whose content does not exist. |
| U04 | Remove and restore a block | Missing | Removal must hide a view, not delete notes, evidence, or accepted artifacts. |
| U05 | Reorder blocks | Partial | Itembank supports saved course-shelf order, not per-course panel order. Persist through a separate compare-and-swap workspace record. |
| U06 | Resize blocks and one-to-three-column layouts | Missing | Visual preference should not change reading width, content order, or keyboard order unexpectedly. |
| U07 | Preset layouts | Partial | Itembank has presentation profiles, but no course-home content presets. A preset must be reversible and keep the next real action visible. |
| U08 | Four course modes: following, self-paced, exam prep, maintenance | Partial | Itembank's course-position and assessment modes are distinct. A layout mode can be a learner preference, not an assessment policy. |
| U09 | Agent-proposed layout or mode changes with approve/dismiss | Missing | Candidate after a bounded agent proposal protocol. A suggestion is never a mutation until accepted. |
| U10 | Progressive feature unlock based on engagement | Missing | Consider only if it reduces confusion. Do not conceal existing accepted activities or recovery controls. |
| U11 | Per-block collapse on narrow screens | Partial | Itembank uses native course-tools disclosure and responsive lists, but no independently collapsible course-home panels. |
| U12 | Per-block error boundary and recovery copy | Partial | Itembank has page-level degraded states; independent panels could fail without blanking the whole course. |
| U13 | Compact block preview linking to a full-page route | Partial | Overview cards link to full routes; a reusable preview-to-route contract is missing. |
| U14 | Sticky course header with mode and tool shortcuts | Partial | Itembank has course area navigation and a shared shell. The grouped, context-specific header is a UI candidate. |
| U15 | Side chat drawer that retains course context | Missing | Tutor chat is not a production course surface. Preserve the current activity and drafts when it opens. |
| U16 | Notes drawer beside the workspace | Partial | Private notes exist in source reading and evidence views; a course-level side drawer is absent. Keep notes learner-owned. |
| U17 | Cross-course dashboard modules for goals, approvals, jobs, digest, deadlines, review | Partial | Shelf, Activity, day and retention views exist, but they are not composed in one optional dashboard. Do not manufacture percentages or empty metrics. |
| U18 | Mobile-specific composition | Partial | Itembank has responsive course navigation and a UI prototype. OpenTutor itself says some mobile layouts are incomplete, so copy no layout wholesale. |
| U19 | Dark rounded-card visual style and muted green accents | Different, not a functional gap | Bundled screenshots show one visual direction. Test it against Itembank's current UI renewal directions with the same real task. The screenshots also show tall empty panels and repeated headings. |
| U20 | Keyboard layout shortcuts and block movement | Partial | Itembank has keyboard shelf movement. Block shortcuts need discoverability, focus restoration, and a non-shortcut path. |
| U21 | Global course search dialog | Missing | Search would need approved roots, source and lesson locators, and explicit result provenance. |
| U22 | Notification bell in the shared header | Missing | Add only with an actual notification source and quiet, recoverable state. |
| U23 | Visible connection and runtime status | Partial | Itembank has diagnostics and degraded banners, but not one persistent compact status control. |
| U24 | Loading skeleton for individual blocks | Missing | A placeholder should communicate what is loading and preserve the eventual reading order. |
| U25 | Course-specific template picker | Missing | A template is presentation state; applying it must not change accepted course artifacts. |
| U26 | Full-page unit navigation from the course outline | Partial | Itembank's map links objectives and activities, but not OpenTutor's single aggregate unit route. |
| U27 | Dismissible agent insight card | Partial | Agent Activity and proposals exist. A compact insight could link to the actual reviewable operation and its evidence. |
| U28 | Course-home continuation action | Present | Itembank's overview and shelf already expose saved resume and source-first next actions. Preserve that priority in any block layout. |

## 2. Starting a course and handling sources

Upstream evidence: `apps/web/src/app/setup/`, `apps/web/src/app/new/`, `apps/api/services/ingestion/`, `apps/api/services/search/`, and [PRD sections 3 to 5](https://github.com/zijinz456/OpenTutor/blob/db15d901a7c5c5f46941487ca4ebc2cfb20425c2/docs/PRD.md). Itembank evidence: `source_adapters.py`, `course.py`, `graph.py`, `surfaces/reading_desk.py`, `surfaces/binding_cli.py`, and `surfaces/agent_operation.py`.

| ID | Small OpenTutor mechanism | Itembank today | Gap and fit |
| --- | --- | --- | --- |
| S01 | Guided setup with model check and template choice | Partial | Itembank has first-use guidance and settings, but this exact integrated course-start sequence is missing. A no-model route must remain useful. |
| S02 | Habit and preference interview | Missing | Could collect optional learner preferences without treating answers as validated learning traits. |
| S03 | One course-creation flow for upload, URL, and Canvas | Partial | Source registration and adapters exist, but the learner-facing flow does not join these inputs end to end. URL fetching needs its own rights and egress decision. |
| S04 | PDF ingestion | Present | Itembank has a PDF adapter with page locators and explicit dependency/degraded behavior. Do not duplicate it. |
| S05 | DOCX ingestion | Present | Itembank has a DOCX adapter with preserved structural locators. Do not duplicate it. |
| S06 | PPTX ingestion | Present | Itembank has a PPTX adapter. Compare fidelity with a shared fixture before changing it. |
| S07 | Canvas material import | Partial | Itembank has Canvas LTI integration, not a general course-material sync equivalent to OpenTutor's Canvas loader. Treat access and downstream content rights separately. |
| S08 | Visible parse progress and stage-specific failure recovery | Partial | Agent Activity has durable states; source ingestion is not yet one learner-facing staged job. |
| S09 | Auto-generated notes after upload | Partial | Itembank can draft bounded artifacts through agent operations, but lacks OpenTutor's one-click ingest-to-notes default. Direct reading may be the better treatment. |
| S10 | Auto-generated flashcards and quiz after upload | Partial | Bank authoring and study exist; automatic generation still needs source binding, lint, review, and accepted revision. |
| S11 | Hybrid keyword and vector retrieval for tutor grounding | Missing | Source locators exist; a disposable, local retrieval index and cited passage protocol are possible later. Do not let an index become canonical source truth. |
| S12 | Source versus AI-notes switch in one reader | Partial | Itembank has source reading and lessons, but no unified side-by-side or toggle in the production course screen. Label synthesis and retain exact source locators. |
| S13 | Regenerate only one section's notes | Partial | Bounded proposals exist. A targeted, reviewed section revision needs conflict and stale-dependency handling. |
| S14 | Course chapter/unit aggregate route | Partial | The course map and objective links exist; there is no one-page unit view joining source, lesson, practice, errors, and review history. |

## 3. Tutor, learning loop, and assessment

Upstream evidence: `apps/api/services/agent/`, `apps/api/routers/chat.py`, `apps/api/services/diagnosis/`, `apps/api/services/spaced_repetition/`, `apps/web/src/app/course/[id]/practice/`, and `apps/web/src/app/course/[id]/review/`. Itembank evidence: `runtime.py`, `model.py`, `retention.py`, `surfaces/quiz_page.py`, `surfaces/study.py`, `surfaces/home.py`, `surfaces/retention_view.py`, and `model_adapter.py`.

| ID | Small OpenTutor mechanism | Itembank today | Gap and fit |
| --- | --- | --- | --- |
| L01 | Always-available course tutor chat | Missing | A chat must honor approved source scope, operation egress, and assessment disclosure. |
| L02 | Passage-grounded tutor answer with inline source citation | Partial | Citations and source bindings are contractual; a production interactive tutor with retrieved, checkable passage citations is absent. |
| L03 | Stateful Socratic tutor conversation | Partial | `guiding-questions` and runtime-issued tiers support bounded tutoring, but there is no durable course chat state machine. |
| L04 | Tutor depth adjustment from error or fatigue signals | Missing | Candidate only with transparent signals and a learner override. A short message is weak evidence of fatigue. |
| L05 | Tutor, planner, and layout specialist routing | Partial | Itembank has bounded agent operations and backend adapters; no always-on routed trio. Keep specialists behind one operation protocol. |
| L06 | Seven generated quiz formats | Present in broader form | Itembank's parser already has mc, multi, table, build, dnd, short, check, visual, and fill. Format count is not a gap. |
| L07 | Wrong-answer collection and review route | Partial | Runtime evidence, missed-item forms, and retention review exist; a course-level misconception page with navigable history is missing. |
| L08 | Adaptive difficulty selection | Partial | Itembank has deterministic selection and evidence. A validated per-learner difficulty policy and UI are not complete. Do not infer mastery from sparse attempts. |
| L09 | FSRS card scheduler | Partial | Itembank has an FSRS strategy over objective evidence. It does not yet offer OpenTutor's complete persistent card-review workflow in the course UI. |
| L10 | Card-by-card review experience | Partial | `study` offers flashcards and a session-only Learn loop; a durable course review route is missing. |
| L11 | Review reminders and forgetting forecast | Partial | Due objective recommendations exist. Proactive notification delivery and a learner-facing forecast are absent. |
| L12 | Knowledge graph visualization with related concepts | Partial | Itembank's canonical graph stores objectives, prerequisites, and bindings; a rich interactive concept map is not the production default. |
| L13 | Graph-aware review order, LOOM and LECTOR | Missing or experimental upstream | OpenTutor's own beta notes mark these experimental. First compare a fixed, evidence-grounded review task with Itembank's due ordering. |
| L14 | Cognitive-load and behavior-signal engine | Missing or experimental upstream | OpenTutor has code, but the accuracy and benefit of inference were not checked. Record as research, not a requirement. |
| L15 | Code execution alongside a coding question | Prototype only in Itembank | Itembank's UI renewal prototype leaves room for a runner. Production needs isolation, draft recovery, and runtime-owned grading. |
| L16 | Preview, feedback, and progression within a compact quiz panel | Partial | Itembank's quiz flow is richer in authority and types, but not embedded as a course-home block. Embedding cannot create another scorer. |
| L17 | Chat streaming indicator and visible tool progress | Missing | Useful when an approved tutor operation takes time. Show exact stage and cancellation or recovery state. |
| L18 | Chat attachments for files, images, and URLs | Partial | Itembank has source registration, OCR tooling, and adapters, but no production course-chat attachment flow. Each attachment needs a separate rights and egress scope. |
| L19 | Clarification and proposed-action cards inside chat | Partial | Itembank has bounded agent proposals outside chat. Inline cards could project the same proposal record without giving chat a second mutation path. |
| L20 | Per-question wrong-answer explanation and confusion pairs | Partial | Itembank has authored distractor analysis and runtime feedback. It lacks OpenTutor's dedicated confusion-pair review presentation. |
| L21 | Swipe gesture for flashcard review | Missing | Touch is an optional accelerator; keep explicit labeled controls, keyboard access, and the same saved outcome. |
| L22 | Image or LaTeX OCR in tutoring | Partial | Itembank has optional OCR tooling and LaTeX display/input paths, not a tutor attachment-to-grounded-answer flow. |

## 4. Planning, evidence, providers, and export

Upstream evidence: `apps/web/src/app/course/[id]/plan/`, `apps/web/src/app/analytics/`, `apps/api/services/scheduler/`, `apps/api/services/llm/`, `apps/api/services/export/`, and `apps/web/src/app/settings/sections/`. Itembank evidence: `surfaces/day.py`, `surfaces/retention_view.py`, `surfaces/settings.py`, `model_adapter.py`, `surfaces/anki.py`, `surfaces/gift.py`, and `surfaces/agent_operation.py`.

| ID | Small OpenTutor mechanism | Itembank today | Gap and fit |
| --- | --- | --- | --- |
| P01 | Course calendar of deadlines and tasks | Partial | Itembank has a cross-subject day plan and due views, but no first-class per-course calendar UI. |
| P02 | Plan generated from syllabus and deadline extraction | Missing | A proposal could cite syllabus locators and require review before saving tasks. |
| P03 | Proactive reminders and notifications | Missing | Needs user-controlled schedule, quiet defaults, and a durable notification record. |
| P04 | Cross-course daily digest | Partial | Day and home recommendations exist; no generated narrative digest. Show source evidence and avoid invented work. |
| P05 | Dedicated charts for study time, quiz activity, error categories, memory health | Partial | Itembank has evidence reports and retention metrics, but not OpenTutor's chart suite. Charts must show denominators and missing data. |
| P06 | Per-concept mastery timeline | Partial | Objective histories exist; a navigable timeline view is missing. |
| P07 | Goal, approval, and running-task counters on home | Partial | Activity and course state exist; one cross-course summary row is missing. Avoid zeroes when data is unavailable. |
| P08 | Provider connection cards and runtime status | Partial | Itembank has model profiles and diagnostics, not OpenTutor's provider-specific cards. |
| P09 | Ten-plus provider presets | Partial | Itembank has registered subprocess and OpenAI-compatible HTTP transports. Provider count is not a meaningful gap, but setup discoverability is. |
| P10 | Local Ollama as turnkey default | Partial | Itembank supports local model profiles and optional OCR. A guided first-run connection test is missing. |
| P11 | Anki export | Present | Itembank has Anki export. Compare a real round trip before changing it. |
| P12 | Calendar and Notion export | Missing or outside current scope | Calendar export may fit learner-owned plans. Notion egress requires a separate share grant. |
| P13 | Portable session/review export | Present or partial | Itembank exports evidence and artifacts through its own contracts; verify clean offline restore rather than assuming formats match. |
| P14 | Usage and provider-cost page | Partial | Itembank has local model diagnostics and storage use. A provider usage estimate needs complete accounting and explicit unknown states. |
| P15 | Notification preferences in settings | Missing | Depends on a real reminder service and clear defaults. |
| P16 | Error breakdown and diagnosed-pattern charts | Partial | Itembank records wrong responses and objective evidence. The visual summaries and diagnosis labels are not one course-level route. |
| P17 | Local deployment health checks and Docker quickstart | Different delivery choice | Itembank packages a Tauri shell around the local runtime. Adopt useful readiness diagnostics, not the Docker stack. |
| P18 | Browser and web-search tools for the agent | Missing or outside scope | Remote browsing can send source content or queries away. It needs per-operation permission and exact egress disclosure. |
| P19 | Optional Notion and external export integrations | Missing or gated upstream | OpenTutor gates Notion export. Itembank should treat external share as a separate grant, never a default backup. |

## What the screenshots actually teach

OpenTutor's bundled `demo-dashboard.png`, `demo-workspace-full.png`, `demo-practice.png`, `demo-notes.png`, and `demo-chat.png` were viewed. The useful UI mechanisms are a stable course header, concise per-panel headings, an add-block entrypoint, a course grid that can grow with the learner, a side tutor that leaves the workspace visible, a notes/source switch, and a compact-to-full activity path. The sample practice screen keeps the prompt and answer targets visually dominant. These are composition and interaction ideas, not a mandate to copy its colors or code.

The same screenshots show much empty vertical space, repeated block headings, and at least one broken request toast in a captured workspace state. They cannot establish mobile quality, persistence, keyboard behavior, source citation quality, or learning benefit. Itembank's [UI craft direction](../ui-craft-2026-09-25/SYNTHESIS.md) and [renewal prototype](../../../prototypes/ui-renewal-20260918/README.md) already provide a stronger local comparison baseline than a screenshot copy.

## Five small adoption slices

1. **UI foundation:** Add a read-only, typed course-home block registry that renders the existing source, lesson, practice, and evidence paths. Verify source-first order, script-free content, desktop and narrow layout, and no duplicate scoring.
2. **Learner layout:** Add reorder and hide controls with keyboard equivalents and undo. Persist a presentation-only layout through the existing compare-and-swap journal, keyed by stable course ID. Keep canonical content reachable through course areas.
3. **Source and notes:** Put accepted source ranges and synthesized notes in one course context with explicit origin labels and exact locators. Preserve the existing reading and private-note authority.
4. **Course review:** Join existing due objectives and saved sittings into a compact review block that opens the authoritative runtime route. Avoid new mastery claims or a parallel scheduler.
5. **Tutor entry:** Prototype a context-preserving side tutor against one synthetic course with cited, rights-granted passages and the runtime's disclosure gate. Promotion requires an exact egress and recovery review.

The first two slices address the user's explicit modular UI request. Later slices are ordered by reusable current capability, not by OpenTutor's marketing order. A later pass should inspect and exercise the upstream app if a specific behavior depends on undocumented runtime details. No upstream source code, dependencies, CSS, images, or learner data were copied.
