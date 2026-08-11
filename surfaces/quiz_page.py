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
/* AgentAssist (plan 08-05): optional, subordinate, collapsed, opt-in
   generated support. Phase 4 tokens only; no fixed or minimum widths, so
   320px/200% zoom never scrolls horizontally. */
.agent-assist{margin:14px 0 0;font-size:13.5px;max-width:72ch}
.assist summary{cursor:pointer;padding:4px 0;font-size:11px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--mut);
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.assist summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.assist-body{display:flex;flex-direction:column;gap:8px;margin-top:8px}
.assist-status{color:var(--mut);font-size:12.5px;margin:0}
.assist-actions{display:flex;flex-wrap:wrap;gap:8px}
.assist-copy{color:var(--mut);margin:0}
.generated{background:var(--card);border:1px solid var(--line);
  border-left:3px solid var(--accent);border-radius:0 9px 9px 0;
  padding:12px 14px}
.generated h4,.authored-hint h4,.rubric h4{margin:0 0 5px;font-size:11px;
  letter-spacing:.09em;text-transform:uppercase;color:var(--mut);
  font-family:ui-monospace,Menlo,Consolas,monospace}
.generated-disclosure{color:var(--mut);font-size:12.5px;margin:0 0 8px}
.generated-text{margin:0;overflow-wrap:anywhere}
.authored-hint{margin-top:10px;background:var(--card);border:1px solid var(--line);
  border-radius:9px;padding:12px 14px}
.authored-hint p{margin:0;overflow-wrap:anywhere}
.assist-lock{display:flex;gap:10px;align-items:flex-start;background:var(--chip);
  border:1px solid var(--line);border-radius:9px;padding:12px 14px}
.lock-glyph{font-size:18px;line-height:1.2}
.lock-label{font-weight:600;margin:0 0 4px}
.lock-copy{color:var(--mut);margin:0 0 8px;overflow-wrap:anywhere}
.rubric-rows{list-style:none;margin:0;padding:0;display:flex;
  flex-direction:column;gap:8px}
.rubric-row{display:flex;gap:10px;align-items:flex-start;background:var(--card);
  border:1px solid var(--line);border-radius:9px;padding:10px 12px}
.rubric-token{flex:0 0 auto;font-size:10.5px;letter-spacing:.08em;
  text-transform:uppercase;font-family:ui-monospace,Menlo,Consolas,monospace;
  color:var(--warn);background:var(--chip);border:1px solid var(--line);
  border-radius:5px;padding:2px 7px}
.rubric-rationale{margin:0;overflow-wrap:anywhere}
.provenance{margin-top:10px;font-size:12.5px;color:var(--mut)}
.provenance summary{cursor:pointer}
.assist-id{overflow-wrap:anywhere;word-break:break-all}
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
<div id="assist-slot">__ASSIST__</div>
</div>
<script id="offline">
__OFFLINE_JS__
</script>
<script id="served">
__SERVED_JS__
</script>
<script id="assist">
__ASSIST_JS__
</script>
</body></html>"""


# The locked 08-UI-SPEC Copywriting Contract strings for the assist region
# (phase 8 UI-SPEC copy tables are binding; tests assert each verbatim).
ASSIST_COPY = {
    "summary": "Help and evidence",
    "request": "Get optional guidance",
    "preparing": "Preparing optional guidance\u2026",
    "generated_heading": "Generated support",
    "generated_disclosure": ("This guidance is generated from the current "
                             "attempt and the help available at this step."),
    "unavailable": ("Generated help is unavailable. You can keep learning "
                    "with the lesson and authored hints."),
    "policy_drop": ("Generated help is unavailable for this step. Continue "
                    "with the available hint or try another attempt."),
    "cancelled": ("Optional guidance was cancelled. Your current work is "
                  "unchanged."),
    "already_requested": ("Optional guidance was already requested for this "
                          "attempt. Continue with the available hint or make "
                          "another attempt."),
    "retry": "Try generated guidance again",
    "pending_heading": ("Pending rubric suggestion \u2014 human review "
                        "required"),
    "rubric_empty": ("No complete rubric suggestion is available. This "
                     "response is still waiting for a human mark."),
    "lock_label": "Optional guidance is locked",
    "authored_heading": "Authored hint",
    "provenance_summary": "Generated support details",
}


# The assist chrome, substituted into TEMPLATE's __ASSIST__ slot only for the
# daemon-served page (build/offline mode ships no assist). Native
# details/summary, one opt-in button, one bounded status line, a generated
# support container, a provenance disclosure, and the structural lock /
# pending rubric containers the client fills -- no accept or mark control.
AGENT_ASSIST_HTML = (r"""<section class="agent-assist" data-agent-assist
  aria-label="Optional generated guidance">
  <details class="assist" id="assist">
    <summary>__ASSIST_SUMMARY__</summary>
    <div class="assist-body">
      <div class="assist-actions">
        <button type="button" class="go ghost" id="assist-request">__ASSIST_REQUEST__</button>
      </div>
      <p class="assist-status" id="assist-status" role="status"
        aria-live="polite"></p>
      <div class="assist-outcome" id="assist-outcome" hidden></div>
    </div>
  </details>
