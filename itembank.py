#!/usr/bin/env python3
"""itembank: author, validate and render exam-style question banks in markdown.

Built because a prose format spec does not fail loudly. An AI handed a prompt
template can conform to it or not with no way to tell which, so banks go
silently malformed and nobody notices until a renderer reports the wrong item
count. The fix is a machine-checkable contract: `itembank spec` tells an
authoring agent the format, `itembank lint` tells it exactly what it got wrong.

  itembank spec                 print the format contract (the AI-facing entry point)
  itembank lint  BANK.md        validate; errors exit non-zero, warnings advise
  itembank build BANK.md [OUT]  self-contained offline HTML quiz; saves nothing
  itembank serve BANK.md        sit it locally, every answer written to an attempt file
  itembank stats BANK.md        item mix, objective coverage, answer-position skew
  itembank start BANK.md        start a resumable, agent-readable assessment
  itembank next SESSION.json    return the next item without its answer key
  itembank submit SESSION.json  score the current response and advance the session
  itembank report SESSION.json  summarize the recorded evidence
  itembank guard [DIR]          fail if a real question bank was committed

Scoring is dichotomous on every item type, matching the NREMT rule that no
credit is given for a partially correct response. A half mark hides the gap the
item exists to find.

Python standard library only. No network, no services, no dependencies.
"""
import sys, re, json, os, html, argparse, collections

LETTERS = "ABCDEFGH"



def grab(pattern, block, flags=0):
    m = re.search(pattern, block, flags)
    return m.group(1).strip() if m else ""


def parse_bank(text):
    """Split on `Qn.` markers and parse each block into a question dict."""
    questions = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if not re.match(r"Q\d+\.", ch.strip()):
            continue
        q = parse_question(ch)
        if q:
            questions.append(q)
    return questions


def parse_question(ch):
    number = grab(r"Q(\d+)\.", ch)
    qtype = (grab(r"(?m)^\[TYPE:\s*(\w+)\s*\]", ch) or "mc").lower()
    # Stem runs from the Qn. marker to the first structural marker that follows.
    stem = grab(
        r"Q\d+\.\s*(.*?)\s*(?:\(difficulty:|\n\[OBJECTIVE|\n\[TYPE|\n\[SELECT"
        r"|\n\[CATEGORIES|\n[A-H]\)|\nROW\)|\nITEM\)|\nSTEP\)|\nMODEL:|\nRUBRIC:"
        r"|\nWHY BEST:)",
        ch, re.S)
    common = {
        "id": "q" + number if number else "",
        "number": int(number) if number else 0,
        "type": qtype,
        "stem": stem,
        "difficulty": grab(r"\(difficulty:\s*([^)]+)\)", ch),
        "objective": grab(r"\[OBJECTIVE:\s*(.*?)\]", ch),
        "why": section("WHY BEST", ch),
        "disc": section("KEY DISCRIMINATOR", ch),
        "second": section("SECOND-BEST", ch),
        "trap": section("TRAP", ch),
        "conf": grab(r"(?m)^CONFIDENCE:\s*(.*?)\s*(?=\n|\Z)", ch),
    }

    if qtype in ("mc", "multi"):
        opts = {}
        for L in LETTERS:
            v = grab(rf"(?m)^{L}\)\s*(.*?)\s*(?=^[A-H]\)|^CORRECT:|\n\n)", ch, re.S)
            if v:
                opts[L] = v
        correct = [c.strip().upper() for c in
                   re.split(r"[,\s]+", grab(r"(?m)^CORRECT:\s*(.*?)\s*$", ch)) if c.strip()]
        correct = [c for c in correct if c in LETTERS]
        if not (stem and opts and correct):
            return None
        da = {}
        for L in LETTERS:
            da[L] = grab(rf"(?m)^-\s*{L}\)\s*(.*?)\s*(?=^-\s*[A-H]\)|^TRAP:|^CONFIDENCE:|\Z)",
                         ch, re.S)
        sel = grab(r"(?m)^\[SELECT:\s*(\d+)\s*\]", ch)
        common.update({
            "opts": opts, "correct": correct, "da": da,
            "select": int(sel) if sel else len(correct),
        })
        return common

    if qtype in ("table", "dnd"):
        cats = [c.strip() for c in grab(r"(?m)^\[CATEGORIES:\s*(.*?)\s*\]", ch).split("|") if c.strip()]
        marker = "ROW" if qtype == "table" else "ITEM"
        rows = []
        for line in re.findall(rf"(?m)^{marker}\)\s*(.+?)\s*$", ch):
            if "::" not in line:
                continue
            t, c = line.rsplit("::", 1)
            rows.append({"text": t.strip(), "cat": c.strip()})
        if not (stem and cats and rows):
            return None
        common.update({"cats": cats, "rows": rows, "notes": notes(ch)})
        return common

    if qtype == "build":
        steps = [s.strip() for s in re.findall(r"(?m)^STEP\)\s*(.+?)\s*$", ch)]
        if not (stem and len(steps) > 1):
            return None
        common.update({"steps": steps, "notes": notes(ch)})
        return common

    if qtype == "short":
        # Constructed response. Nothing here is machine-gradable by design: the
        # rubric is for whoever marks it, and RUBRIC points are what they mark
        # against, so "wrote something plausible" cannot pass as understanding.
        model = section("MODEL", ch)
        rubric = [b.strip() for b in re.findall(
            r"(?m)^-\s*(.+?)\s*$",
            grab(r"(?m)^RUBRIC:\s*(.*?)\s*(?=^[A-Z][A-Z \-]+:|\Z)", ch, re.S))]
        if not stem:
            return None
        common.update({"model": model, "rubric": rubric, "notes": notes(ch)})
        return common

    return None


