---
phase: 17A-visual-system-component-foundation
plan: 06
type: execute
wave: 3
depends_on: ["17A-01", "17A-02"]
files_modified:
  - model_adapter.py
  - itembank.json
  - surfaces/visual_fixture.py
  - surfaces/daemon.py
  - tests/local_harness_roundtrip.py
  - .planning/phases/17A-visual-system-component-foundation/17A-06-DECISIONS.md
autonomous: false
requirements: [AGENT-01, VISUAL-01]
must_haves:
  truths:
    - "A local model is reachable through the shipped openai_compatible transport with a settings entry and no new transport code."
    - "A dsh_stdio transport is a new module plus a registry entry, with zero edits to tier-gate, evidence, or prompt-assembly code (D-27)."
    - "The Agent page runs one skill against the active local profile and writes exactly one journal entry through journal.commit_operation."
    - "Claude and Codex are named as externally harnessed and get no duplicate console inside itembank."
    - "The Agent tab embeds the dsh web UI; itembank builds no agent console of its own."
    - "The embedded frame sets an explicit lang rather than inheriting zh-CN."
    - "Every unavailable state is typed and names the next safe action; a stopped model never blocks studying, scoring, or authored hints."
  artifacts:
    - "tests/local_harness_roundtrip.py covers profile resolution, a stubbed endpoint, timeout, refusal, and the journal write."
    - "17A-06-DECISIONS.md records the adopt-or-build verdict for the external harness with its licence and its egress claim."
  key_links:
    - "The page reaches a model only through model_adapter.invoke, never through its own HTTP call."
    - "The journal write goes through journal.commit_operation, never through a second writer."
---

<objective>
Give the local model the harness it does not have, at the smallest size that is
honest. Claude and Codex already have harnesses that are better than anything
this repo would build, so this plan deliberately does not build a third one for
them.
</objective>

<context>
@.planning/EXEC-CONTEXT.md
@.planning/phases/17A-visual-system-component-foundation/17A-DIRECTION.md
@model_adapter.py
@journal.py
</context>

<findings>
Measured on 2026-08-20 before this plan was written, so the plan is sized
against what exists rather than against what was assumed.

1. **The local transport already ships.** `model_adapter.TRANSPORT_REGISTRY`
   carries `hosted_cli` and `openai_compatible`, and
   `_transport_openai_compatible` already tags its result `"local"`. Ollama and
   llama.cpp both serve an OpenAI-compatible endpoint, which is what that
   transport speaks.

2. **A local model therefore costs a settings entry, not a module.** This exact
   profile resolves and invokes today:

       {"name": "local-qwen", "transport": "openai_compatible",
        "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
        "timeout_seconds": 30}

   It returns a typed `unavailable` when nothing is listening, which is the
   designed degraded behavior and not a failure.

3. **The field is `endpoint`, not `base_url`.** A profile using `base_url`
   fails resolution with `settings.invalid_value`. This is the single most
   likely setup mistake and the page must say so in words.

4. **The journal is ready.** `journal.commit_operation` does compare-and-swap
   with an operation log and a prior revision, so an accepted change is
   undoable without this plan inventing anything.

5. **There is no harness in the tree.** `Modelfile.exec` names an Ollama model
   and `scripts/preflight.py` is a CI-gate mirror. Neither is an agent console.
</findings>

<tasks>
<task type="auto" status="resolved">
  <name>Task 1: adopt the external harness, or build the page (RESOLVED 2026-08-21)</name>
  <files>.planning/phases/17A-visual-system-component-foundation/17A-06-DECISIONS.md</files>
  <action>
Weibao proposed reusing an existing, actively developed DeepSeek harness rather
than building one. Resolve which, and record it. The decision needs four
answers and no more: which project (name and repository), its licence, whether
it is embedded in the app or launched beside it, and what it sends where.

The adopt branch is genuinely cheaper and should win unless one of these is
true: the harness holds its own conversation state that would compete with the
operation journal; it writes files without a compare-and-swap and an undo; or
its licence does not permit the packaged desktop app in Phase 18.

If adopted, itembank still owns acceptance. The harness may draft and show a
diff; `journal.commit_operation` is what makes a change real. That boundary is
not negotiable and is the whole reason this is a checkpoint rather than an
auto task.
  </action>
  <resolution>
ADOPT deepseek-ai/deepseek-harness (MIT, TypeScript, 180,182 stars, pushed
2026-08-21, not archived; all four verified against the GitHub API). Drive it
as a subprocess through its Python SDK over newline-delimited JSON-RPC on
stdio, not as an embedded web UI. Full record and risks in 17A-06-DECISIONS.md.
  </resolution>
  <verify>17A-06-DECISIONS.md names the project, licence, integration shape, and egress. Done.</verify>
</task>

<task type="auto">
  <name>Task 2: a working local profile, shipped in the repo's own settings</name>
  <files>itembank.json, tests/local_harness_roundtrip.py</files>
  <action>
Running it is DONE (2026-08-21): it installs on Node 22, serves at
127.0.0.1:3080, sets no framing headers, frames cleanly, and is already driving
qwen3.8-27b:latest. Pin the package version before writing code against it,
because the published build already differs from the README (no --no-open).

Then, unchanged from the original scope:

Add a `local-qwen` profile to `model_backend.profiles` using `endpoint`, and
leave `model_backend.active` empty so a fresh install still reaches no model
until asked. Write the test first: profile resolution succeeds; a stubbed
endpoint returns a well-formed result; a refused connection, a timeout, and a
non-JSON body each produce a typed unavailable rather than an exception; and a
profile written with `base_url` fails with `settings.invalid_value` so the
likeliest setup mistake stays covered.
  </action>
  <verify>python tests/local_harness_roundtrip.py exits 0 with no network available.</verify>
</task>

<task type="auto">
  <name>Task 3: the Agent page reaches a real model and writes one journal entry</name>
  <files>surfaces/visual_fixture.py, surfaces/daemon.py, tests/local_harness_roundtrip.py</files>
  <action>
Replace the fixture skill buttons with one working path: choose a skill, run it
against the active profile through `model_adapter.invoke`, show the draft as a
bounded diff, and on accept call `journal.commit_operation` exactly once. The
page makes no HTTP call of its own and holds no second writer.

Hosted profiles stay listed with their real egress line. Claude and Codex are
labelled as externally harnessed, with a sentence saying their console is
Claude Code and the Codex CLI, so the absence reads as a decision rather than a
gap.

Every failure the adapter can return gets a named next action: no active
profile, endpoint refused, timed out, malformed response, transport unknown.
`report_only` autonomy must visibly disable accept rather than hide it.
  </action>
  <verify>python tests/local_harness_roundtrip.py, python tests/visual_system_roundtrip.py, python tests/journal_roundtrip.py, and python itembank.py guard . all exit 0.</verify>
</task>
</tasks>

<out_of_scope>
No second harness for Claude or Codex. No conversation history store. No
scoring, marking, or key disclosure from this page, ever. No token freeze and
no change to `theme.DEFAULT_ACCENT`, which belongs to 17A-04.
</out_of_scope>

<summary_obligations>
Record the adopt-or-build verdict, the exact working profile, the five
unavailable states and their copy, the single journal entry a run produces, and
the undo path.
</summary_obligations>
