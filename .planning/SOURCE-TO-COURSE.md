# Source-to-course product contract

**Status:** binding direction for the next milestone. This refines the product
goal without invalidating the shipped parser, scorer, evidence, lesson,
authoring, or packaging work.

**User intent:** `.planning/USER-VISION.md` preserves the goal in Weibao's
words verbatim and remains additive. This contract is an interpretation of
that record, not a replacement for it. When wording or scope appears to drift,
reconcile it against the verbatim record explicitly.

**Research and agent operation:** `research/phase-16/14-synthesis.md` is the
reconciled evidence and product-definition input for the next contract
revision. `AGENT-WORKFLOW.md` is the binding cross-agent procedure for vision
capture, ideaboarding, research waves, synthesis, dispositions, authority,
artifact operations, readiness, and handoff. Open or prototype-gated synthesis
recommendations do not become durable format commitments until their stated
gate passes.

## North star

itembank turns learner-owned material into a tangible, high-quality course. A
course may begin with a book, syllabus, exam blueprint, folder of notes,
existing bank, or a mixture. The system and an approved AI collaborator
discover the material, derive and verify objectives, decide how each objective
is best learned, produce missing artifacts, administer practice and tests, and
revise the path from recorded evidence.

itembank is a local-first, agent-operable learning harness for people. Its
stable contracts connect sources, objectives, treatments, learning activities,
assessments, evidence, validation, permissions, and accepted revisions. AI may
operate and extend those learning workflows, but the product is not primarily
an AI-training, reinforcement-learning, prompt-optimization, or model-evaluation
harness. Those uses may later enter as registered capabilities only when they
serve the learner-centered course system and retain the same authority,
inspectability, rights, and recovery boundaries.

The course is the primary user-facing object. Objectives are its organizing
spine. Sources, readings, lessons, terms, notes, examples, visuals, practice
banks, tests, and evidence are connected artifacts rather than separate
products.

## Product experience and delivery

itembank is a local-first desktop product with the coherence and convenience
people expect from mature SaaS software. This is an experience standard, not a
hosting model. First use is guided. The course shelf gives a clear place to
begin and return. Long AI and maintenance operations expose durable state,
needs-input, recovery, and undo. Navigation and controls behave consistently.
Settings explain storage, network use, model choice, privacy, and updates in
language a learner can act on.

The installed application and browser-served UI remain clients of the same
local runtime. The shipped Tauri shell is the desktop container. Electron is
not a product requirement. Canonical courses, sources, banks, evidence, and
operation records stay on the learner's device. Optional hosted model calls
follow the existing rights and egress contract. This direction does not add
accounts, multi-tenancy, hosted storage, cloud gradebooks, or subscription
billing. Any later commercial or synchronization layer requires its own
decision and may not silently move assessment or content authority off device.

## The course-building loop

1. **Discover and register sources and prior work.** Find approved files
   without assuming their location, including previously created lessons,
   questions, exams, notes, and banks distributed across explicit roots such
   as a course folder and an Obsidian vault. Fingerprint them; retain stable
   page/section locators, provenance, and ownership; and link rather than copy
   an existing artifact when it already supplies the needed treatment.
2. **Establish the target.** Extract or import the syllabus, standards, exam
   blueprint, competencies, intended depth, constraints, and learner context.
3. **Build the objective map.** Produce stable hierarchical objectives,
   prerequisites, source support, assessment demand, and confidence. A heading
   match alone never proves coverage.
4. **Choose treatment per objective.** Prefer direct source reading when the
   source is clear and authoritative. Otherwise choose an excerpt, guided
   lesson, notes, key terms, worked example, visualization, demonstration,
   practice, or assessment-first treatment. Do not rewrite a source merely
   because a model can.
5. **Generate bounded artifacts.** Draft only the missing treatment, cite its
   sources, label generated synthesis, lint deterministic contracts, run
   semantic quality review, and keep approval and reversal visible.
6. **Deliver one learning loop.** Orient -> predict or act -> observe ->
   explain -> apply in a changed situation -> record evidence. Reader mode
   remains available for continuous source/reference reading.
7. **Practice and test appropriately.** Standardized-test courses follow the
   published blueprint, construct distribution, timing, difficulty, and item
   conventions. Knowledge exams follow the actual instructional objectives and
   expected cognitive demand, not generic trivia.
8. **Close the loop with evidence.** Use response history, hint use,
   confidence, response time, error patterns, retention state, coverage, and
   pending review to propose the next useful action. Report uncertainty and
   sample size; never turn sparse evidence into a mastery percentage.

## AI's reasonable role

