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
