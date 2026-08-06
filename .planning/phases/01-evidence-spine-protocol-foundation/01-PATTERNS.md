# Phase 1: Evidence Spine & Protocol Foundation - Pattern Map

**Mapped:** 2026-08-06
**Files analyzed:** 13 (new) + 5 (modified)
**Analogs found:** 13 / 13

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `evidence.py` (new) | service | event-driven / file-I/O | `runtime.py` (`read_session`/`write_session`, `canonical_response`) | role-match (closest thing to "the one writer" precedent) |
| `schemas/item.schema.json` (new) | config | request-response (contract doc) | `model.py` `SPEC` (string constant) | role-match |
| `schemas/session.schema.json` (new) | config | request-response | `model.py` `SPEC` | role-match |
| `schemas/response.schema.json` (new) | config | request-response | `model.py` `SPEC` | role-match |
| `schemas/report.schema.json` (new) | config | request-response | `model.py` `SPEC` | role-match |
| `schemas/lint_error.schema.json` (new) | config | request-response | `model.py` `SPEC` | role-match |
| `schema_validator.py` or similar (new, minimal JSON Schema validator) | utility | transform | none in codebase | no analog |
| `surfaces/migrate.py` (new) | service | batch / file-I/O | `surfaces/day.py` (`load_day_log`) + `surfaces/session.py` (`cmd_start`) | role-match |
| `surfaces/evidence_cli.py` (new — `mark`, `schema` commands) | route/controller | request-response | `surfaces/session.py` (`cmd_submit`) | exact |
| `surfaces/cli.py` (modified — route new commands, update `lint()` error printing) | route | request-response | itself (extend existing pattern) | exact |
| `surfaces/session.py` (modified — call `evidence.append_event()`) | controller | event-driven | itself | exact |
| `surfaces/quiz.py` (modified — `cmd_serve` calls evidence writer; attempt.md becomes a render) | controller | event-driven / file-I/O | itself, `runtime.write_session` pattern | exact |
| `surfaces/day.py` (modified — `write_day_log` becomes `evidence.render_daily_log()`) | controller | file-I/O | itself, `load_day_log`/`write_day_log` | exact |
| `model.py` (modified — `item_id`/`content_hash` fields, coded `lint()` errors) | model | transform | itself (`parse_question`, `lint`) | exact |
| `tests/evidence_roundtrip.py` (new) | test | batch | `tests/scoring_roundtrip.py` | exact |
| `tests/protocol_roundtrip.py` (new) | test | batch | `tests/scoring_roundtrip.py` | exact |
| `fixtures/legacy_attempts/*.md`, `fixtures/legacy_session.json`, `fixtures/legacy_daily_log.md` (new) | fixture | file-I/O | `fixtures/sample_bank.md`, `fixtures/broken_bank.md` | role-match |
| `.github/workflows/ci.yml` (modified — schema-validation step) | config | batch (CI) | itself (existing steps) | exact |

## Pattern Assignments

### `evidence.py` (new service, event-driven/file-I/O)

**Analog:** `runtime.py`

**Atomic write pattern to copy** (`runtime.py:143-150`, `write_session`):
```python
def write_session(path, data):
    target = session_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)
```
This is the *only* atomic-write precedent in the codebase (per CONCERNS.md). `evidence.py`'s
index-rebuild write (the disposable sqlite3/JSON index) should reuse this tmp+`os.replace()`
shape verbatim. The append-only event log itself is a different pattern (see Pattern 2 in
RESEARCH.md — locked single `write()` per line via `msvcrt.locking`/`fcntl.flock`), since
`write_session`'s whole-file replace is wrong for an append-only log (it would require holding
and rewriting the entire file per event, the exact anti-pattern CONCERNS.md flags for the
current attempt-file writer).

**Canonical-form reuse (idempotency key), copy directly, do not reimplement** (`runtime.py:66-96`,
`canonical_response`, and `runtime.py:99-113`, `canonical_key`):
```python
def canonical_response(q, answer):
    answer = normalize_answer(answer)
    t = q["type"]
    if t == "short":
        return None
    if t == "mc":
        ...
```
`evidence.py`'s idempotency key function must import `canonical_response` from `runtime.py`
(`from runtime import canonical_response`) and only add the `short`-item fallback documented
in RESEARCH.md ("Idempotency check extended for `short`", lines 632-645) — hashing the
normalized answer text when `canonical_response()` returns `None`. Do not duplicate the
per-type branching that already lives in `runtime.py`.

