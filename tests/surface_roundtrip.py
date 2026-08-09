#!/usr/bin/env python3
"""Smoke-test the canonical study and Anki export surfaces, plus the Wave 0
semantic-DOM and sentinel-bank helpers Phase 4's later plans reuse.

The original study/export smoke checks are preserved byte-for-byte in
behavior; the additions are reusable infrastructure only: a synthetic
sentinel bank, an explanation fixture matching `runtime.explain_payload`'s
shape, and semantic-DOM helpers built on `tests/presentation_roundtrip.py`.

Standard library only, runnable as `python tests/surface_roundtrip.py`.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "itembank.py"
BANK = ROOT / "fixtures" / "sample_bank.md"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import presentation_roundtrip                            # noqa: E402
import theme_roundtrip                                   # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)],
                          cwd=ROOT, check=True, capture_output=True, text=True)


# ---- reusable sentinel bank and explanation fixtures ------------------------

SENTINEL_BANK = """# Sentinel bank (synthetic)

Fully invented content so the Phase 4 harnesses never depend on the real
fixture bank's shape drifting.

Q1. One plus one equals?   (difficulty: recall)
[ID: sentinel-mc-0001]
[OBJECTIVE: Math / basics]
A) One
B) Two
C) Three
CORRECT: B
WHY BEST: One plus one is two.
KEY DISCRIMINATOR: It is simple arithmetic.
SECOND-BEST: A, if the question meant counting the addends.
TRAP: Counting the question itself.
CONFIDENCE: high

Q2. Explain what a sentinel value is.   (difficulty: analysis)
[ID: sentinel-short-0001]
[TYPE: short]
[OBJECTIVE: Math / basics]
MODEL: A sentinel is a marker value used to signal a boundary or end.
RUBRIC:
- Names a marker value
- States it signals a boundary or end
TRAP: Overcomplicating the definition.
CONFIDENCE: high
"""


def explain_fixture(qtype="mc"):
    """A dict in the exact `runtime.explain_payload()` output shape, for
    presentation assertions that must not need a real bank to run.
    """
    if qtype == "short":
        return {"answer_text": "A sentinel is a marker value.",
                "why": "", "disc": "", "second": "", "trap": "",
                "notes": [], "model": "A sentinel is a marker value.",
                "rubric": ["Names a marker value"]}
    return {"answer_text": "B) Two", "why": "One plus one is two.",
            "disc": "It is simple arithmetic.", "second": "A, if counting addends.",
            "trap": "Counting the question itself.",
            "notes": ["Arithmetic follows the operator."],
            "correct": ["B"], "da": {"A": "One is a single addend."}}


def sentinel_items():
    """The parsed sentinel bank, one dict per item -- cached on the module
    so repeated calls do not re-parse the source text.
    """
    if not hasattr(sentinel_items, "_cache"):
        import itembank
        sentinel_items._cache = itembank.parse_bank(SENTINEL_BANK)
    return sentinel_items._cache


def served_quiz_html(bank_text=SENTINEL_BANK):
    """Render a served quiz page for `bank_text` through the existing
    `quiz.page_for(..., serve=True)` -- the same render the daemon serves, so
    semantic-DOM checks run against real current output without a server.
    """
    from surfaces.quiz import page_for
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "sentinel_bank.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(bank_text)
        import itembank
        qs = itembank.load(path)
        _, page = page_for(path, qs, serve=True, post_path="/quiz/sentinel_bank/answer",
                           lesson_base="", lesson_slugs=set())
        return page


def semantic_dom(html):
    """Parse `html` into the shared semantic DOM (presentation_roundtrip)."""
    return presentation_roundtrip.Dom(html)


# ---- preserved smoke checks + Wave 0 helper self-check ----------------------

def check_study_and_export():
    with tempfile.TemporaryDirectory() as tmp:
        study = Path(tmp) / "study.html"
        basic = Path(tmp) / "basic.tsv"
        cloze = Path(tmp) / "cloze.tsv"
        run("study", BANK, study)
        run("export", BANK, basic)
        run("export", BANK, cloze, "--format", "cloze")
        assert "Flashcards" in study.read_text(encoding="utf-8")
        assert "#notetype:Basic" in basic.read_text(encoding="utf-8")
        assert "#notetype:Cloze" in cloze.read_text(encoding="utf-8")
        assert "{{c1::" in cloze.read_text(encoding="utf-8")


def check_semantic_helpers():
    items = sentinel_items()
    if len(items) < 2:
        fail("sentinel bank parsed into %d items, expected at least 2" % len(items))
    if items[0]["type"] != "mc" or items[1]["type"] != "short":
        fail("sentinel bank item types are not mc/short: %r"
             % [q["type"] for q in items])
    ex = explain_fixture()
    if ex["correct"] != ["B"] or not ex["da"].get("A"):
        fail("explain_fixture does not match the sentinel mc shape: %r" % ex)
    ex = explain_fixture("short")
    if ex.get("model") != "A sentinel is a marker value." or not ex["rubric"]:
        fail("explain_fixture('short') is malformed: %r" % ex)

    page = served_quiz_html()
    dom = semantic_dom(page)
    presentation_roundtrip.assert_single_h1(dom)      # current title header
    presentation_roundtrip.assert_landmark(dom, "header")
    # Current served output builds its controls in JavaScript (the Task 3
    # RED target is native controls present in the served DOM itself); Wave 0
    # only asserts the response host exists and the page really is a
    # script-driven client.
    if dom.find("div", id="host") is None:
        fail("served sentinel page has no #host response container")
    if 'createElement("button")' not in page:
        fail("served sentinel page does not build controls in JavaScript")
    if not theme_roundtrip.surface_has_shared_theme(page):
        fail("served sentinel page carries no shared --accent theme block")


def main():
    check_study_and_export()
    check_semantic_helpers()
    print("study and export surfaces + Wave 0 semantic/sentinel helpers: ok")


if __name__ == "__main__":
    main()
