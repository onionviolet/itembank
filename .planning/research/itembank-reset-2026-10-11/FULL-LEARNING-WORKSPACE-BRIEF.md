Develop **Itembank** into a complete, learner-owned, local-first learning workspace for turning existing materials into structured courses, active learning, practice, assessment, and long-term retention.

The application should feel like a serious standalone learning product rather than an AI wrapper, document viewer, question generator, or collection of disconnected study tools.

The core idea is:

**Bring your materials → understand what already exists → structure the knowledge → learn it → practice it → assess it → retain it → return intelligently.**

Use the strongest ideas from modern learning products while keeping the application original in its design, implementation, interaction patterns, terminology, and assets.

Aim for:

- the interactive teaching quality of Brilliant,
- the practice depth and rigor of Albert,
- the research and source-grounding strengths of notebook-style tools,
- the rapid study workflows of Quizlet,
- the retention discipline of Anki,
- and the flexibility of a personal knowledge workspace,

without simply cloning any one product.

Do not default to AI personas, artificial classmates, simulated teachers, gamified noise, or chatbot-first interaction. AI should support the learning experience rather than become the learning experience.

# 1. Product Philosophy

Itembank should treat the learner as the owner of:

- their source material,
- their courses,
- their notes,
- their progress,
- their questions,
- their generated materials,
- their learning history,
- and their data.

Favor:

- local-first storage,
- readable/exportable files,
- transparent transformations,
- source traceability,
- modular architecture,
- graceful recovery,
- offline usefulness,
- and user control.

Avoid:

- unnecessary lock-in,
- opaque AI-generated content,
- mandatory cloud infrastructure,
- artificial feature restrictions,
- hidden scoring logic where transparency is appropriate,
- and generated materials that disappear into transient chat history.

If AI generates something useful, that work should become a persistent, revisable object in the workspace.

# 2. Reuse Existing Work Before Creating New Work

Before generating anything substantial, inspect what already exists.

Search for and reuse prior work from sources such as:

- existing It embank files,
- imported documents,
- course folders,
- external folders,
- Obsidian vaults,
- notes,
- prior generated lessons,
- question banks,
- flashcard sets,
- outlines,
- summaries,
- study guides,
- syllabus mappings,
- notebooks,
- past assessments,
- annotations,
- saved AI outputs,
- and other connected material.

Do not recreate material simply because generation is easier.

Prefer this hierarchy:

1. Reuse existing high-quality material.
2. Adapt existing material.
3. Combine existing materials.
4. Improve incomplete material.
5. Generate something new only when needed.

When content is reused or transformed, preserve provenance.

The learner should be able to determine:

- where something came from,
- whether it was original or generated,
- which sources informed it,
- when it was changed,
- and whether it has been reviewed.

# 3. Source Intake and Knowledge Ingestion

Support useful ingestion of:

- books,
- textbook chapters,
- syllabi,
- lecture notes,
- PDFs,
- slides,
- transcripts,
- webpages,
- Markdown,
- plain text,
- code,
- CSV or structured question banks,
- images where meaningful,
- existing flashcard sets,
- and learner-created material.

The intake process should do more than upload files.

Itembank should be able to identify:

- document type,
- title,
- author when available,
- course or subject,
- chapters and sections,
- headings,
- page ranges,
- key concepts,
- terminology,
- formulas,
- definitions,
- examples,
- exercises,
- learning objectives,
- syllabus weeks,
- stated examination requirements,
- dependencies,
- and likely relationships to existing material.

Preserve original files.

Generated structure should reference source material rather than replacing it.

Where practical, support synchronization or re-indexing when source files change.

# 4. Course Construction

Turn materials into useful courses rather than indiscriminately turning every document into generated lessons.

A course may contain:

- modules,
- units,
- topics,
- lessons,
- readings,
- explanations,
- examples,
- interactive activities,
- notebooks,
- practice sets,
- flashcard decks,
- assessments,
- projects,
- review sessions,
- and reference material.

Support arbitrary nesting where useful.

Example:

Course  
→ Unit  
→ Topic  
→ Lesson  
→ Reading  
→ Worked Example  
→ Practice  
→ Review

Support:

- prerequisites,
- dependency graphs,
- optional material,
- enrichment material,
- remediation,
- instructor-assigned order,
- exam-focused tracks,
- self-paced tracks,
- and alternative pathways.

