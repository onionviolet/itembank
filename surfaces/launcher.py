"""Chooses a container for the daemon's page. Never chooses a page -- the
daemon is unaware which container it got, and every existing route renders
byte-identical HTML either way (DEL-03).

No dependency is added for this: a `--app=` shell-out to a browser the
machine already has costs nothing, and the only real webview library
(`pywebview`) would be a third named exception to the stdlib-only
constraint. `subprocess.Popen` plus `webbrowser.open` do the whole job.
"""
import os
import shutil
import subprocess
import sys
import webbrowser


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
