"""The format contract: what a bank is, and what makes one invalid.

Everything here reads markdown and returns plain dicts. It knows nothing about
scoring, sessions or surfaces, which is what lets `spec` and `lint` be the whole
of what an authoring agent has to satisfy.
"""
import collections, hashlib, json, os, re, sys, uuid

import resources


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
        r"|\nMODEL:|\nRUBRIC:|\nWHY BEST:|\n\[LESSON-REF|\n\[PAIR|\n\[PREREQ)",
        ch, re.S)
    lesson_ref = grab(r"\[LESSON-REF:\s*(.*?)\]", ch)
    common = {
        "id": "q" + number if number else "",
        "number": int(number) if number else 0,
        "type": qtype,
        "stem": stem,
        "difficulty": grab(r"\(difficulty:\s*([^)]+)\)", ch),
        "objective": grab(r"\[OBJECTIVE:\s*(.*?)\]", ch),
        "objective_line": grab(r"(?m)^Objective:\s*(.*?)\s*$", ch),
        "pair": grab(r"(?m)^\[PAIR:\s*(.*?)\s*\]\s*$", ch),
        "prereq": [p.strip() for p in
                   grab(r"(?m)^\[PREREQ:\s*(.*?)\s*\]\s*$", ch).split(",") if p.strip()],
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

    if qtype == "visual":
        # Interactive visual assessment (phase 06.1). `[INTERACTION:]` names
        # the one protocol-1 interaction family, `[VISUAL:]` is the declarative
        # scene/actions/accessibility configuration, and `[SCORING:]` is the
        # private scoring envelope (accepted states, tolerance). Both JSON
        # fields are parsed as data here and never executed; the public
        # projection of the scene happens in runtime.public_item, which omits
        # every SCORING member.
        interaction = grab(r"(?m)^\[INTERACTION:\s*(\w+)\s*\]", ch).lower()
        visual_raw = grab(r"(?m)^\[VISUAL:\s*(.+?)\s*\]\s*$", ch)
        scoring_raw = grab(r"(?m)^\[SCORING:\s*(.+?)\s*\]\s*$", ch)
        if not stem:
            return None
        common.update({
            "interaction": interaction,
            "visual": _json_or_none(visual_raw),
            "scoring": _json_or_none(scoring_raw),
            # The raw bracketed text is kept so lint can tell "malformed
            # JSON" (raw present, parse failed) apart from "field absent"
            # (raw empty) and address the offending field by name.
            "visual_raw": visual_raw,
            "scoring_raw": scoring_raw,
        })
        return common

    return None


def _json_or_none(raw):
    """Parse one bracketed JSON field (`[VISUAL: ...]` / `[SCORING: ...]`)
    into a dict, or None when absent or malformed. The model layer parses
    JSON as data; executable content is rejected later by the runtime's
    closed allowlist before any renderer sees it."""
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


# The visual lint families (plan 06.1-02, D-01/D-03): each maps to one stable
# dotted code addressed by the offending field, so an authoring agent can
# repair an item without a lookup table. The grammar itself (SCALAR, axis,
# state, executable-content rejection) lives in runtime.py -- the single
# source the scorer uses -- and these findings reuse it through a lazy import,
# the same pattern runtime.py uses for `import model`. The model layer never
# re-implements the grammar; it only reports where the authored JSON violates
# it. Unknown-member and malformed-JSON checks happen here against the raw
# text the parser kept, so a field is named even when the JSON never parsed.
# The per-interaction scene-member allowlist lives in runtime.py
# (phase 999.1, D-999.1-04) so lint and the contract share one authority.
VISUAL_SCORING_MEMBERS = frozenset({"kind", "accepted", "tolerance",
                                    "partial_credit", "feedback"})


def _visual_lint_findings(q, tag):
    """Named, field-addressed lint findings for one visual item (D-01/D-03,
    T-06.1-05). Returns a list of LintError records -- every finding is an
    error, because malformed/unsafe/inaccessible visual configuration must
    fail lint before a learner ever sees the item.

    The grammar checks delegate to runtime.py (the one grammar) through a
    lazy import; the model layer only maps violations to codes and fields.
    """
    import runtime as _runtime  # function-local, mirrors runtime's import model

    interaction = (q.get("interaction") or "").strip()
    visual_raw = q.get("visual_raw") or ""
    scoring_raw = q.get("scoring_raw") or ""
    visual = q.get("visual")
    scoring = q.get("scoring")

    if not interaction:
        return [LintError("item.visual_unknown_interaction", "interaction", tag,
                          "visual item has no [INTERACTION:] line")]
    if interaction not in _runtime.VISUAL_INTERACTIONS:
        return [LintError("item.visual_unknown_interaction", "interaction", tag,
                          "unknown INTERACTION %r (protocol %d supports %s)"
                          % (interaction, _runtime.VISUAL_PROTOCOL_VERSION,
                             ", ".join(_runtime.VISUAL_INTERACTIONS)))]

    findings = []
    if visual_raw and not isinstance(visual, dict):
        findings.append(LintError(
            "item.visual_json_malformed", "visual", tag,
            "[VISUAL:] is not valid JSON"))
    if scoring_raw and not isinstance(scoring, dict):
        findings.append(LintError(
            "item.visual_json_malformed", "scoring", tag,
            "[SCORING:] is not valid JSON"))
    if not isinstance(visual, dict) or not isinstance(scoring, dict):
        # Nothing further can be validated without the parsed JSON.
        return findings

    # Unknown members first: a top-level member outside the closed per-
    # interaction allowlist is an authoring error even when it also looks
    # script-bearing (the executable check below catches nested ones).
    allowed = _runtime._VISUAL_SCENE_MEMBERS.get(interaction) or frozenset()
    unknown = sorted(set(visual) - allowed)
    if unknown:
        findings.append(LintError(
            "item.visual_unknown_member", "visual", tag,
            "unknown VISUAL member(s): %s" % ", ".join(unknown)))
    unknown = sorted(set(scoring) - VISUAL_SCORING_MEMBERS)
    if unknown:
        findings.append(LintError(
            "item.visual_unknown_member", "scoring", tag,
            "unknown SCORING member(s): %s" % ", ".join(unknown)))

    # Executable/script-bearing members anywhere in the scene or envelope
    # (T-06.1-05): a script-bearing bank fails closed even when its JSON is
    # otherwise valid.
    try:
        _runtime._reject_visual_exec(visual, "VISUAL")
        _runtime._reject_visual_exec(scoring, "SCORING")
    except ValueError as exc:
        findings.append(LintError("item.visual_executable_member", "visual",
                                  tag, str(exc)))

    # Actions: a non-empty subset of the locked protocol-1 action vocabulary.
    actions = visual.get("actions")
    if not isinstance(actions, list) or not actions \
            or any(a not in _runtime.VISUAL_ACTIONS for a in actions):
        findings.append(LintError(
            "item.visual_unknown_action", "actions", tag,
            "actions must be a non-empty subset of %s"
            % ", ".join(_runtime.VISUAL_ACTIONS)))

    # Accessibility: the D-07 gate -- a visual item needs an accessible
    # description; the SVG's name/description and the semantic fallback are
    # built from it, so an empty one is an error, not a warning.
    accessibility = visual.get("accessibility")
    if not isinstance(accessibility, dict) \
            or not str(accessibility.get("description") or "").strip():
        findings.append(LintError(
            "item.visual_empty_accessibility", "accessibility", tag,
            "accessibility.description is required (D-07)"))

    # Scoring kind: one of the three protocol-1 response kinds, matching the
    # interaction family, and the protocol is dichotomous (D-02).
    kind = scoring.get("kind")
    if kind not in _runtime.VISUAL_KINDS:
        findings.append(LintError(
            "item.visual_unknown_scoring_kind", "kind", tag,
            "unknown SCORING kind %r (protocol %d supports %s)"
            % (kind, _runtime.VISUAL_PROTOCOL_VERSION,
               ", ".join(_runtime.VISUAL_KINDS))))
    if scoring.get("partial_credit") is not False:
        findings.append(LintError(
            "item.visual_invalid_scoring_kind", "partial_credit", tag,
            "protocol %d is dichotomous; partial_credit must be false"
            % _runtime.VISUAL_PROTOCOL_VERSION))

    # Axis geometry: every min/max/step is a SCALAR (invalid scalar is
    # reported separately so precision problems name the field), step is
    # positive, span divides into at most 200 whole steps (201 ticks).
    def _axis_field(axis, axis_name):
        if not isinstance(axis, dict):
            findings.append(LintError(
                "item.visual_invalid_axis", axis_name, tag,
                "%s must be an object with min, max, step" % axis_name))
            return
        for field in ("min", "max", "step"):
            value = axis.get(field)
            if _runtime.canonical_scalar(value) is None:
                findings.append(LintError(
                    "item.visual_invalid_scalar", field, tag,
                    "%s.%s = %r is not a valid SCALAR (protocol %d grammar)"
                    % (axis_name, field, value, _runtime.VISUAL_PROTOCOL_VERSION)))
        if _runtime.canonical_axis(axis) is None:
            findings.append(LintError(
                "item.visual_invalid_axis", axis_name, tag,
                "%s is invalid (positive SCALAR step, max > min, at most %d "
                "ticks)" % (axis_name, _runtime.VISUAL_MAX_TICKS)))

    if interaction in ("plot", "trace"):
        axes = visual.get("axes")
        if not isinstance(axes, dict) or "x" not in axes or "y" not in axes:
            findings.append(LintError(
                "item.visual_invalid_axis", "axes", tag,
                "%s scene needs axes.x and axes.y" % interaction))
        else:
            _axis_field(axes["x"], "axes.x")
            _axis_field(axes["y"], "axes.y")
    elif interaction in ("numberline", "timeline"):
        _axis_field(visual.get("axis"), "axis")

    # Accepted states must canonicalize and stay in the authored domain, and
    # tolerance must be a non-negative SCALAR. The runtime raises ValueError
    # for these, which is mapped to the field-addressed code. Phase 999.1
    # geometry/duplicate-id errors carry recognizable prefixes so they map to
    # their own codes with the offending field named.
    try:
        _runtime._visual_interaction_contract(q)
    except ValueError as exc:
        message = str(exc)
        if message.startswith("geometry:"):
            findings.append(LintError(
                "item.visual_invalid_geometry", "visual", tag, message))
        elif message.startswith("duplicate_id:"):
            findings.append(LintError(
                "item.visual_duplicate_id", "visual", tag, message))
        elif "does not match INTERACTION" in message:
            findings.append(LintError(
                "item.visual_unknown_scoring_kind", "kind", tag, message))
        elif "accepted state" in message:
            findings.append(LintError(
                "item.visual_invalid_scalar", "accepted", tag, message))
        elif "tolerance" in message and "non-negative SCALAR" in message:
            findings.append(LintError(
                "item.visual_invalid_tolerance", "tolerance", tag, message))
        elif "accessibility" in message:
            findings.append(LintError(
                "item.visual_empty_accessibility", "accessibility", tag,
                message))
        else:
            findings.append(LintError(
                "item.visual_invalid_scalar", "scoring", tag, message))

    # Duplicate/unstable scene ids (D-07: stable ids are part of the
    # accessibility/evidence contract -- a point id must be stable and unique
    # so committed actions and evidence can name it).
    initial = visual.get("initial") or {}
    ids = []
    for point in initial.get("points") or []:
        if isinstance(point, dict) and point.get("id"):
            ids.append(str(point["id"]))
    if len(ids) != len(set(ids)):
        findings.append(LintError(
            "item.visual_duplicate_id", "initial", tag,
            "scene point ids must be unique (found %d ids, %d unique)"
            % (len(ids), len(set(ids)))))
    return findings


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

    # The Phase 6.2 gate directive (D-02): one [GATE:] in the effective
    # lesson preamble (the bank's own, or the external file's when
    # [LESSON-SRC:] replaced it), following the exact [LESSON-SRC:] grab
    # pattern -- additive grammar, default "recommended" when absent, and
    # the value validated at lint time, never here (a parse must not raise).
    gate = grab(r"(?m)^\[GATE:\s*(.*?)\s*\]", head) or "recommended"

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
            "body": lesson_text.strip(),
            "intro": "\n".join(intro).strip(),
            "headings": headings,
            "error": "",
            "detail": ""}


_TERM_REF_RE = re.compile(r"\[\[([^\]]+)\]\]")
_META_CELL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)=(.*)$", re.S)


def _term_refs(text):
    """`[[term]]` references in document order, each reduced to its slug by
    the one slugifier -- the same value the trigger and the `<dt id>` anchor
    use, so a lookup that agrees with an anchor by coincidence is impossible
    (the D-03 rule, restated for terms)."""
    return [{"text": m.group(1).strip(),
             "slug": lesson_slug(m.group(1))}
            for m in _TERM_REF_RE.finditer(text or "")]


