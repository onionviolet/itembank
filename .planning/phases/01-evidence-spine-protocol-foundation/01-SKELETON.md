# Walking Skeleton — itembank Evidence Spine

**Phase:** 1
**Generated:** 2026-08-06

> **Read this qualifier first.** `WALKING_SKELETON` fired because this is Phase 1 with no prior
> phase summaries, but **itembank is not a greenfield project**: `itembank.py`, `model.py`,
> `runtime.py`, `server.py`, `surfaces/*.py`, `tests/*.py` and `.github/workflows/ci.yml` already
> exist and work. The framework, language, layout, and "deployment" (a checkout + `python
> itembank.py`) were settled long before this milestone and are recorded in
> `.planning/codebase/ARCHITECTURE.md` and `.planning/codebase/STACK.md`.
>
> So this file is **not** a project scaffold. It is the architectural contract for the *evidence
> spine* — the subsystem Phase 1 introduces and Phases 6, 7, 8, 10 and 11 all read and write
> against. Every decision below is one a later phase inherits and would have to migrate away from.

## Capability Proven End-to-End

A learner submits one response through `itembank submit`, that response lands as one line in
`_evidence/evidence.jsonl`, and `itembank evidence --objective <obj>` reads it back from that log
alone and prints it.

This is the tracer slice in `01-02-PLAN.md`. It crosses all four existing layers — `model.py`
(item identity), `evidence.py` (the writer and reader), `surfaces/session.py` + `surfaces/cli.py`
(the surface), `tests/evidence_roundtrip.py` (the harness) — with nothing stubbed on the happy path.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| System of record | Single append-only JSONL log at `_evidence/evidence.jsonl` | D-07. Plain text: readable, greppable, git-diffable. Nothing is overwritten, so EVID-05's "auditable" falls out of the format instead of needing code. |
| Query path | Disposable `sqlite3` index at `_evidence/evidence_index.sqlite3`, rebuilt from the log | D-08. A real query engine for "objective X over time" at zero dependency cost. Deletable at any moment with no loss — it is a materialized view, never a second source of record. |
| Write discipline | Exactly one `evidence.append_event()` in the codebase; every surface is a caller | Mirrors the existing one-scorer rule (`runtime.score_response`). `tests/evidence_roundtrip.py` enforces it structurally with the same `os.walk` + regex scan `tests/scoring_roundtrip.py:96-109` uses for the scorer. |
| Append durability | Advisory lock (`msvcrt.locking` on win32, `fcntl.flock` on POSIX) around exactly one `os.write()` per event | The MS C runtime implements `O_APPEND` as `lseek` + `write`, two steps, not one (bpo-42606). Measured on the target machine by `tests/durability_roundtrip.py` before anything writes an event. |
| Reader posture | Per-line `try/except`; a malformed line is skipped and reported, never fatal | D-09. `runtime.read_session()`'s `sys.exit` posture is correct for a whole file and wrong for one line of a growing log. |
| Item identity | Opaque 12-hex `item_id`, assigned once, stored in the bank markdown as `[ID: ...]`; `content_hash` is a **separate** `[HASH: sha256:...]` field used only for change detection | D-01 + D-02. Content-hash-as-ID orphans history on every edit (PITFALLS.md Pitfall 1), and 25 of 45 EMT wrong options are due for editing this milestone. |
| Identity ownership | `model.py` owns identity; it never imports `runtime.py` or `evidence.py` | D-02. Preserves the existing layer split — a bank is self-describing, so copying the `.md` anywhere keeps its evidence resolvable. |
| Undo | Compensating `retraction` events; nothing is ever removed | D-10. A raw line count therefore overstates history — every view and every count shown to the learner is post-retraction. |
| Legacy stores | `_attempts/*.md`, session JSON and `daily_log.md` become **renders** computed from the log | D-11. They are outputs, never inputs. Dual-writing would reintroduce the two-writers problem this phase exists to end. |
| Published contract | `schemas/*.json` (item, session, response, report, lint_error) + `itembank schema`, validated in CI by a minimal stdlib validator that **fails loud on an unsupported keyword** | D-15. A validator that silently ignores keywords it does not implement is a fake gate; failing loud keeps the schemas inside the subset the validator actually enforces. |
| Error contract | Namespaced dotted lint codes (`item.missing_key`, `item.duplicate_id`, …) alongside the field at fault and the unchanged human text | D-16. Codes are an API — renaming one is a breaking change. `LintError.__str__` reproduces today's `"Qn: message"` exactly so CI's substring assertions keep passing. |
| Distinct-response rule | `dedupe_key = sha256(session_id \| item_key \| attempt_number \| canonical_answer)`, with a `short:` + sha256-of-normalized-text fallback where `canonical_response()` returns `None` | D-17 + RESEARCH Pitfall 1. `runtime.canonical_response()` already decides what a response *is*; the fallback is the one documented extension, not a second normalizer. |

## Stack Touched in Phase 1 (the slice, not a scaffold)

- [ ] **Model layer** — `model.py` parses `[ID:]` / `[HASH:]` additively; a bank carrying neither parses byte-identically to today.
- [ ] **Runtime layer** — new `evidence.py` peer module: locked append, defensive read, idempotency, retraction, index.
- [ ] **Store** — one real write to `_evidence/evidence.jsonl` and one real read back out of it.
- [ ] **Surfaces** — `itembank submit` writes an event; `itembank evidence --objective` reads one.
- [ ] **Harness** — `tests/evidence_roundtrip.py` runs the whole path end to end under `python tests/*.py`, exactly as CI already does.

## Out of Scope (Deferred to Later Slices)

Explicit so no later phase re-litigates Phase 1's minimalism:

- Hint tiers and the ladder behaviour (Phase 6) — `hint_tier` is a recorded field, reserved null.
- Session-mode *behaviour* (Phase 6) — the `mode` field is recorded here; what a mode *does* is not.
- Error-category taxonomy (Phase 6/8) — `error_category` is a recorded field, reserved null.
- Model-generated hints and model marking (Phase 8) — `mark` events carry `marker: "human"` only.
- Selection, trends, decay, due-today (Phases 7 and 10) — they read this log; they are not built here.
- Item deletion / retirement semantics (deferred in CONTEXT.md; needed before Phase 11's auditor).
- Whether the legacy files are deleted after a verified migration (deferred in CONTEXT.md).
- Schema version-bump *policy* (deferred in CONTEXT.md) — versions are stamped here, the policy waits for the first bump.

## Subsequent Slice Plan

Each later phase adds capability on top of this spine without changing the decisions above:

- Phase 2: every capability here also gets a daemon route over the same `evidence.py` calls.
- Phase 6: the hint ladder fills `hint_tier`; cursor-hold makes `attempt_number` exceed 1.
- Phase 7: the selector reads `objective_history()` to avoid recent exposure.
- Phase 8: model-written hints append `hint` events; model marks land as `review_state: "pending"`.
- Phase 10: trends and due-today read the same index, with every claim citing the events under it.
- Phase 11: the auditor's coverage claims cite `item_id`s from this identity scheme.
