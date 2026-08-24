"""The one palette, shared by every surface that renders.

`study` used to declare its own blue accent and its own ok and bad, which made
two surfaces of one tool read as two products, and left the study page with no
dark-mode accent at all because its dark block never redefined one. Anything
that renders substitutes __THEME__ rather than restating colours, so a theme
is changed in one place.

Plan 04-03 makes this module the single *derivation* source as well (D-04):
the learner persists exactly one source accent (`accent.source`), and every
mode's `--accent`/`--accent-soft` pair is computed deterministically from it
with WCAG contrast enforced (D-05, D-06). Semantic ok/bad/warn tokens stay
fixed per mode and never derive from the learner accent, so a custom colour
can never turn a verdict colour-only (D-06). Nothing derived is ever persisted.
"""
import colorsys
import html
import json
import re
import sys

from surfaces import presentation
from surfaces.settings import load_settings, write_settings


# The learner-facing persisted source accent, and the document the existing
# `THEME_CSS` constant is computed from (the additive schema default).
DEFAULT_ACCENT = "#0e6e62"
DEFAULT_THEME_CONFIG = {"theme": "system", "accent": {"source": DEFAULT_ACCENT}}

# The polished default palette (04-UI-SPEC Color table). Base tokens are the
# 60/30/10 split; `mut` is the muted-text token every existing surface already
# consumes, kept as a fixed base token. Semantic verdict tokens are fixed per
# mode, deuteranopia-safe, and independent of the custom accent.
BASE_TOKENS = {
    "light": {"bg": "#f3f5f4", "ink": "#171d1c", "card": "#ffffff",
              "chip": "#eef2f1", "line": "#dfe5e3", "mut": "#5f6d6a"},
    "dark": {"bg": "#0e1413", "ink": "#e4ebe9", "card": "#161e1d",
             "chip": "#1d2726", "line": "#26312f", "mut": "#8fa19d"},
    # OLED true-black ground: dark's per-surface offset above bg, translated
    # down so bg is #000000 (card = #161e1d - #0e1413, likewise chip and
    # line); ink and mut are reused from dark verbatim, because a darker
    # ground only raises their measured ratios.
    "oled": {"bg": "#000000", "ink": "#e4ebe9", "card": "#080a0a",
             "chip": "#0f1313", "line": "#181d1c", "mut": "#8fa19d"},
}

# `unknown`/`pending` and the three `*_bg` backgrounds close 14-UI-SPEC §3.3:
# `.planning/UI-SPEC.md` §7.1 named them as drafts "gated on a contrast_ratio
# fixture ... A failing draft is re-picked, not waived", and 06-UI-SPEC §5.5's
# unavailable-tier card already specifies a token that did not exist. `edge`
# closes §3.4: `--line` on `--card` measures 1.28:1 (light) / 1.26:1 (dark),
# so a learner identified the primary response control by a boundary that
# fails WCAG 1.4.11's 3:1 for non-text content.
#
# EVERY VALUE BELOW IS MEASURED, NOT CHOSEN. Each was run through this file's
# own `contrast_ratio` and is re-measured on every run by
# `tests/stylesheet_roundtrip.py:check_semantic_token_contrast`. Do not round,
# re-pick or "improve" a hex here; if one fails the fixture, report the
# measured ratio rather than nudging the digit.
#
# A `*_bg` token is a BACKGROUND and is never itself a text colour -- measuring
# `warn_bg` against `bg` gets 1.03 and asserts the wrong thing.
SEMANTIC_TOKENS = {
    "light": {"ok": "#1b7a3d", "ok_bg": "#e8f4ec", "bad": "#b4272b",
              "bad_bg": "#fbebeb", "warn": "#8a5900", "warn_bg": "#f8f1e2",
              "unknown": "#566067", "unknown_bg": "#edf0f2",
              "pending": "#5b4a9f", "pending_bg": "#efecf7",
              "edge": "#7f8b88"},
    "dark": {"ok": "#4fbf74", "ok_bg": "#11291b", "bad": "#f0666a",
             "bad_bg": "#2b1416", "warn": "#e0a23a", "warn_bg": "#2b2312",
             "unknown": "#9aa7ad", "unknown_bg": "#1b2325",
             "pending": "#b3a3e6", "pending_bg": "#221c33",
             "edge": "#697774"},
    # oled reuses dark's semantic set verbatim: each foreground was measured
    # against dark's bg and card, and oled's grounds are strictly darker, so
    # every ratio moves up. The proof is the fixture, not this comment:
    # stylesheet_roundtrip's check_semantic_token_contrast re-measures every
    # pairing through contrast_ratio at 4.5:1 text / 3.0:1 edge on each run.
    "oled": {"ok": "#4fbf74", "ok_bg": "#11291b", "bad": "#f0666a",
             "bad_bg": "#2b1416", "warn": "#e0a23a", "warn_bg": "#2b2312",
             "unknown": "#9aa7ad", "unknown_bg": "#1b2325",
             "pending": "#b3a3e6", "pending_bg": "#221c33",
             "edge": "#697774"},
}

