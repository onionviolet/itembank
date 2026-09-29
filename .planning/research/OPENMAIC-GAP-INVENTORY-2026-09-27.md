# OpenMAIC capability gap inventory

Date: 2026-09-27. Status: research inventory, not an adoption decision or implementation plan.

## Request and evidence

User request: “absorb everything [https://github.com/THU-MAIC/OpenMAIC](https://github.com/THU-MAIC/OpenMAIC) has that we dont, first writing every little thing from there that we dont have”. This document performs the first step: list the observable differences before deciding what to implement. “Everything” is an inventory scope here, not permission to replace itembank's scoring, source, rights, or accepted revision authority.

OpenMAIC source revision: [`f2875426ae5712d26f0a76e54e9de763e86027a6`](https://github.com/THU-MAIC/OpenMAIC/tree/f2875426ae5712d26f0a76e54e9de763e86027a6), with the [README](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md), [1.1.1 changelog](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/CHANGELOG.md), source tree, package docs, and skills inspected read-only. Itembank comparison uses current `main`, `STATE.md`, `SOURCE-TO-COURSE.md`, `AGENT-WORKFLOW.md`, current source and surface symbols, and the prior [absorption record](competition-2026-09-08/ABSORPTION.md). No OpenMAIC server or full learner run was executed in this pass. A checked source path proves a code path exists, not that its UX or learning benefit passes a live trial.

Legend: **G** = no comparable integrated user flow found; **P** = itembank has a related primitive or limited flow, but not this end-to-end capability; **D** = deliberately different product direction in the current contract. **D still records the difference** because the request is exhaustive. An item can be both useful and blocked by a current boundary. A provider name, bug fix, or internal component is listed when it gives a distinct user or operator capability. This is feature-level coverage, not a claim to enumerate every source file, setting, and commit.

## A. Course creation and workbench

Source: [README, Agent Workbench](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#agent-workbench-and-pro-mode-v100), [changelog 1.0.0](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/CHANGELOG.md#100---2026-08-27). Itembank has a course shelf, source and objective contracts, skill playbooks, and bounded agent proposals. Its recorded live source-to-lesson generation remains unproved.

| ID | OpenMAIC capability itembank lacks or has only partly | State |
| --- | --- | --- |
| A01 | One prompt or uploaded material produces a complete playable course with outline and scenes | P |
| A02 | Classic two-stage outline then per-scene generation pipeline exposed to the user | P |
| A03 | Learner edits the generated outline before scene generation | G |
| A04 | Chat-first Pro workbench for building and revising a whole course | P |
| A05 | Workbench layout with folders, conversation rail, chat, and live classroom pane | G |
| A06 | Multiple open courses as workspace tabs | G |
| A07 | Conversational follow-up steering while a course-building run is active | G |
| A08 | Replayable streamed tool and event history for a durable building session | P |
| A09 | Background agent sessions with database leases, heartbeats, crash resume, and cancellation | P |
| A10 | Agent questions that pause a run and resume after user input | P |
| A11 | Agent creates, renames, moves, and folders courses through validated tools | P |
| A12 | Agent generates, duplicates, inserts, deletes, and reorders course pages | G |
| A13 | Agent patches one scene atomically and edits narration or deck structure | P |
| A14 | Agent reads and searches the scene DSL before editing | G |
| A15 | Agent renders a scene preview for visual inspection | P |
| A16 | Agent imports a slide deck as editable course scenes | G |
| A17 | Agent can create and update owner-stored skills in the workbench | G |
| A18 | User can list, upload, download, and delete workbench skills in Settings | G |
| A19 | Per-viewer course sidecar for ownership, publication, and generation-complete state | P |
| A20 | Per-scene freshness counters and targeted refresh of changed course pages | P |
| A21 | Contextual course and page references in the workbench composer | G |
| A22 | AI edit history spanning multiple workbench sessions with validated JSON Patch | G |
| A23 | Visual course editor as a first-class parallel mode to playback | G |

## B. Materials, retrieval, and media generation

Source: [README, materials and tools](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#agent-workbench-and-pro-mode-v100), [README, lesson generation](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#lesson-generation), [changelog 1.1.0](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/CHANGELOG.md#110---2026-09-24). Itembank has typed source adapters for PDF, DOCX, PPTX, web, transcript, OCR, EPUB, and registered ASR; those are not counted as wholly missing.

| ID | Difference | State |
| --- | --- | --- |
| B01 | Drop or upload mixed document, image, audio, and video files directly into a building session | P |
| B02 | Material upload retains original bytes in an asset pool before extraction | P |
| B03 | Session agent searches extracted material text with a tool | P |
| B04 | Material library lets one stored source serve multiple agent sessions | P |
| B05 | Audio or video extraction yields time-stamped transcripts and prepared keyframes | G |
| B06 | Local ffmpeg/ffprobe plus configured ASR performs that media extraction | G |
| B07 | AliDocMind cloud media extraction is a configurable fallback | G |
| B08 | MinerU and AliDocMind document parsing are selectable provider paths | G |
| B09 | Web search is available during course construction | G |
| B10 | Agent fetches approved web URLs as session material | P |
| B11 | Lexical retrieval foundation over extracted documents for agent context | P |
| B12 | Agent generates images for course pages through configured providers | G |
| B13 | Agent generates video with an asynchronous placeholder then resolves the asset | G |
| B14 | Agent generates narration audio tied to course content | G |
| B15 | Generated media and extracted derivatives have asset IDs and source lineage | P |
| B16 | Generated media persists once and resolves in other browsers without regeneration | G |
| B17 | Agent reuses uploaded material images or video in course scenes | P |
| B18 | Automatic language inference for course generation | G |

## C. Scene types and interactive teaching

Source: [README, Deep Interactive Mode](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#deep-interactive-mode-new), [README, classroom components](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#classroom-components), [interactive host](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/components/scene-renderers/InteractiveIframeHost.tsx). Itembank has semantic Markdown lessons, guided stages, glossary and callout roles, one bounded native comparison interaction, quiz and code activity foundations. The OpenMAIC HTML host is a different execution and portability model.

| ID | Difference | State |
| --- | --- | --- |
| C01 | Generated slide scenes with positioned visual elements and animations | G |
| C02 | Generated 3D models that learners rotate or inspect | G |
| C03 | Generated process or experiment simulations with learner controls | P |
| C04 | Generated educational mini-games | G |
| C05 | Generated explorable mind maps | P |
| C06 | Generated in-browser coding experiences inside interactive scenes | P |
| C07 | General authored or generated interactive HTML embedded in a sandboxed iframe | D |
| C08 | Interactive scene can declare state for the teacher to inspect at question time | G |
| C09 | Runtime error banner for failed generated interactive scripts | G |
| C10 | Interactive scene script validation before accepting model output | G |
| C11 | Agent action can change widget state, set a condition, or highlight part of it | G |
| C12 | Responsive generated interactive pages across desktop, tablet, and phone | P |
| C13 | Project-based learning scene with learner role, milestones, deliverables, and collaborators | G |
| C14 | Vocational task engine and project proficiency/progress events | G |
| C15 | Real-time AI feedback and grading for free-text quiz responses | D |
| C16 | Single and multiple choice quizzes embedded as classroom scenes | P |
| C17 | End-of-class completion page with saved quiz state | P |

## D. Classroom presentation and conversation

Source: [README, classroom and multi-agent interaction](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#multi-agent-interaction), [changelog 1.1.0](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/CHANGELOG.md#110---2026-09-24), [action engine description](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#key-architecture). Prior user vision explicitly preferred direct interaction and highlighting without simulated speakers or classmate conversation. These differences remain visible but are not adopted by this inventory.

| ID | Difference | State |
| --- | --- | --- |
| D01 | AI teacher lectures with narrated, timed slide actions | D |
| D02 | AI classmates and teacher hold proactive group discussion | D |
| D03 | Multi-persona roundtable debate during a lesson | D |
| D04 | Learner interrupts, joins, or is called on in classroom discussion | D |
| D05 | In-class teacher chat answers questions using the current slide | D |
| D06 | Teacher reads a specific slide element selected by the learner | D |
| D07 | Teacher reads a referenced interactive component and its current state | D |
| D08 | Teacher reads a referenced whiteboard element | D |
| D09 | Teacher searches the web during a classroom answer | D |
| D10 | Teacher draws diagrams, formulas, shapes, charts, and text on a shared whiteboard | D |
| D11 | Learner and agent can alter or clear whiteboard state during playback | D |
| D12 | Spotlight and laser pointer actions direct attention during narration | D |
| D13 | Action-level playback timeline and navigation within a scene | P |
| D14 | Immersive presentation mode and classroom keyboard shortcuts | P |
| D15 | Scene narration through multiple selectable TTS voices and providers | G |
| D16 | Microphone speech recognition for questions to the teacher | G |
| D17 | Voice registration or cloning through an optional configured provider | G |
| D18 | Audio prefetch while a prior discussion line plays | G |

## E. Editor and output production

Source: [README, Export](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#export), [changelog 0.3.1](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/CHANGELOG.md#031---2026-07-21), [editor package](https://github.com/THU-MAIC/OpenMAIC/tree/f2875426ae5712d26f0a76e54e9de763e86027a6/packages/%40openmaic/editor), [importer package](https://github.com/THU-MAIC/OpenMAIC/tree/f2875426ae5712d26f0a76e54e9de763e86027a6/packages/%40openmaic/importer). Itembank reads PPTX sources and exports course packages. Reading slide text is not slide-layout import, and a course package is not an editable deck or video.

| ID | Difference | State |
| --- | --- | --- |
| E01 | On-canvas slide drag, resize, rotate, and multi-select | G |
| E02 | Add and edit text by direct canvas action | G |
| E03 | Slide element picker and chat reference to a selected element | G |
| E04 | Slide navigation rail and visual scene thumbnails | G |
| E05 | Timeline editor for narration and scene actions | G |
| E06 | Import PPTX into editable slides while retaining position and style | G |
| E07 | Preserve PPTX charts, images, tables, text insets, arrows, and embedded videos during visual import | G |
| E08 | Export editable PowerPoint with images, charts, and converted LaTeX formulas | G |
| E09 | Export a standalone interactive HTML page | P |
| E10 | Export a playable classroom ZIP with scenes and embedded media | P |
| E11 | Import the classroom ZIP into browser or server storage | P |
| E12 | Inline CDN assets, fonts, images, KaTeX, Tailwind, and Three.js for offline interactive playback | P |
| E13 | Report assets that could not be inlined and remain remote URLs | P |
| E14 | One-click MP4 export of the whole course playback | G |
| E15 | Export narration script as Markdown or DOCX | G |
| E16 | Export subtitle files separately from video | G |
| E17 | Render-service preview of a generated scene | G |
| E18 | Video render queue status, admission control, resource budgets, and rejection reason in UI | G |

## F. Storage, deployment, providers, and localization

Source: [README, pluggable storage](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#pluggable-storage), [README, provider setup](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#2-configure), [storage package](https://github.com/THU-MAIC/OpenMAIC/tree/f2875426ae5712d26f0a76e54e9de763e86027a6/packages/%40openmaic/storage). Some are deployment choices rather than learner features. Itembank intentionally stores canonical learner files locally.

| ID | Difference | State |
| --- | --- | --- |
| F01 | Browser-only storage mode for courses, runtime state, KV settings, and assets | D |
| F02 | Swappable browser and server storage contracts for those object types | G |
| F03 | PostgreSQL server storage for courses, assets, learner runtime, sessions, materials, and skills | D |
| F04 | S3 option for server-managed media bytes | D |
| F05 | Multi-browser access to one server-persisted course | D |
| F06 | Owner-scoped folders, materials, course edits, and quotas | D |
| F07 | Optional single-tenant shared-owner deployment mode | D |
| F08 | Access-code gate for a shared web deployment | D |
| F09 | Docker Compose PostgreSQL stack and Vercel deployment route | G |
| F10 | Server-side config for many model and media providers | P |
| F11 | Per-generation-step model selection for outline, slides, interactive content, and actions | G |
| F12 | Separate image, video, search, ASR, and TTS provider pickers | G |
| F13 | One-key Token Plan presets for several multimodal gateways | G |
| F14 | Provider capability discovery and explicit force-off switches | P |
| F15 | Startup validation and fail-loud unresolved model routing | P |
| F16 | Local Lemonade LLM, image, TTS, and ASR integration | G |
| F17 | Local FunASR integration for speech-to-text | G |
| F18 | Search provider choices including Exa, SearXNG, Brave, Baidu, and Bocha | G |
| F19 | Usage dashboard and course model settings inside the web UI | P |
| F20 | Twelve interface locales across eleven languages | P |
| F21 | Browser-native narration with language detection | G |
| F22 | Dark mode in the classroom and workbench | P |

## G. Skill catalogue differences

Source: [24 agent-runtime skills](https://github.com/THU-MAIC/OpenMAIC/tree/f2875426ae5712d26f0a76e54e9de763e86027a6/skills/agent-runtime) and [OpenMAIC workbench skill](https://github.com/THU-MAIC/OpenMAIC/tree/f2875426ae5712d26f0a76e54e9de763e86027a6/skills/openmaic). These rows mean there is no equivalent **integrated runnable course operation** in itembank. Some topics already have a related playbook or planning contract, so the row is marked partial.

| ID | OpenMAIC built-in skill or skill facility | State |
| --- | --- | --- |
| G01 | Curriculum planner | P |
| G02 | Deep interactive scene authoring | G |
| G03 | Deep research for course generation | P |
| G04 | Fact check generated material | P |
| G05 | Feynman learning style | G |
| G06 | K-12 core literacy planning | G |
| G07 | Learning-to-learn treatment | G |
| G08 | Lecture style | G |
| G09 | Page cloning from a visual reference | G |
| G10 | PPTX import operation | G |
| G11 | Pro editing | G |
| G12 | Slide craft | G |
| G13 | Slide DSL authoring | G |
| G14 | Social-emotional learning treatment | G |
| G15 | Spiral curriculum planning | P |
| G16 | Stage design | G |
| G17 | Stage DSL authoring | G |
| G18 | Style cloning | G |
| G19 | Teacher-style cloning | D |
| G20 | Understanding by Design | P |
| G21 | Vocational course or task design | G |
| G22 | Workshop style | G |
| G23 | Zone of proximal development exercise design | G |
| G24 | Build a personal reusable skill | P |
| G25 | Standard OpenMAIC skill for hosted or self-hosted generation from external agent workbenches | G |
| G26 | OpenClaw messaging-app course generation and async completion link | G |

## H. Reusable packages and operational details

Source: [package tree](https://github.com/THU-MAIC/OpenMAIC/tree/f2875426ae5712d26f0a76e54e9de763e86027a6/packages), [README architecture](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/README.md#key-architecture), [changelog 1.1.1](https://github.com/THU-MAIC/OpenMAIC/blob/f2875426ae5712d26f0a76e54e9de763e86027a6/CHANGELOG.md#111---2026-09-27). These are candidate implementation assets or operation traits, not all independent learner promises.

| ID | Difference | State |
| --- | --- | --- |
| H01 | Published scene DSL package for slide, quiz, PBL, widget, and action content | G |
| H02 | Published React renderer package for that DSL | G |
| H03 | Published generation package with caller-supplied AI call function | P |
| H04 | Published editor package for visual slide manipulation | G |
| H05 | Published PPTX visual importer package | G |
| H06 | Published pluggable storage package | G |
| H07 | 21 classroom action types, including speech, drawing, spotlight, and laser | D |
| H08 | Provider requests guarded against redirects, DNS rebinding, and internal-address SSRF | P |
| H09 | Extraction size and decompression bounds for provider-returned archives | P |
| H10 | Sandboxed render service with network policy for untrusted scene HTML | G |
| H11 | Server asset-pool lifecycle and release after course deletion | P |
| H12 | Per-owner upload quota reservation and crashed-upload recovery | G |
| H13 | Generated-scene validation, bounded retries, and visible failure diagnostics | P |
| H14 | Stable per-scene revision events to synchronize open workbench views | P |

## I. Additions found across OpenMAIC forks

The [fork census](openmaic-forks-2026-09-27/CENSUS.md) records the public fork-network method and every ahead default branch. The [feature audit](openmaic-forks-2026-09-27/FEATURES.md) has pinned implementation links, original change links, and caveats for the 51 findings below, plus dispositions for other substantive leads. The source links here go to the fork's original change, making an implementation trial traceable. **A** means already present in itembank, **S** means source exists but the feature is dormant, alpha, or not verified as a usable flow. G, P, and D keep their meanings above. These rows compare against itembank and current upstream `f2875426`; a fork commit may be old or behind upstream even when its idea is useful.

| ID | Fork addition and original change | Itembank comparison |
| --- | --- | --- |
| I01 | [quintusr course-spec hierarchy, browse, and lesson generation](https://github.com/quintusr/openmaic/commit/1ce219f40596) | P: objective/course hierarchy exists; this browse and one-lesson build flow is not integrated. |
| I02 | [yunkongtech installable PWA and service worker](https://github.com/yunkongtech/Singularis-Study/commit/9ac634bdf761) | G: desktop Tauri and a browser UI exist; installable phone PWA does not. |
| I03 | [yunkongtech Doubao TTS](https://github.com/yunkongtech/Singularis-Study/commit/3d617fff58ca) and [voice/speed controls](https://github.com/yunkongtech/Singularis-Study/commit/b47594576edd) | P: Edge and Piper audio exist; these provider and playback controls do not. |
| I04 | [efcloud sentence-streamed, ordered agent speech](https://github.com/efcloud/OpenMAIC/commit/f8a7c4b7cb9a) | G: itembank does not stream spoken lessons while model text arrives. |
| I05 | [efcloud avatar video overlay](https://github.com/efcloud/OpenMAIC/commit/2fd137acd4bd) | D: simulated speakers are outside the current direct-lesson preference. |
| I06 | [efcloud nested IndexedDB course library](https://github.com/efcloud/OpenMAIC/commit/0efa1a293838) | P: course shelf exists; recursive drag/drop library editing does not. |
| I07 | [zhenzhu managed courses and chapters](https://github.com/zhenzhu143321/OpenMAIC/commit/f6e684fbb89d) and [public view](https://github.com/zhenzhu143321/OpenMAIC/commit/b068ce49085d) | P: local courses exist; publishing is a separate authorized operation. |
| I08 | [Sid standalone placement and coding quiz](https://github.com/Sid3548/OpenMAIC_sid/commit/eaa1548d6ede) | P: practice and coding foundations exist; this route is separate and its scorer conflicts with runtime authority. |
| I09 | [Sid interview practice turns and debrief](https://github.com/Sid3548/OpenMAIC_sid/commit/f69ddb752ec2) | G: a specialized interview activity is absent. |
| I10 | [TJUEZ PDF TOC/chunk summarization](https://github.com/TJUEZ/OpenMAIC/commit/92bfdaf91cc4) | P: PDF extraction exists; this generation-time summary path is absent and needs locator checks. |
| I11 | [chenhaodongHD browser-to-server course sync](https://github.com/chenhaodongHD/OpenMAIC/commit/d4d68f36c063) and [first-scene opening](https://github.com/chenhaodongHD/OpenMAIC/commit/d8eb05079a53) | D: automatic remote course copy needs explicit rights and egress authority. |
| I12 | [academeio medical competency search and quiz alignment](https://github.com/academeio/classroom/commit/baaf92cd82be) | P: blueprint alignment exists; this domain catalog and picker do not. |
| I13 | [academeio local Kokoro TTS](https://github.com/academeio/classroom/commit/b4e8c4428e73) | P: Piper is a local speech engine; Kokoro is another provider option. |
| I14 | [Chanry1 typed course-publishing manifest](https://github.com/Chanry1/AIWinHub-OpenMAIC/commit/41218e4a536b) | D: public publishing and external platform mapping need a separate product decision. |
| I15 | [Automationnow learner-only playback and single-file HTML](https://github.com/Automationnow/OpenMAIC/commit/5a8cf96ce609) | S: its HTML export menu was later removed; keep the code lead without claiming a shipped flow. |
| I16 | [Automationnow slide lock and single-page regeneration](https://github.com/Automationnow/OpenMAIC/commit/87e2f5028fbd) | P: Itembank has accepted revisions; it has no visual slide lock/regenerate control. |
| I17 | [Automationnow speech normalization](https://github.com/Automationnow/OpenMAIC/commit/ae1686b38f98) and [Voxtral TTS](https://github.com/Automationnow/OpenMAIC/commit/f4ea28d03ea3) | G: technical text and currency speech preparation plus this provider are absent. |
| I18 | [HeroAgent four classroom teaching modes](https://github.com/HeroAgent/OpenMAIC/commit/3b378e63ecd7) | D: classroom chat modes are a different learner interaction; a reusable treatment selector remains a possible adaptation. |
| I19 | [HeroAgent cloud sync](https://github.com/HeroAgent/OpenMAIC/commit/7672e61d05ce) | D: server sync is an explicit future operation; Bedrock from the same fork is already supported upstream. |
| I20 | [ade-karya OpenCode CLI and MCP agent harness](https://github.com/ade-karya/KelasKA/commit/ae19e8c4243e) | P: itembank has agent and MCP surfaces, but not this local CLI driver. |
| I21 | [adityapapu Gemini ASR](https://github.com/adityapapu/OpenMAIC/commit/6f1549690577), [Google Cloud TTS](https://github.com/adityapapu/OpenMAIC/commit/df05ebf3890a), and [learning-mode selector](https://github.com/adityapapu/OpenMAIC/commit/8561d513961a) | P: ASR is registered but lacks a backend; this provider and mode picker are absent. |
| I22 | [jfialloss school practice, XP analytics, and assignments](https://github.com/jfialloss/open_maic/commit/a9cacd6ce6bb) | P: assignments, evidence, and practice exist; these school-facing views differ. |
| I23 | [smartboyjia quotas and payments](https://github.com/smartboyjia/DeckMind/commit/4d84facb143f) | D: commercial account and billing infrastructure is outside local-first learner scope. |
| I24 | [layeshi audio-clocked blackboard and completeness gate](https://github.com/layeshi/OpenMAIC/commit/9e52d6c00da3) | G: timed stroke reveal with a deterministic coverage gate is absent. |
| I25 | [Soucieux local MLX speech service](https://github.com/Soucieux/OpenMAIC-Forked/commit/4080f885ad38) | P: local Piper audio exists; MLX is a provider choice. |
| I26 | [UnlimitedWand ordered sentence TTS queue](https://github.com/UnlimitedWand/OpenMAIC/commit/c31b22feb095) and [clip persistence](https://github.com/UnlimitedWand/OpenMAIC/commit/39f398f36f84) | G: no equivalent low-latency spoken lesson queue. |
| I27 | [Omitech semester workspace](https://github.com/OmitechTz/OpenMAIC/commit/cc71f90298ba), [Moodle XML export](https://github.com/OmitechTz/OpenMAIC/commit/1bafa4334b73), and [offline student assignment](https://github.com/OmitechTz/OpenMAIC/commit/2317a37b5622) | P: course assignments and packages exist; Moodle format and that student-safe delivery are gaps. |
| I28 | [leisurehuang generation phase and elapsed-time panel](https://github.com/leisurehuang/OpenMAIC/commit/1f15b9eef07d) | P: operation states exist; this course-generation canvas progress view does not. |
| I29 | [grechkainfo closed-network deployment recipe](https://github.com/grechkainfo-cloud/OpenMAIC/commit/1d2bd36df805) | D: enterprise deployment pattern, distinct from the local desktop product. |
| I30 | [chengyan1215 Electron desktop wrapper](https://github.com/chengyan1215/LyOpenMAIC/commit/28afb3dcd0be) | A: itembank already ships a Tauri desktop shell; no desktop gap is implied. |
| I31 | [Haizard chemistry/physics practical simulation generator](https://github.com/Haizard/OpenMAIC/commit/92d3f6cc0675) | P: interaction primitives exist; this domain template is source-supported but generated quality is untested. |
| I32 | [aharonyaircohen published-course learner portal](https://github.com/aharonyaircohen/OpenMAIC/commit/598dbd610f) | P: course shelf exists; multi-user publication and access gates differ. |
| I33 | [naixin exam snapshot, extraction, and review flow](https://github.com/naixin588/OpenMAIC/commit/feae8be97f) | P: exam runtime exists; scanned exam intake is partial, and the fork's judge cannot replace the scorer. |
| I34 | [faithleysath BYOK CLI and atomic `.maic` archive](https://github.com/faithleysath/OpenMAIC-CLI/commit/55b779b4b8) | P: itembank has CLI and package restore; archive layout and generator flow differ. |
| I35 | [tajo9128 typed knowledge-point mastery and progression](https://github.com/tajo9128/openlearn/commit/e28989da26) | P: evidence-informed next actions exist; the fork's separate mastery engine is only a strategy reference. |
| I36 | [page-xia checkpointed generation resume](https://github.com/page-xia/OpenMAIC/commit/af215e0784) | P: durable operations exist; this scene-generation resume route is absent. |
| I37 | [caojianatSZ scanned-paper OCR structure reconstruction](https://github.com/caojianatSZ/MAIC/commit/bedcac03e934) | P: OCR/source intake exists; bbox-based multi-question segmentation and handwriting separation do not. |
| I38 | [narthanaj SCORM 1.2 export sidecar](https://github.com/narthanaj/OpenMAIC/commit/b16a755106b3) | S: alpha code exists in the fork; itembank has no SCORM export or verified LMS import. |
| I39 | [sweetsora separate outline preview](https://github.com/sweetsora233/OpenMAIC/commit/ea13136fdfc8) and [feedback-driven scene regeneration](https://github.com/sweetsora233/OpenMAIC/commit/e65af5f2fb8a) | P: source/objective plans exist; the fork's separate preview and feedback route are absent. Generic outline editing already exists upstream. |
| I40 | [TianTianHang document-grounded slide revision](https://github.com/TianTianHang/OpenMAIC/commit/30ac7e5dcef2) and [insertion](https://github.com/TianTianHang/OpenMAIC/commit/0d64c2b6391b) | P: proposal review exists; this evidence panel and visual apply flow do not. |
| I41 | [evcgs WiseOCR PDF parser](https://github.com/evcgs/OpenMAIC/commit/1cb22b1ab8c6) | P: PDF/OCR intake exists; this remote parser adapter is an option, not a missing workflow. |
| I42 | [ViffyGwaanl bounded parallel scene generation](https://github.com/ViffyGwaanl/OpenMAIC/commit/968e585d893d) | G: no equivalent multi-scene generation scheduler is integrated. |
| I43 | [vcpandya expanded language selector](https://github.com/vcpandya/OpenMAIC/commit/eaaea08fd304) and [SM-2 review route](https://github.com/vcpandya/OpenMAIC/commit/74a76bf2cac0) | P: language breadth differs; itembank has review scheduling, and caller-provided scores cannot settle evidence. |
| I44 | [NahaLabs CAPS generation brief](https://github.com/Naha1981/NahaLabs-Online-Academy/commit/ab48f57492f3), [progress projection](https://github.com/Naha1981/NahaLabs-Online-Academy/commit/832983ec7235), and [source metadata](https://github.com/Naha1981/NahaLabs-Online-Academy/commit/62e39a3c0345) | P: Itembank has objective-linked courses and evidence; this curriculum-specific brief is an additional domain treatment. |
| I45 | [shervinemp course maintenance review and split-plan/apply flow](https://github.com/THU-MAIC/OpenMAIC/compare/f2875426ae5712d26f0a76e54e9de763e86027a6...shervinemp:main) | P: revision review exists; read-only semantic review and scene split controls differ. Confirm atomicity before reuse. |
| I46 | [ernesttan collaborator roles and invitations](https://github.com/ernesttan1976/OpenMAIC/commit/579156e6f5eb) | D: owner/editor/viewer sharing is a multi-user operation that needs explicit rights and identity. |
| I47 | [zquanjin-wq idempotent server RuntimeStore](https://github.com/zquanjin-wq/RJ-laixue/commit/5e6c1366ad12) and [conflict check](https://github.com/zquanjin-wq/RJ-laixue/commit/cbfd3b9104e0) | P: local runtime evidence is deterministic; this server persistence design is a comparison, not another scorer. |
| I48 | [bochendong problem import preview and commit](https://github.com/bochendong/Syntara/commit/6de05642db241600dfe230d0b843ca9407d4327b) | P: authoring proposals exist; this user-facing extracted-question selection flow is absent. |
| I49 | [DuanDaun Explore and My Courses shelves](https://github.com/DuanDaun520/OpenMAIC/commit/b4c1e80190d4dbeb44b3d3e02aa99fa19b117e05) | P: course shelf exists; author display, favorites, and learned-course groups differ. |
| I50 | [sixgodjson signed share links](https://github.com/sixgodjson/OpenMAIC/commit/117d4dd4e08e), [stage-bound access](https://github.com/sixgodjson/OpenMAIC/commit/8406e384e89f), and [export gate](https://github.com/sixgodjson/OpenMAIC/commit/3c80e3dbc73c) | D: sharing is an explicit future rights operation; the fork's static-secret fallback must not be reused. |
| I51 | [Afristrat local ComfyUI LTX video adapter](https://github.com/Afristrat/OpenMAIC/commit/4f6c6314799ae7bcde92ed2a6a281c69d328e159) | G: local video generation provider is absent; generated video itself remains outside the current core lesson flow. |

### Fork variants and overlaps retained for traceability

These additional substantive leads do not establish a new learner capability category beyond the rows above. Their exact source links are retained so a later provider, localization, or deployment pass can find the original code.

| ID | Fork source | Disposition |
| --- | --- | --- |
| J01 | [agosalesops accounts and completion routes](https://github.com/agosalesops-boop/OpenMAIC/blob/a675b097d4bcab58b8f8b5897667411a339dbc44/lib/persistence/accounts.ts) | D: multi-person accounts and learner completions are related to I46; itembank has assignments locally. |
| J02 | [ZHYYY208 Tauri Windows bundle](https://github.com/ZHYYY208/OpenMAIC-desktop/tree/bb76216d93ffb5a71f503d9b7ecaf8a5b86a733b/desktop/src-tauri) | A: itembank already has a Tauri desktop shell. |
| J03 | [sangcorp Piper adapter](https://github.com/sangcorp/OpenMAIC/blob/0ad45289576969a6032208a711a5fe8fc245d7d1/lib/audio/tts-providers.ts) | A: itembank already has Piper speech. |
| J04 | [ejang Gemini TTS](https://github.com/ejang/OpenMAIC/blob/aab44a0040cde939aafc4b9c4098387e8d20b151/lib/audio/tts-providers.ts) | P: another implementation of I21; Korean UI strings are already upstream. |
| J05 | [franz-fletcher Qwen TTS/ASR WebSocket pool](https://github.com/franz-fletcher/OpenMAIC/blob/0224efdd2e9435bccf88df6b88fff94c81e7b8dd/lib/audio/qwen-token-plan-ws.ts) | P: provider-specific speech variant of I03 and I21. |
| J06 | [phanlemanh ElevenLabs voice discovery](https://github.com/phanlemanh/OpenMAIC/blob/2a8c846ffe81aa1e449f2e993e271c9de25c71d7/app/api/elevenlabs-voices/route.ts) | P: provider voice catalog, within I03's controls. |
| J07 | [gyunt Codex account OAuth transport](https://github.com/gyunt/OpenMAIC/blob/e81e96560240b8afc3e77d8e9b690cfb4c4cedab/lib/server/codex-oauth.ts) | D: account-based model access would require a current API and terms check. |
| J08 | [neolaf2 CLI harness](https://github.com/neolaf2/OpenMAIC/tree/b081a4109758a92294e85410bc1f4209adb02b81/agent-harness) and [publisher skill](https://github.com/neolaf2/OpenMAIC/blob/b081a4109758a92294e85410bc1f4209adb02b81/skills/openmaic-course-publisher/SKILL.md) | P: agent transport and publishing variants of I20 and I14. |
| J09 | [kostas-neoset hosted MinerU adapter](https://github.com/kostas-neoset/OpenMAIC/blob/c78beac876e6c5e37e6006da0552f346ac389677/lib/pdf/mineru-hosted.ts) | P: additional remote parser for an existing intake category. |
| J10 | [groxaxo Inworld speech adapter](https://github.com/groxaxo/OpenMAIC/blob/2cc8b8c358af1f28dd3a778026bd4126da96d75c/lib/audio/inworld.ts) | P: voice-provider variant of I03. |
| J11 | [senthil-nz Tamil localization](https://github.com/senthil-nz/OpenMAIC/blob/3f9c504beefdc1b357ca0fa57b6f863070861515/lib/i18n/common.ts) | P: additional interface locale, not verified generated-lesson quality. |
| J12 | [dostonsulaymon local SDXL-Turbo images](https://github.com/dostonsulaymon/OpenMAIC-doston/blob/f895b44821dd8c6bd69486be445eb15b8978d435/lib/media/adapters/local-image-adapter.ts) and [Uzbek UI](https://github.com/dostonsulaymon/OpenMAIC-doston/blob/f895b44821dd8c6bd69486be445eb15b8978d435/lib/i18n/common.ts) | P: provider and localization variants. |
| J13 | [Peasy87 Socratic prompt builder](https://github.com/Peasy87/OpenMAIC/blob/efa94b6f858f5cef86d749a26beef0ec9c40eeaa/lib/orchestration/prompt-builder-socratic.ts) | A: itembank already has runtime-constrained guiding questions; this is a prompt variant. |
| J14 | [Afristrat wider tenant/course branch](https://github.com/Afristrat/OpenMAIC/tree/97bc4867b7e37ed11dc38111314cf1f3e57674f7) | S: I51 covers the verified video adapter; a distinct tenant-teacher flow was not isolated. |

The [feature audit's lead dispositions](openmaic-forks-2026-09-27/FEATURES.md#disposition-of-the-remaining-census-leads) explain these comparisons. The [census lead table](openmaic-forks-2026-09-27/CENSUS.md#substantive-fork-leads) retains source paths. Its [ahead-branch appendix](openmaic-forks-2026-09-27/CENSUS.md#other-ahead-default-branches) links every ahead default branch returned in this scan. Keep those as audit leads, not as features already tested or as requirements.

## What is already present, so it is not a gap

Itembank already has source adapters for several document types, objective and course structures, semantic lessons, a limited guided reader and deterministic interaction, a wider assessment protocol than OpenMAIC's three quiz response families, local evidence, pending short-answer review, Anki boundaries, local model configuration, course packaging, and a Tauri desktop shell. The current baseline is documented in [`STATE.md`](../STATE.md) and the earlier [capability matrix](competition-2026-09-08/ABSORPTION.md#capability-matrix-against-the-actual-product). The unmerged typed-answer candidate in `STATE.md` is not treated as integrated `main` behavior.

## Limits and next use

This is a source and code inventory. It does not establish that OpenMAIC or a fork succeeds on an identical real source, preserves citations, teaches better, meets accessibility needs, or restores offline without loss. The earlier [hands-on trial](competition-2026-09-08/HANDS-ON.md) had partial generation and unequal conditions. The fork census resolved 6,074 public default-branch tips, found 287 ahead branches, and left 43 fork rows unresolved because GitHub stopped exposing their tips; it did not inspect private forks, non-default branches, or copies outside GitHub's fork network. The next pass should attach a small representative course to these IDs, mark each as verified in the live UI or merely code-supported, then select adoption candidates by teaching value and compatibility. Current user vision prefers direct interactive learning over simulated classroom conversation; that preference remains a decision input, not a reason to omit D rows.

No product code, contracts, skills, or accepted course files changed in this pass. The fork census and feature audit are separate research records; removing the three research documents reverses this pass.
