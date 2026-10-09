"""Lesson and companion-section readers behind the model facade."""
import os, re
from markdown_blocks import (is_separator_row, split_cells)


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
    import model
    s = model.collapse(str(text or "")).lower()
    s = "".join(c for c in s if c.isascii() and (c.isalnum() or c in " -"))
    s = re.sub(r"\s+", "-", s)
    return s.strip("-")


# The three Phase 16A lesson directives, one reader each (D-16A-4, A11Y-02).
# Each returns `(value, raw)`: the value the reader will use, and the text the
# author wrote when that text was refused. A refusal is never an exception
# here, because `parse_lesson` must return a dict on every path; it is a
# fallback plus a `raw` string that `lint` turns into a named finding.


def _lesson_profile(head):
    """`[SEMANTIC-PROFILE: <positive integer>]`, defaulting to
    `SEMANTIC_PROFILE_VERSION`. Anything that is not a decimal positive
    integer falls back and is reported by `lesson.invalid_semantic_profile`."""
    import model
    raw = model.grab(r"(?m)^\[SEMANTIC-PROFILE:\s*(.*?)\s*\]", head)
    if not raw:
        return model.SEMANTIC_PROFILE_VERSION, ""
    if raw.isdigit() and int(raw) > 0:
        return int(raw), ""
    return model.SEMANTIC_PROFILE_VERSION, raw


def _lesson_lang(head):
    """`[LESSON-LANG: <tag>]`, defaulting to `"en"`. The tag is checked for
    being non-empty and nothing more: BCP 47 is an open set.

    A directive that is present but empty is distinguished from an absent one
    by the sentinel `"<empty>"`, because those two cases mean different things
    to an author: one is a document that never asked, and the other is a
    document that asked and said nothing.
    """
    m = re.search(r"(?m)^\[LESSON-LANG:\s*(.*?)\s*\]", head)
    if m is None:
        return "en", ""
    tag = m.group(1).strip()
    if not tag:
        return "en", "<empty>"
    return tag, ""


def _lesson_direction(head):
    """`[LESSON-DIR: <value>]`, defaulting to `"auto"`. A value outside
    `LESSON_DIRECTIONS` falls back and is reported by
    `lesson.invalid_direction`.

    Returns `(value, raw, declared)`. `declared` is True when the directive is
    PRESENT at all, whatever its value, and it is a different fact from the
    value being `"auto"`: `auto` is also the default a lesson that never asked
    receives. The renderer needs that distinction, because per-element
    direction resolution is an explicit opt-in and emitting it on the default
    path would add an attribute to every paragraph of every existing bank
    (plan 16A-08 Task 1 step 2).
    """
    import model
    m = re.search(r"(?m)^\[LESSON-DIR:\s*(.*?)\s*\]", head)
    if m is None:
        return "auto", "", False
    raw = m.group(1).strip()
    if not raw:
        return "auto", "", True
    if raw in model.LESSON_DIRECTIONS:
        return raw, "", True
    return "auto", raw, True


def _lesson_example_order(head):
    """`[EXAMPLE-ORDER: <value> [because <reason>]]`, defaulting to
    `("example-first", "")` (D-16A-6).

    The first whitespace-delimited token is the order value; everything after
    the literal word `because` is the recorded reason CAP-01 requires of an
    override. A value outside `LESSON_EXAMPLE_ORDERS` falls back to
    `"example-first"` and is deliberately NOT a lint code in Phase 16A: a
    fourth code was considered and refused here, so a later reader adding one
    is making that decision rather than discovering it was missing.

    An override carrying no reason is not silently accepted: it keeps its
    `"definition-first"` value so `lint` can see it, and `lint` reports
    `lesson.example_order_no_reason` without suppressing the default check.
    """
    import model
    raw = model.grab(r"(?m)^\[EXAMPLE-ORDER:\s*(.*?)\s*\]", head)
    if not raw:
        return "example-first", ""
    parts = raw.split(None, 1)
    value = parts[0] if parts else ""
    reason = ""
    rest = parts[1] if len(parts) > 1 else ""
    if "because" in rest:
        reason = rest.split("because", 1)[1].strip()
    if value not in model.LESSON_EXAMPLE_ORDERS:
        return "example-first", reason
    return value, reason


