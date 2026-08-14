import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { JSDOM } from "jsdom";

const python = process.env.PYTHON || "python";
const payload = JSON.parse(execFileSync(python, ["-c",
  "import json; from surfaces.lesson import RUNNABLE_JS; " +
  "from surfaces.quiz_page import ASSIST_JS, SERVED_JS; " +
  "print(json.dumps({'run':RUNNABLE_JS,'assist':ASSIST_JS,'served':SERVED_JS}))"],
  { cwd: new URL("../..", import.meta.url), encoding: "utf8" }));

const scriptBody = html => html.replace(/^<script>/, "").replace(/<\/script>$/, "");
const flush = () => new Promise(resolve => setTimeout(resolve, 0));

test("runnable status promotes attributes before failure text and restores idle", async () => {
  const dom = new JSDOM(`<main id="lesson-content" data-run-session="s">
    <div data-code-block="1" data-lang="python"><textarea class="run-source">x</textarea>
    <button class="run-go" aria-describedby="run-status-1">Run</button>
    <p id="run-status-1" class="run-status" aria-live="off"></p>
    <pre class="run-stdout"></pre><pre class="run-stderr"></pre></div></main>`,
    { runScripts: "outside-only" });
  class XHR {
    open() {} setRequestHeader() {}
    send() { this.status = 500; this.responseText = "{}"; this.onload(); }
  }
  dom.window.XMLHttpRequest = XHR;
  dom.window.eval(scriptBody(payload.run));
  const status = dom.window.document.querySelector(".run-status");
  const mutations = [];
  new dom.window.MutationObserver(rows => rows.forEach(row => mutations.push(
    row.type === "attributes" ? `attr:${row.attributeName}`
      : `text:${status.textContent}`))).observe(status,
        { attributes:true, childList:true, subtree:true });
  dom.window.document.querySelector(".run-go").click();
  await flush();
  const failureText = mutations.map((x, i) => x.startsWith("text:") ? i : -1)
    .filter(i => i >= 0).at(-1);
  assert.ok(failureText > mutations.findIndex(x => x === "attr:role"));
  assert.ok(failureText > mutations.lastIndexOf("attr:aria-live"));
  assert.equal(status.getAttribute("role"), "alert");
  assert.equal(status.getAttribute("aria-live"), "assertive");
  assert.notEqual(status.getAttribute("aria-live"), "off");
});

test("assist status is live only while a requested result is pending", async () => {
  const dom = new JSDOM(`<button id="assist-request"></button><p id="assist-status"></p>
    <div id="assist-outcome" hidden></div>`, { runScripts:"outside-only" });
  let resolveFetch;
  dom.window.fetch = () => new Promise(resolve => { resolveFetch = resolve; });
  dom.window.eval(payload.assist);
  dom.window.Assist.setSession("s");
  const status = dom.window.document.getElementById("assist-status");
  dom.window.document.getElementById("assist-request").click();
  assert.equal(status.getAttribute("aria-live"), "polite");
  assert.match(status.textContent, /Preparing optional guidance/);
  resolveFetch({ok:true, json:async()=>({status:"cancelled"})});
  await flush(); await flush();
  assert.equal(status.hasAttribute("aria-live"), false);
  assert.equal(status.textContent, "");
  assert.match(dom.window.document.getElementById("assist-outcome").textContent, /cancelled/i);
});

test("visual ActionStatus orders alert attributes before blocking text", async () => {
  const match = payload.served.match(/function setVisualStatus\(status, text, isError\)\{[\s\S]*?\n\}/);
  assert.ok(match, "shipped served client must expose setVisualStatus");
  const dom = new JSDOM(`<div class="visual-status" role="status" aria-live="polite"></div>`,
    {runScripts:"outside-only"});
  dom.window.eval(`${match[0]}; window.setVisualStatus=setVisualStatus;`);
  const status = dom.window.document.querySelector(".visual-status");
  const mutations = [];
  new dom.window.MutationObserver(rows => rows.forEach(row => mutations.push(
    row.type === "attributes" ? `attr:${row.attributeName}`
      : `text:${status.textContent}`))).observe(status,
        {attributes:true, childList:true, subtree:true});
  dom.window.setVisualStatus(status, "Commit your move before checking it.", true);
  await flush();
  const text = mutations.findIndex(x => x.startsWith("text:Commit your move"));
  assert.ok(text > mutations.findIndex(x => x === "attr:role"));
  assert.ok(text > mutations.findIndex(x => x === "attr:aria-live"));
  dom.window.setVisualStatus(status, "Move committed.", false);
  assert.equal(status.getAttribute("role"), "status");
  assert.equal(status.getAttribute("aria-live"), "polite");
});
