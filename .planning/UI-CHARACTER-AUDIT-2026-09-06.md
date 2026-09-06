# UI character audit and proposed plan

Date: 2026-09-06. Status: proposal for review. Application implementation is not authorized by this document.

## Scope and evidence

Inspected current production renderers in a local daemon using temporary copies of synthetic fixtures. No real learner files were used. Browser observations used the Classic look in system-selected dark mode. Screens sampled: Courses `/`, course Overview and Course map, `/banks`, `/lesson/lesson_bank`, `/quiz/sample_bank`, `/study/sample_bank`, and `/settings`. Desktop captures were 1280px wide. Mobile captures were 375px wide. The course fixture contained two empty courses, so empty-state findings do not establish the quality of populated maps or sources.

Code was inspected symbol-first in presentation.py, theme.py, looks.py, daemon.py, lesson.py, quiz_page.py, study.py, home.py, palette.py, and visual_fixture.py. These large modules were sampled, not read in full. Read the workflow and product contract, current state, relevant August 20 vision passages, 17A direction decision, and relevant 17A/17B UI specification sections. This is a representative audit, not an exhaustive accessibility certification or whole-vision audit. No light-mode visual pass, screen-reader pass, full keyboard journey, populated build/review flow, or full automated test suite was performed.

The repository already contained application and planning edits from other work. They were left alone. Temporary fixture construction and daemon startup produced only disposable data outside the repository. Opening the quiz created a synthetic session there. No answers were submitted.

### User intent captured and routed

> Audit the current UI and create a concrete plan to give it more character. **Do not implement changes.**

> Propose a distinctive visual direction suited to a learning workspace. Explain how typography, color, spacing, geometry, layout, and interaction details can create a recognizable identity. Avoid simply replacing every rounded corner with a square one. Preserve reading comfort, accessibility, responsive behavior, and clear navigation.

Interpretation: refine the current experience using concrete production evidence. The direction below is proposed, not a replacement for an accepted product contract. This document is the owning record for this bounded design request. Existing visual options remain registered. No idea is rejected or removed by this audit.

## F1: Audit findings, ranked by impact

### F1.1: Functional presentation defects make the interface look unfinished

Observed on Study before revealing an explanation: multiple Previous/Next action groups and Got it/Missed render simultaneously. Browser measurement showed `data-acts=revealed` and `data-acts=rating` both had `hidden=true`, `display:flex`, and 46px height. This is a verified defect, not a preference. `surfaces/study.py:90` assigns `.acts{display:flex}` while lines 244 and 249 mark the other groups hidden. The CSS defeats the intended visibility state. This also exposes unnecessary controls in the accessibility tree.

Observed on Quiz: the four table-response dropdowns were 19px tall with 13.3333px text. They appear as bright native white slivers inside the dark question panel, on desktop and mobile. `surfaces/quiz_page.py:130` styles row layout but has no corresponding native select treatment there. Lines 578 and 584 emit table/build selects. This fails the project's own 44px control target and 16px control-text contract. It is not automatically a WCAG AA failure because native controls and target spacing have exceptions.

Observed on Courses: Start walkthrough, Skip for now, and Replay walkthrough are small browser-default buttons beside a styled course CTA. See `surfaces/daemon.py:1945` and the shared `button.go` rule in `surfaces/presentation.py:230`.

Priority: P0 for study visibility, P1 for control consistency. Fix these before judging geometry.

### F1.2: The course workspace has no consistent visual navigation frame

Observed on course Overview and Course map: eight area links render as a default bulleted list above content. The current area has an `aria-current` attribute in code but no distinct visible treatment in the inspected Classic screen. At 375px, this list and the course heading occupy roughly the first 320px before the area heading.

The shelf has no persistent visible application navigation. The lesson offers a Courses link. Study and Settings use an itembank backlink. The quiz uses a session context strip. The user repeatedly has to infer which level each page belongs to.

Code references: `surfaces/daemon.py:1110` (`_course_frame`), `surfaces/daemon.py:1996` (`_course_shelf_body`), `surfaces/presentation.py:474` (`surface_shell`). The shelf renderer explicitly says its course classes are hooks rather than styling. This is an integration gap, not an argument for inventing more routes.

The accepted 17A direction selected Structured studio, sidebar, and indigo, but explicitly changed prototype defaults only. Production still defaults to Classic and teal in `surfaces/looks.py:42` and `surfaces/theme.py:29`. See `phases/17A-visual-system-component-foundation/17A-DIRECTION.md`. Treat this as an unresolved design-to-production handoff, not proof that the current default was accidentally overwritten.

