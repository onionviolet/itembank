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

## A4 wave 1 and A6 execution evidence, 2026-10-09

Source extraction only, awaiting reviewer acceptance. Nine verbatim assets now
live under `surfaces/assets/quiz/`: question-stem.js, latex-input.css,
latex-input.js, question-symbols.js, structure-adapter.js, math-adapter.js,
assist.js, offline.js, and served.js. Import-time `resources.read_text` calls
retain the same constant names, script wrappers, substitutions, and
QUESTION_STEM_JS concatenations. HTML templates remain in Python. Final
`quiz_page.py` line count: 1,049. The large module was sampled by symbols and
windows, never displayed whole.

A throwaway script outside the repository saved pre-edit constants and rendered
outputs to JSON. Every final constant is byte-identical: QUESTION_STEM_JS,
LATEX_INPUT_STYLES, LATEX_INPUT_JS, QUESTION_SYMBOLS_JS, STRUCTURE_ADAPTER_JS,
MATH_ADAPTER_JS, ASSIST_JS, OFFLINE_JS, and SERVED_JS. Offline and served
`quiz.page_for` output (served with assist enabled), plus a synthetic
`baseline_for` output, also match. Eight pre-existing em dash characters in
client copy were preserved to satisfy the hard byte-identity invariant;
new Python and documentation prose introduces none.

Source-reading tests retain all assertions. JS a5_inline_fields now reads
both offline.js and served.js. Python responsive_product reads served.js;
presentation_profiles reads quiz_page.py plus every quiz asset; check reads
that same combined source for generic-refusal checks and includes every asset
in its per-file claim-word checks; presentation's font-family check includes
latex-input.css. No constant line-number dependencies were found.

The new fast `size` preflight gate lists tracked root and recursive surfaces
Python modules over 3,000 lines, sorted descending, as non-failing warnings.
It is registered in `--list` and LOCAL_ONLY. The roundtrip tests cover the
threshold, tracked inventory, scope, ordering, warning visibility, and exit 0.
Current warnings: model.py 4,954; surfaces/daemon.py 4,690; runtime.py 3,994;
surfaces/lesson.py 3,306.

Packaging was verified using `build.stage` into a temporary directory, then a
temporary zipapp. All nine asset files were included verbatim, and a fresh
process imported all nine constants from the archive with byte-identical
values. `build.py` recursively copies surfaces through STAGE_DIRS; no build
allowlist change or installed-app build was needed.

Checks passed: `python3 scripts/preflight.py --quick` (exit 0; Python/JS suites
and clean-tree gate skipped), `node --test tests/js/*.test.mjs` (147 passed,
0 failed, 0 skipped), `python3 tests/preflight_roundtrip.py` (15 CI steps,
15 gates, 2 CI-only), responsive_product (5 passed), presentation_profiles,
latex_input, and a5_inline_fields. The changed check refusal/honest-limits
functions and presentation font-family function passed when invoked without
sockets. Python syntax and diff whitespace checks passed.

Full `tests/check_roundtrip.py` stopped at its HTTP test because loopback bind
raised `PermissionError: [Errno 1] Operation not permitted`; subsequent socket
checks in that suite remain unverified. `tests/serve_roundtrip.py` and
`tests/daemon_roundtrip.py` were not run because they require loopback servers.
Reviewer HTTP coverage remains open. No Git staging, commit, push, installation,
or human acceptance was performed. HTML extraction and later A4 waves remain
outside this work.


## A4 wave 2 execution evidence, 2026-10-09

Source extraction completed under the wave 1 pattern, awaiting review. The
initial checkout was clean. No Git staging, commit, push, installation, or
human acceptance was performed. Undo consists of restoring this task's source,
test, and research-document edits and removing the 29 new assets listed below.
All eleven touched surface modules were sampled by symbols and windows; none
was displayed whole. AST tools located literal spans without a second parser
for bank content.

Import-time `resources.read_text` calls retain every constant name. The three
lesson script percent-format operations remain in Python, as do study and LTI
substitutions at render time. `SHARED_CSS = SHARED_CSS + PRIMITIVE_CSS` remains
unchanged. Both interaction script constants and the progressive script retain
`"<script>" + EXPLORATION_JS + ...`, moving only their trailing literal text.
Existing script tags, whitespace, escapes, and em dash characters inside moved
code were preserved. New prose contains no em dash characters.

### Per-module byte comparison and file inventory

A throwaway script outside the repository imported all eleven modules before
editing and recorded SHA-256 for every uppercase string constant, including
imported and derived constants. The final fresh-process comparison has the
same names and hashes for all 201 constants. This includes the final shared
stylesheet, interaction JS and LINEPLOT_JS, progressive JS, and the imported
lesson aliases. Synthetic `lesson_page`, `day_page`, and `study_page` outputs
also match byte for byte. The comparison script and JSON snapshots remain
outside the repository, so they are execution evidence rather than new tests.

