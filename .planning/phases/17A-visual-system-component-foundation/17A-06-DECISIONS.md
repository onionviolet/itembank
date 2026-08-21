# 17A-06 decision: adopt DeepSeek Harness, drive it as a subprocess

- **Decided:** 2026-08-21
- **Closes:** Task 1 of `17A-06-PLAN.md`
- **Verdict:** **Adopt.** Do not build a second agent console.

## The four answers Task 1 asked for

| Question | Answer | How it was checked |
|---|---|---|
| Which project | `deepseek-ai/deepseek-harness` (`dsh`) | GitHub API, 2026-08-21 |
| Licence | **MIT** | GitHub API `license.spdx_id` |
| Embed or launch beside | **Neither. Drive it as a subprocess.** | `python/README.md` |
| Egress | Whatever provider its config names; local providers keep traffic on the machine | `packages/llm/llm/README.md` |

Also verified rather than assumed: 180,182 stars, TypeScript, `pushed_at`
2026-08-21, `archived: false`. Weibao's "actively in development" is correct to
the day.

## Why adopt wins

The plan said adopt should win unless one of three things was true. None is.

1. **Competing state?** `dsh` keeps an append-only `SessionEvent` log in SQLite
   (`core/session`, `packages/session/`). That is *agent conversation* state,
   not accepted course artifacts. The two objects do not overlap, and the
   boundary below keeps them apart.
2. **Writes without undo?** No. `packages/interaction/` owns "approval /
   interaction capabilities, permission, commands, ask-user", and
   `packages/fs/` is "filesystem capability + policy". It has an approval
   model of its own, and in any case itembank keeps acceptance.
3. **Licence blocks Phase 18?** No. MIT permits the packaged desktop app.

And two things make it a better fit than expected:

- **It has a Python SDK.** `python/README.md`: "Python packages for driving
  DeepSeek Harness as a subprocess. The client SDK communicates with the
  bundled runtime over newline-delimited JSON-RPC on stdio." itembank is
  Python. This is not an iframe problem.
- **It has a skill registry.** `packages/skill/` is a "skill provider registry
  + local impl + catalog/loader tool". itembank already has ten skills under
  `.claude/skills/`. That is the real prize, and it is a later plan, not this
  one.

## The integration shape

**A new `dsh_stdio` transport module in `model_adapter.py`, plus a settings
profile.** Not an iframe of the `dsh web` UI at `127.0.0.1:3080`.

This is exactly the seam D-27 already describes: "Adding a third backend is a
registry entry plus a config entry, with zero edits to tier-gate, evidence, or
prompt-assembly code."

The shipped `hosted_cli` transport is close but not sufficient. It is one-shot
`subprocess.run` with JSON in and JSON out; `dsh` is a persistent
newline-delimited JSON-RPC session over stdio. That difference is the whole
content of the new module.

Rejected alternative: embedding the `dsh web` UI in a tab. It would put a
second application shell, a second visual system, and a second navigation model
inside the app 17A exists to make coherent. The agent page stays itembank's own
surface; `dsh` supplies the engine behind it.

## The boundary that does not move

`dsh` drafts, proposes, and shows a diff. `journal.commit_operation` is what
makes a change real. Its session log is, from itembank's side, derived and
disposable; the operation journal and the evidence store remain the only
durable authorities. This is the same rule that forbids a second scorer, applied
to a second writer.

## Risks, recorded now so they are not rediscovered

1. **Developer preview, breaking changes promised.** The README says so in
   bold, and `AGENTS.md` says `SESSION_FORMAT_VERSION` is `0` "with no
   compatibility promise". **Pin an exact version** of
   `deepseek-harness-sdk` and treat an upgrade as a deliberate, tested change.
2. **Node.js becomes a dependency.** Permitted since the 2026-08-09 constraint
   relaxation, but it is a real install cost for Phase 18. Mitigated by
   `deepseek-harness-runtime-bin`, which ships bundled runtime binaries, so the
   learner may not need a separate Node install. **Unverified.**
