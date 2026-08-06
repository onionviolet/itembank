"""The format contract: what a bank is, and what makes one invalid.

Everything here reads markdown and returns plain dicts. It knows nothing about
scoring, sessions or surfaces, which is what lets `spec` and `lint` be the whole
of what an authoring agent has to satisfy.
"""
import collections, re, sys


LETTERS = "ABCDEFGH"


def grab(pattern, block, flags=0):
    m = re.search(pattern, block, flags)
    return m.group(1).strip() if m else ""


def parse_bank(text):
    """Split on `Qn.` markers and parse each block into a question dict."""
    questions = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if not re.match(r"Q\d+\.", ch.strip()):
            continue
        q = parse_question(ch)
        if q:
            questions.append(q)
    return questions


def parse_question(ch):
    number = grab(r"Q(\d+)\.", ch)
    qtype = (grab(r"(?m)^\[TYPE:\s*(\w+)\s*\]", ch) or "mc").lower()
    # Stem runs from the Qn. marker to the first structural marker that follows.
    stem = grab(
        r"Q\d+\.\s*(.*?)\s*(?:\(difficulty:|\n\[OBJECTIVE|\n\[TYPE|\n\[SELECT"
        r"|\n\[CATEGORIES|\n\[ID|\n\[HASH|\n[A-H]\)|\nROW\)|\nITEM\)|\nSTEP\)"
        r"|\nMODEL:|\nRUBRIC:|\nWHY BEST:)",
        ch, re.S)
    common = {
        "id": "q" + number if number else "",
        "number": int(number) if number else 0,
        "type": qtype,
        "stem": stem,
        "difficulty": grab(r"\(difficulty:\s*([^)]+)\)", ch),
        "objective": grab(r"\[OBJECTIVE:\s*(.*?)\]", ch),
        "item_id": grab(r"(?m)^\[ID:\s*(\S+)\s*\]", ch),          # empty until id-assign (01-04)
        "content_hash": grab(r"(?m)^\[HASH:\s*(\S+)\s*\]", ch),   # empty until id-assign (01-04)
        "why": section("WHY BEST", ch),
        "disc": section("KEY DISCRIMINATOR", ch),
        "second": section("SECOND-BEST", ch),
        "trap": section("TRAP", ch),
        "conf": grab(r"(?m)^CONFIDENCE:\s*(.*?)\s*(?=\n|\Z)", ch),
    }

    if qtype in ("mc", "multi"):
        opts = {}
        for L in LETTERS:
            v = grab(rf"(?m)^{L}\)\s*(.*?)\s*(?=^[A-H]\)|^CORRECT:|\n\n)", ch, re.S)
            if v:
                opts[L] = v
        correct = [c.strip().upper() for c in
                   re.split(r"[,\s]+", grab(r"(?m)^CORRECT:\s*(.*?)\s*$", ch)) if c.strip()]
        correct = [c for c in correct if c in LETTERS]
        if not (stem and opts and correct):
            return None
        da = {}
        for L in LETTERS:
            da[L] = grab(rf"(?m)^-\s*{L}\)\s*(.*?)\s*(?=^-\s*[A-H]\)|^TRAP:|^CONFIDENCE:|\Z)",
                         ch, re.S)
        sel = grab(r"(?m)^\[SELECT:\s*(\d+)\s*\]", ch)
        common.update({
            "opts": opts, "correct": correct, "da": da,
            "select": int(sel) if sel else len(correct),
        })
        return common

    if qtype in ("table", "dnd"):
        cats = [c.strip() for c in grab(r"(?m)^\[CATEGORIES:\s*(.*?)\s*\]", ch).split("|") if c.strip()]
        marker = "ROW" if qtype == "table" else "ITEM"
        rows = []
        for line in re.findall(rf"(?m)^{marker}\)\s*(.+?)\s*$", ch):
            if "::" not in line:
                continue
            t, c = line.rsplit("::", 1)
            rows.append({"text": t.strip(), "cat": c.strip()})
        if not (stem and cats and rows):
            return None
        common.update({"cats": cats, "rows": rows, "notes": notes(ch)})
        return common

    if qtype == "build":
        steps = [s.strip() for s in re.findall(r"(?m)^STEP\)\s*(.+?)\s*$", ch)]
        if not (stem and len(steps) > 1):
            return None
        common.update({"steps": steps, "notes": notes(ch)})
        return common

    if qtype == "short":
        # Constructed response. Nothing here is machine-gradable by design: the
        # rubric is for whoever marks it, and RUBRIC points are what they mark
        # against, so "wrote something plausible" cannot pass as understanding.
        model = section("MODEL", ch)
        rubric = [b.strip() for b in re.findall(
            r"(?m)^-\s*(.+?)\s*$",
            grab(r"(?m)^RUBRIC:\s*(.*?)\s*(?=^[A-Z][A-Z \-]+:|\Z)", ch, re.S))]
        if not stem:
            return None
        common.update({"model": model, "rubric": rubric, "notes": notes(ch)})
        return common

    return None


