"""Style enforcement behind the model facade."""
import collections, re


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
    import model
    sev = (row.get("severity") or "warn").strip().lower()
    if sev in STYLE_SEVERITIES:
        return sev, None
    return None, model.LintError(
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
    import model
    errors, warnings = [], []
    if not isinstance(style, dict) or style.get("error"):
        return errors, warnings
    if lesson is model.LESSON_UNCHECKED:
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
            model.LintError(code, "lesson", "BANK", message))

    def ceiling(row, code, sev):
        """Enforce the earned-severity ceiling (D-13): a row may re-severity
        downward but never raise a check above its catalogue rating."""
        rating = STYLE_CHECK_CATALOGUE[code]
        if sev == "error" and rating == "warn":
            errors.append(model.LintError(
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
                errors.append(model.LintError(
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
                errors.append(model.LintError(
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
                errors.append(model.LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (cadence.section) has no params" % rid))
                continue
            effective = ceiling(row, "style.heading_cadence", sev)
            if len(params) == 2 and _style_is_int(params[0]) \
                    and _style_is_int(params[1]):
                lo, hi = int(params[0]), int(params[1])
                if lo < 0 or hi <= lo:
                    errors.append(model.LintError(
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
                    slug = model.lesson_slug(name)
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
                errors.append(model.LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (style.require) needs a marker and a count, "
                    "got %r" % (rid, row.get("params") or "")))
                continue
            marker, n_tok = params[0], params[1]
            if not _style_is_int(n_tok) or int(n_tok) < 1:
                errors.append(model.LintError(
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
                errors.append(model.LintError(
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
                errors.append(model.LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (style.forbid) names '%s', which is not a "
                    "known forbidden category or marker" % (rid, target)))
        elif kind == "open.with":
            if len(params) != 1:
                errors.append(model.LintError(
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
                errors.append(model.LintError(
                    "style.unknown_parameter", "rules", "BANK",
                    "rule '%s' (density.max) needs a target and a cap, got %r"
                    % (rid, row.get("params") or "")))
                continue
            x, n_tok = params[0], params[1]
            if x.startswith("style."):
                continue  # lexical config, handled above
            if not _style_is_int(n_tok) or int(n_tok) < 1:
                errors.append(model.LintError(
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
    import model
    suppressed = set(_STYLE_IGNORE_RE.findall(lesson_text or ""))
    locked = sorted(suppressed & model.LOCKED_RULE_IDS)
    ignore_errors = [
        model.LintError("style.ignore_locked", "body", "BANK",
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


