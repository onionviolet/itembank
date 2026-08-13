# Phase 16 research stream 03: question and learning-activity design space

**Research date:** 2026-08-13

**Access date for every web source:** 2026-08-13

**Scope:** research only. This document proposes no binding product-contract change.

## 1. Scope and research questions

This stream asks how itembank should represent questions and learning activities
without confusing an instructional purpose with a response widget. The organizing
order is therefore:

1. purpose in the learning loop;
2. cognitive demand and the evidence claim;
3. response form and interaction;
4. feedback, scoring authority, and evidence capture.

The specific questions are:

- What distinct roles do prediction, noticing, retrieval, explanation,
  comparison, diagnosis, practice, transfer, reflection, and formal assessment
  play?
- Which cognitive demands and subject practices can each role validly elicit?
- Which response forms preserve authenticity without creating avoidable access
  barriers?
- When is an activity evidence about learning, and when is it merely a useful
  learning action?
- What feedback is appropriate before, during, and after a response?
- Which responses can the deterministic runtime score, which require a declared
  rubric and reviewer, and which should remain unscored?
- Which apparent interaction ideas deserve semantic capabilities or renderings,
  but not new item types?
- How should standardized-test practice reproduce a sourced construct and
  blueprint rather than imitate isolated visual controls?

### Working definitions

- **Purpose** means why the learner is being asked to act now.
- **Cognitive demand** means the mental work the objective calls for, not how
  visually elaborate the control appears.
- **Response form** means how the learner externalizes a response, such as a
  selection, number, sentence, diagram annotation, ordering, or performance.
- **Activity** means a learning action that may not warrant scoring or item-bank
  identity.
- **Item** means a versioned prompt and response contract intended to produce an
  interpretable observation.
- **Evidence claim** means the limited inference a response can support about an
  objective.
- **Scoring authority** means the component or approved actor allowed to turn a
  response into a score or review state.

## 2. Sources

The source set intentionally combines current primary standards and assessment
frameworks with original studies and one research synthesis. Product-specific
question controls are not copied. The synthesis is included because feedback
effects vary by task and learner, and a single experiment cannot establish a
general feedback policy.