# WCAG thresholds: 4.5:1 for text/control pairings, 3:1 for focus/border
# pairings. A 4.5:1 accent implies its 3:1 focus ring, but the ratios are
# still reported so the preview is honest about both requirements.
TEXT_CONTRAST = 4.5
FOCUS_CONTRAST = 3.0

# Exact CLI correction copy from plan 04-03 Task 2 (the browser settings copy
# lives in 04-UI-SPEC; this is the command-line disclosure).
ADJUST_NOTICE = ("Adjusted for readable contrast. Your source colour is "
                 "still saved.")

# Exact browser-fallback copy for the picker degradation path (04-UI-SPEC
# Copywriting contract; plan 04-03 Task 3). The same string is the stable
# `reason` in every structured unavailable result.
PICKER_FALLBACK = "System picker is unavailable here. Choose a color below instead."

# Exact browser settings copy (04-UI-SPEC Copywriting contract), distinct
# from the CLI's ADJUST_NOTICE: the learner-facing page disclosure shown
# while the derived tokens differ from the preserved source, and the
# neutral line shown when no correction is needed.
ADJUST_BROWSER_COPY = ("Adjusted for readable contrast. Your chosen color is "
                       "saved; this preview shows the accessible rendered color.")
NO_ADJUST_COPY = ("Your chosen colour already meets the readable-contrast "
                  "floor in both modes.")
RESET_CONFIRM_COPY = ("Reset accent to the app default? Your current custom "
                      "source color will be replaced.")
PICKER_OPENING_COPY = "Opening system picker\u2026"
SETTINGS_IDLE_COPY = ("Choose a colour to preview it, then Save accent to "
                      "keep it.")
SETTINGS_SAVED_COPY = "Accent saved. Other open pages change on refresh."
SETTINGS_SAVE_ERROR_COPY = "Accent not saved. Choose a color below and try again."
SETTINGS_PICK_PREVIEW_COPY = "Selection is preview-only. Save accent to keep it."

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _rgb(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def _rgb_hex(rgb):
    return "#%02x%02x%02x" % tuple(int(round(c)) for c in rgb)


def normalize_source(raw):
    """Return the normalized lowercase opaque `#RRGGBB` for `raw`, or None.

    Strict by contract (T-04-09): only six-digit hex, no alpha, no shorthand,
    no colour names. The persisted contract is exactly the normalized source;
    every write path goes through this before anything touches disk.
    """
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if not HEX_RE.match(text):
        return None
    return text.lower()


def _channel(value):
    c = value / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color):
    r, g, b = _rgb(hex_color)
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(hex_a, hex_b):
    """WCAG 2.x contrast ratio between two `#RRGGBB` colors."""
    la, lb = relative_luminance(hex_a), relative_luminance(hex_b)
    hi, lo = (la, lb) if la >= lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