def _terms_row_cells(line):
    """Split one `## TERMS` pipe row with the lesson reader's own cell
    splitter, never a second implementation. Imported lazily because
    surfaces/lesson.py imports this module at load time; a top-level import
    here would cycle, and the reuse is the point (research's anti-pattern:
    don't hand-roll a second splitter)."""
    from surfaces.lesson import _is_separator_row, _split_cells
    return _split_cells(line), _is_separator_row(line)


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
    text = open(bank_path, encoding="utf-8").read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and parse_question(ch) is not None:
            break
        preamble.append(ch)
    head = "".join(preamble)

    m = re.search(r"(?m)^##\s+TERMS\s*$", head)
    if m is None:
        return None

    # Refs are collected from the lesson body -- the text the reader actually
    # renders -- so a [[term]] that can never render is never flagged as
    # unknown by the linter.
    lm = re.search(r"(?m)^##\s+LESSON\s*$", head)
    refs = _term_refs(head[lm.end():]) if lm else []

    rows = []
    ignored = []
    for line in head[m.end():].splitlines():
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
    text = open(bank_path, encoding="utf-8").read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and parse_question(ch) is not None:
            break
        preamble.append(ch)
    head = "".join(preamble)

    sources = {}
    duplicates = []
    m = re.search(r"(?m)^##\s+SOURCES\s*$", head)
    if m is not None:
        for line in head[m.end():].splitlines():
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
        if parse_question(ch) is None:
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


def coverage_map(bank_path):
    """The objective coverage map, computed on demand and never stored (D-12,
    plan 03.2-02): objective -> sorted item tags, built from every item's
    [OBJECTIVE:] value plus its resolved [OBJ:] values (those registered in
    the bank's ## SOURCES). A bank with no items or no objectives maps to {}.
    """
    text = open(bank_path, encoding="utf-8").read()
    qs = parse_bank(text)
    ps = parse_sources(bank_path)
    known = (ps or {}).get("sources") or {}
    out = {}
    for idx, q in enumerate(qs, 1):
        tag = "Q%d" % idx
        objectives = set()
        if q.get("objective"):
            objectives.add(q["objective"])
        if ps:
            for d in ps.get("objs") or []:
                if d["item"] == tag and d["obj"] in known:
                    objectives.add(d["obj"])
        for o in sorted(objectives):
            out.setdefault(o, []).append(tag)
    return {o: tags for o, tags in sorted(out.items())}


_KEY_MARK_RE = re.compile(r"^>\s*\[!KEY(?::\s*([^\]]+))?\]\s*(.*)$")


# ---- plan 03.2-04: winnowing paraphrase lint (D-13) -----------------------
# stdlib-only winnowing over k-gram fingerprints. The window size is the
# executor's discretion (03.2-CONTEXT "Claude's discretion"): the selection
# below is the standard min-hash-per-window winnowing (Schleimer et al.), and
# the shipped default window is 1 -- the deterministic end of the family,
# where every k-gram is its own window minimum. A larger window would thin
# the fingerprint set but loses the exactness the copy-run measurement needs,
# so the default trades memory for determinism: the stage-4 gate (D-08) must
# be deterministic, and the source text itself is read transiently, reduced
# to hashes, and never stored or echoed (T-032-12).

PARAPHRASE_DEFAULTS = {"winnow_threshold": 8, "jaccard_threshold": 0.25}
_PARAPHRASE_K = 4           # word k-gram size
_PARAPHRASE_WINDOW = 1      # winnowing window: min-hash per window; 1 = no thinning

_SPECIFIC_FACT_RE = re.compile(
    r"(?:\d+(?:\.\d+)?\s*(?:mg|mcg|µg|mcg/kg|mg/kg|g|kg|mL|ml|L|cm|mm|m|IU|"
    r"mEq|mmol|units?|U|drops?|gtts?|bpm|mmHg|mm\s?Hg|min|hrs?|sec|%))"
    r"|\d+\.\d+",
    re.I)

_CASE_DIRECTIVE_RE = re.compile(r"\[CASE:\s*([^\]]+?)\]")
_PREREQ_DIRECTIVE_RE = re.compile(r"\[PREREQ:\s*([^\]]+?)\]")


def _fingerprint_tokens(text):
    """The word tokens a paraphrase fingerprint is built from: lowercase
    alphanumeric runs, so case and punctuation never create false distinct
    k-grams."""
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _gram_hash(gram):
    """A stable, process-independent hash of one k-gram (stdlib sha1), so the
    fingerprint is identical across runs -- the deterministic stage-4 gate
    must never vary with PYTHONHASHSEED."""
    return int.from_bytes(
        hashlib.sha1(" ".join(gram).encode("utf-8")).digest()[:8], "big")


def _kgram_hashes(text, k=_PARAPHRASE_K):
    """The k-gram hash list of `text`: hash(words[i:i+k]) for each position."""
    words = _fingerprint_tokens(text)
    return [_gram_hash(words[i:i + k]) for i in range(len(words) - k + 1)]


def _winnow_positions(hashes, window=_PARAPHRASE_WINDOW):
    """Winnowing (Schleimer et al.): the minimum hash in each sliding window
    of `window` consecutive k-grams is selected, rightmost on a tie. Returns
    the selected positions. With the default window 1 every k-gram is its own
    minimum -- the full fingerprint, kept for run-exactness."""
    out = set()
    if not hashes:
        return out
    w = max(1, int(window))
    for i in range(len(hashes) - w + 1):
        chunk = hashes[i:i + w]
        j = i + max(idx for idx, h in enumerate(chunk)
                    if h == min(chunk))
        out.add(j)
    return out


def _winnow_set(hashes, window=_PARAPHRASE_WINDOW):
    return {hashes[i] for i in _winnow_positions(hashes, window)}


def paraphrase_check(candidate_text, source_text, winnow_threshold=8,
                     jaccard_threshold=0.25):
    """The winnowing-based paraphrase comparison (D-13, SEED-05). Both texts
    are reduced to k-gram hashes -- fingerprints only, the source text is
    never stored. Returns a dict:
        copy_words -- the longest run of consecutive candidate words that
            appear verbatim in the source (matching k-gram run + k - 1)
        jaccard    -- |candidate fp & source fp| / |candidate fp | source fp|
        copy       -- copy_words >= winnow_threshold
        overlap    -- jaccard > jaccard_threshold
    """
    c_hashes = _kgram_hashes(candidate_text)
    s_set = set(_kgram_hashes(source_text))
    run = best = 0
    for h in c_hashes:
        if h in s_set:
            run += 1
            best = max(best, run)
        else:
            run = 0
    copy_words = best + _PARAPHRASE_K - 1 if best else 0
    c_win = _winnow_set(c_hashes)
    s_win = _winnow_set(_kgram_hashes(source_text))
    union = c_win | s_win
    jaccard = len(c_win & s_win) / len(union) if union else 0.0
    return {"copy_words": copy_words, "jaccard": jaccard,
            "copy": copy_words >= winnow_threshold,
            "overlap": jaccard > jaccard_threshold}


def _read_source_text(base_dir, locators):
    """Read one source's text transiently for fingerprinting. A locator's
    first whitespace token is taken as a path relative to the bank's
    directory. When it cannot be read -- a prose locator, or a corpus that
    lives outside the repo (D-17) -- the check degrades gracefully to None,
    never an error, and never a stored byte."""
    if not locators or not locators.strip():
        return None
    first = locators.strip().split()[0]
    path = os.path.join(base_dir or ".", first)
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _item_text(q):
    """The full author-written text surface of a parsed item (stem, options,
    rationale fields, table rows, build steps) -- what the paraphrase and
    unsourced-specific checks scan."""
    parts = []
    if q.get("stem"):
        parts.append(q["stem"])
    for letter in sorted(q.get("opts") or {}):
        v = q["opts"].get(letter)
        if v:
            parts.append(v)
    for _, t in _rationale_texts(q):
        parts.append(t)
    for row in q.get("rows") or []:
        parts.append(row.get("text", ""))
    for step in q.get("steps") or []:
        parts.append(step)
    return "\n".join(p for p in parts if p)


def paraphrase_findings(candidate_text, sources, thresholds=None,
                        item_tag=None, subject="the text"):
    """Paraphrase findings for `candidate_text` against every source its
    [SRC:] directives resolve to (D-13). With `item_tag`, only directives
    carried by that item are compared (the bank-lint case); without it, every
    directive in `sources` is used (the seeding-draft case, where the draft's
    own [SRC:]s are resolved by the caller). Returns (code, message) pairs;
    the source text is read transiently and reduced to hashes, and the
    messages name only the source id and file -- never its content."""
    th = dict(PARAPHRASE_DEFAULTS)
    if thresholds:
        th.update(thresholds or {})
    out = []
    if not sources:
        return out
    known = sources.get("sources") or {}
    path = sources.get("path") or ""
    fname = os.path.basename(path) if path else "the bank"
    base_dir = os.path.dirname(os.path.abspath(path)) if path else "."
    seen = set()
    for d in sources.get("srcs") or []:
        if item_tag is not None and d.get("item") != item_tag:
            continue
        sid = d.get("id") or ""
        if sid not in known or sid in seen:
            continue
        seen.add(sid)
        locators = (d.get("locators") or "").strip() or (known[sid] or "")
        text = _read_source_text(base_dir, locators)
        if text is None:
            continue
        r = paraphrase_check(candidate_text, text,
                             th["winnow_threshold"], th["jaccard_threshold"])
        if r["copy"]:
            out.append(("prov.paraphrase_copy",
                        "%d consecutive words of %s match source '%s' of %s "
                        "verbatim -- rewrite, or this is transcription"
                        % (r["copy_words"], subject, sid, fname)))
        elif r["overlap"]:
            out.append(("prov.paraphrase_overlap",
                        "%s shares fingerprint overlap %.2f with source '%s' "
                        "of %s -- paraphrase more freely"
                        % (subject, r["jaccard"], sid, fname)))
    return out


def unsourced_specific_findings(q, sources, item_tag):
    """style.unsourced_specific (D-14): numerals, units and doses in an item's
    text with no resolved [SRC:] are a structural error -- a seeded specific
    must name the source it came from. Structural regex, never a model
    judgement (D-14); a resolved [SRC:] on the item satisfies it."""
    if not sources:
        return []
    known = sources.get("sources") or {}
    path = sources.get("path") or ""
    fname = os.path.basename(path) if path else "the bank"
    has_src = any(d.get("item") == item_tag and d.get("id") in known
                  for d in sources.get("srcs") or [])
    if has_src:
        return []
    m = _SPECIFIC_FACT_RE.search(_item_text(q))
    if not m:
        return []
    return [LintError("style.unsourced_specific", "src", item_tag,
                      "item carries the specific fact %r with no resolved "
                      "[SRC:] -- cite the source it came from in %s"
                      % (m.group(0).strip(), fname))]


def parse_cases(bank_path):
    """An independent read over the bank file for [CASE:] grouping and
    [PREREQ:] edges (D-15/D-16, plan 03.2-04): the `## CASES` registry in
    the preamble (one pipe row per case, first cell the id) plus every
    [CASE: <id>] and [PREREQ: <id>] directive tagged by its item. Never
    called from inside `load()` or `parse_bank()`, and it changes neither's
    return shape.

    Returns None when the bank carries no `## CASES` section and no
    directive; otherwise a dict with exactly:
      `cases`            -- case id -> description from ## CASES
      `case_directives`  -- [CASE:] directives, document order, {id, item}
      `prereq_edges`     -- [PREREQ:] directives, document order,
          {target, item} (one entry per comma-separated target)
      `path`             -- the bank path as given
    """
    text = open(bank_path, encoding="utf-8").read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and parse_question(ch) is not None:
            break
        preamble.append(ch)
    head = "".join(preamble)

    cases = {}
    m = re.search(r"(?m)^##\s+CASES\s*$", head)
    if m is not None:
        for line in head[m.end():].splitlines():
            if not line.strip():
                continue
            cells, is_sep = _terms_row_cells(line)
            if is_sep or not cells or not cells[0]:
                continue
            cases[cells[0]] = " ".join(c.strip() for c in cells[1:]
                                       if c.strip())

    case_directives, prereq_edges = [], []
    n = 0
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if not re.match(r"Q\d+\.", ch.strip()) or parse_question(ch) is None:
            continue
        n += 1
        tag = "Q%d" % n
        for mm in _CASE_DIRECTIVE_RE.finditer(ch):
            cid = mm.group(1).strip()
            if cid:
                case_directives.append({"id": cid, "item": tag})
        for mm in _PREREQ_DIRECTIVE_RE.finditer(ch):
            for target in mm.group(1).split(","):
                t = target.strip()
                if t:
                    prereq_edges.append({"target": t, "item": tag})

    if not cases and not case_directives and not prereq_edges:
        return None
    return {"cases": cases, "case_directives": case_directives,
            "prereq_edges": prereq_edges, "path": bank_path}