Priority: P1. Navigation coherence has more impact than changing all cards.

### F1.3: Unavailable help competes with the task

Observed on Quiz before answering: all six locked hint tiers render as individual panels. Each was 74px tall on desktop, before gaps. The learner sees internal labels such as TIER 4 DISCRIMINATOR and TIER 5 REVEAL. On mobile this creates a long sequence below Submit answer.

References: `surfaces/quiz_page.py:186` to the locked hint rules and `_hint_card` around line 620. Locked copy uses 12px monospace while explaining a recovery action. This is inconsistent with the project's 16px minimum for recovery text. The 17B UI specification also calls for hints collapsed by default without pre-announcing a reveal.

The number of panels and the exposed tier vocabulary are observed. Calling their prominence distracting is a design judgment. The proposed remedy changes presentation only. The runtime still determines every available hint and release.

Priority: P1 after F1.1. Show one help entry point and runtime-permitted content on request.

### F1.4: Repeated containers and drifting type roles weaken identity

Observed: Banks is a stack of similarly weighted rounded boxes. Study nests rounded answer options inside a rounded question card. The lesson encloses sustained reading in another rounded panel. Quiz adds rounded locked-hint panels inside its question panel. The page background, panel fill, border, and repeated rounding do much of the grouping work.

References: `surfaces/presentation.py:210` groups `.card,.step,.state,.empty` under one treatment, and `.row` around line 259 repeats it. `surfaces/lesson.py:147` frames the lesson section. `surfaces/study.py:43` and `:60` frame tabs and answers. `surfaces/quiz_page.py:74` and `:186` frame question and hints.

Radii are not globally extreme in Classic. Most are 8 to 12px. The actual problem is role repetition and hard-coded variations of 5, 7, 8, 9, and 12px. Large pill controls and 22px cards chiefly belong to the optional Neo look in `surfaces/looks.py:137`. A universal anti-pill rewrite would misdiagnose the default.

Typography already has a valuable foundation: Source Serif 4 for reading, iA Writer Quattro for selected metadata, and system sans for controls. But Study uses a 20px sans stem while Quiz uses a 32px serif stem. Study also introduces 11, 13, 14, 15, and 17px sizes outside the shared five-size scale. See `surfaces/study.py:49`, `:56`, `:69`, and `surfaces/presentation.py:150`.

Observed default screens did not show gratuitous gradients or animated decoration. Preserve that restraint. The palette dialog shadow represents elevation and has a purpose. The fixed pill launcher in `surfaces/palette.py:190` is more problematic because it floats over mobile Settings content. Do not remove modal elevation merely to make the design flatter.

Priority: P2. Reassign visual roles before tuning radius values. The preference for editorial structure is subjective.

### F1.5: Secondary settings and empty states lack task hierarchy

Observed on mobile Settings: seven descriptive look cards precede the accent controls. Names, blurbs, mode names, and hex values give theme selection much more space than its importance warrants. References: `surfaces/theme.py:461` and `:589`. Choice is valuable, but its presentation is bulky.

Observed empty Course map: “Nothing has been added…” ends without a next action. This is truthful but not helpful. The fixture is empty by design, so this finding concerns recovery copy and affordances rather than missing course data. References: `surfaces/daemon.py:1127` and the area state supplied by `surfaces/ia.py`.

Priority: P2. Keep all existing looks available. Improve their presentation and explain the next available action for empty areas without inventing functionality.

## D1: Design direction, an annotated learning studio

Disposition: prototype proposal for review. Build on the prior Structured studio selection and the existing reading typography. Recognition should come from a consistent course margin, strong text hierarchy, visible source references, and purposeful study controls. No new font dependency or frontend rewrite is needed to test this direction.

