# LMS depth and complete learner flows

Date and access date: 2026-09-18. Status: research recommendations for root synthesis.
Owner: LMS research lane. Scope: public LMS behavior, representative upstream
source, and local historical planning. No private course material was accessed.

## Finding and evidence boundary

F1. Absorb complete stateful tasks before adding another dashboard layout.
The strongest recurring pattern is a course destination that connects a named
activity to saved work, an explicit finish action, a truthful result, and a
valid next destination. LMS depth includes failed and interrupted transitions.

F2. Keep completion axes separate. Moodle mobile distinguishes a locally
finished quiz from one submitted to the site. Open edX has different course-exit
experiences for passing, non-passing, and future content. PrairieLearn separates
formative homework from exam instances and preserves started exams when their
definition changes. These are useful state contracts, not reasons to import
their grading models. Evidence: D3, S3, D6 below.

F3. Exact passage resume could exceed the documented unit-level Open edX
benchmark, but it is not established by this research. The accepted Itembank
reading contract explicitly leaves exact cursor resume deferred. Root must
measure current behavior before calling any capability missing or achieved.

Evidence classes: **D** is official documentation retrieved today. **S** is a
pinned upstream source or test inspected today, not executed. **H** is prior
research, not refreshed behavior. **L** would mean live product interaction.
There is no L evidence in this lane. Public documentation and source were
inspected, but no authenticated LMS or mobile app was operated. No learning
efficacy, overall parity, or human accessibility claim follows from this report.

## Prior research reconciled

Read the [September 5 absorption report](../2026-09-05-open-source-absorption.md)
for confidence diagnostics, countable outcome evidence, pinned bank selection,
generator questions, source licensing, and parked interchange formats. Read the
[September 7 flow scope](../../notes/2026-09-07-home-and-transition-ui-scope.md)
for Resume, Shelf, Agenda, and Path projections and its transition matrix.
Those are different scopes and both remain relevant.

Sampled Phase 16 [program landscape](../phase-16/05-learning-program-landscape.md)
sections 4.2, 4.11, and 5, [hierarchy and progress](../phase-16/08-curriculum-hierarchy-progress.md)
source and progress sections, and [app flow](../phase-16/09-app-flow-information-architecture.md)
sections 2 through 4. These already require publication revision, semantic
resume, stable hierarchy, offline readiness, and explicit completion criteria.
Their August claims about unshipped Itembank surfaces are historical, not a
current implementation audit. Root owns that audit.

The binding [course contract](../../SOURCE-TO-COURSE.md) learner-experience and
durable-reading sections require accepted artifacts to be reachable in the
ordinary course flow. Reading declarations do not become scores or mastery.
This report samples the latest overhaul vision entry and the current state
front matter. It does not claim an exhaustive vision or codebase audit.

## Prioritized capability and acceptance table

Priority is proposed order, not a new milestone commitment. Each row identifies
a complete observable task and an owner seam for root to map to current code.

