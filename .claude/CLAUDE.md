<!-- GSD:project-start source:PROJECT.md -->

## Project

**itembank**

`itembank` is a source-to-course learning workspace built on a local-first
assessment protocol and runtime.
Today it tests: a markdown format contract with an actionable linter, seven item types,
deterministic scoring behind one scorer, resumable JSON sessions, an offline HTML quiz,
a graded loopback sitting, Anki TSV export, and a cross-subject `day` cockpit.

The next milestone turns learner-owned books, syllabi, exam blueprints, notes,
existing banks, and folders into a coherent course. It discovers and binds
sources, builds a cited objective and prerequisite map, chooses the right
treatment per objective (including direct source reading), creates missing
artifacts, provides Brilliant-quality guided teaching and Albert-style
practice/testing where useful, and revises the path from recorded evidence. A
capable model is a first-class course builder, analyst, and optional teaching
collaborator, not the sole teaching surface.

It is for one learner - Weibao - across EMT, Math 1400, and CSCI 1100, with AI tutors
as first-class clients of the same runtime a human uses.

**Product North Star:** **Learner-owned sources become an inspectable,
high-quality, AI-operable course whose readings, lessons, practice, tests, and
next actions are aligned to cited objectives and improved by honest evidence.**

Read `.planning/SOURCE-TO-COURSE.md` before any course, source, metrics,
agent-authoring, or learner-UI planning. It is the binding next-milestone scope.
Read `.planning/USER-VISION.md` beside it for Weibao's verbatim, additive goal;
never silently replace that record with an interpreted summary.

Read `.planning/AGENT-WORKFLOW.md` before consequential course, source, lesson,
assessment, UI, research, migration, or product-direction work. It is the
shared operating contract for Claude Code/Cowork, Codex, local agents, and other
clients. It defines how to capture vision without rewriting the user's words,
run bounded research waves, reconcile evidence, preserve viable ideas, record
rejections, name authority and recovery, and hand off work without depending on
chat history.

### Course artifact workflow

Before creating a lesson, question set, bank, practice activity, or exam, find
and evaluate prior work across every user-approved root. Those roots may be
separate, including course folders, source folders, and an Obsidian vault.
Discovery is read-only by default and does not authorize mutation.

1. Inventory sources and existing artifacts with their location, stable
   identity, fingerprint, ownership, provenance, objective links, draft or
   accepted state, and validation status where available.
2. Reconcile likely duplicates, moved files, stale links, and conflicting
   versions. Do not identify or merge artifacts from filenames alone.
3. Update the cited objective and prerequisite map. Decide the best treatment
   per objective, including direct reading, before generating anything.
4. Reuse or link an adequate existing artifact. Distinguish linking,
   importing, copying, moving, and superseding, and preserve provenance.
5. Create only genuinely missing treatments through the relevant skill and
   deterministic format contract. Label synthesis and retain citations.
6. Verify lessons in both forms: the durable authored document and the richer
   itembank presentation. The source must remain coherent in plain Markdown or
   Obsidian, while the UI may progressively add hover and focus definitions,
   interactive diagrams, demonstrations, adaptive disclosure, and other
   accessible learning controls.
7. When enhancing legacy material, audit before editing. Preserve stable
   identity and source history, select changes that add learning value, retain
   useful static and accessibility fallbacks, and present a bounded diff.
   Never silently change keyed content, assessment meaning, difficulty, or
   objective alignment.
8. Reindex disposable discovery data, validate links and artifacts, and report
   changes, uncertainties, and reversal steps.

Agent skills are part of the product interface. They should cover whole-course
orchestration, curriculum design, source absorption, lesson authoring,
question and exam authoring, discovery and binding, legacy-artifact upgrades,
and course-quality review. Skills must work as portable playbooks for Claude,
Codex, compatible local agents, and other agent clients while respecting the
same runtime and artifact contracts.

### Prose style rule

