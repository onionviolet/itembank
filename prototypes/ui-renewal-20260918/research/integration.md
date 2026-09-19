# UI renewal integration audit

Date: 2026-09-18

Scope: read-only architecture audit of the working checkout, followed by this research note. No production files, settings, courses, banks, sessions, or evidence were changed. Existing dirty work was preserved. Findings are based on current source, not an installed-app or browser observation. Tests were identified but not executed because this task changed no implementation.

The renewal can replace the complete presentation system without replacing the parser, runtime, course model, routes, evidence store, or desktop container. The existing CSS is a migration liability, not a design requirement. Build the candidate without importing it, then connect the accepted design at the existing read-model and operation boundaries.

## I1. Establish a clean style boundary before integrating screens

**Verified:** the current presentation is assembled from overlapping global style layers.

| Entry point | Current behavior | Leakage risk |
| --- | --- | --- |
| `surfaces/presentation.py:90`, `SHARED_CSS` | Defines global `body`, headings, links, `.card`, `.actions`, `.surface`, spacing, typography, and primitives | Importing it imports the old visual grammar even when only tokens were wanted |
| `surfaces/presentation.py:471`, `PRODUCT_CSS` | Redefines global `body`, headings, buttons, and `.surface`. Hides `.app-nav`. Adds fixed or sticky navigation | A new composition can inherit hidden navigation, old serif headings, width limits, and sidebar offsets |
| `surfaces/presentation.py:665`, `surface_shell` | Emits theme, product aliases, shared CSS, product CSS, extra CSS, then palette CSS | Passing a new `extra_css` makes the candidate an override layer on top of legacy rules |
| `surfaces/theme.py:317`, `theme_css` | Returns both derived palette tokens and `looks.look_css(...)` | A request for theme tokens also imports global shape rules |
| `surfaces/looks.py:396`, `look_css` | Returns selectors such as `body`, `h1`, `.card`, `.stem`, `.choice`, and course navigation rules | Old look selections can change new layouts without the new component opting in |
| `surfaces/quiz.py:398` | Appends product CSS and more `.wrap`, `.card`, `h1.stem`, and `.choice` overrides | Quiz appearance has a separate late cascade |
| `surfaces/lesson.py:25`, `product_reader_css` | Imports product CSS and adds reader widths and mobile padding | A lesson can acquire shell rules through a helper that sounds reader-specific |

**Recommendation, not implementation:** introduce one versioned presentation selection at document assembly. A renewed document receives renewed base rules, tokens, components, and its surface rules. A legacy document receives its current stack. Do not load both stacks and try to out-specify one. During migration, retained legacy content needs an explicitly bounded compatibility region or an unrenewed document, rather than global legacy CSS.

Extract a token-only palette function from the current theme derivation for integration. Keep persisted mode and accent semantics, while allowing the new design to choose new type, spacing, shape, and composition tokens. A prototype should define its own candidate tokens until that integration exists. Do not use `theme_css` as a supposedly neutral import.

**Minimal gate:** generated renewed documents contain no legacy `SHARED_CSS`, `PRODUCT_CSS`, look shape blocks, or old template style body. Verify computed styles on a course page, reader, quiz, and settings page. Check class collisions such as `.card`, `.row`, `.wrap`, and `.actions` explicitly.

## I2. Replace composition across all document assembly paths

**Verified:** a change to `surface_shell` alone will not renew the application.

