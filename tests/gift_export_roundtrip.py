#!/usr/bin/env python3
"""DEL-08 coverage: asserts exact GIFT output for every expressible item type over
synthetic fixtures, that every character in the escape set is actually escaped in the
rendered document, that a `table`/`dnd` item's repeated categories survive as repeated
`matching` sub-questions, that export is byte-deterministic, that a `multi` item's
scoring-divergence warning names its item number, that the module carries no second
scorer or parser, and the loud-failure paths: `build` always refused by item number,
`--strict` promoting `multi` to a per-item failure, an unescapable field named by the
refusal, and a partial or all-skipped export summarising and exiting distinctly from a
complete one.

Standard library only, runnable as `python tests/gift_export_roundtrip.py`.
"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
ITEMBANK = os.path.join(ROOT, "itembank.py")
SAMPLE_BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
ESCAPES_BANK = os.path.join(ROOT, "fixtures", "gift_escapes_bank.md")
BUILD_ONLY_BANK = os.path.join(ROOT, "fixtures", "gift_build_only_bank.md")

# A minimal, synthetic, lint-clean bank with no `build` item -- used only to prove
# the all-clear export path (nothing skipped) prints the plain success line and
# exits 0, distinct from every skip-carrying fixture above.
NO_BUILD_BANK = """Q1. Pick the correct color.

A) Red
B) Blue
C) Green

CORRECT: A

WHY BEST: Testing the all-clear export path.

CONFIDENCE: high

Q2. Pick the correct shape.

A) Circle
B) Square
C) Triangle

CORRECT: C

WHY BEST: Testing the all-clear export path a second time.

