---
phase: 01-evidence-spine-protocol-foundation
reviewed: 2026-08-06T00:00:00Z
depth: standard
files_reviewed: 24
files_reviewed_list:
  - evidence.py
  - model.py
  - runtime.py
  - schema_validate.py
  - itembank.py
  - surfaces/cli.py
  - surfaces/day.py
  - surfaces/evidence_cli.py
  - surfaces/migrate.py
  - surfaces/protocol_cli.py
  - surfaces/quiz.py
  - surfaces/quiz_page.py
  - surfaces/session.py
  - schemas/item.schema.json
  - schemas/lint_error.schema.json
  - schemas/report.schema.json
  - schemas/response.schema.json
  - schemas/session.schema.json
  - tests/durability_roundtrip.py
  - tests/evidence_roundtrip.py
  - tests/protocol_roundtrip.py
  - tests/serve_roundtrip.py
  - .github/workflows/ci.yml
  - .gitignore
findings:
  critical: 2
  warning: 4
  info: 2
  total: 8
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-08-06
**Depth:** standard
**Files Reviewed:** 24
**Status:** issues_found

## Summary

The evidence spine (append-only log, dedupe, retraction, renders, disposable
sqlite3 index, migration) is implemented carefully and is backed by an
unusually thorough test suite that exercises crash-kill, concurrent writers,
retraction ordering, and index disposability end to end. The core append/read
primitives in `evidence.py` are sound and match their own documentation for
the happy paths the tests cover.

Two defects survived that testing, though, and both sit exactly on the
priorities called out for this review: a crash-safety hole in the log reader
that contradicts the module's own "never fatal" contract, and a client-side
HTML-escaping gap in the served quiz page that both breaks rendering for
ordinary mathematical content (`<`, `>`) and opens a DOM-injection path for
anything else in a stem, option, rationale, or model answer. Several smaller
contract-drift and idempotency-window issues are also documented below.

## Critical Issues

### CR-01: `evidence.iter_raw()` can crash on a torn multi-byte UTF-8 sequence, contradicting D-09's "never fatal" guarantee

**File:** `evidence.py:257-281` (specifically `open(path, encoding="utf-8")` at line 268 and the unguarded `for lineno, raw in enumerate(fh, 1)` at line 269)

**Issue:** `iter_raw()` is the one reader every evidence consumer is built on
(`events()`, `live_events()`, `retracted_ids()`, `objective_history()`'s
fallback, `attempt_number()`, `marks_by_event()`, `render_attempt_md()`,
`render_session_json()`, `day_log_from_events()`). Its own docstring, and
`evidence.py`'s module docstring, promise: "a malformed line is skipped and
reported, never fatal (D-09)... a torn line at the tail of a growing log is
an expected failure mode, not a corruption event that should take the rest
of the log down with it."

The implementation only wraps `json.loads(stripped)` in `try/except
(ValueError, TypeError)`. The file is opened in text mode with
`encoding="utf-8"` and no `errors=` argument, so decoding happens inside
Python's `TextIOWrapper` as the `for` loop pulls each line — *outside* the
try/except. If the process is killed (power loss, OOM-kill, `taskkill`)
while `append_line`/`append_line_checked` is mid-write on a line that
contains multi-byte UTF-8 content (any short-answer text, objective, or
rationale with non-ASCII characters — the codebase explicitly exercises CJK
content in `tests/protocol_roundtrip.py`, and the project targets a Mandarin
study lane), the tail of the file can end mid-sequence. Reading that file
back raises `UnicodeDecodeError` (a `ValueError` subclass, but raised at
decode time inside the iterator, not inside the try block that only guards
`json.loads`), which propagates uncaught out of `iter_raw()` and crashes
every caller — `itembank evidence`, `itembank report`, `itembank mark`,
`itembank render`, the `day` cockpit, and `itembank serve`'s own
save-and-render-on-every-answer path — on the very next read.

Note that the *other* tail readers in this file (`_tail_dedupe_keys()`,
`_index_tail_update()`) already defend against exactly this by reading raw
bytes and calling `.decode("utf-8", errors="replace")` themselves. `iter_raw`
is the odd one out, and it is also the most heavily used.

