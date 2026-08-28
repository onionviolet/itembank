#!/usr/bin/env python3
"""The Phase 16A localization render check (plan 16A-08 Task 1).

A11Y-02 says canonical records carry language and direction. Plan 16A-02
landed the two fields; this file asserts the render behavior they exist for:
that a lesson declaring nothing renders exactly as it always did, that an
explicit `[LESSON-DIR: auto]` gives every text run its own bidi resolution,
that an explicit `ltr` or `rtl` asserts one direction for the whole document
and adds no per-element attribute, and that a value outside the closed tuple
falls back to a readable page with a named lint finding rather than to
corrupt text.

The distinction the whole file turns on: `dir_declared` is not the same fact
as `dir == "auto"`. `auto` is also what a lesson that never asked receives,
and emitting the per-element attribute on that path would change every
existing bank's bytes.

Standard library only, no test framework, runnable as
`python tests/localization_render_check.py`.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))

import model                                                 # noqa: E402
import lesson_capability_corpus                              # noqa: E402
from surfaces import lesson                                  # noqa: E402

LESSON_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def _render(path):
    return lesson.lesson_page(path, model.load(path),
                              model.parse_lesson(path))


def _variant(source_path, directive):
    """A copy of `source_path` with its `[LESSON-DIR:]` line replaced."""
    tmp = tempfile.mkdtemp(prefix="loc-variant-")
    path = os.path.join(tmp, os.path.basename(source_path))
    text = open(source_path, encoding="utf-8").read()
    replaced = text.replace("[LESSON-DIR: auto]", directive, 1)
    if replaced == text:
        fail("the localization fixture no longer carries [LESSON-DIR: auto], "
             "so this variant would prove nothing")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(replaced)
    return path


def check_undeclared_bank_unchanged():
    """A lesson that declares no direction gets no per-element attribute."""
    parsed = model.parse_lesson(LESSON_BANK)
    if parsed.get("dir_declared") is not False:
        fail("fixtures/lesson_bank.md reports dir_declared %r; it carries no "
             "[LESSON-DIR:] directive" % parsed.get("dir_declared"))
    if parsed.get("dir") != "auto":
        fail("the undeclared default is %r, expected auto"
             % parsed.get("dir"))
    page = _render(LESSON_BANK)
    for element in ("<p", "<li", "<td"):
        if '%s dir="auto"' % element in page:
            fail("a bank declaring no direction emitted a per-element "
                 "dir attribute on %s; that would change every existing "
                 "bank's bytes and is why the opt-in is explicit" % element)
    if 'dir="auto"' not in page:
        fail("the document element lost its dir attribute entirely")


def check_declared_auto_opts_in():
    workdir = tempfile.mkdtemp(prefix="loc-check-")
    path = lesson_capability_corpus.build_localization_lesson(workdir)
    parsed = model.parse_lesson(path)
    if parsed.get("dir_declared") is not True:
        fail("the localization bank reports dir_declared %r, expected True"
             % parsed.get("dir_declared"))
    if parsed.get("dir") != "auto":
        fail("the localization bank's direction is %r, expected auto"
             % parsed.get("dir"))
    page = _render(path)
    if '<p dir="auto"' not in page:
        fail("an explicit [LESSON-DIR: auto] did not put dir=auto on any "
             "paragraph, so each text run cannot resolve its own direction")


def check_declared_rtl_is_document_wide():
    workdir = tempfile.mkdtemp(prefix="loc-check-rtl-")
    base = lesson_capability_corpus.build_localization_lesson(workdir)
    path = _variant(base, "[LESSON-DIR: rtl]")
    parsed = model.parse_lesson(path)
    if parsed.get("dir") != "rtl" or parsed.get("dir_declared") is not True:
        fail("the rtl variant parsed to dir=%r declared=%r"
             % (parsed.get("dir"), parsed.get("dir_declared")))
    page = _render(path)
    if 'dir="rtl"' not in page:
        fail("an explicit [LESSON-DIR: rtl] did not reach the document "
             "element")
    if '<p dir="auto"' in page:
        fail("an explicit [LESSON-DIR: rtl] emitted a per-element auto "
             "attribute; the author asserted one direction for the document")


def check_invalid_direction_degrades():
    """A11Y-02's Degraded clause in the only form this tool can offer it."""
    workdir = tempfile.mkdtemp(prefix="loc-check-bad-")
    base = lesson_capability_corpus.build_localization_lesson(workdir)
    path = _variant(base, "[LESSON-DIR: sideways]")
    parsed = model.parse_lesson(path)
    if parsed.get("dir") != "auto":
        fail("an unrecognized direction fell back to %r, expected auto"
             % parsed.get("dir"))
    if parsed.get("dir_declared") is not True:
        fail("an unrecognized direction reported dir_declared False; the "
             "directive was present")
    try:
        page = _render(path)
    except Exception as exc:                                 # noqa: BLE001
        fail("an unrecognized direction raised %s during render; a bad value "
             "is a lint finding, never a crash" % exc)
    if 'dir="auto"' not in page:
        fail("the fallback did not reach the document element")
    if 'dir=""' in page:
        fail("the fallback emitted an empty dir attribute")
    if '<p dir="auto"' in page:
        fail("an unrecognized direction emitted the per-element opt-in; the "
             "author did not declare auto, the parser fell back to it")
    errors, _warnings = model.lint(model.load(path),
                                   lesson=model.parse_lesson(path))
    if not any(e.code == "lesson.invalid_direction" for e in errors):
        fail("an unrecognized direction produced no lesson.invalid_direction "
             "error, so an unhandled input is silently accepted")


def check_no_normalization_imports():
    """The posture assertion. The behavior it guards against is invisible in
    output, so the source is the only place to catch it early."""
    for name in ("model.py", "surfaces/lesson.py", "capabilities.py"):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        if "unicodedata" in text:
            fail("%s mentions unicodedata; Phase 16A applies no Unicode "
                 "normalization, and a single normalize call would silently "
                 "collapse two distinct authored spellings" % name)


CHECKS = (check_undeclared_bank_unchanged, check_declared_auto_opts_in,
          check_declared_rtl_is_document_wide,
          check_invalid_direction_degrades, check_no_normalization_imports)


def main():
    for check in CHECKS:
        check()
    print("localization render ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
