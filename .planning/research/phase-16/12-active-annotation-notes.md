# Stream 12: active annotation and learner-built notes

**Status:** research complete for Phase 16 synthesis

**Access date for web sources:** 2026-08-13

**Scope:** active annotation and learner-owned note construction inside source-grounded lessons

**Decision boundary:** this report recommends research and prototypes. It does not change the binding product contract.

## 1. Scope and research questions

This stream asks when a lesson should mark important material for the learner, let the learner mark it, prompt a particular selection, require an identification, or ask the learner to construct a durable note. It treats copying, typing again, paraphrasing, summarizing, explaining, organizing, linking, drawing, and diagramming as different learning actions rather than interchangeable forms of “engagement.”

The governing questions are:

1. Which actions improve encoding, later retrieval, monitoring, or transfer, for whom, in which subjects, and under which constraints?
2. When does annotation become transcription, compliance theater, split attention, or inaccessible interaction overhead?
3. How can a lesson assemble a learner-owned note document whose claims remain traceable to source passages, objectives, lesson steps, media, and the learner's own wording?
4. Which source, lesson, note, quiz, and review sequences are coherent, and which should be separate modes?
5. How may question drafts use learner notes without allowing an incomplete or incorrect private note to become keyed truth?
6. Which choices belong to the learner, author, objective, activity, accommodation, or assessment mode?
7. Can several evidence-backed strategies share one semantic contract, parser, scorer, and UI framework without creating a configuration and testing explosion?

### 1.1 Terms used here

- **Annotation** is an addressable mark or comment attached to a source or lesson target.
- **Learner note** is learner-owned content that may quote, paraphrase, organize, connect, question, calculate, draw, or explain.
- **Prompt response** is an action submitted to complete an instructional step. It can also become a learner note, but the two identities are not automatically the same.
- **Accepted lesson** is reviewed instructional content with source and objective bindings. “Accepted” does not mean assessment-key authority.
- **Keyed truth** is content that the runtime may use to score a keyed item. Only the accepted bank and runtime contract have that authority.
- **Generative** means the learner selects, organizes, and integrates meaning. It does not mean AI-generated.

## 2. Existing itembank inventory

### 2.1 Observed shipped facts

| Existing capability | Evidence in repository | Relevance and gap |
|---|---|---|
| One parser and one scorer | `model.py`, `runtime.py`, AGENTS.md rules 1 to 3 | A note strategy must not introduce another bank parser or scorer. Prose remains pending review. |
| Source registry and locators | `## SOURCES`, `[SRC:]`, `[OBJ:]`, `parse_sources()` and provenance lint in `model.py` | The source side of note provenance exists conceptually, but there is no note-target or learner-wording record. |
| Lesson-to-item linkage | `## LESSON`, lesson headings, `[LESSON-REF:]`, `[CHECK:]` work described in the lesson tests and planning artifacts | A learner note could bind to an existing lesson step, but no shipped grammar does so. |
| Public item withholding | `runtime.public_item()` and JSON session commands | Notes must not expose keys or rationales before runtime permission. |
| Local evidence and deterministic sessions | session files, evidence surfaces, idempotent submit behavior | Annotation events can use the same local-first discipline, but reading behavior must not be mistaken for mastery evidence. |
| Study, Learn loop, Anki export, retention trends | `study`, export surfaces, `retention.py`, README and tests | Review destinations exist, but notes do not yet feed them and the shipped Learn loop is not a per-note scheduler. |
| Transactional bounded writes and provenance manifests | `schemas/write_manifest.schema.json` and Phase 11 artifacts | A future note exporter or agent edit should reuse recoverable writes rather than silently overwriting learner documents. |
| Plain Markdown lesson baseline and richer renderer | SOURCE-TO-COURSE rules 11 and 12 | Notes and prompts need coherent static fallbacks. Meaning cannot depend on a selection overlay or canvas. |

### 2.2 Existing research inventory

Relevant prior work includes `.planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md` on worked examples and semantic lesson blocks; `.planning/research/2026-08-10-lesson-item-coupling.md` on assertion-level provenance; `.planning/research/2026-08-10-style-registry-mechanics.md` on portable lesson semantics; `.planning/research/2026-08-09-extraction-subjects-bilingual.md` on `[SRC:]` and `[OBJ:]`; and Phase 16 Streams 02, 03, 04, 06, 07, 09, and 11 where lesson flow, activities, file lifecycle, app flow, and learner control overlap this topic.

**Inference:** the project already has the authority boundaries and several identity primitives needed for notes. It lacks a first-class learner artifact, target selectors resilient to source revision, note ownership/privacy states, and a distinction between learning action, personal representation, accepted content, and assessment truth.

**Recommendation:** extend the existing semantic and provenance ideas rather than embed a general-purpose note database or let every strategy invent its own data model.

## 3. Sources and evidence quality

Every link in this section was accessed 2026-08-13. Product behavior is supported primarily by vendor or project documentation. Learning claims use reviews, meta-analyses, direct experiments, or government evidence reviews. Product documentation establishes behavior, not learning effectiveness.

### 3.1 Learning research

