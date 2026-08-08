# Phase 7: Selection Engine - Research

**Researched:** 2026-08-08
**Domain:** Deterministic, rule-based item selection over an append-only evidence log (no third-party libraries; stdlib only)
**Confidence:** HIGH

## Summary

This phase has almost no external-library surface — it is stdlib-only by hard
constraint, and every requirement (SEL-01..SEL-05) is satisfiable by composing
code that already exists in `model.py`, `runtime.py`, and `evidence.py`. The
research effort here is therefore concentrated on the *codebase itself*: what
`surfaces/session.py:do_start()` currently does and must stop doing, what
`evidence.py` already exposes for exposure history versus what it is missing,
where `model.py`'s stem-terminator regex will silently eat a new `[PAIR:]`
tag if it is not added to the same alternation, and where a hardcoded test
assertion (`tests/daemon_roundtrip.py:616-624`, `check_api_route_scope`)
constrains how the daemon route can grow.

Three findings materially change how the planner should scope work.
First, `evidence.py`'s disposable sqlite3 index (`_create_index_schema`,
`evidence.py:705-726`) has **no `bank` column**, so a caller cannot cheaply
answer "the last N responses in *this* bank" through the fast indexed path
today — only through `subject` (which the index already carries) or a full
linear scan. Second, `schemas/session.schema.json:41-44` and
`surfaces/daemon.py:670` already enumerate a **feedback**-mode value set of
`("diagnostic", "practice", "exam", "remediation", "drill")` — four of D-06's
four selection-mode names are already live, in the wrong axis, in a published
schema and a daemon constant. D-06's naming hazard is not hypothetical; it is
already partially collided in shipped code. Third, `SEL-01`'s "prerequisite"
filter has **no backing field anywhere** in `model.py`, `schemas/item.schema.json`,
or `07-CONTEXT.md`'s D-01..D-10 — it is the one requirement this phase must
satisfy with a mechanism that does not yet exist in any form, additive tag or
otherwise, and 07-CONTEXT.md is silent on it.

**Primary recommendation:** Build `selection.py` as a pure `select(questions,
spec, history) -> (items, trace)` function per D-01, with a mode table
(`MODES = {name: (filter_fn, order_fn, count_policy)}`) rather than four
branches; extend `evidence.py`'s index with a `bank` column (or accept
subject-scoped cooldown as the pragmatic zero-schema-change default) for
D-08's history read; add `[PAIR:]` to `model.py`'s stem-terminator alternation
*before* adding a `pair` field to the parsed dict; extend `/api/start`'s
request/response shape rather than adding `/api/select` (the hardcoded
4-route test assertion makes a new route a two-file change, not a one-file
change); and treat "prerequisite" as an explicit open decision the planner
must resolve, because no prior art for it exists in this codebase.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Item selection (`select()`) | Runtime (peer module `selection.py`) | — | D-01: pure function, no file I/O, no surface import — same tier as `runtime.py`/`evidence.py` |
| Selection spec expansion (profiles → dict) | Runtime/Settings boundary | Surfaces (CLI/daemon build the raw dict) | D-02: one expansion function, called by every surface, never duplicated per-surface |
| Exposure history read (cooldown, hard/soft) | Runtime (`evidence.py`) | Runtime (disposable sqlite3 index as fast path) | D-08/D-09: `select()` never opens a file; its caller (session.py/daemon.py) reads history via `evidence.objective_history()` and passes it in |
| Trace / explainability | Runtime (`selection.py`, returned alongside items) | CLI (`itembank select --explain` renders it) | D-04/D-05: no second derivation pass; the trace is a return value, plain-text rendering is a surface concern |
| `[PAIR:]` parsing and `item.pair_singleton` lint | Model (`model.py`) | — | Identity/format-contract tier; consistent with `[ID:]`/`[HASH:]` precedent (D-07) |
| CLI surface (`itembank start`, `itembank select`) | Surfaces (`surfaces/cli.py`, `surfaces/session.py`) | — | SURF-04: every capability has a CLI twin |
| Daemon surface (`/api/start` extended) | Surfaces (`surfaces/daemon.py`) | — | Same runtime call as the CLI; `SystemExit`-contained per Phase 2 convention |
| Settings (`selection.profiles`, `selection.cooldown_responses`) | Settings (`surfaces/settings.py`, `schemas/settings.schema.json`) | Runtime (the expansion function reads it) | D-02: profiles live in settings, expanded by one function shared by every surface |

## Standard Stack

**No third-party dependency applies to this phase** — explicitly out of scope
per the phase brief and per `.claude/CLAUDE.md`'s "Python standard library
only, no install step" constraint. There is no npm/pip/cargo ecosystem check
to run: the only "stack" here is which stdlib modules this phase's new code
uses, verified against `import` statements already present in peer modules.

### Core (stdlib only)

