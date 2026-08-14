# Phase 16 research stream 06: lesson feature and style atlas

**Research date:** 2026-08-13

**Access date for web sources:** 2026-08-13

**Scope:** inventory possibilities before selecting a Phase 16 subset
**Evidence labels:** **Observed** means directly supported by a cited source or
the current repository. **Inference** means a conclusion drawn from observations.
**Recommendation** means a proposed itembank decision for stream 07 synthesis.

## 1. Scope and research questions

This report asks what a source-to-course system may need to express, render,
author, validate, and degrade across six deliberately separate layers:

| Layer | Question | Must not silently control |
|---|---|---|
| Content semantics | What role does a passage or object play, such as warning, example, or uncertainty? | Color, layout, or voice alone |
| Interaction behavior | What can the learner do, such as disclose, annotate, compare, predict, or manipulate? | The truth or assessment meaning of content |
| Visual theme | How are stable semantics presented through type, spacing, color, density, and motion? | Teaching sequence, facts, citations, or scoring |
| Teaching strategy | Why and in what order does the learner encounter explanation, action, feedback, and transfer? | A proprietary visual identity or decorative skin |
| Output mode | Is the artifact a reading, note, reference, guided lesson, practice activity, or assessment? | A false assumption that notes are short lessons |
| Authoring workflow | Was the artifact manually composed, extracted, synthesized, transformed, inserted, or upgraded? | Unreviewed provenance or invisible semantic changes |

The report covers small reading interactions, semantic emphasis, note outputs,
full-learning outputs, authoring workflows, transferable publishing conventions,
open-source implementation leads, and missing-feature tests in EMT or health,
mathematics, computer science, and knowledge courses. It does not select a
visual brand for Phase 17 and does not authorize a grammar change.

### Governing constraints

**Observed.** The current contract requires one parser, scorer, and evidence
store; additive format changes; local evidence and banks; runtime authority for
assessment; useful plain-file degradation; accessible equivalents for rich
interactions; cited and visibly synthesized AI work; and audit-before-upgrade.
The research program also requires inventory before ranking.

**Inference.** The durable unit should be a small semantic vocabulary composed
into several output modes. A separate document model per style, note type, or
interaction would create drift and make legacy upgrades harder to review.

**Recommendation.** Treat the atlas as a capability space, not a backlog. Stream
07 should accept only capabilities that pass teaching-purpose, accessibility,
portable-fallback, provenance, validation, and authoring-cost gates.

## 2. Existing itembank research reviewed

### 2.1 Inventory and reuse verdict

| Existing artifact | Date | Valid findings reused | Claims requiring refresh or correction |
|---|---:|---|---|
| `2026-08-09-lesson-display-editor.md` | 2026-08-09 | Readable measure, semantic figures and captions, focusable code, anchored navigation, and source editor preference remain useful implementation hypotheses. | Several competitor and license facts were assumptions. Any dependency choice, browser behavior, or 2026 market claim must be rechecked. Its rejection of sidenotes was a product choice, not a universal accessibility rule. |
| `2026-08-09-visual-design.md` | 2026-08-09 | Separate reading typography from application chrome; use semantic labels, restrained emphasis, and theme-independent meaning. | Product behavior and trend percentages were often secondary or marketing-grade. Specific fonts, token values, and the Paper and Ledger direction belong to Phase 17, not this semantic atlas. |
| `2026-08-10-ui-inspiration-missing-surfaces.md` | 2026-08-10 | Corrected hover-only glosses to explicit disclosure; distinguished reader flow from gated learning; required inspectable recommendation rationales and visible pending status. | Its browser claims about CSS Anchor Positioning and some product mechanics are time-sensitive. Print assumptions are not binding under current Planning Directives. |
| `2026-08-10-lesson-style-catalogue.md` | 2026-08-10 | Expository, checked prose, worked example, case narrative, and artifact-first are useful teaching-strategy candidates. Productive failure is a sequencing parameter, not a visual style. | Prior `SHIP` verdicts predate the source-to-course reframe and cannot bypass Phase 16 synthesis. The rejection of explorable explanations was too broad: bank-authored JavaScript remains refused, but renderer-owned typed simulations are still viable. |
| `2026-08-10-style-registry-mechanics.md` | 2026-08-10 | House rules and style rules must be distinct; style cannot change facts, citations, objectives, or keys; a small registered vocabulary is preferable to prose-only prompting. | The proposed exact registry shape and inheritance model are design hypotheses. They need tests against note modes and source extraction, which were not central to that report. |
| `2026-08-10-lesson-item-coupling.md` | 2026-08-10 | Lessons and banks can have distinct lifecycles while retaining objective and source links; generated coverage should be derived rather than duplicated. | Its chapter-size defaults and file-shape verdicts need re-evaluation for course artifacts beyond bank-linked lessons. |
| `FEATURES.md`, `PITFALLS.md`, `SUMMARY.md` | 2026-08-05 | Retrieval, worked examples, transfer, inspectable evidence, and human review of AI output remain relevant. | Product inventories are older and assessment-centered. Some sources are secondary, and none supplies the complete reading, note, comparison, or legacy-enhancement atlas requested here. |
| Current `model.py`, `surfaces/lesson.py`, daemon routes, and round-trip tests | inspected 2026-08-13 | Current code has one lesson parser, `## TERMS`, `[[term]]`, `[!KEY]`, `[!EXAMPLE]`, `[!CHECK:]`, lesson sources and source records, cases, styles, math, code, and runtime-gated checks. | There is no demonstrated general contract for warnings, misconceptions, uncertainty, highlights, annotations, bookmarks, marginalia, source comparison, note-output identities, or user-selectable transformations. |

### 2.2 What remains genuinely missing from prior research

Prior work explored lesson displays and a shortlist of instructional styles.
It did not adequately compare note creation with learning creation, model
annotations as learner-owned data, specify source comparison, distinguish
semantic emphasis from visual themes, inventory publishing genres, or test a
single capability model across health, mathematics, computer science, and a
knowledge course. It also did not record current open-source activity and
architecture consistently.

## 3. Sources and evidence quality

All web sources below were accessed 2026-08-13. Product behavior uses current
first-party help, documentation, specifications, or repositories where
available. Learning evidence uses reviews or meta-analyses and states important
limitations.