| Code | Rule | Concrete application |
|---|---|---|
| D1.1 Typography | Retain the five shared sizes: 12, 16, 18, 20, 32px. Use Source Serif 4 for course titles, lesson headings, sustained prose, and question content. Use system sans for navigation and controls. Reserve Quattro for short locators, item numbers, and denominators. Use 400/600 weights where available. Recovery and action text stays at least 16px. | The shelf course title becomes a serif anchor. A small source locator sits beside it. Quiz and Study use the same reading voice, while stem size responds to activity density rather than differing by renderer accident. |
| D1.2 Color | Prototype indigo from the recorded 17A choice as the default accent. Continue deriving accessible mode values through theme.py. Retain existing base and semantic palettes for the first pass. Accent identifies current navigation, focus, and the primary action. Status must also have a label or symbol. | A narrow indigo current-area marker and one filled Continue button identify where to go. Ordinary course rows remain neutral. Learner-selected accent and look preferences remain respected. |
| D1.3 Geometry | Keep the 6/8/12px radius vocabulary, assigned by role. Use 6px on controls, 8px on answer groups and popovers, and 12px on dialogs or deliberately separate activity surfaces. Use unboxed rows and rules for library inventories and reading sections. Circles remain valid for radio controls and numbered markers. | Banks becomes title-led rows with aligned secondary actions. Lesson sections use spacing and heading rules. A practice response group can retain gentle rounding because it represents an actionable unit. No blanket square-corner change. |
| D1.4 Layout and rhythm | Preserve the 4/8/16/24/32/48/64 spacing scale. Use 8px within a control group, 16px within a content unit, 32px between sections, and 48px between major reading movements. On desktop, use a roughly 224px course rail and a flexible main region. Keep the existing 59ch prose measure and 1.65 leading within that region. | The course rail holds the current course and area links. A lesson remains a comfortable narrow reading column even when its workspace grows wider. On mobile, show course and current area above a native navigation disclosure with all areas reachable. |
| D1.5 Interaction | Use explicit active, selected, focused, disabled, and unavailable states. Keep 44px targets even in compact density. Cap purposeful transitions at 120 to 150ms and honor reduced motion. One visible action group per study state. Move Search & commands into the shell where present. | Hints begin as one accessible disclosure or runtime-supported help action. Released teaching content opens inline with focus retained. Source and note details use margin or inline disclosures rather than permanent surrounding cards. Preserve reading position and normal back navigation. |

An empty map should say what the learner can do next using an existing supported route. A filled shelf should distinguish title, resume cue, status, and action without making every course a dashboard. A long lesson should read like an annotated text, with an activity surface only where the learner acts.

Existing looks remain registered. A new illustrated or textured background is backburner, with reconsideration only if the plain typography and layout prototype still lacks identity in user review. Its costs are asset maintenance, dark-mode variants, and reading distraction. No existing option is rejected.

## A1: Fix plan in dependency order

Owner: the next UI implementation task. Reviewer: the user for visual direction and representative usability. Every stage preserves runtime, parser, scoring, disclosure, stored settings, course IDs, and accepted source files as the existing authorities. The HTML and CSS remain derived views. No data migration or external service is required. Undo is a scoped code diff reversal. Recheck concurrent edits before applying any patch.

| Code / priority | Result and scope | Affected files and dependencies | Exit evidence |
|---|---|---|---|
| A1.1 / P0 | Honor hidden study groups. Give table/build selects and walkthrough buttons the shared control treatment. | `surfaces/study.py` STUDY_CSS and action-state markup, `surfaces/quiz_page.py` row controls, `surfaces/daemon.py` walkthrough markup, `surfaces/presentation.py` shared controls. No visual-default change needed. | Browser computed visibility agrees with hidden state. Only valid controls appear in the accessibility tree. Selects and onboarding controls meet the project target and text sizes. |
| A1.2 / P1 | Settle one production component contract and apply the course shell to shelf and course areas. Define active-area, course heading, navigation disclosure, and row rules. | `surfaces/presentation.py` shared shell/CSS, `surfaces/daemon.py` `_course_frame` and `_course_shelf_body`. Review `surfaces/looks.py` compatibility. Reference `prototypes/17a/structured-studio.css`, but do not ship the prototype harness. Depends on A1.1. Record the proposed visual contract alongside 17A before broader adoption. | Desktop and mobile shelf-to-course navigation share a recognizable frame. All existing area routes and current-state semantics survive. |
| A1.3 / P1 | Reduce quiz hint scaffolding and align learning typography. Preserve distinct reading and response surfaces. | `surfaces/quiz_page.py` hint renderer and served script, `surfaces/lesson.py` LESSON_CSS and reader navigation, `surfaces/study.py` stem and action styles. Depends on A1.2 rules. | One initial help entry point. No early keyed disclosure. Reader measure is preserved. Study and Quiz use coherent type roles. |
| A1.4 / P2 | Extend rows and hierarchy to Banks, populated course areas, and empty states. Reposition global search without losing keyboard access. | `surfaces/daemon.py` bank and course row renderers, `surfaces/presentation.py` row and state primitives, `surfaces/ia.py` existing notices, `surfaces/palette.py` launcher. Inspect `surfaces/home.py` alternate homes before extending the shell. Depends on A1.2 and populated fixtures. | Library rows remain scannable with long titles. Empty-state actions lead to existing supported functionality. Search does not cover mobile content. |
| A1.5 / P2 | Compact the settings catalogue and complete cross-look coverage. Consider default promotion only after visual review. | `surfaces/theme.py` settings layout and default policy, `surfaces/looks.py` overlays, `surfaces/presentation.py` tokens. Depends on all earlier stages. | Every existing look remains selectable. Custom accents retain contrast derivation. No saved preference is silently reset. Default indigo adoption is explicitly reviewed rather than implied by the prototype. |

