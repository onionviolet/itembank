# Codebase Concerns

**Analysis Date:** 2026-08-05

## Tech Debt

**File I/O error handling:**
- Issue: Multiple `open()` calls use direct method chaining (`open(path).read()`) without context managers, losing the ability to provide precise error context if the file doesn't exist or is unreadable
- Files: `model.py:307`, `surfaces/cli.py:72`, `surfaces/quiz.py:18`, `surfaces/study.py:50`
- Impact: When a file operation fails, the error message is generic (e.g., "no such file") rather than identifying which specific operation failed or what it was trying to do
- Fix approach: Wrap file operations in try-except blocks or use explicit context managers (`with open(...) as fh:`) to provide better error messages that identify the operation context

**Overly broad exception handling:**
- Issue: Multiple functions catch all exceptions with `except Exception:` which silently swallows errors that may indicate real problems
- Files: `surfaces/day.py:393-394` (anki_read), `surfaces/day.py:417-418` (touched_today), `surfaces/cli.py:73-74` (cmd_guard)
- Impact: Real errors (network issues, permissions problems, malformed data) are hidden, making debugging difficult. Anki failures are intentional by design but git subprocess and guard command errors are obscured
- Fix approach: Catch specific exception types (`IOError`, `OSError`, `json.JSONDecodeError`, `subprocess.TimeoutExpired`) and only catch `Exception` for truly expected degradation paths; add logging for suppressed errors in non-degradation contexts

**Non-atomic file writes:**
- Issue: Several modules write files without atomic operations (tmp + replace pattern). Direct writes to final location can leave partial files if interrupted
- Files: `surfaces/quiz.py:49`, `surfaces/quiz.py:172`, `surfaces/day.py:482`, `surfaces/study.py:55`, `surfaces/anki.py:41`
- Impact: If a process is killed during a file write, the attempt file or quiz output could be corrupted or incomplete. Only `runtime.py:147-150` uses atomic writes with `os.replace()`
- Fix approach: Use the `write_session` pattern everywhere: write to a temp file, then atomically replace with `os.replace()`

**Unvalidated data type assumptions:**
- Issue: The code assumes specific shapes for nested dictionaries and lists without validation before access
- Files: `surfaces/day.py:864-866` (accessing `cache["info"]["lanes"][lane]["files"]`), `surfaces/day.py:780-787` (building lane info dict)
- Impact: If data structures get malformed, KeyErrors or IndexErrors will crash the surface instead of providing actionable error messages
- Fix approach: Add defensive checks before nested dict/list access; return sensible defaults rather than crashing

## Known Bugs

**Port fallback may still fail:**
- Symptoms: If port 0 assignment also fails (rare but possible under certain OS constraints), the tool crashes rather than exiting gracefully
- Files: `server.py:40-52`
- Trigger: Run on a system with very restrictive port binding policies
- Workaround: Manually specify a port with `--port <number>`; currently port 0 has no error handling

**Quiz page JSON injection vulnerability (client-side only):**
- Symptoms: The quiz page substitutes `__DATA__` with `json.dumps(items)`. If item stems or option text contain JSON-breaking characters, the page JavaScript could malfunction
- Files: `surfaces/quiz.py:32` (JSON injection into HTML template), `surfaces/quiz_page.py` (template)
- Trigger: Create a question stem containing `</script>` or `__DATA__` markers
- Workaround: The `json.dumps()` with `ensure_ascii=False` partially mitigates this, but the injection happens into a raw template string with no escaping of the JSON itself

## Security Considerations

**Subprocess calls allow command-line injection:**
- Risk: `touched_today()` builds subprocess arguments from user-controlled paths; `open_in_editor()` calls OS commands without escaping
- Files: `surfaces/day.py:403-419` (git subprocess), `surfaces/day.py:422-431` (os.startfile/Popen)
- Current mitigation: Git commands only pass paths via `-C` flag, not as string interpolation; `os.startfile` is Windows-specific and safer than Popen. Still, Popen on Linux/macOS passes paths unchecked to `xdg-open`
- Recommendations: Use `shlex.quote()` for the xdg-open path on Unix systems. Validate that file paths don't contain shell metacharacters before passing to subprocess

**Anki connection over localhost only:**
- Risk: AnkiConnect typically listens on 127.0.0.1:8765. If a user sets `ANKI_CONNECT_URL` to a remote URL, credentials or deck data could transit over network
- Files: `surfaces/day.py:370-395` (anki_read, hardcoded localhost fallback)
- Current mitigation: Default is localhost; README and config defaults don't mention remote URLs; the `_anki_addon_port()` discovery is local-only
- Recommendations: Validate that any `ANKI_CONNECT_URL` environment variable points to localhost or 127.0.0.1; warn if it doesn't

