"""Flashcards and a session-only Learn loop over the same bank.

Plan 04-05 makes this the complete deliberate-review surface (D-12 through
D-14). `study_item` composes the runtime's canonical public item with its
full reveal explanation under one `explain` member -- there is no field
allowlist here, so nothing the runtime returns is silently discarded. The
page renders every explanation field through labelled semantic sections
after the learner deliberately flips the card, and the surface never calls
`runtime.score_response` or submits anything: Flash/Learn, Got it/Missed and
local recall state are presentation and queue behavior only, while quiz
alone is response-driven.
"""
import resources
import html, os, sys

from model import grab, lint, load
from runtime import explain_payload, public_item
from surfaces import presentation, settings
from surfaces.theme import theme_css


def study_item(q):
    """The complete deliberate-review view for one card: the canonical
    public item a learner may see before answering plus the full reveal
    explanation. Composed from the runtime's two payload builders, so a new
    field the runtime returns reaches the learner here by construction and
    no hand-copied projection can drift (D-12, SURF-06).
    """
    view = public_item(q)
    view["explain"] = explain_payload(q, reveal=True)
    return view


esc = presentation.esc
script_safe_json = presentation.script_safe_json


# Card-component rules only; the document shell, base typography, focus
# rings, breakpoint, and reduced-motion kill come from presentation.SHARED_CSS
# and the generated theme block. No color literals anywhere -- every token is
# a semantic custom property, so the custom accent can never mean
# correct/incorrect (T-04-20, T-04-26).
STUDY_CSS = resources.read_text("surfaces/assets/study/study.css")


def _rationale_list(view):
    """Every choice option rendered once, each with its rationale in an
    adjacent native disclosure. The correct option's rationale opens by
    default; every other rationale stays closed but keyboard-reachable, and
    the client opens the learner's locally selected choice on reveal (D-13).
    Labels are text plus semantic tokens -- the custom accent never means
    correct/incorrect (T-04-20, T-04-26).
    """
    ex = view["explain"]
    da = ex.get("da") or {}
    correct = set(ex.get("correct") or [])
    rows = []
    for opt in view.get("options") or []:
        key = opt["key"]
        line = da.get(key, "")
        is_correct = key in correct
        open_attr = " open" if (line and is_correct) else ""
        summary = "%s) %s" % (esc(key), esc(opt["text"]))
        if line:
            badge = ('<span class="badge ok">Correct</span> ' if is_correct
                     else "")
            rows.append('<li><details class="rationale" data-opt="%s" '
                        'data-correct="%d"%s><summary>%s</summary><p>%s%s'
                        "</p></details></li>"
                        % (esc(key), 1 if is_correct else 0, open_attr,
                           summary, badge, esc(line)))
        else:
            rows.append('<li class="no-rationale">%s</li>' % summary)
    return '<ul class="options">%s</ul>' % "".join(rows)


