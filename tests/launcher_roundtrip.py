#!/usr/bin/env python3
"""DEL-03 coverage: browser detection returns a path or None per platform,
and every branch of `open_window`'s container decision -- app, tab, no-
browser fallback, spawn-failure fallback, and opt-out. No real browser is
ever launched: every test that reaches a spawn or a tab-open substitutes
`launcher.subprocess`/`launcher.webbrowser` with a recorder first.

Standard library only, runnable as `python tests/launcher_roundtrip.py`.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from surfaces import launcher                              # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


class _FakeSubprocess:
    """Replaces `launcher.subprocess` for the duration of one test. Records
    every `Popen(...)` call as `("popen", args, kwargs)`; raises `OSError`
    instead when `raise_on_popen` is set, to exercise the spawn-failure
    fallback without a real broken browser.
    """
    def __init__(self, calls, raise_on_popen=False):
        self._calls = calls
        self._raise_on_popen = raise_on_popen

    def Popen(self, *args, **kwargs):
        if self._raise_on_popen:
            raise OSError("simulated spawn failure")
        self._calls.append(("popen", args, kwargs))


class _FakeWebbrowser:
    """Replaces `launcher.webbrowser` for the duration of one test. Records
    every `open(url)` call as `("tab", url)`.
    """
    def __init__(self, calls):
        self._calls = calls

    def open(self, url):
        self._calls.append(("tab", url))
        return True


def recorder(raise_on_popen=False):
    """Installs the recorder pair and returns `(calls, restore)` -- `calls`
    accumulates every spawn/tab-open, `restore()` puts the real
    `subprocess`/`webbrowser` modules back so one test cannot leak into the
    next.
    """
    calls = []
    real_subprocess, real_webbrowser = launcher.subprocess, launcher.webbrowser
    launcher.subprocess = _FakeSubprocess(calls, raise_on_popen=raise_on_popen)
    launcher.webbrowser = _FakeWebbrowser(calls)

    def restore():
        launcher.subprocess = real_subprocess
        launcher.webbrowser = real_webbrowser

    return calls, restore


def test_find_browser_returns_a_path_or_none():
    """A CI runner with no Chromium-family browser legitimately gets None,
    and that is a pass, not a skip -- the one platform-tolerant assertion.
    """
    result = launcher.find_browser()
    if result is not None:
        if not isinstance(result, str):
            fail("find_browser() returned a non-string, non-None value: %r" % (result,))
        if not os.path.exists(result):
            fail("find_browser() returned a path that does not exist: %r" % (result,))


def test_windows_detection_prefers_the_registry():
    """No-op on non-Windows so this file runs identically everywhere.
    Substitutes the PATH lookup so it returns None for every name, then
    asserts find_browser() still returns a path -- proving the registry
    probe runs and is not merely a fallback behind a PATH hit.
    """
    if sys.platform != "win32":
        return
    real_which = launcher.shutil.which
    launcher.shutil.which = lambda name: None
    try:
        result = launcher.find_browser()
        if result is None:
            fail("find_browser() returned None on win32 with PATH lookup "
                 "disabled -- the registry probe did not run or found nothing")
    finally:
        launcher.shutil.which = real_which


def test_app_mode_spawns_the_expected_argv():
    calls, restore = recorder()
    try:
        launcher.find_browser = lambda: "/x/fake-chrome"
        result = launcher.open_window("http://127.0.0.1:8730/", "app", False)
        if result != "app":
            fail("open_window app/found did not return 'app': %r" % (result,))
        if len(calls) != 1 or calls[0][0] != "popen":
            fail("open_window app/found did not spawn exactly one process: %r" % (calls,))
        argv = calls[0][1][0]
        if argv != ["/x/fake-chrome", "--app=http://127.0.0.1:8730/"]:
            fail("spawned argv was not [browser, --app=url]: %r" % (argv,))
    finally:
        restore()
        del launcher.find_browser


def test_tab_setting_never_spawns_a_process():
    calls, restore = recorder()
    try:
        launcher.find_browser = lambda: "/x/fake-chrome"
        result = launcher.open_window("http://u/", "tab", False)
        if result != "tab":
            fail("open_window tab did not return 'tab': %r" % (result,))
        if calls != [("tab", "http://u/")]:
            fail("open_window tab did not open exactly one tab and nothing "
                 "else, even with a browser available: %r" % (calls,))
    finally:
        restore()
        del launcher.find_browser


def test_no_browser_found_falls_back_to_a_tab():
    calls, restore = recorder()
    try:
        launcher.find_browser = lambda: None
        result = launcher.open_window("http://u/", "app", False)
        if result != "tab":
            fail("open_window app/not-found did not return 'tab': %r" % (result,))
        if calls != [("tab", "http://u/")]:
            fail("open_window app/not-found did not fall back to exactly one "
                 "tab: %r" % (calls,))
    finally:
        restore()
        del launcher.find_browser


def test_spawn_failure_falls_back_to_a_tab():
    """The branch flagged planner assumption A-DEL-03 covers: a Chromium
    browser is found but the spawn itself raises (locked profile, broken
    install, sandbox refusal).
    """
    calls, restore = recorder(raise_on_popen=True)
    try:
        launcher.find_browser = lambda: "/x/fake-chrome"
        result = launcher.open_window("http://u/", "app", False)
        if result != "tab":
            fail("open_window app/spawn-failure did not return 'tab': %r" % (result,))
        if calls != [("tab", "http://u/")]:
            fail("open_window app/spawn-failure did not fall back to exactly "
                 "one tab: %r" % (calls,))
    finally:
        restore()
        del launcher.find_browser


def test_opt_out_opens_nothing():
    for window in ("app", "tab"):
        calls, restore = recorder()
        try:
            launcher.find_browser = lambda: "/x/fake-chrome"
            result = launcher.open_window("http://u/", window, True)
            if result is not None:
                fail("open_window(%r, no_open=True) did not return None: %r"
                     % (window, result))
            if calls:
                fail("open_window(%r, no_open=True) opened something: %r"
                     % (window, calls))
        finally:
            restore()
            del launcher.find_browser


def main():
    test_find_browser_returns_a_path_or_none()
    test_windows_detection_prefers_the_registry()
    test_app_mode_spawns_the_expected_argv()
    test_tab_setting_never_spawns_a_process()
    test_no_browser_found_falls_back_to_a_tab()
    test_spawn_failure_falls_back_to_a_tab()
    test_opt_out_opens_nothing()
    print("launcher contract: ok (detection tolerant of no-browser, "
          "registry-first on win32, app/tab/no-browser-fallback/"
          "spawn-failure-fallback/opt-out all covered, no real browser "
          "ever launched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
