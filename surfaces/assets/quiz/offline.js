const Q = __DATA__;
const SERVE = false;
const LESSON_BASE = "__LESSON_BASE__";   /* empty when no reader sits behind this page */
const LESSON_LABEL = "__LESSON_LABEL__";
const LETTERS = "ABCDEFGH";
const LABEL = {mc:"multiple choice", multi:"multiple response",
               table:"options table", build:"build list", dnd:"drag-and-drop",
               short:"short answer", fill:"typed fields", check:"code check",
               visual:"visual assessment"};
const FORMAT_LABEL = {mc:"Single choice", multi:"Multiple choice",
  table:"Table response", build:"Build response", dnd:"Ordering or matching",
  short:"Short response", fill:"Typed fields", visual:"Visual interaction", check:"Code check"};
const FORMAT_INSTRUCTION = {mc:"Choose one option.",
  multi:"Choose the requested number of options.",
  table:"Choose one category for every row.",
  build:"Select every step in the order it should happen.",
  dnd:"Match every row to a category. Dragging is not required.",
  short:"Write your response. It stays pending until a marker reviews it.",
  fill:"Enter a response in every field. Include a unit when the label asks for one.",
  visual:"Use the visual or its adjacent keyboard controls, then submit.",
  check:"Edit the source, then run the check. The runtime records the verdict."};
const FS = "\u001f", PS = "\u001e";   /* must match FIELD_SEP and PAIR_SEP */
const REDUCED = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
let i = 0, score = 0, autoTotal = 0;
let shownAt = performance.now();
const miss = [];
const host = document.getElementById("host");
const cxObjective = document.getElementById("cx-objective");
const cxLesson = document.getElementById("cx-lesson");
const detailBody = document.getElementById("detail-body");
const activityResponse = document.getElementById("activity-response");
const activityDisclosure = document.getElementById("activity-disclosure");
const activityPurpose = document.getElementById("activity-purpose");
const activityInstructions = document.getElementById("activity-instructions");
const esc = s => (s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

function installStickyMeasure(){
  const band = document.querySelector("[data-surface-context]");
  if(!band || !("ResizeObserver" in window)) return;
  let last = -1;
  new ResizeObserver(entries=>{
    const h = Math.round(entries[0].contentRect.height);
    if(h!==last){ last=h; document.documentElement.style.setProperty("--sticky-h",h+"px"); }
  }).observe(band);
}
function scrollCardIfNeeded(card){
  const r=card.getBoundingClientRect();
  const sticky=parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--sticky-h"))||0;
  if(r.top<sticky || r.bottom>innerHeight)
    card.scrollIntoView({block:"start",behavior:REDUCED?"auto":"smooth"});
}
installStickyMeasure();

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
  if(activityPurpose) activityPurpose.textContent = document.getElementById("cx-mode").textContent === "exam"
    ? "Formal assessment" : "Practice";
  if(activityResponse) activityResponse.textContent = q.ordering ? "Ordering response" : FORMAT_LABEL[q.type] || q.type || "Response";
  if(activityInstructions) activityInstructions.textContent = q.ordering
    ? "Arrange the selected blocks in order. Leave unused blocks in the source area."
    : FORMAT_INSTRUCTION[q.type] || "Follow the response instructions below.";
  if(activityDisclosure) activityDisclosure.textContent = q.type === "short"
    ? "Pending human review" : (document.getElementById("cx-mode").textContent === "exam"
      ? "Feedback after completion" : "Feedback available now");
  if(cxLesson) cxLesson.innerHTML = lessonChip(q);
  if(detailBody) detailBody.innerHTML = `<span class="chip">${esc(q.objective||"")}</span>`
    + `<span class="chip">${esc(document.getElementById("cx-mode").textContent)}</span>`
    + lessonChip(q) + metaChips(q);
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
  card.className = "card overhaul-question";
  card.innerHTML = questionStemHTML(q.fill_layout === "inline" ? String(q.stem).replace(/\{\{[a-z][a-z0-9_]{0,31}\}\}/g, "____") : q.stem);
  if(window.renderQuestionSymbols) window.renderQuestionSymbols(q, card);
  const body = document.createElement("div");
  body.className = `response-body overhaul-response response-${q.type}`;
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
    short:asShort, fill:asFillOffline, check:asCheck, visual:asVisualOffline}[q.type])(q, body, act, card);
  scrollCardIfNeeded(card);
}