**File paths from wiring config allow traversal:**
- Risk: `resolve_notes()` expands `~` and absolute paths. A malicious wiring file could specify `../../../etc/passwd` or an absolute path outside the vault
- Files: `surfaces/day.py:227-242` (resolve_notes), `surfaces/day.py:245-280` (lane_files)
- Current mitigation: Only the user can edit lanes.md (not network-exposed); the server only opens files returned by `lane_files()`, not user-named paths
- Recommendations: Document that lanes.md should be treated as trusted; add an optional security check to reject paths outside the vault root (if vault root is defined)

## Performance Bottlenecks

**Anki due/new card counts recalculated on every day page load:**
- Problem: `day_info()` calls `anki_read()` which queries Anki for every deck on every page render, even if the page is refreshed within 60 seconds
- Files: `surfaces/day.py:737-788` (day_info), `surfaces/day.py:841-843` (render cache checks at 60s)
- Cause: Anki queries happen inside `day_info()` which is called on every render, but the cache only wraps the whole `day_info()` result, not individual Anki calls
- Improvement path: Cache Anki counts separately with a shorter TTL (e.g., 10 seconds), or batch the queries once per render

**Git log subprocess called on every day page render:**
- Problem: `touched_today()` runs `git log` and `git status` on every page load to check if lane files have changed
- Files: `surfaces/day.py:403-419`, called from `day_info()` at line 766
- Cause: Git queries are not cached and run synchronously, blocking page render
- Improvement path: Cache results with a ~30-second TTL; consider running asynchronously if page render time becomes critical

**Regex patterns compiled inline on every call:**
- Problem: Multiple regex patterns (`NONE_CELL`, `WOULD_BE`, `parse_day_date`) are compiled fresh on every invocation
- Files: `surfaces/day.py:41` (NONE_CELL compiled once at module level - good), `model.py:202-204` (WOULD_BE compiled once - good), but inline patterns in functions are recompiled every call
- Cause: Some regexes are used in hot paths like `lane_behind()` and `lane_load()` which run once per lane per page load
- Improvement path: Pre-compile all patterns at module level; this is already done for critical ones but inline patterns should be extracted

**Large day.py file (904 lines):**
- Problem: `day.py` is the largest file in the codebase and combines wiring parsing, git operations, Anki integration, HTML generation, and the day surface server
- Files: `surfaces/day.py` (904 lines total)
- Cause: The day surface is complex and touches many systems; splitting it would help but might break the intentional boundaries
- Improvement path: Consider extracting Anki integration (`_anki_addon_port`, `_anki_post`, `anki_read`) and git operations (`touched_today`) into separate modules; keep the core day surface logic together

## Fragile Areas

**JSON session file format has no version evolution strategy:**
- Files: `runtime.py:20` (SESSION_VERSION = 1), `runtime.py:138-139`
- Why fragile: If the session schema needs to change (e.g., add a new field), old session files will fail to load. The version check is present but there's no migration logic
- Safe modification: Before changing the schema, implement a migration function that reads old versions and upgrades them, or implement a compatibility layer that provides sensible defaults for missing fields
- Test coverage: `tests/serve_roundtrip.py` tests session round-trips but not version evolution

**Day log format depends on header row parsing:**
- Files: `surfaces/day.py:434-457` (load_day_log), `surfaces/day.py:468-482` (write_day_log)
- Why fragile: The log reader maps columns by header row; if a user manually edits the log and removes a lane name from the header, ticks for that lane will be misassigned
- Safe modification: Add validation that header names match known `DAY_LANES`; reject logs with unrecognized lane names rather than silently dropping them
- Test coverage: `tests/due_roundtrip.py:107-119` tests old log reading but not invalid/corrupted headers

**Wiring parser depends on table structure detection:**
- Files: `surfaces/day.py:122-187` (parse_lanes), `surfaces/day.py:144-186` (table detection by header keywords)
- Why fragile: Lane wiring is detected by searching for "lane" in lowercase header text. If a document contains an unrelated table with "lane" in a header, it could be misinterpreted as wiring
- Safe modification: Require a stricter format (e.g., first column must be literally "Lane", second must be a specific fixed set of names like "Anki deck"/"Notes file"); or use a marker like `<!-- lanes.md wiring -->` 
- Test coverage: `tests/due_roundtrip.py:36-53` tests a valid wiring but not edge cases of malformed tables

**Plan date parsing accepts multiple formats:**
- Files: `surfaces/day.py:51-68` (parse_day_date)
- Why fragile: Regex matches "Mon Jul 27", "Jul 27", "27 Jul", "2026-07-29", and variations. A plan row like "July 4th order supplies" could accidentally parse as a date
- Safe modification: Tighten the regex or require a fixed format (ISO date only); document the ambiguity in README
- Test coverage: Tests exist for valid dates but not false positives

**Quiz page relies on client-side canonical form computation:**
- Files: `surfaces/quiz_page.py:135-142` (canon() function), `runtime.py:66-96` (canonical_response())
- Why fragile: The JavaScript `canon()` and Python `canonical_response()` must stay in sync. If one is updated and not the other, offline quiz files will score incorrectly
- Safe modification: Extract the canonical form logic into a shared test fixture; test that both implementations produce identical output for the same inputs
- Test coverage: `tests/scoring_roundtrip.py` tests the Python scorer but not the JavaScript version

