"""Chooses a container for the daemon's page. Never chooses a page -- the
daemon is unaware which container it got, and every existing route renders
byte-identical HTML either way (DEL-03).

No dependency is added for this: a `--app=` shell-out to a browser the
machine already has costs nothing, and the only real webview library
(`pywebview`) would be a third named exception to the stdlib-only
constraint. `subprocess.Popen` plus `webbrowser.open` do the whole job.
"""
import json
import os
import shutil
import subprocess
import sys
import webbrowser

import resources
from surfaces.theme import PICKER_FALLBACK, normalize_source


# Captured from the real module at import time: the patched-seam tests replace
# `launcher.subprocess` wholesale, so the failure modes must not be read off
# the (possibly fake) module attribute at call time.
_SUBPROCESS_ERRORS = (OSError, subprocess.SubprocessError)


# POSIX binary-name preference order for the `else` branch of find_browser
# (covers Linux and any other non-Windows, non-macOS platform).
CHROME_NAMES = ("google-chrome-stable", "google-chrome", "chromium",
                "chromium-browser", "microsoft-edge")

# Registry subkey preference order under
# SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths -- Chrome first, then
# Edge. Ordering is not optional: a live registry query this session found
# both browsers where a PATH lookup for the same two names found neither, on
# a Windows 11 machine with both installed at their standard locations.
WINDOWS_APP_PATHS = ("chrome.exe", "msedge.exe")

# Fixed executable path preference order inside /Applications -- Chrome,
# then Edge, then Chromium.
MAC_BROWSERS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


def find_browser():
    """Return a path to a Chromium-family browser executable, or None if
    none is found -- a normal outcome, not an error. Branches on
    `sys.platform` the same three-way `surfaces/day.py:_anki_addon_port`
    already does, rather than inventing a second platform-detection shape.
    """
    if sys.platform == "win32":
        import winreg
        for name in WINDOWS_APP_PATHS:
            for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    key = winreg.OpenKey(
                        hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\%s" % name)
                    return winreg.QueryValue(key, None)
                except OSError:
                    continue
        for name in WINDOWS_APP_PATHS:
            found = shutil.which(name)
            if found:
                return found
        return None

    if sys.platform == "darwin":
        for path in MAC_BROWSERS:
            if os.path.exists(path):
                return path
        try:
            result = subprocess.run(
                ["mdfind", "kMDItemCFBundleIdentifier == 'com.google.Chrome'"],
                capture_output=True, text=True, timeout=2)
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    return os.path.join(line, "Contents/MacOS/Google Chrome")
        except (OSError, subprocess.TimeoutExpired):
            pass
        return None

    for name in CHROME_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def open_window(url, window="app", no_open=False):
    """The one decision point: choose a container for `url` and open it,
    returning what happened (`"app"`, `"tab"`, or `None`) so a caller -- or a
    test -- can observe the branch taken without a real window appearing.

    `no_open` wins over everything and opens nothing. `window == "tab"`
    always opens an ordinary tab, no detection run. Otherwise an app-mode
    browser is detected and spawned; any failure to find or spawn one falls
    through to an ordinary tab, so a browser problem never stops the caller.
    """
    if no_open:
        return None
    if window == "tab":
        webbrowser.open(url)
        return "tab"
    browser = find_browser()
    if browser:
        try:
            subprocess.Popen([browser, "--app=" + url])
            return "app"
        except OSError:
            pass
    webbrowser.open(url)
    return "tab"


def _child_entry():
    """The current entry point for a child `theme pick` invocation: the
    running `.pyz` when bundled, otherwise the source `itembank.py` (resolved
    from `sys.argv[0]` when this is the CLI, or the repository root as the
    fallback)."""
    archive = resources.archive_path()
    if archive is not None:
        return archive
    script = os.path.abspath(sys.argv[0])
    if os.path.basename(script).lower() in ("itembank.py", "itembank"):
        return script
    return os.path.join(resources.ROOT, "itembank.py")


def run_native_picker(source):
    """Launch the current source/`.pyz`'s `theme pick --json --initial SOURCE`
    as a fixed no-shell child, so Tk stays on the picker process's main thread
    and never enters the daemon's HTTP handler (T-04-12).

    Returns the same ``{"available", "source", "reason"}`` contract as
    `surfaces.theme.pick_native_accent` and fails closed on spawn failure,
    non-zero exit, oversize output, or malformed/non-available JSON.
    """
    argv = [sys.executable, _child_entry(), "theme", "pick",
            "--json", "--initial", source]
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    except _SUBPROCESS_ERRORS:
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    if result.returncode != 0:
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    if len(result.stdout) > 4096:
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    try:
        data = json.loads(result.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    if not isinstance(data, dict) or data.get("available") is not True:
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    child_source = data.get("source")
    if normalize_source(child_source) is None:
        return {"available": False, "source": None, "reason": PICKER_FALLBACK}
    return {"available": True, "source": child_source, "reason": None}