def _accent_for_mode(source, mode):
    """Deterministic contrast-corrected accent for one mode.

    Preserves hue and saturation; walks bounded lightness steps from the
    source toward the contrast-increasing extreme (darker in light mode,
    lighter in dark mode) and stops at the nearest step meeting 4.5:1 on both
    the card and the page background. The extreme always passes (black on a
    light page, white on a dark page), so the scan is bounded by construction.
    """
    h, l, s = colorsys.rgb_to_hls(*[c / 255.0 for c in _rgb(source)])
    direction = -1.0 if mode == "light" else 1.0
    if all(contrast_ratio(source, BASE_TOKENS[mode][bg]) >= TEXT_CONTRAST
           for bg in ("card", "bg")):
        return source, False
    for step in range(1, 401):
        candidate_l = max(0.0, min(1.0, l + direction * step * 0.0025))
        candidate = _rgb_hex([c * 255.0 for c in
                              colorsys.hls_to_rgb(h, candidate_l, s)])
        if all(contrast_ratio(candidate, BASE_TOKENS[mode][bg]) >= TEXT_CONTRAST
               for bg in ("card", "bg")):
            return candidate, True
    extreme = _rgb_hex([c * 255.0 for c in
                        colorsys.hls_to_rgb(h, 0.0 if direction < 0 else 1.0, s)])
    return extreme, True


def _soft_for_mode(accent, mode):
    """Derive `accent-soft` toward the mode card color.

    The blend ratio closest to the accent (smallest t) where both
    accent-on-soft and ink-on-soft meet 4.5:1 wins. Bounded deterministic
    scan; t=1 (the card itself) always passes because the accent and ink both
    already meet 4.5:1 on card.
    """
    card = BASE_TOKENS[mode]["card"]
    ink = BASE_TOKENS[mode]["ink"]
    ar, ag, ab = _rgb(accent)
    cr, cg, cb = _rgb(card)
    for step in range(1, 21):
        t = step / 20.0
        soft = _rgb_hex((ar + (cr - ar) * t, ag + (cg - ag) * t,
                         ab + (cb - ab) * t))
        if (contrast_ratio(accent, soft) >= TEXT_CONTRAST and
                contrast_ratio(ink, soft) >= TEXT_CONTRAST):
            return soft
    return card


def derive_theme(source):
    """Deterministic per-mode palette for one source accent.

    Returns ``{"source": normalized, "light": {...}, "dark": {...},
    "oled": {...}, "adjusted_modes": [...]}``; each mode carries ``accent``,
    ``accent_soft``, the base tokens, and the fixed semantic token set. Any
    accessibility correction preserves the source value and is reported in
    ``adjusted_modes``; no derived value is persisted anywhere.
    """
    src = normalize_source(source)
    if src is None:
        sys.exit("settings.invalid_value: %r is not an opaque #RRGGBB color"
                 % (source,))
    derived = {"source": src, "light": {}, "dark": {}, "oled": {},
               "adjusted_modes": []}
    for mode in ("light", "dark", "oled"):
        accent, adjusted = _accent_for_mode(src, mode)
        tokens = dict(BASE_TOKENS[mode])
        tokens["accent"] = accent
        tokens["accent_soft"] = _soft_for_mode(accent, mode)
        tokens.update(SEMANTIC_TOKENS[mode])
        derived[mode] = tokens
        if adjusted:
            derived["adjusted_modes"].append(mode)
    return derived