| Module | Purpose | Why Standard |
|--------|---------|---------------|
| `random` | `random.Random(seed)` deterministic shuffling for tie-breaking within an ordering | Already the codebase's determinism idiom — `surfaces/session.py:71` (`do_start`'s `rng.shuffle`) and `runtime.py:43` (`public_item`'s `build` shuffle) both use it; D-10 requires reusing it, not inventing a second one |
| `sqlite3` | Disposable, lazily-imported query cache over the evidence log | Already established in `evidence.py:700-702` (`_index_connect`), imported lazily inside functions so a Python build without `sqlite3` still runs the linear-scan fallback |
| `collections` | `namedtuple`/`Counter`/`defaultdict` for trace records and mode compositions | Already the pattern for `model.LintError` (a `namedtuple`, `model.py:373-382`) |
| `json` | Selection spec / trace serialization for CLI and `/api/*` | Every existing surface does this identically |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A published `schemas/selection.schema.json` (D-02's discretion point) | Document the spec dict in `model.SPEC`-style prose only | A sixth schema costs one more file and one more `CONTRACTS` tuple entry in `surfaces/protocol_cli.py:23-29`/`38-63`, but every other request/response shape in this codebase (item, session, response, report, lint_error) already has one; a request shape with no schema is the outlier, not the norm. Recommend publishing it — see Open Questions for the concrete cost. |
| A new `/api/select` daemon route | Extend `/api/start`'s request/response shape | `tests/daemon_roundtrip.py:616-624` (`check_api_route_scope`) hardcodes `len(daemon.API_ROUTES) != 4` and fails the build otherwise. A new route is a real, if small, breaking change to a load-bearing test's own stated scope ("D-04 scopes /api/* to exactly four routes **this phase**" — the docstring already anticipates growth in a *later* phase, not this one). Extending `/api/start` avoids touching that assertion at all. |
| A bank-scoped exposure index column | Subject-scoped cooldown using the index's existing `subject` column | Adding a `bank` column to the sqlite3 projection (`evidence.py:705-726`) requires bumping `INDEX_VERSION` (forces one full rebuild — cheap, since D-08 says the index is disposable) and touching `_insert_response_row`, `event_matches`, `objective_history`, and both its indexed/fallback halves. Subject-scoping needs zero schema changes today. Recommend stating the tradeoff to the planner rather than silently picking one — see Open Questions. |

**Installation:** None. No `pip install`, no `package.json`, no lockfile change for this phase.

## Package Legitimacy Audit

**Not applicable.** This phase installs no external packages of any kind —
stdlib only, per `.claude/CLAUDE.md`'s "Technology Stack" section and per the
research emphasis's explicit instruction ("Do NOT propose any third-party
dependency"). No package-legitimacy check was run because there is nothing to
check.

## Architecture Patterns

### System Architecture Diagram

```text
                    itembank start / itembank select      /api/start (extended)
                              |                                     |
                              v                                     v
                     +-------------------+               +-------------------+
                     |  surfaces/session |               | surfaces/daemon   |
                     |  .py: do_start()  |               | .py: handle_api_  |
                     |  (spec assembly)  |               | start()           |
                     +---------+---------+               +---------+---------+
                               |                                    |
                               +---------------+--------------------+
                                               v
                                   +----------------------+
                                   |  selection.py (NEW)  |
                                   |  select(questions,   |
                                   |   spec, history)     |
                                   |  -> (items, trace)   |
                                   +----+-------------+---+
                                        |             |
                     reads (arg, no I/O)|             | pure filter/order/
                                        |             | count-policy logic
                     +------------------+             | (mode table, D-06)
                     |                                v
                     |                     +----------------------+
                     |                     |  MODES table:        |
                     |                     |  diagnostic/practice/|
                     |                     |  remediation/exam    |
                     |                     +----------------------+
                     v
        +---------------------------+
        | evidence.objective_history|  <-- caller reads history BEFORE
        | () / a new bank-aware     |      calling select(); D-09: select()
        | query (D-08's hard/soft   |      never opens the log itself
        | exposure split)           |
        +-------------+-------------+
                       |
             indexed (fast) or linear-scan (fallback, degrade-never-block)
                       v
        +---------------------------+
        | _evidence/evidence.jsonl  |  <-- Phase 1's append-only log,
        | + evidence_index.sqlite3  |      the only authority (D-08)
        +---------------------------+

  selected items + trace
        |
        v
  write_session() (session.py, unchanged) --> session JSON carries the spec (D-03)
```

A reader tracing SEL-01 through SEL-05: a spec dict enters through the CLI or
`/api/start`; the caller resolves it against a settings profile if named
(D-02); the caller reads the evidence snapshot (D-09) and calls
`selection.select(qs, spec, history)`; `select()` looks up `spec["mode"]` in
the mode table, applies that mode's filter/order/count-policy functions
(D-06), and returns `(items, trace)`; the caller writes the session (spec and
snapshot marker included, per D-03) and hands the trace to whichever surface
asked for it (D-04).

### Recommended Project Structure

```
selection.py                    # NEW — peer of model.py/runtime.py/evidence.py
  select(questions, spec, history) -> (items, trace)
  MODES = {...}                 # mode -> (filter_fn, order_fn, count_policy)
  expand_profile(settings, spec)  # D-02's one expansion function
  render_trace(trace)           # plain-text rendering for --explain

model.py                        # EXTENDED
  parse_question(): + "pair" field, TERMINATOR alternation + [PAIR
  lint(): + item.pair_singleton check
  LINT_CODES: + "item.pair_singleton"

evidence.py                     # EXTENDED (if bank-scoped cooldown is chosen)
  _create_index_schema(): + bank column, INDEX_VERSION bump
  event_matches(), objective_history(): + bank= parameter

surfaces/session.py             # EXTENDED
  do_start(): candidates/shuffle/clamp DELETED, replaced by a selection.select() call
  new fields on the written session dict: spec (D-03), evidence snapshot marker

surfaces/cli.py                 # EXTENDED
  `start` parser: + --prerequisite/--type/--difficulty/--exclude/--pair flags
  NEW `select` subcommand: --explain, mirrors `start`'s filters, does not write a session

surfaces/daemon.py              # EXTENDED
  handle_api_start(): + full spec fields, + trace in response when requested
  (no new route — see Alternatives Considered)

surfaces/settings.py            # EXTENDED
  no code change needed beyond what load_settings()/schema_for_key() already do generically

schemas/settings.schema.json    # EXTENDED
  + "selection" top-level group: profiles, cooldown_responses, recency-penalty knob

schemas/session.schema.json     # EXTENDED
  + "selection_spec" field (D-03) on the session document

schemas/selection.schema.json   # NEW, if D-02's discretion resolves to "publish it"

tests/selection_roundtrip.py    # NEW
```

### Pattern 1: One selector, mode table over four branches

**What:** `select()` is one function; the four modes are entries in a dict
mapping mode name to `(filter_fn, order_fn, count_policy)`, not four
`if mode == "diagnostic": ...` branches.

**When to use:** Any time a set of named variants shares the same pipeline
shape (filter, then order, then take N) and differs only in which functions
plug into each stage — which is exactly D-06's own framing ("named
compositions of the same primitive filters, not four code paths").

**Example (illustrative shape, not verified against any external source —
this composes ONLY primitives already verified in this codebase):**
```python
# selection.py — illustrative shape; every primitive named below is a
# real, already-existing capability in this codebase (model.py's
# `objective`/`difficulty`/`type` fields, evidence.py's item-identity
# scheme), not a speculative API.

def _filter_by_spec(qs, spec, hard_excluded):
    out = []
    for q in qs:
        if spec.get("objective") and q.get("objective") != spec["objective"]:
            continue
        if spec.get("type") and q.get("type") != spec["type"]:
            continue
        if spec.get("difficulty") and q.get("difficulty") != spec["difficulty"]:
            continue
        key = evidence.evidence_key(q)   # same key evidence.py already uses
        if key in hard_excluded:
            continue
        out.append(q)
    return out

DIFFICULTY_ORDER = {"recall": 0, "application": 1, "analysis": 2}

def _diagnostic_order(qs, soft_penalty):
    # ascending difficulty; unknown/empty difficulty sorts last, not first,
    # since model.py's difficulty field is free text with no lint-enforced
    # enum (model.py:53) — an unlabeled item must not silently sort as
    # "easiest".
    return sorted(qs, key=lambda q: DIFFICULTY_ORDER.get(q.get("difficulty"), 99))

MODES = {
    "diagnostic": {
        "filter": lambda qs, spec, hard, soft: _one_per_objective(_filter_by_spec(qs, spec, hard)),
        "order": _diagnostic_order,
        "count_policy": "exact",     # cooldown ignored (D-06)
    },
    # practice / remediation / exam entries follow the same three-key shape
}
```

### Pattern 2: History as an argument, never a file the selector opens

**What:** `select(questions, spec, history)` — `history` is data the *caller*
already read, not a path `select()` resolves itself.

**When to use:** Every call. This is D-09, and it mirrors the existing
`score_response(q, answer)` shape (`runtime.py:120-130`) exactly: no hidden
file I/O inside the pure function, so a unit test can construct a synthetic
`history` list without touching disk (needed for the D-10 determinism test).

**Example (verified pattern — `score_response` itself):**
```python
# runtime.py:120-130 — VERIFIED, read this session
def score_response(q, answer):
    """The only scorer. Every surface reaches a verdict through this function.

    Constructed response returns None rather than False: not-yet-marked and
    marked-wrong are different states, and collapsing them would let a pending
    item read as a failure in the evidence.
    """
    key = canonical_key(q)
    if key is None:
        return None
    return canonical_response(q, answer) == key
```
`select()` should read the same way: everything it needs arrives as an
argument, and the caller (`surfaces/session.py:do_start`, or the daemon
equivalent) is where `evidence.objective_history(log, ...)` actually runs.

### Pattern 3: Identifier-addressed exclusion, never index-addressed

**What:** `exclude_item_ids` (D-02) and the hard-exclusion set (D-08) are
built from `evidence.evidence_key(q)` — `q["item_id"]` when assigned, else
`"ref:" + q["id"]` as the pre-id-assign fallback (`evidence.py:317-325`,
verified) — never from a bank's positional item number.

**Why:** `01-CONTEXT.md` D-05 established that item numbers move when a bank
is edited; `evidence.py` already built the one function that resolves an
item to its evidence identity, and `selection.py` must call that same
function rather than re-deriving the same logic a second time. Two
independent derivations of "what identifies this item" is exactly the
one-of-each-thing violation `PROJECT.md`'s core value forbids.

### Anti-Patterns to Avoid

- **Re-deriving the exposure key instead of calling `evidence.evidence_key(q)`:**
  a second, slightly different key-derivation function is how a hard
  exclusion silently stops matching a soft-penalty read for the same item.
- **Branching on mode name in four separate functions:** defeats the
  explicit "one table of compositions, not four code paths" instruction in
  D-06 and makes SEL-02's "visibly different composition" untestable as one
  data structure.
- **A second, ad-hoc history reader that bypasses `live_events`/`objective_history`:**
  D-10 (evidence retraction semantics) is already implemented once in
  `evidence.py`; a selector-local reader that reads `events()` directly
  instead of `live_events()` would let a retracted response still count
  against cooldown.
- **Adding `/api/select` without updating `check_api_route_scope`:** breaks
  CI silently late in the plan if the planner has not read
  `tests/daemon_roundtrip.py:616-624` first.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Determining what identifies an item for exclusion/exposure | A second "item key" function inside `selection.py` | `evidence.evidence_key(q)` (`evidence.py:317-325`) | Already the one function every evidence read/write agrees on; a second derivation risks silent drift between what `select()` excludes and what the log actually recorded |
| Reading "how has this objective performed" | A hand-rolled JSONL scan inside `selection.py` | `evidence.objective_history(log, objective, ...)` (`evidence.py:613-650`) — already implements the indexed/fallback degrade-never-block split | This is literally D-08's own seam; re-implementing it duplicates the retraction-aware (`live_events`) read path and risks missing a retraction |
| Canonicalizing a response for idempotency-adjacent comparisons | A new normalizer in `selection.py` | `runtime.canonical_response()` / `evidence.idempotency_canon()` if ever needed | One canonical-form function already exists project-wide; selection has no reason to need its own, but if it ever needs to compare an answer it must call these, not write a third |
| A JSON Schema validator for the new `selection.schema.json` (if published) | A second validator, or a permissive draft-2020-12 library | `schema_validate.validate()` (`schema_validate.py`) — the one hand-rolled subset validator this project already ships | `schema_validate.py`'s own docstring: "There is no JSON Schema implementation in the Python standard library... this is a subset validator scoped to the exact keywords the documents under `schemas/` use." Any new schema file must stay inside `SUPPORTED` (`schema_validate.py:23-26`): `type`, `properties`, `required`, `additionalProperties`, `enum`, `const`, `items`, `minItems`, `minLength`, `minimum`, `maximum`, `$defs`, `$ref`, `oneOf`. No `patternProperties`, no `allOf`, no `anyOf` — `check_schema()` raises `SchemaError` on anything outside that set (`schema_validate.py:45-91`, verified) |

**Key insight:** every "don't hand-roll" item in this phase is really the
same insight restated five times: this codebase already has one scorer, one
parser, one evidence writer, and one schema validator, and `selection.py`'s
entire job is to be the *sixth* "one of a thing" without becoming a second
copy of any of the other five.

## Runtime State Inventory

**Not applicable — this is not a rename/refactor/migration phase.** This
phase adds a new module and extends existing ones; it does not rename any
existing string, key, or identifier that external state (databases, OS
registrations, secrets) already depends on. Skipped per the trigger
condition in the research protocol.

## Common Pitfalls

### Pitfall 1: `[PAIR:]` swallowed into the stem if the terminator alternation is not updated first

**What goes wrong:** If an author places `[PAIR: <name>]` before any of the
markers `model.py`'s stem-grab regex already recognizes, the entire
`[PAIR: ...]` line is captured as part of the item's *stem* text instead of
being parsed as a separate field.

**Why it happens:** `model.py:43-47` (verified, quoted exactly):
```
    stem = grab(
        r"Q\d+\.\s*(.*?)\s*(?:\(difficulty:|\n\[OBJECTIVE|\n\[TYPE|\n\[SELECT"
        r"|\n\[CATEGORIES|\n\[ID|\n\[HASH|\n[A-H]\)|\nROW\)|\nITEM\)|\nSTEP\)"
        r"|\nMODEL:|\nRUBRIC:|\nWHY BEST:)",
        ch, re.S)
```
This is a non-greedy capture up to the **first** occurrence of any listed
terminator. `\n\[PAIR` is not in that alternation. Since `[ID:]`/`[HASH:]`
are typically authored immediately after the stem line (see
`fixtures/sample_bank.md` lines 8-11, where `[ID:]` and `[HASH:]` sit
directly under the `Qn.` line, before `[OBJECTIVE:]`), a `[PAIR:]` tag placed
in that same early cluster — the natural place an author would put it — is
the exact scenario that breaks.

**How to avoid:** Add `|\n\[PAIR` to the alternation at `model.py:43-47`
*before* wiring `[PAIR:]` parsing into the `common` dict. Confirmed this is
the only regex requiring the change — `model.py:191-193`'s `TERMINATOR`
(used by `assign_ids()` to find where to *insert* a missing `[ID:]`/`[HASH:]`
line) does not need a `[PAIR:` entry, because `[PAIR:]` is never an
insertion target for that function; a `[PAIR:]` line sitting before the
`TERMINATOR` match is simply inert text `assign_ids()` passes through
unchanged.

**Warning signs:** A bank with `[PAIR:]` tags parses with a stem string that
visibly contains the literal text `[PAIR: ...]`, or `q["pair"]` is empty
even though the source markdown clearly has the tag.

### Pitfall 2: `conf` is CONFIDENCE, not a confusion set — confirmed, not overturned

**Finding confirmed as stated in `07-CONTEXT.md` D-07.** `model.py:61`
(verified, quoted exactly):
```
"conf": grab(r"(?m)^CONFIDENCE:\s*(.*?)\s*(?=\n|\Z)", ch),
```
This parses the `CONFIDENCE: high|medium|low` line — the author's stated
confidence in the item (used by `lint()`'s `item.low_confidence` check,
`model.py:538-540`). There is no field anywhere in `model.py`'s `common`
dict, and no grep hit for "pair" or "confusion" in `model.py`,
`schemas/item.schema.json`, or `07-DISCUSSION-LOG.md`'s alternatives list
other than the discussion of this exact tradeoff. D-07's conclusion —
a new `[PAIR:]` tag is required, the shortcut does not exist — is correct.
Nothing here needs to be said loudly as *wrong*; it is confirmed as *right*.

### Pitfall 3: `session.mode` already collides with D-06's selection-mode vocabulary in shipped code, not just in the requirement text

**What goes wrong:** Treating D-06's naming hazard as a future risk rather
than an already-partially-realized one.

**Why it happens:** The *feedback*-mode enum is not confined to
MODE-01..06's four named modes (drill/practice/diagnostic/exam per
`REQUIREMENTS.md` lines 51-54). It is already five values wide in shipped
code, and it already includes `"remediation"` — one of D-06's own four
selection-mode names. Verified in three places:

- `schemas/session.schema.json:41-44` (verified, quoted exactly):
  ```
  "mode": {
    "type": "string",
    "enum": ["diagnostic", "practice", "exam", "remediation", "drill"]
  },
  ```
- `schemas/response.schema.json:59-62` (verified, quoted exactly):
  ```
  "mode": {
    "type": "string",
    "enum": ["diagnostic", "practice", "exam", "remediation", "drill", "legacy"],
    "description": "Captured live on every surface; this is what makes a drill-mode correct distinguishable from an exam-mode correct. ..."
  },
  ```
- `surfaces/daemon.py:670` (verified, quoted exactly):
  ```python
  SESSION_MODES = ("diagnostic", "practice", "exam", "remediation", "drill")
  ```

Three of the four *feedback*-mode enum values already spelled out in
published schemas (`diagnostic`, `practice`, `exam`) are also three of D-06's
four *selection*-mode names verbatim, and the fourth feedback value,
`remediation`, is literally D-06's fourth selection-mode name too — despite
`REQUIREMENTS.md`'s MODE-01..06 only ever describing four feedback modes
(drill/practice/diagnostic/exam), `remediation` is already sitting in the
shipped feedback-mode enum with no MODE-0x requirement backing it. This is
either a forward-looking placeholder someone already added, or a pre-existing
conflation the planner is inheriting.

**How to avoid:** This is exactly the decision D-06 flags for the planner
("Pick one of: a distinct field name (`selection_mode`), or a documented
rule that the two are set together. Do not let them silently alias.") — but
the planner should resolve it knowing the collision is not hypothetical.
Given `remediation` already exists in the feedback-mode enum with no
requirement driving it, the safer resolution is a **distinct
`selection_mode` field** on the spec/session, leaving `mode` exclusively the
feedback-policy field it already is everywhere in shipped code, and treating
the existing presence of `"remediation"` in `SESSION_MODES` as either dead
value (never reachable until Phase 6 wires MODE-01..06 into `do_submit`) or
a decision to retroactively question — but not a reason to reuse `mode` for
both axes.

**Warning signs:** A session or evidence event where `mode="remediation"`
is ambiguous about whether that names the feedback policy or the selection
composition without a second field to disambiguate.

### Pitfall 4: The disposable sqlite3 index has no `bank` column, so "last N responses in this bank" is not cheaply answerable today

**What goes wrong:** Assuming `evidence.objective_history()` can filter by
bank because it filters by so much else.

**Why it happens:** `evidence.py:705-726` (verified, quoted exactly — the
full projected schema):
```python
def _create_index_schema(con):
    con.execute("""CREATE TABLE events (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE,
        ts TEXT,
        session_id TEXT,
        item_id TEXT,
        item_ref TEXT,
        objective TEXT,
        subject TEXT,
        mode TEXT,
        item_type TEXT,
        score TEXT,
        attempt_number INTEGER,
        confidence TEXT,
        response_time_ms INTEGER,
        review_state TEXT,
        retracted INTEGER DEFAULT 0)""")
    con.execute("CREATE INDEX idx_objective ON events(objective, ts)")
    con.execute("CREATE INDEX idx_subject ON events(subject, ts)")
    con.execute("CREATE INDEX idx_session ON events(session_id, ts)")
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
```
There is no `bank` column and no `idx_bank` index. `event_matches()`
(`evidence.py:484-515`, verified) likewise has no `bank` parameter — its
filterable fields are `objective`/`prefix`/`subject`/`mode`/`session_id`/`since`
only. `_insert_response_row()` (`evidence.py:729-746`) does not project
`ev.get("bank")` into the table at all, even though every response event
carries a `bank` field (`response.schema.json:48-51`).

**How to avoid:** Two honest paths, both viable, neither free:
1. **Subject-scoped cooldown (zero schema change):** call
   `evidence.objective_history(log, objective=None, subject=subject_of(spec_objective))`
   and take the tail — works today, at the cost of treating "last N
   responses" as "last N responses in this *subject*" rather than "in this
   *bank*" (multiple banks under one subject would share one cooldown
   window).
2. **Bank-scoped cooldown (schema change):** add a `bank TEXT` column and
   `idx_bank` index to `_create_index_schema`, bump `INDEX_VERSION` from `1`
   to `2` (forces one full rebuild on next `ensure_index()` call — cheap,
   the index is disposable per D-08), add `bank=` to `event_matches()`,
   `_insert_response_row()`, `_objective_history_indexed()`,
   `_objective_history_fallback()`, and `objective_history()`'s signature.
   This is a real, if contained, change to a Phase-1-owned module from a
   Phase-7 plan — legitimate, since `evidence.py`'s own docstring says "the
   one append-only store every later plan writes into and reads from," but
   it should be called out as its own task, not folded silently into
   `selection.py`'s work.

State which path the plan takes; do not leave it implicit. See Open
Questions.

### Pitfall 5: `difficulty` is free text with no enforced enum — ordering by it needs an explicit, defensive ordinal map

**What goes wrong:** Sorting items by `q["difficulty"]` as a string, or
assuming every item has one of exactly three values.

**Why it happens:** `model.py:53` (verified): `"difficulty": grab(r"\(difficulty:\s*([^)]+)\)", ch),`
— captured as free text from an optional `(difficulty: ...)` annotation.
`model.SPEC` (`model.py:290`, verified) documents the convention
`recall|application|analysis`, but `lint()` (`model.py:403-559`, read in
full) never validates `difficulty` against that set — there is no
`item.invalid_difficulty` or similar code in `LINT_CODES`
(`model.py:389-400`, verified — the tuple has no such entry). An item with
no `(difficulty: ...)` annotation at all parses with `difficulty == ""`.

**How to avoid:** `selection.py`'s difficulty-ordering functions (diagnostic
mode's "difficulty ascending", exam mode's "difficulty-balanced") need an
explicit ordinal map (e.g. `{"recall": 0, "application": 1, "analysis": 2}`)
with a defined, stated fallback for an unknown or empty value — sorting it
last rather than first, so an unlabeled item is never silently treated as
"easiest."

