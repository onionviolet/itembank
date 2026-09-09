#!/usr/bin/env python3
"""Native comparison contract and disclosure tests, stdlib only.

--serve opens only the synthetic fixture on the real daemon lesson route.
It creates no sitting and performs no startup update check.
"""
import hashlib
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import model
from surfaces import lesson, lesson_interaction

FIXTURE = ROOT / "fixtures/lesson_comparison.md"
SOURCE = ROOT / "prototypes/competition/rainfall.txt"


class ComparisonTests(unittest.TestCase):
    def page(self, path=FIXTURE, **kwargs):
        return lesson.lesson_page(str(path), model.load(str(path)),
                                  model.parse_lesson(str(path)), **kwargs)

    def test_native_parse_lint_and_unchanged_input(self):
        before = FIXTURE.read_bytes()
        qs = model.load(str(FIXTURE))
        parsed = model.parse_lesson(str(FIXTURE))
        errors, _ = model.lint(qs, lesson=parsed)
        self.assertEqual(errors, [])
        page = self.page()
        self.assertIn('class="lesson-comparison"', page)
        self.assertIn('type="range"', page)
        self.assertIn('AI-authored synthesis', page)
        self.assertIn('href="#source-rain-01"', page)
        self.assertIn('id="source-rain-01"', page)
        self.assertIn('rainfall.txt', page)
        if SOURCE.exists():
            self.assertIn(SOURCE.read_text().strip(), FIXTURE.read_text())
        self.assertEqual(before, FIXTURE.read_bytes())

    def test_bounds_and_missing_explanation(self):
        for header in ("12,18,0,mm", "25,18,24,mm", "12,25,24,mm",
                       "-1,18,24,mm", "12,NaN,24,mm", "12,Infinity,24,mm",
                       "12,18,10001,mm", "12,18.5,24,mm", "12,18,24, "):
            self.assertIn("error", model.parse_lesson_comparison(
                "[COMPARE: " + header + "]\nStatic example."))
        self.assertIn("error", model.parse_lesson_comparison("[COMPARE: 12,18,24,mm]"))
        for value in ("0,0,1,mm", "10000,10000,10000,mm"):
            self.assertNotIn("error", model.parse_lesson_comparison(
                "[COMPARE: " + value + "]\nStatic example."))

    def test_invalid_linted_and_static(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bank.md"
            path.write_text(FIXTURE.read_text().replace("12,18,24,mm", "12,NaN,24,mm"))
            errors, _ = model.lint(model.load(str(path)), lesson=model.parse_lesson(str(path)))
            self.assertIn("lesson.invalid_comparison", [e.code for e in errors])
            page = self.page(path)
            self.assertIn("Comparison unavailable", page)
            self.assertIn("Static examples", page)
            self.assertNotIn('type="range"', page)

    def test_absent_opt_in_preserves_example(self):
        body = "Ordinary **bold** example."
        self.assertIsNone(model.parse_lesson_comparison(body))
        rendered = lesson._callout_html(("example", "Example", None), body)
        self.assertIn("<strong>bold</strong>", rendered)
        self.assertNotIn("comparison", rendered)

    def test_quoted_markers_are_not_active_treatments(self):
        for prefix, suffix in (("> [!NOTE]\n", ""), ("```text\n", "\n```")):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "bank.md"
                text = FIXTURE.read_text().replace(
                    "> [!EXAMPLE]", prefix + "> [!EXAMPLE]")
                text = text.replace("12,18,24,mm", "12,NaN,24,mm")
                text = text.replace("\nInteraction is temporary", suffix + "\n\nInteraction is temporary")
                path.write_text(text)
                errors, _ = model.lint(model.load(str(path)), lesson=model.parse_lesson(str(path)))
                self.assertNotIn("lesson.invalid_comparison", [e.code for e in errors])
                self.assertNotIn('type="range"', self.page(path))

    def test_unclosed_fence_cannot_hide_next_heading_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bank.md"
            text = FIXTURE.read_text().replace(
                "### Compare equal intervals",
                "### Earlier heading\n\n```text\nUnclosed sample\n\n### Compare equal intervals")
            path.write_text(text.replace("12,18,24,mm", "12,NaN,24,mm"))
            errors, _ = model.lint(model.load(str(path)), lesson=model.parse_lesson(str(path)))
            self.assertIn("lesson.invalid_comparison", [e.code for e in errors])
            self.assertNotIn('type="range"', self.page(path))

    def test_hostile_text_is_not_executable(self):
        body = '[COMPARE: 12,18,24,<img onerror=x>]\n<script>alert(1)</script> **Important**'
        rendered = lesson._callout_html(("example", "Example", None), body,
                                       {"comparison_questions": []})
        self.assertNotIn("<img", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;img onerror=x&gt;", rendered)

    def test_runtime_disclosure_owns_whole_block(self):
        qs = model.load(str(FIXTURE))
        body = '[COMPARE: 12,18,24,mm]\nThe hidden label is violet tile.'
        for context in (None, {"comparison_questions": qs}):
            rendered = lesson._callout_html(("example", "Example", None), body, context)
            self.assertIn("withheld", rendered)
            self.assertNotIn("violet tile", rendered)
            self.assertNotIn("12", rendered)
            self.assertNotIn('type="range"', rendered)

    def test_required_gate_truncates_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bank.md"
            path.write_text(FIXTURE.read_text().replace(
                "> [!EXAMPLE]", "> [!CHECK: q1]\n\n> [!EXAMPLE]"))
            qs = model.load(str(path))
            gate = {"policy": "required", "states": {"q1": "open"},
                    "resolve": lambda cid: qs[0], "stem": "bank",
                    "bank": str(path), "skip": "off"}
            page = self.page(path, runtime=True, gate=gate)
            self.assertNotIn('class="lesson-comparison"', page)
            self.assertNotIn('type="range"', page)
            self.assertNotIn("Static examples", page)
            self.assertNotIn("Hypothetical value.", page)

    def test_guided_and_static_retain_meaning(self):
        for mode in ("continuous", "guided", "paced"):
            page = self.page(mode=mode)
            self.assertIn("Static examples", page)
            self.assertIn("B minus A = 6 mm", page)
            self.assertIn('class="comparison-controls" hidden', page)
        self.assertIn("@media print", lesson_interaction.CSS)
        self.assertNotIn("animation", lesson_interaction.CSS)
        self.assertNotIn("transition", lesson_interaction.CSS)

    def test_trusted_script_has_no_egress_or_evidence(self):
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage",
                          "sendBeacon", "innerHTML", "eval(", "new Function", "submit("):
            self.assertNotIn(forbidden, lesson_interaction.JS)

    def test_native_route_writes_nothing(self):
        from surfaces import daemon
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bank.md"
            path.write_bytes(FIXTURE.read_bytes())
            class Handler(daemon.DaemonHandler):
                root = tmp
                banks = {"bank": str(path)}
                sessions = {}
            before = {str(p): p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            with daemon.Daemon(("127.0.0.1", 0), Handler) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    url = "http://127.0.0.1:%d/lesson/bank" % server.server_address[1]
                    with urllib.request.urlopen(url) as response:
                        page = response.read().decode()
                    self.assertIn('class="lesson-comparison"', page)
                    self.assertNotIn('violet tile', page)
                    self.assertEqual(before, {str(p): p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()})
                finally:
                    server.shutdown()
                    thread.join()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        from surfaces import daemon
        print("Fixture SHA-256:", hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), flush=True)
        daemon.serve_scoped(str(ROOT), {"lesson_comparison": str(FIXTURE)}, {},
                            8767, no_open=True, open_path="/lesson/lesson_comparison")
    else:
        unittest.main()
