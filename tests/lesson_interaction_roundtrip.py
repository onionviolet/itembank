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
LINE_FIXTURES = (ROOT / "fixtures/lesson_lineplot_rise.md",
                 ROOT / "fixtures/lesson_lineplot_fall.md")


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


class LinkedLineTests(unittest.TestCase):
    def test_runtime_disclosure_withholds_entire_line_scene(self):
        body = ("[LINEPLOT: 1,0,2]\nPrediction: choose.\n"
                "Static explanation: the hidden label is violet tile.\n"
                "Transfer: try a new rule.")
        questions = model.load(str(LINE_FIXTURES[0]))
        for context in (None, {"comparison_questions": questions}):
            rendered = lesson._callout_html(("example", "Example", None),
                                            body, context)
            self.assertIn("withheld", rendered)
            self.assertNotIn("violet tile", rendered)
            self.assertNotIn('class="lesson-lineplot"', rendered)

    def test_two_changed_content_lessons_share_renderer(self):
        for path, declaration, changed_point in (
                (LINE_FIXTURES[0], "[LINEPLOT: 1,0,2]", "(0, 2)"),
                (LINE_FIXTURES[1], "[LINEPLOT: -1,1,-1]", "(0, -1)")):
            with self.subTest(path=path.name):
                before = path.read_bytes()
                questions = model.load(str(path))
                parsed = model.parse_lesson(str(path))
                errors, _ = model.lint(questions, lesson=parsed)
                self.assertEqual(errors, [])
                self.assertIn(declaration, path.read_text())
                self.assertIn(changed_point, path.read_text())
                page = lesson.lesson_page(str(path), questions, parsed)
                self.assertIn('class="lesson-lineplot"', page)
                self.assertIn('class="lineplot-controls" hidden', page)
                self.assertIn('class="lineplot-static"', page)
                self.assertIn('class="lineplot-y"', page)
                self.assertIn("Commit prediction", page)
                self.assertIn("Transfer:", page)
                self.assertEqual(before, path.read_bytes())

    def test_invalid_declaration_is_linted_and_does_not_render_control(self):
        for declaration in ("[LINEPLOT: 3,0,2]", "[LINEPLOT: 1,0,0]",
                            "[LINEPLOT: 1.5,0,2]", "[LINEPLOT: 1,0,2] <script>"):
            with self.subTest(declaration=declaration):
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "bank.md"
                    path.write_text(LINE_FIXTURES[0].read_text().replace(
                        "[LINEPLOT: 1,0,2]", declaration))
                    questions = model.load(str(path))
                    parsed = model.parse_lesson(str(path))
                    errors, _ = model.lint(questions, lesson=parsed)
                    self.assertIn("lesson.invalid_lineplot", [e.code for e in errors])
                    page = lesson.lesson_page(str(path), questions, parsed)
                    self.assertNotIn('class="lesson-lineplot"', page)
                    self.assertNotIn('class="lineplot-controls"', page)

    def test_static_path_and_trusted_script(self):
        data = model.parse_lesson_lineplot(
            "[LINEPLOT: -1,1,-1]\nPrediction: all?\n"
            "Static explanation: Points are (-2, 3) and (-2, 1).\n"
            "Transfer: Try y = 2x.")
        rendered = lesson_interaction.render_lineplot(data, lambda s: s)
        self.assertIn("Starting rule: y = -1x + 1", rendered)
        self.assertIn("Change only the intercept to -1", rendered)
        self.assertIn("Points: (-2, 3), (0, 1), (2, -1)", rendered)
        self.assertIn("Points: (-2, 1), (0, -1), (2, -3)", rendered)
        self.assertIn("Transfer: Try y = 2x.", rendered)
        self.assertIn('class="lineplot-controls" hidden', rendered)
        self.assertIn("grid-template-columns:repeat(auto-fit", lesson_interaction.LINEPLOT_CSS)
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage",
                          "sendBeacon", "innerHTML", "eval(", "new Function", "submit("):
            self.assertNotIn(forbidden, lesson_interaction.LINEPLOT_JS)


if __name__ == "__main__":
    if "--serve" in sys.argv:
        from surfaces import daemon
        print("Fixture SHA-256:", hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), flush=True)
        daemon.serve_scoped(str(ROOT), {"lesson_comparison": str(FIXTURE)}, {},
                            8767, no_open=True, open_path="/lesson/lesson_comparison")
    else:
        unittest.main()