def _prereq_cycle_findings(questions, cases, all_objectives):
    """A small graph walk over the bank's [PREREQ:] edges (D-16): nodes are
    case ids and minted item [ID:]s; an item's node is its [CASE:] id (when
    it has one) else its [ID:]. A deterministic DFS returns one
    prov.prereq_cycle finding naming the cycle's node path when one exists."""
    known_cases = set(cases.get("cases") or {})
    known_item_ids = {q.get("item_id") for q in questions if q.get("item_id")}
    valid = known_cases | known_item_ids | set(all_objectives)
    node_by_item = {}
    for d in cases.get("case_directives") or []:
        node_by_item[d["item"]] = d["id"]
    edges = {}
    for idx, q in enumerate(questions, 1):
        tag = "Q%d" % idx
        node = node_by_item.get(tag) or (q.get("item_id") or "")
        if not node:
            continue
        for d in cases.get("prereq_edges") or []:
            if d["item"] == tag and d["target"] in valid:
                edges.setdefault(node, set()).add(d["target"])

    GRAY, BLACK = 1, 2
    color = {}

    def visit(node, stack):
        color[node] = GRAY
        for nxt in sorted(edges.get(node, ())):
            if color.get(nxt) == GRAY:
                i = stack.index(nxt)
                return stack[i:] + [nxt]
            if color.get(nxt) is None:
                r = visit(nxt, stack + [nxt])
                if r:
                    return r
        color[node] = BLACK
        return None

    for node in sorted(edges):
        if color.get(node) is None:
            r = visit(node, [node])
            if r:
                return [LintError(
                    "prov.prereq_cycle", "prereq", "BANK",
                    "prerequisite cycle: %s -- breaks the bank's dependency "
                    "order" % " -> ".join(r))]
    return []


def _draft_cited_sources(block):
    """The [SRC:] directives in a seeding draft block, as (id, locators)
    pairs -- parse_sources() cannot see a draft that is not in the bank file
    yet, so the stage-4 check resolves the draft's own citations."""
    out = []
    for mm in _SRC_DIRECTIVE_RE.finditer(block or ""):
        rest = mm.group(1).strip()
        parts = rest.split(None, 1)
        if parts:
            out.append((parts[0], parts[1] if len(parts) > 1 else ""))
    return out


def make_seeding_checks(bank_path, settings=None):
    """The plan 03.2-04 stage-4 `extra_checks` callable for the seeding
    pipeline (D-08): a draft failing prov.paraphrase_* retries before any
    model critique. `settings` is an itembank settings dict (the `paraphrase`
    group's thresholds) or None for the shipped defaults. Source text is read
    transiently and hashed -- never stored, never echoed (D-13)."""
    th = dict(PARAPHRASE_DEFAULTS)
    if settings and isinstance(settings, dict):
        th.update(settings.get("paraphrase") or {})

    def checks(draft):
        out = []
        candidate = draft.get("candidate")
        if candidate is None:
            return out
        ps = parse_sources(bank_path)
        known = (ps or {}).get("sources") or {}
        path = (ps or {}).get("path") or bank_path
        fname = os.path.basename(path) if path else "the bank"
        base_dir = os.path.dirname(os.path.abspath(path)) if path else "."
        seen = set()
        for sid, locators in _draft_cited_sources(draft.get("block") or ""):
            if sid not in known or sid in seen:
                continue
            seen.add(sid)
            loc = (locators or "").strip() or (known[sid] or "")
            text = _read_source_text(base_dir, loc)
            if text is None:
                continue
            r = paraphrase_check(_item_text(candidate), text,
                                 th["winnow_threshold"],
                                 th["jaccard_threshold"])
            if r["copy"]:
                out.append(LintError(
                    "prov.paraphrase_copy", "src", "DRAFT",
                    "%d consecutive words of the draft match source '%s' of "
                    "%s verbatim -- rewrite, or this is transcription"
                    % (r["copy_words"], sid, fname)))
            elif r["overlap"]:
                out.append(LintError(
                    "prov.paraphrase_overlap", "src", "DRAFT",
                    "draft shares fingerprint overlap %.2f with source '%s' "
                    "of %s -- paraphrase more freely"
                    % (r["jaccard"], sid, fname)))
        return out

    return checks


def parse_key_blocks(bank_path):
    """An independent reader over the lesson body for `> [!KEY]` callouts
    (D-05's lesson-only scope): each returns a dict with `id`, `hash`,
    `title`, `body`, `cloze` and `section_slug`. Never called from inside
    `load()` or `parse_bank()`, and it changes neither's return shape; a
    lesson with no key blocks returns an empty list.

    The `[ID:]`/`[HASH:]` directive lines use the same grab idiom as
    `[LESSON-SRC:]` and are the block's machine identity -- minted by
    `assign_ids()` through the exact taken set items use, never a separate
    namespace (research Pitfall 5). `title` is the marker line's own text
    when present; `cloze` is True when the body carries `{{...}}`/`{{n::...}}`
    markers.
    """
    lesson = parse_lesson(bank_path)
    if lesson is None:
        return []
    blocks = []
    for heading in [{"slug": "", "body": lesson["intro"]}] + lesson["headings"]:
        lines = (heading["body"] or "").split("\n")
        i = 0
        while i < len(lines):
            m = _KEY_MARK_RE.match(lines[i])
            if m is None:
                i += 1
                continue
            raw_lines = [lines[i]]
            body_lines = []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                raw_lines.append(lines[i])
                body_lines.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            raw = "\n".join(raw_lines)
            # The spec documents `> [!KEY: <title>]` (title inside the
            # brackets, group 1); the trailing form `> [!KEY] <title>`
            # (group 2) is also accepted for legacy banks. The in-bracket
            # form wins when both are present.
            title = (m.group(1) or m.group(2) or "").strip()
            body = []
            for line in body_lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if re.match(r"^\[(ID|HASH):", stripped):
                    continue          # directives, consumed above
                body.append(line)
            body_text = "\n".join(body).strip()
            blocks.append({
                "id": grab(r"(?m)^>\s*\[ID:\s*(\S+)\s*\]", raw),
                "hash": grab(r"(?m)^>\s*\[HASH:\s*(\S+)\s*\]", raw),
                "title": title,
                "body": body_text,
                "cloze": "{{" in body_text,
                "section_slug": heading["slug"],
            })
    return blocks


def _user_data_dir():
    """The platform per-user data directory, following the exact
    win32/darwin/else branch surfaces/update.py already implements (D-09's
    second resolution level). Read-only here -- resolution never creates
    directories."""
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        base = os.environ.get("APPDATA",
                              os.path.join(home, "AppData", "Roaming"))
    elif sys.platform == "darwin":
        base = os.path.join(home, "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME",
                              os.path.join(home, ".local", "share"))
    return os.path.join(base, "itembank")


_STYLE_DIRECTIVE_RE = re.compile(r"(?m)^\[STYLE:\s*([^\]]+?)\s*\]")


def _style_directive(text):
    """The first `[STYLE: <id>]` directive in a text region, or the empty
    string. Directives are resolved by id only -- D-09's first-match-wins --
    and ids slugify through lesson_slug() so a style id can never escape the
    three resolution directories (T-031-13)."""
    if not text:
        return ""
    m = _STYLE_DIRECTIVE_RE.search(text)
    return m.group(1).strip() if m else ""


def _bank_preamble(bank_path):
    """The bank text before the first real question marker -- the region
    where a bank-level `[STYLE:]` directive may live. Mirrors
    parse_lesson()'s boundary rule exactly: stop accumulating the moment a
    chunk both matches `Qn.` at its start and parses as a real question, so
    an illustrative line shaped like a question marker cannot truncate the
    preamble."""
    text = open(bank_path, encoding="utf-8").read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and parse_question(ch) is not None:
            break
        preamble.append(ch)
    return "".join(preamble)


def _parse_style_file(style_id, path, text, warnings):
    """Parse one style file's `## Voice` prose zone, `## Rules` pipe table
    and `## Exemplar` block into a plain dict. The pipe table reuses the
    existing cell splitter (function-local import: surfaces.lesson imports
    model, so a top-level model -> surfaces import would cycle -- the same
    pattern plan 03.1-02 used for parse_terms). A duplicate rule id inside
    one file is recorded in `duplicate_rules`; the caller owns the LintError
    record."""
    voice, rules_text, exemplar = "", "", ""
    section = ""
    for line in text.splitlines():
        hm = re.match(r"^##\s+(\S+)\s*$", line)
        if hm:
            section = hm.group(1).lower()
            continue
        if section == "voice":
            voice += line + "\n"
        elif section == "rules":
            rules_text += line + "\n"
        elif section == "exemplar":
            exemplar += line + "\n"

    from surfaces.lesson import _is_separator_row, _split_cells
    rules = []
    duplicate_rules = []
    seen = set()
    past_separator = False
    for row in rules_text.splitlines():
        if not row.strip().startswith("|"):
            continue
        if _is_separator_row(row):
            past_separator = True
            continue
        if not past_separator:
            continue  # the header row precedes the separator
        cells = _split_cells(row)
        if len(cells) < 2:
            continue
        rule = {
            "id": cells[0],
            "kind": cells[1],
            "params": cells[2] if len(cells) > 2 else "",
            "severity": cells[3] if len(cells) > 3 else "warn",
            "lock": cells[4] if len(cells) > 4 else "",
            "prompt": cells[5] if len(cells) > 5 else "",
        }
        if rule["id"] in seen:
            duplicate_rules.append(rule["id"])
        seen.add(rule["id"])
        rules.append(rule)
    return {
        "id": style_id,
        "path": path,
        "voice": voice.strip(),
        "rules": rules,
        "exemplar": exemplar.strip(),
        "parent": grab(r"(?m)^\[STYLE-PARENT:\s*(.*?)\s*\]", text),
        "warnings": warnings,
        "duplicate_rules": duplicate_rules,
        "error": "",
        "detail": "",
    }


def load_style(style_id, base):
    """Resolve one style id to its file across the three D-09 levels --
    bank-adjacent `styles/`, the user data dir, then the bundled `styles/`
    directory -- with first match by id winning. A duplicate id across
    levels produces a warning naming both paths, never a silent shadow.

    Returns None on absence (the caller decides how an absent id reads,
    exactly like parse_lesson's None); a dict with `error` set to
    `style.file_unreadable` when the first matching file cannot be read; or
    the parsed Voice/Rules/Exemplar dict. Style ids slugify through
    lesson_slug() before any path is built (T-031-13)."""
    slug = lesson_slug(style_id)
    if not slug:
        return None
    found = []
    if base:
        bank_path = os.path.join(base, "styles", slug + ".md")
        if os.path.isfile(bank_path):
            found.append(bank_path)
    user_path = os.path.join(_user_data_dir(), "styles", slug + ".md")
    if os.path.isfile(user_path):
        found.append(user_path)
    bundled_rel = "styles/" + slug + ".md"
    try:
        resources.read_bytes(bundled_rel)
        found.append("bundled:" + slug)
    except (OSError, KeyError, FileNotFoundError):
        pass
    if not found:
        return None
    warnings = []
    if len(found) > 1:
        warnings.append(
            "style id '%s' exists at both %s and %s; %s wins (D-09)"
            % (slug, found[0], found[1], found[0]))
    chosen = found[0]
    if chosen.startswith("bundled:"):
        try:
            text = resources.read_text(bundled_rel)
        except (OSError, KeyError, FileNotFoundError) as exc:
            return {"id": style_id, "path": chosen, "voice": "",
                    "rules": [], "exemplar": "", "parent": "",
                    "warnings": warnings, "duplicate_rules": [],
                    "error": "style.file_unreadable", "detail": str(exc)}
    else:
        try:
            text = open(chosen, encoding="utf-8").read()
        except OSError as exc:
            return {"id": style_id, "path": chosen, "voice": "",
                    "rules": [], "exemplar": "", "parent": "",
                    "warnings": warnings, "duplicate_rules": [],
                    "error": "style.file_unreadable", "detail": str(exc)}
    return _parse_style_file(style_id, chosen, text, warnings)


