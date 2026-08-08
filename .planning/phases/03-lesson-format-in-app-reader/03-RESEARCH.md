# Phase 3: Lesson Format & In-App Reader - Research

**Researched:** 2026-08-08
**Domain:** Hand-written markdown grammar extension + stdlib HTML rendering, inside an existing four-layer Python app (`model` / `runtime` / `server` / `surfaces`)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**LESSON grammar**

- **D-01:** The `LESSON` section lives **in the bank file, above the first `Qn.`
  marker**, opened by a `## LESSON` heading and running to the first `Qn.` line.
  Lesson subheadings are `###` inside it.
  This is not a new compatibility mechanism — it is the one that already exists.
  `model.parse_bank()` splits on `(?m)^(?=Q\d+\.)` and **discards every chunk before
  the first `Qn.`** (`model.py:27-36`), so today's parser already ignores a preamble.
  LESSON-03's "byte-identical" floor is therefore structural rather than a special
  case the plan has to defend, and a bank with no `LESSON` section is untouched code
  path for code path.
  — **Reversibility:** costly — once real banks carry lessons inline, moving to a
  sidecar-only format needs a migration over every private bank; cheap before the first
  authored lesson, not after.
- **D-02:** A second, optional source: `[LESSON-SRC: <relative/path.md>]` in the same
  preamble region names an external markdown file whose headings resolve identically.
  This is what makes one lesson shareable across the EMT, Math, and CS banks without a
  format break later. It must cost **one branch in the loader and nothing in the
  parser** — both sources produce the same heading list, and everything downstream
  (lint, reader, refs) sees one shape. If it costs more than that, the planner should
  defer it and say so; the grammar is designed so adding it later is additive.
  Path resolution is relative to the bank file, and a path escaping the bank's
  directory is a lint error, not a read.
- **D-03:** `[LESSON-REF: <heading text>]` is an item tag in the same family as
  `[OBJECTIVE:]` / `[TYPE:]` / `[ID:]`, matched by the same `(?m)^\[LESSON-REF:\s*(.*?)\]`
  shape. It names **readable heading text**, and both the lookup key and the rendered
  HTML anchor are produced by **one** `lesson_slug()` function (lowercase, collapse
  whitespace, strip punctuation). One slugifier, structurally, for the same reason
  there is one scorer — a lookup that agrees with the anchor by coincidence eventually
  disagrees.
- **D-04:** `LESSON-REF` is **excluded from `model.content_fingerprint()`**, alongside
  `objective`, `difficulty`, and the rest of the pedagogy metadata already excluded at
  `model.py:142-179`. Tagging an existing item with a lesson reference is not a content
  edit and must not raise `item.content_drift`.
  — **Reversibility:** one-way in practice — including it and later removing it would
  invalidate every stored `[HASH:]`, so the decision has to be right the first time.

**Lint**

- **D-05:** **A `LESSON-REF` naming a heading that does not exist is an ERROR, not a
  warning.** This resolves a real conflict between two governing documents, recorded
  here so it is not rediscovered as a surprise:
  - `.planning/REQUIREMENTS.md` LESSON-04 says lint *warns*.
  - `.planning/ROADMAP.md` § Phase 3 Success Criterion 3 says lint *fails* with an
    actionable message, by item number, never a render-time crash.
  The ROADMAP is the acceptance gate and the stricter statement, and an error also
  satisfies LESSON-04's weaker one. The planner should update REQUIREMENTS.md
  LESSON-04's wording as part of this phase rather than leaving the two disagreeing.
  Code: `item.lesson_ref_unknown`, field `lesson_ref`, tagged by item number.
- **D-06:** Bank-level lesson problems get a new `lesson.*` code namespace, kept in the
  same `tuple(sorted({...}))` construction as `LINT_CODES` and `SETTINGS_CODES` so
  sortedness stays structural:
  - `lesson.duplicate_heading` — error; two headings slug-collide, so a ref is ambiguous.
  - `lesson.src_unreadable` — error; `[LESSON-SRC:]` names a missing or out-of-tree file.
  - `lesson.orphan_heading` — warning; a heading no item references. Never an error: a
    lesson legitimately teaches more than it tests.

**Reader surface**

- **D-07:** The reader is **its own route**, `/lesson/<bank>` (deep-linkable as
  `/lesson/<bank>#<slug>`), served by the Phase 2 daemon and rendered by a new
  `surfaces/lesson.py`. Its required CLI twin is `itembank lesson <bank> [--ref <text>]
  [--out <file.html>]`, reaching the same render through the same call. Folding the
  lesson into `study` was considered and rejected: `study` is an item-by-item review
  surface, a lesson is a continuous document, and a separate route is what makes the
  anchor deep-link and the Phase 6 tier-0 pointer a URL rather than a UI state.
- **D-08:** Markdown rendering is a **deliberately small stdlib renderer** in
  `surfaces/lesson.py` covering headings, paragraphs, lists, tables, inline code,
  fenced code, bold/italic, and links — nothing else. No third-party markdown library
  (stdlib-only constraint), and no attempt at CommonMark completeness.
  **The Phase 9 seam is a requirement of this decision, not a nicety:** a fenced block
  carrying an info string (` ```python `, ` ```math `) must render as
  `<pre><code class="language-python">` with its source preserved verbatim and escaped
  via `html.escape`. Phase 9 then attaches the vendored KaTeX asset and the run button
  by selector, without re-parsing the lesson or forking the renderer.
- **D-09:** Links run **both ways**. Each lesson heading renders the items that
  reference it, deep-linked into the quiz at that item; each item's rendered view
  carries a "Read the lesson" link to `#<slug>`. The item→lesson link is exactly what
  Phase 6's tier 0 will return — build the pointer here, gate nothing here.
- **D-10:** The browser page holds **no key and performs no scoring**, matching the
  rule Phase 4 Success Criterion 3 states for every surface. The reader is a read-only
  render; the item links navigate, they do not answer.

### Claude's Discretion

Every decision above (D-01 through D-10) is Claude's discretion under the delegated
instruction. Three specifically invite the planner to overrule:

- D-02's `[LESSON-SRC:]` directive, if lint and the reader cannot share one code path
  cheaply. Defer it rather than fork the loader.
- D-08's renderer scope, if a stdlib table renderer proves out of proportion to what
  EMT prose actually needs (LOOP-04 wants tables, but the fixture will tell).
- D-05's REQUIREMENTS.md edit, if the project would rather record the conflict than
  resolve it. The lint severity itself is not negotiable — SC3 is the gate.

### Deferred Ideas (OUT OF SCOPE)

- **Lesson review queue with a hand-set schedule** — SCHED-04, Phase 10.
- **Tier-0 hint returning the lesson pointer** — TEACH-02, Phase 6. This phase builds
  the pointer; Phase 6 gates when it is spoken.
- **LaTeX in lessons (LOOP-02) and runnable inline code (LOOP-03)** — Phase 9. D-08
  reserves the seam and implements neither.
- **Theming the reader** — Phase 4's shared palette. The reader ships on the existing
  surface styling and inherits the palette when Phase 4 lands.
- **A lesson authoring command** (`itembank lesson --draft`) — Phase 11's closed
  authoring loop, if anywhere.