def section(label, ch):
    return grab(rf"(?m)^{label}:\s*(.*?)\s*(?=\n[A-Z][A-Z \-]+:|\nDISTRACTOR|\Z)", ch, re.S)


def notes(ch):
    """Free-form bullets under DISTRACTOR ANALYSIS, for the non-lettered types."""
    blk = grab(r"(?m)^DISTRACTOR ANALYSIS:\s*(.*?)\s*(?=^TRAP:|^CONFIDENCE:|\Z)", ch, re.S)
    return [b.strip() for b in re.findall(r"(?m)^-\s*(.+?)\s*$", blk)]


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{
  --bg:#f3f5f4; --card:#fff; --ink:#171d1c; --mut:#5f6d6a; --line:#dfe5e3;
  --accent:#0e6e62; --accent-soft:#e3efec;
  --ok:#1b7a3d; --ok-bg:#e8f4ec; --bad:#b4272b; --bad-bg:#fbebeb; --warn:#b5760a;
  --chip:#eef2f1;
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0e1413; --card:#161e1d; --ink:#e4ebe9; --mut:#8fa19d; --line:#26312f;
    --accent:#34b3a0; --accent-soft:#13302c;
    --ok:#4fbf74; --ok-bg:#11291b; --bad:#f0666a; --bad-bg:#2b1416; --warn:#e0a23a;
    --chip:#1d2726;
  }
}
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
const RECORD = __RECORD__;   /* true only under `itembank serve` */
const REVEAL = __REVEAL__;   /* show model answers after a short item */
const LABEL = {mc:"multiple choice", multi:"multiple response",
               table:"options table", build:"build list", dnd:"drag-and-drop",
               short:"short answer"};
let i = 0, score = 0, autoTotal = 0;
const miss = [];
const LOG = [];              /* every response, in the order answered */
const host = document.getElementById("host");
const esc = s => (s==null?"":String(s));

/* ---- recording -------------------------------------------------------------
   Every answer is POSTed the moment it is given, not batched at the end, so a
   closed tab or a dead battery costs at most the item in progress. The server
   rewrites the whole attempt file each time, which makes the write idempotent
   and means a partial sitting is still a valid file. */
function record(entry){
  LOG.push(entry);
  if(!RECORD) return;
  const el = document.getElementById("savestate");
  fetch("/save", {method:"POST", headers:{"Content-Type":"application/json"},
                  body: JSON.stringify({answers: LOG, done: i>=Q.length})})
    .then(r => { el.textContent = r.ok ? "SAVED" : "SAVE FAILED";
                 el.className = r.ok ? "" : "bad"; })
    .catch(() => { el.textContent = "SAVE FAILED, server gone";
                   el.className = "bad"; });
}

function shuffled(a){const b=a.slice();for(let j=b.length-1;j>0;j--){
  const k=Math.floor(Math.random()*(j+1));[b[j],b[k]]=[b[k],b[j]];}return b;}

function same(a,b){return a.length===b.length && a.every(x=>b.includes(x));}

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
  const raw = Object.keys(q.opts).map(k=>({k, text:q.opts[k], da:q.da?q.da[k]:""}));
  const free = raw.filter(o=>!PINNED.test(o.text));
  const pins = raw.filter(o=> PINNED.test(o.text));
  const shown = shuffled(free).concat(pins);
  shown.forEach((o,n)=> o.label = LETTERS[n]);

  const picked = [];   // holds ORIGINAL keys; display letters are cosmetic
  const wrap = document.createElement("div");
  wrap.className = "opts";
  const btns = {};
  shown.forEach(o=>{
    const b = document.createElement("button");
    b.className = "opt"; b.type = "button"; b.setAttribute("aria-pressed","false");
    b.innerHTML = `<span class="k">${o.label}</span><span>${esc(o.text)}</span>`;
    b.onclick = ()=>{
      if(!multi){ picked.length=0; picked.push(o.k); grade(); return; }
      const at = picked.indexOf(o.k);
      if(at>=0) picked.splice(at,1);
      else if(picked.length < q.select) picked.push(o.k);
      shown.forEach(x=>btns[x.k].setAttribute("aria-pressed",
        picked.includes(x.k)?"true":"false"));
      submit.disabled = picked.length !== q.select;
    };
    btns[o.k]=b; wrap.appendChild(b);
  });
  body.appendChild(wrap);
  let submit;
  if(multi){
    submit = mkSubmit(act, `select ${q.select}`);
    submit.onclick = grade;
  }
  function grade(){
    const right = same(picked, q.correct);
    shown.forEach(o=>{
      btns[o.k].disabled = true;
      if(q.correct.includes(o.k)) btns[o.k].classList.add("right");
      else if(picked.includes(o.k)) btns[o.k].classList.add("wrong");
    });
    if(submit) submit.remove();
    // Re-label the analysis to the letters actually on screen this time.
    const lines = shown.filter(o=>o.da).map(o=>`<b>${o.label})</b> ${esc(o.da)}`);
    const given = picked.map(k=>(shown.find(o=>o.k===k)||{}).label).sort().join(", ");
    close(q, card, act, right, given, lines);
  }
}