| ID / priority / disposition | Absorb and benchmark | Observable acceptance task | Owner, dependency, failure condition |
|---|---|---|---|
| C1 / P0 / Core | Exact continuation with stateful home and course navigation. Canvas card destinations, Open edX Resume, Kolibri pause. D1, D4, D5, S1, S2 | Start an activity, answer once, stop, go Home, restart, resume, then finish. Session identity, response, disclosure tier, and meaningful focus remain correct. Back produces no duplicate attempt. | Shared navigation and runtime projection. Depends on stable IDs and saved session state. Fails if Resume silently starts anew or loses work. |
| C2 / P0 / Core | Explicit finish and result handoff. Open edX exit branches and PrairieLearn save/grade/close. S3, S8 | Finish a mixed objective/prose sitting. Show settled counts, pending review, and unattempted work separately. Review, Continue course, and Home each reach a valid destination. | Runtime result state and surface presenter. Depends on authoritative completion and disclosure. Fails if pending means wrong or end-of-content means passed. |
| C3 / P0 / Core | Honest offline readiness and recovery. Moodle mobile and Kolibri. D3, D5 | Before disconnecting, inspect missing assets and unavailable capabilities. Disconnect, read/practice supported work, restart, then reconnect. Never display saved or submitted without its authoritative acknowledgement. | Packaging, asset manifest, runtime journal. Depends on capability inventory. Fails on silent missing media, lost evidence, or automatic conflict overwrite. |
| C4 / P1 / Core | Course activity inventory with type, location, availability, and completion criterion. Moodle web/mobile. D2, S5, S6 | Find a reading, practice set, formal test, and reviewed lesson through their course. Explain a locked or unavailable item. Rename a reading without changing its completion, then revise its range without inheriting completion. | Course projections and accepted activity revisions. Depends on objective/activity bindings. Fails when accepted output exists only as a file or isolated URL. |
| C5 / P1 / Prototype | Resume, Shelf, Agenda, and Path as projections of the same objects. Canvas, Moodle, Classroom, Khan, Duolingo. D1, D2, D7-D9 | Compare the same multi-course fixture in each view. Pick due work, resume work, find another course, and revisit a completed activity. Retained views must serve a distinct task. | Presentation owner over shared route/state model. Depends on C1 and truthful due metadata. Fails if view changes alter activity identity or reorder user choices unexpectedly. |
| C6 / P1 / Registered | Review queue, confidence diagnostics, issue reporting, and actionable evidence. PrairieLearn issue reporting plus H1 | Report an ambiguous item with its revision and attempt reference. Find it in a local review queue. A confident incorrect response links to authorized explanation and suitable remediation with count/denominator. | Evidence and build/review owners. Depends on available confidence input and reviewed issue state. Fails if the UI modifies scoring or claims a confidence inference it never collected. |
| C7 / P1 / Core | Change-aware continuation and revision pinning. PrairieLearn exams and Phase 16 publication model. D6, H3 | Start a test, accept a new bank revision elsewhere, and resume. Show the pinned revision or a clear refusal. Revisit a changed lesson and distinguish last position from newly required work. | Accepted revisions and runtime. Depends on fingerprints and conflict handling. Fails when old evidence silently transfers to changed content. |
| C8 / P2 / Registered | Learning-resource navigation, bookmarks, transcript seeking, and return-to-passage. Kolibri and Open edX documentation. D4, D5 | Open a citation or supporting resource from learning, inspect it, and return to the same task. Download/export only permitted resources and retain source attribution. | Reader/source owner. Depends on source locators, rights, and fallback. Exact cursor resume needs its own accepted design. Fails when a side trip destroys context. |
| C9 / P2 / Backburner | Cohorts, scheduling, review bundles, discussions, certificates, and institutional exchange. H3 | Before implementation, name one real external consumer and walk its permission, export, review, and return path with a synthetic bundle. | Interop/review owner. Depends on an actual multi-user need. Cost drivers are identity, permission, moderation, and format maintenance. Revisit when a named consumer cannot complete a supported workflow. |

## Lifecycle transition matrix

These are proposed Itembank acceptance contracts. They combine documented
benchmarks with the local authority model and must not be misread as claims
that every competitor supports every row. Each row needs desktop, narrow-screen,
keyboard, and script-free checks wherever that surface supports a static path.

