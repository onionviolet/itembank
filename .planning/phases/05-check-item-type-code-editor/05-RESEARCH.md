# Phase 5: Check Item Type & Code Editor - Research

**Researched:** 2026-08-08
**Domain:** Out-of-process code execution with a cross-platform process-tree kill; a
hand-rolled textarea+gutter code editor; format-contract extension; scorer purity.
**Confidence:** MEDIUM — the format/scoring/editor shape is HIGH confidence (read
directly from source); the Windows Job Object path is MEDIUM (CITED against Microsoft
Learn, not executed in this session); the "one answer value threading through three
consumers" finding below is HIGH confidence (read directly) and materially refines D-01.

## Summary

This phase's real risk is not "can we run Python out of process" — it is that the
codebase currently has **exactly one `answer` value that flows through three different
consumers** (`score_response`, the evidence log's `answer` field, and
`idempotency_canon`), and D-01's results-vector design produces two values (the raw
source and the pass/fail vector) that must NOT collapse into that one slot without
losing the learner's submitted code from the evidence record. This is fixable additively
(a new reserved field on the response event, `null` for every other type — the same
pattern already used for `error_category`/`hint_tier`), but it must be decided at plan
time, not discovered mid-implementation. Section "Purity Boundary" below lays out the
exact call graph and the two viable fixes.