def _explain_sections(view):
    """The full deliberate-review explanation as labelled semantic sections:
    answer and concise why first, every option with its rationale, then the
    labelled Second-best answer / Discriminator / Common trap / Notes
    disclosures, plus each type's canonical non-choice content. Empty
    optional fields are omitted, never fabricated.
    """
    ex = view["explain"]
    t = view["type"]
    h = ['<section class="explain" data-explain>']
    h.append("<h3>Answer</h3>")
    h.append('<div class="answer-text">%s</div>'
             % esc(ex.get("answer_text", "")))
    if ex.get("educational_objective") or ex.get("objective"):
        h.append(presentation.details_section(
            "Educational objective",
            "<p>%s</p>%s" % (
                esc(ex.get("educational_objective") or ""),
                ('<p class="sub">%s</p>' % esc(ex["objective"]))
                if ex.get("objective") else ""),
            data={"objective": ""}))
    if t in ("mc", "multi"):
        if ex.get("why"):
            h.append('<h3>Why this is best</h3><div class="why">%s</div>'
                     % esc(ex["why"]))
        h.append(_rationale_list(view))
    elif t == "short":
        if ex.get("model"):
            h.append('<h3>Model answer</h3><div class="model">%s</div>'
                     % esc(ex["model"]))
        if ex.get("rubric"):
            h.append('<h3>What a marker checks</h3><ul class="rubric">%s</ul>'
                     % "".join("<li>%s</li>" % esc(r) for r in ex["rubric"]))
        if ex.get("why"):
            h.append('<h3>Why this is best</h3><div class="why">%s</div>'
                     % esc(ex["why"]))
    else:
        if ex.get("why"):
            h.append('<h3>Why this is best</h3><div class="why">%s</div>'
                     % esc(ex["why"]))
        if t in ("table", "dnd") and ex.get("row_cats"):
            h.append('<h3>Category map</h3><ul class="rows">')
            for r in view.get("rows") or []:
                cat = ex["row_cats"].get(str(r["id"]), "")
                h.append("<li>%s &rarr; %s</li>"
                         % (esc(r["text"]), esc(cat)))
            h.append("</ul>")
        elif t == "build" and ex.get("steps"):
            h.append('<h3>Correct order</h3><ol class="steps">%s</ol>'
                     % "".join("<li>%s</li>" % esc(s) for s in ex["steps"]))
    for label, key in (("Second-best answer", "second"),
                       ("Discriminator", "disc"),
                       ("Common trap", "trap")):
        if ex.get(key):
            h.append(presentation.details_section(
                label, "<p>%s</p>" % esc(ex[key]),
                data={key: ""}))
    if ex.get("notes"):
        h.append(presentation.details_section(
            "Notes",
            "<ul>%s</ul>" % "".join("<li>%s</li>" % esc(n)
                                    for n in ex["notes"]),
            data={"notes": ""}))
    h.append("</section>")
    return "".join(h)


def _card_markup(view, index):
    """One server-rendered card: a focused stem with local-recall controls
    for choice items, a hidden progressive explanation section, and three
    native action groups (unrevealed / revealed / Learn-rating) each exposing
    exactly one primary next action. The stem and explanation are escaped
    text, never executable markup.
    """
    t = view["type"]
    # C7 (03.1-03): the syllabus reference and the Educational Objective
    # line are answer-adjacent, so no objective chip may appear on a
    # pre-answer card; both render only inside the revealed explanation.
    meta = ('<div class="meta"><span class="chip type">%s</span></div>'
            % esc(t))
    stem = '<h2 class="stem">%s</h2>' % esc(view["stem"])
    recall = ""
    if t in ("mc", "multi"):
        opts = "".join(
            '<button type="button" class="recall-opt" data-recall="%s" '
            'aria-pressed="false">%s) %s</button>'
            % (esc(o["key"]), esc(o["key"]), esc(o["text"]))
            for o in view.get("options") or [])
        recall = ('<div class="recall" data-recall-host>'
                  '<p class="recall-note">Your recall choice &mdash; not '
                  "graded.</p>"
                  '<div class="recall-opts">%s</div></div>' % opts)
    explain = '<section class="explain" data-explain hidden>%s</section>' \
        % _explain_sections(view)
    acts = (
        '<div class="acts" data-acts="front">'
        '<button type="button" class="b" data-action-primary data-reveal>'
        "Reveal explanation</button>"
        '<button type="button" class="b" data-action-secondary data-prev>'
        "Previous</button>"
        '<button type="button" class="b" data-action-secondary data-next>'
        "Next</button></div>"
        '<div class="acts" data-acts="revealed" hidden>'
        '<button type="button" class="b" data-action-primary data-next>'
        "Next</button>"
        '<button type="button" class="b" data-action-secondary data-prev>'
        "Previous</button></div>"
        '<div class="acts" data-acts="rating" hidden>'
        '<button type="button" class="b" data-action-primary data-got>'
        "Got it</button>"
        '<button type="button" class="b" data-action-secondary data-miss>'
        "Missed</button>"
        '<button type="button" class="b" data-action-secondary data-prev>'
        "Previous</button>"
        '<button type="button" class="b" data-action-secondary data-next>'
        "Next</button></div>")
    return ('<article class="card" data-card="%d" hidden>%s%s%s%s%s</article>'
            % (index, meta, stem, recall, explain, acts))


