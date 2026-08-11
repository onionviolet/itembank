---
phase: 03-lesson-format-in-app-reader
verified: 2026-08-11T19:49:00Z
status: human_needed
score: 12/13 must-haves verified
behavior_unverified: 1 # Count of PRESENT_BEHAVIOR_UNVERIFIED truths (present + wired, behavior not exercised); each is detailed in behavior_unverified_items below
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 11/13
  gaps_closed:
    - "When lint is bypassed with --force, the Read the lesson chip is omitted rather than rendered as a link to a dead anchor (03-01 must-have, D-12 note)"
  gaps_remaining: []
  regressions: []
behavior_unverified_items:
  - truth: "A full-chapter lesson (roughly 20,000 words) renders as one continuous document with no pagination and no lazy loading, and scrolls without a perceptible stall (03-04 backstop, UI-SPEC E1)"
    test: "Serve the ~62,000-word lesson (fixtures/big_lesson.md via _tmp_lesson_trial/big_bank.txt) at /lesson/big_bank, open in a browser, and scroll from top to bottom."
    expected: "One continuous document with no pagination, no lazy loading, and no perceptible stall while scrolling."
    why_human: "Structure is verified (one continuous page, no pagination/lazy-load code exists), but 'no perceptible stall while scrolling' is a perceived-performance judgment only a human reading the page can make. Deferred to final-product validation per user instruction (03-06-SUMMARY)."
human_verification:
  - test: "Serve the ~62,000-word lesson at /lesson/big_bank, open it in a browser, and scroll from top to bottom."
    expected: "One continuous document, no pagination, no lazy loading, no perceptible stall while scrolling."
    why_human: "Perceived-performance judgment (UI-SPEC E1 backstop); no automated check can certify scroll feel."
  - test: "In a real browser: open /lesson/lesson_bank, click a backlink into /quiz/lesson_bank#qN and confirm that item is shown first; from that quiz item click 'Read the lesson' and confirm it opens a new tab at the right heading; open /lesson/lesson_bank#<slug> directly and confirm the browser lands on that section."
    expected: "Both link directions work interactively: lesson backlink lands on the quiz with the referenced item pinned first; the quiz chip opens a new tab at the correct lesson heading; a direct fragment deep-link lands on the section."
    why_human: "Structural and HTTP-level evidence is green (hrefs, chip composition, fragment-pin code, live-route tests), but an interactive browser click-through is the user-flow completion check MVP mode requires and was deferred to final-product validation."
  - test: "Repeat the spec-sufficiency trial: give a fresh model only the output of `itembank spec` (no repository access) and ask it to author a bank with a LESSON section, two headings and three items with at least one LESSON-REF; run `itembank lint` on the result."
    expected: "The bank lints with 0 errors on the first attempt, so an authoring agent can write a valid lesson from the contract alone (ROADMAP SC4)."
    why_human: "Artifact evidence exists (_tmp_lesson_trial/fresh_model_bank.txt lints 0 errors), but 'fresh model, no source access, first attempt' is a process claim no codebase check can independently reproduce."
---

# Phase 3: Lesson Format & In-App Reader Verification Report (Re-verification)

**Phase Goal:** As a learner, I want to open the lesson an item is drawn from inside the app, so that I can read the teaching text and jump straight back to the question that tests it.
**Mode:** mvp
**Verified:** 2026-08-09
**Status:** human_needed
**Re-verification:** Yes — after gap closure (commit 9d4380d)

## Re-verification Scope

The previous verification (2026-08-09T02:31:13Z) reported **gaps_found** with one
failed truth: under `serve --force`, a dangling `LESSON-REF` still rendered the
`Read the lesson` chip as a dead-anchor link. Per re-verification protocol, the
failed item received full 3-level verification (exists, substantive, wired)
plus behavioral evidence; all previously-passed must-haves received quick
regression checks (existence + basic sanity + the phase harness).