**Warning signs:** A diagnostic-mode session that puts every item with no
`(difficulty: ...)` line first, or a test that asserts difficulty-ascending
ordering without a fixture item that has no difficulty at all.

### Pitfall 6: `fixtures/sample_bank.md` is too small and unnamespaced to exercise this phase's own tests

**What goes wrong:** Writing `tests/selection_roundtrip.py` against the
existing fixture bank and discovering the four-mode composition test, the
cooldown test, and the pair test all starve or degenerate.

**Why it happens (verified by reading the fixture in full):** `fixtures/sample_bank.md`
has exactly 6 items, one per item type, each with a *different* objective
string (`Distribution / residual maintenance`, `Public notification`,
`Operations`, `Treatment processes`, `Regulatory framework` twice). None of
the objective strings are namespaced (`subject:path`) — every one would
trigger `lint()`'s `item.objective_unnamespaced` warning
(`model.py:451-456`). With 6 items and D-08's proposed default
`cooldown_responses` of 20, any session of more than 6 responses against
this bank exhausts every item and enters the "small bank" starvation case
07-CONTEXT.md's own discretion note already anticipates ("If the fixture
banks are small enough that 20 starves practice mode, pick a fraction of
bank size and say why" — confirmed true for this exact fixture). No item in
the fixture carries a `[PAIR:]` tag (none exists in the format yet), and no
two items share an objective in a way that supports "at most one item per
objective" (diagnostic mode) being meaningfully different from "all items"
at this bank's size.