def resolve_style(qs, bank_path, settings):
    """Apply the locked selection precedence lesson -> bank -> subject
    profile -> house (D-10) and resolve the winning id through load_style.

    Returns {"id", "style", "level", "warnings"}: `id` is the winning style
    id (always `house` in the fallback), `style` is load_style's dict or
    None when the winning id resolves to nothing (lint then reports
    style.file_unreadable -- never a silent house fallback, D-09), and
    `level` names which precedence level supplied the id.

    `qs` is reserved for future selection integration (the signature is part
    of the plan's contract); resolution today is directive-driven."""
    bank_dir = os.path.dirname(os.path.abspath(bank_path)) or "."
    lesson = parse_lesson(bank_path)
    lesson_id = _style_directive(lesson["body"]) if lesson else ""
    if lesson_id:
        return {"id": lesson_id, "style": load_style(lesson_id, bank_dir),
                "level": "lesson", "warnings": []}
    bank_id = _style_directive(_bank_preamble(bank_path))
    if bank_id:
        return {"id": bank_id, "style": load_style(bank_id, bank_dir),
                "level": "bank", "warnings": []}
    subject_id = ""
    if isinstance(settings, dict):
        subject_id = (settings.get("styles") or {}).get("subject_default") \
            or ""
    if subject_id:
        return {"id": subject_id, "style": load_style(subject_id, bank_dir),
                "level": "subject", "warnings": []}
    house = load_style("house", bank_dir)
    return {"id": "house", "style": house, "level": "house", "warnings": []}


def content_fingerprint(q):
    """A change-detection digest of the *tested* content only, never the
    rationale around it.

    Deliberately excludes `why`, `disc`, `second`, `trap`, `conf`, `da`,
    `notes`, `objective`, `difficulty`, `number`, `id`, `item_id`, `pair`,
    `prereq` and `content_hash` -- the hash's job is to detect that stem, options, correct
    answers, categories, rows, steps, model answer or rubric changed, and
    D-04 already accepts the residual risk that a genuine rewrite of what a
    question asks, while its rationale text stays untouched, still inherits
    the old item's trend data. The drift warning this feeds is the only
    signal for that case.

    `pair` and `prereq` are pedagogy metadata (D-12): editing a confusion-set
    name or a prerequisite objective must not orphan an item's evidence history.

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
    elif t == "visual":
        # The tested content of a visual item is the declarative scene and
        # the private scoring envelope together: changing either the prompt's
        # scene or the accepted/tolerance material must change the
        # fingerprint. JSON is hashed in its canonical (sorted) form so
        # reformatting the bank does not drift the digest.
        parts.append("interaction=" + collapse(q.get("interaction") or ""))
        parts.append("visual=" + json.dumps(q.get("visual") or {},
                                            sort_keys=True, separators=(",", ":")))
        parts.append("scoring=" + json.dumps(q.get("scoring") or {},
                                             sort_keys=True, separators=(",", ":")))
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


def _key_content_hash(block_lines):
    """The change-detection digest of one `> [!KEY]` block's content --
    title and body lines only, never its `[ID:]`/`[HASH:]` directive lines,
    so minting an id never reads as content drift and editing the body
    always does."""
    parts = []
    for line in block_lines:
        stripped = re.sub(r"^>\s?", "", line).strip()
        if re.match(r"^\[(ID|HASH):", stripped):
            continue
        if stripped:
            parts.append(stripped)
    return "sha256:" + hashlib.sha256(
        ("\n".join(parts)).encode("utf-8")).hexdigest()[:16]


def _assign_key_ids(chunk, taken, changes, key_count):
    """Mint `[ID:]`/`[HASH:]` into every `> [!KEY]` block of one preamble
    chunk, using the exact `new_item_id()`/taken-set path items use -- there
    is no separate key id namespace (research Pitfall 5). Returns the
    rewritten chunk text. `key_count` is a one-element list so the K-tags
    stay sequential across chunks."""
    lines = chunk.split("\n")
    out = []
    i = 0
    while i < len(lines):
        m = _KEY_MARK_RE.match(lines[i])
        if m is None:
            out.append(lines[i])
            i += 1
            continue
        start = i
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            i += 1
        block_lines = lines[start:i]
        raw = "\n".join(block_lines)
        key_count[0] += 1
        tag = "K%d" % key_count[0]

        had_id = grab(r"(?m)^>\s*\[ID:\s*(\S+)\s*\]", raw)
        item_id = had_id
        id_action = "kept"
        if not item_id:
            item_id = new_item_id()
            while item_id in taken:
                item_id = new_item_id()
            id_action = "assigned"
        taken.add(item_id)

        old_hash = grab(r"(?m)^>\s*\[HASH:\s*(\S+)\s*\]", raw)
        new_hash = _key_content_hash(block_lines)
        if not old_hash:
            hash_action = "recorded"
        elif old_hash != new_hash:
            hash_action = "updated"
        else:
            hash_action = "unchanged"

        changes.append({"item": tag, "item_id": item_id,
                        "action": id_action, "hash_action": hash_action,
                        "old_hash": old_hash, "new_hash": new_hash})

        if id_action == "kept" and hash_action == "unchanged":
            out.extend(block_lines)
            continue

        new_lines = []
        inserted_id = False
        inserted_hash = False
        for line in block_lines:
            if re.match(r"^>\s*\[ID:", line):
                if had_id:
                    new_lines.append("> [ID: %s]" % item_id)
                    inserted_id = True
                continue
            if re.match(r"^>\s*\[HASH:", line):
                if old_hash:
                    new_lines.append("> [HASH: %s]" % new_hash)
                    inserted_hash = True
                continue
            new_lines.append(line)
        pos = 1
        if not inserted_id:
            new_lines.insert(pos, "> [ID: %s]" % item_id)
            pos += 1
        if not inserted_hash:
            new_lines.insert(pos, "> [HASH: %s]" % new_hash)
        out.extend(new_lines)
    return "\n".join(out)


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
    # Prepass: every existing [ID:] in the bank -- item and key alike --
    # joins the claimed set before anything is minted, so a key can never
    # collide with an item id that already exists in this bank (Pitfall 5).
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()):
            q = parse_question(ch)
            if q and q.get("item_id"):
                taken.add(q["item_id"])
        else:
            for km in re.finditer(r"(?m)^>\s*\[ID:\s*(\S+)\s*\]", ch):
                taken.add(km.group(1))
    changes = []
    out_chunks = []
    idx = 0
    key_count = [0]
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if not re.match(r"Q\d+\.", ch.strip()):
            out_chunks.append(_assign_key_ids(ch, taken, changes, key_count))
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
  [PAIR: <confusion set name>]                               optional
  [PREREQ: <objective>[, <objective>...]]                    optional
  [CASE: <case-id>]                                          optional
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

  [PAIR:] names a confusion set: the same name on two or more items is what
  makes them a set, and a name on exactly one item is an authoring mistake
  (`lint` warns). [PREREQ:] lists objectives this item assumes the learner
  already holds; each entry should name an objective some item in the bank
  teaches (`lint` warns when it does not). [CASE:] attaches the item to a
  named case group; the id must be registered in a `## CASES` preamble block
  (one pipe row per case), and a [PREREQ:] target may also be a case id or an
  item [ID:] -- an unresolvable target or a dependency cycle is a `lint`
  error (prov.case_unknown / prov.prereq_unknown / prov.prereq_cycle).

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

7. Visual assessment.  Interactive plot or number-line item (protocol integer 1,
   phase 06.1). The scene and the private scoring envelope are declarative JSON
   fields, parsed as data and never executed; the served runtime projects only
   the key-free scene, and `score_response()` is the only scorer.
     [TYPE: visual]
     [INTERACTION: plot | numberline]
     [VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
     [SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

   `[INTERACTION:]` names the interaction family: `plot` (two axes x and y) or
   `numberline` (one axis). `[VISUAL:]` is the public scene: `version` (the
   protocol integer, 1), `axes`/`axis` (each with SCALAR `min`, `max`, `step`,
   step strictly positive and the span at most 200 whole steps, i.e. 201 ticks),
   `initial` (the starting committed state), `actions` (a non-empty subset of
   the four locked action types `place_point`, `move_point`,
   `select_numberline_point`, `set_interval`), and `accessibility.description`
   (required: the SVG's name/description and the semantic fallback are built
   from it). `[SCORING:]` is private -- it never leaves the server. `kind` is
   one of `point`, `numberline_point`, `interval`; `accepted` lists the
   accepted semantic states; `tolerance` is per-field non-negative SCALAR (0 =
   exact discrete compare); `partial_credit` must be false (dichotomous).

   SCALAR grammar (protocol integer 1): a signed base-10 integer or decimal
   with at most six fractional digits, or a rational INTEGER/POSITIVE_INTEGER.
   Exponents, NaN, infinities, mixed numbers, units and symbolic expressions
   are invalid. The runtime canonicalizes with fractions.Fraction (rational
   reduction, trailing-zero removal, -0 -> "0", bounded numerator/denominator);
   browser floats and pixels are never evidence or scoring inputs. Wire
   responses are exactly:
     {"kind":"point","x":SCALAR,"y":SCALAR}
     {"kind":"numberline_point","value":SCALAR}
     {"kind":"interval","start":SCALAR,"end":SCALAR,"start_closed":BOOL,"end_closed":BOOL}
   Interval endpoints canonicalize into ascending order with closure flags
   swapped when needed. The public `interaction_contract` (version, type,
   interaction, renderer_config, response_schema) is what a renderer or agent
   receives; accepted states, tolerance, and reveal content are never in it.

   Phase 999.1 extends the same protocol integer 1 additively with the
   `hotspot`, `timeline`, `diagram`, and `trace` families (same envelope,
   same interact/evidence machinery; the closed allowlists grow, nothing is
   renumbered). Scene members are closed per interaction; identifiers follow
   `[A-Za-z0-9_-]{1,64}` and are stable authored strings, never pixels.

   Hotspot (click-on-region mapping). The learner selects one named region of
   a plane.
     [INTERACTION: hotspot]
     [VISUAL: {"version":1,"plane":{"width":"10","height":"6"},"regions":[{"id":"heart","label":"Heart","shape":"circle","coords":["2","3","1.5"]},{"id":"liver","label":"Liver","shape":"rect","coords":["6","2","3","2"]},{"id":"lungs","label":"Lungs","shape":"polygon","coords":[["1","5"],["4","5"],["2.5","3.5"]]}],"initial":{"region":null},"actions":["select_hotspot"],"accessibility":{"description":"A diagram of three organs. Select the heart."}}]
     [SCORING: {"kind":"hotspot","accepted":[{"region":"heart"}],"tolerance":{},"partial_credit":false}]
   `plane` is `{width, height}` in positive SCALARs; `regions` entries are
   `{id, label, shape, coords}` with `shape` one of `rect` ([x,y,w,h]),
   `circle` ([cx,cy,r]) or `polygon` ([[x,y],...] with at least 3 in-plane
   vertices), all SCALARs inside the plane, unique ids. Wire response:
     {"kind":"hotspot","region":ID}
   Scoring is exact region-id equality; a non-zero tolerance is an authoring
   error (the family is exact-id). `initial.region` is the pre-selected
   region or null.

   Timeline (place one authored event at a time value). Same `axis` grammar
   as numberline plus `events` [{id,label}]:
     [INTERACTION: timeline]
     [VISUAL: {"version":1,"axis":{"min":"0","max":"10","step":"1"},"events":[{"id":"fall","label":"Fall of Rome"},{"id":"printing","label":"Printing press"}],"initial":{"placements":[]},"actions":["place_timeline_event"],"accessibility":{"description":"A timeline from 0 to 10. Place the fall of Rome at year 5."}}]
     [SCORING: {"kind":"timeline_event","accepted":[{"event":"fall","value":"5"}],"tolerance":{"value":"0"},"partial_credit":false}]
   Wire response: {"kind":"timeline_event","event":ID,"value":SCALAR}.
   Scoring compares the event id exactly and the value within the private
   per-coordinate tolerance (0 = exact tick compare). Committed actions:
   `place_timeline_event`, `move_timeline_event`.

   Diagram (connect two authored nodes). `plane` plus `nodes` [{id,label,x,y}]
   in plane units:
     [INTERACTION: diagram]
     [VISUAL: {"version":1,"plane":{"width":"8","height":"6"},"nodes":[{"id":"a","label":"Premise A","x":"2","y":"4"},{"id":"b","label":"Premise B","x":"6","y":"4"},{"id":"c","label":"Conclusion","x":"4","y":"1"}],"initial":{"connections":[]},"actions":["connect_diagram"],"accessibility":{"description":"An argument diagram. Connect the two premises to the conclusion."}}]
     [SCORING: {"kind":"diagram_connection","accepted":[{"from":"a","to":"c"}],"tolerance":{},"partial_credit":false}]
   Wire response: {"kind":"diagram_connection","from":ID,"to":ID}. The pair
   is ordered, `from` must differ from `to`, both ids must be known, and
   scoring is exact (non-zero tolerance is an authoring error).

   Trace (re-trace a reference path with a fixed number of points). Same
   `axes` geometry as plot plus `point_count` (integer 1..50); the public
   `initial.points` reference polyline is scene data the renderer draws, while
   the accepted path lives only in the private SCORING envelope:
     [INTERACTION: trace]
     [VISUAL: {"version":1,"axes":{"x":{"min":"0","max":"4","step":"1"},"y":{"min":"0","max":"4","step":"1"}},"point_count":3,"initial":{"points":[{"x":"0","y":"0"},{"x":"2","y":"2"},{"x":"4","y":"0"}]},"actions":["place_trace_point","move_trace_point"],"accessibility":{"description":"A grid with a V-shaped path. Place three points along it."}}]
     [SCORING: {"kind":"trace_path","accepted":[{"points":[{"x":"0","y":"0"},{"x":"2","y":"2"},{"x":"4","y":"0"}]}],"tolerance":{"x":"1/2","y":"1/2"},"partial_credit":false}]
   Wire response: {"kind":"trace_path","points":[{"x":SCALAR,"y":SCALAR},...]}.
   The submitted point count must equal `point_count` and each point is
   compared element-wise in order within the private per-coordinate
   tolerance; a count mismatch, out-of-domain point, or off-grid point fails
   closed.

   SVG/HTML role policy (D-07): HTML owns the prompt, controls, status and
   semantic fallback; SVG owns the retained plot/number-line geometry. A canvas
   renderer is permitted only for a dense simulation while the identical
   semantic HTML state/control path remains present and operable. Committed
   semantic actions and runtime observations are append-only evidence; raw
   pointer movement is never recorded.

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

  An item's [LESSON-REF:] tag names readable heading text, not an id; if an
  item carries more than one [LESSON-REF:] tag, only the first is read. A
  referenced heading's text must not contain `]` -- the tag reads up to the
  first closing bracket, so a bracketed heading can never be named. The tag
  itself is listed above with the other shared fields.

THE SLUG RULE
  A heading's slug is its text lowercased, whitespace collapsed, and every
  character outside ASCII letters, digits, spaces and hyphens dropped; each
  run of whitespace becomes a single hyphen. Hyphens are kept, so "A-B" and
  "AB" do not collide. Two headings whose slugs collide make a reference to
  either ambiguous, so the collision is an error: author headings that differ
  in more than casing, spacing and punctuation, and you can predict the
  collision before the linter reports it.

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
VISUAL LINT CODES
  item.visual_json_malformed       error   [VISUAL:] or [SCORING:] is not valid JSON
  item.visual_unknown_interaction  error   INTERACTION is not one of the six families
  item.visual_unknown_action       error   an action is outside the locked action types
  item.visual_unknown_scoring_kind error   SCORING.kind is unknown or does not match
                                           the INTERACTION family
  item.visual_unknown_member       error   a top-level VISUAL/SCORING member is outside
                                           the per-interaction closed allowlist
  item.visual_invalid_axis         error   axis min/max/step geometry is invalid
  item.visual_invalid_scalar       error   a SCALAR violates the protocol-1 grammar
  item.visual_invalid_tolerance    error   a tolerance is not a non-negative SCALAR,
                                           or is non-zero on an exact-id family
  item.visual_invalid_scoring_kind error   partial_credit is not false (dichotomous)
  item.visual_empty_accessibility  error   accessibility.description is empty
  item.visual_duplicate_id         error   scene ids (points, regions, events,
                                           nodes) are duplicated
  item.visual_invalid_geometry     error   plane/regions/events/nodes geometry,
                                           coords, or point_count is malformed
  item.visual_executable_member    error   a script-bearing/executable member is present
  lesson.invalid_gate       error     [GATE:] names a value outside
                                      required|recommended|off
  lesson.check_ref_unknown  error     [!CHECK: <id>] names no item in its own
                                      bank (D-01)
"""


