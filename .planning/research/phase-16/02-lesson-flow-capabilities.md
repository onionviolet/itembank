# Research stream 02: Lesson flow and semantic teaching capabilities

**Research date:** 2026-08-13

**Access date for external sources:** 2026-08-13
**Scope:** research only. This document does not change a product contract.

## 1. Scope and research questions

This stream asks which lesson flows and semantic teaching capabilities improve
learning across EMT or health, mathematics, computer science, and
knowledge-heavy courses. It covers definitions, cited images, callouts, worked
examples, comparisons, diagrams, simulations, prediction, inline checks,
staged reveal, transfer, and resume behavior.

The research questions are:

1. Which capabilities serve a defensible teaching purpose, rather than visual
   novelty?
2. Where does subject matter change the useful sequence or representation?
3. How can each capability remain meaningful in a plain, portable lesson file?
4. What keyboard, touch, screen-reader, narrow-screen, and reduced-connectivity
   behavior is required?
5. What can an author or agent specify reliably, and what needs linting,
   review, or a shared renderer primitive?
6. What learner evidence is useful, and which interactions should remain
   unscored or unrecorded?

### Method and evidence limits

Current primary sources were preferred for standards, official subject
requirements, and product or platform behavior. Government practice guides
and meta-analyses synthesize broader learning evidence. Some cited research is
older because the underlying question is stable and the source remains an
authoritative synthesis. Product popularity is not treated as evidence of
learning effectiveness.

No protected lesson content, visual asset, or proprietary interaction was
copied. Cross-subject recommendations below are inferences from convergent
evidence, not claims that one flow has been experimentally compared across all
four subject families.

## 2. Sources

All external sources were accessed 2026-08-13.