Do not force every subject into the same structure.

# 5. Choose the Right Learning Treatment

For each learning objective, decide what kind of treatment is actually appropriate.

Possible treatments include:

- original source reading,
- annotated reading,
- learner notes,
- concise explanation,
- deep explanation,
- worked example,
- visual explanation,
- diagram,
- simulation,
- executable notebook,
- interactive lesson,
- guided derivation,
- flashcards,
- retrieval practice,
- drill,
- mixed practice,
- case study,
- coding exercise,
- writing prompt,
- assessment,
- or simply linking back to the source.

Do not generate a lesson merely because a lesson can be generated.

For example:

- Vocabulary may benefit from flashcards and retrieval.
- Calculus may benefit from derivations, worked problems, graphs, and practice.
- Programming may benefit from prediction, tracing, repair, and execution.
- History may benefit from primary sources, chronology, causation, comparison, and written argument.
- Biology may benefit from diagrams, labeling, processes, and applied questions.
- Political science may benefit from theories, definitions, cases, comparison, evidence, and argumentative practice.
- Language study may require production, recognition, listening, grammar, and contextual examples.

The learning architecture should adapt to the subject.

# 6. Instructor and Exam Alignment

When a learner provides a syllabus, assignment sheet, exam guide, learning outcomes, instructor materials, or past tests, use them to align the course.

Track distinctions between:

- source knowledge,
- instructor emphasis,
- likely exam relevance,
- learner weakness,
- and optional enrichment.

Support instructor-aligned pacing by understanding:

- class dates,
- syllabus weeks,
- readings,
- lecture sequence,
- assignments,
- quizzes,
- exams,
- deadlines,
- and review periods.

The system should help answer:

- What should I know now?
- What is coming next?
- What am I behind on?
- What is likely to matter on the exam?
- What have I studied but not retained?
- Which prerequisite gap is causing difficulty?

Do not pretend to know instructor intent when evidence is absent.

# 7. Complete Learner Journey

Create a coherent journey through the application.

The experience should flow naturally through:

**Home → Course → Topic → Learn → Practice → Assess → Review → Retain → Return**

The learner should rarely feel stranded in a dead-end screen.

## Home

Surface things that matter now.

Possible areas:

- Continue learning
- Due for review
- Upcoming course work
- Recent courses
- Current streak
- Weak topics
- Recently imported material
- Recommended next task
- Upcoming exam
- Incomplete lessons
- Quick create/import
- Search

Avoid a dashboard full of meaningless statistics.

## Course Home

A course should clearly communicate:

- structure,
- progress,
- current position,
- next recommended action,
- instructor pacing,
- prerequisites,
- review status,
- assessments,
- and source materials.

## Topic/Lesson Workspace

A learner should be able to:

- read,
- understand,
- annotate,
- inspect terminology,
- view examples,
- interact with diagrams,
- run code,
- take notes,
- ask focused questions,
- practice,
- and move into assessment

without constantly changing mental context.

# 8. Reading and Source-Grounded Learning

Make reading a first-class learning mode.

Support:

- comfortable long-form reading,
- original document viewing,
- extracted structured text,
- headings,
- page references,
- citations,
- highlighting,
- annotations,
- learner notes,
- bookmarks,
- contextual definitions,
- symbol explanations,
- formula explanations,
- cross-references,
- and links to related course concepts.

A learner should be able to select something and ask:

- What does this term mean?
- What does this symbol represent?
- Why is this step valid?
- Show me an example.
- Explain this in simpler language.
- Connect this to what I learned earlier.
- What should I remember from this section?

Generated explanations should remain tied to the relevant source passage whenever possible.

# 9. Notes and Knowledge Workspace

Allow learners to build durable notes rather than transient chat responses.

Support:

- freeform notes,
- structured notes,
- notes attached to passages,
- notes attached to concepts,
- notes attached to lessons,
- mathematical notation,
- code blocks,
- diagrams,
- links,
- references,
- embedded questions,
- flashcards created from notes,
- and backlinks where useful.

A learner should be able to refine notes over time.

Generated notes must remain editable.

Do not overwrite learner-authored work without explicit intent.

# 10. Interactive Lessons

Create interactive lessons when interaction meaningfully improves understanding.

A lesson may combine:

- explanation,
- question,
- manipulation,
- prediction,
- diagram,
- graph,
- worked example,
- mini-simulation,
- learner input,
- feedback,
- and reflection.