| Module | Lines before | Lines after | Uppercase strings | Comparison | New files under surfaces/assets/ |
| --- | ---: | ---: | ---: | --- | --- |
| `day.py` | 2081 | 1501 | 5 | PASS | `day/`: `day.css`, `day.js` |
| `presentation.py` | 1952 | 1226 | 14 | PASS | `presentation/`: `shared.css`, `primitive.css`, `product.css`, `quiz-product.css` |
| `lesson.py` | 3306 | 2722 | 85 | PASS | `lesson/`: `lesson.css`, `math-adapter.js`, `runnable.css`, `runnable.js`, `gloss-enhancement.js`, `code-craft.js`, `gloss-hover.js` |
| `daemon.py` | 4690 | 4426 | 22 | PASS | `daemon/`: `restore-script.js`, `shelf-script.js` |
| `visual_fixture.py` | 1572 | 1387 | 15 | PASS | `visual_fixture/`: `chrome.css`, `onefile.css` |
| `study.py` | 455 | 282 | 2 | PASS | `study/`: `study.css`, `study.js` |
| `lesson_interaction.py` | 500 | 122 | 5 | PASS | `lesson_interaction/`: `exploration.js`, `interaction.css`, `interaction.js`, `lineplot.css`, `lineplot.js` |
| `lesson_progressive.py` | 189 | 7 | 3 | PASS | `lesson_progressive/`: `progressive.css`, `progressive.js` |
| `theme.py` | 1065 | 997 | 16 | PASS | `theme/`: `settings.css` |
| `lti.py` | 1423 | 1370 | 29 | PASS | `lti/`: `picker.js` |
| `palette.py` | 378 | 343 | 5 | PASS | `palette/`: `palette.css` |

All 29 requested literal bodies moved cleanly. No requested f-string or other
unclean extraction remains. HTML-bearing templates stay in Python:
`BIND_PANEL`, `LESSON_TEMPLATE`, `PALETTE_HTML`, `LOOK_BODY`, and
`SETTINGS_BODY`. Literals below 20 lines remain, including the explicitly
excluded nine-line `COURSE_FRAME_CSS`. No HTML template was extracted.

### Tests, packaging, and remaining gates

Source-reading tests retain every assertion and include the moved assets:
lesson overflow and scroll targets, study color literals, presentation font
ownership and surface font declarations, primitive prose checks, settings
external-loader exclusions, and the check claim-word gate. The exploration
browser receipt now hashes the relevant assets as well as Python sources.
JS source searches found no additional wave 2 Python-literal reader requiring
an update; those tests import runtime constants or render pages instead.

`build.stage` still recursively copies `surfaces` through `STAGE_DIRS`; no
packaging configuration changed. All 29 new files were present verbatim in a
staged build and temporary zipapp. A fresh process imported all eleven modules
from that zipapp. All string hashes match the checkout baseline except the
three existing visual-fixture path constants `ROOT`, `PROTOTYPE_DIR`, and
`FIXTURE_PATH`, which were separately verified to relocate to the archive path
as their existing `__file__` expressions require. Both visual-fixture asset
constants match exactly. The first archive harness incorrectly required those
paths to equal checkout paths; the corrected harness passed. The checkout
comparison retains the strict all-constants invariant without exceptions.

Checks passed:

- `python3 scripts/preflight.py --quick`: exit 0; every executed gate passed;
  Python suites, JS suites, and clean-tree gate skipped by quick mode.
- `node --test tests/js/*.test.mjs`: 147 passed, 0 failed, 0 skipped, exit 0.
- Full `surface_roundtrip`, `component_primitives_roundtrip`, and
  `settings_roundtrip`: exit 0 each.
- `lesson_roundtrip`: 130 socket-free test functions passed via an external AST
  harness that omitted the suite's unguarded top-level calls, preserving its
  definitions and assertions. `presentation_roundtrip`: 18 socket-free check
  functions passed. Its parser self-check deliberately catches a malformed
  two-h1 fixture, so its expected FAIL diagnostic is not a suite failure.
- Changed `check_roundtrip.check_honest_limits_gate`: passed without sockets.
  All eleven surface modules parse successfully; `git diff --check` passed.

Loopback bind was directly probed and raised
`PermissionError: [Errno 1] Operation not permitted`. These socket checks
remain unverified in this environment:

| Suite | Unrun socket checks |
| --- | --- |
| lesson_roundtrip | test_lesson_src_degraded_daemon_and_cli; test_routes_and_cli_twin; test_gloss_route_and_cli_twin; test_key_review_route_and_cli |
| presentation_roundtrip | test_shared_accent_tokens_across_routes; test_reload_after_save_updates_tokens; test_forced_modes_preserve_semantic_tokens; test_index_and_report_state_copy |
| lesson_exploration_roundtrip | check_routes; check_browser, including its expanded source receipt |
| check_roundtrip | HTTP, agent, cross-path, explanation-threading, and network-refusal cases; the complete suite was not run |
| Other relevant server suites | serve_roundtrip, daemon_roundtrip, and lti_roundtrip were not run because they require loopback servers |

Review and socket-enabled verification remain open. This record proves source
byte preservation, the stated test slices, and staged/archive asset loading.
