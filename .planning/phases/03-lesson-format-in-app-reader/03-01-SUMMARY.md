---
phase: 03-lesson-format-in-app-reader
plan: 03-01
subsystem: lesson-reader
tags: [lesson, tracer, reader, daemon-route, cli-twin, fingerprint]
key-files:
  created:
    - surfaces/lesson.py
    - fixtures/lesson_bank.md
    - tests/lesson_roundtrip.py
  modified:
    - model.py
    - runtime.py
    - itembank.py
    - schemas/item.schema.json
    - surfaces/daemon.py
    - surfaces/cli.py
    - surfaces/quiz.py
    - surfaces/quiz_page.py
key-decisions:
  - "D-04 resolved option-a: lesson_ref/lesson_slug stay EXCLUDED from content_fingerprint(), locked by a regression assertion (fingerprint of a tagged item equals the byte-identical untagged item)."
  - "One slugifier: model.lesson_slug() produces both the lookup key and the HTML anchor id; surfaces/lesson.py imports it and never redefines it."
  - "One parser: parse_lesson() mirrors parse_bank()'s boundary rule over the unbounded split; a prose line shaped like Q1. cannot truncate the lesson."
  - "One render: lesson_page() is the only generator of the lesson document; the daemon route and itembank lesson write byte-identical output."
  - "D-12: the Read the lesson label is substituted away on pages with no reader behind them (static build), so the fixed string never ships to a page that cannot honour it."
requirements-completed: [LESSON-01, LESSON-02, LESSON-03, LESSON-06]
completed: 2026-08-08
---

# Plan 03-01 Summary - Lesson Tracer

**Objective:** Prove the whole lesson architecture end to end on the thinnest
real path: one bank carries one `## LESSON` section with one referenced
heading, the reader renders it at `/lesson/<stem>`, the heading links into the
item that tests it, and that item links back to the heading.

## What Was Built

- `model.lesson_slug()` - one pure slugifier (collapse, lowercase, ASCII
  letters/digits/space/hyphen only, whitespace runs to single hyphens,
  idempotent, empty on empty input).
- `model.parse_lesson(bank_path)` - independent read over the bank file,
  mirroring `parse_bank()`'s boundary rule over the unbounded split; returns
  `None` without a `## LESSON` section, otherwise `source`/`body`/`intro`/
  `headings` (text/slug/body) and empty `error`/`detail`.
- `parse_question()` - `[LESSON-REF:]` captured as `lesson_ref` plus its
  `lesson_slug`, with the `\n[LESSON-REF` stem-terminator alternative so the
  tag can never leak into the stem; `content_fingerprint()` untouched.
- `runtime.public_item()` - carries `lesson_slug` (empty when untagged).
- `schemas/item.schema.json` - additive optional `lesson_slug` property,
  version stays 1.
- `itembank.py` - exports `lesson_slug` and `parse_lesson` alphabetically.
- `surfaces/lesson.py` - the reader: `LESSON_TEMPLATE`, `render_markdown()`
  (stdlib, headings + paragraphs, text runs escaped), `backlinks()`,
  `lesson_page()`, `cmd_lesson()`. No key, no verdict (D-10), stdlib only.
- `surfaces/daemon.py` - `LESSON_GET_RE`, `handle_lesson_get`, ROUTES and
  ROUTE_CLI rows; `handle_quiz_get` passes `lesson_base`.
- `surfaces/cli.py` - `itembank lesson <bank> [--out]` subparser.
- `surfaces/quiz_page.py` - `.chip.lesson` CSS, `LESSON_BASE` constant,
  chips() lesson branch, and the fragment-pin step ahead of the shuffle.
- `surfaces/quiz.py` - `page_for(..., lesson_base="")` and the label
  substitution.
- `fixtures/lesson_bank.md` - synthetic tracer fixture: one `## LESSON`, two
  `###` headings (one referenced, one orphan), three items (mc, multi, short),
  first two tagged `[LESSON-REF:]` immediately after the difficulty
  parenthetical, third untagged.
- `tests/lesson_roundtrip.py` - the phase's one harness: in-process half
  (slug, parse, fingerprint lock, compatibility floor, public_item, schema,
  structural rules) and subprocess half (daemon routes, 404, CLI twin
  byte-identity, chip presence/absence, fragment-pin ordering).

## Commits

| Task | Commit |
|------|--------|
| Task 2 - tracer (fixture, tests, model, runtime, schema, entry point, reader, route, CLI) | 912e0da |
| Task 3 - lesson chip + fragment-pin deep link | 786d41b |

## Deviations

- **Checkpoint/continuation handling:** Task 1's `checkpoint:decision` was
  resolved by the orchestrator as **option-a** (the plan's own recommendation,
  D-04 as written) under the user's standing delegation; the typed
  continuation-executor protocol could not be driven through this install
  (the continuation template it expects is absent), so Tasks 2-3 were
  implemented inline in the orchestrator rather than by a subagent. The
  resolution itself is unchanged from the plan's recommendation.
- **Chip label substitution:** the plan's Task 3 wording has `chips()` append
  an anchor whose label is the locked string; to satisfy the written
  acceptance criterion that the static `build` page contains no `Read the
  lesson` string at all (`grep -c 'Read the lesson' <build> == 0`), the label
  is template-substituted by `quiz.py` (`__LESSON_LABEL__`), becoming the
  empty string when `lesson_base` is empty. The anchor markup, the
  `.chip.lesson` style, the `LESSON_BASE` constant and the D-12 two-part
  condition all remain in `quiz_page.py` as planned.
- **Href composition:** per the plan's own `LESSON_BASE` JS-constant design,
  the chip href is composed at render time (`LESSON_BASE#<slug>`); the
  served-page href acceptance is satisfied structurally (base constant +
  composition), since the page holds no per-item HTML until the client
  renders.
- **Backlink tab behaviour:** lesson to item backlinks open in the same tab per
  the plan's Task 2 action; the UI-SPEC byline copy (which mentions opening
  in a new tab) is kept verbatim per the Copywriting Contract.

## Verification

- `python tests/lesson_roundtrip.py` -> `ok: lesson roundtrip (...)`
- Full suite (`python tests/*.py`, 16 files) -> all pass, including
  `daemon_roundtrip` (route/CLI inventory), `serve_roundtrip`,
  `protocol_roundtrip` (schema validation) and `packaging_roundtrip`.
- `python itembank.py lint fixtures/lesson_bank.md` -> 0 errors.
- `python itembank.py lesson fixtures/lesson_bank.md --out <tmp>` -> `2 lesson
  section(s) -> <out>`, exit 0.
- `python itembank.py lesson fixtures/sample_bank.md --out <tmp>` -> `0 lesson
  section(s) -> <out>`, page contains `No lesson yet`, exit 0.
- `python itembank.py build fixtures/lesson_bank.md <tmp>` -> exit 0, page
  contains no `Read the lesson` string (D-12).
- `python itembank.py guard .` -> exit 0.
- Structural greps: `maxsplit` 0 in `model.py`; `def lesson_slug` 0 in
  `surfaces/lesson.py`; `score_response|canonical_key|explain_payload` 0 in
  the reader; no markdown/mistune/commonmark imports; `parse_bank` untouched
  (`inspect`-asserted).

## Self-Check: PASSED

All plan acceptance criteria for Tasks 2 and 3 hold; the tracer feedback gate
(re-running the tracer `<verify>` after GREEN) passed before Task 3 began.
