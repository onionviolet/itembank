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

test("native assignment drafts exchange stable IDs with dynamic controls", () => {
  const dom = new JSDOM(`<div data-item-id="q1" data-response-type="dnd">
    <form data-answer-form><select name="row_0" data-row-id="second">
    <option value=""></option><option>blue</option><option>red</option></select>
    <select name="row_1" data-row-id="first"><option value=""></option>
    <option>blue</option><option>red</option></select></form></div>`,
    { runScripts: "outside-only", url: "http://localhost/quiz/synthetic" });
  try {
    const win = dom.window;
    win.BOOT = { bank: "synthetic" };
    win.localStorage.setItem("itembank.draft.synthetic.q1", JSON.stringify({ first: "red", second: "blue" }));
    const start = scripts[1].indexOf("function draftKey(");
    const end = scripts[1].indexOf("/* ---- start:", start);
    win.eval(scripts[1].slice(start, end));
    win.installDraft(win.document.querySelector("div"));
    const controls = [...win.document.querySelectorAll("select")];
    assert.deepEqual(controls.map(select => select.value), ["blue", "red"]);
    controls[0].value = "red";
    controls[0].dispatchEvent(new win.Event("change", { bubbles: true }));
    assert.deepEqual(JSON.parse(win.localStorage.getItem("itembank.draft.synthetic.q1")),
      { first: "red", second: "red" });
  } finally { dom.window.close(); }
});

test("visual commit selects remain outside assignment draft restoration and capture", () => {
  const dom = new JSDOM(`<div data-item-id="visual1" data-response-type="visual">
    <form data-answer-form><select data-row-id="point"><option>red</option>
    <option>blue</option></select></form></div>`,
    { runScripts: "outside-only", url: "http://localhost/quiz/synthetic" });
  try {
    const win = dom.window;
    win.BOOT = { bank: "synthetic" };
    const key = "itembank.draft.synthetic.visual1";
    win.localStorage.setItem(key, JSON.stringify({ point: "blue" }));
    const start = scripts[1].indexOf("function draftKey(");
    win.eval(scripts[1].slice(start, scripts[1].indexOf("/* ---- start:", start)));
    win.installDraft(win.document.querySelector("div"));
    const select = win.document.querySelector("select");
    assert.equal(select.value, "red");
    select.value = "blue";
    select.dispatchEvent(new win.Event("input", { bubbles: true }));
    assert.deepEqual(JSON.parse(win.localStorage.getItem(key)), []);
  } finally { dom.window.close(); }
});

for (const [index, script] of scripts.entries()) {
  test(`inline completion saves stable row assignments, surface ${index}`, () => {
    const dom = new JSDOM('<div id="body"></div><div id="act"></div>',
      { runScripts: "outside-only", url: "http://localhost/quiz/synthetic" });
    try {
      const win = dom.window;
      let response;
      win.BOOT = { bank: "synthetic" };
      win.draftKey = (bank, item) => `itembank.draft.${bank}.${item}`;
      win.shuffled = rows => [...rows].reverse();
      win.mkSubmit = act => {
        const button = win.document.createElement("button");
        button.disabled = true; act.appendChild(button); return button;
      };
      win.settle = (q, answer, card, act, done) => {
        response = answer;
        done({ explain: { row_cats: { first: "blue", second: "blue" } } });
      };
      const start = script.indexOf("function asAssign(");
      const end = script.indexOf("function asBuild(", start);
      win.eval(script.slice(start, end));
      const body = win.document.getElementById("body");
      const act = win.document.getElementById("act");
      const question = { id: "q1", type: "dnd", categories: ["red", "blue"], rows: [
        { id: "first", text: "A ___ token." },
        { id: "second", text: "A ___ token." },
      ] };
      win.asAssign(question, body, act, body);
      const selects = [...body.querySelectorAll("select")];
      assert.equal(selects.length, 2);
      assert.match(selects[0].getAttribute("aria-label"), /second/);
      assert.equal(act.firstChild.disabled, true);
      const word = body.querySelector('[data-word="blue"]');
      assert.ok(word && word.draggable);
      const labels = [...body.querySelectorAll('.inline-completion')];
      labels[0].dispatchEvent(new win.Event('drop', { cancelable: true }));
      assert.equal(selects[0].value, '');
      for (const label of labels) {
        word.dispatchEvent(new win.Event('dragstart', { cancelable: true }));
        const over = new win.Event('dragover', { cancelable: true });
        label.dispatchEvent(over);
        assert.equal(over.defaultPrevented, true);
        label.dispatchEvent(new win.Event('drop', { cancelable: true }));
      }
      assert.ok(selects.every(select => select.value === 'blue'));
      assert.equal(body.querySelectorAll('[data-word="blue"]').length, 1);
      for (const select of selects) {
        select.value = "blue";
        select.dispatchEvent(new win.Event("change"));
      }
      assert.equal(act.firstChild.disabled, false);
      if (index === 1) {
        assert.deepEqual(JSON.parse(win.localStorage.getItem(win.draftKey("synthetic", "q1"))),
          { first: "blue", second: "blue" });
        const restored = win.document.createElement("div");
        const actions = win.document.createElement("div");
        win.asAssign(question, restored, actions, restored);
        assert.ok([...restored.querySelectorAll("select")].every(select => select.value === "blue"));
        assert.equal(actions.firstChild.disabled, false);
        const plain = win.document.createElement("div");
        const plainActions = win.document.createElement("div");
        win.asAssign({ ...question, rows: question.rows.map(row => ({ ...row, text: "Plain row" })) },
          plain, plainActions, plain);
        assert.equal(plain.querySelectorAll('button[aria-pressed="true"]').length, 2);
        assert.ok([...plain.querySelectorAll('button[aria-pressed="true"]')]
          .every(button => button.textContent === "blue"));
        assert.equal(plainActions.firstChild.disabled, false);
        const other = win.document.createElement("div");
        const otherActions = win.document.createElement("div");
        win.asAssign({ ...question, id: "q2" }, other, otherActions, other);
        assert.ok([...other.querySelectorAll("select")].every(select => select.value === ""));
        assert.equal(otherActions.firstChild.disabled, true);
      }
      selects[0].value = "";
      selects[0].dispatchEvent(new win.Event("change"));
      assert.equal(act.firstChild.disabled, true);
      selects[0].value = "blue";
      selects[0].dispatchEvent(new win.Event("change"));
      if (index === 1) {
        const settle = win.settle;
        win.settle = (q, answer, card, actions, done, revert) => revert();
        act.firstChild.click();
        assert.ok(selects.every(select => !select.disabled && select.value === "blue"));
        assert.equal(act.firstChild.disabled, false);
        win.settle = settle;
      }
      act.firstChild.click();
      assert.deepEqual({ ...response }, { first: "blue", second: "blue" });
      assert.ok(selects.every(select => select.disabled && select.classList.contains("right")));
      const blocked = new win.Event('dragstart', { cancelable: true });
      word.dispatchEvent(blocked);
      assert.equal(blocked.defaultPrevented, true);
      if (index === 1) assert.equal(win.localStorage.getItem(win.draftKey("synthetic", "q1")), null);
    } finally { dom.window.close(); }
  });
}