## Scaling Limits

**Anki deck querying is single-threaded:**
- Current capacity: For 6 lanes, `anki_read()` makes 12+ queries to Anki (deckNames + 2 queries per deck for due/new). On a slow Anki instance, this could take 5+ seconds
- Limit: If lanes scale to 20+ decks, page load time becomes unacceptable
- Scaling path: Batch Anki queries into a single call; parallelize with threads or async; or cache more aggressively

**Session file rewrite on every answer:**
- Current capacity: The attempt file is rewritten in full on every answer (quiz.py:172), and the session file is rewritten on every submit (session.py:63)
- Limit: For a 100-item test with frequent saves, this could cause disk I/O bottleneck on slow storage
- Scaling path: Use `fsync()` for durability guarantees instead of full rewrites; consider SQLite for large session batches

**Plan parsing reads entire file into memory:**
- Current capacity: The plan file is read line-by-line, which is fine for typical plans (~100-500 rows)
- Limit: A plan file with 10,000+ dated rows would be slow to parse
- Scaling path: Index by date; use lazy parsing if plans grow very large

## Dependencies at Risk

**No external dependencies - risk is minimal:**
- The codebase uses only Python standard library (json, re, os, sys, http.server, subprocess, urllib, etc.)
- Risk: If a future feature requires (e.g., PDF export, advanced markdown parsing), dependencies will need to be added carefully
- Impact: Currently no risk
- Migration plan: N/A

## Missing Critical Features

**No conflict handling for concurrent day ticks:**
- Problem: If two browser tabs open the same day surface and tick different lanes, the second tab's save will overwrite the first. The log file acts as a single writer, not a locking mechanism
- Blocks: Multi-device or multi-user access to the same day surface
- Workaround: Only open one tab at a time; close and re-open if the page reloads

**No undo capability for quiz/session responses:**
- Problem: Once an answer is submitted in a quiz, it is recorded. There is no way to unsee the explanation or change a response
- Blocks: Self-marked quizzes where the user realizes they misclicked
- Workaround: Re-run the session or manually edit the attempt markdown file

**No support for question pooling or randomization at the bank level:**
- Problem: Sessions use a fixed random seed and shuffle from the same items on every run. There's no support for a pool of questions where each sitting draws a random subset (like a real exam)
- Blocks: Using the same bank for both practice and high-stakes assessment
- Workaround: Create separate banks for each test instance

**No support for time limits or pacing constraints:**
- Problem: Quizzes and sessions have no time tracking or per-item time limits
- Blocks: Exam-style testing where speed matters, or timed remediation
- Workaround: Manually track time with an external timer

## Test Coverage Gaps

**No test of JavaScript scoring logic:**
- What's not tested: The `canon()` function in `surfaces/quiz_page.py:135-142` (client-side canonical form)
- Files: `surfaces/quiz_page.py`, no corresponding test
- Risk: If the JavaScript logic diverges from Python `canonical_response()`, offline quizzes will score incorrectly without warning
- Priority: High - This is a security-critical path (the one place a learner-facing surface computes a verdict)

**No test of concurrent writes to day log:**
- What's not tested: If two processes write the day log simultaneously, race conditions could corrupt it
- Files: `surfaces/day.py:875` (write_day_log called from POST handler)
- Risk: On a machine with slow disk I/O or if the page is opened in multiple tabs and submitted rapidly, the log could lose ticks or become malformed
- Priority: Medium - Unlikely in single-user scenarios but possible under load

**No test of malformed session JSON:**
- What's not tested: What happens if a user manually corrupts the session JSON file (missing fields, wrong types)
- Files: `runtime.py:135-140` (read_session), `surfaces/session.py:40-74`
- Risk: The code will crash with a KeyError or TypeError instead of providing a helpful error message
- Priority: Medium - Users might manually edit or partial-transfer session files

**No test of wiring file with mixed encodings:**
- What's not tested: What if lanes.md is UTF-8 but contains a Windows ANSI-encoded line?
- Files: `surfaces/day.py:95` (line-by-line read), `surfaces/day.py:133` (table parsing)
- Risk: Malformed characters could cause regex failures or silent misparses
- Priority: Low - UTF-8 is standard but could happen with legacy documents

**No test of bank file with invalid UTF-8:**
- What's not tested: What if a bank markdown file is partially corrupted with invalid UTF-8 bytes?
- Files: `model.py:307` (open with UTF-8 encoding)
- Risk: Python will raise UnicodeDecodeError, crashing with a cryptic message
- Priority: Low - Corruption is rare but error message should be friendlier

**No test of quiz page with very long item stems:**
- What's not tested: HTML generation for items with stems >10,000 characters, or with many options (>8)
- Files: `surfaces/quiz_page.py` (template generation), `surfaces/quiz.py:24` (page_item call)
- Risk: Page could become slow or options layout could break
- Priority: Low - Format spec limits options to A-H; stems are typically a few hundred chars

---

*Concerns audit: 2026-08-05*
