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
import html, json, os, sys

from model import grab, lint, load
from runtime import explain_payload, public_item
from surfaces import presentation, settings
from surfaces.theme import theme_css


def script_safe_json(value):
    """JSON that cannot close the page's `<script>` data element (T-04-17):
    escape `<`, `>`, `&` and the JS line separators U+2028/U+2029 so bank
    prose can never terminate the script or splice executable markup.
    Rendered card text is escaped again through `presentation.esc`; this
    only guarantees the embedded data element itself stays inert.
    """
    return (json.dumps(value, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


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


# Card-component rules only; the document shell, base typography, focus
# rings, breakpoint, and reduced-motion kill come from presentation.SHARED_CSS
# and the generated theme block. No color literals anywhere -- every token is
# a semantic custom property, so the custom accent can never mean
# correct/incorrect (T-04-20, T-04-26).
STUDY_CSS = r"""
.tabs{display:flex;gap:8px;margin:0 0 14px}
.tab{flex:1;min-height:44px;padding:10px 9px;border:1px solid var(--line);
  border-radius:9px;background:var(--card);color:var(--ink);cursor:pointer;
  font:inherit;font-weight:600}
.tab.on{background:var(--accent-soft);border-color:var(--accent);
  color:var(--accent)}
.status{min-height:24px;font-size:14px;color:var(--mut);margin:0 0 10px}
.bar{height:6px;background:var(--line);border-radius:99px;overflow:hidden;
  margin:0 0 16px}
.bar>i{display:block;height:100%;background:var(--accent);width:0}
.flip{perspective:1200px;margin:0 0 16px}
.inner{position:relative;min-height:280px;transition:transform .15s;
  transform-style:preserve-3d;cursor:pointer}
.inner.flipped{transform:rotateY(180deg)}
.face{position:absolute;inset:0;backface-visibility:hidden;
  background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:24px;overflow-y:auto}
.back{transform:rotateY(180deg)}
.meta{font-size:12px;color:var(--mut);text-transform:uppercase;
  letter-spacing:.04em;margin:0 0 10px}
.chip{display:inline-block;background:var(--chip);color:var(--mut);
  padding:2px 8px;border-radius:5px;margin-right:6px;font-size:11px}
.chip.type{background:var(--accent-soft);color:var(--accent)}
.stem{font-size:20px;font-weight:600;margin:0 0 12px}
.hint{color:var(--mut);font-size:13px;margin:16px 0 0}
.explain h3{font-size:16px;font-weight:600;margin:18px 0 6px;
  text-transform:none;letter-spacing:0}
.explain h3:first-child{margin-top:0}
.answer-text{font-size:17px;font-weight:600;color:var(--ink)}
.why{font-size:15px;line-height:1.5;overflow-wrap:anywhere}
.options{list-style:none;padding:0;margin:0 0 8px}
.options li{margin:0 0 8px}
.rationale{border:1px solid var(--line);border-radius:8px;padding:8px 12px;
  background:var(--card)}
.rationale summary{cursor:pointer;font-weight:600;overflow-wrap:anywhere}
.rationale[open] summary{margin-bottom:6px}
.rationale p{margin:0;font-size:14px;line-height:1.5;
  overflow-wrap:anywhere}
.badge{display:inline-block;font-size:11px;font-weight:600;padding:1px 7px;
  border-radius:5px;border:1px solid currentColor;margin-left:8px;
  vertical-align:middle}
.badge.ok{color:var(--ok);background:var(--ok-bg)}
.model,.rows,.steps,.rubric{font-size:15px;line-height:1.5;
  overflow-wrap:anywhere}
.rows,.steps,.rubric{margin:0;padding-left:18px}
.rows li,.steps li,.rubric li{margin:0 0 4px}
.acts{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
button.b{border:1px solid var(--line);border-radius:9px;min-height:44px;
  padding:10px 20px;font:inherit;font-weight:600;cursor:pointer;
  background:var(--card);color:var(--ink)}
button.b:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
button.b:disabled{opacity:.55;cursor:default}
button.b.nav{background:var(--accent-soft);border-color:var(--accent);
  color:var(--accent)}
button.b.got{background:var(--ok-bg);border-color:var(--ok);color:var(--ok)}
button.b.miss{background:var(--bad-bg);border-color:var(--bad);color:var(--bad)}
.done{text-align:center;padding:40px 10px}
.done .big{font-size:40px;font-weight:800;color:var(--ok)}
@media (max-width:767px){
  .face{padding:18px 16px}
  .stem{font-size:18px}
  .acts button{width:100%}
}
"""


def _rationale_list(view):
    """Every choice option rendered once, each with its rationale in an
    adjacent native disclosure. Deliberate reveal shows the whole field set
    (all disclosures open in this plan task); the relevance/default-open
    refinement and the learner-selection rule land in plan 04-05 Task 2.
    """
    ex = view["explain"]
    da = ex.get("da") or {}
    correct = set(ex.get("correct") or [])
    rows = []
    for opt in view.get("options") or []:
        key = opt["key"]
        line = da.get(key, "")
        badge = (' <span class="badge ok">Correct</span>' if key in correct
                 else "")
        summary = "%s) %s%s" % (esc(key), esc(opt["text"]), badge)
        if line:
            rows.append('<li><details class="rationale" data-opt="%s" open>'
                        "<summary>%s</summary><p>%s</p></details></li>"
                        % (esc(key), summary, esc(line)))
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


def _card_markup(view):
    """One server-rendered card: a front face with the focused stem and an
    objective/type chip, a back face carrying the complete labelled
    explanation, and the native navigation/rating actions the client wires.
    The stem and explanation are escaped text, never executable markup.
    """
    t = view["type"]
    meta = ('<div class="meta"><span class="chip type">%s</span>%s</div>'
            % (esc(t), ('<span class="chip">%s</span>' % esc(view.get("objective", ""))
                        if view.get("objective") else "")))
    front = ('<div class="face front">%s<h2 class="stem">%s</h2>'
             '<p class="hint">recall the answer, then flip</p></div>'
             % (meta, esc(view["stem"])))
    back = '<div class="face back">%s</div>' % _explain_sections(view)
    acts = ('<div class="acts">'
            '<button type="button" class="b nav" data-prev>Prev</button>'
            '<button type="button" class="b nav" data-show>Show answer</button>'
            '<button type="button" class="b got" data-got>Got it</button>'
            '<button type="button" class="b miss" data-miss>Missed</button>'
            '<button type="button" class="b nav" data-next>Next</button>'
            "</div>")
    return ('<article class="card" data-card hidden>'
            '<div class="flip"><div class="inner" data-flip>%s%s</div></div>'
            "%s</article>" % (front, back, acts))


STUDY_JS = r"""
const CARDS=__DATA__;
const esc=s=>(s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const REDUCED=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
const deck=document.getElementById("deck"),status=document.getElementById("status"),prog=document.getElementById("prog");
let mode="flash",order=[],i=0,queue=[],mastered=0;
function shuffle(a){for(let j=a.length-1;j>0;j--){const k=Math.floor(Math.random()*(j+1));[a[j],a[k]]=[a[k],a[j]]}return a}
function cardEl(n){return deck.querySelector('[data-card="'+n+'"]')}
function say(t){status.textContent=t}
function setMode(m){mode=m;document.getElementById("tFlash").classList.toggle("on",m==="flash");document.getElementById("tLearn").classList.toggle("on",m==="learn");start()}
document.getElementById("tFlash").onclick=()=>setMode("flash");
document.getElementById("tLearn").onclick=()=>setMode("learn");
function show(n){
  deck.querySelectorAll("[data-card]").forEach((c,k)=>{c.hidden=k!==n});
  const c=cardEl(n);
  if(c)c.querySelector(".inner").classList.remove("flipped");
}
function wire(c){
  const inner=c.querySelector(".inner");
  inner.onclick=()=>{const on=inner.classList.toggle("flipped");say(on?"Explanation shown. Click the card to hide it.":"Card hidden. Click the card to reveal it.")};
  const prev=c.querySelector("[data-prev]"),next=c.querySelector("[data-next]"),
        showBtn=c.querySelector("[data-show]"),got=c.querySelector("[data-got]"),
        miss=c.querySelector("[data-miss]");
  prev.onclick=()=>{if(mode==="flash"){if(i>0){i--;render()}}else if(queue.length>1){queue.unshift(queue.pop());render()}};
  next.onclick=()=>{if(mode==="flash"){if(i<CARDS.length-1){i++;render()}else finish("Flashcards done.")}else{queue.push(queue.shift());render()}};
  showBtn.onclick=()=>{inner.classList.add("flipped");say("Explanation shown. Rate the card.");showBtn.hidden=true;got.hidden=false;miss.hidden=false};
  got.onclick=()=>{if(mode==="learn"){mastered++;queue.shift();render()}};
  miss.onclick=()=>{if(mode==="learn"){queue.push(queue.shift());render()}};
}
function renderFlash(){
  if(i>=CARDS.length)return finish("Flashcards done.");
  show(i);const c=cardEl(i);
  prog.style.width=(i/CARDS.length*100)+"%";
  say("Flashcards · card "+(i+1)+" of "+CARDS.length+" · click card to flip");
  const showBtn=c.querySelector("[data-show]"),got=c.querySelector("[data-got]"),
        miss=c.querySelector("[data-miss]"),prev=c.querySelector("[data-prev]"),
        next=c.querySelector("[data-next]");
  prev.hidden=false;next.hidden=false;showBtn.hidden=true;got.hidden=true;miss.hidden=true;
}
function renderLearn(){
  if(!queue.length)return finish("Learned all "+CARDS.length+".");
  show(queue[0]);const c=cardEl(queue[0]);
  prog.style.width=(mastered/CARDS.length*100)+"%";
  say("Learn · "+mastered+" mastered / "+CARDS.length+" · "+queue.length+" in pile");
  const showBtn=c.querySelector("[data-show]"),got=c.querySelector("[data-got]"),
        miss=c.querySelector("[data-miss]"),prev=c.querySelector("[data-prev]"),
        next=c.querySelector("[data-next]");
  prev.hidden=true;next.hidden=true;showBtn.hidden=false;got.hidden=true;miss.hidden=true;
}
function finish(msg){
  prog.style.width="100%";say("");
  deck.innerHTML='<div class="done"><div class="big">Done</div><p>'+esc(msg)+'</p><button type="button" class="b nav" data-again>Shuffle and restart</button></div>';
  document.querySelector("[data-again]").onclick=start;
}
function start(){
  order=shuffle([...Array(CARDS.length).keys()]);
  if(mode==="flash"){i=0;renderFlash()}else{queue=[...order];mastered=0;renderLearn()}
}
deck.querySelectorAll("[data-card]").forEach(wire);
start();
"""


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
    text = open(bank_path, encoding="utf-8").read()
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
            page_title, body, theme_css=css, back=back, noscript=noscript)
    cards = []
    for q in qs:
        try:
            cards.append(_card_markup(study_item(q)))
        except Exception:
            body = presentation.state_panel({
                "kind": "bad",
                "status": ("This card could not be shown. Move to the next "
                           "card or reload."),
                "actions": [{"label": "Reload", "href": "#"},
                            {"label": "Choose another bank", "href": "/"}]})
            return presentation.surface_shell(
                page_title, body, theme_css=css, back=back, noscript=noscript)
    body = (
        '<div class="tabs">'
        '<button type="button" class="tab on" id="tFlash">Flashcards</button>'
        '<button type="button" class="tab" id="tLearn">Learn</button></div>'
        '<div class="status" id="status" role="status" aria-live="polite">'
        "</div>"
        '<div class="bar"><i id="prog"></i></div>'
        '<div id="deck">%s</div>'
        % "".join(cards))
    page = presentation.surface_shell(
        page_title, body, theme_css=css + "\n" + STUDY_CSS,
        back=back, noscript=noscript)
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
    open(out, "w", encoding="utf-8").write(page)
    print("%d items -> %s" % (len(qs), out))
    return 0