Do not use em dash characters in repository-authored prose, documentation,
comments, fixtures, generated lessons, or questions. Use commas, parentheses,
colons, semicolons, or separate sentences instead. Verbatim source quotations
and additive statements in `.planning/USER-VISION.md` are the only exceptions.
Future linting should detect this without rewriting quoted source material.

### Direction and operation rules

- Keep quotations, interpretations, research findings, recommendations,
  accepted product clauses, and implementation decisions visibly distinct.
- Every meaningful idea receives a durable route and disposition. Viable ideas
  remain core, registered, prototype, backburner, or deferred. Superseded and
  rejected ideas remain recorded with evidence and reconsideration conditions.
- Before accepting a feature, name its actor, durable object, source of truth,
  authority, state axes, provenance, rights, egress, degraded behavior,
  accessibility, validation, recovery, and maintenance owner.
- Link and edit existing files in place by default. Mutations use an expected
  fingerprint, reviewable diff, atomic write, operation journal, and recoverable
  prior revision. External edits produce stale or conflict state.
- Learner notes never silently become source truth, lesson truth, answer keys,
  scores, or mastery. Presentation state never grants authorization. Derived
  views and indexes never become the only understandable copy.
- Run the implementation-readiness audit in the Phase 16 synthesis before
  planning Phase 14A. Plans trace backward to vision and evidence and forward
  to verification, migration, documentation, and maintenance.

### Object, authority, and operation summary (2026-08-13)

This mirrors `AGENTS.md` so the two stay consistent, and condenses the Phase 16
synthesis (`.planning/research/phase-16/14-synthesis.md` sections 2, 3, 6, and
10). The binding contract is `.planning/SOURCE-TO-COURSE.md`. These are
non-negotiable operation, authority, rights, acceptance, and recovery rules:

- **Authority (synthesis 2.1, 2.3).** The learner owns goals, private notes,
  scratch work, strategy choice, and evidence export. A course builder defines
  scope, treatments, and paths within source and rights limits. A reviewer
  accepts or rejects revisions. A hosted or local agent discovers, aligns,
  drafts, validates, and explains within an operation manifest and never owns
  accepted truth or assessment authority. The deterministic runtime is the sole
  authority for assessment session state, keyed disclosure, scoring, and attempt
  evidence.
- **Durable objects and derived state (synthesis 2.2, 2.3).** Course, scope or
  framework version, concept, objective, source, source binding, artifact,
  lesson, bank or assessment form, activity, learner note, learner artifact,
  evidence event, strategy, agent operation, rights grant, and accepted revision
  each name a source of truth. Accepted files are canonical; indexes, HTML,
  caches, rankings, and progress views are derived and disposable.
- **Separate state axes (synthesis 2.3, 4.1).** Accepted content, workflow state
  (`pending`), epistemic confidence (low), validation state (invalid), rights
  state, and availability are independent. Do not collapse them.
- **One operation protocol (synthesis 10).** Declare intent; declare approved
  roots, rights, egress, write, and execute authority; inventory before
  creating; plan treatment; checkpoint; draft the smallest missing artifact;
  cite and label synthesis; validate deterministically; show an accessible plain
  and rich preview; present a bounded diff; pass configured review; accept
  atomically; update dependency and staleness state; report undo and
  uncertainty. Backend choice changes cost, latency, and disclosure, not the
  artifact or authority contract.
- **Compare-and-swap mutation (synthesis 6).** Every durable write states an
  expected base fingerprint, writes to a temporary file, validates, commits
  atomically, and appends to an operation journal, so any fault leaves the old
  or new valid state. Link, import, copy, move, edit-in-place, supersede,
  migrate, and synchronize are distinct operations, not synonyms. A same-ID,
  divergent-bytes case is a conflict, never a silent overwrite.
- **Rights and egress per operation (synthesis 6, 11).** Read, quote, transform,
  remote-process, package, export, and share are separate grants. Unknown rights
  stay restrictive. Hosted operations minimize and disclose exact egress.