/* ---- visual assessment, offline (plan 06.1-03, D-03/A-05) ------------------
   The static build has no process behind it, so it cannot score a visual item
   or protect its answer. It renders the honest served-runtime-required state:
   no scorer, no key, no private scene fields, and no dead control. The copy
   is the 06.1-UI-SPEC Copywriting Contract's exact offline refusal text. */
function asVisualOffline(q, body, act, card){
  const note = document.createElement("div");
  note.className = "status";
  note.setAttribute("role", "note");
  note.textContent = "This visual item needs a served itembank session because "
    + "scoring and answer protection happen there. Open it with itembank serve "
    + "or the daemon.";
  body.appendChild(note);
}

function fillFields(q, body){
  const controls = {};
  const wrap = document.createElement("div");
  wrap.className = "fill-fields";
  (q.fields || []).forEach(field=>{
    const label = document.createElement("label");
    label.className = "fill-field";
    const text = document.createElement("span");
    text.textContent = field.label || field.id;
    const help = document.createElement("span");
    help.className = "fill-help";
    help.id = "fill-help-" + field.id;
    if(field.kind === "polynomial"){
      help.textContent = String((field.checker || {}).grammar || "Use x, numbers, explicit * and powers 0 to 4.")
        + " Expand products. Example: 3*x^2 + 4*x + 1. Maximum 160 characters.";
    } else if(field.kind === "text"){
      const caseRule = field.case_sensitive === false
        ? "Uppercase and lowercase are treated the same."
        : "Case matters.";
      const spaceRule = field.whitespace === "exact"
        ? "Spaces count exactly as typed."
        : (field.whitespace === "collapse"
          ? "Repeated spaces are treated as one."
          : "Leading and trailing spaces are ignored.");
      help.textContent = caseRule + " " + spaceRule;
    } else {
      help.textContent = "Enter a decimal, fraction, or scientific number."
        + ((field.units || []).length
          ? " Add a space, then one of: " + field.units.join(", ") + "."
          : "");
    }
    const input = document.createElement("input");
    input.type = "text";
    input.inputMode = "text";
    input.autocomplete = "off";
    input.maxLength = 4096;
    input.name = "fill_" + field.id;
    input.setAttribute("aria-describedby", help.id);
    label.append(text, help, input);
    wrap.appendChild(label);
    controls[String(field.id)] = input;
  });
  if(q.fill_layout === "inline"){
    const labels = {};
    (q.fields || []).forEach(field=>{ labels[field.id] = controls[field.id].parentNode; });
    wrap.replaceChildren();
    wrap.className += " fill-inline";
    String(q.stem || "").split(/(\{\{[a-z][a-z0-9_]{0,31}\}\})/).forEach(part=>{
      if(part.startsWith("{{")) wrap.appendChild(labels[part.slice(2, -2)]);
      else wrap.appendChild(document.createTextNode(part));
    });
  }
  body.appendChild(wrap);
  return controls;
}

