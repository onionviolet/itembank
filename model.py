"""The format contract: what a bank is, and what makes one invalid.

Everything here reads markdown and returns plain dicts. It knows nothing about
scoring, sessions or surfaces, which is what lets `spec` and `lint` be the whole
of what an authoring agent has to satisfy.
"""
import collections, hashlib, json, os, re, sys, uuid

import resources
from markdown_blocks import (split_cells, is_separator_row, CALLOUT_MARK_RE,
                             callout_required_of, callout_spec, callout_entered,
                             protect_fenced_code)


from model_lesson import (
    _MEDIA_REF_RE,
    _META_CELL_RE,
    _OBJ_DIRECTIVE_RE,
    _PREAMBLE_HEADING_RE,
    _SRC_DIRECTIVE_RE,
    _TERM_REF_RE,
    _lesson_direction,
    _lesson_directive_defaults,
    _lesson_example_order,
    _lesson_lang,
    _lesson_pace,
    _lesson_profile,
    _preamble_section,
    _term_refs,
    _terms_row_cells,
    lesson_slug,
    lesson_steps,
    parse_activities,
    parse_lesson,
    parse_lesson_comparison,
    parse_lesson_lineplot,
    parse_media,
    parse_sources,
    parse_terms,
)

from model_provenance import (
    PARAPHRASE_DEFAULTS,
    _PARAPHRASE_K,
    _PARAPHRASE_WINDOW,
    _SPECIFIC_FACT_RE,
    _fingerprint_tokens,
    _gram_hash,
    _item_text,
    _kgram_hashes,
    _read_source_text,
    _winnow_positions,
    _winnow_set,
    paraphrase_check,
    paraphrase_findings,
    unsourced_specific_findings,
)

from model_ids import (
    _assign_key_ids,
    _key_content_hash,
    assign_ids,
)

from model_style import (
    STYLE_CHECK_CATALOGUE,
    STYLE_SEVERITIES,
    STYLE_WARNING_FP_RATES,
    StylePrompt,
    WARNING_FP_THRESHOLD,
    _STYLE_CODE_SPAN_RE,
    _STYLE_FENCE_RE,
    _STYLE_FILLER_RE,
    _STYLE_HECTOR_RE,
    _STYLE_IGNORE_RE,
    _STYLE_REFERENCE_RE,
    _STYLE_SENTENCE_RE,
    _STYLE_WORD_RE,
    _style_count,
    _style_first_line,
    _style_first_pos,
    _style_is_int,
    _style_lesson_body,
    _style_lexical_metrics,
    _style_marker_prefix,
    _style_row_severity,
    _style_sections,
    _style_split_params,
    apply_style_ignore,
    run_style_pass,
    style_manual_rules,
    style_suppression_report,
    warning_ship_state,
    write_allowed,
)


LETTERS = "ABCDEFGH"


# One source of truth for the line markers that end an item's stem and that
# the [ID:]/[HASH:] splice point must not land after. The stem terminator and
# TERMINATOR are both built from this constant (plan 05-01), so a marker added
# for a new item type reaches both regexes together or the shared-source test
# in tests/check_roundtrip.py fails -- the two-regex drift risk RESEARCH.md
# names is structural here rather than a discipline.
MARKERS = (
    "A)", "B)", "C)", "D)", "E)", "F)", "G)", "H)",
    "ROW)", "ITEM)", "STEP)", "CASE)",
    "[TYPE:", "[FORMAT:", "[OBJECTIVE:", "[SELECT:", "[CATEGORIES:", "[ID:", "[HASH:",
    "[LESSON-REF:", "[PAIR:", "[PREREQ:", "[LANG:", "[MATCH:", "[INPUT:",
    "[HARNESS:", "[TOLERANCE:", "[FIELDS:", "[FILL-LAYOUT:", "[MATCHING:", "[ORDERING:",
    "MODEL:", "RUBRIC:", "WHY BEST:", "STARTER:",
)


def _marker_alt(prefix, markers):
    """One alternation fragment for the marker vocabulary, each marker
    escaped so the literal text (brackets, colons, parens) survives the trip
    through a regex."""
    return "|".join(prefix + re.escape(m) for m in markers)


_STEM_TERMINATORS = _marker_alt(chr(92) + "n", MARKERS)
# The same vocabulary without the newline prefix, for regexes that already
# anchor their own line start: the [ID:]/[HASH:] splice point matches the
# first structural marker line of a block, so it must not demand a newline
# before that marker (assign_ids' TERMINATOR).
_TERMINATORS = _marker_alt("", MARKERS)


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


def _unique_field_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate field member")
        result[key] = value
    return result


class BankQuestions(list):
    """Ordinary question list with optional authored bank declarations."""

    def __init__(self):
        super().__init__()
        self.staged_cases = []
        self.staged_case_errors = []


def staged_case_spec_errors(questions):
    """Validate fixed cases without interpreting PAIR or assigning scores."""
    errors = list(getattr(questions, "staged_case_errors", []))
    declarations = getattr(questions, "staged_cases", [])
    if not isinstance(declarations, list) or len(declarations) > 64:
        return errors + ["STAGED-CASES must be an array of at most 64 cases"]
    by_id = collections.defaultdict(list)
    for q in questions:
        if q.get("item_id"):
            by_id[q["item_id"]].append(q)
    activities, used = set(), set()
    for case in declarations:
        if not isinstance(case, dict) or set(case) != {
                "version", "activity_id", "stimulus", "children", "order"}:
            errors.append("each staged case requires version, activity_id, stimulus, children and order")
            continue
        ident = case["activity_id"]
        if (not isinstance(ident, str) or not re.fullmatch(r"[a-z][a-z0-9_:-]{0,63}", ident)
                or ident in activities):
            errors.append("staged activity IDs must be unique bounded lowercase ASCII names")
        if isinstance(ident, str):
            activities.add(ident)
        if type(case["version"]) is not int or case["version"] != 1:
            errors.append("staged case version must be 1")
        stimulus = case["stimulus"]
        if (not isinstance(stimulus, str) or not stimulus.strip() or len(stimulus) > 4000
                or any(ord(c) < 32 and c not in "\n\t" for c in stimulus)):
            errors.append("staged stimulus needs nonempty plain text of at most 4000 characters")
        if case["order"] != ["answer", "reason"]:
            errors.append("staged case order must be answer then reason")
        children = case["children"]
        if (not isinstance(children, list) or len(children) != 2
                or any(not isinstance(c, str) or not c for c in children)
                or len(set(children)) != 2):
            errors.append("staged cases require two distinct stable child IDs")
            continue
        for child in children:
            matches = by_id[child]
            if len(matches) != 1 or matches[0]["type"] != "mc":
                errors.append("staged child %s must resolve to one existing MC identity" % child)
            if child in used:
                errors.append("staged child %s overlaps another case" % child)
            used.add(child)
    return errors


def parse_bank(text):
    """Split on `Qn.` markers and parse each block into a question dict."""
    questions = BankQuestions()
    header = re.split(r"(?m)^(?=Q\d+\.)", text)[0]
    declarations = re.findall(r"(?m)^STAGED-CASES:\s*(.*?)\s*$", header)
    if len(re.findall(r"(?m)^STAGED-CASES:", text)) != len(declarations):
        questions.staged_case_errors.append("STAGED-CASES must appear before the first question")
    if len(declarations) > 1:
        questions.staged_case_errors.append("STAGED-CASES may appear only once")
    if declarations:
        try:
            questions.staged_cases = json.loads(declarations[0], object_pairs_hook=_unique_field_members)
        except (ValueError, TypeError):
            questions.staged_case_errors.append("STAGED-CASES must contain valid JSON without duplicate members")
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if not re.match(r"Q\d+\.", ch.strip()):
            continue
        q = parse_question(ch)
        if q:
            questions.append(q)
    return questions


