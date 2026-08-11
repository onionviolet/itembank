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

# A field that still carries a line break or carriage return after escaping
# cannot be written into a GIFT answer block -- GIFT's own grammar is
# line-oriented and no backslash escape rescues an embedded newline.
UNSAFE_NEWLINE = re.compile(r"[\r\n]")

# The published dotted error-code namespace (D-06 precedent, extending
# `model.LINT_CODES`/`settings.SETTINGS_CODES`). Built from a set-then-sorted
# tuple so sortedness is structural rather than maintained by eye.
GIFT_TYPE_UNSUPPORTED = "gift.type_unsupported"
GIFT_FIELD_UNESCAPABLE = "gift.field_unescapable"
GIFT_STRICT_DIVERGENCE = "gift.strict_divergence"

GIFT_CODES = tuple(sorted({
    GIFT_TYPE_UNSUPPORTED, GIFT_FIELD_UNESCAPABLE, GIFT_STRICT_DIVERGENCE,
}))

# The one sentence describing the `multi` scoring divergence, shared between
# the default-mode warning (item still exported) and the `--strict` failure
# (item refused) -- the two modes differ only in whether the item is written
# and which list the message lands in, never in what they say diverges.
MULTI_DIVERGENCE = (
    "type 'multi' exported as GIFT weighted-answer choices -- a learner "
    "selecting only some of the correct options may score partial credit "
    "in the LMS, where itembank's own scorer would mark it wrong.")


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


def unexpressible_field(q):
    """Return the name of the first field this item carries that GIFT
    cannot safely write, or `None` when every field is fine.

    A field is unexpressible once its text still carries a line break or a
    carriage return -- GIFT's answer blocks are line-oriented and no
    backslash escape rescues an embedded newline. Fields are named the way
    an author would recognise them: the stem, an option by its letter, a
    matching row by its position, the category, the short model answer, the
    general feedback -- not a single generic label, so the refusal points at
    exactly the field to fix.
    """
    def bad(text):
        return bool(text) and UNSAFE_NEWLINE.search(text)

    if bad(q.get("stem")):
        return "stem"
    t = q["type"]
    if t in ("mc", "multi"):
        for L in sorted(q.get("opts") or {}):
            fb = (q.get("da") or {}).get(L)
            if bad(q["opts"][L]) or bad(fb):
                return "option %s" % L
        if bad(q.get("why")):
            return "general feedback"
    elif t in ("table", "dnd"):
        for i, r in enumerate(q.get("rows") or [], 1):
            if bad(r.get("text")):
                return "row %d" % i
            if bad(r.get("cat")):
                return "category"
    elif t == "short":
        if bad(q.get("model")):
            return "model answer"
    return None


def gift_item(q, errors, warnings, strict=False):
    """Dispatch one item to its renderer, or record why it could not be
    rendered. `errors` and `warnings` are accumulated into, following
    `model.lint()`'s house convention, rather than raised.

    Two refusals run before any renderer is reached, in both modes alike.
    `build` (ordering) has no GIFT equivalent at all (D-02) -- no flag makes
    it exportable. An item whose escaped field still carries a line break is
    refused by field name rather than written into a shape GIFT would
    misparse. Only after both pass does `strict` get a say: it promotes a
    `multi` item's scoring-divergence warning to a per-item failure instead
    of changing what is checked.
    """
    t = q["type"]
    if t == "build":
        errors.append(
            "%s: Q%d: type 'build' (ordering) has no GIFT equivalent -- "
            "not exported" % (GIFT_TYPE_UNSUPPORTED, q["number"]))
        return None
    if t == "visual":
        # D-09 (plan 06.1-03): a plot/number-line visual item cannot be
        # represented losslessly in GIFT -- approximating it as numeric,
        # matching, embedded markup, or prose would change what is being
        # assessed. Refuse by original item number with the stable
        # gift.type_unsupported code in both default and strict modes, before
        # any field scan or renderer runs, and never approximate.
        errors.append(
            "%s: Q%d: type 'visual' (interactive plot/number-line) has no "
            "GIFT equivalent -- not exported" %
            (GIFT_TYPE_UNSUPPORTED, q["number"]))
        return None
    field = unexpressible_field(q)
    if field is not None:
        errors.append(
            "%s: Q%d: %s contains a character sequence GIFT export cannot "
            "safely escape -- not exported" %
            (GIFT_FIELD_UNESCAPABLE, q["number"], field))
        return None
    if t == "mc":
        return gift_mc(q)
    if t == "multi":
        if strict:
            errors.append(
                "%s: Q%d: %s -- not exported" %
                (GIFT_STRICT_DIVERGENCE, q["number"], MULTI_DIVERGENCE))
            return None
        warnings.append(
            "Q%d: %s Export kept; verify against your LMS if this "
            "matters." % (q["number"], MULTI_DIVERGENCE))
        return gift_multi(q)
    if t in ("table", "dnd"):
        return gift_matching(q)
    if t == "short":
        return gift_short(q)
    errors.append("%s: Q%d: type %r has no GIFT equivalent -- not exported" %
                   (GIFT_TYPE_UNSUPPORTED, q["number"], t))
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


def export_gift(a):
    """The GIFT branch of `itembank export`, reached from
    `anki.cmd_export` when `--format gift` is given. Same load-then-gate-
    then-transform-then-status-line shape as the existing Anki export, so
    GIFT export reads as the same family of command, not a differently-
    voiced new feature.
    """
    qs = load(a.bank)
    errors, _ = lint(qs)
    if errors and not a.force:
        sys.exit("refusing to export a bank with errors; fix them or pass --force")
    document, gift_errors, gift_warnings = render_gift(qs, strict=getattr(a, "strict", False))
    for w in gift_warnings:
        print(w)
    for e in gift_errors:
        print(e)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    content = (document + "\n") if document else ""
    open(a.out, "w", encoding="utf-8").write(content)
    skipped = len(gift_errors)
    exported = len(qs) - skipped
    if skipped:
        print("%d items exported, %d skipped (see above) -> %s" % (exported, skipped, a.out))
        return 1
    print("%d items -> %s" % (exported, a.out))
    return 0
