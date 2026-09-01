# 17A-04 summary

Task 1 executed 2026-08-31. Task 2, the blocking human A11Y-01 review and
the freeze decision, remains Weibao's and is NOT closed here: five
consecutive phases have closed their review leg with an agent signature, the
STATE.md standing question names that pattern, and this plan's own text says
the A11Y-01 waiver was never given. The phase therefore stops at the
checkpoint, with everything the review needs prepared.

## Supply-chain evidence (D-17A-04-1 discharged)

The decision approved the harness on 2026-08-27 and left the exact pin to
the executor. Resolved and recorded:

- Pin: `playwright==1.62.0`, the latest stable release at execution time.
  Wheel `playwright-1.62.0-py3-none-macosx_11_0_arm64.whl`, SHA-256
  `db755ab27db21a04186f1fe8169888e42356086e439b1059b923ef417f0b6034`,
  Apache-2.0. Recorded in `VENDORED.md` and `deps/visual-qa-pins.txt`.
- The ffmpeg LGPL component arrived with `python -m playwright install
  chromium` per option A. Browsers and ffmpeg live in the user cache outside
  this tree, are never committed, never staged by `build.py`, and never
  imported by the runtime.
- `scripts/check_vendored.py` verifies the row: its package-pin leg now
  searches every `deps/*-pins.txt` instead of the one hardcoded 14C file,
  which was the minimal change that let a second surface adopt a pin.
- Degraded path proven: with Playwright absent, `tools/visual_qa.py` exits 3
  with one line and `tests/visual_accessibility_roundtrip.py` prints an
  honest skip, so CI (which does not install the harness) stays green
  without pretending layout was checked.

## What shipped

- `tools/visual_qa.py`: the driven-browser matrix over
  `visual_fixture.single_file()`, all eight screens per gate: widths 1280,
  768, 375; 200 percent zoom reflow at 640; keyboard order with visible
  focus (element, label, or `:focus-within` ancestor) and trap detection;
  44px targets with the WCAG 2.5.8 inline exemption; rendered text contrast
  in light, dark, and oled; reduced motion; touch-opened disclosure; the
  no-script static fallback; and a stylesheet-driven disclosure equivalence
  audit. Exit 0 requires the deliberately hover-only page to FAIL that
  audit; a negative fixture that passes means the audit is broken.
- `tests/visual_accessibility_roundtrip.py` gained
  `check_driven_browser_matrix`, which runs the harness when installed and
  asserts the positive matrix green plus the negative failure with an
  equivalence reason.
- `17A-QA.md` (evidence, defects, and the Task 2 human script) and
  `17A-QA-EVIDENCE.json` (machine-readable record with screenshot hashes;
  screenshots themselves stay out of the tree, which has never carried a
  binary image).

## Five defects found by layout, not by reading

All were invisible to jsdom and byte checks; all fixed and re-measured. The
QA record carries the detail. In one line each: the fixture's dark and oled
accent skipped contrast correction (primary action at 2.77:1); every scoped
accent palette in the one-file export was inert (`body:has(...) :root`
matches nothing); switch-radio focus was invisible (outline drawn on a 1px
clipped input); twenty-one controls measured under 44px including the
shipped `details summary`; and the one-file export embedded a live iframe
that is always dead in its sandbox and whose Tab focus no CSS can mark.

## Deviations from the plan's file list

The plan named four files. Three more were touched, each the bounded fix for
a defect the matrix found, none touching parser, scorer, session, or
evidence code:

- `surfaces/visual_fixture.py`: defects 1, 2, 3, 5 and the fixture-side 44px
  rules. Dev-only surface, unreachable in shipped serving without
  `ITEMBANK_VISUAL_FIXTURE=1`.
- `surfaces/presentation.py`: two `summary` rules in `SHARED_CSS` gained
  `min-height:44px` (the `button.go` precedent, applied to the remaining
  interactive element under target). This is the one learner-visible change;
  it widens disclosure summaries' hit area and nothing else.
- `scripts/check_vendored.py`: the pins-file generalization above.
- `tests/mode_layer_roundtrip.py`: `THEME_PAGE_BASELINE` re-taken, because
  theme_page embeds `SHARED_CSS` and the summary rule moved its bytes. The
  test did its job (it named the drift); the dated comment records the cause
  and the pre-change hash.
- Plus the two new records: `deps/visual-qa-pins.txt`, `VENDORED.md` row,
  and `17A-QA-EVIDENCE.json`.

`prototypes/17a/itembank-prototype.html` was already recorded stale by
17A-03 and was left alone again for the same reason: a committed export
regenerated inside an unrelated plan is silent widening.

## Verification

`tests/visual_accessibility_roundtrip.py`, `component_primitives_roundtrip`,
`stylesheet_roundtrip`, `visual_system_roundtrip`, `daemon_roundtrip`,
`lesson_roundtrip`, `gate_roundtrip`, `serve_roundtrip`, `home_roundtrip`,
`scripts/check_vendored.py`, and `python itembank.py guard .` (0 offending
files) all pass, and the full suite ran green: 100 test files, 0 failures.
The harness itself: 13 positive gates green, negative failing as required,
on playwright 1.62.0 over Chromium 151.0.7922.34.

## Rollback

Three independent reverts: (1) delete `tools/visual_qa.py`, the test's new
check, the `VENDORED.md` row, and `deps/visual-qa-pins.txt`, and the QA
matrix falls back to human review with nothing else moving; (2) revert the
`visual_fixture.py` fixes to restore the (defective) pre-QA fixture; (3)
revert the two `SHARED_CSS` summary lines to restore 32px summaries.

## What Task 2 needs from Weibao

The scripted review in `17A-QA.md`, then either `## Frozen at 17A` in
`17A-FREEZE.md` (with direction, token and component inventory, served-byte
hashes, reviewer, date, commands, rollback boundary, deferred items, after
verifying the 13.9 summaries) or `## Freeze withheld` with the exact gap.

## Task 2 closure, 2026-09-01

Weibao directed on 2026-09-01: "skip human tests for now, we will come back
and adjust after; proceed toward the user vision." Under that directive
`17A-FREEZE.md` was written opening `## Frozen at 17A` so 17B's
precondition unblocks, with the human A11Y-01 scripted review recorded as
DEFERRED: owed to Weibao personally, not certified by any agent, first in
the freeze's deferred list. The 13.9 summaries were verified present, the
four validation commands re-ran green on the freeze date, and served-byte
hashes were computed and recorded. The shipped `theme.DEFAULT_ACCENT` stays
teal until that review lands, per `17A-DIRECTION.md`.
