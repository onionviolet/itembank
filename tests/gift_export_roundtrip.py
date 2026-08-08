#!/usr/bin/env python3
"""DEL-08 coverage: asserts exact GIFT output for every expressible item type over
synthetic fixtures, that every character in the escape set is actually escaped in the
rendered document, that a `table`/`dnd` item's repeated categories survive as repeated
`matching` sub-questions, that export is byte-deterministic, that a `multi` item's
scoring-divergence warning names its item number, and that the module carries no
second scorer or parser.

Standard library only, runnable as `python tests/gift_export_roundtrip.py`.
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
ITEMBANK = os.path.join(ROOT, "itembank.py")
SAMPLE_BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
ESCAPES_BANK = os.path.join(ROOT, "fixtures", "gift_escapes_bank.md")

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


def main():
    test_every_expressible_type_renders()
    test_every_escape_set_character_is_escaped()
    test_matching_preserves_repeated_categories()
    test_export_is_deterministic()
    test_multi_warns_by_item_number()
    test_no_second_scorer_or_parser()
    print("GIFT export contract: ok (exact renders for all five expressible types, "
          "every escape-set character escaped, repeated matching categories "
          "preserved, deterministic export, multi divergence warned by item number, "
          "no second scorer or parser)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
