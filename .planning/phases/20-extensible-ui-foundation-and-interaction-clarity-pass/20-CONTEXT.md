# Phase 20: Extensible UI Foundation and Interaction Clarity Pass - Context

**Gathered:** 2026-09-07
**Status:** Ready for planning
**Source:** User direction plus the 2026-09-06 and 2026-09-07 UI continuation packet

<domain>
## Phase Boundary

Deliver one representative shelf to course overview to lesson to practice slice that feels structurally different, not merely restyled. The slice separates visual presentation, navigation and transition logic, learning activity purpose, and response format while preserving one parser, one scorer, one route identity, and one evidence store.

This phase does not migrate every surface. It does not add item types. It does not create a general plugin loader. It does not change scoring, keyed disclosure, selection authority, or canonical course content.

</domain>

<decisions>
## Implementation Decisions

### Hierarchy

- **D-01:** The current UI still feels the same because page level, course identity, current task, status, and next action compete at similar weight.
- Acceptance requires a learner to identify page level, current course, current task, and next action without reading the whole page.
- Replacing colors, radii, or card borders alone does not satisfy this phase.

### Layer boundaries

- **D-02:** Semantic roles define meaning and state.
- Shared primitives implement accessible behavior once.
- Presentation profiles arrange navigation, density, emphasis, and layout.
- Appearance themes control color, typography, spacing, geometry, and motion without changing behavior.

### Presentation profiles

- **D-03:** `field-guide` and `trajectory-deck` are the first stable presentation-profile values.
- Both render identical semantic markup and runtime state through shared primitives.
- Field Guide emphasizes source-heavy reading, explanation, annotation, and reflection.
- Trajectory Deck emphasizes movement, practice, evidence, operations, and recovery.
- Profile selection remains independent from theme, contrast, and accent.

### Activity meaning

- **D-04:** The UI must not collapse diagnostic, practice, remediation, and exam purpose into the item response type.
- The learner-facing activity frame names purpose and disclosure mode first.
- The response control names the concrete format second: single choice, multiple choice, table, build, drag-and-drop, short response, visual interaction, or code check.
- The parser and runtime type values remain unchanged. This is semantic presentation over `public_item` and session state, not a second item taxonomy.

### Transition logic

- **D-05:** Home, Back, stop, finish, exact resume, interruption, post-practice, post-assessment, and later-return behavior must be explicit and testable.
- Switching profiles preserves route, course, session, evidence, browser history, reading locator, meaningful focus, and unsaved-work warnings.
- Browser Back never causes a second submission.

### State clarity

- **D-06:** Populated, empty, loading, unavailable, conflicted, interrupted, pending review, invalid, and recovery states use different copy and actions.
- Unknown and unavailable are never rendered as zero or empty.
- A region hides only when its absence is uninformative. Otherwise it names the next safe action.

### Extensibility

- **D-07:** One capability-adapter declaration is exercised by both profiles in the slice.
- An adapter declares supported states, profiles, input modes, plain fallback, unavailable behavior, migration effect, tests, and removal recovery.
- No external package loading, runtime fetching, live reload, or universal loader enters this phase.

### Comparative verification

- **D-08:** The identical fixture is rendered in both profiles at 1280, 375, and 320 CSS pixels.
- Checks cover light, dark, high contrast, reduced motion, keyboard, touch targets, 200 percent text, reflow, no script, offline, invalid profile fallback, and removal recovery.
- Automated checks are evidence, not human accessibility certification.

### Audit ownership

- **D-09:** `20-AUDIT-CROSSWALK.md` is the current routing owner for inherited UI findings in this phase. Historical audits remain unchanged as evidence. Each adopted finding must appear in a task and verification gate. Findings routed to 19D, 17C, 18, later profile adoption, or EXT-05 must not be silently absorbed into 20-01.

### Comprehensive Phase 20 closure

