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
  critical: 1
  warning: 7
  info: 3
  total: 11
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-08-07T00:00:00Z
**Depth:** standard
**Files Reviewed:** 17
**Status:** issues_found

## Summary

Reviewed the daemon-consolidation and settings-foundation surface: the new
`server.py`-based `daemon.py` route table, the `settings.py`/`schema_validate.py`
contract behind `itembank config`, and the quiz/study/day render surfaces that the
daemon now serves from one process. The consolidation itself is careful about the
things its own docstrings call out (path allowlisting, `SystemExit` containment
around `session.do_*`, route-vs-CLI inventory, no key leakage to the browser) and
those specific claims hold up under inspection.

The standout problem is in `surfaces/quiz_page.py`: the client-side `esc()` helper
used everywhere item content is written into `innerHTML` does not actually escape
HTML — it is a `null`-coalescing stringifier, not a sanitizer — so any bank content
(stem, option text, rationale, trap, rubric, model answer) containing HTML markup
executes as markup in the browser. This is a real stored-XSS surface reachable
through the daemon's own `/quiz/<stem>` route, on the same bank content the project
says may already come from third-party sources (AAOS-12e-derived text, course
material, and — per the model-backend plans — eventually AI-generated content).

Beyond that, a handful of degrade-never-block and input-validation gaps were found
that don't match the rigor of the D-02/D-03/T-2-xx invariants documented elsewhere
in this same phase: a malformed-encoding `.md` file can crash the whole daemon at
startup instead of being skipped like a non-bank file; a hand-edited `itembank.json`
is never schema-validated on read (only on `config set`), so a bad nested value
crashes `cmd_daemon` with a raw `TypeError` instead of a `settings.*` message;
`cmd_guard`'s own skip-list is narrower than `daemon.py`'s (which explicitly notes
what `cmd_guard` is supposed to already exclude); and the day cockpit's per-plan
state, once built inside the consolidated daemon, never re-derives "today," so a
long-running `itembank daemon` process left up past midnight keeps serving
yesterday's plan row indefinitely.

## Critical Issues

### CR-01: The quiz page's client-side `esc()` does not escape HTML — stored XSS via bank content

**File:** `surfaces/quiz_page.py:125` (definition), used at (non-exhaustive)
`surfaces/quiz_page.py:209,247,286-289,351,426-451,477-480`

**Issue:** The template's `esc` helper is:

```js
const esc = s => (s==null?"":String(s));
```

This is a null/undefined guard plus `String()` coercion — it performs **no HTML
escaping** (no replacement of `<`, `>`, `&`, `"`). It is nonetheless used
throughout the page everywhere item content is inserted via `innerHTML` /
template-literal HTML strings rather than `textContent`:

- `card.innerHTML = ...<p class="stem">${esc(q.stem)}</p>` (item stem)
- `b.innerHTML = ...<span class="ot">${esc(o.text)}</span>` (mc/multi option text)
- `b.innerHTML = ...<span>${esc(s)}</span>` (build step text)
- `blk("Why this is best", ex.why)`, `blk(..., ex.disc)`, `blk(..., ex.second)`,
  `blk(..., ex.model)` → `` `<div class="blk">...${esc(val)}</div>` `` (rationale,
  discriminator, second-best, model answer)
- `ex.rubric.map(esc).join("</li><li>")` and `ex.notes.map(esc).join("</li><li>")`
  (rubric lines, notes — joined raw into `<li>` markup with no escaping)
- `finish()`'s "to harvest" list: `esc(m.q.stem.slice(0,110))`, `esc(m.ex.trap)`

Any of these fields containing HTML (e.g. `<img src=x onerror=alert(1)>` in a
stem, option, rationale, or rubric line) executes as markup in the learner's
browser the moment the item or its explanation renders. The codebase is aware of
this exact class of bug elsewhere in the same file — the `asAssign` per-row
category rationale explicitly uses `r.textContent = line;  // textContent, so a
bank cannot inject markup` — but that discipline was not applied to the `esc()`
helper the rest of the page relies on, so it is broken (or missing) everywhere
else. Compare `surfaces/study.py`'s client-side `esc`, which *does* escape
`& < >` correctly — the two surfaces disagree on what `esc` means.

