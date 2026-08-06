# Architecture Research

**Domain:** Local-first assessment runtime extending into a learning platform (evidence, hints, scheduling, auditing, agent adapters, dual CLI/HTTP surfaces)
**Researched:** 2026-08-05
**Confidence:** HIGH (general patterns — event sourcing, ports-and-adapters, idempotency, content addressing — are well-established industry practice; the itembank-specific synthesis below is opinionated architectural judgment grounded directly in `PROJECT.md`, the existing codebase map, and `ROADMAP.md`, not externally verified against a comparable open-source system of this exact shape)

## Standard Architecture

### System Overview

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                              Surfaces Layer                               │
│  CLI (argparse)         Daemon (one process, route table)                 │
│  surfaces/cli.py        surfaces/daemon.py                                │
│      │                       │                                            │
│      │  argparse -> op_*     │  GET/POST <path> -> op_*                   │
│      ▼                       ▼                                            │
│  surfaces/session.py    surfaces/api.py    (thin marshaling, both sides)  │
│      (CLI JSON verbs)   (HTTP JSON verbs — same verbs, same payloads)     │
│                               │                                            │
│  quiz_page.py / study.py / day.py / report page / settings page           │
│  render HTML shells whose JS calls the SAME /api/* the CLI/agent calls    │
└──────────────┬───────────────┬────────────────────────────────────────────┘
               │                │
               ▼                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    Runtime Layer — the Operations API (Core)              │
│  Scoring | Session state machine | Hint ladder | Public/private payloads  │
│             runtime.py  (op_start / op_next / op_submit / op_hint / ...)  │
│             — the ONLY module that decides correctness or reveals a key — │
└──────────────┬───────────────────────────────────────┬───────────────────┘
               │ reads/writes                            │ reads
               ▼                                          ▼
┌────────────────────────────────┐   ┌───────────────────────────────────┐
│         Evidence Layer          │   │            Model Layer            │
│  Append-only event log +        │   │  Parse markdown bank, LESSON      │
│  projections (session state,    │   │  section, format contract, lint,  │
│  attempt view, day log,         │   │  content-hash item ID minting     │
│  longitudinal/objective query)  │   │             model.py               │
│             evidence.py         │   │  Depends on: nothing              │
│  Depends on: nothing (opaque    │   └───────────────────┬───────────────┘
│  item_id/objective strings)     │                       │
└──────────────────────────────────────────────────────────┘
               ▲                                          ▲
               │ writes (gated by lint)                    │ reads
┌──────────────┴───────────────┐   ┌──────────────────────┴───────────────┐
│   Scheduler / Trends          │   │             Auditor                   │
│  due-today, daily cap,        │   │  syllabus -> objectives -> coverage   │
│  selection weight, decay flag │   │  map -> draft -> lint -> reversible   │
│  reads evidence + model       │   │  write, autonomy-configurable          │
└───────────────────────────────┘   └───────────────┬───────────────────────┘
                                                      │ drafts via
                                                      ▼
                                     ┌──────────────────────────────────────┐
                                     │        Model Adapter (interface)      │
                                     │  draft_item() / grade_rubric_hint()   │
                                     │  vendor-neutral ABC; never scores;    │
                                     │  never writes evidence directly       │
                                     └──────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Notes |
|-----------|----------------|-------|
| `model` | Parse markdown, additive `LESSON`/`LESSON-REF` grammar, mint content-hash item IDs at first lint, format-version compatibility | Unchanged responsibility from today; extended, never re-architected. Zero dependencies, preserved. |
| `runtime` (Operations API) | Score responses, run the session state machine including hint-ladder cursor-hold, decide hint tier content, control public/private visibility | This is the seam both CLI and daemon call. Formalizing it as "the operations API" — not inventing a new layer — is the load-bearing decision in this document. |
| `evidence` (new) | Append-only event log, replay/projection functions, idempotency check, content-agnostic queries by session/objective/date | Single store replacing `_attempts/*.md`, session JSON, `daily_log.md`. No knowledge of scoring rules or LLMs. |
| `scheduler`/trends (new) | Objective due-today selection, daily cap, selection weighting, decay flagging | Pure consumer of `evidence` + `model`; writes nothing except an optional "schedule computed" audit event. |
| `auditor` (new) | Ingest syllabus, map objectives to bank coverage, draft items via the adapter, write only through `model.lint()`, reversible | Never a second parser. Autonomy level is a config value read at call time, not a code fork. |
| Model adapter (new) | Vendor-neutral interface an LLM implements: draft item text, suggest a rubric grade | A *client* of `runtime`'s `op_next`/`op_submit`/`op_hint` when acting as a test-taker; a *supplier* of draft text to the auditor when acting as an author. Never scores, never writes evidence directly. |
| `server`/`daemon` (consolidated) | One loopback process, one route table, HTML shells + `/api/*` JSON | Replaces one server per subcommand. HTML routes render a shell whose JS calls the same `/api/*` an agent calls — no server-side scoring glue duplicated per surface. |
| `surfaces/` | CLI argument parsing, HTML templating, Anki/GIFT export | Both `surfaces/session.py` (CLI) and `surfaces/api.py` (HTTP) are thin marshaling shims over the same `runtime` functions — neither contains a second scoring or session-state implementation. |

## Recommended Project Structure

```
itembank/
├── itembank.py                 # unchanged: entry point
├── model.py                    # extended: LESSON/LESSON-REF grammar, ID minting, FORMAT-VERSION
├── runtime.py                  # extended: hint(), cursor-hold, becomes formal Operations API
├── evidence.py                 # NEW: event log append/replay, projections, idempotency check
├── scheduler.py                # NEW: due-today, daily cap, selection weights, decay flags
├── server.py                   # unchanged: bind()/port-fallback primitive, reused by daemon.py
├── adapters/                   # NEW: vendor-neutral model adapter interface
│   ├── __init__.py             #   Adapter ABC: draft_item(), grade_rubric()
│   ├── claude_code.py          #   shells out to `claude`
│   ├── codex.py                #   shells out to `codex`
│   └── local_stub.py           #   placeholder for a future Qwen/local backend
├── auditor/                    # NEW: syllabus ingest, coverage map, draft-lint-write pipeline
│   ├── __init__.py
│   ├── syllabus.py             #   objective extraction (adapter-assisted)
│   ├── coverage.py             #   objectives vs model.load() objectives
│   └── writer.py               #   reversible write: shadow copy / git commit + lint gate
├── surfaces/
│   ├── cli.py                  # unchanged role: argparse -> calls runtime/evidence/scheduler ops
│   ├── session.py               # CLI JSON verbs — thin marshaling only
│   ├── api.py                  # NEW: HTTP JSON verbs — same marshaling contract as session.py
│   ├── daemon.py                # NEW: ONE Handler, route table (/,/quiz,/study,/report,/settings,/api/*)
│   ├── quiz.py / quiz_page.py   # becomes a page-shell renderer; POST logic moves into api.py
│   ├── study.py, day.py         # same: page render stays, state changes move into api.py
│   ├── anki.py, gift.py         # export surfaces, GIFT new, same shape as anki.py
│   └── theme.py                 # unchanged, shared by quiz/study/day/daemon
├── _evidence/                   # NEW generated dir (gitignored): events.jsonl + cached projections
├── _attempts/                   # retained read-only for migrated history; no longer written
├── fixtures/, tests/            # extended with synthetic fixtures for every new subsystem
└── itembank.json                # NEW: settings file, schema printed by `itembank config`
```

### Structure Rationale

- **`evidence.py` is a sibling of `runtime.py`, not inside it.** Evidence is dumb storage + query over opaque strings (item_id, objective, session_id). Keeping it import-free of `model` and `runtime` (evidence never interprets a question, never scores) prevents the layering rot the current codebase explicitly guards against ("no scoring in multiple places"). Only `runtime` decides what gets appended and what it means.
- **`adapters/` and `auditor/` are new top-level packages, not `surfaces/`.** They are not rendering clients of the runtime in the sense CLI/daemon are — the adapter is a *dependency injected into* the auditor and the rubric-marking path, and the auditor is a *writer into* `model`'s format, gated by `model.lint()`. Putting them in `surfaces/` would blur "surfaces render, they don't author."
- **`surfaces/api.py` sits beside `surfaces/session.py`, same shape.** This is the concrete embodiment of "every capability has a route and a command, neither is the real one." Both files should be reviewable side by side and should be nearly line-for-line parallel in what they call.
- **`surfaces/daemon.py` is new; `server.py` is untouched.** `server.py`'s `Handler`/`bind()` primitive is already the right abstraction — the daemon is one more subclass of it with a route table, not a rewrite of the primitive.

## Architectural Patterns

### Pattern 1: Operations API (ports-and-adapters / hexagonal core)

**What:** Every state-changing capability (`start`, `next`, `submit`, `hint`, `report`, `schedule`, `audit`) is a plain function on `runtime` (or `scheduler`/`auditor` for their own domains) that takes primitive arguments and returns a plain dict. The CLI and the daemon are both *adapters* around this core — they parse input (argv or HTTP) into the function's arguments and serialize the return value (text or JSON), and nothing else.

**When to use:** Any time a capability must be reachable from two independent surfaces (this milestone's explicit constraint: "every capability reachable from both the app and the CLI").

**Trade-offs:** Slightly more indirection than letting the daemon's POST handler call `runtime.score_response()` directly (as `surfaces/quiz.py` does today). The payoff is that the daemon's `/api/submit` and the CLI's `submit` command become guaranteed-identical by construction — there is only one place cursor-hold, idempotency, and hint-tier bookkeeping can be wrong, and it is testable once instead of twice.

**Example:**
```python
# runtime.py — the operations API
def op_submit(session_path, answer, idempotency=None):
    session = evidence.session_state(session_path)   # replay, not a mutable file read
    item = _current_item(session)
    verdict = score_response(item, answer)            # unchanged: the one scorer
    accepted = evidence.record_response(
        session_id=session.id, item_id=item["id"],
        answer=answer, verdict=verdict,
        hints_used=session.hints_used_this_item,
        idempotency_key=idempotency or (session.id, item["id"], session.attempt_no),
    )
    if verdict.correct:
        evidence.advance_cursor(session.id)
    return session_view(session.id)                   # same payload shape either surface returns

# surfaces/session.py (CLI)
def cmd_submit(args):
    print(json.dumps(runtime.op_submit(args.session, json.loads(args.answer))))

# surfaces/api.py (HTTP)
def handle_api_submit(handler, body):
    result = runtime.op_submit(body["session"], body["answer"], body.get("idempotency"))
    handler.send_json(result)
```

### Pattern 2: Event-sourced evidence store, single append-only log

**What:** Every fact worth remembering (item presented, response submitted, hint requested, session completed, day tick, auditor item written, ID migrated) is appended as an immutable event to one NDJSON log. Session state, the human-readable attempt view, the day log, and longitudinal per-objective history are all *projections* — computed by replaying (a filtered slice of) the log — not separately maintained files. Corrections are new compensating events, never edits to old lines.

**When to use:** Exactly this shape of requirement — "auditable and reversible," "how am I doing on this objective over time," "evidence records more than currently needed because an uncaptured field cannot be backfilled." Event sourcing gives all three for free: the audit trail *is* the store, reversal is an appended event, and adding a new field to future events costs nothing to past ones.

**Trade-offs:** Replay cost grows with log size, but for one learner across three subjects this is thousands of events a year at most — a linear scan in stdlib Python is sub-second for years of use. The honest cost is durability: a single-writer append is not the same operation as the existing write-temp-then-rename pattern used for session files. Mitigate by writing one JSON object per line with a single flushed `write()` call (safe for a single local writer under normal crash conditions) and by treating any malformed trailing line on read as evidence of an interrupted write — skip it, do not fail the read. Materialized projections (session-state cache, rendered attempt view) remain safe to write with the existing atomic write-temp-then-rename pattern, because they are caches: if lost or corrupted, they are regenerated by replay, never treated as authoritative.

**Example:**
```jsonl
{"schema_version":1,"ts":"2026-08-05T14:02:01Z","type":"response_submitted","session_id":"s1","item_id":"a3f9c2e1","objective":"airway-mgmt","score":"incorrect","hints_used":0,"attempt_no":1}
{"schema_version":1,"ts":"2026-08-05T14:02:40Z","type":"hint_requested","session_id":"s1","item_id":"a3f9c2e1","tier":3}
{"schema_version":1,"ts":"2026-08-05T14:03:10Z","type":"response_submitted","session_id":"s1","item_id":"a3f9c2e1","objective":"airway-mgmt","score":"correct","hints_used":1,"attempt_no":2}
```
`report` reads the second `response_submitted` event's `hints_used` to say "right at tier 1," not "right at tier 4" — the distinction the milestone requires falls out of the log shape directly, no extra bookkeeping.

### Pattern 3: Content-hash ID, minted once, then pinned (not recomputed)

**What:** At first `lint`, compute a hash over an item's *identity-bearing* fields (type, stem, correct answer, objective — deliberately excluding explanatory fields like `why`/`disc`/`trap`/`da` that are expected to improve over time) and write it back into the bank file as an explicit `ID:` field. After that, the ID is opaque and immutable regardless of later edits to any field, including the stem. `lint` errors on a hash collision (two items minting the same ID) and on a bank that already has an `ID:` field with a different item's content hashed against it, forcing an explicit disambiguation rather than a silent drift.

**When to use:** Anywhere "stable IDs" and "legitimate content edits happen" both hold, which is every real question bank. This is a deliberate divergence from pure content addressing (where the hash *is* the identity forever, so any edit mints a new ID and orphans history) — pure content addressing is the wrong tool here because it would silently break every evidence event referencing the old hash the moment an author fixes a typo.

**Trade-offs:** Requires one explicit migration step to backfill IDs into every existing item (a one-time `itembank id --assign` pass), and the hash-vs-pinned split must be documented clearly in `spec` so an authoring agent understands the ID it sees today will still be there after it improves the `why` text tomorrow.

### Pattern 4: Idempotent `submit` via the natural domain key

**What:** Rather than requiring a client-generated idempotency-key header (the generic HTTP pattern), use the domain's own natural key: `(session_id, item_id, attempt_no)`. Before appending a `response_submitted` event, `op_submit` checks whether an event already exists for that exact key; if so, it returns the previously recorded verdict without rescoring, without incrementing `hints_used`, and without moving the cursor a second time.

**When to use:** Any resumable session where a network retry (daemon) or a re-run (CLI, agent) could resubmit the same answer to the same item.

**Trade-offs:** This is weaker than a generic idempotency key (it cannot distinguish "the same answer, resubmitted" from "a different answer to a question the client thinks it's re-answering") but that ambiguity does not matter here: within one attempt at one item, only one accepted verdict should ever exist, and a differing answer within the same attempt is itself a client bug worth surfacing as an error rather than silently accepting.

### Pattern 5: Strangler-fig daemon consolidation

**What:** Build `surfaces/daemon.py`'s route table and `Handler` subclass as new, standalone plumbing first — it can bind a port and serve a router with zero business logic wired in. Cut each existing per-subcommand server (`quiz.py`'s `serve`, `day.py`'s cockpit) over to the daemon route by route, deleting the old bespoke server only once its route's daemon equivalent is proven against the same fixtures. At every point in the migration, both the old and new implementations are runnable; nothing is a big-bang cutover.

**When to use:** Consolidating N ad hoc servers into one process is exactly the shape strangler-fig migrations solve — replace incrementally at the boundary, verify each slice, delete the old slice last.

## Data Flow

### Hint ladder flow

```
learner answers wrong
    │
    ▼
runtime.op_submit()  ──► runtime.score_response() [unchanged: the one scorer]
    │  incorrect
    ▼
evidence.record_response(correct=False, hints_used=0)   # cursor NOT advanced
    │
    ▼
surface shows "incorrect — try again or ask for a hint" (still public_item(), key still withheld)
    │
learner calls `hint` / POST /api/hint
    ▼
runtime.op_hint()  ──► deterministic tier lookup over the ALREADY-AUTHORED item fields:
    tier 0: LESSON-REF pointer   tier 1: objective   tier 2: trap
    tier 3: da[picked letter]    tier 4: discriminator   tier 5: reveal
    │  (never returns tier N+1 content; a tier not yet requested is never leaked)
    ▼
evidence.record(hint_requested, tier=N)   # hints_used increments
    │
learner resubmits, this time correct
    ▼
evidence.record_response(correct=True, hints_used=N)   # cursor now advances
    │
    ▼
`report` reads the accepted response event's hints_used to distinguish
"right at tier 1" from "right at tier 4"
```

### Evidence store flow (writers and readers)

```
WRITERS                                   EVIDENCE LOG (_evidence/events.jsonl)          READERS
runtime.op_start/next/submit/hint  ──►    append-only, one event per line          ──►   evidence.session_state()
day surface tick                   ──►                                             ──►   evidence.objective_history()
auditor.writer (post-lint, post-write) ──►                                         ──►   evidence.attempt_view() (report)
migration backfill script (one-time, tagged "migrated") ──►                        ──►   evidence.day_log_view()
                                                                                     ──►   scheduler (due-today, decay, weights)
```
Evidence never calls back into `model` or `runtime` — it is queried, not consulted. `runtime` is the only writer of scoring-consequential events; the auditor writes `auditor_item_written` events describing its own actions, never a `response_submitted` event (it never grades anyone).

### Auditor flow

```
itembank audit ingest syllabus.md
    │
    ▼
auditor.syllabus (adapter-assisted extraction: objectives + subtleties, not just headings)
    │
    ▼
auditor.coverage: cross-reference against model.load(bank).objectives  →  gap report
    │
    ├─ autonomy = report-only  ────────────────────────────► print/return gap report, STOP
    │
    ├─ autonomy = draft-and-approve
    │       adapter.draft_item(objective)  →  model.lint(draft)  →  on fail: feed errors back to
    │       adapter, retry to cap (same closed-loop shape as the authoring-loop requirement)
    │       →  present to human  →  on approval only: auditor.writer commits to bank
    │
    └─ autonomy = full audit-draft-lint-fix-commit
            same draft/lint/retry loop, no human gate, auditor.writer commits automatically
            │
            ▼
    auditor.writer: shadow-copy the bank file (or git commit) BEFORE writing, then write via the
    same model.load()/lint() path a human editing by hand would use — the auditor has no private
    notion of validity. Every write is reversible via the shadow copy / git revert, and an
    evidence event records what was written and by which autonomy level.
```

## Anti-Patterns

### Anti-Pattern 1: A second scoring path in the daemon's POST handler

**What people do:** Port `surfaces/quiz.py`'s existing pattern forward — the daemon's `/api/submit` handler calls `runtime.score_response()` and does its own cursor/session bookkeeping inline, "because it's right there."

**Why it's wrong:** This recreates exactly the debt the codebase map already flags (`quiz.py` and `day.py` each standing up their own server with their own glue) at the JSON-API layer instead of the HTML layer, and it is precisely how "one scorer" quietly becomes two.

**Do this instead:** `/api/submit` calls `runtime.op_submit()` — the same function `surfaces/session.py`'s CLI `submit` command calls. If the daemon needs behavior the CLI doesn't have (e.g., a websocket push), that behavior wraps the operations API call, it does not reimplement it.

### Anti-Pattern 2: Re-hashing item IDs on every parse

**What people do:** Treat "content-hash ID" as "recompute the hash from current content every time the bank is loaded," reasoning that it keeps the ID "honest."

**Why it's wrong:** Every legitimate typo fix or improved `why` text becomes an ID change, silently orphaning every evidence event, every scheduler weight, and every longitudinal report row that referenced the old ID — the exact failure mode content-addressed systems are known to hit when content mutates.

**Do this instead:** Hash once, at first lint, over identity-bearing fields only; store the result as an explicit field in the bank file; treat it as opaque and immutable afterward. Provide an explicit, rare escape hatch (`itembank id --rekey`) for the genuine "this is actually a different question now" case, which itself writes a `rekey` event so history can still be joined across the seam.

### Anti-Pattern 3: Three evidence stores becoming two

**What people do:** Build the new event log for sessions and hints, but leave `daily_log.md` or `_attempts/*.md` as a "just for humans" convenience file that is *also* written directly by some surface.

**Why it's wrong:** The instant a second surface writes state outside the log, "how am I doing on this objective over time" has two answers again, and the auditability guarantee (append-only, reversible) no longer covers all state.

**Do this instead:** Any human-readable markdown view (a rendered attempt page, a log-shaped export for git-diff review) is generated on demand from the event log and never parsed back in as a source of truth. If a human wants to hand-edit graded evidence (e.g., manual `short`-answer marking), that edit is itself submitted through an operations-API function that appends a new event — never a direct file edit to a projection.

### Anti-Pattern 4: Adapter output treated as an accepted score

**What people do:** Wire the model adapter's `grade_rubric()` result directly into the same evidence field a deterministic scorer writes, because "the model is usually right."

**Why it's wrong:** This is precisely the out-of-scope anti-feature the project already named — auto-grading prose into mastery without a review state — now reintroduced through the adapter seam instead of a hosted grader.

**Do this instead:** Adapter-suggested rubric grades are written with `review_state: pending`; only an explicit accept (human, or a configured-and-logged auto-accept policy that is itself a visible setting, not a silent default) transitions a rubric point to counted evidence.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Claude Code / Codex CLI | Adapter shells out to the CLI as a subprocess, passing draft/grade requests and reading structured output | Never sees bank content over a network call — this satisfies the "bank content never leaves the machine" constraint as long as these CLIs themselves run locally, which they do in this project's actual usage. |
| Future local Qwen backend | Adapter implementation targeting an HTTP endpoint on `127.0.0.1` once the 7900 XTX build exists | Same `Adapter` ABC; no itembank core code changes when this backend is added — this is the whole point of the interface. |
| GitHub Releases (self-update) | `urllib` fetch of a release manifest + checksum, opt-in or check-on-launch per settings | The one place outside loopback the network constraint permits; sends nothing, fails silently offline. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `model` ↔ everything | One-directional: everything imports `model`, `model` imports nothing | Preserved unchanged from today. |
| `runtime` ↔ `evidence` | `runtime` calls `evidence.append()`/`evidence.session_state()`/query functions directly (in-process function calls, not a service) | `evidence` never calls back into `runtime`. |
| `runtime` ↔ `scheduler`/`auditor` | `scheduler` and `auditor` call `runtime`/`model`/`evidence` read functions; `runtime` never imports `scheduler` or `auditor` | Keeps the core operations API ignorant of who consumes it. |
| `auditor` ↔ `adapters` | `auditor` holds a reference to whichever `Adapter` implementation config selects; calls `draft_item()`/`grade_rubric()` | `adapters` package has zero imports of `model`/`runtime`/`evidence` — it only knows text in, text out. |
| `surfaces/cli.py` ↔ `surfaces/api.py` | No direct import of one by the other; both import `runtime`/`scheduler`/`auditor` independently and stay structurally parallel | Prevents the daemon depending on argparse or the CLI depending on `http.server`. |
| `surfaces/daemon.py` ↔ `surfaces/quiz.py`/`study.py`/`day.py` | Daemon route handlers call page-render functions from these modules for GET (HTML shell), and `surfaces/api.py` for any POST/state change | The old per-surface servers are deleted once their daemon route is proven (strangler-fig), not before. |

## Suggested Build Order

Ordering follows one rule: **land the thing every later requirement reads or writes before building the thing that reads or writes it.** Stable IDs and the evidence store are the two facts almost everything else depends on; everything that only touches rendering, packaging, or a self-contained interface can move independently.

1. **Content-hash item IDs + format/schema versioning** (`model.py`: ID minting/pinning, `FORMAT-VERSION`, machine-readable lint error codes). Small blast radius, no new files, unlocks every ID-keyed evidence event that follows. *Build first.*

2. **Evidence store — the single event log** (`evidence.py`: append, replay/projection functions, idempotent-submit check). Capture the *full* event schema now — including fields not consumed until later (`response_time`, `confidence`, `error_category`, `review_state`) — because adding a field later is free and backfilling one is not. Depends on (1) for stable keys.

3. **Migration/backfill of existing evidence** (`_attempts/*.md`, session JSON, `daily_log.md` → tagged, best-effort-joined events; old files retained read-only, not deleted). Depends on (1) and (2); do this immediately after the store lands, before anything else writes to it, so there is one evidence history, not a split one.

4. **`LESSON` section + `LESSON-REF`** (additive `model.py` grammar + `spec` text). No dependency on (1)-(3); can run in parallel with them, coordinating on `model.py` diffs.

5. **Hint ladder + cursor-hold + `hint` command + `hints_used`/tier reporting.** Depends on (2)/(3) for evidence-backed `hints_used`, and on (4) for tier-0 lesson pointers.

6. **Operations-API formalization + daemon consolidation.** Split into two parallel tracks: (a) daemon *plumbing* — route table, `Handler`, static asset serving, page shells — has no dependency on (1)-(5) and can start immediately; (b) wiring `/api/*` to live `runtime` operations should follow (2) and ideally (5), so the API is worth building once. Old per-subcommand servers retire route by route (strangler-fig), not in one cutover.

7. **Selection engine + objective-level scheduler + daily cap.** Depends on (1) for objective attribution across edited items and (2)/(3) for the history it schedules against.

8. **Trends control loop** (selection-weight adjustment, decay flagging, longitudinal `/report` view). Extends (7)'s weights and reads the rich fields captured in (2). Natural continuation of (7), not a hard prerequisite for anything else.

9. **Model adapter interface + rubric marking for `short`.** Independent of (4)-(8); its only real prerequisite is (2) existing to receive rubric-assist results as `review_state: pending` evidence. Can start as early as (2) lands and proceed in parallel with (4)-(8).

10. **Auditor** (ingest, coverage map, draft-lint-fix-commit, configurable autonomy, reversible writes). Depends on (9) for drafting/extraction and (1) for objective-to-item mapping. Loosely coupled to (7)/(8) for the "point at weak objectives" refinement — build the core ingest/map/draft/lint/write loop without waiting on trends, and connect the refinement afterward.

11. **`check` item type + one subject-invariant loop across EMT/Math/CS** (LaTeX rendering, runnable-code verification, monospace editor). `check` itself (`model`/`runtime` addition) is independent and can be built any time after step 1 lands, coordinating on `model.py`/`runtime.py` diffs with steps 1 and 4. The "one loop across three subjects" integration is necessarily last among content work, since it needs `LESSON` (4), hint ladder (5), and `check` all present.

12. **Surface polish, GIFT export, theming, settings/packaging/self-update.** All independent of the evidence-side work and of each other; the settings *mechanism* (`itembank.json`, `itembank config` printing a schema) is cheapest scaffolded early (right after step 1) with a minimal schema, then every later phase (2, 5, 7, 9, 10) additively registers its own keys — leaving this step to be mostly zipapp packaging, the self-update client, and final UI/theming polish.

### Genuinely parallel work

- **Step 4 (`LESSON`)** alongside steps 1-3 (evidence spine) — different concerns inside the same file, coordinate on `model.py` diffs only.
- **Step 6a (daemon plumbing)** alongside steps 1-5 — pure HTTP scaffolding, no business logic wired in yet.
- **Step 9 (adapter interface)** alongside steps 4-8 — a standalone interface plus subprocess-shelling concrete implementations, gated only by step 2.
- **GIFT export, theming, UI fixes, `study` field-parity fix** (part of step 12) — can start on day one; they touch rendering surfaces only and have no dependency on the evidence spine at all.
- **`check` item type's core parsing/scoring** (part of step 11) — can start early, right after step 1, if `model.py`/`runtime.py` churn is coordinated with whoever owns steps 1 and 4 in the same window.
- **Settings-file mechanism scaffold** — cheapest done right after step 1, then extended additively by each later step rather than saved for the end.

### Not parallelizable

- Steps 2 and 3 (evidence store, then its migration) must be sequential and must both land before step 5 (hint ladder), step 7 (scheduler), step 8 (trends), or step 10 (auditor's evidence-aware refinement) start consuming real history — building any of those against the old three-store world means rebuilding them against the new one.
- Step 6b (`/api/*` wiring to live operations) should not precede step 2, or the daemon's JSON contract will need to change shape once evidence-backed idempotency lands.

## Migration Path for Existing Session and Attempt Files

1. **Nothing is deleted automatically.** `_attempts/*.md` and existing `_attempts/session_*.json` remain on disk, read-only from the new system's point of view, serving as the audit trail of the migration itself.
2. **ID assignment first.** Run `itembank id --assign` (or equivalent) across every bank referenced by existing attempts/sessions to mint and pin content-hash IDs, so the backfill in step 3 has stable keys to write into new evidence events.
3. **One-time backfill script**, idempotent and re-runnable:
   - Session JSON `responses[]` → `response_submitted`/`session_completed` events, joined to the new item ID via bank path + recorded `Qn` position at write time.
   - Attempt markdown headings (verdict markers, `MARK:` overrides) → `response_submitted` events, same join strategy.
   - `daily_log.md` rows → `day_tick` events per date/lane.
   - Every backfilled event is tagged `"provenance": "migrated"` and `"confidence": "exact"` or `"approximate"` (approximate whenever the position-based join is ambiguous — e.g., the bank's item order changed since the original attempt). The script emits a report of any attempt/session it could not join with `exact` confidence, for manual review rather than silent best-effort acceptance.
   - The script checks the evidence log for an existing migration marker per source file before reprocessing it, so re-running it after fixing an ambiguous join does not duplicate events.
4. **Cutover.** Once backfill completes and its report is clean (or manually resolved), all subsequent writes go through `evidence.append()` only; `runtime.write_session()`/`read_session()` are re-pointed to evidence-backed `session_state()`/`record_*()` functions, and the three old write paths are removed from the runtime (the old *files* stay, per step 1).

## Sources

- [Event Sourcing Pattern — Azure Architecture Center, Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing) — append-only store, compensating events for correction, replay to rebuild state, audit trail as a first-class property. HIGH confidence, official vendor-neutral architecture reference.
- [Event sourcing pattern — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/event-sourcing.html) — corroborates the same shape independently. HIGH confidence.
- [Docker Engine v1.10.0 content-addressability migration notes](https://github.com/moby/moby/wiki/Engine-v1.10.0-content-addressability-migration/ce2c0f0233d4f278709a7405a65ad2872dfc82eb) — concrete precedent for the "hash changes when content changes" tension that motivates the mint-once-then-pin pattern here. MEDIUM confidence (project wiki, but describes a shipped, well-known migration).
- [Idempotent requests — Stripe API Reference](https://docs.stripe.com/api/idempotent_requests) — canonical description of check-before-apply idempotency, adapted here to a domain-native key instead of a client-generated header. HIGH confidence, industry-standard reference implementation.
- [HTTP servers — Python 3 official documentation, `http.server`](https://docs.python.org/3/library/http.server.html) — confirms `BaseHTTPRequestHandler`/`self.path` dispatch is the correct stdlib-only primitive for the consolidated daemon; corroborates the existing codebase's own `server.py` approach rather than suggesting a framework. HIGH confidence, official docs.
- Ports-and-adapters / hexagonal architecture (general software-architecture pattern, not sourced to a single document) — underlies the "Operations API" pattern recommended for the CLI/daemon dual-surface requirement. Applied here as established practice, not a novel claim.

---
*Architecture research for: itembank learning-platform milestone (evidence spine, hint ladder, daemon consolidation, scheduler, auditor, model adapter, dual surfacing)*
*Researched: 2026-08-05*
