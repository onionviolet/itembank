---
phase: 05-check-item-type-code-editor
plan: 06
subsystem: page-render
tags: [per-case, matrix, refusal, offline, skip, verdict]

requires:
  - phase: 05-check-item-type-code-editor (05-02)
    provides: runner run_result shape (timed_out/truncated flags), the bound semantics (D-08)
  - phase: 05-check-item-type-code-editor (05-05)
    provides: asCheck + .codewrap mount, the per-case explain payload with actual output on both routes, the honest-limits copy plumbing

provides:
  - close()'s check branch: the per-case matrix consumed from the shared normalized observations (served) or the authored explain halves (offline)
  - .case/.case.right/.case.wrong styles mirroring the option treatments, with the warning-role bound-stop status text
  - the offline file-refusal + skip control (D-06), the network refusal (.pend), and the language refusal (error), each with its own locked sentence
  - the null-verdict pending treatment (criterion 12) rendered from the verdict value, never a textual guess

affects: [05-07 final pass, 05-VALIDATION.md matrix/refusal rows]

actuals:
  tokens: 45000
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "The matrix consumes v.interaction_result.observations (served) or derives rows from explain.cases (offline) -- never a second verdict, never a re-run"
    - "The refusal sentences live in the page's own copy (Copywriting Contract) branched by the daemon's refused_reason field"

key-files:
  created: []
  modified:
    - surfaces/quiz_page.py
    - surfaces/daemon.py
    - tests/check_roundtrip.py

key-decisions:
  - "The unknown-language refusal was raised as SystemExit -> HTTP 400 by plan 05-03, which would have landed in the served page's catch block (connectivity copy). Plan 05-06's premise is that both refusals arrive as normal responses with a distinguishable field, so the daemon now maps that SystemExit to a JSON {'refused': ..., 'refused_reason': 'language'} body on both submit routes, matching the network refusal's {'refused': ..., 'refused_reason': 'lan'} shape. This is a recorded necessary deviation: 05-03 shipped the 400; the page branch needs the normal response."
  - "The page owns its locked copy of both server-refusal sentences (the UI-SPEC Copywriting Contract rows) and picks by refused_reason, rather than echoing the daemon body verbatim -- the plan's acceptance requires the served page to contain the sentences, and the contract rows are page copy by design."
  - "The offline page renders the file refusal + skip instead of the editor (asCheck's !SERVE branch returns before CheckEditorBoot.create); the skip advances i++ directly with no verify/settle/close, so nothing is recorded and the item never reaches autoTotal."
  - "The null-verdict case branches on the payload's verdict value (null), never on a textual guess, rendering the existing pending treatment with the case rows underneath -- a killed run reads 'stopped', not 'failed' (criterion 12)."

requirements-completed: [CODE-02, CODE-03, CODE-05]

coverage:
  - id: M1
    description: "Each authored case renders one row (Case N, status from the stable reason, input where authored, expected vs pattern-expected label, actual output), a mixed pass/fail stays dichotomous, and a null verdict renders pending, never pass/fail"
    requirement: CODE-03
    verification:
      - kind: integration
        ref: "tests/check_roundtrip.py#check_matrix_contract (locked strings in the page, .case selectors, mixed-failure observations with distinct case_index/reason, pre-submit contract leak-free, killed run -> None + timeout observation)"
        status: pass
    human_judgment: false
  - id: M2
    description: "Three refusal causes, three locked sentences: offline file page (refusal + skip, no editor), network (pending treatment), language (error treatment); honest-limits survives all three; connectivity copy unchanged"
    requirement: CODE-05
    verification:
      - kind: integration
        ref: "tests/check_roundtrip.py#check_refusal_states (file refusal + skip label in the built page, no editor rendered offline, both server sentences in the served page, distinct, honest-limits present, skip handler advances without verify/settle/close, connectivity sentences unchanged, no generic message)"
        status: pass
    human_judgment: false

duration: 150min
completed: 2026-08-11
status: complete
---

# Phase 05: Check item type — Plan 06 Summary

**A submitted check source is now read as the learner's executable prediction: the page
renders one row per authored case -- number, status from the stable machine-readable reason,
input where authored, expected (or pattern-expected) text, and the bounded actual output --
with the verdict still the dichotomous runtime return (or the pending treatment for a
killed-at-timeout run, never pass or fail). Where the field cannot be used at all, three
distinct locked sentences replace it: the offline file page shows the refusal and a skip that
records and counts nothing, the network refusal reads as a boundary, the language refusal as a
misconfiguration.**

## Performance

- **Duration:** 150 min
- **Tasks:** 2
- **Commits:** 3 (1 test + 2 feat)

## Task 1 — the per-case result matrix