def theme_preview(source):
    """JSON-safe preview payload: original source, rendered light/dark accent
    pairs, measured ratios, and human-readable adjustment notices. Read-only:
    never loads or writes a settings file (D-06 disclosure before save).
    """
    src = normalize_source(source)
    if src is None:
        sys.exit("settings.invalid_value: %r is not an opaque #RRGGBB color"
                 % (source,))
    derived = derive_theme(src)
    ratios = {}
    for mode in ("light", "dark"):
        d = derived[mode]
        pairs = (
            ("%s_accent_on_card" % mode, d["accent"], d["card"]),
            ("%s_accent_on_bg" % mode, d["accent"], d["bg"]),
            ("%s_accent_on_soft" % mode, d["accent"], d["accent_soft"]),
            ("%s_ink_on_soft" % mode, d["ink"], d["accent_soft"]),
            ("%s_accent_focus_on_bg" % mode, d["accent"], d["bg"]),
        )
        for label, a, b in pairs:
            ratios[label] = round(contrast_ratio(a, b), 2)
    return {
        "source": source.strip() if isinstance(source, str) else source,
        "normalized_source": src,
        "light": {"accent": derived["light"]["accent"],
                  "accent_soft": derived["light"]["accent_soft"]},
        "dark": {"accent": derived["dark"]["accent"],
                 "accent_soft": derived["dark"]["accent_soft"]},
        "ratios": ratios,
        "adjusted_modes": derived["adjusted_modes"],
        "notices": [ADJUST_NOTICE] if derived["adjusted_modes"] else [],
    }


# What actually reaches a served document. A value added to BASE_TOKENS or
# SEMANTIC_TOKENS and not named here defines nothing: `_tokens_css` emits this
# tuple and only this tuple.
_TOKEN_ORDER = ("bg", "card", "ink", "mut", "line", "accent", "accent_soft",
                "ok", "ok_bg", "bad", "bad_bg", "warn", "warn_bg",
                "unknown", "unknown_bg", "pending", "pending_bg",
                "edge", "chip")


def _tokens_css(tokens):
    return "; ".join("--%s:%s" % (name.replace("_", "-"), tokens[name])
                     for name in _TOKEN_ORDER)


def _root_block(tokens):
    return ":root{\n  %s;\n}" % _tokens_css(tokens)


def _dark_media_block(tokens):
    return ("@media (prefers-color-scheme:dark){\n  :root{\n    %s;\n  }\n}"
            % _tokens_css(tokens))


def theme_css(config):
    """The CSS custom-property block for one settings document.

    `config` holds the existing `theme` mode plus the new `accent.source`.
    `theme=system` emits the light block plus the matching dark media
    override; forced modes emit only their selected token set.
    """
    mode = config.get("theme", "system") if isinstance(config, dict) else "system"
    accent = DEFAULT_ACCENT
    if isinstance(config, dict):
        raw = config.get("accent")
        if isinstance(raw, dict):
            raw_source = raw.get("source")
            if normalize_source(raw_source) is not None:
                accent = raw_source
    derived = derive_theme(accent)
    if mode == "dark":
        return _root_block(derived["dark"])
    if mode == "oled":
        return _root_block(derived["oled"])
    light = _root_block(derived["light"])
    if mode == "light":
        return light
    return light + "\n" + _dark_media_block(derived["dark"])


# The one constant every existing surface substitutes for __THEME__; computed
# from the default settings document so a theme is changed in exactly one
# place (the derivation tables above), never by editing CSS by hand.
THEME_CSS = theme_css(DEFAULT_THEME_CONFIG)


def _print_preview(payload):
    print("source: %s" % payload["source"])
    for mode in ("light", "dark"):
        pair = payload[mode]
        print("%s: accent %s, soft %s" % (mode, pair["accent"], pair["accent_soft"]))
    print("ratios:")
    for label in sorted(payload["ratios"]):
        print("  %s: %.2f:1" % (label, payload["ratios"][label]))
    for notice in payload["notices"]:
        print("notice: %s" % notice)


def _write_source(base, source):
    """Persist exactly `accent.source` through the atomic settings writer,
    leaving every other key (known or unknown to the schema) untouched.
    """
    data = load_settings(base)
    data["accent"]["source"] = source
    write_settings(base, data)


def persist_source(base, source):
    """The public persistence helper behind both the CLI's `theme set` /
    `theme reset` and the daemon's `/api/theme` save / reset -- one
    source-only atomic writer, never a second one in a route handler.
    """
    _write_source(base, source)


