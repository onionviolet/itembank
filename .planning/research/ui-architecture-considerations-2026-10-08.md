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

## Model split, 2026-10-09

Source extraction completed under the A3 facade and late-import pattern. The
initial checkout was clean. The accepted scope was four sibling core modules,
explicit facade re-exports, packaging allowlist updates, source-test location
updates, and this execution record. No Git staging, commit, push, install, or
human acceptance was performed. Undo is the task-scoped diff and removal of
the four new modules.

| Module | Lines before | Lines after | Responsibility |
| --- | ---: | ---: | --- |
| `model.py` | 4,954 | 3,252 | Public facade, bank parser, lint authority, shared definitions |
| `model_style.py` | 0 | 610 | Style metrics, enforcement, suppression, warning calibration, StylePrompt, local constants |
| `model_provenance.py` | 0 | 207 | Winnowing, paraphrase checks, source text reading, unsourced-specific findings |
| `model_lesson.py` | 0 | 808 | Slugs, lesson directives, lesson/comparison/lineplot/terms/sources/media/activities readers |
| `model_ids.py` | 0 | 197 | Key content hashes, key identity splice, item ID assignment |

All 70 moved names, including underscore helpers and constants, have explicit
`from model_<family> import (...)` re-exports. No wildcard imports or `__all__`
were introduced. The four modules import no `model` at module load. Shared
facade dependencies are resolved by local `import model` and `model.<name>`
lookups. Each sibling-first import order passed in a fresh Python process.
No shared base module was needed.

`load`, `parse_bank`, `parse_question`, `LintError`, `lint`, and the existing
bank/structure lint entry points remain defined in `model.py`. So do
`content_fingerprint`, `new_item_id`, the shared marker vocabulary and derived
`TERMINATOR`, style loading/resolution, `_user_data_dir`, `STYLE_RULE_KINDS`,
`LOCKED_RULE_IDS`, spec text, and lint code catalogue. These retained clusters
serve shared callers or source assertions; the marker expressions retain one
source. Case/prerequisite directive regexes stay with their retained readers.
Moved lesson readers call the existing `model.parse_question`, never another
bank parser. The core dependency-layer gate discovers root modules and includes
all four new siblings automatically.

The test monkeypatch search covered `mock.patch("model.`, `patch.object(model`,
model attribute assignments, and `setattr(model`. Existing targets are
`_user_data_dir`, `parse_lesson`, `parse_terms`, and `load`. The first and last
stay defined on the facade. `parse_media` resolves its call to the patched
`model.parse_lesson` at call time; an external wrap/count probe observed exactly
one call. Literal style-constant source assertions remain unchanged. Source
inventory checks now include the applicable sibling files in lesson,
localization, assessment-authority, capability-tracer, claim-word, and
subject-dispatch tests. No assertion was weakened.

### Baseline and final comparison

A throwaway script outside the repository captured SHA-256 for every uppercase
constant, the complete facade namespace, and parse/load/lesson/companion-reader
and lint outputs for every markdown fixture recursively under `fixtures/`.
Serialization uses `json.dumps(..., default=repr, sort_keys=True)`. Sets are
sorted before hashing; plain object sentinels have a stable type marker rather
than a process-specific memory address. These are representation normalizations
for comparison, not changes to runtime values.

Final result: all 66 uppercase constant hashes, all 38 fixture records, and
all facade names are identical, with no differences. `load` accepted 28 of
38 fixtures; `parse_lesson` returned without exception for all 38, including
its existing absent-section and degraded outcomes. Both default lint and lint
with explicitly parsed lesson/terms/keys/sources/cases/media/activities were
compared for every accepted bank; rejected loads and reader exceptions were
also recorded. All 85 original function/class bodies are byte-identical after
removing only the added late imports and AST-located `model.` qualifications.
A separate normalized AST comparison also passed for all 85 definitions.

`build.py` explicitly stages all four new root modules. A fresh temporary
`build.stage` tree was archived as a zipapp; a process outside the checkout
imported `model`, `runtime`, and `itembank` from that archive, loaded the sample
bank, and parsed the lesson fixture. Archive CLI lint passed: 6 items, 0 errors,
6 existing objective-prefix warnings. The first archive harness used a wrong
synthetic-bank format and fixture filename; the corrected harness passed.

