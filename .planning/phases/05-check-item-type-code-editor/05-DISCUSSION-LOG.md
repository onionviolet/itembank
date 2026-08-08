# Phase 5: Check Item Type & Code Editor - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-08
**Phase:** 5-check-item-type-code-editor
**Areas discussed:** Gray-area selection only — all four areas delegated to Claude

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Delegate all | Claude picks, biased toward optionality, flags anything one-way | ✓ |
| Language scope | Python-only vs a per-item interpreter field | |
| Test case format in the bank | stdin/stdout pairs, call-and-compare table, or free-form asserts | |
| Editor + timeout mechanics | Textarea+gutter vs contenteditable; Job Object vs taskkill vs process group | |

**User's choice:** Delegate all
**Notes:** Same standing instruction as Phase 2.1. No additional constraints given.

---

## Claude's Discretion

All four areas. Resolved in `05-CONTEXT.md` as D-01 through D-12. Three flagged as open
to planner override: the `::` case separator if expected stdout can contain it (D-03),
the Windows Job Object approach if it cannot be tested on the target machine (D-07), and
the `--lan` execution refusal if it conflicts with Phase 2's `--lan` plumbing (D-09).

**Architectural finding that drove D-01:** `runtime.canonical_response()` is a pure
string reduction shared with the static offline page. Running a subprocess inside it
would put execution on a browser-shared code path, so the runner is a separate module
that produces a per-case results vector *before* the scorer compares it.

**Format finding that drove D-07:** none of the existing item fields record a language
or a test case, so `check` needs new markers rather than a reinterpretation.

## Deferred Ideas

- Runnable code inside lesson prose (LOOP-03, Phase 9) — reuses this runner
- A second language (C, JavaScript) — a `check.languages` config entry
- Model-marked code and model hints on a failed case (Phase 8)
- Real isolation (containers, seccomp) — permanently out at this scale per CODE-05
- Per-case partial credit — computable from D-01's vector, not reported this phase
- Theming the editor (Phase 4)
