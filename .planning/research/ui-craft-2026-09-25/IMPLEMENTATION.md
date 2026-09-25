# UI craft implementation

Date: 2026-09-25. Owner: UI renewal integrator.
Status: source implementation with bounded rendered verification. The design remains
changeable. Installed-app parity and human acceptance are separate gates.

## Scope and decisions

The user authorized implementation after the research capture. This pass takes
the scholarly reading direction and the precision workspace direction into
the existing application. It does not wait for two disposable mockups.
[The research](SYNTHESIS.md) retains the broader alternatives and evidence.

| Code | Implemented direction | Production owner |
| --- | --- | --- |
| D1 | Replace the decorative welcome hero with a compact, truthful course lead and full-width ordered course list. Show canonical action labels. | `surfaces/daemon.py` desk renderers |
| D2 | Compact the shared rail and header. Use labeled navigation icons, a visible active marker, and the existing type scale. | `surfaces/presentation.py` |
| D3 | Use rules and spacing for course rows. Remove the reader's outer card and distinguish source excerpts from examples and notes. | Shared presentation and `surfaces/lesson.py` |
| D4 | Strengthen the existing quantity comparison with exact entry and step buttons. Keep authored starting values and hypothetical exploration distinct. Style the existing equation, plot, and coordinate table as one learning tool. | `surfaces/lesson_interaction.py` |
| D5 | Keep course numbers and the lead in sync with reorder and rollback. Retain keyboard focus. Preserve exploration on browser return. Pass the selected workspace theme into the served reader. | Shelf script, reader route, interaction script |

## Execution boundaries

Two bounded GPT-6 Sol agents at medium reasoning handled the shared frame and
desk renderer. The root handled reading, controls, integration, and rendered
verification. A bounded independent review identified the course-reorder focus
gap, which was fixed and covered by behavior tests.

Concurrent optimization work owns course details, Build and review, discovery,
storage, and quiz observers. Those changes are not credited to this design
pass. Shared-file edits were coordinated by symbol. Storage navigation mapping
and all unrelated edits were preserved.

The canonical course projection still owns labels, destinations, state, and
fingerprints. The first-course lead means first in the user's order. It makes
no recency or mastery claim. Course options use native disclosure and preserve
sample controls and keyboard alternatives to dragging.

Comparison controls remain temporary presentation state. They make no request,
write no evidence, and do not grade. Invalid numeric input leaves the current
model unchanged. Existing static content, runtime disclosure checks, parser,
schemas, and scoring authority remain the owners of their prior contracts.
The served reader consumes the existing theme generator. Static callers keep
their default theme behavior.

## Verification record

Targeted checks cover desk states and escaping, canonical actions, empty and
degraded states, real HTTP lesson disclosure, selected OLED theme, exact input,
bounds, reset, browser-return state, successful reorder, rejected-save rollback,
fingerprints, and keyboard focus. Shared stylesheet, responsive, and theme
checks pass. Full preflight executed 142 Python test scripts and the JavaScript
suite. One Python script asserted the superseded inverted navigation design.
Its check now covers the new foreground/background pair, active underline,
44-pixel target, and muted-text contrast across the existing modes and looks.
That script passed on rerun. The JavaScript suite passed. The clean-tree gate
fails because this shared checkout deliberately retains uncommitted work.
Final quick preflight passed after the implementation changes. Targeted
stylesheet, navigation, lesson, and JavaScript checks passed after the final
visual fixes. The entire slow suite was not rerun after those localized fixes.

Rendered checks use the real daemon with disposable synthetic course and
lesson fixtures. Desktop desk, course overview, and the comparison lesson were
inspected. The comparison changed from 18 to 12 and announced equal quantities.
Keyboard reordering changed the first-course lead and number, saved the order,
and retained focus on the moved course's options. The 390-pixel desk had a
390-pixel document width and the bottom navigation remained within the viewport.
The reader also measured 390 pixels without overflow. Its new buttons measured
45 pixels high. Light, Dark, and OLED carried through to the served reader,
including a measured true-black OLED background. The course-to-lesson-to-practice
handoff reached the synthetic runtime session without submitting an answer.
The linked plot changed to an intercept of -1 and updated its equation, table,
and announcement together. Dark-mode inspection caught black SVG axis labels,
which now inherit the readable foreground color.

No installed application was replaced. No real learner bank, response, or
evidence was changed. These checks establish the bounded behaviors above.
They do not establish learning improvement or human accessibility acceptance.
Only relevant symbols were read in the large presentation, daemon, and lesson
modules. This is not a whole-module audit.

## Recovery and remaining breadth

Revert only this pass's symbol changes and new focused tests to undo it.
The work is uncommitted at the user's standing preference. Do not discard
shared files wholesale because they include concurrent changes.

Bespoke simulations, custom illustration, a broad source inspector, and
additional subject-specific interactions retain their prior dispositions.
Choose the next one from a named learning task and observed friction.
This pass does not freeze the palette or declare the wider renewal complete.

## Palette and control refinement, 2026-09-25

The user asked to adjust the app after reviewing color, button shape, hierarchy,
typography, and interaction states. This follow-up keeps the existing corner
radii and refines the shared presentation rather than adding another look.

- Dark and OLED cards, inset surfaces, and rules have clearer separation.
  OLED retains its true-black page. Accent derivation also checks chip contrast.
- Primary actions use the measured accent and accent-soft pair. Secondary
  controls use the existing edge token. Status labels lose their button shape.
- Course titles and control text use the chrome voice. Resume cues and option
  disclosures use 16px. Reading keeps its paper voice.
- Desk and course buttons show the canonical verb beside the course title.
  Their accessible names retain the full canonical label. Reorder and rollback
  update both names together. Recovery labels remain complete.
- The desktop lead places its action alongside the course. The Courses page
  uses ruled rows. Focus, hover, pressed, and disabled states remain distinct.

Independent review caught muted text below 4.5:1 on the accent-soft lead.
The lead now uses the shared card background, whose text pairings are checked,
while its action and left rule carry the accent. No persisted learner theme,
accent, look, course, answer, or evidence is changed by this refinement.

Focused theme, stylesheet, settings, navigation, responsive, presentation,
desk, and reorder checks passed. Rendered inspection covered the light and
OLED desk, Courses, keyboard focus, and the synthetic reading surface.
The 390px desk had no horizontal overflow. Its actions and option summaries
measured at least 44px high with 16px text. These are bounded checks, not a
complete accessibility certification.

Full preflight executed 142 Python scripts and the JavaScript suite. Two
Python scripts failed on the same superseded theme HTML snapshot. After
refreshing that intentional snapshot, both scripts passed on rerun. The
JavaScript suite and final quick preflight passed. The clean-tree gate still
flags the shared checkout's uncommitted work. The full slow suite was not
repeated after the snapshot correction.

The final source was rebuilt into the native app and DMG. Code-signature and
DMG verification passed, and the frozen runtime reported version 0.5.0.
The installed app was replaced with a recoverable backup of the prior bundle.
This follow-up supersedes the earlier pass's no-installation statement.
The first launch remained at Starting runtime. A scoped stop and relaunch
recovered startup, but the initial cause was not established. Native inspection
then confirmed the updated desk and Courses rows, readable controls, full
accessible action names, and retained course/session destinations. The app
was left open on Your desk. No commit or public release was made.
