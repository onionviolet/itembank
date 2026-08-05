<!-- refreshed: 2026-08-05 -->
# Architecture

**Analysis Date:** 2026-08-05

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                        Surfaces Layer                        │
│  CLI  |  Quiz  |  Study  |  Day  |  Export  |  Session JSON │
│ `surfaces/`                                                  │
└──────────┬──────────┬──────────┬──────────┬───────────────┘
           │          │          │          │
           ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Server Layer (Optional)                   │
│         Loopback HTTP Server for Browser-based Surfaces     │
│              `server.py`                                      │
└──────────┬──────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Runtime Layer (Core)                      │
│  Scoring | Sessions | Public/Private Data Separation        │
│             `runtime.py`                                      │
└──────────┬──────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Model Layer (Foundation)                  │
│  Parsing | Validation | Format Contract                     │
│             `model.py`                                        │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Markdown Question Bank                   │
│                  (.md files + .json sessions)                │
└─────────────────────────────────────────────────────────────┘
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

**Overall:** Layered architecture with **strict separation of concerns** and **single source of truth** for scoring.

**Key Characteristics:**
- **No scoring duplication**: Every surface (CLI, browser, JSON) reaches verdicts by calling `runtime.score_response()`, ensuring consistent grading
- **Public/private data separation**: `public_item()` and `explain_payload()` control what a learner sees before/after responding
- **Format contract enforcement**: `model.lint()` gives explicit, actionable feedback to authoring agents (AI or human)
- **Stateless surfaces**: All surfaces are clients that call into runtime; none reimplements rules
- **No external dependencies**: Python standard library only; no network, services, or install step

## Layers

**Model Layer:**
- Purpose: Parse markdown into structured question dicts; validate format compliance; define the format contract
- Location: `model.py`
- Contains: Parsing functions (`parse_bank`, `parse_question`), validation logic (`lint`), format spec (`SPEC`)
- Depends on: None (no dependencies)
- Used by: All other layers; entry point for format validation
- Pattern: Regex-based markdown parsing; returns plain dicts; returns None on invalid items

**Runtime Layer:**
- Purpose: Score responses; manage resumable assessment sessions; control payload visibility; centralize grading logic
- Location: `runtime.py`
- Contains: Scoring functions (`score_response`, `canonical_response`, `canonical_key`), session I/O (`read_session`, `write_session`), payload builders (`public_item`, `explain_payload`, `page_item`)
- Depends on: `model.py` (indirectly through surfaces)
- Used by: All surfaces; the only module that decides correctness
- Pattern: Pure functions for scoring; JSON-based session files; control flow through `canonical_response()` shape agreement

**Server Layer:**
- Purpose: Provide a reusable loopback HTTP handler; abstract away socket binding and port fallback for browser-based surfaces
- Location: `server.py`
- Contains: Base HTTP handler class (`Handler`), port binding with fallback (`bind`)
- Depends on: Standard library only
- Used by: `surfaces/quiz.py` and `surfaces/day.py` for graded sittings and day cockpit
- Pattern: Minimal abstraction; surfaces subclass `Handler` and add `do_GET` and `do_POST`

**Surfaces Layer:**
- Purpose: Render and interact with question banks via different interfaces
- Location: `surfaces/`
- Contains: Multiple rendering clients; none implement their own scoring or parsing
- Surfaces:
  - `cli.py`: Command parser and router; implements spec, lint, stats, guard (no server)
  - `quiz.py`: Static HTML quiz (`build`) and graded sitting (`serve`)
  - `study.py`: Flashcard and Learn loop surface
  - `day.py`: Cross-subject daily work tracker with day planning table parsing
  - `session.py`: JSON agent-facing CLI commands (start, next, submit, report)
  - `anki.py`: Export to Anki TSV (Basic and Cloze formats)
  - `quiz_page.py`: HTML template for quiz
  - `theme.py`: CSS theming for quiz page
- Pattern: Each surface is a client that calls `model.load()`, `runtime.score_response()`, etc.; surfaces print/render outputs

## Data Flow

### Primary Assessment Flow (serve / graded sitting)

1. User invokes `itembank serve bank.md` → `surfaces/cli.py:cmd_serve()`
2. CLI loads bank via `model.load()` → dict list of questions
3. Server starts via `server.bind()` and generates page via `surfaces/quiz.py:page_for()`
4. Page template (`quiz_page.py`) embeds offline version via `runtime.page_item(q, offline=True)` with key
5. Browser calls server's POST handler on submit
6. Server calls `runtime.score_response(q, answer)` with learner's response
7. Score written to session JSON file via `runtime.write_session()`
8. Response recorded in attempt markdown file via `surfaces/quiz.py:attempt_markdown()`
9. Explanation returned to browser via `runtime.explain_payload()` (question details revealed)