| ID | Transition | Required observable destination and preservation | Failure / degraded branch |
|---|---|---|---|
| T1 | First launch to Home | Optional guidance leads to a usable shelf with one supported open/create action. | An absent root, inaccessible root, and empty root have different explanations. Guidance does not grant read or write authority. |
| T2 | Home to start | Course, objective, activity, mode, expected revision, and valid start action are explicit. | Unsupported or unavailable activities explain a recovery route before starting. |
| T3 | Home to resume | Restore the existing session or accepted reading occurrence and its exact supported locator. Restore useful focus. | Changed or deleted target opens a recovery state with historical context. No silent replacement. |
| T4 | Learning to supporting source and back | Preserve course and originating passage. Citation, glossary, note, and media controls have an explicit return path. | Missing external source retains the accepted local fallback and its stale/availability label. |
| T5 | Answer to feedback to next | Runtime grants the feedback. It stays until explicit advance. Next moves focus to the next task. | Network ambiguity uses the same idempotent submission identity. A retry must not create a second scored event. |
| T6 | Stop to course/Home | Save acknowledged work and expose a truthful Resume cue. Stop is distinct from finish and abandon. | Warn only for possible loss. If saving fails, retain the draft and give retry or safe-copy recovery. |
| T7 | Active work to browser Back/Home | Stable parent route and return locator survive. Previously acknowledged responses remain immutable as required. | Stale tabs cannot overwrite current work. Back does not resubmit POST data. |
| T8 | Finish request to summary | Show incomplete work and the consequence of finalization when relevant. Runtime closes exactly once. | Double click, refresh, or retry returns the same closure result. Failed persistence is not success. |
| T9 | Finished to result/review | Settled, pending, incomplete, invalid, and disclosure-locked states are distinct. Offer only permitted review. | Pending prose retains a review route. An unavailable reviewer does not become a zero. |
| T10 | Result to continue/Home | Next learning activity has a reason and stable course identity. Home carries updated evidence and exact continuation. | No next activity gives a truthful end state and access to review, notes, sources, and evidence. |
| T11 | Course end to later return | Distinguish exhausted available material, met course requirements, future content, and review pending. | New accepted material is shown as changed scope. Prior course status is not silently rewritten. |
| T12 | Online to offline | Report local resources and capability losses. Continue supported learning with durable local state. | A disconnected loopback server differs from unavailable internet or model. Unsupported execution offers static content. |
| T13 | Offline to available service | Reconcile explicit queued operations, if that deployment has a remote service. Local-only completion needs no invented sync gate. | Unsynced, conflict, failed, and accepted remain separate. Never use device time alone as overwrite authority. |
| T14 | Error/crash/restart | Last accepted state survives with the next safe action. User can reach Home without destroying recovery context. | Disk full, denied permission, invalid session, and future schema each report the failed durable operation. |
| T15 | Accepted revision changes during work | An active assessment remains pinned or refuses safely. Changed reading demand creates a new revision. | No inferred completion transfer. A stale derivative can be rebuilt without replacing the canonical file. |
| T16 | Export to restore | Restore on a clean offline instance, validate manifest, and report lost capabilities or records. | An export button or readable ZIP is not a successful recovery test. |

## Integration suggestions and depth gates

D1. Start with C1 and C2 as one complete vertical task. Build one shared
transition presenter over runtime-provided state and route identity. The same
synthetic course should exercise stop, Home, restart, resume, finish, pending
review, and Continue course. Root selects actual edit points after live-code
inspection. Do not implement separate result logic per surface or skin.

D2. Require a small state fixture family alongside every new presentation.
Use not-started, active, stopped, finished/settled, pending-review, unavailable,
stale/conflict, and invalid examples. Compare the same state across views.
Test focus placement and dialog dismissal like the Instructure UI specimen,
but keep Itembank's own markup and static fallback. Upstream tests are behavior
examples, not templates to copy. The InstUI site yielded no usable body text in
this tool, so its inspected test file is the evidence for these recommendations.

D3. Derive a course activity projection from accepted objects before broadening
visual layouts. Keep dates, completion declarations, evidence, availability,
and revision status as independent fields. A date becoming past cannot decide
that an activity is complete. A green check cannot imply learning mastery.

D4. Add an offline capability report to the existing package/recovery seam.
List missing local assets, execution/model dependencies, static alternatives,
write durability, and fingerprint status. Borrow Moodle's precise state
language, not its question-wise timestamp conflict policy. Cross-device sync
is a separate deferred design with explicit conflict semantics.

D5. Preserve assessment depth as bounded later capabilities. PrairieLearn's
question variants and saved exam instances suggest deterministic generation,
seed/variant identity, authored validation, and revision pinning. The existing
parser and scorer remain authorities. A generator is not permission to execute
arbitrary source or to add a second grader. Confidence diagnostics, item issue
review, and reusable stimulus/pinned bank selection retain the September 5
routes until root verifies their present implementation and consumer.

