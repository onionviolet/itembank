import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { JSDOM } from "jsdom";
import { python } from "./python_bin.mjs";

const scripts = JSON.parse(execFileSync(python, ["-c", `
import json
from surfaces import quiz_page
print(json.dumps({
    "latex": quiz_page.LATEX_INPUT_JS,
    "structure": quiz_page.STRUCTURE_ADAPTER_JS,
    "math": quiz_page.MATH_ADAPTER_JS,
}))
`], { cwd: new URL("../..", import.meta.url), encoding: "utf8" }));

const settle = async () => {
  await new Promise(resolve => setTimeout(resolve, 25));
  await new Promise(resolve => setTimeout(resolve, 0));
};

test("quiz adapters enhance only changed content and flush hidden work on return", async () => {
  const dom = new JSDOM("<!doctype html><div id=host></div>", {
    url: "http://localhost/quiz/synthetic", runScripts: "outside-only",
    pretendToBeVisual: true,
  });
  const { window } = dom;
  const { document } = window;
  const host = document.getElementById("host");
  const autoRoots = [];
  const katexSources = [];
  window.katex = { render(source, target) {
    katexSources.push(source);
    target.dataset.renderedSource = source;
  } };
  window.renderMathInElement = root => { autoRoots.push(root); };
  window.eval(scripts.latex.replace(/^<script[^>]*>|<\/script>$/g, ""));
  window.eval(scripts.structure.replace(/^<script[^>]*>|<\/script>$/g, ""));
  window.eval(scripts.math.replace(/^<script[^>]*>|<\/script>$/g, ""));

  const argument = 'Consider the argument: "Every fern is a plant. Therefore, every fern grows."';
  host.innerHTML = `<section id="item"><h1 class="stem">${argument}</h1>` +
    `<p class="ot">Evaluate \`x^2\`.</p>` +
    `<div class="response"><textarea data-input-format="latex"></textarea></div></section>`;
  await settle();
  assert.equal(host.querySelectorAll(".quiz-argument-line").length, 2);
  assert.equal(host.querySelector(".quiz-math-source").dataset.renderedSource, "x^2");
  const input = host.querySelector("textarea");
  assert.equal(host.querySelectorAll(".latex-preview").length, 1);
  input.value = "a^2+b^2";
  input.dispatchEvent(new window.Event("input", { bubbles: true }));
  assert.equal(host.querySelector(".latex-preview").dataset.renderedSource, "a^2+b^2");

  const oldRoots = autoRoots.length;
  const originalQuery = host.querySelectorAll.bind(host);
  let globalScans = 0;
  host.querySelectorAll = selector => {
    if (selector === ".stem" || selector === ".stem,.ot,.rowtext" ||
        selector === 'textarea[data-input-format="latex"]') {
      globalScans += 1;
    }
    return originalQuery(selector);
  };
  for (let index = 0; index < 30; index += 1) {
    const unrelated = document.createElement("span");
    unrelated.textContent = `Unrelated ${index}`;
    host.appendChild(unrelated);
  }
  await settle();
  assert.equal(autoRoots.length, oldRoots, "unrelated mutations must not rerender math");
  assert.equal(globalScans, 0, "unrelated mutations must not rescan every item");

  let hidden = true;
  Object.defineProperty(document, "hidden", { configurable: true, get: () => hidden });
  host.innerHTML = '<section id="replacement"><h1 class="stem">' + argument +
    '</h1><p class="ot">Evaluate `y^3`.</p>' +
    '<textarea data-input-format="latex"></textarea></section>';
  await settle();
  assert.equal(host.querySelectorAll(".quiz-argument-line").length, 0);
  assert.equal(host.querySelectorAll(".latex-preview").length, 0);
  hidden = false;
  document.dispatchEvent(new window.Event("visibilitychange"));
  await settle();
  assert.equal(host.querySelectorAll(".quiz-argument-line").length, 2);
  assert.equal(host.querySelector(".quiz-math-source").dataset.renderedSource, "y^3");
  assert.equal(host.querySelectorAll(".latex-preview").length, 1);
  assert.ok(autoRoots.slice(oldRoots).every(root => root !== host),
    "replacement math should render from changed content, not the full host");
  const settledRoots = autoRoots.length;
  await settle();
  assert.equal(autoRoots.length, settledRoots, "adapters must not trigger each other forever");
  assert.ok(katexSources.includes("a^2+b^2"));
  dom.window.close();
});

test("direct math-source insertion and bundled KaTeX settle without observer feedback", async () => {
  const dom = new JSDOM("<!doctype html><div id=host></div>", {
    url: "http://localhost/quiz/synthetic", runScripts: "outside-only",
    pretendToBeVisual: true,
  });
  const { window } = dom;
  const { document } = window;
  for (const path of ["../../vendor/katex/katex.min.js",
    "../../vendor/katex/contrib/auto-render.min.js"]) {
    window.eval(readFileSync(new URL(path, import.meta.url), "utf8"));
  }
  let renders = 0;
  const render = window.renderMathInElement;
  window.renderMathInElement = (...args) => {
    renders += 1;
    return render(...args);
  };
  window.eval(scripts.math.replace(/^<script[^>]*>|<\/script>$/g, ""));
  const host = document.getElementById("host");
  const source = document.createElement("code");
  source.className = "quiz-math-source";
  source.textContent = "x^2";
  host.appendChild(source);
  await settle();
  assert.equal(source.dataset.mathRendered, "true",
    "a directly inserted math source must enter the renderer");
  assert.ok(source.querySelector(".katex"), "bundled KaTeX must render the source");

  const line = document.createElement("p");
  line.className = "ot";
  line.textContent = "Also $y^3$.";
  host.appendChild(line);
  await settle();
  assert.ok(line.querySelector(".katex"), "bundled auto-render must handle delimiters");
  const settled = renders;
  await settle();
  assert.equal(renders, settled, "KaTeX DOM mutations must not restart rendering");
  dom.window.close();
});
