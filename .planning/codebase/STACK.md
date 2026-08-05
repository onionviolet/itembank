# Technology Stack

**Analysis Date:** 2026-08-05

## Languages

**Primary:**
- Python 3 (3.11+) - All application logic, tooling, and tests

**No Secondary Languages:**
- Standard library only. No Node.js, JavaScript, compiled languages, or external runtimes.

## Runtime

**Environment:**
- Python 3.11+ (tested explicitly in CI via `actions/setup-python@v5`)
- Available on Linux, macOS, Windows

**Package Manager:**
- None required - Standard library only, no external dependencies
- Lockfile: Not applicable

## Frameworks

**Core:**
- Python standard library only: `json`, `re`, `os`, `sys`, `collections`, `argparse`, `html`
- `http.server` (BaseHTTPRequestHandler, TCPServer) - Loopback server for browser surfaces
- `socketserver.TCPServer` - HTTP server binding with OS port fallback (for Windows Hyper-V compatibility)
- `random` - Used for shuffling build-type question steps in rendering

**Testing:**
- Python unittest/subprocess-based - See `tests/` directory
- Test runner: Direct Python script execution (no pytest, unittest framework, or test runner dependency)

**Build/Dev:**
- No build system - Direct Python execution
- GitHub Actions (CI/CD) - For automated test runs on push/PR

## Key Dependencies

**None.**

The tool explicitly states in its docstring and README: "Python standard library only. No network, no services, no dependencies, and no install step: `python itembank.py` from a checkout is the whole thing."

Every import in the codebase is from the Python standard library:
- `itembank.py`: imports from `model`, `runtime`, `surfaces` (internal modules)
- `model.py`: uses `collections`, `re`, `sys`
- `runtime.py`: uses `collections`, `json`, `os`, `sys`
- `server.py`: uses `http.server`, `json`, `socketserver`
- All surfaces (`surfaces/*.py`): use only standard library modules
- Tests (`tests/*.py`): use subprocess, urllib, json, tempfile, threading, time (all standard)

## Configuration

**Environment:**
- No `.env` file or environment file required
- Optional environment variable: `ANKI_CONNECT_URL` - Allows overriding default AnkiConnect URL (see INTEGRATIONS.md)
- Platform-specific defaults: Uses `APPDATA` on Windows, `XDG_DATA_HOME` on Linux/macOS for Anki profile location

**Build:**
- No build configuration files (no `setup.py`, `pyproject.toml`, `requirements.txt`)
- CI configuration: `.github/workflows/ci.yml` - Runs linting, builds, and test suite on push/PR

## Platform Requirements

**Development:**
- Python 3.11+ interpreter
- Read/write access to local filesystem for markdown banks, session files, and logs
- Git (optional, for `git status` integration in day surface)
- Anki Desktop (optional, for deck tracking via AnkiConnect)

**Production:**
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

---

*Stack analysis: 2026-08-05*
