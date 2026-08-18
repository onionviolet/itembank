---
phase: 17A-visual-system-component-foundation
plan: 05
type: execute
wave: 3
depends_on: ["17A-02"]
files_modified:
  - surfaces/theme.py
  - schemas/settings.schema.json
  - tests/stylesheet_roundtrip.py
  - tests/config_roundtrip.py
autonomous: true
requirements: ["ROADMAP backlog small-enhancements row: OLED / true-black theme mode (2026-08-10, promoted 2026-08-17)"]
must_haves:
  truths:
    - "itembank config set theme oled is a valid, schema-documented setting and every served surface renders the true-black token set under it."
    - "Every oled semantic token passes the measured 4.5:1 text and 3.0:1 edge floors through theme.contrast_ratio, never a copied number."
    - "system, light, and dark behavior is byte-identical to before; the change is additive."
  artifacts:
    - "BASE_TOKENS and SEMANTIC_TOKENS carry an oled mode; the schema theme enum carries oled; both roundtrip suites pin it."
  key_links:
    - "stylesheet_roundtrip invariant 4 iterates a hardcoded (light, dark) tuple; oled must be added there or the new tokens are never measured."
---

<objective>
Register the OLED true-black theme: one `theme` enum value `oled`, a true-black
token set derived by the discipline theme.py already implements, and the
settings surface option. Implements the ROADMAP 17A wave-3 entry "17A-05-PLAN.md,
the OLED true-black theme registration" and the backlog small-enhancements row
folded into 17A on 2026-08-17. Depends on 17A-02's frozen type and density
tokens; touches no primitives, no fonts, no layout, no new dependency.
</objective>

<context>
@surfaces/theme.py (BASE_TOKENS/SEMANTIC_TOKENS lines 35 to 69, derive_theme lines 195 to 218, theme_css lines 279 to 300)
@schemas/settings.schema.json (theme property, lines 30 to 38)
@tests/stylesheet_roundtrip.py (check_semantic_token_contrast, lines 431 to 480; SEMANTIC_TEXT_FLOOR 4.5, EDGE_FLOOR 3.0)
@tests/config_roundtrip.py (theme enum pin, lines 134 to 136)
</context>

<tasks>
<task type="auto">
  <name>Task 1: Pin the contract, then add the oled token set and mode</name>
  <files>surfaces/theme.py, tests/stylesheet_roundtrip.py, tests/config_roundtrip.py, schemas/settings.schema.json</files>
  <read_first>theme.py _accent_for_mode (line 147: mode == "light" picks direction, so any non-light mode already derives toward lighter accents) and _tokens_css/_TOKEN_ORDER (lines 259 to 267)</read_first>
  <action>1. Pins first. In tests/stylesheet_roundtrip.py line 441 change `for mode in ("light", "dark"):` to `for mode in ("light", "dark", "oled"):`. In tests/config_roundtrip.py lines 135 to 136 change the pin to `if theme["enum"] != ["system", "light", "dark", "oled"] or theme["default"] != "system":` with message `"theme property changed; it must stay system|light|dark|oled default system"`. Run both suites; each must fail only on the missing oled mode.
2. In surfaces/theme.py add to BASE_TOKENS, deriving each surface by the existing discipline (keep the dark mode's per-surface offset above bg, translated down so bg is true black; ink and mut reused from dark verbatim because a darker ground only raises their measured ratios):
```python
    "oled": {"bg": "#000000", "ink": "#e4ebe9", "card": "#080a0a",
             "chip": "#0f1313", "line": "#181d1c", "mut": "#8fa19d"},
```
(card is dark card #161e1d minus the dark bg offset #0e1413, likewise chip and line; do not re-pick these by eye.)
3. Add to SEMANTIC_TOKENS an `"oled"` entry that is a verbatim copy of the `"dark"` dict (ok #4fbf74, ok_bg #11291b, bad #f0666a, bad_bg #2b1416, warn #e0a23a, warn_bg #2b2312, unknown #9aa7ad, unknown_bg #1b2325, pending #b3a3e6, pending_bg #221c33, edge #697774). Rationale in a comment: each foreground was measured against dark's bg and card; oled's grounds are strictly darker, so every ratio moves up, and the fixture below is the proof, not this comment. Where a value needs a measured check the floor is 4.5:1 text and 3.0:1 edge and the verify command below is the authority; never hand-nudge a hex.
4. In derive_theme change the mode loop to `for mode in ("light", "dark", "oled"):` and initialize `"oled": {}` in the derived dict (accent derivation needs no new code: _accent_for_mode's `mode == "light"` test already sends oled toward lighter, the correct direction for a black ground).
5. In theme_css add, directly after the `mode == "dark"` return: `if mode == "oled":` / `return _root_block(derived["oled"])`. system, light, and dark paths are untouched; THEME_CSS (the default-config constant) is unchanged bytes.
6. Settings surface option. In schemas/settings.schema.json append `"oled"` to the theme enum (after `"dark"`, default stays `"system"`) and set the description to exactly: "The app's color theme. Read by this phase (4). The oled value is a true-black variant of dark for OLED displays." This is the same surface the existing theme setting uses: `itembank config` renders the row from the schema, so the visible option copy becomes `system|light|dark|oled`, and `itembank config set theme oled` validates through the same enum. theme_preview and the /settings accent page stay light/dark only; oled is a mode, not a second accent pipeline.</action>
  <verify>`python tests/stylesheet_roundtrip.py` exits 0 (invariant 4 now measures the oled tokens through theme.contrast_ratio against the 4.5:1 and 3.0:1 floors); `python tests/config_roundtrip.py` exits 0 (the enum and default pin, plus the existing set/preview roundtrips); `python tests/presentation_roundtrip.py` and `python tests/daemon_roundtrip.py` exit 0 proving system/light/dark surfaces unchanged. Degraded state: a settings file predating this change has no oled anywhere and renders exactly as before, which the unchanged-default pins prove.</verify>
</task>
</tasks>

<out_of_scope>Any new font, layout, density, or primitive change; an oled accent pipeline or settings-page preview card; per-mode accent persistence; automatic OLED detection; re-picking any light or dark hex; touching fixtures/, scripts/preflight.py, tests/preflight_roundtrip.py, AGENTS.md, or .gitattributes.</out_of_scope>
<summary_obligations>Record in 17A-05-SUMMARY.md: the six oled base hex values and the reused semantic set, the measured ratios stylesheet_roundtrip reported, the exact schema description string, confirmation that THEME_CSS bytes did not change, and which truths were verified by which command.</summary_obligations>
