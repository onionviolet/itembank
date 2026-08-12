# Note: Widen the item grammar — dynamic option sets, hard-limit audit, prose categories

- **Date:** 2026-08-11
- **Context:** `/gsd-explore` session. Topic: unlimit MC option counts; audit other hard-coded type limits; categories on constructed-response items for note-taking.
- **Status: PLANNED ONLY — routing never landed (verified 2026-08-12).** The
  decisions below were agreed in the explore session but **nothing was
  implemented**, and the routing is incomplete: `V2-GRA-01…04` do **not** exist
  in `REQUIREMENTS.md` (no "Item grammar" subsection under `## v2 Requirements`),
  and `ROADMAP.md` has no phase or backlog entry for this work (its §9/§10 are
  the already-completed Phase 9/10, not these). The only artifacts are this
  note and `seeds/item-grammar-user-options.md`. The seed file's trigger
  condition ("V2-GRA-01 lands") therefore cannot fire yet. See §5 Handoff.
- **Binds on:** any future plan touching `model.py` option parsing, `schemas/item.schema.json`, `surfaces/import_anki.py`, `surfaces/quiz_page.py`, GIFT export, or the `short`/`visual` grammars.

## 1. Verified current state (2026-08-11)

- `LETTERS = "ABCDEFGH"` (`model.py:12`) — the master ceiling; parser regexes hard-code `[A-H]` (`model.py:47, 76, 86, 1400`).
- `schemas/item.schema.json:87` — "A letter A-H".
- `surfaces/import_anki.py:106, 272` — Anki-import option regex `[A-H]` + LETTERS filter.
- `surfaces/quiz_page.py:444/846, 570/981` — JS `LETTERS = "ABCDEFGH"` and the PINNED regex `both [A-H] and [A-H]` (all/none-of-the-above pins assume ≤2 letters).
- Lower bound: `item.too_few_options` errors below 3 options (`model.py:2798-2800`) — exactly what blocks True/False.
- `multi`'s "five or six" is **documented but unenforced**: the linter only checks `SELECT == len(CORRECT)` (`model.py:2790`).
- Other hard-coded minima: `table`/`dnd` ≥2 `CATEGORIES` and ≥2 rows (`model.py:2818-2829`); `build` >1 STEP; `short` ≥2 RUBRIC points (`model.py:2851`); `visual` span ≤200 steps / ≤6 fractional digits.
- `[CATEGORIES:]` exists only on `table`/`dnd` (`model.py:129`); `short` is `MODEL:` + `RUBRIC:` — prose categories are net-new.

> **Line numbers re-verified 2026-08-12 after the 12-phase merge** (the numbers
> above were written pre-merge at 10:14; several shifted): `LETTERS` still at
> `model.py:12`; the `[A-H]` option-lookahead regexes are now `model.py:109` and
> `model.py:119` (grep `[A-H]` — no other hits in `model.py`); the schema ceiling
> is now `schemas/item.schema.json:110`; `surfaces/import_anki.py:106`
> (`_OPTION_RE`) still holds; the JS `LETTERS` constants are now
> `surfaces/quiz_page.py:504` and `:1054`; the mc floor check
> `item.too_few_options` is around `model.py:3035`; the `table`/`dnd` ≥2
> CATEGORIES minimum is around `model.py:3057`.

## 2. Decisions (user-delegated: most-comprehensive option; conflicting options kept open, user chooses later)

1. **Option ceiling: truly unlimited and dynamic.** The parser derives the option set from what is written (greedy `X)` lines up to `CORRECT:`); single letters A–Z, then `AA)` … No hard cap.
2. **Audit every hard-coded type limit**, not just mc. Each limit becomes either derived, a documented convention with a lint warning, or a deliberate pedagogy gate — decided per limit.
3. **Lower the mc floor 3 → 2**, legalizing True/False as a plain 2-option mc. Negative-stem ("which is NOT") mc already works and stays.
4. **Dedicated `[TYPE: tf]` rendering kept as a deferred user choice** (seed) — both paths stay open rather than one being silently chosen.
5. **Prose categories: one capability, two modes** — graded structured constructed response (serve/session, per-category rubric) and ungraded note capture (study/day). Both ship; the graded-vs-capture UX is deferred to the planning model.

