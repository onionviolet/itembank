# Coding Conventions

**Analysis Date:** 2026-08-05

## Naming Patterns

**Files:**
- Module files are snake_case: `model.py`, `runtime.py`, `server.py`, `itembank.py`
- Surface modules in `surfaces/` follow same pattern: `cli.py`, `quiz.py`, `session.py`, `study.py`, `day.py`, `anki.py`
- Test files use `*_roundtrip.py` pattern: `scoring_roundtrip.py`, `day_roundtrip.py`, `serve_roundtrip.py`, `agent_roundtrip.py`
- Executable Python files have shebang: `#!/usr/bin/env python3`

**Functions:**
- Regular functions use snake_case: `parse_bank()`, `canonical_response()`, `score_response()`, `public_item()`, `session_view()`
- Command handlers use `cmd_` prefix: `cmd_spec()`, `cmd_lint()`, `cmd_build()`, `cmd_serve()`, `cmd_start()`, `cmd_next()`, `cmd_submit()`, `cmd_day()`, `cmd_guard()`, `cmd_study()`, `cmd_export()`
- No private functions (underscore prefixes) — all module-level functions are importable
- Helper functions are prefixed by purpose: `page_for()`, `served_items()`, `check_*()` in tests

**Variables:**
- All variables use snake_case: `seen_stems`, `letter_hits`, `correct_answer`, `wrong_answer`, `session_data`
- Dictionary keys use quotes for compound names: `"schema_version"`, `"correct_analysis"`, `"auto_correct"`
- Loop variables single letter when obvious: `for q in qs`, `for L in LETTERS`, `for i, r in enumerate(questions)`

**Types/Constants:**
- Module-level constants in UPPERCASE: `LETTERS = "ABCDEFGH"`, `SESSION_VERSION = 1`, `FIELD_SEP = "\x1f"`, `PAIR_SEP = "\x1e"`
- Regex patterns stored as module constants: `WOULD_BE = re.compile(...)`
- File name hints stored as tuples: `BANK_FILE_HINTS = ("_mc_bank", "_exam_bank", ...)`

## Code Style

**Formatting:**
- No linter or formatter configured — code is manually formatted
- Indentation: 4 spaces (standard Python)
- Line continuation: Implicit inside parentheses without backslashes
- Long regex patterns broken across lines with implicit string concatenation or raw string literals: `r"pattern1" r"pattern2"`
- String formatting: Uses `%` operator throughout: `"%d items, %d errors" % (len(qs), len(errors))`

**Linting:**
- No `.flake8`, `.pylintrc`, or `pyproject.toml` configuration
- No automatic linting — manual code review is the standard
- Standard library only — zero external dependencies by design

**Docstrings:**
- Module docstrings are comprehensive and explain design: See `itembank.py` for the four-layer architecture description
- Function docstrings are present for public APIs: `canonical_response()`, `score_response()`, `page_item()`
- Docstrings explain WHY and WHAT, not HOW
- Example from `runtime.py`: docstrings explain the invariant that one scorer exists everywhere

## Import Organization

**Order:**
1. Standard library imports (grouped): `import collections, re, sys`
2. Then: `import json, os, sys`
3. Relative imports from project: `from model import BANK_FILE_HINTS, SPEC, grab, lint, load`
4. Relative imports from other modules: `from runtime import explain_payload, page_item, response_text, score_response`
5. Late imports (deferred to reduce startup cost) done inside functions: `import random, uuid` inside `cmd_start()`, `import random` inside `public_item()`

**Example from `surfaces/cli.py`:**
```python
import argparse, collections, os, sys

from model import BANK_FILE_HINTS, SPEC, lint, load, parse_bank
from surfaces.anki import cmd_export
from surfaces.day import cmd_day
from surfaces.quiz import cmd_build, cmd_serve
```

**Path Aliases:**
- No path aliases configured — all imports are explicit relative or standard library

## Error Handling

**Patterns:**
- CLI errors use direct `sys.exit(message)` with human-readable messages: `sys.exit("cannot read session %s: %s" % (path, exc))`
- Early returns with meaningful values: None for constructed response (no canonical form), empty string for missing data
- Validation errors accumulated in lists and returned: `lint()` returns `(errors, warnings)` tuples
- Exception handling only for file I/O and JSON parsing:
  ```python
  try:
      data = json.load(open(session_path(path), encoding="utf-8"))
  except (OSError, ValueError) as exc:
      sys.exit("cannot read session %s: %s" % (path, exc))
  ```

