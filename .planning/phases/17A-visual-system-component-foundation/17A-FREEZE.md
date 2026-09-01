## Frozen at 17A

- **Freeze date:** 2026-09-01
- **Authority:** Weibao's directive of 2026-09-01: "skip human tests for
  now, we will come back and adjust after; proceed toward the user vision."
  The freeze exists so downstream work (17B's precondition check) unblocks;
  the human review leg is DEFERRED, not waived and not certified. See the
  reviewer section below.

## Selected direction

`structured-studio` look, `sidebar` navigation, `indigo` accent (`#4a4ad4`),
chosen by Weibao 2026-08-20 and recorded in `17A-DIRECTION.md`. The other
two looks (`quiet-workbench`, `guided-canvas`), the other two navigation
shapes (`tabs`, `bottom`), and the other accents are kept as user-choosable
options per PLANNING-DIRECTIVES section 1; each direction stylesheet remains
one deletable file, guarded by `check_directions_are_deletable`.

Note carried forward from `17A-DIRECTION.md`: the shipped
`theme.DEFAULT_ACCENT` is still teal `#0e6e62`. Moving the shipped default
to indigo was named a token-freeze action needing the accessibility pass;
because the human leg of that pass is deferred (below), the shipped default
is NOT moved by this freeze. It stays teal until Weibao's review lands.

## Token inventory (counts and sources of truth, not duplication)

- **Scale tokens, `surfaces/presentation.py` `SHARED_CSS` `:root`:** 26
  custom properties: 5 frozen type sizes (`--text-xs` 12px, `--text-body`
  16px, `--text-lesson` 18px, `--text-heading` 20px, `--text-display`
  32px), 3 density tokens (`--density-row-gap`, `--density-card-pad`,
  `--density-list-gap`, each aliasing `--space-*` in comfortable and
  compact), 7 spacing steps (`--space-1` through `--space-7`), 3 radii
  (`--r-1` through `--r-3`), 2 measures (`--measure-prose`,
  `--measure-wide`), `--leading-lesson`, 4 font faces (`--font-chrome`,
  `--font-code`, `--font-ledger`, `--font-paper`), and `--sticky-h`.
  Pinned by `check_frozen_type_tokens` and `check_density_bounds` in
  `tests/stylesheet_roundtrip.py`; the exact table is in
  `17A-02-SUMMARY.md`.
- **Colour tokens, `surfaces/theme.py`:** `BASE_TOKENS` carries 6 tokens
  per mode and `SEMANTIC_TOKENS` 11 per mode, across the three modes
  `light`, `dark`, and the 17A-05 `oled` set (ground `#000000`, card
  `#080a0a`, chip `#0f1313`, line `#181d1c`, `ink`/`mut` and the semantic
  set inherited from dark, ratios re-measured, see `17A-05-SUMMARY.md`).
  `stylesheet_roundtrip` invariant 4 iterates `("light", "dark", "oled")`
  and re-measures every pairing through `theme.contrast_ratio` on every
  run, so the token values are held by measurement, not by this record.

## Component inventory

17 primitives in `surfaces/presentation.py`, one per row of 17A-UI-SPEC's
Component Styling Assignments table, held by
`tests/component_primitives_roundtrip.py` ("inventory: 17 primitives, one
per component row"): `course_shelf`, `activity_view`, `settings_panel` plus
`wrap_path`, `first_launch_walkthrough`, `status_notice`,
`note_capture_panel`, `notes_panel_evidence`, `strategy_picker`,
`progress_comprehension_display`, `note_output_trio` plus
`_clip_node_label`, `evidence_drawer`, `diff_review`, `anchor_chip` plus
`chip_row`, `fill_state`, `loading_line`, and the shared `_fallback` head,
each mapped to its ruling and its test in `17A-03-SUMMARY.md`. Seven state
rows (zero, one, many, error, loading, partial, overflow) applied uniformly.

## Served-byte hashes, method stated

Computed 2026-09-01 on this machine, Python 3, `hashlib.sha256` over UTF-8
encoded output of the named functions; each was rendered twice and compared
byte-identical before hashing.

| Artifact | Method | SHA-256 | Bytes |
|---|---|---|---|
| One-file visual system | `surfaces.visual_fixture.single_file()` | `34975bc7452116977ce288f8634f349366bde29199eccc624bb1192c500469d9` | 105560 |
| Shared stylesheet | `surfaces.presentation.SHARED_CSS` | `dd8c699ef2617d52b558853a03d6eed8343e591ea9ea818b85f3397bfaffba0b` | 14874 |
| Theme block, light | `theme.theme_css({"theme": "light"})` | `a13b6feb2b3454991c601f70d33ee3a85c35edb9b1431009201f21099f18bff5` | 340 |
| Theme block, dark | `theme.theme_css({"theme": "dark"})` | `a6b33743f7b68fde0011b8b7d0edd68ad19a3bda5e177d647f5a03a172f7a1f4` | 340 |
| Theme block, oled | `theme.theme_css({"theme": "oled"})` | `18ce54c94499843fb9b250c75c9ac5af4d2f0acfdbb5ea8594ce358e19bfa771` | 340 |

The rendered-pixel screenshot hashes (a different thing: pixels, not served
bytes, and tied to the Chromium 151.0.7922.34 pin) are in `17A-QA.md` and
`17A-QA-EVIDENCE.json`.

## Validation commands, run 2026-09-01, verbatim tail lines

`python tests/visual_accessibility_roundtrip.py` (exit 0):

```
ok: driven-browser matrix: 13 positive gates green in a real layout engine; the hover-only negative failed for the equivalence reason
PASS visual_accessibility_roundtrip.py
```

`python tests/component_primitives_roundtrip.py` (exit 0):

```
ok: component primitives roundtrip -- 17 components across zero, one, many, error, loading, partial and overflow
```

`python tests/stylesheet_roundtrip.py` (exit 0):

```
ok: stylesheet roundtrip -- 23 stylesheets balanced, popover never suppressed on screen, every var(--NAME) a served page references defined in that same page, no in-scope colour literals, quiz controls on --edge, semantic tokens at 4.5:1 and --edge at 3:1 in both modes measured by theme.contrast_ratio, 4 @font-face urls root-absolute, served 200 font/woff2, 404 under a page route, all 4 manifest-recorded faces declared by each of the 4 served routes (the quiz included), and in step with fonts/MANIFEST.json
```

`python itembank.py guard .` (exit 0):

```
0 offending files
```

## Reviewer

The human A11Y-01 scripted review (keyboard, touch, VoiceOver, zoom, high
contrast, reduced motion, and the equivalent-task check, the seven-step
script in `17A-QA.md` "What remains human") is **DEFERRED** by Weibao's
directive of 2026-09-01 ("skip human tests for now, we will come back and
adjust after"). It remains owed to Weibao personally, it is not certified
by any agent, and no agent signature closes it. What IS green is the
automated evidence: the 13-gate driven-browser layout matrix across three
themes (light, dark, oled) and all eight screens, including the hover-only
negative fixture failing for the required equivalence reason, on the pinned
playwright 1.62.0 over Chromium 151.0.7922.34 (`17A-QA.md`,
`17A-QA-EVIDENCE.json`). Automated layout evidence is not accessibility
certification and this record does not claim it is.

## Phase 13.9 evidence

Verified present 2026-09-01 before this freeze was written:
`.planning/phases/13.9-walking-skeleton/13.9-01-SUMMARY.md`,
`13.9-02-SUMMARY.md`, and `13.9-03-SUMMARY.md` all exist (the skeleton was
walked 2026-08-25).

## Rollback boundary

Per-plan reverts recorded in the 17A summaries, each independent:

- `17A-04-SUMMARY.md`: (1) delete `tools/visual_qa.py`, the test's driven
  check, the `VENDORED.md` row, and `deps/visual-qa-pins.txt` and the QA
  matrix falls back to human review; (2) revert the `visual_fixture.py`
  defect fixes; (3) revert the two `SHARED_CSS` summary `min-height:44px`
  lines to restore 32px summaries.
- `17A-03-SUMMARY.md`: the primitive layer comes out by deleting the
  `17A-03` section of `presentation.py` and the
  `SHARED_CSS = SHARED_CSS + PRIMITIVE_CSS` line.
- `17A-02-SUMMARY.md`: the day migration, the `surface_shell` arguments,
  and the type and density tokens, in that order.
- `17A-01-SUMMARY.md`: each direction stylesheet is one deletable file.

## Deferred items

1. **Owed first: the human A11Y-01 scripted review** (the seven-step script
   in `17A-QA.md`), deferred 2026-09-01 by Weibao's directive, to be
   performed by Weibao personally. Until it lands, this freeze carries an
   uncertified accessibility leg and any adjustment it demands is accepted
   in advance ("we will come back and adjust after").
2. Moving the shipped `theme.DEFAULT_ACCENT` from teal to indigo waits on
   that review (`17A-DIRECTION.md`, restated above).
3. `prototypes/17a/itembank-prototype.html` is a stale committed export
   (recorded by 17A-03 and again by 17A-04); regenerate it deliberately, in
   its own bounded diff, or retire it.
4. The `font` shorthand hole in `stylesheet_roundtrip.size_problems`
   (17A-03-SUMMARY.md) is still open and still unexploited.
5. Off-scale stylesheets owed by 14-UI-SPEC section 17 item 6:
   `surfaces/theme.py` SETTINGS_CSS, `surfaces/day.py`, `surfaces/study.py`
   (reported by `stylesheet_roundtrip` on every run).
6. If `bottom` navigation is ever promoted to the small-screen default, the
   course selector needs another home (`17A-DIRECTION.md`).