def section(label, ch):
    return grab(rf"(?m)^{label}:\s*(.*?)\s*(?=\n[A-Z][A-Z \-]+:|\nDISTRACTOR|\Z)", ch, re.S)


def notes(ch):
    """Free-form bullets under DISTRACTOR ANALYSIS, for the non-lettered types."""
    blk = grab(r"(?m)^DISTRACTOR ANALYSIS:\s*(.*?)\s*(?=^TRAP:|^CONFIDENCE:|\Z)", ch, re.S)
    return [b.strip() for b in re.findall(r"(?m)^-\s*(.+?)\s*$", blk)]


SPEC = r"""itembank format contract
=========================

A bank is a markdown file. Everything that is not a question block is ignored,
so a bank can live inside a larger document with prose around it.

A question block starts at `Qn.` at the beginning of a line and runs to the next
one. Options A through H are supported.

SHARED FIELDS (all types)
  Qn. <stem>   (difficulty: recall|application|analysis)     difficulty optional
  [OBJECTIVE: <syllabus or blueprint reference>]             optional
  [ID: <opaque item id>]                                     optional, machine-assigned
  [HASH: sha256:<digest>]                                    optional, machine-assigned
  WHY BEST:            why the keyed answer is correct
  KEY DISCRIMINATOR:   the one distinction the item turns on
  SECOND-BEST:         the runner-up, and what would make it win
  DISTRACTOR ANALYSIS: see below
  TRAP:                the misconception this item weaponises
  CONFIDENCE:          high | medium | low

  [ID:] and [HASH:] are both optional; a bank without them parses exactly as it
  did before these fields existed. [ID:] is assigned once by `itembank id-assign`
  and is never edited by hand. [HASH:] is a fingerprint of the tested content,
  used only to detect that an item changed. The ID is what evidence is recorded
  against, so deleting it orphans that item's history.

THE FIVE ITEM TYPES

1. Multiple choice.  Default. No TYPE line needed.
     A) ...  B) ...  C) ...  D) ...
     CORRECT: B

2. Multiple response.  Pick a fixed number from five or six.
     [TYPE: multi]
     [SELECT: 3]
     A) ... through F) ...
     CORRECT: A, C, E

3. Options table.  Classify each row into a named category.
     [TYPE: table]
     [CATEGORIES: Online | Offline]
     ROW) A protocol stating when to request backup :: Offline
     ROW) Calling the physician about a refusal :: Online

4. Build list.  Put options into a required order.
   List STEPs in the CORRECT order; the renderer shuffles them for display.
     [TYPE: build]
     STEP) Complete an approved education program
     STEP) Pass the certification examination

5. Drag-and-drop.  Sort items into buckets. Same shape as table, but display
   order is shuffled, because a table implies fixed rows and a sort does not.
     [TYPE: dnd]
     [CATEGORIES: Direct care | Readiness]
     ITEM) Assessing the airway :: Direct care

6. Short answer.  Constructed response, typed in prose. NOT auto-graded, ever:
   the answer is recorded and a human or an AI marks it against RUBRIC later.
   Use it where selecting from options would give the answer away, or where the
   skill being tested is producing the explanation rather than recognising it.
     [TYPE: short]
     MODEL:  the answer a full-credit response contains, compressed
     RUBRIC:
     - one checkable claim the answer must make
     - a second one; two is the minimum, because a single point is a vibe
   No WHY BEST is required on a short item; MODEL replaces it. TRAP still helps
   the marker, because it names the wrong answer that will look confident.

DISTRACTOR ANALYSIS
  For mc and multi, one line per option, keyed by letter:
     - A) why this attracts, and the scenario where it WOULD be correct
     - B) Correct: ...
  For table, build and dnd there are no option letters, so write plain bullets
  about the DISCRIMINATIONS: which row is the trap, what wrong sorting principle
  produces a wrong split, which two rows look different but are the same.

THE RULE THAT SURVIVES EVERY TYPE
  A wrong option must teach a second concept by contrast, so name the scenario
  where it WOULD be correct. Everything else here is syntax; this is the part
  worth protecting, and it is the first thing a model drops under length
  pressure. `itembank lint` warns when a distractor line never says it.
"""


