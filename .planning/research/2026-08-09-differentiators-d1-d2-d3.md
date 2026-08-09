---
date: 2026-08-09
topic: "Differentiators D1 (hover key terms), D2 ([!KEY] memorizable blocks), D3 (LESSON-STYLE.md voice contract) + Q3 (lintable style rules)"
confidence:
  d1_format: HIGH        # grammar is our design; parser-additivity verified against model.py
  d1_render: MEDIUM      # popover API baseline verified via web; interestfor is Chromium-only
  d2_format: HIGH        # cloze + callout grammar cross-checked against Obsidian/GitHub/Mochi/RemNote
  d2_anki_export: MEDIUM # Anki TSV header semantics cited from official manual, not tested this session
  d2_fsrs: MEDIUM        # FSRS input surface cited from ts-fsrs/rs-fsrs docs
  d3_q3: HIGH            # lintability judgments verified against model.py's existing lint machinery
consumes: .planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md §1–3, .planning/UI-SPEC.md, model.py
phase_home: 03.1 (grammar/render/fallback), 10 (D2 scheduling evidence), 11 (D3 model-judged enforcement)
---

# Differentiators D1, D2, D3 — Full Design

Binding constraints honored throughout: the runtime, not the model, decides what
reaches the learner; one parser (`model.py`), one scorer, one append-only evidence
store; every grammar below is **additive** — a bank without a `## TERMS` section,
a `[!KEY]` block, or a `LESSON-STYLE.md` beside it parses and lints byte-for-byte
as it does today; accessibility gates from UI-SPEC (no answer leakage in DOM, hover
AND tap AND keyboard, WCAG AA, no punitive framing) are design inputs, not afterthoughts.

Additivity mechanism, verified against the parser: `parse_bank()` splits on `Qn.`
markers and ignores everything else, and `parse_lesson()` is a second independent
read over the preamble that changes neither's return shape
[VERIFIED: model.py:27-36, model.py:167-197 — "Everything that is not a question
block is ignored" / "Never called from inside `load()` or `parse_bank()`, and it
changes neither's return shape"]. New sections follow the `parse_lesson` precedent:
one new independent reader per section, zero changes to `parse_bank`.

Lint precedent, verified: findings are `LintError(code, field, item, message)`
records whose `str()` is the historical `"Qn: message"`, codes are a published
dotted namespace where "adding a code is additive, renaming one is a breaking
change" [VERIFIED: model.py:551-560, 578-590 — `LINT_CODES = tuple(sorted({...
"item.lesson_ref_unknown", "lesson.duplicate_heading", "lesson.orphan_heading",
"lesson.src_unreadable", ...}))`]. All new codes below extend this tuple.

The one slugifier rule, verified: `lesson_slug()` is deliberately the single
slugifier for lookup keys and anchor ids [VERIFIED: model.py:145-164 — "a lookup
that agrees with an anchor by coincidence eventually disagrees, so there is
structurally one call, not two"]. D1 term keys reuse it; no second slugifier.

---

## D1 — Key Terms: `## TERMS` glossary + `[[term]]` inline

### Prior art (what to take, what to fix)

- **LingQ**: every word is known/unknown/in-between; clicked words feed a review
  queue. Take: lookup → queue linkage. Fix: it is language-reading only, no
  assessment link. [CITED: autolingual.com/lingq-review, alllanguageresources.com/lingq-review]
- **Readlang**: click word → translation appears → saved. Take: one-tap gloss,
  clean UI. [CITED: simplyfluent.com/blog/best-reading-apps-language-learning-2026]
- **Kindle Word Wise**: definitions render inline *above* words; a five-level
  slider controls gloss density; line spacing is forced to maximum to make room.
  Take: the density-control idea (deferred). **Reject the above-the-line render**:
  it costs line-height control and fights our 72ch/1.5-leading reading contract.
  [CITED: amazon.com/gp/help nodeId=201645250, makeuseof.com/how-to-enable-use-word-wise-kindle]
- **Obsidian `[[wikilink]]`**: `[[target|display]]` pipe syntax is the de facto
  standard for aliased inline references; we adopt it verbatim so authoring
  models already know it. [ASSUMED — training knowledge of Obsidian link syntax;
  the pipe form is ubiquitous but was not re-verified against Obsidian docs this session]

### 1. Format grammar — FORMAT, cost S, phase 03.1

A new optional preamble section, sibling of `## LESSON`, above the first question:

```markdown
## TERMS

TERM) oropharyngeal airway
ALIAS: OPA | oral airway
DEF: A rigid, curved adjunct sized from the corner of the mouth to the
  earlobe, inserted only in a patient without a gag reflex.
XLAT: zh-Hans :: 口咽通气道
SEE: q3, q7

TERM) nasopharyngeal airway
ALIAS: NPA
DEF: A soft flexible tube tolerated by patients with an intact gag reflex.
```

Grammar rules:

- **Section boundary**: `## TERMS` at line start; runs to the next `## ` heading
  at line start or to the first `Qn.` line that parses as a real question —
  identical boundary rule to `## LESSON` [VERIFIED: model.py:199-204, the
  parse-as-real-question boundary loop]. A bank may carry both sections in
  either order. Parsed by a new `parse_terms(bank_path)` mirroring
  `parse_lesson()`: independent read, returns `None` when absent, dict otherwise.
  `[LESSON-SRC:]`-style external source is deliberately NOT supported for TERMS
  in 03.1 (one shared-file mechanism at a time; add `[TERMS-SRC:]` later only if
  a real bank needs it).
