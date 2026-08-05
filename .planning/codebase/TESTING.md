# Testing Patterns

**Analysis Date:** 2026-08-05

## Test Framework

**Runner:**
- No test framework (no pytest, unittest, or nose)
- Tests are executable Python scripts in `tests/` directory: `scoring_roundtrip.py`, `day_roundtrip.py`, `serve_roundtrip.py`, `agent_roundtrip.py`, `surface_roundtrip.py`, `due_roundtrip.py`
- Standard library only — no test dependencies
- Run tests with: `python tests/scoring_roundtrip.py`

**Assertion Library:**
- No assertion library — tests use plain `if` statements with a `fail()` helper

**Run Commands:**
```bash
python tests/scoring_roundtrip.py       # Test that one scorer exists everywhere
python tests/day_roundtrip.py           # Test plan parsing, floor logic, streak tracking
python tests/serve_roundtrip.py         # Test that process scores and records answers
python tests/agent_roundtrip.py         # Test JSON session interface
python tests/surface_roundtrip.py       # Test basic surface contract
python tests/due_roundtrip.py           # Test outstanding items tracking
```

All tests exit with code 0 on success, non-zero on failure.

## Test File Organization

**Location:**
- Tests co-located in `tests/` directory (separate from source)
- Fixtures stored in `fixtures/` directory: `sample_bank.md`, `sample_plan.md`

**Naming:**
- Pattern: `<concept>_roundtrip.py`
- "Roundtrip" indicates the test exercises a complete cycle (read-process-write or read-check)

**Structure:**
```
tests/
├── agent_roundtrip.py       # JSON session contract
├── day_roundtrip.py         # Plan parser, floor lanes, ticks, streak
├── due_roundtrip.py         # Outstanding items across lanes
├── scoring_roundtrip.py     # One scorer invariant
├── serve_roundtrip.py       # HTTP scoring and persistence
├── surface_roundtrip.py     # Basic CLI
```

## Test Structure

**Suite Organization:**
Tests are single-file suites with multiple check functions and one `main()`:

```python
def check_parser():
    plan = itembank.parse_plan(PLAN, 2026)
    if "2026-01-05" not in plan:
        fail("`**Mon Jan 5**` did not parse into a dated row.")

def check_floor():
    if itembank.day_status(set(itembank.FLOOR_LANES)) != "floor":
        fail("the floor lanes alone did not produce a floor day")

def main():
    check_parser()
    check_floor()
    check_streak_ignores_unfinished_today()
    check_server()
    print("PASS: plan parsed, floor honored, ticks round-tripped to disk")

if __name__ == "__main__":
    sys.exit(main() or 0)
```

**Patterns:**
- Setup: Paths to fixtures set at module level: `ROOT = Path(__file__).resolve().parents[1]`, `BANK = ROOT / "fixtures" / "sample_bank.md"`
- Helper: `fail(msg)` function that prints "FAIL: " prefix and exits with code 1
- Teardown: Tests clean up temp files (e.g., `tempfile.mkdtemp()`) — OS removes temp dir on exit

## Mocking

**Framework:** No mocking — tests run real code

**Patterns:**
- Subprocess spawning: Tests spawn the actual tool process to verify command-line contract
- Example from `day_roundtrip.py`:
  ```python
  proc = subprocess.Popen(
      [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "day", PLAN,
       "--no-open", "--port", "0", "--log", log_path, "--date", "2026-01-06"],
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
  ```
- URL parsing: Tests use `urllib.request` to hit the running HTTP server and verify response format
- Thread-based monitoring: Tests read subprocess output in a background thread to avoid deadlock

**What to Mock:**
- Nothing — tests validate the entire tool end-to-end
- Direct imports used to test functions in isolation: `itembank.score_response(q, answer)`

**What NOT to Mock:**
- Don't mock the scorer — there is one scorer and it must be tested
- Don't mock file I/O — tests verify files are actually written
- Don't mock HTTP — tests start a real server and make real requests

## Fixtures and Factories

**Test Data:**
Located in `fixtures/` directory:
- `sample_bank.md` — Multi-type question bank used by scoring, serve, and agent tests
- `sample_plan.md` — Dated work plan used by day tests

**Pattern for Answers:**
Test files define helper functions to generate correct and wrong answers:
```python
def correct_answer(q):
    if q["type"] == "mc":
        return q["correct"][0]
    if q["type"] == "multi":
        return list(q["correct"])
    if q["type"] in ("table", "dnd"):
        return dict((str(i), r["cat"]) for i, r in enumerate(q["rows"]))
    if q["type"] == "build":
        return list(q["steps"])
    return "A constructed response."

def wrong_answers(q):
    """Every way of being wrong that has bitten a scorer here before."""
    if q["type"] == "mc":
        return [next(k for k in sorted(q["opts"]) if k != q["correct"][0]), "", []]
    # ... more types
```

**Location:**
- Fixtures are committed to `fixtures/` alongside `tests/`
- Temp files created with `tempfile.mkdtemp()` for server tests that need to write output files

## Coverage

**Requirements:** Not enforced — no coverage tool configured

**View Coverage:** Not available — code review is the QA method

**Coverage Gaps:**
- Short answer (constructed response) items: Tests verify they score as `None` but cannot validate human marking
- Browser JavaScript in quiz page: Not tested — tests only verify the JSON contract the page uses
- Edge cases in regex patterns: Tested against fixtures but not exhaustively

