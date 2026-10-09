#!/usr/bin/env python3
"""Admitted native artifact forms, actual runtime review and offline restart."""
import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import sys
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import course
import evidence
import notes
import reading_desk
from surfaces import session
from a5_served_integration_roundtrip import request
from course_guidance_journey_roundtrip import fixture, served
from daemon_roundtrip import json_request


class Forms(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.forms, self.links = [], []
        self.current = None
        self.feed(markup)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == "form":
            self.current = {"url": attrs["action"], "body": {}}
            self.forms.append(self.current)
        if tag == "input" and self.current and attrs.get("type") == "hidden":
            self.current["body"][attrs["name"]] = attrs.get("value", "")
        if tag == "a":
            self.links.append(attrs)

    def handle_endtag(self, tag):
        if tag == "form":
            self.current = None

    def action(self, action):
        return next(f for f in self.forms if f["body"].get("action") == action)


def start(base, root, suffix):
    path = root / "_attempts" / ("session_artifact_" + suffix + ".json")
    begun = session.do_start(str(base / "pending.md"), {"count": 1, "seed": 0}, "practice", str(path), False)
    return path, begun["session_id"]


def post(url, page, action, **values):
    form = Forms(page).action(action)
    body = dict(form["body"], **values)
    status, _, page = request(urllib.parse.urljoin(url, form["url"]), body)
    assert status == 200, (status, page[:500])
    return page


def check_native():
    with fixture() as (root, base, banks, info):
        route = "/course/synthetic/artifacts?" + urllib.parse.urlencode({"bank": "pending", "item_ref": "q1", "kind": "proof"})
        original = "  Original fictional proof π\nEquality preserves the selected fictional rule.\n  "
        with served(root) as url:
            assert request(url + "course/synthetic/artifacts")[0] == 200
            status, _, page = request(urllib.parse.urljoin(url, route))
            assert status == 200, page[:500]
            assert not list((root / "_attempts").glob("session_*.json"))
            page = post(url, page, "start", confirmed="yes")
            sid = Forms(page).action("save")["body"]["session_id"]
            assert sid
            before = list(evidence.events(evidence.log_path(base)))
            assert not any(e.get("event_type") == "response" for e in before)
            page = post(url, page, "save", wording=original)
            assert "Saved privately" in page and "Submit saved revision" not in page
            assert list(evidence.events(evidence.log_path(base))) == before
            stale = Forms(page).action("save")
            page = post(url, page, "preview")
            assert "Submit this saved revision" in page
            page = post(url, page, "cancel")
            assert "Submission cancelled" in page
            page = post(url, page, "preview")
            page = post(url, page, "submit", confirmed="yes")
            assert "Submitted original" in page and "Pending review" in page
            row = next(e for e in evidence.events(evidence.log_path(base)) if e.get("event_type") == "response")
            assert row["answer"] == original and row["score"] is None
            page = post(url, page, "save", wording="Later private draft")
            assert "differs from this submitted original" in page
            stale_body = dict(stale["body"], wording="Refused competing wording")
            status, _, refused = request(urllib.parse.urljoin(url, stale["url"]), stale_body)
            assert status == 400 and "Refused competing wording" in refused and "Notes changed" in refused
            reopened = next(a["href"] for a in Forms(page).links if "note_id=" in a.get("href", ""))
            parsed = urllib.parse.parse_qs(urllib.parse.urlsplit(reopened).query)
            assert parsed["session_id"] == [sid] and parsed["item_ref"] == ["q1"]
            assert request(urllib.parse.urljoin(url, reopened))[0] == 200
            status, marked = json_request(url + "api/mark", {"session_id": sid, "item_ref": "q1", "verdict": True, "notes": "Synthetic reviewer inspected original bytes"})
            assert status == 200 and marked["view"]["status"] == "complete", marked
            page = request(urllib.parse.urljoin(url, reopened))[2]
            assert "Reviewed by human" in page
            evidence.append_event(evidence.log_path(base), evidence.retraction_event(marked["event_id"], "Synthetic reviewer withdrawal"))
            page = request(urllib.parse.urljoin(url, reopened))[2]
            assert "Pending review" in page
            assert "name=\"verdict\"" not in page
            refused = request(url + "course/synthetic/artifacts?bank=../pending&item_ref=q1")
            assert refused[0] == 400
        with served(root) as url:
            page = request(urllib.parse.urljoin(url, reopened))[2]
            assert "Later private draft" in page and "Original fictional proof π" in page
            assert "Pending review" in page
            assert any(sid in a.get("href", "") and a.get("id") == "artifact-return" for a in Forms(page).links)
        doc = notes.read_note_document(reading_desk.note_root(base), course.read_course(base)["object_id"])
        assert doc["sidecar"]["notes"][0]["learner_wording"] == "Later private draft"
    print("Native learner artifacts: save/preview/cancel/submit/conflict/mark/retract/restart/return passed")


def check_browser(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    observations = []
    with fixture() as (root, base, _banks, _info), served(root) as url, sync_playwright() as pw:
        browser = pw.chromium.launch(channel=os.environ.get("ITEMBANK_VISUAL_QA_CHANNEL", "chrome"), headless=True)
        try:
            for width, scheme in ((1280, "light"), (390, "light"), (320, "light"), (1280, "dark"), (390, "dark"), (320, "dark")):
                route = "course/synthetic/artifacts?" + urllib.parse.urlencode({"bank": "pending", "item_ref": "q1"})
                context = browser.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme, reduced_motion="reduce", java_script_enabled=False)
                page = context.new_page()
                page.goto(url + route)
                page.get_by_role("checkbox").check()
                with page.expect_navigation():
                    page.get_by_role("button", name="Start this original-work activity").focus()
                    page.keyboard.press("Enter")
                sid = page.locator('form:has(input[value="save"]) input[name="session_id"]').get_attribute("value")
                assert sid
                original = "Original unaided fictional explanation.\nUse the same rule at equality."
                page.locator("#artifact-wording").fill(original)
                with page.expect_navigation():
                    page.get_by_role("button", name="Save private draft").focus()
                    page.keyboard.press("Enter")
                with page.expect_navigation():
                    page.get_by_role("button", name="Preview saved revision for submission").focus()
                    page.keyboard.press("Enter")
                with page.expect_navigation():
                    page.get_by_role("button", name="Cancel submission").focus()
                    page.keyboard.press("Enter")
                with page.expect_navigation():
                    page.get_by_role("button", name="Preview saved revision for submission").click()
                page.get_by_role("checkbox").check()
                with page.expect_navigation():
                    page.get_by_role("button", name="Submit saved revision").focus()
                    page.keyboard.press("Enter")
                assert page.get_by_role("heading", name="Submitted original").is_visible()
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                page.screenshot(path=str(output / ("artifact-%s-%s.png" % (width, scheme))), full_page=True)
                return_link = page.locator("#artifact-return")
                href = return_link.get_attribute("href")
                assert sid in href
                with page.expect_navigation():
                    return_link.focus()
                    page.keyboard.press("Enter")
                assert sid in page.url
                observations.append({"width": width, "scheme": scheme, "keyboard_forms": True, "script_free": True, "exact_sitting_return": True})
                context.close()
        finally:
            browser.close()
    (output / "observations.json").write_text(json.dumps(observations, indent=2) + "\n")
    print("Chrome native learner artifacts: 6 width/theme/script-free keyboard flows passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", type=Path)
    args = parser.parse_args()
    check_native()
    if args.browser:
        check_browser(args.browser)