| Surface | Concrete seam |
| --- | --- |
| Shelf and course areas | `surfaces/daemon.py`, `_course_shelf_body`, `_course_frame`, `_course_area_rows`, `_course_rows_html`, `_course_area_extra`, `handle_courses_get` |
| Common document shell | `surfaces/presentation.py`, `surface_shell`, `_product_sidebar`, `product_frame_open`, `standalone_product_nav` |
| Quiz | `surfaces/quiz.py` template replacement chain around lines 391-410 and `surfaces/quiz_page.py`, `TEMPLATE` |
| Reader | `surfaces/lesson.py`, `LESSON_TEMPLATE`, `LESSON_CSS`, `product_reader_css`, template replacement around lines 2786-2794 |
| Study | `surfaces/study.py`, `STUDY_CSS`, `study_page`, which calls `surface_shell` |
| Settings | `surfaces/theme.py`, `theme_page`, `SETTINGS_CSS`, `_settings_preview_css` |
| Runtime unavailable and status windows | `scripts/gen_shell_assets.py`, `SHELL_CSS`, generated `src-tauri/assets/runtime-not-ready.html` and `runtime-status.html` |

The current `surface_shell` identifies active main navigation by page-title string and extracts a leading `<nav class="app-nav">` from body markup. These are existing implementation details, not ideal contracts for a renewed shell. `_course_frame` already gets structured navigation entries, current area, notice, and next action from state.

**Recommendation:** make shell inputs explicit: active global destination, course context, current area, page title, primary action, and content. Keep route identity in the existing IA and daemon structures. Pass semantic content and public runtime state to surface renderers. Share the renewed shell and components across course pages, learning pages, operations, and recovery pages. Avoid string inspection for navigation selection.

**Minimal gate:** a connected synthetic journey covers shelf, course overview, Learn, source reading, lesson, practice, feedback, next question, evidence, settings, and recovery. Each screen uses the same navigation and component rules. Test deep links and back navigation, not only a showcase home page. Exported and standalone files require a coherent shell appropriate to their available destinations.

## I3. Preserve authority at existing read-model and operation seams

**Verified:** the binding contract permits replacing presentation composition while keeping canonical models and operation ownership. `SOURCE-TO-COURSE.md`, sections “Product experience and delivery” and “Learner experience”, names the course as the primary object and the Tauri shell as a client of the local runtime. It explicitly separates presentation profiles from appearance settings and forbids an extension from adding a second route catalogue, scorer, evidence store, permission system, or recovery authority.

`surfaces/presentation.py:888`, `SURFACE_ADAPTERS`, documents useful existing seams. The question renderer consumes `runtime.public_item` plus runtime-owned state. Course areas consume IA read models. `semantic_view` at line 948 constructs a profile-neutral presentation view. These declarations do not prove that all views already expose every datum a new UI needs.

`surfaces/daemon.py:404`, `ROUTES`, remains the dispatch catalogue. It includes normal pages, answer posts, lesson checks, skip operations, glossary requests, course reading routes, and course areas. Existing handlers own validation and dispatch to runtime or course operations. `_course_frame` already distinguishes unavailable or empty state and supported recovery actions.

**Recommendation:** render from these existing projections and dispatch through existing operations. Add missing presentation data to the responsible public projection when necessary. Do not scrape old rendered HTML, read keyed banks in a new browser client, duplicate item parsing, infer mastery, or treat local presentation state as completion evidence. Keep provisional, pending, unavailable, unknown, and empty states distinct. Preserve current glossary and hint disclosure gates even if their controls move.

**Minimal gate:** compare available actions and runtime projections across old and renewed rendering for the same synthetic state. Run the owning served-session, scoring, hint, lesson, and course-route checks when those paths are integrated. Include pending prose, delayed feedback, short-answer review, glossary refusal, repeat submission, stale operation, and recovery. A layout change must not alter session IDs, item IDs, hashes, answer order, cursor progression, or durable evidence.

## I4. Design for the installed app and package the actual assets

**Verified:** `src-tauri/tauri.conf.json` opens at 1100 by 760, with minimum size 768 by 512. `src-tauri/src/main.rs`, `spawn_and_connect`, launches the sidecar, starts the proxy, and navigates the WebView to its loopback root. `src-tauri/src/proxy.rs` forwards to the daemon and injects the per-launch token. It deliberately holds no route catalogue. Normal learner pages come from the daemon, not a second application hosted in `frontendDist`.

