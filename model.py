"""The format contract: what a bank is, and what makes one invalid.

Everything here reads markdown and returns plain dicts. It knows nothing about
scoring, sessions or surfaces, which is what lets `spec` and `lint` be the whole
of what an authoring agent has to satisfy.
"""
import collections, hashlib, os, re, sys, uuid


LETTERS = "ABCDEFGH"


# A control character rather than punctuation, for the same reason
# `runtime.FIELD_SEP` is one: option text, table/dnd rows and build steps
# routinely contain commas, pipes and angle brackets, and any printable
# separator eventually collides with content and corrupts the digest. Restated
# here rather than imported, because the model layer reaches into no other
# layer (see `runtime.py`'s own docstring for the architectural rule).
FINGERPRINT_SEP = "\x1f"


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
        r"|\nMODEL:|\nRUBRIC:|\nWHY BEST:|\n\[LESSON-REF)",
        ch, re.S)
    lesson_ref = grab(r"\[LESSON-REF:\s*(.*?)\]", ch)
    common = {
        "id": "q" + number if number else "",
        "number": int(number) if number else 0,
        "type": qtype,
        "stem": stem,
        "difficulty": grab(r"\(difficulty:\s*([^)]+)\)", ch),
        "objective": grab(r"\[OBJECTIVE:\s*(.*?)\]", ch),
        "lesson_ref": lesson_ref,
        "lesson_slug": lesson_slug(lesson_ref) if lesson_ref else "",
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


def collapse(s):
    """Whitespace-collapsed text, case preserved.

    Case is preserved on purpose: a capitalization edit can change what a
    question asks, so it must not be normalized away before hashing.
    """
    return " ".join(str(s or "").split())


def lesson_slug(text):
    """One slugifier for both the lesson lookup key and the rendered HTML
    anchor id (D-03) -- a lookup that agrees with an anchor by coincidence
    eventually disagrees, so there is structurally one call, not two.

    Behaviour: collapse whitespace, lowercase, drop every character outside
    ASCII letters, digits, spaces and hyphens, then replace each run of
    whitespace with a single hyphen and strip leading and trailing hyphens.
    Empty input returns the empty string, and the function is idempotent over
    its own output.

    A heading written entirely in non-ASCII characters therefore reduces to
    the empty string, which collides with any other such heading and is caught
    loudly by plan 03-03's duplicate-heading check rather than fabricated
    into a unique id.
    """
    s = collapse(str(text or "")).lower()
    s = "".join(c for c in s if c.isascii() and (c.isalnum() or c in " -"))
    s = re.sub(r"\s+", "-", s)
    return s.strip("-")


def parse_lesson(bank_path):
    """A second, independent read over the bank file for a different purpose:
    the LESSON section's teaching text. Never called from inside `load()` or
    `parse_bank()`, and it changes neither's return shape.

    Mirrors `parse_bank()`'s boundary rule exactly: iterate every chunk of the
    unbounded split and stop accumulating the moment a chunk both matches
    `Qn.` at its start and parses as a real question. A first-match-only split
    would silently cut a lesson whose prose contains an illustrative line
    shaped like a question marker (03-RESEARCH.md Pitfall 2).

    An optional `[LESSON-SRC: <path>]` in the preamble names an external
    markdown file whose own `## LESSON` section replaces the bank's. The
    directive's path is resolved against the bank file's own directory, and
    anything resolving outside it -- a relative climb, an absolute path, or
    a sibling directory whose name merely starts with the bank's -- is
    refused before any open, on the same absolute-path-plus-separator-suffix
    containment shape `surfaces/migrate.py:scan_legacy()` already proves.
    The refusal and any OS-level read failure are returned as a structured
    dict with `error` set to `lesson.src_unreadable` and `detail` naming the
    reason; the function returns a dict on every path and raises on none
    (T-3-04). An external source wins over an inline `## LESSON` section when
    a bank carries both.

    Returns `None` when the preamble carries no `## LESSON` section; otherwise
    a dict with exactly: `source`, `body`, `intro`, `headings` (each with
    `text`, `slug`, `body`, in document order) and `error`/`detail`, both the
    empty string in this plan -- plan 03-02 is the only plan that ever sets
    `error`, and declaring the keys now keeps that addition one branch in the
    loader and nothing in the parser (D-02).
    """
    text = open(bank_path, encoding="utf-8").read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and parse_question(ch) is not None:
            break
        preamble.append(ch)
    head = "".join(preamble)

    # The one branch in the loader (D-02): an external source replaces the
    # bank's own preamble text before the section match, so everything after
    # this point -- the section search, the heading walk, the returned key
    # set -- runs unchanged over one string whether the lesson came from the
    # bank file or from a shared file. The refusal is decided from the
    # resolved path alone, never from the result of a read (T-3-02).
    source = os.path.abspath(bank_path)
    src = grab(r"(?m)^\[LESSON-SRC:\s*(.*?)\s*\]", head)
    if src:
        bank_dir = os.path.dirname(source) or "."
        resolved = os.path.abspath(os.path.join(bank_dir, src))
        if resolved != bank_dir and not resolved.startswith(bank_dir + os.sep):
            return {"source": source, "body": "", "intro": "", "headings": [],
                    "error": "lesson.src_unreadable",
                    "detail": "%s escapes the bank's directory" % src}
        try:
            head = open(resolved, encoding="utf-8").read()
        except OSError as exc:
            return {"source": source, "body": "", "intro": "", "headings": [],
                    "error": "lesson.src_unreadable", "detail": str(exc)}
        source = resolved

    m = re.search(r"(?m)^##\s+LESSON\s*$", head)
    if m is None:
        return None
    lesson_text = head[m.end():]
    lines = lesson_text.splitlines()
    intro = []
    headings = []
    current = None
    for line in lines:
        hm = re.match(r"^###\s+(.+?)\s*$", line)
        if hm:
            if current is not None:
                headings.append(current)
            current = {"text": hm.group(1).strip(),
                       "slug": lesson_slug(hm.group(1)), "body": []}
        elif current is None:
            intro.append(line)
        else:
            current["body"].append(line)
    if current is not None:
        headings.append(current)
    for h in headings:
        h["body"] = "\n".join(h["body"]).strip()
    return {"source": source,
            "body": lesson_text.strip(),
            "intro": "\n".join(intro).strip(),
            "headings": headings,
            "error": "",
            "detail": ""}


def content_fingerprint(q):
    """A change-detection digest of the *tested* content only, never the
    rationale around it.

    Deliberately excludes `why`, `disc`, `second`, `trap`, `conf`, `da`,
    `notes`, `objective`, `difficulty`, `number`, `id`, `item_id` and
    `content_hash` -- the hash's job is to detect that stem, options, correct
    answers, categories, rows, steps, model answer or rubric changed, and
    D-04 already accepts the residual risk that a genuine rewrite of what a
    question asks, while its rationale text stays untouched, still inherits
    the old item's trend data. The drift warning this feeds is the only
    signal for that case.

    This digest is an integrity check, not a security boundary: this project
    has one local user and no adversary in its threat model.
    """
    t = q["type"]
    parts = ["type=" + t, "stem=" + collapse(q["stem"])]
    if t in ("mc", "multi"):
        for L in sorted(q["opts"]):
            parts.append("opt:%s=%s" % (L, collapse(q["opts"][L])))
        parts.append("correct=" + ",".join(sorted(q["correct"])))
        parts.append("select=%d" % q["select"])
    elif t in ("table", "dnd"):
        parts.append("cats=" + "|".join(q["cats"]))
        for i, r in enumerate(q["rows"]):
            parts.append("row:%d=%s::%s" % (i, collapse(r["text"]), r["cat"]))
    elif t == "build":
        for i, s in enumerate(q["steps"]):
            parts.append("step:%d=%s" % (i, collapse(s)))
    elif t == "short":
        parts.append("model=" + collapse(q["model"]))
        for i, r in enumerate(q["rubric"]):
            parts.append("rubric:%d=%s" % (i, collapse(r)))
    payload = FINGERPRINT_SEP.join(parts)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def new_item_id():
    """A 64-bit-random opaque id, short enough to read in an `[ID:]` line.

    An accidental collision across a personal bank is negligible, and D-05
    makes these globally unique across every bank a caller assigns into
    together, so renaming or splitting a bank file cannot orphan an item's
    evidence history.
    """
    return uuid.uuid4().hex[:16]


TERMINATOR = re.compile(
    r"(?m)^(?:\[TYPE:|\[OBJECTIVE:|\[SELECT:|\[CATEGORIES:|[A-H]\)|ROW\)|ITEM\)|"
    r"STEP\)|MODEL:|RUBRIC:|WHY BEST:)")


def assign_ids(text, taken=None):
    """Pure text transform: mint a missing `[ID:]` and record or refresh
    `[HASH:]` for every question block in `text`. Returns `(new_text,
    changes)` and touches no file -- `surfaces/evidence_cli.py:cmd_id_assign`
    is the only writer, so `lint` stays read-only (D-03).

    `taken` is a set of ids already claimed elsewhere -- a caller assigning
    across several banks in one pass adds each minted id to it, so D-05's
    global uniqueness holds across the whole pass, not just within one bank.

    A block whose id and hash are both already current is passed through
    unchanged, so a no-change run returns `new_text == text` byte for byte: a
    transform that reformats a file it did not need to touch is a transform
    nobody will run on a real bank.
    """
    if taken is None:
        taken = set()
    changes = []
    out_chunks = []
    idx = 0
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if not re.match(r"Q\d+\.", ch.strip()):
            out_chunks.append(ch)
            continue
        q = parse_question(ch)
        if q is None:
            out_chunks.append(ch)
            continue
        idx += 1
        tag = "Q%d" % idx

        had_id = q.get("item_id", "")
        item_id = had_id
        id_action = "kept"
        if not item_id:
            item_id = new_item_id()
            while item_id in taken:
                item_id = new_item_id()
            id_action = "assigned"
        taken.add(item_id)

        old_hash = q.get("content_hash", "")
        new_hash = content_fingerprint(q)
        if not old_hash:
            hash_action = "recorded"
        elif old_hash != new_hash:
            hash_action = "updated"
        else:
            hash_action = "unchanged"

        changes.append({"item": tag, "item_id": item_id, "action": id_action,
                        "hash_action": hash_action, "old_hash": old_hash,
                        "new_hash": new_hash})

        if id_action == "kept" and hash_action == "unchanged":
            out_chunks.append(ch)
            continue

        chunk = ch
        if had_id:
            chunk = re.sub(r"(?m)^\[ID:\s*\S+\s*\]", "[ID: %s]" % item_id, chunk, count=1)
        if old_hash:
            chunk = re.sub(r"(?m)^\[HASH:\s*\S+\s*\]", "[HASH: %s]" % new_hash, chunk, count=1)

        to_insert = []
        if not had_id:
            to_insert.append("[ID: %s]" % item_id)
        if not old_hash:
            to_insert.append("[HASH: %s]" % new_hash)
        if to_insert:
            insert_text = "\n".join(to_insert) + "\n"
            m = TERMINATOR.search(chunk)
            if m:
                chunk = chunk[:m.start()] + insert_text + chunk[m.start():]
            else:
                if not chunk.endswith("\n"):
                    chunk += "\n"
                chunk += insert_text

        out_chunks.append(chunk)
    new_text = "".join(out_chunks)
    return new_text, changes


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
  [LESSON-REF: <heading text>]                               optional, links to a lesson heading
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

THE LESSON SECTION
  A bank may carry one optional LESSON section: the teaching text its items
  test. It lives above the first question, opened by `## LESSON` at the start
  of a line and running to the first `Qn.` line that parses as a real question;
  its subheadings are one level deeper, `### heading text`, and each becomes a
  section an item can point at.

  A bank without a lesson section parses exactly as it did before this
  grammar existed, so adding a lesson to a real bank cannot break it.

  [LESSON-SRC: <path>]                                      optional, external source
  The same preamble region may name an external markdown file whose own
  `## LESSON` section replaces the bank's. A path in that directive is
  resolved relative to the bank file; a path resolving outside the bank's
  own directory is refused rather than read: a bank should not be able to
  name an arbitrary file on the machine. When a bank carries both an inline
  section and an external directive, the external source takes precedence.

  An item's [LESSON-REF:] tag names readable heading text, not an id, and one
  item carries at most one reference; the tag itself is listed above with the
  other shared fields.

THE SLUG RULE
  A heading's slug is its text lowercased, whitespace collapsed, punctuation
  dropped. Two headings whose slugs collide make a reference to either
  ambiguous, so the collision is an error: author headings that differ in
  more than casing, spacing and punctuation, and you can predict the collision
  before the linter reports it.

WHAT THE READER RENDERS
  The lesson reader renders headings, paragraphs, bullet and numbered lists,
  pipe tables, inline code, fenced code, bold, italic and links -- nothing
  else. Any other markdown construct appears as literal text, so write plain
  prose and let that list be the whole toolbox.

  A fenced block's info string (```python, ```math) names the block's
  language. Nothing acts on it yet; a later phase attaches maths rendering
  and a run button to it by name, so the info string is worth writing
  correctly even though nothing acts on it today.

ONE CONSTRAINT
  A line inside lesson prose that begins like a question marker -- `Q1.` at
  the start of a line -- ends the lesson only when it parses as a real question;
  a line merely shaped like one stays in the prose. This is a property of
  the boundary that separates questions from prose, and the context-sensitivity
  is deliberate: a first-match-only boundary would silently cut a lesson
  whose prose contains an illustrative line shaped like a question marker.

LESSON LINT CODES
  item.lesson_ref_unknown   error     an item's LESSON-REF names no heading
  lesson.duplicate_heading  error     two headings slug-collide
  lesson.src_unreadable     error     LESSON-SRC names a missing or out-of-tree
                                      file
  lesson.orphan_heading     warning   a heading no item references; a lesson
                                      legitimately teaches more than it tests
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


# The sentinel default of `lint()`'s lesson parameter. It distinguishes "the
# caller did not supply lesson data" (skip every lesson check -- the behaviour
# every pre-03-03 caller relies on) from "the caller supplied lesson data and
# this bank has no lesson section", because those two demand opposite
# behaviour and `parse_lesson()` legitimately returns None for the second: a
# reference into a bank with no lesson is an error, not a skipped check
# (D-05). A caller that wants the checks passes whatever `parse_lesson()`
# returned, including its no-section result.
LESSON_UNCHECKED = object()


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
    "item.missing_id", "item.duplicate_id", "item.missing_hash",
    "item.content_drift", "item.objective_unnamespaced", "item.lesson_ref_unknown",
    "lesson.duplicate_heading", "lesson.orphan_heading", "lesson.src_unreadable",
    "bank.answer_position_skew",
}))


