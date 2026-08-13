# Stream 10: Visual experience and interaction system

**Research date:** 2026-08-13

**Access date for every external source:** 2026-08-13

**Scope:** Phase 16 research input for the Phase 17 visual system. This report
does not select a framework or authorize implementation.

**Evidence labels:** **FACT** is directly supported by a cited source or the
shipped repository. **INFERENCE** interprets facts for itembank. **RECOMMENDATION**
is a proposed product decision. **OPEN** needs a prototype, measurement, or user
choice.

**Copyright posture:** this report extracts general patterns and system
principles. It does not reproduce protected layouts, product assets, branding,
illustrations, or interaction details.

## 1. Scope and research questions

This stream asks how the complete packaged app can feel coherent, appealing,
readable, responsive, accessible, and trustworthy across sustained learning and
authoring. It covers the course shelf, sources, course map, lessons, notes,
questions, tests, evidence, authoring, diffs, agent activity, settings,
diagnostics, empty states, errors, and offline states.

The governing questions are:

1. Which visual hierarchy can join quiet reading, focused assessment, dense
   evidence, and consequential authoring without making them look like unrelated
   applications?
2. Which typography, spacing, color, surface, icon, imagery, diagram, motion,
   density, theme, focus, selection, progress, status, feedback, and transition
   rules deserve shared tokens and primitives?
3. How should the same content and task flow adapt to desktop, touch, narrow
   screens, zoom, high contrast, reduced motion, screen readers, keyboards,
   localization, long content, and offline operation?
4. Which visual choices make learning easier to orient to, and which merely add
   novelty, decoration, or false motivation?
5. What must Phase 16 fix semantically before Phase 17 styles it, what should
   remain configurable, and what requires a reversible prototype?

### Out of scope

- Final brand identity, logo, illustrations, marketing site, or product name.
- Copying a competitor theme, page composition, icons, or visual assets.
- Selecting a JavaScript or desktop UI framework.
- Changing scoring, feedback entitlement, evidence authority, or the portable
  lesson grammar.
- Treating visual polish as evidence that a lesson teaches well.

## 2. Existing itembank research and shipped behavior

### 2.1 Relevant local evidence inventory

| Local source | Existing finding or shipped contract | Status for this stream |
|---|---|---|
| `.planning/SOURCE-TO-COURSE.md` | The course is the user-facing object. Learn, Practice, Test, Sources, Course map, and Build/review are coherent areas. Continuous reader and guided presentation share durable authored content. | Binding product direction. |
| `.planning/PLANNING-DIRECTIVES.md` sections 4, 4a, and 8 | One parser, scorer, and evidence store remain fixed. Accessibility gates bind. Phase 16 defines logical behavior; Phase 17 defines and implements the visual language. | Binding boundary. |
| `.planning/UI-SPEC.md` | Activity first, evidence before inference, progressive disclosure, calm progress, same loop with varied media, and honest degradation. It defines shared shell, state, accessibility, density, and authority patterns. | Binding shared UI contract unless later synthesis explicitly revises it. |
| `.planning/research/2026-08-09-visual-design.md` | Proposed “Paper & Ledger”: serif authored content, duospace runtime assertions, system UI chrome, and restrained near-neutral surfaces. It warned against generic card grids and celebration motion. | Strong prior recommendation, not a final Phase 17 decision. |
| `.planning/research/2026-08-09-lesson-display-editor.md` | Reader/editor research supports readable measure, continuous reading, semantic lesson blocks, and editor/preview coordination. | Reuse for lessons and authoring. |
| Phase 3 and 3.1 research, UI specs, and implementation | Lessons, terms, semantic callouts, figures, tables, code, glossary interactions, Source Serif 4, and iA Writer Quattro already exist. Rich blocks must retain a useful plain-file form. | Shipped foundation. |
| Phase 4 research, UI spec, and implementation | One palette, contrast-correct derived accents, light/dark/system themes, shared focus/status rules, a small type and spacing system, reduced motion, and responsive shells. | Shipped foundation. Extend, do not casually replace. |
| Phase 5, 6, 6.1, 6.2, and 9 UI specs | Code, hint, visual assessment, gated lesson, math, and table states already specify public/private boundaries, keyboard and touch equivalents, focus, 320px/200% behavior, and honest fallbacks. | Preserve in visual prototypes. |
| Phase 10 and 11 UI specs | Evidence and recommendations must expose denominators and uncertainty. Authoring must distinguish sources, synthesis, findings, draft, validation, diff, approval, publish, and undo. | The visual system must support dense, consequential work. |
| Phase 13 UI spec | The packaged desktop shell is not a new application architecture. Browser fallback remains part of delivery. | Avoid native-only visual assumptions. |

### 2.2 Shipped visual behavior, verified in source

**FACT, repository:** `surfaces/theme.py` is the single palette derivation
source. It ships light and dark neutral surface tokens, fixed semantic success,
error, and warning tokens, and derives accessible accent and soft-accent values
from one persisted source color. It checks 4.5:1 text pairings and reports 3:1
focus pairings. Derived values are not persisted.

**FACT, repository:** `surfaces/presentation.py` owns shared CSS and font roles.
Source Serif 4 is the paper voice, iA Writer Quattro is the ledger voice,
system UI is chrome, and system monospace is code. The shipped lesson renderer
uses semantic HTML for headings, terms, callouts, figures, code, and tables.

**FACT, repository:** `surfaces/quiz_page.py` uses a centered 800px shell, one
sticky context line, one dominant stem, native response controls, 44px targets,
visible focus, a reserved feedback area, and semantic selection/verdict colors.
The quiz is currently card-heavy because the active item and many options each
use bordered surfaces.

**FACT, repository:** `surfaces/study.py` uses the same palette but has its own
component CSS. It exposes Flashcards and Learn modes, a progress bar, semantic
reveals, native disclosures for rationales, reduced-motion detection, and a
single-column narrow layout.

**FACT, repository:** shipped and planned UI contracts repeatedly test 1280,
768, 375, and 320 CSS-pixel widths, 200% zoom, keyboard-only use, reduced
motion, dark/light presentation, screen-reader status, long text, and no
page-level horizontal scroll. Wide tables, math, code, and diffs may scroll in
labeled local regions.

**INFERENCE:** itembank does not need a visual reset. Its strongest existing
assets are unusually aligned with the product thesis: typography already
distinguishes authored material, deterministic records, interface chrome, and
code; the theme already separates accent from assessment semantics; and the UI
contracts already define calm rather than gamified progress. The gap is system
completion and cross-surface composition, not a lack of visual ideas.

**INFERENCE:** the current implementation still reads as a set of separately
styled pages. Shared palette and typography are necessary but insufficient.
Navigation anatomy, density, surface hierarchy, state grammar, icons, charts,
empty/error/offline presentation, and transitions need one explicit system.

## 3. External sources

All links below were accessed 2026-08-13. Product behavior is documented from
primary product or design-system sources. Research sources are peer-reviewed or
standards-based where available.