### Checks and remaining coverage

| Check | Result |
| --- | --- |
| `python3 -c "import model, runtime, itembank"` | Exit 0 |
| `python3 scripts/preflight.py --quick` | Exit 0; all executed gates passed, including 41 core modules in layers; Python/JS suites and clean-tree gate skipped |
| Baseline/final comparison | All constants, fixture records, and names identical |
| Definition/source comparison and sibling-first imports | All 85 original bodies preserved; all four import orders passed |
| Fresh staged zipapp | Imports, bank load, lesson parse, and CLI lint passed |
| `tests/style_roundtrip.py` | Exit 0; all assertions passed |
| `tests/staged_parser_roundtrip.py` | Exit 0 |
| `tests/lesson_run_roundtrip.py` | Exit 0 |
| `tests/lesson_retention_roundtrip.py` | Exit 0 |
| `tests/product_gm_ui_lesson_roundtrip.py` | Exit 0 |
| `tests/lesson_progressive_roundtrip.py` | Exit 0 |
| `tests/note_trio_roundtrip.py` | Exit 0; 9 passed, 0 failed |
| `tests/localization_render_check.py` | Exit 0 |
| `tests/assessment_authority_adversarial.py` | Exit 0; 18 attempted, 18 refused, 0 succeeded |
| `tests/packaging_roundtrip.py` | Exit 0 |
| Socket-free lesson slice | 130 test functions passed, including spec, ID assignment, provenance, and paraphrase |
| Socket-free lesson-code slice | 2 test functions passed |
| Socket-free lesson-interaction slice | 16 unittest cases passed |
| Static stylesheet slice | 13 checks passed over 27 collected stylesheets |
| Changed source-inventory assertions | check_honest_limits_gate, scenario_localization, and test_no_subject_dispatch_in_surfaces passed |
| Socket-free agent-lesson-revision slice | check_keyed_content_refused passed |
| `git diff --check` | Exit 0 |

Slices use external harnesses with the original test definitions and assertions.
The lesson harness omits unguarded top-level test invocations and calls the
socket-free functions explicitly. There are no standalone lint, spec,
id_assign, provenance, or paraphrase roundtrip filenames in this checkout;
those checks are present in the lesson and style suites. Large modules,
including `model.py`, `build.py`, and lesson/source-inspection tests, were
sampled by symbols and bounded windows rather than displayed whole.

Loopback binding was directly probed and raised
`PermissionError: [Errno 1] Operation not permitted`. The following full or
socket-dependent checks remain unverified:

| Suite | Open checks |
| --- | --- |
| lesson_roundtrip | test_lesson_src_degraded_daemon_and_cli; test_routes_and_cli_twin; test_gloss_route_and_cli_twin; test_key_review_route_and_cli |
| lesson_code_roundtrip | test_runnable_page_contract; test_lesson_run_observation; test_lesson_run_refusals_and_bounds; test_lesson_run_zero_evidence_and_session_delta |
| lesson_interaction_roundtrip | test_native_route_writes_nothing |
| stylesheet_roundtrip | collect_served and assertions over served CSS; check_fonts_served; check_every_served_page_declares_fonts; check_type_scale |
| lesson_exploration_roundtrip | check_routes and optional check_browser, both requiring native served routes |
| agent_lesson_revision_roundtrip | check_lesson_correction; check_changed_source_refuses_accept; full suite exited 1 at its stub-server bind |

An initial static stylesheet slice correctly refused to assert the type-scale
check without its required served CSS. The final static slice excludes the
three named served checks and preserves every assertion. Full
`capability_stress_corpus_tracer` exited 0 with 0 passed and 18 skipped because
its shipped-suite prerequisites need sockets; its changed localization
scenario separately passed. The additionally attempted `paced_lesson_tracer`
exited 1: 3 scenarios passed, 5 failed. Its full-sitting daemon bind failed,
three dependent scenarios lacked the route, and its visual-QA browser launch
terminated with SIGABRT. These environmental gaps remain open; no source fix
or weaker test was applied for them.