BANK_FILE_HINTS = ("_mc_bank", "_exam_bank", "_question_bank", "_quiz_bank")


WOULD_BE = re.compile(
    r"would be|would win|would apply|if the stem|correct when|correct if|"
    r"right for|right when|right if|applies when", re.I)


class LintError(collections.namedtuple("LintError", "code field item message")):
    """One lint finding. `code` is a dotted API namespace an authoring agent branches
    on (D-16) — adding a code is additive, renaming one is a breaking change for every
    consumer. `__str__` reproduces the historical "Qn: message" text exactly, so every
    existing caller (and every CI substring assertion) keeps working unchanged.
    """
    __slots__ = ()

    def __str__(self):
        return "%s: %s" % (self.item, self.message)


# The published code namespace. Adding a code here is additive; renaming or removing
# one is a breaking change for every authoring agent that branches on it (D-16).
# Built from a set-then-sorted so the tuple is provably sorted and duplicate-free
# regardless of the order the codes are written below.
LINT_CODES = tuple(sorted({
    "item.duplicate_number", "item.select_mismatch", "item.correct_unknown_option",
    "item.too_few_options", "item.missing_second_best", "item.distractor_missing",
    "item.distractor_no_would_be", "item.too_few_categories", "item.row_category_unknown",
    "item.too_few_rows", "item.missing_distractor_notes", "item.too_few_steps",
    "item.duplicate_steps", "item.missing_model", "item.too_few_rubric_points",
    "item.model_too_long", "item.rubric_point_too_long", "item.missing_why_best",
    "item.missing_trap", "item.low_confidence", "item.duplicate_stem",
    "bank.answer_position_skew",
}))