- **Authored-output accessibility (synthesis 11.4).** Representative authored
  outputs pass keyboard, touch, screen-reader, zoom and reflow, high-contrast,
  and reduced-motion review. An agent never self-certifies accessibility.
- **Clean recovery (synthesis 3 loop G, 6).** Export is not complete until a
  clean-machine, offline restore validates a manifest and reports every loss.
  Interrupted, offline, denied, future-schema, and agent-unavailable states
  preserve the last accepted state and expose the next safe action.
- **Preserve breadth; append-only ledger (synthesis 1, 12).** Every viable idea
  stays as core, registered, prototype, or backburner with dependency, cost, and
  revisit trigger. Untimely is not rejected, and simplicity alone is not a
  rejection reason. The rejection and supersession ledger is append-only: a
  superseded or hard-rejected idea is never deleted, and each rejection records
  evidence, exact reason, conflicting rule, retained alternative, date, and
  reconsideration condition.

**Runtime invariant:** **One runtime, one scorer, one evidence store - and the
runtime, not the model, settles scoring, assessment disclosure, and evidence.**

The tutoring model is smart and well-informed: it reads the item, the key, the
rationale, and the learner's specific wrong answer, so it can teach about *this*
error rather than about the item in general. What it is not allowed to do is choose
how much to say. The runtime gates that by session mode and by hint tier, so a model
argued into wanting to reveal still cannot, because the reveal is the runtime's call
and not the model's.

This invariant is a small safety and consistency boundary, not the product
thesis. AI may search approved roots, design curricula, select readings, draft
and revise artifacts, interpret metrics, propose remediation, and perform
approved bounded writes. It cites sources, labels synthesis, reports uncertainty
and denominators, and leaves acceptance and reversal visible. If a feature
requires a second scorer, parser, or evidence store, the feature is wrong.

### Constraints

> **Amendment 2026-08-09 - constraint relaxation (Weibao, recorded verbatim in
> `.planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md` §1).** The following
> are now **preferences, not rules**: Python-stdlib-only, no install/build step,
> Python-only, offline-first/local-first. Dependencies, bundlers, npm, and
> non-Python components are permitted when they earn their cost. **A packaged
> desktop app is an end goal.** Judge ideas on product merit and report real
> cost; do not reject an idea for needing a dependency. Still non-negotiable:
> (1) the runtime owns correctness, session state, evidence, and keyed
> assessment disclosure; (2) exactly one
> parser, one scorer, one evidence store; (3) evidence and banks stay on disk, no
> telemetry; (4) format changes are additive; (5) the accessibility gates in
> `.planning/UI-SPEC.md`. Bullets below marked *(relaxed 2026-08-09)* are kept
> for history but no longer bind.

> **Pointer 2026-08-13.** The bullets below are preserved as the shipped-runtime
> constraint history. The current binding operation, authority, rights,
> acceptance, and recovery contract is the "Object, authority, and operation
> summary" above, `AGENTS.md`, `.planning/SOURCE-TO-COURSE.md`, and the Phase 16
> synthesis (`.planning/research/phase-16/14-synthesis.md`). Where a bullet reads
> as bank-first or stdlib-only, treat it as history and defer to those files; do
> not delete it. The five non-negotiables and the Runtime invariant remain in
> force.

