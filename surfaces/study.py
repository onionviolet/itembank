"""Flashcards and a session-only Learn loop over the same bank."""
import html, json, os, sys

from model import grab, lint, load
from runtime import answer_text
from surfaces.theme import THEME_CSS


def study_item(q):
    return {"id": q["id"], "type": q["type"], "stem": q["stem"],
            "objective": q.get("objective", ""), "answer": answer_text(q),
            "why": q.get("why", ""), "disc": q.get("disc", ""),
            "trap": q.get("trap", "")}


STUDY_TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__ study</title>
<style>
__THEME__
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:720px;margin:0 auto;padding:22px 18px 80px}h1{font-size:19px;margin:0 0 12px}
.tabs{display:flex;gap:8px;margin-bottom:14px}.tab{flex:1;padding:9px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--ink);cursor:pointer;font:inherit;font-weight:600}.tab.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.status{color:var(--mut);font-size:13px;margin-bottom:10px}.bar{height:6px;background:var(--line);border-radius:99px;overflow:hidden;margin:12px 0}.bar>i{display:block;height:100%;background:var(--accent);width:0}
.flip{perspective:1200px;margin-bottom:16px}.inner{position:relative;min-height:280px;transition:transform .4s;transform-style:preserve-3d;cursor:pointer}.inner.flipped{transform:rotateY(180deg)}
.face{position:absolute;inset:0;backface-visibility:hidden;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:24px;display:flex;flex-direction:column;justify-content:center}.back{transform:rotateY(180deg)}
.meta{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em;margin-bottom:10px}.meta b{color:var(--accent)}.stem{font-size:18px;font-weight:600}.hint{color:var(--mut);font-size:13px;margin-top:16px;text-align:center}.ans{font-size:17px;font-weight:700;color:var(--ok);margin-bottom:10px}.why{font-size:15px;margin-bottom:8px}.disc{font-size:14px;color:var(--mut)}.trap{font-size:14px;color:var(--bad);margin-top:8px}
.row{display:flex;gap:10px;justify-content:center}button.b{border:0;border-radius:9px;padding:11px 20px;font:inherit;font-weight:600;cursor:pointer;color:#fff}.nav{background:var(--accent)}.got{background:var(--ok)}.miss{background:var(--bad)}.ghost{background:var(--card);color:var(--ink);border:1px solid var(--line)}.done{text-align:center;padding:40px 10px}.done .big{font-size:40px;font-weight:800;color:var(--ok)}
</style></head><body><div class="wrap"><h1>__TITLE__ study set</h1><div class="tabs"><button class="tab on" id="tFlash">Flashcards</button><button class="tab" id="tLearn">Learn</button></div><div class="status" id="status"></div><div class="bar"><i id="prog"></i></div><div id="stage"></div></div>
<script>
const CARDS=__DATA__,esc=s=>(s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
const stage=document.getElementById("stage"),status=document.getElementById("status"),prog=document.getElementById("prog");let mode="flash",order=[],i=0,queue=[],mastered=0;
function setMode(m){mode=m;document.getElementById("tFlash").classList.toggle("on",m==="flash");document.getElementById("tLearn").classList.toggle("on",m==="learn");start()}
document.getElementById("tFlash").onclick=()=>setMode("flash");document.getElementById("tLearn").onclick=()=>setMode("learn");
function faces(c){let f=`<div class="face front"><div class="meta">Concept${c.objective?" · <b>"+esc(c.objective)+"</b>":""}</div><div class="stem">${esc(c.stem)}</div><div class="hint">recall the answer, then flip</div></div>`;let b=`<div class="face back"><div class="ans">${esc(c.answer)}</div><div class="why">${esc(c.why)}</div>`;if(c.disc)b+=`<div class="disc"><b>Discriminator:</b> ${esc(c.disc)}</div>`;if(c.trap)b+=`<div class="trap"><b>Trap:</b> ${esc(c.trap)}</div>`;return f+b+"</div>"}
function renderFlash(){let c=CARDS[order[i]];prog.style.width=(i/CARDS.length*100)+"%";status.textContent=`Flashcards · card ${i+1} of ${CARDS.length} · click card to flip`;stage.innerHTML=`<div class="flip"><div class="inner" id="fc">${faces(c)}</div></div><div class="row"><button class="b ghost" id="prev">Prev</button><button class="b nav" id="next">Next</button></div>`;let fc=document.getElementById("fc");fc.onclick=()=>fc.classList.toggle("flipped");document.getElementById("prev").onclick=()=>{if(i>0){i--;renderFlash()}};document.getElementById("next").onclick=()=>{if(i<CARDS.length-1){i++;renderFlash()}else finish("Flashcards done.")}}
function renderLearn(){if(!queue.length)return finish(`Learned all ${CARDS.length}.`);let c=CARDS[queue[0]];prog.style.width=(mastered/CARDS.length*100)+"%";status.textContent=`Learn · ${mastered} mastered / ${CARDS.length} · ${queue.length} in pile`;stage.innerHTML=`<div class="flip"><div class="inner" id="fc">${faces(c)}</div></div><div class="row" id="controls"><button class="b nav" id="show">Show answer</button></div>`;let fc=document.getElementById("fc");document.getElementById("show").onclick=()=>{fc.classList.add("flipped");document.getElementById("controls").innerHTML='<button class="b miss" id="no">Missed</button><button class="b got" id="yes">Got it</button>';document.getElementById("yes").onclick=()=>{mastered++;queue.shift();renderLearn()};document.getElementById("no").onclick=()=>{queue.push(queue.shift());renderLearn()}}}
function finish(msg){prog.style.width="100%";status.textContent="";stage.innerHTML=`<div class="done"><div class="big">Done</div><p>${esc(msg)}</p><button class="b nav" id="again">Shuffle and restart</button></div>`;document.getElementById("again").onclick=start}
function start(){order=shuffle([...Array(CARDS.length).keys()]);if(mode==="flash"){i=0;renderFlash()}else{queue=[...order];mastered=0;renderLearn()}}start();
</script></body></html>"""


def study_page(bank_path, qs):
    """The exact substitution chain `cmd_study` used to run inline, factored
    out so the daemon and the CLI render the study surface from one function
    instead of two copies of the same three `.replace()` calls (D-08
    extended to the study surface). Returns the page string; the study
    surface has no client POST at all, so no path parameterisation is
    needed here the way `quiz.page_for()` and `day.day_page()` need one.
    """
    title = grab(r"(?m)^#\s+(.*?)\s*$", open(bank_path, encoding="utf-8").read()) \
        or os.path.basename(bank_path)
    return (STUDY_TEMPLATE.replace("__THEME__", THEME_CSS)
            .replace("__TITLE__", html.escape(title))
            .replace("__DATA__", json.dumps([study_item(q) for q in qs],
                                            ensure_ascii=False)))


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
