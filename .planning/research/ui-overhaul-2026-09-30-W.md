# UI overhaul lane W evidence

Date: 2026-09-30. Status: source implementation frozen; integrator acceptance pending.

## Result and boundaries

F1: Reading uses a source-first two-column desk, with assignments in a native
 disclosure and private notes after source in DOM order. Saved notes, local draft,
source availability and explicit reading declaration remain separate. Reading
now emits generated theme CSS, fixing missing token values in the inherited
render. Its optional `theme_css` parameter permits the integrator to pass saved
root appearance settings without changing settings semantics.

F2: Lessons retain document composition and a prose measure, with wider existing
code, tables and diagrams. Wide documents align header and prose to the same
edge. Quiz work removes the outer card framing, distinguishes response from
runtime feedback, and gives structural/code/visual responses more width. Native
controls, input names, IDs, matching/ordering/inline fill, draft recovery and
runtime payloads remain unchanged. No parser, scorer, evidence, rights, lesson
 grammar or hint-tier edits.

F3: The exact `<div id="host"></div>` daemon substitution anchor and the lesson
`class="card"` content anchor remain intact. A first attempt changed them and
failed quiz return and lesson tests; both were corrected before final checks.
Do not replace these anchors without coordinating callers and structural tests.

## Owned paths and fingerprints

All four source bytes matched the packet's dirty base before first edit.
Inherited work was preserved. No existing test assertions were weakened.

| Path | Dirty base SHA256 | Final SHA256 |
| --- | --- | --- |
| `surfaces/reading_desk.py` | `0011e557ea9779b8b12ed2c6ecfc5578cf262f89c9e4c3ae01f4807f9bba4653` | `085244b14d3becb683fa86d5d1ba9eb51a2a6962f30fd5317dc64f1ec1ae1974` |
| `surfaces/lesson.py` | `8d9d3f34f8fa6f805b999a63768c69ab564174995ffa78e3c4e5f9b1a709da17` | `e7af446339d6904e64908ec62ad55027dfb3e4d8e2d96b1c68f2a29012ff56c3` |
| `surfaces/quiz_page.py` | `5bb9999c0f34998c2299f5b25618f6afb8ff86d0c4cbda2e7a9bc4a3b64c280f` | `598639300e9edd9f0f0ab49b401d39d1bc041d3dde2bd5e6873b3ba65b07636b` |
| `surfaces/quiz.py` | `b93d63ea7ac265b5c07d035edddce8a8b3d420d4b6465286cd8b15f4ead83fe3` | `01bd75abe3d059ca69deccd3e12ee135b4164b0b21449e3fceddd9103b5c9f70` |
| `tests/ui_overhaul_workspace_roundtrip.py` | `new` | `2bb376f9c106e0207ae1888926c281345404969de44e4b31dd2d0792b886c356` |

Exact lane-only patch against dirty input: `.reasonix/ui-overhaul-20260930/W/workspace.diff`.
Machine-readable hashes: `.reasonix/ui-overhaul-20260930/W/hashes.json`.
Restore only reviewed patch hunks against current bytes; never overwrite from base
or reset the shared checkout. No commits, pushes, branches, app/archive builds,
installation, release or real coursework access occurred.

## Commands and results

| Actual command | Result |
| --- | --- |
| `python3 tests/reading_desk_roundtrip.py` | Pass, 7 tests, including note save/retry and source recovery |
| `python3 tests/quiz_symbol_return_roundtrip.py` | Pass, default/practice/exam preserve exact sitting and cursor |
| `python3 tests/lesson_roundtrip.py` | Pass, rendering, provenance, grammar compatibility and link directions |
| `python3 tests/lesson_code_roundtrip.py` | Pass, controls/refusals, edited source, no evidence delta |
| `python3 tests/agent_roundtrip.py` | Pass, JSON/runtime disclosure and pending prose |
| `python3 tests/serve_roundtrip.py` | Pass, no key leak, native POST, refused-answer preservation and feedback pause |
| `python3 tests/ui_overhaul_workspace_roundtrip.py` | Pass, 3 structural and authority-boundary tests |
| `node --test tests/js/reading_note_save.test.mjs tests/js/matching_workflow.test.mjs tests/js/ordering_workflow.test.mjs tests/js/f1_inline_completion.test.mjs tests/js/question_workflow_recovery.test.mjs` | Pass, 28 tests |
| `python3 scripts/preflight.py --quick --source-only` | All running gates pass. Build, full tests, clean and JS skipped by flags; CI-only schema/dependency gates unrun |
| `python3 tests/scoring_roundtrip.py` | Fail, inherited `.reasonix/chat-wrapup-20260930/surface-test-before.py` counted as second scorer. That file was not changed |

ResourceWarnings from inherited file reads and a Python 3.14 re.split deprecation
were emitted; passing test exit codes were zero. No full preflight ran in W.
Workspace/reading/quick logs are under `.reasonix/ui-overhaul-20260930/W/`.

## Preview evidence and limits

Chrome via Playwright `channel='chrome'` rendered synthetic reading, lesson and
native served-quiz baseline HTML at 1280px and 390px, light and dark, with
JavaScript disabled. Twelve final layouts have no horizontal page overflow.
Reading includes long multilingual text; lesson fixture includes prose, tables
and code; quiz shows native answer controls. Screenshots and generated HTML are
under `.reasonix/ui-overhaul-20260930/W/`; `layout.json` records measurements.
Desktop reading/lesson/quiz and narrow quiz images were visually inspected.
These are no-script layout probes, not a complete served journey, human visual
preference or accessibility acceptance. Static captures do not verify fetching,
fonts served through daemon, active note saves or interactive lesson gates.
Targeted existing runtime/browser tests cover those preserved behaviors in part.

Sampled lesson presentation CSS/template, quiz page composition/render symbols,
quiz page_for CSS seam, reading module and exact cited workflow/UI/product
contract windows. Did not read the large lesson or quiz modules in full.

## Integration request and ownership release

A1: Integrator should pass the daemon's saved root `theme_css` into
`reading_desk.render(..., theme_css=...)` after N releases daemon ownership.
W uses THEME_CSS as its compatible default. Then run the frozen served journey
and final source-only gate. Shared V styling was consumed, never edited by W.

**Ownership release:** Lane W releases `surfaces/reading_desk.py`,
`surfaces/lesson.py`, `surfaces/quiz_page.py`, `surfaces/quiz.py`,
`tests/reading_desk_roundtrip.py`, `tests/quiz_symbol_return_roundtrip.py`,
`tests/ui_overhaul_workspace_roundtrip.py` and this lane evidence to lane I.
No further W writes are planned. Final hashes above are the frozen handoff.