function asFillOffline(q, body, act, card){
  fillFields(q, body);
  const note = document.createElement("div");
  note.className = "status";
  note.setAttribute("role", "note");
  note.textContent = "This typed response needs a served itembank session because "
    + "the runtime checks text rules, numeric values, and units. Open it with "
    + "itembank serve or the daemon.";
  body.appendChild(note);
  const submit = mkSubmit(act, "served runtime required");
  submit.disabled = true;
  submit.textContent = "Serve to check response";
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
    const correct = Array.isArray(ex.correct) && ex.correct.length ? ex.correct : null;
    if(!correct){ return; }
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
function asMatching(q, body, act, card){
  const values = Object.create(null), controls = new Map();
  const once = q.matching.reuse === "once";
  const notice = document.createElement("p"); notice.setAttribute("role", "status");
  notice.textContent = once ? "Use each choice once. Unused choices are allowed." : "Choices can be reused. Match every row.";
  body.appendChild(notice);
  let locked = false;
  q.rows.forEach(row=>{
    const label = document.createElement("label"); label.className = "inline-completion";
    label.appendChild(document.createTextNode(row.text + " (" + row.id + ") "));
    const select = document.createElement("select"); select.dataset.rowId = row.id;
    select.appendChild(document.createElement("option"));
    q.matching.choices.forEach(choice=>{
      const option = document.createElement("option"); option.value = choice.id;
      option.textContent = choice.text + " (" + choice.id + ")"; select.appendChild(option);
    });
    select.onchange = ()=>{
      values[row.id] = select.value; refresh();
    };
    label.appendChild(select); body.appendChild(label); controls.set(row.id, select);
  });
  const submit = mkSubmit(act, "match every row");
  function refresh(){
    const chosen = Array.from(controls.values(), select=>select.value).filter(Boolean);
    controls.forEach(select=>Array.from(select.options).forEach(option=>{
      option.disabled = once && !!option.value && option.value !== select.value && chosen.includes(option.value);
    }));
    submit.disabled = locked || chosen.length !== q.rows.length || (once && new Set(chosen).size !== chosen.length);
  }
  function revert(){ locked = false; controls.forEach(select=>select.disabled = false); act.appendChild(submit); refresh(); }
  submit.onclick = ()=>{
    locked = true; controls.forEach(select=>select.disabled = true); submit.remove();
    settle(q, Object.assign({}, values), card, act, v=>{
      const keys = (v.explain || {}).row_cats || {};
      controls.forEach((select, id)=>{ if(Object.prototype.hasOwnProperty.call(keys, id)) select.classList.add(select.value === keys[id] ? "right" : "wrong"); });
    }, revert);
  };
  refresh();
}

function asAssign(q, body, act, card){
  if(q.matching) return asMatching(q, body, act, card);
  const rows = shuffled(q.rows);
  const chosen = {};                 // row id -> category
  const segs = {};
  let locked = false, dragged = null;
  let draggedWord = null;
  if(q.type === "dnd" && rows.some(r=>String(r.text).split("___").length === 2)){
    const hint = document.createElement("p");
    hint.textContent = "Drag a word into a blank, or choose it from the dropdown. Words can be reused.";
    const bank = document.createElement("div"); bank.className = "inline-word-bank";
    q.categories.forEach(category=>{
      const word = document.createElement("span"); word.textContent = category;
      word.draggable = true; word.dataset.word = category;
      word.ondragstart = event=>{
        if(locked){ event.preventDefault(); return; }
        draggedWord = category;
        if(event.dataTransfer){ event.dataTransfer.effectAllowed = "copy"; event.dataTransfer.setData("text/plain", category); }
      };
      word.ondragend = ()=>{ draggedWord = null; };
      bank.appendChild(word);
    });
    body.append(hint, bank);
  }
  const draggableRows = q.type === "dnd" ? rows.filter(r=>String(r.text).split("___").length !== 2) : [];
  const bucketLists = new Map();
  function redrawBuckets(){
    bucketLists.forEach((list, category)=>{
      list.replaceChildren();
      rows.filter(r=>chosen[String(r.id)] === category).forEach(r=>{
        const entry = document.createElement("li");
        entry.textContent = r.text; entry.dataset.rowId = String(r.id); list.appendChild(entry);
      });
    });
  }
  function prepareDrag(text, id){
    if(!draggableRows.some(r=>String(r.id) === id)) return;
    text.draggable = true; text.classList.add("drag-card"); text.dataset.dragRow = id;
    text.ondragstart = event=>{
      if(locked){ event.preventDefault(); return; }
      dragged = id;
      if(event.dataTransfer){ event.dataTransfer.effectAllowed = "move"; event.dataTransfer.setData("application/x-itembank-row", id); }
    };
    text.ondragend = ()=>{ dragged = null; body.querySelectorAll(".is-over").forEach(el=>el.classList.remove("is-over")); };
  }
  function mountBuckets(){
    if(!draggableRows.length) return;
    const hint = document.createElement("p");
    hint.textContent = "Drag a card to a bucket, or choose its category with the buttons below.";
    const grid = document.createElement("div"); grid.className = "assignment-buckets";
    q.categories.forEach(category=>{
      const bucket = document.createElement("section"), heading = document.createElement("h2"), list = document.createElement("ul");
      bucket.className = "assignment-bucket"; bucket.dataset.category = category;
      bucket.setAttribute("aria-label", category + " bucket"); heading.textContent = category;
      bucket.append(heading, list); bucketLists.set(category, list);
      bucket.ondragover = event=>{ if(!locked && dragged !== null){ event.preventDefault(); bucket.classList.add("is-over"); } };
      bucket.ondragleave = ()=>bucket.classList.remove("is-over");
      bucket.ondrop = event=>{
        event.preventDefault(); bucket.classList.remove("is-over");
        if(locked || dragged === null) return;
        const button = (segs[dragged] || []).find(el=>el.tagName === "BUTTON" && el.textContent === category);
        if(button && !button.disabled) button.click();
        dragged = null;
      };
      grid.appendChild(bucket);
    });
    body.prepend(hint, grid); redrawBuckets();
  }
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
        if(locked) return;
        chosen[id]=c;
        bs.forEach(x=>x.setAttribute("aria-pressed", x.textContent===c?"true":"false"));
        submit.disabled = Object.keys(chosen).length !== q.rows.length;
        redrawBuckets();
      };
      seg.appendChild(b); return b;
    });
    if(q.type === "dnd" && String(r.text).split("___").length === 2){
      const parts = String(r.text).split("___");
      const label = document.createElement("label");
      label.className = "inline-completion";
      label.appendChild(document.createTextNode(parts[0]));
      const select = document.createElement("select");
      select.setAttribute("aria-label", "Blank " + id + ": " + r.text);
      select.appendChild(document.createElement("option"));
      q.categories.forEach(c=>{
        const option = document.createElement("option");
        option.value = c; option.textContent = c; select.appendChild(option);
      });
      select.onchange = ()=>{
        if(select.value) chosen[id] = select.value;
        else delete chosen[id];
        submit.disabled = Object.keys(chosen).length !== q.rows.length;
      };
      label.ondragover = event=>{ if(!locked && draggedWord !== null) event.preventDefault(); };
      label.ondrop = event=>{
        if(locked || draggedWord === null || !q.categories.includes(draggedWord)) return;
        event.preventDefault();
        select.value = draggedWord; draggedWord = null;
        select.dispatchEvent(new Event("change", {bubbles:true}));
      };
      label.appendChild(select);
      label.appendChild(document.createTextNode(parts[1]));
      segs[id] = [select]; body.appendChild(label);
    }else{
      segs[id] = bs;
      prepareDrag(t, id);
      line.appendChild(t); line.appendChild(seg); body.appendChild(line);
    }
  });
  const submit = mkSubmit(act, "assign every row");
  mountBuckets();
  submit.onclick = ()=>{
    locked = true;
    rows.forEach(r=>segs[String(r.id)].forEach(b=>{ b.disabled = true; }));
    submit.remove();
    settle(q, Object.assign({}, chosen), card, act, v=>{
      const cats = (v.explain||{}).row_cats || {};
      rows.forEach(r=>{
        const id = String(r.id);
        if(!Object.prototype.hasOwnProperty.call(cats, id)) return;
        segs[id].forEach(b=>{
          if((b.tagName === "SELECT" ? b.value : b.textContent)===cats[id]) b.classList.add("right");
          else if((b.tagName === "SELECT" ? b.value : b.textContent)===chosen[id]) b.classList.add("wrong");
        });
      });
    });
  };
}

