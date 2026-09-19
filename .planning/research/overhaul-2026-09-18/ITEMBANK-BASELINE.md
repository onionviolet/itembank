# Itembank baseline for the overhaul

Inspected 2026-09-18. Evidence: sampled working-tree source, existing research,
and prototype documentation. This is not a fresh installed-app or learner trial.
Concurrent changes are present. Recheck these symbols before implementation.
Root owns this file. Production files were read only.

## Existing capability and precise gap

| ID | Existing evidence | Gap or limit | Owning seam |
| --- | --- | --- | --- |
| B1 | `surfaces/ia.py::_course_resume_cue` validates canonical sessions and produces a textual status. `_healthy_card` always links to `/course/<id>`. | A Resume label does not route directly to the saved activity. Preserve session identity when enriching the projection. | IA read model, daemon saved-session routing, `tests/course_resume_roundtrip.py` |
| B2 | `surfaces/daemon.py::_course_area_rows` lists lessons and accepted reading occurrences. Overview selects `lessons[0]` and `quizzes[0]`. Map rows have no href. | Course graph relationships are not yet a complete navigable unit sequence. First listed artifact is not necessarily the intended next activity. | Existing course/graph objects and IA, course-area rendering |
| B3 | `_send_quiz_page` uses `home_href="/"` and retains explicit feedback through a flash receipt before Next. | Course-aware exit and return need a stronger public context projection. Existing explicit feedback pause must survive the overhaul. | `surfaces/daemon.py`, `surfaces/quiz.py`, `surfaces/quiz_page.py` |
| B4 | `surface_shell` combines shared, product and surface CSS. `theme_css` appends look shape rules to color tokens. Reader, quiz and settings also assemble documents separately. | A new layout added as extra CSS inherits old global rules. A shell-only change cannot renew every document. | `surfaces/presentation.py`, `surfaces/theme.py`, reader/quiz/settings assembly |
| B5 | `surfaces/lesson_progressive.py` provides Next explanation, Show all, restart, highlights, outline and optional details over permitted content. | Guided learning is an implemented foundation. Cross-restart exact explanation position was not established by this inspection. | Existing guided renderer and future narrowly scoped presentation-position owner |
| B6 | `surfaces/lesson_interaction.py::render` and its script implement a finite A/B comparison, range control, meters, reset and static prose. `model.parse_lesson_comparison` is the parser owner. | One comparison does not establish a general diagram, linked-representation or simulation authoring system. | Model grammar, trusted renderer, existing lesson capability registry |
| B7 | `reading_desk.py::snapshot` binds a source occurrence and revision, validates source bytes and projects note anchors. `save_note` uses existing notes and journal owners. | Source reading and private notes exist. Rich text selection mapping and exact passage resume need their own evidence. The binding contract explicitly defers exact reading cursor resume. | `reading.py`, `reading_desk.py`, `notes.py`, source bindings, journal |
| B8 | `runner.py::run_source` supplies bounded output for lesson runs. `run_cases` supplies execution observations to scoring consumers. | Do not claim code execution is missing. Resource bounds alone do not prove a hostile-code security sandbox. The D1/D2 prototype is non-executable and cannot replace the execution owner. | Existing runner, runtime scorer, CS Dojo work and code-depth audit |
| B9 | `source_adapters.py` defines local Markdown, text, PDF, DOCX, PPTX, web, transcript, OCR, EPUB and ASR paths with sidecars and preview/import functions. | Function existence does not establish availability or extraction fidelity for every source. Compare difficult fixtures before replacing an adapter. | Source adapter, rights, binding, journal and package owners |
| B10 | `director.py::resume_point` reads durable operation checkpoints. `accept_revision` owns accepted changes. | Resumable AI operations already have a backend foundation. A coherent author workbench, steering, candidate previews and recovery need a visible task audit. | Director operations and existing Build/review surface |
| B11 | `retention.py::FSRSStrategy`, objective summaries and recommendations exist. | Do not plan a second FSRS implementation. Verify learner-facing due review and traceable evidence instead. | Existing retention and Study owners |
| B12 | Current renewal showcase documents linked math illustration, varied question workspaces and visible references. Bilingual and code-depth work remain prototypes. | Synthetic in-tab drafts, navigation and sample feedback are not production persistence or assessment parity. | Existing prototype directories as design fixtures, not durable state owners |

## Evidence scope

Read the binding product contract's north star, learner experience, durable
reading and capability research sections. Sampled September 7 and September 18
vision entries, current STATE, the renewal synthesis and its flow/integration
reports, older source absorption and the code-depth audit. Sampled function
windows in IA, daemon, presentation, theme, reading desk, director and runner.
Read the small finite comparison module and guided enhancement implementation.
Located source-adapter and retention symbols without reading those large modules
in full. This baseline does not claim exhaustive code or test coverage.

Current source independently confirms B1-B8 and B10. B9 and B11 are symbol and
contract evidence only. B12 is prototype documentation evidence. Existing
source audits identify additional completion-summary risks that should be
reproduced before classifying them as current rendered defects.

## Baseline implications

The most defensible first integration combines a real course journey with one
existing explainer and runtime-owned assessment. A fresh visual shell alone
cannot establish feature parity. A broad diagram engine alone cannot make
existing activities discoverable or restore their context. Both should be
evaluated on one actual connected synthetic unit before expanding families.

No tests were run to validate implementation in this source inventory. Research
document validation is recorded in the integration plan. Existing reports of
passed tests remain historical evidence at their recorded revisions.