def lint(questions, lesson=LESSON_UNCHECKED):
    """Return (errors, warnings) as lists of LintError records.

    str(record) reproduces the historical 'Qn: message' text exactly; the code and
    field are additive machine-readable fields an authoring agent can branch on
    without a lookup table.

    `lesson` defaults to the LESSON_UNCHECKED sentinel, which turns every lesson
    check off: a caller that never heard of lessons gets byte-for-byte what it got
    before this parameter existed. A caller that supplies lesson data passes
    whatever `parse_lesson()` returned -- a dict of headings (the checks below
    run), None for a bank with no `## LESSON` section (every non-empty
    LESSON-REF is unknown, D-05), or a dict carrying an unreadable-source error
    (lesson.src_unreadable, no heading-level findings).
    """
    errors, warnings = [], []
    seen_stems = {}
    seen_ids = {}
    seen_item_ids = {}
    letter_hits = collections.Counter()
    lesson_on = lesson is not LESSON_UNCHECKED
    if lesson_on:
        known_slugs = set()
        if lesson:
            known_slugs = {h["slug"] for h in lesson["headings"]}

    for idx, q in enumerate(questions, 1):
        tag = "Q%d" % idx
        t = q["type"]

        if q.get("id") in seen_ids:
            errors.append(LintError("item.duplicate_number", "id", tag,
                          "duplicate question number %s (also %s)" %
                          (q["id"], seen_ids[q["id"]])))
        seen_ids[q.get("id")] = tag

        item_id = q.get("item_id", "")
        if not item_id:
            warnings.append(LintError("item.missing_id", "item_id", tag,
                            "no [ID:] line; run `itembank id-assign` before evidence is "
                            "recorded against this item"))
        else:
            if item_id in seen_item_ids:
                errors.append(LintError("item.duplicate_id", "item_id", tag,
                              "duplicate item id %s (also %s)" %
                              (item_id, seen_item_ids[item_id])))
            seen_item_ids[item_id] = tag
            content_hash = q.get("content_hash", "")
            if not content_hash:
                warnings.append(LintError("item.missing_hash", "content_hash", tag,
                                "carries [ID:] but no [HASH:]; run `itembank id-assign` to "
                                "record its fingerprint"))
            else:
                current_hash = content_fingerprint(q)
                if content_hash != current_hash:
                    warnings.append(LintError("item.content_drift", "content_hash", tag,
                                    "content changed since [HASH:] was recorded (recorded "
                                    "%s, now %s); evidence stays attached — run `itembank "
                                    "id-assign` to update the fingerprint" %
                                    (content_hash, current_hash)))

        objective = q.get("objective") or ""
        if objective and ":" not in objective:
            warnings.append(LintError("item.objective_unnamespaced", "objective", tag,
                            "OBJECTIVE %r has no subject prefix; use subject:path (for "
                            "example emt:airway.opa) so two subjects cannot average into "
                            "one trend line" % objective))

        # The per-item lesson check lives inside this loop so the finding is
        # tagged by the item's own number for free (D-05, ROADMAP SC3); a
        # second pass would have to re-derive the numbering. A bank with no
        # lesson section at all (lesson is None) has an empty known-slug set,
        # so every non-empty reference is unknown rather than silently skipped.
        if lesson_on:
            ref = q.get("lesson_ref") or ""
            if ref and lesson_slug(ref) not in known_slugs:
                errors.append(LintError(
                    "item.lesson_ref_unknown", "lesson_ref", tag,
                    "LESSON-REF '%s' does not match any lesson heading" % ref))

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

    # Bank-level lesson findings, in document order for the headings so two
    # runs over the same bank produce byte-identical output. An unreadable
    # external source has no headings to check, so it produces only its own
    # finding. lint() has no bank text of its own -- the lesson dict is the
    # whole contract -- so the locked template's <path> is recovered from the
    # structured detail parse_lesson() returned (the escape refusal embeds the
    # authored directive; an OS error quotes the resolved file), matching
    # T-3-09's echo-the-authored-path intent without fabricating data.
    if lesson_on:
        if lesson and lesson.get("error"):
            detail = lesson.get("detail") or ""
            src_match = re.match(r"(.+?) escapes the bank's directory$", detail)
            if src_match:
                src_path = src_match.group(1)
            else:
                quoted = re.findall(r"'([^']*)'", detail)
                # An OS error quotes the resolved path; echo only its basename
                # so the message never discloses an absolute path the bank file
                # does not already contain (T-3-09).
                src_path = os.path.basename(quoted[-1]) if quoted else ""
            errors.append(LintError(
                "lesson.src_unreadable", "src", "BANK",
                "[LESSON-SRC: %s] could not be read (%s) -- fix the path or "
                "remove the directive" % (src_path, detail)))
        elif lesson:
            referenced = {lesson_slug(q["lesson_ref"]) for q in questions
                          if (q.get("lesson_ref") or "")}
            seen_slugs = {}
            for h in lesson["headings"]:
                slug = h["slug"]
                if slug in seen_slugs:
                    errors.append(LintError(
                        "lesson.duplicate_heading", "headings", "BANK",
                        "lesson heading '%s' collides with '%s' after "
                        "slugifying to '%s' -- rename one"
                        % (h["text"], seen_slugs[slug], slug)))
                else:
                    seen_slugs[slug] = h["text"]
            for h in lesson["headings"]:
                if h["slug"] not in referenced:
                    warnings.append(LintError(
                        "lesson.orphan_heading", "headings", "BANK",
                        "lesson heading '%s' is not referenced by any item's "
                        "[LESSON-REF:] -- fine if it's background reading, but "
                        "check it wasn't meant to be tested" % h["text"]))
    return errors, warnings


def load(path):
    qs = parse_bank(open(path, encoding="utf-8").read())
    if not qs:
        sys.exit("No question blocks found in %s. Run `itembank spec` for the format." % path)
    return qs