- **Tech stack** *(relaxed 2026-08-09 - now a preference, see amendment above)*: Python standard library only, no install step - the founding design constraint. Two named exceptions: a vendored KaTeX asset for Math rendering (goal 5 forbids services and network, not files), and stdlib `urllib` for the opt-in updater.
- **Network**: hosted models are permitted, so the tool is no longer offline-only. But the core loop must **degrade, never block**: sitting a quiz, scoring, lessons, the authored hint ladder, evidence, and reports all work with the network unplugged. The model layer goes quiet when unreachable, the same way `day` omits Anki counts when Anki is closed. Being out of credits must never stop you studying.
- **Data residency**: evidence and banks stay on disk. No cloud sync, no hosted gradebook, no telemetry. Item text may transit to a model in a request; it is never stored remotely by this tool.
- **Accepted risk - the `update_policy` divergence is deliberate (D-13).** The schema default is `opt_in`, so a fresh install with no settings file never phones home without being asked; this repository's own checked-in `itembank.json` sets `check_on_launch` so the updater gets dogfooded through Phases 3–11, which is the reason this phase was pulled forward. The background check is throttled to the configured interval and prints a one-time disclosure before its first request, and the two values are meant to differ - recorded 2026-08-08 so this is not rediscovered later as a surprise.
- **Model backends**: hosted (Claude Code, Codex, or a competitor) and local (an OpenAI-compatible server such as llama.cpp or Ollama running Qwen) are the same code path. The local backend is prepared in advance rather than retrofitted, so the hardware arriving is a config change and not a rewrite.
- **Surfaces**: every capability has both a route in the daemon and a command in the CLI. Neither surface is the real one; both are clients of the runtime.
- **Accepted risk - hosted models see item text.** Weibao's explicit decision on 2026-08-05, after the tradeoff was put to him. It means AAOS-12e-derivative EMT items and course-derived CSCI 1100 items transit to a hosted provider. Two things stay true and are recorded here so they are not rediscovered as surprises: hosted or local, this is **AI assistance on graded coursework**, and the CSCI 1100 AI-use ban applies to both; and the local-only path remains fully built, so any subject can be moved back behind it by changing one setting rather than by changing the code.
- **Data**: No real question banks in this repository, enforced by `itembank guard` in CI. Fixtures are synthetic. Learner evidence lives beside the private bank.
- **Compatibility**: Format changes must be additive. A bank without a `LESSON` section must parse exactly as it does today.
- **Hardware**: The local-model path targets a 7900 XTX build that does not exist yet. The adapter is designed now as a vendor-neutral interface; the local backend waits for the machine.
- **Users**: One. No accounts, no auth, no multi-tenancy, and no design work spent on them.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

> **Note (2026-08-09):** this section describes the stack **as built today**. The
> stdlib-only / no-build-step / Python-only statements below are historical fact,
> not forward constraints - see the Constraints amendment above. Future phases may
> add a build step, npm-managed frontend assets, or non-Python components where
> they earn it, and Phase-12-scope packaging targets a real installer.

## Languages

- Python 3 (3.11+) - All application logic, tooling, and tests
- Standard library only. No Node.js, JavaScript, compiled languages, or external runtimes.

## Runtime

- Python 3.11+ (tested explicitly in CI via `actions/setup-python@v5`)
- Available on Linux, macOS, Windows
- None required - Standard library only, no external dependencies
- Lockfile: Not applicable

## Frameworks

- Python standard library only: `json`, `re`, `os`, `sys`, `collections`, `argparse`, `html`
- `http.server` (BaseHTTPRequestHandler, TCPServer) - Loopback server for browser surfaces
- `socketserver.TCPServer` - HTTP server binding with OS port fallback (for Windows Hyper-V compatibility)
- `random` - Used for shuffling build-type question steps in rendering
- Python unittest/subprocess-based - See `tests/` directory
- Test runner: Direct Python script execution (no pytest, unittest framework, or test runner dependency)
- No build system - Direct Python execution
- GitHub Actions (CI/CD) - For automated test runs on push/PR

## Key Dependencies

- `itembank.py`: imports from `model`, `runtime`, `surfaces` (internal modules)
- `model.py`: uses `collections`, `re`, `sys`
- `runtime.py`: uses `collections`, `json`, `os`, `sys`
- `server.py`: uses `http.server`, `json`, `socketserver`
- All surfaces (`surfaces/*.py`): use only standard library modules
- Tests (`tests/*.py`): use subprocess, urllib, json, tempfile, threading, time (all standard)

## Configuration