**Read-with-defensive-parsing pattern** — no direct analog exists (nothing in this codebase
reads a multi-line append-only file today); `runtime.read_session()` (`runtime.py:133-140`)
is the closest shape for "read + validate schema version, exit loudly on failure at the
whole-file level":
```python
def read_session(path):
    try:
        data = json.load(open(session_path(path), encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.exit("cannot read session %s: %s" % (path, exc))
    if data.get("schema_version") != SESSION_VERSION:
        sys.exit("unsupported session schema in %s" % path)
    return data
```
**What differs:** the evidence log reader must NOT `sys.exit` on a single bad line (D-09:
"skip and report a malformed line rather than crashing") — only `read_session`'s
whole-file-failure posture is the template; per-line handling needs its own
`try/except (ValueError, KeyError)` inside a `for lineno, raw in enumerate(fh, 1):` loop,
printing `"warn  evidence.jsonl:%d malformed, skipped" % lineno` (see RESEARCH.md's
`rebuild_index` example, lines 420-452) rather than exiting.

---

### `schemas/*.schema.json` (new config files)

**Analog:** `model.py` `SPEC` (`model.py:122-196`)

**Pattern to copy — the "self-contained contract string, no repo access needed" precedent:**
```python
SPEC = r"""itembank format contract
=========================

A bank is a markdown file. Everything that is not a question block is ignored...
```
`SPEC` is a plain triple-quoted string constant printed verbatim by `cmd_spec()`
(`surfaces/cli.py:17-19`). The `schemas/*.json` files play the same "no-repo-context agent
reads this and needs nothing else" role (PROTO-05), but as structured JSON rather than prose.
**What differs:** these are separate files on disk, not Python string constants, and are
delivered via a new `itembank schema` command (see `surfaces/evidence_cli.py` below) that
mirrors `cmd_spec`'s `print(SPEC)` shape but reads and prints file contents instead.

---

### `surfaces/migrate.py` (new — migration tool)

**Analog 1:** `surfaces/day.py` `load_day_log()` (`surfaces/day.py:434-457`) — the closest
existing "read a markdown table store, tolerate a header that may not match every row"
reader:
```python
def load_day_log(path):
    log, header = {}, list(DAY_LANES)
    if not os.path.exists(path):
        return log
    for raw in open(path, encoding="utf-8"):
        if not raw.lstrip().startswith("|"):
            continue
        cells = split_row(raw)
        if is_rule_row(cells):
            continue
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", cells[0]):
            named = [c for c in cells[1:] if c in DAY_LANES]
            if named:
                header = named
            continue
        log[cells[0]] = set(lane for lane, c in zip(header, cells[1:])
                            if c in DONE_MARKS)
    return log
```
The migration tool's `daily_log.md` reader should follow this exact "tolerate legacy shape,
map by header row, never assume alignment" structure — CONCERNS.md already flags this exact
reader as fragile, so the migration's copy must not blindly assume column order either.

**Analog 2:** `surfaces/session.py` `cmd_start()` (`surfaces/session.py:14-36`) — the session
JSON shape the migration must read (`items`, `cursor`, `responses`, `mode`, `objective`,
`seed`) and the `uuid.uuid4().hex` id-generation precedent for deterministic-yet-unique
identifiers.

