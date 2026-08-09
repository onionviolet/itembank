---
phase: 03-lesson-format-in-app-reader
plan: 04
subsystem: ui
tags: [lesson, markdown-renderer, fenced-code, D-08, Phase-9-seam, html-escaping]

# Dependency graph
requires:
  - phase: 03-lesson-format-in-app-reader
    provides: "parse_lesson()'s body/headings shape, the lesson reader page and route/CLI twin from plans 03-01/03-02, and the lesson lint gate from 03-03"
provides:
  - "render_markdown() widened to D-08's full declared scope: headings, paragraphs, lists, tables, fenced code, inline code, bold/italic and links -- stdlib only, no CommonMark completeness"
  - "The Phase 9 seam: a fenced block carrying an info string renders <pre><code class=\"language-<info>\"> with verbatim HTML-escaped content, so Phase 9 attaches KaTeX and the run button by selector (LOOP-02/LOOP-03) without re-parsing the lesson or forking the renderer"
  - "The extract-and-placeholder discipline: fenced blocks and inline code spans are lifted to opaque placeholders before the inline pass, so code content is never re-scanned or mangled"
  - "Structure-first escaping: every literal text run is escaped after block resolution (never the raw source wholesale), proved by a full-page injection check over heading, prose, table cell, list item and item stem"
  - "fixtures/lesson_bank.md and fixtures/lesson_shared.md extended to exercise every block kind plus the math fence; tests/lesson_roundtrip.py extended with per-kind render assertions"
affects: [03-05 CLI --ref, 03-06 spec grammar text, Phase 9 shared subject lessons, Phase 4 surface reconciliation]

# Actuals (#2632) - pairs with the plan's estimate (chars/4 over the realized diff)
actuals:
  tokens: 7041
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Extract-and-placeholder: fenced blocks (and inline code spans) are lifted to opaque \\x00K<n>\\x00 / \\x00I<n>\\x00 placeholders before any inline pass, so code content survives verbatim and is only HTML-escaped"
    - "Escape-then-pattern inline pass: backtick spans lifted, remaining text html.escape()d, emphasis/link patterns applied to the escaped text, code spans restored escaped -- escaping before patterns run means markup-shaped input can never become markup"
    - "Word-boundary emphasis: (?<!\\w) and (?!\\w) guards keep an underscore inside an identifier from splitting the word"
    - "Single sanitizer for the language class: lesson_slug()'s character set builds class=\"language-<info>\", so a hostile info string cannot break out of the attribute (T-3-10)"

key-files:
  created: []
  modified:
    - surfaces/lesson.py
    - fixtures/lesson_bank.md
    - fixtures/lesson_shared.md
    - tests/lesson_roundtrip.py

key-decisions:
  - "Visible language label: a fenced block with an info string renders a muted .lang caption above the code element, making the 'language label' concrete while the class stays the Phase 9 selector; no behaviour (KaTeX/run/copy) is attached"
  - "Deep headings render as <h2> at the same Display size rather than a third heading size -- the grammar defines two levels and this phase invents no third"
  - "Table fallback is whole-run: any malformed pipe run (missing separator, mismatched cell count) degrades every line of the run to paragraphs rather than emitting a broken table"
  - "The heading-with-markup case lives in the temp-bank injection test, not fixtures/lesson_bank.md, because test_parse_lesson locks the fixture's heading texts exactly -- same slug-vs-visible split and escaping assertion, no conflict with the 03-01 lock"

requirements-completed: [LESSON-06]

coverage:
  - id: D1
    description: "D-08 block scope: fenced code with and without an info string, verbatim content against the inline pass, HTML escaping, unterminated-fence degradation, one-level lists, pipe tables with paragraph fallback"
    requirement: LESSON-06
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_fenced_code_with_language"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_fenced_code_verbatim_against_inline_pass"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_lists"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_table"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_malformed_table_falls_back_to_paragraph"
        status: pass
    human_judgment: false
  - id: D2
    description: "The Phase 9 seam: language-<info> class on the code element with sanitised info, inert (no KaTeX/run/copy), math fence in the shared fixture"
    requirement: LESSON-06
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_lesson_shared_fixture_carries_math_seam"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_fenced_code_without_language"
        status: pass
    human_judgment: false
  - id: D3
    description: "Inline scope: strong/em at word boundaries, inline code escaped and never re-scanned, links restricted to relative paths or http(s) targets"
    requirement: LESSON-06
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_inline_emphasis"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_inline_code"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_links"
        status: pass
    human_judgment: false
  - id: D4
    description: "Structure-first escaping proved: markup-shaped text in heading, prose, table cell, list item and item stem renders escaped, including the heading anchor id and the backlink row"
    requirement: LESSON-06
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_full_page_escapes_markup_shaped_bank"
        status: pass
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_heading_markup_slug_vs_visible"
        status: pass
    human_judgment: false
  - id: D5
    description: "Wide code and tables scroll inside their own overflow-x:auto containers; no nowrap/ellipsis on lesson prose; page body never scrolls horizontally"
    requirement: LESSON-06
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_overflow_containers"
        status: pass
      - kind: other
        ref: "grep: overflow-x:auto in surfaces/lesson.py (1), no white-space:nowrap/text-overflow, no third-party markdown import"
        status: pass
    human_judgment: false
  - id: D6
    description: "A heading deeper than the grammar's own renders at the same Display size with no third heading size"
    requirement: LESSON-06
    verification:
      - kind: unit
        ref: "tests/lesson_roundtrip.py#test_render_deep_heading_same_size"
        status: pass
    human_judgment: false
  - id: D7
    description: "A full-chapter lesson (~20,000 words) renders as one continuous document with no pagination and no lazy loading, scrolling without a perceptible stall"
    requirement: LESSON-06
    verification: []
    human_judgment: true
    rationale: "Backstop per 03-UI-SPEC E1 long-text row and the plan's must_haves: the renderer emits a single server-rendered document by construction, but the perceptible-stall judgment needs a human against the largest available fixture at UAT"