This is reachable through the consolidated daemon's own `GET /quiz/<stem>` and
`POST /quiz/<stem>/answer` routes with no additional privilege needed, and the
project's own threat model already accepts that item text can originate from
third-party course material (and, per the model-backend roadmap, eventually
model-generated content) — i.e. content not fully trusted to be markup-free.

**Fix:** Make `esc()` actually escape, matching `study.py`'s version (or use
`textContent` at every one of these call sites instead of building HTML strings):

```js
const esc = s => (s==null?"":String(s))
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
```

Also audit `chips(q)`'s `LABEL[q.type]||q.type` fallback, which inserts `q.type`
unescaped with no `esc()` call at all (lower risk since `type` is normally one of
a fixed enum, but should not depend on that going forward).

## Warnings

### WR-01: `scan_dir()` crashes the whole daemon on one badly-encoded `.md` file

**File:** `surfaces/daemon.py:138-146` (also affects `surfaces/day.py:parse_plan`,
called from the same loop)

**Issue:** `scan_dir()` (called once at `itembank daemon` startup to build the
bank/plan allowlist) does:

```python
text = open(path, encoding="utf-8").read()
qs = parse_bank(text)
```

with no `try/except` around the read. Every other classification outcome in this
function degrades gracefully ("neither a bank nor a plan; skip silently" — line
145), matching the project's stated "degrade, never block" constraint. But a
`.md` file in the served directory that is not valid UTF-8 (a binary file
mis-named `.md`, a Windows-1252-saved note, a stray BOM-less legacy file) raises
`UnicodeDecodeError` here uncaught, which propagates out of `scan_dir()` and
aborts `cmd_daemon()` before it ever binds a socket — one bad file prevents the
daemon from serving every other bank and plan in the directory, not just the
offending one.

**Fix:** Wrap the read/classify per candidate and skip files that fail to decode,
the same way a non-bank/non-plan file is already skipped:

```python
try:
    text = open(path, encoding="utf-8").read()
except (OSError, UnicodeDecodeError):
    continue
```

### WR-02: `load_settings()` never validates against the schema, so a malformed `itembank.json` crashes `cmd_daemon` with a raw `TypeError` instead of a `settings.*` error

**File:** `surfaces/settings.py:83-102`, consumed at `surfaces/daemon.py:1089`

**Issue:** `settings.py`'s own module docstring says "There is exactly one
validator here... one contract, printed either as a human summary or verbatim
off disk, and one validator behind every write." That validator
(`schema_validate.validate`) only runs inside `cmd_config`'s `set` action.
`load_settings()` — the function every other consumer (`cmd_daemon`, and any
future reader) calls to get the effective config — only checks that the file
parses as JSON and that the top level is a dict:

```python
try:
    raw = json.load(open(path, encoding="utf-8"))
except (OSError, ValueError) as exc:
    sys.exit("settings.malformed_file: cannot read %s: %s" % (path, exc))
if not isinstance(raw, dict):
    sys.exit("settings.malformed_file: %s does not contain a JSON object" % path)
return merge_over_defaults(defaults, raw)
```

`merge_over_defaults` only recurses into a nested key when *both* the default and
the raw value are dicts (`surfaces/settings.py:73`); otherwise it takes the raw
value verbatim. So a hand-edited `itembank.json` with, say, `"daemon": "oops"`
(a string instead of an object — plausible from a manual edit or an
older/foreign tool writing the file) loads without complaint. `cmd_daemon` then
does `cfg["daemon"]["port"]`, which raises `TypeError: string indices must be
integers`, uncaught, instead of the friendly `settings.malformed_file` /
`settings.invalid_type` message the rest of the module is built around.

**Fix:** Run `schema_validate.validate(raw, schema)` inside `load_settings()`
(after the dict check, before merging) and `sys.exit` with a `settings.*`-coded
message on the first error, the same shape `cmd_config`'s `set` path already
uses.

### WR-03: `cmd_guard` does not exclude `_attempts/`/`_evidence/`, unlike `daemon.py`'s own skip-list

**File:** `surfaces/cli.py:74-97` (specifically line 82), vs.
`surfaces/daemon.py:36-39`

**Issue:** `daemon.py`'s `SKIP_DIRS` comment reads: "Same directories `cmd_guard`
skips, plus the two this daemon itself writes into" — i.e. it documents that
`cmd_guard` is expected to already skip `.git`/`.github`/`fixtures`, and that
`_attempts`/`_evidence` are the daemon's *additional* exclusions on top of that.
But `cmd_guard`'s own walk only excludes `(".git", "fixtures", ".github")`:

```python
dirs[:] = [d for d in dirs if d not in (".git", "fixtures", ".github")]
```

`_attempts/*_attempt_*.md` files are machine-rendered from `evidence.py` and
mirror the item-heading/option/verdict shape closely enough that they can
plausibly parse as a non-empty bank via `parse_bank()`. Both `_attempts/` and
`_evidence/`-adjacent generated files are gitignored (so a clean CI checkout
never has them), but `cmd_guard` walks the live filesystem, not git state — a
developer running `itembank guard .` locally after sitting a quiz would get a
false-positive "parses as a question bank" failure on their own generated
attempt file, undermining confidence in the one mechanical check this project
relies on to keep real banks out of the repo.

**Fix:** Align `cmd_guard`'s skip set with `daemon.py`'s `SKIP_DIRS`
(`{".git", ".github", "fixtures", "_attempts", "_evidence"}`), or better, have
one module own the shared constant so the two lists cannot drift again.

### WR-04: The daemon's per-plan day state never re-derives "today," so a long-running daemon shows a stale date forever

**File:** `surfaces/daemon.py:544-566` (`_plan_day_state`), `surfaces/day.py:832-890`
(`day_state`, `day_render`)

**Issue:** `_plan_day_state()` builds a `day.day_state()` once per plan stem and
caches it for the life of the handler class:

```python
state = handler.day_states.get(stem)
if state is not None:
    return state
...
iso = override.get("iso") or datetime.date.today().isoformat()
state = day.day_state(path, log_path, lanes_path, iso, base="/day/%s" % stem)
handler.day_states[stem] = state
return state
```

`day_render()`'s 60-second cache only refreshes `day_info` (fuses, Anki counts,
git evidence) — it never touches `state["iso"]`/`state["today"]`, which are fixed
at first-request time. Under the new consolidated `itembank daemon` (as opposed
to the old, short-lived per-day `cmd_day` process this replaces), the process is
meant to be able to run indefinitely across multiple banks and plans. If it stays
up past midnight, every subsequent `GET /day/<stem>` (and `GET /day`) keeps
rendering yesterday's plan row, streak, and history against a date that is no
longer "today" — with no error, just silently stale data for the one surface
whose entire point is "what does today owe."

**Fix:** Either rebuild `iso`/`today` (and hence the cached `day_state`) once the
wall-clock date has advanced past `state["today"]`, or drop the per-stem cache
entirely and rebuild the cheap parts of `day_state` (everything except the parsed
plan/log) on every request the way `day_render()`'s `day_info` refresh already
does.

### WR-05: `count` on `/api/start` (and the CLI's `--count`) is type-checked but not range-checked; a negative value silently truncates instead of erroring

**File:** `surfaces/session.py:54-59` (`do_start`), `surfaces/daemon.py:756-758`
(`handle_api_start`)

**Issue:** `handle_api_start` only guards `count`'s *type*:

```python
count = data.get("count", 10)
if not isinstance(count, int) or isinstance(count, bool):
    count = 10
```

`do_start` then does `items = candidates[:min(count, len(candidates))]`. Python
slicing with a negative stop index means "up to but excluding the last `|count|`
elements" — e.g. `count = -1` silently produces *almost the entire bank*
(`candidates[:-1]`) instead of the obviously-invalid input it looks like. A
client (or a CLI user via `--count -1`, which argparse also accepts with no
`choices`/range restriction) gets a session sized nothing like what they asked
for, with no error at all.

**Fix:** Reject or clamp `count < 1` explicitly (e.g. treat it the same as an
invalid type and fall back to the default, or `sys.exit`/400 with a clear
message), rather than letting Python's slice semantics decide the behavior.

### WR-06: `ms_since()` can record a negative `response_time_ms`, unlike its client-side counterpart

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

