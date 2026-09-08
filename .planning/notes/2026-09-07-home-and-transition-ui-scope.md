---
title: Home presentations and transition-complete UI scope
date: 2026-09-07
context: Comparative scope from a live Courses screenshot, existing UI audits, learning-platform documentation, and public repository leads
status: exploratory research synthesis, not an implementation commitment
---

# Home presentations and transition-complete UI scope

## User problem observed

The inspected Courses screenshot does not read as a composed application home.
The product title, page title, navigation, onboarding, course identity, course
state, and primary action occupy one loose column with similar visual weight.
The course is not visibly bounded as an object. The action repeats the course
name instead of naming the next learner action. Persistent walkthrough controls
compete with the course after first use. Large unused space does not create
calm because the remaining elements lack regions and hierarchy.

This is evidence about one rendered state. It does not establish the quality of
populated shelves, completed courses, multiple-course sorting, mobile behavior,
or post-assessment transitions.

## Existing project evidence reconciled

This scope extends existing work rather than opening another general UI survey.

- `UI-CHARACTER-AUDIT-2026-09-06.md` already records inconsistent controls,
  missing application and course navigation frames, excessive hint scaffolding,
  repeated containers, weak empty states, and the selected Measured Field Guide
  and Learning Trajectory Deck presentation profiles.
- `TRANSITION-AUDIT-SYNTHESIS.md` already preserves the source-to-course object
  and authority transition. It does not provide a screen-by-screen learner
  transition matrix.
- `research/phase-16/09-app-flow-information-architecture.md` and
  `16B-UI-SPEC.md` already define course-first areas, stable routes, resume,
  focus restoration, and degraded states.
- `research/2026-09-05-open-source-absorption.md` already surveys Canvas,
  Moodle, PrairieLearn, and open corpora. Its open-source pass concentrates on
  assessment, content, and licensing behavior rather than home composition and
  completion flows.
- `PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md` already owns the first
  shared-profile implementation slice. This note adds comparative home and
  transition evidence for that future work. It does not expand the active Reach
  critical path.

## Current comparative findings

### Home and dashboard patterns

