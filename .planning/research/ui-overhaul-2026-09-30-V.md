# UI overhaul lane V evidence

Date: 2026-09-30. Status: implementation frozen and ownership released.

F1: Replaced the 224px desktop rail with one compact sticky horizontal frame.
All four destinations retain native links and current-page identity. Mobile
navigation has intrinsic height, wrapping labels and 44px-or-larger targets.
Activity space now uses a 1200px outer canvas with measured prose inside it.
Context is static under the shared frame, avoiding competing sticky headers.

F2: Added shared workshop composition and N/W hooks: course choices, source,
private notes and response areas. Source/note roles remain independent of
assessment colors and custom accent. Native controls now follow selected
light/dark/OLED color-scheme. Settings copy uses 16px and 400/600 weights.
No persistence schema, palette derivation, scoring or saved settings changed.

D1: Quiet reading and expressive workshop previews use identical fictional
journey HTML. Quiet uses one reading column and minimal panel grounds;
workshop exposes source and notes together on desktop with distinct grounds.
Workshop is the reversible working direction, not a user preference claim.
Existing locked voice, type scale, target, focus, contrast and motion contracts
are preserved. No unresolved conflict with a frozen aesthetic rule was found.

Changed paths: `surfaces/presentation.py`, `surfaces/theme.py`,
`tests/responsive_product_roundtrip.py`, new `tests/ui_overhaul_visual_roundtrip.py`,
and `prototypes/ui-overhaul-20260930/visual/`. Other assigned tests unchanged.

Baseline source hashes matched the packet before edits. Exact source diff:
`prototypes/ui-overhaul-20260930/visual/source-diff.patch`. Hash manifest:
`prototypes/ui-overhaul-20260930/visual/hashes.json`.

| Path | Base SHA-256 | Final SHA-256 |
| --- | --- | --- |
| `surfaces/presentation.py` | `563a5bf9190adbbe7a09e71b0ecf71a38fa838a075d01f8aabe573beab070dfb` | `f3ae0422acc88c7235ec6d69a764966ef440ccb2c68397cf14d46d2d62970685` |
| `surfaces/theme.py` | `1380b674b1827505a6c28d36509b1ccd09e715deb37a8aed5d08e622488349e4` | `003282985f3e71447a6307ca852f1337d6db18f2c51b863544b0546b81dfc8d1` |
| `tests/responsive_product_roundtrip.py` | `unchanged or new test` | `0f6e441388146dc3023140d3016e7fec19242b8e73d0ad9090d29ed5c6338ea5` |
| `tests/ui_overhaul_visual_roundtrip.py` | `unchanged or new test` | `b6e8c4a4f89115574504a240f2a96ad82d4868c712d0600e8f50a2998bb643f5` |
| `tests/presentation_roundtrip.py` | `unchanged or new test` | `c73ef1bcaee592ba6c7e00ccfaefd18718ad60557f657ca74f4358301856fa6f` |
| `tests/theme_roundtrip.py` | `unchanged or new test` | `f9e68203c919523db0bec766ec4746b1d8033d74b0471cacc0857162d61b6d5f` |
| `tests/visual_character_roundtrip.py` | `unchanged or new test` | `677c4c60b429def2a9e35828c6a97f22f6c2287139560dc92ef2991a8fe5d648` |

Checks actually run:

- `python3 tests/presentation_roundtrip.py`: exit 0. The printed duplicate-h1
  FAIL is an intentional negative harness probe; the harness finishes green.
- `python3 tests/theme_roundtrip.py`, `tests/responsive_product_roundtrip.py`,
  `tests/visual_character_roundtrip.py`, `tests/ui_overhaul_visual_roundtrip.py`,
  and `tests/stylesheet_roundtrip.py`: each exit 0.
- `python3 scripts/preflight.py --quick --source-only`: all gates that ran pass.
  App/sample builds, Python/JS suites and dirty-tree gate were skipped as stated.
- `python3 tests/ui_overhaul_visual_roundtrip.py --previews`: generated same-content
  light/dark pairs and custom-accent workshop.
- `node prototypes/ui-overhaul-20260930/visual/verify.mjs`, with Playwright from
  `/tmp/itembank-overhaul-qa` and the installed Chrome executable configured:
  25 renders pass at 1440/1024/768/390/320px across both directions, light/dark
  and custom accent. Keyboard focus, target bounds, reflow, reduced motion,
  resize input retention, long/multilingual content and no-script disclosure pass.
  Local harness restored with `npm install --prefix /tmp/itembank-overhaul-qa
  --no-audit --no-fund --ignore-scripts playwright`; no runtime dependency added.
- `git diff --check` for lane edited source/tests: exit 0.

Observed screens: screenshot inspection of quiet-light desktop, workshop-light
desktop and workshop-dark 390px comparison journey, containing course entry,
source excerpt, private note and unscored native response. Browser captures and
metrics are in the prototype `observed/` directory. The lane did not inspect
installed screens or certify the served end-to-end course journey. I owns those
source integration checks; human visual/accessibility acceptance remains open.

Sampling: CSS, shell/nav helpers and theme emission/settings CSS were inspected.
The entire large presentation primitive implementation, theme persistence and
other runtime modules were not audited. Saved-theme compatibility is supported
by existing theme tests, not a new full runtime review.

Recovery: compare the source patch against current bytes and undo only its hunks.
Never restore baseline copies over subsequent integration or inherited edits.
The first browser probe had a preview-server path-normalization bug, fixed in
`verify.mjs`; canonicalize the base before prefix checking. Full-page captures
need scroll reset after resize/input focus, now explicit in that same harness.

Ownership release: V releases `surfaces/presentation.py`, `surfaces/theme.py`,
all five assigned tests and its prototype directory to I. No further V writes
are planned. No unresolved integration request. No commit, push, fresh app
archive/build, install, release or real coursework inspection occurred.