### Agent Assessment Flow (session commands)

1. Agent calls `itembank start bank.md --count 10` → `surfaces/session.py:cmd_start()`
2. Selects deterministic subset via random seed; writes session JSON
3. Agent calls `itembank next session.json` → returns `session_view()` with public item
4. Agent submits response: `itembank submit session.json --answer '"B"'`
5. Score computed via `runtime.score_response()`, recorded in session JSON
6. Response returns to agent with `accept` flag and next item via `session_view()`
7. Agent can call `itembank report session.json` for summary via `session_summary()`

### Study Flow

1. User invokes `itembank study bank.md` → `surfaces/study.py:cmd_study()`
2. Generates flashcard HTML with answer folding (no scoring)
3. Provides Learn loop mode for repeated review of wrong items
4. Uses `runtime.answer_text()` to format correct answers

### Day Surface Flow

1. User invokes `itembank day plan.md` → `surfaces/day.py:cmd_day()`
2. Parses plan table (first column as dates) to find today's row
3. Extracts lane names from table headers; loads wiring from `lanes.md`
4. For each lane: loads Anki deck, loads notes file, computes `behind` and `load`
5. Serves day cockpit via server; ticks update plan log and session files
6. Log written as markdown table with one row per day

### Static Quiz Flow (build / offline)

1. User invokes `itembank build bank.md` → `surfaces/quiz.py:cmd_build()`
2. Generates standalone HTML with answers embedded via `runtime.page_item(offline=True)`
3. No server; scoring happens in browser via JavaScript
4. Key is visible to learner (no process to protect it from client)

**State Management:**
- **Session state**: JSON file format (`_attempts/session_*.json`), contains items list, cursor, responses array
- **Attempt records**: Markdown files (`_attempts/*_attempt_*.md`), human/LLM readable, mutable for manual grading
- **Day log**: Markdown table (`daily_log.md`), one row per day, headers match lanes
- **Wiring**: Markdown table (`lanes.md`), lane config and global fuses
- **Question banks**: Markdown files (user-provided), parsed on every invocation (no database)

## Key Abstractions

**Public Item:**
- Purpose: What a learner sees before answering (no key, no explanation)
- Examples: `runtime.public_item()`, returned by `session_view()` on active item
- Pattern: All options/steps/rows without answers; response_schema defines how learner can answer

**Explain Payload:**
- Purpose: What a learner sees after answering (full explanation, key, rationale)
- Examples: `runtime.explain_payload()`, written to attempt file markdown
- Pattern: Answer text, why/discriminator/second-best/trap/notes, DA per option (mc/multi only)

**Canonical Response:**
- Purpose: Reduce any learner response to a comparable string for scoring
- Examples: `runtime.canonical_response()` turns mc answer `["B"]` into string `"B"`
- Pattern: Different shape per question type (string for mc, comma-separated for multi, field-separated for table/build)
- Ensures browser offline page and runtime scorer agree on what a response IS

**Question Dict:**
- Purpose: In-memory representation of a parsed question
- Examples: All surfaces operate on `qs[i]` dicts from `model.load()`
- Fields: `id, number, type, stem, difficulty, objective, opts, correct, da, why, disc, trap, conf, etc.`
- Pattern: Same shape returned by `parse_question()` for all types

**Session Dict:**
- Purpose: Persistent record of a learner's progress through a subset of items
- Examples: Stored in `_attempts/session_*.json`, readable by `runtime.read_session()`
- Fields: `schema_version, session_id, bank, items (indices), cursor, responses (array of {item_id, score, answer}), status, mode, objective, seed`
- Pattern: Items list is indices into original bank, not copies; responses array grows as learner proceeds

## Entry Points

**`itembank.py`:**
- Location: Root; executable
- Triggers: `python itembank.py` or `python itembank.py <cmd>`
- Responsibilities: Insert root into sys.path; import all layers; delegate to CLI main
- Pattern: Not used directly; surfaces/cli.py:main() is the real entry point

**`surfaces/cli.py:main()`:**
- Location: `surfaces/cli.py`
- Triggers: `python itembank.py <cmd>` (or symlinked as `itembank`)
- Responsibilities: Parse arguments; route to cmd_* function in each surface module
- Commands: `spec, lint, build, serve, start, next, submit, report, study, export, day, stats, guard`
- Pattern: Each surface module has a `cmd_*` function that main() imports and calls