**Gap closure evidence (commit 9d4380d, "fix(03): blank unresolved LESSON-REF
slugs on the serve path (D-12 --force gap)"):**

- `surfaces/quiz.py` — `page_for()` gains a `lesson_slugs` keyword parameter; when supplied, any item whose `lesson_slug` is not among the resolved heading slugs is blanked to `""` before the served array is emitted.
- `surfaces/daemon.py` — `handle_quiz_get()` (the single quiz-page renderer for the daemon and for `cmd_serve --force`, which launches the daemon scoped to one bank) now calls `parse_lesson(path)` and passes the set of resolved heading slugs into `page_for`. `parse_lesson` is imported at daemon.py:21.
- `tests/lesson_roundtrip.py` — `test_page_for_shapes_and_build()` gained a regression block asserting (a) a dangling `lesson_slug` ("missing-section") is blanked in the served item array, and (b) all slugs are blanked when no heading resolves (the `--force` no-headings case).

Independent behavioral re-check against `fixtures/broken_bank.md` (which carries
a `LESSON-REF: Missing Section` naming no heading), through the exact
`handle_quiz_get` code path (in-process, no server bound):

- resolved heading slugs: `airway-step-by-step`, `calling-for-help`
- raw parsed slug of the dangling item: `missing-section`
- served `lesson_slug`s after the fix: `['', '', '', '', '', '', '']` — no non-empty slug remains, so `chips()`' client-side condition (`q.lesson_slug && LESSON_BASE`) cannot render a chip for it.

The `--force` gate behavior itself is unchanged and re-confirmed: `cmd_serve`
still refuses a broken bank with `refusing to serve a bank with errors; fix
them or pass --force` unless `--force` is given, and `lint` still reports
`error Q1: LESSON-REF 'Missing Section' does not match any lesson heading`.

## User Flow Coverage

User story: "As a learner, I want to open the lesson an item is drawn from inside the app, so that I can read the teaching text and jump straight back to the question that tests it."

| Step | Expected | Evidence in codebase | Status |
|------|----------|----------|--------|
| Open the lesson from a quiz item | The item's meta row carries an always-visible `Read the lesson` chip that opens a new tab; a dangling reference never produces a dead-anchor chip, even under `--force` | `surfaces/quiz_page.py` `chips()` renders `<a class="chip lesson" href="${LESSON_BASE}#${q.lesson_slug}" target="_blank">` only when `q.lesson_slug && LESSON_BASE`; `surfaces/daemon.py:486-491` now supplies `lesson_base` plus a `lesson_slugs` set from `parse_lesson`; `page_for()` blanks unresolved slugs. Live-route test asserts chip + href + `target="_blank"`; regression block asserts dangling slugs are blanked; direct check on `broken_bank.md` shows all served slugs empty | VERIFIED |
| Read the teaching text | `/lesson/<stem>` renders the lesson as one reading document with per-heading sections and slug anchors | `surfaces/lesson.py` `lesson_page()`/`render_markdown()`; live-route test asserts 200, heading text, `id="the-airway-step-by-step"` anchors, and no answer-key leak; CLI twin byte-identical to route (harness re-passed) | VERIFIED |
| Jump back to the question | Each referenced heading carries a backlink to the item that tests it | `surfaces/lesson.py` `_backlinks_html()` emits `/quiz/<stem>#qN` rows; live-route test asserts `/quiz/lesson_bank#q1` and `#q2` present; `backlinks()` filters by `lesson_slug` | VERIFIED |
| Outcome: read teaching text and jump straight back | The full round trip lesson -> question -> lesson works in a browser | Structure, wiring and HTTP-level evidence all green (see steps above); interactive browser click-through remains a human item (deferred to final-product validation per user instruction) | human item |

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: A bank with a `## LESSON` section and `LESSON-REF`-tagged items renders the lesson as reading material, with a working link from each referenced heading to its item | VERIFIED (regression) | `lesson_page()` renders per-heading `<section id="<slug>">` plus backlinks to `/quiz/<stem>#qN`; live-daemon test `test_routes_and_cli_twin` re-passed (heading, slug anchors, backlinks, orphan copy, no key leak); CLI twin byte-identical |
| 2 | SC1 item side: a resolved `LESSON-REF` shows an always-visible `Read the lesson` chip pre-answer, ungated, pointing at `/lesson/<stem>#<slug>` in a new tab; static `build` page carries no chip (D-12) | VERIFIED (regression) | `chips()` chip branch; `test_page_for_shapes_and_build` re-passed; live-route test asserts exactly 2 non-empty slugs on the served lesson bank; `python itembank.py build fixtures/lesson_bank.md` -> 0 "Read the lesson" hits |
| 3 | `/quiz/<stem>#<id>` pins that item first; an unknown or empty fragment is a no-op | VERIFIED (regression) | Fragment pin before shuffle in `quiz_page.py`; `test_page_for_shapes_and_build` ordering assertion re-passed |
| 4 | SC2: A bank with no `LESSON` section parses and renders byte-identically to before | VERIFIED (regression) | `test_lesson03_compatibility_floor` in re-passed harness; `itembank lesson fixtures/sample_bank.md` renders empty state, exit 0 |
| 5 | SC3: `lint` fails with an actionable message, by item number, when a `LESSON-REF` names a missing heading — never a render-time crash | VERIFIED (regression) | CLI: `python itembank.py lint fixtures/broken_bank.md` -> `error Q1: LESSON-REF 'Missing Section' does not match any lesson heading`, exit 1 |
| 6 | SC3 serve gate: `itembank serve` refuses a bank whose lesson ref names a missing heading unless `--force`; under `--force` the chip is omitted rather than a dead-anchor link | VERIFIED (was FAILED — now closed) | Gate re-confirmed live (`refusing to serve a bank with errors`). Chip omission: `handle_quiz_get` passes `lesson_slugs` from `parse_lesson`; `page_for()` blanks unresolved slugs; regression test asserts dangling + no-headings blanking; independent check on `broken_bank.md` served array = all empty slugs -> no chip can render |
| 7 | SC4: `spec` documents the `LESSON`/`LESSON-REF`/`LESSON-SRC` grammar well enough for first-try authoring | VERIFIED (regression) | `python itembank.py spec` contains `THE LESSON SECTION`, `LESSON-REF`, `LESSON-SRC`, `THE SLUG RULE`, all four lesson codes; trial artifact `_tmp_lesson_trial/fresh_model_bank.txt` lints 0 errors |
| 8 | SC4 machinery: `itembank schema --all` carries the grammar via `SPEC` verbatim — one contract, no second copy | VERIFIED (regression) | `python itembank.py schema --all` embeds the full SPEC incl. lesson grammar; README/docs carry zero `LESSON-SRC`/`LESSON-REF` copies (grep clean) |
| 9 | `[LESSON-SRC:]` shared source: one branch, containment refusal before any open, structured error, degraded reader state | VERIFIED (regression) | `parse_lesson()` refuses out-of-tree paths before open; harness tests (shared parse, traversal/absolute/prefix-sibling refusal, subdirectory accept, missing file, src-wins-over-inline, degraded render) all re-passed |
| 10 | Reader renders exactly D-08's scope: headings, paragraphs, lists, tables, inline code, fenced code, bold/italic/links; fenced code carries `language-<info>` verbatim (Phase 9 seam); all text escaped; stdlib only | VERIFIED (regression) | `render_markdown()`/`_render_blocks()`/`_code_block()`; per-block-kind, verbatim-code, injection, `javascript:` scheme and overflow tests re-passed; no third-party imports in `surfaces/lesson.py` |
| 11 | CLI twin completeness: `itembank lesson --ref` filters one section through the one slugifier; no-match hard-stops with locked message; count semantics; route unchanged (fragment only) | VERIFIED (regression) | CLI: `--ref "when to call for help"` -> `1 lesson section(s)` exit 0; `--ref "no such heading"` -> exit 1 with locked message; harness slug-variant and byte-identical tests re-passed |
| 12 | Backstop E5: `itembank lesson` prints no progress line; a very large `[LESSON-SRC:]` render does not read as a hang | VERIFIED (regression) | Harness CLI one-status-line assertions re-passed; prior measurement of the ~62,000-word fixture at 0.136s stands |
| 13 | Backstop E1: a full-chapter lesson renders as one continuous document and scrolls without a perceptible stall | PRESENT_BEHAVIOR_UNVERIFIED | Structure verified (one continuous page, no pagination/lazy-load code); perceived scroll smoothness is a human judgment, deferred to final-product validation — see Human Verification |

**Score:** 12/13 truths verified (1 present, behavior-unverified; 0 failed)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `model.py` | `lesson_slug()`, `parse_lesson()`, `LESSON-REF` tag, `LESSON_UNCHECKED`, `lint(questions, lesson=...)`, four lesson codes in `LINT_CODES`, SPEC lesson grammar | VERIFIED | 827 lines; all symbols present; harness + CLI evidence re-confirmed |
| `surfaces/lesson.py` | `LESSON_TEMPLATE`, `render_markdown()`, `backlinks()`, `lesson_page()`, `cmd_lesson()` | VERIFIED | 459 lines; all exports present and wired to daemon route + CLI |
| `surfaces/daemon.py` | `LESSON_GET_RE`, `handle_lesson_get`, ROUTES/ROUTE_CLI rows; quiz handler passes `lesson_base` + `lesson_slugs` | VERIFIED | 1226 lines; `handle_quiz_get` now supplies `lesson_slugs` (the gap fix); daemon_roundtrip 46 checks re-passed |
| `surfaces/quiz.py` | `page_for(..., lesson_base="", lesson_slugs=None)`, serve lint gate, `__LESSON_LABEL__` substitution | VERIFIED | 180 lines; `lesson_slugs` blanking is the gap fix; serve_roundtrip re-passed |
| `surfaces/quiz_page.py` | `.chip.lesson` style, `LESSON_BASE`, `chips()` lesson branch, fragment pin before shuffle | VERIFIED | 513 lines; chip branch condition (`q.lesson_slug && LESSON_BASE`) makes blanked slugs render nothing |
| `surfaces/cli.py` | `lesson` subparser with `--ref`, `cmd_lesson` import, `cmd_lint` supplies lesson | VERIFIED | `--ref`/`--out` wired; `cmd_serve --force` reaches the fixed handler via `serve_scoped` |
| `schemas/lint_error.schema.json` | Four lesson codes in closed enum | VERIFIED | All four present; coupling tests re-passed |
| `fixtures/lesson_bank.md`, `lesson_shared.md`, `lesson_src_bank.md`, `broken_bank.md`, `lesson_broken_src_bank.md` | Lesson grammar fixtures incl. shared source, broken refs, unreadable source | VERIFIED | All exist and are exercised by the re-passed harness |
| `tests/lesson_roundtrip.py` | Phase-wide behavioral harness incl. the `--force` regression | VERIFIED | Harness re-passed (`ok: lesson roundtrip ...`), now including the dangling-slug and no-headings regression |
| `tests/protocol_roundtrip.py` | Namespace-prefix coupling admits `lesson` | VERIFIED | `LINT_PREFIXES = ("item", "bank", "lesson")`; coupling tests re-passed |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `surfaces/daemon.py` `handle_quiz_get` | `model.parse_lesson` | resolved heading slugs -> `page_for(lesson_slugs=...)` | WIRED | Newly wired by the gap fix; `parse_lesson` handles None/error/headings shapes safely |
| `surfaces/quiz.py` `page_for` | served item array | blanks `lesson_slug` when not in `lesson_slugs` | WIRED | Regression test + direct check on broken bank confirm |
| `model.parse_lesson` | external lesson file | `[LESSON-SRC:]` containment before open | WIRED | Refusal decided from resolved path; harness tests re-passed |
| `surfaces/lesson.py` | `model.parse_lesson` | reader branches on `error` key / `None` | WIRED | Empty and degraded states distinct; harness re-passed |
| `surfaces/cli.py` | `model.parse_lesson` | `cmd_lint` loads lesson beside questions | WIRED | Turns lesson checks on; `--force` not offered on lint |
| `model.lint` | `schemas/lint_error.schema.json` | every emitted code in the published enum | WIRED | Coupling tests re-passed |
| `surfaces/quiz.py` | `model.lint` | `cmd_serve` gates on the same errors | WIRED | Reproduced: refuses broken bank before binding; `--force` bypass reaches the chip-omitting path |
| `surfaces/lesson.py` | Phase 9 (LOOP-02/03) | `language-<info>` class on code element | WIRED | `_code_block()` emits verbatim escaped content; `math` fence fixture |
| `surfaces/lesson.py` | `model.lesson_slug` | `--ref` resolved by slugifying caller text | WIRED | Slug-variant tests re-passed |
| `model.SPEC` | `surfaces/protocol_cli.py` | `itembank schema --all` publishes SPEC verbatim | WIRED | CLI check confirms; no second copy anywhere |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `lesson_page()` body | heading text/body | bank file read -> `parse_lesson()` headings | Yes — real bank prose | FLOWING |
| lesson backlinks | `Q<n>: <stem>` rows | `backlinks(qs, slug)` over `load(bank)` | Yes — real questions | FLOWING |
| quiz chip | `lesson_slug` | `parse_question()` -> `public_item()` -> served array, then filtered by `lesson_slugs` | Yes on the normal path; unresolved refs blanked on the `--force` path (gap closed) | FLOWING |
| lint findings | code/field/item/message | `lint(qs, lesson=...)` -> `LintError` | Yes — real parse data | FLOWING |
| degraded lesson note | warn sentence + source path | `lesson_page()` error branch from `parse_lesson()` | Yes — authored directive echoed, reason kept in lint | FLOWING |

### Behavioral Spot-Checks (re-verification)

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Clean lesson bank lints | `python itembank.py lint fixtures/lesson_bank.md` | 0 errors, exit 0 | PASS |
| Broken lesson ref fails by item | `python itembank.py lint fixtures/broken_bank.md` | `error Q1: LESSON-REF 'Missing Section' does not match any lesson heading`, exit 1 | PASS |
| Lesson renders with backlinks | `python itembank.py lesson fixtures/lesson_bank.md` | `2 lesson section(s)`, exit 0 | PASS |
| `--ref` filters one section, slug-insensitive | `python itembank.py lesson fixtures/lesson_bank.md --ref "when to call for help"` | `1 lesson section(s)`, exit 0 | PASS |
| `--ref` miss hard-stops | `python itembank.py lesson fixtures/lesson_bank.md --ref "no such heading"` | exit 1, locked message | PASS |
| No-lesson bank renders empty state | `python itembank.py lesson fixtures/sample_bank.md` | `0 lesson section(s)`, exit 0 | PASS |
| Static build carries no lesson chip (D-12) | `python itembank.py build fixtures/lesson_bank.md <out>` | 0 `Read the lesson` matches | PASS |
| Serve gate refuses broken lesson ref | `lint(qs, lesson=parse_lesson(...))` in-process | errors listed; `cmd_serve` would refuse without `--force` | PASS |
| Gap: dangling ref chip omitted under serve path | daemon `handle_quiz_get` code path on `broken_bank.md` (in-process) | served `lesson_slug`s all empty -> no chip can render | PASS |
| Spec documents grammar | `python itembank.py spec` | all lesson grammar sections + 4 codes present | PASS |
| Schema bundle carries grammar | `python itembank.py schema --all` | SPEC verbatim incl. lesson codes | PASS |
| Phase test harness | `python tests/lesson_roundtrip.py` | ok (incl. new `--force` regression) | PASS |
| Daemon regression (changed file) | `python tests/daemon_roundtrip.py` | ok: 46 checks | PASS |
| Serve regression (changed file) | `python tests/serve_roundtrip.py` | ok: 6 items scored in-process | PASS |

### Probe Execution

SKIPPED — no `probe-*.sh` scripts exist in this repo; this phase's runnable checks are the Python roundtrip harnesses above (all executed and passing).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| LESSON-01 | 03-01 | Bank carries optional `LESSON` section | SATISFIED | `parse_lesson()` + fixture; harness re-passed |
| LESSON-02 | 03-01 | Item references a heading via `LESSON-REF` | SATISFIED (code) | Tag -> `lesson_slug` -> chip + backlinks; REQUIREMENTS.md tracking still says Pending (stale — see Anti-Patterns) |
| LESSON-03 | 03-01 | No-lesson bank parses byte-identically | SATISFIED (code) | `test_lesson03_compatibility_floor`; tracking still Pending (stale) |
| LESSON-04 | 03-03 | `lint` fails by item number on missing heading | SATISFIED | Reproduced live; tracked Complete |
| LESSON-05 | 03-06 | `spec` documents the grammar for source-free authoring | SATISFIED (code) | SPEC content + trial artifact lints 0 errors; tracking still Pending (stale) |
| LESSON-06 | 03-01 | Lesson renders in-app with items reachable | SATISFIED | Live-route tests re-passed; tracked Complete |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `surfaces/quiz_page.py` | 199-205 | Comment claims the slug "is empty when lint was bypassed with --force" | INFO (now accurate) | The comment now matches the implemented behavior (slugs blanked by `page_for` via `lesson_slugs`); no misleading comment remains |
| `.planning/REQUIREMENTS.md` | 30-33, 225-228 | LESSON-02/03/05 still `Pending` though implemented and verified | WARNING | Tracking table stale; code evidence is green |
| `surfaces/lesson.py` | 201 | `re.split(r"[/#]", t, 1)` passes `maxsplit` positionally (DeprecationWarning on newer Python) | INFO | Non-blocking; no behavior impact on supported runtimes |

Working-tree hygiene from the initial verification is **resolved**: the trial
bank files in `_tmp_lesson_trial/` are now `.txt` (renamed per the 03-06
summary), so `python itembank.py guard .` exits 0 with 0 offending files.

No `TBD`/`FIXME`/`XXX` debt markers found in phase-modified source files.

### Human Verification Required

### 1. Full-chapter scroll smoothness (backstop E1)

**Test:** Serve the ~62,000-word lesson at `/lesson/big_bank`, open it in a browser, and scroll from top to bottom.
**Expected:** One continuous document, no pagination, no lazy loading, no perceptible stall while scrolling.
**Why human:** Perceived-performance judgment only a human reading the page can make; deferred to final-product validation per user instruction (03-06-SUMMARY).

### 2. Interactive click-through of both link directions

**Test:** In a real browser, open `/lesson/lesson_bank`, click a backlink, confirm it lands on `/quiz/lesson_bank#qN` with that item pinned first; from the quiz item click `Read the lesson` and confirm a new tab opens at the right heading; open `/lesson/lesson_bank#<slug>` directly and confirm the browser lands on that section.
**Expected:** Both link directions work interactively; the direct fragment deep-link lands on the section.
**Why human:** Structure, wiring and live-route HTTP evidence are all green, but interactive browser behavior is the user-flow completion check MVP mode requires.

### 3. Independent spec-sufficiency trial (SC4 first-attempt claim)

**Test:** Give a fresh model only the output of `itembank spec` (no source access) and ask it to author a bank with a `LESSON` section, two headings, three items and at least one `LESSON-REF`; run `itembank lint` on the result.
**Expected:** 0 errors on the first attempt.
**Why human:** The executor's trial artifact (`_tmp_lesson_trial/fresh_model_bank.txt`) lints 0 errors, but "fresh model, no source access, first attempt" is a process claim no codebase check can independently reproduce.

### Gaps Summary

**The single structured gap is CLOSED.** The `--force` dead-anchor chip behavior
from the initial verification is fixed in commit 9d4380d and verified at all
three levels plus behaviorally: `handle_quiz_get` now computes the set of
resolved lesson headings and `page_for()` blanks any item whose `LESSON-REF`
does not resolve, so `chips()` cannot render a chip to a dead anchor; a
regression test locks both the dangling-slug and no-headings cases, and an
independent check against `fixtures/broken_bank.md` through the daemon code
path confirms every served `lesson_slug` is empty. No remaining gaps and no
regressions were found; the lesson, daemon, and serve roundtrip suites all
re-passed after the change.

**Carried-forward warnings (not gaps):** `.planning/REQUIREMENTS.md` still
lists LESSON-02/03/05 as Pending although all are implemented and verified —
update the tracking table. The `re.split(..., 1)` positional-`maxsplit`
DeprecationWarning in `surfaces/lesson.py:201` remains informational.

**Human items remain** (3, including the one behavior-unverified truth), all
deferred to final-product validation per the user's explicit instruction;
automated verification is otherwise green.
## Deferred Verification Run (2026-08-11) — live execution

Executed live in a python-capable environment: fresh sibling worktree
(`itembank-phase-verify`, branch `gsd/deferred-verify`, from main tip
`801ae8f`).

### Automated checks (exact commands and results)

| Check | Command | Result |
|-------|---------|--------|
| Full roundtrip suite (40 files) | `python tests/*_roundtrip.py` (invoked per file in `&&` chains) | PASS — every file exits 0 (the sole env-blocked file is the phase-13 Windows onedir fixture, unrelated to this phase) |
| Lesson harness | `python tests/lesson_roundtrip.py` | PASS — slug/parse/fingerprint/LESSON-SRC/degraded/route/CLI twin/lint/coupling/compatibility floor incl. the `--force` dangling-slug regression |
| Daemon regression | `python tests/daemon_roundtrip.py` | PASS — 63 checks incl. the lesson route and the quiz `lesson_slugs` path |
| Serve regression | `python tests/serve_roundtrip.py` | PASS — 6 items scored; focus-pin regression green |
| Clean lesson bank lints | `python itembank.py lint fixtures/lesson_bank.md` | PASS — 0 errors, exit 0 (4 warnings, machine `[ID:]` notices) |
| Broken lesson ref fails by item | `python itembank.py lint fixtures/broken_bank.md` | PASS — `error Q1: LESSON-REF 'Missing Section' does not match any lesson heading`, exit 1 |
| Lesson renders with backlinks | `python itembank.py lesson fixtures/lesson_bank.md` | PASS — `2 lesson section(s)`, exit 0 |
| `--ref` filters one section, slug-insensitive | `python itembank.py lesson fixtures/lesson_bank.md --ref "when to call for help"` | PASS — `1 lesson section(s)`, exit 0 |
| `--ref` miss hard-stops | `python itembank.py lesson fixtures/lesson_bank.md --ref "no such heading"` | PASS — locked message, exit 1 |
| No-lesson bank renders empty state | `python itembank.py lesson fixtures/sample_bank.md` | PASS — `0 lesson section(s)`, exit 0 |
| Static build carries no lesson chip (D-12) | `python itembank.py build fixtures/lesson_bank.md /tmp/lesson_out.html`, then `grep -c "Read the lesson"` | PASS — 0 hits |
| Spec documents grammar | `python itembank.py spec` | PASS — `LESSON` / `LESSON-REF` / `LESSON-SRC` / THE SLUG RULE + all four lesson codes present |
| Schema bundle carries grammar | `python itembank.py schema --all` | PASS — SPEC embedded verbatim incl. the lesson grammar |

### Truth status updates

Truths 1-12 are live-verified this run. The three items previously labelled
human are resolved as follows:

- **Interactive click-through of both link directions** — VERIFIED with
  recorded automated browser-engine evidence: `03-UAT.md` test 2 (2026-08-10)
  found the served-quiz fragment-pin gap via automated click-through; the gap
  was fixed inline (optional `focus=<item id>` on `/api/start` in
  `surfaces/session.py` + daemon passthrough + served-client fragment send in
  `surfaces/quiz_page.py`), and a post-fix live headless-Chrome check of
  `/quiz/pin_bank#q2` renders the referenced item first with the
  Read-the-lesson chip intact. `tests/serve_roundtrip.py` asserts the focus
  pin and passes here.
- **Independent spec-sufficiency trial (SC4 first-attempt claim)** —
  VERIFIED with recorded evidence: `03-UAT.md` test 3 (2026-08-10) documents
  an independent-model trial — authored from the output of `itembank spec`
  alone, no repository access — whose bank (LESSON section, two headings,
  three items, LESSON-REF) lints 0 errors on the first attempt (3 warnings,
  all expected machine-assigned `[ID:]` notices).
- **Truth 13 / backstop E1 — full-chapter scroll smoothness** — remains
  HUMAN-REQUIRED (perceptual judgment). `03-UAT.md` test 1 records the
  structural proxy (one 402 KB continuous document, 62,545 rendered words,
  headless-Chrome render ~526 ms, no pagination/lazy-load markers), but "no
  perceptible stall while scrolling" is a perceived-performance judgment only
  a human can certify.

### HUMAN-REQUIRED (exact manual steps; 1 item)

1. **Full-chapter scroll smoothness (backstop E1).** Serve the ~62,000-word
   lesson (`fixtures/big_lesson.md` via a bank that names it) at
   `/lesson/big_bank`, open it in a browser, and scroll from top to bottom.
   Expected: one continuous document, no pagination, no lazy loading, no
   perceptible stall while scrolling. (Optional residual confirmation: repeat
   the interactive click-through of both link directions in your own browser
   — the automated evidence above is green, so this is a sanity pass, not a
   gate.)

## Phase 03 Close-Out Live Re-confirmation (2026-08-11)

Close-out run in the phase-03 worktree (`.phase03-wt`, branch
`gsd/phase-03-close`, from main tip `2b5678c`) — the ported record above was
re-executed live, not just copied. The branch carries **zero code diff vs
main** (`git diff main HEAD` empty), so every result below is the merged
code's behavior.

### Truths re-verified live (all VERIFIED)

| Truth | Live command | Result |
|-------|--------------|--------|
| 1, 9, 10 (render, LESSON-SRC, markdown scope) | `python tests/lesson_roundtrip.py` | PASS — slug/parse/fingerprint/LESSON-SRC/degraded/route/CLI twin/lint/coupling/compatibility floor incl. the `--force` dangling-slug regression and both link directions |
| 2 (chip; served) | `python tests/serve_roundtrip.py` | PASS — 6 items scored; focus-pin regression green |
| 3 (fragment pin) | `python tests/serve_roundtrip.py` (focus pin block) | PASS |
| 4 (no-lesson bank) | `python itembank.py lesson fixtures/sample_bank.md` | PASS — `0 lesson section(s)`, exit 0 |
| 5 (lint by item) | `python itembank.py lint fixtures/broken_bank.md` | PASS — `error Q1: LESSON-REF 'Missing Section' does not match any lesson heading`, exit 1 |
| 6 (serve gate/`--force`) | `python tests/lesson_roundtrip.py` regression + `fixtures/lesson_broken_src_bank.md` | PASS — gate + blanking regression green; `lesson.src_unreadable` error, exit 1 |
| 7 (spec grammar) | `python itembank.py spec` | PASS — `THE LESSON SECTION`, `LESSON-REF`, `LESSON-SRC`, `THE SLUG RULE`, all four lesson codes |
| 8 (schema bundle) | `python itembank.py schema --all` | PASS — SPEC embedded verbatim incl. lesson grammar |
| 9 (shared source) | `python itembank.py lint fixtures/lesson_src_bank.md` + `python itembank.py lesson fixtures/lesson_src_bank.md` | PASS — 0 errors; `2 lesson section(s)` from shared source |
| 11 (`--ref` CLI twin) | `python itembank.py lesson fixtures/lesson_bank.md --ref "when to call for help"` / `--ref "no such heading"` | PASS — `1 lesson section(s)` exit 0; locked message exit 1 |
| 12 (no progress line) | lesson harness CLI assertions + `2 lesson section(s)` single status line | PASS |
| 2 (static build D-12) | `python itembank.py build fixtures/lesson_bank.md /tmp/lesson_out.html`, `grep -c "Read the lesson"` | PASS — 0 hits |
| 13 / E1 (scroll smoothness) | — | **HUMAN-REQUIRED** (unchanged; perceptual judgment, see ported record) |

Schema + CI couplings: `python schema_validate.py` block (lint, lint-src,
session, item, response, report payloads vs `schemas/*.json`) PASS;
`python itembank.py lint fixtures/sample_bank.md` 0 errors / 6 warnings;
`python itembank.py guard .` 0 offending files; `.agents/skills` vs
`.claude/skills` mirrors identical; `python tests/protocol_roundtrip.py`
PASS (83 lint codes, schema pins, coupling).

### Full-suite result (45 files) — 41 PASS, 4 pre-existing failures NOT caused by this phase

The full `tests/*.py` suite was run in this worktree (CI shape). 41/45 pass,
including every phase-03 file (`lesson_roundtrip`, `daemon_roundtrip`,
`serve_roundtrip`, `protocol_roundtrip`). The 4 failures reproduce at main
tip with the branch carrying zero code changes, and all belong to other
phases' test/code, not phase 03:

- `tests/evidence_roundtrip.py` — "index was not rebuilt at version 3":
  `evidence.py` declares `INDEX_VERSION = 2` (evidence.py:1035) while the
  test asserts a rebuild lands on `"3"` (tests/evidence_roundtrip.py:1192).
  Test/code drift in the evidence layer (phase 08+), pre-existing.
- `tests/gate_roundtrip.py` — "rows must differ only by context... got
  [None, None]": `objective_history()` projects rows without the `context`
  key on both the indexed and fallback paths (evidence.py:908-917, 939-951)
  while the test expects `context` in the rows. Phase 3.1/10 drift,
  pre-existing.
- `tests/packaging_roundtrip.py` — `dist/itembank-sidecar-onedir is
  missing`: the onedir build artifact requires `powershell -File
  scripts/build_shell.ps1`; this machine has no `docker` and the artifact
  was never built. Environment-blocked, matching the ported record's
  "phase-13 Windows onedir fixture" note; unrelated to phase 03.
- `tests/phase_062_audit.py` — cascades: it asserts the full suite is green,
  so it fails on the three above.

**Phase-03 verdict:** truths 1-12 VERIFIED live (identical to the ported
2026-08-11 deferred-verify run), truth 13/E1 remains HUMAN-REQUIRED. No
phase-03 regression found; the four suite failures are other phases' drift
and are flagged to the orchestrator rather than fixed here (out of phase-03
scope).

---

_Verified: 2026-08-09_
_Verifier: the agent (gsd-verifier)_
