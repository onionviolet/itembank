# Phase 03 Close-Out Handoff — lesson format & in-app reader

Phase: `03-lesson-format-in-app-reader` · Mode: mvp · Branch: `gsd/phase-03-close`
Worktree: `C:\Users\wayba\Downloads\CTF\itembank\.phase03-wt` (from main tip `2b5678c`)
Closed: 2026-08-11

## What phase 03 delivered (all six plans executed, code merged on main)

- `## LESSON` section grammar: `parse_lesson()` in `model.py`, `LESSON-REF`
  item tag, `LESSON-SRC` external source with out-of-tree containment,
  `THE SLUG RULE`, four lesson lint codes in `LINT_CODES`.
- In-app reader `surfaces/lesson.py`: one continuous document, per-heading
  `<section id="<slug>">` anchors, backlinks to `/quiz/<stem>#<id>`,
  markdown renderer scoped to D-08's list, `language-<info>` fence seam.
- Quiz side: always-visible `Read the lesson` chip (`target="_blank"`,
  `/lesson/<stem>#<slug>`), fragment pin (item first), serve lint gate with
  `--force` blanking unresolved slugs (no dead-anchor chip).
- CLI twin: `itembank lesson [--ref <heading>]`, `--ref` miss hard-stops;
  `itembank spec` documents the grammar; `itembank schema --all` embeds SPEC
  verbatim (one contract).
- The 2026-08-10 inline gap fix: served-quiz fragment pin (`focus=` on
  `/api/start` + daemon passthrough + served-client fragment send).

## Verification status (live re-run 2026-08-11, worktree, zero code diff vs main)

- **Truths 1-12: VERIFIED live.** lesson/daemon/serve/protocol roundtrip
  harnesses PASS; `itembank lesson` CLI behaviors PASS; `lint` broken-ref
  error by item PASS; LESSON-SRC shared source + degraded reader PASS; spec +
  `schema --all` grammar PASS; static `build` carries no chip (0 hits).
- **Truth 13 / backstop E1 (scroll smoothness): HUMAN-REQUIRED (pending).**
  Structural proxy recorded (one 402 KB continuous document, 62,545 rendered
  words, headless render ~526 ms, no pagination/lazy-load markers), but "no
  perceptible stall while scrolling" is a perceptual judgment only a human
  can certify. Exact manual steps are in `03-VERIFICATION.md`
  (`HUMAN-REQUIRED` section) — serve the ~62,000-word lesson and scroll.
- `03-UAT.md`: test 2 (interactive click-through) was the one issue; it was
  fixed inline 2026-08-10 and re-verified — UAT now 3/3 passed.
- The ported verification record from branch `gsd/deferred-verify` commit
  `5f5d76d` (2026-08-11 run) is reconciled into `03-VERIFICATION.md`, with a
  close-out re-confirmation section recording this run's exact commands.

## Full suite: 41/45 — 4 failures are OTHER phases' drift, not phase 03

The branch carries zero code diff vs main; all four reproduce at main tip:

1. `tests/evidence_roundtrip.py` — `evidence.py` declares `INDEX_VERSION = 2`
   (evidence.py:1035), test expects a rebuild at `"3"`
   (tests/evidence_roundtrip.py:1192). Evidence-layer test/code drift.
2. `tests/gate_roundtrip.py` — `objective_history()` rows carry no `context`
   key (evidence.py:908-917, 939-951); the test expects `context` in the
   rows. Phase 3.1/10 drift.
3. `tests/packaging_roundtrip.py` — `dist/itembank-sidecar-onedir` missing;
   requires `powershell -File scripts/build_shell.ps1` (build artifact).
   Environment-blocked; matches the previously recorded "phase-13 Windows
   onedir fixture" note.
4. `tests/phase_062_audit.py` — cascades from the three above (it asserts
   the full suite is green).

Recommended owner: flag 1-2 to the evidence/retention maintainer and 3 to
the packaging owner in the orchestrator's central reconciliation; none block
phase 03's close.

## What the orchestrator still owns (NOT touched here, per instruction)

- Tick the ROADMAP Phase 03 checkbox / update the status table.
- `.planning/REQUIREMENTS.md` still lists LESSON-02/03/05 as `Pending`
  though implemented and verified — update the tracking table.
- The single HUMAN-REQUIRED item (E1 scroll smoothness) for final-product
  validation.
