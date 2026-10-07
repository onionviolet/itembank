@../AGENTS.md

<!-- GSD:project-start source:PROJECT.md -->

<!-- CONTEXT BUDGET, a standing rule for this file.
     Loaded in full on every session and subagent, on top of the imported
     AGENTS.md (~9 KB). Keep only Claude-side context that AGENTS.md lacks;
     rules, object model, artifact workflow and prose style live there, with
     full text in docs/AGENT-REFERENCE.md. Target under 8 KB here.
     `gsd-tools generate-claude-md` re-inlines .planning/PROJECT.md and
     .planning/codebase/*.md into the marker blocks below; if you regenerate,
     re-apply this trim. -->

## Project

**Product North Star:** learner-owned sources become an inspectable,
high-quality, AI-operable course whose readings, lessons, practice, tests and
next actions are aligned to cited objectives and improved by honest evidence.
One learner, Weibao (EMT, Math 1400, CSCI 1100), with AI tutors as clients of
the same runtime a human uses.

**Runtime invariant:** one runtime, one scorer, one evidence store; the
runtime, not the model, settles scoring, disclosure and evidence. A tutoring
client sees only the public item and explanation content released for the
current mode and tier. This is a safety boundary, not a capability ceiling:
new scoring behavior extends the one scorer additively.

Beyond AGENTS.md rules 1 to 15, two more bind:

- Format changes are additive. A bank without a `LESSON` section parses as
  today. Deprecation is allowed through an explicit `migrate`; only silent
  breakage is forbidden.
- The accessibility gates in `.planning/UI-SPEC.md` hold.

Python-stdlib-only, no build step and offline-first are **preferences**
(relaxed 2026-08-09). Dependencies and non-Python components are fine when
they earn their cost; a packaged desktop app is an end goal. The core loop
must still degrade, never block, with the network unplugged.

### Reading before consequential work (read sections, not whole files)

| Need | Read |
|---|---|
| Binding next-milestone scope | `.planning/SOURCE-TO-COURSE.md`, relevant sections; fully for contract changes |
| Shared agent operating contract | `.planning/AGENT-WORKFLOW.md` authority map and task-scoped reading mode |
| Object, authority, rights, acceptance, recovery | `docs/AGENT-REFERENCE.md` §"Object and authority model" |
| Weibao's verbatim goal | `.planning/USER-VISION.md` (85KB). Grep it; never replace it with a summary. |
| Full authority synthesis | `.planning/research/phase-16/14-synthesis.md` §2, §3, §6, §10 |
| Current phase and state | `.planning/STATE.md`, "Current position" only |
| Roadmap | `.planning/ROADMAP.md` "Phases" checklist and subphase Status column; one phase's detail only when planning it |
| Idea dispositions / requirement wording | Grep `.planning/IDEA-LEDGER.md` / `.planning/REQUIREMENTS.md` by ID (checkboxes are not status) |
| How a past decision was reached | `.planning/archive/` (index in its README); never for current status |
| Stack, conventions, architecture detail | `.planning/codebase/*.md` |

### Accepted risks, recorded so they are not rediscovered

- **Hosted models see item text** (2026-08-05). EMT and CSCI 1100 items transit
  to a hosted provider. This accepts provider transit only; it is not
  permission to process coursework a course prohibits (the CSCI 1100 AI-use
  ban applies hosted or local).
- **The `update_policy` divergence is deliberate** (D-13). Schema default
  `opt_in`; this repo's `itembank.json` sets `check_on_launch` to dogfood the
  updater.
- **External installations are a supported goal** (Phase 18). No accounts and
  no multi-tenancy still bind.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

Python 3.11+, standard library only as built (no install step, build system
or lockfile). Vendored exceptions: KaTeX for Math and stdlib `urllib` for the
opt-in updater. CI pins optional LTI deps (`cryptography`, `PyJWT`) that the
core loop must never import. This is the stack as built, not a constraint.
Optional integrations: AnkiConnect (`ANKI_CONNECT_URL`), git for `day`.
Entry: `python itembank.py [COMMAND]` or `import itembank` (`__all__`). Detail:
`.planning/codebase/STACK.md`, `INTEGRATIONS.md`, `TESTING.md`.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Match the surrounding code. No linter or formatter; 4 spaces, `%`-style
string formatting.

- snake_case; UPPERCASE constants; command handlers `cmd_<name>(args)`.
- No private underscore functions; `__all__` only in `itembank.py`. Direct
  imports, no `import *`, barrels or path aliases.
- CLI errors use `sys.exit("message")`. Validation accumulates
  `(errors, warnings)` of `"Qn: message"`. `None` = unknown/unmarked,
  `False` = wrong, `""` = missing.
- Docstrings explain why and what, often the protected invariant.
- Separators: `FIELD_SEP = "\x1f"`, `PAIR_SEP = "\x1e"` (content contains `|`, `>`, `,`).
- Item families and grammar: read `python itembank.py spec`, not a cached list.

Detail: `.planning/codebase/CONVENTIONS.md`.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:codebase/ARCHITECTURE.md -->
## Architecture

Layers are in AGENTS.md. Key abstractions: `public_item()` is what a learner
sees before answering (no key); `explain_payload()` after; `canonical_response()`
reduces any response to one comparable string so the offline page and scorer
agree; sessions are JSON in `_attempts/session_*.json`.

Constraints: every verdict goes through `runtime.score_response()`; every
load through `model.load()`; no circular imports, global state or module
caches; session writes are atomic (`.tmp` then `os.replace`); no database.
Anti-patterns that have bitten this repo: scoring in two places, parsing a
bank twice per invocation, leaking keys before the answer, long operations
with no progress output. Detail: `.planning/codebase/ARCHITECTURE.md`.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

`.claude/skills/` and `.agents/skills/` are byte-identical CI-enforced
mirrors sharing `OPERATION-CONTRACT.md`. Shipped: `absorb-book`,
`author-bank`, `build-course`, `curriculum-design`, `guiding-questions`,
`legacy-upgrade`, `ocr`, `problem-intake`, `user-vision`. Guided
`discovery-and-binding`, `lesson-authoring` and `media-intake` are not yet
runnable; their skills document bounded manual use.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Use GSD when it earns its tokens (real phase work, multi-step execution). For
small doc edits and ad-hoc changes, edit directly and commit with plain `git`.
Entry points: `/gsd-quick`, `/gsd-debug`, `/gsd-execute-phase`.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
<!-- GSD:profile-end -->