Every adopted slice needs a named implementation and maintenance owner, durable
state authority, failure test, migration behavior, and rollback. Prefer additive
presentation/state projection first. Do not backfill completion or fabricate
resume history for legacy records. Any new durable format requires the existing
review, compare-and-swap journal, and accepted-revision process. Undo restores
the prior valid revision without deleting attempt history.

Parity evidence is successful completion of the same task in both products,
with comparable state and failure conditions. An advantage claim needs an
additional demonstrated task, such as exact passage recovery with local data
after restart, plus user evaluation. A screenshot, feature label, or unexecuted
test is insufficient. Human accessibility and learning-benefit gates remain open.

## Source ledger

All D and S entries were accessed 2026-09-18. Dates below are publication or
review dates where visible. An undated page is not assumed to describe the
latest deployed version. Code SHAs identify the inspected snapshot, not a
release deployed by a school.

| ID | Source and date | Observed fact used |
|---|---|---|
| D1 | [Canvas Card View guide](https://community.instructure.com/en/kb/articles/662815-how-do-i-view-my-courses-in-the-card-view-dashboard), undated | Course identity, favorites, activity destinations, menu-based card movement and drag movement. Custom names remain distinct from original identity. |
| D2 | [Moodle 5.2 My courses](https://docs.moodle.org/502/en/Course_overview), edited 2026-01-09 | Filters and card/summary/list views, last-access/name sorting, and course dates interacting with completion. Replaces the September 7 reliance on Moodle 3.4 for this comparison. |
| D3 | [Moodle offline quiz](https://docs.moodle.org/502/en/Moodle_Mobile_quiz_offline_attempts), edited 2023-12-03, and [app offline features](https://docs.moodle.org/501/en/Moodle_app_offline_features), revision date not established | Offline quiz has eligibility restrictions. Finished locally can remain unsubmitted. Unsynced attempts affect continuation. The pages contain version-dependent eligibility wording, so exact mobile support requires a versioned live test. |
| D4 | [Open edX start/resume](https://docs.openedx.org/en/latest/learners/SFD_start_course.html), reviewed 2026-01-23 against Teak, and [progress](https://docs.openedx.org/en/latest/learners/SFD_check_progress.html), undated | Documented resume returns to the last completed unit. Content completion includes viewing/submission criteria and differs from grade. Do not import its five-second HTML completion criterion into Itembank reading declarations. |
| D5 | [Kolibri learner guide](https://kolibri.readthedocs.io/en/latest/learn.html), undated | Home and Library, breadcrumb return, resource types, bookmarks, transcript seeking, quiz pause/resume, explicit submission, and later report. Documentation is broader than the small test specimen below. |
| D6 | [PrairieLearn assessment configuration](https://docs.prairielearn.com/assessment/configuration/), undated | Homework/exam behavior distinction, stable exam instances across definition updates, closure policy, lockpoints, and learner issue reporting. These are configurable product policies, not universal Itembank defaults. |
| D7 | [Classroom homepage](https://support.google.com/edu/classroom/answer/17231999?hl=en), undated | Enrolled view has due-soon work and class cards. Module collapse persists and empty modules hide. No AI feature in this page was evaluated in this lane. |
| D8 | [Khan Learner Home](https://support.khanacademy.org/hc/en-us/articles/360030629852-What-is-my-Learner-Home-page-and-what-can-I-do-there), updated 2024-08-13 | Most active work and due-date ordering, with active and past assignment/goal views. This is an older help article freshly retrieved, not live verification. |
| D9 | [Duolingo path rationale](https://blog.duolingo.com/new-duolingo-home-screen-design/), 2022 redesign | Guided sequence incorporates practice and stories. Use as dated design rationale, not current app or efficacy proof. No inference that Itembank should adopt access-limiting hearts. |
| D10 | [Open edX plugin slots](https://docs.openedx.org/en/latest/site_ops/references/frontend-plugin-slots.html), undated | Explicit extension seams include learner dashboard and course exit. Useful architecture lead, not a requirement to import its frontend plugin stack. |

### Pinned source and test specimens

Only the named files/windows were sampled. Tests were not run. SHA retrieval
used public GitHub trees, followed by raw files at those SHAs.

| ID | Pinned path | Inspection result and limit |
|---|---|---|
| S1 | [Canvas dashcards_spec.rb](https://github.com/instructure/canvas-lms/blob/1c9f0bb8013ed69c4f2efe11fd483025469b7e6c/spec/selenium/dashboard/dashcards_spec.rb) | Sampled tests switch dashboard views and navigate card activity destinations. Does not prove full current dashboard accessibility. |
| S2 | [Open edX ResumeButton.test.jsx](https://github.com/openedx/frontend-app-learner-dashboard/blob/3376b89a5b1cbf66deb2dd133c9e8385fd324ae4/src/containers/CourseCard/components/CourseCardActions/ResumeButton.test.jsx) | Resume uses course data and tests disabled state with aria-disabled. Its URL fixture is a courseware location, not evidence of passage offset persistence. |
| S3 | [CourseExit.jsx](https://github.com/openedx/frontend-app-learning/blob/09a89b7b8bb1eeb4085c9988c501736c7ba6dfc0/src/courseware/course/course-exit/CourseExit.jsx) and [CourseExit.test.jsx](https://github.com/openedx/frontend-app-learning/blob/09a89b7b8bb1eeb4085c9988c501736c7ba6dfc0/src/courseware/course/course-exit/CourseExit.test.jsx) | Implementation branches into celebration, in-progress, non-passing, or redirect. Sampled tests cover future content and an access-error detail. Does not verify all imported mode logic. |
| S4 | [InstUI Dialog.test.tsx](https://github.com/instructure/instructure-ui/blob/346d0877d42a17b24df437db74013fbb9ab5fbdb/packages/ui-dialog/src/Dialog/__tests__/Dialog.test.tsx) | Sampled labeling, role, Escape dismissal, and managed-focus tests. This file carries an MIT header. Canvas LMS's license must not be generalized to every Instructure project. No vendoring proposed. |
| S5 | [Moodle course_overview.feature](https://github.com/moodle/moodle/blob/e68a1418bea512dd5992c29eb9e36570a3844e94/public/course/tests/behat/course_overview.feature) | Tests cover available activity types, section labels, manual completion, and completion criteria. This is an activities overview, distinct from the My courses shelf in D2. |
| S6 | [Moodle app overview.feature](https://github.com/moodlehq/moodleapp/blob/54c5f8ad4dda6c901d9db4abe1861b00cfd434f6/src/core/features/course/tests/behat/overview.feature) | Phone/tablet cases, visible versus hidden activities, completion controls, and handled deep links. Offline sync implementation was not inspected. |
| S7 | [Kolibri attempt-log-item.spec.js](https://github.com/learningequality/kolibri/blob/9f1ce4f5715d8bbe2e693eef05ee6ee2328d6d0f/packages/kolibri-common/components/quizzes/QuizReport/__tests__/attempt-log-item.spec.js) | Survey suppresses assessment status icons. Non-survey test checks presence on one sample. Test itself notes incomplete status coverage, so no strong report-coverage claim. |
| S8 | [PrairieLearn exam.test.ts](https://github.com/PrairieLearn/PrairieLearn/blob/01f7c640c3f52d69832e5a39a11c4ea14b5e27ec/apps/prairielearn/src/tests/exam.test.ts) | Sampled save, grade, attachment, closed-question, and close-exam cases. This is a large suite sampled by symbols, not read completely or executed. |

## Candidate coverage register

The register routes every named candidate in this lane and the secondary names
from the historical LMS absorption sources. It is not a claim that all were
inspected today. Direct AI competitors and diagram-authoring systems belong to
the sibling reports.

| Candidate | Coverage | Route and retained trigger |
|---|---|---|
| Canvas LMS / Instructure UI | D1, S1, S4 | C1, C5 and shared interaction contracts. Distinct licenses and architectures. |
| Moodle / Moodle app | D2, D3, S5, S6 | C3, C4, C5. Version-specific offline test before adopting detailed eligibility policy. |
| Open edX dashboard / learning | D4, D10, S2, S3 | C1, C2, C5, C7. Extension-slot idea retained without stack adoption. |
| Kolibri | D5, S7 | C1, C3, C8. Coach/review bundle remains C9. |
| PrairieLearn | D6, S8 | C2, C6, C7. Generator and stimulus family remain registered seeds pending current parser/scorer mapping. |
| Khan Academy | D8 | C5. Evidence display calibration belongs to current evidence contract, not imported mastery labels. |
| Google Classroom | D7 | C5. Roster, teacher dashboards, and messaging remain C9. |
| Duolingo | D9, dated rationale | C5 guided path prototype. Gamification remains separate from evidence and efficacy. |
| Runestone / Parsons problems | H1 and Phase 16 only | Route interactive exercise and code-flow depth to INTERACTIVE-TEACHING.md. Existing build-item mapping needs root verification. |
| H5P | H1/H3 only | Historical interaction-capability seed. Consult sibling interactive-teaching research only for the scope it explicitly covers. No fresh product claim here. |
| Pressbooks / mdBook / Jupyter | Historical authoring/portability seeds, not inspected today | Retain book publishing, static reading, and notebook linking/conversion as separate candidates. Revisit when an accepted lesson cannot meet a named portable-reading or computational-artifact task. No claim that the sibling report covers these tools. |
| Anki / FSRS | H1 only | Retain existing review boundary. Revisit only for a named scheduler or card-export defect. No parallel review engine proposed. |
| OpenStax / LibreTexts | H1 only | Retain source binding and per-title rights check. They are content sources, not LMS-flow benchmarks. |
| nbgrader / code autograders | H1 only | Deferred until a named permitted programming workflow and sandbox authority exist. Root must recheck current course policy instead of repeating the old CSCI premise. |
| QTI / Common Cartridge / SCORM / OLX | H1/H3 only | C9 consumer-gated interchange, supported-subset profile, roundtrip and loss report. Not internal scoring authorities. |
| CASE / CTDL / EPUB | Phase 16 hierarchy and landscape only | Existing framework/portability research route. Revisit for an actual mapping or offline reading-export consumer. |
| Hypothesis / Code.org | Historical landscape references only | Notes/annotation and cohort review leads. Defer new inspection until a concrete anchor or review-bundle task requires them. |
| Blackboard Ultra | Secondary historical lead, not refreshed | C4/C9 course activity and review-workflow comparison. Inspect only when a concrete assignment-to-feedback task remains unresolved after the primary LMS comparison. No current feature claim. |
| Schoology | Secondary historical lead, not refreshed | C9 teacher/learner handoff and course-material organization lead. Revisit for a named classroom review or assignment-return consumer. No current feature claim. |
| Brightspace | Secondary historical lead, not refreshed | C4/C7 completion-condition and release-state lead. Revisit if the proposed availability model cannot explain a real conditional course path. No current feature claim. |
| Coursera | Secondary historical lead, not refreshed | C1/C2 resume and course-end comparison. Revisit if a long self-paced course exposes an unresolved stopping, deadline, or completion transition. No current feature claim. |
| FutureLearn | Secondary historical lead, not refreshed | C5/C9 sequential course and discussion-context lead. Revisit if a named learning task requires a social discussion return path. No current feature claim. |
| Moodle Workplace | Secondary historical lead, not refreshed | C9 program-level requirements and multiple-course administration lead. Revisit only for a named cross-course requirement or organizational consumer. Do not infer Workplace behavior from Moodle LMS evidence. |
| Open Learning Library | Secondary historical lead, not refreshed | C4/C8 open self-study course and resource-navigation lead. Revisit when testing a real open-course source-to-reading-to-practice journey. Do not infer deployment behavior from Open edX source. |

H1 is the September 5 report. H2 is the September 7 scope. H3 is the sampled
Phase 16 landscape, hierarchy, and flow research linked above. Historical
recommendations are retained as seeds, not restated as verified current facts.

## Handoff

Only this report was written. No production changes, commits, installs, or
external messages were made. Root should map C1-C9 and T1-T16 onto current
implementation evidence, then choose the first runnable C1/C2 slice. Remaining
evidence gaps are live competitor task walks, Itembank runtime parity, human
accessibility, exact recovery under faults, and learning benefit. Documentation
retrieval and upstream source inspection establish research evidence only.
