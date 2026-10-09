#!/usr/bin/env python3
"""Opt-in installed-Chrome native restore and script-free recovery journey."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
from daemon_roundtrip import start_daemon
from restore_workspace_roundtrip import NativeRestore, files, request


@contextmanager
def fixture():
    case = NativeRestore("test_preview_changes_nothing_and_names_exact_private_scope")
    case.setUp()
    process = None
    try:
        process, url, _lines = start_daemon(str(case.root))
        yield case, url
    finally:
        if process:
            process.terminate()
            process.wait(timeout=10)
            process.stdout.close()
        case.doCleanups()


def check_static():
    with fixture() as (case, url):
        before = files(case.source)
        status, html = request(url + "restore", dict(case.selection, operation="preview"))
        assert status == 200 and 'name="confirm_private"' in html
        assert "private.txt" in html and "Package losses" in html
        assert files(case.source) == before and not case.dest.exists()


def check_browser(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    receipt = []
    paths = ("surfaces/course_ops.py", "surfaces/restore_workspace.py", "surfaces/daemon.py",
             "surfaces/ia.py", "course_package.py", "workspace.py", "journal.py", "evidence.py")
    source_fingerprints = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}
    with fixture() as (case, url), sync_playwright() as pw:
        before = files(case.source)
        browser = pw.chromium.launch(channel=os.environ.get("ITEMBANK_VISUAL_QA_CHANNEL", "chrome"), headless=True)
        try:
            for width, scripts in ((1280, True), (390, True), (320, False)):
                context = browser.new_context(viewport={"width": width, "height": 900},
                    java_script_enabled=scripts, reduced_motion="reduce",
                    color_scheme="dark" if width == 390 else "light")
                page = context.new_page()
                page.goto(url + "restore")
                page.locator('[name="package_id"]').select_option(case.manifest["package_id"])
                page.locator('[name="source_choice"]').select_option("root:1")
                page.locator('[name="destination_root"]').select_option("0")
                leaf = "browser-%d" % width
                page.locator('[name="destination_name"]').fill(leaf)
                page.get_by_role("button", name="Preview exact restore scope").focus()
                page.keyboard.press("Enter")
                page.get_by_role("button", name="Create validated copy").wait_for()
                assert "private.txt" in page.locator(".restore-workspace").inner_text()
                assert page.locator('[name="confirm_private"]').is_checked() is False
                if scripts:
                    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
                page.screenshot(path=str(output / ("preview-%d.png" % width)), full_page=True)
                for name in ("confirm_copy", "confirm_private"):
                    page.locator('[name="%s"]' % name).focus()
                    page.keyboard.press("Space")
                page.get_by_role("button", name="Create validated copy").focus()
                page.keyboard.press("Enter")
                page.get_by_role("button", name="Open this exact recovered course snapshot").wait_for()
                assert files(case.source) == before
                destination = case.root / "_packages" / "_restore" / leaf
                assert (destination / "private.txt").read_bytes() == b"Fictional private draft\n"
                page.get_by_role("button", name="Open this exact recovered course snapshot").focus()
                page.keyboard.press("Enter")
                page.get_by_text("Opened the validated recovery copy.", exact=True).wait_for()
                assert page.get_by_role("heading", name="Objectives", exact=True).is_visible()
                if scripts:
                    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
                page.screenshot(path=str(output / ("reopened-%d.png" % width)), full_page=True)
                receipt.append({"width": width, "scripts": scripts, "keyboard": "preview/consent/copy/reopen",
                                "source_preserved": True, "destination_private_file": True})
                context.close()
        finally:
            browser.close()
    assert source_fingerprints == {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}, "Source changed during browser gate"
    (output / "receipt.json").write_text(json.dumps({"checks": receipt,
        "source_fingerprints": source_fingerprints}, indent=2) + "\n", encoding="utf-8")
    print("Installed Chrome: keyboard restore/reopen at 1280/390/320, including script-free 320, passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-shots", type=Path)
    args = parser.parse_args()
    check_static()
    if args.browser_shots:
        check_browser(args.browser_shots)
    print("Native restore static route passed")