- No `.env` file or environment file required
- Optional environment variable: `ANKI_CONNECT_URL` - Allows overriding default AnkiConnect URL (see INTEGRATIONS.md)
- Platform-specific defaults: Uses `APPDATA` on Windows, `XDG_DATA_HOME` on Linux/macOS for Anki profile location
- No build configuration files (no `setup.py`, `pyproject.toml`, `requirements.txt`)
- CI configuration: `.github/workflows/ci.yml` - Runs linting, builds, and test suite on push/PR

## Platform Requirements

- Python 3.11+ interpreter
- Read/write access to local filesystem for markdown banks, session files, and logs
- Git (optional, for `git status` integration in day surface)
- Anki Desktop (optional, for deck tracking via AnkiConnect)
- Same as development - Any machine with Python 3.11+
- Runs completely offline by default
- Optional network access only if using Anki integration (communicates with local Anki instance)

## Entry Point

- **CLI:** `python itembank.py [COMMAND] [ARGS]` - Direct script execution
- **Imported module:** `import itembank` from Python code - Exposes public API via `__all__`

## Execution Model

- Single-threaded: Main execution path is synchronous
- Stateless: No persistent daemon or background service
- Local-first: All data stored as plain markdown or JSON files on the filesystem
- No database server, message queue, or service dependencies

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- Module files are snake_case: `model.py`, `runtime.py`, `server.py`, `itembank.py`
- Surface modules in `surfaces/` follow same pattern: `cli.py`, `quiz.py`, `session.py`, `study.py`, `day.py`, `anki.py`
- Test files use `*_roundtrip.py` pattern: `scoring_roundtrip.py`, `day_roundtrip.py`, `serve_roundtrip.py`, `agent_roundtrip.py`
- Executable Python files have shebang: `#!/usr/bin/env python3`
- Regular functions use snake_case: `parse_bank()`, `canonical_response()`, `score_response()`, `public_item()`, `session_view()`
- Command handlers use `cmd_` prefix: `cmd_spec()`, `cmd_lint()`, `cmd_build()`, `cmd_serve()`, `cmd_start()`, `cmd_next()`, `cmd_submit()`, `cmd_day()`, `cmd_guard()`, `cmd_study()`, `cmd_export()`
- No private functions (underscore prefixes) - all module-level functions are importable
- Helper functions are prefixed by purpose: `page_for()`, `served_items()`, `check_*()` in tests
- All variables use snake_case: `seen_stems`, `letter_hits`, `correct_answer`, `wrong_answer`, `session_data`
- Dictionary keys use quotes for compound names: `"schema_version"`, `"correct_analysis"`, `"auto_correct"`
- Loop variables single letter when obvious: `for q in qs`, `for L in LETTERS`, `for i, r in enumerate(questions)`
- Module-level constants in UPPERCASE: `LETTERS = "ABCDEFGH"`, `SESSION_VERSION = 1`, `FIELD_SEP = "\x1f"`, `PAIR_SEP = "\x1e"`
- Regex patterns stored as module constants: `WOULD_BE = re.compile(...)`
- File name hints stored as tuples: `BANK_FILE_HINTS = ("_mc_bank", "_exam_bank", ...)`

## Code Style

- No linter or formatter configured - code is manually formatted
- Indentation: 4 spaces (standard Python)
- Line continuation: Implicit inside parentheses without backslashes
- Long regex patterns broken across lines with implicit string concatenation or raw string literals: `r"pattern1" r"pattern2"`
- String formatting: Uses `%` operator throughout: `"%d items, %d errors" % (len(qs), len(errors))`
- No `.flake8`, `.pylintrc`, or `pyproject.toml` configuration
- No automatic linting - manual code review is the standard
- Standard library only - zero external dependencies by design
- Module docstrings are comprehensive and explain design: See `itembank.py` for the four-layer architecture description
- Function docstrings are present for public APIs: `canonical_response()`, `score_response()`, `page_item()`
- Docstrings explain WHY and WHAT, not HOW
- Example from `runtime.py`: docstrings explain the invariant that one scorer exists everywhere

