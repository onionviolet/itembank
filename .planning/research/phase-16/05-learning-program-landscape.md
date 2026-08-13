# Learning-program landscape and blind spots

**Research stream:** Phase 16, stream 05

**Research date and access date for all web sources:** 2026-08-13

**Scope:** landscape evidence for synthesis, not a product decision or an
implementation plan

## 1. Scope and research questions

This study asks what a source-to-course product misses if it compares only
source chat, lesson pages, and question widgets. It samples distinct learning
program families and compares the whole journey: how content enters, how an
author maintains it, what a learner actually does, which evidence is produced,
how the next action is chosen, how work travels, and what happens when access,
ability, connectivity, money, or institutional support changes.

The questions are:

1. Which complete workflows have pedagogical purposes that itembank does not
   yet represent?
2. Where do authoring cost, maintenance, portability, accessibility, privacy,
   or incentives undermine an attractive learner feature?
3. What evidence can legitimately support a next action, and what evidence is
   only engagement telemetry or a product claim?
4. Which standards are useful as interchange boundaries without becoming a
   second parser, scorer, evidence store, or opaque source of truth?
5. Which neglected learners and contexts change the contract, not merely the
   visual polish?

### Method and limits

Product behavior was checked against current first-party documentation. This
is a documentation audit, not a logged-in usability trial, procurement study,
or accessibility conformance test. Vendor claims about efficacy, scale, and
personalization are not treated as proof of learning. Research claims are
limited to reviews or studies whose method and principal limitation can be
stated here. The sample is purposive, not exhaustive. It covers each requested
family with at least one informative exemplar and uses a second exemplar where
the workflow differs materially.

Every analytical section labels **Observed fact**, **Inference**, and
**Recommendation**. An observed fact describes a source or the current
itembank contract. An inference is this report's interpretation. A
recommendation is input to stream 06 and has no binding force until synthesis.

## 2. Existing itembank research reviewed

The repository already contains a substantial 2026-08-09 to 2026-08-10
landscape. These findings remain useful as internal evidence, but claims about
live products are dated to their research date unless independently refreshed
below.

| Existing artifact reviewed | Valid findings reused | Gap left for this stream |
|---|---|---|
| `2026-08-09-landscape-widening.md` | Readiness graphs, short recommended menus, process evidence, shared manipulatives, blueprint weighting, integrated rationales and glosses, staged coding projects, SRS ownership conflict, standards cautions | Optimizes individual self-study features more than complete author, learner, instructor, and maintenance workflows. QTI was rejected too broadly because export mapping was not separated from adopting it as an internal format. |
| `2026-08-09-blind-spots.md` | Cold start, interruption and resume, audio, backup, migration, authored-content accessibility, licensing, recognition bias, model cost | Audio was treated mainly as TTS export. Offline education, disability-led interaction, cohort workflows, and connectivity-aware synchronization need deeper treatment. |
| `2026-08-09-lesson-display-editor.md` | Durable source plus derived preview, external-editor parity, semantic figures, readable long form | Does not examine packaged publications, executable documents, content-type versioning, or author accessibility tools. |
| `2026-08-09-visual-design.md` and `2026-08-10-ui-inspiration-missing-surfaces.md` | Calm hierarchy, reader and runtime voices, first-run, empty, loading, error, review, and author surfaces | Visual patterns are not evidence models. They leave co-learning, instructor intervention, learner-created artifacts, and low-resource deployment mostly open. |
| `2026-08-10-lesson-style-catalogue.md` | Style as ordering and budget, worked example plus variation, prediction only where meaningful, reference mode beside guided mode | The style lens underweights field work, creation, peer explanation, deliberation, embodied practice, games, and audio dialogue. |
| `2026-08-10-lesson-item-coupling.md` | Lesson and activity adjacency, linked identity, feedback authority | Needs exchange boundaries for LMS and assessment ecosystems and a clear distinction between authored correctness and runtime scoring authority. |
| `FEATURES.md`, `PITFALLS.md`, and `SUMMARY.md` | One evidence spine, uncertainty, quality gates beyond lint, no silent schedule merge, honest execution boundary | They predate the course-first reframe and largely assume one learner, one machine, and one primary author. |

**Observed fact:** Phase 16 streams 01 through 04 did not yet exist in this
worktree when this report was researched, so direct deduplication against their
finished findings was impossible.

**Inference:** The highest-value gaps are not more callout types. They are
learning activities that produce artifacts or explanations, capability
profiles for rich content, offline and synchronization semantics, instructor
and peer review queues, exchange adapters, and accessibility as an authored
quality dimension.

**Recommendation:** Stream 06 should treat the older reports as dated inputs,
not settled product law. Preserve their strong boundaries while revisiting
blanket standards rejections and individual-only assumptions.

## 3. Sources

All links were accessed 2026-08-13. Product rows are primary first-party
sources unless marked research.

### Product and ecosystem sources