# Settings-page-only styles (plan 04-04). The document shell, base
# typography/spacing, focus rings, breakpoint, and reduced-motion rules now
# come from `presentation.SHARED_CSS`; these rules cover only the theme
# form's own components and ride in the same generated style block, using
# token names -- never literals -- so no second palette owner exists.
SETTINGS_CSS = r"""
.field{margin:0 0 16px}
.field label{display:block;font-size:14px;color:var(--mut);margin:0 0 8px}
.field-row{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.source-text{font-size:14px;color:var(--mut)}
.actions{display:flex;flex-wrap:wrap;gap:12px;margin:0 0 24px}
.actions button{min-height:44px;font:inherit;font-size:16px;font-weight:600;
  padding:10px 16px;border-radius:8px;border:1px solid var(--line);
  background:var(--card);color:inherit;cursor:pointer;transition:.12s}
.actions button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.actions button[data-primary]{background:var(--accent-soft);
  border-color:var(--accent);color:var(--accent)}
.actions button:disabled{opacity:.55;cursor:default}
.previews{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:0 0 24px}
.preview-card{background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:16px}
.swatch{height:44px;border-radius:8px;border:1px solid var(--line);
  margin:0 0 8px}
.rendered{font-size:14px;color:var(--mut);margin:0 0 12px}
.samples{display:flex;flex-wrap:wrap;gap:8px}
.sample{font-size:14px;padding:4px 10px;border-radius:6px;
  border:1px solid var(--line)}
.sample.state-ok{color:var(--ok);background:var(--ok-bg);border-color:var(--ok)}
.sample.state-bad{color:var(--bad);background:var(--bad-bg);border-color:var(--bad)}
.sample.state-warn{color:var(--warn);border-color:var(--warn)}
.sample.state-selected{color:var(--accent);background:var(--accent-soft);
  border-color:var(--accent)}
.sample.state-focus{outline:2px solid var(--accent);outline-offset:2px}
details.accessibility{border:1px solid var(--line);border-radius:8px;
  padding:8px 12px;margin:0 0 24px;background:var(--card)}
details.accessibility summary{cursor:pointer;font-size:14px;font-weight:600;
  padding:4px 0}
details.accessibility summary:focus-visible{outline:2px solid var(--accent);
  outline-offset:2px}
details.accessibility p{font-size:14px;color:var(--mut)}
.ratios{margin:8px 0 0}
.ratio{display:flex;justify-content:space-between;gap:16px;
  font-size:14px;color:var(--mut);padding:4px 0;
  border-bottom:1px solid var(--line)}
.ratio:last-child{border-bottom:0}
.status{min-height:24px;font-size:14px;color:var(--mut);margin:0}
@media (max-width:767px){
  .previews{grid-template-columns:1fr}
  .actions button{width:100%}
}
"""


def _settings_preview_card(mode, pair):
    """One labelled light/dark preview card: names its mode, shows the
    rendered accent swatch and tokens separately from the preserved source,
    and carries labelled Correct/Incorrect/Warning/Selected/Focus samples so
    no meaning is carried by color alone (D-03, D-06).
    """
    label = "Light mode" if mode == "light" else "Dark mode"
    return (
        '<section class="preview-card" data-preview="%s">'
        "<h3>%s</h3>"
        '<div class="swatch" data-swatch="%s"></div>'
        '<p class="rendered">accent <span class="mono" '
        'data-rendered-accent="%s">%s</span> &middot; soft <span class="mono" '
        'data-rendered-soft="%s">%s</span></p>'
        '<div class="samples">'
        '<span class="sample state-ok">Correct</span>'
        '<span class="sample state-bad">Incorrect</span>'
        '<span class="sample state-warn">Warning</span>'
        '<span class="sample state-selected">Selected</span>'
        '<span class="sample state-focus">Focus</span>'
        "</div></section>"
        % (mode, label, mode, mode, pair["accent"], mode, pair["accent_soft"]))