/* ---- build list (click into order) ---------------------------------------- */
function installOrderingControls(fieldset){
  if(fieldset.orderingRefresh){ fieldset.orderingRefresh(); return; }
  const selects = Array.from(fieldset.querySelectorAll("select[name^=step_]"));
  const source = document.createElement("div");
  source.className = "ordering-source";
  source.setAttribute("aria-label", "Source blocks");
  const title = document.createElement("h3"); title.textContent = "Source blocks";
  const status = document.createElement("p"); status.setAttribute("role", "status");
  status.textContent = "Use Add, Remove, Up and Down, or choose positions with the dropdowns.";
  const buttons = [], handles = [];
  let dragged = null, dragPlaced = false;
  function changed(index){
    selects[index].dispatchEvent(new Event("change", {bubbles:true}));
    selects[index].focus();
  }
  Array.from(selects[0] ? selects[0].options : []).filter(option=>option.value).forEach(option=>{
    const button = document.createElement("button"); button.type = "button";
    button.textContent = "Add"; button.dataset.blockId = option.value;
    button.setAttribute("aria-label", "Add " + option.textContent);
    const handle = document.createElement("span");
    handle.textContent = option.textContent; handle.dataset.orderingBlockId = option.value;
    handle.draggable = true; handle.title = "Drag to an answer position, or use Add.";
    button.onclick = ()=>{
      const index = selects.findIndex(select=>!select.value);
      if(index < 0) return;
      selects[index].value = option.value; changed(index);
    };
    handle.ondragstart = event=>{
      if(button.disabled){ event.preventDefault(); return; }
      dragged = option.value;
      dragPlaced = false;
      status.textContent = "Moving " + option.textContent + ". Drop it on an answer position.";
      if(event.dataTransfer){ event.dataTransfer.effectAllowed = "copy"; event.dataTransfer.setData("text/plain", dragged); }
    };
    handle.ondragend = ()=>{
      if(!dragPlaced && dragged) status.textContent = "Move cancelled. Use Add or drag to an answer position.";
      dragged = null;
      selects.forEach(select=>select.closest("label").classList.remove("ordering-drop-active"));
      selects.forEach(select=>select.closest("label").classList.remove("ordering-drop-active"));
    };
    const block = document.createElement("div"); block.className = "ordering-block";
    block.append(handle, button); source.appendChild(block); buttons.push(button); handles.push(handle);
  });
  fieldset.prepend(title, status, source);
  const answerTitle = document.createElement("h3"); answerTitle.textContent = "Answer positions";
  source.after(answerTitle);
  const actions = [];
  selects.forEach((select,index)=>{
    const label = select.closest("label");
    ["Remove", "Up", "Down"].forEach(action=>{
      const button = document.createElement("button"); button.type = "button";
      button.textContent = action; button.setAttribute("aria-label", action + " block at position " + (index+1));
      button.onclick = ()=>{
        if(action === "Remove"){ select.value = ""; changed(index); return; }
        const target = index + (action === "Up" ? -1 : 1);
        if(target < 0 || target >= selects.length) return;
        const value = selects[target].value; selects[target].value = select.value; select.value = value;
        changed(target);
      };
      label.after(button); actions.push({button,index,action});
    });
    label.ondragover = event=>{
      if(!select.disabled && dragged){
        event.preventDefault();
        if(event.dataTransfer) event.dataTransfer.dropEffect = "copy";
        label.classList.add("ordering-drop-active");
      }
    };
    label.ondragenter = label.ondragover;
    label.ondragleave = ()=>{ label.classList.remove("ordering-drop-active"); };
    label.ondrop = event=>{
      label.classList.remove("ordering-drop-active");
      if(select.disabled || !dragged) return;
      event.preventDefault();
      const previous = selects.findIndex(other=>other.value === dragged);
      if(previous >= 0) selects[previous].value = select.value;
      select.value = dragged;
      const block = Array.from(select.options).find(option=>option.value === dragged);
      status.textContent = "Placed " + (block ? block.textContent : dragged) + " at position " + (index+1) + ".";
      dragPlaced = true; dragged = null; changed(index);
    };
  });
  function refresh(){
    const used = selects.map(select=>select.value).filter(Boolean);
    selects.forEach(select=>Array.from(select.options).forEach(option=>{
      option.disabled = !!option.value && option.value !== select.value && used.includes(option.value);
    }));
    buttons.forEach((button,index)=>{
      button.disabled = selects.some(select=>select.disabled) || used.includes(button.dataset.blockId);
      handles[index].draggable = !button.disabled;
      handles[index].setAttribute("aria-disabled", button.disabled ? "true" : "false");
    });
    actions.forEach(({button,index,action})=>{
      button.disabled = selects[index].disabled || !selects[index].value
        || (action === "Up" && index === 0) || (action === "Down" && index === selects.length-1);
    });
  }
  fieldset.orderingRefresh = refresh;
  fieldset.addEventListener("change", refresh);
  refresh();
}
function asOrdering(q, body, act, card){
  const fieldset = document.createElement("fieldset");
  const signature = JSON.stringify([q.ordering, q.blocks.slice().sort((a,b)=>a.id < b.id ? -1 : a.id > b.id ? 1 : 0)]);
  fieldset.dataset.orderingSignature = signature;
  const legend = document.createElement("legend");
  legend.textContent = "Arrange the selected blocks. Leave unused blocks in the source area.";
  fieldset.appendChild(legend);
  (q.blocks || []).forEach((block,index)=>{
    const label = document.createElement("label"); label.className = "rowline";
    const text = document.createElement("span"); text.textContent = "Position " + (index+1);
    const select = document.createElement("select"); select.name = "step_" + index;
    select.setAttribute("aria-label", text.textContent); select.appendChild(document.createElement("option"));
    q.blocks.forEach(block=>{
      const option = document.createElement("option"); option.value = block.id;
      option.textContent = block.text + " (" + block.id + ")"; select.appendChild(option);
    });
    label.append(text, select); fieldset.appendChild(label);
  });
  body.appendChild(fieldset);
  const selects = Array.from(fieldset.querySelectorAll("select"));
  installOrderingControls(fieldset);
  const submit = mkSubmit(act, "submit selected blocks");
  submit.disabled = false;
  function lock(value){ selects.forEach(select=>{ select.disabled = value; }); fieldset.orderingRefresh(); }
  submit.onclick = ()=>{
    const response = selects.map(select=>select.value).filter(Boolean);
    lock(true); submit.remove();
    settle(q, response, card, act, ()=>{}, ()=>{ lock(false); act.appendChild(submit); submit.disabled = false; submit.focus(); });
  };
}
function readOrderingDraft(saved, ids){
  if(!Array.isArray(saved) || saved.length > ids.length) return [];
  const selected = saved.filter(Boolean);
  if(!saved.every(value=>typeof value === "string" && (!value || ids.includes(value)))
      || new Set(selected).size !== selected.length) return [];
  return saved.slice();
}

