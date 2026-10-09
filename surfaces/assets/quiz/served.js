const BOOT = __BOOT__;
const SERVE = true;
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
let sessionId = null, i = 0, total = 0, score = 0, autoTotal = 0;
let currentActivity = null;
let shownAt = performance.now();
/* Phase 999.4 (LTI): the server includes the assignment-completion line in
   the final submit response; finish() renders it when present. Never a
   number or score claim -- the two UI-SPEC section-4 lines only. */
let LTI_COMPLETION = null;
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
  const payload = {session_id: sessionId, answer: response};
  if(currentActivity) for(const name of ["activity_id", "child_id", "submission_token"])
    payload[name] = currentActivity[name];
  const v = await api("/api/submit", payload);
  if(v.lti_completion) LTI_COMPLETION = v.lti_completion;
  return {action: v.action, score: v.score, explain: v.explain || {},
          next: v.next,
          selection_feedback: v.selection_feedback,
          ordering_diagnostic: v.ordering_diagnostic,
          refused: v.refused, refused_reason: v.refused_reason,
          entry_error: v.entry_error,
          interaction_result: v.interaction_result,
          activity_feedback: v.activity_feedback};
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

async function settle(q, response, card, act, paint, revert){
  const fb = feedbackFor(card);
  fb.innerHTML = `<div class="status">Checking answer&hellip;</div>`;
  let v;
  try {
    v = await verify(q, response);
  } catch(err){
    /* The server may have recorded this answer and advanced already.
       Never retransmit it against an unknown cursor. Keep the sent draft
       locked until a read reconciles the runtime's current question. */
    fb.innerHTML = `<div class="status">Couldn't confirm whether your answer
      was recorded. Your response is still here. Check the saved state before
      continuing.</div>`;
    act.innerHTML = "";
    const b = document.createElement("button");
    b.className = "go"; b.type = "button"; b.textContent = "Check saved state";
    b.onclick = async ()=>{
      b.disabled = true;
      try {
        const view = await api("/api/next", {session_id: sessionId});
        if(view && view.item && view.item.id === q.id && revert){
          act.innerHTML = "";
          revert();
          fb.innerHTML = `<div class="status">The session is still on this
            question. Review your response before submitting again.</div>`;
        } else {
          fb.innerHTML = `<div class="status">Saved state retrieved. Continue
            from the session's current position.</div>`;
          b.textContent = view && view.summary ? "View summary" : "Continue";
          b.onclick = ()=>renderItem(view);
          b.disabled = false;
        }
      } catch(recoveryError){
        fb.innerHTML = `<div class="status">Couldn't reach the saved session.
          Your response is still here. Check again when the connection returns.</div>`;
        b.disabled = false;
      }
    };
    act.appendChild(b);
    b.focus();
    return;
  }
  /* A rendering failure must never turn an acknowledged answer into a
     network retry. Paint only released verdicts, never a withheld answer. */
  const orderingAck = q.ordering && v.action === "defer_feedback" && v.next
    && (v.next.status === "complete" || (v.next.item && v.next.item.id !== q.id));
  if(paint && !v.refused && (v.action === "advance" || v.action === "complete" || orderingAck)) paint(v);
  close(q, card, act, v, revert);
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
  currentActivity = view.activity || null;
  setContext(q);
  const card = document.createElement("div");
  card.className = "card overhaul-question";
  card.innerHTML = questionStemHTML(q.fill_layout === "inline" ? String(q.stem).replace(/\{\{[a-z][a-z0-9_]{0,31}\}\}/g, "____") : q.stem);
  if(currentActivity){
    const context = document.createElement("section");
    context.className = "staged-context";
    context.dataset.activityStage = currentActivity.stage;
    context.setAttribute("aria-label", "Answer and reason");
    context.innerHTML = `<p>${esc(currentActivity.stimulus)}</p><p><b>${currentActivity.stage === "answer" ? "Step 1 of 2: answer." : "Step 2 of 2: reason."}</b> Commit each response once. Feedback follows both commitments.</p>`;
    if(Object.prototype.hasOwnProperty.call(currentActivity, "committed_answer"))
      context.innerHTML += `<p data-committed-answer>Your committed answer: <b>${esc(currentActivity.committed_answer)}</b>.</p>`;
    card.appendChild(context);
    if(activityDisclosure) activityDisclosure.textContent = document.getElementById("cx-mode").textContent === "exam"
      ? "Feedback after completion" : "Feedback after answer and reason";
  }
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
    short:asShort, fill:asFill, check:asCheck, visual:asVisual}[q.type])(q, body, act, card);
  /* AgentAssist (plan 08-05): the assist client resets per item so the
     Get optional guidance control targets the current item's operation. */
  if(window.Assist) window.Assist.onItem(q);
  /* Announce the new prompt before its answer controls. Focus continuity is
     accessibility state, not motion, so reduced-motion never disables it. */
  const heading = card.querySelector("h1.stem");
  if(heading) heading.focus({preventScroll:true});
  scrollCardIfNeeded(card);
}

/* ---- multiple choice (native radio) + multiple response (native checkboxes) */
const PINNED = /^\s*(all|none)\s+of\s+the\s+above|^\s*both\s+[A-H]\s+and\s+[A-H]/i;

function asChoice(q, body, act, card){
  const multi = q.type === "multi";
  const want = q.response_schema.select;
  /* Keep authored letters stable for cross-option references and the
     runtime's own-selection feedback, as the native form does. */
  const shown = q.options.map(o=>({...o, label:o.key}));

  const fieldset = document.createElement("fieldset");
  fieldset.className = "choices";
  const legend = document.createElement("legend");
  legend.textContent = multi ? `Select ${want}` : "Choose one";
  fieldset.appendChild(legend);
  const picked = [];       // holds ORIGINAL keys
  const boxes = {};
  let submit = null;
  const count = document.createElement("p");
  count.className = "hint";
  count.setAttribute("role", "status");
  count.setAttribute("aria-live", "polite");
  function updateCount(){
    if(multi) count.textContent = `Selected ${picked.length} of ${want}.`;
    if(submit) submit.disabled = multi ? picked.length !== want : picked.length !== 1;
  }
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
        updateCount();
        return;
      }
      if(input.checked){
        if(picked.length >= want){
          input.checked = false;
          count.textContent = `Selected ${want} of ${want}. Deselect an option before choosing another.`;
          return;
        }
        picked.push(o.key);
      } else {
        const at = picked.indexOf(o.key);
        if(at >= 0) picked.splice(at, 1);
      }
      updateCount();
    };
    boxes[o.key] = {label, input};
    fieldset.appendChild(label);
  });
  body.appendChild(fieldset);
  if(multi) body.appendChild(count);
  submit = mkSubmit(act, multi ? `select ${want}` : "choose one");
  updateCount();
  submit.onclick = go;
  function revert(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = false; });
    act.appendChild(submit);
    updateCount();
  }
  function go(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = true; });
    if(submit) submit.remove();
    settle(q, multi ? picked.slice() : picked[0], card, act, paint, revert);
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

