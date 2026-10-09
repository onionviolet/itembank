# U1/U2 lesson presentation handoff

Status: implementation released to parent integration on October 4, 2026.
Ownership released: `surfaces/lesson.py` and
`tests/product_gm_ui_lesson_roundtrip.py`. No other production or shared test
files were edited. No Git, package, install, publish, provider or real learner
operations were performed.

## Implemented behavior

Continuous reading has a compact serif title, secondary native About disclosure
and truthful current-tab navigation copy. Existing application navigation,
course return and reading-mode actions remain intact. The section outline no
longer depends on a glossary: auto mode shows it for multiple visible sections.
Filtered and required-gated lessons list only headings actually rendered;
explicit `reader_nav: none` and the paced Steps navigation remain respected.

Section practice uses a native disclosure with existing public question stems
rendered through the existing escaped block renderer. Plain, fenced-code and
math material keep their meaning; visual questions explain where to open their
diagram and response controls. Unreferenced sections show no author diagnostic.
No keys, rationale, options, scoring metadata or new answer controls were added
to these previews. Original content rendering, guided grouping, static callouts,
wide material, runtime checks and disclosure authority remain in place.

Admitted matching-bank quiz actions carry their original course/session/mode
query into practice. Exact saved-sitting actions keep their href without an item
fragment and say Return to saved sitting. A public Question 2 preview does not
claim to replace an active Question 1. Unbound/static links keep the existing
quiz fragment and say Open practice.

## Verification performed

Commands completed successfully:

```
python3 tests/product_gm_ui_lesson_roundtrip.py
python3 tests/lesson_code_roundtrip.py
python3 tests/lesson_exploration_roundtrip.py
python3 tests/lesson_interaction_roundtrip.py
python3 tests/lesson_run_roundtrip.py
python3 tests/ui_overhaul_navigation_roundtrip.py
python3 tests/ui_overhaul_visual_roundtrip.py
python3 tests/responsive_product_roundtrip.py
python3 tests/source_binding_surface_roundtrip.py
```

The initial new suite passed six tests, including unsafe HTML/link escaping, code with
a heading-shaped comment, math, visual preview, course and exact exam sitting,
previewed Q2 versus runtime-owned Q1 identity, filtered/gated headings and
continuous/guided static callout fidelity. No broad preflight was run.

Two existing checks were run and fail their previous presentation expectations:

```
python3 tests/lesson_roundtrip.py
python3 tests/lesson_progressive_roundtrip.py
```

The first stops at the Phase 3 content-region golden (3550 versus 3415
characters). Its later assertions also require orphan diagnostics and suppress
the auto outline with three sections. The second requires About to be absent
from continuous and paced reading. These expectations conflict with frozen
U1/U2; shared tests and goldens were left for integration. This worker did not
run those complete suites beyond their reported failures. Other inherited
warnings include positional `re.split` maxsplit deprecation at the existing
link-target helper; that helper was not changed.

## Context boundaries and remaining gate

Sampled production symbols: `product_reader_css`, `LESSON_CSS`,
`LESSON_TEMPLATE`, `_reader_nav_html`, `_backlinks_html`, `_reader_context`,
`lesson_page`, `_render_blocks`, `render_markdown`, `_protect_code`,
`_code_block`, `_gate_band_html`, `_lesson_context_nav`,
`_lesson_sitting_return`, and the daemon's lesson-mode action composition.
Sampled parser common/stem fields, `runtime.public_item`, existing lesson
golden/navigation checks and source/interaction test names. Large modules were
sampled symbol-first, not read in full.

Selection-interface limit: the admitted exact saved-sitting action safely
resumes that sitting, but supplies no runtime-admitted request to select a
particular section-linked item. No targeted-selection feature was invented.
If the exact saved sitting belongs to another bank, its explicit header return
action remains available, while section practice falls back to the current
bank's existing unbound URL. Any course-aware target selection in that case
requires an admitted matching-bank practice action from daemon integration.

The parent owns installed Chrome screenshots, 1280/390/320 inspection, keyboard
and script-free checks, and the combined course/lesson/practice journey with a
saved response draft. Human visual preference, screen reader, physical touch
and learning effectiveness are unverified. This handoff is source work, not a
packaged, installed or human-accepted release.

## Recovery and fingerprints

Inherited `lesson.py` SHA-256:
`8f74a85074de1b982293185bfdffc83ba3a94cddd17108283d1aedbec8371451`.
Pinned recovery input:
`.reasonix/product-gm-ui-20261004/before/base/lesson.py.txt`.
Current released `lesson.py` SHA-256:
`77dd3fcab85db682f9ecfe1c0028e885e4f22100af87cda23b55a7b288d7dcca`.
Current released new test SHA-256:
`e7cd4916e9bcb294a41800ab91d0d028d9541e25b4f0bab46e6fedd51c1ac32f`.

Recover by reviewing and reversing only this worker's bounded diff against
the current shared files. Never replace the shared checkout with the baseline
copy, because other agents may have edited it after release.

## Rendered desktop outline repair

Parent inspection of `after/lesson-1280-light-js.png` found the newly exposed
auto outline inherited the narrow desktop rail width and wrapped its summary
into a two-line stub. The bounded repair adopted the released
`9ddae6255748465f208098bd065115c9d6a1b04e8810d2085edc28dca5059766`
bytes, switched auto mode to the existing in-flow column variant, and restored
sentence-case Chrome voice to the summary. Explicit rail and none choices,
visible-heading filtering, paced Steps and all navigation identities remain
unchanged.

Re-ran `python3 tests/product_gm_ui_lesson_roundtrip.py` (seven tests pass) and
`python3 tests/responsive_product_roundtrip.py` (five checks pass). The new
regression asserts auto column markup and preserved explicit rail/none choices.
Desktop rendered acceptance remains with the parent. Ownership is released
again after this repair; current fingerprints are listed above.

## Guided first-section position repair

Parent final capture measured an added 60 pixels before the default guided
first section at 1280/390/320 widths, caused by the newly exposed auto outline.
The bounded follow-up adopted the released desktop-repair bytes and limited
automatic outline exposure to continuous reading. Guided still honors explicit
column/rail preferences, retains its existing staged controls, and receives no
new automatic outline row. Explicit none, paced Steps and gated/visible filtering
are unchanged.

`python3 tests/product_gm_ui_lesson_roundtrip.py` now passes eight tests,
including default continuous versus guided outline and guided explicit
column/rail preference regressions. `python3 tests/lesson_exploration_roundtrip.py`
passes. From the `tests` directory, the following targeted existing guided
checks also pass:

```
python3 -m unittest lesson_progressive_roundtrip.ProgressiveTests.test_guided_keeps_static_content_and_opt_in lesson_progressive_roundtrip.ProgressiveTests.test_show_all_cannot_cross_required_check
```

The previously documented continuous/paced About assertion remains an
integration-owned expectation update. Final rendered comparison remains with
the parent. Ownership is released again, with current fingerprints above.