def theme_page(config):
    """The `/settings` page (plan 04-04 Task 1): one quiet Theme section with
    the labeled browser color input, current source text, Choose with system
    picker / Save accent / Reset actions, side-by-side light/dark preview
    cards, an Accessibility details disclosure with measured ratios and the
    exact adjustment disclosure, a persistent polite status region, and the
    small vanilla client that previews on `input`, arms Save on `change`,
    and never mutates except through POST /api/theme.

    Every token comes from `theme_css(config)` for this settings document --
    no second palette and no literal color in the page.
    """
    src = DEFAULT_ACCENT
    if isinstance(config, dict):
        raw = config.get("accent")
        if isinstance(raw, dict) and normalize_source(raw.get("source")) is not None:
            src = normalize_source(raw["source"])
    preview = theme_preview(src)
    adjust_copy = (ADJUST_BROWSER_COPY if preview["adjusted_modes"]
                   else NO_ADJUST_COPY)
    ratio_rows = "".join(
        '<div class="ratio"><span>%s</span><span class="mono">%.2f:1</span></div>'
        % (html.escape(label.replace("_", " ")), value)
        for label, value in sorted(preview["ratios"].items()))
    cards = "".join(_settings_preview_card(mode, preview[mode])
                    for mode in ("light", "dark"))
    reset_disabled = ' disabled' if src == DEFAULT_ACCENT else ""
    body = SETTINGS_BODY.replace(
        "__SOURCE__", src).replace(
        "__ADJUST_COPY__", adjust_copy).replace(
        "__RATIO_ROWS__", ratio_rows).replace(
        "__PREVIEW_CARDS__", cards).replace(
        "__RESET_DISABLED__", reset_disabled)
    return presentation.surface_shell(
        "Settings", body,
        theme_css=theme_css(config) + "\n" + SETTINGS_CSS,
        back={"href": "/", "label": "itembank"},
        noscript=SETTINGS_NOSCRIPT)