function asMatching(q, body, act, card){
  const values = Object.create(null), controls = new Map();
  const once = q.matching.reuse === "once";
  const notice = document.createElement("p"); notice.setAttribute("role", "status");
  notice.textContent = once ? "Use each choice once. Unused choices are allowed." : "Choices can be reused. Match every row.";
  body.appendChild(notice);
  const storageKey = typeof BOOT !== "undefined" ? draftKey(BOOT.bank, q.id) : null;
  let saved = null;
  const signature = JSON.stringify([q.matching, q.rows]);
  if(storageKey) try{ const draft = JSON.parse(localStorage.getItem(storageKey)); saved = draft && draft.signature === signature ? draft.values : null; if(draft && !saved) notice.textContent = "The saved draft belongs to an older matching declaration. Choose again."; }catch(e){}
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
    if(saved && typeof saved[row.id] === "string" && q.categories.includes(saved[row.id])){
      select.value = saved[row.id]; values[row.id] = saved[row.id];
    }
    select.onchange = ()=>{
      values[row.id] = select.value; refresh();
      if(storageKey) try{ localStorage.setItem(storageKey, JSON.stringify({signature, values})); }catch(e){}
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
      if(storageKey) try{ localStorage.removeItem(storageKey); }catch(e){}
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
  let storageKey = null;
  try{
    if(BOOT && BOOT.bank && q.id){
      storageKey = draftKey(BOOT.bank, q.id);
      const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
      rows.forEach(r=>{
        const id = String(r.id);
        if(saved && typeof saved === "object" && !Array.isArray(saved)
            && q.categories.includes(saved[id])) chosen[id] = saved[id];
      });
    }
  }catch(e){ storageKey = null; }
  function saveDraft(){
    if(storageKey) try{ localStorage.setItem(storageKey, JSON.stringify(chosen)); }catch(e){}
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
        chosen[id]=c; saveDraft();
        bs.forEach(x=>x.setAttribute("aria-pressed", x.textContent===c?"true":"false"));
        submit.disabled = Object.keys(chosen).length !== q.rows.length;
        redrawBuckets();
      };
      b.setAttribute("aria-pressed", chosen[id] === c ? "true" : "false");
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
      select.value = chosen[id] || "";
      select.onchange = ()=>{
        if(select.value) chosen[id] = select.value;
        else delete chosen[id];
        saveDraft();
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
  submit.disabled = Object.keys(chosen).length !== q.rows.length;
  mountBuckets();
  function revert(){
    locked = false;
    rows.forEach(r=>segs[String(r.id)].forEach(b=>{ b.disabled = false; }));
    act.appendChild(submit);
    submit.disabled = Object.keys(chosen).length !== q.rows.length;
  }
  submit.onclick = ()=>{
    locked = true;
    rows.forEach(r=>segs[String(r.id)].forEach(b=>{ b.disabled = true; }));
    submit.remove();
    settle(q, Object.assign({}, chosen), card, act, v=>{
      if(storageKey) try{ localStorage.removeItem(storageKey); }catch(e){}
      const cats = (v.explain||{}).row_cats || {};
      rows.forEach(r=>{
        const id = String(r.id);
        if(!Object.prototype.hasOwnProperty.call(cats, id)) return;
        segs[id].forEach(b=>{
          if((b.tagName === "SELECT" ? b.value : b.textContent)===cats[id]) b.classList.add("right");
          else if((b.tagName === "SELECT" ? b.value : b.textContent)===chosen[id]) b.classList.add("wrong");
        });
      });
    }, revert);
  };
}

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
  let storageKey = null, focusIndex = null;
  if(typeof BOOT !== "undefined" && BOOT.bank) try{
    storageKey = draftKey(BOOT.bank, q.id);
    const saved = JSON.parse(localStorage.getItem(storageKey));
    if(saved && saved.signature === signature){
      const values = readOrderingDraft(saved.values, q.blocks.map(block=>block.id));
      selects.forEach((select,index)=>{ select.value = values[index] || ""; });
      focusIndex = saved.focus;
    }else if(saved){
      const notice = document.createElement("p"); notice.setAttribute("role", "status");
      notice.textContent = "The saved draft belongs to an older ordering declaration. Arrange the blocks again.";
      fieldset.prepend(notice);
    }
  }catch(e){}
  installOrderingControls(fieldset);
  const submit = mkSubmit(act, "submit selected blocks");
  submit.disabled = false;
  function save(){
    if(storageKey) try{ localStorage.setItem(storageKey, JSON.stringify({
      signature, values:selects.map(select=>select.value), focus:selects.indexOf(document.activeElement)
    })); }catch(e){}
  }
  fieldset.addEventListener("change", save); fieldset.addEventListener("focusin", save);
  if(Number.isInteger(focusIndex) && selects[focusIndex]) selects[focusIndex].focus();
  function lock(value){ selects.forEach(select=>{ select.disabled = value; }); fieldset.orderingRefresh(); }
  submit.onclick = ()=>{
    const response = selects.map(select=>select.value).filter(Boolean);
    lock(true); submit.remove();
    settle(q, response, card, act, ()=>{
      if(storageKey) try{ localStorage.removeItem(storageKey); }catch(e){}
    }, ()=>{ lock(false); act.appendChild(submit); submit.disabled = false; submit.focus(); });
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
  if(q.ordering) return asOrdering(q, body, act, card);
  const shown = shuffled(q.steps);
  let storageKey = null, order = [];
  try{
    storageKey = draftKey((BOOT && BOOT.bank) || "", q.id);
    order = readBuildDraft(JSON.parse(localStorage.getItem(storageKey) || "null"), q.steps);
  }catch(e){}
  function saveDraft(){
    if(storageKey) try{ localStorage.setItem(storageKey, JSON.stringify(order)); }catch(e){}
  }
  function complete(){ return order.length === q.steps.length && order.every(value=>value !== ""); }
  const wrap = document.createElement("div");
  wrap.className = "opts";
  const btns = shown.map(s=>{
    const b = document.createElement("button");
    b.className="opt"; b.type="button"; b.setAttribute("aria-pressed","false");
    b.innerHTML = `<span class="ord">-</span><span>${esc(s)}</span>`;
    b.onclick = ()=>{
      const at = order.indexOf(s);
      if(at>=0) order.splice(at,1);
      else{
        const gap = order.indexOf("");
        if(gap>=0) order[gap] = s; else order.push(s);
      }
      saveDraft(); redraw(); submit.disabled = !complete();
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
  redraw(); submit.disabled = !complete();
  function revert(){
    shown.forEach((s,n)=>{ btns[n].disabled = false; });
    act.appendChild(submit);
    redraw();
    submit.disabled = !complete();
  }
  submit.onclick = ()=>{
    shown.forEach((s,n)=>{ btns[n].disabled = true; });
    submit.remove();
    settle(q, order.slice(), card, act, v=>{
      if(storageKey) try{ localStorage.removeItem(storageKey); }catch(e){}
      const right = Array.isArray((v.explain||{}).steps) && (v.explain||{}).steps.length
        ? (v.explain||{}).steps : null;
      if(!right) return;
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
  ta.dataset.inputFormat = q.input_format || "plain";
  ta.placeholder = "Type your answer. Complete sentences; this is marked on what you actually wrote.";
  body.appendChild(ta);
  if(window.ItembankLatexInput && q.input_format === "latex")
    window.ItembankLatexInput.install(ta, body);
  const submit = mkSubmit(act, "your own words, no notes");
  ta.oninput = ()=>{ submit.disabled = ta.value.trim().length < 2; };
  ta.focus();
  function revert(){
    ta.disabled = false;
    act.appendChild(submit);
    submit.disabled = ta.value.trim().length < 2;
  }
  submit.onclick = ()=>{
    ta.disabled = true;
    submit.remove();
    settle(q, ta.value.trim(), card, act, null, revert);
  };
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

function asFill(q, body, act, card){
  const controls = fillFields(q, body);
  const ids = (q.fields || []).map(field=>String(field.id));
  const submit = mkSubmit(act, "complete every field");
  let storageKey = null;
  try {
    storageKey = draftKey((BOOT && BOOT.bank) || "", q.id);
    const saved = readFillDraft(JSON.parse(localStorage.getItem(storageKey) || "null"), ids);
    ids.forEach(id=>{
      if(Object.prototype.hasOwnProperty.call(saved, id)) controls[id].value = saved[id];
    });
  } catch(e) { storageKey = null; }
  const response = ()=>{
    const out = {};
    ids.forEach(id=>{ out[id] = controls[id].value; });
    return out;
  };
  const sync = ()=>{
    submit.disabled = ids.length === 0 || ids.some(id=>controls[id].value.length === 0);
    if(storageKey) try{ localStorage.setItem(storageKey, JSON.stringify(response())); }catch(e){}
  };
  ids.forEach(id=>{ controls[id].oninput = sync; });
  sync();
  function revert(){
    ids.forEach(id=>{ controls[id].disabled = false; });
    act.appendChild(submit);
    sync();
  }
  submit.onclick = ()=>{
    ids.forEach(id=>{ controls[id].disabled = true; });
    submit.remove();
    settle(q, response(), card, act, ()=>{
      if(storageKey) try{ localStorage.removeItem(storageKey); }catch(e){}
    }, revert);
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
  let storageKey = null;
  let initialSource = starter;
  try {
    storageKey = draftKey((BOOT && BOOT.bank) || "", q.id);
    const raw = localStorage.getItem(storageKey);
    const saved = raw === null ? null : JSON.parse(raw);
    if(Array.isArray(saved) && typeof saved[0] === "string") initialSource = saved[0];
  } catch(e) { storageKey = null; }
  const editor = CheckEditorBoot.create(mount, {starter: initialSource});
  const hintLine = document.createElement("div");
  hintLine.className = "hint";
  hintLine.textContent = "Tab inserts a tab, Shift-Tab dedents; the focused Check control activates with Enter or Space.";
  body.appendChild(hintLine);
  const sync = ()=>{ submit.disabled = editor.isEmpty(); };
  const origDispatch = editor.getView().dispatch;
  editor.getView().dispatch = function(tr){
    origDispatch.call(this, tr);
    if(storageKey) try{ localStorage.setItem(storageKey,
      JSON.stringify([editor.getSource()])); }catch(e){}
    sync();
  };
  sync();
  submit.onclick = ()=>{
    const src = editor.getSource();
    submit.disabled = true;
    submit.textContent = "Running…";
    editor.setReadOnly(true);
    settle(q, src, card, act, ()=>{
      if(storageKey) try{ localStorage.removeItem(storageKey); }catch(e){}
    }, ()=>{
      submit.textContent = "Submit answer";
      editor.setReadOnly(false);
      act.appendChild(submit);
      sync();
    });
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

/* ---- check per-case readout (plan 05-06) ---------------------------------
   The served client consumes the shared normalized observations
   (v.interaction_result.observations) -- the exact ordered rows the runtime
   built from the one run -- and never re-derives the verdict. The status
   line comes from the stable machine-readable `reason`; a bounded stop keeps
   the failure row but reads in the warning role. */
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


/* ---- visual assessment (plan 06.1-01) --------------------------------------
   asVisual is the one renderer-registry adapter for declarative plot and
   number-line contracts. It reads ONLY q.interaction_contract
   (renderer_config scene + response_schema), never a key, tolerance or
   scoring field. All input paths -- SVG pointer, tap, and the adjacent
   native semantic controls -- reduce through ONE state object and ONE
   serializer, so equivalent states produce byte-identical canonical SCALAR
   strings. The serialized semantic response is submitted through the normal
   served /api/submit path; this page never computes a verdict. */
/* ---- exact-fraction drawing helpers (phase 999.1, advanced families) --------
   DRAWING ONLY: these parse canonical SCALAR strings into [n,d] pairs for SVG
   layout. The submitted state is always the canonical SCALAR string or a
   stable id -- never this float, never a pixel. */
function vfGCD(a, b){ a = Math.abs(a); b = Math.abs(b);
  while(b){ const t = a % b; a = b; b = t; } return a || 1; }
function vfParse(s){
  if(typeof s !== "string") return null;
  s = s.trim();
  let m = s.match(/^([+-]?\d+)\/(\d+)$/);
  if(m){ let n = +m[1], d = +m[2]; if(!d) return null;
    const g = vfGCD(n, d); n /= g; d /= g;
    if(d < 0){ n = -n; d = -d; } return [n, d]; }
  m = s.match(/^([+-]?\d+)(?:\.(\d{1,6}))?$/);
  if(!m) return null;
  const sign = m[1][0] === "-" ? -1 : 1;
  const whole = Math.abs(+m[1]);
  let d = 1, frac = 0;
  if(m[2]){ d = Math.pow(10, m[2].length); frac = +m[2]; }
  let n = sign * (whole * d + frac);
  const g = vfGCD(n, d); n /= g; d /= g;
  if(d < 0){ n = -n; d = -d; } return [n, d];
}
function vfStr(f){ return f[1] === 1 ? String(f[0]) : f[0] + "/" + f[1]; }
function vfNum(s){ const f = vfParse(s); return f ? f[0] / f[1] : NaN; }
function vfAdd(a, b){ const n = a[0]*b[1] + b[0]*a[1], d = a[1]*b[1];
  const g = vfGCD(n, d); return [n/g, d/g]; }
function vfMul(a, k){ const n = a[0]*k, d = a[1]; const g = vfGCD(n, d);
  return [n/g, d/g]; }
function vfCmp(a, b){ return a[0]*b[1] - b[0]*a[1]; }
function vfPos(f, mn, mx){
  const num = (f[0]*mn[1] - mn[0]*f[1]) * mx[1];
  const den = (mx[0]*mn[1] - mn[0]*mx[1]) * f[1];
  if(!den) return 0;
  return Math.max(0, Math.min(1, num / den));
}
function vfTicks(axis){
  const lo = vfParse(axis.min), hi = vfParse(axis.max), st = vfParse(axis.step);
  if(!lo || !hi || !st || st[0] <= 0) return [];
  const out = [];
  for(let k = 0; ; k++){
    const f = vfAdd(lo, vfMul(st, k));
    if(vfCmp(f, hi) > 0) break;
    out.push({v: vfStr(f), f});
  }
  return out;
}

/* ActionStatus remains persistently polite for ordinary visual updates, as
   required by 06.1. Blocking failures promote it to an assertive alert before
   changing the text, so assistive technology cannot observe alert + live-off
   or miss the failure because content changed first. */
function setVisualStatus(status, text, isError){
  if(isError){
    status.setAttribute("role", "alert");
    status.setAttribute("aria-live", "assertive");
  } else {
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
  }
  status.textContent = text;
}

/* ---- timeline renderer (phase 999.1-02) ------------------------------------
   Time-series placement: the learner picks one authored event and places it
   at a canonical SCALAR time value on an axis. Scene comes from the
   interaction_contract renderer_config only (axis, events, initial, actions,
   accessibility) -- never the answer value or any scoring field. Pointer,
   keyboard and the event/value select controls reduce through ONE state
   object and ONE serializer; a changed explicit commit posts
   place_timeline_event / move_timeline_event through /api/interact. */
function renderTimeline(q, c, body, act, card){
  const rc = c.renderer_config || {};
  const axis = rc.axis || {min:"0", max:"10", step:"1"};
  const events = Array.isArray(rc.events) ? rc.events : [];
  const initial = rc.initial || {};
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const W = 400, H = 130, L = 34, R = 14, T = 24, B = 40;
  const mid = T + (H - T - B) / 2;
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  const tks = vfTicks(axis);
  const mn = vfParse(axis.min), mx = vfParse(axis.max);
  const step = vfParse(axis.step);
  function X(v){ return L + vfPos(vfParse(v), mn, mx) * (W - L - R); }

  const committed = {kind:"timeline_event", event: null, value: null};
  const tentative = {kind:"timeline_event", event: null, value: null};
  const pl = (initial.placements && initial.placements.length)
    ? initial.placements[0] : null;
  if(pl){ committed.event = pl.event; committed.value = pl.value; }
  Object.assign(tentative, committed);
  let selected = committed.event;    /* which event chip the learner moves */

  function snapshot(s){ return {kind:"timeline_event", event: s.event, value: s.value}; }
  function sameState(a, b){ return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b)); }
  function filled(s){ return !!(s.event && s.value); }
  function eventLabel(id){ const ev = events.find(e => e.id === id); return ev ? ev.label : id; }
  function adopt(s){ committed.event = s.event; committed.value = s.value; }
  function revertTentative(){
    tentative.event = committed.event; tentative.value = committed.value;
    draw(tentative); syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  function draw(s){
    let h = `<line x1="${L}" y1="${mid}" x2="${W-R}" y2="${mid}" stroke="currentColor"/>`;
    tks.forEach(tk=>{
      const x = X(tk.v);
      h += `<line x1="${x}" y1="${mid-5}" x2="${x}" y2="${mid+5}" stroke="currentColor"/>`;
      h += `<text x="${x}" y="${mid+20}" font-size="10" text-anchor="middle">${esc(tk.v)}</text>`;
    });
    if(s.event && s.value){
      const x = X(s.value);
      const isCommitted = sameState(s, committed);
      h += `<line x1="${x}" y1="${mid-8}" x2="${x}" y2="${mid+8}" stroke="var(--accent)" stroke-width="2"/>`;
      h += `<text x="${x}" y="${mid-12}" font-size="11" text-anchor="middle" fill="var(--accent)">${esc(eventLabel(s.event))}</text>`;
      if(!isCommitted){
        h += `<text x="${x}" y="${mid+38}" font-size="10" text-anchor="middle" fill="var(--accent)">${esc(s.value)}</text>`;
      }
    }
    svg.innerHTML = h;
  }

  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, ch=>{
        const r = Math.random()*16|0, v = ch==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));

  async function commitMove(){
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId, interaction_version: c.version,
        action_id: aid,
        action_type: filled(committed) ? "move_timeline_event" : "place_timeline_event",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  function snapTick(clientX){
    const r = svg.getBoundingClientRect();
    const px = (clientX - r.left) / r.width * W;
    let best = tks[0], bestD = Infinity;
    tks.forEach(tk=>{
      const d = Math.abs(X(tk.v) - px);
      if(d < bestD){ bestD = d; best = tk; }
    });
    return best;
  }

  svg.addEventListener("pointerdown", e => e.preventDefault());
  svg.addEventListener("pointerup", e => {
    const hit = snapTick(e.clientX);
    if(!hit || !selected) return;
    const before = JSON.stringify(snapshot(tentative));
    tentative.event = selected;
    tentative.value = hit.v;
    draw(tentative); syncControls();
    if(JSON.stringify(snapshot(tentative)) !== before) commitMove();
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    if((e.key === "ArrowLeft" || e.key === "ArrowRight") && step){
      e.preventDefault();
      if(!selected) selected = events[0] ? events[0].id : null;
      const at = tks.findIndex(t => t.v === tentative.value);
      const delta = e.key === "ArrowLeft" ? -1 : 1;
      const nxt = tks[Math.max(0, Math.min(tks.length-1, (at < 0 ? 0 : at) + delta))];
      tentative.event = selected;
      tentative.value = nxt.v;
      draw(tentative); syncControls();
      return;
    }
    if(e.key === "Enter" || e.key === " "){ e.preventDefault(); commitMove(); return; }
    if(e.key === "Escape"){ e.preventDefault(); revertTentative(); }
  });

  const controls = document.createElement("div");
  controls.className = "visual-controls";
  const evSel = document.createElement("select");
  events.forEach(ev=>{
    const o = document.createElement("option");
    o.value = ev.id; o.textContent = ev.label; evSel.appendChild(o);
  });
  evSel.onchange = ()=>{
    selected = evSel.value;
    tentative.event = evSel.value;
    draw(tentative);
  };
  const valSel = document.createElement("select");
  tks.forEach(tk=>{
    const o = document.createElement("option");
    o.value = tk.v; o.textContent = tk.v; valSel.appendChild(o);
  });
  valSel.onchange = ()=>{
    tentative.value = valSel.value;
    draw(tentative);
  };
  controls.appendChild(labelCtl("event", evSel));
  controls.appendChild(labelCtl("value", valSel));
  host.appendChild(controls);
  function labelCtl(label, sel){
    const row = document.createElement("label");
    row.className = "visual-ctl";
    row.appendChild(document.createTextNode(label + " "));
    row.appendChild(sel);
    return row;
  }
  function syncControls(){
    if(evSel.value !== tentative.event) evSel.value = tentative.event || "";
    if(tentative.value && valSel.value !== tentative.value) valSel.value = tentative.value;
  }

  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);

  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);
  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true; commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };
}

/* ---- diagram renderer (phase 999.1-03) -------------------------------------
   Node-connection: the learner connects one authored node to another. Scene
   comes from the interaction_contract renderer_config only (plane, nodes,
   initial, actions, accessibility) -- never the answer connection or any
   scoring field. Pointer (click source then target), keyboard and the
   from/to select controls reduce through ONE state object and ONE
   serializer; a changed explicit commit posts connect_diagram. */
function renderDiagram(q, c, body, act, card){
  const rc = c.renderer_config || {};
  const plane = rc.plane || {width:"8", height:"6"};
  const nodes = Array.isArray(rc.nodes) ? rc.nodes : [];
  const initial = rc.initial || {};
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const W = 400, H = 240, R = 16;
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  const Wf = vfNum(plane.width) || 8, Hf = vfNum(plane.height) || 6;
  function X(n){ return vfNum(n.x) / Wf * (W - 2) + 1; }
  function Y(n){ return vfNum(n.y) / Hf * (H - 2) + 1; }
  function nodeAt(clientX, clientY){
    const r = svg.getBoundingClientRect();
    const x = (clientX - r.left) / r.width * W;
    const y = (clientY - r.top) / r.height * H;
    let best = null, bestD = Infinity;
    nodes.forEach(n=>{
      const dx = x - X(n), dy = y - Y(n);
      const d = Math.sqrt(dx*dx + dy*dy);
      if(d < bestD){ bestD = d; best = n; }
    });
    return (best && bestD <= R) ? best : null;
  }

  const committed = {kind:"diagram_connection", from: null, to: null};
  const tentative = {kind:"diagram_connection", from: null, to: null};
  const conn = (initial.connections && initial.connections.length)
    ? initial.connections[0] : null;
  if(conn){ committed.from = conn.from; committed.to = conn.to; }
  Object.assign(tentative, committed);

  function snapshot(s){ return {kind:"diagram_connection", from: s.from, to: s.to}; }
  function sameState(a, b){ return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b)); }
  function filled(s){ return !!(s.from && s.to); }
  function label(id){ const n = nodes.find(n => n.id === id); return n ? n.label : id; }
  function adopt(s){ committed.from = s.from; committed.to = s.to; }
  function revertTentative(){
    tentative.from = committed.from; tentative.to = committed.to;
    draw(tentative); syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  function draw(s){
    let h = `<rect x="1" y="1" width="${W-2}" height="${H-2}" fill="var(--card)" stroke="currentColor"/>`;
    if(s.from && s.to){
      const a = nodes.find(n => n.id === s.from), b = nodes.find(n => n.id === s.to);
      if(a && b){
        const x1 = X(a), y1 = Y(a), x2 = X(b), y2 = Y(b);
        const ang = Math.atan2(y2 - y1, x2 - x1);
        const tipX = x2 - Math.cos(ang) * (R + 4), tipY = y2 - Math.sin(ang) * (R + 4);
        h += `<line x1="${x1}" y1="${y1}" x2="${tipX}" y2="${tipY}" stroke="var(--accent)" stroke-width="2"/>`;
        h += `<polygon points="${tipX},${tipY} ${tipX - 9*Math.cos(ang - 0.45)},${tipY - 9*Math.sin(ang - 0.45)} ${tipX - 9*Math.cos(ang + 0.45)},${tipY - 9*Math.sin(ang + 0.45)}" fill="var(--accent)"/>`;
      }
    }
    nodes.forEach(n=>{
      const x = X(n), y = Y(n);
      const isFrom = s.from === n.id, isTo = s.to === n.id;
      h += `<circle cx="${x}" cy="${y}" r="${R}" fill="${isFrom || isTo ? "var(--accent)" : "var(--chip)"}" stroke="currentColor"/>`;
      h += `<text x="${x}" y="${y}" font-size="11" text-anchor="middle" dominant-baseline="middle" fill="var(--ink)">${esc(label(n.id))}</text>`;
    });
    svg.innerHTML = h;
  }

  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, ch=>{
        const r = Math.random()*16|0, v = ch==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));

  async function commitMove(){
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId, interaction_version: c.version,
        action_id: aid, action_type: "connect_diagram",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  svg.addEventListener("pointerdown", e => e.preventDefault());
  svg.addEventListener("pointerup", e => {
    const hit = nodeAt(e.clientX, e.clientY);
    if(!hit) return;
    const before = JSON.stringify(snapshot(tentative));
    if(!tentative.from){
      tentative.from = hit.id;
    } else if(!tentative.to){
      if(hit.id === tentative.from){
        tentative.from = null;
      } else {
        tentative.to = hit.id;
      }
    } else {
      tentative.from = hit.id; tentative.to = null;
    }
    draw(tentative); syncControls();
    if(JSON.stringify(snapshot(tentative)) !== before) commitMove();
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    if(e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "ArrowUp" || e.key === "ArrowDown"){
      e.preventDefault();
      if(!nodes.length) return;
      const cur = tentative.to || tentative.from || nodes[0].id;
      const at = nodes.findIndex(n => n.id === cur);
      const delta = (e.key === "ArrowLeft" || e.key === "ArrowUp") ? -1 : 1;
      const nxt = nodes[Math.max(0, Math.min(nodes.length - 1, (at < 0 ? 0 : at) + delta))];
      if(tentative.to){ tentative.to = nxt.id; } else { tentative.from = nxt.id; }
      draw(tentative); syncControls();
      return;
    }
    if(e.key === "Enter" || e.key === " "){ e.preventDefault(); commitMove(); return; }
    if(e.key === "Escape"){ e.preventDefault(); revertTentative(); }
  });

  const controls = document.createElement("div");
  controls.className = "visual-controls";
  function nodeSelect(onPick){
    const sel = document.createElement("select");
    nodes.forEach(n=>{
      const o = document.createElement("option");
      o.value = n.id; o.textContent = n.label; sel.appendChild(o);
    });
    sel.onchange = ()=>{ onPick(sel.value); };
    return sel;
  }
  const fromSel = nodeSelect(v => { tentative.from = v; draw(tentative); });
  const toSel = nodeSelect(v => { tentative.to = v; draw(tentative); });
  controls.appendChild(labelCtl("from", fromSel));
  controls.appendChild(labelCtl("to", toSel));
  host.appendChild(controls);
  function labelCtl(label, sel){
    const row = document.createElement("label");
    row.className = "visual-ctl";
    row.appendChild(document.createTextNode(label + " "));
    row.appendChild(sel);
    return row;
  }
  function syncControls(){
    if(tentative.from && fromSel.value !== tentative.from) fromSel.value = tentative.from;
    if(tentative.to && toSel.value !== tentative.to) toSel.value = tentative.to;
  }

  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);

  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);
  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true; commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };
}

/* ---- trace renderer (phase 999.1-03) ---------------------------------------
   Re-trace a reference polyline: the learner places an ordered list of
   point_count points. Scene comes from the interaction_contract
   renderer_config only (axes, point_count, initial reference path, actions,
   accessibility) -- the answer path stays in the private SCORING envelope
   and is never rendered. Pointer (click places the next point in order),
   keyboard, and per-point x/y selects reduce through ONE state object and
   ONE serializer; a changed explicit commit posts place_trace_point /
   move_trace_point with the full canonical path. */
function renderTrace(q, c, body, act, card){
  const rc = c.renderer_config || {};
  const axes = rc.axes || {};
  const ax = {x: axes.x || {min:"0", max:"4", step:"1"},
              y: axes.y || {min:"0", max:"4", step:"1"}};
  const pointCount = (typeof rc.point_count === "number" && rc.point_count >= 1)
    ? rc.point_count : 1;
  const initial = rc.initial || {};
  const ref = Array.isArray(initial.points) ? initial.points : [];
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const W = 400, H = 240, L = 34, R = 10, T = 14, B = 26;
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  const xTicks = vfTicks(ax.x), yTicks = vfTicks(ax.y);
  const mnX = vfParse(ax.x.min), mxX = vfParse(ax.x.max);
  const mnY = vfParse(ax.y.min), mxY = vfParse(ax.y.max);
  function X(v){ return L + vfPos(vfParse(v), mnX, mxX) * (W - L - R); }
  function Y(v){ return H - B - vfPos(vfParse(v), mnY, mxY) * (H - T - B); }
  function snap(tks, f){
    let best = tks[0], bestD = Infinity;
    tks.forEach(tk=>{
      const d = Math.abs(vfCmp(f, tk.f));
      if(d < bestD){ bestD = d; best = tk; }
    });
    return best;
  }
  function domain(clientX, clientY, tks, mn, mx, isY){
    const r = svg.getBoundingClientRect();
    const t = Math.max(0, Math.min(1, isY
      ? (1 - (clientY - r.top) / r.height)
      : (clientX - r.left) / r.width));
    const f = [mn[0]*mx[1] + Math.round(t * (mx[0]*mn[1] - mn[0]*mx[1])), mn[1]*mx[1]];
    const g = vfGCD(f[0], f[1]); return snap(tks, [f[0]/g, f[1]/g]);
  }

  const committed = {kind:"trace_path", points: []};
  const tentative = {kind:"trace_path", points: []};
  /* The reference polyline (`ref`, from initial.points) is scene data drawn
     for orientation only -- the learner's placed points start empty and the
     submitted path is exactly what they place. The answer path never
     leaves the server. */
  tentative.points = committed.points.map(p => ({x: p.x, y: p.y}));

  function snapshot(s){
    return {kind:"trace_path",
            points: s.points.map(p => ({x: p.x, y: p.y}))};
  }
  function sameState(a, b){ return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b)); }
  function filled(s){ return s.points.length === pointCount; }
  function adopt(s){ committed.points = s.points.map(p => ({x: p.x, y: p.y})); }
  function revertTentative(){
    tentative.points = committed.points.map(p => ({x: p.x, y: p.y}));
    draw(tentative); syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  function draw(s){
    let h = `<line x1="${L}" y1="${H-B}" x2="${W-R}" y2="${H-B}" stroke="currentColor"/>`;
    h += `<line x1="${L}" y1="${T}" x2="${L}" y2="${H-B}" stroke="currentColor"/>`;
    xTicks.forEach(tk=>{
      const x = X(tk.v);
      h += `<line x1="${x}" y1="${H-B}" x2="${x}" y2="${H-B+5}" stroke="currentColor"/>`;
      h += `<text x="${x}" y="${H-B+18}" font-size="10" text-anchor="middle">${esc(tk.v)}</text>`;
    });
    yTicks.forEach(tk=>{
      const y = Y(tk.v);
      h += `<line x1="${L-5}" y1="${y}" x2="${L}" y2="${y}" stroke="currentColor"/>`;
      h += `<text x="${L-8}" y="${y+3}" font-size="10" text-anchor="end">${esc(tk.v)}</text>`;
    });
    if(ref.length >= 2){
      const pts = ref.map(p => X(p.x) + "," + Y(p.y)).join(" ");
      h += `<polyline points="${pts}" fill="none" stroke="var(--line)" stroke-width="2" stroke-dasharray="4 3"/>`;
    }
    if(s.points.length >= 2){
      const pts = s.points.map(p => X(p.x) + "," + Y(p.y)).join(" ");
      h += `<polyline points="${pts}" fill="none" stroke="var(--accent)" stroke-width="2"/>`;
    }
    s.points.forEach((p, i)=>{
      const x = X(p.x), y = Y(p.y);
      h += `<circle cx="${x}" cy="${y}" r="6" fill="var(--accent)" stroke="var(--ink)"/>`;
      h += `<text x="${x+9}" y="${y-6}" font-size="10" fill="var(--accent)">${i+1}</text>`;
    });
    svg.innerHTML = h;
  }

  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, ch=>{
        const r = Math.random()*16|0, v = ch==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));

  async function commitMove(){
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId, interaction_version: c.version,
        action_id: aid,
        action_type: filled(committed) ? "move_trace_point" : "place_trace_point",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  svg.addEventListener("pointerdown", e => e.preventDefault());
  svg.addEventListener("pointerup", e => {
    if(tentative.points.length >= pointCount) return;
    const tkX = domain(e.clientX, e.clientY, xTicks, mnX, mxX, false);
    const tkY = domain(e.clientY, e.clientX, yTicks, mnY, mxY, true);
    tentative.points.push({x: tkX.v, y: tkY.v});
    draw(tentative); syncControls();
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    if(e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "ArrowUp" || e.key === "ArrowDown"){
      e.preventDefault();
      if(!tentative.points.length) return;
      const last = tentative.points[tentative.points.length - 1];
      const moveX = e.key === "ArrowLeft" || e.key === "ArrowRight";
      const tks = moveX ? xTicks : yTicks;
      const at = tks.findIndex(t => t.v === (moveX ? last.x : last.y));
      const delta = (e.key === "ArrowLeft" || e.key === "ArrowDown") ? -1 : 1;
      const nxt = tks[Math.max(0, Math.min(tks.length-1, (at < 0 ? 0 : at) + delta))];
      if(moveX) last.x = nxt.v; else last.y = nxt.v;
      draw(tentative); syncControls();
      return;
    }
    if(e.key === "Enter" || e.key === " "){ e.preventDefault(); commitMove(); return; }
    if(e.key === "Escape"){ e.preventDefault(); revertTentative(); }
  });

  const controls = document.createElement("div");
  controls.className = "visual-controls";
  function valueSelect(tks, onPick){
    const sel = document.createElement("select");
    tks.forEach(tk=>{
      const o = document.createElement("option");
      o.value = tk.v; o.textContent = tk.v; sel.appendChild(o);
    });
    sel.onchange = ()=>{ onPick(sel.value); };
    return sel;
  }
  const selPairs = [];
  for(let i = 0; i < pointCount; i++){
    const sx = valueSelect(xTicks, v => {
      if(!tentative.points[i]) tentative.points[i] = {x: v, y: null};
      tentative.points[i].x = v; draw(tentative);
    });
    const sy = valueSelect(yTicks, v => {
      if(!tentative.points[i]) tentative.points[i] = {x: null, y: v};
      tentative.points[i].y = v; draw(tentative);
    });
    selPairs.push([sx, sy]);
    const row = document.createElement("label");
    row.className = "visual-ctl";
    row.appendChild(document.createTextNode("p" + (i+1) + " "));
    row.appendChild(sx);
    row.appendChild(sy);
    controls.appendChild(row);
  }
  const clearBtn = document.createElement("button");
  clearBtn.type = "button"; clearBtn.className = "go ghost";
  clearBtn.textContent = "Clear last point";
  clearBtn.onclick = ()=>{
    if(tentative.points.length) tentative.points.pop();
    draw(tentative); syncControls();
  };
  controls.appendChild(clearBtn);
  host.appendChild(controls);
  function syncControls(){
    for(let i = 0; i < pointCount; i++){
      const p = tentative.points[i];
      if(p){
        if(selPairs[i][0].value !== p.x) selPairs[i][0].value = p.x || "";
        if(selPairs[i][1].value !== p.y) selPairs[i][1].value = p.y || "";
      }
    }
  }

  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);

  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);
  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true; commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };
}

