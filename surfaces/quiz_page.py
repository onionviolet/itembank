"""The quiz page itself: markup, style and behaviour, as one asset.

Kept apart from the code that fills it in because it is a different kind of
thing to read. `quiz.py` decides what an item may contain; this decides how it
looks and what clicking it does.

The page ships two mutually exclusive clients. `OFFLINE_JS` is the static
`build` compatibility client: it receives the full Python-produced item array
with canonical keys and compares against them, because a file:// page has no
process behind it. `SERVED_JS` is the daemon-served client (SURF-02): it
receives only bootstrap metadata, starts the sitting through POST /api/start,
submits through POST /api/submit, and renders only the server-issued verdict
and explanation. The served page never contains the offline canonicalization
implementation, and the static page never references the API.
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
.statusline{min-height:1.4em;color:var(--mut);font-size:13.5px;margin:0 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:18px 18px 16px;margin-bottom:14px}
.meta{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-bottom:9px}
.chip{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;
  background:var(--chip);color:var(--mut);padding:3px 8px;border-radius:5px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.chip.type{background:var(--accent-soft);color:var(--accent)}
.chip.aon{background:var(--bad-bg);color:var(--bad)}
.chip.lesson{background:var(--accent-soft);color:var(--accent);
  text-decoration:none;display:inline-block}
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
<div id="status" role="status" aria-live="polite" class="statusline"></div>
<div id="host"></div>
</div>
<script id="offline">
__OFFLINE_JS__
</script>
<script id="served">
__SERVED_JS__
</script>
</body></html>"""


# The static `build` compatibility client. This is the only place the
# canonical-key comparison lives; under `serve` this whole block is
# substituted away so the daemon-served page contains none of the offline-only
# implementation (plan 04-01 Test 5).
OFFLINE_JS = r"""const Q = __DATA__;
const SERVE = false;
const LESSON_BASE = "__LESSON_BASE__";   /* empty when no reader sits behind this page */
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
const esc = s => (s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

/* ---- the verdict -----------------------------------------------------------
   A file:// page has no process behind it, so the static build ships a
   canonical key that Python computed and the check below is a single string
   comparison against it. That is a lookup, not a second set of scoring rules:
   every rule about what counts as correct still lives in one function, in one
   language (runtime.canonical_response / canonical_key). */
function canon(q, r){
  if(q.type==="mc")    return String(r).toUpperCase();
  if(q.type==="multi") return r.map(x=>String(x).toUpperCase()).sort().join(",");
  if(q.type==="table" || q.type==="dnd")
    return q.rows.map(row => row.id + PS + (r[String(row.id)]||"")).join(FS);
  if(q.type==="build") return r.join(FS);
  return "";
}

async function verify(q, response){
  return {score: (q.key===null || q.key===undefined) ? null : canon(q, response)===q.key,
          explain: q.explain || {}};
}

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
  /* D-12: a static file:// page has no daemon behind /lesson/<stem> to link
     to, so it gets no chip rather than a link that silently does nothing. */
  if(q.lesson_slug && LESSON_BASE)
    h += `<a class="chip lesson" href="${LESSON_BASE}#${q.lesson_slug}"
          target="_blank" rel="noopener">__LESSON_LABEL__</a>`;
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

/* ---- multiple choice + multiple response ---------------------------------- */
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

/* ---- options table + drag-and-drop ---------------------------------------- */
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

/* ---- short answer (constructed response, never auto-graded) ---------------- */
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
    if(!v.skipWhy) h += blk("Why this is best", ex.why);
    h += blk("Key discriminator", ex.disc);
    h += blk("Second best", ex.second);
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
    answer${pend>1?"s":""} not marked here.</b> Nothing recorded them, because this page
    was opened as a file. Use <code>itembank serve</code> for a sitting that is meant
    to be graded.</p>`;
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

/* A #<id> URL fragment pins that item to the front of the deck before the
   shuffle runs over the rest. */
const frag = location.hash.replace(/^#/, "");
if(frag){ const at = Q.findIndex(x => String(x.id) === frag); if(at >= 0) Q.unshift(Q.splice(at, 1)[0]); }
Q.sort(()=>Math.random()-0.5);
render();
"""


