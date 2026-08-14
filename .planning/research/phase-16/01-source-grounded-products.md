# Source-grounded product landscape

**Research stream:** 01

**Access date for all web sources:** 2026-08-13

**Scope:** Current NotebookLM, renamed Gemini Notebook in July 2026, plus a
small set of adjacent source-grounded and tutoring products. This document
studies product behavior and transferable patterns. It does not reproduce
protected content, visual assets, branding, or interaction details.

## 1. Scope and research questions

This stream asks:

1. How does current Gemini Notebook move from source collection to questions,
   navigation, citations, chat, notes, study aids, and audio or visual outputs?
2. Which patterns improve source inspection and learner agency?
3. Which patterns fail when the primary object is a lesson-centered course
   organized by objectives, prerequisites, practice, tests, and evidence?
4. What should itembank accept, reject, defer, prototype, or leave open?

The comparison unit is a documented capability, not the competitor's visual
expression. Product documentation establishes what is observable. Claims that
a feature improves learning are treated as claims unless supported here by
evidence. This stream does not attempt a learning-science review, which belongs
primarily in stream 02.

### Existing itembank research reviewed

Before the current-product check, this stream inventoried `.planning/research/`
and reviewed the prior landscape and UI artifacts most relevant to source use,
lesson flow, study aids, tutoring, citations, and visual transformations. The
inventory found no prior NotebookLM-specific study. It found a substantial
course-adjacent evidence base that should be reused rather than rediscovered.

| Existing artifact | Date and prior scope | Still-valid finding reused here | Stale, limited, or deliberately not reused |
|---|---|---|---|
| `FEATURES.md` | 2026-08-05, broad feature landscape | Chat should not be the primary tutor surface; deterministic answer-key withholding is structurally stronger than prompt obedience; a bounded model may restate already released material | The product survey predates the current Gemini Notebook workflow and explicitly had no hands-on trials. Its “every AI-tutor product” wording is broader than its cited sample, so this report does not repeat that universal claim |
| `2026-08-09-landscape-widening.md` | 2026-08-09, sequencing, medical learning, study modes, PKM, standards | A visible runtime gate is more legible than conversational refusal; learner-pulled post-verdict explanation differs from pre-answer hints; objectives and blueprint shape must outrank generic quiz generation | Its AI-tutor section declared itself fast-moving and valid only through 2026-08-23. It discussed the 2025 study-mode wave, not Gemini Notebook's July 2026 rename, expanded Studio, interactive media, research import, or agentic artifact creation. Secondary-source descriptions were not carried forward as current facts |
| `2026-08-09-lesson-display-editor.md` | 2026-08-09, reading surface and editor | Focus must accompany hover; inline disclosure works better than desktop-only margin behavior; continuous reader orientation should use semantic navigation rather than engagement pressure | It is a renderer study, not a source-grounded workflow study. Its proposed print obligation was later identified in `PLANNING-DIRECTIVES.md` as non-binding, so print is not used as a veto here |
| `2026-08-09-visual-design.md` | 2026-08-09, visual identity and competitor survey | Take structural teaching patterns rather than product chrome; keep source or provenance material visually secondary but inspectable; do not copy a competitor's motion, assets, or identity | Several competitor observations are marked assumed or rely on search digests and secondary showcases. They remain inspiration only, not evidence of current product behavior |
| `2026-08-10-ui-inspiration-missing-surfaces.md` | 2026-08-10, cross-phase UI input | Source-grounded assistance should be contextual; open chat must not replace a visible disclosure state; Brilliant-style pagination does not transfer to a lesson that must also read continuously; every pointer interaction needs a semantic alternative | The artifact explicitly says it is input, not a specification. Its section B5 calls print a requirement, but the later binding directive says no authoritative print requirement exists. This report retains plain-file degradation because the current source-to-course contract requires it, not because of that stale print claim |
| `2026-08-10-lesson-style-catalogue.md` and `2026-08-10-style-registry-mechanics.md` | 2026-08-10, pedagogical formats and registry mechanics | A style is mainly ordering and budget over semantic teaching blocks; predict-before-explain is conditional; visual novelty should not create bespoke grammar; portable source remains primary | The proposed registry fields and parser costs were phase-specific design proposals. This stream does not adopt them as settled Phase 16 grammar |
| `2026-08-09-extraction-subjects-bilingual.md`, `PITFALLS.md`, and `SUMMARY.md` | 2026-08-05 to 2026-08-09, extraction, audit, and synthesis | Citation-per-claim, exact locators, explicit unknown or conflict state, and source identity are stronger than uncited coverage conclusions | These files focus on bank audit and extraction rather than learner citation navigation. This report extends their provenance principle but does not assume their proposed syntax is the final course contract |
| `.planning/UI-SPEC.md` | Current project UI contract reviewed as prior UI audit input | Evidence before inference; source quotation and locator must remain separate from generated synthesis; long citations may not be silently truncated; deep links and keyboard navigation are explicit verification targets | Its current surfaces predate the Phase 16 course reframe. Existing component names are constraints and reusable primitives, not proof that the end-to-end source-to-lesson flow has been designed |