/* ---- hotspot renderer (phase 999.1-01) -------------------------------------
   Click-on-region mapping: the learner selects one named region of a plane.
   Scene comes from q.interaction_contract.renderer_config only (plane,
   regions, initial, actions, accessibility) -- never the answer region or
   any scoring field. Pointer, keyboard and the radio-list semantic control
   reduce through ONE state object and ONE serializer; a changed explicit
   commit posts a single select_hotspot action through /api/interact and the
   final submit stays the ordinary response event. */
function renderHotspot(q, c, body, act, card){
  const rc = c.renderer_config || {};
  const plane = rc.plane || {width:"10", height:"6"};
  const regions = Array.isArray(rc.regions) ? rc.regions : [];
  const initial = rc.initial || {};
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const W = 400, H = 240;
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  /* plane units -> svg pixels (DRAWING ONLY; the submitted state is a region
     id, never a coordinate). */
  function num(s){
    if(typeof s !== "string") return NaN;
    const m = s.trim().match(/^([+-]?\d+)\/(\d+)$/);
    if(m) return (+m[1]) / (+m[2]);
    return parseFloat(s);
  }
  const Wf = num(plane.width) || 10, Hf = num(plane.height) || 6;
  function SX(x){ return num(x) / Wf * W; }
  function SY(y){ return num(y) / Hf * H; }

  function contains(reg, x, y){
    const co = reg.coords || [];
    if(reg.shape === "rect" && co.length === 4){
      return x >= SX(co[0]) && x <= SX(co[0]) + SX(co[2])
          && y >= SY(co[1]) && y <= SY(co[1]) + SY(co[3]);
    }
    if(reg.shape === "circle" && co.length === 3){
      const dx = x - SX(co[0]), dy = y - SY(co[1]);
      return dx * dx + dy * dy <= SX(co[2]) * SX(co[2]);
    }
    if(reg.shape === "polygon" && co.length >= 3){
      let inside = false;
      for(let i = 0, j = co.length - 1; i < co.length; j = i++){
        const xi = SX(co[i][0]), yi = SY(co[i][1]);
        const xj = SX(co[j][0]), yj = SY(co[j][1]);
        if(((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi))
          inside = !inside;
      }
      return inside;
    }
    return false;
  }

  function shapePath(reg){
    const co = reg.coords || [];
    if(reg.shape === "rect" && co.length === 4)
      return `<rect x="${SX(co[0])}" y="${SY(co[1])}" width="${SX(co[2])}" height="${SY(co[3])}"/>`;
    if(reg.shape === "circle" && co.length === 3)
      return `<circle cx="${SX(co[0])}" cy="${SY(co[1])}" r="${SX(co[2])}"/>`;
    if(reg.shape === "polygon" && co.length >= 3)
      return `<polygon points="${co.map(v => SX(v[0]) + "," + SY(v[1])).join(" ")}"/>`;
    return "";
  }

  function draw(s){
    let h = `<rect x="1" y="1" width="${W-2}" height="${H-2}" fill="var(--card)" stroke="currentColor"/>`;
    regions.forEach(reg=>{
      const sel = s.region === reg.id;
      h += shapePath(reg).replace(/>$/, ` fill="${sel ? "var(--accent)" : "var(--card)"}" stroke="currentColor" stroke-width="1.5"/>`);
      const co = reg.coords || [];
      let lx = 0, ly = 0;
      if(reg.shape === "rect" && co.length >= 2){ lx = SX(co[0]) + SX(co[2])/2; ly = SY(co[1]) + SY(co[3])/2; }
      else if(reg.shape === "circle" && co.length >= 2){ lx = SX(co[0]); ly = SY(co[1]); }
      else if(reg.shape === "polygon" && co.length >= 1){
        co.forEach(v => { lx += SX(v[0]); ly += SY(v[1]); });
        lx /= co.length; ly /= co.length;
      }
      h += `<text x="${lx}" y="${ly}" font-size="11" text-anchor="middle" dominant-baseline="middle" fill="var(--ink)">${esc(reg.label)}</text>`;
    });
    svg.innerHTML = h;
  }

  /* ---- state: committed vs tentative (D-04/D-05) --------------------------- */
  const committed = {kind:"hotspot", region: (initial.region) || null};
  const tentative = {kind:"hotspot", region: (initial.region) || null};
  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, ch=>{
        const r = Math.random()*16|0, v = ch==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));
  function snapshot(s){ return {kind:"hotspot", region: s.region}; }
  function sameState(a, b){ return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b)); }
  function filled(s){ return !!s.region; }
  function adopt(s){ committed.region = s.region; }
  function revertTentative(){
    tentative.region = committed.region;
    draw(tentative);
    syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  async function commitMove(){
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId, interaction_version: c.version,
        action_id: aid, action_type: "select_hotspot",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  svg.addEventListener("pointerdown", e => e.preventDefault());
  svg.addEventListener("pointerup", e => {
    const r = svg.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width * W;
    const y = (e.clientY - r.top) / r.height * H;
    const hit = regions.find(reg => contains(reg, x, y));
    if(!hit) return;
    const before = JSON.stringify(snapshot(tentative));
    tentative.region = hit.id;
    draw(tentative);
    syncControls();
    if(JSON.stringify(snapshot(tentative)) !== before) commitMove();
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    if(e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "ArrowUp" || e.key === "ArrowDown"){
      e.preventDefault();
      const at = regions.findIndex(r => r.id === tentative.region);
      const delta = (e.key === "ArrowLeft" || e.key === "ArrowUp") ? -1 : 1;
      if(regions.length){
        const nxt = regions[Math.max(0, Math.min(regions.length - 1, (at < 0 ? 0 : at) + delta))];
        tentative.region = nxt.id;
        draw(tentative); syncControls();
      }
      return;
    }
    if(e.key === "Enter" || e.key === " "){ e.preventDefault(); commitMove(); return; }
    if(e.key === "Escape"){ e.preventDefault(); revertTentative(); }
  });

  /* ---- adjacent semantic HTML control: radio list of region labels ------- */
  const controls = document.createElement("div");
  controls.className = "visual-controls";
  const radios = [];
  regions.forEach(reg=>{
    const row = document.createElement("label");
    row.className = "visual-ctl";
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "hotspot-region";
    radio.value = reg.id;
    radio.onchange = ()=>{
      tentative.region = reg.id;
      draw(tentative);
      commitMove();
    };
    radios.push(radio);
    row.appendChild(radio);
    row.appendChild(document.createTextNode(" " + reg.label));
    controls.appendChild(row);
  });
  host.appendChild(controls);
  function syncControls(){
    radios.forEach(r => { r.checked = r.value === tentative.region; });
  }

  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);

  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);
  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true; commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };
}

