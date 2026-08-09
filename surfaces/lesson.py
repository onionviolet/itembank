"""The lesson reader: a bank's teaching text rendered as a document, linked
both ways to the items that test it.

This is a read-only render of author-provided prose. It holds no answer key
and reaches no verdict, and its links navigate rather than answer (D-10): the
only way out of a lesson is to another surface, never to a score.
"""
import html, os, re, sys

from model import grab, lesson_slug, load, parse_lesson
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


LESSON_TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>
__THEME__
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:800px;margin:0 auto;padding:22px 18px 96px}
header{margin-bottom:18px}
h1{font-size:21px;margin:0 0 4px;letter-spacing:-.01em}
.sub{color:var(--mut);font-size:13.5px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:18px 18px 16px}
section{margin-bottom:18px}
h2{font-size:19px;margin:0 0 8px;line-height:1.3}
p{margin:0 0 10px}
.bl{margin-top:12px;padding-top:10px;border-top:1px solid var(--line)}
.blabel{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--mut);margin-bottom:6px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.bl a{display:block;color:var(--accent);text-decoration:none;margin:4px 0}
.bl a:hover,.bl a:focus-visible{text-decoration:underline;
  outline:2px solid var(--accent);outline-offset:2px}
.scroll{overflow-x:auto;margin:0 0 10px}
pre{margin:0;background:var(--chip);border-radius:8px;padding:10px 12px}
pre code{display:block;font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  font-size:13.5px;line-height:1.5;color:var(--ink)}
.lang{display:block;font-size:11px;letter-spacing:.05em;color:var(--mut);
  margin-bottom:6px;font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
table{border-collapse:collapse;margin:0 0 10px;min-width:100%}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;font-size:14.5px}
th{background:var(--chip);color:var(--mut);font-weight:700}
.orphan{color:var(--mut);font-size:14px}
.empty{text-align:center;padding:36px 10px}
.empty h2{font-size:19px;margin:0 0 8px}
.empty p{color:var(--mut);max-width:520px;margin:0 auto}
__WARN_CSS__
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
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


def _inline(text):
    """Escape one literal text run after block structure is resolved.
    Plan 03-04 Task 2 widens this to emphasis, inline code and links,
    always on placeholder-protected, already-escaped text.
    """
    return html.escape(text)


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
                    or "|" in nxt):
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

    `ref` is accepted and ignored in this plan; plan 03-05 gives it meaning.
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
    if lesson is None or not lesson.get("headings"):
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
        rendered = render_markdown(lesson["body"])
        # render_markdown emits one <section>...</section> per heading, in
        # document order; re-split so each heading's backlinks sit under its
        # own prose, exactly where the Copywriting Contract puts them.
        parts = rendered.split("</section>")
        body_parts = [parts[0]]
        for idx, h in enumerate(lesson["headings"]):
            section_html = parts[idx + 1] if idx + 1 < len(parts) else ""
            section_html += _backlinks_html(stem, qs, h["slug"])
            section_html += "</section>"
            body_parts.append(section_html)
        body = "\n".join(body_parts)
    return (LESSON_TEMPLATE
            .replace("__THEME__", THEME_CSS)
            .replace("__WARN_CSS__", warn_css)
            .replace("__TITLE__", html.escape(title) + " lesson")
            .replace("__SUB__", SUB_BYLINE)
            .replace("__BODY__", body))


def cmd_lesson(a):
    qs = load(a.bank)
    lesson = parse_lesson(a.bank)
    out = a.out or os.path.splitext(a.bank)[0] + "_lesson.html"
    if os.path.dirname(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    page = lesson_page(a.bank, qs, lesson)
    open(out, "w", encoding="utf-8").write(page)
    count = len(lesson["headings"]) if lesson else 0
    print("%d lesson section(s) -> %s" % (count, out))
    return 0