- **Entry marker**: `TERM)` at line start, mirroring `ROW)`/`STEP)`/`ITEM)`
  [VERIFIED: model.py:93, 104 — `^ROW\)`, `^STEP\)` line-anchored markers].
  An entry runs from its `TERM)` line to the next `TERM)` or section end.
- **Fields** (uppercase-label lines, mirroring `WHY BEST:` field style):
  - `TERM) <canonical term>` — required. The canonical display form.
  - `DEF:` — required, multi-line (continuation lines indented, read until next
    uppercase label or `TERM)`). Plain prose plus inline code only; no nested
    `[[refs]]`, no callouts, no images — a gloss is one breath of text.
  - `ALIAS:` — optional, pipe-separated (`|` mirrors `[CATEGORIES: A | B]`).
  - `XLAT:` — optional, repeatable: `XLAT: <BCP-47 tag> :: <translation>`.
    Reuses the `::` pair separator already in `ROW) text :: category`
    [VERIFIED: model.py:93-97]. **This is the future bilingual-reader field**
    (brief §5, backlog 999.2): designed now, rendered by nothing in 03.1. The
    fork line for a language reader is *tokenization and per-word status*, not
    the gloss store — one extra field keeps the store shared.
  - `SEE:` — optional, comma-separated item references: `q3` (question number id)
    or a 16-hex `[ID:]` item id. Links a term to the items that test it; the
    reader renders these as "tested by" links, and the Phase 7 selector may use
    the reverse index.
- **Key and case sensitivity**: a term's key is `lesson_slug(canonical)` and
  `lesson_slug(alias)` for each alias — the existing one slugifier, so lookup is
  case-insensitive and punctuation-insensitive by construction, and the rendered
  anchor `#term-<slug>` agrees with the lookup key structurally. Display always
  preserves the author's surface form.
- **Inline reference**: `[[term]]` or `[[term|display text]]` (Obsidian pipe
  form). Valid in lesson intro/section prose and in item stems and option text.
  Matched case-insensitively via the slug. Reads to the first `]]`; a term whose
  text contains `]]` cannot be referenced — same rule shape as LESSON-REF's
  "heading text must not contain `]`" [VERIFIED: model.py SPEC:499-503].
- **Escaping and non-matching contexts**:
  - `\[[` renders a literal `[[` (standard backslash escape; the renderer strips
    the backslash).
  - `[[...]]` inside inline code spans and fenced code blocks is never a term
    reference — code is already verbatim in the reader's contract.
  - An unescaped `[[ref]]` matching no term/alias slug → lint **error**
    `term.ref_unknown` (mirrors `item.lesson_ref_unknown`). It is an error, not
    a warning, for the same reason LESSON-REF is: a dangling reference renders
    as a dead affordance.
- **Collision rules** (all at lint time, all deterministic):
  - Two `TERM)` entries whose canonical slugs collide → error `terms.duplicate_term`
    (mirrors `lesson.duplicate_heading` including the "rename one" message shape).
  - An alias slug colliding with any other entry's canonical or alias slug →
    error `terms.alias_collision`. Within one entry, alias == canonical is
    silently ignored (harmless).
  - A term never referenced by any `[[...]]` and never named in any `SEE:` →
    warning `terms.orphan_term` (mirrors `lesson.orphan_heading`; a glossary may
    legitimately define more than the prose links).
- **New lint codes** (additive to `LINT_CODES`): `term.ref_unknown`,
  `terms.duplicate_term`, `terms.alias_collision`, `terms.orphan_term`,
  `term.gloss_leaks_key` (see §4), `terms.bad_field` (malformed XLAT/SEE line).

Additivity proof obligation for the plan: fixture asserting a bank with no
`## TERMS` and no `[[`-sequences produces byte-identical `parse_bank()` output
and identical lint findings to today.

### 2. Render behavior — RENDERER, cost M, phase 03.1

**In the lesson reader:**

- The glossary section renders once, at the end of the lesson, as a "Terms"
  appendix: `<section id="terms"><h3>Terms</h3><dl>` where each entry is
  `<dt id="term-<slug>"><dfn>oropharyngeal airway</dfn> <span class="term-alias">(OPA)</span></dt>
  <dd>…definition…</dd>`. `<dfn>` marks the *defining instance* — this is its
  correct HTML semantics; inline *uses* are not `<dfn>` [CITED: MDN dfn element
  semantics — the element marks the term being defined, not each mention].
- Each inline `[[term]]` renders, **without JS**, as
  `<a class="term" href="#term-<slug>" aria-describedby staying clear>OPA</a>` —
  a real internal link to the appendix entry. Styling hooks: dotted underline
  (`text-decoration: underline dotted`), color `var(--accent)` — UI-SPEC assigns
  accent to "source-link affordances," which this is; the dotted underline is
  the structural (non-color) differentiator from ordinary links, satisfying
  "never color alone."