CONFIDENCE: high
"""

from model import load                                     # noqa: E402
from surfaces import gift                                  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# Golden strings, pinned against `fixtures/sample_bank.md`'s five GIFT-expressible
# items (mc, multi, table, dnd, short -- `build` has no GIFT equivalent and is
# skipped). A renderer change that alters shape fails one of these with a readable
# diff rather than a vague downstream symptom.
GOLDEN_MC = '::Q1:: An operator notices the chlorine residual at the far end of the distribution network has fallen below the regulatory floor, while the reading at the plant outlet is normal. What is the most likely explanation? {\n~The plant is underdosing chlorine # Underdosing would depress the plant outlet reading too; this would be correct if the outlet reading were also low.\n=Chlorine demand in the network is consuming the residual before it reaches the far end # Correct\\: demand in transit consumes the residual.\n~The far-end sampling tap is contaminated # A dirty tap is a real cause of a single bad sample, and this would be right if only one tap out of several at the same location read low.\n~The regulatory floor was recently raised # A changed standard alters the threshold, not the measurement; this would be correct if the question asked why a previously compliant reading is now a violation.\n#### A normal outlet reading rules out underdosing at the source, so the loss is happening in transit. Chlorine demand from biofilm, sediment, and long residence time consumes residual as water travels.\n}'

GOLDEN_MULTI = '::Q2:: Which conditions require an immediate boil-water notice? {\n~%50%Loss of positive pressure across the distribution system # Correct\\: pressure loss permits intrusion.\n~%-100%A single customer complaint about taste # Taste is aesthetic; this would be correct if the question asked what triggers a secondary-standard investigation.\n~%50%Confirmed detection of E. coli in a routine sample # Correct\\: a confirmed indicator organism.\n~%-100%A scheduled hydrant flushing program # Planned flushing is routine; it would be right if the question asked what causes temporary discoloration complaints.\n~%-100%A turbidity reading slightly below the action level # Below the action level means in compliance, and it would be correct if the reading were above it.\n#### Both indicate a credible pathway for pathogens to reach customers. Loss of pressure allows intrusion; a confirmed indicator organism means contamination is already present.\n}'

GOLDEN_TABLE = '::Q3:: Classify each task as ROUTINE or EMERGENCY response. {\n=Monthly calibration of a turbidimeter -> Routine\n=Responding to a confirmed main break flooding a street -> Emergency\n=Quarterly lead and copper sampling -> Routine\n=Isolating a section after a chemical spill enters a storm drain -> Emergency\n}'

GOLDEN_DND = '::Q5:: Sort each parameter into PRIMARY or SECONDARY drinking-water standard. {\n=Total coliform -> Primary\n=Lead -> Primary\n=Iron staining laundry -> Secondary\n=Odour -> Secondary\n}'

GOLDEN_SHORT = '::Q6:: A plant meets every primary standard but customers still complain the water is undrinkable. Explain how both facts can be true at once, and what the operator should investigate. {=Primary standards are health-based and enforceable; they say nothing about taste, odour, colour or staining, which secondary standards cover as non-enforceable guidelines. Water can therefore be legally safe and aesthetically unacceptable at the same time. The operator should investigate the secondary parameters, iron and manganese for staining and taste, sulphide or algal by-products for odour, and turbidity or colour for appearance.}'

# The escape set GIFT_ESCAPE covers: tilde, equals, hash, opening/closing brace,
# colon, and backslash. A scan over this tuple, not seven hand-written literals, so
# a newly added escape-set member is covered by changing one line.
ESCAPE_CHARS = ("~", "=", "#", "{", "}", ":", "\\")


def test_every_expressible_type_renders():
    qs = load(SAMPLE_BANK)
    document, errors, warnings = gift.render_gift(qs)
    blocks = document.split("\n\n")
    golden = [GOLDEN_MC, GOLDEN_MULTI, GOLDEN_TABLE, GOLDEN_DND, GOLDEN_SHORT]
    if len(blocks) != len(golden):
        fail("render_gift(sample_bank.md) produced %d blocks, expected %d: %r" %
             (len(blocks), len(golden), blocks))
    for i, (got, want) in enumerate(zip(blocks, golden)):
        if got != want:
            fail("block %d rendered differently than its golden string:\ngot:  %r\nwant: %r" %
                 (i, got, want))


def collect_user_fields(q):
    """Every user-authored text field this module might escape for one item,
    generic across type rather than hand-listing which item carries which
    character -- a newly added field is covered by adding it here once.
    """
    fields = [q.get("stem")]
    t = q["type"]
    if t in ("mc", "multi"):
        fields.append(q.get("why"))    # general feedback -- mc/multi only, not matching/short
        fields.extend(q.get("opts", {}).values())
        fields.extend(v for v in q.get("da", {}).values() if v)
    elif t in ("table", "dnd"):
        for r in q.get("rows", []):
            fields.append(r.get("text"))
            fields.append(r.get("cat"))
    elif t == "short":
        fields.append(q.get("model"))
    return [f for f in fields if f]


def test_every_escape_set_character_is_escaped():
    """Structural GIFT syntax -- the `::Qn::` name delimiters, the opening/
    closing braces, the =/~ markers, the `#`/`####` feedback markers -- uses
    these same characters unescaped by design, so a whole-document character
    scan cannot tell structure from content. This scans user-authored fields
    instead: every field's `gift_escape()`-transformed form must appear
    verbatim in the rendered document, which is only true if escaping ran.
    """
    qs = load(ESCAPES_BANK)
    document, errors, warnings = gift.render_gift(qs)
    seen = set()
    for q in qs:
        if q["type"] == "build":
            continue    # never rendered (no GIFT equivalent); nothing to check
        for raw in collect_user_fields(q):
            for ch in ESCAPE_CHARS:
                if ch in raw:
                    seen.add(ch)
            escaped = gift.gift_escape(raw)
            if escaped and escaped not in document:
                fail("escaped field not found verbatim in the rendered document -- "
                     "raw: %r, expected escaped form: %r" % (raw, escaped))
    missing = set(ESCAPE_CHARS) - seen
    if missing:
        fail("escape-set characters never appear in any user-authored field of the "
             "fixture: %r -- the fixture no longer exercises them" % sorted(missing))


def test_matching_preserves_repeated_categories():
    qs = load(SAMPLE_BANK)
    q3 = next(q for q in qs if q["number"] == 3)
    block = gift.gift_matching(q3)
    row_count = len(q3["rows"])
    arrow_count = block.count(" -> ")
    if arrow_count != row_count:
        fail("expected %d matching sub-questions (one per row), rendered %d: %r" %
             (row_count, arrow_count, block))
    if block.count("-> Routine") < 2 or block.count("-> Emergency") < 2:
        fail("repeated category values across rows were not preserved: %r" % block)


def test_export_is_deterministic():
    tmp = tempfile.mkdtemp()
    out1 = os.path.join(tmp, "a.gift")
    out2 = os.path.join(tmp, "b.gift")
    r1 = subprocess.run([sys.executable, ITEMBANK, "export", SAMPLE_BANK, out1,
                         "--format", "gift"], capture_output=True, text=True, encoding="utf-8")
    r2 = subprocess.run([sys.executable, ITEMBANK, "export", SAMPLE_BANK, out2,
                         "--format", "gift"], capture_output=True, text=True, encoding="utf-8")
    if r1.returncode not in (0, 1):
        fail("first GIFT export exited %d: %s" % (r1.returncode, r1.stdout + r1.stderr))
    if r2.returncode not in (0, 1):
        fail("second GIFT export exited %d: %s" % (r2.returncode, r2.stdout + r2.stderr))
    a = open(out1, encoding="utf-8").read()
    b = open(out2, encoding="utf-8").read()
    if a != b:
        fail("two GIFT exports of the same bank produced different files")
    shutil.rmtree(tmp, ignore_errors=True)


def test_multi_warns_by_item_number():
    tmp = tempfile.mkdtemp()
    out = os.path.join(tmp, "multi.gift")
    r = subprocess.run([sys.executable, ITEMBANK, "export", SAMPLE_BANK, out,
                        "--format", "gift"], capture_output=True, text=True, encoding="utf-8")
    combined = r.stdout + r.stderr
    if "Q2" not in combined or "partial credit" not in combined:
        fail("multi divergence warning missing or does not name Q2: %r" % combined)
    content = open(out, encoding="utf-8").read()
    if "::Q2::" not in content:
        fail("multi item Q2 was not written to the GIFT file despite being only a warning")
    shutil.rmtree(tmp, ignore_errors=True)


def test_no_second_scorer_or_parser():
    text = open(os.path.join(ROOT, "surfaces", "gift.py"), encoding="utf-8").read()
    for name in ("score_response", "parse_bank", "canonical_response"):
        if name in text:
            fail("surfaces/gift.py references %r -- GIFT export must not carry a "
                 "second scorer or a second parser" % name)


def test_build_always_fails_by_item_number():
    """`build` has no GIFT equivalent (D-02) -- refused by item number and dotted
    code in both modes, and never present in the rendered document either way.
    """
    qs = load(SAMPLE_BANK)
    for strict in (False, True):
        document, errors, warnings = gift.render_gift(qs, strict=strict)
        matches = [e for e in errors if e.startswith(gift.GIFT_TYPE_UNSUPPORTED) and "Q4" in e]
        if not matches:
            fail("strict=%r: no Q4 build-refusal error carrying the dotted code found "
                 "in %r" % (strict, errors))
        if "::Q4::" in document:
            fail("strict=%r: a build item was written into the GIFT document" % strict)


def test_strict_promotes_multi_to_a_failure():
    """Default mode warns and keeps the `multi` item; `--strict` fails it instead,
    sharing the same divergence sentence and differing only in the not-exported
    marker and which list the message lands in.
    """
    qs = load(SAMPLE_BANK)
    document, errors, warnings = gift.render_gift(qs)
    strict_document, strict_errors, strict_warnings = gift.render_gift(qs, strict=True)

    default_msg = next((w for w in warnings if "Q2" in w), None)
    if default_msg is None:
        fail("default mode: no Q2 warning found: %r" % warnings)
    if "::Q2::" not in document:
        fail("default mode: Q2 (multi) was not written to the document despite "
             "being only a warning")
    if "not exported" in default_msg:
        fail("default-mode multi warning carries the not-exported marker: %r" % default_msg)

    strict_msg = next((e for e in strict_errors if "Q2" in e), None)
    if strict_msg is None:
        fail("strict mode: no Q2 error found: %r" % strict_errors)
    if "::Q2::" in strict_document:
        fail("strict mode: Q2 (multi) was still written to the document")
    if "not exported" not in strict_msg:
        fail("strict-mode multi failure does not carry the not-exported marker: %r"
             % strict_msg)
    if not strict_msg.startswith(gift.GIFT_STRICT_DIVERGENCE):
        fail("strict-mode multi failure is not prefixed by its dotted code: %r" % strict_msg)

    if gift.MULTI_DIVERGENCE not in default_msg or gift.MULTI_DIVERGENCE not in strict_msg:
        fail("default and strict multi messages do not state the same divergence:\n"
             "default: %r\nstrict:  %r" % (default_msg, strict_msg))


def test_unescapable_field_is_named():
    """A line break survives escaping, so `unexpressible_field` -- and `gift_item`'s
    refusal built on it -- must name the specific field, not a generic label, and
    must do so per field kind: stem, an option, and a matching row.
    """
    base_mc = {"type": "mc", "number": 1, "opts": {"A": "fine", "B": "ok", "C": "ok"},
               "correct": ["A"], "da": {}, "why": ""}

    stem_item = dict(base_mc, stem="line one\nline two")
    if gift.unexpressible_field(stem_item) != "stem":
        fail("a stem carrying a line break was not named 'stem': %r" %
             gift.unexpressible_field(stem_item))
    errors, warnings = [], []
    if gift.gift_item(stem_item, errors, warnings) is not None:
        fail("gift_item rendered an item with an unescapable stem")
    if not any("stem" in e for e in errors):
        fail("gift_item's refusal for an unescapable stem does not name it: %r" % errors)

    option_item = dict(base_mc, stem="fine", opts={"A": "fine", "B": "line one\nline two", "C": "ok"})
    if gift.unexpressible_field(option_item) != "option B":
        fail("an option carrying a line break was not named 'option B': %r" %
             gift.unexpressible_field(option_item))
    errors, warnings = [], []
    if gift.gift_item(option_item, errors, warnings) is not None:
        fail("gift_item rendered an item with an unescapable option")
    if not any("option B" in e for e in errors):
        fail("gift_item's refusal for an unescapable option does not name it: %r" % errors)

    row_item = {"type": "table", "number": 2, "stem": "fine",
                "rows": [{"text": "fine", "cat": "fine"},
                         {"text": "line one\nline two", "cat": "fine"}]}
    if gift.unexpressible_field(row_item) != "row 2":
        fail("a matching row carrying a line break was not named 'row 2': %r" %
             gift.unexpressible_field(row_item))
    errors, warnings = [], []
    if gift.gift_item(row_item, errors, warnings) is not None:
        fail("gift_item rendered an item with an unescapable matching row")
    if not any("row 2" in e for e in errors):
        fail("gift_item's refusal for an unescapable matching row does not name it: %r" % errors)


def test_partial_export_summary_and_exit_code():
    """A bank with one skipped item prints the exported-and-skipped summary and
    exits 1; a bank with nothing skipped prints the all-clear line and exits 0 --
    the two must never be confused, by a script or by a reader.
    """
    tmp = tempfile.mkdtemp()
    partial_out = os.path.join(tmp, "partial.gift")
    r = subprocess.run([sys.executable, ITEMBANK, "export", SAMPLE_BANK, partial_out,
                        "--format", "gift"], capture_output=True, text=True, encoding="utf-8")
    combined = r.stdout + r.stderr
    if r.returncode != 1:
        fail("exporting sample_bank.md (one build item) exited %d, expected 1: %s"
             % (r.returncode, combined))
    if "5 items exported, 1 skipped" not in combined:
        fail("partial-export summary missing expected counts: %r" % combined)
    if partial_out not in combined:
        fail("partial-export summary does not name the output path: %r" % combined)
    if "%d items ->" % 6 in combined:
        fail("a partial export also printed the all-clear line: %r" % combined)

    no_build_path = os.path.join(tmp, "no_build_bank.md")
    open(no_build_path, "w", encoding="utf-8").write(NO_BUILD_BANK)
    clean_out = os.path.join(tmp, "clean.gift")
    r2 = subprocess.run([sys.executable, ITEMBANK, "export", no_build_path, clean_out,
                         "--format", "gift"], capture_output=True, text=True, encoding="utf-8")
    combined2 = r2.stdout + r2.stderr
    if r2.returncode != 0:
        fail("exporting a bank with no build item exited %d, expected 0: %s"
             % (r2.returncode, combined2))
    if "2 items ->" not in combined2:
        fail("all-clear export did not print the plain success line: %r" % combined2)
    if "skipped" in combined2 or "error" in combined2.lower():
        fail("all-clear export printed error rows or a skipped summary: %r" % combined2)
    shutil.rmtree(tmp, ignore_errors=True)


def test_all_build_bank_exports_nothing_loudly():
    """A bank whose every item is `build` writes an empty GIFT document, prints one
    row per item, names zero exported and every item skipped, and exits 1 -- the
    zero-one-many check at its top end.
    """
    qs = load(BUILD_ONLY_BANK)
    n = len(qs)
    if n < 10:
        fail("gift_build_only_bank.md has only %d items, need 10 or more" % n)

    tmp = tempfile.mkdtemp()
    out = os.path.join(tmp, "none.gift")
    r = subprocess.run([sys.executable, ITEMBANK, "export", BUILD_ONLY_BANK, out,
                        "--format", "gift"], capture_output=True, text=True, encoding="utf-8")
    combined = r.stdout + r.stderr
    if r.returncode != 1:
        fail("exporting an all-build bank exited %d, expected 1: %s" % (r.returncode, combined))
    content = open(out, encoding="utf-8").read()
    if "::" in content:
        fail("an all-build export wrote a question name into the file: %r" % content)
    for q in qs:
        tag = "Q%d" % q["number"]
        if tag not in combined:
            fail("no console row names %s in an all-build export: %r" % (tag, combined))
    if "%d items exported, %d skipped" % (0, n) not in combined:
        fail("all-build export summary does not name zero exported and %d skipped: %r"
             % (n, combined))
    row_shapes = set()
    for line in combined.splitlines():
        if line.startswith(gift.GIFT_TYPE_UNSUPPORTED):
            row_shapes.add(re.sub(r"Q\d+", "Qn", line))
    if len(row_shapes) != 1:
        fail("build-refusal rows are not identically shaped across the bank: %r" % row_shapes)
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    test_every_expressible_type_renders()
    test_every_escape_set_character_is_escaped()
    test_matching_preserves_repeated_categories()
    test_export_is_deterministic()
    test_multi_warns_by_item_number()
    test_no_second_scorer_or_parser()
    test_build_always_fails_by_item_number()
    test_strict_promotes_multi_to_a_failure()
    test_unescapable_field_is_named()
    test_partial_export_summary_and_exit_code()
    test_all_build_bank_exports_nothing_loudly()
    print("GIFT export contract: ok (exact renders for all five expressible types, "
          "every escape-set character escaped, repeated matching categories "
          "preserved, deterministic export, multi divergence warned by item number, "
          "no second scorer or parser, build always refused by item number in both "
          "modes, --strict promotes multi to a per-item failure, unescapable fields "
          "named per field kind, partial and all-skipped exports summarise and exit "
          "distinctly from a complete export)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
