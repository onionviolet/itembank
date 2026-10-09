import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { JSDOM } from "jsdom";
import { python } from "./python_bin.mjs";

const fixture = JSON.parse(execFileSync(python, ["-c", `
import html, json
from surfaces import lesson_interaction
print(json.dumps({"body": lesson_interaction.render(
    {"a":12,"b":18,"max":24,"unit":"mm","text":"Compare equal time intervals."}, html.escape),
    "script": lesson_interaction.JS}))
`], { cwd: new URL("../..", import.meta.url), encoding: "utf8" }));

test("comparison supports exact entry, step buttons, bounds, reset and back navigation", () => {
  const dom = new JSDOM(fixture.body, { runScripts: "outside-only" });
  const { window } = dom;
  const root = window.document.querySelector(".lesson-comparison");
  const controls = root.querySelector(".comparison-controls");
  assert.equal(controls.hidden, true, "static reading must work before enhancement");
  assert.match(root.textContent, /B minus A = 6 mm/);
  window.eval(fixture.script.replace(/^<script[^>]*>|<\/script>$/g, ""));
  const range = root.querySelector("input[type=range]");
  const number = root.querySelector(".comparison-number");
  const result = root.querySelector(".comparison-result");
  const decrease = root.querySelector(".comparison-decrease");
  const increase = root.querySelector(".comparison-increase");
  const change = value => {
    number.value = value;
    number.dispatchEvent(new window.Event("change"));
  };
  assert.equal(controls.hidden, false);
  change("12");
  assert.equal(range.value, "12");
  assert.match(result.textContent, /Equal quantities/);
  assert.match(result.textContent, /Hypothetical value/);
  decrease.click();
  assert.equal(number.value, "11");
  assert.equal(root.querySelector(".comparison-meter-b").value, 11);
  assert.match(result.textContent, /1 mm lower/);
  increase.click();
  assert.equal(number.value, "12");
  window.dispatchEvent(new window.Event("pageshow"));
  assert.equal(number.value, "12", "returning must preserve the current exploration");
  for (const invalid of ["", "25", "-1", "3.5"]) {
    change(invalid);
    assert.equal(number.validity.valid, false);
    assert.equal(range.value, "12", "invalid entry must not silently change the model");
  }
  change("0");
  assert.equal(decrease.disabled, true);
  assert.equal(increase.disabled, false);
  change("24");
  assert.equal(increase.disabled, true);
  range.value = "8";
  range.dispatchEvent(new window.Event("input"));
  assert.equal(number.value, "8");
  assert.equal(increase.disabled, false);
  root.querySelector(".comparison-reset").click();
  assert.equal(number.value, "18");
  assert.equal(number.validity.valid, true);
  assert.match(result.textContent, /Authored starting value/);
  dom.window.close();
});

function gesturePage(copies = 1) {
  const dom = new JSDOM(fixture.body.repeat(copies), { runScripts: "outside-only" });
  const { window } = dom;
  const observers = [];
  window.ResizeObserver = class {
    constructor(callback) { this.callback = callback; observers.push(this); }
    observe(target) { this.target = target; }
  };
  window.eval(fixture.script.replace(/^<script[^>]*>|<\/script>$/g, ""));
  const views = [...window.document.querySelectorAll(".lesson-comparison")].map(root => {
    const handle = root.querySelector(".comparison-handle");
    const range = root.querySelector("input[type=range]");
    let captured = null;
    handle.setPointerCapture = id => { captured = id; };
    handle.hasPointerCapture = id => captured === id;
    handle.releasePointerCapture = id => {
      assert.equal(captured, id);
      captured = null;
      send("lostpointercapture", 0, { pointerId: id });
    };
    const bounds = {left:100, width:240, height:52};
    const direct = root.querySelector(".comparison-direct");
    direct.getBoundingClientRect = () => bounds;
    function send(type, x, extra = {}) {
      const event = new window.Event(type, {bubbles:true, cancelable:true});
      Object.assign(event, {pointerId:1, isPrimary:true, button:0, clientX:x, clientY:50}, extra);
      handle.dispatchEvent(event);
    }
    return {root, handle, range, send, bounds, resize: () => observers.find(observer => observer.target === direct).callback(),
      capture: () => captured};
  });
  return {dom, window, views};
}