function asVisual(q, body, act, card){
  const c = q.interaction_contract || {};
  const interaction = (c.interaction || "").trim();
  if(interaction === "hotspot") return renderHotspot(q, c, body, act, card);
  if(interaction === "timeline") return renderTimeline(q, c, body, act, card);
  if(interaction === "diagram") return renderDiagram(q, c, body, act, card);
  if(interaction === "trace") return renderTrace(q, c, body, act, card);
  const rc = c.renderer_config || {};
  const kind = (c.response_schema || {}).kind || "point";
  const axes = rc.axes || {};
  const axis = rc.axis || {min:"0", max:"1", step:"1"};
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const initial = rc.initial || {};
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 400 240");
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const submit = mkSubmit(act, "commit your placement");

  /* ---- exact SCALAR arithmetic: parse "2" | "1/2" | "2.5" to [n,d] -------- */
  function fracGCD(a, b){ a = Math.abs(a); b = Math.abs(b);
    while(b){ const t = a % b; a = b; b = t; } return a || 1; }
  function fracParse(s){
    if(typeof s !== "string") return null;
    s = s.trim();
    let m = s.match(/^([+-]?\d+)\/(\d+)$/);
    if(m){ let n = +m[1], d = +m[2]; if(!d) return null;
      const g = fracGCD(n, d); n /= g; d /= g;
      if(d < 0){ n = -n; d = -d; } return [n, d]; }
    m = s.match(/^([+-]?\d+)(?:\.(\d{1,6}))?$/);
    if(!m) return null;
    const sign = m[1][0] === "-" ? -1 : 1;
    const whole = Math.abs(+m[1]);
    let d = 1, frac = 0;
    if(m[2]){ d = Math.pow(10, m[2].length); frac = +m[2]; }
    let n = sign * (whole * d + frac);
    const g = fracGCD(n, d); n /= g; d /= g;
    if(d < 0){ n = -n; d = -d; } return [n, d];
  }
  function fracStr(f){ return f[1] === 1 ? String(f[0]) : f[0] + "/" + f[1]; }
  function fracAdd(a, b){ const n = a[0]*b[1] + b[0]*a[1], d = a[1]*b[1];
    const g = fracGCD(n, d); return [n/g, d/g]; }
  function fracMulInt(a, k){ const n = a[0]*k, d = a[1];
    const g = fracGCD(n, d); return [n/g, d/g]; }
  function fracSub(a, b){ return fracAdd(a, [-b[0], b[1]]); }
  function fracCmp(a, b){ return a[0]*b[1] - b[0]*a[1]; }   /* sign of a-b */

  /* ticks(min,max,step) -> [{v: canonical scalar string, f: [n,d]}] */
  function ticks(ax){
    const lo = fracParse(ax.min), hi = fracParse(ax.max), st = fracParse(ax.step);
    if(!lo || !hi || !st || st[0] <= 0) return [];
    const out = [];
    for(let k = 0; ; k++){
      const f = fracAdd(lo, fracMulInt(st, k));
      if(fracCmp(f, hi) > 0) break;
      out.push({v: fracStr(f), f});
    }
    return out;
  }
  /* normalized position of fraction f between mn and mx, as a float in [0,1]
     -- used for DRAWING ONLY; the submitted value is always a canonical
     SCALAR string, never this float. */
  function toFrac(f, mn, mx){
    const num = (f[0]*mn[1] - mn[0]*f[1]) * mx[1];
    const den = (mx[0]*mn[1] - mn[0]*mx[1]) * f[1];
    if(!den) return 0;
    return num / den;
  }
  function clamp01(t){ return Math.max(0, Math.min(1, t)); }
  function snap(tks, f){
    let best = 0, bestDist = Infinity;
    for(let k = 0; k < tks.length; k++){
      const d = Math.abs(fracCmp(f, tks[k].f));
      if(d < bestDist){ bestDist = d; best = k; }
    }
    return tks[best];
  }

  const px = ticks(axes.x || axis), py = ticks(axes.y || axis);
  const valueTicks = ticks(axis);
  const xTicks = px.length ? px : valueTicks;
  const yTicks = py.length ? py : valueTicks;
  const isPlot = !!(axes.x && axes.y);
  const mnX = fracParse(axes.x ? axes.x.min : axis.min);
  const mxX = fracParse(axes.x ? axes.x.max : axis.max);
  const mnY = fracParse(axes.y ? axes.y.min : axis.min);
  const mxY = fracParse(axes.y ? axes.y.max : axis.max);

  function domainX(clientX){
    const r = svg.getBoundingClientRect();
    const t = clamp01((clientX - r.left) / r.width);
    return fracAdd(mnX, fracMulInt(fracSub(mxX, mnX), t));
  }
  function domainY(clientY){
    const r = svg.getBoundingClientRect();
    const t = clamp01((clientY - r.top) / r.height);
    return fracAdd(mnY, fracMulInt(fracSub(mxY, mnY), t));
  }

  const W = 400, H = 240, L = 34, R = 10, T = 14, B = 26;

  function draw(s){
    s = s || tentative;
    let h = "";
    if(isPlot){
      h += `<line x1="${L}" y1="${H-B}" x2="${W-R}" y2="${H-B}" stroke="currentColor"/>`;
      h += `<line x1="${L}" y1="${T}" x2="${L}" y2="${H-B}" stroke="currentColor"/>`;
      px.forEach(tk=>{
        const x = L + clamp01(toFrac(tk.f, mnX, mxX)) * (W - L - R);
        h += `<line x1="${x}" y1="${H-B}" x2="${x}" y2="${H-B+5}" stroke="currentColor"/>`;
        h += `<text x="${x}" y="${H-B+18}" font-size="10" text-anchor="middle">${esc(tk.v)}</text>`;
      });
      py.forEach(tk=>{
        const y = H - B - clamp01(toFrac(tk.f, mnY, mxY)) * (H - T - B);
        h += `<line x1="${L-5}" y1="${y}" x2="${L}" y2="${y}" stroke="currentColor"/>`;
        h += `<text x="${L-8}" y="${y+3}" font-size="10" text-anchor="end">${esc(tk.v)}</text>`;
      });
      if(s.kind === "point" && s.x && s.y){
        const x = L + clamp01(toFrac(fracParse(s.x), mnX, mxX)) * (W - L - R);
        const y = H - B - clamp01(toFrac(fracParse(s.y), mnY, mxY)) * (H - T - B);
        h += `<circle cx="${x}" cy="${y}" r="6" fill="var(--accent)"/>`;
      }
    } else {
      const mid = H / 2;
      h += `<line x1="${L}" y1="${mid}" x2="${W-R}" y2="${mid}" stroke="currentColor"/>`;
      valueTicks.forEach(tk=>{
        const x = L + clamp01(toFrac(tk.f, mnX, mxX)) * (W - L - R);
        h += `<line x1="${x}" y1="${mid-5}" x2="${x}" y2="${mid+5}" stroke="currentColor"/>`;
        h += `<text x="${x}" y="${mid+20}" font-size="10" text-anchor="middle">${esc(tk.v)}</text>`;
      });
      if(s.kind === "numberline_point" && s.value){
        const x = L + clamp01(toFrac(fracParse(s.value), mnX, mxX)) * (W - L - R);
        h += `<circle cx="${x}" cy="${mid}" r="6" fill="var(--accent)"/>`;
      }
      if(s.kind === "interval" && s.start && s.end){
        const x1 = L + clamp01(toFrac(fracParse(s.start), mnX, mxX)) * (W - L - R);
        const x2 = L + clamp01(toFrac(fracParse(s.end), mnX, mxX)) * (W - L - R);
        h += `<line x1="${x1}" y1="${mid}" x2="${x2}" y2="${mid}" stroke="var(--accent)" stroke-width="5"/>`;
        h += `<circle cx="${x1}" cy="${mid}" r="5" fill="${s.start_closed ? "var(--accent)" : "var(--card)"}" stroke="var(--accent)"/>`;
        h += `<circle cx="${x2}" cy="${mid}" r="5" fill="${s.end_closed ? "var(--accent)" : "var(--card)"}" stroke="var(--accent)"/>`;
      }
    }
    svg.innerHTML = h;
  }

  /* ---- state: committed vs tentative (D-04/D-05) ---------------------------
     `state` is the last committed semantic state; `tentative` is in-progress
     editing that produces NO evidence until an explicit commit. Pointer
     down/move, focus, hover, pan/zoom, Escape-cancelled moves, and unchanged
     values never append anything. A commit is exactly: native
     control/Enter/Space, a tap, or pointer-up after a changed drag -- each
     posts ONE semantic action through /api/interact and renders only the
     runtime's observation. */
  const committed = {kind};
  const tentative = {kind};
  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c=>{
        const r = Math.random()*16|0, v = c==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));

  function snapshot(s){ // canonical semantic state dict (wire shape)
    if(kind === "point") return {kind:"point", x:s.x, y:s.y};
    if(kind === "numberline_point") return {kind:"numberline_point", value:s.value};
    return {kind:"interval", start:s.start, end:s.end,
            start_closed:!!s.start_closed, end_closed:!!s.end_closed};
  }
  function sameState(a, b){
    return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b));
  }
  function filled(s){
    return kind === "point" ? (s.x && s.y)
      : kind === "numberline_point" ? s.value
      : (s.start && s.end);
  }
  function adopt(s){ // tentative becomes committed
    Object.keys(committed).forEach(k=>{ if(k!=="kind") delete committed[k]; });
    Object.assign(committed, s);
    commitBtn.disabled = !filled(committed);
    checkBtn.disabled = !filled(committed);
  }
  function revertTentative(){
    Object.keys(tentative).forEach(k=>{ if(k!=="kind") delete tentative[k]; });
    Object.assign(tentative, committed);
    draw(tentative);
    syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  function syncControls(){
    const sels = controls.querySelectorAll("select");
    const wants = kind === "point" ? [tentative.x, tentative.y]
      : kind === "numberline_point" ? [tentative.value] : [tentative.start, tentative.end];
    sels.forEach((sel, i)=>{ if(wants[i]) sel.value = wants[i]; });
    if(kind === "interval"){
      const chks = controls.querySelectorAll("input[type=checkbox]");
      chks[0].checked = !!tentative.start_closed;
      chks[1].checked = !!tentative.end_closed;
    }
  }

  /* ---- the ONE serializer: canonical SCALAR strings, exact wire shapes ---- */
  function serialize(){
    return JSON.stringify(snapshot(tentative));
  }

  async function commitMove(){
    /* The explicit commit boundary: pointer-up after a changed drag, tap, or
       native Enter/Space. An unchanged value commits nothing (D-04). */
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId,
        interaction_version: c.version,
        action_id: aid,
        action_type: kind === "point"
            ? (filled(committed) ? "move_point" : "place_point")
          : kind === "numberline_point" ? "select_numberline_point" : "set_interval",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  svg.addEventListener("pointerdown", e => { e.preventDefault(); });
  svg.addEventListener("pointerup", e => {
    const before = JSON.stringify(snapshot(tentative));
    if(kind === "point"){
      const x = snap(xTicks, domainX(e.clientX));
      const y = snap(yTicks, domainY(e.clientY));
      Object.assign(tentative, {x: x.v, y: y.v});
    } else if(kind === "numberline_point"){
      Object.assign(tentative, {value: snap(valueTicks, domainX(e.clientX)).v});
    } else {
      const hit = snap(valueTicks, domainX(e.clientX)).v;
      if(!tentative.start || (tentative.start && tentative.end))
        Object.assign(tentative, {start: hit, end: undefined});
      else Object.assign(tentative, {end: hit});
    }
    draw(tentative);
    syncControls();
    if(JSON.stringify(snapshot(tentative)) !== before) commitMove();   // changed drag/tap
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.addEventListener("pointerleave", e => { if(e.buttons === 0) return; });
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    /* Arrows step by declared units on the focused scene; Enter/Space commit
       the tentative move; Escape cancels (D-07). */
    const step = fracParse(axis.step);
    if(!step) return;
    if(e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "ArrowUp" || e.key === "ArrowDown"){
      e.preventDefault();
      const delta = e.key === "ArrowLeft" || e.key === "ArrowDown" ? -1 : 1;
      if(kind === "point"){
        const moveX = e.key === "ArrowLeft" || e.key === "ArrowRight";
        const cur = moveX ? (tentative.x || axis.min) : (tentative.y || axis.min);
        const idx = valueTicks.findIndex(t => t.v === cur);
        const tks = moveX ? xTicks : yTicks;
        const at = tks.findIndex(t => t.v === cur);
        const nxt = tks[Math.max(0, Math.min(tks.length-1, (at < 0 ? 0 : at) + delta))];
        if(nxt) Object.assign(tentative, moveX ? {x: nxt.v} : {y: nxt.v});
      } else if(kind === "numberline_point"){
        const at = valueTicks.findIndex(t => t.v === (tentative.value || axis.min));
        const nxt = valueTicks[Math.max(0, Math.min(valueTicks.length-1, (at < 0 ? 0 : at) + delta))];
        if(nxt) Object.assign(tentative, {value: nxt.v});
      } else {
        const focus = e.shiftKey ? "start" : "end";
        const at = valueTicks.findIndex(t => t.v === (tentative[focus] || axis.min));
        const nxt = valueTicks[Math.max(0, Math.min(valueTicks.length-1, (at < 0 ? 0 : at) + delta))];
        if(nxt) Object.assign(tentative, {[focus]: nxt.v});
      }
      draw(tentative); syncControls();
      return;
    }
    if(e.key === "Enter" || e.key === " "){
      e.preventDefault();
      commitMove();
      return;
    }
    if(e.key === "Escape"){
      e.preventDefault();
      revertTentative();
    }
  });

  /* ---- adjacent semantic HTML controls: same state, same serializer ------- */
  function valueSelect(tks, onPick){
    const sel = document.createElement("select");
    tks.forEach(tk=>{ const o = document.createElement("option");
      o.value = tk.v; o.textContent = tk.v; sel.appendChild(o); });
    sel.onchange = ()=>{ onPick(sel.value); };
    return sel;
  }
  const controls = document.createElement("div");
  controls.className = "visual-controls";
  if(kind === "point"){
    const sx = valueSelect(xTicks, v=>{ Object.assign(tentative, {x: v}); draw(tentative); });
    const sy = valueSelect(yTicks, v=>{ Object.assign(tentative, {y: v}); draw(tentative); });
    controls.appendChild(labelCtl("x", sx));
    controls.appendChild(labelCtl("y", sy));
  } else if(kind === "numberline_point"){
    controls.appendChild(labelCtl("point", valueSelect(valueTicks,
      v=>{ Object.assign(tentative, {value: v}); draw(tentative); })));
  } else {
    const s1 = valueSelect(valueTicks, v=>{ Object.assign(tentative, {start: v}); draw(tentative); });
    const s2 = valueSelect(valueTicks, v=>{ Object.assign(tentative, {end: v}); draw(tentative); });
    const c1 = document.createElement("input"); c1.type = "checkbox";
    c1.onchange = ()=>Object.assign(tentative, {start_closed: c1.checked});
    const c2 = document.createElement("input"); c2.type = "checkbox";
    c2.onchange = ()=>Object.assign(tentative, {end_closed: c2.checked});
    const r1 = labelCtl("start", s1, c1);
    const r2 = labelCtl("end", s2, c2);
    r1.appendChild(document.createTextNode(" closed"));
    r2.appendChild(document.createTextNode(" closed"));
    controls.appendChild(r1);
    controls.appendChild(r2);
  }
  host.appendChild(controls);
  function labelCtl(label, sel, extra){
    const row = document.createElement("label");
    row.className = "visual-ctl";
    row.appendChild(document.createTextNode(label + " "));
    row.appendChild(sel);
    if(extra) row.appendChild(extra);
    return row;
  }

  /* ---- actions: Commit move, then Check response (UI-SPEC copy) ----------- */
  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  if(kind === "point" && initial.points && initial.points.length){
    Object.assign(committed, {x: initial.points[0].x, y: initial.points[0].y});
  }
  Object.assign(tentative, committed);
  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);

  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true;
    commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };

}

