/* AgentAssist client: renders only typed /api payloads in
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

  function setStatus(text, live){
    if(!statusEl) return;
    if(live) statusEl.setAttribute("aria-live", "polite");
    else statusEl.removeAttribute("aria-live");
    statusEl.textContent = text || "";
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
  /* The runtime shapes the words; this only renders them. `display` is the
     learner-facing text the runtime already resolved -- never an id, and
     never re-derived here. An absent payload renders nothing, as before; a
     payload that is present but has no text renders the locked empty
     state, because a silent nothing is indistinguishable from a broken
     panel. */
  function unavailableHtml(copy){
    return `<p class="assist-copy">${esc(copy)}</p>
      <button type="button" class="go ghost" id="assist-retry">__ASSIST_RETRY__</button>`;
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
      render(unavailableHtml(copy));
      const retry = document.getElementById("assist-retry");
      if(retry) retry.onclick = () => { request(true); };
      return;
    }
    if(v && v.status === "cancelled"){
      render(`<p class="assist-copy">__ASSIST_CANCELLED__</p>`);
      return;
    }
    render(unavailableHtml("__ASSIST_UNAVAILABLE__"));
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
    setStatus("__ASSIST_PREPARING__", true);
    const path = itemType === "short" ? "/api/rubric-review" : "/api/hint";
    const payload = {session_id: sessionId};
    if(retry) payload.retry = true;
    api(path, payload).then(v => {
      if(itemType === "short") renderRubric(v); else renderHint(v);
      setStatus("", false);
    }).catch(() => {
      render(unavailableHtml("__ASSIST_UNAVAILABLE__"));
      const retryBtn = document.getElementById("assist-retry");
      if(retryBtn) retryBtn.onclick = () => { request(true); };
      setStatus("", false);
    }).then(() => { setBusy(false); });
  }
  if(requestBtn) requestBtn.onclick = () => { request(false); };
  return {setSession, onItem};
})();
window.Assist = Assist;
