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

Both clients share the Phase 4 question hierarchy (D-01 through D-03): one
sticky context line (bank/lesson context, objective, item N of M, session
mode), one native details disclosure for secondary metadata, a single
dominant stem h1, native response controls, a reserved feedback region, and
one primary next action per state.
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
.mono{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  font-variant-numeric:tabular-nums}
/* The one sticky orientation line (D-01): bank/lesson context, objective,
   item N of M, session mode -- and nothing else persistent. */
.context-line{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;
  gap:4px 18px;align-items:center;background:var(--bg);padding:8px 0 10px;
  border-bottom:1px solid var(--line);margin-bottom:14px;font-size:12.5px;
  color:var(--mut)}
.context-line .objective{flex:1 1 220px;min-width:0;overflow-wrap:anywhere}
.context-line .lesson{margin-left:auto}
.context-line a.lesson{color:var(--accent);text-decoration:none;font-weight:600}
.context-line a.lesson:hover,.context-line a.lesson:focus-visible{
  text-decoration:underline;outline:2px solid var(--accent);outline-offset:2px}
/* One native disclosure owns all secondary metadata (D-01). */
.session-details{margin:0 0 14px;font-size:13px;color:var(--mut)}
.session-details summary{cursor:pointer;padding:4px 0;font-size:11px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--mut);
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.session-details summary:focus-visible{outline:2px solid var(--accent);
  outline-offset:2px}
.detail-body{margin-top:8px;display:flex;flex-wrap:wrap;gap:7px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:18px 18px 16px;margin-bottom:14px}
.chip{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;
  background:var(--chip);color:var(--mut);padding:3px 8px;border-radius:5px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.chip.type{background:var(--accent-soft);color:var(--accent)}
.chip.aon{background:var(--bad-bg);color:var(--bad)}
.chip.lesson{background:var(--accent-soft);color:var(--accent);
  text-decoration:none;display:inline-block}
/* The active stem is the page's single dominant h1 (D-02). */
h1.stem{font-size:28px;font-weight:600;line-height:1.2;margin:0 0 14px;
  text-wrap:pretty}
/* Response controls: native inputs with a 44px target (D-03). */
.choices{display:flex;flex-direction:column;gap:7px;border:0;padding:0;
  margin:0 0 6px}
.choices legend{font-size:12.5px;color:var(--mut);margin-bottom:6px}
.choice{display:flex;gap:10px;align-items:center;min-height:44px;width:100%;
  text-align:left;background:var(--card);border:1px solid var(--line);
  border-radius:9px;padding:10px 12px;font:inherit;color:inherit;cursor:pointer;
  transition:.12s}
.choice:hover:not(:disabled){border-color:var(--accent)}
.choice:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:2px}
.choice input{width:20px;height:20px;flex:0 0 auto;accent-color:var(--accent)}
.choice input:disabled{cursor:default}
.choice .k{flex:0 0 auto;font-family:ui-monospace,Menlo,Consolas,monospace;
  font-size:13px;color:var(--mut);min-width:1.2em}
.choice .ot{flex:1 1 auto;min-width:0}
.choice .rat{display:block;margin-top:6px;font-size:12.5px;line-height:1.5;
  color:var(--mut)}
.choice.right{background:var(--ok-bg);border-color:var(--ok)}
.choice.right .rat{color:var(--ok)}
.choice.wrong{background:var(--bad-bg);border-color:var(--bad)}
.choice.wrong .rat{color:var(--bad)}
.choice:has(input:checked){border-color:var(--accent);background:var(--accent-soft)}
.choice:has(input:checked).right{border-color:var(--ok);background:var(--ok-bg)}
.choice:has(input:checked).wrong{border-color:var(--bad);background:var(--bad-bg)}
.opts{display:flex;flex-direction:column;gap:7px}
.opt{display:flex;gap:10px;align-items:center;min-height:44px;width:100%;
  text-align:left;background:var(--card);border:1px solid var(--line);
  border-radius:9px;padding:10px 12px;font:inherit;color:inherit;cursor:pointer;
  transition:.12s}
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
.seg button{font:inherit;font-size:13.5px;padding:8px 12px;min-height:44px;
  border-radius:7px;border:1px solid var(--line);background:var(--card);
  color:inherit;cursor:pointer}