| Source | Type | What it supports and limitation |
|---|---|---|
| [IES, Organizing Instruction and Study to Improve Student Learning](https://ies.ed.gov/ncee/wwc/practiceguide/1) | US government evidence practice guide, released 2007 | Moderate evidence for interleaving worked examples with problem solving, combining graphics with verbal descriptions, and connecting abstract and concrete representations; strong evidence for quiz re-exposure. Broad and durable, but not a modern UI evaluation. |
| [IES, Improving Mathematical Problem Solving in Grades 4 Through 8](https://ies.ed.gov/ncee/WWC/PracticeGuide/16/Published) | US government evidence practice guide, revised 2018 | Strong evidence for teaching visual representations and reflection, moderate evidence for multiple strategies. Population is grades 4 through 8, so adult transfer is an inference. |
| [IES, Improving Adolescent Literacy](https://ies.ed.gov/ncee/wwc/PracticeGuide/8/WhatWeDo) | US government evidence practice guide, released 2008 | Strong evidence for explicit vocabulary and comprehension strategy instruction. The guide supports deliberate definitions, not automatic glossing of every difficult word. |
| [CAST Universal Design for Learning Guidelines 3.0](https://udlguidelines.cast.org/) and [multiple media consideration](https://udlguidelines.cast.org/representation/language-symbols/multiple-media/) | Current institutional design guidance, 2024 | Multiple representations, accessible tools, graduated support, transfer, and monitoring. UDL is a design framework, not proof that every listed option improves every outcome. |
| [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Web standard, W3C Recommendation | Keyboard and pointer equivalence, focus, status messages, target size, and alternatives to dragging. It specifies access, not pedagogy. |
| [W3C Images Tutorial](https://www.w3.org/WAI/tutorials/images/) and [Complex Images](https://www.w3.org/WAI/tutorials/images/complex/) | Current W3C implementation guidance, updated 2026 | Purpose-sensitive short alternatives, structured long descriptions, and text or table equivalents for diagrams and charts. |
| [W3C Content on Hover or Focus](https://www.w3.org/WAI/WCAG21/Understanding/content-on-hover-or-focus.html) and [Tooltip Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) | Current accessibility guidance and a work-in-progress APG pattern | Hover or focus content must be dismissible, hoverable, and persistent. APG explicitly says its tooltip pattern lacks task-force consensus, so native disclosure or visible definitions are safer than a custom tooltip dependency. |
| [Creative Commons recommended attribution practices](https://wiki.creativecommons.org/index.php?title=Recommended_practices_for_attribution) | Rights-holder guidance | Retain title, author, source, and license, and identify modifications. It does not determine whether a particular work is pedagogically suitable. |
| [National EMS Education Standards](https://www.ems.gov/assets/EMS_Education_Standards_2021_Updated2_24_25forEO.pdf) | Current US federal EMS standard, 2021 edition updated 2025 | EMT education includes decisions from assessment findings, evaluating intervention effectiveness, documentation, safety, and team behavior. This supports scenario and changed-state practice, not treatment advice generated outside an approved source. |
| [AHRQ, Simulation to Improve Patient Safety](https://psnet.ahrq.gov/issue/simulation-improve-patient-safety-getting-started) and [Debriefing for Clinical Learning](https://psnet.ahrq.gov/primer/debriefing-clinical-learning) | US government issue brief and primer, 2024 and 2021 | Simulation plus structured debrief supports practice without direct patient harm and reflection on actions and thought processes. Evidence is strongest for facilitated health simulation, so a self-guided screen simulation needs additional validation. |
| [PhET About and design principles](https://phet.colorado.edu/en/about) and [PhET research](https://phet.colorado.edu/en/research) | University project primary documentation | Useful simulations make causal effects visible, coordinate multiple representations, give immediate feedback, and constrain controls to guide exploration. PhET reports four to six think-aloud interviews per simulation, which supports iterative usability research but is not alone an efficacy trial. |
| [Adams et al., simulation interface research](https://phet.colorado.edu/publications/archive/Phet%20Interview%20Paper.htm) | Original design research based on more than 200 interviews | Irrelevant information, too much novelty, and poor representations can impede discovery. The work is physics-centered and older, but the interaction risks are still relevant. |
| [Roediger and Butler, retrieval practice review](https://pubmed.ncbi.nlm.nih.gov/20951630/) | Peer-reviewed research review, 2011 | Retrieval improves long-term retention, feedback usually strengthens the effect, and transfer can occur. It also warns that tests can teach errors, which makes corrective feedback important. |
| [Sentance et al., PRIMM](https://primmportal.com/wp-content/uploads/2020/10/teaching-computer-programming-with-primm-a-sociocultural-perspective.pdf) and [Raspberry Pi educator module](https://training-hub.raspberrypi.org/en/courses/using-primm-to-teach-programming) | Peer-reviewed CS pedagogy paper and current institutional implementation guidance | Predict, Run, Investigate, Modify, Make moves from program comprehension toward creation. Evidence does not justify forcing this exact sequence onto non-code material. |
| [Richter, Scheiter, and Eitel, signaling text-picture relations](https://doi.org/10.1016/j.edurev.2015.12.003) | Meta-analysis, 27 studies and 45 comparisons | Small-to-medium benefit from signaling relations between text and pictures, especially for learners with low prior knowledge. Signals can still become noise if overused. |
| [Sundararajan and Adesope, Keep It Coherent](https://eric.ed.gov/?id=EJ1263249) | Meta-analysis record, 2020 | Interesting but irrelevant details can hinder learning, with moderators and mixed magnitude. This is a reason to require a teaching role for tips, pictures, and animation. |
| [1EdTech Caliper Analytics](https://www.1edtech.org/standards/caliper) | Current learning-event standard documentation | Distinguishes reading, assessment, feedback, session, and tool-use events. It demonstrates a vocabulary, not a requirement to export or collect those events. itembank's on-disk evidence boundary remains controlling. |

## 3. Existing itembank research reviewed

The inventory focused on files that directly address lesson display, learning
flow, subject fit, or capability semantics.

| Existing file | Still-valid finding reused here | Stale, weak, or superseded claim |
|---|---|---|
| `.planning/research/2026-08-09-lesson-display-editor.md` | Continuous prose needs real headings, constrained measure, wide escape for figures, semantic captions, readable math fallback, and a plain anchor-list floor. | Its cross-product "2026 consensus" and several site observations are secondary or marked assumed. They remain design input, not current product evidence. |
| `.planning/research/2026-08-09-differentiators-d1-d2-d3.md` | A term needs a durable glossary entry; hover is only enhancement; callout kinds need semantic roles; lesson style rules need deterministic lint where possible. | Browser-specific popover statements dated 2026-08-09 require implementation-time verification. Earlier review and evidence schemas are proposals, not accepted Phase 16 facts. |
| `.planning/research/2026-08-09-extraction-subjects-bilingual.md` | EMT benefits from staged cases, mathematics from symbolic plus visual representation, CS from runnable code, and language metadata belongs with glossary entries. | Subject conclusions were partly based on product and training observations. This stream rechecks the major recommendations against EMS.gov, IES, AHRQ, and PRIMM sources. |
| `.planning/research/2026-08-09-landscape-widening.md` | A small shared interaction vocabulary is more portable and authorable than bespoke widgets; medical rationales and code-pattern practice expose domain-specific needs. | The file explicitly labels several products and behaviors assumed. Those claims should not enter Phase 16 without fresh primary verification. |
| `.planning/research/2026-08-10-lesson-style-catalogue.md` | Useful styles are compositions of semantic capabilities. Predict-first is conditional, worked-example then variation is strong for procedures, PRIMM is domain-specific, case narratives need progressive disclosure, and arbitrary lesson-authored executable code is unsuitable. | Its Brilliant description has medium confidence and acknowledges no public authoring or pedagogy document. Claims about exact competitor behavior are historical inputs only. Its statement that exactly one new block is missing predates the source-to-course reframe and is not assumed here. |
| `.planning/research/2026-08-10-ui-inspiration-missing-surfaces.md` | Definitions need focus and touch paths; a plain glossary is the floor; worked steps should remain one semantic ordered list; shared declarative components are preferable to author code; staged cases should append linearly and retain earlier information. | Browser support, print-engine behavior, and competitor observations were time-sensitive. Print is also not a binding product requirement under current directives, though a portable static representation still is. |
| `.planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md` | Style selection should express genre fit, separate deterministic lint from semantic review, and avoid a second scoring authority. | This was a research brief for the prior bank-centered milestone. Its phase assignments and "binding" verdicts do not override the 2026-08-13 source-to-course contract. |
| `.planning/UI-SPEC.md` | Existing accessibility gates, runtime-controlled disclosure, no key in hidden DOM, raw math fallback, and equivalent semantic controls remain constraints. | The specification predates Phase 16's complete lesson-capability contract. Its detailed visual direction is not evidence that a capability teaches well. |

**Observed fact:** prior research already converges on portable semantics plus
progressive enhancement. It also contains clearly labeled assumptions and
dated browser or competitor observations.

**Inference:** Phase 16 should preserve the convergence while reopening claims
about exact product behavior, browser support, print behavior, phase ownership,
and how many grammar additions are required.

**Recommendation:** cite prior files as the design history. Use current primary
sources for standards and product behavior, and make implementation verify any
browser-dependent interaction rather than inheriting a dated claim.

## 4. Observed facts, inferences, and recommendations

### 4.1 Observed facts

1. Evidence guides support alternating worked solutions and learner problem
   solving, active retrieval with feedback, visual plus verbal explanation,
   and connections between concrete and abstract representations.
2. Mathematics guidance supports teaching learners how to select and use a
   visual representation, not merely showing a decorative diagram.
3. EMS standards require assessment-linked decisions, reevaluation, safety,
   documentation, and team behavior. A static fact summary cannot exercise all
   of those objectives.
4. Health simulation guidance treats debrief as central to reflecting on what
   happened, why, and how future action should change.
5. PRIMM begins with existing code and moves from prediction and observation to
   modification and independent creation.
6. Accessible images need purpose-sensitive alternatives. Complex diagrams
   generally need both a short identification and a structured long
   description or equivalent representation.
7. Hover-only definitions are inaccessible. Content triggered by hover or
   focus must be dismissible, hoverable, and persistent, while touch needs an
   explicit activation path.
8. Simulation quality depends on constrained, meaningful controls and on
   making causal relations visible. Interactivity by itself is not evidence of
   learning value.
9. Interesting but irrelevant detail can hinder retention or transfer.
10. Standards can distinguish reading, session, feedback, and assessment
    events. That does not imply that every interaction should be evidence.

### 4.2 Inferences

1. A cross-subject lesson loop can share stable moments while allowing some to
   be absent: orient, activate or predict, encounter an explanation or source,
   observe a worked or dynamic representation, check understanding, receive
   feedback, apply in a changed context, summarize, and resume or continue.
2. The semantic role is more durable than its visual treatment. "Warning",
   "misconception", "worked example", and "prediction" can survive plain
   Markdown, while "blue card" or "animated panel" cannot.
3. Prediction is valuable when the learner has enough prior structure to make
   a reasoned commitment and will soon receive corrective observation. It is
   misuse when it solicits blind guesses about arbitrary facts or clinical
   protocol.
4. Resume should restore the learner to a meaningful semantic checkpoint, not
   merely a pixel scroll offset. Scroll position can be a convenience layered
   on section, stage, activity, attempt, and disclosure state.
5. Low-stakes learning evidence should distinguish exposure, attempt,
   feedback, and later transfer. A click, hover, reveal, or time-on-page is not
   mastery.

### 4.3 Recommendations

Adopt a continuous reader and a guided lesson presentation over the same
authored structure. Guided mode may pace or enhance semantic blocks, but it
must not become the only complete copy. Treat direct source reading as a valid
lesson treatment, with orientation, optional definitions, and checks around it
rather than rewriting it automatically.

Use the default logical flow below, with subject-specific substitutions:

1. **Orient:** objective, prerequisite, relevance, source, estimated scope, and
   what the learner will do.
2. **Activate:** recall a prerequisite or make a reasoned prediction. Offer
   "not enough information" or "I do not know" where appropriate.
3. **Encounter:** read the source or concise explanation, with definitions and
   only teaching-relevant callouts or images.
4. **Model or observe:** inspect a worked example, comparison, diagram, code
   execution, or constrained simulation.
5. **Explain:** connect action, representation, and principle. In health or
   simulation contexts, debrief the decision and its consequences.
6. **Check:** retrieve, explain, diagnose, or perform a small application with
   prompt corrective feedback when disclosure policy permits.
7. **Transfer:** apply the principle in a changed surface context, changed
   values, new code, or changed patient presentation.
8. **Close and continue:** state what changed in the learner's model, expose
   sources, record only authorized evidence, and offer the next course action.

Subject profiles should alter the middle of the loop:

| Subject | Preferred capability sequence | Important caution |
|---|---|---|
| EMT or health | scene orientation, information-limited decision, staged findings, action, consequence, structured debrief, changed case | Do not reward unsafe guessing. Use approved and versioned clinical sources, surface scope and uncertainty, and never imply that a screen simulation certifies physical competence. |
| Mathematics | problem structure, selected representation, worked steps with annotations, compare methods, partial completion, independent variation, changed-context transfer | Do not let animation conceal the invariant or let a diagram substitute for symbolic reasoning. |
| Computer science | predict output, run, investigate or trace, explain, modify, debug, make a related artifact | Execute only in an explicit sandbox. Do not equate successful output with conceptual understanding, security, or code quality. |
| Knowledge-heavy | orient with an organizing question, source reading, selected definitions and schema, retrieval with feedback, comparison or explanation, spaced revisit, application | Avoid a glossary dump, disconnected trivia, and callouts that merely repeat highlighted sentences. |

## 5. Pattern inventory and capability contract candidates

The table gives the minimum portability, accessibility, authorability, and
evidence implications for every recommended capability.

| Capability and teaching purpose | Benefits and applicability | Weaknesses and misuse risks | Portable and rich behavior | Accessibility requirements | Authorability and provenance | Evidence implications |
|---|---|---|---|---|---|---|
| **Definition**: remove a vocabulary barrier at point of need | Strong fit for health terminology, mathematical notation, CS vocabulary, and dense source reading | Over-glossing interrupts reading and can prevent contextual inference; a short definition may erase domain nuance | Plain file contains a glossary entry plus an explicit term reference. Rich UI may show a concise focus, click, or touch disclosure and link to the full entry | Never hover-only. Trigger is keyboard focusable and touch-sized; visible or appendix path always exists; language and pronunciation metadata are announced correctly | Author selects terms that are prerequisite or central, writes a context-specific definition, cites source-derived claims, and distinguishes synonym, abbreviation, and formal definition | Optional `term_opened` can show support use, not knowledge. Evidence comes from later use or retrieval, with denominator and context |
| **Cited image**: show appearance, spatial relation, evidence, or authentic context | Especially useful for anatomy, equipment, geometry, architecture diagrams, historical artifacts, or interfaces | Decorative stock images, copyright risk, outdated medical imagery, misleading crop, text embedded in pixels | Markdown contains local or stable asset reference, caption, purpose, short alternative, source record, license, and modification note. UI can zoom or annotate without replacing caption and prose | Purpose-sensitive alt; complex image gets a structured long description or equivalent table/text; zoom and annotations keyboard and touch operable; no color-only meaning | Author states why the image is needed, verifies rights and currency, records Title, Author, Source, License when applicable, checksum, crop or annotation changes, and claim locators | Image viewed or zoomed is exposure only. If interpretation matters, use a separate accessible noticing or application task |
| **Semantic callout**: signal a teaching role such as key principle, warning, misconception, or expert boundary | Helps scanning and can cue organization when roles are sparse and consistent | Card confetti, repeated prose, false authority, "expert tips" without evidence, or warnings used for ordinary facts | Plain block starts with a visible semantic label and coherent text. Rich UI may vary icon, tone, and placement but not meaning | Label is text, icon is redundant, reading order stays in flow, contrast is sufficient, and collapsed content is not required for core meaning | Closed role vocabulary; author must state the role-specific reason. Warnings and clinical tips need sources and currency; synthesis is labeled | No evidence from opening or reading. A later check may target the principle or misconception, but the callout itself is instruction |
| **Worked example**: expose a solution or decision process with reasons | Strong for mathematics, code tracing, procedural health reasoning, and structured analysis; supports novice scaffolding | Passive copying, unexplained steps, examples too similar to practice, or expert over-scaffolding | Ordered steps with result and per-step annotation remain readable in Markdown. UI may align steps with annotations, progressively focus steps, or allow completion of faded steps | Semantic ordered list or table with correct reading order; math and code retain source fallback; no relation conveyed solely by spatial alignment | Author names objective and prerequisites, explains why each non-obvious step is valid, identifies the generalizable step, cites protocol or formula sources, and creates a related but non-identical practice item | Viewing is not mastery. Record attempted completions or self-explanations separately; assess later independent variation and transfer |
| **Comparison or contrasting case**: make a discriminating feature visible | Useful for two math strategies, similar diagnoses, algorithms, concepts, sources, or historical claims | Superficial feature matching, unfair comparison, excessive columns, or giving away an assessment discriminator | Plain file uses a labeled table or paired headed sections followed by an explicit comparison claim. Rich UI may synchronize rows or highlight correspondences | Headers and row relationships programmatic; narrow screen becomes repeated labeled groups without changing order; color is supplementary | Author defines the comparison question and common dimensions, represents both sides fairly, cites each claim, and states the discriminator or tradeoff | Learner explanation or selection of a method can be evidence. Merely expanding the comparison is not |
| **Diagram**: externalize structure, process, dependency, or causal relation | Valuable for anatomy, flow of care, proofs, data structures, program state, timelines, and concept maps | "Spaghetti" maps, unlabeled arrows, decorative complexity, or relationships visible only spatially | Source contains a semantic node and relation list or an image plus structured description, caption, and takeaway. Rich UI can lay out, pan, focus, or step through the same model | Text equivalent preserves nodes, relations, direction, sequence, and critical grouping; keyboard traversal and non-drag controls; narrow view offers list or table | Author chooses a diagram only when relations matter, states the reading task, cites nodes and relations, and validates the static fallback | Pan, zoom, and focus are not learning. A noticing, reconstruction, or transfer response can be evidence through the runtime |
| **Simulation or runnable model**: reveal causal behavior through controlled action | Strong for parameter effects, code behavior, systems, and safe rehearsal; can make invisible state visible | Unguided play, misleading model boundaries, too many controls, unsafe clinical implication, inaccessible canvas, arbitrary author code | Plain file provides purpose, initial state, variable table, predicted relation, static snapshots or trace, limits, and reflection prompt. Rich UI instantiates a reviewed declarative component from those parameters | Every operation has keyboard and single-pointer alternative; state changes announced; no dragging-only path; reduced-motion and pause; equivalent table or trace; touch targets meet size guidance | Author selects from a closed component library, declares variables, ranges, units, invariant, expected observations, limits, and sources. No lesson-authored executable JavaScript | Record prediction, meaningful parameter changes, observation response, and transfer separately. Do not treat time or manipulation count as competence |
| **Prediction or commitment**: activate prior knowledge and make a later observation interpretable | Strong before code execution, a graph reveal, a familiar physical model, or an information-limited case decision | Blind guessing, test anxiety, teaching an error without feedback, or prediction after clues already reveal the result | Prompt and learner response remain explicit in plain form, followed by observation and explanation. Rich UI can hold the observation until commitment without hiding keyed content in DOM | Supports "I do not know" and keyboard/touch response; never depends on drag; feedback and state change announced | Author states the knowledge basis and reveal event, includes corrective explanation, marks whether skipping is allowed, and rejects arbitrary fact prediction | Prediction is low-stakes diagnostic evidence, not a score unless it is an authored assessment item under runtime authority. Confidence may be useful only with clear meaning |
| **Inline check**: retrieve or apply immediately enough to correct the learner's model | Useful after a coherent segment, not after every paragraph; feedback supports retention | Fragmented reading, trivial recognition, punitive gating, answer leakage, and accidental prose auto-grading | Plain lesson carries an explicit activity reference, purpose, and non-key prompt shell. Rich UI inserts the runtime-served public item and legal feedback | Native controls, clear instructions and errors, no keyed material in hidden DOM or accessible names, equivalent response for visual controls | Author links objective, learning purpose, cognitive demand, feedback rule, and source. Deterministic linter checks references; semantic review checks alignment | Attempts, hints, feedback, correctness, pending prose, and timing belong to the existing runtime. Opening or scrolling does not |
| **Staged reveal**: require revision as new information becomes available | Natural for evolving patients, debugging traces, proof discovery, historical evidence, and data interpretation | Artificial suspense, timed pressure, hiding necessary context, answer locking, later-stage key leakage, or model-chosen sequence | Ordered stages are authored in the source. Plain static form labels every stage and sequence. Guided mode serves only reached stages, appends them linearly, and retains prior stages | New stage is a heading-led region, announced once; focus moves predictably; prior information stays available; unrevealed content is absent rather than CSS-hidden when disclosure matters | Author defines each information increment, why it changes the reasoning task, advance condition, source, and complete static representation. Sequence is reviewed and fixed | Runtime records stage reached and associated attempts. Stage opening alone is not success. Never infer correctness from advancement |
| **Transfer activity**: apply a principle under changed surface features | Required to distinguish flexible use from near-copy success | Change too small, change introduces untaught knowledge, scoring an ambiguous prose response, or calling a repeated template "transfer" | Plain file states what remains invariant and what changes. Rich UI may change values, modality, context, representation, or learner-produced artifact | Alternative response routes preserve the same construct. Avoid visual or motor demands unrelated to the objective | Author declares source task, changed dimensions, invariant principle, expected reasoning, and scoring authority. A reviewer checks construct equivalence | This is the strongest candidate evidence for objective application. Report task conditions, help use, and sample size. Prose remains pending until approved marking |
| **Resume checkpoint**: restore context and agency after interruption | Reduces reorientation cost across long reading, guided cases, simulations, and practice | Resuming into an expired or unsafe state, stale source content, hidden state with no explanation, or false completion from scroll depth | Durable semantic checkpoint includes lesson and content identity, section or stage, activity state, disclosed content, source version, and optional scroll offset. Plain file stays complete without checkpoint data | On return, announce location and state, provide "resume" and "start section again", restore focus to a heading rather than arbitrary coordinates, and never trap the user in a prior mode | Renderer records checkpoints; authors mark safe semantic boundaries and short recap text. Source changes invalidate or reconcile checkpoint explicitly | Resume is session state, not mastery. Preserve authorized attempts and disclosures, avoid duplicate events, and show what changed if content version differs |

## 6. Cross-cutting effects

### Accessibility

The portable source must hold the content needed for alternatives, not ask the
renderer or a model to invent them at display time. Every interactive
capability needs keyboard and touch operation, predictable focus, announced
state changes, a non-drag path, and a static representation. Complex visuals
need structured descriptions that preserve relationships, not literal pixel
narration. Definitions and additional content need an explicit activation path
and must not obscure or disappear before they can be read.

Accessibility is also assessment validity. If the accessible alternative
changes the knowledge or motor demand, the two interactions do not measure the
same construct. Equivalent does not always mean visually identical.

### Portability

The authored file should remain coherent in Markdown readers and offline. Rich
behavior is derived from explicit semantics. A definition remains a glossary
entry, a worked example remains ordered annotated steps, a diagram retains its
relation list, and a simulation retains a static trace and variable model.
Generated indexes, component bundles, and resume state may be derived, but they
are not the sole readable lesson.

### Privacy and evidence

Keep the existing on-disk evidence boundary. Do not transmit event streams to
an analytics service merely because an interoperability standard defines them.
Minimize collection: a hover, focus, scroll, zoom, open disclosure, or time on
page is normally navigation or exposure, not evidence of understanding.
Meaningful evidence begins with an intentional response, decision,
explanation, modification, reconstruction, or transfer attempt.

Show denominators and conditions. "Two successful changed-context attempts,
one with a hint" is more honest than a mastery percentage. Never auto-grade
prose, and never let lesson UI decide keyed correctness or disclosure.

### Provenance

Every external image, clinical claim, protocol step, formula convention,
simulation model, and generated synthesis needs source identity and a stable
locator where possible. Media records should include rights and modification
information. Health content needs edition or effective date because an
otherwise accurate lesson can become unsafe when guidance changes.

### Authorability

Authors and agents need a closed semantic catalog, concise examples, lintable
required fields, and explicit quality questions. Deterministic lint can check
missing labels, references, alternatives, citations, units, bounds, response
schema, and unsupported component names. Semantic review must judge whether a
prediction is reasoned, a callout is useful, a visual teaches the objective, a
transfer task truly changes context, or a health scenario stays within source
and scope. Those judgments should not be disguised as deterministic lint.

## 7. Implications for product contracts and agent skills

### Learner flow

Course entry should lead to a reasoned next action, then explain the objective,
source, and activity shape before asking for input. Lessons need both
continuous reader and guided presentation. Direct readings can participate in
the same loop through orientation, definitions, citations, and adjacent
activities. Resume returns to a named semantic checkpoint and offers a recap.

### Semantic content contract

Phase 16 should define semantic records for glossary terms, media and rights,
callout role, annotated example steps, comparison dimensions, diagram
relations and alternative, simulation declaration and fallback, prediction,
activity placement, stages, transfer dimensions, and safe resume boundaries.
The syntax decision belongs to synthesis. This research does not presume that
each role needs a unique top-level Markdown block.

### Agent skills

An authoring agent should:

1. Start from objective, prerequisite, source, cognitive demand, and learner
   context.
2. Decide whether direct reading already provides the best treatment.
3. Select the smallest capability set that creates the intended learning loop.
4. For each capability, fill its purpose, portable form, accessibility
   alternative, citations, misuse check, and evidence intent.
5. Use only registered simulation and interaction primitives.
6. Generate a changed-context transfer activity for important objectives.
7. Lint deterministic fields, then request semantic and domain review.
8. Render and inspect continuous, guided, narrow, keyboard, touch,
   screen-reader, offline, and plain-file forms.

### Legacy upgrades

An upgrade agent must audit before editing. It should preserve stable identity,
source history, objective alignment, assessment meaning, keyed content, and
accepted wording unless a cited correction is required. Add a capability only
when it solves a named learning problem. The proposal must show the before and
after learning loop, portable fallback, accessibility behavior, provenance,
evidence change, and undo path. Cosmetic callout conversion, decorative images,
or splitting prose into interactions without a teaching reason should fail the
upgrade review.

## 8. Accept, reject, defer, prototype, and open questions

| Disposition | Candidate | Rationale |
|---|---|---|
| Accept | Semantic definitions with visible glossary floor and focus, click, and touch enhancement | Evidence supports deliberate vocabulary instruction; the accessibility path is clear |
| Accept | Purposeful cited images with rights, caption, alternatives, and modification record | Supports authentic and spatial learning while preserving provenance and portability |
| Accept | Sparse closed-role callouts | Signaling can help organization, while role and density rules address decorative misuse |
| Accept | Annotated worked examples alternated with independent variations | Convergent evidence and broad procedural applicability |
| Accept | Structured comparisons with explicit dimensions and learner explanation | Useful for discrimination and strategy flexibility across subjects |
| Accept | Semantic diagrams with relation list or structured long description | Preserves meaning across visual and nonvisual contexts |
| Accept | Conditional prediction with immediate observation or feedback and an uncertainty response | Strong fit in math, CS, causal systems, and information-limited cases, but not arbitrary facts |
| Accept | Purpose-classified inline checks under the existing runtime | Retrieval and feedback have strong support; assessment authority remains intact |
| Accept | Linear staged reveal with fixed authored order, retained prior stages, and no hidden future DOM | Fits health and other evolving-evidence reasoning while preventing leakage |
| Accept | Explicit changed-context transfer activities | Necessary to test flexible use rather than near-copy performance |
| Accept | Semantic resume checkpoints plus optional scroll restoration | Preserves context without treating scroll depth as progress |
| Reject | Hover-only definitions or controls | Excludes keyboard, touch, and many low-vision users |
| Reject | Decorative images, animations, "fun facts", or tips with no objective role | Seductive details can distract and create rights and authoring cost |
| Reject | Arbitrary lesson-authored executable code | Unbounded security, review, portability, and accessibility surface |
| Reject | Simulation success inferred from play time, clicks, or reaching an end state | These measures do not establish understanding or safe performance |
| Reject | Blind mandatory prediction | Can teach errors, encourage guessing, and misfit protocol or fact learning |
| Reject | Timed reveal, answer locking, or future stages present but visually collapsed | Adds pressure, harms review of changing evidence, or leaks protected content |
| Reject | Auto-grading explanations or treating callout and glossary use as mastery | Violates scoring authority and overclaims weak signals |
| Defer | Fully open-ended authorable simulations | Start with a small reviewed component library and expand from demonstrated teaching needs |
| Defer | Automatic AI-generated image descriptions at display time | Alternatives require contextual author judgment and must be inspectable in the durable source |
| Prototype | One cross-subject declarative causal model with variable table, static trace, prediction, accessible controls, and transfer | Tests whether one capability contract can serve math or science without becoming a bespoke widget system |
| Prototype | EMT unfolding case with fixed stages, safety decision, consequence, debrief, and changed-case transfer | Tests information disclosure, clinical provenance, prior-stage retention, and safe evidence semantics |
| Prototype | Mathematics worked-example progression with representation choice, compared methods, faded completion, and transfer | Tests annotated steps, narrow layout, symbolic fallback, and scaffold reduction |
| Prototype | CS PRIMM slice with sandboxed run, trace, modify, debug, and make | Tests executable capability boundaries and separates program output from conceptual evidence |
| Open question | What is the smallest diagram relation grammar that remains pleasant to author? | Needs author trials with health, math, and CS diagrams |
| Open question | Which shared simulation primitives earn inclusion in the first library? | Choose from objective demand, reuse across courses, accessibility cost, and validation capacity |
| Open question | How should a changed source version reconcile a resume checkpoint and prior evidence? | Needs a product-level identity and migration contract |
| Open question | Which instructional interactions are permitted in formal test mode? | Must be settled by runtime disclosure policy, not lesson styling |

## 9. Concrete recommendations and risks

1. Define one semantic capability catalog before visual design. Require every
   entry to specify teaching purpose, subject fit, portable form, rich behavior,
   accessibility, authoring fields, provenance, evidence meaning, and misuse.
2. Make the representative Phase 16 unit demonstrate continuous reading and
   guided flow from the same source, including a cited visual, definition,
   callout, worked or dynamic representation, prediction, feedback, transfer,
   and resume.
3. Use at least four subject fixtures, not one generic lesson: EMT or health,
   mathematics, CS, and a knowledge-heavy reading course.
4. Validate learning structure as well as rendering. Reviewers should be able
   to point from every capability to an objective and explain why simpler prose
   or direct reading was insufficient.
5. Separate exposure telemetry from evidence. Store only authorized local
   events, retain denominators and conditions, and leave prose pending.
6. Require current source and rights review for health content and media. A
   polished but outdated or unlicensed capability is a product defect.
7. Test authorability with both a human and an agent. If correct alternatives,
   citations, or transfer variations routinely need expert repair, narrow the
   capability or improve its scaffold before acceptance.

The largest risks are capability accumulation without teaching value,
inaccessible rich interactions, shallow evidence claims, clinical content
drift, media-rights failures, and a guided renderer becoming the only complete
copy. The controlling mitigation is the same across them: semantics first,
portable source always, bounded reviewed enhancement, runtime authority for
assessment, and explicit validation against a real objective.