Two pre-existing em dash characters remain in retained `model.py` text to keep
the original bodies verbatim. No new prose or sibling module introduces one.
Final source/package checks establish the extraction and stated coverage;
socket-enabled verification and reviewer acceptance remain open.


## Runtime split (2026-10-09)

User-authorized implementation of the accepted M1-M5, D1 and R1 proposal.
This is a source refactor with import plumbing only. No Git staging, commit,
push, installation or deployment occurred.

### F1: Extraction and authority

| File | Lines | Moved responsibility |
| --- | ---: | --- |
| runtime.py | 2,876 | Public facade, sole scorer and all R1 retained definitions |
| runtime_sessions.py | 206 | M1 session persistence, migration, staged bindings and views |
| runtime_teaching.py | 416 | M2 authored ladder and teaching-state bookkeeping |
| runtime_feedback.py | 311 | M3 release policy and existing-feedback rendering |
| runtime_visual_contract.py | 248 | M4 protocol validation and public renderer contracts |
| runtime_gloss.py | 184 | M5 authored answer rendering and glossary disclosure gate |

The original facade had 3,994 lines; the facade reduction is 1,118 lines.
All 60 proposed names moved: 42 functions and 18 constants/registries. Every
moved name, including private helpers, is explicitly re-exported. Internal
modules import only standard-library dependencies at load time; functions
resolve runtime-owned helpers and constants through local `import runtime`
and call-time facade attributes. No sibling imports another sibling at load
time. Surfaces continue using the facade.

All R1 candidates remain in runtime.py, including normalization and keys,
scoring, polynomial and visual verdict machinery, teaching_transition,
_idempotent_canon, selected-option classification, checkpoint feedback,
session_summary, public_item and page_item. No additional proposed name
required withholding. An external text audit checked all 108 retained
functions/classes/constants byte-for-byte and all 42 moved functions
byte-for-byte after undoing only local imports and facade qualifiers.

The runtime architecture diagram line alone changed in AGENTS.md, retaining
column alignment. The identical line was absent from .claude/CLAUDE.md and
docs/AGENT-REFERENCE.md; neither needed edits. Numbered rules are unchanged.
Existing function text, including the teaching separator literal, was moved
verbatim. No new prose uses an em dash.

### F2: Before/after comparison