AI is a first-class course builder, analyst, and optional teaching
collaborator. It may search approved roots, outline sources, extract candidate
objectives and terms, align sources to a blueprint, recommend treatment, draft
artifacts, run the lint/fix loop, inspect aggregate evidence, propose
remediation, and explain its citations and uncertainty. It may operate through
Codex, Claude Code/Cowork, another hosted coding-agent-class client, or a
registered local backend.

Autonomy is scoped per operation: recommend-only, draft-and-review, or approved
bounded writes. Discovery is read-only by default. Generated work is
distinguishable from source-authored work, and every accepted mutation is
inspectable and recoverable.

The model is not the deterministic authority. The existing runtime remains the
authority for scoring, session mode, evidence recording, and disclosure of
keyed assessment content. Prose responses remain pending until a human or
human-approved marking action settles them. This boundary must not be inflated
into the product thesis or used to prevent useful AI course-building work.

## Course-quality contract

A useful generated course must demonstrate:

- **Traceability:** every objective and source-derived claim has a stable
  locator; generated synthesis is labeled.
- **Coverage:** every required objective is covered, thin, missing,
  conflicting, or unknown by cited evidence rather than intuition.
- **Alignment:** treatment and assessment match the verb and cognitive demand
  of the objective and, where applicable, the real exam blueprint.
- **Instructional coherence:** prerequisites precede dependents; lessons do not
  become summaries followed by detached questions.
- **Assessment quality:** plausible distractors model real misconceptions and
  state when they would be correct; positions, difficulty, item families, and
  blueprint weights are reviewed; prose is not auto-graded.
- **Transfer:** important objectives include changed-context application, not
  only recall or near-copy questions.
- **Accessibility and degradation:** equivalent semantic controls exist for
  visual tasks; source reading, authored lessons, assessment, evidence, and
  reports remain useful without a model connection.
- **Measured improvement:** AI may interpret metrics and propose changes, but
  shows the evidence window, denominator, missing signals, and uncertainty.

## Learner experience

The home surface is a course shelf. A course workspace has six coherent areas:

- **Learn:** recommended readings, guided lessons, notes, terms, examples,
  visuals, and reviews.
- **Practice:** objective-, unit-, difficulty-, misconception-, and cumulative
  sets.
- **Test:** diagnostic, unit, cumulative, and blueprint-faithful exam sittings.
- **Sources:** books/files, outlines, locators, extraction status, conflicts,
  and direct-reading assignments.
- **Course map:** objectives, prerequisites, treatment, coverage, evidence,
  and gaps.
- **Build / review:** AI proposals, diffs, citations, quality findings,
  approval, rejection, and undo.

Lessons support a continuous reader and a guided presentation over the same
parsed content. The comprehensive UI supports hover/focus definitions,
things-to-know blocks, niche or expert tips, warnings, worked examples, source
citations, diagrams, math, runnable code, inline checks, hints, retries, and
accessible visual interactions. These are semantic teaching roles, not
decorative card types.

Measured Field Guide and Learning Trajectory Deck are user-switchable
presentation profiles over this same semantic content and runtime state. A
profile may change composition, navigation arrangement, density, and emphasis.
It may not change available activities, keyed disclosure, scoring, evidence,
source identity, or accessibility meaning. Color scheme, contrast mode, and
accent remain independent appearance settings. An unavailable or future-schema
profile falls back to a supported profile without changing canonical course or
learner data and reports the fallback visibly.

The complete presentation layer is extensible at named seams. Course shells,
navigation compositions, readers, activity renderers, editors, source views,
agent panels, exporters, and integrations consume stable semantic roles and
shared operation contracts. Presentation profiles arrange shared primitives.
Appearance themes supply visual tokens. Capability adapters map a declared
learning or integration capability to those primitives and provide a useful
static and unavailable fallback. Adding one must not require a second content
model, route catalogue, scorer, evidence store, permission system, or recovery
authority. Extension metadata describes compatibility and degradation. It does
not grant authority or prove that code is installed, safe, or available.

The authored lesson file is the durable content layer. It must remain coherent,
readable, navigable, and reasonably attractive in a plain Markdown or document
reader, including tools such as Obsidian. The itembank UI progressively
enhances that same content with richer presentation and behavior, including hover and
focus affordances, interactive diagrams, JavaScript-backed demonstrations,
adaptive disclosure, and other learning controls, without making the source
file depend on those enhancements for its meaning. A richer capability must
have a useful non-interactive representation and an accessible interaction.

### Durable reading activities, accepted 2026-09-12