The second real risk is the Windows process-tree kill. CI runs on `ubuntu-latest`
only — `.github/workflows/ci.yml:7` — so the Windows Job Object path (and its
`CREATE_SUSPENDED` race) can be verified only by hand on the target Windows 11 machine,
exactly as `01-01-PLAN.md`'s append-durability spike was. Budget for a manual spike
result document, not just code review, before calling D-07 done. A specific,
previously-undocumented gotcha found this session: **`subprocess.Popen` does not expose
`CREATE_SUSPENDED`, and even the raw flag cannot be safely resumed through the public
API**, because CPython's Windows `_execute_child` closes the child's thread handle
before returning control (tracked upstream as `bpo-1677688`, still open). The
suspended-then-assign pattern D-07 names as the race-free path is not available through
`subprocess.Popen` alone; the practical choice is either a narrow, accepted race window
(consistent with D-10's "stops accidents, not escapes" framing) or dropping to the
undocumented `_winapi.CreateProcess` to get the thread handle. This is a decision the
planner should make explicitly rather than let an executor discover it mid-task.

Everything else — the `CASE)`/`[LANG:]`/`[MATCH:]` format additions, the editor, the
timeout/output-cap/stdin-EOF triad, and the POSIX kill path — is standard, well-trodden
ground with a clear, additive implementation inside this codebase's existing patterns.

**Primary recommendation:** Build `runner.py` as a new peer module (stdlib only:
`subprocess`, `tempfile`, `threading`, `os`, `signal`, `sys`, and `ctypes` on Windows)
that is called exactly once per submission, at the surface layer (inside
`quiz.record_answer()` and `session.do_submit()`, both of which currently call
`score_response()` directly with no runner step today), producing a per-case results
list that becomes the `answer` fed to `score_response`/`canonical_response`, while the
raw source text is threaded separately into evidence via a new reserved field.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Format parsing (`CASE)`, `[LANG:]`, `[MATCH:]`) | Model (`model.py`) | — | Same layer as every other type marker; model has zero dependencies and no execution capability, so it cannot leak into runner concerns |
| Code execution, timeout, process-tree kill | New peer module `runner.py` | — | D-01: must be its own module, imported by surfaces, never by `runtime.py` — keeps `canonical_response`/`canonical_key` pure and reachable from a script with no subprocess capability (the offline `build` page's Python-side generator) |
| Scoring (vector -> pass/fail) | Runtime (`runtime.py`) | — | `canonical_response`/`canonical_key`/`score_response` stay pure string/list reductions; D-01's whole point |
| Submission entry point (browser) | Surfaces / Daemon (`surfaces/daemon.py:handle_quiz_answer` -> `surfaces/quiz.py:record_answer`) | — | This is the actual POST target for the browser quiz page — see correction below; runner call belongs here, before `score_response` |
| Submission entry point (agent/CLI) | Surfaces (`surfaces/session.py:do_submit`) | — | A second, independent call site that reaches `score_response()` directly today; the runner must also gate this path, or an agent driving `check` via `itembank submit`/`/api/submit` bypasses execution entirely |
| Editor rendering, Tab/gutter/scroll-sync | Browser (`surfaces/quiz_page.py:TEMPLATE`'s inline `<script>`) | — | Hand-authored vanilla JS, no build step, matches every other item-type's rendering branch |
| Settings (`check.timeout_seconds`, etc.) | Settings (`surfaces/settings.py` + `schemas/settings.schema.json`) | — | Same numeric-bounds validator Phase 2 already built |
| `--lan` refusal | Daemon (`surfaces/daemon.py`) | Settings (`check.allow_lan`) | D-09: the refusal is a request-time daemon decision reading a settings value, not a settings-layer concern by itself |

## User Constraints

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

All twelve decisions D-01 through D-12 in `05-CONTEXT.md` are the user's delegated
judgment ("Delegate all... the most optimal solution that gives us the most options and
directions in the future") and are **not re-opened here**, except where this research
was explicitly invited to challenge D-01's purity mechanics (see "Purity Boundary"
below — the challenge refines the *plumbing*, not the *design*: the runner still runs
before the scorer, never inside it; `canonical_response`/`canonical_key` still stay
pure reductions over an already-computed vector).

Summary of the locked shape (full text in `05-CONTEXT.md`, read this session in full):
- D-01: runner runs before the scorer; `runner.py` returns a results vector;
  `canonical_response` reduces it to `"1,1,0"`-shaped text; `canonical_key` is all-ones.
- D-02: `[LANG: python]` on the item, settings-driven allowlist, one entry shipped.
- D-03: `CASE) <stdin> :: <expected stdout>`, reusing `::` split convention; 2+ cases
  recommended (lint warning `item.check_too_few_cases` below 2).
- D-04: `[MATCH: exact|trimmed|regex]`, default `trimmed`.
- D-05: stem + `CASE)` set ARE fingerprinted; `[LANG:]`/`[MATCH:]` are NOT.
- D-06: server-side execution only; offline `build` page renders "not answerable
  offline" for `check` items.
- D-07: POSIX `start_new_session=True` + `os.killpg`; Windows Job Object via `ctypes`
  with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, `taskkill /T /F /PID` fallback;
  `check.timeout_seconds` settings key, default 5.
- D-08: `check.max_output_bytes` (default 64 KB, truncation fails the case); stdin
  closed after case input is written (EOF, not a second timeout mechanism).
- D-09: `check` execution refused when serving `--lan` unless `check.allow_lan` is true.
- D-10: the no-sandbox sentence appears in exactly two places, worded identically,
  grep-clean of "sandbox"/"isolat"/"contain".
- D-11 (**SUPERSEDED 2026-08-11 by ruling 5/11 — CM6 adopted; see the editor resolution
  below and ROADMAP Phase 5 RESOLVED rulings**): `<textarea>` + synchronized 1-based
  line-number gutter, Tab inserts `\t`,
  Shift-Tab dedents, no external editor library.
- D-12: submitted answer is the source text, sent as-is; `public_item()` gains a
  `check` branch; `explain_payload()` reveals per-case expected output only after
  response.

### Claude's Discretion (explicitly re-opened by 05-CONTEXT.md itself)

- D-03's `::` separator may switch to the `FIELD_SEP` control-character convention if a
  real Python test case's expected stdout plausibly contains `::`.
- D-07's Job Object via `ctypes` may fall back to `taskkill /T /F /PID` as primary if
  proven unreasonable to test on the target Windows 11 machine — the grandchild case
  must still be proven either way.
- D-09's `--lan` refusal wording/plumbing may be adjusted to match how Phase 2's
  `--lan` is actually wired — default must stay closed either way.

### Deferred Ideas (OUT OF SCOPE)

- Runnable code inside lesson prose (LOOP-03, Phase 9) — reuses this runner, not built
  here.
- A second language (C, JavaScript) — `check.languages` entry, no code change needed.
- Model-marked code or model hints on a failed case (Phase 8).
- Real isolation (containers, seccomp, restricted interpreter) — permanently out of
  scope at this project's scale; CODE-05 documents the absence rather than closing the
  gap.
- Per-case partial credit — dichotomous only this phase; the vector makes it
  *computable* later, not *shown* later.
- Theming the editor (Phase 4).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CODE-01 | A `check` item is verified by running the learner's own code and comparing its output to an expected result | `runner.py` design (Architecture Patterns), `CASE)` format grammar (Format Contract) |
| CODE-02 | `check` scores dichotomously, through the same scorer as every other type | Purity Boundary section — the exact `score_response()` call-graph fix required at both submission entry points |
| CODE-03 | The code field is a real editor: monospace, tab inserts a tab, line numbers a rubric point can reference | Editor Interaction section — pixel-alignment, Tab handling, no-wrap requirement, verified against `05-UI-SPEC.md`'s locked markup |
| CODE-04 | Execution is bounded by a timeout and the process tree is cleaned up on both Windows and POSIX | Process-Tree Kill section — exact `ctypes` structures, POSIX failure modes, `CREATE_SUSPENDED` gotcha |
| CODE-05 | The documentation states plainly that this stops accidents and not deliberate escapes, and does not claim isolation | D-10 (locked), verified against `CONCERNS.md`'s existing security language (no prior overclaim found) |

</phase_requirements>

## Standard Stack

### Core

No third-party packages. This phase is entirely Python standard library, per
`.claude/CLAUDE.md`'s "Python standard library only, no install step" constraint and
the explicit instruction in this task not to propose any dependency.

| Module | Stdlib since | Purpose | Why standard |
|--------|--------------|---------|---------------|
| `subprocess` | always | spawn the learner's interpreter, timeout, pipe I/O | the only process-spawning primitive in stdlib |
| `ctypes` | always | Windows Job Object API (`CreateJobObjectW`, `AssignProcessToJobObject`, `SetInformationJobObject`) | explicitly named in D-07 as the stdlib path to a WinAPI call with no wrapper in stdlib |
| `tempfile` | always | write the learner's source to a real file (needed because stdin is reserved for case input, not code delivery) | `tempfile.NamedTemporaryFile`/`TemporaryDirectory` are the stdlib-idiomatic way to get a path a subprocess can `argv`-reference |
| `threading` | always | drain stdout/stderr pipes incrementally without deadlocking on a full OS pipe buffer while enforcing the output cap | matches `surfaces/day.py`'s existing background-thread pattern for long-running I/O (`day.py:840-843`-adjacent Anki/git patterns) |
| `os`, `signal` | always | `os.killpg`, `signal.SIGTERM`/`SIGKILL` on POSIX | D-07's named POSIX mechanism |
| `sys` | always | `sys.executable` — the running interpreter, D-02's `python` language-template default |

### Supporting

| Module | Purpose | When to use |
|--------|---------|-------------|
| `platform` / `sys.platform` | branch POSIX vs. Windows in `runner.py` | matches `surfaces/day.py:338-343`'s existing `sys.platform == "win32"` branch style, which `05-CONTEXT.md`'s Reusable Assets section explicitly points at as the idiom to follow |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| Hand-rolled `ctypes` Job Object | `pywin32` (`win32job` module) | Third-party dependency; explicitly forbidden by this phase's constraints regardless of maturity |
| Hand-rolled textarea+gutter | CodeMirror / Monaco / Ace | **RESOLVED 2026-08-11 (ruling 5/11): CodeMirror 6 adopted.** The earlier veto ("vendored-asset exception is spent on KaTeX", external CDN forbidden by the stdlib/no-network posture) is SUPERSEDED — no such budget exists and the stdlib rule was relaxed. CM6 is vendored at a pinned version with a recorded SHA-256 and a named license review under the §4a supply-chain rule; its `Diagnostic{from,to,severity,message}` maps 1:1 onto our lint records for the Phase 11 authoring surface. |
| `subprocess.communicate(timeout=)` for the whole run | Incremental threaded reads with an output cap | `communicate()` buffers the **entire** output in memory before returning, so an unbounded-output infinite loop is bounded only by the *timeout*, not by `max_output_bytes`, until the process is killed — see "Timeout + Output-Cap Interaction" below for why incremental reads are needed instead |

**Installation:** None for the Python runtime — no packages to install; Python stdlib only. The one JS dependency is the vendored CodeMirror 6 bundle (pinned, hashed, license-reviewed, committed under `assets/vendor/codemirror/`, no registry lookup at build or runtime) plus the §4a-recorded JS test runner for editor behaviour (ruling 16).

**Version verification:** Not applicable (stdlib only). Python target is 3.11+ per
`.claude/CLAUDE.md`, confirmed against CI's `actions/setup-python@v5` with
`python-version: "3.11"` (`.github/workflows/ci.yml:12`) `[VERIFIED: .github/workflows/ci.yml:10-12]`.

## Package Legitimacy Audit

Not applicable — this phase installs zero external packages. `ctypes`, `subprocess`,
`tempfile`, `threading`, `os`, `signal`, and `sys` are all part of the Python 3.11
standard library; none require a registry lookup, and none can be "slopsquatted."

**Packages removed due to SLOP verdict:** none (none proposed).
**Packages flagged as suspicious [SUS]:** none (none proposed).

## Architecture Patterns

### System Architecture Diagram

```text
  Browser (quiz_page.py TEMPLATE)              Agent / CLI
  ┌─────────────────────────┐                  ┌──────────────────┐
  │ asCheck(q, body, act)   │                  │ itembank submit  │
  │  textarea.code + gutter │                  │ /api/submit      │
  └──────────┬───────────────┘                  └─────────┬─────────┘
             │ POST source text                            │ answer = source text
             ▼                                              ▼
  POST /quiz/<stem>/answer                        session.do_submit()
  handle_quiz_answer()  (daemon.py)               (session.py:111)
             │                                              │
             ▼                                              ▼
  quiz.record_answer()  ◄────────────┬──── BOTH call sites must gate on q["type"]=="check"
  (quiz.py:41)                       │     and call the runner exactly once, before scoring
             │                       │
             ▼                       │
   IF type == "check":               │
     runner.run_cases(q, source)  ───┘   <- NEW: runner.py (peer of model.py/runtime.py)
     (spawns subprocess, timeout,             - writes source to a temp file
      process-tree kill, output cap,          - one Popen per CASE), stdin=case input,
      per-case pass/fail + actual output)       stdin.close() after write (EOF)
             │                                 - threaded incremental read, 64 KB cap
             ▼                                 - POSIX: start_new_session + os.killpg
   vector = [1 if c["passed"] else 0 …]        - Windows: Job Object via ctypes,
             │                                   taskkill /T /F /PID fallback
             ▼
   score = score_response(q, vector)   <- runtime.py, UNCHANGED signature, pure
             │
             ▼
   evidence.response_event(…, answer=source_text_raw, …)  <- NEW field carries source;
             │                                                 "answer"/"canonical" carry
             ▼                                                 the vector, consistent with
   explain_payload(q, reveal, run_result=…)  <- NEW optional     every other item type
             │                                    param: per-case actual output, needed
             ▼                                    for "Your output" in the UI-SPEC's
   {score, explain} -> browser renders            per-case matrix
   pass/fail matrix (per 05-UI-SPEC.md)
```

### Recommended Project Structure

```
runner.py                  # NEW peer module: model.py / runtime.py / server.py / runner.py
model.py                   # + check parse branch, CASE)/[LANG:]/[MATCH:], SPEC, lint codes
runtime.py                 # + check branches in canonical_response/canonical_key/
                            #   public_item/explain_payload (signature gains run_result)
surfaces/
  quiz.py                  # record_answer() gains the runner call before score_response
  session.py                # do_submit() gains the same runner call — SEPARATE call site
  daemon.py                 # handle_quiz_answer threads run_result into explain_payload
  quiz_page.py               # + asCheck(), .codewrap/.gutter/.case CSS, per 05-UI-SPEC.md
schemas/
  settings.schema.json      # + "check" group: timeout_seconds, max_output_bytes,
                             #   languages, allow_lan  (x-itembank-phase: 5)
  item.schema.json          # + check_item $def, response_schema {"type":"string",
                             #   "format":"source","language":…}
  response.schema.json      # + new reserved field for raw source (see Purity Boundary)
tests/
  check_roundtrip.py        # NEW — grandchild-spawning timeout case (both platforms),
                             #   multi-case pass/fail matrix, format parse, no-sandbox
                             #   grep assertion
fixtures/
  check_bank.md              # NEW synthetic fixture (guard-safe, no real content)
```

### Pattern 1: Runner Called Exactly Once, at the Surface Layer

**What:** `runner.run_cases(q, source)` is invoked by `quiz.record_answer()` and by
`session.do_submit()` — the two places that currently call `score_response()` directly
with **no runner step at all**. This is a correction to an implicit assumption in
`05-CONTEXT.md`'s "posts source to `/api/submit`" line: the browser quiz page actually
posts to `POST /quiz/<stem>/answer` (`surfaces/daemon.py:42,77` route table;
`surfaces/quiz_page.py:155` `fetch("__POST__", …)` where `__POST__` is set to
`"/quiz/%s/answer" % stem` at `surfaces/daemon.py:483-484`), which is a **different**
route from `/api/submit` (the agent-facing JSON session API, `surfaces/session.py`).
`[VERIFIED: surfaces/daemon.py:42,57-60,76-77,483-484,488-542]` (quoted below in the
Purity Boundary section). Both routes must gate on `q["type"] == "check"` and invoke
the runner before scoring, or an agent driving a `check` item through `itembank
submit`/`/api/submit` bypasses execution entirely and gets a `score_response()` call
against whatever raw string it sent as `answer` — which would silently mis-score every
`check` item an agent (rather than the browser) submits.

**When to use:** Any surface that reaches `score_response()` for a `check` item.

**Example:**
```python
# surfaces/quiz.py — record_answer(), modified
def record_answer(bank_path, qs, session_id, log, out_path, mode, q, response, elapsed_ms):
    run_result = None
    scored_answer = response
    if q["type"] == "check":
        run_result = runner.run_cases(q, response)          # response IS the source text
        scored_answer = [1 if c["passed"] else 0 for c in run_result]
    score = score_response(q, scored_answer)
    event = evidence.response_event(
        session_id, q, response, score, mode, attempt_num,   # `response` (raw source)
        os.path.basename(bank_path), response_time_ms=elapsed_ms, confidence=None,
        check_source=response if q["type"] == "check" else None)   # see Purity Boundary
    ...
    return score, run_result   # run_result threaded to explain_payload by the caller
```

### Pattern 2: One Case, One Subprocess

**What:** `run_cases()` spawns a fresh `subprocess.Popen` per `CASE)` line rather than
one long-lived interpreter fed multiple inputs. This is what makes the per-case timeout,
per-case output cap, and per-case process-tree kill each independent — a case that hangs
forever does not consume the budget of the cases after it, and a case whose code
corrupts interpreter state (e.g. monkey-patches a builtin) cannot contaminate the next
case's run.

**When to use:** Always, for every `CASE)` in a `check` item.

### Anti-Patterns to Avoid

- **Running the check inside `canonical_response`/`canonical_key`:** breaks D-01's own
  stated purity rule and puts process execution on a code path the offline `build` page
  shares (`runtime.py:70-79`'s docstring names three consumers, one of which is the
  static page — quoted verbatim below).
- **Calling the runner a second time to build the explanation:** the code may be
  non-deterministic, slow, or side-effecting (a network call, if the "no sandbox" bound
  ever gets exercised); re-running to get "Your output" for the explain payload doubles
  execution cost and risk for zero benefit. Capture actual per-case output on the one
  run and thread it through.
- **Reading `stdout` then `stderr` sequentially without threads:** classic pipe-buffer
  deadlock — the child blocks writing to a full unread pipe while the parent blocks
  reading the other one. `subprocess.communicate()` already avoids this internally via
  background threads; a hand-rolled incremental-read-with-cap implementation must
  replicate that (see "Timeout + Output-Cap Interaction").
- **Trusting `subprocess.Popen(..., creationflags=CREATE_SUSPENDED)` to let you call
  `ResumeThread` afterward:** `subprocess.Popen` does not expose the thread handle
  `CreateProcess` returns — CPython's Windows `_execute_child` closes it. See Process-
  Tree Kill section.

## Purity Boundary — the Actual Call Graph, and Where D-01's Vector Must Enter It

This section documents the concrete gap between D-01's stated design and the existing
scoring pipeline, found by reading the actual call sites this session rather than
inferring from the module docstring alone.

### The docstring D-01 is built on

`[VERIFIED: runtime.py:1-11]`, `runtime.py`'s module docstring, read this session:

> "Scoring, sessions, and the payloads a surface is allowed to see.
>
> The only scorer lives here. Every surface reaches a verdict by calling into this
> module rather than by reimplementing the rules, browser page included. That is
> what stops the CLI, the JSON session interface and the quiz page from quietly
> disagreeing about the same response."

`[VERIFIED: runtime.py:70-79]`, `canonical_response()`'s docstring:

> "Reduce a selected response to one comparable string.
>
> Three consumers need to agree on what a response *is*: the scorer compares
> two of these, the static `build` page compares the learner's against a key
> computed here, and the attempt record stores what was given. Putting the
> shape in one function is what lets the browser stop deciding correctness
> while still being able to self-check offline, where there is no process to
> ask."

D-01 correctly reads this as: `canonical_response`/`canonical_key` must stay pure, and
must not spawn a subprocess. That part of D-01 is confirmed correct and this research
does **not** challenge it.

### Where D-01 needs refinement: the single-`answer`-value pipeline

`[VERIFIED: surfaces/quiz.py:41-49]`, `record_answer()` — the ONE function
`cmd_serve` and `surfaces/daemon.py` both call:

```
def record_answer(bank_path, qs, session_id, log, out_path, mode, q, response, elapsed_ms):
    ...
    score = score_response(q, response)
    item_key = evidence.evidence_key(q)
    canon = evidence.idempotency_canon(q, response)
```

`[VERIFIED: surfaces/session.py:111-133]`, `do_submit()` — the agent/CLI path,
independently:

```
def do_submit(session_file, answer, confidence):
    ...
    answer = normalize_answer(answer)
    score = score_response(q, answer)
    ...
    canon = evidence.idempotency_canon(q, answer)
    ...
    event = evidence.response_event(
        data["session_id"], q, answer, score, data["mode"], attempt_num,
        os.path.basename(data["bank"]), response_time_ms=response_time_ms,
        confidence=confidence)
```

`[VERIFIED: evidence.py:328-346,355-395]`, `response_event()` and
`idempotency_canon()` — the single `answer` parameter both surfaces pass in is used
for THREE purposes with no branching between them:

```
def idempotency_canon(q, answer):
    canon = canonical_response(q, answer)
    ...

def response_event(session_id, q, answer, score, mode, attempt_num, bank, ...):
    ...
    canon = idempotency_canon(q, answer)
    return {
        ...
        "answer": answer,
        "canonical": canon,
        "score": score,
        ...
    }
```

**The gap:** D-01 states `canonical_response(q, answer)` for `check` reduces an
already-computed *vector* (e.g. `[1, 1, 0]`) to `"1,1,0"`-shaped text. But both existing
call sites pass exactly one `answer` value into `score_response`, `idempotency_canon`,
AND `response_event`'s stored `"answer"` field. If that one value is the vector, the
evidence log's `"answer"` field for every `check` submission becomes `[1, 1, 0]` —
**the learner's actual submitted code is never recorded anywhere.** That is a real
regression: Phase 8's tutoring model (TEACH-04: "reads the item, key, rationale, and the
learner's specific wrong answer") needs the actual source to do anything useful with a
`check` item, and a human reviewing evidence later has no way to see what was written.

If, instead, the one `answer` value passed through is the raw *source text* (matching
D-12's "submitted answer for a `check` item is the source text, sent as-is"), then
`canonical_response(q, source_text)` cannot compute the vector without running the
code — reopening exactly the purity violation D-01 exists to prevent.

**Two source values must exist simultaneously at the point `response_event()` is
called: the raw source (for evidence/audit/future model context) and the vector (for
scoring).** The existing pipeline has no seam for that; it assumes one `answer` serves
every purpose, and every other item type genuinely only needs one (an `mc` answer letter
IS what gets scored AND what gets recorded).

### Recommended fix (this session's proposal — `[ASSUMED]`, planner should confirm)

1. `runner.run_cases(q, source)` runs once, at the surface layer, returning a list of
   per-case dicts: `[{"passed": bool, "actual": str, "timed_out": bool, "truncated": bool}, ...]`.
2. The calling surface (`record_answer`/`do_submit`) builds
   `scored_answer = [1 if c["passed"] else 0 for c in run_result]` and calls
   `score_response(q, scored_answer)` — `canonical_response`'s `check` branch receives
   an already-a-list value and formats it, exactly as D-01 describes; it never sees the
   source and never executes anything.
3. `evidence.response_event()` gains one new **optional, keyword-only, reserved**
   parameter — e.g. `check_source=None` — following the exact precedent already
   established for `error_category`/`hint_tier` (`[VERIFIED: evidence.py:390-391]`:
   `"error_category": None,   # no error taxonomy exists before Phase 6` /
   `"hint_tier": None,        # no hint ladder exists before Phase 8`). For a `check`
   item, the caller passes the raw source; for every other type, it stays `None`. The
   event's existing `"answer"` field keeps carrying `scored_answer` (the vector) — the
   same shape every other type already uses (a list, a dict, or a string that IS what
   was scored) — so `idempotency_canon`/`dedupe_key` behavior is unchanged for every
   type including `check`.
4. `schemas/response.schema.json` gains the new field in `required` (with a `null`
   default meaning) — additive per PROTO-01's "explicit schema version" rule and the
   file's own `additionalProperties: false` (`[VERIFIED: schemas/response.schema.json:8]`),
   which means the new key must be added to `required` too, not just `properties`, or
   validation of a non-`check` event with the key absent will fail against the current
   all-required shape.
5. `explain_payload(q, reveal=True, run_result=None)` gains a new optional parameter —
   `run_result` is the same per-case list from step 1, threaded through so the "Your
   output" / timeout / truncation status text the UI-SPEC locks (`05-UI-SPEC.md`
   Copywriting Contract, "Case status" rows) can be rendered without re-running the
   code. `[VERIFIED: runtime.py:258-267]` — today `explain_payload(q, reveal=True)`
   takes only the static question dict and has **no parameter through which per-case
   actual output could ever reach it**; this is a required signature change, not an
   optional one, given D-12's requirement that the explain payload reveal per-case
   expected/actual output after the response.

**Reversibility of this refinement:** cheap. It is additive to `response_event()`'s
signature and to the schema, and it changes `explain_payload()`'s signature in a
backward-compatible way (new parameter defaults to `None`, existing five call sites for
the other five types pass nothing and are unaffected).

## Format Contract

### The stem-terminator alternation must gain three markers

`[VERIFIED: model.py:43-47]`, `parse_question()`'s stem extraction, read verbatim:

```python
    stem = grab(
        r"Q\d+\.\s*(.*?)\s*(?:\(difficulty:|\n\[OBJECTIVE|\n\[TYPE|\n\[SELECT"
        r"|\n\[CATEGORIES|\n\[ID|\n\[HASH|\n[A-H]\)|\nROW\)|\nITEM\)|\nSTEP\)"
        r"|\nMODEL:|\nRUBRIC:|\nWHY BEST:)",
        ch, re.S)
```

This is a non-greedy `.*?` match terminated by the first of a fixed alternation of
markers. If `\nCASE\)`, `\n\[LANG`, and `\n\[MATCH` are not added to this alternation,
a bank author's `CASE)` lines and `[LANG:]`/`[MATCH:]` tags are silently swallowed into
the stem text — the exact failure mode named in the additional-context brief. The fix
is additive (new alternatives in the existing `(?:...)` group); order among alternatives
does not matter for correctness in Python's `re` (each alternative is tried at the same
scan position; the first structural marker actually present in the text wins regardless
of the alternation's internal ordering), only that the marker literal appears somewhere
in the group.

### The `[ID:]`/`[HASH:]` insertion point needs the same three markers

`[VERIFIED: model.py:191-193]`, the SEPARATE `TERMINATOR` regex `assign_ids()` uses to
find where to insert a missing `[ID:]`/`[HASH:]` line:

```python
TERMINATOR = re.compile(
    r"(?m)^(?:\[TYPE:|\[OBJECTIVE:|\[SELECT:|\[CATEGORIES:|[A-H]\)|ROW\)|ITEM\)|"
    r"STEP\)|MODEL:|RUBRIC:|WHY BEST:)")
```

This is a **second, independently-maintained regex** with the same marker vocabulary as
the stem terminator, used at `model.py:267` (`m = TERMINATOR.search(chunk)`) to decide
where `[ID:]`/`[HASH:]` get spliced into a question block. If only the stem-terminator
alternation is updated and this one is missed, `itembank id-assign` run against a bank
containing `check` items will insert `[ID:]`/`[HASH:]` in the wrong place (after
`WHY BEST:`, or at the very end of the block if no marker matches at all) — a bug that
would not surface in the stem-parsing tests at all, only in an id-assign round-trip
test. **Both regexes must be updated together**, and a test asserting they stay in sync
(e.g. both containing `CASE\)`) is worth adding, since this codebase does not currently
share the marker list between the two patterns (`WOULD_BE`-style module constant
extraction, matching `05-CONTEXT.md`'s Reusable Assets note about `model.WOULD_BE`,
would remove this duplication risk entirely and is a reasonable executor-discretion
cleanup while touching both spots).

### `CASE)` parse branch, matching existing `::`-split precedent

`[VERIFIED: model.py:86-98]`, the `table`/`dnd` `::`-split this phase's D-03 explicitly
reuses:

```python
    if qtype in ("table", "dnd"):
        cats = [c.strip() for c in grab(r"(?m)^\[CATEGORIES:\s*(.*?)\s*\]", ch).split("|") if c.strip()]
        marker = "ROW" if qtype == "table" else "ITEM"
        rows = []
        for line in re.findall(rf"(?m)^{marker}\)\s*(.+?)\s*$", ch):
            if "::" not in line:
                continue
            t, c = line.rsplit("::", 1)
            rows.append({"text": t.strip(), "cat": c.strip()})
```

A `check` branch following this exact shape:

```python
    if qtype == "check":
        lang = (grab(r"(?m)^\[LANG:\s*(\w+)\s*\]", ch) or "python").lower()
        match_mode = (grab(r"(?m)^\[MATCH:\s*(\w+)\s*\]", ch) or "trimmed").lower()
        cases = []
        for line in re.findall(r"(?m)^CASE\)\s*(.+?)\s*$", ch):
            if "::" not in line:
                continue
            stdin_text, expected = line.rsplit("::", 1)
            cases.append({"stdin": stdin_text.strip(), "expected": expected.strip()})
        if not (stem and cases):
            return None
        common.update({"lang": lang, "match": match_mode, "cases": cases, "notes": notes(ch)})
        return common
```

**D-03's own discretion clause applies here concretely**: `line.rsplit("::", 1)` splits
on the LAST `::`, matching the existing `table`/`dnd` precedent exactly
(`[VERIFIED: model.py:93]` — `t, c = line.rsplit("::", 1)`). A Python test case whose
expected stdout itself contains `::` (plausible — e.g. a program printing a URL fragment,
a slice-notation demonstration, or C++-flavored teaching content mixed into a CS bank)
would have its expected text corrupted at the last `::` rather than the first. This
research recommends invoking D-03's own escape hatch and switching `CASE)` specifically
to the `FIELD_SEP` control-character convention `runtime.py:64` already established
(`[VERIFIED: runtime.py:60-67]`, "Control characters rather than punctuation because
option text and build steps contain commas, pipes and \">\" often enough that any
printable separator eventually collides with content") — **but this cannot be
authored by hand in a markdown file** the way `::` can, so the practical shape is
either: keep `::` and document the collision risk in `SPEC`, or require the FIELD_SEP
byte to be typed as an escape sequence the parser un-escapes (adds authoring friction).
Given `check` items are authored by a human (this milestone) or an AI authoring loop
(Phase 11, not yet built), and expected stdout containing a literal `::` is a real but
narrow case, this research's recommendation is: **keep `::`, document the collision in
`SPEC`'s `check` section explicitly** (following the same "state the limit plainly"
posture CODE-05 already establishes project-wide), rather than adding authoring
friction for a narrow case. Flagged for the planner to confirm — this is the kind of
call D-03 explicitly delegates.

### Lint: two new codes, and one existing lint rule that must exclude `check`

`[VERIFIED: model.py:389-400]`, `LINT_CODES` is a `tuple(sorted({...}))` — the existing
pattern for adding codes additively:

```python
LINT_CODES = tuple(sorted({
    "item.duplicate_number", "item.select_mismatch", "item.correct_unknown_option",
    "item.too_few_options", "item.missing_second_best", "item.distractor_missing",
    "item.distractor_no_would_be", "item.too_few_categories", "item.row_category_unknown",
    "item.too_few_rows", "item.missing_distractor_notes", "item.too_few_steps",
    "item.duplicate_steps", "item.missing_model", "item.too_few_rubric_points",
    "item.model_too_long", "item.rubric_point_too_long", "item.missing_why_best",
    "item.missing_trap", "item.low_confidence", "item.duplicate_stem",
    "item.missing_id", "item.duplicate_id", "item.missing_hash",
    "item.content_drift", "item.objective_unnamespaced",
    "bank.answer_position_skew",
}))
```

Add `"item.check_lang_unknown"` and `"item.check_too_few_cases"` per D-02/D-03's
already-named codes.

`[VERIFIED: model.py:533]` — `if t != "short" and not q.get("why"): errors.append(LintError("item.missing_why_best", ...))`. This condition currently exempts only `short` from requiring `WHY BEST`. A `check` item has no keyed option to explain — there is no "why this is best" the way an `mc` item has one — so this condition needs to become `if t not in ("short", "check") and not q.get("why")`, matching `short`'s existing reasoning exactly (`SPEC`'s own text: "No WHY BEST is required on a short item; MODEL replaces it"). Missing this is a real trap: without the fix, every authored `check` item would fail lint with a `missing_why_best` error that makes no sense for a code-execution item.

### `SPEC` text — where D-10's honest-limits sentence and the grammar both land

`[VERIFIED: model.py:280-362]`, `SPEC`'s existing per-type structure (six numbered
items, `THE FIVE ITEM TYPES` heading at `model.py:307` — this heading text itself must
change to `THE SIX ITEM TYPES` or similar once `check` exists, an easy one-line miss).
The `check` section should follow the same worked-example shape as every other type
(stem + markers + a short worked snippet), end with the CODE-05 sentence verbatim from
`05-UI-SPEC.md`'s Copywriting Contract (byte-identical to the UI copy, per D-10 and the
UI-SPEC's own closing note: *"the honest-limits statement carry this exact text, with
no rewording for medium"*).

## Process-Tree Kill — POSIX

### The primitive and its exact failure modes

`os.killpg(os.getpgid(p.pid), signal.SIGTERM)` after `subprocess.Popen(..., start_new_session=True)`
is D-07's named mechanism `[CITED: alexandra-zaharia.github.io — "Kill a Python
subprocess and its children when a timeout is reached", accessed this session]`. Named
failure modes, concretely:

1. **The child that calls `setsid()` itself.** `start_new_session=True` makes the
   immediate child (the learner's interpreter) the leader of a **new** process group and
   session, so `os.killpg` targets that group. If the learner's code itself calls
   `os.setsid()` (or spawns a grandchild that does — unlikely from plain Python without
   `os` calls, but the grandchild-spawning test fixture, described below, must itself
   NOT call `setsid` again, or it would escape into a third group invisible to
   `killpg`). A learner's code that intentionally forks and detaches (double-fork
   daemonization) can escape `killpg` — this is exactly the kind of "deliberate escape"
   D-10's honest-limits sentence exists to disclaim, not a bug to fix.
2. **Zombie reap ordering.** `[CITED: docs.python.org/3/library/subprocess.html]` —
   `Popen.communicate(timeout=)` raising `TimeoutExpired` does **not** kill the child;
   the process keeps running. After `os.killpg(...)`, the immediate child (the one
   `Popen` tracks) must still be reaped via `proc.wait()` or a second
   `proc.communicate()` call, or it becomes a zombie until the parent Python process
   itself exits. Grandchildren that are SIGKILLed are reaped by `init`/`systemd`
   automatically once orphaned — the runner does not need to reap them, only its own
   direct child.
3. **`SIGTERM` vs `SIGKILL` sequencing.** The searched pattern
   (`[CITED: alexandra-zaharia.github.io]`) sends `SIGTERM` only. Given D-08's
   philosophy (bound accidents, not evade deliberate resistance) and D-07's default
   5-second timeout being itself the bound, **this research recommends `SIGKILL`
   directly on timeout**, not a `SIGTERM`-then-wait-then-`SIGKILL` escalation: a
   `SIGTERM` handler the learner's runaway loop never reaches (because the loop itself
   is the problem) buys nothing, and adding a second wait window before `SIGKILL` only
   delays reaching the bound `check.timeout_seconds` is supposed to guarantee. If the
   planner prefers the more conservative two-step escalation (letting a program with a
   legitimate cleanup handler exit gracefully), that is a reasonable alternative --
   `[ASSUMED]`, not dictated by CONTEXT.md, flagged for a planner decision.