3. **A local provider adapter is not confirmed to ship.** `packages/llm/`
   contains `llm-deepseek` and `llm-pi-ai`. The `LlmRuntime` API is explicitly
   provider-neutral and exposes `registerAdapter` and `discoverModels`, so an
   OpenAI-compatible or Ollama route is clearly within the plugin model. Whether
   one ships today was **not** confirmed. If it does not, itembank's own
   `openai_compatible` transport still reaches Ollama directly and loses only
   the agent loop.

## What this does not change

Claude and Codex still get no console inside itembank; their harnesses are
Claude Code and the Codex CLI. Interestingly `dsh` ships
`packages/hooks/` with "Claude Code/Codex hook bridges", so that path exists
if it is ever wanted. Not now.

## Not verified

`dsh` was not installed or run. Every claim above comes from the GitHub API and
from `README.md`, `docs/architecture.md`, `AGENTS.md`, `python/README.md`, and
`packages/llm/llm/README.md` read on 2026-08-21. Task 2 should begin by running
`npx @deepseek-ai/dsh web` once and confirming it starts before any code is
written against it.

---

## Revision, 2026-08-21: embed the web UI. The earlier rejection was wrong.

Weibao pushed back on "do not embed" and was right on the facts. `dsh` was
installed and run rather than read about this time, and the objection did not
survive contact.

### What running it actually showed

| Check | Result |
|---|---|
| `npx @deepseek-ai/dsh --help` | Installs and runs on Node 22 |
| `dsh web --port 3080` | Serves at `http://127.0.0.1:3080` |
| `X-Frame-Options` | **absent** |
| `Content-Security-Policy` | **absent** |
| `frame-ancestors` | **absent** |
| iframe from a `file://` host page | Loads. `contentWindow` reachable, zero console errors |
| Model in the running UI | **`qwen3.8-27b:latest`**, profile `weibao-planing` |

The last row closes risk 3 from the original record. It is not a question of
whether `dsh` reaches an open local model: it is doing so on this machine right
now, against the model named in `Modelfile.exec`.

The installed build also carries `--trusted-host <authority...>`, described as
"extra authority the `/api` browser-trust fence accepts". A plain iframe does
not need it, since the framed document's own requests are same-origin inside
the frame. It exists for the case where an itembank page on another port calls
`/api` directly, which is a supported path rather than a workaround.

Note the installed build has **no** `--no-open` flag despite the README naming
one. The README documents `main`; the published package differs. That is the
developer-preview risk showing up on the first day of contact, and it is an
argument for pinning, not against adopting.

### The revised shape: embed the surface, keep the subprocess seam

Both, not one. This is the standing rule in `PLANNING-DIRECTIVES.md` section 1
applied to an implementation choice.

- **Agent tab: the embedded `dsh` web UI.** The whole console, its tool rows,
  its approval flow, its session view, maintained by someone else. Weibao's
  argument stands: rebuilding a worse version of a clean interface does not
  serve coherence, it just costs months.
- **Programmatic seam: the Python SDK over stdio.** Kept for operations
  itembank drives itself from other screens, where a UI is the wrong shape:
  running `author-bank` from the Build area, and writing the accepted result
  through `journal.commit_operation`.

### What the earlier objection was actually worth

The original record said embedding "would put a second application shell, a
second visual system, and a second navigation model inside the app 17A exists
to make coherent." That was stated as a blocker and it is not one. It is a real
but ordinary cost, of the same kind as embedding any mature tool, and it is
paid back by not maintaining an agent console.

Two concrete pieces of it survive as work rather than as objection:

1. **Locale.** The served document is `<html lang="zh-CN">`. A learner-facing
   embed needs the locale set explicitly rather than inherited.
2. **Theme seam.** `dsh` renders its own palette. The 17A accent
   (`indigo` `#4a4ad4`) does not reach inside a cross-origin frame. Either the
   tab visibly hands off to a different-looking tool, which is honest, or a
   later plan explores whether `dsh` exposes theming through its plugin
   config. Not investigated.

### Unchanged

The authority boundary does not move an inch. `dsh` may draft, run tools, and
show a diff inside its own surface. `journal.commit_operation` is still what
makes a change real in itembank, and the evidence store and the one scorer are
untouched by any of this.