**How to avoid:** Either extend `fixtures/sample_bank.md` with more items
per objective (namespaced, e.g. `water:distribution.residual`), explicit
difficulty spread, and at least one `[PAIR:]`-tagged confusion pair, or add
a second, larger synthetic fixture bank dedicated to selection tests. This
belongs in the plan's Wave 0 (test-infrastructure) gap, not discovered
mid-implementation.

## Code Examples

### Verified: the exclusion/identity key every consumer must share

```python
# evidence.py:317-325 — VERIFIED, read this session
def evidence_key(q):
    """The key a response event is recorded and deduplicated against.

    `q["item_id"]` when one has been assigned (plan 01-04), else a positional
    fallback so the key stays deterministic before any item carries a real
    id. Used identically by `response_event()` and by a caller computing the
    attempt number ahead of building an event, so the two never drift apart.
    """
    return q.get("item_id") or ("ref:" + q["id"])
```
`selection.py`'s hard-exclusion set and `exclude_item_ids` matching must
build/compare against this exact function's output, not a re-derivation.

### Verified: the degrade-never-block query seam `select()`'s caller should use

```python
# evidence.py:613-650 — VERIFIED, read this session (docstring elided to the
# load-bearing lines; full text confirmed present in evidence.py)
def objective_history(log, objective, prefix=False, subject=None, mode=None,
                       session_id=None, since=None):
    index = index_for_log(log)
    status = ensure_index(log, index)
    if status == "used":
        try:
            return _objective_history_indexed(
                index, objective, prefix, subject, mode, session_id, since)
        except Exception as exc:
            print("warn  evidence index unavailable (%s); falling back to a "
                  "full log scan" % exc)
            try:
                if os.path.exists(index):
                    os.remove(index)
            except Exception:
                pass
    return _objective_history_fallback(
        log, objective, prefix, subject, mode, session_id, since)
```
This is D-08/D-09's honest degradation path in full: index used when fresh,
rebuilt or extended when stale (`ensure_index`, `evidence.py:888-940`), and a
full linear scan through `live_events()` when the index cannot be built at
all — never an error, never a block. `selection.py`'s caller (not
`selection.py` itself, per D-09) is the one place this should be called.