def matching_spec_errors(q):
    """Versioned additive dnd contract; legacy category assignments stay intact."""
    if "matching" not in q:
        return []
    spec = q.get("matching")
    if q.get("type") != "dnd" or not isinstance(spec, dict) or set(spec) != {"version", "reuse", "choices"}:
        return ["MATCHING requires a dnd object with version, reuse and choices"]
    if type(spec["version"]) is not int or spec["version"] != 1 or spec["reuse"] not in ("once", "unlimited"):
        return ["MATCHING version must be 1 and reuse must be once or unlimited"]
    choices = spec["choices"]
    valid_id = lambda value: isinstance(value, str) and bool(re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", value))
    if not isinstance(choices, list) or not 2 <= len(choices) <= 64 or any(
            not isinstance(c, dict) or set(c) != {"id", "text"}
            or not valid_id(c["id"]) or not isinstance(c["text"], str)
            or not c["text"].strip() or len(c["text"]) > 1000 for c in choices):
        return ["MATCHING needs 2 to 64 choices with stable id and nonempty text"]
    ids = [c["id"] for c in choices]
    rows = q.get("rows") or []
    row_ids = [r.get("id") for r in rows]
    if len(set(ids)) != len(ids) or not 2 <= len(rows) <= 64 or any(
            not valid_id(r.get("id")) or not r.get("text") or r["cat"] not in ids for r in rows) \
            or len(set(row_ids)) != len(row_ids):
        return ["MATCHING requires unique choice/row IDs and a known key for every row"]
    if spec["reuse"] == "once" and len(set(r["cat"] for r in rows)) != len(rows):
        return ["MATCHING once forbids reused keyed choices"]
    return []


def ordering_spec_errors(q):
    """Validate structural ordering declarations without assigning a verdict."""
    if "ordering" not in q:
        return []
    spec = q.get("ordering")
    if q.get("type") != "build" or not isinstance(spec, dict) or set(spec) != {
            "version", "blocks", "required", "dependencies"}:
        return ["ORDERING requires version, blocks, required and dependencies"]
    if type(spec["version"]) is not int or spec["version"] != 1:
        return ["ORDERING version must be 1"]
    valid_id = lambda value: isinstance(value, str) and bool(re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", value))
    ids, required, edges = spec["blocks"], spec["required"], spec["dependencies"]
    if not isinstance(ids, list) or not 2 <= len(ids) <= 64 or any(not valid_id(i) for i in ids) or len(set(ids)) != len(ids):
        return ["ORDERING needs 2 to 64 unique stable block IDs"]
    blocks = q.get("blocks") or []
    if len(blocks) != len(ids) or [b["id"] for b in blocks] != ids or any(
            not b["text"].strip() or len(b["text"]) > 1000 for b in blocks):
        return ["STEP definitions must match ORDERING blocks in order with nonempty text"]
    if not isinstance(required, list) or not required or any(not valid_id(i) or i not in ids for i in required) or len(set(required)) != len(required):
        return ["ORDERING required must contain unique known block IDs"]
    if not isinstance(edges, list) or len(edges) > 256 or any(
            not isinstance(e, list) or len(e) != 2 or any(not isinstance(i, str) or i not in required for i in e) or e[0] == e[1] for e in edges):
        return ["ORDERING dependencies need at most 256 before/after edges between distinct required blocks"]
    if len(set(tuple(e) for e in edges)) != len(edges):
        return ["ORDERING dependencies cannot repeat an edge"]
    pending = set(required)
    while pending:
        ready = {i for i in pending if not any(after == i and before in pending for before, after in edges)}
        if not ready:
            return ["ORDERING dependencies contain a cycle"]
        pending -= ready
    return []


def parse_question(ch):
    number = grab(r"Q(\d+)\.", ch)
    qtype = (grab(r"(?m)^\[TYPE:\s*(\w+)\s*\]", ch) or "mc").lower()
    # Stem runs from the Qn. marker to the first structural marker that follows.
    # The stem runs to the first structural marker: a fixed inline
    # difficulty tag, or any marker in the shared MARKERS vocabulary at the
    # start of a line. Built from MARKERS (plan 05-01) so a marker added for
    # a new item type reaches this regex and TERMINATOR together.
    stem = grab(
        r"Q\d+\.\s*(.*?)\s*(?:\(difficulty:|" + _STEM_TERMINATORS + r")",
        ch, re.S)
    lesson_ref = grab(r"\[LESSON-REF:\s*(.*?)\]", ch)
    input_format = grab(r"(?m)^\[INPUT:\s*([\w-]+)\s*\]", ch).lower()
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
    if input_format:
        common["input_format"] = input_format

    if qtype in ("mc", "multi"):
        answer_format = grab(r"(?m)^\[FORMAT:\s*([\w-]+)\s*\]", ch).lower()
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
        if answer_format:
            common["answer_format"] = answer_format
        return common

    if qtype in ("table", "dnd"):
        matching_raw = grab(r"(?m)^\[MATCHING:\s*(.*?)\s*\]\s*$", ch)
        matching_declared = bool(re.search(r"(?m)^\[MATCHING:", ch))
        if matching_declared:
            try:
                matching = json.loads(matching_raw, object_pairs_hook=_unique_field_members)
            except ValueError:
                matching = None
            common["matching"] = matching
        cats = [c.strip() for c in grab(r"(?m)^\[CATEGORIES:\s*(.*?)\s*\]", ch).split("|") if c.strip()]
        if isinstance(common.get("matching"), dict):
            choices = common["matching"].get("choices")
            cats = [c.get("id") if isinstance(c.get("id"), str) else "" for c in choices if isinstance(c, dict)] if isinstance(choices, list) else []
        marker = "ROW" if qtype == "table" else "ITEM"
        rows = []
        for line in re.findall(rf"(?m)^{marker}\)\s*(.+?)\s*$", ch):
            if "::" not in line:
                continue
            t, c = line.rsplit("::", 1)
            row = {"text": t.strip(), "cat": c.strip()}
            if matching_declared:
                ident, separator, label = t.partition("|")
                row.update(id=ident.strip(), text=label.strip() if separator else "")
            rows.append(row)
        if not (stem and rows and (cats or matching_declared)):
            return None
        common.update({"cats": cats, "rows": rows, "notes": notes(ch)})
        return common

    if qtype == "build":
        steps = [s.strip() for s in re.findall(r"(?m)^STEP\)\s*(.+?)\s*$", ch)]
        if re.search(r"(?m)^\[ORDERING:", ch):
            raw = grab(r"(?m)^\[ORDERING:\s*(.*?)\s*\]\s*$", ch)
            try:
                common["ordering"] = json.loads(raw, object_pairs_hook=_unique_field_members)
            except (ValueError, TypeError, RecursionError):
                common["ordering"] = None
            common["blocks"] = []
            for step in steps:
                ident, separator, label = step.partition("|")
                common["blocks"].append({"id": ident.strip(), "text": label.strip() if separator else ""})
            common.update(steps=[b["text"] for b in common["blocks"]], notes=notes(ch))
            return common if stem else None
        if not (stem and len(steps) > 1):
            return None
        common.update({"steps": steps, "notes": notes(ch)})
        return common

    if qtype == "check":
        # The machine-runnable item type (plan 05-01). The stem, the CASE)
        # set and the starter are content; [LANG:] and [MATCH:] are
        # configuration (D-05), so content_fingerprint() hashes the first
        # three and never the latter two. One case per CASE) line, split on
        # the last "::" exactly as the table/dnd rows already are (D-03).
        lang = (grab(r"(?m)^\[LANG:\s*(\w+)\s*\]", ch) or "python").lower()
        match_mode = (grab(r"(?m)^\[MATCH:\s*(\w+)\s*\]", ch) or "trimmed").lower()
        harness = grab(r"(?m)^\[HARNESS:\s*(\w+)\s*\]", ch)
        tol = grab(r"(?m)^\[TOLERANCE:\s*([0-9]*\.?[0-9]+)\s*\]", ch)
        starter = section("STARTER", ch)
        cases = []
        for line in re.findall(r"(?m)^CASE\)\s*(.+?)\s*$", ch):
            if "::" not in line:
                continue
            lhs, expected = line.rsplit("::", 1)
            case = {"stdin": lhs.strip(), "expected": expected.strip()}
            if harness:
                case["call"] = lhs.strip()
            cases.append(case)
        if not (stem and cases):
            return None
        common.update({
            "lang": lang, "match": match_mode, "cases": cases,
            "harness": harness or "",
            "tolerance": float(tol) if tol else None,
            "starter": starter, "notes": notes(ch)})
        return common

    if qtype == "fill":
        raw = grab(r"(?m)^\[FIELDS:\s*(.+?)\s*\]\s*$", ch)
        try:
            fields = (json.loads(raw, object_pairs_hook=_unique_field_members)
                      if len(raw) <= 65536 else None)
        except (ValueError, TypeError, RecursionError):
            fields = None
        common.update({"fields_raw": raw, "fields": fields, "notes": notes(ch)})
        if re.search(r"(?m)^\[FILL-LAYOUT:", ch):
            common["fill_layout"] = grab(r"(?m)^\[FILL-LAYOUT:\s*(.*?)\s*\]\s*$", ch)
            common["fill_layout_count"] = len(re.findall(r"(?m)^\[FILL-LAYOUT:", ch))
        return common if stem else None

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


def coverage_map(bank_path):
    """The objective coverage map, computed on demand and never stored (D-12,
    plan 03.2-02): objective -> sorted item tags, built from every item's
    [OBJECTIVE:] value plus its resolved [OBJ:] values (those registered in
    the bank's ## SOURCES). A bank with no items or no objectives maps to {}.
    """
    with open(bank_path, encoding="utf-8") as source_handle:
        text = source_handle.read()
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


_CASE_DIRECTIVE_RE = re.compile(r"\[CASE:\s*([^\]]+?)\]")
_PREREQ_DIRECTIVE_RE = re.compile(r"\[PREREQ:\s*([^\]]+?)\]")
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
    with open(bank_path, encoding="utf-8") as source_handle:
        text = source_handle.read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and parse_question(ch) is not None:
            break
        preamble.append(ch)
    head = "".join(preamble)

    cases = {}
    block = _preamble_section(head, "CASES")
    if block is not None:
        for line in block.splitlines():
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
    with open(bank_path, encoding="utf-8") as source_handle:
        text = source_handle.read()
    preamble = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and parse_question(ch) is not None:
            break
        preamble.append(ch)
    return "".join(preamble)


def _parse_style_file(style_id, path, text, warnings):
    """Parse one style file's `## Voice` prose zone, `## Rules` pipe table
    and `## Exemplar` block into a plain dict. The pipe table reuses the
    shared Markdown cell splitter. A duplicate rule id inside
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

    rules = []
    duplicate_rules = []
    seen = set()
    past_separator = False
    for row in rules_text.splitlines():
        if not row.strip().startswith("|"):
            continue
        if is_separator_row(row):
            past_separator = True
            continue
        if not past_separator:
            continue  # the header row precedes the separator
        cells = split_cells(row)
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
            with open(chosen, encoding="utf-8") as source_handle:
                text = source_handle.read()
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

    A `check` item hashes the stem, the ordered CASE) set and the starter --
    the tested content -- and never `lang` or `match`, which are
    configuration (D-05): switching the interpreter or the grading strictness
    is a config change, not a change to what the item asks, and must not
    orphan the item's history.

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
        if q.get("answer_format"):
            parts.append("format=" + q["answer_format"])
    elif t in ("table", "dnd"):
        if "matching" in q:
            parts.append("matching=" + json.dumps(q["matching"], sort_keys=True, separators=(",", ":")))
            parts.append("row_ids=" + json.dumps([r.get("id") for r in q["rows"]]))
        parts.append("cats=" + "|".join(q["cats"]))
        for i, r in enumerate(q["rows"]):
            parts.append("row:%d=%s::%s" % (i, collapse(r["text"]), r["cat"]))
    elif t == "build":
        if "ordering" in q:
            parts.append("ordering=" + json.dumps(q["ordering"], sort_keys=True, separators=(",", ":")))
            parts.append("block_ids=" + json.dumps([b["id"] for b in q["blocks"]]))
        for i, s in enumerate(q["steps"]):
            parts.append("step:%d=%s" % (i, collapse(s)))
    elif t == "fill":
        parts.append("fields=" + json.dumps(q.get("fields"), sort_keys=True,
                                             separators=(",", ":")))
    elif t == "short":
        parts.append("model=" + collapse(q["model"]))
        for i, r in enumerate(q["rubric"]):
            parts.append("rubric:%d=%s" % (i, collapse(r)))
    elif t == "check":
        for i, c in enumerate(q["cases"]):
            parts.append("case:%d=%s::%s" % (i, collapse(c["stdin"]),
                                             collapse(c["expected"])))
        parts.append("starter=" + collapse(q.get("starter", "")))
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


# The identity-splice point: the first structural marker line of a block,
# where [ID:]/[HASH:] land when  mints them. Built from
# the same MARKERS constant as the stem terminator (plan 05-01) so a new
# item type's markers cannot reach one regex and not the other.
TERMINATOR = re.compile(r"(?m)^(?:" + _TERMINATORS + ")")


HONEST_LIMITS_NOTE = ("Your code runs directly on this machine under a time "
                      "limit and an output cap; this stops accidents like an "
                      "infinite loop, not a deliberate attempt to escape it.")


def _check_section():
    """The SPEC check section, built as one string so HONEST_LIMITS_NOTE
    is interpolated from the single constant rather than retyped (D-10:
    the sentence exists in exactly two places, both from this one source).
    """
    text = [
        "",
        "8. Check.  The learner writes code; the machine runs it once per",
        "   authored case and scores the pass vector through the same scorer as",
        "   every other type.",
        "     [TYPE: check]",
        "     [LANG: python]            optional; defaults to python",
        "     [MATCH: trimmed]          optional; exact | trimmed | regex",
        "     CASE) 5 7 :: 12",
        "     CASE) 10 2 :: 8",
        "     STARTER: ...              optional pre-filled source",
        "     [HARNESS: add]            optional; each CASE) is a call :: return value",
        "     [TOLERANCE: 0.01]         optional; float comparison inside [HARNESS:]",
        "   A CASE) line is <stdin> :: <expected stdout>, or <call> :: <return value>",
        "   in [HARNESS:] mode, split on the LAST :: -- a case whose expected text",
        "   ends with :: something loses that tail at the last occurrence; author",
        "   accordingly. The stem, the CASE) set and the starter are the tested",
        "   content (fingerprinted); [LANG:] and [MATCH:] are configuration (not).",
        "   [HARNESS:] imports the learner's source as a module and calls the named",
        "   function with each case's arguments, comparing the return value -- exact",
        "   for integers and strings, within [TOLERANCE:] for floats. A harness item",
        "   whose expected values include a float but states no [TOLERANCE:] is a",
        "   lint error (item.tolerance_unstated). This type runs the learner's own",
        "   code with no model anywhere in its path, so a course's ban on",
        "   model-assisted work is not engaged by using it.",
    ]
    return "\n".join(text) + "\n   " + HONEST_LIMITS_NOTE + "\n"

SPEC = (r"""itembank format contract
=========================

A bank is a markdown file with question blocks and optional declared metadata.
Prose around the blocks remains readable; STAGED-CASES explicitly binds a
fixed answer/reason activity and is validated rather than treated as prose.

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

  A stem may continue across lines until the first structural marker. Use one
  deliberate line per premise, conclusion, derivation step, event, speaker
  turn, procedure step, or other independently scanned unit. Quiz renderers
  preserve those line breaks. They may progressively enhance an explicitly
  signaled structure, but the exact authored text remains the readable fallback
  and unlabeled prose is never assigned semantic roles by presentation code.

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

THE NINE ITEM TYPES

1. Multiple choice.  Default. No TYPE line needed.
     A) ...  B) ...  C) ...  D) ...
     CORRECT: B
   Explicit true/false uses [FORMAT: true-false] with exactly A) True and
   B) False, in either order, and one correct answer. Ordinary MC still
   requires at least three options. Subject structure rules still apply.

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

   Versioned structural ordering preserves stable IDs and permits every order
   satisfying the authored dependencies. Legacy build items keep exact-text
   scoring. Declare each block once, in the declaration's blocks order:
     [ORDERING: {"version":1,"blocks":["a","b","c","spare"],"required":["a","b","c"],"dependencies":[["a","c"],["b","c"]]}]
     STEP) a | First independent prerequisite
     STEP) b | Second independent prerequisite
     STEP) c | Use both prerequisites
     STEP) spare | Unneeded task
   IDs are unique lowercase identifiers with at most 64 characters. Declare
   2 to 64 blocks and at most 256 unique dependency edges between required
   blocks. Required IDs must be nonempty, unique and known. Cycles and
   self-edges are lint errors. Block text may repeat; identity uses IDs.
   Submit an array of selected IDs. Duplicate or foreign IDs refuse without
   recording an attempt. Missing required blocks, selected distractors and
   violated dependencies are incorrect; no partial credit is assigned.
   Required IDs and dependencies are private key material. Practice permits
   runtime diagnostic categories; exam and diagnostic submissions withhold
   them. Static HTML is a preview requiring a served runtime for scoring.
   Raw response evidence retains selected IDs and checker_version 1.
   Indentation and execution of assembled code are not part of version 1.

