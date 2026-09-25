# Distinctive app craft and useful interaction

Date: 2026-09-25. Owner: UI renewal root integrator.
Status: researched, highly changeable WIP. This report preserves the research
direction. The user's later implementation request is tracked in
[the implementation record](IMPLEMENTATION.md), including production changes
and verification. Human visual acceptance is not claimed.

Authority: [the user's exact direction](../../USER-VISION.md#2026-09-25-distinctive-app-craft-and-interaction-research).
This extends the existing [UI renewal owner](../ui-renewal-2026-09-18.md)
and [overhaul integration plan](../overhaul-2026-09-18/INTEGRATION-PLAN.md).

## Result

Itembank should develop a recognizable learning environment through the way
sources, explanations, learner work, and feedback relate to one another.
Visual character and dependable behavior both matter. A palette substitution
or extra animation alone would not meet the user's request for depth.

The recommended comparison is a scholarly reading workspace with precise
contextual tools versus a more expressive learning workshop. Use identical
content and behavior in both. Keep the existing style as the baseline.
This is a Prototype recommendation. It does not freeze typography, density,
illustration, color, or any previously accepted provisional direction.

## Evidence and limits

The [Reddit report](REDDIT.md) covers seven discussion pages with sampled
comments, including disagreement. The [product craft report](PRODUCT-CRAFT.md)
covers seven official product and platform sources. The
[interaction report](INTERACTIVITY.md) covers eight design, research, and
accessibility sources, plus one bounded public browser interaction.

Access date for all sources is 2026-09-25. Publication dates and actual reading
scope are recorded in the reports. Reddit is anecdotal, self-selected input.
Product makers describe their own choices. The papers and professional UX
guidance provide different evidence from a Reddit opinion. None proves that a
particular Itembank redesign will improve learning.

Earlier in this task, the installed desk was visually inspected. At its current
window size, a large inspirational heading and plant illustration dominated the
first view, with the course collection below it. Targeted source inspection
also found overlapping style layers and repeated generic composition.
That was a bounded observation, not an app-wide defect or accessibility audit.
Other work is changing source concurrently. Recheck source and installed parity
before implementation, rather than treating this snapshot as a release verdict.

The new live reference trial was Ciechanowski's watch model. Dragging its first
slider visibly separated the watch into layers. This verifies a specific
interaction, not keyboard accessibility, general usability, or learning benefit.
No learner coursework, banks, answers, or evidence were uploaded or modified.

## What the research changes about D1-D5

These codes retain their meanings from the earlier conversation. Codes inside
the companion reports are local reference labels, not replacement decisions.

| Original proposal | Reflection and evidence | Revised direction |
| --- | --- | --- |
| D1: Put actual work in the foreground | Retain. Reddit critiques of repeated landing-page composition and Linear's content hierarchy support testing the current task first. More density is not automatically more depth. | Show a precise resume target and meaningful course identity. Keep orientation for a new or empty workspace. Do not fill the desk with invented metrics or expose every advanced tool at once. |
| D2: Establish a sharper visual grammar | Strengthen. A serif heading, cream background, and blue accent can become another generic template. Apple typography and the Reddit disagreement favor deliberate hierarchy and fit. | Specify roles for reading, navigation, source context, learner input, and feedback. Compare complete visual directions on the same content. Font and palette selection follow that comparison. |
| D3: Add deliberate visual depth | Reframe. Depth should make grouping, location, and temporary tools legible. Extra layers, cards, and shadows can weaken hierarchy. | Start with alignment, spacing, contrast, and meaningful containment. Use elevation selectively for overlays or tools. Respect dark and OLED modes. Do not force paper texture, glass, or skeuomorphism. |
| D4: Let the subject shape the screen | Retain and make concrete. Explorable explanations and the watch trial show how a subject can generate its own distinctive visuals and controls. PhET warns that difficult controls compete with concepts. | Give each activity the representation it needs within a common shell. Link a named action to an understandable consequence. Use direct reading when it already teaches the objective well. |
| D5: Finish the small interactions | Promote to an end-to-end quality gate. Reddit critiques and Linear's process support evaluating complete flows. Visual preference can mask usability defects. | Test a whole source, lesson, practice, feedback, reference, and resume journey, including failure and pending states. Verify acknowledged saves, stable focus, and preserved drafts. |

Supporting sources include [Reddit's AI fatigue discussion](https://www.reddit.com/r/UI_Design/comments/1tvb91q/ai_fatigue_from_seeing_same_designs/),
[the debate about AI visual tells](https://www.reddit.com/r/UI_Design/comments/1uchh8o/how_can_you_tell_a_design_is_ai/),
[Linear's redesign process](https://linear.app/now/how-we-redesigned-the-linear-ui),
and [NN/G's account of aesthetic usability](https://www.nngroup.com/articles/aesthetic-usability-effect/).
The table is our interpretation of those sources and the local observation.

## What non-slop means for this project

Use observable quality criteria, not claims about how a screen was authored.
The warning signs worth addressing are interchangeable composition, vague copy,
arbitrary emphasis, incoherent controls, implausible example content, and
unfinished states. Human-made interfaces can have the same problems.

Standard components are useful. Familiar navigation can lower effort while
the teaching material and its composition provide identity. Purple, gradients,
rounded corners, shadcn, sans-serif type, and serif type are not forbidden.
Removing them does not establish quality. These points were contested within
the sampled [webdesign discussion](https://www.reddit.com/r/webdesign/comments/1t3ymps/so_many_websites_look_the_same_with_ai/).

Distinctiveness also needs room for expression. Illustration, a memorable type
pairing, a recognizable course cover system, and occasional playful detail can
be valuable. Give them a coherent role and appropriate prominence. Do not
reduce every visual choice to a utilitarian label or strip the app into a
featureless business dashboard. Neither maximalism nor minimalism is accepted
as a universal rule.

## Three directions to compare

These are original design hypotheses, not copies of reference products.

| Direction | Visual character and signature | Best fit | Main risk |
| --- | --- | --- | --- |
| O1: Scholarly desk | Comfortable reading typography, precise control text, marginal source locators, restrained chapter numbering, a recognizable system for annotations and course marks. Light and dark variants. | Sources, long reading, notes, and linked examples. | Beige surfaces and large serif quotes can recreate generic editorial marketing. Keep the real material central. |
| O2: Learning workshop | A quieter shell surrounding expressive diagrams, labeled parts, step controls, comparison states, and subject-specific compositions. Use color consistently within each representation. | Code traces, causal models, visual explanations, and constructive tasks. | A collection of unrelated widgets can feel fragmented. Shared navigation, interaction states, and typography must hold it together. |
| O3: Precision workspace | Compact outlines, crisp rows, aligned controls, optional contextual panels, visible keyboard routes, and modest type contrast. | Course organization, review, and sustained desktop work. | Copying a monochrome productivity app would merely substitute another familiar template. Reading should not inherit tool-panel density. |

Recommendation: prototype O1 and O2 as coherent complete directions, borrowing
O3's precise controls where useful. Do not combine all their decorative traits.
If the user prefers O3 in a task comparison, retain it as a viable candidate.
All three remain Prototype dispositions under the existing renewal owner.

## Five concrete design commitments to test

These are candidate acceptance questions, not newly accepted requirements.

| Priority | Candidate | Demonstration |
| --- | --- | --- |
| A1 | A desk with useful personal context | The current course and saved activity are visible before promotional framing. A long title, empty shelf, ambiguous resume target, and unavailable source remain understandable. |
| A2 | A recognizable source and annotation language | A passage, locator, private note, generated explanation, and runtime feedback are distinguishable. Opening context preserves the anchor. Course identity combines title and visual mark, never color alone. |
| A3 | One signature teaching interaction | On synthetic material, changing a bounded parameter updates a diagram and table together, or stepping a trace highlights the relevant code and state. The learner can explain what changed. |
| A4 | Activity-specific composition within one app | A source reading, code question, written argument, and visual problem share navigation and control conventions while receiving appropriate working space. The interface does not imply unsupported execution or scoring. |
| A5 | Trustworthy transitions and recovery | Answer, submit, inspect feedback, open a reference, return, fail a request, retry, and resume. Input and focus survive the supported flow. Saved and pending states reflect their actual owner. |

A3 has several viable manifestations. Linked values, a source inspector,
code-state comparison, and an argument outline are detailed in
[the interaction report](INTERACTIVITY.md#five-candidate-patterns).
They do not all need implementation at once. Choose the first by the learning
task and reuse existing capabilities before introducing another renderer.

## Visual and behavioral rules for the comparison

Keep one spacing rhythm, a small type scale, consistent icons, and repeatable
control states across every screen. Test long and multilingual content.
Use subject illustrations or meaningful source imagery when appropriate and
permitted. Generic decorative assets should not crowd out the learner's work.

Use compact navigation with comfortable reading and response areas. A global
small-font reduction is not a density strategy. Expert shortcuts complement
visible actions. Secondary tools open deliberately and have a clear return.

Meaningful motion can show where a panel came from, which representation
changed, or how a part relates to the whole. Routine work should not wait for
a flourish. Preserve meaning with reduced motion. The [W3C dragging guidance](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements)
also requires a click or tap alternative where applicable, independently of
keyboard support. Interaction quality includes these equivalent routes.

Human wording should name the user's material and next action. Avoid vague
claims of progress or mastery. Let personality appear in concise orientation,
authored examples, and occasional illustration without inventing praise or
factual study state.

## Test before calling the design successful

Use the same synthetic content, feature set, and tasks for the current baseline
and each candidate. Change the visual treatment first so the comparison can
isolate style. Then compare proposed interactions with their useful static form.
Counterbalance the order if the same person sees both candidates.

| Gate | Evidence to record | Failure signal |
| --- | --- | --- |
| G1: Identity and visual preference | Ask what feels characteristic and why, with brand names hidden where practical. Keep the person's wording. | Only the accent color or logo distinguishes the candidate. Novelty is attractive but obscures the course. |
| G2: Orientation and useful density | Observe opening the saved task, locating the source, and returning after inspection. Record hesitation and wrong turns separately from preference. | The user searches through slogans, cannot locate the current activity, or must keep reopening hidden tools. |
| G3: Learning interaction | Ask for a prediction, allow exploration, then offer a changed case without the aid. Compare conceptual errors with a static treatment. | The user manipulates controls successfully but cannot describe the relationship or use it in a new case. |
| G4: Control and recovery | Exercise pending feedback, failed submission, retry, navigation return, and exact resume with synthetic state. | Lost input, ambiguous saved state, focus jumps, premature keyed content, or an invented score. |
| G5: Equivalent use and delivery | Inspect narrow layouts, 200 percent text, 400 percent zoom/reflow where applicable, keyboard, click/tap alternatives, reduced motion, and representative screen-reader tasks. Compare prototype, packaged, and installed views. | A useful action disappears, meaning depends only on color or motion, or the installed app differs from the reviewed design. |

These gates are a formative review plan. They have not been run on a new
Itembank candidate in this pass. Do not merge them into a single aesthetic
score or claim general learning efficacy from a small trial. Human preference,
accessibility acceptance, learning benefit, and implementation verification
remain separate evidence.

## Dispositions, dependencies, and next artifact

The parent proposal is [IL-20260925-01](../../IDEA-LEDGER.md#il-20260925-01-distinctive-app-craft-and-useful-interaction),
disposition Prototype. The next useful artifact is a bounded comparison of the
same synthetic desk, reading, practice, and return journey in two visual
directions. The existing renewal showcase is the starting inventory, not a
frozen default and not a reason to create a disconnected new product.

O1-O3 and A1-A5 belong to that parent. Their dependency is a representative
synthetic journey, current presentation owners, and user review. Their cost
drivers are template coverage, content/illustration authoring, focus and
recovery behavior, and package parity.

Bespoke 3D scenes, broad simulation engines, and a large custom illustration
library stay Backburner under this proposal. Their triggers are a named
objective that simpler representations cannot serve and an authoring and
maintenance budget. No existing capabilities or permanent proposals are
rejected or superseded by this research.

## Safe scope and verification record

Accepted learner files and runtime assessment authority retain their existing
owners. This research adds no scoring, parser, source, note, or evidence system.
No product setting, installed application, production file, or learner record
was changed by this research pass. No outside code or visual assets were copied.

The durable outputs are the four reports in this directory and linked additions
to the existing vision inbox, vision record, idea ledger, and renewal owner.
All edits remain reviewable and uncommitted. Preserve concurrent unrelated work.
Undo only this directory and the uniquely titled additions from this pass.

Verification completed on 2026-09-25: all 16 local links and anchors across the
four reports resolve. Authored report prose and whitespace checks pass.
The vision audit recognizes the new downstream link and reports no missing
interpretation, planning effect, or inbox disposition. Its pre-existing
unresolved references and traceability backlog remain unchanged.
Quick preflight passes every executed gate, with Python suites, JavaScript
suites, and the clean-tree gate skipped as specified by its quick mode.
An independent bounded review found no material evidence or authority issues.
No new prototype, runtime test, installed parity, or human acceptance result
is claimed.
