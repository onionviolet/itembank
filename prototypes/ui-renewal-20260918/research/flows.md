# Learner flow audit, 2026-09-18

This is a bounded source audit and proposed journey for the UI comparison. It is not evidence of a rendered defect, user preference, completed implementation, or accessibility acceptance. No runtime, source artifact, assessment state, or existing dirty file was changed.

## Authority and scope

Read the relevant sections of `AGENTS.md`, `.planning/USER-VISION.md`, `.planning/SOURCE-TO-COURSE.md`, and `.planning/AGENT-WORKFLOW.md`. Sampled vision entries cover August 13 logical flow, September 7 home and completion transitions, and September 18 question continuity. The product contract requires a course shelf, reachable accepted artifacts, continuous and guided lesson views, runtime-owned disclosure, and coherent desktop and mobile flows.

The current workspace contains substantial dirty work across planning, rendering, runtime, model, and tests. Every finding describes the current working tree, including those edits. Large files were read symbol-first. This audit did not read all of `runtime.py`, `model.py`, `surfaces/daemon.py`, `surfaces/lesson.py`, or the test suites. It did not inspect live learner materials or run a real sitting.

No simulated teacher, classmate, speaker roster, or classroom discussion is proposed.

## Five concrete opportunities

| Code | Verified source behavior | Learner implication, inferred | Proposed change | Integration targets |
| --- | --- | --- | --- | --- |
| F1 | `_course_shelf_body` selects `shelf["cards"][0]` for the Continue Learning hero. `_healthy_card` gives an in-progress course a Resume label but its `cta_href` is always `/course/<id>`. `_course_resume_cue` produces a status string, without a session destination. | The highest emphasis can follow shelf order rather than the intended interrupted task. Resume takes another navigation step and does not name the actual activity or position. | Keep the shelf as the home object. Above it, show one verified interrupted activity with course, title, position, mode, and a specific Resume action. If the current state cannot prove an exact target, label it Open course. Never imply an exact saved place from a generic session cue. | `surfaces/ia.py::_course_resume_cue`, `_healthy_card`, `course_shelf_state`; `surfaces/daemon.py::_course_shelf_body`, `_desk_hero`, `_saved_quiz_session`; `surfaces/home.py::render_resume_projection` as a comparison seam rather than a second authority. |
| F2 | `_course_area_rows` makes Overview from the first lesson and first quiz. Learn lists lessons and accepted reading occurrences. Map renders objective statements as rows without links. The overview says Start reading and Sit the items. | Learners must reconstruct the relationship between their objective, source, lesson, and practice. A visually polished dashboard still lacks an obvious unit journey. | Make the course overview identify a current unit and its source-backed objective. Present linked available treatments in sequence: Read or learn, check understanding, practice, then review. Clearly distinguish the learner's current activity from optional or ahead-of-class material. Use authored graph order and accepted relationships. Do not infer prerequisites or mastery. | `surfaces/daemon.py::_course_area_rows`, `_course_bank_treatments`, `_course_frame`; `surfaces/ia.py::course_area_state`, `deep_link_target`; existing course graph and reading occurrence projections. |
| F3 | Lessons receive `_lesson_context_nav` with a course return link only when ownership is unique. `_send_quiz_page` passes `home_href="/"`, and the quiz completion JS offers View report. Reports use an app-root return link. | The learner changes navigation models during one activity and loses the visible course or unit destination after practice. Returning home is possible, but returning to the exact learning context is less direct. | Carry one verified course context projection through lesson, question, feedback, report, and exit. Show course and activity in the compact header. Keep Back to course available without competing with Submit or Next. A final completion action returns to the owning unit or course. Ambiguous ownership falls back to Courses visibly. | `surfaces/daemon.py::_lesson_context_nav`, `_send_quiz_page`, `handle_report_get`; `surfaces/quiz.py::page_for`; `surfaces/quiz_page.py` page context and `finish`; `surfaces/lesson.py::lesson_page` and its `context_nav`. |
| F4 | `quiz_page.baseline_for` has a persistent feedback pause, explicit Next link, and runtime-issued verdict text. The JS feedback branch also renders disclosed explanation sections and focuses the Next button. The two paths have different feedback richness. Existing Next controls name question position, and new prompts receive focus. | Script-free and enhanced learners can get different explanatory experiences. Many help and explanation labels can also interrupt the main answer, feedback, next rhythm. This is an opportunity to verify parity, not a claim that hidden content should be exposed. | Arrange each question as prompt, response, runtime-authorized feedback, then one next action. Keep the answered item and response visible throughout feedback. Show the useful granted explanation in the same region across renderers when the public payload permits it. Put supplementary details under labeled disclosure. Keep feedback until explicit Next and preserve refusal drafts, retry, pending review, exam deferral, and reduced-motion focus behavior. | `surfaces/quiz_page.py::baseline_for`, `_question_assist_html`, `_question_symbols_html`, `renderTeaching`, JS post-submit branch around line 3700; `surfaces/daemon.py::_send_quiz_page`, `_mint_quiz_flash`, `_consume_quiz_flash`, `handle_quiz_answer`. |
| F5 | `finish` displays runtime totals but chooses the local `miss` list for harvest copy, including Clean sweep when that list is empty. `baseline_for` returns only Session complete when no item exists. `_report_card` shows a percentage even with zero auto-marked attempts and reports objective counts. The report is more durable than the local miss list. | Completion can feel like a dead end, and the local list is not sufficient evidence of an entirely correct historical sitting after resume. An all-pending sitting showing 0% can resemble failure. These are source-level risks requiring rendered reproduction. | Use one runtime-summary-based completion model for enhanced, script-free, and resumed views. Lead with completed activity and saved state. Show scored numerator/denominator and pending responses separately. Show no scored answers yet when the denominator is zero. Offer Review this sitting and Back to the unit. A source/lesson review link can be offered only when the objective mapping exists and disclosure allows it. | `surfaces/quiz_page.py::finish`, `baseline_for`; `surfaces/daemon.py::_report_card`, `_report_objective_rows`, `handle_report_get`; canonical `session_summary()` output rather than client-only `miss`. |

