# Reasonix harness: parallel subagent dispatch probe (2026-08-10)

- **Date:** 2026-08-10
- **Status:** PASS — all three artifacts landed byte-exact on the FIRST
  dispatch; no retry, no drift, no destruction.
- **Purpose:** determine whether subagents spawned in parallel reliably land
  exact artifacts on disk in THIS harness (Reasonix), to decide whether GSD
  wave-parallel execution (`gsd-execute-phase` waves) can run here instead of
  the Codex harness (where spawn payloads drop, fork agents drift, and typed
  executors hang — see `2026-08-10-subagent-dispatch-recipe.md`).

## Step 0 — tooling discovery

This harness HAS native multi-agent tooling (no "no parallel dispatch"
verdict):

- `fleet` — dispatch 2–64 sub-agent tasks as a small dependency graph;
  independent tasks run in parallel; concurrent writers must declare
  non-overlapping `write_paths`. **Used for this probe.**
- `task` — single sub-agent (supports `run_in_background`).
- `parallel_tasks` / `explore` / `research` / `review` — read-only fan-out
  (cannot write artifacts; not suitable for wave executors).

Syntax used:
`fleet(tasks=[{id, description, prompt, tools:["write_file"], write_paths:[<own file>], max_steps:5}], run_in_background=true)` —
three workers, each with the FULL task inline (no file pointer), each prompt
ending "Create no other files. Spawn no agents. Stop after writing the file."

## Step 1 — parallel message-payload test

Dispatched three workers IN PARALLEL via `fleet`. All three completed within
~10 s of dispatch and returned final answers; no interruption or re-dispatch
needed. Note: `"reasonix-a"` is 10 bytes (the probe text quoted the content,
not a byte count); the workers wrote the quoted content verbatim, which is
the byte-exact requirement.

| Worker | Launched | Completed a turn | File landed (byte-exact) |
|--------|----------|------------------|--------------------------|
| worker-a | yes | yes | yes — `reasonix-a` (10 B, no NL, no BOM) |
| worker-b | yes | yes | yes — `reasonix-b` (10 B, no NL, no BOM) |
| worker-c | yes | yes | yes — `reasonix-c` (10 B, no NL, no BOM) |

Verification (orchestrator, python `rb` read of each file): all three files
byte-exact against the specified content, no trailing newline, no BOM;
`.planning/probes/reasonix/` contains exactly the three files and nothing
else. The workers' own self-reported status was "partial" only because their
tool whitelist excluded a read-back tool — the on-disk check by the
orchestrator is what matters and it is PASS.

## Step 2 — brief-file retry

NOT NEEDED. All three files landed on the first dispatch.

## Step 3 — drift & destruction check

- Sub-subagent spawns: none. Worker whitelist was `["write_file"]` only (no
  agent/spawn tool exposed), and all three final answers report no spawns.
- Changes outside `.planning/probes/reasonix/`: none. Host receipts show each
  worker changed exactly one file (its own target).
- `git status --short` BEFORE vs AFTER the run: **byte-identical** (diff
  empty). No tracked-file change outside `.planning/`; no new untracked
  paths.
- Wall-clock / overlap: all three files first appeared within a single
  0.25 s disk-poll sample (~10 s after dispatch); all three subagent sessions
  share the same launch timestamp. Genuine overlap — NOT serialized
  execution.

## Harness quirks observed (record for wave-parallel use)

1. `write_file` writes exactly the given content — its "wrote N bytes"
   report equals the content length, i.e. no trailing newline is appended.
2. Host receipts flagged each write as "OUTSIDE DECLARED write_paths" because
   the tool resolves paths with backslashes on Windows while the declared
   `write_paths` used forward slashes. Cosmetic audit flag only: the fleet
   preflight accepted the parallel layout and the files landed at the
   declared paths. Declare paths in backslash form if the noise matters.
3. The harness's bash tool mangles `;`-separated statements and inline
   variable assignments; multi-statement scripts must be written to a file
   and executed. Does not affect subagent dispatch (workers used `write_file`
   only).
4. The harness auto-persists permission state to an untracked `reasonix.toml`
   in the workspace root (content = approved command allow-list) shortly
   after a command is approved. Harness-owned, not worker-created, not a
   tracked change; future drift checks should filter harness-owned untracked
   files (`reasonix.toml`, `.reasonix/`) from before/after `git status`
   comparisons.

## Verdict

**PASS.** All three parallel workers landed byte-exact artifacts on the
first dispatch, overlapped in time, and produced zero drift, zero spawns,
and zero changes outside `.planning/`. Unlike the Codex harness (payload
drops, fork drift, destructive recursion — `2026-08-10-subagent-dispatch-
recipe.md`), this harness delivers inline task payloads to parallel
subagents intact. **Recommend adopting this harness for GSD wave-parallel
execution**: wave dispatch = `fleet` with per-worker `write_paths`, full
inline task prompts, and disk verification per wave (never trust reply
text). Inline remains a fine fallback, but is no longer the only mode.