- **With JS**, a small enhancer upgrades each term link in place to
  `<button class="term" popovertarget="gloss-<slug>">OPA</button>` plus one
  shared-per-slug `<div id="gloss-<slug>" popover>` node containing the DEF text
  and a "Full entry →" link to the appendix anchor. The Popover API is Baseline
  Widely Available since April 2025 — Chrome, Firefox, Safari, Edge — and gives
  Esc-to-close, light-dismiss, focus return, and top-layer stacking for free
  [CITED: web.dev/blog/popover-api; developer.mozilla.org Popover_API].
  - **Tap and keyboard**: `popovertarget` on a real `<button>` covers tap and
    Enter/Space natively; Esc closes and returns focus (browser behavior)
    [CITED: hidde.blog/popover-accessibility].
  - **Hover**: progressive enhancement only. Where supported, emit
    `interestfor="gloss-<slug>"` + `popover="hint"` — declarative
    hover/focus/long-press showing, shipped in Chromium 142 (Oct 2025) but
    **not Baseline** [CITED: open-ui.org interest-invokers explainer;
    blink-dev intent-to-ship]. Elsewhere, a ~15-line mouseenter/mouseleave
    (600ms intent delay) fallback calls `showPopover()`. Hover is never the
    only path — click/tap/focus is primary, matching UI-SPEC narrow-viewport
    rule "no hover-only controls."
  - Popover panel styling: surface-30% tokens (`--card`, `--line`), `text-body`
    16px, max-width 36ch, `space-3` padding, 150ms fade honoring
    `prefers-reduced-motion`. The trigger keeps the 2px accent focus outline.
  - `aria-details="gloss-<slug>"` on the trigger associates the gloss for AT.
    Screen readers get the same DEF text, never more (no hidden extra fields).
- `SEE:` items render inside the appendix `<dd>` as "Tested by: Q3, Q7" links
  into the served quiz/report where a session context exists, else plain text.

**Inside an item stem/option (served sitting):** the affordance exists only when
the runtime says so (§4). When permitted, identical button+popover, but the
popover body is **not inlined in the page** — it is fetched from
`GET /gloss?item=<item_id>&term=<slug>` on first open. When not permitted, the
term renders as plain text: no button, no data attribute, no dead affordance,
nothing to discover in the DOM (UI-SPEC gate 1: no concealed content in HTML,
ARIA, or CSS-off text).

**In the static offline quiz (`itembank build`):** terms in stems always render
as plain text. The static page has no runtime to gate a gloss, and an inlined
gloss store would put every definition one view-source away from an active
sitting. Lesson text in the static page (if present) uses the no-JS link form.

### 3. No-JS fallback — RENDERER, cost S, phase 03.1

- Inline term = the plain internal link above; the reader never depends on JS.
  One tap/click jumps to the appendix entry; the browser's back button returns.
- The appendix `<dl>` is always rendered in full — it doubles as the print
  surface: **print CSS** appends `content: " (see Terms)"`-free styling, keeps
  the dotted underline, and prints the full glossary at the end (paper study,
  brief blind spot B4, comes free).
- No `details/summary` for D1: an inline `<details>` inside a paragraph breaks
  text flow and reads poorly in AT; the link-to-appendix pattern is the honest
  degraded form. (`details/summary` is D2's fallback, where blocks are already
  block-level.)

### 4. Evidence semantics and the runtime gate — RUNTIME, cost M, phase 03.1 (events), 10 (queue)

**Events** (append-only, existing evidence store, one new event kind):

```json
{"event": "term_lookup", "ts": "...", "term_slug": "oropharyngeal-airway",
 "context": {"kind": "lesson", "bank": "...", "heading_slug": "..."},
 "session_id": null, "mode": null}
```

- In the lesson reader, opening a gloss fires a `POST /event/term-lookup` beacon
  to the daemon. **Degrade, never block**: with no daemon, the popover still
  opens from inlined content and no event is recorded — the same shape as `day`
  omitting Anki counts when Anki is closed.
- Inside a served sitting, the `GET /gloss` fetch *is* the event: the runtime
  records `term_lookup` with `session_id`, `item_id`, and `mode` before
  returning the DEF. Recording is server-side, so it cannot be skipped while
  still seeing the gloss.
