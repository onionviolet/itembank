# Phase 20: Extensible UI Foundation and Interaction Clarity Pass - Research

**Researched:** 2026-09-07
**Status:** Ready for planning

## Existing implementation seams

- `surfaces/presentation.py` already owns semantic tokens and reusable primitives. Extend this layer rather than adding a second renderer.
- `surfaces/home.py` already derives honest shelf, resume, progress, and evidence-backed next-action state. Presentation profiles must consume this state without recomputing it.
- `surfaces/daemon.py::_course_page_state`, `_course_frame`, `_course_area_rows`, `_course_rows_html`, and `_course_shelf_body` are the current shelf and course composition seam.
- The lesson and quiz routes already receive runtime-safe public state. New activity framing must use the existing session mode and `public_item` response schema.
- `schemas/settings.schema.json` and `surfaces/settings.py` are the durable settings authority. A profile value belongs there with migration and visible fallback.

## Planning findings

### F-01: The current sameness is structural

The current served shell uses consistent tokens, but many regions share the same card, heading, and control treatment. The next pass must alter information grouping, DOM order, emphasis, and transition cues before tuning appearance.

### F-02: Item type alone cannot explain the learner's job

`mc`, `multi`, `table`, `build`, `dnd`, `short`, `visual`, and `check` describe response contracts. Diagnostic, practice, remediation, exam, and drill describe activity purpose and disclosure policy. Showing one as if it were the other makes the interface harder to predict.

### F-03: The safest architecture is a projection

Both profiles can project the same semantic view model through role classes or data attributes. Route handlers, session state, and form actions should remain profile-neutral. This makes profile removal recoverable and prevents a second behavior stack.

### F-04: State coverage must precede surface breadth

One vertical slice across populated, empty, loading, unavailable, conflicted, interrupted, and pending states gives more evidence than restyling every route in the happy path.

### F-05: External platforms contribute different parts of the answer

Canvas contributes multiple projections over one course set. Moodle contributes a separate time-oriented agenda. Google Classroom contributes remembered disclosure and hidden empty modules. Khan Academy contributes resume-first ordering. Duolingo contributes path clarity. Open edX contributes stable course navigation and narrow extension slots. Kolibri contributes offline and interruption behavior. None supplies itembank's authority model as a whole.

### F-06: Comprehensive closure needs staged breadth

The user has expanded Phase 20 beyond the original representative slice. The safe execution shape is sequential: repair verified defects, establish the shared foundation, compare home projections, migrate learning interactions, prove the full transition graph, then adopt the foundation across remaining compatible surfaces and close the audit ledger.

## Validation architecture

- Extend `tests/home_roundtrip.py` for profile-neutral home state and exact-resume preservation.
- Extend `tests/component_primitives_roundtrip.py` for profile parity, semantic roles, and every state class.
- Add `tests/presentation_profiles_roundtrip.py` for settings migration, invalid fallback, identical actions and form targets, item-purpose versus response-format labels, no-script content, and profile removal recovery.
- Extend `tests/visual_accessibility_roundtrip.py` to render both profiles at 1280, 375, and 320 pixels with 200 percent text, keyboard focus, target size, contrast, reflow, and reduced motion checks.
- Use the existing synthetic course and item fixtures. Do not commit a real bank.

## Risks

- A profile branch inside each route would create two renderers and drift.
- Copying prototype colors into component logic would couple behavior to appearance.
- Renaming runtime item types for friendlier copy would break the contract. Map them only at the presentation boundary.
- A profile switch that reloads to a new URL can lose focus, scroll, or unsaved state. Preserve route identity and apply derived presentation without navigation.
- A broad primitive registry before the slice proves two consumers would add abstraction without evidence.