# The Phase 6.2 gate grammar (06.2-CONTEXT D-02): one [GATE:] directive in
# the lesson preamble with exactly three legal values; a lesson declaring
# none defaults to "recommended". The value is validated at lint time -- an
# invalid value is a named lint error, never a render-time crash and never
# a silent default (T-062-01).
GATE_VALUES = ("required", "recommended", "off")

# The one source of truth for the unresolvable [!CHECK:] copy (06.2-UI-SPEC
# section 15, LOCKED): the linter, the lesson renderer and the tests all
# read this constant -- never a duplicate string literal -- so the
# cross-phase divergence guard (06.2-UI-SPEC section 13 gate 12) holds by
# construction. The literal `<bank>` placeholder is filled with the bank
# basename by the renderer; the linter is `itembank lint`, so its message
# carries the sentence verbatim.
CHECK_UNRESOLVED_COPY = ("This check refers to an item that is not in this "
                         "bank. Run itembank lint <bank> for details.")


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


# The same sentinel pattern for the TERMS/key pass (plan 03.1-02): "the
# caller did not supply TERMS data" (skip every terms/key check -- the
# behaviour every pre-03.1-02 caller relies on) stays distinct from "the
# caller supplied TERMS data and this bank has no `## TERMS` section", where
# every [[term]] reference is unknown rather than skipped.
TERMS_UNCHECKED = object()


# The same sentinel for the [!KEY] block pass (plan 03.1-03): "the caller
# did not supply key data" (skip every key-block check -- the behaviour
# every pre-03.1-03 caller relies on) stays distinct from "the caller
# supplied key data and this bank has no key blocks", where an empty list
# is a legitimate no-op rather than a skip.
KEYS_UNCHECKED = object()


# The same sentinel pattern for the style pass (plan 03.1-04): "the caller
# did not supply style data" (skip every style check -- the behaviour every
# pre-03.1-04 caller relies on) stays distinct from "the caller supplied
# style data and the style file could not be read", where
# style.file_unreadable fires instead of a silent house fallback (D-09:
# an unresolvable id is never a silent shadow).
STYLE_UNCHECKED = object()


# The same sentinel pattern for the provenance pass (plan 03.2-02): "the
# caller did not supply provenance data" (skip every ## SOURCES / [SRC:] /
# [OBJ:] check -- the behaviour every pre-03.2-02 caller relies on) stays
# distinct from "the caller supplied provenance data and this bank carries no
# provenance constructs", where parse_sources() returns None and no directive
# exists to check.
SOURCES_UNCHECKED = object()


# The same sentinel pattern for the [CASE:]/[PREREQ:] pass (plan 03.2-04):
# "the caller did not supply case/prereq data" (skip every case/prereq check)
# stays distinct from "the caller supplied it and the bank carries no
# case/prereq constructs", where parse_cases() returns None and nothing exists
# to check.
CASES_UNCHECKED = object()


# The same sentinel pattern for the winnowing paraphrase pass (plan 03.2-04):
# the paraphrase checks stay off unless the caller passes a thresholds dict
# (the settings group `paraphrase`), so every pre-03.2-04 caller gets
# byte-for-byte the same lint output it got before.
PARAPHRASE_UNCHECKED = object()


# The closed rule-kind catalogue (D-16, Pitfall 3): a style row may
# parameterize exactly these kinds, and a row claiming anything else is
# style.rule_unimplemented before the rule is ever applied. `house.mandate`
# is the house-only kind that carries the Directive Â§4 non-negotiables; it
# is documented in styles/house.md and owned by LOCKED_RULE_IDS below, never
# by the file (ruling 13, Open Question 1).
STYLE_RULE_KINDS = frozenset({
    "order.before", "density.max", "style.require", "style.forbid",
    "cadence.section", "open.with", "house.mandate",
})


# The locked house rows, as code constants (ruling 13, Open Question 1):
# styles/house.md documents them in prose; this set decides. A style file may
# not override, suppress, or re-severity a locked id (T-031-12). The five
# Directive Â§4 non-negotiables split into six ids because Â§4.2 is two rows
# (one parser, one scorer).
LOCKED_RULE_IDS = frozenset({
    "runtime.decides",        # Â§4.1 -- the runtime, not a model, decides what reaches the learner
    "no.second.parser",       # Â§4.2 -- exactly one parser
    "no.second.scorer",       # Â§4.2 -- exactly one scorer
    "no.evidence.leave",      # Â§4.3 -- evidence and banks stay on disk
    "format.additive",        # Â§4.4 -- format changes are additive
    "accessibility.gates",    # Â§4.5 -- the nine UI-SPEC Â§8 gates
})


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
    "item.pair_singleton", "item.prereq_unknown",
    "lesson.duplicate_heading", "lesson.orphan_heading", "lesson.src_unreadable",
    "terms.unknown_ref", "terms.duplicate_slug", "terms.empty_block",
    "key.in_rationale", "key.duplicate_id",
    "key.no_front", "key.missing_id", "key.missing_hash",
    "prov.obj_unknown", "prov.src_duplicate", "prov.src_unknown",
    "prov.paraphrase_copy", "prov.paraphrase_overlap",
    "prov.case_unknown", "prov.prereq_unknown", "prov.prereq_cycle",
    "style.unsourced_specific",
    "style.parent_unknown", "style.rule_unimplemented", "style.duplicate_id",
    "style.file_unreadable", "style.override_locked", "style.ignore_locked",
    "style.unknown_parameter", "style.parameter_out_of_range",
    "style.order_before", "style.heading_cadence", "style.require_marker",
    "style.forbidden_marker", "style.open_with", "style.section_density",
    "style.sentence_length", "style.filler_phrase", "style.banned_hector",
    "style.forbidden_phrase",
    "item.objective_line_multi_sentence",
    "item.visual_json_malformed", "item.visual_unknown_interaction",
    "item.visual_unknown_action", "item.visual_unknown_scoring_kind",
    "item.visual_unknown_member", "item.visual_invalid_axis",
    "item.visual_invalid_scalar", "item.visual_invalid_tolerance",
    "item.visual_invalid_scoring_kind",
    "item.visual_empty_accessibility", "item.visual_duplicate_id",
    "item.visual_invalid_geometry",
    "item.visual_executable_member",
    "bank.answer_position_skew",
    "lesson.invalid_gate", "lesson.check_ref_unknown",
}))


# ---- style enforcement (plan 03.1-05) --------------------------------------
# The one shared lexical metrics pass is driven by pre-compiled, deliberately
# backtracking-free regexes (the WOULD_BE precedent, T-031-18) so the whole
# style pass stays under the 50ms/5000-word budget without a cache.
_STYLE_FENCE_RE = re.compile(r"(?ms)^```.*?^```\s*")
_STYLE_CODE_SPAN_RE = re.compile(r"`[^`\n]*`")
_STYLE_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_STYLE_WORD_RE = re.compile(r"\S+")
_STYLE_FILLER_RE = re.compile(
    r"\b(?:a lot of|in order to|due to the fact that|as a matter of fact|"
    r"needless to say|basically|actually|obviously|kind of|sort of|"
    r"pretty much|very|really|quite|just)\b", re.I)
_STYLE_HECTOR_RE = re.compile(
    r"\b(?:you must|you have to|you need to|you should|you always|you never|"
    r"do not forget|don't forget|make sure you remember|remember to|"
    r"you absolutely must)\b", re.I)
_STYLE_REFERENCE_RE = re.compile(
    r"\b(?:see also|see section|see chapter|refer to|further reading|"
    r"for more (?:information|details)|for reference)\b", re.I)
_STYLE_IGNORE_RE = re.compile(r"<!--\s*style-ignore:\s*([A-Za-z0-9_.-]+)")

# The severity vocabulary of a `## Rules` severity cell. `manual` is the
# sanctioned declaration for a discourse rule (D-12 class 3, criterion 3c):
# Phase 11 judgement, skipped here with a note, never fabricated into a check.
STYLE_SEVERITIES = frozenset({"off", "warn", "error", "manual"})

# The closed check catalogue (D-13): every style.* content code the pass can
# emit, with the severity ceiling a style file may not raise. `error` is
# earned by construction -- structural counts or author-controlled literal
# lists; anything that pattern-matches natural language caps at `warn`
# (research section 3.1). Adding a check is a code change in this module plus
# a LINT_CODES entry; a style file can never add one.
STYLE_CHECK_CATALOGUE = {
    "style.order_before": "error",
    "style.heading_cadence": "error",
    "style.require_marker": "error",
    "style.forbidden_marker": "error",
    "style.open_with": "error",
    "style.section_density": "warn",
    "style.sentence_length": "warn",
    "style.filler_phrase": "warn",
    "style.banned_hector": "warn",
    "style.forbidden_phrase": "warn",
}


def _style_lexical_metrics(text):
    """The one shared lexical metrics pass (D-12 class 2): a single
    tokenisation over the lesson prose that every lexical check reads, so a
    lesson is scanned once per lint, not once per check. Fenced and inline
    code spans are masked first (the research's 'code-span masks')."""
    body = _STYLE_FENCE_RE.sub(" ", text or "")
    body = _STYLE_CODE_SPAN_RE.sub(" ", body)
    return {
        "word_count": len(_STYLE_WORD_RE.findall(body)),
        "sentences": [s.strip() for s in _STYLE_SENTENCE_RE.split(body)
                      if s.strip()],
        "filler": len(_STYLE_FILLER_RE.findall(body)),
        "hector": len(_STYLE_HECTOR_RE.findall(body)),
        "reference": len(_STYLE_REFERENCE_RE.findall(body)),
    }