**Gap-focused browsing decision.** Prior research already covered generic
Socratic tutoring, checked prose, learner-pulled explanations, flashcards,
continuous reading, source locators, and the rejection of chat as the product
spine. New browsing therefore focused on changed or previously absent behavior:
Gemini Notebook's 2026 name and ecosystem position; its current source types,
copy-versus-sync behavior, citation navigation, source subset controls, Studio
inventory, prompt inspection, research import, mobile and offline media,
interactive audio, generated visuals, sharing boundaries, and agentic artifact
creation. Adjacent-product browsing was limited to current source-scope,
tutoring, citation, and artifact-version patterns needed to test the remaining
gaps.

## 2. Sources

All sources below were accessed 2026-08-13. Primary product documentation is
used for current behavior. No hands-on account inspection was performed, so
undocumented keyboard, screen-reader, export, and artifact internals remain
unknown.

| Source | Type | What it supports |
|---|---|---|
| [Google, “NotebookLM is now Gemini Notebook”](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/) | Primary release announcement | July 2026 rename and ecosystem direction |
| [Google Help, “Learn about Gemini Notebook”](https://support.google.com/gemininotebook/answer/16164461?hl=en) | Primary help | Product purpose, source-grounded chat, supported modalities, privacy summary |
| [Google Help, “Create a notebook”](https://support.google.com/gemininotebook/answer/16206563?hl=en-GB) | Primary help | Three-panel organization, Studio artifacts, source categorization, prompts, sharing, analytics |
| [Google Help, “Add or discover new sources”](https://support.google.com/gemininotebook/answer/16215270?hl=en) | Primary help | Source types, limits, copies versus synchronization, source selection, source guide, Fast and Deep Research |
| [Google Help, “Use chat”](https://support.google.com/gemininotebook/answer/16179559?hl=en) | Primary help | Source-only chat, citation preview and navigation, Learning Guide mode, saved responses, agentic chat |
| [Google Help, “Create and add notes”](https://support.google.com/gemininotebook/answer/16262519?hl=en) | Primary help | Manual and saved-response notes, source conversion, editing and deletion |
| [Google Help, “Use Mind Maps”](https://support.google.com/gemininotebook/answer/16212283?hl=en) | Primary help | Branch navigation, expand and collapse, node-to-chat questions, download |
| [Google Help, “Generate Flashcards or Quizzes”](https://support.google.com/gemininotebook/answer/16958963?hl=en) | Primary help | Generation controls, explanations, results, review and retake |
| [Google Help, “Generate Audio Overview”](https://support.google.com/gemininotebook/answer/16212820?hl=en) | Primary help | Formats, steering, playback, background use, source-grounded interactive audio, download |
| [Google Help, “Generate Video Overviews”](https://support.google.com/gemininotebook/answer/16454555?hl=en) | Primary help | Formats, visual-style control, steering, playback, download, inaccuracy warning |
| [Google Help, “Generate an Infographic”](https://support.google.com/gemininotebook/answer/16758265?hl=en) | Primary help | Visual-summary controls, download, and factual or visual inaccuracy warning |
| [Google Help, “Get started with the mobile app”](https://support.google.com/gemininotebook/answer/16296687?hl=en) | Primary help | Mobile feature subset, share-to-source flow, offline audio, flashcard review behavior |
| [Google Help, “Notebooks in Gemini Apps”](https://support.google.com/gemininotebook/answer/17003757) | Primary help | Cross-product sync, grounding boundary, chat-as-source behavior, retention differences |
| [Google, “NotebookLM adds Deep Research and support for more source types”](https://blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-deep-research-file-types/) | Primary release announcement | Research-plan and source-import workflow |
| [Google, “Video Overviews are now available in 80 languages”](https://blog.google/innovation-and-ai/models-and-research/google-labs/notebook-lm-audio-video-overviews-more-languages-longer-content/) | Primary release announcement | Multilingual overview availability and summary intent |
| [OpenAI Help, “Using Study Mode in ChatGPT”](https://help.openai.com/en/articles/11780217-study-mode) | Primary help, adjacent product | Socratic prompts, layered explanation, checks, uploaded materials, personalization, limitations |
| [Perplexity Help, “What are Projects?”](https://www.perplexity.ai/help-center/en/articles/10352961-what-are-spaces) | Primary help, adjacent product | Research workspace, full-text retrieval, sharing, connected sources |
| [Perplexity Help, “What is Internal Knowledge Search?”](https://www.perplexity.ai/help-center/en/articles/10352914-what-is-internal-knowledge-search) | Primary help, adjacent product | Explicit source scope, file citations, access-controlled retrieval |
| [Perplexity Help, “Creating assets with Perplexity”](https://www.perplexity.ai/help-center/en/articles/12528830-creating-assets-with-perplexity-overview) | Primary help, adjacent product | Cited generated documents and versioned prompt iteration |

## 3. Observed facts, inference, and recommendation

### 3.1 Observed facts: Gemini Notebook's workflow

#### Entry, sources, and organization

- A notebook begins with imported, uploaded, pasted, or discovered sources.
  Documented inputs include PDFs, web pages, public captioned YouTube videos,
  audio, images, Google Workspace files, Office files, Markdown, CSV, ePub, and
  Gemini chats. Imported web, video, and audio material can be reduced to
  extracted text or transcripts. Google Drive sources can synchronize, while
  other imports are copies.
- The desktop workspace is organized around Sources, Chat, and Studio. Sources
  can be selected or excluded for a chat or generation. With at least five
  sources, the product can label and categorize them, and users can edit that
  organization.
- Opening a source provides a source guide with an automatically generated
  summary. Citation selection can navigate to the cited location in context.
- Fast Research returns candidate web or Drive sources for review before
  import. Deep Research plans and performs broader web research, then offers a
  report and its source set for selective import.
- Source limits, availability, and import fidelity differ by format. For
  example, a YouTube source uses its transcript, nested web content is not
  imported, and a lost Drive permission can make a source inaccessible.

#### Questions, chat, citations, and notes

- Chat answers are grounded in the selected notebook sources. The help page
  states that citations can contain source text or images, show a preview on
  hover, and jump to the source location when selected.
- Chat can be configured as Default, Learning Guide, or a custom style, and as
  shorter, default, or longer. A response can be saved as a note with its
  formatting and clickable citations.
- Notes can be authored by the user or derived from a chat response. Current
  documentation also describes turning a note into a source, which changes its
  role from an editable workspace artifact to grounded context.
- Gemini Notebook and Gemini have different grounding boundaries. Notebook
  responses are described as exclusive to notebook sources, while Gemini may
  also use web search and other tools. Gemini chat threads can be added as
  notebook context and are then visible to notebook collaborators.
- Paid desktop chat can search the web, run code, create downloadable files,
  charts, and images, and modify artifacts as versions. Google labels these
  functions experimental and calls for user supervision.

#### Study aids and navigation

- Studio can generate reports, data tables, mind maps, flashcards, quizzes,
  audio, video, infographics, and slide decks. Generation can happen in the
  background, and custom prompts remain inspectable on several artifact types.
- Flashcard and quiz generation accepts source selection, a steering prompt,
  difficulty, and amount. Mobile flashcards support flip, shuffle, delete,
  “got it” or “missed it,” review of results, and retaking all or missed cards.
  The broader help documentation describes explanation controls and quiz
  review or retake.
- A mind map branches topics and related ideas. Learners can zoom, expand or
  collapse branches, and select a node to ask a focused chat question.
- Studio reports include predefined study guide, FAQ, and briefing forms plus
  custom or suggested forms. Reports and data tables can export to Google Docs
  or Sheets, but exported changes do not synchronize back.

#### Audio and visual features

- Audio Overview supports Deep Dive, Brief, Critique, and Debate formats,
  language, length, expertise or topic steering, playback speed, background
  listening, download, and sharing. English interactive mode lets a listener
  interrupt by voice and receive a source-grounded answer before the overview
  resumes. Google warns of inaccuracies and audio glitches.
- Video Overview supports cinematic, explainer, and short formats, language,
  visual style, and steering. Google warns that voices and visuals can be
  inaccurate and that generation may take more than 30 minutes.
- Infographics are single visual summaries with detail, orientation, style,
  language, and focus controls. The help page explicitly warns of visual and
  factual inaccuracies.
- The mobile app supports adding sources from a device share sheet, source chat,
  study aids, audio playback in the background, and downloading audio for
  offline playback. Several desktop features have documented mobile limits.

#### Privacy, provenance, and sharing

- Google states that Notebook uploads, queries, and responses are not used to
  train foundational models unless the user supplies feedback. Terms and human
  review protections differ for consumer, Workspace, and Education accounts.
- A shared viewer can have access to sources and notes. A focused chat-view link
  hides other materials in the default view but does not revoke underlying
  notebook access. This is an important distinction between presentation and
  authorization.
- The product warns users to respect copyright and not upload or share material
  without rights. Generated outputs may be inaccurate. Deletion and retention
  behavior can differ across Notebook and Gemini surfaces.

### 3.2 Observed facts: adjacent products

- ChatGPT Study Mode guides with questions, layered explanations, and checks
  for understanding. It can work from uploaded notes, readings, images, or a
  syllabus and can personalize through optional memory. Its own documentation
  says it may still give direct answers and may make mistakes.
- Perplexity Projects organizes threads and files into a searchable shared
  research workspace. Internal Knowledge Search can explicitly select web,
  organization files, both, or neither, and provides inline file citations.
  Generated documents can retain citations and be revised through prompts with
  version history.

These products are adjacent because they illuminate source scope, tutoring,
artifact review, and provenance. They are not full course models in the cited
documentation.

### 3.3 Inferences

The following are design inferences, not vendor-stated facts.

1. **Gemini Notebook is a source-to-artifact workspace, not a course engine.**
   Its durable organizing object is a notebook and its principal navigation is
   Sources, Chat, and Studio. The documented workflow does not establish stable
   objectives, prerequisites, treatment decisions, an instructional sequence,
   blueprint alignment, or evidence-driven next actions.
2. **Citation navigation is its strongest transferable pattern.** A compact
   answer can remain inspectable because the learner can preview the evidence
   and jump into source context. This supports trust without forcing source and
   synthesis into one undifferentiated document.
3. **Selectable grounding is a useful control but not enough provenance.** A
   checkbox answers “which sources may be used now.” A course also needs to
   answer which version, locator, ownership state, objective, generated claim,
   and accepted artifact a statement belongs to.
4. **Studio favors many parallel transformations.** That makes exploration
   inviting, but it can produce an artifact gallery whose outputs are not tied
   to a learner need or course decision. Automatic generation may amplify this
   problem.
5. **Generated quizzes are study aids, not demonstrated assessment contracts.**
   Difficulty and quantity controls are convenient, but the cited materials do
   not document objective alignment, construct coverage, deterministic scoring
   authority, item-quality validation, pending prose review, or evidence
   semantics.
6. **Audio's best pattern is continuity across modalities.** Background
   listening plus source inspection and questions preserves an inquiry path.
   A podcast-like summary by itself is passive and cannot establish learning.
7. **Generated visuals need a stronger acceptance boundary than text.** Vendor
   warnings about factual and visual inaccuracies imply that an attractive
   visual artifact cannot be accepted as instructional evidence without source
   locators, alternative text, semantic fallback, and review.
8. **Chat is effective as a side channel, not as the spine.** Study Mode shows
   the value of one-question-at-a-time guidance and layered explanation.
   However, chat history is a fragile course map and does not itself provide a
   stable resume point, coverage state, or validated assessment boundary.
9. **Presentation state and access control must be separate.** Gemini Notebook's
   warning that chat view hides but does not revoke access is directly relevant
   to itembank's source excerpts, answer keys, and reviewer-only material.

### 3.4 Recommendations

1. Make the course map and recommended next action the entry point. Keep source
   chat available within the current objective or artifact, not as the home.
2. Adopt a citation interaction that offers a compact preview and a deliberate
   jump to a stable locator. Label source quotation, paraphrase, and generated
   synthesis separately.
3. Expose the active source scope before every grounded generation or question.
   Preserve an artifact-level provenance record after generation rather than
   relying on transient source selection.
4. Treat generated aids as proposals attached to an objective and learning
   purpose. Do not auto-fill a Studio-like gallery merely because sources were
   added.
5. Keep questions produced for exploration or practice outside formal
   assessment until they pass itembank's parser, lint, review, blueprint, and
   runtime contracts.
6. Prototype audio as an optional representation of an accepted lesson segment
   with synchronized outline, transcript, citations, speed controls, and a
   return-to-lesson position. Do not prototype AI-host theater as the core.
7. Prototype a semantic concept map only when edges name a relationship and
   every node has a linear, keyboard-accessible outline fallback. A generic
   topic cloud should not become course navigation.
8. Require every generated visual to disclose its source basis and review
   state. The portable lesson must contain an equivalent caption, explanation,
   data table, or structured description.
9. Use chat tutoring only within runtime-granted disclosure. A model may ask a
   diagnostic question or vary an explanation, but it may not invent a score,
   hint tier, keyed disclosure, or evidence.
10. Preserve source and artifact operations as reviewable, bounded actions:
    find, preview, select, bind, draft, validate, accept, supersede, or undo.

## 4. Pattern inventory

| Pattern | Benefit | Weakness or failure mode | Applicability to itembank |
|---|---|---|---|
| Source selection before query or generation | Makes grounding scope visible and adjustable | Selection is transient and does not prove why a source supports an objective | Accept, then persist source identity, locator, and purpose on accepted artifacts |
| Citation preview plus source jump | Fast verification without losing the synthesis context | Preview can encourage quote-snippet trust without reading surrounding context | Accept with stable locators, context view, provenance labels, and keyboard or touch equivalents |
| Source guide and generated summary | Reduces entry cost for a long source | Summary can substitute for direct reading or flatten uncertainty | Prototype as orientation, never as automatic replacement for source treatment |
| Fast or deep source discovery with review before import | Expands a source set while preserving a selection gate | Search quality and rights status may be unclear; imports can become copies | Accept the review gate; require approved roots, rights metadata, fingerprints, and link/import distinction |
| Source, chat, artifact separation | Keeps raw material, inquiry, and outputs legible | Encourages notebook-first navigation and parallel artifacts without sequence | Accept the separation inside a course workspace, but subordinate it to objectives and next actions |
| Suggested questions and Learning Guide chat | Lowers prompt burden and supports inquiry | Model pacing is inconsistent and can provide answers too early | Prototype within lessons, constrained by purpose and runtime disclosure |
| Save chat response as note | Converts ephemeral synthesis into a reusable object | Risks laundering generated text into apparent source truth | Accept only with generated provenance, citations, draft status, and explicit promotion review |
| Note-to-source conversion | Lets learner-created context participate in grounding | Collapses epistemic roles unless authorship and revision history remain visible | Defer pending a clear source-role and provenance model |
| Background artifact generation and completion notices | Avoids blocking on long generation | Invites speculative output and clutter | Accept for approved jobs with status, cancellation, cost, provenance, and review state |
| Flashcards with missed-item retry | Supports quick retrieval practice and focused repetition | Binary self-rating is weak evidence; generated cards may test trivia | Accept only for objective-aligned retrieval practice, not mastery or formal test evidence |
| Quiz difficulty, amount, and steering controls | Makes generation accessible | “Hard” is not a construct specification; control does not ensure validity | Reject as sufficient authoring contract; retain as secondary convenience after blueprint controls |
| Mind map with collapsible branches and node-to-question | Gives overview and an inquiry doorway | Unnamed edges can imply false relationships; spatial UI may exclude users | Prototype semantic relationship maps with linear fallback and authored edge meanings |
| Audio formats and interactive interruption | Supports hands-free access and alternative explanation | Passive summaries, performance latency, hallucination, voice glitches, weak citation visibility | Prototype transcript-first optional audio, with synchronized citations and lesson continuity |
| Video, slide, and infographic transformations | Can orient or explain spatial and temporal material | Attractive but inaccurate output, accessibility burden, weak portable fallback | Defer generic generation; prototype only a cited visual explanation with human acceptance |
| Inspectable custom generation prompt | Helps reviewers understand intent and reproduce a draft | Prompt alone does not capture model, sources, or output review | Accept as one field in a fuller generation record |
| Artifact export | Supports use outside the originating app | Exports can lose synchronization, state, and provenance | Accept portable authored files as the source of truth; derived exports must name their status |
| Cross-surface notebook sync | Lets users continue in multiple contexts | Grounding, retention, and sharing rules vary across surfaces | Defer broad cross-app sync; first make local course identity and state explicit |
| Chat-only presentation | Focuses a shared experience | Hiding panels does not revoke source access | Reject as an authorization boundary |
| Prompt-versioned generated assets | Supports iterative revision and rollback | Conversational edits can conceal semantic changes | Accept reviewable versions and diffs, with validation before promotion |
| Full-text project search | Recovers prior files and threads | Retrieval does not establish identity, quality, or objective fit | Accept discovery, followed by fingerprinting, binding, and conflict review |

## 5. Cross-cutting effects

### Accessibility

**Observed:** Official documentation describes hover citation previews, touch
mobile controls, audio speed and download, expandable mind maps, and broad
language support. It also documents desktop/mobile feature differences. The
reviewed pages do not provide a complete keyboard or screen-reader contract for
citations, mind maps, flashcards, or generated visuals.

**Inference:** Hover-only citations, spatial maps, flip cards, unlabeled
generated visual relationships, and audio without a synchronized text path are
unsafe patterns to inherit. Feature presence on mobile is not evidence of
equivalent access.

**Recommendation:** Every citation preview must work by hover, focus, activation,
and touch. Mind maps require an ordered outline and named edges. Flashcards need
screen-reader-readable question and answer states without relying on a flip.
Audio and video need transcript, captions, outline navigation, source links,
and an equivalent non-media lesson. Generated images need authored alternatives
and a review state. These behaviors must be prototype verification gates, not
Phase 17 polish.

### Portability and offline behavior

**Observed:** Notebook sources may be copied or synchronized, outputs can often
be downloaded or exported, and mobile audio can be downloaded for offline
playback. Exported Docs or Sheets do not synchronize back. The product itself
requires a signed-in service.

**Inference:** Downloadable output is not the same as a portable semantic
source. A PNG infographic, audio file, or exported report loses interactive
state and may obscure provenance.

**Recommendation:** itembank's authored Markdown remains the accepted lesson.
Rich views, audio, diagrams, and indexes are derived artifacts with recorded
input fingerprints. The plain file must preserve headings, definitions,
callouts, citations, visual explanations, and activity instructions. Offline
loss of generation or chat must not block reading, practice, deterministic
scoring, evidence, or resume.

### Privacy and authorization

**Observed:** Gemini Notebook has account-specific data terms, warns that
feedback can expose interaction context for review, and distinguishes Notebook
from Gemini retention. Shared chat view is a presentation mode, not an access
revocation mechanism. Perplexity similarly scopes connected files and honors
upstream access in the cited enterprise documentation.

**Inference:** “grounded in my files” does not imply local storage, uniform
retention, or safe disclosure. Cross-product context can silently widen who or
what participates.

**Recommendation:** itembank should display active roots, active sources,
destination, and operation before sending material to any hosted backend.
Authorization must be enforced by the runtime and file boundary, never by
hidden UI. Evidence and banks remain on disk. Source excerpts sent for an
approved operation should be minimized and logged locally without recording
secrets or keyed content in model prompts.

### Provenance and citations

**Observed:** Gemini Notebook offers inline citations, previews, source jumps,
source selection, and inspectable generation prompts. Perplexity offers inline
file citations and cited generated documents.

**Inference:** These patterns make verification convenient, but neither a
citation marker nor a prompt proves source adequacy, version stability, rights,
or objective alignment.

**Recommendation:** The semantic contract should distinguish direct quotation,
source-backed paraphrase, generated synthesis, and learner-authored note. Each
accepted source-backed claim needs stable source identity, fingerprint or
version, locator, and access or ownership status. Citation activation should
show enough context to assess the claim and offer a deliberate open-source
action.

### Authorability and review

**Observed:** Current Gemini Notebook exposes prompts for several Studio
artifacts, permits steering by audience or focus, and can export or version
some generated outputs. Generated study aids also expose coarse difficulty and
amount controls.

**Inference:** Natural-language steering is useful for drafting but cannot be
the only authoring contract. It does not guarantee teaching purpose,
accessibility, portable fallback, assessment validity, or stable revision.

**Recommendation:** Agent skills should author semantic roles, not named visual
cards: orientation, definition, source excerpt, explanation, worked example,
misconception, prediction, check, feedback, transfer, and citation. Each role
needs when-to-use, misuse, portable representation, renderer behavior,
validation, and evidence rules. Generation records should include purpose,
objective, selected sources and locators, prompt, backend, timestamp, input
fingerprint, draft state, reviewer action, and validation outcome.

## 6. Implications for itembank contracts

### Learner flow

Gemini Notebook's useful micro-flow is:

`select sources -> ask or generate -> inspect citation -> open context -> save`

itembank should embed that loop inside a larger course flow:

`resume course -> see why this action is next -> enter objective and treatment
-> read or act -> inspect source when needed -> check understanding -> receive
runtime-governed feedback -> apply or transfer -> record evidence -> continue`

Source chat is thus a contextual action from a lesson, reading, objective, or
review finding. Studio artifacts become candidate treatments or derived views,
not top-level destinations competing with Learn, Practice, Test, Sources,
Course map, and Build/review.

### Semantic content contract

This stream supports semantic additions for:

- stable citations with preview text and open-source locator;
- source scope and provenance on generated blocks;
- generated versus accepted state;
- equivalent text structures for maps, visuals, audio, and video;
- a resumable position independent of chat history;
- relationship-labelled concept links;
- optional derived representations that point back to accepted content;
- learner notes whose authorship and promotion status remain explicit.

It does not support encoding competitor panels, visual styles, AI host personas,
or generic artifact types as the authored grammar.

### Agent skills

Agent playbooks should require this sequence:

1. Declare objective, learning moment, and intended treatment.
2. Show selected approved sources and locators.
3. Decide direct reading versus synthesis before generating.
4. Draft the smallest missing semantic artifact.
5. Label quotations, paraphrases, synthesis, and uncertainty.
6. Supply portable and accessible fallbacks for media or spatial interaction.
7. Validate deterministic contracts and assessment authority.
8. Present a diff with provenance, review state, and undo path.

Agents should not offer “make all Studio artifacts” as a course-building step.
They may propose an audio, map, visual, or quiz only after stating its teaching
role and why the existing source or artifact does not already satisfy it.

### Legacy upgrades

A legacy lesson upgrade should not add flashcards, maps, callout cards, or audio
because those patterns are available. It should audit the objective, source
history, existing teaching gap, assessment semantics, plain-file coherence,
and accessibility first. A valid upgrade might add stable citation locators,
a relationship-labelled outline, a transcript-backed audio derivation, or a
targeted check. It must preserve identity, record derived assets, show the diff,
and revalidate linked questions without changing keyed meaning silently.

## 7. Disposition table

| Capability or decision | Disposition | Rationale and next proof |
|---|---|---|
| Citation preview and jump to stable source context | **Accept** | High verification value; specify hover, focus, touch, keyboard, and screen-reader behavior |
| Explicit source selection for a grounded action | **Accept** | Improves control; persist provenance on the resulting artifact |
| Clear separation of source, inquiry, and generated artifact | **Accept** | Useful boundary when nested under the course and objective map |
| Inspectable prompts and reviewable artifact versions | **Accept** | Supports agent accountability; supplement with source, backend, fingerprint, validation, and approval metadata |
| Review-before-import source discovery | **Accept** | Matches approved-root and bounded-write rules; distinguish link, import, copy, and sync |
| Save useful chat synthesis as a draft note | **Accept** | Prevents loss of useful work; never erase generated provenance or promote automatically |
| Course home as notebook chat or artifact gallery | **Reject** | Omits objectives, prerequisites, treatment, sequence, evidence, formal assessment, and resume logic |
| Generated quiz controls as an assessment-quality contract | **Reject** | Amount and coarse difficulty do not establish construct, alignment, item quality, or scoring authority |
| Chat-only or hidden-panel mode as authorization | **Reject** | Presentation does not revoke access; enforce disclosure in runtime and storage boundaries |
| Automatic generation of every available study artifact | **Reject** | Creates noise and unreviewed transformation without a teaching need |
| AI-generated visual accepted without semantic fallback and review | **Reject** | Vendor documentation itself warns of factual and visual inaccuracies |
| Generic transcript-to-podcast clone | **Reject** | Passive novelty does not justify cost, latency, citation loss, or course displacement |
| Transcript-first, cited lesson audio with return position | **Prototype** | Test accessibility, background continuity, synchronized citations, offline behavior, and learning purpose |
| Relationship-labelled concept map with linear outline | **Prototype** | Test overview and navigation value without unnamed-edge or spatial-access failures |
| Source-aware contextual Learning Guide beside a lesson | **Prototype** | Test one-question pacing, citation inspection, and runtime disclosure boundaries |
| Source guide used only for orientation and treatment review | **Prototype** | Compare against direct-reading entry and check whether it reduces or displaces source engagement |
| Generated visual explanation for one objective | **Prototype** | Require citations, review, alt representation, narrow-screen and screen-reader proof |
| Generic video, infographic, and slide generation | **Defer** | High review and accessibility cost; first prove one teaching-specific visual primitive |
| Note-to-source conversion | **Defer** | Needs epistemic-role, authorship, version, and promotion semantics |
| Cross-product context sync | **Defer** | Retention, sharing, grounding, and local identity complexity exceed Phase 16's core tracer |
| Source-grounded agentic code and file generation in learner view | **Defer** | Useful for build/review, but broad learner-side actions increase supervision and authorization risk |
| Whether audio is authored, generated on demand, or cached | **Open** | Compare quality, cost, privacy, reproducibility, and offline use in prototype |
| Whether learner notes may become course sources | **Open** | Requires course-owner controls and explicit authorship and trust levels |
| Whether maps are authored directly or derived | **Open** | Derivation reduces burden; direct authoring may better preserve meaningful edges |
| Whether contextual chat persists as evidence or remains disposable | **Open** | Avoid creating a second evidence store; define only after the runtime and privacy implications are clear |

## 8. Concrete recommendations and risks

### Recommended Phase 16 prototypes

1. **Citation round trip.** From a lesson claim, preview the cited passage by
   focus and touch, open it in source context, return to the exact lesson
   position, and repeat in plain Markdown through a readable citation link.
2. **Grounded contextual guide.** Ask one question about the current objective
   using a visible source subset. Save the response only as a generated draft
   with citations. Verify that formal assessment keys and higher feedback tiers
   never enter the model context.
3. **Semantic map.** Render one relationship-labelled map and the same content
   as a linear outline. Verify keyboard traversal, screen-reader reading order,
   narrow-screen use, and useful plain-file degradation.
4. **Alternative lesson audio.** Derive a short audio explanation from an
   accepted lesson block. Pair it with transcript, outline, citations, speed,
   pause, download or local cache decision, and a return-to-lesson marker.
5. **Generated visual acceptance.** Draft one cited visual explanation, show
   its review status, provide a structured text or table equivalent, and reject
   it if its claims or relationships cannot be traced.
6. **Study-aid promotion gate.** Generate a retrieval set from sources, bind
   each item to an objective and purpose, lint it, review it, and demonstrate
   that it cannot become a formal test merely through a “hard” setting.

### Principal risks

| Risk | Consequence | Mitigation |
|---|---|---|
| Chat becomes the product spine | Learners wander without sequence, coverage, or resume state | Put next action, objective map, and accepted artifact first; keep chat contextual |
| Citation theater | Markers appear trustworthy while sources are stale, weak, or out of context | Store stable identity, fingerprint, locator, source role, and surrounding context |
| Artifact abundance replaces treatment choice | Every source produces summaries, cards, maps, and media regardless of need | Require objective, learning moment, reuse search, and teaching-purpose justification |
| Generated study aid is mistaken for valid assessment | Scores and evidence lack construct validity | Keep runtime authority and require parser, lint, blueprint, review, and disclosure contracts |
| Generated visual misteaches | Polished imagery encodes false data or relationships | Require review, cited claims, semantic equivalent, and rejection path |
| Accessibility is postponed to rendering | Portable and alternative paths become expensive retrofits | Put interaction and fallback requirements in the semantic capability contract |
| Hosted grounding leaks source or key material | Private files or assessment content cross an unintended boundary | Display and minimize scope, enforce runtime disclosure, keep evidence and banks local |
| Saved synthesis becomes false provenance | Generated text is later treated as source-authored fact | Preserve authorship, generated state, citations, version, and explicit promotion |
| Cross-surface retention surprises | Deleting or hiding one context does not remove another | Avoid implicit sync; document destination and deletion semantics per operation |
| Competitor imitation drives design | itembank inherits notebook goals and protected expression | Copy no assets or chrome; translate only teaching and provenance patterns into native contracts |

### Bottom line

Gemini Notebook demonstrates an unusually coherent source-grounded inquiry
loop: choose evidence, ask or transform, inspect citations, return to context,
and retain useful synthesis. itembank should learn that loop deeply. It should
not inherit the notebook as the primary object, chat as navigation, coarse quiz
generation as assessment design, or a gallery of generated media as a course.

The stronger direction is a lesson-centered course that embeds source-grounded
inquiry exactly where it serves an objective. Citations, source scope, drafts,
and derived media remain inspectable. The runtime retains scoring, disclosure,
and evidence authority. Every rich representation has a portable semantic
form, an accessible interaction, and a reason to exist in the learning loop.