> Also locked: `03-UI-SPEC.md`'s full Copywriting Contract (every user-facing string),
> the "Lesson → Item Deep Link" mechanism (item id is `q.id`, the positional `Qn`
> identifier already used throughout `quiz_page.py`, not the opaque `[ID:]`), and the
> two additive touches to `surfaces/quiz_page.py` it identifies as required to satisfy
> D-09 (a `#<id>` fragment on `/quiz/<bank>` that pins one item first, and an
> always-visible `Read the lesson` chip in the meta row). This research does not
> restate the whole UI-SPEC; the planner reads it directly.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LESSON-01 | A bank can carry an optional `LESSON` section holding the teaching text its items test | §"The `## LESSON` preamble region" below: exact placement, `## LESSON` / `###` heading grammar, and how `model.parse_bank()`'s existing preamble discard (verified `model.py:27-36`) already ignores it |
| LESSON-02 | An item can reference a lesson heading via `LESSON-REF` | §"The `[LESSON-REF:]` item tag and the stem-terminator fix" — exact regex change to `model.py`'s stem-terminator alternation (verified `model.py:43-47`), and where `lesson_ref`/`lesson_slug` join `parse_question()`'s common dict |
| LESSON-03 | A bank with no `LESSON` section parses byte-identically to how it parses today | §"Does the preamble discard genuinely give byte-identical compatibility?" — verified against `model.py:27-36`, cross-checked against `fixtures/sample_bank.md:1-7`'s own already-discarded preamble, with the one real edge case documented (a lesson line that itself starts `Qn.`) |
| LESSON-04 | `lint` warns when a `LESSON-REF` names a heading that does not exist | Superseded by D-05 (ERROR, not warning) — implementation in §"Lint: wiring `lint()` to lesson data," including the **two test-suite couplings a naive implementation will miss**: `schemas/lint_error.schema.json`'s `code` enum (verified) and `tests/protocol_roundtrip.py`'s `prefix in ("item", "bank")` assertion (verified) |
| LESSON-05 | `spec` documents both, so an authoring agent can write lessons without seeing the source | §"Extending `model.SPEC`" — placement (`model.py:280` `SPEC` constant) and a drafted grammar block matching the existing voice |
| LESSON-06 | A lesson renders in the app as reading material, with its items reachable from it | §"The reader surface," §"Minimal stdlib markdown renderer," §"The daemon route," §"The CLI twin" |
</phase_requirements>

## Summary

This phase is almost entirely internal-code-shape work, not library research: every
external dependency question is closed by the project's own stdlib-only rule, and the
three things that actually need investigating — the parser control flow, the test/schema
coupling a new lint namespace touches, and the exact mechanics of joining an existing
route table — are answered by reading the code, not by searching for prior art.

The single most important finding is a **structural double-check on D-01/D-02's core
claim**: `model.parse_bank()`'s preamble discard (`model.py:27-36`) genuinely gives
LESSON-03's byte-identical floor for free, and the codebase already proves it —
`fixtures/sample_bank.md` has a title and two prose paragraphs above `Q1.` today, and
they are silently discarded already. No code change to `parse_bank()` or
`parse_question()`'s control flow is needed to preserve that. The one exception worth
documenting in `SPEC` is that a *lesson* line beginning with the literal pattern
`Qn.` (capital Q, digits, period, start of line) would still be silently absorbed by
the same split boundary that already exists — this is not a new bug the phase
introduces, it is an existing property of the split regex that the LESSON grammar
should tell authors to avoid rather than try to fix.

The second load-bearing finding is that **adding `[LESSON-REF:]` to `parse_question()`
requires editing the stem-terminator alternation at `model.py:43-47`, unconditionally**
— not "only if the author places it before the stem's other tags." The alternation is
a non-greedy match up to the *first* terminator it recognizes; `[LESSON-REF:]` must be
one of the recognized terminators or the stem capture will absorb it (and everything
after it, up to whatever real terminator follows) into the stem field, corrupting every
item that carries the tag.

The third finding, not called out in `03-CONTEXT.md`'s own Integration Points list, is
that **a new `lesson.*` lint code namespace touches two other files that will silently
fail if they are not also updated**: `schemas/lint_error.schema.json`'s `code` property
is a closed `enum` (verified, currently 26 entries, no `lesson.*` member), and
`tests/protocol_roundtrip.py:test_lint_codes_declared()` hard-codes
`prefix in ("item", "bank")`. Both are exercised by CI (`.github/workflows/ci.yml`'s
"Runtime output matches published schema" and "Test suite" steps) against real lint
output, so a lesson-lint code introduced without touching both of these fails the build
the moment a fixture bank exercises it, not the moment it's written.

**Primary recommendation:** Implement the LESSON grammar as two new, independent
functions in `model.py` — `lesson_slug(text)` (pure) and `parse_lesson(bank_path)` (I/O,
mirrors `model.load()`'s open-and-parse shape but returns lesson data instead of
questions) — and leave `model.load()` and `model.parse_bank()` completely untouched.
Wire `[LESSON-REF:]` into `parse_question()`'s existing tag family (one line in the
common dict, one alternation entry). Extend `model.lint(questions, lesson=None)` with
one optional, backward-compatible parameter so every existing caller keeps working
unchanged. Add the new `lesson.*` codes to `LINT_CODES`'s existing set literal, and in
the same commit update `schemas/lint_error.schema.json`'s enum and
`tests/protocol_roundtrip.py`'s prefix tuple. Add `/lesson/<bank>` to `daemon.ROUTES`
and `daemon.ROUTE_CLI` following `STUDY_GET_RE`/`handle_study_get`'s exact shape. Write
the renderer as a small line/block scanner in `surfaces/lesson.py`, protecting fenced
code from inline-formatting regexes by extraction-and-placeholder rather than
interleaved regex passes.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `LESSON`/`LESSON-REF` grammar parsing, slug generation, lint validation | API / Backend (`model.py`) | — | Pure parsing/validation logic with no rendering concern, matching `model.py`'s existing role as the one parser (verified: `model.py` has zero imports from `runtime`/`surfaces`) |
| Lesson content storage | Database / Storage (bank markdown file, or an external `[LESSON-SRC:]` file) | — | No database exists in this project (verified: `CLAUDE.md` "No database"); markdown-on-disk is the one storage tier |
| Server-rendered lesson document (`/lesson/<bank>`) | Frontend Server / SSR (`surfaces/lesson.py`, dispatched by `surfaces/daemon.py`) | — | One-shot HTML generation with no client fetch, mirroring `surfaces/study.py:study_page()` and `surfaces/quiz.py:page_for()`'s existing shape (verified) |
| Lesson→item backlinks, item→lesson chip navigation | Browser / Client (plain `<a href>`, no JS state) | Frontend Server / SSR (hrefs are computed server-side at render time) | Both links are static anchors; D-10 forbids any client-side scoring or key material, so no client logic is needed beyond the one additive `location.hash` splice in `quiz_page.py` (already scoped by `03-UI-SPEC.md`) |
| CLI twin (`itembank lesson`) | API / Backend (`surfaces/cli.py` + `surfaces/lesson.py`) | — | No browser tier at all; same render function the daemon route calls, per D-07 |

## Standard Stack

Not applicable in the conventional sense — `CLAUDE.md`'s constraint is explicit and
non-negotiable for this phase: **Python standard library only, no install step, no
third-party markdown library.** There is no library selection to research.

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `re` (stdlib) | bundled with Python 3.11+ | LESSON preamble/heading extraction, `LESSON-REF` tag parsing, slug generation | Every existing parsing function in `model.py` is `re`-based (verified: `grab()`, `parse_question()`, `lint()`); a second parsing idiom would fork the format contract |
| `html` (stdlib) | bundled | Escaping every literal fragment of rendered lesson markdown | `quiz_page.py`'s own `esc()` and `daemon.py`'s `html.escape()` calls are the established discipline (verified `surfaces/daemon.py:449`, `quiz_page.py:125`) |
| `collections.namedtuple` (stdlib) | bundled | If the lesson parser returns a structured record type, matching `model.LintError`'s own `namedtuple` shape (verified `model.py:373-382`) | Keeps the new data shape consistent with the existing `LintError` convention rather than an ad hoc dict |

### Supporting

None — no new supporting libraries. `model.collapse()` (verified `model.py:133-139`)
is reused by `lesson_slug()` rather than writing a second whitespace normalizer, per
the existing code_context note.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-written stdlib markdown renderer | `markdown`, `mistune`, `commonmark` (PyPI packages) | Forbidden outright by `CLAUDE.md`'s stdlib-only constraint and by D-08's explicit "no third-party markdown library." Not evaluated further. |

**Installation:** None. No new dependency is added by this phase.

**Version verification:** Not applicable — no package versions to verify.

## Package Legitimacy Audit

