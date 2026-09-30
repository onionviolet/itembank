import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { JSDOM } from "jsdom";
import { python } from "./python_bin.mjs";

const scripts = JSON.parse(execFileSync(python, ["-c", `
import json
from surfaces import quiz_page
print(json.dumps([quiz_page.OFFLINE_JS, quiz_page.SERVED_JS]))
`], { cwd: new URL("../..", import.meta.url), encoding: "utf8" }));

function setup(script, type = "dnd") {
  const dom = new JSDOM('<div id="body"></div><div id="act"></div>',
    { runScripts: "outside-only", url: "http://localhost/quiz/synthetic" });
  const win = dom.window;
  win.BOOT = { bank: "synthetic" };
  win.draftKey = (bank, item) => `itembank.draft.${bank}.${item}`;
  win.shuffled = rows => [...rows].reverse();
  win.mkSubmit = act => {
    const button = win.document.createElement("button");
    button.disabled = true; act.appendChild(button); return button;
  };
  const calls = [];
  win.settle = (q, answer, card, act, done, revert) => calls.push({ answer, done, revert });
  const start = script.indexOf("function asAssign(");
  win.eval(script.slice(start, script.indexOf("function asBuild(", start)));
  const question = { id: "bucket1", type, categories: ["red", "blue"], rows: [
    { id: "first", text: "Identical label" },
    { id: "second", text: "Identical label" },
  ] };
  const body = win.document.getElementById("body"), act = win.document.getElementById("act");
  win.asAssign(question, body, act, body);
  const drag = (id, category) => {
    const card = [...body.querySelectorAll("[data-drag-row]")].find(el => el.dataset.dragRow === id);
    const bucket = [...body.querySelectorAll("[data-category]")].find(el => el.dataset.category === category);
    const start = new win.Event("dragstart", { cancelable: true });
    Object.defineProperty(start, "dataTransfer", { value: { setData() {}, effectAllowed: "" } });
    card.dispatchEvent(start);
    bucket.dispatchEvent(new win.Event("dragover", { cancelable: true }));
    bucket.dispatchEvent(new win.Event("drop", { cancelable: true }));
    card.dispatchEvent(new win.Event("dragend"));
    return start;
  };
  return { dom, win, body, act, question, calls, drag };
}

for (const [index, script] of scripts.entries()) {
  test(`bucket dragging and category buttons submit the same stable answer, surface ${index}`, () => {
    const app = setup(script);
    try {
      assert.equal(app.body.querySelectorAll("[draggable=true]").length, 2);
      assert.equal(app.act.firstChild.disabled, true);
      // External and cross-item drops cannot supply a row ID to this reducer.
      app.body.querySelector('[data-category="red"]').dispatchEvent(new app.win.Event("drop", { cancelable: true }));
      assert.equal(app.body.querySelectorAll(".assignment-bucket li").length, 0);
      app.drag("first", "blue");
      app.drag("first", "red");
      assert.equal(app.body.querySelector('[data-category="blue"] li'), null);
      const second = app.body.querySelector('[data-drag-row="second"]').parentElement;
      [...second.querySelectorAll("button")].find(button => button.textContent === "red").click();
      assert.equal(app.act.firstChild.disabled, false);
      const entries = [...app.body.querySelectorAll('[data-category="red"] li')];
      assert.deepEqual(entries.map(el => el.dataset.rowId).sort(), ["first", "second"]);
      assert.ok(entries.every(el => el.textContent === "Identical label"));
      if (index === 1) {
        assert.deepEqual(JSON.parse(app.win.localStorage.getItem("itembank.draft.synthetic.bucket1")),
          { first: "red", second: "red" });
        const body = app.win.document.createElement("div"), act = app.win.document.createElement("div");
        app.win.asAssign(app.question, body, act, body);
        assert.equal(body.querySelectorAll('[data-category="red"] li').length, 2);
        assert.equal(act.firstChild.disabled, false);
      }
      app.act.firstChild.click();
      assert.deepEqual({ ...app.calls[0].answer }, { first: "red", second: "red" });
      assert.equal(app.drag("first", "blue").defaultPrevented, true);
      assert.equal(app.body.querySelector('[data-category="blue"] li'), null);
      if (index === 1) {
        app.calls[0].revert();
        app.drag("first", "blue");
        assert.equal(app.body.querySelector('[data-category="blue"] li').dataset.rowId, "first");
        app.act.firstChild.click();
        assert.deepEqual({ ...app.calls[1].answer }, { first: "blue", second: "red" });
        app.calls[1].done({ explain: {} });
        assert.equal(app.win.localStorage.getItem("itembank.draft.synthetic.bucket1"), null);
      } else app.calls[0].done({ explain: {} });
    } finally { app.dom.window.close(); }
  });

  test(`table classification keeps its existing controls, surface ${index}`, () => {
    const app = setup(script, "table");
    try {
      assert.equal(app.body.querySelector(".assignment-buckets"), null);
      assert.equal(app.body.querySelector("[draggable=true]"), null);
      assert.equal(app.body.querySelectorAll("button").length, 4);
    } finally { app.dom.window.close(); }
  });
}