def _lesson_pace(head):
    """`[LESSON-PACE: <value>]`, defaulting to `"none"` (plan 16D-01,
    D-16D-2). Copies the `[LESSON-DIR:]` shape: the value is validated at
    lint time and never here, the reader falls back silently, and the
    `_raw` companion holds what the author wrote when it was refused so
    `lesson.invalid_pace` can name the offending text.
    """
    import model
    m = re.search(r"(?m)^\[LESSON-PACE:\s*(.*?)\s*\]", head)
    if m is None:
        return "none", ""
    raw = m.group(1).strip()
    if not raw:
        return "none", "<empty>"
    if raw in model.LESSON_PACE_VALUES:
        return raw, ""
    return "none", raw


# The keys every `parse_lesson` return path carries for the directives
# above (eight for the four 16A directives, plus 16D's pace pair). Held in
# one function so an early return and the success
# return cannot drift apart: every path out of `parse_lesson` returns the same
# key set, which is the discipline the existing `error` and `detail` keys
# already follow.
def _lesson_directive_defaults():
    import model
    return {"semantic_profile": model.SEMANTIC_PROFILE_VERSION,
            "semantic_profile_raw": "",
            "lang": "en", "lang_raw": "",
            "dir": "auto", "dir_raw": "", "dir_declared": False,
            "example_order": "example-first", "example_order_reason": "",
            "pace": "none", "pace_raw": ""}


def parse_lesson_comparison(body):
    """Validate the opt-in Example comparison, without executable content.

    None means absent. An error preserves the complete author's static text.
    Both renderer and lint consume this authority over the callout body.
    """
    lines = body.splitlines()
    if not lines or not lines[0].startswith("[COMPARE:"):
        return None
    match = re.fullmatch(
        r"\[COMPARE: ([0-9]{1,5}),([0-9]{1,5}),([0-9]{1,5}),"
        r"([^\[\]\n,]{1,24})\]", lines[0])
    if match:
        a, b, maximum = map(int, match.groups()[:3])
        unit = match.group(4).strip()
        if (0 <= a <= maximum and 0 <= b <= maximum
                and 1 <= maximum <= 10000 and unit
                and any(x.strip() for x in lines[1:])):
            return {"a": a, "b": b, "max": maximum, "unit": unit,
                    "text": "\n".join(lines[1:])}
    return {"error": (
        "Use [COMPARE: A,B,maximum,unit] with whole numbers from 0 to maximum, "
        "maximum 1 to 10000, a unit up to 24 characters, and a static "
        "explanation on following lines.")}


