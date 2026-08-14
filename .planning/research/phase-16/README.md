# Phase 16 research program

**Status:** ready for separate research tasks.

**Purpose:** produce the evidence and design space for Phase 16, Learning Flow
and Lesson Capability Contract. Phase 17 will design and implement the visual
system against the accepted Phase 16 contract.

## Research streams

| Stream | Required output | Primary question |
|---|---|---|
| Source-grounded product landscape | `01-source-grounded-products.md` | What can itembank learn from NotebookLM and adjacent tools without becoming a chat notebook? |
| Lesson flow and capabilities | `02-lesson-flow-capabilities.md` | Which lesson flows and semantic teaching capabilities improve learning across different subjects? |
| Question and activity design | `03-question-activity-matrix.md` | Which question and activity families fit prediction, instruction, practice, transfer, and assessment? |
| Portable lesson contract and agents | `04-portable-contract-agents.md` | How should portable lesson files, rich rendering, media, skills, and legacy upgrades work together? |
| Learning-program landscape and blind spots | `05-learning-program-landscape.md` | What do learning platforms, course builders, interactive textbooks, tutoring systems, assessment tools, and adjacent endeavors reveal that the first four streams missed? |
| Lesson feature and style atlas | `06-feature-style-atlas.md` | What lesson, reading, note, authoring, extraction, style, and testing features exist across mainstream, niche, book-derived, and open-source systems? |
| File lifecycle, interoperability, and edge cases | `07-file-lifecycle-edge-cases.md` | How should itembank find, link, edit in place, organize, reconcile, and preserve files and mixed executable artifacts without forcing relocation? |
| Curriculum hierarchy, pathways, and progress | `08-curriculum-hierarchy-progress.md` | How should fields, branches, programs, semesters, courses, concepts, objectives, and evidence form flexible structures with honest progress? |
| App information architecture, onboarding, and chained flows | `09-app-flow-information-architecture.md` | What should the app show, in what order, and how should discovery, building, learning, practice, testing, review, and resumption connect? |
| Visual experience and interaction system | `10-visual-experience-system.md` | How should the packaged app look and feel coherent, appealing, accessible, responsive, and appropriate across learning and authoring states? |
| Cross-cutting risks, learner control, and validation | `11-cross-cutting-risks-validation.md` | Which privacy, rights, personalization, motivation, scale, search, localization, evaluation, synchronization, and maintenance concerns could invalidate otherwise attractive designs? |
| Active annotation and learner-built notes | `12-active-annotation-notes.md` | When should lessons pre-highlight, prompt, require, or capture learner highlighting, restatement, and note construction, and how should those notes feed review and questions? |
| Expected capabilities and omission audit | `13-expected-capabilities-omissions.md` | What must a coherent source-to-course product reasonably support when derived from user jobs, lifecycle stages, failure modes, and quality promises rather than remembered feature lists? |
| Synthesis and recommendation | `14-synthesis.md` | How do the vision, evidence, rules, capabilities, modes, and skills coalesce into one coherent product and phased contract? |

### Broad landscape coverage

Stream 05 is deliberately wider than a competitor feature checklist. It should
sample different product and research families instead of reviewing five tools
that share the same model:

- Source-grounded study and research workspaces.
- Course authoring, learning management, and instructional-design systems.
- Interactive textbooks, simulations, coding environments, and visual math.
- Practice, assessment, exam-preparation, adaptive-learning, and tutoring
  systems.
- Spaced repetition, note-linked learning, cohort or instructor workflows,
  accessibility-first learning, games, audio learning, and offline education.
- Open standards and ecosystems such as QTI, H5P, SCORM, EPUB, and executable
  notebook formats where they affect portability or authorability.

The stream must compare complete workflows, incentives, evidence models,
authoring costs, failure modes, and neglected learner needs. It must identify
features or product categories absent from the other four reports, including
ideas that itembank should reject.

### Feature atlas coverage

Stream 06 inventories possibilities before ranking them. It should cover:

- Reading interactions such as hover, focus, touch, highlights, annotations,
  marginalia, bookmarks, linked definitions, previews, citations, and source
  comparison.
- Semantic emphasis such as key ideas, things to remember, warnings, common
  errors, expert tips, prerequisites, examples, counterexamples, summaries,
  and confidence or uncertainty labels.
- Note outputs such as notebook pages, outlines, Cornell notes, concept maps,
  glossaries, formula sheets, timelines, comparison tables, study guides, and
  extracted source notes.
- Full-learning outputs such as guided lessons, worked-example sequences,
  prediction and reveal, simulations, cases, inquiry, practice, transfer, and
  cumulative review.
- Authoring modes such as manual composition, source extraction, AI synthesis,
  template conversion, style transformation, block insertion, and legacy
  enhancement.
- Instructional styles inspired by books and genres, including plain-language
  beginner guides, reference handbooks, visual explainers, worked textbooks,
  field guides, casebooks, Socratic lessons, and concise exam review. Study the
  transferable conventions without copying a protected voice, layout, or text.
- Mainstream products, niche programs, research prototypes, open-source GitHub
  projects, plugins, standards, and book or publishing conventions.
- Missing-feature tests that run representative EMT, mathematics, computer
  science, and knowledge-course material through current and proposed flows.

The atlas must distinguish content semantics, interaction behavior, visual
theme, teaching strategy, output mode, and authoring workflow. A feature can
appear in more than one presentation, and a style cannot silently change facts,
citations, objective alignment, or assessment meaning.

### File lifecycle and edge-case coverage

Stream 07 tests whether the product respects files where they already live. It
should cover:

- Finding previous files across approved roots, linking them in place, editing
  at their current location, creating relevant folders, moving files, resolving
  broken links, and explaining every operation in user language.
- Executable notebooks and similar mixed prose, code, output, data, and
  interaction artifacts, including when to link, import, render, or convert.
- Read-only files, removable and network volumes, aliases, symlinks, cloud-sync
  placeholders, renamed vaults, duplicate names, case differences, permissions,
  concurrent edits, external-editor changes, deleted targets, partial moves,
  path portability, encoding, large files, and unsupported formats.
- Provenance, stable identity, fingerprints, conflicts, backups, undo,
  migrations, diagnostics, and recovery from interrupted operations.

The default should be link and edit in place. Moving or copying requires a
clear user choice and a stated reason. Discovery never grants write authority.

### Curriculum hierarchy and progress coverage

Stream 08 should cover:

- Course hierarchy from field to branch, program, year or semester, course,
  unit, concept, objective, lesson, activity, and assessment without assuming
  every subject uses the same levels.
- Prerequisite graphs, alternate paths, electives, cross-listed concepts,
  reusable lessons, subcourses, versioned syllabi, and courses assembled from
  more than one source or institution.
- Progress at each level, including what completion means, who defines it, how
  evidence and coverage differ, how unknown or optional scope is shown, and why
  an open-ended field must not receive a false 100 percent boundary.

The stream must test at least one complex curriculum with several hierarchy
levels and prerequisite branches. Mathematics is a useful case because a field
has disputed boundaries, overlapping branches, multiple valid sequences, and
no honest universal completion point.

### App flow and information architecture coverage

Stream 09 maps what the app shows and how work chains together. It should cover:

- First launch, sample content, walkthroughs, empty states, contextual help,
  progressive disclosure, README guidance, and returning-user resumption.
- Course shelf, source discovery, build and review, course map, learn, notes,
  practice, test, evidence, search, settings, diagnostics, and agent activity.
- Primary and secondary navigation, breadcrumbs, back behavior, deep links,
  recent work, next actions, interruptions, long-running operations, drafts,
  approvals, errors, recovery, and transitions between modes.
- End-to-end task flows for starting from a book, syllabus, existing folder,
  old lesson, question bank, executable notebook, or empty course.
- What is always visible, contextually visible, hidden until needed, or never
  shown to the learner.

