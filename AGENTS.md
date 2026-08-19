# AGENTS.md - itembank for AI coding agents

This file is the universal on-ramp for AI coding agents (OpenAI Codex, Claude
Code, Cursor, Gemini CLI, and anything else that reads `AGENTS.md`). Read this
first, then the files it points at. Claude Code should also load
`.claude/CLAUDE.md`, which carries the full GSD project context.

## What this repo is

`itembank` is becoming a source-to-course learning workspace. It turns books,
syllabi, exam blueprints, notes, existing banks, and other learner-owned files
into an objective map and a tangible course: direct readings where the source
is best, guided lessons where synthesis helps, key terms and notes, worked
examples, interactive explanations, practice, and formal tests. Evidence then
informs the next activity and future course revisions.

The shipped foundation is a local-first assessment protocol and runtime.
Question banks are plain markdown; the tool validates them, renders lessons and
offline quizzes, runs graded sittings, records evidence, audits source coverage,
and exposes deterministic JSON sessions. A hosted coding-agent client or a
registered local model may drive discovery, course design, authoring, analysis,
and remediation, but accepted artifacts remain inspectable files and
deterministic scoring remains in the runtime.

The useful artifact is the **contract**: `itembank spec` prints the format,
`itembank lint` tells an author exactly what it got wrong, by item number, in
language it can act on. Authoring becomes write, check, fix.

The binding next-milestone product contract is
`.planning/SOURCE-TO-COURSE.md`. Read it before planning course, source, agent,
authoring, metrics, or learner-UI work. The course is the user-facing unit;
objectives are its spine; a bank is one assessment artifact inside it.
`.planning/USER-VISION.md` preserves the user's goal verbatim. Never overwrite
it with a summary; append new dated statements and keep interpretations in the
product contract and plans.

The binding cross-agent workflow is `.planning/AGENT-WORKFLOW.md`. Read it
before consequential course, source, lesson, assessment, UI, research,
migration, or product-direction work. It defines vision capture, ideaboarding,
research waves, synthesis, dispositions, authority checks, safe operations,
readiness audits, and handoffs for Codex, Claude Code/Cowork, local agents, and
other clients.

## The four layers (boundaries are the design)

```
model.py                  what a bank is, and what makes one invalid (one parser)
runtime.py                the only scorer; decides what a surface may see
server.py                 one loopback HTTP server
surfaces/                 clients only: quiz, study, day, session, CLI, export
```

Non-negotiable rules:

1. **One parser, one scorer.** Never parse a bank a second way and never decide
   correctness outside `runtime.py`. A future MCP/function-calling adapter must
   wrap the JSON commands, not reimplement them. Clarified 2026-08-15
   (IDEA-LEDGER IL-20260815-05): this names one scoring authority, not a frozen
   capability set. New scoring behavior extends `score_response` additively,
   and advisory graders, human or model, may propose a mark but never settle
   one. A feature is wrong only if it needs a second, parallel authority whose
   verdicts compete with the runtime's.
2. **The runtime owns assessment authority.** Correctness, session state,
   evidence recording, and disclosure of keyed assessment content belong to
   the runtime. An agent may build and teach the course, but it may not invent
   a score, bypass the active feedback mode, or reveal keyed content early.
3. **Never auto-grade prose.** A `short` item scores `None` (pending review),
   never `False`. Marking happens later against a rubric, by a human or a
   human-approved model. Clarified 2026-08-15 (IDEA-LEDGER IL-20260815-06):
   a labeled, provisional AI assessment of a short answer is an advisory
   grade and is allowed; only the settled mark waits for review.
4. **Never commit real question banks.** This repository holds code and
   synthetic fixtures only. `itembank guard .` enforces it in CI.
5. **Evidence and banks stay on disk.** No telemetry, no hosted gradebook.
   Clarified 2026-08-15 (IDEA-LEDGER IL-20260815-06): this bans telemetry and
   vendor-held data, not the learner's own copies. Learner-initiated export,
   backup, and device sync are legitimate features gated by the export and
   share rights grants; Phase 18 external installs need this distinction.

For course-building work:

6. **Do not rewrite by default.** Decide per objective whether direct source
   reading, an excerpt, lesson, notes/terms, example, visual, practice, or test
   is the best treatment.
