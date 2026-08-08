# Phase 3: Lesson Format & In-App Reader - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers three things and nothing else:

1. **A `LESSON` grammar** — an optional, additive region in a bank markdown file
   holding the teaching text its items test, plus a `LESSON-REF` item tag pointing at
   one heading inside it.
2. **Lint and spec coverage** — an actionable, by-item-number failure when a
   `LESSON-REF` names a heading that does not exist, and enough `spec` text that an
   authoring agent with no source access writes a valid lesson on the first try.
3. **An in-app reader** — a daemon route that renders the lesson as reading material
   with working links in both directions (lesson heading → the items that reference it,
   item → the lesson it is drawn from), plus the CLI twin every route is required to
   have.

**Explicitly not in this phase:**

- The hint ladder. Tier 0 of Phase 6's ladder is "lesson pointer" and it will consume
  the item→lesson link built here, but no tier logic, no `hint` command, no cursor-hold.
- LaTeX rendering and runnable inline code (Phase 9, LOOP-02/LOOP-03). The renderer
  built here must **leave the door open** for both (see D-08) and implement neither.
- Any theming or palette work (Phase 4). The reader uses whatever the surfaces
  currently use and inherits Phase 4's palette later, for free.
- A lesson review queue or scheduling (SCHED-04, Phase 10).
- Authoring lessons for real EMT/Math/CS content. Fixtures are synthetic per the
  no-real-banks rule.

</domain>

<decisions>
## Implementation Decisions

**All decisions in this section were delegated by the user.** Asked which of four gray
areas to discuss for this phase, Weibao selected "Delegate all" — the same standing
instruction recorded in `02.1-CONTEXT.md`: *"plan the most optimal solution that gives
us the most options and directions in the future."* Every D-number below is Claude's
judgment resolved toward future optionality and reversibility, not a user-stated
preference. The planner may revise any of them with a stated reason.

### LESSON grammar

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

### Lint

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

