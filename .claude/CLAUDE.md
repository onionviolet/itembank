<!-- GSD:project-start source:PROJECT.md -->

<!-- CONTEXT BUDGET, a standing rule for this file.
     This file is loaded in full on every session and in every subagent, so
     its size is charged unconditionally. It was 37.9KB (~9.5k tokens per
     session, per subagent) until 2026-08-29 and is now held near 16KB by
     keeping rules that bind and pointers to detail, never inlined reference
     material rediscoverable from the code or from .planning/. If it passes
     ~18KB, something reference-shaped has crept back in.
     `gsd-tools generate-claude-md` will re-inline the full text of
     .planning/PROJECT.md and .planning/codebase/*.md into the marker blocks
     below and undo that. If you regenerate, re-apply this trim. -->

## Project

**itembank** is a source-to-course learning workspace built on a local-first
assessment protocol and runtime. It ships today: a markdown format contract
with an actionable linter, seven item types, deterministic scoring behind one
scorer, resumable JSON sessions, an offline HTML quiz, a graded loopback
sitting, Anki TSV export, and a cross-subject `day` cockpit.

The next milestone turns learner-owned books, syllabi, exam blueprints, notes,
existing banks, and folders into a coherent course: discover and bind sources,
build a cited objective and prerequisite map, choose the right treatment per
objective (including direct source reading), create missing artifacts, provide
guided teaching and practice where useful, and revise the path from recorded
evidence. A capable model is a first-class course builder, analyst, and
optional teaching collaborator, not the sole teaching surface.

One learner, Weibao, across EMT, Math 1400, and CSCI 1100, with AI tutors as
first-class clients of the same runtime a human uses.

**Product North Star:** **Learner-owned sources become an inspectable,
high-quality, AI-operable course whose readings, lessons, practice, tests, and
next actions are aligned to cited objectives and improved by honest evidence.**

**Runtime invariant:** **One runtime, one scorer, one evidence store, and the
runtime, not the model, settles scoring, assessment disclosure, and evidence.**

The tutoring model reads the item, the key, the rationale, and the learner's
specific wrong answer, so it can teach about *this* error. What it may not do
is choose how much to say: the runtime gates disclosure by session mode and
hint tier, so a model argued into wanting to reveal still cannot.

This is a small safety boundary, not a capability ceiling. AI may search
approved roots, design curricula, select readings, draft and revise artifacts,
interpret metrics, propose remediation, and perform approved bounded writes.
New scoring behavior (partial credit, semantic short-answer matching,
AI-proposed marks, new item types) belongs *inside* the one scorer as an
additive extension; advisory graders may propose a mark but never settle one.
A feature is wrong only if it needs a second, competing authority.

### The five non-negotiables

1. The runtime owns correctness, session state, evidence, and keyed
   assessment disclosure.
2. Exactly one parser, one scorer, one evidence store.
3. Evidence and banks stay on disk. No telemetry, no vendor-held data.
   Learner-initiated export, backup, and device sync are legitimate features
   gated by the export and share rights grants.
4. Format changes are additive. A bank without a `LESSON` section must parse
   as it does today. Additive does not mean permanent: an element may be
   deprecated with documentation and retired through an explicit `migrate`
   operation. Only *silent* breakage is forbidden.
5. The accessibility gates in `.planning/UI-SPEC.md` hold.

Everything else once listed as a constraint (Python-stdlib-only, no build
step, Python-only, offline-first) is a **preference**, relaxed 2026-08-09 by
Weibao. Dependencies, bundlers, npm, and non-Python components are permitted
when they earn their cost. A packaged desktop app is an end goal. Judge ideas
on product merit and report real cost. The core loop must still **degrade,
never block**: sitting a quiz, scoring, lessons, the authored hint ladder,
evidence, and reports all work with the network unplugged.

### Prose style rule

Do not use em dash characters in repository-authored prose, documentation,
comments, fixtures, generated lessons, or questions. Use commas, parentheses,
colons, semicolons, or separate sentences instead. Verbatim source quotations
and additive statements in `.planning/USER-VISION.md` are the only exceptions.

### Reading before consequential work (read sections, not whole files)

These files are large. Read the section you need, not the file.

| Need | Read |
|---|---|
| Binding next-milestone scope | `.planning/SOURCE-TO-COURSE.md` (17KB, read whole) |
| Shared agent operating contract | `.planning/AGENT-WORKFLOW.md` (10KB, read whole) |
| Object, authority, rights, acceptance, recovery detail | `AGENTS.md` §"Object and authority model" |
| Weibao's verbatim goal | `.planning/USER-VISION.md` (85KB). Grep it. Never replace the record with an interpreted summary. |
| Full authority synthesis | `.planning/research/phase-16/14-synthesis.md` §2, §3, §6, §10 (84KB total) |
| Current phase and state | `.planning/STATE.md` (93KB). Read the current phase's section only. |
| Roadmap | `.planning/ROADMAP.md` (115KB). Read the current and next phase only. |
| Idea dispositions | `.planning/IDEA-LEDGER.md` (82KB). Grep by ID. |
| Stack, conventions, architecture detail | `.planning/codebase/*.md` |

### Object, authority, and operation summary

Full text: `AGENTS.md` §"Object and authority model", which is the mirror of
record. The rules that gate every change:

- **Authority.** The learner owns goals, private notes, scratch work, strategy
  choice, and evidence export. A course builder defines scope, treatments, and
  paths within source and rights limits. A reviewer accepts or rejects. An
  agent discovers, aligns, drafts, validates, and explains within an operation
  manifest, and never owns accepted truth or assessment authority. The runtime
  is the sole authority for session state, keyed disclosure, scoring, and
  attempt evidence.
- **Durable versus derived.** Accepted files are canonical. Indexes, HTML,
  caches, rankings, and progress views are derived and disposable, and never
  become the only understandable copy.
- **Separate state axes.** Accepted content, workflow state, epistemic
  confidence, validation state, rights state, and availability are
  independent. Do not collapse them.
- **Compare-and-swap mutation.** Every durable write states an expected base
  fingerprint, writes to a temporary file, validates, commits atomically, and
  journals the operation, so any fault leaves the old or new valid state.
  Link, import, copy, move, edit-in-place, supersede, migrate, and synchronize
  are distinct operations, not synonyms. Same ID with divergent bytes is a
  conflict, never a silent overwrite.
- **Rights and egress are per operation.** Read, quote, transform,
  remote-process, package, export, and share are separate grants. Unknown
  rights stay restrictive. Hosted operations minimize and disclose egress.
- **Learner notes** never silently become source truth, lesson truth, answer
  keys, scores, or mastery. Presentation state never grants authorization.
- **Accessibility** review (keyboard, touch, screen reader, zoom and reflow,
  high contrast, reduced motion) covers representative outputs: sampled per
  template or capability profile, full when a template or interaction pattern
  changes. An agent never self-certifies.
- **Clean recovery.** Export is not complete until a clean-machine, offline
  restore validates a manifest and reports every loss. Interrupted, offline,
  denied, future-schema, and agent-unavailable states preserve the last
  accepted state and expose the next safe action.
- **Append-only ledger.** Every viable idea keeps a disposition (core,
  registered, prototype, backburner, deferred). Untimely is not rejected, and
  simplicity alone is not a rejection reason. Rejections record evidence,
  reason, conflicting rule, retained alternative, date, and reconsideration
  condition, and are never deleted. Append-only forbids deleting records, not
  archiving or compacting completed-milestone ledgers into summaries that
  point at the full record.
- **One operation protocol.** Declare intent and declare approved roots,
  rights, egress, write, and execute authority; inventory before creating;
  plan treatment; checkpoint; draft the smallest missing artifact; cite and
  label synthesis; validate deterministically; show an accessible plain and
  rich preview; present a bounded diff; pass configured review; accept
  atomically; update dependency and staleness state; report undo and
  uncertainty. Backend choice changes cost, latency, and disclosure, not the
  artifact or authority contract.

### Course artifact workflow

Full text: `AGENTS.md` §"Course artifact workflow". Before creating a lesson,
question set, bank, activity, or exam, in order:

1. **Inventory** sources and artifacts across every user-approved root (course
   folders, source folders, an Obsidian vault) with location, stable identity,
   fingerprint, ownership, provenance, objective links, draft or accepted
   state, and validation status. Discovery is read-only and authorizes no
   mutation.
2. **Reconcile** duplicates, moved files, stale links, and conflicting
   versions. Never identify or merge artifacts from filenames alone.
3. **Map** the cited objectives and prerequisites, and choose the treatment
   per objective (direct reading included) before generating anything.
4. **Reuse or link** an adequate existing artifact. Linking, importing,
   copying, moving, and superseding are distinct; provenance is preserved.
5. **Create** only genuinely missing treatments, through the relevant skill
   and the format contract. Label synthesis and retain citations.
6. **Verify** lessons in both forms: the durable authored document (coherent
   in plain Markdown or Obsidian) and the richer itembank presentation.
7. **Audit before editing** legacy material. Preserve stable identity and
   history, retain static and accessibility fallbacks, present a bounded diff.
   Never silently change keyed content, assessment meaning, difficulty, or
   objective alignment.
8. **Reindex and report** disposable discovery data, validated links, changes,
   uncertainties, and reversal steps.

Agent skills are part of the product interface and must work as portable
playbooks for Claude, Codex, and other clients against the same runtime and
artifact contracts.

### Accepted risks, recorded so they are not rediscovered

- **Hosted models see item text** (Weibao, 2026-08-05). AAOS-12e-derivative
  EMT items and CSCI 1100 items transit to a hosted provider. Hosted or local,
  this is AI assistance on graded coursework and the CSCI 1100 AI-use ban
  applies to both. The local-only path stays fully built, so any subject moves
  back behind it by changing one setting.
- **The `update_policy` divergence is deliberate** (D-13, 2026-08-08). The
  schema default is `opt_in` so a fresh install never phones home unasked;
  this repository's own `itembank.json` sets `check_on_launch` so the updater
  is dogfooded. The two values are meant to differ.
- **External installations are now a supported goal** (2026-08-14), scoped as
  Phase 18. The original "one learner, no design work spent on others" wording
  is superseded; no-accounts and no-multi-tenancy still bind.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

Python 3.11+, standard library only as built today (`json`, `re`, `os`, `sys`,
`collections`, `argparse`, `html`, `http.server`, `socketserver`, `random`).
No install step, no build system, no lockfile, no `requirements.txt`. Two
vendored exceptions: a KaTeX asset for Math rendering and stdlib `urllib` for
the opt-in updater. CI pins two optional LTI deps (`cryptography`, `PyJWT`)
that the core loop must never import.

This describes the stack **as built**, not a forward constraint. See the five
non-negotiables above. Optional integrations: Anki Desktop via AnkiConnect
(`ANKI_CONNECT_URL`), git for `day`'s status line.

Entry points: `python itembank.py [COMMAND]`, or `import itembank` for the
public API in `__all__`. Single-threaded, stateless, no daemon, no database.

Detail: `.planning/codebase/STACK.md`, `INTEGRATIONS.md`, `TESTING.md`.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Match the surrounding code. No linter or formatter is configured; formatting
is manual, 4 spaces, `%`-style string formatting throughout.

- snake_case modules, functions, and variables. UPPERCASE module constants.
- Command handlers use a `cmd_` prefix (`cmd_lint`, `cmd_serve`) and take an
  argparse `Namespace`.
- Tests are `tests/*_roundtrip.py` (plus `*_check.py`, `*_tracer.py`, audits).
  CI runs every `tests/*.py`.
- No private underscore-prefixed functions; everything module-level is
  importable. `__all__` exists only in `itembank.py`.
- Direct imports, never `import *`, no barrel files, no path aliases.
- CLI errors use `sys.exit("message")`. Validation accumulates into
  `(errors, warnings)` lists of `"Qn: message"` strings. `None` means unknown
  or not-yet-marked, `False` means wrong, `""` means missing data.
- Docstrings explain WHY and WHAT, not HOW, and often restate the invariant
  the function protects. Comments are complete sentences.
- Canonical form separators are `FIELD_SEP = "\x1f"` and `PAIR_SEP = "\x1e"`,
  chosen because item content contains `|`, `>`, and `,`.
- Item types: `mc`, `multi`, `table`, `dnd`, `build`, `short`.

Detail: `.planning/codebase/CONVENTIONS.md`.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:codebase/ARCHITECTURE.md -->
## Architecture

Four layers. The boundaries are the design.

| Layer | Responsibility | Files |
|---|---|---|
| Model | Format contract, parsing, validation | `model.py` |
| Runtime | The only scorer; sessions; public/private payload visibility | `runtime.py` |
| Server | Loopback HTTP handler and port fallback | `server.py` |
| Surfaces | Rendering and interaction, all of them clients | `surfaces/*.py` |
| Entry | Command routing | `itembank.py`, `surfaces/cli.py` |

Key abstractions: `public_item()` is what a learner sees before answering (no
key); `explain_payload()` is what they see after; `canonical_response()`
reduces any response to a comparable string so the offline page and the
scorer cannot disagree about what a response *is*; sessions are JSON in
`_attempts/session_*.json` holding item indices, a cursor, and responses.

Architectural constraints, all enforced by the layering:

- Every surface reaches a verdict through `runtime.score_response()`. No
  surface reimplements grading.
- Every surface loads banks through `model.load()`. Nothing else parses.
- No circular imports, no global state, no module-level caches.
- Session writes are atomic (`.tmp` then `os.replace`), so a session is safe
  to read while being written.
- No database. Markdown and JSON on disk.

Anti-patterns, each of which has bitten this repo: scoring in more than one
place, parsing the bank more than once per invocation, leaking answer keys to
the browser before the learner answers, and long operations with no progress
output.

Detail: `.planning/codebase/ARCHITECTURE.md`, `STRUCTURE.md`, `CONCERNS.md`.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

`.claude/skills/` and `.agents/skills/` are byte-identical mirrors, enforced
by CI (`diff -rq`), and share `OPERATION-CONTRACT.md`. Shipped: `absorb-book`,
`author-bank`, `build-course`, `curriculum-design`, `guiding-questions`,
`legacy-upgrade`, `ocr`. Stubs whose command surface has not shipped:
`discovery-and-binding`, `lesson-authoring`, `media-intake`.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Treat GSD as guidance and structure, not mandatory ceremony. Use it when it
earns its tokens: real phase work, multi-step execution, or anything where the
planner/executor/verifier structure genuinely improves the outcome. For small
doc edits and ad-hoc changes, edit files directly and commit with plain `git`;
loading the full framework or the `gsd-sdk` wrapper for one-line changes wastes
tokens.

Entry points, when the structure pays for itself:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