7. **AI is allowed to do useful work.** It may search approved roots, align and
   draft, interpret evidence, propose a path, and perform approved bounded
   writes. It must cite sources, label synthesis, disclose uncertainty and
   denominators, and keep changes reviewable and recoverable.
8. **Match the real target.** Standardized-test courses require a sourced
   blueprint and faithful construct, difficulty, and item-format distribution;
   other knowledge courses follow their actual objectives and cognitive demand.
9. **Find before creating.** Search every user-approved root for existing
   lessons, questions, banks, exams, notes, and source bindings before drafting
   replacements. Roots may be separate and may include an Obsidian vault.
10. **Link deliberately.** Distinguish linking, importing, copying, moving,
    and superseding. Preserve stable identity, provenance, objective links, and
    citations. Never silently merge artifacts because their names look alike.
11. **Enhance progressively.** Authored lesson files must remain coherent and
    useful in plain Markdown readers. The itembank UI may add hover and focus
    definitions, interactive diagrams, demonstrations, adaptive disclosure,
    and other learning controls, but core meaning cannot depend on the richer
    display. Every interactive feature needs a useful static representation
    and an accessible interaction. Clarified 2026-08-15 (IDEA-LEDGER
    IL-20260815-06): the static bar is that the fallback conveys the core
    meaning and remains study-usable, not that it reproduces the interactive
    experience. An inherently interactive treatment is acceptable when its
    static form meets that bar.
12. **Audit before upgrading.** When improving an older lesson, question, or
    exam for new UI capabilities, inspect it first, preserve its identity and
    source history, propose a reviewable diff, and validate it afterward. Do
    not make cosmetic rewrites that add no learning value or silently change
    assessment meaning, keyed content, difficulty, or objective alignment.
13. **Preserve direction.** Keep user quotations separate from interpretations.
    Route every meaningful idea through the vision funnel and trace accepted
    work from vision to evidence, contract, requirement, phase, and verification.
14. **Preserve viable breadth.** Record proposals as core, registered,
    prototype, backburner, deferred, superseded, or rejected. Never silently
    drop an idea. Untimely is not rejected: an optional, expensive, or
    specialized capability stays in the permanent disposition ledger as
    registered, prototype, or backburner with its dependency, cost, and revisit
    trigger. The rejection and supersession ledger is append-only; a superseded
    or hard-rejected idea is never deleted, and every rejection records
    evidence, exact reason, conflicting rule, retained alternative, date, and
    reconsideration condition (synthesis sections 1 and 12). Clarified
    2026-08-15 (IDEA-LEDGER IL-20260815-06): append-only forbids deleting
    records, not organizing them. Completed-milestone ledgers may be archived
    or compacted into summaries that point to the full record, and disposition
    upkeep scales with the stakes of the idea, so the ledger has a maintenance
    path.
15. **Name authority and recovery.** Every operation names its durable object,
    owner, source of truth, rights, remote egress, accepted revision, stale and
    conflict behavior, validation, and recovery. Presentation is not
    authorization, learner notes are not assessment authority, and derived
    views are not canonical truth.

## Object and authority model (summary)

This condenses the Phase 16 synthesis
(`.planning/research/phase-16/14-synthesis.md` sections 2, 3, 6, and 10). The
binding contract is `.planning/SOURCE-TO-COURSE.md`; this summary orients an
agent, it does not replace that file.

- **Actors and authority (synthesis 2.1, 2.3).** The learner owns goals, private
  notes, scratch work, strategy choice, and evidence export. A course builder
  defines scope, treatments, and paths within source and rights limits. A
  reviewer accepts or rejects revisions. A source owner supplies rights and
  authoritative claims. A hosted or local agent discovers, aligns, drafts,
  validates, and explains within an operation manifest, and never owns accepted
  truth or assessment authority. The deterministic runtime is the sole authority
  for assessment session state, keyed disclosure, scoring, and attempt evidence.
- **Durable objects (synthesis 2.2).** Course, scope or framework version,
  concept, objective, source, source binding, artifact, lesson, bank or
  assessment form, activity, learner note, learner artifact, evidence event,
  strategy, agent operation, rights grant, and accepted revision. Each names a
  source of truth. Accepted files are canonical; search indexes, HTML, caches,
  thumbnails, rankings, and progress views are derived and disposable.
