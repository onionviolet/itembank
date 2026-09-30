# UI overhaul lane N evidence

Date: 2026-09-30. Status: source implementation and targeted synthetic checks
complete; installed, human preference and full accessibility acceptance open.

F1: Home repeated the complete course collection and its administration beneath
the focus card. Home now keeps exact saved-session entry and compact course
choices, with an explicit link to the complete Courses collection. Courses
retains drag and keyboard reorder, recovery actions, course options and sample
removal. Walkthrough controls live in a native Workspace help disclosure.

F2: Known active sessions name Resume practice or Resume test. Ambiguous
sittings name Choose a saved sitting and retain the course overview chooser.
Canonical action hrefs, accessible course-specific labels and shelf order are
unchanged. Course overview has hooks for content, context and saved sittings.
The bank-only fallback no longer says course objects have yet to ship.

## Ownership and recovery

Changed source: `surfaces/daemon.py` presentation regions `_app_nav`,
`_course_action_label`, `_course_frame`, `_desk_course_choices`,
`_course_shelf_body`, and course-list composition in `handle_courses_get`;
`surfaces/home.py` `_cards_html` explanatory copy only.
Changed tests: `tests/desk_craft_roundtrip.py` splits compact Home assertions
from complete collection assertions; new `tests/ui_overhaul_navigation_roundtrip.py`.
Other assigned tests remain unchanged. No backend, storage, scoring or response
protocol changes. Shared presentation/theme modules were not edited.

Both source inputs matched the packet's dirty baseline before first edit.
Baseline SHA-256:

```text
surfaces/daemon.py 72e66da98728c114fa813e6588fdbc408a560fdcc93cd4c2046068b8c2e76b9c
surfaces/home.py 24307ce5b56d0e4351392d4803b1a7b585b57fc3feb6f974e2a089bb5c2c95e3
tests/desk_craft_roundtrip.py 6568f3e353e93c935199a1edc2207298feeccdb1465bc0ebee35e9d61462c77c
```

Final SHA-256:

```text
surfaces/daemon.py c6c702abeba1ecf8fdef50237648f92f99765a2c7c8f04b460d59ac6cf7a79b2
surfaces/home.py 90dafb159609c7f899f6ee1a7a36daf4b495c58fe0e732b04d081828d649d1a2
tests/desk_craft_roundtrip.py e40c3f771049240315793b3391f7a922bb6a8f702eae48dacacead86558156b2
tests/ui_overhaul_navigation_roundtrip.py ff0c0a1dcb27475a1d7f3b49d74dcb5b2231116b47d45fe3481b11dc3d70398e
tests/desk_experience_roundtrip.py bae4fdf321b1bf733d3cf0d721f8a7db413b94efb44781ada5499480aade761e
tests/course_shell_roundtrip.py 49bba8a21af9f4e586d9d47f98127fe079272b35d392d096ab9e9946a5bd3b3f
tests/course_resume_roundtrip.py fd7f03cae5285246bde8658d7ebf3f0baa76984ac8fdfaee2dffb7f3e47f0156
```

Exact source diffs against dirty copies are retained locally in
`.reasonix/ui-overhaul-20260930/N-daemon.patch` and `N-home.patch`;
test delta in `N-desk-craft.patch`. Undo only reviewed hunks against current
bytes. Never replace either source file with the baseline copy.

## Gates and observed limits

Passed commands, exit 0:

- `python3 tests/desk_experience_roundtrip.py`
- `python3 tests/desk_craft_roundtrip.py`
- `python3 tests/course_shell_roundtrip.py`
- `python3 tests/course_resume_roundtrip.py`
- `python3 tests/ui_overhaul_navigation_roundtrip.py --browser`

The new served test uses temporary synthetic courses and the existing daemon
harness. It verifies byte-identical learner files after Home, Courses and
overview GETs, exact sitting links, reload and return, all collection controls,
sample removal reachability, long multilingual names, and no horizontal
overflow at 1280px and 390px. Browser check uses installed Chrome through
Playwright's channel setting, never the learner installation. Browser mode is
optional so ordinary CI invocation remains stdlib-only.

`python3 scripts/preflight.py --quick --source-only` passed after the final
source change: lint, broken fixture, guard, mirrors, README commands, schemas,
vendored, paths and summaries. Build, complete suites, cleanliness and JS are
skipped by these flags. No full preflight, app build, installation, commit or
push was run. The inherited build hold remains.

Local screenshots: `.reasonix/ui-overhaul-20260930/N-shots/`, Home/Courses/
overview at both widths. The 390px Home image was inspected: readable saved
practice entry, wrapping multilingual title, visible collection link and
secondary Workspace help. Shared chrome was still being developed by V;
these images are an intermediate source preview, not final visual acceptance.
Failed test during development checked a drag string in the entire page and
matched the shared script; the corrected assertion checks rendered markup.

## Integration request and release

V/I may style `overhaul-home`, `overhaul-course-choices`,
`overhaul-course-choice`, `overhaul-home-tools`, `overhaul-course-heading`,
`overhaul-course-content`, and `overhaul-saved-sittings`. Home choice grid
placement has narrowly scoped local CSS, using existing shared card tokens.
Retain title wrapping and 390px single-column controls if consolidating it.
Full journey, failed save/retry, keyboard/accessibility and final shared visual
review belong to I. No new canonical metric or source lifecycle was introduced.

Read limits: daemon/home were read by relevant symbol windows, not whole files;
assigned test contracts and packet were read. Unrelated backend regions and
complete planning/vision history were not audited.

**Ownership release:** Lane N releases `surfaces/daemon.py`, `surfaces/home.py`
and all N-assigned tests to the integrator. No further source/test edits are
planned by N. Next action: I reviews these exact diffs and runs the combined
served journey after V/W release.
