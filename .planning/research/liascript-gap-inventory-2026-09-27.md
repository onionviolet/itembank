# LiaScript feature gap inventory

Date: 2026-09-27. Research only. No feature adoption, format change, or implementation is authorized by this inventory.

> "Consider everything https://github.com/LiaScript/LiaScript has that we dont, first writing every little thing from there that we dont have, we wont be absorbing everything"

## Method and status

This is a feature-level inventory of the official [LiaScript runtime README](https://github.com/LiaScript/LiaScript/tree/c2e37e36440f270403069e47c712bbb8ffe2d9e7) and its [full documentation course](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md). Those are repository snapshots, not a claim that every demonstration was run. The documentation's own metadata says 2026-09-09. Itembank was inspected at `af105e1b031dec792778d024a9cf5545ce3fecd5`; an existing uncommitted edit to `.planning/USER-VISION.md` was not used as implementation evidence. Current Itembank evidence comes from `README.md`, `model.py`, `capabilities.py`, `surfaces/lesson.py`, `surfaces/lesson_progressive.py`, `surfaces/lesson_interaction.py`, `surfaces/audio.py`, `surfaces/course_package.py`, and the named tests under `tests/`.

**Missing** means no equivalent user-facing workflow was found in the sampled implementation and documentation. **Partial** means Itembank has a related capability but lacks the stated LiaScript behavior or breadth. **Unverified** means a close analogue may exist but the sampled evidence does not settle parity. These are product behavior comparisons, not syntax compatibility requests. LiaScript includes auxiliary projects such as an editor, exporter, and dev server; rows name these as ecosystem features, not features inside the interpreter. Source links at each section head support its rows. A more exhaustive audit of every third-party LiaTemplate and every code path in both repositories would be a separate, unbounded task.

### A. Authoring and course format

Sources: [Markdown and structure](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#markdown-syntax), [tools](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#tools), [macro reference](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#macros), [configuration](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#2-basic-macros).

| ID | LiaScript behavior Itembank lacks or only partly matches | Status |
| --- | --- | --- |
| A01 | One Markdown course file opens directly by URL in a generic LiaScript browser reader, without an Itembank build, local daemon, or registration step. | Missing |
| A02 | The same source is switched among Presentation, Slides, and Textbook modes. Itembank has continuous and guided lesson reading, but no full slide or presentation rendering of a whole course. | Partial |
| A03 | Author controlled slide and subsection boundaries with nested headings, HTML `section` and `article`, and slide persistence rules. | Missing |
| A04 | Inline and block appearance or disappearance steps tied to slide numbers, beyond Itembank's sequential guided explanation blocks. | Partial |
| A05 | Reusable parameterized author macros, including multiline block macros and macro overrides. | Missing |
| A06 | Import an external macro library or course template into a document. | Missing |
| A07 | Document-level metadata controls for author, comment, date, email, editable link, logo, icon, repository, attribution, and version. Itembank has provenance fields, but not this reader-facing bundle. | Partial |
| A08 | Document-level language, narrator, font, stylesheet, script, and onload declarations. | Missing |
| A09 | Course-local and global KaTeX macro definitions. Itembank renders math, but a comparable author-facing formula-macro facility was not found. | Partial |
| A10 | Reader-facing mode, dark appearance, sharing, classroom, and translation defaults set in a source header. Itembank has settings and themes, but not this source-level control set. | Partial |
| A11 | Live browser editor with course preview and image or video upload. The native course workbench does not match this full editor. | Partial |
| A12 | Peer-to-peer live coediting in the LiveEditor. | Missing |
| A13 | VS Code, VS Code Web, and Atom save-to-preview extensions. | Missing |
| A14 | Author snippets and fuzzy syntax help in those editors. `itembank spec` and lint help authors, but no corresponding editor snippet package was found. | Partial |
| A15 | Dev server that reloads courses on save and navigates multiple local projects. Itembank can serve content, but lacks this authoring loop. | Partial |
| A16 | CodiLIA collaborative editor with immediate course publishing. This is a separate LiaScript ecosystem project. | Missing |
| A17 | Inline HTML and CSS styling for arbitrary document elements, including block and inline style comments. Itembank deliberately constrains authored rendering. | Missing |
| A18 | Raw embedded HTML components and arbitrary JavaScript components in lesson content. Itembank has bounded native treatments and learner-code checks, not arbitrary authored components. | Missing |
| A19 | `lia-keep` and source-level persistent-slide behavior that survives navigation or rendering changes. | Missing |

### B. Text, media, and navigation

Sources: [references and QR codes](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#references), [images through embeds](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#images-), [blocks and footnotes](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#markdown-blocks), [publishing](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#publishing).

| ID | LiaScript behavior Itembank lacks or only partly matches | Status |
| --- | --- | --- |
| B01 | Slide deep links by slide number or name in a publicly shareable course URL. Itembank has local heading and source anchors. | Partial |
| B02 | Render a linked LiaScript course as an in-reader preview. Itembank has cited local source preview, but not nested course preview. | Partial |
| B03 | Generate QR codes from links and show a course sharing QR control. | Missing |
| B04 | Context-sensitive image placement, including automatic floating layout and size behavior from Markdown placement. Itembank renders referenced figures, but no equivalent automatic layout was found. | Partial |
| B05 | Automatic image gallery from adjacent images. | Missing |
| B06 | Mixed gallery of images, audio, and video links. | Missing |
| B07 | One-markup inline audio player for an authored audio URL. Audio drill export exists, but not this lesson authoring path. | Partial |
| B08 | One-markup video embedding for local video and known providers such as YouTube and Vimeo. | Missing |
| B09 | Generic URL embed with oEmbed attempt and iframe fallback. | Missing |
| B10 | Configurable autoplay, mute, and other video presentation attributes in authored content. | Missing |
| B11 | Inline footnotes plus standard end footnotes as a general lesson grammar. Source citations exist, but no comparable general footnote system was found. | Partial |
| B12 | Author-chosen alert blocks, arbitrary block styling, and custom typographic treatment beyond Itembank's named semantic callouts. | Partial |
| B13 | Reader-visible email and telephone autolinks with special handling. | Unverified |
| B14 | Course files linked over ordinary HTTPS and multiple public file hosts with relative media resolution. Itembank supports local approved roots and source adapters, not a generic public course reader. | Partial |

### C. Teaching effects and spoken content

Sources: [effects, animations, speech, playback](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#effects), [runtime feature summary](https://github.com/LiaScript/LiaScript/tree/c2e37e36440f270403069e47c712bbb8ffe2d9e7#-features).

| ID | LiaScript behavior Itembank lacks or only partly matches | Status |
| --- | --- | --- |
| C01 | Numbered appearance and disappearance animations for arbitrary Markdown blocks. Guided steps cover a narrower reveal. | Partial |
| C02 | Multiple blocks synchronized to a single animation step. | Missing |
| C03 | Inline word or phrase animation inside a paragraph. Authored highlighting exists, but not arbitrary timed inline reveal. | Partial |
| C04 | CSS animation classes composed with lesson steps. | Missing |
| C05 | Automatic in-course text-to-speech of lesson comments using browser speech or a backup engine. Itembank exports audio drill packs, a different flow. | Partial |
| C06 | Default speaker configured per document, then overridden per slide and per comment. | Missing |
| C07 | Multiple languages and voices within one spoken passage. | Missing |
| C08 | Text hidden from visual reading but available for speech during playback. | Missing |
| C09 | Spoken comments synchronized with numbered visual steps. | Missing |
| C10 | Recorded audio comments played in step order. | Missing |
| C11 | Short video comments in a learner-movable and resizable overlay. | Missing |
| C12 | Inline and block playback buttons for authored words or passages, including language-learning examples. | Missing |
| C13 | Browser-assisted translation of course text, with opt-out and language exceptions for code or foreign-language comments. | Missing |
| C14 | Separate narrator and language settings per lesson and generated speech mode. | Missing |

### D. Quizzes, self-checks, and surveys

Sources: [quiz taxonomy](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#quizzes), [settings and feedback](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#tweaks), [survey taxonomy and classrooms](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#surveys--classrooms). Itembank's single and multiple choice, table classification, fill, ordering, drag and drop, visual, and code checks are existing broad analogues. Rows below describe narrower differences, not absence of quizzes.

| ID | LiaScript behavior Itembank lacks or only partly matches | Status |
| --- | --- | --- |
| D01 | Quiz controls embedded directly inside arbitrary prose, lists, tables, and diagrams, with more than one answer field in a single content block. Itembank has discrete questions and printed cloze. | Partial |
| D02 | Dropdown selection quiz that permits rich Markdown options and several accepted options. `fill` has accepted strings, not this inline control. | Partial |
| D03 | Matrix quiz combining single-choice and multiple-choice rows under one header. Itembank table classification is narrower. | Partial |
| D04 | Gap text that combines typed fields and dropdowns across a long authored passage. | Missing |
| D05 | Text quiz placed inside an ASCII diagram, image-like figure, or table cell. | Missing |
| D06 | Generic quiz escape hatch that takes arbitrary learner input and script-defined checking. Itembank's scorer deliberately accepts only declared types. | Missing |
| D07 | Unlimited retry-until-solved self-check as the default, with trial count shown instead of a conventional mark. Itembank has practice retries and attempt evidence, but not this exact general default. | Partial |
| D08 | Per-quiz maximum trial count with automatic resolution after the limit. | Unverified |
| D09 | Per-quiz show-solution button configured on, off, or after a chosen number of wrong trials. Itembank has runtime feedback tiers, not this author flag. | Partial |
| D10 | Per-quiz hint button configured on, off, or after a chosen number of wrong trials. Itembank has authored tier rules, not this author flag. | Partial |
| D11 | Arbitrarily many progressive hints attached to each quiz in document syntax. Itembank has a bounded hint ladder. | Partial |
| D12 | Per-field or per-row partial-solution reveal for gap text and matrix quizzes. Itembank's `fill` score is all or nothing. | Missing |
| D13 | Per-quiz row randomization of vector and matrix items via one authored flag. Itembank has selection and bank-level position checks, but this exact control was not found. | Unverified |
| D14 | Custom solved, failed, and resolved messages authored per quiz. | Missing |
| D15 | Per-quiz weighted score for SCORM export. Itembank does not export SCORM. | Missing |
| D16 | Quiz-associated scripts that transform or log an answer, react to checks, or consume quiz input. Itembank's runtime owns scoring and evidence. | Missing |
| D17 | Quizzes generated or transformed through macros, including a reusable custom quiz grammar. | Missing |
| D18 | Optional quiz answer obfuscation in delivered source. Itembank withholds keys through the runtime; this exact export option is absent. | Missing |
| D19 | Standalone, ungraded text-input survey. Itembank has learner notes, but not a survey builder. | Missing |
| D20 | Ungraded single-choice vector survey. | Missing |
| D21 | Ungraded multiple-choice vector survey. | Missing |
| D22 | Ungraded single-choice matrix survey. | Missing |
| D23 | Ungraded multiple-choice matrix survey. | Missing |
| D24 | Survey result scripting and immediate aggregate display. | Missing |
| D25 | Classroom session joining, live peer responses, and teacher-visible activity for a shared course. | Missing |

### E. Tables, charts, diagrams, and computation

Sources: [automatic table plots](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#fun-with-tables), [ASCII diagrams](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#ascii-art), [chart notation](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#charts), [JavaScript components](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#javascript-or-js-components).

| ID | LiaScript behavior Itembank lacks or only partly matches | Status |
| --- | --- | --- |
| E01 | Treat an ordinary Markdown data table as a switchable chart without separately defining a visual item. Itembank has bounded plots and tables in lessons, but no general table-to-chart switch. | Partial |
| E02 | Automatic chart type inference from table shape and value range. | Missing |
| E03 | Line, scatter, box, bar, radar, pie, funnel, geographic map, heatmap, parallel coordinates, graph, and Sankey chart families from table data. Itembank's linked line plot and visual questions cover only a small subset. | Partial |
| E04 | Change chart type with a `data-type` author attribute while retaining the table as source data. | Missing |
| E05 | Default chart visibility toggle, including table-first or chart-first view. | Missing |
| E06 | Table transposition as a chart/data presentation option. | Missing |
| E07 | Chart attributes for axes, title, labels, shape, color, line type, and other visual configuration. | Partial |
| E08 | Chart values animated across teaching steps. | Missing |
| E09 | Geographic map charts using linked GeoJSON shape data. | Missing |
| E10 | ASCII-art diagrams automatically recognized and rendered into shapes with boxes, connectors, arrows, emoji, styling, and titles. Itembank can render explicit diagrams, but not this ASCII authoring grammar. | Partial |
| E11 | SVG embedded with `foreignObject` and experimental scripted SVG behavior. | Missing |
| E12 | Data-driven chart notation distinct from table plots, including multiple series and plot styling. | Partial |
| E13 | Arbitrary ECharts visualizations loaded through author scripts or macros. | Missing |
| E14 | Reusable interactive charts and visual libraries imported from community templates. | Missing |
| E15 | State changes in one lesson control feeding another chart, diagram, text block, or component through named script outputs. Itembank has bounded self-contained controls. | Missing |
| E16 | General user input widgets in lesson components, including buttons, sliders, color, date, time, select, checkbox, textarea, and others. Itembank has specific controls, not an author-level widget grammar. | Partial |
| E17 | Author-written JavaScript computations inside lesson text with asynchronous execution, messages, and output rendering. | Missing |

### F. Coding lessons and extensions

Sources: [interactive code blocks](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#interactive-code-blocks), [code and scripts](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#code), [macro imports](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#macros).

| ID | LiaScript behavior Itembank lacks or only partly matches | Status |
| --- | --- | --- |
| F01 | Any author code fence can become an editable, runnable lesson example with an adjacent output panel. Itembank has `check` questions and bounded lesson run controls, but not blanket conversion. | Partial |
| F02 | Executable examples in many languages through author-chosen browser or external runtimes. Itembank's code question and lesson runner support a narrower set. | Partial |
| F03 | Multi-file coding projects declared in lesson Markdown. | Missing |
| F04 | Load arbitrary external libraries or compiler resources for a specific coding example. | Missing |
| F05 | Code execution return values re-rendered as Markdown, HTML, or nested LiaScript. | Missing |
| F06 | Script `send`, `register`, and `dispatch` messaging between interactive components. | Missing |
| F07 | Custom script error handling and asynchronous output states authored inside the course. | Missing |
| F08 | Author-provided input and output macros that wire code examples to other elements. | Missing |
| F09 | Importable extension templates for language runners, simulations, and domain components. | Missing |

### G. Delivery, storage, export, and ecosystem

Sources: [runtime README](https://github.com/LiaScript/LiaScript/tree/c2e37e36440f270403069e47c712bbb8ffe2d9e7#-features), [state connectors](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#state), [publishing](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#publishing), [tools and exporter](https://github.com/LiaScript/docs/blob/17a777dfb028c7979f2e3204090452c95a01c134/README.md#projects).

| ID | LiaScript behavior Itembank lacks or only partly matches | Status |
| --- | --- | --- |
| G01 | Installable browser PWA with cached interpreter and courses. Itembank has an installed desktop shell and offline HTML, not the same PWA. | Partial |
| G02 | Browser database persistence of reader, task, and quiz state for a hosted course. Itembank saves local evidence and sessions through its runtime, a different storage flow. | Partial |
| G03 | SCORM 1.2 connector that saves course state in a compatible LMS. Itembank's LTI integration is a different standard. | Missing |
| G04 | Custom state connector base for a third-party backend. | Missing |
| G05 | Export a LiaScript course as PDF. Itembank can extract PDF sources, but no equivalent full course PDF export was found. | Missing |
| G06 | Export as SCORM and IMS packages for an LMS. Itembank's native package and LTI do not provide these. | Missing |
| G07 | Export as a static web or project package through the LiaScript exporter. Itembank builds an offline quiz and a restore package, not this whole-course publishing form. | Partial |
| G08 | Host one source document on GitHub, GitLab, a public file host, or a plain web server and share its reader URL without an Itembank server. | Missing |
| G09 | Direct browser load of a course URL, local file or ZIP, or local directory through the public course reader. Itembank's source import and package restore are different workflows. | Partial |
| G10 | Export from LiveEditor to GitHub Gist, Nostr, or a data URI for direct sharing. | Missing |
| G11 | Reader-level QR and browser-native sharing controls. | Missing |
| G12 | GitHub topic based discovery of public courses and reusable templates. Itembank has a private local course shelf, not a public course index. | Missing |
| G13 | Open-courSe workflow for forking, editing, translating, and proposing Git changes to a public course. | Missing |
| G14 | Peer-to-peer offline-first classroom collaboration. | Missing |
| G15 | Shareable course references over decentralized protocols such as IPFS. The docs appendix names other protocols as a to-do, so they are not counted as shipped. | Unverified |

## Existing overlaps deliberately excluded from the gap count

Itembank already has plain Markdown source, offline lesson/quiz use, local persistence, quiz scoring, single and multiple choice, several structured item types, fill fields, code questions, source citations, math rendering, glossary definitions, semantic callouts, static fallbacks, continuous and guided reading, progressive reveal, scoped highlighting, a comparison slider, a linked line plot, audio drill export, local desktop packaging, and LTI. These are *not* claims of identical authoring syntax or equal range. Their evidence is in the [shipped item taxonomy](../../README.md#item-types), [source-to-course contract](../SOURCE-TO-COURSE.md), [capability profiles](../../capabilities.py), and lesson renderer and tests named above.

## Limits and next comparison step

The inventory lists 113 feature-level gaps or parity questions. It does not assume those gaps are desirable. In particular, arbitrary authored scripts, external embeds, open sharing, classroom state, and LMS connectors would need separate decisions about execution authority, rights, egress, accessibility, and recovery. The user's explicit scope is to record before selecting. The next pass can assign keep/prototype/backburner/decline dispositions by learner job and actual cost, without treating LiaScript compatibility as the goal.

No LiaScript code or assets were copied into Itembank. No learner content or private source was sent to LiaScript.
