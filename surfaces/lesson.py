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


def _paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit] + "\u2026"


def render_markdown(text):
    """A deliberately small stdlib block renderer for lesson prose.

    In this plan it handles exactly two block kinds: a `###` heading line and
    a blank-line-separated paragraph. Every literal text run goes through
    `html.escape` after block structure is resolved and before interpolation,
    matching the discipline `quiz_page.py` and `daemon.py` already apply to
    bank content -- a stray angle bracket in lesson prose must not break the
    page. The function is structured as a block classifier with escaping done
    second, so plan 03-04 can add list, table, fenced-code and inline handling
    by extending the classifier rather than rewriting the function.
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
            prose = "".join("<p>%s</p>" % html.escape(p)
                            for p in _paragraphs("\n".join(lines[1:])))
            out.append('<section id="%s"><h2>%s</h2>%s</section>'
                       % (lesson_slug(heading), html.escape(heading), prose))
        else:
            out.extend("<p>%s</p>" % html.escape(p) for p in _paragraphs(block))
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