def _style_sections(lesson):
    """The parsed heading tree as (text, slug, body) dicts; empty when the
    lesson carries no sections or carries an unreadable-source error, so no
    structural check fires on data that was never parsed."""
    if not isinstance(lesson, dict) or lesson.get("error"):
        return []
    return lesson.get("headings") or []


def _style_lesson_body(lesson):
    """The whole LESSON text (the suppression-comment and lexical surface)."""
    if not isinstance(lesson, dict) or lesson.get("error"):
        return ""
    return lesson.get("body") or ""


def _style_split_params(params):
    return [p.strip() for p in (params or "").split(",") if p.strip()]


def _style_is_int(s):
    try:
        int(s)
        return True
    except (TypeError, ValueError):
        return False


def _style_marker_prefix(token):
    """The search prefix for a marker token: '[!KEY]' and '[!CHECK: id]' both
    match the prefix '[!KEY' / '[!CHECK', so a rule naming a marker catches
    both the bare and the anchored form."""
    t = token.strip()
    return t.rstrip("]") if t.startswith("[!") else t


def _style_first_line(body):
    for line in (body or "").splitlines():
        if line.strip():
            return line.strip()
    return None


def _style_first_pos(body, token):
    """Position of the first occurrence of `token` in a section body, or
    None. `paragraph` means the first prose paragraph -- the first non-blank
    line that is neither a marker, a callout, a list, a table, a fence nor a
    heading."""
    token = token.strip()
    if not token:
        return None
    if token.lower() == "paragraph":
        for m in re.finditer(r"(?m)^\s*(\S.*?)\s*$", body or ""):
            line = m.group(1)
            if line.startswith((">", "|", "- ", "* ", "```", "###", "[!")):
                continue
            return m.start()
        return None
    idx = (body or "").find(_style_marker_prefix(token))
    return idx if idx >= 0 else None


def _style_count(body, token):
    """Occurrence count of `token` in `body`: a `##` heading line, a `[!...]`
    marker (bare or anchored), or a whole word."""
    token = token.strip()
    if not token:
        return 0
    if token.startswith("##"):
        return len(re.findall(r"(?m)^" + re.escape(token) + r"\s*$", body or ""))
    if token.startswith("[!"):
        return len(re.findall(re.escape(_style_marker_prefix(token)), body or ""))
    return len(re.findall(r"(?i)\b" + re.escape(token) + r"\b", body or ""))


def _style_row_severity(row):
    """Normalise a row's severity cell. Returns (severity, error): severity is
    one of STYLE_SEVERITIES, or None with an error LintError for a cell the
    linter does not implement (D-16 -- a claim is not silently accepted)."""
    sev = (row.get("severity") or "warn").strip().lower()
    if sev in STYLE_SEVERITIES:
        return sev, None
    return None, LintError(
        "style.unknown_parameter", "rules", "BANK",
        "rule '%s' declares severity '%s', which the linter does not "
        "implement; choose one of %s (D-16)"
        % (row.get("id") or "?", row.get("severity") or "?",
           ", ".join(sorted(STYLE_SEVERITIES))))


def run_style_pass(lesson, style):
    """The style content pass (D-12, plan 03.1-05 Task 1). Class 1 structural
    counts over the parsed heading tree and class 2 the one shared lexical
    metrics pass run on every lint; class 3 discourse judgement defers to
    Phase 11 -- a row declaring severity `manual` is skipped by note and never
    fabricated into a check.

    Returns (errors, warnings) as LintError records. The check catalogue is
    closed (D-13): every finding code is a member of STYLE_CHECK_CATALOGUE, a
    style row may enable/disable/re-severity downward/parameterize a check but
    never define one, and error severity is earned by construction -- a row
    may not raise a check above its catalogue rating
    (`style.parameter_out_of_range`, the research's ceiling code)."""
    errors, warnings = [], []
    if not isinstance(style, dict) or style.get("error"):
        return errors, warnings
    if lesson is LESSON_UNCHECKED:
        # The caller never supplied lesson data (the additive opt-out
        # sentinel from lint()): there is no lesson surface to check, so
        # the content pass fires nothing -- a caller that never heard of
        # lessons gets byte-for-byte what it got before. A real parsed
        # lesson (a dict) or an absent-lesson bank (None) still get full
        # enforcement; this guard only matches the "lesson checks off"
        # sentinel (03.1-05, D-12).
        return errors, warnings
    sections = _style_sections(lesson)
    body = _style_lesson_body(lesson)
    metrics = _style_lexical_metrics(body)

    def finding(code, message, severity="error"):
        (errors if severity == "error" else warnings).append(
            LintError(code, "lesson", "BANK", message))

    def ceiling(row, code, sev):
        """Enforce the earned-severity ceiling (D-13): a row may re-severity
        downward but never raise a check above its catalogue rating."""
        rating = STYLE_CHECK_CATALOGUE[code]
        if sev == "error" and rating == "warn":
            errors.append(LintError(
                "style.parameter_out_of_range", "rules", "BANK",
                "rule '%s' tries to raise %s above its catalogue rating (%s); "
                "error severity is earned by construction (D-13)"
                % (row.get("id") or "?", code, rating)))
            return "warn"
        return sev

    # ---- lexical configuration from binding rows (class 2) -----------------
    # sentence-length ceiling, filler phrases, and banned hector words are
    # always-on within the style pass; a row binding the check may disable it,
    # re-severity it downward, or parameterize it. A style.forbid row naming a
    # reference-material category adds the row-driven forbidden_phrase check.
    lexical = {
        "style.sentence_length": {"severity": "warn", "max": 28},
        "style.filler_phrase": {"severity": "warn"},
        "style.banned_hector": {"severity": "warn"},
    }

    def bind_lexical(code, row):
        lexical.setdefault(code, {"severity": STYLE_CHECK_CATALOGUE[code]})
        sev, sev_err = _style_row_severity(row)
        if sev_err is not None:
            errors.append(sev_err)
            return
        if sev in ("manual", "off"):
            lexical[code]["severity"] = sev
            return
        lexical[code]["severity"] = ceiling(row, code, sev)
        for tok in _style_split_params(row.get("params") or ""):
            if "=" in tok:
                k, _, v = tok.partition("=")
                lexical[code].setdefault("params", {})[k.strip()] = v.strip()

    for row in style.get("rules") or []:
        rid = (row.get("id") or "").strip()
        kind = row.get("kind") or ""
        params = _style_split_params(row.get("params") or "")
        if rid in STYLE_CHECK_CATALOGUE:
            bind_lexical(rid, row)
        elif kind == "density.max" and params and params[0].startswith("style."):
            if params[0] in STYLE_CHECK_CATALOGUE:
                bind_lexical(params[0], row)
        elif kind == "style.forbid":
            target = params[0] if params else ""
            if target == "second-person-hectoring":
                bind_lexical("style.banned_hector", row)
            elif target == "reference-material":
                bind_lexical("style.forbidden_phrase", row)

    for code, cfg in lexical.items():
        if cfg.get("severity") in ("off", "manual"):
            continue
        if code == "style.sentence_length":
            try:
                ceiling_n = int(cfg.get("params", {}).get("max", 28))
            except (TypeError, ValueError):
                ceiling_n = 28
            if ceiling_n < 1:
                errors.append(LintError(
                    "style.parameter_out_of_range", "rules", "BANK",
                    "style.sentence_length max=%s is out of range (min 1)"
                    % cfg.get("params", {}).get("max", 28)))
                continue
            for s in metrics["sentences"]:
                n = len(_STYLE_WORD_RE.findall(s))
                if n > ceiling_n:
                    finding("style.sentence_length",
                            "%d-word sentence exceeds the style's %d-word "
                            "ceiling" % (n, ceiling_n), cfg["severity"])
        elif code == "style.filler_phrase" and metrics["filler"]:
            finding("style.filler_phrase",
                    "%d filler phrase(s) in the lesson prose (the style bans "
                    "them)" % metrics["filler"], cfg["severity"])
        elif code == "style.banned_hector" and metrics["hector"]:
            finding("style.banned_hector",
                    "%d banned hector word(s) in the lesson prose"
                    % metrics["hector"], cfg["severity"])
        elif code == "style.forbidden_phrase" and metrics["reference"]:
            finding("style.forbidden_phrase",
                    "%d reference-material phrase(s) in the lesson prose"
                    % metrics["reference"], cfg["severity"])

    # ---- structural counts over the parsed heading tree (class 1) ---------
    for row in style.get("rules") or []:
        rid = (row.get("id") or "").strip()
        kind = row.get("kind") or ""
        params = _style_split_params(row.get("params") or "")
        sev, sev_err = _style_row_severity(row)
        if sev_err is not None:
            errors.append(sev_err)
            continue
        if sev in ("manual", "off"):
            continue
        if rid in STYLE_CHECK_CATALOGUE:
            continue  # already handled as lexical config above
        if kind == "house.mandate":
            continue  # registry-only, policed by lint()'s 03.1-04 block

        if kind == "order.before":
            if len(params) != 2:
                errors.append(LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (order.before) needs exactly two comma-separated "
                    "tokens, got %r" % (rid, row.get("params") or "")))
                continue
            a, b = params[0], params[1]
            effective = ceiling(row, "style.order_before", sev)
            for h in sections:
                pa = _style_first_pos(h["body"], a)
                pb = _style_first_pos(h["body"], b)
                if pa is not None and pb is not None and pb < pa:
                    finding("style.order_before",
                            "section '%s' has %s before %s; the style requires "
                            "%s before %s" % (h["text"], b, a, a, b),
                            effective)
        elif kind == "cadence.section":
            if not params:
                errors.append(LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (cadence.section) has no params" % rid))
                continue
            effective = ceiling(row, "style.heading_cadence", sev)
            if len(params) == 2 and _style_is_int(params[0]) \
                    and _style_is_int(params[1]):
                lo, hi = int(params[0]), int(params[1])
                if lo < 0 or hi <= lo:
                    errors.append(LintError(
                        "style.parameter_out_of_range", "rules", "BANK",
                        "rule '%s' declares cadence bounds %s, %s; need "
                        "0 <= min < max" % (rid, lo, hi)))
                    continue
                for h in sections:
                    n = len(_STYLE_WORD_RE.findall(h["body"] or ""))
                    if n < lo or n > hi:
                        finding("style.heading_cadence",
                                "section '%s' is %d words; the style bounds "
                                "sections to %d..%d words"
                                % (h["text"], n, lo, hi), effective)
            else:
                # MD043-style declared heading skeleton: every declared
                # heading must appear in the lesson, in the declared order.
                actual = [h["slug"] for h in sections]
                pos = 0
                for name in params:
                    slug = lesson_slug(name)
                    if slug not in actual:
                        finding("style.heading_cadence",
                                "declared section '%s' is missing from the "
                                "lesson" % name, effective)
                        continue
                    idx = actual.index(slug)
                    if idx < pos:
                        finding("style.heading_cadence",
                                "declared section '%s' appears out of order"
                                % name, effective)
                    pos = idx + 1
        elif kind == "style.require":
            if len(params) != 2:
                errors.append(LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (style.require) needs a marker and a count, "
                    "got %r" % (rid, row.get("params") or "")))
                continue
            marker, n_tok = params[0], params[1]
            if not _style_is_int(n_tok) or int(n_tok) < 1:
                errors.append(LintError(
                    "style.parameter_out_of_range", "rules", "BANK",
                    "rule '%s' (style.require) needs a positive count, got "
                    "'%s'" % (rid, n_tok)))
                continue
            n = int(n_tok)
            effective = ceiling(row, "style.require_marker", sev)
            if marker.startswith("##"):
                count = _style_count(body, marker)
                if count < n:
                    finding("style.require_marker",
                            "the lesson needs at least %d %s, found %d"
                            % (n, marker, count), effective)
            else:
                for h in sections:
                    count = _style_count(h["body"], marker)
                    if count < n:
                        finding("style.require_marker",
                                "section '%s' needs at least %d %s, found %d"
                                % (h["text"], n, marker, count), effective)
        elif kind == "style.forbid":
            if len(params) != 1:
                errors.append(LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (style.forbid) names exactly one target, got %r"
                    % (rid, row.get("params") or "")))
                continue
            target = params[0]
            if target in ("second-person-hectoring", "reference-material",
                          "style.banned_hector", "style.forbidden_phrase"):
                continue  # handled in the lexical binding pass
            if target.startswith(("[!", "##")):
                effective = ceiling(row, "style.forbidden_marker", sev)
                count = _style_count(body, target)
                if count:
                    finding("style.forbidden_marker",
                            "the style forbids %s, found %d in the lesson"
                            % (target, count), effective)
            else:
                errors.append(LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (style.forbid) names '%s', which is not a "
                    "known forbidden category or marker" % (rid, target)))
        elif kind == "open.with":
            if len(params) != 1:
                errors.append(LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (open.with) names one target, got %r"
                    % (rid, row.get("params") or "")))
                continue
            target = params[0]
            effective = ceiling(row, "style.open_with", sev)
            for h in sections:
                first = _style_first_line(h["body"])
                if first is None:
                    continue
                if target.lower() == "prose":
                    if first.startswith(("[!", ">", "```")):
                        finding("style.open_with",
                                "section '%s' must open with prose, got %r"
                                % (h["text"], first), effective)
                elif not first.startswith(_style_marker_prefix(target)):
                    finding("style.open_with",
                            "section '%s' must open with %s, got %r"
                            % (h["text"], target, first), effective)
        elif kind == "density.max":
            if len(params) != 2:
                errors.append(LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (density.max) needs a target and a cap, got %r"
                    % (rid, row.get("params") or "")))
                continue
            x, n_tok = params[0], params[1]
            if x.startswith("style."):
                continue  # lexical config, handled above
            if not _style_is_int(n_tok) or int(n_tok) < 1:
                errors.append(LintError(
                    "style.parameter_out_of_range", "rules", "BANK",
                    "rule '%s' (density.max) needs a positive cap, got '%s'"
                    % (rid, n_tok)))
                continue
            n = int(n_tok)
            effective = ceiling(row, "style.section_density", sev)
            for h in sections:
                count = _style_count(h["body"], x)
                if count > n:
                    finding("style.section_density",
                            "section '%s' uses %s %d times; the style caps it "
                            "at %d" % (h["text"], x, count, n), effective)
    return errors, warnings


