import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";

const python = process.env.PYTHON || "python";
const source = execFileSync(python, ["-c",
  "from surfaces.quiz_page import SERVED_JS; print(SERVED_JS)"],
  { cwd: new URL("../..", import.meta.url), encoding: "utf8" });

test("the shipped ladder has no reveal countdown or disabled affordance", () => {
  assert.match(source, /class=\"hint-ladder\"/);
  assert.match(source, /data-teach=/);
  assert.doesNotMatch(source, /progressbar|aria-disabled|Show answer|Reveal answer/);
  assert.doesNotMatch(source, /lock-glyph|assist-lock|Optional guidance is locked/);
});

test("locked cards render only route-provided headers and unlock copy", () => {
  assert.match(source, /row\.header/);
  assert.match(source, /row\.unlock_copy/);
  assert.doesNotMatch(source, /row\.content|row\.answer|row\.key/);
});

test("tier actions cannot name a tier", () => {
  assert.match(source, /action:\{kind:button\.dataset\.teach\}/);
  assert.doesNotMatch(source, /tier_index|tier_id|requested_tier/);
});