Avoid presenting 20 screens of generated prose with a “Continue” button.

Interactions should require thinking.

Examples:

- predict an output before executing code,
- manipulate a graph,
- order historical events,
- label a biological structure,
- complete a mathematical derivation,
- identify the incorrect reasoning step,
- modify parameters in a simulation,
- categorize examples,
- construct a causal chain,
- or repair a flawed solution.

# 11. Flashcards and Rapid Study

Include a complete flashcard system suitable for serious study.

Users should be able to:

- create decks manually,
- generate cards from source material,
- create cards from highlights,
- create cards from notes,
- edit generated cards,
- merge duplicates,
- move cards between collections,
- tag cards,
- star cards,
- and study subsets.

Each card may support:

- prompt,
- answer,
- explanation,
- source citation,
- image,
- formula,
- code,
- notes,
- tags,
- difficulty,
- mastery state,
- review history,
- and optional alternate answers.

Flashcard mode should support:

- flip interaction,
- previous/next,
- shuffle,
- term-first or answer-first,
- keyboard controls,
- known/learning marking,
- starred-only study,
- difficult-only study,
- session progress,
- and restart.

Creating and editing large decks should remain fast.

# 12. Adaptive Learning and Retention

Build meaningful adaptive learning rather than simply randomizing questions.

Track appropriate per-item state such as:

- attempts,
- correct responses,
- incorrect responses,
- recent performance,
- response latency where useful,
- confidence if collected,
- mastery,
- difficulty,
- last reviewed,
- next review,
- and prerequisite relationships.

Use a sensible spaced-repetition or memory scheduling approach.

Do not pretend the algorithm is scientifically precise beyond what the data supports.

Provide a clear **Review Due** workflow.

Review should prioritize:

1. material due for retention,
2. repeated weaknesses,
3. prerequisite gaps,
4. recent mistakes,
5. newly learned material,
6. material likely to matter soon.

Avoid making “mastered” a permanent binary label.

# 13. Practice System

Practice should be one of It embank's strongest features.

Practice may be:

- targeted,
- adaptive,
- mixed,
- exam-style,
- timed,
- mastery-based,
- prerequisite-focused,
- or learner-configured.

Support practice from:

- a single concept,
- a lesson,
- a unit,
- a course,
- selected sources,
- weak areas,
- starred material,
- instructor-defined objectives,
- or everything studied so far.

Questions should test actual knowledge rather than superficial wording recognition.

# 14. Rich Question and Response Types

Use question formats appropriate to the subject.

Support formats such as:

- multiple choice,
- multiple select,
- true/false where pedagogically appropriate,
- short typed response,
- long written response,
- fill-in-the-blank,
- cloze,
- numerical response,
- units-aware numerical response,
- LaTeX/math input,
- ordering,
- matching,
- categorization,
- table completion,
- matrix response,
- timeline ordering,
- diagram labeling,
- hotspot selection,
- drag-and-drop,
- graph interpretation,
- graph construction,
- code prediction,
- code tracing,
- code repair,
- executable code,
- data interpretation,
- proof step ordering,
- equation completion,
- source analysis,
- argument construction,
- and worked problem solving.

Do not use multiple choice when the learning objective requires production.

# 15. Practice Feedback

Feedback should support another attempt.

After a response, explain:

- what was correct,
- what was incorrect,
- why,
- which reasoning step failed,
- what misconception may be involved,
- and what to reconsider.

When appropriate, provide hints progressively rather than immediately revealing the solution.

A useful retry loop is:

**attempt → feedback → reconsider → retry → explanation**

not:

**attempt → wrong → show answer**

For worked problems, feedback should target the learner's process where possible.

# 16. Assessment

Assessment should be distinct from ordinary practice.

Support:

- quizzes,
- unit tests,
- cumulative exams,
- custom tests,
- diagnostic tests,
- practice exams,
- and instructor-aligned assessments.

Allow configuration of:

- concepts,
- source ranges,
- number of questions,
- question formats,
- difficulty,
- time limit,
- randomization,
- attempt rules,
- and feedback timing.

After completion, provide meaningful review.

Show:

- overall result,
- performance by objective,
- strong areas,
- weak areas,
- missed concepts,
- relevant source material,
- and suggested review.