def style_manual_rules(style):
    """Rows declared `manual` -- the discourse rules Phase 11 owns (D-12
    class 3). The style pass skips them by note; they are never fabricated
    into checks (criterion 3c)."""
    if not isinstance(style, dict):
        return []
    return [row.get("id") or "" for row in style.get("rules") or []
            if (row.get("severity") or "").strip().lower() == "manual"]


def apply_style_ignore(findings, lesson_text):
    """Filter style findings suppressed by local `<!-- style-ignore: <code> -->`
    comments (D-14, ruling 13). A suppression naming a LOCKED_RULE_IDS id is
    itself lint error `style.ignore_locked` and suppresses nothing -- the
    locked check runs before the ignore table is consulted (T-031-19).
    Returns (kept, suppressed_counts, ignore_errors)."""
    suppressed = set(_STYLE_IGNORE_RE.findall(lesson_text or ""))
    locked = sorted(suppressed & LOCKED_RULE_IDS)
    ignore_errors = [
        LintError("style.ignore_locked", "body", "BANK",
                  "locked rule '%s' may never be suppressed; "
                  "LOCKED_RULE_IDS decides it" % rid) for rid in locked]
    # A locked-id suppression never suppresses: the finding stands and the
    # attempt is itself the lint error above (T-031-19). Only non-locked
    # codes are filtered and counted.
    removable = suppressed - set(locked)
    kept = [f for f in findings if f.code not in removable]
    counts = collections.Counter(
        f.code for f in findings if f.code in removable)
    return kept, dict(counts), ignore_errors


def style_suppression_report(lesson_text):
    """Per-code suppression counts and lesson line locations -- the report
    that retires bad checks (D-14, ruling 13): a check suppressed more often
    than it is heeded is a check that is wrong, and this report says so
    without anyone needing to notice. The named failure mode it prevents is
    an unsuppressable warning getting its whole category globally disabled."""
    counts = collections.Counter()
    locations = {}
    text = lesson_text or ""
    for m in _STYLE_IGNORE_RE.finditer(text):
        code = m.group(1)
        counts[code] += 1
        locations.setdefault(code, []).append(text.count("\n", 0, m.start()) + 1)
    return [{"code": c, "count": counts[c],
             "locations": sorted(set(locations[c]))} for c in sorted(counts)]


# Warning calibration seam (D-14, Task 2): Phase 3.2 owns the corpus and the
# calibration run; this phase owns the checks. Until a rate exists a warning
# ships enabled at its catalogue rating. Phase 3.2 populates this table, and
# a rate above WARNING_FP_THRESHOLD ships the check disabled by default with
# the rate recorded beside the code.
STYLE_WARNING_FP_RATES = {}
WARNING_FP_THRESHOLD = 0.20


def warning_ship_state(code, fp_rate=None):
    """The ship-state of a style warning from its recorded false-positive
    rate: above WARNING_FP_THRESHOLD the check ships disabled by default and
    stays in the catalogue, opt-in per style (research section 3.2). The rate
    is recorded beside the code in the returned record."""
    rate = STYLE_WARNING_FP_RATES.get(code) if fp_rate is None else fp_rate
    return {"code": code, "fp_rate": rate,
            "ship_state": "enabled"
            if rate is None or rate <= WARNING_FP_THRESHOLD else "disabled"}


def write_allowed(style, errors):
    """D-15: a style error blocks a machine-authored write and never a
    human's lint -- the authoring loop consults this gate; a human's lint run
    still returns the full diagnosis and keeps the pen."""
    if style is None or style.get("error"):
        return False
    return not any(e.code.startswith("style.") for e in errors)


class StylePrompt:
    """Compiles a style file's Rules rows into the distilled imperative set
    the authoring model receives (D-17, criterion 3d): one imperative per
    enforceable rule, capped and placed last in the returned context, plus
    exactly one exemplar. The `## Voice` prose zone is never emitted and the
    style file is never embedded verbatim -- the model gets imperatives, not
    an essay."""

    DEFAULT_CAP = 7

    @staticmethod
    def prompt_context(style, cap=None):
        """The style context for the authoring prompt: distilled imperatives
        (capped, default StylePrompt.DEFAULT_CAP), then exactly one exemplar,
        with nothing after them. `## Voice` prose never appears."""
        if cap is None:
            cap = StylePrompt.DEFAULT_CAP
        cap = max(0, int(cap))
        imperatives = StylePrompt._imperatives(style)[:cap]
        blocks = ["## Style requirements",
                  "Follow these style requirements, then imitate the exemplar."]
        if imperatives:
            blocks.append("")
            blocks.extend("- " + i for i in imperatives)
        blocks.append("")
        blocks.append("## Exemplar")
        blocks.append((style.get("exemplar") or "").strip() or "(no exemplar)")
        return "\n".join(blocks)

    @staticmethod
    def _imperatives(style):
        """One distilled imperative per enforceable, prompt-worthy rule, in
        the Rules table's document order. `prompt: yes` rows are the ones the
        style's author chose to surface to the model; disabled (`off`) and
        deferred (`manual`) rows are not enforceable and are skipped."""
        if not isinstance(style, dict):
            return []
        out = []
        for row in style.get("rules") or []:
            sev = (row.get("severity") or "").strip().lower()
            if sev in ("off", "manual"):
                continue
            if (row.get("prompt") or "").strip().lower() != "yes":
                continue
            imp = StylePrompt._distil(row)
            if imp:
                out.append(imp)
        return out

    @staticmethod
    def _distil(row):
        kind = row.get("kind") or ""
        params = _style_split_params(row.get("params") or "")

        def p(i):
            return params[i] if i < len(params) else ""

        if kind == "order.before" and len(params) == 2:
            return "Order each section so %s comes before %s." % (p(0), p(1))
        if kind == "cadence.section" and len(params) == 2 \
                and _style_is_int(p(0)) and _style_is_int(p(1)):
            return "Keep every section between %s and %s words." % (p(0), p(1))
        if kind == "cadence.section" and params:
            return "Use exactly these section headings, in order: %s." \
                % ", ".join(params)
        if kind == "style.require" and len(params) == 2:
            return "Every section needs at least %s of %s." % (p(1), p(0))
        if kind == "style.forbid" and params:
            return "Never use %s." % params[0]
        if kind == "open.with" and params:
            return "Open every section with %s." % params[0]
        if kind == "density.max" and len(params) == 2:
            return "Use %s at most %s times per section." % (p(0), p(1))
        return ""


def _rationale_texts(q):
    """Every author-written rationale string of an item, as (field, text)
    pairs, for the key.in_rationale scan (D-05: a [!KEY] marker belongs in
    the lesson, never inside an item rationale)."""
    out = []
    for f in ("why", "disc", "second", "trap", "model"):
        v = q.get(f)
        if v:
            out.append((f, v))
    da = q.get("da") or {}
    for letter in sorted(da):
        if da[letter]:
            out.append(("da", da[letter]))
    for f in ("notes", "rubric"):
        for entry in q.get(f) or []:
            if entry:
                out.append((f, entry))
    return out


_KEY_ID_RE = re.compile(r"\[!KEY(?::\s*([^\]]+))?\]")


def _is_multi_sentence(text):
    """The one-sentence check for the `Objective:` line (LESSON-15): after
    collapsing whitespace and stripping one trailing sentence terminator,
    any remaining sentence-ending mark inside the line means more than one
    sentence. A deliberate heuristic -- abbreviations like `e.g.` can
    false-positive, so the finding is a warning, never a block."""
    t = re.sub(r"\s+", " ", text.strip()).rstrip(".!?")
    return bool(re.search(r"[.!?][\s\u2014-]", t))


