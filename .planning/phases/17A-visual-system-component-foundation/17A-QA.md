# 17A visual QA evidence (plan 17A-04 Task 1)

Recorded 2026-08-31. Harness: `tools/visual_qa.py`, driving the pinned
dev-only Playwright Chromium approved in `17A-04-DECISIONS.md` D-17A-04-1
(playwright 1.62.0, Chromium 151.0.7922.34, VENDORED.md row `playwright`,
pin line `deps/visual-qa-pins.txt`). Page under test:
`visual_fixture.single_file()`, the one-file synthetic prototype in the
selected direction (`structured-studio`, sidebar nav, indigo accent, chosen
2026-08-20 in `17A-DIRECTION.md`), eight screens, zero script elements.

This file is layout evidence for the human A11Y-01 review, not a
certification. An agent never self-certifies accessibility; Task 2 below
stays Weibao's.

## Exact commands

```
python tools/visual_qa.py
python tools/visual_qa.py --json .planning/phases/17A-visual-system-component-foundation/17A-QA-EVIDENCE.json --shots <local dir>
python tests/visual_accessibility_roundtrip.py
```

Exit 0 means every positive gate passed AND the deliberately hover-only
fixture failed equivalence review. Exit 3 is the refusal when Playwright is
absent; the matrix then falls back to this file's human script.

## The matrix, measured

Full machine-readable record: `17A-QA-EVIDENCE.json` (same directory).

| Gate | Result | Measured |
|---|---|---|
| width-1280 | pass | 8 of 8 screens, no horizontal overflow |
| width-768 | pass | 8 of 8 screens, no horizontal overflow |
| width-375 | pass | 8 of 8 screens, no horizontal overflow |
| zoom-200-reflow | pass | viewport 640 (WCAG 1.4.4 equivalence of 200 percent at 1280), 8 of 8 screens reflow with no horizontal overflow |
| keyboard-order-and-focus | pass | 53 focus stops across all screens; every stop shows an outline of at least 2px on the element, its label, or its `:focus-within` ancestor; focus cycles, no trap |
| targets-44px | pass | 259 interactive elements measured at 768px; 0 non-inline controls under 44px; 6 inline targets carry the WCAG 2.5.8 inline exemption |
| contrast-light | pass | 785 text samples, minimum ratio 4.79, none below WCAG AA |
| contrast-dark | pass | 785 text samples, minimum ratio 4.54, none below AA |
| contrast-oled | pass | 785 text samples, minimum ratio 4.79, none below AA (oled leg renders `theme.theme_css({"theme": "oled"})` appended after the page CSS, exactly what `itembank config set theme oled` serves) |
| reduced-motion | pass | 0 running animations under `prefers-reduced-motion: reduce` |
| touch-disclosure | pass | tapping the first visible glossary trigger (`inspiration`) in a touch context opens its popover definition |
| static-fallback | pass | 0 script elements; 15,888 innerText chars across the eight screens; no screen under 300 chars; 31 headings |
| fixture-disclosure-equivalence | pass | 0 hover-revealed disclosures without a keyboard or touch equivalent |
| hover-only-negative | **fails, as required** | the deliberately hover-only definition (non-focusable span, `:hover`-only reveal, no focus rule) is caught with the reason "hover-only disclosure has no keyboard or touch equivalent" |

Screenshots were written locally and are not committed (this repository has
never carried a binary image; the evidence JSON records their SHA-256):

| Width | SHA-256 |
|---|---|
| 1280 | `5a144c975b89f40cec27e938e659888975994731fa7fb12af5935c38beffb858` |
| 768 | `5a7da1fbb5781f8ba10bf48ef50ce946357cad1e27d875776dd630b66552ca9a` |
| 375 | `bd474475999d14ce9879ba6e6df4774b1673a8443aa740bf12a3109d317263ae` |
| 640 (200 percent) | `6e9479e242ad1b935c0a39f5eec280752f0393b97394c554c1eb93c102fa2118` |

Reproduce them with the `--shots` flag; hashes change only if served bytes,
the browser build, or the pin change.

## Defects the layout engine found, and their fixes

Every one of these was invisible to the byte-level and jsdom checks and was
caught on the first driven-browser runs. All are fixed and re-measured green.

1. **The dark and oled accent was never contrast-corrected on this page.**
   `visual_fixture.token_css` emitted one raw `--accent` after the theme's
   dark media override, so dark mode rendered the light accent: the primary
   action measured 2.77:1. `token_css` now routes through
   `theme.derive_theme` and emits the light and dark accent pair
   (`surfaces/visual_fixture.py`).
2. **Every scoped accent palette in the one-file export was inert.**
   `_scope_css` rewrote `:root` to `body:has(...) :root`, which matches
   nothing, ever (`:root` is never a descendant of `body`). The accent
   switch did nothing. `:root` now maps to the guard itself.
3. **Keyboard focus on the switch radios was invisible.** The visually
   hidden 1px inputs took the global `:focus-visible` outline, which is no
   indicator at all. Per-control `body:has(#id:focus-visible) label[for=id]`
   rules now draw the outline on the visible label.
4. **Twenty-one controls measured under 44px** (switcher labels, accent
   swatches, pager labels, prototype buttons, and the shipped
   `details summary` disclosure at 32px). All now carry `min-height: 44px`
   (and `min-width` for the swatches); the summary fix is in
   `surfaces/presentation.py` `SHARED_CSS`, so it reaches every served
   surface, matching the `button.go` precedent already there.
5. **The one-file export embedded the live agent console iframe**, which is
   always a dead frame in the sandbox this export exists for, and which
   leaves a focus stop no CSS can mark (Chromium matches neither `:focus`
   on a frame nor `:focus-within` on its ancestor once Tab moves into a
   cross-origin frame document; measured directly). The one-file export now
   renders a static placeholder that says when the live console embeds; the
   served route keeps the live frame and its wrapper carries a
   `:focus-within` indicator.

## What remains human: the Task 2 scripted review (A11Y-01)

Weibao performs this against the one-file fixture (and optionally the served
`/_visual-fixture` route with `ITEMBANK_VISUAL_FIXTURE=1`):

1. **Keyboard:** Tab through each screen; confirm the focus outline is
   always visible and the order matches reading order; use arrow keys inside
   the Look, Nav, Accent, and Screen switch groups; Escape closes an open
   glossary popover.
2. **Touch:** on a touch device or emulation, operate every switch, pager,
   glossary trigger, and disclosure with taps only.
3. **Screen reader:** with VoiceOver, walk one lesson screen and the
   practice screen; confirm the task, legal actions, response state, and
   result are announced; confirm nothing announces key material or unshown
   hint text; confirm the glossary popover's definition is reachable and the
   static console placeholder reads as what it is.
4. **Zoom and reflow:** 200 percent browser zoom at a 1280 window; confirm
   reading remains single-column scroll with no horizontal pan.
5. **High contrast and themes:** light, dark, oled; forced-colors mode if
   available; confirm state chips remain distinguishable without color.
6. **Reduced motion:** with the OS setting on, confirm nothing animates.
7. **Equivalent-task:** complete the practice item once by pointer and once
   by keyboard only; the two paths must be the same task.

Acceptance, rejection, or a named gap is recorded in `17A-FREEZE.md` by
Task 2, which also verifies the Phase 13.9 walking-skeleton summaries before
any freeze is written. (13.9 was walked 2026-08-25; the summaries are in
`.planning/phases/13.9-walking-skeleton/`.)