function asBuild(q, body, act, card){
  if(q.ordering){
    asOrdering(q, body, act, card);
    const note = document.createElement("p"); note.setAttribute("role", "note");
    note.textContent = "This ordering item needs a served itembank session. Open it with itembank serve or the daemon to submit a response.";
    body.appendChild(note);
    const submit = act.querySelector("button");
    if(submit){ submit.disabled = true; submit.onclick = null; }
    return;
  }
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
      const right = Array.isArray((v.explain||{}).steps) && (v.explain||{}).steps.length
        ? (v.explain||{}).steps : null;
      if(!right) return;
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
  ta.dataset.inputFormat = q.input_format || "plain";
  ta.placeholder = "Type your answer. Complete sentences; this is marked on what you actually wrote.";
  body.appendChild(ta);
  if(window.ItembankLatexInput && q.input_format === "latex")
    window.ItembankLatexInput.install(ta, body);
  const submit = mkSubmit(act, "your own words, no notes");
  ta.oninput = ()=>{ submit.disabled = ta.value.trim().length < 2; };
  ta.focus();
  submit.onclick = ()=>{
    ta.disabled = true;
    submit.remove();
    settle(q, ta.value.trim(), card, act, null);
  };
}

/* ---- check: vendored CodeMirror 6 code field ---------------------------- */
function asCheck(q, body, act, card){
  const cfg = (q.interaction_contract && q.interaction_contract.renderer_config) || {};
  const n = cfg.hidden_case_count || 0;
  const starter = q.starter || "";
  /* D-06 (plan 05-06): execution is server-side only, so a file:// page has
     no process to ask. Render the locked file-refusal sentence instead of
     the editor -- never a dead field the learner can type into and never
     submit -- and one skip control that advances without verifying, settling
     or closing: nothing is scored, nothing is recorded, and the item never
     reaches the auto-marked total (it is excluded exactly as if it were
     never reached). The honest-limits line below still renders from the
     item card. */
  if(!SERVE){
    const ref = document.createElement("div");
    ref.className = "pend";
    ref.textContent = "This item runs code on the machine serving itembank and can't be answered from a file opened directly in a browser. Open this bank with itembank serve (or the daemon) and try again.";
    body.appendChild(ref);
    const skip = document.createElement("button");
    skip.className = "go ghost"; skip.type = "button";
    skip.textContent = "Skip — not answerable offline";
    act.appendChild(skip);
    skip.onclick = ()=>{ i++; render(); };
    skip.focus();
    const lim2 = document.createElement("div");
    lim2.className = "hint";
    lim2.textContent = "__HONEST_LIMITS__";
    card.appendChild(lim2);
    return;
  }
  const wrap = document.createElement("div");
  wrap.className = "codewrap";
  const mount = document.createElement("div");
  wrap.appendChild(mount);
  body.appendChild(wrap);
  const submit = mkSubmit(act, caseHint(n));
  /* Locked hint copy (05-UI-SPEC Check button hint row): runs against %d
     hidden test case%s -- e.g. "runs against 1 hidden test case" /
     "runs against 3 hidden test cases". Hidden is locked: CASE) pairs are
     key material under D-12 and never reach public_item. */
  function caseHint(n){
    return n === 1 ? "runs against 1 hidden test case"
                   : "runs against " + n + " hidden test cases";
  }
  /* The editor's whole configuration -- line numbers, Tab/Shift-Tab keymap,
     placeholder, read-only lock, no wrap -- lives in the one boot script
     embedded above as a separate script, so the page and the JS test runner boot
     identical editors. The mount gets a semantic program label and concise
     keyboard instructions (05-UI-SPEC); Enter/Space activate the focused
     Check control natively (it is a real button). */
  mount.setAttribute("role", "textbox");
  mount.setAttribute("aria-label", "Source code");
  mount.setAttribute("aria-multiline", "true");
  const editor = CheckEditorBoot.create(mount, {starter: starter});
  const hintLine = document.createElement("div");
  hintLine.className = "hint";
  hintLine.textContent = "Tab inserts a tab, Shift-Tab dedents; the focused Check control activates with Enter or Space.";
  body.appendChild(hintLine);
  const sync = ()=>{ submit.disabled = editor.isEmpty(); };
  const origDispatch = editor.getView().dispatch;
  editor.getView().dispatch = function(tr){
    origDispatch.call(this, tr); sync();
  };
  sync();
  submit.onclick = ()=>{
    const src = editor.getSource();
    submit.disabled = true;
    submit.textContent = "Running…";
    editor.setReadOnly(true);
    settle(q, src, card, act, null, ()=>{ submit.textContent = "Submit answer"; submit.disabled = false; editor.setReadOnly(false); });
  };
  /* The honest-limits line renders from the item card, not from the editor
     branch, so plan 05-06's refusal states replace the editor without
     removing the statement. __HONEST_LIMITS__ is substituted by
     quiz.page_for from model.HONEST_LIMITS_NOTE (D-10). */
  const lim = document.createElement("div");
  lim.className = "hint";
  lim.textContent = "__HONEST_LIMITS__";
  card.appendChild(lim);
}

