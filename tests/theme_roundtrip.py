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


def main():
    check_token_extractor()
    check_contrast()
    check_settings_base()
    check_picker_mocks()
    check_child_seam()
    check_render_collector()
    print("ok: theme Wave 0 harness -- token/contrast extractors, settings "
          "bases, deterministic picker mocks, source/.pyz child seam, and "
          "cross-surface render collector all self-check green against "
          "current theme/config fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