- **Separate state axes (synthesis 2.3, 4.1).** Accepted content, workflow state
  (`pending`), epistemic confidence (low), validation state (invalid), rights
  state, and availability are independent axes. Do not collapse them.
  `unavailable`, `unsupported`, `unknown`, `empty`, and `error` each need a
  different recovery action.
- **Core loops (synthesis 3).** The product's end-to-end acceptance surface is
  seven loops: discover/reconcile/bind, design a course, learn and construct
  notes, practice and test, evidence and remediation, author/review/accept, and
  maintain/recover/leave. Each is an acceptance surface, not a single screen.
- **One operation protocol for every client (synthesis 10).** Declare intent;
  declare approved roots, rights, egress, write, and execute authority;
  inventory before creating; plan treatment; checkpoint; draft the smallest
  missing artifact; cite and label synthesis; run deterministic validation; show
  an accessible plain and rich preview; present a bounded diff; pass configured
  review; accept atomically; update dependency and staleness state; report undo
  and uncertainty. Backend choice changes cost, latency, and privacy disclosure,
  never the artifact or authority contract.
- **Mutation is compare-and-swap (synthesis 6).** Every durable write states an
  expected base fingerprint, writes to a temporary file, validates, commits
  atomically, and appends to an operation journal, so any fault leaves the old
  or the new valid state and never a mixed one. Discovery is read-only. Link,
  import, copy, move, edit-in-place, supersede, migrate, and synchronize are
  distinct operations with distinct identity, approval, and recovery effects;
  they are not synonyms. A same-ID, divergent-bytes case is a conflict, never a
  silent overwrite.
- **Rights and egress are declared per operation (synthesis 6, 11).** Read,
  quote, transform, remote-process, package, export, and share are separate
  grants. Unknown rights stay unknown and restrictive. Hosted operations
  minimize and disclose exact egress; evidence and banks stay on disk.
- **Authored-output accessibility (synthesis 11.4).** Representative authored
  outputs pass keyboard, touch, screen-reader, zoom and reflow, high-contrast,
  and reduced-motion review with equivalent tasks. An agent never self-certifies
  accessibility. Clarified 2026-08-15 (IDEA-LEDGER IL-20260815-06):
  "representative" means sampled per template or capability profile, with full
  review when a template or interaction pattern changes; it does not mean human
  review of every generated artifact.
- **Clean recovery (synthesis 3 loop G, 6).** Export is not complete until a
  clean-machine, offline restore validates a manifest and reports every loss.
  Crash, cancel, disk-full, offline, permission-denied, future-schema, and
  agent-unavailable states preserve the last accepted state and expose the next
  safe action.

## Course artifact workflow

Use this sequence for higher-level course work, whether driven manually or by
Codex, Claude Code/Cowork, a local agent, or another compatible client:

1. Read `.planning/USER-VISION.md` and `.planning/SOURCE-TO-COURSE.md`.
2. Establish explicit read roots and write roots. Discovery is read-only by
   default, and finding a file does not authorize changing it.
3. Inventory existing sources and artifacts across all approved roots. Record
   stable identity, fingerprint, location, ownership, provenance, objective
   links, draft or accepted state, and validation status where available.
4. Reconcile likely duplicates, moved files, stale links, and conflicts. Ask
   for review when identity is uncertain; never infer identity from a filename
   alone.
5. Build or update the versioned objective graph and its outline projection,
   record the graph version, and keep structural order separate from
   prerequisite order. Then decide the best treatment for each objective, and
   reuse or link adequate artifacts before proposing new ones. A rename, split,
   merge, or changed-demand objective creates a reviewed migration proposal;
   historical evidence is never transferred automatically.
6. Create only missing artifacts through the relevant skill and deterministic
   contract. Keep generated synthesis and citations visible. Publish each
   accepted change as a recorded revision with its accepted fingerprint,
   reviewer, and validation result, then mark dependent derivatives stale.
7. Keep learner notes and learner artifacts as separate learner-owned records.
   A note, or a learner-built proof, program, diagram, or explanation, may
   ground reflection or a draft and produces descriptive or pending evidence
   until reviewed; it never silently becomes source truth, lesson truth, a key,
   a score, or mastery.
8. Render and verify lessons both as durable source documents and in the rich
   learning UI. Lint and statistically review question banks and exams.
9. For legacy enhancement, audit first, choose learning-value improvements,
   preserve fallbacks and assessment semantics, then present the bounded diff
   for approval.