**Not applicable.** This phase installs no external packages of any kind (stdlib-only
by `CLAUDE.md`'s explicit constraint, reaffirmed by D-08). The Package Legitimacy Gate
protocol is skipped in its entirety; there is nothing to run `npm view`/`pip index
versions`/`cargo search` against.

**Packages removed due to `[SLOP]` verdict:** none — no packages were proposed.
**Packages flagged as suspicious `[SUS]`:** none.

## Architecture Patterns

### System Architecture Diagram

```
                    Bank markdown file (.md)
                    ┌─────────────────────────────┐
                    │ (optional prose/title)       │
                    │ ## LESSON                     │  <- new: preamble region,
                    │ ### Heading A                 │     above the first Qn.
                    │  ...prose, lists, tables...   │
                    │ [LESSON-SRC: shared.md]  (opt)│  <- optional external file
                    │ Q1. ...                        │
                    │ [LESSON-REF: Heading A]       │  <- new: item tag
                    │ ...                             │
                    └───────────────┬───────────────┘
                                    │ open() + re
                                    v
          model.py (API / Backend layer -- pure parsing + validation)
          ┌──────────────────────────────────────────────────────────┐
          │ parse_bank(text)      -- UNCHANGED. Still discards        │
          │                          everything before Q1 (27-36).    │
          │ parse_question(ch)    -- gains one dict key               │
          │                          (lesson_ref/lesson_slug) and     │
          │                          one terminator-alternation entry │
          │                          (43-47).                         │
          │ parse_lesson(path)    -- NEW. Reads the preamble region   │
          │                          (+ optional [LESSON-SRC:] file), │
          │                          returns {headings:[...], ...}.   │
          │ lesson_slug(text)     -- NEW. Pure. Lookup key == anchor  │
          │                          id, one function (D-03).         │
          │ lint(qs, lesson=None) -- gains one optional kwarg; when   │
          │                          given, adds item.lesson_ref_-    │
          │                          unknown (per item) and the three │
          │                          lesson.* bank-level codes.       │
          └───────────────┬───────────────────────┬────────────────┘
                          │ qs (unchanged shape)   │ lesson dict
                          v                        v
     runtime.py (public_item gains "lesson_slug")   surfaces/lesson.py (NEW)
          │                                          │ lesson_page(bank_path, qs, lesson)
          │                                          │  -- minimal stdlib markdown renderer
          │                                          │  -- backlinks per heading
          v                                          v
  surfaces/quiz.py -> quiz_page.py (SSR)      surfaces/daemon.py
     -- chips() gains a "Read the lesson"        -- GET /lesson/<bank> route,
        chip when q.lesson_slug is set              resolved via handler.banks
     -- bootstrap gains #<id> hash-splice           allowlist, same send_not_found
        (deep-link FROM the reader)                  404 convention as /study/<stem>
          │                                          │
          v                                          v
      Browser: quiz page                      Browser: lesson reader page
      (one item, one card, "Read the           (continuous document, backlinks
       lesson" -> /lesson/<bank>#<slug>)        -> /quiz/<bank>#<id>, new tab
                                                 for the item-side chip, same tab
                                                 for the reader-side backlink)
```

### Recommended Project Structure

No new top-level directories. Everything lands inside the existing four-layer shape:

```
model.py              # + lesson_slug(), parse_lesson(), lesson_ref in
                       #   parse_question(), lesson=None kwarg on lint(),
                       #   lesson.* codes in LINT_CODES, LESSON grammar in SPEC
runtime.py             # + "lesson_slug" key in public_item()'s output dict
surfaces/
├── lesson.py           # NEW -- lesson_page() renderer + cmd_lesson, mirrors
│                        #   quiz.py/study.py's page_for()/study_page() shape
├── daemon.py            # + LESSON_GET_RE, handle_lesson_get, one ROUTES/
│                         #   ROUTE_CLI entry
├── quiz_page.py           # + chips() gains a lesson chip branch, bootstrap
│                          #   gains the #<id> hash-splice (03-UI-SPEC.md's
│                          #   "Lesson -> Item Deep Link" mechanism)
├── cli.py                  # + `lesson` subparser
schemas/
└── lint_error.schema.json  # + 4 new codes in the `code` enum (see Pitfall 1)
fixtures/
└── lesson_bank.md           # NEW -- synthetic fixture with a ## LESSON
                              #   section, >=1 LESSON-REF, and (recommended)
                              #   a second fixture or an addition to
                              #   broken_bank.md exercising the ERROR path
tests/
└── lesson_roundtrip.py       # NEW -- follows tests/*_roundtrip.py's direct-
                               #   execution convention; picked up by CI's
                               #   generic `for t in tests/*.py` loop with
                               #   zero registration elsewhere
```

### Pattern 1: The `## LESSON` preamble region and `[LESSON-SRC:]`

**What:** An optional `## LESSON` heading placed anywhere before the first `Qn.` line,
containing `###` subheadings and prose/lists/tables/code, with an optional
`[LESSON-SRC: <relative/path.md>]` line naming an external file whose own `###`
headings resolve into the same heading list.

**When to use:** Any bank that wants reading material linked to its items. Multiple
banks (EMT, Math, CS) can point `[LESSON-SRC:]` at one shared file rather than
duplicating prose.

**Verified code basis:**
```python
# model.py:27-36 -- UNCHANGED by this phase. Verified by direct read.
def parse_bank(text):
    """Split on `Qn.` markers and parse each block into a question dict."""
    questions = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if not re.match(r"Q\d+\.", ch.strip()):
            continue
        q = parse_question(ch)
        if q:
            questions.append(q)
    return questions
```
`re.split(r"(?m)^(?=Q\d+\.)", text)` is a zero-width split: only `chunks[0]` can ever
fail the `not re.match(r"Q\d+\.", ...)` test, because every later chunk begins exactly
at a line that matched the lookahead. So the *only* chunk `continue`d away is the
preamble — proven directly in the fixture already committed to this repo:

```
# fixtures/sample_bank.md:1-7 -- VERIFIED, quoted verbatim
# Sample bank (synthetic)

Fully invented content for a fictional municipal water-treatment operator
certification. It exists to exercise all five item types and to give `lint`
something that passes cleanly. It is not derived from any real course, exam, or
textbook, and no real question bank belongs in this repository.

Q1. An operator notices the chlorine residual...
```
This title line and two-paragraph description are preamble *today*, already discarded
by the unmodified function above. A `## LESSON` section dropped into that same region
is discarded by the exact same code path — no new branch, no new regex in
`parse_bank()` itself.

**New function, mirroring `model.load()`'s shape rather than forking it:**
```python
def parse_lesson(bank_path):
    """Read a bank file's preamble region and return its lesson structure, or
    None if it carries no `## LESSON` section. Never touches parse_bank()'s
    own control flow (model.py:27-36 stays byte-for-byte); this is a second,
    independent read over the same file for a different purpose, the same
    way `model.load()` is a second read `surfaces/lesson.py` performs
    alongside every existing `model.load()` call, not a replacement for it.
    """
    text = open(bank_path, encoding="utf-8").read()
    # Mirror parse_bank()'s own boundary detection exactly, rather than a
    # naive `re.split(..., maxsplit=1)[0]` -- see Pitfall 2 below for why
    # naive maxsplit=1 silently truncates a lesson containing a `Qn.`-shaped
    # prose line.
    pre_chunks = []
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()) and parse_question(ch) is not None:
            break
        pre_chunks.append(ch)
    preamble = "".join(pre_chunks)

    m = re.search(r"(?m)^\[LESSON-SRC:\s*(.*?)\s*\]", preamble)
    if m:
        bank_dir = os.path.dirname(os.path.abspath(bank_path)) or "."
        src_path = os.path.abspath(os.path.join(bank_dir, m.group(1)))
        # Precedent: surfaces/migrate.py's scan_legacy() escape check
        # (verified surfaces/migrate.py:241-248), same shape reused here
        # rather than invented fresh.
        if src_path != bank_dir and not src_path.startswith(bank_dir + os.sep):
            return {"error": "lesson.src_unreadable",
                    "detail": "%s escapes the bank's directory" % m.group(1)}
        try:
            preamble = open(src_path, encoding="utf-8").read()
        except OSError as exc:
            return {"error": "lesson.src_unreadable", "detail": str(exc)}

    lesson_block = re.search(r"(?m)^##\s+LESSON\s*$(.*)", preamble, re.S)
    if not lesson_block:
        return None
    headings = []
    for m in re.finditer(r"(?m)^###\s+(.+?)\s*$", lesson_block.group(1)):
        headings.append({"text": m.group(1), "slug": lesson_slug(m.group(1))})
    return {"headings": headings, "body": lesson_block.group(1)}
```
This is a **draft for the planner to size**, not implementation-ready code — but every
regex and control-flow claim in it is grounded against the verified `model.py` shown
above and against `surfaces/migrate.py:241-248` (verified) for the path-escape check.

### Pattern 2: The `[LESSON-REF:]` item tag and the stem-terminator fix

**What:** `[LESSON-REF: <heading text>]`, parsed the same way `[OBJECTIVE:]` already
is, added to `parse_question()`'s common dict and to the stem-terminator alternation.

**Verified code basis — the exact regex that must change:**
```python
# model.py:43-47 -- VERIFIED, quoted verbatim. This is the ONE regex the
# phase's own emphasis item #1 asks to be checked precisely.
stem = grab(
    r"Q\d+\.\s*(.*?)\s*(?:\(difficulty:|\n\[OBJECTIVE|\n\[TYPE|\n\[SELECT"
    r"|\n\[CATEGORIES|\n\[ID|\n\[HASH|\n[A-H]\)|\nROW\)|\nITEM\)|\nSTEP\)"
    r"|\nMODEL:|\nRUBRIC:|\nWHY BEST:)",
    ch, re.S)
```
`(.*?)` is non-greedy with `re.S` (dot matches newline), so it captures the *shortest*
run of text up to the *first* alternative in the terminator group that appears in the
block. **If `[LESSON-REF:]` is not one of those alternatives, and an author places it
anywhere before the first tag that *is* recognized** (the natural place to put it,
next to `[OBJECTIVE:]`), the stem capture does not stop at the `[LESSON-REF:]` line —
it keeps consuming past it, through the `[LESSON-REF: ...]` text itself, until it
reaches the next real terminator (e.g. `[OBJECTIVE:` or `A)`). The resulting `stem`
field is corrupted: it now contains the real stem *plus* the literal
`[LESSON-REF: Heading text]` line, verbatim, as trailing "stem" text shown to the
learner. This is not a hypothetical edge case; it is guaranteed to happen for the
natural authoring order (tag right after the difficulty parenthetical, alongside
`[OBJECTIVE:]`).

**Required fix — add exactly one alternative:**
```python
stem = grab(
    r"Q\d+\.\s*(.*?)\s*(?:\(difficulty:|\n\[OBJECTIVE|\n\[TYPE|\n\[SELECT"
    r"|\n\[CATEGORIES|\n\[ID|\n\[HASH|\n\[LESSON-REF|\n[A-H]\)|\nROW\)"
    r"|\nITEM\)|\nSTEP\)|\nMODEL:|\nRUBRIC:|\nWHY BEST:)",
    ch, re.S)
```
Placement inside the alternation is arbitrary (regex alternation tries each in
left-to-right order at *every* position, not "in list order across the whole match" —
what matters is that it's present at all, not where). This fix is required
**regardless of where an author places the tag in the item block**, because the
terminator list has to recognize every possible next-tag boundary, not just the one an
author happens to choose.

**The tag itself**, matching `[OBJECTIVE:]`'s exact shape (verified `model.py:54`):
```python
"lesson_ref": grab(r"(?m)^\[LESSON-REF:\s*(.*?)\]", ch),
"lesson_slug": lesson_slug(grab(r"(?m)^\[LESSON-REF:\s*(.*?)\]", ch)) or "",
```
Both keys added to `parse_question()`'s `common` dict (verified `model.py:48-62`),
following `item_id`/`content_hash`'s existing "empty until assigned" comment
convention.

### Pattern 3: `content_fingerprint()` exclusion is already free (D-04) — verified, not assumed

```python
# model.py:142-177 -- VERIFIED, read in full this session. content_fingerprint()
# reads exactly these q dict keys and no others across every branch:
#   q["type"], q["stem"], q["opts"], q["correct"], q["select"] (mc/multi)
#   q["cats"], q["rows"] (table/dnd)
#   q["steps"] (build)
#   q["model"], q["rubric"] (short)
```
`lesson_ref`/`lesson_slug` are never read anywhere in this function. D-04's exclusion
requires **zero code change** to `content_fingerprint()` — the only risk is a future
edit that accidentally adds `q.get("lesson_ref")` to the `parts` list, which the
planner should flag as a one-way mistake (D-04's own stated reversibility note: doing
this and undoing it later invalidates every stored `[HASH:]`). Recommend a one-line
regression assertion in `tests/lesson_roundtrip.py`: fingerprint an item with and
without an identical `[LESSON-REF:]` value and assert the two hashes are equal.

### Pattern 4: Lint — wiring `lint()` to lesson data

**What:** `model.lint(questions, lesson=None)` — one new optional, backward-compatible
parameter. Every existing call site (`cmd_lint`, `cmd_build`, `cmd_serve`, `cmd_study`,
`tests/protocol_roundtrip.py`, CI's own inline `python itembank.py lint ...` calls —
verified across `surfaces/*.py` and `.github/workflows/ci.yml`) keeps calling
`lint(qs)` unchanged and keeps working, because `lesson=None` skips every lesson check
entirely.

**When `lesson` is given** (the CLI's `cmd_lint` is the one call site that needs to
change, since it's the only one that both loads a bank *and* is the acceptance gate
for SC3):
- Per item (inside the existing `for idx, q in enumerate(questions, 1):` loop,
  verified `model.py:416`): if `q.get("lesson_ref")` is truthy and its slug is not in
  `{h["slug"] for h in lesson["headings"]}` (or `lesson is None` entirely — a
  `LESSON-REF` with no `## LESSON` section at all in the bank), emit
  `item.lesson_ref_unknown`, field `lesson_ref`, as an **error** (D-05).
- Bank-level, once: for each pair of headings whose slugs collide, emit
  `lesson.duplicate_heading` (error). For each heading with zero referencing items,
  emit `lesson.orphan_heading` (warning). If `parse_lesson()` returned an `"error"` key
  (unreadable/out-of-tree `[LESSON-SRC:]`), emit `lesson.src_unreadable` (error).

**Pitfall 1 — the two couplings a naive implementation will miss (verified, both
exercised by CI):**

1. `schemas/lint_error.schema.json`'s `code` property is a **closed JSON Schema
   `enum`**, verified read in full this session:
   ```json
   {"code": {"type": "string", "enum": [
       "bank.answer_position_skew", "item.content_drift", ... 26 entries total,
       no "lesson.*" or "item.lesson_ref_unknown" member present
   ]}}
   ```
   `tests/protocol_roundtrip.py` (verified, lines 401-407) validates *every live lint
   entry* from `itembank lint --json` against this schema via `schema_validate.py`.
   CI's own "Runtime output matches published schema" step (verified
   `.github/workflows/ci.yml:62-64`) does the same against `fixtures/broken_bank.md`.
   **A `lesson.*`/`item.lesson_ref_unknown` code that reaches real lint output without
   also being added to this enum fails CI**, not at write time but the first time a
   fixture bank actually triggers the code.
2. `tests/protocol_roundtrip.py:test_lint_codes_declared()` (verified, lines 83-91)
   hard-codes:
   ```python
   for c in codes:
       prefix = c.split(".", 1)[0]
       if prefix not in ("item", "bank"):
   ```
   A `lesson.*` code added to `LINT_CODES` without extending this tuple to
   `("item", "bank", "lesson")` fails this assertion on the very next test run,
   independent of whether any fixture ever exercises the code.

Both fixes are one-line each; the risk is that they are two files away from
`model.py` and easy to miss in the plan's own file list.

### Pattern 5: The reader surface (daemon route + CLI twin)

**Verified route-table shape, mirrored exactly from `handle_study_get`:**
```python
# surfaces/daemon.py:545-556 -- VERIFIED, quoted verbatim (the pattern to mirror)
def handle_study_get(handler, stem):
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    qs = load(path)
    page = study.study_page(path, qs)
    handler.send_html(page.encode("utf-8"))
```
The new route follows this exactly:
```python
LESSON_GET_RE = re.compile(r"^/lesson/(?P<stem>[^/]+)$")
# ... in ROUTES, grouped with the other stem-parameterised GET routes:
    ("GET", STUDY_GET_RE, "handle_study_get"),
    ("GET", LESSON_GET_RE, "handle_lesson_get"),
# ... in ROUTE_CLI (REQUIRED -- tests/daemon_roundtrip.py:check_route_cli_inventory,
# verified, asserts ROUTE_CLI's key set equals ROUTES' (method, pattern) set, and
# greps surfaces/cli.py for a literal `add_parser("lesson"` string):
    ("GET", LESSON_GET_RE): "lesson",

def handle_lesson_get(handler, stem):
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    qs = load(path)
    lesson = parse_lesson(path)
    page = lesson_mod.lesson_page(path, qs, lesson)
    handler.send_html(page.encode("utf-8"))
```
`handler.banks`/`handler.send_not_found(stem)` is the exact identifier-addressed 404
convention every other stem route already uses (verified `surfaces/daemon.py:906-912`)
— no new 404 body, no new allowlist mechanism; `03-UI-SPEC.md`'s Copywriting Contract
already locks this ("Reuses the daemon's existing `handler.send_not_found(stem)` 404
text verbatim").

**CLI twin**, following `study`'s `sub.add_parser` shape (verified
`surfaces/cli.py:257-261`) but with UI-SPEC's own locked signature
(`itembank lesson <bank> [--ref <text>] [--out <file.html>]` — note `--out` is a flag
here, unlike `study`'s positional `out`):
```python
s = sub.add_parser("lesson", help="render the LESSON section as reading material")
s.add_argument("bank")
s.add_argument("--ref", help="render only the section matching this heading text")
s.add_argument("--out", help="write HTML here instead of printing the summary line")
s.set_defaults(fn=cmd_lesson)
```

### Anti-Patterns to Avoid

- **A second `Qn.`-splitting regex for the lesson parser.** `parse_lesson()` must
  reuse `parse_bank()`'s exact boundary logic (see Pattern 1's draft), not
  `re.split(..., maxsplit=1)[0]` — see Pitfall 2 for the concrete failure this causes.
- **Reading lesson data through `model.load()`.** `load()`'s return shape (a bare list
  of question dicts) is depended on by every existing surface; do not change it to a
  tuple or add a second return value. `parse_lesson()` is a parallel, independent read.
- **Computing the lesson slug in more than one place.** `lesson_slug()` must be the one
  function both the lint duplicate-heading check and the renderer's anchor-id
  generation call — a slug computed inline in two places is the "coincidence today,
  drift tomorrow" problem D-03 explicitly names.
- **Passing raw bank-authored text into HTML without `html.escape`.** Every existing
  render path (`quiz_page.py`'s `esc()`, `daemon.py`'s `html.escape()` calls) treats
  bank content as untrusted-for-markup even though the project's threat model is "one
  local user, no adversary" (verified `model.py:155-156`'s own comment on
  `content_fingerprint`) — the discipline is about correctness (a stray `<` in a stem
  must not break the page), not a security boundary. The lesson renderer must match
  this discipline for every literal text run.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Whitespace normalization for slugs | A second `" ".join(s.split())` idiom | `model.collapse()` (verified `model.py:133-139`) | Already exists, already the exact semantic `lesson_slug()` needs (collapse whitespace, preserve case before lowering) |
| Path-escape checking for `[LESSON-SRC:]` | A fresh `os.path` containment check | The pattern at `surfaces/migrate.py:241-248` (verified: `os.path.abspath` + `startswith(base_abs + os.sep)`) | Identical problem (an optional path override that must resolve inside a base directory) already solved and tested once in this codebase; a second implementation risks a subtly different (and possibly wrong) edge case, e.g. forgetting the `+ os.sep` suffix that prevents `/base-evil` from passing a naive `startswith(base)` check |
| A full CommonMark-compatible markdown parser | Any hand-rolled attempt at spec completeness (nested lists to arbitrary depth, reference-style links, HTML passthrough, etc.) | The deliberately small D-08 scope: headings, paragraphs, lists, tables, inline code, fenced code, bold/italic, links — nothing else | CommonMark's own spec runs to hundreds of edge cases (footnotes, link reference definitions, entity references, precise list-tightness rules); D-08 explicitly rejects completeness in favor of exactly what EMT/Math/CS lesson prose needs, and getting the fenced-code-block shape right for Phase 9 matters far more than table alignment-row edge cases |

**Key insight:** every "don't hand-roll" item above already has a working precedent
*inside this repository* — the discipline this phase should follow is "search
`model.py`/`surfaces/migrate.py` before writing a new primitive," not "reach for a
library," since libraries are off the table entirely.

## Common Pitfalls

### Pitfall 1: The stem-terminator alternation, unmodified, silently corrupts every item's stem

**What goes wrong:** Every `Qn.` item that carries `[LESSON-REF: ...]` renders a stem
that includes the literal tag text as trailing prose, visible to the learner in the
quiz page's `<p class="stem">`.

**Why it happens:** `model.py:43-47`'s stem-capture regex terminates on a fixed list
of alternatives; an unrecognized tag is just more "stem" content to a non-greedy `.*?`
that has nowhere else to stop.

**How to avoid:** Add `\n\[LESSON-REF` to the alternation (Pattern 2, verified above).

**Warning signs:** A fixture bank's rendered quiz page shows `[LESSON-REF: ...]` as
literal text inside the stem paragraph; `content_fingerprint()`'s stem-derived hash
changes when only a `LESSON-REF` was added (it should not, since `content_fingerprint`
never reads `lesson_ref` directly — but a corrupted `stem` field *is* read by it, so
this pitfall would masquerade as a D-04 violation if not caught first).

### Pitfall 2: Naive preamble extraction silently truncates a lesson

**What goes wrong:** A lesson author writes prose containing a line that happens to
start with a capital `Q`, digits, and a period at the start of a line (e.g. copying an
NREMT-style scenario stem into the lesson text as an illustrative example, or a
numbered list styled `Q1. ...`). If `parse_lesson()` is implemented as
`re.split(r"(?m)^(?=Q\d+\.)", text, maxsplit=1)[0]`, that line becomes the *first*
split boundary `re.split` finds, and everything after it — the rest of the intended
lesson — is silently dropped from the extracted preamble, even though
`parse_bank()`'s own `qs` list is completely unaffected (it correctly skips that
false-positive chunk because `parse_question()` returns `None` for it, per Pattern 1's
verified proof of `parse_bank()`'s robustness).

**Why it happens:** `re.split` with `maxsplit=1` stops after the *first* pattern
match, whatever it is — it has no concept of "the first match that turns out to be a
real question," which is exactly what `parse_bank()`'s own per-chunk loop checks for.

**How to avoid:** Mirror `parse_bank()`'s loop exactly (Pattern 1's draft
`parse_lesson()`): iterate every chunk from the *unbounded* split, and only stop
accumulating into the preamble once a chunk both matches `Q\d+\.` at its start *and*
`parse_question()` successfully parses it. This is the same two-condition check
`parse_bank()` already performs, just inverted to "collect until" instead of "skip
before continuing."

**Warning signs:** A fixture lesson containing an illustrative "Q1. ..." example
sentence renders a truncated lesson body in `/lesson/<bank>` while `itembank lint`
reports the full, correct item count — the two disagreeing about "how long is this
document" is the tell. Document this as a known constraint in `SPEC`'s LESSON grammar
text (authors should avoid a line starting with `Qn.` inside lesson prose) rather than
try to eliminate the ambiguity in code, since eliminating it entirely would require
`parse_bank()`'s own split boundary to become context-sensitive, which is out of this
phase's scope and would itself risk LESSON-03's compatibility floor.

### Pitfall 3: The two silent lint-code-namespace couplings

Already covered in full under Pattern 4's "Pitfall 1" (kept there since it's directly
adjacent to the lint implementation code); restated here as a checklist item because
it is easy for a plan's file list to miss `schemas/lint_error.schema.json` and
`tests/protocol_roundtrip.py` entirely, since neither is `model.py` or a `surfaces/`
file:

- [ ] `schemas/lint_error.schema.json`'s `code` enum gains all four new codes
- [ ] `tests/protocol_roundtrip.py:test_lint_codes_declared()`'s
      `prefix in ("item", "bank")` becomes `prefix in ("item", "bank", "lesson")`

### Pitfall 4: `itembank.py`'s explicit re-export list

**What goes wrong:** Any new public symbol added to `model.py` (`lesson_slug`,
`parse_lesson`) is invisible to `import itembank; itembank.lesson_slug(...)` and to
anything relying on `itembank.__all__` unless it is also added to `itembank.py`'s
explicit `from model import (...)` line and its `__all__` list.

**Why it happens:** `itembank.py` (verified, lines 54-56 and 87-120) hand-lists every
re-exported name from `model.py`/`runtime.py`/etc. — there is no `from model import *`
anywhere in this codebase (matching `CLAUDE.md`'s "No barrel files" convention).

**How to avoid:** Add `lesson_slug`, `parse_lesson` (and any new lesson-specific
constant, e.g. a `LESSON_CODES` tuple if the planner chooses to expose one separately
from `LINT_CODES`) to both the import statement and `__all__`, alphabetically
positioned per the existing convention.

**Warning signs:** `tests/protocol_roundtrip.py` or any test importing via
`import itembank` and referencing the new function by its `itembank.`-qualified name
raises `AttributeError` even though `from model import lesson_slug` works fine inside
`surfaces/lesson.py` directly.

### Pitfall 5: The "Read the lesson" chip's href has no server behind it under `itembank build`

**What goes wrong:** `03-UI-SPEC.md` locks the chip's href as `/lesson/<bank>#<slug>`,
opened in a new tab. Under `itembank serve`/`itembank daemon`, that path resolves
against a real daemon and works. Under `itembank build` (the static, file://,
no-process offline page — verified `surfaces/quiz.py:cmd_build()`), there is no server
at all; a `file://.../bank_quiz.html` page's relative link to `/lesson/<bank>` resolves
against the filesystem root, not a daemon, and 404s (or opens nothing, depending on the
browser).

**Why it happens:** `public_item()`'s new `lesson_slug` field is included in the item
payload identically whether `page_for()` is called with `serve=True` or `serve=False`
(verified `surfaces/quiz.py:page_for()`, line 24: `page_item(q, reveal=reveal,
offline=not serve)` — both paths call the same `public_item()` underneath), so the
chip renders identically in both contexts even though only one of them has anything at
`/lesson/<bank>` to link to.

**How to avoid — flagged as an open question, not resolved here:** either (a) accept
the dead link under `build` as a known, documented limitation (consistent with
`build`'s existing "no server, no persistence" nature — the static page already can't
POST answers under `serve`'s scoring path either), or (b) suppress the chip when
`offline=True` (i.e., pass an `offline` flag through to `public_item()` or filter it at
the `page_for()`/`chips()` layer). `03-UI-SPEC.md` does not address this distinction.
Recommend the planner pick (a) for minimal surface area — matching this project's
existing pattern of `build`'s page being the "best-effort, no-process" surface — and
note the accepted limitation directly beside the chip's implementation, but this is a
genuine planner decision.

## Code Examples

### Verified: `model.py`'s existing tag-parsing shape `[LESSON-REF:]` mirrors

```python
# model.py:54 -- VERIFIED, the exact precedent [LESSON-REF:] copies
"objective": grab(r"\[OBJECTIVE:\s*(.*?)\]", ch),
```

### Verified: the path-escape check `[LESSON-SRC:]` should reuse

```python
# surfaces/migrate.py:241-248 -- VERIFIED, quoted verbatim
base_abs = os.path.abspath(base)
if legacy_dir:
    resolved = os.path.abspath(legacy_dir)
    if resolved != base_abs and not resolved.startswith(base_abs + os.sep):
        raise MigrationScopeError(
            "migrate: --legacy-dir %r resolves to %r, outside --base %r; "
            "migration inputs must stay inside the given base, never an "
            "arbitrary path (T-1-03)" % (legacy_dir, resolved, base_abs))
```

### Verified: `LINT_CODES`'s set-then-sorted construction, the pattern D-06 extends

```python
# model.py:389-400 -- VERIFIED, quoted verbatim
LINT_CODES = tuple(sorted({
    "item.duplicate_number", "item.select_mismatch", "item.correct_unknown_option",
    "item.too_few_options", "item.missing_second_best", "item.distractor_missing",
    "item.distractor_no_would_be", "item.too_few_categories", "item.row_category_unknown",
    "item.too_few_rows", "item.missing_distractor_notes", "item.too_few_steps",
    "item.duplicate_steps", "item.missing_model", "item.too_few_rubric_points",
    "item.model_too_long", "item.rubric_point_too_long", "item.missing_why_best",
    "item.missing_trap", "item.low_confidence", "item.duplicate_stem",
    "item.missing_id", "item.duplicate_id", "item.missing_hash",
    "item.content_drift", "item.objective_unnamespaced",
    "bank.answer_position_skew",
}))
```
The four new codes join this same literal set (recommended, since `lint()` is the one
function that emits them — do not create a second `LESSON_LINT_CODES` tuple unless the
planner has a specific reason `SETTINGS_CODES`-style separation is warranted; here,
unlike settings, the codes come out of the *same* `lint()` function and the *same*
`--json` envelope, so one set is the simpler, more honest shape):
```python
LINT_CODES = tuple(sorted({
    # ...existing 26 entries unchanged...
    "item.lesson_ref_unknown",
    "lesson.duplicate_heading", "lesson.src_unreadable", "lesson.orphan_heading",
}))
```

### Verified: `public_item()`'s current output shape, the extension point for `lesson_slug`

```python
# runtime.py:27-48 -- VERIFIED, quoted verbatim (relevant portion)
def public_item(q, shuffle_seed=0):
    """Return an item safe to show before the learner answers."""
    out = {"schema_version": ITEM_VERSION, "id": q["id"], "number": q["number"],
           "type": q["type"], "stem": q["stem"], "objective": q.get("objective", ""),
           "difficulty": q.get("difficulty", "")}
    # ... type-specific fields ...
    return out
```
Add `out["lesson_slug"] = q.get("lesson_slug", "")` (or omit the key entirely when
empty, matching `objective`/`difficulty`'s own "empty string when absent" convention
rather than a conditional key — `chips()`'s new JS branch should check `if(q.lesson_slug)`
either way). Note `runtime.py` has zero imports from `model.py` (verified: its only
imports are `collections, json, os, sys`), so `lesson_slug` must already be computed
*inside* `q` by `model.parse_question()` before `public_item()` ever sees it — `runtime.py`
cannot call `model.lesson_slug()` itself without violating the project's own
"model has no dependents, runtime depends on model only indirectly through surfaces"
architecture rule (per `.claude/CLAUDE.md`'s Layers table). This is why Pattern 2 puts
the `lesson_slug` computation inside `parse_question()`'s common dict, not in `runtime.py`.

### Verified: `chips()`'s existing shape, the extension point for the "Read the lesson" chip

```javascript
// surfaces/quiz_page.py:190-197 -- VERIFIED, quoted verbatim
function chips(q){
  let h = `<span class="chip type">${LABEL[q.type]||q.type}</span>`;
  if(q.type==="short") h += `<span class="chip aon">graded by a marker, not by this page</span>`;
  else if(q.type!=="mc") h += `<span class="chip aon">no partial credit</span>`;
  if(q.objective) h += `<span class="chip">${esc(q.objective)}</span>`;
  if(q.difficulty) h += `<span class="chip">${esc(q.difficulty)}</span>`;
  return h;
}
```
New branch (per `03-UI-SPEC.md`'s locked copy and mechanism): needs the bank stem to
build `/lesson/<stem>#<slug>`, which is not currently threaded into the JS the way
`__POST__` (`"/quiz/%s/answer" % stem`) already is. Recommend a new
`page_for()` parameter/template substitution — `__LESSON_BASE__` = `"/lesson/%s" %
stem`, substituted the same way `__POST__` is (verified `surfaces/quiz.py:page_for()`,
lines 32-38's `.replace()` chain) — so `chips()` can do:
```javascript
if(q.lesson_slug) h += `<a class="chip lesson" target="_blank"
  href="${LESSON_BASE}#${q.lesson_slug}">Read the lesson</a>`;
```

## State of the Art

Not applicable in the usual sense (no external library landscape to survey). The one
relevant "state of the art" fact is internal: this is the **first** markdown-rendering
surface in the codebase. Every existing page (`quiz_page.py`, `study.py`'s
`STUDY_TEMPLATE`, `daemon.py`'s `INDEX_TEMPLATE`/`REPORT_TEMPLATE`) is hand-authored
HTML with Python string templating and zero markdown parsing — `surfaces/lesson.py`'s
renderer has no precedent to mirror inside this repository, unlike almost everything
else this phase touches. This was independently confirmed by `03-UI-SPEC.md`'s own
"Registry Safety" section ("no component registry exists in this project") and its
explicit flag that the reader page is "genuinely new HTML with no existing render
function to call into."

**Deprecated/outdated:** Not applicable.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The general implementation technique for a minimal, safe stdlib markdown renderer (extract fenced code blocks to placeholders before running inline-formatting regexes, to protect code content from bold/italic/link matching) is sound engineering practice, not verified against any specific external source this session | "Minimal stdlib markdown renderer" discussion embedded in Pattern 2/D-08 and Common Pitfalls | Low — this is general parsing-technique knowledge, not a project-specific fact or a package/version claim; if the technique needs adjustment, it surfaces immediately as a rendering bug in `tests/lesson_roundtrip.py`, not as a silent data-correctness issue |
| A2 | Recommending a single merged `LINT_CODES` set (rather than a separate `LESSON_CODES` tuple mirroring `SETTINGS_CODES`'s separation) is the better shape, based on reading D-06's text as "same *construction pattern*," not "same *tuple*" | "Code Examples" § `LINT_CODES` extension | Low-Medium — if the planner instead creates a separate tuple, `tests/protocol_roundtrip.py:test_lint_codes_declared()`'s `codes = itembank.LINT_CODES` check would need to iterate a second tuple too, and `schema_validate.py`'s enum check reads from wherever the codes actually appear in live output, not from either tuple's name — so a separate tuple is not wrong, only a slightly larger diff, and does not break the two verified test/schema couplings as long as both tuples' *members* still end up in `lint_error.schema.json`'s enum |
| A3 | `--ref <text>` on `itembank lesson` filters the CLI's HTML output to just that one heading's section (rather than rendering the full lesson and merely validating the ref exists) — `03-UI-SPEC.md` only locks the *failure* copy for `--ref`, not its success-path rendering scope | "Pattern 5: the reader surface... CLI twin," also listed under Open Questions | Low — if the planner resolves this differently, only `cmd_lesson`'s branching logic changes; no schema, lint, or route-table shape depends on this interpretation |

## Open Questions

1. **Does `--ref <text>` narrow the CLI's rendered output to one heading, or only
   validate that the ref exists before rendering the whole lesson?**
   - What we know: `03-UI-SPEC.md`'s Copywriting Contract locks the failure message
     (`sys.exit("no lesson heading matching %r in %s" % (a.ref, a.bank))`) but says
     nothing about the success-path output shape.
   - What's unclear: whether a matched `--ref` changes the `%d lesson section(s) -> %s`
     count to 1, or leaves the full document rendered.
   - Recommendation: filter to one section (consistent with the phrase "single-mark
     convenience form" style already used elsewhere in this CLI, e.g. `mark --item`,
     verified `surfaces/cli.py:244`), but confirm with the planner/user before
     implementing since it changes the CLI's observable contract.

2. **Does the "Read the lesson" chip render (and dead-link) under `itembank build`'s
   offline, no-server page?**
   - What we know: `public_item()`'s new field flows identically into both `build`'s
     offline payload and `serve`'s online payload (verified: both call `page_item()`
     which calls `public_item()` unconditionally).
   - What's unclear: whether the planner wants the chip suppressed under `offline=True`
     or accepted as a known limitation (see Pitfall 5).
   - Recommendation: accept as a known, documented limitation, matching `build`'s
     existing "best-effort, no persistence" posture, but call it out explicitly in the
     plan rather than let it surface as an unreported gap during UAT.

3. **Should `assign_ids()`'s `TERMINATOR` regex (`model.py:191-193`) also gain a
   `\[LESSON-REF:` alternative?**
   - What we know: `TERMINATOR` decides where `assign_ids()` inserts a missing
     `[ID:]`/`[HASH:]` line. It currently has no `[LESSON-REF:` alternative.
   - What's unclear: whether this causes any actual placement bug. Traced through: if
     `[LESSON-REF:]` is the first tag after the stem/difficulty parenthetical (the
     natural authoring position), `TERMINATOR.search()` simply finds the *next* real
     terminator (e.g. `[OBJECTIVE:` or `A)`) and inserts `[ID:]`/`[HASH:]` immediately
     before it — which places the minted `[ID:]`/`[HASH:]` lines *after* the existing
     `[LESSON-REF:]` line rather than before it. This is a cosmetic ordering
     difference, not a data-loss or parsing bug (every tag is still matched by its own
     independent `grab()` call regardless of line order).
   - Recommendation: no code change required; note the cosmetic ordering behavior in
     case a plan's acceptance test asserts a specific tag order in `id-assign` output.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None — direct script execution, project convention (verified `CLAUDE.md`'s Testing conventions and every existing `tests/*_roundtrip.py`) |
| Config file | none — `.github/workflows/ci.yml`'s "Test suite" step runs `for t in tests/*.py; do python "$t" || exit 1; done` (verified), so a new file needs no registration anywhere |
| Quick run command | `python tests/lesson_roundtrip.py` |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` (mirrors CI exactly) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LESSON-01 | A bank with `## LESSON` + `###` headings parses into a lesson structure | unit | `python tests/lesson_roundtrip.py` (new `check_lesson_parses` function) | ❌ Wave 0 |
| LESSON-02 | `[LESSON-REF: text]` resolves to the correct heading slug; stem is NOT corrupted by the tag | unit | same file, `check_lesson_ref_does_not_corrupt_stem` | ❌ Wave 0 |
| LESSON-03 | A bank with **no** `## LESSON` section parses to the exact same `qs` as before this phase | regression | same file, `check_no_lesson_section_is_unchanged` — compare `parse_bank(text)` output against `fixtures/sample_bank.md`'s pre-phase-recorded shape (e.g. item count, first item's `stem`/`opts`/`correct` fields) | ❌ Wave 0 |
| LESSON-04 | `LESSON-REF` naming a missing heading is a lint **error** (D-05), by item number, never a crash | unit | same file, `check_lesson_ref_unknown_is_error` — assert `item.lesson_ref_unknown` appears in `errors`, not `warnings` | ❌ Wave 0 |
| LESSON-05 | `itembank spec` includes the LESSON/LESSON-REF grammar text | smoke | `python itembank.py spec \| grep -q LESSON-REF` (or an in-test `"LESSON-REF" in model.SPEC` assertion) | ❌ Wave 0 |
| LESSON-06 | `/lesson/<bank>` renders the lesson with working lesson→item and item→lesson links; CLI twin renders the same content | integration | same file, an HTTP-driven check following `tests/serve_roundtrip.py`'s subprocess-daemon pattern (verified shape: spawn `itembank daemon`, GET the route, assert backlink hrefs and the item-side chip's href are present) | ❌ Wave 0 |
| (contract) | New `lesson.*`/`item.lesson_ref_unknown` codes validate against `schemas/lint_error.schema.json` | contract | `python schema_validate.py schemas/lint_error.schema.json --array <lint.json output> errors` (mirrors CI's own existing step, verified `.github/workflows/ci.yml:62-64`) | ✅ (`schema_validate.py` exists; new fixture triggering these codes does not) |

### Sampling Rate

- **Per task commit:** `python tests/lesson_roundtrip.py`
- **Per wave merge:** full `for t in tests/*.py` loop (mirrors CI)
- **Phase gate:** full suite green, plus a manual `itembank lint fixtures/lesson_bank.md`
  and `itembank lint fixtures/broken_bank.md` (or a new fixture) pass with the expected
  `lesson.*` codes present, before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `fixtures/lesson_bank.md` — new synthetic fixture, `## LESSON` section with
      2-3 `###` headings (prose + at least one list + one table, to exercise D-08's
      renderer scope), and 2-3 items carrying `[LESSON-REF:]` (at least one matching,
      recommend also adding one deliberately-unmatched ref to a *second* fixture or to
      `fixtures/broken_bank.md` so `item.lesson_ref_unknown`/`lesson.duplicate_heading`
      are exercised by a file CI's "Broken fixture is caught" step already reads)
- [ ] `tests/lesson_roundtrip.py` — new, following the `tests/serve_roundtrip.py`
      subprocess-and-HTTP pattern for the daemon-route half, and a lighter in-process
      `model.parse_lesson()`/`model.lint()` unit-test half for the parsing/lint half
- [ ] No framework install needed — stdlib `unittest`-free convention already
      established; nothing to install

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Project has no accounts/auth by design (verified `CLAUDE.md`: "One. No accounts, no auth") |
| V3 Session Management | no | Same as above; the existing `session_id` mechanism is an evidence-tracking identifier, not an auth session, and this phase adds no new session concept |
| V4 Access Control | no | Single local user, no multi-tenancy |
| V5 Input Validation | yes | `html.escape` discipline on every literal fragment of rendered lesson prose (matching `quiz_page.py`'s `esc()`/`daemon.py`'s `html.escape()` precedent, verified); path-containment check on `[LESSON-SRC:]` (matching `surfaces/migrate.py:241-248`'s verified precedent) |
| V6 Cryptography | no | This phase introduces no cryptographic operation; `content_fingerprint()`'s `sha256` (unrelated to this phase) is explicitly documented as "an integrity check, not a security boundary" (verified `model.py:155-156`) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Reflected HTML/script injection via lesson prose rendered unescaped (a bank-authored `<script>` or `<img onerror=...>` inside a heading, list item, or table cell reaching the page verbatim) | Tampering (of the rendered page) | `html.escape()` on every literal text run before interpolation into the HTML template, exactly as `quiz_page.py`'s `esc()` already does for stems/options — the renderer must apply this at the *inline-text* level, after markdown structure is resolved, not attempt to escape the raw markdown source wholesale (which would also escape the intended `<pre><code>` fenced-block markup the renderer itself emits) |
| Path traversal via `[LESSON-SRC:]` (e.g. `[LESSON-SRC: ../../../../etc/passwd]` or an absolute path) reading a file outside the bank's own directory | Information Disclosure | The `os.path.abspath` + `startswith(base_abs + os.sep)` containment check (verified precedent `surfaces/migrate.py:241-248`), applied to the bank's own directory as the containment root, refusing (as `lesson.src_unreadable`, a lint error) rather than reading any path that resolves outside it |
| A crafted `[LESSON-REF:]` or heading text causing the lint check or the renderer to raise an unhandled exception (regex catastrophic backtracking, `None` dereference on a malformed structure) | Denial of Service (of the CLI/daemon process) | ROADMAP SC3's own explicit requirement — "never a render-time crash" — is itself the acceptance gate here; every new function should return a structured error (`lesson.src_unreadable`, etc.) rather than let an exception propagate, matching `daemon.py`'s existing blanket `except Exception: handler.send_server_error(exc)` pattern (verified) for the route handler specifically |

Note: this project's own stated threat model (`model.py:155-156`, verified: "this
project has one local user and no adversary in its threat model") means the bar here
is *correctness under malformed/unusual input* (a stray path, a weird heading), not
defense against an actual adversary — the mitigations above are the same discipline
every other surface in this codebase already applies, not new security engineering.

## Sources

### Primary (HIGH confidence — read directly this session)

- `model.py` (full file, 567 lines) — `parse_bank()`, `parse_question()`, the stem
  terminator alternation, `content_fingerprint()`, `LINT_CODES`, `lint()`, `SPEC`,
  `load()`
- `runtime.py` (full file, 300 lines) — `public_item()`, `explain_payload()`,
  `page_item()`, confirmed zero `model` imports
- `surfaces/daemon.py` (full file, 1205 lines) — `ROUTES`/`ROUTE_CLI`/`API_ROUTES`,
  `handle_study_get`/`handle_quiz_get` as the route-join precedent, `send_not_found`,
  `scan_dir`
- `surfaces/quiz_page.py` (full file, 494 lines) — `chips()`, the `Q.sort(...);
  render();` bootstrap tail, `canon()`, the client-side `esc()`
- `surfaces/quiz.py` (full file, 152 lines) — `page_for()`'s `.replace()` substitution
  chain, `cmd_build`/`cmd_serve`
- `surfaces/study.py` (full file, 70 lines) — `study_page()`, `STUDY_TEMPLATE`, the
  precedent for a second render function with no client POST
- `surfaces/cli.py` (full file, 351 lines) — every `sub.add_parser` shape, the
  `study`/`export`/`day` subcommand precedents `lesson` should follow
- `surfaces/settings.py` (partial, lines 1-60) — `SETTINGS_CODES`'s
  `tuple(sorted({...}))` construction, the precedent D-06 cites
- `surfaces/theme.py` (full file) — `THEME_CSS`'s `--accent`/`--warn`/`--chip` tokens
- `surfaces/migrate.py` (partial, `scan_legacy()`) — the path-containment check
  precedent for `[LESSON-SRC:]`
- `evidence.py` (partial, `evidence_key`/`idempotency_canon`/`response_event`) —
  confirmed no interaction with `lesson_ref`/`lesson_slug`
- `schemas/lint_error.schema.json` (full file) — confirmed closed `enum`, 26 existing
  codes, no `lesson.*` member
- `tests/protocol_roundtrip.py` (partial, lines 62-91, 214-230, 398-430) —
  `test_lint_error_shape`, `test_lint_codes_declared`'s prefix assertion, the
  schema-validation-against-live-output test
- `tests/daemon_roundtrip.py` (partial, lines 601-625) —
  `check_route_cli_inventory`/`check_api_route_scope`
- `tests/serve_roundtrip.py` (partial, lines 1-90) — the subprocess/HTTP test pattern
  `tests/lesson_roundtrip.py` should follow for its daemon-route half
- `tests/config_roundtrip.py` (partial, lines 1-70) — a second example of the
  subprocess-driven CLI test pattern
- `itembank.py` (full file) — the explicit `from model import (...)` / `__all__`
  re-export lists, confirmed no `import *` anywhere
- `.github/workflows/ci.yml` (full file) — confirmed `for t in tests/*.py` generic
  discovery (no registration needed) and the schema-validation-of-live-lint-output step
- `fixtures/sample_bank.md` (lines 1-40) — direct proof of an already-discarded
  preamble (title + two prose paragraphs) in a fixture already in CI
- `build.py` (grep) — confirmed `STAGE_DIRS = ("surfaces", "schemas")` means a new
  `surfaces/lesson.py` file needs no packaging registration
- `03-CONTEXT.md`, `03-UI-SPEC.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`,
  `.planning/ROADMAP.md` § Phase 3, `.planning/config.json` — read in full

### Secondary (MEDIUM confidence)

None used — no web search was performed this session. `.planning/config.json` has
every external search provider (`brave_search`, `exa_search`, `firecrawl`,
`tavily_search`, `ref_search`, `perplexity`, `jina`) set to `false`, and this phase's
own emphasis is explicitly internal code-shape research rather than external
library/ecosystem research, so no external lookup was needed or attempted.

### Tertiary (LOW confidence)

- General minimal-markdown-renderer implementation technique (fenced-code
  extract-and-placeholder before inline-formatting regexes) — training knowledge, not
  verified against an external source this session. See Assumptions Log A1.

## Metadata

**Confidence breakdown:**
- LESSON grammar / parser control flow: HIGH — every regex and control-flow claim
  verified by direct read of `model.py`, cross-checked against a real fixture
- Lint / schema / test coupling: HIGH — the two silent-break couplings
  (`schemas/lint_error.schema.json`, `tests/protocol_roundtrip.py`) were found by
  direct read and are independently exercised by CI, not inferred
- Reader surface / daemon route: HIGH — mirrors an exact, verified existing precedent
  (`handle_study_get`) with no new mechanism invented
- Minimal markdown renderer implementation details: MEDIUM — the D-08 scope and the
  Phase 9 fenced-code seam requirement are verified from `03-CONTEXT.md`/`03-UI-SPEC.md`;
  the specific line/block-scanning technique recommended is sound general practice but
  not verified against an external source (see A1)
- Two open CLI-contract questions (`--ref` scope, `build`'s offline chip) — flagged
  explicitly rather than guessed at, since `03-UI-SPEC.md` does not fully lock them

**Research date:** 2026-08-08
**Valid until:** No external dependency to go stale — valid until `model.py`,
`surfaces/daemon.py`, `surfaces/quiz_page.py`, or the two coupled test/schema files
are next modified by another phase (Phase 4's `SURF-07` palette work touches
`quiz_page.py`'s styling but not its `chips()`/bootstrap logic; watch for merge
conflicts if Phase 3 and Phase 4 run concurrently per the parallel-eligible dependency
graph — both are `Depends on: Nothing`/`Depends on: Phase 2`).
