# Phase 1: Evidence Spine & Protocol Foundation - Research

**Researched:** 2026-08-06
**Domain:** Local-first event-sourced evidence store (stdlib-only), item identity schemes, Windows file-append durability, hand-rolled JSON Schema validation
**Confidence:** MEDIUM — the architectural pattern (append-only log + disposable projection) is HIGH confidence, well-established prior art; the Windows append-write mitigation is MEDIUM confidence, grounded in the official Python bug tracker plus two independent technical blog posts, but not empirically measured on this machine yet (that measurement is the recommended spike); everything about *this* codebase's integration points is VERIFIED by direct source read this session.

## Summary

Phase 1 replaces three unversioned, un-keyed, dual-writer stores (`_attempts/*.md`,
`_attempts/session_*.json`, `daily_log.md`) with one append-only JSONL event log, a
disposable derived index for queries, and a published protocol (schema versions +
machine-readable lint codes) an agent can read cold. CONTEXT.md has already locked the
two headline decisions the roadmap flagged as needing a design pass — opaque item IDs
with a separate content-hash fingerprint (D-01/D-02), and append-only JSONL as the
system of record (D-07/D-08) — so this research does not relitigate them. It grounds
them technically, and it resolves the two things CONTEXT.md explicitly left open for
research: what Windows actually guarantees for append writes, and what "write a minimal
JSON Schema validator vs. keep CI shallow" should concretely mean.