`close()`'s check branch in both clients renders `.case` rows mirroring the existing
`.opt.right`/`.opt.wrong` treatments (same border, background, shape — one visual language,
per the UI-SPEC's "match the neighbor" rule). The served client consumes the shared
normalized `v.interaction_result.observations` — stable 1-based `case_index` + `reason` pairs
from the one run, never scraped from prose, never a second verdict. The offline client derives
rows from its shipped explain halves. The four locked status strings (`Passed`, `Failed`,
`Failed — timed out after %ss`, `Failed — output was cut off at %d KB`) select by `reason`,
with bound stops keeping the failure row but reading in the warning role. `Input` is omitted
when the authored stdin is empty; the `Expected (pattern)` label appears only for `[MATCH:
regex]`. A null `verdict` (killed at timeout) renders the existing pending header with the
rows beneath, so the learner sees the item was stopped, not failed (criterion 12). No per-case
score, percentage, or pass count is displayed anywhere.

## Task 2 — three refusal states and the offline skip

- **Offline file page (D-06):** `asCheck` branches on `!SERVE` — the locked file-refusal
  sentence renders in the pending treatment, the editor never boots, and one `Skip — not
  answerable offline` control advances via `i++; render()` directly (no verify/settle/close),
  so nothing is recorded and the item never reaches the auto-marked total.
- **Network refusal:** the daemon's existing `{"refused": LAN_REFUSAL_COPY}` (200 JSON)
  surfaces in `settle` → `close`, rendered as the page's own locked copy in the pending
  treatment; Check is not re-enabled.
- **Language refusal:** plan 05-03 shipped this as `SystemExit` → HTTP 400, which would land
  in the catch block. The daemon now maps it to `{"refused": ..., "refused_reason":
  "language"}` on both submit routes (normal response), rendered as an error — a
  misconfiguration, not a boundary. **Recorded deviation:** this touches surfaces/daemon.py,
  outside the plan's stated file list, because the plan's premise (both refusals arrive as
  normal responses) required it.
- **Connectivity failure:** unchanged — the existing catch-block copy stays verbatim and the
  button re-enables.
- **Honest-limits:** rendered from the item card, so it survives all three refusal states.
- **No generic message** covers more than one cause (`grep` for "something went wrong" etc. is
  0).

## Task Commits

1. `8b6a8ae` (test) — matrix contract + refusal states assertions
2. `bcadf4d` (feat) — quiz_page.py matrix/skip/refusals + daemon.py language-refusal JSON

**Plan metadata:** docs commit below (05-06-SUMMARY.md).

## Files Created/Modified

- surfaces/quiz_page.py — `.case`/`.refused` CSS; `checkMatrix`/`caseStatus`/`checkRows` helpers in both clients; `close()` check branch + refusal branch; offline `asCheck` !SERVE refusal + skip
- surfaces/daemon.py — `REFUSAL_REASON_*`, `_refusal_body`, `_refusal_from_exit`; both network sends carry `refused_reason`; both SystemExit catches map the unknown-language refusal to JSON
- tests/check_roundtrip.py — `check_matrix_contract`, `check_refusal_states` + main() registration

## Deviations from Plan

- **daemon.py touched** (see Task 2): the unknown-language refusal needed to arrive as a
  normal JSON response for the page branch; 05-03 shipped it as a 400. The CLI path is
  unchanged (still `SystemExit` with the locked copy; the CLI test still expects non-zero exit
  with the sentence).
- **Refusal sentences live in the page, not echoed from the daemon body:** the plan's
  acceptance requires the served page to *contain* the locked sentences; they are the
  UI-SPEC Copywriting Contract rows, so the page owns them and branches by `refused_reason`.
  The daemon still sends the full sentence (its own 05-03 contract), so API consumers are
  unchanged.
- **Pre-submit leak test scoped to the interaction contract:** the full `public_item`
  legitimately contains the stem and starter text (which mention stdin and can contain
  short values), so the leak assertion checks the contract blob for case structure keys and
  distinctive expected values, with the renderer_config key set pinned by `check_public_item`.

## Issues Encountered

- JS string literals split across adjacent `"..." "..."` pieces mean a contiguous sentence is
  not a page substring; tests compare whitespace-collapsed text with the JS quote/plus noise
  stripped.
- The offline page legitimately embeds the CM6 boot script in dead code (`if(!SERVE)` guard
  returns before `create()`), so "renders no editor" is asserted as the guard existing and
  preceding the boot call, not as the script's absence.

## User Setup Required

None.

## Next Phase Readiness

- 05-07 closes the attempt-file/schema/README gaps and runs the end-of-phase manual pass,
  which will visually confirm the matrix, the refusals, and the 10+-case backstop.

---
*Phase: 05-check-item-type-code-editor*
*Completed: 2026-08-11*
