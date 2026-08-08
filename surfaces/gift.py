"""GIFT export: a second interoperability format alongside Anki TSV.

Reads item dicts returned by `model.load()` and writes a plain-text GIFT
document a real LMS (Moodle and compatible importers) can read. This module
is a read-side transform: it reaches no verdict of its own. Where GIFT's own
grading model disagrees with the runtime's own scorer -- the `multi`
weighted-answer partial-credit divergence being the one known case -- that
disagreement is reported to the operator, never reconciled by a second
scorer written here.
"""
import os, re, sys

from model import lint, load


# GIFT's escape set: tilde, equals, hash, opening/closing brace, colon, and
# backslash. Every user-authored field in every renderer routes through
# `gift_escape()` -- a bank author writing "between 50% and 60%" or "A ~ B"
# in a stem corrupts the exported file if a single field is missed, and one
# function is the only way to be sure none is.
GIFT_ESCAPE = re.compile(r"([~=#{}:\\])")


def gift_escape(text):
    if not text:
        return ""
    return GIFT_ESCAPE.sub(r"\\\1", text)


def gift_name(q):
    """The GIFT question name: the item's own number, in the same `Q%d`
    shape `model.lint()` already uses for its per-item messages, wrapped in
    the double-colon name delimiters -- so a `Q<n>` in a console error line
    and a `::Q<n>::` in the exported file name the same item.
    """
    return "::Q%d::" % q["number"]


def gift_weight(w):
    """A GIFT percentage weight, five decimal places then trimmed.

    An unspecified float repr is what makes two exports of the same bank
    differ. Formatting at `%.5f` and then stripping trailing zeros (and a
    bare trailing point) gives a clean whole number for two correct options
    and an identical, deterministically truncated value for three, on every
    run.
    """
    s = "%.5f" % w
    s = s.rstrip("0").rstrip(".")
    return s


def gift_mc(q):
    lines = ["%s %s {" % (gift_name(q), gift_escape(q["stem"]))]
    for L in sorted(q["opts"]):
        marker = "=" if L in q["correct"] else "~"
        line = "%s%s" % (marker, gift_escape(q["opts"][L]))
        fb = (q.get("da") or {}).get(L)
        if fb:
            line += " # " + gift_escape(fb)
        lines.append(line)
    if q.get("why"):
        lines.append("#### " + gift_escape(q["why"]))
    lines.append("}")
    return "\n".join(lines)


def gift_multi(q):
    """Pick-N via GIFT's weighted-answer encoding: every option carries a
    percentage weight rather than a bare =/~ marker, because GIFT has no
    other way to express "select exactly N of these." Each correct option
    carries a positive weight of 100 divided by the number of correct
    options; each incorrect option carries -100.
    """
    lines = ["%s %s {" % (gift_name(q), gift_escape(q["stem"]))]
    n_correct = len(q["correct"]) or 1
    pos = gift_weight(100.0 / n_correct)
    neg = gift_weight(-100.0)
    for L in sorted(q["opts"]):
        w = pos if L in q["correct"] else neg
        line = "~%%%s%%%s" % (w, gift_escape(q["opts"][L]))
        fb = (q.get("da") or {}).get(L)
        if fb:
            line += " # " + gift_escape(fb)
        lines.append(line)
    if q.get("why"):
        lines.append("#### " + gift_escape(q["why"]))
    lines.append("}")
    return "\n".join(lines)


def gift_matching(q):
    """`table`/`dnd` as GIFT `matching`: one sub-question per row, in row
    order. Repeated right-hand category values across rows are correct and
    expected -- GIFT `matching` accepts them, and that is precisely what
    makes it a structural fit for itembank's categorise-rows-into-buckets
    shape. Rows are never deduplicated, never sorted, never merged.
    """
    lines = ["%s %s {" % (gift_name(q), gift_escape(q["stem"]))]
    for r in q["rows"]:
        lines.append("=%s -> %s" % (gift_escape(r["text"]), gift_escape(r["cat"])))
    lines.append("}")
    return "\n".join(lines)


def gift_short(q):
    return "%s %s {=%s}" % (gift_name(q), gift_escape(q["stem"]),
                             gift_escape(q.get("model", "")))


def gift_item(q, errors, warnings, strict=False):
    """Dispatch one item to its renderer, or record why it could not be
    rendered. `errors` and `warnings` are accumulated into, following
    `model.lint()`'s house convention, rather than raised.
    """
    t = q["type"]
    if t == "mc":
        return gift_mc(q)
    if t == "multi":
        return gift_multi(q)
    if t in ("table", "dnd"):
        return gift_matching(q)
    if t == "short":
        return gift_short(q)
    errors.append("Q%d: type %r has no GIFT equivalent -- not exported" % (q["number"], t))
    return None


def render_gift(qs, strict=False):
    """Assemble the whole GIFT document in memory and hand it back -- never
    written here. That is what makes an item that fails mid-transform abort
    before any output file exists: a caller only opens a file after this
    function has already returned.
    """
    errors, warnings = [], []
    blocks = []
    for q in qs:
        block = gift_item(q, errors, warnings, strict=strict)
        if block is not None:
            blocks.append(block)
    return "\n\n".join(blocks), errors, warnings
