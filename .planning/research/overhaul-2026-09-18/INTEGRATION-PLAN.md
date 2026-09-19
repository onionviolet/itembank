# Combined ecosystem overhaul integration plan

Date: 2026-09-18. Owner: root integrator. Status: proposed integration sequence.
This plan does not establish feature parity or authorize a production rollout.

Authority: [the user's request](../../USER-VISION.md#2026-09-18-combined-ecosystem-feature-and-teaching-overhaul).
[Refined prompt and operation scope](BRIEF.md).

## Outcome and evaluation rule

Build one coherent course workspace that supports strong teaching, useful
practice, reliable return, and inspectable course creation. Compare named tasks,
not product-wide feature totals. The older LMS research and newer competitors
are complementary inputs. Institutional breadth is not the parity denominator
for this single-learner product, but useful institutional UI patterns remain
eligible regardless of whether the full platform is adopted.

Parity means a named task is reachable, usable, durable where appropriate,
recoverable and accessible in the actual app. A source symbol is implemented
foundation evidence. A fixture is prototype evidence. Neither alone earns task
parity. An advantage requires a demonstrated improvement on the same task and
an explicit account of added authoring and maintenance cost.

## Evidence owners

| Input | Role |
| --- | --- |
| [LMS flows](LMS-FLOWS.md) | Mature navigation, course structure, assessment completion, offline and return workflows |
| [Competitors](COMPETITORS.md) | Source-to-learning workflows, authoring, notes, review, jobs and candidate coverage |
| [Interactive teaching](INTERACTIVE-TEACHING.md) | Explainer production, visual primitives, teaching examples, dependencies and effort |
| [Itembank baseline](ITEMBANK-BASELINE.md) | Current source observations B1-B12 and limits |
| [Existing UI renewal](../ui-renewal-2026-09-18.md) | Visual and interaction candidate, prior browser evidence, separate production boundary |

All recommendations below are proposed. Existing contracts and implementation
remain current until a bounded migration changes them.

## Findings reconciled across lanes

| Finding | Evidence and disagreement | Integrated decision |
| --- | --- | --- |
| R1 Full flow outranks a screen inventory | Competitor C4 spans source, notes, creation, practice and recovery. The renewal showcase demonstrates presentation but not those durable tasks. Baseline B1-B3 confirms continuity gaps. | Use P1 as the first real connected unit, then retain every broader workflow in P2-P5. A completed P1 does not close full feature parity. |
| R2 Useful LMS patterns survive deployment differences | Older research parked LearnHouse and Open edX institutional deployment. Competitor C2/C3 identifies course editing and versioning patterns that remain useful to one learner. | Preserve deployment dispositions while evaluating their learner and author workflows now. Do not use an institutional label to dismiss UI evidence. |
| R3 Rich teaching needs production tools and content craft | Interactive F1 and D1 separate the engine, semantic artifact, author preview, reviewer and transfer task. Baseline B5/B6 confirms native stages and one comparison already exist. | Reuse those foundations in P1. P2 adds reusable linked representations plus author validation and preview. A slider is not proof of Brilliant-quality teaching. |
| R4 First-slice preferences differ | Competitor C6 favors exact source occurrence plus notes. Interactive D3 favors a new finite scene. Earlier renewal favors shell migration. | P1 exercises existing source/scene/practice under one integrated shell to expose cross-surface failure first. P2 then proves author reuse. Exact text-selection assistance is a distinct P4 dependency, not implied complete by P1 source return. |
| R5 Current references have changed | Reports document current source paths, changed repository locations and broader public Brilliant/NotebookLM claims. These are documentation/source observations, not signed-in trials. | Preserve the user's selected experience. Refresh only claims needed by each implementation packet and run a same-task live comparison before comparative acceptance. |

The candidate coverage registers in the three reports jointly own the combined
list. Documentation-only or historical candidates remain labeled. No full
product was installed or trialed during this pass. Earlier live observations
remain dated evidence and are not multiplied into independent confirmations.

## Shared integration architecture

Use existing course, graph, source, reading, notes, director, journal, retention,
runtime and evidence owners. Enrich their public projections where the UI lacks
the information to complete a task. The renewed presentation consumes these
projections and dispatches through existing operations.

Separate color tokens from legacy layout rules. Choose one complete document
style stack for each migrated surface. Use the same explicit course context,
active destination, task title and primary action across shelf, course, reader,
question, result and operations. The installed Tauri container continues to
load the local daemon. Package new assets in every distribution path.

Teaching content remains a readable accepted artifact. A trusted renderer turns
validated authored interaction data into a richer view. Each capability declares
its version, supported parameters, meaning, fallback and input methods. Reuse
the existing capability registry and parser extension seams. Do not introduce a
second lesson parser or a general expression evaluator disguised as diagram
configuration. Execution-capable lessons retain a separate reviewed runner.

Temporary control state, saved presentation position, learner notes, authored
content, model proposals and assessment responses are different objects.
Persist only under their proper owner. Opening a diagram is not a scored
response. A generated explanation is not automatically an accepted source.

## Five workstreams and sequence

| Packet | Observable result | Main seams | Dependency and disposition |
| --- | --- | --- | --- |
| P1 Connected unit | Home resumes the actual activity. One unit connects source, existing explainer, practice, runtime result and return under the renewed shell. | IA, daemon course composition, presentation/theme, reader/quiz context | Proposed next slice under existing Core flow obligations and IL-20260907-02. Detailed below. |
| P2 Teaching components and author preview | An author can create, validate, preview and revise a linked diagram and explanation from a portable artifact. A second lesson reuses the same component. | Existing lesson grammar, capability registry, trusted rendering, media and preview owners | Prototype under existing lesson-capability obligations. Start after P1 establishes the real rendering route. |
| P3 Broader activity depth | Code prediction, trace, repair, construction and appropriate table/order/visual/written tasks work with meaningful feedback and retained context. | Runtime public items, shared question presentation, runner, CS Dojo and D1/D2 work | Existing activity owners IL-20260906-09 and IL-20260912-02. Use P2 components when relevant. Execution and new scoring contracts each need their own gate. |
| P4 Course author workbench | Selected sources become a reviewed objective/treatment proposal and one accepted editable lesson. Interrupted work resumes and revision/undo are visible. | Director checkpoints, source adapters, course operations, Build/review and journal | Existing course-authoring scope. May develop after P1 with P2 as the rich output target. Grounding and accepted writes remain existing-owner operations. |
| P5 Review and delivery | Unit review exposes due work, source-linked errors and pending marks. A course restores offline with named losses. | Retention/Study, evidence reports, package/restore and source reading | Existing review/package obligations. Preserve FSRS and prior restore work. Exact source passage cursor remains a separate proposed extension. |

This is dependency sequencing, not five parallel production writers. Only P1 is
expanded into a ready implementation packet. Later workstreams retain broad
seeds until their preceding task evidence exists.

**Promotion triggers:** after P1 passes its native task gates, audit the visible
P4 authoring and reader-help journeys and select the next failing user task.
Publish that one bounded packet. Basic grounded authoring does not wait for P2
diagram completion. P2 advances when an objective needs linked representations
beyond the existing comparison. P3 advances when a specific code or response
task is unsupported or its current treatment fails the learner comparison.
P5 advances when the integrated unit reaches review or a real export request.
Missing live competitor access delays a comparative claim, not useful native
integration with an independently observable acceptance gate.

## Rich teaching and authoring seeds

P2's first new candidate is a bounded slope/intercept scene linking a plot,
equation, numeric controls, text and table. The author declares the objective,
misconception, variable bounds, source, explanation stages, fallback and
transfer prompt. The learner predicts, changes one quantity, observes the
linked consequences and attempts a changed problem without the control.
Use original synthetic material for the prototype. The interactive report
specifies math, code and non-STEM examples so the architecture is not built
around sliders alone.

Start with trusted HTML/SVG components and the existing math path. Evaluate
selective D3 and editor packages only where the exemplar removes substantial
custom work. Full H5P, LiaScript or graphing-engine integration remains a
named-consumer prototype with its own lifecycle and compatibility trial.
Sketches and raster illustrations can support a lesson, but do not replace
semantic labels, inspectable quantities or accessible controls. Decorative art
has a separate rights and asset record. No generated artwork is needed to
complete this planning pass.

The author route must show plain and rich previews, block-located validation,
an editable source, a bounded revision diff and recoverable acceptance. For a
second lesson, change content and parameters without editing renderer code.
That reuse demonstration is P2's platform gate. Test the transfer prompt
separately to assess whether the interaction helps the learner.

P2's learner-quality gate requires linked representations, a prediction before
revealing consequences, and unassisted transfer compared with a simpler
treatment. Record conceptual errors and navigation burden. Accept the portable
artifact with its expected fingerprint through the existing atomic journal
operation, then reopen the accepted revision. A successful preview alone does
not close that acceptance boundary.

P3 preserves the current D1/D2 experiment and CS Dojo owner. Add source-linked
state tables before executable trace animation if that satisfies the task.
For authentic coding tasks, audit and extend `runner.py` first. Its time and
output bounds do not establish isolation. Compare any browser engine against
the existing runner on cancellation, draft recovery, resource limits and
allowed capabilities before selecting it. Do not require a trace for a task
whose objective is to execute or construct a program.

The interactive report's 15 to 40 engineering-day execution range describes a
new bounded capability in general. It is not an estimate of Itembank's remaining
runner work. Audit current isolation and capabilities before estimating that
incremental effort.

P4 includes grounded reading assistance as well as creation. Select the second
occurrence of repeated text, resolve it to the accepted revision, restrict
context to chosen sources, inspect citations, save and edit a learner note,
then restart and reopen its anchor. Generated summaries and notes must remain
distinguishable from originals in context selection. This supplies the tested
grounding boundary for lesson generation and correction. Reuse the prior
DeepTutor prototype's fixes without treating it as production integration.

Fail the source-help seed on a wrong repeated-text occurrence, stale bytes,
excluded material entering model context, lost draft after model failure, or
an anchor that cannot reopen. A model outage must retain the source and note.

P4's creation task then reviews an outline, retains a direct reading, drafts one
missing lesson, corrects a single semantic block, previews it and accepts a
revision. Stop and resume a job through existing director checkpoints. Retry
must not duplicate accepted artifacts. A source revision marks dependent drafts
stale. Retain proposals, job status and an undo route through failure.

The correction gate changes one claim while preserving unrelated content,
checks source citations versus synthesis, cancels and restarts, accepts against
the expected source and artifact fingerprints, then restores the preceding
accepted revision. Show affected artifacts after source changes. This is the
P4 observable task, not a promise that every backend already supports it.

P5's progress view separates viewed, learner-reported read, attempted, scored,
pending review, due review and course requirements. Use known source/objective
links for remediation. A completed content list is not proof of mastery. Export
and restoration must preserve the richer lesson's canonical assets or report
the loss. Notes and optional history keep their existing explicit export grants.

### Effort and maintenance

The interactive report estimates 3 to 7 engineering days for a finite-scene
prototype, 10 to 25 for a production capability plus author preview, and 2 to 5
author days plus review for a 10 to 20 minute lesson using existing primitives.
These are unmeasured human-effort planning ranges under its stated assumptions,
not an agent runtime or calendar estimate. They are not additive and should not
be applied wholesale to extending already implemented pieces. Measure P1 and
the first two authored lessons before forecasting a library of lessons.

Every new capability needs one maintenance owner, versioned local assets,
representative content and compatibility checks. Conceptual review of a lesson
and a renderer regression are different work. AI drafting can reduce writing
time but does not prove mathematical correctness or instructional quality.

## P1: first implementation packet

**User-visible result:** a synthetic course unit opens in the real daemon with
the renewed layout. It has a source passage, the existing finite comparison,
a runtime-backed practice sitting and a result that returns to the unit. A
returning learner resumes the same saved sitting directly from the shelf.

**Owner:** learner-flow integration under the current Phase 20 presentation and
course owners. One writer implements P1 after refreshing the shared dirty tree.
The existing showcase remains the visual reference. Use a new isolated worktree
only after arranging which required uncommitted baseline changes it must carry.
A worktree from HEAD alone would omit today's foundation work.

**Settled scope:** one synthetic unit, one existing explainer capability, one
existing assessment mode, all screen states on that journey. No new lesson
grammar is needed for P1. Use current authored objectives and treatment links.
If a unit has no intended next treatment, show explicit choices. Do not infer
an educational sequence from directory order.

**Exact edit seams:**

1. `surfaces/ia.py::_course_resume_cue` and `_healthy_card`: expose a structured
   projection of an existing eligible sitting with stable session identity,
   mode, position and destination. Keep unreadable, complete and absent states
   distinct. Reordering courses must not select a different saved sitting.
2. `surfaces/daemon.py::_course_area_rows`, `_course_frame`,
   `_course_shelf_body` and existing saved-session routing: render linked
   treatments and validated resume destinations through current course roots.
   Carry resolved course identity through activity and report requests.
3. `surfaces/presentation.py::surface_shell` and
   `surfaces/theme.py::theme_css`: introduce a token-only color path and an
   explicit document presentation selection. Preserve existing stored appearance
   choices. Do not merge legacy layout sheets into renewed documents.
4. Reader, quiz and report assembly: use explicit parent context with the
   existing public payload. Preserve question feedback until explicit Next,
   return from source help, pending prose and delayed exam disclosure. An
   ambiguous parent returns to a course chooser rather than guessing ownership.
5. Package inventory and tests: reuse existing asset directories where possible.
   Verify both zipapp and desktop packaging include every changed asset. Update
   visual assertions only where the approved candidate changes appearance.

**Resume selection:** preserve the learner's explicitly chosen sitting when
available. Otherwise show eligible active sittings with exact labels if more
than one remains. Do not manufacture a single winner from an ambiguous state.
Completed sittings open their report. Invalid/stale sittings offer recovery
without starting a replacement automatically. A draft not durably saved must
be labeled truthfully before exit. Reading cursor persistence is outside P1.

**Acceptance tasks:**

| ID | Task | Pass evidence | Failure condition |
| --- | --- | --- | --- |
| T1 | Open course, choose the unit, inspect its source, manipulate the existing comparison, enter practice | Same course and unit remain recognizable across every screen. Source return restores the originating view within this journey. | Dead action, wrong treatment, hidden available content or loss of course context |
| T2 | Answer, inspect feedback, leave, restart daemon and resume | Same session, cursor, mode, response history and question identity. No duplicate evidence from Back or reload. | A new sitting is silently created or shelf ordering chooses another one |
| T3 | Finish and reopen result, including pending or withheld cases | Runtime totals and pending counts agree with report. Back to unit is visible. | Client-only miss list invents correctness, pending work displays as failure, or gated content leaks |
| T4 | Complete the journey with keyboard, narrow layout and script disabled | Equivalent supported task and explanation, predictable focus, readable layout, explicit Next | Essential action depends on hover/drag/script or renewed CSS obscures controls |
| T5 | Run packaged daemon and inspect installed desktop at normal/minimum sizes | Same assets, destinations and interaction semantics without development server or network fetch | Source checkout works but distribution omits assets or runtime recovery uses a broken layout |

**Targeted checks:** extend `tests/course_resume_roundtrip.py` with exact route,
ambiguity and restart identity assertions. Use `course_shell_roundtrip.py`,
`ia_route_roundtrip.py` and `presentation_profiles_roundtrip.py` for shared
context. Exercise affected serve, lesson, hint and JS suites when those render
paths change. Preserve `lesson_interaction_roundtrip.py`. Run packaging gates
after asset changes and full preflight once at the resulting implementation
revision. Use generated, browser and installed observations as separate evidence.

**Migration and recovery:** keep the old presentation selectable during staged
integration. Switching presentation must not change canonical course or session
bytes. New projections need no evidence migration. If implementation discovers
a required durable format change, split that proposal into its owning packet
before proceeding. Remove only P1's style selection and assets to restore the
prior presentation. Never reset the shared dirty checkout.

## Parity and advantage demonstrations

Use the same synthetic objective, source scope and intended task in applicable
reference products. Record model/setup differences and mark unsupported tasks
explicitly. Do not compare total feature counts or call a missing live trial a
pass. For P1, obtain direct task observations from at least one mature LMS and
one source-to-learning competitor before calling the journey competitive.

For P2, a reviewer authors a second changed-content lesson using the same
primitive. Record preparation time, correction time, configuration reuse and
fallback quality. A hand-coded one-off is useful prototype evidence, but it
does not establish the authoring system is ready.

Potential advantages are hypotheses: an explanation can return to an exact
accepted source revision, a rich lesson can remain useful offline and in plain
text, a practice error can lead to the relevant source without losing state,
and a learner can inspect and reverse an accepted course change. Demonstrate
these tasks before describing them as superior to a named competitor.

## Verification record

### Assessment follow-up

The [question display review](QUESTION-DISPLAY-REVIEW.md) adds installed-app
observations, a rendered synthetic multi-select retry and explicit limits.
Q1/Q2 gate P1 on reliable controls and question-first layout. Q3/Q4 refine P3
with misconception feedback, annotations, rich stimuli and reasoning tasks.
Q5 strengthens P2's transfer gate. The [assessment audit](ASSESSMENT-AUDIT.md)
separates server-native, API-driven and static clients. Predicted API defects
need reproduction, not classification as installed-app failures. The
[pattern register](QUESTION-PATTERNS.md) retains further candidates and current
official references. This follow-up does not authorize production fixes.

### Original overhaul verification

All three requested Astra low lanes completed their named reports. Root read
the reports and checked the current native seams recorded in the baseline.
Two lanes independently reviewed the initial plan. Their corrections added
P2 learner-quality and atomic-acceptance gates, explicit grounded-help and
single-claim correction tasks, runner-effort qualification and promotion
triggers. The LMS lane filled omitted historical candidate routes. No agent
reported a live competitor trial or production implementation in this pass.

The research directory contains six Markdown artifacts. A local link check
resolved all 26 local links and found no missing target, conflict marker or
em dash. Prose scans and `git diff --check` passed. The new files are untracked,
so their link/prose checks were run directly rather than relying on Git diff.

`python3 scripts/preflight.py --quick` passed every enabled gate. Full Python,
JavaScript and clean-tree checks were deliberately skipped for this research
change. These results do not establish application parity or validate the
proposed implementation.

`python3 scripts/vision_audit.py` completed with no missing dated
interpretations, planning effects or inbox dispositions. The new request has
an exact downstream link. Existing report totals still include 10 unresolved
named files, 4 ambiguous roots, 10 missing relationship fields, 60 entries
without verified downstream links and one unresolved local vision link. Those
legacy records were not repaired by this bounded planning pass.

No production files, dependencies, learner sources, banks, scores, installed
application, branch, commit or remote were changed by this task. Existing
concurrent changes remain present. The new research, exact vision capture and
one existing-ledger routing entry are the complete write scope.

Human visual preference, real course success, live competitor comparisons,
accessibility acceptance and learning benefit remain open. The next concrete
implementation is P1 with T1-T5, followed by the promotion rules above.