### Grandchild-spawning test fixture (portable, stdlib-only, self-cleaning on failure)

Requirements from the additional-context brief: deterministic on both platforms, does
not leak processes when the test itself fails.

**Recommended shape** — a heartbeat file, not a process-listing tool (`psutil` is a
third-party dependency and forbidden; Linux `/proc` scanning does not work on macOS or
Windows and the project targets all three per `.claude/CLAUDE.md`'s Platform
Requirements):

```python
# fixture script, written to a temp .py file by the test, NOT part of runner.py itself
import subprocess, sys, time, os

HEARTBEAT = sys.argv[1]           # a path the test controls and can poll

def main():
    # The grandchild: this process's own child, spawned WITHOUT calling setsid again,
    # so it inherits the parent's (the runner's immediate child's) process group /
    # Windows Job Object membership -- proving the kill reaches two levels deep.
    child = subprocess.Popen([sys.executable, "-c", f"""
import time, os
with open({HEARTBEAT!r}, "a") as fh:
    while True:
        fh.write(str(time.time()) + chr(10)); fh.flush(); time.sleep(0.1)
"""])
    while True:
        time.sleep(1)            # the parent (learner's direct process) also hangs

if __name__ == "__main__":
    main()
```

The test:
1. Runs this fixture through `runner.run_cases()` with a short `timeout_seconds` (e.g.
   1s), with `CASE)`'s stdin irrelevant (the program never reads stdin).
