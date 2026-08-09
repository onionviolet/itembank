#!/usr/bin/env python3
"""Wave 0 harness for Phase 4's accent/theme derivation and picker behavior
(plans 04-03 through 04-05).

Infrastructure-only, like every Wave 0 module: isolated settings bases,
CSS-token and WCAG-contrast extractors, deterministic picker mocks, the
source/`.pyz` child-process seam, and a cross-surface render collector.
Later plans add their RED assertions here before touching production code;
this module must stay green today against `surfaces/theme.py`'s current
THEME_CSS and the existing settings/config contract.

Standard library only, no test framework, runnable as
`python tests/theme_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from surfaces import settings                                # noqa: E402
from surfaces.theme import THEME_CSS                         # noqa: E402

ITEMBANK = os.path.join(ROOT, "itembank.py")
SETTINGS_ON_DISK = os.path.join(ROOT, "itembank.json")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# ---- CSS token / contrast extractors ---------------------------------------

def parse_css_tokens(css):
    """`{selector: {token: value}}` from a CSS block, keeping every `{...}`
    group and its preceding selector text (so `:root{...}` and
    `@media (prefers-color-scheme:dark){:root{...}}` stay distinct).
    """
    result = {}
    i, n = 0, len(css)
    while i < n:
        open_brace = css.find("{", i)
        if open_brace < 0:
            break
        selector = css[i:open_brace].strip()
        depth, j = 1, open_brace + 1
        while j < n and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        body = css[open_brace + 1:j - 1]
        tokens = {}
        for name, value in re.findall(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;]+);", body):
            tokens[name] = value.strip()
        result[selector] = tokens
        i = j
    return result


def _channel(value):
    c = int(value, 16) / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def contrast_ratio(hex_a, hex_b):
    """WCAG 2.x contrast ratio between two `#RRGGBB` colors (stdlib only)."""
    a = hex_a.strip().lstrip("#")
    b = hex_b.strip().lstrip("#")
    if len(a) != 6 or len(b) != 6:
        fail("contrast_ratio needs #RRGGBB inputs, got %r / %r" % (hex_a, hex_b))
    la = 0.2126 * _channel(a[0:2]) + 0.7152 * _channel(a[2:4]) + 0.0722 * _channel(a[4:6])
    lb = 0.2126 * _channel(b[0:2]) + 0.7152 * _channel(b[2:4]) + 0.0722 * _channel(b[4:6])
    hi, lo = (la, lb) if la >= lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


# ---- isolated settings bases ------------------------------------------------

def fresh_base():
    """A temp directory holding a copy of the repository's own itembank.json,
    so theme tests start from the real shipped defaults (same shape as
    `tests/config_roundtrip.py`'s fresh_base).
    """
    tmp = tempfile.mkdtemp()
    shutil.copyfile(SETTINGS_ON_DISK, os.path.join(tmp, "itembank.json"))
    return tmp


def settings_of(base):
    """`settings.load_settings(base)` -- the existing validated merge."""
    return settings.load_settings(base)


# ---- deterministic picker mocks ---------------------------------------------

class ColorChooserMock:
    """A scriptable `tkinter.colorchooser.askcolor` stand-in.

    `result` is what `askcolor` returns: `((r, g, b), "#RRGGBB")` on a pick,
    `(None, None)` on cancel. `error`, when set, is raised instead (missing
    Tk / display failure). Every call is recorded on the shared `calls` list.
    """
    def __init__(self, calls, result=((0, 110, 98), "#0e6e62"), error=None):
        self._calls = calls
        self._result = result
        self._error = error

    def askcolor(self, initialcolor=None, parent=None, **kwargs):
        self._calls.append(("askcolor", initialcolor, parent, kwargs))
        if self._error is not None:
            raise self._error
        return self._result


def patch_attribute(obj, name, value):
    """Context manager installing `value` as `obj.name`, restoring afterwards
    -- the launcher_roundtrip recorder pattern, generalized.
    """
    import contextlib
    @contextlib.contextmanager
    def _patch():
        real = getattr(obj, name)
        setattr(obj, name, value)
        try:
            yield
        finally:
            setattr(obj, name, real)
    return _patch()


def picker_result(chooser, initial="#0e6e62"):
    """The behavior-free probe: drive a chooser mock through the call shape a
    native-picker seam will use and normalize the outcome to
    `{"available": bool, "color": "#RRGGBB" or None, "cancelled": bool}`.
    """
    try:
        result = chooser.askcolor(initialcolor=initial)
    except Exception:
        return {"available": False, "color": None, "cancelled": False}
    if result and result[1]:
        return {"available": True, "color": result[1], "cancelled": False}
    return {"available": False, "color": None, "cancelled": True}


# ---- source / .pyz child-process seam ---------------------------------------

def child_argv(script, *args):
    """The argv shape the daemon will spawn for a picker child: fixed no-shell
    `[python, script, ...args]`, with no environment or shell interpolation.
    """
    return [sys.executable, script] + [str(a) for a in args]


def parse_child_result(stdout):
    """Parse one structured JSON object out of a child process's stdout, or
    return None on malformed output -- a child that prints a traceback must
    read as `available:false`, never as a crash in the daemon.
    """
    try:
        data = json.loads(stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None
    return data if isinstance(data, dict) else None


# ---- cross-surface render collection ---------------------------------------

def theme_blocks(html):
    """The parsed CSS token maps of every `<style>` block in `html`."""
    blocks = []
    for m in re.finditer(r"<style>(.*?)</style>", html, re.S):
        blocks.append(parse_css_tokens(m.group(1)))
    return blocks


def surface_has_shared_theme(html):
    """True when any `<style>` block carries the shared `--accent` token."""
    for block in theme_blocks(html):
        for tokens in block.values():
            if "--accent" in tokens:
                return True
    return False


# ---- self-checks ------------------------------------------------------------

def check_token_extractor():
    parsed = parse_css_tokens(THEME_CSS)
    if ":root" not in parsed:
        fail("token extractor did not find the :root block in THEME_CSS")
    root = parsed[":root"]
    for token in ("--bg", "--ink", "--accent", "--accent-soft", "--ok",
                  "--bad", "--warn", "--chip"):
        if token not in root:
            fail("THEME_CSS :root is missing %r" % token)
    dark = [sel for sel in parsed if "prefers-color-scheme:dark" in sel]
    if not dark:
        fail("token extractor did not separate the dark-mode media block")
    dark_tokens = parsed[dark[0]]
    if "--accent" not in dark_tokens:
        fail("dark-mode block carries no --accent token")


def check_contrast():
    if abs(contrast_ratio("#ffffff", "#000000") - 21.0) > 0.01:
        fail("contrast_ratio(#fff,#000) is not 21:1")
    if contrast_ratio("#ffffff", "#ffffff") != 1.0:
        fail("contrast_ratio of identical colors is not 1:1")
    # The current light semantic tokens must already pass text-level contrast
    # on their own backgrounds (4.5:1) -- a harness floor, not a new contract.
    parsed = parse_css_tokens(THEME_CSS)[":root"]
    for fg, bg in (("--ok", "--bg"), ("--bad", "--bg"), ("--ink", "--bg")):
        if contrast_ratio(parsed[fg], parsed[bg]) < 4.5:
            fail("%s on %s is %.2f:1, below the 4.5:1 text floor"
                 % (fg, bg, contrast_ratio(parsed[fg], parsed[bg])))
    # Determinism: the same input always yields the same ratio.
    if contrast_ratio("#0e6e62", "#f3f5f4") != contrast_ratio("#0e6e62", "#f3f5f4"):
        fail("contrast_ratio is not deterministic")


def check_settings_base():
    base = fresh_base()
    try:
        cfg = settings_of(base)
        if cfg["theme"] != "system":
            fail("fresh settings base does not read theme default 'system': %r"
                 % cfg["theme"])
        if cfg["daemon"]["port"] != 8730:
            fail("fresh settings base does not read daemon.port default: %r"
                 % cfg["daemon"]["port"])
        # An unknown top-level key must survive a write round-trip (the
        # existing settings contract config_roundtrip already guards).
        cfg["legacy_theme_key"] = "preserve-me"
        settings.write_settings(base, cfg)
        again = settings_of(base)
        if again.get("legacy_theme_key") != "preserve-me":
            fail("settings round-trip dropped an unknown key")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def check_picker_mocks():
    calls = []
    picked = picker_result(ColorChooserMock(calls, result=((0, 110, 98), "#0e6e62")))
    if picked != {"available": True, "color": "#0e6e62", "cancelled": False}:
        fail("picker pick normalized wrong: %r" % picked)
    cancelled = picker_result(ColorChooserMock(calls, result=(None, None)))
    if cancelled["available"] is not False or cancelled["cancelled"] is not True:
        fail("picker cancel normalized wrong: %r" % cancelled)
    broken = picker_result(ColorChooserMock(calls, error=RuntimeError("no display")))
    if broken != {"available": False, "color": None, "cancelled": False}:
        fail("picker failure normalized wrong: %r" % broken)
    if len(calls) != 3:
        fail("picker mock did not record every call: %r" % calls)


def check_child_seam():
    argv = child_argv("/x/itembank.pyz", "theme", "pick", "--json",
                      "--initial", "#0e6e62")
    if argv[:4] != [sys.executable, "/x/itembank.pyz", "theme", "pick"]:
        fail("child_argv built the wrong argv: %r" % argv)
    good = parse_child_result('{"available": true, "color": "#0e6e62"}\n')
    if good != {"available": True, "color": "#0e6e62"}:
        fail("parse_child_result failed on a well-formed line: %r" % good)
    if parse_child_result("Traceback (most recent call last):\nboom") is not None:
        fail("parse_child_result accepted malformed child output")


def check_render_collector():
    out = os.path.join(tempfile.mkdtemp(), "quiz.html")
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "build",
         os.path.join(ROOT, "fixtures", "sample_bank.md"), out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        fail("itembank build failed in the collector self-check: %s" % result.stdout)
    html = open(out, encoding="utf-8").read()
    if not surface_has_shared_theme(html):
        fail("built quiz page carries no shared --accent theme block")
    blocks = theme_blocks(html)
    if not blocks:
        fail("theme_blocks found no <style> block in the built quiz page")


# ---- plan 04-03 Task 1: deterministic, contrast-checked palette derivation --

def test_derive_theme_deterministic_and_normalized():
    from surfaces.theme import derive_theme
    d1 = derive_theme("#0E6E62")
    d2 = derive_theme("#0e6e62")
    if json.dumps(d1, sort_keys=True) != json.dumps(d2, sort_keys=True):
        fail("derive_theme is not byte-stable across runs or source casing")
    if d1["source"] != "#0e6e62":
        fail("derive_theme did not normalize the source to lowercase #RRGGBB: %r"
             % d1["source"])
    if d1 != derive_theme("#0e6e62"):
        fail("derive_theme is not deterministic for the same input")
    for mode in ("light", "dark"):
        for token in ("accent", "accent_soft", "bg", "ink", "card", "chip",
                      "line", "ok", "ok_bg", "bad", "bad_bg", "warn"):
            if token not in d1[mode]:
                fail("%s mode is missing token %r" % (mode, token))


def test_derived_accents_meet_contrast_and_report_correction():
    import colorsys
    from surfaces.theme import derive_theme, theme_preview
    for source in ("#0e6e62", "#ffff00", "#000000", "#ffffff", "#c00040"):
        d = derive_theme(source)
        for mode in ("light", "dark"):
            acc = d[mode]["accent"]
            for bg_name in ("card", "bg"):
                ratio = contrast_ratio(acc, d[mode][bg_name])
                if ratio < 4.5:
                    fail("accent %s on %s (%s mode) is %.2f:1, below 4.5:1"
                         % (acc, bg_name, mode, ratio))
    # An inaccessible source is corrected along the same hue/lightness family
    # while the preview retains and reports the original source (D-06).
    p = theme_preview("#ffff00")
    if p["source"] != "#ffff00":
        fail("preview did not retain the original source: %r" % p["source"])
    if not p["adjusted_modes"]:
        fail("preview of an inaccessible source reports no adjustment")
    adjusted = p["light"]["accent"]

    def _hue(hex_color):
        rgb = [int(hex_color[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
        h, _, _ = colorsys.rgb_to_hls(*rgb)
        return h

    delta = abs(_hue(p["source"]) - _hue(adjusted))
    if min(delta, 1.0 - delta) > 0.02:
        fail("corrected accent hue %.3f drifted from source hue %.3f"
             % (_hue(adjusted), _hue(p["source"])))
    if not p["notices"]:
        fail("adjusted preview carries no human-readable notice")


def test_semantic_tokens_independent_and_contrast_checked():
    from surfaces.theme import derive_theme
    a = derive_theme("#0e6e62")
    b = derive_theme("#c00040")
    for mode in ("light", "dark"):
        for tok in ("ok", "ok_bg", "bad", "bad_bg", "warn"):
            if a[mode][tok] != b[mode][tok]:
                fail("semantic token %s/%s differs across unrelated accents"
                     % (mode, tok))
        for fg, bg in (("ok", "ok_bg"), ("bad", "bad_bg"),
                       ("warn", "bg"), ("warn", "card")):
            if contrast_ratio(a[mode][fg], a[mode][bg]) < 4.5:
                fail("%s on %s (%s mode) is below the 4.5:1 floor"
                     % (fg, bg, mode))
        verdicts = (a[mode]["ok"], a[mode]["bad"], a[mode]["warn"],
                    a[mode]["accent"])
        if len(set(verdicts)) != len(verdicts):
            fail("semantic verdict tokens are not pairwise distinct from the "
                 "accent in %s mode" % mode)


def test_theme_css_modes():
    from surfaces.theme import theme_css
    sys_css = theme_css({"theme": "system", "accent": {"source": "#0e6e62"}})
    light_css = theme_css({"theme": "light", "accent": {"source": "#0e6e62"}})
    dark_css = theme_css({"theme": "dark", "accent": {"source": "#0e6e62"}})
    parsed_sys = parse_css_tokens(sys_css)
    if ":root" not in parsed_sys:
        fail("system CSS has no :root block")
    dark_blocks = [sel for sel in parsed_sys if "prefers-color-scheme:dark" in sel]
    if len(dark_blocks) != 1:
        fail("system CSS must emit exactly one prefers-color-scheme:dark branch")
    parsed_light = parse_css_tokens(light_css)
    if len(parsed_light) != 1 or ":root" not in parsed_light:
        fail("light CSS must emit only the :root token set")
    parsed_dark = parse_css_tokens(dark_css)
    if len(parsed_dark) != 1 or ":root" not in parsed_dark:
        fail("dark CSS must emit only the :root token set")
    if parsed_dark[":root"] != parsed_sys[dark_blocks[0]]:
        fail("forced dark tokens differ from the system dark branch")
    if parsed_light[":root"]["--accent"] != parsed_sys[":root"]["--accent"]:
        fail("forced light accent differs from the system light branch")


def test_palette_matches_binding_values():
    from surfaces.theme import derive_theme
    d = derive_theme("#0e6e62")
    light_base = {"bg": "#f3f5f4", "ink": "#171d1c", "card": "#ffffff",
                  "chip": "#eef2f1", "line": "#dfe5e3"}
    dark_base = {"bg": "#0e1413", "ink": "#e4ebe9", "card": "#161e1d",
                 "chip": "#1d2726", "line": "#26312f"}
    light_sem = {"ok": "#1b7a3d", "ok_bg": "#e8f4ec", "bad": "#b4272b",
                 "bad_bg": "#fbebeb", "warn": "#8a5900"}
    dark_sem = {"ok": "#4fbf74", "ok_bg": "#11291b", "bad": "#f0666a",
                "bad_bg": "#2b1416", "warn": "#e0a23a"}
    for name, expected in (("light", light_base), ("dark", dark_base)):
        for token, value in expected.items():
            if d[name][token] != value:
                fail("%s base token %s = %r, expected %r"
                     % (name, token, d[name][token], value))
    for name, expected in (("light", light_sem), ("dark", dark_sem)):
        for token, value in expected.items():
            if d[name][token] != value:
                fail("%s semantic token %s = %r, expected %r"
                     % (name, token, d[name][token], value))


def test_theme_preview_cli_readonly():
    base = tempfile.mkdtemp()
    try:
        r = subprocess.run(
            [sys.executable, ITEMBANK, "theme", "preview", "#0e6e62",
             "--base", base],
            capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            fail("itembank theme preview exited %d: %s"
                 % (r.returncode, r.stdout + r.stderr))
        low = r.stdout.lower()
        for needle in ("source", "light", "dark", "accent", "soft", "ratio"):
            if needle not in low:
                fail("preview output is missing %r: %r" % (needle, r.stdout))
        if os.path.exists(os.path.join(base, "itembank.json")):
            fail("itembank theme preview wrote a settings file")
        adjusted = subprocess.run(
            [sys.executable, ITEMBANK, "theme", "preview", "#ffff00",
             "--base", base],
            capture_output=True, text=True, encoding="utf-8")
        if adjusted.returncode != 0:
            fail("adjusted preview exited %d: %s"
                 % (adjusted.returncode, adjusted.stdout + adjusted.stderr))
        if "Adjusted for readable contrast" not in adjusted.stdout:
            fail("adjusted preview output carries no correction notice")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    check_token_extractor()
    check_contrast()
    check_settings_base()
    check_picker_mocks()
    check_child_seam()
    check_render_collector()
    test_derive_theme_deterministic_and_normalized()
    test_derived_accents_meet_contrast_and_report_correction()
    test_semantic_tokens_independent_and_contrast_checked()
    test_theme_css_modes()
    test_palette_matches_binding_values()
    test_theme_preview_cli_readonly()
    print("ok: theme Wave 0 harness -- token/contrast extractors, settings "
          "bases, deterministic picker mocks, source/.pyz child seam, and "
          "cross-surface render collector all self-check green against "
          "current theme/config fixtures; plan 04-03 derivation, contrast, "
          "semantic-independence, mode-CSS and read-only preview assertions "
          "pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