test("B drag retains grab offset, waits for intent, clamps and commits only on release", () => {
  const {dom, views:[view]} = gesturePage();
  const {range, root, handle, send} = view;
  send("pointerdown", 290); // B endpoint is 280; grab ten pixels to its right.
  assert.equal(dom.window.document.activeElement, range);
  send("pointermove", 293);
  assert.equal(range.value, "18");
  assert.equal(handle.dataset.pending, "0");
  send("pointermove", 315);
  assert.equal(range.value, "21", "half steps snap to a whole authored unit");
  assert.match(root.querySelector(".comparison-result").textContent, /Preview/);
  send("pointermove", 900, {pointerId:2});
  assert.equal(range.value, "21", "another pointer must not alter the gesture");
  send("pointermove", 900);
  assert.equal(range.value, "24");
  send("pointermove", -200);
  assert.equal(range.value, "0");
  send("pointermove", 310);
  send("pointerup", 310);
  assert.equal(range.value, "20");
  assert.equal(view.capture(), null);
  assert.equal(handle.dataset.pending, "0");
  assert.doesNotMatch(root.querySelector(".comparison-result").textContent, /Preview/);
  dom.window.close();
});

test("all gesture interruptions restore the value at grab and clear preview and capture", () => {
  for (const reason of ["Escape", "blur", "resize", "pointercancel", "lostpointercapture", "pagehide", "focusloss"]) {
    const {dom, window, views:[view]} = gesturePage();
    const {range, root, send} = view;
    range.value = "9";
    range.dispatchEvent(new window.Event("input"));
    send("pointerdown", 200);
    send("pointermove", 240);
    assert.equal(range.value, "13");
    if (reason === "Escape") range.dispatchEvent(new window.KeyboardEvent("keydown", {key:"Escape", bubbles:true}));
    else if (reason === "focusloss") range.dispatchEvent(new window.Event("blur"));
    else if (reason.startsWith("pointer") || reason === "lostpointercapture") send(reason, 240);
    else window.dispatchEvent(new window.Event(reason));
    assert.equal(range.value, "9", reason);
    assert.equal(root.querySelector(".comparison-number").value, "9", reason);
    assert.equal(view.capture(), null, reason);
    assert.equal(view.handle.dataset.pending, "0", reason);
    assert.doesNotMatch(root.querySelector(".comparison-result").textContent, /Preview/, reason);
    send("pointerup", 240);
    assert.equal(range.value, "9", "release after cancellation cannot commit");
    dom.window.close();
  }
});

test("instances remain isolated and cancelled movement is never the next gesture's base", () => {
  const {dom, window, views:[first, second]} = gesturePage(2);
  first.send("pointerdown", 280);
  first.send("pointermove", 300);
  assert.equal(first.range.value, "20");
  assert.equal(second.range.value, "18");
  first.send("pointercancel", 300);
  first.send("pointerdown", 280);
  first.send("pointermove", 260);
  first.send("pointerup", 260);
  assert.equal(first.range.value, "16");
  window.dispatchEvent(new window.Event("pageshow"));
  assert.equal(first.range.value, "16");
  second.root.querySelector(".comparison-increase").click();
  assert.equal(second.range.value, "19");
  assert.equal(first.range.value, "16");
  dom.window.close();
});

test("a tap, secondary pointer or failed capture does not change B", () => {
  const {dom, views:[view]} = gesturePage();
  view.send("pointerdown", 280, {button:2});
  assert.equal(view.capture(), null);
  view.send("pointerdown", 280, {isPrimary:false});
  assert.equal(view.capture(), null);
  view.send("pointerdown", 280);
  view.send("pointerup", 280);
  assert.equal(view.range.value, "18");
  assert.equal(view.capture(), null);
  view.handle.setPointerCapture = () => { throw new Error("capture unavailable"); };
  view.send("pointerdown", 280);
  view.send("pointermove", 320);
  assert.equal(view.range.value, "18");
  assert.equal(view.handle.dataset.pending, "0");
  dom.window.close();
});

test("release applies the last pointer position and direct layout resize cancels", () => {
  const {dom, views:[view]} = gesturePage();
  view.send("pointerdown", 280);
  view.send("pointermove", 300);
  assert.equal(view.range.value, "20");
  view.send("pointerup", 310);
  assert.equal(view.range.value, "21", "release can arrive after the last move event");
  view.send("pointerdown", 310);
  view.send("pointermove", 320);
  view.resize();
  assert.equal(view.range.value, "22", "initial unchanged observer delivery keeps the gesture");
  view.bounds.width = 200;
  view.resize();
  assert.equal(view.range.value, "21", "control resize restores the value at grab");
  assert.equal(view.capture(), null);
  assert.equal(view.handle.dataset.pending, "0");
  view.send("pointerup", 320);
  assert.equal(view.range.value, "21");
  dom.window.close();
});