## One coherent journey

The proposed composition is a course workspace with a focused activity mode. Desktop and phone share the same state and routes, but use different amounts of surrounding navigation.

### Enter or return

Home opens with the learner's course shelf. A compact Continue section appears only when a verified activity exists. Its button says Resume practice, question 4 of 10 or Resume lesson, followed by a saved section name when available. The course title remains visible. Completed sessions open their report rather than silently starting a new attempt.

Desktop places this action beside the course shelf rather than above a large decorative hero. Phone puts it first and uses compact course rows. Reordering the shelf never changes which runtime session a Resume action names.

An empty workspace offers the sample course or course creation using the existing supported operations. A stale or unavailable course stays visible with the actual recovery action. No fake progress, estimated mastery, or invented future lesson appears.

### Understand the course

The course overview shows the current unit, its objective, and the available next activity. The overview contains enough context to choose intentionally, with full Learn, Practice, Test, Sources, Map, and Build/review areas remaining reachable. Existing additional areas need not be removed merely to fit the visual shell.

Desktop uses a stable course navigation rail with the active unit or activity highlighted. Secondary source and evidence tools live beside the work when useful. Phone uses a compact course header and an explicit course menu. Activity content remains the first substantial content below the header.

### Read and check understanding

The lesson displays its title, objective, source attribution, and useful content immediately. Continuous reading stays available. Guided or paced reading presents the same parsed teaching content with clear position and previous/next destinations. Source references and exact authored symbol definitions open without losing the current place.

Desktop can place the outline on the left and an optional source or notes panel on the right. Phone shows one content column with source, terms, and notes in accessible disclosures or a focused secondary view with a clear return action. Notes never become scores. Opening or scrolling a reading never implies completion.

The transition to practice names the activity and mode. If the learner opens a lesson from a question, Return to question restores the same sitting instead of starting another one. Actual restoration depends on the existing session and reader contracts.

### Answer, receive feedback, continue

The activity header keeps course, activity, question position, and mode visible. The prompt dominates the main panel. Answer controls use the native response form that the item requires. Help is one secondary action that exposes only the next runtime-authorized assistance.

After submission, the same question remains. Feedback appears directly after the response. Correctness and explanations come only from the public runtime projection. Pending manual review and exam-held feedback use their own copy. The only primary advance action is Next question, N of M, or View summary on the last item.

Desktop avoids scattering feedback across multiple cards. Phone keeps prompt, response, feedback, and advance in reading order. A sticky action footer is optional prototype treatment only and must reserve content space, remain above browser safe areas, and never obscure feedback. No timed or automatic advance is allowed.

### Finish or leave

Completion shows what was saved, the runtime's scored counts, and any pending review. It leads to the course context, not just a generic app home. A review option shows the session's permitted evidence and relevant source links. It does not label an objective mastered from one sitting or automatically schedule remediation.

Leaving mid-activity names whether the accepted response is saved and whether an unsubmitted draft is local to this browser. Resuming uses the canonical session cursor and preserves assessment mode. Feedback receipts are presentation state and must not be used as scoring truth. Browser back or a refresh must not submit an answer twice.

## Required state coverage before promotion

| State | Observable acceptance task |
| --- | --- |
| First entry and empty course | Open a supported sample or creation flow and reach a real activity without a dead link. |
| Mid-practice return | Leave after a saved answer, return from Home, and reach the same runtime session and correct question. |
| Held feedback | Read feedback for an answered item without it disappearing. Explicit Next moves focus to the new prompt. |
| Wrong answer, pending mark, and exam mode | Each shows the runtime-approved actions and content. No presentation control bypasses the gate. |
| Completion and resume of completed sitting | Counts and pending status agree with the report. An empty client-only miss list cannot claim perfect historical performance. |
| Stale or unavailable artifact | The last accepted state remains visible where supported, with an honest recovery destination. |
| Mobile, keyboard, and script-free | Finish the same task with readable content, stable focus, reachable source return, and no hidden mandatory action. |

## Evidence boundaries and research handoff

These five findings are grounded in sampled current source. Their usability effects and the proposed arrangement are design inferences. Rendered browser verification, phone-width task completion, keyboard flow, screen-reader behavior, zoom, high contrast, and reduced-motion checks remain open.

The parent task owns external comparison research and prototype implementation. This audit does not duplicate competitor claims. The prototype should use synthetic content and label any state that does not yet have a canonical projection. In particular, an exact home Resume button, a current-unit sequence, and session-aware return from a source reference require verified data, not decorative placeholder confidence.

Memory orientation used `MEMORY.md` lines 18-29 from rollout `01a0b2fd-cf4a-7523-9714-1586bdc164f8`, which pointed to feedback persistence and script-free focus risks. These behaviors were checked against the current vision entry and source above. No unverified memory-derived implementation claim is relied on here.