# The settings body (plan 04-04 Task 2): one quiet Theme section plus the
# small vanilla client. The document shell, single h1, back link, generated
# theme tokens, shared design CSS, and no-script fallback all come from
# `presentation.surface_shell`.
SETTINGS_BODY = r"""<section data-section="theme" aria-labelledby="theme-heading">
<h2 id="theme-heading">Theme</h2>
<p>One accent colour is shared by every surface. The tool keeps your chosen
source colour and renders an accessible light/dark pair from it.</p>
<form id="theme-form" data-theme-form novalidate>
<div class="field">
<label for="theme-source">Accent colour</label>
<div class="field-row">
<input type="color" id="theme-source" data-settings-source value="__SOURCE__">
<span class="source-text mono" id="source-text" data-source-text>__SOURCE__</span>
</div>
</div>
<div class="actions">
<button type="button" id="pick-accent" data-action-pick>Choose with system picker</button>
<button type="button" id="save-accent" data-action-save data-primary disabled>Save accent</button>
<button type="button" id="reset-accent" data-action-reset__RESET_DISABLED__>Reset accent</button>
</div>
<div class="previews">
__PREVIEW_CARDS__
</div>
<details class="accessibility">
<summary>Accessibility details</summary>
<p id="adjust-notice" data-adjust-notice>__ADJUST_COPY__</p>
<p>Contrast ratios (WCAG):</p>
<div class="ratios" id="ratio-list" data-ratios>
__RATIO_ROWS__
</div>
</details>
<div class="status" id="theme-status" role="status" aria-live="polite" data-theme-status>Loading&hellip;</div>
</form>
</section>
<script>
(function () {
  var input = document.getElementById("theme-source");
  var sourceText = document.getElementById("source-text");
  var save = document.getElementById("save-accent");
  var reset = document.getElementById("reset-accent");
  var pick = document.getElementById("pick-accent");
  var status = document.getElementById("theme-status");
  var adjust = document.getElementById("adjust-notice");
  var ratios = document.getElementById("ratio-list");
  var swatches = {
    light: document.querySelector('[data-swatch="light"]'),
    dark: document.querySelector('[data-swatch="dark"]')
  };
  var rendered = {
    light: {accent: document.querySelector('[data-rendered-accent="light"]'),
            soft: document.querySelector('[data-rendered-soft="light"]')},
    dark: {accent: document.querySelector('[data-rendered-accent="dark"]'),
           soft: document.querySelector('[data-rendered-soft="dark"]')}
  };
  var saved = input.value;
  var dirty = false;
  var confirming = false;

  function say(text) { status.textContent = text; }

  function post(action, extra) {
    return fetch(window.location.origin + "/api/theme", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(Object.assign({action: action}, extra || {}))
    }).then(function (res) {
      return res.json().then(function (body) {
        if (!res.ok) { throw new Error(body && body.error || ("HTTP " + res.status)); }
        return body;
      });
    });
  }

  function paint(p) {
    rendered.light.accent.textContent = p.light.accent;
    rendered.light.soft.textContent = p.light.accent_soft;
    rendered.dark.accent.textContent = p.dark.accent;
    rendered.dark.soft.textContent = p.dark.accent_soft;
    swatches.light.style.background = p.light.accent;
    swatches.dark.style.background = p.dark.accent;
    adjust.textContent = p.adjusted_modes.length
      ? "Adjusted for readable contrast. Your chosen color is saved; this preview shows the accessible rendered color."
      : "Your chosen colour already meets the readable-contrast floor in both modes.";
    ratios.innerHTML = "";
    Object.keys(p.ratios).sort().forEach(function (label) {
      var row = document.createElement("div");
      row.className = "ratio";
      var name = document.createElement("span");
      name.textContent = label.replace(/_/g, " ");
      var value = document.createElement("span");
      value.className = "mono";
      value.textContent = p.ratios[label].toFixed(2) + ":1";
      row.appendChild(name);
      row.appendChild(value);
      ratios.appendChild(row);
    });
  }

  input.addEventListener("input", function () {
    if (confirming) { confirming = false; }
    post("preview", {source: input.value}).then(paint).catch(function () {
      say("Preview is temporarily unavailable. Your draft is still here.");
    });
  });

  input.addEventListener("change", function () {
    dirty = input.value !== saved;
    save.disabled = !dirty;
    if (dirty) { say("Draft changed. Save accent to keep it."); }
  });

  save.addEventListener("click", function () {
    save.disabled = true;
    say("Saving accent\u2026");
    post("save", {source: input.value}).then(function (p) {
      saved = p.source;
      sourceText.textContent = p.source;
      dirty = false;
      save.disabled = true;
      reset.disabled = (p.source === "#0e6e62");
      paint(p.preview);
      say("Accent saved. Other open pages change on refresh.");
      save.focus();
    }).catch(function () {
      save.disabled = false;
      say("Accent not saved. Choose a color below and try again.");
      save.focus();
    });
  });

  reset.addEventListener("click", function () {
    if (!confirming) {
      confirming = true;
      say("Reset accent to the app default? Your current custom source color will be replaced. Click Reset accent again to confirm.");
      reset.focus();
      return;
    }
    reset.disabled = true;
    say("Resetting accent\u2026");
    post("reset", {confirm: "RESET"}).then(function (p) {
      saved = p.source;
      input.value = p.source;
      sourceText.textContent = p.source;
      dirty = false;
      confirming = false;
      reset.disabled = true;
      paint(p.preview);
      say("Reset to the default accent.");
      reset.focus();
    }).catch(function () {
      reset.disabled = false;
      confirming = false;
      say("Reset did not complete. Your draft is still here.");
      reset.focus();
    });
  });

  pick.addEventListener("click", function () {
    pick.disabled = true;
    say("Opening system picker\u2026");
    post("pick").then(function (p) {
      if (p.available) {
        input.value = p.source;
        sourceText.textContent = p.source;
        dirty = p.source !== saved;
        save.disabled = !dirty;
        paint(p.preview);
        say("Selection is preview-only. Save accent to keep it.");
        save.focus();
      } else {
        say("System picker is unavailable here. Choose a color below instead.");
        input.focus();
      }
    }).catch(function () {
      say("System picker is unavailable here. Choose a color below instead.");
      input.focus();
    }).then(function () {
      pick.disabled = false;
    });
  });

  say("Choose a colour to preview it, then Save accent to keep it.");
})();
</script>
"""