`build.py`, `STAGE_FILES`, `STAGE_DIRS`, and `stage`, control zipapp inclusion. Directories currently include `surfaces`, `schemas`, `styles`, `fonts`, and `vendor`. `scripts/build_shell_macos.sh` separately freezes the sidecar and explicitly adds schemas, styles, and fonts. `scripts/gen_shell_assets.py` generates recovery pages from `THEME_CSS`, with its own CSS. Its generated pages do not automatically receive a newly designed normal-page shell.

**Inference:** a new external JS or CSS directory could work in source development while being absent from one distributable. This audit did not build either package or verify a particular missing asset. The separate staging mechanisms make that a concrete migration risk.

**Recommendation:** keep the new application served through the existing daemon and Tauri proxy. Add candidate asset delivery to the existing route and packaging ownership. Vendor required assets locally. Include runtime startup, crash, reconnect, and settings appearance in the design scope. Use the 1100 by 760 app window as a primary composition target, then verify its minimum size and browser reflow.

**Minimal gate:** source-daemon rendering, packaged-daemon rendering, and installed Tauri WebView rendering must load the same renewed assets without a development server or network fetch. Verify one lesson with math, one interactive question, a course page, a settings page, and the runtime unavailable page. Keep source, packaged, installed, and human-acceptance evidence separate.

## I5. Revise legacy visual assertions while retaining behavioral gates

**Verified:** `tests/stylesheet_roundtrip.py`, `check_frozen_type_tokens`, enforces the old five-size scale as exact values. The same module checks density bounds, contrast, token completeness, fonts, and CSS structure. `tests/presentation_roundtrip.py` includes font ownership, shared shell, fallback, and theme assertions. Exact visual tokens and markup snapshots are different from accessibility, runtime, and routing guarantees.

`AGENT-WORKFLOW.md`, “Fresh evaluation of prior choices”, directs audits to establish current needs before using old solutions to narrow alternatives. Old accepted appearance is therefore evidence of the current implementation, not proof that a redesign must retain its exact dimensions or typography.

**Recommendation:** after the user accepts a visual direction, revise the corresponding design contract and visual assertions in one bounded migration. Preserve or strengthen tests for readable contrast, keyboard behavior, touch targets, reduced motion, reflow, disclosure, valid routes, and useful script-free output. Do not retain a weak layout solely to satisfy its snapshot. Do not delete semantic tests merely because the visual design changes.

The smallest useful gate sequence is:

1. Capture generated-document and route baselines against synthetic content, then run `presentation_profiles_roundtrip.py`, `course_shell_roundtrip.py`, and affected IA checks after integration.
2. Run theme and stylesheet gates against the accepted new token contract, including System, Light, Dark, OLED, accent, look compatibility, and preview isolation.
3. Verify learner continuity with the owning served-session, hint, lesson, and JavaScript checks, including explicit Next question focus and script-free paths.
4. Verify rendered keyboard order, visible focus, scroll restoration, 200 percent zoom, narrow reflow, contrast, and reduced motion across representative surfaces. Human screen-reader and touch acceptance remain separately recorded.
5. Run required preflight and packaging gates for the implementation change, then inspect the installed app. Record pre-existing dirty-tree or environment failures separately from candidate regressions.

## Limits and provenance

This is a bounded source audit. Large modules were sampled around the symbols named above. It did not inspect all daemon handlers, every question widget, full course operation internals, the complete IA implementation, Windows packaging, browser state, or the installed bundle. No claim of exhaustive accessibility, test success, or visual quality is made.

Relevant prior memory was used to target the theme-preview ownership audit. Current source was inspected to verify theme derivation, preview helper location, product token aliases, and separate document composition. The prior installed-app result was not treated as current evidence. Memory pointer: `MEMORY.md:1240-1251`, source session `01a0a38d-0d16-7e43-bcdc-4eaa127f4230`.

Disposition: all recommendations in this note are proposed integration inputs. No new production contract, schema, settings value, dependency, or migration was accepted by this audit.