### Verified: what `do_start()` deletes, exactly

```python
# surfaces/session.py:54-84 — VERIFIED, read this session (full function)
def do_start(bank_path, count, objective, mode, seed, out, force):
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        sys.exit("count must be a positive integer, got %r" % (count,))
    qs = load(bank_path)
    errors, _ = lint(qs)
    if errors and not force:
        sys.exit("refusing to start a bank with errors; run lint or pass --force")
    import random, uuid
    candidates = [i for i, q in enumerate(qs) if not objective or q.get("objective") == objective]
    if not candidates:
        sys.exit("no items match objective %r" % objective)
    rng = random.Random(seed)
    rng.shuffle(candidates)
    items = candidates[:min(count, len(candidates))]
    out = out or os.path.join(os.path.dirname(os.path.abspath(bank_path)) or ".", "_attempts",
                              "session_%s.json" % uuid.uuid4().hex[:12])
    data = {"schema_version": SESSION_VERSION, "session_id": uuid.uuid4().hex,
            "bank": os.path.abspath(bank_path), "items": items, "cursor": 0,
            "responses": [], "status": "active", "mode": mode,
            "objective": objective or "", "seed": seed,
            "served_ts": evidence.utc_now()}
    write_session(out, data)
    result = session_view(data, qs)
    result["session_file"] = session_path(out)
    return result
```
**What moves into `selection.py`:** the `candidates` list-comprehension
(objective filter — becomes one primitive filter among several), the
`rng.shuffle(candidates)` call (becomes the mode table's `order` function for
whichever mode wants pure shuffle — none of D-06's four modes actually want
plain shuffle, so this exact line has no direct successor and is genuinely
replaced, not ported), and the `items = candidates[:min(count, len(candidates))]`
clamp (becomes the mode table's `count_policy`). **What is deleted outright:**
the count<1 guard's comment explains a real Python gotcha (negative slice
stop) — 07-CONTEXT.md's canonical_refs already flags this comment as
something that "moves with the code," so it must be preserved verbatim in
`selection.py` or wherever the guard lands, not silently dropped.
**What breaks:** every direct caller of `do_start()` — verified as exactly
two call sites: `surfaces/cli.py`'s `cmd_start` (via `s.set_defaults(fn=cmd_start)`,
`cli.py:174`) and `surfaces/daemon.py`'s `handle_api_start`
(`daemon.py:806`: `result = session.do_start(path, count, objective, mode, seed, out, False)`).
Both call sites' argument lists must grow to carry the fuller spec (D-02),
which is itself a breaking signature change to `do_start()` — the plan should
treat updating both call sites as one atomic task, not two.

