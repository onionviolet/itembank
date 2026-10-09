# UI and architecture considerations (2026-10-08)

Status: findings and proposals only. Nothing here is accepted or implemented.
Method: read the ui-generic-audit (2026-10-07) and product-gm UI lane brief,
counted module sizes and top-level symbols, grepped cross-layer imports and
embedded asset strings. Modules were sampled by symbol, not read in full.

## Findings

F1. Uncommitted work is the largest live risk. `git status` shows 153 dirty
paths, 76 tracked files with about 5,082 insertions, spanning several GSD lanes
(UI GM stages 1 to 4, prior-implementation F1 to F5, feature work). AGENTS.md
says a plan's work should not sit uncommitted where concurrent processes can
remove it. The UI audit already documents per-stage recovery, which makes
per-lane commits feasible.

F2. Open verification debt on the UI overhaul. Per the 2026-10-07 audit:
`tests/js/quiz_observers.test.mjs:130` ("bundled auto-render must handle
delimiters") fails; daemon-backed tests time out at about 6s under load;
no browser evidence exists for stages 2 to 4 (Soft, Cash, Neo, lesson, 390px
question); human visual acceptance (COORDINATION W4) is still owed.

F3. `surfaces/daemon.py` is an 8,616-line god module: 218 top-level defs, 108
`handle_*` handlers, a `ROUTES` table, its own `COURSE_FRAME_CSS`, quiz form
tokens, flash receipts, day force tokens and a module lock. Rule 1 holds (it
calls the runtime), but every UI lane collides on it, which is why the product
GM brief had to reserve it for Integration alone.

F4. Front-end code lives in Python strings. `quiz_page.py` holds `SERVED_JS`
(about 2,990 lines) and `OFFLINE_JS` (about 957). Lesson, day, home, palette,
lti and lesson_interaction each carry their own CSS/JS blobs. JS tests import
adapters by slicing these strings out of `quiz_page.py`. Consequences: no
editor tooling or syntax checking, and CSS authority is split across about
twelve modules despite `presentation.py` and `theme.py` being the intended
owners.

F5. Layering inversions. `model.py` imports `_is_separator_row`,
`_split_cells` and `_CALLOUT_MARK_RE` from `surfaces.lesson` (lines 1082, 1956,
4421). `runtime.py` imports `surfaces.settings` (3613, 3742). The parser and
scorer depend on a client layer, against the four-layer diagram, and the
imported names are underscore-private, which the conventions forbid.

F6. Composition work is the right direction but is unproven in a browser. The
seven-look composition tokens (P4) make looks differ in shape, not just tint,
which answers the owner's W4 complaint. The risk now is breadth: seven looks
times light/dark times four screens is 56 states no human has compared.

## Proposals (ranked)

A1 (S). Commit by lane. Stage each lane's named paths into its own commit
after its targeted tests pass. Needs Weibao's git authorization.

A2 (S). Close F2 before more UI. Fix or explain the quiz_observers failure,
rerun daemon tests on an idle machine, take the missing screenshots. Then ask
Weibao to pick the looks that earn their keep; retiring three or four would cut
the review matrix and maintenance in half.

A3 (M). Split the daemon by route family, mechanically. Move handlers into
`surfaces/routes/{quiz,course,day,reading,api,media,settings}.py`, keep
`ROUTES` as the single table in daemon.py, move per-handler token stores into
a small state object. No behavior change; the diff is moves only, verified by
the existing route tests. This lets UI and feature lanes work in parallel.

A4 (M). Move JS and CSS into real files under `surfaces/assets/`, loaded by a
tiny reader that returns the same strings. Offline export still inlines them,
so the single-file offline quiz is unchanged. JS tests import the module files
directly instead of string-slicing. Do the 3k-line `SERVED_JS` first.

A5 (S). Fix the inversions. Move the table and callout helpers into `model.py`
(or a `markdown_blocks.py` below both) as public names; pass settings into the
runtime as arguments instead of importing a surface.

## Further considerations (not ranked)

- Add a layering check to `preflight --quick`: fail if `model.py`, `runtime.py`
  or `evidence.py` import `surfaces`. Cheap and prevents F5 recurring.
- Add a size budget warning (for example 3,000 lines per module) so new god
  modules surface early, not after the fact.
- Packaged desktop app is a stated end goal; A3 and A4 are prerequisites for a
  clean webview shell, since assets as files are what a packager expects.
- Copy voice (audit P5) remains half done: runtime-owned hint-ladder strings
  ("Tier N is unlocked") still leak runtime vocabulary. Changing them is a
  runtime disclosure-copy change and needs its own decision.

## A5 execution evidence, 2026-10-08

Shared table, callout, and fence syntax now lives in `markdown_blocks.py` as
public names. The lesson surface renders the shared parser's raw fence tokens.
Settings loading, validation classification, model-profile resolution, and
mode precedence now live in `settings_core.py`; surfaces re-export the existing
public settings and precedence entry points. Defaults, file formats, and
settings paths are unchanged. The nine moved settings and precedence function
ASTs match their prior implementations exactly.

The import scan also found `subjects.py` importing surface settings and
`strategies.py` importing surface mode precedence. Both now call the core.
`server.py:41` still imports `surfaces.visual_fixture`, as explicitly excluded
by the task. The generated launcher imports in `build.py` are unchanged; its
package allowlist now includes both shared modules.

The new `layers` gate runs in quick preflight and scans static imports,
including function-local imports, in every root Python module except
`build.py`, `itembank.py`, and `server.py`. It uses the AST rather than matching
comments or launcher strings. Regression cases cover nested and multiline
imports, submodule imports, exclusions, harmless text, and syntax errors.

Verification at this source revision:

| Check | Result |
| --- | --- |
| `python3 scripts/preflight.py --quick` | Exit 0; 37 core modules checked; all fast gates passed |
| `python3 tests/preflight_roundtrip.py` | Exit 0; 15 CI steps, 14 gates, 2 CI-only steps |
| `python3 tests/settings_roundtrip.py` | Exit 0 |
| `python3 tests/lesson_roundtrip.py` | Exit 1; daemon loopback bind denied by sandbox |
| `python3 tests/model_adapter_roundtrip.py` | Exit 1; fake HTTP server bind denied by sandbox |
| `python3 tests/hint_roundtrip.py` | Exit 1; daemon loopback bind denied by sandbox |
| `node --test tests/js/*.test.mjs` | Final exit 0; 147 passed, 0 failed |
| `python3 tests/config_roundtrip.py` | Exit 0 after restoring the surface's schema-print resource import |
| `python3 tests/strategy_precedence_roundtrip.py` | Exit 0; 5 passed |
| `python3 tests/lesson_interaction_roundtrip.py` | Exit 1; 17 ran, 1 socket-bind error |
| `python3 tests/local_harness_roundtrip.py` | Exit 1; loopback bind denied by sandbox |
| Focused lesson slice | 20 fence, table, callout, and term checks passed |
| Focused model-adapter slice | 4 settings and transport-registration checks passed |
| Fresh zipapp smoke check | Both shared modules present; config schema and sample lint passed |
| `git diff --check` | Passed |

The first JS run passed 146 of 147 tests; the quiz-observer timing assertion
failed. That test passed in isolation, and the repeated full command passed
147 of 147. This is an observed intermittent result, not a diagnosed cause.
The sandbox rejects `socket.bind` with `PermissionError: [Errno 1] Operation
not permitted`; rerun the socket-dependent suites in an environment permitting
loopback binds. Focused slices do not replace those full-suite gates.

Large touched modules were read by symbol and bounded windows, including
`model.py`, `runtime.py`, `model_adapter.py`, `subjects.py`, `strategies.py`,
and the lesson, settings, and IA surfaces. No staging, commit, or push was
performed. The source refactor and local checks do not establish installed
desktop-app or human acceptance. Undo is the task-scoped diff plus removal of
the two new shared modules, preserving unrelated concurrent edits.


## A3 wave 1 execution evidence, 2026-10-08

Source extraction only, awaiting reviewer acceptance. `surfaces/routes/quiz.py`
now owns the two quiz handlers, ten quiz-only helpers, both quiz route patterns,
authority fields, token TTL/cap, and session lock. `surfaces/routes/api.py` owns
all 58 `handle_api_*` functions and the two API-only helpers
`_scoped_session_for` and `_teach_reject_authority`. The daemon explicitly
re-exports every moved name. Handler token/flash stores remain on the handler.

Shared helpers remain in the daemon and are imported inside moved functions,
so importing either route module first does not create a module-load cycle.
`_ensure_quiz_session` remains because the assessment-area test patches its
`api_session_path` and `_saved_quiz_session` globals on the daemon.
`_saved_quiz_session` also serves lesson navigation. `_quiz_path` and
`_refresh_attempt_view` are shared with retained handlers. `_course_operation`
remains because the existing course-operations test inspects its definition in
`daemon.py`. No tests were changed. `build.stage` recursively copies `surfaces`,
so no packaging allowlist edit was needed.

Final line counts: daemon 6,512; routes quiz 636; routes api 1,839;
routes initializer 1. Both large implementation files were inspected by symbol
and windows, never displayed whole. Every original top-level function matches
its prior source verbatim after removing added imports. The route-table ASTs
are unchanged and every route handler resolves through the daemon namespace.

Checks passed with exit 0: `python3 -c "import surfaces.daemon"`,
`python3 scripts/preflight.py --quick`,
`python3 tests/package_fixture_inventory_roundtrip.py`,
`python3 tests/course_assessment_area_roundtrip.py`,
`python3 tests/mcp_roundtrip.py`, and
`python3 tests/daemon_discovery_roundtrip.py`. Fresh imports from a temporary
`build.stage` tree passed, including both route modules imported before daemon.
The existing course-operation source-location assertion and diff whitespace
check also passed. Quick preflight skips Python/JS suites and clean-worktree
checks.

`tests/daemon_roundtrip.py` exited 1 because loopback binding raised
`PermissionError: [Errno 1] Operation not permitted`. Reviewer HTTP coverage is
still required. `tests/serve_roundtrip.py`, `tests/course_ops_roundtrip.py`,
`tests/course_resume_roundtrip.py`, `tests/model_phase_roundtrip.py`, and
`tests/source_adapters_roundtrip.py` were not run because their full suites need
loopback servers. No staging, commit, or push was performed. Later route
families and a state-object migration remain outside this wave.

## A3 wave 2 execution evidence, 2026-10-08

Source extraction only, awaiting reviewer acceptance. Five route modules now
own 37 handlers and 20 family-only helpers: course 16/7 (course forms,
research/context help, artifacts, reading, restore, storage); day 8/9 (day,
study, report); lesson 4/2 (check, skip, gloss, media); pages 6/2 (index, help,
palette, banks, disclosure, key); assets 3/0 (KaTeX, fonts, marker response).
Core/surface imports remain top-level, daemon dependencies are imported inside
each function, and every moved name has an explicit daemon re-export. Wave 1
route modules and all tests are unchanged.

The pre-move test search found definition/source dependencies. Retained:
`_course_page_state`, `_course_operation`, `handle_course_get`,
`handle_course_area_get`, `handle_course_lesson_get` (course-operations source
splits); `handle_courses_get`, `handle_activity_get`, `handle_settings_get`
(responsive-product literal definition/copy checks); `handle_seed_accept`
(seeding endpoint source check); `handle_theme_post`, `handle_lesson_get`
(function-source inspection, retained under this task's exception).
The accepted wave 1 `handle_quiz_get` re-export still supports its source check.

Monkeypatch targets remain daemon-owned: `_reject_cross_origin_write`,
`api_session_path`, `_saved_quiz_session`, `_course_area_extra`, `parse_bank`,
`Daemon`, `probe`, and `SURFACE_PARITY`. Patched module attributes on `ia`,
`session`, `evidence`, and `settings` still refer to the same imported modules.
Shared helpers, helpers reached by retained definitions, constants, discovery,
route tables, server/startup, sidecar token/marker authentication, CLI and MCP
remain in daemon. No state-object or packaging-allowlist change was needed.

Final line counts: daemon 4,690; routes course 768, day 675, lesson 324,
pages 321, assets 63; unchanged routes quiz 636, api 1,839, initializer 1.
Daemon and existing large modules were sampled by symbols/windows, never
displayed whole. Programmatic comparison proves all 146 original functions
and classes remain verbatim after removing added imports, all five route/parity
table ASTs are unchanged, and all 110 route handlers and late imports resolve.
Fresh imports with each new route module loaded before daemon passed.

Checks passed with exit 0: the exact requested daemon-plus-five-route import,
`python3 scripts/preflight.py --quick`, and
`python3 tests/package_fixture_inventory_roundtrip.py`. Additional passing
suites: course assessment areas, mock exam, missed review, course guidance UI,
daemon discovery, MCP, responsive product, and navigation color. The existing
course-operation source-location assertions and `git diff --check` passed.
Quick preflight skips Python/JS suites and clean-worktree checks. Missed review
initially exposed a missing late import of wave 1's `QUIZ_SESSION_LOCK`; it
passed after correction, with no test changes.

`tests/daemon_roundtrip.py` exited 1: daemon never printed a URL. A direct
`Daemon` bind to loopback port zero confirmed
`PermissionError: [Errno 1] Operation not permitted`. HTTP suites not run here:
`tests/serve_roundtrip.py`, `tests/course_ops_roundtrip.py`,
`tests/course_resume_roundtrip.py`, `tests/restore_workspace_roundtrip.py`,
`tests/restore_workspace_browser_roundtrip.py`, `tests/storage_roundtrip.py`,
`tests/lesson_roundtrip.py`, `tests/lesson_code_roundtrip.py`,
`tests/ia_route_roundtrip.py`, `tests/stylesheet_roundtrip.py`,
`tests/mode_layer_roundtrip.py`, `tests/model_phase_roundtrip.py`, and
`tests/source_adapters_roundtrip.py`. Reviewer HTTP coverage and acceptance
remain open. No staging, commit, push, app build, install, or deployment.