10. Reindex disposable discovery data, validate links and artifacts, and report
    what changed, what remains uncertain, and how to undo accepted mutations.
    Every durable mutation goes through compare-and-swap with an expected
    fingerprint, atomic write, and operation journal.
11. Before promising an export or package, prove a clean-machine, offline
    restore that validates a manifest and reports every loss. Preserve the last
    accepted state on crash, cancel, disk-full, offline, permission-denied,
    future-schema, and agent-unavailable conditions.

## Prose style

Do not use em dash characters in repository-authored prose, documentation,
comments, fixtures, generated lessons, or questions. Use commas, parentheses,
colons, semicolons, or separate sentences instead. Verbatim source quotations
and the additive user statements in `.planning/USER-VISION.md` are the only
exceptions. Future linting should enforce this rule without rewriting quoted
source material.

## Reading the code (context discipline, a standing rule)

This repository is larger than the context window of most models that work in
it. Whole-file reads are the fastest way to end a session early. The five
largest modules cost roughly 41k tokens (`model.py`), 43k (`surfaces/daemon.py`),
44k (`tests/lesson_roundtrip.py`), 28k (`runtime.py`, `surfaces/lesson.py`), and
26k (`evidence.py`). Several open phase tasks touch four of those at once, so
reading each one whole is not affordable at any context size currently
available locally.

Work symbol-first instead:

1. **Locate before reading.** Search for the symbol (`grep -rn "_render_blocks"`
   or the editor's equivalent) and read a window around each hit, not the file.
   Sixty lines of the right function beats two thousand lines of the right file.
2. **Read whole files only when they are small,** under roughly 400 lines, or
   when the task is genuinely file-shaped, such as a rename across every
   definition in one module.
3. **Prefer the contract to the implementation.** `python itembank.py spec`,
   the schemas, and the roundtrip test names describe behavior in a fraction of
   the tokens the implementation costs.
4. **Let one test name the requirement.** When changing behavior, read the
   failing assertion and its immediate helper, not the whole roundtrip suite.
5. **Say what you did not read.** If a change touches a module you only sampled,
   note it in the summary so a reviewer knows where the blind spot is.

The point is not frugality for its own sake. Everything read early stays in the
window and competes with the reasoning that comes later, so an unnecessary file
read at turn 3 is paid for at turn 40 when the useful context has been
summarized away to make room for it.

## Quick start

```bash
python itembank.py spec                 # the whole format contract
python itembank.py lint bank.md         # validate; exits non-zero on error
python itembank.py build bank.md out.html   # offline quiz (holds the key, saves nothing)
python itembank.py serve bank.md        # graded sitting; every answer written to disk
python itembank.py stats bank.md        # item mix, objective coverage, position skew
python itembank.py study bank.md        # flashcards + Learn loop
python itembank.py day plan.md          # the day cockpit across subjects
```

## The authoring loop (writing a bank)

1. `python itembank.py spec` and follow the contract. Items are `Qn.` blocks
   with `[OBJECTIVE:]`, `[TYPE:]` (mc/multi/table/build/dnd/short/visual),
   `CORRECT:`,
   `WHY BEST:`, `KEY DISCRIMINATOR:`, `DISTRACTOR ANALYSIS:`, `TRAP:`,
   `CONFIDENCE:`. A bank may carry one optional `## LESSON` section of teaching
   text above the first question, with `###` subheadings items link to via
   `[LESSON-REF: heading text]`.
2. `python itembank.py lint bank.md` - fix every `error`; warnings advise.
   Notable checks: every distractor must say when it WOULD be correct;
   answer-position skew is flagged; `CONFIDENCE: low` items must be reviewed.
3. `python itembank.py id-assign bank.md` - the only command that writes into a
   bank; mints opaque ids and content-hash fingerprints.
4. `python itembank.py stats bank.md` - check objective coverage and difficulty
   spread before shipping.

## The tutoring loop (administering a test as an AI tutor)

```bash
python itembank.py start bank.md --count 10 --mode practice --out s.json
python itembank.py next s.json        # returns the item WITHOUT its key
python itembank.py submit s.json --answer '"B"'
python itembank.py report s.json      # objective-level evidence
```

What the runtime guarantees you (an agent):

- `next` returns a `public_item` - stem, options, response schema - never the
  key, rationale, or model text.
- `submit` scores deterministically, records the attempt locally, and returns
  the next item.
- `short` responses are recorded but left `pending` for a marker; you must not
  pretend to have graded them.
- Repeated `submit` calls are idempotent (a `dedupe_key` guards replays).

Your side of the contract (see UI-SPEC.md §9 for the full list):

- You may ask **one diagnostic question** tied to the learner's actual wrong
  answer, and choose among permitted explanation forms (analogy, example,
  counterexample, visualization, derivation, simulation, Socratic question) -
  but only after the runtime has granted the tier for that content.
- You may **not**: reveal the key or higher-tier content, decide the hint tier,
  imply a score, select items, mark prose as accepted, or replace the activity
  with generic chat. Do not retry indefinitely.
- A learner's response may be `submit`-ted multiple times only as the runtime
  allows; you never change the test or the scoring.

## Commit discipline (standing rule)

**One atomic commit per plan.** When executing a GSD plan (or any phase
task), commit exactly once per plan, after that plan's own verification
passes, and only that plan's files. Do not batch two plans into one commit,
do not commit another plan's in-flight work, and do not leave a plan's work
uncommitted in a worktree - a nested worktree under the main checkout can be
removed by a concurrent process, and uncommitted work is then lost. If the
working tree carries another agent's uncommitted edits (this repo is
sometimes executed by concurrent chats), stage only your own plan's files by
name, never `git add -A`. Commit messages follow the repo's
`<type>(<plan>): <summary>` shape, e.g. `feat(10-01): ...` or
`test(10-02): ...`.

