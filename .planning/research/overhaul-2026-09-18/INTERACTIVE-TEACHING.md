# Interactive teaching and non-MC task production

Date and primary-source access date: 2026-09-18. Status: research and proposed
design, not an accepted format or implementation claim. Scope: the interactive
teaching lane in [BRIEF.md](BRIEF.md). No production code or course content changed.

## Findings and evidence boundaries

**F1. The target is a repeatable lesson-production capability.** A diagram
engine supplies drawing and input mechanics. An author still has to choose the
misconception, model, sequence, revealing example, counterexample, question,
feedback and transfer task. “Brilliant-quality” should mean that a learner can
predict, change a meaningful variable, see coordinated representations, explain
the result and transfer it to a fresh problem. Attractive motion alone meets
none of those gates. This is a proposed design criterion, not an efficacy result.

**F2. Itembank already has useful foundations.** Current source inspection of
`surfaces/lesson_interaction.py` found `render(data, inline)`, static meaning
before controls, a bounded integer comparison, reset, linked meters and text,
and a hypothetical-value label. It executes trusted fixed renderer code, not
authored code. It does not score or persist. The current
[absorption record](../competition-2026-09-08/ABSORPTION.md) explicitly adds native
guided progression and optional detail after its earlier prototype-only rows.
The root lane owns the full current mapping. This report does not call finite
interaction or progression missing.

**F3. Existing code-depth work must be continued, not recreated.** The
[audit](../code-question-depth-audit-2026-09-16.md) defines D0 faithful source,
D1 orientation, D2 state tracing, D3 manipulation and D4 construction. The
[current prototype README](../../../prototypes/code-question-depth/README.md)
describes a counterbalanced D1/D2 human comparison with committed predictions,
blank learner-filled traces and human-review fields. It explicitly removed
the former browser key and checker. This is prototype evidence, not proof of
learning benefit or production execution. This lane read those files and the
small interaction module, not whole parser, scorer or lesson-renderer modules.