The output must include state diagrams, task-flow maps, screen inventories, and
representative desktop and narrow-screen wireframes before visual styling.

### Visual experience coverage

Stream 10 researches and prototypes the app's visual and interaction language.
It should cover:

- Visual hierarchy, typography, spacing, color, surfaces, icons, imagery,
  diagrams, motion, density, themes, focus, selection, progress, status, and
  feedback.
- Coherence across reading, guided lessons, notes, questions, tests, course
  maps, sources, authoring, diffs, agent activity, settings, and diagnostics.
- Appealing presentation without decorative clutter, false gamification,
  inaccessible contrast, excessive cards, or visual novelty that obscures the
  learning task.
- Responsive behavior, keyboard and touch behavior, reduced motion, zoom,
  screen readers, high contrast, localization, long content, and degraded or
  offline states.
- Visual references from mainstream, niche, open-source, publishing, learning,
  productivity, and creative tools, with pattern analysis rather than copying.

The output must compare several coherent visual directions against the same
flows and content. It should recommend tokens, reusable primitives, visual QA
gates, and what remains configurable.

### Cross-cutting validation coverage

Stream 11 challenges the other recommendations before synthesis. It should
cover:

- Learner preferences, prior knowledge, accommodations, pacing, autonomy,
  overrides, explanation depth, and the boundary between adaptation and user
  control.
- Motivation, confidence, progress communication, reminders, and habit support
  without punitive streaks, manipulative gamification, or false mastery claims.
- Privacy, local data boundaries, source rights, media licensing, generated
  content provenance, sensitive subjects, retention, export, and deletion.
- Search and recommendation quality, including ranking explanations, stale
  indexes, duplicate concepts, multilingual content, and large collections.
- Performance, reliability, recovery, storage growth, backups, multi-device or
  sync boundaries, sharing and collaboration boundaries, and packaged-app
  update economics.
- Localization, right-to-left text, math and code notation, units, reading
  level, disability access, and culturally specific examples.
- Evaluation of whether the product improves learning, authoring quality, and
  time-to-course without relying on telemetry or misleading aggregate scores.
- Maintenance cost for semantic formats, renderers, skills, generated assets,
  migrations, dependencies, research refreshes, and user documentation.

The output should define adversarial scenarios, measurable validation methods,
and kill or redesign criteria for recommendations that fail these checks.

### Active annotation and learner-note coverage

Stream 12 researches note construction as part of learning, not only as an
output format. It should cover:

- Author pre-highlighting, optional learner highlighting, prompted selection,
  required identification, copying, paraphrasing, summarizing, explaining,
  organizing, linking, and drawing or diagramming.
- The difference between generative note-taking and low-value transcription,
  including when typing material again helps or merely adds friction.
- Learner-owned note documents assembled during a lesson, with provenance back
  to source passages, objectives, lesson steps, media, and learner language.
- Sequences such as source to notes to quiz, source to generated lesson to
  notes, notes to lesson, lesson to notes to practice, and hybrid or optional
  modes.
- Question creation from source material, accepted lessons, learner notes, or
  combinations, including how incorrect or incomplete learner notes are kept
  from becoming assessment authority.
- User choice versus course or activity requirements, accessibility
  alternatives, skip behavior, privacy, editing, export, later review, and
  integration with spaced repetition.
- Strategy registration so several evidence-backed modes can coexist without
  multiplying parsers, scorers, document truths, or inconsistent UI paths.

The output must propose realistic prototypes and missing-feature tests across
EMT, mathematics, computer science, and a reading-heavy subject.

### Expected-capability and omission coverage

Stream 13 derives capabilities independently of competitor lists. It should:

- Model the jobs of learners, course builders, reviewers, source owners,
  instructors where applicable, and agent clients across the full lifecycle.
- Walk every state from installation and first launch through discovery,
  planning, learning, notes, practice, testing, evidence, revision, export,
  migration, recovery, and long-term maintenance.
- Apply failure-mode, accessibility, privacy, provenance, interoperability,
  scale, and degraded-state analysis to find missing baseline behavior.
