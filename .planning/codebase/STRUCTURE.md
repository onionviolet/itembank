# Codebase Structure

**Analysis Date:** 2026-08-05

## Directory Layout

```
itembank/
├── itembank.py              # Entry point: sys.path setup, imports, delegates to cli.main()
├── model.py                 # Format contract, parsing, validation (no dependencies)
├── runtime.py               # Scoring, sessions, payload control (the only scorer)
├── server.py                # Loopback HTTP handler, port fallback
├── surfaces/                # Rendering and interaction clients
│   ├── __init__.py
│   ├── cli.py              # Command parser and router (main entry)
│   ├── quiz.py             # Static quiz (build) and graded sitting (serve)
│   ├── quiz_page.py        # HTML template for quiz
│   ├── theme.py            # CSS theming
│   ├── study.py            # Flashcards and Learn loop
│   ├── session.py          # JSON agent CLI (start, next, submit, report)
│   ├── anki.py             # Anki export (Basic, Cloze TSV)
│   └── day.py              # Day surface (cross-subject planner, fuses, lanes)
├── tests/                   # Test roundtrips (integration-style tests)
│   ├── agent_roundtrip.py
│   ├── day_roundtrip.py
│   ├── due_roundtrip.py
│   ├── scoring_roundtrip.py
│   ├── serve_roundtrip.py
│   └── surface_roundtrip.py
├── fixtures/                # Sample banks and test data
│   ├── sample_bank.md       # Multi-type question bank
│   ├── broken_bank.md       # Invalid bank for lint testing
│   ├── sample_bank_quiz.html
│   ├── sample_bank_study.html
│   ├── sample_plan.md       # Day plan with date table
│   └── sample_lanes.md      # Day lanes/wiring config
├── .planning/              # Planning documents
│   └── codebase/
│       ├── ARCHITECTURE.md
│       └── STRUCTURE.md
├── .github/                 # GitHub configuration (workflows, etc.)
├── .gitignore              # Excludes __pycache__, .env, _attempts, etc.
├── README.md               # User-facing documentation
├── GRADING.md              # Rubric for manual short-answer grading
├── LICENSE                 # Project license
└── ROADMAP.md              # Project roadmap and future plans
```

## Directory Purposes

**`itembank/` (root):**
- Purpose: Python modules and entry point
- Contains: Layer modules (model, runtime, server) and surfaces package
- Key files: `itembank.py` (entry point), `model.py`, `runtime.py`, `server.py`

**`surfaces/`:**
- Purpose: All rendering and interaction clients; none implement their own scoring or parsing
- Contains: CLI router, quiz builder/server, study surface, day planner, session/agent interface, Anki export
- Key files: `cli.py` (command router), `quiz.py` (main rendering), `day.py` (cross-subject planner)
- Pattern: Each surface is independent; all call into model/runtime layers

**`tests/`:**
- Purpose: Integration-style roundtrip tests; verify end-to-end workflows
- Contains: Test modules for scoring, serving, day surface, agent session flow
- Naming: `*_roundtrip.py` pattern
- Usage: Run via pytest or python -m unittest

**`fixtures/`:**
- Purpose: Sample question banks, broken banks for error testing, sample configs
- Contains: `.md` files (banks and plans) and `.html` files (rendered outputs)
- Key files:
  - `sample_bank.md` — valid bank with multiple question types
  - `broken_bank.md` — invalid bank for testing lint errors
  - `sample_plan.md` — day plan table for testing day surface
  - `sample_lanes.md` — lanes/wiring config for testing day surface

**`.planning/`:**
- Purpose: Project documentation and planning
- Contains: Architecture, structure, conventions, testing patterns
- Location: `.planning/codebase/` for generated analysis docs

**`.github/`:**
- Purpose: GitHub-specific configuration
- Contains: Workflows, issue templates, CI/CD configuration

## Key File Locations

**Entry Points:**
- `itembank.py`: Root entry point; run as `python itembank.py <cmd>`
- `surfaces/cli.py:main()`: Command parser and router; called from itembank.py

**Core Logic:**
- `model.py`: Parsing and validation (300+ lines)
- `runtime.py`: Scoring, sessions, data control (260+ lines)
- `server.py`: HTTP server abstraction (50+ lines)

**Surfaces:**
- `surfaces/quiz.py`: Quiz rendering and serve graded sitting
- `surfaces/session.py`: JSON session interface for agents
- `surfaces/day.py`: Day planner with lane tracking
- `surfaces/study.py`: Flashcard and Learn surfaces
- `surfaces/anki.py`: Anki export
- `surfaces/cli.py`: Command line interface

**Configuration & Appearance:**
- `surfaces/quiz_page.py`: HTML template
- `surfaces/theme.py`: CSS theming

**Testing:**
- `tests/*.py`: Integration tests
- `fixtures/*.md`: Sample banks and configs

**Documentation:**
- `README.md`: User guide and usage examples
- `GRADING.md`: Manual grading rubric for short answers
- `ROADMAP.md`: Future plans

## Naming Conventions