## 3. Routing

- Requirements: `V2-GRA-01…04` → `.planning/REQUIREMENTS.md` § "### Item grammar".
- Phases: `ROADMAP.md` §9 (dynamic option sets + hard-limit audit) and §10 (prose categories).
- Seed: `item-grammar-user-options.md` (T/F button rendering; graded-vs-capture UX).
- **Uncommitted on purpose:** the tree is mid-merge from a concurrent agent (UU files); commit deferred to merge resolution.

## 4. Open questions for the planning model

- GIFT/QTI option-letter conventions beyond Z (Moodle GIFT letters are display-side, but confirm before widening export).
- Multi-letter label ergonomics in markdown: the `[A-H]` regex lookaheads must become dynamic along with the parser.
- Where a "four is the sweet spot" lint warning (if any) should fire — per-item >6 vs >8 — and whether it applies to `multi`.
- Whether the `visual` span caps are pedagogy gates or implementation limits.

## 5. Handoff — for the next (more capable) agent, written 2026-08-12

The user asked to record this attempt so a more capable agent can pick it up.
This is the **only** feature-extension work left open from 2026-08-11; the day's
12 roadmap phases all merged and milestone v1.0 shipped (see `.planning/STATE.md`
and `.reasonix/REASONIX.md` for that context).

### What exists and what is missing

- **Exists (uncommitted, untracked):** this note, `seeds/item-grammar-user-options.md`.
- **Missing:** the `V2-GRA-01…04` requirement entries (intended for
  `REQUIREMENTS.md` under `## v2 Requirements`), the ROADMAP phase/backlog
  entries, and **all implementation**. Nothing in `model.py`, `schemas/`,
  `surfaces/`, or `runtime.py` was changed for this.

### Suggested first steps

1. **Write the requirements** — add `### Item grammar` under `REQUIREMENTS.md`
   `## v2 Requirements` (line ~221, after `### Interop`) with four entries:
   - `V2-GRA-01` dynamic, unlimited MC option sets (single letters A–Z, then
     `AA)` … — parser derives the set from what is written; no hard cap.
   - `V2-GRA-02` audit every hard-coded type limit (mc floor, `table`/`dnd`
     minima, `build` steps, `short` rubric points, `visual` span/fraction
     caps) — each becomes derived, a documented convention with a lint
     warning, or a deliberate pedagogy gate, decided per limit.
   - `V2-GRA-03` lower the mc floor 3 → 2, legalizing True/False as a plain
     2-option mc (negative-stem mc already works).
   - `V2-GRA-04` prose categories on constructed response — one grammar
     capability, two modes (graded per-category rubric in serve/session,
     ungraded note capture in study/day).
2. **Add the ROADMAP entries** (new phase or `## Backlog` rows under
   `ROADMAP.md` line ~1151) referencing the decisions in §2 and the deferred
   choices in the seed file — do **not** silently pick the `[TYPE: tf]` or
   graded-vs-capture UX; the user's directive was "implement all, let the user
   choose later."
3. **Implement against the re-verified surface list in §1** (line numbers
   re-checked 2026-08-12): the parser regex lookaheads (`model.py:109,119`),
   `LETTERS` (`model.py:12` and the two JS copies in `quiz_page.py`), the
   schema (`schemas/item.schema.json:110`), Anki import (`import_anki.py:106`),
   the linter floors (`model.py:3035,3057`), and the all/none-of-the-above pin
   logic in `quiz_page.py` that assumes ≤2 letters.
4. **Gates:** `python itembank.py lint fixtures/sample_bank.md`, every
   `tests/*_roundtrip.py`, `python schema_validate.py --all`, and the
   skill-mirror `diff -rq .agents/skills .claude/skills`; follow the
   one-atomic-commit-per-plan rule in `AGENTS.md`.
5. **Tree state:** `main` is clean at milestone v1.0 (490 commits, pushed);
   leftover scratch includes `fake_hosted_unused.py` (a Phase-8 hosted-CLI
   probe, unused — safe to delete) and `.gsd/gh-cred.sh` (git→gh credential
   bridge made during the push). Notes/seeds in `.planning/` are untracked by
   design; do not `git add -A`.
