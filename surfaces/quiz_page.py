"""The quiz page itself: markup, style and behaviour, as one asset.

Kept apart from the code that fills it in because it is a different kind of
thing to read. `quiz.py` decides what an item may contain; this decides how it
looks and what clicking it does.
"""


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
__THEME__
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:800px;margin:0 auto;padding:22px 18px 96px}
header{margin-bottom:18px}
h1{font-size:21px;margin:0 0 4px;letter-spacing:-.01em}
.sub{color:var(--mut);font-size:13.5px}
.mono{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  font-variant-numeric:tabular-nums}
.railwrap{position:sticky;top:0;background:var(--bg);padding:10px 0 12px;z-index:5}
.rail{height:5px;background:var(--line);border-radius:99px;overflow:hidden}
.rail>i{display:block;height:100%;width:0;background:var(--accent);transition:width .3s}
.tally{display:flex;gap:14px;font-size:12.5px;color:var(--mut);margin-top:7px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:18px 18px 16px;margin-bottom:14px}
.meta{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-bottom:9px}
.chip{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;
  background:var(--chip);color:var(--mut);padding:3px 8px;border-radius:5px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.chip.type{background:var(--accent-soft);color:var(--accent)}
.chip.aon{background:var(--bad-bg);color:var(--bad)}
.stem{margin:0 0 13px;font-size:16.5px;text-wrap:pretty}
.opts{display:flex;flex-direction:column;gap:7px}
.opt{display:flex;gap:10px;align-items:flex-start;width:100%;text-align:left;
  background:var(--card);border:1px solid var(--line);border-radius:9px;
  padding:10px 12px;font:inherit;color:inherit;cursor:pointer;transition:.12s}
.opt:hover:not(:disabled){border-color:var(--accent)}
.opt:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.opt[aria-pressed="true"]{border-color:var(--accent);background:var(--accent-soft)}
.opt .k{flex:0 0 auto;font-family:ui-monospace,Menlo,Consolas,monospace;
  font-size:13px;color:var(--mut);min-width:1.2em}
.opt .ot{flex:1 1 auto;min-width:0}
.opt .rat{display:block;margin-top:6px;font-size:12.5px;line-height:1.5;color:var(--mut)}
.opt.right .rat{color:var(--ok)}
.opt.wrong .rat{color:var(--bad)}
.opt.right{border-color:var(--ok);background:var(--ok-bg)}
.opt.wrong{border-color:var(--bad);background:var(--bad-bg)}
.opt:disabled{cursor:default}
.rowline{display:flex;gap:10px;align-items:center;flex-wrap:wrap;
  padding:9px 0;border-bottom:1px solid var(--line)}
.rowline:last-of-type{border-bottom:0}
.rowtext{flex:1 1 240px;min-width:0}
.seg{display:flex;gap:5px;flex-wrap:wrap}
.seg button{font:inherit;font-size:13.5px;padding:5px 11px;border-radius:7px;
  border:1px solid var(--line);background:var(--card);color:inherit;cursor:pointer}
.seg button[aria-pressed="true"]{border-color:var(--accent);background:var(--accent-soft);
  color:var(--accent)}
.seg button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.seg button.right{border-color:var(--ok);background:var(--ok-bg);color:var(--ok)}
.seg button.wrong{border-color:var(--bad);background:var(--bad-bg);color:var(--bad)}
.ord{flex:0 0 auto;width:26px;height:26px;border-radius:50%;display:grid;
  place-items:center;font-family:ui-monospace,Menlo,monospace;font-size:12.5px;
  border:1px solid var(--line);color:var(--mut)}
.ord.set{background:var(--accent);border-color:var(--accent);color:#fff}
.act{margin-top:13px;display:flex;gap:9px;align-items:center;flex-wrap:wrap}
button.go{font:inherit;font-weight:600;font-size:14.5px;padding:9px 17px;border:0;
  border-radius:9px;background:var(--accent);color:#fff;cursor:pointer}
button.go:disabled{opacity:.4;cursor:default}
button.go:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.hint{font-size:12.5px;color:var(--mut)}
.exp{margin-top:14px;padding-top:13px;border-top:1px solid var(--line);font-size:14.5px}
.exp h4{margin:0 0 5px;font-size:11px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--mut);font-family:ui-monospace,Menlo,Consolas,monospace}
.exp .blk{margin-bottom:11px}
.exp ul{margin:5px 0 0;padding-left:18px}
.exp li{margin-bottom:4px}
.verdict{font-weight:600;margin-bottom:10px}
.verdict.y{color:var(--ok)} .verdict.n{color:var(--bad)}
.trap{background:var(--accent-soft);border-left:3px solid var(--accent);
  padding:9px 12px;border-radius:0 7px 7px 0}
textarea.ans{width:100%;min-height:150px;padding:11px 12px;border-radius:9px;
  border:1px solid var(--line);background:var(--card);color:inherit;
  font:inherit;font-size:15.5px;line-height:1.5;resize:vertical}
textarea.ans:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:var(--accent)}
textarea.ans:disabled{opacity:.75}
.pend{color:var(--warn);font-weight:600;margin-bottom:10px}
#savestate.bad{color:var(--bad)}
.done{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px}
.score{font-size:34px;font-weight:700;letter-spacing:-.02em}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style></head><body><div class="wrap">
<header>
  <h1>__TITLE__</h1>
  <div class="sub">__SUB__</div>
</header>
<div class="railwrap">
  <div class="rail"><i id="rail"></i></div>
  <div class="tally mono">
    <span>ITEM <b id="pos">1</b>/<b id="tot">0</b></span>
    <span>CORRECT <b id="ok">0</b></span>
    <span>ALL-OR-NOTHING SCORING</span>
    <span id="savestate"></span>
  </div>
</div>
<div id="host"></div>
</div>
<script>
const Q = __DATA__;
const SERVE = __SERVE__;     /* true under `itembank serve`: the process scores */
const LETTERS = "ABCDEFGH";
const LABEL = {mc:"multiple choice", multi:"multiple response",
               table:"options table", build:"build list", dnd:"drag-and-drop",
               short:"short answer"};
const FS = "\u001f", PS = "\u001e";   /* must match FIELD_SEP and PAIR_SEP */
let i = 0, score = 0, autoTotal = 0;
/* When the current item was rendered, per performance.now() -- a monotonic
   clock, so a system clock change mid-sitting cannot produce a negative or
   absurd elapsed_ms (T-1-25). Reset every time render() shows a new item. */
let shownAt = performance.now();
const miss = [];
const host = document.getElementById("host");
const esc = s => (s==null?"":String(s));

/* ---- the verdict -----------------------------------------------------------
   This page does not decide whether an answer is right. Under `serve` it hands
   the response to the process, which calls the one scorer and returns the
   verdict together with the explanation, so the page never holds a key it could
   leak or score against. There is no process behind a file:// page, so `build`
   ships a canonical key that Python computed and the check below is a single
   string comparison against it. That is a lookup, not a second set of scoring
   rules: every rule about what counts as correct still lives in one function,
   in one language.

   Each answer reaches the server the moment it is given rather than at the end,
   so a closed tab or a dead battery costs at most the item in progress. */
function canon(q, r){
  if(q.type==="mc")    return String(r).toUpperCase();
  if(q.type==="multi") return r.map(x=>String(x).toUpperCase()).sort().join(",");
  if(q.type==="table" || q.type==="dnd")
    return q.rows.map(row => row.id + PS + (r[String(row.id)]||"")).join(FS);
  if(q.type==="build") return r.join(FS);
  return "";
}

async function verify(q, response){
  if(!SERVE)
    return {score: (q.key===null || q.key===undefined) ? null : canon(q, response)===q.key,
            explain: q.explain || {}};
  /* performance.now() rather than Date.now(): elapsed_ms is a monotonic-clock
     delta, so it cannot go negative under a system clock change mid-sitting. */
  const elapsed_ms = Math.max(0, Math.round(performance.now() - shownAt));
  const res = await fetch("/answer", {method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({id: q.id, response: response, elapsed_ms: elapsed_ms})});
  if(!res.ok) throw new Error("HTTP " + res.status);
  return res.json();
}

/* Paint the widget, then the explanation. A failed verify shows the failure
   rather than a verdict: a green tick the process never issued would be a lie
   about work that was not recorded. */
async function settle(q, response, card, act, paint){
  const el = document.getElementById("savestate");
  let v;
  try {
    v = await verify(q, response);
  } catch(err){
    if(el){ el.textContent = "NOT SAVED"; el.className = "bad"; }
    act.innerHTML = "";
    const p = document.createElement("div");
    p.className = "hint";
    p.style.color = "var(--bad)";
    p.textContent = "Could not reach the process that scores and records this sitting ("
                  + err.message + "). This answer was not saved and was not marked. "
                  + "Restart `itembank serve` and sit it again.";
    act.appendChild(p);
    return;
  }
  if(el && SERVE){ el.textContent = "SAVED"; el.className = ""; }
  if(paint) paint(v);
  close(q, card, act, v);
}

function shuffled(a){const b=a.slice();for(let j=b.length-1;j>0;j--){
  const k=Math.floor(Math.random()*(j+1));[b[j],b[k]]=[b[k],b[j]];}return b;}

function chips(q){
  let h = `<span class="chip type">${LABEL[q.type]||q.type}</span>`;
  if(q.type==="short") h += `<span class="chip aon">graded by a marker, not by this page</span>`;
  else if(q.type!=="mc") h += `<span class="chip aon">no partial credit</span>`;
  if(q.objective) h += `<span class="chip">${esc(q.objective)}</span>`;
  if(q.difficulty) h += `<span class="chip">${esc(q.difficulty)}</span>`;
  return h;
}

function render(){
  document.getElementById("pos").textContent = Math.min(i+1, Q.length);
  document.getElementById("tot").textContent = Q.length;
  document.getElementById("ok").textContent = score;
  document.getElementById("rail").style.width = (i/Q.length*100)+"%";
  if(i>=Q.length) return finish();
  shownAt = performance.now();
  const q = Q[i];
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `<div class="meta">${chips(q)}</div><p class="stem">${esc(q.stem)}</p>`;
  const body = document.createElement("div");
  card.appendChild(body);
  const act = document.createElement("div");
  act.className = "act";
  card.appendChild(act);
  host.innerHTML = "";
  host.appendChild(card);
  ({mc:asChoice, multi:asChoice, table:asAssign, dnd:asAssign, build:asBuild,
    short:asShort}[q.type])(q, body, act, card);
  card.scrollIntoView({block:"start", behavior:"smooth"});
}

/* ---- multiple choice + multiple response ----------------------------------
   Options are reshuffled on every page load, not at build time, so reopening
   the same file gives a different arrangement. This is why a bank's keyed
   letters do not need to be balanced: position skew cannot survive a shuffle.
   Options whose text refers to position ("all of the above", "both A and B")
   are pinned to the end in their original order, because shuffling them
   produces nonsense. */
const PINNED = /^\s*(all|none)\s+of\s+the\s+above|^\s*both\s+[A-H]\s+and\s+[A-H]/i;

function asChoice(q, body, act, card){
  const multi = q.type === "multi";
  const want = q.response_schema.select;
  const free = q.options.filter(o=>!PINNED.test(o.text));
  const pins = q.options.filter(o=> PINNED.test(o.text));
  const shown = shuffled(free).concat(pins);
  shown.forEach((o,n)=> o.label = LETTERS[n]);

  const picked = [];   // holds ORIGINAL keys; display letters are cosmetic
  const wrap = document.createElement("div");
  wrap.className = "opts";
  const btns = {};
  let submit;
  shown.forEach(o=>{
    const b = document.createElement("button");
    b.className = "opt"; b.type = "button"; b.setAttribute("aria-pressed","false");
    b.innerHTML = `<span class="k">${o.label}</span><span class="ot">${esc(o.text)}</span>`;
    b.onclick = ()=>{
      if(!multi){ picked.length=0; picked.push(o.key); go(); return; }
      const at = picked.indexOf(o.key);
      if(at>=0) picked.splice(at,1);
      else if(picked.length < want) picked.push(o.key);
      shown.forEach(x=>btns[x.key].setAttribute("aria-pressed",
        picked.includes(x.key)?"true":"false"));
      submit.disabled = picked.length !== want;
    };
    btns[o.key]=b; wrap.appendChild(b);
  });
  body.appendChild(wrap);
  if(multi){
    submit = mkSubmit(act, `select ${want}`);
    submit.onclick = go;
  }
  function go(){
    shown.forEach(o=>{ btns[o.key].disabled = true; });
    if(submit) submit.remove();
    settle(q, multi ? picked.slice() : picked[0], card, act, paint);
  }
  /* The rationale belongs to the option it is about, not to a footnote list
     under the card. The same sentence reads as "why the answer you gave failed"
     when it sits on that answer, and as trivia about the item when it sits in a
     list below four other lines. No authoring changes: this is the `da` the
     bank already carries, and it is the same data the hint ladder's tier 3
     hands back one tier at a time. WHY BEST moves onto the keyed option when
     there is exactly one, since on a multiple-response item it is about the set
     rather than about any single option. */
  function paint(v){
    const ex = v.explain || {};
    const correct = ex.correct || [];
    const sole = correct.length === 1 ? correct[0] : null;
    shown.forEach(o=>{
      const b = btns[o.key];
      if(correct.includes(o.key)) b.classList.add("right");
      else if(picked.includes(o.key)) b.classList.add("wrong");
      const line = (o.key === sole && ex.why) ? ex.why : ((ex.da||{})[o.key] || "");
      if(line){
        const r = document.createElement("span");
        r.className = "rat";
        r.textContent = line;      // textContent, so a bank cannot inject markup
        b.querySelector(".ot").appendChild(r);
      }
    });
    v.skipWhy = !!(sole && ex.why);
  }
}

/* ---- options table + drag-and-drop (assign each row to a category) --------
   Rows are reshuffled every load, so the response is keyed by the row's id
   rather than by where it happens to sit on screen. */
function asAssign(q, body, act, card){
  const rows = shuffled(q.rows);
  const chosen = {};                 // row id -> category
  const segs = {};
  rows.forEach(r=>{
    const id = String(r.id);
    const line = document.createElement("div");
    line.className = "rowline";
    const t = document.createElement("div");
    t.className = "rowtext"; t.textContent = r.text;
    const seg = document.createElement("div");
    seg.className = "seg";
    const bs = q.categories.map(c=>{
      const b = document.createElement("button");
      b.type="button"; b.textContent=c; b.setAttribute("aria-pressed","false");
      b.onclick = ()=>{
        chosen[id]=c;
        bs.forEach(x=>x.setAttribute("aria-pressed", x.textContent===c?"true":"false"));
        submit.disabled = Object.keys(chosen).length !== q.rows.length;
      };
      seg.appendChild(b); return b;
    });
    segs[id] = bs;
    line.appendChild(t); line.appendChild(seg); body.appendChild(line);
  });
  const submit = mkSubmit(act, "assign every row");
  submit.onclick = ()=>{
    rows.forEach(r=>segs[String(r.id)].forEach(b=>{ b.disabled = true; }));
    submit.remove();
    settle(q, Object.assign({}, chosen), card, act, v=>{
      const cats = (v.explain||{}).row_cats || {};
      rows.forEach(r=>{
        const id = String(r.id);
        segs[id].forEach(b=>{
          if(b.textContent===cats[id]) b.classList.add("right");
          else if(b.textContent===chosen[id]) b.classList.add("wrong");
        });
      });
    });
  };
}

/* ---- build list (click into order) ---------------------------------------- */
function asBuild(q, body, act, card){
  const shown = shuffled(q.steps);
  const order = [];
  const wrap = document.createElement("div");
  wrap.className = "opts";
  const btns = shown.map(s=>{
    const b = document.createElement("button");
    b.className="opt"; b.type="button"; b.setAttribute("aria-pressed","false");
    b.innerHTML = `<span class="ord">-</span><span>${esc(s)}</span>`;
    b.onclick = ()=>{
      const at = order.indexOf(s);
      if(at>=0) order.splice(at,1); else order.push(s);
      redraw(); submit.disabled = order.length !== q.steps.length;
    };
    wrap.appendChild(b); return b;
  });
  function redraw(){
    shown.forEach((s,n)=>{
      const at = order.indexOf(s);
      const o = btns[n].querySelector(".ord");
      o.textContent = at>=0 ? (at+1) : "-";
      o.classList.toggle("set", at>=0);
      btns[n].setAttribute("aria-pressed", at>=0?"true":"false");
    });
  }
  body.appendChild(wrap);
  const submit = mkSubmit(act, "tap the steps in order");
  submit.onclick = ()=>{
    shown.forEach((s,n)=>{ btns[n].disabled = true; });
    submit.remove();
    settle(q, order.slice(), card, act, v=>{
      const right = (v.explain||{}).steps || [];
      shown.forEach((s,n)=>{
        const at = right.indexOf(s);
        btns[n].classList.add(order.indexOf(s)===at ? "right" : "wrong");
        btns[n].querySelector(".ord").textContent = at>=0 ? at+1 : "-";
      });
    });
  };
}

/* ---- short answer (constructed response, never auto-graded) ----------------
   The page deliberately cannot mark this. Auto-grading prose means matching
   keywords, and a keyword match cannot tell a correct explanation from a
   confident wrong one that happens to contain the right nouns. So the answer is
   recorded verbatim and a marker checks it against RUBRIC afterwards. The model
   answer stays hidden unless the bank was rendered with --reveal, because
   seeing it turns the next item into recognition. */
function asShort(q, body, act, card){
  const ta = document.createElement("textarea");
  ta.className = "ans";
  ta.placeholder = "Type your answer. Complete sentences; this is marked on what you actually wrote.";
  body.appendChild(ta);
  const submit = mkSubmit(act, "your own words, no notes");
  ta.oninput = ()=>{ submit.disabled = ta.value.trim().length < 2; };
  ta.focus();
  submit.onclick = ()=>{
    ta.disabled = true;
    submit.remove();
    settle(q, ta.value.trim(), card, act, null);
  };
}

function mkSubmit(act, hint){
  const b = document.createElement("button");
  b.className="go"; b.type="button"; b.textContent="Check"; b.disabled=true;
  const h = document.createElement("span"); h.className="hint"; h.textContent=hint;
  act.appendChild(b); act.appendChild(h);
  return b;
}

/* ---- reveal ----------------------------------------------------------------
   Everything rendered here arrives with the verdict. Before an answer is given
   the page holds none of it under `serve`, which is the point: an item cannot
   leak a key the page was never sent. */
function close(q, card, act, v){
  const ex = v.explain || {};
  const right = v.score;
  const pending = (right === null || right === undefined);
  if(!pending){ autoTotal++; if(right) score++; else miss.push({q, ex}); }
  act.innerHTML = "";
  const exp = document.createElement("div");
  exp.className = "exp";
  const blk = (t,val)=> val ? `<div class="blk"><h4>${t}</h4><div>${esc(val)}</div></div>` : "";
  let h = pending
    ? `<div class="pend">Recorded. Not marked here.</div>`
    : `<div class="verdict ${right?"y":"n"}">${right?"Correct":"Not correct"}</div>`;
  if(q.type === "short"){
    if(ex.model){
      h += blk("Model answer", ex.model);
      if(ex.rubric && ex.rubric.length)
        h += `<div class="blk"><h4>What a marker checks</h4><ul><li>`
           + ex.rubric.map(esc).join("</li><li>") + `</li></ul></div>`;
    } else {
      h += `<div class="blk" style="color:var(--mut);font-size:13.5px">The model answer is
        held back so it cannot contaminate the items after this one. It is in the bank file`
        + (SERVE ? `, and in the attempt file next to what you wrote.` : `.`) + `</div>`;
    }
  } else {
    // Skipped when the caller already put WHY BEST on the keyed option.
    if(!v.skipWhy) h += blk("Why this is best", ex.why);
    h += blk("Key discriminator", ex.disc);
    h += blk("Second best", ex.second);
    // Per-option analysis renders on the options themselves; NOTES has no
    // option to belong to, so it keeps a block here.
    if(ex.notes && ex.notes.length) h += `<div class="blk"><h4>Notes</h4><ul><li>`
      + ex.notes.map(esc).join("</li><li>") + `</li></ul></div>`;
  }
  if(ex.trap) h += `<div class="blk trap"><h4>Trap</h4><div>${esc(ex.trap)}</div></div>`;
  exp.innerHTML = h;
  card.appendChild(exp);
  const next = document.createElement("button");
  next.className="go"; next.type="button";
  next.textContent = (i===Q.length-1) ? "See results" : "Next";
  next.onclick = ()=>{ i++; render(); };
  act.appendChild(next);
  next.focus();
}

/* ---- results -------------------------------------------------------------- */
function finish(){
  document.getElementById("rail").style.width = "100%";
  const pct = autoTotal ? Math.round(score/autoTotal*100) : 0;
  const pend = Q.filter(q=>q.type==="short").length;
  let h = `<div class="done"><div class="score mono">${score}/${autoTotal}
    <span style="font-size:17px;color:var(--mut)"> &middot; ${pct}% auto-marked</span></div>`;
  if(pend) h += `<p style="margin:12px 0 0;color:var(--warn)"><b>${pend} short
    answer${pend>1?"s":""} not marked here.</b> ${SERVE
      ? "They are in the attempt file, waiting for a marker."
      : "Nothing recorded them, because this page was opened as a file. Use <code>itembank serve</code> for a sitting that is meant to be graded."}</p>`;
  if(miss.length){
    h += `<p style="margin:14px 0 6px"><b>${miss.length} to harvest.</b>
      Per Anki_Testing_Strategy &sect;2, the discriminator becomes the card, not the question.</p><ul>`;
    miss.forEach(m=>{
      h += `<li style="margin-bottom:9px"><b>${esc(m.q.stem.slice(0,110))}</b>`
        + (m.q.objective ? ` <span class="chip">${esc(m.q.objective)}</span>` : "")
        + (m.ex.trap ? `<br><span style="color:var(--mut)">Trap: ${esc(m.ex.trap)}</span>` : "")
        + `</li>`;
    });
    h += `</ul>`;
  } else {
    h += `<p style="margin-top:14px">Clean sweep. Nothing to harvest.</p>`;
  }
  h += `</div>`;
  host.innerHTML = h;
  window.scrollTo({top:0, behavior:"smooth"});
}

Q.sort(()=>Math.random()-0.5);
render();
</script></body></html>"""