There is no floor at zero. The client-side JS computes the analogous value with
`Math.max(0, Math.round(performance.now() - shownAt))` specifically because a
wall-clock-based delta can go negative under a system clock change — but
`ms_since` uses `datetime.datetime.now()` (wall clock, not monotonic), so the
same hazard applies here and is *not* guarded. A backward clock adjustment
mid-session (NTP correction, manual clock change, DST edge case in some
platforms' local-time handling) produces a negative `response_time_ms` written
into the permanent evidence log — violating the non-negative invariant the
project's own `tests/evidence_roundtrip.py` (`response_time_ms is not a
non-negative int`) assumes holds for every recorded event.

**Fix:** Clamp: `return max(0, int((now - served).total_seconds() * 1000))`.

### WR-07: `schema_validate.check_schema()` accepts `$ref` as a keyword but never resolves or recurses into it, contradicting the module's own "whole document checked before any instance" guarantee

**File:** `schema_validate.py:45-71` (`check_schema`) vs. `108-116` (`$ref`
resolution inside `validate`)

**Issue:** The module docstring states: "a schema that uses a keyword outside
that set is refused, not partially checked... A green result from this validator
means the whole document was checked." `check_schema()` does treat `$ref` as a
recognized keyword (it's in `SUPPORTED`), but its per-keyword dispatch only
recurses for `properties`, `$defs`, `items`, and `oneOf` — there is no branch for
`$ref` at all, so it never checks that the target actually resolves, and never
recurses into the referenced subschema to check *it* for unsupported keywords.
A malformed or dangling `$ref` (e.g. `{"$ref": "#/$defs/typo"}`) passes
`check_schema()` silently and only raises `SchemaError` later, inside
`validate()`, and only if an instance actually exercises that branch (line
108-115) — exactly the "looks like a green build while checking half the
contract" failure mode the module's own docstring says it exists to prevent.
`schemas/settings.schema.json` does not currently use `$ref`, so there is no
live impact today, but the guarantee is not actually enforced for the next
schema that does.

**Fix:** Give `check_schema()` a `$ref` branch that resolves the target against
`$defs` at the top level (which requires threading the root document down through
`check_schema`, similar to how `validate()` threads `root`) and recurses into it.

## Info

### IN-01: "already recorded" progress note can race under concurrent requests

**File:** `surfaces/daemon.py:505-521` (`handle_quiz_answer`)

**Issue:** `Daemon` mixes in `ThreadingMixIn`, so concurrent POSTs to the same
bank's `/quiz/<stem>/answer` run in parallel threads. The "already recorded"
progress note is derived from comparing `os.path.getsize(sess["log"])` before and
after the write, with no lock:

```python
size_before = os.path.getsize(sess["log"]) if os.path.exists(sess["log"]) else -1
score = quiz.record_answer(...)
...
already = size_before >= 0 and os.path.getsize(sess["log"]) == size_before
```

Two overlapping requests can interleave their size snapshots, producing a
misleading "(already recorded)" (or its absence) in the printed progress line.
This is cosmetic only — the actual dedupe decision lives inside
`evidence.append_event`, not here — but worth a comment or a lock if the note is
meant to be trustworthy under concurrency.

**Fix:** Either accept this as a best-effort UX note (document it as such) or
guard the read-modify-read with a per-bank lock.

### IN-02: `Q.sort(()=>Math.random()-0.5)` is a biased shuffle

**File:** `surfaces/quiz_page.py:491`

**Issue:** Sorting with a random comparator is a well-known anti-pattern: it does
not produce a uniform shuffle (some orderings are far more likely than others),
and the ECMAScript spec does not even guarantee the comparator is called on
every pair. `shuffled()` earlier in the same file (line 187) correctly
implements Fisher–Yates and is used for options/rows/steps — the item order
itself uses the weaker pattern instead.

**Fix:** Reuse `shuffled(Q)` in place of `Q.sort(()=>Math.random()-0.5)`.

### IN-03: Raw exception text returned to the client in 500 responses, reachable over `--lan`

**File:** `surfaces/daemon.py` — every `except Exception as exc:
handler.send_error(500, str(exc))` (e.g. lines 525, 607, 626, 786, 809, 840, 861)

**Issue:** Every route handler that catches a routine failure returns the raw
Python exception string as the HTTP error body. Under `--lan` (which the daemon's
own banner already flags as "no accounts and no authentication by design"), any
device on the local network can trigger these paths and see internal exception
text, which can include file paths or other implementation detail not otherwise
exposed by the documented not-found/error copy used elsewhere (e.g.
`NOT_FOUND_BODY`, which is deliberately scrubbed — see `T-2-05` in the daemon
module docstring).

**Fix:** Return a generic message to the client and log `str(exc)` server-side
instead, at least for the `--lan` case.

---

_Reviewed: 2026-08-07T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