| Family | Direct source and source type | What was verified |
|---|---|---|
| Source-grounded study | [Google for Education, NotebookLM](https://edu.google.com/ai-notebooklm/), official product page; [Audio Overview help](https://support.google.com/notebooklm/answer/16212820), official help | Source-only answers with passage citations, flashcards, quizzes, reports, guided learning, and audio that can be queried alongside sources. |
| Course authoring and LMS | [Moodle learning plans](https://docs.moodle.org/502/en/Learning_plans), official docs; [Open edX platform](https://openedx.org/the-platform/), official product page; [Open edX cohorts](https://docs.openedx.org/en/latest/educators/concepts/advanced_features/about_cohorts.html), official docs | Competency templates assigned to groups; publishing, schedules, grading policy, cohorts, differentiated content, discussions, analytics, and OLX import/export. |
| Interactive textbook | [Pressbooks export guide](https://guide.pressbooks.com/chapter/export/), official guide; [Pressbooks accessibility](https://pressbooks.org/user-guides/accessibility/), official statement; [Runestone documentation](https://docs.runestone.academy/en/latest/readme.html), official docs | One authored book exported to EPUB/PDF/XML; author and reader accessibility commitments; interactive textbook customization and class delivery. |
| Simulations and accessible interaction | [PhET accessibility statement](https://phet.colorado.edu/en/inclusive-design/accessibility-statement), official statement; [Desmos accessibility features](https://help.desmos.com/hc/en-us/articles/4404860698253-What-Accessibility-features-does-Desmos-offer), official help; [Desmos conformance report](https://www.desmos.com/acr), first-party ACR | Alternative input, touch, sonification, voicing, interactive descriptions, zoom, Braille math, audio graph tracing, and current coverage limits. |
| Coding environments | [Jupyter notebook format](https://nbformat.readthedocs.io/en/5.2.0/format_description.html), official specification; [Jupyter execution](https://docs.jupyter.org/en/latest/projects/execution.html), official docs | Schema-defined cells and outputs, optional metadata, execution counts, and separate execution tooling. |
| Practice and exam preparation | [UWorld MCAT](https://gradschool.uworld.com/mcat/), official product page; [UWorld USMLE features](https://medical.uworld.com/usmle/features/), official product page | Qbank, explanations, study plan, analytics, flashcards, official materials, and comparison with other users. |
| Adaptive and spaced practice | [Anki deck options](https://docs.ankiweb.net/deck-options), official manual; [Anki exporting](https://docs.ankiweb.net/exporting.html), official manual; [RemNote spaced repetition](https://www.remnote.com/feature/spaced-repetition), official product page; [RemNote help](https://help.remnote.com/en/articles/6022755-getting-started-with-spaced-repetition), official help | FSRS settings, portable exports, embedded note-card identity, global due queue, exam prioritization, self-rating, streak and notification mechanics. |
| AI tutoring | [Khanmigo safety](https://support.khanacademy.org/hc/en-us/articles/14394814244365-What-safety-features-does-Khanmigo-have), official help | AI limitations are disclosed and shared images are not retained under the stated policy. |
| Cohort and instructor workflow | [Open edX data and analytics](https://docs.openedx.org/en/latest/educators/navigation/data_analytics.html), official docs; [Code.org progress](https://support.code.org/hc/en-us/articles/115000693231-Viewing-student-progress), official help; [Code.org pair programming](https://support.code.org/hc/en-us/articles/115002122788-How-does-pair-programming-on-Code-org-work-), official help | Instructor review of grades, answers, projects, and selected work; paired work attribution; some coding work intentionally not auto-validated. |
| Accessibility-first content | [H5P content-type recommendations](https://help.h5p.com/hc/en-us/articles/7505649072797-Content-types-recommendations), official current audit; [Kolibri inclusive content guidance](https://kolibri-studio.readthedocs.io/en/latest/make_inclusive_content.html), official guide | Accessibility varies by content type and version; author choices can break an accessible renderer; alternatives and assistive technology must be planned in content. |
| Learning games | [Duolingo product workflow](https://blog.duolingo.com/duolingo-101-how-to-learn-a-language-on-duolingo/), official product article | Path, hearts lost on errors, practice to regain access, paid unlimited hearts, streak protection, reminders, and optional social features. |
| Audio learning | [NotebookLM Audio Overview help](https://support.google.com/notebooklm/answer/16212820), official help; [W3C EPUB 3 publication status](https://www.w3.org/publishing/groups/epub-wg/PublStatus), official standards status | Audio can be a navigable source companion; EPUB has ongoing text-to-speech enhancement work. |
| Offline education | [Kolibri user guide](https://kolibri.readthedocs.io/en/latest/index.html), official docs; [Open edX offline-content decision](https://docs.openedx.org/projects/edx-platform/en/latest/references/docs/openedx/features/offline_content/docs/001-mobile-offline-content-support.html), official architecture decision | Offline-first channels, local curricula, coach tools, selective or full downloads, local response capture, later sync, and reduced capability for some assessment blocks. |
| Open content interactions | [H5P documentation](https://h5p.org/documentation), official docs; [H5P technical overview](https://h5p.org/node/61447), official technical overview | Import/export, OER reuse, content libraries, editor libraries, platform integrations, and packaged dependencies. |
| Assessment standard | [1EdTech QTI specification index](https://www.1edtech.org/standards/qti/index), official specification portal | QTI 3 exchanges items, tests, and results across tools, includes web-friendly markup, accommodations, CAT support, custom interactions, validation, and conformance certification. |
| Publication standard | [W3C EPUB 3.3 announcement](https://www.w3.org/WAI/news/2023-05-25/EPUB/), official standards notice; [EPUB Reading Systems 3.3](https://www.w3.org/TR/epub-rs-33/), W3C Recommendation | EPUB 3.3 is a recommendation with accessibility integral to the family; reading systems should expose accessible bookshelf, search, annotation, and controls. |
| Legacy course packaging | [ADL SCORM guidance](https://www.adlnet.gov/assets/uploads/ADLGuide2004_Final_073108.pdf), official guidance | A completed SCORM course is a ZIP package and actual behavior depends on LMS support. |

### Learning research

| Claim area | Source, method, and limitation |
|---|---|
| Retrieval practice | [Roediger et al., 2021](https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010419-051019), narrative Annual Review; [Agarwal et al., 2021](https://eric.ed.gov/?id=EJ1319572), systematic review of applied school and classroom studies. These support retrieval across settings, but do not establish that every quiz format, schedule, or high-stakes use is effective. |
| Worked examples | [Barbieri et al., 2023](https://www.danamillercotto.com/uploads/4/7/7/2/47725475/barbieri_et_al__2023__we_meta-analysis.pdf), meta-analysis. About half of included studies were from the United States and other English-speaking contexts, and moderator and dosage evidence remained limited. |
| Gamification | [Li et al., 2024](https://www.sciencedirect.com/science/article/pii/S2155684924000010), meta-analysis reporting a positive overall learning effect and stronger extrinsic than intrinsic motivation effects. The authors report limited coverage and high heterogeneity. [Kalogiannakis et al., 2023](https://link.springer.com/article/10.1007/s11423-023-10337-7), meta-analysis plus systematic review, finds autonomy and relatedness benefits but minimal competence impact; most motivation measures were self-report and may reflect novelty or reporting bias. |
| Process-aware AI support | ["Help Me, But Don't Watch Me," 2026](https://arxiv.org/abs/2604.06178), recent K-12 learner-preference study. Participants preferred time to think and hints over answers and expressed privacy and autonomy concerns. It is recent, population-specific, and preference evidence, not an outcome trial. |
| Executable notebook risk | [Jupyter notebook attacks taxonomy, 2024](https://arxiv.org/abs/2409.19456), security taxonomy rather than intervention research; [Samuel and Mietchen, 2021](https://arxiv.org/abs/2103.02959), reproducibility tooling study. Together they establish risk and environment-restoration difficulty, not the learning effectiveness of notebooks. |

## 4. Complete workflow landscape

### 4.1 Source-grounded workspace: NotebookLM

**Observed fact:** The workflow is source upload, grounded chat, cited derived
media, and generated study aids. Citations link answers to source passages.
Flashcards, quizzes, study guides, mind maps, audio, video, and guided learning
can be generated from the same source collection.

**Inference:** This is excellent for synthesis and modality conversion, but the
unit is a notebook and the dominant evidence is an interaction with generated
outputs. The published workflow does not itself guarantee a stable objective
map, blueprint alignment, accepted artifact history, deterministic scoring, or
course maintenance after sources change. Audio is useful when it remains
navigable to the text, not when fluent conversation hides source uncertainty.

**Recommendation:** Accept passage-level grounding and source-synchronized
derived views. Require generated aids to carry source fingerprints, locators,
generator metadata, and stale status. Reject "generate every modality" as a
course plan. Choose treatment per objective, and make audio a companion with
chapters, transcript, citations, speed controls, and resume position.

### 4.2 Authoring and LMS: Moodle, Open edX, Pressbooks, H5P

**Observed fact:** LMS workflows include roles, publishing, cohorts, grading
policy, schedules, group assignment, discussions, reports, and live course
revision. Moodle learning-plan templates propagate competency changes to
assigned learners. Open edX can vary content by cohort. Pressbooks authors one
book and exports reader formats. H5P composes interaction libraries that bring
their own editor, renderer, dependencies, maintenance, and accessibility state.

**Inference:** Course authoring is lifecycle management, not a one-time file
generation step. A published course needs draft versus accepted state,
effective dates, dependency-aware change impact, learner-version pinning, and
review queues. H5P's current accessibility matrix shows that "supports H5P" is
not an accessibility claim. Capability, library version, content instance, and
author choices all matter. LMS scale also produces surveillance incentives and
administrative complexity that a personal tool should not inherit.

**Recommendation:** Add a small publication lifecycle: draft, accepted,
superseded, and retired, with an impact preview for enrolled or in-progress
learners. Model semantic capabilities and their versioned support profiles,
not arbitrary plugin widgets. Defer rosters, gradebooks, certificates,
e-commerce, and enterprise analytics. Prototype a read-only instructor or
coach review bundle before any multi-user service.

### 4.3 Interactive textbooks and executable notebooks: Runestone, Jupyter

**Observed fact:** Runestone joins explanatory text, code and activities with
instructor customization and analytics. Jupyter stores ordered markdown and
code cells, execution counts, outputs, and extensible metadata in a validated
JSON document, while separate tools execute it.

**Inference:** The powerful pattern is not "embed a code editor." It is a
learner-visible artifact that can be run, inspected, changed, and discussed.
The costs are stale outputs, hidden execution order, unavailable environments,
arbitrary code, untrusted content, accessibility of output, and provenance of
the result. A screenshot of a plot is not equivalent to an executable result,
and a saved output is not proof that the current source generated it.

**Recommendation:** Support artifact-producing activities through a trusted,
declared runner boundary. Store source, environment declaration, input,
captured output, execution status, and accessible static fallback separately.
Never execute imported or agent-generated code merely because it appears in a
lesson. Do not adopt notebook JSON as the lesson source of truth.

### 4.4 Simulations and visual mathematics: PhET, Desmos

**Observed fact:** PhET reports inclusive features per simulation, including
alternative input, enhanced touch, descriptions, voicing, sonification, zoom,
and language selection, with incomplete library-wide coverage. Desmos supports
screen-reader math, Nemeth and UEB Braille, enlarged display, reverse contrast,
and audio graph tracing, while its conformance report records exceptions.

**Inference:** A text description beside a visual is often not an equivalent
learning activity. Inclusive simulation requires equivalent control,
orientation, state change, comparison, and feedback. Sonification and voicing
are teaching representations, not only accommodations. This creates ongoing
content design and testing cost, which is why even mature libraries publish
coverage counts and exceptions.

**Recommendation:** Every interactive capability needs a support profile:
input modalities, perceivable outputs, state narration, static alternative,
evidence equivalence, tested assistive technologies, limitations, and version.
Prototype one accessible number-line or graph interaction with keyboard, touch,
screen reader, and sonification before approving a general simulation grammar.
Reject visual-only hotspots, drag-only assessment, and generic alt text as a
claim of equivalent participation.

### 4.5 Practice, assessment, and exam preparation: UWorld and itembank

**Observed fact:** UWorld combines exam materials, qbank explanations, study
planning, performance analytics, flashcards, and comparison with other users.
itembank already keeps scoring and disclosure in one deterministic runtime and
requires blueprint fidelity for standardized tests.

**Inference:** A qbank becomes a learning program when review of an attempt
produces a concrete remediation path. The main cost is editorial: authentic
items, misconception-specific rationales, current blueprint mappings, and
review of changes. Peer percentiles can motivate but confound cohort,
preparation stage, sample selection, and objective mastery. Completion and
accuracy invite question-chasing when the true target is transfer.

**Recommendation:** Make the post-set workflow first class: triage misses by
misconception, revisit the cited source or lesson, perform a changed-context
application, then schedule later retrieval. Report local denominators and
uncertainty. Reject normative peer ranking and readiness percentages without a
validated model for the specific blueprint and population.

### 4.6 Adaptive learning, tutoring, and spaced repetition

**Observed fact:** Anki and RemNote schedule item review from response history;
RemNote embeds cards in notes, prioritizes an exam, and exposes streaks and
notifications. AI tutors disclose limitations and can provide conversational
support. Recent preference research finds that learners want time to think,
hints, autonomy, and privacy boundaries.

**Inference:** Adaptation has three separate layers: curriculum readiness,
retention scheduling, and within-activity support. Combining them into one
opaque "personalization" score destroys explainability and makes recovery
difficult. Note-linked cards reduce duplication but make editing identity and
schedule migration consequential. Process-aware help becomes surveillance if
the learner cannot see, limit, or erase the observations.

**Recommendation:** Keep three policies separate and legible. Explain why an
objective, review, or hint is offered. Give the learner pause, skip, browse, and
"do not observe process" controls. Preserve card and objective identities
across edits with reviewable migration. Reject covert intervention, emotion
inference, and a single proprietary mastery number.

### 4.7 Note-linked learning and learner-created artifacts

**Observed fact:** RemNote creates flashcards inside notes so an edit updates
the card context. Jupyter and coding platforms make learner work a durable
artifact. Code.org instructors review text responses and projects, and it
explicitly does not claim most programming activities are auto-validated for
correctness.

**Inference:** itembank's source-to-course loop is still author-heavy. Learners
also learn by annotating, explaining, drawing, coding, comparing, and building.
Those products reveal an evidence class between a scored response and passive
page view: a learner artifact awaiting self, peer, or instructor review.

**Recommendation:** Add a non-scored artifact activity concept with prompt,
objective, submission reference, provenance, rubric or review questions,
status, and feedback links. Keep it outside automatic mastery. Permit export or
linking to the learner's chosen notes folder. This generalizes reflection,
self-explanation, lab notebooks, proofs, programs, concept maps, and projects
without pretending they share a scorer.

### 4.8 Cohort, peer, and instructor workflows

**Observed fact:** Open edX cohorts can receive different discussions, content,
assignments, or exams. Code.org attributes paired work and brings responses,
assessments, and projects into instructor review. Changing cohort assignment
mid-run is discouraged because it changes the learner experience.

**Inference:** Cohort membership is part of assessment provenance. Pair work
cannot be interpreted as individual evidence. Useful social learning is
structured around explanation, critique, comparison, and feedback, not a
generic feed. Instructor attention is scarce, so the useful interface is a
triage queue with reason and evidence, not a dashboard of clicks.

**Recommendation:** Defer accounts and live cohorts, but make the semantic
contract future-safe: evidence records individual versus collaborative
context, collaborators, assignment variant, and reviewer status. Prototype an
exportable coach packet that lists pending prose or artifacts, repeated
misconceptions, citations, and requested feedback without exporting keyed
content or the entire private history.

### 4.9 Games and incentive systems

**Observed fact:** Duolingo's path joins short practice with hearts lost on
errors, practice needed to regain access, streaks, reminders, social features,
ads, and paid unlimited hearts. Meta-analyses report positive average effects
for game-related approaches, but effects are heterogeneous, motivation is
often self-reported, and extrinsic motivation effects can exceed intrinsic
ones.

**Inference:** Game-based learning and reward layers are different. A
simulation, strategy game, role-play, or puzzle can embody the target system.
Points, hearts, streaks, and leaderboards can optimize return behavior while
penalizing error, illness, disability, intermittent access, or deep work that
takes longer. Monetizing relief from learning friction is misaligned with
itembank's purpose.

**Recommendation:** Accept purposeful puzzles, safe-to-fail scenarios,
role-play, and visible progress toward learner-chosen goals when the game action
is the learning action. Reject purchasable error relief, lives, randomized
rewards, compulsory streaks, public leaderboards, and engagement targets as
evidence of learning. Allow calm session goals to be hidden.

### 4.10 Audio learning

**Observed fact:** NotebookLM lets a learner listen while querying sources and
viewing citations. EPUB standards work includes text-to-speech support. Earlier
itembank research proposed TTS export.

**Inference:** Audio is not one feature. It includes accessible reading,
pronunciation, auditory discrimination, sonification, conversational
explanation, learner think-aloud, and review while hands or eyes are occupied.
Linear audio makes equations, citations, navigation, and correction difficult.
Synthetic dialogue can sound more authoritative than its source support.

**Recommendation:** Define audio roles separately. A minimum companion has a
transcript, headings, synchronized citations, speed and seek controls, resume,
pronunciation metadata where relevant, and a way to return to the visual or
text representation. Defer generative two-host audio until a prototype tests
factual drift, citation usability, accessibility, cost, and offline caching.
Never make audio the sole representation of assessed content.

### 4.11 Offline and low-resource education

**Observed fact:** Kolibri is designed around offline access, locally curated
channels, coach tools, and openly licensed resources. Open edX's offline design
packages assets, supports selective or complete downloads, stores responses
locally, synchronizes later, and documents that some problem blocks lose hints,
feedback, or execution offline.

**Inference:** "The page opens offline" is not offline learning. A course needs
a manifest of required assets and capability degradation, storage estimates,
download status, update identity, queued writes, conflict handling, and an
honest indication of which feedback is unavailable. Low-resource use also
means shared devices, intermittent power, multilingual content, and a local
coach, not just one laptop without Wi-Fi.

**Recommendation:** Make an offline readiness report part of course validation.
It should list asset size, missing local media, unavailable model or runner
features, static alternatives, queued evidence semantics, and update
fingerprints. Preserve a fully useful read, practice, test, and resume core.
Prototype interruption, device clock change, duplicate submission, and source
update while offline. Defer cross-device merge until conflict semantics are
explicit.

## 5. Standards and interoperability: exchange, not internal truth

| Ecosystem | Observed fact | Inference | Recommendation |
|---|---|---|---|
| QTI 3 | Exchanges assessment content and results among authoring, banking, delivery, scoring, and analytics tools; includes accommodations, web markup, custom interactions, CAT, validation, and certification. | It can preserve more assessment semantics than a flat quiz export, but conformance profiles and custom interactions still limit real portability. Mapping to QTI is not the same as adopting a second internal parser or scorer. | **Defer, then prototype export/import profiles.** Start with a documented supported subset and round-trip loss report. Imported keys enter the existing private model and existing scorer only after lint and review. |
| H5P | Packages content-type libraries, editor widgets, assets, and integrations; supports reuse and import/export; accessibility varies by type and version. | H5P is an ecosystem of executable components, not a portable semantic lesson floor. Embedding it imports dependency, security, upgrade, accessibility, and plain-file degradation costs. | **Prototype as a linked external activity or bounded import, not the canonical lesson grammar.** Require pinned library, license, checksum, accessibility status, offline status, and static fallback. |
| SCORM | Packages courseware as ZIP for LMS delivery; behavior depends on LMS support. | It is valuable only when institutional delivery is a real target. Its launch and completion model is too coarse for itembank's objective evidence and local review semantics. | **Defer export only.** Do not adopt its runtime or evidence model. |
| EPUB 3.3 | Standard distribution and interchange format for accessible publications with reading-system expectations. | Strong fit for durable reading and audio-capable export, weak fit for authoritative interactive assessment. Reading systems vary, so fallback remains necessary. | **Prototype EPUB export** for accepted readings and lessons, with landmarks, metadata, citations, math, alt text, and static activity representations. Keep sittings in itembank. |
| Jupyter/nbformat | Schema-defined document of cells, outputs, and metadata with separate execution tools. | Excellent external artifact for computational courses, but poor canonical source for a general course and unsafe to auto-run. | **Accept linking and bounded conversion.** Preserve notebook identity and environment metadata; never silently flatten or execute. |
| OLX and LMS-specific formats | Open edX supports course import/export through OLX. | Course portability can still be platform-shaped and costly to maintain. | **Open question.** Add only when a named institutional workflow justifies a tested adapter. |

**Observed fact:** The binding Directive says, "Exactly one parser, one scorer,
one evidence store," and "Format changes are additive." It also says the
runtime owns scoring, state, evidence, and keyed disclosure.

**Inference:** These rules reject a second authoritative implementation, not
loss-aware adapters. A QTI or EPUB adapter can map to or from the one internal
model while recording unsupported semantics.

**Recommendation:** Every adapter must declare direction, supported profile,
losses, ownership, provenance, validation result, and whether identity survives
a round trip. Never label syntactic import as semantic equivalence.

## 6. Cross-cutting pattern inventory

| Pattern | Pedagogical purpose and benefit | Weakness, cost, or failure mode | Applicability to itembank |
|---|---|---|---|
| Objective plus artifact lifecycle | Keeps a course current and explains what changed | Versioning, migration, review, and stale-link work | High. Course generation otherwise becomes disposable output. |
| Capability support profile | Makes rich activities testable across input, output, assistive technology, offline state, and version | Significant per-capability QA and maintenance | Essential before adding simulations, H5P, audio, or visual assessment. |
| Learner-created artifact | Supports self-explanation, production, reflection, projects, and authentic practice | Often needs human review; storage and privacy expand | High, but evidence must remain pending or descriptive. |
| Post-attempt remediation chain | Converts a miss into source revisit, misconception correction, transfer, and later retrieval | Longer than instant answer review; authoring cost | High. It unifies lesson, practice, and retention. |
| Coach triage queue | Uses scarce human attention on pending or repeated problems | Risks surveillance and context collapse | Prototype as local export with learner control. |
| Offline readiness manifest | Makes degraded behavior explicit before travel or outage | Asset packaging, updates, sync, and conflict tests | High and consistent with a resilient local core. |
| Source-synchronized multimodality | Lets learners choose reading, audio, visual, or interactive treatment without losing grounding | Every modality can drift; audio and images raise provenance cost | Accept only when tied to the same semantic source and objective. |
| Collaboration provenance | Distinguishes individual, pair, group, and reviewed work | Identity and consent complexity | Additive future-proof metadata; defer live collaboration. |
| Standards adapter with loss report | Enables exchange without surrendering internal authority | Mapping and conformance maintenance | Defer until a real import/export workflow, then prototype narrow profiles. |
| Purposeful play | Lets a learner manipulate the system being learned and fail safely | High design cost and weak transfer when mechanics are merely decorative | Prototype only for objectives where game action is authentic practice. |

## 7. Accessibility, portability, privacy, provenance, and authorability

### Accessibility

**Observed fact:** H5P publishes accessibility status per content type and
version and warns that example content can fail through author choices. PhET
publishes feature coverage by simulation. Desmos documents Braille and audio
graph access. Kolibri tells curators to ask whether an inaccessible medium is
necessary and to provide alternatives.

**Inference:** A platform-level WCAG claim cannot certify authored lessons.
Accessibility metadata must attach to the content instance and capability, and
testing must include task completion with assistive technology. Disability-led
co-design discovers learning representations, such as sonification, that a
compliance checklist misses.

**Recommendation:** Agent skills must lint objective content risks and require
human or tool-assisted review for meaningful sequence, captions, transcripts,
math speech, table headers, link purpose, motion, contrast, input equivalence,
and cognitive load. Record known exceptions. Do not let AI self-certify
accessibility.

### Portability and maintenance

**Observed fact:** Pressbooks and EPUB separate durable publication from the
authoring service. H5P packages versioned executable libraries. Jupyter outputs
can outlive the environment that produced them. Offline Open edX regenerates
packages when published blocks change.

**Inference:** Portability has levels: readable, structurally editable,
behaviorally executable, evidence-preserving, and round-trip safe. "Export"
without naming the level is misleading. Richness creates a maintenance tail.

**Recommendation:** Give every course a portability report across those five
levels. Legacy upgrades start with an audit, migrate one semantic capability at
a time, preserve identity and fallback, and show whether accepted evidence or
learner progress is affected.

### Privacy and incentives

**Observed fact:** LMS and adaptive products can collect detailed engagement,
answer, grade, and comparison data. AI tutoring can observe process. Some
consumer learning products couple mistakes and continuity to paid relief or
habit mechanics.

**Inference:** More process data can improve feedback, but it also changes the
psychological learning space. Learners may avoid experimentation if every
action feels evaluated. Page views, time, and click paths are weak learning
evidence and strong surveillance inputs.

**Recommendation:** Collect the minimum event needed for an explicit learning
purpose, state that purpose at collection, keep private scratch work separate
from submitted evidence, allow deletion or non-observed practice, and never
sell relief from mistakes. Instructor exports are learner-initiated and scoped.

### Provenance and authorability

**Observed fact:** Reusable ecosystems make copying or remixing easy, while
source-grounded generation makes derivative media cheap.

**Inference:** Cheap generation moves cost from drafting to verification,
licensing, accessibility, and staleness management. Every semantic capability
also needs an authoring affordance, validation rule, preview, and repair path.

**Recommendation:** Agents should prefer a small, well-supported capability
vocabulary. For each generated artifact, record source locator, license or
ownership, synthesis label, generator, prompt or plan fingerprint where useful,
reviewer, accepted version, and downstream dependencies. A capability with no
validator or accessible preview stays experimental.

## 8. Implications for Phase 16 outputs

### Learner flow

The landscape adds several states to the simple read, check, practice, test
loop:

1. choose or accept a next action with a visible reason;
2. download or validate offline readiness when needed;
3. orient to objective, source, expected activity, and privacy state;
4. read, listen, manipulate, predict, discuss, or create;
5. submit authoritative responses only through the runtime, while private
   scratch and learner artifacts remain distinct;
6. review feedback, source, and misconception;
7. apply in a changed context;
8. route pending artifacts to self, peer, or coach review;
9. schedule retrieval or a prerequisite action;
10. resume with content version and synchronization state visible.

### Semantic content contract

The Phase 16 contract should describe semantic roles, not product widgets. New
candidate roles exposed by this study are:

- `artifact activity`, for a proof, program, diagram, explanation, annotation,
  project, or field observation;
- `interactive model`, with controls, observable state, prediction, static
  representation, and capability support profile;
- `audio companion`, with transcript, chapters, citations, and navigation;
- `collaborative context`, recording pair or group participation without
  claiming individual mastery;
- `review request`, linking an artifact or prose response to criteria and
  reviewer status;
- `offline manifest`, derived from content and assets rather than handwritten
  lesson prose;
- `publication state and dependency`, for draft, accepted, superseded, stale,
  and retired artifacts.

These are candidates for synthesis, not a demand that all become Markdown
syntax. Derived manifests and review state may belong beside the durable lesson
file.

### Agent skills

Agent instructions should require a treatment decision before media creation,
an authoring and maintenance budget, provenance and licensing checks, a
capability support audit, offline behavior, evidence authority, and a rejection
test. Agents must not infer that an attractive interaction is accessible,
portable, or educational. They should produce a loss report for import/export,
flag stale derived media after source changes, and never run untrusted
executable content.

### Legacy upgrades

An upgrade audit should identify current identity and source, learner evidence,
content version, accessibility defects, external dependencies, static
fallback, and whether a new capability changes assessment meaning. Cosmetic
conversion is rejected. A simulation, audio companion, or interactive block is
accepted only if it teaches an identified objective better and leaves a useful
plain-file path.

## 9. Accept, reject, defer, prototype, and open questions

| Status | Candidate | Reason and boundary |
|---|---|---|
| **Accept** | Versioned artifact lifecycle and stale-derived-artifact detection | Required for maintainable source-to-course generation. Keep accepted source and derived indexes distinct. |
| **Accept** | Capability support profiles | Accessibility, offline, security, fallback, and maintenance attach to a capability instance and version. |
| **Accept** | Learner artifacts with pending or descriptive evidence | Enables authentic creation without auto-grading prose, projects, proofs, or drawings. |
| **Accept** | Post-attempt remediation chain | Connect miss, misconception, source, explanation, changed-context transfer, and later retrieval. |
| **Accept** | Audio as a synchronized companion | Transcript, navigation, citations, and resume are mandatory; audio is not the sole assessed representation. |
| **Accept** | Offline readiness report | A course declares size, assets, degraded capabilities, fallback, queued writes, and update identity. |
| **Accept** | Collaboration provenance fields | Future-safe distinction among individual, paired, group, and reviewed work; no current social platform implied. |
| **Accept** | Loss-aware adapter principle | Import and export can map through the one parser and scorer when unsupported semantics are explicit. |
| **Reject** | Engagement telemetry as learning evidence | Page views, clicks, streaks, and time cannot establish understanding. The binding contract also keeps evidence on disk and forbids telemetry. |
| **Reject** | Lives, hearts, paid error relief, public leaderboards, compulsory streaks | They punish error or absence and align monetization with friction rather than learning. |
| **Reject** | Arbitrary author-supplied JavaScript or auto-running imported notebooks | Security, reproducibility, accessibility, and maintenance costs are uncontrolled; `REQUIREMENTS.md` VIS-01 already refuses bank-authored JavaScript. |
| **Reject** | One opaque personalization or mastery score | It conflates readiness, retention, support, and uncertainty and undermines explainability. |
| **Reject** | Visual alternative described only by alt text | Equivalent learning needs control, state, feedback, and evidence, not just description. |
| **Reject** | Peer percentile as mastery or readiness | Comparison population and preparation stage confound the claim. |
| **Defer** | Accounts, rosters, gradebook, certificates, e-commerce, and live cohorts | High administration, privacy, and authorization cost for no present single-learner need. Keep semantics future-safe. |
| **Defer** | SCORM and OLX adapters | Add only for a named institutional workflow. Never adopt their runtime or evidence as internal authority. |
| **Defer** | Full QTI 3 import/export | Valuable exchange target, but requires a supported profile, conformance fixtures, key handling, identity rules, and loss reports. |
| **Defer** | Generative podcast dialogue | Test factual drift, citations, accessibility, cost, and caching before adding beyond deterministic TTS. |
| **Defer** | Cross-device evidence merge | Requires explicit conflict and ownership semantics; offline duplicate submission alone can use current idempotency. |
| **Prototype** | One accessible visual-math interaction | Keyboard, touch, screen reader, sonification, static fallback, and equivalent evidence in one tracer. |
| **Prototype** | EPUB 3.3 lesson export | Tests durable reading, navigation, metadata, citations, math, alt text, and static activity fallback. |
| **Prototype** | Local coach review packet | Learner-controlled export of pending work and evidence rationale without keys or full history. |
| **Prototype** | Offline course package and interruption tracer | Selective download, missing model, queued responses, resume, duplicate submit, content update, and honest degradation. |
| **Prototype** | Learner artifact activity | A self-explanation or small program with rubric, local file link, pending review, and later reflection. |
| **Prototype** | Narrow QTI round trip | A small supported item subset exported, imported, linted, and compared with an explicit loss report, using the existing scorer only. |
| **Open** | Where do publication state and review state live without creating a second source of truth? | Decide in stream 04 or synthesis after mapping durable versus derived files. |
| **Open** | Which artifact types deserve first-class UI versus a link to an external file or tool? | Base on objective, review need, accessibility, and maintenance cost. |
| **Open** | What minimum collaboration metadata is useful before accounts exist? | Avoid premature identity infrastructure while preserving evidence honesty. |
| **Open** | Which QTI profile and target systems justify adapter cost? | Requires a named real workflow and fixtures from those systems. |
| **Open** | Can audio and sonification be validated automatically enough for agent authoring? | Likely needs human listening and assistive-technology testing. |
| **Open** | What is the content-version policy for a learner mid-course? | Options include pin, migrate with acknowledgement, or apply only non-semantic fixes. |

## 10. Concrete recommendations and risks

### Recommendations for stream 06 synthesis

1. Make capability support profiles a Phase 16 deliverable. A catalog entry is
   incomplete without teaching purpose, content representation, accessible
   interaction, offline behavior, evidence authority, version, validator, and
   known limitations.
2. Extend the flow from consumption and scored response to include learner
   creation and pending review. This is the largest pedagogical category absent
   from the current contract.
3. Specify post-attempt remediation as a workflow, not merely an explanation
   panel.
4. Add publication and staleness semantics before AI can regenerate many
   course artifacts cheaply.
5. Treat offline as a course capability audit with synchronization behavior,
   not a blanket product adjective.
6. Reframe standards as adapter profiles. Prototype EPUB soon, QTI narrowly,
   H5P only as linked or bounded external content, and SCORM only when an LMS
   workflow exists.
7. Give instructor and peer support a local, learner-controlled review-packet
   path before building accounts or social infrastructure.
8. Distinguish accessible reading from equivalent accessible participation.
   Use disability-led exemplars such as PhET and Desmos as the quality bar.
9. Separate curriculum readiness, retention scheduling, and within-activity
   tutoring in both evidence and explanation.
10. Establish an incentives policy that permits purposeful play and calm
    progress while refusing monetized friction and compulsive engagement.

### Principal risks if Phase 16 misses these findings

| Risk | Consequence | Early verification gate |
|---|---|---|
| Widget accumulation without lifecycle | AI creates attractive artifacts that become stale, duplicated, or impossible to maintain | Change a source and show every affected accepted or derived artifact and its status. |
| Renderer-level accessibility claim | Authored content or interaction excludes learners despite passing general UI checks | Complete one representative activity by keyboard, touch, screen reader, and nonvisual output. |
| Passive-only course model | Reading and quiz recognition crowd out explanation, production, projects, and transfer | Course tracer includes one learner artifact and a review path without automatic mastery. |
| Offline page-only thinking | Learner loses hints, assets, scoring, or progress with no warning | Run the tracer disconnected through submit, resume, update, and reconnection. |
| Standards maximalism | A second model or lossy import silently changes scoring and meaning | Every adapter emits a supported-profile and loss report and hands scoring to the existing runtime. |
| Opaque adaptation | Learner cannot understand, contest, or recover from a recommendation | Every next action names the evidence, denominator, policy layer, uncertainty, and alternatives. |
| Social feature creep | Privacy, moderation, authorization, and comparison incentives dominate the personal learning loop | Prototype only a scoped review packet and measure whether it solves the real feedback need. |
| Generated-media enthusiasm | Audio, images, or simulations multiply factual, licensing, accessibility, and storage costs | Require treatment rationale, source links, fallback, capability audit, and stale detection before acceptance. |
| Engagement incentives | The system rewards opening and streak preservation over durable learning | No engagement-only metric may drive mastery, readiness, or punitive access. |

## Bottom line

The broad landscape does not justify a larger gallery of lesson widgets. It
justifies a stricter learning-program contract. The differentiating opportunity
is to keep sources, objectives, authored treatments, learner artifacts,
authoritative assessment, accessibility, offline behavior, review, and revision
connected without making any proprietary renderer or AI conversation the only
place the course exists.

The strongest additions are capability support profiles, learner-created
artifacts with honest review state, post-attempt remediation, publication and
staleness semantics, offline readiness, and loss-aware exchange adapters. The
strongest rejections are monetized error friction, engagement telemetry as
learning evidence, arbitrary executable lesson code, inaccessible interaction
masquerading as a visual plus alt text, and opaque personalization scores.