Failure conditions include lost current-area indication, hidden controls still focusable, disappearing course switching, clipped prose, changed keyed disclosure, or preference resets. Any one prevents completion of its stage. The maintenance obligation is one shared role definition with surface-specific layout only where the task differs. Do not create another parallel token system.

## V1: Verification plan

| Code | Check | Acceptance criteria |
|---|---|---|
| V1.1 Visual consistency | Capture the same synthetic states before and after at 1280, 768, 375, and 320px. Include shelf, populated and empty course areas, reader, quiz, study front/reveal, settings, and open search. Repeat representative screens in light, dark, OLED, high contrast, and a custom accent. | Same roles use the same typography, controls, radii, and spacing. Long titles wrap. No orphan controls or accidental nested cards. User reviews whether the identity feels distinctive and comfortable. |
| V1.2 Usability and state | Walk shelf to course to reading to practice to evidence and back. Test resume, browser back, empty course, unavailable source, and pending review. Exercise Study front/revealed/learn groups and Quiz allowed hint states. | Current location and next action remain clear. Hidden groups have zero rendered area and no focusable descendants. No premature reveal or invented progress. Walkthrough controls remain operable without script. |
| V1.3 Accessibility | Keyboard-only traversal, visible focus, Escape and focus return for overlays, screen-reader review, 200% text enlargement, 400% zoom/reflow, reduced motion, and forced colors. Measure text/control contrast using the existing theme helpers. | Project controls retain 44px targets and 16px action text. Text contrast is at least 4.5:1 and meaningful control/focus boundaries at least 3:1. Labels accompany semantic colors. Representative screen-reader results require human verification. |
| V1.4 Mobile and reading | At 320/375px, check expanded navigation, course switching, long answer text, table/build selects, glossary, wide tables, software keyboard, and bottom safe area. | No page-wide horizontal overflow. Essential navigation is reachable without truncation. Wide data scrolls locally when necessary. Reading retains useful measure and rhythm. Search and sticky chrome do not cover a focused control or final paragraph. |
| V1.5 Regression gates | Run targeted `tests/stylesheet_roundtrip.py`, `tests/presentation_roundtrip.py`, `tests/theme_roundtrip.py`, `tests/ia_route_roundtrip.py`, `tests/surface_roundtrip.py`, `tests/hint_roundtrip.py`, and relevant existing JS hint tests during implementation. Run `python3 scripts/preflight.py` before implementation handoff. | All required gates pass for the reviewed revision. Add browser regression coverage for hidden action groups and native control sizes because static markup tests cannot prove either. Reuse the preflight result rather than repeating suites it already runs. |

WCAG context: [Target Size Minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) defines a 24px AA baseline with exceptions. The project's 44px target is intentionally stronger. [Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) supplies the 320 CSS pixel reflow check and permits exceptions for genuinely two-dimensional content. This audit does not claim standards conformance from screenshots.

## Bounded first implementation pass for review

Proposed scope: A1.1 plus the shelf and course-frame portion of A1.2 only. Four application files: `surfaces/presentation.py`, `surfaces/daemon.py`, `surfaces/study.py`, and `surfaces/quiz_page.py`. Add only regression coverage needed for those changes. Use the existing palette, fonts, and radius tokens. Do not yet change the default look or accent.

Review output: before/after views of a two-course shelf, one course overview, Study before reveal, and Quiz with table responses at 1280 and 375px. Include a populated and empty course example. Acceptance requires a visible current course area, shared onboarding controls, a mobile navigation disclosure, exactly one study action group, and 44px selects.

This pass deliberately stops before reader restyling, hint presentation changes, settings redesign, and global default promotion. It is small enough to review for identity and behavior before extending the rules. No application changes were implemented during this audit.