def parse_lesson_lineplot(body):
    """Validate a finite line scene in an Example, without authored code.

    The three integers are the starting slope, starting intercept and one
    changed intercept. The trusted renderer derives every plotted coordinate.
    The remaining Markdown is the portable teaching explanation.
    """
    lines = body.splitlines()
    if not lines or not lines[0].startswith("[LINEPLOT:"):
        return None
    match = re.fullmatch(r"\[LINEPLOT: (-?[0-9]),(-?[0-9]),(-?[0-9])\]",
                         lines[0])
    if match:
        m, b, changed_b = map(int, match.groups())
        explanation = "\n".join(lines[1:]).strip()
        if (all(-2 <= value <= 2 for value in (m, b, changed_b))
                and changed_b != b and explanation
                and "Prediction:" in explanation
                and "Static explanation:" in explanation
                and "Transfer:" in explanation):
            return {"m": m, "b": b, "changed_b": changed_b,
                    "text": explanation}
    return {"error": (
        "Use [LINEPLOT: slope,intercept,changed-intercept] with integers "
        "from -2 to 2, a different changed intercept, and following static "
        "text containing Prediction:, Static explanation:, and Transfer:.")}


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

    Three additive Phase 16A directives are read from the same effective
    preamble: `[SEMANTIC-PROFILE: <positive integer>]` defaulting to
    `SEMANTIC_PROFILE_VERSION`, `[LESSON-LANG: <tag>]` defaulting to `"en"`,
    and `[LESSON-DIR: <value>]` defaulting to `"auto"`. Like `[GATE:]`, their
    values are validated at lint time and never here, so a malformed directive
    falls back to its default and is reported as a named lint finding rather
    than raising.

    Returns `None` when the preamble carries no `## LESSON` section; otherwise
    a dict with exactly: `source`, `body`, `intro`, `headings` (each with
    `text`, `slug`, `body`, in document order) and `error`/`detail`, both the
    empty string in this plan -- plan 03-02 is the only plan that ever sets
    `error`, and declaring the keys now keeps that addition one branch in the
    loader and nothing in the parser (D-02).
    """
    import model
    with open(bank_path, encoding="utf-8") as source_handle:
        text = source_handle.read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and model.parse_question(ch) is not None:
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
    src = model.grab(r"(?m)^\[LESSON-SRC:\s*(.*?)\s*\]", head)
    if src:
        bank_dir = os.path.dirname(source) or "."
        resolved = os.path.abspath(os.path.join(bank_dir, src))
        if resolved != bank_dir and not resolved.startswith(bank_dir + os.sep):
            early = {"source": source, "body": "", "intro": "",
                     "headings": [], "error": "lesson.src_unreadable",
                     "detail": "%s escapes the bank's directory" % src}
            early.update(_lesson_directive_defaults())
            return early
        try:
            with open(resolved, encoding="utf-8") as source_handle:
                head = source_handle.read()
        except OSError as exc:
            early = {"source": source, "body": "", "intro": "",
                     "headings": [], "error": "lesson.src_unreadable",
                     "detail": str(exc)}
            early.update(_lesson_directive_defaults())
            return early
        source = resolved

    # The Phase 6.2 gate directive (D-02): one [GATE:] in the effective
    # lesson preamble (the bank's own, or the external file's when
    # [LESSON-SRC:] replaced it), following the exact [LESSON-SRC:] grab
    # pattern -- additive grammar, default "recommended" when absent, and
    # the value validated at lint time, never here (a parse must not raise).
    gate = model.grab(r"(?m)^\[GATE:\s*(.*?)\s*\]", head) or "recommended"

    # The Phase 16A directives (D-16A-4, A11Y-02), each copying the [GATE:]
    # shape above exactly: a multiline anchored grab over the effective
    # preamble, a default applied by an `or` expression, and the value
    # validated at lint time and never here. Each keeps a `_raw` companion
    # holding what the author actually wrote when the value was refused, so
    # `lint` can name the offending text instead of reporting that a default
    # was used. An absent directive leaves its `_raw` the empty string, which
    # is what makes "absent" and "present but wrong" distinguishable.
    semantic_profile, semantic_profile_raw = _lesson_profile(head)
    lang, lang_raw = _lesson_lang(head)
    direction, dir_raw, dir_declared = _lesson_direction(head)
    example_order, example_order_reason = _lesson_example_order(head)
    pace, pace_raw = _lesson_pace(head)

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
            "gate": gate,
            "semantic_profile": semantic_profile,
            "semantic_profile_raw": semantic_profile_raw,
            "lang": lang,
            "lang_raw": lang_raw,
            "dir": direction,
            "dir_raw": dir_raw,
            "dir_declared": dir_declared,
            "example_order": example_order,
            "example_order_reason": example_order_reason,
            "pace": pace,
            "pace_raw": pace_raw,
            "body": lesson_text.strip(),
            "intro": "\n".join(intro).strip(),
            "headings": headings,
            "error": "",
            "detail": ""}


def lesson_steps(lesson):
    """Resolve the D-16D-1 pacing ladder over one parsed lesson.

    Precedence, in order: an explicit authored `[STEP: <id>]` marker wins;
    else the configured `[LESSON-PACE:]` heading level; else the whole
    document as one step, which is exactly the pre-16D behaviour, so a
    lesson that never asked for pacing is untouched.

    Returns a list of `{"id", "title", "rung", "content"}` dicts in document
    order. `content` is the step's slice of the effective lesson text with
    marker lines removed: a marker is pacing metadata and is never rendered
    as prose in any mode. Duplicate authored ids are returned exactly as
    written: the parser reports what is written and the linter judges it
    (`lesson.duplicate_step`), which is the same division `[GATE:]` follows.
    """
    import model
    if not lesson:
        return []
    body = lesson.get("body") or ""
    headings = lesson.get("headings") or []
    first_heading = headings[0]["text"] if headings else ""

    def title_of(content, fallback):
        hm = re.search(r"(?m)^###\s+(.+?)\s*$", content)
        if hm:
            return hm.group(1).strip()
        for line in content.splitlines():
            if line.strip():
                return " ".join(line.strip().split()[:8])
        return fallback

    markers = list(model.STEP_RE.finditer(body))
    if markers:
        steps = []
        lead = body[:markers[0].start()].strip()
        if lead:
            steps.append({"id": "intro", "rung": 1,
                          "title": first_heading or "Introduction",
                          "content": model.STEP_LINE_RE.sub("", lead).strip()})
        for i, m in enumerate(markers):
            end = markers[i + 1].start() if i + 1 < len(markers) else len(body)
            content = model.STEP_LINE_RE.sub("", body[m.end():end]).strip()
            steps.append({"id": m.group(1), "rung": 1,
                          "title": title_of(content, m.group(1)),
                          "content": content})
        return steps
    if lesson.get("pace") == "h3" and headings:
        steps = []
        intro = (lesson.get("intro") or "").strip()
        if intro:
            steps.append({"id": "intro", "rung": 2,
                          "title": first_heading or "Introduction",
                          "content": intro})
        for h in headings:
            steps.append({"id": h["slug"], "rung": 2, "title": h["text"],
                          "content": ("### %s\n%s" % (h["text"], h["body"]))
                          .strip()})
        return steps
    return [{"id": "document", "rung": 3,
             "title": first_heading or "Lesson", "content": body}]


_TERM_REF_RE = re.compile(r"\[\[([^\]]+)\]\]")
_META_CELL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)=(.*)$", re.S)
_PREAMBLE_HEADING_RE = re.compile(r"(?m)^##\s")


def _preamble_section(head, name):
    """The body of one `## <NAME>` preamble section, or None when the bank
    carries no such section.

    THE boundary rule, defined once for every preamble registry: a preamble
    section runs until the next level-two heading or the first question,
    whichever comes first. `head` arrives already truncated at the first
    question by the caller's chunk walk; this function applies the other
    half. `parse_terms`, `parse_sources` and `parse_cases` -- plus the
    lesson-body `[[term]]` refs scan -- all read through this one
    definition, so the file carries one boundary rule rather than four that
    can drift. Section order in the preamble is therefore free: `## TERMS`
    above `## LESSON` parses exactly as it does below it.

    Fenced regions are dropped before anything is located, so a pipe row --
    or a `[[term]]` reference -- inside a fence is sample markup an author
    is showing, never a row of the section and never a reference the reader
    could render. The fence pattern is the one `_STYLE_FENCE_RE` the style
    checks already use, not a second copy. An unterminated fence matches
    nothing and drops nothing, so the failure mode is the pre-existing one
    (lint reports the malformed block), never a silently truncated bank.
    """
    import model
    text = model._STYLE_FENCE_RE.sub("", head or "")
    m = re.search(r"(?m)^##\s+%s\s*$" % re.escape(name), text)
    if m is None:
        return None
    body = text[m.end():]
    nxt = _PREAMBLE_HEADING_RE.search(body)
    return body[:nxt.start()] if nxt else body


def _term_refs(text):
    """`[[term]]` references in document order, each reduced to its slug by
    the one slugifier -- the same value the trigger and the `<dt id>` anchor
    use, so a lookup that agrees with an anchor by coincidence is impossible
    (the D-03 rule, restated for terms)."""
    return [{"text": m.group(1).strip(),
             "slug": lesson_slug(m.group(1))}
            for m in _TERM_REF_RE.finditer(text or "")]


def _terms_row_cells(line):
    """Split one `## TERMS` pipe row with the shared Markdown cell splitter."""
    return split_cells(line), is_separator_row(line)


def parse_terms(bank_path):
    """A third, independent read over the bank file for a different purpose:
    the `## TERMS` section's glossary records. Never called from inside
    `load()` or `parse_bank()`, and it changes neither's return shape.

    Mirrors `parse_lesson()`'s boundary rule exactly: iterate every chunk of
    the unbounded split and stop accumulating the moment a chunk both matches
    `Qn.` at its start and parses as a real question.

    Returns `None` when the preamble carries no `## TERMS` section; otherwise
    a dict with exactly:
      `terms` -- slug -> record with keys `canonical`, `aliases`, `def`,
          `xlat` and `see` (the last two empty when absent)
      `refs`  -- `[[term]]` references from the lesson body, in document
          order, each `{"text", "slug"}`
      `ignored` -- reserved/unknown `key=value` meta fields (`zh=` and any
          unrecognised key), captured and marked ignored, never rendered
          (D-24): the reader drops them with no DOM trace, and 999.2 reads
          them back from this list additively
      `empty` -- True when the block parsed to zero term rows
      `collisions` -- slug collisions among term keys and aliases, each
          `{"slug", "texts"}` naming every canonical text that collided with
          the first claimer
    """
    import model
    with open(bank_path, encoding="utf-8") as source_handle:
        text = source_handle.read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and model.parse_question(ch) is not None:
            break
        preamble.append(ch)
    head = "".join(preamble)

    block = _preamble_section(head, "TERMS")
    if block is None:
        return None

    # Refs are collected from the lesson body -- the text the reader actually
    # renders -- so a [[term]] that can never render is never flagged as
    # unknown by the linter. Routed through the same bounded helper the rows
    # are, so there is no surviving second boundary rule here.
    lesson_body = _preamble_section(head, "LESSON")
    refs = _term_refs(lesson_body) if lesson_body is not None else []

    rows = []
    ignored = []
    for line in block.splitlines():
        if not line.strip():
            continue
        cells, is_sep = _terms_row_cells(line)
        if is_sep or len(cells) < 2 or not cells[0]:
            continue
        canonical, definition = cells[0], cells[1]
        aliases, meta = [], {}
        for cell in cells[2:]:
            mm = _META_CELL_RE.match(cell)
            if mm:
                meta[mm.group(1)] = mm.group(2).strip()
            else:
                aliases.append(cell)
        rows.append({"canonical": canonical, "aliases": aliases,
                     "def": definition,
                     "xlat": meta.get("xlat", ""),
                     "see": meta.get("see", "")})
        ignored.extend({"row": canonical, "key": key, "value": value}
                       for key, value in meta.items()
                       if key not in ("xlat", "see"))

    terms, claimed, collisions = {}, {}, {}
    for row in rows:
        slugs = [lesson_slug(row["canonical"])] + \
                [lesson_slug(a) for a in row["aliases"]]
        for slug in slugs:
            if not slug:
                continue
            if slug in claimed and claimed[slug] != row["canonical"]:
                collisions.setdefault(slug, []).append(row["canonical"])
            else:
                claimed.setdefault(slug, row["canonical"])
        terms.setdefault(lesson_slug(row["canonical"]), row)

    return {"terms": terms,
            "refs": refs,
            "ignored": ignored,
            "empty": not rows,
            "collisions": [{"slug": slug, "texts": texts}
                           for slug, texts in collisions.items()]}


_SRC_DIRECTIVE_RE = re.compile(r"\[SRC:\s*([^\]]+?)\]")
_OBJ_DIRECTIVE_RE = re.compile(r"\[OBJ:\s*([^\]]+?)\]")
# The media reference form (plan 16A-05). D-16A-7 settles the registry shape
# and not the reference form; this follows the [SRC:] and [OBJ:] precedent
# directly above rather than inventing a third spelling. An empty id is
# matched and resolved to nothing, so `[MEDIA: ]` is a lint finding rather
# than a silent no-op.
_MEDIA_REF_RE = re.compile(r"\[MEDIA:\s*([^\]]*?)\s*\]")


def parse_sources(bank_path):
    """An independent read over the bank file for provenance: the `## SOURCES`
    registry and every `[SRC: <id> <locators>]` / `[OBJ: framework/objective-id]`
    directive, tagged by the item that carries them (D-11, plan 03.2-02).
    Never called from inside `load()` or `parse_bank()`, and it changes
    neither's return shape.

    The registry lives in the bank preamble, above the first question (the
    same boundary rule as `## LESSON` and `## TERMS`): one pipe row per source,
    `id | locator | ...`, first cell the id, the remaining cells its locators.
    [SRC:] and [OBJ:] directives inside item blocks resolve through that
    registry -- an id the registry does not carry is unresolvable, which lint
    reports naming the id and the file (D-11, T-032-05).

    Returns `None` when the bank carries no `## SOURCES` section and no
    directive; otherwise a dict with exactly:
      `sources` -- source_id -> locators from the `## SOURCES` registry
      `srcs`    -- `[SRC:]` directives, in document order, each
          `{"id", "locators", "item"}`
      `objs`    -- `[OBJ:]` directives, in document order, each
          `{"obj", "item"}`
      `duplicates` -- source ids registered more than once, in first-seen order
      `path`    -- the bank path as given, so lint findings can name the file
    """
    import model
    with open(bank_path, encoding="utf-8") as source_handle:
        text = source_handle.read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and model.parse_question(ch) is not None:
            break
        preamble.append(ch)
    head = "".join(preamble)

    sources = {}
    duplicates = []
    block = _preamble_section(head, "SOURCES")
    if block is not None:
        for line in block.splitlines():
            if not line.strip():
                continue
            cells, is_sep = _terms_row_cells(line)
            if is_sep or not cells or not cells[0]:
                continue
            sid = cells[0]
            locators = " ".join(c.strip() for c in cells[1:] if c.strip())
            if sid in sources:
                duplicates.append(sid)
            else:
                sources[sid] = locators

    # Directives are scanned over every item chunk, numbered exactly the way
    # `parse_bank()` numbers questions, so a finding's item tag always matches
    # the tag lint() uses for the same item.
    srcs, objs = [], []
    n = 0
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if not re.match(r"Q\d+\.", ch.strip()):
            continue
        if model.parse_question(ch) is None:
            continue
        n += 1
        tag = "Q%d" % n
        for mm in _SRC_DIRECTIVE_RE.finditer(ch):
            rest = mm.group(1).strip()
            parts = rest.split(None, 1)
            srcs.append({"id": parts[0] if parts else "",
                         "locators": parts[1] if len(parts) > 1 else "",
                         "item": tag})
        for mm in _OBJ_DIRECTIVE_RE.finditer(ch):
            objs.append({"obj": mm.group(1).strip(), "item": tag})

    if not sources and not srcs and not objs:
        return None
    return {"sources": sources, "srcs": srcs, "objs": objs,
            "duplicates": duplicates, "path": bank_path}


def parse_media(bank_path):
    """An independent read over the bank file for media: the `## MEDIA`
    registry and every `[MEDIA: <id>]` reference in the lesson body (D-16A-7,
    CAP-02). Never called from inside `load()` or `parse_bank()`, and it
    changes neither's return shape, exactly as `parse_sources` and
    `parse_terms` are not.

    The registry lives in the bank preamble, above the first question, under
    the same boundary rule as `## LESSON`, `## TERMS`, and `## SOURCES`: this
    function calls `_preamble_section` and compiles no section regex of its
    own. A sixth reader with its own scanner would be the first place the
    file's one boundary rule stopped being one, which is exactly what that
    function's docstring says it exists to prevent.

    One pipe row per asset, positional against `MEDIA_COLUMNS`: the first cell
    is the id and the remaining seven map onto `path`, `credit`, `alt`,
    `rights`, `derivation`, `availability`, `integrity`. A row with fewer
    cells fills the rest with the empty string rather than raising, so a
    malformed row is lint's problem and never a parse failure, and this
    function raises on no input at all.

    Returns `None` when the bank carries no `## MEDIA` section and no
    `[MEDIA:]` reference; otherwise a dict with exactly:
      `assets`     -- asset id -> a dict carrying exactly `MEDIA_COLUMNS`
      `refs`       -- `[MEDIA:]` references, in document order, each
          `{"id", "heading"}`, where `heading` is the `###` heading text the
          reference falls under and the empty string above the first one
      `duplicates` -- asset ids registered more than once, in first-seen order
      `path`       -- the bank path as given, so lint findings name the file

    Rights are read here and enforced nowhere (D-16A-8). This function records
    what an author declared; no code path in Phase 16A gates on it.
    """
    import model
    with open(bank_path, encoding="utf-8") as source_handle:
        text = source_handle.read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and model.parse_question(ch) is not None:
            break
        preamble.append(ch)
    head = "".join(preamble)

    assets = {}
    duplicates = []
    block = _preamble_section(head, "MEDIA")
    if block is not None:
        for line in block.splitlines():
            if not line.strip():
                continue
            cells, is_sep = _terms_row_cells(line)
            if is_sep or not cells or not cells[0]:
                continue
            aid = cells[0]
            if aid in assets:
                duplicates.append(aid)
                continue
            row = {"id": aid}
            for offset, column in enumerate(model.MEDIA_COLUMNS[1:]):
                index = offset + 1
                row[column] = (cells[index].strip()
                               if index < len(cells) else "")
            assets[aid] = row

    # References are resolved to the `###` heading they fall under by walking
    # the effective lesson body the same way `parse_lesson` splits it, so a
    # lint finding can name where the author has to go to fix it.
    refs = []
    lesson = model.parse_lesson(bank_path)
    body = ""
    if isinstance(lesson, dict):
        body = lesson.get("body") or ""
    heading = ""
    for line in body.split("\n"):
        hm = re.match(r"^###\s+(.+?)\s*$", line)
        if hm:
            heading = hm.group(1).strip()
            continue
        for mm in _MEDIA_REF_RE.finditer(line):
            refs.append({"id": mm.group(1).strip(), "heading": heading})

    if not assets and not refs:
        return None
    return {"assets": assets, "refs": refs, "duplicates": duplicates,
            "path": bank_path}


def parse_activities(bank_path):
    """An independent read over the bank file for activities: the
    `## ACTIVITIES` registry (ACTIVITY-01, plan 16A-06). Never called from
    inside `load()` or `parse_bank()`, and it changes neither's return shape,
    exactly as `parse_sources`, `parse_terms`, and `parse_media` are not.

    The registry lives in the bank preamble, above the first question, under
    the same boundary rule as `## LESSON`, `## TERMS`, `## SOURCES`, and
    `## MEDIA`: this function calls `_preamble_section` and compiles no
    section regex of its own.

    One pipe row per activity, positional against `ACTIVITY_COLUMNS`: the
    first cell is the item id and the remaining ten map onto ACTIVITY-01's ten
    declared fields. A row with fewer cells fills the rest with the empty
    string rather than raising, so a malformed row is lint's problem and never
    a parse failure, and this function raises on no input at all.

    Returns `None` when the bank carries no `## ACTIVITIES` section;
    otherwise a dict with exactly:
      `activities` -- item id -> a dict carrying exactly `ACTIVITY_COLUMNS`
      `order`      -- item ids in DOCUMENT order. Never sorted: two
          activities declaring the same purpose keep the order their author
          wrote them in, because the order is authored information
      `duplicates` -- item ids declared more than once, in first-seen order
      `empty`      -- True when the section exists and carries no data row,
          mirroring `parse_terms`'s own `empty` key
      `path`       -- the bank path as given, so lint findings name the file

    **A declaration is metadata beside an item and grants no scoring path.**
    The `feedback`, `retry`, and `evidence` columns describe what the runtime
    already does in a given mode; nothing in Phase 16A reads them to decide
    anything. `runtime.score_response`, `runtime.public_item`, and
    `evidence.append_event` remain the only things that decide.

    Pure: it opens the file for reading only, holds no cache and no
    module-level state, and writes nothing. Two calls on an unchanged file
    return equal dicts.
    """
    import model
    with open(bank_path, encoding="utf-8") as source_handle:
        text = source_handle.read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and model.parse_question(ch) is not None:
            break
        preamble.append(ch)
    head = "".join(preamble)

    block = _preamble_section(head, "ACTIVITIES")
    if block is None:
        return None

    activities = {}
    order = []
    duplicates = []
    for line in block.splitlines():
        if not line.strip():
            continue
        cells, is_sep = _terms_row_cells(line)
        if is_sep or not cells or not cells[0]:
            continue
        item = cells[0]
        if item in activities:
            duplicates.append(item)
            continue
        row = {"item": item}
        for offset, column in enumerate(model.ACTIVITY_COLUMNS[1:]):
            index = offset + 1
            row[column] = (cells[index].strip()
                           if index < len(cells) else "")
        activities[item] = row
        order.append(item)

    return {"activities": activities, "order": order,
            "duplicates": duplicates, "empty": not activities,
            "path": bank_path}


