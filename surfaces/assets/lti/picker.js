const RETURN_URL = "__DL_RETURN__";
const LINK_BASE = "__DL_BASE__";
const FAILED_COPY = "__DL_FAILED__";
const RETRY_COPY = "__DL_RETRY__";
const CANCEL_COPY = "__DL_CANCEL__";
const CONFIRM_COPY = '__DL_CONFIRM__';
let selected = null;
const rows = document.querySelectorAll(".prow");
const confirmEl = document.getElementById("lti-confirm");
const linkBtn = document.getElementById("lti-link");
rows.forEach(r => r.addEventListener("click", () => {
  rows.forEach(x => x.classList.remove("sel"));
  r.classList.add("sel");
  selected = {bank: r.dataset.bank, objective: r.dataset.objective};
  confirmEl.hidden = false;
  confirmEl.textContent = CONFIRM_COPY.replace("{title}", selected.objective);
  linkBtn.hidden = false;
}));
function postResponse(contentItems){
  const form = document.createElement("form");
  form.method = "POST"; form.action = RETURN_URL; form.hidden = true;
  const input = document.createElement("input");
  input.type = "hidden"; input.name = "content_items";
  input.value = JSON.stringify(contentItems);
  form.appendChild(input);
  document.body.appendChild(form);
  try { form.submit(); }
  catch(err){
    const host = document.getElementById("lti-picker") || document.body;
    const box = document.createElement("p");
    box.className = "status"; box.textContent = FAILED_COPY;
    host.appendChild(box);
    const retry = document.createElement("button");
    retry.type = "button"; retry.className = "go";
    retry.textContent = RETRY_COPY;
    retry.onclick = () => { location.reload(); };
    host.appendChild(retry);
    const cancel = document.createElement("button");
    cancel.type = "button"; cancel.className = "go ghost";
    cancel.textContent = CANCEL_COPY;
    cancel.onclick = () => { location.href = "about:blank"; };
    host.appendChild(cancel);
  }
}
document.getElementById("lti-link").addEventListener("click", () => {
  if(!selected) return;
  postResponse([{type: "ltiResourceLink",
                 url: LINK_BASE + "/lti/launch/" + selected.bank,
                 title: selected.objective,
                 custom: {objective: selected.objective, mode: "practice"}}]);
});
document.getElementById("lti-cancel").addEventListener("click", () => {
  postResponse([]);
});