## Testing

Every test is stdlib-only and self-contained. There is no pytest dependency:

```bash
python tests/protocol_roundtrip.py     # lint codes, schemas, published contracts
python tests/agent_roundtrip.py        # full JSON session round trip
python tests/serve_roundtrip.py        # served sitting reaches disk, no key leak
python tests/scoring_roundtrip.py      # one scorer, offline key matches it
python tests/lesson_roundtrip.py       # LESSON grammar and reader
python tests/surface_roundtrip.py      # study and Anki export
# ...any tests/*_roundtrip.py - CI runs every tests/*.py (see .github/workflows/ci.yml)
```

CI (`.github/workflows/ci.yml`) additionally asserts `fixtures/sample_bank.md`
lints clean, `fixtures/broken_bank.md` is caught with each named error, the
sample builds, and every session payload validates against `schemas/*.json`
via `schema_validate.py`.

**Before you hand work back, run the gates locally.** `scripts/preflight.py`
mirrors ten of the twelve CI steps in one command, so a change is checked
before the push rather than after it:

```bash
python scripts/preflight.py --quick    # fast gates only (~15 seconds)
python scripts/preflight.py            # adds the Python and JS suites
python scripts/preflight.py --list     # which gate mirrors which CI step
```

Each gate names the CI step it stands in for. Two steps are deliberately not
mirrored and are listed with their reason in `CI_ONLY`; the pinned-LTI install
is setup rather than a gate, and the schema pipeline is a long shell sequence
that a Python copy would only be able to disagree with.
`tests/preflight_roundtrip.py` fails the build when CI gains a step that no
gate claims, so the mirror cannot drift silently.

## Skills

Repo playbooks live in two mirrored trees so every agent finds them:

| Skill | Purpose |
|---|---|
| `build-course` | Orchestrate sources → objectives → treatment → artifacts → evidence |
| `absorb-book` | Analyze a source and create only the treatments it actually needs |
| `curriculum-design` | Build objectives, prerequisites, source alignment, coverage, and assessment blueprint |
| `guiding-questions` | Run a Socratic tutoring session with the JSON protocol |
| `author-bank` | The write → lint → fix loop for new items |
| `ocr` | Read text out of images via a local Ollama vision model (optional; needs the model pulled) |

Where each tool finds the playbooks:

- **Codex, Gemini CLI, Cursor, GitHub Copilot, and other agents.md readers**:
  `.agents/skills/<name>/SKILL.md`, auto-discovered from the repo root.
- **Claude Code**: mirrored at `.claude/skills/<name>/SKILL.md` (project-level).
  Invoke with `/name` or let Claude auto-match the description.