function mkSubmit(act, hint){
  const b = document.createElement("button");
  b.className="go"; b.type="button"; b.textContent="Submit answer"; b.disabled=true;
  const h = document.createElement("span"); h.className="hint"; h.textContent=hint;
  act.appendChild(b); act.appendChild(h);
  return b;
}

function hintCard(row, locked){
  const lines = locked ? (row.unlock_copy||[]).map(esc).join(" ") : esc(row.display||"");
  const unavailable = !locked && row.available === false ? " unavailable" : "";
  return `<li class="hint-card ${locked?"locked":"shown"}${unavailable}"
    data-hint-kind="${esc(row.name||"")}">
    <h4>${esc(row.header)}</h4><p>${lines}</p></li>`;
}
function renderQuestionAssist(card, teaching){
  let details=card.querySelector("[data-question-assist]");
  const shown=(teaching.shown||[]);
  if(!shown.length){ if(details) details.remove(); return; }
  const wasOpen=details ? details.open : true;
  if(!details){
    details=document.createElement("details");
    details.className="question-assist";
    details.dataset.questionAssist="";
    const anchor=card.querySelector(".question-symbols") || card.querySelector(".stem");
    anchor.insertAdjacentElement("afterend", details);
  }
  details.innerHTML=`<summary>Assisted question <span class="question-assist-count">
    ${shown.length} ${shown.length===1?"cue":"cues"}</span></summary>
    <p class="question-assist-note">These runtime-issued cues add to the question.
    Collapse this layer to reread the untouched wording.</p>
    <ol class="hint-ladder">${shown.map(x=>hintCard(x,false)).join("")}</ol>`;
  details.open=wasOpen;
}
function renderTeaching(card, result){
  const teaching = (result && result.teaching) || {};
  renderQuestionAssist(card, teaching);
  let region = card.querySelector(".support-region");
  if(!region){ region=document.createElement("section"); region.className="support-region";
    card.querySelector(".act").before(region); }
  if(!teaching.available){
    region.innerHTML = teaching.unavailable_reason
      ? `<p class="assist-copy">${esc(teaching.unavailable_reason)}</p>` : "";
    return;
  }
  const next=teaching.next_locked ? hintCard(teaching.next_locked,true) : "";
  const label=teaching.entitled ? "Open the next hint" : "I'm stumped &mdash; show the next hint";
  const action=teaching.exhausted ? "" : `<div class="hint-actions"><button type="button"
    class="go ghost" data-teach="${teaching.entitled?"hint":"stumped"}">${label}</button></div>`;
  if(!next && !action){ region.remove(); return; }
  region.innerHTML=`<h3 class="hint-heading">Help</h3><ol class="hint-ladder">${next}</ol>${action}`;
  const button=region.querySelector("[data-teach]");
  if(button) button.onclick=()=>api("/api/teach",{session_id:sessionId,
    action:{kind:button.dataset.teach}}).then(fresh=>renderTeaching(card,fresh));
}
function loadTeaching(card){
  return api("/api/teach",{session_id:sessionId}).then(result=>renderTeaching(card,result))
    .catch(()=>{
      let region = card.querySelector(".support-region");
      if(!region){
        region = document.createElement("section");
        region.className = "support-region";
        card.querySelector(".act").before(region);
      }
      region.textContent = "Hints are unavailable right now. You can still revise your answer.";
    });
}