5. Drag-and-drop.  Sort items into buckets. Same shape as table, but display
   order is shuffled, because a table implies fixed rows and a sort does not.
     [TYPE: dnd]
     [CATEGORIES: Direct care | Readiness]
     ITEM) Assessing the airway :: Direct care

   Explicit matching is additive and versioned; old dnd categories remain
   reusable. Omit CATEGORIES when MATCHING declares choices:
     [MATCHING: {"version":1,"reuse":"once","choices":[{"id":"a","text":"Token"},{"id":"b","text":"Token"},{"id":"unused","text":"Spare"}]}]
     ITEM) left | Choose token a. :: a
     ITEM) right | Choose token b. :: b
   Row and choice IDs are unique lowercase identifiers, at most 64 characters.
   Labels may repeat; identity never comes from display text. The UI displays
   IDs beside labels to distinguish duplicates. All rows require a choice;
   unused choices are distractors. reuse is once or unlimited. Version 1
   bounds rows and choices to 2..64 and rejects forbidden key reuse. Invalid
   response construction is refused without evidence or keyed feedback.
   item.invalid_matching identifies declaration errors. Native dropdowns,
   rich controls and drag enhancement submit the same ID mapping.

6. Short answer.  Constructed response, typed in prose. NOT auto-graded, ever:
   the answer is recorded and a human or an AI marks it against RUBRIC later.
   Use it where selecting from options would give the answer away, or where the
   skill being tested is producing the explanation rather than recognising it.
     [TYPE: short]
     [INPUT: latex]                  optional; plain | latex
     MODEL:  the answer a full-credit response contains, compressed
     RUBRIC:
     - one checkable claim the answer must make
     - a second one; two is the minimum, because a single point is a vibe
   No WHY BEST is required on a short item; MODEL replaces it. TRAP still helps
   the marker, because it names the wrong answer that will look confident.
   `[INPUT: latex]` changes the answer control, not the scoring rule. A math
   course may show a local rendered preview while preserving the exact source
   the learner typed. If rendering is unavailable, the source remains usable.
   LaTeX input stays pending until a marker reviews it; the browser never
   decides whether two expressions are equivalent.