- **D-10:** Phase 20 owns every actionable UI finding in `20-AUDIT-CROSSWALK.md` except rows explicitly routed to another named owner. Closure requires every owned row to be fixed and verified, or explicitly superseded by user-reviewed evidence. A passing representative slice alone no longer closes the phase.
- **D-11:** Canvas, Moodle, Google Classroom, Khan Academy, Duolingo, Open edX, Kolibri, Runestone, H5P, PrairieLearn, Anki, and FSRS are behavior references. `20-INSPIRATION-MATRIX.md` records what is adapted, tested, and rejected. Phase 20 copies no external implementation or engagement metric.
- **D-12:** The four shipped home modes remain `shelf`, `next-action`, `agent`, and `split`, with `shelf` still the user-selected default. Phase 20 does not delete or silently rename them. Resume, Shelf, Agenda, and Path are comparative learner jobs and projection prototypes. Map Resume to the existing `next-action` behavior first, map Shelf to the existing `shelf` behavior first, and test whether Agenda or Path should extend an existing mode or earn a new stable setting value. The `agent` and `split` modes remain available throughout comparison.
- **D-13:** The profile foundation expands to every existing learner-facing surface only through the shared semantic and adapter contracts. A surface that cannot migrate without changing assessment, evidence, rights, or recovery authority keeps its current behavior with a visible compatibility disposition.
- **D-14:** EXT-01 through EXT-03 remain existing first-party registration work. Phase 20 owns the UI portion of EXT-04: presentation profiles, independent appearance axes, UI capability adapters, and profile framing for the already-built Agent and MCP capability states. EXT-05 remains deferred because external code isolation, acquisition, grants, compatibility, rollback, and recovery are unsettled. Phase 20 must prove that it adds no external loader.

### the agent's Discretion

- Exact internal names for semantic-role and profile rendering helpers.
- Whether the activity-purpose label is a heading, eyebrow, or compact status row, provided its DOM order precedes the response format.
- Which existing lesson or practice renderer becomes the first capability adapter, provided both profiles exercise it.

</decisions>

<canonical_refs>
## Canonical References

- `.planning/PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md` defines the post-Reach representative slice and exclusions.
- `.planning/notes/2026-09-07-home-and-transition-ui-scope.md` defines the transition matrix and comparative home jobs.
- `.planning/UI-CHARACTER-AUDIT-2026-09-06.md` records the selected profiles and visual-system findings.
- `.planning/TRANSITION-AUDIT-SYNTHESIS.md` records source-to-course compatibility, phone, offline, and authority grievances.
- `.planning/VISION-PLAN-AUDIT-2026-09-06.md` separates Reach walkthrough and instructional-quality gaps from the post-Reach UI owner.
- `.planning/AUDIT-REMEDIATION-PLAN-2026-09-06.md` routes the course shell and representative unit work through R5 and R6.
- `.planning/phases/13.5-reading-teaching-surface-quality-pass/13.5-UI-SPEC.md` owns reader, glossary, wrong-answer, control, copy, and live-region contracts.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md` owns routes, exact resume, mode precedence, offline help, settings, and degraded-state contracts.
- `.planning/phases/17A-visual-system-component-foundation/17A-UI-SPEC.md` owns semantic tokens, primitive states, progressive disclosure, and accessibility QA rules.
- `.planning/phases/17B-production-vertical-tracer/17B-UI-SPEC.md` owns the production learner journey and G4, G5, and G8 evidence expectations.
- `.planning/EXTENSION-DELIVERY-2026-09-06.md` owns extension registration, authority, recovery, and the EXT-05 boundary.
- `.planning/SOURCE-TO-COURSE.md` defines course-first authority and extension boundaries.
- `.planning/AGENT-WORKFLOW.md` defines safe operations, review, and recovery.
- `.planning/phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-AUDIT-CROSSWALK.md` is the current disposition map for the audits above.
- `.planning/phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-AUDIT-INDEX.md` is the navigation map for historical audit evidence.
- `.planning/phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-INSPIRATION-MATRIX.md` maps external behavior references to Phase 20 tests and rejections.
- `.planning/phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-EXTENSION-COVERAGE.md` maps EXT-01 through EXT-05 and every presentation axis to an owner and gate.
- `prototypes/17c-finalists/field-guide.html` and `prototypes/17c-finalists/trajectory-deck.html` are visual references, not production renderers.

</canonical_refs>

<specifics>
## Specific Ideas

- Use one compact application frame, a bounded course object, one short next action, and quieter secondary evidence.
- Keep the response interaction dominant only while the learner is answering.
- Show purpose, format, feedback availability, and position as separate facts instead of one dense metadata line.
- Prefer title-led rows and spacing rules for inventories. Reserve containers for actionable or stateful units.

</specifics>

<deferred>
## Deferred Ideas

- Permanent selection among Resume, Shelf, Agenda, and Path home projections happens only after all four Phase 20 prototypes are compared on identical state.
- Automatic profile switching waits for evidence that it beats explicit user control.
- Surface migration is staged across Phase 20 plans after the foundation passes. A named compatibility disposition is acceptable where migration would cross an authority boundary.
- External capability packages remain behind the EXT-05 supply-chain decision.

</deferred>