A reading occurrence is one deliberate use of an accepted source range in a
course. It has stable identity and immutable accepted revisions. Two
occurrences may share the same source and binding without sharing completion.
Each revision names its course, objectives, permanent binding revision,
accepted source fingerprint, exact locator and assignment context. Opening a
source and reading time imply no completion. Only an explicit learner
declaration recorded by the existing evidence writer marks that occurrence
revision as reported read. Reading declarations and learner notes never become
response scores or mastery. Availability, staleness, acceptance and learner
declarations remain separate states. Legacy courses gain no inferred activity
or history. Accepted revisions and learner records survive restart and preserve
reviewable conflicts and explicit export or restore losses.

Title and Now/Library placement are separate metadata keyed by occurrence.
Renaming or moving an unchanged task retains its occurrence revision and
declaration. Changing the source range or task demand requires a new immutable
revision and never transfers a prior declaration automatically.

The [durable reading contract](research/source-to-reading/durable-reading-contract-2026-09-12.md)
owns the accepted format, staged implementation and evidence. Implementation
acceptance remains separate from product-direction acceptance. Exact cursor
resume, multiple spans and occurrence-private notes remain deferred.

### Owner-backed tasks in Today, accepted 2026-09-12

The [owner-backed to-do request](USER-VISION.md#2026-09-12-owner-backed-to-do-display-and-completion)
makes Today a ranked projection of live course assignment rows. The first
adapter reads the existing vault course-assignment-ledger table in place and
groups tasks into Now, Next, and Later. A compact task exposes its name, course,
due or overdue state, estimate, purpose, completion gate, and authoritative
source. Secondary owner details remain progressively disclosed.

The assignment ledger remains the completion authority. Checking or unchecking
a task changes only that exact Status cell through an expected fingerprint,
atomic replacement, append-only operation record, and retained before image.
An unavailable, malformed, or externally changed owner produces a visible
no-write state. Itembank keeps no copied task database. Day lane ticks remain
day-level evidence and never close an assignment.

### Learning experience and capability research

Do not design the course journey by accumulating attractive widgets. Research
the full learner flow first: entering a course, understanding the next action,
reading or interacting, checking understanding, receiving feedback, navigating
references, practicing, testing, reviewing evidence, and resuming later. Study
current learning and source-grounded tools, including NotebookLM, for useful
patterns in source navigation, generated questions, study aids, and grounded
conversation. Treat them as evidence, not templates. itembank's target is a
stronger lesson- and objective-centered course experience, not a notebook chat
with quizzes attached.

The research must produce a lesson-capability catalog. Candidate capabilities
include definitions available by hover, focus, and touch; relevant cited
images; captions and image alternatives; things-to-know, expert-tip, warning,
misconception, and memory blocks; worked examples; comparisons; timelines;
diagrams; math; code; simulations; prediction prompts; inline checks; staged
reveals; reflection; source excerpts; citations; and transfer activities. Each
capability must state its teaching purpose, suitable contexts, misuse risks,
portable source representation, rich rendering, keyboard and screen-reader
behavior, narrow-screen behavior, evidence implications, and authoring rules.

Question research must cover more than widget shapes. Build a matrix across
learning moment, objective verb, cognitive demand, subject, response form,
feedback mode, authenticity, accessibility, and scoring authority. Distinguish
questions used to predict, notice, retrieve, explain, compare, diagnose,
practice, transfer, and formally assess. Do not add a question type merely
because a competitor has one or because it is visually novel.

The authored representation may behave like an itembank document type, but it
should remain an open, inspectable semantic contract built on portable files
unless research proves that this cannot represent the required learning
behavior. Rich UI state, generated indexes, and compiled assets may be derived;
they must not become the only readable copy of a lesson.

## Agent-operable course workspace

The planned workspace convention must provide discovery, scaffolding, binding,
and a derived machine-readable index without creating a second source of
truth. Agents must be able to answer: what courses exist, where their sources
and accepted artifacts live, which objectives are unsupported, what evidence
exists, what is a draft, what may be changed, and how to validate or undo it.

Discovery and binding must work both manually and agentically. A user may add
an explicit file or folder and link an artifact to a course/objective; an agent
may search only approved roots, propose likely artifact identities and links,
and explain the evidence for each match. The system must distinguish linking,
importing, copying, and superseding, detect moved or changed files by stable
identity plus fingerprint, and surface duplicates or conflicts for review.
It must not silently merge similarly named lessons or questions.

Course files remain readable and searchable. Derived indexes are disposable.
Search roots and write roots are explicit; an agent does not roam the machine
or mutate a new location merely because it found a related file.

Agent playbooks are part of the product interface, not incidental prompts.
They must teach Codex, Claude Code/Cowork, local agents, and other compatible
clients how to discover and bind existing work; design a course; author and
review lessons, questions, practice, and exams; validate artifacts against the
runtime contracts; and improve an older artifact for newer learning-UI
capabilities. Upgrade playbooks must begin with an audit, preserve provenance
and stable identity, produce a reviewable proposal or diff, avoid cosmetic
rewrites that add no learning value, validate graceful degradation, and never
change assessment meaning or keyed content silently.

## Scope boundaries

- Do not equate course generation with one-shot “generate and publish.” Course
  construction is staged, cited, validated, and reviewable.
- Do not assume every objective needs a generated lesson. Direct reading is a
  first-class and often preferable treatment.
- Do not make chat the primary interface. Agent actions produce inspectable
  course artifacts and proposals.
- Do not add a second parser, scorer, or evidence store. A course manifest or
  index composes the existing contracts.
- Do not optimize the UI around banks as the primary navigation unit. Banks
  remain assessment artifacts inside courses.
- Do not claim standardized-test fidelity without a versioned blueprint/source
  and explicit content, difficulty, and item-format mappings.

## Next-milestone sequence

**Superseded 2026-08-13 - see the nine-subphase sequence.** The four-phase
sequence below (Phases 14 to 17) has been resequenced into nine subphases
(14A, 14B, 15A, 15B, 16A, 16B, 16C, 17A, 17B) with explicit dependencies and
freeze gates. The authoritative subphase table lives in
`.planning/research/phase-16/14-synthesis.md` section 15, and the roadmap
governance clauses (prototype before durable commitment; the
implementation-readiness and maintenance/restore audits; the capability runway;
and the permanent rejection ledger) live in `.planning/ROADMAP.md` under
"Next-milestone subphase sequence." The high-level order is unchanged: durable
course and file semantics precede AI course direction, and logical learning
contracts precede visual productization. The four broad phases are preserved
below verbatim as historical rationale, not deleted; they were too coarse and
placed some Phase 16 discoveries after Phase 14 format commitments, which is why
they were subdivided.

### Historical rationale - original four-phase sequence (superseded 2026-08-13)

### Phase 14: Course workspace and source binding

Define the course manifest/folder contract; safe discovery roots; scaffold and
bind operations; derived index; course shelf/map/source UI; objective and
prerequisite model; treatment vocabulary; and composition of existing banks
and lessons.

**Tracer:** create a course from one syllabus plus one source folder, approve
the objective map, bind cited source sections, and see gaps without generating
content.

Discovery includes an explicit multi-root tracer: bind an existing lesson from
one user-approved folder and an existing question bank from another (for
example, an Obsidian vault), then relocate one file and reconcile it without
duplicating or losing the course link.

### Phase 15: AI course director and quality pipeline

Add treatment recommendation, direct-reading selection, bounded artifact
plans, course-level generation/review, standardized-test and knowledge-exam
blueprints, course-quality audit, metric interpretation, and configurable
autonomy. Reuse the shipped `audit`, `coverage`, `seed`, lint, evidence, and
trends contracts.

**Tracer:** generate one missing lesson treatment and one blueprint-aligned
practice set, approve them, sit the set, and receive an evidence-backed
next-action proposal.

### Phase 16: Learning flow and lesson capability contract

Research and specify how the course journey works before committing to visual
chrome. Compare source-grounded and learning products, including NotebookLM,
without copying protected content or mistaking chat features for pedagogy.
Map course entry, next action, lesson flow, source use, questions, feedback,
practice, tests, review, and resume states. Produce the lesson-capability
catalog, question-purpose matrix, portable authoring grammar, interaction
contracts, accessibility behaviors, image and citation policy, legacy-upgrade
rules, and agent authoring descriptions.

**Tracer:** storyboard and prototype one representative course unit across
desktop, narrow screen, keyboard, touch, screen reader, offline, and plain-file
contexts. Demonstrate why each selected capability improves the learning loop
and reject or defer features without a clear teaching role.

### Phase 17: Visual system and comprehensive guided learning UI

Design the visual language and implement the course journey against Phase 16's
flow and capability contracts. Compose reader, guided lesson, practice, test,
source, and review states into one experience. Add the approved accessible
visual teaching primitives, responsive layouts, motion rules, density and
theme choices, and teaching-focused feedback. Preserve continuous reader mode.

**Tracer:** one polished multi-step course unit with direct reading, hover and
focus terms, things-to-know and expert-tip blocks, a cited visual explanation,
prediction, targeted feedback, varied practice, transfer, and course-path
continuation at desktop and phone widths.

The tracer must also open the authored lesson outside the itembank UI and show
that its structure, definitions, callouts, diagram fallback, citations, and
core explanation remain useful. It must exercise an upgrade audit on one
legacy lesson and one legacy question artifact before any enhancement is
accepted.

No phase is complete from framework tests alone. Each exits through a realistic
synthetic end-to-end course fixture and visual/accessibility verification.
