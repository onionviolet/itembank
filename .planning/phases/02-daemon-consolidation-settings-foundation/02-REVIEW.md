---
phase: 02-daemon-consolidation-settings-foundation
reviewed: 2026-08-07T00:00:00Z
depth: standard
files_reviewed: 17
files_reviewed_list:
  - itembank.json
  - schema_validate.py
  - schemas/settings.schema.json
  - surfaces/cli.py
  - surfaces/daemon.py
  - surfaces/day.py
  - surfaces/quiz.py
  - surfaces/quiz_page.py
  - surfaces/session.py
  - surfaces/settings.py
  - surfaces/study.py
  - tests/agent_roundtrip.py
  - tests/config_roundtrip.py
  - tests/daemon_roundtrip.py
  - tests/day_roundtrip.py
  - tests/evidence_roundtrip.py
  - tests/serve_roundtrip.py
findings:
  critical: 2
  warning: 8
  info: 3
  total: 13
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-08-07T00:00:00Z
**Depth:** standard
**Files Reviewed:** 17
**Status:** issues_found

## Summary

This is a re-review of the daemon-consolidation/settings-foundation surface after
commit `6a00bea` fixed the stored-XSS defect (`quiz_page.py`'s `esc()` performing
no HTML escaping) an earlier pass of this same review flagged as CR-01.
**That fix is confirmed correct**: `esc` now replaces `& < >`
(`surfaces/quiz_page.py:125`), and no equivalent unescaped-bank-content-into-
`innerHTML` pattern was found anywhere else in `surfaces/quiz_page.py`,
`surfaces/day.py`, or `surfaces/study.py` — all three consistently escape
bank/plan-derived text before writing it into HTML.

The route table, allowlist-based bank/session resolution, and the `/api/*` input
validation (path-field rejection, traversal rejection, `SystemExit` containment
around `session.do_*`) remain careful and are backed by an unusually thorough test
suite (`tests/daemon_roundtrip.py`, `tests/config_roundtrip.py`).

Two new (or previously under-weighted) **crash-class** defects were found and
reproduced directly against the code in this diff, both fitting this review's
"crashes" criterion for Critical severity rather than Warning: (1) a single
non-UTF-8 `.md` file anywhere under the directory `itembank daemon` is pointed at
takes the *entire* daemon startup down with an uncaught `UnicodeDecodeError`
before it binds a socket, and (2) `itembank.json` is never validated against its
own schema on read, so a syntactically-valid-JSON-but-schema-invalid settings
file crashes `daemon`/`config set` with a raw Python traceback instead of the
project's own `sys.exit()`-with-a-message convention. Several further
input-validation and robustness gaps below round out the standard-depth pass:
a negative `count` on `/api/start`/`--count` is accepted and silently produces a
near-full-bank session via Python's slice semantics; internal `500` responses can
leak local filesystem paths the way `404` responses are deliberately hardened
against not to; the day cockpit's per-plan "today" is computed once and never
re-derived, so a long-running consolidated daemon serves a stale date past
midnight; and a couple of smaller correctness/robustness items round out the
list. None of the findings below is a stored/reflected-XSS-class issue — that
class of defect appears closed for this phase's surfaces.

## Critical Issues

### CR-01: One non-UTF-8 `.md` file anywhere in the served directory crashes the entire daemon at startup

**File:** `surfaces/daemon.py:107-152` (`scan_dir`), specifically line 138

**Issue:** `scan_dir()` — run once, synchronously, before `itembank daemon` binds
any socket — reads every candidate `.md` file with a hard-coded UTF-8 decode and
no error handling:

```python
text = open(path, encoding="utf-8").read()
qs = parse_bank(text)
```

Every *other* classification outcome in this same function degrades gracefully
("neither a bank nor a plan; skip silently", line 145), matching this project's
stated "degrade, never block" constraint (CLAUDE.md). But a `.md` file that is not
valid UTF-8 — a stray editor backup, a mis-renamed binary, a Windows-1252-saved
note, anything an Obsidian vault or a course-materials folder plausibly
accumulates — raises `UnicodeDecodeError` here, uncaught, which propagates out of
`scan_dir()` and aborts `cmd_daemon()` entirely. One bad file anywhere under the
served root prevents the daemon from serving *every* other bank and plan, not
just the offending one. Reproduced directly:

```
$ python itembank.py daemon <dir-containing-one-non-utf8-.md-file> --no-open
itembank daemon
  dir     ...
Traceback (most recent call last):
  ...
  File ".../surfaces/daemon.py", line 138, in scan_dir
    text = open(path, encoding="utf-8").read()
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
```

**Fix:** Wrap the read/classify per candidate and skip files that fail to decode,
consistent with the "skip silently" precedent already in the same loop:

```python
try:
    text = open(path, encoding="utf-8").read()
except (OSError, UnicodeDecodeError):
    continue
```

### CR-02: `itembank.json` is never validated against its own schema on read — a type-invalid (but JSON-valid) settings file crashes `daemon` and `config set` with a raw traceback

**File:** `surfaces/settings.py:83-102` (`load_settings`), `surfaces/settings.py:131-136` (`set_at`), `surfaces/daemon.py:1088-1090` (`cmd_daemon`), `surfaces/daemon.py:1008` (`start_server`)

**Issue:** `settings.py`'s own module docstring states "There is exactly one
validator here, `schema_validate.validate()`... one contract... and one validator
behind every write." That validator only actually runs inside `cmd_config`'s
`set` action. `load_settings()` — the function `cmd_daemon` and every other
consumer calls to get the effective config — only checks that the file parses as
JSON and that the top level is a dict; it never runs the result through
`schema_validate.validate()`. `merge_over_defaults()` only recurses into a nested
key when *both* the default and the raw value are dicts
(`surfaces/settings.py:73`) — otherwise it takes the raw value verbatim, type
mismatch and all. A hand-edited, merge-conflicted, or foreign-tool-written
`itembank.json` that is syntactically valid JSON but violates the schema's types
therefore loads without complaint and crashes later with no `settings.*`-coded
message at all. Three concrete reproductions against a temp `itembank.json`:

1. `"daemon": "oops-not-a-dict"` → `itembank daemon <dir>` crashes at
   `surfaces/daemon.py:1090` (`cfg["daemon"]["lan"]`) with
   `TypeError: string indices must be integers, not 'str'`.
2. `"daemon": {"port": "not-an-int", "lan": false, "open_browser": true}` →
   `itembank daemon <dir>` crashes inside `socketserver.TCPServer.server_bind()`
   (via `surfaces/daemon.py:1008`, `Daemon((host, port), handler_cls)`) with
   `TypeError: 'str' object cannot be interpreted as an integer` — the bad value
   reaches the raw OS socket call.
3. `"daemon": "oops-not-a-dict"` → `itembank config set daemon.port 9000 --base
   <dir>` crashes at `surfaces/settings.py:136` (`set_at`,
   `node[parts[-1]] = value`) with `TypeError: 'str' object does not support item
   assignment`.

`tests/config_roundtrip.py::test_config_malformed_file` only covers JSON
*syntax* errors (`"{not valid json"`), not schema-*type* errors in otherwise-valid
JSON, so none of the three reproductions above is caught by the existing suite.
Note that `surfaces/settings.py:print_table` (the plain `config` table) *does*
guard against exactly this (`nested_current = data.get(name) if
isinstance(data.get(name), dict) else {}`) — the project is clearly aware a
nested value can be malformed, the guard just was never applied to the two paths
(`cmd_daemon`, `set_at`) that assume the schema's shape holds.

**Fix:** Validate the merged document against the schema inside
`load_settings()` and `sys.exit()` with a `settings.*`-coded message on failure,
the same shape the JSON-syntax-error path already uses:

```python
def load_settings(base):
    schema = load_schema()
    defaults = defaults_from_schema(schema)
    path = settings_path(base)
    if not os.path.exists(path):
        return dict(defaults)
    try:
        raw = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.exit("settings.malformed_file: cannot read %s: %s" % (path, exc))
    if not isinstance(raw, dict):
        sys.exit("settings.malformed_file: %s does not contain a JSON object" % path)
    merged = merge_over_defaults(defaults, raw)
    errs = schema_validate.validate(merged, schema)
    if errs:
        sys.exit("%s: %s" % (classify_error(errs[0]), errs[0]))
    return merged
```