**Files:**
- Surface files: `<surface_name>.py` (e.g., `quiz.py`, `study.py`, `day.py`)
- Command handlers: `cmd_<command_name>()` (e.g., `cmd_build()`, `cmd_serve()`, `cmd_start()`)
- Test files: `<feature>_roundtrip.py` (e.g., `scoring_roundtrip.py`)
- Data files: Lowercase with underscores or hyphens (e.g., `sample_bank.md`, `sample_plan.md`)

**Directories:**
- Core modules: Root level (model.py, runtime.py, server.py)
- Renderers: `surfaces/` subdirectory
- Tests: `tests/` subdirectory
- Sample data: `fixtures/` subdirectory

**Functions:**
- Public CLI commands: `cmd_<command>()` (exported from surface modules)
- Parsing: `parse_<thing>()` (e.g., `parse_bank()`, `parse_question()`, `parse_plan()`)
- Validation: `lint()` (returns errors and warnings)
- Scoring: `score_<thing>()` (e.g., `score_response()`)
- Reading/Writing: `read_<thing>()`, `write_<thing>()` (e.g., `read_session()`, `write_session()`)
- Building payloads: `<thing>_payload()` or `<thing>_item()` (e.g., `explain_payload()`, `public_item()`)

**Variables:**
- Question dicts: `q` or `qs` (list of dicts)
- Session dicts: `data` or `session`
- Error/warning lists: `errors`, `warnings`
- Counter objects: `counts`, `objs`, `diff`, `pos`, etc.

**Types:**
- Questions: Plain dicts with keys like `id, type, stem, opts, correct, da, why, etc.`
- Sessions: Plain dicts with keys like `session_id, items, cursor, responses, status, etc.`
- Attempts: Markdown files with human-readable format

## Where to Add New Code

**New Question Type:**
1. Add parsing logic to `model.py:parse_question()` — regex extraction for new fields
2. Add lint validation to `model.py:lint()` — check required fields and relationships
3. Add to `SPEC` in `model.py` — document format for authoring agents
4. Add scoring logic to `runtime.py:canonical_response()` and `canonical_key()` — how to compare responses
5. Add rendering to `runtime.py:public_item()` and `explain_payload()` — what learner sees
6. Add to each surface that renders items (quiz, study, day, etc.) — if visual changes needed

**New Surface:**
1. Create `surfaces/<surface_name>.py`
2. Implement `cmd_<command_name>(args)` function
3. Import in `surfaces/cli.py`
4. Add parser and set `fn=cmd_<command_name>` in `surfaces/cli.py:main()`
5. Call into model/runtime layers; don't duplicate parsing or scoring
6. If needs browser: subclass `server.Handler` and call `server.bind()`

**New Command:**
1. If internal to existing surface, add `cmd_<command>()` to that surface
2. If new behavior: create new surface file per "New Surface" above
3. Add argparse subcommand in `surfaces/cli.py:main()`
4. Command may load bank via `model.load()`, validate via `model.lint()`, score via `runtime.score_response()`

**New Output Format:**
1. For HTML rendering: edit `surfaces/quiz_page.py` (template) or create new template
2. For Anki: extend `surfaces/anki.py` export logic
3. For plain text: add to surface that's closest (study, session, etc.)
4. For markdown: follow attempt file pattern in `surfaces/quiz.py:attempt_markdown()`

**Utility/Helper Function:**
- If stateless data transformation: add to appropriate layer (model, runtime)
- If test-only: add to `tests/` directory
- If used by multiple surfaces: consider adding to runtime layer for reuse

## Special Directories

**`_attempts/`:**
- Purpose: Generated, not committed
- Contains: Session JSON files (`session_*.json`) and attempt markdown files (`*_attempt_*.md`)
- Generated: By `surfaces/session.py:cmd_start()` and `surfaces/quiz.py:cmd_serve()`
- Committed: No; listed in `.gitignore`

**`__pycache__/`:**
- Purpose: Python bytecode cache
- Generated: Automatically by Python on import
- Committed: No; listed in `.gitignore`

**`.planning/`:**
- Purpose: Project documentation and planning
- Contains: Generated architecture/structure/conventions docs
- Committed: Yes; useful for onboarding and future refactors

**`.github/`:**
- Purpose: GitHub workflow and CI/CD
- Contains: Actions, branch protection rules, PR templates
- Committed: Yes

## Module Import Structure

```
itembank.py
  ├─ model.py (BANK_FILE_HINTS, LETTERS, SPEC, grab, lint, load, notes, parse_bank, parse_question, section)
  ├─ runtime.py (FIELD_SEP, PAIR_SEP, SESSION_VERSION, answer_text, canonical_key, canonical_response, 
  │             explain_payload, normalize_answer, page_item, public_item, read_session, response_text, 
  │             score_response, session_path, session_summary, session_view, write_session)
  └─ surfaces/cli.py:main
      ├─ model.py (BANK_FILE_HINTS, SPEC, lint, load, parse_bank)
      ├─ surfaces/anki.py:cmd_export
      ├─ surfaces/day.py:cmd_day
      ├─ surfaces/quiz.py:cmd_build, cmd_serve
      ├─ surfaces/session.py:cmd_next, cmd_report, cmd_start, cmd_submit
      └─ surfaces/study.py:cmd_study
```

Each surface is a thin client. All import model/runtime as needed. No surface imports another surface.

---

*Structure analysis: 2026-08-05*