Allow learners to generate or begin a targeted follow-up session from mistakes.

# 17. Runtime Authority and Scoring Integrity

Keep scoring, answer validation, attempt state, timing, disclosure rules, and assessment progression under runtime authority.

Do not let generated prose decide whether an answer is correct.

Where deterministic grading is possible, use deterministic logic.

Examples:

- multiple choice,
- ordering,
- matching,
- numerical tolerance,
- structured tables,
- exact code output,
- unit-aware answers,
- graph properties,
- known mathematical forms.

For open-ended responses:

- separate rubric,
- learner response,
- machine evaluation,
- confidence,
- and final accepted result.

AI-generated grading prose should be treated as reviewable interpretation rather than unquestionable truth.

# 18. Test Mode

Support a fast test-generation workflow similar to mature flashcard products.

Users should be able to choose:

- number of questions,
- topics,
- difficulty,
- question types,
- source ranges,
- and whether to include prior mistakes.

After submission, display:

- score,
- correct answers,
- incorrect answers,
- learner answers,
- expected answers,
- explanations,
- and concept-level performance.

Provide an immediate **Practice Missed Questions** action.

# 19. Matching and Lightweight Study Games

Provide lightweight study interactions when they actually improve practice.

For example, a matching mode may include:

- randomized terms and definitions,
- timed completion,
- pair removal,
- personal best,
- restart,
- and keyboard/touch support.

Do not build games merely for engagement metrics.

# 20. Subject-Specific Workspaces

Different subjects should be allowed to feel different.

Do not solve subject specialization by merely changing icon colors.

Explore genuinely different compositions.

Examples:

## Mathematics

Possible tools:

- equation rendering,
- symbolic steps,
- scratch work,
- graphs,
- manipulable variables,
- worked derivations,
- proof sequencing,
- calculators where appropriate,
- and step-aware feedback.

## Programming

Possible tools:

- editor,
- console,
- code execution,
- tests,
- tracing views,
- state visualization,
- prediction tasks,
- debugging tasks,
- and notebook cells.

## History / Politics / Humanities

Possible tools:

- timelines,
- source comparison,
- primary documents,
- claim/evidence mapping,
- maps,
- concept comparison,
- essay planning,
- and argument practice.

## Sciences

Possible tools:

- diagrams,
- labeling,
- simulations,
- tables,
- units,
- formula work,
- graph interpretation,
- experimental reasoning,
- and process visualization.

## Languages

Possible tools:

- vocabulary,
- contextual sentences,
- recognition,
- production,
- listening where available,
- grammar transformations,
- and spaced repetition.

Subject workspaces should share a coherent application shell while permitting meaningful specialization.

# 21. Diagrams, Visuals, and Simulations

Support learner-useful visual material.

Examples:

- annotated diagrams,
- timelines,
- concept maps,
- flowcharts,
- graphs,
- geometric constructions,
- process diagrams,
- system models,
- and simulations.

Generated visuals should remain editable or regenerable where practical.

Do not turn every concept into a decorative diagram.

# 22. Executable Notebooks and Computation

Where appropriate, support notebook-style learning.

Possible cells:

- Markdown,
- math,
- executable code,
- output,
- visualization,
- question,
- reflection,
- and dataset preview.

Use notebooks for subjects where exploration and execution improve learning.

Examples:

- programming,
- statistics,
- economics,
- physics,
- mathematics,
- data science.

Preserve notebook state safely and make recovery possible.

# 23. AI Assistance

AI should support:

- document intake,
- source classification,
- syllabus interpretation,
- curriculum planning,
- prerequisite detection,
- lesson authoring,
- question generation,
- feedback generation,
- explanation,
- tutoring,
- note transformation,
- flashcard creation,
- concept linking,
- review planning,
- and evidence-informed next-step recommendations.

Support multiple AI execution paths where practical:

- local models,
- user-supplied APIs,
- remote providers,
- external agent tools,
- and deterministic local logic.

Avoid coupling the architecture to one provider.

AI should not be required for basic reading, studying, reviewing, or using existing generated material.

# 24. AI Tutor Behavior

Tutoring should be contextual rather than chatbot-first.

The tutor should know, when available:

- current course,
- current lesson,
- current source,
- selected passage,
- learner history,
- recent mistakes,
- prerequisites,
- notes,
- and current objective.

Useful actions include:

- explain,
- simplify,
- give another example,
- ask me a question,
- give a hint,
- compare concepts,
- trace the prerequisite,
- show where this appears in the source,
- create practice,
- add to notes,
- and save as a flashcard.

Do not make the learner repeatedly restate context the app already knows.

Useful AI output should be savable into the actual course or workspace.

# 25. Search and Retrieval

Provide strong search across the entire learning workspace.

Search:

- courses,
- documents,
- titles,
- headings,
- passages,
- notes,
- definitions,
- flashcards,
- questions,
- explanations,
- annotations,
- tags,
- and generated material.

Search results should make it clear:

- what matched,
- where it came from,
- which course it belongs to,
- and whether it is source material or generated content.

Support fast navigation from result to context.

# 26. Progress

Track meaningful progress rather than merely counting clicks.

Possible signals include:

- source material completed,
- objectives introduced,
- objectives practiced,
- objectives demonstrated,
- retention state,
- review due,
- assessment performance,
- prerequisite weakness,
- and course pacing.

Distinguish:

- viewed,
- studied,
- practiced,
- demonstrated,
- retained.

Avoid misleading completion percentages.

# 27. Analytics

Provide analytics that help the learner make decisions.

Useful course-level information may include:

- current progress,
- weak concepts,
- retention status,
- accuracy,
- practice volume,
- recent activity,
- upcoming work,
- assessment results,
- and review load.

Useful global information may include:

- study streak,
- time studied,
- cards/questions reviewed,
- due material,
- upcoming assessments,
- recent courses,
- and long-term retention trends.

Charts should communicate useful information, not decorate the dashboard.

# 28. Study Session Results

At the end of a meaningful study session, summarize:

- what was covered,
- questions attempted,
- accuracy,
- concepts improved,
- concepts still weak,
- material newly introduced,
- material due later,
- and relevant next actions.

Allow the learner to:

- review mistakes,
- continue,
- practice weaknesses,
- save notes,
- schedule review,
- or return to the course.

# 29. Organization

Support structures such as:

- courses,
- nested courses,
- units,
- folders,
- collections,
- tags,
- saved views,
- favorites,
- archived material,
- and source libraries.

Avoid requiring learners to manually organize everything before the app is useful.

Use inferred relationships where helpful, but keep them editable.

# 30. Themes and Interface Adaptability

Make the application visually distinctive and enjoyable.

Do not settle for one generic SaaS dashboard.

Explore genuinely different interface compositions where they improve the work.

Support:

- adaptable themes,
- readable typography,
- strong information hierarchy,
- excellent dark mode,
- subject-appropriate layouts,
- responsive desktop/tablet/mobile behavior,
- reduced motion,
- and accessibility.

Themes should be capable of changing more than colors.

They may influence:

- typography,
- density,
- card treatments,
- workspace layout,
- navigation emphasis,
- diagram treatment,
- reading width,
- and interaction presentation,

while preserving usability.

Keep visual decisions revisable.

# 31. Interaction Quality

Prioritize visible, tactile improvements.

Examples:

- immediate saving,
- smooth navigation,
- strong hover/focus states,
- subtle transitions,
- clear state changes,
- useful keyboard shortcuts,
- drag-and-drop where appropriate,
- undo,
- autosave,
- optimistic interactions where safe,
- and sensible loading behavior.

Do not measure progress primarily by test count or number of components created.

A smaller number of complete learner workflows is more valuable than many incomplete screens.

# 32. Keyboard and Accessibility

Support serious keyboard use.

Examples:

- arrow navigation,
- Space to flip cards,
- Enter to submit,
- number keys for answers,
- command palette,
- quick search,
- focus shortcuts,
- and context-aware navigation.

Ensure:

- visible focus,
- semantic controls,
- screen-reader support,
- strong contrast,
- touch accessibility,
- reduced motion,
- and usable text sizing.

# 33. Local-First Data Architecture

The application should remain useful without paid infrastructure.

At minimum, persist:

- courses,
- source metadata,
- source relationships,
- learner notes,
- annotations,
- flashcards,
- questions,
- generated lessons,
- progress,
- mastery,
- spaced-repetition state,
- assessments,
- study history,
- preferences,
- and AI provenance.

Prefer a local-first architecture.

Where cloud functionality exists, it should enhance rather than define basic ownership.

# 34. Readable and Portable Data

Avoid trapping the learner's work in an opaque database.

