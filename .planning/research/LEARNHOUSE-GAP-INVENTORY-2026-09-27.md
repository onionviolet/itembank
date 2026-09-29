# LearnHouse capability gap inventory

Date: 2026-09-27. Status: research inventory for consideration, not an adoption plan.

## Request, scope, and evidence

User request: “Consider [https://github.com/learnhouse/learnhouse ](https://github.com/learnhouse/learnhouse)has that we dont, first writing every little thing from there that we dont have, we wont be absorbing everything but I want to take them into consideration for what we are trying to do”. The first step is a granular record of differences. Presence in LearnHouse does not imply fit, priority, or authorization to copy code.

LearnHouse source: [`5e28b0723176b34ba8777b9980db352268aa8234`](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234) on `dev`, inspected read-only from its README, docs, API routers and models, web components, and selected end-to-end test names. Itembank comparison: current `main` checkout, `SOURCE-TO-COURSE.md`, `STATE.md`, `README.md`, `surfaces/course_ops.py`, `surfaces/course_workbench.py`, and the earlier [selective absorption record](competition-2026-09-08/ABSORPTION.md). The checkout has unrelated uncommitted work; some new candidates are not accepted or packaged. Neither LearnHouse nor the installed itembank app was run for this inventory. A code path establishes an implemented route or component, not production reliability or a good learner experience.

Legend: **G** means no comparable integrated itembank flow found. **P** means a related itembank primitive or plan exists, but the end-to-end capability is partial. **D** means LearnHouse differs from a currently binding itembank direction; keep it visible for consideration. **U** means the upstream tree suggests a feature but its delivered behavior was not verified. These are feature-level observations, including small behavior options, not a line-by-line enumeration of 2,407 upstream files. Routes: **Prototype** needs learner or technical evidence; **Registered** is a plausible optional capability under itembank's current authority; **Backburner** is viable but needs a concrete use case; **Deferred** needs rights, privacy, security, or product-scope resolution; **Different** records a pattern that should not silently replace a current contract.

## A. Course structure, discovery, and publishing

Evidence: [README](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/README.md), [course migration guide](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/docs/content/developers/migration/index.mdx), [course and folder API](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/courses), [folder API](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/folders/folders.py).

| ID | LearnHouse difference | State | Route |
| --- | --- | --- | --- |
| A01 | Author-facing course, chapter, and ordered activity tree with create/edit/delete controls | P | Registered |
| A02 | Drag-and-drop chapter and activity ordering in a visual course editor | G | Prototype |
| A03 | Reorder or move course content across library folders and root | P | Registered |
| A04 | Collections that bundle several published courses for discovery | G | Backburner |
| A05 | Course cloning through author API | G | Registered |
| A06 | Multiple named contributors to one course | G | Backburner |
| A07 | Separate course landing page with thumbnail, description, authors, activity count, and start action | P | Prototype |
| A08 | Draft versus published course and activity states | P | Registered |
| A09 | Public course catalog and organization search across courses, collections, and users | G | Backburner |
| A10 | Course SEO metadata, sitemap, and social preview controls | G | Backburner |
| A11 | Course updates or announcements presented to enrolled learners | G | Backburner |
| A12 | Course access settings for public, signed-in, and restricted groups | G | Deferred |
| A13 | Chapter or activity locks tied to access rules | G | Deferred |
| A14 | Activity completion trail, visible course progress, and course completion event | P | Prototype |
| A15 | Teacher-facing progress view of learners across a course | G | Backburner |
| A16 | Course export/import as an LMS content tree | P | Deferred |

Itembank has a course manifest, objectives, treatments, course shelf, course operations, local evidence, and manifest-validated package export/restore. Its course map is objective-led; LearnHouse's chapter/activity tree is a presentation and publishing model, not a replacement for that graph.

## B. Authoring, migration, and AI workbench

Evidence: [editor components](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/web/components/Objects/Editor), [slash command catalog](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/apps/web/components/Objects/Editor/Extensions/SlashCommands/slashCommandsConfig.tsx), [assisted migration guide](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/docs/content/developers/migration/assisted.mdx), [AI routes](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/ai).

| ID | Difference | State | Route |
| --- | --- | --- | --- |
| B01 | Inline block editor for course pages rather than file-first authoring | D | Different |
| B02 | Slash menu grouped by text, media, interactive, callout, UI, and table blocks | G | Prototype |
| B03 | Drag handle, insert, and rearrange individual content blocks | G | Prototype |
| B04 | Rich preview before publishing an activity | P | Registered |
| B05 | Unsaved-change warning on navigation and save shortcut | P | Registered |
| B06 | Remote edit conflict check and merge/overwrite/discard review UI | P | Deferred |
| B07 | Page version history with restore UI | P | Registered |
| B08 | Simultaneous multi-author text editing via the collaboration server | G | Backburner |
| B09 | AI editor side panel and selection-aware content edits | P | Prototype |
| B10 | AI streamed edits shown in the page editor | G | Prototype |
| B11 | AI-generated quiz, assignment, scenario, image, audio, and interactive block entry points | P | Prototype |
| B12 | Upload several videos, PDFs, images, or audio files into a temporary migration batch | P | Registered |
| B13 | AI proposes chapter grouping, order, and titles before course creation | P | Prototype |
| B14 | Learner edits that proposed structure before committing a private course | P | Registered |
| B15 | Flat, filename-derived structure if the AI service fails | G | Registered |
| B16 | Programmatic course/chapter/activity creation and reordering APIs | P | Registered |
| B17 | Separate media library and reusable uploaded blocks | P | Deferred |
| B18 | Real-time image, audio, and course planning tools in the authoring UI | P | Prototype |

The [assisted migration guide](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/docs/content/developers/migration/assisted.mdx) says that route handles media only and makes the created course private and unpublished. Itembank's source-first path handles text-heavy books, notes, objectives, citations, rights, validation, and accepted revisions; no upstream one-shot publish path should bypass those checks.

## C. Content blocks, media, and learner interaction

Evidence: [activity types](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/docs/content/developers/migration/activity-types.mdx), [editor extensions](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/web/components/Objects/Editor/Extensions), [activity viewers](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/web/components/Objects/Activities), [playground API](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/playgrounds).

| ID | Difference | State | Route |
| --- | --- | --- | --- |
| C01 | Hosted video activity with learner playback tracking | G | Prototype |
| C02 | YouTube video activity as a separate course unit | P | Registered |
| C03 | Video player caption and playback setting controls | G | Registered |
| C04 | Uploaded PDF and generic document as activity viewers | P | Registered |
| C05 | Hosted audio block and podcast embed in a lesson page | P | Prototype |
| C06 | External web embed or remote Markdown activity | D | Different |
| C07 | Image and video blocks with asset management in the editor | P | Deferred |
| C08 | Inline tables, buttons, badges, links, user blocks, and styled callouts | P | Prototype |
| C09 | Inline math equation block | P | Registered |
| C10 | Flipcard and flashcard grid inside lesson content | P | Prototype |
| C11 | Embedded quiz block inside a dynamic page | P | Prototype |
| C12 | Embedded H5P activity | G | Backburner |
| C13 | AI-generated HTML Magic Block with live preview | D | Different |
| C14 | Hosted AI-generated interactive playground, with public/signed-in/group access | G | Deferred |
| C15 | Interactive scenarios inside a page | P | Prototype |
| C16 | Learner can run code in a page-level playground | P | Prototype |
| C17 | Judge0-backed code execution across many languages with test cases | P | Deferred |
| C18 | SQL exercise with an uploaded SQLite database | G | Prototype |
| C19 | Code submission history, code diff, and error annotations beside the editor | P | Prototype |
| C20 | SCORM package as a course activity | G | Backburner |

Itembank already renders semantic Markdown lessons, guided stages, a bounded declarative comparison interaction, offline math, flashcard study, and runtime-owned code checking. C06, C13, and C14 need particular scrutiny because remote content and arbitrary executable HTML change rights, portability, offline behavior, and the static fallback. C17 is a depth comparison, not a claim that itembank cannot run code.

## D. Assignments and assessment operations

Evidence: [assignment route](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/courses/assignments.py), [assignment activity docs](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/docs/content/developers/migration/activity-types.mdx#assignments), [assignment browser tests](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/e2e/features/assignments/tests).

| ID | Difference | State | Route |
| --- | --- | --- | --- |
| D01 | Teacher-authored assignment with due date, instructions, and multiple tasks | P | Registered |
| D02 | Learner upload of a file as submitted work | G | Prototype |
| D03 | Assignment task formats: quiz, form, code, short answer, numeric answer, file, other | P | Registered |
| D04 | Per-assignment grading scale: percent, numeric, letters, pass/fail, GPA | G | Backburner |
| D05 | Teacher rubric and manual task-level mark with overall feedback | P | Registered |
| D06 | Learner draft autosave before final submission | P | Registered |
| D07 | Teacher submissions list with status filters, search, sorting, and counts | G | Backburner |
| D08 | Teacher can reject a submission and ask for a new one | G | Deferred |
| D09 | Configurable retry after a graded attempt | P | Prototype |
| D10 | Teacher control over revealing correct answers after marking | P | Registered |
| D11 | Per-task grading override and formative versus graded behavior | P | Prototype |
| D12 | Assignment analytics including grade distribution and pass rate | P | Backburner |
| D13 | Optional anti-copy/paste setting | G | Deferred |

Itembank's own `Today` assignment projection reads an external assignment ledger; it is not a teacher submission system. Itembank has a stronger assessment authority boundary: the runtime scores objective items, while prose stays pending review. Any adopted D05 to D12 flow must keep that single authority.

## E. Social, collaboration, and audio publishing

Evidence: [discussion routes](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/communities/discussions.py), [board routes](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/boards), [podcast routes](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/podcasts), [collaboration app](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/collab).

| ID | Difference | State | Route |
| --- | --- | --- | --- |
| E01 | Course-linked community with discussion threads | G | Backburner |
| E02 | Discussion comments and nested replies | G | Backburner |
| E03 | Discussion votes, reactions, and labels | G | Backburner |
| E04 | Real-time shared whiteboards with drawings and sticky notes | G | Backburner |
| E05 | Board frames and embedded content | G | Prototype |
| E06 | Board owner/editor/viewer membership | G | Deferred |
| E07 | Podcast series, episodes, thumbnails, and audio uploads | G | Backburner |
| E08 | Reorderable episodes and streaming learner player | G | Backburner |
| E09 | Course contributor collaboration separate from learner discussion | G | Backburner |

These are institution or creator workflows. A personal note, diagram, or source audio activity may serve itembank's learner more directly. The September 8 user direction already kept simulated classroom discussion out of the default lesson flow; this inventory does not reverse it.

## F. Search, AI help, progress, analytics, and credentials

Evidence: [search API](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/search.py), [AI and RAG routes](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/ai), [analytics API](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/analytics.py), [analytics widgets](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/web/components/Dashboard/Analytics), [certifications](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/courses/certifications.py).

| ID | Difference | State | Route |
| --- | --- | --- | --- |
| F01 | Organization-wide search across courses, content, collections, and people | P | Registered |
| F02 | Contextual AI chat within an activity | P | Prototype |
| F03 | Retrieval chat with indexed course content and saved chat sessions | P | Prototype |
| F04 | Follow-up question suggestions in activity AI UI | G | Prototype |
| F05 | Teacher-facing course planning AI | P | Prototype |
| F06 | Course analytics: views, enrollment, active learners, dropoff, retention, completion | P | Backburner |
| F07 | Activity analytics: time, funnel, engagement by content type, peak hours | P | Deferred |
| F08 | Assignment grade distribution and top learners | G | Backburner |
| F09 | Analytics CSV export | P | Deferred |
| F10 | Certificate template, award, revoke, and learner download | G | Backburner |
| F11 | Completion certificate issued automatically from course trail | G | Deferred |
| F12 | Personalized email nudges or progress reminders | G | Deferred |

Itembank already has local attempt evidence and objective reports; it should not equate a view or elapsed time with mastery. F06 to F09 would need learner-owned, local, denominated evidence rather than hosted engagement telemetry. A certificate would need explicit completion criteria and verification.

## G. Organization, delivery, and operator tools

Evidence: [README enterprise features](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/README.md), [API reference groups](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/docs/lib/reference/config.js), [auth routes](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/auth.py), [CLI docs](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/docs/content/cli/commands.mdx), [webhooks](https://github.com/learnhouse/learnhouse/blob/5e28b0723176b34ba8777b9980db352268aa8234/apps/api/src/routers/webhooks.py).

| ID | Difference | State | Route |
| --- | --- | --- | --- |
| G01 | Multi-organization hosted tenancy | D | Different |
| G02 | Organization branding, theme, landing page, and custom domain | P | Backburner |
| G03 | Managed learners, instructors, admins, and custom roles | G | Deferred |
| G04 | User groups for cohort enrollment and gated content | G | Deferred |
| G05 | Email, magic link, OAuth, and enterprise SSO login | G | Deferred |
| G06 | MFA, organization security policy, and recovery codes | G | Deferred |
| G07 | API tokens with scoped rights and headless provisioning | P | Deferred |
| G08 | Bulk enrollment, progress reset, and user data export | G | Backburner |
| G09 | Payment products, prices, checkout, subscriptions, and enrollment | G | Deferred |
| G10 | Webhook endpoint, event delivery history, test event, and secret rotation | G | Backburner |
| G11 | Zapier integration | G | Backburner |
| G12 | Operator CLI for setup, start/stop, update, logs, backup, and diagnosis | P | Registered |
| G13 | Self-hosted multi-service deployment with database and live collaboration server | D | Different |
| G14 | Public API reference and external developer workflow | P | Registered |
| G15 | SCORM delivery or institutional LMS interchange | P | Backburner |

Itembank's shipped foundation is local-first, single-owner files and a desktop shell. G01 and G13 are separate delivery models with real operating and data-residency costs. The other G items remain visible if a creator or institution use case is later accepted.

## H. Small UI and workflow details worth testing

Evidence: [course edit UI](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/web/components/Dashboard/Pages/Course), [student activities](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/web/components/Objects/Activities), [assignment browser tests](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/e2e/features/assignments/tests), [command palette](https://github.com/learnhouse/learnhouse/tree/5e28b0723176b34ba8777b9980db352268aa8234/apps/web/components/Dashboard/CommandPalette).

| ID | Difference | State | Route |
| --- | --- | --- | --- |
| H01 | Dashboard command palette for fast navigation and actions | G | Prototype |
| H02 | Contextual breadcrumbs across organization, course, and activity | P | Prototype |
| H03 | Course author controls grouped by general, structure, access, contributors, certification, and SEO | G | Prototype |
| H04 | Activity type switcher inside author editor | G | Prototype |
| H05 | Sidebar table of contents for long authored activity pages | P | Registered |
| H06 | Preview toggle while editing course content | P | Registered |
| H07 | Clear empty, loading, locked, and unavailable states for course activities | P | Prototype |
| H08 | Saved submission resumes in the activity, with status and retry controls | P | Prototype |
| H09 | Dedicated course share control | G | Deferred |
| H10 | Organization and learner dashboards separated by role | G | Backburner |
| H11 | RTL layout and browser test coverage | P | Registered |

No live visual or accessibility comparison was run. These are code-backed UI candidates, not claims that LearnHouse's styling or flows outperform itembank. Compare representative learner tasks on desktop and phone before selecting a design pattern.

## First consideration pass

1. **Prototype** the visual authoring and review path around one source-backed lesson: outline editing, block-level preview, unsaved-change protection, and clear version differences (B02 to B07, H04 to H06). Preserve accepted Markdown as the canonical artifact.
2. **Register** small learner media and interaction components when a real objective needs them: captioned video, a document activity, flipcard, scenario, or code history (C01 to C05, C10, C15 to C19). Require a study-usable static form and local recovery.
3. **Prototype** assignment submission and feedback only if the use case includes work beyond itembank's current bank sittings (D01 to D12). Keep pending prose and runtime-owned settled marks.
4. **Backburner** social, multi-user, credentials, commerce, and hosted analytics until a concrete creator or institution job appears (E, F06 to F12, G01 to G11). This is a timing and cost route, not a rejection.
5. **Keep the product contrast visible:** LearnHouse is organized around author publishing and institution operations. Itembank's binding differentiator is learner-owned sources, objective-linked treatments, local evidence, reviewable agent edits, and recoverable plain files. A gap is useful only if it strengthens that course journey.

## Coverage and limits

Checked the README feature list, the available platform overview, activity and migration guides, named API router groups, editor extension list, course editor areas, analytics widget list, and assignment E2E test names. The platform overview links several guide pages absent from this checkout, so the source code supplied the finer claims. Did not execute LearnHouse, test its hosted or enterprise edition, audit every setting/translation, or visually compare its actual running UI. Future passes should update individual rows when behavior is confirmed or when Itembank's packaged app changes. No upstream code was copied and no implementation was authorized by this inventory.