### Reader surface

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/ROADMAP.md` § "Phase 3: Lesson Format & In-App Reader" — goal, the four
  success criteria, `UI hint: yes`, and the `Depends on: Nothing` that makes this
  parallel-eligible with Phases 1, 2, and 5.
- `.planning/REQUIREMENTS.md` § "Lessons" — LESSON-01 through LESSON-06. **LESSON-04's
  "warns" contradicts ROADMAP SC3's "fails"; see D-05.**
- `.planning/REQUIREMENTS.md` § "Teaching" TEACH-02 and § "Subject loop" LOOP-02 /
  LOOP-03 / LOOP-04 — the downstream consumers this phase must not block.
- `.planning/PROJECT.md` — stdlib-only with two named exceptions (vendored KaTeX,
  `urllib` for the updater). This phase adds no third exception; that is the argument
  against any markdown library.

### Prior phase context that still binds

- `.planning/phases/02.1-packaging-self-update-interop-export/02.1-CONTEXT.md` —
  the standing "most room for maneuver" steering instruction, and the settings/schema
  conventions (`x-itembank-phase`, `THIS_PHASE` in `surfaces/settings.py:27`) any new
  settings key must follow.
- `.planning/phases/02-daemon-consolidation-settings-foundation/02-CONTEXT.md` — the
  one-daemon-one-port route conventions the `/lesson/<bank>` route joins, and the rule
  that every route has a CLI twin.

### Existing code this phase extends

- `model.py:27-36` `parse_bank()` — the `^(?=Q\d+\.)` split that already discards the
  preamble. LESSON-03's compatibility floor rests on this; read it before designing the
  lesson parser.
- `model.py:39-120` `parse_question()` — the `[OBJECTIVE:]` / `[TYPE:]` / `[ID:]` tag
  shapes `[LESSON-REF:]` mirrors, and the stem-terminator alternation at lines 43-47
  that must gain `\n\[LESSON-REF` or the stem will swallow the tag.
- `model.py:142-179` `content_fingerprint()` — the exclusion list D-04 joins.
- `model.py:280` `SPEC` — the format contract text LESSON-05 requires extending.
- `model.py:389-401` `LINT_CODES` — the `tuple(sorted({...}))` construction the new
  `lesson.*` namespace follows.
- `surfaces/daemon.py` — the route table and `do_GET` dispatch the `/lesson/<bank>`
  route joins; also the `handler.banks` identifier-addressed 404 convention noted near
  line 766.
- `surfaces/study.py` and `surfaces/quiz_page.py` — the existing page-render shape
  (`page_for()` helpers, `html.escape` discipline) the reader mirrors rather than
  invents.
- `surfaces/cli.py` — where `cmd_lesson` registers.

### Codebase maps

- `.planning/codebase/ARCHITECTURE.md` — the four-layer model and the rule that
  surfaces are clients, never parsers.
- `.planning/codebase/CONVENTIONS.md` — `cmd_*` naming, `%`-formatting, no private
  underscore functions.
- `.planning/codebase/TESTING.md` — `tests/*_roundtrip.py`, run directly by
  `python tests/<name>_roundtrip.py`, no runner and no framework.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `model.grab()` and `model.section()` — the whole tag-extraction vocabulary. The
  lesson parser should be built from these, not from a second regex idiom.
- `model.collapse()` — whitespace-collapse with case preserved. `lesson_slug()` builds
  on it rather than writing a second normalizer.
- `surfaces/quiz_page.py`'s page scaffolding — inline CSS, `html.escape` on every
  interpolated value, no external asset. The reader page copies this shape.
- `server.Handler` / `bind()` — not needed; Phase 2 made the daemon the single server
  and `serve`/`day` its callers. The reader must **not** start a server of its own.

### Established Patterns

- **Additive format changes only.** A bank written before this phase parses after it,
  byte for byte. D-01 gets this for free from the existing preamble discard.
- **One parser.** The reader loads through `model.load()`. It never re-reads the bank
  file to find lesson text a second way.
- **Named dotted error codes**, accumulated into `(errors, warnings)` lists of
  `LintError`, tagged by item number.
- **No answer key in the browser before answering** — the reader renders teaching text
  only, and links to items rather than embedding them.

### Integration Points

- `model.py` — lesson parsing, the `[LESSON-REF:]` tag, the stem-terminator alternation,
  the fingerprint exclusion, `SPEC`, and the new `lesson.*` codes.
- `surfaces/lesson.py` (new) — renderer plus `cmd_lesson`.
- `surfaces/daemon.py` — one new GET route.
- `surfaces/cli.py` — one new subcommand.
- `tests/lesson_roundtrip.py` (new) — must include a **no-LESSON-section bank** case
  asserting the parse result is unchanged, which is SC2's actual test.

</code_context>

<specifics>
## Specific Ideas

- The standing steering instruction, carried from Phase 2.1 and reaffirmed by this
  phase's "Delegate all": where two designs cost about the same, take the one that
  keeps a door open; where one is a one-way door, take the other and say why. D-02
  (shareable lesson source), D-08 (the Phase 9 fenced-block seam), and D-06's
  warning-not-error `lesson.orphan_heading` are the three places that shows up here.
- The lesson is the teaching surface's ground floor. PROJECT.md's core value is that
  the runtime, not the model, decides what reaches the learner — a lesson is content
  the runtime can always show, offline, with no model involved. It is the part of the
  teaching loop that must never depend on credits or network.

</specifics>

<deferred>
## Deferred Ideas

- **Lesson review queue with a hand-set schedule** — SCHED-04, Phase 10.
- **Tier-0 hint returning the lesson pointer** — TEACH-02, Phase 6. This phase builds
  the pointer; Phase 6 gates when it is spoken.
- **LaTeX in lessons (LOOP-02) and runnable inline code (LOOP-03)** — Phase 9. D-08
  reserves the seam and implements neither.
- **Theming the reader** — Phase 4's shared palette. The reader ships on the existing
  surface styling and inherits the palette when Phase 4 lands.
- **A lesson authoring command** (`itembank lesson --draft`) — Phase 11's closed
  authoring loop, if anywhere.

</deferred>

---

*Phase: 3-lesson-format-in-app-reader*
*Context gathered: 2026-08-08*