**Reporting shape to copy** (`surfaces/cli.py:29`, matches RESEARCH.md's dry-run example):
```python
print("\n%d items, %d errors, %d warnings" % (len(qs), len(errors), len(warnings)))
```
Use the same `"%d ..., %d ..., %d ..."` printf-style summary line for migration's
found/resolved/unresolved counts (see RESEARCH.md's `migrate()` example, lines 669-685) —
this is the established status-line convention across the whole CLI.

---

### `surfaces/evidence_cli.py` (new — `mark` batch command, `schema` command)

**Analog:** `surfaces/session.py` `cmd_submit()` (`surfaces/session.py:46-67`)

```python
def cmd_submit(a):
    data = read_session(a.session)
    if data["status"] != "active":
        sys.exit("session is already complete")
    qs = load(data["bank"])
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
        write_session(a.session, data)
        sys.exit("session is already complete")
    q = qs[data["items"][data["cursor"]]]
    answer = normalize_answer(a.answer)
    score = score_response(q, answer)
    data["responses"].append({"item_id": q["id"], "objective": q.get("objective", ""),
                               "type": q["type"], "answer": answer, "score": score})
    data["cursor"] += 1
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
    write_session(a.session, data)
    result = {"accepted": True, "item_id": q["id"], "score": score,
              "status": data["status"], "next": session_view(data, qs)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
```
`cmd_mark` should follow the same shape: read state, validate, call the one writer
(`evidence.append_event()` for a mark event instead of `write_session`), print a JSON result
dict with `ensure_ascii=False, indent=2`. **What differs:** D-12 requires the command to
accept a *batch* — so `cmd_mark`'s argparse surface takes a list (e.g. `--marks` as a JSON
array of `{item_id, session_id, verdict, notes}` or a `--file` of NDJSON) and loops, calling
the writer once per mark, accumulating results into a JSON array rather than a single dict —
there is no existing batch-command analog in this codebase, so this loop-and-collect shape is
new but should still emit one final `json.dumps(...)` the way every other JSON surface does.

**`cmd_schema` analog:** `cmd_spec` (`surfaces/cli.py:17-19`):
```python
def cmd_spec(a):
    print(SPEC)
    return 0
```
Read and print the requested `schemas/*.json` file(s) verbatim; same "no processing, just
hand over the contract" shape.

---

### `surfaces/cli.py` (modified)

**Analog:** itself — extend `main()`'s `sub.add_parser(...)` block (`surfaces/cli.py:84-180`)
following the exact existing per-command block shape:
```python
s = sub.add_parser("submit", help="score and record the current session response")
s.add_argument("session")
s.add_argument("--answer", required=True,
              help="response value, or a JSON array/object for structured items")
s.set_defaults(fn=cmd_submit)
```
Add `mark`, `schema`, and `migrate` subparsers in this same style, importing `cmd_mark`,
`cmd_schema` from `surfaces/evidence_cli.py` and `cmd_migrate` from `surfaces/migrate.py`
at the top of the file alongside the existing surface imports (`surfaces/cli.py:10-14`).

**Mandatory paired edit — `lint()` error printing** (`surfaces/cli.py:22-30`, Pitfall 2 in
RESEARCH.md):
```python
def cmd_lint(a):
    qs = load(a.bank)
    errors, warnings = lint(qs)
    for e in errors:
        print("error  " + e)
    for w in warnings:
        print("warn   " + w)
```
When `lint()`'s return shape changes to carry `code`/`field` (PROTO-02), this becomes
`print("error  " + str(e))` — and the two other call sites below must change in the same
commit or `TypeError: can only concatenate str` breaks `lint`, `build`, and `serve`
simultaneously.

---

### `model.py` (modified — item identity fields + coded lint errors)

**Analog:** itself — extend the existing `grab()`-based field parsing at `model.py:39-51`:
```python
common = {
    "id": "q" + number if number else "",
    "number": int(number) if number else 0,
    "type": qtype,
    "stem": stem,
    "difficulty": grab(r"\(difficulty:\s*([^)]+)\)", ch),
    "objective": grab(r"\[OBJECTIVE:\s*(.*?)\]", ch),
    ...
}
```
Add two new additive fields the same way (per RESEARCH.md Pattern 1):
```python
"item_id": grab(r"(?m)^\[ID:\s*(\S+)\s*\]", ch),          # empty until assigned
"content_hash": grab(r"(?m)^\[HASH:\s*(\S+)\s*\]", ch),   # empty until assigned
```

**`LintError` upgrade — the exact `namedtuple` design from RESEARCH.md**, grounded in
`model.py:207-303`'s current `errors.append("%s: %s" % (tag, msg))` string-building shape:
```python
class LintError(collections.namedtuple("LintError", "code field item message")):
    __slots__ = ()
    def __str__(self):
        return "%s: %s" % (self.item, self.message)   # matches today's "Qn: message"
```
Every `errors.append("%s: ..." % (tag, ...))` call site inside `lint()` (e.g. `model.py:219-220`,
`model.py:225-226`, `model.py:229`) becomes `errors.append(LintError("item.duplicate_id", "id",
tag, "duplicate question number %s (also %s)" % (q["id"], seen_ids[q["id"]])))` — dotted code
per D-16, same human text preserved via `__str__` so CI's substring `grep` assertions
(`.github/workflows/ci.yml:25-30`) keep passing unchanged.

---

### `surfaces/session.py` / `surfaces/quiz.py` / `surfaces/day.py` (modified — call evidence writer)

**Analog:** the existing `write_session()` call sites — e.g. `surfaces/session.py:63`
(`write_session(a.session, data)` inside `cmd_submit`). Each surface that currently persists
directly must add a call to `evidence.append_event(...)` alongside (or, per D-11, in place of)
its existing write, following the same "one function call, no branching on caller" shape
`write_session` already establishes. `surfaces/quiz.py`'s attempt-file writer (flagged in
CONCERNS.md as "rewritten in full on every answer", `quiz.py:172`) becomes a render read
from the log — see `surfaces/day.py`'s `write_day_log()` (`surfaces/day.py:468-482`) as the
template for "regenerate the whole markdown view from an in-memory structure and write once",
which is the correct shape for a *render* (whole-file rewrite from source-of-truth), as
opposed to the *log append* (single-line, O(1)) which is a new pattern.

