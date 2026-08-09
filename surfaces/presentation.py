"""The shared semantic-HTML presentation seam (plan 04-04 Task 2).

Every surface that renders reads from one visual system: the palette comes
from `surfaces.theme.theme_css()`, and the *structure* comes from the small
escaped native-element primitives in this module -- `surface_shell`,
`context_line`, `teaching_step`, `state_panel`, and `details_section` --
plus `render_surface(view, adapter=None)`, the replaceable view-to-HTML
seam. Nothing here owns scoring, persistence, routing, scheduling,
evidence, or lesson parsing; view dictionaries carry presentation-ready
labels, content, state, and actions only, never scorers, keys, session
file paths, evidence writers, or mutation callbacks (D-04's "surfaces are
thin clients" rule extended to the markup itself).

The design tokens below implement 04-UI-SPEC's shared shell: the 8-point
spacing scale (4/8/16/24/32/48/64), exactly four font sizes (14/16/20/28)
at two weights (400/600), 720px content / 800px shell measures, 44px
interactive targets, a 2px focus ring with 2px offset, a 768px breakpoint,
320px overflow protection, a 150ms motion cap, and the reduced-motion kill
rule. A future graphical/canvas presentation may only attach behind
`render_surface`'s adapter seam while equivalent semantic HTML remains
present and operable; Phase 4 implements no canvas or media design.
"""
import html, json


# Shared spacing/typography/measure/accessibility CSS. Token *names* come
# from the generated theme block a caller substitutes; this file introduces
# no color literals and no second palette (D-04). No `nowrap` and no
# `text-overflow` anywhere: meaningful text wraps rather than truncating.
SHARED_CSS = r"""
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.surface{max-width:720px;margin:0 auto;padding:24px 16px 64px;min-width:0}
.surface.wide{max-width:800px}
h1{font-size:28px;font-weight:600;line-height:1.2;margin:0 0 8px}
h2{font-size:20px;font-weight:600;line-height:1.2;margin:32px 0 16px}
h3{font-size:16px;font-weight:600;line-height:1.4;margin:24px 0 8px}
p{font-size:16px;line-height:1.5;margin:0 0 16px;overflow-wrap:anywhere}
a{color:var(--accent);text-decoration:none;font-weight:600}
a:hover,a:focus-visible,button:focus-visible,summary:focus-visible,
input:focus-visible,textarea:focus-visible,select:focus-visible{
  outline:2px solid var(--accent);outline-offset:2px}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-variant-numeric:tabular-nums}
.back{margin:0 0 24px;color:var(--mut);font-size:14px}
.context-line{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;
  gap:4px 18px;align-items:center;background:var(--bg);padding:8px 0 10px;
  border-bottom:1px solid var(--line);margin-bottom:14px;font-size:14px;
  color:var(--mut)}
.context-line .cx{overflow-wrap:anywhere}
.card,.step,.state,.empty{background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:16px;margin:0 0 16px}
.step .step-label{font-size:20px;font-weight:600;margin:0 0 8px}
.step .step-prompt{font-size:16px;font-weight:600;margin:0 0 12px}
.step-body{font-size:16px;line-height:1.5;overflow-wrap:anywhere}
.step-status{min-height:24px;font-size:14px;color:var(--mut);
  margin:12px 0 0}
.step details{margin:12px 0 0;border-top:1px solid var(--line);
  padding-top:8px}
.step details summary{cursor:pointer;font-size:14px;font-weight:600}
details.details-section{border:1px solid var(--line);border-radius:8px;
  padding:8px 12px;margin:12px 0 16px;background:var(--card)}
details.details-section summary{cursor:pointer;font-size:14px;
  font-weight:600;padding:4px 0}
.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px}
button.go,a.go{display:inline-flex;align-items:center;justify-content:center;
  min-height:44px;font:inherit;font-size:16px;font-weight:600;
  padding:10px 16px;border-radius:8px;border:1px solid var(--line);
  background:var(--card);color:inherit;cursor:pointer;text-decoration:none;
  transition:.12s}
button.go.primary,a.go.primary{background:var(--accent-soft);
  border-color:var(--accent);color:var(--accent)}
button.go:disabled{opacity:.55;cursor:default}
.state{padding:12px 16px;font-size:14px;color:var(--mut)}
.state .state-text{margin:0}
.state.state-ok{color:var(--ok);background:var(--ok-bg);border-color:var(--ok)}
.state.state-bad{color:var(--bad);background:var(--bad-bg);border-color:var(--bad)}
.state.state-warn{color:var(--warn);border-color:var(--warn)}
.row{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:16px;margin:0 0 16px}
.row .name{font-size:16px;font-weight:600;overflow-wrap:anywhere}
.row .links{display:flex;gap:16px;flex-wrap:wrap;margin-top:8px;font-size:14px}
.row a{color:var(--accent)}
.empty h2{font-size:20px;font-weight:600;margin:0 0 16px}
.empty p{color:var(--mut);font-size:16px}
.headline{font-size:28px;font-weight:600;color:var(--accent);line-height:1.1}
.headline-label{font-size:14px;color:var(--mut);margin:4px 0 0}
.figures{display:flex;gap:32px;flex-wrap:wrap;margin-top:24px}
.figure-value{font-size:20px;font-weight:600;font-variant-numeric:tabular-nums}
.figure-label{font-size:14px;color:var(--mut);margin-top:4px}
.status{font-size:14px;color:var(--mut);margin:16px 0 0}
table{width:100%;border-collapse:collapse;margin:8px 0 16px}
th,td{text-align:left;padding:8px;border-bottom:1px solid var(--line);
  font-size:16px;overflow-wrap:anywhere;vertical-align:top}
th{font-size:14px;color:var(--mut);font-weight:600}
.table-wrap{overflow-x:auto;min-width:0}
code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  overflow-wrap:anywhere}
pre{background:var(--chip);border:1px solid var(--line);border-radius:8px;
  padding:12px;overflow-x:auto;max-width:100%}
@media (max-width:767px){
  .surface{padding:16px 16px 56px}
  h1{font-size:20px}
  .actions button{width:100%}
}
@media (prefers-reduced-motion:reduce){
  *{transition:none!important}
  html{scroll-behavior:auto!important}
}
"""