### 3.1 Standards and research

| Source and direct link | Type | Relevant evidence and limits |
|---|---|---|
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and W3C explanations for [reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html), [focus appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html), [target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), and [status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) | Normative standard plus non-normative explanations | Establishes minimum accessibility outcomes. It does not prescribe a brand, exact component library, or a 44px house target. |
| [WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/) | W3C interaction patterns | Supports native semantics first and documented keyboard behavior for complex widgets. Pattern examples are guidance, not a substitute for user testing. |
| [W3C Making Content Usable for People with Cognitive and Learning Disabilities](https://www.w3.org/TR/coga-usable/) | W3C guidance | Supports clear purpose, familiar patterns, understandable feedback, and reduced cognitive burden. It addresses a broad population, so individual needs can conflict. |
| [W3C Internationalization: Designing for readability](https://www.w3.org/International/techniques/developing-specs.en?open=readability) | W3C internationalization guidance | Reminds designers that writing systems differ in line breaking, emphasis, direction, and typographic conventions. It does not define product-specific translation policy. |
| [de Koning et al., 2009, “Towards a Framework for Attention Cueing in Instructional Animations”](https://doi.org/10.1007/s10648-009-9098-7) | Peer-reviewed review | Cueing can direct attention, but effectiveness depends on what is cued and how it supports the task. This does not justify decorative animation. |
| [Rey, 2012, “A Review of Research and a Meta-Analysis of the Seductive Detail Effect”](https://doi.org/10.1016/j.edurev.2012.05.003) | Peer-reviewed review and meta-analysis | Irrelevant but interesting details can impair learning under some conditions. Study heterogeneity limits a simple “all decoration is harmful” rule. |
| [Mayer and Johnson, 2008, coherence principle boundary conditions](https://doi.org/10.1016/j.learninstruc.2007.09.002) | Peer-reviewed experimental research | Relevant explanatory material can help, while extraneous additions can hurt. The result concerns instructional content, not every visual ornament in software. |
| [Dyson, 2004, “How Physical Text Layout Affects Reading from Screen”](https://doi.org/10.1080/01449290410001715714) | Peer-reviewed review | Screen-reading layout findings vary with task and manipulation. The review supports treating line length and layout as empirical design variables, not claiming one universal optimum. |

### 3.2 Design systems and complete tools

| Source and direct link | Type | Observed pattern |
|---|---|---|
| [Material Design 3 typography](https://m3.material.io/styles/typography/overview) | Primary design-system documentation | Named type roles allow consistent hierarchy across varied surfaces. Material is a vocabulary reference, not an aesthetic target. |
| [Fluent 2 typography](https://fluent2.microsoft.design/typography) | Primary design-system documentation | Type ramps attach styles to semantic roles and emphasize readable hierarchy across Microsoft contexts. |
| [GitHub Primer typography](https://primer.style/product/getting-started/foundations/typography/) | Primary design-system documentation | A compact scale and role-based utilities support dense productivity interfaces. |
| [Atlassian design tokens](https://atlassian.design/foundations/tokens/) | Primary design-system documentation | Tokens encode decisions by semantic role and theme, separating intent from raw values. |
| [Apple Human Interface Guidelines: typography](https://developer.apple.com/design/human-interface-guidelines/typography) and [motion](https://developer.apple.com/design/human-interface-guidelines/motion) | Primary platform guidance | Text should respond to user sizing and motion should clarify relationship or feedback without becoming gratuitous. Platform advice must be adapted for a cross-platform web surface. |
| [Tufte CSS](https://edwardtufte.github.io/tufte-css/) | Primary open-source publishing implementation | A restrained reading system can create hierarchy through measure, typography, figures, notes, and whitespace rather than many interface containers. Its margin-note layout is not directly portable to narrow screens. |
| [Practical Typography, “Summary of key rules”](https://practicaltypography.com/summary-of-key-rules.html) | Practitioner publishing guidance | Offers bounded starting ranges for body size, line spacing, and line length. These are informed conventions rather than universal accessibility thresholds. |
| [Readium CSS](https://readium.org/css/) | Primary open-source digital-publishing project | Reader preferences, writing-system support, pagination/scroll choices, and publication styles require a deliberate override boundary. itembank should borrow interoperability concerns, not duplicate an EPUB renderer. |
| [VS Code UX Guidelines](https://code.visualstudio.com/api/ux-guidelines/overview), [status bar](https://code.visualstudio.com/api/ux-guidelines/status-bar), and [notifications](https://code.visualstudio.com/api/ux-guidelines/notifications) | Primary product extension guidance | Dense creative tools reserve status surfaces for compact contextual information and discourage noisy notifications. This is useful for agent activity and diagnostics. |
| [Obsidian CSS variables reference](https://docs.obsidian.md/Reference/CSS+variables/CSS+variables) and [CSS snippets](https://obsidian.md/help/Extending+Obsidian/CSS+snippets) | Primary product documentation | A durable content workspace can expose extensive theming while keeping Markdown files independent of a theme. itembank should offer bounded variables, not promise arbitrary CSS compatibility. |
| [Khan Academy Wonder Blocks](https://github.com/Khan/wonder-blocks) | Primary open-source design-system repository | A learning product can share accessible components, tokens, icons, and typography across many experiences. Repository documentation does not prove learning effectiveness. |
| [Open edX Paragon](https://paragon-openedx.netlify.app/) | Primary open-source design system | A broad education platform benefits from documented components and accessibility behavior, but its catalog breadth also warns against component accumulation. |
| [JupyterLab interface](https://jupyterlab.readthedocs.io/en/stable/user/interface.html) | Primary open-source product documentation | Dockable panels, documents, tabs, command palette, and status affordances support complex creation. That flexibility increases density and mode-management cost. |
| [NotebookLM overview](https://support.google.com/gemininotebook/answer/16269187) | Primary product help | Source-grounded notebooks combine sources, generated study artifacts, and assistance. Its notebook/chat framing is evidence for source visibility, not itembank’s primary navigation model. |
| [GitHub keyboard shortcuts](https://docs.github.com/en/get-started/accessibility/keyboard-shortcuts) | Primary product documentation | Mature productivity tools make keyboard access discoverable and allow shortcut behavior to respect assistive-technology needs. |

## 4. Observed facts, inference, recommendation, and open questions

### 4.1 Facts

1. **FACT:** WCAG 2.2 requires reflow without loss of information or
   functionality at the specified narrow equivalent, with exceptions for
   content that genuinely needs two-dimensional layout. It also defines
   contrast, focus, target-size, and programmatically determinable status
   outcomes.
2. **FACT:** mainstream design systems use semantic roles and tokens rather
   than styling every screen independently. Material, Fluent, Primer, and
   Atlassian vary aesthetically but converge on role-based type and color.
3. **FACT:** creative and productivity tools such as VS Code and JupyterLab
   support dense work through persistent navigation, panels, commands, status,
   and context rather than by turning every datum into a large card.
4. **FACT:** itembank already has durable Markdown, semantic lesson blocks,
   shared colors and fonts, assessment-specific states, and accessibility
   contracts. It also already vendors key type and math/editor assets.
5. **FACT:** learning research does not support decoration as a general path to
   better learning. Attention cues can help when task-relevant; extraneous
   material can hurt under some conditions.

### 4.2 Inferences

1. **INFERENCE:** the visual system should organize attention around the
   current learning or authoring act, not around a collection of widgets.
2. **INFERENCE:** one low-chroma shell can accommodate diverse subject media if
   subject identity appears in content, diagrams, and a restrained course
   accent rather than separate shells.
3. **INFERENCE:** authoring and evidence need greater information density than
   guided lessons. A single fixed density would either clutter learning or
   cripple professional work.
4. **INFERENCE:** visual distinction between source, authored explanation,
   generated synthesis, runtime verdict, and pending review is part of trust,
   not merely branding.
5. **INFERENCE:** a visual system optimized only for screenshots will fail on
   long lessons, large diffs, many sources, localization, and degraded states.

### 4.3 Recommendations

1. **RECOMMENDATION:** evolve the shipped “Paper & Ledger” foundation into a
   system called **Quiet Workbench** for planning purposes. “Paper” remains the
   reading field; “ledger” remains deterministic and provenance information;
   “workbench” adds dense, resizable, task-oriented authoring and evidence
   regions without adopting a generic IDE aesthetic.
2. **RECOMMENDATION:** use semantic tokens and primitives, not per-page CSS, as
   the Phase 17 unit of implementation and visual QA.
3. **RECOMMENDATION:** offer comfortable and compact density modes at the app
   level, with a focused reading mode that is a layout state rather than a third
   density system.
4. **RECOMMENDATION:** reserve motion for spatial continuity, causality, and
   progress in an initiated operation. Do not animate correctness, rewards,
   tier arrival, reading content, or agent “thinking.”
5. **RECOMMENDATION:** represent progress with path position, completed work,
   due work, evidence sufficiency, and explicit unknowns. Never infer a global
   mastery percentage or open-ended field completion.

### 4.4 Open questions

1. **OPEN:** should lesson body default to 18px or remain the shipped 16px body
   token with a reader preference? Test Source Serif 4 at 100%, 125%, 200%, and
   narrow widths with long EMT, mathematics, and computer-science fixtures.
2. **OPEN:** should users select comfortable/compact globally, per workspace,
   or per surface? A global default plus per-surface temporary override is the
   leading option.
3. **OPEN:** is a left navigation rail plus contextual right inspector still
   usable at 1024px with browser zoom, or should the inspector replace the
   rail? Prototype before locking breakpoints.
4. **OPEN:** which diagram rendering stack satisfies static fallback,
   accessibility, localization, offline packaging, and authorability without a
   second semantic model?
5. **OPEN:** should high contrast be an explicit itembank theme in addition to
   respecting platform forced-colors behavior? Both may be useful but must not
   drift into two separate state grammars.

## 5. Pattern inventory

| Pattern | Benefits | Weaknesses and misuse | Applicability to itembank |
|---|---|---|---|
| Semantic token layers | Themeable, testable, consistent, and separates intent from values. | Token sprawl can hide arbitrary values behind names. | High. Extend the shipped palette into elevation, typography, density, motion, chart, and status roles. |
| Serif reading field plus sans chrome | Makes long-form authored material distinct from controls; already shipped. | Poor serif rendering or too many typefaces can reduce coherence. | High. Keep Source Serif 4 for sustained prose and stems where appropriate. |
| Ledger voice for deterministic records | Makes provenance, counts, IDs, runtime state, and diffs visibly distinct. | Monospace or duospace at paragraph length can feel mechanical and consume width. | High for labels and records, low for long explanations. |
| Persistent course navigation | Maintains place across Learn, Practice, Test, Sources, Map, and Build/review. | A permanent sidebar can starve reading width and narrow screens. | High on desktop. Collapse to top-level switcher and drawer on narrow screens. |
| Contextual inspector | Keeps sources, definitions, hints, evidence, and agent activity adjacent to the task. | Can become a dumping ground or a second attention stream. | High when tied to current selection and absent when empty. |
| Continuous document canvas | Supports long reading, source comparison, selection, annotation, and print-like rhythm. | Harder to stage a guided sequence or reserve focus. | Required as reader mode. Guided mode uses the same content with staged sections. |
| Flat lists with separators | High information density and good scanning. | Can feel austere and needs strong typography. | Prefer for sources, objectives, findings, agent events, settings, and diagnostics. |
| Cards | Useful for independently actionable objects and course covers. | Excessive nesting fragments hierarchy, wastes space, and creates “dashboard soup.” | Use for course shelf items, one recommended next action, and bounded modal decisions. Avoid for every paragraph, option, source, and metric. |
| Tabs | Efficient for peer views with stable labels. | Hide information, wrap badly in localization, and are poor for sequential steps. | Use for Learn/Practice/Test peers or editor/preview/diff, not for a lesson sequence. |
| Disclosures | Progressive detail with native semantics. | Overuse creates hidden-content archaeology and repeated open/close work. | Use for secondary evidence, rationale, diagnostics, and advanced settings. Keep the next action visible. |
| Split view | Supports source/lesson, edit/preview, and current/proposed comparisons. | Narrow and zoomed layouts cannot sustain equal columns. | Desktop enhancement only. Stack in semantic order and preserve focus on narrow screens. |
| Command palette | Fast keyboard access across many actions. | Invisible to novices and can become the only path. | Prototype for navigation and authoring; every command still needs a visible route or CLI twin. |
| Status bar | Compact home for offline state, agent operation, diagnostics, branch/version, and pending writes. | Easily becomes noisy, cryptic, or falsely reassuring. | Desktop compact mode only. Critical or actionable status stays near the affected task. |
| Inline status | Places feedback beside the initiating control and works with live regions. | Repeated announcements or shifting layouts can disrupt. | Default for scoring, saves, source indexing, running code, and agent operations. Reserve space where predictable. |
| Skeleton loading | Suggests structure during remote fetch. | Creates visual churn, misrepresents duration, and is unnecessary for local fast states. | Reject as default. Use text status with determinate progress when known. |
| Illustrations | Can orient, explain, or reduce intimidation. | Decorative art adds asset, cultural, localization, and coherence cost. | Use only as cited instructional imagery, course cover choice, or a tested empty-state aid. Never as a substitute for guidance. |
| Icons plus labels | Improves recognition while preserving meaning. | Icon libraries can import foreign visual identity; icon-only controls are ambiguous. | Adopt one neutral, open, pinned icon set or a small custom semantic set. Label primary and unusual actions. |
| Node-link course map | Reveals prerequisites, branches, and gaps. | Dense graphs become unreadable and inaccessible; visual proximity can imply unsupported relationships. | Provide focused graph views plus outline/table alternative. Never use one giant “knowledge galaxy.” |
| Charts with summaries and tables | Show trends and retain exact accessible values. | Tiny sparklines and unlabeled color series imply precision and hide denominators. | Use only when trend or comparison is the question. Pair with text summary, window, denominator, and table. |
| Microtransitions | Can preserve object continuity and show cause/effect. | Frequent fades and slides slow expert use and harm motion-sensitive users. | Limit to panel/selection continuity, 80 to 150ms, removable without loss. |
| Gamified progress | Can provide short-term motivation for some users. | Confuses engagement with learning, creates pressure, and may encourage shallow completion. | Reject points, gems, streak repair, confetti, mascots, and false mastery bars. Calm course position is enough. |

## 6. Three coherent visual directions compared on the same flows

The comparison uses the same representative flow:

1. Open the course shelf and resume an EMT course.
2. Inspect a source-linked objective and its prerequisites.
3. Read a long lesson containing a definition, warning, table, cited image,
   inline prediction, and check.
4. Answer incorrectly, receive entitled feedback, retry, and continue.
5. Review evidence with sparse data and a pending prose mark.
6. Open an AI-proposed lesson change, compare citations and diff, approve or
   reject it, then inspect agent and offline status.

### Direction A: Quiet Workbench

**Visual thesis:** warm or neutral paper for authored content, restrained
neutral chrome, duospace ledger details, fine separators, few bounded surfaces,
and one course accent. Desktop uses a navigation rail, document canvas, and
optional contextual inspector. Compact professional views use lists, tables,
and split panes.

| Flow moment | Treatment |
|---|---|
| Course shelf | Book-like course entries in a simple list or modest cover grid. One next-action panel is visually primary. Progress is a labeled path state, not a ring around every course. |
| Objective map | Outline first, focused prerequisite graph second. Selection opens evidence and sources in the inspector. |
| Lesson | Broad quiet field with a 62 to 72 character target measure, semantic marginal support at wide widths, and in-flow fallbacks. Definitions and citations are visually quieter than teaching blocks. |
| Question and feedback | The question sits in the document flow. Options are rows, not nested cards. The feedback area is adjacent and stable. Correctness uses text, icon, and border plus semantic color. |
| Evidence | Dense list/table with a plain-language summary, denominator, window, pending state, and expandable raw evidence. |
| Authoring and diff | Workbench split: source or current version, proposed version, inspector for citations and gate findings. Diff is the primary object, agent transcript secondary. |
| Offline/error | A persistent compact state in shell plus a local recovery notice. Authored content remains fully readable. |

**Strengths:** best fit with shipped fonts and theme; supports sustained reading
and dense work; distinct without novelty; exposes authority through typography;
least visual churn.

**Weaknesses:** can feel too editorial or austere; needs careful hierarchy so
dense lists do not resemble a database admin tool; split panes require strong
responsive collapse behavior.

### Direction B: Structured Studio

**Visual thesis:** crisp sans-led interface, stronger 8px grid, clearly bounded
panels, higher chroma selection, explicit modes, and creative-tool conventions.
Reading still uses Source Serif, but most surfaces use panels, tabs, toolbars,
and inspectors.

| Flow moment | Treatment |
|---|---|
| Course shelf | Cover tiles with explicit metadata and actions. |
| Objective map | Canvas-like map with tool palette, filters, zoom, and inspector. |
| Lesson | Center panel with section navigator and annotation tools. Semantic teaching blocks use consistent panel headers. |
| Question and feedback | Focused activity panel with a stronger action bar and mode header. |
| Evidence | Dashboard-like workspace with filters, charts, and detail panels. |
| Authoring and diff | Strongest area: editor, preview, diff, sources, agent activity, and diagnostics fit a studio shell. |
| Offline/error | Status bar, notification center, and affected-panel errors. |

**Strengths:** powerful for authoring, source reconciliation, and diagnostics;
familiar to technical users; scales to many tools and panes.

**Weaknesses:** learning can feel like operating software rather than studying;
panel and toolbar accumulation competes with content; narrow, touch, and screen
reader complexity rises sharply; easy to resemble VS Code, Figma, or a generic
SaaS builder.

### Direction C: Guided Canvas

**Visual thesis:** generous spacing, one learning act per viewport, larger type,
strong illustrative diagrams, smooth staged transitions, simplified chrome,
and visible course-path progression. Authoring is a separate dense mode using
the same tokens.

| Flow moment | Treatment |
|---|---|
| Course shelf | Large course covers and a single resume action. |
| Objective map | Simplified path with current, next, optional, and blocked nodes. |
| Lesson | Staged presentation with one explanation, prediction, diagram, or check at a time. Continuous reader remains available. |
| Question and feedback | Large touch-first choices, immediate targeted feedback, and explicit continuation. |
| Evidence | Narrative review of what happened and what to do next, with details behind disclosure. |
| Authoring and diff | Switches into a denser review mode, creating a stronger mode boundary. |
| Offline/error | Full-width calm notice and preserved downloaded lesson path. |

**Strengths:** strongest focus and touch behavior; easiest novice orientation;
good for guided lesson pacing and diagrams.

**Weaknesses:** low density frustrates sustained reference reading and expert
authoring; “one screen at a time” can hide context; animation and large surfaces
can become theatrical; separate authoring mode risks visual fragmentation.

### 6.4 Comparative decision matrix

Scores are directional judgments from 1 (weak) to 5 (strong), not measured user
outcomes.

| Criterion | Quiet Workbench | Structured Studio | Guided Canvas |
|---|---:|---:|---:|
| Sustained reading | 5 | 3 | 4 |
| Guided learning | 4 | 3 | 5 |
| Dense evidence | 5 | 5 | 2 |
| Authoring and diffs | 5 | 5 | 2 |
| Narrow and touch | 4 | 2 | 5 |
| Keyboard productivity | 5 | 5 | 3 |
| Screen-reader simplicity | 4 | 2 | 4 |
| Fit with shipped system | 5 | 3 | 3 |
| Risk of excessive chrome | 5 | 2 | 4 |
| Risk of novelty hiding work | 5 | 3 | 2 |
| Cross-surface coherence | 5 | 4 | 3 |

**RECOMMENDATION:** accept Quiet Workbench as the default direction, borrow
Structured Studio’s split-view and command patterns only for advanced work,
and borrow Guided Canvas’s focus and touch treatment for guided lesson mode.
This is one responsive system with density and mode variations, not three
themes or three renderers.

## 7. Recommended design system

### 7.1 Token architecture

Keep raw values private to the system and expose semantic roles. Existing token
names remain compatibility aliases during migration.

| Layer | Proposed tokens | Rule |
|---|---|---|
| Color surfaces | `surface-canvas`, `surface-paper`, `surface-raised`, `surface-sunken`, `surface-selection`, `surface-overlay` | A screen should normally use canvas, paper, and at most one raised level. Do not simulate depth with many card shades. |
| Color text | `text-primary`, `text-secondary`, `text-tertiary`, `text-link`, `text-on-accent`, `text-disabled` | Tertiary and disabled must still be tested. Muted text is not permission to fail contrast. |
| Color borders | `border-subtle`, `border-default`, `border-strong`, `border-focus` | Borders express grouping and selection, not decoration around every object. |
| Semantic states | `state-info`, `state-success`, `state-warning`, `state-danger`, `state-pending`, `state-unknown`, each with text/surface/border/icon roles | Course accent never means correct, incorrect, complete, or mastered. Every state has a non-color channel. |
| Provenance | `source-authored`, `generated-synthesis`, `runtime-record`, `human-review`, `unverified` roles | Prefer label, typography, and structure. Color is secondary. |
| Typography | `font-paper`, `font-ledger`, `font-ui`, `font-code`; `text-label`, `text-body`, `text-reading`, `text-heading`, `text-display`, `text-data` | Retain shipped families. Test whether reading needs its own size, do not proliferate display steps. |
| Spacing | `space-1..7` mapped to 4, 8, 16, 24, 32, 48, 64px | Retain shipped scale. Add density aliases such as `control-block`, not intermediate raw values. |
| Shape | `radius-control`, `radius-surface`, `radius-overlay`; `border-width`, `focus-width`, `focus-offset` | Three radii maximum. Cards do not each get a bespoke silhouette. |
| Elevation | `elevation-none`, `elevation-overlay`, `elevation-modal` | Ordinary grouping uses borders or background, not shadows. Shadows are for real overlap. |
| Motion | `duration-instant`, `duration-fast`, `duration-functional`; `ease-standard`, `ease-exit`; distance tokens | Proposed values: 0, 80, 150ms. Reduced motion maps all to 0 except user-controlled media. |
| Layout | `measure-reading`, `measure-form`, `rail-width`, `inspector-width`, `content-gutter`, `sticky-offset` | Values must survive text zoom and localization. Prefer min/max constraints over fixed pixels. |
| Density | `density-comfortable`, `density-compact` mapped to row height, control padding, and inter-group gap | Touch input forces comfortable targets without changing information hierarchy. |
| Charts/diagrams | categorical sequence, comparison, positive/negative, unknown, grid, annotation, focus, selected | Color sequences must be tested in both themes and with patterns/labels. No course accent reuse as a data series by default. |

### 7.2 Typography

**RECOMMENDATION:** retain the four voices already shipped:

- **Paper:** Source Serif 4 for lesson prose, direct readings, extended stems,
  and authored explanation.
- **UI:** system sans for navigation, controls, labels, settings, maps, and
  authoring chrome.
- **Ledger:** iA Writer Quattro for compact runtime facts, provenance, evidence
  counts, status identifiers, and trustworthy machine records.
- **Code:** system monospace for code, literal syntax, and diffs.

Use 400 and 600 as the ordinary weights. Use size, spacing, and placement before
adding weight. Long ledger paragraphs are prohibited. All-caps is limited to
very short machine labels and should be avoided in localized prose. Numeric
tables use tabular figures. Headings follow document semantics, not visual size
alone.

Reader controls may offer a small bounded set: reading size, measure, line
height, and theme. They change rendering only and never rewrite authored files.
The initial presets should be named by outcome, such as Compact, Comfortable,
and Large text, not expose a typography control panel by default.

### 7.3 Spacing, density, and surfaces

- Comfortable learning rows retain the shipped 44px house target. Compact
  authoring rows may be visually shorter only when their actual targets still
  meet the product’s accessibility contract or an adjacent full-size action
  exists as already specified.
- Use whitespace to separate conceptual sections, separators to distinguish
  rows, tint for current selection, and raised surfaces only for overlap or a
  bounded decision.
- Course shelf entries may be cards because each is an independent destination.
  Source lists, objectives, evidence events, findings, settings, and agent
  events should default to lists or tables.
- Never nest more than two visibly bounded surfaces. A callout inside a lesson
  paper should not contain option cards that contain feedback cards.
- On wide screens, the reading field remains visually continuous even when a
  context inspector is present. Do not put the entire lesson inside a dashboard
  card.

### 7.4 Color and themes

Keep `light`, `dark`, and `system`. Prototype explicit high-contrast palettes,
but first support operating-system forced-colors and increased-contrast
preferences without suppressing them. Keep one learner-selected course/app
accent source with contrast-correct rendered variants.

Course identity may use a cover image or a second constrained course color, but
neither may enter assessment semantics, chart meaning, focus, or provenance.
Subject themes should be content-led, not shell recoloring. A mathematics course
can contain different diagrams and notation without making all controls blue.

True black OLED remains deferable. It adds a new tested palette, not a casual
hex replacement. Sepia may be a reader-only preset if user testing shows value;
it should not recolor authoring, tests, or semantic states.

### 7.5 Icons, imagery, and diagrams

Adopt a small open icon family with pinned version, checksum, license review,
and a stable semantic mapping. Primary, destructive, and uncommon actions have
visible labels. Icons may become label-free only for universal, repeated actions
with accessible names and tested discoverability.

Imagery has four permitted roles:

1. Cited instructional evidence or object of study.
2. Explanatory diagram that makes a relationship easier to see.
3. Optional course cover chosen or approved by the user.
4. A sparse orientation image whose empty-state value is tested.

Every instructional image needs source, rights/provenance, caption, alternative
text or a longer equivalent, and a static/offline representation. Decorative
images use empty alternatives. AI-generated imagery is labeled, reviewable, and
never presented as source evidence.

Diagram rules:

- Choose table for exact repeated comparisons, flow for sequence, tree for
  hierarchy, timeline for change, map for spatial relation, plot for quantitative
  relation, and illustration only when appearance itself matters.
- Provide a text summary and, for data graphics, the underlying table.
- Label lines and regions directly where possible. Do not require a legend
  lookup for a two-series chart.
- Encode selection and series with label, shape, pattern, or position in
  addition to color.
- Node maps start focused on the current objective and neighbors. The outline is
  the complete accessible alternative and a first-class view, not a hidden
  compliance appendix.
- Diagrams use authored semantics. The renderer may lay them out, but layout
  coordinates never become the only source of meaning.

### 7.6 Focus, selection, status, progress, and feedback

**Focus:** keep a high-contrast 2px or stronger visible ring with offset. Never
remove focus on mouse use if that makes keyboard modality unclear. When content
is revealed or a mode changes, move focus only when necessary and to the first
meaningful heading, status, or control. Preserve return focus for dialogs and
popover definitions.

**Selection:** accent means selected/current, not correct. Selected rows use at
least border or indicator plus background and accessible state. Hover is a
preview affordance only and must never reveal essential content unavailable by
focus and touch.

**Status:** local status stays near the initiating action and uses one polite
live region. Use alerts only for urgent blocking changes. The shell may show
compact offline, indexing, agent, and pending-write states, but the affected
surface still owns the actionable explanation.

**Progress:** distinguish:

- path position, such as unit 3 of 8;
- completion, such as 4 required activities finished;
- due work, such as 6 reviews due;
- evidence sufficiency, such as 2 attempts, too little evidence;
- pending work, such as 1 response awaiting review;
- coverage, such as supported, thin, missing, conflicting, unknown;
- operation progress, such as 34 of 80 sources indexed.

These are separate visual components and labels. Do not compress them into one
percentage. Determinate progress bars require a known denominator. Indeterminate
operations use a static status and elapsed stage, not an endlessly animated
bar.

**Feedback:** reserve adjacent space when the state is predictable. Keep the
learner’s response visible. State what happened, why when entitled, and the next
legal action. Correctness does not trigger confetti, sound, scale bounce, or
streak copy. Pending prose review never looks incorrect.

### 7.7 Motion and transitions

Motion must answer one of three questions:

1. Where did this object go?
2. What changed because of my action?
3. Is my initiated operation still proceeding?

Permitted examples include an inspector opening from the selected row, a list
item maintaining position after a reversible update, or a determinate operation
advancing. Motion is 80 to 150ms, uses opacity or small transforms, and never
animates layout-dependent reading position. Reduced motion removes it while
leaving the final state and status intact.

Do not animate lesson text arrival, hint tiers, correctness, charts on initial
load, agent typing, background indexing, errors, or progress merely to make the
app feel alive. Scroll position changes are explicit and focus-aware.

## 8. Cross-surface visual rules

| Surface | Primary visual object | Secondary object | Avoid |
|---|---|---|---|
| Course shelf | Course title, target, resume action, honest path state | Source count, last activity, unresolved work | A metric dashboard on every card; generic generated cover art |
| Sources | Searchable source list and selected-source document/outline | Provenance, extraction, conflicts, bindings | Thumbnail wall for text files; hiding paths and ownership |
| Course map | Objective outline with current focus | Local prerequisite graph, treatment, coverage, evidence | Giant galaxy graph; false global completion |
| Lessons/readings | Continuous paper and current learning act | Definitions, citations, optional context inspector | Card per paragraph; decorative callout rainbow; forced pagination |
| Notes | Editable document or outline | Source links and objective links | Sticky-note simulation; visual clutter that breaks plain Markdown |
| Questions/practice | Stem, response control, and adjacent feedback | Context, allowed hints, source link | Multiple chrome bands; tiny choice controls; correctness by color |
| Tests | Question and time/progress facts permitted by mode | Review flags and navigation | Gamified progress, premature feedback, ambient distractions |
| Evidence | Summary with window and denominator, then exact records | Trend chart, raw events | Dashboard tiles with unexplained percentages |
| Authoring | Current/proposed artifact or editor/preview | Sources, checks, agent activity | Chat as primary canvas; approval detached from diff |
| Diffs | Changed content and semantic risk | Citations, validation, ownership, undo | Red/green alone; truncated target identity; beautified diff hiding deletions |
| Agent activity | Current stage and inspectable proposal | Sources, uncertainty, tool log | Animated typing, anthropomorphic avatar, status claiming authority |
| Settings | Grouped native controls with preview | Advanced details and reset | One card per setting; auto-save of consequential changes |
| Diagnostics | Problem list, affected capability, next action | Versions, paths, logs, copyable command | Opaque red banner, codes without explanation, full log as first view |
| Empty state | What this area is and the one next action | Sample or import option | Decorative illustration without instruction; fake populated content |
| Error state | What failed, what is safe, what to do | Technical details and retry | Loss of current work; generic “something went wrong” |
| Offline state | What still works and what does not | Retry/reconnect and cached scope | Blocking the entire app; simulated model output |

## 9. Accessibility, portability, privacy, provenance, and authorability

### 9.1 Responsive, zoom, keyboard, touch, and screen readers

- Preserve logical DOM order: navigation, context, primary activity, status,
  support. CSS may place the inspector beside the activity but must not reorder
  reading or focus.
- At narrow widths and zoom, navigation becomes a labeled drawer or course
  switcher; inspector content follows the affected selection in-flow. No bottom
  sheet may hide the primary action or trap screen-reader reading unexpectedly.
- Test long translated labels at 30% and 100% expansion, unbreakable identifiers,
  right-to-left direction, and scripts whose emphasis and line-breaking rules
  differ from English. Do not use fixed-height text controls or icon-only
  navigation to rescue space.
- Touch and pointer share actions. Drag always has a non-drag alternative.
  Hover-only definitions also work by focus, touch activation, and glossary
  navigation.
- Prefer native buttons, links, details, headings, lists, tables, progress, and
  dialogs. Complex maps and editors document their keyboard model and expose
  equivalent outline or text views.
- Announce completed operations once. Do not make changing timers, agent tokens,
  raw program output, or pointer movement live.
- High contrast and forced colors preserve focus, selection, boundaries, and
  semantic status without relying on background tints.

### 9.2 Long content and localization

Long lessons keep section navigation and stable anchors. Reading width is
bounded but headings, tables, diagrams, and code may use controlled full-width
escapes. Wide content scrolls only in named local regions. A learner can copy,
select, search, annotate, and deep-link without entering a guided mode.

Localization affects more than string width. Tokens and primitives must support
right-to-left flow, logical CSS properties, locale-aware number/date formatting,
plural forms, different name orders, and writing-system-specific fonts. Visual
QA uses pseudo-locales and at least one real right-to-left fixture before Phase
17 completion.

### 9.3 Portability and offline behavior

The authored lesson remains coherent Markdown. Themes, layout, popovers, staged
reveals, and diagrams are enhancements over semantic blocks. Static exports show
definitions, captions, citations, diagram summaries, and all non-assessment
meaning. Interactive assessment that needs runtime authority fails honestly
rather than embedding keys or a client scorer.

Fonts, icons, math, editor, diagram runtime, and any other visual dependency are
vendored at pinned versions with checksums and license review. The app never
depends on a CDN for core rendering. Offline status is visible but quiet and
does not repeatedly notify.

### 9.4 Privacy and provenance

No visual analytics library or remote font request is justified. Product
telemetry remains absent. Interaction state needed for restoration stays local.
Pointer traces, hover history, scroll surveillance, and attention estimates are
not collected as “learning evidence.”

Source-authored content, generated synthesis, runtime facts, and human review
use consistent labels and typography. Cited imagery shows creator/source,
license or rights note when known, locator, and whether it was transformed.
Agent status never visually resembles a deterministic verdict.

### 9.5 Authorability and legacy upgrades

Every visual primitive needs:

1. Teaching or work purpose.
2. Portable authored representation or derived-data source.
3. Plain-file fallback.
4. Keyboard, touch, screen-reader, narrow, and offline behavior.
5. Theme and high-contrast behavior.
6. Agent authoring rule and deterministic validation where possible.
7. Misuse rule and representative fixture.

Legacy upgrade begins with an audit. A proposal names which new primitive adds
learning value, shows the source and rendered diff, preserves stable identity
and assessment semantics, and can be rejected or undone. Pure restyling does
not rewrite the file. A theme migration belongs in CSS/tokens, not in hundreds
of lesson diffs.

## 10. Implications for learner flow, content contract, agents, and upgrades

### Learner flow

- Phase 16 should define selection, focus destination, status ownership, and
  progressive disclosure before Phase 17 animates or positions anything.
- Reader and guided lesson are two presentations of the same semantic content.
  Their visual difference is density and staging, not separate artifacts.
- Every transition from lesson to question to feedback to practice to evidence
  preserves course, unit, objective, and next-action context.
- Tests use a quieter subset of the shell. Authoring tools and agent activity do
  not leak into a sitting.

### Semantic content contract

- Visual roles attach to semantic blocks such as warning, key idea,
  misconception, example, source excerpt, figure, prediction, and check.
- Authors do not choose raw colors, shadows, animation, arbitrary icons, or
  layout coordinates for ordinary lesson blocks.
- Diagram semantics, alternative representation, caption, citation, and
  interaction intent are authored. Theme and layout are derived.
- Progress and status components consume typed state, not guessed strings or
  color classes.

### Agent skills

Agent playbooks should say:

- choose a semantic teaching role before a visual primitive;
- reuse existing lesson and course artifacts before creating a replacement;
- never select color, icon, or motion as the only carrier of meaning;
- supply captions, alternatives, citations, rights/provenance, and static
  fallbacks for media;
- validate long content, localization, narrow screens, themes, and plain-file
  reading;
- show a diff and visual QA artifacts without claiming screenshots prove
  accessibility or learning quality;
- never style generated synthesis as source or agent interpretation as runtime
  fact.

### Legacy upgrades

The upgrade tool should distinguish:

- **render-only migration:** new tokens or primitives improve all compatible
  content without file changes;
- **semantic annotation:** a reviewable file diff adds a missing role, caption,
  alternative, or citation;
- **interaction enhancement:** a static semantic representation gains a rich
  interaction while preserving the original;
- **content revision:** meaning changes and requires source, objective, and
  assessment review;
- **rejection:** cosmetic churn with no learning, authoring, accessibility, or
  provenance value.

## 11. Visual QA gates and prototype plan

### 11.1 Required QA gates

| Gate | Minimum evidence |
|---|---|
| Token integrity | No unreviewed literal colors, type sizes, radii, spacing, shadows, or durations outside token definitions. Semantic tokens pass automated light/dark contrast fixtures. |
| Cross-surface coherence | Course shelf, sources, map, lesson, question, test, evidence, authoring, diff, settings, diagnostics, empty, error, and offline fixtures use the same primitives and state vocabulary. |
| Responsive/reflow | Automated screenshots and DOM checks at 1440, 1280, 1024, 768, 375, and 320 CSS px plus 200% and 400% text/reflow scenarios where applicable. No page-level horizontal scroll except genuine two-dimensional content. |
| Keyboard | Complete representative flow without pointer, including skip links, navigation, definitions, map outline, question, hints, dialogs, diff, approval, and recovery. Focus is never lost or concealed. |
| Screen reader | Manual passes with at least VoiceOver/Safari and NVDA/Firefox or current equivalent. Verify names, roles, states, reading order, status announcements, tables, dialogs, definitions, diagrams, and hidden assessment content. |
| Touch | Real-device or reliable device pass for phone and tablet. Targets, drag alternatives, sticky regions, drawers, virtual keyboard, and orientation changes remain usable. |
| Theme/high contrast | Light, dark, system, forced colors, increased contrast where supported, and custom accent. Selection, focus, status, diagrams, and diffs remain distinct. |
| Reduced motion | System preference removes all nonessential transitions and animation. State and focus remain clear. No autoplay or looping task motion. |
| Localization | Pseudo-localized expansion, right-to-left fixture, locale-aware dates/numbers, long course titles, long objectives, and mixed-script source paths. |
| Long/zero/one/many | Empty, one, typical, and stress fixtures for courses, sources, objectives, questions, citations, findings, diffs, agent events, and diagnostics. No truncation of consequential identity. |
| Offline/degraded | Network disconnected and model unavailable. Fonts, icons, math, authored lessons, scoring, evidence, and local status remain correct; unavailable enhancements state scope and recovery. |
| Assessment integrity | Hidden key, correctness, higher feedback tiers, and private tolerance are absent from HTML, CSS, accessibility tree, source maps, static fallback, screenshots, and client payloads. |
| Portability | Representative lesson remains coherent in plain Markdown and at least one common Markdown reader. Static fallback includes essential semantics and citations. |
| Visual regression | Stable synthetic fixture screenshots per theme/viewport/state, reviewed alongside DOM/state assertions. Pixel difference alone neither passes nor fails accessibility. |
| Performance | Long lesson, large course map outline, large diff, and many-source list have measured startup, interaction, and scroll budgets on packaged target hardware. Avoid animation and virtualize only when semantics/focus are preserved. |

### 11.2 Prototypes before Phase 17 implementation

1. **Same-content direction board:** render one synthetic unit in all three
   directions at desktop and narrow widths. Use identical text, states, and
   actions. Evaluate reading, orientation, density, trust, and accessibility,
   not visual preference alone.
2. **Quiet Workbench tracer:** course shelf to lesson to wrong answer to
   evidence to authoring diff, with source, runtime, generated, pending, offline,
   and error states.
3. **Density prototype:** comfortable and compact on source lists, objective
   outlines, evidence, and diffs. Confirm touch and keyboard targets.
4. **Map prototype:** outline plus focused graph plus screen-reader and narrow
   alternatives. Stress 10, 100, and 1,000 objectives.
5. **Long-content prototype:** EMT table, math, code, citations, right-to-left
   paragraph, long heading, long path, and generated synthesis in one lesson.
6. **Theme prototype:** light, dark, custom accent, forced colors, and reduced
   motion across selection, feedback, diff, chart, and diagram states.
7. **Agent/provenance prototype:** show staged generation, waiting, failure,
   proposed diff, gate findings, approval, publish receipt, and undo without
   anthropomorphism or false authority.

## 12. Accept, reject, defer, prototype, and open decisions

| Disposition | Decision | Rationale and condition |
|---|---|---|
| **Accept** | Quiet Workbench as default visual direction | Best fit with shipped Paper & Ledger foundation and the full reading/authoring task range. |
| **Accept** | Semantic token architecture extending `theme.py` and shared presentation primitives | Prevents per-surface drift and makes themes and QA testable. |
| **Accept** | Source Serif 4, iA Writer Quattro, system UI, and system monospace role split | Already shipped and aligned with source/authority/code semantics. |
| **Accept** | Comfortable and compact density under one component system | Learning and authoring have legitimately different density needs. |
| **Accept** | Lists and separators as default; cards only for independent destinations or bounded decisions | Preserves hierarchy and information density. |
| **Accept** | Reader and guided mode over the same semantic content | Required by portability and the source-to-course contract. |
| **Accept** | One small, open, vendored icon family with labels for uncommon actions | Supports coherence without importing a competitor’s identity. |
| **Accept** | Motion only for continuity, causality, and initiated operation progress | Aligns with reduced motion and learning-relevant attention. |
| **Accept** | Outline-first course map with focused graph enhancement | Works for accessibility, scale, narrow screens, and complex curricula. |
| **Accept** | Text summary and table alongside every evidence visualization | Preserves exact values, denominators, and accessibility. |
| **Reject** | Excessive card grids and nested panels | Wastes space, fragments continuous reading, and creates weak hierarchy. |
| **Reject** | Points, gems, streak repair, confetti, celebratory motion, and mascot pressure | These optimize engagement signals, not honest learning evidence. |
| **Reject** | Generic AI chat as the primary canvas | Hides artifacts, sources, course path, and approval boundaries. |
| **Reject** | Decorative gradients, glass surfaces, 3D objects, and generated art as default identity | High novelty and asset cost with no learning role. |
| **Reject** | Color-only status, graph-only progress, icon-only unusual actions, hover-only help | Inaccessible and ambiguous across themes and modalities. |
| **Reject** | Skeleton screens and animated “thinking” as default loading behavior | Local-first tasks benefit more from truthful stage and progress text. |
| **Reject** | One enormous prerequisite graph | Poor scale, narrow behavior, and semantic accessibility. |
| **Reject** | Per-lesson raw styling, arbitrary animation, and layout coordinates | Breaks coherence, portability, authorability, and safe validation. |
| **Defer** | Marketing identity, logo, and custom illustration system | Not required to validate the product UI; can follow the functional visual system. |
| **Defer** | OLED true-black theme | Requires a complete tested palette and has limited learning impact. |
| **Defer** | Arbitrary community themes or CSS plugins | Broad customization conflicts with support and accessibility guarantees. Bounded tokens come first. |
| **Defer** | Full IDE-style panel docking | High complexity. Fixed responsive regions cover the initial workflow. |
| **Defer** | Spatial canvas for notes and objectives | Outline and focused graph meet more needs with lower accessibility cost. |
| **Prototype** | 18px lesson body versus existing 16px body | Decide with representative reading and zoom tests. |
| **Prototype** | Rail plus inspector breakpoint and collapse model | 1024px and zoom may make three regions untenable. |
| **Prototype** | Compact density target and row rules | Must preserve touch, keyboard, and screen-reader usability. |
| **Prototype** | High-contrast explicit theme in addition to forced-colors support | Determine whether it adds value without a second state grammar. |
| **Prototype** | Course cover imagery and constrained course accent | Test orientation benefit, clutter, provenance, and cross-course scan. |
| **Prototype** | Command palette | Useful for expert work only if visible actions remain complete. |
| **Open** | Exact diagram stack and authored diagram grammar | Depends on Phase 16 semantic contract and offline/accessibility evaluation. |
| **Open** | User scope for density and reader preferences | Choose global, workspace, or temporary per-surface behavior after prototype. |
| **Open** | Minimum supported operating-system high-contrast matrix | Phase 17 must name packaged browser engines and target OS versions. |
| **Open** | Whether learner notes share paper typography or UI typography | Test mixed reading/editing sessions and Markdown fidelity. |

## 13. Concrete recommendation and risks

### Recommended Phase 17 input

Build Phase 17 around **Quiet Workbench**, using the shipped Paper & Ledger
typographic authority model and palette derivation. Establish tokens and
primitives first, then implement one realistic course-unit tracer across all
surfaces and states before multiplying screens. Borrow a fixed split-view and
command palette from creative tools only for advanced authoring. Borrow larger
targets and staged focus from guided learning tools only in guided mode. Keep
continuous reading, evidence inspection, and plain files first-class.

The minimum primitive set is:

1. App shell, navigation rail/drawer, course switcher, breadcrumbs, context
   line, and skip links.
2. Paper canvas, content section, reading controls, anchor navigation, and
   contextual inspector.
3. List, tree/outline, data table, local scroll region, tabs, disclosure, split
   view, and dialog.
4. Button, text field, select, checkbox, radio, segmented choice, command item,
   and toolbar.
5. Inline status, blocking notice, empty state, offline state, progress, badge,
   and provenance label.
6. Question response, feedback, hint stack, source citation, semantic callout,
   figure, diagram, code/math block, and definition interaction.
7. Evidence summary, trend plus table, coverage state, diff, finding, approval,
   receipt, agent stage, and diagnostic record.

### Primary risks

| Risk | Consequence | Mitigation |
|---|---|---|
| Visual system arrives before semantic contracts | Components guess status, provenance, or learning purpose and later fork. | Phase 16 fixes typed states and authored roles first. |
| Paper & Ledger becomes a decorative font trick | Typography implies authority inconsistently. | Define exact content ownership rules and lint/test component usage. |
| Workbench density overwhelms learners | The course feels like an IDE. | Activity-first defaults, comfortable density, contextual inspectors, and guided mode. |
| Guided mode becomes theatrical | Motion and pagination hide context. | Continuous reader remains one click away; no required animation; stable anchors and outline. |
| Token sprawl recreates per-page styling | System becomes ungovernable. | Token review, usage counts, deprecation path, and no raw-value gate. |
| Accessibility judged from screenshots | Focus, names, status, reading order, and hidden content defects ship. | Manual keyboard and screen-reader passes plus structural tests. |
| Responsive design means “stack everything” | Long support and navigation appear before the active task. | Preserve activity-first DOM order and contextual disclosure rules. |
| Graph and chart novelty implies false certainty | Learners infer unsupported mastery or prerequisite structure. | Explicit unknowns, denominators, outline/table alternatives, and focused views. |
| Customization bypasses contrast or semantics | Themes make states unreadable or ambiguous. | Persist bounded sources, derive checked roles, and test all semantic states. |
| AI imagery or copy appears source-authored | Trust and provenance fail. | Persistent generated labels, rights/source metadata, and human approval. |
| Large local datasets degrade the packaged app | Lists, diffs, maps, and search feel broken. | Stress fixtures, measured budgets, semantic virtualization, and incremental status. |
| Cross-platform shell differences cause drift | Browser fallback and packaged app diverge. | Treat browser content as the primary visual system; native chrome stays minimal. |

### Bottom line

**FACT:** itembank already ships the beginnings of a credible visual language
and unusually strong accessibility and authority boundaries.

**INFERENCE:** coherence now depends more on disciplined composition and state
grammar than on additional colors or components.

**RECOMMENDATION:** make Quiet Workbench the default, with comfortable and
compact density plus reader and guided presentations under one semantic system.

**OPEN:** settle reading size, responsive three-region behavior, diagram stack,
high-contrast theme, and preference scope through the named prototypes before
Phase 17 locks implementation.