## Import Organization

- No path aliases configured - all imports are explicit relative or standard library

## Error Handling

- CLI errors use direct `sys.exit(message)` with human-readable messages: `sys.exit("cannot read session %s: %s" % (path, exc))`
- Early returns with meaningful values: None for constructed response (no canonical form), empty string for missing data
- Validation errors accumulated in lists and returned: `lint()` returns `(errors, warnings)` tuples
- Exception handling only for file I/O and JSON parsing:
- Test helper function `fail(msg)` prints "FAIL: " prefix and exits with code 1
- Used throughout test files: `if not qs: fail("fixture bank parsed to nothing")`

## Logging

- Status lines printed to stdout: `print("%d items -> %s" % (len(qs), out))`
- Error messages on stderr via `sys.exit()` - forces non-zero exit
- JSON results printed with proper formatting: `print(json.dumps(result, ensure_ascii=False, indent=2))`
- Progress indicators printed while running: `print("   mix: " + mix)`, `print("   note: ...")`

## Comments

- Design decisions and invariants are documented at module level
- Function-level comments explain WHY when it's non-obvious
- Inline comments explain tricky regex or complex business logic
- Example: `# The static page's key and the scorer's key are the same value, or the offline surface silently disagrees with every other one.`
- Block comments start with `# ` and are complete sentences
- No JSDoc/docstring style for functions - docstrings use plain sentences instead
- Comments often reference the file/design invariant: `# One scorer, structurally, across every module rather than in the one file that happens to hold it today.`

## Function Design

- Functions accept question dicts directly: `def score_response(q, answer)`
- Optional parameters use defaults: `def public_item(q, shuffle_seed=0)`
- Command handlers receive argparse Namespace: `def cmd_build(a)` where `a` is the parsed args
- Functions return dicts for structured data: `public_item()` returns item dict with `"id"`, `"stem"`, `"options"`, etc.
- Validation returns tuples: `lint()` returns `(errors, warnings)`
- Boolean None is used for unknown/pending: short answer scoring returns `None` (not yet marked), not `False`
- Empty strings for missing/invalid data: `grab()` returns `""` when pattern doesn't match

## Module Design

- Explicit `__all__` list in `itembank.py` for the public surface: Lists 29 exported items
- No `__all__` in internal modules - everything at module level is importable
- Pattern: Surfaces import what they need directly, don't use * imports
- No barrel files (index.py pattern)
- Direct imports are preferred: `from model import parse_bank` not `from model import *`
- `model.py`: Format contract, parsing, validation
- `runtime.py`: Scoring (the only scorer), sessions, public/private item payloads
- `server.py`: Single loopback HTTP server
- `surfaces/*`: UI clients (CLI, quiz HTML, study HTML, day page, JSON sessions, Anki export)

## Dictionaries and Data Shapes

## String Constants

- `FIELD_SEP = "\x1f"` - separates fields in canonical form (not visible punctuation)
- `PAIR_SEP = "\x1e"` - separates key-value pairs
- Used instead of `|`, `>`, `,` because content contains those characters
- `"mc"` - multiple choice, pick one
- `"multi"` - multiple response, pick N
- `"table"` - categorize rows
- `"dnd"` - drag and drop, same as table but shuffled display
- `"build"` - ordering, put steps in sequence
- `"short"` - constructed response, human marked

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## System Overview

```text

```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Model | Parse and validate markdown banks; define format contract | `model.py` |
| Runtime | Score responses; manage sessions; control public/private payload visibility | `runtime.py` |
| Server | Loopback HTTP handler for browser surfaces; port fallback logic | `server.py` |
| Surfaces | Rendering and interaction (CLI, quiz, study, day, export, sessions) | `surfaces/` |
| Entry Point | Command routing and argument parsing | `itembank.py` + `surfaces/cli.py` |

## Pattern Overview