/* ---- options table + drag-and-drop (assign each row to a category) -------- */
function asAssign(q, body, act, card){
  const rows = shuffled(q.rows);   // reshuffled every load, both table and dnd
  const chosen = new Array(rows.length).fill(null);
  const segs = [];
  rows.forEach((r, n)=>{
    const line = document.createElement("div");
    line.className = "rowline";
    const t = document.createElement("div");
    t.className = "rowtext"; t.textContent = r.text;
    const seg = document.createElement("div");
    seg.className = "seg";
    const bs = q.cats.map(c=>{
      const b = document.createElement("button");
      b.type="button"; b.textContent=c; b.setAttribute("aria-pressed","false");
      b.onclick = ()=>{
        chosen[n]=c;
        bs.forEach(x=>x.setAttribute("aria-pressed", x.textContent===c?"true":"false"));
        submit.disabled = chosen.includes(null);
      };
      seg.appendChild(b); return b;
    });
    segs.push(bs);
    line.appendChild(t); line.appendChild(seg); body.appendChild(line);
  });
  const submit = mkSubmit(act, "assign every row");
  submit.onclick = ()=>{
    const right = rows.every((r,n)=>chosen[n]===r.cat);
    rows.forEach((r,n)=>segs[n].forEach(b=>{
      b.disabled = true;
      if(b.textContent===r.cat) b.classList.add("right");
      else if(b.textContent===chosen[n]) b.classList.add("wrong");
    }));
    submit.remove();
    close(q, card, act, right, rows.map((r,n)=>`${r.text} -> ${chosen[n]}`).join("; "));
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
    const right = order.every((s,n)=>s===q.steps[n]);
    shown.forEach((s,n)=>{
      btns[n].disabled = true;
      btns[n].classList.add(order.indexOf(s)===q.steps.indexOf(s) ? "right" : "wrong");
      btns[n].querySelector(".ord").textContent = q.steps.indexOf(s)+1;
    });
    submit.remove();
    close(q, card, act, right, order.join(" > "));
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
    const text = ta.value.trim();
    record({n: i+1, type: "short", stem: q.stem, objective: q.objective || "",
            answer: text, correct: null, model: q.model || "", rubric: q.rubric || []});
    act.innerHTML = "";
    const exp = document.createElement("div");
    exp.className = "exp";
    let h = `<div class="pend">Recorded. Not marked here.</div>`;
    if(REVEAL && q.model){
      h += `<div class="blk"><h4>Model answer</h4><div>${esc(q.model)}</div></div>`;
      if(q.rubric && q.rubric.length)
        h += `<div class="blk"><h4>What a marker checks</h4><ul><li>`
           + q.rubric.map(esc).join("</li><li>") + `</li></ul></div>`;
    } else {
      h += `<div class="blk" style="color:var(--mut);font-size:13.5px">The model answer is
        held back so it cannot contaminate the items after this one. It is in the bank file,
        and in the attempt file next to what you wrote.</div>`;
    }
    if(q.trap && REVEAL)
      h += `<div class="blk trap"><h4>Trap</h4><div>${esc(q.trap)}</div></div>`;
    exp.innerHTML = h;
    card.appendChild(exp);
    const next = document.createElement("button");
    next.className="go"; next.type="button";
    next.textContent = (i===Q.length-1) ? "See results" : "Next";
    next.onclick = ()=>{ i++; render(); };
    act.appendChild(next);
    next.focus();
  };
}

function mkSubmit(act, hint){
  const b = document.createElement("button");
  b.className="go"; b.type="button"; b.textContent="Check"; b.disabled=true;
  const h = document.createElement("span"); h.className="hint"; h.textContent=hint;
  act.appendChild(b); act.appendChild(h);
  return b;
}