function orderingCard(diagnostic){
  if(!diagnostic || diagnostic.version !== 1) return "";
  const messages = {
    missing_required: "A required block is missing. Review the selected blocks.",
    selected_distractor: "An unneeded block is selected. Review which blocks belong in the answer.",
    dependency_violation: "A block appears before a prerequisite. Review the order."
  };
  const message = messages[diagnostic.category];
  return message ? '<p data-ordering-diagnostic>' + message + '</p>' : "";
}
function selectionCard(picks){
  if(!picks || !picks.display) return "";
  let rows = "";
  for(const [name, word] of [["right", "right"], ["wrong", "not right"]]){
    for(const option of picks[name] || []){
      rows += `<li class="pick"><span class="mark">${word}</span>
        <span>${esc(option.key)}) ${esc(option.text)}</span></li>`;
    }
  }
  return `<div class="picks" data-selection-feedback><p>${esc(picks.display)}</p><ul>${rows}</ul></div>`;
}

function close(q, card, act, v, revert){
  if(v && v.entry_error){
    if(revert) revert();
    const fb = feedbackFor(card);
    fb.innerHTML = `<div id="fill-entry-error" class="refused pend" role="alert">${esc(v.entry_error)}</div>`;
    card.querySelectorAll('input[name^="fill_"]').forEach(input=>{
      input.setAttribute("aria-invalid", "true");
      input.setAttribute("aria-describedby", "fill-help-" + input.name.slice(5) + " fill-entry-error");
    });
    return;
  }
  /* Server-side refusal (plan 05-06): the daemon returned a normal
     `{"refused": ..., "refused_reason": ...}` body instead of a verdict --
     the served page's settle() surfaced it here, not in the catch block.
     The page renders its own locked copy of the matching sentence (the
     Copywriting Contract rows live in this client script; the daemon's
     `refused_reason` field picks which one), styled by cause: network =
     boundary/pending, language = misconfiguration/error. Check is not
     re-enabled -- retrying cannot change the outcome. */
  if(v && v.refused){
    act.innerHTML = "";
    const fb = feedbackFor(card);
    const langName = ((q.interaction_contract || {}).renderer_config || {}).language || "python";
    const lang = (v.refused_reason === "language")
      ? "This item requests the '" + langName + "' language, which isn't "
        + "enabled in this itembank's settings (check.languages). Add it in "
        + "settings, or ask whoever set up this bank to fix its [LANG:] value."
      : "Code execution is turned off while itembank is serving on your "
        + "network (--lan). Ask whoever runs itembank to turn on "
        + "check.allow_lan in settings if this device should be trusted, or "
        + "answer this item from the machine itembank is running on.";
    const div = document.createElement("div");
    div.className = "refused " + (v.refused_reason === "language" ? "err" : "pend");
    div.textContent = lang;
    act.appendChild(div);
    fb.innerHTML = "";
    return;
  }
  const ex = v.explain || {};
  const right = v.score;
  const pending = (right === null || right === undefined);
  act.innerHTML = "";
  const fb = feedbackFor(card);
  if(v.action === "hold"){
    if(revert) revert();
    fb.innerHTML = v.score === false
      ? `<div class="verdict n">Not correct. Re-read the question, then try another answer or open the next hint.</div>`
      : `<div class="status">Review your response before submitting again.</div>`;
    fb.innerHTML += selectionCard(v.selection_feedback);
    fb.innerHTML += orderingCard(v.ordering_diagnostic);
    loadTeaching(card);
    return;
  }
  if(v.action === "defer_feedback"){
    const nextView = v.next || {};
    if(currentActivity && currentActivity.stage === "answer" && nextView.activity && nextView.activity.stage === "reason"){
      renderItem(nextView);
      return;
    }
    const advanced = nextView.status === "complete" ||
      !!(nextView.item && nextView.item.id !== q.id);
    /* The sitting is parked at the marker's desk and the runtime will not
       move it until a mark is recorded, which is deliberate. What was NOT
       deliberate is that this branch used to print "Recorded." and return,
       leaving no control and no explanation, so a designed pause was
       indistinguishable from a hung page. Found by the 13.9 sitting on
       2026-08-24, whose shuffle put the short item first.

       It still releases no verdict, no model answer and no explanation:
       deferring feedback is the point. It only says where the sitting is. */
    const waiting = (q.type === "short" && advanced)
      ? `<div class="pend"><b>Response recorded, pending human review.</b>
         <div>You can continue the sitting. This response is not scored yet.</div></div>`
      : (q.type === "short")
      ? `<div class="pend"><b>Recorded, and waiting on a mark.</b>
         <div>A constructed response is not scored here. This sitting stays on
         this item until a human marker records a verdict, so nothing you wrote
         is graded by the machine and no model answer is shown to you now.</div>
         <div>You are the marker. Record the verdict below, or from a
         terminal with <span class="mono">itembank mark --session
         ${esc(sessionId || "")} --item ${esc(q.id || "")} --verdict pass|fail</span>.
         Either way it is the same recorded mark.</div></div>`
      : `<div class="pend"><b>Recorded.</b>
         <div>This mode holds every verdict until the sitting is closed.</div></div>`;
    fb.innerHTML = waiting;
    if(advanced){
      const continueButton = document.createElement("button");
      continueButton.className = "go";
      continueButton.type = "button";
      if(nextView.status === "complete"){
        continueButton.textContent = "View summary";
        continueButton.onclick = ()=> finish(nextView.summary || {});
      } else {
        continueButton.textContent = `Next question, ${Number(nextView.position || 0) + 1} of ${Number(nextView.total || total)}`;
        continueButton.onclick = ()=> renderItem(nextView);
      }
      act.appendChild(continueButton);
      continueButton.focus();
      return;
    }
    /* The way out of the desk, on the surface the learner is already on.
       A constructed response is settled by a person, and the person is
       here; before this the only exit was a terminal, so a sitting whose
       short item came up first dead-ended in the app. The verdict is the
       learner's own: the page sends it to `/api/mark`, which appends the
       same mark event `itembank mark` appends, and the runtime decides
       what that mark means for the cursor. No model has a vote here. */
    if(q.type === "short"){
      const settle = async (verdict)=>{
        try {
          const res = await api("/api/mark", {
            session_id: sessionId, item_ref: q.id, verdict: verdict});
          const view = (res && res.view) || null;
          if(view && view.status === "complete"){ finish(view.summary || {}); return; }
          if(view && view.item && view.item.id !== q.id){ renderItem(view); return; }
          fb.innerHTML = waiting
            + `<div class="pend">Mark recorded. The sitting did not move; check again.</div>`;
        } catch(err){
          fb.innerHTML = waiting
            + `<div class="pend">Could not record the mark. Nothing was changed.</div>`;
        }
      };
      const markRow = document.createElement("div");
      markRow.className = "act mark-row";
      for(const [label, verdict] of [["I got this right", true],
                                     ["I did not", false]]){
        const b = document.createElement("button");
        b.className = "go" + (verdict ? "" : " ghost");
        b.type = "button"; b.textContent = label;
        b.onclick = ()=> settle(verdict);
        markRow.appendChild(b);
      }
      act.appendChild(markRow);
    }
    const dnext = document.createElement("button");
    dnext.className = "go ghost"; dnext.type = "button";
    dnext.textContent = "Check again";
    dnext.onclick = async ()=>{
      /* Ask the server whether the desk has been collected. If the mark
         landed, the runtime has advanced and hands back the next item; if it
         has not, the same item comes back and the page says so again. The
         client never decides that a mark exists. */
      try {
        const view = await api("/api/next", {session_id: sessionId});
        if(view && view.item && view.item.id !== q.id){ renderItem(view); return; }
        if(view && view.status === "complete"){ finish(view.summary || {}); return; }
        fb.innerHTML = waiting
          + `<div class="pend">Still waiting on a mark for this item.</div>`;
      } catch(err){
        fb.innerHTML = waiting
          + `<div class="pend">Could not reach itembank to check.</div>`;
      }
    };
    act.appendChild(dnext);
    dnext.focus();
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
      h += `<div class="blk note">The model answer is
        held back so it cannot contaminate the items after this one. It is in the bank file
        and in the attempt file next to what you wrote.</div>`;
    }
  } else if(q.type === "check"){
    /* The matrix consumes the normalized ordered observations from the one
       run -- stable case_index/reason pairs, never scraped from prose and
       never a second verdict. The deadline and cap are interpolated from
       the config the daemon runs with (booleans stay bound flags). */
    const rows = (v.interaction_result && v.interaction_result.observations) || [];
    h += checkMatrix(rows, 5, 64);
  } else {
    if(!v.skipWhy) h += blk("Why this is best", ex.why);
    h += blk("Key discriminator", ex.disc);
    h += blk("Second best", ex.second);
    if(ex.notes && ex.notes.length) h += `<div class="blk"><h4>Notes</h4><ul><li>`
      + ex.notes.map(esc).join("</li><li>") + `</li></ul></div>`;
  }
  if(ex.trap) h += `<div class="blk trap"><h4>Trap</h4><div>${esc(ex.trap)}</div></div>`;
  if(Array.isArray(v.activity_feedback)) h = v.activity_feedback.map((row,index)=>{
    const explanation = row.explain || {};
    const verdict = row.score === true ? "Correct." : row.score === false ? "Not correct." : "Recorded.";
    return `<section data-child-feedback><h2>${index === 0 ? "Answer" : "Reason"} feedback</h2><p>${verdict}</p><p>${esc(explanation.answer_text)}</p><p>${esc(explanation.why)}</p></section>`;
  }).join("");
  exp.innerHTML = h;
  fb.innerHTML = "";
  fb.appendChild(exp);
  const next = document.createElement("button");
  next.className = "go"; next.type = "button";
  const nxt = v.next || {};
  if(nxt.item){
    const nextPosition = Number(nxt.position || 0) + 1;
    const nextTotal = Number(nxt.total || total);
    next.textContent = `Next question, ${nextPosition} of ${nextTotal}`;
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
    <span class="score-sub"> &middot; ${pct}% auto-marked</span></div>`;
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
    h += `<p style="margin-top:14px">Open the report to review the session's recorded results.</p>`;
  }
  if(LTI_COMPLETION && LTI_COMPLETION.line){
    h += `<p class="status" data-field="lti-completion">${esc(LTI_COMPLETION.line)}</p>`;
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

function draftKey(bank, itemId){
  return "itembank.draft." + bank + "." + itemId;
}
function readBuildDraft(saved, steps){
  if(!Array.isArray(saved) || saved.length > steps.length) return [];
  const selected = saved.filter(value=>value !== "");
  if(!saved.every(value=>typeof value === "string" && (value === "" || steps.includes(value)))
      || new Set(selected).size !== selected.length) return [];
  return saved.slice();
}
function installMatchingCapacity(form){
  const fieldset = form.querySelector('[data-matching-reuse="once"]');
  if(!fieldset) return;
  if(form.matchingRefresh){ form.matchingRefresh(); return; }
  const selects = Array.from(fieldset.querySelectorAll("select[data-row-id]"));
  function refresh(){
    const used = selects.map(select=>select.value).filter(Boolean);
    selects.forEach(select=>Array.from(select.options).forEach(option=>{
      option.disabled = !!option.value && option.value !== select.value && used.includes(option.value);
    }));
  }
  form.matchingRefresh = refresh;
  form.addEventListener("change", refresh);
  refresh();
}
function installInlineWordBank(form){
  const blanks = Array.from(form.querySelectorAll(".inline-completion select"));
  if(!blanks.length || form.querySelector(".inline-word-bank")) return;
  let draggedWord = null, locked = false;
  const hint = document.createElement("p");
  hint.textContent = form.querySelector('[data-matching-reuse="once"]') ? "Drag a choice or use the dropdown. Each choice can be used once." : "Drag a word into a blank, or choose it from the dropdown. Words can be reused.";
  const bank = document.createElement("div"); bank.className = "inline-word-bank";
  Array.from(blanks[0].options).filter(option=>option.value !== "").forEach(option=>{
    const word = document.createElement("span");
    word.textContent = option.textContent; word.dataset.word = option.value; word.draggable = true;
    word.ondragstart = event=>{
      if(locked){ event.preventDefault(); return; }
      draggedWord = option.value;
      if(event.dataTransfer){ event.dataTransfer.effectAllowed = "copy"; event.dataTransfer.setData("text/plain", option.value); }
    };
    word.ondragend = ()=>{ draggedWord = null; };
    bank.appendChild(word);
  });
  form.prepend(hint, bank);
  blanks.forEach(select=>{
    const label = select.closest(".inline-completion");
    label.ondragover = event=>{ if(!locked && !select.disabled && draggedWord !== null) event.preventDefault(); };
    label.ondrop = event=>{
      if(locked || select.disabled || draggedWord === null
          || !Array.from(select.options).some(option=>option.value === draggedWord && !option.disabled)) return;
      event.preventDefault(); select.value = draggedWord; draggedWord = null;
      select.dispatchEvent(new Event("change", {bubbles:true}));
    };
  });
  form.addEventListener("submit", ()=>{ locked = true; draggedWord = null; });
}
function readFillDraft(saved, ids){
  const values = Object.create(null);
  if(!saved || typeof saved !== "object") return values;
  ids.forEach((id, index)=>{
    const value = Array.isArray(saved) ? saved[index] : saved[id];
    if(typeof value === "string") values[id] = value;
  });
  return values;
}
function installDraft(baseline){
  const orderingForm = baseline.querySelector("[data-answer-form]");
  const orderingFieldset = orderingForm && orderingForm.querySelector("[data-ordering-signature]");
  if(orderingFieldset && !baseline.hasAttribute("data-feedback-pause")) installOrderingControls(orderingFieldset);
  if(baseline.dataset.responseType === "dnd" && !baseline.hasAttribute("data-feedback-pause")){
    const form = baseline.querySelector("[data-answer-form]");
    if(form){ installMatchingCapacity(form); installInlineWordBank(form); }
  }
  // Draft autosave is presentation state only (080bffc): it refills the
  // visible controls and is never read back as an answer, never sent
  // anywhere, and never recorded until the form POST itself succeeds.
  // Storage unavailable or scripting off degrades to exactly the
  // script-free baseline, so every branch here is allowed to give up.
  //
  // Keyed by bank and item, not session: cmd_serve mints a fresh session id
  // on every launch (surfaces/quiz.py, surfaces/daemon.py _ensure_quiz_session),
  // so a session-keyed draft is orphaned by exactly the restart it exists to
  // survive. The bank stem is stable across a restart, which is the whole
  // point. One learner per installation, so a draft surviving to whichever
  // session next opens the same item is the desired behaviour, not a leak.
  try{
    var store = window.localStorage;
    if(!store) return;
    var bank = (BOOT && BOOT.bank) || "", iid = baseline.dataset.itemId;
    if(!bank || !iid) return;
    var prefix = "itembank.draft." + bank + ".";
    var key = draftKey(bank, iid);
    for(var i = store.length - 1; i >= 0; i--){
      var k = store.key(i);
      if(k && k.indexOf(prefix) === 0 && k !== key) store.removeItem(k);
    }
    if(baseline.hasAttribute("data-feedback-pause")){
      store.removeItem(key);
      return;
    }
    var form = baseline.querySelector("[data-answer-form]");
    if(!form) return;
    var choice = baseline.dataset.responseType === "mc" || baseline.dataset.responseType === "multi";
    if(choice){
      var options = Array.from(form.querySelectorAll('input[name="option"]'));
      var choiceSignature = baseline.dataset.presentationSignature || JSON.stringify([
        baseline.dataset.responseType, baseline.querySelector("h1.stem").textContent,
        options.map(function(el){ return [el.value, el.closest("label").textContent]; })]);
      var choiceSaved = null;
      try{ choiceSaved = JSON.parse(store.getItem(key)); }catch(e){}
      if(choiceSaved && choiceSaved.signature !== choiceSignature){
        store.removeItem(key);
        const notice = document.createElement("p"); notice.setAttribute("role", "status");
        notice.textContent = "The saved choice belongs to an older question revision. Choose again.";
        form.prepend(notice);
      }
      if(choiceSaved && choiceSaved.signature === choiceSignature && Array.isArray(choiceSaved.values)
          && choiceSaved.values.every(function(v){ return typeof v === "string" && options.some(function(el){ return el.value === v; }); })
          && new Set(choiceSaved.values).size === choiceSaved.values.length
          && (baseline.dataset.responseType !== "mc" || choiceSaved.values.length <= 1)){
        // A server-echoed refused submission is newer than the local draft.
        if(!options.some(function(el){ return el.checked; })) options.forEach(function(el){ el.checked = choiceSaved.values.includes(el.value); });
      }
      form.addEventListener("change", function(){
        try{ store.setItem(key, JSON.stringify({signature:choiceSignature,
          values:options.filter(function(el){ return el.checked; }).map(function(el){ return el.value; })})); }catch(e){}
      });
      return;
    }
    var assignment = baseline.dataset.responseType === "dnd" || baseline.dataset.responseType === "table";
    var build = baseline.dataset.responseType === "build";
    var fields = form.querySelectorAll(assignment ? "select[data-row-id]" : build ? "select[name^=step_]" : "textarea, input[type=text]");
    var saved = null, raw = store.getItem(key);
    try{ saved = raw === null ? null : JSON.parse(raw); }catch(e){ saved = null; }
    var matching = form.querySelector("[data-matching-signature]");
    var ordering = form.querySelector("[data-ordering-signature]");
    var signature = matching ? matching.dataset.matchingSignature : ordering ? ordering.dataset.orderingSignature : null;
    if(matching){
      if(saved && saved.signature !== signature){
        const notice = document.createElement("p"); notice.setAttribute("role", "status");
        notice.textContent = "The saved draft belongs to an older matching declaration. Choose again.";
        matching.prepend(notice);
      }
      saved = saved && saved.signature === signature ? saved.values : null;
    }
    var orderingFocus = saved && saved.focus;
    if(ordering){
      if(saved && saved.signature !== signature){
        const notice = document.createElement("p"); notice.setAttribute("role", "status");
        notice.textContent = "The saved draft belongs to an older ordering declaration. Arrange the blocks again.";
        ordering.prepend(notice);
        orderingFocus = null;
        fields.forEach(function(el){ el.value = ""; });
      }
      saved = saved && saved.signature === signature ? saved.values : null;
    }
    var fill = baseline.dataset.responseType === "fill";
    var ids = fill ? Array.from(fields, function(el){ return el.name.slice(5); }) : [];
    var fillValues = fill ? readFillDraft(saved, ids) : null;
    if(build) saved = readBuildDraft(saved, Array.from(fields[0] ? fields[0].options : [], option=>option.value).filter(Boolean));
    fields.forEach(function(el, idx){
      if(assignment && saved && !Array.isArray(saved) && typeof saved[el.dataset.rowId] === "string"
          && Array.from(el.options).some(function(option){ return option.value === saved[el.dataset.rowId]; }))
        el.value = saved[el.dataset.rowId];
      else if(fill && Object.prototype.hasOwnProperty.call(fillValues, ids[idx]))
        el.value = fillValues[ids[idx]];
      else if(!fill && Array.isArray(saved) && typeof saved[idx] === "string")
        el.value = saved[idx];
    });
    if(assignment) installMatchingCapacity(form);
    if(ordering){
      installOrderingControls(ordering);
      if(Number.isInteger(orderingFocus) && fields[orderingFocus]) fields[orderingFocus].focus();
    }
    function save(){
      var vals = fill || assignment ? Object.create(null) : [];
      fields.forEach(function(el, idx){
        if(assignment) vals[el.dataset.rowId] = el.value;
        else if(fill) vals[ids[idx]] = el.value;
        else vals.push(el.value);
      });
      try{ store.setItem(key, JSON.stringify(matching || ordering ? {signature:signature, values:vals, focus:Array.from(fields).indexOf(document.activeElement)} : vals)); }catch(e){}
    }
    form.addEventListener("input", save);
    if(assignment || build) form.addEventListener("change", save);
    if(ordering) form.addEventListener("focusin", save);
  }catch(e){}
}

function restoreQuizPosition(baseline){
  // This is disposable, tab-local presentation state. The runtime still owns
  // answers, cursor and feedback. A changed public item invalidates the view.
  try{
    const store = window.sessionStorage;
    const sid = baseline.dataset.sessionId, iid = baseline.dataset.itemId;
    if(!sid || !iid || !baseline.dataset.presentationSignature) return false;
    const prefix = "itembank.return." + ((BOOT && BOOT.bank) || "") + ".";
    const key = prefix + sid + "." + iid;
    for(let i=store.length-1;i>=0;i--){
      const old = store.key(i);
      if(old && old.startsWith(prefix) && old !== key) store.removeItem(old);
    }
    if(baseline.hasAttribute("data-feedback-pause")){ store.removeItem(key); return false; }
    const signature = baseline.dataset.presentationSignature;
    const controls = ()=>Array.from(baseline.querySelectorAll("a[href], input:not([type=hidden]), select, textarea, button"));
    function identity(el){
      return {tag:el.tagName, name:el.getAttribute("name"),
        value:el.tagName === "INPUT" ? el.value : null,
        href:el.getAttribute("href"), id:el.id || null};
    }
    if(!baseline.quizPositionInstalled){
      baseline.quizPositionInstalled = true;
      window.addEventListener("pagehide", ()=>{
        try{ store.setItem(key, JSON.stringify({signature, y:window.scrollY, width:window.innerWidth,
          focus:controls().includes(document.activeElement) ? identity(document.activeElement) : null})); }catch(e){}
      });
    }
    const saved = JSON.parse(store.getItem(key) || "null");
    if(!saved || saved.signature !== signature || !Number.isFinite(saved.y) || saved.y < 0){
      if(saved) store.removeItem(key);
      return false;
    }
    const focus = saved.focus && controls().find(el=>JSON.stringify(identity(el)) === JSON.stringify(saved.focus));
    if(focus) focus.focus({preventScroll:true});
    else { const heading = baseline.querySelector("h1.stem"); if(heading) heading.focus({preventScroll:true}); }
    window.requestAnimationFrame(()=>{
      if(Number.isFinite(saved.width) && saved.width !== window.innerWidth){
        (focus || baseline.querySelector("h1.stem") || baseline).scrollIntoView({block:"center"});
      } else window.scrollTo(0, saved.y);
    });
    return true;
  }catch(e){ return false; }
}

/* ---- start: one /api/start call bootstraps the whole sitting -------------- */
async function start(){
  const baseline = host.querySelector("[data-server-baseline]");
  if(baseline){
    sessionId = baseline.dataset.sessionId || null;
    if(window.Assist) window.Assist.setSession(sessionId);
    if(baseline.dataset.responseType) setContext({
      type: baseline.dataset.responseType,
      ordering: !!baseline.querySelector("[data-ordering-signature]"),
      objective: baseline.dataset.objective || "",
      lesson_slug: baseline.dataset.lessonSlug || ""
    });
    if(baseline.querySelector("[data-activity-stage]") && activityDisclosure)
      activityDisclosure.textContent = document.getElementById("cx-mode").textContent === "exam"
        ? "Feedback after completion" : "Feedback after answer and reason";
    installDraft(baseline);
    if(!restoreQuizPosition(baseline) && !baseline.hasAttribute("data-feedback-pause")){
      const heading = baseline.querySelector("h1.stem");
      if(heading && !baseline.querySelector("[data-ordering-signature] select:focus")) heading.focus({preventScroll:true});
    }
    return;
  }
  host.innerHTML = `<div class="card"><div class="feedback" role="status"
      aria-live="polite"><div class="status">Loading&hellip;</div></div></div>`;
  try {
    /* D-09: a #<item-id> fragment (lesson backlink) asks the server to start
       with that item first; unknown ids degrade to normal order server-side.
       Phase 999.4 (LTI): the server may embed an objective and a one-time
       launch-context token in BOOT -- the LTI /api/* family reads them. */
    const payload = {bank: BOOT.bank, count: BOOT.count, mode: BOOT.mode};
    if(BOOT.objective) payload.objective = BOOT.objective;
    if(BOOT.lti_ctx) payload.lti_ctx = BOOT.lti_ctx;
    const frag = location.hash.replace(/^#/, "");
    if(frag) payload.focus = frag;
    const view = await api("/api/start", payload);
    sessionId = view.session_id;
    if(window.Assist) window.Assist.setSession(sessionId);
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