# Metrics
duration: 313min
completed: 2026-08-09
status: complete
---

# Phase 3 Plan 04: Blocks and Inlines for the Lesson Reader Summary

**The lesson reader now renders D-08's full deliberately small scope -- fenced code with a sanitised `language-<info>` class (the inert seam Phase 9 attaches KaTeX and the run button to), lists, tables, emphasis, inline code and links -- with every literal text run escaped after structure resolution and proved by a full-page injection check.**

## Performance

- **Duration:** 313 min (includes the two full-suite runs; renderer work itself was compact)
- **Started:** 2026-08-08T20:28:38Z
- **Completed:** 2026-08-09T01:41:51Z
- **Tasks:** 2 (both TDD: test -> feat)
- **Files modified:** 4 (plus one planning artifact, deferred-items.md)

## Accomplishments

- `render_markdown()` was widened from headings-and-paragraphs to D-08's full block scope behind one extraction pass: fenced blocks are lifted to opaque placeholders before the block classifier and inline pass run, so code content is preserved character for character apart from HTML escaping and the inline pass can never reach inside a fence.
- A fenced block carrying an info string renders `<pre><code class="language-<info>">` with the info string sanitised through `lesson_slug()`'s character set (T-3-10) and a muted `.lang` caption; a fence with no info string renders without a class; an unterminated fence degrades to the rest of the section rather than raising (T-3-04). No KaTeX, no run button, no copy button -- the seam is cut and left inert for Phase 9.
- Dash and digit lists render one level deep (one item per line, ended by a blank line or a non-matching line); pipe tables render with a header row and fall back to paragraphs on any malformed shape -- lone pipe line, missing separator, or a row with a different cell count.
- The inline pass is ordered so escaping cannot be undone: backtick spans are lifted first, the remaining text is `html.escape()`d, strong/em (at word boundaries) and links are applied to the escaped text, then code spans are restored escaped. Only a plain relative path or an http/https URL becomes an anchor; a scheme-bearing target renders as plain text (T-3-11). Unmatched markers stay literal rather than raising.
- Both the code element and the table element sit inside their own `overflow-x:auto` container, with no nowrap and no ellipsis truncation on lesson prose, so the page body never scrolls horizontally at any viewport width. A heading deeper than `###` renders at the same Display size; no third heading size was introduced.
- `fixtures/lesson_bank.md` now exercises every block kind plus markup-shaped prose, `fixtures/lesson_shared.md` carries the ` ```math ` fence, and `tests/lesson_roundtrip.py` locks all of it with per-kind assertions plus the full-page injection check (heading, prose, table cell, list item and item stem all markup-shaped, escaped forms present and raw forms absent -- including the heading anchor id and the backlink row).

## Task Commits

Each task followed the TDD RED/GREEN cycle and was committed atomically:

1. **Task 1 RED - block-rendering tests and fixture prose** - `f9cd6fd` (test)
2. **Task 1 GREEN - fenced code, lists, tables, per-block scroll containers** - `18c7bae` (feat)
3. **Task 2 RED - inline-rendering and escaping tests** - `a09198b` (test)
4. **Task 2 GREEN - emphasis, inline code, links over escaped text** - `3f190ea` (feat)

**Plan metadata:** final docs commit (see git log)

## Files Created/Modified

- `surfaces/lesson.py` - `_protect_code()` extraction pass, `_code_block()` (the Phase 9 seam), `_render_blocks()` block classifier, `_inline()` escape-then-pattern inline pass, `_link_target_ok()` scheme gate, `_split_cells()`/`_is_separator_row()`/`_table_html()`, and the reader page's code/table/label CSS in `LESSON_TEMPLATE`
- `fixtures/lesson_bank.md` - ordered list, dash list, header pipe table, ` ```text ` fence whose content looks like inline markup, no-info fence, markup-shaped prose, and the Task 2 bold/italic/inline-code/link plus `<script>`-shaped prose paragraphs
- `fixtures/lesson_shared.md` - the ` ```math ` worked-estimate fence, the other half of the Phase 9 seam
- `tests/lesson_roundtrip.py` - Task 1 block assertions, Task 2 inline assertions, and the full-page injection check
- `.planning/phases/03-lesson-format-in-app-reader/deferred-items.md` - created; one out-of-scope discovery (pre-existing backlink placement quirk in `lesson_page()`)

## Decisions Made

- **Extract-and-placeholder before any inline pass** (the plan's prohibition, made structural): fenced blocks and inline code spans are lifted first, so a single interleaved pass can never mangle the content Phase 9 depends on being verbatim.
- **Escape before patterns, never the raw source wholesale**: structure is resolved first, text runs escaped second, and emphasis/link patterns run on already-escaped text -- a markup-shaped stem or heading can never reach the page as markup (T-3-01), and the renderer's own emitted markup is never double-escaped.
- **One sanitizer for the language class**: `lesson_slug()`'s restricted character set builds `class="language-<info>"`, so a hostile info string cannot close the attribute (T-3-10).
- **Visible `.lang` caption**: makes the muted language label concrete per 03-UI-SPEC's Color table while keeping the class as the only selector Phase 9 needs.
- **Deep headings are `<h2>` at Display size**: no third heading size for a nesting depth the grammar does not define.
- **Whole-run table fallback**: malformed pipe runs degrade to paragraphs, never to a broken table or an exception.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Plan discrepancy] The heading-with-markup fixture case moved to the injection temp-bank**
- **Found during:** Task 2 test authoring
- **Issue:** The plan's action said to add a heading containing an ampersand and an angle bracket to `fixtures/lesson_bank.md`, but `test_parse_lesson` (a 03-01 lock) asserts the fixture's heading texts are exactly `["The Airway, Step By Step", "When to Call for Help"]`; adding a third heading would break the locked parse test and add an orphan-heading warning.
- **Fix:** Kept the fixture heading list untouched and exercised the same slug-versus-visible-text split and escaping in the temp-bank injection test, which the plan's action item 6 requires anyway (heading, prose, table cell, list item and item stem all markup-shaped through the full page render).
- **Files modified:** tests/lesson_roundtrip.py (injection test)
- **Verification:** `test_full_page_escapes_markup_shaped_bank` passes; `test_parse_lesson` still passes.
- **Committed in:** a09198b / 3f190ea (Task 2 commits)

---

**Total deviations:** 1 (plan/test-constraint accommodation)
**Impact on plan:** No functional scope change -- the heading-markup assertion the plan wanted is present, just in the bank the plan's own injection check builds. No scope creep.

## Issues Encountered

- **Injection test needed a LESSON-REF tag to exercise the backlink row:** the first run failed with "escaped form missing" because the temp item had no `[LESSON-REF:]`, so `lesson_slug` was empty and no backlink row rendered. Added the tag line; the escaped stem then reached the page as intended.
- **Raw-leak fingerprints matched legitimate markup:** checking for raw `<td>`/`<li>` tripped on the renderer's own table/list tags; refined to doubled-tag sequences (`<td><td>`, `<li><li>`) and adjacent raw forms, which only leaked content can produce.
- **Out-of-scope discovery, not fixed (Rule scope boundary):** `lesson_page()`'s backlink assembly (plan 03-01 code) re-splits the rendered sections and nests section B inside section A, so both backlink lists land after the last heading's prose rather than under their own heading. Pre-existing, unrelated to this plan's renderer work; logged to `deferred-items.md` for a later plan (candidate: Phase 4 surface reconciliation or a small 03-xx follow-up).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for **03-05** (`--ref` filtering): the renderer is at full D-08 scope, so `cmd_lesson`'s `--ref` path can filter sections with no new rendering work.
- Ready for **03-06** (`spec` grammar text): the LESSON grammar's rendering contract is now real and testable.
- **Phase 9's seam is cut and inert**: `.language-<info>` classes plus `.lang` captions are on the page; KaTeX and the run button attach by selector without re-parsing or forking the renderer (LOOP-02/LOOP-03).

## Self-Check: PASSED

All created files exist (`03-04-SUMMARY.md`, `deferred-items.md`); all four task commits exist in `git log` (`f9cd6fd`, `18c7bae`, `a09198b`, `3f190ea`); full suite green; `itembank lesson fixtures/lesson_bank.md` writes a page containing a table, both list kinds, two fenced blocks and the `language-` class; `itembank lint fixtures/lesson_bank.md` exits 0; `itembank guard .` exits 0.

---
*Phase: 03-lesson-format-in-app-reader*
*Completed: 2026-08-09*