- **No scoring duplication**: Every surface (CLI, browser, JSON) reaches verdicts by calling `runtime.score_response()`, ensuring consistent grading
- **Public/private data separation**: `public_item()` and `explain_payload()` control what a learner sees before/after responding
- **Format contract enforcement**: `model.lint()` gives explicit, actionable feedback to authoring agents (AI or human)
- **Stateless surfaces**: All surfaces are clients that call into runtime; none reimplements rules
- **No external dependencies**: Python standard library only; no network, services, or install step

## Layers

- Purpose: Parse markdown into structured question dicts; validate format compliance; define the format contract
- Location: `model.py`
- Contains: Parsing functions (`parse_bank`, `parse_question`), validation logic (`lint`), format spec (`SPEC`)
- Depends on: None (no dependencies)
- Used by: All other layers; entry point for format validation
- Pattern: Regex-based markdown parsing; returns plain dicts; returns None on invalid items
- Purpose: Score responses; manage resumable assessment sessions; control payload visibility; centralize grading logic
- Location: `runtime.py`
- Contains: Scoring functions (`score_response`, `canonical_response`, `canonical_key`), session I/O (`read_session`, `write_session`), payload builders (`public_item`, `explain_payload`, `page_item`)
- Depends on: `model.py` (indirectly through surfaces)
- Used by: All surfaces; the only module that decides correctness
- Pattern: Pure functions for scoring; JSON-based session files; control flow through `canonical_response()` shape agreement
- Purpose: Provide a reusable loopback HTTP handler; abstract away socket binding and port fallback for browser-based surfaces
- Location: `server.py`
- Contains: Base HTTP handler class (`Handler`), port binding with fallback (`bind`)
- Depends on: Standard library only
- Used by: `surfaces/quiz.py` and `surfaces/day.py` for graded sittings and day cockpit
- Pattern: Minimal abstraction; surfaces subclass `Handler` and add `do_GET` and `do_POST`
- Purpose: Render and interact with question banks via different interfaces
- Location: `surfaces/`
- Contains: Multiple rendering clients; none implement their own scoring or parsing
- Surfaces:
- Pattern: Each surface is a client that calls `model.load()`, `runtime.score_response()`, etc.; surfaces print/render outputs

## Data Flow

### Primary Assessment Flow (serve / graded sitting)

### Agent Assessment Flow (session commands)

### Study Flow

### Day Surface Flow

### Static Quiz Flow (build / offline)

- **Session state**: JSON file format (`_attempts/session_*.json`), contains items list, cursor, responses array
- **Attempt records**: Markdown files (`_attempts/*_attempt_*.md`), human/LLM readable, mutable for manual grading
- **Day log**: Markdown table (`daily_log.md`), one row per day, headers match lanes
- **Wiring**: Markdown table (`lanes.md`), lane config and global fuses
- **Question banks**: Markdown files (user-provided), parsed on every invocation (no database)

## Key Abstractions

- Purpose: What a learner sees before answering (no key, no explanation)
- Examples: `runtime.public_item()`, returned by `session_view()` on active item
- Pattern: All options/steps/rows without answers; response_schema defines how learner can answer
- Purpose: What a learner sees after answering (full explanation, key, rationale)
- Examples: `runtime.explain_payload()`, written to attempt file markdown
- Pattern: Answer text, why/discriminator/second-best/trap/notes, DA per option (mc/multi only)
- Purpose: Reduce any learner response to a comparable string for scoring
- Examples: `runtime.canonical_response()` turns mc answer `["B"]` into string `"B"`
- Pattern: Different shape per question type (string for mc, comma-separated for multi, field-separated for table/build)
- Ensures browser offline page and runtime scorer agree on what a response IS
- Purpose: In-memory representation of a parsed question
- Examples: All surfaces operate on `qs[i]` dicts from `model.load()`
- Fields: `id, number, type, stem, difficulty, objective, opts, correct, da, why, disc, trap, conf, etc.`
- Pattern: Same shape returned by `parse_question()` for all types
- Purpose: Persistent record of a learner's progress through a subset of items
- Examples: Stored in `_attempts/session_*.json`, readable by `runtime.read_session()`
- Fields: `schema_version, session_id, bank, items (indices), cursor, responses (array of {item_id, score, answer}), status, mode, objective, seed`
- Pattern: Items list is indices into original bank, not copies; responses array grows as learner proceeds