1. Canvas supports course-card, list, and recent-activity dashboard views. Its
   cards bound course identity and move less common actions behind a menu. This
   supports multiple projections over one course set, not all information on
   one page. Sources: [Canvas card view](https://community.instructure.com/en/kb/articles/662815-how-do-i-view-my-courses-in-the-card-view-dashboard) and
   [Canvas list view](https://community.canvaslms.com/t5/Student-Guide/How-do-I-use-the-to-do-list-for-all-my-courses-in-the-List-View/ta-p/345).
2. Moodle separates course overview from a time-oriented dashboard. Its
   timeline groups overdue, today, next seven days, and later work, and it
   remembers the active overview tab. Source: [Moodle course overview](https://docs.moodle.org/34/en/Course_overview).
3. Google Classroom presents active class cards alongside due-soon work. Empty
   modules hide automatically, and collapsed modules remain collapsed. Source:
   [Google Classroom homepage](https://support.google.com/edu/classroom/answer/17231999?hl=en).
4. Khan Academy places the most active work first and separates current work
   from past or overdue work. This is evidence for a resume-first projection.
   Source: [Khan Academy Learner Home](https://support.khanacademy.org/hc/en-us/articles/360030629852-What-is-my-Learner-Home-page-and-what-can-I-do-there).
5. Duolingo uses a guided path to reduce uncertainty about the next activity.
   Open edX uses course outlines, sidebar navigation, and completion markers to
   preserve location. These patterns fit inside a course more than on the
   global shelf. Sources: [Duolingo path rationale](https://blog.duolingo.com/new-duolingo-home-screen-design/),
   [Open edX progress](https://docs.openedx.org/en/release-teak/learners/SFD_check_progress.html), and
   [Open edX course sidebar](https://docs.openedx.org/en/latest/learners/sidebar_view_course_section.html).

These observations are facts about the cited products. Applying them to
itembank is a recommendation that requires comparative prototypes and learner
review.

### Public repository leads for deeper inspection

- [`instructure/canvas-lms`](https://github.com/instructure/canvas-lms) and
  [`instructure/instructure-ui`](https://github.com/instructure/instructure-ui):
  dashboard composition, course-card semantics, global versus course
  navigation, to-do transitions, focus behavior, and component contracts.
- [`moodle/moodle`](https://github.com/moodle/moodle) and
  [`moodlehq/moodleapp`](https://github.com/moodlehq/moodleapp): course overview,
  timeline grouping, quiz attempt completion, mobile navigation, and return
  behavior.
- [`openedx/frontend-app-learner-dashboard`](https://github.com/openedx/frontend-app-learner-dashboard)
  and [`openedx/frontend-app-learning`](https://github.com/openedx/frontend-app-learning):
  learner home, course cards, completion screens, breadcrumbs, course exit, and
  declared frontend plugin slots. Open edX explicitly exposes learner-dashboard
  course-list, course-card-action, empty-state, course-exit, and view-courses
  slots. Source: [Open edX plugin slots](https://docs.openedx.org/en/latest/site_ops/references/frontend-plugin-slots.html).
- [`learningequality/kolibri`](https://github.com/learningequality/kolibri):
  offline-first learner home, course-unit navigation, quizzes, interruption,
  synchronization, and degraded operation.

These repositories are evidence sources, not code sources. Their licenses and
architectures differ from itembank. Absorb behavior, state vocabulary, and
testable interaction patterns. Do not vendor or translate implementation code.

## Proposed comparative presentation set

All presentations use the same courses, routes, durable learner state,
recommendation evidence, assessment authority, and recovery behavior.

| Presentation | Primary question | Main composition | Suitable profile emphasis |
|---|---|---|---|
| Resume | What should I do now? | One exact continuation or next-action panel, then quieter courses and attention items | Trajectory Deck |
| Shelf | Which course do I want? | Responsive course rows or cards with state, exact resume cue, and one short action | Either profile |
| Agenda | What needs attention? | Overdue, today, upcoming, revisions, and recently completed groups across courses | Trajectory Deck |
| Path | Where am I in this course? | Unit and objective path with current position, available activities, review, and return points | Field Guide for reading, Trajectory Deck for movement |

These begin as Prototype dispositions. Comparative evidence may retain all as
user-selectable views, combine some, or supersede weak variants. Implementing
all means building reversible comparable projections first. It does not require
four permanent home implementations.

## Shared home contract

- One compact application frame identifies the product, current level, global
  destinations, and settings without duplicating the page heading.
- First-use guidance is a dismissible region. After completion, replay moves to
  Help or an unobtrusive secondary action.
- Every course object contains identity, attention state, exact resume cue,
  relevant evidence with its denominator, and one short next action. Unknown,
  unavailable, not started, interrupted, changed, and complete remain distinct.
- Empty regions hide when absence is uninformative. Meaningful empty states name
  the next supported action. Secondary metadata stays available without
  competing with the learner task.
- Wide and narrow layouts preserve the same routes and semantics. Supporting
  panes become reachable destinations or disclosures. They do not disappear.

## Transition-complete flow matrix

The future comparison must render and walk every row below in both selected
presentation profiles and every retained home projection.

| From | Event | Required destination and preserved context |
|---|---|---|
| First launch | Walkthrough completed, skipped, interrupted, or replayed | Home remains usable. Guidance state is durable and reversible. No course or source-root grant is implied. |
| Home | New course, one course, many courses, corrupted course, or archived course | Exact course state and a supported next action appear without merging identity or hiding plain-file recovery. |
| Home | Start or resume | Enter the precise course area, lesson locator, activity, or review state. Back returns to the prior home projection and position. |
| Course overview | Choose reading, lesson, practice, test, source, map, note, evidence, or build/review | Stable parent and back semantics preserve course identity, focus, scroll, and unsaved-work warnings. |
| Lesson or source | Open a definition, citation, prerequisite, note, or related activity | Return to the exact passage and focus target. A model or renderer outage retains the static instructional route. |
| Practice | Correct, incorrect, retry, skip, stop, or interruption | Runtime-authorized feedback appears. Stop returns to a truthful home or course state with an exact resume cue. |
| Quiz or exam | Submit an item, finish, time out, interrupt, or encounter pending prose review | Assessment mode controls disclosure. Completion distinguishes settled, pending, incomplete, and invalid states before offering review, evidence, course continuation, or home. |
| Quiz or exam result | Review allowed, review locked, remediation offered, or course action recommended | The learner sees why an action is available, what evidence supports it, and where Back or Home leads. No UI invents a score or hint tier. |
| Any activity | Navigate home during active or unsaved work | Confirm only when loss is possible. Preserve or explicitly abandon the activity according to runtime and journal authority. Browser Back must not create a second submission. |
| Return later | No changes, course revision, source unavailable, stale derivative, or unfinished operation | Separate stopping point, changes since last visit, due or recommended work, and recovery action. Do not compress them into one progress label. |
| Course completion | Objectives satisfied, formal requirement pending, or course merely exhausted | State exactly what completed means, retain access to sources, notes, evidence, and review, and offer the next user-owned action without invented mastery. |

## Acceptance evidence for later prototypes

1. The learner can name the page level, current course, current task, and next
   action from every representative state.
2. Starting, stopping, finishing, returning home, using browser Back, and
   resuming preserve one runtime session and do not duplicate attempts.
3. The same transition graph works at 1280, 768, 375, and 320 CSS pixels with
   keyboard, touch, screen-reader-oriented checks, 200 percent text, reflow,
   reduced motion, no script, offline operation, and model unavailable.
4. Presentation switching preserves the current route, durable state, focus or
   meaningful focus successor, reading locator, browser history, and unsaved
   work warning.
5. User comparison records which projection makes each job clearest. A
   retained view must outperform or serve a distinct job from the simpler
   alternative. Visual novelty is not acceptance evidence.

## Scope boundary and next action

The current recommendation is to keep the transition matrix Core and the four
home presentations Prototype. The future UI owner should inspect the named
repositories and current product behavior, update this synthesis with missing
states, then build one fixture-backed comparative prototype. No requirement,
route, schema, scorer, or production default changes through this note.

## Future re-research triggers

This note is a dated baseline. The future UI owner rechecks only affected
evidence when a named platform or repository materially changes its home,
navigation, completion, accessibility, extension, offline, or recovery
behavior; when a prototype or real sitting exposes an omitted transition; when
itembank adds a new activity, presentation profile, shell, input mode, or
authority boundary; or when a source becomes stale, contradicted, unavailable,
or differently licensed.

Fast-moving product behavior and active repository paths are checked again
before the owning UI plan and before final acceptance. Stable principles are
reopened when an observed learner problem or failed gate falsifies them. Each
update records the access date, upstream version or commit when available,
changed assumption, affected finding, and whether the recommendation changed.
The complete landscape is not repeated without a changed assumption or a named
coverage gap.