function mkSubmit(act, hint){
  const b = document.createElement("button");
  b.className="go"; b.type="button"; b.textContent="Submit answer"; b.disabled=true;
  const h = document.createElement("span"); h.className="hint"; h.textContent=hint;
  act.appendChild(b); act.appendChild(h);
  return b;
}

/* ---- check per-case readout (plan 05-06) ---------------------------------
   The learner's submitted source is their executable prediction; the ordered
   rows below are the bounded observations from that exact run, consumed from
   the shared normalized contract -- never scraped from prose, never a second
   verdict, never a re-run of the source. The overall verdict header stays
   the dichotomous runtime return; a null verdict (killed at timeout) renders
   the pending treatment, because a timeout is not a verdict (criterion 12). */
const CASE_STATUS = {
  passed:     ["Passed", ""],
  wrong_output:["Failed", ""],
  runtime_error:["Failed — program stopped with exit code %d", "warn"],
  timeout:    ["Failed — timed out after %ss", "warn"],
  output_cap: ["Failed — output was cut off at %d KB", "warn"]
};
function caseStatus(reason, timeoutSecs, capKB, exitCode){
  const [tmpl, role] = CASE_STATUS[reason] || ["Failed", ""];
  const text = reason === "timeout"
    ? tmpl.replace("%s", String(timeoutSecs))
    : reason === "output_cap" ? tmpl.replace("%d", String(capKB))
    : reason === "runtime_error" ? tmpl.replace("%d", String(exitCode)) : tmpl;
  return {text, role};
}
function checkMatrix(rows, timeoutSecs, capKB){
  let h = `<div class="check-matrix" role="list">`;
  rows.forEach(r=>{
    const st = caseStatus(r.reason, timeoutSecs, capKB, r.exit_code);
    const cls = r.passed ? "right" : "wrong";
    const warn = st.role === "warn" ? " warn" : "";
    h += `<div class="case ${cls}" role="listitem">
      <div class="case-head"><span class="case-n">Case ${r.case_index}</span>
        <span class="st${warn}">${esc(st.text)}</span></div>`;
    if(r.input) h += `<div class="cf"><h5>Input</h5><pre>${esc(r.input)}</pre></div>`;
    h += `<div class="cf"><h5>${r.expected_kind === "pattern" ? "Expected (pattern)" : "Expected"}</h5>
      <pre>${esc(r.expected)}</pre></div>`;
    h += `<div class="cf"><h5>Your output</h5><pre>${esc(r.actual || "")}</pre></div>`;
    if(r.reason === "runtime_error" && r.stderr)
      h += `<div class="cf"><h5>Error output</h5><pre>${esc(r.stderr)}</pre></div>`;
    h += `</div>`;
  });
  return h + `</div>`;
}