## Test Types

**Unit Tests:**
- Scope: Individual functions from `model.py` and `runtime.py`
- Approach: Direct import and call with test data
- Example: `scoring_roundtrip.py` imports `itembank` and calls `score_response(q, answer)` directly
- Assertion: Plain `if` check, fail on mismatch

**Integration Tests:**
- Scope: Full round-trip of a feature (e.g., write session, score response, read session)
- Approach: Subprocess spawning or HTTP client calls
- Example: `agent_roundtrip.py` uses subprocess to run `itembank start`, `itembank submit`, `itembank report` in sequence
- Verification: Check exit code, validate JSON output, verify file state

**E2E Tests:**
- Scope: Complete user workflow (authoring → validation → sitting → grading)
- Approach: Server spawning, browser simulation via urllib, file I/O verification
- Example: `serve_roundtrip.py` starts HTTP server, posts answers, verifies attempt file was written
- Framework: Not used — manual subprocess + HTTP + file checks

## Common Patterns

**Async Testing:**
Used in server tests to avoid blocking:
```python
lines = []
threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                 daemon=True).start()

url = None
for _ in range(60):                       # up to ~6s
    time.sleep(0.1)
    m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
    if m:
        url = m.group(0)
        break
```
- Background thread captures subprocess output
- Main thread polls for URL or signal (HTTP response, file created)

**Error Testing:**
Tests verify bad input is rejected:
```python
if itembank.score_response(q, bad) is not False:
    fail("%s (%s): %r was not marked wrong" % (q["id"], q["type"], bad))
```

Pattern: Generate wrong_answers() programmatically and verify each scores as `False`.

**State Persistence Testing:**
Tests verify writes actually reach disk:
```python
if not os.path.exists(log_path):
    fail("no log file was written; a tick was lost")
written = itembank.load_day_log(log_path)
if written.get("2026-01-06") != set(itembank.FLOOR_LANES):
    fail("the log did not round-trip. Read back: %r" % written)
```

**Invariant Testing:**
Some tests assert structural properties that must always hold:
```python
scorers = []
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "tests")]
    for f in sorted(files):
        if not f.endswith(".py"):
            continue
        path = os.path.join(base, f)
        source = open(path, encoding="utf-8").read()
        scorers += [(os.path.relpath(path, ROOT), n)
                    for n in re.findall(r"(?m)^def (\w*score\w*)\(", source)]
if scorers != [("runtime.py", "score_response")]:
    fail("expected exactly one scorer, found %r" % (scorers,))
```

This test scans every `.py` file to verify only one function named `*score*` exists in the entire codebase.

## Test Execution Model

**Bootstrap:**
- Each test file is standalone and executable: `#!/usr/bin/env python3` shebang
- Working directory: Tests use `__file__` to compute absolute paths — they run from anywhere
- Example from `agent_roundtrip.py`:
  ```python
  ROOT = Path(__file__).resolve().parents[1]
  BANK = ROOT / "fixtures" / "sample_bank.md"
  TOOL = ROOT / "itembank.py"
  ```

**Subprocess Isolation:**
- Tests spawn `python itembank.py <command>` as subprocesses
- Allows testing CLI argument parsing, exit codes, and output format independently
- Example:
  ```python
  result = subprocess.run([sys.executable, str(TOOL), "lint", BANK],
                          cwd=ROOT, check=True, capture_output=True, text=True)
  ```

**HTTP Testing:**
- Tests start server with `--port 0` to get any available port
- Server prints the URL to stdout: `http://127.0.0.1:PORT/`
- Tests scrape the port from output and make requests to `http://127.0.0.1:PORT/`
- This approach avoids port conflicts and works on any machine

**Failure Strategy:**
- `fail(msg)` prints "FAIL: " + message and calls `sys.exit(1)`
- Parent process sees non-zero exit and reports failure
- No exceptions or stack traces — simple, machine-readable output

## Specific Test Descriptions

**`scoring_roundtrip.py`:**
- Asserts the only scorer in the codebase is `runtime.score_response()`
- Tests every question type with correct and wrong answers
- Verifies offline page key matches the scorer's key
- Checks separator handling (control characters don't collide with content)

**`day_roundtrip.py`:**
- Tests plan table parsing (date formats, lane column matching)
- Verifies floor lanes logic (subset that counts as a full day)
- Checks streak counting (unfinished days don't break it)
- Integration test: starts server, posts form data, verifies ticks are written

**`serve_roundtrip.py`:**
- Starts HTTP server on random port
- Verifies served page never contains answer keys or WHY BEST text
- Posts correct and wrong answers, verifies scoring
- Checks attempt file is written to disk in markdown format
- Validates no scoring functions exist in the page source

**`agent_roundtrip.py`:**
- Tests JSON session interface: `start` → `submit` (loop) → `report`
- Verifies response format at each step (accepted flag, next item, summary)
- Uses subprocess + JSON parsing for end-to-end validation

**`due_roundtrip.py`:**
- Tests the `--due` flag of `itembank day` command
- Verifies outstanding items are listed correctly

**`surface_roundtrip.py`:**
- Basic smoke test for surface module imports

---

*Testing analysis: 2026-08-05*