Where practical, support readable formats such as:

- Markdown,
- JSON,
- CSV,
- notebooks,
- plain text,
- common document formats,
- or a documented structured format.

Provide:

- export,
- backup,
- restore,
- and migration paths.

Make it possible to understand the learner's own data outside the app.

# 35. Obsidian and External Knowledge Bases

Treat Obsidian and external folders as meaningful knowledge sources.

Support workflows such as:

- indexing an Obsidian vault,
- recognizing links,
- preserving Markdown,
- linking It embank concepts back to notes,
- importing selected notes,
- and writing compatible output when appropriate.

Do not silently modify external knowledge bases.

Keep read, import, sync, and write-back behaviors explicit.

# 36. Provenance and Citations

Generated educational content should preserve evidence.

Where applicable, attach:

- source document,
- page,
- section,
- excerpt reference,
- note source,
- and generation metadata.

A learner should be able to inspect the evidence supporting an explanation or generated question.

Do not manufacture citations.

If source support is weak, indicate uncertainty.

# 37. Authoring

Allow learners to become authors.

They should be able to create or edit:

- courses,
- lessons,
- questions,
- explanations,
- flashcards,
- diagrams,
- assessments,
- and learning sequences.

AI should accelerate authoring rather than make authored content untouchable.

Generated material should enter editable authoring workflows.

# 38. Content Status and Review

Distinguish clearly between states such as:

- imported,
- generated,
- edited,
- reviewed,
- accepted,
- experimental,
- prototype,
- deprecated,
- and deferred.

Do not present prototype behavior as finished.

When AI creates prose used in consequential learning material, support human review.

# 39. Research and Selective Adoption

Research relevant products and educational tools when doing so can improve the application.

Study useful ideas from:

- Brilliant,
- Albert,
- Anki,
- Quizlet,
- notebook-style research tools,
- LMS products,
- interactive textbooks,
- coding education tools,
- digital notebooks,
- knowledge-management systems,
- and assessment platforms.

Evaluate specific capabilities rather than copying products wholesale.

Useful ideas may be adopted as:

- core functionality,
- optional functionality,
- experimental prototypes,
- future work,
- or rejected approaches.

Document the reasoning when an architectural decision materially affects future work.

Revisit earlier decisions when better evidence appears.

# 40. Feature Preservation

When discovering useful ideas during development, do not discard them merely because they do not fit the current sprint.

Classify them as:

- implement now,
- core later,
- optional,
- prototype,
- research further,
- or defer.

Preserve enough context that good ideas can be revisited.

Do not let the roadmap become an excuse for half-implementing everything.

# 41. Engineering Quality

Treat It embank as a real application.

The codebase should have:

- coherent architecture,
- reusable components,
- clear domain models,
- sensible state management,
- strong typing,
- input validation,
- migration strategy,
- graceful error handling,
- recovery,
- useful logging,
- modular AI provider interfaces,
- testable scoring logic,
- and clear boundaries between deterministic and generative behavior.

Avoid:

- giant components,
- hidden coupling,
- placeholder buttons,
- mock functionality masquerading as complete functionality,
- dead routes,
- fake analytics,
- and generated screens with no persistent data path.

# 42. Modularity

Design the system so capabilities can evolve independently.

Likely modules include:

- source ingestion,
- library,
- course model,
- learning content,
- notes,
- flashcards,
- practice,
- assessment,
- grading,
- retention,
- analytics,
- search,
- AI,
- notebooks,
- diagrams,
- and import/export.

Do not require rewriting the application to add a new subject-specific activity.

# 43. Performance

The application should remain pleasant with realistically large personal libraries.

Design for:

- many courses,
- thousands of notes,
- large PDFs,
- many thousands of flashcards/questions,
- long study histories,
- and substantial generated content.

Use indexing, pagination, virtualization, caching, or background processing where appropriate.

Do not make basic navigation dependent on expensive AI calls.

# 44. Reliability and Recovery

Local-first does not mean fragile.

Protect against:

- interrupted imports,
- malformed source files,
- partial generations,
- schema upgrades,
- accidental deletion,
- crashes,
- corrupted study state,
- and failed AI calls.

Provide reasonable:

- autosave,
- undo,
- retry,
- versioning where valuable,
- backups,
- and recovery.

# 45. Example Content

Include enough original demonstration content to make every major mode testable.

