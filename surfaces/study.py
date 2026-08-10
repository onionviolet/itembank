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
.meta{font-size:12px;color:var(--mut);text-transform:uppercase;
  letter-spacing:.04em;margin:0 0 10px}
.chip{display:inline-block;background:var(--chip);color:var(--mut);
  padding:2px 8px;border-radius:5px;margin-right:6px;font-size:11px}
.chip.type{background:var(--accent-soft);color:var(--accent)}
.stem{font-size:20px;font-weight:600;margin:0 0 12px}
.recall-note{font-size:13px;color:var(--mut);margin:0 0 8px}
.recall-opts{display:flex;flex-direction:column;gap:8px;margin:0 0 16px}
.recall-opt{display:block;width:100%;text-align:left;min-height:44px;
  padding:10px 12px;border:1px solid var(--line);border-radius:9px;
  background:var(--card);color:var(--ink);font:inherit;cursor:pointer;
  transition:background .12s,border-color .12s}
.recall-opt:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.recall-opt[aria-pressed="true"]{border-color:var(--accent);
  background:var(--accent-soft);color:var(--accent)}
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
  border-radius:5px;border:1px solid currentColor;margin-right:8px;
  vertical-align:middle}
.badge.ok{color:var(--ok);background:var(--ok-bg)}
.badge.selected{color:var(--accent);background:var(--accent-soft)}
.model,.rows,.steps,.rubric{font-size:15px;line-height:1.5;
  overflow-wrap:anywhere}
.rows,.steps,.rubric{margin:0;padding-left:18px}
.rows li,.steps li,.rubric li{margin:0 0 4px}
.acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.acts button{min-height:44px;border:1px solid var(--line);border-radius:9px;
  padding:10px 20px;font:inherit;font-weight:600;cursor:pointer;
  background:var(--card);color:var(--ink)}
.acts button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.acts button[data-action-primary]{background:var(--accent-soft);
  border-color:var(--accent);color:var(--accent)}
.acts button:disabled{opacity:.55;cursor:default}
.done{text-align:center;padding:40px 10px}
.done .big{font-size:40px;font-weight:800;color:var(--ok)}
.done button{min-height:44px;border:1px solid var(--accent);border-radius:9px;
  padding:10px 20px;font:inherit;font-weight:600;cursor:pointer;
  background:var(--accent-soft);color:var(--accent)}
@media (max-width:767px){
  .stem{font-size:18px}
  .acts button{width:100%}
  .done button{width:100%}
}
"""


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


STUDY_JS = r"""
const CARDS=__DATA__;
const esc=s=>(s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const REDUCED=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
const deck=document.getElementById("deck"),status=document.getElementById("status"),prog=document.getElementById("prog");
let mode="flash",order=[],i=0,queue=[],mastered=0;
const selected={};
function shuffle(a){for(let j=a.length-1;j>0;j--){const k=Math.floor(Math.random()*(j+1));[a[j],a[k]]=[a[k],a[j]]}return a}
function cardEl(n){return deck.querySelector('[data-card="'+n+'"]')}
function say(t){status.textContent=t}
function setMode(m){mode=m;document.getElementById("tFlash").classList.toggle("on",m==="flash");document.getElementById("tLearn").classList.toggle("on",m==="learn");start()}
document.getElementById("tFlash").onclick=()=>setMode("flash");
document.getElementById("tLearn").onclick=()=>setMode("learn");
function show(n){deck.querySelectorAll("[data-card]").forEach((c,k)=>{c.hidden=k!==n})}
function syncState(c){
  const revealed=!c.querySelector("[data-explain]").hidden;
  const r=c.querySelector("[data-reveal]");
  if(!revealed){
    r.textContent="Reveal explanation";
    r.setAttribute("data-action-primary","");
    r.removeAttribute("aria-disabled");
  }
  c.querySelector("[data-acts=front]").hidden=false;
  c.querySelector("[data-acts=revealed]").hidden=!(revealed&&mode==="flash");
  c.querySelector("[data-acts=rating]").hidden=!(revealed&&mode==="learn");
}
function reveal(c){
  const sec=c.querySelector("[data-explain]");
  if(sec.hidden){say("Revealing explanation\u2026");sec.hidden=false;}
  const sel=selected[c.dataset.card]||[];
  sel.forEach(k=>{
    const d=c.querySelector('[data-opt="'+k+'"]');
    if(!d)return;
    d.open = true;
    const p=d.querySelector("p");
    if(p&&!p.querySelector(".badge.selected")){
      const b=document.createElement("span");
      b.className="badge selected";
      b.textContent="Selected";
      p.insertBefore(b,p.firstChild);
    }
  });
  const r=c.querySelector("[data-reveal]");
  r.textContent="Explanation revealed";
  r.setAttribute("aria-disabled","true");
  r.removeAttribute("data-action-primary");
  syncState(c);
  say("Explanation revealed. Review the answer and rationale.");
  r.focus({preventScroll:true});
}
function wireRecall(c){
  c.querySelectorAll("[data-recall]").forEach(b=>{
    b.addEventListener("click",()=>{
      const k=b.getAttribute("data-recall");
      const wasOn=b.getAttribute("aria-pressed")==="true";
      b.setAttribute("aria-pressed",wasOn?"false":"true");
      let s=selected[c.dataset.card]||(selected[c.dataset.card]=[]);
      const at=s.indexOf(k);
      if(wasOn){if(at>=0)s.splice(at,1)}else if(at<0)s.push(k);
      say(wasOn?"Your recall choice cleared. Not graded.":"Your recall choice recorded. Not graded.");
    });
  });
}
function wireNav(c){
  const prev=c.querySelector("[data-prev]"),next=c.querySelector("[data-next]");
  prev.addEventListener("click",()=>{
    if(mode==="flash"){if(i>0){i--;render()}}
    else if(queue.length>1){queue.unshift(queue.pop());render()}
  });
  next.addEventListener("click",()=>{
    if(mode==="flash"){if(i<CARDS.length-1){i++;render()}else finish("Flashcards done.")}
    else{queue.push(queue.shift());render()}
  });
  c.querySelector("[data-got]").addEventListener("click",()=>{if(mode==="learn"){mastered++;queue.shift();render()}});
  c.querySelector("[data-miss]").addEventListener("click",()=>{if(mode==="learn"){queue.push(queue.shift());render()}});
  c.querySelector("[data-reveal]").addEventListener("click",()=>reveal(c));
}
function render(){mode==="flash"?renderFlash():renderLearn()}
function renderFlash(){
  if(i>=CARDS.length)return finish("Flashcards done.");
  show(i);const c=cardEl(i);
  prog.style.width=((i+1)/CARDS.length*100)+"%";
  syncState(c);
  say("Flashcards · card "+(i+1)+" of "+CARDS.length);
  const r=c.querySelector("[data-reveal]");
  if(r&&!REDUCED)r.focus({preventScroll:true});
}
function renderLearn(){
  if(!queue.length)return finish("Learned all "+CARDS.length+".");
  show(queue[0]);const c=cardEl(queue[0]);
  prog.style.width=(mastered/CARDS.length*100)+"%";
  syncState(c);
  say("Learn · "+mastered+" mastered / "+CARDS.length+" · "+queue.length+" in pile");
  const r=c.querySelector("[data-reveal]");
  if(r&&!REDUCED)r.focus({preventScroll:true});
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
deck.querySelectorAll("[data-card]").forEach(c=>{wireRecall(c);wireNav(c)});
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
