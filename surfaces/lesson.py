"""The lesson reader: a bank's teaching text rendered as a document, linked
both ways to the items that test it.

This is a read-only render of author-provided prose. It holds no answer key
and reaches no verdict, and its links navigate rather than answer (D-10): the
only way out of a lesson is to another surface, never to a score.
"""
import html, os, re, sys

from model import grab, lesson_slug, load, parse_lesson
from surfaces.presentation import SHARED_CSS
from surfaces.theme import THEME_CSS


SUB_BYLINE = ("Reading material for this bank. Following a link below opens "
              "the item in a new tab; nothing here is scored.")

EMPTY_HEADING = "No lesson yet"
EMPTY_BODY = ("This bank has no ## LESSON section. Add one above the first "
              "Qn. line \u2014 see itembank spec for the LESSON/LESSON-REF grammar.")
WARN_SENTENCE = ("The external lesson file for this bank could not be read. "
                 "Run itembank lint %s for details.")
ORPHAN_COPY = "No items reference this section yet."
BACKLINKS_LABEL = "Items testing this"
CHIP_LABEL = "Read the lesson"

# Only the degraded state carries the warn note, so its style is substituted
# in (like __THEME__) rather than shipped on every page -- a bank with no
# lesson and a bank whose lesson source broke must be visually
# distinguishable, and the plain empty state must contain no --warn styling
# at all. `overflow-wrap`/`word-break` make a long [LESSON-SRC:] path wrap
# inside the card; there is deliberately no nowrap and no ellipsis
# truncation on the code element.
WARN_CSS = """.warn{color:var(--warn);font-size:14px;margin:14px auto 0;max-width:520px;
  text-align:center}
.warn code{overflow-wrap:anywhere;word-break:break-all}
"""


# The lesson reader's own CSS layer (03.1-UI-SPEC §2 Reader CSS LOCKED):
# structure and spacing only, riding the shared theme tokens and SHARED_CSS.
# Fonts resolve by token -- --font-paper for Paper-voice prose, --font-ledger
# for Ledger-voice labels -- never a literal family. Sizes are the locked
# project scale (12/16/18/20/32) and the weight pair is 400/600; this layer
# introduces no sixth size and no third weight. Every colour is var(--token):
# no hex literal, no second palette (03.1-UI-SPEC §5).
LESSON_CSS = r"""
.wrap{max-width:var(--measure-prose);margin:0 auto;
  padding:var(--space-4) var(--space-3) var(--space-7);
  font-family:var(--font-paper)}
header{margin-bottom:var(--space-4)}
h1{font-size:32px;font-weight:600;line-height:1.1;margin:0 0 var(--space-3)}
.sub{color:var(--mut);font-size:12px}
.card{background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:var(--space-4) var(--space-4) var(--space-3)}
section{margin-bottom:var(--space-4)}
h2{font-size:20px;font-weight:600;line-height:1.2;margin:var(--space-6) 0 var(--space-3)}
h3{font-size:16px;font-weight:600;line-height:1.4;margin:var(--space-5) 0 var(--space-2)}
p,li{font-size:18px;line-height:var(--leading-lesson);
  margin:0 0 var(--space-3)}
.bl{margin-top:var(--space-2);padding-top:var(--space-2);
  border-top:1px solid var(--line)}
.blabel{display:block;font-size:12px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--mut);margin-bottom:var(--space-1);
  font-family:var(--font-ledger)}
.bl a{display:block;color:var(--accent);text-decoration:none;
  margin:var(--space-1) 0}
.bl a:hover,.bl a:focus-visible{text-decoration:underline;
  outline:2px solid var(--accent);outline-offset:2px}
.scroll{overflow-x:auto;margin:0 0 var(--space-2);
  max-width:var(--measure-wide)}
pre{margin:0;background:var(--chip);border-radius:8px;
  padding:var(--space-2) var(--space-3)}
pre code{display:block;font-family:var(--font-ledger);font-size:14px;
  line-height:1.5;color:var(--ink)}
.lang{display:block;font-size:12px;letter-spacing:.05em;color:var(--mut);
  margin-bottom:var(--space-1);font-family:var(--font-ledger)}
table{border-collapse:collapse;margin:0 0 var(--space-2);min-width:100%}
th,td{border:1px solid var(--line);padding:var(--space-2);
  text-align:left;font-size:14px}
th{background:var(--chip);color:var(--mut);font-weight:600}
.orphan{color:var(--mut);font-size:14px}
.empty{text-align:center;padding:var(--space-6) var(--space-3)}
.empty p{color:var(--mut);max-width:var(--measure-prose);margin:0 auto}
.callout{background:var(--card);border:1px solid var(--line);
  border-radius:var(--r-3);box-shadow:0 1px 0 var(--line);
  padding:var(--space-3);margin:0 0 var(--space-4)}
.callout-label{display:flex;align-items:center;gap:var(--space-1);
  font-size:12px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--mut);margin:0 0 var(--space-2);font-family:var(--font-ledger)}
.callout-icon{display:inline-flex}
.callout-body p:last-child{margin:0}
@media print{
  @page{margin:18mm}
  h2{break-after:avoid}
  [popover]{display:none}
  .callout{box-shadow:none}
  .callout-check{border:0;border-top:1px solid var(--line);border-radius:0;
    background:none;padding:var(--space-2) 0 0}
  /* Check · <objective> label lands with the gate that fills the slot
     (plan 03.1-04 / Phase 6.2); the reserved slot prints as a labelled
     rule, never an empty box (03.1-UI-SPEC §9.4 D1). */
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
/* ?print=drill second-stylesheet placeholder hook: cloze blanking and the
   Answers list land in plan 03.1-04 as a second stylesheet plus one
   server-side blanking pass -- never a second renderer (03.1-UI-SPEC §10). */
"""


