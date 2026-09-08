# Phase 20 UI Design Contract

**Phase:** 20, Extensible UI Foundation and Interaction Clarity Pass
**Status:** Ready for planning
**Date:** 2026-09-07

## Experience outcome

The learner can tell where they are, what object they are working in, what kind of learning task is active, what response is expected, and what happens next. Field Guide and Trajectory Deck feel meaningfully different because they change composition and emphasis, while every action, state, route, and authority rule stays identical.

## Audit repair floor

Profile comparison starts only after these verified defects are repaired in the representative fixture:

- Hidden Study action groups occupy no layout and expose no focusable descendants.
- Table and build inputs use the shared native-control treatment, 44px project target, and 16px action text.
- Walkthrough controls use shared button roles.
- Quiz starts with one help entry instead of six prominent locked-tier panels. Runtime entitlement remains unchanged.
- Current course area is visibly marked in a consistent application and course frame.
- Empty course areas name an existing next action or an honest blocker.
- Open search and sticky chrome do not cover focused controls or final content at 375 or 320 CSS pixels.

## Information hierarchy

Every representative screen follows this order in the DOM and in visual emphasis:

1. Application and page level.
2. Course identity and exact location.
3. Current task and its purpose.
4. Primary content or response interaction.
5. Status, evidence, source, and recovery details.
6. One next action plus quiet secondary navigation.

The page must not repeat the product name, page title, course title, and action label with equal weight.

## Presentation profiles

### `field-guide`

- Source-led composition with a stable course rail or margin.
- Reading measure stays between 58ch and 72ch.
- Citations, definitions, annotations, and source state remain adjacent to the passage they qualify.
- Practice narrows to the activity frame without losing the course locator.

### `trajectory-deck`

- Task-led composition with a visible course journey and current stage.
- The next action and interruption recovery appear before secondary course detail.
- Practice, evidence, and recovery use stronger spatial separation than reading.
- The journey never implies that visiting a stage proves completion or mastery.

Both profiles use the same headings, links, buttons, forms, status text, route targets, and state values. CSS and profile composition may reorder only regions whose reading and focus order remains logical.

## Existing home modes and comparative jobs

The shipped setting values remain stable:

- `shelf`: course or bank rows, evidence-backed next action, and recent activity. It remains the default.
- `next-action`: the exact next action and reason lead. Other content stays one step behind.
- `agent`: Agent is the home, with course state as context.
- `split`: course state and Agent share the wide layout and degrade to Shelf at phone width.

The new comparison language names learner jobs rather than replacing these values. Resume begins as a refinement of `next-action`. Shelf begins as a refinement of `shelf`. Agenda and Path remain prototypes until the human comparison decides whether they extend an existing mode, become new values, combine, or are superseded. Both `agent` and `split` must remain usable in Field Guide and Trajectory Deck.

## Appearance axes

Presentation profile, home mode, look, theme, accent, density, contrast, and motion are independent. Preserve all shipped look values: `classic`, `editorial`, `neo`, `cash`, `console`, `soft`, and `contrast`. A settings migration or profile save may not reset another axis.

## Activity and item separation

The activity frame exposes four separate labels:

- Purpose: Diagnostic, Practice, Remediation, Formal assessment, or Drill.
- Response format: Single choice, Multiple choice, Table response, Build response, Ordering or matching, Short response, Visual interaction, or Code check.
- Disclosure: Feedback available now, Feedback after completion, Review locked, or Pending human review.
- Position: Item N of M when the denominator is known.

Purpose is derived from session or selection mode. Response format is derived from the runtime-safe public item contract. Disclosure comes only from runtime-granted state. No label guesses at correctness or mastery.

The capitalized `Activity` application area continues to mean durable agent or maintenance jobs. It must never be presented as the same object as a learner activity or question.

## Shared primitives in this slice

- `AppFrame`: application level, global destinations, settings.
- `CourseIdentity`: course title, state, exact resume cue.
- `NextAction`: one action and an evidence-grounded reason or a stated blocker.
- `CourseOutline`: objectives and available treatments without invented progress.
- `ReadingFrame`: passage, locator, citations, definitions, next activity.
- `ActivityFrame`: purpose, format, disclosure, position, response control, feedback region.
- `StatusNotice`: empty, loading, unavailable, conflict, pending, invalid, recovery.
- `ProfilePreview`: same fixture rendered under both profile values before save.

## State and copy contract

| State | Required copy behavior | Required action behavior |
|---|---|---|
| Empty | Name what is absent and whether that is normal | Offer one supported creation or return action only when available |
| Loading | Name the object being read | No fake percent and no stale controls |
| Unavailable | Name the unavailable capability and retained fallback | Keep local or static continuation reachable |
| Conflicted | Say what changed and that nothing was overwritten | Offer inspect, retry from current base, or leave unchanged |
| Interrupted | Name the exact stopping point | Resume the same session without duplicate attempts |
| Pending review | State that the response is recorded but unsettled | Offer course continuation without implying a mark |
| Invalid profile | Name the unsupported saved value and active fallback | Preview and save a supported value |
| Recovery | Name the last accepted state and the next safe action | Never make destructive recovery the default |

## Settings contract

- `presentation_profile` accepts `field-guide` and `trajectory-deck`.
- Missing values migrate to the currently shipped composition until the user saves a profile.
- Unknown values render a visible fallback notice and use `field-guide` as the safe static composition.
- Preview does not save and does not navigate.
- Save uses the existing settings write and recovery path.
- Theme, contrast, accent, density, and motion remain independent controls.

## Responsive and accessibility contract

- Test at 1280, 375, and 320 CSS pixels, plus 200 percent text.
- Supporting rails become reachable disclosures or destinations on narrow screens. They do not vanish.
- Interactive targets remain at least 44 by 44 CSS pixels.
- Source, pending, unavailable, danger, focus, and recovery states never rely on color alone.
- Profile switching preserves meaningful focus. If the exact node disappears, focus moves to the equivalent region heading.
- Reduced motion disables nonessential transitions.
- No-script output retains headings, content, response instructions, source labels, status copy, and ordinary form actions.

## Capability adapter used by the slice

The existing question-response renderer is registered as the first internal capability adapter. It declares supported public item formats, session purposes, keyboard and touch behavior, plain fallback, unavailable copy, fixtures, and removal recovery. The declaration grants no scoring or disclosure authority.

The UI portion of EXT-04 also covers bounded declarations for migrated reader, editor, source, Agent, evidence, export, and integration surfaces. The already-built Agent operation and MCP tool table retain their Phase 19B and 19E authorities. Phase 20 changes presentation and capability disclosure only.

## Verification matrix

The same fixture must pass both profiles across populated, empty, loading, unavailable, conflicted, interrupted, pending-review, and invalid-profile states. Automated evidence covers DOM parity, route and form parity, focus, reflow, target size, contrast derivation, static fallback, migration, invalid-value fallback, and removal recovery. Human visual and screen-reader acceptance remain explicitly owed.

The matrix also includes Study front, revealed, and learn states, Quiz before answer and every permitted hint state, table and build responses, empty and populated course areas, open search, walkthrough controls, a long title, a wide table, a software-keyboard viewport, and the bottom safe area.