### Verified: the hardcoded test constraint on the daemon's API surface

```python
# tests/daemon_roundtrip.py:616-624 — VERIFIED, read this session
def check_api_route_scope():
    """D-04 scopes `/api/*` to exactly four routes this phase, and the count
    is asserted rather than trusted.
    """
    if len(daemon.API_ROUTES) != 4:
        fail("D-04 scopes /api/* to exactly four routes this phase; API_ROUTES has "
             "%d" % len(daemon.API_ROUTES))
    if not {"start", "next", "submit", "report"} <= set(daemon.ROUTE_CLI.values()):
        fail("ROUTE_CLI is missing one of the four session CLI commands")
```
"This phase" in the docstring refers to Phase 2, which authored this test —
it does not forbid Phase 7 from growing `API_ROUTES`, but it does mean that
growing it is a **named, deliberate edit to a Phase-2 test's own stated
scope**, not a side effect. Extending `/api/start`'s existing shape avoids
touching this assertion at all, which is the lower-risk path given D-04
already frames the trace as "a `trace` field on `/api/start` when requested"
rather than a new endpoint.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Inline objective filter + `random.shuffle` + count clamp in `do_start()` | `selection.py`'s `select(questions, spec, history)`, one entry point for every caller | This phase | `do_start()` becomes a thin caller; the CLI, `/api/start`, and Phase 10 all reach selection through one function instead of `do_start()` being the only implementation and Phase 10 having nowhere correct to plug in |
| Session JSON as the memory of "what was just answered" | Evidence log (`_evidence/evidence.jsonl`) as the memory, read via `evidence.objective_history()` | Already true since Phase 1 (D-08 in `01-CONTEXT.md`); this phase is the first *consumer* of that fact for exposure/cooldown purposes | SEL-03's "verified across a resumed session" is only true because the log outlives the session file — the session JSON was never durable enough on its own |
| Four selection modes as four hypothetical future code paths | One mode table over three shared primitive stages (filter/order/count) | This phase | Turns SEL-02's "visibly different composition" into a data-driven property testable by inspecting one table, not four independently-verified functions |

**Deprecated/outdated:** Nothing in this phase deprecates an existing public
contract outright; `do_start()`'s signature changes (additively, per D-02's
richer spec) but its two call sites are both internal to this codebase, not
an external API surface with outside consumers.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The illustrative `MODES` table shape (dict of `{filter, order, count_policy}`) is a reasonable data structure for D-06's "one table of compositions" — not verified against any external prior art, purely a reasonable composition of primitives already confirmed to exist in this codebase | Architecture Patterns, Pattern 1 | Low — it is presented as illustrative, not prescriptive; the planner may choose a different concrete shape (e.g. a list of `namedtuple`s) as long as it satisfies "one table, not four code paths" |
| A2 | Subject-scoped cooldown (Pitfall 4, option 1) is described as "the pragmatic zero-schema-change default" — this is a recommendation, not a locked decision; 07-CONTEXT.md does not resolve bank-vs-subject-vs-global cooldown scope at all | Common Pitfalls, Pitfall 4 | Medium — if the planner picks bank-scoped without budgeting the schema-change task, the plan under-scopes a real piece of work; if global-scoped is picked without stating the cross-subject noise tradeoff, practice sessions in one subject could be artificially starved by unrelated activity in another |
| A3 | The `[PAIR:]` tag's placement convention (near `[ID:]`/`[HASH:]`, before `[OBJECTIVE:]`) is inferred from the one existing fixture's authoring pattern, not from any stated convention in 07-CONTEXT.md or model.SPEC | Common Pitfalls, Pitfall 1 | Low — the fix (add `\n\[PAIR` to the terminator alternation) is correct regardless of where an author places the tag, since the terminator alternation is order-independent; this assumption only affects how urgently the pitfall would surface in testing |
| A4 | "Prerequisite" (SEL-01) has no resolution proposed in this research beyond "flag it as unresolved" — genuinely no prior art exists in this codebase to build a recommendation from | Open Questions | High — SEL-01 is unsatisfiable as literally written without the planner making a fresh design decision this research could not source from existing code, `07-CONTEXT.md`, or `07-DISCUSSION-LOG.md` |

**If this table is empty:** N/A — see entries above.

## Open Questions

1. **What does "prerequisite" mean as a selection filter (SEL-01)?**
   - What we know: `SEL-01` requires filtering "by objective, prerequisite,
     item type, and difficulty." `07-ROADMAP.md`'s Phase 7 success criterion
     1 repeats the same four-way filter list. `07-CONTEXT.md`'s D-02 lists
     `prerequisite` as a field on the selection spec dict but never defines
     what value it holds or what it filters against.
   - What's unclear: There is no `prerequisite` field anywhere in
     `model.py`'s parsed question dict, `schemas/item.schema.json`, or any
     other schema (verified — grepped the whole repository for
     `prerequisite`/`PREREQ`, the only hits are planning documents, never
     code). No prerequisite graph, dependency chain, or gating mechanism
     exists in this codebase in any form.
   - Recommendation: Treat this as a genuine design decision the planner
     must make explicitly, not infer. The two shapes that fit this
     codebase's existing patterns without inventing a new subsystem: (a) an
     additive `[PREREQUISITE: <objective>]` item tag, parsed the same way
     `[PAIR:]` is added in this phase (D-07's own precedent), where
     `spec["prerequisite"]` filters `q.get("prerequisite") == value`; or (b)
     `spec["prerequisite"]` names an objective, and the filter actually
     means "only items whose own objective the learner has NOT yet passed
     that objective named as its prerequisite" — which would require reading
     evidence for a second, different objective inside the filter stage,
     a meaningfully bigger feature. Recommend (a) as the minimum viable
     reading consistent with SEL-01's plain "filter by X" phrasing, with (b)
     explicitly named as a Phase 10-adjacent stretch, not assumed silently.

2. **Does `selection_weights` in `schemas/settings.schema.json` (already
   tagged `x-itembank-phase: 7`) belong to this phase, or is it mistagged
   Phase 10 work?**
   - What we know: `settings.schema.json:26-63` (verified) already defines
     `selection_weights` with `objective_miss_rate`, `difficulty_spread`,
     `recency_decay` — all tagged `x-itembank-phase: 7`. 07-CONTEXT.md's
     phase boundary explicitly excludes "Evidence-driven weighting and
     decay (TREND-01, SCHED-01). Phase 10 owns 'a weak objective raises its
     weight'... This phase builds the seam the weight plugs into (D-08) and
     ships no weighting model."
   - What's unclear: whether the planner should (a) leave
     `selection_weights` as-is (inert, tagged 7, unread by any code this
     phase ships — matching the existing "inert until phase N" convention
     `surfaces/settings.py`'s `status_text()` already renders for every
     not-yet-wired key), (b) retag it to `x-itembank-phase: 10` since it is
     actually Phase 10's weighting model, freeing "7" to mean only the new
     `selection.profiles`/`selection.cooldown_responses` group this phase
     actually reads, or (c) wire `recency_decay` as this phase's soft-penalty
     coefficient (D-08), since its description already says "how recently an
     item was last served" — arguably exactly D-08's soft penalty, not
     Phase 10's weighting model at all.
   - Recommendation: (c) is the reading most consistent with the existing
     schema's own field descriptions — `recency_decay` reads as D-08's soft
     penalty, not TREND-01's weighting model — but the planner should state
     this explicitly rather than let a pre-existing schema tag silently
     answer a scope question 07-CONTEXT.md's own phase boundary tries to
     draw a hard line around.

3. **Bank-scoped, subject-scoped, or global cooldown window (D-08's "last N
   responses")?**
   - What we know: Pitfall 4 above establishes the sqlite3 index has no
     `bank` column today; `subject` is already indexed.
   - What's unclear: 07-CONTEXT.md's own text ("anything answered within
     the last `selection.cooldown_responses` responses") does not specify
     the scope of "the last N responses" — across everything the learner has
     ever done, or scoped to the bank/subject currently being selected from.
   - Recommendation: bank-scoped is the most intuitively correct match to
     "this session" framing in SEL-03, but costs a schema-version bump on
     the disposable index; subject-scoped is free today and nearly as
     correct for a bank whose objectives are already namespaced by subject
     (D-06 of `01-CONTEXT.md`). State the choice and its cost explicitly in
     the plan.

4. **Should `itembank select --explain` (a new, session-less "preview"
   command) exist as a genuinely new capability, and if so does SURF-04
   ("every capability has both a route and a CLI command") require a
   matching daemon route despite `check_api_route_scope`'s hardcoded count?**
   - What we know: D-04 frames the trace as printable via
     `itembank select <bank> --explain` and as "a `trace` field on
     `/api/start` when requested" — implying the daemon-side capability is
     an *extension* of `/api/start`, not a new route, while the CLI-side
     capability (`itembank select`) is new and does not itself write a
     session.
   - What's unclear: whether a session-less preview is asymmetric enough
     from "start a session" that SURF-04 should be read as requiring its own
     route, or whether `POST /api/start` with a `"preview": true` field
     (returning the trace and items without writing a session file) is the
     correct daemon-side equivalent of `itembank select`.
   - Recommendation: a `"preview": true` field on the existing `/api/start`
     body is the shape consistent with D-04's own text and avoids editing
     `check_api_route_scope`; name this choice explicitly in the plan rather
     than discovering the test failure after the daemon work is done.

## Environment Availability

**Not applicable — no external dependencies.** This phase adds no new
runtime, service, or CLI-tool dependency: it is pure Python stdlib code
operating on files already on disk (the bank markdown, the evidence log, the
settings file). Skipped per the section's own skip condition.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None — direct script execution, matching every existing test in `tests/*.py` (no pytest/unittest runner dependency, confirmed by `.github/workflows/ci.yml:69-74`'s `for t in tests/*.py; do python "$t" || exit 1; done`) |
| Config file | none — CI discovers every file under `tests/` by glob, not a named list (`.github/workflows/ci.yml:66-68`'s own comment: "Every file under tests/, rather than a named list... two test files existed that CI never ran") |
| Quick run command | `python tests/selection_roundtrip.py` |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` (mirrors CI exactly) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SEL-01 | Filtering by objective/prerequisite/type/difficulty returns exactly the matching set | unit | `python tests/selection_roundtrip.py` (a `check_filter_matches` function) | ❌ Wave 0 |
| SEL-02 | Diagnostic/practice/remediation/exam produce visibly different compositions matching each mode's stated purpose | unit | `python tests/selection_roundtrip.py` (a `check_mode_compositions_differ` function asserting, e.g., diagnostic never repeats an objective while practice does, exam ignores evidence-derived reordering while practice does not) | ❌ Wave 0 |
| SEL-03 | Just-answered items are excluded from the same and the next session, verified across a **resumed** session | integration (subprocess-driven, matching `tests/evidence_roundtrip.py`'s own `run()`-via-subprocess pattern) | `python tests/selection_roundtrip.py` (a `check_cooldown_survives_resume` function: submit, kill/reopen the session file, `start` again against the same bank, assert exclusion) | ❌ Wave 0 |
| SEL-04 | Requesting a named pair serves both items together, adjacently | unit | `python tests/selection_roundtrip.py` (a `check_pair_served_together` function against a fixture with a `[PAIR:]`-tagged item pair) | ❌ Wave 0 — also needs Pitfall 6's extended fixture |
| SEL-05 | For any selected item, the tool states in plain terms why it was chosen over another candidate, with a named runner-up | unit | `python tests/selection_roundtrip.py` (a `check_trace_names_runner_up` function asserting the trace's rejected-candidate field is non-empty and its reason string is human-readable, not a rule id) | ❌ Wave 0 |
| D-10 (determinism, cross-cutting) | Same bank + same spec + same evidence snapshot + same seed produces the same ordered items | unit | `python tests/selection_roundtrip.py` (a `check_determinism` function calling `select()` twice with identical inputs and asserting identical output) | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python tests/selection_roundtrip.py`
- **Per wave merge:** `for t in tests/*.py; do python "$t" || exit 1; done`
- **Phase gate:** Full suite green before `/gsd-verify-work`, plus the existing CI schema-validation step (`.github/workflows/ci.yml:41-64`) extended to cover any new `schemas/selection.schema.json` the plan publishes (mirrors the existing `schema_validate.py schemas/session.schema.json ...` invocations already in that job).

### Wave 0 Gaps
- [ ] `tests/selection_roundtrip.py` — new file, covers SEL-01..SEL-05 and D-10 per the table above
- [ ] `fixtures/sample_bank.md` extension (or a new dedicated fixture) — Pitfall 6: current fixture has 6 items, unnamespaced objectives, no `[PAIR:]` tags, and starves any cooldown-based test at its current size
- [ ] Framework install: none — stdlib only, nothing to install

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Single-user, no-accounts tool by design (`.claude/CLAUDE.md`'s "Users: One. No accounts, no auth") |
| V3 Session Management | partially | The existing session-file/evidence-session-id scheme (Phase 1/2), unchanged by this phase beyond adding a `spec` field to what is recorded (D-03) |
| V4 Access Control | no | No multi-tenancy; loopback-only daemon (`SURF-03`) |
| V5 Input Validation | yes | The selection spec dict arriving from the CLI, `/api/start`'s JSON body, or a settings profile is untrusted-shaped input and must be validated the same way `handle_api_start` already validates `count`/`seed`/`mode`/`objective` (`daemon.py:781-792`, verified: type-checked with a safe default on mismatch, never trusted raw) — the new fields (`prerequisite`, `type`, `difficulty`, `exclude_item_ids`, `pair`) need the same treatment, and `exclude_item_ids` specifically must be validated as a list of strings, not eval'd or path-joined |
| V6 Cryptography | no | No new cryptographic operation in this phase; `evidence.evidence_key`/`idempotency_canon` reuse existing `sha256` usage unchanged |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection via a selection spec's `objective`/`prerequisite` string reaching the sqlite3 index's `LIKE` query unescaped | Tampering | Already mitigated in the existing prefix-match path via `_like_escape()` (`evidence.py:475-481`, verified) and parameterized `?`/`ESCAPE '\\'` binding (`evidence.py:550-556`, verified) — any new bank-scoped or prerequisite-scoped query added by this phase must reuse `_like_escape()` and bound parameters, never string-format a value into SQL text. Cross-checked against standard SQLite guidance: bind the pattern and the `ESCAPE` character as separate parameters, never format them into the query string — matches this codebase's existing implementation exactly [CITED: sqlitetutorial.net, sqlite.org/forum, LOW-confidence web corroboration of an already-implemented pattern, not a new design]. |
| A client-supplied `exclude_item_ids` or `pair` value used to construct a filesystem path or a second `open()` call | Tampering / Information Disclosure | Not applicable in this phase's design — `select()` never opens a file itself (D-09); `exclude_item_ids` is compared only against in-memory `evidence_key(q)` strings, never joined to a path. State this explicitly in the plan's threat notes so a future change does not introduce it. |
| Denial of service via an unbounded `count` or a pathological `objective` regex-like string | Denial of Service | Already the shape `do_start()`'s existing guard handles for `count` (`session.py:55-62`, the negative-slice-stop comment) — `selection.py` must preserve that guard rather than drop it during the port. `objective`/`prerequisite`/`type`/`difficulty` are exact-match string comparisons in `_filter_by_spec`-style code, not regex, so no ReDoS surface is introduced. |

## Sources

### Primary (HIGH confidence — read directly this session)
- `.claude/CLAUDE.md` — stdlib-only constraint, degrade-never-block rule, one-of-each-thing architecture
- `.planning/phases/07-selection-engine/07-CONTEXT.md` — D-01..D-10, phase boundary, deferred items
- `.planning/phases/07-selection-engine/07-DISCUSSION-LOG.md` — pair-tag alternatives already considered
- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — evidence store shape, item identity scheme
- `.planning/REQUIREMENTS.md` — SEL-01..SEL-05, MODE-01..MODE-06, TREND-01, SCHED-01
- `.planning/ROADMAP.md` — Phase 7 goal, success criteria, dependency on Phase 1
- `.planning/STATE.md` — current milestone position, no unrelated blockers for Phase 7
- `model.py` (full file read) — `parse_question()`, stem-terminator regex, `TERMINATOR`, `lint()`, `LINT_CODES`, `SPEC`
- `runtime.py` (full file read) — `score_response()`, `canonical_response()`, `session_path()`, `SESSION_UPGRADES`, `write_session()`
- `evidence.py` (full file read) — `evidence_key()`, `objective_history()`, `event_matches()`, `ensure_index()`, `_create_index_schema()`, `live_events()`
- `surfaces/session.py` (`do_start()` and neighboring functions, read in full)
- `surfaces/daemon.py` (`SESSION_MODES`, `API_ROUTES`, `ROUTE_CLI`, `handle_api_start()`, read in full for these sections)
- `surfaces/settings.py` (full file read) — settings load/validate/write pattern
- `surfaces/evidence_cli.py` (full file read) — CLI command pattern for a new `itembank select`
- `surfaces/protocol_cli.py` (relevant sections read) — `CONTRACTS`, `COMMANDS`, `cmd_schema`
- `surfaces/cli.py` (relevant sections read) — `start`/`serve` argument parsers
- `schema_validate.py` (full file read) — the `SUPPORTED` keyword subset any new schema must stay inside
- `schemas/session.schema.json`, `schemas/settings.schema.json`, `schemas/response.schema.json`, `schemas/item.schema.json` (all read in full)
- `tests/daemon_roundtrip.py` (`check_api_route_scope`, read directly)
- `tests/evidence_roundtrip.py` (test conventions, read in part)
- `fixtures/sample_bank.md` (full file read)
- `.github/workflows/ci.yml` (full file read) — test discovery and schema-validation CI shape

### Secondary (MEDIUM/LOW confidence — web, corroborating an already-implemented pattern)
- WebSearch: "sqlite3 python LIKE prefix query parameterized escape pattern" — corroborates that `evidence.py`'s existing `_like_escape()`/parameterized-`ESCAPE` implementation already matches standard practice; not a new design input
- WebSearch: "explainable rule-based item selection engine runner-up reason trace pattern" — corroborates that pairing a chosen item's trace with a named rejected alternative and its reason (contrastive explanation) is a recognized shape in explainable rule-based systems, supporting D-04's design; not a new design input, LOW confidence, general-domain result rather than an itembank-specific citation

### Tertiary (LOW confidence)
- None beyond the two WebSearch results above, both already listed as Secondary/LOW.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no third-party dependency applies; every stdlib module named is already in use in a peer module, verified by direct read
- Architecture: HIGH — every pattern, pitfall, and code example is grounded in a file-and-line-number read this session, not inferred from training knowledge
- Pitfalls: HIGH for Pitfalls 1-6 (all verified against source); the two Open Questions flagged as genuinely unresolved (prerequisite, cooldown scope) are honestly marked as decisions, not findings

**Research date:** 2026-08-08
**Valid until:** Effectively indefinite for the stdlib/architecture findings (no external library version drift is possible); re-verify the `tests/daemon_roundtrip.py:616-624` line numbers and `evidence.py`'s index schema if Phase 6 or an intervening quick-task touches either file before Phase 7 planning begins.