| Source and type | Method and population | Observed result | Limitation for this decision |
|---|---|---|---|
| [Ponce, Mayer, and Méndez, learner-generated and instructor-provided highlighting meta-analysis](https://doi.org/10.1007/s10648-021-09654-1), peer-reviewed meta-analysis | 36 published articles from 1938 to 2019, 85 effects, college and K-12 academic text readers | Learner highlighting improved memory more consistently than comprehension. Instructor highlighting improved both in the aggregate. Learner highlighting favored college more than school students. | Published-study synthesis with heterogeneous texts, prompts, and tests. Average effects do not justify required highlighting in every lesson. |
| [Kobayashi, limits on the encoding effect of note-taking](https://doi.org/10.1016/j.cedpsych.2004.10.001), peer-reviewed meta-analysis | 57 note-taking versus no-note comparisons; moderators included schooling, presentation medium, duration, and test type | The encoding benefit was positive but modest. Visual presentation interfered with note-taking; recall tests detected more benefit than recognition or higher-order tests. | Older media and studies; focuses on taking notes without later review, so it does not estimate external-storage benefits well. |
| [Urry et al., direct replication and mini meta-analyses](https://doi.org/10.1177/0956797620965541), direct replication plus exploratory synthesis | 142 participants watched a lecture, laptop versus longhand; eight similar studies synthesized | Laptop notes were longer and more verbatim, but longhand did not improve immediate quiz performance. More verbatim overlap was not a robust mechanism. | Immediate test, lecture context, no study opportunity. It does not settle delayed review, stylus drawing, accommodations, or subject-specific notation. |
| [Fiorella, Making Sense of Generative Learning](https://doi.org/10.1007/s10648-023-09769-7), peer-reviewed integrative review | Synthesizes research on explaining, visualizing, enacting, and earlier work on summarizing, mapping, drawing, imagining, self-testing, and teaching | Generative actions can help, but benefits depend on learner, material, timing, and support. Partial maps or drawings often outperform unsupported construction. | A theoretical synthesis, not one common effect size. Strategy quality and outcome measures vary. |
| [Fiorella et al., summarizing and drawing in multimedia lessons](https://doi.org/10.3389/fpsyg.2024.1452385), peer-reviewed experiments and review | Online multimedia lessons; compares prompted summarizing/drawing and controls | Summarizing can remain useful, while drawing can fail when visuals are already dense and learners lack strategy training. | Boundary-condition study, not proof that summaries always transfer or that drawing is broadly ineffective. |
| [Izci and Acikgoz Akkoc, concept-map achievement meta-analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC10755297/), open-access meta-analysis | 78 studies published 2005 to 2017, random-effects model | Reports a large positive aggregate effect on academic achievement with substantial heterogeneity. | Included theses and proceedings, broad interventions, possible publication and design-quality variation. The unusually large pooled estimate should not be treated as a product forecast. |
| [BEME Guide 81 on concept mapping in undergraduate medical education](https://pubmed.ncbi.nlm.nih.gov/37980607/), systematic mixed-method review | 39 medical-education studies: quantitative, qualitative, and mixed methods | Concept maps were used to integrate knowledge, support critical thinking, and expose learner understanding. | Implementations and critical-thinking measures were diverse; medical students are not representative of novice readers. |
| [Kauffman, Zhao, and Yang WWC study record](https://ies.ed.gov/ncee/WWC/Study/86156), independent evidence review of RCT | 39 undergraduates read a 2,000-word online text with conventional, outline, or matrix note formats, with or without self-monitoring prompts | At least one promising positive finding; the RCT met WWC standards without reservations. | One small postsecondary study and one text. Format and monitoring prompts cannot be generalized independently. |
| [IES adolescent literacy practice guide](https://ies.ed.gov/ncee/wwc/PracticeGuide/8), government evidence synthesis | Adolescent literacy research and practitioner guidance | Recommends explicit strategy instruction, modeling, guided practice, feedback, and eventual independence; directed note-taking categories should align with the purpose for reading. | Practice guide bundles evidence and expert judgment. It is not a trial of an itembank-style interface. |
| [Organizing Instruction and Study to Improve Student Learning](https://ies.ed.gov/ncee/wwc/PracticeGuide/1), government evidence synthesis | Research-based practice guide across content-heavy subjects | Supports spaced learning, worked-example/problem alternation, integrated representations, retrieval, and delayed judgments of learning. | Broad guidance. It does not prescribe a note format or prove that notes should become cards automatically. |
| [Review and process effects of spontaneous note-taking](https://pubmed.ncbi.nlm.nih.gov/9878205/), controlled study | 226 high-school graduates read a philosophical text and took notes freely | Reviewing notes mainly helped detailed learning rather than learner-generated inference. | One philosophical text and older study; spontaneous note quality varied. |

### 3.2 Current systems and open-source workflows

| System or project | Primary source and observed behavior | Transferable pattern | Caution |
|---|---|---|---|
| Hypothesis, open source | [Annotation basics](https://web.hypothes.is/help/annotation-basics/) distinguishes a private highlight from an annotation with a note. [Export/import](https://web.hypothes.is/help/exporting-and-importing-annotations/) supports JSON/CSV/HTML export for accessible private, public, group, and LMS annotations. The server is [open source on GitHub](https://github.com/hypothesis/h). | Addressable targets, private/shared scope, tags, search, export, open API. | Web/PDF anchoring can break as content changes. Social annotation and group moderation are separate product problems from private course notes. |
| Zotero, open source | [Annotation storage documentation](https://www.zotero.org/support/kb/annotations_in_database) explains database-stored annotations, conflict-resistant sync, importing embedded annotations, and exporting annotated PDFs. | Separate annotation objects can sync without rewriting source files; annotations can later assemble into notes and remain exportable. | A database-first research manager is heavier than a local Markdown course. External annotations have ownership and conflict states that need explicit import. |
| Readwise Reader | [Highlight and note documentation](https://docs.readwise.io/reader/docs/faqs/highlights-tags-notes) covers text/image highlights, notes, tags, keyboard operation, and return to source context. [Export documentation](https://docs.readwise.io/reader/docs/faqs/exporting) supports Markdown, clipboard, print-with-annotations, CSV, customizable templates, and note-app export. | Fast capture, source return, tag views, portable Markdown, user-controlled export templates. | Highlight collection can become an extract pile rather than a synthesized learning artifact. Hosted sync/privacy assumptions do not fit itembank defaults. |
| H5P Cornell Notes, open source ecosystem | [H5P Cornell Notes](https://h5p.org/cornell-notes) attaches structured notes to text, video, or audio and persists them when content-state saving is enabled. [H5P content types](https://h5p.org/content-types-and-applications) places it alongside Interactive Book and Documentation Tool. | One guided-note shell across text, video, and audio; explicit cue, note, and summary structure. | Saving depends on host integration. A fixed Cornell layout is a strategy, not a universal note schema. |
| RemNote | [Flashcard basics](https://help.remnote.com/en/articles/8663109-flashcard-basics) turns note syntax into multiple card types. [Creating flashcards](https://help.remnote.com/en/articles/6025481-creating-flashcards) supplies outline ancestry as context. [AI generation](https://help.remnote.com/en/articles/10102901-generating-flashcards-with-ai) candidly says self-authored cards are usually better and scopes generation to selected text/sections. | Notes, hierarchy, context, cards, editing, and review form one workflow. Disable/preview makes derivation reversible. | Note syntax can couple writing to scheduler behavior. AI-generated cards are drafts, not verified assessment truth. |
| Perusall | [Product description](https://www.perusall.com/) supports multimodal social annotation, questions, replies, peer/instructor review, and assignments. [AI documentation](https://support.perusall.com/hc/en-us/articles/23863139218327-How-does-Perusall-use-AI) describes optional machine-scored comment quality and generated checkpoint prompts/quizzes. | Annotation can expose confusion and support discussion around an exact passage or media point. | Behavioral grading can reward volume or compliance. It conflicts with itembank's rule that only the runtime scores accepted item responses. Social/private boundaries are costly. |

## 4. Taxonomy of annotation and note construction

| Action | Semantic operation | Likely learning function | Primary failure mode | Appropriate use |
|---|---|---|---|---|
| Author pre-highlighting | Author marks an essential span or region | Attention cue, reduces selection demand | Seductive emphasis, overmarking, learner stops deciding relevance | Definitions, warnings, discriminating features, novice orientation; sparse and author-reviewable |
| Optional learner highlighting | Learner marks any target | Selection, external bookmark | “Paint the page,” false fluency, no organization | Personal reading aid, especially for experienced readers; never mastery evidence |
| Prompted selection | “Mark the sentence that states the mechanism” | Goal-directed selection and monitoring | Prompt gives away too much or tests pointer dexterity | Brief formative step with feedback and accessible alternative |
| Required identification | A target must be selected before progress | Retrieval/discrimination when source is hidden or alternatives compete | Forced compliance, blocking, motor/access barrier, accidental key exposure | Only when identification is the objective or a prerequisite for the next step |
| Copying | Exact excerpt enters notes with quote identity | External storage, evidence capture | Copying masquerades as understanding; copyright bulk extraction | Short quotation needed for later comparison, textual evidence, code/error message, exact rule |
| Typing again | Learner rekeys visible material | Attention, motor rehearsal, sometimes notation practice | Transcription load, source copying, punishes slow typing, weak transfer | Rarely: syntax, formula, vocabulary spelling, command, or procedural sequence where exact production is itself relevant |
| Paraphrasing | Restates a claim in learner language | Semantic encoding and monitoring | Fluent distortion, omitted qualifier, unsupported simplification | After a bounded passage, with source side-by-side and a “check against source” step |
| Summarizing | Selects and compresses main ideas | Selection, organization, global model | Novices omit essentials; summary while reading becomes copyediting | End of a coherent segment, preferably from memory, then source check |
| Explaining | States why/how, predicts consequence, connects prior knowledge | Integration, causal model, transfer | High intrinsic load, plausible misconception | Mechanisms, worked steps, cases, program behavior; scaffold with prompts or partial representations |
| Organizing | Sorts into outline, matrix, timeline, procedure, or Cornell structure | Relational structure and retrieval cues | Template does not fit domain; clerical drag | Comparative facts, sequences, taxonomies, clinical assessment, historical causation |
| Linking | Creates typed relation to concept, source, objective, example, or question | Integration and navigation | Link proliferation without meaning | Reused concepts, prerequisites, contrasting cases; require relation labels for important links |
| Drawing | Produces pictorial representation | Mental model, spatial integration | Artistic/motor burden, duplicates existing animation | Anatomy, geometry, process, architecture; allow labels or selected primitives instead |
| Diagramming/mapping | Nodes and typed relationships | Organization, misconception visibility, transfer | Blank-canvas overload and layout work | Systems, causal networks, dependency graphs; start with partial map for novices |

### 4.1 Facts, inference, recommendation

**Fact:** the highlighting meta-analysis found different average outcomes for learner and instructor highlighting, and a learner-age moderator. It does not establish that highlighting is necessary or sufficient.

**Fact:** note-taking's encoding effect is modest and sensitive to presentation and test mode. Direct replication does not support a blanket longhand advantage.

**Inference:** the valuable unit is not “a note” but the cognitive operation demanded by the prompt and the opportunity to retrieve, check, revise, and reuse its product.

**Recommendation:** author activities by operation and purpose, not by visual widget. `select`, `quote`, `paraphrase`, `summarize`, `explain`, `organize`, `link`, and `diagram` should remain distinct strategy actions even if they share selection and editor components.

## 5. Evidence-backed use and harm conditions

### 5.1 Encoding

Generative note-taking is most plausible when the learner must decide what matters, impose structure, relate the material to prior knowledge, or explain a mechanism. Copying and retyping can encode exact forms, but their value is narrow. They are poor defaults for conceptual learning. Dense animation, demonstrations, live code, or visual explanations can already consume visual attention; simultaneous notes can split attention and make the learner miss the event.

Use short pause points after a meaningful unit. For continuous media, capture an automatic timestamp and still/frame description, then let the learner note after pausing. For code, attach to a stable line range plus content fingerprint and retain a snapshot excerpt because lines move.

### 5.2 Retrieval

Notes support retrieval when the learner later attempts recall before reopening them. A completed note displayed beside every practice item is a reference, not retrieval practice. Notes should offer distinct actions: review, hide and recall, generate a personal prompt, or compare a recalled answer with the note. Spaced review should schedule accepted or learner-approved prompts, not every highlight.

### 5.3 Monitoring

Selecting, paraphrasing, and explaining can reveal uncertainty only if the learner can compare the result with a trustworthy source or rubric. A confidence toggle without calibration is weak. Better monitoring asks the learner to recall or explain, record confidence, then reveal the source/accepted explanation and revise. Preserve the pre-reveal version so the learner can see the gap without converting it into a grade.

### 5.4 Transfer

Transfer requires applying structure beyond the wording and example used during instruction. Explanations, comparison matrices, causal maps, drawings, and worked-example completion are stronger candidates than copied excerpts. A later novel case or problem must be scored only through the runtime if it is an itembank item.

### 5.5 When interaction harms

- Required highlighting harms when selection is not the objective, the learner already understands, the target is ambiguous, or pointer/vision/motor demands dominate.
- Typing again harms when exact reproduction is irrelevant, especially for dysgraphia, motor impairment, low typing fluency, language learners processing dense prose, and visual material that disappears while typing.
- Blank-page summaries and diagrams can overload novices. Partial structures and examples are safer.
- Note prompts inserted every paragraph fragment coherence. Batch at conceptual boundaries.
- Pre-highlighting everything removes signaling value and can turn an author's interpretation into false certainty.
- A “continue only after N highlights” rule measures compliance. It must not become completion or mastery evidence.
- Simultaneous note construction can reduce observation quality in demonstrations, clinical video, animations, and live coding. Pause, replay, transcript, and post-event capture are necessary.

### 5.6 Subject differences

| Subject | Productive constructions | Commonly harmful default | Why |
|---|---|---|---|
| EMT | structured patient-assessment findings, protocol comparison, symptom-to-action map, scene-safety explanation | copying whole protocols or writing during a time-sensitive demonstration | Exact thresholds and sequence matter, but transfer requires case discrimination and safety judgment. Source version matters. |
| Mathematics | annotated worked steps, error diagnosis, representation links, graph/sketch, “why this step is legal” | prose summary after every line, retyping rendered equations, unguided concept maps for novices | Mathematical knowledge is procedural, conceptual, symbolic, and visual. Exact notation and causal justification need different actions. |
| Computer science | predict trace, annotate invariant, explain error, link code to concept, small architecture/data-flow diagram | transcribing code shown on screen or taking notes while execution changes | Exact syntax sometimes matters, but copied code is not program comprehension. Line provenance is revision-sensitive. |
| Reading-heavy history/literature | claim-evidence-context notes, quotation with page locator, chronology, perspective comparison, synthesis across sources | author-highlighting a single “correct” interpretation or notes-only extraction that erases context | Evidence wording and provenance matter; interpretations may conflict and require source comparison. |

## 6. Workflow comparisons

| Sequence | Best fit | Benefits | Risks | Recommendation |
|---|---|---|---|---|
| Source to notes to quiz | Authoritative source is readable and objectives emphasize close reading | Preserves source voice; notes expose selection and organization; quiz supplies retrieval | Weak notes can omit coverage; quiz may accidentally key learner wording | Accept as a mode. Quiz derives from accepted source/objectives, with notes only suggesting emphasis or distractors after review. |
| Source to generated lesson to notes | Source is dense, fragmented, or needs synthesis | Lesson can scaffold and cite; notes capture learner model | Generated lesson can introduce error; two transformations increase provenance burden | Accept only after lesson acceptance. Notes bind both lesson step and underlying sources. |
| Notes to lesson | Learner has prior notes or a course starts from existing artifacts | Respects prior work; agent can diagnose gaps and personalize | Private/idiosyncratic notes may be wrong or incomplete; rewriting can violate ownership | Prototype as audit-first. Treat notes as learner claims, compare against approved sources, propose a lesson draft and conflicts, never silently “correct” the original. |
| Lesson to notes to practice | Objective needs guided model followed by application | Natural encode, externalize, retrieve sequence; practice tests beyond notes | Too many required steps; note shown during practice defeats retrieval | Accept as guided default for selected objectives, with skip or compact mode outside required course conditions. |
| Full lesson without notes | Material is short, well-signaled, or practice itself supplies generation | Lower friction, preserves narrative and observation | No durable learner artifact; fewer monitoring opportunities | Accept as first-class, not degraded. Offer optional end summary or bookmark. |
| Notes-only extraction | Learner needs reference, glossary, formula sheet, or review artifact | Fast and portable; good for known material and exact facts | Extraction can remove context, explanation, and productive practice | Accept as an output, reject as universal learning path. Label quoted, synthesized, and learner-authored sections. |
| Configurable hybrid | Mixed objectives, prior knowledge, preferences, and accommodations | Can select the least burdensome effective action per objective | Choice overload, incoherent paths, author/test explosion | Prototype a small registered set of modes, not arbitrary per-widget settings. |

### 6.1 Create together or separately

Create lessons, notes, quizzes, and spaced-review prompts **together as one reviewed bundle** when they share a stable objective and source slice, because alignment and provenance can be checked in one review. Still store them as separate typed artifacts with independent acceptance, ownership, and revision. A coherent bundle is not one mutable document truth.

Create them **separately** when:

- the source itself is the preferred teaching treatment;
- learner notes are private or intentionally idiosyncratic;
- the lesson is still generated or disputed;
- assessment needs broader blueprint coverage or controlled difficulty;
- the note is a reference artifact rather than a retrieval target;
- the spaced-review prompt would expose a key, oversimplify a process, or require human judgment;
- source rights allow reading/linking but not copied extraction.

**Recommendation:** use a derivation graph, not a pipeline that automatically promotes each output to the next authority level.

## 7. Question generation and assessment authority

### 7.1 Permitted inputs and controls

| Input to question drafting | Permitted use | Required control | May supply keyed truth? |
|---|---|---|---|
| Accepted source material | Draft stems, options, rationales, citations, objective coverage | Exact source locator, source version/fingerprint, author review, normal lint | Yes, only through an accepted bank item whose key is scored by runtime |
| Accepted lesson content | Draft checks aligned to the lesson | Trace lesson claim to source or mark synthesis; separate lesson acceptance from item acceptance | Not by itself |
| Learner notes | Suggest recall targets, personal examples, likely misconceptions, or questions the learner wants to answer | Private by default; explicit learner selection; fact-check against accepted source; never quote privately into shared artifacts without consent | No |
| Source plus learner notes | Personalize wording or choose among source-validated targets | Source wins on fact conflicts; show note-source discrepancy; item remains draft until accepted | Only accepted source-backed bank content |
| Lesson plus learner notes | Create personal practice around learner explanation | Accepted lesson supplies reference; idiosyncratic wording stays labeled; prose response remains pending | No |
| Notes alone | Learner-created self-test or recall prompt | Label “from your notes,” ungraded by default, permit edit/delete, show no official correctness claim | No |

### 7.2 Preventing silent promotion of error

1. Give every note block an `epistemic_role`: `quote`, `learner_claim`, `learner_question`, `learner_example`, `calculation`, `diagram`, or `accepted_reference_link`.
2. Record derivation edges, never replace the origin: a question draft says which note suggested it and which accepted source supports its key.
3. Require an accepted-source support edge for every keyed factual claim. A learner note can affect selection or phrasing but cannot satisfy support.
4. Run normal bank lint, provenance checks, review, ID assignment, and runtime scoring. There is no “personal note scorer.”
5. If sources conflict, stop promotion and present the conflict. Do not pick the learner note, newest source, or model output silently.
6. If only a learner note exists, create an unkeyed self-prompt or a research question. Do not generate an official MC key.
7. Preserve private scope during generation. A generated draft inherits the most restrictive input scope until the learner explicitly approves another destination.
8. Never auto-grade note prose. A later short response still scores `None` pending review.

**Rejected:** automatically converting every highlight into a cloze or every note heading into a multiple-choice question. This produces atomized, context-poor prompts and converts attention marks into implied truth.

## 8. Ownership and authority model

| Decision | Learner | Course author | Objective/activity | Accommodation | Assessment mode/runtime |
|---|---|---|---|---|---|
| Optional personal highlight | Owns content, colors/tags, edit/delete/export | May suggest convention | May offer prompt | Must offer non-pointer equivalent | Never scores it |
| Author pre-highlight | Can hide/reduce where safe | Owns semantic emphasis and citation | Justified by learning purpose | High-contrast and screen-reader signaling required | Cannot reveal withheld keyed content |
| Required identification | Can pause, resume, request equivalent, and see why required | Specifies valid target set and ambiguity policy | Requirement belongs here only if it serves objective | Equivalent text list, keyboard range, speech or structured choice | Runtime owns score only if this is a bank item; lesson completion alone is not correctness |
| Personal note wording | Owns and edits | Cannot silently rewrite | Prompt may constrain form, not beliefs beyond evaluated response | Dictation, handwriting, selection, template, or oral alternative | Private note is not evidence of correctness |
| Note template | Chooses among allowed options where optional | Registers recommended/default strategy | Objective can require fields such as evidence and reasoning | Alternative representation must meet same purpose | No implied grade |
| Skip | Chooses when optional; reason not required | States consequences | Required activity may route to equivalent or mark incomplete | Accommodation cannot be treated as a skip penalty | Formal assessment rules and runtime state govern item skipping |
| Question/card derivation | Selects note blocks and approves personal drafts | Approves shared/course bank drafts | Blueprint and objective constrain coverage | Accessible edit/review | Runtime alone scores accepted items |
| Sharing/export | Explicitly chooses destination and scope | Sets course-space policy | No automatic publication | Accessible formats | Keyed assessment material remains protected |

### 8.1 Optional, required, skip, and resume

Default annotation and note capture should be optional. A course author may require a semantic action only when the objective or activity genuinely depends on it, and must state the purpose. Required means “complete this learning operation or its equivalent,” not “use this mouse gesture.”

Each action has states `not_started`, `draft`, `completed`, `skipped_optional`, `equivalent_completed`, and `needs_review`. Resume returns to the draft with its source/lesson context. A skipped optional action stays available later. Required instructional work can block only its local sequence, never erase prior work, and must offer an accommodation-equivalent route. Assessment skips use the existing runtime contract, not this lesson-state vocabulary.

### 8.2 Editing, later review, and note evolution

Notes are versioned learner artifacts. Editing creates a revision with timestamp and author, while derivation links keep the version used for a card or question draft. The UI may show a current clean note and an optional history. “Update from source” proposes a diff because the learner's wording is owned, not regenerated in place.

If a source changes, targets become `resolved`, `relocated_exact`, `relocated_probable`, or `orphaned`. Probable relocation needs review. Conflicting learner statements remain visible as learner claims beside the accepted reference; they are not silently overwritten. The learner can mark a claim corrected, superseded, disputed, or intentionally personal.

## 9. Provenance design options

### 9.1 Minimum semantic record

```text
note_id, note_document_id, revision_id
owner_id or local-owner marker, privacy_scope
course_id, objective_ids[]
strategy_id, epistemic_role, learner_wording
targets[]:
  target_kind: source | lesson_step | media | item_public | concept
  stable_id, content_fingerprint, locator, quoted_context_hash
  media_time_range or region when applicable
derivations[]: from_note_revision | from_accepted_lesson | from_source
status: draft | learner_accepted | disputed | superseded | deleted
created_at, updated_at
```

The readable export should remain coherent Markdown. Machine metadata may use a sidecar if inline syntax becomes intrusive. Either form needs one canonical parser for this contract.

### 9.2 Options

| Option | Strength | Weakness | Disposition |
|---|---|---|---|
| Copy source text into note | Durable offline context | Rights/storage burden, stale duplicates, confuses quote with learner wording | Allow bounded quotations with locator and quote role; reject bulk default |
| Locator only | Compact and rights-respecting | Breaks when source moves or is unavailable | Insufficient alone |
| Locator plus source fingerprint and context hash | Detects source/version drift and supports relocation | Cannot display context offline without permitted snapshot | Accept as baseline |
| Stable semantic block IDs in accepted lessons | Precise lesson-step links and easy rendering | IDs need migration and authoring support | Accept for authored lessons |
| Character offsets or DOM paths | Easy initial capture | Fragile under edits and reflow | Use only as one selector among several |
| Text-quote selector plus prefix/suffix | Relocates across modest edits, matches web-annotation practice | Ambiguous repeated text, weak for equations/images | Prototype with stable source ID and fingerprint |
| PDF page/coordinates | Supports exact visual region | Page editions and OCR differ; poor accessibility alone | Store alongside quoted/OCR text and edition fingerprint |
| Media timestamp/range | Natural for audio/video | Edits shift time; transcript may differ | Store media fingerprint, transcript cue, and range |
| Code commit/fingerprint plus line range | Reviewable and exact at capture | Lines drift | Store excerpt hash, symbol/path, and revision; show conflict on relocation |

### 9.3 Provenance recommendation

Use a Web Annotation-inspired multi-selector target: stable artifact ID, version fingerprint, semantic block or media ID, human-readable locator, exact selected text or accessible description when rights allow, and prefix/suffix/context hash for relocation. Preserve the learner's content separately from target text. A learner paraphrase must never overwrite the quoted evidence field.

## 10. Extensible strategy model

### 10.1 One shared contract

A registered strategy describes:

```text
strategy_id and version
learning_purpose: select | organize | integrate | retrieve | monitor
input target kinds
response semantic type
prompt and scaffold policy
optional/required policy and equivalent actions
pause/resume behavior
note materialization policy
feedback and source-check timing
derivation destinations
accessibility contract
```

All strategies emit the same small event family: `target_selected`, `content_composed`, `relation_added`, `representation_attached`, `source_checked`, `note_revised`, `activity_completed`, and `activity_skipped`. Renderers vary, but identity, ownership, provenance, and lifecycle do not. If an action is an assessment item, it enters the existing runtime as a normal public item response. A lesson strategy does not score itself.

### 10.2 Initial registered modes

| Mode | Sequence | Default actions | Intended fit |
|---|---|---|---|
| Read with cues | source/lesson, optional note, check | sparse author emphasis, bookmark, end recall | novice orientation, short expository material |
| Guided notes | lesson segments, structured note, source check, practice | partial outline/matrix, paraphrase/explain, revision | content-heavy courses and novice strategy support |
| Close reading | source, evidence selection, annotation, synthesis, question | quotation, claim/evidence links, comparison | history, literature, policy, research |
| Worked reasoning | example, step explanation/diagram, faded completion, practice | annotate why, predict next step, error note | mathematics, CS, clinical reasoning |
| Observe then capture | uninterrupted media/demo, pause, note/map, replay/check | timestamped note, sequence or causal explanation | procedures, animations, live coding |
| Review extraction | accepted lesson/source/learner notes, learner-approved prompts | glossary/formula/reference sheet, cards as drafts | later consolidation, not first instruction |
| Minimal lesson | full lesson/check with no required note | bookmark and optional summary only | low-friction preference, familiar content, accessibility |

### 10.3 When implementing together is cheaper

Build several modes together only at the semantic foundation: stable targets, note identity/versioning, privacy, draft saving, skip/resume, export, strategy registration, accessible selection/composition primitives, and derivation edges. These are shared and are more expensive to retrofit after separate ad hoc widgets ship.

Implement mode-specific pedagogy incrementally. Guided matrices, diagram canvases, social annotation, handwriting recognition, card scheduling, and AI question drafting have different accessibility, authoring, and verification costs. They should not land merely because the shared contract can name them.

### 10.4 Combinatorial failure controls

- Register tested modes, do not expose every field as a setting.
- Permit one primary strategy and at most one optional supplement per lesson step.
- Keep requiredness at activity level, not a global “force notes” toggle.
- Test semantic conformance once, renderer behavior per primitive, and a bounded mode matrix per subject.
- Authoring tools validate that every required action has prompt, purpose, expected semantic type, feedback timing, and accessible equivalent.
- Strategies cannot define new correctness semantics, private scope, or export behavior.
- Version strategy definitions. Existing learner notes retain the version that created them.
- Kill a mode if it requires a second parser, scorer, note truth, or UI state machine.

**Inference:** a small strategy registry reduces duplication. Unlimited configuration multiplies paths across target type, requiredness, scaffold, response form, privacy, feedback, derivation, input method, viewport, and subject.

**Recommendation:** ship the common substrate with two prototypes, Guided Notes and Worked Reasoning, plus Minimal Lesson as the control. Add Close Reading only after provenance relocation works.

## 11. Accessibility, privacy, portability, and authorability

### 11.1 Accessibility

- Text selection must have keyboard and structured-choice equivalents. Never require drag-only highlighting.
- Author emphasis must be conveyed semantically and non-color-only. Screen readers need a concise label, not an announcement on every styled word.
- Drawing requires an alternative: labeled relationships, ordered steps, coordinate entry, tactile/print workflow, uploaded image with description, or oral explanation depending on purpose.
- Typing must have dictation, paste-with-quote labeling, handwriting/image attachment, and shorter equivalent prompts where these preserve the objective.
- Timed media notes require pause, replay, transcript, caption, playback speed, and a post-view note window.
- Math needs accessible MathML/linear notation and no requirement to select a visual glyph range precisely.
- Code notes need keyboard addressable lines, copied excerpt identity, and screen-reader-friendly diff/context.
- Reduced motion, zoom, narrow screens, high contrast, right-to-left text, IME composition, long words, and offline recovery belong in primitive tests.
- Accommodations change interaction and pacing, not the epistemic standard. An oral explanation and typed explanation can satisfy the same semantic response.

### 11.2 Privacy and learner ownership

Learner notes are private and local by default. Course authors may require a submitted response but do not thereby own the learner's notebook. Separate “save to my notes” from “submit this activity,” even when one action can do both after clear consent. Do not send note text to a model unless the learner chooses a bounded operation and sees the destination, fields, retention boundary, and proposed write.

Export must support readable Markdown plus a machine-readable provenance sidecar, and optionally a rendered PDF or standard annotation format later. Deletion should cover the note, its private index, and queued model inputs, while preserving only explicitly required assessment evidence under the runtime's existing rules. Derived cards or drafts become orphaned or are deleted by an explicit cascade choice.

Sharing needs per-note or per-document scope, not a global surprise. Group/social annotation is deferred because moderation, identity, harassment, accessibility, institutional retention, and source-rights work are not incidental features.

### 11.3 Authorability and legacy upgrades

An author specifies learning purpose and semantic action, not DOM details. The authoring preview must show plain Markdown fallback, rich view, keyboard path, screen-reader outline, skip/resume, narrow viewport, source-unavailable state, and note export. Legacy lessons remain valid without annotation. Upgrade begins with an audit, proposes stable step IDs and bounded prompts, preserves lesson wording and provenance, and never converts visual emphasis into a required activity automatically.

## 12. Prototypes and missing-feature tests

### Prototype A: Guided note spine

Build a split but collapsible lesson/note view using stable lesson-step targets. Support partial outline, paraphrase, explain, source-check, draft autosave, optional skip, resume, Markdown export, and learner-visible provenance. Compare Guided Notes with Minimal Lesson.

Success gates: no note loss after interruption; every block returns to source/step; no key appears; all actions work by keyboard; equivalent dictation/plain-form path; learners can distinguish quotation, their words, accepted reference, and generated suggestion; practice remains runtime-scored.

### Prototype B: Worked reasoning

Use annotated worked examples with a fading scaffold. Ask for “why this step,” prediction of the next step, or a labeled relation. Notes collect only learner-approved explanations and error patterns. Compare full worked lesson, worked lesson plus notes, and notes shown during practice versus hidden-until-check.

Success gates: note prompts do not materially increase time without improving delayed transfer or error diagnosis; math/code notation remains accessible; wrong explanations remain learner claims and cannot seed a key.

### Prototype C: Provenance relocation

Capture text, PDF region, media timestamp, and code range notes. Revise each source, then test exact relocation, probable relocation requiring confirmation, and orphan recovery. Export and reimport without losing ownership or learner wording.

### 12.1 Cross-subject fixtures

| Subject fixture | Activities to test | Missing-feature and failure tests | Outcome measures |
|---|---|---|---|
| EMT, respiratory assessment and oxygen decisions | observe short scenario; identify findings; structured patient note; explain action; later case practice | protocol version changes; unsafe learner claim; video notes attempted during critical observation; units/thresholds; source unavailable | delayed case discrimination, sequence recall, time overhead, unsafe-error detection, provenance return rate |
| Mathematics, solving a linear system and interpreting intersection | author cue for invariant; explain row operation; complete partial representation link; graph/diagram; novel transfer problem | equation selection by keyboard/SR; blank-canvas overload; copied steps without justification; multiple valid solutions | delayed procedural accuracy, explanation quality under rubric, representation transfer, cognitive-load/time rating |
| Computer science, loop invariant and off-by-one bug | predict trace; annotate invariant; attach note to code revision; explain failure; debug novel variant | line drift after edit; copied code treated as understanding; terminal output provenance; syntax exactness versus concept | novel bug diagnosis, trace accuracy, relocation success, time away from live execution |
| History, conflicting primary accounts of an event | quote with page/edition; claim-evidence-context matrix; source comparison; synthesis; essay-oriented retrieval | repeated quote ambiguity; OCR uncertainty; author pre-highlight bias; private interpretation used as official key | source attribution, corroboration quality, delayed synthesis, distinction of fact/interpretation, orphan recovery |

### 12.2 Experimental design recommendation

Use within-course randomized or counterbalanced comparisons where ethical and practical, with immediate and delayed measures. Record denominators and attrition locally. Compare learning per minute as well as raw score because interaction overhead is the central product risk. Include prior knowledge, age/education level, input method/accommodation, and subject as planned moderators. Do not infer learning from highlight count, note length, time-on-page, or completion alone.

Minimum comparisons:

1. sparse author cues versus no cues;
2. optional versus prompted learner selection;
3. paraphrase/explain versus copy/retype, matched for time where possible;
4. partial organizer versus blank organizer;
5. lesson plus notes versus the same full lesson without notes;
6. practice after hidden notes versus practice with notes visible;
7. learner-note-informed question drafts versus source-only drafts, all human-reviewed and scored by the same runtime after acceptance.

## 13. Implications for flow, contract, agents, and upgrades

### 13.1 Learner flow

The course chooses a recommended mode per objective. The learner sees why an action exists, what is optional, and what will be saved. Lesson steps alternate coherent instruction with purposeful pauses, not constant form filling. The note rail can collapse and has a full-page later-review view. Practice starts with notes hidden, then offers runtime-permitted feedback or a learner-controlled reference check when the mode permits it.

### 13.2 Semantic content contract

Add concepts for stable target, strategy activity, learner-note document/block/revision, epistemic role, ownership/privacy, derivation edge, conflict/relocation state, equivalent action, and materialization destination. Keep authored prompts portable. Rich selection handles and diagram editors are renderer behavior, not document truth.

### 13.3 Agent skills

Agent instructions should require: choose a strategy from objective and subject demands; justify required actions; prefer source reading when best; keep learner wording separate; cite every accepted factual derivative; propose diffs; never promote notes into keys; label uncertainty; preserve private scope; generate only learner-approved personal review drafts; and run accessible fallback and subject fixtures.

### 13.4 Legacy upgrades

Audit before adding prompts. Identify genuine learning gaps, stable source/step anchors, and an accessible equivalent. Preserve identities and assessment semantics. A legacy lesson with no notes remains valid. Do not add highlights merely to modernize appearance.

## 14. Disposition tables

### 14.1 Accept

| Decision | Reason | Owner/check |
|---|---|---|
| Learner-owned, private-by-default notes | Ownership and privacy must survive lesson use | Phase 16 contract, Stream 11 validation |
| Distinct semantic actions | Evidence and failure modes differ | Lesson contract and authoring skill |
| Sparse author emphasis plus optional learner marks | Supports signaling and autonomy | Author preview and accessibility test |
| Stable multi-selector provenance | Source revisions are normal | File lifecycle and contract work |
| Guided generative pauses at conceptual boundaries | Balances encoding with coherence | Activity authoring and prototype A |
| Separate artifact acceptance and derivation edges | Prevents note error from becoming truth | Parser/linter and review workflow |
| Runtime-only scoring and pending prose | Preserves existing authority | Runtime regression tests |
| Minimal lesson without required notes | Notes are not universally beneficial | First-class control mode |
| Portable Markdown export plus metadata | Learner ownership and interoperability | Export design |

### 14.2 Reject

| Decision | Reason |
|---|---|
| Force a quota of highlights | Measures compliance and creates accessibility burden |
| Retype visible prose as a general strategy | High mechanical cost, weak conceptual justification |
| “Handwriting mode” justified by universal superiority | Direct replication does not support the blanket claim |
| Auto-card every highlight | Selection is not verified truth or good retrieval design |
| Auto-key from learner notes | Violates one-scorer and source-authority boundaries |
| Notes required in every lesson | Subject, prior knowledge, media, and accommodation differences matter |
| One mutable document containing lesson, learner note, and bank key | Ownership, revision, privacy, and authority conflict |
| Arbitrary mix-and-match strategy settings | Combinatorial authoring, UI, and test failure |

### 14.3 Defer

| Capability | Revisit trigger |
|---|---|
| Social/group annotation | Identity, moderation, sharing, retention, and harassment contracts exist |
| Handwriting recognition | Accessible ink storage/export and reliable local recognition justify dependency cost |
| General diagram canvas | Partial-map prototype shows learning value beyond labeled-list alternative |
| Cross-device synchronization | Local conflict, encryption, deletion, and ownership model is accepted |
| Standard Web Annotation import/export | Core selectors stabilize and interoperability fixtures exist |
| AI feedback on learner explanations | Privacy, source-grounded evaluation, human approval, and non-scoring language are validated |

### 14.4 Prototype

| Capability | Kill or redesign criterion |
|---|---|
| Guided Note Spine | No delayed benefit or monitoring gain relative to time; drafts lost; provenance misunderstood |
| Worked Reasoning | Prompts interrupt reasoning, fail accessibility, or collect explanations without transfer benefit |
| Provenance relocation | High ambiguous/orphan rate after ordinary edits or false exact matches |
| Learner-note-informed drafts | Review burden or factual defect rate exceeds source-only drafting without useful personalization |
| Strategy registry | Modes require separate parsers/scorers or shared states become conditional tangles |

### 14.5 Open questions

| Question | Evidence needed |
|---|---|
| Which two modes should become Phase 16 defaults? | Cross-subject prototype results and authoring-cost estimate |
| Should learner notes live inline or in a sidecar? | Plain-reader quality, parser complexity, privacy, and conflict prototypes |
| What counts as learner acceptance of a generated suggestion? | UX test distinguishing preview, insert, edit, and accept |
| How much selected source text may be stored? | Rights policy by source type and offline-use needs |
| Should personal cards use the same bank grammar? | Authority labeling, lint fit, export behavior, and risk of mistaken official status |
| How is an oral or drawn equivalent reviewed? | Accessibility study and durable representation design |
| Can a note contribute non-score evidence of strategy use? | Clear purpose and proof it will not be misread as mastery |
| What is the correct source-check timing? | Immediate versus delayed comparison by objective and prior knowledge |

## 15. Concrete recommendations and risks

1. Define learner notes as a separate owned artifact with versioned blocks and multi-selector provenance.
2. Define annotation activities by cognitive operation, not widget. Begin with `select`, `quote`, `paraphrase`, `summarize`, `explain`, `organize`, `link`, and a constrained `diagram` response.
3. Register a small set of evidence-backed modes. Implement shared identity, privacy, save/resume, export, provenance, and accessibility together; implement specialized renderers later.
4. Make Minimal Lesson first-class. Guided Notes and Worked Reasoning should be reversible prototypes, not universal defaults.
5. Keep question derivation as a reviewed graph. Learner notes may suggest personal practice, but only accepted source-backed bank content can carry a key, and only the runtime scores it.
6. Default notes to private and local. Separate saving to notes, submitting an instructional response, sharing, and sending content to a model.
7. Measure delayed learning, transfer, monitoring calibration, and learning per minute. Never use highlight count or note length as mastery.
8. Require accessible equivalents and static fallbacks before an activity can be required.
9. Preserve source, lesson, note, question, and review as distinct artifacts even when authored and reviewed as an aligned bundle.
10. Treat source drift and note conflict as visible states. Never relocate, rewrite, merge, or promote on filename or semantic similarity alone.

The largest risk is mistaking visible activity for learning. The second is mistaking learner ownership for assessment authority. The proposed design addresses both by making purposeful generative operations available without requiring them universally, and by preserving a strict derivation and scoring boundary from source through lesson and note to accepted question.