| Source | Direct link | Source type | Contribution and limitations |
|---|---|---|---|
| W3C, Web Content Accessibility Guidelines 2.2 | [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Normative web standard | Requires keyboard-operable, programmatically exposed controls and alternatives to path-based gestures and dragging. It governs access, not pedagogy. |
| W3C, Understanding Input Modalities | [Guideline 2.5](https://www.w3.org/WAI/WCAG22/Understanding/input-modalities.html) | Official explanatory guidance | Explains concurrent mouse, touch, keyboard, speech, and alternative input needs. It is informative guidance, not the normative text. |
| CAST, Universal Design for Learning Guidelines 3.0 | [UDL Guidelines 3.0](https://udlguidelines.cast.org/) | Primary design framework | Supports varied response, navigation, media, graduated practice, monitoring, and transfer. UDL is a design framework, not evidence that every learner should always receive every option. |
| 1EdTech, Question and Test Interoperability 3 specification index | [QTI specification documents](https://www.1edtech.org/standards/qti/index) | Primary interoperability standard | Separates item content, interactions, response processing, results, accommodations, and delivery. It demonstrates a broad design space, but importing QTI is outside this stream. |
| ETS, Mislevy, Almond, and Lukas, Evidence-Centered Assessment Design | [RM-03-03](https://www.ets.org/Media/Research/pdf/RM-03-03-Bennett.pdf) | Primary assessment-design research memorandum | Grounds task design in claims and evidence rather than item appearance. Its formal machinery can be heavier than a local course needs. |
| ETS, Best Practices for Constructed-Response Scoring | [Constructed-response scoring](https://www.tr.ets.org/pdfs/about/cr_best_practices.pdf) | Primary professional guidance | Emphasizes explicit constructs, rubrics, scorer training, monitoring, and validity for constructed responses. It does not justify unreviewed model grading. |
| OECD, PISA 2025 Assessment and Analytical Framework | [PISA 2025 framework](https://www.oecd.org/en/publications/pisa-2025-assessment-and-analytical-framework_86c36975-en.html) | Primary international assessment framework | Defines knowledge, processes, contexts, and how domains are assessed. It supports unfamiliar-context application, but PISA is not a universal course blueprint. |
| OECD, PISA 2025 Science Framework | [Science framework](https://pisa-framework.oecd.org/science-2025/) | Primary domain framework | Distinguishes content, procedural, and epistemic knowledge and situates competence in meaningful contexts. |
| College Board, AP Biology exam | [AP Biology exam format](https://apcentral.collegeboard.org/courses/ap-biology/exam) | Current official exam specification | Connects course concepts and science practices to stable section formats, timing, weights, stimuli, data, models, and investigations. It is one exam, not a generic item-design rule. |
| NCES, NAEP assessment frameworks | [NAEP frameworks](https://nces.ed.gov/nationsreportcard/frameworks.aspx) | Current official assessment program documentation | States that subject frameworks are blueprints for content and thinking skills. It supports blueprint-first fidelity across subjects. |
| Next Generation Science Standards | [Example performance expectations and practices](https://www.nextgenscience.org/dci-arrangement/ms-ess3-earth-and-human-activity) | Primary standards framework | Shows that asking questions, analyzing data, and constructing evidence-based explanations are different science practices even when one screen could render all as text entry. |
| Common Core State Standards Initiative, Mathematics | [Mathematics standards](https://corestandards.org/mathematics-standards/) | Primary standards framework | Emphasizes focus, coherence, conceptual understanding, and mathematical practice, useful for separating answer production from reasoning and modeling. |
| Chi and Wylie, 2014, ICAP | [Author-hosted paper](https://education.asu.edu/sites/g/files/litvpz656/files/lcl/chiwylie2014icap_2.pdf) | Peer-reviewed theoretical synthesis with empirical review | Classifies observable engagement as passive, active, constructive, or interactive. Engagement mode predicts learning under stated conditions, but visible activity alone does not prove cognition. |
| Chi et al., 1994, self-explanation | [Publisher record](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1803_3) | Original controlled study | Prompted eighth-grade learners to self-explain a circulatory-system text and found greater knowledge gains in a small sample. Generalization beyond that setting requires caution. |
| Roediger and Karpicke, 2006, repeated retrieval | [Publisher record](https://www.sciencedirect.com/science/article/pii/S0749596X06001367) | Original experiments | Found repeated retrieval supported longer-term retention better than repeated study in the tested conditions. It does not imply that all instruction should become tests. |
| Butler, 2010, retrieval and transfer | [Author-accessible paper](https://andymatuschak.org/files/papers/Butler%20-%202010%20-%20Repeated%20Testing%20Produces%20Superior%20Transfer%20of%20Learning%20Relative%20to%20Repeated.pdf) | Original experiments | Found repeated testing could support transfer to new inference questions and domains under the study conditions. Far-transfer claims remain task-sensitive. |
| Richland, Kornell, and Kao, 2009, pretesting | [PubMed record](https://pubmed.ncbi.nlm.nih.gov/19751074/) | Original experiments | Found unsuccessful pretests could improve later learning of tested concepts. The result supports prediction or prequestioning with corrective teaching, not punitive scoring. |
| Shute, 2008, formative feedback | [Author-hosted research report](https://myweb.fsu.edu/vshute/pdf/shute%202007_f.pdf) | Peer-reviewed research synthesis | Reviews timing, specificity, verification, explanation, hints, and learner/task interactions. It supports targeted feedback but warns against one universal feedback recipe. |

No protected item text, product visual asset, or branded interaction is reproduced
here.

### 2.1 Existing itembank research reviewed

The internal inventory covered the research index, all dated files under
`.planning/research/`, and phase research or completion records found by searching
for question, activity, feedback, assessment, item type, interaction,
accessibility, retrieval, and transfer. The most relevant artifacts are below.
Internal citations are repository paths because these are local project records,
not external authorities.

| Existing artifact | Date or state | Still-valid finding reused here | Stale, superseded, or gap identified |
|---|---|---|---|
| `.planning/research/2026-08-09-landscape-widening.md` | Researched 2026-08-09 | Compose visual tasks from a small interaction vocabulary with one accessibility story; preserve response observations; avoid fashionable interaction for its own sake. | It explicitly includes assumed and secondary product claims and predates the 2026-08-13 course reframe. Its competitor behavior claims were not used as current facts. It did not organize the space purpose first or cover formal blueprint fidelity comprehensively. |
| `.planning/research/2026-08-09-visual-design.md` | Researched 2026-08-09 | Reuse per-distractor feedback, calm motion, continuous reading, and interleaving of prose with checks. | It is primarily a visual-direction artifact. Several competitor descriptions are marked assumed or rely on secondary showcases. Those dated product observations need rechecking in Phase 17 and do not establish pedagogy here. Its earlier claim that celebratory motion is categorically locked out is no longer used as a general research veto; current binding constraints must be read from the current contracts. |
| `.planning/research/2026-08-09-lesson-display-editor.md` | Researched 2026-08-09 | Long lessons can interleave short prose and checks without forcing pagination; feedback status needs an accessible announcement. | It focused on reader and editor display. It did not distinguish prediction, noticing, diagnosis, reflection, and formal assessment as separate purposes. Product examples are dated and partly secondary. |
| `.planning/research/2026-08-10-ui-inspiration-missing-surfaces.md` | Researched 2026-08-10; declares itself input, not specification | Reuse the accurate constraint correction, accessible equivalents for pointer interaction, no key leakage, explicit degraded behavior, and one shared reader. | It contains now-stale browser-support language, including a claim that CSS Anchor Positioning was "Baseline 2026," and product claims marked assumed. Browser support and product behavior must be reverified when implemented. Its asserted print requirement is explicitly corrected by current `PLANNING-DIRECTIVES.md` §4a, which says no authoritative print-path constraint exists. |
| `.planning/research/2026-08-10-lesson-item-coupling.md` | Researched 2026-08-10 | Stable item identity should survive placement; lesson activity and formal bank lifecycle can differ; references need validation. | It answers storage and lifecycle questions, not the pedagogical purpose matrix. Its product-format survey is useful architecture context but does not determine response validity or feedback. |
| `.planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-RESEARCH.md` | Researched 2026-08-08; subsequently implemented | One runtime policy controls feedback and disclosure; duplicate or empty attempts must not unlock content; pending prose is not wrong; mode is not decoration. | Its fixed six-tier ladder is shipped legacy context, not evidence that every Phase 16 learning activity should use that ladder. New activity semantics must compose with the runtime gate rather than generalize one practice loop to all purposes. |
| `.planning/phases/06.1-interactive-visual-assessment-protocol/06.1-RESEARCH.md` and `06.1-03-SUMMARY.md` | Research dated 2026-08-08; completion record dated 2026-08-11 | Semantic state, not pixels, is the response; mouse, touch, keyboard, and native controls serialize through one reducer; pointer motion and hover are not evidence; GIFT refuses unsupported visual items honestly. These shipped findings directly support the response-equivalence rule in this document. | The research proposed a generic `visual` family and only plot and number-line slices shipped. Dense simulations, QTI, and broader interaction families remain open. Phase 16 should not infer that all visual cognition belongs to one demand or that every visual activity should be a `visual` bank item. |
| `.planning/phases/06.2-executable-textbook-loop/06.2-RESEARCH.md` | Researched during Phase 6.2; phase implementation followed | A lesson gate is presentation and evidence policy over existing items, not a seventh type or second scorer. Skip and supported practice must remain visible in evidence. | Required/recommended gate behavior is one existing flow, not the universal lesson sequence. Phase 16 needs voluntary prediction, noticing, reflection, and non-gated continuous reading as peers. |
| `.planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-RESEARCH.md` | Researched 2026-08-08; implementation work followed | One subject-invariant loop can vary medium, allowed response types, and verifier; running an example is ephemeral unless explicitly submitted; math rendering does not score. | The three-subject slice is too narrow for a comprehensive design space. This stream adds history, language, data, arts/performance, and formal-program considerations while keeping the shared-loop finding. The document's same-day package-version claims are stale and irrelevant to question semantics. |
| `.planning/research/FEATURES.md`, `PITFALLS.md`, and `SUMMARY.md` | Milestone-level research, largely 2026-08-08 to 2026-08-10 | Preserve stable identity, deterministic authority, local evidence, honest pending states, targeted feedback, and incremental vertical slices. | These documents predate the source-to-course product contract and center the bank, tutor, or milestone more than the course. They are architectural guardrails, not a current learning-activity taxonomy. |

#### Reused conclusions

The internal record already settled several implementation-facing questions, so
this stream does not reopen them:

1. correctness, disclosure, feedback-mode transition, and evidence authority stay
   in the runtime;
2. pointer coordinates, hover, and tentative movement are not learning evidence;
3. visual controls submit canonical semantic responses and need equivalent input
   routes;
4. lesson gating, hinting, timing, and presentation are policies over items, not
   automatically new item types;
5. runnable observation, reading, and reflection can be useful activities without
   becoming scored attempts;
6. unsupported export or degraded rendering must be explicit rather than silently
   approximated.

#### Stale claims and browsing gaps

The prior audits are only three to five days old by calendar date, but many
product and browser claims are still unsuitable as current evidence because the
documents label them assumed, cite secondary showcases, or were scoped to an
earlier bank-centered milestone. This stream therefore did not repeat broad
competitor browsing. New browsing focused on gaps that remained:

- current normative accessibility behavior, especially dragging, target size,
  programmatic state, and alternative input;
- current primary interoperability evidence that interaction and response
  processing are separable;
- current official exam frameworks showing construct, context, format, timing,
  and blueprint fidelity together;
- subject-practice frameworks beyond the existing EMT, math, and CS slice;
- original research for pretesting, retrieval, self-explanation, transfer, and
  feedback;
- a comprehensive purpose-first matrix and an explicit test for ideas that should
  remain activities, policies, stimuli, or renderings rather than item types.

The external source ledger in §2 supplies those missing or refreshed authorities.
Current competitor product behavior belongs mainly to streams 01 and 02 and to
Phase 17 visual research, so it is not duplicated here.

## 3. Observed facts, inference, and recommendations

### 3.1 Observed facts

1. WCAG 2.2 requires keyboard access, programmatically determinable name, role,
   value, and state, text alternatives for non-text content, and a non-dragging
   way to perform dragging functionality unless dragging is essential.
2. CAST UDL 3.0 explicitly recommends multiple methods for response,
   navigation, expression, communication, graduated practice, progress
   monitoring, and transfer.
3. QTI 3 treats interaction, response processing, results, accommodations, and
   delivery as related but separable concerns. Its existence does not make every
   interaction a distinct cognitive construct.
4. Evidence-centered design begins with what a learner should know or do, what
   observations would support that claim, and what tasks would elicit those
   observations.
5. PISA 2025 explicitly distinguishes content, procedural, and epistemic science
   knowledge and assesses application in contexts. AP Biology publishes a
   course framework plus stable question formats, weights, timing, and science
   practices. NAEP likewise defines subject frameworks as assessment blueprints.
6. The cited retrieval studies found benefits for delayed retention, subsequent
   learning after unsuccessful retrieval, and some changed-question or
   changed-domain transfer under their experimental conditions.
7. The cited self-explanation study found greater gains for a small prompted
   group reading a circulatory-system text. ICAP distinguishes merely attending
   or manipulating from generating new output and engaging in substantive
   dialogue.
8. Shute's review documents that feedback effectiveness depends on content,
   timing, learner, and task. Verification, explanation, hints, and worked
   examples are different feedback moves.

### 3.2 Inference from those facts

1. A visible control is weak metadata for cognitive demand. The same multiple
   choice control can elicit recognition, causal diagnosis, source comparison,
   or transfer. The same prose box can elicit unsupported opinion, a rigorous
   proof, or a reflection that should never be graded.
2. Purpose, demand, subject practice, response form, feedback policy, and scoring
   authority need separate fields or semantics. Combining them in one `TYPE`
   label will force false equivalences.
3. Prediction and pretesting are instructionally useful even when initially
   wrong, provided the attempt is low stakes and followed by the relevant
   observation or teaching. Initial correctness is not the sole value.
4. Manipulation becomes educationally meaningful only when the moved, selected,
   or constructed state provides evidence tied to an objective or prepares a
   later explanation. Motion by itself is not cognitive demand.
5. Authenticity is relational. A spreadsheet may be authentic for data
   analysis, an oral response for pronunciation, source annotation for history,
   code execution for programming, and a timed selected response for a specific
   standardized exam. No single response form is globally most authentic.
6. Accessibility alternatives should preserve the evidence claim, not merely
   reproduce the gesture. An accessible ordering list can replace drag motion;
   it cannot replace a spatial reasoning task if spatial arrangement is itself
   the construct without a carefully equivalent representation.

### 3.3 Recommendations

1. Model every prompt as a composition of `purpose + demand + objective +
   stimulus + response schema + feedback policy + evidence policy + scoring
   authority`, with response form chosen last.
2. Make the ten purposes in this document an authoring vocabulary before adding
   any parser-level item family.
3. Preserve the runtime as the only deterministic scorer. Keep free prose,
   proofs, extended explanations, design work, and reflections pending or
   unscored until an explicit human or human-approved review action occurs.
4. Treat prediction, noticing, reflection, staged reveal, confidence capture,
   hint request, and compare-before-reveal primarily as lesson activities. Add
   bank item identity only when a stable evidence claim and scoring/review
   contract justify it.
5. Require each scored activity to name the claim it supports and the evidence
   it captures. Do not infer mastery from clicks, completion, time, or confidence
   alone.
6. For standardized-test courses, version and cite the target blueprint, then
   match construct, content weight, cognitive demand, stimulus family, response
   constraints, timing, tools, and scoring. Visual similarity is insufficient.

## 4. Purpose-first pattern inventory

### 4.1 Summary matrix

| Purpose | Typical learning moment | Useful demand range | Suitable response families | Feedback default | Evidence status |
|---|---|---|---|---|---|
| Prediction | Before a model, reading, experiment, example, or reveal | anticipate, estimate, hypothesize, commit a model | choice plus reason, numeric estimate, sketch, rank, forecast | Withhold outcome until commitment, then show contrast and explanation | Diagnostic trace, normally low stakes |
| Noticing | During observation, reading, source inspection, worked example, or visualization | identify, discriminate, annotate, detect change or pattern | select span/region, mark feature, table observation, describe change | Point to missed or misread evidence, avoid giving the later inference too early | Process evidence, not mastery alone |
| Retrieval | After initial learning and after delay | recall, recognize, reconstruct, produce | free recall, cue completion, selected response, label, formula or code recall | Corrective answer plus concise rationale; schedule later retrieval | Scorable when key is deterministic |
| Explanation | After observation or answer | explain why/how, justify, derive, connect evidence | short/extended prose, equation derivation, proof, oral explanation, annotated model | Address reasoning gap; worked step or counterexample as needed | Pending review unless bounded deterministic representation |
| Comparison | When discriminating cases, sources, methods, models, or concepts | classify dimensions, contrast, weigh evidence, choose criterion | matrix, paired annotation, sorting, selected claim plus evidence, prose | Name the discriminating dimension and overlooked evidence | Mixed, deterministic for fixed matches, pending for justification |
| Diagnosis | After error, anomaly, flawed work, symptom, bug, or misconception | locate fault, infer cause, choose test, revise | error highlight, fault tree, next-test choice, corrected step, debugging action | Misconception-specific and local to the fault; permit another attempt by mode | Strong process evidence if task is controlled |
| Practice | During skill building and consolidation | imitate, complete, apply, integrate, increase fluency | any construct-aligned response with scaffolding and variation | Immediate or staged formative feedback; fade support | Evidence tagged as supported practice |
| Transfer | After near practice and after delay | adapt, generalize, select model, solve in changed context | novel scenario, case, design, simulation decision, source synthesis | Usually after commitment; explain invariant and changed features | Stronger evidence, but claim limited to sampled contexts |
| Reflection | At transition, review, confidence check, or planning | monitor, explain strategy, identify uncertainty, plan next action | journal, confidence plus reason, error log, study plan, self-rating with evidence | Non-evaluative prompts and links to evidence; no false correctness | Learner-authored context, not score |
| Formal assessment | Diagnostic, unit, cumulative, certification, or blueprint-faithful sitting | whatever the sourced construct requires | blueprint-constrained selected, constructed, performance, oral, practical, or mixed | Mode-controlled, generally no coaching before final submission | Authoritative only through runtime and approved review |

### 4.2 Prediction

**Benefits.** Prediction activates prior models, makes a later discrepancy
visible, and gives the learner a reason to inspect the outcome. It is especially
useful before a physics simulation, a chemistry reaction, a program run, a
historical source reveal, a statistical result, or a narrative turn.

**Weaknesses and misuse.** A trivia guess with no causal relation to the lesson
creates noise. Scoring an uninstructed prediction can punish prior opportunity.
Showing the answer before commitment eliminates the contrast. Requiring a long
explanation before novices have vocabulary can measure writing rather than the
target model.

**Applicability.** Use a quick commitment first, then optionally ask for a reason.
Capture the original prediction immutably as an activity trace, but do not label
it mastery. In formal tests, prediction is relevant only when prediction is part
of the published construct.

Examples across subjects:

- Physics: predict which of two velocity graphs follows a force change, then
  inspect the simulation and explain the mismatch.
- Biology: predict how an intervention changes a system, then compare with data.
- Mathematics: estimate the sign and scale before exact calculation.
- Programming: predict output or failure mode before running code.
- History: predict which source claim later evidence will support, then inspect
  provenance and corroboration.
- Language: predict a speaker's intent from context before hearing the final turn.

### 4.3 Noticing

**Benefits.** Noticing directs attention to evidence needed for later reasoning.
It can reveal whether an error came from perception, reading, representation, or
inference. It is useful for graph features, textual qualifiers, code diffs,
phoneme contrasts, artistic technique, anatomical structure, and source metadata.

**Weaknesses and misuse.** Hotspot clicking can become visual search detached
from meaning. Color-only differences and tiny targets create access barriers.
Correct highlighting does not establish explanation or transfer.

**Applicability.** Ask the learner to mark the evidence and, when the objective
requires it, connect that mark to a claim. Preserve the cited span, region,
timestamp, cell, or semantic feature, not raw pointer coordinates alone.

### 4.4 Retrieval

**Benefits.** Retrieval strengthens later access and exposes what can be produced
without looking. It fits vocabulary, formulas, events, syntax, anatomical labels,
musical notation, and conceptual relationships. Cumulative and spaced retrieval
can revisit objectives after delay.

**Weaknesses and misuse.** Recognition-only practice can overstate productive
recall. Repeating identical surface forms can teach item cues. Excessive retrieval
before understanding can reduce a course to flashcards.

**Applicability.** Vary cues while preserving the knowledge target, distinguish
recognition from production in evidence, and follow errors with corrective
feedback. A later changed-context activity is still needed for important transfer
objectives.

### 4.5 Explanation

**Benefits.** Explanation externalizes causal, procedural, evidential, or
conceptual connections. Self-explanation can turn reading or worked examples into
constructive activity. It fits proof, source reasoning, diagnosis, scientific
mechanism, code behavior, design rationale, and language use.

**Weaknesses and misuse.** Generic "explain your answer" prompts produce vague
prose and create scoring burden. Writing fluency can contaminate the target.
Automatic semantic grading can disguise uncertainty as authority.

**Applicability.** Specify the explanatory move: cite evidence, connect two
steps, justify a method, explain a mechanism, identify an assumption, or state
why a distractor would be valid in another condition. Provide speech, structured
tokens, equations, or diagrams when those preserve the construct. Leave open
responses pending until reviewed.

### 4.6 Comparison

**Benefits.** Comparison makes dimensions and boundary conditions explicit. It
supports concept discrimination, historiography, literary analysis, algorithm
choice, biological structures, legal rules, diagnostic criteria, and language
register.

**Weaknesses and misuse.** A two-column cosmetic layout is not comparison. A
fixed sorting task can cue the categories and undermeasure independent
generation. Too many dimensions can overload the learner.

**Applicability.** Name or elicit the comparison criterion, then ask for evidence
or consequence. Record both placement and justification when justification is
part of the objective.

### 4.7 Diagnosis

**Benefits.** Diagnosis starts with a flawed product, anomaly, or symptom and asks
the learner to locate and explain the fault. It is highly suitable for worked
mathematics, code debugging, grammar correction, experimental design, clinical
reasoning with appropriate educational safeguards, argument evaluation, and
misconception repair.

**Weaknesses and misuse.** Artificial errors can teach bad patterns if feedback
is delayed or ambiguous. Asking only "which is wrong?" undermeasures cause and
repair. High-stakes health or safety cases need authoritative sources and scope
limits.

**Applicability.** Separate fault location, cause, confirming test, and repair.
Each can use a different response form while remaining one diagnostic activity
sequence. Give feedback at the first unsupported inference, not merely at the
final answer.

### 4.8 Practice

**Benefits.** Practice develops accuracy, fluency, coordination, strategy
selection, and integration. Scaffolds can fade from worked example to completion
problem to independent attempt. Variation can expose the invariant structure.

**Weaknesses and misuse.** Completion volume is not learning. Hints, retries, and
worked steps change what the response demonstrates. Uniform immediate answer
reveal can create dependence.

**Applicability.** Declare support state on every attempt. Record hints and
retries separately from correctness. Mix near examples with cumulative and
changed-context work. Do not compare a supported practice score directly with an
unassisted assessment score.

### 4.9 Transfer

**Benefits.** Transfer tests whether a learner can recognize and use an idea when
surface features, context, data, representation, or required action changes. It
is central to the source-to-course quality contract.

**Weaknesses and misuse.** "Real world" decoration does not create transfer. A
remote context can add irrelevant reading, culture, or domain knowledge. One
successful case does not prove general transfer.

**Applicability.** State what changes and what should remain invariant. Use near
transfer before far transfer. Sample more than one context for important claims
and disclose the denominator. Prefer authentic subject work, such as evaluating
sources, designing an investigation, selecting an algorithm, or revising prose,
over a contrived story wrapper.

### 4.10 Reflection

**Benefits.** Reflection supports monitoring, strategy selection, confidence
calibration, error review, and planning. It can provide useful context for an AI
or learner choosing the next action.

**Weaknesses and misuse.** Mandatory journaling after every step becomes friction.
Self-rating is not objective mastery evidence. Sentiment or personal disclosure
should not become hidden telemetry.

**Applicability.** Keep it optional or strategically placed. Ask for evidence:
"Which step remains uncertain and what would test it?" Store locally, let the
learner edit or exclude sensitive reflection, and never score emotional tone.

### 4.11 Formal assessment

**Benefits.** Formal assessment can support diagnostic, unit, cumulative, or
credentialing decisions when claims, blueprint, task sampling, administration,
and scoring align.

**Weaknesses and misuse.** Turning a practice interaction into a test by hiding
hints does not establish validity. Novel widgets can measure interface learning.
Unreviewed AI scoring can convert plausible language into false authority.

**Applicability.** Freeze the permitted supports, timing, navigation, tools,
feedback, retries, and disclosure mode. Use the target exam's current official
framework when fidelity is claimed. Preserve selected responses for deterministic
runtime scoring. Route constructed responses through declared rubrics and
approved review. Report pending work explicitly.

## 5. Response-form design space

Response forms are reusable renderings. They should not independently determine
purpose or score meaning.

| Response family | Good uses | Main validity or access risk | Scoring authority |
|---|---|---|---|
| Single selection | discriminate best claim, next step, model, or interpretation | recognition cues, guessing, implausible distractors | Deterministic runtime with keyed option |
| Multiple selection | identify a set of applicable claims or evidence | unclear partial-credit rule, working-memory load | Runtime only with explicit exact or partial rule |
| Binary or repeated binary | rapid classification or claim evaluation | acquiescence, guessing, treating related rows as independent | Runtime with declared aggregation |
| Numeric entry | calculation, estimate, measurement, parameter | unit, tolerance, rounding, locale, equivalent notation | Runtime with explicit units and tolerance |
| Symbolic expression | algebra, chemistry, logic, code fragments | equivalence is hard; string match is invalid for many constructs | Runtime only for safely normalized bounded grammar, otherwise pending |
| Short text | term, phrase, concise explanation, translation | synonym handling and writing contamination | Deterministic only for tightly bounded accepted forms; prose pending |
| Extended response | explanation, argument, proof, design, synthesis | rubric drift, scorer reliability, language demands | Pending human or human-approved rubric review |
| Table or matrix | compare dimensions, complete data, classify cases | keyboard navigation, cell semantics, overcueing | Mixed by cell contract |
| Ordering | sequence events, steps, priorities, causal chain | drag-only access, multiple valid orders | Runtime with keyboard/button alternative and explicit equivalence |
| Matching or grouping | relations, categories, correspondences | cueing, many simultaneous choices, ambiguous duplicates | Runtime with declared cardinality and partial credit |
| Span annotation | textual evidence, error location, key phrase | exact-boundary scoring, screen-reader selection | Runtime for defined spans or pending for rationale |
| Image or diagram annotation | structure, spatial relation, graph feature | vision, motor precision, coordinate fragility | Runtime only with semantic regions and equivalent non-pointer route |
| Construct or build | equation, model, circuit, timeline, program, argument map | manipulation can replace reasoning; state space can be large | Runtime for finite validated states, otherwise pending |
| Code response | implement, debug, predict, test | unsafe execution, hidden tests, environment mismatch | Approved deterministic sandbox and test contract, not a model's opinion |
| Audio or oral response | pronunciation, fluency, music, oral defense | privacy, recording access, speech-recognition bias | Pending qualified review unless exact signal feature is narrowly validated |
| Physical or external performance | lab technique, art, clinical or vocational procedure | cannot be inferred from a proxy click; safety and observation reliability | Qualified observer or approved device contract |
| Confidence plus reason | calibration and reflection | confidence is not correctness; coercive disclosure | Never correctness authority; local contextual evidence only |

### Response equivalence rule

An alternative interaction is equivalent only when it preserves the target
claim. For ordering conceptual steps, buttons that move a focused item up or down
can replace dragging. For drawing a trend, a data table plus a keyboard-operable
plot editor may preserve the claim. For pronunciation, typed transcription does
not preserve the speech-production claim. The authoring contract therefore needs
an `essential modality` declaration only when the objective truly depends on
that modality, plus an accessible assessment plan rather than a blanket waiver.

## 6. Feedback, scoring authority, and evidence capture

### 6.1 Feedback policy by purpose

| Purpose | Before response | During response | After response |
|---|---|---|---|
| Prediction | Orient and define what to predict, no outcome cue | Allow commitment and optional reason | Reveal observation, contrast, and mechanism |
| Noticing | Define the feature class, not its location | Optional attention cue after struggle | Show missed evidence and its relevance |
| Retrieval | Provide cue and response expectations | Usually no content hint on first attempt | Correct answer, concise rationale, later retrieval scheduling |
| Explanation | State required reasoning move and evidence | Structural scaffold if practice mode allows | Target the first reasoning gap, then model or counterexample |
| Comparison | Define or ask for comparison criterion | Permit structured matrix or source access by mode | Name overlooked dimension and evidence |
| Diagnosis | Present authentic faulty state and available tests | Consequence or test result after chosen action | Localize fault, cause, and repair; allow bounded retry |
| Practice | Declare supports and attempt policy | Hints from general to specific; fade across attempts | Verification plus explanation appropriate to error |
| Transfer | Clarify task and authentic constraints, not solution mapping | Minimal support if evidence is intended as unassisted | Explain invariant, changed features, and alternative strategy |
| Reflection | Offer evidence summary and voluntary prompt | No correction of personal judgment | Suggest a testable next action, not a grade |
| Formal assessment | State rules, timing, tools, and navigation | Only blueprint-authorized accommodations and supports | Feedback at mode-authorized time after disclosure gate |

### 6.2 Authority states

Use explicit states rather than a generic `graded` boolean:

1. **unscored activity:** completion may be recorded, but there is no correctness
   judgment;
2. **deterministically scored:** the single runtime applies a versioned key and
   rule;
3. **pending review:** an open or performance response awaits a declared marker;
4. **reviewed:** an authorized human or human-approved marking action applied a
   versioned rubric, with reviewer and timestamp;
5. **invalidated or superseded:** administration or content problems prevent the
   result from supporting its former claim.

The model may draft feedback, summarize a rubric, or propose a review. It may not
silently promote pending prose to correct, alter a keyed result, select a hidden
hint tier, or reveal protected content before the runtime permits it.

### 6.3 Minimum evidence record

Capture only interpretable, local evidence:

- course, objective, artifact, item/activity, and version identifiers;
- purpose and cognitive-demand tags;
- stimulus and response-schema versions;
- original response plus semantic response representation;
- attempt number, timing window, and completion timestamp;
- support state, hints requested or granted, retries, source access, and tools
  permitted;
- score state, scoring rule or rubric version, authority, and review state;
- confidence only when intentionally requested;
- accessibility or alternate interaction used only when needed to interpret the
  administration, without treating disability-related choices as deficits;
- provenance and blueprint binding for formal items.

Do not treat hover count, pointer path, scroll depth, decorative interactions,
raw dwell time, or emotional language as mastery. If retained for local user
experience diagnostics, they need a separate purpose, retention policy, and no
automatic learning claim.

## 7. Standardized-test fidelity and authenticity

### Observed pattern

Official frameworks specify more than widgets. PISA defines domains,
competencies, knowledge, contexts, and assessment methods. AP Biology connects
course concepts and science practices to timed weighted sections, shared
stimuli, experiments, graphs, models, data, and written responses. NAEP treats
the subject framework as the assessment blueprint.

### Inference

A faithful practice set must reproduce the intended construct and distribution,
not merely use multiple choice or free response. Fidelity has at least eight
dimensions:

1. blueprint version and source;
2. content and objective weights;
3. cognitive-demand and subject-practice distribution;
4. stimulus families and information density;
5. response forms and scoring rules;
6. timing, sectioning, navigation, and permitted tools;
7. difficulty and dependency patterns;
8. accessibility and official accommodation assumptions.

### Recommendation

Maintain two explicit modes:

- **construct practice:** the same objective and reasoning, with formative
  feedback, scaffolds, and varied response forms;
- **simulation or formal sitting:** blueprint-faithful administration with
  controlled feedback, timing, tools, scoring, and disclosure.

Construct practice may improve learning without looking exactly like the exam.
Simulation must look and behave sufficiently like the current official target to
support readiness claims. Never call a set faithful without a versioned mapping
and coverage report.

## 8. Accessibility, portability, privacy, provenance, and authorability

### 8.1 Accessibility

- Every activity needs a logical heading, instructions, programmatic label,
  state, error, and result announcement.
- Hover-only content needs focus and touch access. Dragging needs a single-pointer
  non-dragging route unless dragging itself is essential.
- Selection, ordering, matching, tables, and diagram tasks need predictable
  keyboard operation and screen-reader-readable relationships.
- Color, position, animation, sound, or pointer coordinates cannot be the only
  carrier of task meaning.
- Timed formal tasks need the target program's accommodation rules. Instructional
  activities should avoid timing unless fluency or pacing is the objective.
- Alternative modalities must preserve the evidence claim. When they cannot,
  provide an accessible learning treatment and an honest assessment limitation.

### 8.2 Portability

The plain lesson should retain prompt, stimulus, choices or response expectation,
feedback boundary, citations, and a useful static representation. Rich controls
are derived. Examples:

- drag ordering degrades to a numbered list to reorder;
- hotspot noticing degrades to labeled regions or a textual feature list;
- simulation prediction degrades to initial state, predicted outcome, and a
  sequence of cited snapshots or data;
- compare cards degrade to a semantic table;
- staged reveal degrades to clearly marked prompt and later explanation sections.

Portable degradation does not require a plain reader to score the response. It
requires the learning meaning to remain understandable.

### 8.3 Privacy

Responses, evidence, audio, reflections, and derived state stay on disk under the
project contract. Collect only what the learning or assessment claim needs. Audio,
personal reflection, accessibility choices, and confidence are especially
sensitive. They need explicit purpose, local controls, and deletion or exclusion
paths. No engagement telemetry should leave the device.

### 8.4 Provenance

Every stimulus, excerpt, data set, image, blueprint mapping, key, rubric, and
generated adaptation needs origin, locator, license or ownership status, version,
and transformation record. A source-grounded question should distinguish quoted
source material from generated framing and generated distractors. Formal-item
revisions must preserve old versions and explain construct impact.

### 8.5 Authorability

An author or agent should be required to answer these in order:

1. What objective and learner state is this for?
2. What purpose does the activity serve now?
3. What cognitive work should be observable?
4. What response would provide that observation with least irrelevant burden?
5. What feedback is allowed in this mode and when?
6. Who or what may score it?
7. What evidence is recorded, and what inference is prohibited?
8. How does it work with keyboard, touch, screen reader, narrow screen, offline,
   and plain-file reading?
9. Which source and blueprint claims support it?
10. Does it require a new semantic capability, or only a rendering of one already
    present?

## 9. Implications for flow, content contract, skills, and legacy upgrades

### 9.1 Learner flow

A representative unit should support this sequence without forcing every step:

`orient -> predict -> observe/noticing -> explain -> guided practice -> retrieval
after delay -> changed-context transfer -> reflect/choose next action -> formal
assessment when warranted`

The learner should always know whether a prompt is exploratory, supported
practice, unassisted evidence, reflection, or formal assessment. Resume state
must preserve an unanswered prompt without revealing gated feedback.

### 9.2 Semantic content contract

The contract should represent orthogonal semantics, not a flat explosion of item
types:

- purpose;
- objective and cognitive demand;
- subject practice or construct;
- stimulus roles and source locators;
- response schema and equivalent interaction;
- feedback mode and reveal stages;
- evidence claim and prohibited inference;
- scoring authority and rubric/key version;
- support and retry policy;
- blueprint binding when applicable.

This is an inference and recommendation for Phase 16 synthesis, not a settled
grammar. Any parser change must remain additive and use the one parser.

### 9.3 Agent skills

Question-authoring and course-building skills should:

- choose purpose and demand before response form;
- search for existing adequate items and activities first;
- produce subject-diverse examples and identify construct-irrelevant burden;
- generate misconception-linked distractors and say when each would be correct;
- declare feedback, support, retry, evidence, and authority policies;
- refuse automatic prose scoring;
- verify keyboard, touch, screen-reader, narrow-screen, offline, and plain-file
  behavior;
- lint blueprint claims against cited current official sources;
- statistically inspect answer position, difficulty, objective, purpose, demand,
  and response-form distributions;
- label uncertainty and submit semantic changes for review.

### 9.4 Legacy upgrades

Audit before enhancement:

1. preserve stable identity, fingerprint, key, objective, provenance, and prior
   evidence;
2. identify the existing item's actual purpose and demand;
3. determine whether the proposed rich interaction changes only presentation or
   changes the construct, response, key, difficulty, or access burden;
4. use a rendering-only enhancement when semantics are unchanged;
5. create a new version, not a silent mutation, when response or construct
   changes;
6. verify static fallback and equivalent interaction;
7. rerun lint, scoring, leakage, accessibility, and blueprint checks;
8. present a bounded diff and reversal path.

## 10. Ideas that should not become new item types

| Candidate idea | Better representation | Reason not to add an item type |
|---|---|---|
| Prediction card | `purpose: prediction` on an existing response schema | Prediction changes timing and feedback, not necessarily response grammar. |
| Confidence slider | Response metadata or reflection activity | Confidence is contextual evidence, never correctness. |
| Hint button | Feedback and support policy | A hint is a runtime-controlled disclosure action, not a question. |
| Retry | Attempt policy | Retry changes evidence interpretation, not the prompt's response form. |
| Staged reveal | Lesson sequence and disclosure state | It structures teaching and feedback. |
| Flashcard | Retrieval presentation using cue and response | Card appearance does not define the knowledge claim. |
| "AI question" | Provenance and review status | Authorship does not define pedagogy or scoring. |
| Timed question | Administration policy | Timing is construct-relevant only for selected objectives or blueprints. |
| Compare cards | Comparison purpose plus table, selection, or explanation | Layout is not the comparison operation. |
| Error hunt | Diagnosis purpose plus annotation or correction response | The cognitive role is diagnosis, while the response varies. |
| Hotspot | Semantic region selection rendering | It is one input mechanism and needs equivalent access. |
| Drag and drop | Ordering, matching, grouping, or spatial construction | Drag is a gesture. The underlying relation is the semantic response. |
| Simulation question | Stimulus/tool capability plus prediction, diagnosis, or transfer | A simulation supplies state and consequences; it does not define one demand. |
| Interactive diagram | Stimulus and response capability | Interactivity may support noticing, prediction, construction, or explanation. |
| Reflection question | Unscored reflection activity | Treating personal reflection as a keyed bank item invites false grading. |
| Discussion | Collaborative activity with turn and artifact rules | Dialogue is a learning structure, not one scoreable response type. |
| Source-grounded question | Provenance and stimulus binding | Grounding is a quality and traceability property. |
| Adaptive question | Selection and sequencing policy | Adaptivity chooses or configures items; it is not an item grammar. |
| Worked example completion | Practice sequence with faded steps | The scaffold level should be recorded separately from response form. |
| Gamified challenge | Presentation and progression layer | Points, streaks, and animation do not define evidence. |

Possible parser-level additions should pass a stricter test: the existing response
schemas cannot express the response, a deterministic or pending-review contract
is clear, accessibility equivalence is designed, plain-file meaning survives, and
the new grammar adds demonstrable learning or assessment value.

## 11. Accept, reject, defer, prototype, and open questions

| Status | Proposal | Rationale or question |
|---|---|---|
| Accept | Purpose-first taxonomy covering all ten roles | It directly follows the research index and prevents widget-led design. |
| Accept | Separate purpose, demand, response, feedback, evidence, and authority | Supported by evidence-centered design and by cross-subject examples. |
| Accept | Prediction and noticing as low-stakes instructional activities | They orient attention and expose models, but initial accuracy should not imply mastery. |
| Accept | Retrieval plus corrective feedback and later changed-context work | Retrieval supports retention; it is insufficient alone for all objectives. |
| Accept | Explicit unscored, deterministic, pending, reviewed, and invalidated states | Prevents prose auto-grading and makes authority inspectable. |
| Accept | Equivalent non-dragging operation for ordering, matching, and grouping | Required for accessible operation and reveals drag as a rendering choice. |
| Accept | Blueprint-version binding for any fidelity claim | Official programs define constructs, distributions, conditions, and formats together. |
| Accept | Support-state evidence for hints, retries, source access, and scaffolds | Supported and unassisted responses warrant different interpretations. |
| Reject | New item type for each card, gesture, animation, or competitor control | Visual novelty does not establish a distinct response or evidence contract. |
| Reject | Automatic correctness for free explanation, proof, design, reflection, or oral performance | It violates the product authority boundary and lacks a generally valid deterministic rule. |
| Reject | Engagement or mastery inference from clickstream, dwell, hover, or completion alone | These signals are ambiguous and would encourage telemetry without a valid claim. |
| Reject | Calling a set standardized-test faithful because it shares widget shapes | Fidelity requires a current sourced blueprint and multidimensional mapping. |
| Defer | General symbolic-math equivalence scoring | It may be valuable, but safe normalization, domain limits, and error behavior need separate research. |
| Defer | Automated speech and pronunciation scoring | Bias, privacy, construct definition, offline behavior, and qualified review need domain study. |
| Defer | General executable simulation authoring | It needs security, portability, accessibility, and authoring contracts beyond this matrix. |
| Defer | QTI import or export | QTI is informative, but interoperability scope and mapping cost belong to a later decision. |
| Prototype | One activity rendered through alternative controls | Test ordering with drag, move buttons, keyboard shortcuts, and plain numbered-list fallback against one claim. |
| Prototype | Purpose progression in one multi-subject unit | Exercise prediction, noticing, explanation, practice, delayed retrieval, and transfer with honest evidence labels. |
| Prototype | Diagnostic error sequence | Test fault location, next-test selection, repair, targeted feedback, and bounded retry as one sequence. |
| Prototype | Formal versus construct-practice modes from one objective map | Verify that support and feedback vary without corrupting assessment authority. |
| Open | How many purpose and demand tags should authors see directly? | Too few erase meaning; too many reduce author reliability. Test with agents and humans. |
| Open | Which bounded short-text domains can be deterministically normalized safely? | Synonyms, units, notation, locale, and ambiguity require domain-specific rules. |
| Open | How should collaborative explanations be stored without a second evidence store? | Individual and group contributions need interpretable provenance. |
| Open | When does an accessible alternative change the target construct? | Resolve per objective through claim-preservation review and user testing. |

## 12. Concrete recommendations and risks

### Recommended Phase 16 outputs

1. Approve the purpose taxonomy as semantic authoring guidance, then validate it
   against at least mathematics, science, history, language learning,
   programming, and one performance subject.
2. Define a cognitive-demand vocabulary based on objective verbs and subject
   practices, not a single universal ladder. Allow crosswalks to exam frameworks.
3. Specify response schemas independently and document which are deterministic,
   bounded-normalized, pending review, or unscored.
4. Define feedback and evidence contracts for each purpose, including reveal
   timing, support state, retries, and prohibited inferences.
5. Prototype three high-risk equivalence cases: ordering without drag, visual
   noticing without coordinate-only scoring, and explanation through prose,
   speech, or structured representation without false equivalence.
6. Create a blueprint-fidelity checklist and a machine-readable mapping concept
   before any standardized-test course claims fidelity.
7. Add an authoring test that asks whether a proposed item type is actually a
   purpose tag, response schema, stimulus capability, feedback policy,
   administration setting, or presentation.
8. Make the representative Phase 16 tracer report what each activity teaches,
   what it records, who can score it, how it degrades, and which claim it cannot
   support.

### Principal risks

| Risk | Consequence | Mitigation |
|---|---|---|
| Taxonomy becomes decorative metadata | Authors tag purpose after choosing a widget | Authoring workflow and lint ask for purpose, demand, and claim first. |
| Too many orthogonal fields burden authors | Incomplete or unreliable metadata | Progressive authoring prompts, defaults by activity role, and lint with actionable errors. |
| "Interactive" is treated as inherently better | Manipulation without constructive thought | Require an overt evidence-producing or preparation role for each interaction. |
| Feedback leaks assessment content | Invalid sitting and corrupted evidence | Runtime-controlled mode and disclosure state remain authoritative. |
| Alternate controls change the construct | Incomparable evidence | Claim-preservation review, subject expert review, and accessibility testing. |
| Open responses receive confident machine scores | False correctness and learner harm | Pending-by-default state and explicit authorized review action. |
| Test fidelity drifts as programs change | Misleading readiness claims | Versioned official blueprint, access date, mappings, and revalidation trigger. |
| Context-rich transfer adds irrelevant burden | Measures reading, culture, or tool familiarity instead | Audit prerequisite demands and offer construct-preserving access supports. |
| Reflection becomes surveillance | Reduced trust and unnecessary sensitive data | Local, optional, purpose-limited capture with deletion and exclusion controls. |
| Legacy enhancement changes meaning silently | Prior evidence no longer comparable | Preserve identity and old version; require semantic diff and revalidation. |

## Bottom line

The comprehensive design space does not require a correspondingly large set of
item types. itembank should represent why the learner acts, what cognition and
subject practice the objective requires, what observation can support a limited
claim, how the learner may respond, what feedback is allowed, and who may score.
Prediction, noticing, reflection, hinting, staged reveal, timing, simulations,
and rich diagrams are usually activity, stimulus, feedback, or administration
semantics. Selection, entry, annotation, ordering, construction, speech, and
performance are response families. Only the response families that need a stable
new response and scoring contract should pressure the parser.

This distinction preserves instructional variety, accessibility, portable lesson
files, deterministic authority, and standardized-test fidelity while leaving the
Phase 17 visual system free to render the same semantic activity well across
desktop, narrow screen, touch, keyboard, screen reader, offline, and plain-file
contexts.