| Source | Type | What it supports | Limitations |
|---|---|---|---|
| [NotebookLM Help](https://support.google.com/notebooklm/answer/16164461) and [source import guide](https://support.google.com/notebooklm/answer/16215270) | Current primary product docs | Source-grounded citations, source selection, study guides and other derived outputs, supported inputs, copied or synced source behavior | Describes features, not learning effectiveness |
| [NotebookLM chat guide](https://support.google.com/notebooklm/answer/16179559), [mind maps](https://support.google.com/notebooklm/answer/16212283), and [flashcards or quizzes](https://support.google.com/notebooklm/answer/16958963) | Current primary product docs | Citation preview and jump-to-source, saved responses, output style settings, interactive maps, explain controls, progress and CSV export | Vendor claims and workflow documentation, not independent evaluation; mind maps are unavailable in its mobile app at the access date |
| [Brilliant About](https://brilliant.org/about/), [FAQ](https://brilliant.org/faq/), and [Learning Paths](https://brilliant.org/help/features/what-are-learning-paths/) | Current primary product docs | One-concept progressions, prediction before instruction, manipulation, tailored feedback, practice with scaffold removal, cumulative review | Brilliant reports its own experiments without publishing methods or effect estimates on these pages; effectiveness claims are marketing claims |
| [Readwise Reader highlights, tags, and notes](https://docs.readwise.io/reader/docs/faqs/highlights-tags-notes) and [exports](https://docs.readwise.io/reader/docs/faqs/exporting) | Current primary product docs | Keyboard paragraph navigation, highlighting, tagging, marginal display, jump to original context, Markdown and template-driven export | Product workflow evidence only; synchronized service model differs from itembank's local data preference |
| [RemNote Reader](https://help.remnote.com/en/articles/6690975-learning-from-pdfs-and-files-with-the-remnote-reader) and [help index](https://help.remnote.com/en/) | Current primary product docs | Source annotation, linked notes and flashcards, hierarchies, templates, concept/descriptor structure, guided PDF learning | Product claims, cloud conversion, and paid feature boundaries do not establish learning efficacy or local portability |
| [Obsidian callouts](https://obsidian.md/help/callouts) and [bookmarks](https://obsidian.md/help/Plugins/Bookmarks) | Current primary product docs | Plain-Markdown callout convention, custom rendering, bookmarks over files, headings, blocks, and searches | Plugin and CSS flexibility can create inconsistent semantics; Obsidian behavior is not the itembank contract |
| [PhET interaction style guide](https://phetsims.github.io/binder/) | Primary project design documentation | Keyboard and screen-reader patterns for manipulatives, explicit expanded state, on-demand help, alternative accessible interaction models | Component guidance is simulation-specific and does not prove equivalent learning outcomes for every alternate interaction |
| [W3C WCAG 2.2, SC 1.4.13 explanation](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html) and [ARIA tooltip pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) | Standard and guidance | Dismissible, hoverable, persistent content; focus behavior; distinction between tooltip and interactive dialog | ARIA tooltip pattern explicitly lacks task-force consensus and is not a complete touch design |
| [EPUB 3 overview](https://www.w3.org/publishing/epub32/epub-overview.html) | W3C publishing standard overview | Reflowable web content, semantic inflection, accessibility integration | Does not itself solve cross-reader annotation interoperability |
| [QTI 3 specification index](https://www.1edtech.org/standards/qti/index) | Industry standard | Portable assessment content, results, accessibility integration, web components and custom interactions | Assessment exchange is not a general lesson or note authoring contract |
| [H5P Interactive Video repository](https://github.com/h5p/h5p-interactive-video), [H5P repositories](https://github.com/orgs/h5p/repositories), and [semantics schema](https://github.com/h5p/h5p-interactive-video/blob/master/semantics.json) | Primary open-source code | Schema-driven editors, typed content libraries, build/package model, branching and interactive media ecosystem | Large JavaScript ecosystem and per-content-type packages create integration and supply-chain cost |
| [MyST guide](https://mystmd.org/guide) and [developer guide](https://mystmd.org/guide/developer) | Primary open-source docs | Markdown plus roles/directives, cross-references, scientific publishing, structured AST and multiple outputs | Broader publishing stack than itembank needs; adopting it wholesale risks a second document model |
| [Retrieval practice classroom systematic review](https://eric.ed.gov/?id=EJ1319572) and [Annual Review synthesis](https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010419-051019) | Systematic review and narrative review | Retrieval practice benefits across materials and classrooms | Classroom review coded 50 experiments and found heterogeneous effects; neither proves that every inline quiz or UI treatment helps |
| [Concept-map meta-analysis](https://eric.ed.gov/?id=EJ1179084) | Random-effects meta-analysis | 142 effects, n=11,814; construction was associated with larger benefit than study-only maps | Included varied domains, treatments, and controls; association between moderator and benefit is not a guarantee for generated maps |
| [Critical-thinking concept-map meta-analysis](https://www.sciencedirect.com/science/article/pii/S1747938X22000501) | Random-effects meta-analysis | 21 studies, 1,695 learners; moderate effects with allocation-type moderation | Moderate to high heterogeneity and possible missing studies limit precision |
| [Worked-example study](https://www.sciencedirect.com/science/article/pii/S0747563208002161) and [example variability and self-explanation study](https://pubmed.ncbi.nlm.nih.gov/9514690/) | Controlled learning studies | Worked solutions can support initial skill acquisition; variability and self-explanation matter for transfer | Domain and learner expertise moderate results; examples should fade rather than remain permanent scaffolds |

### 3.1 Product and program pattern sample

| Family and examples | Observed pattern | Transferable convention | What not to infer |
|---|---|---|---|
| Source-grounded workspace: NotebookLM | Selected sources ground chat and generated outputs; citations preview and return to context; output types remain distinct | Claim-to-source navigation, selected-source scope, output identity, saved derived artifacts | Grounded generation is not automatically a coherent course or validated assessment |
| Interactive learning: Brilliant | Short concept progressions combine pretesting, manipulation, feedback, increasing difficulty, later unscaffolded practice and review | Prediction can precede instruction; scaffold removal and changed-context practice belong outside visual novelty | A proprietary interaction, animation, mascot, or layout is not the pedagogical method |
| Reading and annotation: Readwise Reader | Keyboard reading, highlights, tags, notes, marginal display on wide screens, source-context return, configurable Markdown export | Annotation should remain navigable, exportable, and tied to its source | Collecting highlights alone is not elaboration, retrieval, or a lesson |
| Note-linked learning: RemNote | Source reader connects highlights to notes and flashcards; structured concepts, templates, hierarchy, and guided modes coexist | Source notes, reference structure, and retrieval artifacts can share links without becoming one output | Automatic PDF conversion and AI tutoring do not prove source fidelity or course quality |
| Markdown knowledge workspace: Obsidian and plugins | Callout markers remain visible in Markdown while themes and plugins enrich them; bookmarks can target multiple object types | Durable visible markers, configurable presentation, links across separate roots | Arbitrary callout names and community plugins do not provide a controlled teaching vocabulary |
| Interactive simulation: PhET | Accessible components may expose different but equivalent interaction models through keyboard, labels, state, and structured controls | Renderer-owned simulations need designed accessible interaction, not merely an after-the-fact description | One generic “simulation” block cannot cover every model or construct |
| Active textbook: Runestone | Prose, code, Parsons-style activities, questions, and logged work form a course sequence | Artifact-first and active-reading patterns can remain lesson-centered | Its platform architecture and evidence store should not be transplanted into itembank |
| Publishing and standards: EPUB, MyST, QTI | Semantics, cross-references, packaging, accessibility, and multiple presentations are separated in different scopes | Reuse vocabulary and conformance lessons while keeping lesson and assessment authorities distinct | Standards coverage does not guarantee reader support, accessible authoring, or good teaching |

## 4. Categorized feature inventory

### 4.1 Reading interactions

| Capability | Semantic object | Interaction behavior | Benefit and use | Weakness or misuse | Portable and accessible fallback | Atlas disposition |
|---|---|---|---|---|---|---|
| Linked definition | Term identity plus definition, source, scope, aliases | Hover, focus, or tap opens a small disclosure; explicit open and close | Removes lookup friction while keeping context | Too many triggers fragment reading; definitions can leak assessment answers | `[[term]]` remains readable with `## TERMS`; keyboard focus, tap, Escape, persistent panel, glossary link | Accept foundation |
| Citation preview | Claim-to-source locator | Focus, hover, or tap previews excerpt and opens source context | Makes verification immediate | Quoted context can be misleading if too short; inaccessible popovers obscure text | Visible citation marker and end reference; explicit source link; preview is optional enhancement | Accept foundation |
| Source preview | Artifact or section link | Side sheet or inline expansion shows source metadata and excerpt | Supports direct reading and provenance | Can become a miniature reader inside every page | Plain link plus locator and source record | Prototype |
| Highlight | Learner-selected span plus color-independent category | Select text, choose category, navigate highlights | Externalizes attention and supports later notes | Highlighting alone can become passive collecting; anchors break after edits | Store exact quote, surrounding context, source fingerprint and semantic label; render as list if anchoring fails | Prototype |
| Annotation | Learner-authored note anchored to a range, block, figure, or source | Create, edit, reply, filter, jump to anchor | Supports elaboration, questions, and review | Personal notes can be mistaken for source claims; conflict after source edits | Separate learner-owned file or evidence object, author and timestamp visible; orphan queue on mismatch | Prototype |
| Marginalia | Short annotation presentation, not a new semantic type | Wide screens show margin; narrow screens show inline disclosure or list | Preserves reading flow for brief notes | Margins vanish or collide at narrow widths and high zoom | Same annotation object, alternate placement; never margin-only | Defer presentation |
| Bookmark | Stable location plus optional label | Toggle and list; resume or revisit | Low-cost navigation and study planning | Bookmarks without intent become clutter | Durable locator list, works without rich renderer | Accept |
| Reading position | Artifact version plus last meaningful location | Resume and show changed-since-last-read | Supports continuity | Scroll percentage is unstable after edits | Anchor to heading/block identity and fingerprint; offer nearest location after change | Prototype |
| Inline preview link | Link metadata and safe excerpt | Explicit preview before navigation | Reduces context switching | Network, privacy, stale metadata, and unsafe remote embeds | Link remains usable; cached metadata labeled with retrieval date | Defer |
| Source comparison | Two or more cited passages aligned by claim, concept, or locator | Side-by-side on wide screens, stacked synchronized sections on narrow screens; difference and agreement filters | Exposes conflict, terminology changes, and synthesis basis | Visual diff implies textual equivalence; AI alignment may invent correspondence | Comparison table with each passage, locator, edition, and explicit relation; no color-only diff | Prototype high priority |
| Reader highlighting by author | Semantic emphasis, not arbitrary yellow markup | Theme renders role consistently | Guides attention | Overuse destroys hierarchy | Plain labels and headings preserve role | Accept only through named roles |

**Observed.** NotebookLM currently lets users hover citations for quoted text
and select them to navigate to source context. WCAG 2.2 requires hover or focus
content to be dismissible, hoverable, and persistent. The ARIA tooltip guidance
says interactive content belongs in a non-modal dialog, not a tooltip.

**Inference.** “Hover definition” should be shorthand for a multi-input
disclosure contract. Touch and keyboard cannot be afterthoughts, and content
with links, source controls, or actions is a popover/dialog rather than a tooltip.

**Recommendation.** Fix the interaction contract for accessibility, but let the
learner select presentation density, automatic hover opening, margin versus
inline placement, and whether citations preview or open directly.

### 4.2 Semantic emphasis vocabulary

These are content roles. A theme may vary their presentation, but may not merge
roles whose authoring rules, risk, or screen-reader labels differ.

| Role | Teaching purpose | Required fields or checks | Common misuse | Plain-file form |
|---|---|---|---|---|
| Key idea | State the concept that organizes the section | Concise claim; objective link when applicable | Repeating every heading | Labelled block or emphasized sentence |
| Remember | Mark retrieval-worthy information | Reason it matters; avoid answer keys | Turning the lesson into flashcard wallpaper | `Remember:` label |
| Warning | Flag safety, destructive action, contraindication, or severe failure | Severity, condition, action, source for factual safety claims | Styling ordinary advice as danger | `Warning:` block with explicit action |
| Common error or misconception | Name a plausible wrong model and repair it | Error, why it seems plausible, discriminator, correction | Ridiculing learners or merely saying “do not” | Labelled contrast paragraph |
| Tip | Offer an optional efficiency or practice tactic | Applicability and limits | Presenting required knowledge as optional | `Tip:` block |
| Expert nuance | Add context useful beyond the core objective | Audience or level; source or synthesis label | Scope creep and authority theater | Labelled aside |
| Prerequisite | Identify needed prior knowledge | Stable objective or artifact link; action if missing | Generic “know algebra” text | Prerequisite list with links |
| Example | Instantiate a concept | What feature exemplifies the concept | Example without explanation | Heading or `[!EXAMPLE]` block |
| Counterexample | Show a boundary or refute overgeneralization | Target rule and why this case fails | Rare exception that distracts novices | Labelled example with contrast |
| Worked example | Demonstrate a procedure with rationale | Goal, steps, decisions, checks, and variation | Copyable procedure without fading or transfer | Ordered steps plus explanation |
| Summary | Compress the completed section | Map to covered objectives and unresolved questions | Replacing instruction with a summary | Heading and list/table |
| Uncertainty | State confidence, disputed evidence, missing evidence, or scope limits | Kind of uncertainty, basis, affected claim, source/date, review status | Decorative confidence badges or invented percentages | `Uncertainty:` paragraph near claim |
| Source excerpt | Preserve source wording | Quote boundary, locator, edition, rights basis | Passing a paraphrase off as quotation | Block quote plus citation |
| Synthesis | Join claims across sources | Source set, synthesis label, contradictions retained | Blending sources into false consensus | Labelled prose with citations |

**Recommendation.** Use a small core vocabulary plus typed metadata, not a new
block for every synonym. Candidate core roles are `key`, `warning`, `error`,
`tip`, `example`, `counterexample`, `summary`, and `uncertainty`. `Remember` can
be a key subtype; expert nuance can be a tip subtype; source excerpt and
synthesis require provenance semantics rather than visual callout semantics.
This is a prototype proposal, not an authorized grammar.

### 4.3 Note outputs are not short lessons

| Output | Primary job | Typical structure | Learner action | Validation focus | Why it is not merely a short lesson |
|---|---|---|---|---|---|
| Notebook page | Capture and connect learner or source material | Free sections, backlinks, embeds, annotations | Write, link, revisit | Ownership, anchors, provenance | It preserves thinking and fragments rather than supplying a teaching sequence |
| Hierarchical outline | Expose structure and scope | Nested headings and bullets | Expand, collapse, reorder | Coverage and hierarchy | It omits explanatory transitions and practice by design |
| Cornell notes | Support cue, note, and summary review | Cue column, note body, bottom summary | Recall from cues, summarize | Each cue maps to notes; layout degrades linearly | Its retrieval scaffold is the product, not concept instruction |
| Concept map | Represent typed relationships | Nodes and labelled edges | Construct, edit, trace relations | Every edge has a relation; textual adjacency fallback | The relation graph, not prose order, carries meaning |
| Glossary | Provide reference definitions | Term, definition, aliases, scope, source, links | Lookup and compare | Unique identity, collisions, citation | Alphabetical or linked reference is intentionally non-sequential |
| Formula sheet | Support compact retrieval and application | Formula, variables, units, conditions, derivation link, example | Locate and verify applicability | Units, domains, symbol collisions, source | Compression and fast lookup are goals; derivation can remain linked |
| Timeline | Preserve chronology and causation claims | Events, dates/ranges, actors, source, relation | Scan, filter, compare periods | Date precision, disputed dates, no false causation | Time is the organizing axis |
| Comparison table | Make dimensions and contrasts explicit | Entities by consistent criteria, evidence cells | Compare and detect gaps | Same criteria, unknown cells explicit, citations | Symmetry and scanability matter more than narrative flow |
| Study guide | Orient review toward objectives | Scope, objectives, key resources, prompts, practice links | Plan and retrieve | Blueprint alignment and omissions | It routes learning rather than replacing it |
| Source-extracted notes | Preserve selected source claims | Extract/paraphrase label, locator, quote, comment, confidence | Verify and organize | Text fidelity, locator, source version, extraction status | Provenance and selection are central; teaching may be absent |

**Observed.** NotebookLM exposes reports, study guides, briefings, mind maps,
flashcards, quizzes, and saved notes as different outputs. Its mind map supports
expand/collapse and node-to-chat interactions, but the current mobile app lacks
mind maps and notes. Meta-analytic evidence suggests concept mapping can help,
with construction showing larger associated benefits than merely viewing maps,
but studies and comparison conditions are heterogeneous.

**Inference.** A generated concept-map image is a preview, not a sufficient
learning activity. An itembank concept map needs typed, editable relations and
a textual fallback. Likewise, Cornell notes require a cue-driven review mode;
two-column styling alone does not make Cornell notes.

**Recommendation.** Define an output-mode identity with its own required
structure and validator profile. Reuse shared semantic blocks and provenance.
Do not run “make this shorter” and call the result notes.

### 4.4 Full-learning outputs

| Output or strategy | Minimal learning sequence | Best fit | Failure mode | Graceful degradation |
|---|---|---|---|---|
| Guided lesson | Orient, engage, explain, apply, continue | New conceptual learning | Linear slideshow with decorative clicks | Continuous semantic reading with all explanations present |
| Worked-example sequence | Model, explain decisions, complete steps, vary context, fade support | Novice procedural learning | Permanent imitation and no transfer | Numbered worked solution plus independent problems |
| Prediction and reveal | Commit prediction, observe result, explain discrepancy | Causal models, code behavior, cases | Guessing gate with no diagnostic value | Prompt followed by clearly separated reveal and rationale |
| Simulation | Manipulate named parameters, observe model, explain, test limits | Dynamic systems and quantitative intuition | Unvalidated toy that presents model output as reality | Static snapshots, parameter table, model assumptions, worked cases |
| Case or vignette | Context, decision point, staged evidence, consequence, debrief | EMT, health, law, ethics, operations | Trivia in narrative clothing; premature keyed disclosure | Ordered scenario stages with explicit reveal markers |
| Inquiry | Question, evidence gathering, competing explanations, claim, reflection | Science and knowledge courses | Unguided discovery for novices | Evidence packet and scaffolded prompts |
| Socratic lesson | One diagnostic question at a time, learner reasoning, bounded response, synthesis | Misconception diagnosis and explanation | Endless chatbot or concealed answer guessing | Written question path with branching notes and terminal explanation |
| Artifact-first lesson | Predict/run/inspect/modify/make | Computer science, data, systems | Syntax burden overwhelms concept | Captured initial artifact, expected observations, and non-executable analysis |
| Practice | Retrieval or application, feedback, retry policy | Consolidation | Repetition without objective or changed context | Printable or static item set with separate runtime session |
| Transfer task | Apply in structurally related but changed context | Course-quality gate | Cosmetic word substitution | Explicit changed dimensions and rubric, prose remains pending |
| Cumulative review | Sample prior objectives over time and interleave when suitable | Retention and discrimination between methods | Opaque scheduling or overload | Review list with rationale and source objectives |

**Observed.** Brilliant currently describes lessons that begin with pretesting,
use visual manipulation and custom feedback, then increase complexity. It also
describes associated practice where lesson scaffolds fall away and review sets
combine preceding lessons. These are first-party descriptions, not independent
proof of effect. Retrieval-practice reviews find generally positive classroom
effects, but variation means an interaction must be judged by its retrieval
and feedback design, not its quiz appearance.

**Recommendation.** Fix safety and assessment boundaries, but make teaching
strategy selectable only when it remains pedagogically valid for the objective
and learner. Reader versus guided view can be learner-selectable. Prediction-
first versus explanation-first should be chosen by an author or course director
using prior knowledge, stakes, and objective demand, with a learner escape path.

## 5. Style and output-mode taxonomy

### 5.1 Transferable conventions from publishing genres

The entries below abstract conventions. They do not copy wording, branded
characters, page designs, proprietary assets, or a living author's distinctive
voice.

| Genre-inspired style | Transferable conventions | Appropriate use | Reject or constrain |
|---|---|---|---|
| Beginner-friendly plain-language guide | State the job, define jargon near first use, short steps, common-error repair, confidence-building examples, cross-references | First exposure and practical onboarding | Do not imitate a named series' branding, icons, jokes, catchphrases, layout, or authorial voice; do not oversimplify safety-critical distinctions |
| Reference handbook | Stable entry templates, fast scanning, prerequisites, parameters, exceptions, cross-links, version/date | Lookup and field use | Do not force reference order into a guided lesson |
| Visual explainer | One relationship per figure, progressive labelling, captions that state the intended inference, text alternative | Spatial, causal, and quantitative models | Do not make color, motion, or image inspection the only carrier of meaning |
| Field guide | Identification cues, look-alikes, environment/context, quick comparisons, uncertainty | Recognition and practical classification | Avoid false certainty and image-only identification |
| Casebook | Authentic source excerpt, issue framing, questions, competing interpretations, later synthesis | Law, history, ethics, clinical reasoning | Preserve source context and rights; do not convert disagreement into one neat answer |
| Worked textbook | Model solution, rationale annotations, paired variation, faded steps, independent transfer | Mathematics and procedures | Avoid one example followed by near-copy exercises only |
| Socratic dialogue | Short prompts, explicit misconception branches, learner articulation, synthesis | Reasoning and diagnosis | Do not mimic a distinctive writer; avoid endless conversational detours |
| Exam-review book | Blueprint map, high-yield distinctions, time strategy, common traps, mixed sets, error log | Standardized or knowledge exams | Do not let “high yield” erase prerequisites, source uncertainty, or construct fidelity |
| Formula/reference sheet | Dense but consistent entries, symbol definitions, domains, units, minimal examples | Later review and open-reference work | Not a first-teaching format |
| Timeline or atlas | Stable axes, legends, locators, cross-scale navigation, comparisons | Chronology, geography, anatomy, systems | Do not imply causation from proximity or simplify disputed boundaries silently |

### 5.2 Orthogonal style controls

| Control | Examples | Who may choose | What stays fixed |
|---|---|---|---|
| Reading density | spacious, standard, compact | Learner | Semantics, order, citations, target sizes, reflow |
| Navigation | continuous, guided steps, outline rail | Learner when all views are valid | Prerequisites, gating authority, source identity |
| Theme | light, dark, high contrast, low stimulation | Learner | Labels and non-color meaning |
| Explanatory register | concise, standard, expanded | Learner within author-approved variants | Facts, uncertainty, objective demand, assessment content |
| Teaching strategy | expository, worked, prediction-first, case, artifact-first, inquiry | Author or course director; learner may choose among approved peers | Safety sequence, prerequisite needs, assessment boundary |
| Output mode | reading, notes, reference, guided lesson, practice, test | Course plan or explicit user request | Artifact identity and provenance |
| Voice | calm, direct, formal, conversational | Author-configurable within house constraints | No impersonation, no fact or citation changes, no model-as-authority styling |

### 5.3 Fixed versus selectable

**Fixed by pedagogy or safety:** objective alignment; prerequisites that prevent
harm; source quotation boundaries; uncertainty and contradiction; assessment
key disclosure; scoring authority; required alternative representation;
warning severity; the distinction between authored source, extraction,
paraphrase, synthesis, and learner note.

**Fixed by accessibility:** logical DOM order; keyboard operation; visible
focus; label in name; non-color semantics; text alternatives; reduced-motion
behavior; hover/focus disclosure persistence and dismissal; touch target and
reflow gates; an equivalent for drag, drawing, or visual-only tasks.

**Potentially user-selectable:** density, font and contrast preferences,
continuous versus guided view, inline versus margin annotations, citation
preview behavior, glossary auto-open behavior, optional narration, and approved
explanation length. Selection must not create a second parser or content truth.

## 6. Authoring and transformation atlas

| Workflow | Inputs | Required preview or audit | Validation | Acceptable write boundary |
|---|---|---|---|---|
| Manual composition | Objective, sources, author text | Rendered and plain-file preview | Grammar, links, accessibility, sources, style rules | Explicit author file |
| Source extraction | Source span and locator | Side-by-side source and extracted object | Exact quote or labelled paraphrase, fingerprint, omissions | New draft artifact or approved insertion |
| AI synthesis | Multiple cited source claims | Claim-level citation and conflict view | Source support, uncertainty, objective fit, hallucination review | Draft only unless bounded write approved |
| Template conversion | Existing structured artifact plus target output | Field mapping and loss report | Required fields, unmapped content, identity preservation | New derived artifact by default |
| Style transformation | Accepted content plus style constraints | Semantic diff and rendered variants | Facts, citations, objectives, block identities, key content unchanged | New variant or reviewed replacement |
| Semantic block insertion | Existing lesson plus proposed role | Local diff showing why the role adds learning value | Role-specific required fields and overuse checks | Bounded insertion after approval |
| Legacy enhancement | Existing lesson or question | Audit, identity/provenance report, proposed diff, fallback view | No silent key/difficulty/meaning change; links and lint pass | Approved file only, recoverable |
| Note generation | Selected sources/objectives plus named output mode | Source coverage and output-mode preview | Mode-specific contract, extraction labels, gaps | Separate note artifact, not lesson overwrite |
| Full lesson generation | Objective map, prerequisites, source support, learner context | Treatment rationale and end-to-end lesson storyboard | Coherence, practice and transfer, citations, accessibility | Missing treatment only |

### 6.1 Transformation invariants

Every transformation should emit a manifest or review summary containing:

1. Input artifact identities, versions, fingerprints, and approved roots.
2. Requested output mode, teaching strategy, style, and semantic operations.
3. Preserved facts, citations, objectives, block identities, and assessment
   meaning.
4. Added, removed, moved, or reclassified semantic blocks.
5. Source-derived text versus generated synthesis versus learner-owned text.
6. Validation results, unresolved uncertainty, and graceful-degradation result.
7. Destination, approval state, and undo method.

**Recommendation.** A style transformation may change organization and phrasing
only within an explicit review boundary. It must never silently transform a
note into a lesson, a lesson into a test, a warning into a tip, an uncertain
claim into a key idea, or a source extract into model-authored prose.

## 7. Open-source implementation leads

Repository activity is a snapshot observed 2026-08-13 and should be rechecked
at dependency-selection time. “Architecture” is a concise inference from the
repository and project documentation, not a complete code audit.

| Lead | Observed activity and license | Architecture or useful pattern | Applicability | Risk and verdict |
|---|---|---|---|---|
| [H5P](https://github.com/h5p) | Organization showed active repositories updated through 2026-07-29; many content libraries identify MIT licenses, but each dependency needs its own review | Core plus separately versioned JavaScript content-type libraries; `semantics.json` drives editor fields; packaged assets and upgrades | Study typed activity schemas, editors, branching scenarios, interactive books, hotspots, and static summaries | Direct adoption is heavy and may duplicate runtime authority. Prototype schema/editor ideas, do not embed H5P wholesale |
| [MyST Markdown](https://github.com/jupyter-book/mystmd) | Active 2026 release line documented; MIT | Markdown parser produces a structured document tree with directives, roles, cross-references, citations, math, code, and multiple renderers | Strong reference for open semantic directives and graceful publishing | Wholesale adoption risks a second parser. Borrow syntax and AST lessons only unless one-parser integration is proven |
| [Runestone Components](https://github.com/RunestoneInteractive/RunestoneComponents) | Activity and exact license must be rechecked before use | Web components and services for active textbooks, including code, Parsons problems, questions, and interaction logging | Reference for artifact-first lessons and accessible alternate response forms | Large platform assumptions and evidence model do not fit directly. Defer dependency, study interaction contracts |
| [Hypothesis client](https://github.com/hypothesis/client) | Activity and license must be rechecked before use | Web annotation client anchored to documents, with groups, threads, tags, and selectors | Reference for robust anchoring, orphan handling, and annotation ownership | Full client is too broad for early Phase 16. Prototype a small local selector model |
| [JupyterLab](https://github.com/jupyterlab/jupyterlab) | Activity and BSD-3-Clause license should be verified at selection time | Notebook document, kernels, outputs, MIME rendering, extension system | Reference for executable narratives and captured output provenance | Notebook output is another mutable content source. Reject as the core lesson format; permit linked notebook artifacts later |
| [Quarto](https://github.com/quarto-dev/quarto-cli) | Activity and GPL-2.0 license should be verified at selection time | Pandoc-based publishing pipeline for Markdown, code execution, citations, and formats | Reference for multi-output publishing and execution separation | Licensing and a second parsing/build stack require careful review. Defer integration |
| [Tufte CSS](https://github.com/edwardtufte/tufte-css) | Long-lived open project; MIT should be verified in repository at selection time | CSS conventions for sidenotes and readable long-form layout | Reference for marginal presentation and figure width | Presentation inspiration only; margins cannot carry unique semantics |
| [Web Annotation Data Model](https://www.w3.org/TR/annotation-model/) | W3C Recommendation | Body, target, selectors, motivations, provenance | Strong conceptual model for local highlights and annotations | Full standard may be more than needed. Prototype a compatible subset |
| [EPUB 3](https://www.w3.org/publishing/epub32/epub-overview.html) | W3C standard family | Packaged reflowable web publication with semantic inflection and accessibility | Export and portability reference | Reader support varies. Do not use EPUB as the editable source of truth |
| [QTI 3](https://www.1edtech.org/standards/qti/index) | Final release family with accessibility integration | Portable test and item structures, results, web markup, custom interactions | Assessment import/export reference and accessibility vocabulary | Not a lesson contract and must not displace itembank scoring |

### 7.1 Architecture implications

**Observed.** H5P demonstrates the authorability benefit of schemas that drive
editor controls, but also the maintenance cost of many separately versioned
content types. MyST demonstrates that a small textual extension can map to a
structured tree and multiple outputs. Web Annotation separates annotation
body from a target selector. QTI keeps assessment exchange distinct from
general publishing.

**Inference.** itembank should prefer one parsed semantic tree, renderer-owned
interaction components, and separately stored learner annotations. A block
registry needs capability metadata, author form metadata, fallback rendering,
accessibility behavior, and validator rules, but not executable lesson code.

## 8. Cross-cutting effects

### Accessibility

- Hover is an enhancement, never the only trigger. Focus and explicit tap or
  activation must expose the same information.
- Interactive popovers need explicit close behavior, predictable focus, and
  narrow-screen placement. Tooltips cannot contain focusable controls.
- Drag, drawing, spatial manipulation, timelines, maps, and simulations need
  keyboard and structured-text equivalents that test the same construct.
- Semantic labels must remain in the accessibility tree and plain file. Color,
  icon, position, animation, and typography cannot be the only role signal.
- Source comparison must preserve reading order at zoom and on narrow screens.
- Generated text alternatives require author review, especially for health,
  diagrams, charts, and assessment stimuli.

### Portability

- Markdown remains the editable source layer; semantic extensions must have
  useful visible text when unsupported.
- Rich runtime state, indexes, cached previews, and generated thumbnails are
  derived and disposable.
- Notes and annotations should be separate learner-owned artifacts so source
  updates do not rewrite personal work.
- Every interactive has a static representation containing the model,
  assumptions, instructions, and at least one meaningful state.

### Privacy

- Highlights, annotations, reading position, and bookmarks are learner data.
  Keep them local by default and never embed private notes into a shared lesson
  silently.
- Remote preview fetching leaks URLs and interests. Require an explicit policy,
  cache provenance, and a no-network fallback.
- AI synthesis should receive only approved roots and selected source spans.

### Provenance

- Store source identity, version or fingerprint, locator, extraction method,
  and whether text is quotation, paraphrase, synthesis, or learner note.
- Comparison and uncertainty blocks must preserve disagreement rather than
  select a winner without an explicit rationale.
- Failed anchors become visible orphans, not silently relocated annotations.

### Authorability

- Every semantic role needs: when to use, when not to use, required fields,
  good and bad examples, lint rules, rich preview, plain fallback, and upgrade
  behavior.
- A palette of dozens of cards is not authorability. Authors should choose a
  teaching purpose, after which the editor proposes the correct semantic role.
- AI authoring should start from objective and treatment, not requested tone.

## 9. Missing-feature test suite

Each test is designed to fail visibly when current itembank or a proposed
capability model cannot express, render, author, validate, or degrade an
important behavior. Tests use synthetic material only.

| ID | Domain and fixture | Capability under test | Required contexts | Failure exposed | Pass condition |
|---|---|---|---|---|---|
| MF-01 | EMT: oxygen administration term in a short airway lesson | Linked definition with contraindication-safe wording | Mouse, keyboard, touch, screen reader, plain Markdown | Hover-only access; definition obscures trigger; definition leaks a keyed answer | Same definition and citation on every input; dismissible and persistent; plain glossary works; assessment mode can suppress keyed term detail |
| MF-02 | EMT: chest-pain case with evolving vitals | Case stages, prediction, runtime-authorized reveal | Desktop, phone, offline, plain file | Future evidence visible early; UI rather than runtime controls key disclosure | Stages remain ordered in file; rich UI reveals only granted stage; offline static version labels deferred sections without exposing key |
| MF-03 | EMT: protocol warning that differs by jurisdiction and date | Warning plus uncertainty and source comparison | Reader, source view, upgrade review | Warning styled but uncited; uncertain local protocol flattened into universal rule | Severity, scope, jurisdiction, date, sources, and conflict are explicit; update diff preserves prior provenance |
| MF-04 | Mathematics: completing the square | Worked example, rationale annotations, faded steps, variation and transfer | Guided and continuous reader | Example renders, but fade and independent transfer cannot be authored or checked | One semantic sequence renders both ways; learner can complete omitted steps; transfer changes surface features; plain file is coherent |
| MF-05 | Mathematics: slope controlled by two points | Typed simulation with static cases | Keyboard, touch, screen reader, reduced motion, offline, plain file | Pointer drag is the construct; no text alternative; renderer executes arbitrary authored code | Renderer-owned parameters and bounds; equivalent numeric controls and table; three static states and assumptions in file |
| MF-06 | Mathematics: formula sheet using `m` for mass and slope | Formula reference with scopes, units, symbol collisions | Search, narrow screen, export | Pretty formula sheet silently conflates symbols | Each formula declares variables, units/domain, source and objective; collision warning; linear fallback |
| MF-07 | Computer science: predict a loop trace, run, inspect, modify | Artifact-first lesson and prediction/reveal | No runtime, configured runtime, failed execution, screen reader | Execution output becomes untracked lesson truth; answer exposed before prediction | Source remains authoritative; output is labelled derived state; static trace exists; failure does not block explanation |
| MF-08 | Computer science: recursion misconception | Common-error block, counterexample, Socratic branch | Reader, guided, tutor unavailable | Style change turns diagnostic branch into generic chat or reveals answer | Misconception and discriminator are semantic; finite branch ends in explanation; tutor is optional enhancement |
| MF-09 | Knowledge course: two histories disagree on an event's cause | Source comparison and uncertainty | Wide, narrow, keyboard, plain file | Side-by-side-only layout; synthesis erases disagreement; citations lose locators | Stacked fallback preserves source identity and relation; synthesis labels inference; unknown remains unknown |
| MF-10 | Knowledge course: chronology with disputed dates | Timeline note output | Reader, screen reader, export | Timeline is image-only or orders uncertain dates falsely | Structured events include date precision and source; textual chronological list and uncertainty survive |
| MF-11 | Any domain: create Cornell notes from one lesson | Output-mode-specific authoring | Manual, source extraction, AI draft | Two-column CSS passes as Cornell notes; cues cannot drive recall | Cue, notes, summary and source links validate; plain file linearizes predictably; cue-only review works |
| MF-12 | Any domain: create concept map from objectives | Typed relationships and learner construction | Desktop, touch, keyboard, screen reader, plain file | Generated image has unlabeled edges or no editable/text equivalent | Nodes have stable IDs; edges have relation labels; adjacency table fallback; learner edit is distinct from generated suggestion |
| MF-13 | Any domain: highlight, annotate, then revise source | Durable learner annotations | Source unchanged, moved, edited, deleted | Notes silently attach to wrong sentence or disappear | Quote plus context plus fingerprint resolves exact matches; uncertain matches enter orphan review; learner data remains intact |
| MF-14 | Any domain: transform an expository lesson to concise exam review | Style transformation invariants | Diff review, lint, plain file | Facts, warnings, citations, difficulty, or objective coverage change under “style” | Semantic diff reports every change; protected fields are unchanged; omissions are explicit and reversible |
| MF-15 | Any domain: add a new warning to a legacy lesson | Legacy enhancement | Audit, proposal, approval, rollback | Cosmetic rewrite of entire lesson; stable identity lost | Initial audit identifies learning need; bounded insertion only; fingerprint/history and undo recorded |
| MF-16 | Any domain: derive extracted notes and a guided lesson from the same chapter | Note versus learning creation | Source review, output comparison | Both are the same summary at different lengths | Notes preserve extracts and structure; lesson supplies orientation, explanation, activity, feedback, application and transfer; shared claims cite same locators |
| MF-17 | EMT, math, CS, and history versions of “tip” | Semantic-role applicability | Author form and lint | One decorative callout vocabulary treats safety warning, heuristic, and disputed nuance alike | Role-specific fields and severity checks distinguish them; theme may style them without merging semantics |
| MF-18 | Any domain: citation preview with a long quotation | Disclosure accessibility | 400% zoom, keyboard, magnifier, touch | Panel cannot be hovered, dismissed, or scrolled; focus is obscured | WCAG 1.4.13 behavior, explicit open view, stable reading order, end citation fallback |

### 9.1 Capability-model test harness

For each fixture, run five gates:

1. **Express:** can one authored representation encode the purpose without raw
   HTML or lesson-authored script?
2. **Render:** do continuous reader and guided UI preserve the same semantics?
3. **Author:** can a human and agent discover the right role, preview it, and
   receive actionable validation?
4. **Validate:** do lint and runtime boundaries catch missing fields, source
   drift, accessibility failures, and assessment leakage?
5. **Degrade:** does plain Markdown, offline mode, narrow screen, and unavailable
   interaction still convey the core meaning?

A feature fails if any required gate has no testable contract. Visual polish
cannot compensate for a semantic or degradation failure.

## 10. Implications for Phase 16 contracts and skills

### Learner flow

- Course entry should distinguish “read source,” “use notes,” “take a guided
  lesson,” “practice,” and “test.” These are different commitments.
- Reading interactions should remain available without forcing the learner
  into guided pacing.
- Guided lessons should show why an action is requested and allow recovery to
  continuous reader mode unless runtime assessment rules require otherwise.
- Notes, bookmarks, and annotations need a course-level return surface, not
  only local icons in a lesson.
- Citation and comparison actions should move between claim, excerpt, and full
  context without losing the learner's position.

### Semantic content contract

- Represent teaching roles, not card colors.
- Give blocks stable identity so annotations, transformations, citations, and
  legacy upgrades can refer to them.
- Separate content block, interaction specification, and derived state.
- Add role-specific metadata only after the four-domain fixtures prove it is
  needed and a readable fallback exists.
- Keep learner annotations out of lesson source files by default.

### Agent skills

- Ask for target, objective, learner, source support, output mode, and teaching
  strategy before tone or theme.
- Find existing artifacts before drafting. Report whether the task is link,
  extract, synthesize, transform, insert, or enhance.
- For notes, run the chosen note-mode contract. For lessons, demonstrate a
  learning sequence and transfer. Never substitute one for the other.
- Emit provenance, uncertainty, semantic diff, validation, and undo summary.
- Refuse voice imitation and protected layout replication; translate only
  general conventions.

### Legacy upgrades

- Inventory current semantic cues even when they are informal prose.
- Propose a mapping to typed roles without rewriting unrelated wording.
- Preserve stable IDs, locators, citation history, item keys, difficulty, and
  objective links.
- Verify rich and plain-file views before approval.
- Treat ambiguous identity or changed assessment meaning as review blockers.

## 11. Accept, reject, defer, prototype, and open tables

These are stream 06 recommendations for synthesis, not binding product changes.

### Accept

| Capability or rule | Reason | Evidence confidence |
|---|---|---|
| Six-layer separation | Prevents a theme or style from changing pedagogy, truth, or output identity | High, architectural |
| Accessible multi-input linked definitions | Directly serves user vision and has clear W3C behavior | High for accessibility, medium for learning effect |
| Semantic emphasis with visible labels | Portable, authorable, and theme-independent | High |
| Distinct note-output contracts | Notes have different jobs, structures, and validation from lessons | High, conceptual and product evidence |
| Distinct full-learning contract | A lesson needs sequence, action, explanation, application, and transfer | High, binding product contract |
| Claim-level citations and synthesis labels | Required for source-grounded trust and review | High |
| Reader and guided views over one semantic source | Supports preference without duplicate truth | High |
| Runtime-owned assessment disclosure | Existing invariant and needed for prediction, feedback, and cases | High |
| Static and accessible representation for every rich interaction | Binding product direction and accessibility need | High |
| Audit-before-upgrade and semantic diffs | Prevents cosmetic rewrites and hidden assessment changes | High |

### Reject

| Candidate | Reason |
|---|---|
| Hover-only definitions or citations | Excludes keyboard and touch, and fails robust disclosure behavior |
| A separate proprietary format per style or output | Creates incompatible authoring and migration paths |
| Note generation as “shorten the lesson” | Loses mode-specific structure, provenance, and learner action |
| Generated concept map as an uneditable image | Omits typed relationships, construction, and accessible fallback |
| Lesson-authored JavaScript | Violates the existing refusal of bank-authored executable content and creates unsafe, unvalidated behavior |
| Theme-selected semantic meaning | Color or card treatment cannot decide whether content is a warning, uncertainty, or key idea |
| Style transformations that may alter citations, objectives, facts, or assessment meaning | “Style” is not authority to revise substance |
| Direct copying of Brilliant, named book-series layouts, branded devices, assets, or distinctive voice | Legally and pedagogically unnecessary; conventions can be abstracted |
| Opaque AI one-shot publish | Conflicts with staged, cited, reviewable course construction |

### Defer

| Candidate | Why deferred | Revisit trigger |
|---|---|---|
| Full collaborative annotation threads | Significant identity, moderation, merge, and privacy work | Local single-learner annotations prove value and stable anchoring |
| Remote rich-link previews | Privacy, network, stale metadata, and security costs | Explicit network and caching policy exists |
| EPUB as editable source | Reader interoperability and annotation gaps | Export requirements and conformance fixtures exist |
| Wholesale H5P, MyST, Quarto, or Jupyter adoption | Risks duplicate parser/runtime or oversized stack | Prototype proves integration through the one parser and license review passes |
| Marginalia as default presentation | Fragile at narrow widths and zoom | Phase 17 visual tests demonstrate robust alternate placement |
| Free-form learner programmable simulations | Security, validation, accessibility, and provenance cost | Renderer-owned typed simulations are insufficient for a named objective |
| Voice and broad style marketplace | Quality and maintenance scale poorly | Core strategy and output contracts are stable and measurable |

### Prototype

| Prototype | What it must answer |
|---|---|
| Definition and citation disclosure | Can one behavior satisfy mouse, keyboard, touch, magnification, screen reader, assessment leakage, and plain-file gates? |
| Source comparison | Can cited disagreement remain clear in side-by-side, stacked, screen-reader, and Markdown forms? |
| Local annotation anchoring | Can exact quote, context, fingerprint, and stable block identity survive edits without wrong attachment? |
| Typed simulation | Can renderer-owned parameters express math and health models with keyboard controls and meaningful static cases? |
| Note-mode trio | Can outline, Cornell notes, and concept map share semantics while retaining distinct validators and learner actions? |
| Style transformation diff | Can a concise exam-review variant preserve every protected semantic field and report omissions? |
| Legacy warning insertion | Can an agent add one valuable semantic block without cosmetic rewrite or identity drift? |

### Open questions

| Question | Decision evidence needed |
|---|---|
| What is the minimum core semantic block set? | Authoring trials and four-domain fixtures measuring ambiguity and overclassification |
| Should note artifacts share the lesson parser or compose a broader course-document parser? | One-parser prototype showing byte-identical behavior for current banks and useful plain Markdown |
| Where do learner highlights, annotations, and bookmarks live? | Local data model prototype covering ownership, export, move, edit, delete, and orphan recovery |
| When may a learner choose teaching strategy? | Rules for prerequisite risk, novice expertise, assessment conditions, and equivalent objective coverage |
| How is uncertainty represented without fake precision? | Source conflict fixtures, authoring rules, and reviewer comprehension tests |
| Which simulation primitives cover enough objectives? | EMT, math, CS, and knowledge-course prototype inventory, plus accessible-equivalence testing |
| Which citations may preview quoted text? | Rights policy, excerpt-size policy, source permission, and local versus remote handling |
| How should an agent detect style imitation? | Prompt rules, review checklist, and tests against named-series requests without judging broad genre conventions as protected |

## 12. Concrete recommendations and risks

1. Phase 16 should define a capability registry whose entries include semantic
   purpose, allowed contexts, required fields, validator profile, renderer
   behavior, accessible equivalent, plain fallback, evidence behavior, and
   authoring guidance. It should not define Phase 17's visual tokens.
2. Prototype definitions, citations, source comparison, annotation anchoring,
   one typed simulation, and three note modes before freezing grammar.
3. Use the full MF-01 through MF-18 suite as a design gate. At least one test in
   every domain must exercise plain-file, touch, keyboard, screen-reader,
   narrow-screen, and offline behavior.
4. Protect output identity. A note, reading, reference, guided lesson, practice
   set, and test may share blocks but need distinct intent and validation.
5. Make visual theme and density broadly user-selectable. Restrict teaching
   strategy selection to author-approved alternatives. Never make safety,
   provenance, accessibility, or assessment authority optional.
6. Require every AI operation to name its workflow and produce a provenance and
   semantic-diff report. “Restyle” must be mechanically narrower than “revise.”
7. Borrow architecture ideas from open standards and active open-source tools,
   but integrate only through itembank's one parser and runtime boundaries.

The largest risk is capability inflation: dozens of visually attractive blocks
can overwhelm authors and learners while adding little learning value. The
second risk is false portability: Markdown syntax may look readable while the
meaning actually depends on hidden JavaScript, color, layout, or derived state.
The third is transformation drift: AI can produce fluent variants that quietly
change scope, certainty, citations, or assessment demand. The final Phase 16
subset should therefore be smaller than this atlas and should be justified by
the missing-feature tests, not competitor counts.
