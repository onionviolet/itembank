// Resolves the Python interpreter these tests spawn. CI installs a `python`
// shim, but a plain macOS shell often has only `python3`, so hardcoding either
// name makes the suite fail with ENOENT before a single assertion runs.
import { spawnSync } from "node:child_process";

function works(candidate) {
  const probe = spawnSync(candidate, ["-c", ""], { stdio: "ignore" });
  return !probe.error && probe.status === 0;
}

function resolve() {
  if (process.env.PYTHON) return process.env.PYTHON;
  for (const candidate of ["python3", "python"]) {
    if (works(candidate)) return candidate;
  }
  throw new Error(
    "No Python interpreter found: tried python3 and python. " +
    "Set PYTHON to the interpreter these tests should spawn.");
}

export const python = resolve();