SETTINGS_NOSCRIPT = ("The settings page needs JavaScript for live preview "
                     "and saving; the served content above remains visible "
                     "without it.")


def _load_tkinter():
    """Lazy tkinter import; returns the module object or None when Tk is
    missing or unavailable in the packaged runtime. Never called at module
    startup and never invoked from a daemon request thread -- the launcher
    child bridge keeps Tk on the picker process's main thread (T-04-12).
    """
    try:
        import tkinter
        from tkinter import colorchooser  # noqa: F401 -- loads tkinter.colorchooser
    except Exception:
        return None
    return tkinter


def pick_native_accent(initial=None):
    """Open the host OS color picker on this process's main thread.

    Returns ``{"available", "source", "reason"}``: a normalized ``#RRGGBB``
    on selection; cancel, missing Tk, headless/display errors, chooser
    exceptions, and malformed results return ``available: false`` with the
    stable browser-fallback reason and never mutate settings. The hidden root
    is withdrawn and destroyed in every path (T-04-12). Selection is
    preview-only -- persistence happens through an explicit `theme set`.
    """
    tk = _load_tkinter()
    if tk is None:
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        seeded = normalize_source(initial) if initial is not None else None
        result = tk.colorchooser.askcolor(initialcolor=seeded, parent=root)
    except Exception:
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
    if not result or not result[1]:
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    source = normalize_source(result[1])
    if source is None:
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    return {"available": True, "source": source, "reason": None}


def cmd_theme(a):
    """`itembank theme` command family: read-only preview, source-only set,
    confirmed reset, and (plan 04-03 Task 3) the native picker.
    """
    if a.action == "preview":
        _print_preview(theme_preview(a.color))
        return 0
    if a.action == "set":
        src = normalize_source(a.color)
        if src is None:
            sys.exit("settings.invalid_value: %r is not an opaque #RRGGBB color"
                     % (a.color,))
        persist_source(a.base, src)
        _print_preview(theme_preview(src))
        print("set accent.source = %r" % src)
        return 0
    if a.action == "reset":
        if a.confirm_reset != "RESET":
            sys.exit("theme reset requires --confirm-reset RESET")
        persist_source(a.base, DEFAULT_ACCENT)
        _print_preview(theme_preview(DEFAULT_ACCENT))
        print("reset accent.source = %r" % DEFAULT_ACCENT)
        return 0
    if a.action == "pick":
        result = pick_native_accent(initial=getattr(a, "initial", "") or None)
        if result["available"]:
            preview = theme_preview(result["source"])
            if getattr(a, "json", False):
                print(json.dumps({
                    "available": True,
                    "source": result["source"],
                    "preview": preview,
                    "saved": False,
                }, ensure_ascii=False, indent=2))
            else:
                _print_preview(preview)
                print("Selection is preview-only -- run `itembank theme set %s` "
                      "to save." % result["source"])
            return 0
        if getattr(a, "json", False):
            print(json.dumps({
                "available": False,
                "source": None,
                "reason": PICKER_FALLBACK,
            }, ensure_ascii=False, indent=2))
        else:
            print(PICKER_FALLBACK)
        return 0
    sys.exit("usage: itembank theme preview COLOR | set COLOR | reset "
             "--confirm-reset RESET | pick [--initial COLOR] [--json]")