Use several substantially different subjects, for example:

- mathematics,
- biology,
- history/political science,
- programming,
- and vocabulary/language.

The samples should demonstrate subject-specific differences rather than five copies of the same generic lesson template.

Make sample content easy to remove.

# 46. Development Method

Before implementing substantial new work:

1. Inspect the existing repository.
2. Understand the current architecture.
3. Read existing plans and design decisions.
4. Search for related unfinished work.
5. Search existing It embank content.
6. Inspect connected external folders when available.
7. Inspect relevant Obsidian material when available.
8. Identify what can be reused.
9. Identify architectural constraints.
10. Identify incomplete learner journeys.
11. Determine the highest-value observable improvements.

Then build vertically.

Prefer completing one real learning loop:

**source → lesson → practice → feedback → progress → review**

over implementing isolated pieces of ten different systems.

# 47. Prioritization

Prioritize, roughly in this order:

1. Complete learner workflows
2. Source-grounded content
3. Persistent generated work
4. Reading and understanding
5. High-quality practice
6. Correct scoring and runtime behavior
7. Retention and review
8. Course organization
9. Search and navigation
10. Subject-specific interactions
11. Authoring
12. Analytics
13. AI convenience
14. Cosmetic expansion

When choosing between a visible, useful learner improvement and additional internal test-count progress, prefer the learner improvement unless correctness would materially suffer.

# 48. Implementation vs. Prototype

Be explicit about what is:

- implemented,
- partially implemented,
- mocked,
- experimental,
- planned,
- or blocked.

Do not describe a rendered prototype as functioning software.

Do not count a component as complete if the learner cannot complete the intended task.

# 49. Correctness Checks

Before considering a workflow complete, verify the important paths.

At minimum test:

1. Import source material.
2. Preserve the original source.
3. Create or map a course.
4. Open the course again later.
5. Read source-linked material.
6. Create a note.
7. Highlight source material.
8. Generate and save useful AI material.
9. Edit that generated material.
10. Create or generate flashcards.
11. Complete a flashcard session.
12. Complete adaptive practice.
13. Receive useful feedback.
14. Take an assessment.
15. Verify scoring.
16. Review missed material.
17. Schedule or encounter spaced review.
18. Preserve progress across restarts.
19. Search for prior material.
20. Export learner-owned data.
21. Restore or re-import that data.
22. Handle a failed generation gracefully.
23. Use core functionality with keyboard navigation.
24. Use major workflows on a smaller screen.

Fix important failures instead of merely listing them.

# 50. Observable Product Quality

A feature should not be considered finished merely because its backend exists.

Check whether the learner can see and use the improvement.

Ask:

- Is the next action obvious?
- Does the generated artifact appear where expected?
- Can the learner revise it?
- Is its source visible?
- Does it affect progress appropriately?
- Can it be found later?
- Does navigation return the learner to a sensible place?
- Does feedback help another attempt?
- Does the feature work with real course material?
- Does it feel integrated with the rest of the product?

# 51. Definition of Done

The application should eventually be good enough that a learner can realistically use It embank as their primary personal learning workspace.

A learner should be able to:

- bring in an actual syllabus,
- import real course materials,
- connect prior notes,
- find relevant existing work,
- organize material into a useful course,
- understand what to study next,
- read original sources,
- get contextual explanations,
- take meaningful notes,
- study interactively,
- complete worked examples,
- use diagrams or notebooks where appropriate,
- practice with subject-appropriate questions,
- receive useful feedback,
- take real assessments,
- review mistakes,
- retain material with spaced repetition,
- see meaningful progress,
- search everything,
- return weeks later,
- understand where generated material came from,
- revise AI-created content,
- and export their learning data without losing ownership.

The application should feel coherent from beginning to end.

# 52. Final Product Standard

Do not optimize for the number of features, files, tests, routes, generated screens, or AI calls.

Optimize for the number of **complete, high-quality learner tasks** that work from beginning to end.

Prefer:

**fewer deep systems over many shallow systems,**

**reusable learning primitives over one-off demos,**

**evidence over assumptions,**

**persistent artifacts over transient AI output,**

**subject-appropriate interaction over generic templates,**

**learner ownership over platform lock-in,**

and

**working product behavior over impressive-looking prototypes.**

The final product should feel like a personal learning environment that can grow with the learner for years, not simply an AI study generator.