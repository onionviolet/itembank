<!-- generated-by: gsd-doc-writer -->
# Architecture

## System overview

Itembank is a local-first, layered Python application. It accepts plain Markdown learning artifacts, parses and validates them once, runs assessment sessions through one authoritative scorer, records evidence on disk, and presents the results through CLI, browser, export, and desktop surfaces.

## Component diagram

```text
Markdown banks and course artifacts
                |
                v
          model.py parser
                |
                v
       runtime.py session and scorer
          |          |          |
          v          v          v
      evidence.py  server.py  selection.py
          |          |          |
          +----------+----------+
                     |
                     v
        CLI, browser, export, desktop
```

`model.py` is the only bank parser. `runtime.py` is the only settled assessment authority. Surfaces call those layers instead of duplicating parsing or scoring decisions.

## Data flow

1. `itembank.py` dispatches a command to the CLI surface.
2. `model.py` loads and validates the selected bank or course artifact.
3. `runtime.py` creates or advances an assessment session and calls `score_response` for deterministic item types.
4. `evidence.py` appends local evidence. Short prose responses remain pending until reviewed.
5. A surface renders only the content that the runtime permits for the current feedback tier.

## Key abstractions

| Area | Authority | Location |
|---|---|---|
| Bank grammar and validation | Parsing and lint errors | `model.py` |
| Assessment runtime | Session state, scoring, keyed disclosure | `runtime.py` |
| Evidence | Append-only local learning evidence | `evidence.py` |
| Selection | Deterministic item selection | `selection.py` |
| HTTP transport | Loopback request handling | `server.py` |
| Presentation | CLI, quiz, lesson, study, and desktop clients | `surfaces/` |
| Published contracts | JSON payload schemas | `schemas/` |

## Directory structure rationale

```text
fixtures/      Synthetic banks and test inputs
schemas/       Published JSON contracts
surfaces/      Presentation clients with no scoring authority
tests/         Self-contained Python roundtrip tests and JS UI tests
scripts/       Preflight, build, and maintenance commands
src-tauri/     Desktop shell
.planning/     Product intent, requirements, plans, and accepted decisions
```

The boundaries are deliberate. Changes that require a second parser, a second scorer, hosted learner evidence, or early answer-key disclosure violate the project contract.
