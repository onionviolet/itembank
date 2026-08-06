#!/usr/bin/env python3
"""The protocol contract harness: lint codes, and later schema versions and `spec`.

Standard library only, runnable as `python tests/protocol_roundtrip.py`.
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402

BROKEN_BANK = os.path.join(ROOT, "fixtures", "broken_bank.md")
SAMPLE_BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run_lint_json(bank_path):
    # PYTHONIOENCODING forces the child's stdout to UTF-8 regardless of the host
    # console code page (cp1252 on a default Windows console), which would otherwise
    # raise UnicodeEncodeError the moment a lint message carries non-ASCII content.
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "lint", bank_path, "--json"],
        capture_output=True, text=True, encoding="utf-8", env=env)


def test_lint_error_shape():
    qs = itembank.load(BROKEN_BANK)
    errors, warnings = itembank.lint(qs)
    if not errors or not warnings:
        fail("broken_bank.md produced no errors or no warnings; it can no longer exercise "
             "this test")
    for entry in list(errors) + list(warnings):
        if not isinstance(entry, itembank.LintError):
            fail("lint entry is not a LintError: %r" % (entry,))
        if not entry.code or "." not in entry.code:
            fail("code %r is not a non-empty dotted string" % (entry.code,))
        if entry.code not in itembank.LINT_CODES:
            fail("code %r is not declared in LINT_CODES" % (entry.code,))
        if not entry.field:
            fail("field is empty on %r" % (entry,))
        if not entry.item:
            fail("item is empty on %r" % (entry,))
        if str(entry) != "%s: %s" % (entry.item, entry.message):
            fail("str() does not reproduce '%%s: %%s' for %r" % (entry,))


def test_lint_codes_declared():
    codes = itembank.LINT_CODES
    if list(codes) != sorted(codes):
        fail("LINT_CODES is not sorted")
    if len(set(codes)) != len(codes):
        fail("LINT_CODES has duplicates")
    for c in codes:
        prefix = c.split(".", 1)[0]
        if prefix not in ("item", "bank"):
            fail("code %r has an undeclared namespace prefix %r" % (c, prefix))


def test_lint_json_clean():
    clean = run_lint_json(SAMPLE_BANK)
    if clean.returncode != 0:
        fail("lint --json on the clean fixture exited %d: %s" % (clean.returncode, clean.stderr))
    payload = json.loads(clean.stdout)
    if payload["errors"] != []:
        fail("lint --json on the clean fixture reported errors: %r" % (payload["errors"],))

    broken = run_lint_json(BROKEN_BANK)
    if broken.returncode == 0:
        fail("lint --json on the broken fixture exited 0")
    payload = json.loads(broken.stdout)
    for e in payload["errors"]:
        if set(e.keys()) != {"code", "field", "item", "message"}:
            fail("error object has unexpected keys: %r" % (sorted(e.keys()),))


def test_lint_json_encoding():
    """A rubric point can be one word by str.split() and dozens of UTF-8 bytes, so the
    MODEL/RUBRIC length thresholds have to measure whitespace-separated tokens on the
    Unicode code-point string, never bytes. And --json has to round-trip non-ASCII
    content unescaped, or ensure_ascii regressed.

    Two items: Q1's deliberately-unknown table category is CJK text, and it is echoed
    verbatim into an error message, proving the round-trip; Q2's rubric point is 30 CJK
    characters, one whitespace-separated token, proving the threshold counts tokens
    on the code-point string rather than bytes.
    """
    tmpdir = tempfile.mkdtemp()
    bank_path = os.path.join(tmpdir, "encoding_bank.md")
    category_cjk = "在线"       # echoed verbatim into item.row_category_unknown
    rubric_cjk = "的" * 30      # 30 Chinese characters: one whitespace-separated word
    bank_text = (
        "Q1. 一个简单的问题。\n"
        "[TYPE: table]\n"
        "[CATEGORIES: Online | Offline]\n\n"
        "ROW) First thing :: %s\n"
        "ROW) Second thing :: Offline\n\n"
        "WHY BEST: Placeholder.\n\n"
        "DISTRACTOR ANALYSIS:\n"
        "- Placeholder bullet.\n\n"
        "TRAP: Placeholder.\n\n"
        "CONFIDENCE: high\n\n"
        "Q2. Explain why redundancy matters in a distributed system.\n"
        "[TYPE: short]\n\n"
        "MODEL: A short model answer.\n\n"
        "RUBRIC:\n"
        "- %s\n"
        "- Mentions a second, distinct checkable claim in English.\n\n"
        "TRAP: Reciting jargon instead of explaining the mechanism.\n\n"
        "CONFIDENCE: high\n"
    ) % (category_cjk, rubric_cjk)
    open(bank_path, "w", encoding="utf-8").write(bank_text)

    result = run_lint_json(bank_path)
    if category_cjk not in result.stdout:
        fail("lint --json escaped non-ASCII characters; ensure_ascii=False is not in effect "
             "(stdout: %r)" % (result.stdout[:400],))
    payload = json.loads(result.stdout)
    codes = [e["code"] for e in payload.get("errors", []) + payload.get("warnings", [])]
    if "item.row_category_unknown" not in codes:
        fail("the deliberately-unknown CJK table category did not raise "
             "item.row_category_unknown; the fixture no longer exercises this test")
    if "item.rubric_point_too_long" in codes:
        fail("a 30-character CJK rubric point (one whitespace-separated token) was flagged "
             "as too long; length must be measured in tokens on the code-point string, "
             "not bytes")


def main():
    test_lint_error_shape()
    test_lint_codes_declared()
    test_lint_json_clean()
    test_lint_json_encoding()
    print("protocol contract: ok (%d lint codes declared)" % len(itembank.LINT_CODES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