# The daemon-served client (SURF-02): starts and submits through the canonical
# /api/* JSON session API. This script contains no scoring, no canonicalization,
# no key material, and no full item array -- it renders only what the server
# returns. Presentation state (selection, current item, position) is managed
# here; every verdict and every explanation comes from /api/submit.
SERVED_JS = r"""const BOOT = __BOOT__;
const SERVE = true;
const LESSON_BASE = "__LESSON_BASE__";   /* empty when no reader sits behind this page */
const LETTERS = "ABCDEFGH";
const LABEL = {mc:"multiple choice", multi:"multiple response",
               table:"options table", build:"build list", dnd:"drag-and-drop",
               short:"short answer"};
const FS = "\u001f", PS = "\u001e";   /* must match FIELD_SEP and PAIR_SEP */
let sessionId = null, i = 0, total = 0, score = 0, autoTotal = 0;
let shownAt = performance.now();
const miss = [];
const host = document.getElementById("host");
const statusEl = document.getElementById("status");
const esc = s => (s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

function setStatus(text){
  if(statusEl) statusEl.textContent = text;
}

async function api(url, payload){
  const res = await fetch(url, {method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify(payload)});
  if(!res.ok) throw new Error("HTTP " + res.status);
  return res.json();
}

/* ---- the verdict -----------------------------------------------------------
   This page never decides whether an answer is right. Every response goes to
   /api/submit; the server scores it through runtime.score_response and returns
   the verdict, the explanation and the next item. No key, canonicalization or
   scoring code exists anywhere in this script. */
async function verify(q, response){
  const v = await api("/api/submit", {session_id: sessionId, answer: response});
  return {score: v.score, explain: v.explain || {}, next: v.next};
}

async function settle(q, response, card, act, paint, revert){
  setStatus("Checking answer…");
  try {
    const v = await verify(q, response);
    setStatus("");
    if(paint) paint(v);
    close(q, card, act, v);
  } catch(err){
    /* API failure: keep the current item and the entered response visible,
       offer a retry, and never manufacture a verdict the server did not issue. */
    setStatus("Couldn't check that answer. Your selection is still here.");
    if(revert) revert();
    const b = document.createElement("button");
    b.className = "go"; b.type = "button"; b.textContent = "Try again";
    b.onclick = ()=>{ act.innerHTML = ""; settle(q, response, card, act, paint, revert); };
    act.appendChild(b);
    b.focus();
  }
}

function shuffled(a){const b=a.slice();for(let j=b.length-1;j>0;j--){
  const k=Math.floor(Math.random()*(j+1));[b[j],b[k]]=[b[k],b[j]];}return b;}

function chips(q){
  let h = `<span class="chip type">${LABEL[q.type]||q.type}</span>`;
  if(q.type==="short") h += `<span class="chip aon">graded by a marker, not by this page</span>`;
  else if(q.type!=="mc") h += `<span class="chip aon">no partial credit</span>`;
  if(q.objective) h += `<span class="chip">${esc(q.objective)}</span>`;
  if(q.difficulty) h += `<span class="chip">${esc(q.difficulty)}</span>`;
  /* D-12: the chip only ships when a reader sits behind this page, and a
     LESSON-REF that does not resolve to a served heading (--force) has its
     slug omitted rather than linking to a dead anchor. */
  if(q.lesson_slug && LESSON_BASE
     && (!BOOT.lesson_slugs || BOOT.lesson_slugs.indexOf(q.lesson_slug) >= 0))
    h += `<a class="chip lesson" href="${LESSON_BASE}#${q.lesson_slug}"
          target="_blank" rel="noopener">__LESSON_LABEL__</a>`;
  return h;
}

function renderItem(view){
  if(!view || !view.item){ finish((view||{}).summary); return; }
  i = view.position || 0;
  total = view.total || 0;
  document.getElementById("pos").textContent = i + 1;
  document.getElementById("tot").textContent = total;
  document.getElementById("ok").textContent = score;
  document.getElementById("rail").style.width =
    (total ? (i/total*100) : 0) + "%";
  shownAt = performance.now();
  const q = view.item;
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
  setStatus("");
}

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
  function revert(){ shown.forEach(o=>{ btns[o.key].disabled = false; }); }
  function go(){
    shown.forEach(o=>{ btns[o.key].disabled = true; });
    if(submit) submit.remove();
    settle(q, multi ? picked.slice() : picked[0], card, act, paint, revert);
  }
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
  function revert(){
    rows.forEach(r=>segs[String(r.id)].forEach(b=>{ b.disabled = false; }));
  }
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
    }, revert);
  };
}

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
  function revert(){ shown.forEach((s,n)=>{ btns[n].disabled = false; }); }
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
    }, revert);
  };
}

function asShort(q, body, act, card){
  const ta = document.createElement("textarea");
  ta.className = "ans";
  ta.placeholder = "Type your answer. Complete sentences; this is marked on what you actually wrote.";
  body.appendChild(ta);
  const submit = mkSubmit(act, "your own words, no notes");
  ta.oninput = ()=>{ submit.disabled = ta.value.trim().length < 2; };
  ta.focus();
  function revert(){ ta.disabled = false; }
  submit.onclick = ()=>{
    ta.disabled = true;
    submit.remove();
    settle(q, ta.value.trim(), card, act, null, revert);
  };
}

function mkSubmit(act, hint){
  const b = document.createElement("button");
  b.className="go"; b.type="button"; b.textContent="Check"; b.disabled=true;
  const h = document.createElement("span"); h.className="hint"; h.textContent=hint;
  act.appendChild(b); act.appendChild(h);
  return b;
}

function close(q, card, act, v){
  const ex = v.explain || {};
  const right = v.score;
  const pending = (right === null || right === undefined);
  if(!pending){ autoTotal++; if(right){ score++; } else { miss.push({q, ex}); } }
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
        held back so it cannot contaminate the items after this one. It is in the bank file
        and in the attempt file next to what you wrote.</div>`;
    }
  } else {
    if(!v.skipWhy) h += blk("Why this is best", ex.why);
    h += blk("Key discriminator", ex.disc);
    h += blk("Second best", ex.second);
    if(ex.notes && ex.notes.length) h += `<div class="blk"><h4>Notes</h4><ul><li>`
      + ex.notes.map(esc).join("</li><li>") + `</li></ul></div>`;
  }
  if(ex.trap) h += `<div class="blk trap"><h4>Trap</h4><div>${esc(ex.trap)}</div></div>`;
  exp.innerHTML = h;
  card.appendChild(exp);
  const next = document.createElement("button");
  next.className = "go"; next.type = "button";
  const nxt = v.next || {};
  if(nxt.item){
    next.textContent = "Next";
    next.onclick = ()=>{ renderItem(nxt); };
  } else {
    next.textContent = "View summary";
    next.onclick = ()=>{ finish(nxt.summary || {}); };
  }
  act.appendChild(next);
  next.focus();
}

/* ---- results: the summary is the server's session summary ----------------- */
function finish(summary){
  const s = summary || {};
  const auto = s.auto_attempts || 0;
  const correct = s.auto_correct || 0;
  const pend = s.pending_manual || 0;
  const pct = auto ? Math.round(correct/auto*100) : 0;
  document.getElementById("rail").style.width = "100%";
  let h = `<div class="done"><div class="score mono">${correct}/${auto}
    <span style="font-size:17px;color:var(--mut)"> &middot; ${pct}% auto-marked</span></div>`;
  if(pend) h += `<p style="margin:12px 0 0;color:var(--warn)"><b>${pend} short
    answer${pend>1?"s":""} not marked here.</b> They are in the attempt file,
    waiting for a marker.</p>`;
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
  setStatus("");
  window.scrollTo({top:0, behavior:"smooth"});
}

/* ---- start: one /api/start call bootstraps the whole sitting -------------- */
async function start(){
  setStatus("Loading…");
  try {
    const view = await api("/api/start",
      {bank: BOOT.bank, count: BOOT.count, mode: BOOT.mode});
    sessionId = view.session_id;
    renderItem(view);
  } catch(err){
    setStatus("Couldn't load this session. Try again.");
    host.innerHTML = "";
    const b = document.createElement("button");
    b.className = "go"; b.type = "button"; b.textContent = "Try again";
    b.onclick = ()=>{ host.innerHTML = ""; start(); };
    host.appendChild(b);
    b.focus();
  }
}

if(BOOT && BOOT.bank){ start(); }
"""