- Compare the derived expectations with Streams 01 through 12 and identify
  omissions, duplicate proposals, unsupported assumptions, and features that
  lack an owner or verification method.
- Classify each capability as baseline, differentiator, optional extension,
  subject-specific, user-selectable strategy, research prototype, or reject.
- Identify capabilities that should emerge from existing primitives rather
  than become separate features.

The report must include a completeness argument. It cannot prove that no idea
was missed, but it must show that the search covered user jobs, lifecycle
states, system boundaries, failure modes, and quality attributes instead of
stopping when the feature list felt long.

## Required structure for each research document

1. Scope and research questions.
2. Sources with direct links, access dates, and source type.
3. Observed facts separated from inference and recommendation.
4. Pattern inventory with benefits, weaknesses, and applicability to itembank.
5. Accessibility, portability, privacy, provenance, and authorability effects.
6. Implications for the learner flow, semantic content contract, agent skills,
   and legacy upgrades.
7. Accept, reject, defer, prototype, and open-question table.
8. Concrete recommendations and risks.

Use current primary sources when documenting product behavior. Secondary
research is appropriate for learning science and comparative analysis when its
methods and limitations are stated. Do not copy proprietary content, visual
assets, branding, or protected interaction details.

## Synthesis gate

The synthesis task reads all thirteen stream documents and the coverage audit. It identifies agreement,
conflict, gaps, assumptions, and evidence quality, then proposes:

- The logical course and lesson flow.
- The lesson-capability catalog.
- The question-purpose and activity matrix.
- The portable authored representation and derived UI boundary.
- The media and citation policy.
- The agent skill and legacy-upgrade plan.
- Phase 16 prototypes and verification gates.
- Phase 17 visual-design inputs.

Synthesis must also produce:

- One product model with named objects, actors, boundaries, and sources of
  truth.
- A small set of core user loops that explain how the product works end to end.
- A primitive set showing which features compose from shared semantics and
  which require distinct contracts.
- A mode and strategy model showing what users may choose and what pedagogy,
  accessibility, or assessment authority fixes.
- A disposition ledger for every proposal, including reasons and revisit
  triggers for rejected or deferred ideas.
- A traceability matrix from user vision to research evidence, product
  contract, requirement, phase, skill, and verification gate.
- A contradiction and simplification pass that removes redundant rules and
  refuses combinations that weaken the whole experience.

Coherence does not require feature deletion. Every viable proposal lands as
core, configurable or registered, prototype, or backburner. Backburner entries
retain dependencies, estimated cost drivers, and revisit triggers. Several
capabilities may ship together when they compose from shared primitives at
reasonable implementation and verification cost. Reject only for a named
conflict with authority, accessibility, rights, safety, truthful evidence,
portability, or the coherent product model, and preserve the rejected proposal
and rationale in the ledger.

Every rejected entry records the original proposal, originating vision or
research source, evidence considered, exact reason, conflicting product rule or
quality attribute, alternatives retained, decision date, and reconsideration
condition. Distinguish hard rejection from backburner, deferred pending
evidence, and superseded by a better mechanism. Rejection never means silent
deletion.

## Future implementation-readiness audit

Research synthesis does not answer when all work should be executed. After the
Phase 14 through 17 contracts, requirements, and dependencies are updated, run
a separate readiness audit that:

1. Maps every accepted recommendation to an owner, phase, dependency, and
   verification gate.
2. Detects duplicate, missing, circular, or prematurely scheduled work.
3. Separates foundation, prototype, productization, migration, documentation,
   packaging, and maintenance tasks.
4. Identifies which decisions still need ideaboarding, research, user choice,
   or a reversible prototype.
5. Produces a realistic execution sequence and names the trigger for the next
   audit.

Only accepted synthesis conclusions update `SOURCE-TO-COURSE.md`,
`REQUIREMENTS.md`, `ROADMAP.md`, or `UI-SPEC.md`. Research files remain the
durable evidence trail.