`tests/durability_roundtrip.py`'s `probe_kill()` exercises the "reader
survives a kill mid-write" scenario but pads every line with ASCII `x`/`y`
characters, so it never actually lands a kill inside a multi-byte sequence —
this exact failure mode is untested.

**Fix:**
```python
def iter_raw(path):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8", errors="replace") as fh:
        for lineno, raw in enumerate(fh, 1):
            ...
```
`errors="replace"` matches the posture already used by `_tail_dedupe_keys`
and `_index_tail_update`, and keeps the promise that a torn tail degrades to
a reported, skipped line (the replaced/garbled JSON will simply fail
`json.loads` and be reported as malformed) rather than crashing the reader.

---

### CR-02: The served quiz page's client-side `esc()` does not escape HTML — stem/option/rationale text is injected via `innerHTML` unescaped

**File:** `surfaces/quiz_page.py:125` (definition), with unescaped `innerHTML` uses at lines 194-196 (`chips()`), 209 (`stem`), 247 (option text), 351 (build step text), 426-435 (`blk()` for why/disc/second/model and the rubric list), 449 (notes list), 451 (trap), 477-479 (missed-item recap)

**Issue:** The client-side helper is named to suggest HTML escaping but does
not perform any:
```js
const esc = s => (s==null?"":String(s));
```
It only null-guards and stringifies. Every one of the call sites above feeds
its result into `.innerHTML =` (or a template string later assigned to
`.innerHTML`), not `.textContent`. Bank content — the item stem, option
text, WHY BEST/discriminator/second-best/trap text, the short-item model
answer and rubric points, DISTRACTOR ANALYSIS notes, and build steps — is
therefore inserted as raw HTML into the DOM.

This is two problems at once:

1. **Correctness for ordinary content.** Any stem containing `<` or `>` —
   entirely normal for a Math 1400 or CSCI 1100 item ("if `x < 5`", "a
   generic `List<T>`") — will be parsed as the start of an HTML tag and
   silently corrupt or truncate the rendered card. This will reproduce on
   the very first math item that compares two values.
2. **HTML/script injection.** Anything else that looks like a tag or an
   event-handler attribute in authored (or AI-generated — see
   `.claude/CLAUDE.md`'s "hosted models see item text" accepted risk) item
   text executes as markup/script in the quiz page, in both `itembank
   build`'s offline mode and `itembank serve`'s graded mode.

The codebase clearly knows the right pattern and applies it inconsistently:
`asAssign()`'s row text (`t.textContent = r.text`) and the per-option
distractor-analysis line (`r.textContent = line; // textContent, so a bank
cannot inject markup`, line ~289) both use `textContent` deliberately, with
a comment naming exactly this risk. The server-side Python half of the same
surface (`surfaces/quiz.py:page_for`) also escapes the page `<title>` with
`html.escape`. The stem/option/explanation paths in the client script are
the ones that were missed.

`tests/serve_roundtrip.py` and `tests/evidence_roundtrip.py::test_serve_writes_events`
both assert the served page never leaks an answer key, but neither asserts
anything about escaping, so this gap is untested.

**Fix:** Either switch every listed site to `textContent`/DOM node
construction, or implement a real escaper and use it everywhere `esc()` is
currently called:
```js
const esc = s => (s==null?"":String(s))
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
  .replace(/"/g,"&quot;").replace(/'/g,"&#39;");
```
Given most of the affected values are pure text (never actually need to
carry markup), building the fragments with `textContent`/`createElement`
instead of `innerHTML` template strings is the more robust fix and matches
the pattern already used for row text and the per-option rationale line.

## Warnings

### WR-01: `itembank migrate`'s idempotency depends on an 8 MiB tail window that does not scale with the guarantee it backs

**File:** `surfaces/migrate.py:401-402` (`seen = dict(evidence.recent_dedupe_keys(log))`), `evidence.py:45-53` (`DEDUPE_WINDOW_BYTES`), `evidence.py:206-254` (`recent_dedupe_keys`/`append_line_checked`)

**Issue:** `DEDUPE_WINDOW_BYTES`'s own comment justifies the 8 MiB bound by
reasoning that a `dedupe_key` "can only ever come from the same sitting, and
a sitting is at most a few hundred events." That reasoning is specific to
the live response path. `surfaces/migrate.py`'s whole selling point (D-13,
restated in its module docstring) is that "a second run imports nothing
new" falls out of this exact mechanism — but a migration's dedupe keys are
scoped to *source records*, not to one sitting, and `cmd_migrate` can
legitimately be re-run (per its own `--write`, re-runnable-by-design
contract) after the evidence log has grown well past 8 MiB from months of
ordinary live studying in between. Once the log's tail 8 MiB no longer
contains a previously-migrated record's `dedupe_key`, both `_check_or_write`'s
in-memory `seen` map and `evidence.append_event`'s own
`append_line_checked` tail scan will fail to see it, and a second `--write`
run will silently re-import it as a brand-new event — the exact regression
D-13 exists to prevent, in the one caller whose whole purpose is
re-runnability over the long term rather than one sitting.

`tests/evidence_roundtrip.py::test_migration_reconciliation` never grows the
log anywhere near 8 MiB between runs, so this path is untested.

**Fix:** Either widen the migration-specific dedupe check to scan the whole
log (migration is already a batch, offline operation, so the cost is
acceptable), or have `cmd_migrate` maintain its own persistent
`source_key -> event_id` index (e.g. a small sqlite side-table, mirroring
the disposable-index pattern already used for queries) that isn't bounded by
`DEDUPE_WINDOW_BYTES`.

---

### WR-02: Two distinct malformed/incomplete structured responses collapse into one dedupe bucket and the second is silently dropped

**File:** `runtime.py:91-99` (`canonical_response` returns `""` for a
malformed `table`/`dnd`/`build`/`mc` answer), `evidence.py:316-334`
(`idempotency_canon` passes that `""` straight through unchanged),
`evidence.py:427-460` (`attempt_number`, whose "same canonical -> same
attempt" check treats two different `""` canons as the same attempt)

**Issue:** `canonical_response()` intentionally returns `""` for a
partial/malformed structured answer ("a partial or padded assignment is not
a response"). `idempotency_canon()` does not special-case this the way it
special-cases `short`'s `None` — the empty string is used verbatim as
`canonical`, and therefore as an input to `dedupe_key()`. Two genuinely
different malformed answers to the same item in the same session (for
example a `table` response missing two different sets of rows, or a
non-JSON string passed to `--answer` for a structured item, twice, with
different text) both canonicalize to `""`, so `attempt_number()` treats the
second as a retry of the same attempt (`last.get("canonical") == canon` is
`"" == ""`), which reproduces the first submission's `dedupe_key`. The
second submission is reported `already_recorded` and its distinct raw
`answer` is never written to the log at all — an evidence-completeness gap,
reachable via `itembank submit --answer` (an agent or a slightly malformed
CLI invocation) more easily than via the browser, where the "Check" button
stays disabled until a structured response is complete.

Neither `tests/evidence_roundtrip.py::test_duplicate_submit_dedupes` nor any
other test exercises two different malformed answers to the same item.

**Fix:** Hash the raw (normalized) answer into the canonical form for the
empty-string case too, the same way `idempotency_canon` already does for
`short`:
```python
canon = canonical_response(q, answer)
if canon:
    return canon
text = json.dumps(normalize_answer(answer), sort_keys=True, default=str)
return "malformed:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
```
(Using `if canon:` rather than `if canon is not None:` routes both `None`
and `""` through a content-derived fallback, so two different malformed
answers no longer collide.)

---

### WR-03: `session.schema.json`'s `response_record` doesn't document `review_state`, and the two writers of a session's `responses` array disagree on whether it's present

**File:** `schemas/session.schema.json:59-87` (`$defs.response_record`
properties: `item_id`, `objective`, `type`, `answer`, `score`, `status` —
no `review_state`); `evidence.py:1294-1302` (`render_session_json` adds
`"review_state": review_state` to every response record); `surfaces/session.py:106-108`
(`cmd_submit` appends a response record with only `item_id`, `objective`,
`type`, `answer`, `score`, `status` — no `review_state`)

**Issue:** A session's `responses` array is meant to be one logical shape,
written live by `cmd_submit` and reconstructable by
`evidence.render_session_json()` (the latter's own docstring says it
"reconstruct[s] the session dict shape `surfaces/session.py` writes"). In
practice the two disagree: the reconstructed view always carries
`review_state` (`"n/a"`/`"pending"`/`"marked"`), while the live session file
`cmd_submit` writes never does. Since `response_record` has no
`additionalProperties: false`, this doesn't fail the validator (confirmed —
`test_renders_match_log` validates the rendered shape and passes), but it
means a consumer of a live session file and a consumer of a recovered one
see structurally different records for what the runtime documents as the
same contract, and the published schema documents neither behavior.

**Fix:** Either have `cmd_submit` also record `review_state` on every
response (computed the same way `render_session_json` does, via
`marks_by_event`) so the two writers agree, or drop it from
`render_session_json`'s output and surface it only through
`evidence.session_events`/`objective_history` where it already lives on the
raw event. Whichever is chosen, add `review_state` to
`response_record`'s `properties` in `session.schema.json` so the contract
states which is true.

---

### WR-04: `itembank day --date` is not validated before use, and a malformed value crashes instead of exiting cleanly

**File:** `surfaces/day.py:832`

**Issue:**
```python
today = date.fromisoformat(a.date) if a.date else date.today()
```
Every other date-shaped input in this codebase is validated with a clear
error before use (`day_tick_event()` raises a named `ValueError` for a bad
date; `parse_lanes()` reports a malformed fuse date as a lint line rather
than crashing). `--date` is the one exception: a malformed value (wrong
format, or a syntactically valid-looking but non-existent date) raises an
unhandled `ValueError` from `date.fromisoformat`, producing a raw Python
traceback instead of the house-style `sys.exit("...")` every other command
in `surfaces/cli.py` uses for bad input.

**Fix:**
```python
try:
    today = date.fromisoformat(a.date) if a.date else date.today()
except ValueError:
    sys.exit("day: --date must be YYYY-MM-DD, got %r" % (a.date,))
```

## Info

### IN-01: `write_day_log()` and `evidence.render_daily_log()` duplicate the same markdown-table-building logic

**File:** `surfaces/day.py:476-499` (`write_day_log`), `evidence.py:1397-1422`
(`render_daily_log`)

**Issue:** Both functions build byte-identical `daily_log.md` output from a
`{iso_date: set_of_lanes}` mapping, using near-identical list-building code.
This is a deliberate, documented fallback (`write_day_log`'s docstring:
"Kept as the fallback writer for the pre-migration path only") and is
guarded by `tests/evidence_roundtrip.py::test_day_ticks_are_events`
asserting the two outputs stay byte-identical, so it is not a silent-drift
risk today. Flagging only because it is duplicated logic per the review
scope's priority 5 — a future edit to one (e.g. adding a lane, changing the
floor explanation wording) that isn't mirrored to the other will only be
caught by that one pinning test, not by the type system or a shared helper.

**Fix:** Consider having `write_day_log()` call
`evidence.render_daily_log()` internally and just write the result, so
there is one generator of the table and one atomic-write wrapper, rather
than two generators kept in sync by a test.

### IN-02: `Q.sort(()=>Math.random()-0.5)` is a biased shuffle

**File:** `surfaces/quiz_page.py:491`

**Issue:** `Array.prototype.sort` with a random comparator is a well-known
non-uniform shuffle (its bias depends on the engine's sort implementation,
typically over- or under-representing certain permutations, especially for
small arrays). This affects only the top-level item order within one
sitting, not scoring or answer-position balance (which the per-item
`shuffled()` Fisher-Yates helper already handles correctly), so the impact
is cosmetic rather than a correctness issue.

**Fix:** Reuse the existing Fisher-Yates `shuffled()` helper for `Q` too:
`Q = shuffled(Q);` before the first `render()` call.

---

_Reviewed: 2026-08-06_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