**Pattern: Fail Early in Tests**
- Test helper function `fail(msg)` prints "FAIL: " prefix and exits with code 1
- Used throughout test files: `if not qs: fail("fixture bank parsed to nothing")`

## Logging

**Framework:** `print()` only — no logging library

**Patterns:**
- Status lines printed to stdout: `print("%d items -> %s" % (len(qs), out))`
- Error messages on stderr via `sys.exit()` — forces non-zero exit
- JSON results printed with proper formatting: `print(json.dumps(result, ensure_ascii=False, indent=2))`
- Progress indicators printed while running: `print("   mix: " + mix)`, `print("   note: ...")`

## Comments

**When to Comment:**
- Design decisions and invariants are documented at module level
- Function-level comments explain WHY when it's non-obvious
- Inline comments explain tricky regex or complex business logic
- Example: `# The static page's key and the scorer's key are the same value, or the offline surface silently disagrees with every other one.`

**Comment Style:**
- Block comments start with `# ` and are complete sentences
- No JSDoc/docstring style for functions — docstrings use plain sentences instead
- Comments often reference the file/design invariant: `# One scorer, structurally, across every module rather than in the one file that happens to hold it today.`

## Function Design

**Size:** Functions are kept small and focused on one job: `grab()` extracts one regex group, `canonical_response()` normalizes one type of answer

**Parameters:**
- Functions accept question dicts directly: `def score_response(q, answer)`
- Optional parameters use defaults: `def public_item(q, shuffle_seed=0)`
- Command handlers receive argparse Namespace: `def cmd_build(a)` where `a` is the parsed args

**Return Values:**
- Functions return dicts for structured data: `public_item()` returns item dict with `"id"`, `"stem"`, `"options"`, etc.
- Validation returns tuples: `lint()` returns `(errors, warnings)`
- Boolean None is used for unknown/pending: short answer scoring returns `None` (not yet marked), not `False`
- Empty strings for missing/invalid data: `grab()` returns `""` when pattern doesn't match

## Module Design

**Exports:**
- Explicit `__all__` list in `itembank.py` for the public surface: Lists 29 exported items
- No `__all__` in internal modules — everything at module level is importable
- Pattern: Surfaces import what they need directly, don't use * imports

**Barrel Files:**
- No barrel files (index.py pattern)
- Direct imports are preferred: `from model import parse_bank` not `from model import *`

**Module Organization:**
- `model.py`: Format contract, parsing, validation
- `runtime.py`: Scoring (the only scorer), sessions, public/private item payloads
- `server.py`: Single loopback HTTP server
- `surfaces/*`: UI clients (CLI, quiz HTML, study HTML, day page, JSON sessions, Anki export)

## Dictionaries and Data Shapes

**Question Dicts:**
All question dicts have these keys:
```python
common = {
    "id": "q" + number,
    "number": int(number),
    "type": qtype,  # "mc", "multi", "table", "dnd", "build", "short"
    "stem": stem,
    "difficulty": grab(...),
    "objective": grab(...),
    "why": section("WHY BEST", ch),
    "disc": section("KEY DISCRIMINATOR", ch),
    "second": section("SECOND-BEST", ch),
    "trap": section("TRAP", ch),
    "conf": grab(...),
}
```
Type-specific fields added to common dict, never in separate structures.

**Session Dicts:**
```python
data = {
    "schema_version": SESSION_VERSION,
    "session_id": uuid.uuid4().hex,
    "bank": os.path.abspath(a.bank),
    "items": items,  # List of question indices
    "cursor": 0,
    "responses": [],
    "status": "active",  # or "complete"
    "mode": a.mode,
    "objective": a.objective or "",
    "seed": a.seed
}
```

## String Constants

**Separators (Control Characters):**
- `FIELD_SEP = "\x1f"` — separates fields in canonical form (not visible punctuation)
- `PAIR_SEP = "\x1e"` — separates key-value pairs
- Used instead of `|`, `>`, `,` because content contains those characters

**Question Types:**
- `"mc"` — multiple choice, pick one
- `"multi"` — multiple response, pick N
- `"table"` — categorize rows
- `"dnd"` — drag and drop, same as table but shuffled display
- `"build"` — ordering, put steps in sequence
- `"short"` — constructed response, human marked

---

*Convention analysis: 2026-08-05*
