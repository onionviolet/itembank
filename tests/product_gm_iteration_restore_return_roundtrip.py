#!/usr/bin/env python3
"""Completed restore URLs survive reload/restart and preserve exact admission."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import identity
import journal
import workspace
from surfaces import ia
from course_guidance_journey_roundtrip import served
from restore_workspace_roundtrip import NativeRestore, Forms, files, request


@contextmanager
def fixture():
    case = NativeRestore("test_preview_changes_nothing_and_names_exact_private_scope")
    case.setUp()
    try:
        yield case
    finally:
        case.doCleanups()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def publish(url, fields):
    req = urllib.request.Request(url + "restore", data=urllib.parse.urlencode(fields).encode())
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=10) as response:
            status, headers = response.status, response.headers
    except urllib.error.HTTPError as exc:
        status, headers = exc.code, exc.headers
        exc.close()
    assert status == 303, status
    href = headers["Location"]
    assert urllib.parse.urlsplit(href).path == "/restore" and not urllib.parse.urlsplit(href).netloc
    return href


def reopen_form(markup):
    return next(form["fields"] for form in Forms(markup).forms if form["action"] == "/restore/open")


def readonly(url, href, case):
    before = files(case.root)
    status, markup = request(urllib.parse.urljoin(url, href))
    assert status == 200 and "Validated recovery copy" in markup
    assert "Open this exact recovered course snapshot" in markup
    assert "Open this exact ordinary course folder in a separate local process" in markup
    assert files(case.root) == before
    return markup


def check_native():
    with fixture() as case:
        source = files(case.source)
        shelf = ia.course_shelf_state(str(case.root))["cards"]
        with served(case.root) as url:
            status, markup = request(url + "restore", dict(case.selection, operation="preview"))
            assert status == 200 and "private.txt" in markup and not case.dest.exists()
            form = next(row["fields"] for row in Forms(markup).forms if row["fields"].get("operation") == "restore")
            stable = publish(url, dict(form, confirm_copy="yes", confirm_private="yes"))
            assert files(case.source) == source
            assert ia.course_shelf_state(str(case.root))["cards"] == shelf
            assert (case.dest / "private.txt").read_bytes() == b"Fictional private draft\n"
            markup = readonly(url, stable, case)
            selector = reopen_form(markup)
            assert urllib.parse.parse_qs(urllib.parse.urlsplit(stable).query) == {key: [value] for key, value in selector.items()}
            copied = files(case.dest)
            before = files(case.root)
            status, _ = request(urllib.parse.urljoin(url, stable), headers={"Origin": "https://untrusted.invalid"})
            assert status == 403 and files(case.root) == before
            for changes in ({"destination_root": "99"}, {"destination_name": "../escape"},
                            {"destination_inode": "0"}, {"course_fingerprint": "stale"},
                            {"unexpected": "value"}, {"destination_root": ["0", "0"]}):
                bad = dict(selector, **changes)
                bad_href = "restore?" + urllib.parse.urlencode(bad, doseq=True)
                assert request(urllib.parse.urljoin(url, bad_href))[0] == 400
                assert files(case.root) == before
        with served(case.root) as fresh:
            markup = readonly(fresh, stable, case)
            status, reopened = request(fresh + "restore/open", reopen_form(markup))
            assert status == 200 and "Opened the validated recovery copy" in reopened and "Objectives" in reopened
            assert files(case.dest) == copied and files(case.source) == source
            # The ready URL reuses the existing accepted-object conflict gate.
            (case.dest / "other.md").write_text("# Synthetic changed accepted lesson\n", encoding="utf-8")
            changed = files(case.root)
            assert request(urllib.parse.urljoin(fresh, stable))[0] == 400
            assert files(case.root) == changed
    print("Stable restore URL: 303 copy, read-only reload/restart, exact reopen and origin/scope/stale refusals passed")


def check_reference_boundary():
    with fixture() as case:
        document = {"schema_version": 1, "workspace_object_id": identity.new_object_id(),
                    "roots": [str(case.source)], "courses": []}
        journal.commit_operation(str(case.source), document["workspace_object_id"], "workspace",
            workspace.WORKSPACE_REL_PATH, "mint", workspace._serialize(document), None, "human", "test",
            create_if_missing=True, rights={right: "granted" for right in identity.RIGHTS_OPERATIONS})
        source = files(case.source)
        with served(case.root) as url:
            status, markup = request(url + "restore", dict(case.selection, operation="preview"))
            assert status == 200 and "Workspace reference proposal" in markup
            form = next(row["fields"] for row in Forms(markup).forms if row["fields"].get("operation") == "restore")
            stable = publish(url, dict(form, confirm_copy="yes", confirm_private="yes"))
            before = files(case.root)
            status, markup = request(urllib.parse.urljoin(url, stable))
            assert status == 200 and "Review its approved-root references" in markup
            assert "itembank daemon" not in markup and files(case.root) == before
            status, opened = request(url + "restore/open", reopen_form(markup))
            assert status == 200 and "Opened the validated recovery copy" in opened
            assert workspace.read_workspace(str(case.dest))["doc"]["roots"] == document["roots"]
            assert files(case.source) == source and files(case.root) == before
    print("Copied workspace ready URL preserves root-review limits and applies no reference proposal")


def check_browser(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=os.environ.get("ITEMBANK_VISUAL_QA_CHANNEL", "chrome"), headless=True)
        try:
            for width, scripts, touch in ((1280, True, False), (390, True, False), (320, False, True)):
                with fixture() as case:
                    source = files(case.source)
                    shelf = ia.course_shelf_state(str(case.root))["cards"]
                    context = browser.new_context(viewport={"width": width, "height": 900},
                        java_script_enabled=scripts, has_touch=touch, color_scheme="dark" if width == 390 else "light",
                        reduced_motion="reduce")
                    try:
                        page = context.new_page()
                        dialogs = []
                        page.on("dialog", lambda dialog: (dialogs.append(dialog.type), dialog.dismiss()))

                        def click(name):
                            with page.expect_navigation(wait_until="domcontentloaded"):
                                button = page.get_by_role("button", name=name, exact=True)
                                if touch:
                                    button.tap()
                                else:
                                    button.focus()
                                    page.keyboard.press("Enter")

                        with served(case.root) as url:
                            page.goto(url + "restore")
                            page.locator('[name="package_id"]').select_option(case.manifest["package_id"])
                            page.locator('[name="source_choice"]').select_option("root:1")
                            page.locator('[name="destination_root"]').select_option("0")
                            page.locator('[name="destination_name"]').fill(case.selection["destination_name"])
                            click("Preview exact restore scope")
                            assert "private.txt" in page.locator(".restore-workspace").inner_text()
                            assert not page.locator('[name="confirm_private"]').is_checked()
                            assert not case.dest.exists() and files(case.source) == source
                            for name in ("confirm_copy", "confirm_private"):
                                checkbox = page.locator('[name="%s"]' % name)
                                if touch:
                                    checkbox.check()
                                else:
                                    checkbox.focus(); page.keyboard.press("Space")
                            click("Create validated copy")
                            assert page.get_by_role("heading", name="Validated recovery copy", exact=True).is_visible()
                            assert files(case.source) == source
                            copied = files(case.dest)
                            assert ia.course_shelf_state(str(case.root))["cards"] == shelf
                            assert copied["private.txt"] == b"Fictional private draft\n"
                            stable = urllib.parse.urlsplit(page.url).path + "?" + urllib.parse.urlsplit(page.url).query
                            before = files(case.root)
                            response = page.reload(wait_until="domcontentloaded")
                            assert response.status == 200 and response.request.method == "GET" and not dialogs
                            assert page.get_by_role("button", name="Open this exact recovered course snapshot").is_visible()
                            assert files(case.root) == before
                            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                            page.screenshot(path=str(output / ("ready-%s.png" % width)), full_page=True)
                            click("Open this exact recovered course snapshot")
                            assert page.get_by_text("Opened the validated recovery copy.", exact=True).is_visible()
                            assert page.get_by_role("heading", name="Objectives", exact=True).is_visible()
                            assert files(case.root) == before
                        with served(case.root) as fresh:
                            before = files(case.root)
                            page.goto(urllib.parse.urljoin(fresh, stable))
                            assert page.get_by_role("button", name="Open this exact recovered course snapshot").is_visible()
                            assert files(case.root) == before
                            click("Open this exact recovered course snapshot")
                            assert page.get_by_role("heading", name="Objectives", exact=True).is_visible()
                            assert files(case.root) == before and files(case.dest) == copied
                            assert files(case.source) == source
                            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                        rows.append({"width": width, "scripts": scripts, "touch_emulated": touch,
                            "copy_reload_get": True, "restart_reopen_exact": True,
                            "source_preserved": True, "copy_preserved": True,
                            "duplicate_course_enrollment": False, "horizontal_overflow": False})
                    finally:
                        context.close()
        finally:
            browser.close()
    (output / "observations.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print("Chrome stable restore: 3 width/keyboard/touch/script-free reload and fresh-daemon reopen flows passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", type=Path)
    args = parser.parse_args()
    check_native()
    check_reference_boundary()
    if args.browser:
        check_browser(args.browser)
