# External Integrations

**Analysis Date:** 2026-08-05

## APIs & External Services

**Anki Desktop:**
- Service: AnkiConnect (addon running in Anki Desktop)
- What it's used for: Read deck names, card counts (due/new), and sync status for the `day` surface
- SDK/Client: Python `urllib.request` (built-in standard library)
- Auth: None (local connection only)
- URL: Default `http://127.0.0.1:8765`
  - Override via `ANKI_CONNECT_URL` environment variable
  - Queries `http://127.0.0.1:8765` by default; also checks addon port registry on first failure
- Request format: JSON-RPC via POST (action, version, params)
- Error handling: Graceful - if Anki is closed, deck counts are omitted with a note; no failure
- Location: `surfaces/day.py` - Functions `anki_read()`, `_anki_post()`, `_anki_addon_port()`

## Data Storage

**Databases:**
- None. This is a local-first tool with no server-side storage.

**File Storage:**
- Markdown files for question banks (read-only from tool perspective)
  - Bank files: User provides; tool parses and validates but does not modify
  - Fixtures: `fixtures/sample_bank.md`, `fixtures/broken_bank.md` for testing
- JSON session files (read-write) for resumable assessments
  - Location: User-specified directory; defaults to current working directory
  - Schema version: `SESSION_VERSION = 1` in `runtime.py`
  - Example: `session.json` created by `itembank start`, updated by `itembank submit`
- Markdown log files for daily work tracking (write-only from tool perspective)
  - Created alongside plan file by default as `log.md`
  - One row per day, ticked lanes recorded immediately on UI checkbox
  - Location: `surfaces/day.py` - Functions `load_day_log()`, `write_day_log()`
- TSV export files for Anki import
  - Formats: Basic (question|answer), Cloze (text with cloze markers)
  - Location: User-specified via `itembank export BANK.md OUT.tsv --format [basic|cloze]`

**Caching:**
- None. Every invocation reads fresh from disk.

## Authentication & Identity

**Auth Provider:**
- None. This tool has no user accounts, logins, or multi-user support.
- All data is local; nothing is sent to a remote server.

**Security Model:**
- Browser-based quiz (`itembank build`): Offline, self-contained HTML file holding the full answer key
- Server-based quiz (`itembank serve`): Local loopback server (127.0.0.1) only; no external access
- Session files (`itembank start/next/submit`): Plain JSON files on disk; no encryption
- Day surface: Reads local markdown files; optional git status check; optional AnkiConnect (local only)

## Monitoring & Observability

**Error Tracking:**
- None. Errors are printed to stderr and exit with non-zero code.
- No error reporting service or remote logging.

**Logs:**
- CLI: Output to stdout/stderr (progress, warnings, errors)
- Sessions: JSON attempt records stored as session files (human-readable)
- Day surface: Markdown log file written beside plan (one row per day, ticked lanes, computed behind/load)
- No structured logging framework or log aggregation

## CI/CD & Deployment

**Hosting:**
- Not applicable. This is a local tool, not a service.

**CI Pipeline:**
- GitHub Actions (`.github/workflows/ci.yml`)
- Triggered on: push, pull_request to any branch
- Runs on: `ubuntu-latest` with Python 3.11
- Steps:
  1. Lint sample fixture (`python itembank.py lint fixtures/sample_bank.md`)
  2. Verify broken fixture is caught (linter rejects it)
  3. Build sample fixture to HTML (`python itembank.py build`)
  4. Run all test files in `tests/` directory
  5. Guard check: Fail if a real question bank was committed

## Environment Configuration

**Required env vars:**
- None. Tool runs without any environment variables.

**Optional env vars:**
- `ANKI_CONNECT_URL` - Override default AnkiConnect URL
  - Default: `http://127.0.0.1:8765`
  - Use case: Non-standard Anki addon port
  - Location: `surfaces/day.py` line 375

**Platform-specific defaults:**
- `APPDATA` (Windows): Used to find Anki profile location (falls back to `~/AppData/Roaming`)
- `XDG_DATA_HOME` (Linux/macOS): Used to find Anki profile location (falls back to `~/.local/share`)

**Secrets location:**
- Not applicable. No secrets used.

## Webhooks & Callbacks

**Incoming:**
- HTTP POST endpoint in `itembank serve` and `itembank day --lan`
  - Receives form submissions from browser quiz or day surface
  - Handler: `Handler` class in `server.py` (subclassed by surfaces)
  - Endpoint: `POST /submit` (quiz), `POST /action` (day)
- No external webhooks; all endpoints are local loopback (127.0.0.1)

**Outgoing:**
- Git status check (subprocess call, not a webhook)
  - Command: `git status --porcelain` in lane repo
  - Location: `surfaces/day.py` - Function `git_changes()`
  - Purpose: Show evidence dot if lane's file was modified today
- Open file in editor/browser (subprocess call)
  - Commands: `open` (macOS), `xdg-open` (Linux)
  - Purpose: Allow user to open notes file from day surface UI
- No outbound network calls except optional AnkiConnect (local)

## External Tool Dependencies

**Git (optional):**
- Used by: `day` surface for evidence tracking
- Integration: Subprocess call to `git status --porcelain`
- Purpose: Detect if a lane's notes file was modified in git history today
- Fallback: If git not found or repo missing, evidence dot is simply not shown (degraded, not broken)
- Location: `surfaces/day.py` - Function `git_changes()`

**Markdown Parser:**
- Not applicable. Tool uses regex-based parsing, not a markdown library.

**Browser (implicit):**
- Used by: `itembank build` (offline HTML file, user opens in browser), `itembank serve` (local HTTP server, browser connects)
- Integration: User manually opens file or URL; tool serves HTML and accepts form submissions
- No WebSocket or real-time communication; standard HTTP only

## Integration Points Summary

| Service | Required | Type | Failure Mode |
|---------|----------|------|--------------|
| Anki Desktop + AnkiConnect | No | HTTP (local) | Graceful - deck counts omitted with note |
| Git (for status) | No | Subprocess | Graceful - evidence dot not shown |
| Browser (for UI surfaces) | No (CLI surfaces work without) | HTTP (local) | N/A - user initiates |

---

*Integration audit: 2026-08-05*