/* ---- reveal --------------------------------------------------------------- */
function close(q, card, act, right, given, daLines){
  autoTotal++;
  if(right) score++; else miss.push({q, given});
  record({n: i+1, type: q.type, stem: q.stem, objective: q.objective || "",
          answer: given, correct: right, model: "", rubric: []});
  act.innerHTML = "";
  const exp = document.createElement("div");
  exp.className = "exp";
  let h = `<div class="verdict ${right?"y":"n"}">${right?"Correct":"Not correct"}</div>`;
  const blk = (t,v)=> v ? `<div class="blk"><h4>${t}</h4><div>${esc(v)}</div></div>` : "";
  h += blk("Why this is best", q.why);
  h += blk("Key discriminator", q.disc);
  h += blk("Second best", q.second);
  // daLines arrives pre-labelled with this render's shuffled letters.
  const lines = daLines ? daLines.slice() : [];
  if(q.notes) q.notes.forEach(n=>lines.push(esc(n)));
  if(lines.length) h += `<div class="blk"><h4>Distractor analysis</h4><ul><li>`
    + lines.join("</li><li>") + `</li></ul></div>`;
  if(q.trap) h += `<div class="blk trap"><h4>Trap</h4><div>${esc(q.trap)}</div></div>`;
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
  record({n: 0, type: "__end__", stem: "", objective: "", answer: "",
          correct: null, model: "", rubric: []});
  const pct = autoTotal ? Math.round(score/autoTotal*100) : 0;
  const pend = Q.filter(q=>q.type==="short").length;
  let h = `<div class="done"><div class="score mono">${score}/${autoTotal}
    <span style="font-size:17px;color:var(--mut)"> &middot; ${pct}% auto-marked</span></div>`;
  if(pend) h += `<p style="margin:12px 0 0;color:var(--warn)"><b>${pend} short
    answer${pend>1?"s":""} not marked here.</b> ${RECORD
      ? "They are in the attempt file, waiting for a marker."
      : "Nothing recorded them, because this page was opened as a file. Use <code>itembank serve</code> for a sitting that is meant to be graded."}</p>`;
  if(miss.length){
    h += `<p style="margin:14px 0 6px"><b>${miss.length} to harvest.</b>
      Per Anki_Testing_Strategy &sect;2, the discriminator becomes the card, not the question.</p><ul>`;
    miss.forEach(m=>{
      h += `<li style="margin-bottom:9px"><b>${esc(m.q.stem.slice(0,110))}</b>`
        + (m.q.objective ? ` <span class="chip">${esc(m.q.objective)}</span>` : "")
        + (m.q.trap ? `<br><span style="color:var(--mut)">Trap: ${esc(m.q.trap)}</span>` : "")
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




SPEC = r"""itembank format contract
=========================

A bank is a markdown file. Everything that is not a question block is ignored,
so a bank can live inside a larger document with prose around it.

A question block starts at `Qn.` at the beginning of a line and runs to the next
one. Options A through H are supported.

SHARED FIELDS (all types)
  Qn. <stem>   (difficulty: recall|application|analysis)     difficulty optional
  [OBJECTIVE: <syllabus or blueprint reference>]             optional
  WHY BEST:            why the keyed answer is correct
  KEY DISCRIMINATOR:   the one distinction the item turns on
  SECOND-BEST:         the runner-up, and what would make it win
  DISTRACTOR ANALYSIS: see below
  TRAP:                the misconception this item weaponises
  CONFIDENCE:          high | medium | low

THE FIVE ITEM TYPES

1. Multiple choice.  Default. No TYPE line needed.
     A) ...  B) ...  C) ...  D) ...
     CORRECT: B

2. Multiple response.  Pick a fixed number from five or six.
     [TYPE: multi]
     [SELECT: 3]
     A) ... through F) ...
     CORRECT: A, C, E

3. Options table.  Classify each row into a named category.
     [TYPE: table]
     [CATEGORIES: Online | Offline]
     ROW) A protocol stating when to request backup :: Offline
     ROW) Calling the physician about a refusal :: Online

4. Build list.  Put options into a required order.
   List STEPs in the CORRECT order; the renderer shuffles them for display.
     [TYPE: build]
     STEP) Complete an approved education program
     STEP) Pass the certification examination

5. Drag-and-drop.  Sort items into buckets. Same shape as table, but display
   order is shuffled, because a table implies fixed rows and a sort does not.
     [TYPE: dnd]
     [CATEGORIES: Direct care | Readiness]
     ITEM) Assessing the airway :: Direct care

6. Short answer.  Constructed response, typed in prose. NOT auto-graded, ever:
   the answer is recorded and a human or an AI marks it against RUBRIC later.
   Use it where selecting from options would give the answer away, or where the
   skill being tested is producing the explanation rather than recognising it.
     [TYPE: short]
     MODEL:  the answer a full-credit response contains, compressed
     RUBRIC:
     - one checkable claim the answer must make
     - a second one; two is the minimum, because a single point is a vibe
   No WHY BEST is required on a short item; MODEL replaces it. TRAP still helps
   the marker, because it names the wrong answer that will look confident.

DISTRACTOR ANALYSIS
  For mc and multi, one line per option, keyed by letter:
     - A) why this attracts, and the scenario where it WOULD be correct
     - B) Correct: ...
  For table, build and dnd there are no option letters, so write plain bullets
  about the DISCRIMINATIONS: which row is the trap, what wrong sorting principle
  produces a wrong split, which two rows look different but are the same.

THE RULE THAT SURVIVES EVERY TYPE
  A wrong option must teach a second concept by contrast, so name the scenario
  where it WOULD be correct. Everything else here is syntax; this is the part
  worth protecting, and it is the first thing a model drops under length
  pressure. `itembank lint` warns when a distractor line never says it.
"""

BANK_FILE_HINTS = ("_mc_bank", "_exam_bank", "_question_bank", "_quiz_bank")

WOULD_BE = re.compile(
    r"would be|would win|would apply|if the stem|correct when|correct if|"
    r"right for|right when|right if|applies when", re.I)


def lint(questions):
    """Return (errors, warnings) as lists of 'Qn: message' strings."""
    errors, warnings = [], []
    seen_stems = {}
    seen_ids = {}
    letter_hits = collections.Counter()

    for idx, q in enumerate(questions, 1):
        tag = "Q%d" % idx
        t = q["type"]

        if q.get("id") in seen_ids:
            errors.append("%s: duplicate question number %s (also %s)" %
                          (tag, q["id"], seen_ids[q["id"]]))
        seen_ids[q.get("id")] = tag

        if t in ("mc", "multi"):
            if len(q["correct"]) != q["select"]:
                errors.append("%s: SELECT is %d but CORRECT lists %d letters"
                              % (tag, q["select"], len(q["correct"])))
            for c in q["correct"]:
                if c not in q["opts"]:
                    errors.append("%s: CORRECT names option %s, which does not exist" % (tag, c))
            if len(q["opts"]) < 3:
                errors.append("%s: only %d options" % (tag, len(q["opts"])))
            if t == "mc" and q["correct"]:
                letter_hits[q["correct"][0]] += 1
            if t == "mc" and not q.get("second"):
                warnings.append("%s: no SECOND-BEST on a multiple-choice item" % tag)
            for L in sorted(q["opts"]):
                if not q["da"].get(L):
                    warnings.append("%s: option %s has no line in DISTRACTOR ANALYSIS" % (tag, L))
            for L in sorted(q["opts"]):
                if L in q["correct"]:
                    continue
                line = q["da"].get(L)
                if line and not WOULD_BE.search(line):
                    warnings.append("%s: distractor %s never says when it WOULD be correct" % (tag, L))

        elif t in ("table", "dnd"):
            if len(q["cats"]) < 2:
                errors.append("%s: needs at least two CATEGORIES" % tag)
            for r in q["rows"]:
                if r["cat"] not in q["cats"]:
                    errors.append("%s: row assigns category '%s', not in CATEGORIES %s"
                                  % (tag, r["cat"], q["cats"]))
            if len(q["rows"]) < 2:
                errors.append("%s: fewer than two rows" % tag)
            if not q.get("notes"):
                warnings.append("%s: no DISTRACTOR ANALYSIS bullets" % tag)

        elif t == "build":
            if len(q["steps"]) < 2:
                errors.append("%s: build list has fewer than two steps" % tag)
            if len(set(q["steps"])) != len(q["steps"]):
                errors.append("%s: duplicate steps in build list" % tag)
            if not q.get("notes"):
                warnings.append("%s: no DISTRACTOR ANALYSIS bullets" % tag)

        elif t == "short":
            if not q.get("model"):
                errors.append("%s: short item has no MODEL answer, so nothing can grade it" % tag)
            if len(q.get("rubric") or []) < 2:
                errors.append("%s: short item needs at least two RUBRIC points; one point is a "
                              "vibe, not a rubric" % tag)
            if len(q.get("model", "").split()) > 80:
                warnings.append("%s: MODEL answer is %d words. A marker cannot check a wall of "
                                "prose point by point; compress it and push detail into RUBRIC"
                                % (tag, len(q["model"].split())))
            for n, r in enumerate(q.get("rubric") or [], 1):
                if len(r.split()) > 25:
                    warnings.append("%s: RUBRIC point %d is %d words. A point should be one "
                                    "checkable claim" % (tag, n, len(r.split())))

        if t != "short" and not q.get("why"):
            errors.append("%s: no WHY BEST field" % tag)   # short items key off MODEL instead
        if not q.get("trap"):
            warnings.append("%s: no TRAP field" % tag)
        if (q.get("conf") or "").lower().startswith("low"):
            warnings.append("%s: CONFIDENCE is low, needs human review before use" % tag)

        key = re.sub(r"\W+", " ", q["stem"].lower()).strip()
        if key and key in seen_stems:
            errors.append("%s: stem duplicates %s" % (tag, seen_stems[key]))
        seen_stems[key] = tag

    total = sum(letter_hits.values())
    if total >= 12:
        top, n = letter_hits.most_common(1)[0]
        if n / total > 0.40:
            warnings.append(
                "BANK: %.0f%% of multiple-choice answers are keyed %s (%d/%d). Harmless for "
                "`itembank build`, which reshuffles options on every page load. It matters "
                "only if this bank is consumed by something that does NOT shuffle: a printed "
                "exam, an export, or another tool."
                % (n / total * 100, top, n, total))
    return errors, warnings


def load(path):
    qs = parse_bank(open(path, encoding="utf-8").read())
    if not qs:
        sys.exit("No question blocks found in %s. Run `itembank spec` for the format." % path)
    return qs


# ---- agent assessment runtime ----------------------------------------------
# The browser is a presentation adapter. These helpers are the shared runtime
# contract for the CLI and future adapters, so an agent never has to scrape HTML
# or infer whether its response was accepted.

SESSION_VERSION = 1


def public_item(q, shuffle_seed=0):
    """Return an item safe to show before the learner answers."""
    out = {"id": q["id"], "number": q["number"], "type": q["type"],
           "stem": q["stem"], "objective": q.get("objective", ""),
           "difficulty": q.get("difficulty", "")}
    if q["type"] in ("mc", "multi"):
        out["options"] = [{"key": k, "text": q["opts"][k]} for k in sorted(q["opts"])]
        out["response_schema"] = {"type": "array" if q["type"] == "multi" else "string",
                                   "select": q["select"], "allowed": sorted(q["opts"])}
    elif q["type"] in ("table", "dnd"):
        out["rows"] = [{"text": r["text"], "id": i} for i, r in enumerate(q["rows"])]
        out["categories"] = q["cats"]
        out["response_schema"] = {"type": "object", "keys": "row id", "values": q["cats"]}
    elif q["type"] == "build":
        import random
        steps = q["steps"][:]
        random.Random(shuffle_seed).shuffle(steps)
        out["steps"] = steps
        out["response_schema"] = {"type": "array", "items": "step text", "ordered": True}
    elif q["type"] == "short":
        out["response_schema"] = {"type": "string", "min_length": 2}
    return out


def normalize_answer(answer):
    if isinstance(answer, str):
        try:
            return json.loads(answer)
        except (TypeError, ValueError):
            return answer.strip()
    return answer


def score_response(q, answer):
    """Score machine-checkable items. Constructed response stays ungraded."""
    answer = normalize_answer(answer)
    if q["type"] == "short":
        return None
    if q["type"] == "mc":
        if isinstance(answer, list):
            answer = answer[0] if len(answer) == 1 else ""
        return isinstance(answer, str) and answer.upper() == q["correct"][0]
    if q["type"] == "multi":
        given = sorted(str(x).upper() for x in (answer if isinstance(answer, list) else [answer]))
        return given == sorted(q["correct"])
    if q["type"] in ("table", "dnd"):
        if isinstance(answer, list):
            answer = {str(i): v for i, v in enumerate(answer)}
        if not isinstance(answer, dict):
            return False
        return all(str(i) in answer and answer[str(i)] == row["cat"]
                   for i, row in enumerate(q["rows"])) and len(answer) == len(q["rows"])
    if q["type"] == "build":
        return isinstance(answer, list) and answer == q["steps"]
    return False


def session_path(path):
    return os.path.abspath(path)


def read_session(path):
    try:
        data = json.load(open(session_path(path), encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.exit("cannot read session %s: %s" % (path, exc))
    if data.get("schema_version") != SESSION_VERSION:
        sys.exit("unsupported session schema in %s" % path)
    return data


def write_session(path, data):
    target = session_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)


def session_view(data, qs):
    selected = data["items"]
    cursor = data["cursor"]
    view = {"schema_version": SESSION_VERSION, "session_id": data["session_id"],
            "status": data["status"], "mode": data["mode"],
            "objective": data.get("objective", ""), "position": cursor,
            "total": len(selected), "responses": len(data["responses"])}
    if data["status"] == "active" and cursor < len(selected):
        view["item"] = public_item(qs[selected[cursor]], data.get("seed", 0) + cursor)
    else:
        view["summary"] = session_summary(data)
    return view


def session_summary(data):
    responses = data["responses"]
    auto = [r for r in responses if r["score"] is not None]
    correct = sum(1 for r in auto if r["score"] is True)
    by_objective = collections.defaultdict(lambda: {"attempts": 0, "correct": 0, "pending": 0})
    for r in responses:
        bucket = by_objective[r.get("objective") or "(unmapped)"]
        bucket["attempts"] += 1
        if r["score"] is None:
            bucket["pending"] += 1
        elif r["score"]:
            bucket["correct"] += 1
    return {"auto_attempts": len(auto), "auto_correct": correct,
            "pending_manual": len(responses) - len(auto),
            "objectives": dict(by_objective)}


def cmd_start(a):
    qs = load(a.bank)
    errors, _ = lint(qs)
    if errors and not a.force:
        sys.exit("refusing to start a bank with errors; run lint or pass --force")
    import random, uuid
    candidates = [i for i, q in enumerate(qs) if not a.objective or q.get("objective") == a.objective]
    if not candidates:
        sys.exit("no items match objective %r" % a.objective)
    rng = random.Random(a.seed)
    rng.shuffle(candidates)
    items = candidates[:min(a.count, len(candidates))]
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.bank)) or ".", "_attempts",
                                "session_%s.json" % uuid.uuid4().hex[:12])
    data = {"schema_version": SESSION_VERSION, "session_id": uuid.uuid4().hex,
            "bank": os.path.abspath(a.bank), "items": items, "cursor": 0,
            "responses": [], "status": "active", "mode": a.mode,
            "objective": a.objective or "", "seed": a.seed}
    write_session(out, data)
    result = session_view(data, qs)
    result["session_file"] = session_path(out)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_next(a):
    data = read_session(a.session)
    qs = load(data["bank"])
    print(json.dumps(session_view(data, qs), ensure_ascii=False, indent=2))
    return 0


def cmd_submit(a):
    data = read_session(a.session)
    if data["status"] != "active":
        sys.exit("session is already complete")
    qs = load(data["bank"])
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
        write_session(a.session, data)
        sys.exit("session is already complete")
    q = qs[data["items"][data["cursor"]]]
    answer = normalize_answer(a.answer)
    score = score_response(q, answer)
    data["responses"].append({"item_id": q["id"], "objective": q.get("objective", ""),
                               "type": q["type"], "answer": answer, "score": score})
    data["cursor"] += 1
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
    write_session(a.session, data)
    result = {"accepted": True, "item_id": q["id"], "score": score,
              "status": data["status"], "next": session_view(data, qs)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_report(a):
    data = read_session(a.session)
    print(json.dumps({"session_id": data["session_id"], "status": data["status"],
                      "summary": session_summary(data)}, ensure_ascii=False, indent=2))
    return 0


def cmd_spec(a):
    print(SPEC)
    return 0


def cmd_lint(a):
    qs = load(a.bank)
    errors, warnings = lint(qs)
    for e in errors:
        print("error  " + e)
    for w in warnings:
        print("warn   " + w)
    print("\n%d items, %d errors, %d warnings" % (len(qs), len(errors), len(warnings)))
    return 1 if errors else 0


def page_for(bank_path, qs, record=False, reveal=False):
    text = open(bank_path, encoding="utf-8").read()
    title = grab(r"(?m)^#\s+(.*?)\s*$", text) or os.path.basename(bank_path)
    counts = collections.Counter(q["type"] for q in qs)
    mix = ", ".join("%d %s" % (v, k) for k, v in counts.most_common())
    sub = "%d items &middot; %s &middot; dichotomous scoring" % (len(qs), mix)
    if record:
        sub += " &middot; answers recorded"
    return mix, (TEMPLATE
                 .replace("__DATA__", json.dumps(qs, ensure_ascii=False))
                 .replace("__RECORD__", "true" if record else "false")
                 .replace("__REVEAL__", "true" if reveal else "false")
                 .replace("__TITLE__", html.escape(title))
                 .replace("__SUB__", sub))


def cmd_build(a):
    qs = load(a.bank)
    errors, _ = lint(qs)
    if errors and not a.force:
        for e in errors:
            print("error  " + e)
        sys.exit("refusing to build a bank with errors; fix them or pass --force")
    out = a.out or os.path.splitext(a.bank)[0] + "_quiz.html"
    if os.path.dirname(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    # A file:// page cannot write anywhere, so `build` never records. It stays
    # the shareable, no-process mode; `serve` is the one that keeps answers.
    mix, page = page_for(a.bank, qs, record=False, reveal=not a.blind)
    open(out, "w", encoding="utf-8").write(page)
    print("%d items -> %s" % (len(qs), out))
    print("   mix: " + mix)
    if any(q["type"] == "short" for q in qs):
        print("   note: short answers cannot be saved by a file:// page. "
              "Use `itembank serve` if this sitting is meant to be graded.")
    return 0


# ---- attempt file -----------------------------------------------------------
# One markdown file per sitting, rewritten in full on every answer. Markdown
# rather than JSON because the reader is a human or an LLM, both of which read
# prose better than they read a data structure, and because it lands in a vault
# next to the notes it feeds.

def attempt_markdown(bank_path, answers, done):
    from datetime import datetime
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = [a for a in answers if a.get("type") != "__end__"]
    auto = [a for a in body if a.get("correct") is not None]
    right = [a for a in auto if a["correct"]]
    shorts = [a for a in body if a.get("type") == "short"]
    L = []
    L.append("# Attempt: %s" % os.path.basename(bank_path))
    L.append("")
    L.append("*Written by `itembank serve`. Bank: `%s`. Started %s.*" % (bank_path, stamp))
    L.append("")
    L.append("**Status:** %s. %d auto-marked, %d correct. %d short answer(s) awaiting a marker."
             % ("finished" if done else "IN PROGRESS, file may be partial",
                len(auto), len(right), len(shorts)))
    L.append("")
    L.append("**To grade this:** see `GRADING.md` in the itembank repo. Mark each short answer "
             "against its rubric, write the verdict into the `MARK:` line, and leave the "
             "answer text exactly as written.")
    L.append("")
    for a in body:
        L.append("---")
        L.append("")
        head = "## Item %d, %s" % (a.get("n", 0), a.get("type", "?"))
        if a.get("correct") is True:
            head += "  [auto: correct]"
        elif a.get("correct") is False:
            head += "  [auto: WRONG]"
        L.append(head)
        if a.get("objective"):
            L.append("")
            L.append("*Objective: %s*" % a["objective"])
        L.append("")
        L.append("**Q.** %s" % a.get("stem", "").replace("\n", " "))
        L.append("")
        if a.get("type") == "short":
            L.append("**His answer, verbatim:**")
            L.append("")
            L.append("```")
            L.append(a.get("answer", "") or "(left blank)")
            L.append("```")
            L.append("")
            if a.get("model"):
                L.append("**Model answer (from the bank, NOT his):** %s" % a["model"].replace("\n", " "))
                L.append("")
            if a.get("rubric"):
                L.append("**Rubric. Replace each `(unmarked)` with `(pass)` or `(fail)`:**")
                L.append("")
                for r in a["rubric"]:
                    L.append("- (unmarked) %s" % r)
                L.append("")
            L.append("MARK: (unmarked)")
        else:
            L.append("**Selected:** %s" % (a.get("answer") or "(nothing)"))
        L.append("")
    if not done:
        L.append("---")
        L.append("")
        L.append("*Sitting was not finished. Everything above is real; nothing after it was answered.*")
        L.append("")
    return "\n".join(L)


def cmd_serve(a):
    """Run the quiz against a local process so every answer is written to disk.

    The static `build` page is sandboxed by the browser and cannot write a file,
    which is why answers used to evaporate when the tab closed. A loopback
    server is the smallest thing that fixes it without adding a dependency: the
    page POSTs each answer, this process writes the attempt file.
    """
    import http.server, socketserver, webbrowser, threading
    from datetime import datetime

    qs = load(a.bank)
    errors, _ = lint(qs)
    if errors and not a.force:
        for e in errors:
            print("error  " + e)
        sys.exit("refusing to serve a bank with errors; fix them or pass --force")

    out = a.out or os.path.join(
        os.path.dirname(os.path.abspath(a.bank)) or ".", "_attempts",
        "%s_attempt_%s.md" % (os.path.splitext(os.path.basename(a.bank))[0],
                              datetime.now().strftime("%Y-%m-%d_%H%M")))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    _, page = page_for(a.bank, qs, record=True, reveal=a.reveal)
    page_bytes = page.encode("utf-8")
    state = {"writes": 0}

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass                                    # the progress line below is the log

        def do_GET(self):
            if self.path not in ("/", "/index.html"):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page_bytes)))
            self.end_headers()
            self.wfile.write(page_bytes)

        def do_POST(self):
            if self.path != "/save":
                self.send_error(404)
                return
            n = int(self.headers.get("Content-Length") or 0)
            try:
                data = json.loads(self.rfile.read(n).decode("utf-8"))
                md = attempt_markdown(a.bank, data.get("answers", []), data.get("done"))
                open(out, "w", encoding="utf-8").write(md)
                state["writes"] += 1
                answered = len([x for x in data.get("answers", [])
                                if x.get("type") != "__end__"])
                sys.stdout.write("\r  %d/%d answered, saved" % (answered, len(qs)))
                sys.stdout.flush()
                if data.get("done"):
                    print("\n  finished. Attempt file: %s" % out)
            except Exception as exc:                # never let a bad POST kill a sitting
                self.send_error(500, str(exc))
                return
            self.send_response(204)
            self.end_headers()

    print("itembank serve")
    # Windows reserves scattered port ranges (Hyper-V, WSL), so a fixed default
    # can fail with a permission error that looks like a bug in this tool. Fall
    # back to an OS-assigned port rather than making the user diagnose WinError
    # 10013 on their own.
    try:
        srv = socketserver.TCPServer(("127.0.0.1", a.port), H)
    except OSError as exc:
        print("  port %d unavailable (%s), using a free one instead" % (a.port, exc.__class__.__name__))
        srv = socketserver.TCPServer(("127.0.0.1", 0), H)

    with srv:
        url = "http://127.0.0.1:%d/" % srv.server_address[1]
        print("  bank    %s (%d items)" % (a.bank, len(qs)))
        print("  attempt %s" % out)
        print("  url     %s" % url)
        print("  Answers are written as you give them. Ctrl-C when you are done.")
        sys.stdout.flush()
        if not a.no_open:
            threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped. %d save(s) written to %s"
                  % (state["writes"], out if state["writes"] else "nothing yet"))
    return 0