- **Reasonix**: auto-discovers `.agents/skills/` as a convention root - no
  config needed. The optional OCR plugin wiring is personal config, shown
  in `reasonix.toml.example` (the file itself is gitignored).
- **Anything else**: point your tool's skill root at `.agents/skills/`.

The two trees are mirrors of the same playbooks - edit either and copy to
the other; CI runs `diff -rq .agents/skills .claude/skills` and fails on
drift.

## Recording operational findings (a rule for agents working here)

When a session learns something operational that cost it turns or probes - a
tool/permission-gate quirk, a launch recipe, an environment limitation, a
concurrency hazard - **persist it before the session ends** instead of letting
the next session rediscover it from scratch:

1. Save a memory (`remember`) with the concrete behavior and a "how to apply"
   rule.
2. Write the full details to `.reasonix/REASONIX.md` - machine-local and
   gitignored; the canonical home for this machine's runtime notes.
3. Keep machine-specific checkout paths and usernames out of committed docs -
   the CI path-leak step fails agent-facing files that contain them.

Recorded example (2026-08-11): in interactive sessions the command gate
declines `; echo $?` status suffixes, background bash jobs, inline interpreter
code (`python -c`, heredocs, loops), and ad-hoc runner scripts, while bare
commands and simple `&&`-chains run. Full notes: `.reasonix/REASONIX.md` §7.

## Where to look next

- `README.md` - full user documentation (item types, serve vs build, the day
  surface, design boundaries).
- `ROADMAP.md` - the public product contract and sequenced improvement plan.
- `.planning/` - the GSD planning workspace (PROJECT.md, REQUIREMENTS.md, the
  per-phase plans under `.planning/phases/`).
- `.claude/CLAUDE.md` - GSD project context for Claude Code.


<!-- BEGIN PORTABLE AGENT RULES v1 -->
## Working agreement (portable, synced)

*This block is generated. Canonical source: `weibao-planing/_templates/portable_agent_rules.md`. Edit it there and re-run `.claude/scripts/sync_agent_rules.py`, not here. Anything you write outside the BEGIN and END markers is yours and survives a re-sync.*

Applies to every AI agent reading this file, whichever tool loaded it.

### Commits

- Never add a `Co-Authored-By` trailer to a commit message. This overrides the Claude Code harness default, which instructs the opposite.
- Commit or push only when asked. Branch first if the current branch is the default one.

### Communication

- Lead with the answer. Put context after it, and only the context that changes what I do next.
- Do the work first. Then say what you did, whether it worked, and what is left.
- Say what was actually wrong before saying what you did about it.
- Separate what you verified from what you inferred. Never state a guess as a fact.
- Never report a file change, a command, or a commit you did not actually run.
- Correct an error in one sentence, then continue. No apology, no post-mortem.
- Answer every question I asked, each one by name.
- Five items maximum in any list I have to act on. Rank the rest and split it off.

### Prose

- No em dashes, and no ` -- ` standing in for one. Restructure the sentence.
- Banned phrases, no substitutes: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "let me be direct". Say the thing instead of announcing that you are about to.
- No flattery, no enthusiasm you did not feel, no decorative headings, no emoji.
- No hollow adjectives. Replace "robust" with the fact it stands for, or cut it.
- One instruction per sentence. No semicolons, no fragments.
- State each fact once. Do not repeat yourself.

### Reference points

When a reply carries three or more findings, decisions, options, risks, questions, or actions, give each one a short code and keep that code for the rest of the session: `F1` findings, `D1` decisions, `O1` options, `R1` risks, `Q1` questions, `A1` actions. Invent a letter for a category not listed here. No codes on short answers.

### Aliases

When one of these appears as a standalone word in a message, expand it and act as if the expansion had been typed. Inside a longer word or phrase it is not an alias.

- `scr` = simplify and compress your last response, then repeat it.
- `eli` = explain that like I am 18. Simpler words, shorter answer.
- `foc` = what is the real signal here? Cut to the one thing that matters.
- `ref` = rewrite your last response with reference points.

### Scope

- Deliver what was asked at the scope asked. Do not widen the work into cleanup, refactoring, or documentation nobody requested.
- Do not build abstractions for requirements that do not exist yet.
- Never claim something is done without evidence you ran it.
- Restate finished work in one or two sentences. Do not re-narrate every step.

<!-- END PORTABLE AGENT RULES v1 -->