This closes all three reproductions at one point instead of requiring every
current and future caller to defensively type-check its own slice of the
document.

## Warnings

### WR-01: Daemon `500` responses can leak local filesystem paths, unlike its `404` responses

**File:** `surfaces/daemon.py:371,525,607,626,786,809,840,861` (every `handler.send_error(500, str(exc))`)

**Issue:** The daemon is deliberately careful that a `404` never leaks the served
directory or a traceback (`send_not_found`'s docstring, `NOT_FOUND_BODY`, and
`tests/daemon_roundtrip.py`'s `check_unknown_stem`/`check_report_not_found`
assert this explicitly, citing `T-2-05`). No equivalent care applies to the
generic `except Exception` clauses that produce a `500`: every one of them does
`handler.send_error(500, str(exc))`, and `str(exc)` on an `OSError`/`IOError`
(permission denied, disk full, a file moved mid-request) typically includes the
full absolute path involved. A `--lan` daemon serves these same handlers to every
device on the local network — the startup banner even prints "itembank has no
accounts and no authentication by design" — so an ordinary I/O error is one of
the few ways a client elsewhere on the LAN could learn the served directory's
absolute path, exactly what the `404` path was hardened against.

**Fix:** Log `str(exc)` server-side (stdout, matching this project's existing
logging convention) and send a generic, path-free message to the client instead,
e.g. `handler.send_error(500, "internal error")`.

### WR-02: The index's "View report" link resolves to an arbitrary session, not the most recent one

**File:** `surfaces/daemon.py:391-420` (`sessions_by_bank`), `surfaces/daemon.py:431-439` (`handle_index`)

**Issue:** `sessions_by_bank()`'s own docstring says the picked session is
"lexically-last session_id wins" when a bank has more than one recorded session,
and the code matches: `for session_id, path in sorted(index.items()): ...
result[stem] = session_id`. `session_id` is `uuid.uuid4().hex`
(`surfaces/quiz.py:131`, `surfaces/session.py:62`), unrelated to creation time.
For a bank sat more than once, `GET /`'s "View report" link therefore opens
whichever session's hex string happens to sort largest — not the most recently
created or most recently active one. A learner who resits a bank will often find
"View report" opening a stale, unrelated earlier sitting instead of the one they
just finished.

**Fix:** Key the picked session by an actual time signal instead of the
`session_id` string — e.g. the session file's own `mtime` (cheap to read
alongside the existing `open()`/`json.load()` already in the loop), or the
`served_ts` field already present in the session JSON.

### WR-03: `POST /day/<stem>/open` returns a generic `500` instead of `400` for a non-numeric `i`

**File:** `surfaces/day.py:909-917` (`apply_day_post`), `surfaces/daemon.py:612-631` (`handle_day_open`)

**Issue:** `apply_day_post`'s `open` branch does `i = int(data.get("i") or 0)`
with no type guard, unlike every comparable `/api/*` input field in this phase
(`count`/`seed`/`mode`/`confidence` in `handle_api_start`/`handle_api_submit`,
the forbidden-field checks in `api_read_json`). A body such as `{"lane": "EMT",
"i": "not-a-number"}` raises an uncaught `ValueError` inside `apply_day_post`;
`handle_day_open`'s blanket `except Exception` turns that into a `500` rather
than the `400` every other malformed-shape case in this same module returns.

**Fix:**

```python
i = data.get("i")
if not isinstance(i, int) or isinstance(i, bool):
    return None   # caller already turns None into a clean client-facing error
```

### WR-04: `/api/start` and the CLI's `--count` accept a negative count, which silently truncates the bank via Python slice semantics instead of erroring

**File:** `surfaces/session.py:54-59` (`do_start`), `surfaces/daemon.py:756-758` (`handle_api_start`)

**Issue:** `handle_api_start` only type-checks `count`:

```python
count = data.get("count", 10)
if not isinstance(count, int) or isinstance(count, bool):
    count = 10
```

