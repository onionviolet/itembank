#!/usr/bin/env python3
"""Original-work mutations return stable URLs without replay on reload."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import course
import evidence
import notes
import reading_desk
from a5_served_integration_roundtrip import request
from course_guidance_journey_roundtrip import fixture, served
from learner_artifacts_native_roundtrip import Forms, post

ROUTE = "course/synthetic/artifacts?bank=pending&item_ref=q1&kind=proof"
ORIGINAL = '  Original fictional text 中文 π\nKeep the final whitespace.  '
LATER = '  Later private fictional draft 中文\nStill separate.  '


def durable_bytes(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


def saved(base, note_id):
    document = notes.read_note_document(reading_desk.note_root(base),
                                        course.read_course(base)["object_id"])
    return next(row for row in document["sidecar"]["notes"] if row["note_id"] == note_id)


def responses(base):
    return [row for row in evidence.events(evidence.log_path(base))
            if row.get("event_type") == "response"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def mutation(url, markup, action, **values):
    form = Forms(markup).action(action)
    req = urllib.request.Request(urllib.parse.urljoin(url, form["url"]),
        data=urllib.parse.urlencode(dict(form["body"], **values)).encode("utf-8"))
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=10) as response:
            status, headers = response.status, response.headers
    except urllib.error.HTTPError as exc:
        status, headers = exc.code, exc.headers
        exc.close()
    assert status == 303, (action, status)
    target = headers["Location"]
    assert urllib.parse.urlsplit(target).netloc == "", target
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(target).query)
    assert query["bank"] == ["pending"] and query["item_ref"] == ["q1"]
    assert query["kind"] == ["proof"]
    return target, request(urllib.parse.urljoin(url, target))[2]


def readonly_get(url, route, root):
    before = durable_bytes(root)
    status, _, markup = request(urllib.parse.urljoin(url, route))
    assert status == 200 and durable_bytes(root) == before
    return markup


def check_native():
    with fixture() as (root, base, _banks, _info):
        with served(root) as url:
            markup = readonly_get(url, ROUTE, root)
            stable, markup = mutation(url, markup, "save", wording=ORIGINAL)
            first_note = Forms(markup).action("save")["body"]["note_id"]
            markup = readonly_get(url, stable, root)
            assert saved(base, first_note)["learner_wording"] == ORIGINAL
            assert not Forms(markup).action("save")["body"]["session_id"]
            assert not list((root / "_attempts").glob("session_*.json")) and not responses(base)
            stable, markup = mutation(url, markup, "start", confirmed="yes")
            sid = Forms(markup).action("save")["body"]["session_id"]
            assert len(list((root / "_attempts").glob("session_*.json"))) == 1
            markup = readonly_get(url, stable, root)
            assert Forms(markup).action("save")["body"]["session_id"] == sid
            stable, markup = mutation(url, markup, "save", wording=ORIGINAL)
            note_id = Forms(markup).action("save")["body"]["note_id"]
            assert note_id == first_note
            assert saved(base, note_id)["learner_wording"] == ORIGINAL and not responses(base)
            markup = readonly_get(url, stable, root)
            assert "Saved privately" in markup
            stale = Forms(markup).action("save")
            markup = post(url, markup, "preview")
            markup = post(url, markup, "cancel")
            assert "Submission cancelled" in markup and not responses(base)
            markup = post(url, markup, "preview")
            stable, markup = mutation(url, markup, "submit", confirmed="yes")
            rows = responses(base)
            assert len(rows) == 1 and rows[0]["answer"] == ORIGINAL and rows[0]["score"] is None
            assert rows[0]["session_id"] == sid and rows[0]["item_ref"] == "q1"
            assert "Pending review" in readonly_get(url, stable, root)
            stable, markup = mutation(url, markup, "save", wording=LATER)
            assert saved(base, note_id)["learner_wording"] == LATER
            before = durable_bytes(root)
            status, _, refused = request(urllib.parse.urljoin(url, stale["url"]),
                dict(stale["body"], wording="Refused competing text"))
            assert status == 400 and "Notes changed" in refused and "Refused competing text" in refused
            assert durable_bytes(root) == before
            markup = readonly_get(url, stable, root)
            assert "differs from this submitted original" in markup
        with served(root) as url:
            markup = readonly_get(url, stable, root)
            assert LATER in markup and ORIGINAL in markup and "Pending review" in markup
            assert responses(base) == rows
            form = Forms(markup).action("save")["body"]
            assert form["session_id"] == sid and form["note_id"] == note_id
            back = next(link["href"] for link in Forms(markup).links if link.get("id") == "artifact-return")
            assert urllib.parse.parse_qs(urllib.parse.urlsplit(back).query)["session"] == [sid]
            assert request(urllib.parse.urljoin(url, back))[0] == 200
    print("Original-work stable native URLs: start/save/submit, read-only reload, stale refusal and restart passed")


def check_browser(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    observations = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=os.environ.get("ITEMBANK_VISUAL_QA_CHANNEL", "chrome"), headless=True)
        try:
            for width, scripts, touch in ((1280, True, False), (390, False, False), (320, False, True)):
                with fixture() as (root, base, _banks, _info):
                    context = browser.new_context(viewport={"width": width, "height": 900},
                        java_script_enabled=scripts, has_touch=touch, color_scheme="dark" if touch else "light",
                        reduced_motion="reduce")
                    try:
                        page = context.new_page()
                        # Reload must remain a GET and never prompt to replay a form.
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

                        def reload_stable():
                            before, current_url = durable_bytes(root), page.url
                            response = page.reload(wait_until="domcontentloaded")
                            assert response.status == 200 and response.request.method == "GET"
                            assert page.url == current_url and durable_bytes(root) == before and not dialogs
                            return urllib.parse.urlsplit(page.url).path + "?" + urllib.parse.urlsplit(page.url).query

                        with served(root) as url:
                            page.goto(urllib.parse.urljoin(url, ROUTE))
                            page.get_by_role("checkbox").check()
                            click("Start this original-work activity")
                            sid = page.locator('form:has(input[value="save"]) input[name="session_id"]').get_attribute("value")
                            reload_stable()
                            assert len(list((root / "_attempts").glob("session_*.json"))) == 1
                            page.locator("#artifact-wording").fill(ORIGINAL)
                            click("Save private draft")
                            note_id = page.locator('form:has(input[value="save"]) input[name="note_id"]').get_attribute("value")
                            original = saved(base, note_id)["learner_wording"]
                            assert original.strip() == ORIGINAL.strip().replace("\n", "\r\n")
                            assert original.startswith("  ") and original.endswith("  ") and not responses(base)
                            reload_stable()
                            click("Preview saved revision for submission")
                            assert not responses(base)
                            page.get_by_role("checkbox").check()
                            click("Submit saved revision")
                            reload_stable()
                            rows = responses(base)
                            assert len(rows) == 1 and rows[0]["answer"] == original and rows[0]["score"] is None
                            assert rows[0]["session_id"] == sid and rows[0]["item_ref"] == "q1"
                            page.locator("#artifact-wording").fill(LATER)
                            click("Save private draft")
                            stable = reload_stable()
                            later = saved(base, note_id)["learner_wording"]
                            assert later.strip() == LATER.strip().replace("\n", "\r\n")
                            assert page.locator("#artifact-wording").input_value() == LATER
                            assert responses(base) == rows
                            assert page.get_by_text("Pending review", exact=True).is_visible()
                            assert page.get_by_text("The current saved draft differs from this submitted original. Review applies to the original bytes.").is_visible()
                            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                            page.screenshot(path=str(output / ("original-%s.png" % width)), full_page=True)
                        with served(root) as fresh_url:
                            before = durable_bytes(root)
                            page.goto(urllib.parse.urljoin(fresh_url, stable))
                            assert page.locator("#artifact-wording").input_value() == LATER
                            assert responses(base) == rows and durable_bytes(root) == before
                            assert page.get_by_text("Pending review", exact=True).is_visible()
                            href = page.locator("#artifact-return").get_attribute("href")
                            assert urllib.parse.parse_qs(urllib.parse.urlsplit(href).query)["session"] == [sid]
                            with page.expect_navigation(wait_until="domcontentloaded"):
                                page.locator("#artifact-return").click()
                            assert urllib.parse.parse_qs(urllib.parse.urlsplit(page.url).query)["session"] == [sid]
                        observations.append({"width": width, "scripts": scripts, "touch_emulated": touch,
                            "reloads_read_only": 4, "response_count": 1, "score": None,
                            "saved_bytes_submitted_exactly": True, "later_draft_separate": True,
                            "restart_exact_sitting": True})
                    finally:
                        context.close()
        finally:
            browser.close()
    (output / "observations.json").write_text(json.dumps(observations, indent=2) + "\n", encoding="utf-8")
    print("Chrome original-work reload/restart: 3 width/keyboard/touch/script-free journeys passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", type=Path)
    args = parser.parse_args()
    check_native()
    if args.browser:
        check_browser(args.browser)