LESSON_TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>
__THEME__
__SHARED_CSS__
__LESSON_CSS__
__WARN_CSS__
</style></head><body><div class="wrap">
<header>
  <h1>__TITLE__</h1>
  <div class="sub">__SUB__</div>
</header>
<div class="card">__BODY__</div>
</div></body></html>"""


def _truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit] + "\u2026"


_TOKEN_RE = re.compile(r"^\x00K(\d+)\x00$")
_FENCE_RE = re.compile(r"^(`{3,})\s*(.*?)\s*$")
_CALLOUT_MARK_RE = re.compile(r"^>\s*\[!([A-Za-z][^\]]*)\]\s*(.*)$")

# The locked callout kinds (03.1-UI-SPEC §9.2-§9.4): each maps to the exact
# Ledger-voice label the renderer and the linter share (§15). The `CHECK:`
# prefix is handled separately as the inert reserved slot (D-18). Adding a
# kind is a one-line registration here -- the container and its degradation
# contract do not change.
_CALLOUT_KINDS = {
    "KEY": ("key", "Key point"),
    "EXAMPLE": ("example", "Example"),
    "NOTE": ("note", "Note"),
    "WARNING": ("warning", "Warning"),
}

# One in-repo decorative callout mark (03.1-UI-SPEC §2): a single 16×16
# currentColor SVG glyph, aria-hidden, whose visible Ledger label carries
# all semantics -- an icon that fails to render loses nothing.
_CALLOUT_ICON = ('<svg width="16" height="16" viewBox="0 0 16 16" '
                 'aria-hidden="true" focusable="false"><rect x="1.5" y="1.5" '
                 'width="13" height="13" rx="2.5" fill="none" '
                 'stroke="currentColor" stroke-width="1.5"/>'
                 '<path d="M8 6.5v4" stroke="currentColor" stroke-width="1.5" '
                 'stroke-linecap="round"/><circle cx="8" cy="4.3" r="1" '
                 'fill="currentColor"/></svg>')


def _callout_spec(raw):
    """Map one `[!KIND]` marker to its locked `(slug, label)` pair, or None.

    `CHECK:` (with or without an id) maps to the inert reserved slot; the id
    is deliberately dropped -- the anchor carries no key and no scoring path
    (D-18). Any other kind returns None so the block classifier falls
    through to the pre-change paragraph output byte-for-byte: an unknown
    kind never raises and never invents a container.
    """
    kind = raw.strip()
    if kind.startswith("CHECK:"):
        return ("check", "Check")
    return _CALLOUT_KINDS.get(kind)


def _callout_html(spec, body):
    """One honest callout container (D-18): a `<section class="callout
    callout-<slug>">` whose Ledger-voice label and decorative icon are
    accompanied by the escape-first `_inline()` body pass every other text
    run uses (T-031-01). The `[!CHECK: <id>]` variant renders the inert
    reserved slot with the exact Ledger copy and no form, no key, and no
    scoring path (03.1-UI-SPEC §9.4, §15); authored body text under a check
    marker is reserved for the gate that fills the slot (Phase 6.2).
    """
    slug, label = spec
    icon = '<span class="callout-icon">%s</span>' % _CALLOUT_ICON
    if slug == "check":
        inner = "<p>%s</p>" % html.escape(
            "This check is available when you are reading with a session.")
    else:
        inner = _inline(body)
    return ('<section class="callout callout-%s"><p class="callout-label">'
            "%s%s</p><div class=\"callout-body\">%s</div></section>"
            % (slug, icon, html.escape(label), inner))


def _code_block(info, content):
    """The one markup shape Phase 9 attaches to (D-08): a preformatted
    element wrapping a code element whose class names the info string.
    The class is sanitised with the same restricted character set
    `lesson_slug` uses, so a hostile info string cannot close the class
    attribute or introduce a second one (T-3-10); the content is the
    block's source, HTML-escaped and otherwise untouched -- no re-indent,
    no syntax highlighting. A visible label in the muted foreground names
    the language; there is no KaTeX, no run button and no copy button --
    this plan cuts the seam and leaves it inert.
    """
    lang = lesson_slug(info)
    esc = html.escape(content)
    code = ('<code class="language-%s">%s</code>' % (lang, esc)
            if lang else "<code>%s</code>" % esc)
    label = '<span class="lang">%s</span>' % html.escape(lang) if lang else ""
    return '<div class="scroll">%s<pre>%s</pre></div>' % (label, code)


def _protect_code(text):
    """Lift every fenced block out of a section's text before any inline
    pass, replacing each with an opaque placeholder line that no inline
    pattern can match. Returns `(protected_text, tokens)` with the rendered
    code fragments in order.

    This ordering is the whole design: a single interleaved pass would let
    an emphasis or link pattern reach inside a fenced block and silently
    mangle exactly the content Phase 9 depends on being verbatim, and the
    damage would be invisible until someone read the rendered code closely.
    An unterminated fence treats the rest of the section as the block's
    content -- the forgiving reading that keeps the document readable
    (T-3-04).
    """
    lines = text.split("\n")
    out, tokens = [], []
    i = 0
    while i < len(lines):
        m = _FENCE_RE.match(lines[i])
        if m:
            fence = m.group(1)
            info = m.group(2).strip()
            closer = re.compile(r"^`{%d,}\s*$" % len(fence))
            j = i + 1
            body = []
            while j < len(lines) and not closer.match(lines[j]):
                body.append(lines[j])
                j += 1
            if j < len(lines):
                j += 1  # skip the closing fence line
            tokens.append(_code_block(info, "\n".join(body)))
            out.append("\x00K%d\x00" % (len(tokens) - 1))
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out), tokens


def _split_cells(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip() for c in row.split("|")]


def _is_separator_row(row):
    return all(re.match(r"^:?-+:?$", c) for c in _split_cells(row))


def _table_html(rows):
    """A pipe run whose second line is a separator row of dashes becomes a
    table with the first line as the header; anything that does not fit
    that shape -- a lone pipe line, a missing separator, a row with a
    different cell count -- returns None so the caller falls back to a
    paragraph rather than raising or emitting a broken table (T-3-04).
    Alignment markers are not implemented; D-08 declines that edge case.
    """
    if len(rows) < 2 or not _is_separator_row(rows[1]):
        return None
    header = _split_cells(rows[0])
    body = [_split_cells(r) for r in rows[2:]]
    if any(len(r) != len(header) for r in body):
        return None
    head = "".join("<th>%s</th>" % _inline(c) for c in header)
    rows_html = "".join(
        "<tr>%s</tr>" % "".join("<td>%s</td>" % _inline(c) for c in r)
        for r in body)
    return ('<div class="scroll"><table><thead><tr>%s</tr></thead>'
            "<tbody>%s</tbody></table></div>" % (head, rows_html))


_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_STRONG_RE = re.compile(r"(?<!\w)\*\*(.+?)\*\*(?!\w)", re.S)
_EM_RE = re.compile(r"(?<!\w)_([^_]+)_(?!\w)", re.S)
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _link_target_ok(target):
    """Only a plain relative path or an http/https URL becomes an anchor;
    every other target renders as plain text, so a scheme-bearing target in
    lesson prose cannot become a clickable action (T-3-11)."""
    t = target.strip()
    if t.startswith(("http://", "https://")):
        return True
    head = re.split(r"[/#]", t, 1)[0]
    return ":" not in head


def _linkify(text):
    def _rep(m):
        label, target = m.group(1), m.group(2).strip()
        if not _link_target_ok(target):
            return m.group(0)
        return '<a href="%s">%s</a>' % (target, label)
    return _LINK_RE.sub(_rep, text)


def _inline(text):
    """The inline pass for one literal text run, ordered so escaping cannot
    be undone: lift backtick code spans to placeholders first (so they are
    never re-scanned), escape the remaining text, apply emphasis and link
    patterns to the escaped text, then substitute the code spans back in
    escaped. Escaping before the patterns run is what keeps a
    markup-shaped stem or heading from reaching the page as markup
    (T-3-01); markers must sit at a word boundary so an underscore inside
    an identifier does not split it. Unmatched markers stay literal rather
    than raising (T-3-04).
    """
    spans = []

    def _lift(m):
        spans.append(m.group(1))
        return "\x00I%d\x00" % (len(spans) - 1)

    text = _INLINE_CODE_RE.sub(_lift, text)
    text = html.escape(text)
    text = _STRONG_RE.sub(r"<strong>\1</strong>", text)
    text = _EM_RE.sub(r"<em>\1</em>", text)
    text = _linkify(text)
    for idx, span in enumerate(spans):
        text = text.replace("\x00I%d\x00" % idx,
                            "<code>%s</code>" % html.escape(span))
    return text


def _render_blocks(text):
    """The D-08 block classifier for one section: fenced placeholders,
    deeper heading levels, one level of list, pipe tables, then
    paragraphs. Structure is resolved first and every literal text run is
    escaped second -- never the raw source wholesale, which would also
    escape the markup the renderer itself emits.
    """
    protected, tokens = _protect_code(text)
    out = []
    lines = protected.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        tm = _TOKEN_RE.match(line)
        if tm:
            out.append(tokens[int(tm.group(1))])
            i += 1
            continue
        cm = _CALLOUT_MARK_RE.match(line)
        if cm and _callout_spec(cm.group(1)) is not None:
            # The one callout branch (D-18): a `> [!KIND]` marker starts a
            # run whose body is every following `>`-prefixed line, closed at
            # the first non-`>` line. Only locked kinds enter here; an
            # unknown kind falls through to the paragraph path unchanged.
            spec = _callout_spec(cm.group(1))
            body = [cm.group(2)] if cm.group(2) else []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                body.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            out.append(_callout_html(spec, "\n".join(body)))
            continue
        hm = re.match(r"^#{4,}\s+(.+?)\s*$", line)
        if hm:
            # The grammar defines exactly two heading levels; any deeper
            # heading renders at the same Display size, with no third size.
            out.append("<h2>%s</h2>" % _inline(hm.group(1)))
            i += 1
            continue
        if re.match(r"^-\s+", line):
            items = []
            while i < len(lines) and re.match(r"^-\s+", lines[i]):
                items.append(_inline(re.sub(r"^-\s+", "", lines[i])))
                i += 1
            out.append("<ul>%s</ul>"
                       % "".join("<li>%s</li>" % it for it in items))
            continue
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(_inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>%s</ol>"
                       % "".join("<li>%s</li>" % it for it in items))
            continue
        if "|" in line:
            j = i
            rows = []
            while j < len(lines) and "|" in lines[j]:
                rows.append(lines[j])
                j += 1
            table = _table_html(rows)
            if table is not None:
                out.append(table)
                i = j
                continue
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip():
            nxt = lines[i]
            if (re.match(r"^#{4,}\s", nxt) or re.match(r"^-\s+", nxt)
                    or re.match(r"^\d+\.\s+", nxt) or _TOKEN_RE.match(nxt)
                    or "|" in nxt
                    or (_CALLOUT_MARK_RE.match(nxt)
                        and _callout_spec(
                            _CALLOUT_MARK_RE.match(nxt).group(1))
                        is not None)):
                break
            buf.append(nxt)
            i += 1
        out.append("<p>%s</p>" % _inline("\n".join(buf)))
    return "\n".join(out)


def render_markdown(text):
    """A deliberately small stdlib block renderer for lesson prose, covering
    exactly D-08's declared scope: headings, paragraphs, lists, tables,
    inline code, fenced code, bold/italic and links -- nothing else, and no
    attempt at CommonMark completeness. Every literal text run goes through
    `html.escape` after block structure is resolved and before interpolation,
    matching the discipline `quiz_page.py` and `daemon.py` already apply to
    bank content -- a stray angle bracket in lesson prose must not break the
    page. Fenced blocks are extracted to placeholders before the inline pass
    so code content is never re-scanned.
    """
    out = []
    for block in re.split(r"(?m)(?=^###\s)", text):
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        m = re.match(r"^###\s+(.+?)\s*$", lines[0])
        if m:
            heading = m.group(1).strip()
            prose = _render_blocks("\n".join(lines[1:]))
            out.append('<section id="%s"><h2>%s</h2>%s</section>'
                       % (lesson_slug(heading), html.escape(heading), prose))
        else:
            out.append(_render_blocks(block))
    return "\n".join(out)


def backlinks(qs, slug):
    """Every question whose stored slug equals `slug`, in bank order.

    Returns the data the row needs -- the question dicts themselves -- not
    HTML; the renderer owns the row markup.
    """
    return [q for q in qs if q.get("lesson_slug") == slug]


def _backlinks_html(stem, qs, slug):
    refs = backlinks(qs, slug)
    if not refs:
        return '<div class="bl orphan">%s</div>' % html.escape(ORPHAN_COPY)
    rows = "".join(
        '<a href="/quiz/%s#%s">Q%d: %s</a>' %
        (stem, q["id"], q["number"], html.escape(_truncate(q["stem"], 100)))
        for q in refs)
    return '<div class="bl"><span class="blabel">%s</span>%s</div>' % (
        html.escape(BACKLINKS_LABEL), rows)


def lesson_page(bank_path, qs, lesson, ref=None):
    """The one render both surfaces call: the daemon route and `cmd_lesson`
    write the same document because there is only one `lesson_page`.

    A non-empty `ref` narrows the document to the single heading whose slug
    matches the caller's text (D-11): the heading is resolved through
    `model.lesson_slug()` -- the same value the item tag and the HTML anchor
    use -- never by raw string comparison, so a caller may type the heading
    with different casing, spacing or punctuation and still reach it. The
    filtered page keeps the full page's chrome, title and byline; only the
    body sections differ. When `ref` names no heading -- including on a bank
    with no lesson section at all -- the function returns None and leaves
    the hard stop to `cmd_lesson`, so the route, the CLI and a test can call
    it without inheriting a process-exit path (T-3-12).

    A bank with no lesson section, or one whose section holds zero headings,
    renders the shared `No lesson yet` empty state -- never a crash and never
    an empty card under a title. A lesson result carrying a non-empty error
    key (an unreadable or out-of-tree `[LESSON-SRC:]`) renders that same
    empty-state layout plus one `var(--warn)` note naming the offending
    source path in a wrapping code element: the degraded state, in the
    warning tone rather than the error tone, and never an exception
    (T-3-04). The only interpolated value in that note is the
    bank-author-written directive path, HTML-escaped like every other text
    run (T-3-07); the reason detail stays with `itembank lint`, because the
    reader is not a diagnostic surface.
    """
    bank_text = open(bank_path, encoding="utf-8").read()
    title = (grab(r"(?m)^#\s+(.*?)\s*$", bank_text)
             or os.path.basename(bank_path))
    warn_css = ""
    want = lesson_slug(ref) if ref else ""
    if lesson is None or not lesson.get("headings"):
        # An explicit --ref in a bank with no headings is the same miss as a
        # ref that matches nothing: the caller asked for a section that is
        # not there, and an empty-state page would silently lie about it.
        if want:
            return None
        body = '<div class="empty"><h2>%s</h2><p>%s</p></div>' % (
            html.escape(EMPTY_HEADING), html.escape(EMPTY_BODY))
        if lesson is not None and lesson.get("error"):
            src = grab(r"(?m)^\[LESSON-SRC:\s*(.*?)\s*\]", bank_text)
            warn_css = WARN_CSS
            body += ('<p class="warn">%s <code>%s</code></p>' % (
                html.escape(WARN_SENTENCE % os.path.basename(bank_path)),
                html.escape(src)))
    else:
        stem = os.path.splitext(os.path.basename(bank_path))[0]
        if want:
            head_idx = next((i for i, h in enumerate(lesson["headings"])
                             if h["slug"] == want), None)
            if head_idx is None:
                return None
            idxs = (head_idx,)
        else:
            idxs = range(len(lesson["headings"]))
        # One section per heading, rendered from the heading's own text and
        # body -- the exact block `render_markdown` isolates when it renders
        # the whole lesson, so a filtered page is byte-for-byte the full
        # page narrowed. Each heading's backlinks sit directly under its own
        # prose (the Copywriting Contract), which a re-split of the whole
        # render's `</section>` boundaries cannot guarantee once a `--ref`
        # scope drops other headings.
        body = "\n".join(
            render_markdown("### %s\n\n%s" % (h["text"], h["body"]))
            + _backlinks_html(stem, qs, h["slug"])
            for idx in idxs for h in (lesson["headings"][idx],))
    return (LESSON_TEMPLATE
            .replace("__THEME__", THEME_CSS)
            .replace("__SHARED_CSS__", SHARED_CSS)
            .replace("__LESSON_CSS__", LESSON_CSS)
            .replace("__WARN_CSS__", warn_css)
            .replace("__TITLE__", html.escape(title) + " lesson")
            .replace("__SUB__", SUB_BYLINE)
            .replace("__BODY__", body))


def cmd_lesson(a):
    """The lesson CLI's observable contract: render the same document the
    daemon route serves, write it to `--out` (or beside the bank, like
    `cmd_study`), and report on stdout exactly how many sections were
    actually rendered -- one status line, never the document and never a
    progress line. The one hard stop is an explicitly requested `--ref`
    heading that does not exist (T-3-12); a bank with no lesson section, or
    with an unreadable external source, writes its page and exits 0.
    """
    qs = load(a.bank)
    lesson = parse_lesson(a.bank)
    out = a.out or os.path.splitext(a.bank)[0] + "_lesson.html"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    page = lesson_page(a.bank, qs, lesson, ref=a.ref)
    if page is None:
        sys.exit("no lesson heading matching %r in %s" % (a.ref, a.bank))
    open(out, "w", encoding="utf-8").write(page)
    if a.ref:
        count = 1
    elif lesson and lesson.get("headings"):
        count = len(lesson["headings"])
    else:
        count = 0
    print("%d lesson section(s) -> %s" % (count, out))
    return 0