def cmd_stats(a):
    qs = load(a.bank)
    counts = collections.Counter(q["type"] for q in qs)
    print("%d items" % len(qs))
    for k, v in counts.most_common():
        print("  %-6s %4d  %4.0f%%" % (k, v, v / len(qs) * 100))
    objs = collections.Counter(q["objective"] for q in qs if q["objective"])
    if objs:
        print("\nobjective coverage (%d distinct)" % len(objs))
        for k, v in objs.most_common(12):
            print("  %3d  %s" % (v, k))
    diff = collections.Counter(q["difficulty"] for q in qs if q["difficulty"])
    if diff:
        print("\ndifficulty")
        for k, v in diff.most_common():
            print("  %3d  %s" % (v, k))
    mc = [q for q in qs if q["type"] == "mc" and q["correct"]]
    if mc:
        pos = collections.Counter(q["correct"][0] for q in mc)
        print("\nanswer position, %d multiple-choice items" % len(mc))
        for k in sorted(pos):
            print("  %s  %3d  %4.0f%%" % (k, pos[k], pos[k] / len(mc) * 100))
    return 0


def cmd_guard(a):
    """Fail if any markdown outside fixtures/ parses as a real question bank.

    The mechanical half of the content rule. Discipline does not survive a
    late-night commit; a CI check does.
    """
    offenders = []
    for root, dirs, files in os.walk(a.dir):
        dirs[:] = [d for d in dirs if d not in (".git", "fixtures", ".github")]
        for f in files:
            if not f.lower().endswith(".md"):
                continue
            p = os.path.join(root, f)
            try:
                n = len(parse_bank(open(p, encoding="utf-8").read()))
            except Exception:
                continue
            if n > 0 or any(h in f.lower() for h in BANK_FILE_HINTS):
                offenders.append((p, n))
    for p, n in offenders:
        print("error  %s parses as a question bank (%d items). Banks belong in your "
              "private vault, never in this repo." % (p, n))
    print("\n%d offending files" % len(offenders))
    return 1 if offenders else 0