def lint(questions, lesson=LESSON_UNCHECKED, terms=TERMS_UNCHECKED,
         keys=KEYS_UNCHECKED, style=STYLE_UNCHECKED,
         sources=SOURCES_UNCHECKED, cases=CASES_UNCHECKED,
         paraphrase=PARAPHRASE_UNCHECKED):
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

    `terms` follows the same additive sentinel pattern: TERMS_UNCHECKED skips
    every terms/key check; a caller that supplies TERMS data passes whatever
    `parse_terms()` returned -- a dict (the checks run), or None for a bank
    with no `## TERMS` section (every [[term]] reference is unknown).

    `keys` follows it again for the [!KEY] block checks (plan 03.1-03):
    KEYS_UNCHECKED skips them; a caller that supplies key data passes
    whatever `parse_key_blocks()` returned -- an empty list is a real
    "no key blocks" result, not a skip.

    `style` follows the same additive sentinel pattern (plan 03.1-04): the
    style pass is off unless the caller passes style data -- whatever
    `load_style()` returned. None means a directive named a style that
    resolves to nothing (style.file_unreadable, never a silent house
    fallback, D-09); a dict carrying `error` is an unreadable file; a parsed
    dict runs the parent guard, the closed-kind check, the duplicate-id
    check, and the locked-row guard.

    `sources` follows the same additive sentinel pattern (plan 03.2-02): the
    provenance pass is off unless the caller passes provenance data --
    whatever `parse_sources()` returned. A dict runs the duplicate-registry-id
    check and the resolution checks over every [SRC:]/[OBJ:] directive;
    None means the bank carries no provenance constructs, so no directive can
    be unresolvable (the mirror of the lesson=None rule, where a reference
    into a sectionless bank is unknown rather than skipped).

    `cases` follows it again for the [CASE:]/[PREREQ:] pass (plan 03.2-04):
    the case/prereq checks are off unless the caller passes whatever
    `parse_cases()` returned -- a dict runs the unknown-case, unknown-prereq,
    and cycle checks (D-15/D-16); None means the bank carries no case/prereq
    constructs. When case data is present, a [PREREQ:] naming a case or item
    id is valid and stops the legacy objective-only warning.

    `paraphrase` follows it once more for the winnowing paraphrase pass
    (plan 03.2-04, D-13): the checks are off unless the caller passes a
    thresholds dict (the `paraphrase` settings group, defaults 8 and 0.25).
    When on, every item's text is compared against the sources its [SRC:]s
    resolve to -- fingerprints only, source text read transiently and never
    stored.
    """
    errors, warnings = [], []
    seen_stems = {}
    seen_ids = {}
    seen_item_ids = {}
    letter_hits = collections.Counter()
    all_objectives = {q.get("objective", "") for q in questions
                      if q.get("objective")}
    pair_counts = {}
    lesson_on = lesson is not LESSON_UNCHECKED
    terms_on = terms is not TERMS_UNCHECKED
    keys_on = keys is not KEYS_UNCHECKED
    style_on = style is not STYLE_UNCHECKED
    sources_on = sources is not SOURCES_UNCHECKED
    cases_on = cases is not CASES_UNCHECKED
    paraphrase_on = paraphrase is not PARAPHRASE_UNCHECKED
    if lesson_on:
        known_slugs = set()
        if lesson:
            known_slugs = {h["slug"] for h in lesson["headings"]}
    if terms_on:
        known_terms = terms["terms"] if terms else {}
        if terms:
            term_refs = terms.get("refs", [])
        elif isinstance(lesson, dict):
            term_refs = _term_refs(lesson.get("body", ""))
        else:
            term_refs = []
        lesson_body = lesson.get("body", "") if isinstance(lesson, dict) else ""
    if keys_on:
        seen_key_ids = {}
    if cases_on:
        known_case_ids = set((cases or {}).get("cases") or {})
        known_item_id_set = {q.get("item_id") for q in questions
                             if q.get("item_id")}

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
        objective_line = q.get("objective_line") or ""
        if objective_line and _is_multi_sentence(objective_line):
            warnings.append(LintError(
                "item.objective_line_multi_sentence", "objective_line", tag,
                "Objective: must be a single sentence, got more than one"))
        if q.get("pair"):
            pair_counts.setdefault(q["pair"], []).append(tag)
        for prereq in q.get("prereq") or []:
            # A [PREREQ:] target may be an objective (the legacy contract), a
            # case id, or an item [ID:] (plan 03.2-04, D-16). With case data
            # present the legacy objective-only warning is suppressed for
            # case/item targets; a truly unresolvable target is both warned
            # here and errored as prov.prereq_unknown below.
            if prereq not in all_objectives and not (
                    cases_on and (prereq in known_case_ids
                                  or prereq in known_item_id_set)):
                warnings.append(LintError(
                    "item.prereq_unknown", "prereq", tag,
                    "prereq %r is not an objective any item in this bank "
                    "teaches; check the spelling or add the teaching item"
                    % prereq))

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

        if terms_on:
            for rfield, rtext in _rationale_texts(q):
                if "[!KEY" in rtext:
                    errors.append(LintError(
                        "key.in_rationale", rfield, tag,
                        "a [!KEY] marker belongs in the lesson, never inside "
                        "an item rationale (D-05)"))

        # Plan 03.2-04: style.unsourced_specific (D-14) is a structural check
        # inside the provenance pass -- an item with no resolved [SRC:]
        # carrying a numeral/unit/dose is an error. The winnowing paraphrase
        # pass (D-13) compares the item's text against the sources it cites,
        # fingerprints only; the source text is read transiently and never
        # stored or echoed.
        if sources_on and sources:
            for e in unsourced_specific_findings(q, sources, tag):
                errors.append(e)
        if paraphrase_on and sources:
            for code, msg in paraphrase_findings(
                    _item_text(q), sources, paraphrase, item_tag=tag,
                    subject="the item"):
                if code == "prov.paraphrase_copy":
                    errors.append(LintError(code, "src", tag, msg))
                else:
                    warnings.append(LintError(code, "src", tag, msg))

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

        elif t == "visual":
            for finding in _visual_lint_findings(q, tag):
                errors.append(finding)

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

    for pair_name, tags in sorted(pair_counts.items()):
        if len(tags) == 1:
            warnings.append(LintError(
                "item.pair_singleton", "pair", tags[0],
                "pair %r appears on exactly one item (%s); a pair of one is "
                "an authoring mistake, not a valid state"
                % (pair_name, tags[0])))

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
            # Phase 6.2 gate findings (D-02, D-01): the [GATE:] value is
            # validated against the closed set, and every [!CHECK: <id>]
            # must resolve to an item in this same bank -- a cross-bank or
            # unresolvable reference is a named lint error whose copy is the
            # shared CHECK_UNRESOLVED_COPY constant, never a duplicate
            # literal (06.2-UI-SPEC section 13 gate 12).
            gate = lesson.get("gate") or "recommended"
            if gate not in GATE_VALUES:
                errors.append(LintError(
                    "lesson.invalid_gate", "gate", "BANK",
                    "[GATE: %s] is not one of %s -- use required, "
                    "recommended, or off" % (gate, "/".join(GATE_VALUES))))
            known_check_ids = {q.get("id") for q in questions}
            known_check_ids.update(
                q.get("item_id") for q in questions if q.get("item_id"))
            for cm in re.finditer(r"\[!CHECK:\s*([^\s\]]+)\s*\]",
                                  lesson.get("body", "")):
                cid = cm.group(1)
                if cid and cid not in known_check_ids:
                    errors.append(LintError(
                        "lesson.check_ref_unknown", "refs", "BANK",
                        "[!CHECK: %s] %s" % (cid, CHECK_UNRESOLVED_COPY)))

    # Bank-level terms/key findings, in a deterministic order: collisions,
    # then the empty-block warning, then unknown refs, then duplicate [!KEY]
    # ids. `terms` None means no `## TERMS` section: every ref is unknown
    # (mirroring the lesson=None rule), so the checks still run.
    if terms_on:
        if terms and terms.get("collisions"):
            for c in terms["collisions"]:
                first = terms["terms"][c["slug"]]["canonical"]
                for text in c["texts"]:
                    errors.append(LintError(
                        "terms.duplicate_slug", "terms", "BANK",
                        "term '%s' collides with '%s' after slugifying to "
                        "'%s' -- rename one" % (text, first, c["slug"])))
        if terms and terms.get("empty"):
            warnings.append(LintError(
                "terms.empty_block", "terms", "BANK",
                "## TERMS block has no entries; it renders nothing"))
        for ref in term_refs:
            if ref["slug"] not in known_terms:
                errors.append(LintError(
                    "terms.unknown_ref", "refs", "BANK",
                    "[[%s]] has no entry in ## TERMS" % ref["text"]))
        key_ids = {}
        for km in _KEY_ID_RE.finditer(lesson_body):
            kid = km.group(1)
            if not kid:
                continue
            if kid in key_ids:
                errors.append(LintError(
                    "key.duplicate_id", "key", "BANK",
                    "duplicate [!KEY] id '%s' in the lesson -- rename one"
                    % kid))
            key_ids.setdefault(kid, True)

    # Bank-level [!KEY] block findings (plan 03.1-03 Task 1), in document
    # order: a body with neither title nor cloze has no Anki front; an
    # unminted block warns for its missing id and hash; two blocks sharing
    # an [ID:] are a duplicate-id error.
    if keys_on:
        for key in keys or []:
            if not key.get("title") and not key.get("cloze"):
                errors.append(LintError(
                    "key.no_front", "body", "BANK",
                    "a [!KEY] block needs a title or a {{cloze}} marker to "
                    "have an Anki front (key.no_front)"))
            kid = key.get("id") or ""
            if not kid:
                warnings.append(LintError(
                    "key.missing_id", "id", "BANK",
                    "a [!KEY] block has no [ID:] line; run `itembank "
                    "id-assign` before this key can round-trip"))
            else:
                if kid in seen_key_ids:
                    errors.append(LintError(
                        "key.duplicate_id", "id", "BANK",
                        "two [!KEY] blocks share the [ID:] %s -- rename one"
                        % kid))
                seen_key_ids.setdefault(kid, True)
                if not key.get("hash"):
                    warnings.append(LintError(
                        "key.missing_hash", "hash", "BANK",
                        "a [!KEY] block carries [ID:] but no [HASH:]; run "
                        "`itembank id-assign` to record its fingerprint"))

    # Style-registry findings (plan 03.1-04 Task 1), in deterministic order:
    # unreadable file, parent guard, across-level duplicate warning,
    # within-file duplicate rules, then per-row kind/lock/override checks.
    if style_on:
        if style is None:
            errors.append(LintError(
                "style.file_unreadable", "style", "BANK",
                "no style file resolves for the requested style id -- run "
                "`itembank lint` on the bank for details"))
        elif style.get("error"):
            errors.append(LintError(
                "style.file_unreadable", "style", "BANK",
                "style file %s could not be read (%s)"
                % (style.get("path") or "?", style.get("detail") or "")))
        else:
            parent = style.get("parent") or ""
            if parent and parent != "house":
                errors.append(LintError(
                    "style.parent_unknown", "parent", "BANK",
                    "[STYLE-PARENT: %s] names a non-house style; inheritance "
                    "is exactly one level (house -> style, D-10)"
                    % parent))
            for w in style.get("warnings") or []:
                warnings.append(LintError(
                    "style.duplicate_id", "style", "BANK", w))
            for rid in style.get("duplicate_rules") or []:
                errors.append(LintError(
                    "style.duplicate_id", "rules", "BANK",
                    "duplicate rule id '%s' in style %s -- rename one"
                    % (rid, style.get("id") or "?")))
            for row in style.get("rules") or []:
                rid = row.get("id") or ""
                if row.get("kind") not in STYLE_RULE_KINDS:
                    errors.append(LintError(
                        "style.rule_unimplemented", "rules", "BANK",
                        "rule '%s' claims kind '%s', which the linter does "
                        "not implement (D-16)" % (rid, row.get("kind") or "?")))
                if rid in LOCKED_RULE_IDS:
                    errors.append(LintError(
                        "style.override_locked", "rules", "BANK",
                        "rule '%s' names a locked house id; locked rows are "
                        "code constants and may not be overridden, "
                        "suppressed, or re-severed (T-031-12)" % rid))
                if row.get("lock"):
                    errors.append(LintError(
                        "style.ignore_locked", "rules", "BANK",
                        "rule '%s' carries a lock cell; only model.py's "
                        "LOCKED_RULE_IDS may manage locks" % rid))

        # plan 03.1-05: the style content pass -- three cost classes, closed
        # catalogue, local suppression. Threaded behind the STYLE_UNCHECKED
        # sentinel like every other pass, so a caller that never heard of
        # style enforcement gets byte-for-byte what it got before this
        # parameter existed. The registry findings above stay; this runs the
        # lesson-content checks and the one shared lexical metrics pass, and
        # applies the local `<!-- style-ignore: -->` suppressions (a locked
        # suppression is itself style.ignore_locked and never suppresses).
        if style is not None and not style.get("error"):
            style_errors, style_warnings = run_style_pass(lesson, style)
            lesson_text = lesson.get("body", "") \
                if isinstance(lesson, dict) else ""
            kept_errors, _, locked_errors = apply_style_ignore(
                style_errors, lesson_text)
            kept_warnings, _, _ = apply_style_ignore(
                style_warnings, lesson_text)
            errors.extend(locked_errors)
            errors.extend(kept_errors)
            warnings.extend(kept_warnings)

    # Provenance findings (plan 03.2-02), in deterministic order: duplicate
    # registry ids, then unresolvable [SRC:] ids, then unresolvable [OBJ:]
    # ids, each tagged by the carrying item (D-11, T-032-05). `sources` None
    # means the bank carries no provenance constructs at all, so no directive
    # can be unresolvable -- the mirror of the lesson=None rule's opposite.
    if sources_on and sources:
        path = sources.get("path") or "?"
        seen_dup = {}
        for sid in sources.get("duplicates") or []:
            if sid in seen_dup:
                continue
            seen_dup[sid] = True
            errors.append(LintError(
                "prov.src_duplicate", "sources", "BANK",
                "source id '%s' is registered more than once in ## SOURCES "
                "of %s -- keep one row per source" % (sid, path)))
        known = sources.get("sources") or {}
        for d in sources.get("srcs") or []:
            if d["id"] not in known:
                errors.append(LintError(
                    "prov.src_unknown", "src", d["item"],
                    "[SRC:] names source '%s', which is not in ## SOURCES "
                    "of %s" % (d["id"], path)))
        for d in sources.get("objs") or []:
            if d["obj"] not in known:
                errors.append(LintError(
                    "prov.obj_unknown", "obj", d["item"],
                    "[OBJ:] names objective '%s', which is not in ## SOURCES "
                    "of %s" % (d["obj"], path)))

    # Case/edge findings (plan 03.2-04, D-15/D-16), in deterministic order:
    # unknown [CASE:] ids, unknown [PREREQ:] targets, then the first cycle.
    # `cases` None means the bank carries no case/prereq constructs, so
    # nothing can be unknown or cyclic.
    if cases_on and cases:
        path = cases.get("path") or "?"
        fname = os.path.basename(path) if path else "?"
        known_case_ids = set(cases.get("cases") or {})
        known_item_id_set = {q.get("item_id") for q in questions
                             if q.get("item_id")}
        for d in cases.get("case_directives") or []:
            if d["id"] not in known_case_ids:
                errors.append(LintError(
                    "prov.case_unknown", "case", d["item"],
                    "[CASE:] names case '%s', which is not in ## CASES of %s"
                    % (d["id"], fname)))
        for d in cases.get("prereq_edges") or []:
            t = d["target"]
            if t not in known_case_ids and t not in known_item_id_set \
                    and t not in all_objectives:
                errors.append(LintError(
                    "prov.prereq_unknown", "prereq", d["item"],
                    "[PREREQ:] names target '%s', which is neither a case in "
                    "## CASES, an item [ID:], nor an objective any item "
                    "teaches, in %s" % (t, fname)))
        errors.extend(_prereq_cycle_findings(questions, cases, all_objectives))
    return errors, warnings


def load(path):
    qs = parse_bank(open(path, encoding="utf-8").read())
    if not qs:
        sys.exit("No question blocks found in %s. Run `itembank spec` for the format." % path)
    return qs
