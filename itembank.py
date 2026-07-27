#!/usr/bin/env python3
"""itembank: author, validate and render exam-style question banks in markdown.

Built because a prose format spec does not fail loudly. An AI handed a prompt
template can conform to it or not with no way to tell which, so banks go
silently malformed and nobody notices until a renderer reports the wrong item
count. The fix is a machine-checkable contract: `itembank spec` tells an
authoring agent the format, `itembank lint` tells it exactly what it got wrong.

  itembank spec                 print the format contract (the AI-facing entry point)
  itembank lint  BANK.md        validate; errors exit non-zero, warnings advise
  itembank build BANK.md [OUT]  self-contained offline interactive HTML quiz
  itembank stats BANK.md        item mix, objective coverage, answer-position skew
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
    qtype = (grab(r"(?m)^\[TYPE:\s*(\w+)\s*\]", ch) or "mc").lower()
    # Stem runs from the Qn. marker to the first structural marker that follows.
    stem = grab(
        r"Q\d+\.\s*(.*?)\s*(?:\(difficulty:|\n\[OBJECTIVE|\n\[TYPE|\n\[SELECT"
        r"|\n\[CATEGORIES|\n[A-H]\)|\nROW\)|\nITEM\)|\nSTEP\))",
        ch, re.S)
    common = {
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
  </div>
</div>
<div id="host"></div>
</div>
<script>
const Q = __DATA__;
const LABEL = {mc:"multiple choice", multi:"multiple response",
               table:"options table", build:"build list", dnd:"drag-and-drop"};
let i = 0, score = 0;
const miss = [];
const host = document.getElementById("host");
const esc = s => (s==null?"":String(s));

function shuffled(a){const b=a.slice();for(let j=b.length-1;j>0;j--){
  const k=Math.floor(Math.random()*(j+1));[b[j],b[k]]=[b[k],b[j]];}return b;}

function same(a,b){return a.length===b.length && a.every(x=>b.includes(x));}

function chips(q){
  let h = `<span class="chip type">${LABEL[q.type]||q.type}</span>`;
  if(q.type!=="mc") h += `<span class="chip aon">no partial credit</span>`;
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
  ({mc:asChoice, multi:asChoice, table:asAssign, dnd:asAssign, build:asBuild}[q.type])
    (q, body, act, card);
  card.scrollIntoView({block:"start", behavior:"smooth"});
}

/* ---- multiple choice + multiple response ---------------------------------- */
function asChoice(q, body, act, card){
  const multi = q.type === "multi";
  const keys = Object.keys(q.opts);
  const picked = [];
  const wrap = document.createElement("div");
  wrap.className = "opts";
  const btns = {};
  keys.forEach(k=>{
    const b = document.createElement("button");
    b.className = "opt"; b.type = "button"; b.setAttribute("aria-pressed","false");
    b.innerHTML = `<span class="k">${k}</span><span>${esc(q.opts[k])}</span>`;
    b.onclick = ()=>{
      if(!multi){ picked.length=0; picked.push(k); grade(); return; }
      const at = picked.indexOf(k);
      if(at>=0) picked.splice(at,1);
      else if(picked.length < q.select) picked.push(k);
      keys.forEach(x=>btns[x].setAttribute("aria-pressed", picked.includes(x)?"true":"false"));
      submit.disabled = picked.length !== q.select;
    };
    btns[k]=b; wrap.appendChild(b);
  });
  body.appendChild(wrap);
  let submit;
  if(multi){
    submit = mkSubmit(act, `select ${q.select}`);
    submit.onclick = grade;
  }
  function grade(){
    const right = same(picked, q.correct);
    keys.forEach(k=>{
      btns[k].disabled = true;
      if(q.correct.includes(k)) btns[k].classList.add("right");
      else if(picked.includes(k)) btns[k].classList.add("wrong");
    });
    if(submit) submit.remove();
    close(q, card, act, right, picked.join(", "));
  }
}

/* ---- options table + drag-and-drop (assign each row to a category) -------- */
function asAssign(q, body, act, card){
  const rows = q.type==="dnd" ? shuffled(q.rows) : q.rows;
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

function mkSubmit(act, hint){
  const b = document.createElement("button");
  b.className="go"; b.type="button"; b.textContent="Check"; b.disabled=true;
  const h = document.createElement("span"); h.className="hint"; h.textContent=hint;
  act.appendChild(b); act.appendChild(h);
  return b;
}

/* ---- reveal --------------------------------------------------------------- */
function close(q, card, act, right, given){
  if(right) score++; else miss.push({q, given});
  act.innerHTML = "";
  const exp = document.createElement("div");
  exp.className = "exp";
  let h = `<div class="verdict ${right?"y":"n"}">${right?"Correct":"Not correct"}</div>`;
  const blk = (t,v)=> v ? `<div class="blk"><h4>${t}</h4><div>${esc(v)}</div></div>` : "";
  h += blk("Why this is best", q.why);
  h += blk("Key discriminator", q.disc);
  h += blk("Second best", q.second);
  const lines = [];
  if(q.da) Object.keys(q.da).forEach(k=>{ if(q.da[k]) lines.push(`<b>${k})</b> ${esc(q.da[k])}`); });
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
  const pct = Math.round(score/Q.length*100);
  let h = `<div class="done"><div class="score mono">${score}/${Q.length}
    <span style="font-size:17px;color:var(--mut)"> &middot; ${pct}%</span></div>`;
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
    letter_hits = collections.Counter()

    for idx, q in enumerate(questions, 1):
        tag = "Q%d" % idx
        t = q["type"]

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

        if not q.get("why"):
            errors.append("%s: no WHY BEST field" % tag)
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
                "BANK: %.0f%% of multiple-choice answers are %s (%d/%d). Answer-position "
                "skew is invisible to the author and common in AI-written banks; redistribute."
                % (n / total * 100, top, n, total))
    return errors, warnings


def load(path):
    qs = parse_bank(open(path, encoding="utf-8").read())
    if not qs:
        sys.exit("No question blocks found in %s. Run `itembank spec` for the format." % path)
    return qs


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


def cmd_build(a):
    qs = load(a.bank)
    errors, _ = lint(qs)
    if errors and not a.force:
        for e in errors:
            print("error  " + e)
        sys.exit("refusing to build a bank with errors; fix them or pass --force")
    text = open(a.bank, encoding="utf-8").read()
    title = grab(r"(?m)^#\s+(.*?)\s*$", text) or os.path.basename(a.bank)
    counts = collections.Counter(q["type"] for q in qs)
    mix = ", ".join("%d %s" % (v, k) for k, v in counts.most_common())
    out = a.out or os.path.splitext(a.bank)[0] + "_quiz.html"
    if os.path.dirname(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    page = (TEMPLATE.replace("__DATA__", json.dumps(qs, ensure_ascii=False))
                    .replace("__TITLE__", html.escape(title))
                    .replace("__SUB__", "%d items &middot; %s &middot; dichotomous scoring"
                                        % (len(qs), mix)))
    open(out, "w", encoding="utf-8").write(page)
    print("%d items -> %s" % (len(qs), out))
    print("   mix: " + mix)
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

    s = sub.add_parser("build", help="render an interactive HTML quiz")
    s.add_argument("bank")
    s.add_argument("out", nargs="?")
    s.add_argument("--force", action="store_true", help="build despite lint errors")
    s.set_defaults(fn=cmd_build)

    s = sub.add_parser("stats", help="item mix, coverage, answer-position skew")
    s.add_argument("bank")
    s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("guard", help="fail if a real bank was committed")
    s.add_argument("dir", nargs="?", default=".")
    s.set_defaults(fn=cmd_guard)

    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
