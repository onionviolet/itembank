#!/usr/bin/env python3
"""Selected navigation must own a readable foreground/background pair.

--serve provides synthetic state fixtures and the native daemon on port 8768.
It does not save settings, open a sitting, or run startup update checks.
"""
import re
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from surfaces import daemon, looks, presentation, theme


def state_page(look="neo", mode="light", profile="field-guide"):
    links = '<li><a href="?" >Overview</a></li><li><a href="?selected" aria-current="page">Learn</a></li>'
    body = ('<p>Current area: Learn</p>'
            '<nav class="course-areas course-nav-desktop" aria-label="Course areas"><ul>'
            + links + '</ul></nav><details class="course-areas course-nav-mobile">'
            '<summary>Course area: Learn</summary><nav aria-label="Course areas"><ul>'
            + links + '</ul></nav>'
            '<p><a href="?link">Source reference</a></p>'
            '<p><a class="go primary" href="?primary">Continue reading</a></p>'
            '<button class="go" type="button" aria-pressed="true">Pinned</button> '
            '<button class="go" type="button" disabled>Unavailable</button>'
            '<aside class="ib-callout"><strong>Remember</strong><p>Synthetic teaching text.</p></aside>')
    return presentation.surface_shell(
        "Navigation state fixture", body,
        theme_css=theme.theme_css({"look": look, "theme": mode}),
        presentation_profile=profile)


class NavigationColorTests(unittest.TestCase):
    def test_lesson_courses_link_reaches_course_shelf_without_metadata(self):
        with patch.object(daemon.ia, "course_shelf_state", side_effect=ValueError):
            links = daemon._lesson_context_nav(SimpleNamespace(root="unused"), "unused")
        self.assertEqual(links, [{"href": "/courses", "label": "Courses"}])

    def test_selected_pair_is_owned_together_after_look_rules(self):
        # Inspect the actual final shell rule, rather than only theme swatches.
        for look in looks.LOOK_IDS:
            for mode in ("light", "dark", "oled", "system"):
                for profile in presentation.PROFILE_RECIPES:
                    with self.subTest(look=look, mode=mode, profile=profile):
                        page = state_page(look, mode, profile)
                        rules = re.findall(r"\.course-areas a\[aria-current\]\s*\{([^}]+)\}", page)
                        self.assertTrue(rules)
                        final = rules[-1]
                        self.assertIn("background:var(--product-ink)", final)
                        self.assertIn("color:var(--paper)", final)
                        self.assertIn("text-decoration:underline", final)
                        self.assertIn('aria-current="page"', page)
                        base_rules = re.findall(r"\.course-areas a\s*\{([^}]+)\}", page)
                        self.assertIn("color:var(--product-ink)", base_rules[-1])

    def test_selected_pair_contrast(self):
        tokens = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", presentation.product_theme_css()))
        self.assertGreaterEqual(theme.contrast_ratio(tokens["paper"], tokens["product-ink"]), 4.5)
        self.assertGreaterEqual(theme.contrast_ratio(tokens["chip"], tokens["product-ink"]), 4.5)
        print("Selected contrast: %.2f:1. Existing muted pill contrast: %.2f:1." % (
            theme.contrast_ratio(tokens["paper"], tokens["product-ink"]),
            theme.contrast_ratio(tokens["chip"], tokens["product-muted"])))


if __name__ == "__main__":
    if "--serve" in sys.argv:
        class Handler(daemon.DaemonHandler):
            root = str(ROOT)
            banks = {"lesson_comparison": str(ROOT / "fixtures/lesson_comparison.md"),
                     "unit3_bank": str(ROOT / "course_fixture_17b/unit3_bank.md")}
            sessions = {}

            def do_GET(self):
                url = urlsplit(self.path)
                if url.path == "/ui-state":
                    args = parse_qs(url.query)
                    page = state_page(args.get("look", ["neo"])[0],
                                      args.get("mode", ["light"])[0],
                                      args.get("profile", ["field-guide"])[0]).encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(page)))
                    self.end_headers()
                    self.wfile.write(page)
                else:
                    super().do_GET()

        with daemon.Daemon(("127.0.0.1", 8768), Handler) as server:
            print("Native UI audit: http://127.0.0.1:8768/ui-state", flush=True)
            server.serve_forever()
    else:
        unittest.main()