STUDY_JS = resources.read_text("surfaces/assets/study/study.js")


def study_page(bank_path, qs):
    """One deliberate-review page for a bank. Loads the validated local
    settings beside the bank and renders through the shared presentation
    shell with the single generated palette (schema defaults when no settings
    file exists), the exact empty copy in the shared state panel, and a safe
    render-error state that keeps bank context and a recovery action instead
    of a blank page.
    """
    base = os.path.dirname(os.path.abspath(bank_path)) or "."
    cfg = settings.load_settings(base)
    css = theme_css(cfg)
    profile, _notice = settings.resolve_presentation_profile(cfg)
    with open(bank_path, encoding="utf-8") as source_handle:
        text = source_handle.read()
    title = grab(r"(?m)^#\s+(.*?)\s*$", text) or os.path.basename(bank_path)
    page_title = "%s study set" % title
    back = {"href": "/", "label": "itembank"}
    noscript = ("Flashcards need JavaScript for flipping, navigation and "
                "the Learn loop; the complete explanation data is embedded "
                "on this page.")
    if not qs:
        body = presentation.state_panel({
            "kind": "empty",
            "status": "No study cards match this bank.",
            "actions": [{"label": "Choose another bank", "href": "/"}]})
        return presentation.surface_shell(
            page_title, body, theme_css=css, back=back, noscript=noscript,
            presentation_profile=profile)
    cards = []
    for n, q in enumerate(qs):
        try:
            cards.append(_card_markup(study_item(q), n))
        except Exception:
            body = presentation.state_panel({
                "kind": "bad",
                "status": ("This card could not be shown. Move to the next "
                           "card or reload."),
                "actions": [{"label": "Reload", "href": "#"},
                            {"label": "Choose another bank", "href": "/"}]})
            return presentation.surface_shell(
                page_title, body, theme_css=css, back=back, noscript=noscript,
                presentation_profile=profile)
    body = (
        '<section class="ib-course-identity" aria-label="Course context">'
        '<p>Application: itembank</p><h2>%s</h2><p>Study</p></section>'
        '<section class="ib-activity-frame" aria-label="Learner study">'
        '<details class="ib-activity-details"><summary>Study details</summary>'
        '<dl class="ib-activity-facts"><div><dt>Purpose</dt>'
        '<dd>Deliberate review</dd></div><div><dt>Response format</dt>'
        '<dd>Recall and reveal</dd></div><div><dt>Disclosure</dt>'
        '<dd>Explanation after you choose to reveal it</dd></div>'
        '<div><dt>Recall rating</dt><dd>Local to this page, not graded or '
        'saved as evidence</dd></div></dl></details>'
        '<div class="tabs">'
        '<button type="button" class="tab on" id="tFlash">Flashcards</button>'
        '<button type="button" class="tab" id="tLearn">Learn</button></div>'
        '<div class="status" id="status" role="status" aria-live="polite">'
        "</div>"
        '<div class="bar"><i id="prog"></i></div>'
        '<div id="deck">%s</div></section>'
        % (esc(title), "".join(cards)))
    page = presentation.surface_shell(
        page_title, body, theme_css=css + "\n" + STUDY_CSS,
        back=back, noscript=noscript, presentation_profile=profile)
    return (page.replace("</main>",
                         "<script>" + STUDY_JS.replace(
                             "__DATA__", script_safe_json(
                                 [study_item(q) for q in qs])) +
                         "</script></main>"))


def cmd_study(a):
    qs = load(a.bank)
    errors, _ = lint(qs)
    if errors and not a.force:
        sys.exit("refusing to study a bank with errors; fix them or pass --force")
    out = a.out or os.path.splitext(a.bank)[0] + "_study.html"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    page = study_page(a.bank, qs)
    with open(out, "w", encoding="utf-8") as source_handle:
        source_handle.write(page)
    print("%d items -> %s" % (len(qs), out))
    return 0