def lint(questions):
    """Return (errors, warnings) as lists of LintError records.

    str(record) reproduces the historical 'Qn: message' text exactly; the code and
    field are additive machine-readable fields an authoring agent can branch on
    without a lookup table.
    """
    errors, warnings = [], []
    seen_stems = {}
    seen_ids = {}
    letter_hits = collections.Counter()

    for idx, q in enumerate(questions, 1):
        tag = "Q%d" % idx
        t = q["type"]

        if q.get("id") in seen_ids:
            errors.append(LintError("item.duplicate_number", "id", tag,
                          "duplicate question number %s (also %s)" %
                          (q["id"], seen_ids[q["id"]])))
        seen_ids[q.get("id")] = tag

        if t in ("mc", "multi"):
            if len(q["correct"]) != q["select"]:
                errors.append(LintError("item.select_mismatch", "select", tag,
                              "SELECT is %d but CORRECT lists %d letters"
                              % (q["select"], len(q["correct"]))))
            for c in q["correct"]:
                if c not in q["opts"]:
                    errors.append(LintError("item.correct_unknown_option", "correct", tag,
                                  "CORRECT names option %s, which does not exist" % c))
            if len(q["opts"]) < 3:
                errors.append(LintError("item.too_few_options", "opts", tag,
                              "only %d options" % len(q["opts"])))
            if t == "mc" and q["correct"]:
                letter_hits[q["correct"][0]] += 1
            if t == "mc" and not q.get("second"):
                warnings.append(LintError("item.missing_second_best", "second", tag,
                                "no SECOND-BEST on a multiple-choice item"))
            for L in sorted(q["opts"]):
                if not q["da"].get(L):
                    warnings.append(LintError("item.distractor_missing", "da", tag,
                                    "option %s has no line in DISTRACTOR ANALYSIS" % L))
            for L in sorted(q["opts"]):
                if L in q["correct"]:
                    continue
                line = q["da"].get(L)
                if line and not WOULD_BE.search(line):
                    warnings.append(LintError("item.distractor_no_would_be", "da", tag,
                                    "distractor %s never says when it WOULD be correct" % L))

        elif t in ("table", "dnd"):
            if len(q["cats"]) < 2:
                errors.append(LintError("item.too_few_categories", "cats", tag,
                              "needs at least two CATEGORIES"))
            for r in q["rows"]:
                if r["cat"] not in q["cats"]:
                    errors.append(LintError("item.row_category_unknown", "rows", tag,
                                  "row assigns category '%s', not in CATEGORIES %s"
                                  % (r["cat"], q["cats"])))
            if len(q["rows"]) < 2:
                errors.append(LintError("item.too_few_rows", "rows", tag,
                              "fewer than two rows"))
            if not q.get("notes"):
                warnings.append(LintError("item.missing_distractor_notes", "notes", tag,
                                "no DISTRACTOR ANALYSIS bullets"))

        elif t == "build":
            if len(q["steps"]) < 2:
                errors.append(LintError("item.too_few_steps", "steps", tag,
                              "build list has fewer than two steps"))
            if len(set(q["steps"])) != len(q["steps"]):
                errors.append(LintError("item.duplicate_steps", "steps", tag,
                              "duplicate steps in build list"))
            if not q.get("notes"):
                warnings.append(LintError("item.missing_distractor_notes", "notes", tag,
                                "no DISTRACTOR ANALYSIS bullets"))

        elif t == "short":
            if not q.get("model"):
                errors.append(LintError("item.missing_model", "model", tag,
                              "short item has no MODEL answer, so nothing can grade it"))
            if len(q.get("rubric") or []) < 2:
                errors.append(LintError("item.too_few_rubric_points", "rubric", tag,
                              "short item needs at least two RUBRIC points; one point is a "
                              "vibe, not a rubric"))
            if len(q.get("model", "").split()) > 80:
                warnings.append(LintError("item.model_too_long", "model", tag,
                                "MODEL answer is %d words. A marker cannot check a wall of "
                                "prose point by point; compress it and push detail into RUBRIC"
                                % len(q["model"].split())))
            for n, r in enumerate(q.get("rubric") or [], 1):
                if len(r.split()) > 25:
                    warnings.append(LintError("item.rubric_point_too_long", "rubric", tag,
                                    "RUBRIC point %d is %d words. A point should be one "
                                    "checkable claim" % (n, len(r.split()))))

        if t != "short" and not q.get("why"):
            errors.append(LintError("item.missing_why_best", "why", tag,
                          "no WHY BEST field"))   # short items key off MODEL instead
        if not q.get("trap"):
            warnings.append(LintError("item.missing_trap", "trap", tag, "no TRAP field"))
        if (q.get("conf") or "").lower().startswith("low"):
            warnings.append(LintError("item.low_confidence", "conf", tag,
                            "CONFIDENCE is low, needs human review before use"))

        key = re.sub(r"\W+", " ", q["stem"].lower()).strip()
        if key and key in seen_stems:
            errors.append(LintError("item.duplicate_stem", "stem", tag,
                          "stem duplicates %s" % seen_stems[key]))
        seen_stems[key] = tag

    total = sum(letter_hits.values())
    if total >= 12:
        top, n = letter_hits.most_common(1)[0]
        if n / total > 0.40:
            warnings.append(LintError(
                "bank.answer_position_skew", "correct", "BANK",
                "%.0f%% of multiple-choice answers are keyed %s (%d/%d). Harmless for "
                "`itembank build`, which reshuffles options on every page load. It matters "
                "only if this bank is consumed by something that does NOT shuffle: a printed "
                "exam, an export, or another tool."
                % (n / total * 100, top, n, total)))
    return errors, warnings


def load(path):
    qs = parse_bank(open(path, encoding="utf-8").read())
    if not qs:
        sys.exit("No question blocks found in %s. Run `itembank spec` for the format." % path)
    return qs