- **Phase 10 consumption**: repeated lookups make a term a review candidate —
  the LingQ loop, but cross-subject. A derivation (not a stored counter) over
  the event log: ≥3 lookups of one slug within 14 days → the term surfaces in
  the Review queue as a candidate, shown with its evidence ("looked up 3 times
  this week"), consistent with UI-SPEC's evidence-before-inference rule.
  Terms do NOT auto-enter the FSRS queue; the learner accepts the candidate
  (calm progress, no engagement pressure).

**The gate rule — normative, testable:**

> A gloss must never reveal an answer to the active item. The runtime computes,
> at serve time, `glossable(item, term) : bool`, and a term that is not
> glossable renders as plain text with no affordance and no DOM trace.
> `glossable` is false when ANY of:
> 1. `mode` is `diagnostic` or `exam` — no glosses inside items, ever, in
>    withholding modes (glosses remain available in the lesson reader);
> 2. the term's canonical or any alias, whitespace-collapsed and lowercased,
>    equals or is contained in any keyed answer text of the item — for mc/multi:
>    any correct option's text; for table/dnd: any row's assigned category; for
>    build: any step text (order is the answer, steps are all "keyed"); for
>    short: the MODEL answer;
> 3. any keyed answer text of the item (same canonicalization) appears as a
>    substring of the term's DEF.
> The comparison uses `collapse()` + lowercase — the same canonicalization the
> fingerprint uses [VERIFIED: model.py:136-142 `collapse()`].

This is conservative (a DEF merely *mentioning* an option string is blocked),
and that is correct: the cost of a false block is a plain-text term; the cost
of a false allow is a leaked key. Lint mirrors the rule at author time:
warning `term.gloss_leaks_key` — "term '<t>' is glossable from Q<n>'s stem but
its DEF contains that item's keyed answer; the runtime will render it as plain
text there" — so authors learn about it before a learner ever hits the gate.

Test fixtures the plan must include: (a) DOM of a served practice item whose
stem references a gloss-blocked term contains no button/popover/attribute for
it; (b) diagnostic-mode page contains zero gloss affordances in items; (c) the
same bank's lesson page still glosses the term fully.

---

## D2 — `[!KEY]` blocks: one authoring act, three surfaces (reader, Anki, FSRS)

### Prior art

- **GitHub alerts**: `> [!NOTE]` … five types, blockquote-carried, uppercase
  marker on its own logical line; unknown-to-a-renderer alerts degrade to a
  visible blockquote with the literal `[!NOTE]` — the degradation property we
  want [CITED: github.com/community discussion 16925; blog.jakelee.co.uk/github-alert-experiments].
- **Obsidian callouts**: same `> [!type]` grammar plus title-on-marker-line and
  fold modifiers (`-`/`+`); 13 built-in types [CITED: help-adjacent docs via
  markdowntools.io/obsidian-callouts, obsibrain.com callout guide]. We adopt
  the title-on-marker-line, reject fold modifiers (fold state is a renderer
  concern, and our review surface — not the author — decides what is hidden).
- **What they get wrong** (brief §3): callouts are decorative — nothing
  schedules them. Anki cards are divorced from prose. The fix is a stable id
  and an export/schedule path on the block itself.
- **Cloze syntax**: `{{...}}` is the shared convention of Mochi ("The Shiba Inu
  is a breed of {{hunting dog}}") and RemNote (type `{{` to open a cloze)
  [CITED: mochi.cards/docs/markdown/advanced-formatting; help.remnote.com
  creating-flashcards]. Anki's native form is `{{c1::text}}`. We author in the
  simple form and compile to Anki's on export.
- **Anki TSV import**: since 2.1.54, `#key:value` file headers control
  separator, notetype, deck, and — critically — `#guid column:N`, which makes
  re-import an **update, not a duplicate** [CITED: docs.ankiweb.net/importing/text-files.html].
  This is what a stable block id buys.

### 1. Format grammar — FORMAT, cost M, phase 03.1

Inside `## LESSON` prose (intro or any `###` section body):

```markdown
> [!KEY] Adult chest compressions
> [ID: 3f9a2c1d0e8b7a64]
> [HASH: sha256:ab12cd34ef56ab78]
> Compress at least {{2 inches (5 cm)}} deep at {{100 to 120}} per minute,
> allowing full recoil between compressions.
```

- **Block boundary**: a line matching `^>\s*\[!KEY\]` opens the block; the
  optional title is the remainder of that line. The body is every subsequent
  line starting `>` (standard blockquote continuation); the block ends at the
  first non-`>` line. Case: `[!KEY]` uppercase only (GitHub convention;
  lowercase `[!key]` is a lint warning `key.marker_case`, rendered anyway).
- **Display-only siblings**, same grammar, no id, no export, no schedule:
  `[!NOTE]`, `[!EXAMPLE]`, `[!WARNING]` — the GitHub-compatible decorative
  family, styled but inert. Only `[!KEY]` is a first-class memorizable. An
  unknown type `[!FOO]` renders as an ordinary blockquote containing the
  literal text (the GitHub degradation), plus warning `lesson.unknown_callout`.
- **Stable id**: the exact `[ID:]`/`[HASH:]` mechanism items already use,
  reusing `new_item_id()` and the `taken` set so ids are globally unique across
  items AND key blocks in one namespace — one evidence store needs one key
  type [VERIFIED: model.py:297-305 `new_item_id()` 16-hex; model.py:313-394
  `assign_ids()` with cross-bank `taken`]. `itembank id-assign` grows one more
  walk: mint `> [ID: …]` / `> [HASH: …]` lines directly under the marker line
  for any `[!KEY]` lacking them. The HASH fingerprints `collapse(title) +
  collapse(body-with-cloze-markers)` — cloze braces are part of tested content
  (moving a cloze changes the card). Renderer and exporter hide the two
  bookkeeping lines everywhere.
- **Cloze syntax inside the body**: `{{answer}}`, optionally `{{n::answer}}`
  to group deletions onto one Anki card (`{{1::site}} … {{1::rate}}` hide
  together). Unnumbered clozes auto-number sequentially at export. Escaping:
  `{{` inside inline/fenced code is literal; `\{\{` escapes in prose. A
  `{{` without a matching `}}` in the same block → error `key.unclosed_cloze`.
- **Front/back derivation rule** (deterministic, no model involved):
  - Body contains ≥1 cloze → Anki **Cloze** notetype. `Text` = body with each
    `{{…}}`/`{{n::…}}` compiled to `{{c<n>::…}}`. `Back Extra` = title + a
    breadcrumb "bank › lesson heading" for context.
  - No cloze but has a title → Anki **Basic**. Front = title (as a question
    prompt it must stand alone — see style rule E8 in D3). Back = body.
  - No cloze and no title → lint **error** `key.no_front`: "a [!KEY] block
    with no title and no cloze has nothing to prompt with; add a title or
    mark a cloze."
- **New lint codes**: `key.no_front`, `key.unclosed_cloze`, `key.missing_id`
  (warning, mirrors `item.missing_id` wording including "run `itembank
  id-assign`"), `key.duplicate_id` (error), `key.missing_hash` (warning),
  `key.content_drift` (warning, evidence-stays-attached wording),
  `key.body_too_long` (see D3 E7), `lesson.unknown_callout` (warning),
  `key.marker_case` (warning).
- Additivity: banks without `>` callout lines parse unchanged; the current
  reader already renders unknown constructs as literal text
  [VERIFIED: model.py SPEC:514-518 — "Any other markdown construct appears as
  literal text"], so even an *old* renderer showing a new bank degrades to a
  visible quoted block, never hidden content.

### 2. Anki TSV export — FORMAT/RUNTIME, cost S, phase 03.1 (extends existing `itembank export`)

One TSV per bank, `<bank>_keys.tsv`:

```
#separator:tab
#html:true
#guid column:1
#notetype column:2
#deck column:3
#tags column:6
3f9a2c1d0e8b7a64	Cloze	itembank::emt::airway	Compress at least {{c1::2 inches (5 cm)}}…	Adult chest compressions — emt_airway_bank › CPR mechanics	itembank emt
```

Columns: `guid, notetype, deck, field1(Front|Text), field2(Back|Back Extra), tags`.

- **GUID = the block's `[ID:]`** → re-export after an edit and Anki's importer
  updates the existing note instead of duplicating it
  [CITED: docs.ankiweb.net/importing/text-files.html — `#guid column:` header].
  This is the whole reason the id is stable and machine-minted.
- Deck path derives `itembank::<subject>::<bank-stem>`; subject comes from the
  namespaced OBJECTIVE prefix when present (`emt:` → `emt`).
- Optional live path later: AnkiConnect `addNote`/`updateNoteFields` exists and
  the project already speaks AnkiConnect for deck counts, but `addNote` has no
  first-class guid parameter — dedupe there is by field scope — so **TSV with
  `#guid column` is the more correct primary export**; AnkiConnect push is a
  Phase 10+ convenience, not the contract
  [CITED: git.sr.ht/~foosoft/anki-connect API — addNote takes deckName,
  modelName, fields, tags, duplicate options; no guid].
- Export never mutates Anki scheduling state (UI-SPEC "Do Not Build Yet":
  no Anki schedule mutation). Export writes a file; the learner imports it.

### 3. Render behavior — RENDERER, cost M, phase 03.1

**Reader (lesson page):**

```html
<section class="callout callout-key" id="key-3f9a2c1d0e8b7a64">
  <p class="callout-label"><svg aria-hidden="true">…</svg> Key point
     <span class="callout-title">Adult chest compressions</span></p>
  <div class="callout-body"><p>Compress at least <mark class="cloze">2 inches (5 cm)</mark> …</p></div>
</section>
```

- `<section>` not `<aside>`: a KEY block is core content, not tangential.
- The visible text label "Key point" is the non-color differentiator (UI-SPEC:
  semantic meaning never carried by color alone). Icon is inline SVG,
  `aria-hidden`, with the text label carrying the semantics.
- Styling hooks: background `var(--card)`, 1px `var(--line)` border, a 3px
  left border and the label in `var(--accent)` is **not** used — accent is
  reserved for focus/nav/primary action; instead the left border uses
  `var(--ink)` at reduced opacity via the existing surface tokens, `space-3`
  padding, `space-4` vertical margin, `text-body` size (never smaller — this
  is the content that matters most). Display-only siblings get their own
  labels ("Note", "Example", "Warning" with `--warn` pairing text+icon).
- **In the reader, cloze text renders revealed** inside `<mark class="cloze">`
  (subtle background from `--accent-soft` is acceptable here as it is not
  correctness semantics; a dashed underline is the structural cue). Reading is
  reading; hiding text from a reader who has not asked to be tested is
  Duolingo-style friction we reject.
- Each KEY block carries a quiet footer affordance "Add to review" (button,
  POST to daemon) when a daemon is present — the learner opts a block into the
  Phase 10 queue; no auto-enrolment (calm progress). Absent daemon: affordance
  absent, block fully readable.

**Review surface (Phase 10):** the runtime serves a review payload in which
each cloze span is replaced by `<span class="cloze-blank" role="img"
aria-label="hidden">____</span>` — **the hidden text is not in the DOM**; the
reveal is a fetch (`POST /review/reveal`) that also timestamps the reveal
event. Rating buttons `Again / Hard / Good / Easy` appear only after reveal.
Inside a *sitting*, KEY blocks linked (via their lesson heading) to the active
item's `[LESSON-REF:]` are subject to the same withholding rule as hints: in
diagnostic/exam modes the lesson panel is unavailable anyway; in practice
mode a KEY block whose body fails the D1 `glossable`-style containment check
against the active item's keyed answers is rendered with its clozes blanked
even in the reader panel. Same rule, same canonicalization, one implementation.

**Inside an item stem:** `[!KEY]` is not valid in stems (stems are not lesson
prose); the parser never looks for it there. Nothing to gate.

### 4. No-JS fallback and print — RENDERER, cost S, phase 03.1

- **Reader**: the block is plain styled HTML — zero JS involved; "Add to
  review" is a real `<form method="post">` button (works without JS when the
  daemon serves the page; absent on the static build).
- **Review, no JS**: `<details><summary>Show the hidden text</summary>…</details>`
  per cloze, with rating as a POST form. The hidden text IS in the DOM here.
  This is acceptable and must be stated in the plan explicitly: a KEY review is
  self-graded recall producing a learner-entered rating — like a paper
  flashcard — not a runtime-scored verdict; the no-leak DOM gate protects
  *scored assessment*, and no score derives from a KEY reveal. The JS path
  still prefers fetch-on-reveal because it gives honest reveal timestamps.
- **Print**: KEY blocks print as bordered boxes with the "Key point" label;
  a `@media print` rule can render clozes as blanks with the answers in a
  printed answer list at the end — a paper self-test for free (blind spot B4).
  Default print = revealed; blanked print is a `?print=drill` variant later.

### 5. Evidence semantics — RUNTIME, cost M, phase 10 (events + FSRS)

Events (append-only, same store):

```json
{"event": "key_enrolled",  "key_id": "3f9a…", "ts": "…"}
{"event": "key_review",    "key_id": "3f9a…", "ts": "…",
 "rating": "good", "elapsed_days": 4.1, "revealed_ms": 6200, "mode": "review"}
{"event": "key_export",    "key_id": "3f9a…", "ts": "…", "target": "anki_tsv"}
```

- **FSRS entry (Phase 10)**: FSRS needs exactly (memory state, elapsed time,
  grade) per review; state is (stability, difficulty); grade ∈ {Again, Hard,
  Good, Easy}; the standard implementations carry a Card {due, stability,
  difficulty, elapsed_days, state, last_review} plus a ReviewLog, with 19–21
  trainable weights [CITED: open-spaced-repetition ts-fsrs docs + data models;
  borretti.me/article/implementing-fsrs-in-100-lines — implementable in ~100
  lines of pure Python, no dependency needed]. Our `key_review` events are a
  complete ReviewLog; **Card state is derived by replaying the log**, never
  stored as mutable truth — the append-only store stays the single source, and
  a scheduler bug is fixed by re-deriving, not migrating.
- `key_export` events let the auditor answer "which memorizables live only in
  Anki" and keep the Anki lane and the itembank lane visibly separate (UI-SPEC:
  Anki signal is external, never merged).
- Runtime gates: ratings are accepted only for enrolled keys with a served
  reveal in the same session (`revealed_ms` present) — a client cannot fabricate
  a review of a card it never opened; and the daily review cap (Phase 10 lanes
  fuse) applies to KEY reviews the same as items.

---

## D3 — `LESSON-STYLE.md`: the house voice contract

### Prior art

- **Vale** is the proof of concept that a prose style guide can be a lint pass:
  YAML rules over regex/wordlists/metrics, packaged styles for the Microsoft and
  Google developer style guides, markup-aware (lints prose, ignores syntax)
  [CITED: vale.sh/docs; passo.uno/posts/first-steps-with-the-vale-prose-linter].
  We do not adopt Vale itself (Go binary, YAML sprawl, and our linter must stay
  the one linter emitting `LintError` records); we adopt its rule taxonomy:
  **existence/substitution (regex), occurrence (structural count), metric
  (readability)** — all three implementable in pure Python inside `lint()`.
- **textlint/proselint**: same category, JS/Python ecosystems; nothing they
  check that our subset below misses for this use case [ASSUMED — comparative
  claim from training knowledge, not re-verified rule-by-rule].
- **Nobody ships D3's actual move**: the file the authoring model reads IS the
  file the linter parses. Contract and config are one artifact, so they cannot
  drift — the same structural argument as "one scorer."

### 1. Format grammar — FORMAT/CONVENTION, cost M, phase 03.1 (lint core), 11 (model-judged pass)

`LESSON-STYLE.md` lives beside the bank (or is named by `--style`); discovery
mirrors `lanes.md` beside the plan. **Additive**: no file → no style checks →
lint output byte-identical to today.

The file has two audiences and two zones:

```markdown
# LESSON-STYLE — house voice for itembank lessons

## Voice
Write to one learner as "you". Plain, calm, declarative. Explain WHY a fact
holds before drilling WHAT it is. No hype, no hedging, no cheerleading.
The lesson is a colleague talking you through it, not a textbook and not a
quiz-show host.

## Golden paragraph
An OPA holds the tongue off the back of the throat. You size it from the
corner of the mouth to the earlobe, because a wrong size can push the tongue
backward and block the airway you are trying to open. If the patient gags,
remove it — a gag reflex means the airway is protecting itself.

## Rules
| Code | Severity | Params | Rule |
|---|---|---|---|
| style.sentence_too_long | error | max=28 | Keep every sentence at or under 28 words. |
| style.filler_phrase | error | — | Never open with filler: see the blocklist. |
| style.passive_voice | warning | — | Prefer active voice. |
| style.one_idea_per_section | manual | — | Each ### section teaches exactly one idea. |

## Blocklists
FILLER: it is important to note | as we all know | simply put | let's dive in |
  needless to say | it's worth noting | in today's world | delve
MINIMIZERS: just | simply | obviously | easy | clearly | of course
HEDGES: very | really | quite | basically | actually | in general
```

- Prose zones (`## Voice`, `## Golden paragraph`) are read by the authoring
  model verbatim as its system-context (Phase 11 authoring loop prepends the
  file to every lesson-writing request). The golden paragraph is the few-shot
  anchor — one concrete exemplar outperforms ten adjectives.
- `## Rules` is the first pipe table under that heading; the linter parses it
  (pipe-table parsing precedent already exists in `surfaces/day.py`'s lane
  tables). Columns: dotted code, severity ∈ {error, warning, manual}, `k=v`
  params, prose statement.
- **The honesty rule**: a row whose code the linter does not implement but
  whose severity is `error` or `warning` → lint finding `style.unknown_rule`
  (error). The contract cannot claim machine enforcement it does not have;
  aspirational rules must be marked `manual`. `manual` rows are skipped by
  `lint()` and consumed by the Phase 11 quality pass (model-judged,
  report-only, never blocking).
- `## Blocklists` feeds the regex rules; pipe-separated phrase lists, matched
  case-insensitively on word boundaries, code spans excluded.
- Style findings attach to the bank (`item` = "LESSON" or "LESSON:<heading-slug>"),
  reusing `LintError` unchanged. New codes join `LINT_CODES` (all `style.*`).
- Scope: style rules run over `## LESSON` prose only (intro + section bodies,
  minus fenced code, minus callout `[ID:]/[HASH:]` bookkeeping). Item stems and
  rationales keep their existing item-level checks; the voice contract governs
  lessons.

### 2. Q3 — the concrete rules, and what the linter can honestly check

Sentence splitting for all counts: split on `[.!?]` followed by whitespace +
uppercase/quote, with an abbreviation stoplist (e.g., "e.g.", "Dr.", "vs.") —
imperfect but deterministic; counts use `collapse()` word-splitting. Flesch
uses the standard vowel-group syllable heuristic — pure Python, no dependency.

**Hard lint errors — machine-checkable (8):**

| # | Rule | How checked |
|---|---|---|
| E1 | No sentence over 28 words | structural count over split sentences |
| E2 | No `###` section over 250 words | word count per parsed heading body (headings already parsed [VERIFIED: model.py:236-250]) |
| E3 | One idea-block budget: at most 1 `[!KEY]` per section | structural count of KEY markers per section |
| E4 | Filler-phrase blocklist (from `## Blocklists`) never appears | case-insensitive word-boundary regex, code spans excluded |
| E5 | No exclamation marks in lesson prose | regex `!(?![\[(])` outside code/callout-marker lines |
| E6 | Section headings ≤ 60 characters | length of parsed heading text |
| E7 | `[!KEY]` body ≤ 40 words | word count of callout body minus cloze braces — a memorizable must fit a card |
| E8 | Every `[!KEY]` has a title or a cloze (`key.no_front`) | structural presence check (shared with D2) |

**Warnings — machine-checkable but false-positive-prone (10):**

| # | Rule | How checked |
|---|---|---|
| W1 | Prefer active voice | Vale-style heuristic regex: `\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\b` — heuristic, hence warning |
| W2 | Address the learner as "you", never "the student/the learner" | regex on those noun phrases |
| W3 | No teacher-"we" ("we will learn", "we can now") | regex `\bwe\s+(will|are going to|can now|have seen)\b` |
| W4 | Average sentence length ≤ 18 words per section | mean over split sentences |
| W5 | Paragraph ≤ 4 sentences and ≤ 90 words | blank-line-delimited block counts |
| W6 | Flesch Reading Ease ≥ 50 per section | pure-Python syllable heuristic; terminology-heavy EMT prose inflates it, hence warning |
| W7 | No rhetorical questions in prose (a `?`-sentence belongs in an item or a question callout) | sentence-final `?` outside callouts |
| W8 | Minimizer/hedge blocklists ("just", "simply", "obviously", "easy"; "very", "basically") | word-boundary regex; warning because legitimate uses exist |
| W9 | First lesson-prose use of each `## TERMS` term is a `[[term]]` reference | slug-scan of prose vs. reference positions (D1 tie-in) |
| W10 | A section over 150 words contains at least one example marker (`[!EXAMPLE]` or a "For example"-class sentence opener) | structural presence per section — a density proxy, not a quality judgment |

**Model-judged — NOT lintable; severity `manual`, Phase 11 quality pass only (5):**

| # | Rule | Why no deterministic check exists |
|---|---|---|
| M1 | One idea per section — the section's sentences all serve one claim | topical coherence is semantic; word count (E2) is only its proxy |
| M2 | Each example actually illustrates the claim it follows | requires understanding both |
| M3 | At most one analogy per section, and it maps correctly | analogy detection beyond stock phrases is semantic |
| M4 | Explain why before what — mechanism precedes drill | causal-structure judgment |
| M5 | Sections order from familiar to new; no forward references | discourse-level dependency judgment |

**Count: 18 machine-checkable (8 hard errors + 10 warnings) vs 5 model-judged.**
The manual five are exactly the rows the honesty rule forces to be labeled
`manual`, and the Phase 11 auditor reports on them without ever blocking a
lint pass — lesson quality becomes "lint clean + quality report", never "a
model said no."

### 3. Enforcement flow — CONVENTION/RUNTIME, cost S(03.1)+M(11)

1. **Before writing** (Phase 11 authoring loop): the runtime prepends
   `LESSON-STYLE.md` verbatim to the authoring request. The model reads the
   same rules the linter will enforce, including which are `error`.
2. **After writing**: `itembank lint` (with the style file discovered or
   passed) emits `style.*` findings; the authoring loop's VALIDATE stage
   (UI-SPEC state machine D) already blocks DIFF on lint errors — style errors
   ride that gate with zero new machinery.
3. **Quality pass** (Phase 11, report-only): a model judges `manual` rows and
   writes findings into the audit report; per UI-SPEC, report_only never
   exposes a publish control, so a model's style opinion can never block or
   force a write.

---

## Cross-cutting summary table

| Finding | Kind | Cost | Phase |
|---|---|---|---|
| `## TERMS` section + `parse_terms()` + 6 lint codes | FORMAT | S | 03.1 |
| `[[term]]`/`[[term\|display]]` inline grammar + escaping | FORMAT | S | 03.1 |
| `XLAT:` field reserved for bilingual reader | FORMAT | ~0 | 03.1 (design only; 999.2 renders) |
| Term popover render (popover API + interestfor enhancement) | RENDERER | M | 03.1 |
| No-JS term = link to rendered glossary appendix; print glossary | RENDERER | S | 03.1 |
| `glossable(item, term)` gate + `/gloss` endpoint + `term_lookup` event | RUNTIME | M | 03.1 |
| Term lookup → review-candidate derivation | RUNTIME | S | 10 |
| `[!KEY]` + decorative callout family grammar, `{{cloze}}`, `[ID:]/[HASH:]` reuse | FORMAT | M | 03.1 |
| KEY → Anki TSV export with `#guid column` update semantics | FORMAT | S | 03.1 |
| KEY render, reader-revealed cloze, review-blanked cloze via runtime | RENDERER | M | 03.1 (reader) / 10 (review) |
| KEY no-JS review via details/summary + POST rating (self-graded exception, stated) | RENDERER | S | 10 |
| `key_review` events as FSRS ReviewLog; card state derived, never stored | RUNTIME | M | 10 |
| Pure-Python FSRS (~100 lines, no dependency) | RUNTIME | M | 10 |
| `LESSON-STYLE.md` two-zone file; rules table parsed by linter; honesty rule | FORMAT/CONVENTION | M | 03.1 |
| 18 `style.*` lint checks (8 error + 10 warning) | FORMAT | M | 03.1 |
| Model-judged style pass (5 rules, report-only) | RUNTIME | M | 11 |
| Style file prepended to authoring requests | CONVENTION | S | 11 |

## Open questions for discuss-phase

1. Should `[[term]]` be legal in item *option* text at all, or stems only?
   (Options are answer candidates; even a gated gloss affordance on an option
   may cue elimination. Recommendation: stems only in 03.1.)
2. Gloss density control (Word Wise slider analog) — defer; a learner setting
   "underline all terms / only first use / none" is a Phase 4 settings row
   later, not 03.1 scope.
3. Does `[!KEY]` belong in item RATIONALE fields (post-answer surfaces) too?
   Cheap later; out of 03.1.
4. Exact abbreviation stoplist for the sentence splitter — build from fixture
   banks during 03.1, not speculation.

## Sources

- [GitHub alerts syntax and degradation](https://github.com/community/community/discussions/16925), [Jake Lee's alert experiments](https://blog.jakelee.co.uk/github-alert-experiments/)
- [Obsidian callouts syntax](https://www.markdowntools.io/obsidian-callouts), [Obsibrain callout guide](https://www.obsibrain.com/blog/obsidian-callouts-complete-guide-syntax-and-customization)
- [Anki text-file import headers (official manual)](https://docs.ankiweb.net/importing/text-files.html)
- [AnkiConnect API](https://git.sr.ht/~foosoft/anki-connect)
- [Popover API Baseline (web.dev)](https://web.dev/blog/popover-api), [MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API), [popover accessibility (hidde.blog)](https://hidde.blog/popover-accessibility/)
- [Interest invokers explainer (Open UI)](https://open-ui.org/components/interest-invokers.explainer/), [Chromium intent-to-ship](https://groups.google.com/a/chromium.org/g/blink-dev/c/bX1G_yDt6W4)
- [Kindle Word Wise](https://www.amazon.com/gp/help/customer/display.html?nodeId=201645250), [MakeUseOf Word Wise guide](https://www.makeuseof.com/how-to-enable-use-word-wise-kindle/)
- [LingQ review (vocabulary system)](https://www.alllanguageresources.com/lingq-review/), [Simply Fluent reading apps 2026](https://www.simplyfluent.com/blog/best-reading-apps-language-learning-2026/)
- [Mochi cloze/advanced formatting](https://mochi.cards/docs/markdown/advanced-formatting/), [RemNote flashcard creation](https://help.remnote.com/en/articles/6025481-creating-flashcards)
- [ts-fsrs docs](https://open-spaced-repetition.github.io/ts-fsrs/), [Implementing FSRS in 100 lines](https://borretti.me/article/implementing-fsrs-in-100-lines), [RemNote FSRS overview](https://help.remnote.com/en/articles/9124137-the-fsrs-spaced-repetition-algorithm)
- [Vale docs](https://vale.sh/docs), [Vale rule authoring](https://medium.com/valelint/rule-authoring-101-ca066233970c), [First steps with Vale](https://passo.uno/posts/first-steps-with-the-vale-prose-linter/)