</section>"""
    .replace("__ASSIST_SUMMARY__", ASSIST_COPY["summary"])
    .replace("__ASSIST_REQUEST__", ASSIST_COPY["request"]))


# The AgentAssist client (plan 08-05). Wires the served client to POST
# /api/hint and POST /api/rubric-review, renders only the typed payload
# fields, announces each lifecycle state once through the single polite
# status region, and never reads or renders a reason code, a tier, a
# profile, a backend class, a fact manifest, a candidate body, or provider
# detail. It never creates an accept or mark control: the browser may render
# a pending suggestion, never settle one (D-14/D-25).
ASSIST_JS = (r"""/* AgentAssist client: renders only typed /api payloads in
   fixed chrome. No authority vocabulary is read or rendered here. */
const Assist = (function(){
  const statusEl = document.getElementById("assist-status");
  const outcomeEl = document.getElementById("assist-outcome");
  const requestBtn = document.getElementById("assist-request");
  let sessionId = null;
  let itemType = null;
  let requested = false;      /* at most one automatic generation per item */

  const esc = s => (s==null?"":String(s)).replace(/[&<>]/g,
    c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

  function setStatus(text){
    if(statusEl) statusEl.textContent = text || "";
  }
  function setBusy(busy){
    if(requestBtn) requestBtn.disabled = !!busy;
  }
  function render(html){
    if(!outcomeEl) return;
    outcomeEl.hidden = !html;
    outcomeEl.innerHTML = html || "";
  }
  function setSession(id){ sessionId = id; }
  function onItem(q){
    itemType = (q && q.type) || null;
    requested = false;
    setStatus("");
    setBusy(false);
    render("");
  }
  async function api(path, payload){
    const res = await fetch(path, {method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(payload)});
    if(!res.ok) throw new Error("HTTP " + res.status);
    return res.json();
  }
  function authoredHtml(authored){
    if(!authored || !authored.available ||
       typeof authored.content !== "string" || !authored.content) return "";
    return `<div class="authored-hint"><h4>__ASSIST_AUTHORED_HEADING__</h4>
      <p>${esc(authored.content)}</p></div>`;
  }
  function lockHtml(copy){
    return `<div class="assist-lock">
      <span class="lock-glyph" aria-hidden="true">&#128274;</span>
      <div>
        <p class="lock-label">__ASSIST_LOCK_LABEL__</p>
        <p class="lock-copy">${esc(copy)}</p>
        <button type="button" class="go ghost" id="assist-retry">__ASSIST_RETRY__</button>
      </div></div>`;
  }
  function provenanceHtml(id){
    if(!id) return "";
    return `<details class="provenance"><summary>__ASSIST_PROVENANCE_SUMMARY__</summary>
      <p><span class="provenance-label">__ASSIST_GENERATED_HEADING__</span>
      &middot; interaction <span class="mono assist-id">${esc(id)}</span></p>
      </details>`;
  }
  function renderHint(v){
    if(v && v.status === "pass" && v.generated && v.generated.text){
      render(`<div class="generated">
          <h4>__ASSIST_GENERATED_HEADING__</h4>
          <p class="generated-disclosure">__ASSIST_GENERATED_DISCLOSURE__</p>
          <p class="generated-text">${esc(v.generated.text)}</p>
        </div>` + provenanceHtml(v.interaction_id));
      return;
    }
    if(v && (v.status === "unavailable" || v.status === "drop")){
      const copy = v.status === "drop"
        ? "__ASSIST_POLICY_DROP__" : "__ASSIST_UNAVAILABLE__";
      render(lockHtml(copy) + authoredHtml(v.authored));
      const retry = document.getElementById("assist-retry");
      if(retry) retry.onclick = () => { request(true); };
      return;
    }
    if(v && v.status === "cancelled"){
      render(`<p class="assist-copy">__ASSIST_CANCELLED__</p>`);
      return;
    }
    render(lockHtml("__ASSIST_UNAVAILABLE__"));
  }
  function renderRubric(v){
    const points = (v && v.points) || [];
    if(v && v.status === "pending" && points.length){
      const rows = points.map(p => {
        const rationale = (p && p.rationale)
          ? `<div class="rubric-rationale">${esc(p.rationale)}</div>` : "";
        return `<li class="rubric-row">
          <span class="rubric-token">pending</span>
          <div>${rationale}</div></li>`;
      }).join("");
      render(`<div class="rubric">
        <h4>__ASSIST_PENDING_HEADING__</h4>
        <ul class="rubric-rows">${rows}</ul></div>`);
      return;
    }
    render(`<p class="assist-copy">__ASSIST_RUBRIC_EMPTY__</p>`);
  }
  function request(retry){
    if(!sessionId) return;
    if(requested && !retry){
      render(`<p class="assist-copy">__ASSIST_ALREADY_REQUESTED__</p>`);
      return;
    }
    requested = true;
    setBusy(true);
    setStatus("__ASSIST_PREPARING__");
    const path = itemType === "short" ? "/api/rubric-review" : "/api/hint";
    const payload = {session_id: sessionId};
    if(retry) payload.retry = true;
    api(path, payload).then(v => {
      setStatus("");
      if(itemType === "short") renderRubric(v); else renderHint(v);
    }).catch(() => {
      setStatus("");
      render(lockHtml("__ASSIST_UNAVAILABLE__"));
      const retryBtn = document.getElementById("assist-retry");
      if(retryBtn) retryBtn.onclick = () => { request(true); };
    }).then(() => { setBusy(false); });
  }
  if(requestBtn) requestBtn.onclick = () => { request(false); };
  return {setSession, onItem};
})();
window.Assist = Assist;
"""
    .replace("__ASSIST_PREPARING__", ASSIST_COPY["preparing"])
    .replace("__ASSIST_GENERATED_HEADING__", ASSIST_COPY["generated_heading"])
    .replace("__ASSIST_GENERATED_DISCLOSURE__", ASSIST_COPY["generated_disclosure"])
    .replace("__ASSIST_UNAVAILABLE__", ASSIST_COPY["unavailable"])
    .replace("__ASSIST_POLICY_DROP__", ASSIST_COPY["policy_drop"])
    .replace("__ASSIST_CANCELLED__", ASSIST_COPY["cancelled"])
    .replace("__ASSIST_ALREADY_REQUESTED__", ASSIST_COPY["already_requested"])
    .replace("__ASSIST_RETRY__", ASSIST_COPY["retry"])
    .replace("__ASSIST_PENDING_HEADING__", ASSIST_COPY["pending_heading"])
    .replace("__ASSIST_RUBRIC_EMPTY__", ASSIST_COPY["rubric_empty"])
    .replace("__ASSIST_LOCK_LABEL__", ASSIST_COPY["lock_label"])
    .replace("__ASSIST_AUTHORED_HEADING__", ASSIST_COPY["authored_heading"])
    .replace("__ASSIST_PROVENANCE_SUMMARY__", ASSIST_COPY["provenance_summary"]))


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
               short:"short answer", visual:"visual assessment"};
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
    short:asShort, visual:asVisualOffline}[q.type])(q, body, act, card);
  card.scrollIntoView({block:"start", behavior: REDUCED ? "auto" : "smooth"});
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
               short:"short answer", visual:"visual assessment"};
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
          next: v.next};
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
    short:asShort, visual:asVisual}[q.type])(q, body, act, card);
  /* AgentAssist (plan 08-05): the assist client resets per item so the
     Get optional guidance control targets the current item's operation. */
  if(window.Assist) window.Assist.onItem(q);
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
    status.textContent = "Move cancelled. Your last committed state is still here.";
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
      status.textContent = "No change to commit.";
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
        status.textContent = "Move committed. You can adjust it or check your response.";
      } else {
        status.textContent = "That move could not be recorded. Your last committed state is still here. Adjust it and try again.";
        revertTentative();
      }
    } catch(err){
      status.textContent = "That move could not be recorded. Your last committed state is still here. Adjust it and try again.";
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
      status.textContent = "Commit your move before checking it.";
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
    status.textContent = "Move cancelled. Your last committed state is still here.";
  }

  async function commitMove(){
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      status.textContent = "No change to commit.";
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
        status.textContent = "Move committed. You can adjust it or check your response.";
      } else {
        status.textContent = "That move could not be recorded. Your last committed state is still here. Adjust it and try again.";
        revertTentative();
      }
    } catch(err){
      status.textContent = "That move could not be recorded. Your last committed state is still here. Adjust it and try again.";
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
      status.textContent = "Commit your move before checking it.";
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
    status.textContent = "Move cancelled. Your last committed state is still here.";
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
      status.textContent = "No change to commit.";
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
        status.textContent = "Move committed. You can adjust it or check your response.";
      } else {
        status.textContent = "That move could not be recorded. Your last committed state is still here. Adjust it and try again.";
        revertTentative();
      }
    } catch(err){
      status.textContent = "That move could not be recorded. Your last committed state is still here. Adjust it and try again.";
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
      status.textContent = "Commit your move before checking it.";
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

function close(q, card, act, v, revert){
  const ex = v.explain || {};
  const right = v.score;
  const pending = (right === null || right === undefined);
  act.innerHTML = "";
  const fb = feedbackFor(card);
  if(v.action === "hold"){
    if(revert) revert();
    fb.innerHTML = `<div class="verdict n">Not correct yet — the card stays
      open. Optional guidance is available under Help and evidence below.</div>`;
    return;
  }
  if(v.action === "defer_feedback"){
    fb.innerHTML = `<div class="pend">Recorded. ${q.type === "short"
      ? "Not marked here — a human marker reviews it." : ""}</div>`;
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
"""