def main():
    ap = argparse.ArgumentParser(
        prog="itembank",
        description="Author, validate and render exam-style question banks in markdown.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("spec", help="print the format contract")
    s.set_defaults(fn=cmd_spec)

    s = sub.add_parser("lint", help="validate a bank")
    s.add_argument("bank")
    s.set_defaults(fn=cmd_lint)

    s = sub.add_parser("build", help="render an interactive HTML quiz (nothing is saved)")
    s.add_argument("bank")
    s.add_argument("out", nargs="?")
    s.add_argument("--force", action="store_true", help="build despite lint errors")
    s.add_argument("--blind", action="store_true",
                   help="hide model answers on short items, for a self-marked sitting")
    s.set_defaults(fn=cmd_build)

    s = sub.add_parser("serve", help="sit the quiz with every answer written to disk")
    s.add_argument("bank")
    s.add_argument("--out", help="attempt file (default: _attempts/<bank>_attempt_<date>.md)")
    s.add_argument("--port", type=int, default=8731)
    s.add_argument("--reveal", action="store_true",
                   help="show model answers after each short item; off by default so an "
                        "early item cannot teach a later one")
    s.add_argument("--no-open", action="store_true", dest="no_open",
                   help="do not launch a browser")
    s.add_argument("--force", action="store_true", help="serve despite lint errors")
    s.set_defaults(fn=cmd_serve)

    s = sub.add_parser("stats", help="item mix, coverage, answer-position skew")
    s.add_argument("bank")
    s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("start", help="start a resumable JSON assessment session")
    s.add_argument("bank")
    s.add_argument("--count", type=int, default=10)
    s.add_argument("--objective", default="", help="limit the session to one objective")
    s.add_argument("--mode", default="diagnostic",
                   choices=("diagnostic", "practice", "exam", "remediation"))
    s.add_argument("--seed", type=int, default=0, help="deterministic item-selection seed")
    s.add_argument("--out", help="session JSON path")
    s.add_argument("--force", action="store_true", help="start despite lint errors")
    s.set_defaults(fn=cmd_start)

    s = sub.add_parser("next", help="return the next item in a JSON assessment session")
    s.add_argument("session")
    s.set_defaults(fn=cmd_next)

    s = sub.add_parser("submit", help="score and record the current session response")
    s.add_argument("session")
    s.add_argument("--answer", required=True,
                   help="response value, or a JSON array/object for structured items")
    s.set_defaults(fn=cmd_submit)

    s = sub.add_parser("report", help="summarize a JSON assessment session")
    s.add_argument("session")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("guard", help="fail if a real bank was committed")
    s.add_argument("dir", nargs="?", default=".")
    s.set_defaults(fn=cmd_guard)

    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