## Entry Points

- Location: Root; executable
- Triggers: `python itembank.py` or `python itembank.py <cmd>`
- Responsibilities: Insert root into sys.path; import all layers; delegate to CLI main
- Pattern: Not used directly; surfaces/cli.py:main() is the real entry point
- Location: `surfaces/cli.py`
- Triggers: `python itembank.py <cmd>` (or symlinked as `itembank`)
- Responsibilities: Parse arguments; route to cmd_* function in each surface module
- Commands: `spec, lint, build, serve, start, next, submit, report, study, export, day, stats, guard`
- Pattern: Each surface module has a `cmd_*` function that main() imports and calls
- Location: User-provided file (path passed to commands)
- Triggers: Any command that needs to load a bank
- Pattern: `model.load(path)` reads and parses the file
- Location: `_attempts/<bank>_attempt_<date>.md` (default) or `--out` arg
- Triggers: Written by `surfaces/quiz.py:cmd_serve()`
- Pattern: One heading per question; auto-marked verdict marked in heading; human edits `MARK:` for short answers
- Location: `_attempts/session_*.json` (default) or `--out` arg to `start`
- Triggers: Created by `surfaces/session.py:cmd_start()`, read/written by `next` and `submit`
- Pattern: Deterministic item selection via seed; agent-readable JSON; cursor-based navigation
- Location: User-provided; any markdown with a parseable date table
- Triggers: `itembank day plan.md` looks for first table with date-like first column
- Pattern: Headers = lane names; one row per day; day surface reads today's row
- Location: `lanes.md` beside plan, or `--lanes` arg
- Triggers: Parsed by `surfaces/day.py` if present
- Pattern: Two table types: lane wiring (Lane, Deck, Notes glob, Fuse date) and global fuses (Fuse date, date)

## Architectural Constraints

- **Scoring is centralized**: Every surface reaches verdicts through `runtime.score_response()` only. No surface reimplements grading rules.
- **Parsing is centralized**: Every surface loads banks via `model.load()` and `model.parse_bank()` only.
- **No circular imports**: Model layer has no imports from runtime or surfaces; runtime imports from model only via surfaces calling it; server is independent.
- **No global state**: No module-level question dicts or session caches; all state passed as arguments or read from files.
- **Single server instance per surface**: `surfaces/quiz.py` and `surfaces/day.py` each start their own `server.bind()` on demand; no shared instance.
- **Session files are transactional**: Writes via `runtime.write_session()` use atomic rename (write to .tmp, then os.replace); safe to read while writing.
- **No database**: All state is markdown and JSON on disk; no SQLite, no cache, no network backend.

## Anti-Patterns

### Scoring in Multiple Places

### Parsing the Bank Multiple Times

### Leaking Answer Keys to the Browser Before Answering

### Long-Running Operations Without Progress Feedback

## Error Handling

- Format errors: `model.lint()` returns structured `(errors, warnings)` as list of `"Qn: message"` strings. Commands print these and exit non-zero. See `surfaces/cli.py:cmd_lint()`.
- Parsing errors: Malformed JSON in session files → `runtime.read_session()` calls `sys.exit()` with path and exception. See `runtime.py` line 135.
- Missing items: Cursor out of bounds → `surfaces/session.py:cmd_submit()` detects and exits with "session is already complete".
- Lint but continue: `--force` flag lets surfaces load banks with errors (for testing). See `surfaces/quiz.py:cmd_build()` line 38.

## Cross-Cutting Concerns

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
