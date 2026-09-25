# Interaction craft for a distinctive learning workspace

Research date: 2026-09-25. Owner: root research lane.
Status: evidence and prototype recommendations, not a production specification.

## Scope and prior work

This extends the existing [interactive teaching report](../overhaul-2026-09-18/INTERACTIVE-TEACHING.md)
and [UI renewal](../ui-renewal-2026-09-18.md).
Those records already propose linked representations, source context, prediction,
transfer checks, and accessible fallbacks. This pass strengthens their design
rationale and gives one newly observed example. It does not classify those
capabilities as universally absent from current source or the installed app.

## Primary evidence

All sources were accessed on 2026-09-25. Recommendations below are our synthesis.
Publication and access dates are separate.

| Ref | Source and date | Evidence read | Transfer and limit |
| --- | --- | --- | --- |
| I1 | Bret Victor, [Explorable Explanations](https://worrydream.com/ExplorableExplanations/), 2011-03-10, with a February 2024 postscript | Author's essay and examples. It describes adjustable assumptions, immediate consequences, and contextual information. | Let a reader question a model within the reading surface. This is a design argument, not evidence that every interactive lesson improves learning. |
| I2 | Bartosz Ciechanowski, [Mechanical Watch](https://ciechanow.ski/mechanical-watch/), 2022-05-04 | Article read and the first model exercised in the browser. Dragging its slider separated the watch into an exploded view. | One understandable control can expose otherwise hidden structure. Bespoke 3D scenes have substantial authoring and rendering cost. Do not require them for ordinary lessons. |
| I3 | Podolefsky, Moore, and Perkins, [Implicit scaffolding in interactive simulations](https://arxiv.org/abs/1306.6544), submitted 2013-06-27, revised 2014-01-23 | Abstract and bibliographic record only. The authors describe constraints, cues, affordances, and feedback guiding exploration. | Useful rationale for bounded controls. This reading does not independently assess the full study or justify generalized efficacy claims. |
| I4 | Adams and colleagues, [Educational Simulations Part II: Interface Design](https://phet.colorado.edu/publications/archive/PhET%20Interview%20Paper%20Part%20II.htm), archived manuscript, exact publication date not shown | Abstract, methodology, and interface discussion. The authors report over 200 interviews with 89 students across 52 simulations. | Control difficulty can divert attention from concepts. This is qualitative simulation research, not an evaluation of Itembank, every subject, or modern device accessibility. |
| I5 | NN/G, [The Role of Animation and Motion in UX](https://www.nngroup.com/articles/animation-purpose-ux/), 2020-01-12 | Article on feedback, state change, orientation, and distraction. | Give motion a named communication job. A transition must not delay repeated work or distract from reading. |
| I6 | W3C, [Dragging Movements](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements), page updated 2026-08-10 | Explanation of WCAG 2.2 SC 2.5.7, Level AA. | Provide a click or tap alternative to dragging. Keyboard equivalence alone does not satisfy this criterion. Review keyboard access separately. |
| I7 | W3C, [Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html), page updated 2025-09-16 | Explanation of SC 2.3.3, Level AAA. | Let users disable nonessential motion. The criterion permits essential motion. A reduced-motion route should retain meaningful controls and state changes. |
| I8 | NN/G, [The Aesthetic-Usability Effect](https://www.nngroup.com/articles/aesthetic-usability-effect/), 2024-02-03, reviewed 2026-09-01 | Article on appearance affecting perceived usability and masking problems in testing. | Collect visual preference and task performance separately. A beautiful screenshot is not a successful learning or recovery test. |

## Bounded live observation

In a public browser tab, the first watch model initially showed an assembled
watch face. Its slider was visible directly below the model. Moving the handle
from the left toward the right visibly separated its layers and exposed the
mechanism. Screenshots before and after were inspected in the session.
No reference artwork was downloaded or copied into the repository.

The accessibility snapshot did not announce a changed value or description
after this drag. That limited observation does not establish the site's full
accessibility, but it prevents treating this example as an accessibility model.
Keyboard, touch, screen-reader, reduced-motion, offline, and learning outcomes
were not tested. Other examples in the article remain documented references.

## Five candidate patterns

| Pattern | Concrete Itembank example | Distinctive contribution | Acceptance question |
| --- | --- | --- | --- |
| P1: Linked representations | Change a bounded value and inspect the same value in an equation, plot, and table. Use consistent labels and units. | The subject provides the visual character. | Can the learner explain the changed relationship and solve a new case without the controls? |
| P2: Anchored inspection | Open a source passage or term explanation beside its exact anchor. Pin it deliberately and return to the same reading position. | Sources and learner notes feel like connected working material. | Does the user know what the panel refers to, and can they dismiss it without losing place or a draft? |
| P3: Predict, inspect, compare | Enter a code prediction, fill a blank trace, then inspect permitted state changes and compare the prediction with feedback. | The learner's reasoning becomes visible. | Does the view preserve the first prediction, make the relevant step legible, and obey the runtime's disclosure mode? |
| P4: Construct and revise | Arrange synthetic argument claims and supporting evidence using drag or named move controls. Keep an equivalent outline. | A humanities activity gets a composition suited to reasoning. | Can the learner explain a relation and revise it without the graphic implying that mere placement proves correctness? |
| P5: Continuous task state | Select an answer, submit, inspect feedback, open a reference, return, and continue with a stable focus target. | The app feels dependable over a whole session. | Do selection, draft, feedback, position, and acknowledged save state survive supported navigation and retry? |

P1-P4 are Prototype applications of existing owners and capability directions.
P5 is a proposed craft review of existing behavior, not a claim that saving or
resume must be built from scratch. All five require an actual learner task.

## Interaction and motion contract for the next prototype

Every candidate names an object, an action, its visible consequence, and a way
to recover or reset. A hover decoration does not qualify as a learning action.
Use pointer, keyboard, and touch paths appropriate to the task. Tooltips remain
brief. Longer support opens deliberately and has a clear close action.

Use motion to connect an origin to a destination, show a state transition, or
explain a relationship. Do not impose one universal duration on every task.
Repeated actions must remain interruptible. Keep the content position stable
when feedback appears. Preserve keyboard focus or move it deliberately.

In OLED mode, flat black can remain the background. Grouping can use alignment,
spacing, dividers, focus indicators, and optional raised surfaces. More shadows
are not a substitute for comprehensible structure.

Prefer finite, reviewed scenes and reusable semantic components. Public models
can expose public consequences. Protected answers, traces, and explanations
still require runtime disclosure. Exploration is not a score or mastery claim.
Learner prose remains pending review under the existing assessment contract.

## Practical validation

Use synthetic material and the same task across the proposed styles. Record
visual preference, navigation errors, recovery success, and conceptual transfer
separately. Compare an interactive treatment with a useful static treatment.
Stop if the user spends more attention learning the control than the concept.
A small formative trial can identify defects and preference. It cannot prove
general learning efficacy.

Check narrow reflow, keyboard order, click alternatives, text enlargement,
reduced motion, and a representative screen-reader task. Automated checks are
supporting evidence, not human accessibility acceptance. Reuse the existing
lesson model and runtime. A new rendering library needs a demonstrated gap.

## Authority and recovery

This report is an advisory research artifact under the UI renewal owner.
No source files, banks, learner evidence, accepted formats, settings, or installed
application were changed by this lane. Only public pages were sent to external
services. Removing this new report reverses this lane's file creation.
