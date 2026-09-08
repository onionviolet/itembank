# Phase 20 learning-platform inspiration matrix

**Evidence baseline:** Existing project research checked through 2026-09-07
**Use:** Behavior and test inspiration only. No external code, markup, wording, or assets are copied.

| Platform or pattern | Observed useful behavior | Phase 20 adaptation | Acceptance result and exact evidence | Rejected part |
|---|---|---|---|---|
| Canvas dashboard views | Card, list, and recent-activity projections share one course set. Course identity is bounded and secondary actions recede | Prototype Resume, Shelf, and Agenda over one home state. Keep one short action per course | Adapted and verified by `tests/home_roundtrip.py::check_phase20_projection_contract`, `check_phase20_projection_labels_and_actions`, and `check_phase20_profiles_preserve_behavior`. Agenda remains a registered prototype pending Weibao's comparison | Canvas-style opaque mastery rollups and bank-link mutation behavior |
| Moodle dashboard and timeline | Course overview stays separate from time-oriented attention groups and remembers the active view | Agenda groups overdue, today, upcoming, revision, and recently completed only when those facts exist | Adapted as a registered prototype and verified by the home projection contract. No stable `agenda` setting exists until Weibao accepts it | Certainty-weighted grading and generic plugin behavior do not enter scoring |
| Google Classroom home | Active classes and due-soon work coexist. Empty modules hide and collapsed modules remember state | Hide uninformative empty regions and persist reversible disclosure state | Adapted and verified by home empty-state, configured-mode, and projection fixtures. Course data and stable routes remain unchanged | Teacher-assignment and cloud-account assumptions |
| Khan Academy learner home | Current work is promoted above past or overdue work | Resume projection leads with one exact continuation or evidence-backed next action | Adapted and verified by `tests/home_roundtrip.py::check_next_action_comes_from_evidence` and the profile-preservation fixture | Mastery percentages and engagement proxies |
| Duolingo path | A guided path reduces uncertainty about the next activity | Path projection shows current position, available movement, and review points inside a course | Adapted as a registered prototype and verified by the home projection labels fixture. No stable `path` setting exists until Weibao accepts it | Streaks, punitive engagement loops, and a single mandatory path |
| Open edX learning shell | Course outline, sidebar, completion state, exit, and extension slots preserve course context | Use stable course navigation and named adapter seams with declared fallback and removal recovery | Adapted and verified by profile course-context checks, IA-route checks, and `tests/settings_roundtrip.py::check_adapter_manifest_and_no_loader` | Frontend slots that can replace scoring, evidence, rights, or route authority |
| Kolibri offline learner flow | Offline-first home, unit navigation, interrupted quizzes, synchronization, and degraded operation | Treat offline as normal capability state and interruption as exact resume, not generic failure | Adapted and verified by `tests/ia_route_roundtrip.py::check_first_launch_offline`, `check_walkthrough_interruption`, profile degraded-state checks, and serve lifecycle checks | Server synchronization as an assumed requirement |
| PrairieLearn generated questions | Many concrete variants can come from one authored form | Keep as an authoring-time proposal outside Phase 20. UI may show variant provenance when already present | Rejected for Phase 20. Diff review and profile tests show no runtime generator, new item type, or scoring path. Future authoring owner is named in the crosswalk | Runtime generation that destabilizes item identity and evidence |
| Runestone and executable textbook patterns | Reading, prediction, inline check, feedback, and continuation form a coherent loop | Preserve lesson-to-check-to-practice flow and make the activity transition explicit | Adapted and verified by the profile course-to-lesson-to-practice context fixture and serve lifecycle contract | A separate scorer or JavaScript-only lesson meaning |
| H5P interactive content | Rich interactions benefit from a shared capability description and fallback | Use one internal capability-adapter declaration with semantic input and static fallback | Adapted and verified by the versioned `presentation.surface_adapter_manifest()`, settings adapter tests, component plain-HTML checks, and profile parity | Embedded script authority, opaque packages, and unreviewed external loading |
| Anki and FSRS separation | Review scheduling can remain distinct from course progress and itembank due state | Keep review cues labeled by source and denominator | Adapted and verified by `tests/home_roundtrip.py::check_phase20_projection_labels_and_actions` | One blended progress or due score |

## Cross-platform rules adopted

- Multiple projections may exist over one state, but each retained projection must serve a distinct learner question.
- Resume is exact and durable. A generic Continue button without a named destination fails.
- Course navigation and activity completion are separate. Leaving a screen does not settle a task.
- Offline, interrupted, unavailable, unknown, and empty remain distinct.
- Extension seams are narrower than plugins. They cannot replace canonical authority.

## Freshness and falsification

Recheck an external source only if a Phase 20 decision depends on changed current behavior, a repository materially changes the cited area, or a working prototype falsifies the adaptation. The phase does not repeat a broad platform survey merely to increase coverage.