**Question Bank (Markdown File):**
- Location: User-provided file (path passed to commands)
- Triggers: Any command that needs to load a bank
- Pattern: `model.load(path)` reads and parses the file

**Attempt File (Markdown):**
- Location: `_attempts/<bank>_attempt_<date>.md` (default) or `--out` arg
- Triggers: Written by `surfaces/quiz.py:cmd_serve()`
- Pattern: One heading per question; auto-marked verdict marked in heading; human edits `MARK:` for short answers

**Session File (JSON):**
- Location: `_attempts/session_*.json` (default) or `--out` arg to `start`
- Triggers: Created by `surfaces/session.py:cmd_start()`, read/written by `next` and `submit`
- Pattern: Deterministic item selection via seed; agent-readable JSON; cursor-based navigation

**Day Plan (Markdown):**
- Location: User-provided; any markdown with a parseable date table
- Triggers: `itembank day plan.md` looks for first table with date-like first column
- Pattern: Headers = lane names; one row per day; day surface reads today's row

**Lanes Wiring (Markdown):**
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

**What happens:** Early versions may have had scoring logic in quiz_page.py (browser), session.py, and runtime.py, each slightly different

**Why it's wrong:** A response could be graded differently depending which surface scored it, making audit trails unreliable and remediation/appeals impossible

**Do this instead:** Call `runtime.score_response(q, answer)` from every surface. Only this function decides correctness. See `surfaces/session.py:cmd_submit()` line 57 and `surfaces/quiz.py` line ~200 where server calls runtime's scorer.

### Parsing the Bank Multiple Times

**What happens:** Each surface could call `model.parse_bank()` independently, accumulating parsing bugs

**Why it's wrong:** A question might be valid to surface A but invalid to surface B, breaking assumption that the bank is stable

**Do this instead:** Always load via `model.load(path)` once per invocation, cache the result locally within the surface, pass to helper functions. See `surfaces/session.py:cmd_start()` line 15 and subsequent surfaces that hold `qs` locally.

### Leaking Answer Keys to the Browser Before Answering

**What happens:** `build` generates a static page, so the page must hold the key. Any other surface sending the key before POST response is wrong.

**Why it's wrong:** An online quiz reveals the answer to items yet to be answered, turning them into recognition rather than recall

**Do this instead:** `serve` sends only `public_item()` from page generation and server endpoints. Only `build` (static, offline) calls `runtime.page_item(offline=True)` with the key. See `surfaces/quiz.py:page_for()` line 24.

### Long-Running Operations Without Progress Feedback

**What happens:** Day surface parsing Anki with no output while user waits

**Why it's wrong:** User assumes the tool hung and kills it, losing any ticked work that hasn't yet flushed to disk

**Do this instead:** Print progress lines as work completes. See `surfaces/day.py` printing "  loading…" messages and `surfaces/quiz.py` printing "% 20 items ->" on completion.

## Error Handling

**Strategy:** Fail fast and loudly with actionable messages.

**Patterns:**
- Format errors: `model.lint()` returns structured `(errors, warnings)` as list of `"Qn: message"` strings. Commands print these and exit non-zero. See `surfaces/cli.py:cmd_lint()`.
- Parsing errors: Malformed JSON in session files → `runtime.read_session()` calls `sys.exit()` with path and exception. See `runtime.py` line 135.
- Missing items: Cursor out of bounds → `surfaces/session.py:cmd_submit()` detects and exits with "session is already complete".
- Lint but continue: `--force` flag lets surfaces load banks with errors (for testing). See `surfaces/quiz.py:cmd_build()` line 38.

## Cross-Cutting Concerns

**Logging:** stdout only. No log files, no log levels. Each command is responsible for printing its own progress and result. See `surfaces/quiz.py:cmd_build()` printing `"%d items -> %s"` and study surfaces printing item counts.

**Validation:** `model.lint()` is called once per command-invocation before any rendering. No re-validation per item. Surfaces can pass `--force` to skip.

**Authentication:** None. This is a local-only tool. No users, no accounts, no API keys. Bank authorship is not tracked.

**Encoding:** UTF-8 everywhere. Bank markdown, session JSON, attempt files, day log all use UTF-8. HTML output declares charset. See `model.py` line 307 `open(..., encoding="utf-8")`.

---

*Architecture analysis: 2026-08-05*