.seg button[aria-pressed="true"]{border-color:var(--accent);
  background:var(--accent-soft);color:var(--accent)}
.seg button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.seg button.right{border-color:var(--ok);background:var(--ok-bg);color:var(--ok)}
.seg button.wrong{border-color:var(--bad);background:var(--bad-bg);color:var(--bad)}
.ord{flex:0 0 auto;width:26px;height:26px;border-radius:50%;display:grid;
  place-items:center;font-family:ui-monospace,Menlo,monospace;font-size:12.5px;
  border:1px solid var(--line);color:var(--mut)}
.ord.set{background:var(--accent);border-color:var(--accent);color:#fff}
/* Reserved feedback region: directly below the response control, before the
   next action, with stable minimum height so the stem never shifts (D-02). */
.feedback{min-height:96px;margin-top:14px;padding-top:12px;
  border-top:1px solid var(--line);font-size:14.5px}
.feedback .status{color:var(--mut);margin-bottom:8px}
.act{margin-top:13px;display:flex;gap:9px;align-items:center;flex-wrap:wrap}
button.go{font:inherit;font-weight:600;font-size:14.5px;padding:11px 17px;
  min-height:44px;min-width:44px;border:0;border-radius:9px;
  background:var(--accent);color:#fff;cursor:pointer}
button.go:disabled{opacity:.4;cursor:default}
button.go:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
button.ghost{background:var(--card);color:var(--ink);border:1px solid var(--line)}
.hint{font-size:12.5px;color:var(--mut)}
.exp h4{margin:0 0 5px;font-size:11px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--mut);font-family:ui-monospace,Menlo,Consolas,monospace}
.exp .blk{margin-bottom:11px}
.exp ul{margin:5px 0 0;padding-left:18px}
.exp li{margin-bottom:4px}
.verdict{font-weight:600;margin-bottom:10px}
.verdict.y{color:var(--ok)} .verdict.n{color:var(--bad)}
.pend{color:var(--warn);font-weight:600;margin-bottom:10px}
.trap{background:var(--accent-soft);border-left:3px solid var(--accent);
  padding:9px 12px;border-radius:0 7px 7px 0}
textarea.ans{width:100%;min-height:150px;padding:11px 12px;border-radius:9px;
  border:1px solid var(--line);background:var(--card);color:inherit;
  font:inherit;font-size:15.5px;line-height:1.5;resize:vertical}
textarea.ans:focus{outline:2px solid var(--accent);outline-offset:1px;
  border-color:var(--accent)}
textarea.ans:disabled{opacity:.75}
.done{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:20px}
.score{font-size:34px;font-weight:700;letter-spacing:-.02em}
.empty{text-align:center;padding:28px 10px}
@media (max-width:767px){
  .wrap{max-width:100%;padding:18px 16px 80px}
  .context-line{gap:2px 12px}
  h1.stem{font-size:20px}
  .feedback{min-height:120px}
}
@media (prefers-reduced-motion:reduce){
  *{transition:none!important}
  html{scroll-behavior:auto!important}
}
</style></head><body><div class="wrap">
<nav class="context-line" data-surface-context aria-label="Session context">
  <span class="cx" id="cx-bank">__CTX_BANK__</span>
  <span class="cx objective" id="cx-objective"></span>
  <span class="cx mono">Item <b id="pos">1</b> of <b id="tot">0</b></span>
  <span class="cx mode" id="cx-mode">__CTX_MODE__</span>
  <span class="cx lesson" id="cx-lesson"></span>
</nav>
<details class="session-details">
  <summary>Session details</summary>
  <div id="detail-body" class="detail-body"></div>
</details>
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
const LESSON_LABEL = "__LESSON_LABEL__";
const LETTERS = "ABCDEFGH";
const LABEL = {mc:"multiple choice", multi:"multiple response",
               table:"options table", build:"build list", dnd:"drag-and-drop",
               short:"short answer"};
const FS = "\u001f", PS = "\u001e";   /* must match FIELD_SEP and PAIR_SEP */
const REDUCED = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
let i = 0, score = 0, autoTotal = 0;
let shownAt = performance.now();
const miss = [];
const host = document.getElementById("host");
const cxObjective = document.getElementById("cx-objective");
const cxLesson = document.getElementById("cx-lesson");
const detailBody = document.getElementById("detail-body");
const esc = s => (s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

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

function lessonChip(q){
  /* D-12: no chip when no reader sits behind the page, or when the slug does
     not resolve (--force). */
  if(!(q.lesson_slug && LESSON_BASE)) return "";
  return `<a class="chip lesson" href="${LESSON_BASE}#${q.lesson_slug}"
          target="_blank" rel="noopener">${LESSON_LABEL}</a>`;
}

function metaChips(q){
  let h = `<span class="chip type">${LABEL[q.type]||q.type}</span>`;
  if(q.type==="short") h += `<span class="chip aon">graded by a marker, not by this page</span>`;
  else if(q.type!=="mc") h += `<span class="chip aon">no partial credit</span>`;
  if(q.difficulty) h += `<span class="chip">${esc(q.difficulty)}</span>`;
  h += `<span class="chip aon">dichotomous scoring</span>`;
  return h;
}

function setContext(q){
  if(cxObjective) cxObjective.textContent = q.objective || "";
  if(cxLesson) cxLesson.innerHTML = lessonChip(q);
  if(detailBody) detailBody.innerHTML = metaChips(q);
}

function feedbackFor(card){
  let fb = card.querySelector(".feedback");
  if(!fb){
    fb = document.createElement("div");
    fb.className = "feedback";
    fb.setAttribute("role", "status");
    fb.setAttribute("aria-live", "polite");
    card.appendChild(fb);
  }
  return fb;
}

async function settle(q, response, card, act, paint){
  const fb = feedbackFor(card);
  fb.innerHTML = `<div class="status">Checking answer&hellip;</div>`;
  let v;
  try {
    v = await verify(q, response);
  } catch(err){
    fb.innerHTML = `<div class="status">Could not reach the process that scores and records
      this sitting (${esc(err.message)}). This answer was not saved and was not marked.
      Restart itembank and sit it again.</div>`;
    return;
  }
  if(paint) paint(v);
  close(q, card, act, v);
}

function shuffled(a){const b=a.slice();for(let j=b.length-1;j>0;j--){
  const k=Math.floor(Math.random()*(j+1));[b[j],b[k]]=[b[k],b[j]];}return b;}

function render(){
  document.getElementById("pos").textContent = Math.min(i+1, Q.length);
  document.getElementById("tot").textContent = Q.length;
  if(i>=Q.length) return finish();
  shownAt = performance.now();
  const q = Q[i];
  setContext(q);
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `<h1 class="stem">${esc(q.stem)}</h1>`;
  const body = document.createElement("div");
  card.appendChild(body);
  const fb = document.createElement("div");
  fb.className = "feedback";
  fb.setAttribute("role", "status");
  fb.setAttribute("aria-live", "polite");
  card.appendChild(fb);
  const act = document.createElement("div");
  act.className = "act";
  card.appendChild(act);
  host.innerHTML = "";
  host.appendChild(card);
  ({mc:asChoice, multi:asChoice, table:asAssign, dnd:asAssign, build:asBuild,
    short:asShort}[q.type])(q, body, act, card);
  card.scrollIntoView({block:"start", behavior: REDUCED ? "auto" : "smooth"});
}

/* ---- multiple choice (native radio) + multiple response (native checkboxes) */
const PINNED = /^\s*(all|none)\s+of\s+the\s+above|^\s*both\s+[A-H]\s+and\s+[A-H]/i;

function asChoice(q, body, act, card){
  const multi = q.type === "multi";
  const want = q.response_schema.select;
  const free = q.options.filter(o=>!PINNED.test(o.text));
  const pins = q.options.filter(o=> PINNED.test(o.text));
  const shown = shuffled(free).concat(pins);
  shown.forEach((o,n)=> o.label = LETTERS[n]);

  const fieldset = document.createElement("fieldset");
  fieldset.className = "choices";
  const legend = document.createElement("legend");
  legend.textContent = multi ? `Select ${want}` : "Choose one";
  fieldset.appendChild(legend);
  const picked = [];       // holds ORIGINAL keys
  const boxes = {};
  let submit = null;
  shown.forEach(o=>{
    const label = document.createElement("label");
    label.className = "choice";
    const input = document.createElement("input");
    input.type = multi ? "checkbox" : "radio";
    input.name = "answer";
    input.value = o.key;
    const k = document.createElement("span");
    k.className = "k"; k.textContent = o.label;
    const ot = document.createElement("span");
    ot.className = "ot"; ot.innerHTML = esc(o.text);
    label.append(input, k, ot);
    input.onchange = ()=>{
      if(!multi){
        picked.length = 0; picked.push(o.key);
        if(submit) submit.disabled = false;
        return;
      }
      if(input.checked){
        if(picked.length >= want){ input.checked = false; return; }
        picked.push(o.key);
      } else {
        const at = picked.indexOf(o.key);
        if(at >= 0) picked.splice(at, 1);
      }
      if(submit) submit.disabled = picked.length !== want;
    };
    boxes[o.key] = {label, input};
    fieldset.appendChild(label);
  });
  body.appendChild(fieldset);
  submit = mkSubmit(act, multi ? `select ${want}` : "choose one");
  submit.disabled = multi;
  submit.onclick = go;
  function revert(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = false; });
    if(!multi) submit.disabled = false;
  }
  function go(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = true; });
    if(submit) submit.remove();
    settle(q, multi ? picked.slice() : picked[0], card, act, paint);
  }
  function paint(v){
    const ex = v.explain || {};
    const correct = ex.correct || [];
    const sole = correct.length === 1 ? correct[0] : null;
    shown.forEach(o=>{
      const {label, input} = boxes[o.key];
      if(correct.includes(o.key)) label.classList.add("right");
      else if(picked.includes(o.key)) label.classList.add("wrong");
      const line = (o.key === sole && ex.why) ? ex.why : ((ex.da||{})[o.key] || "");
      if(line){
        const r = document.createElement("span");
        r.className = "rat";
        r.textContent = line;      // textContent, so a bank cannot inject markup
        label.querySelector(".ot").appendChild(r);
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

/* ---- short answer --------------------------------------------------------- */
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
  b.className="go"; b.type="button"; b.textContent="Submit answer"; b.disabled=true;
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
  const fb = feedbackFor(card);
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
        held back so it cannot contaminate the items after this one. It is in the bank file.`;
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
  fb.innerHTML = "";
  fb.appendChild(exp);
  const next = document.createElement("button");
  next.className="go"; next.type="button";
  next.textContent = (i===Q.length-1) ? "See results" : "Next";
  next.onclick = ()=>{ i++; render(); };
  act.appendChild(next);
  next.focus();
}

function finish(){
  document.getElementById("rail") && (document.getElementById("rail").style.width = "100%");
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
  window.scrollTo({top:0, behavior: REDUCED ? "auto" : "smooth"});
}

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
const LESSON_LABEL = "__LESSON_LABEL__";
const LETTERS = "ABCDEFGH";
const LABEL = {mc:"multiple choice", multi:"multiple response",
               table:"options table", build:"build list", dnd:"drag-and-drop",
               short:"short answer"};
const FS = "\u001f", PS = "\u001e";   /* must match FIELD_SEP and PAIR_SEP */
const REDUCED = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
let sessionId = null, i = 0, total = 0, score = 0, autoTotal = 0;
let shownAt = performance.now();
const miss = [];
const host = document.getElementById("host");
const cxObjective = document.getElementById("cx-objective");
const cxLesson = document.getElementById("cx-lesson");
const detailBody = document.getElementById("detail-body");
const esc = s => (s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

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
  return {action: v.action, score: v.score, explain: v.explain || {},
          hint_tier: v.hint_tier, next: v.next};
}

async function hintFor(q, card, act, stumped){
  const fb = feedbackFor(card);
  fb.innerHTML = `<div class="status">Revealing the next hint&hellip;</div>`;
  try {
    const v = await api("/api/hint", {session_id: sessionId, stumped: !!stumped});
    if(v.action !== "reveal_tier" || !v.hint) throw new Error("unexpected hint payload");
    renderLadder(card, v.hint);
    act.innerHTML = "";
    addHintControls(q, card, act);
    fb.innerHTML = `<div class="status">Hint shown. The card is still yours --
      answer again whenever you're ready.</div>`;
  } catch(err){
    fb.innerHTML = `<div class="status">Couldn't reveal a hint right now
      (${esc(err.message)}).</div>`;
    addHintControls(q, card, act);
  }
}

function addHintControls(q, card, act){
  const next = document.createElement("button");
  next.className = "go"; next.type = "button";
  next.textContent = "Show next hint";
  next.onclick = ()=>{ act.innerHTML = ""; hintFor(q, card, act, false); };
  act.appendChild(next);
  const stumped = document.createElement("button");
  stumped.className = "go ghost"; stumped.type = "button";
  stumped.textContent = "I'm stumped — show the next hint";
  stumped.onclick = ()=>{ act.innerHTML = ""; hintFor(q, card, act, true); };
  act.appendChild(stumped);
  next.focus();
}

function renderLadder(card, hint){
  const hostEl = card.querySelector(".ladder") ||
    (()=>{ const d = document.createElement("div");
           d.className = "ladder"; card.appendChild(d); return d; })();
  const tier = hint.tier;
  let h = `<h3 class="ladder-title">Hints</h3>`;
  const shown = hint.shown || [];
  for(let idx = 0; idx < 6; idx++){
    const isNew = tier && tier.index === idx;
    if(shown.indexOf(idx) >= 0 || isNew){
      const t = isNew ? tier : {name: ["lesson","objective","trap","rationale",
        "discriminator","reveal"][idx], available: true, content: ""};
      h += `<div class="tier tier-shown"><span class="tier-k">TIER ${idx}</span>
        <span class="tier-name">${esc(t.name)}</span>`;
      if(isNew){
        if(t.available){
          const content = typeof t.content === "string" ? esc(t.content)
            : (t.content && t.content.why ? esc(t.content.why) : "");
          h += `<div class="tier-body">${content}</div>`;
        } else {
          h += `<div class="tier-body mut">This tier has no authored content.</div>`;
        }
      } else {
        h += `<div class="tier-body mut">Already shown.</div>`;
      }
      h += `</div>`;
    } else {
      h += `<div class="tier tier-locked"><span class="tier-k">TIER ${idx}</span>
        <span class="tier-name">${esc(["lesson","objective","trap","rationale",
          "discriminator","reveal"][idx])}</span>
        <span class="tier-lock">Locked</span></div>`;
    }
  }
  hostEl.innerHTML = h;
}

function lessonChip(q){
  /* D-12: no chip when no reader sits behind the page, and no chip when the
     slug does not resolve to a served heading (--force). */
  if(!(q.lesson_slug && LESSON_BASE
       && (!BOOT.lesson_slugs || BOOT.lesson_slugs.indexOf(q.lesson_slug) >= 0)))
    return "";
  return `<a class="chip lesson" href="${LESSON_BASE}#${q.lesson_slug}"
          target="_blank" rel="noopener">${LESSON_LABEL}</a>`;
}

function metaChips(q){
  let h = `<span class="chip type">${LABEL[q.type]||q.type}</span>`;
  if(q.type==="short") h += `<span class="chip aon">graded by a marker, not by this page</span>`;
  else if(q.type!=="mc") h += `<span class="chip aon">no partial credit</span>`;
  if(q.difficulty) h += `<span class="chip">${esc(q.difficulty)}</span>`;
  h += `<span class="chip aon">dichotomous scoring</span>`;
  return h;
}

function setContext(q){
  if(cxObjective) cxObjective.textContent = q.objective || "";
  if(cxLesson) cxLesson.innerHTML = lessonChip(q);
  if(detailBody) detailBody.innerHTML = metaChips(q);
}

function feedbackFor(card){
  let fb = card.querySelector(".feedback");
  if(!fb){
    fb = document.createElement("div");
    fb.className = "feedback";
    fb.setAttribute("role", "status");
    fb.setAttribute("aria-live", "polite");
    card.appendChild(fb);
  }
  return fb;
}

async function settle(q, response, card, act, paint, revert){
  const fb = feedbackFor(card);
  fb.innerHTML = `<div class="status">Checking answer&hellip;</div>`;
  try {
    const v = await verify(q, response);
    if(paint) paint(v);
    close(q, card, act, v, revert);
  } catch(err){
    /* API failure: keep the current item and the entered response visible,
       offer a retry, and never manufacture a verdict the server did not issue. */
    fb.innerHTML = `<div class="status">Couldn't check that answer. Your selection
      is still here.</div>`;
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

function renderItem(view){
  if(!view || !view.item){
    if(view && view.summary){ finish(view.summary); return; }
    emptyState();
    return;
  }
  i = view.position || 0;
  total = view.total || 0;
  document.getElementById("pos").textContent = i + 1;
  document.getElementById("tot").textContent = total;
  shownAt = performance.now();
  const q = view.item;
  setContext(q);
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `<h1 class="stem">${esc(q.stem)}</h1>`;
  const body = document.createElement("div");
  card.appendChild(body);
  const fb = document.createElement("div");
  fb.className = "feedback";
  fb.setAttribute("role", "status");
  fb.setAttribute("aria-live", "polite");
  card.appendChild(fb);
  const act = document.createElement("div");
  act.className = "act";
  card.appendChild(act);
  host.innerHTML = "";
  host.appendChild(card);
  ({mc:asChoice, multi:asChoice, table:asAssign, dnd:asAssign, build:asBuild,
    short:asShort}[q.type])(q, body, act, card);
  /* Restore focus to the first meaningful control of the new item. */
  const first = card.querySelector("input, button, textarea");
  if(first && !REDUCED) first.focus({preventScroll:true});
  card.scrollIntoView({block:"start", behavior: REDUCED ? "auto" : "smooth"});
}

/* ---- multiple choice (native radio) + multiple response (native checkboxes) */
const PINNED = /^\s*(all|none)\s+of\s+the\s+above|^\s*both\s+[A-H]\s+and\s+[A-H]/i;

function asChoice(q, body, act, card){
  const multi = q.type === "multi";
  const want = q.response_schema.select;
  const free = q.options.filter(o=>!PINNED.test(o.text));
  const pins = q.options.filter(o=> PINNED.test(o.text));
  const shown = shuffled(free).concat(pins);
  shown.forEach((o,n)=> o.label = LETTERS[n]);

  const fieldset = document.createElement("fieldset");
  fieldset.className = "choices";
  const legend = document.createElement("legend");
  legend.textContent = multi ? `Select ${want}` : "Choose one";
  fieldset.appendChild(legend);
  const picked = [];       // holds ORIGINAL keys
  const boxes = {};
  let submit = null;
  shown.forEach(o=>{
    const label = document.createElement("label");
    label.className = "choice";
    const input = document.createElement("input");
    input.type = multi ? "checkbox" : "radio";
    input.name = "answer";
    input.value = o.key;
    const k = document.createElement("span");
    k.className = "k"; k.textContent = o.label;
    const ot = document.createElement("span");
    ot.className = "ot"; ot.innerHTML = esc(o.text);
    label.append(input, k, ot);
    input.onchange = ()=>{
      if(!multi){
        picked.length = 0; picked.push(o.key);
        if(submit) submit.disabled = false;
        return;
      }
      if(input.checked){
        if(picked.length >= want){ input.checked = false; return; }
        picked.push(o.key);
      } else {
        const at = picked.indexOf(o.key);
        if(at >= 0) picked.splice(at, 1);
      }
      if(submit) submit.disabled = picked.length !== want;
    };
    boxes[o.key] = {label, input};
    fieldset.appendChild(label);
  });
  body.appendChild(fieldset);
  submit = mkSubmit(act, multi ? `select ${want}` : "choose one");
  submit.disabled = multi;
  submit.onclick = go;
  function revert(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = false; });
    if(!multi) submit.disabled = false;
  }
  function go(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = true; });
    if(submit) submit.remove();
    settle(q, multi ? picked.slice() : picked[0], card, act, paint, revert);
  }
  function paint(v){
    const ex = v.explain || {};
    const correct = ex.correct || [];
    const sole = correct.length === 1 ? correct[0] : null;
    shown.forEach(o=>{
      const {label, input} = boxes[o.key];
      if(correct.includes(o.key)) label.classList.add("right");
      else if(picked.includes(o.key)) label.classList.add("wrong");
      const line = (o.key === sole && ex.why) ? ex.why : ((ex.da||{})[o.key] || "");
      if(line){
        const r = document.createElement("span");
        r.className = "rat";
        r.textContent = line;      // textContent, so a bank cannot inject markup
        label.querySelector(".ot").appendChild(r);
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
  b.className="go"; b.type="button"; b.textContent="Submit answer"; b.disabled=true;
  const h = document.createElement("span"); h.className="hint"; h.textContent=hint;
  act.appendChild(b); act.appendChild(h);
  return b;
}

function close(q, card, act, v, revert){
  const ex = v.explain || {};
  const right = v.score;
  const pending = (right === null || right === undefined);
  act.innerHTML = "";
  const fb = feedbackFor(card);
  if(v.action === "hold"){
    if(revert) revert();
    fb.innerHTML = `<div class="verdict n">Not correct yet — the card stays
      open. A hint is available.</div>`;
    addHintControls(q, card, act);
    return;
  }
  if(v.action === "defer_feedback"){
    fb.innerHTML = `<div class="pend">Recorded. ${q.type === "short"
      ? "Not marked here — a human marker reviews it." : ""}</div>`;
    if(q.type === "short") addHintControls(q, card, act);
    return;
  }
  if(v.action === "reveal_tier"){
    if(revert) revert();
    renderLadder(card, v.hint || {tier: null, shown: []});
    addHintControls(q, card, act);
    return;
  }
  /* advance / complete: the runtime released the verdict and explanation. */
  if(!pending){ autoTotal++; if(right){ score++; } else { miss.push({q, ex}); } }
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
  fb.innerHTML = "";
  fb.appendChild(exp);
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
  const report = "/report?session=" + encodeURIComponent(sessionId || "");
  const auto = s.auto_attempts || 0;
  const correct = s.auto_correct || 0;
  const pend = s.pending_manual || 0;
  const pct = auto ? Math.round(correct/auto*100) : 0;
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
  h += `<div class="act"><a class="go ghost" style="text-decoration:none"
        href="${report}">View report</a></div></div>`;
  host.innerHTML = h;
  window.scrollTo({top:0, behavior: REDUCED ? "auto" : "smooth"});
}

/* ---- empty session: no item to show --------------------------------------- */
function emptyState(){
  const report = "/report?session=" + encodeURIComponent(sessionId || "");
  host.innerHTML = `<div class="done empty">
    <p><b>This session has no question ready.</b></p>
    <p style="color:var(--mut)">No items match this sitting&rsquo;s filters or
      the bank has nothing to serve.</p>
    <div class="act"><a class="go ghost" style="text-decoration:none"
          href="${report}">View report</a>
      <a class="go ghost" style="text-decoration:none"
          href="/settings">Filters / settings</a></div>
  </div>`;
}

/* ---- start: one /api/start call bootstraps the whole sitting -------------- */
async function start(){
  host.innerHTML = `<div class="card"><div class="feedback" role="status"
      aria-live="polite"><div class="status">Loading&hellip;</div></div></div>`;
  try {
    /* D-09: a #<item-id> fragment (lesson backlink) asks the server to start
       with that item first; unknown ids degrade to normal order server-side. */
    const payload = {bank: BOOT.bank, count: BOOT.count, mode: BOOT.mode};
    const frag = location.hash.replace(/^#/, "");
    if(frag) payload.focus = frag;
    const view = await api("/api/start", payload);
    sessionId = view.session_id;
    renderItem(view);
  } catch(err){
    host.innerHTML = `<div class="done empty">
      <p><b>This session has no question ready.</b></p>
      <p style="color:var(--mut)">Couldn't load this session (${esc(err.message)}).
        Your bank is still here; try again.</p>
      <div class="act"><button class="go" type="button" id="retry">Try again</button></div>
    </div>`;
    const b = document.getElementById("retry");
    b.onclick = ()=>{ start(); };
    b.focus();
  }
}

if(BOOT && BOOT.bank){ start(); }
"""