**F4. Current Brilliant public positioning is broader than the older visual
benchmark.** Its homepage now advertises Koji, visual interactive sessions and
adaptive practice. Its FAQ describes interactive problem solving. These are
official product claims, not a private-course trial or evidence of internal
technology. The user's September 8 vision explicitly retains direct
manipulation without conversational presentation. Absorb that chosen learning
pattern without silently adopting the new conversational product direction.
[Brilliant homepage](https://brilliant.org/),
[FAQ](https://brilliant.org/faq/). Evidence class: official marketing, fetched
2026-09-18. No claim about Brilliant's renderer, authoring tools or comparative
learning gains is supported here.

## Primary evidence and candidate routes

All rows were refreshed on 2026-09-18. “Docs” establishes documented capability,
not successful Itembank integration or accessibility acceptance.

| Candidate | Observed primary evidence | Proposed route and limit |
|---|---|---|
| LiaScript | Its [official compendium](https://raw.githubusercontent.com/LiaScript/docs/master/README.md), version 36 dated September 9, 2026, describes Markdown enhancement, quizzes, animation and browser-local offline use. Docs. | Registered authoring reference. Reuse semantic staging and readable source. Full interpreter remains a prototype option because scripts, imports, quiz authority and packaged dependencies require a separate adapter audit. Earlier local LiaScript progression trials remain dated evidence. |
| H5P | [Content catalogue](https://h5p.org/content-types-and-applications) includes branching, hotspots, image comparison and varied response forms. Its [April 2026 accessibility matrix](https://help.h5p.com/hc/en-us/articles/7505649072797-Content-types-recommendations) distinguishes content types, exceptions and maintenance. Docs and vendor conformance statement. | Prototype one named content type only after a real lesson needs it. Check its exact library version and license. Do not infer all H5P content is accessible or adopt an external score as Itembank truth. A package ecosystem is useful but adds upgrade, export and renderer responsibilities. |
| Runestone / Parsons | [Author guide](https://runestone.academy/ns/books/published/authorguide/directives/parsons.html) documents code blocks, ordering and indentation. [Dependency variant](https://author.runestone.academy/ns/books/published/overview/Assessments/parsons.html) describes dependency-based solutions. Docs. | Registered response-family reference. Prefer semantic order/dependency constraints over one arbitrary permutation. Transfer must include writing or repairing code without blocks. A polished sorter alone does not establish program understanding. |
| Python Tutor | [Official product page](https://pythontutor.com/) describes stepwise variables, objects, pointers and stack frames. Public product evidence. | Registered visual grammar reference for trace, stack and heap views. Reuse the representational idea with original content. No hosted upload, embedding license, execution isolation or offline availability was verified. |
| Desmos | [API v1.11](https://www.desmos.com/api/v1.11/docs/index.html) documents graphs, expressions, sliders, state and an API-key script load. Docs. | Prototype adapter when a task needs a real graphing calculator. Native finite SVG is the default for small teaching scenes. Treat key terms, remote loading, licensing and offline packaging as unresolved before adoption. Preserve a numerical/text task when unavailable. |
| SVG | [W3C SVG 2](https://www.w3.org/TR/SVG2/) specifies the vector document vocabulary. Standard. | Core drawing candidate for finite diagrams. Put controls in semantic HTML and use SVG for linked geometry. A vector graphic is not automatically an accessible learning activity. |
| D3 | [Official introduction](https://d3js.org/what-is-d3) describes a low-level visualization toolkit. Docs. | Registered, selective modules for scales, paths or data joins when hand-coded geometry becomes costly. D3 does not supply pedagogy, semantic tasks, scoring, persistence or accessibility by itself. |
| KaTeX / MathJax | [KaTeX options](https://katex.org/docs/options) includes HTML/MathML output and trust controls. [MathJax accessibility](https://docs.mathjax.org/en/latest/basic/accessibility.html) documents exploration and speech support. Docs. | Reuse Itembank's current math path first. Evaluate either renderer against actual expression and assistive-technology fixtures before changing it. Mathematical typesetting does not check mathematical equivalence. |
| CodeMirror | The [official development repository](https://github.com/codemirror/dev) states that it moved to code.haverbeke.berlin and directs consumers to separate packages. Repository evidence. Direct website fetches failed in this pass. | Registered editor component for justified D3/D4 work. An editor is neither execution nor grading. Verify the current upstream, pin and package provenance at integration time. The archived GitHub mirror is not evidence of abandonment. |
| Pyodide | [Worker guide](https://pyodide.org/en/stable/usage/webworker.html) documents running Python off the main thread and communicating across the worker boundary. Docs. | Prototype execution capability only after D1/D2 trials show a need. A worker protects responsiveness but is not a complete hostile-code security boundary. Network, JS interop, packages, resource limits and teardown require explicit tests. |

These sources establish available mechanisms. None establishes that installing
one of them produces a high-quality lesson or improves transfer. No third-party
source code, lesson artwork, proprietary exercise or package was copied here.

## D1: Build a semantic production pipeline

The accepted Markdown and referenced local assets remain canonical. HTML,
layout, calculated diagram state and previews are disposable derivatives.
Start by extending the existing lesson model and parser at demonstrated seams,
not by adding a second Markdown interpreter or a general executable scene DSL.

| Stage | Required authored or platform output | Acceptance gate |
|---|---|---|
| Author intent | Objective, prerequisite, cited source, teaching role, misconception, intended action, transfer check and rights | Author explains why interaction helps this specific objective. Reuse adequate existing material first. |
| Semantic draft | Stable block IDs, capability/version, named variables and units, bounds, initial state, allowed actions, linked views, textual explanation, fallback, disclosure class | A readable Markdown lesson survives without enhancements. No arbitrary script or key in a lesson view. |
| Validate | Existing parser plus capability-specific schema, references, units, bounds, labels, unreachable states, resource budget and fallback checks | Deterministic errors locate the block. Unknown future capability gives an explicit unavailable state with useful fallback. |
| Preview and review | Plain Markdown, rich narrow/wide view, print, keyboard sequence, touch controls, screen-reader reading order, no-script mode and bounded source diff | Subject reviewer checks conceptual correctness. Representative users review task equivalence and accessibility. Automated checks do not self-certify acceptance. |
| Accept portable artifact | Accepted revision/fingerprint, assets and dependency manifest, review record and operation journal | Compare-and-swap rejects stale bases. Atomic acceptance preserves the prior valid revision. A changed dependency marks previews stale. |
| Render and maintain | Trusted renderer selected by declared capability, reset, explicit save/resume semantics and static fallback | Offline opening and clean restore name any losses. Renderer upgrades replay a small golden corpus before publishing new derivatives. |

This is a proposed pipeline, not an invented claim that those fields already
exist in Itembank's format. Prototype new semantics with synthetic fixtures
before accepting a durable grammar. Content ownership belongs to the course
builder and reviewer. Renderer and schema maintenance belongs to the lesson
platform owner. Learner draft state remains separate from accepted content.

## D2: Separate finite scenes from execution

**Finite declarative scenes, core direction.** Start with bounded values,
enumerated stages and reviewed transformations implemented by trusted code.
Useful reusable primitives are quantity comparison, number line, coordinate
plot, point/table linkage, fraction/area partition, timeline, directed relation,
step/state table, block ordering and annotation selection. Register a primitive
only after a lesson needs it. A common state model links the same value or
entity across diagram, equation, prose and table. Labels and units stay stable.
Changing a control must make the causal relationship visible without requiring
the learner to remember a prior screen. Provide reset and comparable states.

**Sandboxed simulations or learner code, prototype direction.** Use a separate
capability manifest and execution adapter with declared language/version,
allowed packages, network policy, resource budget, output limit, cancellation,
seed and reproducible input. Keep secrets and keys outside the sandbox. Kill a
run without losing the draft. Treat browser results as untrusted when they
affect assessment. Do not claim deterministic reproduction for unrestricted
floating-point or asynchronous programs. Multi-file projects and arbitrary
packages remain backburner until isolated execution and restore are proven.

**Assessment authority.** Exploration can display the public consequence of a
public model. It must not display a protected expected trace, solution geometry
or hidden test before the runtime releases it. Responses submit structured
data to the existing runtime, which alone settles correctness and evidence.
Extend that authority additively when a new response family is justified.
Branching narrative completion, moving a slider, running code and passing one
visible example are not mastery. Explanations and arguments remain pending
human review or explicitly provisional advice. An H5P event or external test
result cannot silently become a settled mark.

**Accessibility and portability.** Use named HTML inputs alongside graphical
handles, increment/decrement or move-up/down controls alongside dragging, and
tap/focus equivalents for hover. Preserve focus through updates. Announce
meaningful committed changes rather than every animation frame. Pair shapes
and colors with text labels. Respect reduced motion and forced colors. A
screen-reader user must be able to inspect the same relationships through a
table or ordered description and perform an equivalent task. Static snapshots
must include values, units, causal explanation and a worked or learner-fillable
table. When interaction is the construct, disclose what the static form cannot
assess instead of pretending identical measurement.

## Three proposed exemplar specifications

These are original synthetic design specs, not course artifacts or keyed bank
items. They need source binding and subject review before course acceptance.

| Spec | Authored scene and learner sequence | Non-MC response and authority | Transfer and fallback gates |
|---|---|---|---|
| E1 Math: slope and intercept | Link `y = mx + b`, a coordinate plot and a three-row table. Bound `m` to integers from -3 to 3 and `b` from -4 to 4. First predict which points move when only `b` changes. Commit the prediction, then adjust a named numeric control and inspect both states. Stage the explanation of change versus starting value. | Enter two coordinates or complete table cells. Runtime checks permitted numeric responses against the authored model when this is an assessment. The exploration view does not carry a protected target line. A free explanation remains pending. | Give a fresh table without the slider and ask for a line or rule. Include a negative slope and changed axis scale. Compare with a static worked-example treatment. Plain form contains axes described in text, the same table, initial/changed snapshots and instructions to calculate values. |
| E2 Code: accumulation versus replacement | Preserve a short loop's indentation and line IDs. Learner predicts output before opening a blank trace with iteration, current value and accumulator. D2 lets them fill states. Later D3 offers line reordering or a one-line repair only if the existing D1/D2 trial supports escalation. Link selected trace row to source line and variable labels. | Output prediction and trace cells submit to runtime. Accept semantically equivalent ordering when dependencies allow it. Do not import the removed browser checker. No execution is required for the first comparison. | Present a different loop and ask for prediction without the trace. Then ask for a small repair or function without blocks. Human review checks the first mistaken state and explanation. Plain source and an empty state table remain a complete task. Reuse the current prototype's counterbalanced protocol. |
| E3 Non-STEM: evaluate a historical causal claim | Provide three short synthetic source cards with date, author position and provenance. Show an event timeline and a claim/evidence map. Selecting a card highlights its event and the claim it is offered to support. Learner assigns cards to support, challenge or insufficient, then drafts a causal explanation and an alternative. | Classification is scored only where an authored, reviewed rubric makes the relation determinate. Ambiguous evidence and argument quality stay pending review. The map does not certify causation from temporal order. | Use new source cards containing a conflicting account and a plausible common cause. Require a short argument without the map. Static form uses a dated table and claim/evidence matrix. Keyboard list controls replace drag. Evaluate source use and causal reasoning, not agreement with a single story. |

For each exemplar, measure conceptual errors, successful unassisted transfer,
time and navigation burden separately. Use matched tasks and counterbalanced
order to reduce practice effects. A small formative trial identifies defects
and learner preferences. It does not justify a general efficacy claim. Delayed
transfer and a larger study would be needed for stronger learning claims.

## D3: Choose the smallest maintained implementation

| Choice | Fit and disposition | Cost driver and revisit trigger |
|---|---|---|
| Native HTML/SVG finite primitives | Proposed core for the first linked-representation slice. Reuse current lesson progression, parser and comparison patterns. | Itembank owns geometry, schemas and accessibility. Revisit when several scenes repeat difficult scales/layout or exceed bounded models. |
| Selective libraries | Registered D3, current math renderer and editor components behind narrow adapters. | Pins, licenses, bundles and browser regressions. Adopt only when a representative lesson demonstrates less custom complexity and passes offline/accessible tasks. |
| Full external engine | Prototype LiaScript/H5P/Desmos adapters for a named content consumer. | Parallel content grammar, lifecycle, scoring, dependencies and portability. Promote after one package survives offline open, keyed-disclosure audit, export/restore and human review. |
| General simulation or code engine | Prototype Pyodide-style bounded execution. Multi-file arbitrary package execution is backburner. | Isolation, resource control, package supply chain and reproducibility. Revisit after code-depth evidence demonstrates a task that cannot be served by trace or finite manipulation. |

The first useful platform slice is one linked finite scene plus author
validation, plain/rich preview and a transfer task. E1 is an illustrative
candidate, subject to root's live-code and active-owner reconciliation. It is
not authorization to build a new framework or duplicate an existing widget.

## Effort assumptions, not measured costs

Ranges below are planning estimates in person-days of focused work. Assume one
experienced engineer, an available subject author and a reviewer, reuse of
existing parser/runtime/UI infrastructure, and no procurement or major migration.
They are not calendar promises. Repository surprises and human scheduling can
increase elapsed time. The rows are separate scope options, not additive phases.

| Deliverable | Plausible range | Included and excluded |
|---|---:|---|
| One finite-scene vertical prototype | 3 to 7 engineering days | One synthetic scene, schema experiment, linked views, fallback and focused checks. Excludes production acceptance and efficacy study. |
| Production first capability and author preview route | 10 to 25 engineering days plus 2 to 5 reviewer days | Validation, migration decision, packaging, runtime boundary, recovery and representative interaction tests. Does not create a lesson catalogue. |
| Small family of 4 to 6 reusable capabilities | 25 to 60 engineering days plus review | Shared state and rendering rules, docs/examples and compatibility corpus. Demand for a generic expression engine can exceed this range. |
| Bounded execution capability | 15 to 40 engineering days plus security review | Runner lifecycle, package policy, cancellation, draft recovery and adversarial tests. Excludes multi-language service or arbitrary projects. |
| One 10 to 20 minute lesson using existing primitives | 2 to 5 author days plus 0.5 to 2 review days | Source analysis, storyboard, several tasks, fallback, misconceptions, transfer and one revision. Bespoke art or a new primitive adds engineering and can make the lesson 5 to 15 or more days. |

Maintenance requires a named owner for each capability, pinned assets, a
representative lesson corpus and periodic browser/assistive-technology checks.
Reserve a provisional 10 to 20 percent of delivery capacity for defects and
dependency updates until actual maintenance data replaces that assumption.
Content revisions need source and conceptual review independently of engine
updates. Generated drafts reduce some writing effort but cannot certify
diagram correctness, pedagogical sequencing, rights or accessibility.

## Handoff and unverified gates

This lane refreshed public primary sources, inspected the small finite
interaction implementation, reconciled the later progression record and read
the existing code-depth prototype/audit. It did not run private Brilliant
courses, live external demos, production fixtures, browser accessibility tests,
learning trials or repository preflight. Documentation fetches are not rendered
interaction verification. Root owns link checks, final proposal reconciliation
and project gates. No engine choice, estimate or exemplar is an accepted
requirement. Undo is removal of this new report without touching concurrent work.
