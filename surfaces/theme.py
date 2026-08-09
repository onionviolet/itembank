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
import json
import re
import sys

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
}

SEMANTIC_TOKENS = {
    "light": {"ok": "#1b7a3d", "ok_bg": "#e8f4ec", "bad": "#b4272b",
              "bad_bg": "#fbebeb", "warn": "#8a5900"},
    "dark": {"ok": "#4fbf74", "ok_bg": "#11291b", "bad": "#f0666a",
             "bad_bg": "#2b1416", "warn": "#e0a23a"},
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
    "adjusted_modes": [...]}``; each mode carries ``accent``, ``accent_soft``,
    the base tokens, and the fixed semantic token set. Any accessibility
    correction preserves the source value and is reported in
    ``adjusted_modes``; no derived value is persisted anywhere.
    """
    src = normalize_source(source)
    if src is None:
        sys.exit("settings.invalid_value: %r is not an opaque #RRGGBB color"
                 % (source,))
    derived = {"source": src, "light": {}, "dark": {}, "adjusted_modes": []}
    for mode in ("light", "dark"):
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


_TOKEN_ORDER = ("bg", "card", "ink", "mut", "line", "accent", "accent_soft",
                "ok", "ok_bg", "bad", "bad_bg", "warn", "chip")


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
        _write_source(a.base, src)
        _print_preview(theme_preview(src))
        print("set accent.source = %r" % src)
        return 0
    if a.action == "reset":
        if a.confirm_reset != "RESET":
            sys.exit("theme reset requires --confirm-reset RESET")
        _write_source(a.base, DEFAULT_ACCENT)
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