The single most consequential finding: **Windows does not give Python's `os.open`/`open(...,
"a")` a POSIX-equivalent atomic append guarantee.** The Microsoft C runtime implements
`O_APPEND` as `lseek(fd, 0, SEEK_END)` followed by `write()` — two steps, not one — so two
processes appending to the same log file at the same instant can interleave or clobber
each other's line, exactly the failure the roadmap's spike was called out to check before
the append pattern is trusted. This is now empirically-testable, not theoretical: it is a
still-open, officially-acknowledged Python bug (bpo-42606). The mitigation this research
recommends is a stdlib-only cross-platform advisory lock (`msvcrt.locking` on Windows,
`fcntl.flock` on POSIX) wrapped around a single `write()` syscall per event line, combined
with defensive reader-side parsing that already matches D-09's "skip and report a malformed
line" rule. A spike task belongs in the plan, first, blocking — Open Questions names exactly
what it must measure.

The second finding worth flagging before planning starts: **D-17's idempotency key
("session + item + attempt number + canonical answer") is not directly implementable for
`short` items**, because `runtime.canonical_response()` returns `None` for constructed
response by design (`runtime.py:78-79`). The key needs a documented extension — hash the
normalized short-answer text when the canonical form is `None` — or duplicate short-answer
resubmission cannot be detected the way PROTO-03 requires for every other type.

**Primary recommendation:** Build the evidence writer as a new peer module (`evidence.py`)
beside `runtime.py`, keep the JSONL log as the sole system of record with a stdlib
`sqlite3` file as the disposable derived index (both explicitly sanctioned by D-08), wrap
every append in a cross-platform lock, extend the idempotency key to cover `short` items
explicitly, and land the Windows durability spike as the first task in the phase — every
other evidence-writing task depends on its answer.

## Architectural Responsibility Map

This phase has one runtime tier: a local, single-process, stdlib-only Python CLI. There is
no browser, no daemon (that is Phase 2), and no network boundary in scope. The "tiers"
below are internal layers, not deployment tiers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Item identity (opaque ID + content hash) | Model layer (`model.py`) | — | Identity is a property of the bank format contract, parsed alongside every other field; CONTEXT.md D-02 keeps it out of `runtime.py` to preserve the no-import-from-runtime rule |
| Evidence append/read/idempotency/retraction | Runtime layer (new `evidence.py`, peer to `runtime.py`) | — | Matches "the only scorer" precedent — evidence needs one writer function every surface calls, not one per surface |
| Derived query index (objective-over-time) | Runtime layer (`evidence.py`) | Disk cache (`sqlite3` file) | D-08: log is truth, index is disposable; the index is a materialized view, not a second source of record |
| Legacy migration (`_attempts/*.md`, session JSON, `daily_log.md` → log) | New one-shot tool (`surfaces/migrate.py` or `tools/migrate_evidence.py`) | Runtime layer (calls `evidence.py`'s writer) | One-time/re-runnable operation, not a persistent surface; belongs beside other surfaces but is invoked once, not per-session |
| Renders (`_attempts/*.md`, session JSON, `daily_log.md` as views) | Surfaces layer | Runtime layer (reads from `evidence.py`) | D-11: these become outputs computed from the log, same shape as `page_item()` being a view over a question dict |
| Protocol surface (`schemas/`, lint codes, `itembank schema` command) | Model layer (schemas describe item/lint shape) + Surfaces layer (CLI command) | — | Mirrors `model.SPEC` — a contract lives beside the thing it describes, and a CLI command is the delivery mechanism (matches `spec` today) |
| CI schema validation | Build/CI (`.github/workflows/ci.yml`) | Model/Runtime (minimal validator module) | PROTO-04 requires CI to check runtime output against the schema; the validator itself is a small stdlib module the CI step imports |

## User Constraints (from CONTEXT.md)

<user_constraints>

### Locked Decisions

**Item Identity**
- **D-01:** An item's evidence key is an **opaque ID**, assigned at first lint. The
  **content hash is a separate field** stored beside it, used only for change
  detection — never as the key. Mitigates PITFALLS.md Pitfall 1.
  — Reversibility: one-way.
- **D-02:** The opaque ID **lives in the bank markdown** as a new additive item field.
  `model.py` keeps owning identity with no import from `runtime.py`.
  — Reversibility: one-way. **(Delegated to Claude's discretion — see below.)**
- **D-03:** **`lint` stays read-only.** It reports items missing an ID; a separate
  explicit action assigns them, so ID assignment appears in `git diff` before commit.
  — Reversibility: reversible.
- **D-04:** When lint detects a content hash drifted from the recorded one: **warn,
  update the hash, keep the evidence history attached.** Accepted risk: a genuine
  rewrite silently inherits the old item's trend data.
  — Reversibility: reversible.
- **D-05:** **Item IDs are globally unique across every bank.**
  — Reversibility: costly.
- **D-06:** **Objectives are namespaced by subject** (`emt:airway.opa`,
  `csci1100:loops.while`). Existing banks need a subject assigned at migration.
  — Reversibility: costly.

**Evidence Store**
- **D-07:** The store is a single **append-only JSONL event log**. One line per event.
  Plain text — readable, greppable, git-diffable.
  — Reversibility: one-way.
- **D-08:** **The log is the only authority.** Queries are served by a **disposable
  derived index**, rebuilt whenever the log has grown past it, deletable at any time
  with no loss. A `sqlite3` file is acceptable *as that cache* — never as the system
  of record.
  — Reversibility: reversible.
- **D-09:** **One log for everything** — every subject, session, and mode. The reader
  works line by line and **skips and reports** a malformed line rather than crashing.
  — Reversibility: costly.
- **D-10:** Reversibility (EVID-05) means **compensating events**. Undoing appends a
  retraction referencing the original event; nothing is removed. Every view honours
  retractions; any count shown to the learner must be post-retraction.
  — Reversibility: one-way.

**Migration**
- **D-11:** `_attempts/*.md`, session JSON, and `daily_log.md` become **renders
  generated on demand from the log**. They are outputs, never inputs.
  — Reversibility: one-way.
- **D-12:** Manual `short` marking moves to a **`mark` command plus the equivalent
  route**, appending a mark event. **The command must accept a batch.**
  — Reversibility: reversible.
- **D-13:** Migration is **re-runnable and idempotent**, with **`--dry-run` first**.
  Every source record maps to a deterministic event identity so a second run imports
  nothing new.
  — Reversibility: reversible.
- **D-14:** Old records keyed by positional `Qn` that cannot resolve to an item ID are
  **imported as unresolved, never dropped** — carries the original `Qn`, its source
  file, and no item ID. No stem-similarity guessing.
  — Reversibility: reversible.

**Protocol Surface**
- **D-15:** The published contract is **JSON Schema files in a `schemas/` directory** —
  one per contract: item, session, response, report, lint error. CI validates real
  runtime output against them. **Open cost the planner must solve explicitly:** no
  stdlib JSON Schema validator exists — either write a minimal one or keep CI shallow.
  — Reversibility: one-way.
- **D-16:** Lint errors carry **namespaced dotted codes** (`item.missing_key`,
  `item.duplicate_id`, `lesson.ref_not_found`) alongside the field at fault and the
  human-readable text. Codes are an API.
  — Reversibility: one-way.
- **D-17:** **Idempotency key is session + item + attempt number + canonical answer**,
  using the existing `runtime.canonical_response()`. A retried call inside one attempt
  dedupes (`already_recorded`); a genuine second attempt records.
  — Reversibility: one-way.
- **D-18:** **Attempt number is defined in this phase**, ahead of Phase 6's use of it.
  The runtime increments it when it hands an item back after a wrong answer.
  — Reversibility: one-way.

### Claude's Discretion

- **D-02 (where the opaque ID physically lives)** — user said "do what is best since I
  don't understand." Claude chose the bank-markdown field with the read-only-lint
  mitigation. If a planner finds writing to private bank files unacceptable in
  practice, the fallback is a sidecar index, and reversing this must be raised as a
  decision checkpoint, not made quietly.
- Event field naming, log file location, index file format, and the internal shape of
  the rebuild pass are unconstrained — this research proposes concrete defaults below,
  all flagged `[ASSUMED]` where they go beyond what CONTEXT.md fixed.

### Deferred Ideas (OUT OF SCOPE)

- Item deletion and retirement semantics — needed before Phase 11's auditor.
- Whether old files are deleted after a verified migration, or left in place.
- Whether `day`'s streak/tick data migrates into the same log — closer to Phase 10.
- PROTO-01 version-bump policy (what counts as a breaking schema change).
- How a no-repo-context agent physically *receives* the `schemas/` files (PROTO-05) —
  this research proposes a `schema` CLI command mirroring `spec` (see Architecture
  Patterns), flagged `[ASSUMED]` since it was not decided in discussion.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EVID-01 | Item keeps identity across bank edits | Opaque-ID + content-hash design (D-01/D-02), grounded against `model.py:40`'s current positional `"id": "q" + number` |
| EVID-02 | Stem edit doesn't orphan history; lint warns on drift | D-04 warn-update-keep-history flow, extends `model.lint()` at `model.py:207-303` |
| EVID-03 | One store replaces three; each becomes a view | JSONL log design (D-07/D-08/D-11); render functions read the log, mirroring `runtime.page_item()`'s "view over a dict" pattern |
| EVID-04 | Single cross-subject/cross-session objective query | Derived-index design (sqlite3-backed, see Don't Hand-Roll and Code Examples) |
| EVID-05 | Every write auditable and reversible | Compensating-event design (D-10), `retracts` field in event schema below |
| EVID-06 | Migration loses no recorded response | Migration strategy section: deterministic source-record identity, dry-run count reconciliation, unresolved-import rule (D-13/D-14) |
| EVID-07 | Response time, confidence, error category, hint tier, mode, review state all recorded | Event field set proposed below, with explicit call-outs for the three fields (`response_time_ms`, `confidence`, `error_category`) that need new CLI plumbing that does not exist today |
| EVID-08 | Drill-mode "correct" distinguishable from exam-mode "correct" | `mode` field on every event, sourced from the session's existing `mode` field (`surfaces/cli.py:126`) |
| PROTO-01 | Items, sessions, responses, reports carry explicit schema version | `schemas/*.json` with a `version` field; runtime payloads stamp `schema_version` (extends `SESSION_VERSION` pattern at `runtime.py:20`) |
| PROTO-02 | Lint emits machine-readable code + field + human text | `LintError` namedtuple design, with the three existing string-concatenation call sites that must change together identified by file:line |
| PROTO-03 | Duplicate submit doesn't double-record; tool states which happened | Idempotency-key design (D-17), extended for `short` items (gap identified in Summary) |
| PROTO-04 | Published schema/contract fixture; CI checks runtime against it | Minimal stdlib JSON Schema validator recommendation, CI step design |
| PROTO-05 | No-repo-context agent can read contract, run a session, interpret evidence | `itembank schema` command proposal (mirrors `spec`); `schemas/` files are self-contained JSON |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `json` | stdlib (3.11+) | Event serialization (JSONL lines), schema files | Already used throughout `runtime.py`/`surfaces/session.py`; no reason to diverge |
| `hashlib` | stdlib (3.11+) | Content-hash fingerprint for item identity (D-01) | `sha256`, well-vetted, no hand-rolled hashing |
| `uuid` | stdlib (3.11+) | Opaque item IDs, event IDs, session IDs (already used at `surfaces/session.py:19` for `uuid.uuid4().hex`) | Existing precedent in this exact codebase |
| `sqlite3` | stdlib (3.11+) | Recommended backend for the disposable derived index (D-08 explicitly sanctions a sqlite3 file "as that cache") | [CITED: docs.python.org/3/library/sqlite3.html] — bundled with CPython since 2.5; gives real indexed queries for "objective X over time" without adding a dependency |
| `msvcrt` | stdlib, **Windows-only** (3.11+) | Advisory file locking (`msvcrt.locking`) to serialize concurrent appends on Windows, working around the CRT's non-atomic `O_APPEND` | [CITED: docs.python.org/3/library/msvcrt.html] |
| `fcntl` | stdlib, **POSIX-only** (3.11+) | Advisory file locking (`fcntl.flock`) for the same purpose on Linux/macOS (CI runs `ubuntu-latest` — see `.github/workflows/ci.yml:7`) | [CITED: docs.python.org/3/library/fcntl.html] |
| `re`, `collections`, `os`, `sys` | stdlib | Already the whole toolkit `model.py`/`runtime.py` use | No new usage patterns needed |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `ctypes` | stdlib | Alternative to `msvcrt.locking`: call `CreateFileW` directly with `FILE_APPEND_DATA` for true OS-level atomic append on Windows | Only if the spike shows the lock-based approach is insufficient; higher implementation/testing risk (manual `HANDLE`/struct marshaling) for a benefit (true kernel-level atomicity vs. serialized-write-with-defensive-read) that is hard to observe in a single-learner workload — **not** the primary recommendation |
| `datetime` | stdlib | `ts` field on every event, ISO 8601 UTC | Matches the timestamp shape already in this repo — `.planning/STATE.md:9` uses `"last_updated": "2026-08-06T14:49:25.025Z"` `[VERIFIED: .planning/STATE.md:9]` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-rolled JSON Schema validator | `jsonschema` (PyPI) | Full Draft 2020-12 compliance, but violates the stdlib-only constraint (PROJECT.md Constraints: "Tech stack: Python standard library only... no install step") — not viable here |
| `sqlite3`-backed derived index | Pure-JSON index file, hand-rolled | Simpler code, zero new concepts, but no real query engine — "objective X over time" becomes a linear scan of a growing JSON blob held in memory; acceptable at true MVP scale but throws away the indexed-query benefit D-08 exists to buy. Flagged as planner's discretion, not this research's recommendation. |
| `msvcrt.locking`/`fcntl.flock` advisory lock | `ctypes` + `CreateFileW(..., FILE_APPEND_DATA)` | True OS atomicity vs. simpler, better-tested stdlib API with equivalent practical guarantee for this workload — see Package/tool comparison above |

**Installation:**
```bash
# Nothing to install. Every recommended module ships with CPython 3.11+.
python --version   # confirm >= 3.11 as already required by PROJECT.md
```

**Version verification:** Not applicable — no external packages are introduced by this
phase. All recommended modules (`json`, `hashlib`, `uuid`, `sqlite3`, `msvcrt`, `fcntl`,
`ctypes`, `datetime`) are part of the Python 3.11+ standard library and require no
registry lookup.

## Package Legitimacy Audit

**Not applicable.** This phase introduces zero external packages — every recommendation
above is a Python 3.11+ standard-library module, consistent with the project's hard
"standard library only, no install step" constraint (`.planning/PROJECT.md` Constraints).
The Package Legitimacy Gate (npm/pip/cargo registry check) has nothing to check.

**Packages removed due to `[SLOP]` verdict:** none — none were ever proposed.
**Packages flagged as suspicious `[SUS]`:** none.

## Architecture Patterns

### System Architecture Diagram

```text
                    ┌─────────────────────────────────────────┐
                    │           Legacy stores (read-only        │
                    │           inputs to migration ONLY)        │
                    │  _attempts/*.md | session_*.json |         │
                    │  daily_log.md                              │
                    └───────────────────┬─────────────────────┘
                                        │ one-time / re-runnable,
                                        │ --dry-run first (D-13)
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │        Migration tool (new)                │
                    │  - deterministic source-record identity    │
                    │  - resolves item_id where possible          │
                    │  - imports unresolved records, never drops  │
                    │  - reports pre/post counts (EVID-06)         │
                    └───────────────────┬─────────────────────┘
                                        │ calls the ONE evidence writer
                                        ▼
┌──────────────┐    ┌─────────────────────────────────────────┐
│ CLI surfaces  │───▶│         evidence.py (new, runtime tier)    │
│ start/submit/ │    │  append_event()   — locked, single write() │
│ mark/session  │    │  idempotency check — dedupe_key lookup     │
└──────────────┘    │  retract_event()  — compensating events    │
                    │  rebuild_index()  — disposable, sqlite3     │
                    └───────────────────┬─────────────────────┘
                                        │ single writer,
                                        │ append-only, one line/event
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │     evidence.jsonl  (system of record)     │
                    │  one JSON object per line, D-07/D-09        │
                    └───────────────────┬─────────────────────┘
                          │ replay/rebuild                │ read
                          ▼                                ▼
            ┌───────────────────────┐          ┌───────────────────────┐
            │  evidence_index.sqlite3 │          │   Render functions      │
            │  (disposable, D-08)      │          │  attempt.md / session.  │
            │  objective→events index  │          │  json / daily_log.md    │
            └───────────┬───────────┘          │  view (D-11)             │
                        │ query                └───────────────────────┘
                        ▼
            ┌───────────────────────┐
            │ "how am I doing on X   │
            │  over time" (EVID-04)  │
            └───────────────────────┘
```

A reader can trace the primary use case: a learner submits a response → the surface
calls the one evidence writer → the writer locks, dedupes, and appends one line → the
index is rebuilt (lazily) from the log → three legacy-shaped views and one trend query
are all reads over the same log, never a second write path.

### Recommended Project Structure
```
model.py              # + opaque ID field parsing, content-hash computation,
                       #   coded lint errors (extends existing lint())
runtime.py            # unchanged core (scoring, canonical_response) — evidence
                       #   logic does NOT get bolted on here; see evidence.py
evidence.py            # NEW peer module: append_event, idempotency check,
                       #   retract_event, rebuild_index, render helpers
schemas/
├── item.schema.json    # NEW — public_item()/explain_payload() shape + version
├── session.schema.json # NEW — session dict shape + version
├── response.schema.json# NEW — one evidence event's shape + version
├── report.schema.json  # NEW — session_summary()/objective-query output + version
└── lint_error.schema.json # NEW — LintError shape + version
surfaces/
├── evidence_cli.py      # NEW — `mark` command (batch), `schema` command
├── migrate.py            # NEW — one-shot/re-runnable migration tool, --dry-run
├── session.py             # start/next/submit call evidence.append_event()
├── quiz.py                 # cmd_serve calls evidence.append_event(); attempt.md
                            #   becomes evidence.render_attempt_md() output
└── day.py                   # write_day_log() becomes evidence.render_daily_log()
_evidence/
├── evidence.jsonl          # the system of record (D-07)
└── evidence_index.sqlite3  # disposable derived index (D-08) — safe to delete
tests/
├── evidence_roundtrip.py    # NEW — append/read/retract/idempotency/migration counts
└── protocol_roundtrip.py     # NEW — schema versions present, lint codes shape,
                               #   schemas/ files self-consistent
```

### Pattern 1: Opaque ID + content-hash fingerprint (identity survives edits)

**What:** Assign a stable UUID at first lint-triggered ID-assignment action; store a
`sha256` of the normalized stem+options+correct-answer text beside it as a separate
`content_hash` field. Evidence keys off the opaque ID only. `lint` (read-only) reports
drift; a separate action updates the hash and keeps history (D-04).

**When to use:** Every item, from first assignment onward. This is the load-bearing
mechanism for EVID-01/EVID-02 and the direct fix for PITFALLS.md Pitfall 1.

**Example — grounded in the actual current shape** `[VERIFIED: model.py:39-51]`:
```python
# model.py currently builds the "common" dict like this (verbatim, model.py:39-51):
#   common = {
#       "id": "q" + number if number else "",
#       "number": int(number) if number else 0,
#       "type": qtype,
#       "stem": stem,
#       "difficulty": grab(r"\(difficulty:\s*([^)]+)\)", ch),
#       "objective": grab(r"\[OBJECTIVE:\s*(.*?)\]", ch),
#       "why": section("WHY BEST", ch),
#       "disc": section("KEY DISCRIMINATOR", ch),
#       "second": section("SECOND-BEST", ch),
#       "trap": section("TRAP", ch),
#       "conf": grab(r"(?m)^CONFIDENCE:\s*(.*?)\s*(?=\n|\Z)", ch),
#   }
# Today "id" is positional ("q7"), reassigned every parse if item order changes.
# D-01/D-02 add two NEW additive fields, parsed the same way as everything else:
#   "item_id":      grab(r"(?m)^\[ID:\s*(\S+)\s*\]", ch)          # empty until assigned
#   "content_hash": grab(r"(?m)^\[HASH:\s*(\S+)\s*\]", ch)         # empty until assigned
# A bank with neither line still parses byte-identically for every OTHER field —
# additive, per PROJECT.md's compatibility constraint.
```

### Pattern 2: Cross-platform locked append (Windows durability mitigation)

**What:** Wrap every event append in an advisory lock (`msvcrt.locking` on Windows,
`fcntl.flock` on POSIX) and issue exactly one `write()` syscall for the fully-encoded
line, so torn writes are minimized and interleaving between processes is eliminated —
without any external dependency.

**When to use:** Every call to `evidence.append_event()`, without exception. This is
the direct mitigation for the Windows append-write durability question CONTEXT.md
flagged for research.

**Example:**
```python
# Source: docs.python.org/3/library/msvcrt.html, docs.python.org/3/library/fcntl.html
# (both confirmed this session — see Sources)
import json, os, sys

def append_event(log_path, event: dict) -> None:
    line = (json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8")
    fd = os.open(log_path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        if sys.platform == "win32":
            import msvcrt
            # Lock a 1-byte region at offset 0 as a mutex convention; the byte
            # itself is never read. LK_LOCK blocks with retries (up to ~10s).
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            try:
                os.lseek(fd, 0, os.SEEK_END)
                os.write(fd, line)          # single syscall — minimizes torn-write risk
            finally:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                os.write(fd, line)          # O_APPEND is genuinely atomic on POSIX
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)
```
*Why the CRT's `O_APPEND` is not trusted directly on Windows:* the Microsoft C runtime
implements `O_APPEND` as `lseek(fd, 0, SEEK_END)` then `write()` — not one atomic step —
which is the documented cause of a still-open Python bug
`[CITED: bugs.python.org/issue42606]`. On local NTFS, writes up to the drive's sector
size (~512B–4KB, comfortably larger than one JSON event line) are independently reported
as atomic at the hardware/filesystem level `[CITED: nblumhardt.com/2016/08/atomic-shared-log-file-writes]`
`[CITED: antonymale.co.uk/windows-atomic-file-writes.html]`, which is why "one `write()`
call while holding a lock" is the recommended combination rather than the lock alone.

### Pattern 3: Disposable derived index for cross-subject queries (EVID-04)

**What:** A `sqlite3` file rebuilt from the JSONL log, holding one row per (non-retracted)
event, indexed by `objective`. Deleting it and re-running the rebuild is always safe and
always correct — it is a materialized view, never a second source of truth (D-08).

**When to use:** Any query answering "how am I doing on objective X over time" (EVID-04),
and any future selection/trend work (Phase 7, Phase 10) that reads the same shape.

**Example:**
```python
import sqlite3, json

def rebuild_index(log_path, index_path):
    con = sqlite3.connect(index_path)
    con.execute("DROP TABLE IF EXISTS events")
    con.execute("""CREATE TABLE events (
        event_id TEXT PRIMARY KEY, ts TEXT, session_id TEXT, item_id TEXT,
        objective TEXT, mode TEXT, score TEXT, attempt_number INTEGER,
        retracted INTEGER DEFAULT 0)""")
    con.execute("CREATE INDEX idx_objective ON events(objective, ts)")
    retracted = set()
    rows = []
    with open(log_path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except ValueError:
                print("warn  evidence.jsonl:%d malformed, skipped" % lineno)
                continue                       # D-09: skip and report, never crash
            if ev.get("event_type") == "retraction":
                retracted.add(ev["retracts"])
                continue
            if ev.get("event_type") != "response":
                continue
            rows.append((ev["event_id"], ev["ts"], ev["session_id"], ev.get("item_id"),
                        ev.get("objective", ""), ev.get("mode", ""),
                        json.dumps(ev.get("score")), ev.get("attempt_number", 1)))
    con.executemany(
        "INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?)",
        [r + (1 if r[0] in retracted else 0,) for r in rows])
    con.commit()
    con.close()

def objective_history(index_path, objective):
    con = sqlite3.connect(index_path)
    cur = con.execute(
        "SELECT ts, score, mode FROM events WHERE objective=? AND retracted=0 "
        "ORDER BY ts", (objective,))
    return cur.fetchall()
```

### Anti-Patterns to Avoid

- **Content-hash-as-the-ID:** explicitly rejected by D-01, but worth restating why —
  PITFALLS.md Pitfall 1 documents this as the *accepted, author-acknowledged* trade-off
  of the closest prior-art system (a plain-text hash-keyed spaced-repetition format),
  which loses learning history on every edit. This project's own material makes the
  failure near-certain: "25 of 45 EMT wrong options are due for editing this milestone"
  `[VERIFIED: .planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md:57-58]`.
- **Full-file rewrite per response, applied to evidence:** the exact anti-pattern
  CONCERNS.md already documents for the *current* attempt/session writers — "the attempt
  file is rewritten in full on every answer (`quiz.py:172`)" `[VERIFIED: .planning/codebase/CONCERNS.md:130-133]`.
  An append-only log is chosen specifically to not repeat this at evidence-log scale.
- **Trusting `os.open(..., os.O_APPEND)` alone on Windows as sufficient:** see Pattern 2 —
  this is the literal Windows durability risk CONTEXT.md flagged, now backed by a primary
  source `[CITED: bugs.python.org/issue42606]`.
- **Stem-similarity guessing during migration:** explicitly forbidden by D-14. Positional
  (`number`-based) resolution has the same silent-wrong-match risk as stem similarity if
  a bank was reordered since the legacy record was written — see Migration Strategy below
  for the specific reasoning and the conservative default this research recommends.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-process file locking on Windows/POSIX | A custom pidfile / spin-wait scheme | `msvcrt.locking()` / `fcntl.flock()` | Both are stdlib, both are the OS-blessed primitive for this exact problem, both are already documented and tested at the platform level — reinventing this is exactly the kind of "no prior art" trap PITFALLS.md warns the auditor phase about, one layer earlier |
| Indexed queries over a growing append-only log | Hand-rolled JSON index with manual dict-of-lists bookkeeping | `sqlite3` (explicitly sanctioned by D-08 "as that cache") | A real query engine for filtering/sorting/joining by objective, mode, and time costs nothing extra (bundled with CPython) and avoids a second, subtly-different notion of "index" living only in this codebase |
| JSON Schema validation against Draft 2020-12 in full | A byte-for-byte reimplementation of `$ref`, `oneOf`, `allOf`, format validators, etc. | A **minimal subset validator** (see below) — only the keywords the five hand-authored schemas actually use | The full spec is enormous (dozens of keywords, recursive `$ref` resolution, format assertions); this project authors its own schemas, so it only needs to correctly enforce `type`, `required`, `properties`, `additionalProperties`, `enum`, and `items` — building the full spec would be building an unused general-purpose library inside a single-purpose tool |
| Content-hash computation | A bespoke normalization+hash routine | `hashlib.sha256` over a well-defined, documented normalization (e.g. stem + sorted option text + correct-answer letters, whitespace-collapsed) | `hashlib` is the vetted primitive; the only real design work is *what gets hashed*, which must be specified precisely so `lint`'s drift-detection (D-04) is deterministic across runs |

**Key insight:** Every "don't hand-roll" item above already has a stdlib-blessed answer
that costs zero new dependencies — this phase's entire risk surface is in getting the
*shape* right (event fields, idempotency key, index schema), not in needing a library
that doesn't exist. The one place a hand-rolled component is genuinely necessary (the
JSON Schema validator) is scoped deliberately narrow for exactly that reason.

## Runtime State Inventory

> Included because this phase is fundamentally a migration: three existing on-disk
> stores are being replaced by one, and every legacy record must resolve to a location
> in the new log or be explicitly marked unresolved (EVID-06, D-13, D-14).

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `_attempts/*.md` (attempt markdown, one per sitting), `_attempts/session_*.json` (session state, keyed by positional `item_id`, e.g. `"q7"`), `daily_log.md` (markdown table, one row per day, ticks per lane) — all local files, no external datastore | Migration tool reads all three, writes events into `evidence.jsonl`; positional `item_id` values in legacy files **do not** match the new opaque IDs and must be imported as unresolved unless explicitly re-attributed later (D-14) |
| Live service config | **None.** This project has no external services with configuration outside git — AnkiConnect (a *read* integration, not evidence storage) is untouched by this phase; itembank's own config file (`itembank.json`, per PROJECT.md) does not exist yet and is out of scope for Phase 1 | None |
| OS-registered state | **None.** No Windows Task Scheduler entries, no `pm2`/`launchd`/`systemd` units — this is a CLI tool invoked manually, no background service is registered by anything Phase 1 builds | None |
| Secrets/env vars | **None new.** The only env var in the existing codebase is `ANKI_CONNECT_URL` (`.planning/codebase/CONCERNS.md` §"Anki connection over localhost only"), unrelated to evidence storage and untouched by this phase | None |
| Build artifacts | **None yet at risk.** No installed package, no `egg-info`, no compiled binary exists for this project (stdlib-only, no install step, confirmed `.planning/PROJECT.md` Constraints). The new `_evidence/` directory and `schemas/` directory are new artifacts *created* by this phase, not stale ones left behind by it | Ensure `.gitignore` (or an equivalent guard, matching the existing `itembank guard` pattern at `surfaces/cli.py:58-81`) excludes `_evidence/evidence.jsonl` from being treated as a "real bank" false positive, and excludes learner evidence from the repo the same way `_attempts/` is presumably already excluded — verify at plan time whether `_attempts/` and `daily_log.md` are currently git-ignored, since evidence should follow the same residency rule (`.planning/PROJECT.md` Constraints: "Data residency: evidence and banks stay on disk... Learner evidence lives beside the private bank") |

**Nothing found in categories:** Live service config, OS-registered state, secrets/env
vars, and build artifacts are all explicitly "None" — verified by reading
`.planning/codebase/CONCERNS.md`, `.planning/codebase/ARCHITECTURE.md`, and
`.planning/PROJECT.md` in full this session, and by the absence of any service-registration
or packaging code anywhere in the four existing layers (`model.py`, `runtime.py`,
`server.py`, `surfaces/`).

## Common Pitfalls

### Pitfall 1: The idempotency key (D-17) is not directly implementable for `short` items

**What goes wrong:** D-17 defines the idempotency key as "session + item + attempt
number + canonical answer," built on `runtime.canonical_response()`. That function
explicitly returns `None` for constructed response —
`[VERIFIED: runtime.py:78-79]` `if t == "short": return None` — because free text has no
canonical form. A literal implementation of D-17 either crashes on `short` submissions or
silently treats every `short` submission as having the same key (`None`), which would
make every second `short` answer in the same attempt read as a duplicate regardless of
what was actually typed.

**Why it happens:** D-17 was written correctly for the four auto-scored types, where
`canonical_response()` already exists and is exactly the right normalizer to reuse. The
one type that was scoped out of scoring by design (`short` is "NOT auto-graded, ever" —
`[VERIFIED: model.py:96-99]` "Constructed response. Nothing here is machine-gradable by
design") is the same type that breaks the literal reading of the key.

**How to avoid:** Extend the key deterministically: when `canonical_response()` returns
`None`, fall back to a hash of the normalized answer text itself (e.g.
`"short:" + hashlib.sha256(normalized_text.encode()).hexdigest()`), so two identical
verbatim submissions to the same item in the same attempt still dedupe, and two different
answers do not collide. Document this explicitly in the event schema / idempotency spec
so the planner does not silently drop `short` items from PROTO-03 coverage.

**Warning signs:** A test that submits the same `short` answer twice does not report
`already_recorded`; or a test that submits two *different* `short` answers to the same
item in the same attempt incorrectly dedupes the second one.

### Pitfall 2: `lint()`'s return-shape change (PROTO-02) has three call sites that must move together

**What goes wrong:** `model.lint()` currently returns `(errors, warnings)` as lists of
plain strings, and three call sites concatenate them directly with `+`:
`surfaces/cli.py` `[VERIFIED: surfaces/cli.py:26-27]` (`for e in errors: print("error  " + e)`),
`surfaces/quiz.py` `cmd_build` `[VERIFIED: surfaces/quiz.py:38-40]` (`for e in errors: print("error  " + e)`),
and `surfaces/quiz.py` `cmd_serve` `[VERIFIED: surfaces/quiz.py:144-146]` (identical pattern).
If `lint()`'s error entries become structured objects (to carry the `code`/`field` PROTO-02
requires) without updating these three call sites in the same change, `"error  " + e` raises
`TypeError: can only concatenate str` the moment any bank fails to lint clean, breaking
`lint`, `build`, and `serve` simultaneously.

**Why it happens:** `lint()`'s Python-level return shape (as opposed to the bank markdown
format) is not covered by the "format changes must be additive" constraint, so it is easy
to treat as a free change — but it has real internal callers that were never designed
against a structured error type.

**How to avoid:** Define errors/warnings as a small class or `namedtuple` (`code`, `field`,
`item`, `message`) with a `__str__` that reproduces today's exact `"Qn: message"` text, and
update all three call sites to use `str(e)` (or an f-string) instead of bare `+`
concatenation in the same commit that changes `lint()`'s return type. This keeps CI's
existing string-matching assertions (`.github/workflows/ci.yml:25-30`, which `grep`s for
substrings like `"no WHY BEST"`) passing unchanged.

**Warning signs:** CI's "Broken fixture is caught" step (`.github/workflows/ci.yml:19-30`)
starts failing with a `TypeError` traceback instead of the expected lint output.

### Pitfall 3: Positional-match "resolution" during migration reintroduces the exact risk D-14 forbids

**What goes wrong:** It is tempting, during migration, to resolve a legacy `item_id` like
`"q7"` to a newly-assigned opaque ID by reloading the *current* bank and matching on
`number == 7`. This works only if the bank's item order has not changed since the legacy
record was written. If an item was inserted, removed, or reordered in the meantime, this
silently attaches history to the wrong item — the same failure mode D-14 explicitly rules
out for stem-similarity matching ("a wrong match attaches your history to the wrong
question and nothing ever tells you" `[VERIFIED: .planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md:125-126]`),
just via a different heuristic.

**Why it happens:** Positional matching feels safer than fuzzy stem matching because it's
deterministic — but deterministic-and-wrong is exactly as bad as fuzzy-and-wrong when
there is no signal telling you which case you're in.

**How to avoid:** Default to importing every legacy positional record as unresolved (per
D-14's letter, not just its spirit about stem matching). If the planner wants a
position-based recovery path, it must be an explicit, separately-invoked, clearly-logged
opt-in (e.g. `migrate --resolve-by-position`) that records *how* each item was resolved in
the migrated event's `source_ref`, never a default migration behavior.

**Warning signs:** Migration's "resolved" count is suspiciously close to 100% for old
banks that are known to have been edited since the legacy records were written.

### Pitfall 4: Response-time / confidence / error-category (EVID-07) have no existing capture point

**What goes wrong:** EVID-07 requires recording response time, confidence, and error
category "whether or not anything reads them yet." None of these exist anywhere in the
current codebase — `surfaces/session.py:cmd_submit()` `[VERIFIED: surfaces/session.py:46-67]`
takes only `a.answer` from the CLI; there is no timer, no confidence prompt, and no error
taxonomy anywhere in `model.py` or `runtime.py`. Treating this as "just add three fields to
the event schema" without adding the CLI/route plumbing to actually populate them means
the fields exist but are always `null`, which technically satisfies "recorded" but defeats
the requirement's stated purpose ("because an uncaptured field cannot be backfilled" —
`.planning/PROJECT.md` Active list).

**Why it happens:** It is easy to satisfy the schema-shape half of a "record this field"
requirement without doing the harder half — wiring a real capture point into the CLI
surface that calls it.

**How to avoid:** Scope Phase 1 honestly: `response_time_ms` needs a `start_ts` captured
at `next`/render time and a `submit_ts` at submit time (both derivable without new CLI
flags, since the session already tracks a cursor); `confidence` needs a new optional
`--confidence` argument on `submit` (defaulting to `null` if omitted, so nothing is forced
on the learner this phase); `error_category` has no deterministic source yet (it depends
on hint-ladder/tutoring work not built until Phase 6/8) and should be recorded as `null`
by design, not backfilled with a guess. Say this explicitly in the plan rather than
silently under-delivering EVID-07.

**Warning signs:** A UAT check for EVID-07 that only inspects the schema (field present)
rather than a live session that shows `response_time_ms` and `confidence` populated with
real values.

## Code Examples

Verified patterns for this codebase's actual conventions:

### Idempotency check extended for `short` (Pitfall 1's fix)
```python
# Source: this research, grounded in runtime.py:66-96 (canonical_response) and
# runtime.py:78-79 (short returns None) — both confirmed this session.
import hashlib

def idempotency_key(session_id, item_id, attempt_number, q, answer, canonical_response):
    canon = canonical_response(q, answer)
    if canon is None:                      # short / constructed response
        norm = " ".join(str(answer or "").split()).strip().lower()
        canon = "short:" + hashlib.sha256(norm.encode("utf-8")).hexdigest()
    raw = "%s|%s|%d|%s" % (session_id, item_id, attempt_number, canon)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

### `LintError` as a drop-in-compatible upgrade (Pitfall 2's fix)
```python
# Source: this research, grounded in model.py:207-303's existing "%s: %s" % (tag, msg)
# string shape and the three call sites at cli.py:26-27, quiz.py:38-40, quiz.py:144-146
import collections

class LintError(collections.namedtuple("LintError", "code field item message")):
    __slots__ = ()
    def __str__(self):
        return "%s: %s" % (self.item, self.message)   # matches today's "Qn: message"

# Existing call sites must change from:
#     print("error  " + e)
# to:
#     print("error  " + str(e))     # or an f-string
# in cli.py:cmd_lint, quiz.py:cmd_build, quiz.py:cmd_serve — all three, together.
```

### Migration dry-run count reconciliation shape (EVID-06)
```python
# Source: this research, matching the existing "%d items, %d errors, %d warnings"
# reporting style at surfaces/cli.py:29
def migrate(legacy_paths, log_path, dry_run=True):
    found = {"attempt_md": 0, "session_json": 0, "daily_log": 0}
    would_write = {"resolved": 0, "unresolved": 0}
    # ... scan legacy_paths, tally `found`, compute deterministic source_key per
    # record, check against existing dedupe keys in log_path to skip re-imports ...
    print("found:  %(attempt_md)d attempt-file answers, %(session_json)d session "
          "responses, %(daily_log)d day-log ticks" % found)
    if dry_run:
        print("would write: %(resolved)d resolved, %(unresolved)d unresolved"
              % would_write)
    else:
        print("wrote:       %(resolved)d resolved, %(unresolved)d unresolved"
              % would_write)
    total_found = sum(found.values())
    total_written = sum(would_write.values())
    assert total_found == total_written, "count mismatch — see EVID-06"
```

## State of the Art

| Old Approach | Current Approach (this phase) | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Positional item ID (`"id": "q" + number`) `[VERIFIED: model.py:40]` | Opaque UUID + separate content-hash field (D-01/D-02) | This phase | Item identity survives reordering and stem edits; the exact gap PITFALLS.md Pitfall 1 identifies as this milestone's highest-risk foundational bug |
| Full-file rewrite per response (attempt `.md` rewritten in full on every answer, `[VERIFIED: .planning/codebase/CONCERNS.md:130-133]`) | Single-line append per event | This phase | O(1) write cost per response instead of O(n) in current answered-item count; matches the one place the existing codebase already does atomic writes correctly (`runtime.py:143-150`, `write_session`'s tmp+`os.replace()` pattern) |
| Three independent stores, no cross-store query | One log, disposable index, one query surface (EVID-04) | This phase | "How am I doing on objective X over time" becomes answerable without a join across three differently-shaped files |
| `SESSION_VERSION = 1` with no migration logic `[VERIFIED: runtime.py:20, runtime.py:138-139]` | Explicit `schema_version` per contract (item/session/response/report), published in `schemas/` | This phase | Directly closes the gap `.planning/codebase/CONCERNS.md` §"JSON session file format has no version evolution strategy" already flagged as fragile |

**Deprecated/outdated:**
- Positional `Qn` as an evidence key: superseded by opaque IDs; old positional references
  become explicitly-unresolved migration records, never silently reinterpreted.
- Hand-edited `MARK:` lines in attempt markdown for `short` grading: superseded by the
  `mark` command/route appending a first-class timestamped event (D-12); the rendered
  attempt file becomes read-only output, not an editable input (D-11).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `evidence.py` should be a new peer module to `runtime.py` rather than added inside `runtime.py` itself | Architectural Responsibility Map, Recommended Project Structure | Low — this is an internal organization choice with no format-contract consequence; if the planner prefers extending `runtime.py` directly (which CONTEXT.md's own Integration Points section lists as the target: "runtime.py — the evidence writer, the idempotency check..."), that is equally valid and does not conflict with any locked decision |
| A2 | `sqlite3` (not a hand-rolled JSON index) is the right backend for the disposable derived index | Standard Stack, Don't Hand-Roll, Code Examples | Medium — if sqlite3 turns out to have platform/locking quirks of its own on the target Windows machine, a pure-JSON index is the documented fallback; either satisfies D-08's letter ("A sqlite3 file is acceptable... never as the system of record") |
| A3 | The advisory-lock (`msvcrt.locking`/`fcntl.flock`) approach is sufficient without also implementing the `ctypes` + `CreateFileW(FILE_APPEND_DATA)` true-atomicity path | Architecture Patterns Pattern 2 | Medium-High — this is exactly what the recommended spike (see Open Questions) must confirm empirically before the plan locks it in; if the spike shows corruption even under the lock (e.g., due to antivirus/backup software interfering with the lock file), the `ctypes` path becomes necessary |
| A4 | The `schema` CLI command (mirroring `spec`) is the right delivery mechanism for PROTO-05's "no-repo-context agent can read the contract" | Architecture Patterns, Deferred Ideas cross-reference | Low-Medium — CONTEXT.md explicitly deferred this decision ("How a no-repo-context agent physically receives the schemas/ files... was not decided"); a route (once Phase 2's daemon exists) is an equally valid alternative, and Phase 1 has no daemon dependency, so a CLI command is the only mechanism available *this phase* regardless |
| A5 | `response_time_ms` can be derived from existing session cursor timestamps (`next` call time to `submit` call time) without a new CLI flag, while `confidence` needs a new optional `--confidence` flag | Common Pitfalls #4 | Medium — this assumes agent/CLI callers reliably call `next` immediately before `submit` for the same item, which is true of the current session flow but not verified against every future caller (e.g., a resumed session where `next` was called hours before `submit`) |
| A6 | The content-hash normalization (what exactly gets hashed for drift detection) should be stem + sorted option text + correct-answer letters, whitespace-collapsed | Don't Hand-Roll | Medium — this is a reasonable default but was not specified in CONTEXT.md's discretion notes ("Event field naming... unconstrained") and directly determines how sensitive drift detection is (e.g., should a `WHY BEST` or `TRAP` edit also count as "content changed"?) — the planner should decide the exact field set deliberately, not inherit this research's default silently |

**If this table is empty:** Not applicable — six assumptions are logged above, none load-bearing
enough to block planning, but A3 in particular should be resolved by the spike before
implementation, not assumed away.

## Open Questions

1. **Does the Windows append-write spike confirm the lock-based mitigation is sufficient?**
   - What we know: Python's `O_APPEND` on Windows is documented as non-atomic at the CRT
     level (`[CITED: bugs.python.org/issue42606]`); an advisory lock around a single
     `write()` call is the standard stdlib-only mitigation pattern, and single-sector
     writes are independently reported as atomic on NTFS (`[CITED: nblumhardt.com]`,
     `[CITED: antonymale.co.uk]`).
   - What's unclear: whether this exact combination behaves correctly on *this* Windows
     11 machine, under *this* project's actual write pattern (short JSON lines,
     concurrent CLI invocations), including the crash-mid-write case.
   - Recommendation: **a spike task belongs in the plan, first, blocking every other
     evidence-writing task.** It should measure, concretely: (a) reproduce the
     unlocked-`O_APPEND` corruption with N concurrent writers on this machine — confirms
     the risk is real, not just documented; (b) run the same test with the lock-wrapped
     `append_event()` helper and confirm zero corruption across a realistic volume (e.g.
     10,000 appended lines); (c) simulate a kill mid-write and confirm the reader's
     defensive line-by-line parsing (D-09) degrades gracefully — only the torn trailing
     line is lost/flagged, nothing else. Do not skip this and assume the pattern works.

2. **Exact content-hash normalization for drift detection (D-04).**
   - What we know: the hash must be stable across insignificant whitespace changes
     (`model.py`'s own `grab()` already `.strip()`s every field) but must change when the
     item's *meaning* changes.
   - What's unclear: whether fields like `TRAP`, `WHY BEST`, or per-option `DISTRACTOR
     ANALYSIS` text should count toward the hash, or only the stem/options/correct-answer.
     Including too much makes routine rationale-writing (this milestone's own stated
     backlog: "25 of 45 EMT wrong options are due for editing") fire the drift warning
     constantly; including too little risks missing a genuine meaning-changing edit.
   - Recommendation: hash stem + option text + correct-answer letters only (matches this
     research's A6 assumption); treat rationale-field edits as never drift-worthy, since
     D-04 already accepts the risk of a "genuine rewrite silently inherit[ing] old trend
     data" as a stated trade-off — the hash's job is change detection on the *tested
     content*, not on every field in the block.

3. **JSON Schema validator scope — exact keyword set.**
   - What we know: D-15 requires either a minimal validator or an explicitly-shallow CI
     check; this research recommends the minimal validator, scoped to the keywords the
     five hand-authored schemas actually use.
   - What's unclear: the exact keyword list needed depends on how expressive the planner
     wants `schemas/*.json` to be (e.g. does `response.schema.json` need `enum` on
     `review_state`? Does `item.schema.json` need `oneOf` to express the five item-type
     variants?).
   - Recommendation: write the five schema files first, inventory the keywords actually
     used across all five, then implement exactly that subset in the validator — building
     the validator before the schemas risks either over-building unused keywords or
     under-building ones the schemas end up needing.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python interpreter | Everything | ✓ | 3.11+ required by PROJECT.md; CI pins 3.11 (`.github/workflows/ci.yml:12`) `[VERIFIED: .github/workflows/ci.yml:10-12]` | — |
| `sqlite3` module | Derived query index (Pattern 3) | ✓ | Bundled with CPython since 2.5 | Pure-JSON index (see Alternatives Considered) |
| `msvcrt` module | Locked append on Windows (Pattern 2) | ✓ (Windows-only) | Bundled with CPython on Windows | `ctypes` + `CreateFileW` (higher implementation cost) |
| `fcntl` module | Locked append on POSIX (Pattern 2) | ✓ (POSIX-only, i.e. CI's `ubuntu-latest` runner) | Bundled with CPython on POSIX | None needed — this is the well-tested path already |
| Git | Optional, for evidence residency/gitignore verification | ✓ (repo is git-tracked, confirmed by `gitStatus` in session context) | — | — |

**Missing dependencies with no fallback:** none — every dependency this phase needs is
already present in a standard CPython 3.11+ install on both the CI runner (Linux) and the
target machine (Windows 11).

**Missing dependencies with fallback:** none currently missing; the `ctypes`-based
Windows-atomic-append path is documented as a fallback *if* the spike (Open Question 1)
shows the primary lock-based approach insufficient — not needed today.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None — standalone Python scripts run directly, `[VERIFIED: .github/workflows/ci.yml:38-43]` `for t in tests/*.py; do python "$t" || exit 1; done` |
| Config file | none — no pytest.ini/config; convention is `tests/*_roundtrip.py`, each with a `fail(msg)` helper that prints `"FAIL: " + msg` and exits 1, confirmed at `tests/scoring_roundtrip.py:21-23` |
| Quick run command | `python tests/evidence_roundtrip.py` (new file, this phase) |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` (matches CI exactly, `.github/workflows/ci.yml:40-43`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EVID-01/EVID-02 | Editing an item's stem post-lint still resolves to the same evidence history | unit | `python tests/evidence_roundtrip.py` (new `test_identity_survives_edit`) | ❌ Wave 0 |
| EVID-03 | Three legacy views render correctly as reads over the one log | unit | `python tests/evidence_roundtrip.py` (new `test_renders_match_log`) | ❌ Wave 0 |
| EVID-04 | Cross-subject/cross-session objective query returns correct history | unit | `python tests/evidence_roundtrip.py` (new `test_objective_query`) | ❌ Wave 0 |
| EVID-05 | Retraction leaves original event intact, post-retraction counts correct | unit | `python tests/evidence_roundtrip.py` (new `test_retraction`) | ❌ Wave 0 |
| EVID-06 | Migration pre/post counts reconcile exactly, dry-run matches real run | integration | `python tests/evidence_roundtrip.py` (new `test_migration_reconciliation`, against new legacy fixtures) | ❌ Wave 0 |
| EVID-07 | Response event carries all six required fields (three populated live, three reserved-null per Pitfall 4) | unit | `python tests/protocol_roundtrip.py` (new `test_event_schema_fields`) | ❌ Wave 0 |
| EVID-08 | Two identical-answer events with different `mode` values are distinguishable | unit | `python tests/evidence_roundtrip.py` (new `test_mode_recorded`) | ❌ Wave 0 |
| PROTO-01 | Every schema file and every runtime payload carries a `schema_version`/`version` field | unit | `python tests/protocol_roundtrip.py` (new `test_schema_versions_present`) | ❌ Wave 0 |
| PROTO-02 | `lint()` errors carry `code`/`field`/`message`; existing CI string-match assertions still pass | unit + existing CI step | `python tests/protocol_roundtrip.py` + `.github/workflows/ci.yml`'s existing "Broken fixture is caught" step (`ci.yml:19-30`) unchanged | ❌ Wave 0 for the new test; existing CI step already covers the human-text half |
| PROTO-03 | Duplicate submit (including `short`) returns `already_recorded`, not a second event | unit | `python tests/evidence_roundtrip.py` (new `test_duplicate_submit_dedupes`, covering the Pitfall 1 fix explicitly) | ❌ Wave 0 |
| PROTO-04 | CI validates live runtime output against `schemas/*.json` | CI step | new step in `.github/workflows/ci.yml` running the minimal validator | ❌ Wave 0 — new CI step |
| PROTO-05 | `itembank schema` output is self-contained and machine-parseable with no other repo context | smoke | `python tests/protocol_roundtrip.py` (new `test_schema_command_output`) | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python tests/evidence_roundtrip.py && python tests/protocol_roundtrip.py`
  (fast — both are pure-Python, no I/O beyond temp files, matching the existing
  `scoring_roundtrip.py`'s sub-second runtime)
- **Per wave merge:** full suite — `for t in tests/*.py; do python "$t" || exit 1; done`
  (identical to CI, so a green local run predicts a green CI run)
- **Phase gate:** full suite green, plus the Windows durability spike's own pass/fail
  result (Open Question 1) documented in the plan before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/evidence_roundtrip.py` — covers EVID-01 through EVID-06, EVID-08, PROTO-03
- [ ] `tests/protocol_roundtrip.py` — covers EVID-07 (schema shape), PROTO-01, PROTO-02,
      PROTO-05
- [ ] New CI step in `.github/workflows/ci.yml` — covers PROTO-04
- [ ] New fixtures: `fixtures/legacy_attempts/*.md`, `fixtures/legacy_session.json`,
      `fixtures/legacy_daily_log.md` — synthetic legacy-shaped data for the migration
      reconciliation test (EVID-06), since no such fixtures exist today (`fixtures/`
      currently holds only `sample_bank.md`, `broken_bank.md`, `sample_plan.md`,
      `sample_lanes.md`, and two generated HTML outputs)
      `[VERIFIED: Glob of fixtures/ this session]`
- [ ] Windows durability spike — not a unit test in the conventional sense; a small,
      dedicated, documented experiment (script or manual protocol) whose *result* the
      plan records before evidence-writing tasks proceed (see Open Question 1)
- [ ] Framework install: none — the existing `python tests/*.py` convention needs no new
      tooling, only new files following it

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Single local user, no accounts — `.planning/PROJECT.md` Constraints: "Users: One. No accounts, no auth, no multi-tenancy" |
| V3 Session Management | No (in the ASVS web-session sense) | The "session" concept here is an evidence-tracking JSON file, not an authenticated web session; no cookie/token surface exists in this phase |
| V4 Access Control | No | No multi-tenancy, no roles, no permission boundary within the tool |
| V5 Input Validation | **Yes** | Every input to the evidence writer and migration tool is local-file-derived but must still be validated defensively: malformed JSONL lines are skipped-and-reported per D-09 (never trusted as parsed without a `try/except json.JSONDecodeError`); migration inputs (`_attempts/*.md`, session JSON, `daily_log.md`) may be hand-edited or partially corrupted (`.planning/codebase/CONCERNS.md` already documents "No test of malformed session JSON" as a gap) — the migration tool must not assume well-formed legacy data |
| V6 Cryptography | **Yes, narrowly** | `hashlib.sha256` for the content-hash fingerprint is an *integrity* check (change detection), not a security boundary against an adversary — this distinction should be stated in code comments the same way `check`'s "no sandboxing" posture is stated plainly in `spec` output (PITFALLS.md Pitfall 5's pattern, applied here) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed/truncated evidence log line (accidental corruption, not adversarial) causing a crash on read | Denial of Service (self-inflicted, not attacker-driven, since this is a single-local-user tool) | D-09's "skip and report a malformed line rather than crashing" — already locked; implement as `try/except (ValueError, KeyError)` per line in every reader, matching the existing "fail fast and loudly" philosophy but scoped per-line instead of per-file (`.planning/codebase/ARCHITECTURE.md` §Error Handling) |
| Torn write during a crash mid-append leaving a half-written JSON line | Tampering (accidental, from the process's own crash — not an external attacker) | The reader-side defensive parsing above; this is the same finding as the Windows durability spike — the writer-side lock reduces the *frequency* of this, the reader-side handling is what makes it *safe* regardless of frequency |
| Migration tool given a path outside the expected `_attempts/`/bank-adjacent scope | Tampering / information disclosure (a malformed or malicious `--legacy-dir` argument reading files outside the intended tree) | Scope migration inputs to well-known relative locations (`_attempts/` beside the bank, `daily_log.md` beside the plan) by default, matching how `resolve_notes()` is flagged in CONCERNS.md as needing a documented-trust boundary (`.planning/codebase/CONCERNS.md` §"File paths from wiring config allow traversal") — the same discipline applies here rather than accepting an arbitrary path argument uncritically |
| Evidence data (which may include AAOS-derived EMT item text per the accepted-risk note in PROJECT.md) written to a git-tracked location by mistake | Information Disclosure (this project's own accepted-risk framing: "hosted models see item text," data residency otherwise strict) | Confirm at plan time that `_evidence/` (or wherever the log lands) is excluded the same way existing learner-evidence locations are (`.planning/PROJECT.md` Constraints: "Learner evidence lives beside the private bank") — this is the same check flagged in the Runtime State Inventory's "Build artifacts" row above |

## Sources

### Primary (HIGH confidence)
- `model.py`, `runtime.py`, `server.py`, `surfaces/cli.py`, `surfaces/session.py`,
  `surfaces/quiz.py`, `surfaces/day.py` (lines 420-509), `itembank.py`,
  `.github/workflows/ci.yml`, `tests/scoring_roundtrip.py`, `.planning/config.json` —
  all read directly this session, cited inline with line numbers throughout
- `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`,
  `.planning/STATE.md`, `.planning/codebase/CONCERNS.md`,
  `.planning/codebase/ARCHITECTURE.md`, `.planning/research/PITFALLS.md`,
  `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md`,
  `.planning/phases/01-evidence-spine-protocol-foundation/01-DISCUSSION-LOG.md` — all
  read directly this session

### Secondary (MEDIUM confidence)
- [Issue 42606: Support POSIX atomicity guarantee of O_APPEND on Windows — Python bug tracker](https://bugs.python.org/issue42606) — official, primary source confirming the CRT `lseek`+`write` non-atomicity on Windows
- [msvcrt — Python 3 documentation](https://docs.python.org/3/library/msvcrt.html) — confirmed `locking()` signature and modes this session via WebFetch
- [fcntl — Python 3 documentation](https://docs.python.org/3/library/fcntl.html) — confirmed `flock()` signature and POSIX-only availability this session via WebFetch
- [Atomic shared log file writes with FILE_APPEND_DATA — nblumhardt.com](https://nblumhardt.com/2016/08/atomic-shared-log-file-writes/) — corroborates sector-size atomic-write behavior on Windows (cross-checked against a second independent source below)
- [Atomic File Writes on Windows — antonymale.co.uk](https://antonymale.co.uk/windows-atomic-file-writes.html) — independent corroboration of the same sector-size atomicity claim and the `FILE_APPEND_DATA` mechanism

### Tertiary (LOW confidence)
- General WebSearch summaries on event sourcing / append-only-log-plus-projection
  patterns and JSON Schema validator library landscape — used only to confirm this is a
  well-established architectural pattern (matches D-07/D-08's own reasoning and the
  pwn.college/CTFd prior art already named in CONTEXT.md), not as a source of any
  specific numeric or API claim

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every recommended module is stdlib, confirmed present in every
  CPython 3.11+ distribution; no registry lookups needed
- Architecture (event log + disposable projection): HIGH — well-established pattern,
  directly matches the already-locked D-07/D-08 decisions and this codebase's own
  `write_session()` atomic-write precedent
- Windows append-write durability: MEDIUM — grounded in an official Python bug tracker
  issue plus two independently-corroborating technical sources, but not yet empirically
  measured on the target machine; the recommended spike closes this gap
- Pitfalls (idempotency-key gap for `short`, lint-return-shape call sites, positional-match
  risk, EVID-07 capture-point gap): HIGH — all four are derived directly from reading this
  session's actual source files, not inferred

**Research date:** 2026-08-06
**Valid until:** 30 days for the architectural recommendations (stable pattern, unlikely
to shift); the Windows durability finding should be re-confirmed if the target Windows
build or Python version changes, since it depends on the specific CRT/OS combination