/* Offline-only row derivation: the static page holds the authored case
   halves in its explain payload and derives each observation's reason from
   the case flags plus the dichotomous score. Never a second verdict -- the
   header already came from canon()===key, and a null score (unanswered
   check) renders the pending header above. */
function checkRows(ex, v){
  return (ex.cases || []).map(c=>{
    const timed = !!c.timed_out, trunc = !!c.truncated;
    const failed = v.score === false;
    let reason = "passed";
    if(timed) reason = "timeout";
    else if(trunc) reason = "output_cap";
    else if(failed) reason = "wrong_output";
    return {case_index: c.case_index || 0, passed: !timed && !trunc && !failed,
            reason: reason, input: c.input || "", expected: c.expected || "",
            expected_kind: c.expected_kind || "output",
            actual: c.actual !== undefined ? c.actual : ""};
  });
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
      h += `<div class="blk note">The model answer is
        held back so it cannot contaminate the items after this one. It is in the bank file.`;
    }
  } else if(q.type === "check"){
    /* The per-case readout (plan 05-06). The offline page compares against
       the canonical key it shipped, so the rows derive from the explain
       payload's authored halves plus the score; the served page feeds the
       normalized observations instead. The verdict header above stays the
       dichotomous runtime return; a null verdict (killed at timeout)
       renders the pending treatment, never pass or fail (criterion 12). */
    h += checkMatrix(checkRows(ex, v), 5, 64);
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
  next.textContent = (i===Q.length-1)
    ? "View summary"
    : `Next question, ${i + 2} of ${Q.length}`;
  next.onclick = ()=>{ i++; render(); };
  act.appendChild(next);
  next.focus();
}

function finish(){
  document.getElementById("rail") && (document.getElementById("rail").style.width = "100%");
  const pct = autoTotal ? Math.round(score/autoTotal*100) : 0;
  const pend = Q.filter(q=>q.type==="short").length;
  let h = `<div class="done"><div class="score mono">${score}/${autoTotal}
    <span class="score-sub"> &middot; ${pct}% auto-marked</span></div>`;
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
