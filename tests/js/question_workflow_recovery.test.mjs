import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { JSDOM } from "jsdom";
import { python } from "./python_bin.mjs";

const fixture = JSON.parse(execFileSync(python, ["-c", `
import json
from surfaces import quiz_page
base = dict(id="synthetic", number=1, stem="Synthetic task", type="dnd",
            categories=["red", "blue"], rows=[dict(id=0,text="A ___ word."),dict(id=1,text="A ___ word.")])
def page(item):
    return quiz_page.baseline_for(dict(session_id="synthetic", item=item), {}, "/answer", dict(submit="token"))
print(json.dumps(dict(script=quiz_page.SERVED_JS, assignment=page(base),
    build=page(dict(base, type="build", steps=["Read", "Measure", "Compare"])))))
`], { cwd: new URL("../..", import.meta.url), encoding: "utf8" }));

function setup(html) {
  const dom = new JSDOM(`<div id="host">${html}</div>`,
    { runScripts: "outside-only", url: "http://localhost/quiz/synthetic" });
  const w = dom.window;
  w.BOOT = {bank: "synthetic"}; w.host = w.document.getElementById("host");
  w.sessionId = null; w.setContext = ()=>{};
  w.api = ()=>{ throw new Error("Normal baseline must not start another sitting"); };
  const begin = fixture.script.indexOf("function draftKey(");
  w.eval(fixture.script.slice(begin, fixture.script.indexOf("/* ---- start:", begin)));
  const start = fixture.script.indexOf("async function start()");
  w.eval(fixture.script.slice(start, fixture.script.indexOf("if(BOOT && BOOT.bank)", start)));
  return {dom, w, baseline: w.host.querySelector("[data-server-baseline]")};
}

test("normal server baseline enhances blanks, saves drops and retains its native POST", async () => {
  const {dom, w, baseline} = setup(fixture.assignment);
  try {
    await w.start();
    const form = baseline.querySelector("form");
    assert.equal(form.getAttribute("action"), "/answer");
    assert.equal(form.querySelector('[name="form_token"]').value, "token");
    const word = form.querySelector('[data-word="blue"]');
    const labels = [...form.querySelectorAll(".inline-completion")];
    assert.ok(word && word.draggable);
    labels[0].dispatchEvent(new w.Event("drop", {cancelable:true}));
    assert.equal(labels[0].querySelector("select").value, "");
    for (const label of labels) {
      word.dispatchEvent(new w.Event("dragstart", {cancelable:true}));
      label.dispatchEvent(new w.Event("drop", {cancelable:true}));
    }
    assert.deepEqual(JSON.parse(w.localStorage.getItem("itembank.draft.synthetic.synthetic")), {0:"blue",1:"blue"});
    const data = new w.FormData(form);
    assert.deepEqual([data.get("row_0"), data.get("row_1")], ["blue", "blue"]);
    baseline.replaceWith(w.document.createRange().createContextualFragment(fixture.assignment));
    await w.start();
    assert.ok([...w.host.querySelectorAll(".inline-completion select")].every(el=>el.value === "blue"));
    const freshForm = w.host.querySelector("form");
    freshForm.dispatchEvent(new w.Event("submit", {cancelable:true}));
    const blocked = new w.Event("dragstart", {cancelable:true});
    freshForm.querySelector('[data-word="red"]').dispatchEvent(blocked);
    assert.equal(blocked.defaultPrevented, true);
  } finally { dom.window.close(); }
});

test("native build selects restore gaps, reject foreign drafts and exchange order with dynamic controls", async () => {
  const {dom, w} = setup(fixture.build);
  try {
    const key = "itembank.draft.synthetic.synthetic";
    w.localStorage.setItem(key, JSON.stringify(["", "Measure", ""]));
    await w.start();
    const selects = [...w.host.querySelectorAll('select[name^="step_"]')];
    assert.deepEqual(selects.map(el=>el.value), ["", "Measure", ""]);
    selects[0].value = "Read";
    selects[0].dispatchEvent(new w.Event("change", {bubbles:true}));
    assert.deepEqual(JSON.parse(w.localStorage.getItem(key)), ["Read", "Measure", ""]);
    w.shuffled = x=>x; w.esc = x=>x;
    w.mkSubmit = act=>{const b=w.document.createElement("button"); act.append(b); return b;};
    const start = fixture.script.indexOf("function asBuild(");
    w.eval(fixture.script.slice(start, fixture.script.indexOf("function asShort(",start)));
    const q = {id:"synthetic",type:"build",steps:["Read","Measure","Compare"]};
    const body = w.document.createElement("div"), act = w.document.createElement("div");
    w.asBuild(q, body, act, body);
    assert.deepEqual([...body.querySelectorAll(".ord")].map(el=>el.textContent), ["1","2","-"]);
    assert.equal(act.firstChild.disabled, true);
    body.querySelectorAll("button")[2].click();
    assert.equal(act.firstChild.disabled, false);
    assert.deepEqual(JSON.parse(w.localStorage.getItem(key)), q.steps);
    w.settle = (q, answer, card, actions, done, revert)=>revert();
    act.firstChild.click();
    assert.equal(act.firstChild.disabled, false);
    assert.deepEqual(JSON.parse(w.localStorage.getItem(key)), q.steps);
    let submitted;
    w.settle = (q, answer, card, actions, done)=>{submitted=answer;done({explain:{}});};
    act.firstChild.click();
    assert.deepEqual([...submitted], q.steps);
    assert.equal(w.localStorage.getItem(key), null);
    for (const invalid of [["Read","Read"], ["foreign"], ["Read","Measure","Compare","extra"]]) {
      assert.deepEqual([...w.readBuildDraft(invalid,q.steps)], []);
    }
    w.localStorage.setItem(key,JSON.stringify(["", "Measure"]));
    const otherBody=w.document.createElement("div"), otherAct=w.document.createElement("div");
    w.asBuild(q,otherBody,otherAct,otherBody);
    assert.equal(otherBody.querySelectorAll(".ord")[1].textContent,"2");
    otherBody.querySelectorAll("button")[0].click();
    assert.deepEqual(JSON.parse(w.localStorage.getItem(key)),["Read","Measure"]);
  } finally { dom.window.close(); }
});

test("word-bank fallback survives unavailable storage without changing native controls", () => {
  const {dom,w,baseline}=setup(fixture.assignment);
  try {
    Object.defineProperty(w,"localStorage",{get(){throw new Error("storage unavailable");}});
    w.installDraft(baseline);
    assert.equal(baseline.querySelectorAll(".inline-word-bank").length,1);
    assert.equal(baseline.querySelectorAll("select").length,2);
    w.installDraft(baseline);
    assert.equal(baseline.querySelectorAll(".inline-word-bank").length,1);
  } finally {dom.window.close();}
});
