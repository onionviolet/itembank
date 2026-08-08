# Phase 4: Surface Redesign & Theming - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Unify quiz, study, daemon/report, and day surfaces under one visual system; simplify the question screen; expose all existing study explanation data; derive accessible light/dark accents from the learner's OS color choice; and let the learner edit the current day plan in-page without silently overwriting concurrent file edits. Scoring, answer-key ownership, scheduling, and new learning behavior remain outside this phase.

</domain>

<decisions>
## Implementation Decisions

The user selected every gray area and delegated detailed choices to the planning model with a standing preference for comprehensive, high-quality defaults. When two approaches are both useful and cheap to preserve, the plan should retain both behind progressive disclosure or a setting; it should not add choice where it makes the primary workflow noisier.

### Question-screen hierarchy

- **D-01:** Replace the five chrome bands with one sticky, compact context line containing only orientation data needed while answering: bank/lesson context, objective, progress, and session mode. Secondary metadata belongs behind an accessible details disclosure, not in another persistent band.
- **D-02:** Make the stem the dominant element, keep the response control immediately adjacent, and reserve feedback space so submitting does not cause large layout shifts. Desktop and narrow/mobile widths must use the same information order.
- **D-03:** Preserve keyboard and screen-reader operation as a first-class contract: visible focus, semantic headings/status regions, no meaning conveyed by color alone, and reduced-motion support.

### Accent and OS theming

- **D-04:** Keep `surfaces/theme.py` as the single palette source. System light/dark mode remains automatic by default; the chosen accent is global to the local installation and shared by every surface.
- **D-05:** Use the native OS color picker through the existing Python/launcher boundary where supported, with an accessible browser fallback when native selection is unavailable. Persist the source accent, then deterministically derive light/dark accent tokens and soft variants.
- **D-06:** Contrast correction may adjust the rendered token while preserving the learner's source choice. Show the adjusted preview before save and explain the accessibility adjustment. Correct/incorrect/warning colors remain semantic, color-blind-safe, and independent of the custom accent.
- **D-07:** Include reset-to-system/default and live preview. Advanced manual light/dark token overrides may be retained only if they do not weaken contrast enforcement or complicate the default flow.

### In-page day editing

- **D-08:** Use an explicit edit mode with a structured row/cell editor matching the existing day-plan table, not a raw Markdown editor. Preserve unknown Markdown and surrounding prose byte-for-byte outside the edited row/cells.
- **D-09:** Save with optimistic concurrency against a strong representation of the bytes originally loaded (content hash, optionally paired with file metadata). The server re-reads immediately before replace; a mismatch never auto-overwrites.
- **D-10:** On conflict, show the learner's draft and the newly read file side by side with copy/download and reload/reapply actions. A force-overwrite action may exist only behind an explicit second confirmation; the normal path is reload and reapply.
- **D-11:** Writes use the project's atomic replace pattern and return the new revision token. Validation errors remain in the editor with the draft intact. Navigation away with unsaved changes warns.

### Study explanations

- **D-12:** After reveal, organize explanation content progressively: answer and concise why first; per-option rationales beside their options; second-best, discriminator/trap, and notes in labeled expandable sections. Nothing currently present in the runtime explanation payload is silently discarded.
- **D-13:** Default expansion should follow relevance: the chosen option and correct option open; other option rationales remain available but collapsed. Keyboard and screen-reader users receive the same information and state.
- **D-14:** Quiz and study share explanation presentation primitives/tokens where practical, but keep their different learning intent: quiz feedback is response-driven; study permits deliberate reveal and review.

### the agent's Discretion

- Exact spacing, typography scale, breakpoints, iconography, transition timing, native picker implementation, conflict-diff presentation, and naming of disclosure controls.
- The planner may preserve multiple reversible presentation variants when this improves future optionality, but must select one polished default and verify it end to end.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/ROADMAP.md` section "Phase 4: Surface Redesign & Theming" - goal, dependency, and success criteria.
- `.planning/REQUIREMENTS.md` requirements SURF-02 and SURF-05 through SURF-09 - binding feature scope.
- `.planning/PROJECT.md` - product constraints, especially local-first behavior and runtime-owned scoring.

### Prior phase contracts

- `.planning/phases/02-daemon-consolidation-settings-foundation/02-CONTEXT.md` - one-daemon routing, settings, and CLI/API parity decisions.
- `.planning/phases/03-lesson-format-in-app-reader/03-CONTEXT.md` - lesson/read surface decisions that the shared visual system must accommodate.
- `.planning/phases/05-check-item-type-code-editor/05-CONTEXT.md` - editor/accessibility choices that should visually coexist with this phase.

### Existing implementation

- `surfaces/theme.py` - existing shared CSS variable palette and OS dark-mode seam.
- `surfaces/quiz_page.py` and `surfaces/quiz.py` - current question hierarchy, feedback rendering, and theme injection.
- `surfaces/study.py` - current study layout and explanation omissions.
- `surfaces/day.py` - current literal-color stylesheet, day table parser, render state, and mutation path.
- `surfaces/daemon.py` - page routes, settings integration, and the rule that verdicts come from server/runtime calls.
- `runtime.py` - public item and explanation payload boundaries; the browser must never receive or score against a hidden key.
- `surfaces/settings.py` and `schemas/settings.schema.json` - validation and persistence patterns for theme settings.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `surfaces/theme.py:THEME_CSS` already supplies shared custom properties and `prefers-color-scheme`; extend it rather than introducing per-page palettes.
- `surfaces/quiz_page.py` already renders per-option rationale, second-best, discriminator/trap, and notes; its payload-to-presentation behavior is the closest study analogue.
- `surfaces/day.py` already centralizes parsing, state creation, rendering, and POST mutation, giving the editor one server-owned save seam.
- The updater/settings work already established validated settings and atomic replace patterns suitable for accent persistence and guarded plan writes.

### Established Patterns

- Surfaces are thin clients: parsing stays in `model.py`, scoring in `runtime.py`, and browser code does not hold the key or invent verdicts.
- HTML/CSS/JavaScript is embedded and stdlib-only; offline behavior is mandatory.
- Additive compatibility and byte preservation matter for human-authored Markdown.
- Stable DOM/data markers are preferred for integration tests over prose scraping.

### Integration Points

- Theme tokens flow into quiz, study, day, index, and report templates.
- Accent configuration enters through settings plus a daemon route/CLI twin for any mutation.
- Day editing connects to `day_state`, `day_render`, `apply_day_post`, and daemon day routes, with a new revision token carried through render/save.
- Study explanation rendering consumes the existing runtime explanation payload; it must not create a second explanation source.

</code_context>

<specifics>
## Specific Ideas

- Favor one polished default while retaining genuinely useful, reversible choices for later configuration.
- Accessibility correction should be visible rather than silently changing the learner's chosen color.
- A day conflict must preserve the learner's draft and make recovery obvious; "last writer wins" is explicitly unacceptable.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 4-surface-redesign-theming*
*Context gathered: 2026-08-08*
