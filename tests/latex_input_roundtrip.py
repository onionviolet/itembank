#!/usr/bin/env python3
"""LaTeX answer entry stays a presentation layer over pending short answers."""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import model  # noqa: E402
import runtime  # noqa: E402
from surfaces import quiz, quiz_page  # noqa: E402


SHORT = """# Algebra practice

Q1. Factor the expression. (difficulty: medium)
[TYPE: short]
[INPUT: latex]
[OBJECTIVE: math1400:factoring]
MODEL: `(x+1)^2`
RUBRIC:
- identifies the repeated factor
- preserves the exponent
TRAP: Expanding instead of factoring obscures the requested form.
CONFIDENCE: high
"""


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def test_contract_and_authority():
    questions = model.parse_bank(SHORT)
    check(len(questions) == 1, "LaTeX short item did not parse")
    item = questions[0]
    check(item["input_format"] == "latex", "INPUT metadata was not retained")
    public = runtime.public_item(item)
    check(public.get("input_format") == "latex", "public item lost input format")
    check(public.get("response_schema", {}).get("format") == "latex",
          "response schema does not declare LaTeX")
    check(runtime.score_response(item, r"(x+1)^2") is None,
          "LaTeX short response must remain pending")


def test_invalid_scope_is_linted():
    text = """Q1. Pick one.
[TYPE: mc]
[INPUT: latex]
A) One
B) Two
C) Three
CORRECT: A
WHY BEST: One is keyed.
KEY DISCRIMINATOR: Select the keyed option.
SECOND-BEST: Two is a plausible distractor.
DISTRACTOR ANALYSIS:
- A) Correct.
- B) Would be correct if the key were B.
- C) Would be correct if the key were C.
TRAP: Guessing.
CONFIDENCE: high
"""
    questions = model.parse_bank(text)
    errors, _ = model.lint(questions)
    check("item.input_format_invalid" in [row.code for row in errors],
          "LaTeX input on a non-short item was not rejected")


def test_progressive_rendering():
    item = runtime.public_item(model.parse_bank(SHORT)[0])
    controls = quiz_page._form_controls(item)
    check('data-input-format="latex"' in controls,
          "no-script control lost its declared input format")
    with tempfile.TemporaryDirectory() as tmp:
        bank = os.path.join(tmp, "math_input.md")
        with open(bank, "w", encoding="utf-8") as handle:
            handle.write(SHORT)
        _, page = quiz.page_for(bank, model.load(bank), serve=True,
                                bank_stem="math_input", mode="practice")
        for marker in ('id="latex-input-adapter"',
                       'aria-label", "Rendered LaTeX preview"',
                       "The exact source is saved; the preview does not grade it.",
                       "throwOnError:false", "trust:false"):
            check(marker in page, "LaTeX page lacks %r" % marker)
        check("/assets/katex/katex.min.js" in page,
              "served math input lacks local KaTeX")

    sample = os.path.join(ROOT, "fixtures", "sample_bank.md")
    _, plain_page = quiz.page_for(sample, model.load(sample), serve=True,
                                  bank_stem="sample_bank", mode="practice")
    check('id="latex-input-adapter"' not in plain_page,
          "ordinary bank received the LaTeX input adapter")


if __name__ == "__main__":
    test_contract_and_authority()
    test_invalid_scope_is_linted()
    test_progressive_rendering()
    print("latex input: contract, pending authority, fallback, and local preview passed")