def esc(value):
    """Escape one presentation value for HTML text."""
    return html.escape("" if value is None else str(value))


def script_safe_json(value):
    """JSON that cannot close a page's `<script>` data element (T-04-17):
    escape `<`, `>`, `&` and the JS line separators U+2028/U+2029 so bank
    prose can never terminate the script element or splice executable
    markup. Every surface that embeds boot/item payloads into a `<script>`
    data element routes them through this one helper (study, quiz, day);
    rendered text is escaped again by each surface's own HTML escaper, and
    this only guarantees the embedded data element itself stays inert.
    """
    return (json.dumps(value, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def _action_markup(action, primary=False):
    """One native action from a behavior-free dict: `{"label"}` renders a
    button, `{"label", "href"}` a link. Exactly one element per teaching
    step may carry `data-action-primary`; every other action is
    `data-action-secondary` and can never acquire the primary marker.
    """
    label = action.get("label", "")
    marker = "data-action-primary" if primary else "data-action-secondary"
    cls = "go primary" if primary else "go"
    href = action.get("href")
    if href:
        return '<a class="%s" %s href="%s">%s</a>' % (
            esc(cls), marker, esc(href), esc(label))
    return '<button type="button" class="%s" %s>%s</button>' % (
        esc(cls), marker, esc(label))


def surface_shell(title, body, theme_css="", back=None, wide=False,
                  context=None, noscript=None):
    """The one shared semantic document shell: doctype, generated theme
    block plus shared design-token CSS, an optional sticky context line,
    an optional back link, a single `h1`, a `main` landmark holding `body`,
    and an optional `<noscript>` fallback note. `wide=True` uses the 800px
    quiz measure; the default is the 720px reading column.
    """
    parts = []
    if context:
        parts.append(context_line(context))
    if back:
        parts.append('<p class="back"><a href="%s">&larr; %s</a></p>'
                     % (esc(back.get("href", "/")),
                        esc(back.get("label", "back"))))
    parts.append("<h1>%s</h1>" % esc(title))
    ns = ""
    if noscript is not None:
        ns = "<noscript><p>%s</p></noscript>" % esc(noscript)
    style = "<style>\n%s\n%s\n</style>" % (theme_css, SHARED_CSS)
    cls = "surface" + (" wide" if wide else "")
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>%s</title>%s</head><body><div class=\"%s\">%s<main>%s"
            "</main>%s</div></body></html>"
            % (esc(title), style, esc(cls), "\n".join(parts), body, ns))


def context_line(parts, label="Context"):
    """One sticky, labelled semantic context region (a nav, not a heading),
    carrying the stable `data-surface-context` enhancement hook.
    """
    items = "".join('<span class="cx">%s</span>' % esc(p) for p in parts)
    return ('<nav class="context-line" data-surface-context aria-label="%s">%s'
            "</nav>" % (esc(label), items))


def details_section(summary, body="", data=None, classes=""):
    """One native disclosure whose summary names its content, with optional
    stable `data-*` hooks for integration tests.
    """
    attrs = "".join(' data-%s="%s"' % (esc(k), esc(v))
                    for k, v in (data or {}).items())
    cls = "details-section"
    if classes:
        cls += " " + classes
    return ('<details class="%s"%s><summary>%s</summary>%s</details>'
            % (esc(cls), attrs, esc(summary), body))


def state_panel(state):
    """One persistent polite status region (`role=status`) with optional
    recovery actions -- the shared loading/error/empty/unavailable surface.
    """
    kind = state.get("kind", "neutral")
    text = state.get("status", "")
    actions = "".join(_action_markup(a) for a in state.get("actions", ()))
    return ('<div class="state state-%s" data-state="%s" role="status" '
            'aria-live="polite"><p class="state-text">%s</p>%s</div>'
            % (esc(kind), esc(kind), esc(text), actions))


def teaching_step(label="", prompt="", body="", status="", action=None,
                  details=(), secondary=()):
    """One concise teaching step: a short label/prompt, body prose, a
    persistent immediate-status slot, optional progressive details, and
    exactly one primary next action with optional secondary actions. The
    adapter supplies presentation structure only -- it never decides the
    next step, sequences anything, or renders behavior.
    """
    h = ['<article class="step" data-presentation-step>']
    if label:
        # h2, not h3: the shell's single h1 is followed directly by the step
        # label, and the a11y contract forbids skipping heading levels.
        h.append('<h2 class="step-label">%s</h2>' % esc(label))
    if prompt:
        h.append('<p class="step-prompt">%s</p>' % esc(prompt))
    if body:
        h.append('<div class="step-body">%s</div>' % esc(body))
    if status:
        h.append('<div class="step-status" role="status" aria-live="polite">%s'
                 "</div>" % esc(status))
    for d in details or ():
        h.append(details_section(d.get("summary", ""), d.get("body", "")))
    acts = []
    if action:
        acts.append(_action_markup(action, primary=True))
    for a in secondary or ():
        acts.append(_action_markup(a))
    if acts:
        h.append('<div class="actions">%s</div>' % "".join(acts))
    h.append("</article>")
    return "".join(h)


def default_adapter(view):
    """The polished low-chrome default adapter: one behavior-free view
    dictionary to semantic HTML. Reads only presentation labels, content,
    state, and actions; an optional `theme_css` string in the view supplies
    the generated palette block (consumed by name, never authored here).
    """
    parts = []
    if view.get("context"):
        parts.append(context_line(view["context"]))
    step = view.get("step")
    if isinstance(step, dict):
        parts.append(teaching_step(**step))
    state = view.get("state")
    if isinstance(state, dict):
        parts.append(state_panel(state))
    return surface_shell(view.get("title", "itembank"), "\n".join(parts),
                         theme_css=view.get("theme_css", ""),
                         back=view.get("back"),
                         wide=bool(view.get("wide")),
                         noscript=view.get("noscript"))


def render_surface(view, adapter=None):
    """Render one behavior-free view dictionary to semantic HTML through
    `adapter` (the polished default when none is given). An alternate
    adapter receives the exact same view data and may produce any HTML, but
    it can never own scoring, persistence, routing, scheduling, or evidence
    decisions -- the view carries none of those objects by contract.
    """
    if adapter is None:
        adapter = default_adapter
    return adapter(view)