"""
    + _check_section()
    + r"""

8. Visual assessment.  Interactive plot or number-line item (protocol integer 1,
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

9. Typed completion. One or several text, number, or measurement fields.
     [TYPE: fill]
     [FIELDS: [{"id":"term","label":"Term","kind":"text","accepted":["blue","azure"],"case_sensitive":false,"whitespace":"trim"},{"id":"length","label":"Length","kind":"numeric","answer":"1","unit":"m","units":{"m":"1","cm":"0.01"},"atol":"0","rtol":"0"}]]
   FIELDS is one JSON line with 1 to 16 objects and no duplicate members.
   Polynomial fields use kind: polynomial, private checker and checker_tests.
   Checker keys are domain: rational-polynomial, checker_version:
   a5-rational-polynomial-v2, variable: x, required_form: expanded, target,
   and diagnostics (at most two unique {id,answer} rules). All comparisons
   use exact rational coefficients. Use explicit multiplication and powers
   0 to 4; expanded form requires distribution, not collecting like terms.
   Bounded grammar (ASCII numbers and x, spaces or tabs between tokens):
     expression := term (("+" | "-") term)*
     term := unary ("*" unary)*
     unary := ("+" | "-") unary | power
     power := primary ["^" exponent]
     primary := number | "x" | "(" expression ")"
     number := integer | integer "." integer | "." integer
               | integer "/" integer
     integer := one or more ASCII digits
     exponent := exactly one ASCII digit from 0 through 4
   Unary minus binds outside a power: -x^2 means -(x^2). Decimals and
   rational literals remain exact. Implicit multiplication, functions,
   Unicode algebra, scientific notation, **, chained powers and division
   of expressions are unsupported. A zero literal denominator is invalid.
   Each private test row has input, state, diagnostic_id (null when absent),
   and checker_version. Cover the teacher, every diagnostic, wrong form,
   invalid and unsupported entry. Tests must replay exactly before acceptance.
   Fixed bounds: 160 characters, 96 tokens, 64 nodes, nesting 16, literal
   digits 12, intermediate degree 4, coefficient numerator/denominator
   1000000, and 64 coefficient operations. Refusals record no attempt.
   Polynomial responses stay raw strings; checker targets, diagnostics and
   private tests never enter a public item or an active formal report.
   Each id is a unique lowercase letter followed by up to 31 lowercase
   letters, digits, or underscores. Each label is 1 to 200 characters.
   Response: {"term":"Blue","length":"100 cm"}. All fields must be correct.
   Optional [FILL-LAYOUT: inline] puts existing fields into {{field_id}}
   positions in the stem. Each declared field must occur exactly once;
   unknown, repeated, missing or malformed markers are invalid. With no
   declaration, legacy stems and separate labelled fields stay unchanged.
   [FILL-LAYOUT: fields] explicitly uses the legacy layout. Layout never
   changes the response, scoring, feedback policy or evidence format.
   Text accepts 1 to 32 explicit strings. NFC normalization preserves accents
   and punctuation. case_sensitive defaults to true. whitespace defaults to
   trim and may be exact, trim, or collapse. No synonyms are guessed.
   Numeric answer, atol, rtol, and unit scales are strings, never JSON floats.
   Decimal, signed integer fractions, and scientific notation parse exactly.
   Numeric tokens have at most 128 characters and exponents from -100 to 100.
   Accept when abs(response-answer) <= max(atol, rtol*abs(answer)), inclusive.
   Tolerances default to zero and cannot be negative. NaN, infinity, arbitrary
   expressions, locale commas, and zero denominators are refused.
   Optional units maps 1 to 16 exact names to positive conversion scales.
   The named base unit must have scale 1. Names have 1 to 24 visible characters
   without spaces. A response must separate its number and unit with a space.
   No prefixes, dimensions, affine conversions, or aliases are inferred.
   Labels, accepted text, and responses are single-line strings without control
   characters or Unicode line separators. Every response value is nonempty and
   at most 4096 characters.
   Missing, extra, malformed, or blank fields are refused before an attempt.
   The submitted strings stay in evidence. Every checking rule affects HASH.
   Private accepted answers and numeric rules never enter the public item.
   Automatic glossary definitions are withheld during numeric fill questions:
   equivalent quantities and tolerance intervals cannot be checked safely by
   matching a finite list of answer strings in free prose.
   The served runtime and CLI grade fill. Static build explains that a running
   session is needed and includes no fill key. Anki/GIFT conversion is refused
   until it can preserve these rules. Prose and proofs still use short.

STAGED ANSWER/REASON CASES
  Optional bank metadata, one JSON line before the first Qn. block:
    STAGED-CASES: [{"version":1,"activity_id":"counter-case","stimulus":"A fictional counter starts at 3. Add 2 once.","children":["a200000000000001","a200000000000002"],"order":["answer","reason"]}]
  Declare at most 64 cases. Activity IDs are unique lowercase ASCII names
  beginning with a letter, then letters, digits, underscore, colon or hyphen,
  at most 64 characters. Stimulus is nonempty plain text, at most 4000
  characters. Children are two distinct stable IDs of existing MC items;
  children cannot overlap cases. Version is 1; order is answer then reason.
  PAIR never implies a case. Selection retains the complete ordered unit or
  refuses a split. Each child commits once regardless of correctness, with
  no retry or hint inside the unfinished case. The committed answer is
  visible at reason; practice outcomes wait for both commitments. Exam and
  diagnostic outcomes wait for the whole sitting to close. Children keep
  distinct objectives and attempts, with activity/revision linkage and no
  composite score. Session schema v4 binds exact bank/declaration revisions;
  older ordinary sittings upgrade without inferred cases. Changed or missing
  case binding freezes mutation. The JSON submit action carries the public
  activity_id, child_id and submission_token. Author header proposals use
  the existing local review, fingerprint check, journal acceptance and undo.

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
  Optional deterministic comparison inside an Example callout:
    > [!EXAMPLE]
    > [COMPARE: 12,18,24,mm]
    > Authored synthesis: **equal intervals** let us compare depths.
    > At B=6, B-A=-6 mm. At B=12, equal. At B=18, B-A=6 mm.
  The first body line declares A,B,maximum,unit. Whole numbers only:
  0 <= A,B <= maximum <= 10000, maximum >= 1. Unit is 1 to 24 characters
  without commas or brackets. Following static explanation is required.
  Controls are an explicit Example enhancement, never inferred from tables.
  The runtime glossable gate checks the complete block before rendering.
  Withheld blocks have no payload or controls. Invalid settings retain escaped static text.
  The native page offers a B slider and reset. No script means static text.
  Parameters are temporary presentation state, never scores or evidence.
  No authored executable content or remote imports are accepted.

  Optional linked line plot inside an Example callout:
    > [!EXAMPLE]
    > [LINEPLOT: 1,0,2]
    > Prediction: Which plotted points move if only the intercept changes?
    > Static explanation: Starting points (-2,-2), (0,0), (2,2); changed
    > points (-2,0), (0,2), (2,4). All three y values rise by 2.
    > Transfer: Without the control, sketch y = -x + 1 at x=-2,0,2.
  The three integers are slope, starting intercept and changed intercept,
  each -2 to 2; changed intercept must differ. The static explanation is
  present in plain Markdown and without script. A trusted renderer adds the
  linked equation, plot and exact-coordinate table. The learner commits a
  prediction before controls appear. This is unscored teaching state.

  A bank may carry one optional LESSON section: the teaching text its items
  test. It lives above the first question, opened by `## LESSON` at the start
  of a line and running to the first `Qn.` line that parses as a real question;
  its subheadings are one level deeper, `### heading text`, and each becomes a
  section an item can point at.

  A bank without a lesson section parses exactly as it did before this
  grammar existed, so adding a lesson to a real bank cannot break it.

  Each level-two preamble section -- LESSON, TERMS, SOURCES, CASES -- runs
  until the next level-two heading or the first question, whichever comes
  first, and a pipe row inside a fenced block belongs to no section. Their
  order in the preamble is free: TERMS above LESSON parses exactly as TERMS
  below it.

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
  lesson.invalid_comparison error    an Example comparison has invalid bounds
  lesson.invalid_lineplot   error    a LINEPLOT Example has invalid parameters
                                      or lacks a static explanation
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
  lesson.invalid_semantic_profile
                            error     [SEMANTIC-PROFILE:] is not a positive
                                      integer (D-16A-4)
  lesson.lang_empty         error     [LESSON-LANG:] is present but carries no
                                      language tag (A11Y-02)
  lesson.invalid_direction  error     [LESSON-DIR:] names a value outside
                                      ltr|rtl|auto (A11Y-02)
  lesson.invalid_step       error     a [STEP:] line whose id is not 1-64
                                      chars of a-z 0-9 hyphen starting
                                      alphanumeric (D-16D-2)
  lesson.duplicate_step     error     a step id authored twice, or the
                                      reserved id intro (D-16D-2)
  lesson.invalid_pace       warning   [LESSON-PACE:] names a value outside
                                      none|h3; pacing falls back to none
                                      (D-16D-2)
  lesson.unknown_semantic   warning   > [!KIND] names no known semantic role;
                                      it renders as a plain paragraph
                                      (D-16A-3)
  lesson.unknown_required_semantic
                            error     > [!KIND!] is marked required and names
                                      no known semantic role; it renders the
                                      unsupported-block fallback (D-16A-3)
  lesson.definition_before_example
                            warning   a heading places a definition before its
                                      first worked example (D-16A-6)
  lesson.example_order_no_reason
                            error     [EXAMPLE-ORDER: definition-first] carries
                                      no because clause (D-16A-6)
  media.duplicate_id        error     a ## MEDIA id is registered more than
                                      once (D-16A-7)
  media.missing_alt         error     a ## MEDIA row carries no accessible
                                      alternative (CAP-02)
  media.unknown_rights      error     a ## MEDIA row declares a rights value
                                      outside identity.RIGHTS_STATES (D-16A-8)
  media.unknown_availability
                            error     a ## MEDIA row declares an availability
                                      outside present|missing|remote
  media.ref_unknown         error     [MEDIA: <id>] names no id in the
                                      ## MEDIA registry
  media.declared_present_missing
                            warning   a ## MEDIA row declares availability
                                      present and the file is not beside the
                                      bank
  media.integrity_mismatch  warning   a ## MEDIA row records a sha256 that
                                      the file on disk does not match
  activity.duplicate_item   error     a ## ACTIVITIES item id is declared more
                                      than once (ACTIVITY-01)
  activity.empty_block      warning   ## ACTIVITIES carries a header row and no
                                      declarations
  activity.item_unknown     error     a ## ACTIVITIES row names no item in this
                                      bank
  activity.unknown_purpose  error     a purpose outside the ten declared
                                      purposes
  activity.demand_empty     error     the free-prose cognitive demand column is
                                      empty
  activity.unknown_retry    error     a retry value outside none|unlimited|
                                      until_correct|mode_controlled
  activity.unknown_feedback error     a feedback value outside the five
                                      declared policies
  activity.unknown_evidence_state
                            error     an evidence state the store cannot
                                      produce
  activity.missing_static_fallback
                            error     no static fallback, which an unsupported
                                      response form falls back to
  activity.missing_a11y_equivalent
                            error     no accessibility equivalence
  activity.unsupported_response_form
                            warning   a response form outside the shipped
                                      types; the activity falls back
  lesson.authored_key_disclosure
                            warning   authored text shown before a response
                                      reproduces keyed material the runtime
                                      withholds (an [!EXCERPT] body, a ## MEDIA
                                      alt, or an activity static fallback)
""")

# The Phase 6.2 gate grammar (06.2-CONTEXT D-02): one [GATE:] directive in
# the lesson preamble with exactly three legal values; a lesson declaring
# none defaults to "recommended". The value is validated at lint time -- an
# invalid value is a named lint error, never a render-time crash and never
# a silent default (T-062-01).
GATE_VALUES = ("required", "recommended", "off")


# The `## MEDIA` registry's fixed column order (D-16A-7). Eight columns: an id
# and a path, plus CAP-02's own six media fields verbatim. The order is fixed
# because the rows are positional, exactly as `## SOURCES` rows are, so
# reordering a column after a lesson carries one is a content migration and
# not a code change.
#
# The `rights` and `availability` vocabularies deliberately do NOT live here.
# `rights` is `identity.RIGHTS_STATES` reached through
# `capabilities.MEDIA_RIGHTS_STATES` (D-16A-8), and `availability` is
# `capabilities.MEDIA_AVAILABILITY`. Retyping either set of member strings in
# this file would mint a second vocabulary, which is the one thing D-16A-8
# exists to prevent.
MEDIA_COLUMNS = ("id", "path", "credit", "alt", "rights", "derivation",
                 "availability", "integrity")


# The `## ACTIVITIES` registry's fixed column order (ACTIVITY-01, plan
# 16A-06). Eleven columns: `item` prepended as the key, then ACTIVITY-01's own
# ten fields in the order its sentence names them. The order is this plan's
# choice, recorded in `16A-06-SUMMARY.md`, and the rows are positional, so
# reordering after a bank declares an activity is a content migration.
ACTIVITY_COLUMNS = ("item", "purpose", "demand", "objective", "stimulus",
                    "response_schema", "retry", "feedback", "evidence",
                    "a11y_equivalent", "static_fallback")

# The ten authoring purposes, transcribed from research stream 03 section
# 4.1's summary matrix in that table's own row order.
ACTIVITY_PURPOSES = ("prediction", "noticing", "retrieval", "explanation",
                     "comparison", "diagnosis", "practice", "transfer",
                     "reflection", "formal_assessment")

# Cognitive demand gets NO closed tuple, deliberately. Research stream 03
# section 4.1 gives a per-purpose "useful demand range" of verbs rather than an
# enum, so fixing a five-member Bloom-shaped tuple here would be this phase
# inventing a taxonomy the research left open on purpose. The `demand` column
# is free prose, validated as non-empty and nothing more, which is what can
# honestly be checked.

ACTIVITY_RETRY = ("none", "unlimited", "until_correct", "mode_controlled")

ACTIVITY_FEEDBACK = ("immediate", "after_commitment", "staged",
                     "withheld_until_submit", "non_evaluative")

# What `evidence.py` can ACTUALLY produce, and nothing else. Research stream
# 03's evidence-status column carries phrases like "mixed" and "stronger
# evidence, but claim limited to sampled contexts", which describe an
# inference a reader draws rather than a state the store records; adopting
# that phrasing would put members in a closed tuple that nothing can ever
# reach, and a state nothing can reach is a lie.
ACTIVITY_EVIDENCE_STATES = ("not_recorded", "activity_trace",
                            "scored_by_runtime", "pending_human_mark")

# The shipped item types. ACTIVITY-01 warrants a new type only when scoring
# semantics or response structure cannot be expressed safely, and none of the
# ten purposes above needs one on its own: an activity declaration is metadata
# beside a shipped form, never a new form. A response schema outside this
# tuple is a WARNING with a declared static fallback, not a reason to add a
# type.
RESPONSE_FORMS = ("mc", "multi", "table", "dnd", "build", "short", "check",
                  "visual", "fill")

# The semantic profile a lesson document was authored against (D-16A-4,
# PORT-01's "additive, versioned semantic profile"). A document declaring
# none is profile 1, so every bank written before this directive existed is
# a profile 1 document without being edited. The value is validated at lint
# time; the parse falls back rather than raising.
SEMANTIC_PROFILE_VERSION = 1

# The closed [EXAMPLE-ORDER:] vocabulary (D-16A-6), in GATE_VALUES' shape.
# CAP-01's default is a worked example before the formal definition; the
# second member is the override an author records a reason for.
LESSON_EXAMPLE_ORDERS = ("example-first", "definition-first")

# The closed direction vocabulary for [LESSON-DIR:] (A11Y-02), in
# GATE_VALUES' shape. There is deliberately no companion vocabulary for
# [LESSON-LANG:]: BCP 47 tags are an open set, and validating them would
# need a table this project has no reason to carry, so a language tag is
# checked for being non-empty and nothing more.
LESSON_DIRECTIONS = ("ltr", "rtl", "auto")

# Phase 16D pacing (D-16D-1, D-16D-2). The LESSON grammar's headings are
# `###` only (the `##` level is the section marker itself), so the only
# heading-derived rung is h3; a value naming a boundary that cannot occur
# would be inert and is not offered.
LESSON_PACE_VALUES = ("none", "h3")

# The authored step marker: `[STEP: <id>]` alone on a line, id 1-64 chars of
# a-z 0-9 hyphen starting alphanumeric. The id, never the ordinal, is what a
# resume position and a checkpoint anchor record (D-PACED-1's identity
# argument: an unidentified marker renumbers on insertion exactly the way a
# renderer-computed boundary does).
STEP_RE = re.compile(r"(?m)^\[STEP:\s*([a-z0-9][a-z0-9-]{0,63})\s*\]\s*$")
STEP_LINE_RE = re.compile(r"(?m)^\[STEP:.*$")

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


def _truncate_text(text, limit=70):
    """One short quotation of authored text for a lint message. Long enough
    that an author can find the block, short enough that a lint line stays a
    line."""
    flat = " ".join(str(text or "").split())
    return flat if len(flat) <= limit else flat[:limit - 3] + "..."


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


# The same additive sentinel once more, for the `## MEDIA` pass (plan
# 16A-05): "the caller did not supply media data" (skip every media check,
# which is what every pre-16A caller relies on) stays distinct from "the
# caller supplied media data and this bank has no ## MEDIA section and no
# [MEDIA:] reference", where `parse_media` legitimately returns None and there
# is genuinely nothing to check.
MEDIA_UNCHECKED = object()


# The same additive sentinel once more, for the `## ACTIVITIES` pass (plan
# 16A-06). A pre-16A caller that passes no activity data skips every activity
# check and gets byte-for-byte the lint output it got before.
ACTIVITIES_UNCHECKED = object()


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
    "bank.invalid_staged_cases",
    "item.unknown_format", "item.invalid_true_false",
    "item.duplicate_number", "item.select_mismatch", "item.correct_unknown_option",
    "item.too_few_options", "item.missing_second_best", "item.distractor_missing",
    "item.distractor_no_would_be", "item.too_few_categories", "item.row_category_unknown",
    "item.invalid_matching", "item.too_few_rows", "item.missing_distractor_notes", "item.too_few_steps",
    "item.duplicate_steps", "item.invalid_ordering", "item.missing_model", "item.too_few_rubric_points",
    "item.model_too_long", "item.rubric_point_too_long", "item.missing_why_best",
    "item.missing_trap", "item.low_confidence", "item.duplicate_stem",
    "item.missing_id", "item.duplicate_id", "item.missing_hash",
    "item.content_drift", "item.check_lang_unknown", "item.check_too_few_cases",
    "item.no_normalizer", "item.tolerance_unstated", "item.input_format_invalid",
    "item.objective_unnamespaced", "item.lesson_ref_unknown",
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
    "item.structure_nonconformant",
    "lesson.invalid_gate", "lesson.check_ref_unknown",
    "lesson.invalid_semantic_profile", "lesson.lang_empty",
    "lesson.invalid_direction", "lesson.invalid_comparison", "lesson.invalid_lineplot",
    "lesson.invalid_step", "lesson.duplicate_step", "lesson.invalid_pace",
    "lesson.unknown_semantic", "lesson.unknown_required_semantic",
    "lesson.definition_before_example", "lesson.example_order_no_reason",
    "media.duplicate_id", "media.missing_alt", "media.unknown_rights",
    "media.unknown_availability", "media.ref_unknown",
    "media.declared_present_missing", "media.integrity_mismatch",
    "activity.duplicate_item", "activity.empty_block", "activity.item_unknown",
    "activity.unknown_purpose", "activity.demand_empty",
    "activity.unknown_retry", "activity.unknown_feedback",
    "activity.unknown_evidence_state", "activity.missing_static_fallback",
    "activity.missing_a11y_equivalent", "activity.unsupported_response_form",
    "lesson.authored_key_disclosure",
}))


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

def _looks_float(s):
    """True when `s` parses as a decimal float (a '.' or an exponent is
    present), so an integer-expected harness case never demands a
    [TOLERANCE:] of its own."""
    try:
        float(s)
    except (TypeError, ValueError):
        return False
    return "." in s or "e" in s.lower()


def structure_findings(q, tag):
    """Structural conformance with the body that governs this item's subject.

    Subject-scoped on purpose (see `subjects.STRUCTURE_RULES`): NREMT binds
    EMT and has no authority over Math 1400 or CSCI 1100, so an item whose
    objective names another subject, or names no subject at all, is checked
    against nothing. This is a tier 1 mechanical check in the sense of
    `.planning/research/2026-08-24-item-writing-standards.md`: it counts
    options and keyed answers and makes no judgement about meaning, which is
    why it can be an error at all. Whether options are mutually exclusive IN
    MEANING is tier 3 and deliberately not a lint rule.
    """
    import evidence, subjects        # function-local: model owns no store
    rules = subjects.structure_rules(
        evidence.subject_of(q.get("objective") or ""))
    if not rules:
        return []
    shapes = rules.get(q.get("type"))
    shape = subjects.structure_shape(q)
    if not shapes or shape is None or shape in shapes:
        return []
    allowed = " or ".join("%d correct of %d options" % (c, o) for o, c in shapes)
    return [LintError(
        "item.structure_nonconformant", "opts", tag,
        "%s permits %s for a %s item; this one has %d correct of %d options"
        % (rules["authority"], allowed, q.get("type"), shape[1], shape[0]))]


def lint(questions, lesson=LESSON_UNCHECKED, terms=TERMS_UNCHECKED,
         keys=KEYS_UNCHECKED, style=STYLE_UNCHECKED,
         sources=SOURCES_UNCHECKED, cases=CASES_UNCHECKED,
         paraphrase=PARAPHRASE_UNCHECKED, media=MEDIA_UNCHECKED,
         activities=ACTIVITIES_UNCHECKED):
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
    # The normalizer registry is in play only when this bank actually uses it
    # (contains a check item). A short item in a registry-using bank has no
    # registered normalizer and lands pending -- the author is told. In a
    # legacy bank a short item's pending behaviour is the type's documented
    # design, not an authoring surprise, so nothing is flagged.
    uses_check = any(o["type"] == "check" for o in questions)
    pair_counts = {}
    lesson_on = lesson is not LESSON_UNCHECKED
    terms_on = terms is not TERMS_UNCHECKED
    keys_on = keys is not KEYS_UNCHECKED
    style_on = style is not STYLE_UNCHECKED
    sources_on = sources is not SOURCES_UNCHECKED
    cases_on = cases is not CASES_UNCHECKED
    paraphrase_on = paraphrase is not PARAPHRASE_UNCHECKED
    media_on = media is not MEDIA_UNCHECKED
    activities_on = activities is not ACTIVITIES_UNCHECKED
    for message in staged_case_spec_errors(questions):
        errors.append(LintError("bank.invalid_staged_cases", "staged_cases", "BANK", message))
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

        input_format = q.get("input_format") or "plain"
        if input_format not in ("plain", "latex") or (input_format == "latex" and t != "short"):
            errors.append(LintError(
                "item.input_format_invalid", "input_format", tag,
                "[INPUT:] must be plain, or latex on a short item; got %r on %s"
                % (input_format, t)))

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
            answer_format = q.get("answer_format", "")
            if answer_format and answer_format != "true-false":
                errors.append(LintError("item.unknown_format", "format", tag,
                              "FORMAT must be true-false when present"))
            if answer_format == "true-false" and (t != "mc"
                    or sorted(q["opts"]) != ["A", "B"]
                    or [q["opts"][letter].strip().casefold() for letter in ("A", "B")]
                    not in (["true", "false"], ["false", "true"])
                    or len(q["correct"]) != 1):
                errors.append(LintError("item.invalid_true_false", "format", tag,
                              "true-false needs one correct answer and exactly True and False options"))
            if len(q["opts"]) < 3 and answer_format != "true-false":
                errors.append(LintError("item.too_few_options", "opts", tag,
                              "only %d options" % len(q["opts"])))
            errors.extend(structure_findings(q, tag))
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
            for message in matching_spec_errors(q):
                errors.append(LintError("item.invalid_matching", "matching", tag, message))
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
            for message in ordering_spec_errors(q):
                errors.append(LintError("item.invalid_ordering", "ordering", tag, message))
            if len(q["steps"]) < 2:
                errors.append(LintError("item.too_few_steps", "steps", tag,
                              "build list has fewer than two steps"))
            if "ordering" not in q and len(set(q["steps"])) != len(q["steps"]):
                errors.append(LintError("item.duplicate_steps", "steps", tag,
                              "duplicate steps in build list"))
            if not q.get("notes"):
                warnings.append(LintError("item.missing_distractor_notes", "notes", tag,
                                "no DISTRACTOR ANALYSIS bullets"))

        elif t == "fill":
            from runtime import fill_spec_errors
            for field, message in fill_spec_errors(q):
                errors.append(LintError("item.fill_invalid", field, tag, message))

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

        elif t == "check":
            # Language is validated against the allowlist, never defaulted:
            # a tag naming an interpreter that is not configured must be
            # caught at authoring time (D-02). runner is imported lazily so
            # model.py keeps its no-imports-from-peers property at module
            # scope.
            from runner import LANGUAGES
            lang = q.get("lang") or "python"
            if lang not in LANGUAGES:
                errors.append(LintError("item.check_lang_unknown", "lang", tag,
                              "check item requests language %r, which is not in "
                              "the allowlist (%s); never silently defaulted (D-02)"
                              % (lang, ", ".join(sorted(LANGUAGES)))))
            if len(q.get("cases") or []) < 2:
                warnings.append(LintError("item.check_too_few_cases", "cases", tag,
                                "check item has fewer than two CASE) lines; one "
                                "case tests almost nothing (D-03)"))
            harness = q.get("harness") or ""
            if harness and q.get("tolerance") is None and any(
                    _looks_float(c.get("expected", "")) for c in q.get("cases") or []):
                errors.append(LintError(
                    "item.tolerance_unstated", "tolerance", tag,
                    "harness item's expected values include a float but no "
                    "[TOLERANCE:] is stated; float comparison would be "
                    "machine-dependent (D-20)"))

        elif t == "visual":
            for finding in _visual_lint_findings(q, tag):
                errors.append(finding)

        if uses_check:
            from runtime import supports_auto_verdict
            if not supports_auto_verdict(t):
                warnings.append(LintError(
                    "item.no_normalizer", "type", tag,
                    "%s items have no registered normalizer; their responses "
                    "land pending, never a False verdict (D-21)" % t))

        if t not in ("short", "check") and not q.get("why"):
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
            # Phase 16A directive findings (D-16A-4, A11Y-02). Each fires
            # only when its `_raw` companion is non-empty, so a bank carrying
            # none of the three directives emits none of these three findings
            # and the shipped lint output is byte identical. The reader has
            # already fallen back by the time lint runs; these findings name
            # what the author wrote, which a report of the fallback alone
            # could not.
            profile_raw = lesson.get("semantic_profile_raw") or ""
            if profile_raw:
                errors.append(LintError(
                    "lesson.invalid_semantic_profile", "semantic_profile",
                    "BANK",
                    "[SEMANTIC-PROFILE: %s] is not a positive integer; the "
                    "reader falls back to profile 1" % profile_raw))
            if lesson.get("lang_raw"):
                errors.append(LintError(
                    "lesson.lang_empty", "lang", "BANK",
                    "[LESSON-LANG:] carries no language tag; the reader "
                    "falls back to en"))
            dir_raw = lesson.get("dir_raw") or ""
            if dir_raw:
                errors.append(LintError(
                    "lesson.invalid_direction", "dir", "BANK",
                    "[LESSON-DIR: %s] is not one of ltr, rtl, auto; the "
                    "reader falls back to auto" % dir_raw))
            # Phase 16D pacing findings (D-16D-1, D-16D-2). A step id is a
            # resumable identity, so malformed and duplicated ids are
            # errors; a bad pace value only coarsens pacing, so it is a
            # warning. A bank with no [STEP:] line and no [LESSON-PACE:]
            # tag emits none of these and the shipped output is byte
            # identical.
            pace_raw = lesson.get("pace_raw") or ""
            if pace_raw:
                warnings.append(LintError(
                    "lesson.invalid_pace", "pace", "BANK",
                    "[LESSON-PACE: %s] is not one of none, h3; pacing "
                    "falls back to none" % pace_raw))
            seen_steps = set()
            for raw_line in (lesson.get("body") or "").split("\n"):
                if not raw_line.lstrip().startswith("[STEP:"):
                    continue
                sm = STEP_RE.match(raw_line)
                if sm is None:
                    errors.append(LintError(
                        "lesson.invalid_step", "step", "BANK",
                        "[STEP:] id must be 1-64 chars of a-z 0-9 hyphen, "
                        "starting alphanumeric: %s" % raw_line.strip()))
                    continue
                step_id = sm.group(1)
                if step_id in seen_steps or step_id == "intro":
                    errors.append(LintError(
                        "lesson.duplicate_step", "step", "BANK",
                        "[STEP: %s] appears more than once; a resumable "
                        "step needs one identity" % step_id))
                seen_steps.add(step_id)
            # Phase 16A unknown-semantic findings (D-16A-3, CAP-01's
            # Degraded clause). The marker shape and the required-marker
            # rule come from the shared Markdown block parser.
            # One finding per DISTINCT kind, in
            # first-appearance order, so a lesson using the same unknown
            # kind six times reports it once rather than six times.
            # Validate only the explicitly opted-in Example body. Ordinary
            # examples, tables and emphasis retain their existing meaning.
            # The reader protects fences per heading. An unterminated fence
            # in one heading must not hide declarations in the next.
            protected = "\n\n".join(
                protect_fenced_code(part)[0] for part in re.split(
                    r"(?m)(?=^###\s)", lesson.get("body") or ""))
            comparison_lines = protected.split("\n")
            index = 0
            while index < len(comparison_lines):
                raw_line = comparison_lines[index]
                index += 1
                marker = CALLOUT_MARK_RE.match(raw_line)
                if marker is None or not callout_entered(raw_line):
                    continue
                block = [marker.group(2)] if marker.group(2) else []
                while index < len(comparison_lines) and comparison_lines[index].startswith(">"):
                    following = comparison_lines[index]
                    block.append(re.sub(r"^>\s?", "", following))
                    index += 1
                kind, _ = callout_required_of(marker.group(1))
                if kind != "EXAMPLE":
                    continue
                comparison = parse_lesson_comparison("\n".join(block))
                if comparison and comparison.get("error"):
                    errors.append(LintError("lesson.invalid_comparison",
                                            "semantics", "BANK", comparison["error"]))
                lineplot = parse_lesson_lineplot("\n".join(block))
                if lineplot and lineplot.get("error"):
                    errors.append(LintError("lesson.invalid_lineplot",
                                            "semantics", "BANK", lineplot["error"]))
            seen_unknown = []
            for raw_line in (lesson.get("body") or "").split("\n"):
                cm = CALLOUT_MARK_RE.match(raw_line)
                if cm is None:
                    continue
                marker = cm.group(1)
                if callout_spec(marker) is not None:
                    continue
                kind, required = callout_required_of(marker)
                if callout_spec(kind) is not None and required:
                    continue
                if (kind, required) in seen_unknown:
                    continue
                seen_unknown.append((kind, required))
                if required:
                    errors.append(LintError(
                        "lesson.unknown_required_semantic", "semantics",
                        "BANK",
                        "[!%s!] is marked required and is not a known "
                        "semantic role; it renders the unsupported-block "
                        "fallback" % kind))
                else:
                    warnings.append(LintError(
                        "lesson.unknown_semantic", "semantics", "BANK",
                        "[!%s] is not a known semantic role; it renders as "
                        "a plain paragraph" % kind))
            # Phase 16A worked-example-order findings (D-16A-6, CAP-01's
            # "worked example or concrete case before the formal
            # definition" default and its recorded-override clause).
            #
            # The check runs PER HEADING BODY, never per lesson. A per-lesson
            # check fires on any lesson whose first heading is an overview,
            # and a warning that fires on correct documents is worse than no
            # warning: it teaches the author to skim lint output.
            #
            # Offsets are compared with `str.find` on three literal markers
            # rather than with a regex scan, so the rule stays readable and
            # its false-positive surface stays small.
            order = lesson.get("example_order") or "example-first"
            reason = lesson.get("example_order_reason") or ""
            if order == "definition-first" and not reason:
                errors.append(LintError(
                    "lesson.example_order_no_reason", "example_order",
                    "BANK",
                    "[EXAMPLE-ORDER: definition-first] carries no because "
                    "clause; CAP-01 requires a recorded reason for the "
                    "override"))
            # An override with no reason is not an override, so it does not
            # suppress. Only a reasoned one does.
            if not (order == "definition-first" and reason):
                for h in lesson["headings"]:
                    body = h.get("body") or ""
                    ex = body.find("> [!EXAMPLE]")
                    if ex == -1:
                        continue
                    key = body.find("> [!KEY]")
                    term = body.find("[[")
                    firsts = [o for o in (key, term) if o != -1 and o < ex]
                    if not firsts:
                        continue
                    warnings.append(LintError(
                        "lesson.definition_before_example", "headings",
                        "BANK",
                        "heading %r places a definition before its first "
                        "worked example; CAP-01's default is example "
                        "first, or record a reason with [EXAMPLE-ORDER: "
                        "definition-first because ...]" % h["text"]))
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

    # Bank-level media findings (CAP-02, D-16A-7, D-16A-8), in a
    # deterministic order: duplicates, then per-asset field checks in registry
    # order, then unresolvable references in document order, so two runs over
    # one bank produce byte-identical output.
    #
    # The rights and availability vocabularies are READ from `capabilities`
    # through a function-local import, never restated here. `capabilities`
    # does not import `model`, so this edge does not cycle; the local import
    # keeps this optional capability dependency local to media linting.
    #
    # Membership is all that is checked. No finding here gates anything, and
    # no code path in Phase 16A reads a rights value to decide whether an
    # operation may proceed (D-16A-8): 16A declares and does not enforce.
    if media_on and media:
        import capabilities as _capabilities
        for aid in media.get("duplicates") or []:
            errors.append(LintError(
                "media.duplicate_id", "media", "BANK",
                "media id %s is registered more than once; the first "
                "registration is used" % aid))
        assets = media.get("assets") or {}
        for aid, asset in assets.items():
            if not (asset.get("alt") or "").strip():
                errors.append(LintError(
                    "media.missing_alt", "media", "BANK",
                    "media id %s carries no accessible alternative; the alt "
                    "column is required because the alternative is the only "
                    "copy a reader without the image has" % aid))
            rights = (asset.get("rights") or "").strip()
            if rights not in _capabilities.MEDIA_RIGHTS_STATES:
                errors.append(LintError(
                    "media.unknown_rights", "media", "BANK",
                    "media id %s declares rights %s, which is not one of %s"
                    % (aid, rights or "''",
                       ", ".join(_capabilities.MEDIA_RIGHTS_STATES))))
            availability = (asset.get("availability") or "").strip()
            if availability not in _capabilities.MEDIA_AVAILABILITY:
                errors.append(LintError(
                    "media.unknown_availability", "media", "BANK",
                    "media id %s declares availability %s, which is not one "
                    "of %s" % (aid, availability or "''",
                               ", ".join(_capabilities.MEDIA_AVAILABILITY))))
        # `17C-AUDIT.md` F-LOSS-5. A restored course carried its bank and not
        # the file the bank's MEDIA row declares `present`, and lint reported
        # zero findings, so the first person to meet the loss was the reader
        # of a page with a missing diagram. These two check the declaration
        # against the disk. They are warnings, not errors: a bank read on a
        # machine that does not hold the asset yet (a fresh restore, a
        # partial sync) is not malformed, and an availability of `missing` or
        # `remote` is an honest declaration this must not punish. Only
        # `present` is checked, because only `present` is a claim about this
        # disk.
        bank_dir = os.path.dirname(os.path.abspath(media.get("path") or ""))
        for aid, asset in assets.items():
            if (asset.get("availability") or "").strip() != "present":
                continue
            rel = (asset.get("path") or "").strip()
            if not rel or "://" in rel:
                continue
            target = os.path.normpath(os.path.join(bank_dir, rel))
            if not os.path.exists(target):
                warnings.append(LintError(
                    "media.declared_present_missing", "media", "BANK",
                    "media id %s declares availability present, but %s does "
                    "not exist beside this bank; the declaration and the "
                    "disk disagree" % (aid, rel)))
                continue
            declared = (asset.get("integrity") or "").strip().lower()
            if not declared.startswith("sha256:"):
                continue
            with open(target, "rb") as source_handle:
                digest = hashlib.sha256(source_handle.read()).hexdigest()
            if digest != declared.split(":", 1)[1].strip():
                warnings.append(LintError(
                    "media.integrity_mismatch", "media", "BANK",
                    "media id %s records %s, but %s on disk digests as "
                    "sha256:%s; the file changed since it was recorded"
                    % (aid, declared, rel, digest)))

        for ref in media.get("refs") or []:
            if ref["id"] not in assets:
                errors.append(LintError(
                    "media.ref_unknown", "media", "BANK",
                    "[MEDIA: %s] under heading %r names no id in the "
                    "## MEDIA registry" % (ref["id"], ref["heading"])))

    # Bank-level activity findings (ACTIVITY-01, plan 16A-06), in a
    # deterministic order: duplicates, then the empty-section warning, then
    # per-row checks in DOCUMENT order, so two runs over one bank produce
    # byte-identical output and the findings read down the registry the way
    # the author wrote it.
    #
    # None of these findings gates anything. The `feedback`, `retry`, and
    # `evidence` columns are validated for membership and read by nothing
    # else: they describe what the runtime already does, and a declaration
    # that changed what the runtime did would be a second authority.
    if activities_on and activities:
        known_items = {q.get("id") for q in questions}
        known_items.update(q.get("item_id") for q in questions
                           if q.get("item_id"))
        known_items.discard(None)
        for item in activities.get("duplicates") or []:
            errors.append(LintError(
                "activity.duplicate_item", "activities", "BANK",
                "item %s is declared more than once in ## ACTIVITIES; the "
                "first declaration is used" % item))
        if activities.get("empty"):
            warnings.append(LintError(
                "activity.empty_block", "activities", "BANK",
                "## ACTIVITIES carries a header row and no declarations"))
        declared = activities.get("activities") or {}
        for item in activities.get("order") or []:
            row = declared.get(item) or {}
            if item not in known_items:
                errors.append(LintError(
                    "activity.item_unknown", "activities", "BANK",
                    "## ACTIVITIES declares item %s, which is not an item in "
                    "this bank" % item))
            purpose = (row.get("purpose") or "").strip()
            if purpose not in ACTIVITY_PURPOSES:
                errors.append(LintError(
                    "activity.unknown_purpose", "activities", "BANK",
                    "item %s declares purpose %s, which is not one of the "
                    "ten declared purposes" % (item, purpose or "''")))
            if not (row.get("demand") or "").strip():
                errors.append(LintError(
                    "activity.demand_empty", "activities", "BANK",
                    "item %s declares no cognitive demand; the demand column "
                    "is free prose and must say something" % item))
            retry = (row.get("retry") or "").strip()
            if retry not in ACTIVITY_RETRY:
                errors.append(LintError(
                    "activity.unknown_retry", "activities", "BANK",
                    "item %s declares retry %s, which is not one of %s"
                    % (item, retry or "''", ", ".join(ACTIVITY_RETRY))))
            feedback = (row.get("feedback") or "").strip()
            if feedback not in ACTIVITY_FEEDBACK:
                errors.append(LintError(
                    "activity.unknown_feedback", "activities", "BANK",
                    "item %s declares feedback %s, which is not one of %s"
                    % (item, feedback or "''", ", ".join(ACTIVITY_FEEDBACK))))
            state = (row.get("evidence") or "").strip()
            if state not in ACTIVITY_EVIDENCE_STATES:
                errors.append(LintError(
                    "activity.unknown_evidence_state", "activities", "BANK",
                    "item %s declares evidence %s, which is not one of %s"
                    % (item, state or "''",
                       ", ".join(ACTIVITY_EVIDENCE_STATES))))
            if not (row.get("static_fallback") or "").strip():
                errors.append(LintError(
                    "activity.missing_static_fallback", "activities", "BANK",
                    "item %s declares no static fallback; ACTIVITY-01 "
                    "requires one because an unsupported response form falls "
                    "back to it" % item))
            if not (row.get("a11y_equivalent") or "").strip():
                errors.append(LintError(
                    "activity.missing_a11y_equivalent", "activities", "BANK",
                    "item %s declares no accessibility equivalence" % item))
            form = (row.get("response_schema") or "").strip()
            if form not in RESPONSE_FORMS:
                # A WARNING, not an error. Falling back is the declared
                # behavior ACTIVITY-01's Degraded clause names, so an
                # unsupported form is a documented state and not a defect.
                warnings.append(LintError(
                    "activity.unsupported_response_form", "activities",
                    "BANK",
                    "item %s declares response form %s, which is not one of "
                    "the shipped forms; the activity falls back to its "
                    "declared static equivalent" % (item, form or "''")))

    # Authored text shown BEFORE a response exists, checked against the one
    # gate that already decides what is keyed material (plan 16A-09 finding
    # F3, resolved 2026-08-28).
    #
    # Phase 16A added three places an author can put prose a learner reads
    # before answering: an [!EXCERPT] body, a ## MEDIA row's alt, and an
    # activity's static_fallback. Each is a new mouth for the same old leak,
    # and none of them is gated at render time, deliberately: a lesson page is
    # authored reading material, and suppressing an author's own words at
    # render would be inventing an enforcement this phase does not own.
    #
    # So the signal is delivered where it can be acted on, at authoring time.
    # `runtime.glossable` is consulted rather than a second detector being
    # written: it already answers "could this text disclose keyed answer
    # material", its fragment set is the fields `public_item` withholds, and
    # two gates that disagreed about what counts as keyed would be worse than
    # one gate that is occasionally too strict. The import is function-local
    # because `runtime` does not import `model` and this keeps it that way.
    #
    # A WARNING, not an error. An author may have a real reason to quote a
    # rationale into an excerpt, and the finding names the surface and the
    # text so they can judge it. What they must not do is not know.
    if lesson_on and lesson and not lesson.get("error"):
        from runtime import glossable as _glossable

        authored = []
        body_lines = (lesson.get("body") or "").split("\n")
        for index, line in enumerate(body_lines):
            # `[^\S\n]*` and not `\s*`: `\s` matches a newline, which would
            # let the marker pattern swallow the first body line and quote it
            # back with its own `>` prefix still attached.
            marker = re.match(r"^>[^\S\n]*\[!EXCERPT!?\][^\S\n]*(.*)$", line)
            if marker is None:
                continue
            block = []
            trailing = marker.group(1).strip()
            if trailing:
                block.append(trailing)
            for following in body_lines[index + 1:]:
                if not following.startswith(">"):
                    break
                block.append(re.sub(r"^>\s?", "", following))
            body_text = " ".join(part for part in block if part.strip())
            if body_text.strip():
                authored.append(("an [!EXCERPT] body", body_text))
        if media_on and media:
            for aid, asset in (media.get("assets") or {}).items():
                alt = (asset.get("alt") or "").strip()
                if alt:
                    authored.append(("the ## MEDIA alt for %s" % aid, alt))
        if activities_on and activities:
            for item, row in (activities.get("activities") or {}).items():
                fallback = (row.get("static_fallback") or "").strip()
                if fallback:
                    authored.append(
                        ("the static fallback for %s" % item, fallback))

        for where, text in authored:
            if not _glossable(questions, {"def": text}):
                warnings.append(LintError(
                    "lesson.authored_key_disclosure", "semantics", "BANK",
                    "%s reproduces keyed material the runtime withholds "
                    "before a learner responds: %r. A learner reads this "
                    "without answering anything" % (where, _truncate_text(text))))

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
    with open(path, encoding="utf-8") as stream:
        qs = parse_bank(stream.read())
    if not qs:
        sys.exit("No question blocks found in %s. Run `itembank spec` for the format." % path)
    return qs