`do_start` then does `items = candidates[:min(count, len(candidates))]`. Python's
slice semantics treat a negative stop index as "up to but excluding the last
`|count|` elements," so `count = -1` silently produces *nearly the entire bank*
instead of erroring on the obviously-invalid input. Reproduced directly: a
6-item fixture bank with `--count -1` produces a 5-item session, exit code 0, no
warning of any kind:

```
$ python itembank.py start fixtures/sample_bank.md --count -1 --seed 0
# session_file's "items" array has length 5, not the requested (invalid) -1
```

The same gap exists on the CLI (`argparse`'s `--count` has no range restriction),
and on `/api/start`'s `count` field.

**Fix:** Reject or clamp `count < 1` explicitly rather than letting the slice
decide behavior — e.g. treat a non-positive count the same as an invalid type
(daemon path) and `sys.exit` with a clear message (CLI path).

### WR-05: `ms_since()` can record a negative `response_time_ms` under a backward wall-clock change, unlike its client-side counterpart

**File:** `surfaces/session.py:32-45`

**Issue:**

```python
def ms_since(ts):
    if not ts:
        return None
    try:
        served = datetime.datetime.strptime(...)...
    except ValueError:
        return None
    now = datetime.datetime.now(datetime.timezone.utc)
    return int((now - served).total_seconds() * 1000)
```

There is no floor at zero. The client-side JS computes the analogous quantity
with `Math.max(0, Math.round(performance.now() - shownAt))`
(`surfaces/quiz_page.py:154`) specifically *because* a wall-clock-based delta can
go negative under a system clock adjustment — the comment there says as much
(T-1-25). `ms_since` uses `datetime.datetime.now()` (wall clock, not monotonic),
so the identical hazard applies here and is unguarded: an NTP correction or
manual clock change between `do_next`'s `served_ts` write and a later `do_submit`
can write a negative `response_time_ms` into the permanent evidence log,
violating the non-negative invariant `tests/evidence_roundtrip.py` itself asserts
(`response_time_ms is not a non-negative int`).

**Fix:** `return max(0, int((now - served).total_seconds() * 1000))`.

### WR-06: The daemon's per-plan day state fixes "today" once and never re-derives it — a long-running daemon shows a stale date forever

**File:** `surfaces/daemon.py:544-566` (`_plan_day_state`), `surfaces/day.py:832-890` (`day_state`, `day_render`)

**Issue:** `_plan_day_state()` builds a `day.day_state()` once per plan stem and
caches it for the life of the handler class (`handler.day_states[stem] = state`,
returned unchanged on every later request). `day_render()`'s 60-second cache only
refreshes `day_info` (fuses, Anki counts, git evidence) — it never touches
`state["iso"]`/`state["today"]`, which are fixed at first-request time
(`iso = override.get("iso") or datetime.date.today().isoformat()`). Under the
consolidated `itembank daemon` — meant to run indefinitely across multiple banks
and plans, unlike the old short-lived per-day `cmd_day` process this replaces —
if the process stays up past midnight, every subsequent `GET /day/<stem>` (and
`GET /day`) keeps rendering yesterday's plan row, streak, and history against a
date that is no longer "today," with no error and no visible signal that the
date is stale.

**Fix:** Either rebuild `iso`/`today` (and the day-log derivation that depends on
it) once the wall-clock date has advanced past `state["today"]`, or drop the
per-stem `day_states` cache entirely and rebuild the cheap parts of `day_state`
on every request the way `day_render()`'s `day_info` refresh already does.

### WR-07: `schema_validate.check_schema()` never resolves or recurses into `$ref`, contradicting the module's own "whole document checked" guarantee

**File:** `schema_validate.py:45-71` (`check_schema`) vs. `schema_validate.py:108-116` (`$ref` resolution inside `validate`)

**Issue:** The module docstring states: "a schema that uses a keyword outside
that set is refused, not partially checked... A green result from this validator
means the whole document was checked." `check_schema()` does list `$ref` in
`SUPPORTED`, but its per-keyword dispatch only recurses for `properties`,
`$defs`, `items`, and `oneOf` — there is no branch for `$ref` at all. It never
checks that a `$ref`'s target actually resolves, and never recurses into the
referenced subschema to check *it* for unsupported keywords. A malformed or
dangling `$ref` (e.g. `{"$ref": "#/$defs/typo"}`) currently passes
`check_schema()` silently and only surfaces as a `SchemaError` inside
`validate()` — and only if an instance happens to exercise that exact branch
(lines 108-115). This is the precise "looks like a green build while checking
half the contract" failure mode the module's own docstring says it exists to
prevent. `schemas/settings.schema.json` does not currently use `$ref`, so there
is no live impact today, but the guarantee this module advertises is not
actually enforced for the next schema that adds one.

**Fix:** Give `check_schema()` a `$ref` branch that resolves the target against
the top-level `$defs` (threading `root` down through `check_schema`, mirroring
how `validate()` already threads `root`) and recurses into the resolved
subschema.

### WR-08: `data.get("i")` in the day "open" handler and similar loosely-typed daemon inputs would benefit from the same explicit type checks `/api/*` already applies elsewhere

**File:** `surfaces/day.py:914`

**Issue:** Folded into WR-03 above; listed separately here only to flag that the
pattern (`int(x or 0)` / bare `int(x)` on a client-supplied JSON value) is worth
a repo-wide sweep rather than a single spot-fix, since the same shape could
recur as `/day/*` or a future `/api/*` route grows more fields.

**Fix:** See WR-03's fix; consider a small shared helper (`as_int(data, key,
default=None)` returning `None` on any non-`int`/`bool` value) used by every
handler that currently hand-rolls this check inconsistently.

## Info

### IN-01: `quiz_page.py`'s item-type chip is the one bank-derived field not routed through `esc()`

**File:** `surfaces/quiz_page.py:191`

**Issue:** `` `<span class="chip type">${LABEL[q.type]||q.type}</span>` `` is the
only bank-derived value in this template inserted without going through the
now-fixed `esc()` — every other field (stem, option text, why, discriminator,
trap, rubric, notes) does. It is not currently exploitable: `model.py`'s
`[TYPE: ...]` parser constrains the value to `\w+` (`model.py:41`), which cannot
carry HTML metacharacters. But that constraint lives in a different module than
the escaping discipline this file otherwise applies uniformly — exactly the kind
of split the project's own CR-01 fix (commit `6a00bea`) just closed for every
other field.

**Fix:** Route `q.type` through `esc()` too, so the page's escaping discipline
does not depend on a parser-level assumption holding forever.

### IN-02: `Q.sort(()=>Math.random()-0.5)` is a biased shuffle

**File:** `surfaces/quiz_page.py:491`

**Issue:** Sorting with a random comparator is a well-known non-uniform shuffle
(some orderings are far more likely than others), and the comparator is not even
guaranteed to be invoked on every pair. `shuffled()` earlier in the same file
(line 187) correctly implements Fisher–Yates and is used for options/rows/steps
— the overall item order uses the weaker pattern instead.

**Fix:** `shuffled(Q)` in place of `Q.sort(()=>Math.random()-0.5)`.

### IN-03: The "already recorded" progress note can race under concurrent requests to the same bank

**File:** `surfaces/daemon.py:505-521` (`handle_quiz_answer`)

**Issue:** `Daemon` mixes in `ThreadingMixIn`, so concurrent `POST`s to the same
bank's `/quiz/<stem>/answer` run in parallel threads. The printed "already
recorded" progress note is derived from an unlocked read-modify-read of the
evidence log's file size:

```python
size_before = os.path.getsize(sess["log"]) if os.path.exists(sess["log"]) else -1
score = quiz.record_answer(...)
already = size_before >= 0 and os.path.getsize(sess["log"]) == size_before
```

Two overlapping requests can interleave their size snapshots, producing a
misleading "(already recorded)" note (or its absence). This is cosmetic only —
the real dedupe decision lives inside `evidence.append_event`, not here — but is
worth a comment acknowledging the race, or a per-bank lock if the note is meant
to be trustworthy under concurrency.

**Fix:** Document as best-effort, or guard with a per-bank lock.

---

_Reviewed: 2026-08-07T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