Before editing, a throwaway script outside the repository saved SHA256 hashes
for every uppercase runtime constant and JSON with `default=repr` for
public_item, explain_payload and score_response on every item in every
fixtures/*.md bank accepted by model.load. Responses were the canonical key,
an empty string and the wrong option Z. Exceptions were recorded by type and
message. Both revealed and unrevealed explanations were recorded. Constant
serialization sorts sets and serializes registry callables by unchanged
source rather than process-specific memory addresses; all runs use the same
hash seed.

Result: **byte-identical** before/after JSON, covering 45 constants, 26 banks,
135 items and 405 score calls. Six model.load-rejected fixture files were
recorded separately with identical rejection results. No differences.

Combined before/after SHA256:
`44e3546895ca707d4c4a36bee4366a14e391e80e06c01e34757dfcf38c95768f`.

The unchanged inspect.getsource(score_response) SHA256 is
`39d0e61fd2da19c8b7896db2bf96ed4db83200172bdbe004139afbfe24329f64`.
The scoring test still requires exactly one score_response in runtime.py and
retains its existing pinned hash and all previous assertions.

### F3: Source inspections, rebinding and packaging

The proposal's source-inspection table names five files. Those five now cover
all extracted modules, and course_resume_roundtrip is the sixth strengthened
T1 file, testing facade identity for functions/constants, absence of load-time
back-imports and observable call-time rebinding. No existing assertion was
removed or weakened.

| T1 file | Exact verification result |
| --- | --- |
| scoring_roundtrip | Full script exit 0; all five modules present, one scorer and pinned source |
| model_surface_roundtrip | Full script exit 0; extracted source included in prohibited-flag scan |
| model_phase_roundtrip | Full script exit 1 at socket bind; run_contract_audit separately passed |
| subject_loop_roundtrip | Full script exit 1 at socket startup; test_no_subject_dispatch_in_surfaces separately passed |
| course_guidance_journey_roundtrip | Full script exit 1 at socket startup; source_fingerprints separately verified all five module paths |
| course_resume_roundtrip | Full script exit 1 at socket startup; check_runtime_facade separately passed on final source |

The original course-shelf patch route was also exercised without a server:
with a persisted synthetic sitting, patching runtime.read_session to raise
PermissionError changed the shelf cue from Session in progress to Session
status unavailable. The patch was called. Facade lookup remains observable.

All five modules are included in build.py STAGE_FILES. An external harness
called build.stage, created a zipapp, and launched isolated Python from outside
the checkout. `import runtime, model, itembank` succeeded with runtime.__file__
inside the staged archive. packaging_roundtrip exited 0; its existing optional
onedir-sidecar checks skipped because that artifact was not built.

### F4: Verification and limitations

- `python3 -c "import runtime, model, itembank"`: exit 0.
- `python3 scripts/preflight.py --quick`: exit 0, including layers:
  46 core modules have no client imports. Tests, clean-tree and JS gates skip
  under the existing quick policy; model.py and surfaces/daemon.py remain
  above the size warning threshold.
- External text/AST audits and before/after comparison: passed.
- Full suite commands: 71 attempted, 36 exit 0, 34 exit 1 on socket startup,
  and evidence_roundtrip timed out after 120 seconds. The inventory below
  preserves exact command outcomes rather than claiming full-suite passes
  from partial checks. LTI's exit 0 includes two crypto-free checks only;
  its signature checks skipped because cryptography is not installed.
- Original non-socket slices: 42 hint checks, 23 evidence checks, the three
  separately invoked T1 source checks, the facade check and
  lesson_roundtrip.test_glossable_gate passed. No assertion rewriting.
  The evidence slice additionally demonstrated the day socket restriction;
  serve/day checks remain open. The original course-shelf patch check passed.

Loopback binding raises `PermissionError: [Errno 1] Operation not permitted`.
Some harnesses report this as a daemon failing to print a URL. A control run
of check_disclosure_roundtrip with the original pre-split runtime reproduced
its identical assert-base failure, confirming that startup gap predates the
split. Socket cases cannot be certified in this sandbox.

Every command in the following inventory is `python3 tests/<name>.py`:

| Suite | Result |
| --- | --- |
| scoring_roundtrip.py | Exit 0 |
| model_surface_roundtrip.py | Exit 0 |
| model_phase_roundtrip.py | Exit 1; socket startup blocked |
| subject_loop_roundtrip.py | Exit 1; socket startup blocked |
| course_guidance_journey_roundtrip.py | Exit 1; socket startup blocked |
| hint_roundtrip.py | Exit 1; socket startup blocked |
| model_gate_roundtrip.py | Exit 0 |
| course_resume_roundtrip.py | Exit 1; socket startup blocked |
| a2_question_families_roundtrip.py | Exit 0 |
| a5_inline_fields_roundtrip.py | Exit 0 |
| a5_served_integration_roundtrip.py | Exit 1; socket startup blocked |
| activity_graph_contract_roundtrip.py | Exit 0 |
| blueprint_roundtrip.py | Exit 0 |
| check_disclosure_roundtrip.py | Exit 1; socket startup blocked |
| check_kill_roundtrip.py | Exit 0 |
| check_roundtrip.py | Exit 1; socket startup blocked |
| coding_unit_roundtrip.py | Exit 1; socket startup blocked |
| connected_unit_roundtrip.py | Exit 1; socket startup blocked |
| course_guidance_engine_roundtrip.py | Exit 0 |
| desk_experience_roundtrip.py | Exit 1; socket startup blocked |
| diagram_roundtrip.py | Exit 1; socket startup blocked |
| evidence_anchor_contract_roundtrip.py | Exit 0 |
| fill_roundtrip.py | Exit 0 |
| fill_surface_roundtrip.py | Exit 1; socket startup blocked |
| hotspot_roundtrip.py | Exit 1; socket startup blocked |
| import_roundtrip.py | Exit 0 |
| latex_input_roundtrip.py | Exit 0 |
| learner_artifacts_roundtrip.py | Exit 0 |
| lesson_code_roundtrip.py | Exit 1; socket startup blocked |
| lesson_roundtrip.py | Exit 1; socket startup blocked |
| lesson_run_roundtrip.py | Exit 0 |
| lti_roundtrip.py | Exit 0; signature checks skipped (missing cryptography) |
| matching_workflow_roundtrip.py | Exit 1; socket startup blocked |
| model_adapter_roundtrip.py | Exit 1; socket startup blocked |
| ordering_authoring_roundtrip.py | Exit 0 |
| ordering_contract_roundtrip.py | Exit 0 |
| ordering_gate_roundtrip.py | Exit 0 |
| ordering_workflow_roundtrip.py | Exit 1; socket startup blocked |
| polynomial_production_roundtrip.py | Exit 0 |
| presentation_profiles_roundtrip.py | Exit 0 |
| product_gm_integration_course_roundtrip.py | Exit 1; socket startup blocked |
| product_gm_integration_source_journey_roundtrip.py | Exit 1; socket startup blocked |
| product_gm_integration_source_return_roundtrip.py | Exit 1; socket startup blocked |
| product_gm_iteration_pending_return_roundtrip.py | Exit 1; socket startup blocked |
| product_gm_ui_journey_roundtrip.py | Exit 1; socket startup blocked |
| question_domains_roundtrip.py | Exit 0 |
| rich_practice_readiness_roundtrip.py | Exit 0 |
| runner_verdict_roundtrip.py | Exit 0 |
| source_adapters_roundtrip.py | Exit 1; socket startup blocked |
| staged_activity_contract_roundtrip.py | Exit 0 |
| staged_checker_disclosure_roundtrip.py | Exit 0 |
| staged_checker_ui_roundtrip.py | Exit 1; socket startup blocked |
| timeline_roundtrip.py | Exit 1; socket startup blocked |
| trace_roundtrip.py | Exit 1; socket startup blocked |
| true_false_roundtrip.py | Exit 0 |
| ui_overhaul_journey_roundtrip.py | Exit 1; socket startup blocked |
| ui_overhaul_navigation_roundtrip.py | Exit 1; socket startup blocked |
| visual_accessibility_roundtrip.py | Exit 1; socket startup blocked |
| visual_authoring_roundtrip.py | Exit 0 |
| visual_evidence_roundtrip.py | Exit 1; socket startup blocked |
| visual_roundtrip.py | Exit 1; socket startup blocked |
| gift_export_roundtrip.py | Exit 0 |
| evidence_roundtrip.py | Timed out after 120 seconds; 23 non-socket checks separately passed |
| mock_exam_roundtrip.py | Exit 0 |
| polynomial_checker_contract_roundtrip.py | Exit 0 |
| pacing_roundtrip.py | Exit 0 |
| paced_view_roundtrip.py | Exit 1; socket startup blocked |
| protocol_roundtrip.py | Exit 0 |
| staged_production_roundtrip.py | Exit 0 |
| surface_roundtrip.py | Exit 0 |
| packaging_roundtrip.py | Exit 0; optional onedir-sidecar checks skipped |

Additional known socket suites not attempted after the restriction was proven:
math_offline_roundtrip, daemon_roundtrip, serve_roundtrip and
ui_overhaul_workspace_roundtrip. All exit-1 entries above require a rerun in a
socket-enabled environment; the hint API/browser cases and evidence serve/day
cases also remain open. No runtime behavioral difference was observed in the
verified corpus and non-socket checks.

### F5: Scope, recovery and next gate

runtime.py, build.py and the large test modules were sampled by symbol,
reference windows and AST/text audits rather than displayed in full. The
accepted proposal and task-scoped execution instructions were read before
editing. No unrelated source or installed application was changed.

Recovery: reverse this task's named-file diff, remove its five new modules,
and remove only this appended record while preserving any subsequent edits.
The remaining verification gate is the socket-dependent suite inventory above
in an environment that permits loopback binding. Optional LTI signatures and
packaged onedir checks retain their separate prerequisite gaps.
