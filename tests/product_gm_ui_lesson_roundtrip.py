#!/usr/bin/env python3
"""Fictional learner-facing lesson orientation and practice regressions."""
import html
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from model import load, parse_lesson
from surfaces import lesson


class LessonPresentation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "fiction.md")
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("""# Fictional learning unit

## LESSON

### First

Plain material with **meaning** and $x+1$.

### Second

> [!EXAMPLE]
> A useful static example.

### Third

Additional material, without practice.

Q1. Choose the example.
[OBJECTIVE: Fictional example]
[TYPE: mc]
[LESSON-REF: First]
A) First
B) Second
CORRECT: A
WHY BEST: PRIVATE RATIONALE
KEY DISCRIMINATOR: PRIVATE KEY
DISTRACTOR ANALYSIS:
- B) Wrong in this example; correct for another example.
TRAP: PRIVATE TRAP
CONFIDENCE: high
""")
        self.qs = load(self.path)
        self.parsed = parse_lesson(self.path)

    def page(self, **kwargs):
        return lesson.lesson_page(self.path, self.qs, self.parsed, **kwargs)

    def test_compact_header_and_outline_without_glossary(self):
        page = self.page()
        header = re.search(r"<header>(.*?)</header>", page, re.S).group(1)
        self.assertNotIn("Application:", header)
        self.assertIn("Fictional learning unit lesson", header)
        self.assertIn('<details class="lesson-reading-about">', header)
        self.assertIn("in this tab", header)
        self.assertNotIn("new tab", page)
        self.assertIn('aria-label="Sections in this lesson"', page)
        self.assertIn('class="reader-nav"', page)
        self.assertNotIn('class="reader-nav nav-rail"', page)
        self.assertEqual(page.count('class="nav-n"'), 3)
        self.assertIn('href="#second"', page)
        self.assertNotIn("Items testing this", page)
        self.assertNotIn("No items reference this section yet.", page)
        self.assertIn("Section practice (1)", page)

    def test_explicit_rail_and_none_preferences_remain_respected(self):
        settings_path = os.path.join(self.tmp.name, "itembank.json")
        with open(settings_path, "w", encoding="utf-8") as handle:
            json.dump({"reader": {"reader_nav": "rail"}}, handle)
        self.assertIn('class="reader-nav nav-rail"', self.page())
        self.assertIn('class="reader-nav nav-rail"', self.page(mode="guided"))
        with open(settings_path, "w", encoding="utf-8") as handle:
            json.dump({"reader": {"reader_nav": "column"}}, handle)
        self.assertIn('class="reader-nav"', self.page(mode="guided"))
        with open(settings_path, "w", encoding="utf-8") as handle:
            json.dump({"reader": {"reader_nav": "none"}}, handle)
        self.assertNotIn('class="reader-nav', self.page())

    def test_auto_outline_does_not_add_guided_header_row(self):
        self.assertIn('class="reader-nav"', self.page())
        self.assertNotIn('class="reader-nav', self.page(mode="guided"))

    def test_outline_only_names_rendered_headings(self):
        filtered = self.page(ref="Second")
        self.assertNotIn('class="reader-nav', filtered)
        self.assertIn('id="second"', filtered)
        self.assertNotIn('id="first"', filtered)
        self.assertNotIn('id="third"', filtered)
        gate = {"policy": "required", "states": {}, "resolve": lambda cid: self.qs[0],
                "bank": "fiction.md", "stem": "fiction", "skip": "off"}
        self.parsed["headings"][1]["body"] = "> [!CHECK: q1]\n\nHidden tail."
        gated = self.page(gate=gate)
        self.assertEqual(gated.count('class="nav-n"'), 2)
        self.assertIn('href="#first"', gated)
        self.assertIn('href="#second"', gated)
        self.assertNotIn('href="#third"', gated)
        self.assertNotIn("Hidden tail.", gated)
        self.assertNotIn("Additional material", gated)

    def test_safe_public_plain_code_math_and_visual_previews(self):
        samples = [
            ("mc", "Choose **a term** with <img src=x onerror=bad()>.",
             "&lt;img src=x onerror=bad()&gt;"),
            ("check", "Observe:\n\n```python\n### A code comment\nprint('<script>unsafe</script>')\n```",
             "&lt;script&gt;unsafe&lt;/script&gt;"),
            ("mc", "Compare $x^2$ and \\(x+1\\).", "$x^2$"),
            ("visual", "Place the point at the declared position.",
             "Open the question for its diagram and response controls."),
        ]
        for qtype, stem, expected in samples:
            with self.subTest(qtype=qtype, stem=stem):
                item = dict(self.qs[0], type=qtype, stem=stem)
                preview = lesson._backlinks_html("fiction", [item], "first")
                self.assertIn(expected, preview)
                self.assertNotIn("```", preview)
                self.assertNotIn("<script>unsafe", preview)
                self.assertNotIn("<img src=x", preview)
                self.assertNotIn("PRIVATE", preview)
                self.assertNotIn("<form", preview)
                self.assertNotIn('class="run-go"', preview)
        linked = dict(self.qs[0], stem="[Unsafe](javascript:alert(1))")
        self.assertNotIn('href="javascript:', lesson._backlinks_html("fiction", [linked], "first"))

    def test_admitted_course_and_exact_sitting_action_survives(self):
        practice = "/quiz/fiction?mode=practice&course=course%20one"
        context = [{"href": "/course/course%20one/learn", "label": "Back to course"},
                   {"href": practice, "label": "Continue to practice"}]
        page = self.page(runtime=True, context_nav=context)
        self.assertIn('href="%s#q1"' % html.escape(practice, quote=True), page)
        saved = "/quiz/fiction?mode=exam&session=exact%20saved&course=course%20one"
        context[1] = {"href": saved, "label": "Return to saved sitting"}
        page = self.page(runtime=True, context_nav=context, session_id="exact saved")
        self.assertIn('href="%s"' % html.escape(saved, quote=True), page)
        self.assertNotIn('href="%s#q1"' % html.escape(saved, quote=True), page)
        self.assertNotIn("Return to question 1", page)
        self.assertIn("Return to saved sitting", page)
        self.assertNotIn("PRIVATE RATIONALE", page)
        self.assertNotIn("PRIVATE KEY", page)
        self.assertNotIn("<form", page)

    def test_saved_sitting_never_promises_to_select_previewed_item(self):
        item = dict(self.qs[0], id="q2", number=2)
        saved = "/quiz/fiction?mode=practice&session=active-on-q1&course=fictional"
        preview = lesson._backlinks_html("fiction", [item], "first", [
            {"href": saved, "label": "Return to saved sitting"}])
        self.assertIn("Question 2", preview)
        self.assertIn('href="%s"' % html.escape(saved, quote=True), preview)
        self.assertNotIn("#q2", preview)
        self.assertIn("Return to saved sitting", preview)
        self.assertNotIn("Practice question 2", preview)

    def test_unbound_static_and_guided_keep_meaning(self):
        continuous, guided = self.page(), self.page(mode="guided")
        for page in (continuous, guided):
            self.assertIn("Plain material with <strong>meaning</strong>", page)
            self.assertIn("A useful static example.", page)
            self.assertIn('href="/quiz/fiction#q1"', page)
            self.assertIn("Section practice (1)", page)
            self.assertNotIn("PRIVATE", page)
        example = r'<section class="callout callout-example".*?</section>'
        self.assertEqual(re.search(example, continuous, re.S).group(0),
                         re.search(example, guided, re.S).group(0))
        self.assertIn('data-stage-open', guided)


if __name__ == "__main__":
    unittest.main()