---

### `tests/evidence_roundtrip.py`, `tests/protocol_roundtrip.py` (new)

**Analog:** `tests/scoring_roundtrip.py` (full file structure) — the exact skeleton to copy:
```python
#!/usr/bin/env python3
"""One-line purpose statement, matching the file's own docstring convention."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    ...
    print("scoring contract: ok (%d items, one scorer)" % len(qs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
Both new test files must follow this exact shape: `ROOT`-relative `sys.path.insert`, import
via the public `itembank` module (not deep-importing `evidence` directly, matching the
existing "one public surface" discipline — check `itembank.py`'s `__all__` needs the new
evidence/schema functions added), a `fail(msg)` helper identical in text/exit-code, one
`main()` returning an int, and a final summary `print` in the same
`"<subject> contract: ok (...)"` style. `tests/evidence_roundtrip.py` also needs a
"structurally verify only one writer" check mirroring `scoring_roundtrip.py`'s own closing
block (`tests/scoring_roundtrip.py:96-109`, the `os.walk` + regex scan asserting exactly one
`score_response`-named function exists) — the evidence-writer analog would assert exactly one
`append_event`-named function exists across the codebase.

---

### `fixtures/legacy_attempts/*.md`, `fixtures/legacy_session.json`, `fixtures/legacy_daily_log.md` (new)

**Analog:** `fixtures/sample_bank.md` / `fixtures/broken_bank.md` (synthetic, no real content,
referenced by path constant at the top of a test file, exactly as `BANK = os.path.join(ROOT,
"fixtures", "sample_bank.md")` does in `scoring_roundtrip.py:18`). These new fixtures must
be equally synthetic (per PROJECT.md's "No real question banks" / `itembank guard` rule) and
follow the on-disk shape of what they mimic: `legacy_session.json` should look exactly like
what `write_session()` produces today (`schema_version`, `session_id`, `bank`, `items`,
`cursor`, `responses`, `status`, `mode`, `objective`, `seed`); `legacy_daily_log.md` should
match `write_day_log()`'s exact markdown-table output shape (`surfaces/day.py:468-482`).

---

### `.github/workflows/ci.yml` (modified — new schema-validation step)

**Analog:** itself — the existing step shape (`.github/workflows/ci.yml:14-30`):
```yaml
      - name: Broken fixture is caught
        run: |
          if python itembank.py lint fixtures/broken_bank.md; then
            echo "linter passed a deliberately broken bank; it regressed"
            exit 1
          fi
          for msg in "SELECT is 2" "does not exist" ...; do
            python itembank.py lint fixtures/broken_bank.md | grep -q "$msg" \
              || { echo "linter no longer reports: $msg"; exit 1; }
          done
```
Add a new step, same style, name descriptive of the assertion (`"Runtime output matches
schema"`), invoking either the new minimal validator module directly (`python -c "..."` or a
small dedicated script under `tests/` or `tools/`) against real `itembank` command output,
following the "Test suite" step's loop shape (`.github/workflows/ci.yml:38-43`) if the
validation belongs alongside `tests/*.py` rather than as a bespoke shell block.

## Shared Patterns

### Atomic file writes
**Source:** `runtime.py:143-150` (`write_session`)
**Apply to:** `evidence.py`'s index rebuild, any render writer (`render_attempt_md`,
`render_daily_log`, `render_session_json`) — every whole-file write in this phase must use
the tmp-file-then-`os.replace()` pattern, not a direct `open(path, "w")`.

### Single scorer / single writer discipline
**Source:** `runtime.py:116-126` (`score_response`) and its enforcement test
(`tests/scoring_roundtrip.py:96-109`)
**Apply to:** `evidence.py`'s `append_event()` must be the only function any surface calls to
persist a response; `surfaces/session.py`, `surfaces/quiz.py`, `surfaces/evidence_cli.py`,
`surfaces/migrate.py` are all callers, never independent writers. Mirror the existing
`os.walk` + regex CI-style self-check in the new evidence test.

### Canonical response reuse
**Source:** `runtime.py:66-96` (`canonical_response`)
**Apply to:** `evidence.py`'s idempotency key (D-17) — import and call this function, do not
reimplement per-type comparison logic. Only the `short`-item `None` case needs a documented
extension (hash of normalized text).

### `%d ..., %d ..., %d ...` status-line reporting
**Source:** `surfaces/cli.py:29` (`cmd_lint`), `surfaces/quiz.py:50-51` (`cmd_build`)
**Apply to:** `surfaces/migrate.py`'s dry-run/real-run count reconciliation output (EVID-06),
`surfaces/evidence_cli.py`'s `cmd_mark` batch summary.

### JSON stdout, `ensure_ascii=False, indent=2`
**Source:** `surfaces/session.py:35,42,66,73` (every `cmd_*` in the session surface)
**Apply to:** every new JSON-emitting command (`cmd_mark`, `cmd_migrate --dry-run`, any
evidence query command).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| Minimal JSON Schema validator (module name TBD by planner, e.g. `schema_validate.py`) | utility | transform | No existing validation/parsing-against-a-schema code anywhere in this codebase; `model.py`'s `lint()` validates a bank against domain rules but not against a JSON Schema document. Build fresh per RESEARCH.md's "Don't Hand-Roll" guidance (minimal subset: `type`, `required`, `properties`, `additionalProperties`, `enum`, `items`), no in-repo precedent to imitate. |
| Cross-platform locked append (`msvcrt.locking`/`fcntl.flock` wrapper) | utility | file-I/O | No file-locking code exists anywhere in this codebase today; `write_session`'s tmp+`os.replace()` solves a different problem (whole-file replace, not concurrent append). Use RESEARCH.md's Pattern 2 code example directly (`append_event` in Code Examples / Architecture Patterns) as the primary reference instead of an in-repo analog. |
| `evidence.jsonl` reader with retraction-aware view logic (D-10) | service | event-driven | No compensating-event / retraction concept exists in any current store (session JSON has no undo; attempt markdown is hand-edited). Design fresh from D-10's spec; `runtime.session_summary()` (`runtime.py:167-181`) is the closest "fold a list of records into an aggregate" shape worth reading for style (a `for r in responses` accumulation into a dict), but it has no retraction awareness to copy.

## Metadata

**Analog search scope:** `model.py`, `runtime.py`, `server.py`, `surfaces/*.py`, `tests/*.py`,
`.github/workflows/ci.yml`, `fixtures/*`
**Files scanned:** `model.py`, `runtime.py`, `surfaces/cli.py`, `surfaces/session.py`,
`surfaces/quiz.py`, `surfaces/day.py`, `tests/scoring_roundtrip.py`, `.github/workflows/ci.yml`
**Pattern extraction date:** 2026-08-06