2. Asserts the runner returns within a bounded wall-clock margin of the timeout (proving
   the kill happened, not merely that `communicate()`'s own timeout fired without an
   actual kill).
3. Records the heartbeat file's size/mtime immediately after the runner returns, then
   sleeps ~1s and checks the file did NOT grow further — proving the **grandchild**
   (not just the direct child) actually stopped writing, which is the specific claim
   Success Criterion 3 makes ("including any child process it spawned").
4. Cleans up the heartbeat file and asserts no leaked process by construction: since the
   fixture never daemonizes or calls `setsid`, if the runner's kill path is correct
   (POSIX: `killpg` on the process group; Windows: Job Object close), both processes are
   already gone by the time the test's assertions run — nothing to separately search
   for and kill in a test teardown. If the runner's kill path is buggy, the leaked
   processes are the two children of the test's own subprocess tree, which normal OS
   process-tree cleanup on test-runner exit will still reclaim (CI runs in an ephemeral
   VM; a local dev run should `taskkill /T /F` or `pkill -f HEARTBEAT_PATH` defensively
   in a `finally:` block regardless, since a failing assertion should not leave a
   runaway process on the developer's own machine).

This fixture is portable to both platforms with no platform-specific code inside the
fixture itself — only the test harness invoking `runner.run_cases()` differs by
platform (implicitly, since `runner.py` branches internally).

## Process-Tree Kill — Windows

### The `CREATE_SUSPENDED` gap this session found

`subprocess.CREATE_SUSPENDED` **does not exist** as a module attribute.
`[CITED: docs.python.org/3/library/subprocess.html#windows-constants, fetched this
session]` — the documented Windows Constants are `CREATE_NEW_CONSOLE`,
`CREATE_NEW_PROCESS_GROUP`, the priority-class constants, `CREATE_NO_WINDOW`,
`DETACHED_PROCESS`, `CREATE_DEFAULT_ERROR_MODE`, and `CREATE_BREAKAWAY_FROM_JOB`
(added 3.7) — `CREATE_SUSPENDED` is absent from this list. The raw WinAPI value
(`0x00000004`) can still be passed as a plain integer to `creationflags`, since
`Popen` accepts any int there — but **even with the raw flag, `subprocess.Popen`
cannot resume the suspended thread**, because CPython's Windows `_execute_child`
closes the returned thread handle (`hThread`) before `Popen.__init__` returns, and the
public `Popen` object exposes only the process handle, never the thread handle.
`[CITED: bugs.python.org/issue1677688 — "Support CREATE_SUSPENDED flag in
subprocess.py for Win32", tracked issue, still open at time of this session's search,
migrated to github.com/python/cpython/issues/44688]`. This means the textbook
race-free pattern named in D-07's own wording — "create suspended, assign to job,
resume" — **is not achievable through `subprocess.Popen` alone**.

**Two real options, both requiring a planner decision:**

1. **Accept the narrow race window (`[ASSUMED]` recommendation).** Call
   `subprocess.Popen(...)` normally (not suspended), then call
   `AssignProcessToJobObject` **as the very next statement**, before doing anything
   else (no I/O, no logging in between). The race window is the interval between the
   OS actually starting to execute the child's first instruction and this Python
   process's very next line running — realistically microseconds. A learner's code
   would have to spawn a grandchild in its own first few instructions, faster than the
   parent Python process can make one more WinAPI call, to escape. Given D-10's
   explicit "stops accidents, not deliberate escapes" framing, this is consistent with
   the project's own stated threat model and is the pragmatic choice.
2. **Drop to `_winapi.CreateProcess` directly** (the undocumented internal module
   CPython's own `subprocess.py` uses on Windows) to get the real thread handle, then
   call `ctypes.windll.kernel32.ResumeThread` after assigning the job. This eliminates
   the race entirely but means bypassing the public `subprocess.Popen` API for this one
   code path, which is more code to maintain and relies on `_winapi` (an internal,
   underscore-prefixed module with no stability guarantee across Python versions,
   though it has been stable in practice since 3.3).

This research recommends **option 1**, with the choice and its reasoning recorded
explicitly in the plan (not silently assumed), because it keeps the runner on the
public `subprocess` API entirely, and the residual risk is squarely inside CODE-05's
own documented limit.

### `ctypes` structures and call sequence

`[CITED: learn.microsoft.com/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information,
ns-winnt-jobobject_basic_limit_information, nf-jobapi2-createjobobjectw,
nf-jobapi2-assignprocesstojobobject, nf-jobapi2-setinformationjobobject — all fetched
this session]`. C struct layout, translated to `ctypes`:

```python
import ctypes
from ctypes import wintypes

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount",  ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount",   ctypes.c_ulonglong),
        ("WriteTransferCount",  ctypes.c_ulonglong),
        ("OtherTransferCount",  ctypes.c_ulonglong),
    ]

class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),     # LARGE_INTEGER
        ("PerJobUserTimeLimit",     ctypes.c_int64),
        ("LimitFlags",              wintypes.DWORD),
        ("MinimumWorkingSetSize",   ctypes.c_size_t),
        ("MaximumWorkingSetSize",   ctypes.c_size_t),
        ("ActiveProcessLimit",      wintypes.DWORD),
        ("Affinity",                ctypes.c_size_t),    # ULONG_PTR
        ("PriorityClass",           wintypes.DWORD),
        ("SchedulingClass",         wintypes.DWORD),
    ]

class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo",                IO_COUNTERS),
        ("ProcessMemoryLimit",    ctypes.c_size_t),
        ("JobMemoryLimit",        ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed",     ctypes.c_size_t),
    ]

JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9     # JOBOBJECTINFOCLASS enum value `[CITED — commonly
                                           # documented constant, not independently re-verified
                                           # against a primary MS enum table this session;
                                           # planner should confirm against <winnt.h> or an
                                           # authoritative header dump before shipping]`

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

def create_job_with_kill_on_close():
    hjob = kernel32.CreateJobObjectW(None, None)
    if not hjob:
        raise ctypes.WinError(ctypes.get_last_error())
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    ok = kernel32.SetInformationJobObject(
        hjob, JobObjectExtendedLimitInformation,
        ctypes.byref(info), ctypes.sizeof(info))
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    return hjob

def assign_and_run(hjob, popen_obj):
    PROCESS_ALL_ACCESS = 0x1F0FFF
    hproc = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, popen_obj.pid)
    if not hproc:
        raise ctypes.WinError(ctypes.get_last_error())
    ok = kernel32.AssignProcessToJobObject(hjob, hproc)
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    return hproc

# On timeout: kernel32.CloseHandle(hjob) kills the whole tree because of
# JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE -- no separate TerminateProcess call needed
# once the job handle itself is closed and it was the LAST handle to that job object.
```

`AssignProcessToJobObject` needs a process handle with sufficient access rights —
`OpenProcess(PROCESS_ALL_ACCESS, False, pid)` using the pid `subprocess.Popen` already
exposes (`proc.pid`), rather than trying to extract a raw handle from `Popen` (which,
per the `CREATE_SUSPENDED` finding above, is not reliably exposed for this purpose).

**`taskkill /T /F /PID` fallback (D-07's named fallback):**

```python
subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                capture_output=True, timeout=5)
```

`/T` kills the process tree, `/F` forces termination. This is a documented, always-
available Windows utility rather than another WinAPI call, making it a reasonable
"if the Job Object cannot be created" fallback per D-07's own wording, though it is
markedly less certain than a Job Object close for a process that has already
reparented itself away from its original parent (a `taskkill /T` walks the process
tree by **parent PID at the time of the query**, which can already be stale for a
process that daemonized — the same "deliberate escape, not covered" caveat applies).

### Nested-job note

Since Windows 8 / Server 2012, a process assigned to a job automatically places its
own future children in the same job by default (nested job support), **provided** the
child is created after the parent's own `AssignProcessToJobObject` call completes. This
is exactly the CREATE_SUSPENDED race described above — the window this project accepts
rather than closes.

## Timeout + Output-Cap Interaction

### Why `communicate(timeout=)` alone is insufficient for the 64 KB cap

`subprocess.Popen.communicate(timeout=N)` reads stdout/stderr to completion (or until
the process exits) before returning, buffering the **entire** output in memory. An
infinite loop that `print()`s continuously would have `communicate()` accumulate
unbounded memory for the full `timeout_seconds` window before `TimeoutExpired` fires —
the output cap would never actually bound anything if enforced only after
`communicate()` returns.

### Recommended shape: threaded incremental reads with an early-stop cap

```python
import threading

def _drain(pipe, cap_bytes, buf, truncated_flag, stop_event):
    total = 0
    while not stop_event.is_set():
        chunk = pipe.read(4096)          # blocks until data or EOF; fine on its own thread
        if not chunk:
            break
        buf.append(chunk)
        total += len(chunk)
        if total >= cap_bytes:
            truncated_flag.set()
            stop_event.set()             # signal the main thread to kill early
            # keep draining below the cap check so the child never blocks on a full
            # pipe even after truncation is detected -- do NOT `break` here
    # continue reading (and discarding) until EOF, so the child is never left blocked
    # on a full OS pipe buffer waiting for a reader that stopped
    while True:
        chunk = pipe.read(4096)
        if not chunk:
            break
```

Two threads (stdout, stderr), a `threading.Event` the main thread also watches
alongside the timeout deadline, so a truncation can trigger an early kill rather than
waiting out the full `timeout_seconds` for output that has already exceeded the cap.
This directly answers the additional-context brief's "how to enforce a 64 KB output cap
without deadlocking on a full pipe buffer" — the deadlock risk is specifically in
*stopping* a read loop early without continuing to drain (a half-drained pipe with an
unread remainder blocks the child on its next `write()`), which the "keep reading past
the cap, just stop accumulating" structure above avoids.

### stdin EOF vs. timeout

D-08's second bound: `proc.stdin.write(case["stdin"].encode()); proc.stdin.close()`
immediately after the write (not `communicate(input=...)`, which keeps stdin open
until it writes the whole input then closes it anyway internally — functionally
equivalent, but writing and closing directly is clearer about the EOF-not-timeout
distinction the brief asks for). Closing stdin sends real EOF to the child process
immediately, so a program that reads all of stdin (`sys.stdin.read()`) or reads until
EOF in a loop (`for line in sys.stdin:`) terminates its own read normally rather than
blocking — this is what makes a program that "waits for more input" fail via EOF
(likely producing wrong/incomplete output, scored as a normal case failure) rather than
via the timeout (which would otherwise misleadingly report "timed out" for a program
that was, in fact, correctly waiting for input this test harness intentionally never
sends more of).

### Interpreter invocation shape

Since stdin is reserved for case input, the learner's source must be delivered via a
file argument, not stdin:

```python
import tempfile, os

def run_one_case(argv_template, source, case, timeout_s, max_output_bytes):
    with tempfile.TemporaryDirectory() as td:
        src_path = os.path.join(td, "submission.py")
        with open(src_path, "w", encoding="utf-8") as fh:
            fh.write(source)
        argv = [a.replace("{python}", sys.executable).replace("{file}", src_path)
                for a in argv_template]
        # e.g. argv_template = ["{python}", "-I", "{file}"]
        # -I: isolated mode -- ignores PYTHONPATH / user site-packages / PYTHON* env
        # vars. This is NOT a sandbox and makes no such claim; it only prevents the
        # runner's OWN interpreter configuration from accidentally leaking into (or
        # being polluted by) the learner's run, which is exactly the class of
        # "accident" D-10's honest-limits sentence is scoped to.
        ...
```

`-I` (isolated mode) is a genuine, cheap, stdlib-only accident-guard consistent with
D-10's framing — it is explicitly NOT presented as a security boundary in this
recommendation, matching CODE-05's requirement.

## Editor

### Pixel-alignment pitfalls, concretely

`05-UI-SPEC.md`'s Editor Interaction Contract already locks the markup shape and the
sync rules (`[VERIFIED: 05-UI-SPEC.md:161-207]`, read in full this session — not
re-quoted here since it is the phase's own approved design contract, not external
research). The concrete pixel-alignment failure modes an executor will hit if the
contract's "Font sync is mandatory" line is not followed literally:

- **`box-sizing` mismatch:** if `.gutter` and `textarea.code` do not share the same
  `box-sizing` (the template's global `*{box-sizing:border-box}` at
  `[VERIFIED: quiz_page.py:14]` already applies project-wide, so this is inherited
  correctly by default — but any per-element override would break it).
- **Line-height rounding:** a `line-height` expressed as a unitless number (`1.5`) is
  computed relative to each element's own `font-size`; since both elements share
  `font-size:14px` per the UI-SPEC, `1.5 * 14px = 21px` computes identically in both —
  but if a future edit changes only one element's `font-size` without the other, the
  computed line box heights diverge by a sub-pixel amount that compounds over many
  lines, eventually producing a visible one-line drift at the bottom of a long paste
  (the UI-SPEC's own "verified against a 500-line paste" backstop item exists for
  exactly this reason).
- **Padding-top parity:** the UI-SPEC's markup note says the gutter and textarea "share
  identical... top padding" — a scrollbar appearing on the textarea (horizontal, from
  `overflow-x:auto` under `white-space:pre`) does not affect vertical alignment, but a
  *vertical* scrollbar width difference between the two elements would, if either
  element were allowed to show one — the gutter must never show its own scrollbar
  (`overflow:hidden`, matching `.gutter`'s locked markup) so its content is driven
  purely by `scrollTop` mirroring, never by direct user scroll interaction.
- **Font metrics across the monospace stack:** the shared stack
  (`ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace`) resolves to a
  *different actual font* per OS (SF Mono on macOS, Consolas on Windows, a Linux
  distro's `ui-monospace` fallback). Within one page load both elements resolve to the
  *same* font (identical `font-family` string), so cross-element alignment holds
  regardless of which physical font wins — the risk is only if the two elements' CSS
  rules ever specify the stack differently (a copy-paste maintenance risk more than a
  technical one, worth a single shared CSS custom property or class name rather than
  two independent declarations).

### Tab/Shift-Tab and undo history

`05-UI-SPEC.md`'s contract: Tab inserts `\t` at the cursor (replacing a selection if
one exists) via `preventDefault()`; Shift-Tab dedents the current line by one `\t` or up
to four spaces. A vanilla-JS implementation using `document.execCommand('insertText',
false, '\t')` (rather than directly mutating `textarea.value` and manually resetting
`selectionStart`/`selectionEnd`) **preserves the browser's native undo stack** — a
direct `.value =` assignment clears `undo`/`redo` history entirely in every major
browser, which is a real, easy-to-miss regression versus typing normally. `execCommand`
is deprecated for many use cases but remains the only reliable way to mutate a
`<textarea>`'s content while keeping native undo intact; the alternative (manually
tracking an undo stack in JS) is explicitly out of scope per the UI-SPEC's "Explicitly
not built by this document's contract" list (no mention of undo, but adding a custom
undo stack would be scope creep past D-11 exactly as syntax highlighting is called out
as being). `[ASSUMED]` — recommend `execCommand('insertText', ...)` where supported,
with a plain `.value` splice fallback for the (rare) browser that lacks it, since losing
undo history on Tab is a real but non-blocking UX regression, not a CODE-03 failure
(CODE-03 only requires "tab inserts a tab", not "tab preserves undo").

### Why wrapping must be off

Already locked by the UI-SPEC and independently confirmed by this research: soft-wrap
under `white-space: normal` would make one logical line span multiple visual rows,
breaking the 1-based gutter's row-per-line correspondence CODE-03 exists to guarantee
("line numbers a rubric point can reference"). `white-space: pre` plus
`overflow-x: auto` is the only combination that keeps "gutter row N == textarea line N"
true at any content width, which the UI-SPEC's contract already states as a deliberate
tradeoff, not an oversight.

## Common Pitfalls

### Pitfall 1: `THIS_PHASE` watermark and the parallel-track roadmap

**What goes wrong:** `[VERIFIED: surfaces/settings.py:26-30]`:

> "This phase's own identifier; a key whose x-itembank-phase is at or below this
> number is 'read by this phase' rather than reported as inert."
> `THIS_PHASE = 2.1`

If Phase 5 bumps `THIS_PHASE` to `5` when it lands its `check.*` settings keys,
`itembank config`'s status column would report **every** key with `x-itembank-phase`
between `2.1` and `5` — currently only `"theme"` at `x-itembank-phase: 4`
(`[VERIFIED: schemas/settings.schema.json:16]`) — as "read by this phase", even though
Phase 4 (theming) has not landed and does not actually read `theme` yet.

**Why it happens:** `ROADMAP.md`'s own "Execution Order" note states
`[VERIFIED: ROADMAP.md:367-369]`: "Phases 1, 2, 3, and 5 have no dependency on each
other and are parallel-eligible" — meaning Phase 5 can genuinely finish and merge
before Phase 4, breaking `THIS_PHASE`'s implicit assumption that phases land in numeric
order.

**How to avoid:** Only bump `THIS_PHASE` to a value that does not skip over any
not-yet-landed intervening phase's keys, OR set it to `5` but only for `check.*` keys
specifically (which is not how the constant works today — it is a single scalar
watermark, not a per-key set). The safe, minimal fix for this phase: leave `THIS_PHASE`
unbumped if Phase 4 has not landed by the time Phase 5 executes, and note the gap in the
plan rather than silently mis-reporting `theme`'s status. This is a genuine modeling
limitation in the existing mechanism, not something this phase needs to fully redesign
— flagged as an Open Question below.

**Warning signs:** `itembank config` printed after Phase 5 lands, showing `theme` as
"read by this phase" while Phase 4 is still `Not started` in `ROADMAP.md`.

### Pitfall 2: `answer_text()`/`response_text()` have no `check` branch

`[VERIFIED: runtime.py:219-227,230-255]` — `answer_text(q)` (used by `study`/export
surfaces) and `response_text(q, answer)` (used to render attempt-file text) both branch
on `q["type"]` with no `check` case; both would silently fall through to their final
`return ""` (for `response_text`) or `q.get("model", "")` (for `answer_text`, which
returns `""` for a `check` item since `check` items have no `"model"` key). This is not
a crash, but a silent gap: an attempt file rendered for a `check` item would show an
empty "what the learner answered" line, and `study`/export surfaces would show nothing
useful. Not required by CODE-01..05, but worth flagging so the planner explicitly scopes
it in or out (e.g. `response_text` could show the source's first N lines, or a
placeholder like "(code submission — see attempt file)").

### Pitfall 3: CI is Linux-only

`[VERIFIED: .github/workflows/ci.yml:6-7]` — `runs-on: ubuntu-latest`. The Windows Job
Object path, the `CREATE_SUSPENDED` gap, and `taskkill` fallback are **not exercised in
CI at all**. `tests/check_roundtrip.py` must platform-guard its Windows-specific
assertions (`if sys.platform == "win32":`) so the file still passes on Linux CI while
covering the POSIX path fully — and Success Criterion 3's Windows half can only be
verified end-to-end by manual execution on the target Windows 11 machine, the same
posture `01-01-PLAN.md`'s append-durability spike already established as this project's
precedent for Windows-specific behavior. This should become an explicit spike-result
artifact (matching `01-SPIKE-RESULT.md`'s precedent), not just code review.

### Pitfall 4: `lint()`'s `if not q.get("trap")` warning fires for `check` too

`[VERIFIED: model.py:536-537]` — `if not q.get("trap"): warnings.append(...)` runs
unconditionally for every type, including the branch this phase adds. A `check` item
plausibly has no "misconception this item weaponises" the way an `mc` distractor does
(the failure mode is a wrong program, not a chosen wrong option) — the planner should
decide whether `TRAP:` is meaningful for `check` items (e.g. "the off-by-one error this
case is designed to catch") or whether the warning should be suppressed for this type
the same way `WHY BEST` is (Pitfall in Format Contract section above). `[ASSUMED]` this
research leans toward keeping the warning (a `TRAP:` describing the misconception a case
targets is plausible pedagogical value), but flags it as a real authoring-friction
question, not a parsing bug.

## Code Examples

### Case-result shape returned by `runner.run_cases()`

```python
# Source: this session's design proposal, not copied from an external reference
[
    {"case_index": 0, "passed": True,  "actual": "5\n", "timed_out": False, "truncated": False},
    {"case_index": 1, "passed": False, "actual": "4\n", "timed_out": False, "truncated": False},
    {"case_index": 2, "passed": False, "actual": "",    "timed_out": True,  "truncated": False},
]
```

This shape carries everything `05-UI-SPEC.md`'s Copywriting Contract needs for the
per-case rows: `Passed`/`Failed`/`Failed — timed out after %ss`/`Failed — output was
cut off at %d KB` are all derivable from `(passed, timed_out, truncated)`, and
`"Your output"` is `actual` (subject to `[MATCH:]` mode comparison against the
authored `expected`, computed by `runner.py` itself — the comparison per D-04's
`exact|trimmed|regex` modes belongs in the runner, since it decides `passed`, which
belongs on the execution side of D-01's boundary, not inside `canonical_response`).

### `[MATCH:]` mode application (runner-side, not scorer-side)

```python
import re

def case_passed(match_mode, expected, actual):
    if match_mode == "exact":
        return actual == expected
    if match_mode == "trimmed":
        return actual.rstrip("\n") == expected.rstrip("\n")
    if match_mode == "regex":
        return re.fullmatch(expected, actual, re.S) is not None
    return False   # unknown mode -- should be caught by lint before this is ever reached
```

This lives in `runner.py`, not `runtime.py` — `[MATCH:]` interpretation is part of
deciding whether a case *passed*, which is upstream of the scorer's pure vector
comparison, consistent with D-01's boundary.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `preexec_fn=os.setsid` | `start_new_session=True` | Python 3.2+ | `preexec_fn` is documented as unsafe with threads in the parent process; `start_new_session` is the equivalent, thread-safe stdlib flag — already the mechanism D-07 names, no change needed |
| Manual `p.poll()` spin-loop for timeout | `Popen.wait(timeout=)` / `communicate(timeout=)` raising `TimeoutExpired` | Python 3.3+ | Standard since long before this project's 3.11 floor; no legacy pattern risk here |

**Deprecated/outdated:** none identified specific to this phase's stdlib surface —
`subprocess`, `ctypes`, and `threading` are all stable, actively-maintained stdlib
modules with no pending deprecation relevant to this use.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | Recommended fix for the purity-boundary gap (new `check_source` reserved field on the response event, threaded via `record_answer`/`do_submit`) | Purity Boundary | If the planner chooses a different shape (e.g. storing the vector as `answer` and the source in a separate NEW event type instead of a reserved field), the schema/evidence-writer changes differ; low risk either way since both are additive, but the plan must pick one explicitly |
| A2 | `SIGKILL` directly on timeout (no `SIGTERM`-then-wait escalation) | Process-Tree Kill — POSIX | If the planner prefers graceful `SIGTERM` first, add a short escalation window; changes nothing about the `killpg`/Job-Object mechanism itself, only the signal sequence |
| A3 | `JobObjectExtendedLimitInformation = 9` (the `JOBOBJECTINFOCLASS` enum value) | Process-Tree Kill — Windows | This is a commonly-cited constant but was not independently re-verified against a primary Microsoft enum table this session; if wrong, `SetInformationJobObject` fails at the WinAPI call with `ERROR_INVALID_PARAMETER`, caught by the existing `if not ok: raise ctypes.WinError(...)` guard — a loud failure on the target Windows machine during the manual spike, not a silent one |
| A4 | Accept the narrow `CREATE_SUSPENDED`-unavailable race window (option 1) rather than dropping to `_winapi.CreateProcess` (option 2) | Process-Tree Kill — Windows | If wrong (i.e., the accepted race proves unacceptable to the user), the fallback is documented (option 2) and does not require restarting the design — just swapping the process-spawn call inside `runner.py`'s Windows branch |
| A5 | Keep `::` as `CASE)`'s separator (do not switch to `FIELD_SEP`) and document the collision in `SPEC` instead | Format Contract | If a real bank later needs `::` inside expected stdout, the item cannot be authored correctly until switched to `FIELD_SEP` per D-03's own escape hatch — low risk given CSCI 1100's actual likely test content, but worth a `SPEC` sentence regardless |
| A6 | `execCommand('insertText', ...)` for Tab/Shift-Tab to preserve undo history | Editor | If unsupported in a target browser, falls back to a `.value` splice that loses undo on Tab — a UX regression, not a CODE-03 failure, since CODE-03 only requires the tab character be inserted |
| A7 | `check` items are excluded from the `missing_why_best` lint check the same way `short` is | Format Contract / Pitfall 4 | If not excluded, every real authored `check` item fails lint with a nonsensical error; low risk of being missed since it will surface immediately on the first fixture bank authored |

**If this table is empty:** not applicable — seven assumptions above need planner
confirmation before being treated as locked.

## Open Questions — Resolved at Plan Time

1. **`THIS_PHASE` watermark vs. the parallel-eligible roadmap**
   - What we know: `surfaces/settings.py:30`'s `THIS_PHASE` constant is a single scalar
     watermark, and the roadmap explicitly allows Phase 5 to land before Phase 3/4.
   - What's unclear: whether this phase should bump the constant at all, leave it, or
     whether this is worth a small structural fix (e.g. tracking landed-phase numbers
     as a set rather than a single watermark) as an in-scope cleanup.
   - Recommendation: leave `THIS_PHASE` unbumped unless Phase 4 has already landed by
     the time this phase executes; note the gap in the plan explicitly rather than
     silently accepting an incorrect "read by this phase" status line for `theme`.
   - **Resolution: RESOLVED.** Leave the scalar at `2.1`; Phase 5 settings remain usable
     while the status display does not falsely claim parallel Phase 3/4 delivery. Controlled
     by **05-03 Task 1, "The check settings group"**, including its explicit source gate.

2. **Two-level nested job scope for `check.max_output_bytes`-triggered early kill on
   Windows**
   - What we know: closing the job handle (`CloseHandle(hjob)`) kills the whole tree
     when `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` is set.
   - What's unclear: whether the early-kill-on-truncation path (triggered by the output
     drain thread's `stop_event`) needs a distinct code path from the timeout-triggered
     kill, or whether both can share one `close-the-job-handle` call. They almost
     certainly can share one path — this is a low-risk implementation detail flagged
     only so the executor does not accidentally build two kill mechanisms.
   - Recommendation: implement one `kill_tree(handle_or_pgid)` function per platform,
     called from both the timeout branch and the output-cap branch.
   - **Resolution: RESOLVED.** Timeout and output-cap triggers share the single
     `kill_tree()` path; Windows closes the assigned Job Object through that path and keeps
     the process-tree fallback behind it. Controlled by **05-02 Task 1, "The output cap
     fails the case and kills early"**, with the Job Object implementation completed by
     **05-02 Task 2**.

3. **Whether the offline-refusal branch in `quiz_page.py` needs its own JS unit test**
   - What we know: `CONCERNS.md` already flags "No test of JavaScript scoring logic" as
     a pre-existing gap (`canon()` in `quiz_page.py` has no test today).
   - What's unclear: whether `check`'s offline-refusal rendering (D-06, no `canon()`
     branch needed since `check` never reaches the client-side scoring path) should be
     covered by a Python-side test that inspects the generated HTML string for the
     locked refusal copy. **Ruling 16 (RESOLVED 2026-08-11) supersedes the "no JS test
     harness in this project" premise**: a JS test runner is adopted and recorded under
     §4a (`node --test tests/js/`, matching `05-VALIDATION.md`), but it executes
     DOM-level editor behaviours against the vendored CM6 bundle — it is not a
     whole-page render harness, so this refusal-copy question is still a Python-side
     string assertion over the built page.
   - Recommendation: a string-containment assertion in `tests/check_roundtrip.py`
     against the built page's HTML output (matching how `tests/serve_roundtrip.py`
     likely already asserts against rendered attempt-file text) is sufficient; no new
     JS test infrastructure is needed for this phase.
   - **Resolution: RESOLVED.** Use Python-side assertions over the generated HTML plus the
     end-of-phase human pass; no additional JS test is added for the refusal rendering
     (the JS runner from ruling 16 covers the editor's DOM behaviours against the vendored
     bundle, not whole-page copy). Controlled by **05-06
     Task 2, "The three refusal states and the offline skip control"**, and manually closed
     by **05-07 Task 3**.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python interpreter (`sys.executable`) | D-02's default `python` language entry — the interpreter under test IS the interpreter running the runner itself | Yes (this is a self-referential dependency; if this process is running, `sys.executable` is definitionally available) | 3.11+ per CI/CLAUDE.md | none needed |
| `ctypes.WinDLL("kernel32")` | Windows Job Object path | Yes on any Windows target — `kernel32.dll` is present on every Windows install | OS-provided, not versioned by this project | `taskkill /T /F /PID` (D-07's own named fallback) |
| `taskkill.exe` | Windows fallback kill | Yes — bundled with every supported Windows version | OS-provided | none further; this IS the fallback |
| Windows 11 dev machine (for manual spike verification) | CODE-04's Windows half, given CI is Linux-only | Confirmed present per this session's environment (`Platform: win32`, `OS Version: Windows 11 Enterprise 10.0.26220`) | — | none — this is the only verification path for the Windows branch until CI gains a Windows runner |

**Missing dependencies with no fallback:** none — every dependency above is either
stdlib, OS-bundled, or has an explicit fallback D-07 already names.

**Missing dependencies with fallback:** none currently missing; noted for completeness.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | none — direct-execution stdlib scripts, per `.claude/CLAUDE.md`'s "Test runner: Direct Python script execution (no pytest, unittest framework, or test runner dependency)" |
| Config file | none — `.github/workflows/ci.yml` runs `for t in tests/*.py; do python "$t" || exit 1; done` (`[VERIFIED: .github/workflows/ci.yml:69-74]`) |
| Quick run command | `python tests/check_roundtrip.py` |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` (matches CI exactly, `[VERIFIED: .github/workflows/ci.yml:71-73]`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|--------------------|--------------|
| CODE-01 | `check` item verified by running code, comparing to expected output | unit | `python tests/check_roundtrip.py` (multi-case pass/fail matrix) | ❌ Wave 0 |
| CODE-02 | Dichotomous score through `score_response()`, no second grading path | unit | `python tests/check_roundtrip.py` (assert `score_response` called with the vector, and matches evidence log's stored score) | ❌ Wave 0 |
| CODE-03 | Editor: monospace, working line numbers, Tab inserts a tab | JS runner (ruling 16) + string-assertion | `node --test tests/js/` executes Tab/Shift-Tab/Enter-Space and focus behaviours against the vendored CM6 bundle (05-05), plus `python tests/check_roundtrip.py` (asserts locked CSS/markup strings present in rendered page); the 500-line pixel pass stays manual at 05-07-T3 | ❌ Wave 0 |
| CODE-04 | Timeout + process-tree kill on both platforms, incl. grandchild | integration | `python tests/check_roundtrip.py` — POSIX assertions run everywhere; Windows-specific assertions platform-guarded and run only when `sys.platform == "win32"`, verified manually on the target Windows 11 machine per Pitfall 3 | ❌ Wave 0 |
| CODE-05 | Documentation states plainly this stops accidents, not escapes; no sandboxing claim | automated grep | `python tests/check_roundtrip.py` — case-insensitive grep over `model.SPEC` and the rendered `quiz_page.py` output for `sandbox`/`isolat`/`contain`, asserting zero matches, plus a byte-identity assertion between the two occurrences of the honest-limits sentence (matching `05-UI-SPEC.md`'s own closing note) | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python tests/check_roundtrip.py`
- **Per wave merge:** `for t in tests/*.py; do python "$t" || exit 1; done`
- **Phase gate:** Full suite green before `/gsd-verify-work`; Windows-specific
  assertions additionally require a manual pass on the target Windows 11 machine
  (Pitfall 3), recorded as a spike-result artifact matching `01-01-PLAN.md`'s
  precedent.

### Wave 0 Gaps

- [ ] `tests/check_roundtrip.py` — covers CODE-01 through CODE-05, new file, no
      existing test touches `check` at all.
- [ ] `fixtures/check_bank.md` — new synthetic fixture (guard-safe per `itembank
      guard`'s existing enforcement — no real content, matching every other fixture
      under `fixtures/`).
- [ ] `runner.py`'s own grandchild-spawning fixture script (inline in the test file or
      a separate `fixtures/`-adjacent helper — recommendation: inline as a string
      written to a temp file at test time, matching the "grandchild fixture" code
      example above, so nothing under `fixtures/` risks being mistaken for a real
      question bank by `itembank guard`).
- [ ] No framework install needed — stdlib only.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|-------------------|
| V2 Authentication | No | Single-user, no-auth tool by design (`.claude/CLAUDE.md`: "One. No accounts, no auth") |
| V3 Session Management | No | No web session/cookie model; `check.allow_lan` is a settings toggle, not a session concept |
| V4 Access Control | Partial | D-09's `--lan` refusal IS an access-control control, but explicitly not a security boundary claim — it is a default-closed convenience gate, matching D-10's honest posture |
| V5 Input Validation | Yes | `[LANG:]` validated against `check.languages` allowlist at lint time (`item.check_lang_unknown`) and again at execution time (runtime drift guard, per the UI-SPEC's "Language not in allowlist" copy) — never trusted as free text passed to `argv` |
| V6 Cryptography | No | Nothing in this phase touches cryptographic material |
| V11 Business Logic (informal mapping) | Yes | The "one scorer" invariant (`score_response()` reached identically from every path) IS this phase's core business-logic-integrity control — D-01/CODE-02's whole point |

### Known Threat Patterns for This Phase's Surface

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Arbitrary code execution via a learner-authored `check` submission | Elevation of Privilege (by design, disclosed) | **Explicitly not mitigated** — this is CODE-05's entire point. The mitigation that IS applied is scope-bounding (timeout, output cap, process-tree kill) against *accidental* resource exhaustion, not against a *deliberate* attempt to do something malicious with local code execution the learner already has the ability to run outside this tool anyway (they could just run `python evil.py` directly on their own machine) |
| `argv` injection via `[LANG:]` naming an arbitrary interpreter/argument | Tampering | `check.languages` is a settings-driven allowlist keyed by a fixed set of language names, never free text passed directly into `argv`; a `[LANG:]` value absent from the allowlist is a lint error, never silently accepted or defaulted |
| A phone on `--lan` running arbitrary code on the host | Elevation of Privilege | D-09: `check` execution refused by default when serving `--lan`, unless `check.allow_lan` is explicitly set true — the one place in this phase's design where the honest "no sandbox" disclosure has a matching default rather than only a warning |
| Output-cap bypass via a program that writes to a file instead of stdout | Denial of Service (disk exhaustion) | **Not mitigated by this phase's scope** — D-08 only bounds stdout/stderr and wall-clock time, not filesystem writes. Worth flagging: a learner's code running `open("/some/huge/path", "w")` in a loop is bounded only by the timeout, not by any output cap, since it never touches the piped streams the cap watches. Given `check.timeout_seconds` defaults to 5s, worst-case disk write in that window is bounded by disk throughput, not by this phase's `max_output_bytes` control — this is a real, if narrow, gap the honest-limits sentence's "accidents" framing already implicitly covers (a learner accidentally writing an unbounded file is exactly the class of accident being disclaimed, not defended against) |

## Project Constraints (from CLAUDE.md)

- **Python standard library only, no install step, no build step** — enforced
  throughout this research; `ctypes` is explicitly named as permitted stdlib. **The one
  JS vendored asset is CodeMirror 6 (ruling 5/11, RESOLVED 2026-08-11), pinned, hashed
  and license-reviewed under §4a — the earlier "no vendored asset beyond the KaTeX
  exception" line is SUPERSEDED.**
- **Network degrades, never blocks** — not directly implicated by this phase (`check`
  execution is local-only by design, D-06), but the daemon/CLI must keep functioning
  with the network unplugged regardless of `check`'s presence — no new network calls
  are introduced anywhere in this phase's design.
- **Data residency** — the learner's source code and per-case output stay on disk
  (evidence log) and are never transmitted anywhere; this phase introduces no new
  network egress.
- **Compatibility** — `CASE)`/`[LANG:]`/`[MATCH:]` are additive; a bank with no `check`
  item must parse byte-identically to today, confirmed by the stem-terminator and
  `TERMINATOR` regex analysis above (both are additive alternation extensions, not
  restructurings).
- **CSCI 1100 AI-use ban** — explicitly not implicated: `check` runs the learner's own
  code with no model involved anywhere in the execution path, a distinction
  `05-CONTEXT.md`'s Specific Ideas section already asks to be stated in this phase's own
  docs, which the `SPEC` text and/or a code comment in `runner.py` should restate.
- **Naming/style conventions** — `runner.py` should follow the established module-level
  docstring convention (explains WHY, not HOW; states its own architectural boundary
  the way `runtime.py:1-11` and `model.py:1-6` do), `cmd_`-prefixed CLI handlers if any
  new command surfaces are needed (none obviously required — `check` execution happens
  inside existing submit paths, not as a new top-level command), and dotted lint/error
  codes following the `tuple(sorted({...}))` pattern already established twice
  (`LINT_CODES`, `SETTINGS_CODES`).

## Sources

### Primary (HIGH confidence — read directly this session)

- `runtime.py` (full scoring/session module, lines 1-300) — `[VERIFIED]`
- `model.py` (full format-contract module, lines 1-567) — `[VERIFIED]`
- `evidence.py` (lines 310-410, response-event construction) — `[VERIFIED]`
- `surfaces/quiz.py` (lines 1-80, `record_answer`/`page_for`) — `[VERIFIED]`
- `surfaces/session.py` (full JSON session surface) — `[VERIFIED]`
- `surfaces/daemon.py` (route table, `handle_quiz_get`/`handle_quiz_answer`,
  `/api/submit` grep) — `[VERIFIED]`
- `surfaces/quiz_page.py` (full template — dispatch table, `canon()`, `verify()`,
  `settle()`, `chips()`, `close()`) — `[VERIFIED]`
- `surfaces/settings.py` (full settings surface, `THIS_PHASE`) — `[VERIFIED]`
- `surfaces/day.py` (lines 330-358, platform-branch precedent) — `[VERIFIED]`
- `schemas/settings.schema.json`, `schemas/item.schema.json`,
  `schemas/response.schema.json` (full) — `[VERIFIED]`
- `.github/workflows/ci.yml` (full) — `[VERIFIED]`
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md` (full) —
  `[VERIFIED]`
- `.planning/phases/05-check-item-type-code-editor/05-CONTEXT.md`,
  `05-UI-SPEC.md` — `[VERIFIED]`
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/ROADMAP.md` —
  `[VERIFIED]`

### Secondary (MEDIUM confidence — official docs, fetched this session)

- [JOBOBJECT_EXTENDED_LIMIT_INFORMATION structure](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information) — `[CITED]`
- [JOBOBJECT_BASIC_LIMIT_INFORMATION structure](https://learn.microsoft.com/en-us/windows/desktop/api/winnt/ns-winnt-jobobject_basic_limit_information) — `[CITED]`
- [CreateJobObjectW function](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-createjobobjectw) — `[CITED]`
- [AssignProcessToJobObject function](https://learn.microsoft.com/en-us/windows/desktop/api/jobapi2/nf-jobapi2-assignprocesstojobobject) — `[CITED]`
- [SetInformationJobObject function](https://learn.microsoft.com/en-us/windows/desktop/api/jobapi2/nf-jobapi2-setinformationjobobject) — `[CITED]`
- [IO_COUNTERS structure](https://learn.microsoft.com/en-us/windows/desktop/api/WinNT/ns-winnt-io_counters) — `[CITED]`
- [Python subprocess — Windows Constants](https://docs.python.org/3/library/subprocess.html) — `[CITED]`
- [bugs.python.org issue 1677688 — Support CREATE_SUSPENDED flag in subprocess.py for Win32](https://bugs.python.org/issue1677688) — `[CITED]`
- [Kill a Python subprocess and its children when a timeout is reached — Alexandra Zaharia](https://alexandra-zaharia.github.io/posts/kill-subprocess-and-its-children-on-timeout-python/) — `[CITED]`

### Tertiary (LOW confidence)

- `JobObjectExtendedLimitInformation = 9` (`JOBOBJECTINFOCLASS` enum value) — widely
  cited across secondary Windows-programming sources but not independently
  re-confirmed against a primary Microsoft enum listing this session; flagged as
  Assumption A3.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib-only, no version ambiguity, confirmed against CI's
  Python 3.11 pin.
- Architecture / purity boundary: HIGH — read directly from source, not inferred;
  this is the strongest finding in this document and materially refines D-01's
  implementation (not its design intent).
- Windows process-tree kill: MEDIUM — struct/function definitions CITED against
  Microsoft Learn, `CREATE_SUSPENDED` gap CITED against the Python bug tracker, but
  **not executed on the target machine this session** — the plan should treat D-07's
  Windows half as requiring a manual spike, not code review alone.
- Editor: HIGH for the pixel-alignment mechanics (standard CSS box model reasoning
  applied to the UI-SPEC's already-locked, already-verified markup); MEDIUM for the
  `execCommand`/undo-preservation recommendation (a UX nicety, not independently
  tested this session).
- Pitfalls: HIGH — all four pitfalls were found by reading the exact call sites this
  session, not inferred from documentation.

**Research date:** 2026-08-08
**Valid until:** 30 days for the stdlib/format-contract findings (stable); the Windows
Job Object findings should be treated as valid until the manual spike either confirms
or corrects Assumption A3 and A4 — after that spike, this document's Windows section
should be superseded by the spike-result artifact, matching `01-01-PLAN.md`'s
precedent.
